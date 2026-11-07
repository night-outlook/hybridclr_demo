#!/usr/bin/env python3
"""R03 follow-up: one fresh native initializer build and two independent Players.

An explicitly published WEB_TO_LOCAL handoff is required. This is NOT a
replay of oneuse-K and cannot grant R03, H2 or Human Review Gate acceptance.
All source/build/Player evidence stays in a new external output directory.
"""
from __future__ import annotations

import argparse
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
from build_provenance import RECEIPT_VERSION, verify_installation
from run_terminal_current import CurrentNativeBatch
from run_terminal_local import build_ir_generator, original_s_fixtures, prepare_ir
from prepare_initializer_sources import prepare as prepare_sources
from verify_initializer_observation import strict_load, verify as verify_observation
from verify_initializer_trace import inspect as inspect_native_trace
from verify_initializer_recovery import inspect as inspect_native_recovery
from initializer_host_custody import capture as capture_host, verify_live as verify_host
from run_current_native_validation_cycle import (
    validate_destination, validate_original, validate_sources, validate_machine,
)

BRANCH = "codex/assembly-shadow-r01b-h1"
# Source-authenticated actual .NET8/dnlib v2 outputs, generated twice on
# macOS and Linux at demo 7e53f193cf7453e92856ca307e628ba93a35ab03.
# Different MVIDs and bytes from the consumed __Internal v1 targets.
# This is not a real Player or acceptance attestation.
MODE_SHA = {
    "initializer-control": (
        "d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e",
        "5bb6e17a-09b9-5b29-dac2-41d3519f76f4",
    ),
    "initializer-failure": (
        "6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370",
        "f61d7325-6d38-4640-5873-37371f587b16",
    ),
}
SOURCE_PATHS = (
    "Tools/AssemblyShadow/R03/PlayerFixtures/InitializerNativeTargetFixtures.cs",
    "Tools/AssemblyShadow/R03/PlayerFixtures/PlayerFixtures.csproj",
    "Tools/AssemblyShadow/R03/PlayerFixtures/Program.cs",
    "Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerBridge.cs",
    "Tools/AssemblyShadow/R03IR/prepare_initializer_sources.py",
    "Tools/AssemblyShadow/R03IR/bridge_host_contracts.py",
    "Tools/AssemblyShadow/R03IR/BridgeHost/BridgeHost.csproj",
    "Tools/AssemblyShadow/R03IR/BridgeHost/Program.cs",
    "Tools/AssemblyShadow/R03IR/prepare_initializer_sources.py",
    "Tools/AssemblyShadow/R03IR/verify_initializer_observation.py",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerObservationPlayer.cs",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerPreparedProbe.cpp",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerObservationWriter.cpp",
    "Tools/AssemblyShadow/R03IR/run_initializer_local.py",
    "Tools/AssemblyShadow/R03IR/verify_initializer_trace.py",
    "Tools/AssemblyShadow/R03IR/verify_initializer_recovery.py",
    "Tools/AssemblyShadow/R03IR/test_initializer_recovery.py",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/InitializerHostInclude/vm/AssemblyShadow.h",
    "Tools/AssemblyShadow/R03IR/initializer_host_custody.py",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/initializer_writer_driver.cpp",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/test_initializer_writer_host.py",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/test_initializer_observer_native.py",
)


def check_git_source(repo: Path) -> dict:
    """Git HEAD bytes, not the uncommitted working tree, own every new input."""
    checked = {}
    for relative in SOURCE_PATHS:
        path = repo / relative
        require(path.is_file() and not path.is_symlink(),
                "Missing source: " + relative)
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", "HEAD:" + relative],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        require(proc.returncode == 0 and
                sha(path) == __import__("hashlib").sha256(proc.stdout).hexdigest(),
                "Current Git HEAD source bytes mismatch: " + relative)
        checked[relative] = sha(path)
    return checked


