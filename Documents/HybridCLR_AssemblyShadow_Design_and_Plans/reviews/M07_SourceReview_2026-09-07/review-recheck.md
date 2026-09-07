# 结论复核与误报控制

此文件是本次审查的结论自查，不冒充另一个独立审查者或一次真实 Player 复测。

| 易误读点 | 本报告的限定 |
|---|---|
| 338 是不是候选 AOT 程序集总数上限？ | 不是，是当前分配器在特定大小/fresh 假设下的 Interpreter Image 上界。 |
| 已有 definitions cache，ASR-002 是否误报？ | 不是同一缓存：该 cache 不覆盖每次 allocation 的 CheckActiveComponents/CheckLayout。 |
| 所有 AOT 方法都变成 guard dispatch 了吗？ | 没有；普通直接非虚 AOT 调用仍靠闭包/Bootstrap 隔离，报告只指已接入的受保护入口。 |
| private reference 一定必须允许吗？ | 当前 native 明确保守拒绝；问题是能力比原宏观目标窄且准入需前置。放宽必须另有证明。 |
| 去掉 slot 是否意味着不检查方法 ABI？ | 不是；lookup identity 与 compatibility 分开，执行旧 AOT 仍拒绝。 |
| 并图伪环修复是否会删除 baseline 依赖？ | 不会；安全闭包保留并图，只有加载图改为 target 真实依赖。 |
| source pins 是否已经错误？ | 没有判定当前 pin 错误；指出整个工具仓库 SHA 作为 runtime ABI 的长期耦合。 |
| Stage/Commit/private visibility 是否尚未实现？ | 已实现并读到；原初步评估中的潜在风险不能再当作缺失实现。 |
| FailedAfterCommit 是不是自动停止了整个进程？ | 不是；状态封存、受支持入口 guard、Bootstrap 停止和 OS 进程行为要分开。 |
| M07 已证明 Windows/Android 吗？ | 没有；现有接受记录明确是 macOS ARM64，扩展属 M10。 |
| MonoScript fallback 是否等于 GetClass 直接支持？ | 不等于；报告保留原契约的标签差异。 |
| Add/Remove 不支持是否让 M07 全盘失败？ | 不会；它是独立能力缺口，若属于最终产品目标则须追加 Gate。 |
| 输入数组并发修改是否当前 API 保证安全？ | 未见该保证；原文只保证返回后可复用，未把并发修改写成已确认漏洞。 |
| native reader assert 是否已经证明存在可利用崩溃？ | 没有；仅确定还需 metadata/IL 边界加固和 sanitizer 复现。 |
| 本次 13 项 findings 是否全部已在运行时复现？ | 不是；每项都有证据等级。仅容量/图的独立算法模型实际执行。 |

进一步验证发现某条件由未阅读的更上游 contract 明确禁止时，应将该项分类改为“限制需文档化/计划改进”，并保留来源及反例分析，不把禁止输入伪装成原本支持的场景。
