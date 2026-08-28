# M05 active types, reflection and cache evidence

Status: M05 is not accepted. The v3 native-ON Player/baseline, independent
linked-output replay and normal P01/P03 builds passed. Unity rejected the
original negative fixture's serialized schema before producing a usable
compiler snapshot. The corrected callback-state fixture passes the real Player
compiler regression and all 662 Unity / 249 Python tests. Independent corrective
source review passed; the reviewed v4 pairing is pinned for fresh builds.
No complete fixture replay, runtime matrix or final milestone gate is claimed.
M06 remains closed.

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

## Raw-admission dependency correction (package source readiness passed)

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
The first re-review attempt was interrupted by a tool-side restriction and
produced no verdict. A narrower read-only review of the committed code and
existing results closed the preceding findings but returned FAIL for one
remaining ownership issue: a helper can publish an empty local container
before it receives selected values, and that publication is not propagated
back to its caller. This is a source-derived finding, not a newly executed
reproduction by the reviewer. Mutable-argument publication must be summarized
independently of whether selected values are already present.

The writer then reproduced that finding against the previous implementation:
144 existing tests passed and one new assertion failed because policy remained
valid. The actual outside DLL references only mscorlib, so the incoming
Bootstrap reference rule does not mask this publication channel.
Corrective package commit `90852d8a59fa14b501cf1c6f1cc38e9d4655ee86`
changes only the same two files. It independently carries publication,
argument contents, return aliases and reachable container ownership across
calls. Tests include helper chains, receivers, constructors, related inputs,
returned/global/wrapper aliases and bodyless calls, with positive private-local
and proven read-only cases retained. Unknown mutable calls and recursive
effects without a proof remain conservative; no schema or hash domain changed.

The pinned aggregate and focused suite passed 147/147; the same-source compiler
diagnostic passed all 25 admissions across 36 modules in 2,997 milliseconds.
The main guarded Unity rerun passed 642/642, zero failures/skips, under
`_temp/AssemblyShadow/EditorTests-c138f55f230c44fd8abe39e44843e2ca`.
Results XML SHA-256 is
`0a9e8258031f1fa6411e4fda344db7b9fb66f55622356e90e2527e6a1a572680`.
The propagation and policy-test source hashes are respectively
`6dc9c09bb18da0e186dbf0e9f246097c2192d58d0fd66c81aae73a928df7b146`
and `3af77be2ca0c2db5b5a4b151aadd8487ac4987285702aa2d417b9449c1b8edf3`.
The independent read-only re-review returned PASS for that exact package
revision. It checked the two-file delta, clean package state, both source
hashes, the actual XML hash and all 29 raw-admission policy tests. No reviewed
code was executed during that gate. Both native/runtime and package source
readiness boundaries now permit fresh installation/build validation; neither
verdict accepts M05 runtime behavior or permits progression to M06.

Demo implementation commit `531389393fe9684bc0267e592f4da6ae3184c65d`
contains the frozen probes, tools and configuration, not a Player or milestone
acceptance. Before that commit, only eight new meta files' empty-value spaces
and one Editor source's extra EOF blank line were tidied after the 639-test run.
The raw configuration retains its exact CRLF bytes and hash; the staged
whitespace check explicitly recognizes CRLF rather than normalizing that
hash-bound input. No GUID, runtime source or compiled method body changed in
that whitespace-only integration adjustment.

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
The ownership follow-up required no Python implementation change: fresh arrays
already lose local ownership when passed across an unproved call, even before
they contain selected values. Three added actual-byte tests cover a publishing
helper, returned aliases and a publishing constructor. The main expanded rerun
passed 237/237 in 32.668 seconds, zero skips, including the real compiler smoke.
The new test-file hash is
`3fe758398b4b7c2c40405e6d872aa1d77bcff74de32c7cb27c8a27bfb2286880`;
the implementation hash is unchanged.
This remains an independently stricter M05 evidence specialization, not generic
package-policy parity or a whole-program/native proof. Fresh selected
containers crossing unproved call/return/field/address boundaries fail closed.
Actual linked Player verification remains required; neither suite accepts M05.

