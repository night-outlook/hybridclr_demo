#!/usr/bin/env python3
"""AP3: observe imports from a verified snapshot; invoke no runner entry point.

Use trusted Python -I -S -B. AP2 remains an inert artifact verifier. This
separate observer initializes the exact reviewed preflight/writer/wrapper
source in private module dictionaries and reports their import bindings.
It is not a Python sandbox, runtime configuration adapter or Local authority.
"""
from __future__ import annotations

import __future__ as future
import argparse
import builtins
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import pathlib
import platform
import re
import shutil
import stat
import subprocess
import sys
from types import ModuleType
import typing
from typing import NamedTuple

AP2_HELPER_NAME = "d5b_runner_closure.py"
AP2_HELPER_BLOB = "2535bc14c31f1ff2d73fdb8c7be1d7dab605d990"
MAX_BYTES = 1024 * 1024
LOCAL = "Tools/AssemblyShadow/R03IR/D5Local/"
ADMISSION = "Tools/AssemblyShadow/R03IR/D5Admission/"
MODULE_PATHS = {
    "d5b_rr5_source_preflight": ADMISSION + "d5b_rr5_source_preflight.py",
    "d5b_local_admission": LOCAL + "d5b_local_admission.py",
    "run_d5_local": LOCAL + "run_d5_local.py",
}
PLAN_PATH = LOCAL + "d5b_local_admission_plan_v1.json"
PROFILE_PATH = ADMISSION + "d5b_rr5_source_preflight_v1.json"
ENVELOPE_PATH = LOCAL + "d5b_activation_publication_proposal_v1.json"
ARTIFACT_PATHS = frozenset((*MODULE_PATHS.values(), PLAN_PATH, PROFILE_PATH, ENVELOPE_PATH))
SUCCESS_RESULT = "RunnerImportBindingsObserved_NoExecutionAuthority"
REJECTED_RESULT = "RunnerImportBindingsRejected_NoExecutionAuthority"

# Exact direct import forms in the fixed reviewed source. There is no
# fallback to a finder, loader, sys.path, sys.modules or bytecode lookup.
IMPORT_FORMS = {
    "d5b_rr5_source_preflight": {
        "__future__": ("annotations",), "argparse": (), "hashlib": (),
        "json": (), "pathlib": ("Path",), "re": (), "subprocess": (), "sys": (),
    },
    "d5b_local_admission": {
        "__future__": ("annotations",), "argparse": (), "hashlib": (),
        "json": (), "os": (), "pathlib": ("Path",), "platform": (), "re": (),
        "shutil": (), "stat": (), "subprocess": (), "sys": (),
        "typing": ("Mapping",), "d5b_rr5_source_preflight": (),
    },
    "run_d5_local": {"d5b_local_admission": ("main",)},
}
TRUSTED_STDLIB = {
    "__future__": future, "argparse": argparse, "hashlib": hashlib,
    "json": json, "os": os, "pathlib": pathlib, "platform": platform,
    "re": re, "shutil": shutil, "stat": stat, "subprocess": subprocess,
    "typing": typing,
}


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


class SnapshotFile(NamedTuple):
    path: str
    git_blob: str
    raw: bytes


def _verified_snapshot(raw: bytes, expected_blob: str) -> tuple[dict, tuple, dict]:
    """Only this private path obtains snapshots; callers cannot supply bundles."""
    path = Path(__file__).resolve(strict=True).with_name(AP2_HELPER_NAME)
    helper_raw = _read_absolute(path)
    _need(_blob(helper_raw) == AP2_HELPER_BLOB, "AP2 verifier differs from reviewed bytes")
    helper = ModuleType("_ap3_verified_ap2")
    private_name = "_ap3_verified_ap2_" + format(id(helper), "x")
    _need(private_name not in sys.modules, "Trusted verifier module name is occupied")
    helper.__name__ = private_name
    helper.__file__ = str(path)
    helper.__package__ = ""
    helper.__cached__ = None
    # AP2's dataclass initialization needs its defining module registered.
    # This temporary trusted-helper name is unrelated to candidate imports.
    sys.modules[private_name] = helper
    try:
        exec(compile(helper_raw, str(path), "exec", dont_inherit=True, optimize=0), helper.__dict__)
        bundle = helper.verify_runner_closure(raw, expected_blob)
        records = tuple(SnapshotFile(item.path, item.git_blob, item.raw) for item in bundle.files)
        return json.loads(raw), records, bundle.report
    finally:
        _need(sys.modules.get(private_name) is helper, "Trusted verifier registry changed")
        del sys.modules[private_name]


