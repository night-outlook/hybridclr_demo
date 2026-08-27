# M01 evidence index

These are byte-for-byte copies of machine-generated results from the isolated
macOS ARM64 Unity 2022.3.62f2 IL2CPP project. Result files retain their original
absolute artifact paths. `m01-run-ledger.json` and `artifact-inventory.json` are
main-agent records of observed process exits and file hashes, not additional
test executions.

- `m01-*-final.json` and matching `-native-diagnostics.json`: final six-mode
  matrix. P01 is Passed/CONDITIONAL-GO. Baseline passes. The four pre-use modes
  are timing observations; Prefab/Scene intentionally fail shadow-only probes
  while recording unchanged physical old objects.
- `m01-build.json`, `m01-player-assemblies.json`: final ON build and captured
  post-strip managed inputs, including separate semantic equivalence results.
- `m01-editor-validation.json`: five actual Editor checks, not Player evidence.
- `m01-verification.json`: independent Python verification against real bundle,
  DLL, native library, run-result and diagnostic bytes.
- `m01-native-off-build.json`, `m01-native-off.json`: final native source built
  OFF and run with the ordinary M00 regression harness in a separate app.
- `baseline-manifest.json`, `patch-manifest.json`: frozen first-build identities
  and same-name marker-only P01 identities.
- `m01-source-asset-audit.json`: all 42 business/consumer/serialized-asset files
  and metas still byte-match the first-build source snapshot; eight asmdef
  definitions parsed and recorded.
- `Experiments/`: failed name-only/image-only/class-comparison runs and their
  build receipts. They establish why each hook was added; they are not final
  positive acceptance. Their receipts retain the original Prototype.app path,
  but matching archived binaries are under `_temp/AssemblyShadow/M01-*-GameAssembly.dylib`.
- `m01-native-symbols.txt`: final binary/dSYM UUID and offline source lookup.
- `m01-install-receipt.json`, `m01-install-repeatability.json`, and
  `m01-installed-verification.json`: exact committed source pairing, two
  identical installations, complete file inventory, and default strict demo
  source verification. No development source-check bypass is used.

Raw logs, apps, DLL/PDB/source snapshots and dSYM bundles remain local under the
paths in the inventory and receipts; they are not checked-in binaries. The
first baseline bundle root is never regenerated or overwritten for this record.
Missing local binaries on another machine require reproduction, not assuming
that the JSON alone proves a new build passed.
