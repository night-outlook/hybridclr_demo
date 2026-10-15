"""Inactive read-only V2 file boundary; returns data, never semantic acceptance.

The expected successful transaction receipt and identity MUST be authenticated
outside these files (source/request/process/build/evidence joins). Self-supplied
hashes cannot authenticate a producer. The `codec` parameter is the existing
versioned wire decoder; original business predicates are not called or replaced.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
import os
import stat
from pathlib import Path

ARTIFACT = 'diagnostics.v2.bin'
ENVELOPE = 'envelope.v2.json'
INLINE_MAX = 262144
ARTIFACT_MAX = 3932160

class TransactionError(ValueError):
    pass

def need(ok: bool, message: str) -> None:
    if not ok:
        raise TransactionError(message)

def _hex(value: object) -> bool:
    return (type(value) is str and len(value) == 64 and
            all(c in '0123456789abcdef' for c in value))

def _file_receipt(value: object, bound: int, *, root: bool = False) -> dict:
    need(type(value) is dict and set(value) == {'device', 'inode', 'owner', 'mode', 'bytes', 'sha256'},
         'exact file receipt schema')
    for key in ('device', 'inode', 'owner', 'mode', 'bytes'):
        need(type(value[key]) is int and 0 <= value[key] < 2**64, 'integer receipt field')
    need(value['inode'] > 0 and value['owner'] == os.geteuid(), 'receipt owner/inode')
    need(value['mode'] == (0o700 if root else 0o600), 'receipt mode')
    need(_hex(value['sha256']), 'receipt sha256')
    need(value['bytes'] == 0 if root else 0 < value['bytes'] <= bound, 'receipt size bound')
    if root:
        need(value['sha256'] == '0' * 64, 'directory has no content digest')
    return value

def _identity(s: os.stat_result) -> tuple:
    return (s.st_dev, s.st_ino, s.st_uid, s.st_gid, s.st_mode)

def _stable(s: os.stat_result) -> tuple:
    return _identity(s) + (s.st_size, s.st_nlink, s.st_mtime_ns, s.st_ctime_ns)

def _matches(s: os.stat_result, expected: dict, *, root: bool = False) -> None:
    need((s.st_dev, s.st_ino, s.st_uid, stat.S_IMODE(s.st_mode)) ==
         (expected['device'], expected['inode'], expected['owner'], expected['mode']),
         'file identity/mode changed')
    if root:
        need(stat.S_ISDIR(s.st_mode) and s.st_nlink > 0, 'live directory required')
    else:
        need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and s.st_size == expected['bytes'],
             'regular single-link exact file required')

def _json(data: bytes, *, object_required: bool = True):
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, 'duplicate JSON key')
            obj[k] = v
        return obj
    def constant(_: str):
        raise TransactionError('nonfinite JSON')
    def finite(value):
        number = float(value)
        need(math.isfinite(number), 'nonfinite/overflowed JSON number')
        return number
    try:
        value = json.loads(data.decode('utf-8', 'strict'), object_pairs_hook=pairs,
                           parse_constant=constant, parse_float=finite)
    except (UnicodeError, ValueError, RecursionError) as e:
        raise TransactionError('invalid envelope JSON') from e
    if object_required:
        need(type(value) is dict, 'envelope object required')
    return value

def read_snapshot(directory: str | Path, receipt: dict, expected_identity: dict, codec) -> dict:
    """Read from pinned no-follow descriptors, authenticate everything, then return.

    Caller must enforce an external process memory/time budget for Python JSON
    object graphs. This function bounds encoded I/O, not process RSS. It never
    edits files or erases partial transactions. It does not authenticate a
    malicious same-user producer or promise stability after descriptors close.
    """
    need(type(receipt) is dict and set(receipt) ==
         {'kind', 'complete', 'syncPolicy', 'root', 'artifact', 'envelope'}, 'transaction receipt schema')
    need(receipt['kind'] == 'R03PosixDiagnosticTransactionV2' and receipt['complete'] is True,
         'independently authenticated successful transaction required')
    need(receipt['syncPolicy'] in ('F_FULLFSYNC-files+fsync-directory', 'fsync-files+fsync-directory'),
         'known synchronization policy')
    root_expected = _file_receipt(receipt['root'], 0, root=True)
    artifact_expected = _file_receipt(receipt['artifact'], ARTIFACT_MAX)
    envelope_expected = _file_receipt(receipt['envelope'], INLINE_MAX)
    need(artifact_expected['bytes'] >= 192, 'complete artifact minimum')
    name = os.fspath(directory)
    need(type(name) is str and name.startswith('/') and '\x00' not in name and
         len(os.fsencode(name)) < 4096, 'absolute bounded path')
    parts = name.split('/')[1:]
    need(0 < len(parts) < 64 and all(p and p not in ('.', '..') and len(os.fsencode(p)) <= 255
                                    for p in parts), 'canonical path components')
    dirs = []
    files = []
    owned_fds = []
    try:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        fd = os.open('/', flags)
        owned_fds.append(fd)
        dirs.append((fd, None, os.fstat(fd)))
        for part in parts:
            fd = os.open(part, flags, dir_fd=dirs[-1][0])
            owned_fds.append(fd)
            dirs.append((fd, part, os.fstat(fd)))
        _matches(dirs[-1][2], root_expected, root=True)
        def chain():
            for i, (fd, part, initial) in enumerate(dirs):
                current = os.fstat(fd)
                need(_identity(current) == _identity(initial) and current.st_nlink > 0 and
                     stat.S_ISDIR(current.st_mode), 'directory identity changed')
                if i:
                    named = os.stat(part, dir_fd=dirs[i-1][0], follow_symlinks=False)
                    need(_identity(named) == _identity(current), 'ancestor replaced')
        chain()
        for file_name, expected in ((ARTIFACT, artifact_expected), (ENVELOPE, envelope_expected)):
            fd = os.open(file_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                         dir_fd=dirs[-1][0])
            owned_fds.append(fd)
            files.append((fd, file_name, expected, os.fstat(fd)))
            _matches(files[-1][3], expected)
        def same_files():
            chain()
            for fd, file_name, expected, before in files:
                now = os.fstat(fd)
                _matches(now, expected)
                named = os.stat(file_name, dir_fd=dirs[-1][0], follow_symlinks=False)
                need(_stable(now) == _stable(before) == _stable(named), 'file changed during verification')
        same_files()
        # All original descriptors stay retained through the final identity
        # checks. The stream wrappers do not own or duplicate those descriptors.
        with os.fdopen(files[1][0], 'rb', closefd=False) as stream:
            data = stream.read(envelope_expected['bytes'] + 1)
        need(len(data) == envelope_expected['bytes'] and
             hashlib.sha256(data).hexdigest() == envelope_expected['sha256'], 'envelope hash/length')
        raw = _json(data)
        need(raw.get('reportTransport') == 'NativeBoundedSnapshotV2' and
             'diagnosticArtifact' in raw, 'explicit V2 descriptor required')
        inline = {k: v for k, v in raw.items() if k != 'diagnosticArtifact'}
        need(not any(k in inline for k in codec.FIELDS), 'inline diagnostic collision')
        descriptor = raw['diagnosticArtifact']
        need(type(descriptor) is dict and descriptor.get('bytes') == artifact_expected['bytes'] and
             descriptor.get('sha256') == artifact_expected['sha256'], 'independent artifact receipt mismatch')
        with os.fdopen(files[0][0], 'rb', closefd=False) as stream:
            decoded = codec.decode(stream, descriptor, expected_identity, inline)
        for value in decoded.values():
            if value is not None:
                codec.strict_json(value)
                _json(value.encode('utf-8'), object_required=False)
        same_files()
        return {**inline, **decoded}  # Never relabel this as V1 or change result.
    except OSError as e:
        raise TransactionError(f'filesystem verification failed: {e.errno}') from e
    finally:
        # The operation is read-only. Do not retry close on an uncertain result.
        pending = sys.exc_info()[0] is not None
        close_failure = None
        for fd in reversed(owned_fds):
            try:
                os.close(fd)
            except OSError as e:
                if close_failure is None:
                    close_failure = e
        if close_failure is not None and not pending:
            raise TransactionError('descriptor close failed') from close_failure
