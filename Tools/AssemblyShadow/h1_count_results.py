"""Independent verifier for one authenticated H1 count diagnostic cell.

The Player and its launcher produce evidence; this module independently binds
that evidence to the requested cell and to the current fixture/build bytes.
It deliberately fails closed when the probe did not establish the state and
ledger facts required by the H1 contract.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid
from collections import OrderedDict


HERE = Path(__file__).resolve().parent
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_JSON_BYTES = 512 * 1024 * 1024
ORDINARY_WITNESS_NAME = "AssemblyShadowBaseline.HotUpdate"
ORDINARY_WITNESS_FULL_NAME = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
ORDINARY_WITNESS_TYPE = "AssemblyShadowBaseline.HotUpdate.Entry"
ORDINARY_WITNESS_SHA256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27"
ORDINARY_WITNESS_RELATIVE_PATH = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"
ORDINARY_WITNESS_MARKER = "M00-HOTUPDATE-OK"
EARLY_EVIDENCE_SCHEMA_VERSION = 2
RESULT_EVIDENCE_SCHEMA_VERSION = 2

PARAMETER_CASES = {
    "H1R-P01-a": (0, "base-0", "Accepted"),
    "H1R-P01-b": (1, "base-1", "Accepted"),
    "H1R-P01-c": (254, "base-254", "Accepted"),
    "H1R-P01-d": (255, "base-255", "Accepted"),
    "H1R-P02-a": (256, "base-256", "ControlledRejected"),
    "H1R-P02-b": (65535, "base-65535", "ControlledRejected"),
    "H1R-P03-a": (65536, "base-65536", "ControlledRejected"),
    "H1R-P03-b": (65537, "base-65537", "ControlledRejected"),
    "H1R-P04-return255": (255, "return255", "Accepted"),
    "H1R-P04-partial-names": (255, "partial-names", "Accepted"),
    "H1R-P04-instance": (255, "instance", "Accepted"),
    "H1R-P04-mixed-kinds": (255, "mixed-kinds", "Accepted"),
}
NESTED_CASES = {
    "H1R-N01-a": (0, (0,), ("Target",), False, "Accepted"),
    "H1R-N01-b": (1, (1,), ("Target",), False, "Accepted"),
    "H1R-N01-c": (65534, (65534,), ("Target",), False, "Accepted"),
    "H1R-N01-d": (65535, (65535,), ("Target",), False, "Accepted"),
    "H1R-N02-a": (65536, (65536,), ("Target",), False, "ControlledRejected"),
    "H1R-N02-b": (65537, (65537,), ("Target",), False, "ControlledRejected"),
    "H1R-N03-interleaved": (4, (2, 2), ("Target", "SiblingB"), True, "Accepted"),
    "H1R-N04-adjacent-valid": (65536, (1, 65535), ("Target", "SiblingB"), False, "Accepted"),
    "H1R-N04-adjacent-overflow": (65537, (1, 65536), ("Target", "SiblingB"), False, "ControlledRejected"),
    "H1R-N05-final-repeat": (65535, (65535,), ("Target",), False, "Accepted"),
}


class VerificationError(ValueError):
    """An authenticated receipt or semantic observation is invalid."""


class NoCoverage(VerificationError):
    """The run did not establish the requested production behavior."""


def _early_canonical_json(value, receipt_hash=""):
    """Reproduce H1CountEarlyStartup.ReceiptCodec's compact UTF-8 payload."""
    fields = OrderedDict((
        ("schemaVersion", value.get("schemaVersion")), ("kind", value.get("kind")),
        ("diagnosticOnly", value.get("diagnosticOnly")), ("result", value.get("result")),
        ("error", value.get("error")), ("disposition", value.get("disposition")),
        ("callbackReturnCode", value.get("callbackReturnCode")), ("processId", value.get("processId")),
        ("managedThreadId", value.get("managedThreadId")), ("resultPath", value.get("resultPath")),
        ("family", value.get("family")), ("path", value.get("path")), ("caseId", value.get("caseId")),
        ("baselineBuildId", value.get("baselineBuildId")), ("runtimeAbiHash", value.get("runtimeAbiHash")),
        ("expectedOutcome", value.get("expectedOutcome")), ("expectedCount", value.get("expectedCount")),
        ("fixturePath", value.get("fixturePath")), ("fixtureSha256Expected", value.get("fixtureSha256Expected")),
        ("fixtureSize", value.get("fixtureSize")), ("inputHashBefore", value.get("inputHashBefore")),
        ("inputHashAfter", value.get("inputHashAfter")),
        ("witness", {key: (value.get("witness") or {}).get(key, "") for key in
                      ("path", "sha256", "assemblyName", "assemblyFullName", "observationKind",
                       "logicalIdentityKeys", "physicalIdentityKeys", "publishedIdentityKeys")}),
        ("startUtc", value.get("startUtc")),
        ("endUtc", value.get("endUtc")), ("elapsedTicks", value.get("elapsedTicks")),
        ("stopwatchFrequency", value.get("stopwatchFrequency")), ("committed", value.get("committed")),
        ("baselineAlreadyUsed", value.get("baselineAlreadyUsed")),
        ("operations", [{"phase": item.get("phase"), "code": item.get("code"),
                         "intCode": item.get("intCode")} for item in value.get("operations", [])]),
        ("snapshots", [{"phase": item.get("phase"), "nativeCode": item.get("nativeCode"),
                         "nativeJson": item.get("nativeJson"), "diagnosticsCode": item.get("diagnosticsCode"),
                         "diagnosticsJson": item.get("diagnosticsJson")} for item in value.get("snapshots", [])]),
        ("receiptSha256", receipt_hash)))
    return json.dumps(fields, ensure_ascii=False, separators=(",", ":"))


