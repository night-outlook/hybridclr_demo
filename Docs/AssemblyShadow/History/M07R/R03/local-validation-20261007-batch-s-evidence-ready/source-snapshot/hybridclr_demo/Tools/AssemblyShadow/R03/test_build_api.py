"""Build-helper compile-contract tests; synthetic inputs are not Unity evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from batch_contract import ContractError
from build_api import assembly_plan, compile_profile, csc_arguments, verify_negative, UNITY_PREFIX


def receipt(code=1):
    return dict(schemaVersion=2, lifetimePolicy='R03OwnedCommandV1', exitCode=code, timeout=False,
                remainingProcessGroup=False, postCleanupGroupExists=False, interrupted=False,
                startError=None, cleanupErrors=[])


def profile():
    names = ['Managed/UnityEngine/UnityEditor.CoreModule.dll', 'Managed/UnityEngine/UnityEngine.CoreModule.dll',
             'PlaybackEngines/MacStandaloneSupport/UnityEditor.OSXStandalone.Extensions.dll',
             'NetStandard/ref/2.1.0/netstandard.dll', 'NetStandard/compat/2.1.0/shims/netfx/mscorlib.dll']
    return '-define:UNITY_EDITOR_OSX\n-define:UNITY_2022_3\n' + ''.join('-r:"' + UNITY_PREFIX + n + '"\n' for n in names)


class BuildApiContracts(unittest.TestCase):
    def test_actual_receipt_matches_signed_api(self):
        source = (Path(__file__).parent / 'PlayerProject/R03Build.cs').read_text()
        self.assertIn('public int errors;', source)
        self.assertIn('public int warnings;', source)
        self.assertNotIn('public uint errors;', source)
        self.assertIn('receipt.errors = report.summary.totalErrors;', source)
        self.assertIn('report.summary.totalErrors != 0', source)

    def test_complete_platform_profile(self):
        defines, refs = compile_profile(profile(), Path('/extracted/Contents'))
        self.assertIn('UNITY_EDITOR_OSX', defines)
        self.assertEqual(len(refs), 5)
        self.assertTrue(all(p.is_relative_to('/extracted/Contents') for p in refs))

    def test_mixed_platform_rejected(self):
        with self.assertRaises(ContractError):
            compile_profile(profile() + '-define:UNITY_EDITOR_WIN\n', Path('/Contents'))

    def test_missing_editor_reference_rejected(self):
        with self.assertRaises(ContractError):
            compile_profile(profile().replace('UnityEditor.CoreModule.dll', 'Other.dll'), Path('/Contents'))

    def test_sources_are_not_stubbed_and_no_shared_compiler(self):
        argv = csc_arguments('/runtime/dotnet', '/compiler/csc.dll', ['UNITY_EDITOR_OSX'],
                             [Path('/real/UnityEditor.CoreModule.dll')], [Path('/whole/R03Build.cs')], '/output.dll')
        self.assertIn('/whole/R03Build.cs', argv)
        self.assertIn('/reference:/real/UnityEditor.CoreModule.dll', argv)
        self.assertNotIn('/shared', argv)

    def test_asmdef_source_ownership_and_dependency_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, path, refs in [('HybridCLR.Runtime', 'Runtime', []), ('CodeGen', 'Editor/CodeGen', []),
                                      ('HybridCLR.Editor', 'Editor', ['HybridCLR.Runtime', 'CodeGen'])]:
                folder = root / path; folder.mkdir(parents=True, exist_ok=True)
                (folder / (name + '.asmdef')).write_text(json.dumps({'name': name, 'references': refs}))
                (folder / (name + '.cs')).write_text('// actual source inventory')
            plan = assembly_plan(root)
            self.assertEqual([p[0] for p in plan], ['HybridCLR.Runtime', 'CodeGen', 'HybridCLR.Editor'])
            self.assertEqual(len(plan[-1][3]), 1)

    def test_original_two_count_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            text = "error CS0266: Cannot convert 'int' to 'uint'\nerror CS0266: Cannot convert 'int' to 'uint'\n"
            verify_negative(receipt(), text, Path(d) / 'missing.dll')

    def test_unrelated_errors_never_pass_negative_control(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ContractError):
                verify_negative(receipt(), "error CS0266: 'int' to 'uint'\nerror CS0006: missing API", Path(d) / 'missing.dll')

    def test_negative_control_must_not_emit_assembly(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.dll'; path.write_bytes(b'not accepted')
            with self.assertRaises(ContractError):
                verify_negative(receipt(), "error CS0266: 'int' to 'uint'\nerror CS0266: 'int' to 'uint'", path)

    def test_survivor_cannot_satisfy_negative_control(self):
        with tempfile.TemporaryDirectory() as d:
            row = receipt(); row['remainingProcessGroup'] = True
            with self.assertRaises(ContractError):
                verify_negative(row, "error CS0266: 'int' to 'uint'\nerror CS0266: 'int' to 'uint'", Path(d) / 'missing.dll')


if __name__ == '__main__':
    unittest.main()
