# ADR-0001: pinned local libil2cpp source composition

Status: selected for M00; acceptance requires the baseline Player and review.

## Context

The interpreter repository does not own Unity's assembly/image/class/reflection
resolvers. They live in il2cpp_plus/libil2cpp. The starting native fork was on a
2023-era 2022-3.x revision, while HybridCLR package 8.14.1 specifies
v2022-8.14.0. Installing an unpinned branch would hide that mismatch.

The current Unity project has a running Editor and unrelated local changes.
Unattended builds must not interfere with that session.

## Decision: option B, verified local source installation

Maintain the independent night-outlook/il2cpp_plus fork and start the native
development branch from exact upstream commit
11251b938d2ce7fa865165130bf257ca239db69f (v2022-8.14.0).

The opt-in `PinnedSourceInstaller.Install()` reads
ProjectSettings/AssemblyShadowSourcePins.json. Local paths are resolved relative
to the project. Native and package repositories must have exact pinned HEADs
and clean sources. Source files are compared against committed Git blobs before
copying, then the installed inventory and immutable SHA-256 hashes are checked.

Composition is:

1. Copy pinned il2cpp_plus/libil2cpp into private staging.
2. Copy pinned hybridclr/hybridclr into staged libil2cpp/hybridclr.
3. Invoke the existing local installer using this verified staging tree.
4. Check copied bytes and write assembly-shadow-install.json.
5. Remove only this installer's private staging area.

The existing ordinary installer is unchanged unless the opt-in entry point is
called. UPM package filesystem paths are resolved through PackageInfo so the
local package does not have to be physically embedded under Packages.

The receipt names exactly four mutable generated outputs:
AssemblyManifest.cpp, MethodBridge.cpp, UnityVersion.h and libil2cpp-version.txt,
all under hybridclr/generated. Everything else must match the source pairing.
The independent verifier does not trust a receipt-provided arbitrary exclusion.

## Native feature mode

AssemblyShadowConfig.h defines HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW to zero unless
the native compiler explicitly supplies zero or one. M00 has no resolver hooks.
Build scripts set native compiler flags for OFF/ON independently of C# symbols.
Generated bridges and caches are build outputs, never source revision evidence.

## Consequences and limits

- Local CI can reproduce the pairing after checking out the same four source
  commits. Remote URL/exact-SHA clone mode is deferred to M08, not implemented
  prematurely in M00.
- The original dirty demo and Editor remain untouched; the clean worktree is
  the source of build evidence.
- Clean cache helpers move only selected native caches into a recoverable
  task-specific backup and reject an active project Editor.
- macOS ARM64 is the available target. Other platforms require their own tests.
- M01 must pass its real old-bundle test; a successful ordinary baseline does
  not establish the feasibility of Assembly Shadow.

## Rebase

Preserve old pins/tags, inspect a chosen upstream Unity 2022 commit on a new
branch, re-run OFF and ON Player tests, obtain independent review, then update
the four-repository pairing. Never silently move a pin to main.
