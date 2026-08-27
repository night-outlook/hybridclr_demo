using MCPForUnity.Editor.Constants;
using MCPForUnity.Editor.Helpers;
using UnityEditor;

namespace MCPForUnity.Editor.Services
{
    /// <summary>
    /// 读写当前工程独立的持久自动连接配置，避免多个工作副本共享机器级开关。
    /// </summary>
    internal static class ProjectAutoConnectSettings
    {
        #region Properties

        /// <summary>
        /// 获取或设置当前工程是否持续恢复本地 HTTP 服务与会话。
        /// </summary>
        internal static bool IsEnabled
        {
            get => EditorPrefs.GetBool(GetPreferenceKey(), false);
            set => EditorPrefs.SetBool(GetPreferenceKey(), value);
        }

        #endregion

        #region Helpers

        /// <summary>
        /// 构造当前工程哈希作用域的配置键。
        /// </summary>
        /// <returns>当前工程专用的 EditorPrefs 键。</returns>
        private static string GetPreferenceKey()
            => ProjectIdentityUtility.GetProjectScopedEditorPrefKey(EditorPrefKeys.AutoConnectEnabled);

        #endregion
    }
}
