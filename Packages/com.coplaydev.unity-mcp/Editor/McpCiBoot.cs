using System;
using MCPForUnity.Editor.Constants;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services;
using MCPForUnity.Editor.Services.Transport.Transports;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor
{
    public static class McpCiBoot
    {
        #region Public Methods

        /// <summary>
        /// 为当前工程选择本地 HTTP 传输并启用工程作用域 AutoConnect。
        /// 该入口供 Unity batchmode 预检调用，不会启用机器级 AutoStart。
        /// </summary>
        public static void EnableHttpAutoConnectForCurrentProject()
        {
            EditorPrefs.SetBool(EditorPrefKeys.UseHttpTransport, true);
            EditorPrefs.SetString(EditorPrefKeys.HttpTransportScope, "local");
            HttpEndpointUtility.SaveLocalBaseUrl("http://127.0.0.1:8080");
            ProjectAutoConnectSettings.IsEnabled = true;

            Debug.Log("[MCP-CI] AUTOCONNECT_READY project-scoped=true transport=http scope=local");
        }

        /// <summary>
        /// 为 CI 启动 stdio 自动连接。
        /// </summary>
        public static void StartStdioForCi()
        {
            try
            {
                EditorPrefs.SetBool(EditorPrefKeys.UseHttpTransport, false);
            }
            catch { /* ignore */ }

            StdioBridgeHost.StartAutoConnect();
        }

        #endregion
    }
}
