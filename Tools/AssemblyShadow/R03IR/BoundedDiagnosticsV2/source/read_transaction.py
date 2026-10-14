"""Strict reader for a native V2 transaction; not connected to the Player verifier.

The caller supplies the reviewed wire decoder and an INDEPENDENTLY authenticated
native commit receipt and run identity. Hash-only self-attestation is insufficient.
No original V1 record or semantic result is manufactured by this component.
"""
from __future__ import annotations
import hashlib
import io
import json
import math
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOTAL = 4194304
RESERVE = 262144
MAX_STREAM = TOTAL - RESERVE
NAMES = ('diagnostics.v2.bin', 'raw.v2.json')
KEYS = {'committed', 'directoryDevice', 'directoryInode', 'artifactDevice',
        'artifactInode', 'envelopeDevice', 'envelopeInode', 'artifactBytes',
        'envelopeBytes', 'artifactHash', 'envelopeHash'}

class TransactionError(ValueError):
    pass

def need(ok: bool, message: str) -> None:
    if not ok:
        raise TransactionError(message)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def strict_json(data: bytes | str) -> Any:
    """Bound depth before parsing; reject duplicate keys and nonfinite numbers."""
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'strict')
    depth = 0
    quoted = escaped = False
    for char in data:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            need(depth <= 64, 'JSON depth budget')
        elif char in '}]':
            depth -= 1
            need(depth >= 0, 'JSON nesting')
    need(depth == 0 and not quoted, 'JSON incomplete')
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def no_constant(value):
        raise TransactionError('nonfinite JSON constant: ' + value)
    def finite(value):
        result = float(value)
        need(math.isfinite(result), 'nonfinite JSON number')
        return result
    value = json.loads(data, object_pairs_hook=pairs, parse_constant=no_constant,
                       parse_float=finite)
    stack = [value]
    nodes = 0
    while stack:
        current = stack.pop()
        nodes += 1
        need(nodes <= 200000, 'JSON node budget')
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return value

@dataclass(frozen=True)
class VerifiedTransport:
    report: dict
    envelope_sha256: str
    artifact_sha256: str
    transport: str = 'NativeBoundedSnapshotV2'
    semantic_acceptance: bool = False

def _file_state(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid, s.st_nlink,
            s.st_size, s.st_mtime_ns, s.st_ctime_ns)

def _dir_state(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid)

def read_transaction(directory: str | Path, receipt: dict, identity: dict, wire) -> VerifiedTransport:
    """Validate both owned files and all ancestors; return only after all checks.

    'wire' must be the source-reviewed R03BoundedDiagnosticsV2 decoder, not a
    function supplied by diagnostic contents. This dependency is explicit while
    the original semantic-verifier transport dispatch remains unintegrated.
    The byte/depth/node limits are not a proof of a hard Python process-RSS cap.
    """
    need(type(receipt) is dict and set(receipt) == KEYS, 'commit receipt schema')
    need(receipt['committed'] is True, 'transaction not committed')
    for key in KEYS - {'committed', 'artifactHash', 'envelopeHash'}:
        need(type(receipt[key]) is int and receipt[key] >= 0, 'receipt integer')
    need(192 <= receipt['artifactBytes'] <= MAX_STREAM and
         2 <= receipt['envelopeBytes'] <= RESERVE, 'receipt byte budget')
    for key in ('artifactHash', 'envelopeHash'):
        v = receipt[key]
        need(isinstance(v, str) and len(v) == 64 and
             all(c in '0123456789abcdef' for c in v), 'receipt digest')
    path = os.fspath(directory)
    need(isinstance(path, str) and path.startswith('/') and 1 < len(path) <= 4096,
         'absolute owned directory')
    parts = path.split('/')[1:]
    need(len(parts) <= 64 and all(p not in ('', '.', '..') and '\0' not in p and
                                 len(p.encode()) <= 255 for p in parts), 'canonical directory')
    fds: list[int] = []
    dirs: list[tuple[int, os.stat_result]] = []
    files: list[tuple[int, os.stat_result]] = []
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        fds.append(fd); dirs.append((fd, os.fstat(fd)))
        for name in parts:
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=fd)
            fds.append(fd); dirs.append((fd, os.fstat(fd)))
        owner = dirs[-1][1]
        need(owner.st_uid == os.geteuid() and stat.S_IMODE(owner.st_mode) == 0o700,
             'private owned directory')
        need((owner.st_dev, owner.st_ino) == (receipt['directoryDevice'], receipt['directoryInode']),
             'directory identity')
        def check_dirs():
            for i, (held_fd, original) in enumerate(dirs):
                need(_dir_state(os.fstat(held_fd)) == _dir_state(original), 'changed held directory')
                if i:
                    named = os.stat(parts[i-1], dir_fd=dirs[i-1][0], follow_symlinks=False)
                    need(_dir_state(named) == _dir_state(original), 'changed directory path')
        check_dirs()
        contents = []
        for i, name in enumerate(NAMES):
            f = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=fd)
            fds.append(f); s = os.fstat(f); files.append((f, s))
            prefix = 'artifact' if i == 0 else 'envelope'
            need(stat.S_ISREG(s.st_mode) and s.st_uid == os.geteuid() and
                 stat.S_IMODE(s.st_mode) == 0o600 and s.st_nlink == 1, 'regular private single-link file')
            need((s.st_dev, s.st_ino, s.st_size) ==
                 (receipt[prefix+'Device'], receipt[prefix+'Inode'], receipt[prefix+'Bytes']),
                 'file identity/length')
            chunks = []
            remaining = s.st_size
            while remaining:
                chunk = os.read(f, min(65536, remaining))
                need(bool(chunk), 'short file')
                chunks.append(chunk); remaining -= len(chunk)
            need(os.read(f, 1) == b'', 'trailing file bytes')
            data = b''.join(chunks)
            need(digest(data) == receipt[prefix+'Hash'], 'file hash')
            contents.append(data)
        artifact, envelope = contents
        raw = strict_json(envelope)
        need(type(raw) is dict and raw.get('reportTransport') == 'NativeBoundedSnapshotV2', 'raw transport')
        need('diagnosticArtifact' in raw, 'missing artifact descriptor')
        inline = {k: v for k, v in raw.items() if k != 'diagnosticArtifact'}
        descriptor = raw['diagnosticArtifact']
        need(type(descriptor) is dict and descriptor.get('bytes') == receipt['artifactBytes'] and
             descriptor.get('sha256') == receipt['artifactHash'], 'descriptor versus external receipt')
        fields = wire.decode(io.BytesIO(artifact), descriptor, identity, inline)
        for value in fields.values():
            if value is not None:
                strict_json(value)
        for i, (f, original) in enumerate(files):
            named = os.stat(NAMES[i], dir_fd=fd, follow_symlinks=False)
            need(_file_state(os.fstat(f)) == _file_state(original) == _file_state(named), 'changed file')
        check_dirs()
        return VerifiedTransport({**inline, **fields}, receipt['envelopeHash'], receipt['artifactHash'])
    finally:
        for fd in reversed(fds):
            os.close(fd)
