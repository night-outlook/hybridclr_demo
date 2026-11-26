#!/usr/bin/env python3
"""AP4: observe fixed configuration consumers using captured, verified bytes.

Use trusted Python -I -S -B. This companion initializes the fixed AP3 module
graph, binds two private snapshot views, and calls only read_plan and
checked_profile with their blob checks enabled. It grants no Local authority
and does not bind future admission, source inputs or general runtime reads.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from types import ModuleType

AP3_HELPER_NAME = "d5b_runner_imports.py"
AP3_HELPER_BLOB = "22ad93598131a59b2d5c46174a45187aede848a6"
ACCEPTED_AP3_PREDECESSOR_BLOB = "2bff794380f77b61dbbd84058fcba94d5ee4d9d2"
MAX_BYTES = 1024 * 1024
LOCAL = "Tools/AssemblyShadow/R03IR/D5Local/"
ADMISSION = "Tools/AssemblyShadow/R03IR/D5Admission/"
PLAN_PATH = LOCAL + "d5b_local_admission_plan_v1.json"
PROFILE_PATH = ADMISSION + "d5b_rr5_source_preflight_v1.json"
CANDIDATE_NAMES = ("d5b_rr5_source_preflight", "d5b_local_admission", "run_d5_local")
CONSUMERS = ("d5b_local_admission.read_plan", "d5b_rr5_source_preflight.checked_profile")
SUCCESS_RESULT = "RunnerConfigurationConsumersObserved_NoExecutionAuthority"
REJECTED_RESULT = "RunnerConfigurationConsumersRejected_NoExecutionAuthority"


class _Problem(ValueError):
    pass


def _need(ok: bool, reason: str) -> None:
    if not ok:
        raise _Problem(reason)


def _canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _blob(raw: bytes) -> str:
    _need(type(raw) is bytes, "Snapshot content must be immutable bytes")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _sha(value: object) -> str:
    _need(type(value) is str and len(value) == 40 and
          all(c in "0123456789abcdef" for c in value), "Expected an exact Git SHA-1")
    return value


def _require_isolation() -> None:
    _need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
          "Invoke the trusted observer with Python -I -S -B")


def _fingerprint(value: os.stat_result) -> tuple:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _read_absolute(path: Path) -> bytes:
    """Bounded input/installed-helper read; not continuous installation custody."""
    _need(isinstance(path, Path) and path.is_absolute() and path.name not in ("", ".", ".."),
          "Input must be an absolute file path")
    parent = path.parent
    _need(parent.resolve(strict=True) == parent, "Input parent must be canonical")
    before_parent = parent.lstat()
    _need(stat.S_ISDIR(before_parent.st_mode), "Input parent must be a directory")
    parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    leaf = None
    try:
        opened_parent = os.fstat(parent_fd)
        _need((opened_parent.st_dev, opened_parent.st_ino) ==
              (before_parent.st_dev, before_parent.st_ino), "Input parent changed")
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        before = os.fstat(leaf)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
              before.st_mode & 0o111 == 0 and before.st_size <= MAX_BYTES,
              "Input must be bounded single-link non-executable regular bytes")
        chunks, size = [], 0
        while True:
            chunk = os.read(leaf, min(65536, MAX_BYTES + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            _need(size <= MAX_BYTES, "Input exceeded byte bound")
            chunks.append(chunk)
        after = os.fstat(leaf)
        named = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        _need(_fingerprint(before) == _fingerprint(after) == _fingerprint(named) and
              size == before.st_size, "Input identity or bytes changed during read")
        after_parent = parent.lstat()
        _need(parent.resolve(strict=True) == parent and
              (after_parent.st_dev, after_parent.st_ino) ==
              (before_parent.st_dev, before_parent.st_ino), "Input parent changed after read")
        return b"".join(chunks)
    finally:
        if leaf is not None:
            os.close(leaf)
        os.close(parent_fd)

@contextmanager
def _import_helper(progress: dict):
    """Authenticate the refactored AP3 implementation before executing it."""
    path = Path(__file__).resolve(strict=True).with_name(AP3_HELPER_NAME)
    raw = _read_absolute(path)
    _need(_blob(raw) == AP3_HELPER_BLOB, "AP3 helper differs from the pinned AP4 bytes")
    helper = ModuleType("_ap4_verified_ap3")
    private_name = "_ap4_verified_ap3_" + format(id(helper), "x")
    _need(private_name not in sys.modules, "Trusted helper module name is occupied")
    helper.__name__ = private_name
    helper.__file__ = str(path)
    helper.__package__ = ""
    helper.__cached__ = None
    sys.modules[private_name] = helper
    progress["trustedHelperRegistered"] = True
    try:
        exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), helper.__dict__)
        yield helper
    finally:
        _need(sys.modules.get(private_name) is helper, "Trusted helper registry changed")
        del sys.modules[private_name]
        progress["trustedHelperRegistrationRemoved"] = True


@dataclass(frozen=True)
class _CapturedFile:
    """A private snapshot view, with no filesystem or path-protocol fallback."""

    path: str
    git_blob: str
    _raw: bytes = field(repr=False)
    _operations: list = field(repr=False, compare=False)

    def _record(self, operation: str) -> None:
        self._operations.append({"path": self.path, "operation": operation,
                                 "gitBlob": self.git_blob,
                                 "valueSource": "VerifiedAP2Snapshot"})

    def is_file(self) -> bool:
        self._record("is_file")
        return True

    def is_symlink(self) -> bool:
        self._record("is_symlink")
        return False

    def read_bytes(self) -> bytes:
        self._record("read_bytes")
        return self._raw


def _captured_file(context, path: str, progress: dict) -> _CapturedFile:
    """Private consistency check; only the fresh verified context reaches it."""
    _need(path in (PLAN_PATH, PROFILE_PATH) and path in context.files,
          "Expected the fixed captured configuration record")
    item = context.files[path]
    _need(type(item.path) is str and item.path == path and
          type(item.raw) is bytes and len(item.raw) <= MAX_BYTES and
          _sha(item.git_blob) == _blob(item.raw), "Captured configuration record changed")
    return _CapturedFile(path, item.git_blob, item.raw, progress["configurationOperations"])


def _consume_configuration(context, progress: dict) -> None:
    """Adapt only private configuration globals; call the two fixed consumers."""
    writer = context.modules["d5b_local_admission"]
    preflight = context.modules["d5b_rr5_source_preflight"]
    _need(writer.source is preflight and
          writer.read_plan.__globals__ is writer.__dict__ and
          preflight.checked_profile.__globals__ is preflight.__dict__,
          "Configuration consumers do not belong to the private initialized modules")
    plan_view = _captured_file(context, PLAN_PATH, progress)
    profile_view = _captured_file(context, PROFILE_PATH, progress)
    _need(writer.PLAN_BLOB == plan_view.git_blob and
          preflight.PROFILE_BLOB == profile_view.git_blob,
          "Configuration consumer constants differ from captured bytes")
    progress["configurationArtifacts"] = [
        {"path": view.path, "gitBlob": view.git_blob, "bytes": len(view._raw),
         "sha256": hashlib.sha256(view._raw).hexdigest(),
         "originalRuntimePath": str(writer.PLAN if view is plan_view else preflight.PROFILE)}
        for view in (plan_view, profile_view)
    ]
    writer.PLAN = plan_view
    progress["configurationBindingsInstalled"].append("d5b_local_admission.PLAN")
    preflight.PROFILE = profile_view
    progress["configurationBindingsInstalled"].append("d5b_rr5_source_preflight.PROFILE")
    progress["consumerGlobalsMatchPrivateModules"] = True

    progress["configurationConsumerCallsAttempted"].append(CONSUMERS[0])
    plan = writer.read_plan(verify_blob=True)
    progress["configurationConsumerCallsCompleted"].append(CONSUMERS[0])
    progress["configurationValues"]["plan"] = plan

    # Read the argument before recording checked_profile invocation. An error
    # in this read must not claim that checked_profile's body was entered.
    profile_raw = preflight.PROFILE.read_bytes()
    progress["configurationConsumerCallsAttempted"].append(CONSUMERS[1])
    profile = preflight.checked_profile(profile_raw, check_blob=True)
    progress["configurationConsumerCallsCompleted"].append(CONSUMERS[1])
    progress["configurationValues"]["profile"] = profile
    _need([(entry["path"], entry["operation"]) for entry in progress["configurationOperations"]] == [
        (PLAN_PATH, "is_file"), (PLAN_PATH, "is_symlink"), (PLAN_PATH, "read_bytes"),
        (PROFILE_PATH, "read_bytes")], "Fixed configuration consumption shape changed")
    _need(writer.PLAN is plan_view and preflight.PROFILE is profile_view,
          "Private configuration bindings changed during consumption")


def _progress() -> dict:
    return {
        "importProgress": {"verifiedArtifactCount": 0, "compiledModuleNames": [],
                           "initializationAttempted": [], "initializedModuleNames": []},
        "trustedHelperRegistered": False, "trustedHelperRegistrationRemoved": False,
        "realSysPathUnchanged": True, "ambientCandidateModuleCacheUnchanged": True,
        "configurationBindingsInstalled": [], "configurationArtifacts": [],
        "configurationOperations": [], "configurationConsumerCallsAttempted": [],
        "configurationConsumerCallsCompleted": [], "configurationValues": {},
        "consumerGlobalsMatchPrivateModules": False,
        "importObservation": None,
    }


def _process_state():
    absent = object()
    return (sys.path, tuple(sys.path), absent,
            {name: sys.modules.get(name, absent) for name in CANDIDATE_NAMES})


def _check_process_state(progress: dict, before) -> None:
    path, contents, absent, slots = before
    progress["realSysPathUnchanged"] = sys.path is path and tuple(sys.path) == contents
    progress["ambientCandidateModuleCacheUnchanged"] = all(
        sys.modules.get(name, absent) is prior for name, prior in slots.items())
    _need(progress["realSysPathUnchanged"] and progress["ambientCandidateModuleCacheUnchanged"],
          "Process import state changed during configuration observation")


def _closed_report(result: str, progress: dict, reason: str | None = None) -> dict:
    imports = progress["importProgress"]
    value = {
        "schemaVersion": 1, "kind": "R03D5BRunnerConfigurationObservationV1", "result": result,
        "fixedConfigurationConsumerReadsBound": result == SUCCESS_RESULT,
        "configurationConsumersValidated": result == SUCCESS_RESULT,
        "configurationConsumptionScope": "read_plan_and_checked_profile_from_one_verified_snapshot",
        "configurationMetadataScope": "CapturedArtifactMetadata_NotCurrentPathState",
        "configurationBindingsScope": "PrivateModuleGlobalsOnly",
        "configurationPathnamesReopenedDuringConsumption": False,
        "candidateTopLevelCodeMayHaveRun": bool(imports["initializationAttempted"]),
        "candidateWriterImported": "d5b_local_admission" in imports["initializedModuleNames"],
        "candidateFunctionsInvoked": bool(progress["configurationConsumerCallsAttempted"]),
        "planProfileFunctionsInvoked": bool(progress["configurationConsumerCallsAttempted"]),
        "candidateFunctionScope": "TwoConfigurationConsumersAndTheirReviewedPureHelpers",
        "candidateEntryPointsInvoked": False, "admissionPreviewInvoked": False,
        "sourceInspectionInvoked": False, "candidateFunctionsReplaced": False,
        "candidateSourceRewritten": False, "candidateApprovalConstantChangedByAP4": False,
        "candidateModulesInstalledInSysModules": False,
        "ambientCandidateImportLookupUsed": False,
        "candidateBytecodeLoaded": False, "candidateBytecodeWritten": False,
        "importObservationScope": "AP3BeforeConfigurationBindingAndConsumerCallsOnly",
        "runtimeConfigurationReadsBound": False,
        "futureRuntimeConfigurationReadsBound": False,
        "runtimeImportIsolationVerified": False, "runnerExecutableClosureVerified": False,
        "standardLibraryIdentityVerified": False, "trustedProcessRequired": True,
        "pythonSandboxProvided": False, "checkoutRecheckedAfterModuleInitialization": False,
        "exclusiveCustodyVerified": False, "continuousCustodyVerified": False,
        "liveRemoteRefsVerified": False, "sourceDataInputsVerified": False,
        "currentMacInputsVerified": False, "executionAuthorityVerified": False,
        "approvedEnvelopeGitBlob": None, "independentlyReviewedConfigurationBinding": "Pending",
        "independentlyReviewedExecutableAdmission": "Pending",
        "explicitUserLocalApproval": "NotAuthorized", "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "D5BLocalExecution": "NotAuthorized", "D5LocalValidation": "NotAuthorized",
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
        "allowNativeBuild": False, "allowPlayerLaunch": False, "UnityOrPlayerExecuted": False,
        "realUnityBuild": "NotRun", "realPlayerCellsPassed": 0, "realPlayerCellsNoCoverage": 18,
        "outputCreated": False, "networkUsed": False,
        **progress,
    }
    if reason is not None:
        value["reason"] = reason[:1600]
    return value


@dataclass(frozen=True)
class ConfigurationObservation:
    _report_json: bytes

    @property
    def report(self) -> dict:
        return json.loads(self._report_json)


class Rejected(ValueError):
    def __init__(self, reason: str, progress: dict):
        super().__init__(reason)
        self._report_json = _canonical(_closed_report(REJECTED_RESULT, progress, reason))

    @property
    def report(self) -> dict:
        return json.loads(self._report_json)


def observe_runner_configuration(raw: bytes, expected_closure_blob: str) -> ConfigurationObservation:
    """Observe two captured-byte consumers; accept no modules, contexts or modes."""
    progress = _progress()
    before = _process_state()
    try:
        _require_isolation()
        _sha(expected_closure_blob)
        _need(type(raw) is bytes and len(raw) <= MAX_BYTES and _blob(raw) == expected_closure_blob,
              "Closure bytes do not match their exact external pin")
        with _import_helper(progress) as helper:
            imports = helper._progress()
            progress["importProgress"] = imports
            closure, records, artifact_report = helper._verified_snapshot(raw, expected_closure_blob)
            context = helper._initialize_snapshot_context(closure, records, artifact_report, imports)
            _check_process_state(progress, before)
            imports["realSysPathUnchanged"] = progress["realSysPathUnchanged"]
            imports["ambientCandidateModuleCacheUnchanged"] = progress["ambientCandidateModuleCacheUnchanged"]
            earlier = {
                **helper._closed_report(helper.SUCCESS_RESULT, imports), **context.observation,
                "closureProposalGitBlob": expected_closure_blob,
                "reviewedAP2VerifierGitBlob": helper.AP2_HELPER_BLOB,
                "sourcePins": closure["sourcePins"], "runner": closure["runner"],
                "artifactObservationScope": "AP2BeforeCandidateModuleInitializationOnly",
                "artifactObservation": artifact_report,
                "interpreterFlags": {"isolated": bool(sys.flags.isolated),
                                     "noSite": bool(sys.flags.no_site),
                                     "noBytecodeWrites": bool(sys.dont_write_bytecode)},
            }
            # Freeze the earlier stage before candidate consumer calls.
            progress["importObservation"] = json.loads(_canonical(earlier))
            _consume_configuration(context, progress)
        _check_process_state(progress, before)
        report = {
            **_closed_report(SUCCESS_RESULT, progress),
            "closureProposalGitBlob": expected_closure_blob,
            "pinnedAP3HelperGitBlob": AP3_HELPER_BLOB,
            "acceptedAP3PredecessorGitBlob": ACCEPTED_AP3_PREDECESSOR_BLOB,
            "AP3HelperIncludesPrivateContextRefactor": True,
            "sourcePins": closure["sourcePins"], "runner": closure["runner"],
            "interpreterFlags": {"isolated": bool(sys.flags.isolated),
                                 "noSite": bool(sys.flags.no_site),
                                 "noBytecodeWrites": bool(sys.dont_write_bytecode)},
        }
        return ConfigurationObservation(_canonical(report))
    except Exception as error:
        # State observations still belong in the rejection if their check fails.
        try:
            _check_process_state(progress, before)
        except Exception:
            pass
        raise Rejected(str(error), progress) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure", required=True)
    parser.add_argument("--expected-closure-blob", required=True)
    args = parser.parse_args(argv)
    try:
        _require_isolation()
        raw = _read_absolute(Path(args.closure))
        report = observe_runner_configuration(raw, args.expected_closure_blob).report
        code = 0
    except Rejected as error:
        report, code = error.report, 2
    except Exception as error:
        report, code = _closed_report(REJECTED_RESULT, _progress(), str(error)), 2
    print(_canonical(report).decode("utf-8"), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

