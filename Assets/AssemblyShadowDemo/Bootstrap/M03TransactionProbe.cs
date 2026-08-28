using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using HybridCLR;
using UnityEngine;

namespace AssemblyShadowDemo
{
    /// <summary>One real IL2CPP process per mode. No Editor simulation or baseline-use exemption.</summary>
    public static class M03TransactionProbe
    {
        private const string Contracts = "AssemblyA.Contracts";
        private const string Extensibility = "AssemblyA.Implementation.Extensibility";
        private const string Internal = "AssemblyA.Implementation.Internal";
        private static readonly string[] Candidates = {
            Contracts, Extensibility, Internal, "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"
        };

        public static int RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            string mode = ShadowPatchFileProvider.Argument("-shadowMode", "T03-01");
            var result = new ProbeResult {
                schemaVersion = 2, milestone = "M03", mode = mode, result = "Failed",
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(),
                playerBuildGuid = Application.buildGUID, playerDataPath = Application.dataPath,
                processId = System.Diagnostics.Process.GetCurrentProcess().Id,
                baselineBuildId = expectedBaselineBuildId, runtimeAbiHash = expectedRuntimeAbiHash,
#if ENABLE_IL2CPP && !UNITY_EDITOR
                il2cpp = true,
#endif
            };
            try
            {
                Require(result.il2cpp, "M03 acceptance requires an actual IL2CPP Player.");
                Require(!string.IsNullOrEmpty(expectedBaselineBuildId) && IsHash(expectedRuntimeAbiHash), "Player-embedded baseline/ABI identity is absent.");
                if (mode == "T03-09") RunFeatureDisabled(result);
                else
                {
                    FixtureInput fixture = ReadFixture(expectedBaselineBuildId, expectedRuntimeAbiHash, result);
                    if (mode == "T03-08-Fallback") RunFallback(result, fixture);
                    else RunTransaction(result, fixture);
                }
                // Only a completed mode whose assertions all returned may pass.
                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.error = error.ToString();
                Debug.LogException(error);
            }
            string output = Path.GetFullPath(ShadowPatchFileProvider.Argument("-shadowResultPath",
                Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m03-" + mode + ".json")));
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                if (!string.IsNullOrEmpty(result.nativeDiagnosticsJson))
                {
                    result.nativeDiagnosticsPath = Path.Combine(Path.GetDirectoryName(output), Path.GetFileNameWithoutExtension(output) + "-native-diagnostics.json");
                    File.WriteAllText(result.nativeDiagnosticsPath, result.nativeDiagnosticsJson);
                    result.nativeDiagnosticsSha256 = HashFile(result.nativeDiagnosticsPath);
                }
                File.WriteAllText(output, JsonUtility.ToJson(result, true));
                Debug.Log("[AssemblyShadow M03] " + result.result + ": " + output);
            }
            catch (Exception error) { Debug.LogException(error); return 2; }
            return result.result == "Passed" ? 0 : 1;
        }

