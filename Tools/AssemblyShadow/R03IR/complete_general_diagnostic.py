#!/usr/bin/env python3
"""Strict R03 full-general diagnostic sidecar verifier.

This is a host-side byte/format check of the unmodified, full native
GetDiagnosticsJson text. It does not assert global VM coherence or runtime
acceptance. No write and no path from untrusted JSON is ever followed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import zlib

TEXT_LIMIT = 262144
GENERAL_LIMIT = 3932160
PREFIX = "R03FullGeneralSidecarV1:"
DESCRIPTOR = re.compile(r"R03FullGeneralSidecarV1:([1-9][0-9]*):([0-9a-f]{8})\Z")
REQUIRED_ARRAYS = (
    "startupCandidateNames", "closureLoadOrder", "stableAotNames",
    "commitOrder", "assemblies", "events", "baselineUses",
    "ordinaryAssemblies", "ordinaryClasses",
)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("R03 complete general diagnostic: " + reason)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        require(name not in result, "duplicate field: " + name)
        result[name] = value
    return result


def parse_complete(data: bytes) -> dict:
    require(data and len(data) <= GENERAL_LIMIT and data[:1] == b"{" and
            data[-1:] == b"}", "missing/oversized/non-object full bytes")
    result = json.loads(data.decode("utf-8", "strict"), object_pairs_hook=unique_pairs)
    require(type(result) is dict and type(result.get("schemaVersion")) is int and
            result["schemaVersion"] == 1 and result.get("enabled") is True and
            result.get("state") == "FailedAfterCommit" and
            type(result.get("stateCode")) is int and result["stateCode"] == 9,
            "terminal full-general schema/state mismatch")
    for name in REQUIRED_ARRAYS:
        require(type(result.get(name)) is list, "missing full source array: " + name)
    for key in ("enumerationGeneration", "classEnumerationGeneration", "generation"):
        require(type(result.get(key)) is int and result[key] >= 0, "invalid generation: " + key)
    # Independent class/assembly enumeration can be compared, but a matching
    # generation is NOT a coherent all-VM epoch or shutdown/GC admission.
    require(result["enumerationGeneration"] == result["classEnumerationGeneration"],
            "physical class/assembly enumeration generations disagree")
    return result


def verify(value: str, raw_path: Path | None = None) -> dict:
    require(type(value) is str and value != "", "missing report field 14")
    source = "InlineWithin256KiB"
    sidecar = None
    if value.startswith(PREFIX):
        m = DESCRIPTOR.fullmatch(value)
        require(m is not None, "invalid exact native full-general sidecar descriptor")
        length = int(m.group(1))
        require(TEXT_LIMIT < length <= GENERAL_LIMIT, "sidecar length out of fixed bounds")
        require(raw_path is not None and raw_path.is_absolute() and
                raw_path.is_file() and not raw_path.is_symlink() and
                raw_path.resolve(strict=True) == raw_path,
                "actual canonical raw receipt required for sidecar")
        sidecar = raw_path.with_name(raw_path.name + ".general.json")
        require(sidecar.is_file() and not sidecar.is_symlink() and
                sidecar.resolve(strict=True) == sidecar and
                sidecar.stat().st_size == length,
                "missing/symlink/wrong-sized preopened diagnostic sidecar")
        data = sidecar.read_bytes()
        require(len(data) == length and
                f"{zlib.crc32(data):08x}" == m.group(2),
                "native full-length CRC mismatch")
        source = "FullPreopenedSidecar"
    else:
        data = value.encode("utf-8", "strict")
        require(len(data) <= TEXT_LIMIT, "oversized unbound inline report")
        if raw_path is not None:
            sidecar = raw_path.with_name(raw_path.name + ".general.json")
            require(not sidecar.exists() and not sidecar.is_symlink(),
                    "unclaimed sidecar accompanies inline diagnostic")
            sidecar = None
    doc = parse_complete(data)
    return {
        "kind": "R03CompleteBoundedGeneralDiagnosticsV1",
        "result": "PassedCompleteByteBoundAndSchema_WithoutGlobalEpochProof",
        "transport": source,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "path": str(sidecar) if sidecar else None,
        "ordinaryAssemblyCount": len(doc["ordinaryAssemblies"]),
        "ordinaryClassCount": len(doc["ordinaryClasses"]),
        "enumerationGeneration": doc["enumerationGeneration"],
        "classEnumerationGeneration": doc["classEnumerationGeneration"],
        "coherentVmEpochProven": False,
        "runtimeAcceptance": False,
        "R03Accepted": False,
    }
