"""Strict R02 sidecar semantics. Execution/build identity is bound by run_local.

This module never upgrades an unavailable diagnostic into a zero-cost proof.
Its standalone raw check is necessary but not sufficient for Player acceptance.
"""
from __future__ import annotations
from pathlib import Path
import re
from evidence import require, integer, number, loads, read, binding, check_binding

MODES = ("R00-OFF-NoPatch", "R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03")
OPERATIONS = ("allocation", "closed-generic", "array", "boxing", "virtual", "interface", "delegate", "added-type")
COUNTERS = ("definitionSearches", "definitionRowsScanned", "admissionCacheHits", "admissionCacheMisses",
            "admissionProofAttempts", "admissionProofRejections", "admissionEntries", "admissionRetainedBytes",
            "admissionUnready", "baselineStateChecks", "fieldWorkspaceBuilds", "interfaceWorkspaceBuilds",
            "layoutCheckCalls", "counterpartCacheHits", "counterpartCacheMisses", "counterpartEntries",
            "absentCounterpartEntries", "cacheFixedBytes", "counterpartRetainedBytes", "genericContextChecks",
            "observationLockContentions", "observationMemoHits")
COLD_ONLY = ("definitionSearches", "definitionRowsScanned", "admissionProofAttempts",
             "fieldWorkspaceBuilds", "interfaceWorkspaceBuilds", "layoutCheckCalls")


def marker(mode):
    require(mode in MODES, "Unknown R00 mode")
    return 3001 if mode.endswith("P01") else 3003 if mode.endswith("P03") else 3000


