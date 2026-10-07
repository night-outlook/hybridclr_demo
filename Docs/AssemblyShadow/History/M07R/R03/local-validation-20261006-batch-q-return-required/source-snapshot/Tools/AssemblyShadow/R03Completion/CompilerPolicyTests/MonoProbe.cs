using System;
using System.IO;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
class MonoProbe
{
    static int Main(string[] args)
    {
        if (args.Length != 3) throw new ArgumentException("project snapshot unused-controls");
        var result = R03CompilerPolicyChecks.Run(args[0], args[1], args[2], "Development");
        // Use the real enclosing report type, without invoking any Unity API.
        // The live producer uses this same serializer so optional nulls cannot
        // silently change between its nested observation and the control file.
        Type reportType = typeof(R03CompletionCompilerPolicyContract).GetNestedType("Report", BindingFlags.NonPublic);
        if (reportType == null) throw new InvalidOperationException("Actual report type missing");
        object report = Activator.CreateInstance(reportType, true);
        reportType.GetField("observation").SetValue(report, result);
        string json = JsonConvert.SerializeObject(report, Formatting.Indented);
        if (!JToken.DeepEquals(JObject.Parse(json)["observation"], JObject.Parse(File.ReadAllText(Path.Combine(args[2], "observation.json")))))
            throw new InvalidOperationException("Enclosing report changed control observation");
        // This is a serialization control, not an actual Unity report/execution.
        string path = Path.Combine(Path.GetDirectoryName(args[2]), "serialization-control.json");
        using (var file = new FileStream(path, FileMode.CreateNew))
        using (var writer = new StreamWriter(file, new System.Text.UTF8Encoding(false)))
            writer.Write("{\"kind\":\"ActualReportSerializationControl\",\"result\":\"Passed\",\"unityEditorRun\":false,\"runtimeAcceptance\":false}");
        Console.WriteLine("COMPILER_POLICY_GUARDS_PASSED raw=" + result.sites.Length + " controls=" + result.controls.Count);
        return 0;
    }
}
