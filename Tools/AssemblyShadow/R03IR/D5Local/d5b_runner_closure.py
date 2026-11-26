#!/usr/bin/env python3
"""AP2: verify a closed runner artifact snapshot; never run that runner.

Externally pinned closure proposal C follows A; C is not stored in A and is
not approval. Five reviewed runner-owned files and the AP1 envelope are bound
to a bounded checkout observation. This does not establish candidate import
isolation, live remote refs, source-data admission, Q or continuous custody.
Invoke with trusted Python -I -S -B. Only the blob-pinned AP1 verifier helper
is loaded as code; candidate wrapper/writer/preflight remain inert bytes.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from types import ModuleType
from typing import NamedTuple

KIND = "R03D5BRunnerClosureProposalV1"
SUCCESS_RESULT = "RunnerArtifactClosureObserved_NoExecutionAuthority"
REJECTED_RESULT = "RunnerArtifactClosureRejected_NoExecutionAuthority"
AP1_HELPER_BLOB = "ecf36a7a51f1750c6e8425ee79e9ac8938102b54"
AP1_HELPER_NAME = "d5b_activation_publication.py"
LOCAL = "Tools/AssemblyShadow/R03IR/D5Local/"
ADMISSION = "Tools/AssemblyShadow/R03IR/D5Admission/"
WRAPPER_PATH = LOCAL + "run_d5_local.py"
WRITER_PATH = LOCAL + "d5b_local_admission.py"
PREFLIGHT_PATH = ADMISSION + "d5b_rr5_source_preflight.py"
PLAN_PATH = LOCAL + "d5b_local_admission_plan_v1.json"
PROFILE_PATH = ADMISSION + "d5b_rr5_source_preflight_v1.json"
ENVELOPE_PATH = LOCAL + "d5b_activation_publication_proposal_v1.json"
FIXED_FILES = {
    WRAPPER_PATH: ("entryPoint", "519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39"),
    PREFLIGHT_PATH: ("importedModule", "81e7c3a2eaccb77bff2515c91b173558e4eeba2f"),
    PLAN_PATH: ("runnerPlan", "5c0ab7a6d788ebd5adf57f1fddc567ba700632e9"),
    PROFILE_PATH: ("runnerSourceProfile", "9956ea49656dc8337f9ab177c40faf29ea20c397"),
}
SOURCE_ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
HISTORY_ROLES = ("originalS", "b1EvidenceBase", "b1Oneuse12",
                 "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight")
MAX_FILE_BYTES = 1024 * 1024
MAX_CHECKOUT_FILE_BYTES = 256 * 1024 * 1024
MAX_CHECKOUT_BYTES = 4 * 1024 * 1024 * 1024
MAX_CHECKOUT_ENTRIES = 100000
MAX_TREE_DEPTH = 64
ORIGIN_URLS = frozenset({
    "https://github.com/night-outlook/hybridclr_demo",
    "https://github.com/night-outlook/hybridclr_demo.git",
    "git@github.com:night-outlook/hybridclr_demo",
    "git@github.com:night-outlook/hybridclr_demo.git",
    "ssh://git@github.com/night-outlook/hybridclr_demo",
    "ssh://git@github.com/night-outlook/hybridclr_demo.git",
})


class Rejected(ValueError):
    """The closed artifact observation was not established."""


def _need(ok: bool, reason: str) -> None:
    if not ok:
        raise Rejected(reason)


def git_blob(raw: bytes) -> str:
    _need(type(raw) is bytes, "Git blob input must be bytes")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _sha(value: object) -> str:
    _need(type(value) is str and len(value) == 40 and
          all(c in "0123456789abcdef" for c in value), "Expected an exact Git SHA-1")
    return value


def _path_literal(value: object) -> Path:
    _need(type(value) is str and value.startswith("/") and "\0" not in value,
          "Locations must be absolute path strings")
    path = Path(value)
    _need(str(path) == value and ".." not in path.parts,
          "Locations must use normalized absolute spelling")
    return path


def _directory(value: str) -> tuple[Path, tuple[int, int]]:
    path = _path_literal(value)
    try:
        resolved = path.resolve(strict=True)
    except RuntimeError as error:
        raise Rejected("Directory resolution contains an unsupported loop") from error
    _need(resolved == path, "Directory path contains an alias or symlink")
    observed = path.lstat()
    _need(stat.S_ISDIR(observed.st_mode), "Location must be an existing directory")
    return path, (observed.st_dev, observed.st_ino)


def _separate(left: Path, right: Path) -> bool:
    if left == right or left in right.parents or right in left.parents:
        return False
    # Also compare ancestor identities: distinct path spellings can resolve
    # to the same directory on filesystems with aliases or case folding.
    left_identity = _directory(str(left))[1]
    right_identity = _directory(str(right))[1]
    return (left_identity not in {_directory(str(p))[1] for p in (right, *right.parents)} and
            right_identity not in {_directory(str(p))[1] for p in (left, *left.parents)})


def _locations_shape(locations: object) -> dict:
    _need(type(locations) is dict and set(locations) == {
        "runnerRoot", "workspace", "historicalRoots", "evidenceParent"},
        "Complete runner/workspace/history/output locations required")
    history = locations["historicalRoots"]
    _need(type(history) is dict and set(history) == set(HISTORY_ROLES),
          "All six historical location roles are required")
    for value in [locations["runnerRoot"], locations["workspace"],
                  locations["evidenceParent"], *history.values()]:
        _path_literal(value)
    return {"runnerRoot": locations["runnerRoot"], "workspace": locations["workspace"],
            "historicalRoots": {role: history[role] for role in HISTORY_ROLES},
            "evidenceParent": locations["evidenceParent"]}


def _observe_locations(locations: dict) -> dict:
    named = {"runnerRoot": locations["runnerRoot"], "workspace": locations["workspace"],
             "evidenceParent": locations["evidenceParent"],
             **{"history:" + k: v for k, v in locations["historicalRoots"].items()}}
    workspace = _path_literal(locations["workspace"])
    named.update({"source:" + role: str(workspace / role) for role in SOURCE_ROLES})
    observed = {role: _directory(value) for role, value in named.items()}
    runner = observed["runnerRoot"][0]
    for role, (path, identity) in observed.items():
        if role != "runnerRoot":
            _need(_separate(runner, path) and identity != observed["runnerRoot"][1],
                  "Runner checkout overlaps a protected location")
    parent = observed["evidenceParent"][0]
    for role in ["workspace", *("history:" + role for role in HISTORY_ROLES)]:
        _need(_separate(parent, observed[role][0]) and
              observed["evidenceParent"][1] != observed[role][1],
              "Evidence parent overlaps source or historical locations")
    return {role: {"path": str(path), "device": identity[0], "inode": identity[1]}
            for role, (path, identity) in observed.items()}


def _fingerprint(value: os.stat_result) -> tuple:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _read_relative(root_fd: int, relative: str) -> tuple[bytes, tuple]:
    """Bounded no-follow reads with entry reobservation, not a namespace lock."""
    parts = relative.split("/")
    _need(parts and all(part not in ("", ".", "..", ".git") and
                       "\\" not in part and "\0" not in part for part in parts),
          "Unsupported relative artifact path")
    _need(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
          "No-follow directory-descriptor reads are required")
    opened, chain = [], []
    parent, leaf = root_fd, None
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            opened.append(child)
            identity = os.fstat(child)
            _need(stat.S_ISDIR(identity.st_mode), "Artifact ancestor is not a directory")
            chain.append((parent, part, (identity.st_dev, identity.st_ino)))
            parent = child
        leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(leaf)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
              before.st_size <= MAX_FILE_BYTES and before.st_mode & 0o111 == 0,
              "Artifact must be bounded, single-link, non-executable regular bytes")
        chunks, size = [], 0
        while True:
            chunk = os.read(leaf, min(65536, MAX_FILE_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            _need(size <= MAX_FILE_BYTES, "Artifact exceeded the byte bound")
        after = os.fstat(leaf)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        _need(_fingerprint(before) == _fingerprint(after) == _fingerprint(named) and
              size == before.st_size, "Artifact identity or bytes changed during read")
        for parent_fd, part, identity in chain:
            current = os.stat(part, dir_fd=parent_fd, follow_symlinks=False)
            _need(stat.S_ISDIR(current.st_mode) and
                  (current.st_dev, current.st_ino) == identity,
                  "Artifact ancestor changed during read")
        return b"".join(chunks), _fingerprint(before)
    finally:
        if leaf is not None:
            os.close(leaf)
        for descriptor in reversed(opened):
            os.close(descriptor)


def _read_absolute(path: Path) -> bytes:
    _need(path.is_absolute(), "Input file must use an absolute path")
    parent, identity = _directory(str(path.parent))
    descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        _need((opened.st_dev, opened.st_ino) == identity, "Input parent changed")
        raw, _ = _read_relative(descriptor, path.name)
        _need(_directory(str(parent))[1] == identity, "Input parent changed after read")
        return raw
    finally:
        os.close(descriptor)


def _helper() -> ModuleType:
    # Reviewed verifier code, not a candidate import. Check bytes before
    # compile/exec; ambient module-name lookup/cache cannot select AP1 here.
    path = Path(__file__).resolve().with_name(AP1_HELPER_NAME)
    raw = _read_absolute(path)
    _need(git_blob(raw) == AP1_HELPER_BLOB, "AP1 verifier helper differs from reviewed R2 bytes")
    module = ModuleType("_ap2_reviewed_ap1")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def _catalog(git, tree: str, publication: dict) -> dict:
    expected = dict(FIXED_FILES)
    expected[WRITER_PATH] = ("admissionModule", publication["runnerWriterGitBlob"])
    expected[ENVELOPE_PATH] = ("closedPublicationProposal", publication["proposalEnvelopeGitBlob"])
    result = {}
    for path in sorted(expected):
        role, blob = expected[path]
        _need(git.entry(tree, path) == ("100644", blob), "Runner object closure mismatch: " + path)
        _need(len(git.object(blob, "blob")) <= MAX_FILE_BYTES, "Runner object exceeds file bound")
        result[path] = {"role": role, "mode": "100644", "gitBlob": blob}
    return result


def _proposal(helper: ModuleType, repo: Path, source_commit: str,
              runner_commit: str, runner_ref: str, locations: dict) -> dict:
    _sha(source_commit)
    _sha(runner_commit)
    locations = _locations_shape(locations)
    _need(isinstance(repo, Path) and repo.is_absolute() and str(repo) == locations["runnerRoot"],
          "Proposal object repository must equal its declared absolute runner root")
    publication = helper.audit_publication(repo, source_commit, runner_commit,
                                           helper.SOURCE_REF, runner_ref)
    git = helper._Git(repo)
    tree, _ = git.commit(runner_commit)
    return {
        "schemaVersion": 1, "kind": KIND,
        "sourcePins": {"hybridclr_demo": source_commit, **helper.SOURCE_PINS},
        "sourceRef": helper.SOURCE_REF,
        "runner": {"repository": "night-outlook/hybridclr_demo",
                   "commit": runner_commit, "ref": runner_ref},
        "proposalEnvelopeGitBlob": publication["proposalEnvelopeGitBlob"],
        "entryPoint": WRAPPER_PATH, "files": _catalog(git, tree, publication),
        "repositoryLocalImports": {
            "run_d5_local": WRAPPER_PATH,
            "d5b_local_admission": WRITER_PATH,
            "d5b_rr5_source_preflight": PREFLIGHT_PATH,
        },
        "locations": locations, "scope": "ArtifactSnapshotOnly_NoCandidateImports",
        "runtimeImportIsolationVerified": False, "authorization": dict(helper.CLOSED_AUTHORITY),
    }


def make_closure_proposal(repo: Path, source_commit: str, runner_commit: str,
                          runner_ref: str, locations: dict) -> dict:
    """Construct C from local Git objects. Location spelling, not custody, is bound.

    Writes nothing. C follows A, outside A; later Q must separately bind C.
    """
    try:
        return _proposal(_helper(), repo, source_commit, runner_commit, runner_ref, locations)
    except (OSError, ValueError, UnicodeError) as error:
        raise Rejected(str(error)) from error


def _tree_inventory(git, root_tree: str) -> dict:
    """Read verified raw tree metadata, without Git worktree comparison."""
    inventory = {}
    pending = [("", root_tree, 0)]
    while pending:
        prefix, tree, depth = pending.pop()
        _need(depth <= MAX_TREE_DEPTH, "Runner tree exceeds supported depth")
        for name_bytes, (mode, blob) in git.tree(tree).items():
            name = name_bytes.decode("utf-8")
            _need(name != ".git" and mode in ("40000", "100644", "100755", "120000"),
                  "Unsupported runner tree name, mode or submodule")
            path = prefix + name
            inventory[path] = (mode, blob)
            _need(len(inventory) <= MAX_CHECKOUT_ENTRIES, "Runner tree exceeds entry bound")
            if mode == "40000":
                pending.append((path + "/", blob, depth + 1))
    return inventory


def _hash_worktree_file(parent_fd: int, name: str, mode: str, budget: dict) -> tuple[str, tuple]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    try:
        before = os.fstat(descriptor)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
              bool(before.st_mode & stat.S_IXUSR) == (mode == "100755") and
              before.st_size <= MAX_CHECKOUT_FILE_BYTES,
              "Unsupported tracked regular-file type, links, mode or size")
        budget["bytes"] += before.st_size
        _need(budget["bytes"] <= MAX_CHECKOUT_BYTES, "Runner checkout exceeds total byte bound")
        digest = hashlib.sha1(b"blob " + str(before.st_size).encode("ascii") + b"\0")
        size = 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            size += len(chunk)
            _need(size <= before.st_size, "Tracked file grew during hashing")
            digest.update(chunk)
        after = os.fstat(descriptor)
        named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        _need(size == before.st_size and
              _fingerprint(before) == _fingerprint(after) == _fingerprint(named),
              "Tracked file identity changed during hashing")
        return digest.hexdigest(), _fingerprint(before)
    finally:
        os.close(descriptor)


def _worktree_observation(root: Path, inventory: dict, root_identity: tuple) -> dict:
    """Compare all tracked bytes and exact entries with verifier-owned reads.

    No Git status/diff/hash-object/filter operation is used. Unrelated tracked
    symlinks are checked as literal link text, never followed. Declared runner
    artifacts have the stricter regular-only contract checked separately.
    """
    children = {"": {}}
    for path, entry in inventory.items():
        parent, _slash, name = path.rpartition("/")
        children.setdefault(parent, {})[name] = entry
        if entry[0] == "40000":
            children.setdefault(path, {})
    aggregate = hashlib.sha256()
    budget = {"bytes": 0, "entries": 0, "files": 0}

    def visit(descriptor: int, prefix: str, depth: int) -> None:
        _need(depth <= MAX_TREE_DEPTH, "Runner filesystem exceeds supported depth")
        before = os.fstat(descriptor)
        names = set()
        with os.scandir(descriptor) as listing:
            for entry in listing:
                if not prefix and entry.name == ".git":
                    continue
                names.add(entry.name)
                budget["entries"] += 1
                _need(budget["entries"] <= MAX_CHECKOUT_ENTRIES,
                      "Runner filesystem exceeds entry bound")
        expected = children[prefix]
        _need(names == set(expected), "Runner checkout has missing, untracked or ignored entries")
        for name in sorted(names):
            mode, wanted_blob = expected[name]
            path = prefix + "/" + name if prefix else name
            if mode == "40000":
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                try:
                    child_identity = os.fstat(child)
                    visit(child, path, depth + 1)
                    named = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                    _need(stat.S_ISDIR(named.st_mode) and
                          (named.st_dev, named.st_ino) == (child_identity.st_dev, child_identity.st_ino),
                          "Tracked directory entry changed during observation")
                finally:
                    os.close(child)
                continue
            budget["files"] += 1
            if mode == "120000":
                before_link = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                _need(stat.S_ISLNK(before_link.st_mode) and before_link.st_nlink == 1,
                      "Tracked link has unsupported type or link count")
                raw = os.fsencode(os.readlink(name, dir_fd=descriptor))
                _need(len(raw) <= MAX_CHECKOUT_FILE_BYTES, "Tracked link exceeds byte bound")
                budget["bytes"] += len(raw)
                _need(budget["bytes"] <= MAX_CHECKOUT_BYTES, "Runner checkout exceeds total byte bound")
                after_link = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                _need(_fingerprint(before_link) == _fingerprint(after_link), "Tracked link changed")
                actual_blob, fingerprint = git_blob(raw), _fingerprint(before_link)
            else:
                actual_blob, fingerprint = _hash_worktree_file(descriptor, name, mode, budget)
            _need(actual_blob == wanted_blob, "Tracked working bytes differ from A: " + path)
            aggregate.update(canonical_bytes({"path": path, "mode": mode,
                                               "blob": actual_blob, "identity": fingerprint}))
        after = os.fstat(descriptor)
        _need(_fingerprint(before) == _fingerprint(after), "Tracked directory changed during scan")
        aggregate.update(canonical_bytes({"directory": prefix, "identity": _fingerprint(before)}))

    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(root_fd)
        _need((opened.st_dev, opened.st_ino) == root_identity, "Runner root changed before scan")
        visit(root_fd, "", 0)
        _need(_directory(str(root))[1] == root_identity, "Runner root changed after scan")
    finally:
        os.close(root_fd)
    return {"worktreeInventorySha256": aggregate.hexdigest(), "worktreeFiles": budget["files"],
            "worktreeEntries": budget["entries"], "worktreeBytes": budget["bytes"]}


def _checkout_observation(helper: ModuleType, root: Path, runner: dict) -> dict:
    _, root_identity = _directory(str(root))
    git_dir, _ = _directory(str(root / ".git"))
    _directory(str(git_dir / "objects"))
    _directory(str(git_dir / "refs"))
    for relative in ("shallow", "info/grafts", "objects/info/alternates"):
        _need(not os.path.lexists(git_dir / relative),
              "Shallow, grafted and alternate-object stores are unsupported")
    git = helper._Git(root)
    _need(git.read("rev-parse", "--is-bare-repository").strip() == b"false",
          "Runner must be an ordinary working checkout")
    absolute_git_dir = git.read("rev-parse", "--absolute-git-dir").decode("utf-8").strip()
    common_dir = git.read("rev-parse", "--path-format=absolute", "--git-common-dir").decode("utf-8").strip()
    _need(absolute_git_dir == common_dir == str(git_dir),
          "Runner must have its own ordinary Git administrative directory")
    config = git.read("config", "--local", "--no-includes", "--null", "--list")
    for item in config.split(b"\0"):
        if not item:
            continue
        key = item.split(b"\n", 1)[0].lower()
        _need(not key.startswith((b"filter.", b"url.")) and key not in {
            b"core.worktree", b"core.ignorestat", b"core.sparsecheckout",
            b"core.sparsecheckoutcone", b"core.splitindex", b"diff.external"},
            "Unsupported Git filter, rewrite, sparse or hidden-status configuration")
    origins = git.read("config", "--local", "--no-includes", "--get-all", "remote.origin.url").decode("utf-8").splitlines()
    _need(len(origins) == 1 and origins[0] in ORIGIN_URLS,
          "Runner origin must name the canonical demo repository exactly")
    head = git.read("rev-parse", "--verify", "HEAD").decode("ascii").strip()
    branch = git.read("symbolic-ref", "--quiet", "HEAD").decode("utf-8").strip()
    _need(head == runner["commit"] and branch == runner["ref"] and
          git.ref(runner["ref"]) == runner["commit"],
          "Runner HEAD and checked-out branch must match its exact identity")
    flags = git.read("ls-files", "-v", "-z")
    _need(all(item.startswith(b"H ") for item in flags.split(b"\0") if item),
          "Runner index has skipped, assumed, unmerged or unsupported entries")
    stages = git.read("ls-files", "--stage", "-z")
    index = {}
    for item in stages.split(b"\0"):
        if not item:
            continue
        metadata, separator, _path = item.partition(b"\t")
        fields = metadata.split(b" ")
        _need(separator and len(fields) == 3 and fields[2] == b"0" and fields[0] != b"160000",
              "Runner submodules or unmerged index entries are unsupported")
        path = _path.decode("utf-8")
        _need(path not in index, "Duplicate runner index path")
        index[path] = (fields[0].decode("ascii"), fields[1].decode("ascii"))
    tree, _ = git.commit(runner["commit"])
    inventory = _tree_inventory(git, tree)
    _need(index == {path: entry for path, entry in inventory.items() if entry[0] != "40000"},
          "Runner index does not match the exact committed tree")
    worktree = _worktree_observation(root, inventory, root_identity)
    return {"head": head, "branch": branch, "origin": origins[0],
            "gitDir": absolute_git_dir, "commonDir": common_dir,
            "configSha256": hashlib.sha256(config).hexdigest(),
            "indexFlagsSha256": hashlib.sha256(flags).hexdigest(),
            "indexStagesSha256": hashlib.sha256(stages).hexdigest(), **worktree}


class BundleFile(NamedTuple):
    path: str
    git_blob: str
    raw: bytes


@dataclass(frozen=True)
class VerifiedBundle:
    files: tuple[BundleFile, ...]
    _report_json: bytes

    @property
    def report(self) -> dict:
        # Presentation changes cannot modify the stored observation bytes.
        return json.loads(self._report_json)


def _closed_report(result: str) -> dict:
    return {
        "schemaVersion": 1, "kind": "R03D5BRunnerClosureObservationV1", "result": result,
        "runnerArtifactClosureVerified": False, "runnerCheckoutObservationVerified": False,
        "runtimeImportIsolationVerified": False, "runnerExecutableClosureVerified": False,
        "exclusiveCustodyVerified": False, "liveRemoteRefsVerified": False,
        "sourceDataInputsVerified": False, "currentMacInputsVerified": False,
        "executionAuthorityVerified": False, "candidateWriterExecutedOrImported": False,
        "outputCreated": False, "networkUsed": False, "UnityOrPlayerExecuted": False,
        "approvedEnvelopeGitBlob": None, "independentlyReviewedExecutableAdmission": "Pending",
        "explicitUserLocalApproval": "NotAuthorized", "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "D5BLocalExecution": "NotAuthorized", "D5LocalValidation": "NotAuthorized",
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
        "allowNativeBuild": False, "allowPlayerLaunch": False,
        "realUnityBuild": "NotRun", "realPlayerCellsPassed": 0, "realPlayerCellsNoCoverage": 18,
    }


def _verify(raw: bytes, expected_blob: str) -> VerifiedBundle:
    _sha(expected_blob)
    _need(type(raw) is bytes and len(raw) <= MAX_FILE_BYTES and git_blob(raw) == expected_blob,
          "Closure bytes do not match the external exact blob pin")
    helper = _helper()
    closure = helper.strict_json_object(raw)
    _need(type(closure.get("sourcePins")) is dict and type(closure.get("runner")) is dict,
          "Closure requires explicit source and runner identities")
    locations = _locations_shape(closure.get("locations"))
    root = _path_literal(locations["runnerRoot"])
    runner = closure["runner"]
    _need(set(runner) == {"repository", "commit", "ref"}, "Runner identity fields changed")
    _sha(runner["commit"])
    source_commit = _sha(closure["sourcePins"].get("hybridclr_demo"))
    before_locations = _observe_locations(locations)
    before_checkout = _checkout_observation(helper, root, runner)
    expected = _proposal(helper, root, source_commit, runner["commit"], runner["ref"], locations)
    helper._exact_value(closure, expected, "Runner closure proposal")
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    snapshots, fingerprints = [], {}
    try:
        opened = os.fstat(root_fd)
        _need((opened.st_dev, opened.st_ino) ==
              (before_locations["runnerRoot"]["device"], before_locations["runnerRoot"]["inode"]),
              "Runner root changed before snapshot")
        for path, specification in sorted(expected["files"].items()):
            content, fingerprint = _read_relative(root_fd, path)
            _need(git_blob(content) == specification["gitBlob"],
                  "Runner working artifact differs from pinned Git bytes: " + path)
            snapshots.append(BundleFile(path, specification["gitBlob"], content))
            fingerprints[path] = fingerprint
        # Recheck artifacts, refs, HEAD, index/config, worktree inventory and locations.
        # The snapshot is not permission to subsequently execute these bytes.
        for item in snapshots:
            content, fingerprint = _read_relative(root_fd, item.path)
            _need(content == item.raw and fingerprint == fingerprints[item.path],
                  "Runner artifact changed across snapshot observations")
        _need(_proposal(helper, root, source_commit, runner["commit"], runner["ref"], locations)
              == expected, "Runner object publication changed across observations")
        _need(_checkout_observation(helper, root, runner) == before_checkout,
              "Runner checkout identity/config/index changed across observations")
        _need(_observe_locations(locations) == before_locations,
              "Runner or protected location changed across observations")
    finally:
        os.close(root_fd)
    report = {**_closed_report(SUCCESS_RESULT),
              "runnerArtifactClosureVerified": True, "runnerCheckoutObservationVerified": True,
              "closureProposalGitBlob": expected_blob, "sourcePins": expected["sourcePins"],
              "runner": dict(runner), "observedCheckout": before_checkout,
              "observedLocations": before_locations, "sameSnapshotAtRecheck": True,
              "declaredRepositoryLocalFileCount": len(snapshots),
              "reviewedVerifierHelperGitBlob": AP1_HELPER_BLOB,
              "candidateLiteralProposalBlob": expected["proposalEnvelopeGitBlob"],
              "files": [{"path": item.path, "gitBlob": item.git_blob,
                         "sha256": hashlib.sha256(item.raw).hexdigest(), "bytes": len(item.raw),
                         "observedDevice": fingerprints[item.path][0],
                         "observedInode": fingerprints[item.path][1]} for item in snapshots]}
    return VerifiedBundle(tuple(snapshots), canonical_bytes(report))


def verify_runner_closure(raw: bytes, expected_blob: str) -> VerifiedBundle:
    """Return inert bytes and closed observations from a trusted process.

    The external C pin is byte identity, not approval. No candidate module
    is loaded and this API has no runner execution operation.
    """
    try:
        return _verify(raw, expected_blob)
    except (OSError, ValueError, UnicodeError) as error:
        raise Rejected(str(error)) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure", required=True, type=Path)
    parser.add_argument("--expected-closure-blob", required=True)
    args = parser.parse_args(argv)
    try:
        _need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
              "Invoke the trusted verifier with Python -I -S -B")
        raw = _read_absolute(args.closure)
        report = verify_runner_closure(raw, args.expected_closure_blob).report
        code = 0
    except (Rejected, OSError, ValueError, UnicodeError) as error:
        report = {**_closed_report(REJECTED_RESULT), "reason": str(error)}
        code = 2
    try:
        print(json.dumps(report, sort_keys=True, allow_nan=False), flush=True)
    except (OSError, ValueError):
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
