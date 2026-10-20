# R03 P1 — inactive registry-bound owned physical display-name rows

## Authority and objective

The last factual Local Validation is `20261020-e6a3`, **18/18 PASS / PassedSourceHostAndSDKOnly** at demo `63c812228c749bb44129ee141ab32895cfdc62e1` and native `e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5`. It includes 85 controlled failure tests, 100 actual Apple arm64 C++17 syntax configurations and the original five managed-positive/one expected-negative receipts. That result is consumed, immutable, and **not** a Unity runtime or R03 acceptance.

The previous inactive owned-name capture copied three physical metadata strings during an exact `il2cpp_class_for_each` first-match callback under `g_MetadataLock`, but its `RowView` only contained the copied bytes. A row could not be joined to the exact observed execution registry slot or the Candidate/ActiveShadow registration witness without falling back to an unowned class pointer. This increment carries the **snapshot-local registration binding** alongside each owned display-name row, with no pointer exposed or persisted.

## Design and invariants

1. The existing registration publisher and witness table are unchanged. `AssemblyShadowPhysicalMembership::Scratch::TryObservedRegistrationBinding` reads only its already captured opaque slot identities, seen bits and source roles. The VM callback invokes it **only after** `ObserveEnumeratedOwned(klass)==FirstMatch`. Before a first match, after scrub, on invalid or unrelated addresses, or on a malformed role, lookup fails with outputs reset. This is not proof of physical allocation origin or pointer lifetime.
2. `OwnedPhysicalNames::Capture::Add` requires a valid slot in `[0,2047]` and either Candidate or ActiveShadow. It refuses duplicate row bindings with distinct error codes. Each sealed `RowView` contains its copied physical assembly/namespace/simple-name spans, `registrySlot` and `registrationSource`. No raw `Il2CppClass*`, `Il2CppImage*`, `Il2CppAssembly*`, or borrowed name pointer is part of that row.
3. The existing one-shot, **1024 matched-row**, **256 KiB text**, **4096 bytes per field** and **512 KiB object** bounds remain. Add failure now explicitly scrubs all rows, owned text and slot-use bits, in addition to the existing caller-level `Revoke` and pointer scratch `Scrub`. The receipt exposes `boundRegistrationRows` and `allRowsBoundToObservedRegistry` only on success; rejection leaves that success flag false and preserves the first typed owned-capture error.
4. Lock sequence is unchanged: initial-session metadata Reader; brief observation registry capture/unlock; synchronous physical iterator under `g_MetadataLock`; release; brief observation recheck/unlock; Reader release. No metadata/observation lock nesting; no name copies from duplicate/unrelated callbacks. Registry revision, source witness, state and active snapshot must still match the original before/after checks. All new work is inside the **inactive** method; existing getters and managed APIs are untouched.
5. The slot/source binding is a **bounded observed registry-snapshot claim**. It is not a canonical generic-aware execution `TypeKey`, globally coherent VM epoch, ABA guarantee, lifetime/provenance of class memory, full nonempty execution JSON, cctor/static state, runtime-safe allocation bound, or authorization to dereference a class outside the iterator.

## Source and test inventory

Native `il2cpp_plus@bc3b7df43c5009fa4bc7f6d94e414ad9cd135f62` changes only `AssemblyShadowPhysicalMembership.h`, `AssemblyShadowOwnedPhysicalNames.h`, `AssemblyShadowOwnedPhysicalNamesSource.inl`, the actual source-bound `owned_physical_names_fixture.cpp`, and its `run_owned_physical_names.py` gate (including its focused CI source-test discovery repair). Real `AssemblyShadow.cpp` and `AssemblyShadow.h` are byte-unchanged.

The host fixture now requires **28 ordered groups per strict and ASan+UBSan profile**, adding reversed enumeration, identical display-name collision separation, hash collision/linear-probe binding, pre-first-match and unrelated lookup refusal, invalid slot/role rejection and duplicate-slot scrubbing. The pre-existing 20 controls remain. Each host run must have real version/compile/run receipts and source/Git-blob preservation, not test name counts alone.

Demo `hybridclr_demo@b2d6345f66fdf76456b5fab943f0737da4c62974` extends the Local preflight's receipt consumer and managed aggregate mock contracts: a successful owned-name child must report the exact native result kind/schema, both strict/sanitized `PassedWithinExplicitVmMocks` groups in a **fixed 28-item order**, real source compilation and preservation, and explicit false runtime/provenance claims. Failures and unknown child lifetime remain distinct. Controlled adversarial receipt checks execute inside an existing fixed 85-case leaf to preserve that immutable inventory.

## Boundaries and rollback

This design does not enable the new collector in Player, change source registries, replace legacy JSON, add new allocation pathways or alter Hot Update behavior. If host CI or installed SDK syntax rejects this increment, stop at Primary; do not ask Local to edit native/compiler sources. Revert only the five native and three demo tool/test source paths through a separate reviewed commit, retaining all historical raw evidence.

P1 remains Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. `R03Accepted=false`, `ReadyForHumanReviewGate=false`, PureInterpreter disabled; no automatic H2 or future milestone.
