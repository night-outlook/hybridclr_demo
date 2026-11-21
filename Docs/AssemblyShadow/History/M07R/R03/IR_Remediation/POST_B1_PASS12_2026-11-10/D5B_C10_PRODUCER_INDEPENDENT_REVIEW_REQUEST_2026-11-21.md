# R03 B2 D5-B C10 — Independent design → source → CI review request

**Decision: `PendingIndependentD5BC10Review`.** This is **not** independent approval, a D5-B Local authorization, or a runnable Unity handoff. D5-B C10 is a test-only real-Player *candidate* with source/host CI, not a compiled/linked Unity Player. User's last assignment is to continue **Primary Implementation** after the independent source-custody gate; this document requests a genuinely separate independent reviewer before further source expansion or Local execution.

## 1. Fixed GitHub sources, evidence and review boundaries

Branch `codex/assembly-shadow-r01b-h1` on all four repositories.

| Repository | Exact source pin to review |
| --- | --- |
| `night-outlook/hybridclr_demo` | **CI-tested code `a833d22487352135a88d6b245eea7f2d103af48b`**; later doc-only HEAD is not reclassified as CI-tested |
| `night-outlook/il2cpp_plus` | **`8eeb3cc53a451a6925b490d623c81753822cb1d4`**, exactly two changed native files since D4 |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a`, unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de`, unchanged |

Required starting documents: [D5-B C10 Primary Implementation report](D5B_C10_PRODUCER_PRIMARY_IMPLEMENTATION_REVIEW_2026-11-21.md), [independent D5-B source custody review](D5B_SOURCE_CUSTODY_INDEPENDENT_REVIEW_2026-11-20.md), [original D5-B real-Player/link plan](D5B_REAL_PLAYER_PRODUCER_AND_LINK_PLAN_2026-11-20.md), [D5 42-cell matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md), canonical `README.md` and `WEB_TO_LOCAL.md`.

Independently inspect actual native production diff:
- `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp`, Git blob `8db5fed1ee2e6bf6b95597707a2fa9cdf43807a1`, D5 probe `#if` only;
- `il2cpp_plus/libil2cpp/vm/AssemblyShadowD5WindowProbe.h`, new blob `bb958c44ae11f47160cd306cadc0c3edf56501f9`.

Independently inspect actual demo sources:
- `D5Probe/R03D5WindowOverlay.cpp` blob `2e16ba677f961066cb068bc8199480f642845d0c`;
- `D5Probe/R03D5P5WindowPlayer.cs` blob `851b2fc602185219780dea636a6acac39ae3128a`;
- `D5Probe/R03D5Build.cs` blob `cb4a56cdb8b910fc06721941e92db6165543a38d`;
- `D5Probe/d5c10_link_source_pinset_v1.json` blob `c709a15e27b6b3b7fa0091d36ef3fc514df4a4ba`;
- `D5Probe/d5_link_materials.py` blob `3645b858b72374ae96596d5791657f2afcea5a09`;
- `D5Probe/d5_window_source_contract.py` blob `9ed7018b4514036f0893f432d143aee2bd139cc7`;
- `D5Probe/test_d5_window_source_contract.py` blob `c1f5f4753f98fa843e3c987de018b71e1e1d3681`;
- `D5Probe/test_d5_link_materials.py` blob `5c06e939772af51267ef068d64086c94314ba990`;
- `.github/workflows/r03-b2-d5-c10-window-source-host.yml` blob `5059f7e12a8cd62dd1dcee594283cefdfdd39953`;
- `D5WindowSourceHost.cpp`, `D5WindowOtherTU.cpp`, `D5WindowFeatureOffHost.cpp` and `D5Probe/NativeHostStubs/il2cpp-config.h`.

Real source-host CI: [**GitHub Actions 44854825948**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44854825948), **attempt 1 completed/success 4/4 jobs** at exact demo `a833...`; read raw jobs:
- macOS 15 C++11 `136694455484`;
- macOS 15 C++17 `136694455849`;
- Ubuntu 24.04 C++11 `136694455676`;
- Ubuntu 24.04 C++17 `136694455671`.
Every job: **32/32 source mutation tests**, **25/25 synthetic link/material tests**, **six strict + six sanitized exact-header/overlay C++ host cases**, **one feature-OFF host control**. Total: **228 Python tests, 48 native strict/sanitized receipts, four feature-OFF controls**. No unexpected ASan/UBSan errors. **No full native `AssemblyShadow.cpp` TU or Unity/IL2CPP/Player compiled.**

