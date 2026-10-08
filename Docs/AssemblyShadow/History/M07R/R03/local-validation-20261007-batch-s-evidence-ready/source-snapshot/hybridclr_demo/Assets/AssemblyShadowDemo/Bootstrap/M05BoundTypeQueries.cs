using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    // These deliberately direct receiver chains are independently verified in
    // compiler and linked IL. Keep validation/materialization in the caller so
    // the observations exercise the raw APIs, not generated expected handles.
    [Preserve]
    public static class M05BoundTypeQueries
    {
        [Preserve]
        public static Type[] GetTypes(string assemblyName)
        {
            switch (assemblyName)
            {
                case "AssemblyA.Contracts": return Assembly.Load("AssemblyA.Contracts").GetTypes();
                case "AssemblyA.Implementation.Extensibility": return Assembly.Load("AssemblyA.Implementation.Extensibility").GetTypes();
                case "AssemblyA.Implementation.Internal": return Assembly.Load("AssemblyA.Implementation.Internal").GetTypes();
                case "AssemblyShadowDemo.ContractsConsumer": return Assembly.Load("AssemblyShadowDemo.ContractsConsumer").GetTypes();
                case "AssemblyShadowDemo.ExtensibilityConsumer": return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer").GetTypes();
                default: throw new ArgumentOutOfRangeException("assemblyName");
            }
        }

        [Preserve]
        public static IEnumerable<TypeInfo> GetDefinedTypes(string assemblyName)
        {
            switch (assemblyName)
            {
                case "AssemblyA.Contracts": return Assembly.Load("AssemblyA.Contracts").DefinedTypes;
                case "AssemblyA.Implementation.Extensibility": return Assembly.Load("AssemblyA.Implementation.Extensibility").DefinedTypes;
                case "AssemblyA.Implementation.Internal": return Assembly.Load("AssemblyA.Implementation.Internal").DefinedTypes;
                case "AssemblyShadowDemo.ContractsConsumer": return Assembly.Load("AssemblyShadowDemo.ContractsConsumer").DefinedTypes;
                case "AssemblyShadowDemo.ExtensibilityConsumer": return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer").DefinedTypes;
                default: throw new ArgumentOutOfRangeException("assemblyName");
            }
        }

        [Preserve]
        public static IEnumerable<Type> GetExportedTypes(string assemblyName)
        {
            switch (assemblyName)
            {
                case "AssemblyA.Contracts": return Assembly.Load("AssemblyA.Contracts").ExportedTypes;
                case "AssemblyA.Implementation.Extensibility": return Assembly.Load("AssemblyA.Implementation.Extensibility").ExportedTypes;
                case "AssemblyA.Implementation.Internal": return Assembly.Load("AssemblyA.Implementation.Internal").ExportedTypes;
                case "AssemblyShadowDemo.ContractsConsumer": return Assembly.Load("AssemblyShadowDemo.ContractsConsumer").ExportedTypes;
                case "AssemblyShadowDemo.ExtensibilityConsumer": return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer").ExportedTypes;
                default: throw new ArgumentOutOfRangeException("assemblyName");
            }
        }

        [Preserve]
        public static Type[] GetModuleTypes(string assemblyName)
        {
            switch (assemblyName)
            {
                case "AssemblyA.Contracts": return Assembly.Load("AssemblyA.Contracts").ManifestModule.GetTypes();
                case "AssemblyA.Implementation.Extensibility": return Assembly.Load("AssemblyA.Implementation.Extensibility").ManifestModule.GetTypes();
                case "AssemblyA.Implementation.Internal": return Assembly.Load("AssemblyA.Implementation.Internal").ManifestModule.GetTypes();
                case "AssemblyShadowDemo.ContractsConsumer": return Assembly.Load("AssemblyShadowDemo.ContractsConsumer").ManifestModule.GetTypes();
                case "AssemblyShadowDemo.ExtensibilityConsumer": return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer").ManifestModule.GetTypes();
                default: throw new ArgumentOutOfRangeException("assemblyName");
            }
        }

        [Preserve]
        public static Type GetModuleType(string assemblyName)
        {
            switch (assemblyName)
            {
                case "AssemblyA.Contracts": return Assembly.Load("AssemblyA.Contracts").ManifestModule.GetType("AssemblyA.Contracts.AssemblyAContractVersion", true, false);
                case "AssemblyA.Implementation.Extensibility": return Assembly.Load("AssemblyA.Implementation.Extensibility").ManifestModule.GetType("AssemblyA.Implementation.Extensibility.VersionedComponentBase", true, false);
                case "AssemblyA.Implementation.Internal": return Assembly.Load("AssemblyA.Implementation.Internal").ManifestModule.GetType("AssemblyA.Implementation.Internal.InternalEntry", true, false);
                case "AssemblyShadowDemo.ContractsConsumer": return Assembly.Load("AssemblyShadowDemo.ContractsConsumer").ManifestModule.GetType("AssemblyShadowDemo.Consumers.ContractsConsumer", true, false);
                case "AssemblyShadowDemo.ExtensibilityConsumer": return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer").ManifestModule.GetType("AssemblyShadowDemo.Consumers.DerivedExternalComponent", true, false);
                default: throw new ArgumentOutOfRangeException("assemblyName");
            }
        }
    }
}
