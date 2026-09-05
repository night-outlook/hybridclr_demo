using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Preserve]
    public sealed class M07BootstrapRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake()
        {
            DontDestroyOnLoad(gameObject);
        }

        private IEnumerator Start()
        {
            int exitCode = 2;
            IEnumerator work = null;
            try
            {
                work = M07Probe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code);
                while (true)
                {
                    bool moved;
                    try { moved = work.MoveNext(); }
                    catch (Exception error)
                    {
                        exitCode = M07Probe.CompleteCoroutineFailure(error);
                        var failed = work as IDisposable;
                        if (failed != null) failed.Dispose();
                        work = null;
                        break;
                    }
                    if (!moved) break;
                    yield return work.Current;
                }
            }
            finally
            {
                var disposable = work as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
#if !UNITY_EDITOR
            Application.Quit(exitCode);
#endif
        }
    }
}
