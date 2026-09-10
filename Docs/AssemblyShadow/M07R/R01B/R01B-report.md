# R01B v6 encoding and bounded runtime evidence

Status: **V6 evidence is sealed for independent full-stage review; H1 remains pending.**

Baseline: `M07-Baseline-R01B-20260909-v6`. The current [source-v6-inventory.json](source-v6-inventory.json) binds HybridCLR `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`, Unity package `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`.

The normative R01B execution plan retains its historical accepted R01 entry pins: HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`, il2cpp_plus `7967b8c7043904fcae130b294defd5ce7aa897c4`, Unity package `b649c499385ea68490a0f652a98b732e060aeb89`, demo metadata `b89959fcb5b9a3da1dd0e0ffe7874de412472ae8` / executable `cc7b17683c2e68a162914c347bb81d765dbc26c0`. This v6 delivery records the current pins without rewriting that historical plan.

The immutable source inventory records 200 unique repository/path pairs across 201 source-commit range entries; duplicated version entries remain separately accounted.

## Automated evidence and capacity

The strict startup matrix covers **11/11 modes**, the M07 aggregate **14/14 modes**, and R00 **4/4 modes**. The selected lazy/dense raw result contains **61 passing checks**. Managed regression captures report **1,021 Editor passes** and **492 fresh Python passes**, both with zero failures/skips; the latter is python-v6-sealed-2.log. [Runtime acceptance matrix](runtime-acceptance-matrix.md) maps each behavior to its exact receipt.

The ordinary Player loads and invokes **8,192 valid DLLs** totaling **512 MiB**, with a 64 KiB mean. The mixed Player loads **8,184 valid ordinary DLLs** with **five Shadow images** and **three retained failed ordinary reservations**: 8,189 valid DLLs total 512 MiB plus 12 failed-input bytes. Its valid-DLL mean is not 64 KiB. The workload manifests include a **32 MiB DLL**; padding/input bytes are not metadata-density or RAM measurements. Both receipts record image **8,191 / 8,192** snapshots and reject image **8,193** with ImageLimit while retaining earlier ledger and mapping values. The mixed native ordinary allocation count is 8,187 including failures, while successful ordinary loads remain 8,184. Both retain at least **131,072 free usable pages**.

## Runtime measurements

The ordinary and mixed v6 receipts provide these measured ledger and memory values:

| Workload | Ordinary loaded | Shadow | Retained failures | Reserved / mapped pages | Free usable pages | Initial / lifetime peak RSS |
|---|---:|---:|---:|---:|---:|---:|
| ordinary | 8192 | 0 | 0 | 16,388 / 16,388 | 507,899 (96.874%) | 231.91 / 1642.56 MiB |
| mixed | 8184 | 5 | 3 | 16,392 / 16,389 | 507,895 (96.873%) | 293.56 / 1700.66 MiB |

The concrete v6 runtime receipts and fresh managed captures are hash-bound in [runtime-v6-acceptance.json](runtime-v6-acceptance.json). Native evidence is explicitly a v6 reuse audit over unchanged native-v5 raw executions; no fresh native execution is claimed. V5's R00 handoff defect is historical: BCL raw `ReceiptCodec.Serialize` already contained operations and snapshots, while `JsonUtility` deserialization lost nested arrays because nested DTOs lacked `Serializable` attributes. V6 preserves the Serializable DTO projection correction. The v4-fixed header diagnostic limits remain preserved. The inherited loader supports method parameter counts 0..255 and nested children per declaring type 0..65,535; R01B does not widen `parameterCount` or `nested_type_count`, and does not claim arbitrary over-limit or malformed-shape rejection. The [preliminary code review](preliminary-v6-code-review.json) explicitly retains two NotFixedInheritedScopeLimitation findings. The [workload shape audit](workload-v6-shape-audit.json) binds the raw actual-input audit and its recipe; its bounded PASS does not fix or certify those over-limit cases.

The ordinary and mixed receipts provide the runtime ledger, reservation, mapped-page, retained-failure, RSS, managed-byte, and load-time measurements shown in their sealed raw results. Abort and later initialization/publication failures retain committed reservations and credits; failed preflight leaves the committed ledger unchanged. Peak RSS is the process-lifetime kernel maximum through rejection and mapping checks, not workload-attributable growth. Load time includes I/O, hashing, loading, invocation, checks and memory sampling alongside other validation activity. No calibrated RAM threshold is claimed.

The R00 comparison retains all 48 timing cells from its authenticated raw receipts. Development samples do not establish Release performance, P99, or the directional feature-OFF target, and there is no equivalent R01 Player timing baseline. Windows, Android, and broader device/workload qualification remain M10; repeated per-process Shadow transactions remain R03.

Independent full-stage review is required before the H1 human review handoff. H1 remains pending and R02 remains prohibited.
