using System;
using System.Threading.Tasks;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services.Transport;
using MCPForUnity.Editor.Windows;
using UnityEditor;

namespace MCPForUnity.Editor.Services
{
    /// <summary>
    /// 标识 HTTP 连接请求的来源，因为不同入口对本地服务器启动权限不同。
    /// </summary>
    internal enum HttpConnectionIntent
    {
        /// <summary>
        /// 编辑器启动时的一次性自动启动，可连接远程服务并可启动本地服务。
        /// </summary>
        AutoStart,

        /// <summary>
        /// 域重载后的仅重连流程，必须复用已有服务且禁止启动新进程。
        /// </summary>
        ReloadReconnect,

        /// <summary>
        /// 当前工程的持久本地恢复流程，只能操作 HTTP Local。
        /// </summary>
        PersistentLocal
    }

    /// <summary>
    /// 描述一次协调连接请求的终态，供各入口决定是否记录或重试。
    /// </summary>
    internal enum HttpConnectionOutcome
    {
        /// <summary>
        /// 本次请求建立了新的健康连接。
        /// </summary>
        Connected,

        /// <summary>
        /// 连接已存在且健康，因此没有重复启动。
        /// </summary>
        AlreadyConnected,

        /// <summary>
        /// 当前传输或作用域不适用于该请求。
        /// </summary>
        Skipped,

        /// <summary>
        /// 调用方在执行过程中撤销了连接意图。
        /// </summary>
        Aborted,

        /// <summary>
        /// 启动、连接或健康检查未成功。
        /// </summary>
        Failed
    }

    /// <summary>
    /// 抽象协调器所需的外部副作用，使连接策略可在不启动真实服务器的情况下验证。
    /// </summary>
    internal interface IHttpConnectionEnvironment
    {
        /// <summary>
        /// 获取当前是否选择 HTTP 传输。
        /// </summary>
        bool UseHttpTransport { get; }

        /// <summary>
        /// 获取当前 HTTP 配置是否为远程作用域。
        /// </summary>
        bool IsRemoteScope { get; }

        /// <summary>
        /// 获取 HTTP 传输是否已标记为运行。
        /// </summary>
        bool IsHttpTransportRunning { get; }

        /// <summary>
        /// 获取本地 HTTP 服务当前是否可达。
        /// </summary>
        bool IsLocalServerReachable { get; }

        /// <summary>
        /// 获取当前域是否持有受管服务器启动句柄。
        /// </summary>
        bool HasManagedServerLaunchHandle { get; }

        /// <summary>
        /// 获取最近启动的受管服务器进程是否仍存活。
        /// </summary>
        bool IsManagedServerLaunchProcessAlive { get; }

        /// <summary>
        /// 获取 Unity 编辑器启动后的秒数，用于不受系统时钟调整影响的硬超时。
        /// </summary>
        double TimeSinceStartup { get; }

        /// <summary>
        /// 检查当前本地 URL 是否允许由 Unity 启动服务器。
        /// </summary>
        /// <param name="error">策略拒绝时的诊断原因。</param>
        /// <returns>是否允许启动。</returns>
        bool IsLocalLaunchAllowed(out string error);

        /// <summary>
        /// 启动本地 HTTP 服务器。
        /// </summary>
        /// <param name="quiet">是否跳过交互式确认。</param>
        /// <returns>是否成功派发服务器进程。</returns>
        bool StartLocalServer(bool quiet);

        /// <summary>
        /// 停止可能已失效的 HTTP 传输状态。
        /// </summary>
        /// <returns>停止任务。</returns>
        Task StopHttpTransportAsync();

        /// <summary>
        /// 启动当前配置的桥接连接。
        /// </summary>
        /// <returns>桥接是否启动成功。</returns>
        Task<bool> StartBridgeAsync();

