using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
internal static class Program
{
    private static AssemblyCapability[] Input() => R03ResourceCapabilityProfile.Included.Concat(R03ResourceCapabilityProfile.Excluded).Select(n => new AssemblyCapability { name = n }).ToArray();
    private static void Check(bool value) { if (!value) throw new Exception("Contract failed"); }
    private static void Reject(Action action) { try { action(); } catch (InvalidOperationException) { return; } throw new Exception("Expected rejection"); }
    private static int Main(string[] args)
    {
        string root = args[Array.IndexOf(args, "--output") + 1]; if (Directory.Exists(root)) throw new Exception("Unused output required"); Directory.CreateDirectory(root);
        var cases = new List<object>(); int failures = 0;
        Action<string,Action> test = (id, action) => { string error = null; try { action(); } catch (Exception e) { error = e.ToString(); failures++; }
            cases.Add(new { id, result = error == null ? "Passed" : "Failed", error }); };
        test("P01-exact-profile", () => Check(R03ResourceCapabilityProfile.Select(Input()).Select(c => c.name).SequenceEqual(R03ResourceCapabilityProfile.Included)));
        test("P02-default-unchanged", () => { var a = Input(); Check(ReferenceEquals(a, R03ResourceCapabilityProfile.Apply(a))); });
        test("P03-missing", () => Reject(() => R03ResourceCapabilityProfile.Select(Input().Skip(1).ToArray())));
        test("P04-extra", () => Reject(() => R03ResourceCapabilityProfile.Select(Input().Concat(new[] { new AssemblyCapability { name="extra" } }).ToArray())));
        test("P05-duplicate", () => { var a=Input();a[1]=a[0];Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P06-null", () => Reject(() => R03ResourceCapabilityProfile.Select(null)));
        test("P07-null-row", () => { var a=Input();a[1]=null;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P08-shadow", () => { var a=Input();a[0].isShadowCapable=true;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P09-bootstrap", () => { var a=Input();a[0].isBootstrap=true;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P10-classification", () => { var a=Input();a[0].classification=AssemblyClassification.NormalHotUpdate;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P11-precompiled-state", () => { var a=Input();a[0].isPrecompiled=true;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P12-declared-state", () => { var a=Input();a[0].capabilityDeclared=true;Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P13-case-sensitive", () => { var a=Input();a[0].name=a[0].name.ToLowerInvariant();Reject(() => R03ResourceCapabilityProfile.Select(a)); });
        test("P14-no-alias", () => { var a=Input();var b=R03ResourceCapabilityProfile.Select(a);b[0].isShadowCapable=true;Check(!a[0].isShadowCapable); });
        test("P15-reorder", () => Check(R03ResourceCapabilityProfile.Select(Input().Reverse().ToArray()).Length==3));
        test("P16-scope-release", () => { var a=Input();using(R03ResourceCapabilityProfile.Enter())Check(R03ResourceCapabilityProfile.Apply(a).Length==3);Check(ReferenceEquals(a,R03ResourceCapabilityProfile.Apply(a))); });
        test("P17-nested-rejected", () => { using(R03ResourceCapabilityProfile.Enter())Reject(() => R03ResourceCapabilityProfile.Enter()); });
        test("P18-cross-thread", () => { using(R03ResourceCapabilityProfile.Enter()){ bool rejected=false;var t=new Thread(() => { try { R03ResourceCapabilityProfile.Apply(Input()); } catch(InvalidOperationException){rejected=true;} });t.Start();t.Join();Check(rejected); } });
        test("P19-exception-release", () => { try { using(R03ResourceCapabilityProfile.Enter())throw new Exception("control"); } catch(Exception){} var a=Input();Check(ReferenceEquals(a,R03ResourceCapabilityProfile.Apply(a))); });
        test("P20-wrong-owner-dispose", () => { var scope=R03ResourceCapabilityProfile.Enter();bool rejected=false;var t=new Thread(() => { try {scope.Dispose();}catch(InvalidOperationException){rejected=true;} });t.Start();t.Join();Check(rejected);scope.Dispose();scope.Dispose();Check(R03ResourceCapabilityProfile.Apply(Input()).Length==5); });
        File.WriteAllText(Path.Combine(root,"results.json"),JsonSerializer.Serialize(new {kind="R03CapabilityProfileHost",result=failures==0?"Passed":"Failed",cases,failures,unityEditorRun=false,runtimeAcceptance=false},new JsonSerializerOptions {WriteIndented=true}));
        return failures==0?0:1;
    }
}
