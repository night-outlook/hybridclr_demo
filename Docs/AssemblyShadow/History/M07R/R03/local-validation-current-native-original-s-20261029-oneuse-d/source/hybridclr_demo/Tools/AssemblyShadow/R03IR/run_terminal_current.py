#!/usr/bin/env python3
"""Parallel IR-R03-02 current-native candidate runner; NO active Local authority.

Do NOT invoke until a separate source-bound WEB_TO_LOCAL grants one fresh run.
Legacy R03/source-pins.json, original S, b7e3, c42a, f51d remain immutable.
The actual Player/SDK commands are owned by the existing pinned R03IR runner.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

# This file is launched in a NEW interpreter by the one-use coordinator.
# The coordinator's in-memory sys.path cannot cross a process boundary.
# Resolve the adjacent, owning R03 infrastructure BEFORE its first import.
HERE = Path(__file__).resolve().parent
R03 = HERE.parent / "R03"
sys.path.insert(0, str(R03))

from run_local import Batch as OriginalBatch, require
from run_terminal_local import execute as run_existing_focused_batch
from current_native_source_gate import (
    BRANCH, CONFIG, CURRENT, OLD_NATIVE, candidate_pins, verify_source_roots,
)


class CurrentNativeBatch(OriginalBatch):
    def __init__(self, workspace, output, unity, demo_commit):
        source_workspace = Path(workspace).resolve()
        # Source validation occurs BEFORE the base collector creates its output.
        # No config/JSON controls are allowed to skip these ten actual file digests.
        report = verify_source_roots({
            "hybridclr_demo": source_workspace / "hybridclr_demo",
            "hybridclr": source_workspace / "hybridclr",
            "hybridclr_unity": source_workspace / "hybridclr_unity",
            "il2cpp_plus": source_workspace / "il2cpp_plus",
        }, require_checkout_heads=True)
        require(report["result"] == "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
                "Source-only candidate admission failed")
        super().__init__(workspace, output, unity, demo_commit)
        # The inherited original R03 code still starts with historical 74db;
        # the strictly verified candidate is a separate in-memory effective tuple.
        from current_native_source_gate import read_config
        self.pins = candidate_pins(self.pins, read_config())
        self.current_source_report = report
        require(self.pins["il2cpp_plus"] == CURRENT["il2cpp_plus"] and
                self.pins["il2cpp_plus"] != OLD_NATIVE,
                "Current candidate must not run historical R03 native source")

    def authority(self):
        # The original method independently verifies all four real repositories,
        # branch, clean state, origin and live remote HEAD against effective pins.
        origin = super().authority()
        return {
            "kind": "R03IRCurrentNativePinAuthority",
            "result": "PassedSourceAuthority_NotRuntimeAcceptance",
            "repositories": origin["repositories"],
            "candidateNative": self.pins["il2cpp_plus"],
            "originalNativePinUntouched": OLD_NATIVE,
            "candidateSourceFilesVerified": self.current_source_report["verifiedSourceFiles"],
            "inputContract": str(CONFIG),
            "actualUnityPlayerExecutedAtAuthority": False,
            "runtimeAcceptance": False,
        }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("workspace", "output", "unity", "demo-commit"):
        p.add_argument("--" + field, required=True)
    a = p.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", a.demo_commit) is not None,
            "Exact committed demo HEAD required")
    require(Path(a.workspace).is_absolute() and Path(a.output).is_absolute(),
            "Canonical absolute workspace/output paths required")
    # Intentionally no --dry-run that could create a pseudo-PASS or shell bypass:
    # the current candidate is an explicit distinct source-bound Player execution.
    return run_existing_focused_batch(
        a.workspace, a.output, a.unity, a.demo_commit,
        batch_type=CurrentNativeBatch)


if __name__ == "__main__":
    raise SystemExit(main())
