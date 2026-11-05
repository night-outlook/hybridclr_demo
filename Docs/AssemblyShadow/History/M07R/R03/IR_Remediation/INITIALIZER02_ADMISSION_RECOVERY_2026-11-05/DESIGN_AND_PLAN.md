# Initializer oneuse-02 — Primary admission correction and recovery

Date: 2026-11-05 UTC. Project: HybridCLR Assembly Shadow R03.
Owner: Primary Implementation. Scope: `IR-LOCAL-R03-INITIALIZER-01-ADMISSION-01` only.
The previous oneuse-01 BLOCKED report remains immutable; this is not
a replay of a consumed execution or an independent R03 review.

## Verified cause

At executed demo `bf1e8283061fe3a94c56ea2ac9ab6445905cf738`,
the mandatory Mac readmission `current_native_environment_admission.py`
required the old Git blob `249c47c1b453fc0cd3520173122599ca03cbe78c`
for `PlayerFixtures.csproj`. The actual clean committed project is
`1c5c8628ead41d67d94bb1846dd5bf9764620c68`, resulting from the
reviewed additional explicit compile entry
`<Compile Include="InitializerNativeTargetFixtures.cs"/>`.
The readmission's real exit 2 and error are preserved under
`History/M07R/R03/local-validation-initializer-20261105-oneuse-01`.
The builder itself was not invoked; 15/15 cells NotRun, zero native builds,
zero Players, and no new root/seal. Both prior 25-GiB capacity samples
passed only at their earlier timestamps and grant no current GO.

## Primary source fix

Exact fingerprinting is **retained**, not disabled:
- `REQUIRED_CSPROJ_BLOB = 1c5c8628ead41d67d94bb1846dd5bf9764620c68`,
  including the sole reviewed initializer compile addition.
- `REQUIRED_INITIALIZER_SOURCE_BLOB = da4bf2ece4999d2765ca51d4bdeecf2bc0617fd2`.
- `REQUIRED_PROGRAM_SOURCE_BLOB = c8de453c03321a5b91635da7c6ed795664bcb975`.
- Readmission requires all three regular non-symlink files, exact Git
  object hashes, net8.0, explicit/default-disabled compile items, exactly
  one Program/TerminalProducer/InitializerNativeTarget compilation entry,
  and the exact opt-in generator dispatch in the reviewed Program source.

The legacy 249c blob is **not** on a loose allowlist: approving it would
not exercise the current initializer target. Original S, K and the old
fixture project remain historical read-only sources, not rewritten.

The local initializer runner, production VM/interpreter/package,
historical K target/Player checks, deterministic fixture bytes and A–K
records remain unchanged. No new runtime feature or override is introduced
by this source correction.

## Evidence and host test changes

Two explicitly triggered GitHub Actions workflows consume the same
current-source admission: `r03-ir-initializer-local-contracts.yml` and
`r03-ir-current-native-local-cycle-host.yml`.
The existing 29-case `current_native_environment_contracts.py` tests now
assert initializer+Program pin and compile inclusion. New
`initializer_admission_contracts.py` performs genuine reads of the exact
committed .csproj/C# files, positive readmission tests, failures for
preinitializer/missing/modified/duplicate/symlinked sources,
external-cwd fresh interpreter of the initializer runner without
PYTHONPATH, and a synthetic full `inspect` dispatch in which only
external Mac/Git/SDK/capacity is mocked. No fake Unity acceptance is claimed.

Authoritative Local successor requires **fresh completed/success
macOS and Ubuntu jobs for both workflows at the same FINAL pushed demo
SHA** and independent local preflight with fresh exact Git/SDK/Unity,
preservation and two >=25-GiB samples. Source-only CI is not a native
IL2CPP build or a real Player.

## One-use-02 design and stop rule

Maintain the already reviewed 15-cell initializer runner. Authorize only
a new external absent root
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261105-oneuse-02`;
never reuse the absent-but-reserved `oneuse-01` name or its prior samples.
After all fresh preconditions and exact-source CI pass, perform the same
one fresh ON/Release IL2CPP Unity 2022.3.62f2 macOS ARM64 build, two
initializer-control/failure Player processes, real ten current-native
host components plus additive initializer host tests, and read-only
original S nine-part/90-cell archive, 59 process joins, generated-source
and archived Mach-O checks. Preserve raw request/PID/native V1/build
provenance, logs, failed receipts, independent source/postflight checks
and evidence seal. There are no retries.

A host admission PASS only removes the documented oneuse-01 preflight
blocker; it does not imply that Unity native compilation or Player
execution succeeds. All independent High IR-R03-01/02 and R03 RC obligations
remain open. Captured-generic error15, native V2 first-failure/complete
diagnostics, original source-object-link-process closure, managed shutdown,
whole-VM epoch, GC/RSS, and P1/P2/E0/E1/P3 are NotRun/NotProven.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`,
`qualificationApproved=false`, `fullLegacyRegressionAcceptance=false`,
PureInterpreter disabled. Human Review Gate not approved.

## Stop and return

The future Local Agent must STOP if the current independent readmission
fails, a capacity sample is below 25.0GiB, preservation/source/CI differs,
or a native build/Player fails. Publish the *actual* oneuse-02 return
without altering original 01 raw or history, and return non-trivial
implementation defects to Primary for a new controlled source cycle.
