"""Strict local Static candidate manifest check used before hosted validation."""
import hashlib
import json
from pathlib import Path, PurePosixPath


def checked_inventory(root):
    root = Path(root).resolve(strict=True)
    manifest = json.loads((root / 'deployment-manifest.json').read_text(encoding='utf-8'))
    files = manifest['files']
    if {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} != set(files) | {'deployment-manifest.json'}:
        raise ValueError('Static inventory differs from manifest')
    for name, item in files.items():
        relative = PurePosixPath(name)
        if (relative.is_absolute() or relative.as_posix() != name or '..' in relative.parts
                or '\\' in name or ':' in name):
            raise ValueError('Unsafe static manifest path')
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents) or not path.resolve().is_relative_to(root):
            raise ValueError('Static symlink or escape')
        if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Static candidate hash mismatch')
    return manifest
