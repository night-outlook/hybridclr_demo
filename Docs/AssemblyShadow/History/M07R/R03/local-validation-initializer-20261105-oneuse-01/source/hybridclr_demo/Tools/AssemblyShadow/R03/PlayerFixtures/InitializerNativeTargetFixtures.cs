using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using dnlib.DotNet.Writer;
using HybridCLR.Editor.AssemblyShadow;
using DMethodAttributes = dnlib.DotNet.MethodAttributes;
using DMethodImplAttributes = dnlib.DotNet.MethodImplAttributes;

// Additive, opt-in fixture mode; the original CLR-only three producers, the
// original fifteen S fixtures and K's immutable binary inputs are untouched.
internal static class InitializerNativeTargetFixtures
{
    private const string Export = "R03_IRW_OnPrepared";
    private const string Sentinel = "R03IR.InitializerFailure.AfterPublication.V1";
    private static readonly string[] Kinds = { "initializer-control", "initializer-failure" };

    internal static int Write(string directory)
    {
        string root = Path.GetFullPath(directory);
        Need(!File.Exists(root) && !Directory.Exists(root), "Unused native initializer fixture directory required");
        Directory.CreateDirectory(root);
        string pristine = Path.Combine(root, "clr-inputs");
        TerminalProducerFixtures.Write(pristine);
        byte[] baseline = File.ReadAllBytes(Path.Combine(pristine, "baseline", "Methods.dll"));
        var rows = new List<object>();
        foreach (string kind in Kinds)
        {
            byte[] original = File.ReadAllBytes(Path.Combine(pristine, kind, "Methods.dll"));
            byte[] target = AddCallback(original, kind);
            Need(!original.SequenceEqual(target), "Native initializer must differ from original CLR fixture");
            Verify(target, kind);
            var admission = NativeLayoutAdmissionValidator.Analyze(baseline, target);
            admission.RequireEditorAdmission();
            Need(!admission.pureInterpreterExpansionEnabled && !admission.nativeProofExecuted,
                "Editor metadata admission is not physical Player proof");
            string relative = "native/" + kind + "/Methods.dll";
            string file = Path.Combine(root, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(file));
            using (var stream = new FileStream(file, FileMode.CreateNew))
                stream.Write(target, 0, target.Length);
            using (var decoded = ModuleDefMD.Load(target))
                rows.Add(new { path = relative, kind, size = target.Length, sha256 = Hash(target),
                    mvid = decoded.Mvid.ToString(), originalClrSha256 = Hash(original),
                    expectedNativeCallback = Export, expectedPreparedField = 3,
                    callbackBeforeInitializerOutcome = true, observedInUnity = false,
                    layoutEditorAdmission = "PassedNeedsNativeProof" });
        }
        var record = new { schemaVersion = 1, kind = "R03IRInitializerNativeTargetFixturesV1",
            result = "GeneratedAndIlVerified_NotNativeValidated", assembly = "Methods",
            inputBaselineSha256 = Hash(baseline), targets = rows, expectsNativeProbe = Export,
            originalSInputReplaced = false, existingClrFixtureRegeneratedAsAuthority = false,
            originalFifteenModified = false, originalKRawModified = false,
            runtimeAcceptance = false, R03Accepted = false, H2Passed = false };
        string reportPath = Path.Combine(root, "initializer-native-targets.json");
        using (var writer = new StreamWriter(new FileStream(reportPath, FileMode.CreateNew),
            new UTF8Encoding(false)))
            writer.Write(JsonSerializer.Serialize(record, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        Console.WriteLine(JsonSerializer.Serialize(record));
        return 0;
    }

    private static byte[] AddCallback(byte[] original, string kind)
    {
        Need(Kinds.Contains(kind), "Unsupported initializer kind");
        using (var module = ModuleDefMD.Load(original))
        {
            var witness = module.GetTypes().Single(t => t.FullName == "R03.TerminalWitness");
            var prepare = witness.Methods.Single(m => m.Name == "Prepare");
            var il = prepare.Body.Instructions;
            Need(il.Count > 2 && il[il.Count - 1].OpCode == OpCodes.Ret &&
                il[il.Count - 2].OpCode == OpCodes.Stsfld &&
                ((IField)il[il.Count - 2].Operand).Name.String == "Ready",
                "Callback must follow exactly the Ready store");
            var moduleRef = new ModuleRefUser(module, "__Internal");
            var callback = new MethodDefUser("RecordPreparedInNative",
                MethodSig.CreateStatic(module.CorLibTypes.Int32),
                DMethodImplAttributes.PreserveSig,
                DMethodAttributes.Private | DMethodAttributes.Static | DMethodAttributes.HideBySig |
                DMethodAttributes.PinvokeImpl);
            callback.ImplMap = new ImplMapUser(moduleRef, Export,
                PInvokeAttributes.CallConvCdecl | PInvokeAttributes.NoMangle);
            witness.Methods.Add(callback);
            il.RemoveAt(il.Count - 1);
            var success = Instruction.Create(OpCodes.Ret);
            il.Add(Instruction.Create(OpCodes.Call, callback));
            il.Add(Instruction.Create(OpCodes.Ldc_I4_1));
            il.Add(Instruction.Create(OpCodes.Ceq));
            il.Add(Instruction.Create(OpCodes.Brtrue, success));
            il.Add(Instruction.Create(OpCodes.Ldstr, "R03IR.NativePreparedCallbackFailed.V1"));
            var error = new TypeRefUser(module, "System", "InvalidOperationException", module.CorLibTypes.AssemblyRef);
            il.Add(Instruction.Create(OpCodes.Newobj, (IMethod)new MemberRefUser(module, ".ctor",
                MethodSig.CreateInstance(module.CorLibTypes.Void, module.CorLibTypes.String), error)));
            il.Add(Instruction.Create(OpCodes.Throw));
            il.Add(success);
            using (var digest = SHA256.Create())
                module.Mvid = new Guid(digest.ComputeHash(Encoding.UTF8.GetBytes(
                    "R03IR/InitializerNative/v1/" + kind)).Take(16).ToArray());
            var options = new ModuleWriterOptions(module);
            options.PEHeadersOptions.TimeDateStamp = 0;
            using (var output = new MemoryStream()) { module.Write(output, options); return output.ToArray(); }
        }
    }

    internal static void Verify(byte[] bytes, string kind)
    {
        Need(Kinds.Contains(kind), "Only native initializer target modes accepted");
        using (var module = ModuleDefMD.Load(bytes))
        {
            var witness = module.GetTypes().Single(t => t.FullName == "R03.TerminalWitness");
            var callback = witness.Methods.Single(m => m.Name == "RecordPreparedInNative");
            Need(callback.IsPinvokeImpl && callback.IsStatic && callback.HasImplMap &&
                callback.ImplMap.Name.String == Export && callback.ImplMap.Module.Name.String == "__Internal" &&
                (callback.ImplMap.Attributes & PInvokeAttributes.CallConvMask) == PInvokeAttributes.CallConvCdecl &&
                callback.MethodSig.Params.Count == 0 && callback.MethodSig.RetType.ElementType == ElementType.I4,
                "Exact __Internal Cdecl no-arg native preparedness callback");
            var prepare = witness.Methods.Single(m => m.Name == "Prepare");
            var il = prepare.Body.Instructions;
            int readyIndex = il.ToList().FindIndex(i => i.OpCode == OpCodes.Stsfld &&
                ((IField)i.Operand).Name.String == "Ready");
            Need(readyIndex > 0 && readyIndex + 9 == il.Count,
                "Exactly one verified callback segment after Ready");
            Need(il[readyIndex + 1].OpCode == OpCodes.Call &&
                 ReferenceEquals(il[readyIndex + 1].Operand, callback) &&
                 il[readyIndex + 2].OpCode == OpCodes.Ldc_I4_1 &&
                 il[readyIndex + 3].OpCode == OpCodes.Ceq &&
                 il[readyIndex + 4].OpCode == OpCodes.Brtrue &&
                 il[readyIndex + 5].OpCode == OpCodes.Ldstr &&
                 (string)il[readyIndex + 5].Operand == "R03IR.NativePreparedCallbackFailed.V1" &&
                 il[readyIndex + 6].OpCode == OpCodes.Newobj &&
                 il[readyIndex + 7].OpCode == OpCodes.Throw &&
                 il[readyIndex + 8].OpCode == OpCodes.Ret &&
                 ReferenceEquals(il[readyIndex + 4].Operand, il[readyIndex + 8]),
                 "Exact fail-closed callback before initializer outcome");
            Need(prepare.Body.Instructions.Count(i => i.OpCode == OpCodes.Stsfld) == 7,
                "Exactly seven original preparation stores remain");
            var cctor = module.GlobalType.Methods.Single(m => m.Name == ".cctor");
            var instructions = cctor.Body.Instructions;
            Need(instructions[0].OpCode == OpCodes.Call &&
                 ReferenceEquals(instructions[0].Operand, prepare), "Real initializer calls preparation");
            Need(kind != "initializer-failure" ||
                 (instructions.Count == 4 && instructions[1].OpCode == OpCodes.Ldstr &&
                  (string)instructions[1].Operand == Sentinel &&
                  instructions[3].OpCode == OpCodes.Throw),
                 "Actual original initializer sentinel after callback");
            Need(kind != "initializer-control" ||
                 (instructions.Count == 2 && instructions[1].OpCode == OpCodes.Ret),
                 "Control initializer returns only after callback");
        }
    }

    private static string Hash(byte[] bytes)
    {
        using (var digest = SHA256.Create())
            return Convert.ToHexString(digest.ComputeHash(bytes)).ToLowerInvariant();
    }
    private static void Need(bool ok, string why)
    {
        if (!ok) throw new InvalidOperationException(why);
    }
}
