using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    // Opt-in sidecar after the complete, unmodified R00 observation. Never
    // participates in activation and never changes an R00 result into a pass.
    [Preserve]
    public static class R02PlayerProbe
    {
        public const string OutputVariable = "ASSEMBLY_SHADOW_R02_OUTPUT";
        public const string RunIdVariable = "ASSEMBLY_SHADOW_R02_RUN_ID";
        public const string RoleVariable = "ASSEMBLY_SHADOW_R02_ROLE";
        public static bool Requested { get { return !string.IsNullOrEmpty(Environment.GetEnvironmentVariable(OutputVariable)); } }
        private static readonly string[] Operations = { "allocation", "closed-generic", "array", "boxing", "virtual", "interface", "delegate", "added-type" };

        public static int Run(string baseline, string runtimeAbi)
        {
            string output = Environment.GetEnvironmentVariable(OutputVariable);
            if (string.IsNullOrEmpty(output)) return 0;
            var result = new Result {
                schemaVersion = 1, kind = "R02PlayerWitness", protocol = "R02LocalBatch-v1", result = "Failed", error = "",
                runId = Environment.GetEnvironmentVariable(RunIdVariable) ?? "", role = Environment.GetEnvironmentVariable(RoleVariable) ?? "",
                mode = M07Probe.Argument("-shadowR00Mode", ""), baselineBuildId = baseline, runtimeAbiHash = runtimeAbi,
                buildGuid = Application.buildGUID, unityVersion = Application.unityVersion, platform = Application.platform.ToString(),
                processId = Process.GetCurrentProcess().Id, startedUtcTicks = DateTime.UtcNow.Ticks,
                rows = new List<Row>(40), memoryMeasurement = R00ProcessMemory.Measurement,
                memorySemantics = R00ProcessMemory.MeasurementSemantics, runtimeAcceptance = false
            };
            try
            {
                Require(M07Probe.R00IsIl2CppPlayer(), "R02 requires an IL2CPP Player.");
                Require(Path.IsPathRooted(output) && Directory.Exists(Path.GetDirectoryName(output)) && !File.Exists(output), "R02 output must be an unused absolute file in an existing directory.");
                Guid nonce; Require(Guid.TryParseExact(result.runId, "N", out nonce), "R02 run ID must be a 32-digit GUID.");
                Require(result.role == "candidate" || result.role == "control", "Unknown R02 role.");
                Require(result.mode == "R00-OFF-NoPatch" || result.mode == "R00-ON-NoPatch" || result.mode == "R00-ON-P01" || result.mode == "R00-ON-P03", "Unknown R02 mode.");
                bool patched = result.mode == "R00-ON-P01" || result.mode == "R00-ON-P03";
                int expectedMarker = result.mode == "R00-ON-P03" ? 3003 : patched ? 3001 : 3000;
                Type witness = Type.GetType("AssemblyA.Implementation.Internal.R02AllocationWitness, AssemblyA.Implementation.Internal", true);
                result.witnessType = witness.FullName;
                result.marker = (int)Method(witness, "GetMarker").Invoke(null, null);
                Require(result.marker == expectedMarker, "Wrong R02 witness execution marker.");
                string info;
                result.typeInfoCode = AssemblyShadowRuntime.GetTypeResolutionInfo(witness, out info).ToString();
                result.typeInfoJson = info ?? "";
                var run = (Func<int, int, int, long>)Delegate.CreateDelegate(typeof(Func<int, int, int, long>), Method(witness, "Run"));
                var count = (Func<int>)Delegate.CreateDelegate(typeof(Func<int>), Method(witness, "GetConstructorCount"));
                var scale = (Func<int, int, int, long>)Delegate.CreateDelegate(typeof(Func<int, int, int, long>), Method(witness, "RunScale"));
                // Prime diagnostic and result scaffolding, not witness objects.
                Capture(); Capture();
                for (int operation = 0; operation < (patched ? 8 : 7); ++operation)
                {
                    int selected = operation;
                    Measure(result, Operations[operation], "first-observed", 1, 17, count, () => run(selected, 1, 17));
                    long primed = run(selected, 100, 1017);
                    Require(primed == Expected(100, 1017, result.marker), "Priming checksum mismatch.");
                    Capture(); Capture();
                    Measure(result, Operations[operation], "warm10", 10, 2017, count, () => run(selected, 10, 2017));
                    Measure(result, Operations[operation], "warm10000", 10000, 3017, count, () => run(selected, 10000, 3017));
                }
                Require((int)Method(witness, "PrepareScale").Invoke(null, null) == 1000, "Scale preparation did not create 1000 factories.");
                result.scaleTypeHandles = (string[])Method(witness, "GetScaleTypeHandles").Invoke(null, null);
                Require(result.scaleTypeHandles.Length == 1000 && new HashSet<string>(result.scaleTypeHandles).Count == 1000,
                    "Scale types do not have 1000 distinct complete runtime handles.");
                foreach (int types in new[] { 100, 1000 })
                {
                    int selected = types;
                    Measure(result, "scale-" + types, "first-observed", types, 17, count, () => scale(selected, 1, 17));
                    Require(scale(types, 1, 1017) == Expected(types, 1017, result.marker), "Scale priming mismatch.");
                    Capture(); Capture();
                    Measure(result, "scale-" + types, "warm", types, 2017, count, () => scale(selected, 1, 2017));
                }
                RunParallel(result, run, count);
                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.error = error.ToString();
                UnityEngine.Debug.LogException(error);
            }
            result.endedUtcTicks = DateTime.UtcNow.Ticks;
            try
            {
                byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(result, true) + "\n");
                using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
            }
            catch (Exception error) { UnityEngine.Debug.LogException(error); return 2; }
            return result.result == "Passed" ? 0 : 1;
        }

        private static MethodInfo Method(Type type, string name)
        {
            MethodInfo method = type.GetMethod(name, BindingFlags.Public | BindingFlags.Static);
            Require(method != null, "Missing R02 witness method: " + name);
            return method;
        }
        private static void Require(bool condition, string message)
        { if (!condition) throw new InvalidOperationException(message); }
        public static long Expected(int count, int seed, int marker)
        { return count * (seed * 17L + marker) + 17L * count * (count - 1) / 2; }

        private static void Measure(Result result, string operation, string phase, int iterations, int seed, Func<int> count, Func<long> action)
        {
            var row = new Row { operation = operation, phase = phase, iterations = iterations, seed = seed,
                expectedChecksum = Expected(iterations, seed, result.marker), stopwatchFrequency = Stopwatch.Frequency };
            result.rows.Add(row); // Retain the partially completed row on failure.
            row.constructorsBefore = count();
            row.before = Capture();
            long start = Stopwatch.GetTimestamp();
            row.checksum = action();
            row.elapsedTicks = Stopwatch.GetTimestamp() - start;
            row.after = Capture();
            row.constructorsAfter = count();
            row.passed = row.checksum == row.expectedChecksum && row.constructorsAfter - row.constructorsBefore == iterations;
            Require(row.passed, "R02 constructor/checksum mismatch: " + operation + "/" + phase);
        }

        private static void RunParallel(Result result, Func<int, int, int, long> run, Func<int> count)
        {
            const int workers = 4, iterations = 1000, seed = 7017;
            var parallel = new ParallelRow { workerCount = workers, iterationsPerWorker = iterations, seed = seed,
                threadIds = new int[workers], checksums = new long[workers], errors = new string[workers], joined = new bool[workers] };
            result.parallel = parallel;
            var threads = new Thread[workers];
            using (var start = new ManualResetEvent(false))
            {
                for (int i = 0; i < workers; ++i)
                {
                    int slot = i;
                    threads[i] = new Thread(() => {
                        try {
                            parallel.threadIds[slot] = Environment.CurrentManagedThreadId;
                            start.WaitOne();
                            parallel.checksums[slot] = run(0, iterations, seed + slot * iterations);
                        }
                        catch (Exception error) { parallel.errors[slot] = error.ToString(); }
                    });
                    threads[i].IsBackground = true;
                }
                parallel.constructorsBefore = count(); parallel.before = Capture();
                long ticks = Stopwatch.GetTimestamp();
                foreach (Thread thread in threads) thread.Start();
                start.Set();
                for (int i = 0; i < workers; ++i) parallel.joined[i] = threads[i].Join(60000);
                parallel.elapsedTicks = Stopwatch.GetTimestamp() - ticks;
                parallel.stopwatchFrequency = Stopwatch.Frequency;
                parallel.after = Capture(); parallel.constructorsAfter = count();
                parallel.passed = parallel.constructorsAfter - parallel.constructorsBefore == workers * iterations;
                var ids = new HashSet<int>();
                for (int i = 0; i < workers; ++i)
                    parallel.passed &= parallel.joined[i] && string.IsNullOrEmpty(parallel.errors[i]) &&
                        ids.Add(parallel.threadIds[i]) && parallel.threadIds[i] > 0 &&
                        parallel.checksums[i] == Expected(iterations, seed + i * iterations, result.marker);
                Require(parallel.passed, "R02 multithreaded witness failed.");
            }
        }

        private static Snapshot Capture()
        {
            var value = new Snapshot();
            R00ProcessMemory.Sample memory = R00ProcessMemory.Capture();
            value.currentRssBytes = memory.CurrentRssBytes; value.managedBytes = memory.ManagedBytes;
            value.lifetimePeakRssBytes = memory.LifetimePeakRssBytes;
            string json;
            value.executionCode = AssemblyShadowRuntime.GetExecutionDiagnosticsJson(out json).ToString();
            value.executionJson = json ?? ""; value.utcTicks = DateTime.UtcNow.Ticks;
            return value;
        }

        [Serializable] public sealed class Snapshot
        {
            public string executionCode, executionJson;
            public long utcTicks, currentRssBytes, managedBytes, lifetimePeakRssBytes;
        }
        [Serializable] public sealed class Row
        {
            public string operation, phase;
            public int iterations, seed, constructorsBefore, constructorsAfter;
            public long checksum, expectedChecksum, elapsedTicks, stopwatchFrequency;
            public bool passed;
            public Snapshot before, after;
        }
        [Serializable] public sealed class ParallelRow
        {
            public int workerCount, iterationsPerWorker, seed, constructorsBefore, constructorsAfter;
            public int[] threadIds;
            public string[] errors;
            public bool[] joined;
            public long[] checksums;
            public long elapsedTicks, stopwatchFrequency;
            public bool passed;
            public Snapshot before, after;
        }
        [Serializable] public sealed class Result
        {
            public int schemaVersion, processId, marker;
            public string kind, protocol, result, error, runId, role, mode, baselineBuildId, runtimeAbiHash,
                buildGuid, unityVersion, platform, witnessType, typeInfoCode, typeInfoJson, memoryMeasurement, memorySemantics;
            public long startedUtcTicks, endedUtcTicks;
            public bool runtimeAcceptance;
            public string[] scaleTypeHandles;
            public List<Row> rows;
            public ParallelRow parallel;
        }
    }
}
