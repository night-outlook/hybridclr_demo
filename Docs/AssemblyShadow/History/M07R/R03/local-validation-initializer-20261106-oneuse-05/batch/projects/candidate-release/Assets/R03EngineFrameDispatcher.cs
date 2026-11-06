using System;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadow.R03.IR
{
    // Test-only frame callback. The independent engine witness must be raised
    // from the running Player loop, not from BeforeSceneLoad initialization.
    // This script is copied into the disposable R03 project only.
    [Preserve]
    public sealed class R03EngineFrameDispatcher : MonoBehaviour
    {
        private Exception _sentinel;
        private bool _armed;
        private bool _dispatched;

        internal void Arm(Exception sentinel)
        {
            if (_armed || sentinel == null)
                throw new InvalidOperationException("R03IR frame witness already armed or missing sentinel");
            _sentinel = sentinel;
            _armed = true;
        }

        [Preserve]
        private void Update()
        {
            if (!_armed || _dispatched)
                return;
            _dispatched = true;
            // The native failure is the original genuine runtime failure.
            // Only the already-running Update frame may unwind and deliver
            // the previously allocated sentinel to Unity's own reporter.
            if (R03TerminalPlayer.ForceEngineFailureOnFrame() != 1)
                throw new InvalidOperationException("R03IR: native terminal failure was not published");
            throw _sentinel;
        }
    }
}
