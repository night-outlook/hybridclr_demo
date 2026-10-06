#!/usr/bin/env python3
"""Source-bound current R02 M07/startup gates, reusing the strict legacy checks."""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE.parent) not in sys.path: sys.path.insert(0, str(HERE.parent))
import authority
import m07_results
import r01_early_results
from evidence import binding, read, require, write
from type_resolution_schema import current_m07_schema


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kind", choices=("m07", "startup11"), required=True)
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--candidate-head", required=True)
    p.add_argument("--output", type=Path, required=True)
    args, remaining = p.parse_known_args(argv)
    require("--allow-incomplete" not in remaining, "Incomplete current regression coverage is forbidden")
    output = args.output.absolute()
    require(not output.exists() and not output.is_symlink(), "Unused strict output required")
    receipt = output.with_name(output.name + ".r02-schema.json")
    require(not receipt.exists() and not receipt.is_symlink(), "Unused bridge receipt required")
    report = {"kind": "R02CurrentRegressionVerification", "result": "Failed", "regression": args.kind,
              "runtimeAcceptance": False, "legacyVerifierUnchanged": True}
    try:
        targets = read(args.project_root / authority.TARGETS)
        report["authorityBefore"] = authority.inspect(args.project_root, args.candidate_head, "candidate", targets)
        with current_m07_schema() as bridge:
            report["typeInfoBridge"] = bridge
            verifier = m07_results.main if args.kind == "m07" else r01_early_results.main
            require(verifier(remaining + ["--output", str(output)]) == 0, "Strict delegated verifier failed")
            result = read(output)
            if args.kind == "m07":
                require(result.get("resultPassed") is True and result.get("diagnosticOnly") is False and
                        result.get("missingModes") == [] and len(result.get("modes", [])) == len(m07_results.MODES),
                        "Incomplete M07 matrix")
            else:
                require(result.get("result") == "PassedBoundedProfile" and
                        result.get("requestedModes") == list(r01_early_results.DEFAULT_MODES) and
                        len(result.get("modes", [])) == 11 and
                        all(row.get("diagnosticProfileComplete") is True for row in result["modes"]),
                        "Incomplete startup11 profile")
            require(bridge["verifiedTypeInfoObjects"] > 0, "No current R02 type-info observations were verified")
        report["strictOutput"] = binding(output)
        report["authorityAfter"] = authority.inspect(args.project_root, args.candidate_head, "candidate", targets)
        report["result"] = "Passed"
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    write(receipt, report)
    require(report["result"] == "Passed", report.get("error", "Current regression failed"))
    return 0


if __name__ == "__main__": raise SystemExit(main())
