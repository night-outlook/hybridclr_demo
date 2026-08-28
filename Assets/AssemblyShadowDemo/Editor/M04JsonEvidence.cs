using System;
using System.Linq;
using System.Reflection;
using HybridCLR.Editor.AssemblyShadow;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Checks raw members before JsonUtility can silently default missing zero/false values.</summary>
    public static class M04JsonEvidence
    {
        public static T Read<T>(string json)
        {
            ValidateSchema<T>(json);
            return JsonUtility.FromJson<T>(json);
        }

        public static void ValidateSchema<T>(string json)
        {
            try
            {
                Check(JToken.Parse(json, new JsonLoadSettings { DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error }),
                    typeof(T), typeof(T).Name);
            }
            catch (JsonException error)
            {
                throw new ShadowBuildException("M04EvidenceJsonSchema", "Malformed evidence JSON: " + error.Message);
            }
        }

        private static void Check(JToken value, Type type, string path)
        {
            Require(value != null && value.Type != JTokenType.Null, "Null evidence member: " + path);
            if (type == typeof(string)) { Require(value.Type == JTokenType.String, "Expected string: " + path); return; }
            if (type == typeof(bool)) { Require(value.Type == JTokenType.Boolean, "Expected boolean: " + path); return; }
            if (type == typeof(int))
            {
                int parsed;
                Require(value.Type == JTokenType.Integer && int.TryParse(value.ToString(), out parsed), "Expected integer: " + path);
                return;
            }
            if (type.IsArray)
            {
                var array = value as JArray;
                Require(array != null, "Expected array: " + path);
                for (int index = 0; index < array.Count; ++index) Check(array[index], type.GetElementType(), path + "[" + index + "]");
                return;
            }
            var members = value as JObject;
            Require(members != null, "Expected object: " + path);
            var fields = type.GetFields(BindingFlags.Public | BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
            Require(fields.Length > 0 && members.Count == fields.Length, "Evidence member count differs: " + path);
            foreach (FieldInfo field in fields)
            {
                JToken child;
                Require(members.TryGetValue(field.Name, StringComparison.Ordinal, out child), "Missing evidence member: " + path + "." + field.Name);
                Check(child, field.FieldType, path + "." + field.Name);
            }
        }

        private static void Require(bool condition, string message)
        {
            ShadowHash.Require(condition, "M04EvidenceJsonSchema", message);
        }
    }
}
