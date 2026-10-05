using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Preserve]
    public static class R01FailureProbe
    {
        private const string Control = "R01-Failure-P03-Control";
        private const string Metadata = "R01-Failure-Q04-Metadata";
        private const string Initializer = "R01-Failure-InitializerThrow";
        private static Result active;
        private static string output;

        public static IEnumerator RunAndWriteCoroutine(string baselineId, string abi, Action<int> completed)
        {
            string outputArgument = M07Probe.Argument("-shadowR01FailureResult", "");
            active = new Result {
                schemaVersion = 2, kind = "R01FailureHandoffResult",
                mode = M07Probe.Argument("-shadowR01FailureMode", ""),
                processId = Process.GetCurrentProcess().Id,
                mainThreadId = Thread.CurrentThread.ManagedThreadId,
                unityVersion = Application.unityVersion,
                platform = Application.platform.ToString(),
                buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath,
                baselineBuildId = baselineId,
                runtimeAbiHash = abi,
                result = "Failed",
                error = ""
            };
            try
            {
                Require(active.il2cpp = M07Probe.R00IsIl2CppPlayer(), "Failure handoff requires an IL2CPP Player.");
                Require(new[] { Control, Metadata, Initializer }.Contains(active.mode), "Unknown failure/publication mode.");
                Require(!string.IsNullOrEmpty(outputArgument), "Failure handoff result path is required.");
                output = Path.GetFullPath(outputArgument);
                active.resultPath = output;
                Require(!File.Exists(output) && !Directory.Exists(output), "Result is immutable.");

                M07Probe.Input input = M07Probe.R00ReadInputs(baselineId, abi, "T07-03-FullClosure-P03");
                Bind(active, input);
                M07Probe.Fixture selected;
                M07Probe.PatchManifest patch;
                ValidateInputs(active, input, out selected, out patch);
                AdoptEarlyTransaction(active, input, selected, patch);
                CapturePostHost(active);
                active.result = "Passed";
            }
            catch (Exception error)
            {
                active.error = error.ToString();
                UnityEngine.Debug.LogException(error);
            }

            try { Write(active); }
            catch (Exception error)
            {
                active.result = "Failed";
                active.error += "\nEvidence write: " + error;
                UnityEngine.Debug.LogException(error);
            }
            completed(active.result == "Passed" ? 0 : 1);
            yield break;
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            if (active == null) return 2;
            active.result = "Failed";
            active.error = error.ToString();
            try { Write(active); return 1; }
            catch { return 2; }
        }

        private static void Bind(Result result, M07Probe.Input input)
        {
            result.fixtureManifestPath = input.manifestPath;
            result.fixtureManifestSha256 = M07Probe.HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath;
            result.playerBuildReceiptSha256 = M07Probe.HashFile(input.playerReceiptPath);
            result.baselineManifestPath = input.manifest.baselineManifestPath;
            result.baselineManifestSha256 = input.manifest.baselineManifestSha256;
            result.nativeLibrarySha256 = input.player.nativeLibrarySha256;
            result.nativeMetadataSha256 = input.player.nativeMetadataSha256;
            result.inputSnapshotHash = input.player.inputSnapshotHash;

            string failures = M07Probe.Argument("-shadowR01FailureFixtures", "");
            string negative = M07Probe.Argument("-shadowR01NegativeInput", "");
            Require(!string.IsNullOrEmpty(failures) && !string.IsNullOrEmpty(negative),
                "Failure fixture and negative-input receipts are required.");
            result.failureFixturesPath = Path.GetFullPath(failures);
            result.failureFixturesSha256 = M07Probe.HashFile(result.failureFixturesPath);
            result.negativeInputPath = Path.GetFullPath(negative);
            result.negativeInputSha256 = M07Probe.HashFile(result.negativeInputPath);
        }

        private static void ValidateInputs(Result result, M07Probe.Input input,
            out M07Probe.Fixture selected, out M07Probe.PatchManifest patch)
        {
            FailureFixtures fixtures = JsonUtility.FromJson<FailureFixtures>(File.ReadAllText(result.failureFixturesPath));
            Require(fixtures != null && fixtures.schemaVersion == 1 && fixtures.kind == "R01FailureFixtures" &&
                fixtures.result == "Passed" && fixtures.baselineBuildId == result.baselineBuildId &&
                fixtures.runtimeAbiHash == result.runtimeAbiHash &&
                fixtures.fixtureManifestPath == result.fixtureManifestPath &&
                fixtures.fixtureManifestSha256 == result.fixtureManifestSha256 &&
                fixtures.baselineManifestPath == result.baselineManifestPath &&
                fixtures.baselineManifestSha256 == result.baselineManifestSha256 &&
                fixtures.replayBytesEqual, "Failure fixture binding differs.");
            foreach (FileRow file in fixtures.files)
            {
                M07Probe.ValidateFile(file.path, file.sha256);
                Require(new FileInfo(file.path).Length == file.length, "Failure fixture file length differs.");
            }

            selected = result.mode == Initializer ? fixtures.initializer : input.fixture;
            M07Probe.ValidateFile(selected.patchManifest, selected.patchManifestSha256);
            patch = JsonUtility.FromJson<M07Probe.PatchManifest>(File.ReadAllText(selected.patchManifest));
            Require(patch != null && patch.baselineBuildId == result.baselineBuildId &&
                patch.runtimeAbiHash == result.runtimeAbiHash &&
                patch.baselineManifestSha256 == result.baselineManifestSha256 &&
                patch.compileSnapshotHash == selected.compileSnapshotHash &&
                patch.loadOrder != null && patch.loadOrder.SequenceEqual(M07Probe.Candidates),
                "Selected patch is not the complete baseline-bound budgeted closure.");
            ValidateBudgetContract(patch, selected);

            result.patchId = patch.patchId;
            result.patchManifestPath = selected.patchManifest;
            result.patchManifestSha256 = selected.patchManifestSha256;
            result.closureLoadOrder = patch.loadOrder.ToArray();

            NegativeInput negative = JsonUtility.FromJson<NegativeInput>(File.ReadAllText(result.negativeInputPath));
            foreach (string name in patch.loadOrder)
            {
                M07Probe.PatchAssembly row = patch.closure.Single(item => item.name == name);
                string dllPath = M07Probe.Confined(selected.patchDirectory, row.dll);
                M07Probe.ValidateFile(dllPath, row.sha256);
                long sourceLength = new FileInfo(dllPath).Length;
                Require((ulong)sourceLength == row.dllSize, "Patch budget length differs.");
                string actualPath = dllPath;
                string actualSha = row.sha256;

                if (result.mode == Metadata && name == "AssemblyA.Contracts")
                {
                    Require(negative != null && negative.schemaVersion == 1 &&
                        negative.kind == "Q04-NegativeMetadataTransform" &&
                        negative.sourceAssembly == name &&
                        negative.sourceSha256 == row.sha256 &&
                        negative.sourcePath == dllPath &&
                        negative.sourceLength == sourceLength &&
                        negative.outputLength == sourceLength &&
                        negative.changedByteCount == 1 &&
                        negative.lengthPreserved && negative.identityUnchanged &&
                        negative.assemblyReferencesUnchanged && negative.sourcePatchRowMatches,
                        "Q04 negative input is not bound to the original production P03 DLL.");
                    actualPath = negative.outputPath;
                    actualSha = negative.outputSha256;
                    M07Probe.ValidateFile(actualPath, actualSha);
                    byte[] original = File.ReadAllBytes(dllPath);
                    byte[] transformed = File.ReadAllBytes(actualPath);
                    Require(transformed.Length == original.Length, "Q04 changed image length.");
                    int changed = 0;
                    for (int index = 0; index < original.Length; ++index)
                    {
                        if (original[index] == transformed[index]) continue;
                        Require(index == negative.mutation.changedByteOffset &&
                            original[index] == 1 && transformed[index] == 255,
                            "Q04 changed an undeclared byte.");
                        ++changed;
                    }
                    Require(changed == 1, "Q04 mutation is not exactly one byte.");
                }

                string pdbSha = "";
                if (!string.IsNullOrEmpty(row.pdb))
                {
                    string pdbPath = M07Probe.Confined(selected.patchDirectory, row.pdb);
                    M07Probe.ValidateFile(pdbPath, row.pdbSha256);
                    pdbSha = row.pdbSha256;
                }
                result.byteInputs.Add(new ByteInput {
                    name = name,
                    sourcePath = dllPath,
                    sourceSha256 = row.sha256,
                    actualPath = actualPath,
                    actualSha256 = actualSha,
                    length = new FileInfo(actualPath).Length,
                    pdbSha256 = pdbSha
                });
            }
            result.orderedSizes = result.byteInputs.Select(item => item.length).ToArray();
        }

        private static int ValidateBudgetContract(M07Probe.PatchManifest patch, M07Probe.Fixture selected)
        {
            int profileVersion;
            Dictionary<string, long> verifiedSizes;
            bool declared = ShadowPatchMetadataReservation.ValidateIfDeclared(
                patch.nativeBudgetCapabilityVersion,
                patch.metadataEncodingProfile,
                patch.metadataCapacityReport,
                patch.metadataEncodingProfile2,
                patch.metadataCapacityReport2,
                patch.loadOrder,
                patch.closure.Select(item => new ShadowPatchMetadataAssembly {
                    name = item.name, dllSize = item.dllSize
                }).ToArray(),
                name => {
                    M07Probe.PatchAssembly row = patch.closure.Single(item => item.name == name);
                    string path = M07Probe.Confined(selected.patchDirectory, row.dll);
                    M07Probe.ValidateFile(path, row.sha256);
                    return File.ReadAllBytes(path);
                },
                out profileVersion,
                out verifiedSizes);
            Require(declared && profileVersion == M07Probe.RuntimeAbiVersion &&
                verifiedSizes.Count == patch.loadOrder.Length &&
                patch.loadOrder.All(name => verifiedSizes.ContainsKey(name)),
                "Selected patch metadata budget contract is missing or unsupported.");
            return profileVersion;
        }

        private static string ExpectedEarlyMode(string mode)
        {
            if (mode == Control) return "Control";
            if (mode == Metadata) return "MetadataFailureContinue";
            if (mode == Initializer) return "InitializerFailureContinue";
            throw new InvalidOperationException("Unknown failure/publication mode.");
        }

        private static string ExpectedEarlyResult(string mode)
        {
            return mode == Control ? "Passed" : "PassedExpectedFailureContinued";
        }

        private static void AdoptEarlyTransaction(Result result, M07Probe.Input input,
            M07Probe.Fixture selected, M07Probe.PatchManifest patch)
        {
            string capsuleArg = M07Probe.Argument("-shadowEarlyCapsule", "");
            string capsuleSha = M07Probe.Argument("-shadowEarlyCapsuleSha256", "");
            string earlyArg = M07Probe.Argument("-shadowEarlyResult", "");
            Require(!string.IsNullOrEmpty(capsuleArg) && !string.IsNullOrEmpty(earlyArg) &&
                M07Probe.IsHash(capsuleSha), "Early handoff arguments are missing.");

            string capsulePath = Path.GetFullPath(capsuleArg);
            string earlyPath = Path.GetFullPath(earlyArg);
            byte[] capsuleBytes = File.ReadAllBytes(capsulePath);
            Require(M07Probe.Hash(capsuleBytes) == capsuleSha, "Early capsule hash differs.");

            string raw = File.ReadAllText(earlyPath);
            Require(raw == R01EarlyStartup.LastReceiptJson,
                "Early receipt differs from the current process callback observation.");
            EarlyReceipt receipt = JsonUtility.FromJson<EarlyReceipt>(raw);
            string expectedMode = ExpectedEarlyMode(result.mode);
            Require(receipt != null && receipt.schemaVersion == 1 &&
                receipt.kind == "R01EarlyStartupReceipt" &&
                receipt.mode == expectedMode &&
                receipt.result == ExpectedEarlyResult(result.mode) &&
                receipt.error == "" && receipt.callbackReturnCode == 0 &&
                receipt.processId == result.processId &&
                receipt.capsulePath == capsulePath &&
                receipt.capsuleSha256 == capsuleSha &&
                receipt.resultPath == earlyPath &&
                receipt.baselineBuildId == result.baselineBuildId &&
                receipt.runtimeAbiHash == result.runtimeAbiHash &&
                receipt.patchId == patch.patchId,
                "Early transaction receipt is not the expected same-process failure/publication transaction.");

            R01EarlyStartup.Capsule capsule = R01EarlyStartup.CapsuleCodec.Parse(capsuleBytes);
            Require(capsule.mode == expectedMode &&
                capsule.patchId == patch.patchId &&
                capsule.baselineBuildId == result.baselineBuildId &&
                capsule.runtimeAbiHash == result.runtimeAbiHash &&
                capsule.candidateNames.SequenceEqual(input.manifest.candidateNames) &&
                capsule.stableAotNames.SequenceEqual(input.manifest.stableAotNames) &&
                capsule.closureLoadOrder.SequenceEqual(patch.loadOrder),
                "Early capsule identity differs from the selected failure/publication patch.");

            foreach (ByteInput expected in result.byteInputs)
            {
                R01EarlyStartup.InputRecord row = capsule.inputs.Single(item => item.name == expected.name);
                Require(row.dllPath == expected.actualPath &&
                    row.dllSha256 == expected.actualSha256 &&
                    row.dllLength == expected.length &&
                    row.pdbSha256 == expected.pdbSha256,
                    "Early staged bytes differ from the selected failure/publication input: " + expected.name);
            }

            result.earlyMode = expectedMode;
            result.earlyReceiptPath = earlyPath;
            result.earlyReceiptSha256 = M07Probe.HashFile(earlyPath);
            result.capsulePath = capsulePath;
            result.capsuleSha256 = capsuleSha;
        }

        private static void CapturePostHost(Result result)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            Require(code == AssemblyShadowErrorCode.Success, "Post-host diagnostics query failed.");
            result.postHostDiagnostics = Raw.Create("after-host-continuation", code, json);
            AssemblyShadowDiagnostics diagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out diagnostics) && diagnostics != null,
                "Post-host diagnostics are malformed.");

            string expectedState = result.mode == Control ? "Committed" :
                result.mode == Metadata ? "Failed" : "FailedAfterCommit";
            Require(diagnostics.state == expectedState,
                "Post-host Assembly Shadow state differs: expected " + expectedState + ", got " + diagnostics.state + ".");

            code = AssemblyShadowRuntime.GetMetadataCapacityJson(result.orderedSizes, out json);
            Require(code == AssemblyShadowErrorCode.Success, "Post-host capacity query failed.");
            R01MetadataCapacitySnapshot.Parse(json, M07Probe.RuntimeAbiVersion);
            result.postHostCapacity = Raw.Create("after-host-continuation", code, json);

            code = AssemblyShadowRuntime.GetRecoveryInfoJson(out json);
            Require(code == AssemblyShadowErrorCode.Success, "Post-host recovery query failed.");
            AssemblyShadowRecoveryInfo.Parse(json);
            result.postHostRecovery = Raw.Create("after-host-continuation", code, json);
        }

        private static void Write(Result result)
        {
            string root = Path.GetDirectoryName(output);
            Directory.CreateDirectory(root);
            int index = 0;
            foreach (Raw row in new[] { result.postHostDiagnostics, result.postHostCapacity, result.postHostRecovery })
            {
                if (row == null) continue;
                row.rawPath = Path.Combine(root,
                    Path.GetFileNameWithoutExtension(output) + ".raw-" + index++ + ".json");
                File.WriteAllText(row.rawPath, row.rawJson);
                row.rawSha256 = M07Probe.HashFile(row.rawPath);
            }
            File.WriteAllText(output, JsonUtility.ToJson(result, true));
        }

        private static void Require(bool condition, string detail) { M07Probe.Require(condition, detail); }

        [Serializable, Preserve]
        public sealed class Raw
        {
            [Preserve] public string phase, rawJson, rawPath, rawSha256;
            [Preserve] public int code, threadId;
            [Preserve] public long ticks;
            public static Raw Create(string phase, AssemblyShadowErrorCode code, string json)
            {
                return new Raw {
                    phase = phase,
                    code = (int)code,
                    rawJson = json,
                    threadId = Thread.CurrentThread.ManagedThreadId,
                    ticks = Stopwatch.GetTimestamp()
                };
            }
        }

        [Serializable, Preserve]
        public sealed class ByteInput
        {
            [Preserve] public string name, sourcePath, sourceSha256, actualPath, actualSha256, pdbSha256;
            [Preserve] public long length;
        }

        [Serializable, Preserve]
        public sealed class Result
        {
            [Preserve] public int schemaVersion, processId, mainThreadId;
            [Preserve] public string kind, mode, result, error, resultPath;
            [Preserve] public string unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, failureFixturesPath, failureFixturesSha256;
            [Preserve] public string negativeInputPath, negativeInputSha256;
            [Preserve] public string patchId, patchManifestPath, patchManifestSha256;
            [Preserve] public string nativeLibrarySha256, nativeMetadataSha256, inputSnapshotHash;
            [Preserve] public bool il2cpp;
            [Preserve] public string[] closureLoadOrder = new string[0];
            [Preserve] public long[] orderedSizes = new long[0];
            [Preserve] public List<ByteInput> byteInputs = new List<ByteInput>();
            [Preserve] public string earlyMode, earlyReceiptPath, earlyReceiptSha256, capsulePath, capsuleSha256;
            [Preserve] public Raw postHostDiagnostics, postHostCapacity, postHostRecovery;
        }

        [Serializable, Preserve]
        private sealed class EarlyReceipt
        {
            [Preserve] public int schemaVersion, processId, callbackReturnCode;
            [Preserve] public string kind, mode, result, error, capsulePath, capsuleSha256, resultPath;
            [Preserve] public string baselineBuildId, runtimeAbiHash, patchId;
        }

        [Serializable, Preserve]
        internal sealed class FileRow
        {
            [Preserve] public string path, sha256;
            [Preserve] public long length;
        }

        [Serializable, Preserve]
        internal sealed class FailureFixtures
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind, result, baselineBuildId, runtimeAbiHash;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, fixtureManifestPath, fixtureManifestSha256;
            [Preserve] public M07Probe.Fixture initializer;
            [Preserve] public bool replayBytesEqual;
            [Preserve] public FileRow[] files;
        }

        [Serializable, Preserve]
        internal sealed class Mutation { [Preserve] public int changedByteOffset; }

        [Serializable, Preserve]
        internal sealed class NegativeInput
        {
            [Preserve] public int schemaVersion, changedByteCount;
            [Preserve] public string kind, sourceAssembly, sourcePath, sourceSha256, outputPath, outputSha256;
            [Preserve] public long sourceLength, outputLength;
            [Preserve] public bool lengthPreserved, identityUnchanged, assemblyReferencesUnchanged, sourcePatchRowMatches;
            [Preserve] public Mutation mutation;
        }
    }
}