def _verify_early_native_snapshots(early, request, accepted):
    phases = (["before", "after-configure", "after-begin", "after-reserve", "after-stage",
               "after-validate", "after-commit", "after", "final"] if accepted else
              ["before", "after-configure", "after-begin", "after-reserve", "after-stage",
               "after-validate", "after", "final"])
    snapshots = early.get("snapshots")
    _require(isinstance(snapshots, list) and [item.get("phase") for item in snapshots] == phases,
             "early startup native snapshot phase sequence differs")
    parsed = {}
    for item in snapshots:
        _require(isinstance(item, dict) and item.get("nativeCode") == "Success" and
                 item.get("diagnosticsCode") == "Success", "early native snapshot status is unavailable")
        try:
            native = json.loads(item.get("nativeJson"), object_pairs_hook=_unique_pairs)
            diagnostics = json.loads(item.get("diagnosticsJson"), object_pairs_hook=_unique_pairs)
        except (TypeError, ValueError) as error:
            raise VerificationError("early native snapshot JSON is malformed: " + str(error)) from error
        _require(isinstance(native, dict) and native.get("schemaVersion") == 1 and
                 native.get("kind") == "H1CountNativeDiagnostics" and native.get("diagnosticOnly") is True,
                 "early native count snapshot identity differs")
        _require(native.get("featureEnabled") is request["featureEnabled"] and
                 native.get("featureMode") == ("AssemblyShadowOn" if request["featureEnabled"] else "AssemblyShadowOff"),
                 "early native count snapshot feature differs")
        numeric = ("reservedPages", "mappedPages", "reservationCount", "nextImageId", "nextPageSlot",
                   "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedImageCount")
        _require(all(type(native.get(key)) is int and native[key] >= 0 for key in numeric) and
                 native["mappedPages"] <= native["reservedPages"], "early native ledger counters are invalid")
        _require(isinstance(diagnostics, dict) and diagnostics.get("schemaVersion") == 1 and
                 diagnostics.get("enabled") is True, "early Assembly Shadow diagnostics identity differs")
        parsed[item["phase"]] = (native, diagnostics)
    before = parsed["before"][0]
    _verify_witness_snapshots({phase: pair[0] for phase, pair in parsed.items()}, early.get("witness"))
    _require(before["ordinaryAllocatedCount"] == 1 and before["shadowAllocatedCount"] == 0 and
             before["reservedImageCount"] == 0 and before["reservationCount"] == 1 and
             before["nextImageId"] == 2 and before["reservedPages"] > 0 and
             before["nextPageSlot"] == before["reservedPages"],
             "early startup ledger did not retain exactly one preloaded ordinary witness")
    _require(parsed["after"][0] == parsed["final"][0], "early final native snapshots differ")
    if not accepted:
        # A retained failure must not publish, replace, or consume another
        # identity. Compare the complete identity arrays, not just counters.
        final = parsed["final"][0]
        for inventory in ("logicalAssemblies", "physicalAssemblies", "publishedInterpreterImages"):
            _require(before.get(inventory) == final.get(inventory),
                     "early rejected transaction changed " + inventory)
        reserved = parsed["after-reserve"][0]
        staged = parsed["after-stage"][0]
        validated = parsed["after-validate"][0]
        _require(reserved.get("ordinaryAllocatedCount") == 1 and reserved.get("shadowAllocatedCount") == 0 and
                 reserved.get("reservedImageCount") == 1 and reserved.get("reservationCount") == 2 and
                 reserved.get("nextImageId") == 3 and reserved.get("reservedPages") > 0 and
                 reserved.get("nextPageSlot") == reserved.get("reservedPages") and
                 reserved.get("mappedPages") == before.get("mappedPages"),
                 "early rejected reservation ledger is not exact")
        _require(staged.get("ordinaryAllocatedCount") == 1 and staged.get("shadowAllocatedCount") == 1 and
                 staged.get("reservedImageCount") == 1 and staged.get("reservationCount") == 2 and
                 staged.get("nextImageId") == 3 and staged.get("reservedPages") == reserved.get("reservedPages") and
                 staged.get("nextPageSlot") == reserved.get("nextPageSlot") and staged.get("mappedPages") >= 0,
                 "early rejected staging ledger is not exact")
        _require(validated.get("ordinaryAllocatedCount") == 1 and validated.get("shadowAllocatedCount") == 1 and
                 validated.get("reservedImageCount") == 1 and validated.get("reservationCount") == 2 and
                 validated.get("nextImageId") == 3 and
                 validated.get("reservedPages") >= staged.get("reservedPages") and
                 validated.get("nextPageSlot") >= staged.get("nextPageSlot") and
                 validated.get("reservedPages") - staged.get("reservedPages") ==
                 validated.get("nextPageSlot") - staged.get("nextPageSlot") and
                 validated.get("mappedPages") >= staged.get("mappedPages"),
                 "early rejected validation did not retain one monotonically extended reservation")
        target = "AssemblyShadow.H1Count.Target" if request["family"] == "parameters" else "AssemblyShadow.H1Nested.Target"
        diagnostic = parsed["after-validate"][1]
        _require(diagnostic.get("expected") == 1 and diagnostic.get("staged") == 1 and
                 diagnostic.get("closureLoadOrder") == [target] and isinstance(diagnostic.get("assemblies"), list) and
                 len(diagnostic["assemblies"]) == 1 and diagnostic["assemblies"][0].get("name") == target and
                 diagnostic["assemblies"][0].get("skeletonBuilt") is True and
                 diagnostic["assemblies"][0].get("runtimeMetadataInitialized") is False and
                 diagnostic["assemblies"][0].get("published") is False,
                 "early rejected diagnostics do not identify the staged candidate")
        detail = diagnostic.get("detail")
        if request["family"] == "parameters":
            _require(_parameter_guard_count(detail) == _expected(request)[0],
                     "early rejection detail does not identify the requested parameter count")
        else:
            _require([line.split(": ", 1)[-1] for line in str(detail or "").splitlines()] ==
                     ["interpreter nested type count exceeds native limit"],
                     "early rejection detail does not identify the requested nested count guard")
    if accepted:
        committed = parsed["after-commit"][0]
        _require(committed == parsed["after"][0] and
                 parsed["after-validate"][0]["shadowAllocatedCount"] == 1,
                 "early accepted commit ledger differs")
        _require(committed.get("ordinaryAllocatedCount") == 1 and
                 committed.get("shadowAllocatedCount") == 1 and
                 committed.get("reservedImageCount") == 1 and
                 committed.get("reservationCount") == 2 and
                 committed.get("nextImageId") == 3,
                 "early accepted commit allocation ledger is not exact")
        target_name = ("AssemblyShadow.H1Count.Target" if request["family"] == "parameters"
                       else "AssemblyShadow.H1Nested.Target")
        expected_name = request.get("assemblyName", target_name)
        expected_full_name = request.get("assemblyFullName")
        expected_mvid = request.get("assemblyMvid")

        def inventory(snapshot, key):
            values = snapshot.get(key)
            _require(isinstance(values, list) and all(isinstance(value, dict) for value in values),
                     "early accepted native " + key + " inventory is malformed")
            identity_keys = [value.get("identityKey") for value in values]
            _require(all(isinstance(value, str) and "|" in value for value in identity_keys) and
                     len(identity_keys) == len(set(identity_keys)),
                     "early accepted native " + key + " identities are incomplete or duplicated")
            return values

        before_logical = inventory(before, "logicalAssemblies")
        after_logical = inventory(committed, "logicalAssemblies")
        before_physical = inventory(before, "physicalAssemblies")
        after_physical = inventory(committed, "physicalAssemblies")
        before_published = inventory(before, "publishedInterpreterImages")
        after_published = inventory(committed, "publishedInterpreterImages")

        def named(values):
            return [value for value in values if value.get("name") == target_name]

        def unrelated_keys(values):
            return sorted(value["identityKey"] for value in values if value.get("name") != target_name)

        logical_target_before = named(before_logical)
        logical_target_after = named(after_logical)
        physical_target_before = named(before_physical)
        physical_target_after = named(after_physical)
        published_target_before = named(before_published)
        published_target_after = named(after_published)
        _require(len(logical_target_before) == 1 and len(logical_target_after) == 1 and
                 len(physical_target_before) == 1 and len(physical_target_after) == 2 and
                 not published_target_before and len(published_target_after) == 1,
                 "early accepted target identity cardinality differs")
        published = published_target_after[0]
        _require(logical_target_after[0].get("identityKey") == published.get("identityKey") and
                 sum(value.get("identityKey") == published.get("identityKey")
                     for value in physical_target_after) == 1 and
                 published.get("name") == expected_name and
                 published.get("imageKind") == "Interpreter" and
                 published.get("imageId") == before.get("nextImageId") and
                 published.get("published") is True and published.get("mvidAvailable") is True and
                 isinstance(published.get("nativeAssemblyId"), str) and published.get("nativeAssemblyId") and
                 isinstance(published.get("nativeImageId"), str) and published.get("nativeImageId") and
                 (expected_full_name is None or published.get("fullName") == expected_full_name) and
                 (expected_mvid is None or published.get("mvid") == expected_mvid),
                 "early accepted published interpreter identity differs from the fixture")
        _require(unrelated_keys(before_logical) == unrelated_keys(after_logical) and
                 unrelated_keys(before_physical) == unrelated_keys(after_physical) and
                 unrelated_keys(before_published) == unrelated_keys(after_published),
                 "early accepted commit changed an unrelated native identity")
        _require(logical_target_before[0].get("identityKey") != published.get("identityKey") and
                 any(value.get("identityKey") == logical_target_before[0].get("identityKey")
                     for value in physical_target_after),
                 "early accepted commit did not replace the logical baseline while retaining its physical image")
        _require(parsed["after-commit"][1].get("state") == "Committed" and
                 parsed["after-commit"][1].get("lastError") == 0,
                 "early accepted diagnostics do not prove Committed")
    else:
        _require(parsed["after-validate"][0] == parsed["after"][0] and
                 parsed["after-validate"][1].get("state") == "Failed" and
                 parsed["after-validate"][1].get("lastError") == 13,
                 "early rejected diagnostics do not prove retained ReferenceResolutionFailed")
    return parsed


def verify_early_receipt_document(early, early_bytes, request, *, build=None,
                                  fixture=None, fixture_sha256=None, expected_result_path=None):
    """Verify the authenticated pre-scene transaction receipt.

    This is intentionally independent of the final scene result: a rejected
    startup callback is expected to terminate before H1CountDiagnosticRunner
    can run.
    """
    _require(isinstance(early, dict), "early startup receipt must be an object")
    _require(early.get("schemaVersion") == EARLY_EVIDENCE_SCHEMA_VERSION and
             early.get("kind") == "H1CountEarlyStartupResult" and
             early.get("diagnosticOnly") is True and early.get("path") == "shadow",
             "early startup receipt header differs")
    supplied = _sha(early.get("receiptSha256"), "early startup receipt authentication")
    unsigned = _early_canonical_json(early, "")
    _require(hashlib.sha256(unsigned.encode("utf-8")).hexdigest() == supplied,
             "early startup receipt authentication hash differs")
    _require(isinstance(early_bytes, (bytes, bytearray)) and len(early_bytes) > 0,
             "early startup receipt bytes could not be observed")
    _require(early.get("family") == request["family"] and early.get("caseId") == request["caseId"] and
             early.get("expectedCount") == _expected(request)[0] and
             early.get("expectedOutcome") == _expected(request)[-1],
             "early startup receipt case differs")
    _require(isinstance(early.get("processId"), int) and early["processId"] > 0 and
             early.get("managedThreadId", 0) > 0, "early startup receipt process identity is invalid")
    if expected_result_path is not None:
        _require(early.get("resultPath") == str(expected_result_path),
                 "early startup receipt path differs from the launcher argument")
    if fixture is not None:
        _require(early.get("fixturePath") == str(fixture) and early.get("fixtureSha256Expected") == fixture_sha256 and
                 early.get("inputHashBefore") == fixture_sha256 and early.get("inputHashAfter") == fixture_sha256 and
                 early.get("fixtureSize") == fixture.stat().st_size,
                 "early startup fixture binding differs")
    if build is not None:
        _require(early.get("baselineBuildId") == build.get("baselineBuildId") and
                 early.get("runtimeAbiHash") == build.get("runtimeAbiHash"),
                 "early startup baseline/ABI binding differs")
    expected = _expected(request)[-1]
    accepted = expected == "Accepted"
    expected_ops = [("configure", "Success"), ("begin", "Success"), ("reserve", "Success"),
                    ("stage", "Success"), ("validate", "Success" if accepted else "ReferenceResolutionFailed")]
    if accepted:
        expected_ops.append(("commit", "Success"))
    operations = early.get("operations")
    _require(isinstance(operations, list) and len(operations) == len(expected_ops),
             "early startup operation sequence differs")
    for item, (phase, code) in zip(operations, expected_ops):
        expected_int_code = 13 if code == "ReferenceResolutionFailed" else 0
        _require(isinstance(item, dict) and item.get("phase") == phase and item.get("code") == code and
                 item.get("intCode") == expected_int_code,
                 "early startup operation evidence differs at " + phase)
    _require(early.get("baselineAlreadyUsed") is False, "early startup receipt reports baseline reuse")
    _verify_witness_document(early.get("witness"))
    _verify_early_native_snapshots(early, request, accepted)
    if accepted:
        _require(early.get("result") == "Committed" and early.get("callbackReturnCode") == 0 and
                 early.get("committed") is True and early.get("disposition") == "CommittedForSceneHandoff",
                 "early accepted receipt does not prove committed handoff")
    else:
        _require(early.get("result") == "ExpectedValidationRejection" and early.get("callbackReturnCode") == 1 and
                 early.get("committed") is False and early.get("disposition") == "ValidationFailedNoCommitNoAbort",
                 "early rejected receipt does not prove retained rejection")
    return {"passed": True, "result": early["result"], "callbackReturnCode": early["callbackReturnCode"],
            "receiptSha256": supplied, "accepted": accepted}