def _validate_snapshot(closure: dict, records: tuple, artifact_report: dict) -> dict:
    _need(type(records) is tuple and len(records) == len(ARTIFACT_PATHS),
          "Exactly six snapshot records are required")
    _need(type(closure) is dict and type(closure.get("files")) is dict and
          set(closure["files"]) == ARTIFACT_PATHS, "Snapshot closure roster changed")
    indexed = {}
    for item in records:
        _need(type(item) is SnapshotFile and type(item.path) is str and
              item.path in ARTIFACT_PATHS and item.path not in indexed,
              "Snapshot has a duplicate, unexpected or malformed record")
        _need(type(item.raw) is bytes and len(item.raw) <= MAX_BYTES,
              "Snapshot record must contain bounded immutable bytes")
        wanted = closure["files"][item.path]
        _need(type(wanted) is dict and wanted.get("mode") == "100644" and
              _sha(item.git_blob) == wanted.get("gitBlob") == _blob(item.raw),
              "Snapshot bytes or identity differ from the verified closure")
        indexed[item.path] = item
    _need(set(indexed) == ARTIFACT_PATHS, "Incomplete snapshot")
    _need(type(artifact_report) is dict and
          artifact_report.get("result") == "RunnerArtifactClosureObserved_NoExecutionAuthority" and
          artifact_report.get("runnerArtifactClosureVerified") is True and
          artifact_report.get("runnerCheckoutObservationVerified") is True and
          artifact_report.get("candidateWriterExecutedOrImported") is False and
          artifact_report.get("executionAuthorityVerified") is False,
          "Expected a fresh closed AP2 observation")
    return indexed


def _private_importer(requester: str, modules: dict, sys_view: ModuleType, trace: list):
    def import_module(name, globals=None, locals=None, fromlist=(), level=0):
        forms = IMPORT_FORMS[requester]
        normalized = () if fromlist is None else fromlist
        _need(type(name) is str and name in forms and type(level) is int and level == 0 and
              type(normalized) in (tuple, list) and tuple(normalized) == forms[name],
              "Import is outside the reviewed direct form for " + requester)
        if name == "sys":
            selected, origin = sys_view, "PrivatePathOnlySysView"
        elif name in MODULE_PATHS:
            _need(name in modules, "Project dependency was not initialized in order")
            selected, origin = modules[name], "VerifiedSnapshotSource"
        else:
            _need(name in TRUSTED_STDLIB, "Unknown trusted standard-library dependency")
            selected, origin = TRUSTED_STDLIB[name], "TrustedPreloadedStandardLibrary"
        trace.append({"requester": requester, "name": name,
                      "fromlist": list(normalized), "level": level, "origin": origin})
        return selected
    return import_module