        /// <summary>
        /// 对已运行的桥接执行健康检查。
        /// </summary>
        /// <returns>完整健康检查结果。</returns>
        Task<BridgeVerificationResult> VerifyBridgeAsync();

        /// <summary>
        /// 等待下一次服务器可达性轮询。
        /// </summary>
        /// <param name="delay">等待时长。</param>
        /// <returns>等待任务。</returns>
        Task DelayAsync(TimeSpan delay);

        /// <summary>
        /// 输出本地服务器启动失败的现有诊断信息。
        /// </summary>
        void LogLocalLaunchFailure();
    }

    /// <summary>
    /// 统一所有 HTTP 自动连接入口，并通过单飞任务避免并发启动互相终止会话。
    /// </summary>
    internal sealed class HttpConnectionCoordinator
    {
        #region Constants

        /// <summary>
        /// 本地服务器探测间隔，兼顾启动响应与编辑器负载。
        /// </summary>
        private static readonly TimeSpan POLL_DELAY = TimeSpan.FromMilliseconds(500);

        /// <summary>
        /// 本地启动与域重载重连的统一硬上限，防止后台任务无限等待。
        /// </summary>
        private static readonly TimeSpan HARD_CAP = TimeSpan.FromMinutes(5);

        #endregion

        #region Fields

        /// <summary>
        /// 生产入口共享的协调器实例。
        /// </summary>
        private static readonly HttpConnectionCoordinator SHARED =
            new HttpConnectionCoordinator(new UnityHttpConnectionEnvironment());

        /// <summary>
        /// 保护进行中任务引用，避免不同编辑器回调并发创建连接流程。
        /// </summary>
        private readonly object _attemptGate = new object();

        /// <summary>
        /// 封装真实 Unity 服务或测试替身。
        /// </summary>
        private readonly IHttpConnectionEnvironment _environment;

        /// <summary>
        /// 当前进行中的共享连接任务。
        /// </summary>
        private Task<HttpConnectionOutcome> _activeAttempt;

        #endregion

        #region Properties

        /// <summary>
        /// 获取生产入口使用的共享协调器。
        /// </summary>
        internal static HttpConnectionCoordinator Shared => SHARED;

        #endregion

        #region Lifecycle

        /// <summary>
        /// 创建使用指定外部环境的协调器，以便生产与测试共用同一策略实现。
        /// </summary>
        /// <param name="environment">提供传输、服务器、时间与健康检查副作用的环境。</param>
        internal HttpConnectionCoordinator(IHttpConnectionEnvironment environment)
        {
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
        }

        #endregion

        #region Public API

        /// <summary>
        /// 确保符合意图约束的 HTTP 连接处于健康状态；重叠调用共享同一进行中任务。
        /// </summary>
        /// <param name="intent">连接来源以及其允许的服务器生命周期范围。</param>
        /// <param name="shouldContinue">每个异步阶段前检查的调用方意图。</param>
        /// <returns>连接流程的终态。</returns>
        internal Task<HttpConnectionOutcome> EnsureConnectedAsync(
            HttpConnectionIntent intent,
            Func<bool> shouldContinue)
        {
            if (shouldContinue == null)
            {
                throw new ArgumentNullException(nameof(shouldContinue));
            }

            lock (_attemptGate)
            {
                if (_activeAttempt != null && !_activeAttempt.IsCompleted)
                {
                    return _activeAttempt;
                }

                Task<HttpConnectionOutcome> attempt = EnsureConnectedCoreAsync(intent, shouldContinue);
                _activeAttempt = attempt;
                _ = attempt.ContinueWith(
                    _ => ClearCompletedAttempt(attempt),
                    TaskScheduler.Default);
                return attempt;
            }
        }

        #endregion

        #region Connection Flow

