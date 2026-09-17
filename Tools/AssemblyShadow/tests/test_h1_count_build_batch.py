"""Bounded build planning/recovery tests; never launch Unity here."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import h1_count_build_batch as b
import shadow_tools as s

SCENE = b"  expectedBaselineBuildId: H1Count-On-Debug\n  expectedRuntimeAbiHash: " + b"a"*64 + b"\n  expectedFeatureEnabled: 1\n  expectedCppConfiguration: Debug\nother: unchanged\n"

class BatchTests(unittest.TestCase):
    def test_smoke_is_only_candidate_on_debug(self):
        self.assertEqual([('candidate','on','Debug')], b.modes('smoke'))
    def test_all_six_modes_are_unique_and_repro_is_on_only(self):
        rows=b.modes('all');self.assertEqual(6,len(set(rows)))
        self.assertEqual([('reproduction','on','Debug'),('reproduction','on','Release')],rows[-2:])
    def test_inspect_uses_verified_handoff_role_not_a_hardcoded_branch(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();(root/'ProjectSettings').mkdir()
            (root/b.SETTINGS).write_text('  additionalIl2CppArgs: -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\n')
            (root/s.PINS).write_text('{}')
            proof={'branch':'codex/assembly-shadow-h1-repro-bee-domains','codeCommit':'a'*40}
            def git(path,*args):
                return (b'https://github.com/night-outlook/hybridclr_demo.git' if args[0]=='remote' else b'b'*40)
            with patch.object(b.handoff,'verify',return_value=proof) as preflight,patch.object(s,'git',side_effect=git),patch.object(s,'verify',return_value={'demoSourceVerified':True}):
                row=b.inspect_project(root,'reproduction')
            preflight.assert_called_once_with(root,'reproduction');self.assertEqual(proof,row['handoff'])
    def test_unverified_handoff_cannot_reach_installation_check(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(b.handoff,'verify',side_effect=RuntimeError('wrong anchor')),patch.object(s,'verify') as installed:
                with self.assertRaisesRegex(RuntimeError,'wrong anchor'):b.inspect_project(Path(temp).resolve(),'reproduction')
            installed.assert_not_called()
    def test_unknown_role_never_defaults_to_reproduction(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(b.handoff,'verify') as check:
            with self.assertRaisesRegex(RuntimeError,'Unknown build source role'):b.inspect_project(Path(temp).resolve(),'other')
            check.assert_not_called()
    def test_unchanged_bytes_allowed(self):
        self.assertTrue(b.restore_allowed(b.SETTINGS,b'unchanged',b'unchanged'))
    def test_only_known_empty_standalone_serialization_allowed(self):
        old=b'prefix\n  scriptingDefineSymbols: {}\nsuffix\n'
        new=b'prefix\n  scriptingDefineSymbols:\n    Standalone: \nsuffix\n'
        self.assertTrue(b.restore_allowed(b.SETTINGS,old,new))
    def test_other_settings_change_rejected(self):
        self.assertFalse(b.restore_allowed(b.SETTINGS,b'a',b'b'))
    def test_scene_four_mode_values_allowed(self):
        after=SCENE.replace(b'On-Debug',b'Off-Release').replace(b' 1\n',b' 0\n').replace(b': Debug',b': Release')
        self.assertTrue(b.restore_allowed(b.SCENE,SCENE,after))
    def test_unrelated_scene_change_rejected(self):
        self.assertFalse(b.restore_allowed(b.SCENE,SCENE,SCENE.replace(b'unchanged',b'edited')))
    def test_scene_duplicate_field_rejected(self):
        with self.assertRaises(RuntimeError):
            b.restore_allowed(b.SCENE,SCENE,SCENE+b'  expectedFeatureEnabled: 1\n')
    def test_scene_invalid_abi_rejected(self):
        with self.assertRaises(RuntimeError):
            b.restore_allowed(b.SCENE,SCENE,SCENE.replace(b'a'*64,b'not-a-hash'))
    def test_meta_changes_never_restored(self):
        self.assertFalse(b.restore_allowed(b.SCENE+'.meta',b'old',b'new'))
    def test_dry_run_has_no_process_or_output(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp).resolve();out=p/'not-created';buffer=io.StringIO()
            argv=['tool','--candidate',str(p),'--unity','unused','--pwsh','unused','--output',str(out)]
            with patch.object(sys,'argv',argv),patch.object(b.batch,'run_command') as call,redirect_stdout(buffer):
                self.assertEqual(0,b.main())
            call.assert_not_called();self.assertFalse(out.exists())
            self.assertFalse(json.loads(buffer.getvalue())['humanGatePassed'])
    def test_reuse_not_allowed_for_smoke(self):
        with tempfile.TemporaryDirectory() as temp:
            argv=['tool','--candidate',temp,'--unity','unused','--pwsh','unused','--output',temp+'/out','--reuse-smoke',temp+'/old']
            with patch.object(sys,'argv',argv),self.assertRaises(RuntimeError):b.main()
    def test_real_command_records_exit_and_output(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp).resolve();r=b.command([sys.executable,'-c','print("fixture")'],p,p/'run.log',10)
            self.assertEqual(0,r['exitCode']);self.assertIn('fixture',(p/'run.log').read_text())
            self.assertTrue((p/'run.log.execution.json').is_file())
    def test_failed_command_records_failure_before_raising(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp).resolve()
            with self.assertRaises(RuntimeError):b.command([sys.executable,'-c','raise SystemExit(3)'],p,p/'run.log',10)
            self.assertEqual(3,json.loads((p/'run.log.execution.json').read_text())['exitCode'])
    def test_minimum_free_storage_is_checked_before_build(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp).resolve()
            with patch.object(b.shutil,'disk_usage',return_value=SimpleNamespace(free=0)),self.assertRaisesRegex(RuntimeError,'10 GiB'):
                b.run_one(p,'unused','unused','on','Debug',{},p/'out')

class HandoffMetadataTests(unittest.TestCase):
    def test_only_fixed_handoff_files_are_metadata(self):
        for name in ('WEB_TO_LOCAL.md','LOCAL_VALIDATION.md','RETURN_TO_WEB.md','source-targets.json'):
            self.assertTrue(s.metadata_only('Docs/AssemblyShadow/Handoff/'+name))
    def test_handoff_directory_does_not_hide_code(self):
        for name in ('runner.py','payload.cs','WEB_TO_LOCAL.md.cs','sub/WEB_TO_LOCAL.md','../WEB_TO_LOCAL.md','preflight.json'):
            self.assertFalse(s.metadata_only('Docs/AssemblyShadow/Handoff/'+name))
    def test_unrelated_documents_and_case_variations_not_exempt(self):
        self.assertFalse(s.metadata_only('Documents/Other.md'))
        self.assertFalse(s.metadata_only('docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md'))
    def test_previous_pin_and_project_docs_policy_preserved(self):
        self.assertTrue(s.metadata_only(s.PINS));self.assertTrue(s.metadata_only('Docs/AssemblyShadow/existing.json'))

if __name__=='__main__':unittest.main()
