using System.Threading.Tasks;
using MCPForUnity.Editor.Constants;
using MCPForUnity.Editor.Services;
using MCPForUnity.Editor.Services.Transport;
using NUnit.Framework;
using UnityEditor;

namespace MCPForUnityTests.Editor.Services
{
    /// <summary>
    /// 验证稳定版自动启动状态机不会在编辑器繁忙或域重载期间提前消费会话状态。
    /// </summary>
    public sealed class HttpAutoStartHandlerTests
    {
        #region Fields

        /// <summary>
        /// 提供同步完成的传输实现，以便测试已连接分支而不访问真实服务器。
        /// </summary>
        private FakeTransportClient _fakeClient;

        /// <summary>
        /// 保存测试前的传输管理器，避免测试污染编辑器服务定位器。
        /// </summary>
        private TransportManager _savedManager;

        /// <summary>
        /// 保存测试前的自动启动会话锁存状态。
        /// </summary>
        private bool _savedLatch;

        /// <summary>
        /// 保存测试前的重载连接待处理状态。
        /// </summary>
        private bool _savedConnectPending;

        /// <summary>
        /// 保存测试前的 HTTP 重载恢复状态。
        /// </summary>
        private bool _savedResumeFlag;

        /// <summary>
        /// 保存测试前的自动启动配置。
        /// </summary>
        private bool _savedAutoStart;

        /// <summary>
        /// 保存测试前的传输选择。
        /// </summary>
        private bool _savedUseHttpTransport;

        /// <summary>
        /// 保存当前工程的持久自动连接配置，避免监视器在测试替换服务期间并发运行。
        /// </summary>
        private bool _savedProjectAutoConnect;

        #endregion

        #region Lifecycle

        /// <summary>
        /// 隔离会话状态、编辑器配置与传输服务，使每个用例从确定状态开始。
        /// </summary>
        [SetUp]
        public void SetUp()
        {
            _savedLatch = SessionState.GetBool(HttpAutoStartHandler.SessionInitKey, false);
            _savedConnectPending = SessionState.GetBool(HttpAutoStartHandler.ConnectPendingKey, false);
            _savedResumeFlag = SessionState.GetBool(HttpBridgeReloadHandler.ResumeSessionKey, false);
            _savedAutoStart = EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false);
            _savedUseHttpTransport = EditorPrefs.GetBool(EditorPrefKeys.UseHttpTransport, true);
            _savedProjectAutoConnect = ProjectAutoConnectSettings.IsEnabled;
            _savedManager = MCPServiceLocator.TransportManager;

            SessionState.EraseBool(HttpAutoStartHandler.SessionInitKey);
            SessionState.EraseBool(HttpAutoStartHandler.ConnectPendingKey);
            SessionState.EraseBool(HttpBridgeReloadHandler.ResumeSessionKey);
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, false);
            EditorPrefs.SetBool(EditorPrefKeys.UseHttpTransport, true);
            ProjectAutoConnectSettings.IsEnabled = false;
            EditorConfigurationCache.Instance.Refresh();

