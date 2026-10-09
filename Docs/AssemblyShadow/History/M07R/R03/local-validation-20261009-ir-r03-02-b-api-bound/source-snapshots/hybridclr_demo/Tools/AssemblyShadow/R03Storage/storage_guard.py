"""R03-LQ-001: conservative admission and bounded storage observations.

No cleanup of user data, quota/snapshot changes, automatic retries or reservation.
Free-space samples and a small allocation probe cannot guarantee future capacity.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback

GIB = 1024 ** 3
START_MIN = 64 * GIB
MARGIN = 20 * GIB
FLOOR = 20 * GIB
INTERVAL = 5.0
PROBE_BYTES = 1024 ** 2
Q_CELL_SHA = 'b529089f337d7f3db9ce13069bccb229df08eaabf336f1cff5440e47d45d2a4f'
POLICY = 'R03StorageAdmissionV1'


class StorageBlocked(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise StorageBlocked(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical(path):
    """Reject relative paths, traversal, symlinks (including missing leaf aliases)."""
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'Absolute non-traversing path required')
    require(path.resolve() == path, 'Canonical path required: ' + str(path))
    for parent in (path, *path.parents):
        require(not parent.is_symlink(), 'Symlink is not storage authority: ' + str(parent))
    return path


def existing_parent(path):
    path = canonical(path)
    while not path.exists():
        path = path.parent
    require(path.is_dir(), 'Storage path must be a directory: ' + str(path))
    return path


def write_new(path, value):
    """Exclusive output; never overwrite a receipt, including a failed one."""
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def failure(error):
    return {'type': type(error).__name__, 'message': str(error),
            'errno': getattr(error, 'errno', None), 'filename': getattr(error, 'filename', None),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}


def footprint(root, *, max_entries=5000000, seconds=300):
    """Metadata-only size estimate. No symlink following or APFS sharing inference."""
    root = canonical(root)
    require(root.is_dir(), 'Retained Q live root required')
    started = time.monotonic()
    device = root.stat().st_dev
    logical = allocated = files = directories = symlinks = 0
    seen = set()
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=lambda e: (_ for _ in ()).throw(e)):
        base = Path(directory)
        require(base.stat().st_dev == device, 'Nested mount in retained root; separate sizing required')
        directories += 1
        for name in dirs + names:
            item = base / name
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode):
                symlinks += 1
                continue
            require(info.st_dev == device, 'Nested filesystem in retained root')
            if stat.S_ISREG(info.st_mode):
                files += 1
                logical += info.st_size
                key = (info.st_dev, info.st_ino)
                if key not in seen:
                    allocated += info.st_blocks * 512
                    seen.add(key)
            else:
                require(stat.S_ISDIR(info.st_mode), 'Special file in retained root: ' + str(item))
        dirs[:] = [name for name in dirs if not (base / name).is_symlink()]
        require(files + directories + symlinks <= max_entries and time.monotonic() - started <= seconds,
                'Sizing limit reached; incomplete sizes cannot authorize a batch')
    return {'path': str(root), 'files': files, 'directories': directories, 'symlinksNotFollowed': symlinks,
            'logicalBytesPerPath': logical, 'allocatedBytesUniqueInode': allocated,
            'planningBytes': max(logical, allocated), 'elapsedSeconds': time.monotonic() - started,
            'physicalApfsSharingKnown': False, 'includesRetainedLiveCaches': True}


def required_start(size):
    n = size['planningBytes']
    require(type(n) is int and n >= 0, 'Nonnegative integer size required')
    # One new retained batch, one publication copy, plus staging/headroom margin.
    # This is a deliberately conservative policy, not an observed peak or SLA.
    return max(START_MIN, 2 * n + MARGIN)


def sample(paths):
    rows = []
    for role, path in paths.items():
        ancestor = existing_parent(path)
        info, vfs = ancestor.stat(), os.statvfs(ancestor)
        unit = vfs.f_frsize or vfs.f_bsize
        require(type(unit) is int and unit > 0 and vfs.f_blocks > 0, 'Usable filesystem capacity report required')
        rows.append({'role': role, 'requestedPath': str(path), 'observedPath': str(ancestor),
                     'device': info.st_dev, 'fsid': getattr(vfs, 'f_fsid', None),
                     'availableBytes': max(0, vfs.f_bavail) * unit, 'freeBytes': max(0, vfs.f_bfree) * unit,
                     'totalBytes': vfs.f_blocks * unit, 'availableFileNodes': vfs.f_favail,
                     'readOnly': bool(vfs.f_flag & getattr(os, 'ST_RDONLY', 1))})
    return {'observedUtc': utc(), 'monotonicNs': time.monotonic_ns(), 'volumes': rows}


def capacity_ok(observation, required, original_devices=None):
    require(type(required) is int and required > 0, 'Positive capacity policy required')
    for row in observation['volumes']:
        require(not row['readOnly'], 'Read-only filesystem: ' + row['role'])
        require(row['availableBytes'] >= required,
                '%s: available %d < required %d bytes' % (row['role'], row['availableBytes'], required))
        if original_devices is not None:
            require((row['device'], row['fsid']) == original_devices[row['role']],
                    'Filesystem identity changed: ' + row['role'])
    require(bool(observation['volumes']), 'No storage locations observed')


def allocation_probe(parent):
    """Allocate/read/fsync 1 MiB in an owned directory. Remove ONLY our two paths."""
    parent = canonical(parent)
    require(parent.is_dir(), 'Existing probe parent required')
    report = {'parent': str(parent), 'bytes': PROBE_BYTES, 'result': 'Failed', 'reservation': False}
    folder = item = None
    phase = 'mkdir'
    try:
        folder = Path(tempfile.mkdtemp(prefix='.r03-storage-probe-', dir=parent))
        item = folder / 'allocation.bin'
        phase = 'write'
        data = os.urandom(PROBE_BYTES)
        with item.open('xb') as stream:
            stream.write(data)
            stream.flush()
            phase = 'fsync'
            os.fsync(stream.fileno())
        phase = 'readback'
        require(digest(item) == hashlib.sha256(data).hexdigest(), 'Allocation readback mismatch')
        report.update(result='Passed', allocatedBytes=item.stat().st_blocks * 512)
    except Exception as error:
        report.update(error=failure(error), failedOperation=phase)
    finally:
        errors = []
        if item is not None and item.exists():
            try:
                item.unlink()
            except OSError as error:
                errors.append(failure(error))
        if folder is not None:
            try:
                folder.rmdir()
            except OSError as error:
                errors.append(failure(error))
        report.update(cleanupErrors=errors, ownedDirectory=str(folder) if folder else None)
        if errors:
            report['result'] = 'Failed'
    return report


def diagnostics(paths):
    """Read-only tools before/after a batch, never process/environment sweeps."""
    commands = [['/bin/df', '-k', *dict.fromkeys(str(existing_parent(p)) for p in paths.values())]]
    if sys.platform == 'darwin':
        commands += [['/usr/sbin/diskutil', 'apfs', 'list', '-plist'], ['/usr/bin/quota', '-v']]
        for path in dict.fromkeys(str(existing_parent(p)) for p in paths.values()):
            commands.append(['/usr/sbin/diskutil', 'info', '-plist', path])
    rows = []
    for argv in commands:
        row = {'argv': argv, 'startedUtc': utc(), 'result': 'Unavailable'}
        try:
            result = subprocess.run(argv, capture_output=True, timeout=20, env=dict(os.environ, LC_ALL='C'))
            row.update(result='Captured' if result.returncode == 0 else 'Unavailable', exitCode=result.returncode,
                       stdout=result.stdout.decode('utf-8', 'replace'), stderr=result.stderr.decode('utf-8', 'replace'))
        except Exception as error:
            row['error'] = failure(error)
        row['endedUtc'] = utc()
        rows.append(row)
    return rows


class StorageSession:
    """Single-process sidecar, joined before result publication; never cancels Unity.

    A sampled breach is latched even if space later recovers. Cleanup/final
    authority remain callable. No allocation probe, tree walk or diskutil during
    Player measurement; the observer does only statvfs and a small JSONL append.
    """
    def __init__(self, root, paths, *, interval=INTERVAL):
        self.root = canonical(root)
        self.root.mkdir()  # unused, immediate existing parent required
        self.paths = {k: canonical(v) for k, v in paths.items()}
        self.interval = interval
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.thread = None
        self.devices = None
        self.admitted = False
        self.problem = None
        self.count = 0
        self.minimum = {}
        self.phase = 'admission'
        self.trace = (self.root / 'capacity.jsonl').open('x', encoding='utf-8')

    def observe(self, event):
        with self.lock:
            try:
                value = sample(self.paths)
                value.update(event=event, phase=self.phase, sequence=self.count)
                if self.devices is not None:
                    try:
                        capacity_ok(value, FLOOR, self.devices)
                    except Exception as error:
                        if self.problem is None:
                            self.problem = failure(error)
                for row in value['volumes']:
                    name = row['role']
                    self.minimum[name] = min(self.minimum.get(name, row['availableBytes']), row['availableBytes'])
                self.trace.write(json.dumps(value, sort_keys=True) + '\n')
                self.trace.flush()
                self.count += 1
                return value
            except Exception as error:
                if self.problem is None:
                    self.problem = failure(error)
                return None

    def admit(self, retained):
        report = {'kind': POLICY, 'state': 'Blocked', 'batchStarted': False, 'runtimeAcceptance': False,
                  'startMinimumBytes': START_MIN, 'operatingFloorBytes': FLOOR,
                  'marginBytes': MARGIN, 'capacityReserved': False}
        try:
            cell = canonical(canonical(retained) / 'cells/production-entry-integration.json')
            require(digest(cell) == Q_CELL_SHA, 'Exact preserved Q failed cell required')
            report['qFailedCellSha256'] = Q_CELL_SHA
            report['retainedQSize'] = footprint(retained)
            report['requiredAvailableBytesEachLocation'] = required_start(report['retainedQSize'])
            first = self.observe('admission-before-probes')
            require(first is not None, 'Storage observation unavailable')
            self.devices = {r['role']: (r['device'], r['fsid']) for r in first['volumes']}
            capacity_ok(first, report['requiredAvailableBytesEachLocation'])
            # Probe every location, even on one device: permissions/quotas differ.
            report['probes'] = [allocation_probe(existing_parent(p)) for p in self.paths.values()]
            require(all(r['result'] == 'Passed' for r in report['probes']), 'Allocation or owned probe cleanup failed')
            second = self.observe('admission-after-probes')
            require(second is not None and self.problem is None, 'Unreliable storage observation')
            capacity_ok(second, report['requiredAvailableBytesEachLocation'], self.devices)
            require(digest(cell) == Q_CELL_SHA, 'Retained Q evidence changed')
            report['state'] = 'Admitted'
            self.admitted = True
        except Exception as error:
            report['error'] = failure(error)
        report['diagnostics'] = diagnostics(self.paths)
        write_new(self.root / 'admission.json', report)
        return report

    def start(self):
        require(self.admitted and self.thread is None and not self.stop.is_set(), 'Admitted single storage observer invocation')
        def poll():
            while not self.stop.wait(self.interval):
                self.observe('periodic')
        self.thread = threading.Thread(target=poll, name='r03-storage', daemon=True)
        self.thread.start()

    def before(self, phase, *, cleanup=False):
        with self.lock:
            self.phase = phase
        self.observe('before')
        if not cleanup:
            require(self.problem is None, 'Storage prerequisite lost; preserve evidence and return to Primary: ' + str(self.problem))
        if phase == 'production-entry-integration':
            probe = allocation_probe(existing_parent(self.paths['restoredCapture']))
            write_new(self.root / 'integration-allocation-probe.json', probe)
            if probe['result'] != 'Passed':
                self.problem = {'type': 'AllocationProbeFailed', 'message': 'Pre-integration allocation probe failed', 'probe': probe}
            require(probe['result'] == 'Passed', 'Pre-integration allocation probe failed')

    def record_failure(self, phase, error):
        with self.lock:
            self.observe('exception')
            try:
                write_new(self.root / ('failure-%06d.json' % self.count),
                          {'phase': phase, 'observedUtc': utc(), 'error': failure(error)})
            except Exception as diagnostic_error:
                if self.problem is None:
                    self.problem = failure(diagnostic_error)
                print('Storage diagnostic unavailable: ' + str(diagnostic_error), file=sys.stderr)

    def finish(self, *, batch_started, batch_exit):
        self.stop.set()
        if self.thread is not None:
            self.thread.join(timeout=max(10, 2 * self.interval))
            require(not self.thread.is_alive(), 'Storage observer failed to stop; no completion claim')
        self.observe('finish')
        self.trace.close()
        report = {'kind': 'R03StorageSessionResult', 'batchStarted': batch_started, 'batchExitCode': batch_exit,
                  'state': ('Passed' if self.admitted else 'NotAdmitted') if self.problem is None else 'Failed', 'latchedProblem': self.problem,
                  'samples': self.count, 'minimumSampledAvailableBytes': self.minimum,
                  'sampledMinimumIsNotActualHighWater': True, 'sampleIntervalSeconds': self.interval,
                  'capacityReserved': False, 'runtimeAcceptance': False, 'historicalResultsModified': False,
                  'telemetrySha256': digest(self.root / 'capacity.jsonl'), 'observedUtc': utc()}
        report['diagnostics'] = diagnostics(self.paths)
        write_new(self.root / 'session.json', report)
        return report