class InitializerBatch(CurrentNativeBatch):
    """Never change the historical five-Player runner or its original overlay."""
    def __init__(self, workspace, output, unity, demo_commit, original_s):
        self.original_s = Path(original_s)
        super().__init__(workspace, output, unity, demo_commit)

    def verify_build(self, role_id):
        """The original verifier hard-codes K's overlay; bind OUR composite."""
        from run_local import ROOT
        state = self.builds[role_id]
        config = state["config"]
        receipt_path = state["root"] / "build-receipt.json"
        require(receipt_path.is_file() and not receipt_path.is_symlink(),
                "Actual Unity build receipt missing")
        receipt = loads(receipt_path.read_text(encoding="utf-8"))
        require(type(receipt.get("schemaVersion")) is int and
                receipt["schemaVersion"] == RECEIPT_VERSION and
                receipt.get("result") == "Passed" and
                receipt.get("nonGeneratedCorePreserved") is True and
                type(receipt.get("errors")) is int and receipt["errors"] == 0,
                "Actual successful Unity IL2CPP BuildReport required")
        require(receipt.get("buildPipelineResult") == "Succeeded" and
                receipt.get("playerInventoryStatus") == "PresentAndInventoried",
                "Failed or un-inventoried BuildReport may not pass")
        for key in ("featureEnabled", "diagnosticsLevel", "cppConfiguration",
                    "outputPath", "projectPath", "sourceManifestSha256"):
            require(receipt.get(key) == config[key],
                    "Native build receipt/config mismatch: " + key)
        overlay = Path(config["overlayPath"])
        require(overlay.is_file() and not overlay.is_symlink() and
                overlay == self.root / "initializer-source/R03InitializerCompositeOverlay.cpp",
                "Exact new composite overlay required")
        require(receipt.get("testOverlaySha256") == config["overlaySha256"] ==
                sha(overlay) and config["featureEnabled"] is True and
                config["diagnosticsLevel"] == 2,
                "Actual new native composite overlay/ON profile must match BuildReport")
        require(receipt.get("unityVersion") == "2022.3.62f2" and
                receipt.get("target") == "StandaloneOSX" and
                receipt.get("architecture") == "arm64",
                "Exact Unity 2022.3.62f2 macOS ARM64 build required")
        project = state["project"]
        manifest_path = project / "source-inputs.json"
        require(config["sourceManifestSha256"] == sha(manifest_path),
                "Pinned managed-source manifest")
        manifest = loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            require(sha(project / entry["path"]) == entry["sha256"],
                    "Actual source/fixture file changed: " + entry["path"])
        require(config.get("initializerBridgeContract") ==
                    "R03IR.Managed2Native.Cdecl.Int32NoArgs.V1" and
                receipt.get("initializerBridgeSignature") == "Bi4" and
                receipt.get("initializerBridgeImportModule") == "__InternalDynamic" and
                receipt.get("initializerBridgeControlSha256") == MODE_SHA["initializer-control"][0] and
                receipt.get("initializerBridgeFailureSha256") == MODE_SHA["initializer-failure"][0] and
                receipt.get("initializerBridgeLinkedRuntimeObserved") is False and
                config.get("initializerBridgeControlSha256") == MODE_SHA["initializer-control"][0] and
                config.get("initializerBridgeFailureSha256") == MODE_SHA["initializer-failure"][0] and
                config.get("initializerBridgeControlMvid") == MODE_SHA["initializer-control"][1] and
                config.get("initializerBridgeFailureMvid") == MODE_SHA["initializer-failure"][1],
                "Unmodified AOT roles with one source-bound Bi4 native signature")
        generated = Path(receipt["installedNativeRoot"]) / "hybridclr/generated/MethodBridge.cpp"
        require(generated.is_file() and not generated.is_symlink() and
                len(receipt.get("initializerBridgeGeneratedSha256") or "") == 64 and
                sha(generated) == receipt["initializerBridgeGeneratedSha256"] ==
                    receipt.get("initializerBridgePostBuildSha256"),
                "Real installed post-IL2CPP generated Bi4 source identity")
        generator_source = generated.read_text(encoding="utf-8")
        require(generator_source.count('{"Bi4", __M2NF_Bi4}') == 1 and
                generator_source.count('static void __M2NF_Bi4(') == 1 and
                generator_source.count('typedef int32_t (CDECL *NativeMethod)();') == 1 and
                generator_source.count('const Managed2NativeFunctionPointerCallData hybridclr::interpreter::g_managed2NativeFunctionPointerCallStub[]') == 1,
                "Only one authentic Cdecl/int32 linked bridge source table row")
        app = Path(config["outputPath"])
        self.verify_inventory(app, receipt["playerFiles"])
        game_assembly = app / "Contents/Frameworks/GameAssembly.dylib"
        require(game_assembly.is_file() and not game_assembly.is_symlink() and
                b"Bi4\x00" in game_assembly.read_bytes(),
                "Linked native GameAssembly must contain Bi4 table identity")
        exports = subprocess.run(["nm", "-gU", str(game_assembly)],
                                 capture_output=True, text=True, timeout=80)
        require(exports.returncode == 0 and
                exports.stdout.count("_R03_IRW_BridgeStatus") == 1 and
                exports.stdout.count("_R03_IRW_OnPrepared") == 1,
                "Actual linked GameAssembly export set must include bridge probe and callback")
        state["bi4LinkedEvidence"] = {
            "kind": "R03InitializerLinkedBi4StaticEvidenceV1",
            "gameAssemblySha256": sha(game_assembly),
            "generatedMethodBridgeSha256": sha(generated),
            "exactBi4Entry": True, "genuineLinkedProbeExported": True,
            "realRuntimeProbeExecuted": False, "runtimeAcceptance": False}

        native = Path(receipt["installedNativeRoot"]) / "vm/AssemblyShadowR03Probe.cpp"
        require(native.is_file() and sha(native) == sha(overlay),
                "Real installed native overlay differs from source")
        state["nativeBinding"] = verify_installation(
            receipt, project, self.root, manifest["repositories"])
        executables = [p for p in (app / "Contents/MacOS").iterdir() if p.is_file()]
        require(len(executables) == 1, "Exactly one built Player binary")
        arch = subprocess.run(["lipo", "-archs", str(executables[0])],
                              capture_output=True, text=True, timeout=30)
        require(arch.returncode == 0 and arch.stdout.strip() == "arm64",
                "Real ARM64 executable required")
        state["executable"] = executables[0]
        return receipt


