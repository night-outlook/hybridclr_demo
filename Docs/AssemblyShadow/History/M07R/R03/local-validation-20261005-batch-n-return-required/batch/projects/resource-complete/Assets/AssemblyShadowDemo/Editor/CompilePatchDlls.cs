using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Globalization;
using System.Text;
using AssemblyShadowBaseline.Editor;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Player;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class CompilePatchDlls
    {
        public static void Build()
        {
            BuildBaselineBundles.Build();
            GeneratePatchVariant.RequireVariantSource();
            string baselineRoot = M01Paths.BaselineRoot(EditorUserBuildSettings.activeBuildTarget);
            BuildBaselineBundles.VerifyExisting(baselineRoot);
            string output = Path.GetFullPath(M01Paths.PatchDirectory);
            Directory.CreateDirectory(output);

            var settings = new ScriptCompilationSettings
            {
                group = BuildPipeline.GetBuildTargetGroup(EditorUserBuildSettings.activeBuildTarget),
                target = EditorUserBuildSettings.activeBuildTarget,
                options = EditorUserBuildSettings.development ? ScriptCompilationOptions.DevelopmentBuild : ScriptCompilationOptions.None,
                extraScriptingDefines = new[] { GeneratePatchVariant.Define },
            };
            PlayerBuildInterface.CompilePlayerScripts(settings, output);
#if UNITY_2022
            EditorUtility.ClearProgressBar();
#endif
            string compiled = FindCompiled(output, M01Paths.InternalAssemblyName + ".dll");
            string baseline = Path.Combine(baselineRoot, "AssemblySnapshot/" + M01Paths.InternalAssemblyName + ".dll");
            VerifyAbi(baseline, compiled);
            string patchDll = Path.Combine(output, M01Paths.InternalAssemblyName + ".dll");
            if (!string.Equals(Path.GetFullPath(compiled), Path.GetFullPath(patchDll), StringComparison.Ordinal))
                M01BuildSupport.CopyFile(compiled, patchDll);
            string patchPdb = Path.ChangeExtension(compiled, ".pdb");
            if (File.Exists(patchPdb) && !string.Equals(Path.GetFullPath(patchPdb), Path.GetFullPath(Path.Combine(output, M01Paths.InternalAssemblyName + ".pdb")), StringComparison.Ordinal))
                M01BuildSupport.CopyFile(patchPdb, Path.Combine(output, M01Paths.InternalAssemblyName + ".pdb"));

            string staged = Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01/P01");
            Directory.CreateDirectory(staged);
            string stagedDll = Path.Combine(staged, M01Paths.InternalAssemblyName + ".dll.bytes");
            M01BuildSupport.CopyFile(patchDll, stagedDll);
            string stagedPdb = Path.Combine(staged, M01Paths.InternalAssemblyName + ".pdb.bytes");
            string plainPdb = Path.Combine(output, M01Paths.InternalAssemblyName + ".pdb");
            bool hasPdb = File.Exists(plainPdb);
            if (hasPdb) M01BuildSupport.CopyFile(plainPdb, stagedPdb);
            var manifest = new PatchManifest
            {
                schemaVersion = 1,
                assemblyName = M01Paths.InternalAssemblyName,
                dllFile = "AssemblyA.Implementation.Internal.dll.bytes",
                pdbFile = hasPdb ? "AssemblyA.Implementation.Internal.pdb.bytes" : null,
                patchDllSha256 = M01BuildSupport.Sha256(patchDll),
                baselineMvid = M01BuildSupport.ReadMvid(baseline),
                patchMvid = M01BuildSupport.ReadMvid(patchDll),
                abiCompatible = true,
                preprocessorVariant = GeneratePatchVariant.Define,
            };
            if (manifest.baselineMvid == manifest.patchMvid)
                throw new BuildFailedException("P01 compilation did not produce a new assembly MVID.");
            File.WriteAllText(Path.Combine(staged, "patch-manifest.json"), JsonUtility.ToJson(manifest, true));
            File.WriteAllText(Path.Combine(output, "patch-manifest.json"), JsonUtility.ToJson(manifest, true));
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("[AssemblyShadow M01] Compiled patch: " + JsonUtility.ToJson(manifest));
        }

        private static string FindCompiled(string output, string filename)
        {
            string exact = Path.Combine(output, filename);
            if (File.Exists(exact)) return exact;
            string nested = Directory.GetFiles(output, filename, SearchOption.AllDirectories).FirstOrDefault();
            if (nested == null)
                throw new BuildFailedException("Patch compilation did not emit " + filename);
            return nested;
        }

        internal static void VerifyAbi(string baselinePath, string patchPath)
        {
            using (var baseline = dnlib.DotNet.ModuleDefMD.Load(baselinePath))
            using (var patch = dnlib.DotNet.ModuleDefMD.Load(patchPath))
            {
                if (baseline.Name != patch.Name || baseline.Assembly == null || patch.Assembly == null ||
                    baseline.Assembly.Name.String != M01Paths.InternalAssemblyName ||
                    patch.Assembly.Name.String != M01Paths.InternalAssemblyName)
                    throw new BuildFailedException("Patch module name differs from baseline.");
                var beforeTypes = FlattenTypes(baseline).ToDictionary(item => item.FullName, StringComparer.Ordinal);
                var afterTypes = FlattenTypes(patch).ToDictionary(item => item.FullName, StringComparer.Ordinal);
                if (!beforeTypes.Keys.OrderBy(item => item).SequenceEqual(afterTypes.Keys.OrderBy(item => item)))
                    throw new BuildFailedException("Patch type inventory differs from baseline.");
                int changedBodies = 0;
                foreach (string name in beforeTypes.Keys.OrderBy(item => item))
                {
                    var before = beforeTypes[name];
                    var after = afterTypes[name];
                    if (before == null || after == null || before.BaseType?.FullName != after.BaseType?.FullName)
                        throw new BuildFailedException("Patch ABI type/base mismatch: " + name);
                    var beforeFields = before.Fields.Select(field => field.Name + ":" + field.FieldType.FullName + ":" + field.Attributes).OrderBy(item => item).ToArray();
                    var afterFields = after.Fields.Select(field => field.Name + ":" + field.FieldType.FullName + ":" + field.Attributes).OrderBy(item => item).ToArray();
                    if (!beforeFields.SequenceEqual(afterFields))
                        throw new BuildFailedException("Patch serialized field ABI mismatch: " + name);
                    var beforeInterfaces = before.Interfaces.Select(item => item.Interface.FullName).OrderBy(item => item).ToArray();
                    var afterInterfaces = after.Interfaces.Select(item => item.Interface.FullName).OrderBy(item => item).ToArray();
                    if (!beforeInterfaces.SequenceEqual(afterInterfaces))
                        throw new BuildFailedException("Patch interface ABI mismatch: " + name);
                    var beforeMethods = before.Methods.ToDictionary(item => item.Name + ":" + MethodSignature(item), StringComparer.Ordinal);
                    var afterMethods = after.Methods.ToDictionary(item => item.Name + ":" + MethodSignature(item), StringComparer.Ordinal);
                    if (!beforeMethods.Keys.OrderBy(item => item).SequenceEqual(afterMethods.Keys.OrderBy(item => item)))
                        throw new BuildFailedException("Patch method ABI mismatch: " + name);
                    foreach (string methodName in beforeMethods.Keys)
                        changedBodies += VerifyMethodBody(beforeMethods[methodName], afterMethods[methodName], name + "." + methodName);
                }
                if (changedBodies == 0)
                    throw new BuildFailedException("P01 patch did not change any method body.");
            }
        }

        internal const string SemanticComparisonPolicy = "same-types-fields-method-signatures-and-il";

        // Stripping is allowed to change metadata identity, but must not change the managed
        // semantics consumed by the M01 shadow probe. Keep this comparison separate from the
        // P01 ABI check above: P01 permits exactly the two marker literals, while AOT stripping
        // permits no IL or ABI changes at all.
        internal static void VerifySemanticEquivalence(string baselinePath, string candidatePath)
        {
            using (var baseline = dnlib.DotNet.ModuleDefMD.Load(baselinePath))
            using (var candidate = dnlib.DotNet.ModuleDefMD.Load(candidatePath))
            {
                string before = SemanticSignature(baseline);
                string after = SemanticSignature(candidate);
                if (!string.Equals(before, after, StringComparison.Ordinal))
                {
                    string[] beforeLines = before.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
                    string[] afterLines = after.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
                    int count = Math.Min(beforeLines.Length, afterLines.Length);
                    for (int i = 0; i < count; ++i)
                    {
                        if (!string.Equals(beforeLines[i], afterLines[i], StringComparison.Ordinal))
                            throw new BuildFailedException("Stripped assembly semantic mismatch at " + candidatePath + ": " + beforeLines[i] + " != " + afterLines[i]);
                    }
                    throw new BuildFailedException("Stripped assembly semantic inventory length mismatch at " + candidatePath + ".");
                }
            }
        }

        private static string SemanticSignature(dnlib.DotNet.ModuleDef module)
        {
            var result = new StringBuilder();
            if (module.Assembly == null)
                throw new BuildFailedException("Assembly metadata is missing from " + module.Name + ".");
            result.Append("assembly|").Append(module.Assembly.Name.String).Append('|')
                .Append(module.Assembly.Attributes).Append('|')
                .Append(FormatCustomAttributes(module.Assembly.CustomAttributes)).Append('\n');
            foreach (var type in FlattenTypes(module).OrderBy(item => item.FullName, StringComparer.Ordinal))
            {
                var layout = type.ClassLayout;
                result.Append("type|").Append(type.FullName).Append('|').Append(type.Attributes).Append('|')
                    .Append(type.BaseType == null ? string.Empty : type.BaseType.FullName).Append('|')
                    .Append(layout == null ? string.Empty : layout.PackingSize.ToString(CultureInfo.InvariantCulture) + ":" + layout.ClassSize.ToString(CultureInfo.InvariantCulture)).Append('|')
                    .Append(FormatCustomAttributes(type.CustomAttributes)).Append('|');
                result.Append(string.Join(",", type.Interfaces.Select(item => item.Interface.FullName).OrderBy(item => item, StringComparer.Ordinal).ToArray()));
                result.Append('\n');
                foreach (var field in type.Fields)
                {
                    result.Append("field|").Append(field.Name).Append('|').Append(field.FieldType.FullName).Append('|')
                        .Append(field.Attributes).Append('|')
                        .Append(field.FieldOffset.HasValue ? field.FieldOffset.Value.ToString(CultureInfo.InvariantCulture) : string.Empty).Append('|')
                        .Append(field.HasConstant ? Convert.ToString(field.Constant.Value, CultureInfo.InvariantCulture) : string.Empty).Append('|')
                        .Append(FormatCustomAttributes(field.CustomAttributes)).Append('\n');
                }
                foreach (var method in type.Methods.OrderBy(item => item.Name + ":" + MethodSignature(item), StringComparer.Ordinal))
                {
                    result.Append("method|").Append(method.Name).Append('|').Append(MethodSignature(method)).Append('|')
                        .Append(FormatCustomAttributes(method.CustomAttributes)).Append('|');
                    result.Append(string.Join(",", method.ParamDefs.Select(item => item.Name + ":" + item.Attributes + ":" + FormatCustomAttributes(item.CustomAttributes)).ToArray()));
                    result.Append('\n');
                    AppendMethodBody(result, method);
                }
            }
            return result.ToString();
        }

        private static void AppendMethodBody(StringBuilder result, dnlib.DotNet.MethodDef method)
        {
            if (!method.HasBody)
            {
                result.Append("body|none\n");
                return;
            }
            var body = method.Body;
            result.Append("body|").Append(body.InitLocals).Append('|').Append(body.MaxStack.ToString(CultureInfo.InvariantCulture)).Append('|')
                .Append(body.Variables.Count).Append('|').Append(body.ExceptionHandlers.Count).Append('\n');
            foreach (var local in body.Variables)
                result.Append("local|").Append(local.Type.FullName).Append('\n');
            for (int i = 0; i < body.Instructions.Count; ++i)
            {
                var instruction = body.Instructions[i];
                result.Append("il|").Append(i.ToString(CultureInfo.InvariantCulture)).Append('|').Append(instruction.OpCode.Code).Append('|')
                    .Append(NormalizeSemanticOperand(instruction.Operand, body)).Append('\n');
            }
            foreach (var handler in body.ExceptionHandlers)
            {
                result.Append("eh|").Append(handler.HandlerType).Append('|')
                    .Append(InstructionIndex(body, handler.TryStart)).Append('|').Append(InstructionIndex(body, handler.TryEnd)).Append('|')
                    .Append(InstructionIndex(body, handler.HandlerStart)).Append('|').Append(InstructionIndex(body, handler.HandlerEnd)).Append('|')
                    .Append(InstructionIndex(body, handler.FilterStart)).Append('|')
                    .Append(handler.CatchType == null ? string.Empty : handler.CatchType.FullName).Append('\n');
            }
        }

        private static string NormalizeSemanticOperand(object operand, dnlib.DotNet.Emit.CilBody body)
        {
            if (operand == null) return string.Empty;
            var instruction = operand as dnlib.DotNet.Emit.Instruction;
            if (instruction != null) return "instruction:" + InstructionIndex(body, instruction);
            var instructions = operand as dnlib.DotNet.Emit.Instruction[];
            if (instructions != null) return string.Join(",", instructions.Select(item => InstructionIndex(body, item).ToString(CultureInfo.InvariantCulture)).ToArray());
            return NormalizeOperand(operand);
        }

        private static int InstructionIndex(dnlib.DotNet.Emit.CilBody body, dnlib.DotNet.Emit.Instruction instruction)
        {
            return instruction == null ? -1 : body.Instructions.IndexOf(instruction);
        }

        private static string FormatCustomAttributes(IEnumerable<dnlib.DotNet.CustomAttribute> attributes)
        {
            if (attributes == null) return string.Empty;
            return string.Join(";", attributes.Select(FormatCustomAttribute).OrderBy(item => item, StringComparer.Ordinal).ToArray());
        }

        private static string FormatCustomAttribute(dnlib.DotNet.CustomAttribute attribute)
        {
            var result = new StringBuilder(attribute.AttributeType.FullName);
            result.Append('(').Append(string.Join(",", attribute.ConstructorArguments.Select(FormatAttributeArgument).ToArray())).Append(')');
            foreach (var named in attribute.NamedArguments.OrderBy(item => item.Name.String, StringComparer.Ordinal))
                result.Append('|').Append(named.Name.String).Append('=').Append(FormatAttributeArgument(named.Argument));
            return result.ToString();
        }

        private static string FormatAttributeArgument(dnlib.DotNet.CAArgument argument)
        {
            var values = argument.Value as IList<dnlib.DotNet.CAArgument>;
            if (values != null)
                return "[" + string.Join(",", values.Select(FormatAttributeArgument).ToArray()) + "]";
            return (argument.Type == null ? string.Empty : argument.Type.FullName) + ":" + Convert.ToString(argument.Value, CultureInfo.InvariantCulture);
        }

        private static IEnumerable<dnlib.DotNet.TypeDef> FlattenTypes(dnlib.DotNet.ModuleDef module)
        {
            foreach (var type in module.Types)
            {
                if (!type.IsGlobalModuleType)
                {
                    yield return type;
                    foreach (var nested in FlattenNested(type)) yield return nested;
                }
            }
        }

        private static IEnumerable<dnlib.DotNet.TypeDef> FlattenNested(dnlib.DotNet.TypeDef type)
        {
            foreach (var nested in type.NestedTypes)
            {
                yield return nested;
                foreach (var child in FlattenNested(nested)) yield return child;
            }
        }

        private static string MethodSignature(dnlib.DotNet.MethodDef method)
        {
            return (method.MethodSig == null ? string.Empty : method.MethodSig.ToString()) + ":" + method.Attributes + ":" + method.ImplAttributes;
        }

        private static int VerifyMethodBody(dnlib.DotNet.MethodDef baseline, dnlib.DotNet.MethodDef patch, string methodName)
        {
            if (baseline.HasBody != patch.HasBody) throw new BuildFailedException("Patch method body presence mismatch: " + methodName);
            if (!baseline.HasBody) return 0;
            if (baseline.Body.InitLocals != patch.Body.InitLocals || baseline.Body.Variables.Count != patch.Body.Variables.Count || baseline.Body.ExceptionHandlers.Count != patch.Body.ExceptionHandlers.Count)
                throw new BuildFailedException("Patch method body ABI mismatch: " + methodName);
            for (int i = 0; i < baseline.Body.Variables.Count; ++i)
                if (baseline.Body.Variables[i].Type.FullName != patch.Body.Variables[i].Type.FullName)
                    throw new BuildFailedException("Patch local ABI mismatch: " + methodName);
            if (baseline.Body.Instructions.Count != patch.Body.Instructions.Count)
                throw new BuildFailedException("Patch IL instruction count mismatch: " + methodName);
            int changed = 0;
            for (int i = 0; i < baseline.Body.Instructions.Count; ++i)
            {
                var before = baseline.Body.Instructions[i];
                var after = patch.Body.Instructions[i];
                if (before.OpCode.Code != after.OpCode.Code)
                    throw new BuildFailedException("Patch IL opcode mismatch: " + methodName + " instruction " + i);
                string beforeOperand = NormalizeOperand(before.Operand);
                string afterOperand = NormalizeOperand(after.Operand);
                if (beforeOperand == afterOperand) continue;
                if (beforeOperand == "BASELINE-INTERNAL" && afterOperand == "PATCH-P01-INTERNAL") { changed++; continue; }
                throw new BuildFailedException("Patch IL operand mismatch: " + methodName + " instruction " + i + " (" + beforeOperand + " vs " + afterOperand + ").");
            }
            return changed;
        }

        private static string NormalizeOperand(object operand)
        {
            if (operand == null) return string.Empty;
            var type = operand as dnlib.DotNet.ITypeDefOrRef;
            if (type != null) return "type:" + type.FullName;
            var method = operand as dnlib.DotNet.IMethod;
            if (method != null) return "method:" + method.FullName;
            var field = operand as dnlib.DotNet.IField;
            if (field != null) return "field:" + field.FullName;
            var instruction = operand as dnlib.DotNet.Emit.Instruction;
            if (instruction != null) return "instruction:" + instruction.Offset.ToString(CultureInfo.InvariantCulture);
            var instructions = operand as dnlib.DotNet.Emit.Instruction[];
            if (instructions != null) return string.Join(",", instructions.Select(item => item.Offset.ToString(CultureInfo.InvariantCulture)).ToArray());
            return Convert.ToString(operand, CultureInfo.InvariantCulture);
        }

        [Serializable]
        private sealed class PatchManifest
        {
            public int schemaVersion;
            public string assemblyName;
            public string dllFile;
            public string pdbFile;
            public string patchDllSha256;
            public string baselineMvid;
            public string patchMvid;
            public bool abiCompatible;
            public string preprocessorVariant;
        }
    }
}
