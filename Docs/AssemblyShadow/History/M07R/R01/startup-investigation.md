# R01 startup investigation — initial gap reproduced

Status: the initial pinned ConfigureOnly Player experiment reproduced the declared pre-Configure observation gap on 2026-09-08. Early registration remains unimplemented pending completion of the current frozen-input Editor check. This is evidence for the bounded Type/object/cctor/native-prefab paths, not a whole-program startup proof.

The initial pairing is deliberately labeled `ObserveGap`. It must run an untouched activation control and separate pre-Configure Type, object, cctor and direct AssetBundle prefab-load cases. Negative cases validate then Abort; they never Commit after deliberately using baseline candidates. A successful Validate in these cases is diagnostic evidence of the late observation gap and cannot count as startup acceptance.

The direct prefab case captures native diagnostics immediately before and after AssetBundle loading, before managed component/type inspection. It then verifies the loaded prefab contains the actual candidate script component. This ordering separates native-use evidence from subsequent managed witness inspection. Managed Type/object/cctor probes first load the assembly; their earliest recorded use may therefore be assembly reflection, rather than an isolated class/allocation/cctor hook. The cctor witness verifies its existing counter; it does not reconstruct arbitrary prior side effects.

## Conditional implementation proposal

A read-only native investigation recommends registering embedded candidate identities immediately after MetadataCache physical assembly construction and before unresolved signatures/class startup. This proposal is not implemented and is contingent on the initial real control and negative observations.

- Publish immutable CandidateRegistry once, without assigning transaction owner/build ID or leaving Disabled state.
- Keep Candidate objects and first-use records intact across Configure. Publish approved stable-AOT providers in a separate immutable registry, avoiding mutation of candidate maps already read by hooks.
- Configure must match the complete embedded candidate set, validate the stable set privately, then establish the existing owner/state boundary. Correctable Configure failure must retain first-use history.
- The startup entry point may use physical assembly lookup and raw type handles only; no class initialization, managed reflection or business code.
- Invalid nonempty generated identity data or registration failure must stop runtime initialization. It must not fall back to ConfigureOnly or erase observations.
- Feature OFF performs no early registration. A deliberately empty legacy list retains explicitly labeled ConfigureOnly behavior and does not satisfy a new early-observation claim.
- Preserve the existing pre-Configure execution-mode query contract independently of the presence of early tracking data.

If implemented, rerun an untouched control before accepting the four negative cases. Also verify exact candidate-set mismatch, failed Configure then corrected Configure, and first-use identity/sequence preservation. Unexpected real Unity startup use must be investigated; no whitelist may be added merely to make activation pass.

Codegen/raw metadata activity before registration and opaque engine/plugin effects remain outside the demonstrated observation window. Final supported scope must state that boundary even if intentional negatives are rejected.

## Pre-experiment implementation hazard review

A second read-only native review found that `Runtime::Init()` permits retry after `MetadataCache::Initialize()` returns false, while metadata initialization allocates new physical tables. A process-lifetime candidate registry must not retain pointers across replacement tables. Any early-registration implementation therefore needs a sticky one-attempt/failure boundary and explicit unsupported reload behavior, rather than rebuilding a registry and losing observations. No startup implementation has been applied on the basis of this source investigation.

Other integration checks are: reject duplicate or incomplete embedded identities before publishing; separate configuration publication from candidate observation; retain the pre-Configure execution-mode API behavior; capture the stable registry consistently with transaction state in diagnostics; and test concurrent observation while Configure validates its private inputs. Early registration must use only raw physical metadata and native fixed-record observation, without managed thread, GC, reflection, or exception initialization.

The untouched control may reveal legitimate engine class/vtable/static-storage initialization or eager constructors before Bootstrap. Such evidence must be investigated without whitelisting it to pass activation. Initialization retry, exact-set/duplicate rejection, corrected Configure preserving first-use records, and OFF/empty-list compatibility are required focused checks if the conditional implementation proceeds.

## Actual initial Player result

The M07-Baseline-R01-gap-v1 pairing completed all ten fresh processes with 16,828 launch inputs unchanged. The untouched control, oversize reservation rejection, size mismatch, four startup negatives and feature OFF passed individual strict diagnostic validation. Ordinary-first and ordinary-after-reserve failed in the probe before image load: it compared the raw JSON file hash to the different semantic snapshot identity. The complete strict suite remains Failed; those failures are retained and must be corrected and rerun in a new pairing.

All four startup negatives observed actual baseline use while diagnostics reported ConfigureOnly and empty first-use records before observation, afterward, through Configure and after Abort. Validate returned Success and Abort returned Success; no intentional negative committed. The native-prefab diagnostics were additionally captured immediately around direct bundle loading, before managed component inspection. The independent per-mode audit confirms the recorded result schema, byte inputs, operation order, capacity/recovery data and process/build identity for these eight successful diagnostic cases.

Evidence: `initial-pairing.json` binds the exact Player receipts, completed fixture/replay receipts and `_temp/AssemblyShadow/R01/initial-diagnostic-audit-1.json`. Its complete-suite Failed result is preserved. This closes ASR-011's risk-verification step for the demonstrated paths and justifies the conditional early-observation implementation; it does not close the final startup acceptance boundary.
