#!/usr/bin/env python3
"""Separate current reusable contracts from six fixed-H1 positive fixtures.

No production verifier is modified and no historical evidence is promoted.
The positive tests require the exact accepted H1 repository fixture; current
R02 instead must be rejected by those H1-only admission contracts.
"""
from __future__ import annotations
import argparse
from collections import Counter
import contextlib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

H1_CHECKPOINT = "2cbf68658a5b73189930fcdfe250835b72639515"
H1_BRANCH = "codex/assembly-shadow-r01b-h1"
PINNED_POSITIVES = frozenset(
    "test_h1_graph_reuse.H1GraphReuseTests." + name for name in (
        "test_historical_bridge_authenticates_original_git_source",
        "test_historical_reanalysis_delta_is_exact_analysis_only_successor",
        "test_real_69130_graph_to_current_tool_only_successor_matches_exact_policy",
        "test_real_transition_on_pilot_nested_early_prepare_preserves_authenticated_authority",
        "test_split_checkout_process_regression_uses_designated_analysis_authority",
    )) | {"test_h1_handoff_preflight.LiveCommittedHandoffTests.test_actual_committed_candidate_handoff_passes_preflight"}
# Direct transitive policy/test inputs used by the six historical positives.
# Drift requires a new fixture review, never automatic reuse of old code.
FIXTURE_EQUIVALENCE = (
    "h1_bee_primary_tests.py", "h1_graph_reuse.py", "h1_historical_reanalysis.py",
    "h1_handoff_preflight.py", "h1_paired_performance.py", "shadow_tools.py",
    "r00_player_inputs.py", "r00_results.py", "r01_early_results.py",
    "analyze-h1-paired-performance.py", "tests/test_h1_graph_reuse.py",
    "tests/test_h1_handoff_preflight.py",
)


def leaves(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from leaves(item)
        else:
            yield item


def select(suite, scope):
    if scope not in ("current", "historical"):
        raise ValueError("Unknown regression scope")
    items = list(leaves(suite))
    ids = [item.id() for item in items]
    if len(ids) != 387 or len(set(ids)) != len(ids) or not PINNED_POSITIVES <= set(ids):
        raise ValueError("H1 regression inventory changed; explicit scope review required")
    return unittest.TestSuite(item for item in items if (item.id() in PINNED_POSITIVES) == (scope == "historical"))


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE, timeout=90).strip()


def fixture_bindings(project, current):
    if git(project, "rev-parse", "HEAD") != H1_CHECKPOINT or git(project, "branch", "--show-current") != H1_BRANCH:
        raise ValueError("Historical positive fixture must use the fixed H1 checkpoint and branch")
    rows = []
    for relative in FIXTURE_EQUIVALENCE:
        name = "Tools/AssemblyShadow/" + relative
        old = (project / name).read_bytes()
        now = (current / name).read_bytes()
        old_git = subprocess.check_output(["git", "-C", str(project), "show", H1_CHECKPOINT + ":" + name])
        new_git = subprocess.check_output(["git", "-C", str(current), "show", "HEAD:" + name])
        if not old == now == old_git == new_git:
            raise ValueError("Historical/current fixture tool differs: " + name)
        rows.append({"path": name, "sha256": hashlib.sha256(old).hexdigest()})
    return rows


def negative_suite(project):
    import h1_graph_reuse as reuse
    import h1_historical_reanalysis as historical
    import h1_handoff_preflight as handoff
    import shadow_tools

    class R02RejectionTests(unittest.TestCase):
        def test_r02_is_not_h1_analysis_only_successor(self):
            with self.assertRaisesRegex(shadow_tools.VerificationError, "Historical analysis successor delta differs"):
                historical.authenticate_analysis_delta(project, git(project, "rev-parse", "HEAD"))

        def test_r02_is_not_h1_retained_graph_successor(self):
            current = shadow_tools.read_json(project / shadow_tools.PINS)
            with self.assertRaisesRegex(shadow_tools.VerificationError, "Graph reuse non-metadata delta differs"):
                reuse.authenticate_transition(project, reuse.retained_graph_pins(current), current)

        def test_r02_handoff_is_not_accepted_by_h1_schema(self):
            with self.assertRaisesRegex(shadow_tools.VerificationError, "Incomplete handoff sections"):
                handoff.verify(project, "candidate")

    return unittest.defaultTestLoader.loadTestsFromTestCase(R02RejectionTests)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--current-root", required=True, type=Path)
    parser.add_argument("--scope", required=True, choices=("current", "historical"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    project = args.project.resolve(strict=True); current = args.current_root.resolve(strict=True)
    if args.output.exists() or not args.output.is_absolute() or args.output != args.output.resolve():
        raise ValueError("Unused canonical output required")
    if args.scope == "current" and project != current:
        raise ValueError("Current contracts must run from current checkout")
    authenticated = fixture_bindings(project, current) if args.scope == "historical" else []
    sys.path[:0] = [str(project / "Tools/AssemblyShadow"), str(project / "Tools/AssemblyShadow/tests")]
    import h1_bee_primary_tests as original
    suite = select(unittest.defaultTestLoader.loadTestsFromNames(original.MODULES), args.scope)
    if args.scope == "current":
        targets = json.loads((project / "Docs/AssemblyShadow/History/M07R/R02/source-targets.json").read_text())
        if targets.get("kind") != "R02SourceTargets":
            raise ValueError("Current successor tests require the R02 source contract")
        suite.addTests(negative_suite(project))
    args.output.mkdir(parents=True)
    rows = []

    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test); rows.append({"id": test.id(), "result": "Passed"})
        def addFailure(self, test, error):
            super().addFailure(test, error); rows.append({"id": test.id(), "result": "Failed", "detail": self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error); rows.append({"id": test.id(), "result": "Error", "detail": self._exc_info_to_string(error, test)})
        def addSkip(self, test, reason):
            super().addSkip(test, reason); rows.append({"id": test.id(), "result": "Skipped", "reason": reason})

    log = args.output / "tests.log"
    with log.open("x") as stream, contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    expected = 384 if args.scope == "current" else 6
    passed = result.wasSuccessful() and not result.skipped and result.testsRun == expected and len(rows) == expected
    report = {"kind": "R02ScopedLegacyRegression", "result": "Passed" if passed else "Failed",
              "scope": args.scope, "executionCheckout": git(project, "rev-parse", "HEAD"),
              "currentCheckout": git(current, "rev-parse", "HEAD"), "testCount": result.testsRun,
              "counts": dict(Counter(row["result"] for row in rows)), "tests": rows,
              "fixedPositiveIds": sorted(PINNED_POSITIVES), "fixtureBindings": authenticated,
              "rawLogSha256": hashlib.sha256(log.read_bytes()).hexdigest(),
              "classification": "CurrentContractsAndH1Rejections" if args.scope == "current" else "FixedH1PositiveFixtureExecution",
              "runtimeAcceptance": False, "historicalPlayerExecutionReused": False}
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("kind", "result", "scope", "testCount", "counts")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
