using UnityEngine;

namespace AssemblyShadowDemo
{
    /// <summary>The build supplies the accepted M04 baseline and runtime ABI.</summary>
    public sealed class M04BootstrapRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake()
        {
            int result = AssemblyShadowDemo.M04ReferenceProbe.RunAndWrite(expectedBaselineBuildId, expectedRuntimeAbiHash);
            Application.Quit(result);
        }
    }
}
