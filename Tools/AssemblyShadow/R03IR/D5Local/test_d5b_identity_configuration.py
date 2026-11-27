#!/usr/bin/env python3
"""AP6 bounded composition tests with an explicit AP5 orchestration double.

The unit success path uses real AP2 checkout observations and unchanged AP4
configuration consumers. Its AP5 stage is deliberately doubled: these tests
do not establish five real sibling identities or production remote reachability.
The separate CI integration file covers the pinned real sibling checkouts.
Run this file with trusted Python -I -S -B.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import copy
from dataclasses import FrozenInstanceError
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import unittest
from unittest import mock


HERE = Path(__file__).resolve(strict=True).parent
sys.path.insert(0, str(HERE))
import d5b_identity_configuration as observer
import test_d5b_runner_imports as ap3_tests

AP2 = ap3_tests.ap2_tests.closure
AP1 = ap3_tests.ap2_tests.publication
RUNNER_REF = "refs/heads/codex/ap6-fixture"
SHARED_FIELDS = ("sourcePins", "sourceRef", "runner", "locations", "authorization")
CHECKOUT_FIELDS = (
    "head", "branch", "origin", "gitDir", "commonDir", "configSha256",
    "indexFlagsSha256", "indexStagesSha256", "worktreeInventorySha256",
    "worktreeFiles", "worktreeEntries", "worktreeBytes",
)
HELPER_PREFIXES = (
    "_ap6_verified_", "_ap5_verified_ap2_", "_ap4_verified_ap3_", "_ap3_verified_ap2_",
)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class _AP6Fixture(ap3_tests._AP2FixtureAdapter):
    """Fixture construction only; no earlier suite's test methods are inherited."""

    def setUp(self):
        super().setUp()
        self.runner_ref = RUNNER_REF
        self.runner_branch = RUNNER_REF.removeprefix("refs/heads/")
        self._checkout(self.source_commit, self.runner_commit)
        self.proposal = self._make_proposal()
        self.raw = canonical(self.proposal)
        self.pin = blob(self.raw)
        self.identity = {
            "schemaVersion": 1, "kind": "R03D5BFiveIdentityProposalV1",
            **{key: copy.deepcopy(self.proposal[key]) for key in SHARED_FIELDS},
            "scope": "CheckoutAndLiveRefObservationOnly_NoExecutionAuthority",
        }
        self.identity_raw = canonical(self.identity)
        self.identity_pin = blob(self.identity_raw)
        self.stage_calls = []

    def _registry(self):
        return {name: module for name, module in sys.modules.items()
                if name.startswith(HELPER_PREFIXES)}

    def _closed(self, report):
        for key, value in AP1.CLOSED_AUTHORITY.items():
            self.assertEqual(report[key], value, key)
            self.assertIs(type(report[key]), type(value), key)
        for key in (
            "executionAuthorityVerified", "runtimeConfigurationReadsBound",
            "runnerExecutableClosureVerified", "exclusiveCustodyVerified",
            "continuousCustodyVerified", "candidateEntryPointsInvoked",
            "admissionPreviewInvoked", "UnityOrPlayerExecuted", "outputCreated",
        ):
            self.assertIs(report[key], False, key)
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)

    def _observe(self, closure_raw=None, closure_pin=None, identity_raw=None, identity_pin=None):
        before = self._registry()
        try:
            return observer.observe_identity_configuration(
                self.raw if closure_raw is None else closure_raw,
                self.pin if closure_pin is None else closure_pin,
                self.identity_raw if identity_raw is None else identity_raw,
                self.identity_pin if identity_pin is None else identity_pin)
        finally:
            self.assertEqual(self._registry(), before)

    def _reject(self, *args, **kwargs):
        with self.assertRaises(observer.Rejected) as caught:
            self._observe(*args, **kwargs)
        report = caught.exception.report
        self.assertEqual(report["result"], "IdentityConfigurationRejected_NoExecutionAuthority")
        self._closed(report)
        return report

    def _unit_identity_report(self, helper):
        # Deliberate stage double. Only these runner/location values come from
        # actual accepted AP2 observations; no sibling or live-ref claim is made
        # by the test evidence outside the simulated AP5 report.
        artifact = AP2.verify_runner_closure(self.raw, self.pin).report
        progress = helper._progress()
        progress["sourcePinsMatchAcceptedAP1SiblingPins"] = True
        progress["localPassesCompleted"] = ["before", "after"]
        progress["checkoutObservations"]["after"]["runner"] = artifact["observedCheckout"]
        progress["locationObservations"]["after"] = artifact["observedLocations"]
        return {
            **helper._closed_report(helper.SUCCESS_RESULT, progress),
            "proposalGitBlob": self.identity_pin,
            "sourcePins": copy.deepcopy(self.identity["sourcePins"]),
            "runner": copy.deepcopy(self.identity["runner"]),
        }

    @contextmanager
    def _unit_stages(self, *, identity_transform=None, configuration_transform=None,
                     identity_failure=None, configuration_failure=None, interrupt_profile=False,
                     before_configuration=None, before_consumption=None):
        real_loader = observer._load_helper
        captured = {}

        @contextmanager
        def wrapped_loader(role, progress):
            with real_loader(role, progress) as helper:
                if role == "identity":
                    def identity_stage(raw, pin):
                        self.stage_calls.append(("identity", raw, pin))
                        if identity_failure is not None:
                            error = identity_failure(helper)
                            if hasattr(error, "report"):
                                captured[role] = error.report
                            raise error
                        report = self._unit_identity_report(helper)
                        if identity_transform is not None:
                            identity_transform(report)
                        captured[role] = report
                        return helper.FiveIdentityObservation(canonical(report))
                    with mock.patch.object(helper, "observe_five_identities", side_effect=identity_stage):
                        yield helper
                else:
                    self.assertEqual(role, "configuration")
                    actual = helper.observe_runner_configuration
                    def configuration_stage(raw, pin):
                        self.stage_calls.append(("configuration", raw, pin))
                        if configuration_failure is not None:
                            error = configuration_failure(helper)
                            if hasattr(error, "report"):
                                captured[role] = error.report
                            raise error
                        try:
                            if before_configuration is not None:
                                before_configuration()
                            with ExitStack() as stack:
                                if interrupt_profile:
                                    read_bytes = helper._CapturedFile.read_bytes
                                    def interrupted_read(view):
                                        if view.path == helper.PROFILE_PATH:
                                            raise OSError("AP6 unit fixture interrupted captured profile read")
                                        return read_bytes(view)
                                    stack.enter_context(mock.patch.object(
                                        helper._CapturedFile, "read_bytes", interrupted_read))
                                if before_consumption is not None:
                                    consume = helper._consume_configuration
                                    def observed_consumption(context, child_progress):
                                        before_consumption(context, child_progress)
                                        return consume(context, child_progress)
                                    stack.enter_context(mock.patch.object(
                                        helper, "_consume_configuration", side_effect=observed_consumption))
                                report = actual(raw, pin).report
                        except helper.Rejected as error:
                            captured[role] = error.report
                            raise
                        if configuration_transform is not None:
                            configuration_transform(report)
                        captured[role] = report
                        return helper.ConfigurationObservation(canonical(report))
                    with mock.patch.object(helper, "observe_runner_configuration", side_effect=configuration_stage):
                        yield helper

        with mock.patch.object(observer, "_load_helper", side_effect=wrapped_loader):
            yield captured


