using System;
using System.IO;
using UnityEngine;

namespace AssemblyShadowDemo
{
    [Serializable] public sealed class NativeAssemblyInfo
    {
        public string assembly;
        public string image;
        public string name;
        public bool isInterpreter;
        public bool matchesShadow;
    }
    [Serializable] public sealed class NativeObjectInfo
    {
        public string @object;
        public string @class;
        public string type;
        public int instanceSize;
        public NativeAssemblyInfo physicalAssembly;
    }
    [Serializable] public sealed class NativeEvent
    {
        public int sequence;
        public string phase;
        public string site;
        public string assembly;
        public string image;
        public string @class;
        public string type;
        public bool active;
        public bool isInterpreter;
    }
    [Serializable] public sealed class NativeDiagnostics
    {
        public bool enabled;
        public bool active;
        public NativeAssemblyInfo baseline;
        public NativeAssemblyInfo shadow;
        public bool moduleInitializerRun;
        public NativeEvent[] events;
    }
    [Serializable] public sealed class ReflectionProbe
    {
        public string fullName;
        public string moduleMvid;
        public bool moduleMvidSupported;
        public string moduleMvidNote;
        public bool isDynamic;
        public bool typeAssemblyIdentity;
        public int sameNameAssemblyCount;
        public string result;
        public NativeAssemblyInfo assembly;
        public NativeObjectInfo instance;
        public bool passed;
    }
    [Serializable] public sealed class ComponentProbe
    {
        public string phase;
        public string componentAssembly;
        public bool missingScript;
        public bool getComponentByName;
        public bool getComponentByNameFound;
        public NativeObjectInfo byNameNativeObject;
        public bool getComponentByType;
        public int serializedValue;
        public int baseSerializedValue;
        public string result;
        public NativeObjectInfo nativeObject;
        public bool dataReference;
        public bool passed;
        public string error;
    }
    [Serializable] public sealed class DataProbe
    {
        public int serializedValue;
        public string result;
        public NativeObjectInfo nativeObject;
        public bool passed;
    }
    [Serializable] public sealed class SceneProbe
    {
        public ComponentProbe firstLoad;
        public ComponentProbe reload;
        public bool derivedConsumerAot;
        public string derivedConsumerResult;
        public bool passed;
    }
    [Serializable] public sealed class BaselineUse
    {
        public string kind;
        public string type;
        public NativeAssemblyInfo assemblyBefore;
        public NativeObjectInfo objectBefore;
        public NativeObjectInfo objectAfterActivate;
        public string resultAfterActivate;
    }
    [Serializable] public sealed class ResolutionProbe
    {
        public string assemblyLoad;
        public string assemblyGetType;
        public string monoScriptGetClass = "UnityEditor-only API; native resource-resolution evidence is recorded separately";
        public string objectNew;
        public bool resourceNativeTraceObserved;
    }
    [Serializable] public sealed class ShadowDemoResult
    {
        public string milestone = "M01";
        public string mode;
        public string result = "Failed";
        public string gate = "UNDETERMINED";
        public string gateNotes;
        public bool il2cpp;
        public string unityVersion;
        public string platform;
        public string baselineBuildId;
        public string baselineManifestSha256;
        public ShadowPatchFileProvider.BundleFile[] baselineBundleSha256;
        public string patchDllSha256;
        public string baselineMvid;
        public string patchMvid;
        public bool originalBundlesUnchanged;
        public bool nativeFeatureEnabled;
        public ReflectionProbe reflection;
        public ComponentProbe prefab;
        public DataProbe scriptableObject;
        public SceneProbe scene = new SceneProbe();
        public ResolutionProbe assemblyResolution = new ResolutionProbe();
        public BaselineUse[] baselineUsesBeforeActivate = Array.Empty<BaselineUse>();
        public string nativeDiagnosticsPath;
        public string nativeDiagnosticsSha256;
        public string persistentResultPath;
        public string error;
    }

    public static class ShadowDemoResultWriter
    {
        public static void Write(ShadowDemoResult result, string diagnostics)
        {
            string persistent = Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m01-result.json");
            string requested = ShadowPatchFileProvider.Argument("-shadowResultPath", persistent);
            result.persistentResultPath = persistent;
            string nativePath = Path.Combine(Path.GetDirectoryName(Path.GetFullPath(requested)),
                Path.GetFileNameWithoutExtension(requested) + "-native-diagnostics.json");
            Directory.CreateDirectory(Path.GetDirectoryName(nativePath));
            File.WriteAllText(nativePath, diagnostics);
            result.nativeDiagnosticsPath = nativePath;
            result.nativeDiagnosticsSha256 = ShadowPatchFileProvider.Hash(File.ReadAllBytes(nativePath));
            string json = JsonUtility.ToJson(result, true);
            Directory.CreateDirectory(Path.GetDirectoryName(persistent));
            File.WriteAllText(persistent, json);
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(requested)));
            if (Path.GetFullPath(requested) != Path.GetFullPath(persistent)) File.WriteAllText(requested, json);
            Debug.Log("[AssemblyShadow M01] " + JsonUtility.ToJson(result));
        }
    }
}
