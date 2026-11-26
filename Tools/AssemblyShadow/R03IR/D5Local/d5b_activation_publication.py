#!/usr/bin/env python3
"""AP1: source-only audit of a separate-runner publication PROPOSAL.

This reads local Git objects and local branch-ref observations. It performs
no fetch, push, checkout, working-tree write, candidate-code import, or Local
operation. A structurally valid proposal is NOT approval, an executable
envelope, proof of a live remote ref, or proof of any current physical input.

The runner fixture may differ from the reviewed source only by one literal
envelope-blob substitution and one new, explicitly non-authorizing proposal.
The existing writer rejects the proposal's distinct kind. Complete future
activation still needs separately reviewed runner identity/custody enforcement
and explicit user approval; neither is implemented or authenticated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Mapping


BRANCH = "codex/assembly-shadow-r01b-h1"
SOURCE_REF = "refs/heads/" + BRANCH
WRITER_PATH = "Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py"
R5_WRITER_BLOB = "99746fe64976da313cbd0e1625f0fcc5a67bca62"
ENVELOPE_PATH = (
    "Tools/AssemblyShadow/R03IR/D5Local/"
    "d5b_activation_publication_proposal_v1.json")
PROPOSAL_KIND = "R03D5BActivationPublicationProposalV1"
SUCCESS_RESULT = "ProposalPublicationStructureVerified_NoExecutionAuthority"
REJECTED_RESULT = "ProposalPublicationRejected_NoExecutionAuthority"
SOURCE_PINS = {
    "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "1268dd417ffe9090fcd9ea2d49542c97ed3cccb3",
}
CLOSED_AUTHORITY = {
    "approvedEnvelopeGitBlob": None,
    "independentlyReviewedExecutableAdmission": "Pending",
    "explicitUserLocalApproval": "NotAuthorized",
    "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
    "D5BLocalExecution": "NotAuthorized",
    "D5LocalValidation": "NotAuthorized",
    "R03Accepted": False,
    "H2Passed": False,
    "ReadyForHumanReviewGate": False,
    "allowNativeBuild": False,
    "allowPlayerLaunch": False,
}
CLOSED_WRITER_LINE = b"APPROVED_EXECUTION_ENVELOPE_BLOB = None\n"
SHA1 = re.compile(r"^[0-9a-f]{40}$")
REGULAR_MODES = {"100644", "100755"}
TREE_MODE = "40000"
PROPOSAL_MODE = "100644"


class Rejected(ValueError):
    """The proposal was not structurally verified; no authority was granted."""


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def _sha(value: str, label: str) -> str:
    need(type(value) is str and SHA1.fullmatch(value) is not None,
         label + " must be an exact lowercase 40-character SHA-1")
    return value


def _object_id(kind: str, raw: bytes) -> str:
    return hashlib.sha1(kind.encode("ascii") + b" " +
                        str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def git_blob(raw: bytes) -> str:
    need(type(raw) is bytes, "Git blob input must be bytes")
    return _object_id("blob", raw)


def strict_json_object(raw: bytes) -> dict:
    """Reject duplicate keys at every depth, non-finite numbers, and nonobjects."""
    need(type(raw) is bytes, "Proposal JSON input must be bytes")

    def pairs(items: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in items:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise Rejected("Non-finite JSON number: " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=constant)
    except Rejected:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Rejected("Invalid or excessively nested UTF-8 proposal JSON") from error
    need(type(value) is dict, "Proposal JSON must be an object")
    return value


def _exact_value(actual: object, expected: object, label: str) -> None:
    # Dict equality alone accepts True == 1 and False == 0.
    need(type(actual) is type(expected), label + " has the wrong JSON type")
    if type(expected) is dict:
        need(set(actual) == set(expected), label + " has unexpected JSON keys")
        for key in expected:
            _exact_value(actual[key], expected[key], label + "." + key)
    else:
        need(actual == expected, label + " does not match the closed proposal")


def proposal_envelope(source_commit: str) -> dict:
    """Return test/proposal data only. This is never an execution envelope."""
    _sha(source_commit, "Source commit")
    return {
        "schemaVersion": 1, "kind": PROPOSAL_KIND, "branch": BRANCH,
        "sourcePins": {"hybridclr_demo": source_commit, **SOURCE_PINS},
        "scope": "NoUnityOrPlayerLaunch",
        "authorization": dict(CLOSED_AUTHORITY),
    }


def proposal_writer_bytes(source_writer: bytes, envelope_blob: str) -> bytes:
    """Compute the sole allowed fixture delta; do not execute or write it."""
    _sha(envelope_blob, "Proposal envelope blob")
    need(type(source_writer) is bytes and
         git_blob(source_writer) == R5_WRITER_BLOB,
         "Source writer does not have the reviewed R5 Git blob")
    need(source_writer.count(CLOSED_WRITER_LINE) == 1,
         "Reviewed writer must contain one literal closed approval assignment")
    replacement = (b'APPROVED_EXECUTION_ENVELOPE_BLOB = "' +
                   envelope_blob.encode("ascii") + b'"\n')
    return source_writer.replace(CLOSED_WRITER_LINE, replacement, 1)


def _relative_path(value: str) -> str:
    need(type(value) is str and value and not value.startswith("/") and
         "\\" not in value and "\0" not in value and
         all(part not in ("", ".", "..", ".git") for part in value.split("/")),
         "Proposal path must be a safe relative Git path")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise Rejected("Proposal path must be valid UTF-8") from error
    need(value != WRITER_PATH and not value.startswith(WRITER_PATH + "/") and
         not WRITER_PATH.startswith(value + "/"),
         "Proposal path must be separate from the writer path")
    return value


class _Git:
    """Fixed read-only commands; no inherited Git config or command overrides."""

    def __init__(self, repo: Path):
        need(isinstance(repo, Path), "Repository must be a pathlib.Path")
        try:
            self.repo = repo.resolve(strict=True)
        except OSError as error:
            raise Rejected("Repository directory is unavailable") from error
        need(self.repo.is_dir(), "Repository must be a directory")
        executable = shutil.which("git", path=os.defpath)
        need(executable is not None, "A system Git executable is required")
        self.command = [
            executable, "--no-replace-objects", "--literal-pathspecs",
            "-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull,
            "-c", "core.attributesFile=" + os.devnull,
            "-c", "protocol.allow=never", "-C", str(self.repo),
        ]
        # No inherited GIT_DIR, alternates, config parameters, namespace,
        # replace-ref bases, external command paths, or remote helpers.
        self.environment = {
            "PATH": os.defpath, "LANG": "C", "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_COUNT": "0",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
            "GIT_ATTR_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "",
        }
        self.objects: dict[str, tuple[str, bytes]] = {}
        self.trees: dict[str, dict[bytes, tuple[str, str]]] = {}
        config = self.read("config", "--local", "--no-includes", "--null", "--list")
        for item in config.split(b"\0"):
            if not item:
                continue
            key = item.split(b"\n", 1)[0].lower()
            need(not key.startswith((b"include.", b"includeif.", b"extensions."))
                 and not key.endswith((b".promisor", b".partialclonefilter")),
                 "Git includes, extensions, and partial-clone configuration are unsupported")
        need(self.read("rev-parse", "--show-object-format").strip() == b"sha1",
             "AP1 requires SHA-1 Git objects")
        bare = self.read("rev-parse", "--is-bare-repository").strip()
        need(bare in (b"true", b"false"), "Invalid Git repository metadata")
        location = self.read("rev-parse", "--absolute-git-dir" if bare == b"true"
                             else "--show-toplevel").decode("utf-8").strip()
        need(Path(location).resolve(strict=True) == self.repo,
             "Repository input must name its root, not a discovered parent repository")

    def run(self, *arguments: str, input_bytes: bytes | None = None,
            accepted: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
        try:
            process = subprocess.run(
                self.command + list(arguments), input=input_bytes,
                capture_output=True, env=self.environment, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise Rejected("Read-only Git command could not complete") from error
        need(process.returncode in accepted,
             "Read-only Git command rejected input: " +
             process.stderr.decode("utf-8", errors="replace")[-400:].strip())
        return process

    def read(self, *arguments: str, input_bytes: bytes | None = None) -> bytes:
        return self.run(*arguments, input_bytes=input_bytes).stdout

    def ref(self, name: str) -> str:
        need(type(name) is str and name.startswith("refs/heads/"),
             "Publication refs must be full local branch refs")
        self.read("check-ref-format", name)
        symbolic = self.run("symbolic-ref", "--quiet", name, accepted=(0, 1))
        need(symbolic.returncode == 1, "Publication refs must not be symbolic")
        value = self.read("show-ref", "--verify", "--hash", name).decode("ascii").strip()
        return _sha(value, "Observed local ref target")

    def object(self, oid: str, kind: str) -> bytes:
        _sha(oid, "Git object")
        if oid not in self.objects:
            output = self.read("cat-file", "--batch",
                               input_bytes=oid.encode("ascii") + b"\n")
            header, separator, payload = output.partition(b"\n")
            parts = header.split(b" ")
            need(separator == b"\n" and len(parts) == 3 and
                 parts[0] == oid.encode("ascii") and parts[2].isdigit(),
                 "Git object is missing or has an invalid batch header")
            try:
                actual_kind = parts[1].decode("ascii")
                size = int(parts[2])
            except (UnicodeError, ValueError) as error:
                raise Rejected("Invalid Git object metadata") from error
            need(actual_kind in ("blob", "tree", "commit", "tag") and
                 len(payload) == size + 1 and payload[-1:] == b"\n",
                 "Git object type or byte count is invalid")
            raw = payload[:-1]
            need(_object_id(actual_kind, raw) == oid,
                 "Actual Git object bytes do not match their SHA-1")
            self.objects[oid] = (actual_kind, raw)
        actual_kind, raw = self.objects[oid]
        need(actual_kind == kind, "Expected a Git " + kind + " object")
        return raw

    def commit(self, oid: str) -> tuple[str, tuple[str, ...]]:
        raw = self.object(oid, "commit")
        headers, separator, _message = raw.partition(b"\n\n")
        need(separator == b"\n\n", "Commit has no complete header block")
        trees = []
        parents = []
        try:
            for line in headers.split(b"\n"):
                if line.startswith(b"tree "):
                    trees.append(_sha(line[5:].decode("ascii"), "Commit tree"))
                elif line.startswith(b"parent "):
                    parents.append(_sha(line[7:].decode("ascii"), "Commit parent"))
        except UnicodeError as error:
            raise Rejected("Commit object IDs must be ASCII") from error
        need(len(trees) == 1, "Commit must name exactly one tree")
        return trees[0], tuple(parents)

    def tree(self, oid: str) -> Mapping[bytes, tuple[str, str]]:
        if oid not in self.trees:
            raw = self.object(oid, "tree")
            entries = {}
            order = []
            position = 0
            while position < len(raw):
                space = raw.find(b" ", position)
                zero = raw.find(b"\0", space + 1) if space >= 0 else -1
                need(space > position and zero > space + 1 and zero + 21 <= len(raw),
                     "Malformed raw Git tree entry")
                mode_raw = raw[position:space]
                name = raw[space + 1:zero]
                need(mode_raw in (b"40000", b"100644", b"100755", b"120000", b"160000")
                     and b"/" not in name and name not in (b".", b"..")
                     and name not in entries, "Invalid or duplicate Git tree entry")
                mode = mode_raw.decode("ascii")
                entries[name] = (mode, raw[zero + 1:zero + 21].hex())
                order.append(name + (b"/" if mode == TREE_MODE else b""))
                position = zero + 21
            need(order == sorted(order), "Noncanonical Git tree entry ordering")
            self.trees[oid] = entries
        return self.trees[oid]

    def entry(self, tree_oid: str, path: str) -> tuple[str, str] | None:
        parts = path.encode("utf-8").split(b"/")
        for index, part in enumerate(parts):
            found = self.tree(tree_oid).get(part)
            if found is None:
                return None
            if index == len(parts) - 1:
                return found
            need(found[0] == TREE_MODE, "Touched path crosses a non-directory Git entry")
            tree_oid = found[1]
        raise Rejected("Empty Git path")


def _changed_paths(git: _Git, source_tree: str, runner_tree: str,
                   envelope_path: str) -> set[str]:
    allowed = {WRITER_PATH.encode("utf-8"), envelope_path.encode("utf-8")}
    changed = set()

    def compare(before_oid: str | None, after_oid: str, prefix: bytes) -> None:
        before = git.tree(before_oid) if before_oid is not None else {}
        after = git.tree(after_oid)
        for name in set(before) | set(after):
            old, new = before.get(name), after.get(name)
            if old == new:
                continue
            path = prefix + name
            if path in allowed:
                changed.add(path.decode("utf-8"))
                continue
            need(any(target.startswith(path + b"/") for target in allowed),
                 "Unexpected runner tree change: " + repr(path))
            need(new is not None and new[0] == TREE_MODE and
                 (old is None or old[0] == TREE_MODE),
                 "Changed publication ancestor must remain a Git directory")
            compare(old[1] if old is not None else None, new[1], path + b"/")

    compare(source_tree, runner_tree, b"")
    need(changed == {WRITER_PATH, envelope_path},
         "Runner must change only the writer and add the proposal envelope")
    return changed


def _closed_report(result: str) -> dict:
    return {
        "schemaVersion": 1,
        "kind": "R03D5BActivationPublicationAuditV1",
        "result": result,
        "executionAuthorityVerified": False,
        "liveRemoteRefsVerified": False,
        "currentPhysicalInputsVerified": False,
        "runnerIdentityAndCustodyVerified": False,
        "outputCreated": False,
        "UnityOrPlayerExecuted": False,
        "realUnityBuild": "NotRun",
        "realPlayerCellsPassed": 0,
        "realPlayerCellsNoCoverage": 18,
        **CLOSED_AUTHORITY,
    }


def audit_publication(repo: Path, source_commit: str, runner_commit: str,
                      source_ref: str, runner_ref: str,
                      envelope_path: str = ENVELOPE_PATH) -> dict:
    """Audit actual local publication objects; never authorize or run a runner.

    Ref values are point-in-time local observations, rechecked at the end.
    They are neither live remote checks nor a cross-process namespace lock.
    Working-tree cleanliness and contents are deliberately not used as proof.
    """
    _sha(source_commit, "Source commit")
    _sha(runner_commit, "Runner commit")
    need(source_commit != runner_commit, "Source and runner commits must differ")
    need(type(source_ref) is str and type(runner_ref) is str and
         source_ref != runner_ref, "Source and runner refs must be distinct")
    need(source_ref == SOURCE_REF,
         "Source ref must be the canonical branch named by the proposal")
    envelope_path = _relative_path(envelope_path)
    git = _Git(repo)
    expected_refs = {source_ref: source_commit, runner_ref: runner_commit}
    for name, target in expected_refs.items():
        need(git.ref(name) == target, "Observed local ref does not equal the supplied commit")
    source_tree, _source_parents = git.commit(source_commit)
    runner_tree, runner_parents = git.commit(runner_commit)
    need(runner_parents == (source_commit,),
         "Runner must have the source commit as its sole parent")
    source_writer = git.entry(source_tree, WRITER_PATH)
    runner_writer = git.entry(runner_tree, WRITER_PATH)
    need(source_writer is not None and source_writer[0] in REGULAR_MODES and
         source_writer[1] == R5_WRITER_BLOB,
         "Source must contain the reviewed regular-file R5 writer")
    need(runner_writer is not None and runner_writer[0] == source_writer[0],
         "Runner writer must preserve the source regular-file mode")
    need(git.entry(source_tree, envelope_path) is None,
         "Proposal envelope path must be absent from the source commit")
    envelope = git.entry(runner_tree, envelope_path)
    need(envelope is not None and envelope[0] == PROPOSAL_MODE,
         "Runner proposal must be a new non-executable regular Git file")
    proposal_raw = git.object(envelope[1], "blob")
    _exact_value(strict_json_object(proposal_raw), proposal_envelope(source_commit),
                 "Proposal envelope")
    source_raw = git.object(source_writer[1], "blob")
    expected_writer = proposal_writer_bytes(source_raw, git_blob(proposal_raw))
    need(git.object(runner_writer[1], "blob") == expected_writer,
         "Runner writer is not the single exact proposal-blob substitution")
    changed = _changed_paths(git, source_tree, runner_tree, envelope_path)
    for name, target in expected_refs.items():
        need(git.ref(name) == target, "Observed local publication ref changed during audit")
    return {
        **_closed_report(SUCCESS_RESULT),
        "sourceCommit": source_commit,
        "runnerCommit": runner_commit,
        "sourceRef": source_ref,
        "runnerRef": runner_ref,
        "observedLocalRefs": expected_refs,
        "sourceWriterGitBlob": source_writer[1],
        "runnerWriterGitBlob": runner_writer[1],
        "proposalEnvelopeGitBlob": envelope[1],
        "proposalEnvelopePath": envelope_path,
        "proposalKind": PROPOSAL_KIND,
        "changedPaths": sorted(changed),
        "runnerSoleParentIsSource": True,
        "candidateWriterExecutedOrImported": False,
        "networkUsed": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--runner-commit", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--runner-ref", required=True)
    parser.add_argument("--envelope-path", default=ENVELOPE_PATH)
    args = parser.parse_args(argv)
    try:
        result = audit_publication(
            args.repo, args.source_commit, args.runner_commit,
            args.source_ref, args.runner_ref, args.envelope_path)
        code = 0
    except (Rejected, OSError, UnicodeError, ValueError) as error:
        result = {**_closed_report(REJECTED_RESULT), "reason": str(error)}
        code = 2
    try:
        print(json.dumps(result, sort_keys=True, allow_nan=False), flush=True)
    except (OSError, ValueError):
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
