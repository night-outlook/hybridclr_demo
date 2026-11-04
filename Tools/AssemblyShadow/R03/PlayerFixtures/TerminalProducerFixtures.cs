using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Loader;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using dnlib.DotNet.Writer;
using AssemblyShadow.R03.Fixtures;
using HybridCLR.Editor.AssemblyShadow;
using DMethodAttributes = dnlib.DotNet.MethodAttributes;
using DMethodImplAttributes = dnlib.DotNet.MethodImplAttributes;
using DTypeAttributes = dnlib.DotNet.TypeAttributes;
using DFieldAttributes = dnlib.DotNet.FieldAttributes;

// Additive host fixture preparation. No Unity/native execution or state write.
internal static class TerminalProducerFixtures
{
    internal const string Sentinel = "R03IR.InitializerFailure.AfterPublication.V1";
    private static readonly string[] Kinds = { "captured-generic", "initializer-failure", "initializer-control" };

    internal static int Write(string directory)
    {
        string root = Path.GetFullPath(directory);
        Need(!File.Exists(root) && !Directory.Exists(root), "Unused terminal fixture directory required.");
        Directory.CreateDirectory(root);
        byte[] baseline;
        using (var module = ModuleDefMD.Load(EvolutionFixtureCorpus.Build("Methods")))
            baseline = Serialize(module, "baseline");
        Put(root, "baseline/Methods.dll", baseline);
        var rows = new List<object>();
        foreach (string kind in Kinds)
        {
            byte[] bytes = Build(kind);
            var admission = NativeLayoutAdmissionValidator.Analyze(baseline, bytes);
            admission.RequireEditorAdmission();
            Need(!admission.pureInterpreterExpansionEnabled && !admission.nativeProofExecuted,
                "Metadata admission cannot claim native proof.");
            VerifyIl(bytes, kind);
            string relative = kind + "/Methods.dll";
            Put(root, relative, bytes);
            using (var parsed = ModuleDefMD.Load(bytes))
                rows.Add(new { path = relative, kind, sha256 = ShadowHash.Bytes(bytes), size = bytes.Length,
                    mvid = parsed.Mvid.ToString(), hasModuleInitializer = kind != "captured-generic",
                    initializerThrows = kind == "initializer-failure", emittedIlVerified = true,
                    layoutEditorAdmission = "PassedNeedsNativeProof" });
        }
        var receipt = new { schemaVersion = 1, kind = "R03IRTerminalProducerFixtures",
            result = "GeneratedAndIlVerified_NotNativeValidated", assembly = "Methods",
            baseline = new { path = "baseline/Methods.dll", sha256 = ShadowHash.Bytes(baseline), size = baseline.Length,
                authority = "NewDeterministicHostFixture_NotOriginalS" },
            instanceField = "R03.Node.stable", genericMethod = "R03.Node.GenericKeep<T>",
            preparationMethod = "R03.TerminalWitness.Prepare", expectedPreparedField = 3,
            expectedMethodReturn = 42, initializerSentinel = Sentinel, files = rows,
            capturedBaselineArgumentExecuted = false, commitInitializerExecuted = false,
            nativeObserverIntegrated = false, playerExecution = "NotRun", runtimeAcceptance = false,
            originalSFixturesModified = false, oldIrTargetModified = false };
        Json(root, "terminal-fixtures.json", receipt);
        return 0;
    }

