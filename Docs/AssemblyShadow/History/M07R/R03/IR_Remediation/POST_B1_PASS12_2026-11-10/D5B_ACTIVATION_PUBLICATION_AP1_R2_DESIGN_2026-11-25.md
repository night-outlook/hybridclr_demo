# D5-B AP1 R2 — commit-header topology correction

**Client date:** 2026-11-25 America/Los_Angeles. Historical UTC labels remain unchanged.

**Status:** Focused Primary source-only design addendum. R2 implementation evidence, exact-source CI and separate independent rereview are pending; this document assigns no review verdict.

## 1. Reason for the return

The [independent AP1 review publication][review] at demo `6d0a5d1613c483119b41d774765ef9752adb7732`, report Git blob `9065580fc26868b1c76b773348657564150c6741`, assigns `D5BActivationPublicationAP1IndependentReview=ReturnRequired` for **D5B-AP1-IR-01**. Its reviewed implementation was `25551bca385c5af20c417110ad1ee27593a3eefc`; the review-publication commit is not that tested source.

The original `_Git.commit` scans the complete header block and collects every top-level `parent ` line. Git recognizes topology from the initial tree header and immediately following contiguous parent headers. The review demonstrated a stored commit with a later parent-named header that Git treats as having no parents, while AP1 reported `runnerSoleParentIsSource=true`. Both ordinary object storage and a strict Git object check succeeded. Correct object type and hash, or successful `git fsck`, therefore cannot establish that AP1 interpreted parentage correctly. [Independent report §§6 and 10][review]

R2 corrects this parser contract only. The review accepted H/E/A/Q constructibility and preserved R5's `PassDryAdmissionSourceOnly`; neither is reopened.

## 2. Supported commit grammar

The shared parser will accept a strict, unambiguous subset of commit headers. It need not accept every object Git can store. Object-type, exact-byte hash and header/message-boundary checks remain prerequisites.

| Region | Required interpretation |
|---|---|
| First header | Exactly one initial `tree <40-character lowercase hexadecimal object ID>` line. No metadata, parent or continuation may precede it. |
| Parent prefix | Consume only the immediately following contiguous `parent <40-character lowercase hexadecimal object ID>` lines, preserving order and cardinality without sorting or deduplication. |
| Metadata | The first non-parent header permanently closes the parent prefix. Supported metadata has an ASCII field name, a space and opaque value bytes. A later top-level `tree` or `parent` structural header is rejected, including a second tree or a parent list resumed after metadata. |
| Continuations | A leading-space continuation is supported only after a metadata header. Its contents cannot introduce or reopen topology. Orphan continuations after tree/parent headers and other unsupported layouts fail closed. |
| Message | Everything after the first blank-line separator is message content. Tree- or parent-looking message lines have no topology effect. |

Structural fields must satisfy their exact syntax; malformed identifiers, structural prefixes and duplicated or misplaced tree headers are not repaired or reinterpreted. Metadata values and continuations remain opaque bytes rather than requiring the whole header block to decode as UTF-8. This is a topology parser, not signature authentication or a complete validator of all Git metadata semantics.

Both source H and runner A pass through this same grammar. H may have an ordinary root, linear or merge parent prefix. The existing runner rule remains stricter: A's parsed parent tuple must be **exactly `(H,)`**. Multiple genuine prefix parents are a parent list, not metadata; they cannot satisfy the sole-parent rule.

After parsing either commit, use the same sanitized read-only Git path for `rev-list --no-walk --parents <oid> --`. Require exactly one row whose tokens equal `[oid, *parsedParents]`. Reject inconsistent or unsupported effective local topology, including shallow/graft views that change parentage. This bounded agreement observation does not walk history, authenticate signatures, grant authority or provide a namespace lock.

## 3. Focused regression and evidence plan

Retain all **18 existing AP1 methods** and the entire **94-method R5 suite**, including existing helpers and assertions. Append real stored-object regressions; normal `commit-tree` construction alone cannot express the uncovered distinction.

The focused cases must exercise both source and runner parsing, including a late parent after ordinary metadata, misplaced or duplicate tree headers, interrupted parent prefixes and malformed structural fields. Positive controls must retain ordinary root/linear/merge source parsing and the valid direct-child runner relationship. Supported metadata continuations and message text containing tree/parent-looking strings must remain non-topological.

For accepted topology, compare the parser's parent tuple with Git's own parent observation. Include a real temporary shallow/graft mismatch control. For the review's late-parent shape, require rejection even where ordinary storage or strict object checking accepts the bytes. Keep the observed Git parent list, parser/auditor disposition and object-check result distinct; a successful integrity check is not a substitute for the parent comparison.

Primary will record preservation checks, actual appended method inventory, exact tested source, host results and fresh CI run/job/raw-log evidence. Workflow counts and summary receipts must match the completed suite. No new test count, source commit, successful run or independent closure is claimed here. Separate independent rereview must adjudicate D5B-AP1-IR-01 against the corrected source.

## 4. Preserved scope and authority

The [AP1 H/E/A/Q design][design] remains unchanged: source H and runner A are frozen; E excludes A/Q; later approval and handoff publication belongs to separate Q, whose own hash is resolved externally. Canonical source-ref binding, exact closed proposal schema, literal writer/envelope binding and the two-path tree-delta restriction remain required.

R2 does not implement fifth-runner custody, imported-module closure, new plan/adapter authorization semantics, Q approval validation, live remote qualification or physical admission. Those remain concrete future Primary tasks. The preserved R5 namespace limitation also remains: unresolved-creation no-adoption behavior does not prove protection against every replacement after recorded mkdir or after a final identity observation.

The R5 writer, plan, wrapper, preflight and existing test bytes remain preservation requirements. Both production approval constants remain `None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All 18 real D5 Player cases remain `NoCoverage`; candidate Local/macOS, Unity, IL2CPP, Bee, native VM, Mach-O, GC, PID and Player validation remain `NotRun`.

This addendum grants no user approval, activation permission, Local handoff or later-milestone authority. Stop at focused Primary parser remediation, its evidence and separate independent rereview.

[review]: https://github.com/night-outlook/hybridclr_demo/blob/6d0a5d1613c483119b41d774765ef9752adb7732/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_2026-11-25.md
[design]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md
