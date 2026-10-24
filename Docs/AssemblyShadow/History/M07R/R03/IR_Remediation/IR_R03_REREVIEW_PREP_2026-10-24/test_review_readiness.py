#!/usr/bin/env python3
"""Host-only adversarial IR-R03-01/02 source and historical-provenance tests.

Uses exact repo source and original checkpoint bytes, never Unity or a Player.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r03_readiness_contract", HERE / "review_readiness.py")
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class ReviewReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = argparse.ArgumentParser()
        for name in ("demo", "native", "hybridclr", "package"):
            parser.add_argument("--" + name, required=True)
        args, _ = parser.parse_known_args()
        cls.demo = pathlib.Path(args.demo)
        cls.native = pathlib.Path(args.native)
        cls.hybridclr = pathlib.Path(args.hybridclr)
        cls.package = pathlib.Path(args.package)
        cls.core = tool.read(cls.native, "libil2cpp/vm/AssemblyShadow.cpp").decode()
        cls.policy = tool.read(cls.native, "libil2cpp/vm/AssemblyShadowTerminalExecution.h").decode()
        cls.runtime = tool.read(cls.native, "libil2cpp/vm/Runtime.cpp").decode()
        cls.interp = tool.read(cls.hybridclr, "hybridclr/interpreter/Interpreter_Execute.cpp").decode()
        cls.player = tool.read(cls.demo, tool.PLAYER).decode()
        cls.runner = tool.read(cls.demo, tool.RUNNER).decode()
        cls.pins = tool.jread(cls.demo, "Tools/AssemblyShadow/R03/source-pins.json")
        cls.transport = tool.jread(cls.demo, tool.S_PREFIX + "/FILE_TRANSPORT.json")
        cls.seal = tool.jread(cls.demo, tool.S_PREFIX + "/batch/seal-receipt.json")
        cls.correction = tool.jread(cls.demo, tool.CORRECTIVE)
        cls.stale = tool.jread(cls.demo, tool.OLD_EVIDENCE)
        cls.review = tool.read(cls.demo, tool.OLD_REVIEW).decode()
        cls.owner = tool.read(cls.demo, tool.OWNER).decode()
        cls.c04 = tool.jread(cls.demo, tool.C04)

    def assert_bad(self, act):
        with self.assertRaises(tool.ReviewReadinessError):
            act()

    def test_01_actual_native_terminal_guard_is_present_not_runtime_certified(self):
        r = tool.check_terminal_source(self.core, self.policy, self.runtime, self.interp)
        self.assertEqual(r["staticGuards"], "PassedPresentSourceContractsOnly")
        self.assertTrue(r["terminalCheckBeforeMethodAndBeforeSuccess"])
        self.assertFalse(r["allDirectAotToAotEntryCovered"])
        self.assertEqual(r["actualPostPoisonPlayerOnCurrentSource"], "NotRun")

    def test_02_remove_early_terminal_denial_rejected(self):
        mutated = self.core.replace(
            "if (TerminalMethodDenied(method)) return false;", "if (false) return false;", 1)
        self.assert_bad(lambda: tool.check_terminal_source(mutated, self.policy,
                                                           self.runtime, self.interp))

    def test_03_remove_second_terminal_denial_rejected(self):
        mutated = self.core.replace(
            "if (error == AssemblyShadowError::Success) return !TerminalMethodDenied(method);",
            "if (error == AssemblyShadowError::Success) return true;", 1)
        self.assert_bad(lambda: tool.check_terminal_source(mutated, self.policy,
                                                           self.runtime, self.interp))

    def test_04_broad_diagnostic_constructor_allowlist_rejected(self):
        mutated = self.core.replace('"InvalidOperationException"', '"AllUserCode"', 1)
        self.assert_bad(lambda: tool.check_terminal_source(mutated, self.policy,
                                                           self.runtime, self.interp))

    def test_05_missing_runtime_guard_rejected(self):
        mutated = self.runtime.replace(
            'AssemblyShadow::RequireActiveMethod(method, "Runtime::InvokeWithThrow");',
            '(void)method;', 1)
        self.assert_bad(lambda: tool.check_terminal_source(self.core, self.policy,
                                                           mutated, self.interp))

    def test_06_missing_interpreter_nested_call_guard_rejected(self):
        mutated = self.interp.replace(
            'REQUIRE_ACTIVE_METHOD(newMethodInfo, "Interpreter.nestedCall")',
            '((void)0)', 1)
        self.assert_bad(lambda: tool.check_terminal_source(self.core, self.policy,
                                                           self.runtime, mutated))

    def test_07_native_disabled_fallback_must_stay_off(self):
        policy = self.policy.replace("(state != kDisabled && durableFailure)",
                                     "(durableFailure)", 1)
        self.assert_bad(lambda: tool.check_terminal_source(self.core, policy,
                                                           self.runtime, self.interp))

    def test_08_player_source_contains_actual_pre_and_post_poison_witness(self):
        r = tool.check_player_fixture(self.player, self.runner, self.pins)
        self.assertEqual(r["sourceFixtureContracts"], "PassedPresentSourceContractsOnly")
        self.assertEqual(r["playerGate"], "BlockedStaleRunnerNativePin")
        self.assertFalse(r["nativePinMatchesCurrent"])
        self.assertEqual(r["freshPostPoisonPlayerExecution"], "NotRun")

    def test_09_missing_side_effect_field_refusal_rejected(self):
        player = self.player.replace("report.finalShadowField == report.preShadowField",
                                     "report.finalShadowField >= report.preShadowField", 1)
        self.assert_bad(lambda: tool.check_player_fixture(player, self.runner, self.pins))

    def test_10_missing_actual_attempt_receipt_rejected(self):
        player = self.player.replace("report.activeReflectionAttempted = true;",
                                     "report.activeReflectionAttempted = false;", 1)
        self.assert_bad(lambda: tool.check_player_fixture(player, self.runner, self.pins))

    def test_11_corrected_original_S_not_old_reconciliation_is_authority(self):
        r = tool.check_original_s(self.transport, self.seal, self.correction,
                                  self.stale, self.review, self.owner, self.c04)
        self.assertEqual(r["originalSArchiveCorrectiveBytes"],
                         "MatchedOriginalCommittedTransportAndSeal")
        self.assertEqual(r["IR_R03_01_Status"], "PartiallyRemediatedAwaitingIndependentRereview")
        self.assertFalse(r["independentArchiveSemanticReauthenticationByThisTool"])
        self.assertTrue(r["stalePrimaryArchiveWithdrawn"])

    def test_12_mutated_original_S_archive_receipt_rejected(self):
        altered = copy.deepcopy(self.transport)
        row = next(x for x in altered["files"]
                   if x["originalPath"] == "batch/evidence.tar.gz")
        row["originalSha256"] = "0" * 64
        self.assert_bad(lambda: tool.check_original_s(altered, self.seal,
                         self.correction, self.stale, self.review, self.owner, self.c04))

    def test_13_stale_primary_archive_not_promoted_to_current_S(self):
        fake = copy.deepcopy(self.correction)
        fake["withdrawnHistoricalClaims"]["status"] = "TrustedAsOriginalS"
        self.assert_bad(lambda: tool.check_original_s(self.transport, self.seal,
                         fake, self.stale, self.review, self.owner, self.c04))

    def test_14_forged_S_archive_seal_digest_rejected(self):
        fake = copy.deepcopy(self.seal)
        fake["archiveSha256"] = self.stale["originalArtifacts"]["evidence.tar.gz"]
        self.assert_bad(lambda: tool.check_original_s(self.transport, fake,
                         self.correction, self.stale, self.review, self.owner, self.c04))

    def test_15_owner_gate_scope_must_remain_D1_A_D2_A(self):
        self.assert_bad(lambda: tool.check_original_s(self.transport, self.seal,
                         self.correction, self.stale, self.review,
                         self.owner.replace("D1=A", "D1=B"), self.c04))

    def test_16_corrective_auditor_must_remain_distinct_from_independent_review(self):
        fake = copy.deepcopy(self.correction)
        fake["observedAudit"]["independentReviewer"] = True
        self.assert_bad(lambda: tool.check_original_s(self.transport, self.seal,
                         fake, self.stale, self.review, self.owner, self.c04))

    def test_17_unknown_C04_fields_are_not_inferred_false(self):
        fake = copy.deepcopy(self.c04)
        fake["newMethodInvocationAttempted"] = False
        self.assert_bad(lambda: tool.check_original_s(self.transport, self.seal,
                         self.correction, self.stale, self.review, self.owner, fake))

    def test_18_actual_full_run_computes_limited_result(self):
        r = tool.verify(self.demo, self.native, self.hybridclr, self.package)
        self.assertEqual(r["result"], "PassedSourceOnlyPreflight_PendingRealPlayerAndIndependentReview")
        self.assertEqual(r["focusedPlayerWitness"]["playerGate"], "BlockedStaleRunnerNativePin")
        self.assertEqual(r["originalSProvenance"]["priorIndependentFullStageResult"], "FAIL")
        for k in ("R03Accepted", "H2Passed", "ReadyForHumanReviewGate",
                  "qualificationApproved", "PureInterpreterEnabled", "runtimeAcceptance"):
            self.assertIs(r[k], False)
        self.assertIs(r["newUnityOrPlayerOrSdkCompilation"], False)

    def test_19_exact_native_source_git_blob_pins(self):
        for path, data in (
            ("libil2cpp/vm/AssemblyShadow.cpp", self.core.encode()),
            ("libil2cpp/vm/AssemblyShadowTerminalExecution.h", self.policy.encode()),
            ("libil2cpp/vm/Runtime.cpp", self.runtime.encode()),
            ("hybridclr/interpreter/Interpreter_Execute.cpp", self.interp.encode()),
        ):
            with self.subTest(path=path):
                self.assertEqual(tool.blob(data), tool.EXPECTED_BLOBS[path])

    def test_20_duplicate_JSON_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d).resolve()
            (root / "invalid.json").write_text('{"state":0,"state":1}')
            self.assert_bad(lambda: tool.jread(root, "invalid.json"))


if __name__ == "__main__":
    unittest.main()
