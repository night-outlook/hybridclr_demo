using UnityEngine;

namespace AssemblyShadowDemo
{
    /// <summary>The build, not external fixtures, supplies the accepted baseline identity.</summary>
    public sealed class M03BootstrapRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake()
        {
            int result = M03TransactionProbe.RunAndWrite(expectedBaselineBuildId, expectedRuntimeAbiHash);
            Application.Quit(result);
        }
    }
}
