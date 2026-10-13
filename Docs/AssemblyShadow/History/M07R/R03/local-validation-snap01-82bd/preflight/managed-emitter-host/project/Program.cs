using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Runtime.InteropServices;
public static class Bridge {
public sealed class Report
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

private static void Check(bool condition, string message)
{ if (!condition) throw new Exception("Host assertion: " + message); }
private const string Guard = "{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":1,\"stateCode\":9,\"extra\":\"synthetic guard seed, NOT actual game evidence\"}";
public static int Main(string[] args)
{
    Check(args.Length == 4, "library/mode/output/producer argv");
    IntPtr lib = NativeLibrary.Load(args[0]);
    NativeLibrary.SetDllImportResolver(typeof(Bridge).Assembly,
        (name, assembly, searchPath) => name == "__Internal" ? lib : IntPtr.Zero);
    string mode = args[1], path = args[2];
    var r = new Report {
        processId = Environment.ProcessId, result = "Passed", runId = "synthetic-host-run",
        caseId = "synthetic-" + mode, requestSha256 = new string('a',64),
        stimulus = mode.Contains("baseline") ? "baseline-owner" : "type-resolution",
        unityVersion = "2022.3.62f2", platform = "OSXPlayer",
        initialState = 6, poisonedState = 9, finalState = 9,
        nativeStimulusReturn = 1, preActiveReflection = 42, preActiveDelegate = 42,
        preCanaryCount = 1, finalCanaryCount = 1, preShadowField = 2, finalShadowField = 2,
        nativePhase = 910, terminalReportingProbeMask = 15, reserveGcProbeMask = 31,
        shadowFieldReadable = true, prePositive = true,
        activeReflectionAttempted = true, activeDelegateAttempted = true,
        aotReflectionAttempted = true, activeReflectionException = "ManagedExceptionCaught",
        activeDelegateException = "ManagedExceptionCaught", aotReflectionException = "ManagedExceptionCaught",
        firstRecovery = "{\"stateCode\":9,\"terminalFailureCode\":13}",
        finalRecovery = "{\"stateCode\":9,\"terminalFailureCode\":13}",
        finalDiagnostics = "{\"stateCode\":9}", finalExecutionDiagnostics = "{\"classes\":[]}",
        recoveryStable = true, fixedDiagnosticsReadable = true
    };
    if (mode == "occupied") {
        File.WriteAllText(path, "preserved");
        Check(R03_IR_ReportOpen(path) == -1, "occupied output rejected");
        Check(File.ReadAllText(path) == "preserved", "occupied bytes unchanged");
        Console.WriteLine("ExpectedRejectionVerified"); return 0;
    }
    Check(!File.Exists(path) && R03_IR_ReportOpen(path) == 1, "fresh output opened");
    bool expected = true;
    if (mode == "baseline" || mode == "duplicate-baseline") {
        Check(R03_IR_ReportText(8, Guard) == 1, "seed native-owned slot8 once");
        r.nativeGuardJson = Guard; // expected-value comparison only; emitter skips slot8
    }
    if (mode == "duplicate-baseline") {
        Check(R03_IR_ReportText(8, Guard) == -1, "duplicate remains forbidden"); expected = false;
    }
    if (mode == "missing-baseline") expected = false;
    if (mode == "duplicate-int") {
        Check(R03_IR_ReportInt(0, 6) == 1, "preseed integer"); expected = false;
    }
    if (mode == "off") {
        r.stimulus = "off"; r.initialState = r.poisonedState = r.finalState = 0;
        r.finalCanaryCount = 2; r.terminalReportingProbeMask = r.reserveGcProbeMask = 0;
    }
    if (mode == "failed-semantic") { r.result = "Failed"; r.failurePhase = 170; }
    if (mode == "unicode") r.error = "quotes\" backslash\\ newline\n 中文 é 🧪";
    if (mode == "exact-utf8" || mode == "oversize-utf8") {
        r.finalExecutionDiagnostics = new string('\u00e9', 131072 + (mode == "oversize-utf8" ? 1 : 0));
        Check(Encoding.UTF8.GetByteCount(r.finalExecutionDiagnostics) ==
              (mode == "exact-utf8" ? 262144 : 262146), "UTF8 byte boundary");
        expected = mode == "exact-utf8";
    }
    if (mode == "actual-producer") {
        r.finalExecutionDiagnostics = File.ReadAllText(args[3], Encoding.UTF8);
        Check(Encoding.UTF8.GetByteCount(r.finalExecutionDiagnostics) == 331078, "actual synthetic producer bytes");
        expected = false;
    }
    bool emitted = EmitNativeReport(r);
    Check(emitted == expected, "exact managed emitter result");
    if (expected) {
        using var observed = JsonDocument.Parse(File.ReadAllBytes(path));
        var root = observed.RootElement;
        Check(root.GetProperty("reportTransport").GetString() == "NativePreopenedSnapshotV1", "transport version");
        // Reflection here runs in the healthy host only, outside tested emitter.
        // Every field declared by actual Report must round-trip exactly.
        var expectedJson = JsonSerializer.SerializeToElement(r, new JsonSerializerOptions { IncludeFields = true });
        int count = 0;
        foreach (var property in expectedJson.EnumerateObject()) {
            Check(root.TryGetProperty(property.Name, out var value), "missing: " + property.Name);
            Check(value.ValueKind == property.Value.ValueKind &&
                  value.ToString() == property.Value.ToString(), "mismatch: " + property.Name);
            ++count;
        }
        Check(root.EnumerateObject().Count() == count + 1, "no additional or missing native fields");
        if (mode == "repeat-seal") Check(R03_IR_ReportSeal() == -1, "repeat seal rejected");
    } else {
        Check(new FileInfo(path).Length == 0, "incomplete evidence never serialized as complete");
        Check(R03_IR_ReportSeal() == -1, "failed transport cannot recover");
    }
    Console.WriteLine("HostRoundTripVerified");
    // No unload before process exit: the failure-path stream may still exist.
    return 0;
}

}
