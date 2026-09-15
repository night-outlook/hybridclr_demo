"""Bounded failure evidence owned by one newly created capture attempt.

This journal is diagnostic-only. It cannot create a build receipt, alter an old
attempt, approve a macro domain, or substitute for compiler/PCH execution.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import traceback
import uuid

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_FILES = 4096


def encode(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def new_file(path: Path, raw: bytes) -> None:
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


class RetentionError(ValueError):
    pass


class Attempt:
    def __init__(self, root: Path, operation: str, *, max_file_bytes=MAX_FILE_BYTES,
                 max_total_bytes=MAX_TOTAL_BYTES, max_files=MAX_FILES):
        self.root = Path(root)
        if not self.root.is_absolute() or self.root != self.root.resolve():
            raise RetentionError('Capture attempt root must be absolute and canonical')
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise RetentionError('Symlink in capture attempt root')
        if any(type(x) is not int or x <= 0 for x in (max_file_bytes, max_total_bytes, max_files)):
            raise RetentionError('Invalid retention bound')
        if self.root.exists():
            raise RetentionError('Capture attempt root must be new')
        self.root.mkdir(parents=True, exist_ok=False, mode=0o700)
        self.inputs = self.root / 'attempt-inputs'
        self.inputs.mkdir(mode=0o700)
        self.limits = (max_file_bytes, max_total_bytes, max_files)
        self.rows = []
        self.used_bytes = 0
        self.seen = {}
        self.content_hashes = set()
        self.inventory = self.root / 'attempt-inputs.jsonl'
        new_file(self.inventory, b'')
        self.state = {'schemaVersion': 1, 'kind': 'H1CaptureAttempt', 'operation': operation,
            'status': 'InProgress', 'stage': 'created', 'diagnosticOnly': True,
            'candidateAcceptance': False, 'humanGatePassed': False, 'mayEnterR02': False,
            'planning': 'NotRun', 'pchReplay': 'NotRun', 'macroProbes': 'NotRun',
            'transitivePchHeaders': 'NotDiscoveredBeforePchInspection'}
        self._state()

    def _state(self) -> None:
        self.state['retainedInputCount'] = len(self.rows)
        self.state['retainedUniqueBytes'] = self.used_bytes
        tmp = self.root / ('attempt-state-' + uuid.uuid4().hex + '.tmp')
        new_file(tmp, encode(self.state))
        os.replace(tmp, self.root / 'attempt-state.json')

    def stage(self, stage: str, **facts) -> None:
        self.state.update(stage=stage, **facts)
        self._state()

    def _record(self, row: dict) -> dict:
        if len(self.rows) >= self.limits[2]:
            raise RetentionError('Capture input inventory exceeds retention count bound')
        # Append, do not rewrite already retained observations.
        with self.inventory.open('ab') as stream:
            stream.write(encode(row).replace(b'\n', b'') + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        self.rows.append(row)
        return row

    def keep_bytes(self, source: str, raw: bytes, role: str) -> dict:
        if type(raw) is not bytes:
            raise RetentionError('Retention requires bytes')
        digest = hashlib.sha256(raw).hexdigest()
        key = (str(source), role)
        previous = self.seen.get(key)
        if previous is not None:
            if previous['sha256'] != digest:
                raise RetentionError('Capture input changed during retention: ' + str(source))
            return previous
        if len(raw) > self.limits[0] or (digest not in self.content_hashes and
                self.used_bytes + len(raw) > self.limits[1]):
            self._record({'sourcePath': str(source), 'role': role, 'status': 'RetentionBoundExceeded',
                          'bytes': len(raw), 'sha256': digest})
            raise RetentionError('Capture input exceeds retention byte bound: ' + str(source))
        if len(self.rows) >= self.limits[2]:
            raise RetentionError('Capture input inventory exceeds retention count bound')
        target = self.inputs / (digest + '.bin')
        if digest not in self.content_hashes:
            new_file(target, raw)
            self.content_hashes.add(digest)
            self.used_bytes += len(raw)
        row = self._record({'sourcePath': str(source), 'role': role, 'status': 'Retained',
            'retainedPath': str(target), 'bytes': len(raw), 'sha256': digest})
        self.seen[key] = row
        return row

    def read_file(self, path: Path, role: str, *, required=True) -> bytes | None:
        path = Path(path)
        try:
            if not path.is_absolute() or path != path.resolve() or any(
                    p.is_symlink() for p in (path, *path.parents)):
                raise RetentionError('Input must be absolute, canonical, and not symlinked')
            with path.open('rb') as stream:
                before = os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode):
                    raise RetentionError('Input is not a regular file')
                if before.st_size > self.limits[0]:
                    raise RetentionError('Input exceeds per-file retention bound')
                raw = stream.read(self.limits[0] + 1)
                after = os.fstat(stream.fileno())
            if any(p.is_symlink() for p in (path, *path.parents)):
                raise RetentionError('Input became symlinked during read')
            current = path.stat()
            identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            if identity(before) != identity(after) or identity(after) != identity(current) or len(raw) != after.st_size:
                raise RetentionError('Input changed during read')
        except (OSError, ValueError) as error:
            self._record({'sourcePath': str(path), 'role': role, 'status': 'UnavailableToRetention',
                'errorType': type(error).__name__, 'error': str(error)})
            if required:
                raise
            return None
        # Retention budget exhaustion is fatal even for an optional file.
        self.keep_bytes(str(path), raw, role)
        return raw

    def retain_declared_inputs(self, graph: dict, project: Path) -> None:
        """Snapshot declared text/PCH inputs without executing an unvalidated action.

        Transitive includes not enumerated in the graph remain explicitly unknown.
        Compiler/native binaries are not silently copied into this small journal.
        """
        suffixes = {'.pch', '.h', '.hpp', '.hxx', '.c', '.cpp', '.cc', '.cxx', '.m', '.mm', '.rsp', '.plist'}
        selected = set()
        nodes = graph.get('Nodes', [])
        if type(nodes) is not list:
            return
        for node in nodes:
            if type(node) is not dict or not str(node.get('Annotation', '')).startswith(('C_Mac_arm64', 'Link_Mac_arm64')):
                continue
            for key in ('Inputs', 'Outputs'):
                values = node.get(key, [])
                if type(values) is not list:
                    continue
                for source in values:
                    if type(source) is not str or not source or '\0' in source:
                        continue
                    path = Path(os.path.abspath(source if os.path.isabs(source) else project / source))
                    if path.suffix in suffixes and (key == 'Inputs' or path.suffix == '.pch'):
                        selected.add(path)
                        if len(selected) > self.limits[2]:
                            raise RetentionError('Declared input inventory exceeds retention bound')
        for path in sorted(selected):
            self.read_file(path, 'declared-native-input', required=False)

    def finish(self, status: str) -> None:
        self.state.update(status=status)
        self._state()

    def fail(self, error: BaseException) -> None:
        if self.state['stage'] == 'planning' and self.state['planning'] == 'Started':
            self.state['planning'] = 'Failed'
        self.state.update(status='FailedNotAccepted', errorType=type(error).__name__, error=str(error))
        self._state()
        failure = dict(self.state)
        failure['traceback'] = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        raw = self.inventory.read_bytes()
        failure['inputInventorySha256'] = hashlib.sha256(raw).hexdigest()
        new_file(self.root / 'attempt-failure.json', encode(failure))

    @contextmanager
    def guard(self):
        try:
            yield self
        except BaseException as error:
            try:
                self.fail(error)
            except BaseException as retention_error:
                # The original product/parser exception remains the propagated cause.
                try:
                    error.add_note('Failure-journal write also failed: ' + str(retention_error))
                except AttributeError:
                    pass
            raise