def _require(condition, message):
    if not condition:
        raise VerificationError(message)


def _sha(value, label):
    _require(isinstance(value, str) and len(value) == 64 and
             all(character in "0123456789abcdefABCDEF" for character in value),
             label + " must be a SHA-256")
    return value.lower()


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _canonical_file(value, label: str) -> Path:
    path = Path(value)
    _require(path.is_absolute() and path == path.resolve() and path.is_file() and
             not path.is_symlink(), label + " must be an existing canonical file")
    for parent in path.parents:
        _require(not parent.is_symlink() and parent == parent.resolve(),
                 label + " has a symlinked or noncanonical parent")
    return path


def _unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise VerificationError("Duplicate JSON key: " + key)
        value[key] = item
    return value


def _witness_keys(snapshot, witness, field, label):
    values = snapshot.get(field)
    _require(isinstance(values, list), label + " witness inventory is missing")
    logical = field == "logicalAssemblies"
    expected_kind = "Aot" if logical else "Interpreter"
    matches = [value for value in values
               if isinstance(value, dict) and value.get("name") == witness["assemblyName"] and
               value.get("fullName") == witness["assemblyFullName"] and
               value.get("imageKind") == expected_kind]
    _require(len(matches) == 1, label + " witness identity is missing or ambiguous")
    identity = matches[0]
    state_valid = (identity.get("published") is False and identity.get("mvidAvailable") is False and
                   identity.get("mvid") == "" and identity.get("imageId") == 0) if logical else (
                  identity.get("published") is True and identity.get("mvidAvailable") is True and
                  isinstance(identity.get("mvid"), str) and bool(identity["mvid"]) and
                  identity.get("imageId") == 1)
    _require(state_valid and isinstance(identity.get("nativeAssemblyId"), str) and
             identity["nativeAssemblyId"] not in ("0", "0x0") and
             isinstance(identity.get("nativeImageId"), str) and
             identity["nativeImageId"] not in ("0", "0x0") and
             isinstance(identity.get("identityKey"), str) and identity["identityKey"],
             label + " witness identity is incomplete or has the wrong native publication state")
    return [identity["identityKey"]]


def _verify_witness_document(witness, *, require_file=True):
    _require(isinstance(witness, dict), "ordinary witness observation is missing")
    _require(witness.get("available", True) is True, "ordinary witness observation is unavailable")
    path_value = witness.get("path")
    _require(isinstance(path_value, str) and path_value.endswith(ORDINARY_WITNESS_RELATIVE_PATH),
             "ordinary witness path is not the pinned M00 path")
    path = _canonical_file(path_value, "ordinary witness") if require_file else None
    _require(witness.get("sha256") == ORDINARY_WITNESS_SHA256 and
             (path is None or _sha256(path) == ORDINARY_WITNESS_SHA256) and
             witness.get("assemblyName") == ORDINARY_WITNESS_NAME and
             witness.get("assemblyFullName") == ORDINARY_WITNESS_FULL_NAME and
             witness.get("observationKind") == "NativeAssemblyIdentity",
             "ordinary witness provenance or identity observation differs")


def _verify_witness_snapshots(snapshots, witness):
    _verify_witness_document(witness)
    expected = (witness.get("logicalIdentityKeys"), witness.get("physicalIdentityKeys"),
                witness.get("publishedIdentityKeys"))
    supplied = all(isinstance(value, list) and len(value) == 1 and
                   isinstance(value[0], str) and value[0] for value in expected)
    _require(supplied, "ordinary witness native identity binding is incomplete")
    for phase, snapshot in snapshots.items():
        actual = tuple(_witness_keys(snapshot, witness, field, "native " + field + " at " + phase)
                       for field in ("logicalAssemblies", "physicalAssemblies", "publishedInterpreterImages"))
        _require(actual == expected, "ordinary witness native identity changed at " + phase)


def read_json(path, label: str) -> tuple[dict, bytes]:
    path = _canonical_file(path, label)
    with path.open("rb") as stream:
        data = stream.read(MAX_JSON_BYTES + 1)
    _require(0 < len(data) <= MAX_JSON_BYTES, label + " is empty or oversized")
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError) as error:
        raise VerificationError(label + " is not valid JSON: " + str(error)) from error
    _require(type(value) is dict, label + " must contain an object")
    return value, data


def _hash_map(value, label):
    _require(isinstance(value, dict), label + " must be an object")
    for file_name, expected in value.items():
        _require(isinstance(file_name, str) and SHA256.fullmatch(str(expected) or "") is not None,
                 label + " contains an invalid hash")
        path = _canonical_file(file_name, label + " file")
        _require(_sha256(path) == expected, label + " hash differs: " + file_name)


def _expected(request):
    family = request["family"]
    table = PARAMETER_CASES if family == "parameters" else NESTED_CASES
    if request["caseId"] not in table:
        raise VerificationError("Unknown canonical " + family + " case: " + request["caseId"])
    return table[request["caseId"]]


def _path_parts(path_name):
    paths = {
        "Ordinary-ON": ("ordinary", True),
        "Ordinary-OFF": ("ordinary", False),
        "Shadow-ON": ("shadow", True),
    }
    _require(path_name in paths, "invalid expected path")
    return paths[path_name]


def _expected_parameter_shape(case_id):
    count, variant, _ = PARAMETER_CASES[case_id]
    if variant == "mixed-kinds":
        pattern = ("System.Int32", "System.String", "System.Object", "System.Int32&", "System.String[]")
        types = [pattern[i % len(pattern)] for i in range(count)]
    else:
        types = ["System.Int32"] * count
    if variant == "partial-names":
        rows = [{"sequence": i, "name": f"p{i:04d}", "isReturn": False}
                for i in range(1, count + 1) if (i - 1) % 17 == 0]
    elif variant == "return255":
        rows = [{"sequence": 0, "name": "result", "isReturn": True}]
    else:
        rows = []
    return count, types, rows, variant == "instance"


def _expected_nested_shape(case_id):
    count, groups, declaring, interleaved, _ = NESTED_CASES[case_id]
    expected = []
    for name, group_count in zip(declaring, groups):
        parent = "AssemblyShadow.H1Nested." + name
        children = [parent + "+" + name + "Child" + f"{i:05d}" for i in range(group_count)]
        expected.append({"declaringType": parent, "count": group_count, "children": children})
    return count, expected, interleaved


