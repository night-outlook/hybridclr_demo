using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>Diagnostic-only BCL callback invoked before Unity admits its global assembly catalog.</summary>
    [Preserve]
    public static class H1CountEarlyStartup
    {
        public const long MaxFixtureBytes = 32L * 1024 * 1024;
        public const int MaxNativeJsonCharacters = 1024 * 1024;
        private const string ParameterAssembly = "AssemblyShadow.H1Count.Target";
        private const string NestedAssembly = "AssemblyShadow.H1Nested.Target";
        private static string s_lastReceiptJson;
        private static Receipt s_lastReceipt;
        [Preserve]
        public static string LastReceiptJson { get { return s_lastReceiptJson; } }
        [Preserve]
        public static Receipt LastReceipt { get { return s_lastReceipt; } }

        [Preserve]
        public static int Run() { return RunArguments(Environment.GetCommandLineArgs()); }

        // Public for focused Editor tests of the no-op and fail-closed argument paths.
        public static int RunArguments(string[] args)
        {
            var receipt = new Receipt();
            Arguments input = null;
            Stopwatch elapsed = Stopwatch.StartNew();
            s_lastReceiptJson = null;
            s_lastReceipt = null;
            try
            {
                // Ordinary loading must not call any shadow/native diagnostic API at this gateway.
                if (Arguments.One(args, "-shadowH1Path") == "ordinary") return 0;
                input = Arguments.Read(args);
                receipt.resultPath = input.resultPath;
                receipt.family = input.family; receipt.path = "shadow"; receipt.caseId = input.caseId;
                receipt.baselineBuildId = input.baselineBuildId; receipt.runtimeAbiHash = input.runtimeAbiHash;
                receipt.expectedOutcome = input.expectedOutcome; receipt.expectedCount = input.expectedCount;
                receipt.fixturePath = input.fixturePath; receipt.fixtureSha256Expected = input.fixtureSha256;
                receipt.processId = Process.GetCurrentProcess().Id;
                receipt.managedThreadId = Environment.CurrentManagedThreadId;
                receipt.startUtc = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture);
                RequireNewPath(input.resultPath);
                byte[] bytes = ReadFixture(input.fixturePath);
                receipt.fixtureSize = bytes.LongLength;
                receipt.inputHashBefore = Sha256(bytes);
                Require(receipt.inputHashBefore == input.fixtureSha256, "Fixture SHA-256 differs from the launcher digest.");
                Snapshot(receipt, "before");
                string target = input.family == "parameters" ? ParameterAssembly : NestedAssembly;
                Operation(receipt, "configure", delegate { return AssemblyShadowRuntime.ConfigureCandidates(input.baselineBuildId,
                    new[] { ParameterAssembly, NestedAssembly }, new[] { "mscorlib" }); });
                Operation(receipt, "begin", delegate { return AssemblyShadowRuntime.BeginTransaction(input.caseId, input.baselineBuildId, new[] { target }, 2); });
                Operation(receipt, "reserve", delegate { return AssemblyShadowRuntime.ReserveMetadataBudget(new[] { bytes.LongLength }, 2); });
                Operation(receipt, "stage", delegate { return AssemblyShadowRuntime.StageAssembly(bytes, null); });
                AssemblyShadowErrorCode validation = Operation(receipt, "validate", AssemblyShadowRuntime.ValidateTransaction, false);
                VerifyUnchangedInput(receipt, input);
                if (input.expectedOutcome == "ControlledRejected")
                {
                    Require(validation == AssemblyShadowErrorCode.ReferenceResolutionFailed,
                        "Expected count validation rejection; observed " + validation + ".");
                    RequireState(AssemblyShadowState.Failed);
                    // The failed transaction remains retained. Returning nonzero prevents Unity catalog admission.
                    receipt.disposition = "ValidationFailedNoCommitNoAbort";
                    receipt.result = "ExpectedValidationRejection";
                    receipt.callbackReturnCode = 1;
                }
                else
                {
                    Require(validation == AssemblyShadowErrorCode.Success, "Validation failed: " + validation + ".");
                    RequireState(AssemblyShadowState.Validated);
                    Operation(receipt, "commit", AssemblyShadowRuntime.CommitTransaction);
                    RequireState(AssemblyShadowState.Committed);
                    receipt.committed = true;
                    receipt.disposition = "CommittedForSceneHandoff";
                    receipt.result = "Committed";
                    receipt.callbackReturnCode = 0;
                }
                Snapshot(receipt, "after");
                Snapshot(receipt, "final");
            }
            catch (Exception error)
            {
                receipt.result = "Failed"; receipt.callbackReturnCode = 2; receipt.error = error.ToString();
                if (input != null)
                {
                    try { Snapshot(receipt, "failure"); }
                    catch (Exception observationError) { receipt.error += "\nFailure observation: " + observationError; }
                }
            }
            receipt.elapsedTicks = elapsed.ElapsedTicks;
            receipt.endUtc = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture);
            string json = ReceiptCodec.Authenticate(receipt);
            s_lastReceiptJson = json;
            s_lastReceipt = receipt;
            if (input != null)
            {
                try { WriteNew(input.resultPath, json); }
                catch (Exception error)
                {
                    receipt.result = "Failed"; receipt.callbackReturnCode = 2;
                    receipt.error += "\nReceipt write: " + error;
                    s_lastReceiptJson = ReceiptCodec.Authenticate(receipt);
                    s_lastReceipt = receipt;
                }
            }
            return receipt.callbackReturnCode;
        }

        private static AssemblyShadowErrorCode Operation(Receipt receipt, string phase,
            Func<AssemblyShadowErrorCode> operation, bool requireSuccess = true)
        {
            AssemblyShadowErrorCode code = operation();
            receipt.operations.Add(new OperationReceipt { phase = phase, code = code.ToString(), intCode = (int)code });
            if (code == AssemblyShadowErrorCode.BaselineAlreadyUsed) receipt.baselineAlreadyUsed = true;
            Snapshot(receipt, "after-" + phase);
            Require(!requireSuccess || code == AssemblyShadowErrorCode.Success, phase + " failed: " + code + ".");
            return code;
        }

        private static void Snapshot(Receipt receipt, string phase)
        {
            var snapshot = new SnapshotReceipt { phase = phase };
            receipt.snapshots.Add(snapshot);
            string nativeJson, diagnosticsJson;
            AssemblyShadowErrorCode nativeCode = GetSnapshot(out nativeJson);
            snapshot.nativeCode = nativeCode.ToString(); snapshot.nativeJson = nativeJson;
            AssemblyShadowErrorCode diagnosticsCode = AssemblyShadowRuntime.GetDiagnosticsJson(out diagnosticsJson);
            snapshot.diagnosticsCode = diagnosticsCode.ToString(); snapshot.diagnosticsJson = diagnosticsJson;
            Require(nativeCode == AssemblyShadowErrorCode.Success && diagnosticsCode == AssemblyShadowErrorCode.Success,
                "Native startup observation is unavailable at " + phase + ".");
            Require(!string.IsNullOrEmpty(nativeJson) && nativeJson.Length <= MaxNativeJsonCharacters &&
                !string.IsNullOrEmpty(diagnosticsJson) && diagnosticsJson.Length <= MaxNativeJsonCharacters,
                "Native startup observation exceeds its bounds or is empty.");
        }

        private static void RequireState(AssemblyShadowState expected)
        {
            AssemblyShadowState actual;
            Require(AssemblyShadowRuntime.GetState(out actual) == AssemblyShadowErrorCode.Success && actual == expected,
                "Unexpected retained transaction state: " + actual + "; expected " + expected + ".");
        }

        private static void VerifyUnchangedInput(Receipt receipt, Arguments input)
        {
            byte[] after = ReadFixture(input.fixturePath);
            receipt.inputHashAfter = Sha256(after);
            Require(after.LongLength == receipt.fixtureSize && receipt.inputHashAfter == receipt.inputHashBefore,
                "Fixture bytes changed during the early transaction.");
        }

        public static byte[] ReadFixture(string path)
        {
            RequireAbsoluteRegularFile(path);
            using (var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
            {
                Require(stream.Length > 0 && stream.Length <= MaxFixtureBytes, "Fixture length exceeds the diagnostic bound.");
                byte[] bytes = new byte[(int)stream.Length];
                int offset = 0;
                while (offset < bytes.Length)
                {
                    int count = stream.Read(bytes, offset, bytes.Length - offset);
                    Require(count > 0, "Fixture ended before its captured length.");
                    offset += count;
                }
                Require(stream.ReadByte() == -1, "Fixture grew during bounded read.");
                return bytes;
            }
        }

        private static void RequireAbsoluteRegularFile(string path)
        {
            Require(Path.IsPathRooted(path) && Path.GetFullPath(path) == path && File.Exists(path), "Fixture must be an absolute regular file.");
            Require((File.GetAttributes(path) & (FileAttributes.Directory | FileAttributes.ReparsePoint)) == 0,
                "Fixture must not be a directory or symbolic link.");
        }

        private static void RequireNewPath(string path)
        {
            Require(Path.IsPathRooted(path) && Path.GetFullPath(path) == path &&
                !File.Exists(path) && !Directory.Exists(path), "Early receipt requires a new absolute file path.");
            string parent = Path.GetDirectoryName(path);
            Require(Directory.Exists(parent), "Early receipt parent directory must already exist.");
            for (var directory = new DirectoryInfo(parent); directory != null; directory = directory.Parent)
                Require((directory.Attributes & FileAttributes.ReparsePoint) == 0, "Early receipt parent must not be a symbolic link.");
        }

        private static void WriteNew(string path, string json)
        {
            RequireNewPath(path);
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(json);
        }

        public static string Sha256(byte[] bytes)
        {
            using (var sha = SHA256.Create())
            {
                var text = new StringBuilder(64);
                foreach (byte value in sha.ComputeHash(bytes)) text.Append(value.ToString("x2", CultureInfo.InvariantCulture));
                return text.ToString();
            }
        }

        private static bool IsSha256(string value)
        {
            if (value == null || value.Length != 64) return false;
            foreach (char c in value) if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f')) return false;
            return true;
        }
        private static void Require(bool condition, string error) { if (!condition) throw new InvalidDataException(error); }

#if UNITY_EDITOR || !ENABLE_IL2CPP
        private static AssemblyShadowErrorCode GetSnapshot(out string json)
        {
            json = null;
            throw new NotSupportedException("H1 early diagnostics require the diagnostic IL2CPP Player.");
        }
#else
        [Preserve, MethodImpl(MethodImplOptions.InternalCall)]
        private static extern AssemblyShadowErrorCode GetSnapshot(out string json);
#endif

        public sealed class Arguments
        {
            public string resultPath, family, caseId, fixturePath, fixtureSha256, baselineBuildId, runtimeAbiHash, expectedOutcome;
            public int expectedCount;
            public static Arguments Read(string[] args)
            {
                Require(One(args, "-shadowH1Path") == "shadow", "Unknown H1 loader path.");
                var value = new Arguments {
                    resultPath = One(args, "-shadowH1EarlyResult"), family = One(args, "-shadowH1Family"), caseId = One(args, "-shadowH1Case"),
                    fixturePath = One(args, "-shadowH1Fixture"), fixtureSha256 = One(args, "-shadowH1FixtureSha256"),
                    baselineBuildId = One(args, "-shadowH1BaselineBuildId"), runtimeAbiHash = One(args, "-shadowH1RuntimeAbiHash"),
                    expectedOutcome = One(args, "-shadowH1ExpectedOutcome")
                };
                Require(value.family == "parameters" || value.family == "nested", "Unknown count family.");
                Require(value.caseId.StartsWith(value.family == "parameters" ? "H1R-P" : "H1R-N", StringComparison.Ordinal), "Case and family differ.");
                Require(value.expectedOutcome == "Accepted" || value.expectedOutcome == "ControlledRejected", "Unknown expected outcome.");
                Require(int.TryParse(One(args, "-shadowH1ExpectedCount"), NumberStyles.None, CultureInfo.InvariantCulture, out value.expectedCount) &&
                    value.expectedCount >= 0 && value.expectedCount <= 65537, "Expected count is outside the H1 fixture range.");
                Require(IsSha256(value.fixtureSha256) && IsSha256(value.runtimeAbiHash), "Malformed H1 SHA-256 argument.");
                return value;
            }
            public static string One(string[] args, string name)
            {
                string result = null;
                Require(args != null, "Arguments are missing.");
                for (int i = 0; i < args.Length; ++i)
                    if (args[i] == name)
                    {
                        Require(result == null && i + 1 < args.Length && !string.IsNullOrEmpty(args[i + 1]) &&
                            args[i + 1].Length <= 16384 && !args[i + 1].StartsWith("-shadow", StringComparison.Ordinal), "Missing or duplicate argument: " + name);
                        result = args[i + 1];
                    }
                Require(result != null, "Missing argument: " + name);
                return result;
            }
        }

        public sealed class Receipt
        {
            public int schemaVersion = 1, callbackReturnCode = 2, processId, managedThreadId, expectedCount;
            public string kind = "H1CountEarlyStartupResult", result = "Failed", error = "", disposition = "Uncompleted";
            public string resultPath = "", family = "", path = "shadow", caseId = "", baselineBuildId = "", runtimeAbiHash = "";
            public string expectedOutcome = "", fixturePath = "", fixtureSha256Expected = "", inputHashBefore = "", inputHashAfter = "";
            public string startUtc = "", endUtc = "", receiptSha256 = "";
            public long fixtureSize, elapsedTicks, stopwatchFrequency = Stopwatch.Frequency;
            public bool diagnosticOnly = true, committed, baselineAlreadyUsed;
            public List<OperationReceipt> operations = new List<OperationReceipt>();
            public List<SnapshotReceipt> snapshots = new List<SnapshotReceipt>();
        }
        public sealed class OperationReceipt { public string phase, code; public int intCode; }
        public sealed class SnapshotReceipt { public string phase, nativeCode, nativeJson, diagnosticsCode, diagnosticsJson; }

        public static class ReceiptCodec
        {
            // Digest is SHA-256 of this exact compact UTF-8 encoding with receiptSha256 empty.
            public static string Authenticate(Receipt value)
            {
                value.receiptSha256 = "";
                value.receiptSha256 = Sha256(Encoding.UTF8.GetBytes(Serialize(value)));
                return Serialize(value);
            }

            public static bool VerifySerialized(string json, string suppliedHash)
            {
                if (string.IsNullOrEmpty(json) || !IsSha256(suppliedHash)) return false;
                string signedSuffix = ",\"receiptSha256\":\"" + suppliedHash + "\"}";
                if (!json.EndsWith(signedSuffix, StringComparison.Ordinal)) return false;
                string unsigned = json.Substring(0, json.Length - signedSuffix.Length) +
                    ",\"receiptSha256\":\"\"}";
                return Sha256(Encoding.UTF8.GetBytes(unsigned)) == suppliedHash;
            }

            public static string Serialize(Receipt r)
            {
                var b = new StringBuilder(4096); b.Append('{');
                Property(b, "schemaVersion", r.schemaVersion); Property(b, "kind", r.kind); Property(b, "diagnosticOnly", r.diagnosticOnly);
                Property(b, "result", r.result); Property(b, "error", r.error); Property(b, "disposition", r.disposition);
                Property(b, "callbackReturnCode", r.callbackReturnCode); Property(b, "processId", r.processId); Property(b, "managedThreadId", r.managedThreadId);
                Property(b, "resultPath", r.resultPath); Property(b, "family", r.family); Property(b, "path", r.path); Property(b, "caseId", r.caseId);
                Property(b, "baselineBuildId", r.baselineBuildId); Property(b, "runtimeAbiHash", r.runtimeAbiHash);
                Property(b, "expectedOutcome", r.expectedOutcome); Property(b, "expectedCount", r.expectedCount);
                Property(b, "fixturePath", r.fixturePath); Property(b, "fixtureSha256Expected", r.fixtureSha256Expected); Property(b, "fixtureSize", r.fixtureSize);
                Property(b, "inputHashBefore", r.inputHashBefore); Property(b, "inputHashAfter", r.inputHashAfter);
                Property(b, "startUtc", r.startUtc); Property(b, "endUtc", r.endUtc); Property(b, "elapsedTicks", r.elapsedTicks); Property(b, "stopwatchFrequency", r.stopwatchFrequency);
                Property(b, "committed", r.committed); Property(b, "baselineAlreadyUsed", r.baselineAlreadyUsed);
                Name(b, "operations"); b.Append('[');
                for (int i = 0; i < r.operations.Count; ++i) { if (i != 0) b.Append(','); var v = r.operations[i]; b.Append('{'); Property(b, "phase", v.phase); Property(b, "code", v.code); Property(b, "intCode", v.intCode); b.Append('}'); }
                b.Append(']'); Name(b, "snapshots"); b.Append('[');
                for (int i = 0; i < r.snapshots.Count; ++i) { if (i != 0) b.Append(','); var v = r.snapshots[i]; b.Append('{'); Property(b, "phase", v.phase); Property(b, "nativeCode", v.nativeCode); Property(b, "nativeJson", v.nativeJson); Property(b, "diagnosticsCode", v.diagnosticsCode); Property(b, "diagnosticsJson", v.diagnosticsJson); b.Append('}'); }
                b.Append(']'); Property(b, "receiptSha256", r.receiptSha256); b.Append('}'); return b.ToString();
            }
            private static void Property(StringBuilder b, string name, string value) { Name(b, name); String(b, value ?? ""); }
            private static void Property(StringBuilder b, string name, long value) { Name(b, name); b.Append(value.ToString(CultureInfo.InvariantCulture)); }
            private static void Property(StringBuilder b, string name, bool value) { Name(b, name); b.Append(value ? "true" : "false"); }
            private static void Name(StringBuilder b, string name) { if (b[b.Length - 1] != '{') b.Append(','); String(b, name); b.Append(':'); }
            private static void String(StringBuilder b, string value)
            {
                b.Append('"');
                foreach (char c in value)
                {
                    switch (c)
                    {
                        case '"': b.Append("\\\""); break; case '\\': b.Append("\\\\"); break;
                        case '\n': b.Append("\\n"); break; case '\r': b.Append("\\r"); break; case '\t': b.Append("\\t"); break;
                        default: if (c < 32) b.Append("\\u").Append(((int)c).ToString("x4")); else b.Append(c); break;
                    }
                }
                b.Append('"');
            }
        }
    }
}