    private static byte[] Build(string kind)
    {
        using (var module = ModuleDefMD.Load(EvolutionFixtureCorpus.Build("Methods", 42, insertVirtual: true)))
        {
            var node = module.GetTypes().Single(t => t.FullName == "R03.Node");
            var stable = node.Fields.Single(f => f.Name == "stable");
            var keep = node.Methods.Single(m => m.Name == "Keep");
            keep.Body = Increment(stable);
            var generic = new MethodDefUser("GenericKeep", MethodSig.CreateInstanceGeneric(1, module.CorLibTypes.Int32),
                DMethodImplAttributes.IL | DMethodImplAttributes.Managed, DMethodAttributes.Public | DMethodAttributes.HideBySig);
            generic.GenericParameters.Add(new GenericParamUser(0, GenericParamAttributes.NonVariant, "T"));
            generic.Body = Increment(stable);
            node.Methods.Add(generic);
            var read = new MethodDefUser("ReadStable", MethodSig.CreateInstance(module.CorLibTypes.Int32),
                DMethodImplAttributes.IL | DMethodImplAttributes.Managed, DMethodAttributes.Public | DMethodAttributes.HideBySig);
            read.Body = new CilBody();
            Emit(read.Body, OpCodes.Ldarg_0); Emit(read.Body, OpCodes.Ldfld, stable); Emit(read.Body, OpCodes.Ret);
            node.Methods.Add(read);

            var witness = new TypeDefUser("R03", "TerminalWitness", module.CorLibTypes.Object.TypeDefOrRef)
            { Attributes = DTypeAttributes.Public | DTypeAttributes.Abstract | DTypeAttributes.Sealed | DTypeAttributes.BeforeFieldInit };
            module.Types.Add(witness);
            var funcRef = new TypeRefUser(module, "System", "Func`1", module.CorLibTypes.AssemblyRef);
            var funcSig = new GenericInstSig(new ClassSig(funcRef), module.CorLibTypes.Int32);
            var funcType = new TypeSpecUser(funcSig);
            var instance = Field(witness, "Instance", new ClassSig(node));
            var cached = Field(witness, "CachedKeep", funcSig);
            var direct = Field(witness, "PreDirectReturn", module.CorLibTypes.Int32);
            var delegated = Field(witness, "PreDelegateReturn", module.CorLibTypes.Int32);
            var genericResult = Field(witness, "PreGenericReturn", module.CorLibTypes.Int32);
            var field = Field(witness, "PreField", module.CorLibTypes.Int32);
            var ready = Field(witness, "Ready", module.CorLibTypes.Int32);
            var prepare = new MethodDefUser("Prepare", MethodSig.CreateStatic(module.CorLibTypes.Void),
                DMethodImplAttributes.IL | DMethodImplAttributes.Managed,
                DMethodAttributes.Public | DMethodAttributes.Static | DMethodAttributes.HideBySig);
            prepare.Body = new CilBody();
            var il = prepare.Body;
            Emit(il, OpCodes.Newobj, node.Methods.Single(m => m.Name == ".ctor")); Emit(il, OpCodes.Stsfld, instance);
            Emit(il, OpCodes.Ldsfld, instance); Emit(il, OpCodes.Ldftn, keep);
            Emit(il, OpCodes.Newobj, new MemberRefUser(module, ".ctor", MethodSig.CreateInstance(module.CorLibTypes.Void,
                module.CorLibTypes.Object, module.CorLibTypes.IntPtr), funcType));
            Emit(il, OpCodes.Stsfld, cached);
            Emit(il, OpCodes.Ldsfld, instance); Emit(il, OpCodes.Callvirt, keep); Emit(il, OpCodes.Stsfld, direct);
            Emit(il, OpCodes.Ldsfld, cached);
            Emit(il, OpCodes.Callvirt, new MemberRefUser(module, "Invoke", MethodSig.CreateInstance(new GenericVar(0)), funcType));
            Emit(il, OpCodes.Stsfld, delegated);
            Emit(il, OpCodes.Ldsfld, instance);
            Emit(il, OpCodes.Callvirt, new MethodSpecUser(generic, new GenericInstMethodSig(module.CorLibTypes.Object)));
            Emit(il, OpCodes.Stsfld, genericResult);
            Emit(il, OpCodes.Ldsfld, instance); Emit(il, OpCodes.Call, read); Emit(il, OpCodes.Stsfld, field);
            Emit(il, OpCodes.Ldc_I4_1); Emit(il, OpCodes.Stsfld, ready); Emit(il, OpCodes.Ret);
            witness.Methods.Add(prepare);

            if (kind != "captured-generic")
            {
                var cctor = new MethodDefUser(".cctor", MethodSig.CreateStatic(module.CorLibTypes.Void),
                    DMethodImplAttributes.IL | DMethodImplAttributes.Managed,
                    DMethodAttributes.Private | DMethodAttributes.Static | DMethodAttributes.HideBySig |
                    DMethodAttributes.SpecialName | DMethodAttributes.RTSpecialName);
                cctor.Body = new CilBody();
                Emit(cctor.Body, OpCodes.Call, prepare);
                if (kind == "initializer-failure")
                {
                    var error = new TypeRefUser(module, "System", "InvalidOperationException", module.CorLibTypes.AssemblyRef);
                    Emit(cctor.Body, OpCodes.Ldstr, Sentinel);
                    Emit(cctor.Body, OpCodes.Newobj, new MemberRefUser(module, ".ctor",
                        MethodSig.CreateInstance(module.CorLibTypes.Void, module.CorLibTypes.String), error));
                    Emit(cctor.Body, OpCodes.Throw);
                }
                else Emit(cctor.Body, OpCodes.Ret);
                module.GlobalType.Methods.Add(cctor);
            }
            return Serialize(module, kind);
        }
    }

