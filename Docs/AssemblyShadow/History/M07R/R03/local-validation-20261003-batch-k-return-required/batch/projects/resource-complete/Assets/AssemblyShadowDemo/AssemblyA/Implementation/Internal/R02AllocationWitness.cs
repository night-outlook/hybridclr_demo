using System;
using System.Reflection;
using System.Threading;
using UnityEngine.Scripting;

namespace AssemblyA.Implementation.Internal
{
    // Deliberately independent of Unity objects. Constructors, not native guard
    // counters, are the semantic oracle. All calls occur after R00 activation.
    [Preserve]
    public static class R02AllocationWitness
    {
#if ASSEMBLY_SHADOW_P03
        private const int Marker = 3003;
#elif ASSEMBLY_SHADOW_P01
        private const int Marker = 3001;
#else
        private const int Marker = 3000;
#endif
        private static int created;
        private static Func<int, long>[] scale;
        private static Type[] scaleTypes;
        [Preserve] public static int GetMarker() { return Marker; }
        [Preserve] public static int GetConstructorCount() { return Interlocked.CompareExchange(ref created, 0, 0); }

        [Preserve]
        public static long Run(int operation, int count, int seed)
        {
            if (count < 1 || count > 10000) throw new ArgumentOutOfRangeException(nameof(count));
            if (operation < 0 || operation > 7) throw new ArgumentOutOfRangeException(nameof(operation));
            long sum = 0;
            for (int i = 0; i < count; ++i)
            {
                int value = checked(seed + i);
                switch (operation)
                {
                    case 0: sum += new Payload(value).Read(); break;
                    case 1: sum += (i & 1) == 0 ? new Box<int>(value).Read() : new Box<long>(value).Read(); break;
                    case 2:
                        var array = new Payload[2]; array[0] = new Payload(value);
                        sum += array[0].Read(); GC.KeepAlive(array); break;
                    case 3:
                        object boxed = new ValuePayload(value); sum += ((ValuePayload)boxed).Read();
                        GC.KeepAlive(boxed); break;
                    case 4:
                        Payload polymorphic = new DerivedPayload(value); sum += polymorphic.Read(); break;
                    case 5:
                        IValue throughInterface = new DerivedPayload(value); sum += throughInterface.Read(); break;
                    case 6:
                        Func<long> throughDelegate = new DerivedPayload(value).Read; sum += throughDelegate(); break;
                    case 7:
#if ASSEMBLY_SHADOW_P01 || ASSEMBLY_SHADOW_P03
                        sum += new AddedPayload(value).Read(); break;
#else
                        throw new InvalidOperationException("AddedPayload is a patch-only workload.");
#endif
                }
            }
            return sum;
        }

        [Preserve]
        public static int PrepareScale()
        {
            if (scale != null) return scale.Length;
            // 1000 distinct complete reference-type constructions, without
            // generating 1000 nested value-type generic instantiations.
            Type[] markers = { typeof(M0), typeof(M1), typeof(M2), typeof(M3), typeof(M4),
                typeof(M5), typeof(M6), typeof(M7), typeof(M8), typeof(M9) };
            MethodInfo factory = typeof(R02AllocationWitness).GetMethod(nameof(ScaleFactory), BindingFlags.Public | BindingFlags.Static);
            var prepared = new Func<int, long>[1000];
            var preparedTypes = new Type[1000];
            for (int a = 0; a < 10; ++a)
                for (int b = 0; b < 10; ++b)
                    for (int c = 0; c < 10; ++c)
                    {
                        Type type = typeof(Triple<,,>).MakeGenericType(markers[a], markers[b], markers[c]);
                        preparedTypes[a * 100 + b * 10 + c] = typeof(Box<>).MakeGenericType(type);
                        prepared[a * 100 + b * 10 + c] = (Func<int, long>)Delegate.CreateDelegate(
                            typeof(Func<int, long>), factory.MakeGenericMethod(type));
                    }
            // Preparation is main-thread-only and precedes all worker launches.
            scaleTypes = preparedTypes;
            scale = prepared;
            return scale.Length;
        }

        [Preserve]
        public static string[] GetScaleTypeHandles()
        {
            if (scaleTypes == null) throw new InvalidOperationException("PrepareScale must run first.");
            var handles = new string[scaleTypes.Length];
            for (int i = 0; i < handles.Length; ++i)
                handles[i] = scaleTypes[i].TypeHandle.Value.ToInt64().ToString();
            return handles;
        }

        [Preserve]
        public static long RunScale(int typeCount, int passes, int seed)
        {
            if (scale == null) throw new InvalidOperationException("PrepareScale must run first.");
            if (typeCount != 100 && typeCount != 1000) throw new ArgumentOutOfRangeException(nameof(typeCount));
            if (passes < 1 || passes > 10) throw new ArgumentOutOfRangeException(nameof(passes));
            long sum = 0;
            for (int p = 0; p < passes; ++p)
                for (int i = 0; i < typeCount; ++i)
                    sum += scale[i](checked(seed + p * typeCount + i));
            return sum;
        }

        [Preserve] public static long ScaleFactory<T>(int seed) { return new Box<T>(seed).Read(); }

        // Compile the required AOT value-type and reference-sharing bodies.
        // Preserve this method, but never execute it before a measured row.
        [Preserve]
        public static long AotReferences(int seed)
        {
            return new Box<int>(seed).Read() + new Box<long>(seed).Read() +
                ScaleFactory<Triple<M0, M0, M0>>(seed) + ScaleFactory<Triple<object, object, object>>(seed);
        }

        [Preserve] public interface IValue { long Read(); }
        [Preserve]
        public class Payload : IValue
        {
            public readonly int Seed;
            [Preserve] public Payload(int seed) { Seed = seed; Interlocked.Increment(ref created); }
            [Preserve] public virtual long Read() { return Seed * 17L + Marker; }
        }
        [Preserve] public sealed class DerivedPayload : Payload
        {
            [Preserve] public DerivedPayload(int seed) : base(seed) { }
            [Preserve] public override long Read() { return base.Read(); }
        }
        [Preserve] public sealed class Box<T>
        {
            public readonly int Seed;
            public T Value;
            [Preserve] public Box(int seed) { Seed = seed; Value = default(T); Interlocked.Increment(ref created); }
            [Preserve] public long Read() { return Seed * 17L + Marker; }
        }
        [Preserve] public struct ValuePayload
        {
            public readonly int Seed;
            [Preserve] public ValuePayload(int seed) { Seed = seed; Interlocked.Increment(ref created); }
            [Preserve] public long Read() { return Seed * 17L + Marker; }
        }
#if ASSEMBLY_SHADOW_P01 || ASSEMBLY_SHADOW_P03
        [Preserve] public sealed class AddedPayload : Payload
        {
            [Preserve] public AddedPayload(int seed) : base(seed) { }
        }
#endif
        [Preserve] public sealed class Triple<A, B, C> { public A First; public B Second; public C Third; }
        [Preserve] public sealed class M0 { }
        [Preserve] public sealed class M1 { }
        [Preserve] public sealed class M2 { }
        [Preserve] public sealed class M3 { }
        [Preserve] public sealed class M4 { }
        [Preserve] public sealed class M5 { }
        [Preserve] public sealed class M6 { }
        [Preserve] public sealed class M7 { }
        [Preserve] public sealed class M8 { }
        [Preserve] public sealed class M9 { }
    }
}
