# R03 B2 D5-B — independent source-custody review request

**Status: `D5BSourceCustodyIndependentReview=Pending`.** This is a separate review request, **not a Primary self-approval or an executable Local handoff**. Scope: the bounded D5-B **source/remote and historical evidence-custody preparation slice** following independent D5-A `PassD5AForD5BPreparation`. Do **not** authorize Unity/IL2CPP, native/player builds, P3–P6 fault execution, D5-B Local Validation, D6, H2/M08A/X02/SNAP-01 or Human Review Gate.

## 1. Exact source tuple and evidence

Branch `codex/assembly-shadow-r01b-h1`, GitHub Connector read-only independent source review.

| Repository | Source authority |
| --- | --- |
| `night-outlook/hybridclr_demo` | **Exact CI-tested implementation commit `2843c545ef1597f866ebd329ff27d4f73d58ba90`**; later doc-only commits are not new tested source |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` (unchanged D3 real Runtime/Codec) |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` (unchanged) |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` (unchanged D2–D4 native) |

Exact new code Git blobs:
- `Tools/AssemblyShadow/R03IR/D5Admission/d5b_preparation_v1.json`: `202c7847e4ae741902162391a4e4bd7a66e33c2c`
- `Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py`: `185c1bd6603a8c43e4222d30ed8bb057ab94824a`
- `Tools/AssemblyShadow/R03IR/D5Admission/test_d5b_custody_authority.py`: `d89da965d336ddc50e906036deecc5d8a18f5e46`
- `.github/workflows/r03-b2-d5b-custody-preparation.yml`: `5c988dbd880797b2b6841874b3ac2767fb4a164a`

[**Primary implementation/source evidence review**](D5B_SOURCE_CUSTODY_PRIMARY_REVIEW_2026-11-20.md) · [**next Player-producer/link preparation plan**](D5B_REAL_PLAYER_PRODUCER_AND_LINK_PLAN_2026-11-20.md) · [Independent D5-A review](D5A_INDEPENDENT_SOURCE_REVIEW_2026-11-20.md) · [D5 42-cell matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md).

**Actual CI**: [run 44725519765](https://github.com/night-outlook/hybridclr_demo/actions/runs/44725519765), demo head `2843c545ef1597f866ebd329ff27d4f73d58ba90`, attempt 1 **completed/success 2/2 jobs**. Ubuntu 24.04 job `136251811066`, macOS 15 job `136251811428`. Each raw log has **50/50 unit/source/synthetic cases PASS**, no unexpected assertion, and explicit `PreparedSourceOnly_NoLocalExecution`, `remoteSourceVerification=NotRun`, `nativeUnityInstallation=NotRun`, 18/18 Player `NoCoverage`, `D5BLocalExecution=NotAuthorized`. Run `44724709973` had an initial 13-versus-12 source-input test error; later superseded source runs are separately recorded in the Primary report. Do not classify any synthetic run as an actual Local result.

## 2. Independent reviewer checklist

1. **Role and transport separation.** Verify GitHub repo/branch/exact SHA and new source blob pins independently. Compare the demo bootstrap `b9776f7dc87170ba08bfed9021c0ee8546bceccf` to current HEAD, confirm no change in legacy B1 `current_native_candidate.json`, `current_native_source_gate.py`, `run_current_native_validation_cycle.py`, oneuse-12 receipts or three production repos. Verify disposable write smoke branch `codex/smoke-d5b-admission-20261120-b01` (commit `3c2d0253bb9b4fa2fcffa34bb5ed8d33300fac97`) did not replace feature HEAD.
2. **IR-D5A-04 old evidence-root counterexamples.** Independently inspect `check_proposed_custody` for mandatory six historical roles, proper original-S/B1 locations, full workspace/sibling source exclusion, symlinked/noncanonical parent, existing leaf, nested older root and a new *absent* child inside prior evidence. Confirm tests exercise the new nested case rather than the previous merely existing-root case. Identify whether supplied history map can still be forged/omitted without an approved handoff.
3. **IR-D5A-05 reviewed remote-authority contract.** Inspect `APPROVED_LOCAL_HANDOFF_BLOB=None`, `read_independently_approved_handoff`, `verify_live_source_heads`, `parse_remote_ref` and `run_git`. Prove there is **no code path** in this revision that accepts user self-claims/flags to grant Local execution. Confirm the future active source verification would compare actual `git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1` to the reviewed four-repo SHA and check local clean HEAD and correct remotes. Clearly state: tests monkeypatch the approval blob and Git results; **no real live remote readback was executed in D5-B CI**.
4. **Exact source-copy provenance, not fake native link.** Inspect `check_native_file_copy` source vs synthetic copy and all 12 expected `libil2cpp` inputs with Git blobs (separate from the 13th standalone allocator host). Verify negative mutation, symlink, missing file and injected `NativeHostTests` cases. No actual Unity installation, Bee DAG, compiler, binary UUID or Player evidence exists.
5. **CI source and negative tests.** Fetch/inspect all 50 case results and exact preview from **both raw job logs**, confirm no Unity/SDK/Player execution, retain prior failed/earlier runs rather than promoting them. Preserve expected 18 `NoCoverage` real Player cells.
6. **Review scope/gates.** Do not issue `PassD5BLocalExecution`; the only permissible positive disposition is a narrow approval for further **Primary test-producer/native-link preparation**, never Local Unity/IL2CPP Player execution. An actual approved Local handoff requires a separate user decision, new reviewed release source pins, real native build provenance and actual fault producers.

## 3. Required decision and explicit bounds

Choose `PassD5BCustodyForProducerPreparation`, `ReturnRequired`, or `Blocked`. A bounded pass must list any remaining source/approval and real-Player blockers and must **not** advertise an executable Local runner.

**Current authority:** `D5AIndependentReview=PassD5AForD5BPreparation`, `D5BSourceCustody=PrimaryCompleteSourceCI`, **`D5BSourceCustodyIndependentReview=Pending`**, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
