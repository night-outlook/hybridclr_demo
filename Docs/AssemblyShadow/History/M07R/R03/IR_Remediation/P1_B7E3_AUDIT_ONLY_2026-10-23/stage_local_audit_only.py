#!/usr/bin/env python3
"""One-shot staging and after-verification for a historical b7e3 AUDIT-ONLY run.

Source, consumed preflight, raw batch, SDK and prior evidence remain read-only.
This never launches Unity, compiler, core batch or the successor auditor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys

BRANCH = "codex/assembly-shadow-r01b-h1"
EXECUTION_PINS = {
    "hybridclr_demo": "49c6b62d38d7668be10004ac1e5a030d74894f09",
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb",
}
HISTORICAL_AUDITOR_BLOB = "c451e0cb7794e624eabb9029db0a35ba28d14592"
RAW_RESULT_SHA256 = "f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6"
RAW_MANIFEST_SHA256 = "4b286c29a7ef36ec4377642b6009804ad532b0ae3166c186866fe74f4246130e"
ORIGINAL_AUDITOR_SHA = "2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0"
CHECKPOINT = ("Docs/AssemblyShadow/History/M07R/R03/"
              "local-validation-p1-admitted-execution-20261023-b7e3")
HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_id(raw: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(len(raw)).encode() + b"\0" + raw)
    return h.hexdigest()


def json_read(path: Path):
    pairs = {}
    def unique(items):
        value = {}
        for k, v in items:
            if k in value:
                raise ValueError("Duplicate JSON key in " + str(path) + ": " + k)
            value[k] = v
        return value
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or symlinked evidence: " + str(path))
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def require_absent(root: Path) -> None:
    if not root.is_absolute() or root.exists() or root.is_symlink() or root.resolve() != root:
        raise ValueError("Audit-only staging root already used or noncanonical: " + str(root))


def path_beneath(root: Path, rel: str) -> Path:
    val = PurePosixPath(rel)
    if (val.is_absolute() or ".." in val.parts or str(val) != rel or
            not rel or "\\" in rel):
        raise ValueError("Invalid manifest path: " + rel)
    return root / rel


def source_refs(expected, workspace):
    if expected["pins"] != EXECUTION_PINS:
        raise ValueError("Unexpected original execution tuple")
    if expected["workspace"] != str(workspace):
        raise ValueError("Workspace differs from original b7e3 source")
    if expected["preflight"] != str(Path(expected["preflight"]).resolve()):
        raise ValueError("Original preflight path is noncanonical")


def consumed_input_hashes(checkpoint: Path, original_preflight: Path):
    """Bound ORIGINAL preflight files to the immutable Git-published checkpoint."""
    manifest = checkpoint / "MANIFEST.sha256"
    rows = manifest.read_text().splitlines()
    matched = {}
    copies = json_read(checkpoint / "COPY_BINDINGS.json")
    encoded = {row["checkpoint"]: row for row in copies["encodedTextEvidence"]}
    for line in rows:
        hash_value, separator, path = line.partition("  ")
        if separator != "  " or len(hash_value) != 64:
            raise ValueError("Historical checkpoint manifest malformed")
        if not path.startswith("preflight/"):
            continue
        archive_file = path_beneath(checkpoint, path)
        if digest(archive_file) != hash_value:
            raise ValueError("Published checkpoint preflight copy changed: " + path)
        if path in encoded:
            # Local published this original UTF-8 log in a lossless JSON wrapper.
            # Verify BOTH the source bytes and the committed encoded copy.
            row = encoded[path]
            original = Path(row["source"])
            relative = str(original.relative_to(original_preflight))
            wrapped = json_read(archive_file)
            data = wrapped["text"].encode("utf-8")
            if (wrapped["kind"] != "ExactUtf8TextEvidenceEncoding" or
                    wrapped["sourcePath"] != str(original) or
                    wrapped["sourceSha256"] != row["decodedSha256"] or
                    len(data) != row["decodedBytes"] or
                    hashlib.sha256(data).hexdigest() != row["decodedSha256"]):
                raise ValueError("Encoded Local preflight copy corrupted: " + path)
            file = path_beneath(original_preflight, relative)
            if not file.is_file() or file.is_symlink() or file.read_bytes() != data:
                raise ValueError("Original decoded preflight log changed: " + relative)
            verified_hash = row["decodedSha256"]
        else:
            relative = path[len("preflight/"):]
            file = path_beneath(original_preflight, relative)
            if not file.is_file() or file.is_symlink() or digest(file) != hash_value:
                raise ValueError("Consumed original preflight changed: " + relative)
            verified_hash = hash_value
        if relative in matched:
            raise ValueError("Duplicate preflight source binding: " + relative)
        matched[relative] = verified_hash
    if len(matched) < 70:
        raise ValueError("Incomplete original preflight checkpoint bindings")
    # Extra consumed preflight files, if present, are not permitted to disappear
    # from the staging receipt; their status remains evidence, never deleted.
    full = {}
    for path in original_preflight.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink in consumed preflight tree: " + str(path))
        if path.is_file():
            full[str(path.relative_to(original_preflight))] = digest(path)
    if not set(matched).issubset(full):
        raise ValueError("Missing originally committed preflight files")
    return full


def raw_manifest_hashes(raw: Path):
    if digest(raw / "RESULT.json") != RAW_RESULT_SHA256 or digest(raw / "MANIFEST.json") != RAW_MANIFEST_SHA256:
        raise ValueError("Consumed b7e3 raw RESULT or MANIFEST diverged from immutable GitHub publication")
    manifest = json_read(raw / "MANIFEST.json")
    seen = set()
    files = 0
    bytes_count = 0
    for row in manifest["files"]:
        rel = row["path"]
        if rel in seen:
            raise ValueError("Duplicate raw file: " + rel)
        seen.add(rel)
        path = path_beneath(raw, rel)
        if (not path.is_file() or path.is_symlink() or
                path.stat().st_size != row["size"] or
                digest(path) != row["sha256"]):
            raise ValueError("Raw evidence changed: " + rel)
        files += 1
        bytes_count += row["size"]
    # Symlinks are separate legacy negative controls, never silently followed.
    current = {str(p.relative_to(raw)) for p in raw.rglob("*")
               if p.is_file() and not p.is_symlink()}
    if current != seen | {"MANIFEST.json"}:
        raise ValueError("Raw manifest has unrecorded or missing regular files")
    return {"manifestSha256": digest(raw / "MANIFEST.json"),
            "regularFiles": files, "bytes": bytes_count}


def sdk_source_hashes(sdk: Path):
    receipt = json_read(sdk / "SDK_BEFORE.json")
    if receipt["unityVersion"] != "2022.3.62f2":
        raise ValueError("Unexpected installed official SDK version")
    files = receipt["files"]
    if len(files) != 2405:
        raise ValueError("Unexpected installed SDK file count")
    bytes_count = 0
    for row in files:
        path = Path(row["path"])
        if not path.is_file() or path.stat().st_size != row["bytes"]:
            raise ValueError("SDK file missing/size changed: " + str(path))
        if row["symlink"] is not None:
            if not path.is_symlink() or os.readlink(path) != row["symlink"]:
                raise ValueError("SDK symlink changed: " + str(path))
        elif path.is_symlink():
            raise ValueError("Unexpected SDK symlink: " + str(path))
        if digest(path) != row["sha256"]:
            raise ValueError("SDK byte changed: " + str(path))
        bytes_count += row["bytes"]
    if bytes_count != 316062203:
        raise ValueError("Unexpected original installed SDK size")
    return {"snapshotSha256": digest(sdk / "SDK_BEFORE.json"),
            "files": len(files), "bytes": bytes_count}


def sdk_scratch_hashes(raw: Path, scratch: Path, expected_count: int = 1925):
    """Independently bind the retained SDK scratch copy to the raw producer."""
    if not scratch.is_dir() or scratch.is_symlink() or scratch.resolve() != scratch:
        raise ValueError("Original SDK scratch root missing or noncanonical")
    recorded = raw / "native-sdk/native-sdk-inputs.json"
    manifest = json_read(recorded)
    entries = manifest["files"]
    if not isinstance(entries, list) or len(entries) != expected_count:
        raise ValueError("Unexpected native SDK scratch manifest count")
    seen = set()
    checked = 0
    for row in entries:
        rel = row["path"]
        file = path_beneath(scratch, rel)
        if rel in seen:
            raise ValueError("Duplicate SDK scratch input: " + rel)
        seen.add(rel)
        expected_sha = row["sha256"]
        if (not isinstance(expected_sha, str) or len(expected_sha) != 64 or
                not all(c in "0123456789abcdef" for c in expected_sha)):
            raise ValueError("Malformed native SDK scratch SHA")
        if (not file.is_file() or file.is_symlink() or file.resolve() != file or
                digest(file) != expected_sha):
            raise ValueError("Native SDK scratch input changed or noncanonical: " + rel)
        checked += 1
    return {"nativeSdkInputsManifestSha256": digest(recorded),
            "checkedScratchFiles": checked,
            "checkedSource": "b7e3/native-sdk/native-sdk-inputs.json",
            "sourceSdkOrCompilerReinvoked": False}


def original_source_bindings(sdk: Path):
    inputs = json_read(sdk / "SOURCE_BINDINGS.json")
    checked = 0
    for row in inputs:
        path = Path(row["path"])
        if (not path.is_file() or path.is_symlink() or
                path.stat().st_size != row["bytes"] or
                digest(path) != row["sha256"]):
            raise ValueError("Source binding changed: " + str(path))
        checked += 1
    return {"sourceBindings": checked, "sourceReceiptSha256":
            digest(sdk / "SOURCE_BINDINGS.json")}


def snapshot(checkpoint, preflight, output, workspace):
    expected = json_read(preflight / "EXPECTED.json")
    source_refs(expected, workspace)
    if Path(expected["output"]) != output or Path(expected["preflight"]) != preflight:
        raise ValueError("Preflight/raw binding differs from original")
    if json_read(checkpoint / "LOCAL_RESULT.json")["result"] != "FAIL":
        raise ValueError("Historical Local failed state changed")
    if digest(preflight / "audit.py") != ORIGINAL_AUDITOR_SHA:
        raise ValueError("Original failed auditor changed")
    preflight_files = consumed_input_hashes(checkpoint, preflight)
    raw = raw_manifest_hashes(output)
    sdk = sdk_source_hashes(preflight)
    scratch = Path(expected["scratch"])
    if scratch.resolve() != scratch or not scratch.is_absolute():
        raise ValueError("Original SDK scratch path is noncanonical")
    sdk_scratch = sdk_scratch_hashes(output, scratch)
    source = original_source_bindings(preflight)
    return {"preflightFiles": preflight_files, "raw": raw,
            "sdk": sdk, "sdkScratch": sdk_scratch, "source": source,
            "originalB7E3LocalState": "FAIL"}


def stage(args):
    workspace = Path(args.workspace)
    preflight = Path(args.preflight)
    output = Path(args.raw)
    target = Path(args.stage)
    checkpoint = workspace / "hybridclr_demo" / CHECKPOINT
    source = HERE / "audit_historical_only.py"
    require_absent(target)
    if target in preflight.parents or preflight in target.parents:
        raise ValueError("Audit stage overlaps original consumed evidence")
    if target in output.parents or output in target.parents:
        raise ValueError("Audit stage overlaps original raw evidence")
    scratch_path = Path(json_read(preflight / "EXPECTED.json")["scratch"])
    if target in scratch_path.parents or scratch_path in target.parents:
        raise ValueError("Audit stage overlaps original SDK scratch evidence")
    if target in workspace.parents or workspace in target.parents:
        raise ValueError("Audit stage overlaps source repositories")
    if blob_id(source.read_bytes()) != HISTORICAL_AUDITOR_BLOB:
        raise ValueError("Published historical-audit source blob changed")
    before = snapshot(checkpoint, preflight, output, workspace)
    if json_read(preflight / "PREPARATION.json")["result"] != "PreparedNotExecuted":
        raise ValueError("Original preparation record differs")
    # New root created only after independent before checks; any exception
    # consumes it. NEVER retry the same or another root automatically.
    shutil.copytree(preflight, target, symlinks=False)
    (target / "ORIGINAL_B7E3_FAILED_AUDITOR.py").write_bytes(
        (target / "audit.py").read_bytes())
    (target / "audit.py").write_bytes(source.read_bytes())
    initial = {"kind": "R03P1IsolatedHistoricalAuditStage", "schemaVersion": 1,
               "status": "StagedNotExecuted", "auditMode":
               "HistoricalB7E3SourceBound_NotLiveGitAuthority",
               "sourceCommitPins": EXECUTION_PINS,
               "historicalAuditorBlob": HISTORICAL_AUDITOR_BLOB,
               "originalAuditorSha256": ORIGINAL_AUDITOR_SHA,
               "stage": str(target), "originalPreflight": str(preflight),
               "originalRaw": str(output),
               "originalSdkScratch": str(scratch_path), "originalSdkAnchor":
               json_read(preflight / "SDK_BEFORE.json")["anchor"],
               "initialSnapshot": before, "originalCoreRetried": False,
               "originalLocalResultPromoted": False,
               "auditRun": "NotRun"}
    with (target / "AUDIT_ONLY_STAGE.json").open("xb") as fh:
        fh.write((json.dumps(initial, indent=2) + "\n").encode())
    after = snapshot(checkpoint, preflight, output, workspace)
    if after != before:
        raise ValueError("Original evidence changed during audit-only staging")
    return {"result": "StagedNotExecuted", "stage": str(target),
            "historicalSourceBlob": HISTORICAL_AUDITOR_BLOB,
            "originalFileCount": len(before["preflightFiles"]),
            "rawFiles": before["raw"]["regularFiles"],
            "sdkFiles": before["sdk"]["files"],
            "sdkScratchFiles": before["sdkScratch"]["checkedScratchFiles"]}


def verify_after(args):
    workspace = Path(args.workspace)
    preflight = Path(args.preflight)
    raw = Path(args.raw)
    stage_path = Path(args.stage)
    checkpoint = workspace / "hybridclr_demo" / CHECKPOINT
    before = json_read(stage_path / "AUDIT_ONLY_STAGE.json")
    assert before["kind"] == "R03P1IsolatedHistoricalAuditStage"
    if before["initialSnapshot"]["originalB7E3LocalState"] != "FAIL":
        raise ValueError("Original b7e3 failure state was altered")
    assert blob_id((stage_path / "audit.py").read_bytes()) == HISTORICAL_AUDITOR_BLOB
    current = snapshot(checkpoint, preflight, raw, workspace)
    if current != before["initialSnapshot"]:
        raise ValueError("Consumed original source/sdk/evidence changed since stage")
    outcome = {"kind": "R03P1IsolatedAuditAfterPreservation", "result": "Preserved",
               "originalB7E3LocalResult": "FAIL",
               "originalRequiredAuditorReclassified": False,
               "sdkRawSourcePreflightUntouched": True,
               "preflightCount": len(current["preflightFiles"]),
               "rawFiles": current["raw"]["regularFiles"],
               "sdkFiles": current["sdk"]["files"],
               "sdkScratchFiles": current["sdkScratch"]["checkedScratchFiles"],
               "newSdkOrCoreRun": False}
    with (stage_path / "AUDIT_ONLY_AFTER.json").open("xb") as fh:
        fh.write((json.dumps(outcome, indent=2) + "\n").encode())
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--verify-after", action="store_true")
    opts = parser.parse_args()
    try:
        result = verify_after(opts) if opts.verify_after else stage(opts)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, AssertionError, OSError, KeyError) as exc:
        print("AUDIT_ONLY_FAIL_CLOSED: " + repr(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
