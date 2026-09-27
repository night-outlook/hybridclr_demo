import ctypes
import errno
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import process_identity as identity
import unity_session as session


class KernelIdentity(unittest.TestCase):
    def test_current_process_has_kernel_birth(self):
        observed = identity.kernel_identity(os.getpid())
        self.assertEqual(observed['pid'], os.getpid())
        self.assertEqual(observed['group'], os.getpgrp())
        self.assertEqual(observed['uid'], os.getuid())
        self.assertTrue(identity.same_birth(observed, identity.kernel_identity(os.getpid())))

    def test_native_layout_and_darwin_arguments_include_zombies(self):
        class Lib:
            pass
        def call(pid, flavor, arg, target, size):
            self.assertEqual((pid, flavor, arg, size), (123, 3, 1, 136))
            row = target._obj
            row.pid = 123; row.pgid = 100; row.uid = os.getuid()
            row.start_sec = 12345; row.start_usec = 678; row.flags = 4; row.status = 5
            return size
        lib = Lib(); lib.proc_pidinfo = call
        with patch.object(identity.ctypes, 'CDLL', return_value=lib):
            row = identity.darwin_identity(123)
        self.assertEqual(row['birth'], [12345, 678]); self.assertTrue(row['exiting']); self.assertTrue(row['zombie'])
        self.assertEqual(ctypes.sizeof(identity.BsdInfo), 136)

    def test_darwin_missing_is_distinct_from_permission_and_truncation(self):
        class Lib:
            pass
        for code, size, expected in ((errno.ESRCH, 0, None), (errno.EPERM, 0, ValueError), (0, 135, ValueError)):
            def call(*args):
                ctypes.set_errno(code); return size
            lib = Lib(); lib.proc_pidinfo = call
            with self.subTest(code=code, size=size), patch.object(identity.ctypes, 'CDLL', return_value=lib):
                if expected is None: self.assertIsNone(identity.darwin_identity(123))
                else:
                    with self.assertRaises(expected): identity.darwin_identity(123)

    def test_birth_change_user_or_group_change_is_not_same_instance(self):
        row = identity.kernel_identity(os.getpid())
        for key in ('birth', 'uid', 'group', 'pid', 'source'):
            altered = dict(row); altered[key] = 'different'
            self.assertFalse(identity.same_birth(row, altered))
        self.assertFalse(identity.same_birth({}, {}))

    def test_real_zombie_keeps_kernel_birth(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)'])
        try:
            before = identity.kernel_identity(child.pid)
            child.terminate()
            deadline = time.monotonic() + 4
            while time.monotonic() < deadline:
                after = identity.kernel_identity(child.pid)
                if after and after['zombie']: break
                time.sleep(.01)
            self.assertIsNotNone(after)
            self.assertTrue(after['zombie'])
            self.assertTrue(identity.same_birth(before, after))
        finally:
            child.wait(timeout=5)

    def test_missing_kernel_record_not_replaced_with_ps_start(self):
        row = dict(pid=123, group=100)
        with patch.object(identity, 'kernel_identity', side_effect=ValueError('unavailable')):
            with self.assertRaises(ValueError): identity.attach(row)


class LifecyclePolicy(unittest.TestCase):
    compiler = Path('/Applications/Unity.app/Contents/DotNetSdkRoslyn/VBCSCompiler.dll')

    def row(self):
        return dict(pid=123, group=100, start='display time', state='S', command='dotnet exec '+str(self.compiler),
                    kernel=dict(source='DarwinProcBsdInfo', birth=[10000, 1234], pid=123, group=100,
                                uid=42, parent=1, status=2, exiting=False, zombie=False))

    def retirement(self, scans):
        sent = []
        with patch.object(session, 'reap'):
            result = session.retire(100, self.compiler, scan=lambda _: next(scans),
                send=lambda pid, sig: sent.append((pid, sig)), clock=lambda: 0, sleep=lambda _: None)
        return result, sent

    def test_kernel_exit_survives_display_start_and_argv_loss(self):
        row = self.row()
        dying = dict(row, command='(dotnet)', start='Thu Jan 1 00:00:00 1970', state='?E',
                     kernel=dict(row['kernel'], exiting=True))
        zombie = dict(dying, command='<defunct>', state='Z', kernel=dict(dying['kernel'], zombie=True))
        result, sent = self.retirement(iter([[row], [row], [row], [dying], [zombie], []]))
        self.assertTrue(result['clean']); self.assertEqual(sent, [(123, signal.SIGTERM)])
        self.assertEqual(result['observations'][-3]['members'], [dying])

    def test_changed_live_command_fails_with_exact_observation(self):
        row = self.row(); changed = dict(row, command='different live program')
        result, _ = self.retirement(iter([[row], [row], [row], [changed]]))
        self.assertFalse(result['clean']); self.assertEqual(result['after'], [changed])
        self.assertEqual(result['identityMismatch']['observed'], changed)
        self.assertEqual(result['identityMismatch']['expected'], row)

    def test_same_pid_new_kernel_birth_rejected_even_when_exiting(self):
        row = self.row(); changed = dict(row, kernel=dict(row['kernel'], birth=[10000, 1235], exiting=True))
        result, sent = self.retirement(iter([[row], [changed]]))
        self.assertFalse(result['clean']); self.assertEqual(sent, [])
        self.assertEqual(result['after'], [changed])

    def test_new_child_after_signal_preserved_and_not_signalled(self):
        row = self.row(); extra = dict(row, pid=124, command='unknown')
        result, sent = self.retirement(iter([[row], [row], [row], [row, extra]]))
        self.assertFalse(result['clean']); self.assertEqual(result['after'], [row, extra])
        self.assertEqual(sent, [(123, signal.SIGTERM)])

    def test_initial_unknown_exiting_process_not_authorized(self):
        row = self.row(); row['command'] = '<defunct>'; row['kernel']['exiting'] = True
        result, sent = self.retirement(iter([[row]]))
        self.assertFalse(result['clean']); self.assertEqual(sent, [])

    def test_known_exiting_process_is_waited_for_not_signalled(self):
        row = self.row(); dying = dict(row, kernel=dict(row['kernel'], exiting=True))
        result, sent = self.retirement(iter([[row], [dying], [dying], []]))
        self.assertTrue(result['clean']); self.assertEqual(sent, [])

    def test_native_attachment_failure_preserves_raw_census(self):
        raw = [self.row()]
        with patch.object(session, 'reap'):
            result = session.retire(100, self.compiler, scan=lambda _: (_ for _ in ()).throw(session.CensusError('native read failed', raw)))
        self.assertFalse(result['clean']); self.assertEqual(result['after'], raw)
        self.assertIn('censusError', result['observations'][-1])


if __name__ == '__main__': unittest.main()
