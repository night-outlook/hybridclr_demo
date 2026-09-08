using System;
using System.IO;
using System.Linq;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Player;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01FailureFixturesTests
    {
        [Test]
        public void InitializerThrowCompilerShapeIsIsolated()
        {
            string root = Path.GetFullPath("_temp/AssemblyShadow/R01InitializerThrowCompiler-" + Guid.NewGuid().ToString("N"));
            string output = Path.Combine(root, "CompilerOutput");
            Directory.CreateDirectory(output);
            try
            {
                var settings = new ScriptCompilationSettings {
                    group = BuildPipeline.GetBuildTargetGroup(EditorUserBuildSettings.activeBuildTarget),
                    target = EditorUserBuildSettings.activeBuildTarget,
                    options = ScriptCompilationOptions.DevelopmentBuild,
                    extraScriptingDefines = ShadowReflectionBindingEvidence.CompilationDefines(new[] {
                        M03Build.InitializerDefine, M03Build.P03InitializerDefine, M03Build.P01Define, M03Build.P03Define,
                        "ASSEMBLY_SHADOW_R01_INITIALIZER_THROW"
                    })
                };
                var compilation = PlayerBuildInterface.CompilePlayerScripts(settings, output);
                Assert.IsNotNull(compilation.assemblies);
                Assert.Greater(compilation.assemblies.Count, 0, "Unity must return compiled fixture assemblies.");
                string[] emitted = compilation.assemblies.Select(path => File.Exists(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(output, path))).ToArray();
                string internalPath = emitted.Single(path => Path.GetFileName(path) == "AssemblyA.Implementation.Internal.dll");
                string extensibilityPath = emitted.Single(path => Path.GetFileName(path) == "AssemblyA.Implementation.Extensibility.dll");
                using (var internalModule = ModuleDefMD.Load(internalPath))
                using (var extensibilityModule = ModuleDefMD.Load(extensibilityPath))
                {
                    Assert.IsNull(internalModule.GlobalType.Methods.SingleOrDefault(method => method.Name == ".cctor"),
                        "The R01 define must suppress Internal's module initializer.");
                    TypeDef initializerType = extensibilityModule.Find("AssemblyA.Implementation.Extensibility.M03ModuleInitializer", false);
                    Assert.IsNotNull(initializerType);
                    MethodDef initialize = initializerType.Methods.SingleOrDefault(method => method.Name == "Initialize" && method.IsStatic &&
                        method.Parameters.Count == 0 && method.ReturnType.ElementType == ElementType.Void);
                    Assert.IsNotNull(initialize);
                    Assert.IsNotNull(initialize.Body);
                    int marker = initialize.Body.Instructions.ToList().FindIndex(instruction => instruction.OpCode.Code == Code.Ldstr &&
                        (instruction.Operand as string) == "M03-INIT:AssemblyA.Implementation.Extensibility");
                    int throwLiteral = initialize.Body.Instructions.ToList().FindIndex(instruction => instruction.OpCode.Code == Code.Ldstr &&
                        (instruction.Operand as string) == "R01-INIT-THROW:AssemblyA.Implementation.Extensibility");
                    Assert.GreaterOrEqual(marker, 0);
                    Assert.Greater(throwLiteral, marker);
                    var newobj = initialize.Body.Instructions.Skip(throwLiteral).FirstOrDefault(instruction => instruction.OpCode.Code == Code.Newobj);
                    Assert.IsNotNull(newobj);
                    var constructor = (IMethod)newobj.Operand;
                    Assert.AreEqual(".ctor", constructor.Name.String);
                    Assert.AreEqual("System.InvalidOperationException", constructor.DeclaringType.FullName);
                    Assert.AreEqual(0, constructor.MethodSig.GenParamCount);
                    Assert.AreEqual(1, constructor.MethodSig.Params.Count);
                    Assert.AreEqual("System.String", constructor.MethodSig.Params[0].FullName);
                    Assert.AreEqual(ElementType.Void, constructor.MethodSig.RetType.ElementType);
                    Assert.IsTrue(initialize.Body.Instructions.Skip(throwLiteral).Any(instruction => instruction.OpCode.Code == Code.Throw));

                    MethodDef moduleCctor = extensibilityModule.GlobalType.Methods.SingleOrDefault(method => method.Name == ".cctor");
                    Assert.IsNotNull(moduleCctor);
                    var call = moduleCctor.Body.Instructions.SingleOrDefault(instruction => instruction.OpCode.Code == Code.Call && instruction.Operand is IMethod &&
                        ((IMethod)instruction.Operand).Name == "Initialize" && ((IMethod)instruction.Operand).DeclaringType.FullName == initializerType.FullName);
                    Assert.IsNotNull(call);
                    IMethod called = (IMethod)call.Operand;
                    Assert.AreEqual(0, called.MethodSig.GenParamCount);
                    Assert.AreEqual(0, called.MethodSig.Params.Count);
                    Assert.AreEqual(ElementType.Void, called.MethodSig.RetType.ElementType);
                    MethodDef resolved = called.ResolveMethodDef();
                    Assert.IsNotNull(resolved);
                    Assert.AreEqual(initialize.MDToken.Raw, resolved.MDToken.Raw);
                }
            }
            finally
            {
                if (Directory.Exists(root)) Directory.Delete(root, true);
            }
        }
    }
}
