using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;

namespace AssemblyShadow.R03.Player
{
    [Serializable] public sealed class InputDll { public string name; public string path; public string sha256; }
    [Serializable] public sealed class Request
    {
        public int schemaVersion;
        public string runId;
        public string caseId;
        public string baselineId;
        public string[] candidates;
        public string[] stable;
        public string[] roots;
        public InputDll[] dlls;
        public string invokeAssembly;
        public bool observeMethod;
        public bool oldExecutionGuard;
        public bool noPatch;
    }
    [Serializable] public sealed class Step { public string phase; public int code; public int state; }
    [Serializable] public sealed class Result
    {
        public int schemaVersion = 2;
        public string kind = "R03PlayerObservation";
        public string runId;
        public string caseId;
        public string requestSha256;
        public int pid;
        public string startedUtc;
        public string endedUtc;
        public string unityVersion;
        public string platform;
        public bool il2cpp;
        public bool published;
        public string phase;
        public Step[] steps;
        public string exception;
        public string exceptionType;
        public string exceptionStack;
        public int invocationResult;
        public int delegateResult;
        public int warmAllocationCount;
        public string beforeWarm;
        public string afterWarm;
        public string nativeMethod;
        public string runtimeProbe;
        public string diagnostics;
        public int diagnosticsCode;
        public int finalState;
        public string recovery;
        public int recoveryCode;
        public long managedBytesBefore;
        public long managedBytesAfter;
        public bool acceptance = false;
    }

