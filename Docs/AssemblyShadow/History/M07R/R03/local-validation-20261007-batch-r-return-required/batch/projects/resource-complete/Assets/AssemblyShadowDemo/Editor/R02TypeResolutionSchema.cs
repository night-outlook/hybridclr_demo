using System;
using System.Collections.Generic;

namespace AssemblyShadowDemo.Editor
{
    // Independent wire inventory used by actual pre/post-link proof and host
    // interoperability checks. Never infer the accepted schema from DTO defaults.
    public static class R02TypeResolutionSchema
    {
        public const string ExtensionType = "HybridCLR.AssemblyShadowTypeResolutionInfo/R02Diagnostics";
        public static Dictionary<string, string> Fields()
        {
            return new Dictionary<string, string>(StringComparer.Ordinal)
            {
                { "schemaVersion", "System.Int32" },
                { "diagnosticsLevel", "System.Int32" },
                { "definitionSearches", "System.UInt64" },
                { "definitionRowsScanned", "System.UInt64" },
                { "admissionCacheHits", "System.UInt64" },
                { "admissionCacheMisses", "System.UInt64" },
                { "admissionProofAttempts", "System.UInt64" },
                { "admissionProofRejections", "System.UInt64" },
                { "admissionEntries", "System.UInt64" },
                { "admissionRetainedBytes", "System.UInt64" },
                { "admissionUnready", "System.UInt64" },
                { "baselineStateChecks", "System.UInt64" },
                { "fieldWorkspaceBuilds", "System.UInt64" },
                { "interfaceWorkspaceBuilds", "System.UInt64" },
                { "layoutCheckCalls", "System.UInt64" },
                { "counterpartCacheHits", "System.UInt64" },
                { "counterpartCacheMisses", "System.UInt64" },
                { "counterpartEntries", "System.UInt64" },
                { "absentCounterpartEntries", "System.UInt64" },
                { "cacheFixedBytes", "System.UInt64" },
                { "counterpartRetainedBytes", "System.UInt64" },
                { "genericContextChecks", "System.UInt64" },
                { "observationLockContentions", "System.UInt64" },
                { "observationMemoHits", "System.UInt64" },
                { "observationMemoTlsBytesPerThread", "System.UInt64" },
                { "counterStorageBytes", "System.UInt64" },
                { "counterThreadCapacity", "System.UInt64" },
                { "droppedCounterThreads", "System.UInt64" },
                { "counterSaturated", "System.Boolean" },
                { "counterCoverage", "System.String" },
                { "classesCoverage", "System.String" },
                { "memoryAccountingAvailable", "System.Boolean" },
                { "memoryAccountingScope", "System.String" },
            };
        }
    }
}
