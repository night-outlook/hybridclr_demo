"""Versioned input capsule for the R01 early-activation experiment.

This is a trusted, local test-runner transport, not a signed deployment format.
Callers must run the existing current-source M07/R00 preflight first. The capsule
binds those admitted artifacts for the pre-Unity BCL reader; it grants no new
assembly, resource, or runtime compatibility permission.
"""
from __future__ import annotations
import hashlib
import io
import json
import re
import struct
from pathlib import Path
from shadow_tools import require

MAGIC = b"R01EARLY"
VERSION = 1
MAX_COUNT = 65536
MAX_STRING = 16384
MAX_CAPSULE = 16 * 1024 * 1024
MODES = ("Control", "OrdinaryFirst", "OrdinaryAfterReserve", "Oversize", "Mismatch", "Type", "Object", "Cctor", "NativeScript",
         "MetadataFailure", "InitializerFailure", "Baseline")
FIXED_IMAGE_SHA = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _hash(value, label):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value), label + ": invalid SHA-256")


def _file(path, expected_hash=None):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink() and path == path.resolve(strict=True) and path.is_file(),
            "Capsule input must be a canonical regular file: " + str(path))
    actual = digest(path)
    if expected_hash is not None:
        _hash(expected_hash, str(path))
        require(actual == expected_hash, "Capsule input changed: " + str(path))
    return {"path": str(path), "length": path.stat().st_size, "sha256": actual}


def encode(data: dict) -> bytes:
    """Encode the exact protocol consumed by R01EarlyStartup; reject ambiguity."""
    validate(data)
    out = io.BytesIO()
    out.write(MAGIC + struct.pack("<i", VERSION))
    def string(value):
        encoded = value.encode("utf-8")
        require(len(encoded) <= MAX_STRING and "\0" not in value, "Capsule string exceeds bounds or contains NUL")
        out.write(struct.pack("<i", len(encoded))); out.write(encoded)
    def strings(values):
        out.write(struct.pack("<i", len(values)))
        for value in values: string(value)
    for key in ("mode", "baselineBuildId", "runtimeAbiHash", "patchId"): string(data[key])
    strings(data["candidates"]); strings(data["stableAotNames"])
    out.write(struct.pack("<i", len(data["inputs"])))
    for row in data["inputs"]:
        string(row["name"])
        for prefix in ("dll", "pdb"):
            string(row[prefix + "Path"]); out.write(struct.pack("<q", row[prefix + "Length"])); string(row[prefix + "Sha256"])
    string(data["ordinaryPath"]); string(data["ordinarySha256"])
    out.write(struct.pack("<i", len(data["prerequisiteFiles"])))
    for row in data["prerequisiteFiles"]:
        string(row["path"]); out.write(struct.pack("<q", row["length"])); string(row["sha256"])
    result = out.getvalue()
    require(len(result) <= MAX_CAPSULE, "Capsule exceeds 16 MiB")
    return result


def decode(payload: bytes) -> dict:
    require(type(payload) is bytes and len(payload) <= MAX_CAPSULE, "Invalid capsule bytes")
    stream = io.BytesIO(payload)
    def take(count):
        b = stream.read(count)
        require(len(b) == count, "Truncated capsule")
        return b
    def integer(fmt): return struct.unpack(fmt, take(struct.calcsize(fmt)))[0]
    def count():
        value = integer("<i"); require(0 <= value <= MAX_COUNT, "Capsule count out of bounds"); return value
    def string():
        size = integer("<i"); require(0 <= size <= MAX_STRING, "Capsule string out of bounds")
        try: value = take(size).decode("utf-8", errors="strict")
        except UnicodeDecodeError as e: raise ValueError("Invalid capsule UTF-8") from e
        require("\0" not in value, "Capsule string contains NUL"); return value
    require(take(8) == MAGIC and integer("<i") == VERSION, "Unsupported early capsule")
    data = {key: string() for key in ("mode", "baselineBuildId", "runtimeAbiHash", "patchId")}
    for key in ("candidates", "stableAotNames"): data[key] = [string() for _ in range(count())]
    data["inputs"] = []
    for _ in range(count()):
        row = {"name": string()}
        for prefix in ("dll", "pdb"):
            row[prefix + "Path"] = string(); row[prefix + "Length"] = integer("<q"); row[prefix + "Sha256"] = string()
        data["inputs"].append(row)
    data["ordinaryPath"] = string(); data["ordinarySha256"] = string()
    data["prerequisiteFiles"] = [{"path": string(), "length": integer("<q"), "sha256": string()} for _ in range(count())]
    require(stream.read(1) == b"", "Trailing capsule bytes")
    validate(data)
    return data