        /// <summary>
        /// 执行传输与作用域前置判断，并把请求路由到本地或远程连接流程。
        /// </summary>
        /// <param name="intent">连接来源。</param>
        /// <param name="shouldContinue">调用方是否仍需要连接。</param>
        /// <returns>连接流程终态。</returns>
        private async Task<HttpConnectionOutcome> EnsureConnectedCoreAsync(
            HttpConnectionIntent intent,
            Func<bool> shouldContinue)
        {
            try
            {
                if (!_environment.UseHttpTransport)
                {
                    return HttpConnectionOutcome.Skipped;
                }

                bool isRemote = _environment.IsRemoteScope;
                if (intent == HttpConnectionIntent.PersistentLocal && isRemote)
                {
                    return HttpConnectionOutcome.Skipped;
                }

                if (!shouldContinue())
                {
                    return HttpConnectionOutcome.Aborted;
                }

                return isRemote
                    ? await EnsureRemoteConnectedAsync(shouldContinue)
                    : await EnsureLocalConnectedAsync(intent, shouldContinue);
            }
            catch (Exception ex)
            {
                McpLog.Debug(
                    $"[HTTP Connection] 自动连接执行异常：{ex.Message}\n" +
                    $"[HTTP Connection] Automatic connection failed: {ex.Message}");
                return HttpConnectionOutcome.Failed;
            }
        }

        /// <summary>
        /// 连接外部管理的远程 HTTP 服务，绝不触碰本地服务器进程。
        /// </summary>
        /// <param name="shouldContinue">调用方是否仍需要连接。</param>
        /// <returns>远程连接终态。</returns>
        private async Task<HttpConnectionOutcome> EnsureRemoteConnectedAsync(Func<bool> shouldContinue)
        {
            if (!shouldContinue())
            {
                return HttpConnectionOutcome.Aborted;
            }

            if (_environment.IsHttpTransportRunning)
            {
                return await VerifyExistingConnectionAsync();
            }

            return await ConnectAndVerifyAsync();
        }

        /// <summary>
        /// 恢复本地 HTTP 连接，并在允许的意图下启动缺失的本地服务器。
        /// </summary>
        /// <param name="intent">决定是否允许启动服务器的连接来源。</param>
        /// <param name="shouldContinue">调用方是否仍需要连接。</param>
        /// <returns>本地连接终态。</returns>
        private async Task<HttpConnectionOutcome> EnsureLocalConnectedAsync(
            HttpConnectionIntent intent,
            Func<bool> shouldContinue)
        {
            bool serverReachable = _environment.IsLocalServerReachable;
            if (_environment.IsHttpTransportRunning)
            {
                if (serverReachable)
                {
                    HttpConnectionOutcome existing = await VerifyExistingConnectionAsync();
                    if (existing == HttpConnectionOutcome.AlreadyConnected)
                    {
                        return existing;
                    }
                }

                // 因为服务器消失或健康检查失败时传输状态已失真，所以重启前必须先清理旧连接。
                await _environment.StopHttpTransportAsync();
                if (!shouldContinue())
                {
                    return HttpConnectionOutcome.Aborted;
                }
            }

            if (serverReachable)
            {
                return await ConnectAndVerifyAsync();
            }

            if (intent != HttpConnectionIntent.ReloadReconnect)
            {
                if (!_environment.IsLocalLaunchAllowed(out string policyError))
                {
                    McpLog.Debug(
                        $"[HTTP Connection] 本地启动策略拒绝当前地址：{policyError}\n" +
                        $"[HTTP Connection] Local launch policy rejected the current URL: {policyError}");
                    return HttpConnectionOutcome.Failed;
                }

                if (!_environment.StartLocalServer(quiet: true))
                {
                    return HttpConnectionOutcome.Failed;
                }
            }

            return await WaitForLocalServerAndConnectAsync(intent, shouldContinue);
        }