def target_fixture(batch):
    root = batch.root / "host/initializer-native-targets"
    binary = batch.root / "bin/player-fixtures/PlayerFixtures.dll"
    require(binary.is_file() and not root.exists(),
            "Fresh built target generator and unused target root required")
    batch.command(["dotnet", str(binary), "--ir-terminal-native-targets", str(root)], 300)
    receipt_path = root / "initializer-native-targets.json"
    report = loads(receipt_path.read_text(encoding="utf-8"))
    require(report.get("schemaVersion") == 1 and
            report.get("kind") == "R03IRInitializerNativeTargetFixturesV1" and
            report.get("result") == "GeneratedAndIlVerified_NotNativeValidated" and
            report.get("originalSInputReplaced") is False and
            report.get("originalFifteenModified") is False and
            report.get("expectsNativeModule") == "__InternalDynamic" and
            report.get("interpreterImportContract") ==
                "R03IR.InterpreterCurrentProcessImport.V2" and
            report.get("runtimeAcceptance") is False and
            type(report.get("targets")) is list and len(report["targets"]) == 2,
            "Deterministic native test fixture record")
    found = {}
    for row in report["targets"]:
        mode = row.get("kind")
        require(mode in MODE_SHA and mode not in found and
                row.get("path") == "native/" + mode + "/Methods.dll" and
                row.get("sha256") == MODE_SHA[mode][0] and
                row.get("mvid") == MODE_SHA[mode][1] and
                row.get("callbackBeforeInitializerOutcome") is True and
                row.get("expectedNativeModule") == "__InternalDynamic" and
                row.get("interpreterImportContract") ==
                    "R03IR.InterpreterCurrentProcessImport.V2" and
                row.get("observedInUnity") is False and
                row.get("layoutEditorAdmission") == "PassedNeedsNativeProof",
                "Exact independent initializer target identity")
        dll = root / row["path"]
        require(dll.is_file() and not dll.is_symlink() and
                sha(dll) == row["sha256"] and
                type(row.get("size")) is int and row["size"] == dll.stat().st_size,
                "New target must match the compiled fixture producer bytes")
        found[mode] = dll
    require(set(found) == set(MODE_SHA), "Both distinct initializer targets required")
    batch.initializer_targets = found
    batch.initializer_target_report = receipt_path
    return {"kind": "R03InitializerTargetsSourceBound",
            "targetSha256": {key: sha(value) for key, value in found.items()},
            "generatorReceiptSha256": sha(receipt_path),
            "nativeExecuted": False, "runtimeAcceptance": False}


