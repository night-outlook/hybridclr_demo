using System;
using System.Collections.Generic;
using System.Linq;
using HybridCLR;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataEncodingProfile
    {
        [Preserve] public int profileVersion;
        [Preserve] public int nativeBudgetCapabilityVersion;
    }

    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataCapacityReport
    {
        [Preserve] public int profileVersion;
        [Preserve] public int nativeBudgetCapabilityVersion;
        [Preserve] public int requiredImages;
        [Preserve] public bool fits;
        [Preserve] public bool runtimeReserveMetadataBudget;
    }

    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataAssembly
    {
        [Preserve] public string name;
        [Preserve] public ulong dllSize;
    }

    [Preserve]
    public static class ShadowPatchMetadataReservation
    {
        public static bool ReserveIfDeclared(
            int nativeBudgetCapabilityVersion,
            ShadowPatchMetadataEncodingProfile profile,
            ShadowPatchMetadataCapacityReport report,
            string[] loadOrder,
            ShadowPatchMetadataAssembly[] closure,
            Func<string, byte[]> readVerifiedDll,
            out AssemblyShadowErrorCode code)
        {
            int profileVersion;
            Dictionary<string, long> verifiedSizes;
            bool declared = ValidateIfDeclared(nativeBudgetCapabilityVersion, profile, report, loadOrder, closure, readVerifiedDll,
                out profileVersion, out verifiedSizes);
            code = AssemblyShadowErrorCode.Success;
            if (!declared)
                return false;

            code = Reserve(profileVersion, loadOrder, verifiedSizes);
            return true;
        }

        public static bool ValidateIfDeclared(
            int nativeBudgetCapabilityVersion,
            ShadowPatchMetadataEncodingProfile profile,
            ShadowPatchMetadataCapacityReport report,
            string[] loadOrder,
            ShadowPatchMetadataAssembly[] closure,
            Func<string, byte[]> readVerifiedDll,
            out int profileVersion,
            out Dictionary<string, long> verifiedSizes)
        {
            profileVersion = 0;
            verifiedSizes = new Dictionary<string, long>(StringComparer.OrdinalIgnoreCase);
            bool declared = nativeBudgetCapabilityVersion != 0 || profile != null || report != null ||
                (closure ?? new ShadowPatchMetadataAssembly[0]).Any(item => item != null && item.dllSize != 0);
            if (!declared)
                return false;

            Require(nativeBudgetCapabilityVersion == 1, "Metadata budget capability version is missing or unsupported.");
            Require(profile != null && profile.profileVersion == 1 && profile.nativeBudgetCapabilityVersion == 1,
                "Metadata encoding profile capability is missing or unsupported.");
            Require(report != null && report.profileVersion == 1 && report.nativeBudgetCapabilityVersion == 1 &&
                report.runtimeReserveMetadataBudget && report.fits,
                "Metadata capacity report does not advertise a fitting version 1 runtime reservation.");
            Require(loadOrder != null && loadOrder.Length > 0, "Metadata reservation load order is missing.");
            Require(closure != null && closure.Length == loadOrder.Length, "Metadata reservation closure does not match load order.");
            Require(readVerifiedDll != null, "Verified DLL reader is required for metadata reservation.");
            Require(report.requiredImages == loadOrder.Length, "Metadata capacity report image count does not match load order.");

            var entries = new Dictionary<string, ShadowPatchMetadataAssembly>(StringComparer.OrdinalIgnoreCase);
            foreach (ShadowPatchMetadataAssembly entry in closure)
            {
                Require(entry != null && !string.IsNullOrWhiteSpace(entry.name) && entry.dllSize > 0,
                    "Metadata reservation closure contains an invalid assembly entry.");
                Require(!entries.ContainsKey(entry.name), "Metadata reservation closure contains duplicate assembly names.");
                entries.Add(entry.name, entry);
            }

            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string name in loadOrder)
            {
                Require(!string.IsNullOrWhiteSpace(name) && seen.Add(name), "Metadata reservation load order contains a duplicate or empty name.");
                ShadowPatchMetadataAssembly entry;
                Require(entries.TryGetValue(name, out entry), "Metadata reservation load order is not the manifest closure: " + name);
                byte[] dll = readVerifiedDll(name);
                Require(dll != null && dll.LongLength > 0, "Verified DLL bytes are missing: " + name);
                Require((ulong)dll.LongLength == entry.dllSize, "Verified DLL length differs from manifest declaration: " + name);
                verifiedSizes.Add(name, dll.LongLength);
            }

            profileVersion = profile.profileVersion;
            return true;
        }

        public static AssemblyShadowErrorCode Reserve(int profileVersion, IEnumerable<string> orderedNames, IDictionary<string, long> verifiedSizes)
        {
            Require(profileVersion == 1, "Metadata reservation profile version is unsupported.");
            Require(orderedNames != null && verifiedSizes != null, "Metadata reservation inputs are missing.");
            var sizes = new List<long>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string name in orderedNames)
            {
                Require(!string.IsNullOrWhiteSpace(name) && seen.Add(name), "Metadata reservation order contains a duplicate or empty name.");
                long size;
                Require(verifiedSizes.TryGetValue(name, out size) && size > 0, "Metadata reservation order is not the verified manifest closure: " + name);
                sizes.Add(size);
            }
            Require(sizes.Count > 0, "Metadata reservation order is empty.");
            return AssemblyShadowRuntime.ReserveMetadataBudget(sizes.ToArray(), profileVersion);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition)
                throw new InvalidOperationException(message);
        }
    }
}