## Pinned preparation and compiler-input lifetime

Initial M05 setup committed the isolated scene and settings at demo source
`4ee799ff05353de0339a5d5e6bc83887a5c2929a`, with metadata pin commit
`9ff0c72a9972cec1aeb57106cfd88d41dabc4c96`. The runtime ABI hash is
`403d77eab1c45c2b3b2a52cbfc17d26c19b77ecf25f26774da1efa58358b8a41`.
The repeated pinned installation produced identical receipt SHA-256
`6f99c1ad911a6fa1471600d1c91ccdbeeab175a41fc3172973e1df8d32861b5b`.
Full installed-source verification passed with 940 source files, 942 installed
files, demo inputs verified and native ON. Earlier M04 receipts/settings are
preserved under `_temp/AssemblyShadow/M05PreInstall-jHTYjllU`; the initial M05
record is under `_temp/AssemblyShadow/M05Integration-8IdZleUf`.

Fresh declaration generation in `_temp/UnityExec_20260828_012812.log` confirmed
the unchanged 25 sites and configuration hash. The following preflight passed
in `_temp/UnityExec_20260828_012858.log`, with its immutable snapshot at
`_temp/AssemblyShadow/M05CompilerPreflight-c10b1ab52c0e45a383cb420d23dd6639/Snapshot`.
The configured full Editor suite then passed 642/642, zero skips, under
`_temp/AssemblyShadow/EditorTests-ab67f7e684524ec799680258e7ac2c8a`, XML SHA-256
`889118a5496d3f02b94bc4ba6e9b49e9cf23bb11afd01387e0fda243f6067c02`.

The first fresh Python replay failed because its direct compiler directory
had disappeared: preflight log line 523 records Bee deleting 80 prior artifact
files. A unique directory name did not give those producer-owned files an
independent lifetime. The corrected generator compiles into `CompilerOutput`
and hash-checks copies of exactly the returned DLLs and their present PDBs into
a sibling `Assemblies` directory before deriving declarations. It rejects
overwrite, out-of-root inputs, duplicate output names and a capture directory
inside producer ownership. It neither invents a runtime role nor filters by a
library name. Two focused Editor regressions cover retention and those guards.

The corrected full Editor suite passed 644/644, zero failures/skips, under
`_temp/AssemblyShadow/EditorTests-d4ba75bcec9440bda5d2930b4522dc23`, XML SHA-256
`9ba51c7d570df1d4b6e7cc7ce2a5895a7256408f52b36eb8bbbaa64da8d28353`.
Two real consecutive Generate runs are recorded in
`_temp/UnityExec_20260828_014025.log` and `_temp/UnityExec_20260828_014141.log`.
The latter explicitly deletes the first run's producer artifacts. All 36
preserved DLLs and 36 PDBs remain byte-identical; hashes and paths are in
`_temp/AssemblyShadow/M05Integration-8IdZleUf/compiler-output-lifetime.json`.
The preserved direct-compiler root is
`_temp/AssemblyShadow/M05RawAdmissionCompiler-955e889bd4c1442eaf694f53ff6a0ff3/Assemblies`.

