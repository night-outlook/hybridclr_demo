using System;
using System.Threading.Tasks;
using MCPForUnity.Editor.Constants;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services.Transport;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Services
{
    /// <summary>
    /// Automatically starts the HTTP MCP bridge on editor load when the user has opted in
    /// via the "Auto-Start on Editor Load" toggle in Advanced Settings.
    /// This complements HttpBridgeReloadHandler (which only resumes after domain reloads).
    /// </summary>
    [InitializeOnLoad]
    internal static class HttpAutoStartHandler
    {
        internal const string SessionInitKey = "HttpAutoStartHandler.SessionInitialized";

        // Set while AutoStartAsync is in flight. A domain reload kills the in-flight task but
        // leaves this set, so the next domain load can finish the connect phase without
        // re-spawning the server (StartLocalHttpServer would first stop a still-booting process).
        internal const string ConnectPendingKey = "HttpAutoStartHandler.ConnectPending";

        // Bounds the per-frame retry when editor services keep throwing on a fresh launch.
        // Plain static, so every domain reload grants a fresh budget.
        private const int MaxServiceNotReadyRetries = 300;
        private static int _serviceNotReadyRetries;

        internal enum TickDecision
        {
            DeferBusy,
            DeferToResume,
            Skip,
            ShouldStart,
            ShouldReconnect,
        }

        static HttpAutoStartHandler()
        {
            if (Application.isBatchMode &&
                string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("UNITY_MCP_ALLOW_BATCH")))
            {
                return;
            }

            bool latched = SessionState.GetBool(SessionInitKey, false);
            bool connectPending = SessionState.GetBool(ConnectPendingKey, false);

            // Cheap pre-check so the common case (auto-start off, nothing pending) costs one
            // EditorPrefs read per domain load instead of an update subscription. The pref is
            // re-read every domain load, so enabling it takes effect at the next reload.
            if (!latched && !connectPending &&
                !EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false))
            {
                return;
            }

            // Latched with nothing pending: this session already auto-started.
            if (latched && !connectPending)
            {
                return;
            }

            // Pending EditorApplication.delayCall/update delegates are wiped by domain reloads,
            // so the deferred work must NOT latch up front — latching eagerly killed auto-start
            // for the whole session whenever startup included a compile (#1229). An update tick
            // is reload-safe because this ctor re-arms it on every domain load.
            EditorApplication.update += WaitForEditorReady;
        }

        /// <summary>
        /// Drops a reload-interrupted auto-start connect. Called when the user takes manual
        /// control of the bridge lifecycle, so no later domain load revives the connect.
        /// </summary>
        internal static void CancelPendingReconnect() => SessionState.EraseBool(ConnectPendingKey);

        private static void WaitForEditorReady()
        {
            switch (TickCore(HttpBridgeReloadHandler.IsEditorBusy()))
            {
                case TickDecision.DeferBusy:
                case TickDecision.DeferToResume:
                    return; // stay registered, try again next tick

                case TickDecision.Skip:
                    EditorApplication.update -= WaitForEditorReady;
                    return;

                case TickDecision.ShouldStart:
                    if (!TryBeginAutoStart())
                    {
                        DeferOrGiveUp();
                        return;
                    }
                    SessionState.SetBool(SessionInitKey, true);
                    EditorApplication.update -= WaitForEditorReady;
                    return;

                case TickDecision.ShouldReconnect:
                    if (!TryBeginReconnect())
                    {
                        DeferOrGiveUp();
                        return;
                    }
                    EditorApplication.update -= WaitForEditorReady;
                    return;
            }
        }

        // Services may not be initialized on the first frames of a fresh launch; retry next
        // tick, but not forever — a persistently broken environment shouldn't churn exceptions
        // every frame for the whole session. A later domain reload retries with a fresh budget.
        private static void DeferOrGiveUp()
        {
            if (++_serviceNotReadyRetries < MaxServiceNotReadyRetries) return;
            EditorApplication.update -= WaitForEditorReady;
            McpLog.Warn("[HTTP Auto-Start] Editor services unavailable; giving up until the next domain reload");
        }

        /// <summary>
        /// Decision core for the editor-ready tick, separated so EditMode tests can drive it
        /// without spawning servers. Never writes the session latch — the caller latches only
        /// after the start work actually dispatches.
        /// </summary>
        internal static TickDecision TickCore(bool editorBusy)
        {
            if (editorBusy) return TickDecision.DeferBusy;

            bool connectPending = SessionState.GetBool(ConnectPendingKey, false);
            if (!connectPending)
            {
                if (SessionState.GetBool(SessionInitKey, false)) return TickDecision.Skip;

                // Only check lightweight EditorPrefs here — heavier services are touched in
                // TryBeginAutoStart once the editor is idle. No latch when disabled: the pref
                // is re-read on the next domain load.
                if (!EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false)) return TickDecision.Skip;
            }

            // A pending reload-resume owns bridge revival — checked only when we would
            // otherwise act, so a plain Skip never waits out the resume window.
            if (HttpBridgeReloadHandler.IsResumePending) return TickDecision.DeferToResume;

            return connectPending ? TickDecision.ShouldReconnect : TickDecision.ShouldStart;
        }

        /// <summary>
        /// Returns true when the auto-start decision was actually made (including deliberate
        /// early-outs). Returns false when services were not ready yet, so the caller leaves
        /// the session latch unset and retries instead of consuming it.
        /// </summary>
        private static bool TryBeginAutoStart()
        {
            try
            {
                if (!EditorConfigurationCache.Instance.UseHttpTransport) return true;

                // Don't auto-start if bridge is already running.
                if (MCPServiceLocator.TransportManager.IsRunning(TransportMode.Http)) return true;

                _ = AutoStartAsync();
                return true;
            }
            catch (Exception ex)
            {
                McpLog.Debug($"[HTTP Auto-Start] Services not ready: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Returns false when services were not ready yet (caller retries). On true the
        /// pending reconnect was either dispatched or deliberately dropped (auto-start
        /// disabled, transport switched, bridge already running).
        /// </summary>
        internal static bool TryBeginReconnect()
        {
            bool proceed;
            try
            {
                proceed = EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false)
                    && EditorConfigurationCache.Instance.UseHttpTransport
                    && !MCPServiceLocator.TransportManager.IsRunning(TransportMode.Http);
            }
            catch (Exception ex)
            {
                McpLog.Debug($"[HTTP Auto-Start] Services not ready: {ex.Message}");
                return false;
            }

            if (!proceed)
            {
                SessionState.EraseBool(ConnectPendingKey);
                return true;
            }

            _ = ReconnectAsync();
            return true;
        }

        private static async Task AutoStartAsync()
        {
            SessionState.SetBool(ConnectPendingKey, true);
            try
            {
                HttpConnectionOutcome outcome = await HttpConnectionCoordinator.Shared.EnsureConnectedAsync(
                    HttpConnectionIntent.AutoStart,
                    () => EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false));
                if (outcome == HttpConnectionOutcome.Failed)
                {
                    McpLog.Warn(
                        "[HTTP 自动启动] 未能建立健康连接。\n" +
                        "[HTTP Auto-Start] Failed to establish a healthy connection.");
                }
            }
            catch (Exception ex)
            {
                McpLog.Warn(
                    $"[HTTP 自动启动] 执行异常：{ex.Message}\n" +
                    $"[HTTP Auto-Start] Failed: {ex.Message}");
            }
            finally
            {
                // Reached on every terminal outcome. A domain reload that kills the task
                // mid-flight skips this, leaving the key set for the reconnect path.
                SessionState.EraseBool(ConnectPendingKey);
            }
        }

        /// <summary>
        /// Finishes an auto-start whose connect phase was killed by a domain reload.
        /// Connect-only: never spawns a server — the previous domain already did.
        /// </summary>
        private static async Task ReconnectAsync()
        {
            try
            {
                HttpConnectionOutcome outcome = await HttpConnectionCoordinator.Shared.EnsureConnectedAsync(
                    HttpConnectionIntent.ReloadReconnect,
                    () => EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false));
                if (outcome == HttpConnectionOutcome.Failed)
                {
                    McpLog.Warn(
                        "[HTTP 自动启动] 域重载后未能恢复健康连接。\n" +
                        "[HTTP Auto-Start] Failed to restore a healthy connection after domain reload.");
                }
            }
            catch (Exception ex)
            {
                McpLog.Warn(
                    $"[HTTP 自动启动] 域重载后重连异常：{ex.Message}\n" +
                    $"[HTTP Auto-Start] Post-reload reconnect failed: {ex.Message}");
            }
            finally
            {
                SessionState.EraseBool(ConnectPendingKey);
            }
        }

    }
}
