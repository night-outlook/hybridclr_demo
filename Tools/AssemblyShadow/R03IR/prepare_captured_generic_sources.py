#!/usr/bin/env python3
"""Extend a NEW unbuilt oneuse-09 initializer project with the captured witness.

Uses the already-prepared exact source-bound initializer composite/2 DLLs and
the original AOT/IL2CPP bridge helper. Does not modify the historical oneuse07
source, root, seal or any source repository; no Unity/Player is executed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from prepare_initializer_sources import read_json, need, sha

HERE = Path(__file__).resolve().parent
NATIVE = HERE / "PlayerProject/R03CapturedGenericPhysicalProbe.cpp"
MANAGED = {
    "Assets/R03CapturedGenericAotOwner.cs":
        HERE / "PlayerProject/R03CapturedGenericAotOwner.cs",
    "Assets/R03CapturedGenericPlayer.cs":
        HERE / "PlayerProject/R03CapturedGenericPlayer.cs",
}
ABICONTRACT = "R03IR.CapturedGeneric.PhysicalAotOwner.V1"


def extend(project, config_path, receipt_dir):
    project, config_path, receipt_dir = map(Path, (project, config_path, receipt_dir))
    need(all(p.is_absolute() for p in (project, config_path, receipt_dir)),
         "Absolute isolated source paths required")
    need(project.is_dir() and not project.is_symlink() and
         (project / ".r03-isolated-project").is_file() and
         config_path.is_file() and not config_path.is_symlink() and
         not receipt_dir.exists() and not receipt_dir.is_symlink() and
         not receipt_dir.is_relative_to(project),
         "New unconsumed isolated project and unused external output required")
    manifest = project / "source-inputs.json"
    record, config = read_json(manifest), read_json(config_path)
    need(record.get("schemaVersion") == 1 and
         type(record.get("files")) is list and
         config.get("schemaVersion") == 1 and
         config.get("projectPath") == str(project) and
         config.get("sourceManifestSha256") == sha(manifest.read_bytes()) and
         config.get("featureEnabled") is True and
         config.get("diagnosticsLevel") == 2 and
         config.get("cppConfiguration") in ("Release", "Debug"),
         "Original source manifest/build profile must remain coherent")
    output = Path(config.get("outputPath", ""))
    build_receipt = Path(config.get("receiptPath", ""))
    need(output.is_absolute() and build_receipt.is_absolute() and
         not output.exists() and not build_receipt.exists(),
         "Only a fresh unbuilt project can receive the generic extension")
    require_old = {
        "Assets/R03TerminalPlayer.cs", "Assets/R03EngineFrameDispatcher.cs",
        "Assets/R03InitializerObservationPlayer.cs",
        "Assets/Editor/R03InitializerBridge.cs",
    }
    entries = {e.get("path"): e for e in record["files"]}
    need(len(entries) == len(record["files"]) and require_old.issubset(entries),
         "Exact existing R03/initializer source roster required")
    for item in require_old:
        need((project / item).is_file() and not (project / item).is_symlink() and
             sha((project / item).read_bytes()) == entries[item]["sha256"],
             "Previous named Player source must not drift: " + item)
    overlay = Path(config.get("overlayPath", ""))
    need(overlay.is_absolute() and overlay.is_file() and
         not overlay.is_symlink() and
         overlay.name == "R03InitializerCompositeOverlay.cpp" and
         sha(overlay.read_bytes()) == config.get("overlaySha256"),
         "Only previously prepared initializer composite may be extended")
    origin = overlay.read_bytes()
    prep = overlay.parent / "SOURCE_PREPARATION.json"
    need(prep.is_file() and not prep.is_symlink(),
         "Missing exact prior initializer source receipt")
    prep_record = read_json(prep)
    need(prep_record.get("result") == "PreparedSourcesOnly_NoUnityOrPlayer" and
         prep_record.get("compositeOverlaySha256") == sha(origin) and
         prep_record.get("initializerBridgeSignature") == "Bi4" and
         prep_record.get("runtimeAcceptance") is False,
         "Exact oneuse-09 initializer preextension source provenance required")
    need(NATIVE.is_file() and not NATIVE.is_symlink() and
         all(p.is_file() and not p.is_symlink() for p in MANAGED.values()),
         "All Primary physical native and managed source files must be present")
    need(b"R03_IRG_Probe" not in origin and
         b"R03_IRG_Seal" not in origin,
         "Never append duplicate native exports")
    for relative in MANAGED:
        need(relative not in entries and not (project / relative).exists(),
             "No preexisting captured-generic Player source: " + relative)
    appended = (b"\n// Source-bound physical captured generic A2 extension "
                b"(test-only, no original source mutation)\n" + NATIVE.read_bytes())
    combined = origin + appended
    need(combined.startswith(origin) and len(combined) > len(origin),
         "Original initializer composite remains an exact prefix")

    # Only new isolated scratch project files are mutated. Exclusive receipt
    # creation prevents a previous failed cycle from masquerading as fresh.
    for relative, path in MANAGED.items():
        dest = project / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as stream:
            stream.write(path.read_bytes())
        record["files"].append({
            "path": relative, "sha256": sha(dest.read_bytes()),
            "origin": {"kind": "R03PhysicalCapturedGenericA2PrimarySource",
                       "source": str(path), "runtimeAcceptance": False},
        })
    overlay.write_bytes(combined)
    manifest_bytes = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
    manifest.write_bytes(manifest_bytes)
    config["overlaySha256"] = sha(combined)
    config["sourceManifestSha256"] = sha(manifest_bytes)
    config["capturedGenericPhysicalContract"] = ABICONTRACT
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    receipt_dir.mkdir(parents=True)
    receipt = {
        "schemaVersion": 1, "kind": "R03PhysicalCapturedGenericA2SourcesV1",
        "result": "PreparedNewProjectSourceOnly_NoUnityOrPlayer",
        "project": str(project),
        "overlay": str(overlay),
        "initializerCompositeBeforeSha256": sha(origin),
        "genericNativePartSha256": sha(NATIVE.read_bytes()),
        "combinedOverlayAfterSha256": sha(combined),
        "managedSourceSha256": {name: sha(path.read_bytes())
                               for name, path in MANAGED.items()},
        "sourceManifestSha256": sha(manifest_bytes),
        "initializerBridgeKept": True,
        "unityBuildExecuted": False,
        "playerExecuted": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }
    target = receipt_dir / "SOURCE_PREPARATION.json"
    with target.open("xb") as stream:
        stream.write((json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("project", "config", "output"):
        p.add_argument("--"+key, type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(extend(args.project, args.config, args.output),
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
