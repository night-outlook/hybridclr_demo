using System;
using System.Linq;
using AssemblyA.Contracts;
using AssemblyA.Implementation.Extensibility;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    /// <summary>
    /// Runs generic Unity APIs inside the admitted closure. The fixed AOT
    /// Bootstrap invokes this method only through reflection after Commit.
    /// </summary>
    public static class M07UnityPathProbe
    {
        [Serializable]
        public sealed class Result
        {
            public string marker;
            public string componentType;
            public string componentAssembly;
            public string baseType;
            public string baseAssembly;
            public string interfaceType;
            public string interfaceAssembly;
            public string getComponentGeneric;
            public string getComponentType;
            public string tryGetComponent;
            public string getComponents;
            public string getComponentInChildren;
            public string getComponentInParent;
            public string interfaceComponent;
            public string baseComponent;
            public string addComponentGeneric;
            public string addComponentType;
            public string createInstanceGeneric;
            public string createInstanceType;
            public string createInstanceString;
            public string instantiateExisting;
            public string serializedState;
            public string messageMarker;
            public int p04RuntimeValue;
            public int p05SerializedValue;
        }

        public static string Run(GameObject root, ScriptableObject existingAsset)
        {
            if (root == null) throw new ArgumentNullException("root");
            VersionedPrefabComponent component = root.GetComponentInChildren<VersionedPrefabComponent>(true);
            if (component == null) throw new InvalidOperationException("M07 generic probe root has no VersionedPrefabComponent.");
            Type activeType = typeof(VersionedPrefabComponent);
            Type resolvedType = Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true);
            if (!object.ReferenceEquals(activeType, resolvedType)) throw new InvalidOperationException("M07 Type.GetType and generic token disagree.");

            var genericHost = new GameObject("M07 AddComponent Generic");
            var typeHost = new GameObject("M07 AddComponent Type");
            VersionedPrefabComponent addedGeneric = null;
            Component addedType = null;
            VersionedScriptableObject createdGeneric = null;
            ScriptableObject createdType = null;
            ScriptableObject createdString = null;
            ScriptableObject cloned = null;
            try
            {
                addedGeneric = genericHost.AddComponent<VersionedPrefabComponent>();
                addedType = typeHost.AddComponent(resolvedType);
                if (addedGeneric == null || addedType == null || !object.ReferenceEquals(addedGeneric.GetType(), activeType) ||
                    !object.ReferenceEquals(addedType.GetType(), activeType)) throw new InvalidOperationException("M07 AddComponent allocated a non-active type.");

                VersionedPrefabComponent genericGet = root.GetComponentInChildren<VersionedPrefabComponent>(true);
                Component typedGet = root.GetComponentInChildren(resolvedType, true);
                VersionedPrefabComponent tryGet;
                bool got = component.gameObject.TryGetComponent<VersionedPrefabComponent>(out tryGet);
                VersionedPrefabComponent[] all = root.GetComponentsInChildren<VersionedPrefabComponent>(true);
                VersionedPrefabComponent fromParent = component.GetComponentInParent<VersionedPrefabComponent>(true);
                IVersionTextProvider interfaceGet = component.GetComponent<IVersionTextProvider>();
                VersionedComponentBase baseGet = component.GetComponent<VersionedComponentBase>();

                createdGeneric = ScriptableObject.CreateInstance<VersionedScriptableObject>();
                createdType = ScriptableObject.CreateInstance(typeof(VersionedScriptableObject));
                createdString = ScriptableObject.CreateInstance("AssemblyA.Implementation.Internal.VersionedScriptableObject");
                cloned = existingAsset == null ? null : UnityEngine.Object.Instantiate(existingAsset);
                if (createdGeneric == null || createdType == null || createdString == null ||
                    !object.ReferenceEquals(createdGeneric.GetType(), typeof(VersionedScriptableObject)) ||
                    !object.ReferenceEquals(createdType.GetType(), typeof(VersionedScriptableObject)) ||
                    !object.ReferenceEquals(createdString.GetType(), typeof(VersionedScriptableObject)) ||
                    (existingAsset != null && (cloned == null || !object.ReferenceEquals(cloned.GetType(), existingAsset.GetType()))))
                    throw new InvalidOperationException("M07 ScriptableObject creation returned a non-active type.");

                var result = new Result {
                    marker = VersionedPrefabComponent.M07PatchMarker(),
                    componentType = activeType.FullName,
                    componentAssembly = activeType.Assembly.GetName().Name,
                    baseType = activeType.BaseType.FullName,
                    baseAssembly = activeType.BaseType.Assembly.GetName().Name,
                    interfaceType = typeof(IVersionTextProvider).FullName,
                    interfaceAssembly = typeof(IVersionTextProvider).Assembly.GetName().Name,
                    getComponentGeneric = Identity(genericGet),
                    getComponentType = Identity(typedGet),
                    tryGetComponent = got + ":" + Identity(tryGet),
                    getComponents = all.Length + ":" + string.Join(",", all.Select(Identity).ToArray()),
                    getComponentInChildren = Identity(genericGet),
                    getComponentInParent = Identity(fromParent),
                    interfaceComponent = Identity(interfaceGet as Component),
                    baseComponent = Identity(baseGet),
                    addComponentGeneric = Identity(addedGeneric),
                    addComponentType = Identity(addedType),
                    createInstanceGeneric = Identity(createdGeneric),
                    createInstanceType = Identity(createdType),
                    createInstanceString = Identity(createdString),
                    instantiateExisting = Identity(cloned),
                    serializedState = component.ReadM07SerializedState(),
                    messageMarker = component.RunM07MessagePaths(),
                    p04RuntimeValue = component.WriteAndReadM07RuntimeOnlyField(704),
                    p05SerializedValue = component.ReadM07AddedSerializedField(),
                };
                return JsonUtility.ToJson(result);
            }
            finally
            {
                if (cloned != null) UnityEngine.Object.Destroy(cloned);
                if (createdString != null) UnityEngine.Object.Destroy(createdString);
                if (createdType != null) UnityEngine.Object.Destroy(createdType);
                if (createdGeneric != null) UnityEngine.Object.Destroy(createdGeneric);
                UnityEngine.Object.Destroy(typeHost);
                UnityEngine.Object.Destroy(genericHost);
            }
        }

        private static string Identity(UnityEngine.Object value)
        {
            return value == null ? "null" : value.GetType().Assembly.GetName().Name + ":" + value.GetType().FullName;
        }
    }
}
