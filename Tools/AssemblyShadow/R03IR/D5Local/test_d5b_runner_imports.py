#!/usr/bin/env python3
"""AP3 reviewed-source import tests; no candidate function is invoked.

Run with trusted Python -I -S -B. The explicit path insertion below is test
harness setup for importing the reviewed observer and AP2 fixture helpers;
it is not the routing mechanism for candidate imports. Private snapshot
seams are tested as internal consistency checks, never as a public source
of provenance or authorization. No alternate candidate code is executed.
"""
from __future__ import annotations

import _io
import builtins
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
import copy
from dataclasses import FrozenInstanceError, fields
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import unittest
from unittest import mock


TRUSTED_TEST_DIRECTORY = Path(__file__).resolve(strict=True).parent
sys.path.insert(0, str(TRUSTED_TEST_DIRECTORY))
import d5b_runner_imports as observer
import test_d5b_runner_closure as ap2_tests


MODULE_NAMES = ("d5b_rr5_source_preflight", "d5b_local_admission", "run_d5_local")
WRAPPER_PATH = ap2_tests.WRAPPER_PATH
WRITER_PATH = ap2_tests.WRITER_PATH
PREFLIGHT_PATH = ap2_tests.PREFLIGHT_PATH
MODULE_PATHS = (PREFLIGHT_PATH, WRITER_PATH, WRAPPER_PATH)


class _AP2FixtureAdapter(unittest.TestCase):
    """Reuse fixture construction without inheriting any of AP2's 25 tests."""

    _git = ap2_tests.D5BRunnerClosureSourceOnly._git
    _git_blob = ap2_tests.D5BRunnerClosureSourceOnly._git_blob
    _blob = ap2_tests.D5BRunnerClosureSourceOnly._blob
    _tree = ap2_tests.D5BRunnerClosureSourceOnly._tree
    _commit = ap2_tests.D5BRunnerClosureSourceOnly._commit
    _chain = ap2_tests.D5BRunnerClosureSourceOnly._chain
    _checkout = ap2_tests.D5BRunnerClosureSourceOnly._checkout
    _make_proposal = ap2_tests.D5BRunnerClosureSourceOnly._make_proposal

    def setUp(self):
        self.assertTrue(sys.flags.isolated, "Run this suite with Python -I -S -B")
        self.assertTrue(sys.flags.no_site, "Run this suite with Python -I -S -B")
        self.assertTrue(sys.dont_write_bytecode, "Run this suite with Python -I -S -B")
        ap2_tests.D5BRunnerClosureSourceOnly.setUp(self)


