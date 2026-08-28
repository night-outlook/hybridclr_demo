# M05 active types, reflection and cache evidence

Status: M05 is not accepted. Source/tooling validation is in progress; no M05
Player, fixture replay, complete runtime matrix or final milestone gate is
claimed. M06 remains closed. This working record must be completed with the
actual immutable executable pairing and runtime evidence before acceptance.

The [type contract](M05-type-contract.md) and
[raw-query contract](M05-raw-type-admission.md) govern implementation and the
acceptance boundary. The operator sequence is in
`Tools/AssemblyShadow/README.md`.

## Native/runtime source readiness

The bounded native/runtime source pairing is:

- hybridclr: `7f0da36e1a978abfd22c2c195ecb2741588a5d69`.
- il2cpp_plus: `8ceb7e40abe458dce5343bedaf250333ef9433a1`.

The independent native/runtime reviewer returned PASS for source readiness
only. The main readiness receipt is
`_temp/AssemblyShadow/M05NativeReadiness-KERPwUl0/native-tests.json`, SHA-256
`bf0a94c406d606ea39a69c8aa47ddbfa0d623165ac1ba1507b6a781ebb0a3c72`.
It records 32 ON/OFF syntax checks, eight 62-check ASan core runs, reflection
ON 31/OFF 3, disabled type-info 2, and 148 zero-exit commands with 1,094
unchanged transitive inputs. Its physical metadata/interner/GC/exception seams
do not establish real Player cold initialization, resource binding, concurrency
or performance. Installed-runtime verification remains a separate requirement.

Early preserved regressions against those current source HEADs are under
`_temp/AssemblyShadow/M05PreservedNative-bG7Z2yNM`: M04 passed 53 resolver,
24 reference-identity and 22 ON/OFF syntax checks plus one million lookups with
zero counted allocations; M03 visibility passed 18,674 checks. These receipts
truthfully retain the older configured pins/generated-header provenance and
are not a claim that the new source pairing is installed.

The first preserved M03 parser run crashed in its facade lookup adapter: the
production M05 lookup now calls `ResolveClass`, but the old dynamically linked
test executable supplied only its identity `ResolveImage` adapter. The updated
adapter explicitly counts identity-only class resolution without emulating a
transaction or active type mapping. All original assertions remain, with two
additional assertions proving one class-resolution call on general lookup and
none on the physical approved-facade path. The rerun passed 23,027 identity,
30 name, 25 facade, 15 facade-lookup and 27 disabled-API checks; all 1,005
transitive inputs remained unchanged. The failed and corrected receipts are
both retained. No production native fix was needed for this harness gap.

## Compiler and initial Editor evidence

Fresh Unity Player compilation generated and verified all 25 raw-query
declarations in `_temp/UnityExec_20260827_234010.log`; compiler output is
`_temp/AssemblyShadow/M05RawAdmissionCompiler-89e37e21e43a4d6a96f9b3865bd03ea2`.
Configuration byte SHA-256 is
`d47806dc47b699aa3fb0ece4f285a158e4677e4b40c9ae23fb448929a7bed8a8`;
the separate canonical configuration hash is
`82a05bf1e0bdf822a42458bf3b47fd67b5d99e24113fe5173aeef091f7ac53f8`.
The independent Python decoder agreed on five method fingerprints and all 25
literal receiver chains. These are compiler observations, not linked proof.

The first complete Editor run passed 617/618. Its sole failure was an obsolete
assertion requiring exactly nine public APIs. M05 intentionally adds a tenth;
the correction checks the exact ten-name inventory and retains error-code,
out-parameter and non-simulating Editor behavior checks for every operation.

The corrected full run passed 618/618 with zero failures/skips under
`_temp/AssemblyShadow/EditorTests-d5dbe8ae236f49439bcd088db0939a60`.
Results XML SHA-256 is
`60eae842827b7d5fb554df6ec7c38cede7abf3fc4323138272c897cf1a7b6e54`.
The full Python suite passed 210/210 in 28.768 seconds. These results precede
the following newly added regressions and must be rerun after their fix.

## Raw-admission dependency correction (corrected source awaiting re-review)

Independent review of package `7d37b38e66f57ecacca1b7e322cdd005c06911fc`
returned FAIL for a confirmed provider-broker gap. An emitted outside runtime
DLL calls an admitted Bootstrap helper returning candidate types; policy
accepted it while the graph contained only Outside-to-Bootstrap, leaving
Outside out of the candidate's reverse closure.

Six actual-byte regressions reproduce the missing rejection: direct caller,
same/cross-Bootstrap forwarding, literal reflection, delegate access and type
token access. All six fail at the expected policy assertion; the five original
loader-policy tests pass. The chosen repair propagates finite provider
selection requirements and rejects unsupported callable-selector exposure,
including interface/virtual registration and forwarding delegates. It does
not replace raw observations with generated expected types or prohibit generic
already-selected type/diagnostic/iterator plumbing.

