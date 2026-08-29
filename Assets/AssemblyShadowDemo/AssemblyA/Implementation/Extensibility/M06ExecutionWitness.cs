using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using AssemblyA.Contracts;

namespace AssemblyA.Implementation.Extensibility
{
    public abstract class M06ExecutionBase : IVersionTextProvider
    {
        [NonSerialized] private readonly string m_baseField;
        public static int BaseConstructorCount;
        protected M06ExecutionBase() { ++BaseConstructorCount; m_baseField = "M06-BASE-FIELD"; }
        public string BaseField { get { return m_baseField; } }
        public virtual string Dispatch() { return "M06-BASE-DISPATCH"; }
        public virtual string BaseDispatch() { return "M06-BASE-VIRTUAL"; }
        public abstract string AbstractDispatch();
        public virtual string BaseProperty { get { return "M06-BASE-PROPERTY"; } }
        public event Action BaseChanged;
        public string RaiseBase() { if (BaseChanged != null) BaseChanged(); return "M06-BASE-EVENT"; }
        public abstract string GetVersionText();
    }

    public static class M06ExecutionWitness
    {
#if ASSEMBLY_SHADOW_M06_P03
        private const string Marker = "M06-P03";
        private const int Generation = 6000;
#elif ASSEMBLY_SHADOW_M06_P02
        private const string Marker = "M06-P02";
        private const int Generation = 5000;
#else
        private const string Marker = "M06-BASELINE";
        private const int Generation = 1000;
#endif
        private static int s_runCount;
        private static int s_cctorCount;
        private static string s_staticMarker;
        private static int s_moduleCount;
        private static long s_moduleStartTicks, s_moduleEndTicks, s_moduleFrequency;
        private static string s_providerAssembly = "none";
        private static string s_providerMarker = "none";
        private static int s_providerCount;
        private static int s_beforeFieldInitCalls;
        static M06ExecutionWitness() { ++s_cctorCount; s_staticMarker = Marker; }

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

        public static string[] GetModuleEvidence() { return new[] { "assembly=AssemblyA.Implementation.Extensibility", "marker=" + s_staticMarker, "cctor=" + s_cctorCount, "runs=" + s_runCount, "module.count=" + s_moduleCount, "module.startTicks=" + s_moduleStartTicks, "module.endTicks=" + s_moduleEndTicks, "module.frequency=" + s_moduleFrequency, "provider.assembly=" + s_providerAssembly, "provider.marker=" + s_providerMarker, "provider.count=" + s_providerCount }; }
        internal static void BeginModuleInitialization(long startTicks) { s_moduleStartTicks = startTicks; s_moduleFrequency = System.Diagnostics.Stopwatch.Frequency; }
        internal static void RecordModuleProvider(string providerAssembly, string providerMarker, int providerCount) { ++s_moduleCount; s_providerAssembly = providerAssembly ?? "none"; s_providerMarker = providerMarker ?? "none"; s_providerCount = providerCount; }
        internal static void EndModuleInitialization() { s_moduleEndTicks = System.Diagnostics.Stopwatch.GetTimestamp(); }
        public static async Task<string[]> RunAsync()
        {
            var output = new List<string>();
            using (var cancellation = new CancellationTokenSource()) { cancellation.Cancel(); try { await CancelledAsync(cancellation.Token); } catch (OperationCanceledException e) { output.Add("cancel=" + e.GetType().Name); } }
            try { await ThrowAsync(); } catch (InvalidOperationException e) { output.Add("async.throw=" + e.Message); }
            var iterator = Iterate(output).GetEnumerator(); try { output.Add("iterator.moveNext=" + iterator.MoveNext()); output.Add("iterator.value=" + iterator.Current); } finally { iterator.Dispose(); output.Add("iterator.disposed=true"); }
            output.AddRange(Run("async")); return output.ToArray();
        }
        public static IEnumerator RunCoroutine(List<string> observations)
        {
            if (observations == null) throw new ArgumentNullException(nameof(observations));
            observations.Add("coroutine.begin=" + Marker); yield return null; observations.Add("coroutine.continuation=" + WarmupValue(1));
        }
        public static int WarmupValue(int value) { return Generation + value; }
        public static T WarmupEcho<T>(T value) { return value; }
        private static string[] WarmupObservations() { var n = NewObservations(); var d = DispatchObservations(); var g = GenericObservations(); return new[] { "phase=warmup", "warmup=" + WarmupValue(7), "echo=" + WarmupEcho("warmup"), "new=" + n[1], "dispatch=" + d[1], "generic=" + g[1] }; }

