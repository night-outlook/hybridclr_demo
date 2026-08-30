using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>Managed M06 execution-semantics acceptance probe.</summary>
    [Preserve]
    public static partial class M06ExecutionProbe
    {
        internal const int RuntimeAbiVersion = 1;
        internal const string Contracts = "AssemblyA.Contracts";
        internal const string Extensibility = "AssemblyA.Implementation.Extensibility";
        internal const string Internal = "AssemblyA.Implementation.Internal";
        internal const string ContractsConsumer = "AssemblyShadowDemo.ContractsConsumer";
        internal const string ExtensibilityConsumer = "AssemblyShadowDemo.ExtensibilityConsumer";
        internal const string MvidPolicy = "unavailable-pinned-il2cpp-use-byte-bound-build-and-native-diagnostics";
        internal static readonly string[] Candidates = { Contracts, Extensibility, Internal, ContractsConsumer, ExtensibilityConsumer };
        internal static readonly string[] Modes = {
            "T06-01-New-P01", "T06-01-New-P02", "T06-01-New-P03",
            "T06-02-Statics-P01", "T06-02-Statics-P02", "T06-02-Statics-P03",
            "T06-03-P01", "T06-04-P02", "T06-05-P03",
            "T06-06-Delegates-P01", "T06-06-Delegates-P02", "T06-06-Delegates-P03",
            "T06-07-Generics-P01", "T06-07-Generics-P02", "T06-07-Generics-P03",
            "T06-08-Async-P01", "T06-08-Async-P02", "T06-08-Async-P03",
            "T06-09-InitializerFailure", "T06-09-BaselineRecovery",
            "T06-10-Warmup-P01", "T06-10-Warmup-P02", "T06-10-Warmup-P03",
            "T06-11-FeatureOff",
            "T06-12-NoWarmup-P01", "T06-12-NoWarmup-P02", "T06-12-NoWarmup-P03",
            "T06-13-ReleaseNoPdb"
        };

        public static int RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            Result result = NewResult(Argument("-shadowM06Mode", "T06-01-New-P01"), expectedBaselineBuildId, expectedRuntimeAbiHash);
            bool inputsValidated = false;
            try
            {
                Require(result.il2cpp, "M06 acceptance requires an actual IL2CPP Player.");
                Require(IsKnownMode(result.mode), "Unknown M06 mode: " + result.mode);
                Input input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash);
                inputsValidated = true;
                BindResult(result, input);
                RunCore(result, input);
                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.error = error.ToString();
                UnityEngine.Debug.LogException(error);
                if (inputsValidated)
                {
                    try { CaptureTransaction(result, "failure"); } catch (Exception captureError) { result.error += "\nFailure diagnostics: " + captureError; }
                    try { CaptureExecution(result, "failure"); } catch (Exception captureError) { result.error += "\nFailure execution diagnostics: " + captureError; }
                }
            }
            try { WriteEvidence(result); return result.result == "Passed" ? 0 : 1; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); return 2; }
        }

        public static IEnumerator RunAndWriteCoroutine(string expectedBaselineBuildId, string expectedRuntimeAbiHash, Action<int> completed)
        {
            Result result = NewResult(Argument("-shadowM06Mode", "T06-01-New-P01"), expectedBaselineBuildId, expectedRuntimeAbiHash);
            int exitCode = 2;
            // Awake's first MoveNext must validate inputs and publish the transaction
            // before any later-order Unity callback can acquire a candidate.
            Input input = null;
            bool inputsValidated = false;
            Exception failure = null;
            try
            {
                Require(result.il2cpp, "M06 acceptance requires an actual IL2CPP Player.");
                Require(IsKnownMode(result.mode), "Unknown M06 mode: " + result.mode);
                input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash);
                inputsValidated = true;
                BindResult(result, input);
            }
            catch (Exception error) { failure = error; }
            if (failure == null)
            {
                IEnumerator work = RunCoreCoroutine(result, input);
                try
                {
                    while (true)
                    {
                        bool moved = false;
                        object current = null;
                        try { moved = work.MoveNext(); if (moved) current = work.Current; }
                        catch (Exception error) { failure = error; break; }
                        if (!moved) break;
                        yield return current;
                    }
                }
                finally { try { DisposeIterator(work); } catch (Exception error) { if (failure == null) failure = error; } }
            }
            if (failure != null)
            {
                result.error = failure.ToString();
                UnityEngine.Debug.LogException(failure);
                if (inputsValidated)
                {
                    try { CaptureTransaction(result, "failure"); } catch (Exception captureError) { result.error += "\nFailure diagnostics: " + captureError; }
                    try { CaptureExecution(result, "failure"); } catch (Exception captureError) { result.error += "\nFailure execution diagnostics: " + captureError; }
                }
            }
            else result.result = "Passed";
            try { WriteEvidence(result); exitCode = result.result == "Passed" ? 0 : 1; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); }
            if (completed != null) completed(exitCode);
        }

        public static bool IsAsyncMode()
        {
            string mode = Argument("-shadowM06Mode", "T06-01-New-P01");
            return mode.StartsWith("T06-08-", StringComparison.Ordinal) || mode == "T06-09-BaselineRecovery";
        }

        private static void RunCore(Result result, Input input)
        {
            result.developmentBuild = input.player.developmentBuild;
            result.variant = input.player.variant;
            if (result.mode == "T06-11-FeatureOff") { RunFeatureOff(result, input); return; }
            if (result.mode == "T06-09-BaselineRecovery") { RunBaselineRecovery(result, input); return; }
            Fixture fixture = result.mode == "T06-09-InitializerFailure" ? input.manifest.initializerFailureFixture : SelectFixture(input.manifest, result.mode);
            Require(fixture != null, "M06 fixture is missing for " + result.mode);
            RunTransaction(result, input, fixture);
        }

        private static IEnumerator RunCoreCoroutine(Result result, Input input)
        {
            result.developmentBuild = input.player.developmentBuild;
            result.variant = input.player.variant;
            if (result.mode == "T06-11-FeatureOff") { RunFeatureOff(result, input); yield break; }
            if (result.mode == "T06-09-BaselineRecovery") { RunBaselineRecovery(result, input); yield break; }
            Fixture fixture = result.mode == "T06-09-InitializerFailure" ? input.manifest.initializerFailureFixture : SelectFixture(input.manifest, result.mode);
            Require(fixture != null, "M06 fixture is missing for " + result.mode);
            IEnumerator work = RunTransactionCoroutine(result, input, fixture);
            try { while (work.MoveNext()) yield return work.Current; }
            finally { DisposeIterator(work); }
        }

        private static void RunTransaction(Result result, Input input, Fixture fixture)
        {
            Require(!IsAsyncMode(), "M06 asynchronous execution requires the Unity coroutine entrypoint.");
            if (!PrepareTransaction(result, input, fixture)) return;
            if (ModeIsWarmup(result.mode)) RunWarmup(result, fixture);
            ObserveExecution(result, input, fixture);
            FinishTransaction(result);
        }

        private static IEnumerator RunTransactionCoroutine(Result result, Input input, Fixture fixture)
        {
            if (!PrepareTransaction(result, input, fixture)) yield break;
            if (ModeIsWarmup(result.mode)) RunWarmup(result, fixture);
            IEnumerator work = ObserveExecutionCoroutine(result, input, fixture);
            try { while (work.MoveNext()) yield return work.Current; }
            finally { DisposeIterator(work); }
            FinishTransaction(result);
        }

        private static bool PrepareTransaction(Result result, Input input, Fixture fixture)
        {
            result.patchId = fixture.patchId;
            result.patchManifestPath = fixture.patchManifest;
            result.patchManifestSha256 = fixture.patchManifestSha256;
            result.compileSnapshotHash = fixture.compileSnapshotHash;
            RequireState(result, AssemblyShadowState.Disabled, "initial");
            CaptureTransaction(result, "initial");
            CaptureExecution(result, "initial");
            TimedOperation(result, "configure", () => {
                result.configureCode = (int)AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames);
                RequireCode(result.configureCode, AssemblyShadowErrorCode.Success, "configure");
            });
            TimedOperation(result, "begin", () => {
                result.beginCode = (int)AssemblyShadowRuntime.BeginTransaction(fixture.patchId, input.manifest.baselineBuildId, fixture.closureLoadOrder, RuntimeAbiVersion);
                RequireCode(result.beginCode, AssemblyShadowErrorCode.Success, "begin");
            });
            RequireState(result, AssemblyShadowState.Staging, "staging");
            RunSupplementaryMetadata(result, input, fixture);
            TimedOperation(result, "stage", () => {
                foreach (string name in fixture.closureLoadOrder)
                {
                    PatchAssembly patch = fixture.patch.closure.Single(row => row.name == name);
                    byte[] dll = File.ReadAllBytes(patch.dll);
                    byte[] pdb = string.IsNullOrEmpty(patch.pdb) ? null : File.ReadAllBytes(patch.pdb);
                    Require(Hash(dll) == patch.sha256 && (pdb == null ? string.IsNullOrEmpty(patch.pdbSha256) : Hash(pdb) == patch.pdbSha256),
                        "M06 patch bytes changed after input verification: " + name);
                    int code = (int)AssemblyShadowRuntime.StageAssembly(dll, pdb);
                    result.stageResults.Add(new StageResult { name = name, code = code, dllSha256 = Hash(dll), pdbSha256 = pdb == null ? "" : Hash(pdb) });
                    RequireCode(code, AssemblyShadowErrorCode.Success, "stage-" + name);
                }
            });
            result.stageOrder = fixture.closureLoadOrder.ToArray();
            CaptureTransaction(result, "staged");
            RequireNoEarlyInitializers(result);
            TimedOperation(result, "validate", () => {
                result.validateCode = (int)AssemblyShadowRuntime.ValidateTransaction();
                RequireCode(result.validateCode, AssemblyShadowErrorCode.Success, "validate");
            });
            CaptureTransaction(result, "validated");
            RequireNoEarlyInitializers(result);
            TimedOperation(result, "commit", () => result.commitCode = (int)AssemblyShadowRuntime.CommitTransaction());
            if (result.mode == "T06-09-InitializerFailure")
            {
                RequireCode(result.commitCode, AssemblyShadowErrorCode.ModuleInitializerFailed, "initializer-failure-commit");
                RequireState(result, AssemblyShadowState.FailedAfterCommit, "initializer-failure");
                CaptureTransaction(result, "initializer-failure");
                CaptureExecution(result, "initializer-failure");
                ValidateRetainedInitializerFailure(result.transactionSnapshots.Last().diagnostics, fixture, input.manifest.baselineBuildId);
                Require(!result.businessLaunched, "Business ran after a failed initializer.");
                return false;
            }
            RequireCode(result.commitCode, AssemblyShadowErrorCode.Success, "commit");
            RequireState(result, AssemblyShadowState.Committed, "committed");
            CaptureTransaction(result, "committed");
            CaptureExecution(result, "committed");
            var committed = result.transactionSnapshots.Last().diagnostics;
            Require(committed.commitOrder.SequenceEqual(fixture.closureLoadOrder) && committed.assemblies.All(row => row.moduleInitializerAttempted && row.moduleInitializerRan && row.published),
                "M06 publication/initializer order differs from the declared closure.");
            return true;
        }

        private static void FinishTransaction(Result result)
        {
            result.businessLaunched = true;
            CaptureTransaction(result, "final");
            CaptureExecution(result, "final");
            Require(result.executionSnapshots.Last().diagnostics.shadowMethodChecks > 0, "No shadow execution guard observations were captured.");
        }

        private static void TimedOperation(Result result, string phase, Action operation)
        {
            CaptureExecution(result, phase + "-before");
            ulong before = LatestExecutionTransformations(result), shadowBefore = LatestShadowTransformations(result);
            long start = Stopwatch.GetTimestamp();
            try { operation(); }
            finally
            {
                long end = Stopwatch.GetTimestamp();
                CaptureExecution(result, phase + "-after");
                AddTiming(result, phase, start, end, before, LatestExecutionTransformations(result), shadowBefore, LatestShadowTransformations(result));
            }
        }

        private static void RequireNoEarlyInitializers(Result result)
        {
            var execution = result.executionSnapshots.Last().diagnostics;
            var transaction = result.transactionSnapshots.Last().diagnostics;
            Require(execution.baselineClassCctorStarted == 0 && execution.shadowClassCctorStarted == 0 &&
                transaction.assemblies.All(row => !row.moduleInitializerAttempted && !row.moduleInitializerRan && !row.published),
                "Stage/Validate initialized or published business classes before Commit.");
        }

        private static void DisposeIterator(IEnumerator iterator)
        { IDisposable disposable = iterator as IDisposable; if (disposable != null) disposable.Dispose(); }

        private static void RunWarmup(Result result, Fixture fixture)
        {
            Require(fixture.warmup != null && fixture.warmup.types != null && fixture.warmup.methods != null, "M06 warmup mode requires the verified schema-2 warmup envelope.");
            long start = Stopwatch.GetTimestamp();
            ulong totalBefore = LatestExecutionTransformations(result), shadowBefore = LatestShadowTransformations(result);
            foreach (WarmupType entry in fixture.warmup.types)
            {
                Require(entry != null && fixture.closureLoadOrder.Contains(entry.assembly, StringComparer.Ordinal), "M06 warmup type is outside the active closure.");
                Type type = WitnessType(entry.assembly);
                Require(type.FullName == entry.type, "M06 warmup type identity differs from the verified manifest: " + entry.type);
                ulong before = LatestExecutionTransformations(result), shadowBeforeType = LatestShadowTransformations(result);
                bool classResult = RuntimeApi.PreJitClass(type);
                Require(classResult, "M06 PreJitClass rejected the verified warmup target: " + entry.type);
                CaptureExecution(result, "warmup-type-" + entry.assembly);
                ulong after = LatestExecutionTransformations(result), shadowAfterType = LatestShadowTransformations(result);
                result.warmupObservations.Add(new WarmupObservation { phase = "prejit", targetKind = "type", assemblyName = entry.assembly, declaringType = type.FullName,
                    name = "", genericArity = 0, preJitClass = classResult, preJitMethod = false, returnedValues = new string[0],
                    transformationBefore = before, transformationAfter = after, shadowTransformationBefore = shadowBeforeType, shadowTransformationAfter = shadowAfterType });
            }
            foreach (WarmupMethod entry in fixture.warmup.methods)
            {
                MethodInfo method = ResolveWarmupMethod(entry, fixture);
                ulong before = LatestExecutionTransformations(result), shadowBeforeMethod = LatestShadowTransformations(result);
                bool methodResult = RuntimeApi.PreJitMethod(method);
                Require(methodResult, "M06 PreJitMethod rejected the verified warmup target: " + entry.name);
                string actualReturn = methodResult.ToString();
                CaptureExecution(result, "warmup-method-" + entry.assembly + "-" + entry.name);
                ulong after = LatestExecutionTransformations(result), shadowAfterMethod = LatestShadowTransformations(result);
                result.warmupObservations.Add(new WarmupObservation { phase = "prejit", targetKind = "method", assemblyName = entry.assembly,
                    declaringType = method.DeclaringType.FullName, name = method.Name, genericArity = method.IsGenericMethod ? method.GetGenericArguments().Length : 0,
                    genericArguments = method.IsGenericMethod ? method.GetGenericArguments().Select(type => type.AssemblyQualifiedName).ToArray() : new string[0],
                    returnType = method.ReturnType.AssemblyQualifiedName, parameterTypes = method.GetParameters().Select(parameter => parameter.ParameterType.AssemblyQualifiedName).ToArray(),
                    metadataToken = method.MetadataToken, preJitClass = false, preJitMethod = methodResult, returnedValues = new[] { actualReturn }, actualReturn = actualReturn,
                    transformationBefore = before, transformationAfter = after, shadowTransformationBefore = shadowBeforeMethod, shadowTransformationAfter = shadowAfterMethod });
            }
            Require(fixture.warmup.types.Length > 0, "M06 warmup manifest has no explicit module owners.");
            AddTiming(result, "prejit", start, Stopwatch.GetTimestamp(), totalBefore, LatestExecutionTransformations(result), shadowBefore, LatestShadowTransformations(result));
            long moduleStart = Stopwatch.GetTimestamp();
            ulong moduleTotal = LatestExecutionTransformations(result), moduleShadow = LatestShadowTransformations(result);
            foreach (WarmupMethod entry in fixture.warmup.methods.Where(method => method.name == "Run"))
            {
                Type owner = WitnessType(entry.assembly);
                Require(owner.FullName == entry.declaringType, "M06 module warmup target differs from its manifest.");
                CaptureExecution(result, "module-warmup-before-" + entry.assembly);
                ulong before = LatestExecutionTransformations(result), shadow = LatestShadowTransformations(result);
                foreach (WarmupMethod methodEntry in fixture.warmup.methods.Where(method => method.assembly == entry.assembly && method.name != "Run"))
                {
                    MethodInfo method = ResolveWarmupMethod(methodEntry, fixture);
                    CaptureExecution(result, "warmup-call-before-" + entry.assembly + "-" + method.Name);
                    ulong callBefore = LatestExecutionTransformations(result), shadowCallBefore = LatestShadowTransformations(result);
                    string returned = InvokeWarmupMethod(method);
                    Require(returned == (method.Name == "WarmupValue" ? (ExpectedGeneration(entry.assembly, fixture.patchId) + 7).ToString() : method.ReturnType == typeof(int) ? "7" : "warmup"), "M06 declared warmup method returned wrong value.");
                    CaptureExecution(result, "warmup-call-after-" + entry.assembly + "-" + method.Name);
                    result.warmupObservations.Add(new WarmupObservation { phase = "module-warmup-method", targetKind = "method", assemblyName = entry.assembly,
                        declaringType = owner.FullName, name = method.Name, metadataToken = method.MetadataToken, genericArity = method.GetGenericArguments().Length,
                        returnedValues = new[] { returned }, actualReturn = returned, transformationBefore = callBefore, transformationAfter = LatestExecutionTransformations(result),
                        shadowTransformationBefore = shadowCallBefore, shadowTransformationAfter = LatestShadowTransformations(result) });
                }
                string[] values = InvokeRun(owner, "warmup");
                Require(ParseModuleValue(values, "phase=") == "warmup" && ParseModuleValue(values, "echo=") == "warmup" &&
                    ParseModuleInt(values, "warmup=") == ExpectedGeneration(entry.assembly, fixture.patchId) + 7,
                    "M06 literal module warmup returned the wrong business result.");
                CaptureExecution(result, "module-warmup-after-" + entry.assembly);
                result.warmupObservations.Add(new WarmupObservation { phase = "module-warmup", targetKind = "module", assemblyName = entry.assembly,
                    declaringType = owner.FullName, name = "Run", genericArity = 0, preJitClass = false, preJitMethod = false,
                    returnedValues = values, actualReturn = string.Join(";", values), transformationBefore = before,
                    transformationAfter = LatestExecutionTransformations(result), shadowTransformationBefore = shadow, shadowTransformationAfter = LatestShadowTransformations(result) });
            }
            AddTiming(result, "module-warmup", moduleStart, Stopwatch.GetTimestamp(), moduleTotal, LatestExecutionTransformations(result), moduleShadow, LatestShadowTransformations(result));
            CaptureExecution(result, "warmup");
            long end = Stopwatch.GetTimestamp();
            result.timings.Add(new TimingObservation { phase = "warmup", stopwatchFrequency = Stopwatch.Frequency, startTicks = start, endTicks = end,
                elapsedTicks = end - start, transformationsBefore = totalBefore, transformationsAfter = LatestExecutionTransformations(result),
                shadowTransformationsBefore = shadowBefore, shadowTransformationsAfter = LatestShadowTransformations(result) });
        }

        private static MethodInfo ResolveWarmupMethod(WarmupMethod entry, Fixture fixture)
        {
            Require(entry != null && fixture.closureLoadOrder.Contains(entry.assembly, StringComparer.Ordinal), "M06 warmup method is outside the active closure.");
            Type declaring = WitnessType(entry.assembly);
            Require(declaring.FullName == entry.declaringType, "M06 warmup method declaring type differs from the verified manifest.");
            Require(entry.name == "WarmupValue" || entry.name == "WarmupEcho" || entry.name == "Run", "M06 warmup method is not in the finite dispatcher.");
            MethodInfo[] matches = declaring.GetMethods(BindingFlags.Public | BindingFlags.Static).Where(candidate => candidate.DeclaringType == declaring && candidate.Name == entry.name).ToArray();
            Require(matches.Length == 1, "M06 warmup method is missing or ambiguous: " + entry.name);
            MethodInfo method = matches[0];
            Require(entry.isStatic, "M06 warmup method must be explicitly static.");
            int expectedArity = entry.name == "WarmupEcho" ? 1 : 0;
            Require(method.IsGenericMethodDefinition == (expectedArity != 0) && method.GetGenericArguments().Length == expectedArity && entry.genericArity == expectedArity,
                "M06 warmup generic arity differs from the verified manifest: " + entry.name);
            if (expectedArity != 0)
            {
                Require(entry.genericArguments != null && entry.genericArguments.Length == 1, "M06 generic warmup argument is missing.");
                method = method.MakeGenericMethod(ResolveWarmupType(entry.genericArguments[0], declaring.Assembly));
            }
            Require(method.ReturnType == ResolveWarmupType(entry.returnType, declaring.Assembly), "M06 warmup return signature differs from the verified manifest.");
            ParameterInfo[] parameters = method.GetParameters();
            Require(entry.parameterTypes != null && entry.parameterTypes.Length == parameters.Length, "M06 warmup parameter signature differs from the verified manifest.");
            for (int index = 0; index < parameters.Length; ++index)
                Require(parameters[index].ParameterType == ResolveWarmupType(entry.parameterTypes[index], declaring.Assembly), "M06 warmup parameter signature differs from the verified manifest.");
            return method;
        }

        private static Type ResolveWarmupType(WarmupTypeIdentity identity, Assembly declaringAssembly)
        {
            Require(identity != null && declaringAssembly != null && !string.IsNullOrEmpty(identity.assembly) && !string.IsNullOrEmpty(identity.type), "M06 warmup type identity is incomplete.");
            Type resolved;
            if (identity.type == "System.Int32") resolved = typeof(int);
            else if (identity.type == "System.String") resolved = typeof(string);
            else if (identity.type == "System.String[]") resolved = typeof(string[]);
            else throw new InvalidOperationException("M06 warmup type identity is not in the finite primitive set: " + identity.type);
            // Unity compiles against netstandard but IL2CPP retargets these CLI
            // primitives to mscorlib. Accept only the exact declared reference
            // captured on this active shadow assembly, or the resolved provider.
            Require(identity.assembly == resolved.Assembly.FullName || declaringAssembly.GetReferencedAssemblies().Any(reference => reference.FullName == identity.assembly),
                "M06 warmup compiler/runtime primitive provider is not bound to the active declaring assembly: " + identity.assembly);
            return resolved;
        }

        private static string InvokeWarmupMethod(MethodInfo method)
        {
            object value = method.Name == "WarmupValue" ? method.Invoke(null, new object[] { 7 }) : method.Invoke(null, new object[] { method.ReturnType == typeof(int) ? (object)7 : "warmup" });
            return value == null ? "<null>" : value.ToString();
        }

        private static void ObserveExecution(Result result, Input input, Fixture fixture)
        {
            IEnumerator work = ObserveExecutionCoroutine(result, input, fixture);
            try
            {
                Require(!work.MoveNext(), "M06 yielded business execution must use the Unity coroutine entrypoint.");
            }
            finally { DisposeIterator(work); }
        }

        private static void RunSupplementaryMetadata(Result result, Input input, Fixture fixture)
        {
            Require(input.player.supplementaryMetadataInputs != null || fixture.requiredAotMetadataNames.Length == 0,
                "M06 supplementary metadata inputs are missing for a fixture that requires AOT metadata.");
            foreach (string requiredName in fixture.requiredAotMetadataNames)
            {
                SupplementaryMetadataInput item = input.player.supplementaryMetadataInputs.SingleOrDefault(candidate => candidate.assemblyName == requiredName);
                Require(item != null, "M06 required AOT metadata input is missing: " + requiredName);
                Require(item.identity != null && item.identity.name == item.assemblyName && item.identity.sha256 == item.sha256 && Absolute(item.identity.path) == Absolute(item.path),
                    "M06 required AOT metadata identity/path binding differs: " + requiredName);
                byte[] bytes = File.ReadAllBytes(item.path);
                LoadImageErrorCode code = RuntimeApi.LoadMetadataForAOTAssembly(bytes, HomologousImageMode.Consistent);
                result.supplementaryMetadata.Add(new SupplementaryMetadataObservation { assemblyName = item.assemblyName, path = item.path,
                    sha256 = Hash(bytes), resultCode = (int)code, loaded = code == LoadImageErrorCode.OK });
                Require(Hash(bytes) == item.sha256 && code == LoadImageErrorCode.OK, "M06 required supplementary AOT metadata failed: " + item.assemblyName);
            }
        }

        private static void RunFeatureOff(Result result, Input input)
        {
            AssemblyShadowState state; AssemblyExecutionMode mode; string json;
            result.configureCode = (int)AssemblyShadowRuntime.ConfigureCandidates(null, null, null);
            result.beginCode = (int)AssemblyShadowRuntime.BeginTransaction(null, null, null, -1);
            result.stageResults.Add(new StageResult { name = "", code = (int)AssemblyShadowRuntime.StageAssembly(null, null), dllSha256 = "", pdbSha256 = "" });
            result.validateCode = (int)AssemblyShadowRuntime.ValidateTransaction();
            result.commitCode = (int)AssemblyShadowRuntime.CommitTransaction();
            result.abortCode = (int)AssemblyShadowRuntime.AbortTransaction();
            result.stateCode = (int)AssemblyShadowRuntime.GetState(out state); result.state = state.ToString();
            result.executionModeCode = (int)AssemblyShadowRuntime.GetAssemblyExecutionMode(Internal, out mode); result.executionMode = mode.ToString();
            result.diagnosticsCode = (int)AssemblyShadowRuntime.GetDiagnosticsJson(out json); result.nativeDiagnosticsJson = json;
            result.executionDiagnosticsCode = (int)AssemblyShadowRuntime.GetExecutionDiagnosticsJson(out json); result.executionDiagnosticsJson = json;
            string typeJson = "must-be-cleared";
            result.typeResolutionCode = (int)AssemblyShadowRuntime.GetTypeResolutionInfo(null, out typeJson);
            RecordCheck(result, "GetState:disabled", result.stateCode, AssemblyShadowErrorCode.FeatureDisabled, state.ToString(), "Disabled");
            RecordCheck(result, "GetAssemblyExecutionMode:disabled", result.executionModeCode, AssemblyShadowErrorCode.FeatureDisabled, mode.ToString(), "AotBaseline");
            RecordCheck(result, "GetTypeResolutionInfo:disabled", result.typeResolutionCode, AssemblyShadowErrorCode.FeatureDisabled, typeJson, null);
            Require(typeJson == null, "M06 feature-off type output was not cleared.");
            foreach (int code in new[] { result.configureCode, result.beginCode, result.stageResults[0].code, result.validateCode, result.commitCode, result.abortCode,
                result.stateCode, result.executionModeCode, result.diagnosticsCode, result.typeResolutionCode, result.executionDiagnosticsCode })
                RequireCode(code, AssemblyShadowErrorCode.FeatureDisabled, "feature-off API");
            ValidateJsonShape(new ProofJsonReader(result.nativeDiagnosticsJson).Read(), typeof(AssemblyShadowDiagnostics), "disabledDiagnostics");
            AssemblyShadowDiagnostics disabled;
            Require(AssemblyShadowDiagnostics.TryParse(result.nativeDiagnosticsJson, out disabled), "M06 OFF transaction diagnostics are missing.");
            ValidateDisabledDiagnostics(disabled);
            result.transactionSnapshots.Add(new TransactionSnapshot { phase = "disabled", rawJson = result.nativeDiagnosticsJson, diagnostics = disabled });
            Require(result.executionDiagnosticsJson == null && state == AssemblyShadowState.Disabled && mode == AssemblyExecutionMode.AotBaseline,
                "M06 OFF API output was not reset.");
            M04ReferenceProbe.AssemblyIdentity mscorlib = input.player.assemblyIdentities.SingleOrDefault(identity => identity != null && identity.name == "mscorlib");
            Require(mscorlib != null, "M06 feature-off ordinary compatibility requires the linked mscorlib identity.");
            result.ordinary = M04OrdinaryAssemblyProbe.Run(mscorlib.path, mscorlib.sha256, mscorlib.fullName, mscorlib.mvid);
            Require(result.ordinary.loadedNameSame && result.ordinary.enumeratedSame && result.ordinary.duplicateRejected && result.ordinary.fixedImageCallerBytesUnchanged,
                "M06 feature-off ordinary HybridCLR behavior failed.");
            result.result = "Passed";
        }

        private static void ValidateDisabledDiagnostics(AssemblyShadowDiagnostics value)
        {
            Require(value != null && value.schemaVersion == 1 && !value.enabled && value.runtimeAbiVersion == 1 &&
                value.state == "Disabled" && value.stateCode == (int)AssemblyShadowState.Disabled && value.lastError == (int)AssemblyShadowErrorCode.FeatureDisabled &&
                value.generation == 0 && value.expected == 0 && value.staged == 0 && value.retainedBytes == 0 && value.enumerationGeneration == 0 && value.classEnumerationGeneration == 0 &&
                value.detail == "" && value.baselineBuildId == "" && value.patchId == "" &&
                value.assemblies != null && value.assemblies.Length == 0 && value.events != null && value.events.Length == 0 &&
                value.ordinaryAssemblies != null && value.ordinaryAssemblies.Length == 0 && value.ordinaryClasses != null && value.ordinaryClasses.Length == 0 &&
                value.baselineUses != null && value.baselineUses.Length == 0 && value.closureLoadOrder != null && value.closureLoadOrder.Length == 0 &&
                value.stableAotNames != null && value.stableAotNames.Length == 0 && value.commitOrder != null && value.commitOrder.Length == 0,
                "M06 OFF transaction diagnostics changed the preserved schema-1 disabled contract.");
        }

        private static void RunBaselineRecovery(Result result, Input input)
        {
            string failed = Argument("-shadowM06FailedResult", "");
            Require(!string.IsNullOrEmpty(failed) && File.Exists(failed), "M06 baseline recovery requires a failed result file.");
            Result failedResult = ReadJson<Result>(File.ReadAllText(failed));
            Require(failedResult != null && failedResult.mode == "T06-09-InitializerFailure" && failedResult.result == "Passed" &&
                failedResult.commitCode == (int)AssemblyShadowErrorCode.ModuleInitializerFailed && failedResult.stateCode == (int)AssemblyShadowState.FailedAfterCommit &&
                !failedResult.businessLaunched && failedResult.processId != Process.GetCurrentProcess().Id && failedResult.baselineBuildId == input.manifest.baselineBuildId,
                "M06 baseline recovery is not bound to the controlled failed initializer transaction.");
            Require(Absolute(failedResult.fixtureManifestPath) == input.manifestPath && failedResult.fixtureManifestSha256 == HashFile(input.manifestPath),
                "M06 baseline recovery fixture manifest binding differs from the verified input.");
            Require(Absolute(failedResult.playerBuildReceiptPath) == input.playerReceiptPath && failedResult.playerBuildReceiptSha256 == HashFile(input.playerReceiptPath),
                "M06 baseline recovery Player receipt binding differs from the verified input.");
            Require(failedResult.il2cpp && failedResult.buildGuid == input.player.buildGuid && failedResult.runtimeAbiHash == input.player.runtimeAbiHash &&
                failedResult.patchId == "InitializerFailure" && failedResult.patchManifestSha256 == input.manifest.initializerFailureFixture.patchManifestSha256 &&
                failedResult.compileSnapshotHash == input.manifest.initializerFailureFixture.compileSnapshotHash && failedResult.executionProofSha256 == input.player.executionProofSha256 &&
                failedResult.stageOrder.SequenceEqual(input.manifest.initializerFailureFixture.closureLoadOrder), "M06 failed-result native/patch identity differs.");
            VerifyBytes(failedResult.rawTransactionDiagnosticsPath, failedResult.rawTransactionDiagnosticsSha256, "failed transaction raw evidence");
            VerifyBytes(failedResult.rawExecutionDiagnosticsPath, failedResult.rawExecutionDiagnosticsSha256, "failed execution raw evidence");
            Require(File.ReadAllText(failedResult.rawTransactionDiagnosticsPath) == failedResult.nativeDiagnosticsJson &&
                File.ReadAllText(failedResult.rawExecutionDiagnosticsPath) == failedResult.executionDiagnosticsJson,
                "M06 failed native evidence does not prove the sealed failure.");
            ValidateJsonShape(new ProofJsonReader(failedResult.nativeDiagnosticsJson).Read(), typeof(AssemblyShadowDiagnostics), "failedTransaction");
            ValidateJsonShape(new ProofJsonReader(failedResult.executionDiagnosticsJson).Read(), typeof(AssemblyShadowExecutionDiagnostics), "failedExecution");
            var retained = AssemblyShadowDiagnostics.Parse(failedResult.nativeDiagnosticsJson);
            var retainedExecution = AssemblyShadowExecutionDiagnostics.Parse(failedResult.executionDiagnosticsJson);
            ValidateRetainedInitializerFailure(retained, input.manifest.initializerFailureFixture, input.manifest.baselineBuildId);
            Require(retainedExecution.enabled && retainedExecution.stateCode == (int)AssemblyShadowState.FailedAfterCommit && retainedExecution.state == "FailedAfterCommit" &&
                retainedExecution.generation == retained.generation && retainedExecution.rejectedBaselineMethods == 0 && retainedExecution.droppedClassObservations == 0,
                "M06 retained execution diagnostics differ from the failed transaction.");
            Require(failedResult.transactionSnapshots != null && failedResult.transactionSnapshots.Count > 0 && failedResult.executionSnapshots != null && failedResult.executionSnapshots.Count > 0 &&
                failedResult.transactionSnapshots.Last().rawJson == failedResult.nativeDiagnosticsJson && failedResult.executionSnapshots.Last().rawJson == failedResult.executionDiagnosticsJson &&
                JsonUtility.ToJson(failedResult.transactionSnapshots.Last().diagnostics) == JsonUtility.ToJson(retained) &&
                JsonUtility.ToJson(failedResult.executionSnapshots.Last().diagnostics) == JsonUtility.ToJson(retainedExecution), "M06 retained typed/raw final failure snapshots disagree.");
            RequireState(result, AssemblyShadowState.Disabled, "baseline-recovery");
            result.recoveryResultPath = Absolute(failed);
            result.recoveryResultSha256 = HashFile(failed);
            Type type = WitnessType(Internal);
            string[] values = InvokeRun(type, "new");
            ValidateBusinessValues(Internal, "BASELINE", "new", values, 0, null);
            AssemblyExecutionMode recoveryMode;
            int recoveryCode = (int)AssemblyShadowRuntime.GetAssemblyExecutionMode(Internal, out recoveryMode);
            RecordCheck(result, "GetAssemblyExecutionMode:recovery", recoveryCode, AssemblyShadowErrorCode.CandidateNotRegistered, recoveryMode.ToString(), "AotBaseline");
            Require(recoveryMode == AssemblyExecutionMode.AotBaseline, "Recovery did not execute the actual baseline.");
            AddObservation(result, Internal, type, recoveryMode, "baseline-recovery", values, AssemblyShadowErrorCode.CandidateNotRegistered);
            CaptureTransaction(result, "baseline-recovery"); CaptureExecution(result, "baseline-recovery");
            result.businessLaunched = true;
        }

        private static void ValidateRetainedInitializerFailure(AssemblyShadowDiagnostics value, Fixture fixture, string baselineBuildId)
        {
            Require(value != null && value.schemaVersion == 1 && value.enabled && value.runtimeAbiVersion == RuntimeAbiVersion &&
                value.stateCode == (int)AssemblyShadowState.FailedAfterCommit && value.state == "FailedAfterCommit" && value.lastError == (int)AssemblyShadowErrorCode.ModuleInitializerFailed &&
                value.baselineBuildId == baselineBuildId && value.patchId == fixture.patchId && fixture.patchId == "InitializerFailure" && value.generation > 0 &&
                value.closureLoadOrder != null && value.closureLoadOrder.SequenceEqual(fixture.closureLoadOrder) && value.assemblies != null &&
                value.expected == (ulong)fixture.closureLoadOrder.Length && value.staged == value.expected, "M06 raw transaction does not prove this initializer failure.");
            RequireSet(value.assemblies.Select(row => row.name), fixture.closureLoadOrder, "failed transaction image inventory");
            foreach (var row in value.assemblies)
            {
                var patch = fixture.patch.closure.Single(item => item.name == row.name);
                Require(row.mvid == patch.mvid && row.skeletonBuilt && row.runtimeMetadataInitialized && row.published &&
                    row.moduleInitializerAttempted && !row.moduleInitializerRan, "M06 raw transaction lacks the exact attempted/failed initializer image.");
            }
        }

        private static string TypeInfo(Result result, Type type)
        {
            string json; result.typeResolutionCode = (int)AssemblyShadowRuntime.GetTypeResolutionInfo(type, out json);
            RecordCheck(result, "GetTypeResolutionInfo:" + type.FullName, result.typeResolutionCode, AssemblyShadowErrorCode.Success, "", "");
            AssemblyShadowTypeResolutionInfo info;
            Require(AssemblyShadowTypeResolutionInfo.TryParse(json, out info), "M06 type-resolution JSON is malformed.");
            return json;
        }

        private static ulong LatestExecutionTransformations(Result result)
        {
            ExecutionSnapshot snapshot = result.executionSnapshots.LastOrDefault();
            return snapshot == null || snapshot.diagnostics == null ? 0UL : snapshot.diagnostics.interpreterTransformations;
        }

        private static ulong LatestShadowTransformations(Result result)
        {
            ExecutionSnapshot snapshot = result.executionSnapshots.LastOrDefault();
            return snapshot == null || snapshot.diagnostics == null ? 0UL : snapshot.diagnostics.shadowInterpreterTransformations;
        }

        private static void AddTiming(Result result, string phase, long start, long end, ulong totalBefore, ulong totalAfter, ulong shadowBefore, ulong shadowAfter)
        {
            result.timings.Add(new TimingObservation { phase = phase, stopwatchFrequency = Stopwatch.Frequency, startTicks = start, endTicks = end,
                elapsedTicks = end - start, transformationsBefore = totalBefore, transformationsAfter = totalAfter,
                shadowTransformationsBefore = shadowBefore, shadowTransformationsAfter = shadowAfter });
        }

        private static void AddModuleObservation(Result result, Type type, Assembly assembly, string phase)
        {
            string[] values = InvokeModuleEvidence(type);
            int moduleCount = ParseModuleInt(values, "module.count=");
            long start = ParseModuleLong(values, "module.startTicks=");
            long end = ParseModuleLong(values, "module.endTicks=");
            long frequency = ParseModuleLong(values, "module.frequency=");
            int providerCount = ParseModuleInt(values, "provider.count=");
            string providerMarker = ParseModuleValue(values, "provider.marker=");
            Require(moduleCount >= 0 && providerCount >= 0 && frequency >= 0 && end >= start, "M06 module initializer evidence is malformed: " + assembly.GetName().Name);
            result.moduleObservations.Add(new ModuleObservation { phase = phase, assemblyName = assembly.GetName().Name, moduleName = ObservedModuleName(assembly), providerAssembly = ParseModuleValue(values, "provider.assembly="),
                values = values, moduleCount = moduleCount, providerCount = providerCount, providerMarker = providerMarker,
                initializerStartTicks = start, initializerEndTicks = end, initializerStopwatchFrequency = frequency });
        }

        private static string ObservedModuleName(Assembly assembly)
        {
            // The pinned IL2CPP supports GetModulesInternal for both AOT and shadow
            // images; ManifestModule is supported only for active shadow images.
            Module[] modules = assembly.GetModules();
            Require(modules != null && modules.Length == 1 && modules[0] != null && !string.IsNullOrEmpty(modules[0].Name),
                "M06 expected exactly one actual named runtime module.");
            return modules[0].Name;
        }

        private static int ParseModuleInt(string[] values, string prefix)
        {
            long value = ParseModuleLong(values, prefix);
            Require(value >= int.MinValue && value <= int.MaxValue, "M06 module integer evidence overflow: " + prefix);
            return (int)value;
        }

        private static long ParseModuleLong(string[] values, string prefix)
        {
            string value = ParseModuleValue(values, prefix);
            long parsed;
            Require(long.TryParse(value, out parsed), "M06 module numeric evidence is missing: " + prefix);
            return parsed;
        }

        private static string ParseModuleValue(string[] values, string prefix)
        {
            string value = (values ?? new string[0]).SingleOrDefault(item => item != null && item.StartsWith(prefix, StringComparison.Ordinal));
            Require(value != null, "M06 module evidence is missing: " + prefix);
            return value.Substring(prefix.Length);
        }

        private static string PhaseFor(string mode)
        {
            if (mode.StartsWith("T06-01-", StringComparison.Ordinal)) return "new";
            if (mode.StartsWith("T06-02-", StringComparison.Ordinal)) return "statics";
            if (mode.StartsWith("T06-06-", StringComparison.Ordinal)) return "delegates";
            if (mode.StartsWith("T06-07-", StringComparison.Ordinal)) return "generics";
            if (mode.StartsWith("T06-08-", StringComparison.Ordinal)) return "async";
            return "dispatch";
        }

        private static bool ModeIsWarmup(string mode) { return mode.StartsWith("T06-10-", StringComparison.Ordinal); }

        private static Type WitnessType(string assemblyName)
        {
            switch (assemblyName)
            {
                case Contracts: return Type.GetType("AssemblyA.Contracts.M06ExecutionWitness, AssemblyA.Contracts", true);
                case Extensibility: return Type.GetType("AssemblyA.Implementation.Extensibility.M06ExecutionWitness, AssemblyA.Implementation.Extensibility", true);
                case Internal: return Type.GetType("AssemblyA.Implementation.Internal.M06ExecutionWitness, AssemblyA.Implementation.Internal", true);
                case ContractsConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness, AssemblyShadowDemo.ContractsConsumer", true);
                case ExtensibilityConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness, AssemblyShadowDemo.ExtensibilityConsumer", true);
                default: throw new ArgumentException("Unknown M06 witness assembly: " + assemblyName);
            }
        }

        private static Assembly LoadWitnessAssembly(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA.Contracts");
                case Extensibility: return Assembly.Load("AssemblyA.Implementation.Extensibility");
                case Internal: return Assembly.Load("AssemblyA.Implementation.Internal");
                case ContractsConsumer: return Assembly.Load("AssemblyShadowDemo.ContractsConsumer");
                case ExtensibilityConsumer: return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer");
                default: throw new ArgumentException("Unknown M06 witness assembly: " + name);
            }
        }

        private static string[] InvokeRun(Type type, string phase)
        {
            MethodInfo method = type.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
            Require(method != null && method.ReturnType == typeof(string[]), "M06 witness Run signature is invalid.");
            return (string[])method.Invoke(null, new object[] { phase });
        }

        private static IEnumerator ObserveExecutionCoroutine(Result result, Input input, Fixture fixture)
        {
            CaptureExecution(result, "business-before");
            long start = Stopwatch.GetTimestamp();
            ulong totalBefore = LatestExecutionTransformations(result), shadowBefore = LatestShadowTransformations(result);
            bool comparison = ModeIsWarmup(result.mode) || result.mode.StartsWith("T06-12-", StringComparison.Ordinal);
            foreach (string name in Candidates)
            {
                Assembly assembly = LoadWitnessAssembly(name);
                Type type = WitnessType(name);
                bool shadow = fixture.closureLoadOrder.Contains(name, StringComparer.Ordinal);
                AssemblyExecutionMode mode;
                int code = (int)AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                RecordCheck(result, "GetAssemblyExecutionMode:" + name, code, AssemblyShadowErrorCode.Success, mode.ToString(),
                    shadow ? "InterpreterShadow" : "AotBaseline");
                Require(mode == (shadow ? AssemblyExecutionMode.InterpreterShadow : AssemblyExecutionMode.AotBaseline), "M06 physical execution world differs: " + name);
                string infoJson = TypeInfo(result, type);
                var info = AssemblyShadowTypeResolutionInfo.Parse(infoJson);
                Require(info.logicalAssembly == name && info.isActive && info.executionModeCode == (int)mode &&
                    info.physicalImageKind == (shadow ? "Interpreter" : "Aot") && System.Object.ReferenceEquals(type, WitnessType(name)), "M06 active type identity differs: " + name);
                AddObservation(result, name, type, mode, "mode", new string[0]);
                AddModuleObservation(result, type, assembly, "before-business");
                string[] phases = comparison ? new[] { "new", "dispatch", "generics" } : new[] { PhaseFor(result.mode) };
                foreach (string phase in phases)
                {
                    string[] firstValues = null;
                    for (int invocation = 0; invocation < 2; ++invocation)
                    {
                        string boundary = name + "-" + phase + "-" + invocation;
                        CaptureExecution(result, boundary + "-before");
                        ulong before = LatestExecutionTransformations(result), beforeShadow = LatestShadowTransformations(result);
                        long callStart = Stopwatch.GetTimestamp();
                        string[] values;
                        if (phase == "async")
                        {
                            var output = new List<string>();
                            IEnumerator async = InvokeAsyncCoroutine(type, output);
                            try { while (async.MoveNext()) yield return async.Current; }
                            finally { DisposeIterator(async); }
                            values = output.ToArray();
                        }
                        else values = InvokeRun(type, phase);
                        long callEnd = Stopwatch.GetTimestamp();
                        CaptureExecution(result, boundary + "-after");
                        if (shadow && phase != "async" && (invocation == 1 || ModeIsWarmup(result.mode)))
                            Require(LatestShadowTransformations(result) == beforeShadow, "M06 warmed/repeated synchronous path still transformed shadow IL: " + boundary);
                        AddTiming(result, invocation == 0 ? "first" : "second", callStart, callEnd, before, LatestExecutionTransformations(result), beforeShadow, LatestShadowTransformations(result));
                        if (phase == "dispatch" || phase == "generics")
                            AddTiming(result, phase == "dispatch" ? "virtual" : "generic", callStart, callEnd, before, LatestExecutionTransformations(result), beforeShadow, LatestShadowTransformations(result));
                        ValidateBusinessValues(name, shadow ? fixture.patchId : "BASELINE", phase, values, invocation, firstValues);
                        AddObservation(result, name, type, mode, invocation == 0 ? phase : "second-" + phase, values);
                        if (invocation == 0) firstValues = values;
                    }
                }
                MethodInfo run = type.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
                Require(run != null, "M06 literal Run method is missing.");
                RequireMethodProof(input, fixture, name, run, shadow);
                result.methodObservations.Add(new MethodObservation { phase = "business", assemblyName = name, actualDeclaringType = run.DeclaringType.FullName,
                    name = run.Name, signature = run.ToString(), metadataToken = run.MetadataToken });
                string[] exceptions = InvokeRun(type, "exceptions");
                ValidateExceptionEvidence(input, fixture, name, type, exceptions, shadow);
                AddObservation(result, name, type, mode, "exceptions", exceptions);
                AddModuleObservation(result, type, assembly, "after-business");
                if (PhaseFor(result.mode) == "async")
                {
                    var values = new List<string>();
                    IEnumerator coroutine = InvokeCoroutine(type, values);
                    int yielded = 0, firstFrame = Time.frameCount;
                    try { while (coroutine.MoveNext()) { ++yielded; yield return coroutine.Current; } }
                    finally { DisposeIterator(coroutine); }
                    Require(yielded > 0 && Time.frameCount > firstFrame, "M06 coroutine did not resume through a later Unity frame.");
                    Require(ParseModuleValue(values.ToArray(), "coroutine.begin=") == ExpectedMarker(shadow ? fixture.patchId : "BASELINE") &&
                        ParseModuleInt(values.ToArray(), "coroutine.continuation=") == ExpectedGeneration(name, shadow ? fixture.patchId : "BASELINE") + 1,
                        "M06 coroutine continuation executed the wrong body.");
                    values.Add("driver.yields=" + yielded); values.Add("driver.frameDelta=" + (Time.frameCount - firstFrame)); values.Add("driver.disposed=true");
                    AddObservation(result, name, type, mode, "coroutine", values.ToArray());
                }
            }
            CaptureExecution(result, "business-after");
            AddTiming(result, "business", start, Stopwatch.GetTimestamp(), totalBefore, LatestExecutionTransformations(result), shadowBefore, LatestShadowTransformations(result));
            ValidateModuleOrder(result, fixture);
        }

        private static void AddObservation(Result result, string name, Type type, AssemblyExecutionMode mode, string phase, string[] values, AssemblyShadowErrorCode expectedCode = AssemblyShadowErrorCode.Success)
        {
            AssemblyExecutionMode observed;
            int code = (int)AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out observed);
            result.executionModeCode = code; result.executionMode = observed.ToString();
            RecordCheck(result, "GetAssemblyExecutionMode:" + phase + ":" + name, code, expectedCode, observed.ToString(), mode.ToString());
            result.observations.Add(new ExecutionObservation { phase = phase, assemblyName = name, witness = type.FullName,
                typeInfoJson = TypeInfo(result, type), executionCode = code, mode = observed.ToString(),
                repeatedSameType = System.Object.ReferenceEquals(type, WitnessType(name)), values = values });
        }

        private static string ExpectedMarker(string patch) { return "M06-" + patch; }
        private static int ExpectedGeneration(string name, string patch)
        {
            if (patch == "BASELINE") return 1000;
            if (patch == "P01") { Require(name == Internal, "P01 only replaces Internal."); return 5000; }
            if (patch == "P02")
            {
                if (name == Extensibility) return 5000; if (name == Internal) return 6000; if (name == ExtensibilityConsumer) return 9000;
            }
            if (patch == "P03")
            {
                if (name == Contracts || name == Extensibility) return 6000; if (name == Internal) return 7000;
                if (name == ContractsConsumer) return 8000; if (name == ExtensibilityConsumer) return 10000;
            }
            throw new InvalidOperationException("M06 unexpected business generation: " + name + "/" + patch);
        }

        private static void ValidateBusinessValues(string name, string patch, string phase, string[] values, int invocation, string[] first)
        {
            Require(values != null && values.All(item => item != null && item.IndexOf('=') > 0), "M06 business evidence is malformed.");
            string marker = ExpectedMarker(patch); int generation = ExpectedGeneration(name, patch);
            Func<string, string> value = key => ParseModuleValue(values, key + "=");
            Action<string, string> equal = (key, expected) => Require(value(key) == expected, "M06 " + name + "/" + phase + "/" + key + " expected " + expected + ", got " + value(key));
            if (phase != "async") equal("phase", phase);
            if (phase == "new")
            {
                int offset = name == Contracts ? 10 : name == Extensibility ? 20 : name == Internal ? 30 : name == ContractsConsumer ? 40 : 50;
                equal("marker", marker); equal("ctor", (generation + offset).ToString()); equal("ctor.first", value("ctor")); equal("ctor.second", value("ctor"));
                equal("ctor.count", "2"); equal("helper.count", "2"); equal("field", marker + ":field"); equal("interface", marker + ":interface"); equal("event", marker + ":event:1");
            }
            else if (phase == "statics")
            {
                equal("marker", marker); equal("cctor", "1"); equal("generic.int", (invocation * 2 + 1).ToString()); equal("generic.string", value("generic.int"));
                equal("generic.int.repeat", (invocation * 2 + 2).ToString()); equal("generic.string.repeat", value("generic.int.repeat"));
                equal("explicit.value", (invocation + 2).ToString()); equal("beforefieldinit.flag", "True"); equal("beforefieldinit.count", "2");
                equal("beforefieldinit.int.first", value("beforefieldinit.int.repeat")); equal("beforefieldinit.string.first", value("beforefieldinit.string.repeat"));
                int intValue = ParseModuleInt(values, "beforefieldinit.int.first="), stringValue = ParseModuleInt(values, "beforefieldinit.string.first=");
                Require(new[] { intValue - generation - 5, stringValue - generation - 6 }.OrderBy(number => number).SequenceEqual(new[] { 1, 2 }),
                    "M06 closed generic statics did not initialize independently.");
                if (first != null) foreach (string key in new[] { "beforefieldinit.int.first=", "beforefieldinit.string.first=" }) Require(ParseModuleValue(first, key) == ParseModuleValue(values, key), "M06 static initialized twice.");
            }
            else if (phase == "dispatch")
            {
                equal("virtual", marker + (name == Contracts || name == ContractsConsumer ? ":virtual" : ":sealed")); equal("interface", marker + ":interface");
                if (name == Internal || name == Extensibility || name == ExtensibilityConsumer) { equal("abstract", marker + ":abstract"); equal("assignable", "True"); }
            }
            else if (phase == "delegates")
            {
                equal("instance", marker + ":I2"); equal("static", marker + ":S2"); equal("closed", marker + ":I3");
                // Contracts exercises Action multicast and returns its instance delegate separately;
                // the other four exercise Func multicast's last-return-value semantics.
                equal("multicast", marker + (name == Contracts ? ":I2" : ":S2"));
                equal("invocation.count", "2"); equal("handler.first", "2"); equal("handler.second", "1"); equal("event.beforeRemove", "2"); equal("event.afterRemove", "2"); equal("event.removed", "True");
            }
            else if (phase == "generics")
            {
                equal("generic.value", "4"); equal("method", marker); equal("nullable", "4"); equal("boxed", "4"); equal("generic.method", "6"); equal("array", "2");
                int input = name == Internal ? generation + 4 : 4;
                equal("ref", (input + 2).ToString()); equal("out", (input + 3).ToString());
                Require(value("generic.type").Contains("DemoValue"), "M06 generic reflection closed over the wrong type.");
                if (name == Internal) equal("struct", (generation + 4).ToString());
            }
            else if (phase == "async")
            {
                equal("marker", marker); equal("cancel", "TaskCanceledException"); equal("async.throw", marker + ":async");
                equal("iterator.moveNext", "True"); equal("iterator.value", generation.ToString()); equal("iterator.finally", "true"); equal("iterator.disposed", "true");
                Require(!values.Contains("iterator.after=true"), "M06 iterator did not dispose at its suspension point.");
            }
            else throw new InvalidOperationException("M06 unknown business phase.");
            if (first != null && phase != "statics") Require(first.SequenceEqual(values), "M06 repeated execution changed deterministic business values.");
        }

        private static string[] InvokeAsync(Type type)
        {
            MethodInfo method = type.GetMethod("RunAsync", BindingFlags.Public | BindingFlags.Static);
            Require(method != null, "M06 async witness is missing.");
            Task<string[]> task = (Task<string[]>)method.Invoke(null, null);
            Require(task.IsCompleted, "M06 async witness must be driven by the coroutine path.");
            return task.GetAwaiter().GetResult();
        }

        private static IEnumerator InvokeAsyncCoroutine(Type type, List<string> values)
        {
            MethodInfo method = type.GetMethod("RunAsync", BindingFlags.Public | BindingFlags.Static);
            Require(method != null, "M06 async witness is missing.");
            Task<string[]> task = (Task<string[]>)method.Invoke(null, null);
            while (!task.IsCompleted) yield return null;
            if (task.IsCanceled) throw new InvalidOperationException("M06 async witness was canceled.");
            if (task.IsFaulted) throw task.Exception == null ? new InvalidOperationException("M06 async witness failed.") : task.Exception.InnerException ?? task.Exception;
            string[] returned = task.GetAwaiter().GetResult();
            if (returned != null) values.AddRange(returned);
        }

        private static IEnumerator InvokeCoroutine(Type type, List<string> values)
        {
            MethodInfo method = type.GetMethod("RunCoroutine", BindingFlags.Public | BindingFlags.Static);
            Require(method != null, "M06 coroutine witness is missing.");
            return (IEnumerator)method.Invoke(null, new object[] { values });
        }

        private static string[] InvokeModuleEvidence(Type type)
        {
            MethodInfo method = type.GetMethod("GetModuleEvidence", BindingFlags.Public | BindingFlags.Static);
            Require(method != null, "M06 module evidence witness is missing.");
            return (string[])method.Invoke(null, null);
        }

        private static Fixture SelectFixture(FixtureManifest manifest, string mode)
        {
            string id = mode.Contains("P02") ? "P02" : mode.Contains("P03") || mode == "T06-13-ReleaseNoPdb" ? "P03" : "P01";
            return manifest.fixtures.SingleOrDefault(fixture => fixture.patchId == id);
        }

        private static Result NewResult(string mode, string baseline, string abi)
        {
            return new Result { schemaVersion = 1, milestone = "M06", mode = mode, result = "Failed", error = "", il2cpp = IsIl2CppPlayer(),
                configureCode = -1, beginCode = -1, validateCode = -1, commitCode = -1, abortCode = -1, stateCode = -1, executionModeCode = -1,
                diagnosticsCode = -1, executionDiagnosticsCode = -1, typeResolutionCode = -1,
                processId = Process.GetCurrentProcess().Id, unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, baselineBuildId = baseline, runtimeAbiHash = abi, moduleMvidObservationPolicy = MvidPolicy,
                stageOrder = new string[0], checks = new List<Check>(), transactionSnapshots = new List<TransactionSnapshot>(), executionSnapshots = new List<ExecutionSnapshot>(),
                observations = new List<ExecutionObservation>(), methodObservations = new List<MethodObservation>(), moduleObservations = new List<ModuleObservation>(),
                warmupObservations = new List<WarmupObservation>(), timings = new List<TimingObservation>(), supplementaryMetadata = new List<SupplementaryMetadataObservation>(),
                stageResults = new List<StageResult>() };
        }

        private static bool IsKnownMode(string mode) { return Modes.Contains(mode, StringComparer.Ordinal); }
        private static string Argument(string name, string fallback) { string[] args = Environment.GetCommandLineArgs(); for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == name) return args[i + 1]; return fallback; }
        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }
        private static string Hash(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        private static void RequireCode(int actual, AssemblyShadowErrorCode expected, string operation) { Require(actual == (int)expected, "M06 " + operation + " returned " + actual + ", expected " + (int)expected + "."); }
        private static void RequireState(Result result, AssemblyShadowState expected, string operation)
        {
            AssemblyShadowState actual; int code = (int)AssemblyShadowRuntime.GetState(out actual);
            RecordCheck(result, "GetState:" + operation, code, AssemblyShadowErrorCode.Success, actual.ToString(), expected.ToString());
            result.stateCode = (int)actual; result.state = actual.ToString(); Require(actual == expected, "M06 " + operation + " state mismatch: " + actual);
        }
        private static void RecordCheck(Result result, string name, int actualCode, AssemblyShadowErrorCode expectedCode, string actual, string expected)
        {
            result.checks.Add(new Check { name = name, actualCode = actualCode, expectedCode = (int)expectedCode, actual = actual, expected = expected });
            RequireCode(actualCode, expectedCode, name);
            Require(actual == expected, "M06 " + name + " returned an unexpected value: " + actual);
        }
        private static void Require(bool condition, string message) { if (!condition) throw new InvalidOperationException(message); }

        [Serializable, Preserve] public sealed class Result
        {
            [Preserve] public int schemaVersion, processId, configureCode, beginCode, validateCode, commitCode, abortCode, stateCode, executionModeCode, diagnosticsCode, executionDiagnosticsCode, typeResolutionCode;
            [Preserve] public string milestone, mode, result, error, unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash, variant, moduleMvidObservationPolicy;
            [Preserve] public bool il2cpp, developmentBuild, businessLaunched;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256, generationProofPath, generationProofSha256, executionProofPath, executionProofSha256;
            [Preserve] public string patchId, patchManifestPath, patchManifestSha256, compileSnapshotHash, state, executionMode, nativeDiagnosticsJson, executionDiagnosticsJson, rawTransactionDiagnosticsPath, rawTransactionDiagnosticsSha256, rawExecutionDiagnosticsPath, rawExecutionDiagnosticsSha256, recoveryResultPath, recoveryResultSha256;
            [Preserve] public string[] stageOrder;
            [Preserve] public List<Check> checks;
            [Preserve] public List<TransactionSnapshot> transactionSnapshots;
            [Preserve] public List<ExecutionSnapshot> executionSnapshots;
            [Preserve] public List<ExecutionObservation> observations;
            [Preserve] public List<MethodObservation> methodObservations;
            [Preserve] public List<ModuleObservation> moduleObservations;
            [Preserve] public List<WarmupObservation> warmupObservations;
            [Preserve] public List<TimingObservation> timings;
            [Preserve] public List<SupplementaryMetadataObservation> supplementaryMetadata;
            [Preserve] public List<StageResult> stageResults;
            [Preserve] public M04OrdinaryAssemblyProbe.Result ordinary;
        }

        [Serializable, Preserve] public sealed class FixtureManifest
        {
            [Preserve] public int schemaVersion;
            [Preserve] public bool developmentBuild;
            [Preserve] public string milestone, unityVersion, target, architecture, baselineManifestPath, baselineManifestSha256, baselineBuildId, runtimeAbiHash, baselineInputSnapshot, baselineInputSnapshotHash, stableAotProvenanceHash, stableAotProvenance, generationProofPath, generationProofSha256;
            [Preserve] public string[] candidateNames, closureLoadOrder, stableAotNames;
            [Preserve] public Fixture[] fixtures;
            [Preserve] public Fixture initializerFailureFixture;
        }

        [Serializable, Preserve] public sealed class Fixture
        {
            [Preserve] public string patchId, compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256, variant, generationPlanPath, generationPlanSha256;
            [Preserve] public bool developmentBuild;
            [Preserve] public string[] defines, changedRoots, closureLoadOrder, stableAotNames, requiredAotMetadataNames;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity[] assemblyIdentities;
            [Preserve] public M05TypeProbe.TypeInventory[] typeInventories;
            [Preserve, NonSerialized] internal PatchManifest patch;
            [Preserve, NonSerialized] internal WarmupPlan warmup;
        }

        [Serializable, Preserve] public sealed class PlayerBuildReceipt
        {
            [Preserve] public int schemaVersion, nativeMetadataVersion, buildOptions;
            [Preserve] public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput, inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments, placeholderManifestPath, placeholderManifestSha256, nativeMetadataPath, nativeMetadataSha256, typeProofPath, typeProofSha256, generationProofPath, generationProofSha256, executionProofPath, executionProofSha256;
            [Preserve] public bool developmentBuild;
            [Preserve] public string[] placeholderAssemblyNames, nativeGeneratedAssemblyNames;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity[] assemblyIdentities;
            [Preserve] public M04ReferenceProbe.NativeAssemblyIdentity[] nativeAssemblyIdentities;
            [Preserve] public SupplementaryMetadataInput[] supplementaryMetadataInputs;
        }

        [Serializable, Preserve] public sealed class SupplementaryMetadataInput
        {
            [Preserve] public string assemblyName, path, sha256;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity identity;
        }

        [Serializable, Preserve] public sealed class Check { [Preserve] public string name, actual, expected; [Preserve] public int actualCode, expectedCode; }
        [Serializable, Preserve] public sealed class StageResult { [Preserve] public string name, dllSha256, pdbSha256; [Preserve] public int code; }
        [Serializable, Preserve] public sealed class TransactionSnapshot { [Preserve] public string phase, rawJson; [Preserve] public AssemblyShadowDiagnostics diagnostics; }
        [Serializable, Preserve] public sealed class ExecutionSnapshot { [Preserve] public string phase, rawJson; [Preserve] public AssemblyShadowExecutionDiagnostics diagnostics; }
        [Serializable, Preserve] public sealed class ExecutionObservation { [Preserve] public string phase, assemblyName, witness, typeInfoJson, mode; [Preserve] public int executionCode; [Preserve] public bool repeatedSameType; [Preserve] public string[] values; }
        [Serializable, Preserve] public sealed class MethodObservation { [Preserve] public string phase, assemblyName, actualDeclaringType, name, signature; [Preserve] public int metadataToken; }
        [Serializable, Preserve] public sealed class ModuleObservation { [Preserve] public string phase, assemblyName, moduleName, providerMarker, providerAssembly; [Preserve] public string[] values; [Preserve] public int moduleCount, providerCount; [Preserve] public long initializerStartTicks, initializerEndTicks, initializerStopwatchFrequency; }
        [Serializable, Preserve] public sealed class WarmupObservation { [Preserve] public string phase, targetKind, assemblyName, declaringType, name, returnType, actualReturn; [Preserve] public string[] genericArguments, parameterTypes; [Preserve] public int genericArity, metadataToken; [Preserve] public bool preJitClass, preJitMethod; [Preserve] public ulong transformationBefore, transformationAfter, shadowTransformationBefore, shadowTransformationAfter; [Preserve] public string[] returnedValues; }
        [Serializable, Preserve] public sealed class TimingObservation { [Preserve] public string phase; [Preserve] public long stopwatchFrequency, startTicks, endTicks, elapsedTicks; [Preserve] public ulong transformationsBefore, transformationsAfter, shadowTransformationsBefore, shadowTransformationsAfter; }
        [Serializable, Preserve] public sealed class SupplementaryMetadataObservation { [Preserve] public string assemblyName, path, sha256; [Preserve] public int resultCode; [Preserve] public bool loaded; }

        [Serializable, Preserve] public sealed class TypeProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, policy, compileSnapshotHash, linkedPlayerReceiptHash, nativeLibrarySha256, buildGuid;
            [Preserve] public bool developmentBuild;
            [Preserve] public M05TypeProbe.TypeInventory[] assemblies;
            [Preserve] public MethodWitness[] moduleMethods;
        }
        [Serializable, Preserve] public sealed class MethodWitness
        {
            [Preserve] public string declaringType, name, signature;
            [Preserve] public bool hasBody;
            [Preserve] public int implementationFlags;
            [Preserve] public string[] instructions;
        }
        [Serializable, Preserve] public sealed class ExecutionProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, policy, compileSnapshotHash, linkedPlayerReceiptHash, nativeLibrarySha256, buildGuid, generationProofPath, generationProofSha256, typeProofPath, typeProofSha256;
            [Preserve] public bool developmentBuild;
            [Preserve] public string[] apiSignatures;
            [Preserve] public EnumValue[] errorCodes;
            [Preserve] public SchemaType[] schemaTypes;
            [Preserve] public ExecutionImage[] images;
        }
        [Serializable, Preserve] public sealed class EnumValue { [Preserve] public string name; [Preserve] public int value; }
        [Serializable, Preserve] public sealed class SchemaType { [Preserve] public string side, assemblyName, assemblyIdentity, typeName; [Preserve] public int typeAttributes; [Preserve] public bool isSerializable; [Preserve] public SchemaField[] fields; }
        [Serializable, Preserve] public sealed class SchemaField { [Preserve] public string name, type, resolvedType; [Preserve] public int attributes; }
        [Serializable, Preserve] public sealed class ExecutionImage { [Preserve] public string role, planId, compileSnapshotHash, planHash, pdbPath, pdbSha256; [Preserve] public bool pdbAvailable; [Preserve] public M04ReferenceProbe.AssemblyIdentity identity; [Preserve] public ExecutionMethod[] methods; }
        [Serializable, Preserve] public sealed class ExecutionMethod
        {
            [Preserve] public string declaringType, name, signature;
            [Preserve] public int metadataToken, genericArity, methodFlags, implementationFlags, maxStack;
            [Preserve] public bool isStatic, hasBody, initLocals;
            [Preserve] public ExecutionSignatureType returnType;
            [Preserve] public ExecutionSignatureType[] parameterTypes;
            [Preserve] public string[] genericParameterNames, locals, instructions;
            [Preserve] public ExceptionHandler[] exceptionHandlers;
            [Preserve] public SequencePoint[] sequencePoints;
        }
        [Serializable, Preserve] public sealed class ExecutionSignatureType { [Preserve] public string assembly, type; }
        [Serializable, Preserve] public sealed class ExceptionHandler { [Preserve] public string handlerType, catchType; [Preserve] public int tryStart, tryEnd, filterStart, handlerStart, handlerEnd; }
        [Serializable, Preserve] public sealed class SequencePoint { [Preserve] public string document, checksumAlgorithm, checksum; [Preserve] public int instructionIndex, ilOffset, startLine, startColumn, endLine, endColumn; }

        [Serializable, Preserve] private sealed class Input
        {
            [Preserve] public string manifestPath, playerReceiptPath;
            [Preserve] public FixtureManifest manifest;
            [Preserve] public PlayerBuildReceipt player;
            [Preserve] public BaselineManifest baseline;
            [Preserve] public ExecutionProof executionProof;
            [Preserve] public GenerationProof generationProof;
        }
        [Serializable, Preserve] private sealed class BaselineManifest { [Preserve] public string baselineBuildId; [Preserve] public BaselineAssembly[] assemblies; }
        [Serializable, Preserve] private sealed class BaselineAssembly { [Preserve] public string name, mvid; }
        [Serializable, Preserve] internal sealed class PatchManifestVersion { [Preserve] public int schemaVersion; }
        [Serializable, Preserve] internal sealed class PatchManifestEnvelope { [Preserve] public int schemaVersion; [Preserve] public PatchManifest patch; [Preserve] public WarmupPlan warmup; }
        [Serializable, Preserve] internal sealed class WarmupPlan { [Preserve] public WarmupType[] types; [Preserve] public WarmupMethod[] methods; }
        [Serializable, Preserve] internal sealed class WarmupType { [Preserve] public string assembly, type; }
        [Serializable, Preserve] internal sealed class WarmupMethod { [Preserve] public string assembly, declaringType, name; [Preserve] public bool isStatic; [Preserve] public int genericArity; [Preserve] public WarmupTypeIdentity[] genericArguments, parameterTypes; [Preserve] public WarmupTypeIdentity returnType; }
        [Serializable, Preserve] internal sealed class WarmupTypeIdentity { [Preserve] public string assembly, type; }
        [Serializable, Preserve] internal sealed class PatchManifest { [Preserve] public int schemaVersion, semanticHashSchema; [Preserve] public string patchId, baselineBuildId, baselineManifestSha256, runtimeAbiHash, compileSnapshotHash; [Preserve] public string[] loadOrder; [Preserve] public PatchAssembly[] closure; }
        [Serializable, Preserve] internal sealed class PatchAssembly { [Preserve] public string name, dll, sha256, pdb, pdbSha256, mvid, baselineMvid; }
    }
}
