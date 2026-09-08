using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// R01 native budget and startup-boundary experiments. Inputs are still
    /// validated by M07Probe's hash-bound fixture boundary; this class owns
    /// only the R01 operation order and evidence schema.
    /// </summary>
    [Preserve]
    public static class M07R01Probe
    {
        private const int ProfileVersion = 1;
        private const string InternalAssembly = "AssemblyA.Implementation.Internal";
        private const string InternalType = "AssemblyA.Implementation.Internal.InternalEntry";
        private const string CctorType = "AssemblyA.Implementation.Internal.M06ExecutionWitness";
        private const string OrdinaryImageName = "AssemblyShadowBaseline.HotUpdate";
        private const string OrdinaryGuardPrefix = "__AssemblyShadowReflectionBinding_";
        private const string PrefabBundleName = "versioned-prefab.bundle";
        private const string StartupObservationGap = "ObserveGap";
        private const string StartupEarlyGuard = "RequireEarlyGuard";
        private static readonly string[] Modes = {
            "R01-P03-Control", "R01-P03-OrdinaryFirst", "R01-P03-Oversize", "R01-P03-Mismatch",
            "R01-P03-OrdinaryAfterReserve",
            "R01-PreConfigure-Type", "R01-PreConfigure-Object", "R01-PreConfigure-Cctor",
            "R01-PreConfigure-NativePrefab", "R01-FeatureOff"
        };

        private static Result s_active;
        private static bool s_inputsReady;

        public static IEnumerator RunAndWriteCoroutine(string expectedBaselineBuildId, string expectedRuntimeAbiHash, Action<int> completed)
        {
            string mode = M07Probe.Argument("-shadowR01Mode", Modes[0]);
            string startupExpectation = M07Probe.Argument("-shadowR01StartupExpectation", StartupEarlyGuard);
            Result result = NewResult(mode, expectedBaselineBuildId, expectedRuntimeAbiHash, startupExpectation);
            s_active = result;
            s_inputsReady = false;
            try
            {
                M07Probe.Require(M07Probe.R00IsIl2CppPlayer(), "R01 acceptance requires an actual IL2CPP Player.");
                M07Probe.Require(Modes.Contains(mode, StringComparer.Ordinal), "Unknown R01 mode: " + mode);
                M07Probe.Require(startupExpectation == StartupObservationGap || startupExpectation == StartupEarlyGuard,
                    "Unknown R01 startup expectation: " + startupExpectation);
                string inputMode = mode == "R01-FeatureOff" ? "T07-14-FeatureOff" : "T07-03-FullClosure-P03";
                M07Probe.Input input = M07Probe.R00ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash, inputMode);
                s_inputsReady = true;
                BindInputs(result, input);

                if (mode == "R01-FeatureOff") RunFeatureOff(result);
                else if (mode == "R01-P03-Control") RunControl(result, input);
                else if (mode == "R01-P03-OrdinaryFirst") RunOrdinaryFirst(result, input);
                else if (mode == "R01-P03-Oversize") RunOversize(result, input);
                else if (mode == "R01-P03-Mismatch") RunMismatch(result, input);
                else if (mode == "R01-P03-OrdinaryAfterReserve") RunOrdinaryAfterReserve(result, input);
                else RunPreConfigure(result, input, mode, startupExpectation);

                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.result = "Failed";
                result.error = error.ToString();
                UnityEngine.Debug.LogException(error);
                if (s_inputsReady)
                {
                    try { CaptureDiagnostics(result, "failure"); }
                    catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
                    try { CaptureRecovery(result, "failure"); }
                    catch (Exception recoveryError) { result.error += "\nRecovery diagnostics: " + recoveryError; }
                }
            }

            try { WriteEvidence(result); }
            catch (Exception error)
            {
                result.result = "Failed";
                result.error += "\nEvidence write failed: " + error;
                UnityEngine.Debug.LogException(error);
                try { WriteEvidence(result); } catch (Exception retryError) { UnityEngine.Debug.LogException(retryError); }
            }
            if (completed != null) completed(result.result == "Passed" ? 0 : 1);
            yield break;
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            Result result = s_active;
            if (result == null) return 2;
            result.result = "Failed";
            result.error = error == null ? "R01 coroutine failed." : error.ToString();
            UnityEngine.Debug.LogException(error);
            if (s_inputsReady)
            {
                try { CaptureDiagnostics(result, "runner-failure"); } catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
                try { CaptureRecovery(result, "runner-failure"); } catch (Exception recoveryError) { result.error += "\nRecovery diagnostics: " + recoveryError; }
            }
            try { WriteEvidence(result); return 1; }
            catch (Exception writeError) { UnityEngine.Debug.LogException(writeError); return 2; }
        }

        private static void RunControl(Result result, M07Probe.Input input)
        {
            List<LoadedAssembly> closure = LoadClosure(result, input, -1, 0);
            long[] sizes = closure.Select(item => (long)item.actualDll.Length).ToArray();
            QueryCapacity(result, "before-configure", sizes, AssemblyShadowErrorCode.Success);
            ConfigureAndBegin(result, input);
            Reserve(result, sizes, AssemblyShadowErrorCode.Success);
            QueryCapacity(result, "after-reserve", sizes, AssemblyShadowErrorCode.Success);
            StageClosure(result, closure);
            Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "validated");
            Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "committed");
            CaptureDiagnostics(result, "committed");
            CaptureRecovery(result, "committed");
            CapturePhysicalWorld(result, "committed");
        }

        private static void RunOrdinaryFirst(Result result, M07Probe.Input input)
        {
            QueryCapacity(result, "before-ordinary", new long[0], AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity beforeOrdinary = LastCapacity(result);
            byte[] ordinaryBytes = LoadVerifiedOrdinaryImage(result, input, "ordinary-before-configure");
            MethodInfo ordinaryGuard = FindOrdinaryImageGuard();
            Assembly ordinary = (Assembly)ordinaryGuard.Invoke(null, new object[] { ordinaryBytes });
            result.observations.Add(new Observation {
                phase = "ordinary-before-configure", kind = "ordinary-interpreter-load",
                detail = ordinary.FullName, passed = ordinary.GetName().Name == "AssemblyShadowBaseline.HotUpdate"
            });
            M07Probe.Require(ordinary.GetName().Name == "AssemblyShadowBaseline.HotUpdate",
                "The verified ordinary hot-update image loaded an unexpected identity.");
            CaptureDiagnostics(result, "ordinary-before-configure");

            List<LoadedAssembly> closure = LoadClosure(result, input, -1, 0);
            long[] sizes = closure.Select(item => (long)item.actualDll.Length).ToArray();
            QueryCapacity(result, "after-ordinary-before-configure", sizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity afterOrdinary = LastCapacity(result);
            M07Probe.Require(afterOrdinary.ordinaryAllocatedCount > beforeOrdinary.ordinaryAllocatedCount,
                "The ordinary fixed-image load did not consume the shared ordinary image budget.");
            result.observations.Add(new Observation {
                phase = "after-ordinary-before-configure", kind = "shared-cursor-consumption",
                detail = beforeOrdinary.ordinaryAllocatedCount + "->" + afterOrdinary.ordinaryAllocatedCount,
                passed = true
            });
            ConfigureAndBegin(result, input);
            Reserve(result, sizes, AssemblyShadowErrorCode.Success);
            QueryCapacity(result, "after-reserve", sizes, AssemblyShadowErrorCode.Success);
            StageClosure(result, closure);
            Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "validated");
            Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "committed");
            CaptureDiagnostics(result, "committed");
            CaptureRecovery(result, "committed");
            CapturePhysicalWorld(result, "committed");
        }

        private static void RunOrdinaryAfterReserve(Result result, M07Probe.Input input)
        {
            List<LoadedAssembly> closure = LoadClosure(result, input, -1, 0);
            long[] sizes = closure.Select(item => (long)item.actualDll.Length).ToArray();
            QueryCapacity(result, "before-configure", sizes, AssemblyShadowErrorCode.Success);
            ConfigureAndBegin(result, input);
            Reserve(result, sizes, AssemblyShadowErrorCode.Success);
            QueryCapacity(result, "after-reserve", sizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity afterReserve = LastCapacity(result);

            byte[] ordinaryBytes = LoadVerifiedOrdinaryImage(result, input, "ordinary-after-reserve");
            Assembly ordinary = (Assembly)FindOrdinaryImageGuard().Invoke(null, new object[] { ordinaryBytes });
            M07Probe.Require(ordinary.GetName().Name == OrdinaryImageName,
                "The verified ordinary hot-update image loaded an unexpected identity after reservation.");
            CaptureDiagnostics(result, "ordinary-after-reserve");
            QueryCapacity(result, "after-ordinary-after-reserve", sizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity afterOrdinary = LastCapacity(result);
            M07Probe.Require(afterOrdinary.ordinaryAllocatedCount > afterReserve.ordinaryAllocatedCount &&
                afterOrdinary.shadowAllocatedCount == afterReserve.shadowAllocatedCount &&
                afterOrdinary.reservedImageCount == afterReserve.reservedImageCount &&
                !SameCursors(afterReserve.cursors, afterOrdinary.cursors),
                "The ordinary image did not consume a separate post-reservation cursor position.");
            result.observations.Add(new Observation {
                phase = "ordinary-after-reserve", kind = "reserved-slot-isolation",
                detail = "reserved=" + afterReserve.reservedImageCount + ";ordinary=" +
                    afterReserve.ordinaryAllocatedCount + "->" + afterOrdinary.ordinaryAllocatedCount,
                passed = true
            });

            StageClosure(result, closure);
            Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "validated");
            Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "committed");
            CaptureDiagnostics(result, "committed");
            CaptureRecovery(result, "committed");
            CapturePhysicalWorld(result, "committed");
        }

        private static void RunOversize(Result result, M07Probe.Input input)
        {
            List<LoadedAssembly> closure = LoadClosure(result, input, input.fixture.closureLoadOrder.Length - 1, 64L * 1024L * 1024L);
            long[] sizes = closure.Select(item => (long)item.actualDll.Length).ToArray();
            int lastIndex = sizes.Length - 1;
            QueryCapacity(result, "before-configure", sizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity capacity = LastCapacity(result);
            M07Probe.Require(!capacity.fits && capacity.firstFailingIndex == lastIndex && capacity.acceptedImages == (uint)lastIndex,
                "The oversize batch did not fail at its last ordered member during dry-run.");
            ConfigureAndBegin(result, input);
            AssemblyShadowMetadataCapacity beforeReserve = LastCapacity(result);
            Reserve(result, sizes, AssemblyShadowErrorCode.MetadataCapacityExceeded);
            QueryCapacity(result, "after-failed-reserve", sizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity afterReserve = LastCapacity(result);
            M07Probe.Require(SameCursors(beforeReserve.cursors, afterReserve.cursors) &&
                SameCursors(beforeReserve.finalCursors, afterReserve.finalCursors) &&
                afterReserve.acceptedImages == beforeReserve.acceptedImages && afterReserve.fits == false,
                "Failed whole-batch reservation changed shared cursors or accepted images.");
            M07Probe.Require(result.stageResults.Count == 0, "Oversize rejection reached Stage before publication.");
            Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "aborted");
            CaptureRecovery(result, "aborted");
            CaptureDiagnostics(result, "aborted");
        }

        private static void RunMismatch(Result result, M07Probe.Input input)
        {
            List<LoadedAssembly> closure = LoadClosure(result, input, 0, 0, true);
            long[] reservedSizes = closure.Select(item => item.originalDll.LongLength).ToArray();
            QueryCapacity(result, "before-configure", reservedSizes, AssemblyShadowErrorCode.Success);
            ConfigureAndBegin(result, input);
            Reserve(result, reservedSizes, AssemblyShadowErrorCode.Success);
            QueryCapacity(result, "after-reserve", reservedSizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity beforeStage = LastCapacity(result);
            LoadedAssembly mismatched = closure[0];
            AssemblyShadowErrorCode stageCode = AssemblyShadowRuntime.StageAssembly(mismatched.actualDll, mismatched.pdb);
            result.stageCode = stageCode.ToString();
            result.stageResults.Add(new StageResult {
                name = mismatched.name, code = stageCode.ToString(), dllSha256 = M07Probe.Hash(mismatched.actualDll),
                pdbSha256 = mismatched.pdb == null ? "" : M07Probe.Hash(mismatched.pdb), actualLength = mismatched.actualDll.LongLength
            });
            Expect(result, "stage-mismatched-length", stageCode, AssemblyShadowErrorCode.MetadataBudgetMismatch);
            QueryCapacity(result, "after-mismatch", reservedSizes, AssemblyShadowErrorCode.Success);
            AssemblyShadowMetadataCapacity afterStage = LastCapacity(result);
            M07Probe.Require(SameCursors(beforeStage.cursors, afterStage.cursors),
                "Budget mismatch consumed an additional owner/index allocation.");
            Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "aborted");
            CaptureRecovery(result, "aborted");
            CaptureDiagnostics(result, "aborted");
        }

        private static void RunPreConfigure(Result result, M07Probe.Input input, string mode, string startupExpectation)
        {
            string observation = mode.Substring("R01-PreConfigure-".Length);
            CaptureDiagnostics(result, "before-preconfigure-observation");
            if (observation == "Type") ObserveType(result);
            else if (observation == "Object") ObserveObject(result);
            else if (observation == "Cctor") ObserveCctor(result);
            else if (observation == "NativePrefab") ObserveNativePrefab(result, input);
            else throw new InvalidOperationException("Unknown R01 pre-Configure observation: " + observation);
            CaptureDiagnostics(result, "after-preconfigure-observation");

            List<LoadedAssembly> closure = LoadClosure(result, input, -1, 0);
            long[] sizes = closure.Select(item => (long)item.actualDll.Length).ToArray();
            QueryCapacity(result, "after-preconfigure-observation", sizes, AssemblyShadowErrorCode.Success);
            ConfigureAndBegin(result, input);
            Reserve(result, sizes, AssemblyShadowErrorCode.Success);
            StageClosure(result, closure);
            AssemblyShadowErrorCode validateCode = AssemblyShadowRuntime.ValidateTransaction();
            AssemblyShadowErrorCode expected = startupExpectation == StartupEarlyGuard
                ? AssemblyShadowErrorCode.BaselineAlreadyUsed : AssemblyShadowErrorCode.Success;
            Expect(result, "validate-after-preconfigure-use", validateCode, expected);
            CaptureState(result, "validated-or-early-guard");
            result.observations.Add(new Observation {
                phase = "preconfigure-result", kind = observation, detail = validateCode.ToString(),
                passed = validateCode == expected
            });
            Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.Success);
            CaptureState(result, "aborted");
            CaptureRecovery(result, "aborted");
            CaptureDiagnostics(result, "aborted");
        }

        private static void RunFeatureOff(Result result)
        {
            string json;
            result.capacityCode = AssemblyShadowRuntime.GetMetadataCapacityJson(new long[0], out json).ToString();
            result.capacityJson = json;
            AddCheck(result, "capacity-feature-off", result.capacityCode, AssemblyShadowErrorCode.FeatureDisabled.ToString(),
                result.capacityCode == AssemblyShadowErrorCode.FeatureDisabled.ToString() && json == null);
            result.reserveCode = AssemblyShadowRuntime.ReserveMetadataBudget(new long[0], ProfileVersion).ToString();
            AddCheck(result, "reserve-feature-off", result.reserveCode, AssemblyShadowErrorCode.FeatureDisabled.ToString(),
                result.reserveCode == AssemblyShadowErrorCode.FeatureDisabled.ToString());
            result.recoveryCode = AssemblyShadowRuntime.GetRecoveryInfoJson(out json).ToString();
            result.recoveryJson = json;
            AddCheck(result, "recovery-feature-off", result.recoveryCode, AssemblyShadowErrorCode.FeatureDisabled.ToString(),
                result.recoveryCode == AssemblyShadowErrorCode.FeatureDisabled.ToString() && json == null);
            AssemblyShadowState state;
            result.stateCode = AssemblyShadowRuntime.GetState(out state).ToString();
            result.state = state.ToString();
            AddCheck(result, "state-feature-off", result.stateCode, AssemblyShadowErrorCode.FeatureDisabled.ToString(),
                result.stateCode == AssemblyShadowErrorCode.FeatureDisabled.ToString());
            result.observations.Add(new Observation { phase = "feature-off", kind = "capability", detail = "no fabricated budget or recovery JSON", passed = true });
        }

        private static void ObserveType(Result result)
        {
            Assembly assembly = Assembly.Load(InternalAssembly);
            Type type = assembly.GetType(InternalType, true);
            result.observations.Add(new Observation {
                phase = "before-configure", kind = "type", detail = type.AssemblyQualifiedName,
                assemblyName = assembly.GetName().Name, passed = assembly.GetName().Name == InternalAssembly
            });
        }

        private static void ObserveObject(Result result)
        {
            Assembly assembly = Assembly.Load(InternalAssembly);
            Type type = assembly.GetType("AssemblyA.Implementation.Internal.M06ExecutionWitness+M06InternalNode", true);
            object value = Activator.CreateInstance(type);
            result.observations.Add(new Observation {
                phase = "before-configure", kind = "object", detail = value.GetType().AssemblyQualifiedName,
                assemblyName = value.GetType().Assembly.GetName().Name, passed = value != null
            });
        }

        private static void ObserveCctor(Result result)
        {
            Assembly assembly = Assembly.Load(InternalAssembly);
            Type type = assembly.GetType(CctorType, true);
            MethodInfo evidenceMethod = type.GetMethod("GetModuleEvidence", BindingFlags.Public | BindingFlags.Static);
            string[] evidence = (string[])evidenceMethod.Invoke(null, null);
            string cctor = evidence.Single(value => value.StartsWith("cctor=", StringComparison.Ordinal));
            result.observations.Add(new Observation {
                phase = "before-configure", kind = "cctor", detail = string.Join(";", evidence),
                assemblyName = assembly.GetName().Name, passed = cctor == "cctor=1"
            });
            M07Probe.Require(cctor == "cctor=1", "The fixed cctor witness did not report exactly one initialization.");
        }

        private static void ObserveNativePrefab(Result result, M07Probe.Input input)
        {
            string bundlePath = M07Probe.Confined(input.resourceRoot, "Bundles/" + PrefabBundleName);
            CaptureDiagnostics(result, "before-native-prefab-load");
            AssetBundle bundle = AssetBundle.LoadFromFile(bundlePath);
            M07Probe.Require(bundle != null, "The baseline prefab bundle could not be loaded before Configure.");
            try
            {
                string assetName = bundle.GetAllAssetNames().Single();
                GameObject asset = bundle.LoadAsset<GameObject>(assetName);
                // Capture native evidence before managed component/type inspection can record another use.
                CaptureDiagnostics(result, "after-native-prefab-load");
                result.observations.Add(new Observation {
                    phase = "before-configure", kind = "native-prefab-direct", detail = assetName,
                    path = bundlePath, passed = asset != null,
                    assemblyName = asset == null ? "" : "baseline-asset-bundle-direct"
                });
                M07Probe.Require(asset != null, "The baseline prefab asset did not load through the direct AssetBundle path.");
                Component candidate = asset.GetComponents<Component>().FirstOrDefault(component => component != null &&
                    component.GetType().FullName == "AssemblyA.Implementation.Internal.VersionedPrefabComponent");
                M07Probe.Require(candidate != null, "The loaded prefab did not resolve its candidate script component.");
                Type componentType = candidate.GetType();
                M07Probe.Require(componentType.Assembly.GetName().Name == InternalAssembly, "The prefab candidate component came from another assembly.");
                result.observations.Add(new Observation {
                    phase = "after-native-prefab-capture", kind = "native-prefab-component",
                    detail = componentType.FullName, assemblyName = componentType.Assembly.GetName().Name, passed = true
                });
            }
            finally { bundle.Unload(false); }
        }

        private static MethodInfo FindOrdinaryImageGuard()
        {
            MethodInfo[] guards = typeof(AssemblyShadowBaseline.BaselineBootstrap)
                .GetMethods(BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Where(method => method.Name.StartsWith(OrdinaryGuardPrefix, StringComparison.Ordinal))
                .ToArray();
            M07Probe.Require(guards.Length == 1, "The fixed ordinary-image guard is missing or ambiguous.");
            MethodInfo guard = guards[0];
            M07Probe.Require(guard.ReturnType == typeof(Assembly) && guard.GetParameters().Length == 1 &&
                guard.GetParameters()[0].ParameterType == typeof(byte[]),
                "The fixed ordinary-image guard signature differs from the M00 contract.");
            return guard;
        }

        private static byte[] LoadVerifiedOrdinaryImage(Result result, M07Probe.Input input, string phase)
        {
            M07R01OrdinarySnapshotBinding.VerifiedImage verified = M07R01OrdinarySnapshotBinding.LoadVerifiedImage(
                input.player.inputSnapshot, input.player.inputSnapshotHash, input.player.buildGuid,
                input.player.playerOutput, input.player.nativeLibraryPath, input.player.nativeLibrarySha256,
                M07Probe.Argument(M07R01OrdinarySnapshotBinding.RawReceiptSha256Argument, ""), OrdinaryImageName);
            byte[] bytes = verified.bytes;
            result.byteInputs.Add(new ByteInputObservation {
                phase = phase, assemblyName = OrdinaryImageName, path = verified.path,
                originalLength = bytes.LongLength, actualLength = bytes.LongLength,
                originalSha256 = M07Probe.Hash(bytes), actualSha256 = M07Probe.Hash(bytes),
                transformation = "verified ON snapshot filtered ordinary image; M00 fixed guard; no padding"
            });
            return bytes;
        }

        private static void ConfigureAndBegin(Result result, M07Probe.Input input)
        {
            CaptureDiagnostics(result, "before-configure");
            Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(
                input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames), AssemblyShadowErrorCode.Success);
            CaptureState(result, "configured");
            CaptureDiagnostics(result, "configured");
            Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(
                input.fixture.patchId, input.manifest.baselineBuildId, input.fixture.closureLoadOrder, M07Probe.RuntimeAbiVersion), AssemblyShadowErrorCode.Success);
            CaptureState(result, "begun");
        }

        private static void Reserve(Result result, long[] sizes, AssemblyShadowErrorCode expected)
        {
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.ReserveMetadataBudget(sizes, ProfileVersion);
            result.reserveCode = code.ToString();
            AddCheck(result, "reserve", result.reserveCode, expected.ToString(), code == expected);
            M07Probe.Require(code == expected, "R01 reserve returned " + code + ", expected " + expected + ".");
        }

        private static void StageClosure(Result result, List<LoadedAssembly> closure)
        {
            foreach (LoadedAssembly item in closure)
            {
                AssemblyShadowErrorCode code = AssemblyShadowRuntime.StageAssembly(item.actualDll, item.pdb);
                result.stageCode = code.ToString();
                result.stageResults.Add(new StageResult {
                    name = item.name, code = code.ToString(), dllSha256 = M07Probe.Hash(item.actualDll),
                    pdbSha256 = item.pdb == null ? "" : M07Probe.Hash(item.pdb), actualLength = item.actualDll.LongLength
                });
                Expect(result, "stage-" + item.name, code, AssemblyShadowErrorCode.Success);
            }
            result.stageOrder = closure.Select(item => item.name).ToArray();
            CaptureState(result, "staged");
        }

        private static List<LoadedAssembly> LoadClosure(Result result, M07Probe.Input input, int expandedIndex, long expandedLength, bool padOneByte = false)
        {
            var values = new List<LoadedAssembly>();
            for (int index = 0; index < input.fixture.closureLoadOrder.Length; ++index)
            {
                string name = input.fixture.closureLoadOrder[index];
                M07Probe.PatchAssembly assembly = input.patch.closure.Single(item => item.name == name);
                string path = M07Probe.Confined(input.fixture.patchDirectory, assembly.dll);
                byte[] original = File.ReadAllBytes(path);
                M07Probe.Require(M07Probe.Hash(original) == assembly.sha256, "Verified closure bytes changed: " + name);
                byte[] actual = original;
                string transformation = "verified closure bytes";
                if (index == expandedIndex)
                {
                    long targetLength = padOneByte ? checked(original.LongLength + 1) : expandedLength;
                    M07Probe.Require(targetLength >= original.LongLength, "Expanded test length is shorter than the verified input.");
                    actual = new byte[checked((int)targetLength)];
                    Buffer.BlockCopy(original, 0, actual, 0, original.Length);
                    transformation = padOneByte ? "one-byte zero-padding" : "zero-padding-to-64MiB";
                }
                result.byteInputs.Add(new ByteInputObservation {
                    phase = "closure", assemblyName = name, path = path,
                    originalLength = original.LongLength, actualLength = actual.LongLength,
                    originalSha256 = M07Probe.Hash(original), actualSha256 = M07Probe.Hash(actual), transformation = transformation
                });
                byte[] pdb = string.IsNullOrEmpty(assembly.pdb) ? null : File.ReadAllBytes(M07Probe.Confined(input.fixture.patchDirectory, assembly.pdb));
                values.Add(new LoadedAssembly { name = name, actualDll = actual, originalDll = original, pdb = pdb });
            }
            return values;
        }

        private static void QueryCapacity(Result result, string phase, long[] sizes, AssemblyShadowErrorCode expected)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetMetadataCapacityJson(sizes, out json);
            var observation = new CapacityObservation {
                phase = phase, orderedSizes = (long[])sizes.Clone(), code = code.ToString(), rawJson = json,
                parsed = false, fits = false, firstFailingIndex = -1
            };
            result.capacitySnapshots.Add(observation);
            result.capacityCode = code.ToString();
            result.capacityJson = json;
            if (code == AssemblyShadowErrorCode.Success)
            {
                AssemblyShadowMetadataCapacity capacity;
                M07Probe.Require(AssemblyShadowMetadataCapacity.TryParse(json, out capacity),
                    "R01 metadata capacity JSON is malformed at " + phase + ".");
                observation.parsed = true;
                observation.profileVersion = capacity.profileVersion;
                observation.indexBits = capacity.indexBits;
                observation.kindBits = capacity.kindBits;
                observation.cursors = capacity.cursors;
                observation.finalCursors = capacity.finalCursors;
                observation.remainingSlots = capacity.remainingSlots;
                observation.requiredImages = capacity.requiredImages;
                observation.acceptedImages = capacity.acceptedImages;
                observation.firstFailingIndex = capacity.firstFailingIndex;
                observation.firstFailingSize = capacity.firstFailingSize;
                observation.failureReason = capacity.failureReason;
                observation.fits = capacity.fits;
                observation.ordinaryAllocatedCount = capacity.ordinaryAllocatedCount;
                observation.shadowAllocatedCount = capacity.shadowAllocatedCount;
                observation.reservedImageCount = capacity.reservedImageCount;
            }
            AddCheck(result, "capacity-" + phase, code.ToString(), expected.ToString(), code == expected);
            M07Probe.Require(code == expected, "R01 metadata capacity query returned " + code + ", expected " + expected + ".");
        }

        private static AssemblyShadowMetadataCapacity LastCapacity(Result result)
        {
            CapacityObservation observation = result.capacitySnapshots.Last();
            M07Probe.Require(observation.parsed && !string.IsNullOrEmpty(observation.rawJson), "R01 capacity snapshot was not parsed.");
            AssemblyShadowMetadataCapacity value;
            M07Probe.Require(AssemblyShadowMetadataCapacity.TryParse(observation.rawJson, out value), "R01 capacity snapshot cannot be reparsed.");
            return value;
        }

        private static void CaptureState(Result result, string phase)
        {
            AssemblyShadowState state;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetState(out state);
            result.stateCode = code.ToString(); result.state = state.ToString();
            result.stateSnapshots.Add(new StateSnapshot { phase = phase, code = code.ToString(), state = state.ToString(), passed = code == AssemblyShadowErrorCode.Success });
            M07Probe.Require(code == AssemblyShadowErrorCode.Success, "R01 state query failed at " + phase + ": " + code);
        }

        private static void CaptureRecovery(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetRecoveryInfoJson(out json);
            result.recoveryCode = code.ToString(); result.recoveryJson = json;
            result.recoverySnapshots.Add(new RecoverySnapshot { phase = phase, code = code.ToString(), rawJson = json, parsed = false });
            M07Probe.Require(code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json),
                "R01 recovery query failed at " + phase + ": " + code + ".");
            AssemblyShadowRecoveryInfo info;
            M07Probe.Require(AssemblyShadowRecoveryInfo.TryParse(json, out info), "R01 recovery JSON is malformed at " + phase + ".");
            RecoverySnapshot snapshot = result.recoverySnapshots.Last();
            snapshot.parsed = true; snapshot.stateCode = info.stateCode; snapshot.state = info.state;
            snapshot.published = info.published; snapshot.abortAllowed = info.abortAllowed;
            snapshot.dispositionCode = info.dispositionCode; snapshot.disposition = info.disposition;
            snapshot.terminalFailureCode = info.terminalFailureCode;
            snapshot.retainedBytes = info.retainedBytes;
            snapshot.baselineEligibilityRequiresStartupValidation = info.baselineEligibilityRequiresStartupValidation;
            if (phase == "committed")
            {
                M07Probe.Require(info.state == "Committed" && info.published && !info.abortAllowed &&
                    info.disposition == "ActiveShadow" && !info.baselineEligibilityRequiresStartupValidation,
                    "R01 committed recovery disposition is not ActiveShadow.");
            }
            else if (phase == "aborted")
            {
                M07Probe.Require(info.state == "Aborted" && !info.published && !info.abortAllowed &&
                    info.disposition == "BaselineEligibleAfterAbort" && info.baselineEligibilityRequiresStartupValidation,
                    "R01 aborted recovery disposition is not BaselineEligibleAfterAbort.");
            }
        }

        private static void CaptureDiagnostics(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            result.diagnosticsCode = code.ToString(); result.nativeDiagnosticsJson = json;
            result.diagnosticSnapshots.Add(new DiagnosticSnapshot { phase = phase, code = code.ToString(), rawJson = json, parsed = !string.IsNullOrEmpty(json) });
        }

        private static void CapturePhysicalWorld(Result result, string phase)
        {
            foreach (string name in M07Probe.Candidates)
            {
                AssemblyExecutionMode mode;
                AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                bool expectedShadow = result.stageOrder != null && result.stageOrder.Contains(name, StringComparer.Ordinal);
                bool passed = expectedShadow
                    ? code == AssemblyShadowErrorCode.Success && mode == AssemblyExecutionMode.InterpreterShadow
                    : (code == AssemblyShadowErrorCode.Success && mode == AssemblyExecutionMode.AotBaseline) ||
                        code == AssemblyShadowErrorCode.CandidateNotRegistered;
                result.physicalWorld.Add(new PhysicalWorldObservation { phase = phase, assemblyName = name, code = code.ToString(), mode = mode.ToString(), passed = passed });
                M07Probe.Require(passed, "R01 physical execution mode differs for " + name + ": " + code + ":" + mode);
            }
        }

        private static void Expect(Result result, string operation, AssemblyShadowErrorCode actual, AssemblyShadowErrorCode expected)
        {
            AddCheck(result, operation, actual.ToString(), expected.ToString(), actual == expected);
            M07Probe.Require(actual == expected, "R01 " + operation + " returned " + actual + ", expected " + expected + ".");
            if (operation == "configure") result.configureCode = actual.ToString();
            else if (operation == "begin") result.beginCode = actual.ToString();
            else if (operation == "validate" || operation == "validate-after-preconfigure-use") result.validateCode = actual.ToString();
            else if (operation == "commit") result.commitCode = actual.ToString();
            else if (operation == "abort") result.abortCode = actual.ToString();
        }

        private static void AddCheck(Result result, string name, string actual, string expected, bool passed)
        {
            result.checks.Add(new Check { name = name, actual = actual, expected = expected, passed = passed });
            M07Probe.Require(passed, "R01 check failed: " + name + "; actual=" + actual + "; expected=" + expected);
        }

        private static bool SameCursors(uint[] left, uint[] right)
        {
            return left != null && right != null && left.SequenceEqual(right);
        }

        private static Result NewResult(string mode, string baseline, string runtimeAbi, string startupExpectation)
        {
            return new Result {
                schemaVersion = 1, milestone = "M07R-R01", mode = mode, result = "Failed", error = "",
                il2cpp = M07Probe.R00IsIl2CppPlayer(), processId = Process.GetCurrentProcess().Id,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, baselineBuildId = baseline, runtimeAbiHash = runtimeAbi,
                profileVersion = ProfileVersion, startupExpectation = startupExpectation,
                checks = new List<Check>(), stageResults = new List<StageResult>(), capacitySnapshots = new List<CapacityObservation>(),
                stateSnapshots = new List<StateSnapshot>(), recoverySnapshots = new List<RecoverySnapshot>(), diagnosticSnapshots = new List<DiagnosticSnapshot>(),
                observations = new List<Observation>(), physicalWorld = new List<PhysicalWorldObservation>(), byteInputs = new List<ByteInputObservation>()
            };
        }

        private static void BindInputs(Result result, M07Probe.Input input)
        {
            result.fixtureManifestPath = input.manifestPath; result.fixtureManifestSha256 = M07Probe.HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath; result.playerBuildReceiptSha256 = M07Probe.HashFile(input.playerReceiptPath);
            result.baselineManifestPath = input.manifest.baselineManifestPath; result.baselineManifestSha256 = input.manifest.baselineManifestSha256;
            result.patchId = input.fixture == null ? "" : input.fixture.patchId;
            result.patchManifestPath = input.fixture == null ? "" : input.fixture.patchManifest;
            result.patchManifestSha256 = input.fixture == null ? "" : input.fixture.patchManifestSha256;
            result.target = input.manifest.target; result.architecture = input.manifest.architecture;
            result.playerInputSnapshot = input.player.inputSnapshot; result.playerInputSnapshotSha256 = input.player.inputSnapshotHash;
            result.nativeLibraryPath = input.player.nativeLibraryPath; result.nativeLibrarySha256 = input.player.nativeLibrarySha256;
            result.nativeMetadataPath = input.player.nativeMetadataPath; result.nativeMetadataSha256 = input.player.nativeMetadataSha256;
            result.candidateNames = (string[])input.manifest.candidateNames.Clone();
            result.closureLoadOrder = input.fixture == null ? new string[0] : (string[])input.fixture.closureLoadOrder.Clone();
        }

        private static void WriteEvidence(Result result)
        {
            string output = Path.GetFullPath(M07Probe.Argument("-shadowR01Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/r01-" + result.mode + ".json")));
            string directory = Path.GetDirectoryName(output);
            Directory.CreateDirectory(directory);
            result.resultPath = output;
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream)) writer.Write(JsonUtility.ToJson(result, true));
            UnityEngine.Debug.Log("[AssemblyShadow M07R-R01] " + JsonUtility.ToJson(result));
        }

        private sealed class LoadedAssembly { public string name; public byte[] originalDll, actualDll, pdb; }

        [Serializable, Preserve] public sealed class Result
        {
            [Preserve] public int schemaVersion, processId, profileVersion;
            [Preserve] public string milestone, mode, result, error, startupExpectation, unityVersion, platform, buildGuid, playerDataPath;
            [Preserve] public string baselineBuildId, runtimeAbiHash, target, architecture, resultPath;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, patchId, patchManifestPath, patchManifestSha256;
            [Preserve] public string playerInputSnapshot, playerInputSnapshotSha256, nativeLibraryPath, nativeLibrarySha256, nativeMetadataPath, nativeMetadataSha256;
            [Preserve] public string configureCode, beginCode, reserveCode, stageCode, validateCode, commitCode, abortCode, stateCode, state;
            [Preserve] public string capacityCode, capacityJson, recoveryCode, recoveryJson, diagnosticsCode, nativeDiagnosticsJson;
            [Preserve] public bool il2cpp;
            [Preserve] public string[] candidateNames, closureLoadOrder, stageOrder;
            [Preserve] public List<Check> checks; [Preserve] public List<StageResult> stageResults;
            [Preserve] public List<CapacityObservation> capacitySnapshots; [Preserve] public List<StateSnapshot> stateSnapshots;
            [Preserve] public List<RecoverySnapshot> recoverySnapshots; [Preserve] public List<DiagnosticSnapshot> diagnosticSnapshots;
            [Preserve] public List<Observation> observations; [Preserve] public List<PhysicalWorldObservation> physicalWorld;
            [Preserve] public List<ByteInputObservation> byteInputs;
        }

        [Serializable, Preserve] public sealed class Check { [Preserve] public string name, actual, expected; [Preserve] public bool passed; }
        [Serializable, Preserve] public sealed class StageResult { [Preserve] public string name, code, dllSha256, pdbSha256; [Preserve] public long actualLength; }
        [Serializable, Preserve] public sealed class CapacityObservation
        {
            [Preserve] public string phase, code, rawJson, failureReason; [Preserve] public long[] orderedSizes;
            [Preserve] public bool parsed, fits; [Preserve] public int profileVersion, indexBits, kindBits, firstFailingIndex;
            [Preserve] public ulong firstFailingSize; [Preserve] public uint[] cursors, finalCursors, remainingSlots;
            [Preserve] public uint requiredImages, acceptedImages;
            [Preserve] public ulong ordinaryAllocatedCount, shadowAllocatedCount, reservedImageCount;
        }
        [Serializable, Preserve] public sealed class StateSnapshot { [Preserve] public string phase, code, state; [Preserve] public bool passed; }
        [Serializable, Preserve] public sealed class RecoverySnapshot
        {
            [Preserve] public string phase, code, rawJson, state, disposition, reason; [Preserve] public bool parsed, published, abortAllowed, baselineEligibilityRequiresStartupValidation;
            [Preserve] public int stateCode, dispositionCode, terminalFailureCode; [Preserve] public ulong retainedBytes;
        }
        [Serializable, Preserve] public sealed class DiagnosticSnapshot { [Preserve] public string phase, code, rawJson; [Preserve] public bool parsed; }
        [Serializable, Preserve] public sealed class Observation
        {
            [Preserve] public string phase, kind, detail, path, assemblyName; [Preserve] public bool passed;
        }
        [Serializable, Preserve] public sealed class PhysicalWorldObservation
        {
            [Preserve] public string phase, assemblyName, code, mode; [Preserve] public bool passed;
        }
        [Serializable, Preserve] public sealed class ByteInputObservation
        {
            [Preserve] public string phase, assemblyName, path, originalSha256, actualSha256, transformation;
            [Preserve] public long originalLength, actualLength;
        }

    }
}
