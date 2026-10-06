using System;
using System.Runtime.CompilerServices;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>Read-only H1 count observations supplied by the diagnostic native bridge.</summary>
    [Preserve]
    public static class H1CountNativeDiagnostics
    {
        [Preserve]
        public static H1CountNativeDiagnosticSnapshot Read()
        {
#if UNITY_EDITOR || !ENABLE_IL2CPP
            throw new NotSupportedException("H1 count diagnostics require a native IL2CPP Player; Editor and Mono execution are unsupported.");
#else
            string json;
            AssemblyShadowErrorCode code = GetSnapshot(out json);
            if (code != AssemblyShadowErrorCode.Success)
                throw new InvalidOperationException("H1 count diagnostics failed with native status " + code + " (" + (int)code + ").");
            return Parse(json);
#endif
        }

        /// <summary>Returns the authenticated native snapshot without invoking JsonUtility.</summary>
        /// <remarks>The startup gateway uses this diagnostic-only path before Unity services exist.</remarks>
        [Preserve]
        internal static string ReadRaw()
        {
#if UNITY_EDITOR || !ENABLE_IL2CPP
            throw new NotSupportedException("H1 count diagnostics require a native IL2CPP Player; Editor and Mono execution are unsupported.");
#else
            string json;
            AssemblyShadowErrorCode code = GetSnapshot(out json);
            if (code != AssemblyShadowErrorCode.Success || string.IsNullOrEmpty(json))
                throw new InvalidOperationException("H1 count diagnostics failed with native status " + code + " (" + (int)code + ").");
            return json;
#endif
        }

        /// <summary>Parses and validates one native diagnostic snapshot.</summary>
        [Preserve]
        public static H1CountNativeDiagnosticSnapshot Parse(string json)
        {
            if (string.IsNullOrEmpty(json))
                throw new ArgumentException("H1 count diagnostics JSON must not be null or empty.", nameof(json));
            H1CountNativeDiagnosticsJsonReader.Validate(json);

            H1CountNativeDiagnosticSnapshot value = JsonUtility.FromJson<H1CountNativeDiagnosticSnapshot>(json);
            if (value == null)
                throw new FormatException("H1 count diagnostics JSON did not produce a snapshot.");
            value.Validate();
            return value;
        }

#if UNITY_EDITOR || !ENABLE_IL2CPP
        [Preserve]
        private static AssemblyShadowErrorCode GetSnapshot(out string json)
        {
            json = null;
            throw new NotSupportedException("H1 count diagnostics require a native IL2CPP Player; Editor and Mono execution are unsupported.");
        }
#else
        [Preserve, MethodImpl(MethodImplOptions.InternalCall)]
        private static extern AssemblyShadowErrorCode GetSnapshot(out string json);
#endif
    }

    [Serializable, Preserve]
    public sealed class H1CountNativeDiagnosticSnapshot
    {
        [Preserve] public int schemaVersion;
        [Preserve] public string kind;
        [Preserve] public bool diagnosticOnly;
        [Preserve] public bool featureEnabled;
        [Preserve] public string featureMode;
        [Preserve] public ulong reservedPages;
        [Preserve] public ulong mappedPages;
        [Preserve] public ulong reservationCount;
        [Preserve] public ulong nextImageId;
        [Preserve] public ulong nextPageSlot;
        [Preserve] public ulong ordinaryAllocatedCount;
        [Preserve] public ulong shadowAllocatedCount;
        [Preserve] public ulong reservedImageCount;
        [Preserve] public H1CountNativeAssemblyIdentity[] logicalAssemblies;
        [Preserve] public H1CountNativeAssemblyIdentity[] physicalAssemblies;
        [Preserve] public H1CountNativeAssemblyIdentity[] publishedInterpreterImages;

        internal void Validate()
        {
            if (schemaVersion != 1)
                throw new FormatException("Unsupported H1 count diagnostics schema version.");
            if (kind != "H1CountNativeDiagnostics")
                throw new FormatException("Unexpected H1 count diagnostics kind.");
            if (!diagnosticOnly)
                throw new FormatException("H1 count diagnostics must be diagnostic-only.");
            if (featureMode != "AssemblyShadowOn" && featureMode != "AssemblyShadowOff")
                throw new FormatException("Unknown H1 count diagnostics feature mode.");
            if (featureEnabled != (featureMode == "AssemblyShadowOn"))
                throw new FormatException("H1 count diagnostics feature mode is inconsistent.");
            if (mappedPages > reservedPages)
                throw new FormatException("H1 count diagnostics mapped pages exceed reserved pages.");
            if (logicalAssemblies == null || physicalAssemblies == null || publishedInterpreterImages == null)
                throw new FormatException("H1 count diagnostics assembly inventories are unavailable.");
            ValidateIdentities(logicalAssemblies, false);
            ValidateIdentities(physicalAssemblies, false);
            ValidateIdentities(publishedInterpreterImages, true);
        }

        private static void ValidateIdentities(H1CountNativeAssemblyIdentity[] identities, bool publishedOnly)
        {
            for (int i = 0; i < identities.Length; ++i)
            {
                H1CountNativeAssemblyIdentity identity = identities[i];
                if (identity == null || string.IsNullOrEmpty(identity.nativeAssemblyId) ||
                    string.IsNullOrEmpty(identity.nativeImageId) || string.IsNullOrEmpty(identity.name) ||
                    string.IsNullOrEmpty(identity.fullName) || string.IsNullOrEmpty(identity.identityKey) ||
                    string.IsNullOrEmpty(identity.imageKind))
                    throw new FormatException("H1 count diagnostics contains an incomplete native identity.");
                if (identity.imageKind != "Aot" && identity.imageKind != "Interpreter")
                    throw new FormatException("H1 count diagnostics contains an unknown image kind.");
                if (identity.imageKind == "Aot" && identity.imageId != 0)
                    throw new FormatException("AOT identity unexpectedly has an interpreter image ID.");
                if (identity.imageKind == "Interpreter" && identity.imageId == 0)
                    throw new FormatException("Interpreter identity is missing its image ID.");
                if (identity.mvidAvailable != !string.IsNullOrEmpty(identity.mvid))
                    throw new FormatException("H1 count diagnostics MVID availability disagrees with its value.");
                if (publishedOnly && (!identity.published || identity.imageKind != "Interpreter"))
                    throw new FormatException("Published image inventory contains a non-published/non-interpreter identity.");
            }
        }
    }

    [Serializable, Preserve]
    public sealed class H1CountNativeAssemblyIdentity
    {
        [Preserve] public string nativeAssemblyId;
        [Preserve] public string nativeImageId;
        [Preserve] public string name;
        [Preserve] public string fullName;
        [Preserve] public int versionMajor;
        [Preserve] public int versionMinor;
        [Preserve] public int versionBuild;
        [Preserve] public int versionRevision;
        [Preserve] public string culture;
        [Preserve] public uint flags;
        [Preserve] public string publicKeyToken;
        [Preserve] public bool mvidAvailable;
        [Preserve] public string mvid;
        [Preserve] public string imageKind;
        [Preserve] public uint imageId;
        [Preserve] public bool published;
        [Preserve] public string identityKey;
    }
}
