using System;
using System.IO;
using System.Reflection;
using HybridCLR;
using UnityEngine;

namespace AssemblyShadowBaseline
{
    public sealed class BaselineBootstrap : MonoBehaviour
    {
        [Serializable]
        private sealed class Result
        {
            public string milestone = "M00";
            public string result = "Failed";
            public string unityVersion;
            public string platform;
            public bool il2cpp;
            public string hotUpdateAssembly;
            public string hotUpdateResult;
            public bool assemblyLoadIdentity;
            public string prefabResult;
            public int scriptableObjectValue;
            public bool sceneComponent;
            public bool missingScript;
            public int interpreterStackSize;
            public string error;
        }

        private void Start()
        {
            var result = new Result
            {
                unityVersion = Application.unityVersion,
                platform = Application.platform.ToString(),
#if ENABLE_IL2CPP && !UNITY_EDITOR
                il2cpp = true,
#endif
            };
            try
            {
                Require(result.il2cpp, "The M00 acceptance test must run in an IL2CPP Player.");
                var dll = File.ReadAllBytes(Path.Combine(Application.streamingAssetsPath,
                    "AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"));
                Assembly hotAssembly = Assembly.Load(dll);
                result.hotUpdateAssembly = hotAssembly.GetName().Name;
                var entry = hotAssembly.GetType("AssemblyShadowBaseline.HotUpdate.Entry", true);
                result.hotUpdateResult = (string)entry.GetMethod("Run", BindingFlags.Public | BindingFlags.Static)
                    .Invoke(null, null);
                Require(result.hotUpdateResult == "M00-HOTUPDATE-OK", "Ordinary hot-update method did not run.");
                Require(result.hotUpdateAssembly == "AssemblyShadowBaseline.HotUpdate", "Unexpected hot assembly.");

                result.assemblyLoadIdentity = Assembly.Load("AssemblyShadowBaseline.Aot") == typeof(BaselineProbe).Assembly;
                Require(result.assemblyLoadIdentity, "AOT Assembly.Load identity changed.");
                var prefab = Resources.Load<GameObject>("AssemblyShadowBaseline/BaselinePrefab");
                Require(prefab != null, "Baseline prefab is missing.");
                var instance = Instantiate(prefab);
                foreach (var component in instance.GetComponents<Component>())
                    result.missingScript |= component == null;
                var probe = instance.GetComponent<BaselineProbe>();
                Require(probe != null, "Baseline GetComponent failed.");
                result.prefabResult = (string)probe.GetType().GetMethod("Read").Invoke(probe, null);
                Require(result.prefabResult == "M00-AOT-OK|1234", "AOT prefab/serialization/reflection changed.");
                Require(!result.missingScript, "Baseline prefab has a Missing Script.");
                var data = Resources.Load<BaselineData>("AssemblyShadowBaseline/BaselineData");
                Require(data != null, "Baseline ScriptableObject is missing.");
                result.scriptableObjectValue = data.number;
                Require(data.number == 5678, "ScriptableObject serialization changed.");
                result.sceneComponent = gameObject.GetComponent<BaselineProbe>() != null;
                Require(result.sceneComponent, "Baseline scene component is missing.");
                result.interpreterStackSize = RuntimeApi.GetInterpreterThreadObjectStackSize();
                Require(result.interpreterStackSize > 0, "HybridCLR native runtime is not active.");
                Destroy(instance);
                result.result = "Passed";
            }
            catch (Exception exception)
            {
                result.error = exception.ToString();
                Debug.LogException(exception);
            }

            string path = Argument("-shadowResultPath", Path.Combine(Application.persistentDataPath,
                "AssemblyShadowTests/m00-result.json"));
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
            File.WriteAllText(path, JsonUtility.ToJson(result, true));
            Debug.Log("[AssemblyShadow M00] " + JsonUtility.ToJson(result));
            Application.Quit(result.result == "Passed" ? 0 : 1);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        private static string Argument(string name, string fallback)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == name) return args[i + 1];
            return fallback;
        }
    }
}