def _verify_shape(shape, request, artifact):
    family = request["family"]
    _require(shape.get("sha256") == artifact.get("sha256") and
             shape.get("sizeBytes") == artifact.get("sizeBytes"),
             "independently decoded fixture bytes differ from manifest")
    _require(shape.get("identity", {}).get("name") == artifact.get("name") and
             shape.get("identity", {}).get("fullName") == artifact.get("fullName") and
             shape.get("identity", {}).get("version") == artifact.get("version") and
             shape.get("identity", {}).get("mvid") == artifact.get("mvid"),
             "independently decoded fixture identity differs from manifest")
    if family == "parameters":
        count, types, rows, instance = _expected_parameter_shape(request["caseId"])
        methods = [m for m in shape.get("methods", [])
                   if m.get("name") == "Probe" and m.get("declaringType") == artifact.get("targetType")]
        _require(len(methods) == 1, "fixture Probe method identity is not unique")
        method = methods[0]
        sig = method.get("signature", {})
        _require(sig.get("count") == count and sig.get("returnType") == "System.Int32" and
                 sig.get("instance") is instance and sig.get("parameterTypes") == types,
                 "independently decoded parameter signature differs from canonical case")
        actual_rows = [{"sequence": r.get("sequence"), "name": r.get("name"),
                        "isReturn": r.get("sequence") == 0}
                       for r in method.get("paramRows", [])]
        _require(actual_rows == rows, "independently decoded parameter rows differ")
    else:
        count, groups, interleaved = _expected_nested_shape(request["caseId"])
        actual = shape.get("nestedGroups")
        types = shape.get("types")
        _require(isinstance(actual, list) and isinstance(types, list) and
                 all(isinstance(item, dict) for item in actual + types),
                 "independently decoded nested relationships are malformed")
        _require(shape.get("nestedClassTableCount") == count and
                 shape.get("typeDefCount") == 1 + len(groups) + count and
                 shape.get("methodDefCount") == 0 and shape.get("paramTableCount") == 0 and
                 shape.get("methods") == [] and shape.get("nestedClassSortedDeclared") is True,
                 "independently decoded nested table counts differ")
        for expected in groups:
            parents = [item for item in types if item.get("fullName") == expected["declaringType"]]
            _require(len(parents) == 1 and type(parents[0].get("rid")) is int and
                     parents[0].get("parentRid") is None,
                     "nested declaring TypeDef is absent, duplicated, or itself nested")
            parent_rid = parents[0]["rid"]
            children = [item for item in types if item.get("parentRid") == parent_rid]
            _require([item.get("fullName") for item in children] == expected["children"],
                     "independently decoded nested child relationships differ")
            found = [g for g in actual if g.get("declaringType") == expected["declaringType"]]
            if expected["count"] == 0:
                _require(found == [] and children == [],
                         "zero-nested case contains a relationship row")
            else:
                _require(len(found) == 1 and found[0].get("parentRid") == parent_rid and
                         found[0].get("count") == expected["count"] and
                         found[0].get("first") == expected["children"][0] and
                         found[0].get("last") == expected["children"][-1],
                         "independently decoded nested group differs")
        _require(sum(group.get("count", -1) for group in actual) == count and
                 len(actual) == sum(1 for group in groups if group["count"]),
                 "independently decoded nested group inventory differs")
        _require(type(interleaved) is bool, "invalid nested interleaving contract")


def _verify_audit_observation(audited, shape, request, fixture_case):
    """Recreate the formal audit row from fresh bytes, then compare its real schema."""
    _require(isinstance(audited, dict), "fixture audit selected observation is missing")
    module_name = "h1_count_manifest" if request["family"] == "parameters" else "h1_nested_manifest"
    try:
        module = importlib.import_module(module_name)
        fresh = module.validate_observation(fixture_case, request["flavor"], shape)
    except (KeyError, TypeError, ValueError) as error:
        raise VerificationError("fresh fixture audit validation failed: " + str(error)) from error
    _require(audited == fresh,
             "stored fixture audit observation differs from the freshly decoded formal audit row")
    return fresh


def _text_fields(result):
    texts = []
    for key in ("errorFull", "controlledRejectionErrorFull"):
        if isinstance(result.get(key), str):
            texts.append(result[key])
    if isinstance(result.get("countGuardDiagnostic"), str):
        texts.append(result["countGuardDiagnostic"])
    publication = result.get("publication") or {}
    for key in ("rejectedExceptionFull", "publicAssemblyObservation"):
        if isinstance(publication.get(key), str):
            texts.append(publication[key])
    for step in result.get("operationSteps") or []:
        if isinstance(step, dict):
            texts.extend(str(step.get(k)) for k in ("detail", "errorFull") if step.get(k))
    return "\n".join(texts).lower()


def _snapshot_checks(result, request, accepted):
    records = result.get("snapshots")
    if not isinstance(records, list) or not records:
        raise NoCoverage("native diagnostic snapshot/ledger evidence is missing")
    expected_phases = (["before", "after", "final"] if request["flavor"] == "ordinary" else
                       ["before", "after-configure", "after-begin", "after-reserve",
                        "after-stage", "after-validate"] +
                       (["after-commit"] if accepted else []) + ["after", "final"])
    _require([record.get("phase") for record in records if isinstance(record, dict)] == expected_phases and
             len(records) == len(expected_phases),
             "native ledger phase sequence is incomplete, duplicated, or unexpected")
    snapshots = {}
    numeric = ("reservedPages", "mappedPages", "reservationCount", "nextImageId",
               "nextPageSlot", "ordinaryAllocatedCount", "shadowAllocatedCount",
               "reservedImageCount")
    for record in records:
        if not isinstance(record, dict) or record.get("available") is not True:
            raise NoCoverage("native diagnostic snapshot/ledger is unavailable")
        snapshot = record.get("snapshot")
        if not isinstance(snapshot, dict):
            raise NoCoverage("native diagnostic snapshot body is missing")
        for field in ("schemaVersion", "kind", "diagnosticOnly", "featureEnabled",
                      "featureMode") + numeric:
            if field not in snapshot:
                raise NoCoverage("native ledger field is missing: " + field)
        if (snapshot["kind"] != "H1CountNativeDiagnostics" or snapshot["schemaVersion"] != 1 or
                snapshot["diagnosticOnly"] is not True):
            raise VerificationError("native ledger identity is invalid")
        if snapshot["featureEnabled"] is not request["featureEnabled"]:
            raise VerificationError("native ledger feature state differs from authenticated build")
        expected_mode = "AssemblyShadowOn" if request["featureEnabled"] else "AssemblyShadowOff"
        if snapshot["featureMode"] != expected_mode:
            raise VerificationError("native ledger feature mode differs from authenticated build")
        if snapshot["mappedPages"] > snapshot["reservedPages"]:
            raise VerificationError("native ledger mapped pages exceed reservation")
        if any(type(snapshot[field]) is not int or snapshot[field] < 0 for field in numeric):
            raise VerificationError("native ledger counters are invalid")
        snapshots[record["phase"]] = snapshot
    before = snapshots["before"]
    _verify_witness_snapshots(snapshots, result.get("witness"))
    _require(before["ordinaryAllocatedCount"] == 1 and before["shadowAllocatedCount"] == 0 and
             before["reservedImageCount"] == 0 and before["reservationCount"] == 1 and
             before["nextImageId"] == 2 and before["reservedPages"] > 0 and
             before["nextPageSlot"] == before["reservedPages"],
             "native ledger did not retain exactly one preloaded ordinary witness")
    if request["flavor"] == "shadow":
        _require(snapshots["after-configure"] == before and snapshots["after-begin"] == before,
                 "shadow configure/begin changed the empty native ledger or assembly inventories")
    _require(snapshots["after"] == snapshots["final"],
             "successive final native ledger observations differ")

    def exact(snapshot, ordinary, shadow, reserved, reservations, image_id):
        return (snapshot["ordinaryAllocatedCount"] == ordinary and
                snapshot["shadowAllocatedCount"] == shadow and
                snapshot["reservedImageCount"] == reserved and
                snapshot["reservationCount"] == reservations and
                snapshot["nextImageId"] == image_id)

    final = snapshots["final"]
    if request["flavor"] == "ordinary":
        _require(exact(final, 2, 0, 0, 2, 3) and
                 final["reservedPages"] > 0 and
                 final["nextPageSlot"] == final["reservedPages"],
                 "ordinary ledger did not retain exactly one ordinary identity and page reservation")
    else:
        reserved = snapshots["after-reserve"]
        _require(exact(reserved, 1, 0, 1, 2, 3) and reserved["reservedPages"] > 0 and
                 reserved["nextPageSlot"] == reserved["reservedPages"] and
                 reserved["mappedPages"] == before["mappedPages"],
                 "profile 2 reservation ledger is not exact")
        staged = snapshots["after-stage"]
        _require(exact(staged, 1, 1, 1, 2, 3) and
                 staged["reservedPages"] == reserved["reservedPages"] and
                 staged["nextPageSlot"] == reserved["nextPageSlot"] and
                 staged["mappedPages"] >= reserved["mappedPages"],
                 "StageAssembly did not use exactly one reserved shadow identity")
        validated = snapshots["after-validate"]
        _require(exact(validated, 1, 1, 1, 2, 3) and
                 validated["reservedPages"] >= reserved["reservedPages"] and
                 validated["nextPageSlot"] >= reserved["nextPageSlot"] and
                 validated["reservedPages"] - reserved["reservedPages"] ==
                 validated["nextPageSlot"] - reserved["nextPageSlot"] and
                 validated["mappedPages"] >= staged["mappedPages"] and
                 exact(final, 1, 1, 1, 2, 3) and
                 final["reservedPages"] >= reserved["reservedPages"] and
                 final["nextPageSlot"] >= reserved["nextPageSlot"] and
                 final["reservedPages"] - reserved["reservedPages"] ==
                 final["nextPageSlot"] - reserved["nextPageSlot"] and
                 final["mappedPages"] >= validated["mappedPages"],
                 "shadow validation/final ledger refunded credits or allocated an extra identity")
        if accepted:
            _require(snapshots["after-commit"] == final,
                     "commit or public lookup changed the retained native ledger")
        else:
            _require(validated == final,
                     "failed validation ledger was not retained exactly")
    _require(result.get("ledgerVerified") is True and
             result.get("admissionFailedNoCoverage") is not True,
             "probe ledger disposition contradicts the independently verified snapshots")
    return snapshots


