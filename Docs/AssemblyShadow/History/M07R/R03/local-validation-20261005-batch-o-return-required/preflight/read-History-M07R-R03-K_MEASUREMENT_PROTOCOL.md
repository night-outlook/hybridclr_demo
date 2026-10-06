# R03 K — current-source observation protocol

Status: prepared for Local batch I. This is diagnostic/measurement evidence, not a release SLA or H2 approval.

## Objective

Obtain comparable current-source observations after R03 changes without using the test-only finalizer lease or the R03 runtime probe as a performance optimization. Preserve the previously accepted R02 CPU residual and H1 RSS risk; this protocol does not waive either.

## Fixed profiles and workload

Use the fresh resource-complete source tuple and the existing R00 verifier/workload. Run each of the four original modes three times in fresh processes:

- feature OFF/no patch;
- feature ON/no patch baseline control;
- feature ON/P01;
- feature ON/P03.

Each process uses the same Unity 2022.3.62f2 StandaloneOSX/arm64 development-IL2CPP build class defined by the existing R00/M07 toolchain. The diagnostic producer lease and R03 runtime probe are not enabled in this measurement group. The same original R00 operations/phases and verifier remain authoritative.

The execution supplement observes existing M06 static, delegate and exception rules after the original R00 receipt is produced. Its interval is explicitly excluded from the original measured interval and it does not claim the full M06 matrix.

## Samples and retained quantities

For every mode/operation/phase retain three raw `nanosecondsPerIteration` samples and report min/median/max without manufacturing a new threshold. Retain the original process/managed/native memory fields already emitted by the R00 receipt, build/source hashes, PID/run identity and exact app receipt.

Also retain fresh early-startup/capability observations in their separate cells; do not merge those timings into the R00 distribution.

## Interpretation

- `releasePerformanceAcceptance=false`.
- `noiseOrOverheadThresholdClaimed=false`.
- No subtraction of unrelated background/finalizer work is allowed to make a performance result pass.
- H's isolated warm-certificate proof remains a correctness/diagnostic witness, not an unisolated production timing profile.
- A Local batch may return all measurement cells Passed when the fixed protocol and original contracts execute correctly. That means the observations are trustworthy, not that a product performance budget has been approved.
- Any materially adverse result is returned to Primary with raw samples and existing risks; acceptance/defer decisions remain owner/H2 work.
