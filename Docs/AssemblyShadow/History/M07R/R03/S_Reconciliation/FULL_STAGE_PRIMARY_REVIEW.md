# R03 — stage-wide Primary assessment after S

## Review status

**Primary assessment completed for the scope described here; independent stage verdict NotRun.** This is the implementation owner's design/plan/source/evidence assessment and a preparation record for independent review. It cannot satisfy RC6 by being renamed independent. No R03, qualification, Human Review Gate or release approval is issued.

Read [PRIMARY_RECONCILIATION.md](PRIMARY_RECONCILIATION.md) for execution and transport identities. All conclusions below refer to demo evidence publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, actual S demo `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`, native `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, and IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

## Method and coverage of this assessment

The governing sources are `Plan/DESIGN.md`, `Plan/stages/R03-evolution-semantics.md`, `Plan/stages/R03-remaining-completion.md`, ROADMAP, EVIDENCE_CONTRACT, HUMAN_REVIEW_GATES and ADR-0002. The decomposition does not replace the original exit conditions. The assessment read these requirements, representative cross-layer implementation and declared test matrices, the Local return, selected bound receipts and the byte-audit results. It did not manually review every captured source line, execute a new Unity/Player, reproduce all negative controls, or perform a separate-agent adversarial review.

Representative source review included package `Metadata/PureInterpreterEligibility.cs`, `LogicalMethodIdentity.cs`, `NativeLayoutAdmissionValidator.cs`; IL2CPP+ `libil2cpp/vm/AssemblyShadowTypeResolver.cpp` and its header; the focused `R03/player-cases.json`; and the documented source/authority/consumer call chains integrated by S. The complete source and raw evidence remain the independent reviewer's inputs, not merely this summary. Two oversized source-capture omissions must be resolved directly from their pinned repository versions if relevant to the independent review.

## RC1–RC6 exit matrix

Evidence paths below are relative to `History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/` unless noted. A passing witness is deliberately narrower than a universal capability claim.

| Obligation | Source and evidence examined | Primary disposition |
|---|---|---|
| RC1 — eligibility/qualification and supported scope | Package PureInterpreter eligibility and native-layout admission; static qualification cell; capability/layout audits; fixed-AOT rejection matrix; ADR-0002 | Static qualification and prescribed negative controls have evidence. Qualification approval and structural expansion are not established. Original step-3 scope needs an explicit owner decision, not an inferred waiver. |
| RC2 — original-resource regression | Source-catalog fixture, original M07 entries/ABI/resource checks; six builds; resource 755-case roster; 14 resource Players; `preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json`, resource aggregate | Prescribed resource-complete S regression passes. Historical focused M01 NoCoverage stays historical; this is not blanket retroactive M00–M07 acceptance. |
| RC3 — runtime identity and compatibility | LogicalMethodIdentity, physical/native type resolver and admission boundary; 23 focused Players; resource/runtime and execution supplement; `PRODUCER_RUNTIME_AUDIT.json`, `COMPLETION_RUNTIME_AUDIT.json`, `LAYOUT_IDENTITY_AUDIT.json` | Named supported/rejection witnesses pass. This does not establish arbitrary structural evolution, all generic/interop combinations or universal old-reflection-handle remapping. Independent review must verify each broader plan claim against a named assertion, not aggregate counts. |
| RC4 — installed-baseline generation, closure and roles | P01–P05 production integration, actual graph bindings, fresh restored compiler snapshot; `INTEGRATED_DETAIL_AUDIT.json`, `LO_REPAIR_AUDIT.json`, `LP_REPAIR_AUDIT.json` | The prescribed integration and empty restored roots/closure pass. Existing generation/role host proofs remain separate; no second publication in one process or production recovery coordinator follows. |
| RC5 — impact regression and performance/memory protocol | Fresh startup/capacity/rejection/resource/measurement contracts; `batch/measurements.json`, `COMPLETION_RUNTIME_AUDIT.json`, storage audit | Bounded unfenced-development observations and diagnostic correctness pass. Production SLA/noise, all optional comparison controls and deferred CPU/RSS risk closure are not inferred. Explicit claim/scope disposition remains required. |
| RC6 — freeze and independent stage review | Frozen quartet, source delta, byte-authenticated archive, this matrix and separate review request | Preparation and Primary reconciliation exist. Separate independent review is NotRun; Human Review Gate readiness and H2 remain false. |

The historical G03/G04 installed-baseline/deleted-edge and G05/G06 ordinary-role proofs are not described as absent. S integrates the prepared call chains; the independent review must still trace safety closure separately from target-only load order and verify actual installed/target bytes. Host positives alone are not fresh runtime proof.

## Design-to-source observations

### Type domains, physical layouts and qualification

PureInterpreter, Unity-bound and AOT/interop-exposed domains must retain the union of their constraints. Static analysis can establish a candidate's declared eligibility or explicit NeedsProof/rejection, but cannot make an existing AOT value representation, native allocation or Unity serialized layout safely expandable by declaration. The inspected qualification boundary remains non-authorizing, matching the unchanged false flags.

The distinction matters for interpreting the focused matrix: an AddType or incompatible value/base/layout case expected to reject is evidence that its rejection boundary works, not proof that arbitrary new structure is supported. Proposed private-reference field addition/removal beyond the admitted fixed-AOT envelope needs the original qualification decision and its own publication/allocation/access evidence. Add/Remove assembly support is a separate X01 capability and is not approved by this review or the RC1 decision.

The native type resolver and layout validator form a necessary second boundary beyond host/metadata comparison. Independent review should challenge actual staged versus active identities, baseline-use detection, private visibility and poison/terminal states. S's physical witnesses are concrete empirical support; they do not remove the need to examine every bypass path in a separate review.

### Logical method identity versus physical artifacts

The inspected method identity code uses a canonical declaration/signature identity, rather than treating a physical metadata token, slot or simple name as a stable cross-version method identifier. Concrete generic construction and native/managed physical identity remain separate obligations. Changing this distinction would undermine moved-slot, delegate, reflection or interface dispatch even when assembly names match.

S's supported call paths and explicit rejection controls provide evidence for the prepared fixtures. They do not license execution through an obsolete AOT method or establish universal remapping of unsupported FieldInfo/PropertyInfo/EventInfo or interop wrappers. For each claim about constraints, byref/modifiers, generic construction or stack traces, independent review must identify the exact source assertion and actual observation; an unbound claim stays Unproved rather than being filled from the test count.

### Producer/consumer boundaries and cumulative integration

The historical O/P/Q/R returns exposed different harness boundaries, not one continuously failing runtime feature: source-policy versus linked-policy authority, codec context, canonical DLL lookup, image-record shape, initialization order, versioned type-info consumption, storage admission and cleanup versus remote acceptance. The current acceptance case is S's complete source-bound execution, not a synthetic union of earlier partial passes.

The strict R02 bridge validates the known extension before in-memory legacy projection; it is not permissive unknown-field handling or an evidence rewrite. S records consumption at per-resource, positive startup and aggregate entry points, with OFF zero consumption and negative startup no business handoff. The recorded current fixture counts are 17 objects per ON/positive case and 221 ON objects at aggregate; these counts aid custody and do not replace semantic assertions.

The installation-baseline comparison must not be replaced by previous-patch comparison. Empty roots/closure in the restored target is a distinct fresh compiler/integration result, not inferred from restoring ProjectSettings. P01–P05 byte bindings and actual target order remain part of the evidence.

### Cleanup, remote authority and environmental readiness

The LR repair separates authorization to clean up an owned local transaction from acceptance of a new runtime result. Exact local roots, HEADs, source/backup bytes, generated pins, transaction identity and producer receipts remain required. Fresh remote acceptance is checked after cleanup; its failure still fails the cell. This distinction prevents a transient transport error from being the first operation on the restoration path without pretending local state proves the remote tip.

S exercised the actual successful production restore, exact original-byte restoration and subsequent fresh remote check. R remains quarantined, staged and historically Failed. No filesystem/transport cause is reconstructed from later successes. Storage admission, periodic observations and Git receipts improve failure evidence; they neither reserve capacity nor guarantee continuing connectivity. No crash-atomicity, complete concurrency tolerance or retry/resume service is claimed.

## Findings and owner-controlled closures

**S-SCOPE-001 — RC1 scope/qualification remains unresolved.** Classification: acceptance/scope obligation, not a new S runtime defect. The original plan requires qualification before structural expansion or an explicit reviewed decision to defer it. All approval/expansion flags remain false. Closure requires the owner choice in OWNER_DECISIONS.md and the corresponding reviewed plan/ADR or implementation/evidence. This report alone changes neither.

**S-CLAIM-002 — RC5 evidence is not production performance acceptance.** Classification: claim/risk boundary. The 12-process measurement protocol supplies current-profile observations, not an approved SLA, noise/overhead threshold or acceptance of deferred R02 CPU/H1 RSS risks. Failed contaminated certificates stay Failed. Retain diagnostic-only claims or commission the explicit missing production controls before making broader claims.

**S-REVIEW-003 — independent full-stage verdict missing.** Classification: process/evidence blocker. The current host did not invoke a separate independent reviewer. The machine byte-audit's name does not change that. The pinned project config disables automatic reviewer invocation; it does not waive the explicit user and R03-stage review requirement. No helper outcome/effective identity is fabricated and no configuration is changed. A separate read-only review must cover design → plan → implementation → evidence and return its own verdict and findings.

No additional S cell failure or specific unobserved product bug is alleged by these items. Equally, absence of a newly demonstrated bug in this Primary assessment is not an independent release-correctness verdict.

## Exit recommendation

Keep S reconciled as the complete prescribed empirical PASS. Do not repeat its expensive batch solely to fill an administrative handoff. Complete the separate independent review and explicit owner scope decisions next. Any substantive finding returns to Primary for a minimal in-scope fix, source-bound impact tests and re-review; a future runtime batch needs a new exact handoff when actually justified.

No production or agent configuration rollback is required by this assessment. A later corrective change must be a reviewed forward commit, never a reset, discarded evidence or relabeled negative. `R03Accepted`, `H2Passed`, `qualificationApproved`, `ReadyForHumanReviewGate`, `fullLegacyRegressionAcceptance` and PureInterpreter expansion remain false. H2 is separately human-initiated after R03 exit closure; M08A and later work remain unauthorized.