An attempted replay against all preflight snapshot assemblies also exposed a
distinct decoder bug. That broader snapshot contains five precompiled inputs
in addition to the 36 direct compiler outputs. Captured NUnit token
`0x7000379d` contains an XML-filter regex with isolated surrogate code units;
strict Unicode-scalar decoding rejected its valid CLI string payload. .NET
strings preserve 16-bit code units rather than requiring every unit to be an
independent scalar. [Microsoft's encoding documentation](https://learn.microsoft.com/en-us/dotnet/standard/base-types/character-encoding-introduction)
explains that distinction. The correction uses lossless `surrogatepass` only
for `#US`; token, bounds, length and terminal validation, strict identifier
UTF-8 decoding and exact finite provider checks remain unchanged. No NUnit
waiver, skipped entry or string replacement was added.

Five added actual-byte regressions cover legal code units and malformed
structures. The writer passed 52 focused and 242 full Python tests with zero
skips against the broader 41-DLL snapshot, and successfully replayed its actual
compiled raw proof with 189 captured references. That broader check is static
decoder evidence, not runtime membership proof. The main independently passed
242/242 in 32.185 seconds, zero skips, against the preserved exact 36-DLL set
while the second Unity compilation retired the original producer outputs.
The generator/source-test hashes are
`ccb7bad42fe66c61c963c66f791706e15a9efe37495c9f765a6490d0ca66b3ed` and
`f2585af75724ee37fc61625e476466e10e20ed07f984d522347ab98711869aa9`;
the Python verifier/test hashes are
`64481cf0de76abfec9e0fa64851dce7478a2e778d4f2a6eb2ea600ee1bfcdd49` and
`82d250ac09fc450cd3bad770479527e927f9da70798a5b5de86f6a90ef8cc2b7`.
The independent read-only corrective review returned PASS at demo commit
`006a5554ebb7bf2b24cfbdaac33cb18bc9926fce`. It verified the exact source/test
hashes, unchanged configuration, 644-test XML and all 72 preserved-file hashes
after the observed producer cleanup. Python counts remain supplied test
evidence at that gate. This permits repinning and build validation only;
no M05 Player or milestone acceptance is claimed.

## First actual native-ON Player and linked-output replay

The reviewed installation was repeated successfully in
`_temp/UnityExec_20260828_014832.log`; both receipts have SHA-256
`be1eeb52602e4870cbfd3e3f28d957da57f9edfd6517bf58bae2e051b06a5d9c`.
Full installed-source verification passed with 940 source files, 942 installed
files, demo source verified and native ON. The exact demo executable source
pin was `006a5554ebb7bf2b24cfbdaac33cb18bc9926fce`.

`M05Build.BuildPlayerBaseline` completed successfully in
`_temp/UnityExec_20260828_015441.log`, including semantic equality of the three
frozen M01 business DLLs and unchanged resource bytes. The immutable v1 input
snapshot is `_temp/AssemblyShadow/M05PlayerInputs-505c7d6cccfb4cdeb3f00c6cd2313d69`.
Its hash is `00c9b5ecdb42165cfd8c4d341aa96d24fcbfc0e1aac1e9a6dc0cdfdc0cf6fc50`,
build GUID `3d7ba625c3af454e853affd32fd992d7`, and actual GameAssembly SHA-256
`db0036a0cf229b63d6f8856737e0cff4a7a6a48581d3e42b8363143b04f1305c`.
The Player receipt and type-proof hashes are respectively
`48c2ce8764fd49a1ab731fbda45d8650cce189f90a51063b9a79c066b392fc5e` and
`58212c21291ec9b4cead9534b98b280ccca44fc6d579ecb876ee5f7d88c36884`.
The baseline manifest hash is
`e1feac039c1a7643d891fce61840a662b25b9267d951dc65d62ae534f5a086af`.
Receipts are also preserved under `_temp/AssemblyShadow/M05Integration-8IdZleUf`.

Independent replay then exposed a transport-name bug: the historical linked
snapshot schema intentionally uses lowercase file/name keys, while actual
Assembly.Name retains its metadata spelling. All 60 linked DLL hashes and
MVIDs match the receipt; 59 names differ only by case. The new raw-boundary
reader incorrectly compared those two representations exactly, and used a
case-sensitive consumer membership set. The correction must normalize only
lookup/membership keys, retaining actual full identities, exact hashes,
canonical paths and collision rejection. Three added PE-byte regressions cover
the lowercase linked transport representation, consumer self-reference and
continued rejection of outside imports, wrong identities/hashes and canonical
collisions. The corrected raw replay passes all 25 sites over 38 compiled
inputs and 60 linked DLLs.

The type-inventory disagreement involved eight of 5,865 TypeDefs: generated
nested types in Unity.2D.Animation.Runtime (rows 64-65) and Unity.Collections
(rows 62-63 and 65-68) retain nonempty nested Namespace entries. The Python
reader had dropped those segments, while pinned dnlib correctly retains each
declaring and nested namespace/name pair in ReflectionFullName. The general
per-segment correction matches all 60 actual DLLs, including six linked method
witnesses and the runtime DTO. Four new PE-byte regressions cover mixed-depth
namespaces, escaping, distinct siblings, exact order and tampering; three
generated PE graphs with ten TypeDefs also match the pinned dnlib reader.
No C# or captured artifact change is required for either reader correction.

The raw-reader/source-test SHA-256 values are
`67712657e5e360b546d457cd6c5eb9d313cac8760947bc717e7a714b3c816319` and
`2362364957394d718c92716575c404563b8369701dc0296c068ccd3aca6342d1`.
The type-reader/source-test values are
`1f18a2bc26a572870acf7630485ed7a2736883430fd313a9b585f1391c897440` and
`c1aa4c9fffff0088ed0e3fbb5482c92150263bdcb7183a6d74fd1be5ad3e5fdf`.
Both writers are frozen. Main integration passed 249 Python tests in 32.835
seconds with zero skips, and fresh Unity Editor validation passed 644/644 with
zero failures/skips. The XML is
`_temp/AssemblyShadow/EditorTests-b9adf28722414be698a43cff2c35e449/results.xml`,
SHA-256 `8ff8f5d24fd12e99bfa138015bb4f3bbf5d48239fa01f307c54bd40d149611fa`.
The main combined replay passed raw compiled/linked proof, all type inventories
and witnesses, and actual native metadata in 6.577 seconds. Its bounded record
is `_temp/AssemblyShadow/M05Integration-8IdZleUf/v1-linked-corrective-replay.json`;
this is static byte-bound evidence, not a Player runtime result. The corrective
source gate returned PASS for committed demo
`2b7635339795d80dc2c77c8d3903256abc1c0fd3`. The independent reviewer inspected
the exact four source/test hashes, 644-test XML, unchanged v1 proof/receipt,
all 60 linked DLL hashes, the 5,865-type inventory and six IL witnesses. It did
not execute reviewed code; Python counts remain supplied main evidence.
This permits the fresh v2 pairing to be installed and built, not M05 runtime
acceptance. The source pin now names that reviewed implementation revision. This
fresh identity retains exact four-repository provenance across the eventual
ON/OFF and fixture receipts; the v1 artifacts remain unchanged. The v2 scene
and setting were configured by the guarded Unity method in
`_temp/UnityExec_20260828_020853.log` with the unchanged runtime ABI hash.

## Reviewed v2 build and first fixture-policy rejection

The source pairing pinned demo `2b7635339795d80dc2c77c8d3903256abc1c0fd3`
and retained runtime/native/package revisions listed above. Fresh declaration
generation passed in `_temp/UnityExec_20260828_021820.log`; all 25 sites retain
the same configuration hash. Its preserved direct compiler outputs are
`_temp/AssemblyShadow/M05RawAdmissionCompiler-66babb4880844875ae84b993f3e8e01e/Assemblies`.
A targeted real-compiler smoke passed through unittest discovery (one test,
2.555 seconds); an initial module-style invocation had only an import-path
failure and was not test evidence. Repeat installation in
`_temp/UnityExec_20260828_021849.log` produced identical receipts with hash
`e5d9ceff6e684a23a6d3599d3ec225e05c6143c8d08d7a43abf82a7d456db618`.
Full source verification passed. Fresh compiler preflight passed in
`_temp/UnityExec_20260828_021952.log`.

The complete native-ON v2 build passed in
`_temp/UnityExec_20260828_022113.log`, including the frozen M01 semantic and
resource checks. Snapshot
`_temp/AssemblyShadow/M05PlayerInputs-01b834c51222430a9f12ba98f5b76c5f`
has hash `315efc52db994f8be332e6d5d8c966c392d84ee03a7b24c57a9d1e470b8a400c`,
build GUID `69c6ece7d0f04910a6a16471f7c2f00e`, and native library hash
`169f8d947c3c1c0be1dd348b0c52e2a7f2432a2c15ec8d11d2ef5c572be4c0a4`.
The Player receipt, type proof and baseline-manifest hashes are respectively
`84e1583bad5b6408388111c13f0e036255fa533ca319311c5554b6dafcc18bae`,
`d1bf8ea4fb6b550327773d15a7af27e70ae64b675c04cc11fde99655dacf5704`,
and `36654f3b0013016689c93f037cdb6ca39dd82b41c51ab69b5d72cce110487a8f`.
Independent raw/type/native replay passed 25 sites, 60 linked assemblies,
5,865 TypeDefs and six method witnesses. The record is
`_temp/AssemblyShadow/M05Integration-8IdZleUf/v2-on-linked-replay.json`.

`M05Build.BuildFixtures` failed in `_temp/UnityExec_20260828_022715.log`.
Its immutable P01 compilation is under
`_temp/AssemblyShadow/M05Fixtures-6e5d8c12ae31415eb572d2c0507c5cba/P01-compile/Snapshot`.
The actual policy rejected operation 19 of
`InternalEntry.GetM05TypeNameForms` as UnboundedManagedAcquisition and
UnknownReflectionDependency. The rejected source call is the required literal
`M05InternalGeneric` closed over `System.Int32` via Type.GetType(string,bool),
not a dynamic name. No admitted P01 artifact was emitted. Read-only inspection
of the actual DLL confirms `ldstr`, `ldc.i4.1`, then the lookup at IL operations
17-19; constant-stack analysis is sound. The scanner instead splits the type
at the generic argument's first comma and then compares a constructed generic
name with a TypeDef name. Fixing only the comma boundary is insufficient.

The corrective scope is a strict, bounded literal syntax tree and closed
captured-metadata resolution for each generic definition and argument. The
actual `mscorlib` reference facade forwards `System.Int32` to captured
`netstandard`; neither a host-framework fallback nor dnlib's primitive-scope
normalization is evidence of that original literal identity. All components
must resolve before any acquisition evidence is admitted. Business forwarding
and terminal providers retain their actual-reference or declared-edge checks;
authenticated compiler Reference providers are resolution evidence, not
invented business edges. Exact Bootstrap approval must retain each distinct
component type, including multiple arguments from the same provider.

Corrective source/test review and fresh matched builds remain pending. No
bypass, method/name waiver, replacement typeof query or altered captured bytes
is permitted by this result. The general compiler preflight still cannot claim
linked Player membership or runtime policy acceptance.

## Generic-literal correction and local validation

Package commit `b132981fa72f8259efde8e8319029b8812858bcf` changes only the
scanner, minimal Reference-role declaration check, new bounded resolver and
new test source, with the two new paired metas. The original literal remains
the approval target; all generic-definition, argument and forwarding-provider
evidence is emitted atomically. Deduplication includes the component type.
Runtime, NormalHotUpdate and BuildFiltered providers cannot take the compiler
Reference exemption. No graph edge, assembly identity or runtime observation
is synthesized.

The new grammar supports closed, explicitly assembly-qualified generic
arguments and nested names. Generic string queries with ignoreCase overloads
(even false), resolver callbacks, arrays, pointers, byrefs, escapes or
unqualified arguments remain rejected. This restriction concerns literal
admission, not M05's separately tested native composite-type reconstruction.
Historical simple-name resolution is otherwise unchanged, except that
resolver-delegate overloads cannot be authorized by a literal alone.

Main reran the pinned Mono aggregate and focused harness: 147 existing tests
and 17 new tests passed. New actual-byte synthetic cases include all 15
plain/nested/generic forms across the five real candidate names. A separate
replay of the captured failed P01 DLL finds five dependency components and
zero unknown acquisitions at `InternalEntry.GetM05TypeNameForms`, retaining
Internal, `mscorlib` and `netstandard` provenance. Full command output is
`_temp/AssemblyShadow/M05Integration-8IdZleUf/generic-literal-focused.log`,
SHA-256 `7048b21af118f7627c978d717e22b5a0aba230a1c046e112e7c0cb3a2f55e487`.

The fresh guarded Unity package/demo run passed 661/661, with zero failures,
inconclusive cases or skips, including all 17 new cases. XML:
`_temp/AssemblyShadow/EditorTests-007a1078a51c4a2c83ecdffad0e98797/results.xml`,
SHA-256 `24ef8e3a9d4628cd6c7db06c65637ecad513cda4f0d61dd4b3b9a50fe1c61c36`.
The full Python regression suite also passed 249/249 without skips using the
preserved v2 direct-compiler inventory. None of these results admits an old
fixture or accepts a Player runtime case. Package commit identity participates
in the ABI hash, so v1/v2 artifacts stay immutable and fresh matched v3
ON/OFF/fixture evidence is required.

Guarded Configure passed in `_temp/UnityExec_20260828_025949.log`, selecting
`M05-Baseline-v3` and the package-corrected ABI hash
`2e3761532b293f033677580292a0654129bcf8699e88bc5f11b7da8c1a6e7353`.
The scene's runner GUID and all other serialized values remain unchanged.

The independent corrective source reviewer returned PASS for package
`90852d8a59fa14b501cf1c6f1cc38e9d4655ee86` to
`b132981fa72f8259efde8e8319029b8812858bcf`, and demo
`b4a493488f3af39b033911421ac5aed313cf1c6a` to
`d19222f70d9b255f397656a11b2ee35dd882629a`. It inspected the committed code,
source hashes, focused log, actual 661-test XML and Configure output without
executing reviewed code. No actionable finding remained. This permits the
fresh v3 source pairing to be installed and built, not runtime acceptance.
The source pin now identifies that exact reviewed demo revision; this report
and inventory refresh is a later metadata-only commit.

## V3 build and negative-fixture compiler boundary

Fresh v3 declaration generation passed in `_temp/UnityExec_20260828_030518.log`.
The preserved direct compiler root is
`_temp/AssemblyShadow/M05RawAdmissionCompiler-7b0fbb2c340b4812a17046c5c2bc906d/Assemblies`.
All 25 sites retain the same configuration hash. The real-compiler smoke and
full 249-test Python suite passed, with zero skips. Repeat installation in
`_temp/UnityExec_20260828_030559.log` produced identical receipt hash
`8eaade52a789baf0905cb0e2b49b1d168e4cd9b01c20cb9e061d3b3df8e2ed48`.
Full installed verification passed for 940 source files and 942 installed
files, including demo source and native ON. Preflight passed in
`_temp/UnityExec_20260828_030728.log`.

The native-ON build passed in `_temp/UnityExec_20260828_030825.log`, including
the immutable M01 semantic/resource checks. Snapshot
`_temp/AssemblyShadow/M05PlayerInputs-8284e1028e47432387bd8172a40148ed`
has hash `ea13a119f62973b9fc099d7901087c8180e5e12c38070d093387803d992588c5`,
build GUID `b40a3586fbf5496eb278ab2979fedffe`, and actual native library hash
`3ac89b5ccd52a15cc7baa65173f3075fb1540d4e779cc9bedd5d01e54391eabc`.
The Player receipt, type proof and baseline manifest hashes are respectively
`9ad7b7ed163899b341e562dce689930eeaed63df6a929c994f4b8421a9df4b21`,
`ebcec8ae4f97d08039f58509c2926117720975c0781cf2aea6c0c9c6ec71160d`,
and `0dc224d0798bbe05ee7aa8e6ab33c878624ebd35e4b8f14036f6863e5b399e01`.
The independent replay again passed 25 admissions, 60 linked assemblies,
5,865 TypeDefs, six method witnesses and native metadata 31, with inputs
unchanged. Its record is
`_temp/AssemblyShadow/M05Integration-8IdZleUf/v3-on-linked-replay.json`.

The next fixture run, `_temp/UnityExec_20260828_031532.log`, completed P01 and
P03 under `_temp/AssemblyShadow/M05Fixtures-10593064976440438a94cbc598f125af`.
Their manifest hashes are
`a2cc281d84ead22092d71987b2af3912207e0c6cbeeff4e5acc3a383a3e194d1` and
`fda07e5c36718a8feda63b58807858d479d7110d9563032234e3eb4ff88f0d49`.
It then failed on LayoutMismatch: Unity found the extra serialized
`m05BadLayoutField`, rejected Editor/Player schema parity and returned no
accepted Player assemblies. C# emission alone is not a compiler snapshot.
There is no top-level fixture manifest/replay and no runtime acceptance.
The failure log hash is
`10d6487fff6f6de42f6facba83d6ab6f7b71af99d07a7f20a40c678386f857b8`.

Pinned API inspection found no supported skip-TypeDB flag. Rather than invoking
an internal API or relabeling independent compiler output, the corrected
test-only fixture keeps the existing serialized schema, adds nonserialized
instance state and consumes it in serialization callbacks. Existing resource
tooling must reject that callback state as `UnknownRequiresReview` (external
DLL-only error `ResourceRebuildRequired`); this is not a hard serialized-field
diff claim. The actual extra instance field still requires an independent
native allocation failure. Neither production compiler nor policy code changed.

A new regression invokes the real public `CompilePlayerScripts`, requires
nonempty successful output, preserves its returned DLL/PDB bytes outside Bee's
producer directory and inspects the actual fields, attributes and callback IL.
The focused guarded run passed one test with zero failures/skips at
`_temp/AssemblyShadow/EditorTests-72eea618dd7d49a8ade8bb7d2aac4596/results.xml`.
Its XML hash is
`0189de0bb186a5f9bffe788d5593f2e0c5b6e2001259a1d3bc79eb5bf6b33da7`.
The added field/callbacks remain absent from baseline, P01 and P03 builds unless
the separate layout-mismatch define is present.

The subsequent full guarded Unity run passed 662/662, zero failed/skipped or
inconclusive cases, in 84.721 seconds. XML:
`_temp/AssemblyShadow/EditorTests-5d7892f3ca644847a6e65e45ec7b5677/results.xml`,
SHA-256 `a2dd0c9af4bea52ac6144cc5bc8a933df5aaceaee975c191f12a7b2bc62a6ecf`.
The full Python suite passed 249/249 in 32.829 seconds, zero skips, using the
preserved v3 compiler inputs. Witness and test source hashes are respectively
`35a7c0ce8821c751e53453211233706ebc00c75b9d7efc3d2f442fc12967ebee` and
`9fb723bddfe922f834e90d2105c9a4f9fb4baa1978f269d9ce4721336416422f`.
Configure passed in `_temp/UnityExec_20260828_033628.log`, selecting
`M05-Baseline-v4` with the unchanged runtime ABI hash. Only the baseline ID and
two nonsemantic empty-value whitespace lines changed in the scene; the latter
were restored before source freeze.

The correction is committed at demo
`d3d1f23b11cce6c966298a03b035f71382bedbb1`. Independent passive source
review returned PASS for `dbbdc9c3e1908cb198f544aa7e51b1e0c9912fea` through that
revision. The reviewer checked the exact six-file scope, guards, compiler
regression, unchanged resource policy, XML/source/DLL hashes, original v3
failure and v4 Configure log. No reviewed code or tests were executed by the
reviewer. This permits the pinned v4 pairing to be installed and built; actual
resource-policy and native bad-byte rejection remain pending. This metadata-only
follow-up pins that reviewed source and updates its complete file inventory.
Fresh v4 ON/OFF/fixture/runtime evidence remains necessary; v3 stays immutable.

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