        /// <summary>
        /// 等待本地服务器可达，并在进程退出或五分钟硬上限后执行最后一次连接诊断。
        /// </summary>
        /// <param name="intent">用于持续验证远程切换约束的连接来源。</param>
        /// <param name="shouldContinue">调用方是否仍需要连接。</param>
        /// <returns>等待与连接终态。</returns>
        private async Task<HttpConnectionOutcome> WaitForLocalServerAndConnectAsync(
            HttpConnectionIntent intent,
            Func<bool> shouldContinue)
        {
            double startTime = _environment.TimeSinceStartup;

            while (true)
            {
                if (!shouldContinue())
                {
                    return HttpConnectionOutcome.Aborted;
                }

                if (!_environment.UseHttpTransport)
                {
                    return HttpConnectionOutcome.Aborted;
                }

                if (intent == HttpConnectionIntent.PersistentLocal && _environment.IsRemoteScope)
                {
                    return HttpConnectionOutcome.Aborted;
                }

                if (_environment.IsLocalServerReachable)
                {
                    if (_environment.IsHttpTransportRunning)
                    {
                        return await VerifyExistingConnectionAsync();
                    }

                    return await ConnectAndVerifyAsync();
                }

                double elapsed = _environment.TimeSinceStartup - startTime;
                bool launchProcessDied = _environment.HasManagedServerLaunchHandle
                    && !_environment.IsManagedServerLaunchProcessAlive
                    && elapsed > 1.0;
                if (launchProcessDied || elapsed > HARD_CAP.TotalSeconds)
                {
                    HttpConnectionOutcome finalAttempt = await ConnectAndVerifyAsync();
                    if (finalAttempt == HttpConnectionOutcome.Connected)
                    {
                        return finalAttempt;
                    }

                    _environment.LogLocalLaunchFailure();
                    return HttpConnectionOutcome.Failed;
                }

                await _environment.DelayAsync(POLL_DELAY);
            }
        }

        /// <summary>
        /// 验证现有传输是否真正健康，防止仅凭运行标记误判连接状态。
        /// </summary>
        /// <returns>健康时返回已连接，否则返回失败。</returns>
        private async Task<HttpConnectionOutcome> VerifyExistingConnectionAsync()
        {
            BridgeVerificationResult result = await _environment.VerifyBridgeAsync();
            return IsHealthy(result)
                ? HttpConnectionOutcome.AlreadyConnected
                : HttpConnectionOutcome.Failed;
        }

        /// <summary>
        /// 启动桥接并立即执行健康检查，只有完整握手与 ping 成功才视为已连接。
        /// </summary>
        /// <returns>新连接的终态。</returns>
        private async Task<HttpConnectionOutcome> ConnectAndVerifyAsync()
        {
            if (!await _environment.StartBridgeAsync())
            {
                return HttpConnectionOutcome.Failed;
            }

            BridgeVerificationResult result = await _environment.VerifyBridgeAsync();
            if (IsHealthy(result))
            {
                return HttpConnectionOutcome.Connected;
            }

            await _environment.StopHttpTransportAsync();
            return HttpConnectionOutcome.Failed;
        }

        /// <summary>
        /// 统一健康判定，确保握手存在但 ping 失败时不会误报成功。
        /// </summary>
        /// <param name="result">桥接健康检查结果。</param>
        /// <returns>是否满足完整健康条件。</returns>
        private static bool IsHealthy(BridgeVerificationResult result)
            => result != null && result.Success && result.PingSucceeded;

        #endregion

        #region Single Flight

        /// <summary>
        /// 仅在引用仍指向已完成任务时清理单飞状态，避免旧 continuation 清除新任务。
        /// </summary>
        /// <param name="completedAttempt">刚完成的连接任务。</param>
        private void ClearCompletedAttempt(Task<HttpConnectionOutcome> completedAttempt)
        {
            lock (_attemptGate)
            {
                if (ReferenceEquals(_activeAttempt, completedAttempt))
                {
                    _activeAttempt = null;
                }
            }
        }

        #endregion

        #region Unity Environment