def prepare_initializer(batch, role):
    state = batch.builds[role["id"]]
    config_path = state["root"] / "config.json"
    prepared = prepare_sources(state["project"], config_path,
                               batch.root / "initializer-source", batch.initializer_targets)
    state["config"] = loads(config_path.read_text(encoding="utf-8"))
    require(prepared["compositeOverlaySha256"] ==
            state["config"]["overlaySha256"] and
            prepared["managedSourceSha256"] ==
            sha(state["project"] / "Assets/R03InitializerObservationPlayer.cs") and
            prepared.get("initializerBridgeContract") ==
                "R03IR.Managed2Native.Cdecl.Int32NoArgs.V1" and
            prepared.get("initializerBridgeSignature") == "Bi4" and
            prepared.get("initializerBridgeHelperSha256") ==
                sha(state["project"] / "Assets/Editor/R03InitializerBridge.cs") and
            prepared["R03Accepted"] is False and
            prepared["unityBuildExecuted"] is False,
            "Source preparation cannot claim a Player or mutate the wrong input")
    return prepared


def local_hosts(batch):
    # Do not substitute a handful of new tests for K's ten actual native
    # host components. Both the original owner suites and the new initializer
    # compile/contracts must pass before launching any new Unity build.
    import run_current_native_host_preflight as full_native_host
    from current_native_source_gate import CURRENT
    # The actual ten-suite host output retains intentional directory symlinks.
    # Keep it as an immutable sibling, never inside batch_evidence.seal's
    # strict symlink-free regular-file traversal. Losslessly bind its bytes
    # and literal symlink identities into the product archive instead.
    output = batch.root.parent / (batch.root.name + "-native-host-raw")
    require(not output.exists() and not output.is_symlink() and
            output.parent == batch.root.parent,
            "One fresh sibling ten-host evidence root required")
    recorded = batch.command([
        sys.executable, "-B", str(HERE / "run_current_native_host_preflight.py"),
        "--workspace", str(batch.workspace),
        "--expected-demo", batch.pins["hybridclr_demo"],
        "--expected-native", CURRENT["il2cpp_plus"],
        "--output", str(output),
    ], 7200)
    report = loads((output / "RESULT.json").read_text(encoding="utf-8"))
    full_native_host.verify_current_host_report(
        report, batch.pins["hybridclr_demo"], CURRENT["il2cpp_plus"])
    captured = capture_host(output, batch.root / "host-custody")
    require(captured["result"] == "PassedFullRegularBytesAndLiteralSymlinkTargets" and
            captured["symlinkCount"] == 4,
            "Exactly four native-host negative-control symlinks preserved")
    batch.native_host_raw = output
    batch.native_host_custody = batch.root / "host-custody"
    tests = ("test_initializer_observer_native.py", "test_initializer_writer_host.py")
    receipts = {"tenCurrentNativeHost": recorded, "tenCurrentNativeHostResultSha256":
                sha(output / "RESULT.json"), "boundActualHostCustody": captured}
    for name in tests:
        receipt = batch.command([
            sys.executable, "-B", "-m", "unittest", "discover",
            "-s", str(HERE / "NativeDiagnostics"), "-p", name, "-v"], 600)
        receipts[name] = receipt
    for name in ("test_initializer_observation.py",
                 "test_initializer_source_preparation.py",
                 "test_initializer_local_orchestration.py",
                 "test_initializer_bridge_source.py",
                 "test_initializer_trace.py",
                 "test_initializer_recovery.py",
                 "test_initializer_host_custody.py"):
        receipts[name] = batch.command([
            sys.executable, "-B", "-m", "unittest", "discover",
            "-s", str(HERE), "-p", name, "-v"], 300)
    return {"result": "PassedActualHostContracts_NoUnity", "commands": receipts,
            "runtimeAcceptance": False}


