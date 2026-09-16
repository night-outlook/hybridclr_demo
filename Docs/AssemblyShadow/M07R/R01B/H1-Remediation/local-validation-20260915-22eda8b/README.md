# H1 Local Validation checkpoint — handoff 22eda8b

Result: **Local Validation → Primary Implementation**.

Validated checkout `22eda8b9d27c2494cdf66749aefebcbbc8701371` with candidate source anchor `b6db7c2fb2fce364d49458b7dfc78886fd430004`.

## Outcome

- V00 passed with `SourceTargetVerifiedNotBuildAccepted`.
- V01 candidate validation passed: Bee Primary 250/250, H1 Python 445/445, strict provenance 4/4, normal M02 owner 15/15, Unity compile, focused tests 4/4 and 10/10, and full Editor tests 351/351.
- Reproduction compile and focused tests passed 14/14. Its additional full Editor sweep completed 330/342 with 12 preserved failures from missing reproduction baselines/fixtures.
- V02 retained-graph replay failed before planning because declared input retention reached 267,613,743 bytes and the next input exceeded the fixed 256 MiB total budget. Planning, PCH replay, and macro probes are `NotRun`.
- The separate bounded negative planning case retained its graph/request/config, failed at `planning`, and recorded PCH replay and macro probes as `NotRun`.
- V03 pinned installation and strict installed-runtime verification passed. The fresh candidate ON/Debug Player build completed, then the mandatory provenance adapter failed on the same 256 MiB retention limit. Exact restoration passed; no provenance receipt exists.
- Remaining candidate/reproduction builds, V04, successor packaging, and independent M08 are `Blocked / NotRun`.
- `humanGatePassed=false`; `mayEnterR02=false`.

## Read order

1. `results-summary.json`
2. `source-state.json`
3. `failure-manifest.json`
4. `v00/candidate-handoff.json`
5. V01 inventories, NUnit XML, Unity logs, and compile reports
6. `v02/retained-apple-replay.tar.gz` and `v02/negative-plan-attempt/`
7. V03 installed-runtime and smoke runner evidence
8. `v03/candidate-on-debug-failure-inputs.tar.gz`
9. `checkpoint-manifest.json`

## Raw roots

The portable archives preserve the two complete provenance attempts. Their unpacked local roots remain:

- `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-22eda8b/v02/retained-apple-replay`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-fa63d77e368c42d0b558979fecb5fc1b`

Historical evidence under `Documents/AgentHandoff/` and the pre-existing untracked `v7`–`v11` directories were not modified or incorporated into this checkpoint.
