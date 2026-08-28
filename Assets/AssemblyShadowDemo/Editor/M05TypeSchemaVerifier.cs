using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;

namespace AssemblyShadowDemo.Editor
{
    [Serializable] public sealed class M05MethodWitness
    {
        public string declaringType, name, signature;
        public bool hasBody;
        public int implementationFlags;
        public string[] instructions;
    }

    [Serializable] public sealed class M05TypeProof
    {
        public int schemaVersion;
        public string milestone, policy, compileSnapshotHash, linkedPlayerReceiptHash, nativeLibrarySha256, buildGuid;
        public bool developmentBuild;
        public M05TypeInventory[] assemblies;
        public M05MethodWitness[] moduleMethods;
    }

    /// <summary>Actual linked type/member evidence, independent of Editor reflection and historical Players.</summary>
    public static class M05TypeSchemaVerifier
    {
        public const string Policy = "active-type-world:1";
        public const string ProofName = "m05-type-proof.json";
        internal static readonly string[] BootstrapRoots = {
            "AssemblyShadowDemo.M05TypeProbe/Result", "AssemblyShadowDemo.M05TypeProbe/FixtureManifest",
            "AssemblyShadowDemo.M05TypeProbe/PlayerBuildReceipt", "AssemblyShadowDemo.M05TypeProbe/TypeProof",
            "AssemblyShadowDemo.M05TypeProbe/PatchManifest",
            "AssemblyShadowDemo.M05TypeProbe/BaselineManifest", "AssemblyShadowDemo.M05TypeProbe/SnapshotReceipt",
            "AssemblyShadowDemo.M05ResourceProbe/FrozenManifest",
            "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Configuration", "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Site",
        };

        public static M05TypeProof Capture(string root, AssemblySnapshotReceipt receipt, M04AssemblyIdentity[] linkedIdentities)
        {
            Require(receipt != null && receipt.kind == "PlayerBuildInputs" && receipt.sourcePins != null &&
                receipt.buildId != null && receipt.buildId.StartsWith("M05-Baseline-", StringComparison.Ordinal) &&
                receipt.snapshotHash == AssemblySnapshot.ComputeHash(receipt), "M05TypeProofSnapshot", "Verified M05 Player input snapshot required.");
            Require((receipt.playerBuildOptions & (int)BuildOptions.Development) != 0, "M05TypeProofBuild", "M05 type proof requires an actual development Player.");
            ShadowLinkedPlayerEvidence.ReadAndVerify(root, receipt);
            M04AssemblyIdentityProof.Verify(linkedIdentities, M04AssemblyIdentityProof.ReadLinked(root, receipt));
            M03DiagnosticSchemaVerifier.Verify(root, receipt);
            var input = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            var linked = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            try
            {
                foreach (string name in new[] { "AssemblyShadowDemo.Bootstrap", "HybridCLR.Runtime" })
                {
                    input.Add(name, ReadModule(root, receipt, name, false));
                    linked.Add(name, ReadModule(root, receipt, name, true));
                }
                VerifySchemas(input["AssemblyShadowDemo.Bootstrap"], linked["AssemblyShadowDemo.Bootstrap"], input, linked);
                VerifyRuntime(input["HybridCLR.Runtime"], linked["HybridCLR.Runtime"]);
                using (var core = ReadModule(root, receipt, "mscorlib", true))
                    return new M05TypeProof {
                        schemaVersion = 1, milestone = "M05", policy = Policy,
                        compileSnapshotHash = receipt.snapshotHash, linkedPlayerReceiptHash = receipt.linkedPlayerReceiptHash,
                        nativeLibrarySha256 = receipt.nativeLibrarySha256, buildGuid = receipt.buildGuid,
                        developmentBuild = (receipt.playerBuildOptions & (int)BuildOptions.Development) != 0,
                        assemblies = M05TypeInventoryProof.ReadIdentities(linkedIdentities), moduleMethods = ReadModuleMethods(core),
                    };
            }
            finally { foreach (var module in input.Values.Concat(linked.Values)) module.Dispose(); }
        }

