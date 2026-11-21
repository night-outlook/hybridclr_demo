// D5-C10 isolated managed Player candidate. NOT part of the B1/normal
// product project. Real linked Unity/IL2CPP execution is still NotRun.
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
            public string runId;
            public string caseId;
            public string baselineId;
            public string dllPath;
            public string dllSha256;
            public string sourceTupleSha256;
            public int maximumWaitMilliseconds;
        }

        [Serializable]
        private sealed class Observation
        {
            public int schemaVersion = 1;
            public string kind = "R03D5C10PlayerObservationV1";
            public string result = "NoCoverage";
            public string runId;
            public string caseId;
            public string requestSha256;
            public string sourceTupleSha256;
            public int processId;
            public string unityVersion;
            public string platform;
            public int windowProtocolVersion;
            public int commitCode = -1;
            public int postCommitState = -1;
            public bool workerObservedP5;
            public bool workerFinished;
            public bool shadowMethodInvokeAttempted;
            public bool shadowMethodInvokeReturned;
            public int shadowMethodReturn = -1;
            public string workerExceptionType;
            public string topLevelError;
            public int[] nativeWindowFields;
            public bool nativeWindowTimedOut;
            public bool nativeObservedShadowMethodDuringP5;
            public bool nativeAllowedShadowMethodDuringP5;
            public bool actualLinkAndBinaryIdentityExternallyAuthenticated = false;
            public bool R03Accepted = false;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_WindowProtocolVersion();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ArmP5Window(int milliseconds);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReleaseP5Window();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_D5_ReadP5Window([Out] int[] fields, int count);

        private sealed class P5Worker
        {
            public bool observed;
            public bool done;
            public bool attempted;
            public bool returned;
            public int value = -1;
            public string exceptionType;

            public void Run()
            {
                int[] snapshot = new int[11];
                Stopwatch timer = Stopwatch.StartNew();
                try
                {
                    // No Unity objects or engine APIs on this worker thread.
                    // Observe the *actual* native P5 boundary, not a C# timer.
                    while (timer.ElapsedMilliseconds < 4000)
                    {
                        if (R03_D5_ReadP5Window(snapshot, snapshot.Length) == 1 &&
                            snapshot[1] == 2)
                        {
                            observed = true;
                            break;
                        }
                        Thread.Sleep(1);
                    }
                    if (!observed) return;
                    try
                    {
                        // This is intentionally a REAL active-shadow body
                        // attempt while CommitTransaction is at P5 (before P6).
                        // Any successful body is a critical review finding.
                        Type type = Type.GetType("R03.Node, Methods", true);
                        MethodInfo method = type.GetMethod("Keep",
                            BindingFlags.Instance | BindingFlags.Public);
                        if (method == null) throw new MissingMethodException("R03.Node.Keep");
                        object instance = Activator.CreateInstance(type);
                        attempted = true;
                        object output = method.Invoke(instance, null);
                        returned = true;
                        if (output is int) value = (int)output;
                    }
                    catch (Exception error)
                    {
                        exceptionType = error.GetType().FullName;
                    }
                }
                catch (Exception error)
                {
                    exceptionType = error.GetType().FullName;
                }
                finally
                {
                    // The wait is also native-time-bounded: a broken worker
                    // cannot permanently block the transaction.
                    R03_D5_ReleaseP5Window();
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
            string requestPath = GetArg("-r03D5Request");
            if (requestPath == null) return;
            string outputPath = GetArg("-r03D5Output");
            Observation obs = new Observation
            {
                processId = Process.GetCurrentProcess().Id,
                platform = Application.platform.ToString(),
                unityVersion = Application.unityVersion,
                nativeWindowFields = new int[11]
            };
            try
            {
                if (string.IsNullOrEmpty(outputPath) || File.Exists(outputPath) ||
                    !Path.IsPathRooted(outputPath))
                    throw new InvalidOperationException("Fresh absolute output required");
                byte[] requestBytes = File.ReadAllBytes(requestPath);
                obs.requestSha256 = Hash(requestBytes);
                Request req = JsonUtility.FromJson<Request>(Encoding.UTF8.GetString(requestBytes));
                if (req == null || req.schemaVersion != 1 || req.caseId != "D5-C10" ||
                    string.IsNullOrEmpty(req.runId) || string.IsNullOrEmpty(req.baselineId) ||
                    string.IsNullOrEmpty(req.sourceTupleSha256) ||
                    req.maximumWaitMilliseconds < 20 || req.maximumWaitMilliseconds > 2000 ||
                    !Path.IsPathRooted(req.dllPath) || string.IsNullOrEmpty(req.dllSha256))
                    throw new InvalidOperationException("Invalid D5-C10 request envelope");
                obs.caseId = req.caseId;
                obs.runId = req.runId;
                obs.sourceTupleSha256 = req.sourceTupleSha256;
                if (Application.platform != RuntimePlatform.OSXPlayer ||
                    Application.unityVersion != "2022.3.62f2")
                    throw new InvalidOperationException("Requires Unity 2022.3.62f2 macOS Player");
                byte[] dll = File.ReadAllBytes(req.dllPath);
                if (!string.Equals(Hash(dll), req.dllSha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Methods.dll exact SHA-256 mismatch");
                obs.windowProtocolVersion = R03_D5_WindowProtocolVersion();
                if (obs.windowProtocolVersion != 1)
                    throw new InvalidOperationException("D5 native window overlay was not linked/enabled");
                var names = new[] { "A", "B", "Layout", "Methods", "R03Contract" };
                if (AssemblyShadowRuntime.ConfigureCandidates(req.baselineId,
                    names, new[] { "mscorlib" }) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.BeginTransaction("D5-C10-" + req.runId,
                        req.baselineId, new[] { "Methods" }, 2) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.ReserveMetadataBudget(
                        new[] { dll.LongLength }, 2) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.StageAssembly(dll, null) != AssemblyShadowErrorCode.Success ||
                    AssemblyShadowRuntime.ValidateTransaction() != AssemblyShadowErrorCode.Success)
                    throw new InvalidOperationException("D5 fixture staged transaction failed");
                if (R03_D5_ArmP5Window(req.maximumWaitMilliseconds) != 1)
                    throw new InvalidOperationException("Native D5 probe arm refused");
                var worker = new P5Worker();
                Thread thread = new Thread(worker.Run) { IsBackground = true };
                thread.Start(); // before the native P5 publication
                obs.commitCode = (int)AssemblyShadowRuntime.CommitTransaction();
                obs.workerFinished = thread.Join(5000);
                obs.workerObservedP5 = worker.observed;
                obs.shadowMethodInvokeAttempted = worker.attempted;
                obs.shadowMethodInvokeReturned = worker.returned;
                obs.shadowMethodReturn = worker.value;
                obs.workerExceptionType = worker.exceptionType;
                AssemblyShadowState state;
                if (AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success)
                    obs.postCommitState = (int)state;
                if (R03_D5_ReadP5Window(obs.nativeWindowFields, 11) != 1)
                    throw new InvalidOperationException("Native window fixed receipt unreadable");
                obs.nativeWindowTimedOut = obs.nativeWindowFields[6] != 0;
                obs.nativeObservedShadowMethodDuringP5 = obs.nativeWindowFields[7] != 0;
                obs.nativeAllowedShadowMethodDuringP5 = obs.nativeWindowFields[8] != 0;
                obs.result = obs.nativeAllowedShadowMethodDuringP5 ?
                    "UnsafeEarlyMethodAdmissionObserved" :
                    (obs.workerFinished && obs.workerObservedP5 &&
                     obs.nativeObservedShadowMethodDuringP5 && !obs.nativeWindowTimedOut ?
                        "CandidateObservedDeniedInP5_RequiresIndependentBinaryProof" : "NoCoverage");
            }
            catch (Exception error)
            {
                obs.topLevelError = error.GetType().FullName;
                obs.result = "NoCoverage";
            }
            finally
            {
                if (!string.IsNullOrEmpty(outputPath) && Path.IsPathRooted(outputPath))
                {
                    try
                    {
                        // CreateNew is mandatory: no prior evidence overwrite.
                        using (var stream = new FileStream(outputPath,
                            FileMode.CreateNew, FileAccess.Write, FileShare.None))
                        using (var writer = new StreamWriter(stream, new UTF8Encoding(false)))
                            writer.Write(JsonUtility.ToJson(obs, true));
                    }
                    catch (Exception) { /* Native/Player raw logs remain evidence. */ }
                }
                Application.Quit(0);
            }
        }

        private static string GetArg(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == key) return args[i+1];
            return null;
        }

        private static string Hash(byte[] bytes)
        {
            using (SHA256 hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).
                    Replace("-", "").ToLowerInvariant();
        }
    }
}
