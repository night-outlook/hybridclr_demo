"""Fresh R02 vs H1-runtime paired measurements, never historical relabeling."""
from __future__ import annotations
from pathlib import Path
import random
import sys
from evidence import require, read, write, binding, check_binding, number
from verify import MODES

TOOLS = Path(__file__).resolve().parent.parent
if str(TOOLS) not in sys.path: sys.path.insert(0, str(TOOLS))
import h1_paired_performance as shared


def schedule(seed=20260926):
    rng = random.Random(seed)
    pairs = []
    for phase, count in (("pilot", 1), ("formal", 10)):
        for n in range(count):
            modes = list(MODES); rng.shuffle(modes)
            for mode in modes:
                pairs.append({"pairId": mode + "-" + phase + "-" + str(n + 1).zfill(2),
                              "mode": mode, "phase": phase, "order": ["A", "B"] if n % 2 == 0 else ["B", "A"]})
    return {"kind": "R02PairedSchedule", "protocol": "R02LocalBatch-v1", "seed": seed,
            "algorithm": "seeded mode shuffle per round; alternating AB/BA; all pilots first", "pairs": pairs,
            "ratioResolutionTicks": 10, "outlierPolicy": "Retain all valid samples; no latency-based exclusions",
            "retryPolicy": "No automatic retries; preserve failure and stop this series",
            "sidecarEnabled": False, "cooldownSeconds": 2, "runtimeAcceptance": False}


def validate_schedule(value):
    require(value == schedule(), "Schedule differs from frozen R02 protocol")
    return value["pairs"]


def authenticate_map(value):
    require(value.get("kind") == "R02ControlledBuildMap" and value.get("protocol") == "R02LocalBatch-v1", "Wrong R02 build map")
    bindings, facts = shared._build_bindings(value)
    require(all(facts["A"][key] == facts["B"][key] for key in shared.MATCH_FIELDS), "Unmatched controlled build facts")
    require(all(facts["A"][key] != facts["B"][key] for key in shared.EXPECTED_DIFFERENCES), "Control is not a distinct source/runtime")
    return bindings, facts


def verify_intervals(pairs, expected):
    require(len(pairs) == len(expected) == 44, "Incomplete paired series")
    previous_end = 0.0
    identities = set()
    for row, planned in zip(pairs, expected):
        require(row["pairId"] == planned["pairId"] and row["mode"] == planned["mode"] and row["phase"] == planned["phase"] and
                row["order"] == planned["order"] and row.get("result") == "Passed", "Pair does not match schedule")
        require(set(row["sides"]) == {"A", "B"}, "Pair is missing a side")
        for side in planned["order"]:
            value = row["sides"][side]
            start = number(value["startedAtUnix"], "start")
            end = number(value["endedAtUnix"], "end")
            require(0 < start <= end and start >= previous_end, "Pair chronology overlaps or is reversed")
            require(value["runId"] not in identities, "Reused sample nonce")
            identities.add(value["runId"]); previous_end = end
    return identities


def analyze(index_path: Path):
    index = read(index_path)
    require(index.get("kind") == "R02PairedIndex" and index.get("result") == "Passed", "Incomplete/failed paired index")
    schedule_path = check_binding(index["schedule"])
    expected = validate_schedule(read(schedule_path))
    map_path = check_binding(index["buildMap"])
    builds, facts = authenticate_map(read(map_path))
    verify_intervals(index["pairs"], expected)
    metrics = []
    for pair, plan in zip(index["pairs"], expected):
        verified = {"attempt": 1}
        for side in plan["order"]:
            retained = pair["sides"][side]
            receipt = read(check_binding(retained["receipt"]))
            require(receipt.get("kind") == "R02Sample" and receipt.get("result") == "Passed" and
                    receipt.get("sidecarEnabled") is False and receipt["runId"] == retained["runId"], "Wrong performance sample")
            require(receipt["role"] == ("control" if side == "A" else "candidate"), "Reversed performance role")
            require(receipt["mode"] == plan["mode"], "Wrong performance sample mode")
            command = read(check_binding(receipt["command"]))
            require(command["result"] == "Passed" and command["processGroupClean"] is True and command["timedOut"] is False,
                    "Sample command failed")
            require(retained["startedAtUnix"] == command["startedAtUnix"] and retained["endedAtUnix"] == command["endedAtUnix"],
                    "Invented sample interval")
            launch = check_binding(receipt["launch"])
            world = "OFF" if plan["mode"] == MODES[0] else "ON"
            rebuilt = shared.verify_launch(launch, plan["mode"], expected_build=builds[side][world])
            require(rebuilt["valid"], "Strict R00 sample reconstruction failed: " + rebuilt.get("error", ""))
            require(read(check_binding(receipt["raw"])) == rebuilt["raw"], "Sample raw binding mismatch")
            player_start = rebuilt["process"]["startedAtUnix"]
            player_end = player_start + rebuilt["process"]["durationSeconds"]
            require(command["startedAtUnix"] <= player_start <= player_end <= command["endedAtUnix"] + 1,
                    "Player launch not contained in sample command")
            verified[side] = rebuilt
        metrics.append(shared._attempt_metrics(verified, plan))
    return {"kind": "R02PairedAnalysis", "result": "Passed", "comparability": "ComparabilityPassed",
            "sampleIndex": binding(index_path), "formalPairs": 40, "pilotPairs": 4,
            "statistics": shared._aggregate(metrics), "pairs": metrics, "buildFacts": facts,
            "performanceAcceptance": "NotClaimedPendingReview", "runtimeAcceptance": False,
            "scope": "Fresh H1-runtime control vs R02 candidate, common new managed sources; Development macOS arm64 only"}
