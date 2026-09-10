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
        }
    }
}
