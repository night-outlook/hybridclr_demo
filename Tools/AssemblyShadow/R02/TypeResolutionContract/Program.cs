using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Nodes;
using HybridCLR;
// Attribute only: the parser itself is linked from the exact package source.
namespace UnityEngine.Scripting { public sealed class PreserveAttribute : Attribute { } }
public static class Program
{
    static int checks;
    static void Check(bool condition, string message) { ++checks; if (!condition) throw new Exception(message); }
    static void Reject(string json)
    {
        Check(!AssemblyShadowTypeResolutionInfo.TryParse(json, out var info) && info == null, "Accepted invalid JSON: " + json);
    }
    static JsonObject Object(string json) { return JsonNode.Parse(json).AsObject(); }
    static string Changed(string json, Action<JsonObject> edit)
    { var node = Object(json); edit(node); return node.ToJsonString(); }
    public static int Main(string[] args)
    {
        try
        {
            if (args.Length != 1) throw new Exception("Exact fixture directory required");
            var paths = Directory.GetFiles(args[0], "*.json").OrderBy(x => x).ToArray();
            Check(paths.Length == 13, "Expected twelve native extensions and one legacy fixture");
            foreach (var path in paths)
            {
                var json = File.ReadAllText(path);
                var info = AssemblyShadowTypeResolutionInfo.Parse(json);
                Check(info.definitionCacheHits == ulong.MaxValue, "Root UInt64 narrowed");
                using var document = JsonDocument.Parse(json);
                if (!document.RootElement.TryGetProperty("r02", out var raw))
                { Check(info.r02 == null, "Legacy absence is not zero diagnostics"); continue; }
                Check(info.r02 != null, "Missing native diagnostics");
                Check(raw.EnumerateObject().Count() == 33, "Producer inventory changed");
                foreach (var field in raw.EnumerateObject())
                {
                    var member = typeof(AssemblyShadowTypeResolutionInfo.R02Diagnostics).GetField(field.Name);
                    Check(member != null, "Native field not exposed: " + field.Name);
                    object expected = member.FieldType == typeof(ulong) ? (object)field.Value.GetUInt64() :
                        member.FieldType == typeof(int) ? (object)field.Value.GetInt32() :
                        member.FieldType == typeof(bool) ? (object)field.Value.GetBoolean() : field.Value.GetString();
                    Check(expected.Equals(member.GetValue(info.r02)), "Field mismatch: " + field.Name);
                }
            }
            var complete = File.ReadAllText(Path.Combine(args[0], "2-normal.json"));
            var legacy = File.ReadAllText(Path.Combine(args[0], "legacy.json"));
            var extension = Object(complete)["r02"].AsObject();
            foreach (var key in Object(legacy).Select(x => x.Key).ToArray())
                Reject(Changed(complete, x => x.Remove(key)));
            foreach (var key in extension.Select(x => x.Key).ToArray())
            {
                Reject(Changed(complete, x => x["r02"].AsObject().Remove(key)));
                Reject(complete.Replace("\"" + key + "\":", "\"" + key + "\":null,\"" + key + "\":"));
                Reject(Changed(complete, x => x["r02"][key] = null));
            }
            foreach (var field in typeof(AssemblyShadowTypeResolutionInfo.R02Diagnostics).GetFields().Where(x => x.FieldType == typeof(ulong) && x.Name != "counterThreadCapacity"))
            {
                var json = Changed(complete, x => x["r02"][field.Name] = JsonValue.Create(ulong.MaxValue));
                Check((ulong)field.GetValue(AssemblyShadowTypeResolutionInfo.Parse(json).r02) == ulong.MaxValue, "UInt64 precision");
                foreach (var bad in new[] { "-1", "1.5", "1e2", "18446744073709551616", "01", "true", "[]", "{}", "\"0\"" })
                    Reject(json.Replace("\"" + field.Name + "\":18446744073709551615", "\"" + field.Name + "\":" + bad));
            }
            Reject(Changed(complete, x => x["r02"]["schemaVersion"] = 2));
            Reject(Changed(complete, x => x["schemaVersion"] = 2));
            Reject(Changed(complete, x => x["r02"]["diagnosticsLevel"] = 3));
            Reject(Changed(complete, x => x["r02"]["counterThreadCapacity"] = 129));
            Reject(Changed(complete, x => x["r02"]["counterCoverage"] = "Unknown"));
            Reject(Changed(complete, x => x["r02"]["classesCoverage"] = "Unknown"));
            Reject(Changed(complete, x => x["r02"]["memoryAccountingScope"] = "RSS"));
            Reject(Changed(complete, x => x["unknown"] = 0));
            Reject(Changed(complete, x => x["r02"]["unknown"] = 0));
            Reject(Changed(complete, x => x["r02"] = null));
            Reject(complete + "{}"); Reject(complete.Replace("\"r02\":", "\"r02\":{},\"r02\":"));
            Reject(Changed(File.ReadAllText(Path.Combine(args[0], "0-normal.json")), x => x["r02"]["memoryAccountingAvailable"] = true));
            Reject(Changed(complete, x => x["r02"]["classesCoverage"] = "Disabled"));
            Reject(Changed(complete, x => x["r02"]["counterSaturated"] = 0));
            Reject(Changed(complete, x => x["r02"]["memoryAccountingAvailable"] = "true"));
            // Object field order is not an implicit schema discriminator.
            var reversed = new JsonObject();
            foreach (var item in Object(complete).Reverse()) reversed.Add(item.Key, item.Value.DeepClone());
            Check(AssemblyShadowTypeResolutionInfo.Parse(reversed.ToJsonString()).r02.schemaVersion == 1, "Field order");
            Console.WriteLine(JsonSerializer.Serialize(new { kind = "R02ProducerParserContract", result = "Passed", checks, nativeFixtures = 12, legacyFixtures = 1, unityPlayerRun = false }));
            return 0;
        }
        catch (Exception error) { Console.Error.WriteLine(error); return 1; }
    }
}
