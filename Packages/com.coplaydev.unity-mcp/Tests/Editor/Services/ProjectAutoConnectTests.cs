using MCPForUnity.Editor;
using MCPForUnity.Editor.Constants;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services;
using NUnit.Framework;
using UnityEditor;

namespace MCPForUnityTests.Editor.Services
{
    /// <summary>
    /// 验证持久自动连接的工程隔离设置与编辑器轮询决策。
    /// </summary>
    public sealed class ProjectAutoConnectTests
    {
        #region Fields

        /// <summary>
        /// 保存工程作用域键在测试前是否存在。
        /// </summary>
        private bool _scopedKeyExisted;

        /// <summary>
        /// 保存工程作用域键在测试前的值。
        /// </summary>
        private bool _savedScopedValue;

        /// <summary>
        /// 保存非作用域键在测试前是否存在，以验证不会意外写入全局配置。
        /// </summary>
        private bool _baseKeyExisted;

        /// <summary>
        /// 保存非作用域键在测试前的值。
        /// </summary>
        private bool _savedBaseValue;

        private bool _useHttpExisted;
        private bool _savedUseHttp;
        private bool _scopeExisted;
        private string _savedScope;
        private bool _localUrlExisted;
        private string _savedLocalUrl;

        #endregion

        #region Lifecycle

        /// <summary>
        /// 保存并清空两个相关键，确保作用域行为可独立观察。
        /// </summary>
        [SetUp]
        public void SetUp()
        {
            string scopedKey = ProjectIdentityUtility.GetProjectScopedEditorPrefKey(EditorPrefKeys.AutoConnectEnabled);
            _scopedKeyExisted = EditorPrefs.HasKey(scopedKey);
            _savedScopedValue = EditorPrefs.GetBool(scopedKey, false);
            _baseKeyExisted = EditorPrefs.HasKey(EditorPrefKeys.AutoConnectEnabled);
            _savedBaseValue = EditorPrefs.GetBool(EditorPrefKeys.AutoConnectEnabled, false);
            _useHttpExisted = EditorPrefs.HasKey(EditorPrefKeys.UseHttpTransport);
            _savedUseHttp = EditorPrefs.GetBool(EditorPrefKeys.UseHttpTransport, false);
            _scopeExisted = EditorPrefs.HasKey(EditorPrefKeys.HttpTransportScope);
            _savedScope = EditorPrefs.GetString(EditorPrefKeys.HttpTransportScope, string.Empty);
            _localUrlExisted = EditorPrefs.HasKey(EditorPrefKeys.HttpBaseUrl);
            _savedLocalUrl = EditorPrefs.GetString(EditorPrefKeys.HttpBaseUrl, string.Empty);
            EditorPrefs.DeleteKey(scopedKey);
            EditorPrefs.DeleteKey(EditorPrefKeys.AutoConnectEnabled);
            EditorPrefs.DeleteKey(EditorPrefKeys.UseHttpTransport);
            EditorPrefs.DeleteKey(EditorPrefKeys.HttpTransportScope);
            EditorPrefs.DeleteKey(EditorPrefKeys.HttpBaseUrl);
        }

        /// <summary>
        /// 恢复测试前的用户配置，避免改变当前工程的真实自动连接选择。
        /// </summary>
        [TearDown]
        public void TearDown()
        {
            RestoreBool(EditorPrefKeys.AutoConnectEnabled, _baseKeyExisted, _savedBaseValue);
            string scopedKey = ProjectIdentityUtility.GetProjectScopedEditorPrefKey(EditorPrefKeys.AutoConnectEnabled);
            RestoreBool(scopedKey, _scopedKeyExisted, _savedScopedValue);
            RestoreBool(EditorPrefKeys.UseHttpTransport, _useHttpExisted, _savedUseHttp);
            RestoreString(EditorPrefKeys.HttpTransportScope, _scopeExisted, _savedScope);
            RestoreString(EditorPrefKeys.HttpBaseUrl, _localUrlExisted, _savedLocalUrl);
        }

        #endregion

        #region Tests

        /// <summary>
        /// 验证启用操作只写入当前工程哈希对应的键，不污染机器级基础键。
        /// </summary>
        [Test]
        public void IsEnabled_WritesOnlyProjectScopedPreference()
        {
            ProjectAutoConnectSettings.IsEnabled = true;

            string scopedKey = ProjectIdentityUtility.GetProjectScopedEditorPrefKey(EditorPrefKeys.AutoConnectEnabled);
            Assert.IsTrue(EditorPrefs.GetBool(scopedKey, false));
            Assert.IsFalse(EditorPrefs.HasKey(EditorPrefKeys.AutoConnectEnabled));
            Assert.IsTrue(ProjectAutoConnectSettings.IsEnabled);
        }

