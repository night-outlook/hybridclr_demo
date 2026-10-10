using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadow.R03.IR
{
    // Independent supplementary Player. The original R03Player remains inert
    // because this executable receives -r03IrRequest, never -r03Request.
    [Preserve]
    public static class R03TerminalPlayer
    {
        [Serializable, Preserve] private sealed class Request
        {
            public int schemaVersion;
            public string runId, caseId, baselineId, dllPath, dllSha256, stimulus;
        }
        [Serializable, Preserve] private sealed class NativeGuard
        {
            public int schemaVersion, activeGuard, baselineGuard, caughtOldGuard, stateCode;
            public bool available;
        }
        [Serializable, Preserve] public sealed class Report
        {
            public int schemaVersion = 1;
            public string kind = "R03IRPostPoisonEntryV1";
            public string result = "Failed", runId, caseId, requestSha256, stimulus;
            public int processId, initialState, poisonedState, finalState;
            public string unityVersion, platform, error, nativeGuardJson;
            public int nativeStimulusReturn, preActiveReflection, preActiveDelegate;
            public int preCanaryCount, finalCanaryCount;
            public int preShadowField, finalShadowField;
            public bool shadowFieldReadable;
            public bool prePositive, activeReflectionAttempted, activeReflectionSucceeded;
            public bool activeDelegateAttempted, activeDelegateSucceeded;
            public bool aotReflectionAttempted, aotReflectionSucceeded;
            public string activeReflectionException, activeDelegateException, aotReflectionException;
            public string firstRecovery, finalRecovery, finalDiagnostics, finalExecutionDiagnostics;
            public bool recoveryStable, fixedDiagnosticsReadable;
            public int nativePhase, failurePhase, terminalReportingProbeMask;
            public bool acceptance = false;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_ObserveMethod(string assembly, string namespaze, string type, string method,
            int oldGuard, [Out] byte[] output, int capacity);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ForceTypeFailure();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_TracePhase(int phase);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ProbeTerminalReporting();
        private static void Phase(Report report, int phase)
        {
            report.nativePhase = phase;
            R03_IR_TracePhase(phase); // Native stderr checkpoint, not Unity logging.
        }

        private static int s_canary;
        private static string s_failedRequirement;
        [Preserve]
        private static void TerminalAotCanary() { ++s_canary; }
        private static bool s_started;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Start()
        {
            if (s_started) return;
            s_started = true;
            string requestPath = Argument("-r03IrRequest");
            if (requestPath == null) return;
            string outputPath = Argument("-r03IrOutput");
            Report report = new Report
            {
                processId = Process.GetCurrentProcess().Id,
                unityVersion = Application.unityVersion,
                platform = Application.platform.ToString()
            };
            try
            {
                Phase(report, 10);
                Require(outputPath != null && !File.Exists(outputPath), "Unused output path required");
                byte[] requestBytes = File.ReadAllBytes(requestPath);
                report.requestSha256 = Hash(requestBytes);
                Request request = JsonUtility.FromJson<Request>(Encoding.UTF8.GetString(requestBytes));
                Require(request != null && request.schemaVersion == 1 && !string.IsNullOrEmpty(request.runId) &&
                    request.runId == Argument("-r03IrRunId") && !string.IsNullOrEmpty(request.caseId) &&
                    !string.IsNullOrEmpty(request.stimulus), "Exact request/run identity");
                report.runId = request.runId;
                report.caseId = request.caseId;
                report.stimulus = request.stimulus;
                Require(Application.platform == RuntimePlatform.OSXPlayer, "Actual macOS Player required");
                AssemblyShadowState state;
                var canary = typeof(R03TerminalPlayer).GetMethod("TerminalAotCanary", BindingFlags.NonPublic | BindingFlags.Static);
                Require(canary != null, "Preserved AOT canary required");

                if (request.stimulus == "off")
                {
                    Require(AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.FeatureDisabled &&
                        state == AssemblyShadowState.Disabled, "Feature OFF state");
                    report.initialState = (int)state;
                    canary.Invoke(null, null);
                    report.preCanaryCount = s_canary;
                    canary.Invoke(null, null);
                    report.finalCanaryCount = s_canary;
                    report.finalState = (int)state;
                    report.prePositive = report.preCanaryCount == 1;
                    Require(report.prePositive && report.finalCanaryCount == 2, "Ordinary OFF execution must not be poisoned");
                    report.result = "Passed";
                    return;
                }

                Require(request.stimulus == "baseline-owner" || request.stimulus == "type-resolution",
                    "Supported independent ON stimuli only");
                Require(!string.IsNullOrEmpty(request.dllPath) && Path.IsPathRooted(request.dllPath) &&
                    !string.IsNullOrEmpty(request.dllSha256) && !string.IsNullOrEmpty(request.baselineId),
                    "Complete immutable target DLL binding");
                byte[] dll = File.ReadAllBytes(request.dllPath);
                Require(Hash(dll) == request.dllSha256, "Target DLL hash changed");
                var names = new[] { "A", "B", "Layout", "Methods", "R03Contract" };
                Phase(report, 20);
                Require(AssemblyShadowRuntime.ConfigureCandidates(request.baselineId, names, new[] { "mscorlib" }) ==
                    AssemblyShadowErrorCode.Success, "Configure");
                Phase(report, 30);
                Require(AssemblyShadowRuntime.BeginTransaction("R03IR-" + request.runId, request.baselineId,
                    new[] { "Methods" }, 2) == AssemblyShadowErrorCode.Success, "Begin");
                Phase(report, 40);
                Require(AssemblyShadowRuntime.ReserveMetadataBudget(new[] { dll.LongLength }, 2) ==
                    AssemblyShadowErrorCode.Success, "Reserve");
                Phase(report, 50);
                Require(AssemblyShadowRuntime.StageAssembly(dll, null) == AssemblyShadowErrorCode.Success, "Stage");
                Phase(report, 60);
                Require(AssemblyShadowRuntime.ValidateTransaction() == AssemblyShadowErrorCode.Success, "Validate");
                Phase(report, 70);
                Require(AssemblyShadowRuntime.CommitTransaction() == AssemblyShadowErrorCode.Success, "Commit");
                Require(AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success &&
                    state == AssemblyShadowState.Committed, "Committed before poison");
                report.initialState = (int)state;

                // True positive control: the same already-resolved active method,
                // its delegate, and the AOT reflection canary all execute first.
                Phase(report, 80);
                Type activeType = Type.GetType("R03.Node, Methods", true);
                Phase(report, 90);
                object instance = Activator.CreateInstance(activeType);
                Phase(report, 100);
                MethodInfo activeMethod = activeType.GetMethod("Keep", BindingFlags.Instance | BindingFlags.Public);
                Require(activeMethod != null, "Active Keep method");
                Phase(report, 110);
                FieldInfo stableField = activeType.GetField("stable", BindingFlags.Instance | BindingFlags.NonPublic);
                Require(stableField != null && stableField.FieldType == typeof(int),
                    "IR active private primitive field required");
                Phase(report, 120);
                Require((int)stableField.GetValue(instance) == 0, "Fresh IR counter must start at zero");
                Phase(report, 130);
                Func<int> activeDelegate = (Func<int>)Delegate.CreateDelegate(typeof(Func<int>), instance, activeMethod);
                Phase(report, 140);
                report.preActiveReflection = (int)activeMethod.Invoke(instance, null);
                Phase(report, 150);
                report.preActiveDelegate = activeDelegate();
                canary.Invoke(null, null);
                report.preCanaryCount = s_canary;
                Phase(report, 160);
                report.preShadowField = (int)stableField.GetValue(instance);
                report.prePositive = report.preActiveReflection == 42 &&
                    report.preActiveDelegate == 42 && report.preCanaryCount == 1 &&
                    report.preShadowField == 2;
                Require(report.prePositive, "Pre-poison positive controls must really execute");

                Phase(report, 170);
                if (request.stimulus == "baseline-owner")
                {
                    byte[] buffer = new byte[16384];
                    int count = R03_ObserveMethod("Methods", "R03", "Node", "Keep", 3, buffer, buffer.Length);
                    Require(count > 0 && count < buffer.Length, "Native baseline-owner guard receipt");
                    report.nativeGuardJson = Encoding.UTF8.GetString(buffer, 0, count);
                    NativeGuard guard = JsonUtility.FromJson<NativeGuard>(report.nativeGuardJson);
                    Require(guard != null && guard.available && guard.activeGuard == 1 &&
                        guard.baselineGuard == 0 && guard.caughtOldGuard == 1 && guard.stateCode == 9,
                        "First terminal failure and caught managed guard exception required");
                    report.nativeStimulusReturn = guard.caughtOldGuard;
                }
                else
                {
                    // Calls the actual production type-failure function with
                    // test-only input; no fabricated state write.
                    report.nativeStimulusReturn = R03_IR_ForceTypeFailure();
                    Require(report.nativeStimulusReturn == 1, "Caught native-to-managed type failure");
                }
                Require(AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success &&
                    state == AssemblyShadowState.FailedAfterCommit, "Terminal state retained after caught exception");
                Phase(report, 180);
                report.poisonedState = (int)state;
                string recovery;
                Require(AssemblyShadowRuntime.GetRecoveryInfoJson(out recovery) == AssemblyShadowErrorCode.Success,
                    "Original terminal recovery diagnostics");
                report.firstRecovery = recovery;
                Phase(report, 185);
                report.terminalReportingProbeMask = R03_IR_ProbeTerminalReporting();
                Require(report.terminalReportingProbeMask == 15,
                    "Native handled-true report only; logging-enabled and callback guards still deny execution");

                Phase(report, 190);
                report.activeReflectionAttempted = true;
                try { activeMethod.Invoke(instance, null); report.activeReflectionSucceeded = true; }
                catch (Exception failure) { report.activeReflectionException = failure.GetType().FullName; }
                Phase(report, 200);
                report.activeDelegateAttempted = true;
                try { activeDelegate(); report.activeDelegateSucceeded = true; }
                catch (Exception failure) { report.activeDelegateException = failure.GetType().FullName; }
                Phase(report, 210);
                report.aotReflectionAttempted = true;
                try { canary.Invoke(null, null); report.aotReflectionSucceeded = true; }
                catch (Exception failure) { report.aotReflectionException = failure.GetType().FullName; }
                report.finalCanaryCount = s_canary;
                // Read the already resolved primitive FieldInfo after poison.
                // A failed read cannot pass: we do not infer no body execution
                // merely from a caught exception or unchanged AOT canary.
                Phase(report, 220);
                report.finalShadowField = (int)stableField.GetValue(instance);
                report.shadowFieldReadable = true;

                string diagnostics, execution;
                Require(AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success,
                    "Final state diagnostic");
                report.finalState = (int)state;
                int recoveryCode = (int)AssemblyShadowRuntime.GetRecoveryInfoJson(out recovery);
                int diagnosticsCode = (int)AssemblyShadowRuntime.GetDiagnosticsJson(out diagnostics);
                int executionCode = (int)AssemblyShadowRuntime.GetExecutionDiagnosticsJson(out execution);
                report.finalRecovery = recovery;
                report.finalDiagnostics = diagnostics;
                report.finalExecutionDiagnostics = execution;
                report.recoveryStable = report.firstRecovery == report.finalRecovery;
                report.fixedDiagnosticsReadable = recoveryCode == 0 && diagnosticsCode == 0 && executionCode == 0 &&
                    !string.IsNullOrEmpty(recovery) && !string.IsNullOrEmpty(diagnostics) &&
                    !string.IsNullOrEmpty(execution);
                Require(report.finalState == 9 && report.recoveryStable && report.fixedDiagnosticsReadable,
                    "Original failure, state and fixed diagnostics must survive all attempts");
                Require(report.activeReflectionAttempted && !report.activeReflectionSucceeded &&
                    !string.IsNullOrEmpty(report.activeReflectionException), "Active reflection must reject");
                Require(report.activeDelegateAttempted && !report.activeDelegateSucceeded &&
                    !string.IsNullOrEmpty(report.activeDelegateException), "Active delegate must reject");
                Require(report.aotReflectionAttempted && !report.aotReflectionSucceeded &&
                    !string.IsNullOrEmpty(report.aotReflectionException) &&
                    report.finalCanaryCount == report.preCanaryCount, "AOT reflective body side effect forbidden");
                Require(report.shadowFieldReadable && report.preShadowField == 2 &&
                    report.finalShadowField == report.preShadowField,
                    "Actual active shadow Keep method body must not mutate its instance field after poison");
                report.result = "Passed";
            }
            catch (Exception error)
            {
                // Exception.ToString may make virtual calls in poisoned state.
                // Original native cause/last phase is retained in flushed stderr.
                report.failurePhase = report.nativePhase;
                report.error = "ManagedFailure; see native first-failure and phase checkpoints";
                Phase(report, 900);
                try { report.error = s_failedRequirement ?? error.GetType().FullName; }
                catch { /* Keep literal rather than losing the original report. */ }
            }
            finally
            {
                try
                {
                    Phase(report, 910);
                    using (var output = new FileStream(outputPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                    using (var writer = new StreamWriter(output, new UTF8Encoding(false)))
                        writer.Write(JsonUtility.ToJson(report, true) + "\n");
                    Application.Quit(0); // Host verifier owns acceptance, not this process exit.
                }
                catch (Exception)
                {
                    // Never route a reporting failure through a managed logger.
                    R03_IR_TracePhase(990);
                    Application.Quit(2);
                }
            }
        }

        private static void Require(bool ok, string message)
        {
            if (!ok)
            {
                // Preserve our own assertion text without virtual exception formatting.
                s_failedRequirement = message;
                throw new InvalidOperationException("R03IR: " + message);
            }
        }
        private static string Argument(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == key) return args[i + 1];
            return null;
        }
        private static string Hash(byte[] bytes)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }
    }
}
