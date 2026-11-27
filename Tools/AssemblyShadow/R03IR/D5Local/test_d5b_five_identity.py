#!/usr/bin/env python3
"""Primary internal AP5 regressions using ordinary checkouts and file-only refs.

These tests establish fixture behavior, not independent approval, production
HTTPS reachability, current source custody, or executable admission. No earlier
AP1--AP4 test class or candidate Python module is imported or inherited.
"""
from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest import mock

HERE = Path(__file__).resolve(strict=True).parent
MODULE_PATH = HERE / "d5b_five_identity.py"
SPEC = importlib.util.spec_from_file_location("_ap5_focused_subject", MODULE_PATH)
observer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = observer
SPEC.loader.exec_module(observer)
REAL_RUN_REMOTE = observer._run_remote
REAL_OBSERVE_CHECKOUT = observer._observe_checkout
REAL_OBSERVE_LOCATIONS = observer._observe_locations
AP2_PIN = "2535bc14c31f1ff2d73fdb8c7be1d7dab605d990"
AP1_PIN = "ecf36a7a51f1750c6e8425ee79e9ac8938102b54"
ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus", "runner")
SOURCE_REF = "refs/heads/codex/assembly-shadow-r01b-h1"
RUNNER_REF = "refs/heads/codex/ap5-focused-fixture"
CLOSED_AUTHORITY = {
    "approvedEnvelopeGitBlob": None,
    "independentlyReviewedExecutableAdmission": "Pending",
    "explicitUserLocalApproval": "NotAuthorized",
    "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
    "D5BLocalExecution": "NotAuthorized", "D5LocalValidation": "NotAuthorized",
    "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
    "allowNativeBuild": False, "allowPlayerLaunch": False,
}
FALSE_REPORT_FIELDS = (
    "acceptedAP1SourceTupleVerified", "runnerPublicationRelationVerified",
    "AP2ArtifactCompatibilityVerified", "AP4ConfigurationCompatibilityVerified",
    "sourceSemanticPreflightVerified", "AP4CompositionVerified",
    "sourceDataInputsVerified", "runnerArtifactClosureVerified",
    "runtimeConfigurationReadsBound", "runtimeImportIsolationVerified",
    "runnerExecutableClosureVerified", "standardLibraryIdentityVerified",
    "rawGitIndexBytesVerified", "completeGitAdministrativeCustodyVerified",
    "simultaneousFiveIdentitySnapshotVerified", "remoteRefsFrozen",
    "exclusiveCustodyVerified", "continuousCustodyVerified", "currentMacInputsVerified",
    "candidateWriterExecutedOrImported", "candidateEntryPointsInvoked",
    "admissionPreviewInvoked", "sourceInspectionEntryPointInvoked",
    "executionAuthorityVerified", "UnityOrPlayerExecuted", "QExecutionAuthorized",
    "outputCreated",
)


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def inventory(root):
    """Read-only bytes/mode/identity snapshot, excluding access timestamps."""
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            info = path.lstat()
            identity = (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                        info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            if stat.S_ISLNK(info.st_mode):
                value = ("link", os.readlink(path))
            elif stat.S_ISREG(info.st_mode):
                value = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
            else:
                value = ("directory",)
            result[str(path.relative_to(root))] = (identity, value)
    return result


class D5BFiveIdentityFocused(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ap5-focused-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve(strict=True)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.bare_parent = self.root / "bare"
        self.bare_parent.mkdir()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.history = {}
        for name in ("originalS", "b1EvidenceBase", "b1Oneuse12",
                     "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight"):
            path = self.root / ("history-" + name)
            path.mkdir()
            self.history[name] = str(path)
        self.git = shutil.which("git", path=os.defpath)
        self.assertIsNotNone(self.git)
        self.env = {
            "PATH": os.defpath, "LANG": "C", "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_COUNT": "0",
            "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
            "GIT_ALLOW_PROTOCOL": "file", "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1", "GIT_ATTR_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "AP5 Fixture", "GIT_AUTHOR_EMAIL": "ap5@example.invalid",
            "GIT_COMMITTER_NAME": "AP5 Fixture", "GIT_COMMITTER_EMAIL": "ap5@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-26T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2026-11-26T00:00:00+0000",
        }
        self.roots, self.bares, self.pins = {}, {}, {}
        for role in ROLES[:-1]:
            checkout = self.workspace / role
            checkout.mkdir()
            remote = self.bare_parent / (role + ".git")
            remote.mkdir()
            self.roots[role], self.bares[role] = checkout, remote
            self._git(checkout, "init", "-q", "--object-format=sha1")
            self._git(checkout, "symbolic-ref", "HEAD", SOURCE_REF)
            self._git(checkout, "remote", "add", "origin",
                      "https://github.com/night-outlook/" + role + ".git")
            (checkout / "tracked.txt").write_bytes((role + " fixture\n").encode())
            (checkout / ".gitignore").write_bytes(b"ignored-data\n")
            (checkout / "nested").mkdir()
            (checkout / "nested/payload.bin").write_bytes(b"raw\x00fixture\r\n")
            if role == "hybridclr_demo":
                for name in observer.CANDIDATE_NAMES:
                    (checkout / (name + ".py")).write_bytes(b"# Inert candidate bytes only.\n")
            self._git(checkout, "add", "--all")
            self._git(checkout, "commit", "-q", "-m", role + " source fixture")
            self.pins[role] = self._git(checkout, "rev-parse", "HEAD").decode().strip()
            self._git(remote, "init", "--bare", "-q", "--object-format=sha1")
            self._git(remote, "symbolic-ref", "HEAD", SOURCE_REF)
            self._git(checkout, "push", "-q", remote.as_uri(), SOURCE_REF)
        runner = self.root / "runner"
        self._git(self.root, "clone", "-q", "--no-hardlinks", "--branch",
                  SOURCE_REF.removeprefix("refs/heads/"),
                  self.bares["hybridclr_demo"].as_uri(), str(runner))
        self.roots["runner"] = runner
        self._git(runner, "remote", "set-url", "origin",
                  "https://github.com/night-outlook/hybridclr_demo.git")
        self._git(runner, "checkout", "-q", "-b", RUNNER_REF.removeprefix("refs/heads/"))
        (runner / "runner-fixture.txt").write_bytes(b"Separate direct-child runner fixture.\n")
        self._git(runner, "add", "--all")
        self._git(runner, "commit", "-q", "-m", "runner direct child")
        self.runner_pin = self._git(runner, "rev-parse", "HEAD").decode().strip()
        self._git(runner, "push", "-q", self.bares["hybridclr_demo"].as_uri(), RUNNER_REF)
        self.proposal = {
            "schemaVersion": 1, "kind": observer.KIND, "sourcePins": dict(self.pins),
            "sourceRef": SOURCE_REF,
            "runner": {"repository": "night-outlook/hybridclr_demo",
                       "commit": self.runner_pin, "ref": RUNNER_REF},
            "locations": {"runnerRoot": str(runner), "workspace": str(self.workspace),
                          "historicalRoots": dict(self.history), "evidenceParent": str(self.evidence)},
            "scope": observer.SCOPE, "authorization": dict(CLOSED_AUTHORITY),
        }
        self.raw = canonical(self.proposal)
        self.pin = blob(self.raw)
        self.calls = []

    def _git(self, root, *args, data=None, check=True):
        result = subprocess.run(
            [self.git, "-c", "protocol.allow=never", "-c", "protocol.file.allow=always",
             "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
             "-C", str(root), *args], input=data, capture_output=True,
            env=self.env, timeout=30, check=check)
        return result.stdout if check else result

    def _route(self, command, environment):
        """Only the private subprocess seam is adapted to real file remotes."""
        self.assertEqual(command[0], self.git)
        self.assertEqual(command[-5:-2], ["ls-remote", "--exit-code", "--refs"])
        endpoint, ref = command[-2:]
        permitted = {"https://github.com/night-outlook/" + role + ".git": role
                     for role in ROLES[:-1]}
        self.assertIn(endpoint, permitted)
        role = permitted[endpoint]
        self.assertIn(ref, (SOURCE_REF, RUNNER_REF) if role == "hybridclr_demo" else (SOURCE_REF,))
        self.assertEqual(environment["GIT_ALLOW_PROTOCOL"], "https")
        self.assertIn("--git-dir=" + os.devnull, command)
        self.calls.append((list(command), dict(environment)))
        routed = list(command)
        routed[-2] = self.bares[role].as_uri()
        routed[routed.index("protocol.https.allow=always")] = "protocol.https.allow=never"
        position = routed.index("ls-remote")
        routed[position:position] = ["-c", "protocol.file.allow=always"]
        file_environment = dict(environment, GIT_ALLOW_PROTOCOL="file")
        return REAL_RUN_REMOTE(routed, file_environment)

    def _observe(self, proposal=None, raw=None, pin=None, transport=None):
        raw = raw if raw is not None else canonical(self.proposal if proposal is None else proposal)
        pin = blob(raw) if pin is None else pin
        with mock.patch.object(observer, "_run_remote", side_effect=transport or self._route):
            return observer.observe_five_identities(raw, pin)

    def _reject(self, proposal=None, raw=None, pin=None, transport=None, before_remote=False):
        start = len(self.calls)
        with self.assertRaises(observer.Rejected) as caught:
            self._observe(proposal, raw, pin, transport)
        report = caught.exception.report
        self.assertEqual(report["result"], observer.REJECTED_RESULT)
        self.assertIs(report["fixedFiveIdentityObservationVerified"], False)
        self.assertIs(report["fiveCheckoutObservationsMatched"], False)
        self.assertIs(report["fiveLiveRefObservationsMatched"], False)
        self._closed(report)
        if before_remote:
            self.assertEqual(report["remoteCallsAttempted"], [])
            self.assertEqual(len(self.calls), start)
            self.assertIs(report["networkMayHaveBeenUsed"], False)
        return report

    def _closed(self, report):
        for key, value in CLOSED_AUTHORITY.items():
            self.assertEqual(report[key], value, key)
            self.assertIs(type(report[key]), type(value), key)
        for key in FALSE_REPORT_FIELDS:
            self.assertIs(report[key], False, key)
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)
        self.assertEqual(report["independentlyReviewedFiveIdentityObservation"], "Pending")
        self.assertTrue(report["realSysPathUnchanged"])
        self.assertTrue(report["ambientCandidateModuleCacheUnchanged"])

    def _cli(self, *, flags=("-I", "-S", "-B"), raw=None, pin=None, extra=(), omit=(), path=None):
        proposal_path = self.evidence / "proposal.json" if path is None else path
        if path is None:
            proposal_path.write_bytes(self.raw if raw is None else raw)
        command = [sys.executable, *flags, str(MODULE_PATH)]
        if "proposal" not in omit:
            command += ["--proposal", str(proposal_path)]
        if "pin" not in omit:
            command += ["--expected-proposal-blob", self.pin if pin is None else pin]
        command.extend(extra)
        environment = dict(self.env, PYTHONPATH=str(self.roots["runner"]), PYTHONDONTWRITEBYTECODE="")
        return subprocess.run(command, capture_output=True, cwd=self.root,
                              env=environment, timeout=30, check=False)

    def test_01_real_five_checkouts_and_ten_remote_reads_remain_closed(self):
        before = inventory(self.root)
        observation = self._observe()
        report = observation.report
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertTrue(report["fixedFiveIdentityObservationVerified"])
        self.assertTrue(report["fiveCheckoutObservationsMatched"])
        self.assertTrue(report["fiveLiveRefObservationsMatched"])
        self.assertTrue(report["runnerSoleParentObserved"])
        self.assertEqual(report["localPassesCompleted"], ["before", "after"])
        self.assertEqual(report["remotePassesCompleted"], ["before", "after"])
        self.assertEqual(report["checkoutCallsAttempted"],
                         [{"pass": phase, "role": role} for phase in ("before", "after") for role in ROLES])
        self.assertEqual(report["remoteCallsAttempted"], report["checkoutCallsAttempted"])
        self.assertEqual(report["plannedReadOrder"],
                         ["locationsBefore", "localBefore", "remoteBefore", "remoteAfter", "localAfter", "locationsAfter"])
        self.assertEqual(len(self.calls), 10)
        for phase in ("before", "after"):
            self.assertEqual(set(report["checkoutObservations"][phase]), set(ROLES))
            self.assertEqual(set(report["remoteObservations"][phase]), set(ROLES))
            for role in ROLES:
                checkout = report["checkoutObservations"][phase][role]
                remote = report["remoteObservations"][phase][role]
                expected = self.runner_pin if role == "runner" else self.pins[role]
                self.assertEqual(checkout["head"], expected)
                self.assertEqual(remote["head"], expected)
                self.assertEqual(checkout["gitDir"], str(self.roots[role] / ".git"))
                self.assertEqual(checkout["commonDir"], checkout["gitDir"])
                self.assertEqual(remote["requestedTransport"], "https")
        self.assertFalse(report["sourcePinsMatchAcceptedAP1SiblingPins"])
        self.assertEqual(report["pinnedAP2HelperGitBlob"], AP2_PIN)
        self.assertEqual(report["pinnedAP1HelperGitBlob"], AP1_PIN)
        self.assertEqual(report["interpreterFlags"], {"isolated": True, "noSite": True, "noBytecodeWrites": True})
        self._closed(report)
        self.assertEqual(before, inventory(self.root))

    def test_02_pin_and_immutable_byte_type_reject_before_helper_or_transport(self):
        values = [(self.raw, "0" * 40), (self.raw, "A" * 40), (self.raw, 1),
                  (self.raw, "a" * 39), (bytearray(self.raw), self.pin),
                  (memoryview(self.raw), self.pin), (self.raw.decode(), self.pin),
                  (b"x" * (observer.MAX_BYTES + 1), "0" * 40)]
        for raw, pin in values:
            with self.subTest(type=type(raw).__name__, pin=pin):
                with mock.patch.object(observer, "_import_helper", side_effect=AssertionError("helper must not run")) as helper:
                    report = self._reject(raw=raw, pin=pin, before_remote=True)
                helper.assert_not_called()
                self.assertFalse(report["trustedHelperRegistered"])
                self.assertFalse(report["proposalSchemaValidated"])

    def test_03_closed_schema_types_roles_authority_and_endpoint_controls(self):
        changes = [(("schemaVersion",), True), (("schemaVersion",), 1.0),
                   (("kind",), "approval"), (("scope",), "execute"),
                   (("sourceRef",), "refs/heads/main"),
                   (("runner", "repository"), "someone/else"),
                   (("runner", "commit"), self.pins["hybridclr_demo"]),
                   (("runner", "commit"), "A" * 40),
                   (("sourcePins", "hybridclr"), 1),
                   (("sourcePins", "hybridclr_unity"), "0" * 39),
                   (("authorization", "allowNativeBuild"), True),
                   (("authorization", "R03Accepted"), 0),
                   (("authorization", "approvedEnvelopeGitBlob"), self.pin),
                   (("locations", "workspace"), []),
                   (("runner", "ref"), SOURCE_REF)]
        for path, value in changes:
            candidate = copy.deepcopy(self.proposal)
            target = candidate
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
            with self.subTest(path=path, value=value):
                self._reject(proposal=candidate, before_remote=True)
        for container, key in (((), "schemaVersion"), (("sourcePins",), "hybridclr"),
                               (("runner",), "commit"), (("locations",), "evidenceParent"),
                               (("authorization",), "H2Passed")):
            candidate = copy.deepcopy(self.proposal)
            target = candidate
            for part in container:
                target = target[part]
            del target[key]
            with self.subTest(missing=container + (key,)):
                self._reject(proposal=candidate, before_remote=True)
        for container, key in (((), "remoteUrl"), ((), "mode"), ((), "report"),
                               (("runner",), "transport"), (("sourcePins",), "extra"),
                               (("locations",), "sourceRoots"), (("authorization",), "execute")):
            candidate = copy.deepcopy(self.proposal)
            target = candidate
            for part in container:
                target = target[part]
            target[key] = "file:///not-a-production-endpoint"
            with self.subTest(extra=container + (key,)):
                self._reject(proposal=candidate, before_remote=True)

        metadata_only = copy.deepcopy(self.proposal)
        metadata_only["sourcePins"].update({
            "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
            "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
            "il2cpp_plus": "1268dd417ffe9090fcd9ea2d49542c97ed3cccb3",
        })
        metadata_report = self._reject(proposal=metadata_only, before_remote=True)
        self.assertTrue(metadata_report["proposalSchemaValidated"])
        self.assertTrue(metadata_report["sourcePinsMatchAcceptedAP1SiblingPins"])
        self.assertFalse(metadata_report["acceptedAP1SourceTupleVerified"])

    def test_04_strict_json_rejects_duplicates_nonfinite_invalid_and_nonobject(self):
        duplicates = [self.raw.replace(b'"schemaVersion": 1', b'"schemaVersion": 1, "schemaVersion": 1', 1),
                      self.raw.replace(b'"allowNativeBuild": false', b'"allowNativeBuild": false, "allowNativeBuild": false', 1)]
        cases = [b"[]", b"null", b"true", b'{"x":"\xff"}', b'{"schemaVersion":NaN}',
                 b'{"schemaVersion":Infinity}', b'{"schemaVersion":-Infinity}',
                 b"[" * 1200 + b"0" + b"]" * 1200, *duplicates]
        for raw in cases:
            with self.subTest(prefix=raw[:50]):
                self._reject(raw=raw, before_remote=True)

    def test_05_exact_runner_ref_spelling_rejects_patterns_and_aliases(self):
        for ref in ("main", "refs/heads/main", "refs/tags/codex/x", "refs/heads/codex/",
                    "refs/heads/codex/a..b", "refs/heads/codex/a.lock", "refs/heads/codex/a.",
                    "refs/heads/codex/a*b", "refs/heads/codex/a b", "refs/heads/codex/a@{b",
                    "refs/heads/codex/a\\b", "refs/heads/codex/.hidden", "refs/heads/codex/" + "x" * 240):
            proposal = copy.deepcopy(self.proposal)
            proposal["runner"]["ref"] = ref
            with self.subTest(ref=ref):
                self._reject(proposal=proposal, before_remote=True)

    def test_06_missing_untracked_ignored_and_raw_modified_files_reject(self):
        checkout = self.roots["hybridclr"]
        tracked = checkout / "tracked.txt"
        saved = tracked.read_bytes()
        for kind in ("modified", "missing", "untracked", "ignored", "empty-directory"):
            with self.subTest(kind=kind):
                if kind == "modified":
                    tracked.write_bytes(saved.replace(b"\n", b"\r\n"))
                elif kind == "missing":
                    tracked.unlink()
                elif kind == "untracked":
                    (checkout / "untracked").write_bytes(b"untracked\n")
                elif kind == "ignored":
                    (checkout / "ignored-data").write_bytes(b"ignored\n")
                else:
                    (checkout / "untracked-directory").mkdir()
                report = self._reject(before_remote=True)
                self.assertEqual(report["checkoutCallsAttempted"][-1]["role"], "hybridclr")
                tracked.write_bytes(saved)
                for name in ("untracked", "ignored-data"):
                    (checkout / name).unlink(missing_ok=True)
                if (checkout / "untracked-directory").exists():
                    (checkout / "untracked-directory").rmdir()

    def test_07_staged_assumed_skipped_and_submodule_index_reject(self):
        checkout = self.roots["hybridclr_unity"]
        tracked = checkout / "tracked.txt"
        original = tracked.read_bytes()
        for kind in ("staged", "assumed", "skipped", "submodule", "unmerged"):
            with self.subTest(kind=kind):
                if kind == "staged":
                    tracked.write_bytes(b"different staged bytes\n")
                    self._git(checkout, "add", "tracked.txt")
                elif kind == "assumed":
                    self._git(checkout, "update-index", "--assume-unchanged", "tracked.txt")
                elif kind == "skipped":
                    self._git(checkout, "update-index", "--skip-worktree", "tracked.txt")
                elif kind == "submodule":
                    self._git(checkout, "update-index", "--add", "--cacheinfo",
                              "160000," + self.pins["hybridclr_unity"] + ",submodule")
                else:
                    oid = blob(original)
                    data = ("0 " + "0" * 40 + "\ttracked.txt\n100644 " + oid + " 1\ttracked.txt\n").encode()
                    self._git(checkout, "update-index", "--index-info", data=data)
                self._reject(before_remote=True)
                self._git(checkout, "update-index", "--no-assume-unchanged", "--no-skip-worktree", "tracked.txt", check=False)
                self._git(checkout, "reset", "--hard", "-q", self.pins["hybridclr_unity"])

    def test_08_modes_hardlinks_symlink_replacement_and_special_files_reject(self):
        checkout = self.roots["il2cpp_plus"]
        path = checkout / "tracked.txt"
        raw = path.read_bytes()
        for kind in ("mode", "hardlink", "symlink", "fifo", "directory"):
            with self.subTest(kind=kind):
                if kind == "mode":
                    path.chmod(0o755)
                elif kind == "hardlink":
                    os.link(path, self.root / "outside-hardlink")
                else:
                    path.unlink()
                    if kind == "symlink":
                        path.symlink_to(self.root / "absent-target")
                    elif kind == "fifo":
                        os.mkfifo(path)
                    else:
                        path.mkdir()
                self._reject(before_remote=True)
                (self.root / "outside-hardlink").unlink(missing_ok=True)
                if path.is_dir():
                    path.rmdir()
                else:
                    path.unlink()
                path.write_bytes(raw)
                path.chmod(0o644)

    def test_09_tracked_symlink_literal_is_observed_without_target_read(self):
        checkout = self.roots["hybridclr"]
        target = self.root / "outside-link-target"
        target.write_bytes(b"The target is outside checkout scope.\n")
        link = checkout / "tracked-link"
        link.symlink_to(target)
        self._git(checkout, "add", "tracked-link")
        self._git(checkout, "commit", "-q", "-m", "literal symlink fixture")
        commit = self._git(checkout, "rev-parse", "HEAD").decode().strip()
        self._git(checkout, "push", "-q", self.bares["hybridclr"].as_uri(), SOURCE_REF)
        proposal = copy.deepcopy(self.proposal)
        proposal["sourcePins"]["hybridclr"] = commit
        target.unlink()
        report = self._observe(proposal=proposal).report
        self.assertEqual(report["result"], observer.SUCCESS_RESULT)
        self.assertFalse(target.exists())
        self.assertTrue(link.is_symlink())
        self._closed(report)

    def test_10_origins_and_unsupported_local_configuration_reject(self):
        checkout = self.roots["hybridclr"]
        config = checkout / ".git/config"
        original = config.read_bytes()
        settings = [("remote.origin.url", "https://github.com/someone/hybridclr.git"),
                    ("filter.fixture.clean", "unused-nonexistent-command"),
                    ("url.file:///unused.insteadOf", "https://github.com/"),
                    ("core.worktree", str(checkout)), ("core.ignorestat", "true"),
                    ("core.sparsecheckout", "true"), ("core.sparsecheckoutcone", "true"),
                    ("core.splitindex", "true"), ("diff.external", "unused-nonexistent-command"),
                    ("include.path", str(self.root / "absent-config")),
                    ("remote.origin.promisor", "true"), ("remote.origin.partialclonefilter", "blob:none"),
                    ("extensions.worktreeConfig", "true")]
        for key, value in settings:
            with self.subTest(key=key):
                self._git(checkout, "config", "--local", key, value)
                self._reject(before_remote=True)
                config.write_bytes(original)
        self._git(checkout, "config", "--local", "--add", "remote.origin.url",
                  "https://github.com/night-outlook/hybridclr.git")
        self._reject(before_remote=True)

    def test_11_shallow_grafted_alternate_gitfiles_and_bare_layout_reject(self):
        checkout = self.roots["hybridclr"]
        git_dir = checkout / ".git"
        for relative in ("shallow", "info/grafts", "objects/info/alternates"):
            path = git_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"")
            with self.subTest(relative=relative):
                self._reject(before_remote=True)
            path.unlink()
        saved = self.root / "saved-admin"
        git_dir.rename(saved)
        git_dir.write_text("gitdir: " + str(saved) + "\n", encoding="utf-8")
        self._reject(before_remote=True)
        git_dir.unlink()
        git_dir.symlink_to(saved, target_is_directory=True)
        self._reject(before_remote=True)
        git_dir.unlink()
        saved.rename(git_dir)
        self._git(checkout, "config", "core.bare", "true")
        self._reject(before_remote=True)

    def test_12_detached_wrong_branch_symbolic_ref_and_wrong_head_reject(self):
        checkout = self.roots["hybridclr"]
        pin = self.pins["hybridclr"]
        self._git(checkout, "checkout", "--detach", "-q", pin)
        self._reject(before_remote=True)
        self._git(checkout, "checkout", "-q", SOURCE_REF.removeprefix("refs/heads/"))
        self._git(checkout, "checkout", "-q", "-b", "codex/different")
        self._reject(before_remote=True)
        self._git(checkout, "checkout", "-q", SOURCE_REF.removeprefix("refs/heads/"))
        self._git(checkout, "update-ref", "refs/heads/codex/alias-target", pin)
        self._git(checkout, "symbolic-ref", SOURCE_REF, "refs/heads/codex/alias-target")
        self._reject(before_remote=True)
        self._git(checkout, "symbolic-ref", "--delete", SOURCE_REF)
        self._git(checkout, "update-ref", SOURCE_REF, pin)
        self._git(checkout, "commit", "--allow-empty", "-q", "-m", "head drift")
        self._reject(before_remote=True)

    def test_13_locations_reject_aliases_overlap_missing_and_duplicate_history(self):
        alias = self.root / "workspace-alias"
        alias.symlink_to(self.workspace, target_is_directory=True)
        changes = [("workspace", str(alias)), ("workspace", str(self.workspace) + "/."),
                   ("workspace", str(self.workspace) + "/../workspace"),
                   ("workspace", "relative"), ("evidenceParent", str(self.workspace / "hybridclr")),
                   ("runnerRoot", str(self.roots["hybridclr_demo"])),
                   ("runnerRoot", str(self.roots["runner"] / "nested")),
                   ("evidenceParent", str(self.root / "missing"))]
        for key, value in changes:
            proposal = copy.deepcopy(self.proposal)
            proposal["locations"][key] = value
            with self.subTest(key=key, value=value):
                self._reject(proposal=proposal, before_remote=True)
        proposal = copy.deepcopy(self.proposal)
        proposal["locations"]["historicalRoots"]["originalS"] = str(self.workspace)
        self._reject(proposal=proposal, before_remote=True)
        proposal = copy.deepcopy(self.proposal)
        proposal["locations"]["historicalRoots"]["originalS"] = self.history["b1EvidenceBase"]
        self._reject(proposal=proposal, before_remote=True)
        saved = self.root / "saved-source"
        self.roots["hybridclr"].rename(saved)
        self.roots["hybridclr"].symlink_to(self.roots["hybridclr_unity"], target_is_directory=True)
        self._reject(before_remote=True)

    def test_14_all_fifteen_administrative_roots_must_have_unique_identities(self):
        for first, second in (("gitDir", "gitDir"), ("objects", "objects"), ("refs", "refs"), ("objects", "refs")):
            seen = {}
            def collide(ap2, ap1, identity):
                result = REAL_OBSERVE_CHECKOUT(ap2, ap1, identity)
                if identity["role"] == "hybridclr_demo":
                    seen["first"] = dict(result["gitAdministrativeDirectoryIdentities"][first])
                if identity["role"] == "runner":
                    result["gitAdministrativeDirectoryIdentities"][second] = seen["first"]
                return result
            with self.subTest(first=first, second=second):
                with mock.patch.object(observer, "_observe_checkout", side_effect=collide):
                    report = self._reject(before_remote=True)
                self.assertEqual(len(report["checkoutObservations"]["before"]), 5)
                self.assertEqual(report["localPassesCompleted"], [])

    def test_15_runner_requires_the_demo_source_as_its_only_parent(self):
        checkout = self.roots["runner"]
        tree = self._git(checkout, "rev-parse", "HEAD^{tree}").decode().strip()
        demo = self.pins["hybridclr_demo"]
        for label, parents in (("zero", ()), ("wrong", (self.runner_pin,)),
                               ("merge", (demo, self.runner_pin))):
            args = ["commit-tree", tree]
            for parent in parents:
                args += ["-p", parent]
            commit = self._git(checkout, *args, data=(label + " parent fixture\n").encode()).decode().strip()
            self._git(checkout, "update-ref", RUNNER_REF, commit)
            self._git(checkout, "reset", "--hard", "-q", commit)
            proposal = copy.deepcopy(self.proposal)
            proposal["runner"]["commit"] = commit
            with self.subTest(topology=label):
                report = self._reject(proposal=proposal, before_remote=True)
                self.assertIn("sole commit parent", report["reason"])
                self.assertEqual(len(report["checkoutObservations"]["before"]), 5)
                self.assertFalse(report["runnerSoleParentObserved"])

    def test_16_exact_remote_parser_rejects_ambiguous_malformed_and_changed_rows(self):
        good = (self.pins["hybridclr"] + "\t" + SOURCE_REF + "\n").encode()
        self.assertEqual(observer._exact_remote_head(good, SOURCE_REF, self.pins["hybridclr"]), self.pins["hybridclr"])
        bad = [b"", good + good, good + b"\n", good.replace(b"\t", b" "),
               good.replace(SOURCE_REF.encode(), b"refs/heads/wrong"),
               ("0" * 40 + "\t" + SOURCE_REF + "\n").encode(),
               good.upper(), b"\xff\t" + SOURCE_REF.encode() + b"\n",
               good.replace(b"\t", b"\t\t"), b"x" * (observer.MAX_REMOTE_BYTES + 1),
               bytearray(good), good.decode()]
        for raw in bad:
            with self.subTest(prefix=repr(raw)[:80]):
                with self.assertRaises((ValueError, UnicodeError)):
                    observer._exact_remote_head(raw, SOURCE_REF, self.pins["hybridclr"])

    def test_17_real_bare_remote_missing_and_drifted_refs_reject(self):
        bare = self.bares["hybridclr"]
        self._git(bare, "update-ref", "-d", SOURCE_REF)
        report = self._reject()
        self.assertEqual(report["remoteCallsAttempted"],
                         [{"pass": "before", "role": "hybridclr_demo"}, {"pass": "before", "role": "hybridclr"}])
        self.assertEqual(set(report["remoteObservations"]["before"]), {"hybridclr_demo"})
        self.assertTrue(report["networkMayHaveBeenUsed"])
        self._git(bare, "update-ref", SOURCE_REF, self.pins["hybridclr"])
        calls = 0
        def drift(command, environment):
            nonlocal calls
            calls += 1
            if calls == 6:
                self._git(self.bares["hybridclr_demo"], "update-ref", SOURCE_REF, self.runner_pin)
            return self._route(command, environment)
        report = self._reject(transport=drift)
        self.assertEqual(report["remotePassesCompleted"], ["before"])
        self.assertEqual(report["remoteCallsAttempted"][-1], {"pass": "after", "role": "hybridclr_demo"})
        self.assertEqual(report["checkoutObservations"]["after"], {})

    def test_18_remote_subprocess_errors_bounds_and_no_fallback_keep_progress(self):
        good = (self.pins["hybridclr_demo"] + "\t" + SOURCE_REF + "\n").encode()
        cases = [OSError("fixture transport unavailable"), subprocess.TimeoutExpired(["git"], 30),
                 subprocess.CompletedProcess([], 1, b"", b"fixture failure"),
                 subprocess.CompletedProcess([], 0, good + good, b""),
                 subprocess.CompletedProcess([], 0, good, b"x" * (observer.MAX_REMOTE_BYTES + 1)),
                 subprocess.CompletedProcess([], 0, b"x" * (observer.MAX_REMOTE_BYTES + 1), b""),
                 subprocess.CompletedProcess([], 0, good.decode(), b""),
                 subprocess.CompletedProcess([], 0, good, "not bytes")]
        for item in cases:
            count = 0
            def fail(command, environment):
                nonlocal count
                count += 1
                if isinstance(item, Exception):
                    raise item
                return item
            with self.subTest(case=type(item).__name__, stdout=str(getattr(item, "stdout", ""))[:40]):
                report = self._reject(transport=fail)
                self.assertEqual(count, 1)
                self.assertEqual(report["localPassesCompleted"], ["before"])
                self.assertEqual(report["remotePassesCompleted"], [])
                self.assertEqual(report["remoteObservations"], {"before": {}, "after": {}})
                self.assertEqual(report["remoteCallsAttempted"], [{"pass": "before", "role": "hybridclr_demo"}])
                self.assertTrue(report["remoteProcessLaunchMayHaveBeenAttempted"])

    def test_19_production_remote_arguments_and_environment_are_fixed(self):
        identity = observer._identities(self.proposal)[-1]
        inherited = {"GIT_DIR": "/unused", "GIT_WORK_TREE": "/unused", "GIT_NAMESPACE": "fixture",
                     "GIT_CONFIG_PARAMETERS": "'url.file:///unused.insteadOf=https://github.com/'",
                     "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.proxy", "GIT_CONFIG_VALUE_0": "unused",
                     "GIT_EXEC_PATH": "/unused", "GIT_ASKPASS": "/unused-askpass",
                     "SSH_ASKPASS": "/unused-askpass", "GIT_SSH_COMMAND": "unused-command",
                     "HTTPS_PROXY": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9",
                     "ALL_PROXY": "http://127.0.0.1:9", "GIT_SSL_NO_VERIFY": "1",
                     "GIT_CONFIG_GLOBAL": "/unused", "GIT_CONFIG_SYSTEM": "/unused", "PATH": "/unused"}
        with mock.patch.dict(os.environ, inherited):
            command, environment = observer._remote_invocation(identity)
        self.assertEqual(command[0], self.git)
        self.assertNotIn("-C", command)
        self.assertIn("--git-dir=" + os.devnull, command)
        self.assertEqual(command[-5:], ["ls-remote", "--exit-code", "--refs",
                                         "https://github.com/night-outlook/hybridclr_demo.git", RUNNER_REF])
        for setting in ("protocol.allow=never", "protocol.https.allow=always", "core.fsmonitor=false",
                        "core.hooksPath=" + os.devnull, "credential.helper=", "credential.interactive=false",
                        "core.askPass=", "http.proxy=", "http.followRedirects=false", "http.sslVerify=true",
                        "http.extraHeader=", "http.cookieFile=" + os.devnull, "http.saveCookies=false"):
            self.assertIn(setting, command)
        self.assertEqual(environment, {
            "PATH": os.defpath, "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_COUNT": "0",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1", "GIT_ATTR_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "https"})
        completed = subprocess.CompletedProcess(command, 0, b"", b"")
        with mock.patch.object(subprocess, "run", return_value=completed) as run:
            self.assertIs(REAL_RUN_REMOTE(command, environment), completed)
        run.assert_called_once_with(command, input=b"", capture_output=True, cwd="/", env=environment,
                                    timeout=observer.REMOTE_TIMEOUT_SECONDS, check=False)

    def test_20_null_gitdir_blocks_benign_cwd_rewrite_without_any_network(self):
        checkout = self.roots["hybridclr_demo"]
        bare = self.bares["hybridclr_demo"]
        identity = observer._identities(self.proposal)[0]
        endpoint = "https://github.com/night-outlook/hybridclr_demo.git"
        self._git(checkout, "config", "url." + bare.as_uri() + ".insteadOf", endpoint)
        command, environment = observer._remote_invocation(identity)
        # A file-only gate makes this selected-system-Git behavior test incapable
        # of HTTPS access. The URL remains the actual production HTTPS endpoint.
        file_environment = dict(environment, GIT_ALLOW_PROTOCOL="file")
        position = command.index("ls-remote")
        tested = command[:position] + ["-c", "protocol.file.allow=always"] + command[position:]
        no_context = subprocess.run(tested, input=b"", capture_output=True, cwd=checkout,
                                    env=file_environment, timeout=30, check=False)
        self.assertNotEqual(no_context.returncode, 0)
        self.assertIn(b"transport 'https' not allowed", no_context.stderr)
        inherited = dict(os.environ, GIT_DIR=str(checkout / ".git"),
                         GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="url." + bare.as_uri() + ".insteadOf",
                         GIT_CONFIG_VALUE_0=endpoint, GIT_ASKPASS=str(self.root / "nonexistent-askpass"),
                         HTTPS_PROXY="http://127.0.0.1:9", GIT_SSL_NO_VERIFY="1")
        with mock.patch.dict(os.environ, inherited, clear=True):
            fresh_command, fresh_environment = observer._remote_invocation(identity)
        self.assertEqual(fresh_command, command)
        self.assertEqual(fresh_environment, environment)
        ambient_context = [arg for arg in tested if arg != "--git-dir=" + os.devnull]
        rewritten = subprocess.run(ambient_context, input=b"", capture_output=True, cwd=checkout,
                                   env=file_environment, timeout=30, check=False)
        self.assertEqual(rewritten.returncode, 0, rewritten.stderr.decode())
        self.assertEqual(observer._exact_remote_head(rewritten.stdout, SOURCE_REF, self.pins["hybridclr_demo"]),
                         self.pins["hybridclr_demo"])

    def test_21_second_pass_uses_ten_fresh_local_readers_and_order(self):
        readers, events = [], []
        def checkout(ap2, ap1, identity):
            factory = ap1._Git
            def fresh(root):
                reader = factory(root)
                readers.append(reader)
                return reader
            with mock.patch.object(ap1, "_Git", side_effect=fresh):
                result = REAL_OBSERVE_CHECKOUT(ap2, ap1, identity)
            events.append("local:" + identity["role"])
            return result
        def locations(ap2, proposal, identities):
            events.append("locations")
            return REAL_OBSERVE_LOCATIONS(ap2, proposal, identities)
        def remote(command, environment):
            events.append("remote:" + ("runner" if command[-1] == RUNNER_REF else command[-2].rsplit("/", 1)[1][:-4]))
            return self._route(command, environment)
        with mock.patch.object(observer, "_observe_checkout", side_effect=checkout), \
             mock.patch.object(observer, "_observe_locations", side_effect=locations):
            self._observe(transport=remote)
        self.assertEqual(len(readers), 10)
        self.assertEqual(len({id(reader) for reader in readers}), 10)
        self.assertEqual(events, ["locations"] + ["local:" + role for role in ROLES] +
                         ["remote:" + role for role in ROLES] * 2 + ["local:" + role for role in ROLES] + ["locations"])

    def test_22_second_pass_rejects_changed_config_index_worktree_and_local_ref(self):
        checkout = self.roots["hybridclr"]
        config = checkout / ".git/config"
        original_config = config.read_bytes()
        for kind in ("config", "index", "worktree", "ref"):
            count = 0
            def change(command, environment):
                nonlocal count
                count += 1
                result = self._route(command, environment)
                if count == 10:
                    if kind == "config":
                        self._git(checkout, "config", "ap5.fixture", "changed")
                    elif kind == "index":
                        self._git(checkout, "update-index", "--assume-unchanged", "tracked.txt")
                    elif kind == "worktree":
                        (checkout / "tracked.txt").write_bytes(b"changed after remote pass\n")
                    else:
                        self._git(checkout, "commit", "--allow-empty", "-q", "-m", "second-pass drift")
                return result
            with self.subTest(kind=kind):
                report = self._reject(transport=change)
                self.assertEqual(report["remotePassesCompleted"], ["before", "after"])
                self.assertEqual(report["localPassesAttempted"], ["before", "after"])
                self.assertEqual(report["locationObservations"].keys(), {"before"})
                config.write_bytes(original_config)
                self._git(checkout, "update-index", "--no-assume-unchanged", "tracked.txt", check=False)
                self._git(checkout, "reset", "--hard", "-q", self.pins["hybridclr"])

    def test_23_second_pass_rejects_changed_checkout_and_admin_directory_identity(self):
        for kind in ("checkout", "admin"):
            checkout = self.roots["hybridclr"]
            target = checkout if kind == "checkout" else checkout / ".git"
            saved = self.root / ("saved-" + kind)
            count = 0
            def change(command, environment):
                nonlocal count
                count += 1
                result = self._route(command, environment)
                if count == 10:
                    target.rename(saved)
                    shutil.copytree(saved, target, symlinks=True)
                return result
            with self.subTest(kind=kind):
                report = self._reject(transport=change)
                self.assertEqual(report["localPassesCompleted"], ["before", "after"])
                self.assertIn("Checkout state changed", report["reason"])
                shutil.rmtree(target)
                saved.rename(target)

    def test_24_final_location_recheck_rejects_changed_historical_identity(self):
        count = 0
        history = Path(self.history["originalS"])
        saved = self.root / "saved-history"
        def change(command, environment):
            nonlocal count
            count += 1
            result = self._route(command, environment)
            if count == 10:
                history.rename(saved)
                history.mkdir()
            return result
        report = self._reject(transport=change)
        self.assertEqual(report["localPassesCompleted"], ["before", "after"])
        self.assertEqual(set(report["locationObservations"]), {"before", "after"})
        self.assertIn("Declared locations changed", report["reason"])

    def test_25_response_bytes_are_rechecked_even_when_parsed_head_is_unchanged(self):
        count = 0
        def change(command, environment):
            nonlocal count
            count += 1
            result = self._route(command, environment)
            if count == 6:
                return subprocess.CompletedProcess(command, 0, result.stdout.replace(b"\n", b"\r\n"), result.stderr)
            return result
        report = self._reject(transport=change)
        self.assertEqual(report["remotePassesCompleted"], ["before", "after"])
        self.assertEqual(report["localPassesCompleted"], ["before"])
        self.assertIn("Remote responses changed", report["reason"])

    def test_26_helper_pins_authenticate_original_bytes_and_cleanup_all_outcomes(self):
        self.assertEqual(observer.AP2_HELPER_BLOB, AP2_PIN)
        self.assertEqual(blob((HERE / observer.AP2_HELPER_NAME).read_bytes()), AP2_PIN)
        self.assertEqual(blob((HERE / "d5b_activation_publication.py").read_bytes()), AP1_PIN)
        before = {key: value for key, value in sys.modules.items() if key.startswith("_ap5_verified_ap2_")}
        real_read = observer._read_absolute
        def changed_ap2(path):
            value = real_read(path)
            return value + b"\n# inert byte drift\n" if path.name == observer.AP2_HELPER_NAME else value
        with mock.patch.object(observer, "_read_absolute", side_effect=changed_ap2):
            report = self._reject(before_remote=True)
        self.assertFalse(report["trustedHelperRegistered"])
        self.assertFalse(report["trustedHelperRegistrationRemoved"])
        original_helper = observer._import_helper
        from contextlib import contextmanager
        @contextmanager
        def bad_ap1(progress):
            with original_helper(progress) as ap2:
                original_ap1_read = ap2._read_absolute
                def read(path):
                    value = original_ap1_read(path)
                    return value + b"\n# inert byte drift\n" if path.name == "d5b_activation_publication.py" else value
                with mock.patch.object(ap2, "_read_absolute", side_effect=read):
                    yield ap2
        with mock.patch.object(observer, "_import_helper", bad_ap1):
            report = self._reject(before_remote=True)
        self.assertTrue(report["trustedHelperRegistered"])
        self.assertTrue(report["trustedHelperRegistrationRemoved"])
        report = self._observe().report
        self.assertTrue(report["trustedHelperRegistered"])
        self.assertTrue(report["trustedHelperRegistrationRemoved"])
        rejected = self._reject(raw=b"{}", before_remote=True)
        self.assertTrue(rejected["trustedHelperRegistrationRemoved"])
        after = {key: value for key, value in sys.modules.items() if key.startswith("_ap5_verified_ap2_")}
        self.assertEqual(before, after)

    def test_27_candidate_modules_remain_inert_and_process_and_files_unchanged(self):
        candidates = {name: ModuleType(name) for name in observer.CANDIDATE_NAMES}
        before_path, contents = sys.path, tuple(sys.path)
        before = inventory(self.root)
        original_import = builtins.__import__
        def guard(name, *args, **kwargs):
            self.assertNotIn(name.split(".")[0], observer.CANDIDATE_NAMES)
            return original_import(name, *args, **kwargs)
        with mock.patch.dict(sys.modules, candidates), mock.patch.object(builtins, "__import__", side_effect=guard):
            result = self._observe()
            for name, module in candidates.items():
                self.assertIs(sys.modules[name], module)
        self.assertIs(sys.path, before_path)
        self.assertEqual(tuple(sys.path), contents)
        self.assertEqual(before, inventory(self.root))
        self.assertEqual(list(self.evidence.iterdir()), [])
        self.assertFalse(any(self.root.rglob("__pycache__")))
        self._closed(result.report)

    def test_28_public_api_and_report_are_narrow_and_frozen(self):
        self.assertEqual(tuple(inspect.signature(observer.observe_five_identities).parameters),
                         ("raw", "expected_proposal_blob"))
        observation = self._observe()
        self.assertIsInstance(observation._report_json, bytes)
        original = observation._report_json
        report = observation.report
        report["authorization"] = {"execute": True}
        report["sourcePins"]["hybridclr"] = "0" * 40
        report["checkoutObservations"]["before"].clear()
        self.assertEqual(observation._report_json, original)
        self.assertEqual(observation.report["sourcePins"], self.proposal["sourcePins"])
        self.assertEqual(len(observation.report["checkoutObservations"]["before"]), 5)
        with self.assertRaises(FrozenInstanceError):
            observation._report_json = b"{}"
        for keyword in ("transport", "remote_url", "policy", "report", "mode", "execute"):
            with self.subTest(keyword=keyword):
                with self.assertRaises(TypeError):
                    observer.observe_five_identities(self.raw, self.pin, **{keyword: object()})
        with self.assertRaises(observer.Rejected) as caught:
            self._observe(raw=b"{}")
        rejected = caught.exception.report
        rejected["executionAuthorityVerified"] = True
        self.assertFalse(caught.exception.report["executionAuthorityVerified"])

    def test_29_real_cli_requires_all_isolation_flags_before_transport(self):
        for flags in (("-S", "-B"), ("-I", "-B"), ("-I", "-S")):
            with self.subTest(flags=flags):
                result = self._cli(flags=flags)
                self.assertEqual(result.returncode, 2, result.stderr.decode())
                self.assertEqual(result.stderr, b"")
                report = json.loads(result.stdout)
                self.assertIn("Python -I -S -B", report["reason"])
                self.assertEqual(report["remoteCallsAttempted"], [])
                self.assertFalse(report["trustedHelperRegistered"])
                self._closed(report)

    def test_30_real_cli_argument_and_pretransport_rejections(self):
        for omit in (("proposal",), ("pin",), ("proposal", "pin")):
            result = self._cli(omit=omit)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, b"")
            self.assertIn(b"required", result.stderr)
        for extra in (("--execute",), ("--mode", "preview"), ("--remote-url", "file:///unused"),
                      ("--approved-envelope-blob", self.pin), ("--allow-player-launch",),
                      ("--allow-native-build",), ("--report", "unused")):
            with self.subTest(extra=extra):
                result = self._cli(extra=extra)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"unrecognized arguments", result.stderr)
        cases = [(self.raw, "0" * 40), (b"{}", blob(b"{}")), (b"[]", blob(b"[]"))]
        for raw, pin in cases:
            result = self._cli(raw=raw, pin=pin)
            self.assertEqual(result.returncode, 2, result.stderr.decode())
            self.assertEqual(result.stderr, b"")
            report = json.loads(result.stdout)
            self.assertEqual(report["remoteCallsAttempted"], [])
            self.assertFalse(report["networkMayHaveBeenUsed"])
            self._closed(report)
        for name in ("missing.json", "relative.json"):
            path = self.root / name if name == "missing.json" else Path(name)
            result = self._cli(path=path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["remoteCallsAttempted"], [])

    def test_31_real_cli_input_symlinks_hardlinks_and_executable_files_reject(self):
        original = self.evidence / "input.json"
        original.write_bytes(self.raw)
        alias = self.evidence / "alias.json"
        alias.symlink_to(original)
        result = self._cli(path=alias)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["remoteCallsAttempted"], [])
        alias.unlink()
        os.link(original, alias)
        result = self._cli(path=alias)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["remoteCallsAttempted"], [])
        alias.unlink()
        original.chmod(0o755)
        result = self._cli(path=original)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["remoteCallsAttempted"], [])


if __name__ == "__main__":
    unittest.main()
