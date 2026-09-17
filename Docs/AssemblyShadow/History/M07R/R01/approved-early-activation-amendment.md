# Approved R01 early-activation experiment

Status: authorized by the user's response annotations on 2026-09-08; fresh v6 implementation and bounded evidence are available. The strict 11-mode profile is `PassedBoundedProfile`, the nine-suite native scope is `PassedNativeScope`, and all 14 producer cases have passed, while the strict14 aggregate has passed. Final packaging has passed; independent stage review is pending, so this amendment does not stage-accept R01 or pass H1. This appends to `startup-blocker-report.md` and does not change its historical findings or source/evidence hashes.

The current evidence is indexed by [early-v6-strict-matrix.json](early-v6-strict-matrix.json:1), [early-v6-native-regressions.json](early-v6-native-regressions.json:1), and [early-v6-runtime-and-gap-review.json](early-v6-runtime-and-gap-review.json:1). These indices distinguish the bounded strict/native results from the still-open strict14, package and stage gates.

The user approved the proposed bounded early-activation experiment within R01. Investigate activation before Unity's global MonoScript catalog initializes. First identify an actual owned-runtime entry point, establish native/managed service readiness and lock/reentrancy conditions, and prove successful and failed activation behavior. Preserve the strict early-use guard and all historical evidence. The production M09 signing/download/LKG/health/deployment coordinator remains outside this experiment.

The user declared a target of **up to 64k assemblies**. Use **65,536** as the conservative count boundary until clarified. This target exceeds the current encoding profile's best-case fresh small-image capacity of 338, so **R01B is mandatory after R01**. It is no longer contingent on accepting the five-image demo as a production target. The allocation domain (ordinary plus Shadow images), maximum DLL size, size distribution and required headroom remain to be specified; a clarification is pending while R01 proceeds. No claim of 64k support follows from this authorization.

Order remains: complete R01 implementation/tests/evidence/stage review, then execute R01B with its full encoding ADR, actual metadata-range and lifecycle evidence, then **stop at H1** for human full review. This approval does not pass H1 or authorize R02.

The first diagnostic experiment should avoid changes to the current production source while testing the real native activation APIs on the retained immutable Player. If a debugger-assisted bridge is used, record its source/build hash, exact Player identity, native function addresses, input hashes, invocation boundary and limitations. It is feasibility evidence, not a substitute for a fresh source-pinned ON/OFF Player pair and strict acceptance matrices.

Strict14 completion and original raw hashes are recorded in [early-v6-m07-aggregate.json](early-v6-m07-aggregate.json). The stopped ordering-failure attempt remains preserved; all 140 restart-sealed raw Player files are unchanged.
