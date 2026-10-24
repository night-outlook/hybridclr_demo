#!/usr/bin/env python3
"""Audit only the PUBLISHED immutable b7e3 checkpoint, never run Unity/core/SDK.

Checks every published checkpoint byte and every available raw-manifest member.
Missing external raw/sdk files remain explicitly UNAVAILABLE, not assumed passed.
The old Local result and independent audit failure are never rewritten.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

HERE = Path(__file__).resolve().parent
R03 = HERE.parents[1]
CHECKPOINT = R03 / "local-validation-p1-admitted-execution-20261023-b7e3"
BRANCH = "codex/assembly-shadow-r01b-h1"
EXPECTED_REPOS = {
    "hybridclr_demo": "49c6b62d38d7668be10004ac1e5a030d74894f09",
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb",
}
EXPECTED_NAMES = (
    "command-failures", "legacy-host", "metadata-gate", "bounded-class",
    "bounded-physical", "bounded-first-use", "owned-general", "live-general",
    "owned-execution", "empty-live", "opaque-inventory", "physical-membership",
    "owned-physical-names", "owned-physical-json", "live-owned-physical-json",
    "observed-type-shape", "live-type-shape-census", "observed-type-shape-json",
    "vm-shape-json", "admitted-execution", "bounded-status", "bounded-inventory",
    "frozen-v2", "managed-sdk", "native-sdk",
)
EXPECTED_FLAGS = (
    "ownedBindingCaseInventoryVerified", "ownedPhysicalJsonCaseInventoryVerified",
    "liveOwnedPhysicalJsonCaseInventoryVerified",
    "observedTypeShapeCaseInventoryVerified",
    "liveTypeShapeCensusCaseInventoryVerified",
    "observedTypeShapeJsonCaseInventoryVerified",
    "vmShapeJsonSourceCaseInventoryVerified",
    "admittedExecutionMetadataCaseInventoryVerified",
)
EXPECTED_ADMITTED = (
    "closed-before-first-init", "original-reader-opens-once",
    "actual-old-getter-inside-reader", "separate-output-owned-after-admission",
    "original-error-code-propagated", "original-exception-unwinds-reader",
    "shutdown-blocked-until-reader-exits",
    "shutdown-refuses-without-calling-getter",
    "reopen-epoch-two-refuses-unproven-source",
)
SHA = re.compile(r"^[0-9a-f]{64}$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def regular_file(path: Path) -> None:
    assert path.is_file() and not path.is_symlink(), f"Nonregular or missing: {path}"


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("Duplicate JSON object key " + key)
        obj[key] = value
    return obj


def strict_json(path: Path):
    regular_file(path)
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(
                          ValueError("Non-finite JSON: " + s)))


def valid_rel(path: str) -> str:
    assert isinstance(path, str) and path and "\\" not in path
    p = PurePosixPath(path)
    assert not p.is_absolute() and ".." not in p.parts
    assert all(x not in ("", ".", "..") for x in path.split("/"))
    assert str(p) == path, f"Noncanonical relative path: {path}"
    return path


def published_checkpoint_integrity(root: Path):
    """Validate 100% of published checkpoint, not 100% of external raw."""
    manifest = root / "MANIFEST.sha256"
    regular_file(manifest)
    bindings = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        hash_value, sep, rel = line.partition("  ")
        assert sep == "  " and SHA.fullmatch(hash_value), line[:90]
        rel = valid_rel(rel)
        assert rel not in bindings, f"Duplicate checkpoint file: {rel}"
        bindings[rel] = hash_value
    assert len(bindings) >= 2500
    observed = set()
    checked_bytes = 0
    for p in root.rglob("*"):
        if p.is_symlink():
            raise AssertionError("Unexpected symlink inside checkpoint: " + str(p))
        if not p.is_file():
            continue
        rel = valid_rel(p.relative_to(root).as_posix())
        if rel == "MANIFEST.sha256":
            continue
        assert rel in bindings, f"Unmanifested checkpoint file: {rel}"
        actual = file_sha(p)
        assert actual == bindings[rel], f"Published checkpoint SHA mismatch: {rel}"
        checked_bytes += p.stat().st_size
        observed.add(rel)
    assert observed == set(bindings), (
        f"Checkpoint missing {len(set(bindings) - observed)} declared files")
    return bindings, {"checkpointFileCount": len(bindings),
                      "checkpointFileBytes": checked_bytes,
                      "checkpointManifestSha256": file_sha(manifest)}


def raw_manifest_coverage(root: Path, bindings):
    """Check raw-manifest rows available in Git; report external omissions."""
    batch = root / "batch"
    manifest = strict_json(batch / "MANIFEST.json")
    assert manifest["inventoryScope"] == "CompletedBatchFiles"
    assert manifest["commandLifetimeUnverified"] is False
    seen = set()
    copied, missing = [], []
    raw_bytes = copied_bytes = missing_bytes = 0
    extensions = collections.Counter()
    missing_examples = []
    for entry in manifest["files"]:
        rel = valid_rel(entry["path"])
        assert rel not in seen, f"Duplicated raw manifest entry: {rel}"
        seen.add(rel)
        assert isinstance(entry["size"], int) and entry["size"] >= 0
        assert SHA.fullmatch(entry["sha256"])
        raw_bytes += entry["size"]
        if f"batch/{rel}" in bindings:
            assert bindings[f"batch/{rel}"] == entry["sha256"]
            p = batch / rel
            assert p.stat().st_size == entry["size"]
            copied_bytes += entry["size"]
            copied.append(rel)
        else:
            missing_bytes += entry["size"]
            missing.append(rel)
            extensions[Path(rel).suffix.lower() or "(none)"] += 1
            if len(missing_examples) < 15:
                missing_examples.append(rel)
    assert "RESULT.json" in copied
    assert copied_bytes + missing_bytes == raw_bytes
    return {"rawDeclaredCount": len(seen), "rawDeclaredBytes": raw_bytes,
            "availablePublishedCount": len(copied),
            "availablePublishedBytes": copied_bytes,
            "unavailableExternalCount": len(missing),
            "unavailableExternalBytes": missing_bytes,
            "unavailableByExtension": dict(sorted(extensions.items())),
            "unavailableExamples": missing_examples}, set(copied)


def exact_component_contract(root: Path):
    batch = root / "batch"
    raw = strict_json(batch / "RESULT.json")
    assert raw["kind"] == "R03P1FailureAwareSourceSDKPreflight"
    assert raw["result"] == "PassedSourceHostAndSDKOnly"
    assert raw["componentCount"] == raw["attemptedComponentCount"] == 25
    assert tuple(c["name"] for c in raw["commands"]) == EXPECTED_NAMES
    assert raw["sourcePreserved"] is True
    assert raw["commandLifetimeUnverified"] is False
    assert raw["stoppedAfter"] is None
    assert raw["postflightError"] is None
    assert raw["UnityPlayerExecuted"] is False
    assert raw["officialUnitySdkCompileAttempted"] is True
    assert raw["officialUnitySdkCompilePassed"] is True
    for index, item in enumerate(raw["commands"]):
        name = EXPECTED_NAMES[index]
        assert item["name"] == name and item["status"] == "Passed"
        assert item["commandInvoked"] and item["exit"] == 0
        assert item["commandLifetimeUnverified"] is False
        assert item["timedOut"] is False and item["interrupted"] is False
        assert item["innerResult"] == item["expectedInnerResult"]
        assert item["outputCompleteness"] == "CompleteDirectChildStreams"
        assert item["stopBatchReason"] is None
        assert strict_json(batch / "commands" / (name + ".json")) == item
        source = batch / name / "RESULT.json"
        if source.is_file():
            assert file_sha(source) == item["innerResultSha256"]
            assert strict_json(source)["result"] == item["innerResult"]
        for stream in ("stdout", "stderr"):
            p = batch / "commands" / name / (stream + ".bin")
            regular_file(p)
            assert file_sha(p) == item[stream + ".binSha256"]
            assert p.stat().st_size == item[stream + "CapturedBytes"]
            assert item[stream + "Available"] is True
    for flag in EXPECTED_FLAGS:
        assert sum(c.get(flag) is True for c in raw["commands"]) == 1, flag
    return raw, {"count": 25, "orderedIdentities": list(EXPECTED_NAMES),
                 "inventoryFlags": list(EXPECTED_FLAGS)}


def original_85_and_admitted(root: Path):
    batch = root / "batch"
    r = strict_json(batch / "command-failures/RESULT.json")
    assert r["result"] == "PassedWithinHostScope"
    assert r["testsRun"] == r["expectedTestCount"] == 85
    assert len(r["testIds"]) == len(set(r["testIds"])) == 85
    assert [m["expectedTests"] for m in r["modules"]] == [5, 14, 44, 10, 12]
    for k in ("failures", "errors", "skipped", "expectedFailures",
              "unexpectedSuccesses"):
        assert r[k] == 0
    ad = strict_json(batch / "admitted-execution/RESULT.json")
    assert ad["result"] == "PassedWithinInactiveMetadataAdmittedExecutionHostScope"
    assert ad["actualSourceCompiled"] and ad["originalGetterNotActivated"]
    for profile in ("strict", "sanitized"):
        assert tuple(ad["profiles"][profile]["caseGroups"]) == EXPECTED_ADMITTED
        assert ad["profiles"][profile]["result"] == ad["result"]
    for key in ("canonicalExecutionTypeKeys", "coherentVmEpochProven",
                "physicalPointerOriginProven", "runtimeAcceptance",
                "UnityPlayerExecuted"):
        assert ad[key] is False
    assert len(ad["commands"]) == 5
    return {"original85UniqueTests": 85,
            "admittedCasesPerProfile": 9, "profiles": ["strict", "sanitized"],
            "fullRuntimeOrPointerProof": False}


def managed_command_evidence(root: Path):
    batch = root / "batch"
    r = strict_json(batch / "managed-sdk/build-api/results.json")
    assert r["result"] == "Passed" and r["unityVersion"] == "2022.3.62f2"
    assert len(r["inputs"]) == 428
    assert len(r["commands"]) == 6
    assert [x["expectedExit"] for x in r["commands"]] == [0, 0, 0, 0, 0, 1]
    assert r["commands"][-1]["id"] == "OriginalUnsignedCounts"
    for i, x in enumerate(r["commands"], 1):
        p = batch / f"managed-sdk/commands/{i:04d}/command.json"
        regular_file(p)
        assert file_sha(p) == x["receipt"]["sha256"]
        assert p.stat().st_size == x["receipt"]["size"]
        c = strict_json(p)
        assert c["exitCode"] == x["expectedExit"]
        assert not c["timeout"] and not c["interrupted"]
        assert not c["remainingProcessGroup"] and not c["postCleanupGroupExists"]
        assert "csc.dll" in " ".join(c["command"])
        for stream in ("stdout", "stderr"):
            log = p.parent / (stream + ".log")
            regular_file(log)
            assert file_sha(log) == c[stream + "Sha256"]
        rsp = batch / "managed-sdk/build-api" / x["id"] / "compiler.rsp"
        regular_file(rsp)
        assert file_sha(rsp) == x["response"]["sha256"]
        assert rsp.stat().st_size == x["response"]["size"]
    neg_stdout = (batch / "managed-sdk/commands/0006/stdout.log").read_text()
    assert neg_stdout.count("error CS0266") == 2, "Original expected negative changed"
    return {"managedCompilerCommands": 6, "positiveCommands": 5,
            "originalNegativeExpectedExit": 1, "negativeCS0266Count": 2,
            "managedInputs": 428,
            "productsRecompiledByThisVerifier": False}


def native_command_evidence(root: Path):
    batch = root / "batch"
    r = strict_json(batch / "native-sdk/results.json")
    assert r["kind"] == "R03NativeRuntimePrerequisites"
    assert r["result"] == "Passed"
    assert r["plannedTranslationUnitCount"] == 100
    assert len(r["commands"]) == 101
    units = collections.Counter()
    for i, row in enumerate(r["commands"], 1):
        p = batch / f"native-sdk/commands/{i:04d}/command.json"
        regular_file(p)
        assert file_sha(p) == row["sha256"], i
        c = strict_json(p)
        assert c["exitCode"] == 0 and c["timeout"] is False
        assert c["interrupted"] is False
        assert c["remainingProcessGroup"] is False
        assert c["postCleanupGroupExists"] is False
        assert c["command"][0].endswith("clang++")
        for stream in ("stdout", "stderr"):
            log = p.parent / (stream + ".log")
            regular_file(log)
            assert file_sha(log) == c[stream + "Sha256"]
        if i == 1:
            assert "--version" in c["command"]
            continue
        argv = c["command"]
        assert "-std=c++17" in argv and "-fsyntax-only" in argv
        assert argv[argv.index("-arch") + 1] == "arm64"
        units[Path(argv[-1]).name] += 1
    assert len(units) == 20 and set(units.values()) == {5}
    return {"nativeVersionCommands": 1, "nativeSyntaxCommands": 100,
            "distinctTU": 20, "profilesPerTU": 5,
            "compilerReexecutedByThisVerifier": False}


def historical_git_receipts(root: Path, raw):
    batch = root / "batch"
    d = raw["postflightGitDiagnostics"]
    assert d["kind"] == "R03P1PostflightGitAuthorityDiagnostics"
    assert d["actualDirectCommandCount"] == 20
    assert d["completedRepositoryCount"] == 4
    assert d["timeoutSecondsUnchanged"] == 120
    assert d["timedOutCommands"] == d["completedNonzeroCommands"] == 0
    assert d["commandLifetimeUnverified"] is False and d["noRetry"] is True
    assert d["descendantQuiescenceProven"] is False
    before = raw["fourRepositoriesBefore"]
    after = raw["fourRepositoriesAfter"]
    assert len(before) == len(after) == 4
    verified = 0
    modes = ("01-remote", "02-branch", "03-rev-parse",
             "04-status", "05-ls-remote")
    for b, a in zip(before, after):
        repo = b["repository"].split("/")[-1]
        pinned = EXPECTED_REPOS[repo]
        assert b == a and b["head"] == b["remoteHead"] == pinned
        assert b["clean"] is True and b["branch"] == BRANCH
        assert b["repository"] == "night-outlook/" + repo
        for i, mode in enumerate(modes, 1):
            directory = batch / "postflight-git" / repo / mode
            start = strict_json(directory / "START.json")
            result = strict_json(directory / "RESULT.json")
            assert result["repository"] == repo
            assert result["ordinal"] == i
            assert result["status"] == "Completed" and result["exit"] == 0
            assert result["timeoutSeconds"] == 120
            assert result["timedOut"] is False
            assert result["commandLifetimeUnverified"] is False
            assert result["stdoutAvailable"] and result["stderrAvailable"]
            for stream in ("stdout", "stderr"):
                data = (directory / (stream + ".bin")).read_bytes()
                assert sha(data) == result[stream + "StoredSha256"]
                assert len(data) == result[stream + "StoredPrefixBytes"]
                assert result[stream + "PrefixOnly"] is False
                assert result[stream + "StoredSha256"] == result[stream + "CapturedSha256"]
                assert len(data) == result[stream + "CapturedBytes"]
            output = (directory / "stdout.bin").read_text().strip()
            if i == 2:
                assert output == BRANCH
            elif i == 3:
                assert output == pinned
            elif i == 4:
                assert not output
            elif i == 5:
                assert output.split()[0] == pinned
            assert start["repository"] == repo and start["ordinal"] == i
            verified += 1
    assert verified == 20
    return {"historicalGitDirectReceiptsVerified": 20,
            "executionSourceRefs": EXPECTED_REPOS,
            "liveRemoteHeadsRechecked": False,
            "historicalRemoteAuthoritativeAtCapture": True}


def preservation_and_fail_state(root: Path):
    pre = root / "preflight"
    preserve = strict_json(pre / "INDEPENDENT_PRESERVATION_AFTER.json")
    local = strict_json(root / "LOCAL_RESULT.json")
    finding = strict_json(root / "FINDING.json")
    prior_audit = pre / "audit.py"
    assert file_sha(prior_audit) == (
        "2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0")
    assert local["result"] == "FAIL"
    assert finding["id"] == "IR-LOCAL-P1-ADMITTED-AUDIT-ROSTER-01"
    assert preserve["result"] == "Preserved"
    assert preserve["sdkFiles"] == 2405 and preserve["sdkBytes"] == 316062203
    assert preserve["installedSdkUnchanged"] is True
    assert preserve["consumedP1RawScratchAuditSets"] == 22
    assert preserve["originalCheckpointSets"] == 24
    assert preserve["negativeControlSymlinks"] == 88
    assert preserve["separateBlockedCheckpoints"] == ["e1e5", "6c72"]
    assert preserve["acceptanceFlagsRemainFalse"] is True
    assert not (pre / "EVIDENCE_AUDIT.json").exists()
    return {"originalLocalOutcome": "FAIL",
            "originalRequiredAuditor": "FailedAtLine190",
            "postLine190OriginalAuditorChecks": "NotRun",
            "reportedSdkFiles": 2405, "reportedSdkBytes": 316062203,
            "externalOriginalBytesRechecked": False,
            "historicalOutcomeReclassified": False}


def run(root: Path):
    bindings, checkpoint = published_checkpoint_integrity(root)
    coverage, copied = raw_manifest_coverage(root, bindings)
    raw, components = exact_component_contract(root)
    original = original_85_and_admitted(root)
    managed = managed_command_evidence(root)
    native = native_command_evidence(root)
    git = historical_git_receipts(root, raw)
    state = preservation_and_fail_state(root)
    return {
        "kind": "R03P1AuditOnlyPublishedSnapshotV1", "schemaVersion": 1,
        "result": "PassedPublishedSnapshotScope_ExternalInputsUnavailable",
        "completeFullIndependentAudit": False,
        "originalLocalResultUnchanged": "FAIL",
        "scope": "Read-only GitHub-published checkpoint bytes. No external SDK source or consumed raw/scratch access.",
        "checkpoint": checkpoint, "rawManifestCoverage": coverage,
        "rawComponents": components, "originalTestsAndAdmitted": original,
        "managed": managed, "native": native, "historicalGit": git,
        "historicalState": state, "runtimeAcceptance": False,
        "R03Accepted": False, "ReadyForHumanReviewGate": False,
        "PureInterpreterEnabled": False, "noCoreSdkPlayerExecution": True,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, help="Write report only OUTSIDE repository in a fresh report directory.")
    opts = ap.parse_args()
    try:
        report = run(CHECKPOINT)
        result = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if opts.output:
            assert opts.output.is_absolute()
            assert not opts.output.exists() and not opts.output.is_symlink()
            assert CHECKPOINT.resolve() not in opts.output.resolve().parents
            assert HERE.resolve() not in opts.output.resolve().parents
            opts.output.parent.mkdir(parents=True, exist_ok=True)
            with opts.output.open("xb") as fh:
                fh.write(result.encode("utf-8"))
        print("AUDIT_ONLY_PUBLISHED_SNAPSHOT_REPORT=" + json.dumps({
            "result": report["result"], "checkpointFiles": report["checkpoint"]["checkpointFileCount"],
            "rawDeclared": report["rawManifestCoverage"]["rawDeclaredCount"],
            "rawPublished": report["rawManifestCoverage"]["availablePublishedCount"],
            "rawExternalUnavailable": report["rawManifestCoverage"]["unavailableExternalCount"],
            "managed": report["managed"]["managedCompilerCommands"],
            "nativeSyntax": report["native"]["nativeSyntaxCommands"],
            "git": report["historicalGit"]["historicalGitDirectReceiptsVerified"],
            "localStillFail": report["originalLocalResultUnchanged"],
            "fullAudit": report["completeFullIndependentAudit"],
        }, sort_keys=True))
        return 0
    except (AssertionError, ValueError, KeyError, OSError) as exc:
        print("FAIL_CLOSED published-snapshot verification: " + repr(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