def _verify_reflection(result, request, expected_count, shape):
    if request["family"] == "parameters":
        observation = result.get("parameter") or {}
        _require(observation.get("available") is True and observation.get("count") == expected_count and
                 result.get("observedCountAvailable") is True and result.get("observedCount") == expected_count,
                 "observed parameter count is missing or incorrect")
        count, types, rows, instance = _expected_parameter_shape(request["caseId"])
        _require(observation.get("targetType") == request["targetType"] and
                 "Probe(" in observation.get("targetMethod", "") and
                 observation.get("returnType") == "System.Int32" and observation.get("instance") is instance and
                 observation.get("parameterTypes") == types and observation.get("repeatPassed") is True and
                 observation.get("paramRowsRepeatPassed") is True,
                 "observed parameter reflection shape differs")
        observed_rows = observation.get("paramRows")
        if request["caseId"] == "H1R-P04-return255":
            audited_methods = [method for method in (shape or {}).get("methods", [])
                               if method.get("declaringType") == request["targetType"] and
                               method.get("name") == "Probe"]
            audited_rows = audited_methods[0].get("paramRows") if len(audited_methods) == 1 else None
            _require(audited_rows == [{"rid": audited_rows[0]["rid"], "flags": audited_rows[0]["flags"],
                                       "sequence": 0, "name": "result"}] if audited_rows else False,
                     "independent fixture bytes do not contain the required return Param row 0")
            _require(observation.get("returnParameterRowByteOracleRequired") is True and
                     type(observation.get("returnParameterRowPublicReflectionAvailable")) is bool and
                     isinstance(observation.get("returnParameterRowObservation"), str),
                     "return Param-row capability observation is incomplete")
            if observation["returnParameterRowPublicReflectionAvailable"]:
                _require(observed_rows == rows and "exposed" in observation["returnParameterRowObservation"],
                         "available return Param-row reflection contradicts its observation")
            else:
                _require(observed_rows == [] and "did not expose" in observation["returnParameterRowObservation"],
                         "unavailable return Param-row reflection contradicts its observation")
        else:
            _require(observed_rows == rows, "observed Param rows differ")
    else:
        observation = result.get("nested") or {}
        _require(observation.get("available") is True and observation.get("totalCount") == expected_count and
                 result.get("observedCountAvailable") is True and result.get("observedCount") == expected_count and
                 observation.get("repeatPassed") is True,
                 "observed nested count is missing or incorrect")
        _, groups, _ = _expected_nested_shape(request["caseId"])
        actual = observation.get("groups") or []
        _require(len(actual) == len(groups), "observed nested group count differs")
        for observed, expected in zip(actual, groups):
            _require(observed.get("declaringType") == expected["declaringType"] and
                     observed.get("count") == expected["count"] and
                     observed.get("children") == expected["children"] and
                     observed.get("repeatPassed") is True,
                     "observed nested child identities differ")


def _public_inventory(publication, accepted, shadow):
    before = publication.get("publicAssembliesBefore")
    after = publication.get("publicAssembliesAfter")
    physical_before = publication.get("physicalAssembliesBefore")
    physical_after = publication.get("physicalAssembliesAfter")
    published_before = publication.get("publishedInterpreterImagesBefore")
    published_after = publication.get("publishedInterpreterImagesAfter")
    _require(isinstance(before, list) and isinstance(after, list) and
             isinstance(physical_before, list) and isinstance(physical_after, list) and
             isinstance(published_before, list) and isinstance(published_after, list) and
             all(isinstance(value, str) and "|" in value for value in
                 before + after + physical_before + physical_after + published_before + published_after) and
             before == sorted(set(before)) and after == sorted(set(after)) and
             physical_before == sorted(set(physical_before)) and physical_after == sorted(set(physical_after)) and
             published_before == sorted(set(published_before)) and published_after == sorted(set(published_after)),
             "native logical/physical/published inventories are malformed")
    def name(value):
        return value.split("|", 1)[0]
    def target(value):
        parts = value.split("|")
        return (len(parts) >= 3 and parts[0] == publication.get("publicAssemblyName") and
                parts[1] == publication.get("publicAssemblyMvid") and
                parts[2] == publication.get("publicAssemblyFullName"))
    target_name = str(publication.get("publicAssemblyName"))
    if not accepted:
        _require(before == after and publication.get("publicAssemblyInventoryStable") is True and
                 physical_before == physical_after and published_before == published_after and
                 publication.get("publicIdentityObservationAvailable") is True and
                 publication.get("noPublicFixtureIdentity") is True,
                 "rejected operation changed a logical, physical, or published image inventory")
        return
    target_before = [value for value in before if name(value) == target_name]
    target_after = [value for value in after if name(value) == target_name]
    unrelated_before = [value for value in before if name(value) != target_name]
    unrelated_after = [value for value in after if name(value) != target_name]
    _require(len(target_after) == 1 and target(target_after[0]) and unrelated_before == unrelated_after,
             "accepted operation lost or added an unrelated public assembly identity")
    if shadow:
        _require(len(target_before) == 1 and not target(target_before[0]) and
                 publication.get("publicAssemblyLoaded") is True,
                 "committed shadow fixture did not replace exactly one baseline public identity")
    else:
        _require(target_before == [],
                 "ordinary accepted fixture identity was already public before Assembly.Load")
    physical_target_before = [value for value in physical_before if target(value)]
    physical_target_after = [value for value in physical_after if target(value)]
    published_target_before = [value for value in published_before if target(value)]
    published_target_after = [value for value in published_after if target(value)]
    _require(not physical_target_before and len(physical_target_after) == 1 and
             not published_target_before and len(published_target_after) == 1,
             "accepted operation did not add exactly one authenticated physical/published fixture identity")


def _state_checks(result, accepted):
    expected = [
        ("after-configure", "CandidatesRegistered"),
        ("after-begin", "Staging"),
        ("after-reserve", "Staging"),
        ("after-stage", "Staged"),
        ("after-validate", "Validated" if accepted else "Failed"),
    ] + ([("after-commit", "Committed")] if accepted else [])
    states = result.get("states")
    if not isinstance(states, list):
        raise NoCoverage("shadow transaction state evidence is missing")
    _require(len(states) == len(expected),
             "shadow transaction state observations are incomplete or unexpected")
    for observed, (phase, state) in zip(states, expected):
        _require(isinstance(observed, dict) and observed.get("phase") == phase and
                 observed.get("available") is True and observed.get("code") == "Success" and
                 observed.get("state") == state,
                 "shadow transaction state differs at " + phase)


def _operation_checks(result, accepted, shadow):
    operations = result.get("operationSteps")
    _require(isinstance(operations, list) and all(isinstance(step, dict) for step in operations),
             "operation step evidence is malformed")
    if shadow:
        expected = [
            ("ConfigureCandidates", True, "Success"),
            ("BeginTransaction", True, "Success"),
            ("ReserveMetadataBudget", True, "Success"),
            ("StageAssembly", True, "Success"),
            ("ValidateTransaction", accepted, "Success" if accepted else "ReferenceResolutionFailed"),
        ] + ([('CommitTransaction', True, 'Success')] if accepted else [])
    else:
        expected = [
            ("ordinary-path-selected", True, "Success"),
            ("Assembly.Load(byte[])", accepted, "Success" if accepted else "Exception"),
        ]
    _require(len(operations) == len(expected), "operation step count differs")
    for step, (operation, success, code) in zip(operations, expected):
        _require(step.get("operation") == operation and step.get("success") is success and
                 step.get("code") == code,
                 "operation status differs for " + operation)


