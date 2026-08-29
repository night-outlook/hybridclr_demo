using System;
using UnityEngine;

namespace AssemblyShadowDemo
{
    // Runtime, test-only witness for M06 startup-policy validation. Editor tests
    // inject it into a test-owned scene copy to prove that an ordinary fixed
    // callback with a real Contracts AssemblyRef cannot run before activation.
    public sealed class M06EarlyStartupProbe : MonoBehaviour
    {
        private void Awake() { }
        private static Type CandidateDependency() { return typeof(AssemblyA.Contracts.AssemblyAContractVersion); }
    }
}
