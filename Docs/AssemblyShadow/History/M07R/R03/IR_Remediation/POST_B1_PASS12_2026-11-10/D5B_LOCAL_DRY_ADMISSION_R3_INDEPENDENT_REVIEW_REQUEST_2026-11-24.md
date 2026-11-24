# Independent review request — D5-B prospective dry-admission R3 receipt durability

**Status: PENDING.** A **separate independent reviewer** (not Primary Implementation / Local Validation) must assess the R3 focused response to [independent R2 `ReturnRequired`](D5B_LOCAL_DRY_ADMISSION_R2_INDEPENDENT_REREVIEW_2026-11-24.md): final positive receipt/fsync safety and descriptor-close partial-output accounting. Read [R3 design amendment](D5B_LOCAL_DRY_ADMISSION_R3_DESIGN_2026-11-24.md) and [Primary R3 implementation/CI evidence](D5B_LOCAL_DRY_ADMISSION_R3_PRIMARY_2026-11-24.md) as guidance only, not proof. Independently inspect actual pinned code/test bytes, confirm the exact fresh raw CI and look for additional counterexamples. This request grants **no** local execution authority.

## 1. Exact four-repository source tuple and file custody

Branch for every repository: `codex/assembly-shadow-r01b-h1`.

| Repository | Immutable R3 source revision |
|---|---|
| `night-outlook/hybridclr_demo` | **`eeba27a51e46dd5304da108e14285a1ad5ccd10d`** (exact code/CI tested) |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

Use GitHub Connector to check canonical repository identities, branch HEADs and the *exact code* commit independently. Diff old independent R2 branch HEAD `hybridclr_demo@a909909d724c33515eee41458311f122fc745ce4` to R3 **code SHA** `eeba27a51e46dd5304da108e14285a1ad5ccd10d`; require only three D5Local/CI file changes and no edits in historical B1/D5-A/B, earlier independently reviewed C10/RR5 source inputs, the Unity package or native forks. Diff R3 code SHA to current demo branch HEAD and verify any differences are documentation only.

| Actual file to read | Reviewed R3 Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `3cf4e746bc1cd361d162ab4681af3d6d0281ae37` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `0698cff62f1e8a0437c8f2e808dfa504b36106da` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `ee768deafb7b229d7e0b9b0ef74cf9d04d710095` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` (unchanged) |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` (unchanged) |

## 2. Mandatory source and test review

1. **R2-IR-01 — final receipt after-flush failure:** read `_write_locked`, the new durable `INCOMPLETE.json` veto, final `LOCAL_BATCH_STAGING.json` writer/readback, atomic same-directory `os.rename(...,src_dir_fd,dst_dir_fd)`, directory `fsync` **while veto remains**, and last `os.unlink(INCOMPLETE)` commit. Confirm a source-visible positive `LOCAL_BATCH_RESULT.json` cannot become **structurally admitted** after stage-file fsync, final directory fsync, rename or unlink errors. Examine the exceptional case where final bytes exist and match manifest but `FAILURE.json` is also unwritable. Verify tests 67–70 are genuinely injected *after* complete bytes are written, not just a pre-write short circuit. Check what may reappear after a crash and whether any unresolved durability assumption is appropriately bounded.
2. **Fail-closed physical verifier:** independently review `_committed_receipt_structure` and `inspect_dry_receipt_structure`. Require exclusive five-file canonical list, explicit rejection of incomplete/staging/failure/unexpected entries, exact v3 manifest SHA-256 and byte-size joins, and a final result that does **not** assert Unity/Player/R03 acceptance. Inspect test 66 (positive) and 74–76 (negative). Attempt to construct false positives such as a partial final JSON, a correct positive file without durable commit, a failure marker or a duplicate manifest entry. State residual source-only limitations.
3. **R2-IR-02 — cleanup state:** verify the parent descriptor is closed **before final visibility commit** and its failure keeps the incomplete marker; verify root descriptor cleanup errors are caught in the **same root-created accounting**, not a fall-through `finally`. The public CLI must return `outputCreated=true`, `retryAllowed=false`, and `IndeterminateAfterCommit`/`requiresPhysicalReconciliation=true` when a postcommit descriptor-close error occurs. Confirm test 71, 72, 73 inject actual descriptor-close faults instead of only mocking a caller status. Check preservation of original exceptions and that no cleanup failure can silently produce `outputCreated=false` or false success.
4. **Existing custody/source contract:** read actual source inspection calls and approvals, not just author comments. `approved_envelope(approved_raw)` must be invoked inside the writer; same-source and physical historical/parent identities and live Git remotes must be rechecked before writing, after preliminary files and before atomic final commit. Current production `APPROVED_EXECUTION_ENVELOPE_BLOB` must remain `None`. No Local or Unity runs are permitted; 18/18 D5 Player cases remain `NoCoverage`.
5. **Exact raw CI and failed attempts:** independently fetch [run 45375970635](https://github.com/night-outlook/hybridclr_demo/actions/runs/45375970635), push attempt 1, immutable demo SHA `eeba27a51e46dd5304da108e14285a1ad5ccd10d`, job `138382258238`. Inspect the **full raw log**, require `completed/success` 1/1, `Ran 76 tests in` / `OK`, individual test_66–test_76 outcomes, and the public wrapper `--mode execute` exit 2 with `NotAuthorized`, `outputCreated=false` and Local CLOSED. Historical run outcomes remain independent: `45375634381`, `45375689831`, `45375922233`, `45375960396` failed; `45375806304` passed an older 65-test code; do not promote any of these to R3 success.

## 3. Decision, risk boundary and publication

Publish a **new independent report** covering design → exact Git source/test → raw CI, with fixed blob IDs, genuinely reproducible source/synthetic host findings, per-finding closure and a single verdict: `D5BDryAdmissionR3IndependentReview=PassDryAdmissionSourceOnly` **or** `ReturnRequired`. Do not approve via Primary's self-check, do not implement further R3 fixes while acting as the reviewer, and do not begin D5-C/D, H2, D6, M08A, X02, SNAP-01 or Human Review Gate. If new defects are found, route focused findings back to Primary with source anchors and failing evidence. The older R2 `ReturnRequired` is not superseded by an R3 primary CI PASS alone.

**Even if source-only review passes**, actual Local dry admission remains unapproved without a **separate explicit user execution decision**, an immutable independently reviewed non-null approval envelope, physical macOS source/SDK/Unity checks, a new exact pushed four-repo handoff and a fresh one-use evidence root. No real Unity/IL2CPP/Bee/native VM/Mach-O/GC/PID/Player evidence was executed here.

**Hard stop:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; 18/18 D5 real Player cells `NoCoverage`.