import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from evidence import EvidenceError,read
import prepare_metadata as m

class Metadata(unittest.TestCase):
    def test_only_runtime_pairing_differs_in_pins(self):
        a=m.pins('a'*40);b=m.pins('a'*40,True)
        self.assertEqual(a['demo'],b['demo'])
        self.assertEqual(a['hybridclr'],b['hybridclr'])
        self.assertEqual(a['hybridclrUnity'],b['hybridclrUnity'])
        self.assertEqual(a['il2cppPlus']['revision'],m.NATIVE)
        self.assertEqual(b['il2cppPlus']['revision'],m.H1_NATIVE)
    def test_targets_bind_exact_source_control_and_gate_limits(self):
        t=m.targets('a'*40,'b'*40)
        self.assertEqual(t['control']['publishedHead'],'b'*40)
        self.assertEqual(t['candidate']['sourceCommit'],t['control']['sourceCommit'])
        self.assertFalse(t['R02Accepted']);self.assertFalse(t['mayEnterR03'])
        self.assertEqual(t['control']['repositories']['il2cpp_plus']['branch'],'codex/assembly-shadow-r01b')
    def test_invalid_anchors_rejected(self):
        for value in ('main','a'*39,'A'*40,''):
            with self.assertRaises(EvidenceError):m.targets(value,'b'*40)
            with self.assertRaises(EvidenceError):m.targets('a'*40,value)
    def test_preparation_is_not_publication(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root).resolve()/'staging';m.prepare('candidate','a'*40,out,'b'*40)
            self.assertFalse(read(out/'PREPARATION.json')['published'])
            self.assertEqual(read(out/m.authority.TARGETS)['control']['publishedHead'],'b'*40)
            self.assertIn('R02LocalBatch-v1',(out/'Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md').read_text())
    def test_control_staging_does_not_emit_candidate_handoff(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root).resolve()/'staging';m.prepare('control','a'*40,out)
            self.assertFalse((out/'Docs').exists())
    def test_existing_output_refused(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(EvidenceError):m.prepare('control','a'*40,Path(root).resolve())
    def test_prompt_requires_live_remote_verification(self):
        with patch.object(m,'read',return_value=m.targets('a'*40,'b'*40)):
            with patch.object(m.authority,'inspect',side_effect=EvidenceError('remote changed')):
                with self.assertRaises(EvidenceError):m.prompt(Path('/candidate'),'c'*40,Path('/control'),'b'*40)
    def test_prompt_rejects_wrong_control_head_before_inspection(self):
        with patch.object(m,'read',return_value=m.targets('a'*40,'b'*40)):
            with patch.object(m.authority,'inspect') as inspect:
                with self.assertRaises(EvidenceError):m.prompt(Path('/candidate'),'c'*40,Path('/control'),'d'*40)
                inspect.assert_not_called()
