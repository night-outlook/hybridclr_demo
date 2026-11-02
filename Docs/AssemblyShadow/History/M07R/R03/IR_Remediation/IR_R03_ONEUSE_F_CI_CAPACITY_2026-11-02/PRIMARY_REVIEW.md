# Primary review — F prerequisite block, CI authority and G capacity

**Basis:** `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-f/{README.md,LOCAL_RESULT.json,FINDING.json,local-evidence/oneuse-F-CI_GATE.json}` and canonical `RETURN_TO_WEB.md`.

**Factual F disposition:** BLOCKED, coordinator0, ten stages NotRun, F root absent. Both OS jobs of combined-host 41433978929 PASSED at demo9db; eight required workflows unavailable at that exact SHA. E FAIL unchanged; F is not a runtime rerun or a product FAIL.

**Source review:** Direct GitHub Connector inspection of all nine workflow files identified five missing canonical handoff path triggers: oracle source-only, general IR host, K host, K sourcecheck and L contracts. The full canonical handoff is added to all five without changing their code/test selections. The host contract rechecks nine files, event branch and actual push paths including negative mutations; the final-commit GitHub run list must still be independently checked to establish CI authority.

**Explicit Primary capacity GO/NO-GO:** F's read-only observation **39.5234375 GiB** is 0.4765625 GiB below the 40-GiB advisory (hard20 unchanged). E's observed ~2.966-GiB disk reduction supports a narrow G-only GO if **two fresh samples ≥39.0 GiB** on the actual target volume, with successful CI/source/toolchain admission. Below39.0: NO-GO, do not consume G root. This is an explicit administrative risk acceptance, not a claim that future growth is bounded or that 39.523 is a current measurement.

**Remaining:** Final commit nine-workflow CI results, fresh Mac storage/source/CLI admission, original-S reauthentication, 3 actual Unity builds, 5 actual Players, 135 official installed-source pairs, native owner quit, whole-VM capture coherence and independent R03 IR-R03-01/02 review are all not yet proven by this source review. All acceptance flags false.
