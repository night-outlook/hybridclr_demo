# 命令登记与任务绑定

本页区分 ExistingSourceReferenced、NeedsLocalVerification、Proposed。旧计划记录过的 CLI 仍需在本地 exact commit 检查；路径存在、`--help` 成功与语义验证是三件不同的事。不臆造 Unity executeMethod 或不存在的开关。

## C1. 已知只读命令

M00 逐仓库实际 root 盘点（每次一张卡）：

```bash
git -C "$REPO" rev-parse --show-toplevel
git -C "$REPO" rev-parse HEAD
git -C "$REPO" branch --show-current
git -C "$REPO" status --porcelain=v1 --untracked-files=all
git -C "$REPO" cat-file -e "$REVIEW_SHA^{commit}"
```

变量由当前卡填成实际值。HEAD 不同先记录差异，不 reset/clean/checkout 覆盖用户工作。M00 首任务只执行 demo 盘点。

原 v6 从 fixed git object 提取到全新仓库外目录：

```bash
set -euo pipefail
set -o noclobber
V6=9534c7c775d69b79ecd612917231bef3d202a5aa
E=Docs/AssemblyShadow/M07R/R01B/Evidence
mkdir "$NEW_AUDIT_DIR"
git -C "$DEMO" show "$V6:$E/evidence-v6-index.json" > "$NEW_AUDIT_DIR/evidence-v6-index.json"
git -C "$DEMO" show "$V6:$E/r01b-v6-evidence.tar.gz" > "$NEW_AUDIT_DIR/r01b-v6-evidence.tar.gz"
shasum -a 256 "$NEW_AUDIT_DIR/evidence-v6-index.json" "$NEW_AUDIT_DIR/r01b-v6-evidence.tar.gz"
```

NEW_AUDIT_DIR 必须事先不存在。此命令只有字节提取/散列意义，不等于 M01 全部认证。

## C2. ExistingSourceReferenced 的测试入口

```bash
python3 "$DEMO/Tools/AssemblyShadow/run-r01b-index-runtime-tests.py"   --demo-root "$DEMO" --native-root "$HYBRIDCLR"   --runtime-root "$IL2CPP_PLUS" --compiler clang++ --output "$NEW_RECEIPT"
```

该旧 harness 为 macOS、实际 adapter/codec 加 opaque image/TLS stub，旧配置是 O1+sanitizers；不是完整 loader 或 Debug/Release 计数验收。

```bash
python3 "$DEMO/Tools/AssemblyShadow/run-r00-players.py"   --project-root "$DEMO" --fixture-manifest "$FIXTURES"   --on-build "$ON_RECEIPT" --off-build "$OFF_RECEIPT"   --replay-receipt "$REPLAY" --output-root "$NEW_R00_OUTPUT"   --early-startup-strategy R01EarlyStartup
```

旧 runner 一次四模式，不假定它有 --mode/--pairs/--release。输出必须符合其 canonical new-child 约束。2A 单对调度需要受审的新 driver/adapter，不能擅自改 legacy startup 为“可比”。

Python 基础 discovery 形状：

```bash
(cd "$DEMO" && python3 -m unittest discover -s Tools/AssemblyShadow/tests -p 'test_*.py' -v)
```

运行前绑定真实 compiler-input env；不能因环境缺失跳过测试再宣称 492 PASS。

## C3. 分组核对，不一次读取全部工具

每张 command-inspection 卡仅查一个 suite 的 parser/source/历史 receipt，登记完整 argv/cwd/env/输入输出/side effects。

- Native：run-m03-visibility-tests.py、run-r01-budget-contention-native-tests.py、run-r01-startup-native-tests.py、run-r01-transaction-native-tests.py、run-r01b-parser-tests.py、run-r01b-live-capability-tests.py。
- Player：run-r01b-lazy-player.py、run-r01b-old-player-rejection.py、verify-r01b-capacity-result.py，以及当前真实 startup/M07/容量 launcher。
- Build/Editor：从现有 build scripts、Editor symbols 和 receipt 核对 actual entry，不在计划猜参数。

上述脚本位于 demo `Tools/AssemblyShadow/`。跨平台/编译配置和 asserted build flags 由实际记录核对。

## C4. Proposed 工具合同

需要时在单独 Implement→Validate→Review 卡内建立，能复用则复用受审模块。以下不是现在已存在的命令。

| 工具 | 有界调用合同 | 用途 |
|---|---|---|
| audit-h1-evidence.py | --operation bytes / members / references / sources / raw；--input-map；--output-root | 一次认证一层/一组，不在一次调用自动跑全计划 |
| create-h1-count-fixtures.py | --family parameters / nested；--case-set；--seed；--output-root | 一个 count family |
| h1_count_fixture_audit.py | --manifest；--output | 独立读取实际 DLL shape |
| run-h1-count-players.py | --project-root；--case-manifest；--build-matrix；--family；--load-path；--cpp-config；--output-root | family/path/config 单分片；可额外 --case-id 定向 |
| verify-h1-count-results.py | --required-matrix；--result-index；--output | 最终 84+variants 集合验证 |
| run-h1-controlled-performance.py | --protocol；--build-map；--schedule；--mode；--pair-id（或冻结 batch）；--output-root | 一对/一个小批正式样本 |
| verify-h1-controlled-performance.py | --protocol；--sample-index；--output | 独立配对重算 |

输入 map 中的 archive/index/hash/source mapping 必须显式绑定；不用命令字符串猜 artifact。任何 narrower selector 都要记录 requested/executed IDs，不能产生 FullMatrixPassed。

## C5. 派发前条件

`command-manifest.json` 每条含 commandId、status、script/symbol commit/hash、argv数组、cwd、必要 env、inputs+hash、输出新目录、副作用、支持配置、oracle、allowlist。runtime 尚未实现的 Proposed 只能派发工具开发卡，不能派发运行卡。

执行卡中的命令不得含 TBD/未解析占位符。返回码 0 仅代表该入口实际目标满足；JSON 区分 Failed/Blocked/NoCoverage。零 testcase、缺必需 cell、输入变更、hash mismatch 不得 exit 0。所有正式结果使用新 run ID，不能覆盖旧结果。
