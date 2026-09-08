using System;
using System.Collections;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07BootstrapLifetimeTests
    {
        private delegate void Release(ref IEnumerator work);

        private static Release ReleaseOwnedProbe()
        {
            MethodInfo method = typeof(M07BootstrapRunner).GetMethod("ReleaseProbe", BindingFlags.Static | BindingFlags.NonPublic);
            return (Release)Delegate.CreateDelegate(typeof(Release), method);
        }

        [Test]
        public void OwnerIsDetachedBeforeDisposalAndRepeatedCleanupDoesNotDisposeTwice()
        {
            IEnumerator owner = null;
            var probe = new DisposableProbe(() => Assert.IsNull(owner));
            owner = probe;
            Release release = ReleaseOwnedProbe();
            release(ref owner);
            release(ref owner);
            Assert.IsNull(owner);
            Assert.AreEqual(1, probe.disposeCount);
        }

        [Test]
        public void ThrowingDisposalStillReleasesTheOwnedReference()
        {
            var probe = new DisposableProbe(() => { throw new InvalidOperationException("dispose failure"); });
            IEnumerator owner = probe;
            Release release = ReleaseOwnedProbe();
            Assert.Throws<InvalidOperationException>(() => release(ref owner));
            Assert.IsNull(owner);
            release(ref owner);
            Assert.AreEqual(1, probe.disposeCount);
        }

        private sealed class DisposableProbe : IEnumerator, IDisposable
        {
            private readonly Action onDispose;
            public int disposeCount;
            public DisposableProbe(Action onDispose) { this.onDispose = onDispose; }
            public object Current { get { return null; } }
            public bool MoveNext() { return false; }
            public void Reset() { throw new NotSupportedException(); }
            public void Dispose() { ++disposeCount; onDispose(); }
        }
    }
}