class D5BIdentityConfigurationComposition(_AP6Fixture):
    def test_01_public_api_is_four_exact_inputs_and_has_no_execution_mode(self):
        self.assertEqual(list(inspect.signature(observer.observe_identity_configuration).parameters),
                         ["closure_raw", "expected_closure_blob", "identity_raw", "expected_identity_blob"])
        self.assertEqual(observer.SUCCESS_RESULT, "IdentityConfigurationObserved_NoExecutionAuthority")
        self.assertEqual(observer.REJECTED_RESULT, "IdentityConfigurationRejected_NoExecutionAuthority")

    def test_02_stage_order_preserves_raw_inputs_and_real_ap4_consumers(self):
        with self._unit_stages() as captured:
            result = self._observe()
        report = result.report
        self.assertIsInstance(result, observer.IdentityConfigurationObservation)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertEqual(self.stage_calls, [
            ("identity", self.identity_raw, self.identity_pin),
            ("configuration", self.raw, self.pin),
        ])
        self.assertEqual(report["stageCallsAttempted"], ["identity", "configuration"])
        self.assertEqual(report["stageCallsReturned"], ["identity", "configuration"])
        self.assertEqual(report["stageCallsCompleted"], ["identity", "configuration"])
        self.assertIs(report["proposalFieldsMatched"], True)
        self.assertIs(report["fixedAP1SiblingPinsMatched"], True)
        self.assertEqual(report["matchedProposalProjection"],
                         {field: self.identity[field] for field in SHARED_FIELDS})
        self.assertIs(report["sharedObservationsMatched"], True)
        self.assertEqual(report["comparisonCallsAttempted"], ["runner", "locations"])
        self.assertEqual(report["comparisonCallsCompleted"], ["runner", "locations"])
        self.assertEqual(report["observations"], captured)
        self.assertEqual(captured["configuration"]["configurationConsumerCallsCompleted"], [
            "d5b_local_admission.read_plan", "d5b_rr5_source_preflight.checked_profile",
        ])
        self._closed(report)
        self._closed(captured["identity"])
        self._closed(captured["configuration"])

    def test_03_bad_external_pins_reject_before_helper_loading(self):
        for changes in ({"closure_pin": "0" * 40}, {"identity_pin": "0" * 40},
                        {"closure_pin": "G" * 40}, {"identity_pin": True}):
            with self.subTest(changes=changes):
                with mock.patch.object(observer, "_load_helper") as loader:
                    report = self._reject(**changes)
                loader.assert_not_called()
                self.assertEqual(report["stageCallsAttempted"], [])

    def test_04_changed_raw_bytes_reject_before_stages(self):
        oversized = b" " * (observer.MAX_BYTES + 1)
        for changes in ({"closure_raw": self.raw + b"\n"},
                        {"identity_raw": self.identity_raw + b"\n"},
                        {"closure_raw": self.raw.decode()},
                        {"identity_raw": bytearray(self.identity_raw)},
                        {"closure_raw": oversized, "closure_pin": blob(oversized)},
                        {"identity_raw": oversized, "identity_pin": blob(oversized)}):
            with self.subTest(field=next(iter(changes))):
                with mock.patch.object(observer, "_load_helper") as loader:
                    report = self._reject(**changes)
                loader.assert_not_called()
                self.assertEqual(report["stageCallsAttempted"], [])

    def test_05_strict_json_rejects_duplicates_nonfinite_and_nonobjects(self):
        variants = (
            ("closure", self.raw.replace(b'"schemaVersion": 1', b'"schemaVersion": 1, "schemaVersion": 1', 1)),
            ("identity", self.identity_raw.replace(b'"schemaVersion": 1', b'"schemaVersion": 1, "schemaVersion": 1', 1)),
            ("closure", b'[]'), ("identity", b'{"schemaVersion": NaN}'),
            ("identity", b'{"schemaVersion": "\xff"}'),
        )
        for role, raw in variants:
            with self.subTest(role=role, raw=raw[:45]):
                with self._unit_stages():
                    report = self._reject(**{role + "_raw": raw, role + "_pin": blob(raw)})
                self.assertEqual(report["stageCallsAttempted"], [])
                self.assertEqual(self.stage_calls, [])

    def test_06_each_shared_proposal_field_must_match_before_stages(self):
        changes = [(("sourcePins", role), "a" * 40) for role in self.identity["sourcePins"]]
        changes.extend([
            (("sourceRef",), "refs/heads/codex/ap6-other-source"),
            (("runner", "repository"), "night-outlook/other-repository"),
            (("runner", "commit"), "b" * 40),
            (("runner", "ref"), "refs/heads/codex/ap6-other-runner"),
        ])
        changes.extend((("locations", field), str(self.parent / ("changed-" + field)))
                       for field in ("runnerRoot", "workspace", "evidenceParent"))
        changes.extend((("locations", "historicalRoots", role), str(self.parent / ("changed-" + role)))
                       for role in self.history)
        changes.extend((("authorization", field),
                        not value if type(value) is bool else "ChangedByUnitFixture")
                       for field, value in AP1.CLOSED_AUTHORITY.items())
        for path, value in changes:
            identity = copy.deepcopy(self.identity)
            target = identity
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            raw = canonical(identity)
            with self.subTest(field=".".join(path)):
                with self._unit_stages():
                    report = self._reject(identity_raw=raw, identity_pin=blob(raw))
                self.assertEqual(report["stageCallsAttempted"], [])
                self.assertEqual(self.stage_calls, [])
                self.assertIs(report["proposalFieldsMatched"], False)
                self.assertIsNone(report["matchedProposalProjection"])
                self.assertEqual(report["comparisonCallsAttempted"], [])

    def test_07_matching_arbitrary_sibling_pins_do_not_replace_the_ap1_tuple(self):
        self.assertEqual(AP1.SOURCE_PINS, {
            "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
            "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
            "il2cpp_plus": "1268dd417ffe9090fcd9ea2d49542c97ed3cccb3",
        })
        for role in AP1.SOURCE_PINS:
            closure, identity = copy.deepcopy(self.proposal), copy.deepcopy(self.identity)
            closure["sourcePins"][role] = identity["sourcePins"][role] = "a" * 40
            closure_raw, identity_raw = canonical(closure), canonical(identity)
            with self.subTest(role=role):
                with self._unit_stages():
                    report = self._reject(closure_raw, blob(closure_raw), identity_raw, blob(identity_raw))
                self.assertEqual(report["stageCallsAttempted"], [])
                self.assertEqual(self.stage_calls, [])

    def test_08_exact_schema_and_closed_authority_types_are_required(self):
        for change in ("boolean-schema", "numeric-authority", "both-numeric-authority", "extra-identity-field"):
            closure, identity = copy.deepcopy(self.proposal), copy.deepcopy(self.identity)
            if change == "boolean-schema":
                identity["schemaVersion"] = True
            elif change == "numeric-authority":
                identity["authorization"]["R03Accepted"] = 0
            elif change == "both-numeric-authority":
                closure["authorization"]["R03Accepted"] = 0
                identity["authorization"]["R03Accepted"] = 0
            else:
                identity["execute"] = False
            closure_raw, identity_raw = canonical(closure), canonical(identity)
            with self.subTest(change=change):
                with self._unit_stages():
                    report = self._reject(closure_raw, blob(closure_raw), identity_raw, blob(identity_raw))
                self.assertEqual(report["stageCallsAttempted"], [])
                self.assertEqual(self.stage_calls, [])

    def test_09_both_installed_helper_pins_are_checked_before_stages(self):
        helpers = {
            "d5b_five_identity.py": "ab4e9cbf796d4ab91602a14a9294d3773e75879c",
            "d5b_runner_configuration.py": "5263742017950a28bd9750eeeaefe50df4f4fa49",
        }
        for name, expected in helpers.items():
            self.assertEqual(blob((HERE / name).read_bytes()), expected)
        real_read = observer._read_absolute
        for helper_name in helpers:
            def changed_helper(path):
                raw = real_read(path)
                return raw + b"\n" if Path(path).name == helper_name else raw
            with self.subTest(helper=helper_name):
                with mock.patch.object(observer, "_read_absolute", side_effect=changed_helper):
                    with self._unit_stages():
                        report = self._reject()
                self.assertEqual(report["stageCallsAttempted"], [])
                self.assertEqual(self.stage_calls, [])

    def test_10_identity_rejection_preserves_child_progress_and_stops_configuration(self):
        def interrupted_identity(helper):
            progress = helper._progress()
            progress["localPassesAttempted"] = ["before"]
            progress["localPassesCompleted"] = ["before"]
            progress["remotePassesAttempted"] = ["before"]
            progress["remoteCallsAttempted"] = [{"pass": "before", "role": "hybridclr_demo"}]
            return helper.Rejected("AP6 unit identity-stage interruption", progress)
        with self._unit_stages(identity_failure=interrupted_identity) as captured:
            report = self._reject()
        self.assertEqual([item[0] for item in self.stage_calls], ["identity"])
        self.assertEqual(report["stageCallsAttempted"], ["identity"])
        self.assertEqual(report["stageCallsReturned"], [])
        self.assertEqual(report["stageCallsCompleted"], [])
        self.assertEqual(report["observations"]["identity"], captured["identity"])
        self.assertIsNone(report["observations"].get("configuration"))
        self.assertIs(report["sharedObservationsMatched"], False)
        self.assertEqual(report["comparisonCallsAttempted"], [])
        self.assertEqual(report["comparisonCallsCompleted"], [])

    def test_11_real_ap4_partial_consumption_survives_in_composition_rejection(self):
        with self._unit_stages(interrupt_profile=True) as captured:
            report = self._reject()
        self.assertEqual(report["stageCallsAttempted"], ["identity", "configuration"])
        self.assertEqual(report["stageCallsReturned"], ["identity"])
        self.assertEqual(report["stageCallsCompleted"], ["identity"])
        self.assertEqual(report["observations"], captured)
        child = report["observations"]["configuration"]
        self.assertEqual(child["configurationConsumerCallsAttempted"], ["d5b_local_admission.read_plan"])
        self.assertEqual(child["configurationConsumerCallsCompleted"], ["d5b_local_admission.read_plan"])
        self.assertEqual(child["importProgress"]["initializedModuleNames"], list(ap3_tests.MODULE_NAMES))
        self.assertIs(child["candidateTopLevelCodeMayHaveRun"], True)
        self.assertIs(child["candidateFunctionsInvoked"], True)
        self.assertIs(child["candidateEntryPointsInvoked"], False)
        self.assertIs(report["sharedObservationsMatched"], False)

    def test_12_generic_child_failure_does_not_fabricate_child_observation(self):
        for role in ("identity", "configuration"):
            self.stage_calls.clear()
            failure = {role + "_failure": lambda helper: RuntimeError("AP6 unit generic interruption")}
            with self.subTest(role=role):
                with self._unit_stages(**failure):
                    report = self._reject()
                attempted = ["identity"] if role == "identity" else ["identity", "configuration"]
                completed = [] if role == "identity" else ["identity"]
                self.assertEqual(report["stageCallsAttempted"], attempted)
                self.assertEqual(report["stageCallsReturned"], completed)
                self.assertEqual(report["stageCallsCompleted"], completed)
                self.assertIsNone(report["observations"].get(role))

    def test_13_every_common_runner_field_participates_in_the_stage_comparison(self):
        # Returned-report doubles isolate every comparison member; no disk drift is claimed.
        for field in CHECKOUT_FIELDS:
            self.stage_calls.clear()
            def drift(report):
                runner = report["checkoutObservations"]["after"]["runner"]
                value = runner[field]
                runner[field] = value + 1 if type(value) is int else value + ":AP6-drift"
            with self.subTest(field=field):
                with self._unit_stages(identity_transform=drift):
                    report = self._reject()
                self.assertEqual(report["stageCallsCompleted"], ["identity", "configuration"])
                self.assertIs(report["sharedObservationsMatched"], False)
                self.assertEqual(report["comparisonCallsAttempted"], ["runner"])
                self.assertEqual(report["comparisonCallsCompleted"], [])

    def test_14_location_drift_and_boolean_integer_aliases_reject(self):
        # Returned-report doubles exercise exact typed equality independently of Git.
        def location_drift(report):
            report["locationObservations"]["after"]["evidenceParent"]["inode"] += 1
        with self._unit_stages(identity_transform=location_drift):
            report = self._reject()
        self.assertEqual(report["stageCallsCompleted"], ["identity", "configuration"])
        self.assertIs(report["sharedObservationsMatched"], False)
        self.assertEqual(report["comparisonCallsAttempted"], ["runner", "locations"])
        self.assertEqual(report["comparisonCallsCompleted"], ["runner"])
        def integer_count(report):
            report["checkoutObservations"]["after"]["runner"]["worktreeFiles"] = 1
        def boolean_count(report):
            report["importObservation"]["artifactObservation"]["observedCheckout"]["worktreeFiles"] = True
        with self._unit_stages(identity_transform=integer_count, configuration_transform=boolean_count):
            report = self._reject()
        self.assertIs(report["sharedObservationsMatched"], False)
        self.assertEqual(report["comparisonCallsAttempted"], ["runner"])
        self.assertEqual(report["comparisonCallsCompleted"], [])

    def test_15_comparison_uses_ap5_final_and_ap4_preinitialization_observations(self):
        def distinguish_earlier_pass(report):
            report["checkoutObservations"]["before"]["runner"] = {"head": "earlier-unit-double"}
            report["locationObservations"]["before"] = {"unitDoubleEarlierPass": True}
        with self._unit_stages(identity_transform=distinguish_earlier_pass):
            report = self._observe().report
        self.assertIs(report["sharedObservationsMatched"], True)
        imported = report["observations"]["configuration"]["importObservation"]
        self.assertEqual(imported["artifactObservationScope"], "AP2BeforeCandidateModuleInitializationOnly")
        self.assertEqual(report["comparisonScope"], "AP5AfterObservation_VersusAP2BeforeCandidateInitializationOnly")
        self.assertIs(report["checkoutRecheckedAfterConfigurationConsumers"], False)
        self.assertIs(report["observations"]["configuration"]["checkoutRecheckedAfterModuleInitialization"], False)
        self._closed(report)

    def test_16_success_and_rejection_reports_are_fresh_detached_json(self):
        with self._unit_stages() as captured:
            result = self._observe()
        original = result.report
        returned = result.report
        returned["observations"]["configuration"]["configurationValues"].clear()
        returned["authorization"] = {"allowPlayerLaunch": True}
        captured["identity"]["runner"].clear()
        self.assertEqual(result.report, original)
        self.assertIsNot(result.report, result.report)
        with self.assertRaises(FrozenInstanceError):
            result._report_json = b"{}"
        with self._unit_stages(identity_failure=lambda helper: helper.Rejected("unit denial", helper._progress())):
            with self.assertRaises(observer.Rejected) as caught:
                self._observe()
        original_denial = caught.exception.report
        denial_copy = caught.exception.report
        denial_copy["observations"]["identity"]["remoteCallsAttempted"].append({"role": "invented"})
        self.assertEqual(caught.exception.report, original_denial)
        self.assertIsNot(caught.exception.report, caught.exception.report)

    def test_17_private_helpers_and_ambient_candidate_slots_are_restored(self):
        original_path = sys.path
        path_contents = tuple(sys.path)
        before = self._registry()
        absent = object()
        previous = {name: sys.modules.get(name, absent) for name in ap3_tests.MODULE_NAMES}
        sentinels = {name: ModuleType(name) for name in ap3_tests.MODULE_NAMES}
        sys.modules.update(sentinels)
        try:
            with self._unit_stages():
                self._closed(self._observe().report)
            with self._unit_stages(interrupt_profile=True):
                self._reject()
            self.assertEqual(self._registry(), before)
            self.assertIs(sys.path, original_path)
            self.assertEqual(tuple(sys.path), path_contents)
            for name, sentinel in sentinels.items():
                self.assertIs(sys.modules.get(name), sentinel)
        finally:
            for name, value in previous.items():
                if value is absent:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value

    def test_18_real_cli_pre_stage_denials_do_not_claim_observation(self):
        closure_path, identity_path = self.parent / "closure.json", self.parent / "identity.json"
        closure_path.write_bytes(self.raw)
        identity_path.write_bytes(self.identity_raw)
        base = ["--closure", str(closure_path), "--expected-closure-blob", self.pin,
                "--identity-proposal", str(identity_path), "--expected-identity-blob", self.identity_pin]
        environment = {key: value for key, value in self.git_environment.items()
                       if not key.startswith("PYTHON")}
        for case in ("bad-pin", "missing-isolation", "relative-path", "execution-option"):
            arguments, flags = list(base), ["-I", "-S", "-B"]
            if case == "bad-pin":
                arguments[arguments.index("--expected-identity-blob") + 1] = "0" * 40
            elif case == "missing-isolation":
                flags = ["-I", "-B"]
            elif case == "relative-path":
                arguments[arguments.index("--closure") + 1] = "closure.json"
            else:
                arguments.append("--execute")
            with self.subTest(case=case):
                completed = subprocess.run(
                    [sys.executable, *flags, str(Path(observer.__file__).resolve()), *arguments],
                    capture_output=True, env=environment, cwd=self.parent, timeout=60, check=False)
                self.assertEqual(completed.returncode, 2, completed.stderr.decode(errors="replace"))
                if case == "execution-option":
                    self.assertIn(b"unrecognized arguments", completed.stderr)
                    self.assertEqual(completed.stdout, b"")
                else:
                    report = json.loads(completed.stdout)
                    self.assertEqual(report["result"], observer.REJECTED_RESULT)
                    self.assertEqual(report["stageCallsAttempted"], [])
                    self.assertEqual(report["stageCallsCompleted"], [])
                    self._closed(report)

    def test_19_real_runner_directory_change_between_stages_rejects_comparison(self):
        original_mode = self.repo.stat().st_mode & 0o777
        changed_mode = original_mode ^ 0o010
        try:
            with self._unit_stages(before_configuration=lambda: self.repo.chmod(changed_mode)) as captured:
                report = self._reject()
            self.assertEqual(self.repo.stat().st_mode & 0o777, changed_mode)
            self.assertEqual(report["stageCallsCompleted"], ["identity", "configuration"])
            before = captured["identity"]["checkoutObservations"]["after"]["runner"]
            after = captured["configuration"]["importObservation"]["artifactObservation"]["observedCheckout"]
            self.assertNotEqual(before["worktreeInventorySha256"], after["worktreeInventorySha256"])
            self.assertIs(report["sharedObservationsMatched"], False)
            self.assertEqual(report["comparisonCallsAttempted"], ["runner"])
            self.assertEqual(report["comparisonCallsCompleted"], [])
        finally:
            self.repo.chmod(original_mode)

    def test_20_real_path_change_after_capture_preserves_bounded_consumer_semantics(self):
        plan_path = ap3_tests.ap2_tests.PLAN_PATH
        pathname = self.repo / plan_path
        original = pathname.read_bytes()
        changed = b'{"ap6FixtureChangedPath": true}\n'
        captures = []
        def change_after_capture(context, progress):
            self.assertEqual(context.files[plan_path].raw, original)
            captures.append(context.files[plan_path].raw)
            pathname.write_bytes(changed)
        try:
            with self._unit_stages(before_consumption=change_after_capture):
                report = self._observe().report
            self.assertEqual(captures, [original])
            self.assertEqual(pathname.read_bytes(), changed)
            self.assertEqual(report["result"], observer.SUCCESS_RESULT)
            self.assertIs(report["sharedObservationsMatched"], True)
            configuration = report["observations"]["configuration"]
            self.assertEqual(configuration["configurationValues"]["plan"], json.loads(original))
            self.assertEqual(configuration["configurationConsumerCallsCompleted"], [
                "d5b_local_admission.read_plan", "d5b_rr5_source_preflight.checked_profile",
            ])
            self.assertIs(configuration["configurationPathnamesReopenedDuringConsumption"], False)
            self.assertIs(report["checkoutRecheckedAfterConfigurationConsumers"], False)
            self.assertIs(report["identityObservationRemainsCurrentDuringConfiguration"], False)
            self._closed(report)
        finally:
            pathname.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
