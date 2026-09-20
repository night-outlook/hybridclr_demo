using System;
using UnityEngine.Scripting;

namespace AssemblyA.Implementation.Internal
{
    /// <summary>
    /// Pure managed witness used by the R00 Player observation harness. It has
    /// no Unity object or resource dependency so the measured operations stay
    /// on the allocation, reflection, and generic execution paths.
    /// </summary>
    [Preserve]
    public static class R00PerformanceWitness
    {
#if ASSEMBLY_SHADOW_P03
        private const string Marker = "R00-P03";
        private const int MarkerValue = 3003;
#elif ASSEMBLY_SHADOW_P01
        private const string Marker = "R00-P01";
        private const int MarkerValue = 3001;
#else
        private const string Marker = "R00-BASELINE";
        private const int MarkerValue = 3000;
#endif

        [Preserve]
        public static string GetMarker()
        {
            return Marker;
        }

        [Preserve]
        public static R00PerformancePayload NewPayload(int seed)
        {
            return new R00PerformancePayload(seed, Marker, MarkerValue);
        }

        [Preserve]
        public static int GetConstructorCount()
        {
            return R00PerformancePayload.ConstructorCount;
        }

        [Preserve]
        public static int RunAllocationBatch(int count, int seed)
        {
            if (count < 1 || count > 10000) throw new ArgumentOutOfRangeException(nameof(count));
            int checksum = 0;
            for (int i = 0; i < count; ++i)
            {
                R00PerformancePayload payload = NewPayload(seed + i);
                checksum = unchecked(checksum + payload.Checksum);
            }
            return checksum;
        }

        [Preserve]
        public static int InvokeStep(int value)
        {
            return unchecked(value * 31 + MarkerValue);
        }

        [Preserve]
        public static T ClosedGeneric<T>(T value)
        {
            return value;
        }

        // Retain an explicit int MethodSpec for the native ON/OFF baselines.
        // The observation harness never executes this reference before timing.
        [Preserve]
        public static int ClosedGenericIntAotReference(int value)
        {
            return ClosedGeneric<int>(value);
        }
    }

    [Preserve]
    public sealed class R00PerformancePayload
    {
        internal static int ConstructorCount;

        [Preserve]
        public readonly int Seed;
        [Preserve]
        public readonly string Marker;
        [Preserve]
        public readonly int MarkerValue;

        [Preserve]
        public R00PerformancePayload(int seed, string marker, int markerValue)
        {
            ++ConstructorCount;
            Seed = seed;
            Marker = marker;
            MarkerValue = markerValue;
        }

        [Preserve]
        public int Checksum
        {
            get { return unchecked(Seed * 17 + MarkerValue + Marker.Length); }
        }
    }
}
