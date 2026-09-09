using System;
using System.Collections.Generic;
using System.Linq;
using HybridCLR;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    // Retain every legacy field so only the exact dormant JsonUtility wire
    // object is accepted beside profile 2. A populated legacy pair is invalid.
    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataEncodingProfile
    {
        [Preserve] public int profileVersion, metadataIndexBits, metadataKindBits, sizeMultiplier, nativeBudgetCapabilityVersion;
        [Preserve] public int[] extraShiftBits, kindStrides;
        [Preserve] public uint[] indexMasks, initialCursors, kindLimits;
        [Preserve] public string nativeSourceRevision, nativeHelperSha256;
    }

    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataCapacityReport
    {
        [Preserve] public int schemaVersion, profileVersion, metadataIndexBits, metadataKindBits, nativeBudgetCapabilityVersion;
        [Preserve] public string nativeSourceRevision, nativeHelperSha256;
        [Preserve] public ShadowDormantCapacityEntry[] inputs, allocations;
        [Preserve] public uint[] cursorsBefore, cursorsAfter, remainingSlotsBefore, remainingSlotsAfter;
        [Preserve] public int requiredImages, acceptedImages, availableImages, availableImagesAtFailure, firstFailingIndex;
        [Preserve] public string firstFailingAssembly, failureReason, firstFailingReason, actualRemainingRuntime, runtimeCursorSource;
        [Preserve] public ulong firstFailingBytes, firstFailingSize;
        [Preserve] public int ordinaryAssemblyCount, aotCandidateAssemblyCount;
        [Preserve] public bool fits, ordinaryConsumptionIsEstimate, runtimeReserveMetadataBudget;
    }

    [Serializable, Preserve]
    public sealed class ShadowDormantCapacityEntry { [Preserve] public string name; }

    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataEncodingProfile2
    {
        [Preserve] public int schemaVersion;
        [Preserve] public int profileVersion;
        [Preserve] public int nativeBudgetCapabilityVersion;
        [Preserve] public string codecId;
        [Preserve] public int codecBits;
        [Preserve] public int invalidIndexSentinel;
        [Preserve] public int aotMaxIndex;
        [Preserve] public int minImageId;
        [Preserve] public int maximumImageCount;
        [Preserve] public int pageValues;
        [Preserve] public int usablePageCapacity;
        [Preserve] public int chargedPageCeiling;
        [Preserve] public int minimumFreePageMargin;
        [Preserve] public ulong maximumDllBytes;
        [Preserve] public ulong aggregateDllEnvelopeBytes;
        [Preserve] public string nativeSourceRevision;
        [Preserve] public string nativeCodecHeaderSha256;
    }

    [Serializable, Preserve]
    public sealed class ShadowPatchMetadataCapacityReport2
    {
        [Preserve] public int schemaVersion;
        [Preserve] public int profileVersion;
        [Preserve] public int nativeBudgetCapabilityVersion;
        [Preserve] public string nativeSourceRevision;
        [Preserve] public string nativeCodecHeaderSha256;
        [Preserve] public string codecId;
        [Preserve] public int codecBits;
        [Preserve] public int invalidIndexSentinel;
        [Preserve] public int aotMaxIndex;
        [Preserve] public int minImageId;
        [Preserve] public int maximumImageCount;
        [Preserve] public ulong maximumDllBytes;
        [Preserve] public int usablePageCapacity;
        [Preserve] public int chargedPageCeiling;
        [Preserve] public int minimumFreePageMargin;
        [Preserve] public int requiredImages;
        [Preserve] public int acceptedImages;
        [Preserve] public bool admissionAccepted;
        [Preserve] public bool fitsPreliminary;
        [Preserve] public bool finalPageFitKnown;
        [Preserve] public bool runtimeFinalizationRequired;
        [Preserve] public bool aggregateInputDllBytesInformational;
        [Preserve] public int firstFailingIndex;
        [Preserve] public string failureReason;
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
            ShadowPatchMetadataEncodingProfile2 profile2,
            ShadowPatchMetadataCapacityReport2 report2,
            string[] loadOrder,
            ShadowPatchMetadataAssembly[] closure,
            Func<string, byte[]> readVerifiedDll,
            out AssemblyShadowErrorCode code)
        {
            int profileVersion;
            Dictionary<string, long> verifiedSizes;
            bool declared = ValidateIfDeclared(nativeBudgetCapabilityVersion, profile, report, profile2, report2, loadOrder, closure, readVerifiedDll,
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
            ShadowPatchMetadataEncodingProfile2 profile2,
            ShadowPatchMetadataCapacityReport2 report2,
            string[] loadOrder,
            ShadowPatchMetadataAssembly[] closure,
            Func<string, byte[]> readVerifiedDll,
            out int profileVersion,
            out Dictionary<string, long> verifiedSizes)
        {
            profileVersion = 0;
            verifiedSizes = new Dictionary<string, long>(StringComparer.OrdinalIgnoreCase);
            bool declared = nativeBudgetCapabilityVersion != 0 || profile != null || report != null || profile2 != null || report2 != null ||
                (closure ?? new ShadowPatchMetadataAssembly[0]).Any(item => item != null && item.dllSize != 0);
            if (!declared)
                return false;

            Require(nativeBudgetCapabilityVersion == 2, "Metadata budget capability version is missing or unsupported.");
            Require((profile == null && report == null) || IsDormantLegacyPair(profile, report),
                "Legacy metadata profile fields cannot be mixed with profile 2.");
            Require(profile2 != null && profile2.schemaVersion == 2 && profile2.profileVersion == 2 &&
                profile2.nativeBudgetCapabilityVersion == 2 && profile2.codecId == "SparseSignedInt32" && profile2.codecBits == 32 &&
                profile2.invalidIndexSentinel == -1 && profile2.aotMaxIndex == int.MaxValue && profile2.minImageId == 1 &&
                profile2.maximumImageCount == 8192 && profile2.pageValues == 4096 && profile2.usablePageCapacity == 524287 &&
                profile2.chargedPageCeiling == 393215 && profile2.minimumFreePageMargin == 131072 &&
                profile2.maximumDllBytes == 33554432UL && profile2.aggregateDllEnvelopeBytes == 536870912UL &&
                !string.IsNullOrWhiteSpace(profile2.nativeSourceRevision) && IsSha256(profile2.nativeCodecHeaderSha256),
                "Metadata encoding profile capability is missing or unsupported.");
            Require(report2 != null && report2.schemaVersion == 2 && report2.profileVersion == 2 &&
                report2.nativeBudgetCapabilityVersion == 2 && report2.codecId == profile2.codecId &&
                report2.codecBits == profile2.codecBits && report2.invalidIndexSentinel == profile2.invalidIndexSentinel &&
                report2.aotMaxIndex == profile2.aotMaxIndex && report2.minImageId == profile2.minImageId &&
                report2.maximumImageCount == profile2.maximumImageCount && report2.maximumDllBytes == profile2.maximumDllBytes &&
                report2.usablePageCapacity == profile2.usablePageCapacity && report2.chargedPageCeiling == profile2.chargedPageCeiling &&
                report2.minimumFreePageMargin == profile2.minimumFreePageMargin &&
                string.Equals(report2.nativeSourceRevision, profile2.nativeSourceRevision, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(report2.nativeCodecHeaderSha256, profile2.nativeCodecHeaderSha256, StringComparison.OrdinalIgnoreCase) &&
                report2.admissionAccepted && report2.fitsPreliminary && !report2.finalPageFitKnown &&
                report2.runtimeFinalizationRequired && report2.aggregateInputDllBytesInformational &&
                report2.firstFailingIndex == -1 && report2.failureReason == "None",
                "Metadata capacity report does not advertise a fitting version 2 runtime reservation.");
            Require(loadOrder != null && loadOrder.Length > 0, "Metadata reservation load order is missing.");
            Require(closure != null && closure.Length == loadOrder.Length, "Metadata reservation closure does not match load order.");
            Require(readVerifiedDll != null, "Verified DLL reader is required for metadata reservation.");
            Require(report2.requiredImages == loadOrder.Length && report2.acceptedImages == loadOrder.Length,
                "Metadata capacity report image count does not match load order.");

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

            profileVersion = profile2.profileVersion;
            return true;
        }

        public static AssemblyShadowErrorCode Reserve(int profileVersion, IEnumerable<string> orderedNames, IDictionary<string, long> verifiedSizes)
        {
            Require(profileVersion == 2, "Metadata reservation profile version is unsupported.");
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

        private static bool IsDormantLegacyPair(ShadowPatchMetadataEncodingProfile profile, ShadowPatchMetadataCapacityReport report)
        {
            return profile != null && report != null && profile.profileVersion == 1 && profile.metadataIndexBits == 22 &&
                profile.metadataKindBits == 2 && profile.sizeMultiplier == 4 && profile.nativeBudgetCapabilityVersion == 1 &&
                Empty(profile.nativeSourceRevision) && Empty(profile.nativeHelperSha256) &&
                Same(profile.extraShiftBits, new[] { 6, 4, 2, 0 }) && Same(profile.kindStrides, new[] { 64, 16, 4, 1 }) &&
                Same(profile.indexMasks, new uint[] { 268435455, 67108863, 16777215, 4194303 }) &&
                Same(profile.initialCursors, new uint[] { 64, 0, 0, 0 }) && Same(profile.kindLimits, new uint[] { 256, 256, 256, 255 }) &&
                report.schemaVersion == 1 && report.profileVersion == 1 && report.metadataIndexBits == 22 &&
                report.metadataKindBits == 2 && report.nativeBudgetCapabilityVersion == 1 &&
                Empty(report.nativeSourceRevision) && Empty(report.nativeHelperSha256) &&
                report.inputs != null && report.inputs.Length == 0 && report.allocations != null && report.allocations.Length == 0 &&
                ZeroCursors(report.cursorsBefore) && ZeroCursors(report.cursorsAfter) &&
                ZeroCursors(report.remainingSlotsBefore) && ZeroCursors(report.remainingSlotsAfter) &&
                report.requiredImages == 0 && report.acceptedImages == 0 && report.availableImages == 0 &&
                report.availableImagesAtFailure == 0 && !report.fits && report.firstFailingIndex == -1 &&
                Empty(report.firstFailingAssembly) && report.firstFailingBytes == 0 && report.firstFailingSize == 0 &&
                report.failureReason == "None" && report.firstFailingReason == "None" &&
                report.ordinaryAssemblyCount == 0 && report.aotCandidateAssemblyCount == 0 &&
                report.actualRemainingRuntime == "NotKnown" && report.runtimeCursorSource == "BaselineOrdinaryPlan" &&
                report.ordinaryConsumptionIsEstimate && !report.runtimeReserveMetadataBudget;
        }

        private static bool Empty(string value) { return string.IsNullOrEmpty(value); }
        private static bool Same<T>(T[] actual, T[] expected) { return actual != null && actual.SequenceEqual(expected); }
        private static bool ZeroCursors(uint[] values) { return values != null && values.Length == 4 && values.All(value => value == 0); }

        private static void Require(bool condition, string message)
        {
            if (!condition)
                throw new InvalidOperationException(message);
        }

        private static bool IsSha256(string value)
        {
            if (value == null || value.Length != 64) return false;
            for (int index = 0; index < value.Length; ++index)
            {
                char c = value[index];
                if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
            }
            return true;
        }
    }
}