        private static void RunFeatureDisabled(ProbeResult result)
        {
            AssemblyShadowState state; AssemblyExecutionMode mode; string json;
            // Invalid/null inputs deliberately establish native-OFF precedence.
            result.configure = Expect(result, "configure-null", AssemblyShadowRuntime.ConfigureCandidates(null, null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.begin = Expect(result, "begin-null-invalid-abi", AssemblyShadowRuntime.BeginTransaction(null, null, null, -1), AssemblyShadowErrorCode.FeatureDisabled);
            result.stage = Expect(result, "stage-null", AssemblyShadowRuntime.StageAssembly(null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.stateCode = Expect(result, "state", AssemblyShadowRuntime.GetState(out state), AssemblyShadowErrorCode.FeatureDisabled);
            result.state = state.ToString();
            result.executionModeCode = Expect(result, "mode-null", AssemblyShadowRuntime.GetAssemblyExecutionMode(null, out mode), AssemblyShadowErrorCode.FeatureDisabled);
            result.executionMode = mode.ToString();
            result.diagnosticsCode = Expect(result, "diagnostics", AssemblyShadowRuntime.GetDiagnosticsJson(out json), AssemblyShadowErrorCode.FeatureDisabled);
            result.nativeDiagnosticsJson = json;
            Expect(result, "configure-valid-off", AssemblyShadowRuntime.ConfigureCandidates(result.baselineBuildId, Candidates, new string[0]), AssemblyShadowErrorCode.FeatureDisabled);
            Expect(result, "stage-empty-off", AssemblyShadowRuntime.StageAssembly(new byte[0], new byte[] { 1 }), AssemblyShadowErrorCode.FeatureDisabled);
            Require(state == AssemblyShadowState.Disabled && mode == AssemblyExecutionMode.AotBaseline, "OFF out values changed.");
        }

        private static void RunTransaction(ProbeResult result, FixtureInput fixture)
        {
            string mode = result.mode;
            Require(new[] { "T03-01", "T03-02", "T03-03", "T03-04", "T03-05", "T03-06", "T03-07", "T03-08", "T03-10", "T03-11", "T03-12", "T03-13", "T03-14", "T03-15" }.Contains(mode), "Unknown M03 mode: " + mode);
            string patchId = mode == "T03-08" ? "P03-InitializerThrow" :
                new[] { "T03-02", "T03-03", "T03-07", "T03-12", "T03-15" }.Contains(mode) ? "P03" : "P01";
            PatchInput patch = fixture.Patch(patchId);
            BindPatch(result, patch);
            string[] closure = mode == "T03-03" ? new[] { Contracts, Extensibility, Internal } : patch.manifest.loadOrder;
            result.expectedClosure = closure;
            RequireState(result, "initial", AssemblyShadowState.Disabled);
            RequireNoImages(Capture(result, "initial"));
            if (mode == "T03-14") CheckBeforeConfigure(result);
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(fixture.manifest.baselineBuildId, fixture.manifest.candidateNames, fixture.manifest.stableAotNames));
            RequireState(result, "configured", AssemblyShadowState.CandidatesRegistered);
            if (mode == "T03-14") CheckBeforeBegin(result, fixture, patch);
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(patchId,
                mode == "T03-06" ? result.baselineBuildId + "-WRONG" : result.baselineBuildId, closure, 1),
                mode == "T03-06" ? AssemblyShadowErrorCode.BaselineBuildMismatch : AssemblyShadowErrorCode.Success);
            if (mode == "T03-06")
            {
                RequireState(result, "wrong-baseline", AssemblyShadowState.CandidatesRegistered);
                RequireNoImages(Capture(result, "wrong-baseline"));
                return;
            }
            RequireState(result, "begun", AssemblyShadowState.Staging);
            RequireNoImages(Capture(result, "begun"));
            var observer = new InitObserver(result);
            TextWriter previous = Console.Out;
            ThreadStress stress = null;
            Console.SetOut(observer);
            try
            {
                if (mode == "T03-04")
                {
                    byte[] dll, pdb; fixture.Patch("P03").ReadAssembly(Contracts, out dll, out pdb);
                    result.stage = Expect(result, "extra-candidate", AssemblyShadowRuntime.StageAssembly(dll, pdb), AssemblyShadowErrorCode.UnexpectedClosureMember);
                    RequireNoImages(Capture(result, "extra-rejected"));
                    AbortAndSeal(result, patch);
                    return;
                }
                if (mode == "T03-10")
                {
                    Assembly baseline = Assembly.Load(Internal);
                    PhysicalAssembly physical = InspectPhysical(baseline);
                    Require(!physical.isInterpreter && string.Equals(physical.name, Internal, StringComparison.OrdinalIgnoreCase), "Assembly.Load did not obtain the physical baseline.");
                    result.baselineUseAssemblyLoad = baseline.FullName;
                }
                if (mode == "T03-13")
                {
                    byte[] dll, pdb; patch.ReadAssembly(Internal, out dll, out pdb);
                    Require(pdb != null && pdb.Length > 0, "Corrected PDB retry needs real compiler symbols.");
                    result.badPdbStage = Expect(result, "bad-pdb", AssemblyShadowRuntime.StageAssembly(dll, new byte[] { 0x42, 0x41, 0x44 }), AssemblyShadowErrorCode.BadImage);
                    RequireNoImages(Capture(result, "bad-pdb-rejected"));
                    RequireState(result, "bad-pdb-retryable", AssemblyShadowState.Staging);
                }
                if (mode == "T03-14")
                {
                    Expect(result, "commit-before-validate", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.InvalidState);
                    Expect(result, "null-dll", AssemblyShadowRuntime.StageAssembly(null, null), AssemblyShadowErrorCode.InvalidArgument);
                    Expect(result, "bad-dll", AssemblyShadowRuntime.StageAssembly(new byte[] { 1, 2, 3 }, null), AssemblyShadowErrorCode.BadImage);
                    RequireNoImages(Capture(result, "invalid-inputs-no-images"));
                }
                if (mode == "T03-12")
                {
                    stress = new ThreadStress(fixture.manifest.stableAotNames, closure);
                    stress.Start();
                    result.stressStarted = true;
                    stress.WaitForGeneration(false);
                }
                string[] order = mode == "T03-03" ? new[] { Contracts, Extensibility } :
                    new[] { "T03-02", "T03-07", "T03-12" }.Contains(mode) ? Shuffled(closure, result) : closure;
                foreach (string name in order)
                {
                    Stage(result, patch, name);
                    CheckPrivate(Capture(result, "staged-" + name), closure, result.initializerEvents.Count);
                }
                RequireState(result, "after-stage", mode == "T03-03" ? AssemblyShadowState.Staging : AssemblyShadowState.Staged);
                result.initializersAfterStage = result.initializerEvents.Count;
                Require(result.initializersAfterStage == 0, "A real initializer ran during Stage.");
                if (mode == "T03-05")
                {
                    AssemblyShadowDiagnostics before = Capture(result, "before-duplicate");
                    byte[] dll, pdb; patch.ReadAssembly(Internal, out dll, out pdb);
                    result.duplicateStage = Expect(result, "duplicate", AssemblyShadowRuntime.StageAssembly(dll, pdb), AssemblyShadowErrorCode.DuplicateAssemblyName);
                    AssemblyShadowDiagnostics after = Capture(result, "after-duplicate");
                    Require(after.staged == before.staged && after.retainedBytes == before.retainedBytes && after.assemblies.Count(a => a.skeletonBuilt) == before.assemblies.Count(a => a.skeletonBuilt), "Duplicate Stage retained another image.");
                    AbortAndSeal(result, patch);
                    return;
                }
                if (mode == "T03-11")
                {
                    // Intentionally creates baseline Reflection handles: isolated rejection test only.
                    result.managedEnumeration = AppDomain.CurrentDomain.GetAssemblies().Select(InspectPhysical).ToArray();
                    Require(result.managedEnumeration.Any(a => string.Equals(a.name, Internal, StringComparison.OrdinalIgnoreCase) && !a.isInterpreter), "Managed enumeration did not observe baseline Internal.");
                    Require(!result.managedEnumeration.Any(a => closure.Contains(a.name, StringComparer.OrdinalIgnoreCase) && a.isInterpreter), "Managed enumeration exposed a private shadow image.");
                }
                AssemblyShadowErrorCode expectedValidation = mode == "T03-03" ? AssemblyShadowErrorCode.ClosureMemberMissing :
                    mode == "T03-10" || mode == "T03-11" ? AssemblyShadowErrorCode.BaselineAlreadyUsed : AssemblyShadowErrorCode.Success;
                result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), expectedValidation);
                AssemblyShadowDiagnostics validated = Capture(result, "after-validate");
                CheckPrivate(validated, closure, result.initializerEvents.Count);
                result.initializersAfterValidate = result.initializerEvents.Count;
                Require(result.initializersAfterValidate == 0, "A real initializer ran during Validate.");
                if (expectedValidation != AssemblyShadowErrorCode.Success)
                {
                    if (mode == "T03-03") Require(validated.expected == 3 && validated.staged == 2 && !validated.assemblies.Any(a => a.runtimeMetadataInitialized), "Missing member validation initialized an incomplete closure.");
                    else Require(validated.baselineUses.Any(u => string.Equals(u.name, Internal, StringComparison.OrdinalIgnoreCase) && !string.IsNullOrEmpty(u.kind)), "Baseline use rejection lacks use evidence.");
                    AbortAndSeal(result, patch);
                    return;
                }
                RequireState(result, "validated", AssemblyShadowState.Validated);
                result.stateAtValidate = "Validated";
                Require(validated.assemblies.Length == closure.Length && validated.assemblies.All(a => a.skeletonBuilt && a.runtimeMetadataInitialized), "Validation did not initialize the full closure.");
                Require(validated.events.Where(e => e.kind == "metadata-begin").All(e => e.stagedCount == closure.Length), "Metadata began before all skeletons existed.");
                if (mode == "T03-15")
                {
                    // Validate creates real generic/array metadata; Abort must keep it private too.
                    AbortAndSeal(result, patch);
                    return;
                }
                result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), mode == "T03-08" ? AssemblyShadowErrorCode.ModuleInitializerFailed : AssemblyShadowErrorCode.Success);
                AssemblyShadowDiagnostics committed = Capture(result, "after-commit");
                Require(committed.generation == 1 && committed.enumerationGeneration == 1, "Commit must publish exactly one generation.");
                CheckOrdinary(committed, closure);
                if (closure.Length == Candidates.Length) CheckPublishedClasses(committed);
                Require(committed.assemblies.All(a => a.published), "Commit did not publish all staged assemblies.");
                Require(result.initializerEvents.All(e => e.stateCode == "Success" && e.diagnosticsCode == "Success" && e.state == "Committing" && e.generation == 1), "Initializer reentrant queries must observe Committing and active generation 1.");
                if (mode == "T03-08")
                {
                    RequireState(result, "initializer-failure", AssemblyShadowState.FailedAfterCommit);
                    Require(committed.lastError == (int)AssemblyShadowErrorCode.ModuleInitializerFailed, "Initializer failure must retain the exact native error.");
                    string[] attempted = closure.Take(Array.IndexOf(closure, Internal) + 1).ToArray();
                    Require(result.initializerEvents.Select(e => e.name).SequenceEqual(attempted), "Throwing initializer sequence differs from manifest order.");
                    Require(committed.assemblies.Single(a => string.Equals(a.name, Internal, StringComparison.OrdinalIgnoreCase)).moduleInitializerAttempted && !committed.assemblies.Single(a => string.Equals(a.name, Internal, StringComparison.OrdinalIgnoreCase)).moduleInitializerRan, "Throwing initializer was incorrectly marked successful.");
                    Expect(result, "abort-after-failure", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.AlreadyCommitted);
                    Expect(result, "commit-after-failure", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.AlreadyCommitted);
                    RequireState(result, "still-failed-after-commit", AssemblyShadowState.FailedAfterCommit);
                    WriteFallbackMarker(result, fixture, patch);
                    return;
                }
                RequireState(result, "committed", AssemblyShadowState.Committed);
                result.stateAfterCommit = "Committed";
                Require(result.initializerEvents.Select(e => e.name).SequenceEqual(closure) && result.reentrantQueries == closure.Length, "Initializers must run once each in manifest dependency order.");
                Require(committed.commitOrder.SequenceEqual(closure, StringComparer.OrdinalIgnoreCase) && committed.assemblies.All(a => a.moduleInitializerAttempted && a.moduleInitializerRan), "Native initializer completion differs from real managed effects.");
                if (stress != null) stress.WaitForGeneration(true);
                AssemblyExecutionMode executionMode;
                result.executionModeCode = Expect(result, "active-execution-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(Internal, out executionMode));
                result.executionMode = executionMode.ToString();
                Require(executionMode == AssemblyExecutionMode.InterpreterShadow, "Internal did not switch to shadow execution.");
                InvokeBusiness(result, true);
                Expect(result, "commit-again", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.AlreadyCommitted);
                Expect(result, "abort-after-commit", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.AlreadyCommitted);
                RequireState(result, "committed-frozen", AssemblyShadowState.Committed);
            }
            finally
            {
                Console.SetOut(previous);
                if (stress != null)
                {
                    // Every exit path stops and joins; a timeout is a failed probe, never silent success.
                    result.stressJoined = stress.StopAndJoin();
                    stress.CopyTo(result);
                    Require(result.stressJoined, "Concurrent reader did not stop within 10 seconds.");
                    Require(result.stressErrors.Length == 0, "Concurrent reader failed: " + string.Join("; ", result.stressErrors));
                    Require(result.stressBefore > 0 && result.stressAfter > 0, "Stress did not span publication.");
                }
            }
        }

