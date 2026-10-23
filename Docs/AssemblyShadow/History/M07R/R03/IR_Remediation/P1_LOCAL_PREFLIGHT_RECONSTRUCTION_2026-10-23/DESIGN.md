# R03 P1 — Immutable Local collector reconstruction correction

## Authority and observed defect

The latest Local result '20261022-e1e5' is **Blocked / PrerequisiteBlocked** at demo 19de9dd4d1040aeb2b72b4e3fe0f89b18df94696, native e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb, hybridclr 4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity 948c0e3b4f8891481301770115e8ba4945eea6de. Its Local-owned, independently written 57,332-byte provenance helper failed at frozen CPP reconstruction before INVOCATION.json or the 25-child core batch. **Zero** tests/compilations in that new cycle were invoked. The separate 7896 PASS, 7c2c PASS and 82dd raw FAIL remain immutable.

The archived early opaque CPP reconstruction does not strip the *new* source-authenticated admitted_include. The analogous early API reconstruction does not strip admitted_decl. The later owned-physical-names reconstruction already strips both. The Local-owned FINDING.json records the original two frozen blobs, exact residual bytes and read-only restoration. This is a **collector prerequisite defect**, not evidence of native production source regression.

## Chosen correction and boundaries

Publish one **Primary-owned, deterministic collector preparer**, not a mutation of the consumed Local helper. The checked-in tool is Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py. On a fresh Local run it reads the exact historical failed run-once.py and audit.py *from the committed e1e5 checkpoint*. It requires the failed helper SHA256 73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd and the immutable Git bytes at demo 050a086304ac81b5680c6b4a9ae237418e492464. It refuses missing, duplicated or previously rewritten source anchors.

Its **only two generated collector changes** are:
1. Early opaque cpp_without_live reconstruction removes exactly native verifier literal admitted_include before the previously required integrated JSON, shape and live additions.
2. Early opaque API reconstruction removes exactly native verifier literal admitted_decl before the previously required integrated JSON, shape and live declarations.

Both formerly correct later owned-name removal expressions, frozen opaque Git blobs 53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2 / 32956c2c4084951131b497c1201712a0d4fe11b3, all old historical revisions, twenty Git postflight operations, 25 components, 85 original tests, eight inventories, 100 official SDK syntax configurations, compiler modes, and limits remain unchanged. No rebaseline or relaxation.

Before any new directory is created, preparer verifies four clean local branch/commit pins and demo Docs-only ancestry from code anchor 117cc6b1c2be8050cd2f433ef17db8b3c5138f93; every file in the immutable e1e5 checkpoint's 42-entry SHA256 manifest; both current native CPP/API equal the 82dd source plus *exactly one* admitted literal and match the old Local finding; both distinct native verifier scripts publish identical literal values; original frozen blobs match historical SHA256; and all four new roots are absent, canonical, pairwise disjoint. Then it exclusively creates the fresh preflight root containing corrected run-once.py, the **unchanged** archived independent audit.py, generated exact-source EXPECTED.json, and PREPARATION.json with sha-bound proof. It does **not** launch the batch, a compiler, Unity, or the audit. The original blocked checkpoint remains untouched; postflight --verify-after independently verifies its 42 files and generated helper hashes and writes BLOCKED_HISTORY_AFTER.json, once.

Independent Local admission is mandatory *before* preparer execution. The preparer cannot self-approve the evidence; the later Local collector/audit must independently execute and publish actual observations. On failure, retain partial/raw state and STOP, without repairing scripts or trying a new root.

## Scope and exit

One fresh Local P1 source/host/installed official Unity2022.3.62f2 SDK **syntax-only** batch, with 25 separately receipted components, original 85 tests, nine new strict+sanitized groups, eight inventories, five genuine managed positive outputs + original compiler-negative, 100 native syntax invocations, 20 final Git authority commands and four exact clean remote heads. The original audit and new history-preservation receipt must succeed for a scoped PASS.

No new native production edit, active getter redirect, normal Player/Editor/IL2CPP product link, full metadata Shutdown/GC/RSS/latency experiment, protected SNAP-01, H2/X02/M08A or Human Review Gate. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; P3 Incomplete. R03Accepted=false, ReadyForHumanReviewGate=false and PureInterpreter disabled.
