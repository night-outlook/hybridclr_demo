"""Owned POSIX command lifetime; process-group cleanup never turns failure into PASS.

R03-LA-001: avoid persistent .NET workers at creation, not by globally stopping
servers after the build. Diagnostics are best-effort, bounded and non-authoritative.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

POLICY = 'R03OwnedCommandV1'
BUILD_FLAGS = ('--disable-build-servers', '-p:UseSharedCompilation=false', '-nodeReuse:false')
BUILD_ENV = {
    'DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER': '1',
    'DOTNET_CLI_USE_MSBUILD_SERVER': '0',
    'MSBUILDUSESERVER': '0',
    'MSBUILDDISABLENODEREUSE': '1',
}
MAX_MEMBERS = 64


def build_arguments(project, binary, intermediate, package):
    return ['dotnet', 'build', str(project), '-c', 'Release', '--output', str(binary),
            '-p:PackageRoot=' + str(package), '-p:BaseIntermediateOutputPath=' + str(intermediate) + '/',
            *BUILD_FLAGS]


def child_environment():
    # Never mutate the agent's environment or any unrelated build server.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0')
    env['TMPDIR'] = '/private/tmp' if sys.platform == 'darwin' else tempfile.gettempdir()
    env.update(BUILD_ENV)
    return env


def _write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # Inability to inspect is not evidence of absence.


def parse_members(text, pgid):
    members, count = [], 0
    for line in text.splitlines():
        fields = line.split(None, 4)
        if len(fields) != 5 or not all(f.isdigit() for f in fields[:3]):
            continue
        pid, ppid, group = map(int, fields[:3])
        if group != pgid:
            continue
        count += 1
        if len(members) < MAX_MEMBERS:
            members.append({'pid': pid, 'ppid': ppid, 'pgid': group,
                            'state': fields[3][:16], 'executable': fields[4][:512]})
    return {'members': members, 'observedCount': count, 'truncated': count > MAX_MEMBERS}


def group_snapshot(pgid):
    # comm, not args: do not persist other processes' command lines or environment.
    # macOS ps has no portable --pgroup; filter its bounded-duration numeric table.
    result = {'pgid': pgid, 'capturedUtcEpoch': time.time(), 'status': 'Unavailable'}
    try:
        ps = subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,stat=,comm='],
                            capture_output=True, text=True, timeout=3,
                            env=dict(os.environ, LC_ALL='C'))
        if ps.returncode == 0:
            result.update(parse_members(ps.stdout, pgid), status='Captured')
        else:
            result['error'] = 'ps exit ' + str(ps.returncode)
    except Exception as error:
        result['error'] = type(error).__name__
    return result


def run_owned_command(args, root, timeout=600):
    """Use a new root; record before raising. No survivor grace-to-PASS or retry."""
    if os.name != 'posix' or not args or timeout <= 0:
        raise ValueError('A POSIX command and positive timeout are required')
    root = Path(root)
    root.mkdir(parents=True)  # Existing command/evidence roots must never be reused.
    args = [str(x) for x in args]
    env = child_environment()
    start = time.time()
    process, code, start_error, interrupted = None, None, None, False
    timed_out, remaining_group = False, False
    cleanup_errors, diagnostics = [], None
    after_cleanup = None
    with (root / 'stdout.log').open('xb') as out, (root / 'stderr.log').open('xb') as err:
        try:
            process = subprocess.Popen(args, stdout=out, stderr=err, env=env, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
            except KeyboardInterrupt:
                interrupted = True
        except OSError as error:
            start_error = type(error).__name__ + ': ' + str(error)
        finally:
            if process is not None:
                pgid = process.pid  # start_new_session binds PGID to this child PID.
                remaining_group = group_exists(pgid)
                if remaining_group:
                    diagnostics = group_snapshot(pgid)
                    # A diagnostic failure cannot prevent cleanup or permit success.
                    try:
                        _write(root / 'process-group-before-cleanup.json', diagnostics)
                    except OSError as error:
                        cleanup_errors.append('diagnostic write: ' + type(error).__name__)
                    try:
                        if pgid <= 1 or pgid == os.getpgrp():
                            raise RuntimeError('Refusing to signal the caller process group')
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except Exception as error:
                        cleanup_errors.append('owned group kill: ' + type(error).__name__)
                try:
                    code = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    cleanup_errors.append('owned parent did not exit after SIGKILL')
                # Observe cleanup separately; never replace remainingProcessGroup.
                after_cleanup = group_exists(pgid)
    receipt = {
        'schemaVersion': 2, 'lifetimePolicy': POLICY,
        'command': args, 'pid': process.pid if process else None,
        'pgid': process.pid if process else None, 'cwd': str(Path.cwd()),
        'startedUtcEpoch': start, 'endedUtcEpoch': time.time(), 'exitCode': code,
        'timeout': timed_out, 'interrupted': interrupted, 'startError': start_error,
        'remainingProcessGroup': remaining_group, 'postCleanupGroupExists': after_cleanup,
        'cleanupErrors': cleanup_errors,
        'processGroupBeforeCleanup': diagnostics,
        'childEnvironmentPolicy': {k: env[k] for k in (*BUILD_ENV, 'TMPDIR', 'PYTHONDONTWRITEBYTECODE', 'GIT_TERMINAL_PROMPT')},
        'stdoutSha256': _sha(root / 'stdout.log'), 'stderrSha256': _sha(root / 'stderr.log'),
    }
    _write(root / 'command.json', receipt)
    if interrupted:
        raise KeyboardInterrupt
    if code != 0 or timed_out or remaining_group or start_error or cleanup_errors:
        raise RuntimeError('Command failed; preserved receipt: ' + str(root / 'command.json'))
    return receipt
