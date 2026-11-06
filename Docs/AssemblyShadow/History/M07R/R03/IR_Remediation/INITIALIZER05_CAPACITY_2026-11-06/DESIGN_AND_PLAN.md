# Initializer oneuse-05 — capacity readiness and preserved 25 GiB admission

Date: 2026-11-06 UTC. Primary Implementation Owner. Scope:
`IR-LOCAL-R03-INITIALIZER-04-CAPACITY-01` only, followed by the SAME
source-bound initializer native-recovery verification if actual disk
capacity becomes eligible. No R03/H2/Human Review Gate approval.

## Confirmed incoming Local facts

Oneuse-04 execution source was demo
`e0f52c008b6b244e58be135e9bdba46192b76d04`,
Local checkpoint publication
`c55950504e21b1a61044f818e1819946ec2dea7e`.
The two independent `statvfs` readings of the ACTUAL shared
`/Users/ah/GitHub/hybridclr/r03-local-validation` output parent on
device `16777230`:

| Time UTC | Available bytes | Available GiB | Short of 25 GiB |
| --- | ---: | ---: | ---: |
| 2026-11-06 07:40:41 | 26,557,333,504 | 24.733444214 | 286,212,096 |
| 2026-11-06 07:41:43 | 26,553,147,392 | 24.729545593 | 290,398,208 |

The mandatory25 GiB = `26,843,545,600 bytes`. Last deficit is
about **277 MiB**. The previous soft advisory40 GiB and hard
floor20 GiB have NOT changed. Local correctly returned
`CapacityBlocked`: runner0, Unity0, build0, Players0,
15/15 planned cells NotRun, neither new oneuse-04 root created,
no fresh product seal or VM recovery result. The original
pre-callback initializer exception is STILL UNKNOWN.
No current evidence proves what data consumed the disk.

The published oneuse-04 checkpoint and the preserved oneuse-01
BLOCKED / oneuse-02 FAIL / oneuse-03 FAIL and product seal
PASS are immutable. Original S 16,978 files, 17 old checkpoints,
2405 SDK inputs, 132 external evidence files, all old batch/host
inventories and all source bindings had Passed before/after
preservation. This historical status must not be modified.

## Primary decision: capacity, not code change

Do **not** lower any threshold, reinterpret an APFS "purgeable"
estimate as available bytes, overwrite an old root, relocate a
source tree, GC Git objects, clear Unity/IL2CPP/SDK data, delete
a backup, thin APFS snapshots, delete or move historical
evidence, redirect TMPDIR, or fake an alternate-device same
path. No current proof identifies an expendable path, so
Primary does **not** authorize ANY automatic deletion or moving
a path on the user's Mac.

There are two acceptable readiness conditions:

1. **User-controlled, separately authorized capacity action** on the
   SAME actual APFS output volume, limited to data the user
   independently establishes as disposable and outside all protected
   source/SDK/Unity/original S/evidence paths. The Local Agent may
   inventory externally suggested candidates read-only and submit
   exact real path, purpose, owners and size estimate for a user
   decision; it MUST NOT delete automatically or interpret a
   candidate listing as deletion authorization. Avoid generic
   `rm -rf`, disk cleaning utilities or whole-cache purges.
2. **Natural/external capacity increase**, e.g. space becoming
   available through a user action or other already controlled
   activity, provided that the actual SAME volume meets the gate
   in two new independently timed physical measurements.

A new **different mounted filesystem** is NOT part of this
authority. If the user wants an alternate volume, Primary
must separately design and source-pin the provenance,
host/evidence/SDK/cross-device policy and obtain explicit
approval first; no mount or symlink substitution.

At least the observed ~277 MiB deficit must be resolved;
additional several-GiB margin is **recommended** because
the next test creates an actual IL2CPP build and archives.
About 32 GiB available is a useful nonbinding goal, NOT a
new gate or promise. The mandatory minimum remains **25 GiB**
for both new readings; the advisory **40 GiB** is unchanged.
A momentary one-sample PASS is insufficient.

