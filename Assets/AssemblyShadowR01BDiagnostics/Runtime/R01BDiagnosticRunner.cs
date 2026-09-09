using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Preserve]
    public sealed class R01BDiagnosticRunner : MonoBehaviour
    {
        [SerializeField] private string expectedBaselineBuildId;
        [SerializeField] private string expectedRuntimeAbiHash;

        private void Awake() { DontDestroyOnLoad(gameObject); }

        private IEnumerator Start()
        {
            int exitCode = 2;
            bool lazy = HasArgument("-shadowR01BLazyDll");
            bool capacity = HasArgument("-shadowR01BManifest");
            try
            {
                if (lazy == capacity) throw new InvalidOperationException("R01B diagnostic Player requires exactly one probe mode.");
                IEnumerator work = lazy
                    ? R01BLazyProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code)
                    : R01BCapacityProbe.RunAndWriteCoroutine(expectedBaselineBuildId, expectedRuntimeAbiHash, code => exitCode = code);
                try
                {
                    if (work.MoveNext()) throw new InvalidOperationException("R01B diagnostic probe unexpectedly yielded.");
                }
                catch (Exception error)
                {
                    exitCode = lazy ? R01BLazyProbe.CompleteCoroutineFailure(error) : R01BCapacityProbe.CompleteCoroutineFailure(error);
                }
                var disposable = work as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
            catch (Exception error)
            {
                Debug.LogException(error);
            }
#if !UNITY_EDITOR
            Application.Quit(exitCode);
#endif
            yield break;
        }

        private static bool HasArgument(string name)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int index = 0; index < args.Length; ++index)
                if (args[index] == name) return true;
            return false;
        }
    }
}
