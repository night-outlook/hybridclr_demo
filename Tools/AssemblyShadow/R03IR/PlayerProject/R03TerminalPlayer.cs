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
            public int nativePhase, failurePhase, terminalReportingProbeMask, reserveGcProbeMask;
            public bool acceptance = false;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ReportOpen([MarshalAs(UnmanagedType.LPUTF8Str)] string path);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ReportInt(int field, int value);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ReportText(int field, [MarshalAs(UnmanagedType.LPUTF8Str)] string value);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ReportSeal();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_Exit(int status);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ProbeBooleanReserve();
        // N test-only native observers: bound while healthy, no post-terminal
        // managed UTF-8 decode or reflective FieldInfo.GetValue dispatch.
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_BindActiveField(IntPtr managedHandle);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ReadActiveField(out int value);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ObserveOldGuardIntoSnapshot();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_EngineLoggerCalled();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ArmEngineWitness(string output, string run, string caseId, string requestSha);

        [Preserve]
        private sealed class EngineWitnessLogger : ILogHandler
        {
            public void LogException(Exception exception, UnityEngine.Object context) { R03_IR_EngineLoggerCalled(); }
            public void LogFormat(LogType type, UnityEngine.Object context, string format, params object[] args)
            { R03_IR_EngineLoggerCalled(); }
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
            bool reportOpened = false, engineCase = false, engineArmed = false;
            Exception engineSentinel = null;
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
                engineCase = request.stimulus == "engine-unhandled";
                if (!engineCase)
                {
                    Require(R03_IR_ReportOpen(outputPath) == 1, "Exclusive native report destination");
                    reportOpened = true;
                }
                else
                {
                    // Allocate while healthy; the actual uncaught exception must
                    // leave Start and be routed by Unity, never by a direct probe.
                    engineSentinel = new InvalidOperationException("R03_ENGINE_UNHANDLED_" + request.runId);
                    UnityEngine.Debug.unityLogger.logHandler = new EngineWitnessLogger();
                    UnityEngine.Debug.LogException(engineSentinel); // One healthy logger control, no forwarding.
                }
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

                Require(request.stimulus == "baseline-owner" || request.stimulus == "type-resolution" || engineCase,
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
                report.reserveGcProbeMask = R03_IR_ProbeBooleanReserve();
                Require(report.reserveGcProbeMask == 31, "Physical pinned Boolean must survive real healthy GC");
                if (engineCase)
                {
                    Require(R03_IR_ArmEngineWitness(outputPath, request.runId, request.caseId,
                        report.requestSha256) == 1, "Exclusive engine witness arm");
                    engineArmed = true;
                    // Prescribed production failure, followed by an uncaught,
                    // preallocated sentinel. No direct report probe is invoked.
                    R03_IR_ForceTypeFailure();
                    throw engineSentinel;
                }

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
                // Bind the actual active instance only before poison. The
                // native test observer retains its own pinned strong root.
                GCHandle fieldHandle = GCHandle.Alloc(instance, GCHandleType.Normal);
                try
                {
                    Require(R03_IR_BindActiveField(GCHandle.ToIntPtr(fieldHandle)) == 1,
                        "Healthy native active-instance field observer must bind");
                }
                finally { fieldHandle.Free(); }

                Phase(report, 170);
                if (request.stimulus == "baseline-owner")
                {
                    // Full ACTUAL native guard JSON is checked and written to
                    // preopened snapshot slot 8 entirely in native code.
                    // Managed UTF-8 conversion would be forbidden after poison.
                    report.nativeStimulusReturn = R03_IR_ObserveOldGuardIntoSnapshot();
                    Require(report.nativeStimulusReturn == 1,
                        "Actual caught baseline guard and native snapshot receipt required");
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
                catch (Exception) { report.activeReflectionException = "ManagedExceptionCaught"; }
                Phase(report, 200);
                report.activeDelegateAttempted = true;
                try { activeDelegate(); report.activeDelegateSucceeded = true; }
                catch (Exception) { report.activeDelegateException = "ManagedExceptionCaught"; }
                Phase(report, 210);
                report.aotReflectionAttempted = true;
                try { canary.Invoke(null, null); report.aotReflectionSucceeded = true; }
                catch (Exception) { report.aotReflectionException = "ManagedExceptionCaught"; }
                report.finalCanaryCount = s_canary;
                // Read the already resolved primitive FieldInfo after poison.
                // A failed read cannot pass: we do not infer no body execution
                // merely from a caught exception or unchanged AOT canary.
                Phase(report, 220);
                // The original FieldInfo.GetValue virtual call remains
                // forbidden. Read only the exact instance/field pinned and
                // validated before poison; retain the original value==2 proof.
                int afterField;
                report.shadowFieldReadable = R03_IR_ReadActiveField(out afterField) == 1;
                report.finalShadowField = afterField;
                Require(report.shadowFieldReadable, "Bound native primitive field must remain readable");

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
            catch (Exception)
            {
                if (engineArmed) throw; // Unity, not this code, routes the unhandled sentinel.
                // Exception.ToString may make virtual calls in poisoned state.
                // Original native cause/last phase is retained in flushed stderr.
                report.failurePhase = report.nativePhase;
                report.error = "ManagedFailure; see native first-failure and phase checkpoints";
                Phase(report, 900);
                report.error = s_failedRequirement ?? "ManagedExceptionCaught";
            }
            finally
            {
                if (!engineArmed)
                {
                    // A complete native snapshot avoids reflection/virtual I/O
                    // after poison. Native exit terminates this disposable test
                    // only; it does NOT validate ordinary runtime shutdown.
                    int exit = 2;
                    try
                    {
                        Phase(report, 910);
                        if (!reportOpened && outputPath != null) reportOpened = R03_IR_ReportOpen(outputPath) == 1;
                        if (reportOpened && EmitNativeReport(report)) exit = 0;
                    }
                    catch { R03_IR_TracePhase(990); }
                    R03_IR_Exit(exit);
                }
            }
        }

        private static bool EmitNativeReport(Report r)
        {
            bool ok = true;
            ok &= R03_IR_ReportInt(0, r.initialState) == 1;
            ok &= R03_IR_ReportInt(1, r.poisonedState) == 1;
            ok &= R03_IR_ReportInt(2, r.finalState) == 1;
            ok &= R03_IR_ReportInt(3, r.nativeStimulusReturn) == 1;
            ok &= R03_IR_ReportInt(4, r.preActiveReflection) == 1;
            ok &= R03_IR_ReportInt(5, r.preActiveDelegate) == 1;
            ok &= R03_IR_ReportInt(6, r.preCanaryCount) == 1;
            ok &= R03_IR_ReportInt(7, r.finalCanaryCount) == 1;
            ok &= R03_IR_ReportInt(8, r.preShadowField) == 1;
            ok &= R03_IR_ReportInt(9, r.finalShadowField) == 1;
            ok &= R03_IR_ReportInt(10, r.nativePhase) == 1;
            ok &= R03_IR_ReportInt(11, r.failurePhase) == 1;
            ok &= R03_IR_ReportInt(12, r.terminalReportingProbeMask) == 1;
            ok &= R03_IR_ReportInt(13, r.reserveGcProbeMask) == 1;
            ok &= R03_IR_ReportInt(14, r.shadowFieldReadable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(15, r.prePositive ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(16, r.activeReflectionAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(17, r.activeReflectionSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(18, r.activeDelegateAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(19, r.activeDelegateSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(20, r.aotReflectionAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(21, r.aotReflectionSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(22, r.recoveryStable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(23, r.fixedDiagnosticsReadable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(24, r.acceptance ? 1 : 0) == 1;
            ok &= R03_IR_ReportText(0, r.result) == 1;
            ok &= R03_IR_ReportText(1, r.runId) == 1;
            ok &= R03_IR_ReportText(2, r.caseId) == 1;
            ok &= R03_IR_ReportText(3, r.requestSha256) == 1;
            ok &= R03_IR_ReportText(4, r.stimulus) == 1;
            ok &= R03_IR_ReportText(5, r.unityVersion) == 1;
            ok &= R03_IR_ReportText(6, r.platform) == 1;
            ok &= R03_IR_ReportText(7, r.error) == 1;
            // Baseline slot 8 was already filled exactly once by the native
            // guard observer. A second write must never mask/corrupt it.
            if (r.stimulus != "baseline-owner")
                ok &= R03_IR_ReportText(8, r.nativeGuardJson) == 1;
            ok &= R03_IR_ReportText(9, r.activeReflectionException) == 1;
            ok &= R03_IR_ReportText(10, r.activeDelegateException) == 1;
            ok &= R03_IR_ReportText(11, r.aotReflectionException) == 1;
            ok &= R03_IR_ReportText(12, r.firstRecovery) == 1;
            ok &= R03_IR_ReportText(13, r.finalRecovery) == 1;
            ok &= R03_IR_ReportText(14, r.finalDiagnostics) == 1;
            ok &= R03_IR_ReportText(15, r.finalExecutionDiagnostics) == 1;
            // Call Seal even after a rejected store, so native failure state is
            // observed. It must never seal a failed/missing/duplicate field set.
            int seal = R03_IR_ReportSeal();
            return ok && seal == 1;
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
