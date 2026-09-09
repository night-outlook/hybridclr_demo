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
            bool r01b = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01BManifest") >= 0;
            bool r01bLazy = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01BLazyDll") >= 0;
            bool r01bMixed = r01b && Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01BMixed") >= 0;
            bool r01Failure = Array.IndexOf(Environment.GetCommandLineArgs(), "-shadowR01FailureMode") >= 0;
            IEnumerator work = null;
            try
            {
                if ((r00 ? 1 : 0) + (r01 ? 1 : 0) + (r01b ? 1 : 0) + (r01bLazy ? 1 : 0) + (r01Failure ? 1 : 0) > 1)
                    throw new InvalidOperationException("M07 revision modes cannot run together.");
                work = r01bLazy
                    ? R01BLazyProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : r01bMixed
                    ? RunR01BMixed(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : r01b
                    ? R01BCapacityProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : r01Failure
                    ? R01FailureProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : r01
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
                        exitCode = r01bLazy ? R01BLazyProbe.CompleteCoroutineFailure(error) : r01b ? R01BCapacityProbe.CompleteCoroutineFailure(error) : r01Failure ? R01FailureProbe.CompleteCoroutineFailure(error) : r01 ? M07R01Probe.CompleteCoroutineFailure(error) : r00 ? M07R00PerformanceProbe.CompleteCoroutineFailure(error) : M07Probe.CompleteCoroutineFailure(error);
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

        private static IEnumerator RunR01BMixed(string baselineBuildId, string runtimeAbiHash, Action<int> completed)
        {
            int m07ExitCode = 2;
            IEnumerator m07 = M07Probe.RunAndWriteCoroutine(baselineBuildId, runtimeAbiHash, code => m07ExitCode = code);
            try
            {
                while (true)
                {
                    bool moved;
                    try { moved = m07.MoveNext(); }
                    catch (Exception error)
                    {
                        m07ExitCode = M07Probe.CompleteCoroutineFailure(error);
                        break;
                    }
                    if (!moved) break;
                    yield return m07.Current;
                }
            }
            finally
            {
                var disposable = m07 as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
            if (m07ExitCode != 0)
            {
                completed(m07ExitCode);
                yield break;
            }

            IEnumerator capacity = R01BCapacityProbe.RunAndWriteCoroutine(baselineBuildId, runtimeAbiHash, completed);
            try
            {
                while (capacity.MoveNext()) yield return capacity.Current;
            }
            finally
            {
                var disposable = capacity as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
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
