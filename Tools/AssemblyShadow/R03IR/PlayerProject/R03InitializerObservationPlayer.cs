using System;
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
    // Additive diagnostic process; never receives original S/K request flags.
    [Preserve]
    public static class R03InitializerObservationPlayer
    {
        [Serializable]
        private sealed class Request
        {
            public int schemaVersion;
            public string runId, caseId, stimulus, baselineId, dllPath, dllSha256;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRW_Open(string path, string runId, string caseId,
            string stimulus, string fixtureSha256);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRW_Seal(int commitReturn, int finalState,
            int canaryBefore, int canaryAfter, int postAttempted, int postSucceeded);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRW_Trace(int phase, int a, int b, int c, int d);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_Exit(int code);

        private static bool s_started;
        private static int s_canary;
        [Preserve] private static void AotCanary() { ++s_canary; }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Run()
        {
            if (s_started) return;
            s_started = true;
            string path = Arg("-r03IrInitializerRequest");
            if (path == null) return;
            string output = Arg("-r03IrInitializerOutput");
            int commit = -1, finalState = -1, before = 0, after = 0;
            int attempted = 0, succeeded = 0;
            int lastPhase = 0;
            bool opened = false;
            try
            {
                Need(!string.IsNullOrEmpty(output) && Path.IsPathRooted(output) &&
                    !File.Exists(output), "Unused absolute output");
                var request = JsonUtility.FromJson<Request>(Encoding.UTF8.GetString(File.ReadAllBytes(path)));
                Need(request != null && request.schemaVersion == 1 &&
                    request.runId == Arg("-r03IrInitializerRunId") &&
                    !string.IsNullOrEmpty(request.caseId) &&
                    (request.stimulus == "initializer-control" ||
                     request.stimulus == "initializer-failure") &&
                    !string.IsNullOrEmpty(request.baselineId) &&
                    !string.IsNullOrEmpty(request.dllPath) &&
                    Path.IsPathRooted(request.dllPath), "Exact initializer request");
                byte[] dll = File.ReadAllBytes(request.dllPath);
                Need(Hash(dll) == request.dllSha256, "Immutable Methods DLL");
                Need(Application.platform == RuntimePlatform.OSXPlayer &&
                    Application.unityVersion == "2022.3.62f2", "Pinned macOS Player");
                lastPhase = 101;
                int openResult = R03_IRW_Open(output, request.runId, request.caseId,
                    request.stimulus, request.dllSha256);
                Need(openResult == 1, "Native output preopen");
                opened = true;
                R03_IRW_Trace(102, openResult, 0, 0, 0);
                lastPhase = 110;
                MethodInfo canary = typeof(R03InitializerObservationPlayer).GetMethod("AotCanary",
                    BindingFlags.Static | BindingFlags.NonPublic);
                Need(canary != null, "Preserved AOT canary");
                canary.Invoke(null, null);
                before = s_canary;
                R03_IRW_Trace(111, before, 0, 0, 0);
                Need(before == 1, "Healthy AOT canary");
                lastPhase = 120;
                R03_IRW_Trace(120, 0, 0, 0, 0);
                int configured = (int)AssemblyShadowRuntime.ConfigureCandidates(request.baselineId,
                    new[] { "A", "B", "Layout", "Methods", "R03Contract" },
                    new[] { "mscorlib" });
                R03_IRW_Trace(121, configured, 0, 0, 0);
                Need(configured == (int)AssemblyShadowErrorCode.Success, "Configure");
                lastPhase = 130;
                int began = (int)AssemblyShadowRuntime.BeginTransaction("R03IRW-" + request.runId,
                    request.baselineId, new[] { "Methods" }, 2);
                R03_IRW_Trace(131, began, 0, 0, 0);
                Need(began == (int)AssemblyShadowErrorCode.Success, "Begin");
                lastPhase = 140;
                int reserved = (int)AssemblyShadowRuntime.ReserveMetadataBudget(new[] { dll.LongLength }, 2);
                R03_IRW_Trace(141, reserved, 0, 0, 0);
                Need(reserved == (int)AssemblyShadowErrorCode.Success, "Reserve");
                lastPhase = 150;
                int staged = (int)AssemblyShadowRuntime.StageAssembly(dll, null);
                R03_IRW_Trace(151, staged, 0, 0, 0);
                Need(staged == (int)AssemblyShadowErrorCode.Success, "Stage");
                lastPhase = 160;
                int validated = (int)AssemblyShadowRuntime.ValidateTransaction();
                R03_IRW_Trace(161, validated, 0, 0, 0);
                Need(validated == (int)AssemblyShadowErrorCode.Success, "Validate");
                // The actual Commit invokes Methods.<Module>.cctor after publication.
                lastPhase = 190;
                R03_IRW_Trace(190, 1, 0, 0, 0);
                commit = (int)AssemblyShadowRuntime.CommitTransaction();
                R03_IRW_Trace(191, commit, 0, 0, 0);
                AssemblyShadowState state;
                lastPhase = 200;
                int getState = (int)AssemblyShadowRuntime.GetState(out state);
                finalState = (int)state;
                R03_IRW_Trace(201, getState, finalState, commit, 0);
                Need(getState == (int)AssemblyShadowErrorCode.Success, "State after Commit");
                bool failure = request.stimulus == "initializer-failure";
                lastPhase = 205;
                R03_IRW_Trace(205, failure ? 1 : 0, commit, finalState, 0);
                Need(failure ? (commit == 19 && finalState == 9) :
                               (commit == 0 && finalState == 6),
                    "Distinct initializer control/failure result");
                if (failure)
                {
                    lastPhase = 210;
                    attempted = 1;
                    R03_IRW_Trace(210, 1, s_canary, 0, 0);
                    try { canary.Invoke(null, null); succeeded = 1; }
                    catch (Exception) { /* Native first failure is authoritative. */ }
                    R03_IRW_Trace(211, succeeded, s_canary, 0, 0);
                }
                lastPhase = 220;
                after = s_canary;
                R03_IRW_Trace(220, before, after, attempted, succeeded);
                Need(after == 1 && succeeded == 0, "AOT side effect did not advance");
            }
            catch (Exception)
            {
                // Only preopened native primitive diagnostics after a terminal
                // outcome; no managed exception message/stack formatting or log.
                after = s_canary;
                if (opened)
                    R03_IRW_Trace(900, lastPhase, commit, finalState, after);
            }
            finally
            {
                // The native writer reads the pre-bound field and seals its own
                // separate diagnostic record; not a V2 acceptance snapshot.
                if (opened)
                    R03_IRW_Trace(901, commit, finalState, before, after);
                int sealedResult = opened ? R03_IRW_Seal(commit, finalState,
                    before, after, attempted, succeeded) : -1;
                R03_IR_Exit(sealedResult == 1 ? 0 : 2);
            }
        }

        private static string Arg(string key)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == key) return args[i + 1];
            return null;
        }
        private static string Hash(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }
        private static void Need(bool ok, string reason)
        {
            if (!ok) throw new InvalidOperationException("R03IR initializer: " + reason);
        }
    }
}