        public static void Verify(string root, AssemblySnapshotReceipt snapshot, M05Build.M05PlayerBuildReceipt receipt, M04AssemblyIdentity[] linked)
        {
            string path = Path.GetFullPath(Path.Combine(root, ProofName));
            Require(receipt.typeProofPath == path && File.Exists(path) && ShadowHash.File(path) == receipt.typeProofSha256,
                "M05TypeProofBinding", "Type proof must be the immutable hash-bound snapshot companion.");
            var claimed = M04JsonEvidence.Read<M05TypeProof>(File.ReadAllText(path));
            var actual = Capture(root, snapshot, linked);
            Require(claimed.schemaVersion == 1 && claimed.milestone == "M05" && claimed.policy == Policy &&
                claimed.compileSnapshotHash == actual.compileSnapshotHash && claimed.linkedPlayerReceiptHash == actual.linkedPlayerReceiptHash &&
                claimed.nativeLibrarySha256 == actual.nativeLibrarySha256 && claimed.buildGuid == actual.buildGuid &&
                claimed.developmentBuild == actual.developmentBuild && actual.developmentBuild,
                "M05TypeProofBinding", "Type proof is not bound to this development Player's actual linked/native inputs.");
            M05TypeInventoryProof.Verify(claimed.assemblies, actual.assemblies);
            VerifyWitnesses(claimed.moduleMethods, actual.moduleMethods);
        }

        internal static void VerifySchemas(ModuleDef input, ModuleDef linked, IDictionary<string, ModuleDef> inputs, IDictionary<string, ModuleDef> linkedModules)
        {
            Require(input.Assembly.Name == "AssemblyShadowDemo.Bootstrap" && input.Assembly.FullName == linked.Assembly.FullName,
                "M05TypeSchemaIdentity", "M05 Bootstrap schema must retain its captured assembly identity.");
            ShadowDiagnosticSchemaProof.Verify(input, linked, BootstrapRoots, "M05Type", inputs, linkedModules, allowCoreLibraryLists: true);
            VerifyPrivateInputPreservation(input);
            // The Editor asmdef intentionally has no Bootstrap dependency. Compare the captured
            // wire DTO shape, not runtime-loaded reflection types or just a duplicated field list.
            VerifyArtifactDto(typeof(M05Build.M05FixtureManifest), input.Find("AssemblyShadowDemo.M05TypeProbe/FixtureManifest", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M05Build.M05PlayerBuildReceipt), input.Find("AssemblyShadowDemo.M05TypeProbe/PlayerBuildReceipt", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M05TypeProof), input.Find("AssemblyShadowDemo.M05TypeProbe/TypeProof", false), new HashSet<string>());
            foreach (string name in new[] { "AssemblyShadowDemo.M05TypeProbe", "AssemblyShadowDemo.M05ResourceProbe", "AssemblyShadowDemo.M04OrdinaryAssemblyProbe" })
            // Iterator/async bodies live in compiler-generated nested types. They are part
            // of the exact probe, not an exemption from explicit JSON-input admission.
            foreach (var type in input.GetTypes().Where(type => type.FullName == name || type.FullName.StartsWith(name + "/", StringComparison.Ordinal)))
            foreach (var method in type.Methods.Where(method => method.HasBody))
            foreach (var instruction in method.Body.Instructions)
            {
                var call = instruction.Operand as MethodSpec;
                if (call == null || call.Name != "FromJson" || call.DeclaringType.FullName != "UnityEngine.JsonUtility") continue;
                Require(call.GenericInstMethodSig.GenericArguments.Count == 1 && BootstrapRoots.Contains(call.GenericInstMethodSig.GenericArguments[0].FullName),
                    "M05TypeSchemaRoot", "Every JSON-deserialized input must have an explicit captured schema root.");
            }
        }

        private static void VerifyPrivateInputPreservation(ModuleDef input)
        {
            // Preserve annotations are a source/prelink obligation. The linker may consume
            // the annotation itself; actual postlink fields/types are checked above instead.
            var pending = new Queue<TypeDef>(new[] { "PatchManifest", "BaselineManifest", "SnapshotReceipt" }
                .Select(name => input.Find("AssemblyShadowDemo.M05TypeProbe/" + name, false)));
            var visited = new HashSet<string>(StringComparer.Ordinal);
            while (pending.Count != 0)
            {
                var type = pending.Dequeue();
                Require(type != null && type.IsSerializable && TrustedPreserve(type.CustomAttributes, input),
                    "M05InputPreservation", "Private JSON input DTO must explicitly preserve its captured type.");
                if (!visited.Add(type.FullName)) continue;
                foreach (var field in type.Fields.Where(field => field.IsPublic && !field.IsStatic))
                {
                    Require(TrustedPreserve(field.CustomAttributes, input), "M05InputPreservation",
                        "Private JSON input fields require explicit trusted Preserve annotations, including zero/false defaults: " + field.FullName);
                    TypeSig element = field.FieldType;
                    while (element is SZArraySig) element = element.Next;
                    if (element.IsPrimitive || element.ElementType == ElementType.String) continue;
                    Require(element.DefinitionAssembly != null && element.DefinitionAssembly.FullName == input.Assembly.FullName,
                        "M05InputPreservation", "Private JSON input DTO child must be captured in Bootstrap: " + field.FullName);
                    pending.Enqueue(input.Find(element.FullName, false));
                }
            }
        }

