using System;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class R01BOverflowFixture
{
    private const int Id = 8192;
    private const int TargetBytes = 61440;
    private const int MetadataTypeCount = 96;
    private const uint FixedPeTimestamp = 0x5f3759df;

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 1)
                throw new ArgumentException("expected one output DLL path");
            string output = Path.GetFullPath(args[0]);
            if (File.Exists(output) || Directory.Exists(output))
                throw new InvalidOperationException("refusing to overwrite " + output);
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            Create(output);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("r01b-overflow-fixture: " + error.Message);
            return 1;
        }
    }

    private static void Create(string output)
    {
        string name = "AssemblyShadow.WorkloadV2.I8192";
        var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(name, new Version(1, 0, 0, Id)), name, ModuleKind.Dll);
        string core = output + ".core";
        try
        {
            ModuleDefinition module = assembly.MainModule;
            module.RuntimeVersion = "v4.0.30319";
            module.Mvid = DeterministicMvid();
            TypeDefinition entry = AddType(module, "MetadataEntry_8192", true);
            var payload = new FieldDefinition("PayloadRva_00",
                FieldAttributes.Public | FieldAttributes.Static | FieldAttributes.HasFieldRVA,
                module.TypeSystem.Byte);
            payload.InitialValue = Payload(45000);
            entry.Fields.Add(payload);
            for (int index = 0; index < MetadataTypeCount; ++index)
            {
                AddType(module, "MetadataType_8192_" + index.ToString("D4", CultureInfo.InvariantCulture) +
                    "_Strings_0123456789abcdef0123456789abcdef", false);
            }
            assembly.Write(core, new WriterParameters { Timestamp = FixedPeTimestamp, DeterministicMvid = false });
        }
        finally
        {
            assembly.Dispose();
        }

        long coreBytes = new FileInfo(core).Length;
        if (coreBytes > TargetBytes)
            throw new InvalidOperationException("core DLL exceeds the 60 KiB fixture target");
        using (var input = new FileStream(core, FileMode.Open, FileAccess.Read, FileShare.Read))
        using (var destination = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
        {
            input.CopyTo(destination);
            destination.SetLength(TargetBytes);
            destination.Flush(true);
        }
        File.Delete(core);
    }

    private static TypeDefinition AddType(ModuleDefinition module, string name, bool entry)
    {
        var type = new TypeDefinition("AssemblyShadow.WorkloadV2", name,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed | TypeAttributes.BeforeFieldInit,
            module.TypeSystem.Object);
        module.Types.Add(type);
        AddMethod(module, type, "ReturnId");
        if (entry)
            AddMethod(module, type, "ReturnPayloadMarker");
        return type;
    }

    private static void AddMethod(ModuleDefinition module, TypeDefinition type, string name)
    {
        var method = new MethodDefinition(name,
            MethodAttributes.Public | MethodAttributes.Static | MethodAttributes.HideBySig,
            module.TypeSystem.Int32);
        var body = new MethodBody(method);
        body.GetILProcessor().Emit(OpCodes.Ldc_I4, Id);
        body.GetILProcessor().Emit(OpCodes.Ret);
        method.Body = body;
        type.Methods.Add(method);
    }

    private static Guid DeterministicMvid()
    {
        using (SHA256 hash = SHA256.Create())
        {
            byte[] digest = hash.ComputeHash(Encoding.UTF8.GetBytes("R01B-managed-workload-v2:mvid:8192"));
            byte[] bytes = new byte[16];
            Buffer.BlockCopy(digest, 0, bytes, 0, bytes.Length);
            bytes[7] = (byte)((bytes[7] & 0x0f) | 0x40);
            bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
            return new Guid(bytes);
        }
    }

    private static byte[] Payload(int length)
    {
        var bytes = new byte[length];
        for (int index = 0; index < bytes.Length; ++index)
            bytes[index] = (byte)((Id * 17 + index) % 251);
        return bytes;
    }
}
