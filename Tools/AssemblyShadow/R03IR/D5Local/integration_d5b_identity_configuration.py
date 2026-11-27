#!/usr/bin/env python3
"""Required CI-only AP6 composition check using the three fixed AP1 sources.

AP6_PINNED_SIBLINGS must name a directory containing existing full-object-store
checkouts hybridclr, hybridclr_unity and il2cpp_plus at their accepted AP1 pins.
The fixture will clone these actual sources and route only AP5's private remote
transport to file remotes. Missing inputs fail; this test never skips.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve(strict=True).parent
sys.path.insert(0, str(HERE))
import test_d5b_identity_configuration as unit


class D5BIdentityConfigurationPinnedSources(unit._AP6Fixture):
    def _fixture_git(self, root, *arguments):
        completed = subprocess.run(
            [self.system_git, "-c", "protocol.allow=never", "-c", "protocol.file.allow=always",
             "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
             "-C", str(root), *arguments],
            capture_output=True, env=self.file_environment, timeout=300, check=True)
        return completed.stdout

    def _clone_checkout(self, source, target, commit, ref, repository):
        self._fixture_git(self.parent, "clone", "--quiet", "--no-hardlinks", "--no-checkout",
                          "--", str(source), str(target))
        self._fixture_git(target, "remote", "set-url", "origin",
                          "https://github.com/" + repository + ".git")
        self._fixture_git(target, "checkout", "--quiet", "--force", "-B",
                          ref.removeprefix("refs/heads/"), commit)
        self.assertTrue((target / ".git").is_dir())
        self.assertFalse((target / ".git/objects/info/alternates").exists())
        self.assertEqual(self._fixture_git(target, "rev-parse", "HEAD").decode().strip(), commit)
        self.assertEqual(self._fixture_git(target, "symbolic-ref", "HEAD").decode().strip(), ref)

    def _compose_pinned_sources(self, sources):
        self.system_git = shutil.which("git", path=os.defpath)
        self.assertIsNotNone(self.system_git)
        self.file_environment = dict(self.git_environment, **{
            "PATH": os.defpath, "LANG": "C", "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_COUNT": "0",
            "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
            "GIT_ALLOW_PROTOCOL": "file", "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1", "GIT_ATTR_NOSYSTEM": "1",
        })
        for role, pin in unit.AP1.SOURCE_PINS.items():
            source = sources / role
            self.assertEqual(self._fixture_git(source, "rev-parse", "HEAD").decode().strip(), pin,
                             role + " must be checked out at its exact accepted AP1 pin")
            self.assertEqual(self._fixture_git(source, "rev-parse", "--is-shallow-repository"),
                             b"false\n", role + " requires its full object store")
            self._clone_checkout(source, self.workspace / role, pin, self.source_ref,
                                 "night-outlook/" + role)
        self._clone_checkout(self.repo, self.workspace / "hybridclr_demo", self.source_commit,
                             self.source_ref, "night-outlook/hybridclr_demo")

        bare_parent = self.parent / "file-remotes"
        bare_parent.mkdir()
        remotes = {}
        for role in ("hybridclr_demo", *unit.AP1.SOURCE_PINS):
            remote = bare_parent / (role + ".git")
            self._fixture_git(self.parent, "init", "--quiet", "--bare", "--object-format=sha1",
                              str(remote))
            self._fixture_git(self.workspace / role, "push", "--quiet", str(remote), self.source_ref)
            remotes[role] = remote
        self._fixture_git(self.repo, "push", "--quiet", str(remotes["hybridclr_demo"]), self.runner_ref)
        for role, remote in remotes.items():
            expected_refs = [self.source_ref]
            if role == "hybridclr_demo":
                expected_refs.append(self.runner_ref)
            actual_refs = self._fixture_git(remote, "for-each-ref", "--format=%(refname)")
            self.assertEqual(sorted(actual_refs.decode().splitlines()), sorted(expected_refs))

        real_loader = unit.observer._load_helper
        remote_calls = []

        @contextmanager
        def routed_loader(role, progress):
            with real_loader(role, progress) as helper:
                if role != "identity":
                    yield helper
                    return
                real_run_remote = helper._run_remote

                def route(command, environment):
                    self.assertEqual(command[0], self.system_git)
                    self.assertEqual(command[-5:-2], ["ls-remote", "--exit-code", "--refs"])
                    endpoint, ref = command[-2:]
                    endpoints = {"https://github.com/night-outlook/" + name + ".git": name
                                 for name in remotes}
                    self.assertIn(endpoint, endpoints)
                    remote_role = endpoints[endpoint]
                    allowed_refs = ((self.source_ref, self.runner_ref) if remote_role == "hybridclr_demo"
                                    else (self.source_ref,))
                    self.assertIn(ref, allowed_refs)
                    self.assertEqual(environment["GIT_ALLOW_PROTOCOL"], "https")
                    self.assertIn("--git-dir=" + os.devnull, command)
                    remote_calls.append((remote_role, ref))
                    routed = list(command)
                    routed[-2] = remotes[remote_role].as_uri()
                    routed[routed.index("protocol.https.allow=always")] = "protocol.https.allow=never"
                    position = routed.index("ls-remote")
                    routed[position:position] = ["-c", "protocol.file.allow=always"]
                    return real_run_remote(routed, dict(environment, GIT_ALLOW_PROTOCOL="file"))

                # This private transport route is the sole behavioral adaptation.
                # The AP5 public API, pin policy, checkout scanner and AP4 consumers
                # execute unchanged on real commits, files and ls-remote responses.
                with mock.patch.object(helper, "_run_remote", side_effect=route):
                    yield helper

        with mock.patch.object(unit.observer, "_load_helper", side_effect=routed_loader):
            result = self._observe()
        report = result.report
        self.assertEqual(report["result"], unit.observer.SUCCESS_RESULT)
        self.assertEqual(report["stageCallsAttempted"], ["identity", "configuration"])
        self.assertEqual(report["stageCallsReturned"], ["identity", "configuration"])
        self.assertEqual(report["stageCallsCompleted"], ["identity", "configuration"])
        self.assertIs(report["proposalFieldsMatched"], True)
        self.assertIs(report["fixedAP1SiblingPinsMatched"], True)
        self.assertIs(report["sharedObservationsMatched"], True)
        self.assertEqual(report["matchedProposalProjection"],
                         {field: self.identity[field] for field in unit.SHARED_FIELDS})
        self.assertEqual(report["comparisonCallsAttempted"], ["runner", "locations"])
        self.assertEqual(report["comparisonCallsCompleted"], ["runner", "locations"])
        self._closed(report)
        identity = report["observations"]["identity"]
        configuration = report["observations"]["configuration"]
        self._closed(identity)
        self._closed(configuration)
        self.assertIs(identity["sourcePinsMatchAcceptedAP1SiblingPins"], True)
        self.assertIs(identity["fixedFiveIdentityObservationVerified"], True)
        self.assertEqual(identity["localPassesCompleted"], ["before", "after"])
        self.assertEqual(identity["remotePassesCompleted"], ["before", "after"])
        expected_calls = [(role, self.source_ref)
                          for role in ("hybridclr_demo", *unit.AP1.SOURCE_PINS)]
        expected_calls.append(("hybridclr_demo", self.runner_ref))
        self.assertEqual(remote_calls, expected_calls * 2)
        self.assertEqual(configuration["configurationConsumerCallsCompleted"], [
            "d5b_local_admission.read_plan", "d5b_rr5_source_preflight.checked_profile",
        ])
        artifact = configuration["importObservation"]["artifactObservation"]
        self.assertEqual({key: identity["checkoutObservations"]["after"]["runner"][key]
                          for key in unit.CHECKOUT_FIELDS}, artifact["observedCheckout"])
        self.assertEqual(identity["locationObservations"]["after"], artifact["observedLocations"])
        self.assertEqual(list(self.evidence.iterdir()), [])
        for role, path in self.history.items():
            if role != "b1EvidenceBase":
                self.assertEqual(list(path.iterdir()), [])
        roles = ("hybridclr_demo", *unit.AP1.SOURCE_PINS, "runner")
        receipt = {
            "schemaVersion": 1, "kind": "R03AP6PinnedSourceIntegrationReceiptV1",
            "result": report["result"],
            "actualAP1SiblingPins": {
                role: identity["checkoutObservations"]["after"][role]["head"]
                for role in unit.AP1.SOURCE_PINS
            },
            "fixtureDemoH": self.source_commit, "fixtureRunnerA": self.runner_commit,
            "fileRefCalls": [
                {"pass": label, "role": role,
                 **{field: identity["remoteObservations"][label][role][field]
                    for field in ("repository", "ref", "head")},
                 "actualTransport": "file"}
                for label in ("before", "after") for role in roles
            ],
            "completedRealAP4Consumers": configuration["configurationConsumerCallsCompleted"],
            "stageCallsCompleted": report["stageCallsCompleted"],
            "proposalFieldsMatched": report["proposalFieldsMatched"],
            "fixedAP1SiblingPinsMatched": report["fixedAP1SiblingPinsMatched"],
            "sharedObservationsMatched": report["sharedObservationsMatched"],
            "observationDoublesUsed": False,
            "realAP5PublicAPIUsed": True, "realAP4PublicAPIUsed": True,
            "privateAP5FileTransportOnly": True, "productionHttpsExercised": False,
            "systemGit": {"path": self.system_git,
                          "version": self._fixture_git(self.parent, "--version").decode().strip()},
            "closedAuthority": {
                **{field: report[field] for field in unit.AP1.CLOSED_AUTHORITY},
                "executionAuthorityVerified": report["executionAuthorityVerified"],
            },
        }
        print("\n" + json.dumps(receipt, sort_keys=True, allow_nan=False),
              flush=True)

    def test_real_pinned_sources_and_unchanged_helpers_compose(self):
        supplied = os.environ.get("AP6_PINNED_SIBLINGS")
        self.assertTrue(supplied, "AP6_PINNED_SIBLINGS is required; CI integration may not skip")
        sources = Path(supplied).resolve(strict=True)
        for role in unit.AP1.SOURCE_PINS:
            self.assertTrue((sources / role / ".git").is_dir(), role + " must be an ordinary checkout")
        self._compose_pinned_sources(sources)


if __name__ == "__main__":
    unittest.main()
