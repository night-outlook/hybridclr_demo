# Primary static review — Apple Bee macro domains and plan-stage retention

Review scope: candidate code anchor `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` relative to Local Validation return `33543dd39efec42a9480ea976ae3a3684dcd5ffd`.

## Verdict

**PASS for return to Local Validation V01–V05. This is not M08 PASS, Player acceptance, or Human Review Gate approval.**

## Findings closed by this anchor

1. **Global macro-profile equality was incorrectly applied across source domains.** The authenticated Apple Bee fixture shows 446 compiler actions: 430 IL2CPP/runtime/PCH actions, 2 BDWGC C actions and 14 zlib C actions. The correction defines domains only from reviewed canonical source ownership and requires exhaustive link/object coverage. Observed macro values, action count, node index, display name and C language cannot select an exemption.
2. **External domains remain provenance-covered.** Every action must use the selected compiler/SDK, have empty unevidenced environment state, carry exact Shadow/count diagnostic definitions and produce a unique object consumed by the selected GameAssembly link. Unknown external files fail closed. BDWGC/zlib cannot use a forced PCH or claim IL2CPP_DEBUG/IL2CPP_DEVELOPMENT ownership.
3. **Runtime assertion evidence remains strict.** Runtime—including PCH producers, generated C/C++ and brotli—uses the pinned IL2CPP configuration and must be internally consistent. Requested Debug/Release verification uses the runtime domain only. `NDEBUG` is definedness-sensitive.
4. **External macro states are not silently ignored.** BDWGC and zlib each have an internally consistent domain ledger and compiler probes without injecting IL2CPP configuration. External NDEBUG is recorded/probed but is never used as runtime assertion evidence.
5. **Graph linkage is explicit.** Object producer outputs, link Inputs and link argv objects must be the same complete set. Post-link selection is proven by file-input/output edges; scheduling dependencies alone do not prove linkage.
6. **Plan-stage diagnostics are retained.** Fresh capture and explicit replay own an attempt directory before interpretation. Raw inputs/stages are retained before planning; an early failure cannot create a successful provenance receipt. PCH replay/probes remain NotRun unless actually reached.

## Regression coverage

Read-only GitHub CI run `34967358028` checked exact code anchor `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` with contents-only permissions. It authenticated the committed Local Validation failure fixture, including Bee graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`, then executed **250 tests; 250 Passed; no nonpasses**.

Authenticated-fixture tests assert the real graph's 430/2/14 domain membership, 444 linked objects, six probe contexts and post-link edges, plus tamper cases for source membership, mixed macro states, feature/count definitions, compiler/SDK/environment drift, link coverage, forced-input routes and PCH behavior. Additional tests cover failure retention, selection/archive integration and synthetic host-compiler probes.

CI artifact: `h1-bee-primary-463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9`, artifact ID `10395946340`, uploaded ZIP SHA-256 `99be2fc3fe8b07b876244815002294d779a7a4ff959b79c8078da78cfc50b618`.

## Explicit limits

- Ubuntu CI does not execute Unity or Apple clang Player builds.
- The old failed Player remains failed/unaccepted and is historical evidence only.
- Actual Apple PCH producer replay and per-domain compiler probes must succeed in fresh V03.
- Fresh six-build, runtime/count/startup/performance evidence and successor package remain Local Validation work.
- Independent whole-chain M08 has not been rerun. H1 remains InProgress and R02 prohibited.
