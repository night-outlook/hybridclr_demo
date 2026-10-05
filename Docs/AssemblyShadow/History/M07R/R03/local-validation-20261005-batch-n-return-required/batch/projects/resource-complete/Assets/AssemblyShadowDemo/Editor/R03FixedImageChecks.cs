using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Serialization.Json;
using dnlib.DotNet;
using HybridCLR.AssemblyShadow.CodeGen;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    // Pure guard-consumer checks shared with the host suite. These do not claim
    // current Player-provider semantics; the unmodified snapshot policy does that.
    public static class R03FixedImageChecks
    {
        public const string Profile = "R03FrozenFixedImageV1";
        public const string ConfigurationSha = "26837a5f710abae42a69a85ea2edf66939eff9afa6f6e8ce5b8e2cafc44f564a";
        public const string ImagePath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        public const string ImageSha = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        public const string Provider = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        public const string Development = "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369";
        public const string Release = "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022";
        public static readonly string[] SiteIds = { "h1-count-ordinary-witness-image", "m00-normal-hot-update-image" };
        [Serializable] public sealed class Case
        {
            public string id, operation, mode, configurationPath, configurationSha256, imagePath, imageSha256;
            public string expectedCode, observedCode, selectedSemanticHash, result;
        }
        [Serializable] public sealed class Observation
        {
            public string profile = Profile, imageSha256, providerIdentity, imageSemanticHash, mvid;
            public string classification = "FrozenHistoricalInputMaterialization";
            public int sizeBytes;
            public string[] siteIds;
            public bool freshCscExecutionClaimed, historicalPlayerExecutionReused, runtimeAcceptance;
            public List<Case> cases = new List<Case>();
        }
        public static Observation Run(string project, string controls)
        {
            byte[] raw = File.ReadAllBytes(Path.Combine(project, ReflectionBindingConfiguration.ProjectRelativePath));
            Require(ShadowHash.Bytes(raw) == ConfigurationSha, "The original six-site configuration must remain byte-identical.");
            var original = ReflectionBindingConfiguration.Parse(raw);
            var fixedSites = original.sites.Where(s => ReflectionBindingConfiguration.KindOf(s) == "FixedAssemblyBytes").ToArray();
            Require(original.sites.Length == 6 && fixedSites.Select(s => s.id).OrderBy(s => s, StringComparer.Ordinal).SequenceEqual(SiteIds), "Complete fixed-site closure changed.");
            foreach (var site in fixedSites)
                Require(site.imagePath == ImagePath && site.imageSha256 == ImageSha && site.providerAssemblyIdentity == Provider &&
                    original.ProviderSemanticHash(site, "Development") == Development && original.ProviderSemanticHash(site, "Release") == Release,
                    "Image/provider/mode contract changed.");
            byte[] image = File.ReadAllBytes(Path.Combine(project, ImagePath));
            original.ValidateImageEvidence(new Dictionary<string, byte[]> { { ImagePath, image } });
            var result = new Observation { imageSha256 = ShadowHash.Bytes(image), sizeBytes = image.Length, siteIds = SiteIds };
            using (var module = ModuleDefMD.Load(image, new ModuleCreationOptions { TryToLoadPdbFromDisk = false }))
            {
                result.providerIdentity = module.Assembly.FullName; result.mvid = module.Mvid.ToString();
                result.imageSemanticHash = AssemblySemanticHasher.Compute(module).semanticHash;
            }
            Require(result.sizeBytes == 4608, "Frozen input size changed.");
            Require(!Directory.Exists(controls), "Unused control directory required."); Directory.CreateDirectory(controls);
            Action<string, string, string, Action<ReflectionBindingConfiguration>, byte[], string> run = (id, operation, expected, mutate, input, mode) =>
            {
                var config = ReflectionBindingConfiguration.Parse(raw); if (mutate != null) mutate(config);
                string configPath = Path.Combine(controls, id + ".json");
                using (var stream = new FileStream(configPath, FileMode.CreateNew)) new DataContractJsonSerializer(typeof(ReflectionBindingConfiguration)).WriteObject(stream, config);
                string inputPath = null;
                if (input != null) { inputPath = Path.Combine(controls, id + ".dll.bytes"); using (var stream = new FileStream(inputPath, FileMode.CreateNew)) stream.Write(input, 0, input.Length); }
                var row = new Case { id = id, operation = operation, mode = mode, expectedCode = expected, configurationPath = configPath,
                    configurationSha256 = ShadowHash.File(configPath), imagePath = inputPath, imageSha256 = input == null ? null : ShadowHash.File(inputPath) };
                try
                {
                    // Parse the actual preserved control bytes, not the pre-serialization object.
                    var parsed = ReflectionBindingConfiguration.Parse(File.ReadAllBytes(configPath));
                    if (operation == "ValidateImageEvidence") parsed.ValidateImageEvidence(input == null ? new Dictionary<string, byte[]>() :
                        new Dictionary<string, byte[]> { { ImagePath, File.ReadAllBytes(inputPath) } });
                    else if (operation == "ProviderSemanticHash") row.selectedSemanticHash = parsed.ProviderSemanticHash(parsed.sites.Single(s => s.id == SiteIds[0]), mode);
                    else if (operation != "Parse") throw new InvalidOperationException("Unknown control operation.");
                    row.observedCode = "Success";
                }
                catch (ReflectionBindingException error) { row.observedCode = error.Code; }
                row.result = row.observedCode == expected ? "Passed" : "Failed"; result.cases.Add(row);
            };
            run("F01-exact-image", "ValidateImageEvidence", "Success", null, image, null);
            run("F02-missing-image", "ValidateImageEvidence", "FixedImageEvidenceMissing", null, null, null);
            byte[] changed = (byte[])image.Clone(); changed[changed.Length - 1] ^= 1;
            run("F03-mutated-image", "ValidateImageEvidence", "FixedImageHashMismatch", null, changed, null);
            run("F04-provider-identity", "ValidateImageEvidence", "FixedImageIdentityMismatch", c => {
                foreach (var s in c.sites.Where(s => ReflectionBindingConfiguration.KindOf(s) == "FixedAssemblyBytes"))
                    s.providerAssemblyIdentity = "Other, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
            }, image, null);
            run("F05-development", "ProviderSemanticHash", "Success", null, null, "Development");
            run("F06-release", "ProviderSemanticHash", "Success", null, null, "Release");
            run("F07-missing-mode", "ProviderSemanticHash", "ProviderSemanticCompilerModeMissing", null, null, null);
            run("F08-unknown-mode", "ProviderSemanticHash", "ProviderSemanticCompilerModeMissing", null, null, "Unknown");
            run("F09-omitted-variant", "Parse", "InvalidProviderSemanticVariants", c => {
                c.sites.Single(s => s.id == SiteIds[0]).providerSemanticVariants = c.sites.Single(s => s.id == SiteIds[0]).providerSemanticVariants.Take(1).ToArray();
            }, null, null);
            run("F10-image-path", "Parse", "InvalidFixedImage", c => c.sites.Single(s => s.id == SiteIds[0]).imagePath = "../outside.dll", null, null);
            Require(result.cases.Count == 10 && result.cases.All(c => c.result == "Passed") &&
                result.cases.Single(c => c.id == "F05-development").selectedSemanticHash == Development &&
                result.cases.Single(c => c.id == "F06-release").selectedSemanticHash == Release, "Fixed-image guard controls failed.");
            return result;
        }
        // Only the actual pinned Mono/Editor runtime may establish the original
        // semantic encoder's declared mode relationship. The .NET host reports
        // its own observation separately, never adding another accepted variant.
        public static void RequirePinnedSemantics(Observation value)
        {
            Require(value.imageSemanticHash == Development || value.imageSemanticHash == Release,
                "Frozen input has no declared semantic variant: " + value.imageSemanticHash);
        }
        private static void Require(bool value, string message) { if (!value) throw new InvalidOperationException(message); }
    }
}
