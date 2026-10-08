using System;
using System.IO;
using UnityEditor.Build;

namespace AssemblyShadowDemo.Editor
{
    internal static class GeneratePatchVariant
    {
        internal const string Define = "ASSEMBLY_SHADOW_P01";

        internal static void RequireVariantSource()
        {
            string source = Path.Combine(M01Paths.Root, "AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs");
            if (!File.Exists(source) || File.ReadAllText(source).IndexOf("PATCH-P01-INTERNAL", StringComparison.Ordinal) < 0)
                throw new BuildFailedException("P01 source variant marker is missing.");
        }
    }
}
