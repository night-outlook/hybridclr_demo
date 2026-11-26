# D5-B runner artifact closure — AP2 independent review request

Client date: **2026-11-25, America/Los_Angeles**. Preserve earlier UTC labels.

**Requested verdict: `PassRunnerArtifactClosureSourceOnly` or `ReturnRequired`. Current AP2 independent status: Pending.** This request permits source review and isolated source-host fixtures only; it cannot issue Local execution or full activation approval.

## 1. Exact review target

Review `night-outlook/hybridclr_demo` source `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`: [verifier][module], [tests][tests], [design][design] and [Primary evidence][primary]. The unchanged sibling identities are `hybridclr` `c3c232023724cbad565b85e9b2c3beea8ce2789a`, `hybridclr_unity` `948c0e3b4f8891481301770115e8ba4945eea6de`, and `il2cpp_plus` `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`.

The AP1 R2 review at `653930479b37230d757ed8a089e320b0ac53998b` remains `PassActivationPublicationProposalOnly`, closing `D5B-AP1-IR-01`. R5 remains `PassDryAdmissionSourceOnly`. AP2 preserves nine baseline blobs: the five R5 files, preflight profile, custody-authority module, AP1 auditor and AP1 tests; the existing 94/22 methods remain intact.

## 2. Questions for independent assessment

1. **Publication and policy:** C follows A outside its tree and binds H/A/E, canonical repository identity/ref, locations and an exact roster. It does not bind a literal origin URL; accepted canonical spellings are checked and the observed URL is recorded. Its external blob pin conveys identity, not authority. Confirm exact schema/policy and closed fields. Future Q binds C externally; no self-hash is embedded.
2. **Direct closure:** Five runner-owned files—wrapper, derived writer, imported preflight, plan and runner-relative profile—plus E are checked against real Git objects and checkout bytes. Source-inspection datasets under H remain separate. Verify the changed-helper-in-H case that AP1's two-path delta alone cannot cover.
3. **Trusted helper:** AP1 R2 blob `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` is verified before loading. Candidate modules remain inert; the preserved AP1 object/topology/ref/delta checks continue to apply. The verifier, Python/stdlib, Git and OS remain external trust assumptions.
4. **Observed checkout:** Assess exact branch/HEAD/ref, ordinary private `.git`, full committed-tree/index equality and verifier-owned raw-byte inventory. No Git `status`, `diff`, `hash-object` or worktree conversion is used. Missing/untracked/ignored entries and extra empty directories reject. Check unsupported config/index/layout rejection and protected-root separation. Origin spelling is not remote authentication; protected roots are not source/evidence admission.
5. **Bounded reads and reporting:** The six artifacts remain regular, single-link, `100644`, non-executable and at most 1 MiB. Wider scans support UTF-8 paths, single-link regular/symlink leaves, owner-execute-bit equality and literal symlink bytes without following targets. Limits per scan are 256 MiB per regular leaf, 4 GiB total leaf bytes, 100,000 entries and depth 64. Assess raw-byte/fingerprint rechecks; no converted/LFS/smudge/line-ending materialization, cumulative I/O/memory/time sandbox, runtime isolation, continuous custody or ABA exclusion is claimed.

The API is `make_closure_proposal(repo, source_commit, runner_commit, runner_ref, locations)`, `canonical_bytes(value)`, `git_blob(raw)`, and `verify_runner_closure(raw, expected_blob) -> VerifiedBundle`; `BundleFile` holds `path`, `git_blob`, `raw`, and `report` returns a copy. The constructor validates objects/location spelling without asserting custody. `main(argv=None)` exposes only `--closure` and `--expected-closure-blob`, requiring trusted Python **`-I -S -B`**; the programmatic API assumes a trusted process.

Report kind: `R03D5BRunnerClosureObservationV1`. Results: `RunnerArtifactClosureObserved_NoExecutionAuthority` or `RunnerArtifactClosureRejected_NoExecutionAuthority`. In particular, `runtimeImportIsolationVerified` and `runnerExecutableClosureVerified` remain false even on success.

## 3. Evidence binding

