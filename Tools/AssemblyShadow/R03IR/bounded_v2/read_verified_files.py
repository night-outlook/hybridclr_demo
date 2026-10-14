"""Inactive file-acquisition component; caller authenticates the expected receipt.

No self-authentication from file-provided hashes. No semantic acceptance is
returned. The caller must still run the V2 codec and unchanged business checks.
"""
from __future__ import annotations
import hashlib
import os
import stat
from pathlib import Path

MAX_ENVELOPE = 262144
MAX_ARTIFACT = 3932160
NAMES = ('diagnostics.v2.bin', 'raw.json')

class FileContractError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise FileContractError(message)

def _walk(path: Path) -> int:
    text = os.fspath(path)
    need(isinstance(text, str) and text.startswith('/') and not text.endswith('/'), 'absolute directory')
    parts = text.split('/')[1:]
    need(parts and all(p not in ('', '.', '..') for p in parts), 'canonical components')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    current = os.open('/', flags)
    try:
        for part in parts:
            child = os.open(part, flags, dir_fd=current)
            previous, current = current, child
            os.close(previous)
        result, current = current, -1
        return result
    finally:
        if current >= 0:
            os.close(current)

def _identity(s):
    return dict(device=s.st_dev, inode=s.st_ino, owner=s.st_uid, mode=stat.S_IMODE(s.st_mode))

def _expected(value):
    need(type(value) is dict and set(value) == {'device','inode','owner','mode'}, 'identity schema')
    need(all(type(v) is int and 0 <= v < 2**64 for v in value.values()), 'identity numbers')
    need(value['inode'] > 0 and value['mode'] <= 0o7777, 'identity values')
    return value

def _digest(value):
    need(isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value), 'digest')
    return value

def _stamp(s):
    return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def read_verified_files(root: Path, expected: dict) -> tuple[bytes, bytes]:
    """Return (envelope, artifact) only after all receipt/file checks.

    expected must come from independently authenticated command/source/PID/run
    evidence, not an adjacent untrusted receipt. Bounds cover bytes, not process
    RSS or the later JSON graph. Concurrent malicious owner writes are not solved
    by hashes/stat; use the retained immutable snapshot and external evidence seal.
    """
    need(type(expected) is dict and expected.get('complete') is True, 'complete external receipt')
    directory = _expected(expected.get('directory'))
    records = []
    for key, identity, limit in [('artifact','artifactFile',MAX_ARTIFACT),('envelope','envelopeFile',MAX_ENVELOPE)]:
        value = expected.get(key)
        need(type(value) is dict and set(value)=={'bytes','sha256'}, 'file receipt schema')
        need(type(value['bytes']) is int and 0 < value['bytes'] <= limit, 'file byte bound')
        records.append((value['bytes'],_digest(value['sha256']),_expected(expected.get(identity))))
    directory_fd = _walk(root)
    handles = []
    before = []
    content = []
    try:
        ds = os.fstat(directory_fd)
        need(stat.S_ISDIR(ds.st_mode) and ds.st_uid==os.geteuid() and not(ds.st_mode & 0o022)
             and _identity(ds)==directory, 'directory identity')
        for name, (count, digest, identity) in zip(NAMES, records):
            fd = os.open(name, os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC, dir_fd=directory_fd)
            handles.append(fd)
            s = os.fstat(fd)
            named = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            need(stat.S_ISREG(s.st_mode) and stat.S_ISREG(named.st_mode) and s.st_nlink==named.st_nlink==1
                 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600
                 and _identity(s)==identity and _stamp(s)==_stamp(named) and s.st_size==count, 'file identity')
            before.append(s)
            data = bytearray()
            while len(data)<count:
                part=os.read(fd,min(65536,count-len(data)))
                need(bool(part),'short file')
                data.extend(part)
            need(os.read(fd,1)==b'', 'trailing file byte')
            need(hashlib.sha256(data).hexdigest()==digest,'full file hash')
            content.append(bytes(data))
        # Keep both descriptors open through the whole acquisition; then
        # independently recheck each bound name and unchanged metadata.
        for name,fd,s in zip(NAMES,handles,before):
            need(_stamp(os.fstat(fd))==_stamp(s) and
                 _stamp(os.stat(name,dir_fd=directory_fd,follow_symlinks=False))==_stamp(s), 'file changed during read')
        again=_walk(root)
        try:
            need(_identity(os.fstat(again))==directory and _identity(os.fstat(directory_fd))==directory,'directory changed')
        finally:
            os.close(again)
        # close errors must be surfaced before a successful return.
        while handles:
            os.close(handles.pop())
        owned, directory_fd = directory_fd, -1
        os.close(owned)  # Never retry a close after an error on a possibly reused FD.
        return content[1],content[0]
    finally:
        for fd in handles:
            os.close(fd)
        if directory_fd>=0:
            os.close(directory_fd)