            _fakeClient = new FakeTransportClient();
            var manager = new TransportManager();
            manager.Configure(() => _fakeClient, () => _fakeClient);
            MCPServiceLocator.Register(manager);
        }

        /// <summary>
        /// 恢复所有全局状态，避免用例改变真实编辑器会话行为。
        /// </summary>
        [TearDown]
        public void TearDown()
        {
            SessionState.SetBool(HttpAutoStartHandler.SessionInitKey, _savedLatch);
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, _savedConnectPending);
            SessionState.SetBool(HttpBridgeReloadHandler.ResumeSessionKey, _savedResumeFlag);
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, _savedAutoStart);
            EditorPrefs.SetBool(EditorPrefKeys.UseHttpTransport, _savedUseHttpTransport);
            ProjectAutoConnectSettings.IsEnabled = _savedProjectAutoConnect;
            EditorConfigurationCache.Instance.Refresh();
            MCPServiceLocator.Register(_savedManager);
        }

        #endregion

        #region Tests

        /// <summary>
        /// 验证编辑器繁忙时状态机保留后续重试机会且不写入会话锁存。
        /// </summary>
        [Test]
        public void TickCore_EditorBusy_Defers()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.DeferBusy,
                HttpAutoStartHandler.TickCore(editorBusy: true));
            Assert.IsFalse(IsLatchSet);
        }

        /// <summary>
        /// 验证已有重载恢复任务时自动启动让出连接所有权。
        /// </summary>
        [Test]
        public void TickCore_ResumePending_YieldsToReloadHandler()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);
            SessionState.SetBool(HttpBridgeReloadHandler.ResumeSessionKey, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.DeferToResume,
                HttpAutoStartHandler.TickCore(editorBusy: false));
            Assert.IsFalse(IsLatchSet);
        }

        /// <summary>
        /// 验证没有自动启动工作时不会被无关的恢复标记永久阻塞。
        /// </summary>
        [Test]
        public void TickCore_ResumePendingButNothingToDo_SkipsWithoutWaiting()
        {
            SessionState.SetBool(HttpBridgeReloadHandler.ResumeSessionKey, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.Skip,
                HttpAutoStartHandler.TickCore(editorBusy: false));
        }

        /// <summary>
        /// 验证关闭自动启动时跳过且不提前锁存本次编辑器会话。
        /// </summary>
        [Test]
        public void TickCore_AutoStartDisabled_SkipsWithoutLatch()
        {
            Assert.AreEqual(HttpAutoStartHandler.TickDecision.Skip,
                HttpAutoStartHandler.TickCore(editorBusy: false));
            Assert.IsFalse(IsLatchSet);
        }

        /// <summary>
        /// 验证启用自动启动时只返回启动决策，由调用者在成功派发后写入锁存。
        /// </summary>
        [Test]
        public void TickCore_AutoStartEnabled_ShouldStartWithoutWritingLatch()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.ShouldStart,
                HttpAutoStartHandler.TickCore(editorBusy: false));
            Assert.IsFalse(IsLatchSet);
        }

        /// <summary>
        /// 验证已完成自动启动的会话不会重复派发。
        /// </summary>
        [Test]
        public void TickCore_Latched_Skips()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);
            SessionState.SetBool(HttpAutoStartHandler.SessionInitKey, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.Skip,
                HttpAutoStartHandler.TickCore(editorBusy: false));
        }

        /// <summary>
        /// 验证域重载中断连接后进入仅重连分支而不是再次启动服务器。
        /// </summary>
        [Test]
        public void TickCore_LatchedWithConnectPending_Reconnects()
        {
            SessionState.SetBool(HttpAutoStartHandler.SessionInitKey, true);
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.ShouldReconnect,
                HttpAutoStartHandler.TickCore(editorBusy: false));
        }

        /// <summary>
        /// 验证重载恢复任务优先于被中断的自动启动连接。
        /// </summary>
        [Test]
        public void TickCore_ResumePendingBeatsReconnect()
        {
            SessionState.SetBool(HttpAutoStartHandler.SessionInitKey, true);
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, true);
            SessionState.SetBool(HttpBridgeReloadHandler.ResumeSessionKey, true);

            Assert.AreEqual(HttpAutoStartHandler.TickDecision.DeferToResume,
                HttpAutoStartHandler.TickCore(editorBusy: false));
        }

        /// <summary>
        /// 验证用户关闭自动启动后会消费旧的待重连标记。
        /// </summary>
        [Test]
        public void TryBeginReconnect_AutoStartDisabled_DropsPendingReconnect()
        {
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, true);

            Assert.IsTrue(HttpAutoStartHandler.TryBeginReconnect());
            Assert.IsFalse(IsConnectPendingSet);
        }

        /// <summary>
        /// 验证切换到 stdio 后不会恢复 HTTP 自动启动任务。
        /// </summary>
        [Test]
        public void TryBeginReconnect_StdioSelected_DropsPendingReconnect()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);
            EditorPrefs.SetBool(EditorPrefKeys.UseHttpTransport, false);
            EditorConfigurationCache.Instance.Refresh();
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, true);

            Assert.IsTrue(HttpAutoStartHandler.TryBeginReconnect());
            Assert.IsFalse(IsConnectPendingSet);
        }

        /// <summary>
        /// 验证已经运行的桥接不会因待重连标记被重复启动。
        /// </summary>
        [Test]
        public void TryBeginReconnect_BridgeAlreadyRunning_DropsPendingReconnect()
        {
            EditorPrefs.SetBool(EditorPrefKeys.AutoStartOnLoad, true);
            Task<bool> start = MCPServiceLocator.TransportManager.StartAsync(TransportMode.Http);
            Assert.IsTrue(start.IsCompleted && start.Result);
            SessionState.SetBool(HttpAutoStartHandler.ConnectPendingKey, true);

            Assert.IsTrue(HttpAutoStartHandler.TryBeginReconnect());
            Assert.IsFalse(IsConnectPendingSet);
            Assert.AreEqual(1, _fakeClient.StartCalls);
        }

        #endregion

        #region Helpers

        /// <summary>
        /// 获取当前自动启动会话锁存状态。
        /// </summary>
        private static bool IsLatchSet => SessionState.GetBool(HttpAutoStartHandler.SessionInitKey, false);

        /// <summary>
        /// 获取当前重载连接待处理状态。
        /// </summary>
        private static bool IsConnectPendingSet => SessionState.GetBool(HttpAutoStartHandler.ConnectPendingKey, false);

        /// <summary>
        /// 提供无外部副作用的传输客户端，用于验证传输管理器的真实状态变化。
        /// </summary>
        private sealed class FakeTransportClient : IMcpTransportClient
        {
            /// <summary>
            /// 获取启动调用次数，用于防止重复连接回归。
            /// </summary>
            internal int StartCalls { get; private set; }

            /// <summary>
            /// 获取测试传输是否已连接。
            /// </summary>
            public bool IsConnected { get; private set; }

            /// <summary>
            /// 获取稳定的测试传输名称。
            /// </summary>
            public string TransportName => "fake-http";

            /// <summary>
            /// 获取与当前连接状态一致的传输快照。
            /// </summary>
            public TransportState State => IsConnected
                ? TransportState.Connected(TransportName)
                : TransportState.Disconnected(TransportName);

            /// <summary>
            /// 同步完成启动，以便测试调用次数与状态更新。
            /// </summary>
            /// <returns>始终返回成功。</returns>
            public Task<bool> StartAsync()
            {
                StartCalls++;
                IsConnected = true;
                return Task.FromResult(true);
            }

            /// <summary>
            /// 同步完成停止并清理连接状态。
            /// </summary>
            /// <returns>已完成任务。</returns>
            public Task StopAsync()
            {
                IsConnected = false;
                return Task.CompletedTask;
            }

            /// <summary>
            /// 返回当前真实测试连接状态。
            /// </summary>
            /// <returns>当前是否连接。</returns>
            public Task<bool> VerifyAsync() => Task.FromResult(IsConnected);

            /// <summary>
            /// 测试传输没有工具重注册副作用，因此直接完成。
            /// </summary>
            /// <returns>已完成任务。</returns>
            public Task ReregisterToolsAsync() => Task.CompletedTask;
        }

        #endregion
    }
}