def _verify_failure_diagnostics(publication, result):
    raw = publication.get("failureDiagnosticsJson")
    _require(publication.get("failureDiagnosticsAvailable") is True and
             publication.get("failureDiagnosticsCode") == "Success" and
             isinstance(raw, str) and raw,
             "shadow rejection failure diagnostics are unavailable")
    try:
        diagnostic = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (TypeError, ValueError) as error:
        raise VerificationError("shadow failure diagnostics JSON is invalid: " + str(error)) from error
    _require(isinstance(diagnostic, dict) and diagnostic.get("schemaVersion") == 1 and
             diagnostic.get("state") == "Failed" and diagnostic.get("lastError") == 13 and
             isinstance(diagnostic.get("detail"), str) and diagnostic.get("detail") and
             publication.get("failureDiagnosticsState") == diagnostic["state"] and
             publication.get("failureDiagnosticsLastError") == diagnostic["lastError"] and
             publication.get("failureDiagnosticsDetail") == diagnostic["detail"] and
             result.get("countGuardDiagnostic") == diagnostic["detail"] and
             result.get("controlledRejectionErrorFull") == diagnostic["detail"],
             "shadow failure diagnostics do not bind Failed/ReferenceResolutionFailed to the guard detail")


def _verify_publication(result, request, accepted, artifact):
    publication = result.get("publication") or {}
    shadow = request["flavor"] == "shadow"
    if accepted and artifact is not None:
        snapshots = result.get("snapshots") or []
        before = next((record.get("snapshot") for record in snapshots
                       if isinstance(record, dict) and record.get("phase") == "before" and
                       isinstance(record.get("snapshot"), dict)), None)
        _require(publication.get("publicAssemblyName") == artifact.get("name") and
                 publication.get("publicAssemblyFullName") == artifact.get("fullName") and
                 publication.get("publicAssemblyMvid") == artifact.get("mvid") and
                 publication.get("publicAssemblyMvidAvailable") is True and
                 publication.get("imageKind") == "Interpreter" and
                 isinstance(publication.get("nativeAssemblyId"), str) and publication.get("nativeAssemblyId") and
                 isinstance(publication.get("nativeImageId"), str) and publication.get("nativeImageId") and
                 isinstance(publication.get("imageId"), int) and publication.get("imageId") > 0 and
                 isinstance(before, dict) and publication.get("imageId") == before.get("nextImageId"),
                 "published assembly identity differs from the authenticated fixture")
    _operation_checks(result, accepted, shadow)
    if not shadow:
        _require(result.get("states") == [] and
                 all(publication.get(key) is False for key in
                     ("configureCalled", "beginCalled", "reserveCalled", "stageCalled",
                      "validateCalled", "commitCalled", "abortCalled", "committed")),
                 "ordinary operation invoked or fabricated a Shadow transaction")
        _require(publication.get("publicAssemblyLoaded") is accepted and
                 (not accepted or publication.get("publicAssemblyMatchesExpected") is True),
                 "ordinary publication outcome differs")
        _public_inventory(publication, accepted, False)
        return

    _state_checks(result, accepted)
    _require(publication.get("configureCalled") is True and publication.get("configureCode") == "Success" and
             publication.get("beginCalled") is True and publication.get("beginCode") == "Success" and
             publication.get("reserveCalled") is True and publication.get("reserveCode") == "Success" and
             publication.get("reserveProfileVersion") == 2 and
             publication.get("stageCalled") is True and publication.get("stageCode") == "Success" and
             publication.get("validateCalled") is True and
             publication.get("validateCode") == ("Success" if accepted else "ReferenceResolutionFailed") and
             publication.get("abortCalled") is False and publication.get("initializerObserved") is False,
             "shadow transaction publication steps differ")
    if accepted:
        _require(publication.get("commitCalled") is True and publication.get("commitCode") == "Success" and
                 publication.get("committed") is True and publication.get("publicAssemblyLoaded") is True and
                 publication.get("publicAssemblyMatchesExpected") is True and
                 publication.get("executionModeAvailable") is True and
                 publication.get("executionModeCode") == "Success" and
                 publication.get("executionMode") == "InterpreterShadow",
                 "committed shadow publication is not authenticated")
    else:
        _require(publication.get("commitCalled") is False and publication.get("committed") is False and
                 publication.get("publicAssemblyLoaded") is False and
                 publication.get("executionModeAvailable") is True and
                 publication.get("executionModeCode") == "Success" and
                 publication.get("executionMode") == "AotBaseline",
                 "failed shadow validation publication/execution mode differs")
        _verify_failure_diagnostics(publication, result)
    _public_inventory(publication, accepted, True)


def _parameter_guard_count(diagnostic):
    _require(isinstance(diagnostic, str) and diagnostic,
             "parameter count-guard diagnostic is missing")
    pattern = re.compile(
        r"(?:^|: )(?:method token:[0-9]+|method:[^\s]+\.[^\s]+) "
        r"parameter count:([0-9]+) is too large$")
    counts = []
    for line in diagnostic.splitlines():
        match = pattern.search(line.rstrip("\r"))
        if match:
            counts.append(int(match.group(1)))
    _require(counts and len(set(counts)) == 1,
             "parameter diagnostic does not contain one unambiguous exact native guard count")
    return counts[0]


def _verify_count_guard(result, request, expected_count):
    diagnostic = result.get("countGuardDiagnostic")
    _require(result.get("countGuardDiagnosticAvailable") is True and
             result.get("countGuardExpectedDecodedCount") == expected_count and
             result.get("countGuardDiagnosticSource") in
             ("ordinary-exception", "shadow-diagnostics-detail"),
             "count-guard attribution fields are incomplete")
    if request["family"] == "parameters":
        parsed = _parameter_guard_count(diagnostic)
        _require(parsed == expected_count and
                 result.get("countGuardDecodedCountAvailable") is True and
                 result.get("countGuardDecodedCount") == parsed and
                 result.get("countGuardCountSource") == "native-parameter-guard-diagnostic",
                 "parameter count-guard decoded count differs from the native diagnostic")
        return parsed
    lines = [line.split(": ", 1)[-1] for line in str(diagnostic or "").splitlines()]
    _require(lines == ["interpreter nested type count exceeds native limit"] and
             result.get("countGuardDecodedCountAvailable") is False and
             result.get("countGuardDecodedCount") == -1 and
             result.get("countGuardCountSource") == "independently-bound-fixture-byte-oracle",
             "nested count-guard attribution is not exact or fabricates a native decoded count")
    return None


def _verify_launch_outcome(launch, expected_startup_rejection=False):
    if expected_startup_rejection:
        _require(launch.get("exitCode") == 1 and launch.get("timedOut") is False and
                 launch.get("launcherInitiatedTermination") is False and
                 launch.get("processFailed") is True and launch.get("signalTerminated") is False and
                 launch.get("crashed") is False and launch.get("expectedStartupRejection") is True and
                 launch.get("launchSucceeded") is True and launch.get("passed") is True and
                 launch.get("earlyReceiptChecks", {}).get("passed") is True and
                 launch.get("observationErrors") == [] and launch.get("error") in (None, ""),
                 "expected startup rejection did not exit with complete authenticated observations")
    else:
        _require(launch.get("exitCode") == 0 and launch.get("timedOut") is False and
                 launch.get("launcherInitiatedTermination") is False and
                 launch.get("processFailed") is False and launch.get("signalTerminated") is False and
                 launch.get("crashed") is False and launch.get("launchSucceeded") is True and
                 launch.get("passed") is True and launch.get("observationErrors") == [] and
                 launch.get("error") in (None, ""),
                 "diagnostic launch did not exit cleanly with complete observations")
    before, after = launch.get("inputHashesBefore"), launch.get("inputHashesAfter")
    _require(isinstance(before, dict) and before and before == after and
             launch.get("inputsUnchanged") is True,
             "diagnostic launch inputs were unavailable or changed")


