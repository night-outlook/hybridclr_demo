using System;
using System.Linq;
using System.Reflection;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
internal static class Semantics
{
    public static void Main(string[] args)
    {
        foreach (string path in args)
        using (var module = ModuleDefMD.Load(path, new ModuleCreationOptions { TryToLoadPdbFromDisk = false }))
        {
            var result = AssemblySemanticHasher.Compute(module);
            Console.WriteLine("FILE " + path);
            Console.WriteLine("IDENTITY " + module.Assembly.FullName);
            Console.WriteLine("SEMANTIC " + result.semanticHash);
            foreach (string section in new[] { "WriteIdentity", "WriteTypes", "WriteMethods", "WriteAttributes" })
            {
                var method = typeof(AssemblySemanticHasher).GetMethod(section, BindingFlags.Static | BindingFlags.NonPublic);
                var parameters = method.GetParameters().Length == 1 ? new object[] { module } : new object[] { module, new SemanticHashOptions() };
                Console.WriteLine(section + "\n" + (string)method.Invoke(null, parameters));
            }
        }
    }
}
