# Local Validation → Primary Implementation

## Current blocker: strict pilot seal invalidated after 14/40 formal pairs by `st_dev` drift

Fresh Local Validation at checkout `bb2bf106c172c985e9330de9cc0e2f58b24f096b`, source/tool anchor `91ac4db31cec704551c7db05bd918c8d5695ce83`, passed current/protected authority, current Python validation, exact 9-path and 22-path source audits, complete retained artifact reauthentication, a new retained-runner-aware bridge, the retained-pilot admission preflight, and a new 8/8 strict pilot seal.

The new bridge SHA-256 is `b207fe8a91c15650d00670dd593207b00fed9a0e05cf618d13982b18402437a2`. The admission preflight SHA-256 is `111c897d2925f0fb85a2b33d941e2a342a7984ba630c5b00ec1ed3f702608898`. The strict seal SHA-256 is `25a768a7fd05e7d103aab31d42d2fcbc121423afbeeae73ffb180a7281d794cc` and records `deepLaunchVerificationCount=8`.

A new formal series started from the retained pilot index only. Pair 1 passed the focused authority gate: protected A had no formal authority; candidate B used the current runner and a valid current `H1FormalSideLaunchAuthority`; the child consumed it, passed graph preparation, launched the Player, and echoed the exact authority/bridge/seal/map in its R00 receipt. Formal pairs 1–14 passed: all 10 OFF-NoPatch pairs and four ON-NoPatch pairs.

Pair 15 never produced a protocol output root or sample index before a supervising terminal interruption, so it remains attempt 1. Resume from the authenticated pair-14 sample index then failed before pair 15 with:

`Pilot verification cache invalidated by changed file identity`

The affected protected OFF `GameAssembly.dylib` is byte-identical:

- sealed SHA-256: `ae75b36f20a8adf323a821ee2f2f585ae0bfc664e8e81063f8b3cc0ec4023b8d`;
- current SHA-256: `ae75b36f20a8adf323a821ee2f2f585ae0bfc664e8e81063f8b3cc0ec4023b8d`;
- unchanged: size, inode, mode, mtime, ctime;
- changed: `device` from `16777229` to `16777230`.

The verifier therefore failed closed exactly as implemented. Local did not weaken it or reseal/relabel the partial formal series.

## Required Primary decision

Decide whether `st_dev` is intentionally acceptance-critical for the multi-hour formal seal:

1. If yes, require a stable mount, issue a new source-authoritative handoff, create a new bridge/seal, and restart all 40 formal pairs from the retained pilot index. The current 14/40 series remains historical only.
2. If no, implement and test a narrow stable cross-remount identity contract while preserving content hashes and the remaining immutable stat guard. Return that source/tool change to Local for a fresh V00 and a wholly new formal series.

This cycle also preserved the initial pre-launch batch output-name collision and the terminal interruption as non-protocol failures. Neither was relabelled as a formal attempt.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260922-authority91ac-formal-seal-invalidated/`.

Final strict analysis, V05, and independent M08 were not run. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
