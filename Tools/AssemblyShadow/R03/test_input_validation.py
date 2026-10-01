"""Negative controls for compiler/lifetime acceptance; not Unity execution."""
from pathlib import Path
import tempfile
import types
import unittest
from batch_contract import ContractError
from input_validation import compiler_args, verify_negative, unity_toolchain
from unity_command import clean_outer, unity_command, supervised


def row(code=0):
    return dict(schemaVersion=2, lifetimePolicy='R03OwnedCommandV1', exitCode=code, timeout=False,
                remainingProcessGroup=False, postCleanupGroupExists=False, interrupted=False,
                startError=None, cleanupErrors=[])


class InputContracts(unittest.TestCase):
    def test_clean_success(self): clean_outer(row(), 0)
    def test_survivor_never_passes(self):
        value=row();value['remainingProcessGroup']=True
        with self.assertRaises(ContractError): clean_outer(value,0)
    def test_cleanup_does_not_replace_original_observation(self):
        value=row();value['postCleanupGroupExists']=True
        with self.assertRaises(ContractError): clean_outer(value,0)
    def test_timeout_rejected(self):
        value=row();value['timeout']=True
        with self.assertRaises(ContractError): clean_outer(value,0)
    def test_boolean_exit_rejected(self):
        value=row();value['exitCode']=False
        with self.assertRaises(ContractError): clean_outer(value,0)
    def test_expected_compile_failure_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            verify_negative(row(1),'error CS0009: Invalid public key.',Path(d)/'no.dll')
            with self.assertRaises(ContractError): verify_negative(row(0),'error CS0009: Invalid public key.',Path(d)/'no.dll')
    def test_arbitrary_diagnostic_is_not_expected_failure(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ContractError): verify_negative(row(1),'CS0103: missing name',Path(d)/'no.dll')
    def test_wrong_metadata_error_is_not_key_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ContractError): verify_negative(row(1),'CS0009: invalid header',Path(d)/'no.dll')
    def test_negative_control_cannot_emit_output(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'bad.dll';target.write_bytes(b'not accepted')
            with self.assertRaises(ContractError): verify_negative(row(1),'CS0009: Invalid public key',target)
    def test_compiler_argv_preserves_spaces_and_aliases(self):
        cmd=compiler_args('/path with spaces/dotnet','/compiler/csc.dll',['/ref/mscorlib.dll'],'/source.cs','/consumer.dll','/a/A.dll',['/b/B.dll'])
        self.assertEqual(cmd[0],'/path with spaces/dotnet')
        self.assertIn('/reference:Subject=/a/A.dll',cmd)
        self.assertIn('/reference:Dependency0=/b/B.dll',cmd)
        self.assertNotIn('/shared',cmd)
    def test_unity_reference_profile_matches_recorded_toolchain(self):
        runtime,compiler,refs=unity_toolchain('/editor/Unity.app/Contents/MacOS/Unity')
        self.assertEqual(str(runtime),'/editor/Unity.app/Contents/NetCoreRuntime/dotnet')
        self.assertTrue(str(compiler).endswith('DotNetSdkRoslyn/csc.dll'))
        self.assertTrue(str(refs[1]).endswith('compat/2.1.0/shims/netfx/mscorlib.dll'))
    def test_unowned_project_rejected_before_any_launch(self):
        b=types.SimpleNamespace(unity='/Unity',root=Path('/owned'))
        with self.assertRaises(ContractError): unity_command(b,['/Unity','-projectPath','/unrelated'],1)
    def test_both_engine_entrypoints_use_supervision(self):
        source=(Path(__file__).parent/'run_local.py').read_text()
        self.assertEqual(source.count('unity_command(self, [self.unity,'),2)
        self.assertIn('len(self.cells) == 36',source)
        self.assertIn("len(self.matrix['cases']) == 19",source)
        self.assertIn("self.cell('player-fixtures', lambda: validate_inputs(self)",source)
    def test_expectation_boolean_is_not_exit_code(self):
        with self.assertRaises(ContractError): supervised(None,None,[],1,expected_exit=True)


if __name__ == '__main__': unittest.main()
