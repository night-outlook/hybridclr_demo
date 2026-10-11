"""Bounded, redacted Git observations; never retries or grants source authority.

Successful remote observations and all failures are retained by an active cell
scope. Before a scope exists, a failure carries the same receipt in its error.
Raw stdout/stderr remain private to this process; only hashes/lengths and bounded
redacted excerpts are persisted. Exit/timeout/spawn/decoding failures are distinct.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
from batch_contract import ContractError

LIMIT = 16384
TIMEOUT = 120
_SCOPE = ContextVar('assembly_shadow_git_receipts', default=None)
REPOS = ('hybridclr_demo', 'hybridclr', 'hybridclr_unity', 'il2cpp_plus')


def redact(text):
    # Remove whole credential-bearing values before truncating an excerpt.
    text = re.sub(r'(?i)([a-z][a-z0-9+.-]{0,31}://)[^/\s@]+@', r'\1[REDACTED]@', text)
    text = re.sub(r'(?i)(https?://[^\s?#]+)[?#][^\s]*', r'\1?[REDACTED]', text)
    text = re.sub(r'(?im)((?:proxy-)?authorization\s*[:=])[^\r\n]*', r'\1 [REDACTED]', text)
    text = re.sub(r'(?i)((?:password|passwd|token|secret|credential)\s*[=:]\s*)[^\s,;]+', r'\1[REDACTED]', text)
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b', '[REDACTED]', text)
    return text


def stream_record(raw):
    if raw is None:
        return {'available': False, 'bytes': None, 'sha256': None, 'excerpt': '', 'truncated': False}
    if isinstance(raw, str): raw = raw.encode('utf-8', errors='replace')
    text = redact(raw.decode('utf-8', errors='replace'))
    encoded = text.encode('utf-8')
    return {'available': True, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'excerpt': encoded[:LIMIT].decode('utf-8', errors='ignore'),
            'truncated': len(encoded) > LIMIT, 'redacted': text != raw.decode('utf-8', errors='replace')}


@contextmanager
def capture_git(directory, pins, phase):
    directory = Path(directory).absolute() if directory is not None else None
    if directory is not None and directory != directory.resolve():
        raise RuntimeError('Non-canonical Git evidence directory')
    authority = {k: pins[k] for k in (*REPOS, 'branch') if k in pins}
    token = _SCOPE.set((directory, authority, phase))
    try: yield
    finally: _SCOPE.reset(token)


def persist(receipt):
    scope = _SCOPE.get()
    if scope is None or scope[0] is None: return None
    root = scope[0]
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise RuntimeError('Symlinked Git evidence directory')
    root.mkdir(parents=True, exist_ok=True)
    path = root / (uuid.uuid4().hex + '.json')
    with path.open('x', encoding='utf-8') as file:
        json.dump(receipt, file, indent=2, sort_keys=True); file.write('\n')
        file.flush(); os.fsync(file.fileno())
    return str(path)


class GitCommandFailure(ContractError):
    def __init__(self, receipt, receipt_path=None):
        self.receipt, self.receipt_path = receipt, receipt_path
        summary = {'kind': receipt['kind'], 'repository': receipt['repository'],
                   'argv': receipt['argv'], 'status': receipt['status'], 'exitCode': receipt['exitCode'],
                   'receiptPath': receipt_path}
        # The pre-constructor storage gate has no active batch output. Preserve
        # its diagnostic directly in the already-owned caller exception receipt.
        if receipt_path is None: summary['observation'] = receipt
        super().__init__('Git command failed: ' + json.dumps(summary, sort_keys=True))


def run_git(repo, *args):
    argv = ['git', '-C', str(repo), *map(str, args)]
    scope = _SCOPE.get()
    started = datetime.now(timezone.utc).isoformat(); clock = time.monotonic_ns()
    out = err = None; code = None; failure = None; decoded = None; status = 'Passed'
    try:
        result = subprocess.run(argv, capture_output=True, env=dict(os.environ, GIT_TERMINAL_PROMPT='0'),
                                timeout=TIMEOUT)
        out, err, code = result.stdout, result.stderr, result.returncode
        if code != 0: status = 'NonzeroExit'
        else: decoded = out if isinstance(out, str) else out.decode('utf-8')
    except subprocess.TimeoutExpired as error:
        status, out, err = 'Timeout', error.stdout, error.stderr
        failure = {'type': type(error).__name__, 'timeoutSeconds': TIMEOUT}
    except OSError as error:
        status = 'SpawnError'
        failure = {'type': type(error).__name__, 'errno': error.errno, 'message': redact(str(error))}
    except UnicodeError as error:
        status = 'DecodeError'
        failure = {'type': type(error).__name__, 'message': 'Git output was not UTF-8'}
    receipt = {'schemaVersion': 1, 'kind': 'R03GitCommandObservation', 'repository': str(Path(repo).absolute()),
        'argv': [redact(a) for a in argv], 'argvRedacted': any(redact(a) != a for a in argv),
        'startUtc': started, 'endUtc': datetime.now(timezone.utc).isoformat(),
        'elapsedNanoseconds': time.monotonic_ns() - clock, 'timeoutSeconds': TIMEOUT,
        'exitCode': code, 'status': status, 'failure': failure,
        'stdout': stream_record(out), 'stderr': stream_record(err),
        'requestedSourceAuthority': scope[1] if scope else None, 'phase': scope[2] if scope else None,
        'sourceAuthorityValidatedByThisReceipt': False, 'attempt': 1, 'retryPerformed': False,
        'helperSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path = None
    if status != 'Passed' or (args and args[0] == 'ls-remote'):
        try: path = persist(receipt)
        except Exception as error:
            receipt['evidenceWriteFailure'] = {'type': type(error).__name__, 'message': redact(str(error))}
            if status == 'Passed': receipt['status'] = 'EvidenceWriteError'
            raise GitCommandFailure(receipt) from None
    if status != 'Passed': raise GitCommandFailure(receipt, path) from None
    return decoded.strip()