def expected_checksum(count, seed, value):
    return 17 * (count * seed + count * (count - 1) // 2) + value * count


def expected_rows(mode):
    operations = OPERATIONS if mode.endswith(("P01", "P03")) else OPERATIONS[:-1]
    rows = [(op, phase, count, seed) for op in operations for phase, count, seed in
            (("first-observed", 1, 17), ("warm10", 10, 2017), ("warm10000", 10000, 3017))]
    rows.extend(("scale-" + str(n), phase, n, seed) for n in (100, 1000)
                for phase, seed in (("first-observed", 17), ("warm", 2017)))
    return rows


def snapshot(value, role, mode, start, end):
    require(type(value) is dict, "Missing snapshot")
    ticks = integer(value["utcTicks"], "snapshot ticks", start, end)
    for key in ("currentRssBytes", "managedBytes", "lifetimePeakRssBytes"):
        integer(value[key], key)
    require(value["lifetimePeakRssBytes"] >= value["currentRssBytes"], "RSS exceeds lifetime peak")
    require(isinstance(value["executionJson"], str), "Raw execution JSON is required")
    if mode == MODES[0]:
        require(value["executionCode"] == "FeatureDisabled", "OFF diagnostics were enabled")
        return None
    require(value["executionCode"] == "Success", "Enabled execution diagnostics failed")
    raw = loads(value["executionJson"])
    require(type(raw) is dict, "Execution diagnostics are not an object")
    if role == "control":
        require("r02" not in raw, "Control unexpectedly contains R02 runtime")
        return None
    r02 = raw.get("r02")
    require(type(r02) is dict and r02.get("schemaVersion") == 1, "Missing R02 diagnostics")
    require(type(r02.get("diagnosticsLevel")) is int and r02["diagnosticsLevel"] == 2,
            "This frozen functional batch requires diagnostics level 2")
    require(r02.get("counterCoverage") == "BoundedComplete" and r02.get("droppedCounterThreads") == 0 and
            r02.get("counterSaturated") is False, "Counters are unavailable, saturated, or truncated")
    require(r02.get("classesCoverage") in ("BoundedComplete", "Truncated"), "Unexpected class coverage")
    require(r02.get("memoryAccountingAvailable") is True and
            r02.get("memoryAccountingScope") == "R02StructuresExcludingAllocatorOverhead", "Memory accounting unavailable")
    for key in COUNTERS + ("counterStorageBytes", "counterThreadCapacity", "observationMemoTlsBytesPerThread"):
        integer(r02[key], key)
    require(r02["counterThreadCapacity"] == 128, "Counter capacity differs from frozen runtime")
    return r02


def verify_raw(raw, role, mode, run_id, r00, launch):
    require(role in ("control", "candidate"), "Unknown source role")
    require(re.fullmatch(r"[0-9a-f]{32}", run_id) is not None, "Invalid run ID")
    require(type(raw) is dict and raw.get("schemaVersion") == 1 and raw.get("kind") == "R02PlayerWitness" and
            raw.get("protocol") == "R02LocalBatch-v1", "Wrong R02 result contract")
    require(raw.get("result") == "Passed" and raw.get("error") == "" and raw.get("runtimeAcceptance") is False,
            "Raw witness failed or overclaimed acceptance")
    require((raw["role"], raw["mode"], raw["runId"]) == (role, mode, run_id), "Wrong role/mode/nonce")
    require(raw["marker"] == marker(mode), "Wrong active witness marker")
    require(raw["witnessType"] == "AssemblyA.Implementation.Internal.R02AllocationWitness", "Wrong witness type")
    require(r00.get("il2cpp") is True and r00.get("result") == "Passed", "R00 did not pass as an IL2CPP Player")
    for key in ("processId", "buildGuid", "baselineBuildId", "runtimeAbiHash", "unityVersion", "platform", "mode"):
        require(raw[key] == r00[key], "R02/R00 identity mismatch: " + key)
    require(raw["processId"] == integer(launch["processId"], "Player PID", 1), "Launch PID mismatch")
    require(raw["unityVersion"] == "2022.3.62f2" and raw["platform"] == "OSXPlayer", "Wrong platform")
    require(launch["exitCode"] == 0 and launch["timedOut"] is False and launch["passed"] is True,
            "Player did not exit successfully")
    start = integer(raw["startedUtcTicks"], "R02 start", 1)
    end = integer(raw["endedUtcTicks"], "R02 end", start)
    begin_unix = number(launch["startedAtUnix"], "launch start")
    finish = begin_unix + number(launch["durationSeconds"], "launch duration")
    require(begin_unix - 1 <= start / 1e7 - 62135596800 <= end / 1e7 - 62135596800 <= finish + 1,
            "R02 interval outside its Player launch")
    if mode == MODES[0]:
        require(raw["typeInfoCode"] == "FeatureDisabled", "OFF type diagnostics enabled")
    else:
        require(raw["typeInfoCode"] == "Success", "Type diagnostics failed")
        info = loads(raw["typeInfoJson"])
        require(info["logicalAssembly"] == "AssemblyA.Implementation.Internal" and info["isActive"] is True and
                info["executionMode"] == ("InterpreterShadow" if mode.endswith(("P01", "P03")) else "AotBaseline"),
                "Wrong physical execution world")
    require(type(raw["memoryMeasurement"]) is str and raw["memoryMeasurement"] and
            "noForcedGC" in raw["memorySemantics"], "Missing memory semantics")
    handles = raw["scaleTypeHandles"]
    require(type(handles) is list and len(handles) == 1000 and len(set(handles)) == 1000 and
            all(type(h) is str and re.fullmatch(r"-?[1-9][0-9]*", h) for h in handles), "Scale types are not 1000 unique physical handles")
    expected = expected_rows(mode)
    require(type(raw["rows"]) is list and len(raw["rows"]) == len(expected), "Missing/extra witness rows")
    summaries = []
    prior_tick = start
    for row, contract in zip(raw["rows"], expected):
        require((row["operation"], row["phase"], row["iterations"], row["seed"]) == contract, "Witness row order/shape mismatch")
        _, _, count, seed = contract
        integer(row["iterations"], "iterations", 1, 10000)
        before_count = integer(row["constructorsBefore"], "constructors before")
        after_count = integer(row["constructorsAfter"], "constructors after", before_count)
        require(after_count - before_count == count, "Constructor count is not invocation count")
        expected_sum = expected_checksum(count, seed, marker(mode))
        require(type(row["checksum"]) is int and row["checksum"] == expected_sum == row["expectedChecksum"] and
                row["passed"] is True, "Independent checksum mismatch")
        ticks = integer(row["elapsedTicks"], "elapsed ticks")
        frequency = integer(row["stopwatchFrequency"], "stopwatch frequency", 1)
        a = snapshot(row["before"], role, mode, prior_tick, end)
        b = snapshot(row["after"], role, mode, row["before"]["utcTicks"], end)
        prior_tick = row["after"]["utcTicks"]
        deltas = {}
        if a is not None:
            for key in COUNTERS:
                require(b[key] >= a[key], "Counter decreased: " + key)
                deltas[key] = b[key] - a[key]
            require(deltas["admissionProofRejections"] == 0, "Positive witness encountered an admission rejection")
            # A narrowly scoped single-class hot loop is the Player certificate
            # oracle. Other workload deltas are reported, not guessed per type.
            if mode.endswith(("P01", "P03")) and row["operation"] == "allocation" and row["phase"] == "warm10000":
                require(all(deltas[k] == 0 for k in COLD_ONLY), "Warm single-class path rebuilt proof or scanned metadata")
                require(deltas["admissionCacheHits"] >= count, "Warm single-class path did not hit its certificate")
        summaries.append({"operation": row["operation"], "phase": row["phase"], "secondsPerOp": ticks / frequency / count,
                          "elapsedTicks": ticks, "counterDeltas": deltas,
                          "diagnosticEvidence": "Available" if a is not None else "Unavailable"})
    p = raw["parallel"]
    require((p["workerCount"], p["iterationsPerWorker"], p["seed"]) == (4, 1000, 7017), "Wrong parallel workload")
    require(p["passed"] is True and p["joined"] == [True] * 4 and
            len(p["errors"]) == 4 and all(x in ("", None) for x in p["errors"]), "Parallel workers did not all complete")
    require(len(p["threadIds"]) == 4 and len(set(p["threadIds"])) == 4 and
            all(type(x) is int and x > 0 for x in p["threadIds"]), "Parallel worker identities invalid")
    require(p["constructorsAfter"] - p["constructorsBefore"] == 4000, "Parallel constructor count mismatch")
    require(p["checksums"] == [expected_checksum(1000, 7017 + i * 1000, marker(mode)) for i in range(4)], "Parallel checksum mismatch")
    integer(p["elapsedTicks"], "parallel ticks"); integer(p["stopwatchFrequency"], "parallel frequency", 1)
    snapshot(p["before"], role, mode, prior_tick, end)
    snapshot(p["after"], role, mode, p["before"]["utcTicks"], end)
    return {"kind": "R02WitnessSemantics", "result": "Passed", "role": role, "mode": mode, "runId": run_id,
            "rowCount": len(expected), "scaleTypeCount": 1000, "workerCount": 4, "measurements": summaries,
            "runtimeAcceptance": False, "scope": "Raw semantics only; requires strict R00 source/build/launch authentication"}
