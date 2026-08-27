# Independent M01 and full-goal acceptance

Verdict: PASS, 2026-08-27, for the M01 **CONDITIONAL-GO** PoC and the substantive
user goal "finish M00 and M01". Unconditional GO and production readiness are
not approved.

Reviewer: `/root/m01_acceptance_gpt56sol_high_1`, independent read-only
code-reviewer (gpt-5.6-sol/high). This is the explicit milestone review required
by the plan. The repository's optional configured gate-reviewer mode is Off.

## Immutable reviewed boundary

| Repository | M00 base/tag | Reviewed M01 target |
| --- | --- | --- |
| demo | 37dc94785b0734ebae1784c0ade110c57a617ea9 | 283fbe409f1790c4db634e8c414b360ec95c2c89 |
| hybridclr | 210cbe0ecc878a6ab7e392b1ce191a46d509ba25 | 1bc69c3acc2434804e71560418df8c728a63360e |
| hybridclr_unity | 9b32d91a7b97cb3a7f875f342b2a9173125364ef | a1d2697dfa3b1c510d5bfe5cf5e513886a3af78a |
| il2cpp_plus | bb3bfbad1405c42ea353eafda92a03b91bffb564 | 03a450c73b5c5db2ed6f87dc4f194788fd204567 |

Demo build-source pin: 323bbf9855a4ef1c893662ac55034d5f780f2bd7. The target above
adds only source-pin/evidence metadata. The original M00 independent PASS is
preserved in [M00-review.md](../Baseline/M00-review.md).

## Findings and independently checked evidence

No actionable blocking issue remains within M00/M01.

- The reviewer inspected the four-repository source diffs, business and
  serialized script bindings, patch/semantic comparison, Bootstrap, and native
  implementation. There is no renamed assembly, AOT Host, component replacement
  or object-header rewrite circumventing the feasibility test.
- Both read-only verifiers were independently rerun successfully: default
  strict installed-source verification (923 source files, 925 installed files,
  demoSourceVerified=true) and the complete six-mode M01 artifact verifier.
- Actual native events prove shadow resolution before allocation and physical
  shadow objects for the old prefab, scene and reload. The stale baseline
  comparison targets and bounded query-target mapping are explicitly visible.
- The recorded constraints accurately distinguish this successful fixture from
  general type/cast/reflection/cache consistency.
- M00 implementation/evidence are unchanged, its four baseline tags retain the
  expected targets, and its accepted native binary still matches SHA-256
  6394bc2c8027d0dd4e1334b22d1dcaf9f8a8896eb231f02c934edd5bd8baddef.
- The reviewed task worktrees are clean. Main-agent checks also rehashed all 53
  inventory artifacts and all 29 archived raw JSON copies successfully.

The reviewer did not launch Unity/Players or rerun the temporary-repository test
suite. Runtime executions, five Editor checks and 34 Python tests are main-agent
evidence; the reviewer inspected their relevant code/results/logs. The NUnit
wrapper was compiled but not separately executed by Unity Test Runner. The new
native-OFF API stubs were source-reviewed, not directly invoked by the ordinary
M00 regression harness.

## Conditions retained by PASS

- Activate before business use; only the tested Bootstrap-then-bundle ordering
  is accepted. Pre-created AOT objects do not become safe or change their class.
- Unity still holds baseline cached classes. The one-pair, nongeneric query
  target map does not establish global cast/type/reflection/cache coherence.
- Stage immediately registers interpreter metadata. Transaction isolation,
  failure cleanup, Usage Guard, wider assembly/type and execution semantics,
  and remaining Unity APIs stay in the documented M03-M07 backlog.
- Coverage is Unity 2022.3.62f2 macOS ARM64, headless, exact P01. Windows/Android,
  visual behavior and live debugger launch/attach are unvalidated. Known
  headless shader and allocator-shutdown diagnostics remain disclosed.
- M02-M12 and full product acceptance criteria are outside this completed goal.

## Administrative closeout

The reviewer expressly permits a review-record-only closeout commit and local
annotated `assembly-shadow-m01-poc` tags identifying CONDITIONAL-GO, followed by
a small final metadata/tag/preservation recheck. No executable changes are
covered by that allowance. The demo tag designates this review-record-only
closeout; the other three tags designate the reviewed targets above. The demo
build-source pin remains unchanged. No commits or tags are pushed.

Main-agent preservation audit: the original demo remains at
8b8d60e77b998a6dbc0c6a508b8d36a46feec2b3 with its original three dirty files:

| File | Preserved SHA-256 |
| --- | --- |
| Assets/Settings/Renderer2D.asset | 2eee53b1cb41185b0648a570ed28a65070935fb6bab6400d2a0f4247dc968818 |
| Assets/Editor.meta | bcf6c7bb48d2a7ef4aeecfeb696cb6b23303593923c8e73ada2e1f9bd3c40594 |
| .DS_Store | e516642a8e6803cc7f2ad6a77332b0384689690d14126cd02adec8009215767f |

Its pre-existing Unity Editor PID 13313 remains running and was not controlled
or stopped. The independent final administrative recheck is reported in the
task's review response after tags exist, without another executable/source edit.