        private static string[] NewObservations()
        {
            int before = M06ExecutionBase.BaseConstructorCount; var node = new ExtNode(); var second = new ExtNode(); IVersionTextProvider provider = node; int eventCount = 0; node.Changed += () => ++eventCount;
            var helper = new List<string>(); helper.Add(node.Field); helper.Add(second.Field);
            return new[] { "phase=new", "marker=" + Marker, "ctor=" + node.Value, "field=" + node.Field,
                "interface=" + provider.GetVersionText(), "property=" + node.Property, "event=" + node.Raise() + ":" + eventCount,
                "ctor.first=" + node.Value, "ctor.second=" + second.Value, "ctor.count=" + (M06ExecutionBase.BaseConstructorCount - before), "helper.count=" + helper.Count, "base.field=" + node.BaseField, "base.property=" + node.BaseProperty, "base.event=" + node.RaiseBase() };
        }
        private static string[] StaticObservations()
        {
            GenericState<int>.Count++; GenericState<string>.Count++;
            int explicitFirst = ++ExplicitStaticState.Value;
            int beforeIntFirst = BeforeFieldInitState<int>.Value; int beforeStringFirst = BeforeFieldInitState<string>.Value;
            int beforeIntSecond = BeforeFieldInitState<int>.Value; int beforeStringSecond = BeforeFieldInitState<string>.Value;
            return new[] { "phase=statics", "marker=" + s_staticMarker, "cctor=" + s_cctorCount,
                "generic.int=" + GenericState<int>.Count, "generic.string=" + GenericState<string>.Count,
                "generic.int.repeat=" + (++GenericState<int>.Count), "generic.string.repeat=" + (++GenericState<string>.Count),
                "explicit.value=" + explicitFirst, "explicit.type=" + typeof(ExplicitStaticState).FullName,
                "beforefieldinit.flag=" + ((typeof(BeforeFieldInitState<int>).Attributes & TypeAttributes.BeforeFieldInit) != 0),
                "beforefieldinit.int.first=" + beforeIntFirst, "beforefieldinit.int.repeat=" + beforeIntSecond,
                "beforefieldinit.string.first=" + beforeStringFirst, "beforefieldinit.string.repeat=" + beforeStringSecond,
                "beforefieldinit.count=" + s_beforeFieldInitCalls };
        }
        private static string[] DispatchObservations()
        {
            ExtNode node = new ExtNode(); ExtNode baseNode = new SealedNode();
            return new[] { "phase=dispatch", "virtual=" + baseNode.Dispatch(), "base=" + node.BaseDispatch(),
                "abstract=" + node.AbstractDispatch(), "interface=" + ((IVersionTextProvider)node).GetVersionText(), "assignable=" + (node is M06ExecutionBase), "contract=" + AssemblyAContractVersion.Value };
        }
        private static string[] DelegateObservations()
        {
            var node = new ExtNode(); Func<int, string> instance = node.Format; Func<int, string> statics = FormatStatic;
            Func<int, string> closed = value => node.Format(value + 1); Func<int, string> multicast = instance + statics;
            int first = 0, second = 0; Action one = () => ++first; Action two = () => ++second; Action both = one + two; int count = both.GetInvocationList().Length; both();
            node.Changed += one; node.Raise(); int beforeRemoval = first; node.Changed -= one; node.Raise(); int afterRemoval = first;
            return new[] { "phase=delegates", "instance=" + instance(2), "static=" + statics(2), "closed=" + closed(2), "multicast=" + multicast(2), "invocation.count=" + count, "handler.first=" + first, "handler.second=" + second, "event.beforeRemove=" + beforeRemoval, "event.afterRemove=" + afterRemoval, "event.removed=" + (beforeRemoval == afterRemoval) };
        }
        private static string[] GenericObservations()
        {
            var value = new Pair<DemoValue> { Value = new DemoValue { number = 4, text = Marker } };
            Type closed = typeof(Pair<>).MakeGenericType(typeof(DemoValue)); DemoValue roundTrip = Echo(value.Value); int? nullable = roundTrip.number; object boxed = nullable;
            MethodInfo method = typeof(M06ExecutionWitness).GetMethod("GenericMethod", BindingFlags.NonPublic | BindingFlags.Static).MakeGenericMethod(typeof(int));
            object reflected = method.Invoke(null, new object[] { 6 });
            int refValue = 2, outValue; RefOps(ref refValue, out outValue, in roundTrip);
            return new[] { "phase=generics", "generic.type=" + closed.FullName, "generic.value=" + value.Value.number, "method=" + roundTrip.text, "nullable=" + nullable.Value, "boxed=" + boxed, "generic.method=" + reflected, "ref=" + refValue, "out=" + outValue, "array=" + new[] { refValue, outValue }.Length };
        }
        private static string[] ExceptionObservations()
        {
            string filter = "none", finallyValue = "not-run", wrapped = "none", stack = ""; Exception inner = null; int token = typeof(M06ExecutionWitness).GetMethod("ThrowForEvidence").MetadataToken;
            try { typeof(M06ExecutionWitness).GetMethod("ThrowForEvidence").Invoke(null, null); }
            catch (TargetInvocationException error) { inner = error.InnerException; wrapped = inner.GetType().Name; stack = inner.StackTrace ?? ""; }
            finally { finallyValue = "ran"; }
            try { throw new InvalidOperationException(Marker); } catch (InvalidOperationException error) when (Filter(error)) { filter = error.Message; }
            var result = new List<string> { "phase=exceptions", "filter=" + filter, "finally=" + finallyValue, "wrapped=" + wrapped, "stack.text=" + stack, "stack.frames=" + CountFrames(stack), "method.token=" + token };
            System.Diagnostics.StackFrame[] frames = inner == null ? new System.Diagnostics.StackFrame[0] : new System.Diagnostics.StackTrace(inner, true).GetFrames(); bool sourceAvailable = false;
            if (frames != null) for (int i = 0; i < frames.Length; ++i) { sourceAvailable = sourceAvailable || frames[i].GetFileName() != null; MethodBase frameMethod = frames[i].GetMethod(); bool methodAvailable = frameMethod != null; result.Add("frame." + i + ".methodAvailable=" + methodAvailable); result.Add("frame." + i + ".declaringType=" + (!methodAvailable || frameMethod.DeclaringType == null ? "absent" : frameMethod.DeclaringType.FullName)); result.Add("frame." + i + ".method=" + (methodAvailable ? frameMethod.Name : "absent")); result.Add("frame." + i + ".token=" + (methodAvailable ? frameMethod.MetadataToken : 0)); result.Add("frame." + i + ".file=" + (frames[i].GetFileName() ?? "absent")); result.Add("frame." + i + ".line=" + frames[i].GetFileLineNumber()); result.Add("frame." + i + ".column=" + frames[i].GetFileColumnNumber()); }
            result.Add("source.status=" + (sourceAvailable ? "available" : "absent"));
            return result.ToArray();
        }
        private static bool Filter(Exception error) { return error.Message == Marker; }
        [MethodImpl(MethodImplOptions.NoInlining)] public static void ThrowForEvidence() { ThrowNested(); }
        [MethodImpl(MethodImplOptions.NoInlining)] private static void ThrowNested() { throw new InvalidOperationException(Marker); }
        private static int CountFrames(string stack) { return string.IsNullOrEmpty(stack) ? 0 : stack.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries).Length; }
        private static async Task CancelledAsync(CancellationToken token) { await Task.Delay(1, token); }
        private static async Task ThrowAsync() { await Task.Yield(); throw new InvalidOperationException(Marker + ":async"); }
        private static IEnumerable<int> Iterate(List<string> trace) { try { trace.Add("iterator.begin=true"); yield return Generation; trace.Add("iterator.after=true"); } finally { trace.Add("iterator.finally=true"); } }
        private static T GenericMethod<T>(T value) { return value; }
        private static void RefOps(ref int value, out int output, in DemoValue input) { value += input.number; output = value + 1; }
        private static int InitializeBeforeFieldInit<T>() { ++s_beforeFieldInitCalls; return Generation + typeof(T).Name.Length + s_beforeFieldInitCalls; }
        private static string FormatStatic(int value) { return Marker + ":S" + value; }
        private static T Echo<T>(T value) { return value; }

        private class ExtNode : M06ExecutionBase
        {
            public readonly int Value = Generation + 20; public readonly string Field = Marker + ":field";
            public string Property { get; private set; } = Marker + ":property"; public event Action Changed;
            public override string Dispatch() { return Marker + ":virtual"; }
            public override string BaseDispatch() { return Marker + ":base:" + base.BaseDispatch(); }
            public override string AbstractDispatch() { return Marker + ":abstract"; }
            public override string GetVersionText() { return Marker + ":interface"; }
            public string Format(int value) { return Marker + ":I" + value; }
            public string Raise() { if (Changed != null) Changed(); return Marker + ":event"; }
        }
        private sealed class SealedNode : ExtNode { public override string Dispatch() { return Marker + ":sealed"; } }
        private sealed class Pair<T> { public T Value; }
        private static class GenericState<T> { public static int Count; }
        private static class ExplicitStaticState { public static int Value; static ExplicitStaticState() { ++Value; } }
        private static class BeforeFieldInitState<T> { public static readonly int Value = InitializeBeforeFieldInit<T>(); }
    }
}
