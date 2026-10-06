using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using MCPForUnity.Editor.Services;
using NUnit.Framework;

namespace MCPForUnityTests.Editor.Services
{
    /// <summary>
    /// 验证所有 HTTP 自动连接入口共享同一套启动、清理、连接与健康检查语义。
    /// </summary>
    public sealed class HttpConnectionCoordinatorTests
    {
        #region Tests

        /// <summary>
        /// 验证本地服务器已可达时直接连接桥接且不会重复拉起服务器。
        /// </summary>
        [Test]
        public void ReachableLocalServer_ConnectsWithoutRelaunch()
        {
            var environment = new FakeHttpConnectionEnvironment { IsLocalServerReachable = true };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Connected, outcome);
            Assert.AreEqual(0, environment.StartLocalServerCalls);
            Assert.AreEqual(1, environment.StartBridgeCalls);
            Assert.AreEqual(1, environment.VerifyBridgeCalls);
        }

        /// <summary>
        /// 验证本地服务器消失但 HTTP 传输仍标记运行时，先清理失效传输再重启服务器。
        /// </summary>
        [Test]
        public void StaleHttpTransport_IsStoppedBeforeLocalRestart()
        {
            var environment = new FakeHttpConnectionEnvironment
            {
                IsHttpTransportRunning = true,
                IsLocalServerReachable = false
            };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true).GetAwaiter().GetResult();

