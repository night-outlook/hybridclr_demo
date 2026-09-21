#!/usr/bin/env python3
"""Run all remaining H1 formal pairs sequentially using one sealed bridge authority.

The batch never retries a failed pair automatically.  It stops after retaining
that whole-pair attempt.  A protocol-valid retry must be performed explicitly
with run-h1-paired-performance.py; this batch may then resume from the resulting
sample index.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

from shadow_tools import VerificationError, read_json, require


_spec = importlib.util.spec_from_file_location(
    "h1_formal_batch_driver", Path(__file__).with_name("run-h1-paired-performance.py"))
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict[str, str]:
    path = path.resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), "Expected canonical regular file: " + str(path))
    return {"path": str(path), "sha256": digest(path)}


def _latest_formal(attempts: list[dict], pair_id: str) -> dict | None:
    rows = [row for row in attempts if row.get("phase") == "formal" and row.get("pairId") == pair_id]
    return max(rows, key=lambda row: row.get("attempt", 0)) if rows else None


def require_resumable(attempts: list[dict], schedule: list[dict]) -> None:
    for pair in [row for row in schedule if row.get("phase") == "formal"]:
        latest = _latest_formal(attempts, pair["pairId"])
        if latest is not None:
            require(latest.get("status") == "Passed",
                    "Formal batch cannot skip an unresolved failed pair; explicitly retry first: " + pair["pairId"])


def remaining_pairs(attempts: list[dict], schedule: list[dict]) -> list[dict]:
    require_resumable(attempts, schedule)
    return [
        row for row in schedule if row.get("phase") == "formal" and
        _latest_formal(attempts, row["pairId"]) is None
    ]


def _write_receipt(path: Path, value: dict) -> None:
    require(not path.exists() and not path.is_symlink(), "Formal batch receipt must be new")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--schedule", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--build-map", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--graph-reuse-bridge", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--pilot-verification-receipt", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--prior-index", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout", type=driver._positive, default=900)
    args = parser.parse_args(argv)

    output_root = args.output_root
    require(output_root.is_absolute() and output_root == output_root.resolve() and
            not output_root.exists() and not output_root.is_symlink(),
            "Formal batch output root must be a new canonical absolute path")
    require(output_root.parent.is_dir() and not output_root.parent.is_symlink(),
            "Formal batch output parent is unavailable")
    output_root.mkdir()

    protocol = driver._validate_protocol(args.protocol)
    schedule = driver._validate_schedule(args.schedule, args.protocol, protocol)
    build = driver._validate_build(args.build_map, protocol)

    prior_path = args.prior_index
    initial_binding = binding(prior_path)
    rows = []
    sequence = 0
    status = "Passed"
    failure = ""

    while True:
        attempts = driver._load_prior(
            prior_path, args.protocol, args.schedule, args.build_map, schedule, "formal", build,
            args.pilot_verification_receipt, args.graph_reuse_bridge)
        pending = remaining_pairs(attempts, schedule)
        if not pending:
            break
        pair = pending[0]
        sequence += 1
        pair_root = output_root / (
            f"{sequence:02d}-" + driver._safe_name(pair["pairId"]) + "-attempt-1")
        started = time.time()
        code = driver.main([
            "--protocol", str(args.protocol),
            "--schedule", str(args.schedule),
            "--build-map", str(args.build_map),
            "--graph-reuse-bridge", str(args.graph_reuse_bridge),
            "--pilot-verification-receipt", str(args.pilot_verification_receipt),
            "--prior-index", str(prior_path),
            "--output-root", str(pair_root),
            "--phase", "formal",
            "--pair-id", pair["pairId"],
            "--attempt", "1",
            "--timeout", str(args.timeout),
        ])
        ended = time.time()
        sample_path = pair_root / "sample-index.json"
        sample_binding = binding(sample_path) if sample_path.is_file() else None
        rows.append({
            "pairId": pair["pairId"],
            "mode": pair["mode"],
            "order": pair["order"],
            "attempt": 1,
            "outputRoot": str(pair_root),
            "exitCode": code,
            "startedAtUnix": started,
            "finishedAtUnix": ended,
            "durationSeconds": ended - started,
            "sampleIndex": sample_binding,
        })
        if sample_binding is not None:
            prior_path = sample_path
        if code != 0:
            status = "StoppedOnFailedWholePair"
            failure = (
                "A formal pair failed and was retained. Diagnose it and perform an explicit whole-pair retry "
                "before resuming the batch from the retry sample index."
            )
            break

    final_attempts = read_json(prior_path).get("attempts", [])
    formal_rows = [row for row in schedule if row.get("phase") == "formal"]
    passed_pairs = [
        pair["pairId"] for pair in formal_rows
        if (_latest_formal(final_attempts, pair["pairId"]) or {}).get("status") == "Passed"
    ]
    complete = len(passed_pairs) == len(formal_rows)
    if status == "Passed":
        require(complete, "Formal batch ended without a failed pair but formal inventory is incomplete")

    receipt = {
        "schemaVersion": 1,
        "kind": "H1FormalBatchRun",
        "status": "PassedAllFormalPairs" if complete else status,
        "protocol": binding(args.protocol),
        "schedule": binding(args.schedule),
        "buildMap": binding(args.build_map),
        "graphReuseBridge": binding(args.graph_reuse_bridge),
        "pilotVerification": binding(args.pilot_verification_receipt),
        "initialPriorIndex": initial_binding,
        "finalSampleIndex": binding(prior_path),
        "formalPairCount": len(formal_rows),
        "formalPairsPassed": len(passed_pairs),
        "formalPairsStartedByThisBatch": len(rows),
        "failure": failure,
        "runs": rows,
    }
    receipt_path = output_root / "formal-batch.json"
    _write_receipt(receipt_path, receipt)
    print(("Passed" if complete else "Stopped") + ": " + str(receipt_path), flush=True)
    return 0 if complete else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        print("[FAIL] " + str(error), flush=True)
        raise SystemExit(1)
