# R03 initializer one-use follow-up — executable plan and acceptance matrix

Date: 2026-11-05 UTC. Primary Implementation. Read `INITIALIZER_ONEUSE_DESIGN.md`
and the current `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` first.

## P0 — source and policy admission (no writes)

Use exactly the four pinned branch heads in the current Primary-to-Local
handoff, never the consumed K/J/I execution commits or prior smoke branches.
The demo commit is the final **published** remote head printed in the
Primary handoff prompt. Independently verify all four clean owning
repositories, branch, canonical origin and `ls-remote` head equality; inspect
current README and handoff. Keep the separately preserved original-S worktree
clean at demo `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`. Do not
checkout, modify, repackage or rebuild its original S evidence.

Use the previously established local defaults (override only when the
actual environment has a different documented canonical path):

~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261105-oneuse-01
# DEMO_COMMIT = exact final pushed demo HEAD from the Primary handoff prompt
~~~

Before executing a write, run the existing independent read-only machine
admission (`current_native_environment_admission.py`) using these values
and repeat Git/original-S/SDK/process/volume/custody checks. Verify target
macOS arm64, installed Unity 2022.3.62f2, no conflicting Unity/IL2CPP
process or reused output root. Take **two new timestamped capacity readings**
of the actual RUN_ROOT parent, at separated times immediately prior to
execution: both >=25.0 GiB, otherwise Blocked without creating RUN_ROOT.
Hard 20 GiB and normal advisory 40 GiB remain unchanged. If >=25 but <40,
record the one-use exception and no disk cleanup or sibling-volume trick.
Record original A–K preservation without modifying their source/evidence.

## P1 — source/host gates

The new runner validates its four live remote pins, eleven historical source
blobs, 45 native VM source files and seven new exact Git HEAD source bytes.
Execute actual ten-component current-native C++11 host preflight plus the
initializer observer, native writer, Python source preparation, schema and
new runner's positive/negative tests. Retain each original command, compiler
return code, output and unique source/install receipt; no simulated host
command may satisfy this step.

## P2 — immutable archive/provenance

Under the same new RUN_ROOT, read the original nine-part/15,713-member S
archive and the 90 original cell identities; independently join 59 historical
process receipts to authenticated original commands; run read-only original generated
source and archived NativeOn/NativeOff GameAssembly source/registration/symbol
audits. Preserve raw SHA reports and any errors. Archive identity and named
Mach-O symbol existence must not be promoted into source-object-link/Player
mapping, which remains NotProven.

These independent audits are not a gate that can suppress the new native
initializer build. If an archival stage fails, its cell fails, but unrelated
initializer stages still execute when their prerequisites pass.

## P3 — new fixture and one native Player build

Build the opt-in pinned PlayerFixtures generator and invoke ONLY
`--ir-terminal-native-targets`, producing two separately hashed/MVID-checked
Methods.dll files. Then use one unused isolated Unity project:
`prepare_ir` copies original R03 terminal source; the new source preparer
copies the initializer Player and concatenates original probe plus two
native additive sources. Authenticate every input and composite digest
before Unity. Build ON/Release C++11 with diagnostics level 2.
The new verifier checks actual Unity BuildReport, installed composite native
source, original/changed source pins, source-to-install receipt, binary
inventory and ARM64 architecture. No source edits in the original project.

If Unity fails, preserve Editor.log, Bee diagnostics, BuildReport,
native compiler error, installation receipts and command process receipts.
Do NOT retry the same RUN_ROOT or ask Local to implement a C++ refactor.

## P4 — two distinct real Players

With the one freshly built app and separate fresh OS PIDs, run:
- `IR-R03-02-initializer-control` using native fixture SHA
  `f909d3a4dd2ae3e561f1c0a2e25b50009203e440ce35a743afae937073e294a8`;
  expect Commit 0, Committed 6, bound field 3, callback once, positive
  mask 15, AOT canary stays 1 and post-terminal attempt false.
- `IR-R03-02-initializer-failure` using SHA
  `1cf13922d9f5798873a2581867f4dc0ea7415bd5ceee815e1b9489d99ce4937d`;
  expect Commit 19, FailedAfterCommit 9, the native callback once before
  initializer failure, pin-bound primitive field stays 3, positive mask 15,
  postterminal AOT attempt true but success false and canary stays 1.

Both must produce a real preopened native V1 JSON (bounded <=2048 bytes)
bound to independent request/fixture/launch PID and the actual built bundle.
Log observed Unity/IL2CPP native diagnostics as factual results, including
nonzero exit, failure and missing evidence. Never call V1 a complete
NativePreopenedSnapshotV2 or a real captured-generic test.

## P5 — seal and return

Reverify all four Git origin/branch/remote/clean heads after the run. Preserve
the exact 15-cell local ledger, unique command/process receipts, BuildReport,
native input and Player logs, machine/capacity admissions, original S audits,
full raw and BATCH_EXECUTION/evidence-index/seal receipts. The runner's
`LOCAL_BATCH_RESULT.json` is scoped: either
`FocusedInitializerEvidenceReadyForIndependentReview` only when all fourteen
cells and seal pass, or `ReturnRequired`. Both retain all R03/H2 acceptance
flags false.

The Local Agent owns factual `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`:
publish an additive new checkpoint under
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261105-oneuse-01/`,
preserve old evidence, record exact execution and evidence-publication
SHA separately, and commit/push the actual evidence via Git.
Report non-trivial issues to Primary, but do not rewrite the previous
one-use record, mutate product VM, self-approve review, or begin H2/M08A/X02.

## Post-run decision matrix

| Item | Passing Local proof | Unresolved even after scoped PASS |
| --- | --- | --- |
| Real initializer | 1 BuildReport, 2 native Player PIDs, 2 separate fixture+callback V1 records | Full terminal V2/recovery/general diagnostics |
| Current VM guard | Current 10 native host suites and previously K observed paths | Captured-generic error 15 and other uncovered entry paths |
| Original S | Archive+90 cells and 59 process joins, generated-source identity, two archived Mach-O registered symbols | Complete compiler command/object/link/process chain, captured omission crosswalk |
| Acceptance | Exact new output seal and pins; evidence ready for separate review | IR-R03-01/02 independent closure, RC1–RC6, managed shutdown, whole-VM epoch, GC/RSS, P1/P2/E0/E1/P3 |

Stop after the single execution and evidence publication. Any source-level or
cross-module fix, extra build, new scenario, or rerun requires a new Primary
design, commit and authority. Previous K and independent October 8 verdicts
remain unchanged.
