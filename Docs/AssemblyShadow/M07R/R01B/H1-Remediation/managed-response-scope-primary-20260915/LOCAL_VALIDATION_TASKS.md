# Local Validation tasks — source anchor `5f561abd`

Run fresh V00–V05 from the authoritative `WEB_TO_LOCAL.md`. Do not reuse the failed `dc9116a` V02 result as acceptance for the new source anchor.

## V00 — preflight

- `git pull --ff-only` candidate branch and record checkout HEAD plus source anchor.
- Verify `AssemblyShadowSourcePins.json` and `source-targets.json` both bind `5f561abdfbe020d1d480594a2130c5ec846c0e6a`.
- Verify protected native/package/IL2CPP/reproduction/performance identities.
- Run committed handoff/source preflight into a new immutable evidence root.

## V01 — affected regressions

- Run full bounded H1 Python inventory, including both managed provenance suites.
- Compile candidate and reproduction in Unity and run focused affected Editor tests.
- Preserve exact test IDs/log/XML/failures/skips.

## V02 — real unchanged-Bee-cache proof

- Preserve the normal Bee cache; do **not** clear it to force Csc execution.
- Build a fresh candidate ON/Debug smoke through the managed-provenance wrapper.
- Require schema 3 for fresh managed begin/capture/proof.
- For each required assembly, inspect the selected compilation's `responseSources` and `responseFiles`; membership must be exact and recursively complete.
- Unrelated DAG responses, including legitimate CodeGen staging responses, may change without invalidating a required chain when they are not in that action's recursive closure.
- Any direct or nested response used by a required action must remain byte-identical; mutation must fail closed.
- Still require unchanged graph/action/dependencies/Csc output/downstream outputs, exact reachability, unique chain and exact fresh Player path/SHA/size binding.
- Require `evidenceMode=BeeCacheHitBoundToFreshPlayerInput` for a legitimate unchanged cache hit and `freshCompilerExecutionClaim=false`.
- Do not use legacy `--reuse-proof` to satisfy this requirement.

## V03 — fresh provenance-bound build set

- After V02 passes, run fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release through the established strict provenance flow.
- Require native provenance, managed provenance, input snapshot/build receipt binding, store verification and exact restoration.
- Stop and return to Primary on unsupported/ambiguous Bee structure; do not broaden response/source/dependency rules locally.

## V04 — runtime/count/startup/capacity/performance

- Run the established 132 candidate count cells, 8 unfixed reproduction cells, fresh baseline/fixtures/replay, 11 startup modes, capacity/lazy/dense/FieldRVA/generic/array/reflection and affected M03–M07 checks.
- Run controlled Development performance only where both candidate and preserved reference support the workload.

## V05 — successor/M08

- Seal the successor archive/index only from explicit fresh evidence locations.
- Run strict semantic verifiers and a genuine independent whole-chain M08 review.
- A tool/CI/V02/V03 PASS is not M08 PASS.
- If independent M08 passes, stop for explicit Human Review Gate. `humanGatePassed` must remain false until then.

**Never begin R02 in this Local cycle.**
