"""Server-side HF authorization-code/PKCE login, separate from analysis tokens.

Authenticate only through the fixed HTTPS provider's token and userinfo endpoints.
ID tokens are not decoded/trusted; access/refresh tokens never reach the browser,
disk, result artifacts or application logs. Sessions are bounded and ephemeral.
"""
from base64 import b64encode, urlsafe_b64encode
from dataclasses import dataclass, field
from hashlib import sha256
import json
import secrets
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .results import _unique_object
from .storage import StorageError
from .submissions import Principal

ISSUER = 'https://huggingface.co'


def _digest(value): return sha256(value.encode('utf-8')).hexdigest()


def _bounded(value, limit):
    return isinstance(value,str) and 0 < len(value) <= limit and not any(ord(c)<32 or ord(c)==127 for c in value)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None


@dataclass(frozen=True)
class HFOAuthProvider:
    client_id: str
    client_secret: str = field(default='', repr=False)
    client_type: str = field(default='confidential', kw_only=True)

    def __post_init__(self):
        if self.client_type not in ('confidential','public'):
            raise ValueError('Expected an explicit confidential or public OAuth client type')
        if not _bounded(self.client_id,512):
            raise ValueError('HF OAuth application credentials are required')
        if self.client_type=='confidential' and not _bounded(self.client_secret,4096):
            raise ValueError('HF OAuth application credentials are required for confidential clients')
        if self.client_type=='public' and self.client_secret!='':
            raise ValueError('Public HF OAuth clients must not configure a client secret')

    def _json(self, request):
        try:
            # Refuse redirects, including redirects that would expose Basic or
            # Bearer credentials to another endpoint. Never surface provider body.
            with build_opener(_NoRedirect).open(request,timeout=10) as response:
                raw=response.read(65537)
                if len(raw)>65536: raise ValueError('Provider response exceeds limit')
                data=json.loads(raw.decode('utf-8'),object_pairs_hook=_unique_object)
                if not isinstance(data,dict): raise ValueError('Invalid provider response')
                return data
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,UnicodeError):
            raise StorageError('oauth_provider_failed','HF sign-in could not be verified. Start sign-in again.',502) from None

    def exchange(self, code, verifier, redirect_uri):
        # Public apps authenticate with PKCE, never a missing-secret fallback.
        if self.client_type=='public' and (not isinstance(verifier,str) or not 43 <= len(verifier) <= 128
                or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~' for c in verifier)):
            raise StorageError('oauth_verifier_invalid','A valid PKCE verifier is required.',401)
        body=urlencode({'client_id':self.client_id,'code':code,'code_verifier':verifier,
                        'grant_type':'authorization_code','redirect_uri':redirect_uri}).encode('ascii')
        headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'}
        if self.client_type=='confidential':
            basic=b64encode((self.client_id+':'+self.client_secret).encode('utf-8')).decode('ascii')
            headers['Authorization']='Basic '+basic
        data=self._json(Request(ISSUER+'/oauth/token',data=body,headers=headers))
        token=data.get('access_token');expires=data.get('expires_in')
        if not _bounded(token,8192) or data.get('token_type','').lower()!='bearer' or type(expires) not in (int,float) or not 0 < expires <= 43200*60:
            raise StorageError('oauth_provider_failed','HF returned an invalid sign-in response.',502)
        # Only this TLS-authenticated response supplies the stable subject. Neither
        # an uploaded username/role nor an unverified ID-token payload is used.
        info=self._json(Request(ISSUER+'/oauth/userinfo',headers={'Authorization':'Bearer '+token,'Accept':'application/json'}))
        if not _bounded(info.get('sub'),512):
            raise StorageError('oauth_subject_missing','HF user identity could not be verified.',502)
        return info,expires


class IdentitySessions:
    """One-process absolute-TTL sessions. Restart requires login again, not data loss.

    All roles remain operator configuration in SubmissionService. A local session
    does not continually recheck HF revocation; maximum lifetime is one hour.
    """
    def __init__(self, provider, origin, *, clock=time.monotonic, max_pending=128,
                 max_sessions=256, pending_ttl=300, session_ttl=3600):
        parsed=urlsplit(origin)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
            raise ValueError('Explicit canonical app origin required for OAuth')
        if parsed.scheme=='http' and parsed.hostname not in ('localhost','127.0.0.1','::1'):
            raise ValueError('HF sign-in requires HTTPS outside localhost')
        if any(type(v) is not int or v<1 for v in (max_pending,max_sessions,pending_ttl,session_ttl)) or session_ttl>3600:
            raise ValueError('Invalid bounded identity-session configuration')
        if not hasattr(provider,'exchange') or not _bounded(provider.client_id,512):
            raise ValueError('Expected a configured HF OAuth provider')
        self.provider,self.origin,self.clock=provider,origin.rstrip('/'),clock
        self.redirect_uri=self.origin+'/auth/callback'
        self.max_pending,self.max_sessions=max_pending,max_sessions
        self.pending_ttl,self.session_ttl=pending_ttl,session_ttl
        self.secure=parsed.scheme=='https'
        self.cookie_name='__Host-koevd_identity' if self.secure else 'koevd_identity'
        self.binding_cookie='__Host-koevd_login_bind' if self.secure else 'koevd_login_bind'
        self.pending,self.sessions,self.lock={}, {}, threading.RLock()

    def cleanup(self):
        with self.lock:
            for collection in (self.pending,self.sessions):
                for key,value in list(collection.items()):
                    if value['expires_at']<=self.clock():del collection[key]

    def begin(self, previous_binding=None):
        with self.lock:
            self.cleanup()
            if _bounded(previous_binding,256):
                for key,value in list(self.pending.items()):
                    if secrets.compare_digest(value['binding_sha256'],_digest(previous_binding)):del self.pending[key]
            if len(self.pending)>=self.max_pending:
                raise StorageError('login_capacity','Too many sign-in attempts. Try later.',503)
            state,binding,verifier=(secrets.token_urlsafe(32) for _ in range(3))
            challenge=urlsafe_b64encode(sha256(verifier.encode('ascii')).digest()).rstrip(b'=').decode('ascii')
            self.pending[_digest(state)]={'binding_sha256':_digest(binding),'verifier':verifier,
                                         'expires_at':self.clock()+self.pending_ttl}
            query=urlencode({'client_id':self.provider.client_id,'redirect_uri':self.redirect_uri,
                'scope':'openid profile','response_type':'code','state':state,
                'code_challenge':challenge,'code_challenge_method':'S256'})
            return ISSUER+'/oauth/authorize?'+query,binding

    def complete(self, state, binding, code, *, previous_session=None):
        if not all(_bounded(v,256) for v in (state,binding)) or not _bounded(code,4096):
            raise StorageError('oauth_state_invalid','Invalid sign-in callback. Start sign-in again.',401)
        with self.lock:
            self.cleanup();entry=self.pending.get(_digest(state))
            if entry is None or not secrets.compare_digest(entry['binding_sha256'],_digest(binding)):
                raise StorageError('oauth_state_invalid','Sign-in state is expired or belongs to another browser.',401)
            # Consume before network I/O: replay and concurrent callbacks cannot
            # exchange one code twice, even if the provider request fails.
            del self.pending[_digest(state)]
        info,provider_ttl=self.provider.exchange(code,entry['verifier'],self.redirect_uri)
        if not isinstance(info,dict) or not _bounded(info.get('sub'),512) or type(provider_ttl) not in (int,float) or not provider_ttl>=1:
            raise StorageError('oauth_subject_missing','Verified identity response is invalid.',502)
        ttl=min(int(provider_ttl),self.session_ttl)
        subject='hf:'+_digest(info['sub'])
        username=info.get('preferred_username') or info.get('name') or subject
        if not _bounded(username,256):username=subject
        with self.lock:
            self.cleanup()
            if _bounded(previous_session,256):self.sessions.pop(_digest(previous_session),None)
            if len(self.sessions)>=self.max_sessions:
                raise StorageError('identity_capacity','Sign-in session capacity reached. Try later.',503)
            token,csrf=secrets.token_urlsafe(32),secrets.token_urlsafe(32)
            self.sessions[_digest(token)]={'principal':Principal(subject,'hf_oauth'),'username':username,
                'csrf':csrf,'expires_at':self.clock()+ttl}
            return token,ttl

    def get(self, session_token, csrf=None):
        if not _bounded(session_token,256):
            raise StorageError('identity_required','Sign in with HF before managing submissions.',401)
        with self.lock:
            self.cleanup();entry=self.sessions.get(_digest(session_token))
            if entry is None:raise StorageError('identity_required','Sign-in session expired. Sign in again.',401)
            if csrf is not None and (not _bounded(csrf,256) or not secrets.compare_digest(entry['csrf'],csrf)):
                raise StorageError('identity_csrf','Invalid sign-in CSRF token.',403)
            return dict(entry)

    def logout(self, session_token, csrf):
        with self.lock:
            self.get(session_token,csrf);self.sessions.pop(_digest(session_token),None)

    def close(self):
        with self.lock:self.sessions.clear();self.pending.clear()
