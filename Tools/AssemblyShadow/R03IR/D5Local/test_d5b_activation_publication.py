#!/usr/bin/env python3
"""AP1 object-only publication tests; no Local, Unity, Player, or remote writes."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import d5b_activation_publication as publication
import d5b_local_admission as gate


REVIEWED_WRITER_BLOB = "99746fe64976da313cbd0e1625f0fcc5a67bca62"
WRITER_PATH = "Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py"
PLAN_PATH = "Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json"
WRAPPER_PATH = "Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py"
PREFLIGHT_PATH = "Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py"
ENVELOPE_PATH = (
    "Tools/AssemblyShadow/R03IR/D5Local/"
    "d5b_activation_publication_proposal_v1.json")
SOURCE_PATH = "Assets/PublicationFixture.cs"
PROPOSAL_KIND = "R03D5BActivationPublicationProposalV1"
ANCHOR = b"APPROVED_EXECUTION_ENVELOPE_BLOB = None\n"


class D5BActivationPublicationSourceOnly(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "objects-only-repository"
        self.repo.mkdir()
        self.git_environment = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")}
        self.git_environment.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "AP1 Synthetic Source Fixture",
            "GIT_AUTHOR_EMAIL": "ap1-fixture@example.invalid",
            "GIT_COMMITTER_NAME": "AP1 Synthetic Source Fixture",
            "GIT_COMMITTER_EMAIL": "ap1-fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-26T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2026-11-26T00:00:00+0000",
        })
        self._git("init", "-q", "--object-format=sha1")
        self.sequence = 0
        self.source_ref = "refs/heads/" + gate.BRANCH
        self.runner_ref = "refs/heads/ap1-structural-runner-fixture"
        checkout = Path(__file__).resolve().parents[4]
        self.fixture_bytes = {
            name: (checkout / name).read_bytes()
            for name in (WRITER_PATH, PLAN_PATH, WRAPPER_PATH, PREFLIGHT_PATH)}
        self.fixture_bytes[SOURCE_PATH] = b"// Synthetic tree-delta sentinel.\n"
        self.writer_raw = self.fixture_bytes[WRITER_PATH]
        self.assertEqual(self.writer_raw.count(ANCHOR), 1)
        self.source_entries = {
            name: ("100644", "blob", self._blob(raw))
            for name, raw in self.fixture_bytes.items()}
        self.assertEqual(self.source_entries[WRITER_PATH][2], REVIEWED_WRITER_BLOB)
        self.closed_authority = json.loads(
            self.fixture_bytes[PLAN_PATH])["authorization"]
        self.source_commit = self._commit(self.source_entries)
        (self.runner_commit, self.proposal_raw, self.envelope_blob,
         self.runner_entries) = self._runner()
        self._git("update-ref", self.source_ref, self.source_commit)
        self._git("update-ref", self.runner_ref, self.runner_commit)


    def _git(self, *arguments, data=None):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *arguments], input=data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.git_environment, check=True)
        return result.stdout

    def _blob(self, raw):
        return self._git("hash-object", "-w", "--stdin", data=raw).decode().strip()

    def _tree(self, entries):
        root = {}
        for path, entry in entries.items():
            components = path.split("/")
            directory = root
            for component in components[:-1]:
                directory = directory.setdefault(component, {})
            directory[components[-1]] = entry

        def store(directory):
            records = []
            for name, value in sorted(directory.items()):
                if isinstance(value, dict):
                    mode, kind, oid = "040000", "tree", store(value)
                else:
                    mode, kind, oid = value
                records.append(f"{mode} {kind} {oid}\t{name}\0".encode("utf-8"))
            return self._git("mktree", "-z", data=b"".join(records)).decode().strip()

        return store(root)

    def _commit(self, entries, parents=()):
        arguments = ["commit-tree", self._tree(entries)]
        for parent in parents:
            arguments.extend(("-p", parent))
        self.sequence += 1
        message = f"AP1 synthetic object fixture {self.sequence}\n".encode()
        return self._git(*arguments, data=message).decode().strip()

    def _proposal(self, source_commit=None):
        return {
            "schemaVersion": 1, "kind": PROPOSAL_KIND, "branch": gate.BRANCH,
            "sourcePins": {
                "hybridclr_demo": source_commit or self.source_commit,
                **gate.source.PINS,
            },
            "scope": "NoUnityOrPlayerLaunch",
            "authorization": copy.deepcopy(self.closed_authority),
        }

    def _encode(self, value):
        return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()

    def _runner(self, *, source_commit=None, source_entries=None,
                proposal_raw=None, writer_pin=None, writer_raw=None,
                changes=None, parents=None):
        source_commit = source_commit or self.source_commit
        proposal_raw = (self._encode(self._proposal(source_commit))
                        if proposal_raw is None else proposal_raw)
        envelope_blob = self._blob(proposal_raw)
        pin = envelope_blob if writer_pin is None else writer_pin
        writer_raw = self.writer_raw if writer_raw is None else writer_raw
        activated_writer = writer_raw.replace(
            ANCHOR, f'APPROVED_EXECUTION_ENVELOPE_BLOB = "{pin}"\n'.encode())
        entries = dict(self.source_entries if source_entries is None
                       else source_entries)
        entries[WRITER_PATH] = ("100644", "blob", self._blob(activated_writer))
        entries[ENVELOPE_PATH] = ("100644", "blob", envelope_blob)
        for path, entry in (changes or {}).items():
            if entry is None:
                entries.pop(path, None)
            else:
                entries[path] = entry
        commit = self._commit(entries, (source_commit,) if parents is None else parents)
        return commit, proposal_raw, envelope_blob, entries

    def _audit(self, **changes):
        arguments = {
            "repo": self.repo, "source_commit": self.source_commit,
            "runner_commit": self.runner_commit, "source_ref": self.source_ref,
            "runner_ref": self.runner_ref,
        }
        arguments.update(changes)
        return publication.audit_publication(**arguments)

    def _reject_runner(self, runner_commit):
        self._git("update-ref", self.runner_ref, runner_commit)
        with self.assertRaises(publication.Rejected):
            self._audit(runner_commit=runner_commit)

    def _refs(self):
        return self._git("for-each-ref", "--format=%(refname) %(objectname)")


    def _assert_verified_closed_report(self, report):
        self.assertEqual(report["result"],
                         "ProposalPublicationStructureVerified_NoExecutionAuthority")
        self.assertEqual(report["sourceCommit"], self.source_commit)
        self.assertEqual(report["runnerCommit"], self.runner_commit)
        self.assertEqual(report["sourceRef"], self.source_ref)
        self.assertEqual(report["runnerRef"], self.runner_ref)
        self.assertEqual(report["observedLocalRefs"], {
            self.source_ref: self.source_commit, self.runner_ref: self.runner_commit})
        self.assertEqual(report["sourceWriterGitBlob"], REVIEWED_WRITER_BLOB)
        self.assertEqual(report["proposalEnvelopeGitBlob"], self.envelope_blob)
        self.assertEqual(report["runnerWriterGitBlob"], self.runner_entries[WRITER_PATH][2])
        self.assertEqual(report["changedPaths"], sorted((WRITER_PATH, ENVELOPE_PATH)))
        for field in ("liveRemoteRefsVerified", "currentPhysicalInputsVerified",
                      "executionAuthorityVerified", "outputCreated",
                      "UnityOrPlayerExecuted", "R03Accepted", "H2Passed",
                      "ReadyForHumanReviewGate"):
            self.assertIs(report[field], False, field)
        self.assertEqual(report["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")
        self.assertEqual(report["D5BLocalExecution"], "NotAuthorized")
        self.assertEqual(report["D5LocalValidation"], "NotAuthorized")
        self.assertEqual(report["realUnityBuild"], "NotRun")
        self.assertEqual(report["realPlayerCellsPassed"], 0)
        self.assertEqual(report["realPlayerCellsNoCoverage"], 18)

    def test_01_separate_refs_construct_real_closed_publication_chain(self):
        self.assertEqual(publication.R5_WRITER_BLOB, REVIEWED_WRITER_BLOB)
        self.assertEqual(publication.ENVELOPE_PATH, ENVELOPE_PATH)
        self.assertNotEqual(self.source_commit, self.runner_commit)
        self.assertEqual(self._git("rev-parse", self.source_ref).decode().strip(),
                         self.source_commit)
        self.assertEqual(self._git("rev-parse", self.runner_ref).decode().strip(),
                         self.runner_commit)
        self.assertEqual(
            self._git("rev-list", "--parents", "-n", "1", self.runner_commit)
            .decode().split(), [self.runner_commit, self.source_commit])
        self.assertEqual(self._git("cat-file", "blob",
                                   self.source_commit + ":" + WRITER_PATH),
                         self.writer_raw)
        self.assertEqual(self._git("cat-file", "blob",
                                   self.runner_commit + ":" + ENVELOPE_PATH),
                         self.proposal_raw)
        self.assertEqual(json.loads(self.proposal_raw)["sourcePins"],
                         {"hybridclr_demo": self.source_commit, **gate.source.PINS})
        writer = self._git("cat-file", "blob", self.runner_commit + ":" + WRITER_PATH)
        self.assertEqual(writer, self.writer_raw.replace(
            ANCHOR, ('APPROVED_EXECUTION_ENVELOPE_BLOB = "' +
                     self.envelope_blob + '"\n').encode()))
        before = self._refs()
        self._assert_verified_closed_report(self._audit())
        self.assertEqual(self._refs(), before)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)

    def test_02_same_ref_publication_leaves_old_source_pin_stale(self):
        self._git("update-ref", self.source_ref, self.runner_commit)
        observed = self._git("ls-remote", str(self.repo), self.source_ref).decode()
        self.assertEqual(observed.split(), [self.runner_commit, self.source_ref])
        self.assertEqual(json.loads(self.proposal_raw)["sourcePins"]["hybridclr_demo"],
                         self.source_commit)
        with self.assertRaises(gate.Rejected):
            gate.exact_remote_head(observed, self.source_commit)
        with self.assertRaises(publication.Rejected):
            self._audit()
        with self.assertRaises(publication.Rejected):
            self._audit(runner_ref=self.source_ref)

    def test_03_moved_or_missing_source_and_runner_refs_are_rejected(self):
        for role, ref, expected, replacement in (
            ("source", self.source_ref, self.source_commit, self.runner_commit),
            ("runner", self.runner_ref, self.runner_commit, self.source_commit),
        ):
            for state in ("moved", "missing"):
                with self.subTest(role=role, state=state):
                    try:
                        if state == "missing":
                            self._git("update-ref", "-d", ref)
                        else:
                            self._git("update-ref", ref, replacement)
                        with self.assertRaises(publication.Rejected):
                            self._audit()
                    finally:
                        self._git("update-ref", ref, expected)
        alias = "refs/heads/ap1-source-alias"
        self._git("update-ref", alias, self.source_commit)
        for canonical_target in (self.source_commit, self.runner_commit):
            with self.subTest(source_alias=True, canonical_target=canonical_target):
                try:
                    self._git("update-ref", self.source_ref, canonical_target)
                    self.assertEqual(self._git("rev-parse", alias).decode().strip(),
                                     self.source_commit)
                    with self.assertRaises(publication.Rejected):
                        self._audit(source_ref=alias)
                finally:
                    self._git("update-ref", self.source_ref, self.source_commit)
        with self.subTest(symbolic_canonical_source=True):
            try:
                self._git("symbolic-ref", self.source_ref, alias)
                self.assertEqual(self._git("rev-parse", self.source_ref)
                                 .decode().strip(), self.source_commit)
                with self.assertRaises(publication.Rejected):
                    self._audit()
            finally:
                self._git("update-ref", "--no-deref", self.source_ref,
                          self.source_commit)

    def test_04_missing_or_noncommit_objects_are_rejected(self):
        blob = self._blob(b"An actual blob is not a commit.\n")
        tree = self._tree(self.source_entries)
        tag = self._git("mktag", data=(
            f"object {self.source_commit}\ntype commit\ntag ap1-fixture\n"
            "tagger AP1 Fixture <ap1-fixture@example.invalid> 1795651200 +0000\n"
            "\nAn annotated tag is not an exact commit object.\n"
        ).encode()).decode().strip()
        reader = publication._Git(self.repo)
        for kind, oid in (("missing", "f" * 40), ("blob", blob),
                          ("tree", tree), ("tag", tag)):
            with self.subTest(guard="commit-object", kind=kind):
                if kind != "missing":
                    self.assertEqual(self._git("cat-file", "-t", oid)
                                     .decode().strip(), kind)
                with self.assertRaises(publication.Rejected):
                    reader.commit(oid)
            for role in ("source_commit", "runner_commit"):
                with self.subTest(role=role, kind=kind):
                    with self.assertRaises(publication.Rejected):
                        self._audit(**{role: oid})


    def test_05_runner_pin_must_equal_exact_proposal_blob(self):
        wrong_blob = self._blob(self.proposal_raw + b"\n")
        self.assertNotEqual(wrong_blob, self.envelope_blob)
        runner, raw, actual_blob, _ = self._runner(writer_pin=wrong_blob)
        self.assertEqual(raw, self.proposal_raw)
        self.assertEqual(actual_blob, self.envelope_blob)
        self._reject_runner(runner)

    def test_06_runner_rejects_extra_source_helper_or_plan_changes(self):
        for path in (SOURCE_PATH, WRAPPER_PATH, PREFLIGHT_PATH, PLAN_PATH):
            with self.subTest(path=path):
                changed = ("100644", "blob",
                           self._blob(self.fixture_bytes[path] + b"\n"))
                runner, _, _, _ = self._runner(changes={path: changed})
                self._reject_runner(runner)
        for name, changes in (
            ("added-file", {"Docs/unreviewed-extra.txt":
                            ("100644", "blob", self._blob(b"unexpected\n"))}),
            ("removed-source", {SOURCE_PATH: None}),
        ):
            with self.subTest(change=name):
                runner, _, _, _ = self._runner(changes=changes)
                self._reject_runner(runner)

    def test_07_source_writer_must_be_exact_reviewed_closed_blob(self):
        changed = self.writer_raw + b"\n# Unreviewed source mutation.\n"
        entries = dict(self.source_entries)
        entries[WRITER_PATH] = ("100644", "blob", self._blob(changed))
        source = self._commit(entries)
        runner, _, _, _ = self._runner(
            source_commit=source, source_entries=entries, writer_raw=changed)
        self._git("update-ref", self.source_ref, source)
        self._git("update-ref", self.runner_ref, runner)
        with self.assertRaises(publication.Rejected):
            self._audit(source_commit=source, runner_commit=runner)

    def test_08_runner_writer_allows_only_one_exact_pin_substitution(self):
        expected = self._git("cat-file", "blob", self.runner_entries[WRITER_PATH][2])
        for name, wrong_writer in (
            ("unchanged-closed-writer", self.writer_raw),
            ("extra-comment", expected + b"\n# Unreviewed runner mutation.\n"),
            ("second-constant", expected + ANCHOR),
        ):
            with self.subTest(change=name):
                runner, _, _, _ = self._runner(changes={
                    WRITER_PATH: ("100644", "blob", self._blob(wrong_writer))})
                self._reject_runner(runner)

    def test_09_writer_and_proposal_mode_type_substitutions_are_rejected(self):
        empty_tree = self._tree({})
        for path in (WRITER_PATH, ENVELOPE_PATH):
            normal_blob = self.runner_entries[path][2]
            for label, entry in (
                ("changed-mode", ("100755", "blob", normal_blob)),
                ("symlink", ("120000", "blob", normal_blob)),
                ("directory", ("040000", "tree", empty_tree)),
                ("gitlink", ("160000", "commit", self.source_commit)),
            ):
                with self.subTest(role="runner", path=path, substitution=label):
                    runner, _, _, _ = self._runner(changes={path: entry})
                    self._reject_runner(runner)
        for label, entry in (
            ("symlink", ("120000", "blob", REVIEWED_WRITER_BLOB)),
            ("directory", ("040000", "tree", empty_tree)),
            ("gitlink", ("160000", "commit", self.source_commit)),
        ):
            with self.subTest(role="source", substitution=label):
                entries = {**self.source_entries, WRITER_PATH: entry}
                source = self._commit(entries)
                runner, _, _, _ = self._runner(
                    source_commit=source, source_entries=entries)
                self._git("update-ref", self.source_ref, source)
                self._git("update-ref", self.runner_ref, runner)
                with self.assertRaises(publication.Rejected):
                    self._audit(source_commit=source, runner_commit=runner)

    def test_10_proposal_must_be_new_and_present_in_runner(self):
        runner, _, _, _ = self._runner(changes={ENVELOPE_PATH: None})
        self._reject_runner(runner)
        entries = {**self.source_entries, ENVELOPE_PATH:
                   ("100644", "blob", self._blob(b"{}\n"))}
        source = self._commit(entries)
        runner, _, _, _ = self._runner(source_commit=source, source_entries=entries)
        self._git("update-ref", self.source_ref, source)
        self._git("update-ref", self.runner_ref, runner)
        with self.assertRaises(publication.Rejected):
            self._audit(source_commit=source, runner_commit=runner)


    def test_11_duplicate_json_keys_are_rejected_at_every_level(self):
        for label, marker in (
            ("top-level", '"schemaVersion": 1'),
            ("source-pins", '"hybridclr_demo": "' + self.source_commit + '"'),
            ("authorization", '"R03Accepted": false'),
        ):
            with self.subTest(level=label):
                original = marker.encode()
                self.assertEqual(self.proposal_raw.count(original), 1)
                raw = self.proposal_raw.replace(
                    original, original + b", " + original, 1)
                # Equal duplicate values still create an ambiguous input.
                self.assertEqual(json.loads(raw), json.loads(self.proposal_raw))
                runner, _, _, _ = self._runner(proposal_raw=raw)
                self._reject_runner(runner)

    def test_12_proposal_schema_and_field_types_are_exact(self):
        for label, raw in (
            ("truncated-json", b'{"schemaVersion":'),
            ("invalid-utf8", b'{"kind":"\xff"}'),
            ("nan", b'{"schemaVersion":NaN}'),
            ("infinity", b'{"schemaVersion":Infinity}'),
            ("negative-infinity", b'{"schemaVersion":-Infinity}'),
            ("excessive-nesting", b"[" * 1100 + b"0" + b"]" * 1100),
            ("oversized-integer", b"9" * 5000),
        ):
            with self.subTest(raw_input=label):
                with self.assertRaises(publication.Rejected):
                    publication.strict_json_object(raw)
                runner, _, _, _ = self._runner(proposal_raw=raw)
                self._reject_runner(runner)
        variants = [
            ("array-root", []), ("null-root", None), ("string-root", "proposal"),
        ]
        for path, value in (
            (("schemaVersion",), True),
            (("schemaVersion",), 1.0),
            (("schemaVersion",), "1"),
            (("kind",), "R03D5BApprovedDryAdmissionEnvelopeV1"),
            (("branch",), "main"),
            (("scope",), "BuildAndRunUnityPlayer"),
            (("sourcePins",), []),
            (("authorization",), []),
            (("authorization", "R03Accepted"), 0),
            (("authorization", "allowNativeBuild"), 0),
            (("authorization", "approvedEnvelopeGitBlob"), False),
        ):
            value_object = self._proposal()
            target = value_object
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            variants.append((".".join(path) + "=" + repr(value), value_object))
        missing = self._proposal()
        missing.pop("scope")
        variants.append(("missing-scope", missing))
        extra = self._proposal()
        extra["userLocalExecutionApproval"] = "ExplicitlyApproved"
        variants.append(("extra-execution-approval", extra))
        for label, value in variants:
            with self.subTest(change=label):
                runner, _, _, _ = self._runner(proposal_raw=self._encode(value))
                self._reject_runner(runner)


    def test_13_proposal_requires_exact_source_and_other_repository_pins(self):
        variants = []
        for role in ("hybridclr_demo", *gate.source.PINS):
            proposal = self._proposal()
            proposal["sourcePins"][role] = "f" * 40
            variants.append(("wrong-" + role, proposal))
        for label, action in (
            ("missing-role", lambda pins: pins.pop("hybridclr")),
            ("extra-role", lambda pins: pins.__setitem__("extra", "e" * 40)),
            ("non-string-demo", lambda pins: pins.__setitem__("hybridclr_demo", 1)),
        ):
            proposal = self._proposal()
            action(proposal["sourcePins"])
            variants.append((label, proposal))
        for label, proposal in variants:
            with self.subTest(change=label):
                runner, _, _, _ = self._runner(proposal_raw=self._encode(proposal))
                self._reject_runner(runner)

    def test_14_authority_promotions_are_rejected(self):
        promotions = {
            "approvedEnvelopeGitBlob": self.envelope_blob,
            "independentlyReviewedExecutableAdmission":
                "PassedForD5BLocalDryAdmissionOnly",
            "explicitUserLocalApproval": "ExplicitlyApproved",
            "WEB_TO_LOCAL": "OPEN_FOR_EXACT_D5B_DRY_ADMISSION_ONLY",
            "D5BLocalExecution": "Authorized",
            "D5LocalValidation": "Authorized",
            "R03Accepted": True,
            "H2Passed": True,
            "ReadyForHumanReviewGate": True,
            "allowNativeBuild": True,
            "allowPlayerLaunch": True,
        }
        self.assertEqual(set(promotions), set(self.closed_authority))
        for field, value in promotions.items():
            with self.subTest(field=field):
                proposal = self._proposal()
                proposal["authorization"][field] = value
                runner, _, _, _ = self._runner(proposal_raw=self._encode(proposal))
                self._reject_runner(runner)

    def test_15_runner_has_exactly_one_parent_equal_to_source(self):
        other = self._commit(self.source_entries)
        intermediate = self._commit(self.source_entries, (self.source_commit,))
        for label, parents in (
            ("root-commit", ()),
            ("wrong-parent", (other,)),
            ("two-parents", (self.source_commit, other)),
            ("indirect-parent", (intermediate,)),
        ):
            with self.subTest(shape=label):
                runner, _, _, _ = self._runner(parents=parents)
                self._reject_runner(runner)

    def test_16_proposal_cannot_become_production_execution_envelope(self):
        self.assertEqual(gate.git_blob(self.proposal_raw), self.envelope_blob)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        with self.assertRaises(gate.Rejected):
            gate.approved_envelope(self.proposal_raw)
        # This sole approval mock shows that matching immutable bytes do
        # not make the closed proposal kind executable. Git is never mocked.
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               self.envelope_blob):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(self.proposal_raw)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)


    def _cli(self, *extra):
        return subprocess.run([
            sys.executable, "-B", str(Path(publication.__file__).resolve()),
            "--repo", str(self.repo),
            "--source-commit", self.source_commit,
            "--runner-commit", self.runner_commit,
            "--source-ref", self.source_ref,
            "--runner-ref", self.runner_ref, *extra,
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.git_environment, check=False)

    def test_17_cli_audits_objects_without_changing_refs_or_authority(self):
        before = self._refs()
        result = self._cli()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self._assert_verified_closed_report(json.loads(result.stdout))
        self.assertEqual(self._refs(), before)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)

    def test_18_cli_exposes_no_execution_or_authority_override(self):
        before = self._refs()
        for arguments in (
            ("--execute",),
            ("--mode", "execute"),
            ("--approved-envelope-git-blob", self.envelope_blob),
            ("--authorize", "ExplicitlyApproved"),
        ):
            with self.subTest(arguments=arguments):
                result = self._cli(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn("unrecognized arguments", result.stderr.decode())
                self.assertEqual(result.stdout, b"")
                self.assertEqual(self._refs(), before)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)


if __name__ == "__main__":
    unittest.main()