            CollectionAssert.AreEqual(new[] { "stop-http", "start-local", "start-bridge", "verify" },
                environment.Events);
            Assert.AreEqual(HttpConnectionOutcome.Connected, outcome);
        }

        /// <summary>
        /// 验证域重载重连只等待并连接现有服务器，绝不启动新进程。
        /// </summary>
        [Test]
        public void ReloadReconnect_NeverStartsLocalServer()
        {
            var environment = new FakeHttpConnectionEnvironment
            {
                IsLocalServerReachable = false,
                StartBridgeResult = false,
                DelayAdvanceSeconds = 301.0
            };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.ReloadReconnect, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Failed, outcome);
            Assert.AreEqual(0, environment.StartLocalServerCalls);
        }

        /// <summary>
        /// 验证持久恢复在服务器启动期间遭遇域重载时，下一域只等待原进程而不会再次启动。
        /// </summary>
        [Test]
        public void PersistentLaunchInterruptedByReload_ResumesWithoutSecondServerLaunch()
        {
            var launchDelay = new TaskCompletionSource<bool>();
            var originalEnvironment = new FakeHttpConnectionEnvironment
            {
                MakeServerReachableOnStart = false,
                StartBridgeResult = false,
                DelayCompletion = launchDelay
            };
            var originalCoordinator = new HttpConnectionCoordinator(originalEnvironment);

            Task<HttpConnectionOutcome> interruptedAttempt = originalCoordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true);

            Assert.IsFalse(interruptedAttempt.IsCompleted);
            Assert.AreEqual(1, originalEnvironment.StartLocalServerCalls);

            var reloadedEnvironment = new FakeHttpConnectionEnvironment
            {
                IsLocalServerReachable = false,
                StartBridgeResult = false,
                DelayAdvanceSeconds = 301.0
            };
            var reloadedCoordinator = new HttpConnectionCoordinator(reloadedEnvironment);
            HttpConnectionIntent resumeIntent = ProjectAutoConnectMonitor.ResolveIntent(
                persistentConnectPending: true,
                autoStartConnectPending: false);

            HttpConnectionOutcome reloadedOutcome = reloadedCoordinator.EnsureConnectedAsync(
                resumeIntent, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionIntent.ReloadReconnect, resumeIntent);
            Assert.AreEqual(HttpConnectionOutcome.Failed, reloadedOutcome);
            Assert.AreEqual(0, reloadedEnvironment.StartLocalServerCalls);

            launchDelay.SetResult(true);
            originalEnvironment.DelayAdvanceSeconds = 301.0;
            Assert.AreEqual(HttpConnectionOutcome.Failed, interruptedAttempt.GetAwaiter().GetResult());
        }

        /// <summary>
        /// 验证并发入口复用一个进行中的连接任务，避免双重启动与会话互相冲掉。
        /// </summary>
        [Test]
        public void OverlappingRequests_ShareOneConnectionAttempt()
        {
            var completion = new TaskCompletionSource<bool>();
            var environment = new FakeHttpConnectionEnvironment
            {
                IsLocalServerReachable = true,
                StartBridgeCompletion = completion
            };
            var coordinator = new HttpConnectionCoordinator(environment);

            Task<HttpConnectionOutcome> first = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true);
            Task<HttpConnectionOutcome> second = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.AutoStart, () => true);

            Assert.AreEqual(1, environment.StartBridgeCalls);
            completion.SetResult(true);
            HttpConnectionOutcome[] outcomes = Task.WhenAll(first, second).GetAwaiter().GetResult();

            CollectionAssert.AreEqual(
                new[] { HttpConnectionOutcome.Connected, HttpConnectionOutcome.Connected }, outcomes);
            Assert.AreEqual(1, environment.StartBridgeCalls);
            Assert.AreEqual(1, environment.VerifyBridgeCalls);
        }

        /// <summary>
        /// 验证持久本地连接在远程 HTTP 配置下跳过，防止误操作外部服务。
        /// </summary>
        [Test]
        public void PersistentLocal_RemoteScope_IsSkipped()
        {
            var environment = new FakeHttpConnectionEnvironment { IsRemoteScope = true };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Skipped, outcome);
            Assert.AreEqual(0, environment.StartBridgeCalls);
            Assert.AreEqual(0, environment.StartLocalServerCalls);
        }

        /// <summary>
        /// 验证 stdio 配置下所有 HTTP 协调请求都跳过。
        /// </summary>
        [Test]
        public void StdioSelected_IsSkipped()
        {
            var environment = new FakeHttpConnectionEnvironment { UseHttpTransport = false };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.AutoStart, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Skipped, outcome);
            Assert.IsEmpty(environment.Events);
        }

        /// <summary>
        /// 验证调用方撤销连接意图后立即中止且不产生外部副作用。
        /// </summary>
        [Test]
        public void CancelledIntent_IsAborted()
        {
            var environment = new FakeHttpConnectionEnvironment { IsLocalServerReachable = true };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => false).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Aborted, outcome);
            Assert.IsEmpty(environment.Events);
        }

        /// <summary>
        /// 验证已运行且健康的连接不会被重复启动。
        /// </summary>
        [Test]
        public void HealthyRunningConnection_IsAlreadyConnected()
        {
            var environment = new FakeHttpConnectionEnvironment
            {
                IsHttpTransportRunning = true,
                IsLocalServerReachable = true
            };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.AlreadyConnected, outcome);
            Assert.AreEqual(0, environment.StartBridgeCalls);
            Assert.AreEqual(1, environment.VerifyBridgeCalls);
        }

        /// <summary>
        /// 验证桥接启动后健康检查失败会返回失败，而不是误报已连接。
        /// </summary>
        [Test]
        public void FailedHealthVerification_DoesNotReportConnected()
        {
            var environment = new FakeHttpConnectionEnvironment
            {
                IsLocalServerReachable = true,
                VerificationResult = new BridgeVerificationResult
                {
                    Success = false,
                    HandshakeValid = false,
                    PingSucceeded = false,
                    Message = "unreachable"
                }
            };
            var coordinator = new HttpConnectionCoordinator(environment);

            HttpConnectionOutcome outcome = coordinator.EnsureConnectedAsync(
                HttpConnectionIntent.PersistentLocal, () => true).GetAwaiter().GetResult();

            Assert.AreEqual(HttpConnectionOutcome.Failed, outcome);
            Assert.AreEqual(1, environment.VerifyBridgeCalls);
        }

        #endregion

        #region Test Doubles

        /// <summary>
        /// 以完整的协调器边界模拟外部服务，并记录真实调用顺序与状态变化。
        /// </summary>
        private sealed class FakeHttpConnectionEnvironment : IHttpConnectionEnvironment
        {
            /// <summary>
            /// 初始化默认成功的健康检查结果，只有失败用例才覆盖它。
            /// </summary>
            internal FakeHttpConnectionEnvironment()
            {
                VerificationResult = new BridgeVerificationResult
                {
                    Success = true,
                    HandshakeValid = true,
                    PingSucceeded = true,
                    Message = "healthy"
                };
            }

            /// <summary>
            /// 获取按发生顺序记录的外部副作用。
            /// </summary>
            internal List<string> Events { get; } = new List<string>();

            /// <summary>
            /// 获取或设置是否使用 HTTP 传输。
            /// </summary>
            public bool UseHttpTransport { get; set; } = true;

            /// <summary>
            /// 获取或设置是否选择远程 HTTP 范围。
            /// </summary>
            public bool IsRemoteScope { get; set; }

            /// <summary>
            /// 获取或设置 HTTP 传输是否正在运行。
            /// </summary>
            public bool IsHttpTransportRunning { get; set; }

            /// <summary>
            /// 获取或设置本地服务器是否可达。
            /// </summary>
            public bool IsLocalServerReachable { get; set; }

            /// <summary>
            /// 获取或设置当前域是否持有受管服务器进程句柄。
            /// </summary>
            public bool HasManagedServerLaunchHandle { get; set; }

            /// <summary>
            /// 获取或设置受管服务器进程是否存活。
            /// </summary>
            public bool IsManagedServerLaunchProcessAlive { get; set; } = true;

            /// <summary>
            /// 获取模拟的编辑器启动时间。
            /// </summary>
            public double TimeSinceStartup { get; private set; }

            /// <summary>
            /// 获取或设置每次轮询等待推进的秒数。
            /// </summary>
            internal double DelayAdvanceSeconds { get; set; } = 0.5;

            /// <summary>
            /// 获取或设置是否在成功派发本地进程后立即模拟服务器可达。
            /// </summary>
            internal bool MakeServerReachableOnStart { get; set; } = true;

            /// <summary>
            /// 获取或设置用于模拟域重载中断点的轮询等待完成源。
            /// </summary>
            internal TaskCompletionSource<bool> DelayCompletion { get; set; }

            /// <summary>
            /// 获取或设置本地启动策略是否允许当前 URL。
            /// </summary>
            internal bool LocalLaunchAllowed { get; set; } = true;

            /// <summary>
            /// 获取或设置本地服务器启动调用的返回值。
            /// </summary>
            internal bool StartLocalServerResult { get; set; } = true;

            /// <summary>
            /// 获取本地服务器启动调用次数。
            /// </summary>
            internal int StartLocalServerCalls { get; private set; }

            /// <summary>
            /// 获取或设置桥接启动调用的立即返回值。
            /// </summary>
            internal bool StartBridgeResult { get; set; } = true;

            /// <summary>
            /// 获取或设置用于控制进行中桥接启动的完成源。
            /// </summary>
            internal TaskCompletionSource<bool> StartBridgeCompletion { get; set; }

            /// <summary>
            /// 获取桥接启动调用次数。
            /// </summary>
            internal int StartBridgeCalls { get; private set; }

            /// <summary>
            /// 获取或设置健康检查结果。
            /// </summary>
            internal BridgeVerificationResult VerificationResult { get; set; }

            /// <summary>
            /// 获取健康检查调用次数。
            /// </summary>
            internal int VerifyBridgeCalls { get; private set; }

            /// <summary>
            /// 获取本地启动失败诊断调用次数。
            /// </summary>
            internal int LogLocalLaunchFailureCalls { get; private set; }

            /// <summary>
            /// 根据测试配置返回本地启动策略结果。
            /// </summary>
            /// <param name="error">策略拒绝时返回诊断原因。</param>
            /// <returns>当前 URL 是否允许由 Unity 启动。</returns>
            public bool IsLocalLaunchAllowed(out string error)
            {
                error = LocalLaunchAllowed ? null : "blocked";
                return LocalLaunchAllowed;
            }

            /// <summary>
            /// 记录本地启动并在成功时把服务器切换为可达状态。
            /// </summary>
            /// <param name="quiet">是否静默启动；测试仅保留真实边界参数。</param>
            /// <returns>配置的启动结果。</returns>
            public bool StartLocalServer(bool quiet)
            {
                StartLocalServerCalls++;
                Events.Add("start-local");
                if (StartLocalServerResult && MakeServerReachableOnStart)
                {
                    IsLocalServerReachable = true;
                }

                return StartLocalServerResult;
            }

            /// <summary>
            /// 清理 HTTP 传输并同步更新测试状态。
            /// </summary>
            /// <returns>已完成任务。</returns>
            public Task StopHttpTransportAsync()
            {
                Events.Add("stop-http");
                IsHttpTransportRunning = false;
                return Task.CompletedTask;
            }

            /// <summary>
            /// 启动桥接并支持保持任务未完成以验证单飞合并。
            /// </summary>
            /// <returns>桥接是否启动成功。</returns>
            public async Task<bool> StartBridgeAsync()
            {
                StartBridgeCalls++;
                Events.Add("start-bridge");
                bool result = StartBridgeCompletion == null
                    ? StartBridgeResult
                    : await StartBridgeCompletion.Task;
                if (result)
                {
                    IsHttpTransportRunning = true;
                }

                return result;
            }

            /// <summary>
            /// 返回配置的桥接健康检查结果并记录调用。
            /// </summary>
            /// <returns>完整的健康检查结果。</returns>
            public Task<BridgeVerificationResult> VerifyBridgeAsync()
            {
                VerifyBridgeCalls++;
                Events.Add("verify");
                return Task.FromResult(VerificationResult);
            }

            /// <summary>
            /// 推进模拟时间而不产生真实等待，使硬超时分支可确定测试。
            /// </summary>
            /// <param name="delay">生产轮询请求的等待时长。</param>
            /// <returns>已完成任务。</returns>
            public Task DelayAsync(TimeSpan delay)
            {
                TimeSinceStartup += DelayAdvanceSeconds;
                return DelayCompletion?.Task ?? Task.CompletedTask;
            }

            /// <summary>
            /// 记录启动失败诊断请求以验证失败路径不会被吞掉。
            /// </summary>
            public void LogLocalLaunchFailure()
            {
                LogLocalLaunchFailureCalls++;
            }
        }

        #endregion
    }
}
