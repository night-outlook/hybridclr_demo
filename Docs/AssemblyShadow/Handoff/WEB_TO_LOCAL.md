# Primary Implementation -> Local Validation: R02 after batch D

## Objective and read order

Run one fresh `R02LocalBatch-v1` against the source-bound H1-runtime control and R02 candidate. Verify the batch-D completion/prerequisite repairs, then complete all independent functional, regression, CPU/memory and evidence cells. Do not begin R03.

Read `Docs/AssemblyShadow/README.md`, this file, `History/M07R/R02/D_COMPLETION_REPAIR.md`, `History/M07R/R02/DESIGN.md`, `History/M07R/R02/LOCAL_VALIDATION_TASKS.md`, and `History/M07R/R02/source-targets.json` under the same canonical documentation root. `PRIMARY_VALIDATION.md` records the actual Primary checks; it is not Player acceptance.

Input Local return: `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`. Batch D remains `ReturnRequired` with 8 Passed, 3 Failed and 20 Blocked. Its missing post-signal census cannot establish the exact historical process transition. Preserve D and prior A/B/C; never relabel their rejected controlled builds.

## Exact source and workspace authority

H1 remains `PassedWithExplicitDeferredRisk` after D1=A and D2=A. R02Accepted=false; mayEnterR03=false.

Common executable/tool source anchor: `57a9470bf299af60f88112998c8326c4c013204a`.
Use the exact latest pushed candidate transport HEAD in the final Primary prompt; its delta from the source anchor must be metadata-only under unchanged `shadow_tools.metadata_only`. Do not substitute the source anchor for that final handoff.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `57a9470bf299af60f88112998c8326c4c013204a` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` |

Control demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact HEAD `a379f0b809a5d8af967df06fc83271d90fd84f4c`. It includes the common source anchor as ancestry. Its siblings in `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/` are:

- `hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, remote branch `codex/assembly-shadow-r01b-h1`;
- `hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, remote branch `codex/assembly-shadow-r01b-h1`;
- `il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`, remote branch `codex/assembly-shadow-r01b`.

Control sibling checkouts may remain detached at those exact commits. The two demo checkouts must use their specified branches. Canonical remotes: `https://github.com/night-outlook/<repository>.git`. All eight owning checkouts must be clean, correctly identified and source-bound. No source or generated outputs may be copied between roles. Preserve unrelated worktrees and the separate historical R01 reference.

## Completed Primary changes

The production R02 cache/guard/diagnostics implementation and semantic/performance witnesses remain unchanged in this cycle. The seven changed/new executable files are the R02 workflow, `run_local.py`, `unity_session.py`, `process_identity.py`, `native_prerequisite.py` and the two corresponding new test modules. Runtime/package pins are unchanged.

`R02OwnedUnityRoslyn-v2` identifies each process by kernel birth time, PID, group and UID. It still initially admits only the exact owned Unity Roslyn command. A same-birth instance marked exiting/zombie may be waited for if its displayed arguments change; it is not signalled in that state and is not clean until absent. New instances, changed live commands, inaccessible identity, unexpected descendants or surviving processes fail. Every census is retained before policy evaluation, with phase and exact mismatch details. The outer no-survivor rule, actual command status and timeouts are unchanged. Formal Player commands are not wrapped.

Four independent native scripts remain in `native-regressions`. The transaction probe now runs through `native-generated-inputs` -> `native-transaction`, after `candidate-build`. The prerequisite authenticates current generated UnityVersion.h, full installed runtime, source pins/install receipt, current controlled graph's AssemblyA.Contracts.dll and the supplied Unity installation's baselib. The transaction command receives explicit paths and rechecks them after execution. No historical DLL default, fabricated header or unrelated checkout output is accepted.

The earlier independent M00 preparation remains mandatory in both roles. It must produce the frozen SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`. Batch D never reached this step; actual byte equality is still unverified. A mismatch returns to Primary with compiled bytes; do not rewrite the hash or import another workspace's DLL.

## One serial Local batch

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, clang++, at least 30 GiB free (entry minimum, not a guarantee of total archive space). Resolve actual absolute tool paths. Close Unity for both projects. Use `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1` for batch entry. Child commands receive canonical temporary paths and the committed no-server-reuse settings.

From the candidate checkout, invoke `Tools/AssemblyShadow/R02/run_local.py` with `--candidate`, the final prompt's `--candidate-head`, `--control`, `--control-head a379f0b809a5d8af967df06fc83271d90fd84f4c`, absolute `--unity` and `--pwsh`, and an unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Without `--execute`, inspect the plan. Add `--execute` for the single new execution. No semantic retry, timeout increase or source change is authorized.

There are now 33 required cells: the original coverage is preserved and the native transaction prerequisite is split explicitly. Cover source authority/common graph, host Primary checks, new candidate/control controlled ON/OFF graphs, eight functional sidecars, four pilot plus forty formal A/B pairs (88 timing processes), Editor/native/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity, final authority and complete sealing. Independent cells continue only with valid source/workspace state; failed prerequisites block consumers. A missing native generated prerequisite is Blocked, not permission to compile with old headers.

The four pilot pairs are not formal performance acceptance. The 40 formal pairs have 10 per mode, balanced AB/BA, unique fresh processes and no R02 sidecar during timing. Keep the existing strict R00 verification and measurement meanings. D1/D2 require measured disposition, not just a PASS label.

## Evidence and failure collection

Preserve command JSON/stdout/stderr, `commands/*-unity-completion.json`, kernel identity observations including the rejecting snapshot, compiler binding, actual command exit and signals. Preserve candidate/control ordinary-input authentication and preparation roots, build workflows/maps/input snapshots, every launch/raw/verifier chain, negative inputs, partial failures and restoration receipts.

New native records: `native-generated-inputs.json`, `native-transaction-integrity.json`, and `run-r01-transaction-native-tests.py.json`. A failed prerequisite retains available file bindings; a failed command cannot be overridden by a successful post-check. Never retain only summaries or remove failing attempts.

`LOCAL_BATCH_RESULT.json` binds `seal/seal-index.json` and the content-addressed archive. Keep indexed generated roots outside the batch directory. Historical capacity bytes are authenticated inputs only, not reused execution; missing bytes block the relevant path, with no basename fallback. Preserve A/B/C/D, H1 archives, source-27df performance and the older R01 reference.

## Review, boundaries and return

Report cold/warm allocation, reflection, closed-generic distributions/sample counts, current H1-runtime control versus R02, and remaining D1/D2 costs. Keep the older R01 comparison separate. Distinguish native owned storage/allocation requests, managed memory, point-in-time RSS and lifetime peak. No codec-only causal or production-SLA claim is authorized.

After all required cells and evidence succeed, obtain a genuinely independent R02 stage review with the fixed source/evidence tuple and preserve its verbatim verdict. This is not H2. Stop and return to Primary before R03 regardless of that outcome.

Permitted Local changes: exact worktree setup/fast-forward, absolute tool resolution, unused output suffixes, normal build/fixture generation and scripted bounded restoration, evidence collection, and bounded environment fixes with receipts. Forbidden: production/verifier refactors, identity-policy or pin edits, fabricated generated headers, relaxed cleanup/hash/case expectations, cross-role runtime installation, hiding failures or cleaning retained evidence. Do not run `tools/r02/finalize_sources.py --prepare`.

Update and push `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications. Record non-trivial problems in `RETURN_TO_WEB.md` with the first failing command, complete source/build/input tuple, rejecting identity or prerequisite snapshot and retained evidence. No non-trivial implementation is assigned to Local.
