using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowBaseline
{
    [Preserve]
    public sealed class BaselineProbe : MonoBehaviour
    {
        public int number = 1234;

        [Preserve]
        public string Read() => "M00-AOT-OK|" + number;
    }
}
