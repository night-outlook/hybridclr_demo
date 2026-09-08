using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using HybridCLR;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// Bounded raw diagnostics observer for the R01 early transaction. The
    /// worker keeps querying after the sixteen-sample retention limit so the
    /// dropped counters describe the complete observation interval.
    /// </summary>
    [Preserve]
    public sealed class R01EarlyObserver
    {
        private const int RetainedPerPhase = 16;
        private const int WaitMilliseconds = 10000;
        private readonly object sync = new object();
        private readonly List<Sample> samples = new List<Sample>(RetainedPerPhase * 2);
        private readonly List<string> errors = new List<string>();
        private Thread thread;
        private volatile bool stop;
        private volatile bool after;
        private int beforeCount;
        private int afterCount;
        private int droppedBeforeCount;
        private int droppedAfterCount;
        private bool joined;

        public bool Joined { get { lock (sync) return joined; } }
        public Sample[] Samples { get { lock (sync) return samples.ToArray(); } }
        public string[] Errors { get { lock (sync) return errors.ToArray(); } }
        public int droppedBefore { get { return Volatile.Read(ref droppedBeforeCount); } }
        public int droppedAfter { get { return Volatile.Read(ref droppedAfterCount); } }

        public void StartAndWaitBefore()
        {
            lock (sync)
            {
                Require(thread == null, "R01 observer was already started.");
                thread = new Thread(Run) { IsBackground = true, Name = "R01-early-observer" };
                thread.Start();
            }
            WaitForPhase(false);
        }

        public void MarkAfterAndWait()
        {
            lock (sync) Require(thread != null, "R01 observer was not started.");
            after = true;
            WaitForPhase(true);
        }

        public void Stop()
        {
            Thread current;
            lock (sync) current = thread;
            if (current == null)
            {
                AddError("R01 observer was never started.");
                return;
            }
            stop = true;
            bool didJoin = current.Join(WaitMilliseconds);
            lock (sync) joined = didJoin;
            if (!didJoin) AddError("R01 observer did not join within 10 seconds.");
        }

        private void Run()
        {
            try
            {
                while (!stop)
                {
                    bool currentAfter = after;
                    Sample sample = Capture(currentAfter ? "after" : "before");
                    Record(sample, currentAfter);
                    Thread.Yield();
                }
            }
            catch (Exception error)
            {
                AddError(error.ToString());
            }
        }

        private void WaitForPhase(bool wantAfter)
        {
            Stopwatch timer = Stopwatch.StartNew();
            while (timer.ElapsedMilliseconds < WaitMilliseconds)
            {
                if (Errors.Length != 0)
                    throw new InvalidOperationException("R01 observer failed: " + Errors[0]);
                if ((wantAfter ? Volatile.Read(ref afterCount) : Volatile.Read(ref beforeCount)) != 0)
                    return;
                Thread.Yield();
            }
            string message = wantAfter ? "after" : "before";
            AddError("R01 observer captured no " + message + " sample within 10 seconds.");
            throw new TimeoutException(Errors[Errors.Length - 1]);
        }

        private Sample Capture(string phase)
        {
            Assembly ordinary = Assembly.Load("mscorlib");
            Require(ordinary != null && ordinary.GetName().Name == "mscorlib", "Stable ordinary mscorlib load changed identity.");
            string rawJson;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out rawJson);
            Sample sample = new Sample {
                phase = phase, rawJson = rawJson, code = (int)code,
                threadId = Thread.CurrentThread.ManagedThreadId, ticks = Stopwatch.GetTimestamp()
            };
            if (code != AssemblyShadowErrorCode.Success)
                AddError("R01 diagnostics query returned " + code + ".");
            return sample;
        }

        private void Record(Sample sample, bool currentAfter)
        {
            lock (sync)
            {
                if (currentAfter)
                {
                    int count = ++afterCount;
                    if (count <= RetainedPerPhase) samples.Add(sample); else ++droppedAfterCount;
                }
                else
                {
                    int count = ++beforeCount;
                    if (count <= RetainedPerPhase) samples.Add(sample); else ++droppedBeforeCount;
                }
            }
        }

        internal static Sample CaptureInitializerDiagnostics()
        {
            string rawJson;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out rawJson);
            return new Sample {
                phase = "initializer", rawJson = rawJson, code = (int)code,
                threadId = Thread.CurrentThread.ManagedThreadId, ticks = Stopwatch.GetTimestamp()
            };
        }

        private void AddError(string error)
        {
            lock (sync)
            {
                if (errors.Count < 64) errors.Add(error ?? "R01 observer error.");
            }
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        [Serializable, Preserve]
        public sealed class Sample
        {
            [Preserve] public string phase, rawJson;
            [Preserve] public int code, threadId;
            [Preserve] public long ticks;
        }
    }

    /// <summary>
    /// Console writer used around the production module initializer failure.
    /// It forwards every write and captures only exact M03-INIT lines.
    /// </summary>
    [Preserve]
    public sealed class R01EarlyInitializerCapture : TextWriter
    {
        private const string Prefix = "M03-INIT:";
        private readonly TextWriter previous;
        private readonly object sync = new object();
        private readonly StringBuilder pending = new StringBuilder();
        private readonly List<Event> events = new List<Event>();

        public R01EarlyInitializerCapture(TextWriter previousWriter)
        {
            if (previousWriter == null) throw new ArgumentNullException("previousWriter");
            previous = previousWriter;
        }

        public override Encoding Encoding { get { return Encoding.UTF8; } }
        public Event[] Events { get { lock (sync) return events.ToArray(); } }

        public override void Write(char value)
        {
            string[] completed;
            lock (sync)
            {
                previous.Write(value);
                pending.Append(value);
                completed = TakeCompletedLines();
            }
            CaptureCompleted(completed);
        }

        public override void Write(string value)
        {
            if (value == null) return;
            foreach (char valueChar in value) Write(valueChar);
        }

        public override void Write(char[] buffer, int index, int count)
        {
            if (buffer == null) throw new ArgumentNullException("buffer");
            if (index < 0 || count < 0 || index > buffer.Length - count) throw new ArgumentOutOfRangeException();
            for (int i = 0; i < count; ++i) Write(buffer[index + i]);
        }

        private string[] TakeCompletedLines()
        {
            var lines = new List<string>();
            int newline;
            while ((newline = IndexOfNewline()) >= 0)
            {
                string line = pending.ToString(0, newline);
                pending.Remove(0, newline + 1);
                if (line.EndsWith("\r", StringComparison.Ordinal)) line = line.Substring(0, line.Length - 1);
                lines.Add(line);
            }
            return lines.ToArray();
        }

        private int IndexOfNewline()
        {
            for (int i = 0; i < pending.Length; ++i)
                if (pending[i] == '\n') return i;
            return -1;
        }

        private void CaptureCompleted(string[] lines)
        {
            foreach (string line in lines)
            {
                if (!line.StartsWith(Prefix, StringComparison.Ordinal)) continue;
                R01EarlyObserver.Sample diagnostics = R01EarlyObserver.CaptureInitializerDiagnostics();
                lock (sync) events.Add(new Event { name = line.Substring(Prefix.Length), diagnostics = diagnostics });
            }
        }

        [Serializable, Preserve]
        public sealed class Event
        {
            [Preserve] public string name;
            [Preserve] public R01EarlyObserver.Sample diagnostics;
        }
    }
}
