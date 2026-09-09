using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
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
            output = Path.GetFullPath(M07Probe.Argument("-shadowR01FailureResult", ""));
            active = new Result {
                schemaVersion = 1, kind = "R01FailureResult", mode = M07Probe.Argument("-shadowR01FailureMode", ""),
                processId = Process.GetCurrentProcess().Id, mainThreadId = Thread.CurrentThread.ManagedThreadId,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, baselineBuildId = baselineId, runtimeAbiHash = abi,
                resultPath = output, il2cpp = M07Probe.R00IsIl2CppPlayer(), result = "Failed", error = ""
            };
            try
            {
                Require(active.il2cpp && new[] { Control, Metadata, Initializer }.Contains(active.mode), "Requires an IL2CPP Player and an exact failure mode.");
                Require(!File.Exists(output), "Result is immutable.");
                M07Probe.Input input = M07Probe.R00ReadInputs(baselineId, abi, "T07-03-FullClosure-P03");
                Bind(active, input);
                Run(active, input);
                active.result = "Passed";
            }
            catch (Exception error) { active.error = error.ToString(); UnityEngine.Debug.LogException(error); }
            try { Write(active); }
            catch (Exception error) { active.result = "Failed"; active.error += "\nEvidence write: " + error; UnityEngine.Debug.LogException(error); }
            completed(active.result == "Passed" ? 0 : 1);
            yield break;
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            if (active == null) return 2;
            active.result = "Failed"; active.error = error.ToString();
            try { Write(active); return 1; } catch { return 2; }
        }

        private static void Bind(Result result, M07Probe.Input input)
        {
            result.fixtureManifestPath = input.manifestPath; result.fixtureManifestSha256 = M07Probe.HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath; result.playerBuildReceiptSha256 = M07Probe.HashFile(input.playerReceiptPath);
            result.baselineManifestPath = input.manifest.baselineManifestPath; result.baselineManifestSha256 = input.manifest.baselineManifestSha256;
            result.nativeLibrarySha256 = input.player.nativeLibrarySha256; result.nativeMetadataSha256 = input.player.nativeMetadataSha256;
            result.inputSnapshotHash = input.player.inputSnapshotHash;
            result.failureFixturesPath = Path.GetFullPath(M07Probe.Argument("-shadowR01FailureFixtures", ""));
            result.failureFixturesSha256 = M07Probe.HashFile(result.failureFixturesPath);
            result.negativeInputPath = Path.GetFullPath(M07Probe.Argument("-shadowR01NegativeInput", ""));
            result.negativeInputSha256 = M07Probe.HashFile(result.negativeInputPath);
        }

        private static void Run(Result result, M07Probe.Input input)
        {
            FailureFixtures fixtures = JsonUtility.FromJson<FailureFixtures>(File.ReadAllText(result.failureFixturesPath));
            Require(fixtures.schemaVersion == 1 && fixtures.kind == "R01FailureFixtures" && fixtures.result == "Passed" &&
                fixtures.baselineBuildId == result.baselineBuildId && fixtures.runtimeAbiHash == result.runtimeAbiHash &&
                fixtures.fixtureManifestPath == result.fixtureManifestPath && fixtures.fixtureManifestSha256 == result.fixtureManifestSha256 &&
                fixtures.baselineManifestPath == result.baselineManifestPath && fixtures.baselineManifestSha256 == result.baselineManifestSha256 &&
                fixtures.replayBytesEqual, "Failure fixture binding differs.");
            foreach (FileRow file in fixtures.files) {
                M07Probe.ValidateFile(file.path, file.sha256);
                Require(new FileInfo(file.path).Length == file.length, "Failure fixture file length differs.");
            }
            M07Probe.Fixture selected = result.mode == Initializer ? fixtures.initializer : input.fixture;
            M07Probe.ValidateFile(selected.patchManifest, selected.patchManifestSha256);
            var patch = JsonUtility.FromJson<M07Probe.PatchManifest>(File.ReadAllText(selected.patchManifest));
            Require(patch.nativeBudgetCapabilityVersion == 1 && patch.baselineBuildId == result.baselineBuildId && patch.runtimeAbiHash == result.runtimeAbiHash &&
                patch.baselineManifestSha256 == result.baselineManifestSha256 && patch.compileSnapshotHash == selected.compileSnapshotHash &&
                patch.loadOrder.SequenceEqual(M07Probe.Candidates), "Selected patch is not the complete baseline-bound budgeted closure.");
            result.patchId = patch.patchId; result.patchManifestPath = selected.patchManifest; result.patchManifestSha256 = selected.patchManifestSha256;
            result.closureLoadOrder = patch.loadOrder;
            var dlls = new List<byte[]>(); var pdbs = new List<byte[]>();
            NegativeInput negative = JsonUtility.FromJson<NegativeInput>(File.ReadAllText(result.negativeInputPath));
            foreach (string name in patch.loadOrder)
            {
                var row = patch.closure.Single(item => item.name == name);
                string dllPath = M07Probe.Confined(selected.patchDirectory, row.dll);
                M07Probe.ValidateFile(dllPath, row.sha256);
                byte[] dll = File.ReadAllBytes(dllPath); byte[] pdb = null;
                Require((ulong)dll.LongLength == row.dllSize, "Patch budget length differs.");
                string actualPath = dllPath;
                if (result.mode == Metadata && name == "AssemblyA.Contracts")
                {
                    Require(negative.schemaVersion == 1 && negative.kind == "Q04-NegativeMetadataTransform" &&
                        negative.sourceAssembly == name && negative.sourceSha256 == row.sha256 && negative.sourcePath == dllPath &&
                        negative.sourceLength == dll.LongLength && negative.outputLength == dll.LongLength && negative.changedByteCount == 1 &&
                        negative.lengthPreserved && negative.identityUnchanged && negative.assemblyReferencesUnchanged && negative.sourcePatchRowMatches,
                        "Q04 negative input is not bound to the original production P03 DLL.");
                    actualPath = negative.outputPath;
                    M07Probe.ValidateFile(actualPath, negative.outputSha256);
                    byte[] transformed = File.ReadAllBytes(actualPath);
                    Require(transformed.Length == dll.Length, "Q04 changed image length.");
                    int changed = 0;
                    for (int index = 0; index < dll.Length; ++index)
                        if (dll[index] != transformed[index]) {
                            Require(index == negative.mutation.changedByteOffset && dll[index] == 1 && transformed[index] == 255,
                                "Q04 changed an undeclared byte."); changed++;
                        }
                    Require(changed == 1, "Q04 mutation is not exactly one byte."); dll = transformed;
                }
                if (!string.IsNullOrEmpty(row.pdb)) {
                    string path = M07Probe.Confined(selected.patchDirectory, row.pdb);
                    M07Probe.ValidateFile(path, row.pdbSha256); pdb = File.ReadAllBytes(path);
                }
                dlls.Add(dll); pdbs.Add(pdb);
                result.byteInputs.Add(new ByteInput { name = name, sourcePath = dllPath, sourceSha256 = row.sha256,
                    actualPath = actualPath, actualSha256 = M07Probe.Hash(dll), length = dll.LongLength,
                    pdbSha256 = pdb == null ? "" : M07Probe.Hash(pdb) });
            }
            long[] sizes = dlls.Select(bytes => bytes.LongLength).ToArray(); result.orderedSizes = sizes;
            Capture(result, "before-reserve", sizes);
            Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(result.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(patch.patchId, result.baselineBuildId, patch.loadOrder, M07Probe.RuntimeAbiVersion));
            var observer = new Observer(patch.loadOrder);
            TextWriter previous = Console.Out;
            try
            {
                observer.Start(); observer.Wait(false);
                Console.SetOut(new InitializerWriter(previous, result));
                Expect(result, "reserve", AssemblyShadowRuntime.ReserveMetadataBudget(sizes, 2));
                Capture(result, "after-reserve", sizes);
                for (int index = 0; index < dlls.Count; ++index) {
                    var code = AssemblyShadowRuntime.StageAssembly(dlls[index], pdbs[index]);
                    Expect(result, "stage:" + patch.loadOrder[index], code);
                }
                Capture(result, "after-stage", sizes);
                Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(),
                    result.mode == Metadata ? AssemblyShadowErrorCode.ReferenceResolutionFailed : AssemblyShadowErrorCode.Success);
                Capture(result, "after-validate", sizes);
                if (result.mode != Metadata) {
                    Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(),
                        result.mode == Initializer ? AssemblyShadowErrorCode.ModuleInitializerFailed : AssemblyShadowErrorCode.Success);
                    Capture(result, "after-commit", sizes);
                }
                observer.MarkAfter(); observer.Wait(true);
                if (result.mode != Control) {
                    Expect(result, "abort-rejected", AssemblyShadowRuntime.AbortTransaction(), result.mode == Metadata ? AssemblyShadowErrorCode.InvalidState : AssemblyShadowErrorCode.AlreadyCommitted);
                    Expect(result, "begin-rejected", AssemblyShadowRuntime.BeginTransaction("must-not-restart", result.baselineBuildId, patch.loadOrder, M07Probe.RuntimeAbiVersion),
                        result.mode == Metadata ? AssemblyShadowErrorCode.InvalidState : AssemblyShadowErrorCode.AlreadyCommitted);
                    Capture(result, "after-rejected-operations", sizes);
                }
            }
            finally
            {
                Console.SetOut(previous); observer.Stop();
                result.observerJoined = observer.Joined; result.observerSamples = observer.Samples;
                result.observerErrors = observer.Errors;
            }
            Require(result.observerJoined && result.observerErrors.Length == 0, "Concurrent observer failed or did not join.");
        }

        private static void Expect(Result result, string operation, AssemblyShadowErrorCode code, AssemblyShadowErrorCode expected = AssemblyShadowErrorCode.Success)
        {
            result.operations.Add(new Operation { operation = operation, code = (int)code, name = code.ToString() });
            Require(code == expected, operation + ": expected " + expected + ", got " + code);
        }
        private static Raw ReadDiagnostics(string phase)
        {
            string json; var code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            Require(code == AssemblyShadowErrorCode.Success, "Diagnostic query failed.");
            return Raw.Create(phase, code, json);
        }
        private static void Capture(Result result, string phase, long[] sizes)
        {
            result.diagnostics.Add(ReadDiagnostics(phase));
            string json; var code = AssemblyShadowRuntime.GetMetadataCapacityJson(sizes, out json);
            Require(code == AssemblyShadowErrorCode.Success, "Capacity query failed."); R01MetadataCapacitySnapshot.Parse(json, 2);
            result.capacities.Add(Raw.Create(phase, code, json));
            code = AssemblyShadowRuntime.GetRecoveryInfoJson(out json);
            Require(code == AssemblyShadowErrorCode.Success, "Recovery query failed."); AssemblyShadowRecoveryInfo.Parse(json);
            result.recovery.Add(Raw.Create(phase, code, json));
        }
        private static void Ordinary(AssemblyShadowDiagnostics value, string[] closure)
        {
            Require(value.generation <= value.enumerationGeneration && value.enumerationGeneration <= 1 &&
                value.classEnumerationGeneration >= value.enumerationGeneration && value.classEnumerationGeneration <= 1, "Incoherent observer generations.");
            if (value.classEnumerationGeneration == 0) Require(value.ordinaryClasses.All(row => !row.usesStagedMetadata), "Private class leaked.");
            foreach (string name in closure) {
                var rows = value.ordinaryAssemblies.Where(row => row.name == name).ToArray();
                Require(rows.Count(row => !row.isInterpreter) == 1 && rows.Count(row => row.isInterpreter) == (int)value.enumerationGeneration,
                    "Private or partially published assembly registry: " + name);
            }
        }
        private static void Write(Result result)
        {
            string root = Path.GetDirectoryName(output); Directory.CreateDirectory(root);
            int index = 0;
            foreach (Raw row in result.diagnostics.Concat(result.capacities).Concat(result.recovery).Concat(result.observerSamples)
                .Concat(result.initializerEvents.Select(item => item.diagnostics))) {
                row.rawPath = Path.Combine(root, Path.GetFileNameWithoutExtension(output) + ".raw-" + index++ + ".json");
                File.WriteAllText(row.rawPath, row.rawJson); row.rawSha256 = M07Probe.HashFile(row.rawPath);
            }
            File.WriteAllText(output, JsonUtility.ToJson(result, true));
        }
        private static void Require(bool condition, string detail) { M07Probe.Require(condition, detail); }

        private sealed class Observer
        {
            private readonly string[] closure; private readonly object sync = new object();
            private readonly List<Raw> samples = new List<Raw>(); private readonly List<string> errors = new List<string>();
            private Thread thread; private volatile bool stop, after; private int beforeCount, afterCount;
            public bool Joined; public Raw[] Samples { get { lock (sync) return samples.ToArray(); } }
            public string[] Errors { get { lock (sync) return errors.ToArray(); } }
            public Observer(string[] closure) { this.closure = closure; }
            public void Start() { thread = new Thread(Run) { IsBackground = true, Name = "R01-failure-observer" }; thread.Start(); }
            public void MarkAfter() { after = true; }
            public void Wait(bool wantAfter) {
                var timer = Stopwatch.StartNew();
                while ((wantAfter ? Volatile.Read(ref afterCount) : Volatile.Read(ref beforeCount)) == 0 && timer.ElapsedMilliseconds < 10000) {
                    Require(Errors.Length == 0, "Observer rejected a runtime sample."); Thread.Yield();
                }
                Require((wantAfter ? Volatile.Read(ref afterCount) : Volatile.Read(ref beforeCount)) > 0, "Observer did not capture required side.");
            }
            public void Stop() { stop = true; Joined = thread != null && thread.Join(10000); }
            private void Run() {
                ulong previous = 0, previousEnumeration = 0;
                try {
                    while (!stop) {
                        bool currentAfter = after;
                        Require(Assembly.Load("mscorlib").GetName().Name == "mscorlib", "Stable AOT load changed identity.");
                        Raw row = ReadDiagnostics(currentAfter ? "after" : "before");
                        var value = JsonUtility.FromJson<AssemblyShadowDiagnostics>(row.rawJson); Ordinary(value, closure);
                        Require(value.generation >= previous && value.enumerationGeneration >= previousEnumeration, "Observer generation regressed.");
                        previous = value.generation; previousEnumeration = value.enumerationGeneration;
                        lock (sync) {
                            int count = currentAfter ? ++afterCount : ++beforeCount;
                            if (count <= 16) samples.Add(row);
                        }
                        Thread.Yield();
                    }
                } catch (Exception error) { lock (sync) errors.Add(error.ToString()); }
            }
        }
        private sealed class InitializerWriter : TextWriter
        {
            private readonly TextWriter previous; private readonly Result result; private readonly StringBuilder pending = new StringBuilder();
            public InitializerWriter(TextWriter previous, Result result) { this.previous = previous; this.result = result; }
            public override Encoding Encoding { get { return Encoding.UTF8; } }
            public override void Write(char value) {
                previous.Write(value);
                if (value != '\n') { pending.Append(value); return; }
                string line = pending.ToString().TrimEnd('\r'); pending.Length = 0;
                if (line.StartsWith("M03-INIT:", StringComparison.Ordinal))
                    result.initializerEvents.Add(new InitializerEvent { name = line.Substring(9), diagnostics = ReadDiagnostics("initializer") });
            }
            public override void Write(string value) { if (value != null) foreach (char item in value) Write(item); }
        }
        [Serializable, Preserve] public sealed class Raw {
            [Preserve] public string phase, rawJson, rawPath, rawSha256; [Preserve] public int code, threadId; [Preserve] public long ticks;
            public static Raw Create(string phase, AssemblyShadowErrorCode code, string json) { return new Raw { phase = phase, code = (int)code, rawJson = json,
                threadId = Thread.CurrentThread.ManagedThreadId, ticks = Stopwatch.GetTimestamp() }; }
        }
        [Serializable, Preserve] public sealed class Operation { [Preserve] public string operation, name; [Preserve] public int code; }
        [Serializable, Preserve] public sealed class ByteInput { [Preserve] public string name, sourcePath, sourceSha256, actualPath, actualSha256, pdbSha256; [Preserve] public long length; }
        [Serializable, Preserve] public sealed class InitializerEvent { [Preserve] public string name; [Preserve] public Raw diagnostics; }
        [Serializable, Preserve] public sealed class Result {
            [Preserve] public int schemaVersion, processId, mainThreadId; [Preserve] public string kind, mode, result, error, resultPath;
            [Preserve] public string unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, failureFixturesPath, failureFixturesSha256, negativeInputPath, negativeInputSha256;
            [Preserve] public string patchId, patchManifestPath, patchManifestSha256, nativeLibrarySha256, nativeMetadataSha256, inputSnapshotHash;
            [Preserve] public bool il2cpp, observerJoined; [Preserve] public string[] closureLoadOrder, observerErrors = new string[0];
            [Preserve] public long[] orderedSizes; [Preserve] public List<ByteInput> byteInputs = new List<ByteInput>();
            [Preserve] public List<Operation> operations = new List<Operation>(); [Preserve] public List<Raw> diagnostics = new List<Raw>(), capacities = new List<Raw>(), recovery = new List<Raw>();
            [Preserve] public Raw[] observerSamples = new Raw[0]; [Preserve] public List<InitializerEvent> initializerEvents = new List<InitializerEvent>();
        }
        [Serializable, Preserve] internal sealed class FileRow { [Preserve] public string path, sha256; [Preserve] public long length; }
        [Serializable, Preserve] internal sealed class FailureFixtures {
            [Preserve] public int schemaVersion; [Preserve] public string kind, result, baselineBuildId, runtimeAbiHash;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, fixtureManifestPath, fixtureManifestSha256;
            [Preserve] public M07Probe.Fixture initializer; [Preserve] public bool replayBytesEqual; [Preserve] public FileRow[] files;
        }
        [Serializable, Preserve] internal sealed class Mutation { [Preserve] public int changedByteOffset; }
        [Serializable, Preserve] internal sealed class NegativeInput {
            [Preserve] public int schemaVersion, changedByteCount; [Preserve] public string kind, sourceAssembly, sourcePath, sourceSha256, outputPath, outputSha256;
            [Preserve] public long sourceLength, outputLength; [Preserve] public bool lengthPreserved, identityUnchanged, assemblyReferencesUnchanged, sourcePatchRowMatches;
            [Preserve] public Mutation mutation;
        }
    }
}
