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
    /// R00-only performance observation boundary. M07 owns input and
    /// transaction validation; this companion owns the distinct R00 result
    /// schema and the bounded managed witness measurements.
    /// </summary>
    [Preserve]
    public static class M07R00PerformanceProbe
    {
        private const string InternalAssembly = "AssemblyA.Implementation.Internal";
        private const string WitnessTypeName = "AssemblyA.Implementation.Internal.R00PerformanceWitness";
        private const int WarmupCount = 100;
        private const int RepeatedCount = 10000;
        private static readonly string[] Modes = { "R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03", "R00-OFF-NoPatch" };

        private static Result s_active;
        private static bool s_inputsReady;

        public static IEnumerator RunAndWriteCoroutine(string expectedBaselineBuildId, string expectedRuntimeAbiHash, Action<int> completed)
        {
            string mode = M07Probe.Argument("-shadowR00Mode", Modes[0]);
            Result result = NewResult(mode, expectedBaselineBuildId, expectedRuntimeAbiHash);
            s_active = result;
            s_inputsReady = false;
            long invocationTimestamp = Stopwatch.GetTimestamp();
            long invocationUtcTicks = DateTime.UtcNow.Ticks;
            result.readiness = CaptureReadiness(invocationTimestamp, invocationUtcTicks, false);

            M07Probe.Require(M07Probe.R00IsIl2CppPlayer(), "R00 acceptance requires an actual IL2CPP Player.");
            M07Probe.Require(Modes.Contains(mode, StringComparer.Ordinal), "Unknown R00 mode: " + mode);

            bool featureEnabled = mode != "R00-OFF-NoPatch";
            string inputMode = mode == "R00-OFF-NoPatch" ? "T07-14-FeatureOff" :
                mode == "R00-ON-P03" ? "T07-03-FullClosure-P03" : "T07-01-Prefab-P01";
            M07Probe.Input input = M07Probe.R00ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash, inputMode);
            s_inputsReady = true;
            result.featureEnabled = featureEnabled;
            BindInputs(result, input);

            if (mode == "R00-ON-NoPatch")
            {
                // ReadInputs validates the real M07 P01-bound manifest and
                // receipt before this world is deliberately reduced to an
                // ON/no-patch observation.
                input.fixture = null;
                input.patch = null;
                result.patchId = "";
                result.patchManifest = new ArtifactReceipt { name = "patch-manifest", available = false };
            }

            if (featureEnabled)
            {
                if (input.fixture == null)
                {
                    result.configureCode = M07Probe.Expect(result.m07Transaction, "configure", AssemblyShadowRuntime.ConfigureCandidates(
                        input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
                    AssemblyShadowState state;
                    AssemblyShadowErrorCode stateCode = AssemblyShadowRuntime.GetState(out state);
                    AddCheck(result, "configured-state", stateCode == AssemblyShadowErrorCode.Success && state == AssemblyShadowState.CandidatesRegistered,
                        stateCode + ":" + state, "Success:CandidatesRegistered");
                    M07Probe.Require(stateCode == AssemblyShadowErrorCode.Success && state == AssemblyShadowState.CandidatesRegistered,
                        "R00 ON/no-patch did not remain in CandidatesRegistered state.");
                    result.stateCode = stateCode.ToString();
                    result.state = state.ToString();
                    result.stageOrder = new string[0];
                }
                else
                {
                    M07Probe.R00RunTransaction(result.m07Transaction, input);
                    CopyTransaction(result);
                    result.transactionCommitted = true;
                }
            }
            else
            {
                M07Probe.Require(input.fixture == null, "R00 OFF world unexpectedly selected a patch fixture.");
                M07Probe.R00RunFeatureOff(result.m07Transaction);
                CopyTransaction(result);
            }

            CaptureDiagnostics(result, "before-benchmark");
            result.selectedType = CaptureSelectedType(result, mode);
            result.readiness = CaptureReadiness(invocationTimestamp, invocationUtcTicks, true);
            yield return null;
            RunWitnessBenchmarks(result, mode);
            RunExistingExecutionRegressions(result);
            CaptureDiagnostics(result, "after-benchmark");
            result.result = "Passed";

            int exitCode;
            try { WriteEvidence(result); exitCode = 0; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); exitCode = 2; }
            if (completed != null) completed(exitCode);
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            Result result = s_active;
            if (result == null) return 2;
            result.result = "Failed";
            result.error = error == null ? "R00 coroutine failed." : error.ToString();
            UnityEngine.Debug.LogException(error);
            if (s_inputsReady)
            {
                try { CaptureDiagnostics(result, "failure"); }
                catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
            }
            try { WriteEvidence(result); return 1; }
            catch (Exception writeError) { UnityEngine.Debug.LogException(writeError); return 2; }
        }

        private static Result NewResult(string mode, string baseline, string runtimeAbi)
        {
            return new Result {
                schemaVersion = 1, milestone = "M07R-R00", mode = mode, result = "Failed", error = "",
                il2cpp = M07Probe.R00IsIl2CppPlayer(), processId = Process.GetCurrentProcess().Id,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, baselineBuildId = baseline, runtimeAbiHash = runtimeAbi,
                assertions = new List<Assertion>(), operations = new List<OperationObservation>(),
                patchManifest = new ArtifactReceipt { name = "patch-manifest", available = false },
                m07Transaction = M07Probe.R00NewResult(mode, baseline, runtimeAbi)
            };
        }

        private static void BindInputs(Result result, M07Probe.Input input)
        {
            result.fixtureManifest = new ArtifactReceipt { name = "fixture-manifest", available = true, path = input.manifestPath, sha256 = M07Probe.HashFile(input.manifestPath) };
            result.playerBuildReceipt = new PlayerReceipt {
                available = true, path = input.playerReceiptPath, sha256 = M07Probe.HashFile(input.playerReceiptPath),
                variant = input.player.variant, buildGuid = input.player.buildGuid, playerOutput = input.player.playerOutput,
                inputSnapshot = input.player.inputSnapshot, inputSnapshotHash = input.player.inputSnapshotHash,
                nativeLibraryPath = input.player.nativeLibraryPath, nativeLibrarySha256 = input.player.nativeLibrarySha256,
                nativeMetadataPath = input.player.nativeMetadataPath, nativeMetadataSha256 = input.player.nativeMetadataSha256,
                nativeMetadataVersion = input.player.nativeMetadataVersion, nativeArguments = input.player.nativeArguments,
                resourceBuildReceiptPath = input.player.resourceBuildReceiptPath, resourceBuildReceiptSha256 = input.player.resourceBuildReceiptSha256,
                resourceAbiHash = input.player.resourceAbiHash
            };
            result.baselineManifest = new ArtifactReceipt {
                name = "baseline-manifest", available = true, path = input.manifest.baselineManifestPath,
                sha256 = input.manifest.baselineManifestSha256
            };
            result.resourceReceipt = new ArtifactReceipt {
                name = "selected-resource-receipt", available = true, path = input.resourceReceiptPath,
                sha256 = M07Probe.HashFile(input.resourceReceiptPath)
            };
            result.patchId = input.fixture == null ? "" : input.fixture.patchId;
            if (input.fixture != null)
                result.patchManifest = new ArtifactReceipt { name = "patch-manifest", available = true, path = input.fixture.patchManifest, sha256 = input.fixture.patchManifestSha256 };

            // RunTransaction's existing pre-commit guard consumes these
            // hash-bound fields. Populate the same validated boundary as the
            // normal M07 entry instead of duplicating its validation.
            result.m07Transaction.fixtureManifestPath = input.manifestPath;
            result.m07Transaction.fixtureManifestSha256 = M07Probe.HashFile(input.manifestPath);
            result.m07Transaction.playerBuildReceiptPath = input.playerReceiptPath;
            result.m07Transaction.playerBuildReceiptSha256 = M07Probe.HashFile(input.playerReceiptPath);
            result.m07Transaction.baselineManifestPath = input.manifest.baselineManifestPath;
            result.m07Transaction.baselineManifestSha256 = input.manifest.baselineManifestSha256;
            result.m07Transaction.resourceReceiptPath = input.resourceReceiptPath;
            result.m07Transaction.resourceReceiptSha256 = M07Probe.HashFile(input.resourceReceiptPath);
            result.m07Transaction.baselineResourceAbiHash = input.baseline.resourceAbiHash;
            result.m07Transaction.selectedResourceAbiHash = input.resources.resourceAbiHash;
            result.m07Transaction.patchId = input.fixture == null ? "" : input.fixture.patchId;
            result.m07Transaction.patchManifestPath = input.fixture == null ? "" : input.fixture.patchManifest;
            result.m07Transaction.patchManifestSha256 = input.fixture == null ? "" : input.fixture.patchManifestSha256;
            result.m07Transaction.resourcePrecheckPassed = true;
            result.m07Transaction.resourcePrecheckPhase = "before-commit-before-business-resource-load";
        }

        private static void CopyTransaction(Result result)
        {
            result.configureCode = result.m07Transaction.configureCode;
            result.beginCode = result.m07Transaction.beginCode;
            result.stageProbeCode = result.m07Transaction.stageProbeCode;
            result.validateCode = result.m07Transaction.validateCode;
            result.commitCode = result.m07Transaction.commitCode;
            result.abortCode = result.m07Transaction.abortCode;
            result.stateCode = result.m07Transaction.stateCode;
            result.state = result.m07Transaction.state;
            result.stageOrder = result.m07Transaction.stageOrder == null ? new string[0] : result.m07Transaction.stageOrder.ToArray();
        }

        private static TypeIdentity CaptureSelectedType(Result result, string mode)
        {
            Type type = Type.GetType(WitnessTypeName + ", " + InternalAssembly, true);
            Type repeated = Type.GetType(WitnessTypeName + ", " + InternalAssembly, true);
            bool same = object.ReferenceEquals(type, repeated);
            AddCheck(result, "selected-type-identity", same, same.ToString(), true.ToString());
            M07Probe.Require(same, "R00 selected witness Type identity changed between acquisitions.");

            string marker = InvokeString(type.GetMethod("GetMarker", BindingFlags.Public | BindingFlags.Static));
            string expectedMarker = ExpectedMarker(mode);
            AddCheck(result, "witness-marker", marker == expectedMarker, marker, expectedMarker);
            M07Probe.Require(marker == expectedMarker, "R00 witness marker differs: " + marker + ", expected " + expectedMarker);

            string json = "";
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetTypeResolutionInfo(type, out json);
            bool enabled = mode != "R00-OFF-NoPatch";
            AssemblyShadowTypeResolutionInfo info = null;
            if (enabled)
            {
                M07Probe.Require(code == AssemblyShadowErrorCode.Success, "R00 selected type diagnostics failed: " + code);
                info = AssemblyShadowTypeResolutionInfo.Parse(json);
                M07Probe.Require(info.logicalAssembly == InternalAssembly && info.isActive &&
                    info.executionMode == (mode == "R00-ON-NoPatch" ? "AotBaseline" : "InterpreterShadow"),
                    "R00 selected type is not in the expected physical execution world.");
            }
            else M07Probe.Require(code == AssemblyShadowErrorCode.FeatureDisabled, "R00 OFF type diagnostics returned " + code);

            return new TypeIdentity {
                fullName = type.FullName, assemblyName = type.Assembly.GetName().Name, assemblyQualifiedName = type.AssemblyQualifiedName,
                runtimeTypeHandle = type.TypeHandle.Value.ToInt64().ToString(), sameType = same, diagnosticsCode = code.ToString(), rawJson = json,
                logicalAssembly = info == null ? InternalAssembly : info.logicalAssembly,
                executionMode = info == null ? "AotBaseline" : info.executionMode,
                physicalImageKind = info == null ? "Aot" : info.physicalImageKind,
                isActive = info == null || info.isActive,
                pointerDetailsAvailable = info != null && info.pointerDetailsAvailable,
                definitionCacheHits = info == null ? 0 : info.definitionCacheHits,
                definitionCacheMisses = info == null ? 0 : info.definitionCacheMisses,
                compositeRebuilds = info == null ? 0 : info.compositeRebuilds,
                allocationRemaps = info == null ? 0 : info.allocationRemaps,
                guardFailures = info == null ? 0 : info.guardFailures
            };
        }

        private static void RunWitnessBenchmarks(Result result, string mode)
        {
            Type witness = Type.GetType(WitnessTypeName + ", " + InternalAssembly, true);
            RequireMethod(witness, "GetMarker", 0);
            MethodInfo constructorCount = RequireMethod(witness, "GetConstructorCount", 0);
            MethodInfo newPayload = RequireMethod(witness, "NewPayload", 1);
            MethodInfo allocationBatch = RequireMethod(witness, "RunAllocationBatch", 2);
            MethodInfo invokeStep = RequireMethod(witness, "InvokeStep", 1);
            MethodInfo genericDefinition = RequireMethod(witness, "ClosedGeneric", 1);
            MethodInfo closedGeneric = genericDefinition.MakeGenericMethod(typeof(int));

            result.operations.Add(MeasureAllocation(result, allocationBatch, constructorCount, "allocation", "first", 1, 17));
            result.operations.Add(MeasureAllocation(result, allocationBatch, constructorCount, "allocation", "warmup", WarmupCount, 1017));
            result.operations.Add(MeasureAllocation(result, allocationBatch, constructorCount, "allocation", "repeat10", 10, 2017));
            result.operations.Add(MeasureAllocation(result, allocationBatch, constructorCount, "allocation", "repeat10000", RepeatedCount, 3017));

            result.operations.Add(MeasureReflection(result, invokeStep, "reflectionInvoke", "first", 1, 17, false));
            result.operations.Add(MeasureReflection(result, invokeStep, "reflectionInvoke", "warmup", WarmupCount, 1017, false));
            result.operations.Add(MeasureReflection(result, invokeStep, "reflectionInvoke", "repeat10", 10, 2017, false));
            result.operations.Add(MeasureReflection(result, invokeStep, "reflectionInvoke", "repeat10000", RepeatedCount, 3017, false));

            result.operations.Add(MeasureReflection(result, closedGeneric, "closedGeneric", "first", 1, 17, true));
            result.operations.Add(MeasureReflection(result, closedGeneric, "closedGeneric", "warmup", WarmupCount, 1017, true));
            result.operations.Add(MeasureReflection(result, closedGeneric, "closedGeneric", "repeat10", 10, 2017, true));
            result.operations.Add(MeasureReflection(result, closedGeneric, "closedGeneric", "repeat10000", RepeatedCount, 3017, true));

            // Keep the fresh-return witness after the timed first-call row so
            // that the row labelled first is the first payload allocation in
            // the process-local witness, while still proving NewPayload's
            // per-call freshness and constructor count independently.
            int beforeWitness = InvokeInt(constructorCount);
            object first = newPayload.Invoke(null, new object[] { 17 });
            object second = newPayload.Invoke(null, new object[] { 18 });
            int afterWitness = InvokeInt(constructorCount);
            bool fresh = first != null && second != null && !object.ReferenceEquals(first, second) && afterWitness - beforeWitness == 2;
            AddCheck(result, "fresh-managed-payload-and-constructor-count", fresh, (afterWitness - beforeWitness).ToString(), "2 distinct payloads");
            M07Probe.Require(fresh, "R00 witness did not return two fresh payloads with two constructor calls.");
            result.witness = new WitnessObservation {
                typeName = witness.FullName, assemblyName = witness.Assembly.GetName().Name,
                firstPayloadType = first == null ? "" : first.GetType().FullName,
                secondPayloadType = second == null ? "" : second.GetType().FullName,
                firstPayloadDistinct = first != null && second != null && !object.ReferenceEquals(first, second),
                constructorCountBefore = beforeWitness, constructorCountAfter = afterWitness,
                constructorDelta = afterWitness - beforeWitness,
                firstPayloadChecksum = ReadPayloadChecksum(first), secondPayloadChecksum = ReadPayloadChecksum(second)
            };
        }

        private static OperationObservation MeasureAllocation(Result result, MethodInfo batch, MethodInfo constructorCount,
            string operation, string phase, int count, int seed)
        {
            int beforeConstructors = InvokeInt(constructorCount);
            long start = Stopwatch.GetTimestamp();
            int checksum = InvokeInt(batch, count, seed);
            long elapsed = Stopwatch.GetTimestamp() - start;
            int afterConstructors = InvokeInt(constructorCount);
            int actual = afterConstructors - beforeConstructors;
            long expected = ExpectedAllocationChecksum(seed, count, ExpectedMarkerValue(result.mode), ExpectedMarker(result.mode).Length);
            bool passed = actual == count && checksum == expected;
            AddCheck(result, operation + "-" + phase, passed, actual + ":" + checksum, count + ":" + expected);
            M07Probe.Require(passed, "R00 allocation observation differs: " + phase);
            return new OperationObservation {
                operation = operation, phase = phase, requestedIterations = count, methodCalls = 1,
                actualNewCount = actual, actualInvocationCount = 0, checksum = checksum, expectedChecksum = expected,
                constructorCountBefore = beforeConstructors, constructorCountAfter = afterConstructors,
                elapsedTicks = elapsed, stopwatchFrequency = Stopwatch.Frequency, passed = passed
            };
        }

        private static OperationObservation MeasureReflection(Result result, MethodInfo method, string operation, string phase,
            int count, int seed, bool generic)
        {
            int beforeConstructors = 0;
            long start = Stopwatch.GetTimestamp();
            int checksum = 0;
            for (int i = 0; i < count; ++i)
                checksum = unchecked(checksum + InvokeInt(method, seed + i));
            long elapsed = Stopwatch.GetTimestamp() - start;
            long expected = ExpectedInvocationChecksum(seed, count, ExpectedMarkerValue(result.mode), generic);
            bool passed = checksum == expected;
            AddCheck(result, operation + "-" + phase, passed, count + ":" + checksum, count + ":" + expected);
            M07Probe.Require(passed, "R00 " + operation + " observation differs: " + phase);
            return new OperationObservation {
                operation = operation, phase = phase, requestedIterations = count, methodCalls = count,
                actualNewCount = 0, actualInvocationCount = count, checksum = checksum, expectedChecksum = expected,
                constructorCountBefore = beforeConstructors, constructorCountAfter = beforeConstructors,
                elapsedTicks = elapsed, stopwatchFrequency = Stopwatch.Frequency, passed = passed
            };
        }

        private static void CaptureDiagnostics(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            AssemblyShadowErrorCode expected = result.featureEnabled ? AssemblyShadowErrorCode.Success : AssemblyShadowErrorCode.FeatureDisabled;
            AddCheck(result, "diagnostics-" + phase, code == expected, code.ToString(), expected.ToString());
            M07Probe.Require(code == expected, "R00 diagnostics returned " + code + ", expected " + expected);
            AssemblyShadowDiagnostics diagnostics;
            bool parsed = AssemblyShadowDiagnostics.TryParse(json, out diagnostics);
            if (result.featureEnabled) M07Probe.Require(parsed, "R00 enabled diagnostics JSON is unavailable or malformed.");
            DiagnosticsObservation observation = new DiagnosticsObservation {
                phase = phase, diagnosticsOnly = true, code = code.ToString(), rawJson = json ?? "", parsed = parsed,
                unavailableReason = parsed ? "" : "native diagnostics schema unavailable"
            };
            observation.counters = new DiagnosticsCounters {
                proofBuildCount = "unavailable", typeRowsScanned = "unavailable", nativeAllocationCount = "unavailable",
                generation = parsed ? diagnostics.generation : 0, expected = parsed ? diagnostics.expected : 0,
                staged = parsed ? diagnostics.staged : 0, retainedBytes = parsed ? diagnostics.retainedBytes : 0,
                enumerationGeneration = parsed ? diagnostics.enumerationGeneration : 0,
                classEnumerationGeneration = parsed ? diagnostics.classEnumerationGeneration : 0,
                eventCount = parsed && diagnostics.events != null ? diagnostics.events.Length : 0,
                baselineUseCount = parsed && diagnostics.baselineUses != null ? diagnostics.baselineUses.Length : 0,
                assemblyCount = parsed && diagnostics.assemblies != null ? diagnostics.assemblies.Length : 0
            };
            if (phase == "before-benchmark") result.diagnosticsBefore = observation;
            else if (phase == "after-benchmark") result.diagnosticsAfter = observation;
            else result.diagnosticsFailure = observation;
        }

        private static void RunExistingExecutionRegressions(Result result)
        {
            Type type = Type.GetType(InternalAssembly + ".M06ExecutionWitness, " + InternalAssembly, true);
            MethodInfo run = RequireMethod(type, "Run", 1);
            string raw;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetTypeResolutionInfo(type, out raw);
            M07Probe.Require(code == (result.featureEnabled ? AssemblyShadowErrorCode.Success : AssemblyShadowErrorCode.FeatureDisabled),
                "R00 existing M06 witness type diagnostics failed.");
            if (result.featureEnabled)
            {
                AssemblyShadowTypeResolutionInfo info = AssemblyShadowTypeResolutionInfo.Parse(raw);
                M07Probe.Require(info.isActive && info.logicalAssembly == InternalAssembly &&
                    info.executionMode == (result.transactionCommitted ? "InterpreterShadow" : "AotBaseline"),
                    "R00 existing M06 witness is not in the active execution world.");
            }
            result.executionRegressions = new List<ExecutionRegression>();
            foreach (string phase in new[] { "new", "dispatch", "generics" })
            {
                for (int repetition = 0; repetition < 2; ++repetition)
                {
                    var observations = (string[])run.Invoke(null, new object[] { phase });
                    M07Probe.Require(observations != null && observations.Contains("phase=" + phase), "M06 witness phase missing.");
                    string[] required = phase == "new" ? new[] { "ctor.count=2", "ctor.first=1030", "ctor.second=1030", "helper.count=2" } :
                        phase == "dispatch" ? new[] { "virtual=M06-BASELINE:sealed", "abstract=M06-BASELINE:abstract", "assignable=True" } :
                        new[] { "generic.value=4", "method=M06-BASELINE", "nullable=4", "boxed=4", "struct=1004", "ref=1006", "out=1007", "generic.method=6", "array=2" };
                    M07Probe.Require(required.All(observations.Contains), "R00 existing M06 execution observations differ: " + phase);
                    result.executionRegressions.Add(new ExecutionRegression { phase = phase, repetition = repetition,
                        typeName = type.FullName, diagnosticsCode = code.ToString(), typeDiagnosticsJson = raw ?? "", observations = observations });
                }
            }
        }

        private static ReadinessObservation CaptureReadiness(long invocationTimestamp, long invocationUtcTicks, bool ready)
        {
            DateTime utc = DateTime.UtcNow;
            DateTime processStart;
            bool processStartAvailable = false;
            long processStartUtcTicks = 0;
            string reason = "";
            try { processStart = Process.GetCurrentProcess().StartTime.ToUniversalTime(); processStartUtcTicks = processStart.Ticks; processStartAvailable = true; }
            catch (Exception error) { reason = error.GetType().Name + ":" + error.Message; }
            long elapsedMilliseconds = processStartAvailable ? Math.Max(0, (utc.Ticks - processStartUtcTicks) / TimeSpan.TicksPerMillisecond) : -1;
            return new ReadinessObservation {
                phase = ready ? "configured-and-witness-resolved" : "probe-invoked",
                processStartAvailable = processStartAvailable, unavailableReason = reason,
                processStartUtcTicks = processStartUtcTicks, probeInvocationUtcTicks = invocationUtcTicks,
                businessReadyUtcTicks = ready ? utc.Ticks : 0, startupToBusinessReadyMilliseconds = ready ? elapsedMilliseconds : -1,
                invocationTimestamp = invocationTimestamp, businessReady = ready
            };
        }

        private static MethodInfo RequireMethod(Type type, string name, int parameterCount)
        {
            MethodInfo[] methods = type.GetMethods(BindingFlags.Public | BindingFlags.Static).Where(method => method.Name == name && method.GetParameters().Length == parameterCount).ToArray();
            M07Probe.Require(methods.Length == 1, "R00 witness method is absent or ambiguous: " + name);
            return methods[0];
        }

        private static int InvokeInt(MethodInfo method, params object[] arguments)
        {
            object value = method.Invoke(null, arguments);
            M07Probe.Require(value is int, "R00 witness method returned a non-Int32 value: " + method.Name);
            return (int)value;
        }

        private static string InvokeString(MethodInfo method)
        {
            object value = method.Invoke(null, null);
            M07Probe.Require(value is string, "R00 witness marker returned a non-string value.");
            return (string)value;
        }

        private static int ReadPayloadChecksum(object payload)
        {
            M07Probe.Require(payload != null, "R00 payload is null.");
            FieldInfo seed = payload.GetType().GetField("Seed", BindingFlags.Public | BindingFlags.Instance);
            FieldInfo marker = payload.GetType().GetField("Marker", BindingFlags.Public | BindingFlags.Instance);
            FieldInfo markerValue = payload.GetType().GetField("MarkerValue", BindingFlags.Public | BindingFlags.Instance);
            M07Probe.Require(seed != null && marker != null && markerValue != null, "R00 payload fields are unavailable.");
            return unchecked((int)seed.GetValue(payload) * 17 + (int)markerValue.GetValue(payload) + ((string)marker.GetValue(payload)).Length);
        }

        private static long ExpectedAllocationChecksum(int seed, int count, int markerValue, int markerLength)
        {
            int checksum = 0;
            for (int i = 0; i < count; ++i) checksum = unchecked(checksum + (seed + i) * 17 + markerValue + markerLength);
            return checksum;
        }

        private static long ExpectedInvocationChecksum(int seed, int count, int markerValue, bool generic)
        {
            int checksum = 0;
            for (int i = 0; i < count; ++i)
                checksum = unchecked(checksum + (generic ? seed + i : unchecked((seed + i) * 31 + markerValue)));
            return checksum;
        }

        private static string ExpectedMarker(string mode)
        {
            return mode == "R00-ON-P03" ? "R00-P03" : mode == "R00-ON-P01" ? "R00-P01" : "R00-BASELINE";
        }

        private static int ExpectedMarkerValue(string mode)
        {
            return mode == "R00-ON-P03" ? 3003 : mode == "R00-ON-P01" ? 3001 : 3000;
        }

        private static void AddCheck(Result result, string name, bool passed, string actual, string expected)
        {
            result.assertions.Add(new Assertion { name = name, passed = passed, actual = actual ?? "", expected = expected ?? "" });
        }

        private static void WriteEvidence(Result result)
        {
            string output = Path.GetFullPath(M07Probe.Argument("-shadowR00Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/r00-" + result.mode + ".json")));
            string directory = Path.GetDirectoryName(output);
            Directory.CreateDirectory(directory);
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new System.Text.UTF8Encoding(false))) writer.Write(JsonUtility.ToJson(result, true));
        }

        [Serializable, Preserve]
        public sealed class Result
        {
            [Preserve] public int schemaVersion, processId;
            [Preserve] public string milestone, mode, result, error, unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public bool il2cpp, featureEnabled, transactionCommitted;
            [Preserve] public string configureCode, beginCode, stageProbeCode, validateCode, commitCode, abortCode, stateCode, state, patchId;
            [Preserve] public string[] stageOrder;
            [Preserve] public ArtifactReceipt fixtureManifest, baselineManifest, resourceReceipt, patchManifest;
            [Preserve] public PlayerReceipt playerBuildReceipt;
            [Preserve] public ReadinessObservation readiness;
            [Preserve] public DiagnosticsObservation diagnosticsBefore, diagnosticsAfter, diagnosticsFailure;
            [Preserve] public TypeIdentity selectedType;
            [Preserve] public WitnessObservation witness;
            [Preserve] public List<OperationObservation> operations;
            [Preserve] public List<Assertion> assertions;
            [Preserve] public List<ExecutionRegression> executionRegressions;
            [NonSerialized] internal M07Probe.Result m07Transaction;
        }

        [Serializable, Preserve] public sealed class ArtifactReceipt { [Preserve] public string name, path, sha256; [Preserve] public bool available; }
        [Serializable, Preserve] public sealed class PlayerReceipt
        {
            [Preserve] public bool available; [Preserve] public string path, sha256, variant, buildGuid, playerOutput, inputSnapshot, inputSnapshotHash;
            [Preserve] public string nativeLibraryPath, nativeLibrarySha256, nativeMetadataPath, nativeMetadataSha256, nativeArguments;
            [Preserve] public int nativeMetadataVersion; [Preserve] public string resourceBuildReceiptPath, resourceBuildReceiptSha256, resourceAbiHash;
        }
        [Serializable, Preserve] public sealed class ReadinessObservation
        {
            [Preserve] public string phase, unavailableReason; [Preserve] public bool processStartAvailable, businessReady;
            [Preserve] public long processStartUtcTicks, probeInvocationUtcTicks, businessReadyUtcTicks, startupToBusinessReadyMilliseconds, invocationTimestamp;
        }
        [Serializable, Preserve] public sealed class DiagnosticsObservation
        {
            [Preserve] public string phase, code, rawJson, unavailableReason; [Preserve] public bool diagnosticsOnly, parsed;
            [Preserve] public DiagnosticsCounters counters;
        }
        [Serializable, Preserve] public sealed class DiagnosticsCounters
        {
            [Preserve] public string proofBuildCount, typeRowsScanned, nativeAllocationCount;
            [Preserve] public ulong generation, expected, staged, retainedBytes, enumerationGeneration, classEnumerationGeneration;
            [Preserve] public int eventCount, baselineUseCount, assemblyCount;
        }
        [Serializable, Preserve] public sealed class TypeIdentity
        {
            [Preserve] public string fullName, assemblyName, assemblyQualifiedName, runtimeTypeHandle, diagnosticsCode, rawJson, logicalAssembly, executionMode, physicalImageKind;
            [Preserve] public bool sameType, isActive, pointerDetailsAvailable;
            [Preserve] public ulong definitionCacheHits, definitionCacheMisses, compositeRebuilds, allocationRemaps, guardFailures;
        }
        [Serializable, Preserve] public sealed class WitnessObservation
        {
            [Preserve] public string typeName, assemblyName, firstPayloadType, secondPayloadType;
            [Preserve] public bool firstPayloadDistinct; [Preserve] public int constructorCountBefore, constructorCountAfter, constructorDelta;
            [Preserve] public int firstPayloadChecksum, secondPayloadChecksum;
        }
        [Serializable, Preserve] public sealed class OperationObservation
        {
            [Preserve] public string operation, phase; [Preserve] public int requestedIterations, methodCalls, actualNewCount, actualInvocationCount;
            [Preserve] public long checksum, expectedChecksum, elapsedTicks, stopwatchFrequency;
            [Preserve] public int constructorCountBefore, constructorCountAfter; [Preserve] public bool passed;
        }
        [Serializable, Preserve] public sealed class Assertion
        {
            [Preserve] public string name, actual, expected; [Preserve] public bool passed;
        }

        [Serializable, Preserve] public sealed class ExecutionRegression
        {
            [Preserve] public string phase, typeName, diagnosticsCode, typeDiagnosticsJson;
            [Preserve] public int repetition;
            [Preserve] public string[] observations;
        }
    }

    // These wrappers keep M07's existing validation logic and DTOs private to
    // the M07 partial while allowing the separate R00 result boundary to reuse
    // that logic without reflection or a second validator.
    public static partial class M07Probe
    {
        internal static bool R00IsIl2CppPlayer() { return IsIl2CppPlayer(); }
        internal static Result R00NewResult(string mode, string baseline, string runtimeAbi) { return NewResult(mode, baseline, runtimeAbi); }
        internal static Input R00ReadInputs(string baseline, string runtimeAbi, string mode) { return ReadInputs(baseline, runtimeAbi, mode); }
        internal static void R00RunTransaction(Result result, Input input) { RunTransaction(result, input); }
        internal static void R00RunFeatureOff(Result result) { RunFeatureOff(result); }
    }
}
