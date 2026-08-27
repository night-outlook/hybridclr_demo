using System;
using System.Threading.Tasks;
using MCPForUnity.Editor.Helpers;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Services
{
    /// <summary>
    /// 描述持久自动连接监视器在当前编辑器状态下的纯决策。
    /// </summary>
    internal enum ProjectAutoConnectDecision
    {
        /// <summary>
        /// 当前工程关闭了持久自动连接。
        /// </summary>
        Disabled,

        /// <summary>
        /// 编辑器处于批处理、编译或资源更新阶段。
        /// </summary>
        Busy,

        /// <summary>
        /// 当前选择 stdio，不能操作 HTTP 本地服务。
        /// </summary>
        UnsupportedTransport,

        /// <summary>
        /// 当前选择远程 HTTP，不能由本工程管理服务器。
        /// </summary>
        RemoteScope,

        /// <summary>
        /// 当前状态允许执行一次持久本地连接检查。
        /// </summary>
        ShouldConnect
    }

    /// <summary>
    /// 每三秒检查当前工程的本地 HTTP 连接，并在失败时限制重复警告频率。
    /// </summary>
    [InitializeOnLoad]
    internal static class ProjectAutoConnectMonitor
    {
        #region Constants

        /// <summary>
        /// 跨域保留持久连接正在启动或等待本地服务的状态，避免重载后重复拉起服务器。
        /// </summary>
        internal const string ConnectPendingKey = "ProjectAutoConnectMonitor.ConnectPending";

        /// <summary>
        /// 持久连接轮询间隔，避免每帧进行端口探测。
        /// </summary>
        private const double POLL_INTERVAL_SECONDS = 3.0;

        /// <summary>
        /// 重复失败警告的最小间隔，避免服务器不可用时刷屏。
        /// </summary>
        private const double FAILURE_LOG_COOLDOWN_SECONDS = 30.0;

        #endregion

        #region Fields

        /// <summary>
        /// 下一次允许轮询的编辑器启动时间。
        /// </summary>
        private static double _nextCheckTime;

        /// <summary>
        /// 上一次失败警告的编辑器启动时间。
        /// </summary>
        private static double _lastFailureLogTime = double.NegativeInfinity;

        /// <summary>
        /// 防止多个更新或延迟回调重复等待同一个协调器任务。
        /// </summary>
        private static bool _checkInProgress;

        #endregion

        #region Lifecycle

        /// <summary>
        /// 注册轻量更新回调，并在已有工程配置启用时安排即时恢复。
        /// </summary>
        static ProjectAutoConnectMonitor()
        {
            EditorApplication.update += OnEditorUpdate;
            if (ProjectAutoConnectSettings.IsEnabled)
            {
                RequestImmediateCheck();
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// 在用户启用开关后尽快检查连接，而不等待下一个三秒周期。
        /// </summary>
        internal static void RequestImmediateCheck()
        {
            _nextCheckTime = 0.0;
            EditorApplication.delayCall -= RunImmediateCheck;
            EditorApplication.delayCall += RunImmediateCheck;
        }

        /// <summary>
        /// 依据编辑器与传输快照返回无副作用的监视器决策。
        /// </summary>
        /// <param name="isEnabled">当前工程是否启用持久自动连接。</param>
        /// <param name="isBatchMode">是否运行在批处理模式。</param>
        /// <param name="isCompiling">编辑器是否正在编译。</param>
        /// <param name="isUpdating">编辑器是否正在更新资源。</param>
        /// <param name="useHttpTransport">是否选择 HTTP 传输。</param>
        /// <param name="isRemoteScope">是否选择远程 HTTP。</param>
        /// <returns>当前监视器决策。</returns>
        internal static ProjectAutoConnectDecision Evaluate(
            bool isEnabled,
            bool isBatchMode,
            bool isCompiling,
            bool isUpdating,
            bool useHttpTransport,
            bool isRemoteScope)
        {
            if (!isEnabled)
            {
                return ProjectAutoConnectDecision.Disabled;
            }

            if (isBatchMode || isCompiling || isUpdating)
            {
                return ProjectAutoConnectDecision.Busy;
            }

            if (!useHttpTransport)
            {
                return ProjectAutoConnectDecision.UnsupportedTransport;
            }

            return isRemoteScope
                ? ProjectAutoConnectDecision.RemoteScope
                : ProjectAutoConnectDecision.ShouldConnect;
        }

        /// <summary>
        /// 根据跨域连接标记选择恢复意图；任何未完成启动都必须进入禁止拉起进程的重连路径。
        /// </summary>
        /// <param name="persistentConnectPending">持久连接是否在上一域中被中断。</param>
        /// <param name="autoStartConnectPending">一次性自动启动是否在上一域中被中断。</param>
        /// <returns>当前域应使用的连接意图。</returns>
        internal static HttpConnectionIntent ResolveIntent(
            bool persistentConnectPending,
            bool autoStartConnectPending)
        {
            return persistentConnectPending || autoStartConnectPending
                ? HttpConnectionIntent.ReloadReconnect
                : HttpConnectionIntent.PersistentLocal;
        }

        #endregion

        #region Polling

        /// <summary>
        /// 按固定间隔发起连接检查；禁用时只进行一次廉价配置读取。
        /// </summary>
        private static void OnEditorUpdate()
        {
            if (!ProjectAutoConnectSettings.IsEnabled)
            {
                return;
            }

            double now = EditorApplication.timeSinceStartup;
            if (now < _nextCheckTime)
            {
                return;
            }

            _nextCheckTime = now + POLL_INTERVAL_SECONDS;
            _ = CheckConnectionAsync();
        }

        /// <summary>
        /// 执行由开关触发的即时检查，并让后续轮询从当前时刻重新计时。
        /// </summary>
        private static void RunImmediateCheck()
        {
            EditorApplication.delayCall -= RunImmediateCheck;
            _nextCheckTime = EditorApplication.timeSinceStartup + POLL_INTERVAL_SECONDS;
            _ = CheckConnectionAsync();
        }

        /// <summary>
        /// 在允许的编辑器状态下调用共享协调器，并合并重叠监视器请求。
        /// </summary>
        /// <returns>连接检查任务。</returns>
        private static async Task CheckConnectionAsync()
        {
            ProjectAutoConnectDecision decision = Evaluate(
                ProjectAutoConnectSettings.IsEnabled,
                Application.isBatchMode,
                EditorApplication.isCompiling,
                EditorApplication.isUpdating,
                EditorConfigurationCache.Instance.UseHttpTransport,
                HttpEndpointUtility.IsRemoteScope());
            if (decision != ProjectAutoConnectDecision.ShouldConnect || _checkInProgress)
            {
                return;
            }

            _checkInProgress = true;
            bool persistentConnectPending = SessionState.GetBool(ConnectPendingKey, false);
            bool autoStartConnectPending = SessionState.GetBool(HttpAutoStartHandler.ConnectPendingKey, false);
            HttpConnectionIntent intent = ResolveIntent(persistentConnectPending, autoStartConnectPending);
            SessionState.SetBool(ConnectPendingKey, true);
            try
            {
                HttpConnectionOutcome outcome = await HttpConnectionCoordinator.Shared.EnsureConnectedAsync(
                    intent,
                    () => ProjectAutoConnectSettings.IsEnabled);
                if (outcome == HttpConnectionOutcome.Failed)
                {
                    LogFailure("连接检查未能恢复健康会话。", "The connection check could not restore a healthy session.");
                }
            }
            catch (Exception ex)
            {
                LogFailure($"连接检查异常：{ex.Message}", $"Connection check failed: {ex.Message}");
            }
            finally
            {
                SessionState.EraseBool(ConnectPendingKey);
                _checkInProgress = false;
            }
        }

        /// <summary>
        /// 以三十秒冷却输出等价的中英文警告，避免服务器离线时重复刷屏。
        /// </summary>
        /// <param name="chinese">中文诊断。</param>
        /// <param name="english">等价英文诊断。</param>
        private static void LogFailure(string chinese, string english)
        {
            double now = EditorApplication.timeSinceStartup;
            if (now - _lastFailureLogTime < FAILURE_LOG_COOLDOWN_SECONDS)
            {
                return;
            }

            _lastFailureLogTime = now;
            McpLog.Warn($"[自动连接] {chinese}\n[Auto Connect] {english}");
        }

        #endregion
    }
}
