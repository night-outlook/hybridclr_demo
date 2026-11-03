#!/usr/bin/env python3
"""Host-only adversarial contracts for current 8+2 native suite dispatch.

No Unity SDK, Player, historical original-S process, or installed SDK is run.
Tests the real current Local wrapper's exact receipts/roster and fail-close
rules. Source/host CI also compiles and executes the two actual C++11 suites.
"""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

import current_native_source_gate as source
import run_current_native_host_preflight as host

DEMO = "a" * 40


def legacy():
    heads = host.expected_heads(DEMO)
    return {"schemaVersion": 1, "kind": "R03PrimaryHostOnlyPreflight",
            "result": "PassedHostOnly", "sourcePreserved": True,
            "actualUnityOrPlayerRun": False, "officialUnitySdkCompile": False,
            "runtimeAcceptance": False, "historicalEvidenceUpgraded": False,
            "repositories": [
                {"repository": "night-outlook/" + name, "branch": host.BRANCH,
                 "head": sha, "remoteHead": sha, "clean": True}
                for name, sha in heads.items()
            ],
            "commands": [{"name": name, "status": "Passed"}
                         for name in host.LEGACY_COMPONENTS]}


def complete():
    return {"schemaVersion": 1, "kind": "R03IRCurrentNativeTenHostComponents",
            "result": "PassedHostOnlyTenComponents",
            "expectedDemo": DEMO, "expectedNative": source.CURRENT["il2cpp_plus"],
            "expectedComponentCount": 10, "sourcePreserved": True,
            "actualUnityOrPlayerRun": False, "officialUnitySdkCompile": False,
            "runtimeAcceptance": False, "R03Accepted": False,
            "components": [
                {"name": name, "origin": "ImmutableHistoricalHelper", "status": "Passed"}
                for name in host.LEGACY_COMPONENTS
            ] + [
                {"name": name, "origin": "FreshLocalCurrentOwner",
                 "status": "Passed", "processId": 1234, "exitCode": 0,
                 "unittestCases": tests, "stderrSha256": "f"*64}
                for name, _, tests in host.OWNER_SUITES
            ]}