def validate(data):
    require(data["mode"] in MODES and data["baselineBuildId"] and data["patchId"], "Invalid early mode/baseline/patch identity")
    _hash(data["runtimeAbiHash"], "runtime ABI")
    for key in ("candidates", "stableAotNames"):
        values = data[key]
        require(type(values) is list and 0 < len(values) <= MAX_COUNT and all(type(v) is str and v for v in values), "Invalid " + key)
        require(len(set(v.casefold() for v in values)) == len(values), "Duplicate " + key)
    candidates = {v.casefold() for v in data["candidates"]}
    require(not candidates.intersection(v.casefold() for v in data["stableAotNames"]), "Candidate/stable overlap")
    rows = data["inputs"]
    require(type(rows) is list and 0 < len(rows) <= MAX_COUNT, "Invalid closure count")
    require(len({r["name"].casefold() for r in rows}) == len(rows), "Duplicate closure member")
    require(all(r["name"].casefold() in candidates for r in rows), "Closure escapes candidates")
    paths = []
    for row in rows:
        for prefix in ("dll", "pdb"):
            path, size, sha = row[prefix + "Path"], row[prefix + "Length"], row[prefix + "Sha256"]
            require(type(size) is int and 0 <= size <= 0x7fffffffffffffff, "Invalid image size")
            if prefix == "pdb" and not path:
                require(size == 0 and sha == "", "Incomplete absent PDB"); continue
            require(type(path) is str and Path(path).is_absolute() and size > 0, "Invalid image path/size")
            _hash(sha, path); paths.append(path)
    require(len(paths) == len(set(paths)), "Duplicate image paths")
    ordinary = data["mode"] in ("OrdinaryFirst", "OrdinaryAfterReserve")
    if ordinary:
        require(Path(data["ordinaryPath"]).is_absolute() and data["ordinarySha256"] == FIXED_IMAGE_SHA, "Ordinary image is not the pinned M00 payload")
    else: require(data["ordinaryPath"] == data["ordinarySha256"] == "", "Unexpected ordinary payload")
    files = data["prerequisiteFiles"]
    require(type(files) is list and 0 < len(files) <= MAX_COUNT, "Missing prerequisite file binding")
    require(len({r["path"] for r in files}) == len(files), "Duplicate prerequisite path")
    for row in files:
        require(Path(row["path"]).is_absolute() and type(row["length"]) is int and 0 <= row["length"] <= 0x7fffffffffffffff, "Invalid prerequisite file")
        _hash(row["sha256"], row["path"])


def from_context(context, mode, patch_id="P03", fixture_path=None, replacement=None):
    """Materialize only after verify_inputs or failure.prepare succeeds.

    replacement is a verified failure fixture/negative substitution supplied by
    the existing failure verifier, never an arbitrary external replacement.
    """
    import m07_results as m07
    require(mode in MODES, "Unsupported early mode")
    manifest, baseline, on = context["manifest"], context["baseline"], context["on"]
    selected = context["fixtures"][patch_id]
    if mode == "InitializerFailure":
        require(replacement is not None and "initializer" in replacement, "Verified initializer fixture required")
        selected = replacement["initializer"]
    patch, patch_root = selected["patch"], selected["root"]
    data = {"mode": mode, "baselineBuildId": manifest["baselineBuildId"], "runtimeAbiHash": manifest["runtimeAbiHash"],
            "patchId": patch["patchId"], "candidates": list(manifest["candidateNames"]), "stableAotNames": list(manifest["stableAotNames"]),
            "inputs": [], "ordinaryPath": "", "ordinarySha256": "", "prerequisiteFiles": []}
    by_name = {row["name"]: row for row in patch["closure"]}
    for name in patch["loadOrder"]:
        row = by_name[name]
        dll = _file(patch_root / row["dll"], row["sha256"])
        if mode == "MetadataFailure" and row["name"] == "AssemblyA.Contracts":
            require(replacement is not None and "negative" in replacement, "Verified Q04 negative input required")
            negative = replacement["negative"]["data"]
            dll = _file(negative["outputPath"], negative["outputSha256"])
        pdb = _file(patch_root / row["pdb"], row["pdbSha256"]) if row.get("pdb") else {"path": "", "length": 0, "sha256": ""}
        data["inputs"].append({"name": row["name"], **{prefix + suffix: item[key] for prefix, item in (("dll", dll), ("pdb", pdb)) for suffix, key in (("Path", "path"), ("Length", "length"), ("Sha256", "sha256"))}})
    if mode in ("OrdinaryFirst", "OrdinaryAfterReserve"):
        snapshot_root = Path(on["player"]["inputSnapshot"])
        m07.prior._reflection_snapshot(snapshot_root, on["snapshot"], on["path"], require_linked=True)
        ordinary = _file(snapshot_root / "ReflectionBindings/Images" / (FIXED_IMAGE_SHA + ".dll.bytes"), FIXED_IMAGE_SHA)
        data["ordinaryPath"], data["ordinarySha256"] = ordinary["path"], ordinary["sha256"]
    paths = {Path(manifest["baselineManifestPath"]), Path(selected["path"]), Path(on["path"])}
    if fixture_path is not None: paths.add(Path(fixture_path))
    resources = Path(manifest["baselineManifestPath"]).parent / baseline["resourceBaselinePath"]
    resource_receipt = resources / "resource-build-receipt.json"
    paths.add(resource_receipt)
    catalog = json.loads(resource_receipt.read_text(encoding="utf-8-sig"))
    paths.update(resources / catalog["bundleDirectory"] / row["name"] for row in catalog["bundles"])
    if not patch["dllOnly"]:
        resource_root = Path(selected["fixture"]["replacementResourcePath"])
        paths.update(p for p in resource_root.rglob("*") if p.is_file())
    data["prerequisiteFiles"] = [_file(path) for path in sorted(paths)]
    validate(data)
    return data


def write_capsule(path, data):
    path = Path(path)
    payload = encode(data)
    with path.open("xb") as stream: stream.write(payload)
    return {"schemaVersion": 1, "kind": "R01EarlyStartupCapsuleReceipt", "path": str(path.resolve()),
            "sha256": hashlib.sha256(payload).hexdigest(), "length": len(payload), "data": data}
