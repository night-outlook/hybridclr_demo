# Primary source audit — observed registry-bound owned names

**Review type:** Primary source/test review, **not independent R03 full-stage review**.

## Examined paths and invariants

- `il2cpp_plus/libil2cpp/vm/AssemblyShadowPhysicalMembership.h`: the new binding lookup is opaque, captured-state/seen/role gated, resets outputs on failure and returns an index and Source only. Existing hash/linear probing, `ObserveEnumeratedOwned`, void adapter, witness capture, revision equality and cleanup remain unchanged.
- `il2cpp_plus/libil2cpp/vm/AssemblyShadowOwnedPhysicalNames.h`: fixed-capacity row slot+role, typed invalid/duplicate rejection, no retained VM class/name pointers, full text/row/slot-bitmap scrub on failure. New arrays are bounded under existing 512 KiB static assertion.
- `il2cpp_plus/libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl`: binding lookup only after FirstMatch and before physical metadata text is copied, under existing metadata lock; observed registry recheck remains post-iterator and under a distinct short lock. A failed collector propagates its original typed error; no existing getter is called.
- `il2cpp_plus/tools/r03/diagnostic_stream/{owned_physical_names_fixture.cpp,run_owned_physical_names.py}`: actual production header/.inl compiled under explicit VM/lock mocks; strict/sanitized 28-item inventories; first-match, reversed role, display-name and hash collisions, invalid/duplicate/scrub tests; original CPP/API/physical header reconstructed against immutable prior Git blobs.
- `hybridclr_demo/Tools/AssemblyShadow/R03IR/{run_p1_metadata_local_preflight.py,test_p1_command_failures.py,test_p1_managed_receipt.py}`: an apparently Passed child cannot substitute incomplete 28-group inventories or false scope flags; original missing/malformed lifetime fail-stop and bounded one-shot batch controls remain.

## Findings and dispositions

- **Closed in code (needs Local official SDK verification):** owned name rows previously could not be associated with a witnessed observed slot/source without class-pointer fallback. Returned rows now carry registration binding but only for the current observed registry snapshot.
- **Closed in code (needs Local verification):** an internal failure in `Capture::Add` previously marked Failed without itself clearing its copied text; the new `Fail` scrubs raw text/rows/slot tracking. Caller `Revoke` still scrubs on VM method failure.
- **Closed in source-host contract (needs Local verification):** aggregate producer `Passed` could be accepted without an exact group set; the demo consumer now requires 28 exact ordered group names for each compiler profile and all explicit false scope flags.
- **Open and not overridden:** allocation provenance/lifetime, canonical generic-aware TypeKey, all-VM coherent epoch/ABA, full owned execution rows/JSON, process GC/RSS/latency, MetadataLock/Shutdown, P2 real native/C# V2 transactions, E0 owner-safe point, E1 drain/restart, full linked P3 runtime, strict S custody, original fingerprint FAIL and independent full-stage R03 re-review.

No Local Agent nontrivial native/compiler fix is authorized. Host CI failures require Primary correction, new source pins and new documentation, not a reclassification of prior test evidence.