        private static bool TrustedPreserve(IEnumerable<CustomAttribute> attributes, ModuleDef input)
        {
            var matches = attributes.Where(attribute => attribute.AttributeType.FullName == "UnityEngine.Scripting.PreserveAttribute").ToArray();
            if (matches.Length != 1) return false;
            IAssembly owner = matches[0].AttributeType.DefinitionAssembly;
            return owner != null && owner.Name == "UnityEngine.CoreModule" && input.GetAssemblyRefs().Any(reference => reference.FullName == owner.FullName);
        }

        private static void VerifyArtifactDto(System.Type expected, TypeDef actual, HashSet<string> visited)
        {
            Require(actual != null, "M05ArtifactSchema", "Missing runtime artifact DTO for " + expected.FullName);
            if (!visited.Add(expected.FullName + "|" + actual.FullName)) return;
            var expectedFields = expected.GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
            var fields = actual.Fields.Where(field => field.IsPublic && !field.IsStatic && !field.IsNotSerialized).ToArray();
            Require(fields.Length == expectedFields.Length, "M05ArtifactSchema", "Editor/runtime artifact field count differs: " + actual.FullName);
            foreach (var expectedField in expectedFields)
            {
                var matches = fields.Where(field => field.Name == expectedField.Name).ToArray();
                Require(matches.Length == 1, "M05ArtifactSchema", "Editor/runtime artifact field differs: " + expectedField.Name);
                System.Type type = expectedField.FieldType; TypeSig signature = matches[0].FieldType;
                while (type.IsArray)
                {
                    Require(signature is SZArraySig, "M05ArtifactSchema", "Artifact array shape differs: " + expectedField.Name);
                    type = type.GetElementType(); signature = signature.Next;
                }
                if (type.IsPrimitive || type == typeof(string))
                    Require(type.FullName == signature.FullName, "M05ArtifactSchema", "Artifact primitive type differs: " + expectedField.Name);
                else
                {
                    Require(signature.DefinitionAssembly != null && signature.DefinitionAssembly.FullName == actual.Module.Assembly.FullName,
                        "M05ArtifactSchema", "Artifact DTO must be captured in Bootstrap: " + expectedField.Name);
                    VerifyArtifactDto(type, actual.Module.Find(signature.FullName, false), visited);
                }
            }
        }

