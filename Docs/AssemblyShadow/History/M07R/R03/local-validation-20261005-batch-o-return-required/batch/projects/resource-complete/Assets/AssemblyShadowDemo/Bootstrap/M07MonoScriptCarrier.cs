using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>Fixed-AOT carrier used to preserve a real MonoScript object in the mixed bundle.</summary>
    [Preserve]
    public sealed class M07MonoScriptCarrier : ScriptableObject
    {
        [SerializeField] private UnityEngine.Object script;
        public UnityEngine.Object Script { get { return script; } }
    }
}
