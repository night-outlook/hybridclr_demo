using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// Optional source-bound supplementary observations AFTER the original R00
    /// evidence/measurement is written. Uses the already exercised M06 witness after recording;
    /// never changes the original benchmark schema, result, or expectations.
    /// </summary>
    [Preserve]
    public static class R03CompletionExecution
    {
        [Serializable, Preserve] private sealed class Request
        {
            public int schemaVersion, repetition;
            public string kind, runId, mode, output, r00Result;
            public string[] phases;
        }
        [Serializable, Preserve] private sealed class Observation
        {
            public string phase;
            public int repetition;
            public string[] values;
        }
        [Serializable, Preserve] private sealed class Report
        {
            public int schemaVersion = 1, processId;
            public string kind = "R03ExecutionSupplement", runId, mode, result = "Observed", error = "";
            public string requestSha256, r00Sha256, buildGuid, typeName, diagnostics, diagnosticsCode;
            public string startedUtc, endedUtc;
            public bool il2cpp, featureEnabled, transactionCommitted, R03Accepted, H2Passed;
            public List<Observation> observations = new List<Observation>();
        }
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Install()
        {
            if (M07Probe.Argument("-shadowR03ExecutionRequest", "").Length != 0)
                Application.wantsToQuit += OnQuit;
        }
        private static bool OnQuit()
        {
            Application.wantsToQuit -= OnQuit;
            try
            {
                string originalPath = M07Probe.Argument("-shadowR00Result", "");
                M07Probe.Require(Path.IsPathRooted(originalPath) && File.Exists(originalPath), "Original R00 evidence must exist before supplementary work.");
                var original = JsonUtility.FromJson<M07R00PerformanceProbe.Result>(File.ReadAllText(originalPath));
                M07Probe.Require(original != null && original.result == "Passed", "No supplementary work after an unsuccessful original R00 result.");
                // Exactly the witness already exercised by original R00; never
                // load another assembly or invoke a baseline concrete handle.
                Type type = Type.GetType("AssemblyA.Implementation.Internal.M06ExecutionWitness, AssemblyA.Implementation.Internal", true);
                MethodInfo run = type.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
                Run(run, original);
            }
            catch (Exception error) { UnityEngine.Debug.LogException(error); }
            // Never suppress/delay original shutdown or rewrite its exit/result.
            // Missing/Failed supplementary evidence fails the external contract.
            return true;
        }
        private static void Run(MethodInfo run, M07R00PerformanceProbe.Result original)
        {
            string requestPath = M07Probe.Argument("-shadowR03ExecutionRequest", "");
            if (requestPath.Length == 0) return;
            M07Probe.Require(Path.IsPathRooted(requestPath) && File.Exists(requestPath), "Source-bound supplement request required.");
            var request = JsonUtility.FromJson<Request>(File.ReadAllText(requestPath));
            M07Probe.Require(request != null && request.schemaVersion == 1 && request.kind == "R03ExecutionSupplement" &&
                request.mode == original.mode && request.repetition >= 0 && request.repetition < 3 &&
                request.runId != null && request.runId.Length == 32 &&
                request.phases.SequenceEqual(new[] { "statics", "delegates", "exceptions" }), "Invalid supplementary scope.");
            M07Probe.Require(Path.IsPathRooted(request.output) && !File.Exists(request.output) &&
                Path.GetDirectoryName(request.output) == Path.GetDirectoryName(requestPath) &&
                Path.GetFullPath(request.r00Result) == Path.GetFullPath(M07Probe.Argument("-shadowR00Result", "")), "Supplement evidence path mismatch.");
            M07Probe.Require(run != null && run.Name == "Run" && run.DeclaringType != null &&
                run.DeclaringType.FullName == "AssemblyA.Implementation.Internal.M06ExecutionWitness", "Use the actual previously exercised witness method.");
            var report = new Report { runId = request.runId, mode = request.mode, processId = original.processId,
                buildGuid = original.buildGuid, il2cpp = original.il2cpp, featureEnabled = original.featureEnabled,
                transactionCommitted = original.transactionCommitted, typeName = run.DeclaringType.FullName,
                requestSha256 = M07Probe.HashFile(requestPath), r00Sha256 = M07Probe.HashFile(request.r00Result),
                startedUtc = DateTime.UtcNow.ToString("O") };
            try
            {
                string raw;
                report.diagnosticsCode = AssemblyShadowRuntime.GetTypeResolutionInfo(run.DeclaringType, out raw).ToString();
                report.diagnostics = raw;
                foreach (string phase in request.phases)
                    for (int repetition = 0; repetition < 2; ++repetition)
                        report.observations.Add(new Observation { phase = phase, repetition = repetition,
                            values = (string[])run.Invoke(null, new object[] { phase }) });
            }
            catch (Exception error) { report.result = "Failed"; report.error = error.ToString(); }
            report.endedUtc = DateTime.UtcNow.ToString("O");
            M07Probe.Require(report.r00Sha256 == M07Probe.HashFile(request.r00Result) && report.requestSha256 == M07Probe.HashFile(requestPath),
                "Original result/request changed during supplementary observation.");
            using (var file = new FileStream(request.output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(file, new System.Text.UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(report, true));
            // Evidence written is not a claim of semantic acceptance. The Python
            // verifier checks the real selected DLL/PDB and original M06 rules.
            M07Probe.Require(report.result == "Observed", "Supplement failed: " + report.error);
        }
    }
}
