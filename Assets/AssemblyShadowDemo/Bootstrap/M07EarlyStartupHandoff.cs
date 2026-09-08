using System;
using System.IO;
using System.Linq;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    public static partial class M07Probe
    {
        // This handoff imports observations captured by the actual early call.
        // It does not repeat a transaction or synthesize pre-Commit snapshots.
        private static void AdoptEarlyTransaction(Result result, Input input)
        {
            string capsulePath = Path.GetFullPath(Argument("-shadowEarlyCapsule", ""));
            string capsuleSha = Argument("-shadowEarlyCapsuleSha256", "");
            string receiptPath = Path.GetFullPath(Argument("-shadowEarlyResult", ""));
            byte[] capsuleBytes = File.ReadAllBytes(capsulePath);
            Require(IsHash(capsuleSha) && Hash(capsuleBytes) == capsuleSha, "Handoff capsule hash differs from the early callback input.");
            string raw = File.ReadAllText(receiptPath);
            Require(raw == R01EarlyStartup.LastReceiptJson, "Early receipt differs from the current process's retained callback observation.");
            EarlyReceipt receipt = JsonUtility.FromJson<EarlyReceipt>(raw);
            Require(receipt != null && receipt.schemaVersion == 1 && receipt.kind == "R01EarlyStartupReceipt" &&
                receipt.result == "Passed" && receipt.error == "" && receipt.callbackReturnCode == 0 &&
                receipt.processId == result.processId && receipt.managedThreadId == Environment.CurrentManagedThreadId &&
                receipt.capsulePath == capsulePath && receipt.capsuleSha256 == capsuleSha && receipt.resultPath == receiptPath &&
                receipt.baselineBuildId == result.baselineBuildId && receipt.runtimeAbiHash == result.runtimeAbiHash &&
                receipt.patchId == input.fixture.patchId &&
                new[] { "Control", "OrdinaryFirst", "OrdinaryAfterReserve" }.Contains(receipt.mode),
                "Early callback receipt is not an admissible successful transaction for this Player.");
            R01EarlyStartup.Capsule capsule = R01EarlyStartup.CapsuleCodec.Parse(capsuleBytes);
            Require(capsule.mode == receipt.mode && capsule.patchId == receipt.patchId &&
                capsule.baselineBuildId == receipt.baselineBuildId && capsule.runtimeAbiHash == receipt.runtimeAbiHash &&
                capsule.candidateNames.SequenceEqual(input.manifest.candidateNames) && capsule.stableAotNames.SequenceEqual(input.manifest.stableAotNames) &&
                capsule.closureLoadOrder.SequenceEqual(input.fixture.closureLoadOrder), "Early input inventory differs from the admitted M07 fixture.");
            // Semantic manifest/resource validation runs in ReadInputs. Its exact
            // bytes must have been hashed by the BCL callback before any mutation.
            string[] prerequisites = new[] { input.manifestPath, input.playerReceiptPath, input.manifest.baselineManifestPath,
                input.fixture.patchManifest, input.resourceReceiptPath }.Concat(input.resources.bundles.Select(bundle =>
                    Confined(input.resourceRoot, input.resources.bundleDirectory + "/" + bundle.name))).ToArray();
            foreach (string path in prerequisites)
            {
                R01EarlyStartup.PrerequisiteRecord bound = capsule.prerequisites.Single(row => row.path == Path.GetFullPath(path));
                Require(bound.length == new FileInfo(path).Length && bound.sha256 == HashFile(path), "Resource/manifest changed since early precheck: " + path);
            }
            result.configureCode = EarlyCode(result, receipt, "configure", "configure");
            result.beginCode = EarlyCode(result, receipt, "begin", "begin");
            result.reserveMetadataBudget = EarlyCode(result, receipt, "reserve", "reserve-metadata-budget");
            result.stageOrder = input.fixture.closureLoadOrder.ToArray();
            foreach (string name in result.stageOrder)
            {
                PatchAssembly patch = input.patch.closure.Single(row => row.name == name);
                R01EarlyStartup.InputRecord bytes = capsule.inputs.Single(row => row.name == name);
                Require(bytes.dllPath == Confined(input.fixture.patchDirectory, patch.dll) && bytes.dllSha256 == patch.sha256 &&
                    bytes.pdbSha256 == patch.pdbSha256 && (string.IsNullOrEmpty(patch.pdb) ? bytes.pdbPath == "" :
                    bytes.pdbPath == Confined(input.fixture.patchDirectory, patch.pdb)), "Early staged bytes differ from the selected patch: " + name);
                result.stageResults.Add(new StageResult { name = name, code = EarlyCode(result, receipt, "stage:" + name, "stage-" + name),
                    dllSha256 = bytes.dllSha256, pdbSha256 = bytes.pdbSha256 });
            }
            ImportEarlySnapshot(result, receipt, "after-stage", "staged", AssemblyShadowState.Staged);
            result.validateCode = EarlyCode(result, receipt, "validate", "validate");
            ImportEarlySnapshot(result, receipt, "after-validate", "validated-resource-precheck-complete", AssemblyShadowState.Validated);
            result.commitCode = EarlyCode(result, receipt, "commit", "commit");
            EarlySnapshot proof = receipt.snapshots.Single(row => row.phase == "after-commit");
            AssemblyShadowDiagnostics committed;
            Require(proof.diagnosticsCode == "Success" && AssemblyShadowDiagnostics.TryParse(proof.diagnosticsJson, out committed) &&
                committed.state == "Committed" && committed.generation > 0, "Early callback did not commit its world.");
            RequireState(result, AssemblyShadowState.Committed, "early-handoff");
            CaptureAssemblyModes(result, false);
            result.commitCompletedBeforeResourceLoad = !result.businessResourceLoadStarted;
            Require(result.resourcePrecheckPassed && result.commitCompletedBeforeResourceLoad, "Business resource load preceded early handoff.");
            Capture(result, "committed-before-resources");
        }

        private static string EarlyCode(Result result, EarlyReceipt receipt, string phase, string check)
        {
            EarlyOperation operation = receipt.operations.Single(row => row.phase == phase);
            Require(operation.code == "Success" && operation.intCode == (int)AssemblyShadowErrorCode.Success,
                "Early operation did not succeed: " + phase);
            return Expect(result, check, (AssemblyShadowErrorCode)operation.intCode);
        }

        private static void ImportEarlySnapshot(Result result, EarlyReceipt receipt, string sourcePhase, string phase, AssemblyShadowState state)
        {
            EarlySnapshot observation = receipt.snapshots.Single(row => row.phase == sourcePhase);
            AssemblyShadowDiagnostics diagnostics = null;
            Require(observation.diagnosticsCode == "Success" && AssemblyShadowDiagnostics.TryParse(observation.diagnosticsJson, out diagnostics) &&
                diagnostics.state == state.ToString(), "Early snapshot state differs: " + sourcePhase);
            result.snapshots.Add(new Snapshot { phase = phase, diagnostics = diagnostics });
        }

        [Serializable, Preserve] private sealed class EarlyReceipt
        {
            [Preserve] public int schemaVersion, processId, managedThreadId, callbackReturnCode;
            [Preserve] public string kind, mode, result, error, capsulePath, capsuleSha256, resultPath, baselineBuildId, runtimeAbiHash, patchId;
            [Preserve] public EarlyOperation[] operations;
            [Preserve] public EarlySnapshot[] snapshots;
        }
        [Serializable, Preserve] private sealed class EarlyOperation { [Preserve] public string phase, code; [Preserve] public int intCode; }
        [Serializable, Preserve] private sealed class EarlySnapshot { [Preserve] public string phase, diagnosticsCode, diagnosticsJson; }
    }
}
