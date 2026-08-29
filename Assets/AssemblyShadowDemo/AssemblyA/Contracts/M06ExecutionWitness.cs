using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;

namespace AssemblyA.Contracts
{
    public interface IM06ContractWitness
    {
        string ContractValue { get; }
    }

    public delegate string M06ContractFormatter(int value);

    // This fixture deliberately uses only the stable primitive/object/string
    // boundary. Its outputs are observations of real operations, not expected
    // values injected by the Bootstrap.
    public static class M06ExecutionWitness
    {
#if ASSEMBLY_SHADOW_M06_P03
        private const string Marker = "M06-P03";
        private const int Generation = 6000;
#else
        private const string Marker = "M06-BASELINE";
        private const int Generation = 1000;
#endif
        private static int s_runCount;
        private static int s_cctorCount;
        private static string s_staticMarker;
        private static int s_moduleCount;
        private static long s_moduleStartTicks;
        private static long s_moduleEndTicks;
        private static long s_moduleFrequency;
        private static string s_providerAssembly = "none";
        private static string s_providerMarker = "none";
        private static int s_providerCount;
        private static int s_beforeFieldInitCalls;

        static M06ExecutionWitness()
        {
            ++s_cctorCount;
            s_staticMarker = Marker;
        }

        public static string[] Run(string phase)
        {
            if (phase == null) throw new ArgumentNullException(nameof(phase));
            ++s_runCount;
            switch (phase)
            {
                case "new": return NewObservations();
                case "statics": return StaticObservations();
                case "dispatch": return DispatchObservations();
                case "delegates": return DelegateObservations();
                case "generics": return GenericObservations();
                case "exceptions": return ExceptionObservations();
                case "warmup": return WarmupObservations();
                case "async": return new[] { "async=sync-boundary", "marker=" + Marker };
                default: throw new ArgumentException("Unknown M06 phase: " + phase, nameof(phase));
            }
        }

        public static string[] GetModuleEvidence()
        {
            return new[] { "assembly=AssemblyA.Contracts", "marker=" + s_staticMarker,
                "cctor=" + s_cctorCount, "runs=" + s_runCount, "module.count=" + s_moduleCount,
                "module.startTicks=" + s_moduleStartTicks, "module.endTicks=" + s_moduleEndTicks,
                "module.frequency=" + s_moduleFrequency, "provider.assembly=" + s_providerAssembly,
                "provider.marker=" + s_providerMarker,
                "provider.count=" + s_providerCount };
        }

        internal static void BeginModuleInitialization(long startTicks)
        {
            s_moduleStartTicks = startTicks;
            s_moduleFrequency = System.Diagnostics.Stopwatch.Frequency;
        }

        internal static void RecordModuleProvider(string providerAssembly, string providerMarker, int providerCount)
        {
            ++s_moduleCount;
            s_providerAssembly = providerAssembly ?? "none";
            s_providerMarker = providerMarker ?? "none";
            s_providerCount = providerCount;
        }

        internal static void EndModuleInitialization()
        {
            s_moduleEndTicks = System.Diagnostics.Stopwatch.GetTimestamp();
        }

        public static async Task<string[]> RunAsync()
        {
            var observations = new List<string>();
            using (var cancellation = new CancellationTokenSource())
            {
                cancellation.Cancel();
                try { await CancelledAsync(cancellation.Token); }
                catch (OperationCanceledException error) { observations.Add("cancel=" + error.GetType().Name); }
            }
            try { await ThrowAsync(); }
            catch (InvalidOperationException error) { observations.Add("async.throw=" + error.Message); }
            var iterator = Iterate(observations).GetEnumerator();
            try
            {
                observations.Add("iterator.moveNext=" + iterator.MoveNext());
                observations.Add("iterator.value=" + iterator.Current);
            }
            finally { iterator.Dispose(); observations.Add("iterator.disposed=true"); }
            observations.AddRange(Run("async"));
            return observations.ToArray();
        }

        public static IEnumerator RunCoroutine(List<string> observations)
        {
            if (observations == null) throw new ArgumentNullException(nameof(observations));
            observations.Add("coroutine.begin=" + Marker);
            yield return null;
            observations.Add("coroutine.continuation=" + WarmupValue(1));
        }

        public static int WarmupValue(int value) { return Generation + value; }
        public static T WarmupEcho<T>(T value) { return value; }

        private static string[] WarmupObservations()
        {
            var created = NewObservations();
            var dispatched = DispatchObservations();
            var generic = GenericObservations();
            return new[] { "phase=warmup", "warmup=" + WarmupValue(7), "echo=" + WarmupEcho("warmup"),
                "new=" + created[1], "dispatch=" + dispatched[1], "generic=" + generic[1] };
        }

