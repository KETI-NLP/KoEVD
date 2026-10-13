"""Local operator policy decisions, never supplied by a result uploader.

Content hashes/actor declarations preserve consistency; they are not signatures
or proof of human approval. The operator controls the directory, roles and the
explicit decision digest selected at startup. No decision is selected by mtime.
"""
from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
import uuid

from .eligibility import RankPolicy, VERSION, _sha
from .results import canonical_hash, read_document
from .storage import encode, token

FORMAT = 'koevd-operator-policy-decision-v1'
MAX_BYTES, MAX_HISTORY = 16384, 256
FIELDS = {'format', 'admission_version', 'action', 'actor', 'decided_at',
          'reason', 'previous_sha256'}


def validate_decision(document):
    if (not isinstance(document, dict) or set(document) != FIELDS
            or document.get('format') != FORMAT or document.get('admission_version') != VERSION
            or document.get('action') not in ('ratify', 'revoke')):
        raise ValueError('Unsupported operator policy decision')
    token(document['actor'], 'local policy actor')
    reason = document['reason']
    if not isinstance(reason, str) or not reason.strip() or len(reason.encode('utf-8')) > 4096:
        raise ValueError('A bounded operator decision reason is required')
    when = document['decided_at']
    if not isinstance(when, str) or len(when) != 20:
        raise ValueError('Use a UTC decision time YYYY-MM-DDTHH:MM:SSZ')
    try:
        parsed = datetime.strptime(when, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as exc:
        raise ValueError('Invalid UTC policy decision time') from exc
    if parsed.strftime('%Y-%m-%dT%H:%M:%SZ') != when:
        raise ValueError('Use canonical UTC decision time')
    previous = document['previous_sha256']
    if previous is not None and not _sha(previous):
        raise ValueError('Invalid previous decision digest')
    if len(encode(document)) > MAX_BYTES:
        raise ValueError('Policy decision exceeds size limit')
    return document


class PolicyArchive:
    """Immutable addressed files on operator-owned local disk.

    Atomic hard-link publication prevents partial decisions being selected.
    This is not a cloud bucket adapter or protection against the disk owner.
    Branches are allowed; the operator must pin one explicitly selected chain.
    """
    def __init__(self, root, *, create=False):
        self.root = Path(root).absolute()
        self._safe_path(self.root)
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
            if os.name != 'nt': os.chmod(self.root, 0o700)
        if not self.root.is_dir():
            raise ValueError('Operator policy archive does not exist')

    @staticmethod
    def _safe_path(path):
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Policy path must not traverse symlinks')

    def read(self, digest):
        if not _sha(digest):
            raise ValueError('Pin an explicit policy decision SHA-256')
        path = self.root / (digest + '.json')
        self._safe_path(path)
        document = validate_decision(read_document(path, max_bytes=MAX_BYTES))
        if canonical_hash(document) != digest:
            raise ValueError('Archived decision differs from its selected digest')
        return document

    def history(self, digest):
        if not _sha(digest):
            raise ValueError('Pin an explicit policy decision SHA-256')
        history, seen = [], set()
        while digest is not None:
            if digest in seen or len(history) >= MAX_HISTORY:
                raise ValueError('Policy history cycle or size limit')
            seen.add(digest)
            document = self.read(digest)
            history.append({'sha256': digest, 'decision': document})
            digest = document['previous_sha256']
        history.reverse()
        for previous, current in zip(history, history[1:]):
            if current['decision']['decided_at'] < previous['decision']['decided_at']:
                raise ValueError('Policy decision time precedes its parent')
        return history

    def record(self, document):
        validate_decision(document)
        previous = document['previous_sha256']
        if previous is not None:
            chain = self.history(previous)
            if len(chain) >= MAX_HISTORY:
                raise ValueError('Policy history size limit')
            if document['decided_at'] < chain[-1]['decision']['decided_at']:
                raise ValueError('Policy decision time precedes its parent')
        digest = canonical_hash(document)
        dest = self.root / (digest + '.json')
        self._safe_path(dest)
        if dest.exists():
            self.read(digest)  # A corrupt existing record is never overwritten.
            return digest
        pending = self.root / ('.' + uuid.uuid4().hex + '.pending')
        try:
            fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(encode(document) + b'\n')
                stream.flush(); os.fsync(stream.fileno())
            try:
                os.link(pending, dest)
            except FileExistsError:
                self.read(digest)
            if os.name != 'nt':
                fd = os.open(self.root, os.O_RDONLY)
                try: os.fsync(fd)
                finally: os.close(fd)
        finally:
            if pending.exists(): pending.unlink()
        self.history(digest)
        return digest

    def policy(self, digest):
        history = self.history(digest)
        return (RankPolicy(status='ratified', ratification_sha256=digest)
                if history[-1]['decision']['action'] == 'ratify' else RankPolicy())


def configured_policy(root=None, digest=None):
    if root is None and digest is None:
        return RankPolicy()
    if not root or not digest:
        raise ValueError('Policy archive and explicit decision SHA-256 must be configured together')
    return PolicyArchive(root).policy(digest)


def main():
    import argparse
    import sys
    from .common import configure_cli_stdio
    from .storage import StorageError
    configure_cli_stdio()
    parser = argparse.ArgumentParser(description='Local policy archive; no automatic approval, HTTP intake or deployment')
    parser.add_argument('--policy-root', required=True)
    parser.add_argument('--roles-file', required=True, help='Independent operator-owned role configuration')
    parser.add_argument('--actor', required=True, help='Local OS/operator assertion, not authenticated login')
    commands = parser.add_subparsers(dest='command', required=True)
    archive = commands.add_parser('archive'); archive.add_argument('--decision-file', required=True)
    for command in ('inspect', 'history'):
        commands.add_parser(command).add_argument('--head-sha256', required=True)
    args = parser.parse_args()
    try:
        roles = read_document(args.roles_file, max_bytes=1024*1024)
        if (not isinstance(roles, dict) or set(roles) != {'reviewers', 'admins'}
                or any(not isinstance(v, list) or len(v) > 1000
                       or any(not isinstance(s, str) for s in v) for v in roles.values())):
            raise ValueError('Invalid independent operator roles')
        token(args.actor, 'local policy actor')
        if args.actor not in roles['admins']:
            raise ValueError('Operator administrator required')
        store = PolicyArchive(args.policy_root, create=args.command == 'archive')
        if args.command == 'archive':
            document = read_document(args.decision_file, max_bytes=MAX_BYTES)
            validate_decision(document)
            if document['actor'] != args.actor:
                raise ValueError('Decision actor differs from local operator assertion')
            digest = store.record(document)
        else: digest = args.head_sha256
        history = store.history(digest)
        policy = store.policy(digest)
        result = {'execution_scope': 'operator_local', 'decision_sha256': digest,
                  'policy': asdict(policy), 'policy_sha256': policy.sha256,
                  'history_decisions': len(history), 'human_approval_authenticated': False,
                  'server_configuration_changed': False, 'published': False}
        if args.command == 'history': result['private_history'] = history
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, StorageError, OSError) as exc:
        print(json.dumps({'error': 'invalid_operator_policy', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__': main()