def verify_result_document(result: dict, request: dict, *, build: dict | None = None,
                           launch: dict | None = None, fixture_case: dict | None = None,
                           shape: dict | None = None, audit_observation: dict | None = None) -> dict:
    """Evaluate an already loaded cell; exposed for focused synthetic tests."""
    expected_count, *rest = _expected(request)
    expected_outcome = rest[-1]
    if launch is not None:
        _verify_launch_outcome(launch)
        for key, value in (("family", request["family"]), ("caseId", request["caseId"]),
                           ("path", request["flavor"]), ("cppConfiguration", request["cppConfiguration"]),
                           ("processId", launch.get("processId"))):
            if key == "processId":
                continue
            _require(launch.get(key) == value, "launch receipt requested cell differs: " + key)
        _require(launch.get("featureEnabled") is request["featureEnabled"],
                 "launch receipt feature state differs")
    if build is not None:
        _require(build.get("cppConfiguration") == request["cppConfiguration"] and
                 build.get("featureEnabled") is request["featureEnabled"],
                 "authenticated build receipt does not match requested cell")
    fresh_audit = None
    artifact = fixture_case[request["flavor"]] if fixture_case is not None else None
    if artifact is not None and shape is not None:
        _verify_shape(shape, request, artifact)
        if audit_observation is not None:
            fresh_audit = _verify_audit_observation(
                audit_observation, shape, request, fixture_case)
    _require(result.get("schemaVersion") == RESULT_EVIDENCE_SCHEMA_VERSION and
             result.get("kind") == "H1CountDiagnosticResult",
             "diagnostic result header differs")
    _require(result.get("family") == request["family"] and result.get("caseId") == request["caseId"] and
             result.get("path") == request["flavor"] and result.get("expectedCount") == expected_count and
             result.get("expectedOutcome") == expected_outcome,
             "diagnostic result cell or expected count differs")
    if build is not None:
        _require(result.get("expectedCppConfiguration") == build.get("cppConfiguration") and
                 result.get("buildDeclaredCppConfiguration") == build.get("cppConfiguration") and
                 result.get("actualCppConfiguration") in (None, "") and
                 result.get("actualCppConfigurationAvailable") is False and
                 result.get("externalBuildReceiptBindingRequired") is True and
                 result.get("expectedFeatureEnabled") is build.get("featureEnabled"),
                 "diagnostic result build expectations differ")
        _require(result.get("expectedBaselineBuildId") == build.get("baselineBuildId") and
                 result.get("expectedRuntimeAbiHash") == build.get("runtimeAbiHash"),
                 "diagnostic result baseline/ABI differs")
    if launch is not None:
        _require(result.get("buildGuid") == launch.get("buildGuid") and
                 result.get("processId") == launch.get("processId"),
                 "diagnostic result PID/build GUID differs from launch receipt")
    raw_result = result.get("result")
    accepted = expected_outcome == "Accepted"
    if raw_result != "Passed":
        failure_class = str(result.get("failureClass") or "Unavailable")
        if failure_class in ("ProbeFailure", "NoCoverage", "Unavailable") or "badimage" in _text_fields(result):
            raise NoCoverage("diagnostic result did not establish the requested cell: " + failure_class)
        raise VerificationError("diagnostic result is not Passed: " + failure_class)
    _require(result.get("failureClass") == "None" and
             result.get("externalFixtureByteAuditBindingRequired") is True,
             "Passed diagnostic disposition or external fixture binding differs")
    if accepted:
        _require(result.get("operationSucceeded") is True and
                 result.get("observedControlledRejection") is False,
                 "accepted cell claims Passed without a successful operation")
        actual_count = result.get("observedCount")
    else:
        _require(result.get("observedControlledRejection") is True and
                 result.get("operationSucceeded") is False,
                 "rejected cell lacks controlled count-guard evidence")
        parsed_count = _verify_count_guard(result, request, expected_count)
        actual_count = parsed_count if parsed_count is not None else (
            shape.get("nestedClassTableCount") if isinstance(shape, dict) else None)
        _require(actual_count == expected_count,
                 "controlled rejection is not bound to an independently observed count")
    expected_disposition = ("CommittedAndPublished" if request["flavor"] == "shadow" else
                            "OrdinaryAssemblyLoadOnly") if accepted else (
                            "ValidationFailedNoCommitNoAbort" if request["flavor"] == "shadow" else
                            "OrdinaryRejectedNoCommitNoAbort")
    _require(result.get("disposition") == expected_disposition,
             "diagnostic disposition differs from the actual operation outcome")
    _verify_publication(result, request, accepted, artifact)
    _snapshot_checks(result, request, accepted)
    if accepted:
        _verify_reflection(result, request, expected_count, shape)
    return {"status": "Passed", "expectedOutcome": expected_outcome,
            "actualCount": actual_count, "rawResult": raw_result,
            "reflectionVerified": accepted, "publicationVerified": True,
            "ledgerVerified": True, "auditObservationVerified": fresh_audit is not None}


