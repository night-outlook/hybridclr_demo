#!/usr/bin/env python3
"""AP5: observe five pinned checkouts and exact remote refs, without admission.

Use trusted Python -I -S -B. The externally pinned proposal selects identities,
not authority. Local raw-byte observations and HTTPS ref reads are repeated
sequentially; they are not atomic, continuous custody or an execution handoff.
No candidate Python is imported. Accepted AP1/AP2 verifier helpers are pinned.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from types import ModuleType

AP2_HELPER_NAME = "d5b_runner_closure.py"
AP2_HELPER_BLOB = "2535bc14c31f1ff2d73fdb8c7be1d7dab605d990"
KIND = "R03D5BFiveIdentityProposalV1"
SCOPE = "CheckoutAndLiveRefObservationOnly_NoExecutionAuthority"
SOURCE_REF = "refs/heads/codex/assembly-shadow-r01b-h1"
SOURCE_ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
IDENTITY_ROLES = (*SOURCE_ROLES, "runner")
CANDIDATE_NAMES = ("d5b_rr5_source_preflight", "d5b_local_admission", "run_d5_local")
MAX_BYTES = 1024 * 1024
MAX_REMOTE_BYTES = 65536
REMOTE_TIMEOUT_SECONDS = 30
SUCCESS_RESULT = "FiveIdentitiesObserved_NoExecutionAuthority"
REJECTED_RESULT = "FiveIdentitiesRejected_NoExecutionAuthority"


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
def _import_helper(progress: dict):
    """Authenticate AP2 before execution; its loader separately pins AP1."""
    path = Path(__file__).resolve(strict=True).with_name(AP2_HELPER_NAME)
    raw = _read_absolute(path)
    _need(_blob(raw) == AP2_HELPER_BLOB, "AP2 helper differs from the pinned AP5 bytes")
    helper = ModuleType("_ap5_verified_ap2")
    private_name = "_ap5_verified_ap2_" + format(id(helper), "x")
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


def _runner_ref(value: object) -> str:
    _need(type(value) is str and value.startswith("refs/heads/codex/") and
          len(value) <= 240 and value != SOURCE_REF,
          "Runner requires a distinct full codex branch ref")
    for part in value.split("/"):
        _need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", part) is not None and
              ".." not in part and not part.endswith((".", ".lock")),
              "Runner ref is outside the supported branch spelling")
    return value


def _proposal(ap2: ModuleType, ap1: ModuleType, raw: bytes) -> dict:
    value = ap1.strict_json_object(raw)
    pins = value.get("sourcePins")
    _need(type(pins) is dict and set(pins) == set(SOURCE_ROLES),
          "Exactly four source commit pins are required")
    pins = {role: _sha(pins[role]) for role in SOURCE_ROLES}
    runner = value.get("runner")
    _need(type(runner) is dict and set(runner) == {"repository", "commit", "ref"},
          "Runner identity fields changed")
    commit, ref = _sha(runner["commit"]), _runner_ref(runner["ref"])
    _need(commit != pins["hybridclr_demo"], "Runner and demo source commits must differ")
    locations = ap2._locations_shape(value.get("locations"))
    expected = {
        "schemaVersion": 1, "kind": KIND, "sourcePins": pins, "sourceRef": SOURCE_REF,
        "runner": {"repository": "night-outlook/hybridclr_demo", "commit": commit, "ref": ref},
        "locations": locations, "scope": SCOPE, "authorization": dict(ap1.CLOSED_AUTHORITY),
    }
    ap1._exact_value(value, expected, "Five-identity proposal")
    return expected


def _identities(proposal: dict) -> tuple[dict, ...]:
    workspace = Path(proposal["locations"]["workspace"])
    values = [{"role": role, "repository": "night-outlook/" + role,
               "root": str(workspace / role), "commit": proposal["sourcePins"][role],
               "ref": SOURCE_REF} for role in SOURCE_ROLES]
    values.append({"role": "runner", **proposal["runner"],
                   "root": proposal["locations"]["runnerRoot"]})
    return tuple(values)


def _observe_locations(ap2: ModuleType, proposal: dict, identities: tuple) -> dict:
    observed = ap2._observe_locations(proposal["locations"])
    roots = [Path(item["root"]) for item in identities]
    _need(all(ap2._separate(a, b) for i, a in enumerate(roots) for b in roots[i + 1:]),
          "Five checkout roots must be pairwise physically separate")
    workspace = Path(proposal["locations"]["workspace"])
    historical = [Path(value) for value in proposal["locations"]["historicalRoots"].values()]
    _need(all(ap2._separate(workspace, item) for item in historical),
          "Source workspace overlaps a declared historical location")
    history_identities = [ap2._directory(str(path))[1] for path in historical]
    _need(len(set(history_identities)) == len(historical),
          "Declared historical roles must name distinct physical roots")
    return observed


def _origins(repository: str) -> frozenset[str]:
    return frozenset(
        prefix + repository + suffix
        for prefix in ("https://github.com/", "git@github.com:", "ssh://git@github.com/")
        for suffix in ("", ".git")
    )


def _observe_checkout(ap2: ModuleType, ap1: ModuleType, identity: dict) -> dict:
    """Role-aware administration checks plus unchanged AP2 raw-byte scanning."""
    root = Path(identity["root"])
    _, root_identity = ap2._directory(str(root))
    git_dir, git_identity = ap2._directory(str(root / ".git"))
    admin = {"gitDir": {"device": git_identity[0], "inode": git_identity[1]}}
    for name in ("objects", "refs"):
        _, found = ap2._directory(str(git_dir / name))
        admin[name] = {"device": found[0], "inode": found[1]}
    for relative in ("shallow", "info/grafts", "objects/info/alternates"):
        _need(not os.path.lexists(git_dir / relative),
              "Shallow, grafted and alternate-object stores are unsupported")
    git = ap1._Git(root)
    _need(git.read("rev-parse", "--is-bare-repository").strip() == b"false",
          "Each identity requires an ordinary working checkout")
    absolute = git.read("rev-parse", "--absolute-git-dir").decode("utf-8").strip()
    common = git.read("rev-parse", "--path-format=absolute", "--git-common-dir").decode("utf-8").strip()
    _need(absolute == common == str(git_dir),
          "Each checkout must own its ordinary Git administrative directory")
    config = git.read("config", "--local", "--no-includes", "--null", "--list")
    for item in config.split(b"\0"):
        if item:
            key = item.split(b"\n", 1)[0].lower()
            _need(not key.startswith((b"filter.", b"url.")) and key not in {
                b"core.worktree", b"core.ignorestat", b"core.sparsecheckout",
                b"core.sparsecheckoutcone", b"core.splitindex", b"diff.external"},
                "Unsupported Git filter, rewrite, sparse or hidden-status configuration")
    origins = git.read("config", "--local", "--no-includes", "--get-all",
                       "remote.origin.url").decode("utf-8").splitlines()
    _need(len(origins) == 1 and origins[0] in _origins(identity["repository"]),
          "Checkout origin must name its canonical repository exactly")
    head = git.read("rev-parse", "--verify", "HEAD").decode("ascii").strip()
    branch = git.read("symbolic-ref", "--quiet", "HEAD").decode("utf-8").strip()
    _need(head == identity["commit"] and branch == identity["ref"] and
          git.ref(identity["ref"]) == identity["commit"],
          "Checkout HEAD and attached branch must match the exact proposed identity")
    flags = git.read("ls-files", "-v", "-z")
    _need(all(item.startswith(b"H ") for item in flags.split(b"\0") if item),
          "Index has skipped, assumed, unmerged or unsupported entries")
    stages = git.read("ls-files", "--stage", "-z")
    index = {}
    for item in stages.split(b"\0"):
        if not item:
            continue
        metadata, separator, path_raw = item.partition(b"\t")
        fields = metadata.split(b" ")
        _need(separator and len(fields) == 3 and fields[2] == b"0" and fields[0] != b"160000",
              "Submodules and unmerged index entries are unsupported")
        path = path_raw.decode("utf-8")
        _need(path not in index, "Duplicate index path")
        index[path] = (fields[0].decode("ascii"), fields[1].decode("ascii"))
    tree, parents = git.commit(identity["commit"])
    inventory = ap2._tree_inventory(git, tree)
    _need(index == {path: entry for path, entry in inventory.items() if entry[0] != "40000"},
          "Index does not match the exact committed tree")
    worktree = ap2._worktree_observation(root, inventory, root_identity)
    return {**identity, "head": head, "branch": branch, "tree": tree, "parents": list(parents),
            "origin": origins[0], "gitDir": absolute, "commonDir": common,
            "gitAdministrativeDirectoryIdentities": admin, "gitExecutable": git.command[0],
            "configSha256": hashlib.sha256(config).hexdigest(),
            "indexFlagsSha256": hashlib.sha256(flags).hexdigest(),
            "indexStagesSha256": hashlib.sha256(stages).hexdigest(), **worktree}


def _remote_invocation(identity: dict) -> tuple[list[str], dict[str, str]]:
    """No repository context, inherited config, caller endpoint or alternate transport."""
    executable = shutil.which("git", path=os.defpath)
    _need(executable is not None and Path(executable).is_absolute(),
          "A system Git executable is required")
    url = "https://github.com/" + identity["repository"] + ".git"
    command = [
        executable, "--no-replace-objects", "--literal-pathspecs", "--git-dir=" + os.devnull,
        "-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
        "-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull,
        "-c", "credential.helper=", "-c", "credential.interactive=false",
        "-c", "core.askPass=", "-c", "http.proxy=", "-c", "http.followRedirects=false",
        "-c", "http.sslVerify=true", "-c", "http.extraHeader=",
        "-c", "http.cookieFile=" + os.devnull, "-c", "http.saveCookies=false",
        "ls-remote", "--exit-code", "--refs", url, identity["ref"],
    ]
    environment = {
        "PATH": os.defpath, "LANG": "C", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_COUNT": "0",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
        "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
        "GIT_ATTR_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "https",
    }
    return command, environment


def _run_remote(command: list[str], environment: dict[str, str]):
    # Output size is validated after capture. Timeout and this validation do
    # not establish a hard bound on subprocess/OS memory consumption.
    return subprocess.run(command, input=b"", capture_output=True, cwd="/",
                          env=environment, timeout=REMOTE_TIMEOUT_SECONDS, check=False)


def _exact_remote_head(raw: bytes, ref: str, expected: str) -> str:
    _need(type(raw) is bytes and len(raw) <= MAX_REMOTE_BYTES,
          "Remote ref response must be bounded bytes")
    lines = raw.splitlines()
    _need(len(lines) == 1, "Require exactly one returned remote-ref row")
    fields = lines[0].split(b"\t")
    _need(len(fields) == 2 and fields[1] == ref.encode("ascii"),
          "Remote response does not name exactly the requested ref")
    actual = _sha(fields[0].decode("ascii"))
    _need(actual == expected, "Live remote ref differs from the proposed commit")
    return actual


def _observe_remote(identity: dict) -> dict:
    command, environment = _remote_invocation(identity)
    try:
        result = _run_remote(command, environment)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise _Problem("Exact remote Git query could not complete") from error
    _need(type(result.stdout) is bytes and type(result.stderr) is bytes and
          len(result.stdout) <= MAX_REMOTE_BYTES and len(result.stderr) <= MAX_REMOTE_BYTES,
          "Remote query output exceeds the supported response shape")
    _need(result.returncode == 0, "Exact remote Git query did not complete successfully")
    head = _exact_remote_head(result.stdout, identity["ref"], identity["commit"])
    return {"repository": identity["repository"], "ref": identity["ref"], "head": head,
            "url": "https://github.com/" + identity["repository"] + ".git",
            "requestedTransport": "https", "gitExecutable": command[0],
            "responseSha256": hashlib.sha256(result.stdout).hexdigest(),
            "responseBytes": len(result.stdout)}


def _local_pass(ap2: ModuleType, ap1: ModuleType, proposal: dict,
                identities: tuple, label: str, progress: dict) -> None:
    progress["localPassesAttempted"].append(label)
    found = progress["checkoutObservations"][label]
    for identity in identities:
        progress["checkoutCallsAttempted"].append({"pass": label, "role": identity["role"]})
        found[identity["role"]] = _observe_checkout(ap2, ap1, identity)
    admin = [directory for entry in found.values()
             for directory in entry["gitAdministrativeDirectoryIdentities"].values()]
    _need(len({(entry["device"], entry["inode"]) for entry in admin}) == 3 * len(identities),
          "Observed Git, objects and refs directory identities must be pairwise distinct")
    _need(found["runner"]["parents"] == [proposal["sourcePins"]["hybridclr_demo"]],
          "Runner must have the proposed demo source as its sole commit parent")
    progress["localPassesCompleted"].append(label)


def _remote_pass(identities: tuple, label: str, progress: dict) -> None:
    progress["remotePassesAttempted"].append(label)
    for identity in identities:
        progress["remoteCallsAttempted"].append({"pass": label, "role": identity["role"]})
        progress["remoteObservations"][label][identity["role"]] = _observe_remote(identity)
    progress["remotePassesCompleted"].append(label)


def _progress() -> dict:
    return {
        "trustedHelperRegistered": False, "trustedHelperRegistrationRemoved": False,
        "realSysPathUnchanged": True, "ambientCandidateModuleCacheUnchanged": True,
        "proposalSchemaValidated": False, "sourcePinsMatchAcceptedAP1SiblingPins": None,
        "locationObservations": {}, "checkoutObservations": {"before": {}, "after": {}},
        "remoteObservations": {"before": {}, "after": {}},
        "localPassesAttempted": [], "localPassesCompleted": [], "checkoutCallsAttempted": [],
        "remotePassesAttempted": [], "remotePassesCompleted": [], "remoteCallsAttempted": [],
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
          "Process import state changed during identity observation")


def _closed_report(result: str, progress: dict, reason: str | None = None) -> dict:
    success = result == SUCCESS_RESULT
    report = {
        "schemaVersion": 1, "kind": "R03D5BFiveIdentityObservationV1", "result": result,
        "fixedFiveIdentityObservationVerified": success,
        "fiveCheckoutObservationsMatched": success, "fiveLiveRefObservationsMatched": success,
        "runnerSoleParentObserved": progress["localPassesCompleted"] == ["before", "after"],
        "observationScope": "FiveProposedIdentitiesAtRepeatedSequentialObservationsOnly",
        "plannedReadOrder": ["locationsBefore", "localBefore", "remoteBefore",
                      "remoteAfter", "localAfter", "locationsAfter"],
        "remoteProcessLaunchMayHaveBeenAttempted": bool(progress["remoteCallsAttempted"]),
        "networkMayHaveBeenUsed": bool(progress["remoteCallsAttempted"]),
        "acceptedAP1SourceTupleVerified": False, "runnerPublicationRelationVerified": False,
        "AP2ArtifactCompatibilityVerified": False, "AP4ConfigurationCompatibilityVerified": False,
        "sourceSemanticPreflightVerified": False, "AP4CompositionVerified": False,
        "sourceDataInputsVerified": False, "runnerArtifactClosureVerified": False,
        "runtimeConfigurationReadsBound": False, "runtimeImportIsolationVerified": False,
        "runnerExecutableClosureVerified": False, "standardLibraryIdentityVerified": False,
        "rawGitIndexBytesVerified": False, "completeGitAdministrativeCustodyVerified": False,
        "simultaneousFiveIdentitySnapshotVerified": False, "remoteRefsFrozen": False,
        "exclusiveCustodyVerified": False, "continuousCustodyVerified": False,
        "currentMacInputsVerified": False, "trustedProcessRequired": True,
        "candidateWriterExecutedOrImported": False, "candidateEntryPointsInvoked": False,
        "admissionPreviewInvoked": False, "sourceInspectionEntryPointInvoked": False,
        "executionAuthorityVerified": False, "approvedEnvelopeGitBlob": None,
        "independentlyReviewedFiveIdentityObservation": "Pending",
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
class FiveIdentityObservation:
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


def observe_five_identities(raw: bytes, expected_proposal_blob: str) -> FiveIdentityObservation:
    """Observe an exact proposed tuple; accept no reports, transports or execution modes."""
    progress = _progress()
    before = _process_state()
    try:
        _require_isolation()
        _sha(expected_proposal_blob)
        _need(type(raw) is bytes and len(raw) <= MAX_BYTES and _blob(raw) == expected_proposal_blob,
              "Proposal bytes do not match their exact external pin")
        with _import_helper(progress) as ap2:
            ap1 = ap2._helper()
            proposal = _proposal(ap2, ap1, raw)
            progress["proposalSchemaValidated"] = True
            progress["sourcePinsMatchAcceptedAP1SiblingPins"] = all(
                proposal["sourcePins"][role] == pin for role, pin in ap1.SOURCE_PINS.items())
            identities = _identities(proposal)
            progress["locationObservations"]["before"] = _observe_locations(ap2, proposal, identities)
            _local_pass(ap2, ap1, proposal, identities, "before", progress)
            _remote_pass(identities, "before", progress)
            _remote_pass(identities, "after", progress)
            _need(progress["remoteObservations"]["before"] == progress["remoteObservations"]["after"],
                  "Remote responses changed between observation passes")
            _local_pass(ap2, ap1, proposal, identities, "after", progress)
            _need(progress["checkoutObservations"]["before"] == progress["checkoutObservations"]["after"],
                  "Checkout state changed between observation passes")
            progress["locationObservations"]["after"] = _observe_locations(ap2, proposal, identities)
            _need(progress["locationObservations"]["before"] == progress["locationObservations"]["after"],
                  "Declared locations changed between observation passes")
        _check_process_state(progress, before)
        report = {**_closed_report(SUCCESS_RESULT, progress),
                  "proposalGitBlob": expected_proposal_blob,
                  "pinnedAP2HelperGitBlob": AP2_HELPER_BLOB,
                  "pinnedAP1HelperGitBlob": ap2.AP1_HELPER_BLOB,
                  "sourcePins": proposal["sourcePins"], "runner": proposal["runner"],
                  "interpreterFlags": {"isolated": bool(sys.flags.isolated),
                                       "noSite": bool(sys.flags.no_site),
                                       "noBytecodeWrites": bool(sys.dont_write_bytecode)}}
        return FiveIdentityObservation(_canonical(report))
    except Exception as error:
        try:
            _check_process_state(progress, before)
        except Exception:
            pass
        raise Rejected(str(error), progress) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--expected-proposal-blob", required=True)
    args = parser.parse_args(argv)
    try:
        _require_isolation()
        raw = _read_absolute(Path(args.proposal))
        report = observe_five_identities(raw, args.expected_proposal_blob).report
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
