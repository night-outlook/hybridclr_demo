# Experimental interpreter codec implementation contract

Status: **Native implementation candidate selected and integrated within R01B; not adopted by a Player or accepted as production capacity.** HybridCLR `7bf9479`, il2cpp_plus `2109c2c` and hybridclr_unity `e06c293` contain the paired native/runtime/managed profile-2 implementation shape. The final ADR remains open until workload, lazy-growth, integration and regression evidence is complete. This keeps DLL-byte heuristics separate from the proof while allowing the implementation to be exercised against real metadata paths.

## Kernel invariants

- Preserve the whole nonnegative signed-int32 raw/AOT domain. `-1` is invalid. Other negative values belong to the interpreter domain, including unknown tokens which must fail explicitly rather than fall back to AOT.
- Use 4,096-value pages, excluding the final sentinel page: 524,287 usable pages. The selected workload may charge at most 393,215 pages, including reserved/unmapped/aborted pages, to retain at least 25% free.
- One shared process-lifetime ledger allocates ordinary and Shadow image identities. Identity zero is reserved; allocate identities monotonically from 1 through 8,192. A failed admission does not partially reserve a batch; successful reservation remains charged if later binding, staging or initialization fails.
- One stable immutable owner record per image carries private ownership and atomic lifecycle. Page bindings become immutable when visible. Publish/Abort use a single per-image state transition with valid C++11 memory orders. No page or identity reuse.
- Kernel owner tokens are internal authorization inputs, not substitutes for production TLS checks. Zero is the unscoped caller and cannot own a private reservation. Runtime adapters must supply the actual ordinary-construction or Shadow staging context; global enumeration must not gain private access.
- Decoding does not allocate. Encoding may bind only inside already charged per-image quota. Any additional credits must be admitted through the same global ledger before binding; all quota and integer failures are explicit and leave existing mappings intact.
- Raw arithmetic validates owner and range. Native fields that are intentionally raw stay raw. Narrow generic-constraint starts use the interpreter sidecar, preserving native AOT structure/file layout.

## Integration and acceptance boundary

The kernel is implemented and exercised by scoped native tests, and the runtime adapter now calls reservation, owner-checked encoding/decoding, finalization and publication from ordinary and Shadow construction paths. It must not silently replace the installed profile or be reported as an accepted 8,192-assembly runtime. Acceptance still needs exact metadata demand/reservation inputs, explicit disposition of failures during construction and after publication, complete arithmetic inventory, fresh source-pinned baseline/Player pairing, and end-to-end lazy/resource evidence. The managed/native profile and capability contracts exist in the paired source pins, but their presence does not establish Player acceptance.

The declared supported metadata envelope may add transparent admission dimensions measured from real inputs, while retaining the user-selected image count, DLL maximum, average/total and headroom. It must not be retrofitted to exclude failing target cases. Excess demand must be rejected before publication for accepted workloads; any post-publication exhaustion in an experiment is an unresolved failure, not successful capacity evidence.

The bounded design reviews permit this implementation candidate and close selected kernel/remediation findings within their stated scopes; they do not waive the final R01B exit criteria, full-stage Player evidence or H1 human review.
