# PCH primary implementation and Git handoff

Read `Documents/AgentHandoff/WEB_TO_LOCAL.md` first. This directory is supporting primary evidence, not an H1 successor acceptance package.

- `STATIC_REVIEW.md`: implementation self-review, assumptions and residual risk.
- `LOCAL_VALIDATION_TASKS.md`: pending real-environment work.
- `source-files.json`: exact code/test bytes and reproduction subset.
- `portable-validation.json`: 160-case selected portable test summary and byte ranges into the raw log.
- `portable-tests.log`: unchanged concatenated completed per-module logs with exact test IDs.
- `strict-published-byte-recheck.log`: actual normal-verifier recheck after an EOF-only representation change.

No Unity/Apple/Player/M08 execution is claimed here. Local D01/D02 results remain in the prior committed checkpoint, not relabeled as fresh results. Native and package implementation pins are unchanged. The authoritative source anchor for each role is also recorded in `Documents/AgentHandoff/source-targets.json` and its ProjectSettings pin.
