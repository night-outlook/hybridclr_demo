import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import evidence
import unity_session as session


class Policy(unittest.TestCase):
    compiler = Path('/Applications/Unity 2022/Unity.app/Contents/DotNetSdkRoslyn/VBCSCompiler.dll')

    def row(self, pid=123, command=None):
        return dict(pid=pid, group=100, start='Sat Sep 26 20:00:00 2026',
                    command=command or 'dotnet exec ' + str(self.compiler))

    def test_only_exact_compiler_identity_matches(self):
        for value in ('dotnet exec '+str(self.compiler), '/path/dotnet exec "'+str(self.compiler)+'" -pipename:test'):
            self.assertTrue(session.roslyn_command(value, self.compiler))
        for value in ('python exec '+str(self.compiler), 'dotnet exec '+str(self.compiler)+'.other',
                      'dotnet exec /other/VBCSCompiler.dll', 'dotnet '+str(self.compiler),
                      'sh -c dotnet exec '+str(self.compiler)):
            self.assertFalse(session.roslyn_command(value, self.compiler))

    def cleanup(self, scans, sender=None):
        sent = []
        def send(pid, sig):
            sent.append((pid, sig))
            if sender: sender(pid, sig)
        with patch.object(session, 'reap'):
            result = session.retire(100, self.compiler, scan=lambda group: next(scans), send=send,
                                    clock=lambda: 0, sleep=lambda _: None)
        return result, sent

    def test_only_authorized_pid_is_terminated(self):
        row = self.row()
        result, sent = self.cleanup(iter([[row], [row], [row], []]))
        self.assertTrue(result['clean']);self.assertEqual(sent,[(123,signal.SIGTERM)])

    def test_empty_group_passes_without_signals(self):
        result, sent = self.cleanup(iter([[], [], []]))
        self.assertTrue(result['clean']);self.assertEqual(sent,[])

    def test_unknown_companion_fails_before_any_signal(self):
        result, sent = self.cleanup(iter([[self.row(), self.row(124,'unrelated worker')]]))
        self.assertFalse(result['clean']);self.assertEqual(sent,[])

    def test_pid_reuse_or_new_member_fails(self):
        for newer in (dict(self.row(), start='new start'), self.row(124)):
            result, sent = self.cleanup(iter([[self.row()], [newer]]))
            self.assertFalse(result['clean']);self.assertEqual(sent,[])

    def test_identity_rechecked_immediately_before_signal(self):
        result, sent = self.cleanup(iter([[self.row()], [self.row()], [dict(self.row(),command='other')]]))
        self.assertFalse(result['clean']);self.assertEqual(sent,[])

    def test_disappearing_process_is_not_signaled(self):
        result, sent = self.cleanup(iter([[self.row()], [self.row()], [], []]))
        self.assertTrue(result['clean']);self.assertEqual(sent,[])

    def test_census_failure_is_not_success(self):
        with patch.object(session,'reap'):
            result=session.retire(100,self.compiler,scan=lambda _:(_ for _ in ()).throw(OSError('ps failed')))
        self.assertFalse(result['clean'])


@unittest.skipUnless(os.name == 'posix', 'POSIX process ownership')
class Integration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.addCleanup(self.tmp.cleanup)
        contents=self.root/'Unity.app/Contents'
        self.unity=contents/'MacOS/Unity';self.unity.parent.mkdir(parents=True);self.unity.write_text('fixture')
        self.compiler=contents/'DotNetSdkRoslyn/VBCSCompiler.dll';self.compiler.parent.mkdir();self.compiler.write_text('fixture')

    def invoke(self, command):
        receipt=self.root/'completion.json'
        outer=evidence.run([sys.executable,str(Path(session.__file__)), '--unity',str(self.unity),
                            '--receipt',str(receipt),'--',*command],self.root,self.root/'outer',20)
        return outer,evidence.read(receipt)

    def test_clean_command_keeps_strict_outer_check(self):
        outer,inner=self.invoke([sys.executable,'-c','print("build finished")'])
        self.assertEqual(outer['result'],'Passed');self.assertTrue(outer['processGroupClean'])
        self.assertEqual(inner['result'],'Passed')

    def test_failed_command_cannot_be_promoted(self):
        outer,inner=self.invoke([sys.executable,'-c','import sys;sys.exit(7)'])
        self.assertEqual(outer['result'],'Failed');self.assertEqual(inner['commandExitCode'],7)
        self.assertTrue(inner['completion']['clean'])

    def test_real_owned_compiler_is_reaped_but_unrelated_session_untouched(self):
        # A real native process retains dotnet-shaped argv; no production
        # compiler executes in this host test.
        source=self.root/'fake.c';source.write_text('#include <unistd.h>\nint main(void){for(;;)pause();}\n')
        binary=self.root/'dotnet'
        subprocess.run(['cc',str(source),'-o',str(binary)],check=True,capture_output=True)
        other=subprocess.Popen([str(binary),'exec',str(self.compiler)],start_new_session=True)
        try:
            code='import subprocess,sys;subprocess.Popen(sys.argv[1:])'
            outer,inner=self.invoke([sys.executable,'-c',code,str(binary),'exec',str(self.compiler)])
            self.assertEqual(outer['result'],'Passed',inner)
            self.assertTrue(outer['processGroupClean']);self.assertIsNone(other.poll())
            self.assertEqual(len(inner['completion']['actions']),1)
        finally:
            other.terminate();other.wait(timeout=5)

    def test_arbitrary_child_still_fails(self):
        code='import subprocess,sys;subprocess.Popen([sys.executable,"-c","import time;time.sleep(10)"])'
        outer,inner=self.invoke([sys.executable,'-c',code])
        self.assertEqual(outer['result'],'Failed');self.assertFalse(inner['completion']['clean'])


if __name__=='__main__': unittest.main()
