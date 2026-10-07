using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Installer;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Adapter for a new byte-bound copy of the original M01/M07 fixture.
    /// All compilation/resource/manifest operations use the production entry
    /// points. This never authors replacement source assets or grants expansion.
    /// Python authenticates the owning Git tuple and installed root separately.
    /// </summary>
    public static class R03CompletionBuild
    {
        [Serializable] private sealed class Context
        {
            public int schemaVersion;
            public string kind, projectPath, baselineId, runPath, receiptRoot, capabilityProfile;
            public bool R03Accepted, H2Passed, expansionAuthorized;
        }
        [Serializable] private sealed class Receipt
        {
            public int schemaVersion = 1;
            public string kind = "R03OriginalResourceBuildAdapter", phase, projectPath, baselineId, unityVersion, target;
            public string sourcePinsPath, sourcePinsSha256, resourceRoot, baselineManifest, baselineManifestSha256;
            public string playerReceipt, playerReceiptSha256, fixtureManifest, fixtureManifestSha256, replayReceipt, replayReceiptSha256;
            public bool expansionAuthorized, R03Accepted, H2Passed;
        }
        [Serializable] private sealed class GenerationRow
        {
            public string patchId, compileSnapshot, snapshotHash, patchManifest, patchManifestSha256;
            public string generationRoot, generationHash, eligibilityPath, eligibilitySha256;
            public string[] installedBaselineRoots, closure, loadOrder;
            public bool expansionAuthorized;
        }
        [Serializable] private sealed class IntegrationReport
        {
            public int schemaVersion = 1;
            public string kind = "R03ProductionEntryIntegration", baselineManifest, baselineManifestSha256;
            public GenerationRow[] patches;
            public string returnToBaselineSnapshot, returnToBaselineSnapshotHash, returnGenerationRoot, returnGenerationHash;
            public string policyDomainsPath, policyDomainsSha256;
            public string[] returnChangedRoots, returnClosure;
            public bool runtimeProofExecuted, expansionAuthorized, R03Accepted, H2Passed;
        }

        [Serializable] private sealed class PolicyDomainReport
        {
            public int schemaVersion = 1;
            public string kind = "R03LiveSourcePolicyDomains", result = "Failed";
            public string projectPath, unityVersion, target, baselineSnapshotHash;
            public string sourcePolicyPath, sourcePolicySha256, linkedPolicyPath, linkedPolicySha256;
            public string[] guardProviders;
            public ShadowPolicyDiagnostic[] sourceDiagnostics, linkedPolicyDiagnostics;
            public bool sourceInventoryValidationPassed, linkedPolicyRejectedForSource, sourcePolicyUnchanged, freshUnityInventory;
            public bool runtimeAcceptance, qualificationApproved, expansionAuthorized, R03Accepted, H2Passed;
        }

        // This check uses Unity's live source/asmdef inventory, not AssemblyRef
        // rows reconstructed from already-emitted compiler DLLs. The negative
        // control proves all three original LO-001 guards remain enabled.
        private static string VerifyPolicyDomains(Context context, ShadowPolicyConfiguration source,
            string pristineSourceJson, ShadowPolicyConfiguration linked, AssemblySnapshotReceipt baseline)
        {
            string path = Path.Combine(context.receiptRoot, "compiler-policy-domains.json");
            var report = new PolicyDomainReport {
                projectPath = context.projectPath, unityVersion = Application.unityVersion,
                target = EditorUserBuildSettings.activeBuildTarget.ToString(), baselineSnapshotHash = baseline.snapshotHash,
                sourcePolicyPath = Path.Combine(context.receiptRoot, "compiler-policy-domains", "source-policy.json"),
                linkedPolicyPath = Path.Combine(context.receiptRoot, "compiler-policy-domains", "linked-policy.json"),
                guardProviders = new[] { "Unity.Burst.Unsafe", "Unity.RenderPipelines.Universal.2D.Internal", "Unity.RenderPipelines.Universal.Config.Runtime" }
            };
            string linkedJson = JsonUtility.ToJson(linked);
            Write(report.sourcePolicyPath, source); Write(report.linkedPolicyPath, linked);
            report.sourcePolicySha256 = ShadowHash.File(report.sourcePolicyPath);
            report.linkedPolicySha256 = ShadowHash.File(report.linkedPolicyPath);
            try
            {
                var good = ShadowAssemblyPolicyValidator.ValidateBeforeCompile(source, EditorUserBuildSettings.activeBuildTarget);
                var wrongDomain = ShadowAssemblyPolicyValidator.ValidateBeforeCompile(linked, EditorUserBuildSettings.activeBuildTarget);
                report.sourceDiagnostics = good.Diagnostics.ToArray();
                report.linkedPolicyDiagnostics = wrongDomain.Diagnostics.ToArray();
                report.freshUnityInventory = true;
                report.sourceInventoryValidationPassed = good.IsValid;
                report.linkedPolicyRejectedForSource = !wrongDomain.IsValid;
                report.sourcePolicyUnchanged = JsonUtility.ToJson(source) == pristineSourceJson;
                Require(report.sourcePolicyUnchanged && JsonUtility.ToJson(linked) == linkedJson,
                    "Policy validation mutated an input domain.");
                good.ThrowIfInvalid();
                Require(!wrongDomain.IsValid, "Linked Player policy must not validate the source inventory.");
                for (int index = 0; index < report.guardProviders.Length; index++)
                {
                    string consumer = index == 0 ? "Unity.Burst" : "Unity.RenderPipelines.Universal.Runtime";
                    string expected = consumer + " references an assembly removed from the captured Player build: " + report.guardProviders[index] + ".";
                    Require(wrongDomain.Diagnostics.Any(d => d.code == "RuntimeReferencesFilteredAssembly" && d.message == expected),
                        "Missing live source-domain guard: " + report.guardProviders[index]);
                }
                report.result = "Passed";
            }
            finally { Write(path, report); }
            return path;
        }

        private static Context ReadContext()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string marker = Path.Combine(project, ".r03-completion-project");
            Require(File.Exists(marker), "Missing explicit resource-complete project authority.");
            var value = JsonUtility.FromJson<Context>(File.ReadAllText(marker));
            Require(value != null && value.schemaVersion == 1 && value.kind == "R03ResourceCompleteFixtureV1" &&
                value.projectPath == project && value.capabilityProfile == R03ResourceCapabilityProfile.Id && !value.expansionAuthorized && !value.R03Accepted && !value.H2Passed,
                "Invalid resource-complete project authority.");
            Require(Application.unityVersion == "2022.3.62f2" && EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneOSX,
                "Pinned Unity/StandaloneOSX required.");
            string prefix = Path.Combine(project, "_temp", "AssemblyShadow") + Path.DirectorySeparatorChar;
            Require(Path.GetFullPath(value.runPath).StartsWith(prefix, StringComparison.Ordinal) &&
                Path.GetFullPath(value.receiptRoot).StartsWith(prefix, StringComparison.Ordinal), "Receipt path escaped fixture.");
            Require(AssemblyShadowBuildCommands.Argument("-shadowBaselineId", "") == value.baselineId,
                "Explicit per-batch baseline argument required.");
            return value;
        }
        internal static IDisposable BeginCapabilityScope()
        {
            var context = ReadContext();
            R03CompletionInventoryContract.ValidatePackages(context.projectPath);
            return R03ResourceCapabilityProfile.Enter();
        }
        private static void Execute(string phase, Action action, string variant = null)
        {
            var context = ReadContext();
            string destination = Path.Combine(context.receiptRoot, phase + ".json");
            Require(!File.Exists(destination), "Phase receipt already exists.");
            var old = variant == null ? new HashSet<string>() : new HashSet<string>(PlayerReceipts(context.projectPath), StringComparer.Ordinal);
            using (BeginCapabilityScope()) action();
            var session = ShadowBuildSession.Load();
            var receipt = new Receipt { phase = phase, projectPath = context.projectPath, baselineId = context.baselineId,
                unityVersion = Application.unityVersion, target = EditorUserBuildSettings.activeBuildTarget.ToString(),
                sourcePinsPath = Path.GetFullPath(AssemblyShadowSettings.Instance.sourcePinFile), resourceRoot = session.resourceBaselinePath,
                baselineManifest = session.baselineManifestPath };
            receipt.sourcePinsSha256 = ShadowHash.File(receipt.sourcePinsPath);
            if (!string.IsNullOrEmpty(receipt.baselineManifest)) receipt.baselineManifestSha256 = ShadowHash.File(receipt.baselineManifest);
            if (variant != null)
            {
                string[] added = PlayerReceipts(context.projectPath).Where(path => !old.Contains(path)).ToArray();
                Require(added.Length == 1, "Exactly one newly produced Player receipt required; never select an older match.");
                var player = JsonUtility.FromJson<M07Build.M07PlayerBuildReceipt>(File.ReadAllText(added[0]));
                Require(player.variant == variant && player.baselineBuildId == context.baselineId,
                    "Produced Player variant/baseline mismatch.");
                receipt.playerReceipt = added[0]; receipt.playerReceiptSha256 = ShadowHash.File(added[0]);
            }
            if (phase == "finalize")
            {
                receipt.fixtureManifest = Path.Combine(context.runPath, "m07-fixtures.json");
                receipt.replayReceipt = Path.Combine(context.runPath, "m07-editor-replay.json");
                receipt.fixtureManifestSha256 = ShadowHash.File(receipt.fixtureManifest);
                receipt.replayReceiptSha256 = ShadowHash.File(receipt.replayReceipt);
            }
            Write(destination, receipt);
        }
        private static string[] PlayerReceipts(string project)
        {
            string root = Path.Combine(project, "_temp", "AssemblyShadow");
            if (!Directory.Exists(root)) return new string[0];
            return Directory.GetDirectories(root, "M07PlayerInputs-*", SearchOption.TopDirectoryOnly)
                .Select(path => Path.Combine(path, "m07-player-build.json")).Where(File.Exists).Select(Path.GetFullPath).ToArray();
        }
        public static void Install() { Execute("install", () => { M07Build.Configure(); PinnedSourceInstaller.Install(); M07SourceAssets.ValidateExisting(false); }); }
        public static void CompilerPreflight() { Execute("compiler", () => R03CompletionCompilerPolicyContract.Verify(M07Build.ValidateCompilerInputsWithSnapshot())); }
        public static void Resources() { Execute("resources", M07Build.BuildBaselineResources); }
        public static void PlayerOn() { Execute("player-on", M07Build.BuildPlayerBaseline, "NativeOn"); }
        public static void PlayerOff() { Execute("player-off", M07Build.BuildFeatureDisabledPlayer, "NativeOff"); }
        public static void StructuralPrepare() { Execute("prepare", M07StructuralResources.Prepare); }
        public static void StructuralCompile() { Execute("compile", M07StructuralResources.Compile); }
        public static void StructuralRestore() { Execute("restore", M07StructuralResources.Restore); }
        public static void FinalizeFixtures() { Execute("finalize", M07StructuralResources.FinalizeFixtures); }

        public static void VerifyProductionEntries()
        {
            using (BeginCapabilityScope()) VerifyProductionEntriesCore();
        }
        private static void VerifyProductionEntriesCore()
        {
            var context = ReadContext();
            string fixturePath = Path.Combine(context.runPath, "m07-fixtures.json");
            var manifest = JsonUtility.FromJson<M07Build.M07FixtureManifest>(File.ReadAllText(fixturePath));
            Require(manifest != null && manifest.baselineBuildId == context.baselineId, "Current fixture manifest required.");
            var baseline = M07Build.ReadBaseline(manifest.baselineManifestPath);
            var baselineReceipt = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            var settings = AssemblyShadowSettings.Instance;
            // Compiler inventory and linked Player inventory are different domains.
            // ApplyPatch deep-clones its input; retain the pristine source policy
            // for the restored-domain compilation, never a BuildFiltered policy.
            var sourcePolicy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
            string sourcePolicyJson = JsonUtility.ToJson(sourcePolicy);
            var rows = new List<GenerationRow>();
            var policy = ShadowFilteredInputPolicy.ApplyPatch(sourcePolicy, baselineReceipt, baseline.shadowCandidates, baseline.bootstrapAssemblies);
            var resourceAbi = JsonUtility.FromJson<ResourceAbiDescriptor>(File.ReadAllText(Path.Combine(Path.GetDirectoryName(manifest.baselineManifestPath), "resource-abi.json")));
            Require(ResourceAbiHasher.Compute(resourceAbi) == baseline.resourceAbiHash, "Frozen resource descriptor differs.");
            using (var installed = ShadowFixtureProof.Load(manifest.baselineInputSnapshot, baselineReceipt, policy))
            {
                foreach (var fixture in manifest.fixtures.OrderBy(f => f.patchId, StringComparer.Ordinal))
                {
                    var targetReceipt = AssemblySnapshot.ReadAndVerify(fixture.compileSnapshot, false);
                    var patch = JsonUtility.FromJson<ShadowPatchManifest>(File.ReadAllText(fixture.patchManifest));
                    using (var target = ShadowFixtureProof.Load(fixture.compileSnapshot, targetReceipt, policy))
                    {
                        // Explicit original roots plus the installation baseline,
                        // never the most recently downloaded patch, drive closure.
                        var explicitRoots = fixture.patchId == "P03" ? M07Build.Candidates : new[] { fixture.patchId == "P02" ? "AssemblyA.Implementation.Extensibility" : "AssemblyA.Implementation.Internal" };
                        ShadowReflectionBindingEvidence.AddCompiledDependencies(policy, target.Assemblies.Values);
                        var calculated = AssemblyReferenceGraph.DetectChangedRoots(baseline.assemblies, target.Assemblies.Values, explicitRoots);
                        var patchClosure = patch.closure.Select(c => c.name).OrderBy(AssemblyIdentityUtil.CanonicalName, StringComparer.Ordinal).ToArray();
                        Require(calculated.SequenceEqual(patch.changedRoots), "Production manifest changed roots differ from installed baseline: " + fixture.patchId);
                        var graph = new AssemblyReferenceGraph(target.Assemblies.Values, policy.dependencies,
                            baseline.dependencyGraph);
                        var closure = graph.ReverseClosure(calculated);
                        Require(closure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(patchClosure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal)) && graph.LoadOrder(closure).SequenceEqual(patch.loadOrder), "Manifest closure/load mismatch.");
                        string folder = Path.Combine(context.receiptRoot, "integration", fixture.patchId);
                        var ordinary = target.Assemblies.Values.Where(a => a.classification == AssemblyClassification.NormalHotUpdate).Select(a => a.filePath);
                        var plan = ShadowGenerationPlan.Create(Path.Combine(folder, "generation"), fixture.compileSnapshot, policy, patch.changedRoots, ordinary);
                        Require(plan.Closure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(patchClosure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal)) && plan.LoadOrder.SequenceEqual(patch.loadOrder), "Compile generation and deployment order differ.");
                        var eligibility = PureInterpreterEligibility.Analyze(installed, target, explicitRoots, policy.dependencies, resourceAbi);
                        Require(!eligibility.expansionAuthorized && eligibility.closure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(patchClosure.Select(AssemblyIdentityUtil.CanonicalName).OrderBy(x => x, StringComparer.Ordinal)), "Qualification is not runtime authorization.");
                        string qualification = Path.Combine(folder, "eligibility.json"); Write(qualification, eligibility);
                        rows.Add(new GenerationRow { patchId = fixture.patchId, compileSnapshot = fixture.compileSnapshot, snapshotHash = targetReceipt.snapshotHash,
                            patchManifest = fixture.patchManifest, patchManifestSha256 = ShadowHash.File(fixture.patchManifest),
                            installedBaselineRoots = calculated, closure = closure, loadOrder = patch.loadOrder,
                            generationRoot = plan.Root, generationHash = plan.PlanHash, eligibilityPath = qualification, eligibilitySha256 = ShadowHash.File(qualification) });
                    }
                }
                // This fresh restored-domain compiler snapshot is the complete
                // target baseline, not an empty incremental download.
                Require(JsonUtility.ToJson(sourcePolicy) == sourcePolicyJson,
                    "Source compiler policy was mutated by linked-Player analysis.");
                string policyDomains = VerifyPolicyDomains(context, sourcePolicy, sourcePolicyJson, policy, baselineReceipt);
                string restored = AssemblySnapshot.CompileWithOptions(Path.Combine(context.receiptRoot, "return-baseline"),
                    EditorUserBuildSettings.activeBuildTarget, settings.architecture,
                    ShadowSourcePins.Read(settings.sourcePinFile, EditorUserBuildSettings.activeBuildTarget, settings.architecture), sourcePolicy, new string[0], true);
                var currentReceipt = AssemblySnapshot.ReadAndVerify(restored, false);
                using (var target = ShadowFixtureProof.Load(restored, currentReceipt, policy))
                {
                    var roots = AssemblyReferenceGraph.DetectChangedRoots(baseline.assemblies, target.Assemblies.Values, null);
                    Require(roots.Length == 0, "Return-to-baseline must be compared with installation bytes, not P03.");
                    var ordinary = target.Assemblies.Values.Where(a => a.classification == AssemblyClassification.NormalHotUpdate).Select(a => a.filePath);
                    var plan = ShadowGenerationPlan.Create(Path.Combine(context.receiptRoot, "return-generation"), restored, policy, roots, ordinary);
                    Require(plan.Closure.Count == 0, "Return-to-baseline compile generation must have an empty Shadow closure.");
                    Write(Path.Combine(context.receiptRoot, "integration.json"), new IntegrationReport { baselineManifest = manifest.baselineManifestPath,
                        baselineManifestSha256 = ShadowHash.File(manifest.baselineManifestPath), patches = rows.ToArray(),
                        policyDomainsPath = policyDomains, policyDomainsSha256 = ShadowHash.File(policyDomains),
                        returnToBaselineSnapshot = restored, returnToBaselineSnapshotHash = currentReceipt.snapshotHash,
                        returnChangedRoots = roots, returnClosure = plan.Closure.ToArray(), returnGenerationRoot = plan.Root, returnGenerationHash = plan.PlanHash });
                }
            }
        }
        private static void Write(string path, object value)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            M04AssemblyIdentityProof.WriteNewJson(path, value);
        }
        private static void Require(bool condition, string message)
        { if (!condition) throw new ShadowBuildException("R03Completion", message); }
    }
}