        /// <summary>
        /// 把协调器边界映射到当前 Unity 编辑器服务。
        /// </summary>
        private sealed class UnityHttpConnectionEnvironment : IHttpConnectionEnvironment
        {
            /// <summary>
            /// 获取当前缓存的传输选择。
            /// </summary>
            public bool UseHttpTransport => EditorConfigurationCache.Instance.UseHttpTransport;

            /// <summary>
            /// 获取当前 HTTP 作用域。
            /// </summary>
            public bool IsRemoteScope => HttpEndpointUtility.IsRemoteScope();

            /// <summary>
            /// 获取 HTTP 传输运行状态。
            /// </summary>
            public bool IsHttpTransportRunning =>
                MCPServiceLocator.TransportManager.IsRunning(TransportMode.Http);

            /// <summary>
            /// 获取本地 HTTP 服务可达状态。
            /// </summary>
            public bool IsLocalServerReachable => MCPServiceLocator.Server.IsLocalHttpServerReachable();

            /// <summary>
            /// 获取当前域是否持有服务器启动句柄。
            /// </summary>
            public bool HasManagedServerLaunchHandle => MCPServiceLocator.Server.HasManagedServerLaunchHandle;

            /// <summary>
            /// 获取最近启动的服务器进程是否存活。
            /// </summary>
            public bool IsManagedServerLaunchProcessAlive =>
                MCPServiceLocator.Server.IsManagedServerLaunchProcessAlive();

            /// <summary>
            /// 获取 Unity 编辑器单调启动时间。
            /// </summary>
            public double TimeSinceStartup => EditorApplication.timeSinceStartup;

            /// <summary>
            /// 委托现有安全策略检查本地启动 URL。
            /// </summary>
            /// <param name="error">策略拒绝原因。</param>
            /// <returns>是否允许启动。</returns>
            public bool IsLocalLaunchAllowed(out string error)
                => HttpEndpointUtility.IsHttpLocalUrlAllowedForLaunch(
                    HttpEndpointUtility.GetLocalBaseUrl(), out error);

            /// <summary>
            /// 通过现有服务器服务启动本地进程。
            /// </summary>
            /// <param name="quiet">是否跳过交互式确认。</param>
            /// <returns>是否成功派发。</returns>
            public bool StartLocalServer(bool quiet)
                => MCPServiceLocator.Server.StartLocalHttpServer(quiet);

            /// <summary>
            /// 精确停止 HTTP 传输而不影响 stdio。
            /// </summary>
            /// <returns>停止任务。</returns>
            public Task StopHttpTransportAsync()
                => MCPServiceLocator.TransportManager.StopAsync(TransportMode.Http);

            /// <summary>
            /// 通过桥接服务启动当前 HTTP 连接。
            /// </summary>
            /// <returns>是否启动成功。</returns>
            public Task<bool> StartBridgeAsync() => MCPServiceLocator.Bridge.StartAsync();

            /// <summary>
            /// 执行真实桥接验证，并请求编辑器窗口刷新健康状态。
            /// </summary>
            /// <returns>桥接健康检查结果。</returns>
            public async Task<BridgeVerificationResult> VerifyBridgeAsync()
            {
                BridgeVerificationResult result = await MCPServiceLocator.Bridge.VerifyAsync();
                if (IsHealthy(result))
                {
                    MCPForUnityEditorWindow.RequestHealthVerification();
                }

                return result;
            }

            /// <summary>
            /// 使用异步延迟让出编辑器主线程。
            /// </summary>
            /// <param name="delay">等待时长。</param>
            /// <returns>等待任务。</returns>
            public Task DelayAsync(TimeSpan delay) => Task.Delay(delay);

            /// <summary>
            /// 复用服务器服务的启动日志尾部诊断。
            /// </summary>
            public void LogLocalLaunchFailure() => MCPServiceLocator.Server.LogLocalHttpServerLaunchFailure();
        }

        #endregion
    }
}