def archive_audit(batch):
    output = batch.root / "original-s-provenance"
    batch.command([sys.executable, "-B", str(HERE / "audit_s_provenance.py"),
                   "--repo", str(batch.original_s),
                   "--output", str(output)], 10800)
    recorded = loads((output / "audit.json").read_text(encoding="utf-8"))
    require(recorded.get("result") == "Passed" and
            recorded.get("archiveMembers") == 15713 and
            recorded.get("cells") == 90, "Original S historical authority")
    return {"result": "PassedArchivedSIdentityOnly",
            "receiptSha256": sha(output / "audit.json"), "runtimeAcceptance": False}


def original_process_audit(batch):
    output = batch.root / "original-s-process-joins"
    batch.command([sys.executable, "-B", str(HERE / "audit_s_process_joins.py"),
                   "--original", str(batch.original_s),
                   "--audit", str(batch.root / "original-s-provenance"),
                   "--output", str(output)], 5400)
    recorded = loads((output / "process-joins.json").read_text(encoding="utf-8"))
    require(recorded.get("result") == "Passed" and
            recorded.get("totalPlayerReceipts") == 59 and
            recorded.get("originalLedgerCellsPreviouslyAuthenticated") == 90 and
            recorded.get("R03Accepted") is False,
            "Exact original 59 process joins are archived evidence, not new Players")
    return {"result": "Passed59ArchivedProcessJoinsOnly",
            "receiptSha256": sha(output / "process-joins.json"),
            "runtimeAcceptance": False}


def original_binary_audit(batch, script, expected):
    output = batch.root / (script.replace("audit_s_", "original-s-").replace(".py", "") + ".json")
    batch.command([sys.executable, "-B", str(HERE / script),
                   "--original", str(batch.original_s),
                   "--output", str(output)], 5400)
    report = loads(output.read_text(encoding="utf-8"))
    require(report.get("result") == expected and report.get("R03Accepted") is False,
            "Original S audit must be explicitly scoped: " + script)
    return {"result": expected, "receiptSha256": sha(output),
            "runtimeAcceptance": False}


