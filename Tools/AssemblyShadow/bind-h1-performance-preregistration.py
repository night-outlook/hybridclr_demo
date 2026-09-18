#!/usr/bin/env python3
"""Bind the preregistered H1 performance protocol/schedule to a fresh evidence root without changing sampling decisions."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

import h1_paired_performance as analysis
from shadow_tools import require

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "tests/fixtures/h1"
SOURCE_PROTOCOL = FIXTURES / "performance-protocol.preregistered.json"
SOURCE_SCHEDULE = FIXTURES / "performance-schedule.preregistered.json"

_spec = importlib.util.spec_from_file_location(
    "h1_bound_performance_runner", HERE / "run-h1-paired-performance.py")
_runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_runner)


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def bind(output_root: Path) -> dict:
    require(output_root.is_absolute() and output_root == output_root.resolve() and
            not output_root.exists() and not output_root.is_symlink() and
            output_root.parent.is_dir() and not output_root.parent.is_symlink(),
            "output root must be a new canonical directory in an existing parent")
    require(SOURCE_PROTOCOL.is_file() and not SOURCE_PROTOCOL.is_symlink() and
            SOURCE_SCHEDULE.is_file() and not SOURCE_SCHEDULE.is_symlink(),
            "preregistered performance fixtures are missing")

    source_protocol = read(SOURCE_PROTOCOL)
    source_schedule = read(SOURCE_SCHEDULE)
    require(source_protocol.get("schemaVersion") == 1 and
            source_protocol.get("kind") == "H1ControlledPerformanceProtocolTemplate" and
            source_protocol.get("protocolId") == analysis.PROTOCOL_ID,
            "preregistered protocol identity differs")
    require(source_schedule.get("schemaVersion") == 1 and
            source_schedule.get("kind") == "H1ControlledPairSchedule" and
            source_schedule.get("executionRequiresFrozenBuildMap") is True,
            "preregistered schedule identity differs")

    output_root.mkdir()
    protocol_out = output_root / "performance-protocol.preregistered.json"
    schedule_out = output_root / "performance-schedule.bound.json"
    protocol_out.write_bytes(SOURCE_PROTOCOL.read_bytes())

    bound_schedule = copy.deepcopy(source_schedule)
    bound_schedule["protocolPath"] = str(protocol_out)
    bound_schedule["protocolSha256"] = analysis.digest(protocol_out)
    schedule_out.write_text(json.dumps(bound_schedule, indent=2) + "\n", encoding="utf-8")

    restored = copy.deepcopy(bound_schedule)
    restored["protocolPath"] = source_schedule["protocolPath"]
    restored["protocolSha256"] = source_schedule["protocolSha256"]
    require(restored == source_schedule,
            "binding changed preregistered schedule fields other than protocolPath/protocolSha256")

    protocol, pairs = _runner._validate_protocol(protocol_out), None
    pairs = _runner._validate_schedule(schedule_out, protocol_out, protocol)

    require([row["pairId"] for row in pairs] ==
            [row["pairId"] for row in source_schedule["pairs"]] and
            [row["order"] for row in pairs] ==
            [row["order"] for row in source_schedule["pairs"]],
            "bound schedule changed preregistered pair identity/order")

    receipt = {
        "schemaVersion": 1,
        "kind": "H1PerformancePreregistrationBinding",
        "result": "Passed",
        "sourceProtocolPath": str(SOURCE_PROTOCOL),
        "sourceProtocolSha256": analysis.digest(SOURCE_PROTOCOL),
        "sourceSchedulePath": str(SOURCE_SCHEDULE),
        "sourceScheduleSha256": analysis.digest(SOURCE_SCHEDULE),
        "boundProtocolPath": str(protocol_out),
        "boundProtocolSha256": analysis.digest(protocol_out),
        "boundSchedulePath": str(schedule_out),
        "boundScheduleSha256": analysis.digest(schedule_out),
        "protocolBytesUnchanged": protocol_out.read_bytes() == SOURCE_PROTOCOL.read_bytes(),
        "scheduleSemanticFieldsUnchanged": True,
        "pairCount": len(pairs),
        "protocolId": protocol["protocolId"],
        "acceptanceClaimed": False,
    }
    require(receipt["protocolBytesUnchanged"] and receipt["pairCount"] == 44,
            "bound preregistration integrity differs")
    receipt_path = output_root / "performance-preregistration-binding.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    receipt = bind(args.output_root)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
