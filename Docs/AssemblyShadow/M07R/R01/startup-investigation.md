# R01 startup investigation — pending real experiment

Status: initial ConfigureOnly implementation prepared; no R01 Player result yet. ASR-011 remains a risk pending the real experiment, not a confirmed reproduced defect in this delivery.

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
