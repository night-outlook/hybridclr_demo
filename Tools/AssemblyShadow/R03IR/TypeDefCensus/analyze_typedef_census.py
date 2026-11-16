#!/usr/bin/env python3
"""Offline R03 B2 TypeDef capacity analysis. No Unity/VM source capture or acceptance.

Inputs are untrusted, caller-provided length-only event inventories. This tool
cannot authenticate their origin, completeness, metadata lifetime, or exact
name contents. It must never be treated as R03 validation evidence on its own.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "R03B2TypeDefCensusV1"
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 200_000
HEX40 = set("0123456789abcdef")
EVENT_KEYS = frozenset({
    "handleId", "ownerImageOrdinal", "firstOwnerImageOrdinal", "role",
    "namespaceBytes", "simpleNameBytes", "declaringIndex", "genericIndex",
    "arity",
})
SOURCE_KEYS = frozenset({
    "branch", "nativeCommit", "demoCommit", "metadataReaderEpoch",
    "metadataLockHeld", "originalV1ImageCount", "classPasses",
    "originalV1ImagePasses", "observedClasses", "declaredEvents",
    "droppedEvents", "complete",
})
ROOT_KEYS = frozenset({"schema", "captureKind", "source", "events"})


class CensusError(ValueError):
    pass


def reject(message: str) -> None:
    raise CensusError(message)


def exact_keys(value: object, keys: frozenset[str], name: str) -> dict:
    if type(value) is not dict:
        reject(f"{name}: expected an object")
    missing, extra = keys - value.keys(), value.keys() - keys
    if missing or extra:
        reject(f"{name}: missing={sorted(missing)}, unexpected={sorted(extra)}")
    return value


def unsigned(value: object, label: str, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        reject(f"{label}: invalid unsigned integer")
    return value


def signed32(value: object, label: str) -> int:
    if type(value) is not int or not -(1 << 31) <= value < (1 << 31):
        reject(f"{label}: invalid signed 32-bit integer")
    return value


def checked_sha(value: object, label: str) -> str:
    if type(value) is not str or len(value) != 40 or any(c not in HEX40 for c in value):
        reject(f"{label}: expected lowercase 40-character SHA")
    return value


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            reject(f"duplicate JSON property: {key}")
        result[key] = value
    return result


def load_bytes(raw: bytes) -> dict:
    if len(raw) > MAX_INPUT_BYTES:
        reject("input exceeds 16 MiB limit")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=lambda _: reject("non-finite JSON number"))
    except (UnicodeError, json.JSONDecodeError) as ex:
        raise CensusError(f"malformed UTF-8 JSON: {ex}") from ex


def histogram(values: list[int]) -> dict[str, int]:
    bins = {"0": 0, "1-8": 0, "9-16": 0, "17-32": 0, "33-64": 0, "65+": 0}
    for n in values:
        bucket = ("0" if n == 0 else "1-8" if n <= 8 else
                  "9-16" if n <= 16 else "17-32" if n <= 32 else
                  "33-64" if n <= 64 else "65+")
        bins[bucket] += 1
    return bins


def analyze(document: dict, digest: str = "") -> dict:
    body = exact_keys(document, ROOT_KEYS, "root")
    if body["schema"] != SCHEMA:
        reject("unsupported schema")
    if body["captureKind"] not in ("Synthetic", "UnverifiedSource"):
        reject("captureKind must be Synthetic or UnverifiedSource")

    s = exact_keys(body["source"], SOURCE_KEYS, "source")
    if s["branch"] != "codex/assembly-shadow-r01b-h1":
        reject("unexpected source branch")
    native = checked_sha(s["nativeCommit"], "source.nativeCommit")
    demo = checked_sha(s["demoCommit"], "source.demoCommit")
    epoch = unsigned(s["metadataReaderEpoch"], "metadataReaderEpoch", (1 << 32)-1)
    if epoch != 1:
        reject("current sources admit only the initial metadata reader epoch")
    if s["metadataLockHeld"] is not True:
        reject("metadata lock admission must be explicitly recorded")
    images = unsigned(s["originalV1ImageCount"], "originalV1ImageCount", 65536)
    if images == 0:
        reject("at least one original V1 image required for owner ordinals")
    if unsigned(s["classPasses"], "classPasses", 100) != 3:
        reject("expected three class observations")
    if unsigned(s["originalV1ImagePasses"], "originalV1ImagePasses", 100) != 2:
        reject("expected two V1 image observations")
    classes = unsigned(s["observedClasses"], "observedClasses", MAX_EVENTS)
    declared = unsigned(s["declaredEvents"], "declaredEvents", MAX_EVENTS)
    dropped = unsigned(s["droppedEvents"], "droppedEvents", MAX_EVENTS)
    if type(s["complete"]) is not bool:
        reject("source.complete must be a boolean")
    if s["complete"] and dropped:
        reject("completed source cannot report dropped events")

    events = body["events"]
    if type(events) is not list or len(events) != declared:
        reject("declaredEvents does not match the event list")
    if len(events) > MAX_EVENTS:
        reject("too many events")

    records: dict[int, tuple[tuple[int, ...], set[str]]] = {}
    roots = 0
    nonroots = 0
    for i, candidate in enumerate(events):
        e = exact_keys(candidate, EVENT_KEYS, f"events[{i}]")
        handle = unsigned(e["handleId"], f"events[{i}].handleId", (1 << 53)-1)
        if handle == 0:
            reject(f"events[{i}]: handleId is zero")
        owner = unsigned(e["ownerImageOrdinal"], f"events[{i}].owner", images-1)
        first = unsigned(e["firstOwnerImageOrdinal"], f"events[{i}].firstOwner", images-1)
        if owner != first:
            reject(f"events[{i}]: original V1 first-owner mismatch")
        role = e["role"]
        if role not in ("root", "nonroot"):
            reject(f"events[{i}]: invalid role")
        ns = unsigned(e["namespaceBytes"], f"events[{i}].namespaceBytes", 1_000_000)
        name = unsigned(e["simpleNameBytes"], f"events[{i}].simpleNameBytes", 1_000_000)
        declaration = signed32(e["declaringIndex"], f"events[{i}].declaringIndex")
        generic = signed32(e["genericIndex"], f"events[{i}].genericIndex")
        arity = unsigned(e["arity"], f"events[{i}].arity", (1 << 32)-1)
        signature = (owner, first, ns, name, declaration, generic, arity)
        if handle in records:
            original, roles = records[handle]
            if original != signature:
                reject(f"events[{i}]: conflicting owner/declaration for handleId={handle}")
            roles.add(role)
        else:
            records[handle] = (signature, {role})
        if role == "root":
            roots += 1
        else:
            nonroots += 1

    nss = [v[0][2] for v in records.values()]
    names = [v[0][3] for v in records.values()]
    root_ids = sum("root" in roles for _, roles in records.values())
    nonroot_ids = sum("nonroot" in roles for _, roles in records.values())
    overlaps = sum(len(roles) == 2 for _, roles in records.values())
    unique = len(records)
    total_name_bytes = sum(nss) + sum(names)
    full = bool(s["complete"] and dropped == 0 and events and classes)
    no_name_overlimit = max(nss + names, default=0) <= 64

    return {
        "schema": "R03B2TypeDefCensusAnalysisV1",
        "inputSha256": digest,
        "analysisStatus": "StructurallyCompleteUnverified" if full else "IncompleteLowerBound",
        "captureKind": body["captureKind"],
        "sourcePins": {"branch": s["branch"], "nativeCommit": native,
                       "demoCommit": demo},
        "observedClasses": classes,
        "events": {"recorded": len(events), "dropped": dropped,
                   "rootOccurrences": roots, "nonrootOccurrences": nonroots},
        "distinctTypeDefs": {"union": unique, "roots": root_ids,
                             "nonroots": nonroot_ids, "sharedBothRoles": overlaps},
        "nameLengths": {"namespaceHistogram": histogram(nss),
                        "simpleNameHistogram": histogram(names),
                        "maxNamespaceBytes": max(nss, default=0),
                        "maxSimpleNameBytes": max(names, default=0),
                        "totalDistinctNameBytes": total_name_bytes},
        "capacityObservations": {
            "currentCombined128Exceeded": unique > 128,
            "prototype1024Exceeded": unique > 1024,
            "current64ByteFieldLimitExceeded": not no_name_overlimit,
            "fixedSlabMinimumBufferBytes64BitHostModel": 192 * unique,
            "compactArenaMinimumBufferBytes64BitHostModel": 72 * unique + total_name_bytes,
            "estimatesIncludeAllocatorOrRuntimeCosts": False,
            "capacityDecisionAuthorized": False,
        },
        "provenance": {"inputOriginAuthenticated": False,
                       "fullRealSourceCensusProven": False,
                       "sourceEpochIndependentlyProven": False,
                       "classGcVmEpochProven": False,
                       "nativeV2TransportImplemented": False,
                       "R03Accepted": False,
                       "ReadyForHumanReviewGate": False},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="write JSON here; otherwise stdout")
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > MAX_INPUT_BYTES:
            reject("input exceeds 16 MiB limit")
        raw = args.input.read_bytes()
        result = analyze(load_bytes(raw), hashlib.sha256(raw).hexdigest())
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
    except (OSError, CensusError) as ex:
        print(f"CensusRejected: {ex}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
