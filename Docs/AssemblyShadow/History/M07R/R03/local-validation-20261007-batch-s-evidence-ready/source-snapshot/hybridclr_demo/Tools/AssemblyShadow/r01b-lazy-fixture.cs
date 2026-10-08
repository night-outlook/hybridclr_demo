using System;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class R01BLazyFixture
{
    private const string AssemblyName = "AssemblyShadow.R01BLazyFixture";
    private const string Namespace = "AssemblyShadow.R01B";
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
            Console.Error.WriteLine("r01b-lazy-fixture: " + error.Message);
            return 1;
        }
    }

    private static void Create(string output)
    {
        var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(AssemblyName, new Version(1, 0, 0, 1)), AssemblyName, ModuleKind.Dll);
        try
        {
            ModuleDefinition module = assembly.MainModule;
            module.RuntimeVersion = "v4.0.30319";
            module.Mvid = DeterministicMvid();
            TypeDefinition attribute = AddMarkerAttribute(module);
            TypeDefinition retryAttribute = AddRetryAttribute(module);
            TypeDefinition malformedAttribute = AddMalformedAttribute(module);
            TypeDefinition contract = AddGenericContract(module);
            TypeDefinition inherited = AddInheritedContract(module, contract);
            AddImplementation(module, inherited, contract);
            TypeDefinition box = AddGenericBox(module);
            TypeDefinition carrier = AddCarrier(module, attribute, box);
            TypeDefinition retryCarrier = AddRetryCarrier(module, retryAttribute);
            TypeDefinition malformedCarrier = AddMalformedCarrier(module);
            AddClass(module, "LazyEntry", module.TypeSystem.Object,
                TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
            AddMarker(carrier, attribute, module, "lazy-marker", ClosedBox(module, box, module.TypeSystem.Int32));
            AddRetry(retryCarrier, retryAttribute, module, 7);
            AddMalformed(malformedCarrier, malformedAttribute, module);
            assembly.Write(output, new WriterParameters { Timestamp = FixedPeTimestamp, DeterministicMvid = false });
        }
        finally
        {
            assembly.Dispose();
        }
        Verify(output);
    }

    private static TypeDefinition AddMarkerAttribute(ModuleDefinition module)
    {
        TypeDefinition type = AddClass(module, "LazyMarkerAttribute", module.ImportReference(typeof(Attribute)),
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
        FieldDefinition name = new FieldDefinition("Name", FieldAttributes.Public, module.TypeSystem.String);
        FieldDefinition payloadType = new FieldDefinition("PayloadType", FieldAttributes.Public, module.ImportReference(typeof(Type)));
        type.Fields.Add(name);
        type.Fields.Add(payloadType);
        MethodDefinition constructor = AddMethod(type, ".ctor", MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName, module.TypeSystem.Void);
        constructor.Parameters.Add(new ParameterDefinition("name", ParameterAttributes.None, module.TypeSystem.String));
        constructor.Parameters.Add(new ParameterDefinition("payloadType", ParameterAttributes.None, module.ImportReference(typeof(Type))));
        ILProcessor il = Body(constructor);
        il.Emit(OpCodes.Ldarg_0);
        il.Emit(OpCodes.Call, module.ImportMethod(typeof(Attribute), ".ctor", typeof(void)));
        il.Emit(OpCodes.Ldarg_0);
        il.Emit(OpCodes.Ldarg_1);
        il.Emit(OpCodes.Stfld, name);
        il.Emit(OpCodes.Ldarg_0);
        il.Emit(OpCodes.Ldarg_2);
        il.Emit(OpCodes.Stfld, payloadType);
        il.Emit(OpCodes.Ret);
        return type;
    }

    private static TypeDefinition AddRetryAttribute(ModuleDefinition module)
    {
        TypeDefinition type = AddClass(module, "LazyRetryAttribute", module.ImportReference(typeof(Attribute)),
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
        MethodDefinition constructor = AddMethod(type, ".ctor", MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName, module.TypeSystem.Void);
        constructor.Parameters.Add(new ParameterDefinition("marker", ParameterAttributes.None, module.TypeSystem.Int32));
        ILProcessor il = Body(constructor);
        il.Emit(OpCodes.Ldarg_0);
        il.Emit(OpCodes.Call, module.ImportMethod(typeof(Attribute), ".ctor", typeof(void)));
        il.Emit(OpCodes.Ldstr, "R01B retry marker constructor failure");
        il.Emit(OpCodes.Newobj, module.ImportMethod(typeof(InvalidOperationException), ".ctor", typeof(string)));
        il.Emit(OpCodes.Throw);
        return type;
    }

    private static TypeDefinition AddMalformedAttribute(ModuleDefinition module)
    {
        TypeDefinition type = AddClass(module, "LazyMalformedAttribute", module.ImportReference(typeof(Attribute)),
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
        FieldDefinition calls = new FieldDefinition("ConstructorCalls", FieldAttributes.Public | FieldAttributes.Static, module.TypeSystem.Int32);
        type.Fields.Add(calls);
        MethodDefinition constructor = AddMethod(type, ".ctor", MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName, module.TypeSystem.Void);
        constructor.Parameters.Add(new ParameterDefinition("validType", ParameterAttributes.None, module.ImportReference(typeof(Type))));
        constructor.Parameters.Add(new ParameterDefinition("truncatedValue", ParameterAttributes.None, module.TypeSystem.Int32));
        ILProcessor il = Body(constructor);
        il.Emit(OpCodes.Ldarg_0);
        il.Emit(OpCodes.Call, module.ImportMethod(typeof(Attribute), ".ctor", typeof(void)));
        il.Emit(OpCodes.Ldsfld, calls);
        il.Emit(OpCodes.Ldc_I4_1);
        il.Emit(OpCodes.Add);
        il.Emit(OpCodes.Stsfld, calls);
        il.Emit(OpCodes.Ret);
        return type;
    }

    private static TypeDefinition AddGenericContract(ModuleDefinition module)
    {
        TypeDefinition type = AddClass(module, "ILazyContract`1", null,
            TypeAttributes.Interface | TypeAttributes.Abstract | TypeAttributes.Public);
        GenericParameter parameter = new GenericParameter("T", type);
        type.GenericParameters.Add(parameter);
        MethodDefinition echo = AddMethod(type, "Echo", MethodAttributes.Public | MethodAttributes.Abstract | MethodAttributes.Virtual | MethodAttributes.HideBySig | MethodAttributes.NewSlot, parameter);
        echo.Parameters.Add(new ParameterDefinition("value", ParameterAttributes.None, parameter));
        return type;
    }

    private static TypeDefinition AddInheritedContract(ModuleDefinition module, TypeDefinition contract)
    {
        TypeDefinition type = AddClass(module, "IInheritedLazyContract", null,
            TypeAttributes.Interface | TypeAttributes.Abstract | TypeAttributes.Public);
        type.Interfaces.Add(new InterfaceImplementation(ClosedBox(module, contract, module.TypeSystem.Int32)));
        type.Interfaces.Add(new InterfaceImplementation(module.ImportReference(typeof(IDisposable))));
        return type;
    }

    private static TypeDefinition AddImplementation(ModuleDefinition module, TypeDefinition inherited, TypeDefinition contract)
    {
        TypeDefinition type = AddClass(module, "LazyImplementation", module.TypeSystem.Object,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
        // C# emits the inherited interface closure on the implementing class.
        // Vtable setup needs the generic and AOT interface entries as well.
        type.Interfaces.Add(new InterfaceImplementation(inherited));
        foreach (InterfaceImplementation parent in inherited.Interfaces)
            type.Interfaces.Add(new InterfaceImplementation(parent.InterfaceType));
        MethodDefinition constructor = AddMethod(type, ".ctor", MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName, module.TypeSystem.Void);
        ILProcessor constructorIl = Body(constructor);
        constructorIl.Emit(OpCodes.Ldarg_0);
        constructorIl.Emit(OpCodes.Call, module.ImportMethod(typeof(object), ".ctor", typeof(void)));
        constructorIl.Emit(OpCodes.Ret);
        MethodDefinition echo = AddMethod(type, "Echo", MethodAttributes.Public | MethodAttributes.Virtual | MethodAttributes.HideBySig | MethodAttributes.NewSlot | MethodAttributes.Final, module.TypeSystem.Int32);
        echo.Parameters.Add(new ParameterDefinition("value", ParameterAttributes.None, module.TypeSystem.Int32));
        ILProcessor il = Body(echo);
        il.Emit(OpCodes.Ldarg_1);
        il.Emit(OpCodes.Ldc_I4_7);
        il.Emit(OpCodes.Add);
        il.Emit(OpCodes.Ret);
        MethodDefinition dispose = AddMethod(type, "Dispose", MethodAttributes.Public | MethodAttributes.Virtual | MethodAttributes.HideBySig | MethodAttributes.NewSlot | MethodAttributes.Final, module.TypeSystem.Void);
        Body(dispose).Emit(OpCodes.Ret);
        return type;
    }

    private static TypeDefinition AddGenericBox(ModuleDefinition module)
    {
        TypeDefinition type = AddClass(module, "LazyBox`1", module.TypeSystem.Object,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
        GenericParameter parameter = new GenericParameter("T", type);
        type.GenericParameters.Add(parameter);

        MethodDefinition constructor = AddMethod(type, ".ctor", MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName, module.TypeSystem.Void);
        ILProcessor constructorIl = Body(constructor);
        constructorIl.Emit(OpCodes.Ldarg_0);
        constructorIl.Emit(OpCodes.Call, module.ImportMethod(typeof(object), ".ctor", typeof(void)));
        constructorIl.Emit(OpCodes.Ret);

        MethodDefinition echo = AddMethod(type, "Echo", MethodAttributes.Public | MethodAttributes.Static | MethodAttributes.HideBySig, parameter);
        echo.Parameters.Add(new ParameterDefinition("value", ParameterAttributes.None, parameter));
        ILProcessor echoIl = Body(echo);
        echoIl.Emit(OpCodes.Ldarg_0);
        echoIl.Emit(OpCodes.Ret);

        ArrayType array = new ArrayType(parameter);
        MethodDefinition makeArray = AddMethod(type, "MakeArray", MethodAttributes.Public | MethodAttributes.Static | MethodAttributes.HideBySig, array);
        makeArray.Parameters.Add(new ParameterDefinition("value", ParameterAttributes.None, parameter));
        ILProcessor arrayIl = Body(makeArray);
        arrayIl.Emit(OpCodes.Ldc_I4_1);
        arrayIl.Emit(OpCodes.Newarr, parameter);
        arrayIl.Emit(OpCodes.Dup);
        arrayIl.Emit(OpCodes.Ldc_I4_0);
        arrayIl.Emit(OpCodes.Ldarg_0);
        arrayIl.Emit(OpCodes.Stelem_Any, parameter);
        arrayIl.Emit(OpCodes.Ret);
        return type;
    }

    private static TypeDefinition AddCarrier(ModuleDefinition module, TypeDefinition attribute, TypeDefinition box)
    {
        return AddClass(module, "LazyAttributeCarrier", module.TypeSystem.Object,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
    }

    private static TypeDefinition AddRetryCarrier(ModuleDefinition module, TypeDefinition retryAttribute)
    {
        return AddClass(module, "LazyRetryCarrier", module.TypeSystem.Object,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
    }

    private static TypeDefinition AddMalformedCarrier(ModuleDefinition module)
    {
        return AddClass(module, "LazyMalformedCarrier", module.TypeSystem.Object,
            TypeAttributes.Class | TypeAttributes.Public | TypeAttributes.Sealed);
    }

    private static void AddMarker(TypeDefinition owner, TypeDefinition attribute, ModuleDefinition module, string name, TypeReference payload)
    {
        MethodReference constructor = AddConstructorReference(module, attribute, module.TypeSystem.String, module.ImportReference(typeof(Type)));
        var custom = new CustomAttribute(constructor);
        custom.ConstructorArguments.Add(new CustomAttributeArgument(module.TypeSystem.String, name));
        custom.ConstructorArguments.Add(new CustomAttributeArgument(module.ImportReference(typeof(Type)), payload));
        owner.CustomAttributes.Add(custom);
    }

    private static void AddRetry(TypeDefinition owner, TypeDefinition attribute, ModuleDefinition module, int marker)
    {
        MethodReference constructor = AddConstructorReference(module, attribute, module.TypeSystem.Int32);
        var custom = new CustomAttribute(constructor);
        custom.ConstructorArguments.Add(new CustomAttributeArgument(module.TypeSystem.Int32, marker));
        owner.CustomAttributes.Add(custom);
    }

    private static void AddMalformed(TypeDefinition owner, TypeDefinition attribute, ModuleDefinition module)
    {
        MethodReference constructor = AddConstructorReference(module, attribute, module.ImportReference(typeof(Type)), module.TypeSystem.Int32);
        const string validTypeName = "AssemblyShadow.R01B.LazyBox`1[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]";
        byte[] typeBytes = Encoding.UTF8.GetBytes(validTypeName);
        if (typeBytes.Length >= 128)
            throw new InvalidOperationException("unexpected constructed-generic type name length");
        // The Type fixed argument is valid; the second Int32 fixed argument is deliberately truncated.
        byte[] malformedBlob = new byte[2 + 1 + typeBytes.Length];
        malformedBlob[0] = 1;
        malformedBlob[1] = 0;
        malformedBlob[2] = (byte)typeBytes.Length;
        Buffer.BlockCopy(typeBytes, 0, malformedBlob, 3, typeBytes.Length);
        owner.CustomAttributes.Add(new CustomAttribute(constructor, malformedBlob));
    }

    private static TypeDefinition AddClass(ModuleDefinition module, string name, TypeReference baseType, TypeAttributes attributes)
    {
        var type = new TypeDefinition(Namespace, name, attributes, baseType);
        module.Types.Add(type);
        return type;
    }

    private static MethodDefinition AddMethod(TypeDefinition type, string name, MethodAttributes attributes, TypeReference returnType)
    {
        var method = new MethodDefinition(name, attributes, returnType);
        type.Methods.Add(method);
        return method;
    }

    private static ILProcessor Body(MethodDefinition method)
    {
        var body = new MethodBody(method);
        body.InitLocals = false;
        method.Body = body;
        return body.GetILProcessor();
    }

    private static TypeReference ClosedBox(ModuleDefinition module, TypeDefinition definition, TypeReference argument)
    {
        var instance = new GenericInstanceType(definition);
        instance.GenericArguments.Add(argument);
        return instance;
    }

    private static MethodReference AddConstructorReference(ModuleDefinition module, TypeDefinition type, params TypeReference[] parameters)
    {
        foreach (MethodDefinition method in type.Methods)
            if (method.Name == ".ctor" && method.Parameters.Count == parameters.Length)
                return method;
        var reference = new MethodReference(".ctor", module.TypeSystem.Void, type) { HasThis = true };
        foreach (TypeReference parameter in parameters)
            reference.Parameters.Add(new ParameterDefinition(parameter));
        return reference;
    }

    private static MethodReference AddConstructorReference(ModuleDefinition module, TypeDefinition type)
    {
        var reference = new MethodReference(".ctor", module.TypeSystem.Void, type) { HasThis = true };
        return reference;
    }

    private static TypeDefinition FindType(ModuleDefinition module, string name)
    {
        foreach (TypeDefinition type in module.Types)
            if (type.Name == name) return type;
        throw new InvalidOperationException("missing type " + name);
    }

    private static void Verify(string output)
    {
        using (AssemblyDefinition assembly = AssemblyDefinition.ReadAssembly(output))
        {
            ModuleDefinition module = assembly.MainModule;
            if (assembly.Name.Name != AssemblyName || assembly.Name.Version != new Version(1, 0, 0, 1) || module.Mvid != DeterministicMvid())
                throw new InvalidOperationException("generated fixture identity is not reproducible");
            foreach (string typeName in new[] { "LazyMarkerAttribute", "LazyRetryAttribute", "LazyMalformedAttribute", "ILazyContract`1", "IInheritedLazyContract",
                "LazyImplementation", "LazyBox`1", "LazyAttributeCarrier", "LazyRetryCarrier", "LazyMalformedCarrier", "LazyEntry" })
                FindType(module, typeName);
            VerifyVTableShape(module);
            if (FindType(module, "LazyAttributeCarrier").CustomAttributes.Count != 1 ||
                FindType(module, "LazyRetryCarrier").CustomAttributes.Count != 1 ||
                FindType(module, "LazyMalformedCarrier").CustomAttributes.Count != 1)
                throw new InvalidOperationException("generated fixture custom-attribute shape is incomplete");
        }
    }

    private static void VerifyVTableShape(ModuleDefinition module)
    {
        TypeDefinition contract = FindType(module, "ILazyContract`1");
        TypeDefinition inherited = FindType(module, "IInheritedLazyContract");
        TypeDefinition implementation = FindType(module, "LazyImplementation");
        VerifyMethodFlags(contract, "Echo", MethodAttributes.Public | MethodAttributes.Abstract |
            MethodAttributes.Virtual | MethodAttributes.HideBySig | MethodAttributes.NewSlot);
        MethodAttributes implementationFlags = MethodAttributes.Public | MethodAttributes.Final |
            MethodAttributes.Virtual | MethodAttributes.HideBySig | MethodAttributes.NewSlot;
        VerifyMethodFlags(implementation, "Echo", implementationFlags);
        VerifyMethodFlags(implementation, "Dispose", implementationFlags);
        string closedContract = ClosedBox(module, contract, module.TypeSystem.Int32).FullName;
        VerifyInterfaces(inherited, closedContract, typeof(IDisposable).FullName);
        VerifyInterfaces(implementation, inherited.FullName, closedContract, typeof(IDisposable).FullName);
    }

    private static void VerifyMethodFlags(TypeDefinition type, string name, MethodAttributes expected)
    {
        MethodDefinition found = null;
        foreach (MethodDefinition method in type.Methods)
        {
            if (method.Name != name) continue;
            if (found != null) throw new InvalidOperationException("duplicate fixture method " + type.Name + "." + name);
            found = method;
        }
        if (found == null || found.Attributes != expected || found.Overrides.Count != 0)
            throw new InvalidOperationException("fixture interface method differs from implicit C# shape: " + type.Name + "." + name);
    }

    private static void VerifyInterfaces(TypeDefinition type, params string[] expected)
    {
        if (type.Interfaces.Count != expected.Length)
            throw new InvalidOperationException("fixture interface closure is incomplete: " + type.Name);
        for (int index = 0; index < expected.Length; ++index)
            if (type.Interfaces[index].InterfaceType.FullName != expected[index])
                throw new InvalidOperationException("fixture interface closure differs from C# shape: " + type.Name);
    }

    private static MethodReference ImportMethod(this ModuleDefinition module, Type type, string name, Type returnType, params Type[] parameterTypes)
    {
        if (name == ".ctor")
        {
            var constructor = type.GetConstructor(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic,
                null, parameterTypes, null);
            if (constructor != null) return module.ImportReference(constructor);
        }
        foreach (var method in type.GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Static))
        {
            if (method.Name != name || method.GetParameters().Length != parameterTypes.Length || method.ReturnType != returnType) continue;
            bool matches = true;
            for (int index = 0; index < parameterTypes.Length; index++)
                if (method.GetParameters()[index].ParameterType != parameterTypes[index]) matches = false;
            if (matches) return module.ImportReference(method);
        }
        throw new InvalidOperationException("missing framework method " + type.FullName + "." + name);
    }

    private static Guid DeterministicMvid()
    {
        using (SHA256 hash = SHA256.Create())
        {
            byte[] digest = hash.ComputeHash(Encoding.UTF8.GetBytes("R01B-lazy-interpreter-fixture:mvid:v2-vtable-shape"));
            byte[] bytes = new byte[16];
            Buffer.BlockCopy(digest, 0, bytes, 0, bytes.Length);
            bytes[7] = (byte)((bytes[7] & 0x0f) | 0x40);
            bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
            return new Guid(bytes);
        }
    }
}