Internal Primary peer review found mutable configuration-selected filters reachable through the earlier Git-status comparison. The mechanism was removed. Test 17 retains its injected ancestor replacement and rejection, with its regex also accepting the new scan's earlier `Tracked directory changed during scan` error. This is not independent approval. A focused 25-method run passed in 20.623 seconds; the final combined evidence below is separate and takes precedence.

Outer unittest harnesses use Python `-B`; AP2 tests 19/20 launch the actual verifier CLI with `-I -S -B` and check each missing flag. CLI isolation is not attributed to the outer harness.

[Run 45774292828, job 139754092541][ci] targets `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`.

| Suite | Methods | Host seconds | CI seconds |
|---|---:|---:|---:|
| R5 | 94 | `0.189` | `0.188` |
| AP1 R2 | 22 | `11.934` | `4.220` |
| AP2 | `25` | `19.305` | `6.797` |

Host: Python `3.12.14`, fixture Git `/usr/local/bin/git — git version 2.56.1`, auditor Git `/bin/git — git version 2.47.3`; retained log `23828` bytes, SHA-256 `11651964c906570888ca035e1d5aa6e5db7f63fcb7be5801d2060f75f2f6c3d2`. CI: Python `3.11.18`, fixture Git `/usr/bin/git — git version 2.56.1`, auditor Git `/bin/git — git version 2.56.1`; retained log `47973` bytes, SHA-256 `f86025615a33de28d13ab585230dd5b6a238039d66afff0db6187253ecfdf105`. Exact case/blob/transport provenance accompanies the Primary record; method totals must not be treated as subcase totals.

## 4. Verdict scope and gates

Return a bounded verdict with concrete findings and reproducible source-host evidence. `PassRunnerArtifactClosureSourceOnly` may accept only this artifact/checkout observation contract. Use `ReturnRequired` for a material defect or unsupported verification claim.

No production A/E/C/Q was created. Full source admission/live refs, runtime import isolation, plan authorization, Q authority/revocation, physical custody and explicit user approval remain deferred. The production approval constant remains `None`; the closed plan and deliberately non-executable proposal kind remain unchanged. All Local gates remain CLOSED, Unity/native remains `NotRun`, and all 18 Player cells remain `NoCoverage`. Neither verdict creates a Local handoff.

[module]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py
[tests]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py
[design]: D5B_RUNNER_CLOSURE_AP2_DESIGN_2026-11-25.md
[primary]: D5B_RUNNER_CLOSURE_AP2_PRIMARY_2026-11-25.md
[ci]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45774292828/job/139754092541

## 5. Reviewer read order and publication boundary

1. Read `Docs/AssemblyShadow/README.md` and the current closed `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` checkpoint at the latest verified publication HEAD.
2. Read the [AP2 design](D5B_RUNNER_CLOSURE_AP2_DESIGN_2026-11-25.md), [Primary report](D5B_RUNNER_CLOSURE_AP2_PRIMARY_2026-11-25.md), [machine evidence](D5B_RUNNER_CLOSURE_AP2_EVIDENCE_2026-11-25.json), [retained CI log](D5B_RUNNER_CLOSURE_AP2_CI_45774292828_JOB_139754092541.log) and [host log](D5B_RUNNER_CLOSURE_AP2_SOURCE_HOST_2026-11-25.log).
3. Inspect the exact four-path source commit `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a` and confirm the successor is documentation/evidence only. Freshly resolve all four canonical feature refs; distinguish publication HEAD from tested source.
4. Independently assess the bounded contract and, where useful, rerun isolated source-host fixtures. Preserve the R5/AP1 reviewed blobs and AP2 source during review; return material source changes to Primary.
5. Publish a separate AP2 verdict and evidence under this history directory. Update README/CURRENT_STATUS as appropriate for the independent role; preserve Primary/Local ownership and all CLOSED gates. Stop after independent publication/readback.

Focused CI attempt **1** returned **1 successful job / 10 successful steps**. The source-host literal inventory check and raw CI log independently confirm **94/22/25** methods. No uploaded Actions artifacts are claimed; the exact decoded CI bytes are committed with BOM preserved. Internal peer rereads and the preparatory 25-method run are Primary development evidence, not this requested independent verdict.