def _initialize_snapshot(closure: dict, records: tuple, artifact_report: dict, progress: dict) -> dict:
    files = _validate_snapshot(closure, records, artifact_report)
    progress["verifiedArtifactCount"] = len(files)
    root = Path(closure["locations"]["runnerRoot"])
    modules, code, trace = {}, {}, []
    sys_view = ModuleType("sys")
    sys_view.path = []
    for name, relative in MODULE_PATHS.items():
        item = files[relative]
        code[name] = compile(item.raw, str(root / relative), "exec", dont_inherit=True, optimize=0)
    progress["compiledModuleNames"] = list(code)
    for name, relative in MODULE_PATHS.items():
        module = ModuleType(name)
        module.__file__ = str(root / relative)
        module.__package__ = ""
        module.__cached__ = None
        module.__loader__ = None
        module.__spec__ = None
        namespace_builtins = dict(builtins.__dict__)
        namespace_builtins["__import__"] = _private_importer(name, modules, sys_view, trace)
        module.__dict__["__builtins__"] = namespace_builtins
        progress["initializationAttempted"].append(name)
        exec(code[name], module.__dict__)
        modules[name] = module
        progress["initializedModuleNames"].append(name)
    preflight = modules["d5b_rr5_source_preflight"]
    writer = modules["d5b_local_admission"]
    wrapper = modules["run_d5_local"]
    _need(writer.source is preflight and wrapper.main is writer.main and
          callable(writer.main) and writer.main.__globals__ is writer.__dict__,
          "Project import bindings do not select the initialized snapshot modules")
    _need(writer.HERE == root / LOCAL.rstrip("/") and
          preflight.ROOT == root / ADMISSION.rstrip("/") and
          writer.PLAN == root / PLAN_PATH and preflight.PROFILE == root / PROFILE_PATH,
          "Runner-relative path metadata differs from the verified mapping")
    _need(writer.PLAN_BLOB == files[PLAN_PATH].git_blob and
          preflight.PROFILE_BLOB == files[PROFILE_PATH].git_blob and
          writer.APPROVED_EXECUTION_ENVELOPE_BLOB == closure["proposalEnvelopeGitBlob"],
          "Initialized constants differ from the closed snapshot policy")
    _need(sys_view.path == [str(root / ADMISSION.rstrip("/"))],
          "Unexpected private sys.path initialization")
    return {
        "moduleSources": [{"name": name, "path": relative,
                           "gitBlob": files[relative].git_blob,
                           "sha256": hashlib.sha256(files[relative].raw).hexdigest(),
                           "bytes": len(files[relative].raw),
                           "compilationFilename": str(root / relative)}
                          for name, relative in MODULE_PATHS.items()],
        "dataArtifacts": [{"path": path, "gitBlob": files[path].git_blob,
                           "bytes": len(files[path].raw)}
                          for path in (PLAN_PATH, PROFILE_PATH, ENVELOPE_PATH)],
        "importTrace": trace,
        "projectBindings": {"writer.source": "d5b_rr5_source_preflight",
                            "wrapper.main": "d5b_local_admission.main"},
        "privateSysPath": list(sys_view.path),
        "candidateLiteralProposalBlob": closure["proposalEnvelopeGitBlob"],
    }


def _progress() -> dict:
    return {"verifiedArtifactCount": 0, "compiledModuleNames": [],
            "initializationAttempted": [], "initializedModuleNames": [],
            "realSysPathUnchanged": True, "ambientCandidateModuleCacheUnchanged": True}


def _closed_report(result: str, progress: dict, reason: str | None = None) -> dict:
    value = {
        "schemaVersion": 1, "kind": "R03D5BRunnerImportObservationV1", "result": result,
        "fixedModuleImportSelectionVerified": result == SUCCESS_RESULT,
        "candidateTopLevelCodeMayHaveRun": bool(progress["initializationAttempted"]),
        "candidateWriterImported": "d5b_local_admission" in progress["initializedModuleNames"],
        "candidateEntryPointsInvoked": False, "admissionPreviewInvoked": False,
        "candidateFunctionsInvoked": False, "planProfileFunctionsInvoked": False,
        "candidateModulesInstalledInSysModules": False,
        "ambientCandidateImportLookupUsed": False,
        "candidateBytecodeLoaded": False, "candidateBytecodeWritten": False,
        "runtimeImportIsolationVerified": False, "runtimeConfigurationReadsBound": False,
        "runnerExecutableClosureVerified": False, "standardLibraryIdentityVerified": False,
        "trustedProcessRequired": True, "pythonSandboxProvided": False,
        "checkoutRecheckedAfterModuleInitialization": False,
        "exclusiveCustodyVerified": False, "liveRemoteRefsVerified": False,
        "sourceDataInputsVerified": False, "currentMacInputsVerified": False,
        "executionAuthorityVerified": False, "approvedEnvelopeGitBlob": None,
        "independentlyReviewedImportBootstrap": "Pending",
        "independentlyReviewedExecutableAdmission": "Pending",
        "explicitUserLocalApproval": "NotAuthorized", "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "D5BLocalExecution": "NotAuthorized", "D5LocalValidation": "NotAuthorized",
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
        "allowNativeBuild": False, "allowPlayerLaunch": False,
        "UnityOrPlayerExecuted": False, "realUnityBuild": "NotRun",
        "realPlayerCellsPassed": 0, "realPlayerCellsNoCoverage": 18,
        "outputCreated": False, "networkUsed": False,
        **progress,
    }
    if reason is not None:
        value["reason"] = reason[:1600]
    return value