        private static string[] NewObservations()
        {
            int before = ContractNode.ConstructorCount;
            var node = new ContractNode();
            var second = new ContractNode();
            IVersionTextProvider provider = node;
            int eventCount = 0;
            node.Changed += () => ++eventCount;
            var helper = new List<string>(); helper.Add(node.Field); helper.Add(second.Field);
            return new[] { "phase=new", "marker=" + Marker, "ctor=" + node.Value,
                "field=" + node.Field, "interface=" + provider.GetVersionText(),
                "property=" + node.Property, "event=" + node.Raise() + ":" + eventCount,
                "ctor.first=" + node.Value, "ctor.second=" + second.Value,
                "ctor.count=" + (ContractNode.ConstructorCount - before), "helper.count=" + helper.Count,
                "default.ctor=" + new DefaultNode().Value };
        }

        private static string[] StaticObservations()
        {
            GenericState<int>.Count++;
            GenericState<string>.Count++;
            int explicitFirst = ++ExplicitStaticState.Value;
            int beforeIntFirst = BeforeFieldInitState<int>.Value;
            int beforeStringFirst = BeforeFieldInitState<string>.Value;
            int beforeIntSecond = BeforeFieldInitState<int>.Value;
            int beforeStringSecond = BeforeFieldInitState<string>.Value;
            bool beforeFieldInit = (typeof(BeforeFieldInitState<int>).Attributes & TypeAttributes.BeforeFieldInit) != 0;
            return new[] { "phase=statics", "marker=" + s_staticMarker, "cctor=" + s_cctorCount,
                "generic.int=" + GenericState<int>.Count, "generic.string=" + GenericState<string>.Count,
                "generic.int.repeat=" + (++GenericState<int>.Count), "generic.string.repeat=" + (++GenericState<string>.Count),
                "explicit.value=" + explicitFirst, "explicit.type=" + typeof(ExplicitStaticState).FullName,
                "beforefieldinit.flag=" + beforeFieldInit, "beforefieldinit.int.first=" + beforeIntFirst,
                "beforefieldinit.int.repeat=" + beforeIntSecond, "beforefieldinit.string.first=" + beforeStringFirst,
                "beforefieldinit.string.repeat=" + beforeStringSecond, "beforefieldinit.count=" + s_beforeFieldInitCalls };
        }

        private static string[] DispatchObservations()
        {
            var node = new ContractNode();
            ContractNode baseNode = node;
            return new[] { "phase=dispatch", "virtual=" + baseNode.Dispatch(),
                "base=" + node.BaseDispatch(), "index=" + node[2], "interface=" + ((IVersionTextProvider)node).GetVersionText(),
                "contract.interface=" + ((IM06ContractWitness)node).ContractValue };
        }

        private static string[] DelegateObservations()
        {
            var node = new ContractNode();
            M06ContractFormatter contractDelegate = node.Format;
            Func<int, string> instance = node.Format;
            Func<int, string> statics = FormatStatic;
            Func<int, string> closed = value => node.Format(value + 1);
            int firstCount = 0; int secondCount = 0;
            Action first = () => { ++firstCount; node.Format(3); };
            Action second = () => { ++secondCount; node.Format(4); };
            Action multicast = first + second;
            int invocationCount = multicast.GetInvocationList().Length;
            multicast();
            node.Changed += first;
            node.Raise();
            int beforeRemoval = firstCount;
            node.Changed -= first;
            node.Raise();
            int afterRemoval = firstCount;
            return new[] { "phase=delegates", "instance=" + instance(2), "static=" + statics(2),
                "closed=" + closed(2), "contract.delegate=" + contractDelegate(2), "multicast=" + instance(2), "invocation.count=" + invocationCount,
                "handler.first=" + firstCount, "handler.second=" + secondCount, "event.beforeRemove=" + beforeRemoval,
                "event.afterRemove=" + afterRemoval, "event.removed=" + (beforeRemoval == afterRemoval) };
        }

        private static string[] GenericObservations()
        {
            var value = new DemoValue { number = 4, text = Marker };
            var box = new GenericBox<DemoValue> { Value = value };
            Type closed = typeof(GenericBox<>).MakeGenericType(typeof(DemoValue));
            DemoValue roundTrip = Echo(value);
            int? nullable = roundTrip.number;
            object boxed = nullable;
            MethodInfo reflected = typeof(M06ExecutionWitness).GetMethod("GenericMethod", BindingFlags.Static | BindingFlags.NonPublic).MakeGenericMethod(typeof(int));
            object reflectedValue = reflected.Invoke(null, new object[] { 6 });
            int refValue = 2; int outValue; RefOps(ref refValue, out outValue, in roundTrip);
            return new[] { "phase=generics", "generic.type=" + closed.FullName,
                "generic.value=" + box.Value.number, "method=" + roundTrip.text,
                "nullable=" + nullable.Value, "boxed=" + boxed, "generic.method=" + reflectedValue,
                "ref=" + refValue, "out=" + outValue, "array=" + new[] { roundTrip.number, outValue }.Length };
        }

