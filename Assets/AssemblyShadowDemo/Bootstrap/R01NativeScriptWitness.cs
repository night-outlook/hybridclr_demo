using System;
using System.Runtime.InteropServices;
using System.Text;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// R01 negative witness for the public native class-resolution route used by
    /// Unity's script catalog. Call before Configure, while the assembly snapshot
    /// still identifies physical baseline assemblies. This does not load a prefab.
    /// </summary>
    public static class R01NativeScriptWitness
    {
        private const string CandidateImageName = "AssemblyA.Implementation.Internal.dll";
        private const string CandidateNamespace = "AssemblyA.Implementation.Internal";
        private const string CandidateTypeName = "InternalEntry";

        public static IntPtr ResolveCandidate()
        {
#if UNITY_STANDALONE_OSX && ENABLE_IL2CPP && !UNITY_EDITOR
            IntPtr domain = NativeDomainGet();
            if (domain == IntPtr.Zero)
                throw new InvalidOperationException("R01 native witness requires an initialized IL2CPP domain.");

            UIntPtr nativeCount;
            IntPtr assemblies = NativeDomainGetAssemblies(domain, out nativeCount);
            ulong count = nativeCount.ToUInt64();
            // Marshal.ReadIntPtr accepts an Int32 byte offset. Bound the complete
            // traversal before reading any element, without assuming an assembly count.
            if (assemblies == IntPtr.Zero || count == 0 || count > (ulong)(int.MaxValue / IntPtr.Size))
                throw new InvalidOperationException("R01 native witness received an invalid assembly snapshot.");

            byte[] expectedImageName = Encoding.UTF8.GetBytes(CandidateImageName);
            IntPtr candidateImage = IntPtr.Zero;
            for (int index = 0; index < (int)count; ++index)
            {
                IntPtr assembly = Marshal.ReadIntPtr(assemblies, checked(index * IntPtr.Size));
                if (assembly == IntPtr.Zero)
                    throw new InvalidOperationException("R01 native witness received a null assembly.");
                IntPtr image = NativeAssemblyGetImage(assembly);
                if (image == IntPtr.Zero)
                    throw new InvalidOperationException("R01 native witness received a null image.");
                if (!IsExactUtf8Name(NativeImageGetName(image), expectedImageName))
                    continue;
                if (candidateImage != IntPtr.Zero)
                    throw new InvalidOperationException("R01 native witness found an ambiguous candidate image.");
                candidateImage = image;
            }
            if (candidateImage == IntPtr.Zero)
                throw new InvalidOperationException("R01 native witness could not find the physical candidate image.");

            byte[] namespaceBytes = Encoding.UTF8.GetBytes(CandidateNamespace + "\0");
            byte[] typeBytes = Encoding.UTF8.GetBytes(CandidateTypeName + "\0");
            IntPtr namespaceUtf8 = IntPtr.Zero;
            IntPtr typeUtf8 = IntPtr.Zero;
            try
            {
                namespaceUtf8 = Marshal.AllocHGlobal(namespaceBytes.Length);
                Marshal.Copy(namespaceBytes, 0, namespaceUtf8, namespaceBytes.Length);
                typeUtf8 = Marshal.AllocHGlobal(typeBytes.Length);
                Marshal.Copy(typeBytes, 0, typeUtf8, typeBytes.Length);
                // The first candidate type lookup occurs here, through the same
                // exported API as Unity, without constructing a managed Type.
                IntPtr klass = NativeClassFromName(candidateImage, namespaceUtf8, typeUtf8);
                if (klass == IntPtr.Zero)
                    throw new InvalidOperationException("R01 native witness did not resolve InternalEntry.");
                return klass;
            }
            finally
            {
                if (typeUtf8 != IntPtr.Zero)
                    Marshal.FreeHGlobal(typeUtf8);
                if (namespaceUtf8 != IntPtr.Zero)
                    Marshal.FreeHGlobal(namespaceUtf8);
            }
#else
            throw new PlatformNotSupportedException("R01 native witness requires a macOS IL2CPP Player.");
#endif
        }

#if UNITY_STANDALONE_OSX && ENABLE_IL2CPP && !UNITY_EDITOR
        private static bool IsExactUtf8Name(IntPtr name, byte[] expected)
        {
            if (name == IntPtr.Zero)
                return false;
            for (int index = 0; index < expected.Length; ++index)
                if (Marshal.ReadByte(name, index) != expected[index])
                    return false;
            return Marshal.ReadByte(name, expected.Length) == 0;
        }

        // Unity 2022.3's IL2CPP generator internalizes __Internal imports into
        // direct extern C calls; these do not use the runtime plugin resolver.
        [DllImport("__Internal", EntryPoint = "il2cpp_domain_get", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeDomainGet();

        [DllImport("__Internal", EntryPoint = "il2cpp_domain_get_assemblies", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeDomainGetAssemblies(IntPtr domain, out UIntPtr count);

        [DllImport("__Internal", EntryPoint = "il2cpp_assembly_get_image", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeAssemblyGetImage(IntPtr assembly);

        [DllImport("__Internal", EntryPoint = "il2cpp_image_get_name", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeImageGetName(IntPtr image);

        [DllImport("__Internal", EntryPoint = "il2cpp_class_from_name", ExactSpelling = true, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeClassFromName(IntPtr image, IntPtr namespaze, IntPtr name);
#endif
    }
}
