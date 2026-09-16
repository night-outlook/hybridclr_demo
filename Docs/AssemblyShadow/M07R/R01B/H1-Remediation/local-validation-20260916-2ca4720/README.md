# Local Validation checkpoint — handoff 2ca4720

## Exit

**Local Validation → Primary Implementation**

The requested branch was explicitly fast-forwarded to `2ca4720508dc114e9c55756fcb2a068678dff90c`. Candidate source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a`, candidate native/package/IL2CPP pins, preserved reproduction pins, and the independent performance-reference pin all match the handoff.

The authoritative V00 preflight fails before source verification with:

```text
Blocked: Incomplete handoff sections
```

The committed preflight requires nine literal, case-sensitive heading substrings. The published `WEB_TO_LOCAL.md` contains only three of them and lacks six. Its semantically similar headings do not satisfy the executable contract:

| Required literal | Published heading |
| --- | --- |
| `## Source targets` | `## Exact source targets` |
| `## Implementation` | `## Repair contract` |
| `## Local validation` | `## Local Validation` |
| `## Alternatives` | absent |
| `## Risks` | absent |
| `## Human review gate` | `## Gate` |

The handoff explicitly requires V00 to pass before V01–V05 and forbids Local Validation from rewriting `WEB_TO_LOCAL.md`. V01–V05 are therefore `Blocked / NotRun`. No Unity compile, test, installation, Player build, Bee-cache mutation, runtime, performance, successor, or M08 command was started for this anchor.

`humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Source state

| Role | Exact observed identity | Result |
| --- | --- | --- |
| Candidate checkout | `2ca4720508dc114e9c55756fcb2a068678dff90c` | requested handoff |
| Candidate source anchor | `5f561abdfbe020d1d480594a2130c5ec846c0e6a` | pinned and in checkout history |
| Candidate native | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | clean |
| Candidate package | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | clean |
| Candidate IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` | clean |
| Reproduction demo | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | preserved and clean |
| Reproduction native | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | preserved and clean |
| Performance reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | preserved and clean |

Pre-existing untracked historical `v7`–`v11` directories were preserved and excluded.

## Evidence

- `v00/preflight.stdout.log`: empty, as emitted.
- `v00/preflight.stderr.log`: exact failure text.
- `v00/preflight.exit-code.txt`: exit code `1`.
- `v00/handoff-section-census.json`: exact required, present, missing, and published headings.
- `v00/source-state.txt`: raw repository, pin, dirty-state, disk, OS, Unity, Python, PowerShell, and Git observations.
- `source-state.json`: normalized source/pin/authority hashes.
- `results-summary.json`: explicit V00 failure and V01–V05 `BlockedNotRun` status.

Authority hashes:

- `WEB_TO_LOCAL.md`: `33f23574233ddcfba36438bc6c393557ac34df879ed8210f33cb44efdbf8230c`
- `source-targets.json`: `c69b83f4887e9e59544f4e9011184d0e9d6943eaf0f56032415a2d4b60f3a937`
- source pins: `5a06ac32695a8bfaf4c5501f02429346d3618b182ab90885419b033c7e52de48`
- preflight script: `994e6e48c05aa15b2c66207a256ca76dcebdc8075bb9c1350d35e1d6f55263b1`

No production code or acceptance policy was changed locally.