def trace_report(root: Path, request: dict, pid: int | None, *,
                 complete: bool = False) -> dict:
    """Diagnostic only; no success promotion and no synthetic trace fallback."""
    path = root / "raw.json.native-trace.jsonl"
    if not path.is_file() or path.is_symlink() or type(pid) is not int or pid <= 0:
        return {"result": "UnavailableNoBoundNativeJournal",
                "traceExists": path.is_file() and not path.is_symlink(),
                "runtimeAcceptance": False, "R03Accepted": False}
    recovery_path = root / "raw.json.vm-recovery.json"
    recovery = {"result": "UnavailableNoBoundVmRecovery", "runtimeAcceptance": False}
    if recovery_path.is_file() and not recovery_path.is_symlink():
        try:
            recovery = inspect_native_recovery(
                recovery_path, request, pid, request["dllSha256"])
        except Exception as error:
            recovery = {
                "result": "RejectedVmRecovery_NotRuntimeAuthenticated",
                "error": str(error), "rawSha256": sha(recovery_path),
                "rawBytes": recovery_path.stat().st_size, "runtimeAcceptance": False}
    try:
        observed = inspect_native_trace(
            path, request, pid, request["dllSha256"], require_complete=complete)
        observed["vmRecovery"] = recovery
        if complete:
            require(recovery.get("result") ==
                    "ParsedNativeVMFirstFailure_NotRuntimeAuthenticated",
                    "Exact native VM recovery reason required alongside strict V1")
            commit_codes = observed.get("commitStatusReported")
            require(type(commit_codes) is list and len(commit_codes) == 1 and
                    recovery["stateCode"] == (6 if commit_codes[0] == 0 else 9) and
                    recovery["terminalFailureCode"] ==
                    (0 if commit_codes[0] == 0 else 19) and
                    commit_codes[0] in (0, 19),
                    "VM native recovery must agree with real Commit and terminal state")
            if request["stimulus"] == "initializer-failure":
                require("R03IR.InitializerFailure.AfterPublication.V1" in recovery["vmReason"],
                        "Real postprepared initializer sentinel must occur in first VM failure")
            else:
                require(recovery["vmReason"] == "",
                        "Healthy control must not contain an unexpected initializer failure")
        return observed
    except Exception as error:
        return {"result": "RejectedNativeJournal_NotRuntimeAuthenticated",
                "error": str(error), "vmRecovery": recovery,
                "traceSha256": sha(path), "traceBytes": path.stat().st_size,
                "runtimeAcceptance": False, "R03Accepted": False}


def init_player(batch, mode):
    role_id = "candidate-release"
    batch.verify_build(role_id)
    state = batch.builds[role_id]
    root = batch.root / "players" / ("IR-R03-02-" + mode)
    root.mkdir(parents=True, exist_ok=False)
    dll = batch.initializer_targets[mode]
    require(sha(dll) == MODE_SHA[mode][0] and
            sha(batch.initializer_target_report) == batch.target_receipt_sha,
            "Fixture and producer receipt changed before actual Player launch")
    run_id = uuid.uuid4().hex
    case_id = "IR-R03-02-" + mode
    request = {
        "schemaVersion": 1, "runId": run_id, "caseId": case_id,
        "stimulus": mode, "baselineId": "R03Initializer-" + role_id,
        "dllPath": str(dll), "dllSha256": MODE_SHA[mode][0],
    }
    write(root / "request.json", request)
    command = [str(state["executable"]), "-batchmode", "-nographics",
               "-r03IrInitializerRequest", str(root / "request.json"),
               "-r03IrInitializerOutput", str(root / "raw.json"),
               "-r03IrInitializerRunId", run_id, "-logFile", str(root / "Player.log")]
    try:
        launch = batch.command(command, 180)
    except Exception as error:
        raw_file = root / "raw.json"
        receipt_file = batch.root / "commands" / ("%04d" % batch.command_count) / "command.json"
        pid = None
        if receipt_file.is_file() and not receipt_file.is_symlink():
            receipt = loads(receipt_file.read_text(encoding="utf-8"))
            pid = receipt.get("pid")
        observed = trace_report(root, request, pid)
        write(root / "verification.json", {
            "result": "Failed", "error": str(error),
            "semanticVerifierStatus": "NotRun_CommandFailed",
            "rawPresent": raw_file.is_file() and not raw_file.is_symlink(),
            "rawSha256": sha(raw_file) if raw_file.is_file() and not raw_file.is_symlink() else None,
            "nativeDiagnostic": observed,
            "launchPidFromOwnedReceipt": pid,
            "runId": run_id, "requestSha256": sha(root / "request.json"),
            "buildReceiptSha256": sha(state["root"] / "build-receipt.json"),
            "nativeOverlaySha256": state["config"]["overlaySha256"],
            "executableSha256": sha(state["executable"]),
            "R03Accepted": False, "runtimeAcceptance": False,
        })
        raise
    raw_path = root / "raw.json"
    binding = {
        "runId": run_id, "caseId": case_id, "requestSha256": sha(root / "request.json"),
        "buildReceiptSha256": sha(state["root"] / "build-receipt.json"),
        "sourceManifestSha256": sha(state["project"] / "source-inputs.json"),
        "nativeOverlaySha256": state["config"]["overlaySha256"],
        "targetGeneratorReceiptSha256": batch.target_receipt_sha,
        "executableSha256": sha(state["executable"]), "launchPid": launch["pid"],
        "argv": command, "runtimeAcceptance": False, "R03Accepted": False,
        "H2Passed": False,
    }
    try:
        require(raw_path.is_file() and not raw_path.is_symlink(),
                "Actual fresh native diagnostic raw missing")
        binding["rawSha256"] = sha(raw_path)
        raw = strict_load(raw_path.read_bytes())
        verdict = verify_observation(raw, request, launch, sha(dll))
        diagnostic = trace_report(root, request, launch["pid"], complete=True)
        require(diagnostic.get("result") == "CompletePhaseTrace_NotRuntimeAuthenticated",
                "Real native preopened phase journal required alongside strict V1")
        binding["nativeDiagnostic"] = diagnostic
        require(verdict.get("result") == "SchemaConsistentNotRuntimeAuthenticated" and
                raw["processId"] == launch["pid"] and
                raw["runtimeAcceptance"] is False, "Native diagnostic receipt")
        binding.update(verdict)
        binding["result"] = "PassedFocusedV1PlayerObservation_NotV2"
        write(root / "verification.json", binding)
    except Exception as error:
        if "nativeDiagnostic" not in binding:
            binding["nativeDiagnostic"] = trace_report(root, request, launch["pid"])
        write(root / "verification.json", dict(binding, result="Failed",
                                               error=str(error)))
        raise
    return binding