class CurrentNativeHostContracts(unittest.TestCase):
    def test_01_exact_legacy_and_fresh_rosters(self):
        self.assertEqual(len(host.LEGACY_COMPONENTS), 8)
        self.assertEqual(len(host.OWNER_SUITES), 2)
        self.assertEqual(len(host.ALL_COMPONENTS), 10)
        self.assertEqual(len(set(host.ALL_COMPONENTS)), 10)
        self.assertEqual(host.verify_legacy_report(legacy(), DEMO)[0]["origin"],
                         "ImmutableHistoricalHelper")
        self.assertEqual(host.verify_current_host_report(
            complete(), DEMO, source.CURRENT["il2cpp_plus"])["result"],
            "PassedVerifiedTenLocalNativeHostComponents")

    def test_02_legacy_roster_missing_failing_duplicate_or_fake_head(self):
        cases = (
            lambda x: x["commands"].pop(),
            lambda x: x["commands"][0].update(status="Failed"),
            lambda x: x["commands"].append(copy.deepcopy(x["commands"][0])),
            lambda x: x["repositories"][1].update(head="0"*40),
            lambda x: x["repositories"][1].update(remoteHead="0"*40),
            lambda x: x.update(sourcePreserved=False),
            lambda x: x.update(actualUnityOrPlayerRun=True),
            lambda x: x.update(runtimeAcceptance=True),
            lambda x: x.update(result="ObservedNotAccepted"),
        )
        for mutate in cases:
            with self.subTest(mutation=repr(mutate)):
                x = legacy()
                mutate(x)
                with self.assertRaises(ValueError):
                    host.verify_legacy_report(x, DEMO)

    def test_03_ten_components_not_a_count_or_synthetic_pass(self):
        cases = (
            lambda x: x["components"].pop(),
            lambda x: x["components"].append(copy.deepcopy(x["components"][0])),
            lambda x: x["components"][8].update(status="NotRun"),
            lambda x: x["components"][8].update(origin="ImmutableHistoricalHelper"),
            lambda x: x["components"][9].update(exitCode=71),
            lambda x: x["components"][9].update(unittestCases=0),
            lambda x: x["components"][9].update(processId=True),
            lambda x: x.update(expectedComponentCount=True),
            lambda x: x.update(result="PassedHostOnly"),
            lambda x: x.update(sourcePreserved=False),
            lambda x: x.update(runtimeAcceptance=True),
            lambda x: x.update(R03Accepted=True),
            lambda x: x.update(expectedNative="0"*40),
            lambda x: x.update(expectedDemo="b"*40),
        )
        for mutate in cases:
            with self.subTest(mutation=repr(mutate)):
                x = complete()
                mutate(x)
                with self.assertRaises(ValueError):
                    host.verify_current_host_report(x, DEMO, source.CURRENT["il2cpp_plus"])

    def test_04_fresh_owner_requires_real_hashed_two_three_case_receipts(self):
        with tempfile.TemporaryDirectory(prefix="r03-owner-receipt-") as tmp:
            root = Path(tmp)
            name = host.OWNER_SUITES[0][0]
            folder = root / "steps" / name
            folder.mkdir(parents=True)
            p = folder / "stderr.log"
            p.write_text("test_a ... ok\ntest_b ... ok\n\nRan 2 tests in 0.05s\n\nOK\n")
            row = {"name": name, "state": "Passed", "exitCode": 0,
                   "processId": 123, "timedOut": False,
                   "mayHaveExternalOwnedChildren": False,
                   "stderrSha256": host.digest(p), "stdoutSha256": "b"*64}
            got = host.verify_owner_run(row, root, name, 2)
            self.assertEqual(got["unittestCases"], 2)
            p.write_text("Ran 2 tests in 0.05s\nFAILED (failures=1)\n")
            row["stderrSha256"] = host.digest(p)
            with self.assertRaises(ValueError):
                host.verify_owner_run(row, root, name, 2)
            p.write_text("Ran 1 test in 0.05s\nOK\n")
            row["stderrSha256"] = host.digest(p)
            with self.assertRaises(ValueError):
                host.verify_owner_run(row, root, name, 2)
            p.write_text("Ran 2 tests in 0.05s\nOK\n")
            row["stderrSha256"] = "0"*64
            with self.assertRaises(ValueError):
                host.verify_owner_run(row, root, name, 2)

    def test_05_actual_historical_helper_is_unchanged(self):
        self.assertEqual(source.git_blob(host.LEGACY_HELPER.read_bytes()),
                         host.LEGACY_HELPER_BLOB)
        self.assertEqual(host.LEGACY_HELPER_BLOB,
                         "2d51be157b94a47ac19d1061d0066c1f98dbc177")

    def test_06_current_wrapper_fail_stops_unity_and_checks_final_report(self):
        import run_current_native_validation_cycle as cycle
        text = Path(cycle.__file__).read_text(encoding="utf-8")
        self.assertIn('script / "run_current_native_host_preflight.py"', text)
        self.assertIn("verify_current_host_report(", text)
        self.assertIn('step_ok(stages["native-host-diagnostics"])', text)
        self.assertIn('"current-native-players"] = {', text)
        self.assertIn('"state": "Blocked"', text)
        self.assertLess(text.index('script / "run_current_native_host_preflight.py"'),
                        text.index('script / "run_terminal_current.py"'))
        self.assertNotIn('script / "run_primary_host_preflight.py"', text)

    def test_07_current_host_uses_new_receipt_root_no_historical_write(self):
        src = Path(host.__file__).read_text(encoding="utf-8")
        self.assertIn('output / "historical-eight"', src)
        self.assertIn('source.git_blob(LEGACY_HELPER.read_bytes())', src)
        self.assertIn('historical.verify_repo(workspace, name, expected)', src)
        self.assertLess(src.index('historical.verify_repo(workspace, name, expected)'),
                        src.index('output.mkdir(mode=0o700)'))
        self.assertIn('output.mkdir(mode=0o700)', src)
        self.assertIn('result["result"] = "FailedOrIncomplete"', src)
        self.assertIn('"expectedComponentCount": 10', src)
        self.assertIn('source_fingerprints(args.workspace)', src)
        self.assertIn('len(components) == 10', src)

    def test_08_actual_ci_workflow_runs_host_contract_and_two_cxx_suites(self):
        root = Path(__file__).resolve().parents[3]
        workflow = (root / ".github/workflows/r03-ir-current-native-local-cycle-host.yml").read_text()
        for script in ("current_native_host_contracts.py",
                       "native_owner_decision_contracts.py",
                       "engine_owner_quit_contracts.py"):
            self.assertIn("python3 -B Tools/AssemblyShadow/R03IR/" + script, workflow)
        self.assertIn("Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
