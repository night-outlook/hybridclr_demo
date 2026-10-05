using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
#if HOST_LAYOUT
using System.Text.Json;
#else
using Newtonsoft.Json;
#endif

// The same executable source runs against production source in .NET and against
// the complete real package compiled for pinned Unity Mono. Neither launches a
// Unity Editor/Player or turns historical inputs into a new runtime certificate.
internal static class Program
{
    [Serializable] public sealed class InputFile { public string path, sha256; public long size; }
    [Serializable] public sealed class Inputs
    {
        public string kind, basis, baselineName, targetName, runtimeFacadeSha256, compilerFacadeSha256;
        public InputFile[] linked, compiler;
        public InputFile runtimeFacade;
    }
    [Serializable] public sealed class Case { public string id, result, error; }
    [Serializable] public sealed class Inventory { public string path, sha256; public long size; }
    [Serializable] public sealed class Report
    {
        public string kind = "R03LayoutIdentityContracts", result = "Failed", basis = "ReusedAuditedLocalMLayoutInputs";
        public int schemaVersion = 1, failures;
        public bool unityEditorRun, playerRun, runtimeAcceptance, nativeProofExecuted, expansionAuthorized;
        public List<Case> cases = new List<Case>(); public Inventory[] files;
    }
    [Serializable] public sealed class Comparison
    {
        public string kind = "R03CapturedLayoutComparison", basis = "ReusedAuditedLocalMLayoutInputs";
        public NativeLayoutAdmissionReport declared, resolved;
        public NativeLayoutIdentityFile[] linkedInventory, compilerInventory;
        public NativeLayoutResolvedType[] linkedResolutions, compilerResolutions;
        public bool nativeProofExecuted, runtimeAcceptance;
    }
    static string root; static Report report;
    static void Need(bool value, string message) { if (!value) throw new InvalidOperationException(message); }
    static void Expect(string code, Action action)
    {
        try { action(); } catch (ShadowBuildException e) { Need(e.Code == code, "Expected " + code + ", observed " + e.Code); return; }
        throw new InvalidOperationException("Expected rejection: " + code);
    }
    static void Save(string relative, object value)
    {
        string path = Path.Combine(root, relative); Directory.CreateDirectory(Path.GetDirectoryName(path));
#if HOST_LAYOUT
        string json = JsonSerializer.Serialize(value, value.GetType(), new JsonSerializerOptions { WriteIndented = true, IncludeFields = true });
#else
        string json = JsonConvert.SerializeObject(value, Formatting.Indented);
#endif
        using (var f = new FileStream(path, FileMode.CreateNew)) using (var w = new StreamWriter(f, new System.Text.UTF8Encoding(false))) w.Write(json + "\n");
    }
    static void Check(string id, Action action)
    {
        try { action(); report.cases.Add(new Case { id = id, result = "Passed" }); }
        catch (Exception e) { report.failures++; report.cases.Add(new Case { id = id, result = "Failed", error = e.ToString() }); }
    }
    static ModuleDefUser Module(string name, Version version = null)
    {
        var m = new ModuleDefUser(name + ".dll", Guid.NewGuid()) { Kind = ModuleKind.Dll };
        new AssemblyDefUser(name, version ?? new Version(1, 0, 0, 0)).Modules.Add(m); return m;
    }
    static byte[] Bytes(ModuleDef m) { using (var s = new MemoryStream()) { m.Write(s); return s.ToArray(); } }
    static AssemblyRef Ref(string name, Version version = null) { return new AssemblyRefUser(name, version ?? new Version(1, 0, 0, 0), new PublicKeyToken()) { HasPublicKey = false }; }
    static TypeRef T(ModuleDef m, string scope, string name) { return new TypeRefUser(m, "Shape", name, Ref(scope)); }
    static void Field(TypeDef t, string name, TypeSig sig) { t.Fields.Add(new FieldDefUser(name, new FieldSig(sig), FieldAttributes.Private)); }
    static byte[] Provider(string assembly = "Provider", bool duplicate = false)
    {
        using (var m = Module(assembly))
        {
            foreach (string n in new[] { "Base", "Other", "I", "G`1", "Modifier" })
            {
                var t = new TypeDefUser("Shape", n, null) { Attributes = n == "I" ? TypeAttributes.Public | TypeAttributes.Interface | TypeAttributes.Abstract : TypeAttributes.Public };
                if (n == "G`1") { t.GenericParameters.Add(new GenericParamUser(0, 0, "T")); t.NestedTypes.Add(new TypeDefUser("", "Nested", null)); }
                m.Types.Add(t);
            }
            if (duplicate) m.Types.Add(new TypeDefUser("Shape", "Base", null));
            return Bytes(m);
        }
    }
    static byte[] Facade(string assembly = "Facade", string destination = "Provider", string mode = "valid")
    {
        using (var m = Module(assembly))
        {
            foreach (string n in new[] { "Base", "Other", "I", "G`1", "Modifier" })
            {
                var e = new ExportedTypeUser(m, 0, "Shape", n, TypeAttributes.Public | (mode == "not-forwarder" ? 0 : TypeAttributes.Forwarder), Ref(destination));
                m.ExportedTypes.Add(e);
                if (n == "G`1") m.ExportedTypes.Add(new ExportedTypeUser(m, 0, "", "Nested", TypeAttributes.NestedPublic, e));
                if (mode == "duplicate" && n == "Base") m.ExportedTypes.Add(new ExportedTypeUser(m, 0, "Shape", n, e.Attributes, Ref(destination)));
            }
            if (mode == "definition-and-forward") m.Types.Add(new TypeDefUser("Shape", "Base", null));
            return Bytes(m);
        }
    }
    static byte[] Consumer(string scope, string change = "")
    {
        using (var m = Module("Consumer"))
        {
            var t = new TypeDefUser("App", "Node`1", T(m, scope, change == "parent" ? "Other" : "Base")) { Attributes = TypeAttributes.Public };
            t.GenericParameters.Add(new GenericParamUser(0, 0, "T"));
            t.GenericParameters[0].GenericParamConstraints.Add(new GenericParamConstraintUser(T(m, scope, change == "constraint" ? "Base" : "I")));
            if (change != "interface") t.Interfaces.Add(new InterfaceImplUser(T(m, scope, "I")));
            Field(t, "value", new ClassSig(T(m, scope, change == "field" ? "Other" : "Base")));
            var arg = change == "generic" ? (TypeSig)m.CorLibTypes.Int64 : m.CorLibTypes.Int32;
            Field(t, "generic", new GenericInstSig(new ClassSig(T(m, scope, "G`1")), new SZArraySig(arg)));
            Field(t, "nested", new ClassSig(new TypeRefUser(m, "", "Nested", T(m, scope, "G`1"))));
            Field(t, "modified", new CModReqdSig(T(m, scope, change == "modifier" ? "Other" : "Modifier"), m.CorLibTypes.Int32));
            if (change == "offset") { t.Attributes |= TypeAttributes.ExplicitLayout; t.Fields[0].FieldOffset = 8; }
            m.Types.Add(t); return Bytes(m);
        }
    }
    static NativeLayoutAdmissionReport Compare(byte[] a, byte[] b, byte[][] before, byte[][] after)
    {
        using (var x = NativeLayoutIdentityContext.Load(before)) using (var y = NativeLayoutIdentityContext.Load(after))
            return NativeLayoutAdmissionValidator.Analyze(a, b, x, y);
    }
    static void Synthetic()
    {
        byte[] p = Provider(), f = Facade(), a = Consumer("Provider"), b = Consumer("Facade");
        foreach (var kv in new Dictionary<string, byte[]> { { "provider", p }, { "facade", f }, { "before", a }, { "after", b } })
            File.WriteAllBytes(Path.Combine(root, kv.Key + ".dll"), kv.Value);
        Check("S01-raw-scopes-remain-distinct", () => Need(!NativeLayoutAdmissionValidator.Analyze(a, b).editorAccepted, "Legacy unbound comparison cannot alias"));
        Check("S02-complete-forwarder-positive", () => { var r = Compare(a, b, new[] { p, a }, new[] { p, f, b }); Need(r.editorAccepted && !r.nativeProofExecuted && r.allocationProofStillRequired, "Nominal proof only"); });
        Check("S03-two-hop-forwarder", () => Need(Compare(a, b, new[] { p, a }, new[] { p, Facade("Facade", "Bridge"), Facade("Bridge"), b }).editorAccepted, "Transitive forwarder"));
        foreach (string mutation in new[] { "parent", "interface", "field", "generic", "constraint", "modifier", "offset" })
            Check("S04-" + mutation, () => { var changed = Consumer("Facade", mutation); Need(!Compare(a, changed, new[] { p, a }, new[] { p, f, changed }).editorAccepted, "Real shape change remains rejected"); });
        Check("S05-unrelated-same-named-types", () => { var fake = Provider("Unrelated"); var c = Consumer("Unrelated"); Need(!Compare(a, c, new[] { p, a }, new[] { fake, c }).editorAccepted, "Same names are not authority"); });
        Check("S06-missing-declared-provider", () => Expect("NativeLayoutResolutionMissingAssembly", () => Compare(a, b, new[] { p, a }, new[] { p, b })));
        Check("S07-missing-forward-destination", () => Expect("NativeLayoutResolutionMissingAssembly", () => Compare(a, b, new[] { p, a }, new[] { f, b })));
        Check("S08-cycle", () => Expect("NativeLayoutResolutionCycle", () => Compare(a, b, new[] { p, a }, new[] { b, Facade("Facade", "Bridge"), Facade("Bridge", "Facade") })));
        Check("S09-duplicate-image", () => Expect("NativeLayoutResolutionAmbiguous", () => { using (var c = NativeLayoutIdentityContext.Load(new[] { p, p })) { } }));
        Check("S10-duplicate-definition", () => Expect("NativeLayoutResolutionAmbiguous", () => { using (var c = NativeLayoutIdentityContext.Load(new[] { Provider("Provider", true) })) { } }));
        foreach (string mode in new[] { "duplicate", "definition-and-forward", "not-forwarder" })
            Check("S11-" + mode, () => Expect(mode == "not-forwarder" ? "NativeLayoutResolutionForwarder" : "NativeLayoutResolutionAmbiguous", () => { using (var c = NativeLayoutIdentityContext.Load(new[] { Facade(mode: mode) })) { } }));
        Check("S12-input-membership", () => { using (var c = NativeLayoutIdentityContext.Load(new[] { p, a })) Expect("NativeLayoutResolutionInput", () => NativeLayoutAdmissionValidator.Analyze(a, b, c, c)); });
        Check("S13-disposed-owner", () => { var c = NativeLayoutIdentityContext.Load(new[] { p, a }); c.Dispose(); Expect("NativeLayoutResolutionDisposed", () => { var x = c.Files; }); });
        Check("S14-source-clone", () => { var clone = (byte[])p.Clone(); using (var c = NativeLayoutIdentityContext.Load(new[] { clone, a })) { clone[0] ^= 255; Need(NativeLayoutAdmissionValidator.Analyze(a, a, c, c).editorAccepted, "Own copied bytes"); } });
        Check("S15-resolution-receipts-isolated", () => { using (var x = NativeLayoutIdentityContext.Load(new[] { p, a })) using (var y = NativeLayoutIdentityContext.Load(new[] { p, f, b })) { NativeLayoutAdmissionValidator.Analyze(a, b, x, y); var r = y.Resolutions; Need(r.Length >= 5 && r.Any(i => i.forwardingPath.Length == 2), "Actual forwarding records"); r[0].forwardingPath[0] = "tampered"; Need(y.Resolutions.All(i => !i.forwardingPath.Contains("tampered")), "Receipt copies"); } });
        Check("S16-empty-inventory", () => Expect("NativeLayoutResolutionInput", () => { using (var c = NativeLayoutIdentityContext.Load(new byte[0][])) { } }));
        Check("S17-no-ambient-resolution", () => { var c = Consumer("System.Private.CoreLib"); Expect("NativeLayoutResolutionMissingAssembly", () => Compare(a, c, new[] { p, a }, new[] { c })); });
        Check("S18-full-assembly-version", () => { byte[] c; using (var m = ModuleDefMD.Load(b)) { m.GetAssemblyRefs().Single(x => x.Name == "Facade").Version = new Version(9, 0, 0, 0); c = Bytes(m); } Expect("NativeLayoutResolutionMissingAssembly", () => Compare(a, c, new[] { p, a }, new[] { p, f, c })); });
    }
    static byte[] Read(InputFile file)
    { byte[] b = File.ReadAllBytes(file.path); Need(b.LongLength == file.size && ShadowHash.Bytes(b) == file.sha256, "Input hash: " + file.path); return b; }
    static void Real(Inputs input)
    {
        Need(input.kind == "R03LayoutReplayInputs" && input.basis == "ReusedAuditedLocalMLayoutInputs", "Explicit reused-input basis");
        var a = input.linked.Select(Read).ToArray(); var b = input.compiler.Select(Read).ToArray(); byte[] facade = Read(input.runtimeFacade);
        int ai = Array.FindIndex(input.linked, x => Path.GetFileName(x.path).Equals(input.baselineName, StringComparison.Ordinal));
        int bi = Array.FindIndex(input.compiler, x => Path.GetFileName(x.path).Equals(input.targetName, StringComparison.Ordinal));
        Need(ai >= 0 && bi >= 0, "Exact compared modules");
        using (var linked = NativeLayoutIdentityContext.Load(a))
        using (var compiler = NativeLayoutIdentityContext.LoadCompiler(b, linked, facade, input.runtimeFacadeSha256, input.compilerFacadeSha256))
        {
            var raw = NativeLayoutAdmissionValidator.Analyze(a[ai], b[bi]);
            Check("M01-original-scope-reproduction", () => Need(!raw.editorAccepted && raw.types.Count(t => t.reasons.Contains("ParentChanged")) == 43, "Original 43 scope differences preserved"));
            Check("M02-authenticated-layout-positive", () => {
                var mapped = NativeLayoutAdmissionValidator.Analyze(a[ai], b[bi], linked, compiler);
                Save("comparison.json", new Comparison { declared = raw, resolved = mapped, linkedInventory = linked.Files, compilerInventory = compiler.Files, linkedResolutions = linked.Resolutions, compilerResolutions = compiler.Resolutions });
                mapped.RequireEditorAdmission(); Need(!mapped.nativeProofExecuted && mapped.allocationProofStillRequired && !mapped.pureInterpreterExpansionEnabled, "No native proof or expansion");
                Need(compiler.Resolutions.Any(r => r.runtimeFacadeUsed) && compiler.Resolutions.All(r => r.forwardingPath.Length > 0), "Actual paths recorded");
            });
            Check("M03-inventory-order-independent", () => {
                using (var x = NativeLayoutIdentityContext.Load(a.Reverse())) using (var y = NativeLayoutIdentityContext.LoadCompiler(b.Reverse(), x, facade, input.runtimeFacadeSha256, input.compilerFacadeSha256))
                    Need(NativeLayoutAdmissionValidator.Analyze(a[ai], b[bi], x, y).editorAccepted, "Order cannot select a different provider");
            });
            Check("M04-wrong-facade-hash", () => Expect("NativeLayoutResolutionFacadeHash", () => { using (var c = NativeLayoutIdentityContext.LoadCompiler(b, linked, facade, new string('0', 64), input.compilerFacadeSha256)) { } }));
            Check("M05-wrong-compiler-hash", () => Expect("NativeLayoutResolutionFacadeIdentity", () => { using (var c = NativeLayoutIdentityContext.LoadCompiler(b, linked, facade, input.runtimeFacadeSha256, new string('0', 64))) { } }));
            Check("M06-definition-is-not-runtime-facade", () => {
                byte[] fake = b.Single(x => ShadowHash.Bytes(x) == input.compilerFacadeSha256);
                Expect("NativeLayoutResolutionFacadeShape", () => { using (var c = NativeLayoutIdentityContext.LoadCompiler(b, linked, fake, ShadowHash.Bytes(fake), input.compilerFacadeSha256)) { } });
            });
            Check("M07-changed-real-parent", () => {
                byte[] changed;
                using (var m = ModuleDefMD.Load(b[bi])) { var t = m.GetTypes().Single(x => x.FullName == "AssemblyA.Implementation.Internal.InternalEntry"); t.BaseType = new TypeRefUser(m, "System", "String", m.GetAssemblyRefs().Single(x => x.Name == "netstandard")); changed = Bytes(m); }
                var altered = (byte[][])b.Clone(); altered[bi] = changed;
                using (var c = NativeLayoutIdentityContext.LoadCompiler(altered, linked, facade, input.runtimeFacadeSha256, input.compilerFacadeSha256))
                    Need(!NativeLayoutAdmissionValidator.Analyze(a[ai], changed, linked, c).editorAccepted, "True parent change rejected");
            });
        }
        foreach (var file in input.linked.Concat(input.compiler).Concat(new[] { input.runtimeFacade })) Read(file);
    }
    static int Main(string[] args)
    {
        Need(args.Length == 4 && args[0] == "--output" && args[2] == "--input", "--output unused --input authenticated-json");
        root = Path.GetFullPath(args[1]); Need(!Directory.Exists(root) && !File.Exists(root), "Unused evidence root"); Directory.CreateDirectory(root); report = new Report();
        try
        {
            Synthetic();
#if HOST_LAYOUT
            var input = JsonSerializer.Deserialize<Inputs>(File.ReadAllText(args[3]), new JsonSerializerOptions { IncludeFields = true });
#else
            var input = JsonConvert.DeserializeObject<Inputs>(File.ReadAllText(args[3]));
#endif
            Real(input);
        }
        catch (Exception e) { report.failures++; report.cases.Add(new Case { id = "unexpected", result = "Failed", error = e.ToString() }); }
        report.files = Directory.GetFiles(root, "*.dll", SearchOption.AllDirectories).OrderBy(x => x, StringComparer.Ordinal).Select(p => new Inventory { path = Path.GetFileName(p), sha256 = ShadowHash.File(p), size = new FileInfo(p).Length }).ToArray();
        report.result = report.failures == 0 ? "Passed" : "Failed"; Save("results.json", report);
        Console.WriteLine("LAYOUT_IDENTITY cases=" + report.cases.Count + " failures=" + report.failures); return report.failures == 0 ? 0 : 1;
    }
}
