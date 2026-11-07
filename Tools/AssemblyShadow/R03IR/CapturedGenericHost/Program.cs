// Genuine .NET8 host control for the test-only AOT generic owner source.
// Does not invoke Unity, HybridCLR, the physical IL2CPP method guard,
// any Shadow Commit or the original historical Methods fixture.
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Loader;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using dnlib.DotNet;
using AssemblyShadow.R03.Fixtures;
using AssemblyShadow.R03.IR;

internal static class Program
{
    private static void Need(bool value, string reason)
    {
        if (!value) throw new InvalidOperationException("Captured generic host: " + reason);
    }

    private static bool ExactPhysicalContext(MethodInfo closed, Type physicalArgument, Type owner)
    {
        return closed != null && closed.IsConstructedGenericMethod &&
            closed.DeclaringType == owner &&
            closed.GetGenericMethodDefinition().DeclaringType == owner &&
            closed.GetGenericArguments().Length == 1 &&
            closed.GetGenericArguments()[0] == physicalArgument &&
            physicalArgument.Assembly.GetName().Name == "Methods" &&
            owner.Assembly != physicalArgument.Assembly &&
            !owner.Assembly.GetReferencedAssemblies().Any(a => a.Name == "Methods");
    }

    private static int Main(string[] args)
    {
        if (args.Length != 2 || args[0] != "--emit-and-verify")
        {
            Console.Error.WriteLine("Use --emit-and-verify <unused-absolute-host-directory>");
            return 2;
        }
        try { return EmitAndVerify(args[1]); }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.GetType().FullName + ": " + error.Message);
            return 7;
        }
    }

    private static int EmitAndVerify(string destination)
    {
        Need(Path.IsPathFullyQualified(destination) && Path.GetFullPath(destination) == destination &&
             !Directory.Exists(destination) && !File.Exists(destination),
             "Fresh absolute host-only destination required");
        // The same reviewed fixture producer used by original R03 host tests.
        // This is an independently emitted host byte array, not historical S.
        byte[] methods = EvolutionFixtureCorpus.Build("Methods");
        Guid mvid;
        using (var module = ModuleDefMD.Load(methods))
        {
            Need(module.Assembly != null && module.Assembly.Name.String == "Methods" &&
                 module.GetTypes().Count(t => t.FullName == "R03.Node") == 1,
                 "Real Methods/R03.Node IL metadata identity");
            var node = module.GetTypes().Single(t => t.FullName == "R03.Node");
            Need(node.Methods.Any(m => m.Name == "Keep") &&
                 node.Fields.Count(f => f.Name == "stable" && !f.IsStatic) == 1,
                 "Original physical instance shape in host fixture");
            mvid = module.Mvid;
        }
        string methodsSha256 = Convert.ToHexString(SHA256.HashData(methods)).ToLowerInvariant();
        var owner = typeof(R03CapturedGenericAotOwner);
        MethodInfo definition = owner.GetMethod("Touch", BindingFlags.Public | BindingFlags.Static);
        Need(definition != null && definition.IsGenericMethodDefinition &&
             definition.IsStatic && definition.GetParameters().Length == 0 &&
             definition.ReturnType == typeof(int) &&
             definition.GetGenericArguments().Length == 1 &&
             (definition.GetGenericArguments()[0].GenericParameterAttributes &
              GenericParameterAttributes.ReferenceTypeConstraint) != 0 &&
             owner.Assembly.GetName().Name == "R03CapturedGenericHost" &&
             !owner.Assembly.GetReferencedAssemblies().Any(a => a.Name == "Methods"),
             "Independent, class-constrained, zero-arg AOT-owner source method");
        // A genuine CLR runtime loads a physically distinct module and
        // constructs an actual MethodInfo with Methods.R03.Node as T.
        var context = new AssemblyLoadContext("R03-Captured-Generic-Host", isCollectible: true);
        try
        {
            Assembly physical;
            using (var stream = new MemoryStream(methods, writable: false))
                physical = context.LoadFromStream(stream);
            Type node = physical.GetType("R03.Node", throwOnError: true);
            Need(node != null && node.IsClass && node.Assembly.GetName().Name == "Methods" &&
                 physical.ManifestModule.ModuleVersionId == mvid &&
                 owner.Assembly != physical, "Distinct owner versus physical argument module");
            MethodInfo closed = definition.MakeGenericMethod(node);
            Need(ExactPhysicalContext(closed, node, owner),
                 "Actual closed generic MethodInfo captures independently owned Methods.R03.Node");
            // The CLR permits a same-owner T because it satisfies "class".
            // Our source/semantic contract must reject this false witness.
            MethodInfo wrongOwner = definition.MakeGenericMethod(owner);
            Need(!ExactPhysicalContext(wrongOwner, node, owner),
                 "Same-owner argument must not prove physical Methods capture");
            bool invalidValueTypeRejected = false;
            try { definition.MakeGenericMethod(typeof(int)); }
            catch (ArgumentException) { invalidValueTypeRejected = true; }
            Need(invalidValueTypeRejected, "Real CLR rejects nonreference generic argument");

            int before = owner.GetProperty("Calls").GetValue(null) is int initial ? initial : -1;
            Need(before == 0, "Fresh host counter");
            int warm = R03CapturedGenericAotOwner.WarmShared();
            int afterWarm = R03CapturedGenericAotOwner.Calls;
            int reflected = (int)closed.Invoke(null, null);
            int afterReflect = R03CapturedGenericAotOwner.Calls;
            var callback = (Func<int>)closed.CreateDelegate(typeof(Func<int>));
            int delegated = callback();
            int afterDelegate = R03CapturedGenericAotOwner.Calls;
            Need(warm == 42 && reflected == 42 && delegated == 42 &&
                 afterWarm == 1 && afterReflect == 2 && afterDelegate == 3,
                 "Real CLR pre-positive generic bodies and monotone side effects");

            Directory.CreateDirectory(destination);
            string dllPath = Path.Combine(destination, "Methods.dll");
            using (var stream = new FileStream(dllPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                stream.Write(methods, 0, methods.Length);
            var receipt = new
            {
                schemaVersion = 1,
                kind = "R03CapturedGenericOwnerHostV1",
                result = "PassedCLRPhysicalOwnerStructureAndBodies_NotUnity",
                ownerAssembly = owner.Assembly.GetName().Name,
                ownerMethod = owner.FullName + ".Touch<T>",
                capturedArgumentAssembly = node.Assembly.GetName().Name,
                capturedArgumentType = node.FullName,
                ownerHasStaticMethodsDependency = owner.Assembly.GetReferencedAssemblies().Any(a => a.Name == "Methods"),
                ownerDifferentFromArgument = owner.Assembly != node.Assembly,
                openGenericDefinition = definition.IsGenericMethodDefinition,
                closedGenericMethod = closed.IsConstructedGenericMethod,
                genericArity = closed.GetGenericArguments().Length,
                referenceTypeConstraint = true,
                methodsSha256,
                methodsMvid = mvid.ToString(),
                methodsSize = methods.Length,
                clrModuleMvidMatches = true,
                prewarmedReturn = warm,
                reflectiveReturn = reflected,
                delegatedReturn = delegated,
                callCountAfterWarm = afterWarm,
                callCountAfterReflection = afterReflect,
                callCountAfterDelegate = afterDelegate,
                wrongOwnerRejectedByWitnessContract = true,
                invalidValueTypeRejectedByCLR = invalidValueTypeRejected,
                // These explicit negatives cannot be overridden by host tests.
                il2cppMethodContextObserved = false,
                nativeGuardExecuted = false,
                capturedBaselineFailure15Observed = false,
                unityOrPlayerExecuted = false,
                originalSReusedAsNewInput = false,
                runtimeAcceptance = false,
                R03Accepted = false,
                H2Passed = false
            };
            string text = JsonSerializer.Serialize(receipt, new JsonSerializerOptions { WriteIndented = true }) + "\n";
            using (var writer = new StreamWriter(
                new FileStream(Path.Combine(destination, "HOST_RESULT.json"), FileMode.CreateNew,
                               FileAccess.Write, FileShare.None), new UTF8Encoding(false)))
                writer.Write(text);
            Console.WriteLine(text);
            return 0;
        }
        finally { context.Unload(); }
    }
}
