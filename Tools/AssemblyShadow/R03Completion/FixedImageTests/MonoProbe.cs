using System;
using System.IO;
using System.Runtime.Serialization.Json;
using AssemblyShadowDemo.Editor;
class MonoProbe
{
    static int Main(string[] args)
    {
        if (args.Length!=2 || Directory.Exists(args[1])) throw new InvalidOperationException("New probe output required.");
        Directory.CreateDirectory(args[1]);
        var value=R03FixedImageChecks.Run(args[0],Path.Combine(args[1],"controls"));
        // The record is written even when strict mode comparison fails.
        using (var stream=new FileStream(Path.Combine(args[1],"observation.json"),FileMode.CreateNew))
            new DataContractJsonSerializer(typeof(R03FixedImageChecks.Observation)).WriteObject(stream,value);
        using(var stream=new FileStream(Path.Combine(args[1],"semantic-sections.json"),FileMode.CreateNew))
            new DataContractJsonSerializer(typeof(System.Collections.Generic.Dictionary<string,string>)).WriteObject(stream,SemanticDiagnostics.Capture(File.ReadAllBytes(Path.Combine(args[0],R03FixedImageChecks.ImagePath))));
        R03FixedImageChecks.RequirePinnedSemantics(value);
        Console.WriteLine("PINNED_MONO_FIXED_IMAGE_PASSED " + value.imageSemanticHash);
        return 0;
    }
}
