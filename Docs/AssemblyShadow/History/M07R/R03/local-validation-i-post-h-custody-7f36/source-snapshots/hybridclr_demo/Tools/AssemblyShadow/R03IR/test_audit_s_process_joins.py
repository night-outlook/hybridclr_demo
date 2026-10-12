"""Synthetic fail-closed tests for the original S process/source receipt join."""
from pathlib import Path
import unittest

from audit_s_process_joins import native_int, original_relpath, bound_file, check_command
from audit_s_provenance import require


class ProcessJoinTests(unittest.TestCase):
    def test_only_true_positive_integer_process_ids(self):
        for value in (True, False, 0, -1, '1', 1.0, None):
            with self.subTest(value=repr(value)):
                self.assertFalse(native_int(value))
        self.assertTrue(native_int(1))
        self.assertTrue(native_int(65535))

    def test_original_path_requires_exact_S_root(self):
        path = original_relpath(
            '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/commands/0001/command.json')
        self.assertEqual(path, 'commands/0001/command.json')
        for value in ('/other/commands/0001/command.json',
                      '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/../wrong',
                      '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery//absolute',
                      None, True):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    original_relpath(value)

    def test_archive_digest_binding_is_exact(self):
        members = {'x/raw.json': {'sha256': 'a'*64, 'size': 4}}
        bound_file(members, 'x/raw.json', 'a'*64, 'Raw')
        for path, digest in [('x/raw.json', 'b'*64), ('missing.json', 'a'*64),
                             ('x/raw.json', None), ('x/raw.json', True)]:
            with self.subTest(path=path, digest=digest):
                with self.assertRaises(ValueError):
                    bound_file(members, path, digest, 'Raw')

    def test_original_owned_command_pid_and_exit(self):
        command = 'commands/0001/command.json'
        command_sha = 'c'*64
        console = 'early/Control-P01/console-combined.log'
        console_sha = 'd'*64
        members = {command:{'sha256':command_sha}, console:{'sha256':console_sha}}
        receipt = {'result':'Passed','R03Accepted':False,'launchPid':4321,'originalExit':0,
            'commandReceipt':'/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/'+command,
            'commandSha256':command_sha,
            'console':'/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/'+console,
            'consoleSha256':console_sha}
        cmd = {'pid':4321,'pgid':4321,'exitCode':0,'interrupted':False,
               'remainingProcessGroup':False,'lifetimePolicy':'R03OwnedCommandV1'}
        verified=check_command(lambda _:cmd, members, receipt, 'early/Control-P01', 'early-Control-P01')
        self.assertEqual(verified['pid'],4321)
        self.assertEqual(verified['exitCode'],0)
        for key, value in [('launchPid',4322),('launchPid',True),('originalExit',1),
                           ('result','Failed'),('commandSha256','e'*64),
                           ('R03Accepted',True)]:
            with self.subTest(key=key,value=repr(value)):
                changed=dict(receipt,key_dummy=1)
                changed[key]=value
                with self.assertRaises(ValueError):
                    check_command(lambda _:cmd, members, changed, 'early/Control-P01', 'early-Control-P01')

    def test_cannot_substitute_different_process_group(self):
        command='commands/0001/command.json'
        members={command:{'sha256':'a'*64}}
        receipt={'result':'Passed','launchPid':17,'commandReceipt':
            '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/'+command,
            'commandSha256':'a'*64}
        for bad in ({'pid':17,'pgid':18,'exitCode':0,'interrupted':False,
                      'remainingProcessGroup':False,'lifetimePolicy':'R03OwnedCommandV1'},
                    {'pid':17,'pgid':17,'exitCode':0,'interrupted':True,
                      'remainingProcessGroup':False,'lifetimePolicy':'R03OwnedCommandV1'}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    check_command(lambda _:bad, members, receipt, 'x', 'x')


if __name__ == '__main__':
    unittest.main()
