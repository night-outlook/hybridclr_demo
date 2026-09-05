# M07 Unity resources and APIs report

Status: implementation is statically validated in isolated worktrees; actual
Unity build, Player execution, evidence retention and Gate 3B remain pending.

## Implemented scope

M07 adds seven canonical resource bundles, guarded baseline/P05 source-asset
generation, five positive patch policies, three structural rejection policies,
a business-free bootstrap and a 14-case runtime probe. The runtime proves Unity
type acquisition, allocation, deserialization, messages, scenes and cache reuse
only after a hash-bound transaction Commit.

The package resource receipt now records effective compiler and Editor define
sets. Startup validation scans `Resources`, preloaded assets, ProjectSettings
GUID references and installed Addressables configuration for candidate scripts.
The native layout gate accepts only safe appended private primitive storage at
the physical metadata boundary; serialized compatibility remains controlled by
the resource ABI/build policy.

## Offline verification completed

- the M07 Python verifier and its 17 focused tests pass;
- the existing M04-M06 Python suites pass together (115 tests);
- current M07 Bootstrap, Editor and Editor-test sources compile against the
  pinned Unity 2022.3.62f2 managed references;
- package Editor sources compile against the pinned Unity references;
- candidate baseline/P01/P03 source variants and focused native layout tests
  have static proof; the remaining structural defines are intentionally left to
  the real guarded Unity compiler/fixture workflow;
- `git diff --check` and PowerShell/Python parser checks pass.

These checks are readiness evidence only. Exact artifact paths, hashes, build
GUIDs, process IDs, timings, strict-verifier output, independent review and tag
identities will be added only after the real isolated Unity/IL2CPP pipeline has
completed.

## Known limits before execution

Unity import can still expose serialization, scene, `MonoScript.GetClass`,
AssetBundle or generated-code behavior that source compilation cannot prove.
The Player records either direct `GetClass` evidence or the plan-permitted,
finite runtime-component corroboration path when the Editor-only script object
or method is unavailable; unexpected invocation failures still fail closed.
The guarded build therefore preserves every failure output, fixes the root
cause in source, selects a new immutable baseline identity and reruns the full
pipeline. A partial case set or `--allow-incomplete` output is diagnostic only.
