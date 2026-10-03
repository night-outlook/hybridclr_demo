using System;
using System.IO;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01EarlyObserverTests
    {
        [Test]
        public void ObserverStartsEmptyAndExposesBoundedReceiptShape()
        {
            var observer = new R01EarlyObserver();
            Assert.IsFalse(observer.Joined);
            Assert.AreEqual(0, observer.Samples.Length);
            Assert.AreEqual(0, observer.Errors.Length);
            Assert.AreEqual(0, observer.droppedBefore);
            Assert.AreEqual(0, observer.droppedAfter);
        }

        [Test]
        public void InitializerCaptureDelegatesOrdinaryWrites()
        {
            var previous = new StringWriter();
            var capture = new R01EarlyInitializerCapture(previous);
            capture.Write("ordinary output");
            capture.WriteLine(" and a newline");
            Assert.AreEqual("ordinary output and a newline" + Environment.NewLine, previous.ToString());
            Assert.AreEqual(0, capture.Events.Length);
        }

        [Test]
        public void InitializerCaptureRejectsMissingPreviousWriter()
        {
            Assert.Throws<ArgumentNullException>(() => new R01EarlyInitializerCapture(null));
        }

        [Test]
        public void ObserverSourceHasNoUnityServiceOrJsonCalls()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/R01EarlyObserver.cs");
            StringAssert.DoesNotContain("JsonUtility", source);
            StringAssert.DoesNotContain("UnityEngine.Application", source);
            StringAssert.DoesNotContain("UnityEngine.Debug", source);
            StringAssert.Contains("AssemblyShadowRuntime.GetDiagnosticsJson", source);
            StringAssert.Contains("Assembly.Load(\"mscorlib\")", source);
        }
    }
}
