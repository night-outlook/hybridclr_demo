#!/usr/bin/env python3
"""Exercise the REAL shared B1 source validator consumed by Mac admission and
the oneuse-11 runner, against four real, pinned GitHub CI checkouts.

Only original-S/Unity/capacity/toolchain prerequisites are replaced by
*explicit mocks* for a non-Mac host. Actual repository identity, HEAD,
remote/branch/clean checks and source/VM delta validations are NEVER mocked
in the positive path. This is source-only, not a Unity/Player result.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import current_native_environment_admission as admission
import current_native_source_gate as source
import current_native_vm_delta_contracts as delta
import run_current_native_validation_cycle as cycle
import run_current_native_host_preflight as host
from batch_contract import ContractError

WORKSPACE: Path | None = None
DEMO_SHA: str | None = None


class SharedB1AdmissionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = WORKSPACE
        cls.sha = DEMO_SHA
        if cls.workspace is None or cls.sha is None:
            raise ValueError("Exact four-repository workspace and demo commit required")
        cls.roots = {name: cls.workspace / name for name in cycle.REPOS}

    def test_01_exact_14_and_47_shared_runner_admission(self):
        result = cycle.validate_sources(self.workspace, self.sha)
        self.assertEqual(result["result"], "PassedReadOnlySourceAdmission_NotBuildOrRuntime")
        self.assertEqual(result["sourceGate"]["verifiedSourceFiles"], 14)
        self.assertEqual(result["vmDelta"]["changedVmFileCount"], 46)
        self.assertEqual(result["sourceGate"]["currentCandidatePins"], source.CURRENT)
        self.assertEqual(result["vmDelta"]["currentNativeCommit"], source.CURRENT["il2cpp_plus"])
        self.assertEqual(
            {r["repository"]: r["commit"] for r in result["repositories"]},
            {"night-outlook/hybridclr_demo": self.sha,
             **{"night-outlook/" + key: val for key, val in source.CURRENT.items()}})
        self.assertIs(result["R03Accepted"], False)
        self.assertIs(result["ReadyForHumanReviewGate"], False)

    def test_02_same_path_called_by_mac_readmission(self):
        """Admit real source via the Mac wrapper; do not simulate Mac acceptance."""
        with tempfile.TemporaryDirectory(prefix="r03-b1-admission-host-") as tmp:
            root = Path(tmp).resolve(strict=True)
            # Outside checkouts, absent; all local environment checks mocked.
            original = root / "unavailable-original-s"
            unity = root / "unavailable-unity"
            output = root / "unused"
            with mock.patch.object(cycle, "validate_destination") as destination, \
                 mock.patch.object(admission, "registered_original",
                     return_value={"result":"MockedOriginalS_NotAvailableOnCI"}), \
                 mock.patch.object(cycle, "validate_machine",
                     return_value={"result":"MockedMacMachine_NotAvailableOnCI"}), \
                 mock.patch.object(admission, "verify_toolchain",
                     return_value={"result":"MockedToolchain_NotAvailableOnCI"}), \
                 mock.patch.object(admission, "verify_standalone_current_cli",
                     return_value={"result":"MockedCli_NotAvailableOnCI"}), \
                 mock.patch.object(admission, "sample_capacity",
                     return_value={"result":"MockedCapacity_NotAvailableOnCI"}):
                result = admission.inspect(self.workspace, original, unity, output, self.sha)
            destination.assert_called_once_with(self.workspace, original, output)
            self.assertEqual(result["currentSource"]["sourceGate"]["verifiedSourceFiles"], 14)
            self.assertEqual(result["currentSource"]["vmDelta"]["changedVmFileCount"], 46)
            self.assertEqual(result["result"], "PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun")
            self.assertTrue(result["runRootCreated"] is False and
                            result["coordinatorInvoked"] is False and
                            result["archiveOrPlayerExecuted"] is False)
            self.assertFalse(output.exists())

    def test_03_old_11_45_source_profile_rejected_by_exact_shared_gate(self):
        """A forged success label is insufficient when the old roster is returned."""
        original = source.verify_source_roots(self.roots, require_checkout_heads=True)
        old = copy.deepcopy(original)
        old["verifiedSourceFiles"] = 11
        with mock.patch.object(source, "verify_source_roots", return_value=old), \
             mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}):
            with self.assertRaisesRegex(ValueError, "Fourteen-file B1"):
                cycle.validate_sources(self.workspace, self.sha)

    def test_04_old_45_vm_inventory_rejected_by_exact_shared_gate(self):
        original = source.verify_source_roots(self.roots, require_checkout_heads=True)
        old = {"result": "PassedCurrentNativeVmSourceDeltaOnly",
               "changedVmFileCount": 45,
               "currentNativeCommit": source.CURRENT["il2cpp_plus"]}
        with mock.patch.object(source, "verify_source_roots", return_value=original), \
             mock.patch.object(delta, "validate", return_value=old), \
             mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}):
            with self.assertRaisesRegex(ValueError, "Forty-six-file B1"):
                cycle.validate_sources(self.workspace, self.sha)

    def test_05_native_candidate_pin_mutation_rejected_by_real_gate(self):
        with tempfile.TemporaryDirectory(prefix="r03-b1-wrong-pin-") as tmp:
            path = Path(tmp) / "mutated-current-candidate.json"
            doc = json.loads(source.CONFIG.read_text())
            doc["candidateNativePin"] = "41764ae1eeefb33b05966e7f7676e52aae39c340"
            path.write_text(json.dumps(doc), encoding="utf-8")
            # read_config(path=CONFIG) captures its default at definition
            # time; replace the callable so this mutation truly reaches the
            # identical production parser rather than patching a dead constant.
            real_reader = source.read_config
            with mock.patch.object(source, "read_config",
                         side_effect=lambda: real_reader(path)), \
                 mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}):
                with self.assertRaises(source.CandidateSourceError):
                    cycle.validate_sources(self.workspace, self.sha)

    def test_06_vm_path_and_blob_mutation_rejected_by_real_delta_validator(self):
        with tempfile.TemporaryDirectory(prefix="r03-b1-vm-drift-") as tmp:
            path = Path(tmp) / "mutated-native-delta.json"
            doc = json.loads(delta.MANIFEST.read_text())
            doc["files"][0]["gitBlob"] = "0"*40
            path.write_text(json.dumps(doc), encoding="utf-8")
            with mock.patch.object(delta, "MANIFEST", path), \
                 mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}):
                with self.assertRaises(delta.SourceDeltaError):
                    cycle.validate_sources(self.workspace, self.sha)

    def test_07_wrong_native_repo_head_refused_before_any_product_run(self):
        with mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}), \
             mock.patch.object(source, "git_head", side_effect=lambda p:
                 "0"*40 if p == self.roots["il2cpp_plus"] else
                 (self.sha if p == self.roots["hybridclr_demo"] else
                  source.CURRENT[p.name])):
            with self.assertRaises(source.CandidateSourceError):
                cycle.validate_sources(self.workspace, self.sha)

    def test_08_wrong_demo_sha_refused_before_any_product_run(self):
        with self.assertRaises(ContractError):
            cycle.validate_sources(self.workspace, "f"*40)

    def test_10_real_inner_native_host_source_admission(self):
        # Source-only execution of the *actual* inner host preflight. A
        # source-inventory PASS on the outer runner must not hide a stale
        # validation contract reached later by the same one-use cycle.
        report = host.inputs(self.workspace, self.sha, source.CURRENT["il2cpp_plus"])
        self.assertEqual(report["verifiedSourceFiles"], 14)
        self.assertEqual(report["currentCandidatePins"], source.CURRENT)
        self.assertEqual(report["result"],
                         "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation")

    def test_11_inner_native_host_old_source_and_vm_counts_fail_closed(self):
        genuine = source.verify_source_roots(self.roots, require_checkout_heads=True)
        native = {"result": "PassedCurrentNativeVmSourceDeltaOnly",
                  "changedVmFileCount": 46,
                  "currentNativeCommit": source.CURRENT["il2cpp_plus"]}
        stale_source = copy.deepcopy(genuine)
        stale_source["verifiedSourceFiles"] = 11
        with mock.patch.object(source, "verify_source_roots", return_value=stale_source), \
             mock.patch.object(host.delta, "validate", return_value=native):
            with self.assertRaisesRegex(ValueError, "fourteen-source B1"):
                host.inputs(self.workspace, self.sha, source.CURRENT["il2cpp_plus"])
        stale_vm = copy.deepcopy(native)
        stale_vm["changedVmFileCount"] = 45
        with mock.patch.object(source, "verify_source_roots", return_value=genuine), \
             mock.patch.object(host.delta, "validate", return_value=stale_vm):
            with self.assertRaisesRegex(ValueError, "forty-six-file B1"):
                host.inputs(self.workspace, self.sha, source.CURRENT["il2cpp_plus"])

    def test_09_no_generated_output_or_source_edits(self):
        self.assertEqual(len(source.FILES), 14)
        self.assertEqual(len(delta.EXPECTED_VM_NAMES), 46)
        self.assertEqual(cycle.NATIVE, source.CURRENT["il2cpp_plus"])
        for p in (self.workspace / "oneuse-12", self.workspace / "oneuse-11", self.workspace / "oneuse-10"):
            self.assertFalse(p.exists(), "Host tests must never create runtime roots")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--demo-commit", required=True)
    args = parser.parse_args()
    WORKSPACE = args.workspace
    DEMO_SHA = args.demo_commit
    unittest.main(argv=["b1-real-shared-admission"], verbosity=2)
