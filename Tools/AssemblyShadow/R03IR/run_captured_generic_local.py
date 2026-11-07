#!/usr/bin/env python3
"""R03 IR-R03-02 oneuse-08: exact-source 1-build/3-real-Player Local batch.

Only runnable after a NEW explicit Primary WEB_TO_LOCAL authorizes the exact
pushed SHA, verified dual-OS source tests, fresh Mac volume/Unity/SDK/original-S
admission and fresh empty output roots. This file creates NO runtime evidence
on its own and cannot grant full R03/H2 acceptance.

One real AOT IL2CPP image carries: original initializer control/failure +
physical captured generic. The earlier oneuse07 binary/output is never reused.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "R03"))

from batch_contract import loads, require, sha
from batch_evidence import finalize, write
from run_terminal_local import original_s_fixtures, build_ir_generator, prepare_ir
from run_initializer_local import (
    InitializerBatch, target_fixture, prepare_initializer, local_hosts,
    archive_audit, original_process_audit, original_binary_audit,
    init_player, check_git_source, MODE_SHA)
from prepare_captured_generic_sources import extend as extend_captured
from verify_captured_generic_native import inspect as verify_captured
from run_current_native_validation_cycle import (
    validate_destination, validate_original, validate_sources, validate_machine)

BRANCH = "codex/assembly-shadow-r01b-h1"
OWNER = "Assembly-CSharp"
EXTRA_SOURCE_PATHS = (
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03CapturedGenericAotOwner.cs",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03CapturedGenericPlayer.cs",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03CapturedGenericPhysicalProbe.cpp",
    "Tools/AssemblyShadow/R03IR/CapturedGenericHost/CapturedGenericHost.csproj",
    "Tools/AssemblyShadow/R03IR/CapturedGenericHost/Program.cs",
    "Tools/AssemblyShadow/R03IR/prepare_captured_generic_sources.py",
    "Tools/AssemblyShadow/R03IR/run_captured_generic_local.py",
    "Tools/AssemblyShadow/R03IR/verify_captured_generic_native.py",
    "Tools/AssemblyShadow/R03IR/test_captured_generic_native_consumer.py",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/test_captured_generic_physical_probe.py",
)
MODES = ("initializer-control", "initializer-failure", "captured-generic")
CELLS = (
    "entry-authority", "initializer-host-contracts", "captured-host-contracts",
    "original-s-archive", "original-s-process-joins",
    "audit_s_generated_material", "audit_s_binary_linkage",
    "real-dll-fixtures", "ir-generator-build",
    "initializer-native-targets", "captured-generic-targets",
    "prepare-release", "prepare-initializer", "prepare-captured",
    "build-captured",
    "player-initializer-control", "player-initializer-failure",
    "player-captured-generic", "final-authority",
)


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def check_new_sources(repo: Path) -> dict:
    """Compare actual *Git HEAD* with working bytes for every new A2 input."""
    result = {}
    for path in EXTRA_SOURCE_PATHS:
        disk = repo / path
        require(disk.is_file() and not disk.is_symlink() and
                disk.resolve(strict=True) == disk, "Missing actual A2 source: " + path)
        shown = subprocess.run(
            ["git", "-C", str(repo), "show", "HEAD:" + path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=50)
        require(shown.returncode == 0 and
                sha_bytes(shown.stdout) == sha(disk),
                "Current exact Git A2 source drift: " + path)
        result[path] = sha(disk)
    return result


class CapturedBatch(InitializerBatch):
    """Preserve the original initializer code and evidence predicates unchanged."""

    def verify_build(self, role_id):
        receipt = super().verify_build(role_id)
        project = self.builds[role_id]["project"]
        config = self.builds[role_id]["config"]
        extension = self.root / "captured-source/SOURCE_PREPARATION.json"
        require(extension.is_file() and not extension.is_symlink(),
                "Source-bound physical generic addition receipt")
        pre = loads(extension.read_text(encoding="utf-8"))
        require(pre.get("kind") == "R03PhysicalCapturedGenericA2SourcesV1" and
                pre.get("result") == "PreparedNewProjectSourceOnly_NoUnityOrPlayer" and
                pre.get("initializerBridgeKept") is True and
                pre.get("R03Accepted") is False and
                pre.get("unityBuildExecuted") is False and
                pre.get("combinedOverlayAfterSha256") == config["overlaySha256"] and
                pre.get("sourceManifestSha256") == config["sourceManifestSha256"] and
                config.get("capturedGenericPhysicalContract") ==
                    "R03IR.CapturedGeneric.PhysicalAotOwner.V1",
                "Full source-bound initializer+physical-generic composite build")
        overlay = Path(config["overlayPath"])
        require(overlay.is_file() and
                sha(overlay) == pre["combinedOverlayAfterSha256"] and
                (project / "Assets/R03CapturedGenericAotOwner.cs").is_file() and
                (project / "Assets/R03CapturedGenericPlayer.cs").is_file(),
                "Genuine additional native and AOT C# sources retained in isolated build")
        game_assembly = Path(config["outputPath"]) / "Contents/Frameworks/GameAssembly.dylib"
        nm = subprocess.run(["nm", "-gU", str(game_assembly)],
                            capture_output=True, text=True, timeout=90)
        for export in ("_R03_IRG_Open", "_R03_IRG_Probe",
                       "_R03_IRG_AttemptRuntimeInvoke", "_R03_IRG_Seal"):
            require(nm.returncode == 0 and
                    nm.stdout.count(export) == 1,
                    "Actual linked native physical captured generic AOT export: " + export)
        require(not receipt.get("initializerBridgeLinkedRuntimeObserved", True) and
                receipt.get("initializerBridgeSignature") == "Bi4",
                "Keep original real Bi4 bridge proof scope unchanged")
        return receipt


def captured_hosts(batch):
    """Actual host compilation; never a fake native Player/acceptance result."""
    results = {}
    for directory, pattern in (
        ("NativeDiagnostics", "test_captured_generic_physical_probe.py"),
        (".", "test_captured_generic_native_consumer.py"),
    ):
        root = HERE if directory == "." else HERE / directory
        results[pattern] = batch.command([
            sys.executable, "-B", "-m", "unittest", "discover",
            "-s", str(root), "-p", pattern, "-v"], 600)
    obj = batch.root / "obj/captured-owner-host"
    binpath = batch.root / "bin/captured-owner-host"
    src = HERE / "CapturedGenericHost/CapturedGenericHost.csproj"
    results["owner-build"] = batch.command([
        "dotnet", "build", str(src), "-c", "Release", "-v", "minimal",
        "-p:PackageRoot=" + str(batch.workspace / "hybridclr_unity"),
        "-p:BaseIntermediateOutputPath=" + str(obj) + "/",
        "-p:OutputPath=" + str(binpath) + "/",
        "--disable-build-servers", "-p:UseSharedCompilation=false",
        "-nodeReuse:false"], 500)
    dll = binpath / "R03CapturedGenericHost.dll"
    dest = batch.root / "host/captured-owner"
    require(dll.is_file() and not dest.exists(), "Unreused CLR host tool")
    results["owner-runtime"] = batch.command([
        "dotnet", str(dll), "--emit-and-verify", str(dest)], 120)
    receipt = loads((dest / "HOST_RESULT.json").read_text(encoding="utf-8"))
    require(receipt.get("kind") == "R03CapturedGenericOwnerHostV1" and
            receipt.get("result") ==
            "PassedCLRPhysicalOwnerStructureAndBodies_NotUnity" and
            receipt.get("nativeGuardExecuted") is False and
            receipt.get("capturedBaselineFailure15Observed") is False,
            "Only real CLR structural prerequisite, never native proof")
    results["owner-strict-source"] = batch.command([
        sys.executable, "-B", str(HERE / "verify_captured_generic_host.py"),
        "--receipt", str(dest / "HOST_RESULT.json"),
        "--methods", str(dest / "Methods.dll"),
        "--owner-source", str(HERE / "PlayerProject/R03CapturedGenericAotOwner.cs"),
        "--native-source", str(batch.workspace /
                               "il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp"),
    ], 120)
    return {"result": "PassedHostOnlyCapturedGenericContracts_NoUnity",
            "commands": results, "runtimeAcceptance": False,
            "actualCapturedError15": "NotRun"}


def captured_target(batch):
    """Real compiled fixture; two NEW generated byte copies must match exactly."""
    exe = batch.root / "bin/player-fixtures/PlayerFixtures.dll"
    left = batch.root / "host/captured-targets"
    repeat = batch.root / "host/captured-repeat"
    require(exe.is_file() and not left.exists() and not repeat.exists(),
            "Actual fresh fixture producer with two unused destination roots")
    batch.command(["dotnet", str(exe), "--ir-terminal-producers", str(left)], 300)
    batch.command(["dotnet", str(exe), "--ir-terminal-producers", str(repeat)], 300)
    manifest = loads((left / "terminal-fixtures.json").read_text(encoding="utf-8"))
    other = loads((repeat / "terminal-fixtures.json").read_text(encoding="utf-8"))
    require(manifest == other and manifest.get("schemaVersion") == 1 and
            manifest.get("kind") == "R03IRTerminalProducerFixtures" and
            manifest.get("result") == "GeneratedAndIlVerified_NotNativeValidated" and
            manifest.get("assembly") == "Methods" and
            manifest.get("capturedBaselineArgumentExecuted") is False and
            manifest.get("commitInitializerExecuted") is False and
            manifest.get("originalSFixturesModified") is False,
            "Independent host-only terminal producer receipt")
    for kind in MODES:
        expected = left / kind / "Methods.dll"
        reproduced = repeat / kind / "Methods.dll"
        require(expected.is_file() and reproduced.is_file() and
                sha(expected) == sha(reproduced) and
                expected.read_bytes() == reproduced.read_bytes(),
                "Generated terminal fixture bytes must repeat exactly: " + kind)
    base = left / "baseline/Methods.dll"
    otherbase = repeat / "baseline/Methods.dll"
    require(base.is_file() and sha(base) == sha(otherbase),
            "Independent generated baseline used only for fixture metadata")
    rows = [x for x in manifest.get("files", [])
            if x.get("kind") == "captured-generic"]
    require(len(rows) == 1 and
            rows[0].get("path") == "captured-generic/Methods.dll" and
            rows[0].get("layoutEditorAdmission") == "PassedNeedsNativeProof" and
            rows[0].get("hasModuleInitializer") is False and
            rows[0].get("initializerThrows") is False and
            rows[0].get("emittedIlVerified") is True,
            "One real non-throwing captured-generic target")
    fixture = left / rows[0]["path"]
    require(fixture.stat().st_size == rows[0]["size"] and
            sha(fixture) == rows[0]["sha256"] and
            sha(fixture) != sha(base),
            "Actual target bytes distinct from independently generated baseline")
    batch.command(["dotnet", str(exe), "--ir-terminal-host", str(left)], 300)
    host = loads((left / "terminal-host.json").read_text(encoding="utf-8"))
    require(host.get("result") == "PassedHostBodiesOnly" and
            host.get("capturedBaselineArgumentExecuted") is False and
            host.get("postPoisonEntryExecuted") is False,
            "Actual positive CLR side effects; not error15 runtime evidence")
    batch.captured_dll = fixture
    batch.captured_manifest = left / "terminal-fixtures.json"
    batch.captured_manifest_sha = sha(batch.captured_manifest)
    return {
        "kind": "R03CapturedPhysicalTargetProducerV1",
        "result": "PassedRepeatableCompiledFixtureAndClrBodies_NoUnity",
        "sha256": sha(fixture), "mvid": rows[0]["mvid"],
        "size": fixture.stat().st_size, "sourceReceiptSha256": batch.captured_manifest_sha,
        "originalSRegeneratedOrReplaced": False, "nativeGuardExecuted": False,
        "runtimeAcceptance": False,
    }


def prepare_captured(batch, role):
    state = batch.builds[role["id"]]
    config = state["root"] / "config.json"
    receipt = extend_captured(state["project"], config,
                              batch.root / "captured-source")
    state["config"] = loads(config.read_text(encoding="utf-8"))
    require(receipt.get("combinedOverlayAfterSha256") ==
            state["config"]["overlaySha256"] and
            receipt.get("sourceManifestSha256") ==
            state["config"]["sourceManifestSha256"] and
            receipt.get("R03Accepted") is False,
            "Real new source appended without mutating historical initializer code")
    return receipt


def generic_player(batch):
    role = "candidate-release"
    batch.verify_build(role)
    state = batch.builds[role]
    root = batch.root / "players/IR-R03-02-captured-generic"
    root.mkdir(parents=True, exist_ok=False)
    dll = batch.captured_dll
    require(dll.is_file() and sha(batch.captured_manifest) == batch.captured_manifest_sha,
            "Original compiled captured fixture must remain unchanged")
    nonce = uuid.uuid4().hex
    request = {
        "schemaVersion": 1, "runId": nonce,
        "caseId": "IR-R03-02-captured-generic", "stimulus": "captured-generic",
        "baselineId": "R03CapturedGeneric-candidate-release",
        "dllPath": str(dll), "dllSha256": sha(dll),
    }
    write(root / "request.json", request)
    command = [str(state["executable"]), "-batchmode", "-nographics",
               "-r03IrCapturedRequest", str(root / "request.json"),
               "-r03IrCapturedOutput", str(root / "raw.json"),
               "-r03IrCapturedRunId", nonce, "-logFile", str(root / "Player.log")]
    evidence = {
        "schemaVersion": 1, "kind": "R03IRCapturedGenericActualPlayerEvidenceV1",
        "result": "Failed", "requestSha256": sha(root / "request.json"),
        "dllSha256": sha(dll), "dllProducerSha256": batch.captured_manifest_sha,
        "buildReceiptSha256": sha(state["root"] / "build-receipt.json"),
        "executableSha256": sha(state["executable"]),
        "sourceManifestSha256": sha(state["project"] / "source-inputs.json"),
        "nativeOverlaySha256": state["config"]["overlaySha256"],
        "runId": nonce, "R03Accepted": False, "H2Passed": False,
        "runtimeAcceptance": False, "nativeV2TransportImplemented": False,
    }
    try:
        launch = batch.command(command, 210)
        evidence["launchPid"] = launch["pid"]
        raw = root / "raw.json"
        require(raw.is_file() and not raw.is_symlink(),
                "Real native preopened captured generic V1 must be published")
        evidence["rawSha256"] = sha(raw)
        observed = verify_captured(
            raw, request, expected_pid=launch["pid"],
            expected_owner=OWNER, expected_fixture_sha256=sha(dll))
        require(observed["result"] == "SchemaConsistentNotRuntimeAuthenticated" and
                observed["capturedNativeError15Field"] == 15 and
                observed["nativeVMProofIndependent"] is False,
                "V1 native strict semantics require actual source/exe/PID independent joins")
        evidence["semanticRecord"] = observed
        evidence["result"] = "PassedFocusedCapturedGenericV1PlayerObservation_NotV2"
    except Exception as error:
        evidence["error"] = str(error)
        raw = root / "raw.json"
        evidence["rawPresent"] = raw.is_file() and not raw.is_symlink()
        if evidence["rawPresent"]:
            evidence["rawSha256"] = sha(raw)
        write(root / "verification.json", evidence)
        raise
    write(root / "verification.json", evidence)
    return evidence


def execute(workspace, original_s, output, unity, demo_commit):
    require(re.fullmatch(r"[0-9a-f]{40}", demo_commit) is not None,
            "Exact pushed source commit required")
    workspace, output, original_s, unity = map(
        Path, (workspace, output, original_s, unity))
    validate_destination(workspace, original_s, output)
    host_root = output.parent / (output.name + "-native-host-raw")
    require(host_root.is_absolute() and not host_root.exists() and
            host_root.parent == output.parent and
            not host_root.is_symlink(), "Unused actual native host evidence root")
    validate_original(original_s)
    validate_sources(workspace, demo_commit)
    validate_machine(unity, output)
    batch = CapturedBatch(workspace, output, unity, demo_commit, original_s)
    role = next(r for r in batch.matrix["roles"] if r["id"] == "candidate-release")
    require(role["candidate"] and role["feature"] and role["cpp"] == "Release",
            "One ON/Release build only")
    batch.cell("entry-authority", lambda: {
        "repositories": batch.authority()["repositories"],
        "previousInitializerSourceSha256": check_git_source(
            workspace / "hybridclr_demo"),
        "physicalCapturedSourceSha256": check_new_sources(
            workspace / "hybridclr_demo")})
    batch.cell("initializer-host-contracts", lambda: local_hosts(batch),
               ("entry-authority",))
    batch.cell("captured-host-contracts", lambda: captured_hosts(batch),
               ("initializer-host-contracts",))
    batch.cell("original-s-archive", lambda: archive_audit(batch),
               ("entry-authority",))
    batch.cell("original-s-process-joins", lambda: original_process_audit(batch),
               ("original-s-archive",))
    for script, expected in (
        ("audit_s_generated_material.py", "PassedIdentityAndLexicalScanOnly"),
        ("audit_s_binary_linkage.py",
         "PassedArchivedSourceRegistrationBinaryIdentity_NotFullLinkage"),
    ):
        batch.cell(script.removesuffix(".py"),
                   lambda s=script, e=expected: original_binary_audit(batch, s, e),
                   ("original-s-archive",))
    batch.cell("real-dll-fixtures", lambda: original_s_fixtures(batch),
               ("entry-authority",))
    batch.cell("ir-generator-build", lambda: build_ir_generator(batch),
               ("real-dll-fixtures",))
    batch.cell("initializer-native-targets", lambda: target_fixture(batch),
               ("ir-generator-build",))
    if hasattr(batch, "initializer_target_report"):
        batch.target_receipt_sha = sha(batch.initializer_target_report)
    batch.cell("captured-generic-targets", lambda: captured_target(batch),
               ("ir-generator-build", "captured-host-contracts"))
    batch.cell("prepare-release", lambda: prepare_ir(batch, role),
               ("initializer-native-targets", "captured-generic-targets"))
    batch.cell("prepare-initializer", lambda: prepare_initializer(batch, role),
               ("prepare-release",))
    batch.cell("prepare-captured", lambda: prepare_captured(batch, role),
               ("prepare-initializer",))
    batch.cell("build-captured", lambda: batch.build(role),
               ("prepare-captured",))
    for mode in MODE_SHA:
        batch.cell("player-" + mode, lambda m=mode: init_player(batch, m),
                   ("build-captured",))
    batch.cell("player-captured-generic", lambda: generic_player(batch),
               ("build-captured",))
    batch.cell("final-authority", lambda: {
        "repositories": batch.authority()["repositories"],
        "previousInitializerSourceSha256": check_git_source(
            workspace / "hybridclr_demo"),
        "physicalCapturedSourceSha256": check_new_sources(
            workspace / "hybridclr_demo")})
    require(tuple(row["id"] for row in batch.cells) == CELLS,
            "One fresh fixed 19-cell/one-build/three-Player roster")
    states = {row["id"]: row["result"] for row in batch.cells}
    custody = {"result": "NotRun_NativeHostFailed", "runtimeAcceptance": False}
    if hasattr(batch, "native_host_raw") and hasattr(batch, "native_host_custody"):
        from initializer_host_custody import verify_live
        try:
            custody = verify_live(batch.native_host_raw, batch.native_host_custody)
        except Exception as error:
            custody = {"result": "FailedLiveNativeHostCustodyBinding",
                       "error": str(error), "runtimeAcceptance": False}
    success = (all(status == "Passed" for status in states.values()) and
               custody["result"] ==
               "PassedFullRawHostAndArchiveBinding_NoRuntimeAcceptance")
    record = finalize(batch.root, {
        "schemaVersion": 1,
        "kind": "R03IRCapturedGenericOneUse08EvidenceBatchV1",
        "result": "FocusedCapturedGenericAndInitializerEvidenceForIndependentReview"
            if success else "ReturnRequired",
        "repositories": dict(batch.pins), "cells": batch.cells,
        "plannedFreshUnityBuilds": 1,
        "verifiedFreshUnityBuilds": int(states["build-captured"] == "Passed"),
        "plannedFreshPlayers": 3,
        "verifiedFreshPlayers": sum(states["player-" + mode] == "Passed"
                                    for mode in MODES),
        "recordedNativeHostCustody": custody,
        "nativeV2TransportImplemented": False,
        "firstRecoveryAuthenticatedV2": False,
        "wholeVmEpoch": "NotProven",
        "fullOriginalSIndependentCompilerLinkPlayerJoin": False,
        "originalRetiredEvidenceRegenerated": False,
        "capturedNativeAotOwnerPath": "TestOnly",
        "runtimeAcceptance": False, "R03Accepted": False,
        "H2Passed": False, "ReadyForHumanReviewGate": False,
        "qualificationApproved": False,
        "fullLegacyRegressionAcceptance": False,
        "pureInterpreterExpansionEnabled": False,
    })
    print(json.dumps({"kind": record["kind"], "result": record["result"],
                      "cells": states, "seal": record["sealStatus"],
                      "R03Accepted": False}, sort_keys=True), flush=True)
    return 0 if success and record["sealStatus"] == "Passed" else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "original-s", "output", "unity", "demo-commit"):
        p.add_argument("--"+name, required=True)
    args = p.parse_args()
    return execute(args.workspace, args.original_s, args.output, args.unity,
                   args.demo_commit)


if __name__ == "__main__":
    raise SystemExit(main())
