"""Kernel birth identity for the owned Unity command; never enumerate other users.

Darwin PROC_PIDTBSDINFO arg=1 includes zombies. Unlike ps's display fields,
start_tvsec/start_tvusec remain the process birth time during exit. See the
Apple proc_info.h/proc_info.c references in the batch-D repair design.
"""
from __future__ import annotations
import ctypes
import errno
import os
from pathlib import Path
import sys
from evidence import require


class BsdInfo(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        'flags', 'status', 'xstatus', 'pid', 'ppid', 'uid', 'gid', 'ruid',
        'rgid', 'svuid', 'svgid', 'reserved')] + [
        ('comm', ctypes.c_char * 16), ('name', ctypes.c_char * 32)] + [
        (name, ctypes.c_uint32) for name in ('nfiles', 'pgid', 'jobc', 'tdev', 'tpgid')
    ] + [('nice', ctypes.c_int32), ('start_sec', ctypes.c_uint64), ('start_usec', ctypes.c_uint64)]


def darwin_identity(pid):
    require(ctypes.sizeof(BsdInfo) == 136, 'Unsupported proc_bsdinfo ABI')
    lib = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
    call = lib.proc_pidinfo
    call.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
    call.restype = ctypes.c_int
    info = BsdInfo()
    ctypes.set_errno(0)
    size = call(pid, 3, 1, ctypes.byref(info), ctypes.sizeof(info))
    if size == 0 and ctypes.get_errno() == errno.ESRCH:
        return None
    require(size == ctypes.sizeof(info), 'proc_pidinfo failed or truncated: errno=' + str(ctypes.get_errno()))
    require(info.pid == pid and info.start_sec > 0 and info.start_usec < 1000000,
            'Invalid kernel process birth identity')
    return dict(source='DarwinProcBsdInfo', birth=[info.start_sec, info.start_usec],
                pid=info.pid, group=info.pgid, uid=info.uid, parent=info.ppid,
                status=info.status, exiting=bool(info.flags & 4), zombie=info.status == 5)


def linux_identity(pid):
    path = Path('/proc') / str(pid)
    try:
        # comm is enclosed in parentheses and may itself contain spaces/').
        text = (path / 'stat').read_text()
        fields = text[text.rindex(')') + 2:].split()
        return dict(source='LinuxProcStat', birth=[int(fields[19])], pid=pid,
                    group=int(fields[2]), parent=int(fields[1]), uid=path.stat().st_uid,
                    status=fields[0], exiting=fields[0] in ('Z', 'X'), zombie=fields[0] == 'Z')
    except (FileNotFoundError, ProcessLookupError):
        return None


def kernel_identity(pid):
    require(type(pid) is int and pid > 0, 'Positive process ID required')
    if sys.platform == 'darwin':
        return darwin_identity(pid)
    if sys.platform.startswith('linux'):
        return linux_identity(pid)
    raise ValueError('Kernel birth identity unavailable on this host')


def same_birth(a, b):
    return a is not None and b is not None and all(a.get(k) == b.get(k) for k in (
        'source', 'birth', 'pid', 'group', 'uid')) and bool(a.get('birth'))


def attach(row):
    info = kernel_identity(row['pid'])
    if info is None:
        return None
    require(info['group'] == row['group'], 'Process group changed during census')
    require(info['uid'] == os.getuid(), 'Owned process has unexpected user identity')
    return dict(row, kernel=info)
