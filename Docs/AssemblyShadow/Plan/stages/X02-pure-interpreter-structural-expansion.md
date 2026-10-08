# X02 — PureInterpreter structural-expansion qualification

Status: **Deferred; not authorized to start.** Owner D1=A (2026-10-08) moved the unproved private-reference add/remove and other changes outside NativeLayoutAdmissionV1 out of bounded R03. X02 is separate from X01 assembly Add/Remove and is not automatically opened by a passing R03/H2.

## Goal

Define, separately review and experimentally prove a narrowly eligible PureInterpreter type-domain capability. Existing NativeLayoutAdmissionV1 checks remain authoritative; static `R03PureInterpreterEligibilityV1` reports are **screening only**, never an admission certificate.

## Preconditions before an experiment

1. A separate explicit owner authorization and gated design for a concrete type/domain profile.
2. Exact four-repository/runtime/Unity pins plus baseline and target source, compiled DLLs, resources, type graphs and hashes.
3. Independently reviewed proof of no pre-existing baseline objects/usage and no unresolved Unity/native/serialization, fixed-AOT concrete consumer, generic/value ABI, boxing, reflection/delegate, or interop exposures. Mixed domains use the union of constraints.
4. Explicit expected rejection for missing or contradictory proof, plus preservation of ownership, single-publication, staged-private and failure-state invariants.

## Future implementation and evidence

- Real-DLL positive/negative field-change fixtures with method/type identities, metadata layout and native allocation facts.
- An explicit, opt-in capability boundary; no marker-only bypass or blanket removal of physical admission checks.
- Fresh source-bound IL2CPP Player observations for staging, validation, publication, allocation, field access, constructed generics/interop as applicable, old handles and negative rejection paths; resource ABI and ordinary-role regressions.
- Independent design → plan → implementation → evidence review, then a separate owner go/no-go for any supported expansion profile.

Until all those conditions are met, `qualificationApproved=false`, `expansionAuthorized=false` and `authorizesExpansion=false`; unsupported cases remain rejected or NeedsProof. D1=A is not X02 initiation or approval.

See [ADR-0002](../../Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md), [R03 stage](R03-evolution-semantics.md), and [owner disposition](../../History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md).
