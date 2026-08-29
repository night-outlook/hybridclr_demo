using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    // Imported only by the Editor test assembly, whose real AssemblyRefs include
    // the candidate witnesses. It is never part of a Player startup scene.
    public sealed class M06EarlyStartupProbe : MonoBehaviour
    {
        private void Awake() { }
    }
}
