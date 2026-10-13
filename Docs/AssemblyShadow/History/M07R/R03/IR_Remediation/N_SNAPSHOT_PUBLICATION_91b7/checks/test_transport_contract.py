"""Candidate preservation and native first-failure decoding. No Unity execution."""
from pathlib import Path
import hashlib
import re
import unittest
from classify_snapshot_failure import classify

H = Path(__file__).resolve().parent
BASE = H / 'source/hybridclr_demo/Tools/AssemblyShadow'
CAND = H / 'candidate/hybridclr_demo/Tools/AssemblyShadow'

class NativeFailureClassification(unittest.TestCase):
    def setUp(self):
        self.line = b'[R03SnapshotFailure] version=1 pid=321 operation=text field=15 reason=9 previousState=1 length=262145 limit=262144 errno=0 intMask=01ffffff textMask=00007fff\n'

    def read(self, data=None, pid=321):
        data = self.line if data is None else data
        return classify(data, pid, hashlib.sha256(data).hexdigest())

    def test_exact_prefix_not_claimed_full_length(self):
        r = self.read()
        self.assertEqual(r['firstFailure']['slot'], 15)
        self.assertFalse(r['firstFailure']['fullLengthKnown'])
        self.assertFalse(r['runtimeAcceptance'])

    def test_missing_failure_is_not_acceptance(self):
        r = self.read(b'[R03SnapshotSealed] version=1 pid=321 intMask=01ffffff textMask=0000ffff\n')
        self.assertIsNone(r['firstFailure'])
        self.assertEqual(r['semanticVerification'], 'SeparateOriginalRawVerifierRequired')
        self.assertFalse(r['runtimeAcceptance'])

    def test_pid_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'PID mismatch'): self.read(pid=322)

    def test_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            classify(self.line, 321, '0' * 64)

    def test_multiple_first_failures_rejected(self):
        with self.assertRaisesRegex(ValueError, 'More than one'): self.read(self.line * 2)

    def test_malformed_line_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Malformed'): self.read(self.line.replace(b'field=15 ', b''))

    def test_changed_limit_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Changed scan bound'):
            self.read(self.line.replace(b'limit=262144', b'limit=524288'))

    def test_invalid_negative_slot_is_preserved_as_diagnostic(self):
        data = self.line.replace(b'field=15 reason=9', b'field=-2 reason=6').replace(b'length=262145', b'length=0')
        result = self.read(data)
        self.assertEqual(result['firstFailure']['slot'], -2)
        self.assertEqual(result['firstFailure']['reason'], 'InvalidSlotIndex')
        self.assertFalse(result['runtimeAcceptance'])

    def test_unknown_reason_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown'): self.read(self.line.replace(b'reason=9 ', b'reason=99 '))

    def test_out_of_schema_mask_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Out-of-schema'):
            self.read(self.line.replace(b'intMask=01ffffff', b'intMask=ffffffff'))

    def test_wrong_operation_reason_pair_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Operation/reason pair'):
            self.read(self.line.replace(b'operation=text', b'operation=close'))

    def test_over_limit_must_record_exact_bounded_prefix(self):
        with self.assertRaisesRegex(ValueError, 'Inconsistent bounded scan length'):
            self.read(self.line.replace(b'length=262145', b'length=262144'))

    def test_unmeasured_text_length_is_not_claimed_known(self):
        data = self.line.replace(b'reason=9', b'reason=7').replace(b'length=262145', b'length=0')
        r = self.read(data)['firstFailure']
        self.assertFalse(r['fullLengthKnown'])
        self.assertFalse(r['lengthMeasured'])

class CandidatePreservation(unittest.TestCase):
    def test_original_sources_match_pinned_git_blobs(self):
        for rel, expected in [
          ('R03/PlayerProject/AssemblyShadowR03Probe.cpp','2de5e4ef90eaa79daed65c3df0a8faa58ebd5837'),
          ('R03IR/PlayerProject/R03TerminalPlayer.cs','a7420cbc71c13f2951c1b5330b61307d2c4da5e5')]:
            b = (BASE/rel).read_bytes()
            self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(), expected)

    def test_all_non_emitter_csharp_is_unchanged(self):
        rel='R03IR/PlayerProject/R03TerminalPlayer.cs'
        old=(BASE/rel).read_text(); new=(CAND/rel).read_text()
        original='            return ok && R03_IR_ReportSeal() == 1;'
        candidate='''            // Call Seal even after a rejected store, so native failure state is
            // observed. It must never seal a failed/missing/duplicate field set.
            int seal = R03_IR_ReportSeal();
            return ok && seal == 1;'''
        self.assertEqual(new.replace(candidate, original), old)

    def test_native_non_writer_methods_are_unchanged(self):
        rel='R03/PlayerProject/AssemblyShadowR03Probe.cpp'
        old=(BASE/rel).read_text(); new=(CAND/rel).read_text()
        begin='namespace r03_ir_snapshot {'; end='extern "C" IL2CPP_EXPORT void R03_IR_Exit'
        self.assertEqual(old[:old.index(begin)], new[:new.index(begin)].replace('#include <cerrno>\n',''))
        self.assertEqual(old[old.index(end):], new[new.index(end):])

    def test_original_slot_schema_and_limit_unchanged(self):
        rel='R03/PlayerProject/AssemblyShadowR03Probe.cpp'
        old=(BASE/rel).read_text(); new=(CAND/rel).read_text()
        for name in ('TextLimit','IntNames','TextNames','IntCount','FirstBool','TextCount'):
            pat=r'^constexpr [^\n]*\b'+name+r'[^\n]*$'
            self.assertEqual(re.findall(pat,old,re.M), re.findall(pat,new,re.M))

    def test_only_two_existing_repository_files_changed(self):
        allfiles={str(p.relative_to(H/'candidate')) for p in (H/'candidate').rglob('*') if p.is_file()}
        self.assertEqual(allfiles,{
         'hybridclr_demo/Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp',
         'hybridclr_demo/Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'})

if __name__=='__main__': unittest.main()
