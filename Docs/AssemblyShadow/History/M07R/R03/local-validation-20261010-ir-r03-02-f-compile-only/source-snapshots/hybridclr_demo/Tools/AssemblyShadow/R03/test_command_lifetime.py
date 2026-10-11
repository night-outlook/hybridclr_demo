"""Real POSIX process tests; synthetic failure fixtures are not Player evidence."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import command_lifetime as lifetime


class PolicyTests(unittest.TestCase):
    def test_build_policy_is_explicit_and_last(self):
        args = lifetime.build_arguments('project with spaces/p.csproj', '/out/bin', '/out/obj', '/package')
        self.assertEqual(args[:3], ['dotnet', 'build', 'project with spaces/p.csproj'])
        self.assertEqual(args[-3:], list(lifetime.BUILD_FLAGS))
        for flag in lifetime.BUILD_FLAGS:
            self.assertEqual(args.count(flag), 1)
        self.assertIn('-p:BaseIntermediateOutputPath=/out/obj/', args)

    def test_environment_overrides_are_child_scoped(self):
        with patch.dict(os.environ, {k: 'hostile-inherited-value' for k in lifetime.BUILD_ENV}):
            before = dict(os.environ)
            child = lifetime.child_environment()
            self.assertEqual(dict(os.environ), before)
            for key, value in lifetime.BUILD_ENV.items():
                self.assertEqual(child[key], value)

    def test_diagnostic_members_are_filtered_and_bounded(self):
        lines = ['1 1 999 S unrelated-secret-args']
        lines += [f'{n} 1 123 S /compiler' for n in range(1000, 1070)]
        value = lifetime.parse_members('\n'.join(lines), 123)
        self.assertEqual(value['observedCount'], 70)
        self.assertEqual(len(value['members']), 64)
        self.assertTrue(value['truncated'])
        self.assertTrue(all(x['pgid'] == 123 for x in value['members']))
        self.assertNotIn('unrelated', json.dumps(value))

    def test_diagnostic_parser_handles_spaces_and_bad_rows(self):
        value = lifetime.parse_members('bad row\n42 1 123 S /path with spaces/compiler\n42 x y invalid', 123)
        self.assertEqual(value['observedCount'], 1)
        self.assertEqual(value['members'][0]['executable'], '/path with spaces/compiler')


@unittest.skipUnless(os.name == 'posix', 'POSIX process-group contract')
class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'command'

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, code, timeout=10):
        return lifetime.run_owned_command([sys.executable, '-c', code], self.root, timeout)

    def receipt(self):
        return json.loads((self.root / 'command.json').read_text())

    def test_clean_success_and_hashes(self):
        value = self.invoke("print('completed')")
        self.assertEqual(value['exitCode'], 0)
        self.assertFalse(value['remainingProcessGroup'])
        self.assertFalse(value['postCleanupGroupExists'])
        self.assertEqual(value['cleanupErrors'], [])
        self.assertIsNone(value['processGroupBeforeCleanup'])
        self.assertEqual(value['stdoutSha256'], lifetime._sha(self.root / 'stdout.log'))
        self.assertEqual(value['pid'], value['pgid'])
        self.assertNotEqual(value['pgid'], os.getpgrp())

    def test_nonzero_exit_is_not_success(self):
        with self.assertRaises(RuntimeError):
            self.invoke('raise SystemExit(7)')
        self.assertEqual(self.receipt()['exitCode'], 7)
        self.assertFalse(self.receipt()['remainingProcessGroup'])

    def test_launch_error_gets_receipt(self):
        with self.assertRaises(RuntimeError):
            lifetime.run_owned_command(['/no-such-r03-executable'], self.root)
        self.assertIn('FileNotFoundError', self.receipt()['startError'])
        self.assertIsNone(self.receipt()['pid'])

    def test_timeout_remains_failure_after_owned_cleanup(self):
        with self.assertRaises(RuntimeError):
            self.invoke('import time; time.sleep(60)', timeout=0.1)
        value = self.receipt()
        self.assertTrue(value['timeout'])
        self.assertTrue(value['remainingProcessGroup'])
        self.assertNotEqual(value['exitCode'], 0)
        self.assertTrue((self.root / 'process-group-before-cleanup.json').is_file())

    def test_zero_exit_with_survivor_rejected_unrelated_process_untouched(self):
        sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
        try:
            with self.assertRaises(RuntimeError):
                self.invoke("import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); print(p.pid,flush=True)")
            value = self.receipt()
            child = int((self.root / 'stdout.log').read_text().strip())
            self.assertEqual(value['exitCode'], 0)
            self.assertTrue(value['remainingProcessGroup'])
            snapshot = value['processGroupBeforeCleanup']
            self.assertEqual(snapshot['status'], 'Captured')
            self.assertIn(child, [x['pid'] for x in snapshot['members']])
            self.assertNotIn(sentinel.pid, [x['pid'] for x in snapshot['members']])
            self.assertIsNone(sentinel.poll())
        finally:
            sentinel.kill()
            sentinel.wait(timeout=10)

    def test_diagnostic_failure_does_not_skip_cleanup(self):
        with patch.object(lifetime.subprocess, 'run', side_effect=OSError('ps unavailable')):
            with self.assertRaises(RuntimeError):
                self.invoke('import time; time.sleep(60)', timeout=0.1)
        value = self.receipt()
        self.assertTrue(value['remainingProcessGroup'])
        self.assertEqual(value['processGroupBeforeCleanup']['status'], 'Unavailable')
        self.assertEqual(value['exitCode'], -signal.SIGKILL)

    def test_survivor_disappearing_during_diagnostics_cannot_pass(self):
        # Simulates a group observed once, which vanishes before killpg. The
        # original observation must not be overwritten by the cleanup result.
        with patch.object(lifetime, 'group_exists', side_effect=[True, False]):
            with self.assertRaises(RuntimeError):
                self.invoke('pass')
        self.assertTrue(self.receipt()['remainingProcessGroup'])
        self.assertFalse(self.receipt()['postCleanupGroupExists'])
        self.assertEqual(self.receipt()['exitCode'], 0)

    def test_child_receives_policy_without_modifying_parent(self):
        before = dict(os.environ)
        value = self.invoke('import os,json; print(json.dumps({k:os.environ[k] for k in ' + repr(list(lifetime.BUILD_ENV)) + '}))')
        self.assertEqual(json.loads((self.root / 'stdout.log').read_text()), lifetime.BUILD_ENV)
        self.assertEqual(dict(os.environ), before)
        self.assertEqual({k: value['childEnvironmentPolicy'][k] for k in lifetime.BUILD_ENV}, lifetime.BUILD_ENV)

    def test_existing_output_is_not_overwritten(self):
        self.root.mkdir()
        marker = self.root / 'keep.txt'
        marker.write_text('original')
        with self.assertRaises(FileExistsError):
            self.invoke('pass')
        self.assertEqual(marker.read_text(), 'original')
        self.assertFalse((self.root / 'command.json').exists())

    def test_invalid_invocation_does_not_start(self):
        with self.assertRaises(ValueError):
            lifetime.run_owned_command([], self.root)
        self.assertFalse(self.root.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