def execute(workspace, original_s, output, unity, demo_commit):
    require(not __debug__ is False, "Optimized Python invalidates validation")
    workspace = Path(workspace)
    output = Path(output)
    original_s = Path(original_s)
    unity = Path(unity)
    validate_destination(workspace, original_s, output)
    host_root = output.parent / (output.name + "-native-host-raw")
    require(host_root.is_absolute() and not host_root.exists() and
            not host_root.is_symlink() and
            host_root.parent == output.parent and host_root != output,
            "Unused separate sibling host evidence root required before dispatch")
    validate_original(original_s)
    validate_sources(workspace, demo_commit)
    validate_machine(unity, output)
    batch = InitializerBatch(workspace, output, unity, demo_commit, original_s)
    role = next(r for r in batch.matrix["roles"] if r["id"] == "candidate-release")
    require(role["candidate"] is True and role["feature"] is True and
            role["cpp"] == "Release", "Only one new ON/Release build admitted")
    batch.cell("entry-authority", lambda: {
        "repositories": batch.authority()["repositories"],
        "initializerSourceSha256": check_git_source(workspace / "hybridclr_demo")})
    batch.cell("initializer-host-contracts", lambda: local_hosts(batch),
               ("entry-authority",))
    batch.cell("original-s-archive", lambda: archive_audit(batch),
               ("entry-authority",))
    batch.cell("original-s-process-joins", lambda: original_process_audit(batch),
               ("original-s-archive",))
    for script, expected in (
        ("audit_s_generated_material.py", "PassedIdentityAndLexicalScanOnly"),
        ("audit_s_binary_linkage.py",
         "PassedArchivedSourceRegistrationBinaryIdentity_NotFullLinkage"),
    ):
        batch.cell(script.removesuffix(".py"), lambda s=script, e=expected:
                   original_binary_audit(batch, s, e), ("original-s-archive",))
    batch.cell("real-dll-fixtures", lambda: original_s_fixtures(batch),
               ("entry-authority",))
    batch.cell("ir-generator-build", lambda: build_ir_generator(batch),
               ("real-dll-fixtures",))
    batch.cell("initializer-native-targets", lambda: target_fixture(batch),
               ("ir-generator-build",))
    if hasattr(batch, "initializer_target_report"):
        batch.target_receipt_sha = sha(batch.initializer_target_report)
    batch.cell("prepare-release", lambda: prepare_ir(batch, role),
               ("initializer-native-targets", "initializer-host-contracts"))
    batch.cell("prepare-initializer", lambda: prepare_initializer(batch, role),
               ("prepare-release",))
    batch.cell("build-initializer", lambda: batch.build(role),
               ("prepare-initializer",))
    for mode in MODE_SHA:
        batch.cell("player-" + mode, lambda m=mode: init_player(batch, m),
                   ("build-initializer",))
    batch.cell("final-authority", lambda: {
        "repositories": batch.authority()["repositories"],
        "initializerSourceSha256": check_git_source(workspace / "hybridclr_demo")})
    expected_cells = (
        "entry-authority", "initializer-host-contracts", "original-s-archive",
        "original-s-process-joins", "audit_s_generated_material", "audit_s_binary_linkage",
        "real-dll-fixtures", "ir-generator-build", "initializer-native-targets",
        "prepare-release", "prepare-initializer", "build-initializer",
        "player-initializer-control", "player-initializer-failure",
        "final-authority",
    )
    require(tuple(row["id"] for row in batch.cells) == expected_cells,
            "Exact new non-replayed 15-cell roster")
    statuses = {row["id"]: row["result"] for row in batch.cells}
    custody_postflight = {"result": "NotRun_HostFailed", "runtimeAcceptance": False}
    if hasattr(batch, "native_host_raw") and hasattr(batch, "native_host_custody"):
        try:
            custody_postflight = verify_host(batch.native_host_raw, batch.native_host_custody)
        except Exception as error:
            custody_postflight = {"result": "FailedLiveHostCustodyBinding",
                                  "error": str(error), "runtimeAcceptance": False}
    passed = (all(value == "Passed" for value in statuses.values()) and
              custody_postflight["result"] == "PassedFullRawHostAndArchiveBinding_NoRuntimeAcceptance")
    result = finalize(batch.root, {
        "schemaVersion": 1, "kind": "R03IRInitializerOneUseEvidenceBatchV1",
        "result": "FocusedInitializerEvidenceReadyForIndependentReview"
                  if passed else "ReturnRequired",
        "repositories": dict(batch.pins), "cells": batch.cells,
        "plannedFreshUnityBuilds": 1,
        "verifiedFreshUnityBuilds": int(statuses["build-initializer"] == "Passed"),
        "plannedFreshInitializerPlayers": 2,
        "verifiedFreshInitializerPlayers": sum(
            statuses["player-" + mode] == "Passed" for mode in MODE_SHA),
        "originalSIndependentBinaryAudit": statuses["audit_s_binary_linkage"],
        "originalSArchivedProcessJoinAudit": statuses["original-s-process-joins"],
        "actualNativeHostCustodyPostflight": custody_postflight,
        "nativeHostRawOutsideProductSeal": str(batch.native_host_raw) if
            hasattr(batch, "native_host_raw") else None,
        "capturedGenericFailure": "NotRun",
        "completeNativeSnapshotV2": "NotImplemented_NotRun",
        "firstRecoveryAuthenticated": False,
        "wholeVmEpoch": "NotProven", "managedShutdown": "NotProven",
        "fullLegacyRegressionAcceptance": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False, "qualificationApproved": False,
        "pureInterpreterExpansionEnabled": False,
    })
    print(json.dumps({"result": result["result"], "seal": result["sealStatus"],
                      "cells": statuses, "R03Accepted": False}, sort_keys=True),
          flush=True)
    return 0 if result["result"] == "FocusedInitializerEvidenceReadyForIndependentReview" and result["sealStatus"] == "Passed" else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "original-s", "output", "unity", "demo-commit"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", a.demo_commit) is not None,
            "Exact current pushed demo commit required")
    return execute(a.workspace, a.original_s, a.output, a.unity, a.demo_commit)


if __name__ == "__main__":
    raise SystemExit(main())
