#!/usr/bin/env python3
"""Authenticated host-side V2 consumer. Not installed in the Player/runner.

The caller supplies an independently authenticated directory/file receipt and
request/build/source/launch context. These are trust inputs, NOT extracted from
the artifact being checked. Integrity hashes alone are not producer signatures.
V1 remains in run_terminal_local.verify_ir. Never rewrite V2 into fake V1 raw.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys

# -I workers import only this exact source directory, never PYTHONPATH/user site.
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from NativeDiagnostics import diagnostic_wire as wire

class AdmissionError(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise AdmissionError(reason)

# Explicit parser budgets, distinct from encoded transport and runtime memory.
JSON_DEPTH = 64
JSON_TOKENS = 131072
NUMBER_CHARS = 128
MEMORY_BYTES = 512 * 1024 * 1024
CPU_SECONDS = 8
WALL_SECONDS = 15
INPUT_BYTES = 65536
STAMP_KEYS = ('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink',
              'st_size','st_mtime_ns','st_ctime_ns')
DIR_KEYS = ('st_dev','st_ino','st_uid','st_gid','st_mode')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounded_json(text, maximum):
    """Bound structure BEFORE json.loads; reject duplicates/nonfinite numbers."""
    need(type(text) is str, 'JSON text type')
    try:
        need(len(text.encode('utf-8',errors='strict')) <= maximum, 'JSON byte budget')
    except UnicodeError as exc:
        raise AdmissionError('JSON UTF-8') from exc
    depth = tokens = 0
    quoted = escaped = False
    for c in text:
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
            tokens += 1
        elif c in '[{':
            depth += 1
            tokens += 1
            need(depth <= JSON_DEPTH, 'JSON depth budget')
        elif c in ']}':
            depth -= 1
            need(depth >= 0, 'JSON unbalanced container')
        elif c in ',:':
            tokens += 1
        need(tokens <= JSON_TOKENS, 'JSON token budget')
    need(not quoted and depth == 0, 'JSON incomplete structure')
    def pairs(items):
        result = {}
        for k,v in items:
            need(k not in result, 'JSON duplicate key')
            result[k] = v
        return result
    def number(value):
        need(len(value) <= NUMBER_CHARS, 'JSON numeric budget')
        n = float(value)
        need(math.isfinite(n), 'JSON nonfinite value')
        return n
    def integer(value):
        need(len(value) <= NUMBER_CHARS, 'JSON numeric budget')
        return int(value)
    def constant(_):
        raise AdmissionError('JSON nonfinite value')
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_float=number,
                           parse_int=integer, parse_constant=constant)
        # JSON escapes can contain unpaired UTF-16 surrogates despite UTF-8
        # input bytes. Never normalize such strings into a semantic witness.
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, str):
                try:
                    item.encode('utf-8', errors='strict')
                except UnicodeError as exc:
                    raise AdmissionError('JSON unpaired surrogate') from exc
            elif isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
        return value
    except (ValueError,RecursionError,OverflowError) as exc:
        if isinstance(exc, AdmissionError):
            raise
        raise AdmissionError('JSON syntax') from exc


def stamp(s, keys=STAMP_KEYS):
    return {k:getattr(s,k) for k in keys}


def _validate_stamp(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'Receipt stat schema')
    need(all(type(value[k]) is int and value[k] >= 0 for k in keys), 'Receipt stat values')
    need(value['st_ino'] > 0 and value['st_uid'] == os.geteuid(), 'Receipt owner/inode')


def _validate_file(value, maximum):
    need(type(value) is dict and set(value) == {'stat','sha256'}, 'Receipt file schema')
    _validate_stamp(value['stat'], STAMP_KEYS)
    s = value['stat']
    need(stat.S_ISREG(s['st_mode']) and stat.S_IMODE(s['st_mode']) == 0o600
         and s['st_nlink'] == 1, 'Receipt file type/mode/link')
    need(0 < s['st_size'] <= maximum, 'Receipt file size budget')
    need(wire.hex_value(value['sha256'],64), 'Receipt file digest')


def _check_file(fd, directory, name, expected):
    # Compare both retained FD and current descriptor-relative name. A private,
    # caller-admitted directory is required; this is not adversarial user isolation.
    need(stamp(os.fstat(fd)) == expected['stat'], 'File FD identity changed')
    need(stamp(os.stat(name,dir_fd=directory,follow_symlinks=False)) == expected['stat'],
         'File name identity changed')


def _open_file(directory, name, expected):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    fd = os.open(name,flags,dir_fd=directory)
    try:
        _check_file(fd,directory,name,expected)
    except BaseException:
        os.close(fd)
        raise
    return fd


def verify_v2_pair(directory_fd, authority, request_text, launch, build_sha, pins):
    """Read one fixed raw.json + diagnostics.v2 pair, return only a small receipt.

    This in-process primitive is for tests/integration. Use verify_isolated for
    untrusted artifact parsing. No filesystem writes, Unity invocation or source
    mutation occur here. The caller retains independent evidence authenticity.
    """
    need(type(directory_fd) is int and directory_fd >= 0, 'Directory descriptor')
    need(type(authority) is dict and set(authority) == {'kind','directory','raw','artifact'},
         'Authority schema')
    need(authority['kind'] == 'R03BoundedPairAuthorityV2', 'Authority kind')
    _validate_stamp(authority['directory'], DIR_KEYS)
    d = authority['directory']
    need(stat.S_ISDIR(d['st_mode']) and stat.S_IMODE(d['st_mode']) == 0o700,
         'Private directory mode')
    _validate_file(authority['raw'],wire.RESERVE)
    _validate_file(authority['artifact'],wire.MAX_STREAM)
    need(authority['raw']['stat']['st_ino'] != authority['artifact']['stat']['st_ino'],
         'Distinct files required')
    need(authority['raw']['stat']['st_size'] + authority['artifact']['stat']['st_size'] <= wire.TOTAL,
         'Pooled transport budget')
    need(type(launch) is dict and type(launch.get('pid')) is int
         and type(launch.get('exitCode')) is int and launch['exitCode'] == 0,
         'Original Player command must succeed')
    need(wire.hex_value(build_sha,64), 'Build digest')
    need(type(pins) is dict and set(pins) == {'hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus'},
         'Four source pins')
    need(type(request_text) is str, 'Exact request UTF-8 text')
    request = bounded_json(request_text,16384)
    need(type(request) is dict and request.get('stimulus') in ('baseline-owner','type-resolution','off'),
         'Snapshot case; engine witness requires original engine verifier')
    identity = {'runId':request.get('runId'),'caseId':request.get('caseId'),
                'processId':launch['pid'],'requestSha256':digest(request_text.encode('utf-8')),
                'buildSha256':build_sha,'demoCommit':pins['hybridclr_demo'],
                'hybridclrCommit':pins['hybridclr'],'packageCommit':pins['hybridclr_unity'],
                'nativeCommit':pins['il2cpp_plus']}
    wire.binding(identity)  # Validate externally supplied identity before file I/O.
    directory = os.dup(directory_fd)
    raw_fd = artifact_fd = None
    try:
        os.set_inheritable(directory,False)
        need(stamp(os.fstat(directory),DIR_KEYS) == d, 'Directory identity changed')
        raw_fd = _open_file(directory,'raw.json',authority['raw'])
        artifact_fd = _open_file(directory,'diagnostics.v2',authority['artifact'])
        with os.fdopen(raw_fd,'rb',closefd=False) as stream:
            envelope = stream.read(authority['raw']['stat']['st_size']+1)
        need(len(envelope) == authority['raw']['stat']['st_size']
             and digest(envelope) == authority['raw']['sha256'], 'Original raw bytes/digest')
        try:
            raw = bounded_json(envelope.decode('utf-8',errors='strict'),wire.RESERVE)
        except UnicodeError as exc:
            raise AdmissionError('Envelope UTF-8') from exc
        need(type(raw) is dict and raw.get('reportTransport') == 'NativeBoundedSnapshotV2',
             'Explicit V2 transport; no automatic V1 fallback')
        need(raw.get('requestSha256') == identity['requestSha256'], 'Original raw/launch request digest')
        expected = raw.get('diagnosticArtifact')
        need(type(expected) is dict and expected.get('bytes') == authority['artifact']['stat']['st_size']
             and expected.get('sha256') == authority['artifact']['sha256'],
             'Sidecar must match external original receipt')
        inline = {k:v for k,v in raw.items() if k != 'diagnosticArtifact'}
        # Never accept inline/sidecar diagnostic collisions or alternate paths.
        wire.inline_bytes(inline)
        with os.fdopen(artifact_fd,'rb',closefd=False) as stream:
            fields = wire.decode(stream,expected,identity,inline)
        # Authentication of both complete fields/footer must finish before JSON
        # parsing or original semantic predicates can observe either field.
        for value in fields.values():
            if value is not None:
                bounded_json(value,wire.MAX_STREAM)
        for name in ('firstRecovery','finalRecovery','nativeGuardJson'):
            value = inline.get(name)
            if value is not None:
                bounded_json(value,wire.RESERVE)
        _check_file(raw_fd,directory,'raw.json',authority['raw'])
        _check_file(artifact_fd,directory,'diagnostics.v2',authority['artifact'])
        need(stamp(os.fstat(directory),DIR_KEYS) == d, 'Directory identity changed')
        semantic_view = {**inline,**fields}  # Stays explicitly tagged V2.
        from run_terminal_local import _verify_ir_semantics
        semantic = _verify_ir_semantics(semantic_view,request,launch,build_sha)
        _check_file(raw_fd,directory,'raw.json',authority['raw'])
        _check_file(artifact_fd,directory,'diagnostics.v2',authority['artifact'])
        need(stamp(os.fstat(directory),DIR_KEYS) == d, 'Directory identity changed')
        return {'kind':'R03VerifiedBoundedSnapshotV2','transport':'NativeBoundedSnapshotV2',
                'result':'Passed','semantic':semantic,'runtimeAcceptance':False,
                'rawSha256':authority['raw']['sha256'],'artifactSha256':authority['artifact']['sha256'],
                'identityBinding':expected['binding'],
                'fields':{name:{'isNull':value is None,'utf8Bytes':0 if value is None else len(value.encode('utf-8')),
                                'sha256':digest(b'' if value is None else value.encode('utf-8'))}
                          for name,value in fields.items()}}
    finally:
        # Close each owned FD even if another close fails; no delete/retry/reseal.
        error = None
        for fd in (artifact_fd,raw_fd,directory):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError as exc:
                    error = error or exc
        if error is not None:
            raise error


def verify_isolated(directory_fd, authority, request_text, launch, build_sha, pins):
    """Fixed-budget verifier child. No process resource settings change in parent."""
    data = wire.canonical({'authority':authority,'requestText':request_text,'launch':launch,
                           'buildSha256':build_sha,'pins':pins})
    need(len(data) <= INPUT_BYTES, 'Worker input bound')
    result = subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',str(directory_fd)],
        input=data,capture_output=True,pass_fds=(directory_fd,),timeout=WALL_SECONDS,
        env={**os.environ,'PYTHONOPTIMIZE':'','PYTHONDONTWRITEBYTECODE':'1'})
    need(result.returncode == 0 and len(result.stdout) <= INPUT_BYTES, 'Verifier worker rejected or failed')
    answer = bounded_json(result.stdout.decode('utf-8'),INPUT_BYTES)
    need(type(answer) is dict and answer.get('kind') == 'R03VerifiedBoundedSnapshotV2'
         and answer.get('result') == 'Passed', 'Verifier response contract')
    return answer


def _worker(fd):
    import resource
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY_BYTES,MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU_SECONDS,CPU_SECONDS+1))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_FSIZE,(0,0))
    data = sys.stdin.buffer.read(INPUT_BYTES+1)
    need(len(data) <= INPUT_BYTES, 'Worker input bound')
    record = bounded_json(data.decode('utf-8'),INPUT_BYTES)
    need(type(record) is dict and set(record) == {'authority','requestText','launch','buildSha256','pins'},
         'Worker input schema')
    answer = verify_v2_pair(fd,record['authority'],record['requestText'],record['launch'],
                            record['buildSha256'],record['pins'])
    sys.stdout.buffer.write(wire.canonical(answer)+b'\n')


if __name__ == '__main__':
    try:
        need(len(sys.argv) == 3 and sys.argv[1] == '--worker', 'Only inherited-descriptor worker mode')
        _worker(int(sys.argv[2]))
    except Exception as exc:
        # Never print untrusted diagnostic text, secret file paths or a fake PASS.
        sys.stderr.write('V2ConsumerRejected: '+type(exc).__name__+'\n')
        sys.exit(2)
