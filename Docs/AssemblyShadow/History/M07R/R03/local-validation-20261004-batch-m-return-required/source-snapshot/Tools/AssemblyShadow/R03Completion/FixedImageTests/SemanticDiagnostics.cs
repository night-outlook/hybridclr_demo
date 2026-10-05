using System.Collections.Generic;
using System.Reflection;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
static class SemanticDiagnostics
{
    public static Dictionary<string,string> Capture(byte[] image)
    {
        var values=new Dictionary<string,string>();
        using(var module=ModuleDefMD.Load(image,new ModuleCreationOptions {TryToLoadPdbFromDisk=false}))
        foreach(string section in new[]{"WriteIdentity","WriteTypes","WriteMethods","WriteAttributes","WriteResources"})
        {
            var method=typeof(AssemblySemanticHasher).GetMethod(section,BindingFlags.Static|BindingFlags.NonPublic);
            values.Add(section,(string)method.Invoke(null,section=="WriteIdentity" ? new object[]{module} : new object[]{module,new SemanticHashOptions()}));
        }
        return values;
    }
}
