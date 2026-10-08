"""Strict R02 type-info bridge; legacy verifiers remain unchanged by default.

Only the known versioned extension is validated and projected for the original
M07 field/semantic checks. Projection is in memory; raw files and hashes are
never rewritten. The scope is single-threaded, synchronous verifier execution.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import sys
if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import m05_results
import m07_results
from evidence import require, loads

COUNTERS = (
    "definitionSearches", "definitionRowsScanned", "admissionCacheHits", "admissionCacheMisses",
    "admissionProofAttempts", "admissionProofRejections", "admissionEntries", "admissionRetainedBytes",
    "admissionUnready", "baselineStateChecks", "fieldWorkspaceBuilds", "interfaceWorkspaceBuilds",
    "layoutCheckCalls", "counterpartCacheHits", "counterpartCacheMisses", "counterpartEntries",
    "absentCounterpartEntries", "cacheFixedBytes", "counterpartRetainedBytes", "genericContextChecks",
    "observationLockContentions", "observationMemoHits", "observationMemoTlsBytesPerThread",
    "counterStorageBytes", "counterThreadCapacity", "droppedCounterThreads")
BOOLEANS = ("counterSaturated", "memoryAccountingAvailable")
STRINGS = ("counterCoverage", "classesCoverage", "memoryAccountingScope")
FIELDS = frozenset(COUNTERS + BOOLEANS + STRINGS + ("schemaVersion", "diagnosticsLevel"))
COVERAGE = ("Disabled", "Truncated", "Saturated", "BoundedComplete")


def validate_extension(value, path="r02"):
    require(type(value) is dict and set(value) == FIELDS, path + ": exact 33-field R02 object required")
    require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 1, path + ": unknown schema")
    require(type(value["diagnosticsLevel"]) is int and value["diagnosticsLevel"] in (0, 1, 2), path + ": invalid profile")
    for name in COUNTERS:
        require(type(value[name]) is int and 0 <= value[name] <= (1 << 64) - 1, path + ": invalid UInt64 " + name)
    for name in BOOLEANS:
        require(type(value[name]) is bool, path + ": invalid boolean " + name)
    for name in STRINGS:
        require(type(value[name]) is str, path + ": invalid string " + name)
    require(value["counterThreadCapacity"] == 128 and
            value["memoryAccountingScope"] == "R02StructuresExcludingAllocatorOverhead", path + ": unsupported accounting contract")
    require(value["counterCoverage"] in COVERAGE and value["classesCoverage"] in COVERAGE, path + ": unknown coverage")
    level = value["diagnosticsLevel"]
    if level == 0:
        require(value["counterCoverage"] == value["classesCoverage"] == "Disabled" and
                value["memoryAccountingAvailable"] is False, path + ": disabled profile claims available data")
    else:
        require(value["counterCoverage"] != "Disabled" and
                ((value["classesCoverage"] == "Disabled") if level == 1 else (value["classesCoverage"] != "Disabled")),
                path + ": coverage/profile mismatch")
    # No cross-counter equations: native fields are a non-atomic live snapshot.
    return value


def legacy_projection(value, path):
    require(type(value) is dict and set(value) == set(m05_results.TYPE_INFO_FIELDS.split()) | {"r02"},
            path + ": expected legacy fields plus known r02, with no omissions or additions")
    validate_extension(value["r02"], path + ".r02")
    legacy = {key: item for key, item in value.items() if key != "r02"}
    m05_results.verify_type_info(legacy, path)
    return legacy


@contextmanager
def current_m07_schema():
    original = m07_results.verify_type_resolutions
    record = {"kind": "R02StrictM07TypeInfoBridge", "schemaVersion": 1,
              "profile": 2, "verifiedTypeInfoObjects": 0, "rawEvidenceModified": False}
    def verify(result, path, closure, feature_off):
        if feature_off:
            return original(result, path, closure, feature_off)
        # Copy only the branch delegated to the legacy checker. Every original
        # file, raw string and outer result remains untouched and hash-bound.
        projected = dict(result); projected["typeResolutions"] = []
        for index, row in enumerate(result["typeResolutions"]):
            value = loads(row["rawJson"])
            legacy = legacy_projection(value, str(path) + ".typeResolutions[" + str(index) + "]")
            require(value["r02"]["diagnosticsLevel"] == 2, "Current M07 evidence requires the default R02 profile")
            item = dict(row); item["rawJson"] = json.dumps(legacy, separators=(",", ":"))
            projected["typeResolutions"].append(item)
        original(projected, path, closure, feature_off)
        record["verifiedTypeInfoObjects"] += len(projected["typeResolutions"])
    m07_results.verify_type_resolutions = verify
    try:
        yield record
    finally:
        m07_results.verify_type_resolutions = original
