// Host-only adapter for testing the EXACT Unity Editor source helper using
// real dnlib DLL bytes. Unity, IL2CPP, and native Player are NOT run here.
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using AssemblyShadow.R03.Editor;

namespace HybridCLR.Editor.AssemblyShadow
{
    public static class ShadowHash
    {
        public static string File(string path)
        {
            using (var sha = SHA256.Create())
                using (var stream = System.IO.File.OpenRead(path))
                    return Convert.ToHexString(sha.ComputeHash(stream)).ToLowerInvariant();
        }
    }
}

namespace AssemblyShadow.R03.Editor
{
    public sealed class BuildConfig
    {
        public bool featureEnabled = true;
        public int diagnosticsLevel = 2;
        public string cppConfiguration = "Release";
        public string initializerBridgeContract = R03InitializerBridge.Contract;
        public string initializerBridgeControlPath;
        public string initializerBridgeControlSha256;
        public string initializerBridgeControlMvid;
        public string initializerBridgeFailurePath;
        public string initializerBridgeFailureSha256;
        public string initializerBridgeFailureMvid;
    }
}

internal static class Program
{
    static int Main(string[] argv)
    {
        if (argv.Length != 9)
        {
            Console.Error.WriteLine("Expected control/failure paths, SHA256/MVIDs and installed native root (9 args).");
            return 2;
        }
        var conf = new BuildConfig
        {
            initializerBridgeControlPath = Path.GetFullPath(argv[0]),
            initializerBridgeControlSha256 = argv[1],
            initializerBridgeControlMvid = argv[2],
            initializerBridgeFailurePath = Path.GetFullPath(argv[3]),
            initializerBridgeFailureSha256 = argv[4],
            initializerBridgeFailureMvid = argv[5],
        };
        // Exercise strict rejection without changing positive source.
        if (argv[6] == "legacy") conf.initializerBridgeContract = "Unsupported";
        else if (argv[6] != "valid") return 2;
        string root = Path.GetFullPath(argv[7]);
        string outPath = Path.GetFullPath(argv[8]);
        try
        {
            var result = R03InitializerBridge.Generate(conf, root);
            string json = JsonSerializer.Serialize(new {
                result = result.result, signature = result.signature,
                importModule = result.importModule,
                controlSha256 = result.controlSha256,
                failureSha256 = result.failureSha256,
                generatedSourceBeforeSha256 = result.generatedSourceBeforeSha256,
                generatedSourceAfterSha256 = result.generatedSourceAfterSha256,
                actualNativePlayerLinked = result.actualNativePlayerLinked,
                runtimeAcceptance = result.runtimeAcceptance
            }, new JsonSerializerOptions { WriteIndented = true }) + "\n";
            if (System.IO.File.Exists(outPath))
                throw new InvalidOperationException("Existing host receipt");
            System.IO.File.WriteAllText(outPath, json);
            Console.WriteLine(json);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("Host source test rejected: " + error.GetType().Name
                + " | " + error.Message);
            return 7;
        }
    }
}