## 2. Mandatory independent review checklist

1. **C10 safety and real-source fidelity:** confirm the test-only macro is OFF/absent by default, no production changes for normal builds, D2/D3/D4 logic/owner preserved and one-shot control. Independently analyze the *TEST ENABLED* P5 scheduling modification: the transaction lock is intentionally released/reacquired while a capped 20–2000-ms P5 window is exposed. Verify all metadata, assembly and usage locks have actually unwound before this point; analyze other code paths entering a state `Committing` and any realistic data races/deadlocks. A source-host pass cannot prove real VM lock ordering or production timing.
2. **Meaning of a method guard receipt:** actual `AssertMethodIsActive` observes only real active-shadow MethodInfo and preserves boolean return. Examine `shadowToBaseline`, terminal checks and P5-vs-P6 race accounting, presence/absence of method body side effects. In an actual Player, **early admitted business execution before initializer policy is critical ReturnRequired**. A denied host case is a synthetic counter, not real method execution proof.
3. **C# and P/Invoke semantics:** inspect staged DLL binding, two-thread timing, `Type.GetType`/reflection and managed initialization behavior, `Join` bounded wait, exception reporting, all eleven native wire fields, process identity, `FileMode.CreateNew`, and feature-OFF results. Do not assume Unity compiles this new C# fixture; no Editor or Player was available in source-host CI.
4. **Native Unity build/link candidate:** `R03D5Build.Build` source should require the isolated project marker, source tuple/overlays and `PinnedSourceInstaller.Install`; verify extra header and generated/source installation, ON/OFF test macros and BuildPipeline reports. **No direct Local command may be published from this report**, and actual compiler/linker source provenance is NotRun. Compare against historical R03 B1 builder to ensure no silent mutation.
5. **Evidence artifact truthfulness:** inspect 13-source Git blob roster, five required TUs, four expected exports and fake Mach-O/nm data intentionally used in synthetic tests. `d5_link_materials.py` must reject claiming real execution; verify that positive synthetic consistency is not misreported as authentic Bee compilation/link. Consider path/symlink, object SHA, binary hash and self-reported command substitution risks. A real linked binary/PID/source chain remains compulsory later.
6. **Raw CI and failures:** independently verify 4/4 exact final source-host jobs including all 57 Python tests/job, native strict/sanitized results and source-only status. Earlier CI failures (initial fake BuildPipeline regex, temporary corrupted workflow, 39-character `Runtime.cpp` pin) remain failures at old commits; verify final manifest uses the real **40-character** Git blob `1b176ee5fd3e2127a0237877e5c9c32bc53058b3`.
7. **History/Local authority:** compare exact demo base `ea230ebdd6833a99d3177c54fa67ef5b684c700b` and native base `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` to current reviewed commits, ensure no old B1 validators/source/oneuse-12 or other production repo changes. Keep all 18 D5 Player cases `NoCoverage`. The previous D5-B source-custody `APPROVED_LOCAL_HANDOFF_BLOB=None`, user Local approval and `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION` remain intact.

## 3. Decision needed — restricted

Choose exactly one of `PassD5BC10ForNextPreparation`, `ReturnRequired`, or `Blocked`. A positive decision is **only** a bounded source-host test-producer preparation checkpoint. It does **not** grant permission to run Unity, IL2CPP, native Player, Local Validation, D5 completion, R03 acceptance, H2 or Human Review Gate. Any real-Player test must have a **new separately approved** source/implementation+fixture review and an explicit user Local execution decision. Before any future Local, restore/prove full historical evidence-root binding, exclusive oneuse creation, latest reviewed four-remote SHA admission, native source→Bee→object→linked binary→PID evidence and necessary P3–P6/GC/ABI tests.

**Current:** `D5BC10_Primary=CompleteSourceHost`, **`D5BC10_IndependentReview=Pending`**, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
