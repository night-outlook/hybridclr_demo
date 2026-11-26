#!/usr/bin/env python3
"""AP2 source-host closure tests; candidate code remains inert Git/file bytes."""
from __future__ import annotations

import builtins
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import d5b_activation_publication as publication
import d5b_runner_closure as closure


WRITER_PATH = "Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py"
WRAPPER_PATH = "Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py"
PREFLIGHT_PATH = "Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py"
PLAN_PATH = "Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json"
PROFILE_PATH = "Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json"
ENVELOPE_PATH = publication.ENVELOPE_PATH
SOURCE_PATH = "Assets/ClosureFixture.txt"
REVIEWED_BLOBS = {
    WRITER_PATH: "99746fe64976da313cbd0e1625f0fcc5a67bca62",
    WRAPPER_PATH: "519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39",
    PREFLIGHT_PATH: "81e7c3a2eaccb77bff2515c91b173558e4eeba2f",
    PLAN_PATH: "5c0ab7a6d788ebd5adf57f1fddc567ba700632e9",
    PROFILE_PATH: "9956ea49656dc8337f9ab177c40faf29ea20c397",
}


class D5BRunnerClosureSourceOnly(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve(strict=True)
        self.repo = self.parent / "runner"
        self.repo.mkdir()
        self.workspace = self.parent / "workspace"
        self.workspace.mkdir()
        for role in ("hybridclr_demo", *publication.SOURCE_PINS):
            (self.workspace / role).mkdir()
        original = self.parent / "original-S"
        historical_base = self.parent / "historical-B1"
        original.mkdir()
        historical_base.mkdir()
        self.history = {"originalS": original, "b1EvidenceBase": historical_base}
        for role in ("b1Oneuse12", "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight"):
            path = historical_base / role
            path.mkdir()
            self.history[role] = path
        self.evidence = self.parent / "evidence"
        self.evidence.mkdir()
        self.locations = {
            "runnerRoot": str(self.repo), "workspace": str(self.workspace),
            "historicalRoots": {role: str(path) for role, path in self.history.items()},
            "evidenceParent": str(self.evidence),
        }
        self.git_environment = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")}
        self.git_environment.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "AP2 Synthetic Fixture",
            "GIT_AUTHOR_EMAIL": "ap2-fixture@example.invalid",
            "GIT_COMMITTER_NAME": "AP2 Synthetic Fixture",
            "GIT_COMMITTER_EMAIL": "ap2-fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-26T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2026-11-26T00:00:00+0000",
        })
        self._git("init", "-q", "--object-format=sha1")
        self._git("remote", "add", "origin",
                  "https://github.com/night-outlook/hybridclr_demo.git")
        self.sequence = 0
        self.source_ref = "refs/heads/" + publication.BRANCH
        self.runner_branch = "ap2-closure-runner-fixture"
        self.runner_ref = "refs/heads/" + self.runner_branch
        checkout = Path(__file__).resolve().parents[4]
        self.fixture_bytes = {
            path: (checkout / path).read_bytes() for path in REVIEWED_BLOBS}
        for path, expected in REVIEWED_BLOBS.items():
            self.assertEqual(self._git_blob(self.fixture_bytes[path]), expected)
        self.fixture_bytes[SOURCE_PATH] = b"Synthetic non-closure source sentinel.\n"
        self.source_entries = {
            path: ("100644", "blob", self._blob(raw))
            for path, raw in self.fixture_bytes.items()}
        self.source_commit, self.runner_commit, self.runner_entries = self._chain()
        self._checkout(self.source_commit, self.runner_commit)
        self.proposal = self._make_proposal()
        self.raw = closure.canonical_bytes(self.proposal)
        self.pin = self._git_blob(self.raw)

    def _git(self, *arguments, data=None):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *arguments], input=data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.git_environment, check=True)
        return result.stdout

    def _git_blob(self, raw):
        return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                            b"\0" + raw).hexdigest()

    def _blob(self, raw):
        return self._git("hash-object", "-w", "--stdin", data=raw).decode().strip()

    def _tree(self, entries):
        root = {}
        for path, entry in entries.items():
            directory = root
            parts = path.split("/")
            for part in parts[:-1]:
                directory = directory.setdefault(part, {})
            directory[parts[-1]] = entry
        def store(directory):
            records = []
            for name, entry in sorted(directory.items()):
                mode, kind, oid = ("040000", "tree", store(entry)) if isinstance(
                    entry, dict) else entry
                records.append(f"{mode} {kind} {oid}\t{name}\0".encode())
            return self._git("mktree", "-z", data=b"".join(records)).decode().strip()
        return store(root)


    def _commit(self, entries, parents=()):
        arguments = ["commit-tree", self._tree(entries)]
        for parent in parents:
            arguments.extend(("-p", parent))
        self.sequence += 1
        return self._git(*arguments, data=(
            f"AP2 synthetic fixture {self.sequence}\n").encode()).decode().strip()

    def _chain(self, source_entries=None):
        entries = dict(self.source_entries if source_entries is None else source_entries)
        source = self._commit(entries)
        envelope = (json.dumps(publication.proposal_envelope(source),
                               sort_keys=True, indent=2) + "\n").encode()
        envelope_blob = self._blob(envelope)
        writer = self.fixture_bytes[WRITER_PATH].replace(
            b"APPROVED_EXECUTION_ENVELOPE_BLOB = None\n",
            f'APPROVED_EXECUTION_ENVELOPE_BLOB = "{envelope_blob}"\n'.encode())
        entries[WRITER_PATH] = ("100644", "blob", self._blob(writer))
        entries[ENVELOPE_PATH] = ("100644", "blob", envelope_blob)
        return source, self._commit(entries, (source,)), entries

    def _checkout(self, source, runner):
        self._git("update-ref", self.source_ref, source)
        self._git("update-ref", self.runner_ref, runner)
        self._git("checkout", "-q", "--force", "-B", self.runner_branch, runner)

    def _make_proposal(self, *, repo=None, source=None, runner=None, locations=None):
        return closure.make_closure_proposal(
            self.repo if repo is None else repo,
            self.source_commit if source is None else source,
            self.runner_commit if runner is None else runner,
            self.runner_ref, self.locations if locations is None else locations)

    def _verify(self, proposal=None):
        raw = self.raw if proposal is None else closure.canonical_bytes(proposal)
        return closure.verify_runner_closure(raw, self._git_blob(raw))

    def _assert_rejected(self, proposal=None):
        with self.assertRaises(closure.Rejected):
            self._verify(proposal)


    def _assert_closed(self, report):
        self.assertEqual(report["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")
        for field in ("D5BLocalExecution", "D5LocalValidation", "explicitUserLocalApproval"):
            self.assertEqual(report[field], "NotAuthorized")
        for field in (
            "runtimeImportIsolationVerified", "runnerExecutableClosureVerified",
            "exclusiveCustodyVerified", "liveRemoteRefsVerified",
            "sourceDataInputsVerified", "currentMacInputsVerified",
            "executionAuthorityVerified", "candidateWriterExecutedOrImported",
            "outputCreated", "networkUsed", "UnityOrPlayerExecuted",
            "R03Accepted", "H2Passed", "ReadyForHumanReviewGate",
            "allowNativeBuild", "allowPlayerLaunch",
        ):
            self.assertIs(report[field], False, field)
        self.assertIsNone(report["approvedEnvelopeGitBlob"])
        self.assertEqual(report["independentlyReviewedExecutableAdmission"], "Pending")
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)

    def test_01_six_file_snapshot_is_immutable_and_closed(self):
        bundle = self._verify()
        self.assertIsInstance(bundle, closure.VerifiedBundle)
        self.assertIs(type(bundle.files), tuple)
        self.assertEqual({item.path for item in bundle.files},
                         set(REVIEWED_BLOBS) | {ENVELOPE_PATH})
        self.assertEqual(len(bundle.files), 6)
        for item in bundle.files:
            self.assertIs(type(item.raw), bytes)
            self.assertEqual(item.git_blob, self._git_blob(item.raw))
            self.assertEqual(item.raw, self._git(
                "cat-file", "blob", self.runner_commit + ":" + item.path))
            with self.assertRaises(AttributeError):
                item.raw = b"changed"
        with self.assertRaises(AttributeError):
            bundle.files = ()
        report = bundle.report
        self.assertEqual(report["result"], closure.SUCCESS_RESULT)
        self.assertIs(report["runnerArtifactClosureVerified"], True)
        self.assertIs(report["runnerCheckoutObservationVerified"], True)
        self.assertIs(report["sameSnapshotAtRecheck"], True)
        self.assertEqual(report["declaredRepositoryLocalFileCount"], 6)
        self.assertEqual(report["closureProposalGitBlob"], self.pin)
        self._assert_closed(report)
        report["executionAuthorityVerified"] = True
        self._assert_closed(bundle.report)
        saved = bundle.files[0]
        (self.repo / saved.path).write_bytes(saved.raw + b"\n")
        self.assertEqual(bundle.files[0], saved)
        self.assertNotEqual(saved.raw, (self.repo / saved.path).read_bytes())


    def test_02_verification_never_imports_or_executes_candidate_modules(self):
        candidate_names = {"run_d5_local", "d5b_local_admission",
                           "d5b_rr5_source_preflight"}
        original_import, previous_profile = builtins.__import__, sys.getprofile()
        attempts = []
        def guarded_import(name, *args, **kwargs):
            if name.rsplit(".", 1)[-1] in candidate_names:
                attempts.append(name)
                raise AssertionError("Candidate import attempted")
            return original_import(name, *args, **kwargs)
        def guarded_profile(frame, event, arg):
            if event == "call" and Path(frame.f_code.co_filename).stem in candidate_names:
                attempts.append(frame.f_code.co_filename)
                raise AssertionError("Candidate code executed")
        try:
            sys.setprofile(guarded_profile)
            with mock.patch.object(builtins, "__import__", side_effect=guarded_import):
                bundle = self._verify()
        finally:
            sys.setprofile(previous_profile)
        self.assertEqual(attempts, [])
        self._assert_closed(bundle.report)

    def test_03_manifest_requires_external_exact_bytes_pin(self):
        oversized = b" " * (closure.MAX_FILE_BYTES + 1)
        for label, raw, pin in (
            ("wrong-pin", self.raw, "0" * 40),
            ("changed-bytes", self.raw + b"\n", self.pin),
            ("text-not-bytes", self.raw.decode(), self.pin),
            ("malformed-pin", self.raw, "G" * 40),
            ("oversized", oversized, self._git_blob(oversized)),
        ):
            with self.subTest(change=label):
                with mock.patch.object(closure, "_helper") as helper:
                    with self.assertRaises(closure.Rejected):
                        closure.verify_runner_closure(raw, pin)
                    helper.assert_not_called()

    def test_04_manifest_schema_types_authority_and_roster_are_exact(self):
        variants = []
        for path, value in (
            (("schemaVersion",), True),
            (("kind",), "R03D5BApprovedDryAdmissionEnvelopeV1"),
            (("scope",), "ExecuteRunner"),
            (("entryPoint",), PREFLIGHT_PATH),
            (("runtimeImportIsolationVerified",), True),
            (("runner", "repository"), "night-outlook/other"),
            (("authorization", "approvedEnvelopeGitBlob"), self.pin),
            (("authorization", "explicitUserLocalApproval"), "ExplicitlyApproved"),
            (("authorization", "allowPlayerLaunch"), True),
            (("authorization", "R03Accepted"), 0),
            (("files", PROFILE_PATH, "gitBlob"), "f" * 40),
            (("files", WRAPPER_PATH, "mode"), 100644),
            (("files", PREFLIGHT_PATH, "role"), "sourceData"),
            (("repositoryLocalImports", "d5b_rr5_source_preflight"), PROFILE_PATH),
        ):
            proposal = copy.deepcopy(self.proposal)
            target = proposal
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            variants.append((".".join(path), proposal))
        missing = copy.deepcopy(self.proposal)
        missing["files"].pop(PROFILE_PATH)
        variants.append(("missing-profile", missing))
        extra = copy.deepcopy(self.proposal)
        extra["files"][SOURCE_PATH] = copy.deepcopy(extra["files"][PLAN_PATH])
        variants.append(("extra-file", extra))
        for label, proposal in variants:
            with self.subTest(change=label):
                self._assert_rejected(proposal)
        duplicate = self.raw.replace(b'"schemaVersion": 1',
                                     b'"schemaVersion": 1, "schemaVersion": 1', 1)
        for raw in (b"[]", b'{"x":"\xff"}', duplicate):
            with self.subTest(raw=raw[:30]):
                with self.assertRaises(closure.Rejected):
                    closure.verify_runner_closure(raw, self._git_blob(raw))


    def test_05_changed_reviewed_objects_reject_after_valid_ap1_publication(self):
        for path in (WRAPPER_PATH, PREFLIGHT_PATH, PLAN_PATH, PROFILE_PATH):
            with self.subTest(path=path):
                entries = dict(self.source_entries)
                entries[path] = ("100644", "blob",
                                 self._blob(self.fixture_bytes[path] + b"\n"))
                source, runner, _ = self._chain(entries)
                self._checkout(source, runner)
                report = publication.audit_publication(
                    self.repo, source, runner, self.source_ref, self.runner_ref)
                self.assertEqual(report["result"],
                                 "ProposalPublicationStructureVerified_NoExecutionAuthority")
                with self.assertRaises(closure.Rejected):
                    proposal = self._make_proposal(source=source, runner=runner)
                    self._verify(proposal)

    def test_06_closure_git_objects_require_regular_nonexecutable_modes(self):
        for label, entry in (
            ("executable", ("100755", "blob", REVIEWED_BLOBS[PREFLIGHT_PATH])),
            ("symlink", ("120000", "blob", self._blob(b"../D5Local/run_d5_local.py"))),
            ("tree", ("040000", "tree", self._tree({}))),
            ("gitlink", ("160000", "commit", self.source_commit)),
        ):
            with self.subTest(kind=label):
                entries = {**self.source_entries, PREFLIGHT_PATH: entry}
                source, runner, _ = self._chain(entries)
                self._checkout(source, runner)
                with self.assertRaises(closure.Rejected):
                    proposal = self._make_proposal(source=source, runner=runner)
                    self._verify(proposal)

    def test_07_tracked_untracked_and_ignored_changes_are_rejected(self):
        target = self.repo / PREFLIGHT_PATH
        original = target.read_bytes()
        exclude = self.repo / ".git" / "info" / "exclude"
        original_exclude = exclude.read_bytes()
        for change in ("tracked", "staged", "untracked", "ignored"):
            with self.subTest(change=change):
                extra = self.repo / ("ap2-" + change + ".txt")
                try:
                    if change in ("tracked", "staged"):
                        target.write_bytes(original + b"\n")
                        if change == "staged":
                            self._git("add", "--", PREFLIGHT_PATH)
                    else:
                        if change == "ignored":
                            exclude.write_bytes(original_exclude + b"\nap2-ignored.txt\n")
                        extra.write_bytes(b"unexpected runner-local material\n")
                    self._assert_rejected()
                finally:
                    if change == "staged":
                        self._git("reset", "-q", "HEAD", "--", PREFLIGHT_PATH)
                    target.write_bytes(original)
                    if extra.exists():
                        extra.unlink()
                    exclude.write_bytes(original_exclude)

    def test_08_assumed_and_skipped_index_entries_are_rejected(self):
        target = self.repo / PREFLIGHT_PATH
        original = target.read_bytes()
        for flag in ("assume-unchanged", "skip-worktree"):
            for changed in (False, True):
                with self.subTest(flag=flag, changed=changed):
                    try:
                        self._git("update-index", "--" + flag, PREFLIGHT_PATH)
                        if changed:
                            target.write_bytes(original + b"\n")
                        self.assertEqual(self._git("status", "--porcelain=v1"), b"")
                        self._assert_rejected()
                    finally:
                        self._git("update-index", "--no-" + flag, PREFLIGHT_PATH)
                        target.write_bytes(original)


    def test_09_working_files_reject_symlinks_hardlinks_and_executable_bits(self):
        target = self.repo / PREFLIGHT_PATH
        original = target.read_bytes()
        original_mode = stat.S_IMODE(target.stat().st_mode)
        for substitution in ("symlink", "hardlink", "executable"):
            with self.subTest(substitution=substitution):
                outside = self.parent / (substitution + ".py")
                outside.write_bytes(original)
                try:
                    if substitution == "executable":
                        # Git may ignore executable mode changes; the file reader must not.
                        self._git("config", "core.filemode", "false")
                        target.chmod(original_mode | 0o111)
                        self.assertEqual(self._git("status", "--porcelain=v1"), b"")
                    else:
                        target.unlink()
                        if substitution == "symlink":
                            target.symlink_to(outside)
                        else:
                            os.link(outside, target)
                            self.assertEqual(target.stat().st_nlink, 2)
                            self.assertEqual(self._git("status", "--porcelain=v1"), b"")
                    self._assert_rejected()
                finally:
                    target.unlink()
                    target.write_bytes(original)
                    target.chmod(original_mode)
                    self._git("config", "core.filemode", "true")

    def test_10_directory_aliases_reject_for_runner_and_file_ancestors(self):
        alias = self.parent / "runner-alias"
        alias.symlink_to(self.repo, target_is_directory=True)
        proposal = copy.deepcopy(self.proposal)
        proposal["locations"]["runnerRoot"] = str(alias)
        self._assert_rejected(proposal)
        ancestor = (self.repo / PREFLIGHT_PATH).parent
        saved = self.parent / "saved-admission-directory"
        ancestor.rename(saved)
        ancestor.symlink_to(saved, target_is_directory=True)
        try:
            self._assert_rejected()
        finally:
            ancestor.unlink()
            saved.rename(ancestor)

    def test_11_checkout_branch_head_and_origin_are_exact(self):
        canonical_origin = "https://github.com/night-outlook/hybridclr_demo.git"
        for mismatch in ("detached", "wrong-branch", "moved-head", "wrong-origin",
                         "multiple-origins"):
            with self.subTest(mismatch=mismatch):
                try:
                    if mismatch == "detached":
                        self._git("checkout", "-q", "--detach", self.runner_commit)
                    elif mismatch == "wrong-branch":
                        self._git("checkout", "-q", "-b", "wrong-runner-branch",
                                  self.runner_commit)
                    elif mismatch == "moved-head":
                        self._git("update-ref", self.runner_ref, self.source_commit)
                    elif mismatch == "wrong-origin":
                        self._git("remote", "set-url", "origin",
                                  "https://github.com/night-outlook/another-demo.git")
                    else:
                        self._git("config", "--add", "remote.origin.url", canonical_origin)
                    self._assert_rejected()
                finally:
                    self._git("config", "--replace-all", "remote.origin.url", canonical_origin)
                    self._checkout(self.source_commit, self.runner_commit)

    def test_12_filters_rewrites_and_hidden_status_configuration_reject(self):
        for key, value in (
            ("filter.ap2-inert.clean", "unused-inert-filter"),
            ("url.https://example.invalid/.insteadOf", "https://github.com/"),
            ("core.ignorestat", "true"),
            ("core.sparsecheckout", "true"),
            ("core.sparsecheckoutcone", "true"),
            ("core.worktree", str(self.repo)),
            ("core.splitindex", "true"),
            ("diff.external", "unused-inert-diff"),
        ):
            with self.subTest(key=key):
                try:
                    self._git("config", key, value)
                    self._assert_rejected()
                finally:
                    self._git("config", "--unset", key)

    def test_13_shared_and_modified_git_administration_reject(self):
        git_dir = self.repo / ".git"
        alternate = self.parent / "alternate-objects"
        alternate.mkdir()
        for relative, raw in (
            ("shallow", (self.runner_commit + "\n").encode()),
            ("info/grafts", (self.runner_commit + "\n").encode()),
            ("objects/info/alternates", (str(alternate) + "\n").encode()),
        ):
            with self.subTest(administration=relative):
                path = git_dir / relative
                path.write_bytes(raw)
                try:
                    self._assert_rejected()
                finally:
                    path.unlink()
        relocated = self.parent / "relocated-git"
        git_dir.rename(relocated)
        git_dir.symlink_to(relocated, target_is_directory=True)
        try:
            self._assert_rejected()
        finally:
            git_dir.unlink()
            relocated.rename(git_dir)
        self._git("checkout", "-q", "--detach", self.source_commit)
        linked = self.parent / "linked-runner"
        self._git("worktree", "add", "--quiet", str(linked), self.runner_branch)
        try:
            self.assertTrue((linked / ".git").is_file())
            proposal = copy.deepcopy(self.proposal)
            proposal["locations"]["runnerRoot"] = str(linked)
            self._assert_rejected(proposal)
        finally:
            self._git("worktree", "remove", "--force", str(linked))
            self._checkout(self.source_commit, self.runner_commit)


    def test_14_locations_require_complete_canonical_disjoint_directories(self):
        variants = []
        for label, key, value in (
            ("runner-is-source-workspace", "runnerRoot", str(self.workspace)),
            ("output-is-runner", "evidenceParent", str(self.repo)),
            ("output-is-source", "evidenceParent", str(self.workspace / "hybridclr_demo")),
            ("output-is-history", "evidenceParent", str(self.history["b1NativeHostRaw"])),
            ("output-contains-runner", "evidenceParent", str(self.parent)),
            ("relative", "evidenceParent", "relative-output"),
            ("unnormalized", "evidenceParent", str(self.evidence) + "/../evidence"),
            ("non-string", "evidenceParent", False),
            ("absent", "evidenceParent", str(self.parent / "absent-output")),
        ):
            proposal = copy.deepcopy(self.proposal)
            proposal["locations"][key] = value
            variants.append((label, proposal))
        for label, history_path in (("history-is-runner", self.repo),
                                    ("history-contains-runner", self.parent)):
            proposal = copy.deepcopy(self.proposal)
            proposal["locations"]["historicalRoots"]["originalS"] = str(history_path)
            variants.append((label, proposal))
        for label, mutation in (
            ("missing-output", lambda locations: locations.pop("evidenceParent")),
            ("missing-history-role", lambda locations:
             locations["historicalRoots"].pop("b1Oneuse12")),
            ("extra-history-role", lambda locations:
             locations["historicalRoots"].update(extra=str(self.evidence))),
            ("extra-location-role", lambda locations: locations.update(extra=str(self.evidence))),
        ):
            proposal = copy.deepcopy(self.proposal)
            mutation(proposal["locations"])
            variants.append((label, proposal))
        evidence_alias = self.parent / "evidence-alias"
        evidence_alias.symlink_to(self.evidence, target_is_directory=True)
        proposal = copy.deepcopy(self.proposal)
        proposal["locations"]["evidenceParent"] = str(evidence_alias)
        variants.append(("aliased-output", proposal))
        for label, proposal in variants:
            with self.subTest(location=label):
                self._assert_rejected(proposal)
        source = self.workspace / "hybridclr"
        saved = self.parent / "temporarily-absent-source"
        source.rename(saved)
        try:
            self._assert_rejected()
        finally:
            saved.rename(source)

    def test_15_file_bytes_and_identity_changes_between_reads_reject(self):
        target = self.repo / WRAPPER_PATH
        original = target.read_bytes()
        read_relative = closure._read_relative
        for change in ("bytes", "same-bytes-new-inode"):
            with self.subTest(change=change):
                observed = []
                def mutate_after_first_read(root_fd, relative):
                    result = read_relative(root_fd, relative)
                    if relative == WRAPPER_PATH and not observed:
                        observed.append(result[1])
                        if change == "bytes":
                            target.write_bytes(original + b"\n")
                        else:
                            replacement = self.parent / "replacement-wrapper.py"
                            replacement.write_bytes(original)
                            os.replace(replacement, target)
                            self.assertNotEqual(target.stat().st_ino, result[1][1])
                    return result
                try:
                    with mock.patch.object(closure, "_read_relative",
                                           side_effect=mutate_after_first_read):
                        with self.assertRaisesRegex(closure.Rejected,
                                                    "changed across snapshot observations"):
                            self._verify()
                    self.assertEqual(len(observed), 1)
                finally:
                    target.write_bytes(original)

    def test_16_real_ref_and_checkout_config_changes_during_snapshot_reject(self):
        read_relative = closure._read_relative
        for changed_ref in (self.source_ref, self.runner_ref):
            with self.subTest(ref=changed_ref):
                changed = []
                def move_ref_after_read(root_fd, relative):
                    result = read_relative(root_fd, relative)
                    if relative == WRAPPER_PATH and not changed:
                        changed.append(changed_ref)
                        replacement = (self.runner_commit if changed_ref == self.source_ref
                                       else self.source_commit)
                        self._git("update-ref", changed_ref, replacement)
                    return result
                try:
                    with mock.patch.object(closure, "_read_relative", side_effect=move_ref_after_read):
                        self._assert_rejected()
                    self.assertEqual(changed, [changed_ref])
                finally:
                    self._git("update-ref", self.source_ref, self.source_commit)
                    self._git("update-ref", self.runner_ref, self.runner_commit)
        observe_checkout = closure._checkout_observation
        changed = []
        def change_config_after_observation(*args):
            observation = observe_checkout(*args)
            if not changed:
                changed.append(True)
                # This benign key remains accepted, so equality at recheck must detect it.
                self._git("config", "ap2.observation", "changed")
            return observation
        try:
            with mock.patch.object(closure, "_checkout_observation",
                                   side_effect=change_config_after_observation):
                with self.assertRaisesRegex(closure.Rejected,
                                            "checkout identity/config/index changed"):
                    self._verify()
            self.assertEqual(changed, [True])
        finally:
            self._git("config", "--unset", "ap2.observation")


    def test_17_identical_ancestor_replacement_during_actual_read_rejects(self):
        target = self.repo / WRAPPER_PATH
        ancestor = target.parent
        saved = self.parent / "original-local-ancestor"
        target_stat = target.stat()
        target_identity = (target_stat.st_dev, target_stat.st_ino)
        original_ancestor_inode = ancestor.stat().st_ino
        real_read, changed = os.read, []
        def replace_ancestor_after_bytes(descriptor, size):
            content = real_read(descriptor, size)
            observed = os.fstat(descriptor)
            if content and not changed and (observed.st_dev, observed.st_ino) == target_identity:
                changed.append(True)
                ancestor.rename(saved)
                shutil.copytree(saved, ancestor)
                self.assertNotEqual(ancestor.stat().st_ino, original_ancestor_inode)
            return content
        try:
            with mock.patch.object(closure.os, "read", side_effect=replace_ancestor_after_bytes):
                with self.assertRaisesRegex(closure.Rejected,
                                            "ancestor changed during read|Tracked directory changed during scan"):
                    self._verify()
            self.assertEqual(changed, [True])
            self.assertEqual(self._git("status", "--porcelain=v1"), b"")
        finally:
            if saved.exists():
                shutil.rmtree(ancestor)
                saved.rename(ancestor)

    def test_18_protected_directory_identity_change_between_observations_rejects(self):
        observe_checkout = closure._checkout_observation
        for protected in (self.evidence, self.workspace / "hybridclr",
                          self.history["b1Preflight"]):
            with self.subTest(protected=str(protected)):
                saved = self.parent / ("saved-" + protected.name)
                changed = []
                def replace_protected_directory(*args):
                    observation = observe_checkout(*args)
                    if not changed:
                        changed.append(protected.stat().st_ino)
                        protected.rename(saved)
                        protected.mkdir()
                        self.assertNotEqual(protected.stat().st_ino, changed[0])
                    return observation
                try:
                    with mock.patch.object(closure, "_checkout_observation",
                                           side_effect=replace_protected_directory):
                        with self.assertRaisesRegex(closure.Rejected,
                                                    "protected location changed"):
                            self._verify()
                    self.assertEqual(len(changed), 1)
                finally:
                    if saved.exists():
                        protected.rmdir()
                        saved.rename(protected)

    def _cli(self, *, flags=("-I", "-S", "-B"), extra=(), proposal_path=None,
             expected_blob=None):
        path = self.parent / "closure-proposal.json" if proposal_path is None else proposal_path
        if proposal_path is None:
            path.write_bytes(self.raw)
        return subprocess.run(
            [sys.executable, *flags, str(Path(closure.__file__).resolve()),
             "--closure", str(path), "--expected-closure-blob",
             self.pin if expected_blob is None else expected_blob, *extra],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.git_environment, check=False)

    def test_19_isolated_cli_returns_closed_json_without_mutating_runner(self):
        before_refs = self._git("show-ref")
        before_index = self._git("ls-files", "--stage", "-z")
        before_bytes = {path: (self.repo / path).read_bytes()
                        for path in (*REVIEWED_BLOBS, ENVELOPE_PATH)}
        result = self._cli()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], closure.SUCCESS_RESULT)
        self.assertIs(report["runnerArtifactClosureVerified"], True)
        self.assertIs(report["sameSnapshotAtRecheck"], True)
        self._assert_closed(report)
        self.assertEqual(self._git("show-ref"), before_refs)
        self.assertEqual(self._git("ls-files", "--stage", "-z"), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1", "--ignored"), b"")
        for path, content in before_bytes.items():
            self.assertEqual((self.repo / path).read_bytes(), content)
        self.assertEqual(list(self.evidence.iterdir()), [])
        for role in closure.SOURCE_ROLES:
            self.assertEqual(list((self.workspace / role).iterdir()), [])

    def test_20_cli_requires_isolation_pin_and_rejects_execution_overrides(self):
        for flags in (("-S", "-B"), ("-I", "-B"), ("-I", "-S")):
            with self.subTest(flags=flags):
                result = self._cli(flags=flags)
                self.assertEqual(result.returncode, 2)
                report = json.loads(result.stdout)
                self.assertEqual(report["result"], closure.REJECTED_RESULT)
                self.assertIn("Python -I -S -B", report["reason"])
                self._assert_closed(report)
        result = self._cli(expected_blob="0" * 40)
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], closure.REJECTED_RESULT)
        self._assert_closed(report)
        for extra in (("--execute",), ("--approved-envelope-blob", self.pin),
                      ("--allow-player-launch",), ("--entry-point", PREFLIGHT_PATH)):
            with self.subTest(override=extra[0]):
                result = self._cli(extra=extra)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"unrecognized arguments", result.stderr)


    def test_21_verification_uses_only_object_and_metadata_git_commands(self):
        allowed = {"config", "rev-parse", "symbolic-ref", "show-ref",
                   "check-ref-format", "cat-file", "rev-list", "ls-files"}
        run, observed = subprocess.run, []
        def observe_git_command(arguments, *args, **kwargs):
            self.assertIsInstance(arguments, list)
            self.assertEqual(Path(arguments[0]).name, "git")
            self.assertIn("-C", arguments)
            operation = arguments[arguments.index("-C") + 2]
            observed.append(operation)
            self.assertIn(operation, allowed, "Repository worktree conversion is forbidden")
            self.assertNotIn("--filters", arguments)
            self.assertNotIn("--textconv", arguments)
            return run(arguments, *args, **kwargs)
        with mock.patch.object(subprocess, "run", side_effect=observe_git_command):
            bundle = self._verify()
        self.assertTrue({"cat-file", "rev-list", "ls-files"}.issubset(set(observed)))
        self.assertEqual(bundle.report["result"], closure.SUCCESS_RESULT)
        self._assert_closed(bundle.report)

    def test_22_unrelated_tracked_executable_and_literal_symlink_are_valid(self):
        executable_path = "Tools/NonClosure/ordinary-executable-data.txt"
        link_path = "Assets/LiteralSymlink"
        missing_target = self.parent / "missing-symlink-target"
        self.assertFalse(missing_target.exists())
        entries = {**self.source_entries,
                   executable_path: ("100755", "blob", self._blob(b"Benign fixture bytes.\n")),
                   link_path: ("120000", "blob", self._blob(os.fsencode(missing_target)))}
        source, runner, runner_entries = self._chain(entries)
        self._checkout(source, runner)
        self.assertTrue((self.repo / executable_path).stat().st_mode & 0o111)
        self.assertTrue((self.repo / link_path).is_symlink())
        self.assertEqual(os.readlink(self.repo / link_path), str(missing_target))
        self.assertFalse((self.repo / link_path).exists())
        proposal = self._make_proposal(source=source, runner=runner)
        bundle = self._verify(proposal)
        self.assertEqual(bundle.report["result"], closure.SUCCESS_RESULT)
        self.assertEqual({item.path for item in bundle.files},
                         set(REVIEWED_BLOBS) | {ENVELOPE_PATH})
        self.assertEqual(self._git("cat-file", "blob", runner_entries[link_path][2]),
                         os.fsencode(missing_target))
        self._assert_closed(bundle.report)

    def test_23_full_inventory_rejects_unrelated_changes_and_extra_empty_directories(self):
        target = self.repo / SOURCE_PATH
        original = target.read_bytes()
        original_mode = stat.S_IMODE(target.stat().st_mode)
        for change in ("bytes", "staged", "executable-mode", "missing",
                       "empty-root-directory", "empty-nested-directory"):
            with self.subTest(change=change):
                extra = self.repo / ("extra-empty" if change == "empty-root-directory"
                                     else "Assets/extra-empty")
                try:
                    if change in ("bytes", "staged"):
                        target.write_bytes(original + b"changed unrelated tracked bytes\n")
                        if change == "staged":
                            self._git("add", "--", SOURCE_PATH)
                    elif change == "executable-mode":
                        self._git("config", "core.filemode", "false")
                        target.chmod(original_mode | 0o111)
                    elif change == "missing":
                        target.unlink()
                    else:
                        extra.mkdir()
                    self._assert_rejected()
                finally:
                    if change == "staged":
                        self._git("reset", "-q", "HEAD", "--", SOURCE_PATH)
                    if extra.exists():
                        extra.rmdir()
                    target.write_bytes(original)
                    target.chmod(original_mode)
                    self._git("config", "core.filemode", "true")

    def test_24_full_inventory_enforces_per_file_and_aggregate_byte_bounds(self):
        content = b"x" * (max(map(len, self.fixture_bytes.values())) + 128)
        entries = {**self.source_entries,
                   "Assets/BoundedFixture.bin": ("100644", "blob", self._blob(content))}
        source, runner, runner_entries = self._chain(entries)
        self._checkout(source, runner)
        proposal = self._make_proposal(source=source, runner=runner)
        self.assertEqual(self._verify(proposal).report["result"], closure.SUCCESS_RESULT)
        with mock.patch.object(closure, "MAX_CHECKOUT_FILE_BYTES", len(content) - 1):
            self._assert_rejected(proposal)
        with mock.patch.object(closure, "MAX_CHECKOUT_FILE_BYTES", len(content)):
            self.assertEqual(self._verify(proposal).report["result"], closure.SUCCESS_RESULT)
        total = sum(len(self._git("cat-file", "blob", entry[2]))
                    for entry in runner_entries.values())
        with mock.patch.object(closure, "MAX_CHECKOUT_BYTES", total - 1):
            self._assert_rejected(proposal)
        with mock.patch.object(closure, "MAX_CHECKOUT_BYTES", total):
            self.assertEqual(self._verify(proposal).report["result"], closure.SUCCESS_RESULT)

    def test_25_full_inventory_enforces_entry_count_and_depth_bounds(self):
        deep_path = "/".join(["DepthFixture"] + ["level"] * 8 + ["ordinary.txt"])
        entries = {**self.source_entries,
                   deep_path: ("100644", "blob", self._blob(b"Bounded depth fixture.\n"))}
        source, runner, _ = self._chain(entries)
        self._checkout(source, runner)
        proposal = self._make_proposal(source=source, runner=runner)
        self.assertEqual(self._verify(proposal).report["result"], closure.SUCCESS_RESULT)
        for name, limit in (("MAX_CHECKOUT_ENTRIES", 1), ("MAX_TREE_DEPTH", 7)):
            with self.subTest(bound=name):
                with mock.patch.object(closure, name, limit):
                    self._assert_rejected(proposal)


if __name__ == "__main__":
    unittest.main()
