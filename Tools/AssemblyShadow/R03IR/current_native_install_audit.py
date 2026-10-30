#!/usr/bin/env python3
"""Read-only source-to-installed-native VM parity after three real R03 builds.

Verifies exactly the 43 changed source VM file bytes in every installed Unity
native tree, plus the actual R03 build/source tuple. This is NOT proof every
file was compiled, linked or executed, and is NOT R03 product acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "R03"))
import current_native_vm_delta_contracts as delta
import current_native_source_gate as candidate
from batch_contract import loads, sha
from build_provenance import canonical_path, inventory_entries, NATIVE_RELATIVE

ROLES = {
    "candidate-release": ("Release", True, 2),
    "candidate-debug": ("Debug", True, 2),
    "candidate-off": ("Release", False, 0),
}


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def vm_installed_parity(source_root: Path, native_root: Path, rows: list,
                        before: dict, after: dict) -> list[dict]:
    """Compare each native checkout blob with the *actual* installed file."""
    found = set()
    observed = []
    for row in rows:
        src = delta.typed_path(row["path"])
        check(src not in found, "Duplicate changed VM source: " + src)
        found.add(src)
        rel = str(PurePosixPath(src).relative_to("libil2cpp"))
        source = canonical_path(source_root / src, directory=False)
        target = canonical_path(native_root / rel, directory=False)
        data = source.read_bytes()
        git_blob = delta.git_blob(data)
        source_sha = hashlib.sha256(data).hexdigest()
        check(git_blob == row["gitBlob"], "Original current checkout source changed: " + src)
        check(sha(target) == source_sha, "Installed VM bytes not equal current source: " + rel)
        check(rel in before and rel in after and
              before[rel]["sha256"] == source_sha and
              after[rel]["sha256"] == source_sha and
              before[rel]["size"] == after[rel]["size"] == len(data),
              "Build-v2 before/after installed VM inventories do not bind: " + rel)
        observed.append({"source": src, "installed": rel, "size": len(data),
                         "sourceGitBlob": git_blob, "sha256": source_sha})
    check(len(observed) == len(rows), "Changed native source coverage missing")
    return observed


def verify_role(workspace: Path, batch: Path, demo_commit: str,
                manifest: dict, name: str) -> dict:
    role = ROLES[name]
    project = canonical_path(batch / "projects" / name, directory=True)
    receipt_path = canonical_path(batch / "builds" / name /
                                  "build-receipt.json", directory=False)
    receipt = loads(receipt_path.read_text(encoding="utf-8"))
    config_path = canonical_path(batch / "builds" / name /
                                 "config.json", directory=False)
    config = loads(config_path.read_text(encoding="utf-8"))
    check(type(receipt) is dict and receipt.get("kind") == "R03IsolatedPlayerBuild"
          and receipt.get("schemaVersion") == 2 and receipt.get("result") == "Passed"
          and receipt.get("errors") == 0, "Actual successful R03 build-v2 required: " + name)
    check(config["featureEnabled"] is role[1] and receipt["featureEnabled"] is role[1]
          and receipt["cppConfiguration"] == config["cppConfiguration"] == role[0]
          and receipt["diagnosticsLevel"] == config["diagnosticsLevel"] == role[2],
          "Actual Release/Debug/OFF build role mismatch: " + name)
    check(receipt.get("sourceManifestSha256") == config.get("sourceManifestSha256"),
          "Build source manifest/config mismatch: " + name)
    check(receipt.get("unityVersion") == "2022.3.62f2" and
          receipt.get("target") == "StandaloneOSX" and
          receipt.get("architecture") == "arm64",
          "Build Unity/IL2CPP platform identity mismatch: " + name)
    project_pins = loads((project / "ProjectSettings/AssemblyShadowSourcePins.json").read_text())
    expected = {"hybridclr": candidate.CURRENT["hybridclr"],
                "hybridclrUnity": candidate.CURRENT["hybridclr_unity"],
                "il2cppPlus": candidate.CURRENT["il2cpp_plus"],
                "demo": demo_commit}
    for field, sha40 in expected.items():
        row = project_pins.get(field)
        check(type(row) is dict and row.get("revision") == sha40 and
              row.get("url") == "https://github.com/night-outlook/" + (
                  "hybridclr_unity" if field == "hybridclrUnity" else
                  "il2cpp_plus" if field == "il2cppPlus" else
                  "hybridclr_demo" if field == "demo" else "hybridclr") + ".git",
              "Actual project source pin mismatch: " + name + ":" + field)
    installed = canonical_path(Path(receipt["installedNativeRoot"]), directory=True)
    check(installed == project / NATIVE_RELATIVE,
          "Actual installed native root mismatches produced role: " + name)
    before = inventory_entries(receipt["installedBefore"])
    after = inventory_entries(receipt["installedAfter"])
    rows = vm_installed_parity(workspace / "il2cpp_plus", installed,
                               manifest["files"], before, after)
    check(len(rows) == 43, "Forty-three changed VM files per role required")
    return {"role": name, "result": "PassedPhysicalInstalledCurrentNativeSourceParity",
            "buildReceiptSha256": sha(receipt_path),
            "projectSourcePinsSha256": sha(project / "ProjectSettings/AssemblyShadowSourcePins.json"),
            "installedNativeRoot": str(installed),
            "changedVmFiles": len(rows), "installedFileBytes": sum(x["size"] for x in rows),
            "sources": rows, "linkedPlayerInclusion": "NotProvenBySourceParity",
            "generatedCppFullInclusion": "NotProvenBySourceParity",
            "runtimeAcceptance": False, "R03Accepted": False}


def audit(workspace: Path, batch: Path, demo_commit: str, output: Path) -> dict:
    check(re.fullmatch("[0-9a-f]{40}", demo_commit) is not None,
          "Exact demo handoff commit required")
    for p in (workspace, batch):
        canonical_path(p, directory=True)
    check(not output.exists() and output.is_absolute() and
          output.resolve(strict=False) == output and not output.is_symlink() and
          output.parent.is_dir() and not output.is_relative_to(workspace) and
          not output.is_relative_to(batch), "Unused external report path required")
    source_native = canonical_path(workspace / "il2cpp_plus", directory=True)
    manifest = loads(delta.MANIFEST.read_text(encoding="utf-8"))
    source_result = delta.validate(manifest, source_native)
    check(source_result["changedVmFileCount"] == 43, "Source VM inventory not admitted")
    batch_result = loads((batch / "LOCAL_BATCH_RESULT.json").read_text(encoding="utf-8"))
    check(batch_result.get("result") == "FocusedEvidenceReadyForPrimaryReview" and
          batch_result.get("sealStatus") == "Passed" and
          batch_result.get("repositories") ==
          {"hybridclr_demo": demo_commit, **candidate.CURRENT},
          "Current native batch must be sealed and source matched before parity audit")
    checks = [verify_role(workspace, batch, demo_commit, manifest, role)
              for role in ROLES]
    report = {"schemaVersion": 1, "kind": "R03IRCurrentNativeInstalledVmSourceParity",
              "result": "PassedInstalledSourceParityOnly",
              "repositories": batch_result["repositories"],
              "historicalNative": delta.LEGACY_NATIVE,
              "currentNative": delta.CURRENT_NATIVE,
              "roles": checks, "verifiedBuildRoles": len(checks),
              "changedVmFilesPerRole": 43,
              "installedVmSourcePairs": sum(len(x["sources"]) for x in checks),
              "fullNativeIncludeClosure": "NotProven",
              "generatedCppBinaryLinkage": "NotProven",
              "currentUnityPlayerExecution": "ReferencedSealedSiblingEvidence_NotExecutedHere",
              "independentReview": "NotRun",
              "runtimeAcceptance": False, "R03Accepted": False,
              "ReadyForHumanReviewGate": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True, allow_nan=False)
        file.write("\n")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", required=True, type=Path)
    ap.add_argument("--batch", required=True, type=Path)
    ap.add_argument("--demo-commit", required=True)
    ap.add_argument("--output", required=True, type=Path)
    opt = ap.parse_args()
    data = audit(opt.workspace, opt.batch, opt.demo_commit, opt.output)
    print(json.dumps({"result": data["result"],
          "roles": data["verifiedBuildRoles"],
          "sourcePairs": data["installedVmSourcePairs"],
          "runtimeAcceptance": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
