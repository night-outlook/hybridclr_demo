# R01B profile 2 contract draft

Status: **Native/managed integration shape implemented in the pinned R01B source, not installed as an accepted Player profile.** Profile 1 evidence and field meanings remain historical; a Player must reject an unsupported profile before staging. HybridCLR `7bf9479`, il2cpp_plus `2109c2c` and hybridclr_unity `e06c293` are the paired implementation pins. Their profile-2 contracts and native admission calls are source/integration evidence only; full workload capacity and H1 remain pending.

## Units and scope

The supported test envelope is 8,192 process-lifetime interpreter image identities, a 32 MiB maximum input DLL, and 512 MiB aggregate DLL input at a 64 KiB average. The 512 MiB quantity is input bytes, not metadata RAM or encoded index capacity. A 4,096-value index page is not a 4,096-byte memory allocation. Reserved, unused and aborted identities/page credits remain consumed. Native AOT assemblies are separate.

The lifetime target does not require an 8,192-member Shadow closure. Existing bounded closure/parser limits should change only where the declared supported transaction workload requires it; do not widen them merely because the lifetime image count increases.

## Explicit encoding identity

Profile 2 must identify the sparse signed-int32 codec, 4,096 index values per page, 524,287 usable pages, a 393,215 charged-page ceiling, and image IDs 1 through 8,192. The full nonnegative int32 AOT domain and the -1 sentinel remain distinct. Use a new budget capability/profile identifier and synchronized baseline/source provenance. Whether the overall ABI number must change depends on actual public interface changes; profile versioning must never be implicit.

## Preliminary and final reports

Build-time planning and the existing ordered DLL-size reservation call can report only preliminary identity/DLL admission. Their result must explicitly say that runtime footprint finalization remains required. Preserve exact ordered DLL identities, sizes and hashes. Do not describe a size-only result as final metadata capacity acceptance.

Private native initialization computes the actual footprint and seals it internally before publication. It must not trust a caller-supplied page charge as proof. Runtime diagnostics should distinguish permanently reserved pages from mapped pages and report finalized versus unfinalized image reservations. Free capacity is calculated from all charged credits against usable pages, including failed and unmapped reservations.

A finalized report must bind the actual codec/profile and source identity, image reservations, charged pages, mapped pages and remaining usable pages. The committed transaction must have all its members finalized; the existing transaction publication boundary remains authoritative. Diagnostics alone do not authorize publication or reset the process ledger.

## Integration locations

Native budget/codec adapters, VM capacity JSON and capability APIs, managed MetadataCapacityPlanner/profile validation, manifest DTO/readers, runtime capacity parsing and bootstrap consumers are present across the three pinned repositories. Keep historical profile-1 records readable as profile 1; reject mixed or partially specified profile-2 declarations. Source pins and installed-source receipts must still be paired in the final baseline, and this draft does not claim that the current source pairing has passed the full Player matrix.

The profile-2 report remains preliminary until private native initialization computes and seals the actual footprint. A valid profile declaration, capability-2 negotiation and managed parser result cannot by themselves claim runtime capacity support; the final report must be produced by the pinned runtime and checked against the complete workload and failure semantics.
