# R01B v6 runtime acceptance matrix

Status: **Automated v6 evidence is sealed; independent full-stage review and H1 remain pending.**

Baseline: `M07-Baseline-R01B-20260909-v6`. Each row is a concrete hash-bound receipt from [runtime-v6-acceptance.json](runtime-v6-acceptance.json).

| Gate | Evidence |
|---|---|
| Startup ordering, refusal, metadata/initializer failures: 11 exact strict modes; selected launch and early raw results | `_temp/AssemblyShadow/R01B-v6-matrix-1/strict-verification.json` (`9ea5707a7e609f62940ee78059b018b0152b79a62ac0fc6575e93b5f70c3c9c6`) |
| Resources, nested prefabs, closure, APIs, scenes, serialization, messages, caches, P04/P05, OFF: 14 exact modes; source/baseline binding and unchanged evidence | `_temp/AssemblyShadow/R01B/v6-m07-aggregate-1.json` (`868963c010ccbf3b3b58d465808e762ededdf609d9cc67ec6ad039f77a0dc002`) |
| Ordinary image boundaries: 8,191 and 8,192 charged; 8,193 ImageLimit rejection preserves mappings | `_temp/AssemblyShadow/R01B-v6-capacity-ordinary-1/strict-verification.json` (`2e9b7d06cf952d1a749a6ecd68a6a2feb8b0d58e4ee0f935d248f88357130b04`) |
| Mixed ordinary/Shadow/retained failures: 8,184 valid ordinary + 5 Shadow + 3 retained failures | `_temp/AssemblyShadow/R01B-v6-capacity-mixed-1/strict-verification.json` (`f60c64307c0a44e40f2e06fd07e8e2ca5dc67d72ea459543c95c76e224375626`) |
| Generics, arrays, inherited interfaces, attributes/retry and dense fixtures: 61 passing raw checks | `_temp/AssemblyShadow/R01B-v6-lazy-1/r01b-lazy-player-launch.json` (`146391cc1dc896dbc8de4c63ab97e241698ea49cdcceeb3ab48828fc94dbc7c3`) |
| Immutable profile-1 Player refusal: Historical old pins and exact current new pins; unchanged inputs | `_temp/AssemblyShadow/R01B-v6-old-player-1/old-player-rejection-receipt.json` (`a05180cec370574855f6c466c5def5e2539ae1708e828b2fd55e1f21e4613d16`) |
| Authenticated R00 handoff: Four strict modes after the Serializable DTO correction | `_temp/AssemblyShadow/R01B-v6-r00-1/strict-verification.json` (`aeb9a23ed307f56640212b01cde92b9e4c7d347f718f6c268b1b4114d2c58554`) |
| Descriptive timing and readiness: 48 unique timing cells, four readiness rows, selected current gate/launch/raw hashes | `_temp/AssemblyShadow/R01B/v6-r00-comparison-1.json` (`501a06a1d49658e36495a34b46d6ae8fe9535db6379b8429d87ebc26f22efb17`) |
| Managed compiler and Editor regression: 1,021 Editor and 492 fresh Python passes; capture bytes verified | `Docs/AssemblyShadow/M07R/R01B/corrective-v6-source-validation.json` (`8dd782d8e00cbaee6e2867e0a6b4d942fd25ceb3cc358574f79fa4448e96a18c`) |
| Native evidence reuse: Current native heads and v5 index/raw hashes; no fresh v6 execution | `Docs/AssemblyShadow/M07R/R01B/native-v6-validation.json` (`87925772c14f09e5585ffcad207160caaaecb08e3010bb1045a7ac6eb7709ed9`) |
| Actual workload count widths: 8,192 actual file hashes and dense/lazy/patch shapes; no over-limit certification | `Docs/AssemblyShadow/M07R/R01B/workload-v6-shape-audit.json` (`3dd60a7174523b28a90659da5b46d3f002f31aa727c54e3e06631a66b0e693f1`) |
| Inherited loader limitations: Two NotFixedInheritedScopeLimitation findings; counterexamples NotRun | `Docs/AssemblyShadow/M07R/R01B/preliminary-v6-code-review.json` (`531569637566faaabd50e0ff859e2c0a5e0033bd80e69b877b7b7913b569ed02`) |

H1 has not passed. R02 remains prohibited.
