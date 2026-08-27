using MCPForUnity.Editor.Windows.Components.Connection;
using NUnit.Framework;

namespace MCPForUnityTests.Editor.Windows
{
    /// <summary>
    /// 验证稳定版连接面板对短暂探测失败的去抖行为。
    /// </summary>
    public sealed class McpConnectionSectionRegressionTests
    {
        #region Tests

        /// <summary>
        /// 验证达到连续失败阈值后才结束空悬的本地 HTTP 会话。
        /// </summary>
        [Test]
        public void OrphanedSession_EndsAtThreshold()
        {
            Assert.IsTrue(McpConnectionSection.ShouldEndOrphanedSession(
                true, true, false, false, McpConnectionSection.OrphanedSessionDownPollThreshold));
        }

        /// <summary>
        /// 验证一次短暂的服务器探测失败不会结束健康会话。
        /// </summary>
        [Test]
        public void OrphanedSession_SingleFailedPollIsDebounced()
        {
            Assert.IsFalse(McpConnectionSection.ShouldEndOrphanedSession(true, true, false, false, 1));
        }

        /// <summary>
        /// 验证编辑器繁忙时即使超过阈值也延迟结束会话。
        /// </summary>
        [Test]
        public void OrphanedSession_BusyEditorDefers()
        {
            Assert.IsFalse(McpConnectionSection.ShouldEndOrphanedSession(
                true, true, false, true, McpConnectionSection.OrphanedSessionDownPollThreshold + 1));
        }

        /// <summary>
        /// 验证非本地 HTTP 或连接切换过程中不会误结束会话。
        /// </summary>
        [TestCase(false, true)]
        [TestCase(true, false)]
        public void OrphanedSession_IneligibleStateDoesNotEnd(bool httpLocalSelected, bool sessionRunning)
        {
            Assert.IsFalse(McpConnectionSection.ShouldEndOrphanedSession(
                httpLocalSelected, sessionRunning, false, false,
                McpConnectionSection.OrphanedSessionDownPollThreshold + 2));
        }

        /// <summary>
        /// 验证单次桥接健康检查失败不会立即显示为损坏。
        /// </summary>
        [Test]
        public void HealthVerification_SingleFailureIsDebounced()
        {
            Assert.IsFalse(McpConnectionSection.ShouldReportUnhealthy(1));
        }

        /// <summary>
        /// 验证达到健康检查失败阈值后才报告不健康状态。
        /// </summary>
        [Test]
        public void HealthVerification_ReportsAtThreshold()
        {
            Assert.IsTrue(McpConnectionSection.ShouldReportUnhealthy(
                McpConnectionSection.UnhealthyVerificationThreshold));
            Assert.GreaterOrEqual(McpConnectionSection.UnhealthyVerificationThreshold, 2);
        }

        #endregion
    }
}
