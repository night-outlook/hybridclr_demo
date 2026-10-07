using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Compile-only plans precede the Player. They never stand in for an admitted patch.</summary>
    public static class M06GenerationBuild
    {
        public const string ProofName = "m06-generation.json";
        public static void PrepareGenerationInputs() { Prepare(M06Build.RequestedDevelopment()); }
        public static M06GenerationProof ReadAndVerify(string proofPath) { return ReadAndVerify(proofPath, false); }

        private static void Prepare(bool development)
        {
            M06Build.ConfigureMode(development);
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            string root = M06Build.NewRoot("M06Generation-");
            var proof = new M06GenerationProof { baselineBuildId = settings.buildId, unityVersion = Application.unityVersion,
                target = target.ToString(), architecture = settings.architecture, sourcePins = pins, developmentBuild = development, selectedPlanId = "P03" };
            var plans = new List<M06GenerationPlanProof>();
            foreach (string id in new[] { "Ordinary", "P01", "P02", "P03", "InitializerFailure" })
            {
                string[] defines = id == "Ordinary" ? new string[0] : M06Build.ExpectedDefines(id);
                string[] roots = id == "Ordinary" ? new string[0] : M06Build.ExpectedChangedRoots(id);
                string directory = Path.Combine(root, id); Directory.CreateDirectory(directory);
                string snapshot = M06Build.CompileSnapshot(Path.Combine(directory, "Compile"), defines, development, policy, pins);
                var captured = AssemblySnapshot.ReadAndVerify(snapshot, false);
                ShadowCompilerModeEvidence.ReadAndVerify(snapshot, development);
                string policyPath = Path.Combine(directory, "execution-policy.json");
                M04AssemblyIdentityProof.WriteNewJson(policyPath, CaptureExecutionPolicy(snapshot, captured, policy, Path.Combine(directory, "StartupAssets")));
                string[] ordinary = SettingsUtil.HotUpdateAssemblyNamesExcludePreserved.Select(name => {
                    var file = captured.assemblies.Single(item => item.name == name);
                    return ShadowHash.SafeChild(snapshot, file.path);
                }).ToArray();
                var plan = ShadowGenerationPlan.Create(Path.Combine(directory, "Plan"), snapshot, policy, roots, ordinary);
                var link = LinkGeneratorCommand.GenerateLinkXml(plan, Path.Combine(directory, "Generated/link.xml"));
                InstallOne("Link", OutputPath(link), link.OutputSha256);
                Il2CppDefGeneratorCommand.GenerateIl2CppDef();
                var strip = StripFresh(Path.Combine(directory, "StripProject"), development);
                string stripped = Path.GetFullPath(SettingsUtil.GetAssembliesPostIl2CppStripDir(target));
                string[] collisions = Directory.GetFiles(stripped, "*.dll").Select(Path.GetFileNameWithoutExtension)
                    .Select(AssemblyIdentityUtil.CanonicalName).Intersect(plan.SelectedNames.Select(AssemblyIdentityUtil.CanonicalName))
                    .OrderBy(name => name, StringComparer.Ordinal).ToArray();
                var aot = ShadowGenerationAotInputs.Capture(Path.Combine(directory, "AotInputs"), plan, stripped, collisions);
                var bridge = MethodBridgeGeneratorCommand.GenerateMethodBridgeAndReversePInvokeWrapper(plan, aot,
                    Path.Combine(SettingsUtil.TemplatePathInPackage, "MethodBridge.cpp.tpl"), Path.Combine(directory, "Generated/MethodBridge.cpp"), development);
                var generic = AOTReferenceGeneratorCommand.GenerateAOTGenericReference(plan, aot, Path.Combine(directory, "Generated/AOTGenericReferences.cs"));
                plans.Add(new M06GenerationPlanProof { planId = id, compileSnapshot = snapshot, compileSnapshotHash = captured.snapshotHash,
                    planPath = Path.Combine(plan.Root, ShadowGenerationPlan.ReceiptName), planSha256 = ShadowHash.File(Path.Combine(plan.Root, ShadowGenerationPlan.ReceiptName)), planHash = plan.PlanHash,
                    compilerModePath = Path.Combine(snapshot, ShadowCompilerModeEvidence.ReceiptName), compilerModeSha256 = ShadowHash.File(Path.Combine(snapshot, ShadowCompilerModeEvidence.ReceiptName)),
                    defines = defines, changedRoots = roots, closureLoadOrder = plan.LoadOrder.ToArray(),
                    executionPolicyPath = policyPath, executionPolicySha256 = ShadowHash.File(policyPath),
                    aotInputPath = Path.Combine(aot.Root, ShadowGenerationAotInputs.ReceiptName), aotInputSha256 = ShadowHash.File(Path.Combine(aot.Root, ShadowGenerationAotInputs.ReceiptName)), aotInventoryHash = aot.InventoryHash,
                    stripBuildGuid = strip.guid, stripOutput = strip.output, stripBuildOptions = strip.options, stripSourceDirectory = strip.source,
                    linkReceiptPath = link.ReceiptPath, linkReceiptSha256 = ShadowHash.File(link.ReceiptPath),
                    bridgeReceiptPath = bridge.ReceiptPath, bridgeReceiptSha256 = ShadowHash.File(bridge.ReceiptPath),
                    aotReceiptPath = generic.ReceiptPath, aotReceiptSha256 = ShadowHash.File(generic.ReceiptPath),
                    requiredAotMetadataNames = RequiredMetadataNamesFromOutput(generic, plan.Closure) });
            }
            proof.plans = plans.ToArray(); proof.baselineCompileSnapshot = plans[0].compileSnapshot; proof.baselineCompileSnapshotHash = plans[0].compileSnapshotHash;
            RequireCoverage(proof);
            var selected = ReadPlan(proof, "P03");
            var selectedAot = ReadAot(selected, plans.Single(item => item.planId == "P03"));
            var selectedRow = plans.Single(item => item.planId == "P03");
            var outputs = new List<M06InstalledOutput>();
            foreach (var value in new[] {
                ShadowGenerationOutput.ReadAndVerify(selectedRow.linkReceiptPath, selected),
                ShadowGenerationOutput.ReadAndVerify(selectedRow.bridgeReceiptPath, selected, selectedAot),
                ShadowGenerationOutput.ReadAndVerify(selectedRow.aotReceiptPath, selected, selectedAot) })
                outputs.Add(new M06InstalledOutput { role = value.Stage, sourcePath = OutputPath(value), destinationPath = Slot(value.Stage), sha256 = value.OutputSha256 });
            // These ordinary placeholder/header inputs are generated explicitly;
            // GenerateAll is never called after selecting the P03 output.
            Il2CppDefGeneratorCommand.GenerateIl2CppDef();
            foreach (string role in new[] { "AssemblyManifest", "UnityVersion" })
            {
                string source = Path.Combine(root, "Common", Path.GetFileName(Slot(role))); Directory.CreateDirectory(Path.GetDirectoryName(source));
                File.Copy(Slot(role), source, false);
                outputs.Add(new M06InstalledOutput { role = role, sourcePath = source, destinationPath = Slot(role), sha256 = ShadowHash.File(source) });
            }
            proof.installedOutputs = outputs.ToArray();
            foreach (var output in proof.installedOutputs) InstallOne(output.role, output.sourcePath, output.sha256);
            string path = Path.Combine(root, ProofName); M04AssemblyIdentityProof.WriteNewJson(path, proof);
            ReadAndVerify(path, true);
            Debug.Log("[AssemblyShadow M06] Immutable generation proof selected: " + path);
            AssetDatabase.Refresh();
        }

        internal static M06GenerationProof ReadAndVerify(string path, bool requireInstalled)
        {
            M06Build.Require(Path.IsPathRooted(path) && File.Exists(path), "An explicit absolute -shadowM06Generation proof is required.");
            var proof = M04JsonEvidence.Read<M06GenerationProof>(File.ReadAllText(path));
            BuildTarget target;
            M06Build.Require(proof.schemaVersion == 1 && proof.milestone == "M06" && proof.policy == "compile-only-generator-provenance:1" &&
                Enum.TryParse(proof.target, out target) && proof.selectedPlanId == "P03" && proof.sourcePins != null &&
                proof.sourcePins.target == proof.target && proof.sourcePins.architecture == proof.architecture && proof.sourcePins.unityVersion == proof.unityVersion, "Generation context differs.");
            M06Build.RequireSafeId(proof.baselineBuildId);
            target = (BuildTarget)Enum.Parse(typeof(BuildTarget), proof.target);
            if (requireInstalled) RequireCurrentSelection(proof);
            M06Build.RequireSet(proof.plans.Select(row => row.planId), new[] { "Ordinary", "P01", "P02", "P03", "InitializerFailure" }, "Generation plan set");
            var bridges = new Dictionary<string, ShadowGenerationOutput>(StringComparer.Ordinal);
            Dictionary<string, ShadowGenerationOutput> selectedOutputs = null;
            foreach (var row in proof.plans)
            {
                var plan = ReadPlan(proof, row.planId); var receipt = AssemblySnapshot.ReadAndVerify(row.compileSnapshot, false);
                M06Build.Require(row.compilerModePath == Path.Combine(row.compileSnapshot, ShadowCompilerModeEvidence.ReceiptName), "Compiler-mode evidence must be inside its snapshot.");
                M06Build.VerifyHash(row.compilerModePath, row.compilerModeSha256);
                ShadowCompilerModeEvidence.ReadAndVerify(row.compileSnapshot, proof.developmentBuild);
                ShadowCompilerModeEvidence.ReadAndVerify(Path.Combine(plan.Root, "Snapshot"), proof.developmentBuild);
                M06Build.Require(ShadowHash.File(Path.Combine(plan.Root, "Snapshot", ShadowCompilerModeEvidence.ReceiptName)) == row.compilerModeSha256, "Copied plan compiler-mode evidence differs.");
                M06Build.Require(receipt.snapshotHash == row.compileSnapshotHash && plan.Receipt.snapshotHash == receipt.snapshotHash && plan.LoadOrder.SequenceEqual(row.closureLoadOrder), "Plan compiler/closure binding differs.");
                ShadowSourcePins.RequireSameBuildSources(proof.sourcePins, receipt.sourcePins);
                M06Build.RequireSet(row.defines, row.planId == "Ordinary" ? new string[0] : M06Build.ExpectedDefines(row.planId), "Generation defines");
                M06Build.RequireSet(ShadowReflectionBindingEvidence.UserDefines(receipt.extraScriptingDefines), row.defines, "Actual compiler defines");
                M06Build.RequireSet(row.changedRoots, row.planId == "Ordinary" ? new string[0] : M06Build.ExpectedChangedRoots(row.planId), "Generation roots");
                M06Build.RequireSet(plan.Receipt.explicitRoots, row.changedRoots.Select(AssemblyIdentityUtil.CanonicalName), "Plan explicit roots");
                if (requireInstalled) M06Build.RequireSet(plan.Receipt.ordinaryAssemblies, SettingsUtil.HotUpdateAssemblyNamesExcludePreserved.Select(AssemblyIdentityUtil.CanonicalName), "Actual ordinary hot-update input names");
                foreach (var image in plan.Receipt.images.Where(item => item.role == "Ordinary"))
                {
                    var source = receipt.assemblies.Single(item => item.name == image.name);
                    M06Build.Require(image.sourcePath == ShadowHash.SafeChild(row.compileSnapshot, source.path) && image.sha256 == source.sha256 && image.pdbSha256 == source.pdbSha256,
                        "Ordinary input must be the exact current compiler DLL/PDB, not a stale semantic substitute.");
                }
                M06Build.VerifyHash(row.executionPolicyPath, row.executionPolicySha256);
                var startup = M04JsonEvidence.Read<M06ExecutionPolicyProof>(File.ReadAllText(row.executionPolicyPath));
                M06Build.Require(startup.schemaVersion == 1 && startup.milestone == "M06" && startup.compileSnapshotHash == receipt.snapshotHash && startup.diagnostics.Length == 0, "Execution startup policy differs.");
                M06Build.VerifyHash(startup.startupScenePath, startup.startupSceneSha256); M06Build.VerifyHash(startup.bootstrapScriptPath, startup.bootstrapScriptSha256);
                foreach (var script in startup.scripts) { M06Build.VerifyHash(script.assetPath, script.assetSha256); M06Build.VerifyHash(script.scriptPath, script.scriptSha256); }
                foreach (var asset in startup.preloadedAssets) M06Build.VerifyHash(asset.assetPath, asset.sha256);
                foreach (var file in startup.files) M06Build.VerifyHash(file.path, file.sha256);
                var aot = ReadAot(plan, row);
                Guid stripGuid;
                M06Build.Require(Guid.TryParse(row.stripBuildGuid, out stripGuid) && stripGuid != Guid.Empty && Path.IsPathRooted(row.stripOutput) && Path.IsPathRooted(row.stripSourceDirectory) &&
                    Path.IsPathRooted(aot.Receipt.sourceDirectory), "Actual strip-build identity/source binding differs.");
                var link = ShadowGenerationOutput.ReadAndVerify(row.linkReceiptPath, plan);
                var bridge = ShadowGenerationOutput.ReadAndVerify(row.bridgeReceiptPath, plan, aot);
                var generic = ShadowGenerationOutput.ReadAndVerify(row.aotReceiptPath, plan, aot);
                bridges.Add(row.planId, bridge);
                if (row.planId == proof.selectedPlanId)
                    selectedOutputs = new[] { link, bridge, generic }.ToDictionary(output => output.Stage, StringComparer.Ordinal);
                M06Build.VerifyHash(row.linkReceiptPath, row.linkReceiptSha256); M06Build.VerifyHash(row.bridgeReceiptPath, row.bridgeReceiptSha256); M06Build.VerifyHash(row.aotReceiptPath, row.aotReceiptSha256);
                M06Build.Require(bridge.Development == proof.developmentBuild && (((BuildOptions)row.stripBuildOptions & BuildOptions.Development) != 0) == proof.developmentBuild, "Generation development mode differs.");
                M06Build.Require(row.requiredAotMetadataNames.SequenceEqual(RequiredMetadataNamesFromOutput(generic, plan.Closure)), "Required AOT metadata does not match actual collector output.");
            }
            var ordinary = proof.plans.Single(row => row.planId == "Ordinary");
            M06Build.Require(proof.baselineCompileSnapshot == ordinary.compileSnapshot && proof.baselineCompileSnapshotHash == ordinary.compileSnapshotHash, "Baseline/ordinary snapshot mismatch.");
            RequireCoverage(bridges); VerifyInstalled(proof, requireInstalled, selectedOutputs); return proof;
        }

        internal static VerifiedGenerationPlan ReadPlan(M06GenerationProof proof, string id)
        {
            var row = proof.plans.Single(item => item.planId == id); M06Build.VerifyHash(row.planPath, row.planSha256);
            return ShadowGenerationPlan.ReadAndVerify(Path.GetDirectoryName(row.planPath), (BuildTarget)Enum.Parse(typeof(BuildTarget), proof.target), proof.architecture, row.planHash);
        }
        internal static VerifiedGenerationAotInputs ReadAot(VerifiedGenerationPlan plan, M06GenerationPlanProof row)
        { M06Build.VerifyHash(row.aotInputPath, row.aotInputSha256); return ShadowGenerationAotInputs.ReadAndVerify(Path.GetDirectoryName(row.aotInputPath), plan, row.aotInventoryHash); }
        internal static void RequireCoverage(M06GenerationProof proof)
        {
            var outputs = proof.plans.ToDictionary(row => row.planId, row => {
                var plan = ReadPlan(proof, row.planId); return ShadowGenerationOutput.ReadAndVerify(row.bridgeReceiptPath, plan, ReadAot(plan, row));
            }, StringComparer.Ordinal);
            RequireCoverage(outputs);
        }
        private static void RequireCoverage(IDictionary<string, ShadowGenerationOutput> outputs)
        {
            ShadowGenerationOutput.RequireCoverage(outputs["P03"], outputs["Ordinary"], outputs["P01"], outputs["P02"], outputs["InitializerFailure"]);
        }
        internal static string[] RequiredMetadataNames(ShadowGenerationOutputReceipt receipt, IEnumerable<string> closure)
        {
            M06Build.Require(receipt != null && receipt.stage == "AotGenericReference" && receipt.emittedAssemblyNames != null, "Actual AOT collector output is required.");
            var excluded = new HashSet<string>(closure.Select(AssemblyIdentityUtil.CanonicalName), StringComparer.Ordinal);
            string[] names = receipt.emittedAssemblyNames.Select(name => {
                M06Build.Require(!string.IsNullOrWhiteSpace(name) && name.IndexOfAny(new[] { '/', '\\', ',' }) < 0, "Invalid emitted AOT assembly name.");
                return name.EndsWith(".dll", StringComparison.Ordinal) ? name.Substring(0, name.Length - 4) : name;
            }).ToArray();
            M06Build.Require(names.Distinct(StringComparer.Ordinal).Count() == names.Length, "Duplicate AOT collector assembly names.");
            return names.Where(name => !excluded.Contains(AssemblyIdentityUtil.CanonicalName(name))).OrderBy(name => name, StringComparer.Ordinal).ToArray();
        }
        private static string[] RequiredMetadataNamesFromOutput(ShadowGenerationOutput output, IEnumerable<string> closure)
        {
            M06Build.Require(output != null && output.Stage == "AotGenericReference", "Actual AOT collector output is required.");
            var receipt = new ShadowGenerationOutputReceipt { stage = output.Stage, emittedAssemblyNames = output.EmittedAssemblyNames };
            return RequiredMetadataNames(receipt, closure);
        }
        internal static void VerifyInstalled(M06GenerationProof proof, bool installed)
        {
            var row = proof.plans.Single(item => item.planId == "P03"); var plan = ReadPlan(proof, "P03"); var aot = ReadAot(plan, row);
            var outputs = new[] {
                ShadowGenerationOutput.ReadAndVerify(row.linkReceiptPath, plan),
                ShadowGenerationOutput.ReadAndVerify(row.bridgeReceiptPath, plan, aot),
                ShadowGenerationOutput.ReadAndVerify(row.aotReceiptPath, plan, aot),
            }.ToDictionary(output => output.Stage, StringComparer.Ordinal);
            VerifyInstalled(proof, installed, outputs);
        }
        private static void VerifyInstalled(M06GenerationProof proof, bool installed, IDictionary<string, ShadowGenerationOutput> outputs)
        {
            VerifyInstalledFiles(proof, installed);
            foreach (var item in proof.installedOutputs)
            {
                if (new[] { "Link", "MethodBridge", "AotGenericReference" }.Contains(item.role))
                {
                    ShadowGenerationOutput output;
                    M06Build.Require(outputs != null && outputs.TryGetValue(item.role, out output) && item.sourcePath == OutputPath(output) && item.sha256 == output.OutputSha256,
                        "Default slot does not bind selected P03 output.");
                }
            }
        }
        internal static void VerifyInstalledFiles(M06GenerationProof proof, bool installed)
        {
            M06Build.RequireSet(proof.installedOutputs.Select(slot => slot.role), new[] { "Link", "MethodBridge", "AotGenericReference", "AssemblyManifest", "UnityVersion" }, "Selected generator slots");
            foreach (var item in proof.installedOutputs)
            {
                M06Build.Require(Path.IsPathRooted(item.destinationPath) && (!installed || item.destinationPath == Slot(item.role)), "Generator destination is not its actual default slot.");
                M06Build.VerifyHash(item.sourcePath, item.sha256);
                if (installed) M06Build.VerifyHash(item.destinationPath, item.sha256);
            }
        }
        private static string OutputPath(ShadowGenerationOutput output)
        { return ShadowHash.SafeChild(Path.GetDirectoryName(output.ReceiptPath), output.OutputPath); }
        private static string Slot(string role)
        {
            switch (role)
            {
                case "Link": return Path.GetFullPath(Path.Combine(Application.dataPath, SettingsUtil.HybridCLRSettings.outputLinkFile));
                case "AotGenericReference": return Path.GetFullPath(Path.Combine(Application.dataPath, SettingsUtil.HybridCLRSettings.outputAOTGenericReferenceFile));
                case "MethodBridge": return Path.GetFullPath(Path.Combine(SettingsUtil.GeneratedCppDir, "MethodBridge.cpp"));
                case "AssemblyManifest": return Path.GetFullPath(Path.Combine(SettingsUtil.GeneratedCppDir, "AssemblyManifest.cpp"));
                case "UnityVersion": return Path.GetFullPath(Path.Combine(SettingsUtil.GeneratedCppDir, "UnityVersion.h"));
                default: throw new InvalidOperationException("Unknown generator slot: " + role);
            }
        }
        private static void InstallOne(string role, string source, string hash)
        {
            M06Build.VerifyHash(source, hash); string destination = Slot(role); Directory.CreateDirectory(Path.GetDirectoryName(destination)); File.Copy(source, destination, true); M06Build.VerifyHash(destination, hash);
            if (role == "Link") AssetDatabase.ImportAsset("Assets/" + SettingsUtil.HybridCLRSettings.outputLinkFile, ImportAssetOptions.ForceUpdate);
        }

        internal static void RequireCurrentSelection(M06GenerationProof proof)
        {
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            M06Build.Require(proof.baselineBuildId == settings.buildId && proof.target == target.ToString() && proof.architecture == settings.architecture && proof.unityVersion == Application.unityVersion,
                "Selected generation belongs to another baseline/target/architecture/Editor.");
            ShadowSourcePins.RequireSameBuildSources(proof.sourcePins, ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture));
        }

        internal static M06ExecutionPolicyProof CaptureExecutionPolicy(string snapshot, AssemblySnapshotReceipt receipt, ShadowPolicyConfiguration policy, string evidenceRoot = null)
        {
            Type runner = M01BuildSupport.FindType("AssemblyShadowDemo.Bootstrap", "AssemblyShadowDemo.M06BootstrapRunner");
            using (var set = ShadowFixtureProof.Load(snapshot, receipt, policy))
            {
                // Compiler inventories precede Unity's authoritative Player
                // filter/linker receipt. Validate the complete connected shadow
                // graph now; the baseline builder later runs strict validation
                // over every assembly proven to enter the linked Player.
                ShadowReflectionBindingEvidence.ValidateCompilerSnapshot(set, policy, snapshot, receipt).ThrowIfInvalid();
                var actual = ShadowExecutionPolicy.CaptureCurrentEditor(policy, runner, set);
                M06Build.Require(actual.IsValid, "Execution startup policy rejected: " + string.Join("; ", actual.Diagnostics));
                var result = new M06ExecutionPolicyProof { compileSnapshotHash = receipt.snapshotHash,
                    startupScenePath = PhysicalAsset(actual.StartupScenePath), startupSceneSha256 = ShadowHash.File(PhysicalAsset(actual.StartupScenePath)),
                    bootstrapScriptPath = PhysicalAsset(actual.BootstrapScriptPath), bootstrapScriptSha256 = ShadowHash.File(PhysicalAsset(actual.BootstrapScriptPath)),
                    bootstrapAssemblyIdentity = actual.BootstrapAssemblyIdentity, bootstrapTypeName = actual.BootstrapTypeName, bootstrapExecutionOrder = actual.BootstrapExecutionOrder,
                    diagnostics = actual.Diagnostics,
                    scripts = actual.Scripts.Select(script => new M06StartupScript { rootAssetPath = script.RootAssetPath, assetPath = PhysicalAsset(script.AssetPath), scriptPath = PhysicalAsset(script.ScriptPath),
                        assetSha256 = ShadowHash.File(PhysicalAsset(script.AssetPath)), scriptSha256 = ShadowHash.File(PhysicalAsset(script.ScriptPath)), assemblyIdentity = script.AssemblyIdentity, typeName = script.TypeName,
                        phase = script.Phase, executionOrder = script.ExecutionOrder, isCandidate = script.IsCandidate, isBootstrapRunner = script.IsBootstrapRunner,
                        isCandidateDependent = script.IsCandidateDependent, dependencyProved = script.DependencyProved, callbacks = script.Callbacks, dependencyEvidence = script.DependencyEvidence }).ToArray(),
                    preloadedAssets = actual.PreloadedAssets.Select(asset => new M06PreloadedAsset { assetPath = PhysicalAsset(asset.AssetPath), typeName = asset.TypeName,
                        assemblyIdentity = asset.AssemblyIdentity, isCandidate = asset.IsCandidate, sha256 = ShadowHash.File(PhysicalAsset(asset.AssetPath)) }).ToArray() };
                result.startupSceneSourcePath = result.startupScenePath; result.bootstrapScriptSourcePath = result.bootstrapScriptPath;
                foreach (var item in result.scripts) { item.assetSourcePath = item.assetPath; item.scriptSourcePath = item.scriptPath; }
                foreach (var item in result.preloadedAssets) item.sourcePath = item.assetPath;
                string[] sources = new[] { result.startupScenePath, result.bootstrapScriptPath }.Concat(result.scripts.SelectMany(item => new[] { item.assetPath, item.scriptPath }))
                    .Concat(result.preloadedAssets.Select(item => item.assetPath)).Distinct(StringComparer.Ordinal).OrderBy(path => path, StringComparer.Ordinal).ToArray();
                sources = sources.Concat(sources.Where(path => File.Exists(path + ".meta")).Select(path => path + ".meta")).OrderBy(path => path, StringComparer.Ordinal).ToArray();
                if (evidenceRoot != null) { M06Build.Require(!Directory.Exists(evidenceRoot) && !File.Exists(evidenceRoot), "Startup evidence output is immutable."); Directory.CreateDirectory(evidenceRoot); }
                result.files = sources.Select((path, index) => {
                    string copied = evidenceRoot == null ? path : Path.GetFullPath(Path.Combine(evidenceRoot, index.ToString("D4") + "-" + Path.GetFileName(path)));
                    string hash = ShadowHash.File(path); if (evidenceRoot != null) { File.Copy(path, copied, false); M06Build.VerifyHash(copied, hash); }
                    return new M06StartupFile { sourcePath = path, path = copied, sha256 = hash };
                }).ToArray();
                var copies = result.files.ToDictionary(file => file.sourcePath, file => file.path, StringComparer.Ordinal);
                result.startupScenePath = copies[result.startupSceneSourcePath]; result.bootstrapScriptPath = copies[result.bootstrapScriptSourcePath];
                foreach (var item in result.scripts) { item.assetPath = copies[item.assetSourcePath]; item.scriptPath = copies[item.scriptSourcePath]; }
                foreach (var item in result.preloadedAssets) item.assetPath = copies[item.sourcePath];
                return result;
            }
        }
        internal static void RequireSameStartup(M06ExecutionPolicyProof captured, M06ExecutionPolicyProof current)
        {
            // Compare the imported observations and bytes, not scratch-copy paths.
            Func<M06ExecutionPolicyProof, string> normalized = proof => {
                var copy = JsonUtility.FromJson<M06ExecutionPolicyProof>(JsonUtility.ToJson(proof));
                copy.startupScenePath = copy.startupSceneSourcePath; copy.bootstrapScriptPath = copy.bootstrapScriptSourcePath;
                foreach (var script in copy.scripts) { script.assetPath = script.assetSourcePath; script.scriptPath = script.scriptSourcePath; }
                foreach (var asset in copy.preloadedAssets) asset.assetPath = asset.sourcePath;
                foreach (var file in copy.files) file.path = file.sourcePath;
                return JsonUtility.ToJson(copy, true);
            };
            M06Build.Require(normalized(captured) == normalized(current), "Current imported startup inventory differs from verified generation inputs.");
        }
        private static string PhysicalAsset(string path)
        {
            if (path.StartsWith("Packages/", StringComparison.Ordinal))
            {
                var package = UnityEditor.PackageManager.PackageInfo.FindForAssetPath(path);
                M06Build.Require(package != null && !string.IsNullOrEmpty(package.resolvedPath), "Cannot bind imported package asset: " + path);
                string prefix = "Packages/" + package.name + "/"; M06Build.Require(path.StartsWith(prefix, StringComparison.Ordinal), "Package asset owner differs.");
                return Path.GetFullPath(Path.Combine(package.resolvedPath, path.Substring(prefix.Length)));
            }
            return Path.GetFullPath(path);
        }
        private sealed class StripResult { internal string guid, output, source; internal int options; }
        private static StripResult StripFresh(string output, bool development)
        {
            M06Build.Require(!Directory.Exists(output) && !File.Exists(output), "Strip export must be fresh.");
            var target = EditorUserBuildSettings.activeBuildTarget;
            M06Build.Require(target == BuildTarget.StandaloneOSX || target == BuildTarget.StandaloneWindows64, "M06 strip export supports the explicitly tested standalone targets only.");
            var check = typeof(SettingsUtil).Assembly.GetType("HybridCLR.Editor.BuildProcessors.CheckSettings");
            var disabled = check == null ? null : check.GetProperty("DisableMethodBridgeDevelopmentFlagChecking", BindingFlags.Public | BindingFlags.Static);
            M06Build.Require(disabled != null, "Pinned strip preprocessor seam is unavailable.");
            bool oldDisable = (bool)disabled.GetValue(null), oldScripts = EditorUserBuildSettings.buildScriptsOnly;
#if UNITY_EDITOR_OSX
            bool oldExport = UnityEditor.OSXStandalone.UserBuildSettings.createXcodeProject;
#elif UNITY_EDITOR_WIN
            bool oldExport = UnityEditor.WindowsStandalone.UserBuildSettings.createSolution;
#endif
            try
            {
                disabled.SetValue(null, true); EditorUserBuildSettings.buildScriptsOnly = true;
#if UNITY_EDITOR_OSX
                UnityEditor.OSXStandalone.UserBuildSettings.createXcodeProject = true;
#elif UNITY_EDITOR_WIN
                UnityEditor.WindowsStandalone.UserBuildSettings.createSolution = true;
#endif
                BuildOptions options = BuildOptions.CleanBuildCache | BuildOptions.DetailedBuildReport | (development ? BuildOptions.Development : BuildOptions.None);
                string location = target == BuildTarget.StandaloneWindows64 ? Path.Combine(output, "M06Strip.exe") : output;
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { M06Build.BootstrapScene }, locationPathName = location, target = target,
                    targetGroup = BuildTargetGroup.Standalone, options = options, extraScriptingDefines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]) });
                M06Build.Require(report.summary.result == BuildResult.Succeeded && ((report.summary.options & BuildOptions.Development) != 0) == development, "Actual strip build failed or changed development mode.");
                var copier = typeof(SettingsUtil).Assembly.GetType("HybridCLR.Editor.BuildProcessors.CopyStrippedAOTAssemblies");
                var locator = copier == null ? null : copier.GetMethod("GetStripAssembliesDir2021", BindingFlags.Public | BindingFlags.Static);
                M06Build.Require(locator != null, "Pinned strip output locator is unavailable.");
                string source = Path.GetFullPath((string)locator.Invoke(null, new object[] { target }));
                string copied = Path.GetFullPath(SettingsUtil.GetAssembliesPostIl2CppStripDir(target));
                M06Build.Require(Directory.GetFiles(source, "*.dll").Length > 0, "Actual strip output is empty.");
                var expected = Directory.GetFiles(source, "*.dll").ToDictionary(Path.GetFileName, ShadowHash.File, StringComparer.Ordinal);
                var actual = Directory.GetFiles(copied, "*.dll").ToDictionary(Path.GetFileName, ShadowHash.File, StringComparer.Ordinal);
                M06Build.Require(expected.Count == actual.Count && actual.All(item => expected.ContainsKey(item.Key) && expected[item.Key] == item.Value), "Copied stripped DLLs differ from actual build output.");
                return new StripResult { guid = report.summary.guid.ToString(), output = Path.GetFullPath(report.summary.outputPath), options = (int)report.summary.options, source = source };
            }
            finally
            {
                disabled.SetValue(null, oldDisable); EditorUserBuildSettings.buildScriptsOnly = oldScripts;
#if UNITY_EDITOR_OSX
                UnityEditor.OSXStandalone.UserBuildSettings.createXcodeProject = oldExport;
#elif UNITY_EDITOR_WIN
                UnityEditor.WindowsStandalone.UserBuildSettings.createSolution = oldExport;
#endif
            }
        }
    }
}
