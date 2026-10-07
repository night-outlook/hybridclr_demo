import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import run_local as local

class M00BatchBoundary(unittest.TestCase):
    def test_materialization_precedes_m07_without_compiler_hash_substitution(self):
        import inspect
        source=inspect.getsource(local.Batch.build)
        self.assertLess(source.index('ordinary_input.prepare'),source.index('Invoke-M07Build.ps1'))
        self.assertNotIn('R02OrdinaryInput.Prepare',source)
        self.assertIn('ordinary_input.verify(project, prepared)',source)

    def test_read_only_forensics_is_independent_of_fresh_builds(self):
        source=Path(local.__file__).read_text()
        self.assertIn('"m00-batch-e-forensics", ["common-sources"]',source)
        # Original per-role build dependencies remain unchanged.
        self.assertIn('role + "-build", ["common-sources", "primary"]',source)

    def test_forensic_failure_retains_already_bound_inputs(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve()
            batch=object.__new__(local.Batch);batch.out=root;batch.roots={'candidate':root};batch.retained=set()
            observed=root/'old.dll';observed.write_bytes(b'labelled fixture')
            def failed(project, output):
                output.mkdir()
                local.write(output/'analysis.json',{'result':'Failed','retainedInputs':[local.binding(observed)]})
                raise RuntimeError('original forensic rejection')
            with patch.object(local.m00_forensics,'analyze_batch_e',side_effect=failed):
                with self.assertRaisesRegex(RuntimeError,'original forensic rejection'):batch.m00_diagnostics()
            self.assertIn(observed,batch.retained)
