# Local Validation Tasks — M07 Fixed-Byte Bootstrap Repair

Run fresh **V00–V05** from the authoritative `Documents/AgentHandoff/WEB_TO_LOCAL.md`.

## V00

- Pull candidate handoff HEAD and record candidate source anchor `29261690798059077e5263de71526867a32bce30`.
- Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
- Run split reproduction-tooling preflight against `ba8fee33753a5ebc215b7a98739e343d8e05572e`; protected behavior/runtime pins must remain exact.

## V01

- Run full H1 Python inventory and `h1_bee_primary_tests.py`.
- Compile candidate and reproduction-tooling checkout in Unity 2022.3.62f2.
- Run affected H1 Editor tests, explicitly including `M07FixedByteBootstrapPolicyTests`.
- Require both policy tests to pass in real Unity; Primary's 300/300 CI is supporting evidence only.

## V02

Run a fresh candidate ON/Debug schema-3 normal-cache proof under source anchor `29261690798059077e5263de71526867a32bce30`. Preserve normal Bee cache and all strict native/managed/store/restoration controls.

## V03

Run a fresh six-build set using `h1_count_build_batch_tooling.py`: candidate ON/OFF × Debug/Release and reproduction ON Debug/Release. Require strict native+managed provenance, tooling bindings, and exact restoration for every accepted build.

## V04

Re-run the complete current-source chain. Historical `d8349b3` V00–V03, candidate 132/132 count, and eight reproduction cells remain preserved evidence but are not relabeled as current-source acceptance.

For M07:

1. use a new baseline ID and fresh outputs;
2. require `M07Build.ValidateCompilerInputs` to pass the real global policy with exactly the reviewed callsite/targets;
3. run `M07FixedByteBootstrapPolicyTests` evidence alongside the workflow;
4. exercise a controlled failing M07 invocation before acceptance and require exact restoration of:
   - `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
   - `ProjectSettings/AssemblyShadowSettings.asset`;
   - `ProjectSettings/EditorBuildSettings.asset`;
   with `workflow-inputs-restored.json` and preserved pre-restore bytes;
5. then run the normal successful baseline/resources/players/startup11/capacity/old-player/M03–M07 chain and controlled Development performance against the protected performance reference.

Any requirement for another bootstrap target or a broader bootstrap exemption returns to Primary.

## V05

Build the successor evidence package only from explicit fresh current-anchor evidence. Include V00 authority, fresh six-build receipts, M07 policy regression, failure-restoration receipt/evidence, complete V04 runtime/performance evidence, and historical checkpoints under their original identities.

Authenticate package bytes/membership, then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only genuine independent whole-chain M08 PASS may make the package Ready for Human Review Gate. Then stop for explicit human H1 approval. **Do not begin R02.**
