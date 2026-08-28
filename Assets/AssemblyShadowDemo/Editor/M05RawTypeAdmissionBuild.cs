using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Serialization.Json;
using System.Text;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.AssemblyShadow.CodeGen;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build.Player;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    // Declaration generation only. The actual Player/patch snapshot must still
    // reproduce these exact method fingerprints and pass role/linked checks.
    public static class M05RawTypeAdmissionBuild
    {
        private const string Consumer = "AssemblyShadowDemo.Bootstrap";
        private const string HelperType = "AssemblyShadowDemo.M05BoundTypeQueries";
        private static readonly string[] Methods = { "GetTypes", "GetDefinedTypes", "GetExportedTypes", "GetModuleTypes", "GetModuleType" };
        private static readonly Dictionary<string, string> Owners = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            { "AssemblyA.Contracts", "AssemblyA.Contracts.AssemblyAContractVersion" },
            { "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Extensibility.VersionedComponentBase" },
            { "AssemblyA.Implementation.Internal", "AssemblyA.Implementation.Internal.InternalEntry" },
            { "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.Consumers.ContractsConsumer" },
            { "AssemblyShadowDemo.ExtensibilityConsumer", "AssemblyShadowDemo.Consumers.DerivedExternalComponent" },
        };

        public static void Generate()
        {
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            ShadowHash.Require(target == BuildTarget.StandaloneOSX, "RawAdmissionCompilerTarget", "M05 requires the pinned StandaloneOSX Player compiler.");
            string directory = Path.GetFullPath("_temp/AssemblyShadow/M05RawAdmissionCompiler-" + Guid.NewGuid().ToString("N"));
            string compilerOutput = Path.Combine(directory, "CompilerOutput");
            Directory.CreateDirectory(compilerOutput);
            var compilation = PlayerBuildInterface.CompilePlayerScripts(new ScriptCompilationSettings
            {
                group = BuildPipeline.GetBuildTargetGroup(target), target = target,
                options = ScriptCompilationOptions.DevelopmentBuild,
                extraScriptingDefines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]),
            }, compilerOutput);
            ShadowHash.Require(compilation.assemblies != null && compilation.assemblies.Count > 0, "RawAdmissionCompileFailed", directory);
            var emitted = compilation.assemblies.Select(path => File.Exists(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(compilerOutput, path))).ToArray();
            // Bee owns direct compiler outputs and may remove them on the next
            // compilation. Keep the exact returned DLL set outside that directory.
            string preserved = Path.Combine(directory, "Assemblies");
            var paths = CaptureCompilerOutputs(compilerOutput, preserved, emitted);
            var byName = paths.ToDictionary(Path.GetFileNameWithoutExtension, StringComparer.Ordinal);
            var modules = new Dictionary<string, ModuleDefMD>(StringComparer.Ordinal);
            try
            {
                foreach (string name in Owners.Keys.Concat(new[] { Consumer }))
                {
                    string path;
                    ShadowHash.Require(byName.TryGetValue(name, out path) && File.Exists(path), "RawAdmissionCompilerInputMissing", name);
                    modules.Add(name, ModuleDefMD.Load(File.ReadAllBytes(path)));
                }
                string corlib = modules[Consumer].CorLibTypes.AssemblyRef.Name.String;
                string[] framework = AssemblySnapshot.TargetCompilerReferences()
                    .Where(path => Path.GetFileNameWithoutExtension(path) == corlib).Distinct(StringComparer.Ordinal).ToArray();
                ShadowHash.Require(framework.Length == 1, "RawAdmissionCompilerFrameworkAmbiguous",
                    "Expected one actual target-compiler reference for " + corlib + ", found " + framework.Length + ".");
                modules.Add(corlib, ModuleDefMD.Load(File.ReadAllBytes(framework[0])));
                var configuration = Derive(modules);
                string destination = Path.GetFullPath(RawTypeAdmissionConfiguration.ProjectRelativePath);
                if (File.Exists(destination))
                {
                    var existing = RawTypeAdmissionConfiguration.Parse(File.ReadAllBytes(destination));
                    ShadowHash.Require(existing.ComputeHash() == configuration.ComputeHash(), "RawAdmissionDeclarationChanged",
                        "The existing declaration is immutable for this baseline; inspect the changed compiler bytes before declaring a new one.");
                }
                else
                {
                    byte[] bytes = Serialize(configuration);
                    ShadowHash.Require(RawTypeAdmissionConfiguration.Parse(bytes).ComputeHash() == configuration.ComputeHash(),
                        "RawAdmissionDeclarationSerialization", "Serialized configuration changed its exact declaration.");
                    using (var output = new FileStream(destination, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                        output.Write(bytes, 0, bytes.Length);
                }
                Debug.Log("[AssemblyShadow M05] Declared 25 raw-query sites from " + preserved + "; configuration SHA-256 " +
                    ShadowHash.File(destination) + ". Actual Player/patch byte and role verification remains required.");
            }
            finally { foreach (var module in modules.Values) module.Dispose(); }
        }

        internal static string[] CaptureCompilerOutputs(string compilerOutput, string destination, string[] emitted)
        {
            string sourceRoot = Path.GetFullPath(compilerOutput).TrimEnd(Path.DirectorySeparatorChar);
            string prefix = sourceRoot + Path.DirectorySeparatorChar;
            string capturedRoot = Path.GetFullPath(destination).TrimEnd(Path.DirectorySeparatorChar);
            ShadowHash.Require(capturedRoot != sourceRoot && !capturedRoot.StartsWith(prefix, StringComparison.Ordinal),
                "RawAdmissionCompilerCaptureLifetime", "Captured inputs must be outside the producer-owned compiler directory.");
            ShadowHash.Require(!Directory.Exists(capturedRoot) && !File.Exists(capturedRoot), "RawAdmissionCompilerCaptureExists", capturedRoot);
            ShadowHash.Require(emitted != null && emitted.Length > 0, "RawAdmissionCompilerInputMissing", compilerOutput);
            var paths = emitted.Select(Path.GetFullPath).ToArray();
            ShadowHash.Require(paths.All(path => path.StartsWith(prefix, StringComparison.Ordinal) && File.Exists(path) &&
                string.Equals(Path.GetExtension(path), ".dll", StringComparison.OrdinalIgnoreCase)), "RawAdmissionCompilerOutputEscaped", compilerOutput);
            ShadowHash.Require(paths.Select(Path.GetFileName).Distinct(StringComparer.OrdinalIgnoreCase).Count() == paths.Length,
                "RawAdmissionCompilerCaptureNames", "Returned compiler DLL names must be unique.");
            Directory.CreateDirectory(capturedRoot);
            return paths.Select(path =>
            {
                string captured = Path.Combine(capturedRoot, Path.GetFileName(path));
                CopyCompilerFile(path, captured);
                string pdb = Path.ChangeExtension(path, ".pdb");
                if (File.Exists(pdb)) CopyCompilerFile(pdb, Path.ChangeExtension(captured, ".pdb"));
                return captured;
            }).ToArray();
        }

        private static void CopyCompilerFile(string source, string destination)
        {
            string expected = ShadowHash.File(source);
            File.Copy(source, destination, false);
            ShadowHash.Require(ShadowHash.File(destination) == expected && ShadowHash.File(source) == expected,
                "RawAdmissionCompilerCaptureBytes", source);
        }

        internal static RawTypeAdmissionConfiguration Derive(IReadOnlyDictionary<string, ModuleDefMD> modules)
        {
            ModuleDefMD consumer;
            ShadowHash.Require(modules.TryGetValue(Consumer, out consumer) && consumer.Assembly != null && consumer.Assembly.Name.String == Consumer,
                "RawAdmissionCompilerInputMissing", Consumer);
            var types = consumer.GetTypes().Where(type => type.FullName == HelperType).ToArray();
            ShadowHash.Require(types.Length == 1, "RawAdmissionCompilerHelperMissing", HelperType);
            var sites = new List<RawTypeAdmissionSite>();
            foreach (string name in Methods)
            {
                var methods = types[0].Methods.Where(method => method.Name.String == name).ToArray();
                ShadowHash.Require(methods.Length == 1 && methods[0].HasBody, "RawAdmissionCompilerHelperMissing", name);
                var method = methods[0];
                string methodHash = ReflectionBindingFingerprint.Compute(method);
                var providers = new HashSet<string>(StringComparer.Ordinal);
                for (int index = 0; index < method.Body.Instructions.Count; index++)
                {
                    var operation = method.Body.Instructions[index].Operand as IMethod;
                    string kind = operation == null ? null : RawTypeAdmissionConfiguration.KindOf(operation.FullName);
                    if (kind == null) continue;
                    string providerName = ReceiverLiteral(method, index);
                    ModuleDefMD provider;
                    ShadowHash.Require(Owners.ContainsKey(providerName) && providers.Add(providerName) && modules.TryGetValue(providerName, out provider) &&
                        provider.Assembly != null && provider.Assembly.Name.String == providerName,
                        "RawAdmissionCompilerProviderMissing", providerName);
                    sites.Add(new RawTypeAdmissionSite
                    {
                        id = "m05-" + name + "-" + providerName,
                        consumerAssembly = Consumer, declaringType = HelperType,
                        methodSignature = ReflectionBindingFingerprint.MethodSignature(method), methodHash = methodHash,
                        operationIndex = index, operationSignature = operation.FullName,
                        providerAssemblyIdentity = modules[providerName].Assembly.FullName,
                        typeName = kind == "Module.GetType" ? Owners[providerName] : "",
                        throwOnError = kind == "Module.GetType", ignoreCase = false,
                        reason = "M05 observes this exact literal-bound raw type query; no generated result or runtime-commit claim.",
                    });
                }
                ShadowHash.Require(providers.SetEquals(Owners.Keys), "RawAdmissionCompilerSiteInventory",
                    name + " must contain exactly one raw query for each of the five candidates.");
            }
            var configuration = new RawTypeAdmissionConfiguration { sites = sites.OrderBy(site => site.id, StringComparer.Ordinal).ToArray() };
            configuration.Validate();
            ShadowHash.Require(RawTypeAdmissionVerifier.Verify(modules, configuration).Length == 25,
                "RawAdmissionCompilerSiteInventory", "All 25 actual receiver chains must verify before declaration.");
            return configuration;
        }

        private static string ReceiverLiteral(MethodDef method, int operationIndex)
        {
            var instructions = method.Body.Instructions;
            for (int index = operationIndex - 1; index > 0; index--)
            {
                var call = instructions[index].Operand as IMethod;
                if (instructions[index].OpCode.Code != Code.Call || call == null ||
                    call.FullName != "System.Reflection.Assembly System.Reflection.Assembly::Load(System.String)") continue;
                int literal = index - 1;
                while (literal >= 0 && instructions[literal].OpCode.Code == Code.Nop) literal--;
                ShadowHash.Require(literal >= 0 && instructions[literal].OpCode.Code == Code.Ldstr,
                    "RawAdmissionCompilerReceiver", method.FullName);
                return (string)instructions[literal].Operand;
            }
            throw new InvalidOperationException("Raw query has no literal Assembly.Load receiver: " + method.FullName);
        }

        private static byte[] Serialize(RawTypeAdmissionConfiguration configuration)
        {
            using (var stream = new MemoryStream())
            {
                using (var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, new UTF8Encoding(false), false, true))
                    new DataContractJsonSerializer(typeof(RawTypeAdmissionConfiguration)).WriteObject(writer, configuration);
                return stream.ToArray();
            }
        }
    }
}
