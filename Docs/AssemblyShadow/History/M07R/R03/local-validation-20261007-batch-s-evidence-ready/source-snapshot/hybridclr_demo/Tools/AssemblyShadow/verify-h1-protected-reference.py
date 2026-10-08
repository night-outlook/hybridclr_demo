#!/usr/bin/env python3
"""Authenticate the protected profile-1 H1 reference family before rebuilding evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from shadow_tools import require

REFERENCE_DEMO_HEAD = "88508b59b7c4ef8c5023cbbe655d43ebfcf5304c"
REFERENCE_SOURCE_ANCHOR = "f1c923cbaa814e1b63f3c5b9f8303c90616de726"
REFERENCE_REVISIONS = {
    "hybridclr": "b22fa3d92223645c32663e4a2157eaadf8ea495e",
    "hybridclrUnity": "b649c499385ea68490a0f652a98b732e060aeb89",
    "il2cppPlus": "7967b8c7043904fcae130b294defd5ce7aa897c4",
}
REFERENCE_REPOSITORIES = {
    "demo": "night-outlook/hybridclr_demo",
    "hybridclr": "night-outlook/hybridclr",
    "hybridclrUnity": "night-outlook/hybridclr_unity",
    "il2cppPlus": "night-outlook/il2cpp_plus",
}
MEASUREMENT_SOURCES = (
    "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs",
    "Assets/AssemblyShadowDemo/Bootstrap/R00ProcessMemory.cs",
    "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/R00PerformanceWitness.cs",
)
REQUIRED_REFERENCE_PRODUCERS = (
    "Assets/AssemblyShadowDemo/Editor/M07Build.cs",
    "Assets/AssemblyShadowDemo/Editor/M07StructuralResources.cs",
    "Assets/AssemblyShadowDemo/Editor/R00ControlledBuild.cs",
    "Assets/AssemblyShadowDemo/Bootstrap/ShadowPatchMetadataReservation.cs",
)
PINS = "ProjectSettings/AssemblyShadowSourcePins.json"
TARGETS = "Docs/AssemblyShadow/Handoff/source-targets.json"


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=False,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    require(result.returncode == 0, f"{root}: git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def canonical_repo(value: Path, label: str) -> Path:
    require(value.is_absolute() and not value.is_symlink() and value == value.resolve(strict=True),
            label + " must be a canonical absolute path")
    root = value.resolve(strict=True)
    require(root.is_dir(), label + " must be a directory")
    require((root / ".git").exists() or run_git(root, "rev-parse", "--is-inside-work-tree") == "true",
            label + " is not a Git worktree")
    top = Path(run_git(root, "rev-parse", "--show-toplevel")).resolve(strict=True)
    require(top == root, label + " must be the Git worktree root")
    return root


def origin_matches(root: Path, repository: str) -> None:
    origin = run_git(root, "remote", "get-url", "origin")
    allowed = {
        f"https://github.com/{repository}",
        f"https://github.com/{repository}.git",
        f"git@github.com:{repository}.git",
    }
    require(origin in allowed, f"{root}: unexpected origin {origin}")


def tracked_clean(root: Path, label: str) -> None:
    status = run_git(root, "status", "--porcelain", "--untracked-files=no")
    require(status == "", label + " has tracked working-tree changes")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def verify_reference(reference_demo: Path, hybridclr: Path, unity: Path, il2cpp: Path,
                     candidate: Path) -> dict:
    reference_demo = canonical_repo(reference_demo, "reference demo")
    hybridclr = canonical_repo(hybridclr, "reference HybridCLR")
    unity = canonical_repo(unity, "reference HybridCLR Unity")
    il2cpp = canonical_repo(il2cpp, "reference IL2CPP")
    candidate = canonical_repo(candidate, "candidate demo")

    roots = {
        "demo": reference_demo,
        "hybridclr": hybridclr,
        "hybridclrUnity": unity,
        "il2cppPlus": il2cpp,
    }
    expected_heads = {
        "demo": REFERENCE_DEMO_HEAD,
        "hybridclr": REFERENCE_REVISIONS["hybridclr"],
        "hybridclrUnity": REFERENCE_REVISIONS["hybridclrUnity"],
        "il2cppPlus": REFERENCE_REVISIONS["il2cppPlus"],
    }
    for key, root in roots.items():
        origin_matches(root, REFERENCE_REPOSITORIES[key])
        tracked_clean(root, "reference " + key)
        actual = run_git(root, "rev-parse", "HEAD")
        require(actual == expected_heads[key], f"reference {key} HEAD differs: {actual}")

    origin_matches(candidate, REFERENCE_REPOSITORIES["demo"])
    tracked_clean(candidate, "candidate demo")

    pins_path = reference_demo / PINS
    require(pins_path.is_file() and not pins_path.is_symlink(), "reference source pins are missing")
    pins = read_json(pins_path)
    require(pins.get("demo", {}).get("revision") == REFERENCE_SOURCE_ANCHOR,
            "reference demo source anchor differs")
    for key, revision in REFERENCE_REVISIONS.items():
        row = pins.get(key)
        require(type(row) is dict and row.get("revision") == revision,
                "reference source pin differs: " + key)

    candidate_targets = read_json(candidate / TARGETS)
    candidate_pins = read_json(candidate / PINS)
    target = candidate_targets.get("demoTargets", {}).get("candidate")
    require(type(target) is dict, "candidate source target is missing")
    candidate_anchor = target.get("codeCommit", "")
    require(candidate_pins.get("demo", {}).get("revision") == candidate_anchor,
            "candidate source pin/target differs")
    require(run_git(candidate, "merge-base", "--is-ancestor", candidate_anchor, "HEAD") == "",
            "candidate source anchor is not an ancestor of checkout")

    producer_hashes = {}
    for relative in REQUIRED_REFERENCE_PRODUCERS:
        path = reference_demo / relative
        require(path.is_file() and not path.is_symlink(), "reference producer missing: " + relative)
        producer_hashes[relative] = sha256(path)

    reservation = (reference_demo / "Assets/AssemblyShadowDemo/Bootstrap/ShadowPatchMetadataReservation.cs").read_text()
    require("nativeBudgetCapabilityVersion == 1" in reservation and
            "Require(profileVersion == 1" in reservation and
            "ShadowPatchMetadataEncodingProfile2" not in reservation,
            "protected reference no longer exposes the expected profile-1 reservation contract")

    measurements = {}
    for relative in MEASUREMENT_SOURCES:
        a = reference_demo / relative
        b = candidate / relative
        require(a.is_file() and b.is_file() and not a.is_symlink() and not b.is_symlink(),
                "measurement source missing: " + relative)
        a_hash, b_hash = sha256(a), sha256(b)
        require(a_hash == b_hash, "reference/candidate measurement source differs: " + relative)
        measurements[relative] = a_hash

    return {
        "schemaVersion": 1,
        "kind": "H1ProtectedReferenceInputs",
        "status": "ProtectedReferenceInputsVerifiedNotBuilt",
        "reference": {
            "demoHead": REFERENCE_DEMO_HEAD,
            "demoSourceAnchor": REFERENCE_SOURCE_ANCHOR,
            "runtimeHeads": REFERENCE_REVISIONS,
            "sourcePinSha256": sha256(pins_path),
            "producerHashes": producer_hashes,
        },
        "candidate": {
            "checkoutHead": run_git(candidate, "rev-parse", "HEAD"),
            "sourceAnchor": candidate_anchor,
            "sourcePinSha256": sha256(candidate / PINS),
        },
        "matchedMeasurementSources": measurements,
        "profile": 1,
        "buildsProduced": False,
        "acceptanceClaimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-demo", required=True, type=Path)
    parser.add_argument("--reference-hybridclr", required=True, type=Path)
    parser.add_argument("--reference-hybridclr-unity", required=True, type=Path)
    parser.add_argument("--reference-il2cpp-plus", required=True, type=Path)
    parser.add_argument("--candidate-demo", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = verify_reference(args.reference_demo, args.reference_hybridclr,
                              args.reference_hybridclr_unity, args.reference_il2cpp_plus,
                              args.candidate_demo)
    output = args.output
    require(output.is_absolute() and output == output.resolve() and not output.exists() and
            output.parent.is_dir() and not output.is_symlink(),
            "output must be a new canonical file in an existing directory")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
