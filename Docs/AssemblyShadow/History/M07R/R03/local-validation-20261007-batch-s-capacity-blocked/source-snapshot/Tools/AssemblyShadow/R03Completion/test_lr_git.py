"""Real local Git plus deterministic transport faults; no network or Unity."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import run_completion  # Installs the production R03 import path.
import git_diagnostics as diag
from run_local import git


class GitObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / 'repo'; self.repo.mkdir()
        self.pins = {'hybridclr_demo': 'a'*40, 'branch': 'codex/test'}

    def run_fake(self, result=None, error=None, args=('ls-remote','origin','refs/heads/codex/test')):
        with diag.capture_git(self.root/'evidence',self.pins,'resource-p05-restore'), \
             patch.object(diag.subprocess,'run',return_value=result,side_effect=error) as call:
            try: value = git(self.repo,*args)
            finally: self.assertEqual(call.call_count,1)
        return value

    def row(self):
        paths=list((self.root/'evidence').glob('*.json')); self.assertEqual(len(paths),1)
        return json.loads(paths[0].read_text())

    def test_nonzero_retains_repo_argv_exit_streams_and_source(self):
        with self.assertRaises(diag.GitCommandFailure) as caught:
            self.run_fake(subprocess.CompletedProcess([],128,b'partial',b'fatal: offline'))
        row=self.row()
        self.assertEqual(row['argv'],['git','-C',str(self.repo),'ls-remote','origin','refs/heads/codex/test'])
        self.assertEqual(row['exitCode'],128); self.assertEqual(row['status'],'NonzeroExit')
        self.assertEqual(row['stderr']['excerpt'],'fatal: offline')
        self.assertEqual(row['stdout']['excerpt'],'partial')
        self.assertEqual(row['requestedSourceAuthority'],self.pins)
        self.assertEqual(row['phase'],'resource-p05-restore')
        self.assertFalse(row['sourceAuthorityValidatedByThisReceipt'])
        self.assertLessEqual(row['startUtc'],row['endUtc'])
        self.assertGreaterEqual(row['elapsedNanoseconds'],0)
        self.assertIn(caught.exception.receipt_path,str(caught.exception))

    def test_timeout_is_not_fabricated_numeric_exit(self):
        error=subprocess.TimeoutExpired('git',120,output=b'partial stdout',stderr=b'partial stderr')
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(error=error)
        row=self.row();self.assertEqual(row['status'],'Timeout');self.assertIsNone(row['exitCode'])
        self.assertEqual(row['stderr']['excerpt'],'partial stderr');self.assertEqual(row['attempt'],1)
        self.assertFalse(row['retryPerformed'])

    def test_spawn_failure_is_not_remote_rejection(self):
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(error=FileNotFoundError(2,'missing git'))
        row=self.row();self.assertEqual(row['status'],'SpawnError');self.assertEqual(row['failure']['errno'],2)
        self.assertFalse(row['stdout']['available']);self.assertIsNone(row['exitCode'])

    def test_signal_exit_kept_negative(self):
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(subprocess.CompletedProcess([],-15,b'',b''))
        self.assertEqual(self.row()['exitCode'],-15)

    def test_success_remote_is_observation_not_acceptance(self):
        text=b'wrong-tip\trefs/heads/codex/test\n'
        self.assertEqual(self.run_fake(subprocess.CompletedProcess([],0,text,b'')),text.decode().strip())
        self.assertFalse(self.row()['sourceAuthorityValidatedByThisReceipt'])

    def test_success_local_does_not_dump_arbitrary_git_blobs(self):
        self.assertEqual(self.run_fake(subprocess.CompletedProcess([],0,b'  exact  \n',b''),args=('show','HEAD:file')),'exact')
        self.assertFalse((self.root/'evidence').exists())

    def test_empty_ref_response_remains_empty(self):
        self.assertEqual(self.run_fake(subprocess.CompletedProcess([],0,b'',b'')),'')
        self.assertEqual(self.row()['stdout']['bytes'],0)

    def test_redaction_precedes_truncation(self):
        secret='S'*20000
        raw=('https://user:'+secret+'@github.com/private?token=hidden\nAuthorization: Bearer private-value\npassword=private2\ngithub_pat_private3').encode()
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(subprocess.CompletedProcess([],128,b'',raw))
        encoded=json.dumps(self.row())
        for text in (secret,'hidden','private-value','private2','private3'):self.assertNotIn(text,encoded)
        self.assertTrue(self.row()['stderr']['redacted'])
        self.assertEqual(self.row()['stderr']['bytes'],len(raw))

    def test_argv_credential_removed(self):
        with self.assertRaises(diag.GitCommandFailure):
            self.run_fake(subprocess.CompletedProcess([],128,b'',b''),args=('ls-remote','https://user:topsecret@github.com/repo'))
        self.assertNotIn('topsecret',json.dumps(self.row())); self.assertTrue(self.row()['argvRedacted'])

    def test_bounded_excerpt_and_full_length_hash(self):
        raw=b'x'*40000
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(subprocess.CompletedProcess([],1,b'',raw))
        row=self.row()['stderr'];self.assertEqual(len(row['excerpt']),diag.LIMIT)
        self.assertEqual(row['bytes'],40000);self.assertTrue(row['truncated'])
        self.assertEqual(row['sha256'],diag.hashlib.sha256(raw).hexdigest())

    def test_utf8_decode_failure_retains_byte_evidence(self):
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(subprocess.CompletedProcess([],0,b'\xff',b''))
        self.assertEqual(self.row()['status'],'DecodeError');self.assertEqual(self.row()['exitCode'],0)

    def test_preconstructor_failure_embeds_receipt_without_scope(self):
        with patch.object(diag.subprocess,'run',return_value=subprocess.CompletedProcess([],128,b'',b'offline')):
            with self.assertRaises(diag.GitCommandFailure) as caught:git(self.repo,'ls-remote','origin')
        self.assertIn('offline',str(caught.exception));self.assertIsNone(caught.exception.receipt_path)
        self.assertIsNone(caught.exception.receipt['requestedSourceAuthority'])

    def test_receipt_failure_denies_success(self):
        with patch.object(diag,'persist',side_effect=OSError(28,'no space')):
            with self.assertRaises(diag.GitCommandFailure) as caught:
                self.run_fake(subprocess.CompletedProcess([],0,b'tip',b''))
        self.assertEqual(caught.exception.receipt['status'],'EvidenceWriteError')
        self.assertIn('evidenceWriteFailure',caught.exception.receipt)

    def test_scope_restored_after_exception(self):
        with self.assertRaises(diag.GitCommandFailure):self.run_fake(subprocess.CompletedProcess([],1,b'',b''))
        self.assertIsNone(diag._SCOPE.get())

    def test_real_git_failing_remote_without_network(self):
        subprocess.run(['git','init','-q',str(self.repo)],check=True,capture_output=True)
        with diag.capture_git(self.root/'evidence',self.pins,'real-local-fault'):
            with self.assertRaises(diag.GitCommandFailure):git(self.repo,'ls-remote',str(self.root/'missing.git'))
        row=self.row(); self.assertEqual(row['exitCode'],128)
        self.assertIn('repository',row['stderr']['excerpt'].lower())




class TransportPreflightTests(unittest.TestCase):
    def test_all_four_observed_once_and_failure_retained(self):
        import transport_preflight as preflight
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp).resolve()/'proof';seen=[]
            def observe(repo,pin):
                seen.append(repo.name)
                if repo.name=='hybridclr':raise RuntimeError('Controlled remote failure')
                return {'commit':pin,'remoteHeadVerified':True}
            with patch.object(preflight,'identity',side_effect=observe):
                code=preflight.check(preflight.HERE.parents[3],output,'a'*40)
            value=json.loads((output/'verification.json').read_text())
            self.assertEqual(seen,list(preflight.REPOS));self.assertEqual(code,2)
            self.assertEqual(value['result'],'TransportBlocked')
            self.assertEqual([r['result'] for r in value['repositories']],['Passed','Failed','Passed','Passed'])
            self.assertFalse(value['retryPerformed']);self.assertFalse(value['runtimeAcceptance'])

    def test_pass_is_point_in_time_only(self):
        import transport_preflight as preflight
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp).resolve()/'proof'
            with patch.object(preflight,'identity',return_value={'remoteHeadVerified':True}):
                self.assertEqual(preflight.check(preflight.HERE.parents[3],output,'a'*40),0)
            value=json.loads((output/'verification.json').read_text())
            self.assertTrue(value['pointInTimeOnly'])
            with self.assertRaises(RuntimeError):preflight.check(preflight.HERE.parents[3],output,'a'*40)

    def test_no_sink_still_binds_expected_pins_in_error(self):
        with diag.capture_git(None,{'hybridclr_demo':'a'*40},'entry'), \
             patch.object(diag.subprocess,'run',return_value=subprocess.CompletedProcess([],128,b'',b'offline')):
            with self.assertRaises(diag.GitCommandFailure) as caught:git('/tmp/fixture-repository','ls-remote','origin')
        self.assertEqual(caught.exception.receipt['requestedSourceAuthority'],{'hybridclr_demo':'a'*40})
        self.assertIsNone(caught.exception.receipt_path)

    def test_host_batch_without_runtime_pins_retains_original_cell_behavior(self):
        import contextlib,io
        from run_local import Batch
        with tempfile.TemporaryDirectory() as temp:
            batch=object.__new__(Batch);batch.root=Path(temp).resolve();batch.outputs={};batch.cells=[];batch.failed=False
            with contextlib.redirect_stdout(io.StringIO()):batch.cell('host-fixture',lambda:{'result':'fixture'})
            self.assertEqual(batch.cells[0]['result'],'Passed')

if __name__=='__main__':unittest.main()
