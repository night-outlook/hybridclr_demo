"""Contract tests for the independent H1 count result verifier.

Positive cases bind canonical coordination manifests and formal audit rows to
freshly decoded fixture DLLs. Synthetic probe DTOs exercise runtime evidence.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from h1_count_fixture_audit import inspect_file
from h1_count_results import (
    NoCoverage, VerificationError, _expected_nested_shape,
    _expected_parameter_shape, _path_parts, _verify_audit_observation,
    _verify_launch_outcome, _verify_shape, _early_canonical_json,
    verify_early_receipt_document, verify_result_document,
)

COORDINATION = Path(os.environ.get(
    "H1R_COORDINATION_ROOT", "/Users/ah/GitHub/hybridclr/h1r-coordination-20260910"))
ZERO_MVID = "00000000-0000-0000-0000-000000000001"
TARGET_MVID = "00000000-0000-0000-0000-000000000002"
BASELINE_MVID = "00000000-0000-0000-0000-000000000003"
WITNESS_MVID = "00000000-0000-0000-0000-000000000004"
WITNESS_PATH = str((Path(__file__).resolve().parents[3] /
                    "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes").resolve())


def _load_contract(family, case_id, flavor):
    fixture_dir, audit_name = (("parameter-fixtures-final-generator", "parameter-manifest-audit-1.json")
                               if family == "parameters" else
                               ("nested-fixtures-next", "nested-manifest-audit-1.json"))
    manifest = json.loads((COORDINATION / fixture_dir / "h1-count-fixture-manifest.json").read_text())
    audit = json.loads((COORDINATION / audit_name).read_text())
    case = next(row for row in manifest["cases"] if row["caseId"] == case_id)
    audited = next(row for row in audit["cases"] if row["caseId"] == case_id)["observed"][flavor]
    shape = inspect_file(Path(case[flavor]["path"]))
    request = {"caseId": case_id, "family": family, "flavor": flavor,
               "featureEnabled": True, "cppConfiguration": "Release",
               "targetType": case[flavor]["targetType"],
               "assemblyName": case[flavor]["name"],
               "assemblyFullName": case[flavor]["fullName"],
               "assemblyMvid": case[flavor]["mvid"]}
    return request, case, audited, shape


def _snapshot(feature, **updates):
    value = {"schemaVersion": 1, "kind": "H1CountNativeDiagnostics", "diagnosticOnly": True,
             "featureEnabled": feature, "featureMode": "AssemblyShadowOn" if feature else "AssemblyShadowOff",
             "reservedPages": 0, "mappedPages": 0, "reservationCount": 0,
             "nextImageId": 1, "nextPageSlot": 0, "ordinaryAllocatedCount": 0,
             "shadowAllocatedCount": 0, "reservedImageCount": 0,
             "logicalAssemblies": [], "physicalAssemblies": [], "publishedInterpreterImages": []}
    full_name = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
    aot_witness = _native_aot_identity("AssemblyShadowBaseline.HotUpdate", full_name, "0xwa", "0xwai")
    interpreter_witness = _native_identity("AssemblyShadowBaseline.HotUpdate", WITNESS_MVID,
                                           full_name, "0xw", "0xwi", "Interpreter")
    value["logicalAssemblies"] = [aot_witness]
    value["physicalAssemblies"] = [aot_witness, interpreter_witness]
    value["publishedInterpreterImages"] = [interpreter_witness]
    value.update(updates)
    return value


def _native_key(name, mvid, full_name, assembly_id, image_id, kind):
    return "|".join((name, mvid, full_name, assembly_id, image_id, kind, "1" if kind == "Interpreter" else "0"))


def _native_identity(name, mvid, full_name, assembly_id, image_id, kind):
    return {"name": name, "mvid": mvid, "fullName": full_name,
            "nativeAssemblyId": assembly_id, "nativeImageId": image_id,
            "mvidAvailable": True, "imageKind": kind,
            "imageId": 1 if kind == "Interpreter" else 0, "published": True,
            "identityKey": _native_key(name, mvid, full_name, assembly_id, image_id, kind)}


def _native_aot_identity(name, full_name, assembly_id, image_id):
    key = "|".join((name, "<unavailable>", full_name, assembly_id, image_id, "Aot", "0"))
    return {"name": name, "mvid": "", "fullName": full_name,
            "nativeAssemblyId": assembly_id, "nativeImageId": image_id,
            "mvidAvailable": False, "imageKind": "Aot", "imageId": 0,
            "published": False, "identityKey": key}


def _witness():
    full_name = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
    logical_key = "|".join(("AssemblyShadowBaseline.HotUpdate", "<unavailable>", full_name,
                            "0xwa", "0xwai", "Aot", "0"))
    interpreter_key = _native_key("AssemblyShadowBaseline.HotUpdate", WITNESS_MVID,
                                  full_name, "0xw", "0xwi", "Interpreter")
    return {"available": True, "path": WITNESS_PATH,
            "sha256": "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27",
            "assemblyName": "AssemblyShadowBaseline.HotUpdate",
            "assemblyFullName": "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "observationKind": "NativeAssemblyIdentity",
            "logicalIdentityKeys": [logical_key], "physicalIdentityKeys": [interpreter_key],
            "publishedIdentityKeys": [interpreter_key]}


def _snapshots(feature, flavor, accepted):
    before = _snapshot(feature)
    if flavor == "ordinary":
        before = _snapshot(feature, reservedPages=2, mappedPages=1, reservationCount=1,
                           nextImageId=2, nextPageSlot=2, ordinaryAllocatedCount=1)
        final = _snapshot(feature, reservedPages=4, mappedPages=2, reservationCount=2,
                          nextImageId=3, nextPageSlot=4, ordinaryAllocatedCount=2)
        return [{"phase": "before", "available": True, "snapshot": before},
                {"phase": "after", "available": True, "snapshot": copy.deepcopy(final)},
                {"phase": "final", "available": True, "snapshot": copy.deepcopy(final)}]
    before = _snapshot(feature, reservedPages=2, mappedPages=1, reservationCount=1,
                       nextImageId=2, nextPageSlot=2, ordinaryAllocatedCount=1)
    reserved = _snapshot(feature, reservedPages=5, mappedPages=1, reservationCount=2, nextImageId=3,
                         nextPageSlot=5, ordinaryAllocatedCount=1, reservedImageCount=1)
    staged = dict(reserved, shadowAllocatedCount=1)
    validated = dict(staged, mappedPages=2)
    records = [{"phase": "before", "available": True, "snapshot": before},
               {"phase": "after-configure", "available": True, "snapshot": copy.deepcopy(before)},
               {"phase": "after-begin", "available": True, "snapshot": copy.deepcopy(before)},
               {"phase": "after-reserve", "available": True, "snapshot": reserved},
               {"phase": "after-stage", "available": True, "snapshot": staged},
               {"phase": "after-validate", "available": True,
                "snapshot": copy.deepcopy(validated)}]
    if accepted:
        records.append({"phase": "after-commit", "available": True,
                        "snapshot": copy.deepcopy(validated)})
    records.extend([{"phase": "after", "available": True, "snapshot": copy.deepcopy(validated)},
                    {"phase": "final", "available": True, "snapshot": copy.deepcopy(validated)}])
    return records


def _publication(request, accepted):
    shadow = request["flavor"] == "shadow"
    baseline_full_name = "mscorlib, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
    witness_full_name = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
    witness_aot = "|".join(("AssemblyShadowBaseline.HotUpdate", "<unavailable>", witness_full_name,
                            "0xwa", "0xwai", "Aot", "0"))
    witness_interpreter = _native_key("AssemblyShadowBaseline.HotUpdate", WITNESS_MVID,
                                      witness_full_name, "0xw", "0xwi", "Interpreter")
    before = sorted([_native_key("mscorlib", ZERO_MVID, baseline_full_name, "0xa", "0xb", "Aot"), witness_aot])
    identity = _native_key(request["assemblyName"], request["assemblyMvid"],
                           request["assemblyFullName"], "0xc", "0xd", "Interpreter")
    if shadow and accepted:
        before = sorted(before + [_native_key(request["assemblyName"], BASELINE_MVID,
                                              request["assemblyFullName"], "0xe", "0xf", "Aot")])
    physical_before = sorted(before + [witness_interpreter])
    physical_after = list(before)
    published_before = [witness_interpreter]
    published_after = [witness_interpreter]
    if accepted:
        physical_after = sorted(physical_before + [identity])
        published_after = sorted([witness_interpreter, identity])
    else:
        physical_after = list(physical_before)
    value = {"configureCalled": False, "beginCalled": False, "reserveCalled": False,
             "stageCalled": False, "validateCalled": False, "commitCalled": False,
             "abortCalled": False, "committed": False, "initializerObserved": False,
             "publicAssemblyLoaded": accepted, "publicAssemblyMatchesExpected": accepted,
             "publicAssemblyName": request["assemblyName"] if accepted else None,
             "publicAssemblyFullName": request["assemblyFullName"] if accepted else None,
             "publicAssemblyMvid": request["assemblyMvid"] if accepted else None,
             "publicAssemblyMvidAvailable": accepted,
             "nativeAssemblyId": "0xc" if accepted else None,
             "nativeImageId": "0xd" if accepted else None,
             "nativeAssemblyFullName": request["assemblyFullName"] if accepted else None,
             "imageKind": "Interpreter" if accepted else None,
             "imageId": 2 if accepted else 0,
             "publicIdentityObservationAvailable": not accepted,
             "noPublicFixtureIdentity": not accepted, "publicAssemblyInventoryStable": not accepted,
             "publicAssembliesBefore": before,
             "publicAssembliesAfter": (before if not accepted else
                                       sorted([item for item in before
                                               if item.split("|", 1)[0] != request["assemblyName"]] +
                                              [identity])),
             "physicalAssembliesBefore": physical_before,
             "physicalAssembliesAfter": physical_after,
             "publishedInterpreterImagesBefore": published_before,
             "publishedInterpreterImagesAfter": published_after,
             "executionModeAvailable": False}
    if shadow:
        value.update({"configureCalled": True, "configureCode": "Success",
                      "beginCalled": True, "beginCode": "Success",
                      "reserveCalled": True, "reserveCode": "Success", "reserveProfileVersion": 2,
                      "stageCalled": True, "stageCode": "Success", "validateCalled": True,
                      "validateCode": "Success" if accepted else "ReferenceResolutionFailed",
                      "commitCalled": accepted, "commitCode": "Success" if accepted else None,
                      "committed": accepted, "executionModeAvailable": True,
                      "executionModeCode": "Success",
                      "executionMode": "InterpreterShadow" if accepted else "AotBaseline"})
    return value


def _operations(flavor, accepted):
    if flavor == "ordinary":
        return [{"operation": "ordinary-path-selected", "success": True, "code": "Success"},
                {"operation": "Assembly.Load(byte[])", "success": accepted,
                 "code": "Success" if accepted else "Exception"}]
    rows = [{"operation": "ConfigureCandidates", "success": True, "code": "Success"},
            {"operation": "BeginTransaction", "success": True, "code": "Success"},
            {"operation": "ReserveMetadataBudget", "success": True, "code": "Success"},
            {"operation": "StageAssembly", "success": True, "code": "Success"},
            {"operation": "ValidateTransaction", "success": accepted,
             "code": "Success" if accepted else "ReferenceResolutionFailed"}]
    return rows + ([{"operation": "CommitTransaction", "success": True, "code": "Success"}]
                   if accepted else [])


def _states(accepted):
    rows = [("after-configure", "CandidatesRegistered"), ("after-begin", "Staging"),
            ("after-reserve", "Staging"), ("after-stage", "Staged"),
            ("after-validate", "Validated" if accepted else "Failed")]
    if accepted:
        rows.append(("after-commit", "Committed"))
    return [{"phase": phase, "available": True, "code": "Success", "state": state}
            for phase, state in rows]


def _result(request, accepted, return_row_available=True):
    count = (_expected_parameter_shape(request["caseId"])[0] if request["family"] == "parameters"
             else _expected_nested_shape(request["caseId"])[0])
    disposition = (("CommittedAndPublished" if request["flavor"] == "shadow" else
                    "OrdinaryAssemblyLoadOnly") if accepted else
                   ("ValidationFailedNoCommitNoAbort" if request["flavor"] == "shadow" else
                    "OrdinaryRejectedNoCommitNoAbort"))
    result = {"schemaVersion": 2, "kind": "H1CountDiagnosticResult", "result": "Passed",
              "failureClass": "None", "family": request["family"], "path": request["flavor"],
              "caseId": request["caseId"], "expectedOutcome": "Accepted" if accepted else "ControlledRejected",
              "expectedCount": count, "observedCount": count if accepted else -1,
              "observedCountAvailable": accepted, "operationSucceeded": accepted,
              "observedControlledRejection": not accepted, "disposition": disposition,
              "externalFixtureByteAuditBindingRequired": True, "ledgerVerified": True,
              "admissionFailedNoCoverage": False, "publication": _publication(request, accepted),
              "witness": _witness(),
              "operationSteps": _operations(request["flavor"], accepted),
              "states": _states(accepted) if request["flavor"] == "shadow" else [],
              "snapshots": _snapshots(request["featureEnabled"], request["flavor"], accepted)}
    if accepted and request["family"] == "parameters":
        _, types, rows, instance = _expected_parameter_shape(request["caseId"])
        result["parameter"] = {"available": True, "targetType": request["targetType"],
                               "targetMethod": "System.Int32 Probe()", "count": count,
                               "returnType": "System.Int32", "instance": instance,
                               "parameterTypes": types, "paramRows": rows,
                               "repeatPassed": True, "paramRowsRepeatPassed": True}
        if request["caseId"] == "H1R-P04-return255":
            result["parameter"].update({
                "paramRows": rows if return_row_available else [],
                "returnParameterRowByteOracleRequired": True,
                "returnParameterRowPublicReflectionAvailable": return_row_available,
                "returnParameterRowObservation":
                    ("Public reflection exposed Param sequence 0 with name result."
                     if return_row_available else "Public reflection did not expose Param sequence 0.")})
    elif accepted:
        _, groups, _ = _expected_nested_shape(request["caseId"])
        result["nested"] = {"available": True, "targetType": "AssemblyShadow.H1Nested.Target",
                            "totalCount": count, "repeatPassed": True,
                            "groups": [{**group, "first": group["children"][0] if group["children"] else None,
                                        "last": group["children"][-1] if group["children"] else None,
                                        "repeatPassed": True} for group in groups]}
    else:
        diagnostic = (f"method token:1 parameter count:{count} is too large"
                      if request["family"] == "parameters" else
                      "interpreter nested type count exceeds native limit")
        result.update({"countGuardDiagnostic": diagnostic,
                       "countGuardDiagnosticSource": "shadow-diagnostics-detail" if request["flavor"] == "shadow" else "ordinary-exception",
                       "countGuardExpectedDecodedCount": count, "countGuardDiagnosticAvailable": True,
                       "countGuardDecodedCountAvailable": request["family"] == "parameters",
                       "countGuardDecodedCount": count if request["family"] == "parameters" else -1,
                       "countGuardCountSource": ("native-parameter-guard-diagnostic" if request["family"] == "parameters" else
                                                 "independently-bound-fixture-byte-oracle")})
        if request["flavor"] == "shadow":
            raw = json.dumps({"schemaVersion": 1, "state": "Failed", "lastError": 13,
                              "detail": diagnostic}, separators=(",", ":"))
            result["controlledRejectionErrorFull"] = diagnostic
            result["publication"].update({"failureDiagnosticsAvailable": True,
                                           "failureDiagnosticsCode": "Success",
                                           "failureDiagnosticsJson": raw,
                                           "failureDiagnosticsState": "Failed",
                                           "failureDiagnosticsLastError": 13,
                                           "failureDiagnosticsDetail": diagnostic})
    return result


@unittest.skipUnless(COORDINATION.is_dir(), "canonical H1R coordination directory is unavailable")
class H1CountResultTests(unittest.TestCase):
    def test_authenticated_early_rejection_requires_named_count_and_no_publication(self):
        request = {"family": "parameters", "caseId": "H1R-P03-a", "pathName": "Shadow-ON",
                   "featureEnabled": True}
        before = _snapshot(True, reservedPages=2, mappedPages=1, nextPageSlot=2,
                           reservationCount=1, nextImageId=2, ordinaryAllocatedCount=1)
        reserved = _snapshot(True, reservedPages=3, mappedPages=1, nextPageSlot=3, reservationCount=2,
                             nextImageId=3, ordinaryAllocatedCount=1, reservedImageCount=1)
        staged = dict(reserved, shadowAllocatedCount=1)
        detail = "method token:1 parameter count:65536 is too large"
        phases = ["before", "after-configure", "after-begin", "after-reserve", "after-stage",
                  "after-validate", "after", "final"]
        native = [before, before, before, reserved, staged, staged, staged, staged]
        diagnostics = []
        for phase in phases:
            diagnostics.append({"schemaVersion": 1, "enabled": True,
                                "state": "Failed" if phase in ("after-validate", "after", "final") else "Staging",
                                "lastError": 13 if phase in ("after-validate", "after", "final") else 0,
                                "expected": 1, "staged": 1,
                                "closureLoadOrder": ["AssemblyShadow.H1Count.Target"],
                                "assemblies": [{"name": "AssemblyShadow.H1Count.Target", "skeletonBuilt": True,
                                                "runtimeMetadataInitialized": False, "published": False}],
                                "detail": detail if phase in ("after-validate", "after", "final") else ""})
        receipt = {"schemaVersion": 2, "kind": "H1CountEarlyStartupResult", "diagnosticOnly": True,
                   "result": "ExpectedValidationRejection", "error": "",
                   "disposition": "ValidationFailedNoCommitNoAbort", "callbackReturnCode": 1,
                   "processId": 1, "managedThreadId": 1, "resultPath": "/tmp/early.json",
                   "family": "parameters", "path": "shadow", "caseId": "H1R-P03-a",
                   "baselineBuildId": "", "runtimeAbiHash": "", "expectedOutcome": "ControlledRejected",
                   "expectedCount": 65536, "fixturePath": "", "fixtureSha256Expected": "", "fixtureSize": 0,
                   "inputHashBefore": "", "inputHashAfter": "", "startUtc": "", "endUtc": "",
                   "elapsedTicks": 0, "stopwatchFrequency": 1, "committed": False, "baselineAlreadyUsed": False,
                   "operations": [{"phase": phase, "code": code, "intCode": 13 if code != "Success" else 0}
                                  for phase, code in [("configure", "Success"), ("begin", "Success"),
                                                      ("reserve", "Success"), ("stage", "Success"),
                                                      ("validate", "ReferenceResolutionFailed")]],
                   "snapshots": [{"phase": phase, "nativeCode": "Success",
                                  "nativeJson": json.dumps(n, separators=(",", ":")),
                                  "diagnosticsCode": "Success",
                                  "diagnosticsJson": json.dumps(d, separators=(",", ":"))}
                                 for phase, n, d in zip(phases, native, diagnostics)],
                   "receiptSha256": ""}
        receipt["witness"] = _witness()
        receipt["receiptSha256"] = hashlib.sha256(_early_canonical_json(receipt, "").encode()).hexdigest()
        encoded = _early_canonical_json(receipt, receipt["receiptSha256"]).encode()
        self.assertTrue(verify_early_receipt_document(receipt, encoded, request)["passed"])
        receipt["operations"][4]["intCode"] = 12
        receipt["receiptSha256"] = hashlib.sha256(_early_canonical_json(receipt, "").encode()).hexdigest()
        encoded = _early_canonical_json(receipt, receipt["receiptSha256"]).encode()
        with self.assertRaises(VerificationError):
            verify_early_receipt_document(receipt, encoded, request)

        receipt["witness"].pop("logicalIdentityKeys")
        receipt["receiptSha256"] = hashlib.sha256(_early_canonical_json(receipt, "").encode()).hexdigest()
        encoded = _early_canonical_json(receipt, receipt["receiptSha256"]).encode()
        with self.assertRaises(VerificationError):
            verify_early_receipt_document(receipt, encoded, request)
        receipt["operations"][4]["intCode"] = 13
        receipt["snapshots"][5]["diagnosticsJson"] = receipt["snapshots"][5]["diagnosticsJson"].replace("65536", "65537")
        receipt["receiptSha256"] = hashlib.sha256(_early_canonical_json(receipt, "").encode()).hexdigest()
        encoded = _early_canonical_json(receipt, receipt["receiptSha256"]).encode()
        with self.assertRaises(VerificationError):
            verify_early_receipt_document(receipt, encoded, request)

    def verify_contract(self, family, case_id, flavor, accepted, **options):
        request, case, audited, shape = _load_contract(family, case_id, flavor)
        result = _result(request, accepted, **options)
        semantic = verify_result_document(result, request, fixture_case=case, shape=shape,
                                          audit_observation=audited)
        self.assertEqual("Passed", semantic["status"])
        self.assertTrue(semantic["auditObservationVerified"])
        return request, case, audited, shape, result

    def test_positive_real_parameter_audit_and_ordinary_probe(self):
        self.verify_contract("parameters", "H1R-P01-a", "ordinary", True)

    def test_positive_real_zero_nested_audit_and_probe(self):
        self.verify_contract("nested", "H1R-N01-a", "ordinary", True)

    def test_positive_shadow_state_and_ledger_contract(self):
        self.verify_contract("parameters", "H1R-P01-a", "shadow", True)

    def test_shadow_validation_may_extend_the_single_page_reservation(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P01-a", "shadow", True)
        for row in result["snapshots"]:
            if row["phase"] in ("after-validate", "after-commit", "after", "final"):
                row["snapshot"]["reservedPages"] = 9
                row["snapshot"]["nextPageSlot"] = 9
                row["snapshot"]["mappedPages"] = 9
        semantic = verify_result_document(result, request, fixture_case=case, shape=shape,
                                          audit_observation=audited)
        self.assertEqual("Passed", semantic["status"])

        result["snapshots"][-1]["snapshot"]["nextPageSlot"] = 10
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_positive_controlled_parameter_rejection(self):
        self.verify_contract("parameters", "H1R-P02-a", "shadow", False)

    def test_positive_return_row_uses_authenticated_byte_oracle(self):
        self.verify_contract("parameters", "H1R-P04-return255", "ordinary", True,
                             return_row_available=False)

    def test_path_flavor_and_feature_are_independent(self):
        self.assertEqual(("ordinary", True), _path_parts("Ordinary-ON"))
        self.assertEqual(("ordinary", False), _path_parts("Ordinary-OFF"))
        self.assertEqual(("shadow", True), _path_parts("Shadow-ON"))

    def test_stored_audit_row_must_equal_fresh_decoding(self):
        request, case, audited, shape = _load_contract("parameters", "H1R-P01-a", "ordinary")
        with self.assertRaises(VerificationError):
            _verify_audit_observation(dict(audited, signatureCount=1), shape, request, case)

    def test_zero_nested_requires_parent_typedef(self):
        request, case, _, shape = _load_contract("nested", "H1R-N01-a", "ordinary")
        broken = copy.deepcopy(shape)
        next(row for row in broken["types"] if row["fullName"] == request["targetType"])["parentRid"] = 1
        with self.assertRaises(VerificationError):
            _verify_shape(broken, request, case["ordinary"])

    def _mutated_runtime_fails(self, mutator):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P02-a", "shadow", False)
        mutator(result)
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_rejected_operation_must_not_claim_load_success(self):
        self._mutated_runtime_fails(lambda result: result.__setitem__("operationSucceeded", True))

    def test_parameter_guard_count_is_parsed(self):
        def mutate(result):
            wrong = "method token:1 parameter count:255 is too large"
            result["countGuardDiagnostic"] = wrong
            result["controlledRejectionErrorFull"] = wrong
            raw = json.loads(result["publication"]["failureDiagnosticsJson"])
            raw["detail"] = wrong
            result["publication"]["failureDiagnosticsJson"] = json.dumps(raw)
            result["publication"]["failureDiagnosticsDetail"] = wrong
        self._mutated_runtime_fails(mutate)

    def test_exact_state_is_required(self):
        self._mutated_runtime_fails(lambda result: result["states"][3].__setitem__("state", "Validated"))

    def test_ledger_extra_allocation_is_rejected(self):
        def mutate(result):
            for row in result["snapshots"]:
                if row["phase"] in ("after", "final"):
                    row["snapshot"]["nextImageId"] = 4
        self._mutated_runtime_fails(mutate)

    def test_rejected_public_inventory_must_be_identical(self):
        self._mutated_runtime_fails(lambda result: result["publication"]["publicAssembliesAfter"].append(
            "Injected|" + TARGET_MVID))

    def test_rejected_physical_and_published_inventories_must_be_identical(self):
        for field in ("physicalAssembliesAfter", "publishedInterpreterImagesAfter"):
                with self.subTest(field=field):
                    self._mutated_runtime_fails(lambda result, field=field:
                        result["publication"][field].append("Injected|identity"))

    def test_missing_witness_is_rejected(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P02-a", "shadow", False)
        result.pop("witness")
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_tampered_witness_observation_or_hash_is_rejected(self):
        for field, value in (("observationKind", "ManagedReflectionMarker"), ("sha256", "0" * 64)):
            with self.subTest(field=field):
                request, case, audited, shape, result = self.verify_contract(
                    "parameters", "H1R-P02-a", "shadow", False)
                result["witness"][field] = value
                with self.assertRaises(VerificationError):
                    verify_result_document(result, request, fixture_case=case, shape=shape,
                                           audit_observation=audited)

    def test_changed_witness_native_identity_is_rejected(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P02-a", "shadow", False)
        result["snapshots"][-1]["snapshot"]["logicalAssemblies"][0]["identityKey"] = "changed"
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_physical_witness_identity_row_must_be_published_interpreter_with_mvid(self):
        for field, value in (("imageKind", "Aot"), ("published", False),
                             ("mvidAvailable", False), ("mvid", ""),
                             ("nativeAssemblyId", "0"), ("nativeImageId", "0x0"),
                             ("imageId", 2)):
            with self.subTest(field=field):
                request, case, audited, shape, result = self.verify_contract(
                    "parameters", "H1R-P02-a", "shadow", False)
                for row in result["snapshots"]:
                    row["snapshot"]["physicalAssemblies"][1][field] = value
                with self.assertRaises(VerificationError):
                    verify_result_document(result, request, fixture_case=case, shape=shape,
                                           audit_observation=audited)

    def test_logical_witness_identity_row_must_be_unpublished_aot_without_mvid(self):
        for field, value in (("imageKind", "Interpreter"), ("published", True),
                             ("mvidAvailable", True), ("mvid", WITNESS_MVID),
                             ("nativeAssemblyId", "0"), ("nativeImageId", "0x0"),
                             ("imageId", 1)):
            with self.subTest(field=field):
                request, case, audited, shape, result = self.verify_contract(
                    "parameters", "H1R-P02-a", "shadow", False)
                for row in result["snapshots"]:
                    row["snapshot"]["logicalAssemblies"][0][field] = value
                with self.assertRaises(VerificationError):
                    verify_result_document(result, request, fixture_case=case, shape=shape,
                                           audit_observation=audited)

    def test_witness_identity_arrays_are_mandatory(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P02-a", "shadow", False)
        result["witness"].pop("physicalIdentityKeys")
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_shadow_replacement_must_preserve_unrelated_identity(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P01-a", "shadow", True)
        result["publication"]["publicAssembliesAfter"] = [
            value for value in result["publication"]["publicAssembliesAfter"]
            if not value.startswith("mscorlib|")]
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_failure_diagnostics_raw_json_is_authoritative(self):
        def mutate(result):
            raw = json.loads(result["publication"]["failureDiagnosticsJson"])
            raw["lastError"] = 9
            result["publication"]["failureDiagnosticsJson"] = json.dumps(raw)
        self._mutated_runtime_fails(mutate)

    def test_launch_status_and_inputs_are_required(self):
        launch = {"exitCode": 0, "timedOut": False, "launcherInitiatedTermination": False,
                  "processFailed": False, "signalTerminated": False, "crashed": False,
                  "launchSucceeded": True, "passed": True, "observationErrors": [], "error": "",
                  "inputHashesBefore": {"/input": "a" * 64},
                  "inputHashesAfter": {"/input": "a" * 64}, "inputsUnchanged": True}
        _verify_launch_outcome(launch)
        for field, value in {"exitCode": 1, "timedOut": True, "crashed": True,
                             "observationErrors": ["failed"], "inputsUnchanged": False}.items():
            with self.subTest(field=field), self.assertRaises(VerificationError):
                _verify_launch_outcome(dict(launch, **{field: value}))

    def test_return_row_capability_cannot_contradict_rows(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P04-return255", "ordinary", True,
            return_row_available=False)
        result["parameter"]["paramRows"] = [{"sequence": 0, "name": "result", "isReturn": True}]
        with self.assertRaises(VerificationError):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)

    def test_generic_bad_image_is_no_coverage(self):
        request, case, audited, shape, result = self.verify_contract(
            "parameters", "H1R-P01-a", "ordinary", True)
        result.update({"result": "Failed", "failureClass": "ProbeFailure",
                       "errorFull": "BadImage: unrelated format error"})
        with self.assertRaises(NoCoverage):
            verify_result_document(result, request, fixture_case=case, shape=shape,
                                   audit_observation=audited)


if __name__ == "__main__":
    unittest.main()
