# Independent M00 acceptance

Verdict: PASS, 2026-08-27.

Reviewer: `/root/m00_acceptance_gpt56sol_high_1`, independent read-only
code-reviewer (gpt-5.6-sol/high). This is the explicit milestone review required
by the plan; the repository's optional configured gate-reviewer mode is Off.

## Immutable reviewed boundary

| Repository | Base | Reviewed target |
| --- | --- | --- |
| demo | 8b8d60e77b998a6dbc0c6a508b8d36a46feec2b3 | 738fdf0cbaeb1c0f75ae7b55c5ef82c77b42b1ec |
| package | fd32708e7f5106f0ffa375bcfe43342ee594c1e5 | 9b32d91a7b97cb3a7f875f342b2a9173125364ef |
| il2cpp_plus | 11251b938d2ce7fa865165130bf257ca239db69f | bb3bfbad1405c42ea353eafda92a03b91bffb564 |
| hybridclr | unchanged | 210cbe0ecc878a6ab7e392b1ce191a46d509ba25 |

The reviewer independently confirmed the strict source verifier (921 source
files, 923 installed files, exact demo inputs), raw log/artifact/receipt hashes,
ARM64 binary, actual Player assertions, and native preprocessing for default
zero, explicit one, and invalid two. The installer/cache safety review found no
blocking defect. The reviewer did not rerun Unity or the fixture suite that
creates temporary repositories; those executions are the main-agent evidence.

The PASS retains the report's platform, live-debugger, headless-rendering and
allocator-shutdown limitations. It is not a claim of Windows/Android or visual
coverage. M01 must still collect real native resolution traces.

## Administrative closeout

The reviewer expressly approved a review-record-only commit and local baseline
tags after PASS, with no executable/source changes. The demo tag points to the
commit containing this closeout. The other three tags point to the reviewed
targets above. The demo build-source pin remains
2c886877c9e19bbb8f10aa8efeb0786903d73193.

Tag name in all four repositories: `assembly-shadow-m00-baseline`.
No commits or tags are pushed by this task.

Main-agent preservation audit: the original demo's three dirty-file hashes
remain unchanged and its pre-existing Unity Editor PID 13313 was preserved.
