using System;
using System.Collections.Generic;
using System.Threading;
using AssemblyA.Implementation.Internal;
using AssemblyShadowDemo;
public static class Program
{
    static int checks;
    static void Check(bool ok) { ++checks; if (!ok) throw new Exception("Check " + checks + " failed"); }
    static long Expected(int n, int seed, int marker) { long sum = 0; for (int i = 0; i < n; ++i) sum += (seed + i) * 17L + marker; return sum; }
    static void Reject(Action action) { bool threw = false; try { action(); } catch (ArgumentException) { threw = true; } Check(threw); }
    public static int Main()
    {
        try
        {
            int marker = R02AllocationWitness.GetMarker();
#if ASSEMBLY_SHADOW_P03
            Check(marker == 3003);
#elif ASSEMBLY_SHADOW_P01
            Check(marker == 3001);
#else
            Check(marker == 3000);
#endif
            for (int op = 0; op < (marker == 3000 ? 7 : 8); ++op)
                foreach (int count in new[] { 1, 10, 10000 })
                {
                    int before = R02AllocationWitness.GetConstructorCount();
                    Check(R02AllocationWitness.Run(op, count, 3017) == Expected(count, 3017, marker));
                    Check(R02AllocationWitness.GetConstructorCount() - before == count);
                    Check(R02PlayerProbe.Expected(count, 3017, marker) == Expected(count, 3017, marker));
                }
            Reject(() => R02AllocationWitness.Run(-1, 1, 1));
            Reject(() => R02AllocationWitness.Run(8, 1, 1));
            Reject(() => R02AllocationWitness.Run(0, 0, 1));
            Reject(() => R02AllocationWitness.Run(0, 10001, 1));
            Check(R02AllocationWitness.PrepareScale() == 1000);
            string[] handles = R02AllocationWitness.GetScaleTypeHandles();
            Check(handles.Length == 1000 && new HashSet<string>(handles).Count == 1000);
            Check(R02AllocationWitness.PrepareScale() == 1000);
            foreach (int size in new[] { 100, 1000 })
            {
                int before = R02AllocationWitness.GetConstructorCount();
                Check(R02AllocationWitness.RunScale(size, 2, 17) == Expected(size * 2, 17, marker));
                Check(R02AllocationWitness.GetConstructorCount() - before == size * 2);
            }
            Reject(() => R02AllocationWitness.RunScale(99, 1, 0));
            Reject(() => R02AllocationWitness.RunScale(100, 0, 0));
            var threads = new Thread[8]; var outputs = new long[8]; var errors = new Exception[8];
            int start = R02AllocationWitness.GetConstructorCount();
            for (int i = 0; i < threads.Length; ++i)
            {
                int index = i;
                threads[i] = new Thread(() => { try { outputs[index] = R02AllocationWitness.Run(0, 1000, index); } catch (Exception error) { errors[index] = error; } });
                threads[i].Start();
            }
            for (int i = 0; i < threads.Length; ++i)
            { Check(threads[i].Join(10000)); Check(errors[i] == null); Check(outputs[i] == Expected(1000, i, marker)); }
            Check(R02AllocationWitness.GetConstructorCount() - start == 8000);
            Console.WriteLine("{\"kind\":\"R02ManagedHostTests\",\"result\":\"Passed\",\"checks\":" + checks + ",\"marker\":" + marker + ",\"unityPlayerRun\":false}");
            return 0;
        }
        catch (Exception error) { Console.Error.WriteLine(error); return 1; }
    }
}