    private static CilBody Increment(FieldDef field)
    {
        var il = new CilBody();
        Emit(il, OpCodes.Ldarg_0); Emit(il, OpCodes.Dup); Emit(il, OpCodes.Ldfld, field);
        Emit(il, OpCodes.Ldc_I4_1); Emit(il, OpCodes.Add); Emit(il, OpCodes.Stfld, field);
        il.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_S, (sbyte)42)); Emit(il, OpCodes.Ret);
        return il;
    }
    private static FieldDef Field(TypeDef owner, string name, TypeSig type)
    {
        var field = new FieldDefUser(name, new FieldSig(type), DFieldAttributes.Public | DFieldAttributes.Static);
        owner.Fields.Add(field); return field;
    }
    private static void Emit(CilBody body, OpCode code) { body.Instructions.Add(Instruction.Create(code)); }
    private static void Emit(CilBody body, OpCode code, IField value) { body.Instructions.Add(Instruction.Create(code, value)); }
    private static void Emit(CilBody body, OpCode code, IMethod value) { body.Instructions.Add(Instruction.Create(code, value)); }
    private static void Emit(CilBody body, OpCode code, string value) { body.Instructions.Add(Instruction.Create(code, value)); }
    private static byte[] Serialize(ModuleDef module, string kind)
    {
        using (var hash = SHA256.Create())
            module.Mvid = new Guid(hash.ComputeHash(Encoding.UTF8.GetBytes("R03IR/TerminalProducers/v1/" + kind)).Take(16).ToArray());
        var options = new ModuleWriterOptions(module); options.PEHeadersOptions.TimeDateStamp = 0;
        using (var stream = new MemoryStream()) { module.Write(stream, options); return stream.ToArray(); }
    }

    internal static void VerifyIl(byte[] bytes, string kind)
    {
        Need(Kinds.Contains(kind), "Unknown terminal fixture kind.");
        using (var module = ModuleDefMD.Load(bytes))
        {
            var node = module.GetTypes().Single(t => t.FullName == "R03.Node");
            Need(node.Fields.Count(f => !f.IsStatic) == 1 && node.Fields.Single().Name == "stable" &&
                node.Fields.Single().IsPrivate && node.Fields.Single().FieldSig.Type.ElementType == ElementType.I4, "Existing primitive-only instance layout.");
            foreach (string name in new[] { "Keep", "GenericKeep" })
            {
                var m = node.Methods.Single(x => x.Name == name);
                var codes = m.Body.Instructions.Select(i => i.OpCode.Code).ToArray();
                Need(codes.SequenceEqual(new[] { Code.Ldarg_0, Code.Dup, Code.Ldfld, Code.Ldc_I4_1, Code.Add, Code.Stfld, Code.Ldc_I4_S, Code.Ret }), "Exact side-effecting IL: " + name);
                Need(ReferenceEquals(m.Body.Instructions[2].Operand, node.Fields.Single()) &&
                     ReferenceEquals(m.Body.Instructions[5].Operand, node.Fields.Single()) &&
                     m.Body.Instructions[6].GetLdcI4Value() == 42, "Exact increment operands.");
            }
            var generic = node.Methods.Single(m => m.Name == "GenericKeep");
            Need(generic.GenericParameters.Count == 1 && generic.MethodSig.GenParamCount == 1 && generic.MethodSig.HasThis,
                "Real generic instance method required.");
            var prepare = module.GetTypes().Single(t => t.FullName == "R03.TerminalWitness").Methods.Single(m => m.Name == "Prepare");
            Need(prepare.Body.Instructions.Count(i => i.OpCode == OpCodes.Stsfld) == 7 &&
                prepare.Body.Instructions.Any(i => i.Operand is MethodSpec && ((MethodSpec)i.Operand).Method.Name == "GenericKeep"), "Actual prepared counters and generic call.");
            Need(prepare.Body.Instructions.Where(i => i.OpCode == OpCodes.Stsfld).Select(i => ((IField)i.Operand).Name.String)
                .SequenceEqual(new[] { "Instance", "CachedKeep", "PreDirectReturn", "PreDelegateReturn", "PreGenericReturn", "PreField", "Ready" }), "Ordered observation stores.");
            var calls = prepare.Body.Instructions.Where(i => i.OpCode == OpCodes.Call || i.OpCode == OpCodes.Callvirt).Select(i => (IMethod)i.Operand).ToArray();
            Need(calls.Length == 4 && ReferenceEquals(calls[0], node.Methods.Single(m => m.Name == "Keep")) &&
                calls[1].Name == "Invoke" && calls[2] is MethodSpec && ReferenceEquals(((MethodSpec)calls[2]).Method, generic) &&
                ReferenceEquals(calls[3], node.Methods.Single(m => m.Name == "ReadStable")), "Exact direct/delegate/generic/read call sequence.");
            var cctors = module.GlobalType.Methods.Where(m => m.Name == ".cctor").ToArray();
            Need(cctors.Length == (kind == "captured-generic" ? 0 : 1), "Module initializer presence.");
            if (cctors.Length != 0)
            {
                var body = cctors[0].Body.Instructions;
                Need(body[0].OpCode == OpCodes.Call && ReferenceEquals(body[0].Operand, prepare), "Preparation before initializer outcome.");
                if (kind == "initializer-failure")
                    Need(body.Count == 4 && body[1].OpCode == OpCodes.Ldstr && (string)body[1].Operand == Sentinel &&
                        body[2].OpCode == OpCodes.Newobj && body[3].OpCode == OpCodes.Throw, "Actual sentinel throw, not a synthetic terminal state.");
                else Need(body.Count == 2 && body[1].OpCode == OpCodes.Ret, "Successful initializer control.");
            }
        }
    }

    // Executes ONLY new pure managed host fixtures in isolated load contexts.
    // .NET module initialization is not Unity Commit/HybridCLR validation.
    internal static int VerifyHost(string directory)
    {
        string root = Path.GetFullPath(directory);
        var results = new List<object>();
        foreach (string kind in Kinds)
        {
            byte[] bytes = File.ReadAllBytes(Path.Combine(root, kind, "Methods.dll"));
            Need(ShadowHash.Bytes(bytes) == ShadowHash.Bytes(Build(kind)), "Host input differs from deterministic current generator: " + kind);
            VerifyIl(bytes, kind);
            var context = new AssemblyLoadContext("R03IR-" + kind, isCollectible: true);
            try
            {
                System.Reflection.Assembly assembly;
                using (var stream = new MemoryStream(bytes)) assembly = context.LoadFromStream(stream);
                Exception observed = null;
                try { RuntimeHelpers.RunModuleConstructor(assembly.ManifestModule.ModuleHandle); }
                catch (Exception error) { observed = error; }
                if (kind == "initializer-failure")
                {
                    Need(observed != null, "Throwing module initializer unexpectedly returned.");
                    while (observed.InnerException != null) observed = observed.InnerException;
                    Need(observed is InvalidOperationException && observed.Message == Sentinel, "Exact initializer sentinel required.");
                    results.Add(new { kind, result = "ExpectedClrInitializerException", sideEffectsAfterFailureRead = false });
                    continue;
                }
                Need(observed == null, "Healthy CLR initializer must complete.");
                Type witness = assembly.GetType("R03.TerminalWitness", true);
                if (kind == "captured-generic") witness.GetMethod("Prepare").Invoke(null, null);
                foreach (string name in new[] { "PreDirectReturn", "PreDelegateReturn", "PreGenericReturn" })
                    Need((int)witness.GetField(name).GetValue(null) == 42, "Real healthy call return: " + name);
                Need((int)witness.GetField("Ready").GetValue(null) == 1 && (int)witness.GetField("PreField").GetValue(null) == 3, "Three real prepared body increments.");
                object instance = witness.GetField("Instance").GetValue(null);
                Type node = assembly.GetType("R03.Node", true);
                var stable = node.GetField("stable", BindingFlags.NonPublic | BindingFlags.Instance);
                Need((int)stable.GetValue(instance) == 3, "Actual initial object field.");
                Need((int)node.GetMethod("GenericKeep").MakeGenericMethod(typeof(int)).Invoke(instance, null) == 42, "Healthy constructed generic call.");
                Need(((Func<int>)witness.GetField("CachedKeep").GetValue(null))() == 42, "Cached delegate call.");
                Need((int)node.GetMethod("Keep").Invoke(instance, null) == 42 && (int)stable.GetValue(instance) == 6, "Three additional actual body side effects.");
                results.Add(new { kind, result = "PassedClrPositiveBodies", preparedField = 3, finalField = 6 });
            }
            finally { context.Unload(); }
        }
        var mutations = VerifyMutationControls();
        Json(root, "terminal-host.json", new { schemaVersion = 1, kind = "R03IRTerminalProducerClrHostCheck",
            result = "PassedHostBodiesOnly", results, mutations, runtime = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
            capturedBaselineArgumentExecuted = false, nativeCommitInitializerExecuted = false,
            postPoisonEntryExecuted = false, unityOrPlayerExecuted = false, runtimeAcceptance = false, R03Accepted = false });
        return 0;
    }
    private static string[] VerifyMutationControls()
    {
        var detected = new List<string>();
        Action<string, string, Action<ModuleDef>> check = (name, kind, change) =>
        {
            byte[] changed;
            using (var module = ModuleDefMD.Load(Build(kind))) { change(module); changed = Serialize(module, kind); }
            bool rejected = false;
            try { VerifyIl(changed, kind); } catch (InvalidOperationException) { rejected = true; }
            Need(rejected, "IL oracle accepted mutation: " + name);
            detected.Add(name);
        };
        Func<ModuleDef, TypeDef> node = m => m.GetTypes().Single(t => t.FullName == "R03.Node");
        check("wrong-return", "captured-generic", m => node(m).Methods.Single(x => x.Name == "Keep").Body.Instructions[6].Operand = (sbyte)43);
        check("public-instance-field", "captured-generic", m => node(m).Fields.Single().Attributes = DFieldAttributes.Public);
        check("missing-generic-parameter", "captured-generic", m => node(m).Methods.Single(x => x.Name == "GenericKeep").GenericParameters.Clear());
        check("missing-instance-write", "captured-generic", m =>
        {
            var body = node(m).Methods.Single(x => x.Name == "Keep").Body;
            body.Instructions[5] = Instruction.Create(OpCodes.Pop);
            body.Instructions.Insert(6, Instruction.Create(OpCodes.Pop));
        });
        check("wrong-positive-target", "initializer-control", m =>
        {
            var body = m.GetTypes().Single(t => t.FullName == "R03.TerminalWitness").Methods.Single().Body;
            body.Instructions.First(i => i.OpCode == OpCodes.Callvirt).Operand = node(m).Methods.Single(x => x.Name == "ReadStable");
        });
        check("wrong-sentinel", "initializer-failure", m => m.GlobalType.Methods.Single().Body.Instructions[1].Operand = "wrong");
        check("missing-initializer", "initializer-failure", m => m.GlobalType.Methods.Clear());
        check("initializer-returns", "initializer-failure", m =>
        {
            var body = m.GlobalType.Methods.Single().Body;
            while (body.Instructions.Count > 1) body.Instructions.RemoveAt(1);
            body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        });
        check("missing-positive-preparation", "initializer-failure", m => m.GlobalType.Methods.Single().Body.Instructions.RemoveAt(0));
        check("control-throws", "initializer-control", m =>
        {
            var body = m.GlobalType.Methods.Single().Body;
            body.Instructions.RemoveAt(1);
            body.Instructions.Add(Instruction.Create(OpCodes.Ldnull));
            body.Instructions.Add(Instruction.Create(OpCodes.Throw));
        });
        return detected.ToArray();
    }
    private static void Put(string root, string relative, byte[] bytes)
    {
        string path = Path.Combine(root, relative); Directory.CreateDirectory(Path.GetDirectoryName(path));
        using (var stream = new FileStream(path, FileMode.CreateNew)) stream.Write(bytes, 0, bytes.Length);
    }
    private static void Json(string root, string name, object value)
    {
        string json = JsonSerializer.Serialize(value, new JsonSerializerOptions { WriteIndented = true });
        using (var writer = new StreamWriter(new FileStream(Path.Combine(root, name), FileMode.CreateNew), new UTF8Encoding(false))) writer.Write(json + "\n");
        Console.WriteLine(json);
    }
    private static void Need(bool ok, string reason) { if (!ok) throw new InvalidOperationException(reason); }
}
