#!/usr/bin/env python3
"""AP4 source-only configuration-consumer regression tests.

Run with trusted Python -I -S -B. The path insertion loads only the trusted
observer and retained fixture modules. Candidate modules come from the actual
AP2 snapshot and AP3 private initializer. Negative fixtures use inert data or
benign interruptions; they never execute an alternate candidate program.
These are internal Primary checks, not independent AP4 approval.
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
import shutil
import subprocess
import sys
from types import CodeType, FunctionType, ModuleType, SimpleNamespace
import unittest
from unittest import mock


TRUSTED_TEST_DIRECTORY = Path(__file__).resolve(strict=True).parent
sys.path.insert(0, str(TRUSTED_TEST_DIRECTORY))
import d5b_runner_configuration as observer
import test_d5b_runner_imports as ap3_tests


MODULE_NAMES = ap3_tests.MODULE_NAMES
MODULE_PATHS = ap3_tests.MODULE_PATHS
PLAN_PATH = ap3_tests.ap2_tests.PLAN_PATH
PROFILE_PATH = ap3_tests.ap2_tests.PROFILE_PATH
CONSUMERS = ("d5b_local_admission.read_plan", "d5b_rr5_source_preflight.checked_profile")
OPERATIONS = ((PLAN_PATH, "is_file"), (PLAN_PATH, "is_symlink"),
              (PLAN_PATH, "read_bytes"), (PROFILE_PATH, "read_bytes"))
HELPER_PREFIXES = ("_ap4_verified_ap3_", "_ap3_verified_ap2_")


class D5BRunnerConfigurationSourceOnly(ap3_tests._AP2FixtureAdapter):
    """Module-qualified fixture reuse does not discover either retained suite."""

    def _registry(self):
        return {name: module for name, module in sys.modules.items()
                if name.startswith(HELPER_PREFIXES)}

    def _call(self, raw, pin):
        before = self._registry()
        try:
            return observer.observe_runner_configuration(raw, pin)
        finally:
            self.assertEqual(self._registry(), before)

    def _observe(self):
        return self._call(self.raw, self.pin)

    @contextmanager
    def _context(self):
        # This seam starts from actual authenticated AP2 records. It is not a
        # public means of supplying a context or claiming external provenance.
        progress = observer._progress()
        before = self._registry()
        with observer._import_helper(progress) as helper:
            closure, records, artifact_report = helper._verified_snapshot(self.raw, self.pin)
            context = helper._initialize_snapshot_context(
                closure, records, artifact_report, helper._progress())
            yield helper, context
        self.assertEqual(self._registry(), before)

    def _assert_json_only(self, value):
        ap3_tests.D5BRunnerImportsSourceOnly._assert_json_only(self, value)

    def _assert_protected_empty(self):
        ap3_tests.D5BRunnerImportsSourceOnly._assert_protected_empty(self)

    def _assert_closed(self, report):
        self.assertEqual(report["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")
        for field in ("D5BLocalExecution", "D5LocalValidation", "explicitUserLocalApproval"):
            self.assertEqual(report[field], "NotAuthorized", field)
        for field in (
            "candidateEntryPointsInvoked", "admissionPreviewInvoked", "sourceInspectionInvoked",
            "candidateFunctionsReplaced", "candidateSourceRewritten",
            "candidateApprovalConstantChangedByAP4", "candidateModulesInstalledInSysModules",
            "ambientCandidateImportLookupUsed", "candidateBytecodeLoaded", "candidateBytecodeWritten",
            "configurationPathnamesReopenedDuringConsumption", "runtimeConfigurationReadsBound",
            "futureRuntimeConfigurationReadsBound", "runtimeImportIsolationVerified",
            "runnerExecutableClosureVerified", "standardLibraryIdentityVerified", "pythonSandboxProvided",
            "checkoutRecheckedAfterModuleInitialization", "exclusiveCustodyVerified",
            "continuousCustodyVerified", "liveRemoteRefsVerified", "sourceDataInputsVerified",
            "currentMacInputsVerified", "executionAuthorityVerified", "R03Accepted", "H2Passed",
            "ReadyForHumanReviewGate", "allowNativeBuild", "allowPlayerLaunch", "UnityOrPlayerExecuted",
            "outputCreated", "networkUsed",
        ):
            self.assertIs(report[field], False, field)
        self.assertIs(report["trustedProcessRequired"], True)
        self.assertIsNone(report["approvedEnvelopeGitBlob"])
        self.assertEqual(report["independentlyReviewedConfigurationBinding"], "Pending")
        self.assertEqual(report["independentlyReviewedExecutableAdmission"], "Pending")
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)

    def _assert_no_candidate_progress(self, report):
        self.assertEqual(report["importProgress"]["initializationAttempted"], [])
        self.assertEqual(report["importProgress"]["initializedModuleNames"], [])
        self.assertEqual(report["configurationBindingsInstalled"], [])
        self.assertEqual(report["configurationOperations"], [])
        self.assertEqual(report["configurationConsumerCallsAttempted"], [])
        self.assertEqual(report["configurationConsumerCallsCompleted"], [])
        self.assertEqual(report["configurationValues"], {})
        self.assertIs(report["candidateTopLevelCodeMayHaveRun"], False)
        self.assertIs(report["candidateWriterImported"], False)
        self.assertIs(report["candidateFunctionsInvoked"], False)
        self.assertIs(report["planProfileFunctionsInvoked"], False)
        self.assertIs(report["fixedConfigurationConsumerReadsBound"], False)
        self.assertIs(report["configurationConsumersValidated"], False)
        self.assertIsNone(report["importObservation"])
        self._assert_closed(report)

    def _operation_records(self, pairs=OPERATIONS):
        return [{"path": path, "operation": operation,
                 "gitBlob": self._git_blob(self.fixture_bytes[path]),
                 "valueSource": "VerifiedAP2Snapshot"} for path, operation in pairs]

    def _cli(self, *, flags=("-I", "-S", "-B"), extra=(), expected_blob=None,
             omit_closure=False, omit_pin=False, environment=None, cwd=None):
        proposal_path = self.parent / "ap4-closure-proposal.json"
        proposal_path.write_bytes(self.raw)
        arguments = [sys.executable, *flags, str(Path(observer.__file__).resolve())]
        if not omit_closure:
            arguments.extend(("--closure", str(proposal_path)))
        if not omit_pin:
            arguments.extend(("--expected-closure-blob",
                              self.pin if expected_blob is None else expected_blob))
        arguments.extend(extra)
        environment_values = {key: value for key, value in self.git_environment.items()
                              if not key.startswith("PYTHON")}
        environment_values.update({} if environment is None else environment)
        return subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=environment_values, cwd=cwd, check=False, timeout=60)

    def test_01_actual_consumers_keep_private_function_identity_and_enabled_checks(self):
        consume = observer._consume_configuration
        entries, hashes, observed_contexts = [], [], []

        def observe_consumption(context, progress):
            observed_contexts.append(context)
            preflight, writer, wrapper = (context.modules[name] for name in MODULE_NAMES)
            functions = {name: {key: value for key, value in vars(module).items()
                                if isinstance(value, FunctionType)}
                         for name, module in context.modules.items()}
            namespaces = {name: dict(vars(module)) for name, module in context.modules.items()}
            read_plan, checked_profile = writer.read_plan, preflight.checked_profile
            self.assertIs(writer.source, preflight)
            self.assertIs(wrapper.main, writer.main)
            self.assertIs(read_plan.__globals__, vars(writer))
            self.assertIs(checked_profile.__globals__, vars(preflight))
            self.assertEqual(writer.APPROVED_EXECUTION_ENVELOPE_BLOB,
                             self.proposal["proposalEnvelopeGitBlob"])
            previous_profile = sys.getprofile()

            def profile(frame, event, arg):
                if event != "call":
                    return
                if frame.f_code is read_plan.__code__:
                    self.assertIs(frame.f_globals, vars(writer))
                    self.assertIs(frame.f_locals["verify_blob"], True)
                    entries.append(CONSUMERS[0])
                elif frame.f_code is checked_profile.__code__:
                    self.assertIs(frame.f_globals, vars(preflight))
                    self.assertIs(frame.f_locals["check_blob"], True)
                    self.assertIs(frame.f_locals["raw"], context.files[PROFILE_PATH].raw)
                    entries.append(CONSUMERS[1])
                elif frame.f_code is writer.git_blob.__code__:
                    self.assertIs(frame.f_locals["raw"], context.files[PLAN_PATH].raw)
                    hashes.append(PLAN_PATH)
                elif frame.f_code is preflight.git_blob.__code__:
                    self.assertIs(frame.f_locals["data"], context.files[PROFILE_PATH].raw)
                    hashes.append(PROFILE_PATH)

            try:
                sys.setprofile(profile)
                consume(context, progress)
            finally:
                sys.setprofile(previous_profile)
            self.assertIs(writer.read_plan, read_plan)
            self.assertIs(preflight.checked_profile, checked_profile)
            self.assertIs(type(writer.PLAN), observer._CapturedFile)
            self.assertIs(type(preflight.PROFILE), observer._CapturedFile)
            for name, module in context.modules.items():
                self.assertEqual(set(vars(module)), set(namespaces[name]))
                for key, value in namespaces[name].items():
                    if (name, key) not in ((MODULE_NAMES[1], "PLAN"), (MODULE_NAMES[0], "PROFILE")):
                        self.assertIs(vars(module)[key], value, (name, key))
                for key, function in functions[name].items():
                    self.assertIs(getattr(module, key), function)

        with mock.patch.object(observer, "_consume_configuration", side_effect=observe_consumption):
            report = self._observe().report
        self.assertEqual(len(observed_contexts), 1)
        self.assertEqual(entries, list(CONSUMERS))
        self.assertEqual(hashes, [PLAN_PATH, PROFILE_PATH])
        self.assertEqual(report["configurationConsumerCallsAttempted"], entries)
        self.assertEqual(report["configurationConsumerCallsCompleted"], entries)
        self.assertEqual(report["pinnedAP3HelperGitBlob"], "22ad93598131a59b2d5c46174a45187aede848a6")
        self.assertEqual(report["acceptedAP3PredecessorGitBlob"], "2bff794380f77b61dbbd84058fcba94d5ee4d9d2")
        self.assertIs(report["AP3HelperIncludesPrivateContextRefactor"], True)
        self.assertIs(report["consumerGlobalsMatchPrivateModules"], True)
        self.assertIs(report["configurationConsumersValidated"], True)
        self.assertIs(report["fixedConfigurationConsumerReadsBound"], True)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self._assert_closed(report)

    def test_02_each_public_call_uses_one_fresh_snapshot_and_initialization(self):
        import_helper, consume = observer._import_helper, observer._consume_configuration
        contexts, helpers, order = [], [], []

        @contextmanager
        def observed_helper(progress):
            with import_helper(progress) as helper:
                helpers.append(helper)
                snapshot, initialize = helper._verified_snapshot, helper._initialize_snapshot_context
                captured = []

                def observe_snapshot(*args):
                    order.append("snapshot")
                    result = snapshot(*args)
                    captured.append(result)
                    return result

                def observe_initialization(*args):
                    order.append("initialize")
                    self.assertEqual(len(captured), 1)
                    for actual, expected in zip(args[:3], captured[0]):
                        self.assertIs(actual, expected)
                    context = initialize(*args)
                    contexts.append(context)
                    return context

                with mock.patch.object(helper, "_verified_snapshot", side_effect=observe_snapshot) as verified, \
                        mock.patch.object(helper, "_initialize_snapshot_context", side_effect=observe_initialization) as initialized, \
                        mock.patch.object(helper, "observe_runner_imports") as public_imports:
                    yield helper
                    verified.assert_called_once_with(self.raw, self.pin)
                    initialized.assert_called_once()
                    public_imports.assert_not_called()

        def observed_consume(context, progress):
            order.append("consume")
            self.assertIs(context, contexts[-1])
            return consume(context, progress)

        with mock.patch.object(observer, "_import_helper", side_effect=observed_helper), \
                mock.patch.object(observer, "_consume_configuration", side_effect=observed_consume):
            reports = [self._observe().report for unused in range(2)]
        self.assertEqual(order, ["snapshot", "initialize", "consume"] * 2)
        self.assertEqual(len(helpers), 2)
        self.assertIsNot(helpers[0], helpers[1])
        for name in MODULE_NAMES:
            self.assertIsNot(contexts[0].modules[name], contexts[1].modules[name])
        for path in (PLAN_PATH, PROFILE_PATH):
            self.assertEqual(contexts[0].files[path].raw, contexts[1].files[path].raw)
            self.assertIsNot(contexts[0].files[path].raw, contexts[1].files[path].raw)
        for report in reports:
            self.assertEqual(report["importProgress"]["initializedModuleNames"], list(MODULE_NAMES))
            self.assertEqual(report["importProgress"]["initializationAttempted"], list(MODULE_NAMES))
            self.assertEqual(report["importProgress"]["verifiedArtifactCount"], 6)
            self._assert_closed(report)

    def test_03_report_matches_four_actual_captured_file_operations(self):
        actual, views = [], {}

        def observed_method(name):
            original = getattr(observer._CapturedFile, name)

            def call(view):
                result = original(view)
                actual.append((view.path, name))
                self.assertIs(views.setdefault(view.path, view), view)
                if name == "read_bytes":
                    self.assertIs(result, view._raw)
                    self.assertEqual(result, self.fixture_bytes[view.path])
                else:
                    self.assertIs(result, name == "is_file")
                return result
            return call

        with ExitStack() as stack:
            for operation in ("is_file", "is_symlink", "read_bytes"):
                stack.enter_context(mock.patch.object(observer._CapturedFile, operation,
                                                      new=observed_method(operation)))
            report = self._observe().report
        self.assertEqual(actual, list(OPERATIONS))
        self.assertEqual(report["configurationOperations"], self._operation_records(actual))
        self.assertEqual(report["configurationBindingsInstalled"],
                         ["d5b_local_admission.PLAN", "d5b_rr5_source_preflight.PROFILE"])
        self.assertEqual(report["configurationValues"], {
            "plan": json.loads(self.fixture_bytes[PLAN_PATH]),
            "profile": json.loads(self.fixture_bytes[PROFILE_PATH]),
        })
        self.assertEqual(report["configurationArtifacts"], [
            {"path": path, "gitBlob": self._git_blob(self.fixture_bytes[path]),
             "bytes": len(self.fixture_bytes[path]),
             "sha256": hashlib.sha256(self.fixture_bytes[path]).hexdigest(),
             "originalRuntimePath": str(self.repo / path)} for path in (PLAN_PATH, PROFILE_PATH)])
        self.assertEqual(report["configurationConsumptionScope"],
                         "read_plan_and_checked_profile_from_one_verified_snapshot")
        self.assertEqual(report["configurationMetadataScope"], "CapturedArtifactMetadata_NotCurrentPathState")
        self.assertEqual(report["configurationBindingsScope"], "PrivateModuleGlobalsOnly")
        self._assert_closed(report)

    def test_04_actual_candidate_call_graph_and_consumption_use_no_io(self):
        consume = observer._consume_configuration
        filenames = {str(self.repo / path) for path in MODULE_PATHS}
        observed_calls, observed_edges, blocked = set(), set(), []
        expected_names, expected_edges = set(), set()

        def guarded_consume(context, progress):
            preflight, writer, wrapper = (context.modules[name] for name in MODULE_NAMES)
            allowed = {}
            for module, names in ((writer, ("read_plan", "need", "git_blob", "parse_json")),
                                  (preflight, ("checked_profile", "git_blob", "read_object",
                                               "strict_pairs", "require"))):
                for name in names:
                    function = getattr(module, name)
                    allowed[function.__code__] = (module.__name__ + "." + name, vars(module))
            plan_name, profile_name = CONSUMERS
            expected_edges.update({
                (None, plan_name), (plan_name, "d5b_local_admission.need"),
                (plan_name, "d5b_local_admission.git_blob"),
                (plan_name, "d5b_local_admission.parse_json"),
                ("d5b_local_admission.parse_json", "d5b_rr5_source_preflight.read_object"),
                ("d5b_rr5_source_preflight.read_object", "d5b_rr5_source_preflight.strict_pairs"),
                ("d5b_rr5_source_preflight.strict_pairs", "d5b_rr5_source_preflight.require"),
                ("d5b_rr5_source_preflight.read_object", "d5b_rr5_source_preflight.require"),
                (None, profile_name), (profile_name, "d5b_rr5_source_preflight.git_blob"),
                (profile_name, "d5b_rr5_source_preflight.read_object"),
                (profile_name, "d5b_rr5_source_preflight.require"),
            })
            # Python 3.12+ inlines this comprehension. Earlier interpreters
            # have a real candidate <listcomp> frame, which is allowed only
            # when it is the exact nested code object from the pinned reader.
            for constant in writer.read_plan.__code__.co_consts:
                if isinstance(constant, CodeType):
                    self.assertEqual(constant.co_name, "<listcomp>")
                    name = plan_name + ".<listcomp>"
                    allowed[constant] = (name, vars(writer))
                    expected_edges.add((plan_name, name))
            expected_names.update(name for name, namespace in allowed.values())
            previous_profile = sys.getprofile()

            def profile(frame, event, arg):
                if event != "call" or frame.f_code.co_filename not in filenames:
                    return
                self.assertIn(frame.f_code, allowed, "Unexpected candidate function entered")
                name, namespace = allowed[frame.f_code]
                self.assertIs(frame.f_globals, namespace)
                parent = frame.f_back
                while parent is not None and parent.f_code.co_filename not in filenames:
                    parent = parent.f_back
                ancestor = None if parent is None else allowed[parent.f_code][0]
                observed_calls.add(name)
                observed_edges.add((ancestor, name))

            def deny(label):
                def call(*args, **kwargs):
                    blocked.append(label)
                    raise AssertionError("Configuration consumption attempted " + label)
                return call

            guards = (
                (builtins, ("open", "input")), (io, ("open",)), (_io, ("open", "open_code")),
                (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat",
                        "is_file", "is_dir", "is_symlink", "exists", "resolve", "absolute", "cwd", "home",
                        "iterdir", "glob", "rglob", "walk", "mkdir", "touch", "unlink", "rmdir", "rename",
                        "replace", "symlink_to", "hardlink_to", "chmod", "__fspath__")),
                (os, ("open", "fdopen", "read", "pread", "readv", "write", "pwrite", "writev", "close",
                      "stat", "lstat", "fstat", "scandir", "listdir", "readlink", "access", "getcwd", "chdir",
                      "fchdir", "link", "symlink", "unlink", "remove", "mkdir", "makedirs", "rmdir",
                      "removedirs", "rename", "replace", "chmod", "fchmod", "chown", "truncate", "ftruncate",
                      "utime", "fsync", "fdatasync", "system", "popen", "fork", "forkpty", "posix_spawn",
                      "posix_spawnp", "execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp",
                      "execvpe", "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp",
                      "spawnvpe", "fspath")),
                (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
                (shutil, ("copyfile", "copy", "copy2", "copytree", "move", "rmtree")),
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with ExitStack() as stack:
                for owner, attributes in guards:
                    for attribute in attributes:
                        if hasattr(owner, attribute):
                            stack.enter_context(mock.patch.object(owner, attribute,
                                                                  new=deny(owner.__name__ + "." + attribute)))
                # AP3 copied builtins before the consumption boundary; guard
                # those exact dictionaries as well as the ambient modules.
                for module in context.modules.values():
                    stack.enter_context(mock.patch.dict(module.__dict__["__builtins__"],
                                                        {"open": deny("candidate builtins.open"),
                                                         "input": deny("candidate builtins.input")}))
                stack.enter_context(redirect_stdout(stdout))
                stack.enter_context(redirect_stderr(stderr))
                try:
                    sys.setprofile(profile)
                    consume(context, progress)
                finally:
                    sys.setprofile(previous_profile)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")

        with mock.patch.object(observer, "_consume_configuration", side_effect=guarded_consume):
            report = self._observe().report
        self.assertEqual(observed_calls, expected_names)
        self.assertEqual(observed_edges, expected_edges)
        self.assertEqual(blocked, [])
        self.assertEqual(report["configurationValues"]["plan"]["producerScope"]["d5PlayerCells"],
                         ["D5-C%02d" % value for value in range(1, 19)])
        self._assert_closed(report)
        self._assert_protected_empty()

    def test_05_configuration_pathname_changes_after_capture_use_captured_bytes(self):
        consume = observer._consume_configuration
        replaced = []

        def replace_then_consume(context, progress):
            for path in (PLAN_PATH, PROFILE_PATH):
                actual_path = self.repo / path
                before_inode = actual_path.stat().st_ino
                replacement = self.parent / (actual_path.name + ".benign-replacement")
                replacement.write_bytes(b'{"fixture": "benign replacement after verified capture"}\n')
                os.replace(replacement, actual_path)
                self.assertNotEqual(actual_path.stat().st_ino, before_inode)
                self.assertNotEqual(actual_path.read_bytes(), context.files[path].raw)
                replaced.append(path)
            return consume(context, progress)

        with mock.patch.object(observer, "_consume_configuration", side_effect=replace_then_consume):
            report = self._observe().report
        self.assertEqual(replaced, [PLAN_PATH, PROFILE_PATH])
        self.assertEqual(report["configurationValues"], {
            "plan": json.loads(self.fixture_bytes[PLAN_PATH]),
            "profile": json.loads(self.fixture_bytes[PROFILE_PATH]),
        })
        self.assertEqual(report["configurationOperations"], self._operation_records())
        self.assertEqual(report["configurationMetadataScope"], "CapturedArtifactMetadata_NotCurrentPathState")
        self.assertIs(report["checkoutRecheckedAfterModuleInitialization"], False)
        self.assertIs(report["importObservation"]["artifactObservation"]["runnerCheckoutObservationVerified"], True)
        self._assert_closed(report)

    def test_06_invalid_public_inputs_reject_before_helper_code(self):
        class InertBytes(bytes):
            pass

        oversized = b" " * (observer.MAX_BYTES + 1)
        cases = (
            ("wrong-pin", self.raw, "0" * 40), ("changed-bytes", self.raw + b"\n", self.pin),
            ("text", self.raw.decode(), self.pin), ("mutable-bytes", bytearray(self.raw), self.pin),
            ("byte-subclass", InertBytes(self.raw), self.pin), ("malformed-pin", self.raw, "G" * 40),
            ("short-pin", self.raw, self.pin[:-1]), ("non-string-pin", self.raw, 7),
            ("oversized", oversized, self._git_blob(oversized)),
        )
        for label, raw, pin in cases:
            with self.subTest(change=label), \
                    mock.patch.object(observer, "_import_helper") as helper, \
                    mock.patch.object(observer, "_consume_configuration") as consume:
                with self.assertRaises(observer.Rejected) as caught:
                    self._call(raw, pin)
                helper.assert_not_called()
                consume.assert_not_called()
                self._assert_no_candidate_progress(caught.exception.report)

    def test_07_pinned_helper_drift_rejects_before_compilation(self):
        read_absolute = observer._read_absolute
        helper_path = Path(observer.__file__).resolve().with_name(observer.AP3_HELPER_NAME)
        self.assertEqual(self._git_blob(helper_path.read_bytes()), observer.AP3_HELPER_BLOB)
        reads = []

        def changed_helper(path):
            reads.append(path)
            return read_absolute(path) + b"\n# Harmless trusted-helper mismatch fixture.\n"

        with mock.patch.object(observer, "_read_absolute", side_effect=changed_helper), \
                mock.patch.object(observer, "compile", create=True) as compiler, \
                mock.patch.object(observer, "_consume_configuration") as consume:
            with self.assertRaises(observer.Rejected) as caught:
                self._observe()
        self.assertEqual(reads, [helper_path])
        compiler.assert_not_called()
        consume.assert_not_called()
        self.assertIn("AP3 helper differs from the pinned AP4 bytes", str(caught.exception))
        self.assertIs(caught.exception.report["trustedHelperRegistered"], False)
        self._assert_no_candidate_progress(caught.exception.report)

    def test_08_private_captured_records_require_consistent_immutable_bytes(self):
        with self._context() as (helper, context):
            for path in (PLAN_PATH, PROFILE_PATH):
                item = context.files[path]
                variants = {
                    "wrong-path": item._replace(path="inert-unexpected.json"),
                    "non-string-path": item._replace(path=3),
                    "mutable-content": item._replace(raw=bytearray(item.raw)),
                    "changed-bytes": item._replace(raw=item.raw + b"\n"),
                    "changed-blob": item._replace(git_blob="0" * 40),
                    "malformed-blob": item._replace(git_blob="G" * 40),
                    "non-string-blob": item._replace(git_blob=3),
                    "oversized": item._replace(raw=b" " * (observer.MAX_BYTES + 1)),
                }
                for label, changed in variants.items():
                    with self.subTest(path=path, change=label):
                        files = {**context.files, path: changed}
                        progress = observer._progress()
                        with self.assertRaises(observer._Problem):
                            observer._captured_file(context._replace(files=files), path, progress)
                        self.assertEqual(progress["configurationOperations"], [])
                files = dict(context.files)
                del files[path]
                with self.subTest(path=path, change="missing-record"), self.assertRaises(observer._Problem):
                    observer._captured_file(context._replace(files=files), path, observer._progress())
            with self.assertRaises(observer._Problem):
                observer._captured_file(context, helper.ENVELOPE_PATH, observer._progress())

    def test_09_private_adapters_are_narrow_frozen_snapshot_views(self):
        with self._context() as (helper, context):
            for path in (PLAN_PATH, PROFILE_PATH):
                with self.subTest(path=path):
                    progress = observer._progress()
                    view = observer._captured_file(context, path, progress)
                    self.assertEqual([item.name for item in fields(view)],
                                     ["path", "git_blob", "_raw", "_operations"])
                    self.assertIs(type(view.path), str)
                    self.assertIs(view._raw, context.files[path].raw)
                    self.assertIs(view._operations, progress["configurationOperations"])
                    self.assertIs(view.is_file(), True)
                    self.assertIs(view.is_symlink(), False)
                    self.assertIs(view.read_bytes(), context.files[path].raw)
                    self.assertEqual(progress["configurationOperations"], self._operation_records(
                        ((path, "is_file"), (path, "is_symlink"), (path, "read_bytes"))))
                    public_calls = {name for name in dir(view)
                                    if not name.startswith("_") and callable(getattr(view, name))}
                    self.assertEqual(public_calls, {"is_file", "is_symlink", "read_bytes"})
                    for missing in ("open", "read_text", "write_bytes", "stat", "resolve", "__fspath__", "__getattr__"):
                        self.assertFalse(hasattr(view, missing), missing)
                    with self.assertRaises(TypeError):
                        os.fspath(view)
                    with self.assertRaises(TypeError):
                        Path(view)
                    with self.assertRaises(FrozenInstanceError):
                        view._raw = b"inert replacement"

    def test_10_private_binding_and_blob_mismatches_reject_before_consumer_calls(self):
        with self._context() as (helper, context):
            preflight, writer = (context.modules[name] for name in MODULE_NAMES[:2])
            cases = (
                (writer, "source", ModuleType("inert_wrong_source")),
                (writer, "read_plan", SimpleNamespace(__globals__={})),
                (preflight, "checked_profile", SimpleNamespace(__globals__={})),
                (writer, "PLAN_BLOB", "0" * 40),
                (preflight, "PROFILE_BLOB", "0" * 40),
            )
            for module, attribute, value in cases:
                with self.subTest(module=module.__name__, attribute=attribute), \
                        mock.patch.object(module, attribute, value):
                    progress = observer._progress()
                    with self.assertRaises(observer._Problem):
                        observer._consume_configuration(context, progress)
                    self.assertEqual(progress["configurationBindingsInstalled"], [])
                    self.assertEqual(progress["configurationOperations"], [])
                    self.assertEqual(progress["configurationConsumerCallsAttempted"], [])
            for path in (PLAN_PATH, PROFILE_PATH):
                with self.subTest(self_consistent_changed_record=path):
                    raw = context.files[path].raw + b"\n"
                    files = {**context.files, path: context.files[path]._replace(
                        raw=raw, git_blob=self._git_blob(raw))}
                    progress = observer._progress()
                    with self.assertRaisesRegex(observer._Problem, "constants differ"):
                        observer._consume_configuration(context._replace(files=files), progress)
                    self.assertEqual(progress["configurationBindingsInstalled"], [])
                    self.assertEqual(progress["configurationConsumerCallsAttempted"], [])

    def test_11_real_consumers_reject_changed_read_bytes_with_truthful_progress(self):
        read_bytes = observer._CapturedFile.read_bytes
        for path, attempted, completed, operations, reason in (
            (PLAN_PATH, CONSUMERS[:1], (), OPERATIONS[:3], "Unreviewed D5-B local plan bytes"),
            (PROFILE_PATH, CONSUMERS, CONSUMERS[:1], OPERATIONS, "Unreviewed RR5 proposal bytes"),
        ):
            with self.subTest(changed_read=path):
                def changed_read(view):
                    raw = read_bytes(view)
                    # Whitespace preserves the JSON values, so rejection
                    # specifically demonstrates the real enabled hash check.
                    return raw + b"\n" if view.path == path else raw

                with mock.patch.object(observer._CapturedFile, "read_bytes", new=changed_read):
                    with self.assertRaises(observer.Rejected) as caught:
                        self._observe()
                report = caught.exception.report
                self.assertIn(reason, str(caught.exception))
                self.assertEqual(report["result"], observer.REJECTED_RESULT)
                self.assertEqual(report["configurationConsumerCallsAttempted"], list(attempted))
                self.assertEqual(report["configurationConsumerCallsCompleted"], list(completed))
                self.assertEqual(report["configurationOperations"], self._operation_records(operations))
                self.assertEqual(set(report["configurationValues"]), {"plan"} if completed else set())
                self.assertIs(report["candidateFunctionsInvoked"], True)
                self.assertIs(report["planProfileFunctionsInvoked"], True)
                self.assertIs(report["configurationConsumersValidated"], False)
                self.assertIs(report["fixedConfigurationConsumerReadsBound"], False)
                self.assertIs(report["trustedHelperRegistrationRemoved"], True)
                self._assert_closed(report)
                self._assert_protected_empty()

    def test_12_profile_read_interruption_does_not_claim_profile_invocation(self):
        read_bytes = observer._CapturedFile.read_bytes
        actual_consumers = []
        filenames = {str(self.repo / path) for path in MODULE_PATHS}
        previous_profile = sys.getprofile()

        def interrupted_read(view):
            if view.path == PROFILE_PATH:
                raise RuntimeError("Benign interruption before profile argument is available")
            return read_bytes(view)

        def profile(frame, event, arg):
            if event == "call" and frame.f_code.co_filename in filenames:
                name = frame.f_globals["__name__"] + "." + frame.f_code.co_name
                if name in CONSUMERS:
                    actual_consumers.append(name)

        try:
            sys.setprofile(profile)
            with mock.patch.object(observer._CapturedFile, "read_bytes", new=interrupted_read):
                with self.assertRaises(observer.Rejected) as caught:
                    self._observe()
        finally:
            sys.setprofile(previous_profile)
        report = caught.exception.report
        self.assertEqual(actual_consumers, list(CONSUMERS[:1]))
        self.assertEqual(report["configurationConsumerCallsAttempted"], actual_consumers)
        self.assertEqual(report["configurationConsumerCallsCompleted"], actual_consumers)
        self.assertEqual(report["configurationOperations"], self._operation_records(OPERATIONS[:3]))
        self.assertEqual(report["configurationValues"], {"plan": json.loads(self.fixture_bytes[PLAN_PATH])})
        self.assertIn("before profile argument", report["reason"])
        self.assertIs(report["configurationConsumersValidated"], False)
        self.assertIs(report["fixedConfigurationConsumerReadsBound"], False)
        self._assert_closed(report)

    def test_13_earlier_reports_remain_frozen_preconsumer_observations(self):
        consume = observer._consume_configuration
        before = []

        def observe_stage_boundary(context, progress):
            earlier = progress["importObservation"]
            before.append(observer._canonical(earlier))
            self.assertEqual(progress["configurationConsumerCallsAttempted"], [])
            ap3_tests.D5BRunnerImportsSourceOnly._assert_closed(self, earlier)
            ap3_tests.ap2_tests.D5BRunnerClosureSourceOnly._assert_closed(self, earlier["artifactObservation"])
            consume(context, progress)
            original_size = context.observation["dataArtifacts"][0]["bytes"]
            initialized = progress["importProgress"]["initializedModuleNames"]
            try:
                context.observation["dataArtifacts"][0]["bytes"] = -1
                initialized.append("inert later-stage presentation marker")
                self.assertEqual(observer._canonical(earlier), before[0])
            finally:
                context.observation["dataArtifacts"][0]["bytes"] = original_size
                initialized.pop()

        with mock.patch.object(observer, "_consume_configuration", side_effect=observe_stage_boundary):
            report = self._observe().report
        earlier = report["importObservation"]
        self.assertEqual(observer._canonical(earlier), before[0])
        self.assertEqual(report["importObservationScope"], "AP3BeforeConfigurationBindingAndConsumerCallsOnly")
        self.assertEqual(earlier["artifactObservationScope"], "AP2BeforeCandidateModuleInitializationOnly")
        self.assertIs(report["candidateFunctionsInvoked"], True)
        self.assertIs(earlier["candidateFunctionsInvoked"], False)
        self.assertIs(earlier["planProfileFunctionsInvoked"], False)
        self.assertIs(earlier["artifactObservation"]["candidateWriterExecutedOrImported"], False)
        self._assert_closed(report)

    def test_14_private_helper_registrations_are_removed_for_all_outcomes(self):
        original_compile, consume = builtins.compile, observer._consume_configuration
        ap3_path = str(Path(observer.__file__).resolve().with_name(observer.AP3_HELPER_NAME))
        ap2_path = str(Path(observer.__file__).resolve().with_name("d5b_runner_closure.py"))
        invalid = copy.deepcopy(self.proposal)
        invalid["scope"] = "Inert invalid scope fixture"
        invalid_raw = ap3_tests.ap2_tests.closure.canonical_bytes(invalid)
        before = self._registry()
        for outcome in ("success", "ap3-compile-interruption", "ap2-rejection", "consumer-interruption"):
            with self.subTest(outcome=outcome):
                registrations = []

                def observe_compile(raw, filename, *args, **kwargs):
                    if filename in (ap3_path, ap2_path):
                        prefix = HELPER_PREFIXES[0 if filename == ap3_path else 1]
                        active = [(name, module) for name, module in self._registry().items()
                                  if name.startswith(prefix) and name not in before]
                        self.assertEqual(len(active), 1)
                        name, module = active[0]
                        self.assertEqual(module.__name__, name)
                        self.assertEqual(module.__file__, filename)
                        registrations.append(filename)
                        if outcome == "ap3-compile-interruption" and filename == ap3_path:
                            raise RuntimeError("Benign trusted AP3 compiler interruption")
                    return original_compile(raw, filename, *args, **kwargs)

                def observe_consume(context, progress):
                    if outcome == "consumer-interruption":
                        raise RuntimeError("Benign interruption at the consumer boundary")
                    return consume(context, progress)

                with mock.patch.object(builtins, "compile", new=observe_compile), \
                        mock.patch.object(observer, "_consume_configuration", side_effect=observe_consume):
                    if outcome == "success":
                        report = self._observe().report
                    else:
                        with self.assertRaises(observer.Rejected) as caught:
                            self._call(invalid_raw if outcome == "ap2-rejection" else self.raw,
                                       self._git_blob(invalid_raw) if outcome == "ap2-rejection" else self.pin)
                        report = caught.exception.report
                self.assertEqual(registrations, [ap3_path] if outcome == "ap3-compile-interruption"
                                 else [ap3_path, ap2_path])
                self.assertEqual(self._registry(), before)
                self.assertIs(report["trustedHelperRegistered"], True)
                self.assertIs(report["trustedHelperRegistrationRemoved"], True)
                if outcome in ("ap3-compile-interruption", "ap2-rejection"):
                    self._assert_no_candidate_progress(report)
                elif outcome == "consumer-interruption":
                    self.assertEqual(report["importProgress"]["initializedModuleNames"], list(MODULE_NAMES))
                    self.assertEqual(report["configurationConsumerCallsAttempted"], [])
                    self.assertEqual(report["configurationConsumerCallsCompleted"], [])
                    self.assertIs(report["candidateFunctionsInvoked"], False)
                    self.assertIsNotNone(report["importObservation"])
                self._assert_closed(report)

    def test_15_public_observations_are_immutable_json_with_a_narrow_signature(self):
        result = self._observe()
        self.assertIs(type(result), observer.ConfigurationObservation)
        self.assertEqual([item.name for item in fields(result)], ["_report_json"])
        self.assertEqual(set(vars(result)), {"_report_json"})
        self.assertIs(type(result._report_json), bytes)
        self.assertEqual(result._report_json, observer._canonical(result.report))
        with self.assertRaises(FrozenInstanceError):
            result._report_json = b"{}"
        report = result.report
        self._assert_json_only(report)
        report["executionAuthorityVerified"] = True
        report["configurationOperations"].clear()
        report["configurationValues"]["plan"]["authorization"]["D5BLocalExecution"] = "Inert changed copy"
        report["importObservation"]["candidateFunctionsInvoked"] = True
        report["importProgress"]["initializedModuleNames"].clear()
        self._assert_closed(result.report)
        self.assertEqual(result.report["configurationOperations"], self._operation_records())
        self.assertEqual(result.report["configurationValues"]["plan"]["authorization"]["D5BLocalExecution"],
                         "NotAuthorized")
        self.assertIs(result.report["importObservation"]["candidateFunctionsInvoked"], False)
        self.assertEqual(result.report["importProgress"]["initializedModuleNames"], list(MODULE_NAMES))
        with self.assertRaises(observer.Rejected) as caught:
            self._call(self.raw, "0" * 40)
        rejected = caught.exception.report
        self._assert_json_only(rejected)
        self.assertIs(type(caught.exception._report_json), bytes)
        rejected["configurationConsumerCallsCompleted"].append("inert changed copy")
        rejected["reason"] = "inert changed copy"
        self.assertEqual(caught.exception.report["configurationConsumerCallsCompleted"], [])
        self.assertNotEqual(caught.exception.report["reason"], "inert changed copy")
        signature = inspect.signature(observer.observe_runner_configuration)
        self.assertEqual(list(signature.parameters), ["raw", "expected_closure_blob"])
        for keyword in ("context", "modules", "bundle", "mode"):
            with self.subTest(keyword=keyword), self.assertRaises(TypeError):
                observer.observe_runner_configuration(self.raw, self.pin, **{keyword: object()})

    def test_16_real_isolated_cli_preserves_checkout_and_creates_no_output(self):
        before_refs, before_index = self._git("show-ref"), self._git("ls-files", "--stage", "-z")
        paths = (*ap3_tests.ap2_tests.REVIEWED_BLOBS, ap3_tests.ap2_tests.ENVELOPE_PATH)
        before_bytes = {path: (self.repo / path).read_bytes() for path in paths}
        ambient = self.parent / "ap4-cli-ambient"
        ambient.mkdir()
        for name in MODULE_NAMES:
            (ambient / (name + ".py")).write_bytes(b"# Inert ignored PYTHONPATH/CWD fixture.\n")
        result = self._cli(environment={"PYTHONPATH": str(ambient)}, cwd=ambient)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertEqual(report["configurationConsumerCallsCompleted"], list(CONSUMERS))
        self.assertEqual(report["configurationOperations"], self._operation_records())
        self.assertEqual(report["interpreterFlags"],
                         {"isolated": True, "noSite": True, "noBytecodeWrites": True})
        self._assert_closed(report)
        self.assertEqual(self._git("show-ref"), before_refs)
        self.assertEqual(self._git("ls-files", "--stage", "-z"), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")
        self.assertEqual({path: (self.repo / path).read_bytes() for path in paths}, before_bytes)
        self.assertFalse((ambient / "__pycache__").exists())
        self._assert_protected_empty()

    def test_17_cli_requires_all_three_real_interpreter_flags(self):
        for flags in (("-S", "-B"), ("-I", "-B"), ("-I", "-S")):
            with self.subTest(flags=flags):
                result = self._cli(flags=flags)
                self.assertEqual(result.returncode, 2, result.stderr.decode())
                self.assertEqual(result.stderr, b"")
                report = json.loads(result.stdout)
                self.assertIn("Python -I -S -B", report["reason"])
                self._assert_no_candidate_progress(report)
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")
        self._assert_protected_empty()

    def test_18_cli_requires_both_arguments_and_rejects_execution_options(self):
        result = self._cli(expected_blob="0" * 40)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, b"")
        self._assert_no_candidate_progress(json.loads(result.stdout))
        for omission in ({"omit_closure": True}, {"omit_pin": True}):
            with self.subTest(omission=omission):
                result = self._cli(**omission)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"required", result.stderr)
        for extra in (("--execute",), ("--mode", "preview"), ("--inspect",),
                      ("--approved-envelope-blob", self.pin), ("--allow-player-launch",),
                      ("--allow-native-build",), ("--entry-point", ap3_tests.PREFLIGHT_PATH)):
            with self.subTest(arguments=extra):
                result = self._cli(extra=extra)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"unrecognized arguments", result.stderr)
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")
        self._assert_protected_empty()


if __name__ == "__main__":
    unittest.main()
