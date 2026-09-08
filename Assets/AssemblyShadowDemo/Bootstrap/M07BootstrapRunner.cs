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
            bool r00 = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR00Mode") >= 0;
            bool r01 = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01Mode") >= 0;
            IEnumerator work = null;
            try
            {
                if (r00 && r01) throw new InvalidOperationException("M07 R00 and R01 modes cannot run together.");
                work = r01
                    ? M07R01Probe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : r00
                    ? M07R00PerformanceProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : M07Probe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code);
                while (true)
                {
                    bool moved;
                    try { moved = work.MoveNext(); }
                    catch (Exception error)
                    {
                        exitCode = r01 ? M07R01Probe.CompleteCoroutineFailure(error) : r00 ? M07R00PerformanceProbe.CompleteCoroutineFailure(error) : M07Probe.CompleteCoroutineFailure(error);
                        break;
                    }
                    if (!moved) break;
                    yield return work.Current;
                }
            }
            finally
            {
                ReleaseProbe(ref work);
            }
            // Completed resource iterators retain scene AsyncOperations even
            // after Dispose. Release the owned chain and clear this coroutine's
            // Current on another frame before collecting while Unity is live.
            yield return null;
#if !UNITY_EDITOR
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
            GC.WaitForPendingFinalizers();
            Debug.Log("[AssemblyShadow M07] Completed probe references released; two pre-quit collection cycles completed.");
            Application.Quit(exitCode);
#endif
        }

        private static void ReleaseProbe(ref IEnumerator work)
        {
            IEnumerator completed = work;
            work = null;
            var disposable = completed as IDisposable;
            if (disposable != null) disposable.Dispose();
        }
    }
}
