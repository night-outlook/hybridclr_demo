using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Linq;
using System.Reflection;
using HybridCLR;
using UnityEngine;

namespace AssemblyShadowDemo
{
    public static partial class M06ExecutionProbe
    {
        private static void BindResult(Result result, Input input)
        {
            result.fixtureManifestPath = input.manifestPath;
            result.fixtureManifestSha256 = HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath;
            result.playerBuildReceiptSha256 = HashFile(input.playerReceiptPath);
            result.generationProofPath = input.player.generationProofPath;
            result.generationProofSha256 = input.player.generationProofSha256;
            result.executionProofPath = input.player.executionProofPath;
            result.executionProofSha256 = input.player.executionProofSha256;
        }

        private static void CaptureTransaction(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            result.diagnosticsCode = (int)code;
            result.nativeDiagnosticsJson = json;
            RequireCode(result.diagnosticsCode, AssemblyShadowErrorCode.Success, "transaction diagnostics");
            AssemblyShadowDiagnostics diagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out diagnostics), "M06 transaction diagnostics JSON is malformed.");
            result.transactionSnapshots.Add(new TransactionSnapshot { phase = phase, rawJson = json, diagnostics = diagnostics });
            result.stateCode = diagnostics.stateCode;
            result.state = diagnostics.state;
        }

        private static void CaptureExecution(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetExecutionDiagnosticsJson(out json);
            result.executionDiagnosticsCode = (int)code;
            result.executionDiagnosticsJson = json;
            RequireCode(result.executionDiagnosticsCode, AssemblyShadowErrorCode.Success, "execution diagnostics");
            AssemblyShadowExecutionDiagnostics diagnostics;
            Require(AssemblyShadowExecutionDiagnostics.TryParse(json, out diagnostics), "M06 execution diagnostics JSON is malformed.");
            Require(diagnostics.enabled && diagnostics.droppedClassObservations == 0 && diagnostics.rejectedBaselineMethods == 0 && diagnostics.baselineClassCctorStarted == 0,
                "M06 execution lost observations or executed/initialized a replaced baseline.");
            if (result.executionSnapshots.Count > 0)
            {
                var previous = result.executionSnapshots.Last().diagnostics;
                Require(diagnostics.interpreterTransformations >= previous.interpreterTransformations && diagnostics.shadowInterpreterTransformations >= previous.shadowInterpreterTransformations,
                    "M06 transformation counters regressed.");
            }
            result.executionSnapshots.Add(new ExecutionSnapshot { phase = phase, rawJson = json, diagnostics = diagnostics });
        }

        private static ExecutionImage ExecutionImageFor(Input input, Fixture fixture, string name, bool shadow)
        {
            return input.executionProof.images.Single(image => image.identity.name == name &&
                (shadow ? image.role == "GenerationPlan" && image.planId == fixture.patchId : image.role == "LinkedPlayer"));
        }

        private static void RequireMethodProof(Input input, Fixture fixture, string name, MethodInfo actual, bool shadow)
        {
            ExecutionImage image = ExecutionImageFor(input, fixture, name, shadow);
            ExecutionMethod method = image.methods.SingleOrDefault(row => row.metadataToken == actual.MetadataToken);
            Require(method != null && method.name == actual.Name && method.declaringType.Replace('/', '+') == actual.DeclaringType.FullName &&
                method.isStatic == actual.IsStatic && method.genericArity == actual.GetGenericArguments().Length && method.hasBody &&
                method.returnType.type == actual.ReturnType.FullName && method.parameterTypes.Select(row => row.type).SequenceEqual(actual.GetParameters().Select(row => row.ParameterType.FullName)),
                "M06 actual method token/signature differs from the hash-bound physical image: " + name + "/" + actual.Name);
        }

        private static void ValidateExceptionEvidence(Input input, Fixture fixture, string name, Type type, string[] values, bool shadow)
        {
            string marker = ExpectedMarker(shadow ? fixture.patchId : "BASELINE");
            Require(ParseModuleValue(values, "filter=") == marker && ParseModuleValue(values, "finally=") == "ran" &&
                ParseModuleValue(values, "wrapped=") == "InvalidOperationException" && ParseModuleInt(values, "stack.frames=") > 0 &&
                !string.IsNullOrWhiteSpace(ParseModuleValue(values, "stack.text=")), "M06 actual exception/filter/finally stack evidence is missing.");
            MethodInfo throwing = type.GetMethod("ThrowForEvidence", BindingFlags.Public | BindingFlags.Static);
            Require(throwing != null && throwing.MetadataToken == ParseModuleInt(values, "method.token="), "M06 exception token differs from the invoked witness.");
            RequireMethodProof(input, fixture, name, throwing, shadow);
            ExecutionImage image = ExecutionImageFor(input, fixture, name, shadow);
            string[] frameKeys = values.Where(value => value.StartsWith("frame.", StringComparison.Ordinal) && value.Contains(".declaringType=")).ToArray();
            Require(frameKeys.Length == ParseModuleInt(values, "stack.frames="), "M06 stack frame inventory is incomplete.");
            bool found = false, source = false;
            foreach (string key in frameKeys)
            {
                string prefix = key.Substring(0, key.IndexOf("declaringType=", StringComparison.Ordinal));
                if (!FrameMethodAvailable(values, prefix)) continue;
                if (ParseModuleValue(values, prefix + "declaringType=") != type.FullName) continue;
                string methodName = ParseModuleValue(values, prefix + "method=");
                int token = ParseModuleInt(values, prefix + "token=");
                ExecutionMethod method = image.methods.SingleOrDefault(row => row.metadataToken == token && row.name == methodName && row.declaringType.Replace('/', '+') == type.FullName);
                Require(method != null && method.hasBody, "M06 stack frame has no byte-bound method definition.");
                found |= methodName == "ThrowNested" || methodName == "ThrowForEvidence";
                string file = ParseModuleValue(values, prefix + "file="); int line = ParseModuleInt(values, prefix + "line=");
                if (file != "absent" && line > 0)
                {
                    Require(shadow ? image.pdbAvailable && method.sequencePoints.Any(point => point.document == file && point.startLine <= line && point.endLine >= line) : true,
                        "M06 patch stack source line is not bound to its actual PDB.");
                    source = true;
                }
            }
            Require(found, "M06 stack omitted the actual throwing candidate method.");
            if (shadow)
            {
                PatchAssembly deployed = fixture.patch.closure.Single(row => row.name == name);
                Require(input.player.developmentBuild ? image.pdbAvailable && source && deployed.pdbSha256 == image.pdbSha256 : string.IsNullOrEmpty(deployed.pdb) && !source,
                    "M06 exception evidence does not match the genuine development/PDB or release/no-PDB image.");
            }
        }

        private static bool FrameMethodAvailable(string[] values, string prefix)
        {
            string available = ParseModuleValue(values, prefix + "methodAvailable=");
            Require(available == "True" || available == "False", "M06 stack frame method availability is not explicit.");
            if (available == "True") return true;
            Require(ParseModuleValue(values, prefix + "declaringType=") == "absent" && ParseModuleValue(values, prefix + "method=") == "absent" &&
                ParseModuleInt(values, prefix + "token=") == 0, "M06 unavailable stack method must not manufacture method identity.");
            return false;
        }

        private static void ValidateModuleOrder(Result result, Fixture fixture)
        {
            long previousEnd = 0;
            foreach (string name in fixture.closureLoadOrder)
            {
                var before = result.moduleObservations.Single(row => row.assemblyName == name && row.phase == "before-business");
                var after = result.moduleObservations.Single(row => row.assemblyName == name && row.phase == "after-business");
                Require(before.moduleCount == 1 && after.moduleCount == 1 && before.initializerStartTicks > 0 && before.initializerStopwatchFrequency == System.Diagnostics.Stopwatch.Frequency &&
                    before.initializerEndTicks >= before.initializerStartTicks && before.initializerStartTicks >= previousEnd && before.initializerStartTicks == after.initializerStartTicks && before.initializerEndTicks == after.initializerEndTicks,
                    "M06 module initializer did not run once in provider-first order: " + name);
                previousEnd = before.initializerEndTicks;
                if (name == Contracts) { Require(before.providerAssembly == "none" && before.providerMarker == "none" && before.providerCount == 0, "Root Contracts initializer unexpectedly has a provider."); continue; }
                string provider = name == Internal || name == ExtensibilityConsumer ? Extensibility : Contracts;
                bool replacedProvider = fixture.closureLoadOrder.Contains(provider);
                Require(before.providerAssembly == provider && before.providerCount == (replacedProvider ? 1 : 0) && before.providerMarker == ExpectedMarker(replacedProvider ? fixture.patchId : "BASELINE"),
                    "M06 initializer observed the wrong provider generation: " + name);
            }
            foreach (var stable in result.moduleObservations.Where(row => !fixture.closureLoadOrder.Contains(row.assemblyName)))
                Require(stable.moduleCount == 0, "M06 unchanged baseline unexpectedly ran a patch module initializer.");
        }

        private static void WriteEvidence(Result result)
        {
            string output = Path.GetFullPath(Argument("-shadowM06Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m06-" + result.mode + ".json")));
            string directory = Path.GetDirectoryName(output);
            Directory.CreateDirectory(directory);
            if (!string.IsNullOrEmpty(result.nativeDiagnosticsJson))
            {
                string path = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "-native-diagnostics.json");
                using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(result.nativeDiagnosticsJson);
                result.rawTransactionDiagnosticsPath = path;
                result.rawTransactionDiagnosticsSha256 = HashFile(path);
            }
            if (!string.IsNullOrEmpty(result.executionDiagnosticsJson))
            {
                string path = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "-execution-diagnostics.json");
                using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(result.executionDiagnosticsJson);
                result.rawExecutionDiagnosticsPath = path;
                result.rawExecutionDiagnosticsSha256 = HashFile(path);
            }
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(JsonUtility.ToJson(result, true));
        }

        private static string HashFile(string path)
        {
            using (var stream = File.OpenRead(path)) using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
    }
}
