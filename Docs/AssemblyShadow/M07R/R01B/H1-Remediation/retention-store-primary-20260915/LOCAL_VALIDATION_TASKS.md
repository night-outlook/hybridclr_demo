# Local Validation tasks — retention-store successor

Authority: `Documents/AgentHandoff/WEB_TO_LOCAL.md`. This checklist is operational only.

- [ ] **V00** pull candidate handoff; verify source anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe`, protected pins/refs, and run authoritative preflight to a new output.
- [ ] **V01** rerun affected H1 Python/Bee/provenance/retention tests; Unity compile and focused/affected Editor tests on candidate and reproduction. Preserve exact IDs/logs/XML.
- [ ] **V02-A** replay exact retained Apple input if source locators/bytes remain; otherwise record `Unavailable` and use a fresh capture.
- [ ] **V02-B** prove declared-input retention crosses the previous 267,613,743-byte partial volume without omission; record declared path count, nominal bytes, logical unique bytes, physical stored bytes, observation/content/blob counts, policy and limits.
- [ ] **V02-C** run `h1_verify_capture_store.py` on the completed attempt. Require `StoreVerifiedNotAcceptance` and exact reversible SHA/length validation.
- [ ] **V02-D** if planning/PCH is reached, require existing 446/444/430/2/14/six-context/linkage/PCH/probe contracts. Do not call earlier-stage success overall provenance PASS.
- [ ] **V02-E** run logical-limit, physical-store-limit, compressed-tamper, corrupt-finalization and incompressible-raw-fallback regressions. Limit/tamper cases must not publish provenance receipts.
- [ ] **V03-A** reinstall exact pins and rerun installed-runtime verification.
- [ ] **V03-B** fresh candidate ON/Debug smoke: Player + retention-store verifier + compiler/PCH/domain + managed provenance + final/strict receipt + restoration.
- [ ] **V03-C** after valid smoke, finish candidate ON/OFF × Debug/Release and reproduction ON Debug/Release in immutable roots.
- [ ] **V04** complete current count/repro/startup/capacity/regression/performance chain from project docs.
- [ ] **V05** create/authenticate successor evidence, run strict semantic verifiers, then commission genuinely independent whole-chain M08.
- [ ] Update/push `LOCAL_VALIDATION.md`; put nontrivial issues in `RETURN_TO_WEB.md`; auxiliary raw/checkpoint evidence goes under `Docs/AssemblyShadow/...`.

Do **not** locally change retention bounds or codec, omit source bytes, broaden provenance/domain/witness rules, repoint reproduction, change performance methodology, claim M08 PASS, or enter R02.
