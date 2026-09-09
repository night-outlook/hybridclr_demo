using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Preserve]
    public static class R01BCapacityProbe
    {
        private const int RequiredImages = 8192;
        private const long MaximumDllBytes = 33554432;
        private const long AggregateDllBytes = 536870912;
        private const ulong UsablePageCapacity = 524287;
        private const ulong MinimumFreePageMargin = 131072;
        private static Result active;
        private static string output;

        public static IEnumerator RunAndWriteCoroutine(string baselineBuildId, string runtimeAbiHash, Action<int> completed)
        {
            completed(RunAndWrite(baselineBuildId, runtimeAbiHash));
            yield break;
        }

        private static int RunAndWrite(string baselineBuildId, string runtimeAbiHash)
        {
            output = Path.GetFullPath(Argument("-shadowR01BResult", Path.Combine(
                Application.persistentDataPath, "AssemblyShadowTests/r01b-capacity.json")));
            active = new Result {
                schemaVersion = 1, kind = "R01BCapacityPlayerResult", milestone = "R01B",
                result = "Failed", baselineBuildId = baselineBuildId, runtimeAbiHash = runtimeAbiHash,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(),
                buildGuid = Application.buildGUID, processId = Process.GetCurrentProcess().Id,
                memoryMeasurement = R01BProcessMemory.Measurement,
                resultPath = output, il2cpp = IsIl2CppPlayer(),
                mixedManifestPath = "", mixedManifestSha256 = "", mixedCorpusRoot = "",
                scenario = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01BMixed") >= 0
                    ? "MixedShadowRetainedFailures" : "OrdinaryEnvelope",
                retainedFailureExceptions = new string[0]
            };
            try
            {
                Require(active.il2cpp, "R01B capacity acceptance requires an IL2CPP Player.");
                Require(!File.Exists(output), "R01B result path must be immutable.");
                bool mixed = active.scenario == "MixedShadowRetainedFailures";
                string manifestPath = Path.GetFullPath(Argument(mixed ? "-shadowR01BMixedManifest" : "-shadowR01BManifest", ""));
                string corpusRoot = Path.GetFullPath(Argument(mixed ? "-shadowR01BMixedCorpus" : "-shadowR01BCorpus", ""));
                Require(File.Exists(manifestPath) && Directory.Exists(corpusRoot), "R01B workload inputs are missing.");
                active.manifestPath = manifestPath;
                active.manifestSha256 = Hash(File.ReadAllBytes(manifestPath));
                WorkloadManifest manifest;
                int expectedShadowImageCount = 0;
                if (mixed)
                {
                    MixedWorkloadManifest mixedManifest = JsonUtility.FromJson<MixedWorkloadManifest>(File.ReadAllText(manifestPath));
                    ValidateMixedManifest(mixedManifest);
                    manifest = mixedManifest.ToWorkloadManifest();
                    expectedShadowImageCount = mixedManifest.shadow.imageCount;
                    active.mixedManifestPath = manifestPath;
                    active.mixedManifestSha256 = active.manifestSha256;
                    active.mixedCorpusRoot = corpusRoot;
                    active.shadowDllBytes = mixedManifest.shadow.validDllBytes;
                    active.validDllBytes = mixedManifest.totals.validDllBytes;
                    active.retainedFailureInputBytes = mixedManifest.failedInputBytes;
                    VerifyMixedShadowEvidence(mixedManifest, baselineBuildId, runtimeAbiHash);
                }
                else
                {
                    manifest = JsonUtility.FromJson<WorkloadManifest>(File.ReadAllText(manifestPath));
                    ValidateManifest(manifest);
                    active.validDllBytes = AggregateDllBytes;
                }
                active.corpusRoot = corpusRoot;
                var initialMemory = R01BProcessMemory.Capture();
                active.workingSetBytesBefore = initialMemory.ResidentBytes;
                active.maximumWorkingSetBytes = initialMemory.PeakResidentBytes;

                active.initial = Capacity(new long[0]);
                if (mixed)
                {
                    Require(active.initial.lifetimeReservedImageCount == (ulong)expectedShadowImageCount && active.initial.shadowAllocatedCount == (ulong)expectedShadowImageCount &&
                        active.initial.ordinaryAllocatedCount == 0 &&
                        active.initial.reservedShadowImageCount == active.initial.shadowAllocatedCount,
                        "The mixed capacity scenario did not start after the five-image committed Shadow closure.");
                    var failures = new List<string>();
                    for (int attempt = 0; attempt != 3; ++attempt)
                    {
                        bool failed = false;
                        try { Assembly.Load(new byte[] { 0x42, 0x41, 0x44, (byte)attempt }); }
                        catch (Exception error)
                        {
                            failed = true;
                            failures.Add(error.GetType().FullName + ": " + error.Message);
                        }
                        Require(failed, "Malformed ordinary DLL did not fail at retained-reservation attempt " + attempt + ".");
                        CapacityResult checkpoint = Capacity(new long[0]);
                        Require(checkpoint.lifetimeReservedImageCount == active.initial.lifetimeReservedImageCount + (ulong)attempt + 1,
                            "Failed ordinary load did not permanently consume one image identity.");
                    }
                    active.retainedFailureExceptions = failures.ToArray();
                    active.retainedFailureCount = failures.Count;
                }
                else
                {
                    Require(active.initial.lifetimeReservedImageCount == 0 && active.initial.remainingImageCount == RequiredImages &&
                        active.initial.ordinaryAllocatedCount == 0 && active.initial.shadowAllocatedCount == 0 &&
                        active.initial.reservedShadowImageCount == 0 && active.initial.reservedPages == 0 && active.initial.mappedPages == 0,
                        "The ordinary capacity scenario did not start with a fresh interpreter ledger.");
                }

                active.afterRetainedFailures = Capacity(new long[0]);
                Require(active.afterRetainedFailures.lifetimeReservedImageCount ==
                    active.initial.lifetimeReservedImageCount + (ulong)active.retainedFailureCount &&
                    active.afterRetainedFailures.remainingImageCount == (ulong)RequiredImages - active.afterRetainedFailures.lifetimeReservedImageCount &&
                    active.afterRetainedFailures.reservedShadowImageCount == active.initial.reservedShadowImageCount &&
                    active.afterRetainedFailures.reservedPages >= active.initial.reservedPages + (ulong)active.retainedFailureCount &&
                    active.afterRetainedFailures.mappedPages == active.initial.mappedPages,
                    "Retained failures did not preserve the expected image/page ledger.");
                active.validImagesToLoad = checked(RequiredImages - (int)active.afterRetainedFailures.lifetimeReservedImageCount);
                Require(active.validImagesToLoad > 4096, "Mixed setup left too few valid ordinary images for boundary coverage.");
                long[] orderedSizes = manifest.assemblies.Take(active.validImagesToLoad).Select(item => item.sizeBytes).ToArray();
                active.before = Capacity(orderedSizes);
                Require(active.before.lifetimeReservedImageCount == active.afterRetainedFailures.lifetimeReservedImageCount &&
                    active.before.remainingImageCount == (ulong)active.validImagesToLoad && active.before.fitsPreliminary &&
                    active.before.requiredImages == (ulong)active.validImagesToLoad &&
                    active.before.acceptedImages == (ulong)active.validImagesToLoad,
                    "The capacity Player did not admit all remaining valid ordinary identities.");

                var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                var loadedAssemblies = new List<Assembly>(active.validImagesToLoad);
                Stopwatch timer = Stopwatch.StartNew();
                for (int index = 0; index < active.validImagesToLoad; ++index)
                {
                    WorkloadAssembly item = manifest.assemblies[index];
                    string path = Confined(corpusRoot, item.file);
                    byte[] bytes = File.ReadAllBytes(path);
                    Require(bytes.LongLength == item.sizeBytes && Hash(bytes) == item.sha256,
                        "R01B workload DLL differs from its manifest: " + item.file);
                    Assembly loaded = Assembly.Load(bytes);
                    string actualName = loaded.GetName().Name;
                    Require(actualName == item.name && names.Add(actualName),
                        "R01B ordinary load returned a duplicate or wrong identity at " + index + ".");
                    VerifyMethods(loaded, item, index, false);
                    loadedAssemblies.Add(loaded);
                    active.loadedImages = index + 1;
                    active.invokedImages = index + 1;
                    active.loadedDllBytes += bytes.LongLength;
                    active.maximumWorkingSetBytes = Math.Max(active.maximumWorkingSetBytes, R01BProcessMemory.Capture().PeakResidentBytes);
                    if (active.afterRetainedFailures.lifetimeReservedImageCount + (ulong)index + 1 == RequiredImages - 1)
                    {
                        active.at8191 = Capacity(new[] { manifest.assemblies[index + 1].sizeBytes });
                        Require(active.at8191.lifetimeReservedImageCount == RequiredImages - 1 && active.at8191.remainingImageCount == 1 &&
                            active.at8191.fitsPreliminary && active.at8191.requiredImages == 1 && active.at8191.acceptedImages == 1,
                            "R01B 8191 checkpoint did not admit exactly one final identity.");
                    }
                }
                timer.Stop();
                active.loadMilliseconds = timer.ElapsedMilliseconds;
                Require(active.loadedImages == active.validImagesToLoad &&
                    active.loadedDllBytes == manifest.assemblies.Take(active.validImagesToLoad).Sum(item => item.sizeBytes) &&
                    (mixed ? active.loadedDllBytes + active.shadowDllBytes == AggregateDllBytes : active.loadedDllBytes == AggregateDllBytes),
                    "R01B Player did not load the declared scenario workload.");

                active.after = Capacity(new long[0]);
                Require(active.after.lifetimeReservedImageCount == RequiredImages && active.after.remainingImageCount == 0 &&
                    active.after.fitsPreliminary && active.after.requiredImages == 0 && active.after.acceptedImages == 0,
                    "R01B lifetime ledger did not retain exactly 8192 interpreter identities.");
                Require(active.after.reservedPages <= 393215 && active.after.freeUsablePages >= MinimumFreePageMargin,
                    "R01B loaded workload did not preserve the 25% usable page margin.");

                bool rejected = false;
                string overflowPath = Path.GetFullPath(Argument("-shadowR01BOverflowDll", ""));
                string overflowName = Argument("-shadowR01BOverflowName", "");
                string overflowHash = Argument("-shadowR01BOverflowSha256", "");
                Require(File.Exists(overflowPath) && !string.IsNullOrWhiteSpace(overflowName) && IsHash(overflowHash),
                    "The distinct 8193rd assembly evidence is missing.");
                byte[] overflowBytes = File.ReadAllBytes(overflowPath);
                Require(Hash(overflowBytes) == overflowHash && overflowBytes.LongLength > 0 && overflowBytes.LongLength <= MaximumDllBytes &&
                    !names.Contains(overflowName) && manifest.assemblies.All(item => item.sha256 != overflowHash),
                    "The 8193rd assembly input is not distinct and hash-bound.");
                active.overflowPath = overflowPath;
                active.overflowName = overflowName;
                active.overflowSha256 = overflowHash;
                active.overflowDllBytes = overflowBytes.LongLength;
                try
                {
                    Assembly.Load(overflowBytes);
                }
                catch (Exception error)
                {
                    rejected = true;
                    active.limitException = error.GetType().FullName + ": " + error.Message;
                    Require(error.GetType().FullName == "System.ExecutionEngineException" &&
                        error.Message.Contains("InterpreterImage::AllocImageIndex failed"),
                        "The 8193rd load failed for a reason other than the image limit.");
                }
                Require(rejected, "The 8193rd process-lifetime interpreter image was not rejected.");
                active.afterRejected = Capacity(new[] { overflowBytes.LongLength });
                Require(!active.afterRejected.fitsPreliminary && active.afterRejected.failureReason == "ImageLimit" &&
                    active.afterRejected.acceptedImages == 0 && active.afterRejected.firstFailingIndex == 0 &&
                    active.afterRejected.lifetimeReservedImageCount == RequiredImages,
                    "The 8193rd rejection did not preserve the all-or-nothing lifetime ledger.");
                foreach (int index in new[] { 0, 4095, 4096, active.validImagesToLoad - 1 }.Distinct())
                {
                    VerifyMethods(loadedAssemblies[index], manifest.assemblies[index], index, true);
                    ++active.postRejectionMappingChecks;
                }
                active.maximumWorkingSetBytes = Math.Max(active.maximumWorkingSetBytes, R01BProcessMemory.Capture().PeakResidentBytes);
                active.managedBytesAfter = GC.GetTotalMemory(false);
                active.result = "Passed";
            }
            catch (Exception error)
            {
                active.error = error.ToString();
                UnityEngine.Debug.LogException(error);
            }
            Write(active);
            return active.result == "Passed" ? 0 : 1;
        }

        private static void VerifyMethods(Assembly loaded, WorkloadAssembly item, int index, bool afterRejection)
        {
            string suffix = item.id.ToString("D4");
            Type entry = loaded.GetType("AssemblyShadow.WorkloadV2.MetadataEntry_" + suffix, true);
            MethodInfo returnId = entry.GetMethod("ReturnId", BindingFlags.Public | BindingFlags.Static);
            MethodInfo payload = entry.GetMethod("ReturnPayloadMarker", BindingFlags.Public | BindingFlags.Static);
            Require(returnId != null && payload != null && (int)returnId.Invoke(null, null) == item.id &&
                (int)payload.Invoke(null, null) == item.id,
                "R01B fixture method result is wrong at " + index + (afterRejection ? " after rejection." : "."));
            int fieldCount = item.id == 0 ? 4 : item.id == 1 ? 2 : 1;
            for (int fieldIndex = 0; fieldIndex < fieldCount; ++fieldIndex)
            {
                FieldInfo field = entry.GetField("PayloadRva_" + fieldIndex.ToString("D2"), BindingFlags.Public | BindingFlags.Static);
                byte expected = (byte)((item.id * 17 + fieldIndex * 29) % 251);
                Require(field != null && field.FieldType == typeof(byte) && (byte)field.GetValue(null) == expected,
                    "R01B initialized RVA field is wrong at " + index + ":" + fieldIndex +
                    (afterRejection ? " after rejection." : "."));
                if (!afterRejection)
                {
                    ++active.payloadRvaChecks;
                    if ((item.id == 0 && fieldIndex > 0) || (item.id == 1 && fieldIndex == 1))
                        ++active.highRvaFieldChecks;
                }
            }
            if (index == 0 || index == 4095 || index == 4096 || index == 8191 || index == active.validImagesToLoad - 1)
            {
                Type dense = loaded.GetType("AssemblyShadow.WorkloadV2.MetadataType_" + suffix +
                    "_0095_Strings_0123456789abcdef0123456789abcdef", true);
                MethodInfo denseReturn = dense.GetMethod("ReturnId", BindingFlags.Public | BindingFlags.Static);
                Require(denseReturn != null && (int)denseReturn.Invoke(null, null) == item.id,
                    "R01B dense metadata/name lookup is wrong at " + index + ".");
                if (!afterRejection) ++active.denseNameChecks;
            }
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            if (active == null) return 2;
            active.result = "Failed";
            active.error = error.ToString();
            try { Write(active); return 1; }
            catch { return 2; }
        }

        private static CapacityResult Capacity(long[] sizes)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetMetadataCapacityJson(sizes, out json);
            Require(code == AssemblyShadowErrorCode.Success, "GetMetadataCapacityJson failed: " + code);
            AssemblyShadowMetadataCapacityProfile2 value = AssemblyShadowMetadataCapacityProfile2.Parse(json);
            return new CapacityResult {
                rawJson = json, fitsPreliminary = value.fitsPreliminary, failureReason = value.failureReason,
                requiredImages = value.requiredImages, acceptedImages = value.acceptedImages,
                firstFailingIndex = value.firstFailingIndex, reservedPages = value.reservedPages,
                mappedPages = value.mappedPages, lifetimeReservedImageCount = value.lifetimeReservedImageCount,
                remainingImageCount = value.remainingImageCount, ordinaryAllocatedCount = value.ordinaryAllocatedCount,
                shadowAllocatedCount = value.shadowAllocatedCount, reservedShadowImageCount = value.reservedShadowImageCount,
                freeUsablePages = UsablePageCapacity - value.reservedPages
            };
        }

        private static void ValidateManifest(WorkloadManifest manifest)
        {
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.kind == "R01BWorkloadV2VerifiedManifest" &&
                manifest.status == "CorrectedMetadataOnlySealedCorpus" && manifest.assemblies != null && manifest.assemblies.Length == RequiredImages &&
                manifest.totals != null && manifest.totals.assemblyCount == RequiredImages &&
                manifest.totals.totalBytes == AggregateDllBytes && manifest.totals.meanBytes == 65536 &&
                manifest.totals.maxBytes == MaximumDllBytes, "R01B verified workload manifest has the wrong envelope.");
            long total = 0;
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var files = new HashSet<string>(StringComparer.Ordinal);
            for (int index = 0; index < manifest.assemblies.Length; ++index)
            {
                WorkloadAssembly item = manifest.assemblies[index];
                Require(item != null && item.id == index && !string.IsNullOrWhiteSpace(item.name) && names.Add(item.name) &&
                    !string.IsNullOrWhiteSpace(item.file) && files.Add(item.file) && IsHash(item.sha256) &&
                    item.sizeBytes > 0 && item.sizeBytes <= MaximumDllBytes, "Invalid R01B workload row " + index + ".");
                total = checked(total + item.sizeBytes);
            }
            Require(total == AggregateDllBytes, "R01B workload rows do not total 512 MiB.");
        }

        private static void ValidateMixedManifest(MixedWorkloadManifest manifest)
        {
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.kind == "R01BMixedWorkloadManifest" &&
                manifest.status == "DerivedFromVerifiedM07P03AndOrdinaryCorpus" && manifest.requiredImages == RequiredImages &&
                manifest.retainedFailureCount == 3 && manifest.failedInputBytes == 12 && manifest.shadow != null &&
                manifest.retainedFailureInputs != null && manifest.retainedFailureInputs.Length == manifest.retainedFailureCount &&
                manifest.paddingEvidence != null && manifest.paddingEvidence.method == "DeterministicZeroTrailer" &&
                !manifest.paddingEvidence.addressabilityEstablished &&
                manifest.paddingEvidence.note == "Zero trailer padding preserves the original PE/CLI body and identity proof; it cannot establish metadata addressability for the added bytes." &&
                manifest.shadow.imageCount == 5 && manifest.shadow.assemblies != null && manifest.shadow.assemblies.Length == 5 &&
                manifest.ordinary != null && manifest.ordinary.selectedCount == RequiredImages - 8 &&
                manifest.assemblies != null && manifest.assemblies.Length == manifest.ordinary.selectedCount &&
                manifest.totals != null && manifest.totals.assemblyCount == RequiredImages &&
                manifest.totals.shadowImageCount == manifest.shadow.imageCount &&
                manifest.totals.retainedFailureCount == manifest.retainedFailureCount &&
                manifest.totals.validDllBytes == AggregateDllBytes &&
                manifest.totals.maxBytes == MaximumDllBytes && manifest.totals.meanBytes == 65536 &&
                manifest.totals.failedInputBytes == manifest.failedInputBytes &&
                manifest.totals.ordinaryValidDllBytes == manifest.ordinary.validDllBytes &&
                manifest.totals.shadowValidDllBytes == manifest.shadow.validDllBytes &&
                manifest.totals.paddingBytes == manifest.ordinary.paddingBytes &&
                manifest.totals.ordinarySourceBytes + manifest.totals.paddingBytes == manifest.totals.ordinaryValidDllBytes &&
                manifest.totals.ordinaryValidDllBytes + manifest.totals.shadowValidDllBytes == AggregateDllBytes,
                "R01B mixed manifest has the wrong exact envelope.");
            long ordinaryTotal = 0;
            long maximum = 0;
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for (int index = 0; index < manifest.assemblies.Length; ++index)
            {
                MixedWorkloadAssembly item = manifest.assemblies[index];
                Require(item != null && item.id == index && item.name == "AssemblyShadow.WorkloadV2.I" + index.ToString("D4") &&
                    item.file == item.name + ".dll" && IsHash(item.sha256) && IsHash(item.sourceSha256) &&
                    item.bodyPrefixSha256 == item.sourceSha256 &&
                    !string.IsNullOrWhiteSpace(item.mvid) && !string.IsNullOrWhiteSpace(item.sourceMvid) &&
                    item.sizeBytes > 0 && item.sizeBytes <= MaximumDllBytes &&
                    item.sourceSizeBytes > 0 && item.paddingBytes >= 0 && item.sizeBytes == item.sourceSizeBytes + item.paddingBytes &&
                    item.mvid == item.sourceMvid && item.typeDefRows == item.sourceTypeDefRows &&
                    item.methodDefRows == item.sourceMethodDefRows && item.stringsHeapBytes == item.sourceStringsHeapBytes &&
                    names.Add(item.name), "Invalid R01B mixed ordinary row " + index + ".");
                ordinaryTotal = checked(ordinaryTotal + item.sizeBytes);
                maximum = Math.Max(maximum, item.sizeBytes);
            }
            for (int index = 0; index < manifest.retainedFailureInputs.Length; ++index)
            {
                MixedFailureInput failure = manifest.retainedFailureInputs[index];
                string[] failureHashes = { "8b89c1271ee642214aaa676a5f6ed0373b8f12f66fb0718459f1f27c116cc4a0", "4da897f8d49208f2049051303861d7cfc0d893dc0f2886cb78b68bab93af38ac", "457440f66892d182988508f95b282effa40cb51edb7f2bcad621bf0acde1ee79" };
                Require(failure != null && failure.attempt == index && failure.hex == "424144" + index.ToString("D2") &&
                    failure.sizeBytes == 4 && failure.sha256 == failureHashes[index],
                    "Invalid R01B mixed retained failure input " + index + ".");
            }
            Require(ordinaryTotal == manifest.ordinary.validDllBytes && maximum == MaximumDllBytes &&
                manifest.ordinary.sourceBytes + manifest.ordinary.paddingBytes == manifest.ordinary.validDllBytes &&
                manifest.ordinary.paddingAssemblyId == manifest.assemblies[manifest.assemblies.Length - 1].id,
                "R01B mixed ordinary rows do not satisfy their envelope.");
            long shadowTotal = 0;
            var shadowNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (MixedShadowAssembly item in manifest.shadow.assemblies)
            {
                Require(item != null && !string.IsNullOrWhiteSpace(item.name) && IsHash(item.sha256) &&
                    !string.IsNullOrWhiteSpace(item.mvid) && !string.IsNullOrWhiteSpace(item.fullName) &&
                    item.sizeBytes > 0 && item.sizeBytes <= MaximumDllBytes && item.typeDefRows > 0 &&
                    item.methodDefRows > 0 && item.stringsHeapBytes > 4096 && shadowNames.Add(item.name),
                    "Invalid R01B mixed Shadow row.");
                shadowTotal = checked(shadowTotal + item.sizeBytes);
            }
            Require(shadowTotal == manifest.shadow.validDllBytes, "R01B mixed Shadow rows do not satisfy their envelope.");
        }

        private static void VerifyMixedShadowEvidence(MixedWorkloadManifest manifest, string baselineBuildId, string runtimeAbiHash)
        {
            string path = Path.GetFullPath(Argument("-shadowEarlyResult", ""));
            Require(File.Exists(path), "R01B mixed early-startup result is missing.");
            EarlyReceipt result = JsonUtility.FromJson<EarlyReceipt>(File.ReadAllText(path));
            Require(result != null && result.kind == "R01EarlyStartupReceipt" && result.mode == "Control" &&
                result.result == "Passed" && result.callbackReturnCode == 0 &&
                result.processId == Process.GetCurrentProcess().Id && result.baselineBuildId == baselineBuildId &&
                result.runtimeAbiHash == runtimeAbiHash && result.operations != null &&
                result.byteInputs != null && result.snapshots != null,
                "R01B mixed early result is not the committed Control capsule for this process.");
            Require(result.operations.Any(item => item.phase == "commit" && item.code == "Success" && item.intCode == 0),
                "R01B mixed early result has no successful commit operation.");
            foreach (MixedShadowAssembly expected in manifest.shadow.assemblies)
                Require(result.operations.Any(item => item.phase == "stage:" + expected.name && item.code == "Success" && item.intCode == 0),
                    "R01B mixed early result has no successful stage for " + expected.name + ".");
            Require(result.snapshots.Any(item => item.phase == "after-commit" && !string.IsNullOrEmpty(item.diagnosticsJson)),
                "R01B mixed early result has no post-commit diagnostic snapshot.");
            string nativeJson;
            Require(AssemblyShadowRuntime.GetDiagnosticsJson(out nativeJson) == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(nativeJson),
                "R01B mixed native committed diagnostics are unavailable.");
            AssemblyShadowDiagnostics native = AssemblyShadowDiagnostics.Parse(nativeJson);
            Require(native != null && native.state == "Committed" && native.generation > 0 && native.assemblies != null && native.assemblies.Length >= manifest.shadow.assemblies.Length,
                "R01B mixed native state is not the committed early Shadow closure.");
            foreach (MixedShadowAssembly expected in manifest.shadow.assemblies)
            {
                EarlyByteInput actual = result.byteInputs.FirstOrDefault(item => item.name == expected.name);
                Require(actual != null && actual.sha256 == expected.sha256 && actual.length > 0,
                    "R01B mixed early Shadow hash differs for " + expected.name + ".");
            }
        }

        private static string Confined(string root, string relative)
        {
            Require(!string.IsNullOrWhiteSpace(relative) && !Path.IsPathRooted(relative), "R01B workload path is not relative.");
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string full = Path.GetFullPath(Path.Combine(root, relative));
            Require(full.StartsWith(prefix, StringComparison.Ordinal), "R01B workload path escapes its root.");
            return full;
        }

        private static void Write(Result result)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(result, true));
        }

        private static string Hash(byte[] bytes)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        private static bool IsHash(string value)
        {
            return value != null && value.Length == 64 && value.All(c => (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'));
        }

        private static string Argument(string name, string fallback)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int index = 0; index + 1 < args.Length; ++index)
                if (args[index] == name) return args[index + 1];
            return fallback;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }

        [Serializable, Preserve]
        private sealed class WorkloadManifest
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind, status;
            [Preserve] public WorkloadAssembly[] assemblies;
            [Preserve] public WorkloadTotals totals;
        }

        [Serializable, Preserve]
        private sealed class MixedWorkloadManifest
        {
            [Preserve] public int schemaVersion, requiredImages, retainedFailureCount, failedInputBytes;
            [Preserve] public string kind, status;
            [Preserve] public MixedFailureInput[] retainedFailureInputs;
            [Preserve] public MixedPaddingEvidence paddingEvidence;
            [Preserve] public MixedSource source;
            [Preserve] public MixedShadow shadow;
            [Preserve] public MixedOrdinary ordinary;
            [Preserve] public MixedTotals totals;
            [Preserve] public MixedWorkloadAssembly[] assemblies;

            public WorkloadManifest ToWorkloadManifest()
            {
                return new WorkloadManifest { schemaVersion = 1, kind = "R01BWorkloadV2VerifiedManifest",
                    status = "CorrectedMetadataOnlySealedCorpus", totals = new WorkloadTotals {
                        assemblyCount = assemblies.Length, totalBytes = ordinary.validDllBytes, meanBytes = ordinary.validDllBytes / assemblies.Length,
                        maxBytes = totals.maxBytes }, assemblies = assemblies.Select(item => new WorkloadAssembly {
                            id = item.id, name = item.name, file = item.file, sha256 = item.sha256, sizeBytes = item.sizeBytes }).ToArray() };
            }
        }

        [Serializable, Preserve] private sealed class MixedSource { public string ordinaryManifestPath, ordinaryManifestSha256, ordinaryCorpusRoot, fixtureManifestPath, fixtureManifestSha256, patchManifestPath, patchManifestSha256, patchId, onBuildPath, onBuildSha256, offBuildPath, offBuildSha256, replayReceiptPath, replayReceiptSha256, generatorPath, generatorSha256; }
        [Serializable, Preserve] private sealed class MixedFailureInput { public int attempt, sizeBytes; public string hex, sha256; }
        [Serializable, Preserve] private sealed class MixedPaddingEvidence { public string method, note; public bool addressabilityEstablished; }
        [Serializable, Preserve] private sealed class MixedShadow { public int imageCount; public long validDllBytes; public MixedShadowAssembly[] assemblies; }
        [Serializable, Preserve] private sealed class MixedShadowAssembly { public string name, path, sha256, mvid, fullName; public long sizeBytes; public int typeDefRows, methodDefRows, stringsHeapBytes; }
        [Serializable, Preserve] private sealed class MixedOrdinary { public int selectedCount, sourceStartIndex, sourceEndIndex, paddingAssemblyId; public long sourceBytes, paddingBytes, validDllBytes; }
        [Serializable, Preserve] private sealed class MixedTotals { public int assemblyCount, shadowImageCount, retainedFailureCount, failedInputBytes; public long ordinarySourceBytes, ordinaryValidDllBytes, shadowValidDllBytes, paddingBytes, validDllBytes, maxBytes, meanBytes; }
        [Serializable, Preserve] private sealed class MixedWorkloadAssembly
        {
            public int id, typeDefRows, methodDefRows, stringsHeapBytes, sourceTypeDefRows, sourceMethodDefRows, sourceStringsHeapBytes;
            public string name, file, sha256, sourcePath, sourceSha256, bodyPrefixSha256, mvid, sourceMvid, fullName;
            public long sizeBytes, sourceSizeBytes, paddingBytes;
        }

        [Serializable, Preserve]
        private sealed class WorkloadAssembly
        {
            [Preserve] public int id;
            [Preserve] public string name, file, sha256;
            [Preserve] public long sizeBytes;
        }

        [Serializable, Preserve]
        private sealed class WorkloadTotals
        {
            [Preserve] public int assemblyCount;
            [Preserve] public long totalBytes, meanBytes, maxBytes;
        }

        [Serializable, Preserve]
        private sealed class EarlyReceipt
        {
            [Preserve] public string kind, mode, baselineBuildId, runtimeAbiHash, result;
            [Preserve] public int processId, callbackReturnCode;
            [Preserve] public EarlyOperation[] operations;
            [Preserve] public EarlySnapshot[] snapshots;
            [Preserve] public EarlyByteInput[] byteInputs;
        }

        [Serializable, Preserve]
        private sealed class EarlyOperation { [Preserve] public string phase, code; [Preserve] public int intCode; }

        [Serializable, Preserve]
        private sealed class EarlySnapshot { [Preserve] public string phase, diagnosticsJson; }

        [Serializable, Preserve]
        private sealed class EarlyByteInput { [Preserve] public string name, sha256; [Preserve] public long length; }

        [Serializable, Preserve]
        private sealed class Result
        {
            [Preserve] public int schemaVersion, processId, loadedImages, invokedImages, payloadRvaChecks, denseNameChecks,
                postRejectionMappingChecks, retainedFailureCount, validImagesToLoad, highRvaFieldChecks;
            [Preserve] public string kind, milestone, result, error, baselineBuildId, runtimeAbiHash, unityVersion, platform,
                buildGuid, resultPath, manifestPath, manifestSha256, corpusRoot, limitException,
                overflowPath, overflowName, overflowSha256, scenario;
            [Preserve] public string[] retainedFailureExceptions;
            [Preserve] public bool il2cpp;
            [Preserve] public string memoryMeasurement;
            [Preserve] public long loadedDllBytes, shadowDllBytes, validDllBytes, retainedFailureInputBytes, overflowDllBytes, loadMilliseconds, workingSetBytesBefore, maximumWorkingSetBytes, managedBytesAfter;
            [Preserve] public string mixedManifestPath, mixedManifestSha256, mixedCorpusRoot;
            [Preserve] public CapacityResult initial, afterRetainedFailures, before, at8191, after, afterRejected;
        }

        [Serializable, Preserve]
        private sealed class CapacityResult
        {
            [Preserve] public string rawJson, failureReason;
            [Preserve] public bool fitsPreliminary;
            [Preserve] public int firstFailingIndex;
            [Preserve] public ulong requiredImages, acceptedImages, reservedPages, mappedPages, lifetimeReservedImageCount,
                remainingImageCount, ordinaryAllocatedCount, shadowAllocatedCount, reservedShadowImageCount, freeUsablePages;
        }
    }
}
