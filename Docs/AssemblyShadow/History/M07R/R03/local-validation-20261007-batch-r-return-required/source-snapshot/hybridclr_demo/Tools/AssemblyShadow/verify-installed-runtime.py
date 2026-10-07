#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from shadow_tools import VerificationError, main
from h1_m07_workflow_authority import BASELINE_BOUND, authenticate_originals, verify as verify_m07_workflow

ENV_ROOT = "H1_M07_WORKFLOW_AUTHORITY_ROOT"
ENV_BASELINE = "H1_M07_WORKFLOW_BASELINE_ID"


def _argument_value(argv, name, default=None):
    for index, value in enumerate(argv):
        if value == name:
            if index + 1 >= len(argv):
                raise VerificationError(f"Missing value for {name}")
            return argv[index + 1]
        prefix = name + "="
        if value.startswith(prefix):
            return value[len(prefix):]
    return default


def _without_demo_source_flags(argv):
    return [value for value in argv if value not in ("--skip-demo-source", "--verify-demo-source")]


def _run_m07_context(argv):
    root_text = os.environ.get(ENV_ROOT)
    baseline_id = os.environ.get(ENV_BASELINE)
    if bool(root_text) != bool(baseline_id):
        raise VerificationError("Incomplete M07 workflow authority environment")
    if not root_text:
        return None
    if "--skip-demo-source" in argv:
        raise VerificationError("M07 workflow authority cannot be invoked with --skip-demo-source")

    project_text = _argument_value(argv, "--project")
    project = Path(project_text) if project_text else Path(__file__).resolve().parents[2]
    recovery_root = Path(root_text)
    context = authenticate_originals(project, recovery_root)
    required = {row["path"]: row for row in context["mutablePaths"] if row["path"] in BASELINE_BOUND}
    required_changed = [path for path, row in required.items() if row["changed"]]

    # Before ValidateCompilerInputs mutates anything, retain the exact generic
    # verifier. Once either required workflow-owned file changes, fail closed
    # into the split authority path; verify_m07_workflow then requires both
    # required files to be changed and bound to the requested baseline.
    if not required_changed:
        return main(["verify", *argv])

    runtime_argv = _without_demo_source_flags(argv)
    runtime_status = main(["verify", *runtime_argv, "--skip-demo-source"])
    if runtime_status != 0:
        return runtime_status
    result = verify_m07_workflow(project, recovery_root, baseline_id)
    print(json.dumps(result, indent=2 if "--json" in argv else None, sort_keys="--json" in argv))
    return 0


def entry(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        contextual = _run_m07_context(argv)
        return contextual if contextual is not None else main(["verify", *argv])
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(entry())
