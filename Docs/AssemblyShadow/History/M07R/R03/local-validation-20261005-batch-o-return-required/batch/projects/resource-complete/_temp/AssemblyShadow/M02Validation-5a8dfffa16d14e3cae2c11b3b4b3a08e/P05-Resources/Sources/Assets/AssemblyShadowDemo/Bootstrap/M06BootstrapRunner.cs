using System;
using System.Collections;
using UnityEngine;

namespace AssemblyShadowDemo
{
    [DefaultExecutionOrder(-32000)]
    public sealed class M06BootstrapRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake()
        {
            StartCoroutine(RunCoroutine());
        }

        private IEnumerator RunCoroutine()
        {
            int exitCode = -1;
            IEnumerator work = M06ExecutionProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code);
            try
            {
                while (true)
                {
                    bool moved;
                    try { moved = work.MoveNext(); }
                    catch (Exception error)
                    {
                        Debug.LogException(error);
                        exitCode = 2;
                        break;
                    }
                    if (!moved) break;
                    yield return work.Current;
                }
            }
            finally
            {
                try { IDisposable disposable = work as IDisposable; if (disposable != null) disposable.Dispose(); }
                catch (Exception error) { Debug.LogException(error); exitCode = 2; }
            }
            Application.Quit(exitCode < 0 ? 2 : exitCode);
        }
    }
}
