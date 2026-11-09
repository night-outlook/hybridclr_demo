// Fresh isolated R03 A2 Player. No historical S/K/initializer07 reuse.
// This source is inert unless -r03IrCapturedRequest is explicitly present.
// It calls the exact native physical-generic witness only AFTER Commit=0/6.
// Unity IL2CPP compilation and runtime are Local Validation obligations.
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadow.R03.IR
{
    [Preserve]
    public static class R03CapturedGenericPlayer
    {
        [Serializable, Preserve]
        private sealed class Request
        {
            public int schemaVersion;
            public string runId, caseId, stimulus, baselineId, dllPath, dllSha256;
        }

        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRG_Open(
            string path, string runId, string caseId, string fixtureSha256,
            string ownerAssembly);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRG_Probe();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRG_AttemptRuntimeInvoke();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRG_Seal();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRB1_Open(string path, string runId,
            string caseId, string fixtureSha256);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IRB1_Seal(int expectedCode, int expectedOrigin);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_Exit(int status);

        private static bool s_started;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Run()
        {
            if (s_started) return;
            s_started = true;
            string path = Argument("-r03IrCapturedRequest");
            if (path == null) return; // Never run during original R03 or initializer.
            try
            {
                string output = Argument("-r03IrCapturedOutput");
                string nonce = Argument("-r03IrCapturedRunId");
                Need(!string.IsNullOrEmpty(path) && Path.IsPathRooted(path) &&
                     !string.IsNullOrEmpty(output) && Path.IsPathRooted(output) &&
                     !File.Exists(output), "Fresh absolute isolated inputs/output");
                var request = JsonUtility.FromJson<Request>(
                    Encoding.UTF8.GetString(File.ReadAllBytes(path)));
                Need(request != null && request.schemaVersion == 1 &&
                     request.runId == nonce && request.caseId == "IR-R03-02-captured-generic" &&
                     request.stimulus == "captured-generic" &&
                     !string.IsNullOrEmpty(request.baselineId) &&
                     !string.IsNullOrEmpty(request.dllPath) &&
                     Path.IsPathRooted(request.dllPath),
                     "Exact test-only physical captured-generic request");
                byte[] dll = File.ReadAllBytes(request.dllPath);
                Need(Hash(dll) == request.dllSha256,
                     "Source-bound actual captured-generic Methods DLL");
                Need(Application.unityVersion == "2022.3.62f2" &&
                     Application.platform == RuntimePlatform.OSXPlayer,
                     "Exact macOS Unity 2022.3.62f2 Player");
                // Warm exactly one shared generic AOT body without referencing
                // any physical Methods type. Compile this exact independent
                // owner into the isolated AOT Player, not the hot-update DLL.
                Need(R03CapturedGenericAotOwner.Calls == 0 &&
                     R03CapturedGenericAotOwner.WarmShared() == 42 &&
                     R03CapturedGenericAotOwner.Calls == 1,
                     "Healthy actual AOT generic prepositive");
                string owner = typeof(R03CapturedGenericAotOwner)
                               .Assembly.GetName().Name;
                Need(!string.IsNullOrEmpty(owner) && owner != "Methods",
                     "Separate original AOT owner assembly");
                // Native fd and physical owner are bound before any Shadow
                // candidate/transaction activity. No baseline Methods Type
                // or R03.Node is resolved by managed code in this phase.
                Need(R03_IRG_Open(output, request.runId, request.caseId,
                                  request.dllSha256, owner) == 1,
                     "Exclusive native physical generic witness/open");
                Need(R03_IRB1_Open(output + ".first-error-b1.json",
                                   request.runId, request.caseId, request.dllSha256) == 1,
                     "Independent native B1 first-error preopen");
                Need(AssemblyShadowRuntime.ConfigureCandidates(
                         request.baselineId,
                         new[] { "A", "B", "Layout", "Methods", "R03Contract" },
                         new[] { "mscorlib" }) == AssemblyShadowErrorCode.Success,
                     "Stable source-specific baseline candidate registration");
                Need(AssemblyShadowRuntime.BeginTransaction(
                         "R03IRG-" + request.runId, request.baselineId,
                         new[] { "Methods" }, 2) == AssemblyShadowErrorCode.Success,
                     "Fresh independent captured-generic transaction");
                Need(AssemblyShadowRuntime.ReserveMetadataBudget(
                         new[] { dll.LongLength }, 2) == AssemblyShadowErrorCode.Success,
                     "Actual IL2CPP metadata budget");
                Need(AssemblyShadowRuntime.StageAssembly(dll, null) ==
                     AssemblyShadowErrorCode.Success, "Stage real Methods candidate");
                Need(AssemblyShadowRuntime.ValidateTransaction() ==
                     AssemblyShadowErrorCode.Success,
                     "No baseline first-use before Shadow publication");
                int commit = (int)AssemblyShadowRuntime.CommitTransaction();
                AssemblyShadowState state;
                Need(AssemblyShadowRuntime.GetState(out state) ==
                     AssemblyShadowErrorCode.Success &&
                     commit == (int)AssemblyShadowErrorCode.Success &&
                     (int)state == 6,
                     "Real baseline-to-shadow committed world");
                // A2: The native probe acquires raw physical Methods TypeDef
                // handles *after* the successful Commit. It invokes the
                // production physical captured generic guard on a genuine
                // inflated MethodInfo; it must record error15/state9.
                Need(R03_IRG_Probe() == 1,
                     "Native actual physical captured generic guard");
                // A second actual runtime method-entry attempt must be blocked
                // without incrementing the prewarmed stable AOT counter.
                Need(R03_IRG_AttemptRuntimeInvoke() == 1,
                     "Real postterminal AOT method body remains denied");
                Need(R03_IRG_Seal() == 1,
                     "Native bounded source/PID/first-recovery observation");
                Need(R03_IRB1_Seal(15, 1) == 1,
                     "Actual originating Guard15 B1 record preserved after Runtime::Invoke");
                R03_IR_Exit(0);
            }
            catch (Exception)
            {
                // Failed or incomplete original native file is never converted
                // into a synthetic PASS. No exception ToString or managed
                // terminal JSON/file IO is attempted after the VM was poisoned.
                R03_IR_Exit(2);
            }
        }

        private static string Argument(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == key) return args[i + 1];
            return null;
        }

        private static string Hash(byte[] bytes)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes))
                       .Replace("-", "").ToLowerInvariant();
        }

        private static void Need(bool value, string message)
        {
            if (!value) throw new InvalidOperationException(message);
        }
    }
}