The corrective package commit is
`c8d0f725d2fb3ea8462b97c84b6fd7ff12a196b8`. Its four-file slice adds the
bounded selector propagation analysis, integrates it into compiled policy and
adds actual-byte positive/negative regressions. It requires truthful candidate
dependencies for outside callers and rejects unsupported selector tokens,
delegates, reflective ownership and interface exposure. Selected-value field
analysis follows actual IL operands/locals rather than rejecting innocent LINQ
cache stores merely because the same method performs a raw query.

The focused package aggregate passed 136/136. A diagnostic check of the actual
fresh compiler output passed 25 admissions across 36 runtime modules, including
the real private forwarder and LINQ caches; its loader omits unresolved-framework
rejection and therefore is not complete policy or Player acceptance.

The main agent's new guarded Unity run passed 631/631, zero failures/skips,
under `_temp/AssemblyShadow/EditorTests-ad60c41972b4470f81d0d5fb1556b58f`.
Results XML SHA-256 is
`0c284fd8c154b12618cbb842ad7ea369b83178bc2f86ecb7cb99cb3bf11feef3`.
Independent re-review of that immutable package range confirmed a remaining
output-channel defect despite the green suite. A void Bootstrap helper can
write selected types into a caller-supplied `object[]`; an outside caller then
receives candidate types while the graph still omits its candidate dependency.
A custom delegate taking `Type[]` is a second confirmed channel. Return-type
classification misses both a mutable output parameter and a custom delegate
whose output capability is described by its `Invoke` signature rather than
its instance fields. The field-only IL prefilter also skips array/indirect
writes. This remains inside the existing callable-selector boundary, not a
requirement to taint all opaque diagnostic inputs.

The review also confirmed a second P1: a composite token such as
`typeof(List<Broker>)` hides the selector owner in a generic argument. Looking
only at the outer generic definition misses the broker. The repair uses
recursive token checks plus conservative finite-provider projection across
actual incoming AssemblyRefs, including transitive Bootstrap references.
This intentionally requires dependencies for some unrelated incoming
references but does not restrict outgoing pinned diagnostics.

The next corrective package commit is
`db2beedba28ece948d93071c411835bc6edae032`, changing only the propagation
helper and policy tests. It follows selected-value effects through locals,
fresh allocations, array/field/byref aliases and direct writer helpers;
caller/global/unknown writes, selected callbacks, indirect calls/block stores,
thrown selected containers and effectful recursion fail closed. Structural
read-only recursion and actual closed-generic scalar outputs remain supported.
Output tests also declare the candidate edges first, so the conservative
incoming-reference rule cannot mask a missing output-effect rejection.

The focused aggregate passed 144/144. The same-source actual compiler smoke
passed 25 admissions across 36 modules. The main guarded Editor rerun passed
639/639, zero failures/skips, under
`_temp/AssemblyShadow/EditorTests-99db8b5897684bf9b6f8f44de0c3a435`.
Results XML SHA-256 is
`c322f272f01917831619226ba7708f3f2110304d5f3ca04d2334205d249591f1`.
Independent immutable source re-review is pending; no Player acceptance is
implied by these source/tooling results.

The first independent offline selector correction passed 223 tests. It already
rejected the original caller-array and custom-callback outputs, but had a
safe-local-array false rejection and a nested broker-owner metadata omission.
The subsequent two-file correction adds finite local-array ownership/alias
tracking and exact recursive broker-owner token/import checks. It passed
44 focused tests including the real 36-DLL compiler smoke. The main reran the
entire suite with the explicit real compiler/configuration environment:
234/234 passed in 33.690 seconds, zero skips. The verifier and test file hashes
are respectively `3ba5f6ffbcb7653a077b46aca3da13cd95506ef239fc4c5ffa5775d5db50a0f4`
and `276183e1cf5a5ec12c8c6d31331deb1816bf7c015f6207b60ebce59baedf2682`.
This remains an independently stricter M05 evidence specialization, not generic
package-policy parity or a whole-program/native proof. Fresh selected
containers crossing unproved call/return/field/address boundaries fail closed.
Actual linked Player verification remains required; neither suite accepts M05.

## Preserved resource boundary

The frozen M01 manifest remains SHA-256
`e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d`.
The scene, prefab and data bundle hashes remain respectively
`f4e0106dff4cc822a66a8b13557336023742b010182065a8da633cc5feac2486`,
`985a762b8db78f128aea520571d79a553e0f7e37d9a7cd897e50366e70bcd98a`,
and `7f93e66e3537d7b3634ff725e35c20dffaec172d2424cee789ff959ef0d72935`.
Runtime M05 resource identity, serialized values, reference equality and actual
scene reload still require the fresh Player cases. No historical M00–M04
artifact is replaced by this working record.
