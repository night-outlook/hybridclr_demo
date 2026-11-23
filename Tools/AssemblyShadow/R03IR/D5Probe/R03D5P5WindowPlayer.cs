// D5-C10 isolated source-only real Player candidate, never product assembly.
// The only durable C10 result is the native preopened fixed binary receipt.
// Managed post-terminal JSON/FileStream/exception formatting is forbidden.
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadow.R03.D5
{
    [Preserve]
    public static class R03D5P5WindowPlayer
    {
        [Serializable]
        private sealed class Request
        {
            public int schemaVersion;
            public string runId, caseId, baselineId, dllPath, dllSha256, sourceTupleSha256;
            public int maximumWaitMilliseconds;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_WindowProtocolVersion();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ArmP5Window(int milliseconds);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReleaseP5Window();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReadP5Window([Out] int[] fields, int count);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReceiptOpen(string path, string runId,
            string requestSha256, string fixtureSha256);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReceiptEvent(int slot, int a, int b, int c, int d);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_BindKeepCanary(IntPtr liveGcHandle);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReceiptSeal(int commit, int state, int workerFinished, int keepAttempted);

        private sealed class P5Worker
        {
            public bool observed;
            public bool done;
            public bool keepAttempted;
            public bool keepReturned;
            public bool nativeBindSucceeded;

            public void Run()
            {
                int[] snapshot = new int[11];
                Stopwatch timer = Stopwatch.StartNew();
                try
                {
                    // The method name and primitive field are exact fixtures.
                    // A constructor rejection MUST NOT become a Keep denial.
                    while (timer.ElapsedMilliseconds < 4000)
                    {
                        if (R03_D5_ReadP5Window(snapshot, snapshot.Length) == 1 &&
                            snapshot[1] == 2)
                        {
                            observed = true;
                            R03_D5_ReceiptEvent(2, snapshot[1], snapshot[3], snapshot[4], 0);
                            break;
                        }
                        Thread.Sleep(1);
                    }
                    if (!observed) return;

                    Type type = Type.GetType("R03.Node, Methods", true);
                    MethodInfo method = type.GetMethod("Keep",
                        BindingFlags.Instance | BindingFlags.Public);
                    if (method == null || method.ReturnType != typeof(int) ||
                        method.GetParameters().Length != 0)
                        return;
                    object instance = Activator.CreateInstance(type); // NOT Keep.
                    if (instance == null) return;

                    GCHandle handle = GCHandle.Alloc(instance, GCHandleType.Normal);
                    try
                    {
                        // Native binds its own pinned strong root and reads
                        // the real private R03.Node.stable int field.
                        nativeBindSucceeded = R03_D5_BindKeepCanary(
                            GCHandle.ToIntPtr(handle)) == 1;
                        if (!nativeBindSucceeded ||
                            R03_D5_ReadP5Window(snapshot, snapshot.Length) != 1 ||
                            snapshot[1] != 2)
                            return;
                        // Mark the EXACT intended method call before Invoke.
                        keepAttempted = R03_D5_ReceiptEvent(4, 1, 0, 0, 0) == 1;
                        if (!keepAttempted) return;
                        try
                        {
                            object output = method.Invoke(instance, null);
                            keepReturned = output is int && (int)output == 42;
                        }
                        catch (Exception)
                        {
                            // Do not inspect/walk a managed exception after a
                            // terminal method guard. B1 native first error is
                            // authoritative; missing receipt stays NoCoverage.
                        }
                        finally
                        {
                            // A failed P/Invoke here is not proof of denial;
                            // native method guard and canary remain authoritative.
                            R03_D5_ReceiptEvent(5, keepReturned ? 1 : 2,
                                keepReturned ? 42 : -1, 0, 0);
                        }
                    }
                    finally { handle.Free(); }
                }
                catch (Exception)
                {
                    // Constructor, reflection or binder errors are NOT Keep
                    // guard results. Never promote a generic exception.
                }
                finally
                {
                    R03_D5_ReleaseP5Window(); // native timer is also bounded
                    done = true;
                }
            }
        }

        private static bool s_started;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        [Preserve]
        private static void Start()
        {
            if (s_started) return;
            s_started = true;
            string requestPath = Arg("-r03D5Request");
            if (string.IsNullOrEmpty(requestPath)) return;
            string outputPath = Arg("-r03D5Output");
            int commit = -1, stateCode = -1, finish = 0, keep = 0;
            bool receiptOpened = false;
            Thread thread = null;
            P5Worker worker = null;
            try
            {
                if (string.IsNullOrEmpty(outputPath) ||
                    !Path.IsPathRooted(outputPath) || File.Exists(outputPath) ||
                    !Path.IsPathRooted(requestPath))
                    throw new InvalidOperationException("Fresh absolute native C10 evidence required");
                byte[] requestBytes = File.ReadAllBytes(requestPath);
                Request req = JsonUtility.FromJson<Request>(Encoding.UTF8.GetString(requestBytes));
                if (req == null || req.schemaVersion != 1 || req.caseId != "D5-C10" ||
                    string.IsNullOrEmpty(req.runId) || string.IsNullOrEmpty(req.baselineId) ||
                    string.IsNullOrEmpty(req.sourceTupleSha256) ||
                    req.maximumWaitMilliseconds < 20 || req.maximumWaitMilliseconds > 2000 ||
                    string.IsNullOrEmpty(req.dllPath) || !Path.IsPathRooted(req.dllPath) ||
                    string.IsNullOrEmpty(req.dllSha256))
                    throw new InvalidOperationException("Invalid D5-C10 source request");
                if (Application.platform != RuntimePlatform.OSXPlayer ||
                    Application.unityVersion != "2022.3.62f2")
                    throw new InvalidOperationException("Requires real Unity 2022.3.62f2 macOS IL2CPP");
                byte[] dll = File.ReadAllBytes(req.dllPath);
                if (!string.Equals(Sha(dll), req.dllSha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Methods.dll exact SHA mismatch");
                if (R03_D5_WindowProtocolVersion() != 1)
                    throw new InvalidOperationException("Native D5 witness is not linked");
                // Open once, before registration/staging/commit/possible poison.
                receiptOpened = R03_D5_ReceiptOpen(outputPath, req.runId,
                    Sha(requestBytes), Sha(dll)) == 1;
                if (!receiptOpened) throw new InvalidOperationException("Native evidence exclusive open failed");
                if (AssemblyShadowRuntime.ConfigureCandidates(req.baselineId,
                        new[] { "A", "B", "Layout", "Methods", "R03Contract" },
                        new[] { "mscorlib" }) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.BeginTransaction("D5-C10-" + req.runId,
                        req.baselineId, new[] { "Methods" }, 2) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.ReserveMetadataBudget(
                        new[] { dll.LongLength }, 2) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.StageAssembly(dll, null) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.ValidateTransaction() != AssemblyShadowErrorCode.Success)
                    throw new InvalidOperationException("D5 fixture did not validate");
                if (R03_D5_ReceiptEvent(1, 1, 0, 0, 0) != 1 ||
                    R03_D5_ArmP5Window(req.maximumWaitMilliseconds) != 1)
                    throw new InvalidOperationException("Native C10 arming failed");
                worker = new P5Worker();
                thread = new Thread(worker.Run) { IsBackground = true };
                thread.Start();
                commit = (int)AssemblyShadowRuntime.CommitTransaction();
            }
            catch (Exception)
            {
                // All post-commit factual error provenance belongs to the
                // native first-error source, not managed exception messages.
            }
            finally
            {
                try
                {
                    if (thread != null && thread.Join(5000))
                    {
                        finish = 1;
                        keep = worker != null && worker.keepAttempted ? 1 : 0;
                    }
                }
                catch (Exception) { finish = 0; }
                try
                {
                    AssemblyShadowState state;
                    if (AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success)
                        stateCode = (int)state;
                }
                catch (Exception) { stateCode = -1; }
                int sealedResult = -1;
                try
                {
                    if (receiptOpened)
                        sealedResult = R03_D5_ReceiptSeal(commit, stateCode, finish, keep);
                }
                catch (Exception) { sealedResult = -1; }
                // A complete native file is only a *candidate*. Real binary/PID
                // admission and independent C10 classification remain required.
                Application.Quit(sealedResult == 1 && finish == 1 ? 0 : 2);
            }
        }

        private static string Arg(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == key) return args[i + 1];
            return null;
        }
        private static string Sha(byte[] bytes)
        {
            using (SHA256 hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).
                    Replace("-", "").ToLowerInvariant();
        }
    }
}
