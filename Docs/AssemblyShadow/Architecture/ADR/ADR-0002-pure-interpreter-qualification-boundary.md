# ADR-0002 — PureInterpreter qualification is evidence, not runtime authority

Status: Accepted for R03 preparation (2026-10-03); amended by owner D1=A on 2026-10-08. Static classification remains non-authorizing, and structural expansion is deferred to X02.

## Context

R03 step 3 requires a qualification boundary before experimenting with layout changes that conservative `NativeLayoutAdmissionV1` does not support. A static classifier alone cannot prove absence of existing baseline objects, fixed AOT/native consumers, dynamic reflection/interop use, or runtime ownership/failure-state requirements. Conversely, resource compatibility and a managed assembly name are insufficient evidence for physical-layout safety.

## Decision

`R03PureInterpreterEligibilityV1` is an **analysis-only qualification input**. It never changes `NativeLayoutAdmissionV1`, never stages or loads an assembly, never runs business code, and is not consumed by the runtime as an admission certificate.

The report is byte-bound to the installation baseline and complete target compiled sets, their loaded metadata/reference graphs, resource descriptor, changed roots, conservative closure and target load order. It classifies each concrete type across the union of these domains:

- `PureInterpreterCandidate`;
- `UnityBound`;
- `AotInteropExposed`.

Unknown or contradictory evidence produces `ExcludedOrNeedsProof`; it cannot produce affirmative authority. Static candidates remain `StaticCandidateNeedsRuntimeAndReview` and require the report's complete proof list.

The implementation must treat at least these as exclusion/NeedsProof signals: serialized/resource references, Unity native inheritance, value representation, open/closed generic boundaries, pointer/byref/modifier or native-callable ABI, fixed/ordinary concrete consumers, unresolved assemblies/types/base chains, dynamic reflection/Activator/Marshal consumers, and source/descriptor mutation.

Every report and per-type row retains:

- `authorizesExpansion=false`;
- `runtimeProofExecuted=false`;
- `qualificationApproved=false`;
- `expansionAuthorized=false`.

The shipping/default profile remains conservative. Private-reference addition/removal and other structural expansion remain disabled.

## Qualification boundary

Expansion experimentation may be designed only after all of the following exist for the intended type/domain:

1. complete installed/target inventory and exact source binding;
2. proof of no existing baseline object/use that would cross the changed representation;
3. no unresolved fixed AOT, reflection, native, interop, generic, delegate, value-representation, Unity/resource consumer;
4. correct prepublication owner/failure-state behavior;
5. independent qualification review;
6. explicit owner approval for the experiment;
7. separate pinned Player evidence for the proposed expanded operation and its rejection boundaries.

A qualification report does not satisfy items 2–7 by itself. R03 batch I validates the report, binding, resource/runtime regressions and existing conservative behavior; it **does not approve structural expansion**.

## Consequences

- Resource ABI success cannot bypass native layout admission.
- A marker or assembly classification cannot bypass ownership/physical guards.
- Failure or partial staging cannot leave usable qualification authority.
- Later approval, if any, must be a new source-bound decision/evidence record; historical H/I evidence is not retroactively broadened.
- If R03 concludes without expansion, the conservative support scope remains valid and the unapproved expansion work stays explicitly out of scope rather than silently becoming supported.

## Owner-approved R03 scope boundary — 2026-10-08

D1=A limits R03/H2 supported-layout claims to the existing NativeLayoutAdmissionV1 envelope. The qualification steps above specify **future X02 entry conditions**, not evidence that private-reference add/remove was achieved in R03. See [deferred X02](../../Plan/stages/X02-pure-interpreter-structural-expansion.md) and [recorded owner disposition](../../History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md). Every static report remains analysis-only, with all authorization flags false; the native/resource/ownership checks and rejection behavior are unchanged. Independent full-stage review must judge this bounded claim; no H2 or later milestone is approved.
