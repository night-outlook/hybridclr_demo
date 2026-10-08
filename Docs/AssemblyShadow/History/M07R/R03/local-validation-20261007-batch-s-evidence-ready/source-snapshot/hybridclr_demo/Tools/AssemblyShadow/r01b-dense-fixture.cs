using System;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class R01BDenseFixture
{
    private const int TypeCount = 4097;
    private const int TargetBytes = 1024 * 1024;
    private const uint FixedPeTimestamp = 0x5f3759df;
    private const string Namespace = "AssemblyShadow.Dense";

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 2)
                throw new ArgumentException("expected fixture id and output DLL path");
            int id = int.Parse(args[0], CultureInfo.InvariantCulture);
            if (id < 1 || id > 2)
                throw new ArgumentOutOfRangeException("fixture id");
            string output = Path.GetFullPath(args[1]);
            if (File.Exists(output) || Directory.Exists(output))
                throw new InvalidOperationException("refusing to overwrite " + output);
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            Create(id, output);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("r01b-dense-fixture: " + error.Message);
            return 1;
        }
    }

    private static void Create(int id, string output)
    {
        string assemblyName = AssemblyName(id);
        var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(assemblyName, new Version(1, 0, 0, id)),
            assemblyName, ModuleKind.Dll);
        try
        {
            ModuleDefinition module = assembly.MainModule;
            module.RuntimeVersion = "v4.0.30319";
            module.Mvid = DeterministicMvid(id);
            for (int index = 0; index < TypeCount; ++index)
            {
                var type = new TypeDefinition(
                    Namespace,
                    DenseTypeName(id, index),
                    TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed,
                    module.TypeSystem.Object);
                module.Types.Add(type);

                var method = new MethodDefinition(
                    "ReturnId",
                    MethodAttributes.Public | MethodAttributes.Static | MethodAttributes.HideBySig,
                    module.TypeSystem.Int32);
                type.Methods.Add(method);
                var body = new MethodBody(method) { InitLocals = false };
                method.Body = body;
                ILProcessor il = body.GetILProcessor();
                il.Emit(OpCodes.Ldc_I4, id * 10000 + index);
                il.Emit(OpCodes.Ret);
            }
            assembly.Write(output, new WriterParameters {
                Timestamp = FixedPeTimestamp,
                DeterministicMvid = false
            });
        }
        finally
        {
            assembly.Dispose();
        }

        Verify(id, output);
        long length = new FileInfo(output).Length;
        if (length > TargetBytes)
            throw new InvalidOperationException("generated fixture exceeds 1 MiB: " + length);
        using (var stream = new FileStream(output, FileMode.Append, FileAccess.Write, FileShare.None))
        {
            byte[] zeros = new byte[8192];
            while (stream.Length < TargetBytes)
            {
                int count = (int)Math.Min(zeros.Length, TargetBytes - stream.Length);
                stream.Write(zeros, 0, count);
            }
        }
        if (new FileInfo(output).Length != TargetBytes)
            throw new InvalidOperationException("fixture padding did not reach exactly 1 MiB");
    }

    private static void Verify(int id, string output)
    {
        using (AssemblyDefinition assembly = AssemblyDefinition.ReadAssembly(output))
        {
            ModuleDefinition module = assembly.MainModule;
            if (assembly.Name.Name != AssemblyName(id) ||
                assembly.Name.Version != new Version(1, 0, 0, id) ||
                module.Mvid != DeterministicMvid(id))
                throw new InvalidOperationException("generated fixture identity is not reproducible");
            if (module.Types.Count != TypeCount + 1)
                throw new InvalidOperationException("unexpected TypeDef count");
            for (int index = 0; index < TypeCount; ++index)
            {
                TypeDefinition type = module.Types[index + 1];
                if (type.Namespace != Namespace || type.Name != DenseTypeName(id, index) ||
                    type.Methods.Count != 1 || type.Methods[0].Name != "ReturnId")
                    throw new InvalidOperationException("generated dense type shape differs at " + index);
            }
        }
    }

    private static string AssemblyName(int id)
    {
        return "AssemblyShadow.Workload.I" + id.ToString("D4", CultureInfo.InvariantCulture);
    }

    private static string DenseTypeName(int id, int index)
    {
        return "DenseType_" + id.ToString("D4", CultureInfo.InvariantCulture) + "_" +
            index.ToString("D4", CultureInfo.InvariantCulture) +
            "_MetadataBoundary_0123456789abcdef0123456789abcdef";
    }

    private static Guid DeterministicMvid(int id)
    {
        using (SHA256 hash = SHA256.Create())
        {
            byte[] digest = hash.ComputeHash(Encoding.UTF8.GetBytes(
                "R01B-dense-fixture:v2:" + id.ToString(CultureInfo.InvariantCulture)));
            byte[] bytes = new byte[16];
            Buffer.BlockCopy(digest, 0, bytes, 0, bytes.Length);
            bytes[7] = (byte)((bytes[7] & 0x0f) | 0x40);
            bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
            return new Guid(bytes);
        }
    }
}