@dataclass(frozen=True)
class ImportObservation:
    _report_json: bytes

    @property
    def report(self) -> dict:
        return json.loads(self._report_json)


class Rejected(ValueError):
    """Closed rejection retaining conservative initialization progress."""

    def __init__(self, reason: str, progress: dict):
        super().__init__(reason)
        self._report_json = _canonical(_closed_report(REJECTED_RESULT, progress, reason))

    @property
    def report(self) -> dict:
        return json.loads(self._report_json)


def observe_runner_imports(raw: bytes, expected_closure_blob: str) -> ImportObservation:
    """Verify AP2, initialize fixed snapshot source privately, return data only.

    Flags are necessary preconditions, not attestation of an arbitrary process.
    No caller-supplied bundles, modules, import callbacks or runner functions
    are accepted. Plan/profile path reads and executable integration remain
    deferred; no candidate function is called by this observer.
    """
    progress = _progress()
    real_path, path_before = sys.path, tuple(sys.path)
    absent = object()
    cache_before = {name: sys.modules.get(name, absent) for name in MODULE_PATHS}
    try:
        _require_isolation()
        _sha(expected_closure_blob)
        _need(type(raw) is bytes and len(raw) <= MAX_BYTES and
              _blob(raw) == expected_closure_blob, "Closure bytes do not match their exact external pin")
        closure, records, artifact_report = _verified_snapshot(raw, expected_closure_blob)
        observed = _initialize_snapshot(closure, records, artifact_report, progress)
        progress["realSysPathUnchanged"] = sys.path is real_path and tuple(sys.path) == path_before
        progress["ambientCandidateModuleCacheUnchanged"] = all(
            sys.modules.get(name, absent) is prior for name, prior in cache_before.items())
        _need(progress["realSysPathUnchanged"] and progress["ambientCandidateModuleCacheUnchanged"],
              "Process import state changed during the observation")
        report = {
            **_closed_report(SUCCESS_RESULT, progress), **observed,
            "closureProposalGitBlob": expected_closure_blob,
            "reviewedAP2VerifierGitBlob": AP2_HELPER_BLOB,
            "sourcePins": closure["sourcePins"], "runner": closure["runner"],
            "artifactObservationScope": "AP2BeforeCandidateModuleInitializationOnly",
            "artifactObservation": artifact_report,
            "interpreterFlags": {"isolated": bool(sys.flags.isolated),
                                 "noSite": bool(sys.flags.no_site),
                                 "noBytecodeWrites": bool(sys.dont_write_bytecode)},
        }
        return ImportObservation(_canonical(report))
    except Exception as error:
        progress["realSysPathUnchanged"] = sys.path is real_path and tuple(sys.path) == path_before
        progress["ambientCandidateModuleCacheUnchanged"] = all(
            sys.modules.get(name, absent) is prior for name, prior in cache_before.items())
        raise Rejected(str(error), progress) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure", required=True, type=Path)
    parser.add_argument("--expected-closure-blob", required=True)
    args = parser.parse_args(argv)
    try:
        _require_isolation()
        raw = _read_absolute(args.closure)
        report = observe_runner_imports(raw, args.expected_closure_blob).report
        code = 0
    except Rejected as error:
        report, code = error.report, 2
    except Exception as error:
        report, code = _closed_report(REJECTED_RESULT, _progress(), str(error)), 2
    try:
        print(json.dumps(report, sort_keys=True, allow_nan=False), flush=True)
    except (OSError, ValueError):
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
