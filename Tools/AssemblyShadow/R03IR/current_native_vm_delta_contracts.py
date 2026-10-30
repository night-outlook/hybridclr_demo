#!/usr/bin/env python3
"""All 43 changed current-native VM bytes vs legacy focused-native pin, SOURCE ONLY.

No Unity, IL2CPP, compiler or Player execution. The exact native source
checkout is immutable, and the manifest is a review inventory, not a claim
that all listed files are linked into a particular Player.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "current_native_vm_delta.json"
MANIFEST_BLOB = "5a08fd5248f5cc915dd04c3560b2fbf4c21ae471"
LEGACY_NATIVE = "74dbdbea80d83923863303bd2b2c0a87f36541b1"
CURRENT_NATIVE = "6510aed7cab67e9fc70b13ae22a115ad9819193b"
EXPECTED_VM_NAMES = (
    "Assembly.cpp",
    "Assembly.h",
    "AssemblyShadow.cpp",
    "AssemblyShadow.h",
    "AssemblyShadowAdmittedExecutionDiagnosticsSource.inl",
    "AssemblyShadowBoundedExecutionEmptyLive.h",
    "AssemblyShadowBoundedExecutionEmptyLiveSource.inl",
    "AssemblyShadowBoundedFirstUseCapture.h",
    "AssemblyShadowBoundedGeneralComposer.h",
    "AssemblyShadowBoundedGeneralLive.h",
    "AssemblyShadowBoundedGeneralLiveSource.inl",
    "AssemblyShadowBoundedOrdinaryClasses.h",
    "AssemblyShadowBoundedPhysicalAssemblies.h",
    "AssemblyShadowBoundedTransactionInventory.h",
    "AssemblyShadowBoundedTransactionStatus.h",
    "AssemblyShadowDiagnosticWriter.h",
    "AssemblyShadowExecutionRegistrationWitness.h",
    "AssemblyShadowExecutionRegistryPublisher.h",
    "AssemblyShadowExecutionRegistryRevision.h",
    "AssemblyShadowFrozenExecutionCapture.h",
    "AssemblyShadowFrozenExecutionRecord.h",
    "AssemblyShadowFrozenGeneralCapture.h",
    "AssemblyShadowFrozenR02Capture.h",
    "AssemblyShadowFrozenR02Serializer.h",
    "AssemblyShadowMetadataLifetime.h",
    "AssemblyShadowObservedTypeShape.h",
    "AssemblyShadowObservedTypeShapeCensus.h",
    "AssemblyShadowObservedTypeShapeJson.h",
    "AssemblyShadowObservedTypeShapeJsonLiveSource.inl",
    "AssemblyShadowObservedTypeShapeLiveSource.inl",
    "AssemblyShadowOpaqueExecutionInventory.h",
    "AssemblyShadowOpaqueExecutionInventorySource.inl",
    "AssemblyShadowOwnedPhysicalLiveJsonSource.inl",
    "AssemblyShadowOwnedPhysicalNames.h",
    "AssemblyShadowOwnedPhysicalNamesJson.h",
    "AssemblyShadowOwnedPhysicalNamesSource.inl",
    "AssemblyShadowPhysicalMembership.h",
    "AssemblyShadowPhysicalMembershipSource.inl",
    "AssemblyShadowR02Diagnostics.h",
    "AssemblyShadowR02Snapshot.h",
    "AssemblyShadowVisibility.cpp",
    "AssemblyShadowVisibility.h",
    "Runtime.cpp",
)
KEYS = {"path", "gitBlob", "baselineDelta", "diffChanges"}


class SourceDeltaError(ValueError):
    pass


def require(ok, why):
    if not ok:
        raise SourceDeltaError(why)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def typed_path(relative: str) -> str:
    require(isinstance(relative, str) and relative.startswith("libil2cpp/vm/"),
            "VM-only relative path required")
    require("\\" not in relative and ".." not in PurePosixPath(relative).parts and
            not PurePosixPath(relative).is_absolute() and
            str(PurePosixPath(relative)) == relative,
            "Canonical non-traversal VM path")
    return relative


def require_source(root: Path, row: dict) -> str:
    rel = typed_path(row["path"])
    f = root / rel
    require(f.is_file() and not f.is_symlink() and f.resolve() == f,
            "Source must be a regular, physically canonical file: " + rel)
    actual = git_blob(f.read_bytes())
    require(actual == row["gitBlob"], "Source Git blob changed: " + rel)
    return actual


def validate(cfg: dict, root: Path, *, check_native_commit: bool = True) -> dict:
    require(root.is_absolute() and root.is_dir() and not root.is_symlink()
            and root.resolve() == root, "Native checkout must be canonical")
    require(cfg["schemaVersion"] == 1 and
            cfg["kind"] == "R03IR02PinnedCurrentNativeVmDelta" and
            cfg["branch"] == "codex/assembly-shadow-r01b-h1" and
            cfg["baselineNativeCommit"] == LEGACY_NATIVE and
            cfg["candidateNativeCommit"] == CURRENT_NATIVE,
            "Immutable legacy/current native source authority")
    require(type(cfg["files"]) is list and len(cfg["files"]) == len(EXPECTED_VM_NAMES) == 43,
            "Exactly 43 changed production-facing VM paths")
    require(tuple(row["path"].replace("libil2cpp/vm/", "") for row in cfg["files"])
            == EXPECTED_VM_NAMES, "Ordered, complete canonical VM delta path identity")
    compare = cfg["comparison"]
    require(compare == {"aheadBy":157, "behindBy":0, "totalFilesChanged":128,
                        "vmFilesChanged":43, "diagnosticToolFilesChanged":60,
                        "workflowFilesChanged":25}, "Fixed Git history delta cardinality")
    require(cfg["acceptance"] == {"actualUnityPlayerRun":False,
             "nativeCompilerReexecuted":False,
             "allChangedVmFilesSemanticallyReviewed":False,
             "allChangedVmFilesIncludedInPlayerBinary":False,
             "IRR0302Closed":False, "R03Accepted":False,
             "ReadyForHumanReviewGate":False}, "Source-only non-acceptance fields required")
    if check_native_commit:
        run = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        require(run.stdout.strip() == CURRENT_NATIVE, "Wrong native Git checkout HEAD")
    seen = set()
    for i, row in enumerate(cfg["files"]):
        require(type(row) is dict and set(row) == KEYS, "Exact VM source-row schema")
        require(row["path"] not in seen, "Duplicate source-row path")
        seen.add(row["path"])
        require(row["baselineDelta"] in ("modified", "added") and
                type(row["diffChanges"]) is int and row["diffChanges"] > 0 and
                type(row["gitBlob"]) is str and len(row["gitBlob"]) == 40 and
                all(c in "0123456789abcdef" for c in row["gitBlob"]),
                "Source change receipt invalid at row " + str(i))
        require_source(root, row)
    counts = {t: sum(x["baselineDelta"] == t for x in cfg["files"])
              for t in ("modified", "added")}
    require(counts == {"modified": 9, "added": 34},
            "Original delta status distribution mismatch")
    return {"result": "PassedCurrentNativeVmSourceDeltaOnly",
            "baseNativeCommit": LEGACY_NATIVE, "currentNativeCommit": CURRENT_NATIVE,
            "changedVmFileCount":43, "modified":9, "added":34,
            "officialUnitySdkCompilation":"NotRun",
            "linkedPlayerInputCoverage":"NotProven",
            "independentSemanticReview":"NotRun",
            "runtimeAcceptance":False, "R03Accepted":False}


class CurrentVmDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.native = cls.NATIVE

    def check(self, cfg=None):
        return validate(self.cfg if cfg is None else cfg, self.native)

    def test_01_pinned_manifest_blob(self):
        self.assertEqual(git_blob(MANIFEST.read_bytes()), MANIFEST_BLOB)

    def test_02_path_roster_and_source_schema(self):
        self.assertEqual(len(EXPECTED_VM_NAMES), 43)
        self.assertEqual(len(set(EXPECTED_VM_NAMES)), 43)
        self.assertEqual(len(self.cfg["files"]), 43)
        self.assertEqual(self.cfg["files"][0]["path"], "libil2cpp/vm/Assembly.cpp")
        self.assertEqual(self.cfg["files"][-1]["path"], "libil2cpp/vm/Runtime.cpp")

    def test_03_all_43_genuine_native_checkout_sources_match(self):
        x = self.check()
        self.assertEqual(x["result"], "PassedCurrentNativeVmSourceDeltaOnly")
        self.assertEqual(x["changedVmFileCount"], 43)
        self.assertFalse(x["runtimeAcceptance"])

    def test_04_mutated_blob_is_refused(self):
        other = copy.deepcopy(self.cfg)
        other["files"][3]["gitBlob"] = "0" * 40
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_05_dropped_source_is_refused(self):
        other = copy.deepcopy(self.cfg)
        other["files"].pop()
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_06_duplicate_vm_source_is_refused(self):
        other = copy.deepcopy(self.cfg)
        other["files"][1] = copy.deepcopy(other["files"][0])
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_07_malformed_or_extra_schema_fields_refused(self):
        other = copy.deepcopy(self.cfg)
        other["files"][0]["fakePermission"] = True
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_08_changed_native_commit_refused(self):
        other = copy.deepcopy(self.cfg)
        other["candidateNativeCommit"] = LEGACY_NATIVE
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_09_claimed_compilation_or_acceptance_refused(self):
        for flag in ("actualUnityPlayerRun", "nativeCompilerReexecuted",
                     "IRR0302Closed", "R03Accepted", "allChangedVmFilesIncludedInPlayerBinary"):
            other = copy.deepcopy(self.cfg)
            other["acceptance"][flag] = True
            with self.subTest(flag=flag), self.assertRaises(SourceDeltaError):
                self.check(other)

    def test_10_changed_delta_cardinality_refused(self):
        other = copy.deepcopy(self.cfg)
        other["comparison"]["vmFilesChanged"] = 41
        with self.assertRaises(SourceDeltaError):
            self.check(other)

    def test_11_vm_paths_must_be_canonical_and_unaliased(self):
        for name in ("libil2cpp/vm/../Runtime.cpp", "libil2cpp/vm/../../escape",
                     "libil2cpp/vm/../vm/Foo.h", "libil2cpp/vm/\\Foo.h"):
            with self.subTest(name=name), self.assertRaises(SourceDeltaError):
                typed_path(name)

    def test_12_actual_key_native_source_blobs_match(self):
        by_name = {x["path"]: x["gitBlob"] for x in self.cfg["files"]}
        for name, pin in (
            ("AssemblyShadow.cpp", "57cf47f964a83973df8296955ccf856b105c595f"),
            ("AssemblyShadow.h", "68e78fe6250e3bd1028641d9513eb7d14158e8da"),
            ("Runtime.cpp", "96b914fbeb31c69d649e4076a802de0b6418daa8"),
        ):
            with self.subTest(name=name):
                self.assertEqual(by_name["libil2cpp/vm/" + name], pin)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native", required=True, help="Exact read-only native checkout")
    opt = p.parse_args()
    CurrentVmDeltaTests.NATIVE = Path(opt.native)
    unittest.main(argv=["current-native-vm-delta"], verbosity=2)


if __name__ == "__main__":
    main()
