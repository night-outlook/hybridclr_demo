# R03 initializer oneuse-03 — native failure journal and host evidence boundary

Date: 2026-11-06 UTC. Owner: Primary Implementation. Branch:
`codex/assembly-shadow-r01b-h1`. **R03 only; source-side design and
next Local evidence, not independent acceptance**.

## 1. Frozen incoming evidence

Actual oneuse-02 executed at demo `7da27a486b529cdebf73100b5ce4c332a1bb7e86`;
Local publication `61bf436d65e5909767206d385ecba865e4c7a5ac`.
Original source revision was tested with interpreter
`4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package
`948c0e3b4f8891481301770115e8ba4945eea6de`, native
`41764ae1eeefb33b05966e7f7676e52aae39c340`.
One source-bound run, **13/15 cells Passed**, both Players Failed,
their command receipts 0014/0015 exit2 PIDs8065/8067, native raw files
both zero bytes, original semantic verifiers NotRun_CommandFailed.
One actual Unity2022.3.62f2 macOS arm64 ON/Release C++11 IL2CPP build
Passed, errors0/warnings1, installed overlay and GameAssembly four
`R03_IRW_*` native exports authenticated. Original nine-part S
archive/90-cell/59-process/lexical/Mach-O audits and ten native host
components Passed **within narrow historical/host scopes**.
The exact first native/managed predicate failure remains unknown.

Independent `SEAL_FAILED.json` records the intentional
`native-host-diagnostics/historical-eight/native-v2-file-transaction/evidence/sanitized/case-0168/alias`
directory symlink. A real host negative case created it; it must
not be unlinked or suppressed. The generic `batch_evidence.py` correctly
rejects included links. The original seal/index/archive were **not**
created; Local's separate additive publication and full raw manifest
do NOT retroactively pass the product seal. All oneuse-02 evidence,
K and other historical sources remain immutable.

## 2. Native observation correction (diagnostic, not guessed VM fix)

New `PlayerProject/R03InitializerObservationWriter.cpp` owns two
separate exclusively created native files before candidate Configure:
- `raw.json`, original strict V1 report; can remain empty on failure.
- `raw.json.native-trace.jsonl`, append-only bounded native phase
  diagnostics, independent of strict V1 success and of V2.

On successful Open, the trace starts at phase100 and records phase101
for raw preopen. Both fds use `O_EXCL|O_NOFOLLOW`, regular 0600
mode/nlink validation. Each trace event contains exact
`runId/caseId/stimulus/fixtureSha256/pid` and monotonic sequence,
fixed integer phase plus four primitive integer values, and explicit
false acceptance markers. Format is strict JSONL, max128 events,
512 bytes/line and 65536 bytes total; each phase is immediately
written and `fsync`'d. Event production uses only preopened native fds
and bounded C++11 formatting; it does not allocate or format managed
exception objects after the terminal boundary.

Instrument without loosening predicates:
- Managed phases100–220: preopen, healthy AOT canary, real Configure,
  Begin/Reserve/Stage/Validate return codes, before/after Commit,
  observed GetState, control/failure decision and actual postterminal
  AOT attempt result.
- Native phases299–302: real `R03_IRW_OnPrepared` call count and exact
  branch -1 through -9, observed state/owner/class/offset/field
  primitives and successful pinned callback.
- Native phases400–401: `R03_IRW_ReadPrepared` return code, primitive
  field/offset/callback state, without calling class initialization or
  managed user code in postterminal.
- Native phases600–620: Seal's six actual primitive inputs, bound
  read result, strict V1 rejection reason1–6, raw write/fsync failure
  or actual durable successful seal.
- Managed phases900/901: numeric last managed stage on catch and
  final attempted seal inputs. No managed exception string, stack,
  or Unity debug logging after poison.

The writer's strict accepted control/failure 0/6 and 19/9,
field3/positiveMask15/callback1/canary1→1 requirements stay
unchanged. A failed/empty strict V1 report is NEVER upgraded by
a trace. A trace helps discriminate failure before Commit,
failed native callback, unexpected final state, field mismatch,
managed postterminal effect, or native file failure.

`verify_initializer_trace.py` is deliberately not the existing
`verify_initializer_observation.py`. Its typed strict parser rejects
duplicates, nonfinite numbers, partial/oversize events, reordered
sequence, wrong PID/request/fixture, missing callback/read/seal
phases and any acceptance marker. During nonzero Player termination
the coordinator loads the exact owned command PID and validates
any raw native journal in `verification.json/nativeDiagnostic`.
It still records `NotRun_CommandFailed`, empty raw SHA and exit2
as failure. Successful semantic verification requires the original
strict V1 and a complete observed phase journal, **both** bound
to the independent request, process and actual build.

This is a diagnostic-source correction, NOT proof of the causal VM
defect, full first failure/recovery, native V2 transport, or
global VM coherence. A later actual Player can reveal a new code
defect; Primary will then own the correction.

## 3. Host negative-test evidence boundary (no symlink weakening)

Use a **new separate sibling raw host directory**:
`<RUN_ROOT>-native-host-raw`, required absent and canonical.
The full historical eight + current two native host tests run there
normally, retaining all raw files and *all four* intentional symlink
nodes/targets as live test fixtures. Product batch remains
`<RUN_ROOT>`. No mutation or deletion of hostile test links.

`initializer_host_custody.py` enumerates that real host tree without
following any symbolic link, checking regular bytes with
`O_NOFOLLOW` and SHA256, recording every directory and the literal
name/target of each symlink in sorted typed
`host-custody/HOST_MANIFEST.json`. The test-only
`HOST_REGULAR_BYTES.tar.gz` contains **every regular host byte**
and a copy of the canonical manifest, and **no symlink tar members**
or untrusted directory traversals. Every archive member/size/digest
is reread and independently checked. The actual raw sibling remains
on disk, unchanged; the custody archive, manifest and receipt sit
inside `<RUN_ROOT>/host-custody/` and therefore participate in the
existing general evidence index/archive/seal exactly as ordinary
regular files. The original `batch_evidence.py` link rejection is
untouched and still fails a directly included raw host tree.

Before finalization, verify live raw host contents and all symlink
identities against the included manifest and archive, including
unchanged literal target strings. A mismatch forces ReturnRequired
with explicit custody postflight failure; the seal cannot promote
the batch to acceptance. Because the four actual negative links
are outside the product tree, the product seal can complete
for a failed Player too; a successful seal then proves only the
bounded evidence archive, **not Player success**.

The revised shared host workflow consumes an **actual complete ten-host
CLI output** on both Linux/macOS, captures its four live links and
regular bytes, then passes the unchanged `batch_evidence.finalize`
on a copy of the authenticated custody artifact. Small synthetic
host tests additionally reject link-target drift, byte changes,
archive tampering, output reuse, and direct-link inclusion.

## 4. Local execution, permissions and stop

Keep the original 15-cell logic, one real Unity
2022.3.62f2 ON/Release IL2CPP build and two separate real
control/failure Players. No new product VM/interpreter/package change.
The distinct new name is
`R03IR-Initializer-20261106-oneuse-03` with fresh sibling raw host
`R03IR-Initializer-20261106-oneuse-03-native-host-raw`.
Neither oneuse-01 nor oneuse-02 can be replayed, renamed, resealed,
repaired in-place, or used as a new execution path.

Mandatory preflight: exact final published four-repo branch/head/clean
identity, Unity/SDK/original-S/preservation admission, no conflicting
processes, both new output roots genuinely absent, **two new**
independently measured free-space samples on their actual shared
volume each >=25.0GiB (hard20/advisory40 unchanged). This oneuse
25-GiB exception is conditional and not inherited from 01/02.
Run only if the final exact source SHA passes both required
initializer and shared host workflows on macOS and Ubuntu, and the
source-only managed Player API compile is confirmed for the current
source byte identities. The user can stop before dispatch if any
gate is not satisfied. No old results are reclassified.

Expected Local outputs include `batch/LOCAL_BATCH_RESULT.json`,
`BATCH_EXECUTION.json`, one BuildReport, two real Player
requests/command PIDs/raw V1/native trace/verification files,
the read-only original-S archives/process/lexical/Mach-O audit
results, separate raw host sibling and bound in-batch custody,
postflight, main archive/index/seal or explicit unchanged
failure, and independent before/after source/evidence preservation.
All raw logs retained unmodified.

Acceptance boundaries remain unchanged:
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
qualificationApproved=false; runtimeAcceptance=false;
fullLegacyRegressionAcceptance=false`, PureInterpreter disabled.
Both independent High IR-R03-01/02 and RC1–RC6, captured-generic
error15, full native V2/general diagnostics, original compiler/
object/link/Player join, managed shutdown, GC/RSS, whole-VM epoch,
P1/P2/E0/E1/P3 and performance are still open.
Do not start H2/M08A/X02/SNAP-01 or self-approve Human Review Gate.
