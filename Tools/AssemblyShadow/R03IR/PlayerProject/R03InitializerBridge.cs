// R03 initializer-only bridge augmentation. Not a production bridge generator.
// Used solely by the verified, fresh isolated R03 build after normal
// PrebuildCommand.GenerateAll(). No assembly role or hot-update setting changes.
// Actual dnlib Methods.dll ABI and distinct control/failure source hashes/MVIDs
// are reauthenticated before changing the freshly generated file.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadow.R03.Editor
{
    internal static class R03InitializerBridge
    {
        internal const string ImportModule = "__InternalDynamic";
        internal const string NativeEntry = "R03_IRW_OnPrepared";
        internal const string NativeSignature = "Bi4";
        internal const string Contract = "R03IR.Managed2Native.Cdecl.Int32NoArgs.V1";
        private const string TableName =
            "const Managed2NativeFunctionPointerCallData hybridclr::interpreter::g_managed2NativeFunctionPointerCallStub[]";

        // This is the exact Cdecl int32() ABI emitted by the pinned HybridCLR
        // Generator's GenerateManaged2NativeFunctionPointerMethod for "Bi4".
        // The source MethodBridge.cpp is normal prebuild output; only this
        // fixed, source-derived test signature is added at a strict sentinel.
        private const string Wrapper =
            "\n// R03 initializer source-bound Bi4 bridge (test-only)\n" +
            "static void __M2NF_Bi4(Il2CppMethodPointer methodPointer, uint16_t* argVarIndexs, StackObject* localVarBase, void* ret)\n" +
            "{\n" +
            "    (void)argVarIndexs; (void)localVarBase;\n" +
            "    typedef int32_t (CDECL *NativeMethod)();\n" +
            "    *(int32_t*)ret = ((NativeMethod)(methodPointer))();\n" +
            "}\n\n";

        internal sealed class Result
        {
            public string result;
            public string signature;
            public string importModule;
            public string nativeEntry;
            public string controlSha256;
            public string controlMvid;
            public string failureSha256;
            public string failureMvid;
            public string generatedSourceBeforeSha256;
            public string generatedSourceAfterSha256;
            public bool ordinaryHotUpdateAnalyzerUnchanged;
            public bool actualNativePlayerLinked;
            public bool runtimeAcceptance;
        }

        private static void Need(bool ok, string why)
        {
            if (!ok) throw new InvalidOperationException("R03 initializer bridge: " + why);
        }

        private static void VerifyTarget(string path, string sha, string mvid)
        {
            Need(!string.IsNullOrEmpty(path) && Path.IsPathRooted(path) &&
                 Path.GetFullPath(path) == path && File.Exists(path) &&
                 !string.IsNullOrEmpty(sha) && sha.Length == 64 &&
                 ShadowHash.File(path) == sha &&
                 !string.IsNullOrEmpty(mvid), "Exact existing source target identity");
            using (var module = ModuleDefMD.Load(File.ReadAllBytes(path)))
            {
                Need(module.Assembly != null && module.Assembly.Name.String == "Methods" &&
                     string.Equals(module.Mvid.ToString(), mvid, StringComparison.OrdinalIgnoreCase),
                     "Exact Methods assembly MVID");
                var witness = module.GetTypes().Single(t => t.FullName == "R03.TerminalWitness");
                var imports = module.GetTypes().SelectMany(t => t.Methods)
                    .Where(m => m.IsPinvokeImpl).ToArray();
                Need(imports.Length == 1 && imports[0].DeclaringType == witness,
                     "One native-only interpreted callback import");
                var callback = imports[0];
                Need(callback.Name.String == "RecordPreparedInNative" &&
                     callback.HasImplMap && callback.ImplMap.Name.String == NativeEntry &&
                     callback.ImplMap.Module.Name.String == ImportModule &&
                     callback.ImplMap.Module.Name.String != "__Internal" &&
                     (callback.ImplMap.Attributes & PInvokeAttributes.CallConvMask) ==
                         PInvokeAttributes.CallConvCdecl &&
                     (callback.ImplMap.Attributes & PInvokeAttributes.NoMangle) != 0 &&
                     callback.IsStatic && callback.MethodSig != null &&
                     callback.MethodSig.Params.Count == 0 &&
                     callback.MethodSig.RetType.ElementType == ElementType.I4,
                     "Exactly source-derived Cdecl Int32() PInvoke ABI for Bi4");
            }
        }

        internal static Result Generate(BuildConfig config, string installedNative)
        {
            Need(config != null && config.initializerBridgeContract == Contract,
                 "Explicit initializer-only code generation contract");
            Need(config.featureEnabled && config.diagnosticsLevel == 2 &&
                 config.cppConfiguration == "Release",
                 "One ON/diagnostics2/Release test-only build");
            Need(!string.IsNullOrEmpty(installedNative) &&
                 Path.IsPathRooted(installedNative), "Pinned installed native root");
            VerifyTarget(config.initializerBridgeControlPath,
                         config.initializerBridgeControlSha256,
                         config.initializerBridgeControlMvid);
            VerifyTarget(config.initializerBridgeFailurePath,
                         config.initializerBridgeFailureSha256,
                         config.initializerBridgeFailureMvid);
            Need(config.initializerBridgeControlPath != config.initializerBridgeFailurePath &&
                 config.initializerBridgeControlSha256 != config.initializerBridgeFailureSha256 &&
                 config.initializerBridgeControlMvid != config.initializerBridgeFailureMvid,
                 "Two physically distinct source-bound V2 target DLLs");
            string file = Path.Combine(installedNative, "hybridclr", "generated", "MethodBridge.cpp");
            Need(File.Exists(file), "Normal Prebuild-generated MethodBridge.cpp required");
            string before = File.ReadAllText(file, Encoding.UTF8);
            Need(before.IndexOf(TableName, StringComparison.Ordinal) >= 0 &&
                 before.IndexOf(TableName, StringComparison.Ordinal) ==
                     before.LastIndexOf(TableName, StringComparison.Ordinal) &&
                 before.IndexOf("__M2NF_Bi4", StringComparison.Ordinal) < 0 &&
                 before.IndexOf("\"Bi4\"", StringComparison.Ordinal) < 0,
                 "Unmodified normal generator table, no duplicate Bi4 code");

            // This isolated suite has no hot-update analyzer assemblies.
            // It must NOT overwrite, hide, or discard an unrelated generated
            // native-call signature: require the exact null-only table.
            var match = Regex.Match(before,
                @"const Managed2NativeFunctionPointerCallData hybridclr::interpreter::g_managed2NativeFunctionPointerCallStub\[\]\s*\{\s*\{nullptr,\s*nullptr\},\s*\};",
                RegexOptions.CultureInvariant);
            Need(match.Success && match.Value.IndexOf(TableName, StringComparison.Ordinal) == 0 &&
                 Regex.Matches(before, Regex.Escape(TableName)).Count == 1,
                 "Exactly one null-only generated native bridge table");
            var raw = match.Value;
            int row = raw.IndexOf("{nullptr", StringComparison.Ordinal);
            Need(row >= 0, "Explicit null-only native table sentinel");
            string modifiedTable = raw.Insert(row, "{\"Bi4\", __M2NF_Bi4},\n    ");
            string after = before.Substring(0, match.Index) + Wrapper + modifiedTable +
                           before.Substring(match.Index + match.Length);
            Need(after.Contains("\"Bi4\", __M2NF_Bi4") &&
                 Regex.Matches(after, "\"Bi4\"").Count == 1 &&
                 Regex.Matches(after, "__M2NF_Bi4").Count == 2 &&
                 after.IndexOf("typedef int32_t (CDECL *NativeMethod)();",
                               StringComparison.Ordinal) >= 0 &&
                 after != before,
                 "Exact generated Cdecl bridge wrapper and only one linked table row");
            string beforeSha = ShadowHash.File(file);
            File.WriteAllText(file, after, new UTF8Encoding(false));
            string afterSha = ShadowHash.File(file);
            Need(beforeSha != afterSha && File.ReadAllText(file, Encoding.UTF8) == after,
                 "Deterministic verified generated bridge write");
            return new Result {
                result = "SourceBoundInitializerBi4Generated_NotPlayerValidated",
                signature = NativeSignature, importModule = ImportModule,
                nativeEntry = NativeEntry,
                controlSha256 = config.initializerBridgeControlSha256,
                controlMvid = config.initializerBridgeControlMvid,
                failureSha256 = config.initializerBridgeFailureSha256,
                failureMvid = config.initializerBridgeFailureMvid,
                generatedSourceBeforeSha256 = beforeSha,
                generatedSourceAfterSha256 = afterSha,
                ordinaryHotUpdateAnalyzerUnchanged = true,
                actualNativePlayerLinked = false,
                runtimeAcceptance = false,
            };
        }
    }
}