        /// <summary>
        /// 验证 batchmode 入口选择本地 HTTP，只启用当前工程 AutoConnect，且不写入全局 AutoStart。
        /// </summary>
        [Test]
        public void EnableHttpAutoConnectForCurrentProject_ConfiguresSafeProjectScopedLocalHttp()
        {
            bool autoStartExisted = EditorPrefs.HasKey(EditorPrefKeys.AutoStartOnLoad);
            bool savedAutoStart = EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false);
            try
            {
                EditorPrefs.SetString(EditorPrefKeys.HttpBaseUrl, "http://localhost:9999");
                McpCiBoot.EnableHttpAutoConnectForCurrentProject();

                Assert.IsTrue(EditorPrefs.GetBool(EditorPrefKeys.UseHttpTransport, false));
                Assert.AreEqual("local", EditorPrefs.GetString(EditorPrefKeys.HttpTransportScope, string.Empty));
                Assert.AreEqual("http://127.0.0.1:8080", HttpEndpointUtility.GetLocalBaseUrl());
                Assert.IsTrue(ProjectAutoConnectSettings.IsEnabled);
                Assert.IsFalse(EditorPrefs.HasKey(EditorPrefKeys.AutoConnectEnabled));
                Assert.AreEqual(autoStartExisted, EditorPrefs.HasKey(EditorPrefKeys.AutoStartOnLoad));
                Assert.AreEqual(savedAutoStart, EditorPrefs.GetBool(EditorPrefKeys.AutoStartOnLoad, false));
            }
            finally
            {
                RestoreBool(EditorPrefKeys.AutoStartOnLoad, autoStartExisted, savedAutoStart);
            }
        }

        /// <summary>
        /// 验证关闭配置时监视器明确返回禁用决策。
        /// </summary>
        [Test]
        public void Evaluate_Disabled_ReturnsDisabled()
        {
            Assert.AreEqual(ProjectAutoConnectDecision.Disabled,
                ProjectAutoConnectMonitor.Evaluate(false, false, false, false, true, false));
        }

        /// <summary>
        /// 验证批处理、编译和资源更新阶段都被视为忙碌，避免重入 Unity 生命周期。
        /// </summary>
        [TestCase(true, false, false)]
        [TestCase(false, true, false)]
        [TestCase(false, false, true)]
        public void Evaluate_BusyEditor_ReturnsBusy(bool isBatchMode, bool isCompiling, bool isUpdating)
        {
            Assert.AreEqual(ProjectAutoConnectDecision.Busy,
                ProjectAutoConnectMonitor.Evaluate(true, isBatchMode, isCompiling, isUpdating, true, false));
        }

        /// <summary>
        /// 验证 stdio 配置不会触发本地 HTTP 自动恢复。
        /// </summary>
        [Test]
        public void Evaluate_Stdio_ReturnsUnsupportedTransport()
        {
            Assert.AreEqual(ProjectAutoConnectDecision.UnsupportedTransport,
                ProjectAutoConnectMonitor.Evaluate(true, false, false, false, false, false));
        }

        /// <summary>
        /// 验证远程 HTTP 配置不会触发本地服务器自动启动。
        /// </summary>
        [Test]
        public void Evaluate_RemoteHttp_ReturnsRemoteScope()
        {
            Assert.AreEqual(ProjectAutoConnectDecision.RemoteScope,
                ProjectAutoConnectMonitor.Evaluate(true, false, false, false, true, true));
        }

        /// <summary>
        /// 验证空闲的本地 HTTP 配置会触发连接检查。
        /// </summary>
        [Test]
        public void Evaluate_LocalHttp_ReturnsShouldConnect()
        {
            Assert.AreEqual(ProjectAutoConnectDecision.ShouldConnect,
                ProjectAutoConnectMonitor.Evaluate(true, false, false, false, true, false));
        }

        #endregion

        #region Helpers

        /// <summary>
        /// 按测试前的存在状态恢复布尔编辑器配置。
        /// </summary>
        /// <param name="key">需要恢复的编辑器配置键。</param>
        /// <param name="existed">测试前是否存在该键。</param>
        /// <param name="value">测试前的布尔值。</param>
        private static void RestoreBool(string key, bool existed, bool value)
        {
            if (existed)
            {
                EditorPrefs.SetBool(key, value);
            }
            else
            {
                EditorPrefs.DeleteKey(key);
            }
        }

        /// <summary>
        /// 按测试前的存在状态恢复字符串编辑器配置。
        /// </summary>
        private static void RestoreString(string key, bool existed, string value)
        {
            if (existed)
            {
                EditorPrefs.SetString(key, value);
            }
            else
            {
                EditorPrefs.DeleteKey(key);
            }
        }

        #endregion
    }
}