def _validate_build(build, launch):
    _require(build.get("schemaVersion") == 1 and build.get("kind") == "H1CountDiagnosticPlayerBuild" and
             build.get("diagnosticOnly") is True, "diagnostic build receipt header differs")
    _require(build.get("cppConfiguration") in ("Debug", "Release") and type(build.get("featureEnabled")) is bool,
             "diagnostic build receipt C++/feature fields are invalid")
    _require(build.get("target") == "StandaloneOSX" and build.get("architecture") == "arm64" and
             isinstance(build.get("nativeArguments"), str) and
             ("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + ("1" if build["featureEnabled"] else "0")) in build["nativeArguments"] and
             "-DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1" in build["nativeArguments"] and
             isinstance(build.get("extraScriptingDefines"), list) and
             "ASSEMBLY_SHADOW_H1_COUNT_DIAGNOSTICS" in build["extraScriptingDefines"] and
             "ASSEMBLY_SHADOW_R01B_DIAGNOSTICS" in build["extraScriptingDefines"],
             "diagnostic build target or explicit diagnostic flags are missing")
    for key in ("inputSnapshotHash", "sourcePinFile", "sourcePinSha256", "sourcePinsJson"):
        _require(isinstance(build.get(key), str) and build[key], "build receipt field missing: " + key)
    for key in ("buildGuid", "playerExecutable", "nativeLibraryPath", "nativeMetadataPath"):
        _require(isinstance(build.get(key), str) and build[key], "build receipt field missing: " + key)
    try:
        uuid.UUID(build["buildGuid"])
    except ValueError as error:
        raise VerificationError("build receipt GUID is invalid") from error
    for path_key, hash_key in (("playerExecutable", "playerExecutableSha256"),
                               ("nativeLibraryPath", "nativeLibrarySha256"),
                               ("nativeMetadataPath", "nativeMetadataSha256")):
        path = _canonical_file(build[path_key], path_key)
        _require(_sha256(path) == build.get(hash_key), "current " + path_key + " bytes differ from build receipt")
    source_pin = _canonical_file(build["sourcePinFile"], "source pin")
    _require(_sha256(source_pin) == build.get("sourcePinSha256"),
             "current source pin bytes differ from build receipt")
    project_root = Path(launch.get("projectRoot", ""))
    _require(project_root.is_absolute() and project_root == project_root.resolve() and project_root.is_dir() and
             not project_root.is_symlink(), "launch project root is not canonical")
    for parent in project_root.parents:
        _require(not parent.is_symlink() and parent == parent.resolve(),
                 "launch project root has a symlinked or noncanonical parent")
    # Re-read the complete immutable build evidence, including all native inputs.
    # Earlier Passed reports and before/after maps do not establish current bytes.
    spec = importlib.util.spec_from_file_location("h1_count_launcher_verification", HERE / "run-h1-count-players.py")
    _require(spec is not None and spec.loader is not None, "count launcher validator unavailable")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    validated_build, _, _ = validator.validate_build_receipt(
        _canonical_file(launch.get("buildReceiptPath"), "build receipt"), project_root,
        launch.get("family"), launch.get("path"))
    _require(validated_build == build, "build receipt changed during verification")
    _hash_map(launch.get("inputHashesBefore"), "launcher input snapshot")
    _require(launch.get("inputHashesBefore") == launch.get("inputHashesAfter") and
             launch.get("inputsUnchanged") is True, "launcher input snapshot changed during run")


def _write_new(path: Path, report: dict):
    _require(path.is_absolute() and path == path.resolve() and not path.exists() and
             path.parent.is_dir() and not path.parent.is_symlink() and path.parent == path.parent.resolve(),
             "output must be a new canonical JSON path")
    for parent in path.parent.parents:
        _require(not parent.is_symlink() and parent == parent.resolve(),
                 "output parent has a symlinked or noncanonical ancestor")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")


def verify_evidence(launch_path: Path, request: dict) -> dict:
    """Authenticate and evaluate one cell without writing a verification report."""
    report = {"schemaVersion": RESULT_EVIDENCE_SCHEMA_VERSION,
              "kind": "H1CountResultVerification",
              "requested": dict(request), "result": "Failed"}
    result_document = None
    launch_document = None
    try:
        launch, launch_bytes = read_json(launch_path, "launch receipt")
        launch_document = launch
        report["inputs"] = {"launchReceipt": {"path": str(launch_path),
                                               "sha256": hashlib.sha256(launch_bytes).hexdigest()}}
        _require(launch.get("diagnosticOnly") is True and isinstance(launch.get("processId"), int) and
                 launch.get("processId") > 0, "launch receipt is not an authenticated diagnostic process")
        expected_flavor, feature = _path_parts(request["pathName"])
        request = dict(request, flavor=expected_flavor, featureEnabled=feature)
        report["requested"] = dict(request)
        expected_startup_rejection = expected_flavor == "shadow" and _expected(request)[-1] == "ControlledRejected"
        _verify_launch_outcome(launch, expected_startup_rejection)
        _require(launch.get("family") == request["family"] and launch.get("caseId") == request["caseId"] and
                 launch.get("path") == expected_flavor and launch.get("cppConfiguration") == request["cppConfiguration"] and
                 launch.get("featureEnabled") is feature and
                 launch.get("mode") == expected_flavor.capitalize() + ("On" if feature else "Off"),
                 "launch receipt requested cell differs")
        build_path = _canonical_file(launch.get("buildReceiptPath"), "build receipt")
        build, build_bytes = read_json(build_path, "build receipt")
        _require(hashlib.sha256(build_bytes).hexdigest() == launch.get("buildReceiptSha256"),
                 "build receipt hash differs from launch receipt")
        _validate_build(build, launch)
        manifest_path = _canonical_file(launch.get("fixtureManifestPath"), "fixture manifest")
        manifest, manifest_bytes = read_json(manifest_path, "fixture manifest")
        _require(hashlib.sha256(manifest_bytes).hexdigest() == launch.get("fixtureManifestSha256"),
                 "fixture manifest hash differs from launch receipt")
        audit_path = _canonical_file(launch.get("fixtureAuditPath"), "fixture audit")
        audit, audit_bytes = read_json(audit_path, "fixture audit")
        _require(hashlib.sha256(audit_bytes).hexdigest() == launch.get("fixtureAuditSha256"),
                 "fixture audit hash differs from launch receipt")
        _require(manifest.get("family") == request["family"] and manifest.get("caseSet") == "all" and
                 manifest.get("schemaVersion") == 1, "fixture manifest contract differs")
        cases = [case for case in manifest.get("cases", []) if case.get("caseId") == request["caseId"]]
        _require(len(cases) == 1, "requested fixture case is absent or duplicated")
        case = cases[0]
        canonical = _expected({"family": request["family"], "caseId": request["caseId"]})
        _require(case.get("family") == request["family"] and case.get("count") == canonical[0] and
                 case.get("expected") == canonical[-1], "fixture case differs from independent canonical table")
        expected_audit_kind = ("H1CountFixtureShapeAudit" if request["family"] == "parameters" else
                               "H1NestedFixtureShapeAudit")
        _require(audit.get("schemaVersion") == 1 and audit.get("kind") == expected_audit_kind and
                 audit.get("result") == "Passed" and
                 audit.get("family") == request["family"] and audit.get("caseSet") == "all" and
                 request["caseId"] in audit.get("requestedCaseIds", []) and
                 request["caseId"] in audit.get("executedCaseIds", []),
                 "fixture audit does not cover the requested canonical case")
        binding = audit.get("sourceBinding")
        _require(isinstance(binding, dict) and binding.get("manifestPath") == str(manifest_path) and
                 binding.get("manifestSha256") == hashlib.sha256(manifest_bytes).hexdigest(),
                 "fixture audit source binding differs from current manifest")
        required_sources = [("coreAuditPath", "coreAuditSha256"),
                            ("manifestToolPath", "manifestToolSha256")]
        if request["family"] == "nested":
            required_sources.append(("sharedManifestPath", "sharedManifestSha256"))
        for path_key, hash_key in required_sources:
            _require(path_key in binding and hash_key in binding,
                     "fixture audit source binding is incomplete: " + path_key)
            source = _canonical_file(binding[path_key], "fixture audit source")
            _require(_sha256(source) == binding.get(hash_key),
                     "fixture audit source hash differs: " + str(source))
        audit_cases = [item for item in audit.get("cases", [])
                       if isinstance(item, dict) and item.get("caseId") == request["caseId"]]
        _require(len(audit_cases) == 1 and isinstance(audit_cases[0].get("observed"), dict),
                 "fixture audit observation is missing or duplicated")
        artifact = case[expected_flavor]
        audited_artifact = audit_cases[0]["observed"].get(expected_flavor)
        _require(isinstance(audited_artifact, dict),
                 "fixture audit selected artifact observation is missing")
        fixture = _canonical_file(artifact.get("path"), "fixture DLL")
        fixture_sha = _sha256(fixture)
        _require(fixture_sha == artifact.get("sha256") and fixture_sha == launch.get("fixtureDllSha256"),
                 "current fixture bytes differ from authenticated manifest/launch receipt")
        sys.path.insert(0, str(HERE))
        from h1_count_fixture_audit import inspect_file
        shape = inspect_file(fixture)
        _verify_shape(shape, request, artifact)
        _verify_audit_observation(audited_artifact, shape, request, case)
        build_guid = launch.get("buildGuid") or build.get("buildGuid")
        _require(build_guid == build.get("buildGuid") and launch.get("playerExecutableSha256") == build.get("playerExecutableSha256"),
                 "launch receipt is not bound to the authenticated build")
        if expected_flavor == "shadow":
            early_path = _canonical_file(launch.get("earlyResultPath"), "early startup receipt")
            early, early_bytes = read_json(early_path, "early startup receipt")
            _require(hashlib.sha256(early_bytes).hexdigest() == launch.get("earlyResultSha256"),
                     "early startup receipt hash differs from launch receipt")
            early_request = dict(request, assemblyName=artifact.get("name"),
                                 assemblyFullName=artifact.get("fullName"), assemblyMvid=artifact.get("mvid"))
            early_check = verify_early_receipt_document(
                early, early_bytes, early_request, build=build, fixture=fixture,
                fixture_sha256=fixture_sha, expected_result_path=early_path)
            report["earlyStartup"] = {"result": early.get("result"),
                                      "receiptSha256": early_check["receiptSha256"],
                                      "verified": True}
        else:
            _require(launch.get("earlyResultSha256") in (None, "") and
                     not Path(launch.get("earlyResultPath", "")).exists(),
                     "ordinary launch unexpectedly produced an early startup receipt")
        if expected_startup_rejection:
            result_claim_path = launch.get("resultPath")
            _require(isinstance(result_claim_path, str) and result_claim_path and not Path(result_claim_path).exists(),
                     "rejected shadow startup unexpectedly produced a scene result")
            report.update({"result": "Passed", "status": "Passed", "semantic": {
                "status": "Passed", "expectedOutcome": "ControlledRejected",
                "actualCount": _expected(request)[0], "rawResult": "ExpectedValidationRejection",
                "reflectionVerified": False, "publicationVerified": True, "ledgerVerified": True,
                "auditObservationVerified": True},
                "executed": {"processId": launch.get("processId"), "buildGuid": build_guid,
                             "family": request["family"], "caseId": request["caseId"], "path": "shadow",
                             "result": "ExpectedValidationRejection",
                             "expectedOutcome": "ControlledRejected",
                             "earlyResultPath": str(early_path), "expectedCount": _expected(request)[0]}})
            result_document = None
            return report
        result_path = _canonical_file(launch.get("resultPath"), "diagnostic result")
        result, result_bytes = read_json(result_path, "diagnostic result")
        result_document = result
        _require(hashlib.sha256(result_bytes).hexdigest() == launch.get("resultSha256"),
                 "diagnostic result hash differs from launch receipt")
        _require(result.get("fixturePath") == str(fixture) and
                 result.get("fixtureSha256Expected") == fixture_sha and
                 result.get("fixtureSize") == fixture.stat().st_size and
                 result.get("inputHashBefore") == fixture_sha and
                 result.get("inputHashAfter") == fixture_sha and
                 result.get("externalFixtureByteAuditBindingRequired") is True,
                 "diagnostic result is not bound to the independently audited fixture bytes")
        request["targetType"] = artifact.get("targetType")
        semantic = verify_result_document(result, request, build=build, launch=launch,
                                          fixture_case=case, shape=shape,
                                          audit_observation=audited_artifact)
        report.update({"result": "Passed", "status": "Passed", "semantic": semantic,
                       "executed": {"processId": launch.get("processId"), "buildGuid": build_guid,
                                    "resultPath": str(result_path), "fixtureSha256": fixture_sha,
                                    "expectedCount": _expected(request)[0]}})
    except NoCoverage as error:
        report.update({"result": "NoCoverage", "status": "NoCoverage",
                       "failure": {"class": "NoCoverage", "message": str(error)}})
    except Exception as error:
        report.update({"result": "Failed", "status": "Failed",
                       "failure": {"class": type(error).__name__, "message": str(error)}})
    if launch_document is not None:
        report.setdefault("executed", {}).update({
            "caseId": launch_document.get("caseId"), "family": launch_document.get("family"),
            "path": launch_document.get("path"), "processId": launch_document.get("processId"),
            "buildGuid": launch_document.get("buildGuid")})
    if result_document is not None:
        report.setdefault("executed", {}).update({
            "result": result_document.get("result"), "failureClass": result_document.get("failureClass"),
            "errorFull": result_document.get("errorFull"),
            "countGuardDiagnostic": result_document.get("countGuardDiagnostic"),
            "countGuardDiagnosticReason": result_document.get("countGuardDiagnosticReason")})
    return report


def verify_paths(launch_path: Path, request: dict, output: Path) -> int:
    report = verify_evidence(launch_path, request)
    _write_new(output, report)
    return 0 if report["result"] == "Passed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", required=True)
    parser.add_argument("--expected-case", required=True)
    parser.add_argument("--expected-family", choices=("parameters", "nested"), required=True)
    parser.add_argument("--expected-path", choices=("Ordinary-ON", "Ordinary-OFF", "Shadow-ON"), required=True)
    parser.add_argument("--expected-cpp", choices=("Debug", "Release"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    request = {"caseId": args.expected_case, "family": args.expected_family,
               "pathName": args.expected_path, "cppConfiguration": args.expected_cpp}
    return verify_paths(Path(args.launch_receipt), request, Path(args.output))


if __name__ == "__main__":
    raise SystemExit(main())
