using System;
using System.Collections.Generic;
using Stopwatch = System.Diagnostics.Stopwatch;
using Process = System.Diagnostics.Process;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// Runtime-only M04 witness.  The bootstrap knows candidate names as data,
    /// and acquires candidate types only through the fixed entrypoint names.
    /// No candidate Assembly or Type handle is created on a successful path
    /// before the transaction is committed.
    /// </summary>
    [Preserve]
    public static class M04ReferenceProbe
    {
        private const string Contracts = "AssemblyA.Contracts";
        private const string Extensibility = "AssemblyA.Implementation.Extensibility";
        private const string Internal = "AssemblyA.Implementation.Internal";
        private const string ContractsConsumer = "AssemblyShadowDemo.ContractsConsumer";
        private const string ExtensibilityConsumer = "AssemblyShadowDemo.ExtensibilityConsumer";
        private const int RuntimeAbiVersion = 1;
        private static readonly string[] Candidates = { Contracts, Extensibility, Internal, ContractsConsumer, ExtensibilityConsumer };

        public static int RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            var result = new Result {
                schemaVersion = 1, milestone = "M04", mode = Argument("-shadowM04Mode", "T04-01"), result = "Failed",
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, processId = Process.GetCurrentProcess().Id,
                baselineBuildId = expectedBaselineBuildId, runtimeAbiHash = expectedRuntimeAbiHash,
                il2cpp = IsIl2CppPlayer(), checks = new List<Check>(), snapshots = new List<Snapshot>(),
                actualLogicalAssemblies = new List<AssemblyObservation>(), assemblyObservations = new List<AssemblyObservation>(),
                loadObservations = new List<LoadObservation>(), refRows = new List<ReferenceRow>(), executingWitnesses = new List<ExecutingWitness>(),
                stageOrder = new string[0], stageResults = new List<StageResult>(), benchmark = new Benchmark(), businessMarker = "M04-REFERENCE-PROBE",
                moduleMvidObservationPolicy = "unavailable-pinned-il2cpp-use-byte-bound-build-and-native-diagnostics",
            };
            try
            {
                Require(result.il2cpp, "M04 acceptance requires an actual IL2CPP Player.");
                Require(!string.IsNullOrEmpty(expectedBaselineBuildId) && IsHash(expectedRuntimeAbiHash), "Player-embedded baseline/ABI identity is absent.");
                Require(IsKnownMode(result.mode), "Unknown M04 mode: " + result.mode);

                Input input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash, result);
                result.fixtureManifestPath = input.manifestPath;
                result.fixtureManifestSha256 = HashFile(input.manifestPath);
                result.playerBuildReceiptPath = input.playerReceiptPath;
                result.playerBuildReceiptSha256 = HashFile(input.playerReceiptPath);

                if (result.mode == "T04-10-BenchmarkOff")
                {
                    // The OFF benchmark intentionally does not call Configure;
                    // it measures the ordinary constant-name lookup path only.
                    RunBenchmark(result, false);
                }
                else if (result.mode == "T04-08")
                {
                    RunFeatureDisabled(result, input);
                }
                else
                {
                    Fixture fixture = SelectFixture(input.manifest, result.mode);
                    BindFixture(result, input, fixture);
                    RunTransaction(result, input, fixture);
                }
                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.error = error.ToString();
                UnityEngine.Debug.LogException(error);
                // Diagnostics are captured from both successful and failed
                // native paths; a failed capture is itself retained in error.
                try { Capture(result, "failure"); }
                catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
            }
            return WriteEvidence(result);
        }

        private static void RunTransaction(Result result, Input input, Fixture fixture)
        {
            bool p01 = result.mode == "T04-01";
            bool stagedVisibility = result.mode == "T04-03";
            bool missingMember = result.mode == "T04-04";
            bool escapingReference = result.mode == "T04-05";
            bool benchmarkOn = result.mode == "T04-09-BenchmarkOn";
            bool benchmarkOff = result.mode == "T04-10-BenchmarkOff";
            string patchId = p01 ? "P01" : "P03";
            Require(fixture.patchId == patchId, "Mode/fixture mismatch: " + result.mode);
            string[] closure = fixture.closureLoadOrder;
            Require(closure != null && closure.Length > 0, "M04 fixture closure is empty.");
            RequireState(result, AssemblyShadowState.Disabled, "initial");
            Capture(result, "initial");

            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(fixture.patchId, input.manifest.baselineBuildId, escapingReference ? new[] { Contracts } : closure, RuntimeAbiVersion));
            RequireState(result, AssemblyShadowState.Staging, "staging");

            var toStage = missingMember ? new[] { Internal } : escapingReference ? new[] { Contracts } : closure;
            foreach (string name in toStage) Stage(result, fixture, name);
            result.stageOrder = toStage.ToArray();
            Capture(result, "staged");

            AssemblyShadowErrorCode expectedValidation = missingMember ? AssemblyShadowErrorCode.ClosureMemberMissing :
                escapingReference ? AssemblyShadowErrorCode.ReferenceEscapesClosure : AssemblyShadowErrorCode.Success;
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), expectedValidation);
            Capture(result, "validated");
            if (expectedValidation != AssemblyShadowErrorCode.Success)
            {
                result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction());
                RequireState(result, AssemblyShadowState.Aborted, "aborted");
                Capture(result, "aborted");
                return;
            }

            if (stagedVisibility)
            {
                // This is intentionally the one negative process that creates
                // managed baseline handles after private validation.
                Assembly normalBaseline = LoadContractsLiteral();
                AssemblyExecutionMode normalMode;
                Require(AssemblyShadowRuntime.GetAssemblyExecutionMode(Contracts, out normalMode) == AssemblyShadowErrorCode.Success && normalMode == AssemblyExecutionMode.AotBaseline,
                    "Normal lookup exposed a staged shadow before commit.");
                result.loadObservations.Add(new LoadObservation { requested = Contracts, overload = "staged-normal", assemblyName = normalBaseline.GetName().Name, sameAssembly = true });
                result.actualLogicalAssemblies = EnumerateAssemblies(false);
                Require(!result.actualLogicalAssemblies.Any(item => Candidates.Contains(item.name, StringComparer.OrdinalIgnoreCase) && item.isInterpreter), "Private staging leaked a shadow into normal enumeration.");
                result.commit = Expect(result, "commit-after-baseline-use", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.BaselineAlreadyUsed);
                result.abort = Expect(result, "abort-after-baseline-use", AssemblyShadowRuntime.AbortTransaction());
                RequireState(result, AssemblyShadowState.Aborted, "sealed");
                Capture(result, "sealed");
                return;
            }

            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction());
            Capture(result, "committed");
            RequireState(result, AssemblyShadowState.Committed, "committed");
            CaptureAssemblyIdentity(result, input, fixture);
            if (!benchmarkOn && !benchmarkOff)
            {
                result.actualLogicalAssemblies = EnumerateAssemblies(true);
                VerifyLogicalCandidateInventory(result, input, fixture);
            }
            if (result.mode == "T04-02" || result.mode == "T04-06" || result.mode == "T04-07")
            {
                RunIdentityWitnesses(result, input, fixture);
            }
            if (result.mode == "T04-02")
            {
                // Ordinary HybridCLR loading remains independently covered
                // after the active five-assembly snapshot is published.
                result.ordinary = M04OrdinaryAssemblyProbe.Run(input.MscorlibPath, input.MscorlibSha256, input.MscorlibFullName, input.MscorlibMvid);
            }
            if (benchmarkOn || benchmarkOff)
            {
                RunBenchmark(result, benchmarkOn);
            }
            if (result.mode == "T04-02")
            {
                Require(fixture.assemblyIdentities != null && fixture.assemblyIdentities.Length == Candidates.Length, "P03 must carry all five patch identities.");
            }
            Capture(result, "final");
        }

        private static void RunFeatureDisabled(Result result, Input input)
        {
            AssemblyShadowState state; AssemblyExecutionMode mode; string json;
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames), AssemblyShadowErrorCode.FeatureDisabled);
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction("P03", input.manifest.baselineBuildId, input.manifest.closureLoadOrder, RuntimeAbiVersion), AssemblyShadowErrorCode.FeatureDisabled);
            result.stage = Expect(result, "stage", AssemblyShadowRuntime.StageAssembly(null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.stateCode = Expect(result, "state", AssemblyShadowRuntime.GetState(out state), AssemblyShadowErrorCode.FeatureDisabled);
            result.state = state.ToString();
            result.executionModeCode = Expect(result, "execution-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(Internal, out mode), AssemblyShadowErrorCode.FeatureDisabled);
            result.executionMode = mode.ToString();
            result.diagnosticsCode = Expect(result, "diagnostics", AssemblyShadowRuntime.GetDiagnosticsJson(out json), AssemblyShadowErrorCode.FeatureDisabled);
            result.nativeDiagnosticsJson = json;
            AssemblyShadowDiagnostics disabledDiagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out disabledDiagnostics), "OFF native diagnostics JSON is malformed.");
            result.snapshots.Add(new Snapshot { phase = "disabled", diagnostics = disabledDiagnostics });
            Require(state == AssemblyShadowState.Disabled && mode == AssemblyExecutionMode.AotBaseline, "OFF out values changed.");
            result.ordinary = M04OrdinaryAssemblyProbe.Run(input.MscorlibPath, input.MscorlibSha256, input.MscorlibFullName, input.MscorlibMvid);
            RunBenchmark(result, false);
        }

        private static void RunIdentityWitnesses(Result result, Input input, Fixture fixture)
        {
            foreach (string name in fixture.closureLoadOrder)
            {
                Assembly loaded = LoadSimple(name);
                Require(loaded != null && string.Equals(loaded.GetName().Name, name, StringComparison.OrdinalIgnoreCase), "Simple Assembly.Load identity mismatch: " + name);
                result.loadObservations.Add(new LoadObservation { requested = name, overload = "simple", assemblyName = loaded.GetName().Name, sameAssembly = true });
                Assembly suffix = LoadSuffixVariant(name);
                Require(ObjectEquals(loaded, suffix), "DLL suffix did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = SuffixLiteral(name), overload = "dll-suffix", assemblyName = suffix.GetName().Name, sameAssembly = true });
                Assembly named = LoadByAssemblyName(name);
                Require(ObjectEquals(loaded, named), "AssemblyName overload did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = name, overload = "AssemblyName", assemblyName = named.GetName().Name, sameAssembly = true });
                Type type = GetWitnessType(name);
                Assembly fromType = type.Assembly;
                Require(ObjectEquals(loaded, fromType), "Type.Assembly did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = WitnessTypeLiteral(name), overload = "Type.GetType", assemblyName = fromType.GetName().Name, sameAssembly = true });
                Assembly fromPath = LoadPathVariant(name);
                Require(ObjectEquals(loaded, fromPath), "Path variant did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = PathLiteral(name), overload = "path", assemblyName = fromPath.GetName().Name, sameAssembly = true });
                Assembly caseVariant = LoadCaseVariant(name);
                Require(ObjectEquals(loaded, caseVariant), "Case variant did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = CaseLiteral(name), overload = "case", assemblyName = caseVariant.GetName().Name, sameAssembly = true });
                Assembly backslash = LoadBackslashPathVariant(name);
                Require(ObjectEquals(loaded, backslash), "Backslash path variant did not resolve the active Assembly: " + name);
                result.loadObservations.Add(new LoadObservation { requested = BackslashPathLiteral(name), overload = "backslash-path", assemblyName = backslash.GetName().Name, sameAssembly = true });
            }

            foreach (string name in fixture.closureLoadOrder)
            {
                Assembly loaded = LoadSimple(name);
                AssemblyIdentity identity = fixture.assemblyIdentities.Single(item => item.name == name);
                AssemblyName[] references = loaded.GetReferencedAssemblies();
                Require(references.Length == (identity.referenceIdentities == null ? 0 : identity.referenceIdentities.Length), "Declared AssemblyRef count mismatch: " + name);
                for (int index = 0; index < references.Length; ++index)
                {
                    ReferenceIdentity expected = identity.referenceIdentities[index];
                    AssemblyName actual = references[index];
                    Require(expected.referenceIndex == index && expected.name == actual.Name && expected.version == actual.Version.ToString() && expected.culture == (actual.CultureName ?? "") && expected.publicKeyToken == Token(actual), "Declared AssemblyRef identity mismatch: " + name + " row " + index);
                    result.refRows.Add(new ReferenceRow { assemblyName = name, referenceIndex = index, name = actual.Name, fullName = actual.FullName, version = actual.Version.ToString(), culture = actual.CultureName ?? "", publicKeyToken = Token(actual) });
                }
            }

            foreach (string name in fixture.closureLoadOrder)
            {
                string typeName = name == Internal ? "AssemblyA.Implementation.Internal.InternalEntry" : name == Extensibility ? "AssemblyA.Implementation.Extensibility.VersionedComponentBase" : name == Contracts ? "AssemblyA.Contracts.AssemblyAContractVersion" : name == ContractsConsumer ? "AssemblyShadowDemo.Consumers.ContractsConsumer" : "AssemblyShadowDemo.Consumers.DerivedExternalComponent";
                object witness = InvokeExecutingWitness(name, typeName);
                Assembly loaded = LoadSimple(name);
                Assembly witnessAssembly = witness as Assembly;
                Require(witnessAssembly != null && ObjectEquals(loaded, witnessAssembly), "Executing-assembly witness mismatch: " + name);
                result.executingWitnesses.Add(new ExecutingWitness { assemblyName = name, executingAssemblyName = witnessAssembly.GetName().Name, sameAssembly = true });
                Require(EnumerateAssemblyHandles().Any(candidate => ObjectEquals(candidate, loaded)), "AppDomain enumeration lost the active Assembly identity: " + name);
            }
            result.actualLogicalAssemblies = EnumerateAssemblies(true);
            foreach (AssemblyObservation observation in result.actualLogicalAssemblies.Where(item => fixture.closureLoadOrder.Contains(item.name, StringComparer.OrdinalIgnoreCase)))
                Require(observation.isInterpreter, "Logical enumeration did not expose an active shadow: " + observation.name);
        }

        private static object InvokeExecutingWitness(string assemblyName, string typeName)
        {
            Type type = GetWitnessType(assemblyName);
            MethodInfo method = type.GetMethod("GetExecutingAssemblyObject", BindingFlags.Public | BindingFlags.Static);
            Require(method != null && method.ReturnType == typeof(object), "M04 executing witness entrypoint missing: " + typeName);
            return method.Invoke(null, null);
        }

        private static Assembly[] EnumerateAssemblyHandles()
        {
            return AppDomain.CurrentDomain.GetAssemblies();
        }

        private static List<AssemblyObservation> EnumerateAssemblies(bool logical)
        {
            var result = new List<AssemblyObservation>();
            foreach (Assembly assembly in EnumerateAssemblyHandles())
            {
                if (assembly == null) continue;
                string name = assembly.GetName().Name;
                AssemblyExecutionMode mode;
                AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                result.Add(new AssemblyObservation { name = name, fullName = assembly.FullName, mvid = "", mvidAvailable = false, executionCode = code.ToString(), executionMode = mode.ToString(), isInterpreter = code == AssemblyShadowErrorCode.Success && mode == AssemblyExecutionMode.InterpreterShadow, logical = logical });
            }
            return result;
        }

        private static void CaptureAssemblyIdentity(Result result, Input input, Fixture fixture)
        {
            foreach (string name in Candidates)
            {
                Assembly loaded = LoadSimple(name);
                AssemblyExecutionMode mode;
                AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                AssemblyIdentity expected = fixture.assemblyIdentities.SingleOrDefault(item => item.name == name) ?? input.player.assemblyIdentities.Single(item => item.name == name);
                Require(loaded.FullName == expected.fullName, "Runtime Assembly full identity is not byte-bound: " + name);
                bool interpreter = code == AssemblyShadowErrorCode.Success && mode == AssemblyExecutionMode.InterpreterShadow;
                Require(interpreter == fixture.assemblyIdentities.Any(item => item.name == name), "Runtime execution mode differs from the active closure: " + name);
                result.assemblyObservations.Add(new AssemblyObservation { name = name, fullName = loaded.FullName, mvid = "", mvidAvailable = false, executionCode = code.ToString(), executionMode = mode.ToString(), isInterpreter = interpreter, logical = true });
            }
            Type entry = Type.GetType("AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal", true);
            MethodInfo marker = entry.GetMethod("GetMarker", BindingFlags.Public | BindingFlags.Instance);
            Require(marker != null, "M04 InternalEntry marker is missing.");
            result.businessMarker = (string)marker.Invoke(Activator.CreateInstance(entry), null);
            Require(result.businessMarker == "PATCH-P01-INTERNAL", "M04 active Internal business marker mismatch.");
            Assembly mscorlib = Assembly.Load("mscorlib");
            Require(IsAotStable(input, mscorlib, "mscorlib"), "Stable AOT mscorlib changed execution mode.");
            Assembly unityCore = Assembly.Load("UnityEngine.CoreModule");
            Require(IsAotStable(input, unityCore, "UnityEngine.CoreModule"), "Stable Unity AOT assembly changed execution mode.");
            AddStableObservation(result, input, mscorlib, "mscorlib");
            AddStableObservation(result, input, unityCore, "UnityEngine.CoreModule");
        }

        private static void AddStableObservation(Result result, Input input, Assembly assembly, string name)
        {
            AssemblyExecutionMode mode;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
            result.assemblyObservations.Add(new AssemblyObservation { name = name, fullName = assembly.FullName, mvid = "", mvidAvailable = false, executionCode = code.ToString(), executionMode = mode.ToString(), isInterpreter = false, logical = true });
        }

        private static bool IsAotStable(Input input, Assembly assembly, string name)
        {
            AssemblyExecutionMode mode;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
            AssemblyIdentity linked = input.player.assemblyIdentities.SingleOrDefault(item => item.name == name);
            Require(linked != null && assembly.FullName == linked.fullName, "Stable AOT full identity mismatch: " + name);
            return code == AssemblyShadowErrorCode.CandidateNotRegistered && mode == AssemblyExecutionMode.AotBaseline;
        }

        private static void VerifyLogicalCandidateInventory(Result result, Input input, Fixture fixture)
        {
            foreach (string name in Candidates)
            {
                AssemblyObservation[] matches = result.actualLogicalAssemblies.Where(item => string.Equals(item.name, name, StringComparison.OrdinalIgnoreCase)).ToArray();
                Require(matches.Length == 1, "Logical enumeration returned a duplicate or missing candidate: " + name);
                bool expectedShadow = fixture.assemblyIdentities.Any(item => item.name == name);
                Require(matches[0].isInterpreter == expectedShadow, "Logical execution mode differs for candidate: " + name);
                AssemblyIdentity identity = expectedShadow ? fixture.assemblyIdentities.Single(item => item.name == name) : input.player.assemblyIdentities.Single(item => item.name == name);
                Require(!matches[0].mvidAvailable && string.IsNullOrEmpty(matches[0].mvid) && matches[0].fullName == identity.fullName, "Logical Assembly identity differs for candidate: " + name);
            }
        }

        private static void RunBenchmark(Result result, bool enabled)
        {
            const int iterations = 1000000;
            const int warmups = 1000;
            Assembly warmupAssembly = null;
            for (int index = 0; index < warmups; ++index) if (index == 0) warmupAssembly = LoadInternalLiteral(); else LoadInternalLiteral();
            long checksum = 0;
            Stopwatch timer = Stopwatch.StartNew();
            Assembly last = null;
            for (int index = 0; index < iterations; ++index)
            {
                last = LoadInternalLiteral();
                checksum += last == null ? 0 : 1;
            }
            timer.Stop();
            Require(last != null && checksum == iterations && ObjectEquals(warmupAssembly, last), "Benchmark dropped or changed a constant-name lookup.");
            result.benchmark = new Benchmark { enabled = enabled, requestedName = Internal, warmupCount = warmups, lookupCount = iterations, elapsedTicks = timer.ElapsedTicks, stopwatchFrequency = Stopwatch.Frequency, checksum = checksum, finalSameAssembly = true, finalAssemblyName = last.GetName().Name, finalFullName = last.FullName, finalMvid = "", finalMvidAvailable = false, finalReferenceIdentities = last.GetReferencedAssemblies().Select(item => item.FullName).ToArray() };
        }

        private static Assembly LoadInternalLiteral()
        {
            return Assembly.Load("AssemblyA.Implementation.Internal");
        }
        private static Assembly LoadContractsLiteral()
        {
            return Assembly.Load("AssemblyA.Contracts");
        }

        private static void Stage(Result result, Fixture fixture, string name)
        {
            PatchAssembly assembly = fixture.patch.closure.Single(item => item.name == name);
            string path = Path.GetFullPath(Path.Combine(fixture.patchRoot, assembly.dll));
            Require(File.Exists(path), "Patch DLL is missing: " + path);
            byte[] bytes = File.ReadAllBytes(path);
            Require(Hash(bytes) == assembly.sha256, "Patch DLL hash mismatch: " + name);
            byte[] pdb = null;
            if (!string.IsNullOrEmpty(assembly.pdb)) pdb = File.ReadAllBytes(Path.GetFullPath(Path.Combine(fixture.patchRoot, assembly.pdb)));
            string code = Expect(result, "stage-" + name, AssemblyShadowRuntime.StageAssembly(bytes, pdb));
            result.stageResults.Add(new StageResult { name = name, code = code, dllSha256 = Hash(bytes), pdbSha256 = pdb == null ? "" : Hash(pdb) });
        }

        private static Fixture SelectFixture(FixtureManifest manifest, string mode)
        {
            string id = mode == "T04-01" ? "P01" : "P03";
            return manifest.fixtures.Single(fixture => fixture.patchId == id);
        }

        private static void BindFixture(Result result, Input input, Fixture fixture)
        {
            result.patchId = fixture.patchId;
            result.patchManifestPath = Path.GetFullPath(fixture.patchManifest);
            result.patchManifestSha256 = fixture.patchManifestSha256;
            result.compileSnapshotHash = fixture.compileSnapshotHash;
            Require(HashFile(result.patchManifestPath) == fixture.patchManifestSha256, "Patch manifest hash mismatch.");
            Require(fixture.patch != null && fixture.patch.patchId == fixture.patchId, "Patch manifest identity mismatch.");
            Require(fixture.patch.baselineBuildId == input.manifest.baselineBuildId && fixture.patch.runtimeAbiHash == input.manifest.runtimeAbiHash, "Patch baseline/ABI mismatch.");
            Require(fixture.assemblyIdentities != null && fixture.assemblyIdentities.Length == fixture.patch.closure.Length, "Patch identity evidence is incomplete.");
            foreach (PatchAssembly patch in fixture.patch.closure)
            {
                AssemblyIdentity identity = fixture.assemblyIdentities.Single(item => item.name == patch.name);
                Require(identity.mvid == patch.mvid && identity.sha256 == patch.sha256, "Patch identity does not bind actual DLL bytes: " + patch.name);
                BaselineAssembly baseline = input.baseline.assemblies.Single(item => item.name == patch.name);
                Require(patch.baselineMvid == baseline.mvid, "Patch baseline MVID was not sourced from the verified baseline manifest: " + patch.name);
            }
        }

        private static Input ReadInputs(string expectedBaseline, string expectedAbi, Result result)
        {
            string manifestPath = Path.GetFullPath(Argument("-shadowFixtureManifest", ""));
            string playerPath = Path.GetFullPath(Argument("-shadowPlayerBuild", ""));
            Require(File.Exists(manifestPath), "Verified M04 fixture manifest is required.");
            Require(File.Exists(playerPath), "Verified M04 Player build receipt is required.");
            FixtureManifest manifest = JsonUtility.FromJson<FixtureManifest>(File.ReadAllText(manifestPath));
            PlayerBuildReceipt player = JsonUtility.FromJson<PlayerBuildReceipt>(File.ReadAllText(playerPath));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M04", "M04 fixture schema mismatch.");
            Require(player != null && player.schemaVersion == 1 && player.milestone == "M04", "M04 Player receipt schema mismatch.");
            Require(manifest.baselineBuildId == expectedBaseline && manifest.runtimeAbiHash == expectedAbi, "Fixture does not match Player-embedded baseline/ABI.");
            Require(player.baselineBuildId == expectedBaseline && player.runtimeAbiHash == expectedAbi && player.buildGuid == Application.buildGUID, "Player receipt identity mismatch.");
            ValidateNativeMetadataReceipt(player);
            Require(!string.IsNullOrEmpty(manifest.baselineManifestPath) && HashFile(manifest.baselineManifestPath) == manifest.baselineManifestSha256, "Baseline manifest hash mismatch.");
            BaselineManifest baseline = JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            Require(baseline != null && baseline.assemblies != null && baseline.baselineBuildId == expectedBaseline, "Baseline manifest identity evidence is incomplete.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(Candidates), "M04 candidate identity drifted.");
            Require(manifest.fixtures != null && manifest.fixtures.Length == 2 && manifest.fixtures.Any(f => f.patchId == "P01") && manifest.fixtures.Any(f => f.patchId == "P03"), "M04 requires P01 and P03 fixtures.");
            Require(player.assemblyIdentities != null && player.assemblyIdentities.Length > 0, "Linked Player assembly identities are required.");
            AssemblyIdentity mscorlib = player.assemblyIdentities.FirstOrDefault(item => string.Equals(item.name, "mscorlib", StringComparison.OrdinalIgnoreCase));
            Require(mscorlib != null && File.Exists(mscorlib.path) && HashFile(mscorlib.path) == mscorlib.sha256, "Linked mscorlib identity is not byte-bound.");
            foreach (Fixture fixture in manifest.fixtures)
            {
                fixture.patchManifest = Path.GetFullPath(fixture.patchManifest);
                fixture.patchRoot = Path.GetFullPath(fixture.patchDirectory);
                Require(File.Exists(fixture.patchManifest) && HashFile(fixture.patchManifest) == fixture.patchManifestSha256, "Fixture patch manifest hash mismatch: " + fixture.patchId);
                fixture.patch = JsonUtility.FromJson<PatchManifest>(File.ReadAllText(fixture.patchManifest));
                Require(fixture.patch != null && fixture.patch.closure != null, "Fixture patch closure missing: " + fixture.patchId);
                ValidateFixtureArtifacts(fixture, manifest, player, baseline);
            }
            return new Input { manifestPath = manifestPath, playerReceiptPath = playerPath, manifest = manifest, player = player, baseline = baseline, MscorlibPath = mscorlib.path, MscorlibSha256 = mscorlib.sha256, MscorlibFullName = mscorlib.fullName, MscorlibMvid = mscorlib.mvid };
        }

        private static void ValidateNativeMetadataReceipt(PlayerBuildReceipt player)
        {
            Require(!string.IsNullOrEmpty(player.nativeMetadataPath) && Path.IsPathRooted(player.nativeMetadataPath), "Native metadata path must be absolute.");
            string metadataPath = Path.GetFullPath(player.nativeMetadataPath);
            Require(File.Exists(metadataPath) && string.Equals(Path.GetFileName(metadataPath), "global-metadata.dat", StringComparison.Ordinal), "Native global metadata file is missing.");
            Require(IsHash(player.nativeMetadataSha256) && HashFile(metadataPath) == player.nativeMetadataSha256, "Native metadata hash mismatch.");
            Require(player.nativeMetadataVersion == 31, "Unsupported native metadata version; expected Unity 2022.3 metadata v31.");
            string[] metadataFiles = Directory.GetFiles(Application.dataPath, "global-metadata.dat", SearchOption.AllDirectories)
                .Select(Path.GetFullPath).ToArray();
            Require(metadataFiles.Length == 1 && string.Equals(metadataFiles[0], metadataPath, StringComparison.Ordinal), "Native metadata path is not the unique file under the executed Player data path.");
            Require(player.nativeAssemblyIdentities != null && player.nativeAssemblyIdentities.Length > 0, "Native assembly inventory is empty.");
            foreach (NativeAssemblyIdentity identity in player.nativeAssemblyIdentities)
            {
                Require(identity != null && identity.assemblyIndex >= 0 && identity.imageIndex >= 0 &&
                    !string.IsNullOrEmpty(identity.imageName) && !string.IsNullOrEmpty(identity.name) &&
                    !string.IsNullOrEmpty(identity.fullName), "Native assembly inventory contains an incomplete identity.");
            }
            Require(player.nativeGeneratedAssemblyNames != null && player.nativeGeneratedAssemblyNames.Length > 0 &&
                player.nativeGeneratedAssemblyNames.All(name => !string.IsNullOrEmpty(name)), "Native generated assembly inventory is empty.");
        }

        private static void ValidateFixtureArtifacts(Fixture fixture, FixtureManifest manifest, PlayerBuildReceipt player, BaselineManifest baseline)
        {
            Require(fixture.patch.patchId == fixture.patchId && fixture.patch.baselineBuildId == manifest.baselineBuildId && fixture.patch.runtimeAbiHash == manifest.runtimeAbiHash, "Fixture patch identity mismatch: " + fixture.patchId);
            string[] expected = fixture.patchId == "P01" ? new[] { Internal } : manifest.closureLoadOrder;
            Require(fixture.patch.loadOrder != null && fixture.patch.loadOrder.SequenceEqual(fixture.closureLoadOrder), "Fixture closure order mismatch: " + fixture.patchId);
            Require(fixture.closureLoadOrder != null && fixture.closureLoadOrder.SequenceEqual(expected), "Fixture closure membership mismatch: " + fixture.patchId);
            Require(fixture.assemblyIdentities != null && fixture.assemblyIdentities.Length == fixture.patch.closure.Length && fixture.assemblyIdentities.Select(item => item.name).SequenceEqual(fixture.assemblyIdentities.OrderBy(item => item.name, StringComparer.Ordinal).Select(item => item.name)), "Fixture identity order is not deterministic: " + fixture.patchId);
            foreach (PatchAssembly patch in fixture.patch.closure)
            {
                AssemblyIdentity identity = fixture.assemblyIdentities.Single(item => item.name == patch.name);
                BaselineAssembly baselineAssembly = baseline.assemblies.SingleOrDefault(item => item.name == patch.name);
                Require(baselineAssembly != null && identity.mvid == patch.mvid && identity.sha256 == patch.sha256 && patch.baselineMvid == baselineAssembly.mvid, "Fixture identity does not bind prelink baseline: " + patch.name);
                string dll = Path.GetFullPath(Path.Combine(fixture.patchRoot, patch.dll));
                Require(File.Exists(dll) && HashFile(dll) == patch.sha256, "Fixture DLL hash mismatch: " + patch.name);
                if (!string.IsNullOrEmpty(patch.pdb))
                {
                    string pdb = Path.GetFullPath(Path.Combine(fixture.patchRoot, patch.pdb));
                    Require(File.Exists(pdb) && HashFile(pdb) == patch.pdbSha256, "Fixture PDB hash mismatch: " + patch.name);
                }
            }
        }

        private static void RequireState(Result result, AssemblyShadowState expected, string phase)
        {
            AssemblyShadowState actual; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetState(out actual);
            result.stateCode = code.ToString(); result.state = actual.ToString();
            Require(code == AssemblyShadowErrorCode.Success && actual == expected, phase + " state mismatch: " + actual);
        }

        private static string Capture(Result result, string phase)
        {
            string json; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            result.diagnosticsCode = code.ToString();
            Require(code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json), "Fresh native diagnostics query failed: " + code);
            result.nativeDiagnosticsJson = json;
            AssemblyShadowDiagnostics diagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out diagnostics), "Fresh native diagnostics JSON is malformed.");
            result.snapshots.Add(new Snapshot { phase = phase, diagnostics = diagnostics });
            return code.ToString();
        }

        private static string Expect(Result result, string operation, AssemblyShadowErrorCode actual, AssemblyShadowErrorCode expected = AssemblyShadowErrorCode.Success)
        {
            result.checks.Add(new Check { name = operation, actual = actual.ToString(), expected = expected.ToString(), actualCode = (int)actual, expectedCode = (int)expected });
            Require(actual == expected, operation + " returned " + actual + ", expected " + expected);
            return actual.ToString();
        }

        private static int WriteEvidence(Result result)
        {
            try
            {
                string output = Path.GetFullPath(Argument("-shadowM04Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m04-" + result.mode + ".json")));
                string directory = Path.GetDirectoryName(output);
                Directory.CreateDirectory(directory);
                if (!string.IsNullOrEmpty(result.nativeDiagnosticsJson))
                {
                    string raw = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "-native-diagnostics.json");
                    WriteCreateNew(raw, result.nativeDiagnosticsJson);
                    result.rawDiagnosticsPath = raw; result.rawDiagnosticsSha256 = HashFile(raw);
                }
                WriteCreateNew(output, JsonUtility.ToJson(result, true));
                UnityEngine.Debug.Log("[AssemblyShadow M04] " + result.result + ": " + output);
                return result.result == "Passed" ? 0 : 1;
            }
            catch (Exception error) { UnityEngine.Debug.LogException(error); return 2; }
        }

        private static void WriteCreateNew(string path, string text)
        {
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(text ?? "");
        }

        private static Assembly LoadSimple(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA.Contracts");
                case Extensibility: return Assembly.Load("AssemblyA.Implementation.Extensibility");
                case Internal: return Assembly.Load("AssemblyA.Implementation.Internal");
                case ContractsConsumer: return Assembly.Load("AssemblyShadowDemo.ContractsConsumer");
                case ExtensibilityConsumer: return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer");
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Assembly LoadSuffixVariant(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA.Contracts.dll");
                case Extensibility: return Assembly.Load("AssemblyA.Implementation.Extensibility.dll");
                case Internal: return Assembly.Load("AssemblyA.Implementation.Internal.dll");
                case ContractsConsumer: return Assembly.Load("AssemblyShadowDemo.ContractsConsumer.dll");
                case ExtensibilityConsumer: return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer.dll");
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static string SuffixLiteral(string name)
        {
            switch (name)
            {
                case Contracts: return "AssemblyA.Contracts.dll";
                case Extensibility: return "AssemblyA.Implementation.Extensibility.dll";
                case Internal: return "AssemblyA.Implementation.Internal.dll";
                case ContractsConsumer: return "AssemblyShadowDemo.ContractsConsumer.dll";
                case ExtensibilityConsumer: return "AssemblyShadowDemo.ExtensibilityConsumer.dll";
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Assembly LoadCaseVariant(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("assemblya.contracts");
                case Extensibility: return Assembly.Load("assemblya.implementation.extensibility");
                case Internal: return Assembly.Load("assemblya.implementation.internal");
                case ContractsConsumer: return Assembly.Load("assemblyshadowdemo.contractsconsumer");
                case ExtensibilityConsumer: return Assembly.Load("assemblyshadowdemo.extensibilityconsumer");
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static string CaseLiteral(string name)
        {
            switch (name)
            {
                case Contracts: return "assemblya.contracts";
                case Extensibility: return "assemblya.implementation.extensibility";
                case Internal: return "assemblya.implementation.internal";
                case ContractsConsumer: return "assemblyshadowdemo.contractsconsumer";
                case ExtensibilityConsumer: return "assemblyshadowdemo.extensibilityconsumer";
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Type GetWitnessType(string name)
        {
            switch (name)
            {
                case Contracts: return Type.GetType("AssemblyA.Contracts.AssemblyAContractVersion, AssemblyA.Contracts", true);
                case Extensibility: return Type.GetType("AssemblyA.Implementation.Extensibility.VersionedComponentBase, AssemblyA.Implementation.Extensibility", true);
                case Internal: return Type.GetType("AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal", true);
                case ContractsConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.ContractsConsumer, AssemblyShadowDemo.ContractsConsumer", true);
                case ExtensibilityConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.DerivedExternalComponent, AssemblyShadowDemo.ExtensibilityConsumer", true);
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static string WitnessTypeLiteral(string name)
        {
            switch (name)
            {
                case Contracts: return "AssemblyA.Contracts.AssemblyAContractVersion, AssemblyA.Contracts";
                case Extensibility: return "AssemblyA.Implementation.Extensibility.VersionedComponentBase, AssemblyA.Implementation.Extensibility";
                case Internal: return "AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal";
                case ContractsConsumer: return "AssemblyShadowDemo.Consumers.ContractsConsumer, AssemblyShadowDemo.ContractsConsumer";
                case ExtensibilityConsumer: return "AssemblyShadowDemo.Consumers.DerivedExternalComponent, AssemblyShadowDemo.ExtensibilityConsumer";
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Assembly LoadByAssemblyName(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load(new AssemblyName("AssemblyA.Contracts"));
                case Extensibility: return Assembly.Load(new AssemblyName("AssemblyA.Implementation.Extensibility"));
                case Internal: return Assembly.Load(new AssemblyName("AssemblyA.Implementation.Internal"));
                case ContractsConsumer: return Assembly.Load(new AssemblyName("AssemblyShadowDemo.ContractsConsumer"));
                case ExtensibilityConsumer: return Assembly.Load(new AssemblyName("AssemblyShadowDemo.ExtensibilityConsumer"));
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Assembly LoadPathVariant(string name)
        {
            // These are literal path forms understood by the native name
            // parser. They do not read patch files from disk.
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA/AssemblyA.Contracts.dll");
                case Extensibility: return Assembly.Load("AssemblyA/AssemblyA.Implementation.Extensibility.dll");
                case Internal: return Assembly.Load("AssemblyA/AssemblyA.Implementation.Internal.dll");
                case ContractsConsumer: return Assembly.Load("Consumers/AssemblyShadowDemo.ContractsConsumer.dll");
                case ExtensibilityConsumer: return Assembly.Load("Consumers/AssemblyShadowDemo.ExtensibilityConsumer.dll");
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static string PathLiteral(string name)
        {
            switch (name)
            {
                case Contracts: return "AssemblyA/AssemblyA.Contracts.dll";
                case Extensibility: return "AssemblyA/AssemblyA.Implementation.Extensibility.dll";
                case Internal: return "AssemblyA/AssemblyA.Implementation.Internal.dll";
                case ContractsConsumer: return "Consumers/AssemblyShadowDemo.ContractsConsumer.dll";
                case ExtensibilityConsumer: return "Consumers/AssemblyShadowDemo.ExtensibilityConsumer.dll";
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static Assembly LoadBackslashPathVariant(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA\\AssemblyA.Contracts.dll");
                case Extensibility: return Assembly.Load("AssemblyA\\AssemblyA.Implementation.Extensibility.dll");
                case Internal: return Assembly.Load("AssemblyA\\AssemblyA.Implementation.Internal.dll");
                case ContractsConsumer: return Assembly.Load("Consumers\\AssemblyShadowDemo.ContractsConsumer.dll");
                case ExtensibilityConsumer: return Assembly.Load("Consumers\\AssemblyShadowDemo.ExtensibilityConsumer.dll");
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static string BackslashPathLiteral(string name)
        {
            switch (name)
            {
                case Contracts: return "AssemblyA\\AssemblyA.Contracts.dll";
                case Extensibility: return "AssemblyA\\AssemblyA.Implementation.Extensibility.dll";
                case Internal: return "AssemblyA\\AssemblyA.Implementation.Internal.dll";
                case ContractsConsumer: return "Consumers\\AssemblyShadowDemo.ContractsConsumer.dll";
                case ExtensibilityConsumer: return "Consumers\\AssemblyShadowDemo.ExtensibilityConsumer.dll";
                default: throw new ArgumentException("Unknown M04 candidate: " + name);
            }
        }
        private static bool ObjectEquals(object left, object right) { return object.ReferenceEquals(left, right); }
        private static string Argument(string name, string fallback) { string[] args = Environment.GetCommandLineArgs(); for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == name) return args[i + 1]; return fallback; }
        private static bool IsKnownMode(string mode) { return new[] { "T04-01", "T04-02", "T04-03", "T04-04", "T04-05", "T04-06", "T04-07", "T04-08", "T04-09-BenchmarkOn", "T04-10-BenchmarkOff" }.Contains(mode, StringComparer.Ordinal); }
        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }
        private static bool IsHash(string value) { return value != null && value.Length == 64 && value.All(c => (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')); }
        private static string HashFile(string path) { return Hash(File.ReadAllBytes(path)); }
        private static string Hash(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        private static string Token(AssemblyName name) { return BitConverter.ToString(name.GetPublicKeyToken() ?? new byte[0]).Replace("-", "").ToLowerInvariant(); }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        [Serializable, Preserve] public sealed class Result
        {
            [Preserve] public int schemaVersion, processId; [Preserve] public string milestone, mode, result, error; [Preserve] public bool il2cpp;
            [Preserve] public string unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            [Preserve] public string patchId, patchManifestPath, patchManifestSha256, compileSnapshotHash, rawDiagnosticsPath, rawDiagnosticsSha256, businessMarker, moduleMvidObservationPolicy;
            [Preserve] public string configure, begin, stage, validate, commit, abort, stateCode, state, executionModeCode, executionMode, diagnosticsCode, nativeDiagnosticsJson;
            [Preserve] public string[] stageOrder; [Preserve] public List<Check> checks; [Preserve] public List<Snapshot> snapshots;
            [Preserve] public List<AssemblyObservation> actualLogicalAssemblies, assemblyObservations; [Preserve] public List<LoadObservation> loadObservations;
            [Preserve] public List<ReferenceRow> refRows; [Preserve] public List<ExecutingWitness> executingWitnesses; [Preserve] public List<StageResult> stageResults;
            [Preserve] public Benchmark benchmark; [Preserve] public M04OrdinaryAssemblyProbe.Result ordinary;
        }

        [Serializable, Preserve] public sealed class FixtureManifest
        {
            [Preserve] public int schemaVersion; [Preserve] public string milestone, unityVersion, target, architecture, baselineManifestPath, baselineManifestSha256, baselineBuildId, runtimeAbiHash, baselineInputSnapshot, baselineInputSnapshotHash, stableAotProvenanceHash, stableAotProvenance;
            [Preserve] public string[] candidateNames, closureLoadOrder, stableAotNames; [Preserve] public Fixture[] fixtures;
        }
        [Serializable, Preserve] public sealed class PlayerBuildReceipt
        {
            [Preserve] public int schemaVersion; [Preserve] public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput, inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments, placeholderManifestPath, placeholderManifestSha256, nativeMetadataPath, nativeMetadataSha256; [Preserve] public int nativeMetadataVersion; [Preserve] public string[] placeholderAssemblyNames, nativeGeneratedAssemblyNames;
            [Preserve] public AssemblyIdentity[] assemblyIdentities; [Preserve] public NativeAssemblyIdentity[] nativeAssemblyIdentities;
        }
        [Serializable, Preserve] public sealed class NativeAssemblyIdentity
        {
            [Preserve] public int assemblyIndex;
            [Preserve] public int imageIndex;
            [Preserve] public uint token;
            [Preserve] public string imageName;
            [Preserve] public string name, fullName, version, culture, publicKeyToken;
        }
        [Serializable, Preserve] public sealed class Fixture
        {
            [Preserve] public string patchId, compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256; [Preserve] public string[] defines, changedRoots, closureLoadOrder, stableAotNames; [Preserve] public AssemblyIdentity[] assemblyIdentities;
            [Preserve, NonSerialized] internal string patchRoot; [Preserve, NonSerialized] internal PatchManifest patch;
        }
        [Serializable, Preserve] public sealed class AssemblyIdentity
        {
            [Preserve] public string name, fullName, version, culture, publicKeyToken, mvid, path, sha256; [Preserve] public ReferenceIdentity[] referenceIdentities;
        }
        [Serializable, Preserve] public sealed class ReferenceIdentity
        {
            [Preserve] public int referenceIndex; [Preserve] public string name, fullName, version, culture, publicKeyToken;
        }
        [Serializable, Preserve] public sealed class Check { [Preserve] public string name, actual, expected; [Preserve] public int actualCode, expectedCode; }
        [Serializable, Preserve] public sealed class Snapshot { [Preserve] public string phase; [Preserve] public AssemblyShadowDiagnostics diagnostics; }
        [Serializable, Preserve] public sealed class AssemblyObservation { [Preserve] public string name, fullName, mvid, executionCode, executionMode; [Preserve] public bool mvidAvailable, isInterpreter, logical; }
        [Serializable, Preserve] public sealed class LoadObservation { [Preserve] public string requested, overload, assemblyName; [Preserve] public bool sameAssembly; }
        [Serializable, Preserve] public sealed class ReferenceRow { [Preserve] public string assemblyName, name, fullName, version, culture, publicKeyToken; [Preserve] public int referenceIndex; }
        [Serializable, Preserve] public sealed class ExecutingWitness { [Preserve] public string assemblyName, executingAssemblyName; [Preserve] public bool sameAssembly; }
        [Serializable, Preserve] public sealed class StageResult { [Preserve] public string name, code, dllSha256, pdbSha256; }
        [Serializable, Preserve] public sealed class Benchmark { [Preserve] public bool enabled, finalSameAssembly, finalMvidAvailable; [Preserve] public int warmupCount, lookupCount; [Preserve] public long elapsedTicks, stopwatchFrequency, checksum; [Preserve] public string requestedName, finalAssemblyName, finalFullName, finalMvid; [Preserve] public string[] finalReferenceIdentities; }

        [Serializable, Preserve] private sealed class Input { [Preserve] public string manifestPath, playerReceiptPath, MscorlibPath, MscorlibSha256, MscorlibFullName, MscorlibMvid; [Preserve] public FixtureManifest manifest; [Preserve] public PlayerBuildReceipt player; [Preserve] public BaselineManifest baseline; }
        [Serializable, Preserve] private sealed class BaselineManifest { [Preserve] public string baselineBuildId; [Preserve] public BaselineAssembly[] assemblies; }
        [Serializable, Preserve] private sealed class BaselineAssembly { [Preserve] public string name, mvid; }
        [Serializable, Preserve] internal sealed class PatchManifest { [Preserve] public int schemaVersion, semanticHashSchema; [Preserve] public string patchId, baselineBuildId, runtimeAbiHash, compileSnapshotHash; [Preserve] public string[] loadOrder; [Preserve] public PatchAssembly[] closure; }
        [Serializable, Preserve] internal sealed class PatchAssembly { [Preserve] public string name, dll, sha256, pdb, pdbSha256, mvid, baselineMvid; }
    }
}