        private static string[] ExceptionObservations()
        {
            string filter = "none";
            string finallyValue = "not-run";
            string wrapped = "none"; string stack = "none"; Exception inner = null; int token = typeof(M06ExecutionWitness).GetMethod("ThrowForEvidence").MetadataToken;
            try { typeof(M06ExecutionWitness).GetMethod("ThrowForEvidence").Invoke(null, null); }
            catch (TargetInvocationException error) { inner = error.InnerException; wrapped = inner.GetType().Name; stack = inner.StackTrace ?? ""; }
            catch (InvalidOperationException error) when (Filter(error)) { filter = error.Message; }
            finally { finallyValue = "ran"; }
            try { throw new InvalidOperationException(Marker); }
            catch (InvalidOperationException error) when (Filter(error)) { filter = error.Message; }
            var result = new List<string> { "phase=exceptions", "filter=" + filter, "finally=" + finallyValue,
                "wrapped=" + wrapped, "stack.text=" + stack, "stack.frames=" + CountFrames(stack), "method.token=" + token };
            var actualFrames = inner == null ? new System.Diagnostics.StackFrame[0] : new System.Diagnostics.StackTrace(inner, true).GetFrames();
            bool sourceAvailable = false;
            if (actualFrames != null)
            {
                for (int i = 0; i < actualFrames.Length; ++i)
                {
                    sourceAvailable = sourceAvailable || actualFrames[i].GetFileName() != null;
                    MethodBase frameMethod = actualFrames[i].GetMethod();
                    bool methodAvailable = frameMethod != null;
                    result.Add("frame." + i + ".methodAvailable=" + methodAvailable);
                    result.Add("frame." + i + ".declaringType=" + (!methodAvailable || frameMethod.DeclaringType == null ? "absent" : frameMethod.DeclaringType.FullName));
                    result.Add("frame." + i + ".method=" + (methodAvailable ? frameMethod.Name : "absent"));
                    result.Add("frame." + i + ".token=" + (methodAvailable ? frameMethod.MetadataToken : 0));
                    result.Add("frame." + i + ".file=" + (actualFrames[i].GetFileName() ?? "absent"));
                    result.Add("frame." + i + ".line=" + actualFrames[i].GetFileLineNumber());
                    result.Add("frame." + i + ".column=" + actualFrames[i].GetFileColumnNumber());
                }
            }
            result.Add("source.status=" + (sourceAvailable ? "available" : "absent"));
            return result.ToArray();
        }

        private static bool Filter(Exception error) { return error.Message == Marker; }
        [MethodImpl(MethodImplOptions.NoInlining)]
        public static void ThrowForEvidence() { ThrowNested(); }
        [MethodImpl(MethodImplOptions.NoInlining)]
        private static void ThrowNested() { throw new InvalidOperationException(Marker); }
        private static int CountFrames(string stack) { return string.IsNullOrEmpty(stack) ? 0 : stack.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries).Length; }
        private static async Task CancelledAsync(CancellationToken token) { await Task.Delay(1, token); }
        private static async Task ThrowAsync() { await Task.Yield(); throw new InvalidOperationException(Marker + ":async"); }
        private static IEnumerable<int> Iterate(List<string> trace)
        {
            try { trace.Add("iterator.begin=true"); yield return Generation; trace.Add("iterator.after=true"); }
            finally { trace.Add("iterator.finally=true"); }
        }
        private static T GenericMethod<T>(T value) { return value; }
        private static int InitializeBeforeFieldInit<T>() { ++s_beforeFieldInitCalls; return Generation + typeof(T).Name.Length + s_beforeFieldInitCalls; }
        private static void RefOps(ref int value, out int output, in DemoValue input) { value += input.number; output = value + 1; }
        private static string FormatStatic(int value) { return Marker + ":S" + value; }
        private static T Echo<T>(T value) { return value; }

        private class ContractNode : IVersionTextProvider, IM06ContractWitness
        {
            public static int ConstructorCount;
            public readonly int Value;
            public readonly string Field;
            public string Property { get; private set; }
            public event Action Changed;
            public ContractNode()
            {
                ++ConstructorCount;
                Value = Generation + 10;
                Field = Marker + ":field";
                Property = Marker + ":property";
            }
            public virtual string Dispatch() { return Marker + ":virtual"; }
            public string BaseDispatch() { return Marker + ":base"; }
            public string GetVersionText() { return Marker + ":interface"; }
            public string ContractValue { get { return Marker + ":contract"; } }
            public string Format(int value) { return Marker + ":I" + value; }
            public string Raise() { if (Changed != null) Changed(); return Marker + ":event"; }
            public string this[int index] { get { return Marker + ":index" + index; } }
        }

        private sealed class DefaultNode { public int Value { get { return Generation + 99; } } }

        private sealed class GenericBox<T> { public T Value; }
        private static class GenericState<T> { public static int Count; }
        private static class ExplicitStaticState { public static int Value; static ExplicitStaticState() { ++Value; } }
        private static class BeforeFieldInitState<T> { public static readonly int Value = InitializeBeforeFieldInit<T>(); }
    }
}