        internal static void VerifyRuntime(ModuleDef input, ModuleDef linked)
        {
            Require(input.Assembly.Name == "HybridCLR.Runtime" && input.Assembly.FullName == linked.Assembly.FullName,
                "M05TypeSchemaIdentity", "Runtime schema requires the captured HybridCLR.Runtime identity.");
            const string diagnostic = "HybridCLR.AssemblyShadowTypeResolutionInfo";
            ShadowDiagnosticSchemaProof.Verify(input, linked, new[] { diagnostic }, "M05Type");
            var fields = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (string name in new[] { "schemaVersion", "executionModeCode" }) fields.Add(name, "System.Int32");
            foreach (string name in new[] { "logicalAssembly", "executionMode", "physicalImageKind", "typeKey", "inputTypePointer", "activeTypePointer", "baselineTypePointer" }) fields.Add(name, "System.String");
            foreach (string name in new[] { "isActive", "pointerDetailsAvailable", "baselinePointerAvailable", "containsShadowTypes" }) fields.Add(name, "System.Boolean");
            foreach (string name in new[] { "definitionCacheHits", "definitionCacheMisses", "compositeRebuilds", "allocationRemaps", "guardFailures" }) fields.Add(name, "System.UInt64");
            foreach (var module in new[] { input, linked })
            {
                var type = module.Find(diagnostic, false);
                var actual = type.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray();
                Require(actual.Length == 18 && actual.All(field => fields.ContainsKey(field.Name.String) && fields[field.Name.String] == field.FieldType.FullName),
                    "M05TypeSchemaFields", "Type-resolution diagnostics must have exactly the declared 18 typed fields, including ulong counters.");
                var api = module.Find("HybridCLR.AssemblyShadowRuntime", false);
                Require(api != null, "M05TypeApi", "Missing native transaction API.");
                string[] signatures = {
                    "ConfigureCandidates(System.String,System.String[],System.String[])", "BeginTransaction(System.String,System.String,System.String[],System.Int32)",
                    "StageAssembly(System.Byte[],System.Byte[])", "ValidateTransaction()", "CommitTransaction()", "AbortTransaction()",
                    "GetState(HybridCLR.AssemblyShadowState&)", "GetAssemblyExecutionMode(System.String,HybridCLR.AssemblyExecutionMode&)",
                    "GetDiagnosticsJson(System.String&)", "GetTypeResolutionInfo(System.Type,System.String&)",
                };
                foreach (string signature in signatures)
                {
                    var methods = api.Methods.Where(method => method.FullName == "HybridCLR.AssemblyShadowErrorCode HybridCLR.AssemblyShadowRuntime::" + signature).ToArray();
                    Require(methods.Length == 1 && methods[0].IsPublic && methods[0].IsStatic && methods[0].IsInternalCall && !methods[0].HasBody,
                        "M05TypeApi", "Exact native API missing or not InternalCall: " + signature);
                }
                var query = api.Methods.Single(method => method.Name == "GetTypeResolutionInfo");
                Require(query.ParamDefs.Any(parameter => parameter.Sequence == 2 && parameter.IsOut), "M05TypeApi", "Diagnostic JSON argument must remain out string.");
            }
        }

        internal static M05MethodWitness[] ReadModuleMethods(ModuleDef core)
        {
            Require(core != null && core.Assembly != null && core.Assembly.Name == "mscorlib", "M05ModuleMethods", "Pinned linked CoreLib is required.");
            string[] signatures = {
                "System.Type System.Reflection.RuntimeModule::GetType(System.String,System.Boolean,System.Boolean)",
                "System.Type[] System.Reflection.RuntimeModule::GetTypes()",
                "System.Reflection.Assembly System.Reflection.RuntimeModule::get_Assembly()",
                "System.Reflection.Module System.Reflection.RuntimeAssembly::GetManifestModuleInternal()",
                "System.Type System.Reflection.Assembly::InternalGetType(System.Reflection.Module,System.String,System.Boolean,System.Boolean)",
                "System.Type[] System.Reflection.RuntimeModule::InternalGetTypes(System.IntPtr)",
            };
            var methods = new List<MethodDef>();
            foreach (string signature in signatures)
            {
                var matches = core.GetTypes().SelectMany(type => type.Methods).Where(method => method.FullName == signature).ToArray();
                Require(matches.Length == 1, "M05ModuleMethods", "Required linked Module call-chain method is stripped or changed: " + signature);
                methods.Add(matches[0]);
            }
            for (int i = 0; i < methods.Count; ++i)
                Require(i < 3 ? methods[i].HasBody && !methods[i].IsInternalCall && methods[i].IsVirtual : methods[i].IsInternalCall && !methods[i].HasBody,
                    "M05ModuleMethods", "Module wrapper/native implementation flags changed: " + methods[i].FullName);
            Require(!methods[3].IsStatic && !methods[4].IsStatic && methods[5].IsStatic, "M05ModuleMethods", "Native Module entrypoint static/instance contract changed.");
            Require(Calls(methods[0], methods[4]) && Calls(methods[1], methods[5]), "M05ModuleMethods", "Module wrappers do not call their actual native entrypoints.");
            Require(methods[2].Body.Instructions.Any(instruction => instruction.OpCode == OpCodes.Ldfld && instruction.Operand is IField &&
                ((IField)instruction.Operand).FullName == "System.Reflection.Assembly System.Reflection.RuntimeModule::assembly"),
                "M05ModuleMethods", "RuntimeModule.Assembly no longer reads its actual assembly field.");
            return methods.Select(method => new M05MethodWitness {
                declaringType = method.DeclaringType.FullName, name = method.Name.String, signature = method.FullName,
                hasBody = method.HasBody, implementationFlags = (int)method.ImplAttributes,
                instructions = method.HasBody ? method.Body.Instructions.Select((instruction, index) =>
                    index.ToString("D4", CultureInfo.InvariantCulture) + ":" + instruction.OpCode.Name + Operand(method, instruction.Operand)).ToArray() : new string[0],
            }).ToArray();
        }

