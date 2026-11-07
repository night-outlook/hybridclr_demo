# R03 captured-generic A1 — independent-owner CLR structural prerequisite

Date: 2026-11-07 UTC. Owner: Primary Implementation. Scope: **R03 / IR-R03-02 / A1 only**. This is **not** a native method guard fix, IL2CPP Player run, Local authority, native V2 receipt, independent R03 review or Human Review Gate.

## Design intent and actual source

The pinned native `night-outlook/il2cpp_plus` at `41764ae1eeefb33b05966e7f7676e52aae39c340` already has `AssemblyShadow.cpp::CapturedArgumentVisitor`: it traverses the *physical* method/class generic context, including `method->genericMethod->context`, and rejects an active shadowed baseline type with `Fail("CapturedBaselineType", candidate)`. Its error is `BaselineAlreadyUsed` (15) when the candidate is shadowed. The method's declaring AOT assembly is a **different** identity from a captured baseline type's physical assembly. A matched method owner alone does not establish a captured argument.

New test-only `Tools/AssemblyShadow/R03IR/PlayerProject/R03CapturedGenericAotOwner.cs` defines `AssemblyShadow.R03.IR.R03CapturedGenericAotOwner.Touch<T>() where T : class`: a non-inlined, observable counter increment with no static `Methods` assembly reference. `WarmShared()` only calls `Touch<object>()` so future Player source can preserve a reference-generic AOT instantiation without early use of `Methods.R03.Node`. The source has conditional Unity `Preserve` attributes but **has not been copied into an actual Unity project or built by IL2CPP**.

The isolated `CapturedGenericHost` .NET8 project links this identical owner source with the existing `EvolutionFixtureCorpus.Build("Methods")` producer. It emits a new, host-only real `Methods.dll`, loads it into a collectible `AssemblyLoadContext`, obtains its physical `R03.Node` Type, and constructs `Touch<Methods.R03.Node>` via a genuine closed CLR `MethodInfo`. It requires:
- owner Assembly = `R03CapturedGenericHost`, captured Type Assembly = `Methods`, distinct physical owners and no compiled owner static AssemblyRef to `Methods`;
- exactly one reference-constrained method type parameter and a real constructed MethodInfo with the exact physical argument;
- `Touch<object>` shared warm control, then reflected and delegated calls to the actual closed method returning42 and incrementing owner counter 1→2→3;
- explicit rejection by the **host witness contract** of a same-owner argument, and actual CLR rejection of the disallowed value-type generic argument.

The Python consumer `verify_captured_generic_host.py` rejects mismatched bytes/source anchors, missing/different owner or captured argument, numeric/boolean substitution, wrong side-effect counts, duplicate JSON keys, original-S misattribution or any claims that IL2CPP, a native method guard, error15, runtime acceptance or H2 occurred. `test_captured_generic_host.py` exercises one real positive + adversarial structural/byte/source mutations. The host refuses a second write into its consumed temporary output directory.

## Actual CI evidence

The first host CI attempt at demo `39d182bc82289e97f4fdd2aece424f3548411523`, run `42363693573`, FAILED in C# compilation because dnlib's `ModuleDef.Mvid` is `Guid?`; it was not converted safely to `Guid`. Primary fixed this by requiring a nonempty `HasValue` before reading `.Value`, with no source-input or runtime changes. The original failure remains Failed.

The next exact-source run **42363760691**, demo `353617ca0461a5df34f57e44784adae0525b7277`, completed **success** on `ubuntu-24.04` and `macos-15`. Each built the actual net8 C# program with **0 errors, 0 warnings**, executed the real CLR closed-generic owner/argument fixture, passed the strict host consumer, and passed **8 Python tests** (including >35 internal mutation cases) and the no-reuse negative control. It did **not** execute any Unity/IL2CPP code.

The raw host fixture metadata is the same nominal MVID `4773fc19-55e6-0b61-bd26-4e01952444ca` and 2,048-byte size on both CI OSes, but the **physical Methods.dll SHA-256 differs**:

| Actual host OS | SHA-256 of newly generated host Methods.dll |
| --- | --- |
| Ubuntu 24.04 | `ecd0438188ffe0c633fcf1997e2ac508ee2fd4beca7e33125c883712a1a6cd08` |
| macOS 15 | `3e7ea51b72b877d93860e61caae845fe389f43ec999ffab083ab60f7c332fb6c` |

The origin of byte drift has **not** been demonstrated. Matching MVID does NOT establish matching DLL bytes, and neither independently emitted host file is the original S baseline or approved as an actual Player input. Future A2 must pin the exact relevant physical execution bytes and must not reuse these OS-dependent digests as interchangeable authority.

## Boundary and the next unfinished Primary-owned step

A1 proves a **CLR-host structural prerequisite only**. It does not demonstrate that the Unity IL2CPP runtime constructs the same inflated MethodInfo, its native `method_inst` contains a physical baseline Methods TypeDef rather than a logical shadow type, that the intended native guard executes, or that terminal error15 and physical post-poison no-side-effect behavior occur.

**Next A2 design/implementation blocker:** acquire or retain the physical baseline type/generic argument without triggering the startup baseline-use barrier before Shadow publication. The native source installs candidate tracking at startup when configured; `RecordBaselineUse` can record class/reflection/initialization use and cause `ValidateTransaction` or `CommitTransaction` to reject the update early. Conversely, ordinary post-publication logical type lookup may return the interpreter shadow type instead of the physical baseline. No proof currently supports either shortcut.

Primary must implement a test-only, source-authenticated way to obtain the genuine physical baseline generic argument and to construct/observe an **actual runtime-inflated method context** belonging to this separate owner, with a native observer that records owner vs argument assembly/type handles, original first failure, state9/error15 and unchanged counter, without executing method bodies after poison. It must undergo focused host/C++/managed API validation and independent source review **before** a fresh single-use Local validation batch is proposed. Do not fabricate MethodInfo pointers, synthetically set failure15, relax candidate-use admission, or modify original S/initializer oneuse-07 fixtures.

Current `Handoff/WEB_TO_LOCAL.md` remains **CLOSED**; the consumed oneuse-07 remains focused PASS, independent R03 overall FAIL and High `IR-R03-01/02` open. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`. PureInterpreter disabled. No later milestones or automatic Human Review Gate.
