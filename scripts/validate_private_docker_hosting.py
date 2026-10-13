"""HF Docker access-cookie boundary, distinct from Static owner access.

This is resource access only. It never establishes a KoEVD submitter identity.
Cookie values must stay in memory and must not be written to evidence or argv.
"""
import re
from urllib.parse import urlparse


def checked_host(value):
    parsed = urlparse(value)
    if (parsed.scheme != 'https' or parsed.username or parsed.password
            or parsed.port is not None or parsed.query or parsed.fragment
            or parsed.path not in ('', '/')
            or not re.fullmatch(r'[a-z0-9-]+\.hf\.space', parsed.hostname or '')):
        raise ValueError('Require an API-verified HTTPS Docker Space origin')
    return value.rstrip('/')


def access_cookies(jar, origin):
    host = urlparse(checked_host(origin)).hostname
    candidates = [cookie for cookie in jar if cookie.name == 'spaces-jwt']
    if len(candidates) != 1:
        raise ValueError('Expected one HF Docker resource-access cookie')
    cookie = candidates[0]
    if cookie.domain != host or cookie.path != '/' or not cookie.secure or 'HttpOnly' not in cookie._rest:
        raise ValueError('Unexpected Docker resource-access cookie scope')
    return [{'name': cookie.name, 'value': cookie.value, 'domain': host,
             'path': '/', 'secure': True, 'httpOnly': True}]
