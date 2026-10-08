using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using AssemblyShadowDemo.Editor;
class Program
{
    static int Main(string[] args)
    {
        string Read(string key) => args[Array.IndexOf(args,key)+1];
        string output=Path.GetFullPath(Read("--output"));
        if (Directory.Exists(output)) throw new InvalidOperationException("Unused output required");
        Directory.CreateDirectory(output);
        object result;
        try
        {
            var observation=R03FixedImageChecks.Run(Path.GetFullPath(Read("--project")),Path.Combine(output,"controls"));
            File.WriteAllText(Path.Combine(output,"semantic-sections.json"),JsonSerializer.Serialize(SemanticDiagnostics.Capture(File.ReadAllBytes(Path.Combine(Read("--project"),R03FixedImageChecks.ImagePath)))));
            result=new {kind="R03FixedImageHostContracts",result="Passed",observation,
                semanticRuntime="DotNet8HostObservationOnly", pinnedMonoSemanticVerification=false,
                unityEditorRun=false,currentProviderCompilation=false,runtimeAcceptance=false,expansionAuthorized=false};
        }
        catch (Exception e)
        {
            result=new {kind="R03FixedImageHostContracts",result="Failed",error=e.ToString(),unityEditorRun=false,runtimeAcceptance=false};
            File.WriteAllText(Path.Combine(output,"results.json"),JsonSerializer.Serialize(result,new JsonSerializerOptions {IncludeFields=true,WriteIndented=true}));
            return 1;
        }
        File.WriteAllText(Path.Combine(output,"results.json"),JsonSerializer.Serialize(result,new JsonSerializerOptions {IncludeFields=true,WriteIndented=true}));
        return 0;
    }
}
