using System;
using System.Collections;
using UnityEngine;

namespace AssemblyShadowDemo
{
    /// <summary>Invokes the selected M05 Player probe and exits with its result.</summary>
    public sealed class M05BootstrapRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake()
        {
            if (M05TypeProbe.IsResourceMode())
                StartCoroutine(RunResourceProbe());
            else
                Application.Quit(M05TypeProbe.RunAndWrite(expectedBaselineBuildId, expectedRuntimeAbiHash));
        }

        private IEnumerator RunResourceProbe()
        {
            int exitCode = -1;
            IEnumerator work = M05TypeProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code);
            while (true)
            {
                bool moved;
                try { moved = work.MoveNext(); }
                catch (Exception error)
                {
                    exitCode = M05TypeProbe.CompleteCoroutineFailure(error);
                    DisposeEnumerator(work);
                    work = null;
                    break;
                }
                if (!moved) break;
                object current = work.Current;
                yield return current;
            }
            DisposeEnumerator(work);
            Application.Quit(exitCode < 0 ? 2 : exitCode);
        }

        private static void DisposeEnumerator(IEnumerator work)
        {
            IDisposable disposable = work as IDisposable;
            if (disposable != null) disposable.Dispose();
        }
    }
}
