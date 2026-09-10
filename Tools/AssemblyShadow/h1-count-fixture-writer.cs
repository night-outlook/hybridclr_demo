using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class H1CountFixtureWriter
{
    private const uint FixedPeTimestamp = 0x5f3759df;
    private const int MaximumCount = 65537;
    private const int MaximumNestedCount = 131071;
    private const string ShadowAssemblyName = "AssemblyShadow.H1Count.Target";
    private const string NestedShadowAssemblyName = "AssemblyShadow.H1Nested.Target";

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 6 && args.Length != 7)
                throw new ArgumentException("expected output, assembly name, case id, count, variant, seed, and optional family");

            string output = Path.GetFullPath(args[0]);
            string assemblyName = args[1];
            string caseId = args[2];
            string variant = args[4];
            bool nested = args.Length == 7;
            if (nested && args[6] != "nested")
                throw new ArgumentException("optional family must be nested");
            int count = ParseCount(args[3], nested ? MaximumNestedCount : MaximumCount);
            int seed;
            if (!Int32.TryParse(args[5], NumberStyles.None, CultureInfo.InvariantCulture, out seed) || seed < 0)
                throw new ArgumentException("seed must be a non-negative signed 32-bit integer");
            if (nested)
            {
                ValidateNestedInvocation(assemblyName, caseId, count, variant);
                CreateNested(output, assemblyName, caseId, count, variant, seed);
            }
            else
            {
                ValidateInvocation(assemblyName, caseId, count, variant);
                Create(output, assemblyName, caseId, count, variant, seed);
            }
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("h1-count-fixture-writer: " + error.Message);
            return 1;
        }
    }

    private static int ParseCount(string value, int maximum = MaximumCount)
    {
        int count;
        if (!Int32.TryParse(value, NumberStyles.None, CultureInfo.InvariantCulture, out count) ||
            count < 0 || count > maximum)
            throw new ArgumentException("count is outside the fixture limit");
        return count;
    }

    private static void ValidateNestedInvocation(string assemblyName, string caseId, int count, string variant)
    {
        if (String.IsNullOrEmpty(assemblyName) || String.IsNullOrEmpty(caseId))
            throw new ArgumentException("assembly name and case id are required");
        if (assemblyName == NestedShadowAssemblyName && caseId.Length == 0)
            throw new ArgumentException("nested case id is required");
        if (variant == "nested-single" || variant == "nested-final-repeat")
            return;
        if (variant == "nested-interleaved" && count == 4)
            return;
        if (variant == "nested-adjacent-valid" && count == 65536)
            return;
        if (variant == "nested-adjacent-overflow" && count == 65537)
            return;
        throw new ArgumentException("unknown nested fixture variant");
    }

    private static void ValidateInvocation(string assemblyName, string caseId, int count, string variant)
    {
        if (String.IsNullOrEmpty(assemblyName) || String.IsNullOrEmpty(caseId))
            throw new ArgumentException("assembly name and case id are required");
        if (variant == "return255" || variant == "partial-names" || variant == "instance" || variant == "mixed-kinds")
        {
            if (count != 255)
                throw new ArgumentException("P04 variants require count 255");
            return;
        }
        if (!variant.StartsWith("base-", StringComparison.Ordinal) ||
            variant.Substring(5) != count.ToString(CultureInfo.InvariantCulture))
            throw new ArgumentException("unknown parameter fixture variant");
    }

    private static void Create(string output, string assemblyName, string caseId, int count, string variant, int seed)
    {
        if (File.Exists(output) || Directory.Exists(output))
            throw new InvalidOperationException("refusing to overwrite " + output);
        string directory = Path.GetDirectoryName(output);
        if (String.IsNullOrEmpty(directory))
            throw new ArgumentException("output must have a parent directory");
        Directory.CreateDirectory(directory);

        var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(assemblyName, new Version(1, 0, 0, 1)),
            assemblyName, ModuleKind.Dll);
        try
        {
            ModuleDefinition module = assembly.MainModule;
            module.RuntimeVersion = "v4.0.30319";
            module.Mvid = DeterministicMvid(seed, assemblyName, caseId, count, variant);
            string typeName = assemblyName == ShadowAssemblyName
                ? "Target"
                : "Ordinary_" + Sanitize(caseId);
            var type = new TypeDefinition("AssemblyShadow.H1Count", typeName,
                TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed | TypeAttributes.BeforeFieldInit,
                module.TypeSystem.Object);
            module.Types.Add(type);

            MethodAttributes attributes = MethodAttributes.Public | MethodAttributes.HideBySig;
            if (variant != "instance")
                attributes |= MethodAttributes.Static;
            var method = new MethodDefinition("Probe", attributes, module.TypeSystem.Int32);
            AddParameters(module, method, count, variant);
            if (variant == "return255")
            {
                method.MethodReturnType.Name = "result";
                method.MethodReturnType.Attributes = ParameterAttributes.Retval;
            }
            var body = new MethodBody(method);
            ILProcessor il = body.GetILProcessor();
            il.Emit(OpCodes.Ldc_I4, Marker(seed, caseId, count, variant));
            il.Emit(OpCodes.Ret);
            method.Body = body;
            type.Methods.Add(method);

            assembly.Write(output, new WriterParameters
            {
                Timestamp = FixedPeTimestamp,
                DeterministicMvid = false,
            });
        }
        finally
        {
            assembly.Dispose();
        }
    }

    private static void CreateNested(string output, string assemblyName, string caseId, int count,
        string variant, int seed)
    {
        if (File.Exists(output) || Directory.Exists(output))
            throw new InvalidOperationException("refusing to overwrite " + output);
        string directory = Path.GetDirectoryName(output);
        if (String.IsNullOrEmpty(directory))
            throw new ArgumentException("output must have a parent directory");
        Directory.CreateDirectory(directory);

        var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(assemblyName, new Version(1, 0, 0, 1)),
            assemblyName, ModuleKind.Dll);
        try
        {
            ModuleDefinition module = assembly.MainModule;
            module.RuntimeVersion = "v4.0.30319";
            module.Mvid = DeterministicMvid(seed, assemblyName, caseId, count, variant, "nested");
            string firstName = "Target";
            string[] names = variant == "nested-adjacent-valid" ||
                variant == "nested-adjacent-overflow" || variant == "nested-interleaved"
                ? new[] { firstName, "SiblingB" }
                : new[] { firstName };
            int[] groupCounts = variant == "nested-adjacent-valid"
                ? new[] { 1, 65535 }
                : variant == "nested-adjacent-overflow" ? new[] { 1, 65536 }
                : variant == "nested-interleaved" ? new[] { 2, 2 } : new[] { count };
            var declaring = new TypeDefinition[names.Length];
            for (int index = 0; index < names.Length; ++index)
            {
                declaring[index] = new TypeDefinition("AssemblyShadow.H1Nested", names[index],
                    TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed | TypeAttributes.BeforeFieldInit,
                    module.TypeSystem.Object);
                module.Types.Add(declaring[index]);
            }
            for (int group = 0; group < declaring.Length; ++group)
            {
                for (int index = 0; index < groupCounts[group]; ++index)
                {
                    var child = new TypeDefinition("", names[group] + "Child" +
                        index.ToString("D5", CultureInfo.InvariantCulture),
                        TypeAttributes.NestedPublic | TypeAttributes.Class | TypeAttributes.Sealed |
                        TypeAttributes.BeforeFieldInit, module.TypeSystem.Object);
                    declaring[group].NestedTypes.Add(child);
                }
            }
            assembly.Write(output, new WriterParameters
            {
                Timestamp = FixedPeTimestamp,
                DeterministicMvid = false,
            });
        }
        finally
        {
            assembly.Dispose();
        }
    }

    private static void AddParameters(ModuleDefinition module, MethodDefinition method, int count, string variant)
    {
        for (int index = 0; index < count; ++index)
        {
            string name = String.Empty;
            if (variant == "partial-names" && index % 17 == 0)
                name = "p" + (index + 1).ToString("D4", CultureInfo.InvariantCulture);
            method.Parameters.Add(new ParameterDefinition(name, ParameterAttributes.None,
                ParameterType(module, index, variant)));
        }
    }

    private static TypeReference ParameterType(ModuleDefinition module, int index, string variant)
    {
        if (variant != "mixed-kinds")
            return module.TypeSystem.Int32;
        switch (index % 5)
        {
            case 0: return module.TypeSystem.Int32;
            case 1: return module.TypeSystem.String;
            case 2: return module.TypeSystem.Object;
            case 3: return new ByReferenceType(module.TypeSystem.Int32);
            default: return new ArrayType(module.TypeSystem.String);
        }
    }

    private static int Marker(int seed, string caseId, int count, string variant)
    {
        unchecked
        {
            int value = seed * 397 + count;
            foreach (char character in caseId + ":" + variant)
                value = value * 31 + character;
            return value;
        }
    }

    private static Guid DeterministicMvid(int seed, string assemblyName, string caseId, int count,
        string variant, string family = "parameters")
    {
        using (SHA256 hash = SHA256.Create())
        {
            byte[] digest = hash.ComputeHash(Encoding.UTF8.GetBytes(
                "H1R/M02.B/" + family + "/" + seed.ToString(CultureInfo.InvariantCulture) + ":" +
                assemblyName + ":" + caseId + ":" + count.ToString(CultureInfo.InvariantCulture) + ":" + variant));
            byte[] bytes = new byte[16];
            Buffer.BlockCopy(digest, 0, bytes, 0, bytes.Length);
            bytes[7] = (byte)((bytes[7] & 0x0f) | 0x40);
            bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
            return new Guid(bytes);
        }
    }

    private static string Sanitize(string value)
    {
        var builder = new StringBuilder(value.Length);
        foreach (char character in value)
            builder.Append(Char.IsLetterOrDigit(character) ? character : '_');
        return builder.ToString();
    }
}
