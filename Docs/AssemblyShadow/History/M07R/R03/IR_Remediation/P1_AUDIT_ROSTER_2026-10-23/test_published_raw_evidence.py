#!/usr/bin/env python3
"""Independent check of PUBLISHED b7e3 receipts only; no compiler or full audit."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "local-validation-p1-admitted-execution-20261023-b7e3"
BATCH = ARCHIVE / "batch"
PREFLIGHT = ARCHIVE / "preflight"
RAW_SHA = "f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6"
MANIFEST_SHA = "4b286c29a7ef36ec4377642b6009804ad532b0ae3166c186866fe74f4246130e"
ORIGINAL_AUDITOR_SHA = "2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0"
NAMES = (
    "command-failures", "legacy-host", "metadata-gate", "bounded-class",
    "bounded-physical", "bounded-first-use", "owned-general", "live-general",
    "owned-execution", "empty-live", "opaque-inventory", "physical-membership",
    "owned-physical-names", "owned-physical-json", "live-owned-physical-json",
    "observed-type-shape", "live-type-shape-census", "observed-type-shape-json",
    "vm-shape-json", "admitted-execution", "bounded-status", "bounded-inventory",
    "frozen-v2", "managed-sdk", "native-sdk",
)
ADMITTED_GROUPS = (
    "closed-before-first-init", "original-reader-opens-once",
    "actual-old-getter-inside-reader", "separate-output-owned-after-admission",
    "original-error-code-propagated", "original-exception-unwinds-reader",
    "shutdown-blocked-until-reader-exits",
    "shutdown-refuses-without-calling-getter",
    "reopen-epoch-two-refuses-unproven-source",
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_bytes())


class PublishedEvidenceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read_json(BATCH / "RESULT.json")
        cls.manifest = read_json(BATCH / "MANIFEST.json")
        cls.admitted = read_json(BATCH / "admitted-execution/RESULT.json")
        cls.contracts = read_json(BATCH / "command-failures/RESULT.json")
        cls.managed = read_json(BATCH / "managed-sdk/build-api/results.json")
        cls.native = read_json(BATCH / "native-sdk/results.json")
        cls.facts = read_json(PREFLIGHT / "FACTUAL_RECEIPT_OBSERVATIONS.json")
        cls.preservation = read_json(PREFLIGHT / "INDEPENDENT_PRESERVATION_AFTER.json")
        cls.local = read_json(ARCHIVE / "LOCAL_RESULT.json")

    def test_01_pinned_raw_and_manifest_bytes(self):
        self.assertEqual(digest((BATCH / "RESULT.json").read_bytes()), RAW_SHA)
        self.assertEqual(digest((BATCH / "MANIFEST.json").read_bytes()), MANIFEST_SHA)
        self.assertEqual(self.manifest["inventoryScope"], "CompletedBatchFiles")
        self.assertFalse(self.manifest["commandLifetimeUnverified"])

    def test_02_selected_published_files_are_sha_bound_into_manifest(self):
        index = collections.defaultdict(list)
        for row in self.manifest["files"]:
            index[row["path"]].append(row)
        for rel in (
            "RESULT.json", "admitted-execution/RESULT.json",
            "command-failures/RESULT.json", "managed-sdk/build-api/results.json",
            "native-sdk/results.json",
        ):
            with self.subTest(rel=rel):
                self.assertEqual(len(index[rel]), 1)
                raw = (BATCH / rel).read_bytes()
                self.assertEqual(len(raw), index[rel][0]["size"])
                self.assertEqual(digest(raw), index[rel][0]["sha256"])

    def test_03_raw25_identity_and_lifetime_status(self):
        self.assertEqual(self.raw["kind"], "R03P1FailureAwareSourceSDKPreflight")
        self.assertEqual(self.raw["result"], "PassedSourceHostAndSDKOnly")
        self.assertEqual(self.raw["componentCount"], self.raw["attemptedComponentCount"])
        self.assertEqual(self.raw["componentCount"], 25)
        self.assertEqual(tuple(c["name"] for c in self.raw["commands"]), NAMES)
        self.assertEqual({c["status"] for c in self.raw["commands"]}, {"Passed"})
        self.assertIsNone(self.raw["stoppedAfter"])
        self.assertIsNone(self.raw["postflightError"])
        self.assertTrue(self.raw["sourcePreserved"])
        self.assertFalse(self.raw["commandLifetimeUnverified"])
        self.assertFalse(self.raw["UnityPlayerExecuted"])

    def test_04_original_85_tests_are_distinct_and_have_zero_failures(self):
        d = self.contracts
        self.assertEqual(d["result"], "PassedWithinHostScope")
        self.assertEqual(d["expectedTestCount"], d["testsRun"])
        self.assertEqual(d["testsRun"], len(d["testIds"]))
        self.assertEqual(len(set(d["testIds"])), 85)
        self.assertEqual([m["expectedTests"] for m in d["modules"]], [5, 14, 44, 10, 12])
        for key in ("failures", "errors", "skipped", "unexpectedSuccesses"):
            self.assertEqual(d[key], 0)

    def test_05_admitted_strict_and_sanitized_nine_groups(self):
        d = self.admitted
        self.assertEqual(d["result"], "PassedWithinInactiveMetadataAdmittedExecutionHostScope")
        for profile in ("strict", "sanitized"):
            with self.subTest(profile=profile):
                self.assertEqual(tuple(d["profiles"][profile]["caseGroups"]), ADMITTED_GROUPS)
                self.assertEqual(d["profiles"][profile]["result"], d["result"])
        self.assertTrue(d["actualSourceCompiled"])
        self.assertTrue(d["originalGetterNotActivated"])
        for key in ("canonicalExecutionTypeKeys", "coherentVmEpochProven",
                    "physicalPointerOriginProven", "runtimeAcceptance",
                    "UnityPlayerExecuted"):
            self.assertFalse(d[key], key)

    def test_06_managed_six_command_receipts_are_sha_bound(self):
        d = self.managed
        self.assertEqual(d["result"], "Passed")
        self.assertEqual(d["unityVersion"], "2022.3.62f2")
        self.assertEqual(len(d["inputs"]), 428)
        self.assertEqual(len(d["commands"]), 6)
        self.assertEqual([c["expectedExit"] for c in d["commands"]], [0, 0, 0, 0, 0, 1])
        self.assertEqual(d["commands"][-1]["id"], "OriginalUnsignedCounts")
        for i, row in enumerate(d["commands"], 1):
            with self.subTest(index=i):
                receipt = BATCH / f"managed-sdk/commands/{i:04d}/command.json"
                self.assertEqual(digest(receipt.read_bytes()), row["receipt"]["sha256"])
                self.assertEqual(len(receipt.read_bytes()), row["receipt"]["size"])
                observed = read_json(receipt)
                self.assertEqual(observed["exitCode"], row["expectedExit"])
                self.assertFalse(observed["timeout"])
                self.assertFalse(observed["remainingProcessGroup"])
                self.assertFalse(observed["postCleanupGroupExists"])

    def test_07_native_100_syntax_receipts_plus_version_are_sha_bound(self):
        d = self.native
        self.assertEqual(d["kind"], "R03NativeRuntimePrerequisites")
        self.assertEqual(d["result"], "Passed")
        self.assertEqual(d["plannedTranslationUnitCount"], 100)
        self.assertEqual(len(d["commands"]), 101)
        units = collections.Counter()
        for i, row in enumerate(d["commands"], 1):
            with self.subTest(index=i):
                receipt = BATCH / f"native-sdk/commands/{i:04d}/command.json"
                self.assertEqual(digest(receipt.read_bytes()), row["sha256"])
                cmd = read_json(receipt)
                self.assertEqual(cmd["exitCode"], 0)
                self.assertFalse(cmd["timeout"])
                self.assertFalse(cmd["interrupted"])
                self.assertFalse(cmd["remainingProcessGroup"])
                self.assertFalse(cmd["postCleanupGroupExists"])
                argv = cmd["command"]
                if i == 1:
                    self.assertIn("--version", argv)
                else:
                    self.assertIn("-fsyntax-only", argv)
                    self.assertIn("-std=c++17", argv)
                    self.assertIn("-arch", argv)
                    self.assertEqual(argv[argv.index("-arch") + 1], "arm64")
                    units[Path(argv[-1]).name] += 1
        self.assertEqual(len(units), 20)
        self.assertEqual(set(units.values()), {5})

    def test_08_original_twenty_git_postflight_claim_retained(self):
        d = self.raw["postflightGitDiagnostics"]
        self.assertEqual(d["actualDirectCommandCount"], 20)
        self.assertEqual(d["completedRepositoryCount"], 4)
        self.assertEqual(d["timedOutCommands"], 0)
        self.assertEqual(d["completedNonzeroCommands"], 0)
        self.assertFalse(d["commandLifetimeUnverified"])
        self.assertFalse(d["descendantQuiescenceProven"])

    def test_09_reported_preservation_kept_separate_from_full_audit(self):
        d = self.preservation
        self.assertEqual(d["result"], "Preserved")
        self.assertTrue(d["installedSdkUnchanged"])
        self.assertTrue(d["sourceBindingsPreserved"])
        self.assertEqual(d["sdkFiles"], 2405)
        self.assertEqual(d["sdkBytes"], 316062203)
        self.assertEqual(d["consumedP1RawScratchAuditSets"], 22)
        self.assertEqual(d["originalCheckpointSets"], 24)
        self.assertEqual(d["negativeControlSymlinks"], 88)
        self.assertEqual(d["separateBlockedCheckpoints"], ["e1e5", "6c72"])
        self.assertTrue(d["acceptanceFlagsRemainFalse"])

    def test_10_full_auditor_failure_and_local_fail_are_not_promoted(self):
        self.assertEqual(self.local["result"], "FAIL")
        self.assertEqual(self.facts["completeRequiredIndependentAudit"], "FailedAtLine190")
        self.assertEqual(self.facts["laterOriginalAuditStatements"], "NotRun")
        self.assertTrue(self.facts["noRawResultReclassification"])
        self.assertEqual(self.facts["rawAggregate"], "PassedSourceHostAndSDKOnly")
        self.assertEqual(digest((PREFLIGHT / "audit.py").read_bytes()), ORIGINAL_AUDITOR_SHA)
        self.assertFalse((PREFLIGHT / "EVIDENCE_AUDIT.json").exists())


if __name__ == "__main__":
    unittest.main()