        private static void CheckBeforeConfigure(ProbeResult result)
        {
            Expect(result, "stage-disabled", AssemblyShadowRuntime.StageAssembly(new byte[] { 1 }, null), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "validate-disabled", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "commit-disabled", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "abort-disabled", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "configure-null", AssemblyShadowRuntime.ConfigureCandidates(null, null, null), AssemblyShadowErrorCode.InvalidArgument);
            RequireState(result, "invalid-configure-unchanged", AssemblyShadowState.Disabled);
        }

        private static void CheckBeforeBegin(ProbeResult result, FixtureInput fixture, PatchInput patch)
        {
            Expect(result, "configure-again", AssemblyShadowRuntime.ConfigureCandidates(result.baselineBuildId, Candidates, fixture.manifest.stableAotNames), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "abi-mismatch", AssemblyShadowRuntime.BeginTransaction("bad-abi", result.baselineBuildId, patch.manifest.loadOrder, 2), AssemblyShadowErrorCode.RuntimeAbiMismatch);
            Expect(result, "duplicate-closure", AssemblyShadowRuntime.BeginTransaction("duplicate", result.baselineBuildId, new[] { Internal, Internal }, 1), AssemblyShadowErrorCode.DuplicateAssemblyName);
            Expect(result, "unknown-candidate", AssemblyShadowRuntime.BeginTransaction("unknown", result.baselineBuildId, new[] { "M03.NotRegistered" }, 1), AssemblyShadowErrorCode.CandidateNotRegistered);
            Expect(result, "empty-closure", AssemblyShadowRuntime.BeginTransaction("empty", result.baselineBuildId, new string[0], 1), AssemblyShadowErrorCode.InvalidArgument);
            AssemblyExecutionMode mode;
            Expect(result, "null-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(null, out mode), AssemblyShadowErrorCode.InvalidArgument);
            Expect(result, "unknown-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode("M03.NotRegistered", out mode), AssemblyShadowErrorCode.CandidateNotRegistered);
            RequireState(result, "begin-errors-unchanged", AssemblyShadowState.CandidatesRegistered);
            RequireNoImages(Capture(result, "begin-errors-no-images"));
        }

        private static void AbortAndSeal(ProbeResult result, PatchInput patch)
        {
            result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction());
            RequireState(result, "aborted", AssemblyShadowState.Aborted);
            AssemblyShadowDiagnostics aborted = Capture(result, "aborted");
            CheckPrivate(aborted, result.expectedClosure, result.initializerEvents.Count);
            Expect(result, "begin-after-abort", AssemblyShadowRuntime.BeginTransaction(patch.manifest.patchId, result.baselineBuildId, patch.manifest.loadOrder, 1), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "commit-after-abort", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.InvalidState);
            Expect(result, "abort-again", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.InvalidState);
            RequireState(result, "aborted-frozen", AssemblyShadowState.Aborted);
        }

        private static void Stage(ProbeResult result, PatchInput patch, string name)
        {
            byte[] dll, pdb; patch.ReadAssembly(name, out dll, out pdb);
            string code = Expect(result, "stage-" + name, AssemblyShadowRuntime.StageAssembly(dll, pdb));
            result.stageResults.Add(new StageResult { name = name, code = code, dllSha256 = ShadowPatchFileProvider.Hash(dll), pdbSha256 = pdb == null ? null : ShadowPatchFileProvider.Hash(pdb) });
        }

        private static string[] Shuffled(string[] closure, ProbeResult result)
        {
            int seed;
            Require(int.TryParse(ShadowPatchFileProvider.Argument("-shadowStageSeed", "3107"), out seed), "Invalid shuffle seed.");
            var random = new System.Random(seed);
            string[] order = closure.ToArray();
            for (int i = order.Length - 1; i > 0; --i) { int j = random.Next(i + 1); string value = order[i]; order[i] = order[j]; order[j] = value; }
            if (order.Length > 1 && order.SequenceEqual(closure)) Array.Reverse(order);
            result.stageSeed = seed;
            result.stageOrder = order;
            return order;
        }

        private static void RequireNoImages(AssemblyShadowDiagnostics diagnostics)
        {
            Require(diagnostics.staged == 0 && diagnostics.retainedBytes == 0 && diagnostics.generation == 0 &&
                !diagnostics.assemblies.Any(a => a.skeletonBuilt || a.runtimeMetadataInitialized || a.published), "Rejected input allocated or published image metadata.");
        }

        private static void CheckPrivate(AssemblyShadowDiagnostics diagnostics, string[] closure, int initializerCount)
        {
            Require(diagnostics.generation == 0 && initializerCount == 0 && diagnostics.assemblies.All(a => !a.published && !a.moduleInitializerAttempted && !a.moduleInitializerRan), "Private staging executed or published an image.");
            Require(diagnostics.classEnumerationGeneration == 0 && !diagnostics.ordinaryClasses.Any(c => c.usesStagedMetadata), "Ordinary il2cpp_class_for_each exposed private or aborted staged metadata.");
            CheckOrdinary(diagnostics, closure);
        }

        private static void CheckPublishedClasses(AssemblyShadowDiagnostics diagnostics)
        {
            Require(diagnostics.classEnumerationGeneration == 1, "Class registry did not observe active publication.");
            Require(diagnostics.ordinaryClasses.Any(c => c.usesStagedMetadata && c.isConstructedGeneric && c.typeName.Contains("M03Pair")), "Published class enumeration has no constructed M03Pair generic fixture.");
            Require(diagnostics.ordinaryClasses.Any(c => c.usesStagedMetadata && c.isConstructedGeneric && c.typeName.Contains("Nullable`1") && !c.isInterpreter), "Class enumeration did not expose the constructed AOT Nullable with staged argument after commit.");
            // SetupFields materializes these generic classes, but need not fully
            // initialize Holder itself. Do not assert an unexecuted class exists.
            // Array metadata is not required to be eagerly materialized by field layout.
            // Any array that does exist still participates in the universal privacy checks.
        }

        private static void CheckOrdinary(AssemblyShadowDiagnostics diagnostics, string[] closure)
        {
            Require(diagnostics.enumerationGeneration == 0 || diagnostics.enumerationGeneration == 1, "Ordinary enumeration observed an unexpected generation.");
            Require(diagnostics.generation <= diagnostics.enumerationGeneration, "Registry snapshot predates transaction generation.");
            Require((diagnostics.classEnumerationGeneration == 0 || diagnostics.classEnumerationGeneration == 1) && diagnostics.classEnumerationGeneration >= diagnostics.enumerationGeneration, "Class registry snapshot generation is incoherent.");
            if (diagnostics.classEnumerationGeneration == 0)
                Require(!diagnostics.ordinaryClasses.Any(c => c.usesStagedMetadata), "Concurrent class enumeration leaked private staged metadata.");
            foreach (string candidate in Candidates)
            {
                var rows = diagnostics.ordinaryAssemblies.Where(a => string.Equals(a.name, candidate, StringComparison.OrdinalIgnoreCase)).ToArray();
                Require(rows.Count(a => !a.isInterpreter) == 1, "Physical AOT registry changed for " + candidate);
                int expectedShadow = diagnostics.enumerationGeneration == 1 && closure.Contains(candidate, StringComparer.OrdinalIgnoreCase) ? 1 : 0;
                Require(rows.Count(a => a.isInterpreter) == expectedShadow, "Half-published ordinary registry at generation " + diagnostics.enumerationGeneration + ": " + candidate);
            }
        }

        private static AssemblyShadowDiagnostics Capture(ProbeResult result, string point)
        {
            string json;
            result.diagnosticsCode = Expect(result, "diagnostics-" + point, AssemblyShadowRuntime.GetDiagnosticsJson(out json));
            AssemblyShadowDiagnostics diagnostics = ParseDiagnostics(json);
            result.nativeDiagnosticsJson = json;
            result.snapshots.Add(new Snapshot { point = point, diagnostics = diagnostics });
            return diagnostics;
        }

        private static AssemblyShadowDiagnostics ParseDiagnostics(string json)
        {
            AssemblyShadowDiagnostics result = AssemblyShadowDiagnostics.Parse(json);
            Require(result.schemaVersion == 1 && result.enabled && result.runtimeAbiVersion == 1 && result.assemblies != null && result.events != null && result.ordinaryAssemblies != null && result.ordinaryClasses != null && result.baselineUses != null, "Incomplete native diagnostic schema.");
            Require(Enum.IsDefined(typeof(AssemblyShadowState), result.stateCode) && ((AssemblyShadowState)result.stateCode).ToString() == result.state, "State enum/string ABI mismatch.");
            return result;
        }

        private static void RequireState(ProbeResult result, string point, AssemblyShadowState expected)
        {
            AssemblyShadowState state;
            result.stateCode = Expect(result, "state-" + point, AssemblyShadowRuntime.GetState(out state));
            result.state = state.ToString();
            result.states.Add(point + ":" + (int)state + ":" + state);
            Require(state == expected, point + ": expected " + expected + ", got " + state);
        }

        private static string Expect(ProbeResult result, string operation, AssemblyShadowErrorCode actual, AssemblyShadowErrorCode expected = AssemblyShadowErrorCode.Success)
        {
            result.checks.Add(new Check { operation = operation, actual = actual.ToString(), expected = expected.ToString(), actualCode = (int)actual, expectedCode = (int)expected });
            Require(actual == expected, operation + ": expected " + expected + ", got " + actual);
            return actual.ToString();
        }

        private static PhysicalAssembly InspectPhysical(Assembly assembly)
        {
            // Compatibility inspection only; this does not load/activate an M01 patch.
#pragma warning disable 618
            string json = RuntimeApi.InspectAssemblyShadowPrototypeAssembly(assembly);
#pragma warning restore 618
            PhysicalAssembly result = JsonUtility.FromJson<PhysicalAssembly>(json);
            Require(result != null && !string.IsNullOrEmpty(result.name), "Physical Assembly inspection failed.");
            return result;
        }

        private static void InvokeBusiness(ProbeResult result, bool shadow)
        {
            Assembly assembly = Assembly.Load(Internal);
            PhysicalAssembly physical = InspectPhysical(assembly);
            Require(physical.isInterpreter == shadow && physical.matchesShadow == shadow, "Business Assembly resolved to the wrong physical image.");
            Type entry = assembly.GetType("AssemblyA.Implementation.Internal.InternalEntry", true);
            MethodInfo method = entry.GetMethod("GetMarker", BindingFlags.Public | BindingFlags.Instance);
            Require(method != null, "Real InternalEntry.GetMarker was stripped or absent.");
            result.reflectionAssembly = assembly.GetName().Name;
            result.reflectionType = entry.FullName;
            result.businessStarted = true;
            result.businessMarker = (string)method.Invoke(Activator.CreateInstance(entry), null);
            Require(result.businessMarker == (shadow ? "PATCH-P01-INTERNAL" : "BASELINE-INTERNAL"), "Business marker did not come from the expected implementation.");
        }

        private static void BindPatch(ProbeResult result, PatchInput patch)
        {
            result.patchId = patch.manifest.patchId;
            result.patchManifestPath = patch.path;
            result.patchManifestSha256 = patch.hash;
            result.compileSnapshotHash = patch.manifest.compileSnapshotHash;
        }

        private static string FallbackPath()
        {
            return Path.GetFullPath(ShadowPatchFileProvider.Argument("-shadowFallbackMarker", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m03-fallback.json")));
        }

        private static void WriteFallbackMarker(ProbeResult result, FixtureInput fixture, PatchInput patch)
        {
            Require(!result.businessStarted, "Failed activation already started business code.");
            string path = FallbackPath();
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var marker = new FallbackMarker { schemaVersion = 1, baselineBuildId = result.baselineBuildId, runtimeAbiHash = result.runtimeAbiHash,
                baselineManifestSha256 = fixture.manifest.baselineManifestSha256, patchId = patch.manifest.patchId, patchManifestSha256 = patch.hash,
                compileSnapshotHash = patch.manifest.compileSnapshotHash, failure = "ModuleInitializerFailed", state = "FailedAfterCommit",
                generation = 1, businessStarted = false, processId = result.processId };
            File.WriteAllText(path, JsonUtility.ToJson(marker, true));
            result.fallbackMarkerPath = path;
            result.fallbackMarkerSha256 = HashFile(path);
        }

        private static void RunFallback(ProbeResult result, FixtureInput fixture)
        {
            PatchInput failedPatch = fixture.Patch("P03-InitializerThrow");
            BindPatch(result, failedPatch);
            string path = FallbackPath();
            Require(File.Exists(path), "Next-process fallback marker is missing.");
            var marker = JsonUtility.FromJson<FallbackMarker>(File.ReadAllText(path));
            Require(marker != null && marker.schemaVersion == 1 && marker.baselineBuildId == result.baselineBuildId && marker.runtimeAbiHash == result.runtimeAbiHash &&
                marker.baselineManifestSha256 == result.baselineManifestSha256 && marker.patchId == failedPatch.manifest.patchId && marker.patchManifestSha256 == failedPatch.hash &&
                marker.compileSnapshotHash == failedPatch.manifest.compileSnapshotHash && marker.failure == "ModuleInitializerFailed" && marker.state == "FailedAfterCommit" &&
                marker.generation == 1 && !marker.businessStarted && marker.processId != result.processId, "Fallback marker is not bound to this baseline and failed patch in a previous process.");
            result.fallbackMarkerPath = path;
            result.fallbackMarkerSha256 = HashFile(path);
            RequireState(result, "fallback-initial", AssemblyShadowState.Disabled);
            RequireNoImages(Capture(result, "fallback-before-business"));
            AssemblyExecutionMode executionMode;
            result.executionModeCode = Expect(result, "fallback-unregistered-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(Internal, out executionMode), AssemblyShadowErrorCode.CandidateNotRegistered);
            result.executionMode = executionMode.ToString();
            Require(executionMode == AssemblyExecutionMode.AotBaseline, "Fresh process did not report baseline mode.");
            InvokeBusiness(result, false);
            RequireState(result, "fallback-after-business", AssemblyShadowState.Disabled);
            RequireNoImages(Capture(result, "fallback-after-business"));
            result.fallbackObserved = true;
        }

        private static FixtureInput ReadFixture(string expectedBaseline, string expectedAbi, ProbeResult result)
        {
            string path = ShadowPatchFileProvider.Argument("-shadowFixtureManifest", string.Empty);
            Require(!string.IsNullOrEmpty(path) && File.Exists(path), "Verified M03 fixture manifest is required.");
            path = Path.GetFullPath(path);
            var manifest = JsonUtility.FromJson<FixtureManifest>(File.ReadAllText(path));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M03", "Fixture schema mismatch.");
            Require(manifest.baselineBuildId == expectedBaseline && manifest.runtimeAbiHash == expectedAbi, "Fixture does not match the Player-embedded baseline/ABI.");
            Require(manifest.unityVersion == Application.unityVersion, "Fixture Unity version mismatch.");
            RequireSet(manifest.candidateNames, Candidates, "candidate set");
            Require(manifest.closureLoadOrder != null && manifest.closureLoadOrder.SequenceEqual(Candidates), "Fixture provider order changed.");
            Require(manifest.stableAotNames != null && manifest.stableAotNames.Length > 0 && manifest.stableAotNames.Distinct(StringComparer.OrdinalIgnoreCase).Count() == manifest.stableAotNames.Length &&
                !manifest.stableAotNames.Intersect(Candidates, StringComparer.OrdinalIgnoreCase).Any() && manifest.stableAotNames.SequenceEqual(manifest.stableAotNames.OrderBy(n => n, StringComparer.Ordinal)), "Stable AOT allowlist is invalid.");
            Require(manifest.stableAotProvenanceHash == HashText("m03-stable-aot:1\n" + manifest.stableAotProvenance) && manifest.stableAotProvenance.EndsWith("\nphysical=" + string.Join(",", manifest.stableAotNames), StringComparison.Ordinal), "Stable AOT provenance hash/names differ.");
            RequireHash(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            var baseline = JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 && baseline.baselineBuildId == expectedBaseline && baseline.runtimeAbiHash == expectedAbi && baseline.playerInputSnapshotHash == manifest.baselineInputSnapshotHash, "Baseline manifest identity mismatch.");
            RequireSet(baseline.shadowCandidates, Candidates, "baseline candidates");
            Require(baseline.unityVersion == manifest.unityVersion && baseline.target == manifest.target && baseline.architecture == manifest.architecture, "Baseline target mismatch.");
            VerifyPins(baseline.sourcePins, expectedAbi, baseline.unityVersion, baseline.target, baseline.architecture);
            Require(manifest.fixtures != null && manifest.fixtures.Length == 3, "Expected three M03 fixtures.");
            RequireSet(manifest.fixtures.Select(f => f.patchId).ToArray(), new[] { "P01", "P03", "P03-InitializerThrow" }, "fixture ids");
            var input = new FixtureInput { manifest = manifest, baseline = baseline, root = Path.GetDirectoryName(path) };
            // Validate every artifact before Configure; requested negative tests mutate only call inputs.
            foreach (Fixture item in manifest.fixtures) input.Patch(item.patchId);
            result.fixtureManifestPath = path;
            result.fixtureManifestSha256 = HashFile(path);
            result.baselineManifestSha256 = manifest.baselineManifestSha256;
            result.stableAotNames = manifest.stableAotNames;
            result.stableAotProvenanceHash = manifest.stableAotProvenanceHash;
            result.integrityOnlyUnsigned = true; // Integrity and source consistency, not M09 authenticity.
            return input;
        }

        private sealed class FixtureInput
        {
            public FixtureManifest manifest;
            public BaselineManifest baseline;
            public string root;
            private readonly Dictionary<string, PatchInput> patches = new Dictionary<string, PatchInput>();
            public PatchInput Patch(string id)
            {
                PatchInput cached;
                if (patches.TryGetValue(id, out cached)) return cached;
                Fixture fixture = manifest.fixtures.Single(f => f.patchId == id);
                string path = ConfinedAbsolute(root, fixture.patchManifest);
                string directory = ConfinedAbsolute(root, fixture.patchDirectory);
                Require(Path.GetDirectoryName(path) == directory, "Patch manifest is outside its declared artifact directory.");
                RequireHash(path, fixture.patchManifestSha256);
                var patch = JsonUtility.FromJson<PatchManifest>(File.ReadAllText(path));
                Require(patch != null && patch.schemaVersion == 1 && patch.semanticHashSchema == 1 && patch.patchId == id && patch.baselineBuildId == manifest.baselineBuildId && patch.baselineManifestSha256 == manifest.baselineManifestSha256 && patch.runtimeAbiHash == manifest.runtimeAbiHash, "Patch/baseline identity mismatch: " + id);
                Require(patch.unityVersion == manifest.unityVersion && patch.target == manifest.target && patch.architecture == manifest.architecture && patch.compileSnapshotHash == fixture.compileSnapshotHash && IsHash(patch.compileSnapshotHash), "Patch compiler/target identity mismatch: " + id);
                VerifyPins(patch.sourcePins, manifest.runtimeAbiHash, manifest.unityVersion, manifest.target, manifest.architecture);
                Require(SameRepositories(baseline.sourcePins, patch.sourcePins), "Patch runtime source repository mismatch.");
                Require(patch.bootstrapAbiHash == baseline.bootstrapAbiHash && patch.baselineResourceAbiHash == baseline.resourceAbiHash && patch.resourceAbiHash == baseline.resourceAbiHash && patch.dllOnly, "Patch fixed Bootstrap/resource ABI changed.");
                Require(patch.unsigned && patch.signatureAlgorithm == "None", "M03 does not implement signed artifact verification.");
                string[] expected = id == "P01" ? new[] { Internal } : Candidates;
                Require(patch.closure != null, "Patch closure is missing.");
                RequireSet(patch.closure.Select(a => a.name).ToArray(), expected, id + " closure");
                RequireSet(patch.loadOrder, expected, id + " load order");
                Require(patch.loadOrder.SequenceEqual(expected) && fixture.closureLoadOrder.SequenceEqual(patch.loadOrder), "Patch provider order differs from verified fixture.");
                Require(fixture.stableAotNames.SequenceEqual(manifest.stableAotNames), "Patch stable AOT provenance differs.");
                cached = new PatchInput { manifest = patch, path = path, hash = fixture.patchManifestSha256, root = directory };
                foreach (PatchAssembly assembly in patch.closure) { byte[] dll, pdb; cached.ReadAssembly(assembly.name, out dll, out pdb); }
                patches.Add(id, cached);
                return cached;
            }
        }

        private sealed class PatchInput
        {
            public PatchManifest manifest;
            public string path, hash, root;
            public void ReadAssembly(string name, out byte[] dll, out byte[] pdb)
            {
                PatchAssembly assembly = manifest.closure.Single(a => string.Equals(a.name, name, StringComparison.OrdinalIgnoreCase));
                string dllPath = ConfinedRelative(root, assembly.dll);
                dll = File.ReadAllBytes(dllPath);
                Require(IsHash(assembly.sha256) && ShadowPatchFileProvider.Hash(dll) == assembly.sha256, "Patch DLL hash mismatch: " + name);
                Guid mvid, baselineMvid;
                Require(Guid.TryParse(assembly.mvid, out mvid) && Guid.TryParse(assembly.baselineMvid, out baselineMvid), "Patch MVID evidence missing: " + name);
                pdb = null;
                if (!string.IsNullOrEmpty(assembly.pdb))
                {
                    pdb = File.ReadAllBytes(ConfinedRelative(root, assembly.pdb));
                    Require(IsHash(assembly.pdbSha256) && ShadowPatchFileProvider.Hash(pdb) == assembly.pdbSha256, "Patch PDB hash mismatch: " + name);
                }
                else Require(string.IsNullOrEmpty(assembly.pdbSha256), "PDB hash has no corresponding file.");
            }
        }

        private static void VerifyPins(SourcePins pins, string abi, string unity, string target, string architecture)
        {
            Require(pins != null && pins.schemaVersion == 1 && pins.unityVersion == unity && pins.target == target && pins.architecture == architecture, "Source-pin target mismatch.");
            foreach (RepositoryPin pin in new[] { pins.hybridclr, pins.hybridclrUnity, pins.il2cppPlus, pins.demo })
                Require(pin != null && !string.IsNullOrEmpty(pin.url) && IsHex(pin.revision, 40), "Missing exact source pin.");
            Require(HashText("assembly-shadow-runtime-abi:1\n" + unity + "\n" + target + "\n" + architecture + "\n" + pins.hybridclr.revision + "\n" + pins.il2cppPlus.revision + "\n" + pins.hybridclrUnity.revision) == abi, "Source pins do not reproduce the Player runtime ABI hash.");
        }

        private static bool SameRepositories(SourcePins a, SourcePins b)
        {
            return a.hybridclr.url == b.hybridclr.url && a.hybridclrUnity.url == b.hybridclrUnity.url && a.il2cppPlus.url == b.il2cppPlus.url;
        }
        private static string ConfinedAbsolute(string root, string path)
        {
            Require(!string.IsNullOrEmpty(path), "Missing artifact path.");
            string full = Path.GetFullPath(path);
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            Require(full.StartsWith(prefix, StringComparison.Ordinal), "Artifact escapes fixture root: " + full);
            for (string current = full; current != Path.GetFullPath(root); current = Path.GetDirectoryName(current))
                Require((File.GetAttributes(current) & FileAttributes.ReparsePoint) == 0, "Artifact path traverses a symbolic link: " + current);
            return full;
        }
        private static string ConfinedRelative(string root, string relative) { return ConfinedAbsolute(root, ShadowPatchFileProvider.SafePath(root, relative)); }
        private static string HashFile(string path) { return ShadowPatchFileProvider.Hash(File.ReadAllBytes(path)); }
        private static string HashText(string value) { return ShadowPatchFileProvider.Hash(Encoding.UTF8.GetBytes(value)); }
        private static void RequireHash(string path, string hash) { Require(IsHash(hash) && File.Exists(path) && HashFile(path) == hash, "Artifact hash mismatch: " + path); }
        private static bool IsHash(string value) { return IsHex(value, 64); }
        private static bool IsHex(string value, int count) { return value != null && value.Length == count && value.All(c => c >= '0' && c <= '9' || c >= 'a' && c <= 'f'); }
        private static void RequireSet(string[] actual, string[] expected, string description)
        {
            Require(actual != null && actual.Length == expected.Length && actual.Distinct(StringComparer.Ordinal).Count() == actual.Length && new HashSet<string>(actual, StringComparer.Ordinal).SetEquals(expected), "Exact set mismatch: " + description);
        }
        private static void Require(bool condition, string message) { if (!condition) throw new InvalidOperationException(message); }

        private sealed class InitObserver : TextWriter
        {
            private readonly ProbeResult result;
            private readonly StringBuilder pending = new StringBuilder();
            public InitObserver(ProbeResult result) { this.result = result; }
            public override Encoding Encoding { get { return Encoding.UTF8; } }
            public override void Write(char value) { if (value == '\n') FlushLine(); else pending.Append(value); }
            public override void Write(string value) { if (value != null) foreach (char c in value) Write(c); }
            private void FlushLine()
            {
                string line = pending.ToString().TrimEnd('\r'); pending.Length = 0;
                if (!line.StartsWith("M03-INIT:", StringComparison.Ordinal)) return;
                AssemblyShadowState state; string json;
                AssemblyShadowErrorCode stateCode = AssemblyShadowRuntime.GetState(out state);
                AssemblyShadowErrorCode diagnosticCode = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
                AssemblyShadowDiagnostics diagnostics = ParseDiagnostics(json);
                result.initializerEvents.Add(new InitializerEvent { name = line.Substring("M03-INIT:".Length), state = state.ToString(), stateCode = stateCode.ToString(), diagnosticsCode = diagnosticCode.ToString(), generation = diagnostics.generation });
                result.reentrantQueries++;
            }
        }

        private sealed class ThreadStress
        {
            private readonly string[] closure;
            private readonly object sync = new object();
            private readonly List<string> errors = new List<string>();
            private readonly List<StressSample> samples = new List<StressSample>();
            private Thread thread;
            private volatile bool stop;
            private int iterations, before, after;
            public ThreadStress(string[] stable, string[] closure)
            {
                Require(stable != null && stable.Contains("mscorlib", StringComparer.OrdinalIgnoreCase), "Concurrent load target mscorlib lacks verified stable AOT provenance.");
                this.closure = closure;
            }
            public void Start() { thread = new Thread(Run) { IsBackground = true, Name = "M03-ordinary-reader" }; thread.Start(); }
            public void WaitForGeneration(bool published)
            {
                var clock = System.Diagnostics.Stopwatch.StartNew();
                while ((published ? Volatile.Read(ref after) : Volatile.Read(ref before)) == 0 && clock.ElapsedMilliseconds < 10000)
                {
                    lock (sync) Require(errors.Count == 0, "Concurrent reader failed: " + string.Join("; ", errors));
                    Thread.Yield();
                }
                Require((published ? Volatile.Read(ref after) : Volatile.Read(ref before)) > 0, "Concurrent reader never observed requested generation.");
            }
            public bool StopAndJoin() { stop = true; return thread == null || thread.Join(10000); }
            public void CopyTo(ProbeResult result)
            {
                lock (sync)
                {
                    result.stressIterations = iterations; result.stressBefore = before; result.stressAfter = after;
                    result.stressErrors = errors.ToArray(); result.stressSamples = samples.ToArray();
                }
            }
            private void Run()
            {
                long lastGeneration = 0, lastEnumeration = 0;
                while (!stop)
                {
                    try
                    {
                        Assembly loaded = Assembly.Load("mscorlib");
                        Require(loaded != null && string.Equals(loaded.GetName().Name, "mscorlib", StringComparison.OrdinalIgnoreCase), "Ordinary stable assembly load changed identity.");
                        string json;
                        Require(AssemblyShadowRuntime.GetDiagnosticsJson(out json) == AssemblyShadowErrorCode.Success, "Concurrent diagnostic query failed.");
                        AssemblyShadowDiagnostics diagnostics = ParseDiagnostics(json);
                        CheckOrdinary(diagnostics, closure);
                        Require(diagnostics.generation >= lastGeneration && diagnostics.enumerationGeneration >= lastEnumeration, "Generation regressed across coherent samples.");
                        lastGeneration = diagnostics.generation; lastEnumeration = diagnostics.enumerationGeneration;
                        lock (sync)
                        {
                            iterations++;
                            if (diagnostics.enumerationGeneration == 0) before++; else after++;
                            // Keep bounded representative evidence on both sides, not an unbounded log.
                            if (diagnostics.enumerationGeneration == 0 && before <= 16 || diagnostics.enumerationGeneration == 1 && after <= 16)
                                samples.Add(new StressSample { generation = diagnostics.generation, enumerationGeneration = diagnostics.enumerationGeneration, shadowCount = diagnostics.ordinaryAssemblies.Count(a => a.isInterpreter && closure.Contains(a.name, StringComparer.OrdinalIgnoreCase)) });
                        }
                        Thread.Yield();
                    }
                    catch (Exception error) { lock (sync) errors.Add(error.ToString()); return; }
                }
            }
        }

        // Runtime mirrors of the editor-only M02 DTOs: field names intentionally match ShadowManifests.cs.
        [Serializable] private sealed class RepositoryPin { public string url, revision; }
        [Serializable] private sealed class SourcePins { public int schemaVersion; public string unityVersion, target, architecture; public RepositoryPin hybridclr, hybridclrUnity, il2cppPlus, demo; }
        [Serializable] private sealed class BaselineManifest { public int schemaVersion, semanticHashSchema; public string baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, playerInputSnapshotHash, bootstrapAbiHash, resourceAbiHash; public string[] shadowCandidates; public SourcePins sourcePins; }
        [Serializable] private sealed class PatchManifest { public int schemaVersion, semanticHashSchema; public string patchId, baselineBuildId, baselineManifestSha256, runtimeAbiHash, unityVersion, target, architecture, compileSnapshotHash, bootstrapAbiHash, baselineResourceAbiHash, resourceAbiHash, signatureAlgorithm; public bool dllOnly, unsigned; public string[] loadOrder; public PatchAssembly[] closure; public SourcePins sourcePins; }
        [Serializable] private sealed class PatchAssembly { public string name, dll, sha256, pdb, pdbSha256, mvid, baselineMvid; }
        [Serializable] private sealed class FixtureManifest { public int schemaVersion; public string milestone, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, baselineManifestPath, baselineManifestSha256, baselineInputSnapshotHash, stableAotProvenance, stableAotProvenanceHash; public string[] candidateNames, closureLoadOrder, stableAotNames; public Fixture[] fixtures; }
        [Serializable] private sealed class Fixture { public string patchId, patchDirectory, patchManifest, patchManifestSha256, compileSnapshotHash; public string[] closureLoadOrder, stableAotNames; }
        [Serializable] private sealed class FallbackMarker { public int schemaVersion, processId; public string baselineBuildId, runtimeAbiHash, baselineManifestSha256, patchId, patchManifestSha256, compileSnapshotHash, failure, state; public long generation; public bool businessStarted; }
        [Serializable] private sealed class Check { public string operation, actual, expected; public int actualCode, expectedCode; }
        [Serializable] private sealed class StageResult { public string name, code, dllSha256, pdbSha256; }
        [Serializable] private sealed class InitializerEvent { public string name, state, stateCode, diagnosticsCode; public long generation; }
        [Serializable] private sealed class PhysicalAssembly { public string name; public bool isInterpreter, matchesShadow; }
        [Serializable] private sealed class Snapshot { public string point; public AssemblyShadowDiagnostics diagnostics; }
        [Serializable] private sealed class StressSample { public long generation, enumerationGeneration; public int shadowCount; }
        [Serializable] private sealed class ProbeResult
        {
            public int schemaVersion, processId; public string milestone, mode, result, error; public bool il2cpp;
            public string unityVersion, platform, baselineBuildId, runtimeAbiHash, baselineManifestSha256, fixtureManifestPath, fixtureManifestSha256;
            public string playerBuildGuid, playerDataPath;
            public string patchId, patchManifestPath, patchManifestSha256, compileSnapshotHash, stableAotProvenanceHash;
            public bool integrityOnlyUnsigned; public string[] stableAotNames, expectedClosure, stageOrder; public int stageSeed;
            public string configure, begin, stage, validate, commit, abort, duplicateStage, badPdbStage, stateCode, state, stateAtValidate, stateAfterCommit;
            public string executionModeCode, executionMode, diagnosticsCode, nativeDiagnosticsJson, nativeDiagnosticsPath, nativeDiagnosticsSha256;
            public List<Check> checks = new List<Check>(); public List<string> states = new List<string>(); public List<Snapshot> snapshots = new List<Snapshot>();
            public List<StageResult> stageResults = new List<StageResult>(); public List<InitializerEvent> initializerEvents = new List<InitializerEvent>();
            public int reentrantQueries, initializersAfterStage, initializersAfterValidate;
            public PhysicalAssembly[] managedEnumeration; public string baselineUseAssemblyLoad, reflectionAssembly, reflectionType, businessMarker;
            public bool businessStarted, fallbackObserved; public string fallbackMarkerPath, fallbackMarkerSha256;
            public bool stressStarted, stressJoined; public int stressIterations, stressBefore, stressAfter;
            public string[] stressErrors = new string[0]; public StressSample[] stressSamples = new StressSample[0];
        }
    }
}