        private static bool Calls(MethodDef caller, MethodDef target)
        {
            return caller.Body.Instructions.Any(instruction => (instruction.OpCode == OpCodes.Call || instruction.OpCode == OpCodes.Callvirt) &&
                instruction.Operand is IMethod && ((IMethod)instruction.Operand).FullName == target.FullName &&
                ((IMethod)instruction.Operand).DeclaringType.DefinitionAssembly.FullName == target.Module.Assembly.FullName);
        }

        private static string Operand(MethodDef method, object operand)
        {
            if (operand == null) return "";
            if (operand is Instruction) return " ->" + method.Body.Instructions.IndexOf((Instruction)operand).ToString(CultureInfo.InvariantCulture);
            if (operand is IList<Instruction>) return " ->[" + string.Join(",", ((IList<Instruction>)operand).Select(item => method.Body.Instructions.IndexOf(item))) + "]";
            if (operand is IMethod) return " method:" + ((IMethod)operand).FullName + " | " + ((IMethod)operand).DeclaringType.DefinitionAssembly.FullName;
            if (operand is IField) return " field:" + ((IField)operand).FullName + " | " + ((IField)operand).DeclaringType.DefinitionAssembly.FullName;
            if (operand is ITypeDefOrRef) return " type:" + ((ITypeDefOrRef)operand).AssemblyQualifiedName;
            if (operand is string) return " utf8:" + Convert.ToBase64String(Encoding.UTF8.GetBytes((string)operand));
            if (operand is Local) return " local:" + ((Local)operand).Index + ":" + ((Local)operand).Type.FullName;
            if (operand is Parameter) return " arg:" + ((Parameter)operand).Index + ":" + ((Parameter)operand).Type.FullName;
            if (operand is IFormattable) return " " + ((IFormattable)operand).ToString(null, CultureInfo.InvariantCulture);
            throw new ShadowBuildException("M05ModuleMethods", "Unsupported normalized IL operand: " + operand.GetType().FullName);
        }

        internal static void VerifyWitnesses(M05MethodWitness[] claimed, M05MethodWitness[] actual)
        {
            Require(claimed != null && actual != null && claimed.Length == actual.Length, "M05ModuleWitness", "Module witness count differs.");
            for (int index = 0; index < actual.Length; ++index)
            {
                var a = claimed[index]; var b = actual[index];
                Require(a != null && a.declaringType == b.declaringType && a.name == b.name && a.signature == b.signature &&
                    a.hasBody == b.hasBody && a.implementationFlags == b.implementationFlags && a.instructions != null && a.instructions.SequenceEqual(b.instructions),
                    "M05ModuleWitness", "Module witness does not replay from actual linked IL: " + index);
            }
        }

        private static ModuleDefMD ReadModule(string root, AssemblySnapshotReceipt receipt, string name, bool linked)
        {
            var files = linked ? receipt.linkedPlayerReceipt.assemblies.Select(file => new { file.name, file.path, file.sha256 }) :
                receipt.assemblies.Select(file => new { file.name, file.path, file.sha256 });
            var matches = files.Where(file => AssemblyIdentityUtil.CanonicalName(file.name) == AssemblyIdentityUtil.CanonicalName(name)).ToArray();
            Require(matches.Length == 1, "M05TypeSchemaMissing", "Exactly one captured module required: " + name);
            string path = ShadowHash.SafeChild(root, (linked ? ShadowLinkedPlayerEvidence.DirectoryName + "/" : "") + matches[0].path);
            byte[] bytes = File.ReadAllBytes(path);
            Require(ShadowHash.Bytes(bytes) == matches[0].sha256, "M05TypeSchemaBytes", "Captured module changed: " + path);
            var module = ModuleDefMD.Load(bytes);
            if (module.Assembly != null && module.Assembly.Name == name) return module;
            module.Dispose(); throw new ShadowBuildException("M05TypeSchemaIdentity", "Captured module identity differs: " + name);
        }

        private static void Require(bool value, string code, string message) { ShadowHash.Require(value, code, message); }
    }
}