## Read-only implementation

`Tools/AssemblyShadow/R03IR/capacity_readiness.py` supplies
a small repeatable, no-write probe for readiness checks. It:

- Requires an existing canonical output parent, source workspace,
  original S checkout and Unity executable, and exact two
  **absent** canonical new roots.
- Uses physical `os.statvfs(parent).f_bavail * f_frsize` and
  `st_dev` on the real output parent; never an APFS
  purgeable-space approximation or host volume alias.
- Evaluates the fixed25 GiB criterion without lowering the
  fixed20/25/40 GiB values.
- Emits exactly **one real timestamped sample per invocation**
  as JSON on stdout, always with
  `eligibleForUnityRun=false` and
  `twoIndependentSamplesCompleted=false`. No source/CI/SDK
  attestation is implied. It never manufactures a second sample
  or creates an output root.
- Without `--candidate`, inspects **no arbitrary user files**.
  With an explicitly selected `--candidate /absolute/path`,
  inventories regular-file logical/allocated bytes and symlink
  count without following links. Rejects any overlapping source,
  original S, output parent (including all old batches), Unity,
  system/SDK-sensitive directory, foreign device, reused root
  or symlinked candidate root.
- Reports `bytesReclaimable=Unknown`. APFS clones, shared
  blocks and snapshots prevent a file-size estimate from
  certifying recoverable free space.
- Contains **no delete, move, purge or mkdir operation**,
  automatic cleanup, temporary root or background work.

`test_capacity_readiness.py` exercises the real CLI from a
foreign cwd, 25 GiB exact lower boundary, previous observed
shortfall, no implicit two-sample approval, path/symlink
negative guards and no mutation of protected bytes.
`.github/workflows/r03-ir-capacity-readiness.yml` runs
these host-only tests on Ubuntu24.04 and macOS15; it
cannot establish a real user Mac capacity PASS.

## Distinct readiness and one-use-05 authority

**Readiness is NOT a Unity execution or a one-use run.**
A Local Agent may run the read-only probe multiple times
while the user frees space; each sample must be labeled
as an independent observation, without entering
`R03IR-Initializer-20261106-oneuse-05`. It is inappropriate
to create that directory, its host sibling, an empty
batch ledger or seal for a readiness check.

Only after TWO genuinely fresh, separated timestamped
measurements BOTH meet 26,843,545,600 bytes, and the
normal source/CI/Unity/SDK/historical preservation gates
pass, does the following distinct next **single-use**
run become conditionally authorized:

`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261106-oneuse-05`
and its `-native-host-raw` sibling. Both must remain
absent until the actual runner is invoked ONCE. Use
the exact final pushed source pins; one fresh Unity
ON/Release macOS ARM64 IL2CPP build, two separate
initializer Players, exact native VM recovery/journal,
ten native host components, full preserved original-S
read-only audit and sealed host/product custody, per
the unchanged previous `INITIALIZER04_PRECALLBACK`
design and plan. This is not a oneuse04 replay.

If the gate remains below25, **STOP before the batch**,
record `CapacityReadinessBlocked`. The user must supply
capacity or explicit per-path approval; Primary cannot
free their Mac storage remotely. If the actual oneuse-05
admission is started then fails, publish a fresh
Blocked checkpoint, consume its one-use name and
return to Primary. Never retry it in-place.

## Nonacceptance

No observed native VM reason for oneuse04, no newly run
Player, and no first prepared-callback proof. Original
oneuse03's control/failure Both19/state9 pre-callback
still requires an actual next run. High
`IR-R03-01`/`IR-R03-02`, captured-generic error15,
full native V2/first-failure/general diagnostics,
original S source/object/link/Player closure, managed
shutdown, whole-VM epoch, GC/RSS, RC/P/E and
qualification remain open.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`, `qualificationApproved=false`,
`fullLegacyRegressionAcceptance=false`,
PureInterpreter disabled. No Human Review Gate, H2,
M08A, X02 or SNAP-01 work is authorized.