class D5BRunnerImportsSourceOnly(_AP2FixtureAdapter):
    def _observe(self):
        return observer.observe_runner_imports(self.raw, self.pin)

    def _snapshot(self):
        # These are real AP2-verified records; the private seam is not an API
        # by which a caller may claim that arbitrary records were reviewed.
        return observer._verified_snapshot(self.raw, self.pin)

    def _assert_closed(self, report):
        self.assertEqual(report["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")
        for field in ("D5BLocalExecution", "D5LocalValidation", "explicitUserLocalApproval"):
            self.assertEqual(report[field], "NotAuthorized", field)
        for field in (
            "candidateEntryPointsInvoked", "admissionPreviewInvoked",
            "candidateFunctionsInvoked", "planProfileFunctionsInvoked",
            "candidateModulesInstalledInSysModules", "ambientCandidateImportLookupUsed",
            "candidateBytecodeLoaded", "candidateBytecodeWritten",
            "runtimeImportIsolationVerified", "runtimeConfigurationReadsBound",
            "runnerExecutableClosureVerified", "standardLibraryIdentityVerified",
            "pythonSandboxProvided", "checkoutRecheckedAfterModuleInitialization",
            "exclusiveCustodyVerified", "liveRemoteRefsVerified",
            "sourceDataInputsVerified", "currentMacInputsVerified",
            "executionAuthorityVerified", "R03Accepted", "H2Passed",
            "ReadyForHumanReviewGate", "allowNativeBuild", "allowPlayerLaunch",
            "UnityOrPlayerExecuted", "outputCreated", "networkUsed",
        ):
            self.assertIs(report[field], False, field)
        self.assertIs(report["trustedProcessRequired"], True)
        self.assertIsNone(report["approvedEnvelopeGitBlob"])
        self.assertEqual(report["independentlyReviewedImportBootstrap"], "Pending")
        self.assertEqual(report["independentlyReviewedExecutableAdmission"], "Pending")
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)

    def _assert_json_only(self, value):
        if type(value) is dict:
            for key, child in value.items():
                self.assertIs(type(key), str)
                self._assert_json_only(child)
        elif type(value) is list:
            for child in value:
                self._assert_json_only(child)
        else:
            self.assertIn(type(value), (str, int, float, bool, type(None)))

    def _assert_no_candidate_progress(self, report):
        self.assertEqual(report["initializationAttempted"], [])
        self.assertEqual(report["initializedModuleNames"], [])
        self.assertIs(report["candidateTopLevelCodeMayHaveRun"], False)
        self.assertIs(report["candidateWriterImported"], False)
        self.assertIs(report["fixedModuleImportSelectionVerified"], False)
        self._assert_closed(report)

    def _assert_protected_empty(self):
        self.assertEqual(list(self.evidence.iterdir()), [])
        for role in ap2_tests.closure.SOURCE_ROLES:
            self.assertEqual(list((self.workspace / role).iterdir()), [])
        for role, path in self.history.items():
            if role != "b1EvidenceBase":
                self.assertEqual(list(path.iterdir()), [])

    @contextmanager
    def _candidate_cache_entries(self, entries):
        absent = object()
        previous = {name: sys.modules.get(name, absent) for name in entries}
        sys.modules.update(entries)
        try:
            yield
        finally:
            for name, value in previous.items():
                if value is absent:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value

    def _cli(self, *, flags=("-I", "-S", "-B"), extra=(), expected_blob=None,
             omit_closure=False, omit_pin=False, environment=None, cwd=None):
        path = self.parent / "ap3-closure-proposal.json"
        path.write_bytes(self.raw)
        arguments = [sys.executable, *flags, str(Path(observer.__file__).resolve())]
        if not omit_closure:
            arguments.extend(("--closure", str(path)))
        if not omit_pin:
            arguments.extend(("--expected-closure-blob",
                              self.pin if expected_blob is None else expected_blob))
        arguments.extend(extra)
        # Negative flag cases must not activate unrelated ambient Python setup.
        environment_values = {key: value for key, value in self.git_environment.items()
                              if not key.startswith("PYTHON")}
        environment_values.update({} if environment is None else environment)
        return subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=environment_values, cwd=cwd, check=False, timeout=60)

    def test_01_real_ap2_snapshot_initializes_three_private_bindings(self):
        filenames = {str(self.repo / path): name
                     for name, path in zip(MODULE_NAMES, MODULE_PATHS)}
        namespaces, cache_observations = {}, []
        previous_profile = sys.getprofile()

        def observe_module_returns(frame, event, arg):
            name = filenames.get(frame.f_code.co_filename)
            if name is not None and frame.f_code.co_name == "<module>" and event == "return":
                namespaces[name] = frame.f_globals
                cache_observations.append({item: sys.modules.get(item) for item in MODULE_NAMES})

        before = {name: sys.modules.get(name) for name in MODULE_NAMES}
        try:
            sys.setprofile(observe_module_returns)
            result = self._observe()
        finally:
            sys.setprofile(previous_profile)
        report = result.report
        self.assertEqual(set(namespaces), set(MODULE_NAMES))
        preflight, writer, wrapper = (namespaces[name] for name in MODULE_NAMES)
        self.assertIs(writer["source"].__dict__, preflight)
        self.assertIs(wrapper["main"], writer["main"])
        self.assertIs(writer["main"].__globals__, writer)
        for name, namespace in namespaces.items():
            self.assertEqual(namespace["__name__"], name)
            self.assertNotEqual(namespace["__name__"], "__main__")
            self.assertIsNone(namespace["__cached__"])
            self.assertIsNone(namespace["__loader__"])
            self.assertIsNone(namespace["__spec__"])
        self.assertTrue(cache_observations)
        for observed_cache in cache_observations:
            self.assertEqual(observed_cache, before)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertEqual(report["initializedModuleNames"], list(MODULE_NAMES))
        self.assertEqual(report["compiledModuleNames"], list(MODULE_NAMES))
        self.assertEqual(report["initializationAttempted"], list(MODULE_NAMES))
        self.assertEqual(report["verifiedArtifactCount"], 6)
        self.assertIs(report["candidateTopLevelCodeMayHaveRun"], True)
        self.assertIs(report["candidateWriterImported"], True)
        self.assertIs(report["fixedModuleImportSelectionVerified"], True)
        self.assertEqual(report["closureProposalGitBlob"], self.pin)
        self.assertEqual(report["candidateLiteralProposalBlob"],
                         self.proposal["proposalEnvelopeGitBlob"])
        self.assertEqual(report["projectBindings"], {
            "writer.source": "d5b_rr5_source_preflight",
            "wrapper.main": "d5b_local_admission.main",
        })
        self.assertEqual(report["interpreterFlags"], {
            "isolated": True, "noSite": True, "noBytecodeWrites": True,
        })
        self.assertEqual([item["path"] for item in report["dataArtifacts"]],
                         [ap2_tests.PLAN_PATH, ap2_tests.PROFILE_PATH, ap2_tests.ENVELOPE_PATH])
        for item, path in zip(report["moduleSources"], MODULE_PATHS):
            raw = self._git("cat-file", "blob", self.runner_commit + ":" + path)
            self.assertEqual(item["gitBlob"], self._git_blob(raw))
            self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(item["bytes"], len(raw))
            self.assertEqual(item["compilationFilename"], str(self.repo / path))
        ap2_tests.D5BRunnerClosureSourceOnly._assert_closed(self, report["artifactObservation"])
        self._assert_closed(report)

    def test_02_report_matches_actual_ordered_direct_import_requests(self):
        expected_imports = {
            MODULE_NAMES[0]: [("__future__", ("annotations",)), ("argparse", ()),
                             ("hashlib", ()), ("json", ()), ("pathlib", ("Path",)),
                             ("re", ()), ("subprocess", ()), ("sys", ())],
            MODULE_NAMES[1]: [("__future__", ("annotations",)), ("argparse", ()),
                             ("hashlib", ()), ("json", ()), ("os", ()),
                             ("pathlib", ("Path",)), ("platform", ()), ("re", ()),
                             ("shutil", ()), ("stat", ()), ("subprocess", ()),
                             ("sys", ()), ("typing", ("Mapping",)),
                             (MODULE_NAMES[0], ())],
            MODULE_NAMES[2]: [(MODULE_NAMES[1], ("main",))],
        }
        actual = []
        make_importer = observer._private_importer

        def observed_importer(requester, modules, sys_view, trace):
            selected_importer = make_importer(requester, modules, sys_view, trace)

            def record(name, globals=None, locals=None, fromlist=(), level=0):
                actual.append((requester, name, tuple(fromlist or ()), level))
                return selected_importer(name, globals, locals, fromlist, level)
            return record

        with mock.patch.object(observer, "_private_importer", side_effect=observed_importer):
            report = self._observe().report
        expected = [(requester, name, fromlist, 0)
                    for requester in MODULE_NAMES
                    for name, fromlist in expected_imports[requester]]
        self.assertEqual(len(expected), 23)
        self.assertEqual(actual, expected)
        self.assertEqual(
            [(item["requester"], item["name"], tuple(item["fromlist"]), item["level"])
             for item in report["importTrace"]], actual)
        for item in report["importTrace"]:
            expected_origin = ("PrivatePathOnlySysView" if item["name"] == "sys" else
                               "VerifiedSnapshotSource" if item["name"] in MODULE_NAMES else
                               "TrustedPreloadedStandardLibrary")
            self.assertEqual(item["origin"], expected_origin)

    def test_03_ambient_candidate_module_cache_entries_are_never_selected(self):
        substitutes = {name: ModuleType(name) for name in MODULE_NAMES}
        for name, module in substitutes.items():
            module.fixture_label = "inert ambient " + name
        with self._candidate_cache_entries(substitutes):
            report = self._observe().report
            for name, module in substitutes.items():
                self.assertIs(sys.modules[name], module)
                self.assertEqual(vars(module), {
                    "__name__": name, "__doc__": None, "__package__": None,
                    "__loader__": None, "__spec__": None,
                    "fixture_label": "inert ambient " + name,
                })
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertIs(report["ambientCandidateModuleCacheUnchanged"], True)
        self.assertIs(report["candidateModulesInstalledInSysModules"], False)

    def test_04_ambient_meta_path_and_path_cache_are_not_consulted(self):
        ambient = self.parent / "ambient-import-path"
        ambient.mkdir()
        calls = []

        class CandidateFinderObserver:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split(".", 1)[0] in MODULE_NAMES:
                    calls.append(fullname)
                    raise AssertionError("Ambient candidate finder consulted")
                return None

        finder = CandidateFinderObserver()
        path_before = list(sys.path)
        try:
            sys.path.insert(0, str(ambient))
            with mock.patch.object(sys, "meta_path", [finder, *sys.meta_path]), \
                    mock.patch.dict(sys.path_importer_cache, {str(ambient): finder}):
                report = self._observe().report
                self.assertIs(sys.path_importer_cache[str(ambient)], finder)
        finally:
            sys.path[:] = path_before
        self.assertEqual(calls, [])
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertIs(report["ambientCandidateImportLookupUsed"], False)

    def test_05_ambient_source_and_opaque_bytecode_fixtures_are_not_read(self):
        ambient = self.parent / "ambient-source-and-bytecode"
        ambient.mkdir()
        cache = ambient / "__pycache__"
        cache.mkdir()
        fixture_paths = []
        for name in MODULE_NAMES:
            source_path = ambient / (name + ".py")
            source_path.write_bytes(b"# Inert ambient source fixture; must never be selected.\n")
            fixture_paths.append(source_path)
            for bytecode_path in (ambient / (name + ".pyc"),
                                  cache / (name + "." + sys.implementation.cache_tag + ".pyc")):
                bytecode_path.write_bytes(b"Opaque non-executable bytecode-selection fixture.\n")
                fixture_paths.append(bytecode_path)
        before = {path: path.read_bytes() for path in fixture_paths}
        original_initialize = observer._initialize_snapshot
        attempts = []

        def guarded_initialize(*args):
            def reject_content_open(*arguments, **kwargs):
                attempts.append(repr(arguments[:1]))
                raise AssertionError("Import phase attempted a content open")
            with ExitStack() as stack:
                for owner, attribute in ((builtins, "open"), (io, "open"), (_io, "open"),
                                         (_io, "open_code"), (os, "open")):
                    stack.enter_context(mock.patch.object(owner, attribute,
                                                          side_effect=reject_content_open))
                return original_initialize(*args)

        path_before = list(sys.path)
        try:
            sys.path.insert(0, str(ambient))
            with mock.patch.object(observer, "_initialize_snapshot", side_effect=guarded_initialize):
                report = self._observe().report
        finally:
            sys.path[:] = path_before
        self.assertEqual(attempts, [])
        self.assertEqual({path: path.read_bytes() for path in fixture_paths}, before)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertIs(report["candidateBytecodeLoaded"], False)
        self.assertIs(report["candidateBytecodeWritten"], False)

    def test_06_real_sys_path_is_unchanged_during_writer_initialization(self):
        original_initialize = observer._initialize_snapshot
        real_path, path_before = sys.path, tuple(sys.path)
        writer_filename = str(self.repo / WRITER_PATH)
        observed_private_paths = []
        visited_lines = []

        def guarded_initialize(*args):
            previous_trace = sys.gettrace()

            def trace(frame, event, arg):
                if frame.f_code.co_filename == writer_filename:
                    self.assertIs(sys.path, real_path)
                    self.assertEqual(tuple(sys.path), path_before)
                    if event == "line":
                        visited_lines.append(frame.f_lineno)
                        if "sys" in frame.f_globals:
                            private = frame.f_globals["sys"]
                            self.assertIsNot(private, sys)
                            self.assertIsNot(private.path, real_path)
                            observed_private_paths.append(tuple(private.path))
                return trace

            try:
                sys.settrace(trace)
                return original_initialize(*args)
            finally:
                sys.settrace(previous_trace)

        with mock.patch.object(observer, "_initialize_snapshot", side_effect=guarded_initialize):
            report = self._observe().report
        expected_path = str(self.repo / "Tools/AssemblyShadow/R03IR/D5Admission")
        self.assertTrue(visited_lines)
        self.assertIn((), observed_private_paths)
        self.assertIn((expected_path,), observed_private_paths)
        self.assertEqual(report["privateSysPath"], [expected_path])
        self.assertIs(sys.path, real_path)
        self.assertEqual(tuple(sys.path), path_before)
        self.assertIs(report["realSysPathUnchanged"], True)

    def test_07_import_phase_calls_no_candidate_function_or_content_reader(self):
        allowed_code_names = {
            str(self.repo / PREFLIGHT_PATH): {"<module>", "Rejected"},
            str(self.repo / WRITER_PATH): {"<module>", "Rejected", "PathIdentityMismatch",
                                         "CreationFailure", "PartialOutput"},
            str(self.repo / WRAPPER_PATH): {"<module>"},
        }
        original_initialize = observer._initialize_snapshot
        code_events, blocked_attempts = [], []

        def guarded_initialize(*args):
            previous_profile = sys.getprofile()

            def profile(frame, event, arg):
                if event == "call" and frame.f_code.co_filename in allowed_code_names:
                    code_events.append((frame.f_code.co_filename, frame.f_code.co_name))
                    self.assertIn(frame.f_code.co_name,
                                  allowed_code_names[frame.f_code.co_filename],
                                  "Candidate function was invoked")

            def deny_operation(*arguments, **kwargs):
                blocked_attempts.append(repr(arguments[:1]))
                raise AssertionError("Candidate initialization attempted content or process I/O")

            stdout, stderr = io.StringIO(), io.StringIO()
            with ExitStack() as stack:
                for owner, attribute in ((builtins, "open"), (io, "open"), (_io, "open"),
                                         (_io, "open_code"), (os, "open"), (os, "system"),
                                         (subprocess, "run"), (subprocess, "Popen")):
                    stack.enter_context(mock.patch.object(owner, attribute, side_effect=deny_operation))
                stack.enter_context(redirect_stdout(stdout))
                stack.enter_context(redirect_stderr(stderr))
                try:
                    sys.setprofile(profile)
                    observed = original_initialize(*args)
                finally:
                    sys.setprofile(previous_profile)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            return observed

        with mock.patch.object(observer, "_initialize_snapshot", side_effect=guarded_initialize):
            report = self._observe().report
        self.assertEqual({path for path, name in code_events}, set(allowed_code_names))
        self.assertEqual(blocked_attempts, [])
        self._assert_closed(report)
        self._assert_protected_empty()

    def test_08_after_snapshot_source_change_does_not_replace_captured_bytes(self):
        verified_snapshot = observer._verified_snapshot
        source_path = self.repo / WRITER_PATH
        before = source_path.read_bytes()
        compiled_candidate_bytes = {}
        original_compile = builtins.compile

        def capture_then_change(raw, pin):
            snapshot = verified_snapshot(raw, pin)
            source_path.write_bytes(before + b"\n# Harmless after-snapshot source change.\n")
            return snapshot

        def observe_compile(source, filename, *args, **kwargs):
            if filename in {str(self.repo / path) for path in MODULE_PATHS}:
                compiled_candidate_bytes[filename] = source
            return original_compile(source, filename, *args, **kwargs)

        with mock.patch.object(observer, "_verified_snapshot", side_effect=capture_then_change), \
                mock.patch.object(observer, "compile", side_effect=observe_compile, create=True):
            report = self._observe().report
        self.assertEqual(compiled_candidate_bytes[str(source_path)], before)
        self.assertNotEqual(source_path.read_bytes(), before)
        self.assertEqual(len(compiled_candidate_bytes), 3)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertEqual(report["artifactObservationScope"],
                         "AP2BeforeCandidateModuleInitializationOnly")
        self.assertIs(report["checkoutRecheckedAfterModuleInitialization"], False)
        self._assert_closed(report)

    def test_09_invalid_external_pin_or_raw_input_rejects_before_helper(self):
        oversized = b" " * (observer.MAX_BYTES + 1)
        for label, raw, pin in (
            ("wrong-pin", self.raw, "0" * 40),
            ("changed-bytes", self.raw + b"\n", self.pin),
            ("text", self.raw.decode(), self.pin),
            ("mutable-bytes", bytearray(self.raw), self.pin),
            ("malformed-pin", self.raw, "G" * 40),
            ("non-string-pin", self.raw, 7),
            ("oversized", oversized, self._git_blob(oversized)),
        ):
            with self.subTest(change=label), \
                    mock.patch.object(observer, "_verified_snapshot") as snapshot, \
                    mock.patch.object(observer, "_initialize_snapshot") as initialize:
                with self.assertRaises(observer.Rejected) as caught:
                    observer.observe_runner_imports(raw, pin)
                snapshot.assert_not_called()
                initialize.assert_not_called()
                self._assert_no_candidate_progress(caught.exception.report)

    def test_10_changed_trusted_helper_bytes_reject_before_compilation(self):
        helper_path = Path(observer.__file__).resolve().with_name(observer.AP2_HELPER_NAME)
        read_absolute = observer._read_absolute
        reads = []

        def changed_helper(path):
            reads.append(path)
            raw = read_absolute(path)
            return raw + b"\n# Harmless helper-byte mismatch fixture.\n"

        with mock.patch.object(observer, "_read_absolute", side_effect=changed_helper), \
                mock.patch.object(observer, "compile", create=True) as compiler, \
                mock.patch.object(observer, "_initialize_snapshot") as initialize:
            with self.assertRaises(observer.Rejected) as caught:
                self._observe()
        self.assertEqual(reads, [helper_path])
        compiler.assert_not_called()
        initialize.assert_not_called()
        self.assertIn("AP2 verifier differs", str(caught.exception))
        self._assert_no_candidate_progress(caught.exception.report)

    def test_11_malformed_private_snapshot_records_reject_before_compilation(self):
        closure, records, artifact_report = self._snapshot()
        first = records[0]
        variants = {
            "mutable-container": list(records),
            "missing": records[:-1],
            "duplicate": (records[1], *records[1:]),
            "unexpected": (first._replace(path="Unexpected.py"), *records[1:]),
            "non-string-path": (first._replace(path=1), *records[1:]),
            "plain-tuple-record": (tuple(first), *records[1:]),
            "mutable-content": (first._replace(raw=bytearray(first.raw)), *records[1:]),
            "changed-bytes": (first._replace(raw=first.raw + b"\n"), *records[1:]),
            "changed-blob": (first._replace(git_blob="0" * 40), *records[1:]),
            "malformed-blob": (first._replace(git_blob="x" * 40), *records[1:]),
            "oversized": (first._replace(raw=b" " * (observer.MAX_BYTES + 1)), *records[1:]),
        }
        for label, candidate_records in variants.items():
            with self.subTest(change=label), \
                    mock.patch.object(observer, "compile", create=True) as compiler:
                progress = observer._progress()
                with self.assertRaises(observer._Problem):
                    observer._initialize_snapshot(closure, candidate_records, artifact_report, progress)
                compiler.assert_not_called()
                self.assertEqual(progress["initializationAttempted"], [])
                self.assertEqual(progress["verifiedArtifactCount"], 0)

    def test_12_private_snapshot_requires_consistent_roster_and_closed_ap2_report(self):
        closure, records, artifact_report = self._snapshot()
        variants = []
        missing_roster = copy.deepcopy(closure)
        del missing_roster["files"][ap2_tests.PLAN_PATH]
        variants.append(("missing-roster", missing_roster, artifact_report))
        wrong_mode = copy.deepcopy(closure)
        wrong_mode["files"][ap2_tests.PLAN_PATH]["mode"] = 100644
        variants.append(("wrong-mode-type", wrong_mode, artifact_report))
        wrong_blob = copy.deepcopy(closure)
        wrong_blob["files"][ap2_tests.PROFILE_PATH]["gitBlob"] = "0" * 40
        variants.append(("wrong-closure-blob", wrong_blob, artifact_report))
        for field, value in (("result", "Unverified"),
                             ("runnerArtifactClosureVerified", False),
                             ("runnerCheckoutObservationVerified", False),
                             ("candidateWriterExecutedOrImported", True),
                             ("executionAuthorityVerified", True)):
            changed = copy.deepcopy(artifact_report)
            changed[field] = value
            variants.append((field, closure, changed))
        for label, candidate_closure, candidate_report in variants:
            with self.subTest(change=label), \
                    mock.patch.object(observer, "compile", create=True) as compiler:
                progress = observer._progress()
                with self.assertRaises(observer._Problem):
                    observer._initialize_snapshot(candidate_closure, records, candidate_report, progress)
                compiler.assert_not_called()
                self.assertEqual(progress["initializationAttempted"], [])

    def test_13_import_requests_outside_reviewed_direct_forms_are_denied(self):
        private_sys = ModuleType("sys")
        private_sys.path = []
        importer = observer._private_importer(MODULE_NAMES[1], {}, private_sys, [])
        for name, fromlist, level in (
            ("unlisted_fixture_module", (), 0),
            ("pathlib.extra", (), 0),
            ("pathlib", (), 0),
            ("pathlib", ("*",), 0),
            ("pathlib", ("Path", "PurePath"), 0),
            ("pathlib", "Path", 0),
            ("pathlib", ("Path",), 1),
            ("pathlib", ("Path",), False),
            (MODULE_NAMES[0], ("main",), 0),
            (MODULE_NAMES[2], (), 0),
        ):
            with self.subTest(name=name, fromlist=fromlist, level=level):
                with self.assertRaises(observer._Problem):
                    importer(name, fromlist=fromlist, level=level)
        missing_dependency = observer._private_importer(MODULE_NAMES[2], {}, private_sys, [])
        with self.assertRaisesRegex(observer._Problem, "not initialized in order"):
            missing_dependency(MODULE_NAMES[1], fromlist=("main",))

    def test_14_public_result_is_frozen_json_data_with_fresh_report_copies(self):
        result = self._observe()
        self.assertIs(type(result), observer.ImportObservation)
        self.assertEqual([item.name for item in fields(result)], ["_report_json"])
        self.assertEqual(set(vars(result)), {"_report_json"})
        self.assertIs(type(result._report_json), bytes)
        with self.assertRaises(FrozenInstanceError):
            result._report_json = b"{}"
        report = result.report
        self._assert_json_only(report)
        report["executionAuthorityVerified"] = True
        report["projectBindings"]["wrapper.main"] = "changed presentation copy"
        report["initializedModuleNames"].clear()
        report["artifactObservation"]["authorization"] = "changed presentation copy"
        self._assert_closed(result.report)
        self.assertEqual(result.report["initializedModuleNames"], list(MODULE_NAMES))
        self.assertEqual(result.report["projectBindings"]["wrapper.main"],
                         "d5b_local_admission.main")
        self.assertNotIn("authorization", result.report["artifactObservation"])
        signature = inspect.signature(observer.observe_runner_imports)
        self.assertEqual(list(signature.parameters), ["raw", "expected_closure_blob"])
        with self.assertRaises(TypeError):
            observer.observe_runner_imports(self.raw, self.pin, bundle=object())

    def test_15_rejections_report_partial_initialization_truthfully(self):
        make_importer = observer._private_importer
        for requester, import_name, initialized, writer_imported in (
            (MODULE_NAMES[0], "argparse", [], False),
            (MODULE_NAMES[1], MODULE_NAMES[0], [MODULE_NAMES[0]], False),
            (MODULE_NAMES[2], MODULE_NAMES[1], list(MODULE_NAMES[:2]), True),
        ):
            with self.subTest(interrupted_module=requester):
                def interrupted_importer(name, modules, private_sys, trace):
                    direct_importer = make_importer(name, modules, private_sys, trace)

                    def invoke(dependency, globals=None, locals=None, fromlist=(), level=0):
                        if name == requester and dependency == import_name:
                            raise RuntimeError("Benign import-observation interruption")
                        return direct_importer(dependency, globals, locals, fromlist, level)
                    return invoke

                with mock.patch.object(observer, "_private_importer", side_effect=interrupted_importer):
                    with self.assertRaises(observer.Rejected) as caught:
                        self._observe()
                report = caught.exception.report
                self.assertEqual(report["result"], observer.REJECTED_RESULT)
                self.assertEqual(report["verifiedArtifactCount"], 6)
                self.assertEqual(report["compiledModuleNames"], list(MODULE_NAMES))
                self.assertEqual(report["initializedModuleNames"], initialized)
                self.assertEqual(report["initializationAttempted"],
                                 list(MODULE_NAMES[:MODULE_NAMES.index(requester) + 1]))
                self.assertIs(report["candidateTopLevelCodeMayHaveRun"], True)
                self.assertIs(report["candidateWriterImported"], writer_imported)
                self.assertIs(report["fixedModuleImportSelectionVerified"], False)
                self.assertIs(report["realSysPathUnchanged"], True)
                self.assertIs(report["ambientCandidateModuleCacheUnchanged"], True)
                self._assert_closed(report)
                self._assert_json_only(report)
                report["initializationAttempted"].clear()
                self.assertTrue(caught.exception.report["initializationAttempted"])
                self._assert_protected_empty()

    def test_16_compilation_interruption_reports_no_candidate_initialization(self):
        original_compile = builtins.compile

        def interrupt_first_candidate(source, filename, *args, **kwargs):
            if filename == str(self.repo / PREFLIGHT_PATH):
                raise RuntimeError("Benign pre-initialization compiler interruption")
            return original_compile(source, filename, *args, **kwargs)

        with mock.patch.object(observer, "compile", side_effect=interrupt_first_candidate, create=True):
            with self.assertRaises(observer.Rejected) as caught:
                self._observe()
        report = caught.exception.report
        self.assertEqual(report["verifiedArtifactCount"], 6)
        self.assertEqual(report["compiledModuleNames"], [])
        self._assert_no_candidate_progress(report)
        self._assert_protected_empty()

    def test_17_temporary_trusted_helper_registration_is_always_removed(self):
        helper_path = str(Path(observer.__file__).resolve().with_name(observer.AP2_HELPER_NAME))
        original_compile = builtins.compile
        prefix = "_ap3_verified_ap2_"
        before = {name: module for name, module in sys.modules.items() if name.startswith(prefix)}
        registrations = []
        invalid_closure = copy.deepcopy(self.proposal)
        invalid_closure["scope"] = "Invalid benign fixture scope"
        invalid_raw = ap2_tests.closure.canonical_bytes(invalid_closure)
        for outcome in ("success", "compile-interruption", "ap2-rejection"):
            with self.subTest(outcome=outcome):
                def observe_helper_compile(source, filename, *args, **kwargs):
                    if filename == helper_path:
                        added = [(name, module) for name, module in sys.modules.items()
                                 if name.startswith(prefix) and name not in before]
                        self.assertEqual(len(added), 1)
                        name, module = added[0]
                        self.assertEqual(module.__name__, name)
                        self.assertEqual(module.__file__, helper_path)
                        registrations.append(name)
                        if outcome == "compile-interruption":
                            raise RuntimeError("Benign trusted-helper compile interruption")
                    return original_compile(source, filename, *args, **kwargs)

                with mock.patch.object(observer, "compile", side_effect=observe_helper_compile, create=True):
                    if outcome == "success":
                        self.assertEqual(self._observe().report["result"], observer.SUCCESS_RESULT)
                    else:
                        with self.assertRaises(observer.Rejected) as caught:
                            observer.observe_runner_imports(
                                invalid_raw if outcome == "ap2-rejection" else self.raw,
                                self._git_blob(invalid_raw) if outcome == "ap2-rejection" else self.pin)
                        self._assert_no_candidate_progress(caught.exception.report)
                self.assertEqual({name: module for name, module in sys.modules.items()
                                  if name.startswith(prefix)}, before)
        self.assertEqual(len(registrations), 3)

    def test_18_real_isolated_cli_preserves_checkout_and_creates_no_output(self):
        before_refs = self._git("show-ref")
        before_index = self._git("ls-files", "--stage", "-z")
        before_bytes = {path: (self.repo / path).read_bytes()
                        for path in (*ap2_tests.REVIEWED_BLOBS, ap2_tests.ENVELOPE_PATH)}
        ambient = self.parent / "cli-ambient"
        ambient.mkdir()
        for name in MODULE_NAMES:
            (ambient / (name + ".py")).write_bytes(b"# Inert PYTHONPATH/CWD fixture.\n")
        result = self._cli(environment={"PYTHONPATH": str(ambient)}, cwd=ambient)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertEqual(report["initializedModuleNames"], list(MODULE_NAMES))
        self._assert_closed(report)
        self.assertEqual(self._git("show-ref"), before_refs)
        self.assertEqual(self._git("ls-files", "--stage", "-z"), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")
        self.assertEqual({path: (self.repo / path).read_bytes() for path in before_bytes}, before_bytes)
        self.assertFalse((ambient / "__pycache__").exists())
        self._assert_protected_empty()

    def test_19_cli_requires_actual_isolation_no_site_and_no_bytecode_flags(self):
        for flags in (("-S", "-B"), ("-I", "-B"), ("-I", "-S")):
            with self.subTest(flags=flags):
                result = self._cli(flags=flags)
                self.assertEqual(result.returncode, 2, result.stderr.decode())
                self.assertEqual(result.stderr, b"")
                report = json.loads(result.stdout)
                self.assertIn("Python -I -S -B", report["reason"])
                self._assert_no_candidate_progress(report)
        self._assert_protected_empty()
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")

    def test_20_cli_rejects_bad_pins_and_execution_arguments_without_output(self):
        result = self._cli(expected_blob="0" * 40)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, b"")
        self._assert_no_candidate_progress(json.loads(result.stdout))
        for extra in (("--execute",), ("--mode", "preview"),
                      ("--approved-envelope-blob", self.pin),
                      ("--allow-player-launch",), ("--entry-point", PREFLIGHT_PATH)):
            with self.subTest(arguments=extra):
                result = self._cli(extra=extra)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"unrecognized arguments", result.stderr)
        for omission in ({"omit_closure": True}, {"omit_pin": True}):
            with self.subTest(omission=omission):
                result = self._cli(**omission)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"required", result.stderr)
        self._assert_protected_empty()
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")


if __name__ == "__main__":
    unittest.main()
