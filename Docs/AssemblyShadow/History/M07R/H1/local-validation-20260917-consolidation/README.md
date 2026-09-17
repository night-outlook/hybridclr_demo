# Local Validation Checkpoint — Documentation Consolidation

Date: 2026-09-17

This checkpoint preserves the fresh validation attempts made after consolidating the active documentation under `Docs/AssemblyShadow/`.

## Current disposition

- Candidate preflight at handoff `b1c7ed1949f94c9eca9d98b4fecdea06f1c16f9c`: `SourceTargetVerifiedNotBuildAccepted`.
- The first reproduction command used the reproduction checkout's legacy handoff preflight and failed `Wrong handoff branch`; that command verifies the protected behavior checkout, not the separate tooling checkout.
- The correct candidate-owned split tooling preflight then failed `Protected reproduction published head changed build behavior after its source pin`.
- Root cause: documentation consolidation removed the exact legacy handoff metadata classification needed when comparing historical reproduction commits. It did not represent a protected-source change.
- Bounded correction: retain the five exact historical `Documents/AgentHandoff` metadata paths in `shadow_tools.metadata_only`; arbitrary files under that path remain build inputs. This is an explicit historical old-to-new migration rule, not a live compatibility document or a broader allowlist.
- Focused regression tests: 35 passed.
- Correct split reproduction-tooling preflight after correction: `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; exact tooling commit `ba8fee33753a5ebc215b7a98739e343d8e05572e`; protected published head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`; behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`; editor source compatibility `Compatible`.
- Complete Python inventory after correction: 986 passed, 28 skipped environment-dependent tests, no failures/errors.

The raw failed attempts are retained unchanged under `raw/V00/`. V01 Unity compilation and later V02–V05 work have not yet been claimed by this checkpoint.