    public static class R03Player
    {
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_ObserveMethod(string assembly, string namespaze, string type, string method,
            int oldGuard, [Out] byte[] output, int capacity);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_BeginWarmProbe(string assembly);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_MarkWarmProbe(int boundary);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_ReadRuntimeProbe([Out] byte[] output, int capacity);
        private static readonly byte[] RuntimeProbeBuffer = new byte[131072];
        private static bool started;
        private static readonly List<Step> Steps = new List<Step>();
        private static Result result;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Start()
        {
            if (started) return;
            started = true;
            string requestPath = Argument("-r03Request");
            if (requestPath == null) return;
            string outputPath = Argument("-r03Output");
            result = new Result { startedUtc = DateTime.UtcNow.ToString("O"), pid = Process.GetCurrentProcess().Id,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), phase = "Input" };
#if ENABLE_IL2CPP && !UNITY_EDITOR
            result.il2cpp = true;
#endif
            try
            {
                if (outputPath == null || File.Exists(outputPath)) throw new IOException("An unused output path is required.");
                byte[] requestBytes = File.ReadAllBytes(requestPath);
                result.requestSha256 = Hash(requestBytes);
                var request = JsonUtility.FromJson<Request>(Encoding.UTF8.GetString(requestBytes));
                if (request == null || request.schemaVersion != 1 || string.IsNullOrEmpty(request.runId) ||
                    string.IsNullOrEmpty(request.caseId) || string.IsNullOrEmpty(request.baselineId) ||
                    request.candidates == null || request.stable == null || request.roots == null || request.dlls == null)
                    throw new InvalidDataException("Incomplete request.");
                result.runId = request.runId; result.caseId = request.caseId;
                if (Argument("-r03RunId") != request.runId) throw new InvalidDataException("Launch nonce mismatch.");
                if (!result.il2cpp) throw new InvalidOperationException("This witness requires an IL2CPP Player.");
                var bytes = new List<byte[]>();
                foreach (var item in request.dlls)
                {
                    if (item == null || string.IsNullOrEmpty(item.name) || !Path.IsPathRooted(item.path))
                        throw new InvalidDataException("Each DLL requires an absolute input path and identity.");
                    byte[] dll = File.ReadAllBytes(item.path);
                    if (Hash(dll) != item.sha256) throw new InvalidDataException("Input DLL hash mismatch: " + item.name);
                    bytes.Add(dll);
                }
                result.managedBytesBefore = GC.GetTotalMemory(false);
                if (request.noPatch)
                {
                    result.phase = "BaselineInvoke";
                    Invoke(request.invokeAssembly);
                    result.phase = "Completed";
                    return;
                }
                // This fixed test bootstrap touches no fixture type before
                // registration. It does not prove production early startup or
                // authorize these deliberately invalid deployment inputs.
                if (!Call("Configure", () => AssemblyShadowRuntime.ConfigureCandidates(request.baselineId, request.candidates, request.stable))) return;
                if (!Call("Begin", () => AssemblyShadowRuntime.BeginTransaction("R03-" + request.runId, request.baselineId,
                    request.dlls.Select(d => d.name).ToArray(), 2))) return;
                if (!Call("Reserve", () => AssemblyShadowRuntime.ReserveMetadataBudget(bytes.Select(b => b.LongLength).ToArray(), 2))) return;
                for (int i = 0; i < bytes.Count; ++i)
                {
                    byte[] dll = bytes[i];
                    if (!Call("Stage:" + request.dlls[i].name, () => AssemblyShadowRuntime.StageAssembly(dll, null))) return;
                }
                if (!Call("Validate", AssemblyShadowRuntime.ValidateTransaction)) return;
                if (!Call("Commit", AssemblyShadowRuntime.CommitTransaction)) return;
                result.published = true;
                if (!string.IsNullOrEmpty(request.invokeAssembly))
                {
                    result.phase = "ActiveInvoke";
                    Invoke(request.invokeAssembly);
                }
                if (request.observeMethod)
                {
                    result.phase = "NativeMethod";
                    byte[] buffer = new byte[16384];
                    int size = R03_ObserveMethod(request.invokeAssembly, "R03", "Node", "Keep",
                        request.oldExecutionGuard ? 1 : 0, buffer, buffer.Length);
                    if (size < 1 || size >= buffer.Length) throw new InvalidOperationException("Native probe failed: " + size);
                    result.nativeMethod = Encoding.UTF8.GetString(buffer, 0, size);
                }
                result.phase = "Completed";
            }
            catch (Exception error)
            {
                result.exception = error.ToString(); result.exceptionType = error.GetType().FullName;
                result.exceptionStack = error.StackTrace;
            }
            finally
            {
                try
                {
                    int size = R03_ReadRuntimeProbe(RuntimeProbeBuffer, RuntimeProbeBuffer.Length);
                    if (size < 1 || size >= RuntimeProbeBuffer.Length) throw new InvalidOperationException("Runtime probe receipt failed: " + size);
                    result.runtimeProbe = Encoding.UTF8.GetString(RuntimeProbeBuffer, 0, size);
                }
                catch (Exception error) { result.exception = (result.exception ?? "") + "\nRuntimeProbeFailure: " + error; }
                result.managedBytesAfter = GC.GetTotalMemory(false);
                result.steps = Steps.ToArray();
                result.endedUtc = DateTime.UtcNow.ToString("O");
                try
                {
                    AssemblyShadowState state;
                    AssemblyShadowRuntime.GetState(out state); result.finalState = (int)state;
                    string diagnostics;
                    result.diagnosticsCode = (int)AssemblyShadowRuntime.GetDiagnosticsJson(out diagnostics); result.diagnostics = diagnostics;
                    string recovery;
                    result.recoveryCode = (int)AssemblyShadowRuntime.GetRecoveryInfoJson(out recovery); result.recovery = recovery;
                }
                catch (Exception error) { result.exception = (result.exception ?? "") + "\nDiagnosticFailure: " + error; }
                try
                {
                    using (var stream = new FileStream(outputPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                    using (var writer = new StreamWriter(stream, new UTF8Encoding(false)))
                        writer.Write(JsonUtility.ToJson(result, true) + "\n");
                    Application.Quit(0); // Recording success is not test acceptance.
                }
                catch (Exception error) { UnityEngine.Debug.LogException(error); Application.Quit(2); }
            }
        }

        private static bool Call(string phase, Func<AssemblyShadowErrorCode> action)
        {
            result.phase = phase;
            AssemblyShadowErrorCode code = action();
            AssemblyShadowState state; AssemblyShadowRuntime.GetState(out state);
            Steps.Add(new Step { phase = phase, code = (int)code, state = (int)state });
            return code == AssemblyShadowErrorCode.Success;
        }
        private static void Invoke(string assembly)
        {
            Type type = Type.GetType("R03.Node, " + assembly, true);
            object instance = Activator.CreateInstance(type);
            MethodInfo method = type.GetMethod("Keep", BindingFlags.Instance | BindingFlags.Public);
            result.invocationResult = (int)method.Invoke(instance, null);
            result.delegateResult = ((Func<int>)Delegate.CreateDelegate(typeof(Func<int>), instance, method))();
            string info;
            // Fixed preparation, not a retry-until-passing loop: warm the native
            // diagnostic marshalling and perform eight allocations before the
            // measured 10,000-allocation interval. Both cores use this same code.
            AssemblyShadowRuntime.GetTypeResolutionInfo(type, out info);
            for (int preparation = 0; preparation < 8; ++preparation) instance = Activator.CreateInstance(type);
            int probe = R03_BeginWarmProbe(assembly);
            if (probe < 0) throw new InvalidOperationException("Cannot bind exact warm probe: " + probe);
            if (AssemblyShadowRuntime.GetTypeResolutionInfo(type, out info) == AssemblyShadowErrorCode.Success)
                result.beforeWarm = info;
            if (probe == 1 && R03_MarkWarmProbe(1) != 1) throw new InvalidOperationException("Invalid warm start boundary.");
            for (int i = 0; i < 10000; ++i)
            { instance = Activator.CreateInstance(type); ++result.warmAllocationCount; }
            if (probe == 1 && R03_MarkWarmProbe(2) != 1) throw new InvalidOperationException("Invalid warm end boundary.");
            GC.KeepAlive(instance);
            if (AssemblyShadowRuntime.GetTypeResolutionInfo(type, out info) == AssemblyShadowErrorCode.Success)
                result.afterWarm = info;
            if (probe == 1 && R03_MarkWarmProbe(3) != 1) throw new InvalidOperationException("Invalid observer end boundary.");
        }
        private static string Argument(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == key) return args[i + 1];
            return null;
        }
        private static string Hash(byte[] bytes)
        { using (var hash = SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
    }
}
