# Static review — managed cache action-local response scope

## Review basis

Reviewed from Local return `dc9116a46097739b634c791ac7213f431b54af22` through Primary source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a`, focusing on `Tools/AssemblyShadow/h1_managed_provenance.py`, `h1_compiler_actions.py`, managed provenance regressions, and the committed Local V02 failure census.

## Finding disposition

### P1 — graph-wide response stability creates false rejection

**Closed in source; requires fresh Local validation.**

Schema 2 collected all Csc response files in a Bee DAG and required all of them unchanged for any required cached action. Local evidence showed seven unrelated CodeGen response files changed while each required action's own recursive response closure remained unchanged.

Schema 3 moves stability ownership to the selected action. `actions.expand()` remains the authority for recursive response expansion and supplies `responseSources`. Capture retains exactly those sources on the matched compilation. Verification requires exact equality between retained action `responseFiles` membership and recorded `responseSources`, then verifies every member's retained bytes and end-of-build unchanged observation.

This is narrower than schema 2 and does not accept any response used by a required action if it changes.

## Preserved invariants

Reviewed as unchanged in acceptance semantics:

- source membership and Player define checks;
- compiler/action transcript reparse;
- compiler/tool/reference dependency closure;
- compiler-output pre-existence, identity and stability;
- downstream DLL retention and stability;
- output-to-fresh-Player reachability;
- exact fresh Player path/SHA/size binding;
- ambiguity rejection and changed-action preference;
- cache resource bounds;
- no fresh-Csc-execution claim for cached proof;
- explicit prior-proof reuse remains separate;
- human/M08/R02 gate flags remain false.

## Compatibility

New begin/capture/proof records use schema 3. Schema-1/2 historical evidence remains readable. Schema-2 cache proof deliberately preserves its historical graph-wide response semantics rather than being reinterpreted under the new rule.

## Regression review

Primary suite at source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` passed 283/283 in workflow run `35066118142`.

The two new tests are specifically adversarial:

- unrelated response in same DAG mutates after begin and does not affect required chains;
- nested response belonging to a required action mutates after begin and verification fails closed.

The existing cache-proof negative tests remain active for stale outputs, ambiguity, source/dependency/required-response mutation, wrong fresh Player path and retroactive output creation.

## Review conclusion

No source-level finding remains that justifies broadening acceptance beyond per-required-action recursive response ownership. The implementation is suitable to return to Local Validation for **fresh V00–V05**.

This conclusion is a Primary static/code review only. It is not V02/V03 acceptance, independent M08 PASS, Human Review Gate approval, or permission to begin R02.
