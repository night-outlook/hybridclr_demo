using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    // These Editor DTOs deliberately have no compile-time Bootstrap dependency.
    // Their complete shapes are compared with the actual prelink and linked DTOs.
    [Serializable] public sealed class M06ExecutionProofPaths
    { public string typeProofPath, typeProofSha256, executionProofPath, executionProofSha256; }

    [Serializable] public sealed class M06ExecutionProof
    {
        public int schemaVersion;
        public string milestone, policy, compileSnapshotHash, linkedPlayerReceiptHash, nativeLibrarySha256, buildGuid;
        public string generationProofPath, generationProofSha256, typeProofPath, typeProofSha256;
        public bool developmentBuild;
        public string[] apiSignatures;
        public M06ExecutionEnumValue[] errorCodes;
        public M06ExecutionSchemaType[] schemaTypes;
        public M06ExecutionImage[] images;
    }
    [Serializable] public sealed class M06ExecutionEnumValue { public string name; public int value; }
    [Serializable] public sealed class M06ExecutionSchemaType
    {
        public string side, assemblyName, assemblyIdentity, typeName;
        public int typeAttributes;
        public bool isSerializable;
        public M06ExecutionSchemaField[] fields;
    }
    [Serializable] public sealed class M06ExecutionSchemaField { public string name, type, resolvedType; public int attributes; }
    [Serializable] public sealed class M06ExecutionImage
    {
        public string role, planId, compileSnapshotHash, planHash, pdbPath, pdbSha256;
        public bool pdbAvailable;
        public M04AssemblyIdentity identity;
        public M06ExecutionMethod[] methods;
    }
    [Serializable] public sealed class M06ExecutionMethod
    {
        public string declaringType, name, signature;
        public int metadataToken, genericArity, methodFlags, implementationFlags, maxStack;
        public bool isStatic, hasBody, initLocals;
        public M06ExecutionSignatureType returnType;
        public M06ExecutionSignatureType[] parameterTypes;
        public string[] genericParameterNames, locals, instructions;
        public M06ExecutionExceptionHandler[] exceptionHandlers;
        public M06ExecutionSequencePoint[] sequencePoints;
    }
    [Serializable] public sealed class M06ExecutionSignatureType { public string assembly, type; }
    [Serializable] public sealed class M06ExecutionExceptionHandler
    {
        public string handlerType, catchType;
        public int tryStart, tryEnd, filterStart, handlerStart, handlerEnd;
    }
    [Serializable] public sealed class M06ExecutionSequencePoint
    {
        public string document, checksumAlgorithm, checksum;
        public int instructionIndex, ilOffset, startLine, startColumn, endLine, endColumn;
    }

    /// <summary>
    /// Replays execution evidence from immutable compiler, linker and generation-plan
    /// bytes. It neither loads business assemblies into the Editor nor resolves through
    /// ambient search paths, and does not compare the expanded M06 DLLs with M01 DLLs.
    /// </summary>
    public static class M06ExecutionSchemaVerifier
    {
        public const string Policy = "execution-world:1";
        public const string TypePolicy = "active-execution-types:1";
        public const string TypeProofName = "m06-type-proof.json";
        public const string ExecutionProofName = "m06-execution-proof.json";
        private const string Bootstrap = "AssemblyShadowDemo.Bootstrap";
        private const string Runtime = "HybridCLR.Runtime";
        private const string Probe = "AssemblyShadowDemo.M06ExecutionProbe/";
        private const string Diagnostics = "HybridCLR.AssemblyShadowExecutionDiagnostics";
        private const string ClassInfo = "HybridCLR.AssemblyShadowExecutionClassInfo";
        private const string MetadataCapacity = "HybridCLR.AssemblyShadowMetadataCapacity";
        private const string MetadataAllocation = "HybridCLR.AssemblyShadowMetadataAllocation";
        private const string RecoveryInfo = "HybridCLR.AssemblyShadowRecoveryInfo";
        private static readonly string[] Candidates = {
            "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
            "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer",
        };
        private static readonly string[] RequiredBootstrapRoots = {
            Probe + "Result", Probe + "FixtureManifest", Probe + "PlayerBuildReceipt", Probe + "TypeProof", Probe + "ExecutionProof", Probe + "GenerationProof", Probe + "ExecutionPolicyProof",
            Probe + "PatchManifestVersion", Probe + "PatchManifestEnvelope", Probe + "PatchManifest", Probe + "BaselineManifest", Probe + "SnapshotReceipt",
            "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Configuration", "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Site",
        };
        // Additional input roots must be explicitly admitted here; a newly introduced
        // JsonUtility call does not automatically authorize its DTO or stripping policy.
        private static readonly string[] AdditionalJsonRoots = {
            Probe + "GenerationPlan", Probe + "CompilerModeProof",
            Probe + "GenerationOutput", Probe + "AotInputProof", Probe + "LinkedPlayerReceipt",
        };
        private static readonly string[] LegacyApiNames = {
            "ConfigureCandidates(System.String,System.String[],System.String[])",
            "BeginTransaction(System.String,System.String,System.String[],System.Int32)",
            "StageAssembly(System.Byte[],System.Byte[])", "ValidateTransaction()", "CommitTransaction()", "AbortTransaction()",
            "GetState(HybridCLR.AssemblyShadowState&)", "GetAssemblyExecutionMode(System.String,HybridCLR.AssemblyExecutionMode&)",
            "GetDiagnosticsJson(System.String&)", "GetTypeResolutionInfo(System.Type,System.String&)", "GetExecutionDiagnosticsJson(System.String&)",
        };
        private static readonly string[] NegotiatedApiNames = {
            "GetMetadataCapacityJson(System.Int64[],System.String&)",
            "ReserveMetadataBudget(System.Int64[],System.Int32)",
            "GetRecoveryInfoJson(System.String&)",
        };
        private static readonly string[] NegotiatedNativeApiNames = {
            "GetMetadataCapacityJsonInternal(System.Int64[],System.String&)",
            "ReserveMetadataBudgetInternal(System.Int64[],System.Int32)",
            "GetRecoveryInfoJsonInternal(System.String&)",
        };
        private static readonly string[] ApiNames = LegacyApiNames.Concat(NegotiatedApiNames).ToArray();
        private static readonly string[] ErrorNames = {
            "Success", "FeatureDisabled", "InvalidState", "InvalidArgument", "CandidateNotRegistered", "DuplicateAssemblyName",
            "BaselineAssemblyNotFound", "BaselineBuildMismatch", "AssemblyNameMismatch", "BadImage", "UnsupportedAssembly",
            "ClosureMemberMissing", "UnexpectedClosureMember", "ReferenceResolutionFailed", "ReferenceEscapesClosure", "BaselineAlreadyUsed",
            "ResourceAbiMismatch", "RuntimeAbiMismatch", "AlreadyCommitted", "ModuleInitializerFailed", "InternalError", "BaselineMethodExecution",
            "CapabilityUnavailable", "MetadataCapacityExceeded", "MetadataBudgetMismatch",
        };

        public static M06ExecutionProofPaths WriteProofs(string snapshot, AssemblySnapshotReceipt captured,
            M04AssemblyIdentity[] linked, string generationProofPath)
        {
            snapshot = Path.GetFullPath(snapshot);
            string typePath = Path.Combine(snapshot, TypeProofName), executionPath = Path.Combine(snapshot, ExecutionProofName);
            Require(!File.Exists(typePath) && !File.Exists(executionPath), "Immutable", "M06 proofs are write-once snapshot companions.");
            M05TypeProof typeProof;
            M06ExecutionProof proof = Capture(snapshot, captured, linked, generationProofPath, out typeProof);
            proof.typeProofPath = typePath;
            proof.typeProofSha256 = ShadowHash.Bytes(new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(typeProof, true)));
            // Validate everything before the first write. A failed partial write remains
            // evidence and is never silently deleted or replaced by a subsequent capture.
            M04AssemblyIdentityProof.WriteNewJson(typePath, typeProof);
            Require(ShadowHash.File(typePath) == proof.typeProofSha256, "Write", "Serialized type-proof bytes differ.");
            M04AssemblyIdentityProof.WriteNewJson(executionPath, proof);
            var result = new M06ExecutionProofPaths { typeProofPath = typePath, typeProofSha256 = proof.typeProofSha256,
                executionProofPath = executionPath, executionProofSha256 = ShadowHash.File(executionPath) };
            VerifyProofs(snapshot, captured, linked, generationProofPath, result.typeProofPath, result.typeProofSha256,
                result.executionProofPath, result.executionProofSha256);
            return result;
        }

        public static void VerifyProofs(string snapshot, AssemblySnapshotReceipt captured, M04AssemblyIdentity[] linked,
            string generationProofPath, string typeProofPath, string typeProofSha256, string executionProofPath, string executionProofSha256)
        {
            snapshot = Path.GetFullPath(snapshot);
            Require(typeProofPath == Path.Combine(snapshot, TypeProofName) && executionProofPath == Path.Combine(snapshot, ExecutionProofName),
                "Binding", "Proofs must be the exact immutable Player snapshot companions.");
            VerifyHash(typeProofPath, typeProofSha256); VerifyHash(executionProofPath, executionProofSha256);
            var claimedType = M04JsonEvidence.Read<M05TypeProof>(File.ReadAllText(typeProofPath));
            var claimed = M04JsonEvidence.Read<M06ExecutionProof>(File.ReadAllText(executionProofPath));
            M05TypeProof actualType;
            var actual = Capture(snapshot, captured, linked, generationProofPath, out actualType);
            actual.typeProofPath = typeProofPath; actual.typeProofSha256 = typeProofSha256;
            Require(JsonUtility.ToJson(claimedType) == JsonUtility.ToJson(actualType), "TypeReplay", "Type proof does not replay from this Player's linked bytes.");
            Require(JsonUtility.ToJson(claimed) == JsonUtility.ToJson(actual), "Replay", "Execution/schema/symbol evidence differs from actual captured bytes.");
            VerifyHash(typeProofPath, typeProofSha256); VerifyHash(executionProofPath, executionProofSha256);
        }

        private static M06ExecutionProof Capture(string snapshot, AssemblySnapshotReceipt supplied, M04AssemblyIdentity[] linkedIdentities,
            string generationProofPath, out M05TypeProof typeProof)
        {
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            Require(supplied != null && supplied.snapshotHash == captured.snapshotHash && supplied.snapshotHash == AssemblySnapshot.ComputeHash(supplied),
                "Snapshot", "The supplied Player receipt must be the hash-verified captured snapshot.");
            Require(captured.buildId != null && captured.buildId.StartsWith("M06-Baseline-", StringComparison.Ordinal),
                "Snapshot", "Execution evidence requires an actual M06 Player baseline.");
            Require(Path.IsPathRooted(generationProofPath), "Generation", "Generation proof must be an explicit absolute path.");
            generationProofPath = Path.GetFullPath(generationProofPath);
            string generationHash = ShadowHash.File(generationProofPath);
            var generation = M06GenerationBuild.ReadAndVerify(generationProofPath);
            bool development = (((BuildOptions)captured.playerBuildOptions) & BuildOptions.Development) != 0;
            Require(generation.baselineBuildId == captured.buildId && generation.developmentBuild == development &&
                generation.target == captured.target && generation.architecture == captured.architecture && generation.unityVersion == captured.unityVersion,
                "Generation", "Compile-only generation and actual Player provenance differ.");
            ShadowSourcePins.RequireSameBuildSources(generation.sourcePins, captured.sourcePins);
            M04AssemblyIdentityProof.Verify(linkedIdentities, M04AssemblyIdentityProof.ReadLinked(snapshot, captured));
            M03DiagnosticSchemaVerifier.Verify(snapshot, captured);
            var before = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            var after = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            M06ExecutionSchemaType[] schemas;
            try
            {
                foreach (string name in new[] { Bootstrap, Runtime })
                    before.Add(name, ReadModule(FindFile(snapshot, captured, name, false)));
                // Definitions used to explain linker retargeting come exclusively
                // from this successful Player's closed, hash-verified linked set.
                // Compiler reference assemblies are not runtime implementations.
                foreach (var file in captured.linkedPlayerReceipt.assemblies)
                {
                    Require(after.Keys.All(name => AssemblyIdentityUtil.CanonicalName(name) != AssemblyIdentityUtil.CanonicalName(file.name)),
                        "SchemaResolution", "Duplicate canonical linked schema module: " + file.name);
                    after.Add(file.name, ReadModule(FindFile(snapshot, captured, file.name, true)));
                }
                M05TypeSchemaVerifier.VerifyRuntime(before[Runtime], after[Runtime]);
                VerifyRuntimeModules(before[Runtime], after[Runtime]);
                string[] roots = VerifyBootstrap(before, after);
                schemas = ReadSchemaGraph(before, roots, "PlayerInput", after).Concat(ReadSchemaGraph(after, roots, "LinkedPlayer", after)).ToArray();
                typeProof = new M05TypeProof { schemaVersion = 1, milestone = "M06", policy = TypePolicy,
                        compileSnapshotHash = captured.snapshotHash, linkedPlayerReceiptHash = captured.linkedPlayerReceiptHash,
                        nativeLibrarySha256 = captured.nativeLibrarySha256, buildGuid = captured.buildGuid, developmentBuild = development,
                        assemblies = M05TypeInventoryProof.ReadIdentities(linkedIdentities), moduleMethods = M05TypeSchemaVerifier.ReadModuleMethods(after["mscorlib"]) };
            }
            finally { foreach (ModuleDef module in before.Values.Concat(after.Values)) module.Dispose(); }

            var images = new List<M06ExecutionImage>();
            foreach (bool isLinked in new[] { false, true })
                foreach (string name in Candidates)
                    images.Add(ReadImage(FindFile(snapshot, captured, name, isLinked), isLinked ? "LinkedPlayer" : "PlayerInput",
                        "", captured.snapshotHash, "", false));
            BuildTarget target = (BuildTarget)Enum.Parse(typeof(BuildTarget), generation.target);
            foreach (var row in generation.plans.OrderBy(item => item.planId, StringComparer.Ordinal))
            {
                var plan = ShadowGenerationPlan.ReadAndVerify(Path.GetDirectoryName(row.planPath), target, generation.architecture, row.planHash);
                foreach (string name in row.closureLoadOrder)
                {
                    var matches = plan.Receipt.images.Where(item => AssemblyIdentityUtil.CanonicalName(item.name) == AssemblyIdentityUtil.CanonicalName(name)).ToArray();
                    Require(matches.Length == 1 && Candidates.Contains(matches[0].name, StringComparer.Ordinal), "GenerationImage", "Selected candidate image is missing or ambiguous: " + name);
                    var file = matches[0];
                    images.Add(ReadImage(new CapturedFile { name = file.name, path = ShadowHash.SafeChild(plan.Root, file.path), sha256 = file.sha256,
                        pdbPath = string.IsNullOrEmpty(file.pdbPath) ? "" : ShadowHash.SafeChild(plan.Root, file.pdbPath), pdbSha256 = file.pdbSha256 ?? "" },
                        "GenerationPlan", row.planId, row.compileSnapshotHash, row.planHash, true));
                }
                plan.VerifyUnchanged();
            }
            // All reads above are replayed against their immutable receipts after parsing.
            var finalSnapshot = AssemblySnapshot.ReadAndVerify(snapshot, true);
            Require(finalSnapshot.snapshotHash == captured.snapshotHash, "SnapshotChanged", "Player inputs changed during proof capture.");
            M06GenerationBuild.ReadAndVerify(generationProofPath); VerifyHash(generationProofPath, generationHash);
            return new M06ExecutionProof { schemaVersion = 1, milestone = "M06", policy = Policy,
                compileSnapshotHash = captured.snapshotHash, linkedPlayerReceiptHash = captured.linkedPlayerReceiptHash,
                nativeLibrarySha256 = captured.nativeLibrarySha256, buildGuid = captured.buildGuid, developmentBuild = development,
                generationProofPath = generationProofPath, generationProofSha256 = generationHash, typeProofPath = "", typeProofSha256 = "",
                apiSignatures = ApiNames.Select(ApiFullName).ToArray(), errorCodes = ErrorNames.Select((name, value) => new M06ExecutionEnumValue { name = name, value = value }).ToArray(),
                schemaTypes = schemas, images = images.ToArray() };
        }

        internal static void VerifyRuntimeModules(ModuleDef input, ModuleDef linked)
        {
            Require(input != null && linked != null && input.Assembly != null && linked.Assembly != null &&
                input.Assembly.Name == Runtime && input.Assembly.FullName == linked.Assembly.FullName, "RuntimeIdentity", "Captured Runtime identities differ.");
            ShadowDiagnosticSchemaProof.Verify(input, linked, new[] { Diagnostics, ClassInfo, MetadataCapacity, MetadataAllocation, RecoveryInfo }, "M06Execution");
            foreach (ModuleDef module in new[] { input, linked })
            {
                TypeDef api = module.Find("HybridCLR.AssemblyShadowRuntime", false);
                var methods = api == null ? new MethodDef[0] : api.Methods.Where(method => method.IsPublic && !method.IsConstructor).ToArray();
                Require(methods.Length == ApiNames.Length, "Api", "The public Assembly Shadow API must have exactly fourteen operations.");
                foreach (string name in LegacyApiNames)
                {
                    var matches = methods.Where(method => method.FullName == ApiFullName(name)).ToArray();
                    Require(matches.Length == 1 && matches[0].IsStatic && matches[0].IsInternalCall && !matches[0].HasBody,
                        "Api", "Missing exact native InternalCall: " + name);
                }
                foreach (string name in NegotiatedApiNames)
                {
                    var matches = methods.Where(method => method.FullName == ApiFullName(name)).ToArray();
                    Require(matches.Length == 1 && matches[0].IsStatic && !matches[0].IsInternalCall && matches[0].HasBody,
                        "Api", "Missing exact managed negotiated wrapper: " + name);
                }
                var nativeMethods = api.Methods.Where(method => method.IsPrivate && method.IsStatic && method.IsInternalCall).ToArray();
                Require(nativeMethods.Length == NegotiatedNativeApiNames.Length, "Api", "The private negotiated native API inventory changed.");
                foreach (string name in NegotiatedNativeApiNames)
                {
                    var matches = nativeMethods.Where(method => method.FullName == ApiFullName(name)).ToArray();
                    Require(matches.Length == 1 && !matches[0].HasBody,
                        "Api", "Missing exact private native InternalCall: " + name);
                }
                foreach (string name in new[] { "GetDiagnosticsJson", "GetExecutionDiagnosticsJson" })
                    Require(methods.Single(method => method.Name == name).ParamDefs.Any(parameter => parameter.Sequence == 1 && parameter.IsOut),
                        "Api", "Diagnostic argument must remain out string: " + name);
                Require(methods.Single(method => method.Name == "GetMetadataCapacityJson").ParamDefs.Any(parameter => parameter.Sequence == 2 && parameter.IsOut),
                    "Api", "Metadata capacity argument must remain out string.");
                Require(methods.Single(method => method.Name == "GetRecoveryInfoJson").ParamDefs.Any(parameter => parameter.Sequence == 1 && parameter.IsOut),
                    "Api", "Recovery argument must remain out string.");
                var code = module.Find("HybridCLR.AssemblyShadowErrorCode", false);
                var values = code == null ? new FieldDef[0] : code.Fields.Where(field => field.IsLiteral).ToArray();
                Require(code != null && code.IsEnum && values.Length == ErrorNames.Length, "ErrorCodes", "Execution error-code inventory differs.");
                for (int value = 0; value < ErrorNames.Length; ++value)
                {
                    var matches = values.Where(field => field.Name == ErrorNames[value]).ToArray();
                    Require(matches.Length == 1 && matches[0].Constant != null && matches[0].Constant.Value is int && (int)matches[0].Constant.Value == value,
                        "ErrorCodes", "Stable error-code name/value changed: " + ErrorNames[value]);
                }
                var root = new Dictionary<string, string>(StringComparer.Ordinal) {
                    { "schemaVersion", "System.Int32" }, { "enabled", "System.Boolean" }, { "stateCode", "System.Int32" }, { "state", "System.String" },
                    { "classes", ClassInfo + "[]" },
                };
                foreach (string name in new[] { "generation", "methodChecks", "shadowMethodChecks", "rejectedBaselineMethods", "baselineClassCctorStarted",
                    "shadowClassCctorStarted", "interpreterTransformations", "shadowInterpreterTransformations", "droppedClassObservations" }) root.Add(name, "System.UInt64");
                var row = new Dictionary<string, string>(StringComparer.Ordinal) { { "executionModeCode", "System.Int32" } };
                foreach (string name in new[] { "logicalAssembly", "typeKey", "executionMode", "physicalImageKind", "staticStoragePointer" }) row.Add(name, "System.String");
                foreach (string name in new[] { "isActive", "cctorStarted", "cctorFinished", "hasInitializationException", "pointerDetailsAvailable", "staticStorageAvailable" }) row.Add(name, "System.Boolean");
                VerifyFields(module.Find(Diagnostics, false), root); VerifyFields(module.Find(ClassInfo, false), row);
                VerifyFields(module.Find(MetadataCapacity, false), new Dictionary<string, string>(StringComparer.Ordinal) {
                    { "schemaVersion", "System.Int32" }, { "enabled", "System.Boolean" }, { "profileVersion", "System.Int32" },
                    { "indexBits", "System.Int32" }, { "kindBits", "System.Int32" }, { "cursors", "System.UInt32[]" },
                    { "remainingSlots", "System.UInt32[]" }, { "requiredImages", "System.UInt32" }, { "acceptedImages", "System.UInt32" },
                    { "firstFailingIndex", "System.Int32" }, { "firstFailingSize", "System.UInt64" }, { "failureReason", "System.String" },
                    { "fits", "System.Boolean" }, { "allocations", MetadataAllocation + "[]" }, { "finalCursors", "System.UInt32[]" },
                    { "ordinaryAllocatedCount", "System.UInt64" }, { "shadowAllocatedCount", "System.UInt64" }, { "reservedImageCount", "System.UInt64" },
                });
                VerifyFields(module.Find(MetadataAllocation, false), new Dictionary<string, string>(StringComparer.Ordinal) {
                    { "imageIndex", "System.UInt32" }, { "kind", "System.Int32" }, { "dllSize", "System.UInt64" },
                });
                VerifyFields(module.Find(RecoveryInfo, false), new Dictionary<string, string>(StringComparer.Ordinal) {
                    { "schemaVersion", "System.Int32" }, { "enabled", "System.Boolean" }, { "capabilityVersion", "System.Int32" },
                    { "stateCode", "System.Int32" }, { "state", "System.String" }, { "published", "System.Boolean" },
                    { "abortAllowed", "System.Boolean" }, { "dispositionCode", "System.Int32" }, { "disposition", "System.String" },
                    { "terminalFailureCode", "System.Int32" }, { "reason", "System.String" }, { "retainedBytes", "System.UInt64" },
                    { "baselineEligibilityRequiresStartupValidation", "System.Boolean" },
                });
            }
            VerifyPreserve(input.Find(Diagnostics, false)); VerifyPreserve(input.Find(ClassInfo, false));
            VerifyPreserve(input.Find(MetadataCapacity, false)); VerifyPreserve(input.Find(MetadataAllocation, false)); VerifyPreserve(input.Find(RecoveryInfo, false));
        }

        private static string[] VerifyBootstrap(IDictionary<string, ModuleDef> before, IDictionary<string, ModuleDef> after)
        {
            ModuleDef input = before[Bootstrap], linked = after[Bootstrap];
            Require(input.Assembly.FullName == linked.Assembly.FullName, "BootstrapIdentity", "Bootstrap identity changed after linking.");
            var roots = RequiredBootstrapRoots.Concat(AdditionalJsonRoots.Where(name => input.Find(name, false) != null)).ToArray();
            ShadowDiagnosticSchemaProof.Verify(input, linked, roots, "M06Execution", before, after, allowCoreLibraryLists: true);
            VerifyArtifactDto(typeof(M06PlayerBuildReceipt), input.Find(Probe + "PlayerBuildReceipt", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M06FixtureManifest), input.Find(Probe + "FixtureManifest", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M05TypeProof), input.Find(Probe + "TypeProof", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M06ExecutionProof), input.Find(Probe + "ExecutionProof", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M06GenerationProof), input.Find(Probe + "GenerationProof", false), new HashSet<string>());
            VerifyArtifactDto(typeof(M06ExecutionPolicyProof), input.Find(Probe + "ExecutionPolicyProof", false), new HashSet<string>());
            VerifyJsonInputCalls(input, roots); VerifyJsonInputCalls(linked, roots);
            return roots;
        }

        internal static void VerifyJsonInputCalls(ModuleDef module, string[] roots)
        {
            TypeDef probe = module.Find(Probe.TrimEnd('/'), false);
            var helpers = probe == null ? new MethodDef[0] : probe.Methods.Where(method => method.Name == "ReadJson").ToArray();
            Require(helpers.Length <= 1, "JsonRoot", "Only one exact finite JSON input helper is admitted.");
            MethodDef helper = helpers.SingleOrDefault();
            if (helper != null)
            {
                var result = helper.MethodSig == null ? null : helper.MethodSig.RetType as GenericMVar;
                Require(helper.IsPrivate && helper.IsStatic && helper.HasBody && helper.GenericParameters.Count == 1 && result != null && result.Number == 0 &&
                    helper.MethodSig.GenParamCount == 1 && helper.MethodSig.Params.Count == 1 && helper.MethodSig.Params[0].FullName == "System.String",
                    "JsonRoot", "JSON helper must remain private static T ReadJson<T>(string), not a runtime Type selector.");
            }
            int helperCalls = 0, helperDeserializers = 0;
            foreach (var type in module.GetTypes())
                foreach (var method in type.Methods.Where(method => method.HasBody))
                    foreach (var instruction in method.Body.Instructions)
                    {
                        var call = instruction.Operand as IMethod;
                        if (call == null) continue;
                        var spec = call as MethodSpec;
                        if (call.DeclaringType.FullName == Probe.TrimEnd('/') && call.Name == "ReadJson")
                        {
                            Require(helper != null && spec != null && ReferenceEquals(spec.Method, helper) && instruction.OpCode == OpCodes.Call &&
                                ClosedRoot(spec, roots, module), "JsonRoot", "ReadJson must only be directly called with finite captured DTO roots, never an open/delegate/reflection escape: " + method.FullName);
                            ++helperCalls;
                        }
                        bool scoped = type.FullName == Probe.TrimEnd('/') || type.FullName.StartsWith(Probe, StringComparison.Ordinal) ||
                            type.FullName == "AssemblyShadowDemo.M06BootstrapRunner" || type.FullName.StartsWith("AssemblyShadowDemo.M06BootstrapRunner/", StringComparison.Ordinal) ||
                            type.FullName == "AssemblyShadowDemo.M04OrdinaryAssemblyProbe" || type.FullName.StartsWith("AssemblyShadowDemo.M04OrdinaryAssemblyProbe/", StringComparison.Ordinal);
                        if (!scoped || call.DeclaringType.FullName != "UnityEngine.JsonUtility" || !call.Name.String.StartsWith("FromJson", StringComparison.Ordinal)) continue;
                        Require(call.Name == "FromJson" && instruction.OpCode == OpCodes.Call && spec != null && spec.GenericInstMethodSig.GenericArguments.Count == 1,
                            "JsonRoot", "JSON inputs require typed FromJson, not overwrite/runtime-Type deserialization: " + method.FullName);
                        if (ReferenceEquals(method, helper))
                        {
                            var argument = spec.GenericInstMethodSig.GenericArguments[0] as GenericMVar;
                            Require(argument != null && argument.Number == 0, "JsonRoot", "The finite JSON helper must directly deserialize its own method type parameter.");
                            ++helperDeserializers;
                        }
                        else Require(ClosedRoot(spec, roots, module), "JsonRoot", "Every direct JSON input requires an explicit captured schema root: " + method.FullName);
                    }
            Require(helper == null || (helperCalls > 0 && helperDeserializers == 1), "JsonRoot", "The finite helper must have actual closed callers and exactly one direct deserializer.");
        }

        private static bool ClosedRoot(MethodSpec method, string[] roots, ModuleDef module)
        {
            if (method.GenericInstMethodSig.GenericArguments.Count != 1) return false;
            TypeSig argument = method.GenericInstMethodSig.GenericArguments[0];
            return !argument.ContainsGenericParameter && roots.Contains(argument.FullName) && argument.DefinitionAssembly != null &&
                argument.DefinitionAssembly.FullName == module.Assembly.FullName && module.Find(argument.FullName, false) != null;
        }

        private static M06ExecutionSchemaType[] ReadSchemaGraph(IDictionary<string, ModuleDef> modules, string[] bootstrapRoots, string side,
            IDictionary<string, ModuleDef> linkedModules)
        {
            var pending = new Queue<TypeDef>(bootstrapRoots.Select(root => modules[Bootstrap].Find(root, false)));
            foreach (string root in new[] { "HybridCLR.AssemblyShadowDiagnostics", "HybridCLR.AssemblyShadowTypeResolutionInfo", Diagnostics, ClassInfo,
                MetadataCapacity, MetadataAllocation, RecoveryInfo })
                pending.Enqueue(modules[Runtime].Find(root, false));
            var visited = new HashSet<string>(StringComparer.Ordinal); var result = new List<M06ExecutionSchemaType>();
            while (pending.Count != 0)
            {
                TypeDef type = pending.Dequeue();
                Require(type != null && type.IsSerializable, "Schema", "Missing captured serializable schema node.");
                if (!visited.Add(type.Module.Assembly.FullName + "|" + type.FullName)) continue;
                if (side == "PlayerInput" && (type.FullName.StartsWith(Probe, StringComparison.Ordinal) || type.FullName == Diagnostics || type.FullName == ClassInfo)) VerifyPreserve(type);
                var fields = type.Fields.Where(field => field.IsPublic && !field.IsStatic && !field.IsNotSerialized).OrderBy(field => field.Name.String, StringComparer.Ordinal).ToArray();
                result.Add(new M06ExecutionSchemaType { side = side, assemblyName = type.Module.Assembly.Name.String, assemblyIdentity = type.Module.Assembly.FullName,
                    typeName = type.FullName, typeAttributes = (int)type.Attributes, isSerializable = type.IsSerializable,
                    fields = fields.Select(field => new M06ExecutionSchemaField { name = field.Name.String, type = field.FieldType.AssemblyQualifiedName,
                        resolvedType = ResolvedSchemaFieldType(field, linkedModules), attributes = (int)field.Attributes }).ToArray() });
                foreach (FieldDef field in fields)
                {
                    TypeSig element = Unwrap(field.FieldType, type.Module);
                    if (element.IsPrimitive || element.ElementType == ElementType.String) continue;
                    ModuleDef owner;
                    Require(element.DefinitionAssembly != null && (element.DefinitionAssembly.Name == Bootstrap || element.DefinitionAssembly.Name == Runtime) &&
                        modules.TryGetValue(element.DefinitionAssembly.Name.String, out owner),
                        "Schema", "Schema child must come from the exact captured module set: " + field.FullName);
                    owner = modules[element.DefinitionAssembly.Name.String];
                    Require(element.DefinitionAssembly.FullName == owner.Assembly.FullName, "Schema", "Schema child identity differs: " + field.FullName);
                    pending.Enqueue(owner.Find(element.FullName, false));
                }
            }
            return result.OrderBy(row => row.assemblyName, StringComparer.Ordinal).ThenBy(row => row.typeName, StringComparer.Ordinal).ToArray();
        }

        internal static string ResolvedSchemaFieldType(FieldDef source, IDictionary<string, ModuleDef> linkedModules)
        {
            Require(source != null && source.DeclaringType != null && source.Module != null && source.FieldType != null,
                "SchemaResolution", "A captured declared field is required.");
            ModuleDef owner = ExactLinkedSchemaModule(source.Module.Assembly, linkedModules);
            var types = owner.GetTypes().Where(type => type.FullName == source.DeclaringType.FullName).ToArray();
            Require(types.Length == 1, "SchemaResolution", "The exact linked schema owner is missing or ambiguous: " + source.FullName);
            var fields = types[0].Fields.Where(field => field.Name == source.Name).ToArray();
            Require(fields.Length == 1 && fields[0].Attributes == source.Attributes &&
                SameSchemaSignatureShape(source.FieldType, fields[0].FieldType, source.Module, owner, 0),
                "SchemaResolution", "The actual linked field changed its declaration shape: " + source.FullName);
            // Unity can rewrite netstandard compiler signatures to implementation
            // signatures during linking. Preserve each declared AQN independently;
            // resolve this actual linked signature, never a name-only substitution.
            return ResolveLinkedSchemaSignature(fields[0].FieldType, linkedModules, 0).AssemblyQualifiedName;
        }

        private static bool SameSchemaSignatureShape(TypeSig declared, TypeSig linked, ModuleDef declaredModule, ModuleDef linkedModule, int depth)
        {
            if (declared == null || linked == null || declaredModule == null || linkedModule == null || depth >= 64 ||
                declared.ContainsGenericParameter || linked.ContainsGenericParameter) return false;
            var declaredArray = declared as SZArraySig; var linkedArray = linked as SZArraySig;
            if (declaredArray != null || linkedArray != null)
                return declaredArray != null && linkedArray != null &&
                    SameSchemaSignatureShape(declaredArray.Next, linkedArray.Next, declaredModule, linkedModule, depth + 1);
            var declaredGeneric = declared as GenericInstSig; var linkedGeneric = linked as GenericInstSig;
            if (declaredGeneric != null || linkedGeneric != null)
            {
                if (declaredGeneric == null || linkedGeneric == null || declaredGeneric.GenericType == null || linkedGeneric.GenericType == null ||
                    declaredGeneric.GenericType.FullName != linkedGeneric.GenericType.FullName || declaredGeneric.GenericType.IsValueType != linkedGeneric.GenericType.IsValueType ||
                    declaredGeneric.GenericArguments.Count != linkedGeneric.GenericArguments.Count ||
                    !SameSchemaDefinitionScope(declaredGeneric.GenericType, linkedGeneric.GenericType, declaredModule, linkedModule)) return false;
                for (int index = 0; index < declaredGeneric.GenericArguments.Count; ++index)
                    if (!SameSchemaSignatureShape(declaredGeneric.GenericArguments[index], linkedGeneric.GenericArguments[index], declaredModule, linkedModule, depth + 1)) return false;
                return true;
            }
            bool declaredLeaf = declared is CorLibTypeSig || declared is ClassOrValueTypeSig;
            bool linkedLeaf = linked is CorLibTypeSig || linked is ClassOrValueTypeSig;
            return declaredLeaf && linkedLeaf && declared.FullName == linked.FullName && declared.IsValueType == linked.IsValueType &&
                SameSchemaDefinitionScope(declared, linked, declaredModule, linkedModule);
        }

        private static bool SameSchemaDefinitionScope(TypeSig declared, TypeSig linked, ModuleDef declaredModule, ModuleDef linkedModule)
        {
            IAssembly declaredIdentity = declared.DefinitionAssembly, linkedIdentity = linked.DefinitionAssembly;
            if (declaredIdentity == null || linkedIdentity == null) return false;
            if (AssemblyNameComparer.CompareAll.Equals(declaredIdentity, linkedIdentity)) return true;
            IAssembly declaredCore = declaredModule.CorLibTypes == null ? null : declaredModule.CorLibTypes.AssemblyRef;
            IAssembly linkedCore = linkedModule.CorLibTypes == null ? null : linkedModule.CorLibTypes.AssemblyRef;
            return declaredCore != null && linkedCore != null && AssemblyNameComparer.CompareAll.Equals(declaredIdentity, declaredCore) &&
                AssemblyNameComparer.CompareAll.Equals(linkedIdentity, linkedCore);
        }

        private static TypeSig ResolveLinkedSchemaSignature(TypeSig signature, IDictionary<string, ModuleDef> modules, int depth)
        {
            Require(signature != null && depth < 64 && !signature.ContainsGenericParameter, "SchemaResolution", "Open or excessively nested schema signature.");
            if (signature is SZArraySig) return new SZArraySig(ResolveLinkedSchemaSignature(signature.Next, modules, depth + 1));
            var generic = signature as GenericInstSig;
            if (generic != null)
            {
                Require(generic.GenericType != null && generic.GenericType.FullName == "System.Collections.Generic.List`1" && generic.GenericArguments.Count == 1,
                    "SchemaResolution", "Only the declared closed List<T> schema container is supported.");
                TypeDef definition = ResolveLinkedSchemaDefinition(generic.GenericType.TypeDefOrRef, modules);
                Require(!definition.IsValueType && definition.GenericParameters.Count == 1, "SchemaResolution", "The actual linked List definition differs.");
                return new GenericInstSig(new ClassSig(definition), ResolveLinkedSchemaSignature(generic.GenericArguments[0], modules, depth + 1));
            }
            Require(signature is CorLibTypeSig || signature is ClassOrValueTypeSig, "SchemaResolution", "Unsupported schema signature: " + signature.FullName);
            TypeDef leaf = ResolveLinkedSchemaDefinition(signature.ToTypeDefOrRef(), modules);
            Require(leaf.GenericParameters.Count == 0, "SchemaResolution", "Unconstructed generic schema definition.");
            return leaf.IsValueType ? (TypeSig)new ValueTypeSig(leaf) : new ClassSig(leaf);
        }

        private static ModuleDef ExactLinkedSchemaModule(IAssembly identity, IDictionary<string, ModuleDef> modules)
        {
            Require(identity != null && modules != null, "SchemaResolution", "Missing exact linked definition scope.");
            var matches = modules.Values.Where(module => module != null && module.Assembly != null &&
                AssemblyIdentityUtil.CanonicalName(module.Assembly.Name) == AssemblyIdentityUtil.CanonicalName(identity.Name)).ToArray();
            Require(matches.Length == 1 && AssemblyNameComparer.CompareAll.Equals(identity, matches[0].Assembly) && matches[0].Assembly.Modules.Count == 1,
                "SchemaResolution", "Absent, duplicate or identity-mismatched linked definition scope: " + identity.FullName);
            return matches[0];
        }

        private static TypeDef ResolveLinkedSchemaDefinition(ITypeDefOrRef reference, IDictionary<string, ModuleDef> modules)
        {
            Require(reference != null && reference.DefinitionAssembly != null, "SchemaResolution", "Missing linked type reference.");
            string name = reference.FullName;
            IAssembly identity = reference.DefinitionAssembly;
            var visited = new HashSet<string>(StringComparer.Ordinal);
            for (int depth = 0; depth < 32; ++depth)
            {
                ModuleDef module = ExactLinkedSchemaModule(identity, modules);
                Require(visited.Add(module.Assembly.FullName + "|" + name), "SchemaResolution", "Cyclic linked type forwarding.");
                var definitions = module.GetTypes().Where(type => type.FullName == name).ToArray();
                var exports = module.ExportedTypes.Where(type => type.FullName == name).ToArray();
                Require(definitions.Length + exports.Length == 1, "SchemaResolution", "Linked definition or forwarder is missing or ambiguous: " + name);
                if (definitions.Length == 1) return definitions[0];
                ExportedType export = exports[0];
                var exportPath = new HashSet<ExportedType>();
                AssemblyRef target = null;
                while (export != null && exportPath.Count < 32 && exportPath.Add(export))
                {
                    target = export.Implementation as AssemblyRef;
                    if (target != null)
                    {
                        Require(export.IsForwarder, "SchemaResolution", "Linked export is not a type forwarder.");
                        break;
                    }
                    var parent = export.Implementation as ExportedType;
                    Require(parent != null && parent.Module == module && module.ExportedTypes.Count(item => item.FullName == parent.FullName) == 1,
                        "SchemaResolution", "Invalid nested linked forwarder.");
                    export = parent;
                }
                Require(target != null, "SchemaResolution", "Cyclic or unsupported linked export target.");
                identity = target;
            }
            throw new ShadowBuildException("M06ExecutionSchemaResolution", "Linked type forwarding exceeds the bounded schema policy.");
        }

        private static void VerifyArtifactDto(System.Type expected, TypeDef actual, HashSet<string> visited)
        {
            Require(actual != null, "ArtifactSchema", "Missing captured artifact DTO for " + expected.FullName);
            if (!visited.Add(expected.FullName + "|" + actual.FullName)) return;
            var expectedFields = expected.GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
            var fields = actual.Fields.Where(field => field.IsPublic && !field.IsStatic && !field.IsNotSerialized).ToArray();
            Require(fields.Length == expectedFields.Length, "ArtifactSchema", "Editor/runtime artifact field count differs: " + actual.FullName);
            foreach (var expectedField in expectedFields)
            {
                var matches = fields.Where(field => field.Name == expectedField.Name).ToArray();
                Require(matches.Length == 1, "ArtifactSchema", "Editor/runtime artifact field differs: " + actual.FullName + "." + expectedField.Name);
                System.Type type = expectedField.FieldType; TypeSig signature = matches[0].FieldType;
                while (type.IsArray)
                {
                    Require(signature is SZArraySig && type.GetArrayRank() == 1, "ArtifactSchema", "Artifact array shape differs: " + expectedField.Name);
                    type = type.GetElementType(); signature = signature.Next;
                }
                if (type.IsPrimitive || type == typeof(string))
                    Require(type.FullName == signature.FullName, "ArtifactSchema", "Artifact primitive type differs: " + expectedField.Name);
                else
                {
                    Require(signature.DefinitionAssembly != null && signature.DefinitionAssembly.FullName == actual.Module.Assembly.FullName,
                        "ArtifactSchema", "Artifact child must be captured in Bootstrap: " + expectedField.Name);
                    VerifyArtifactDto(type, actual.Module.Find(signature.FullName, false), visited);
                }
            }
        }

        private static TypeSig Unwrap(TypeSig signature, ModuleDef owner)
        {
            for (int depth = 0; depth < 64; ++depth)
            {
                if (signature is SZArraySig) { signature = signature.Next; continue; }
                var list = signature as GenericInstSig;
                if (list == null) return signature;
                Require(list.GenericType != null && list.GenericType.FullName == "System.Collections.Generic.List`1" && list.GenericArguments.Count == 1 &&
                    list.GenericType.DefinitionAssembly != null && list.GenericType.DefinitionAssembly.FullName == owner.CorLibTypes.AssemblyRef.FullName && !list.ContainsGenericParameter,
                    "Schema", "Only closed captured CoreLib List<T> is admitted in a schema: " + signature.FullName);
                signature = list.GenericArguments[0];
            }
            throw new ShadowBuildException("M06ExecutionSchema", "Excessive schema collection nesting.");
        }

        private static void VerifyFields(TypeDef type, IDictionary<string, string> expected)
        {
            Require(type != null && type.IsSerializable, "Fields", "Execution diagnostics must be serializable.");
            var fields = type.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray();
            Require(fields.Length == expected.Count && fields.All(field => expected.ContainsKey(field.Name.String) && expected[field.Name.String] == field.FieldType.FullName),
                "Fields", "Execution diagnostics must retain the exact 14/12 typed field contract: " + type.FullName);
        }

        private static void VerifyPreserve(TypeDef type)
        {
            Require(type != null && type.IsSerializable && TrustedPreserve(type.CustomAttributes, type.Module), "Preserve", "Execution DTO must explicitly preserve its source type.");
            foreach (var field in type.Fields.Where(field => field.IsPublic && !field.IsStatic && !field.IsNotSerialized))
                Require(TrustedPreserve(field.CustomAttributes, type.Module), "Preserve", "Execution DTO fields must explicitly preserve zero/false values: " + field.FullName);
        }

        private static bool TrustedPreserve(IEnumerable<CustomAttribute> attributes, ModuleDef module)
        {
            var values = attributes.Where(attribute => attribute.AttributeType.FullName == "UnityEngine.Scripting.PreserveAttribute").ToArray();
            if (values.Length != 1) return false;
            IAssembly owner = values[0].AttributeType.DefinitionAssembly;
            return owner != null && owner.Name == "UnityEngine.CoreModule" && module.GetAssemblyRefs().Any(reference => reference.FullName == owner.FullName);
        }

        private sealed class CapturedFile { internal string name, path, sha256, pdbPath, pdbSha256; }

        private static CapturedFile FindFile(string root, AssemblySnapshotReceipt receipt, string name, bool linked)
        {
            if (linked)
            {
                var matches = receipt.linkedPlayerReceipt.assemblies.Where(entry => AssemblyIdentityUtil.CanonicalName(entry.name) == AssemblyIdentityUtil.CanonicalName(name)).ToArray();
                Require(matches.Length == 1, "Module", "Exactly one captured linked module required: " + name);
                var file = matches[0]; string directory = Path.Combine(root, ShadowLinkedPlayerEvidence.DirectoryName);
                return new CapturedFile { name = file.name, path = ShadowHash.SafeChild(directory, file.path), sha256 = file.sha256,
                    pdbPath = string.IsNullOrEmpty(file.pdbPath) ? "" : ShadowHash.SafeChild(directory, file.pdbPath), pdbSha256 = file.pdbSha256 ?? "" };
            }
            else
            {
                var matches = receipt.assemblies.Where(entry => AssemblyIdentityUtil.CanonicalName(entry.name) == AssemblyIdentityUtil.CanonicalName(name)).ToArray();
                Require(matches.Length == 1, "Module", "Exactly one captured Player input module required: " + name);
                var file = matches[0];
                return new CapturedFile { name = file.name, path = ShadowHash.SafeChild(root, file.path), sha256 = file.sha256,
                    pdbPath = string.IsNullOrEmpty(file.pdbPath) ? "" : ShadowHash.SafeChild(root, file.pdbPath), pdbSha256 = file.pdbSha256 ?? "" };
            }
        }

        private static ModuleDefMD ReadModule(CapturedFile file, bool symbols = false)
        {
            byte[] bytes = File.ReadAllBytes(file.path);
            Require(ShadowHash.Bytes(bytes) == file.sha256, "ModuleBytes", "Captured DLL changed: " + file.path);
            var options = new ModuleCreationOptions { TryToLoadPdbFromDisk = false };
            if (symbols && !string.IsNullOrEmpty(file.pdbPath))
            {
                byte[] pdb = File.ReadAllBytes(file.pdbPath);
                Require(ShadowHash.Bytes(pdb) == file.pdbSha256, "SymbolBytes", "Captured PDB changed: " + file.pdbPath);
                options.PdbFileOrData = pdb;
            }
            var module = ModuleDefMD.Load(bytes, options);
            if (module.Assembly == null || AssemblyIdentityUtil.CanonicalName(module.Assembly.Name) != AssemblyIdentityUtil.CanonicalName(file.name) || !module.Mvid.HasValue)
            { module.Dispose(); throw new ShadowBuildException("M06ExecutionModuleIdentity", "Captured module identity differs: " + file.path); }
            if (symbols && !string.IsNullOrEmpty(file.pdbPath) && module.PdbState == null)
            { module.Dispose(); throw new ShadowBuildException("M06ExecutionSymbols", "Captured PDB did not bind to its actual DLL: " + file.pdbPath); }
            return module;
        }

        private static M06ExecutionImage ReadImage(CapturedFile file, string role, string planId, string snapshotHash, string planHash, bool shadow)
        {
            var identity = M04AssemblyIdentityProof.ReadFile(file.path, file.sha256, file.name);
            M06ExecutionMethod[] methods;
            using (var module = ReadModule(file, true))
            {
                VerifyWitnessBoundary(module, shadow);
                methods = module.GetTypes().SelectMany(type => type.Methods).OrderBy(method => method.MDToken.Raw).Select(ReadMethod).ToArray();
                Require(methods.Length != 0 && methods.Select(method => method.metadataToken).Distinct().Count() == methods.Length,
                    "Methods", "Actual method-token inventory is empty or ambiguous: " + file.name);
            }
            VerifyHash(file.path, file.sha256);
            if (!string.IsNullOrEmpty(file.pdbPath)) VerifyHash(file.pdbPath, file.pdbSha256);
            return new M06ExecutionImage { role = role, planId = planId, compileSnapshotHash = snapshotHash, planHash = planHash,
                identity = identity, pdbPath = file.pdbPath ?? "", pdbSha256 = file.pdbSha256 ?? "", pdbAvailable = !string.IsNullOrEmpty(file.pdbPath), methods = methods };
        }

        private static void VerifyWitnessBoundary(ModuleDef module, bool shadow)
        {
            string name = module.Assembly.Name.String;
            string typeName = name == "AssemblyShadowDemo.ContractsConsumer" ? "AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness" :
                name == "AssemblyShadowDemo.ExtensibilityConsumer" ? "AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness" : name + ".M06ExecutionWitness";
            TypeDef type = module.Find(typeName, false);
            Require(type != null, "Witness", "Actual candidate execution witness was stripped or omitted: " + typeName);
            foreach (string methodName in new[] { "Run", "GetModuleEvidence", "RunAsync", "RunCoroutine", "WarmupValue", "WarmupEcho", "ThrowForEvidence" })
            {
                var methods = type.Methods.Where(method => method.Name == methodName).ToArray();
                Require(methods.Length == 1 && methods[0].IsPublic && methods[0].IsStatic && methods[0].HasBody && WitnessSignature(methods[0]),
                    "Witness", "Actual preserved fixed witness boundary is missing: " + typeName + "::" + methodName);
            }
            string initializerName = name == "AssemblyShadowDemo.ContractsConsumer" ? "AssemblyShadowDemo.Consumers.ContractsConsumerM06ModuleInitializer" :
                name == "AssemblyShadowDemo.ExtensibilityConsumer" ? "AssemblyShadowDemo.Consumers.ExtensibilityConsumerM06ModuleInitializer" : name + ".M06ModuleInitializer";
            var initializers = module.GetTypes().Where(candidate => candidate.FullName == initializerName).ToArray();
            var cctors = module.GlobalType.Methods.Where(method => method.IsStaticConstructor).ToArray();
            if (shadow)
            {
                Require(initializers.Length == 1 && cctors.Length == 1 && cctors[0].HasBody, "Initializer", "Shadow image lacks its actual module initializer: " + name);
                Require(cctors[0].Body.Instructions.Count(instruction => instruction.OpCode == OpCodes.Call && instruction.Operand is IMethod &&
                    ((IMethod)instruction.Operand).DeclaringType.FullName == initializers[0].FullName && ((IMethod)instruction.Operand).Name == "Initialize") == 1,
                    "Initializer", "Module .cctor must call the actual M06 initializer exactly once: " + name);
            }
            else Require(initializers.Length == 0, "Initializer", "Baseline compiler/linked image unexpectedly contains a patch module initializer: " + name);
        }

        private static bool WitnessSignature(MethodDef method)
        {
            MethodSig signature = method.MethodSig;
            if (signature == null || signature.HasThis || signature.ParamsAfterSentinel != null) return false;
            var parameters = signature.Params;
            if (method.Name == "WarmupEcho")
                return method.GenericParameters.Count == 1 && signature.GenParamCount == 1 && parameters.Count == 1 &&
                    signature.RetType is GenericMVar && ((GenericMVar)signature.RetType).Number == 0 &&
                    parameters[0] is GenericMVar && ((GenericMVar)parameters[0]).Number == 0;
            if (method.GenericParameters.Count != 0 || signature.GenParamCount != 0) return false;
            if (method.Name == "ThrowForEvidence") return signature.RetType.FullName == "System.Void" && parameters.Count == 0 && method.IsNoInlining;
            if (method.Name == "Run") return StringArray(signature.RetType) && parameters.Count == 1 && parameters[0].FullName == "System.String";
            if (method.Name == "GetModuleEvidence") return StringArray(signature.RetType) && parameters.Count == 0;
            if (method.Name == "WarmupValue") return signature.RetType.FullName == "System.Int32" && parameters.Count == 1 && parameters[0].FullName == "System.Int32";
            if (method.Name == "RunAsync")
            {
                var task = signature.RetType as GenericInstSig;
                return parameters.Count == 0 && task != null && task.GenericType.FullName == "System.Threading.Tasks.Task`1" &&
                    task.GenericArguments.Count == 1 && StringArray(task.GenericArguments[0]);
            }
            if (method.Name == "RunCoroutine")
            {
                var list = parameters.Count == 1 ? parameters[0] as GenericInstSig : null;
                return signature.RetType.FullName == "System.Collections.IEnumerator" && list != null &&
                    list.GenericType.FullName == "System.Collections.Generic.List`1" && list.GenericArguments.Count == 1 && list.GenericArguments[0].FullName == "System.String";
            }
            return false;
        }

        private static bool StringArray(TypeSig signature)
        { return signature is SZArraySig && signature.Next.FullName == "System.String"; }

        internal static M06ExecutionMethod ReadMethod(MethodDef method)
        {
            Require(method != null && method.MethodSig != null, "Method", "A declared captured method is required.");
            CilBody body = method.Body;
            return new M06ExecutionMethod {
                declaringType = method.DeclaringType.ReflectionFullName, name = method.Name.String, signature = method.FullName,
                metadataToken = unchecked((int)method.MDToken.Raw), genericArity = method.GenericParameters.Count,
                methodFlags = (int)method.Attributes, implementationFlags = (int)method.ImplAttributes,
                isStatic = method.IsStatic, hasBody = method.HasBody, initLocals = body != null && body.InitLocals, maxStack = body == null ? 0 : body.MaxStack,
                returnType = SignatureType(method.MethodSig.RetType), parameterTypes = method.MethodSig.Params.Select(SignatureType).ToArray(),
                genericParameterNames = method.GenericParameters.OrderBy(parameter => parameter.Number).Select(parameter => parameter.Name.String).ToArray(),
                locals = body == null ? new string[0] : body.Variables.Select(local => local.Type.AssemblyQualifiedName).ToArray(),
                instructions = body == null ? new string[0] : body.Instructions.Select((instruction, index) => index.ToString("D4", CultureInfo.InvariantCulture) + ":" + instruction.OpCode.Name + Operand(body, instruction.Operand)).ToArray(),
                exceptionHandlers = body == null ? new M06ExecutionExceptionHandler[0] : body.ExceptionHandlers.Select(handler => new M06ExecutionExceptionHandler {
                    handlerType = handler.HandlerType.ToString(), catchType = handler.CatchType == null ? "" : handler.CatchType.AssemblyQualifiedName,
                    tryStart = Boundary(body, handler.TryStart, false), tryEnd = Boundary(body, handler.TryEnd, true),
                    handlerStart = Boundary(body, handler.HandlerStart, false), handlerEnd = Boundary(body, handler.HandlerEnd, true),
                    filterStart = handler.FilterStart == null ? -1 : Boundary(body, handler.FilterStart, false),
                }).ToArray(),
                sequencePoints = body == null ? new M06ExecutionSequencePoint[0] : body.Instructions.Select((instruction, index) => {
                    var point = instruction.SequencePoint;
                    if (point == null) return null;
                    var document = point.Document;
                    return new M06ExecutionSequencePoint { instructionIndex = index, ilOffset = checked((int)instruction.Offset),
                        document = document == null ? "" : document.Url, checksumAlgorithm = document == null ? "" : document.CheckSumAlgorithmId.ToString(),
                        checksum = document == null || document.CheckSum == null ? "" : Hex(document.CheckSum),
                        startLine = point.StartLine, startColumn = point.StartColumn, endLine = point.EndLine, endColumn = point.EndColumn };
                }).Where(point => point != null).ToArray(),
            };
        }

        private static M06ExecutionSignatureType SignatureType(TypeSig type)
        { return new M06ExecutionSignatureType { assembly = type.DefinitionAssembly == null ? "" : type.DefinitionAssembly.FullName, type = type.ReflectionFullName }; }

        private static int Boundary(CilBody body, Instruction instruction, bool end)
        {
            if (instruction == null && end) return body.Instructions.Count;
            int index = instruction == null ? -1 : body.Instructions.IndexOf(instruction);
            Require(index >= 0, "IlBoundary", "IL branch/EH target is outside the actual method body.");
            return index;
        }

        private static string Operand(CilBody body, object value)
        {
            if (value == null) return "";
            if (value is Instruction) return " branch:" + Boundary(body, (Instruction)value, false).ToString(CultureInfo.InvariantCulture);
            var targets = value as IList<Instruction>;
            if (targets != null) return " switch:" + string.Join(",", targets.Select(target => Boundary(body, target, false).ToString(CultureInfo.InvariantCulture)));
            var method = value as IMethod;
            if (method != null)
            {
                var spec = method as MethodSpec;
                return " method:" + method.FullName + " @" + method.DeclaringType.AssemblyQualifiedName +
                    (spec == null ? "" : " args:" + string.Join("|", spec.GenericInstMethodSig.GenericArguments.Select(type => type.AssemblyQualifiedName)));
            }
            var field = value as IField;
            if (field != null) return " field:" + field.FullName + " @" + field.DeclaringType.AssemblyQualifiedName;
            var typeRef = value as ITypeDefOrRef;
            if (typeRef != null) return " type:" + typeRef.AssemblyQualifiedName;
            if (value is string) return " utf8:" + Convert.ToBase64String(Encoding.UTF8.GetBytes((string)value));
            if (value is Local) return " local:" + ((Local)value).Index.ToString(CultureInfo.InvariantCulture) + ":" + ((Local)value).Type.AssemblyQualifiedName;
            if (value is Parameter) return " parameter:" + ((Parameter)value).Index.ToString(CultureInfo.InvariantCulture) + ":" + ((Parameter)value).Type.AssemblyQualifiedName;
            if (value is float) return " r4:" + BitConverter.ToInt32(BitConverter.GetBytes((float)value), 0).ToString("x8", CultureInfo.InvariantCulture);
            if (value is double) return " r8:" + BitConverter.ToInt64(BitConverter.GetBytes((double)value), 0).ToString("x16", CultureInfo.InvariantCulture);
            var signature = value as MethodSig;
            if (signature != null) return " signature:" + ((int)signature.CallingConvention).ToString(CultureInfo.InvariantCulture) + ":" + signature.GenParamCount.ToString(CultureInfo.InvariantCulture) +
                ":" + signature.RetType.AssemblyQualifiedName + "(" + string.Join("|", signature.Params.Select(type => type.AssemblyQualifiedName)) + ") after:" +
                (signature.ParamsAfterSentinel == null ? "" : string.Join("|", signature.ParamsAfterSentinel.Select(type => type.AssemblyQualifiedName)));
            if (value is IFormattable) return " " + value.GetType().FullName + ":" + ((IFormattable)value).ToString(null, CultureInfo.InvariantCulture);
            throw new ShadowBuildException("M06ExecutionIlOperand", "Unsupported actual IL operand: " + value.GetType().FullName);
        }

        private static string Hex(byte[] bytes) { return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant(); }
        private static string ApiFullName(string name) { return "HybridCLR.AssemblyShadowErrorCode HybridCLR.AssemblyShadowRuntime::" + name; }
        private static void VerifyHash(string path, string expected)
        { Require(!string.IsNullOrEmpty(expected) && File.Exists(path) && ShadowHash.File(path) == expected, "Bytes", "Captured evidence bytes changed: " + path); }
        private static void Require(bool value, string code, string message) { ShadowHash.Require(value, "M06Execution" + code, message); }
    }
}
