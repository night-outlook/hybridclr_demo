# H1 continuation source delivery — 2026-09-14

**Scope: source, validation tooling, focused tests, successor packaging support, and local execution instructions. This is not new Player evidence, M08 PASS, or H1 approval.**

This continuation starts from the transfer package and live coordination snapshot on `codex/assembly-shadow-r01b-h1`; it does not restart H1 remediation from M00. The governing state remains: H1 `InProgress`, technical readiness `Blocked`, latest independent M08 `FAIL`, `humanGatePassed=false`, `readyForHumanH1=false`, and `mayEnterR02=false`.

Read [LOCAL_CONTINUE.md](LOCAL_CONTINUE.md) first and execute [LOCAL_VALIDATION_TASKS.md](LOCAL_VALIDATION_TASKS.md) in order. Implementation details are in [IMPLEMENTATION.md](IMPLEMENTATION.md), source/provenance boundaries in [SOURCE_BASIS.md](SOURCE_BASIS.md), and successor evidence requirements in [SUCCESSOR_PACKAGE.md](SUCCESSOR_PACKAGE.md).

## Prepared changes

| Area | Prepared work |
|---|---|
| witness contract | Align the real M02 Python reader with the six-site current H1 configuration while retaining historical five-site readability. Current H1 requires exact schema/transformer 4, method hashes/operation index, fixed DLL hash/provider and semantic variants. |
| witness runtime checks | M02 Player probe checks the actual generated witness guard for null/tampered bytes, caller-byte immutability and zero AssemblyResolve side effects. Positive load remains in the fresh count witness path. |
| native compiler provenance | Interpret actual Bee compile actions per translation unit, recursively expand retained response files, honor ordered `-D/-U`, and treat `NDEBUG` by definedness. Candidate four-mode and reproduction two-mode summaries are separate. |
| managed source provenance | Freeze Bootstrap/Diagnostics source/configuration before BuildPlayer and bind actual Player DLLs to retained Csc/ILPP graphs. Explicit byte-identical reuse requires a reverified direct prior proof and is never automatic. |
| successor packaging | Require schema-2 raw count evidence/132 cells, fresh startup11, eight-cell reproduction, compiler/managed provenance and explicit archive membership. Integrity validation never sets M08/H1 flags. |
| test identities | Record NUnit/Python leaf test IDs and non-pass outcomes rather than trusting aggregate counts alone. |

Portable validation performed before publication: 102 new Python unit tests, 12 delivery/application tests, and 6 standalone clang macro-semantics checks passed. These checks do not constitute Unity compilation, IL2CPP build, or Player acceptance.

## Publication boundary

The source/tooling continuation is committed to the candidate and reproduction demo branches. Historical evidence, coordination snapshots and old build receipts remain immutable. No native runtime algorithm, `hybridclr_unity`, or `il2cpp_plus` source is changed by this continuation. The reproduction branch receives diagnostic/provenance tooling only; it must keep the unfixed native behavior used by the counterexample runs.
