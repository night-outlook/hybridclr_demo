# R03 oneuse-D — pre-Local net8 generator proof (2026-10-29)

## Problem and bounded scope

The active oneuse-D coordinator has not run on the Local Mac. The prior oneuse-C coordinator failed at standalone Python CLI import before any Unity native build. The separately existing fixture CI compiles the real .NET generator but previously triggered only on generator-source changes, used full demo/package checkouts, and did not bind IR output to the separately pinned binary SHA/MVID or two independent fresh generations.

Before consuming oneuse-D, address this host/tooling risk **within R03 only**. Leave the original S archive, all prior receipts, product C++/C#, original R03 source pins, IR Player fixture, current-native source pins, and existing ten-stage Local coordinator unchanged.

## Design

- Extend the **existing** GitHub Actions fixture workflow with bounded sparse demo and package checkouts (actual compiler inputs), pinned .NET SDK 8.0.318, and no-server compiler flags consistent with Local.
- Compile the actual `PlayerFixtures.csproj` on Ubuntu and macOS. Execute `--output` in a new CI-only directory to generate 15 comparison files, then `--ir-target` in **two distinct absent** directories. Demand that running `--ir-target` at an already occupied directory fails.
- A separate pure Python verifier requires the actual target `Methods.dll` SHA256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd` and MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`, real byte length, expected schema/field/method, editor layout admission, Boolean safety flags, distinct original target, 15 unique original comparison entries, and exact repeatability.
- Preserve the pre-existing original-S historical inventory lookup, pinned by Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`, but correct its false byte-equivalence invariant: fresh original-mode outputs have non-reproducible MVID/serialized bytes. Enforce the 15-item path, assembly, references and size comparison; verify regenerated file bytes against their own inventory; report **all** SHA/MVID differences as historical nonidentity, without treating them as a failure or adopting these bytes. Original S comes solely from the separately authenticated fc55 archival worktree, not regenerated CI output.
- Add sixteen adversarial host-only tests for checksum forgery, receipt mutation, duplicate keys, wrong types, symlinks, missing/repeated roots and forged acceptance. Their positive test uses synthetic bytes with a temporary expected hash override and expressly does not prove real generator or runtime behavior.
- Change only read-only admission's **advisory** capacity threshold from 30 to 40 GiB, consistent with `WEB_TO_LOCAL.md`; preserve 20 GiB hard floor and no-write behavior, add 35/40 GiB boundary regression cases.

## Evidence contract

Before Local oneuse-D admission, obtain fresh macOS and Ubuntu workflow conclusions at the actual final pushed demo commit, retain generator compiler logs, two matching pinned IR receipts, negative duplicate-root exit, observed historical-S 15-file structural comparison and all byte/MVID differences, plus exact source Git status. A CI PASS is source/host evidence, **not** Unity/IL2CPP builds, installed VM parity, real Players, or historical S independent acceptance. A failure/cancellation/unsupported CI result blocks dispatch to Local until Primary resolves it.

Local oneuse-D remains: one read-only original sparse fc55/source/SDK/CLI/capacity admission, exactly one existing ten-stage coordinator, three real native build roles, five Players, 126 physical installed VM source comparisons, original S archive/90-cell/59-process audit, and return to Primary. No H2/M08A/X02/SNAP-01 or Human Review Gate advancement.

R03Accepted=false; IR-R03-01/02 High/open; runtimeAcceptance=false; ReadyForHumanReviewGate=false; PureInterpreter disabled.
