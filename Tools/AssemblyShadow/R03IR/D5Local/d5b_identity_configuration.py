#!/usr/bin/env python3
"""AP6: compose sequential identity and configuration observations without admission.

Use trusted Python -I -S -B. Two externally pinned immutable proposals must
agree before one fresh AP5 observation and one fresh AP4 configuration call.
The comparison concerns AP5's final observation and AP4's earlier AP2 snapshot;
it does not reobserve checkout state after candidate configuration consumers.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from types import ModuleType

HELPERS = {
    "identity": ("d5b_five_identity.py", "ab4e9cbf796d4ab91602a14a9294d3773e75879c"),
    "configuration": ("d5b_runner_configuration.py", "5263742017950a28bd9750eeeaefe50df4f4fa49"),
}
CANDIDATE_NAMES = ("d5b_rr5_source_preflight", "d5b_local_admission", "run_d5_local")
SHARED_PROPOSAL_FIELDS = ("sourcePins", "sourceRef", "runner", "locations", "authorization")
CHECKOUT_FIELDS = (
    "head", "branch", "origin", "gitDir", "commonDir", "configSha256",
    "indexFlagsSha256", "indexStagesSha256", "worktreeInventorySha256",
    "worktreeFiles", "worktreeEntries", "worktreeBytes",
)
MAX_BYTES = 1024 * 1024
SUCCESS_RESULT = "IdentityConfigurationObserved_NoExecutionAuthority"
REJECTED_RESULT = "IdentityConfigurationRejected_NoExecutionAuthority"
COMPARISON_SCOPE = "AP5AfterObservation_VersusAP2BeforeCandidateInitializationOnly"


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
    _need(os.name == "posix", "The reviewed no-follow observer requires POSIX")
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
def _load_helper(role: str, progress: dict):
    """Authenticate installed helper bytes before their private initialization."""
    record = progress["helperProgress"][role]
    record["loadAttempted"] = True
    filename, expected_blob = HELPERS[role]
    path = Path(__file__).resolve(strict=True).with_name(filename)
    raw = _read_absolute(path)
    _need(_blob(raw) == expected_blob, role + " helper differs from the pinned AP6 bytes")
    record["bytesVerified"] = True
    helper = ModuleType("_ap6_verified_" + role)
    private_name = helper.__name__ + "_" + format(id(helper), "x")
    _need(private_name not in sys.modules, "Trusted helper module name is occupied")
    helper.__name__, helper.__file__ = private_name, str(path)
    helper.__package__, helper.__cached__ = "", None
    sys.modules[private_name] = helper
    record["registrationAdded"] = True
    try:
        record["initializationAttempted"] = True
        exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), helper.__dict__)
        record["initializationCompleted"] = True
        yield helper
    finally:
        _need(sys.modules.get(private_name) is helper, "Trusted helper registry changed")
        del sys.modules[private_name]
        record["registrationRemoved"] = True


def _progress() -> dict:
    return {
        "inputPinsVerified": [], "closureProposalGitBlob": None, "identityProposalGitBlob": None,
        "helperProgress": {
            role: {"loadAttempted": False, "bytesVerified": False,
                   "registrationAdded": False, "initializationAttempted": False,
                   "initializationCompleted": False, "registrationRemoved": False}
            for role in HELPERS
        },
        "relationHelperProgress": {"trustedHelperRegistered": False,
                                   "trustedHelperRegistrationRemoved": False},
        "identityProposalSchemaValidated": False, "proposalFieldsMatched": False,
        "fixedAP1SiblingPinsMatched": False, "matchedProposalProjection": None,
        "sharedObservationsMatched": False,
        "comparisonCallsAttempted": [], "comparisonCallsCompleted": [],
        "stageCallsAttempted": [], "stageCallsReturned": [], "stageCallsCompleted": [],
        "observations": {"identity": None, "configuration": None},
        "realSysPathUnchanged": True, "ambientCandidateModuleCacheUnchanged": True,
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
          "Process import state changed during composed observation")


def _relation(ap5: ModuleType, closure_raw: bytes, identity_raw: bytes, progress: dict):
    """Check shared policy before either observation; AP4 later validates all of C."""
    with ap5._import_helper(progress["relationHelperProgress"]) as ap2:
        ap1 = ap2._helper()
        closure = ap1.strict_json_object(closure_raw)
        identity = ap5._proposal(ap2, ap1, identity_raw)
        progress["identityProposalSchemaValidated"] = True
        for field in SHARED_PROPOSAL_FIELDS:
            _need(field in closure, "Closure is missing shared field " + field)
            ap1._exact_value(closure[field], identity[field], "Proposal relation " + field)
        progress["proposalFieldsMatched"] = True
        for role, pin in ap1.SOURCE_PINS.items():
            ap1._exact_value(identity["sourcePins"][role], pin, "Fixed AP1 sibling pin " + role)
        progress["fixedAP1SiblingPinsMatched"] = True
        progress["matchedProposalProjection"] = json.loads(_canonical(
            {field: identity[field] for field in SHARED_PROPOSAL_FIELDS}))
    return closure, identity, ap1


def _observe_stage(role: str, helper: ModuleType, raw: bytes, pin: str,
                   proposal: dict, ap1: ModuleType, progress: dict) -> None:
    progress["stageCallsAttempted"].append(role)
    function = (helper.observe_five_identities if role == "identity"
                else helper.observe_runner_configuration)
    try:
        observation = function(raw, pin)
    except helper.Rejected as error:
        progress["observations"][role] = json.loads(_canonical(error.report))
        raise _Problem(role + " observation rejected: " + str(error)) from error
    progress["stageCallsReturned"].append(role)
    report = json.loads(_canonical(observation.report))
    progress["observations"][role] = report
    _need(report.get("result") == helper.SUCCESS_RESULT, role + " observation did not succeed")
    for field in ("sourcePins", "runner"):
        ap1._exact_value(report.get(field), proposal[field], role + " returned " + field)
    blob_field = "proposalGitBlob" if role == "identity" else "closureProposalGitBlob"
    ap1._exact_value(report.get(blob_field), pin, role + " returned proposal pin")
    for field, value in ap1.CLOSED_AUTHORITY.items():
        ap1._exact_value(report.get(field), value, role + " closed authority " + field)
    flags = (("fixedFiveIdentityObservationVerified", "fiveCheckoutObservationsMatched",
              "fiveLiveRefObservationsMatched", "runnerSoleParentObserved") if role == "identity"
             else ("fixedConfigurationConsumerReadsBound", "configurationConsumersValidated"))
    for field in flags:
        _need(report.get(field) is True, role + " incomplete observation " + field)
    progress["stageCallsCompleted"].append(role)


def _compare_observations(ap1: ModuleType, progress: dict) -> None:
    identity = progress["observations"]["identity"]
    configuration = progress["observations"]["configuration"]
    imports = configuration["importObservation"]
    _need(imports["artifactObservationScope"] == "AP2BeforeCandidateModuleInitializationOnly",
          "AP4 nested artifact observation scope changed")
    artifact = imports["artifactObservation"]
    _need(artifact["runnerArtifactClosureVerified"] is True and artifact["sameSnapshotAtRecheck"] is True,
          "AP4 did not return its completed AP2 artifact observations")
    progress["comparisonCallsAttempted"].append("runner")
    earlier_runner = identity["checkoutObservations"]["after"]["runner"]
    projected_runner = {field: earlier_runner[field] for field in CHECKOUT_FIELDS}
    ap1._exact_value(artifact["observedCheckout"], projected_runner,
                     "AP5-after runner versus AP2-before-initialization runner")
    progress["comparisonCallsCompleted"].append("runner")
    progress["comparisonCallsAttempted"].append("locations")
    ap1._exact_value(artifact["observedLocations"], identity["locationObservations"]["after"],
                     "AP5-after locations versus AP2-before-initialization locations")
    progress["comparisonCallsCompleted"].append("locations")
    progress["sharedObservationsMatched"] = True


def _possibility(progress: dict, role: str, field: str) -> bool:
    """Retain child facts; an unreported attempted call remains conservatively possible."""
    report = progress["observations"][role]
    if type(report) is dict and type(report.get(field)) is bool:
        return report[field]
    return role in progress["stageCallsAttempted"]


def _closed_report(result: str, progress: dict, reason: str | None = None) -> dict:
    success = result == SUCCESS_RESULT
    report = {
        "schemaVersion": 1, "kind": "R03D5BIdentityConfigurationObservationV1", "result": result,
        "sequentialIdentityConfigurationVerified": success,
        "proposalCompatibilityVerified": success,
        "plannedStageOrder": ["proposalRelation", "identity", "configuration", "comparePriorObservations"],
        "comparisonScope": COMPARISON_SCOPE, "comparedRunnerFields": list(CHECKOUT_FIELDS),
        "pinnedAP5HelperGitBlob": HELPERS["identity"][1],
        "pinnedAP4HelperGitBlob": HELPERS["configuration"][1],
        "networkMayHaveBeenUsed": _possibility(progress, "identity", "networkMayHaveBeenUsed"),
        "candidateTopLevelCodeMayHaveRun": _possibility(progress, "configuration", "candidateTopLevelCodeMayHaveRun"),
        "candidateConfigurationFunctionsMayHaveRun": _possibility(progress, "configuration", "candidateFunctionsInvoked"),
        "identityObservationRemainsCurrentDuringConfiguration": False,
        "checkoutRecheckedAfterConfigurationConsumers": False,
        "AP5AdministrativeRootsRecheckedByAP4": False,
        "sourceSemanticPreflightVerified": False, "sourceDataInputsVerified": False,
        "acceptedAP1SourceTupleApproved": False, "productionHttpsReachabilityQualified": False,
        "runtimeConfigurationReadsBound": False, "futureRuntimeConfigurationReadsBound": False,
        "runtimeImportIsolationVerified": False, "runnerExecutableClosureVerified": False,
        "simultaneousFiveIdentitySnapshotVerified": False, "remoteRefsFrozen": False,
        "exclusiveCustodyVerified": False, "continuousCustodyVerified": False,
        "completeGitAdministrativeCustodyVerified": False, "rawGitIndexBytesVerified": False,
        "currentMacInputsVerified": False, "standardLibraryIdentityVerified": False,
        "pythonSandboxProvided": False, "trustedProcessRequired": True,
        "candidateEntryPointsInvoked": False, "admissionPreviewInvoked": False,
        "sourceInspectionInvoked": False, "candidateApprovalConstantsChangedByAP6": False,
        "executionAuthorityVerified": False, "approvedEnvelopeGitBlob": None,
        "independentlyReviewedIdentityConfigurationComposition": "Pending",
        "independentlyReviewedExecutableAdmission": "Pending",
        "explicitUserLocalApproval": "NotAuthorized", "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "D5BLocalExecution": "NotAuthorized", "D5LocalValidation": "NotAuthorized",
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
        "allowNativeBuild": False, "allowPlayerLaunch": False, "UnityOrPlayerExecuted": False,
        "realUnityBuild": "NotRun", "realPlayerCellsPassed": 0, "realPlayerCellsNoCoverage": 18,
        "QExecutionAuthorized": False, "outputCreated": False, **progress,
    }
    if reason is not None:
        report["reason"] = reason[:1600]
    return report


@dataclass(frozen=True)
class IdentityConfigurationObservation:
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


def observe_identity_configuration(closure_raw: bytes, expected_closure_blob: str,
                                   identity_raw: bytes, expected_identity_blob: str
                                   ) -> IdentityConfigurationObservation:
    """Compose fresh fixed observers; accept no reports, transports, contexts or modes."""
    progress, before = _progress(), _process_state()
    try:
        _require_isolation()
        for role, raw, pin, field in (
            ("closure", closure_raw, expected_closure_blob, "closureProposalGitBlob"),
            ("identity", identity_raw, expected_identity_blob, "identityProposalGitBlob"),
        ):
            _sha(pin)
            _need(type(raw) is bytes and len(raw) <= MAX_BYTES and _blob(raw) == pin,
                  role + " bytes do not match their exact external pin")
            progress["inputPinsVerified"].append(role)
            progress[field] = pin
        with _load_helper("identity", progress) as ap5:
            with _load_helper("configuration", progress) as ap4:
                closure, identity, ap1 = _relation(ap5, closure_raw, identity_raw, progress)
                _observe_stage("identity", ap5, identity_raw, expected_identity_blob, identity, ap1, progress)
                _observe_stage("configuration", ap4, closure_raw, expected_closure_blob, closure, ap1, progress)
                _compare_observations(ap1, progress)
        _check_process_state(progress, before)
        return IdentityConfigurationObservation(_canonical(_closed_report(SUCCESS_RESULT, progress)))
    except Exception as error:
        try:
            _check_process_state(progress, before)
        except Exception:
            pass
        raise Rejected(str(error), progress) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure", required=True)
    parser.add_argument("--expected-closure-blob", required=True)
    parser.add_argument("--identity-proposal", required=True)
    parser.add_argument("--expected-identity-blob", required=True)
    args = parser.parse_args(argv)
    try:
        _require_isolation()
        closure_raw = _read_absolute(Path(args.closure))
        identity_raw = _read_absolute(Path(args.identity_proposal))
        report = observe_identity_configuration(
            closure_raw, args.expected_closure_blob, identity_raw, args.expected_identity_blob).report
        code = 0
    except Rejected as error:
        report, code = error.report, 2
    except Exception as error:
        report, code = _closed_report(REJECTED_RESULT, _progress(), str(error)), 2
    try:
        print(_canonical(report).decode("utf-8"), end="", flush=True)
    except (OSError, ValueError):
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
