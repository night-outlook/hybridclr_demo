using NUnit.Framework;
using UnityEditor;
using UnityEngine.UIElements;

namespace MCPForUnityTests.Editor.Windows
{
    /// <summary>
    /// 验证连接面板资源能实例化持久自动连接所需的真实 UI 控件。
    /// </summary>
    public sealed class McpConnectionSectionUxmlTests
    {
        #region Tests

        /// <summary>
        /// 验证 UXML 克隆结果包含 Auto Connect 行和可绑定的开关。
        /// </summary>
        [Test]
        public void CloneTree_ContainsAutoConnectRowAndToggle()
        {
            const string assetPath =
                "Packages/com.coplaydev.unity-mcp/Editor/Windows/Components/Connection/McpConnectionSection.uxml";
            VisualTreeAsset asset = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(assetPath);

            Assert.IsNotNull(asset);
            TemplateContainer root = asset.CloneTree();
            Assert.IsNotNull(root.Q<VisualElement>("auto-connect-row"));
            Assert.IsNotNull(root.Q<Toggle>("auto-connect-toggle"));
        }

        #endregion
    }
}
