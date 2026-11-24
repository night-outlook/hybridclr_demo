#!/usr/bin/env python3
"""Synthetic fixed native receipt regression tests, not a Player acceptance."""
import importlib.util
from pathlib import Path
import struct
import unittest

path = Path(__file__).with_name("d5_c10_native_receipt.py")
spec = importlib.util.spec_from_file_location("d5_c10_native_receipt", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def material(events=None, *, first=2, change=None, first_reason="Keep target guard refused"):
    rows = {
        1: (1, 0, 0, 0), 2: (2, 1, 0, 0),
        3: (0, 32, 1, 0), 4: (1, 1, 5, 0),
        5: (2, 1, 1, 0), 6: (-1, 9, 0, 1),
        7: (1, 0, 1, 0), 8: (1, 0, 0, 0),
        9: (0, 0, 1, 0), 10: (1, 1, 2, 1),
    }
    if change:
        rows.update(change)
    if events:
        for slot in events:
            rows.pop(slot, None)
    output = bytearray(gate.RECEIPT_BYTES)
    gate.HEADER.pack_into(output, 0, b"D5C10E1!", 3, 4242,
                          b"synthetic-case", b"a"*64, b"b"*64, 0)
    for slot, (a,b,c,d) in rows.items():
        checksum = gate.MAGIC ^ slot ^ (a & 0xffffffff) ^ (b & 0xffffffff) ^ (c & 0xffffffff) ^ (d & 0xffffffff)
        gate.EVENT.pack_into(output, gate.HEADER.size + (slot-1)*gate.EVENT.size,
                             gate.MAGIC, slot, a, b, c, d, checksum, 32)
    if first == 2:
        reason = first_reason.encode("utf-8")
        code, origin, length = 19, 1, len(reason)
    else:
        reason = b""
        code = origin = length = 0
    gate.FIRST_ERROR.pack_into(output, gate.HEADER.size + 10*gate.EVENT.size,
                               gate.MAGIC, first, code, origin, length, reason)
    return bytes(output)


def parse_mock(raw, *, exit_code=20, pid=4242):
    # Deliberately synthetic process-monitor values. Never real Player proof.
    return gate.parse_material(raw, externally_observed_pid=pid,
                               externally_observed_exit_code=exit_code)


class D5C10NativeReceipt(unittest.TestCase):
    def test_01_fixed_layout(self):
        self.assertEqual((gate.HEADER.size, gate.EVENT.size,
                          gate.FIRST_ERROR.size, gate.RECEIPT_BYTES),
                         (212, 32, 4120, 4652))

    def test_02_denied_candidate_with_real_target_and_side_effect_snapshot(self):
        d=parse_mock(material())
        self.assertEqual(d["result"], "CandidateObservedDeniedInP5_RequiresIndependentBinaryProof")
        self.assertEqual(d["methodBodySideEffect"], "BodyNotExecuted")
        self.assertEqual(d["methodGuard"], "DeniedGuard")
        self.assertFalse(d["actualLinkedBinaryAndPidAuthenticated"])

    def test_03_constructor_guard_no_keep_attempt(self):
        # Constructor may have a guard receipt but target Keep was never invoked.
        d=parse_mock(material(events=[4],change={6:(-1,9,1,0)}))
        self.assertEqual(d["result"], "NoCoverage")

    def test_04_missing_target_guard_receipt(self):
        self.assertEqual(parse_mock(material(change={7:(0,0,0,0)}))["result"],
                         "NoCoverage")

    def test_05_unbound_canary_is_not_denial_proof(self):
        self.assertEqual(parse_mock(material(change={9:(-1,-1,0,0)}))["result"],
                         "NoCoverage")

    def test_06_target_body_increment_is_critical_material(self):
        d=parse_mock(material(change={9:(0,1,1,0)}))
        self.assertEqual(d["methodBodySideEffect"], "BodyExecuted")
        self.assertEqual(d["result"], "UnsafeEarlyMethodAdmissionObserved_SourceMaterial")

    def test_07_allowed_method_guard_without_body_effect_is_critical_material(self):
        d=parse_mock(material(first=0,change={5:(1,1,1,0),7:(1,1,0,0),6:(-1,6,1,1),9:(0,0,1,0),10:(1,1,1,1)}), exit_code=42)
        self.assertEqual(d["methodGuard"], "AllowedGuard")
        self.assertEqual(d["result"], "UnsafeEarlyMethodAdmissionObserved_SourceMaterial")

    def test_08_target_raced_p6_is_not_candidate(self):
        self.assertEqual(parse_mock(material(change={5:(3,1,1,0),7:(0,0,0,1),10:(1,1,3,1)}))["result"],
                         "NoCoverage")

    def test_09_timeout_not_candidate(self):
        self.assertEqual(parse_mock(material(change={8:(1,0,1,0)}))["result"],
                         "NoCoverage")

    def test_10_no_immutable_first_error_for_denial(self):
        self.assertEqual(parse_mock(material(first=0))["result"], "NoCoverage")

    def test_11_missing_seal(self):
        self.assertEqual(parse_mock(material(events=[10]))["result"], "NoCoverage")

    def test_12_partial_receipt_fails_closed(self):
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(material()[:-50])

    def test_13_overlong_receipt_fails_closed(self):
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(material()+b"x")

    def test_14_bad_digest_rejected(self):
        b=bytearray(material()); b[100]=ord("q")
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(bytes(b))

    def test_15_bad_slot_checksum_rejected(self):
        b=bytearray(material()); b[gate.HEADER.size+13] ^= 0x55
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(bytes(b))

    def test_16_bad_first_error_reason_rejected(self):
        b=bytearray(material()); b[-5] = 1
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(bytes(b))

    def test_17_no_managed_completion_is_required_for_native_denial(self):
        # Native Keep guard completed; terminal poison may prevent managed
        # finally/Join, and ReleaseP5 may be absent. Never forge that fact.
        actual = parse_mock(material())
        self.assertEqual(actual["result"],
                         "CandidateObservedDeniedInP5_RequiresIndependentBinaryProof")
        self.assertFalse(actual["nativeWorkerP5ReleaseObserved"])
        self.assertEqual(actual["managedWorkerCompletion"], "Unknown_NotJoined")

    def test_18_inconsistent_keep_attempt_not_denial_proof(self):
        self.assertEqual(parse_mock(material(change={6:(-1,9,1,0)}))["result"],
                         "NoCoverage")

    def test_19_nonterminal_denial_not_enough(self):
        self.assertEqual(parse_mock(material(change={6:(-1,6,1,1)}))["result"],
                         "NoCoverage")

    def test_21_missing_native_guard_completion_slot5(self):
        # This is the exact prior independent RR-03 false positive.
        self.assertEqual(parse_mock(material(events=[5]))["result"],
                         "NoCoverage")

    def test_22_wrong_worker_attempt_token_cannot_claim_denial(self):
        self.assertEqual(parse_mock(material(change={4:(1,2,0,0)}))["result"],
                         "NoCoverage")

    def test_23_guard_event_must_match_native_counter(self):
        self.assertEqual(parse_mock(material(change={5:(2,1,1,0),7:(1,1,0,0)}))["result"],
                         "NoCoverage")

    def test_24_seal_must_be_native_autocollector(self):
        self.assertEqual(parse_mock(material(change={10:(1,1,2,0)}))["result"],
                         "NoCoverage")

    def test_25_completed_target_result_cannot_be_inferred_from_arm(self):
        self.assertEqual(parse_mock(material(change={5:(0,1,1,0)}))["result"],
                         "NoCoverage")

    def test_26_canary_mutation_is_unsafe_even_if_denied_guard(self):
        x=parse_mock(material(change={9:(0,17,1,0)}))
        self.assertEqual(x["result"],"UnsafeEarlyMethodAdmissionObserved_SourceMaterial")

    def test_27_missing_native_P5_event_does_not_promote(self):
        self.assertEqual(parse_mock(material(events=[2]))["result"],"NoCoverage")

    def test_28_native_guard_complete_without_managed_join(self):
        # Guard's immutable same-token event, not a made-up workerFinished=1.
        x=parse_mock(material())
        self.assertEqual(x["result"],"CandidateObservedDeniedInP5_RequiresIndependentBinaryProof")
        self.assertFalse(x["nativeWorkerP5ReleaseObserved"])
        self.assertEqual(x["managedWorkerCompletion"],"Unknown_NotJoined")
        self.assertFalse(x["actualLinkedBinaryAndPidAuthenticated"])

    def test_29_missing_external_process_join_rejected(self):
        self.assertEqual(gate.parse_material(material())["result"], "NoCoverage")

    def test_30_wrong_external_pid_rejected(self):
        self.assertEqual(parse_mock(material(), pid=4243)["result"], "NoCoverage")

    def test_31_failed_native_exit_even_full_slot10_rejected(self):
        self.assertEqual(parse_mock(material(), exit_code=2)["result"], "NoCoverage")

    def test_32_exit_zero_is_never_a_denial_candidate(self):
        self.assertEqual(parse_mock(material(), exit_code=0)["result"], "NoCoverage")

    def test_33_admitted_guard_wrong_exit_code_rejected(self):
        raw = material(first=0, change={5:(1,1,1,0),7:(1,1,0,0),
            6:(-1,6,1,1),9:(0,1,1,0),10:(1,1,1,1)})
        self.assertEqual(parse_mock(raw, exit_code=20)["result"], "NoCoverage")

    def test_34_claimed_external_process_join_remains_not_authenticated(self):
        result = parse_mock(material())
        self.assertTrue(result["externalProcessJoinMatched"])
        self.assertFalse(result["externalProcessProvenanceIndependentlyVerified"])
        self.assertFalse(result["actualLinkedBinaryAndPidAuthenticated"])

    def test_35_preexisting_terminal_before_keep_is_not_healthy_p5(self):
        x=parse_mock(material(change={4:(1,1,9,2)}), exit_code=2)
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardEntryPrecondition"], "PreexistingTerminalOrFirstError")
        self.assertEqual(x["guardEntryState"], 9)
        self.assertEqual(x["guardEntryFirstFailureStatus"], 2)

    def test_36_preexisting_first_failure_writing_rejected(self):
        x=parse_mock(material(change={4:(1,1,5,1)}), exit_code=2)
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardEntryPrecondition"], "PreexistingTerminalOrFirstError")

    def test_37_preexisting_frozen_first_error_in_committing_rejected(self):
        self.assertEqual(parse_mock(material(change={4:(1,1,5,2)}))["result"],
                         "NoCoverage")

    def test_38_target_armed_but_actual_guard_entry_absent(self):
        self.assertEqual(parse_mock(material(events=[4]))["result"], "NoCoverage")

    def test_39_not_committing_at_actual_guard_entry_rejected(self):
        x=parse_mock(material(change={4:(1,1,3,0)}))
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardEntryPrecondition"], "MissingOrUnexpectedGuardEntry")

    def test_40_v1_receipt_cannot_be_interpreted_under_v3_semantics(self):
        b=bytearray(material())
        struct.pack_into("<i",b,8,1)
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(bytes(b))

    def test_41_admitted_guard_without_native_worker_release_preserved_as_unknown(self):
        raw=material(first=0,change={5:(1,1,1,0),7:(1,1,0,0),
            6:(-1,6,0,1),9:(0,0,1,0),10:(1,1,1,1)})
        self.assertEqual(parse_mock(raw,exit_code=42)["result"],"AllowedGuardAtP5_CanaryUnknown")

    def test_42_malformed_native_worker_release_observation_rejected(self):
        self.assertEqual(parse_mock(material(change={6:(-1,9,2,1)}))["result"],
                         "NoCoverage")

    def test_43_healthy_p5_entry_then_terminal_failure_is_bounded_candidate(self):
        x=parse_mock(material())
        self.assertEqual(x["guardEntryPrecondition"],"HealthyP5ObservedNonterminal")
        self.assertEqual(x["result"],"CandidateObservedDeniedInP5_RequiresIndependentBinaryProof")
        self.assertFalse(x["realPlayerC10Passed"])

    def test_44_durable_failure_before_first_error_is_not_healthy(self):
        x = parse_mock(material(change={4:(1,2,5,0),5:(2,1,1,1)}))
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardEntryPrecondition"], "PreexistingTerminalOrFirstError")

    def test_45_mixed_entry_snapshot_is_not_healthy(self):
        x = parse_mock(material(change={4:(1,3,5,0)}))
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardEntryPrecondition"], "RacedOrUnknownGuardEntry")

    def test_46_terminal_denial_raced_healthy_entry(self):
        x = parse_mock(material(change={5:(2,1,1,1)}))
        self.assertEqual(x["result"], "NoCoverage")
        self.assertEqual(x["guardDenialKind"], 1)

    def test_47_unowned_failure_denial_is_not_candidate(self):
        self.assertEqual(parse_mock(material(change={5:(2,1,1,2)}))["result"], "NoCoverage")

    def test_48_allowed_guard_canary_unreadable_is_critical(self):
        raw = material(first=0,change={5:(1,1,1,0),6:(-1,6,1,1),
            7:(1,1,0,0),9:(0,-1,0,0),10:(1,0,1,1)})
        x = parse_mock(raw,exit_code=42)
        self.assertEqual(x["result"], "AllowedGuardAtP5_CanaryUnknown")
        self.assertEqual(x["methodBodySideEffect"], "Unknown")
        self.assertFalse(x["realPlayerC10Passed"])
        self.assertEqual(parse_mock(raw,pid=4243,exit_code=42)["result"],"NoCoverage")

    def test_49_v2_receipt_rejected(self):
        b = bytearray(material())
        struct.pack_into("<i",b,8,2)
        with self.assertRaises(gate.InvalidReceipt):
            parse_mock(bytes(b))

    def test_20_no_false_acceptance(self):
        x=parse_mock(material())
        self.assertFalse(x["realPlayerC10Passed"])
        self.assertFalse(x["R03Accepted"])
        self.assertEqual(x["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")


if __name__=="__main__":
    unittest.main()
