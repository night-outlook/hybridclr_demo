"""Strict read-only resolver for an externally authenticated V2 commit receipt.

Inactive: no existing Player/verifier dispatch is replaced. The codec argument
must be the version-pinned consumer, not code chosen by input. Expected identity
and commit receipt are trusted only after command/source/evidence authentication.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import stat

class ReceiptError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise ReceiptError(message)

def strict_json(data):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    def constant(value):
        raise ReceiptError('nonfinite JSON constant')
    def finite(value):
        number = float(value)
        need(math.isfinite(number), 'nonfinite JSON number')
        return number
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite)
    except (ValueError, UnicodeError, RecursionError) as e:
        raise ReceiptError('invalid JSON') from e

def _directory(root, expected):
    """No-follow each component; expected identity is never derived from input."""
    need(type(root) is str and root.startswith('/') and len(os.fsencode(root)) < 4096, 'absolute root')
    parts = root.split('/')[1:]
    need(parts and all(p not in ('', '.', '..') and len(os.fsencode(p)) <= 255 for p in parts), 'canonical root')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open('/', flags)
    try:
        for p in parts:
            new = os.open(p, flags, dir_fd=fd)
            old, fd = fd, new
            os.close(old)
        _check_directory(os.fstat(fd), expected)
        return fd
    except BaseException:
        os.close(fd)
        raise

def _check_directory(st, expected):
    need(stat.S_ISDIR(st.st_mode) and st.st_dev == expected['device'] and
         st.st_ino == expected['inode'] and st.st_uid == expected['owner'] == os.geteuid() and
         st.st_nlink > 0 and not st.st_mode & 0o022, 'directory identity')

def _file(st, expected):
    need(stat.S_ISREG(st.st_mode) and st.st_dev == expected['device'] and
         st.st_ino == expected['inode'] and st.st_uid == os.geteuid() and
         st.st_nlink == 1 and stat.S_IMODE(st.st_mode) == 0o600 and
         st.st_size == expected['bytes'], 'file identity/length')

def _read(fd, name, expected, maximum):
    need(type(expected) is dict and set(expected) == {'device','inode','bytes','sha256'}, 'file receipt schema')
    need(all(type(expected[k]) is int and expected[k] >= 0 for k in ('device','inode','bytes')), 'file integers')
    need(0 < expected['bytes'] <= maximum, 'file bound')
    h = expected['sha256']
    need(type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h), 'file digest')
    child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=fd)
    try:
        _file(os.fstat(child), expected)
        pieces = []
        left = expected['bytes']
        while left:
            piece = os.read(child, min(65536, left))
            need(bool(piece), 'short file')
            pieces.append(piece)
            left -= len(piece)
        need(os.read(child, 1) == b'', 'trailing file')
        data = b''.join(pieces)
        need(hashlib.sha256(data).hexdigest() == h, 'file bytes')
        _file(os.fstat(child), expected)
        _file(os.stat(name, dir_fd=fd, follow_symlinks=False), expected)
        return data
    finally:
        os.close(child)

def read_transaction(root, expected_directory, receipt, identity, codec):
    """All checks precede any return. Returns tagged V2 data, NOT a V1 rewrite.

    Bounds encoded input; does not claim a hard bound on Python object RSS.
    Calls no semantic predicate and cannot turn a Failed report into Passed.
    """
    need(type(expected_directory) is dict and set(expected_directory) == {'device','inode','owner'}, 'directory schema')
    need(all(type(v) is int and v >= 0 for v in expected_directory.values()), 'directory integers')
    need(type(receipt) is dict and set(receipt) == {'complete','directory','artifact','envelope'}, 'commit receipt schema')
    need(type(receipt['directory']) is dict and set(receipt['directory']) == set(expected_directory) and
         all(type(v) is int for v in receipt['directory'].values()), 'receipt directory types')
    need(receipt['complete'] is True and receipt['directory'] == expected_directory, 'durable commit required')
    # Validate context before file I/O. The codec's binding rejects partial IDs.
    codec.binding(identity)
    root = os.fspath(root)
    fd = _directory(root, expected_directory)
    try:
        raw_bytes = _read(fd, 'raw.json', receipt['envelope'], codec.RESERVE)
        artifact = _read(fd, 'diagnostics.r03v2', receipt['artifact'], codec.MAX_STREAM)
        need(len(raw_bytes) + len(artifact) <= codec.TOTAL, 'aggregate bytes')
        raw = strict_json(raw_bytes)
        need(type(raw) is dict, 'envelope object')
        descriptor = raw.get('diagnosticArtifact')
        need(type(descriptor) is dict and descriptor.get('bytes') == len(artifact) and
             descriptor.get('sha256') == receipt['artifact']['sha256'], 'artifact receipt join')
        result = codec.hydrate(raw, artifact, descriptor, identity)
        need(result.get('reportTransport') == 'NativeBoundedSnapshotV2', 'tag preserved')
        for name in codec.FIELDS:
            if result[name] is not None:
                strict_json(result[name])
        # Revalidate descriptor-relative leaves and absolute root before return.
        _file(os.stat('raw.json', dir_fd=fd, follow_symlinks=False), receipt['envelope'])
        _file(os.stat('diagnostics.r03v2', dir_fd=fd, follow_symlinks=False), receipt['artifact'])
        _check_directory(os.fstat(fd), expected_directory)
        again = _directory(root, expected_directory)
        os.close(again)
        return result
    finally:
        os.close(fd)
