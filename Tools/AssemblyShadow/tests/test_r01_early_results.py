"""Full early wire-schema fixtures, not Player acceptance evidence.

Native diagnostic/recovery field layout and event shape were projected from
R01-early-current-pair-v1/Results/r01-R01-PreConfigure-Object.json; intermediate
state transitions follow AssemblyShadow.cpp. PE identities use real synthetic
ECMA-335 tables. This emitter does not call the early gate's expected helpers.
"""
import base64
import zlib
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_early_capsule as capsule
import r01_early_results as gate
import r01_results as budget
import m04_results as m04
from shadow_tools import VerificationError
from test_m04_results import make_pe

ORDER = ["AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", gate.INTERNAL,
         "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"]
# Retained P01 native receipt projection: registry order differs from first-use
# order. Neither provider is in the P01 replacement closure (Internal only).
P01_BASELINE_USES = [
    dict(name="AssemblyA.Contracts", kind="AssemblyReflection",
         detail="Image::ClassFromName.input FirstUseSequence=2", type="",
         thread=18199233411598851025, timestamp=1172860484094166),
    dict(name="AssemblyA.Implementation.Extensibility", kind="AssemblyReflection",
         detail="Image::ClassFromName.input FirstUseSequence=1", type="",
         thread=18199233411598851025, timestamp=1172860483755750),
]

GUARDS = {"Type", "Object", "Cctor", "NativeScript"}
FAILURES = {"MetadataFailure", "InitializerFailure"}
POSITIVES = {"Control", "OrdinaryFirst", "OrdinaryAfterReserve"}

# Exact pinned M00 payload, compressed for self-contained offline tests.
FIXED_ORDINARY = zlib.decompress(base64.b64decode(
    "eJztV11sHFcVPnf2x2s7Nd7YDQmEdhM34MTt7uyfd1cNxbs7s7Ehrl2vnYbIwpnZuVlPNTuzzMzaWWiqUpQiHopAavuQpwr6UjVI"
    "rUilqmp4QEKqRCIhKgQPgEKERB6KeEICBDHn3pndcVwL9wVVCO76nnvPzz33O+f+zPX8ue9CCADCWLe2AN4Gr8zA3uVZrCMPvjMC"
    "1wZvHnmbnL55ZHlddxJt22raSivRUEzTchMqTdgdM6GbCWmhnmhZGk3ed9/QQ76PRRngNAlB7PhvftrzewuOJoaJCDCETNST/W4S"
    "SaIPbJT3BQ83QNByUILXDcHMZWbK/oK23/DybfS74AccC+0S5HmAfdhc/BzA8kfISb8gvtg2Nob87DY+6dKLLrZnB/24hgLc21yc"
    "T9qO3QAfG2Lkge671w7FM0mbGlbDV533fY1+yK6yE+b1Sa+d5UMi8B5O+gbmnHyUGHcpY2IYvgx8fBz2w937I+h3PzxYemEYhcd+"
    "zpZscgDDvYQBhVEx5StIXxHmik9eivpthLcHLqEyHB2egoETR4XJGMvYiU/ZOKx9Auer1L9YIT5qloONXFJMZsVsusQkETBYOnDy"
    "iWcAnsa2iNNP1F1bN5sOs7iGs7A9ObFSh19HvNRNnFqZk7C9g/x7jK8YlurHiS7Iky8KiUGW57+TLBzwcjaCdcCvbMlifl/wctJv"
    "ia8HWBI81FH4G/mREIVDAqM3yCvCJ+B9gcmvcPllchLpLU7fIs8hHQhtIj1HGC0IjP6Vjz3M5adQzvy+zr17uRnlG+AY575BRiEV"
    "0gjjQhzQNV8XhmHUPYyS46gJwxj2vgqMi/ncd/pclrwPOaQEioj0AXIS6TinfxJmkN7m9GioCosJBuN7MBKq4RxvMQ6eP3gFkRL4"
    "MedehmeELyE3CFcwJ3FgukNIh3Au1i8hHYUy0gOgwP7QBMxxeRKG8QwnYQzOIv00bEIVJvAiqMIUXEaaRbzf5BKCEpZRAiW+Lofh"
    "ziQL/eBxtjLhZ3fuZo0weXAWpuBR4u0nAb2E0QO/d6pyviiLpXSplqsV5Fy5JOcz04VcvpwuTk9XZFkulNKZdDFdns4W07npcrUm"
    "5bPVdKk4XcxKmUIaVkzd7datjt2gp6hJbcWlWtlxaEs1uvOWadUbtt52l7tt6qxtpGFtre4qrt4o27bSncOxTFPXv0Y/n8v+G2W+"
    "ACfnLa1j0Mfg5KKtb+A0c622QVvUZEMsU6KuohvOY4BYq3Ilk8+LcildlsuZTCZdLWarcmk6U8uXcvkCwhYzYimfq2XFXKGQzxXk"
    "dDpTruVzkijVgGOVFFeBmm7QRcVd97ggGs6a1HVcxdQUW4OljunqLVrTqaHNosygcEYxOpS5gl426uuKZm1WFIcaukmTs5a70tYw"
    "DpA13bXsim1tOopqUJYDClWr1cbp7SCpLh55tYOqvqiKX6RALFG102wyD4Fsh+tA4bnnmVuihnKR95xA70fEzFCl6gaucqCtdJHU"
    "u45LW0lmYpm4DLg+1Ngz2qRmGP5QNkngRaOS5XljYUOygcB7WklXmqbl4NZweiIfYH9AndobeoM6fhrwcmR4HFi2XMVgC+l3+er2"
    "wpulRpvaDiyoT9GGi4l1gW07XTFw0/FdCHOOl8MF0+iCbLp2lx+nI/Mg4u8R/Pos4Nd1BRZBwvO9DDLKFoDdBVff/MsfX/0gN/PC"
    "q/rt1dfuPgrhBCGxUAJIBDvxOKeHIgmBjIxEB4T4eHx8AASyPx8vxW58fWzr5iO/fSIUjR/EejgU/UxEiMaEqICnNj6Ol95IjPhf"
    "6QfYlbgsHHjSVtqPW6Z8sUHbbDWX19myE7Qb4Cc/zGis96UpEEjzs5sM9rW/sSx7m2zOvGD15Vu92+TQ+PXfA5lfFPjdB3AD3xg3"
    "BoPbh80xhhXFoOI9pQ7dezvt+LzDUl2qf/+lH/wqcu4r0ku/+Nbxf7xr/ZD5SK04uD4pZT11SndnO2pqvavautYw7KC3ptGWtebw"
    "/ZY6rau2YndTFUpTiu3qF5SG66QyoqiK4qJENyS1mdSUZmrPbdrWVKjPljP5afCBvfhLHxgL/rl/3v+TD/4gbgpP3J56czII5Ge9"
    "x94u5frkdm6tatmSYcwrugktp2HZ1Dsbftk6hm76afrsXnifDramn/70KhvjOqu7D13tD13lQ5MNZ3fU/yWF8GQd9F7R98hZMsRd"
    "5Kywt+PZGYCr296vV4Uc0jNQhzWkMixhbw7P9OPIzyGtea9uuB7+893dXptf8Fv2fd3xLAaJz3wG3wA2+tHxbUfRpwkXwOL6h/io"
    "ZdTiBwYc1Cvgop2FnFfeCO9jDzjE5KKVjvLmLp7uEGYj9n85UFkO4GH+JujZS1gdaHA/7XvmSfCcxbbZnsFqo3VgI+KLJagAT/EX"
    "GMPgclsTsRuYLwVayAPejg7+KHIqyrsYwTrqNPS3iW87hesMHhFFj7Mod/FebaOFwj0msWeAd0AmeRynUdrks1TRuo0+WSRN9Ov6"
    "Mdgc04Iv131MvZjM/wi2HM/bIs5pobSD+XU/lL2duSvyMTtRJPYc9z9dEt7/S7eKHzeQ/5ePo/wL32u2Jg=="
))
assert hashlib.sha256(FIXED_ORDINARY).hexdigest() == capsule.FIXED_IMAGE_SHA


def make_capsule(root, mode="Control"):
    inputs = []
    for index, name in enumerate(ORDER):
        dll = root / (name + ".dll")
        dll.write_bytes(make_pe(name, mvid=uuid.UUID(int=index + 1)))
        pdb = root / (name + ".pdb")
        if index == 0: pdb.write_bytes(b"owned-pdb")
        inputs.append(dict(name=name, dllPath=str(dll), dllLength=dll.stat().st_size,
                           dllSha256=capsule.digest(dll), pdbPath=str(pdb) if index == 0 else "",
                           pdbLength=pdb.stat().st_size if index == 0 else 0,
                           pdbSha256=capsule.digest(pdb) if index == 0 else ""))
    prerequisite = root / "resource-build-receipt.json"
    prerequisite.write_bytes(b"source-bound-resource-receipt")
    ordinary = root / "ordinary.dll"
    ordinary.write_bytes(FIXED_ORDINARY)
    return dict(mode=mode, baselineBuildId="baseline", runtimeAbiHash="a" * 64,
                patchId="R01-P03-InitializerThrow" if mode == "InitializerFailure" else "P03",
                candidates=ORDER, stableAotNames=["assemblyshadowdemo.bootstrap", "mscorlib"], inputs=inputs,
                ordinaryPath=str(ordinary) if mode.startswith("Ordinary") else "",
                ordinarySha256=capsule.digest(ordinary) if mode.startswith("Ordinary") else "",
                prerequisiteFiles=[dict(path=str(prerequisite), length=prerequisite.stat().st_size,
                                        sha256=capsule.digest(prerequisite))])


def emit_receipt(data, capsule_path, result_path, pid=1234):
    mode = data["mode"]
    rows = data["inputs"]
    names = [row["name"] for row in rows]
    sizes = [row["dllLength"] for row in rows]
    derived = []
    if mode == "Oversize":
        sizes[-1] = 64 * 1024 * 1024
        raw = Path(rows[-1]["dllPath"]).read_bytes()
        h = hashlib.sha256(raw)
        zero = bytes(1024 * 1024)
        remaining = sizes[-1] - len(raw)
        while remaining:
            n = min(remaining, len(zero)); h.update(zero[:n]); remaining -= n
        derived.append(dict(name=names[-1], path=rows[-1]["dllPath"], length=sizes[-1],
                            sha256=h.hexdigest(), kind="oversize-dll"))
    byte_inputs = []
    for row in rows:
        for prefix in ("dll", "pdb"):
            if row[prefix + "Path"]:
                byte_inputs.append(dict(name=row["name"], path=row[prefix + "Path"],
                    length=row[prefix + "Length"], sha256=row[prefix + "Sha256"], kind=prefix))
    if data["ordinaryPath"]:
        p = Path(data["ordinaryPath"])
        byte_inputs.append(dict(name=gate.ORDINARY, path=str(p), length=p.stat().st_size,
                                sha256=capsule.digest(p), kind="ordinary"))
    byte_inputs.extend(dict(name="", kind="prerequisite", **row) for row in data["prerequisiteFiles"])
    read_count = len(byte_inputs)
    byte_inputs.extend(derived)
    result = dict(schemaVersion=1, kind="R01EarlyStartupReceipt", mode=mode, processId=pid,
                  managedThreadId=1, stopwatchFrequency=1_000_000, elapsedTicks=10_000,
                  capsulePath=str(capsule_path), capsuleSha256=capsule.digest(capsule_path),
                  resultPath=str(result_path), baselineBuildId=data["baselineBuildId"],
                  runtimeAbiHash=data["runtimeAbiHash"], patchId=data["patchId"],
                  result="PassedExpectedFailure" if mode in FAILURES else
                         "PassedExpectedRejection" if mode not in POSITIVES | {"Baseline"} else "Passed",
                  error="", callbackReturnCode=0 if mode in POSITIVES | {"Baseline"} else 1,
                  inputReadCount=read_count, byteInputs=byte_inputs, operations=[], snapshots=[],
                  observerJoined=False, observerErrors=[], observerSamples=[], observerDroppedBefore=0,
                  observerDroppedAfter=0, initializerEvents=[])
    d = dict(schemaVersion=1, enabled=True, runtimeAbiVersion=1, metadataBudgetCapabilityVersion=1,
             recoveryCapabilityVersion=1, startupCandidateSchemaVersion=1, startupObservationMode="EarlyTracking",
             startupCandidateNames=data["candidates"], state="Disabled", stateCode=0, lastError=0,
             detail="", baselineBuildId="", patchId="", generation=0, expected=0, staged=0, retainedBytes=0,
             closureLoadOrder=[], stableAotNames=[], commitOrder=[], assemblies=[], events=[], baselineUses=[],
             enumerationGeneration=0,
             ordinaryAssemblies=[dict(name=n, isInterpreter=False) for n in data["candidates"] + ["AssemblyShadowDemo.Bootstrap", "mscorlib"]],
             classEnumerationGeneration=0, ordinaryClasses=[])
    cursors = list(budget.FRESH_CURSORS)
    ordinary = shadow = reserved = 0
    terminal = 0
    terminal_reason = ""

    def op(name, code=0, text="Success"):
        result["operations"].append(dict(phase=name, code=text, intCode=code,
            startedTicks=100 + 10 * len(result["operations"]), elapsedTicks=1))
        d["lastError"] = code
        d["detail"] = ""

    def state(name):
        d["state"], d["stateCode"] = name, m04.STATE_CODES[name]

    def event(kind, name=""):
        d["events"].append(dict(sequence=len(d["events"]) + 1, kind=kind, name=name,
                                generation=d["generation"], stagedCount=d["staged"]))

    def sample(phase, raw, thread=2, ticks=1):
        return dict(phase=phase, rawJson=json.dumps(raw), code=0, threadId=thread, ticks=ticks)

    def snap(phase):
        nonlocal terminal_reason
        if terminal and not terminal_reason: terminal_reason = d["detail"]
        state_name = d["state"]
        disposition, dc, abort = ("RestartRequired", 0, False) if terminal else (
            ("BaselineUnselected", 5, False) if state_name in ("Disabled", "CandidatesRegistered") else
            ("BaselineEligibleAfterAbort", 3, False) if state_name == "Aborted" else
            ("ActiveShadow", 4, False) if state_name == "Committed" else
            ("AbortRequired", 2, True) if d["lastError"] == 15 else ("CorrectInputOrAbort", 1, True))
        recovery = dict(schemaVersion=1, enabled=True, capabilityVersion=1, stateCode=d["stateCode"], state=state_name,
                        published=d["generation"] == 1, abortAllowed=abort, disposition=disposition, dispositionCode=dc,
                        terminalFailureCode=terminal, reason=terminal_reason if terminal else d["detail"],
                        retainedBytes=d["retainedBytes"], baselineEligibilityRequiresStartupValidation=dc != 4)
        capacity = dict(schemaVersion=1, enabled=True, profileVersion=1, indexBits=22, kindBits=2,
                        remainingSlots=budget.remaining_slots(cursors), ordinaryAllocatedCount=ordinary,
                        shadowAllocatedCount=shadow, reservedImageCount=reserved, **budget.evaluate_budget(cursors, sizes))
        result["snapshots"].append(dict(phase=phase, diagnosticsCode="Success", diagnosticsJson=json.dumps(d),
            recoveryCode="Success", recoveryJson=json.dumps(recovery), capacityCode="Success",
            capacityJson=json.dumps(capacity), orderedSizes=sizes.copy()))

    snap("before-startup-ops")
    if mode in ("Control", "MetadataFailure", "InitializerFailure"):
        result["observerJoined"] = True
    if mode == "Baseline": return result
    if mode == "OrdinaryFirst":
        op("ordinary-before-configure"); ordinary += 1
        cursors = budget.evaluate_budget(cursors, [Path(data["ordinaryPath"]).stat().st_size])["finalCursors"]
        d["ordinaryAssemblies"].append(dict(name=gate.ORDINARY, isInterpreter=True))
        snap("after-ordinary-before-configure")
    if mode in GUARDS:
        op("preconfigure-" + mode.lower())
        d["baselineUses"] = [dict(name=gate.INTERNAL, kind="AssemblyReflection",
            detail="Image::ClassFromName.input FirstUseSequence=1", type="", thread=777, timestamp=888)]
        snap("after-preconfigure-witness")
    op("configure"); state("CandidatesRegistered"); d["baselineBuildId"] = data["baselineBuildId"]
    d["stableAotNames"] = ["AssemblyShadowDemo.Bootstrap", "mscorlib"]; event("candidates-registered"); snap("after-configure")
    op("begin"); state("Staging"); d["patchId"] = data["patchId"]; d["closureLoadOrder"] = names
    d["expected"] = len(names)
    d["assemblies"] = [dict(name=n, mvid="", skeletonBuilt=False, runtimeMetadataInitialized=False,
                           published=False, moduleInitializerAttempted=False, moduleInitializerRan=False) for n in names]
    event("transaction-begun"); snap("after-begin")
    if result["observerJoined"]: result["observerSamples"].append(sample("before", d))
    if mode == "Oversize":
        op("reserve", 23, "MetadataCapacityExceeded"); d["detail"] = "Metadata capacity rejected before Stage: " + names[-1]
        snap("after-failed-reserve")
    else:
        op("reserve"); cursors = budget.evaluate_budget(cursors, sizes)["finalCursors"]; reserved += len(names)
        event("metadata-budget-reserved"); snap("after-reserve")
        if result["observerJoined"]: result["observerSamples"].append(sample("before", d, ticks=10))
        if mode == "OrdinaryAfterReserve":
            op("ordinary-after-reserve"); ordinary += 1
            cursors = budget.evaluate_budget(cursors, [Path(data["ordinaryPath"]).stat().st_size])["finalCursors"]
            d["ordinaryAssemblies"].append(dict(name=gate.ORDINARY, isInterpreter=True)); snap("after-ordinary-after-reserve")
        if mode == "Mismatch":
            raw = Path(rows[0]["dllPath"]).read_bytes() + b"\0"
            result["byteInputs"].append(dict(name=names[0], path=rows[0]["dllPath"], length=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(), kind="mismatch-dll"))
            op("stage:" + names[0], 24, "MetadataBudgetMismatch"); d["detail"] = "DLL size differs from the reserved closure input."
            snap("after-mismatch")
        else:
            for row, assembly in zip(rows, d["assemblies"]):
                op("stage:" + row["name"])
                assembly["mvid"] = gate.read_identity(Path(row["dllPath"]))["mvid"]; assembly["skeletonBuilt"] = True
                d["staged"] += 1; shadow += 1; d["retainedBytes"] += row["dllLength"] + row["pdbLength"]
                event("skeleton-created", row["name"])
            state("Staged"); snap("after-stage")
            if mode in GUARDS:
                op("validate", 15, "BaselineAlreadyUsed"); d["detail"] = gate.INTERNAL
            elif mode == "MetadataFailure":
                op("validate", 13, "ReferenceResolutionFailed"); state("Failed"); terminal = 13
                event("metadata-begin", names[0]); d["detail"] = "AssemblyA.Contracts: Image::ReadType invalid type"
            else:
                op("validate")
                for a in d["assemblies"]:
                    event("metadata-begin", a["name"]); a["runtimeMetadataInitialized"] = True; event("metadata-ready", a["name"])
                state("Validated"); event("transaction-validated")
                if mode == "Control" and data["patchId"] == "P01":
                    d["baselineUses"] = copy.deepcopy(P01_BASELINE_USES)
            snap("after-validate")
            if mode in POSITIVES | {"InitializerFailure"}:
                op("commit", 19 if mode == "InitializerFailure" else 0,
                   "ModuleInitializerFailed" if mode == "InitializerFailure" else "Success")
                # During initializer execution, the previous successful Validate is the mutable error.
                d["lastError"] = 0
                state("Committing"); d["generation"] = d["enumerationGeneration"] = d["classEnumerationGeneration"] = 1
                for a in d["assemblies"]: a["published"] = True
                d["ordinaryAssemblies"].extend(dict(name=n, isInterpreter=True) for n in names)
                event("active-published")
                for a in d["assemblies"]:
                    event("initializer-begin", a["name"]); a["moduleInitializerAttempted"] = True
                    if mode == "InitializerFailure":
                        result["initializerEvents"].append(dict(name=a["name"], diagnostics=sample("initializer", d, 1, 20 + len(result["initializerEvents"]))))
                    if mode == "InitializerFailure" and a["name"] == "AssemblyA.Implementation.Extensibility":
                        event("initializer-failed", a["name"]); state("FailedAfterCommit"); terminal = 19
                        d["lastError"] = 19; d["detail"] = "R01-INIT-THROW:AssemblyA.Implementation.Extensibility"; break
                    a["moduleInitializerRan"] = True; d["commitOrder"].append(a["name"]); event("initializer-complete", a["name"])
                if not terminal: state("Committed"); event("transaction-committed")
                snap("after-commit")
    if mode in FAILURES:
        code, text, final_op = (2, "InvalidState", "begin-after-failure") if mode == "MetadataFailure" else (18, "AlreadyCommitted", "begin-after-commit")
        op("abort", code, text); op(final_op, code, text)
        d["detail"] = "Operation is not allowed in the current transaction state."
        snap("after-rejected-operations")
    elif mode not in POSITIVES:
        op("abort"); state("Aborted"); event("transaction-aborted")
        d["detail"] = "Private metadata retained; a second transaction is forbidden."; snap("after-abort")
    if result["observerJoined"]: result["observerSamples"].append(sample("after", d, ticks=1000))
    return result


class EarlyReceiptTests(unittest.TestCase):
    def create(self, root, mode, patch_id=None):
        data = make_capsule(root, mode)
        if patch_id is not None:
            data["patchId"] = patch_id
            by_name = {row["name"]: row for row in data["inputs"]}
            data["inputs"] = [by_name[name] for name in gate.m07.fixture_order(patch_id)]
        cap = root / "r01-early.capsule"; capsule.write_capsule(cap, data)
        out = root / "r01-early.json"
        value = emit_receipt(data, cap, out)
        return data, cap, out, value

    def verify(self, cap, out, value):
        out.write_text(json.dumps(value))
        return gate.verify_early_receipt(out, cap, value["mode"], 1234)

    def test_all_actual_schema_modes_pass(self):
        for mode in capsule.MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), mode)
                self.assertTrue(self.verify(cap, out, value)["diagnosticProfileComplete"])

    def test_every_mode_rejects_operation_input_and_publication_mutants(self):
        for mode in capsule.MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, original = self.create(Path(t).resolve(), mode)
                mutations = [
                    ("input read count", lambda v: v.update(inputReadCount=v["inputReadCount"] + 1)),
                    ("byte hash", lambda v: v["byteInputs"][0].update(sha256="f" * 64)),
                    ("callback", lambda v: v.update(callbackReturnCode=2)),
                    ("mode", lambda v: v.update(mode="Type" if mode != "Type" else "Control")),
                    ("native missing", lambda v: mutate_raw(v, 0, "diagnosticsJson", lambda d: d.pop("events"))),
                    ("generation", lambda v: mutate_raw(v, 0, "diagnosticsJson", lambda d: d.update(generation=1))),
                    ("recovery bool", lambda v: mutate_raw(v, 0, "recoveryJson", lambda d: d.update(published=0))),
                    ("capacity profile", lambda v: mutate_raw(v, 0, "capacityJson", lambda d: d.update(profileVersion=2))),
                    ("capacity ordinary", lambda v: mutate_raw(v, 0, "capacityJson", lambda d: d.update(ordinaryAllocatedCount=1))),
                    ("observation mode", lambda v: mutate_raw(v, 0, "diagnosticsJson", lambda d: d.update(startupObservationMode="ConfigureOnly"))),
                ]
                if original["operations"]:
                    mutations += [("native operation code", lambda v: v["operations"][-1].update(intCode=20)),
                                  ("wrong snapshot phase", lambda v: v["snapshots"][-1].update(phase="made-up"))]
                for name, mutate in mutations:
                    with self.subTest(mutation=name):
                        value = copy.deepcopy(original); mutate(value)
                        with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_phase_specific_mutants_rejected(self):
        cases = [
            ("Control", "after-reserve", "capacityJson", "reservedImageCount", 0),
            ("Control", "after-stage", "capacityJson", "shadowAllocatedCount", 0),
            ("Control", "after-stage", "diagnosticsJson", "retainedBytes", 0),
            ("Control", "after-commit", "diagnosticsJson", "commitOrder", []),
            ("Control", "after-commit", "recoveryJson", "dispositionCode", 0),
            ("Type", "after-preconfigure-witness", "diagnosticsJson", "baselineUses", []),
            ("Type", "after-configure", "diagnosticsJson", "baselineUses", []),
            ("Object", "after-abort", "diagnosticsJson", "baselineUses", []),
            ("NativeScript", "after-preconfigure-witness", "diagnosticsJson", "baselineUses", []),
            ("MetadataFailure", "after-validate", "diagnosticsJson", "lastError", 2),
            ("MetadataFailure", "after-rejected-operations", "diagnosticsJson", "lastError", 13),
            ("InitializerFailure", "after-commit", "diagnosticsJson", "lastError", 18),
            ("InitializerFailure", "after-rejected-operations", "diagnosticsJson", "lastError", 19),
            ("MetadataFailure", "after-rejected-operations", "recoveryJson", "terminalFailureCode", 2),
            ("InitializerFailure", "after-rejected-operations", "recoveryJson", "terminalFailureCode", 18),
            ("Oversize", "after-failed-reserve", "capacityJson", "reservedImageCount", 4),
            ("Mismatch", "after-mismatch", "capacityJson", "shadowAllocatedCount", 1),
            ("OrdinaryFirst", "after-ordinary-before-configure", "capacityJson", "ordinaryAllocatedCount", 2),
            ("OrdinaryAfterReserve", "after-ordinary-after-reserve", "capacityJson", "ordinaryAllocatedCount", 2),
        ]
        for mode, phase, raw, key, wanted in cases:
            with self.subTest(mode=mode, phase=phase, key=key), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), mode)
                self.verify(cap, out, value)
                index = next(i for i, row in enumerate(value["snapshots"]) if row["phase"] == phase)
                mutate_raw(value, index, raw, lambda d: d.update({key: wanted}))
                with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_observer_and_initializer_mutants_rejected(self):
        for mode in ("Control", "MetadataFailure", "InitializerFailure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, original = self.create(Path(t).resolve(), mode)
                mutations = [
                    lambda v: v.update(observerJoined=False),
                    lambda v: v.update(observerErrors=["failed"]),
                    lambda v: v.update(observerSamples=v["observerSamples"][:1]),
                    lambda v: v["observerSamples"][0].update(threadId=1),
                    lambda v: v.update(observerDroppedBefore=1),
                    lambda v: v["observerSamples"][-1].update(code=20),
                ]
                if mode == "InitializerFailure":
                    mutations.extend([lambda v: v.update(initializerEvents=[]),
                                      lambda v: v["initializerEvents"][0].update(name="wrong-provider"),
                                      lambda v: v["initializerEvents"][0]["diagnostics"].update(threadId=2)])
                for mutate in mutations:
                    value = copy.deepcopy(original); mutate(value)
                    with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_reserved_cursor_mutation_remains_rejected_after_self_consistent_rebudget(self):
        with tempfile.TemporaryDirectory() as t:
            data, cap, out, value = self.create(Path(t).resolve(), "Control")
            def mutate(c):
                cursors = c["cursors"].copy(); cursors[3] += 1
                c.update(budget.evaluate_budget(cursors, [row["dllLength"] for row in data["inputs"]]))
                c["remainingSlots"] = budget.remaining_slots(cursors)
            mutate_raw(value, 3, "capacityJson", mutate)
            with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_mvid_half_publication_private_cache_and_terminal_reason_mutants(self):
        mutations = [
            ("Control", "after-stage", "diagnosticsJson", lambda d: d["assemblies"][0].update(mvid=str(uuid.UUID(int=99)))),
            ("Control", "after-commit", "diagnosticsJson", lambda d: d["assemblies"][0].update(published=False)),
            ("Control", "after-stage", "diagnosticsJson", lambda d: d["ordinaryClasses"].append(dict(
                assemblyName=gate.INTERNAL, typeName="InternalEntry", isInterpreter=True,
                isConstructedGeneric=False, usesStagedMetadata=True))),
            ("Control", "after-configure", "diagnosticsJson", lambda d: d["ordinaryAssemblies"].pop()),
            ("MetadataFailure", "after-rejected-operations", "recoveryJson", lambda d: d.update(reason="erased")),
            ("InitializerFailure", "after-rejected-operations", "recoveryJson", lambda d: d.update(retainedBytes=0)),
            ("Control", "after-reserve", "capacityJson", lambda d: d["allocations"][1].update(kind=True)),
        ]
        for mode, phase, field, mutate in mutations:
            with self.subTest(mode=mode, phase=phase), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), mode)
                index = next(i for i, row in enumerate(value["snapshots"]) if row["phase"] == phase)
                mutate_raw(value, index, field, mutate)
                with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_coherent_cross_generation_observer_and_published_aot_generic_allowed(self):
        with tempfile.TemporaryDirectory() as t:
            _, cap, out, value = self.create(Path(t).resolve(), "Control")
            private = json.loads(next(row["diagnosticsJson"] for row in value["snapshots"] if row["phase"] == "after-validate"))
            final = json.loads(value["snapshots"][-1]["diagnosticsJson"])
            private["enumerationGeneration"] = private["classEnumerationGeneration"] = 1
            private["ordinaryAssemblies"] = final["ordinaryAssemblies"]
            private["ordinaryClasses"] = [dict(assemblyName="mscorlib", typeName="List",
                isInterpreter=False, isConstructedGeneric=True, usesStagedMetadata=True)]
            sample = dict(phase="before", code=0, threadId=2, ticks=100, rawJson=json.dumps(private))
            value["observerSamples"].insert(-1, sample)
            self.verify(cap, out, value)
            private["classEnumerationGeneration"] = 0
            sample["rawJson"] = json.dumps(private)
            with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_observer_and_initializer_native_raw_mutants(self):
        with tempfile.TemporaryDirectory() as t:
            _, cap, out, original = self.create(Path(t).resolve(), "InitializerFailure")
            for target, mutate in [
                ("observer", lambda d: d.update(generation=1)),
                ("observer", lambda d: d.update(events=[])),
                ("observer", lambda d: d["assemblies"][0].update(mvid=str(uuid.UUID(int=99)))),
                ("initializer", lambda d: d.update(generation=0)),
                ("initializer", lambda d: d["assemblies"][-1].update(published=False)),
                ("initializer", lambda d: d.update(commitOrder=ORDER)),
            ]:
                value = copy.deepcopy(original)
                sample = value["observerSamples"][0] if target == "observer" else value["initializerEvents"][0]["diagnostics"]
                raw = json.loads(sample["rawJson"]); mutate(raw); sample["rawJson"] = json.dumps(raw)
                with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_all_observer_modes_reject_metadata_ready_before_skeleton_or_validate(self):
        for mode in ("Control", "MetadataFailure", "InitializerFailure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, original = self.create(Path(t).resolve(), mode)
                self.verify(cap, out, original)
                for sample_index in (0, 1):
                    # First is the mandatory after-Begin sample, second is a
                    # retained after-Reserve sample; neither has staged owners.
                    with self.subTest(sample=sample_index):
                        value = copy.deepcopy(original)
                        sample = value["observerSamples"][sample_index]
                        raw = json.loads(sample["rawJson"])
                        self.assertFalse(any(a["runtimeMetadataInitialized"] for a in raw["assemblies"]))
                        raw["assemblies"][0]["runtimeMetadataInitialized"] = True
                        sample["rawJson"] = json.dumps(raw)
                        with self.assertRaisesRegex(VerificationError, "privateMetadataReadiness"):
                            self.verify(cap, out, value)
                # Real skeletons still do not imply completed runtime metadata.
                value = copy.deepcopy(original)
                staged = json.loads(next(row["diagnosticsJson"] for row in value["snapshots"] if row["phase"] == "after-stage"))
                staged["assemblies"][0]["runtimeMetadataInitialized"] = True
                value["observerSamples"].insert(-1, dict(phase="before", code=0, threadId=2,
                    ticks=100, rawJson=json.dumps(staged)))
                with self.assertRaisesRegex(VerificationError, "privateMetadataReadiness"):
                    self.verify(cap, out, value)

    def test_validated_private_observer_requires_completed_metadata(self):
        for mode in ("Control", "InitializerFailure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), mode)
                validated = json.loads(next(row["diagnosticsJson"] for row in value["snapshots"] if row["phase"] == "after-validate"))
                sample = dict(phase="before", code=0, threadId=2, ticks=100, rawJson=json.dumps(validated))
                value["observerSamples"].insert(-1, sample)
                self.verify(cap, out, value)
                validated["assemblies"][0]["runtimeMetadataInitialized"] = False
                sample["rawJson"] = json.dumps(validated)
                with self.assertRaisesRegex(VerificationError, "privateMetadataReadiness"):
                    self.verify(cap, out, value)

    def test_physical_stable_identity_spelling_and_order_are_independent_of_policy(self):
        for mode in ("Control", "MetadataFailure", "InitializerFailure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                data, cap, out, value = self.create(Path(t).resolve(), mode)
                self.assertEqual(data["stableAotNames"], ["assemblyshadowdemo.bootstrap", "mscorlib"])
                raw = json.loads(value["snapshots"][0]["diagnosticsJson"])
                self.assertIn(dict(name="AssemblyShadowDemo.Bootstrap", isInterpreter=False), raw["ordinaryAssemblies"])
                self.assertTrue(self.verify(cap, out, value)["diagnosticProfileComplete"])
                configured = next(row for row in value["snapshots"] if row["phase"] == "after-configure")
                self.assertEqual(json.loads(configured["diagnosticsJson"])["stableAotNames"],
                                 ["AssemblyShadowDemo.Bootstrap", "mscorlib"])

    def test_missing_ambiguous_and_reordered_physical_stable_identity_rejected(self):
        def missing(d):
            d["ordinaryAssemblies"] = [a for a in d["ordinaryAssemblies"] if a["name"] != "AssemblyShadowDemo.Bootstrap"]
        def duplicate(d):
            d["ordinaryAssemblies"].append(dict(name="assemblyshadowdemo.bootstrap", isInterpreter=False))
        def reorder(d):
            d["stableAotNames"].reverse()
        def retain_order(d):
            d["ordinaryAssemblies"].reverse()
        for mode in ("Control", "MetadataFailure", "InitializerFailure"):
            for mutate in (missing, duplicate, reorder, retain_order):
                for observer in (False, True):
                    with self.subTest(mode=mode, mutation=mutate.__name__, observer=observer), tempfile.TemporaryDirectory() as t:
                        _, cap, out, value = self.create(Path(t).resolve(), mode)
                        row = value["observerSamples"][0] if observer else next(
                            r for r in value["snapshots"] if r["phase"] == "after-configure")
                        field = "rawJson" if observer else "diagnosticsJson"
                        raw = json.loads(row[field]); mutate(raw); row[field] = json.dumps(raw)
                        with self.assertRaises(VerificationError): self.verify(cap, out, value)

    def test_initializer_failure_stops_at_extensibility_preserving_internal_witness_identity(self):
        with tempfile.TemporaryDirectory() as t:
            _, cap, out, value = self.create(Path(t).resolve(), "InitializerFailure")
            self.assertEqual([row["name"] for row in value["initializerEvents"]],
                             ["AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility"])
            final = json.loads(value["snapshots"][-1]["diagnosticsJson"])
            self.assertEqual(final["commitOrder"], ["AssemblyA.Contracts"])
            self.assertEqual([row["name"] for row in final["assemblies"] if row["moduleInitializerAttempted"]],
                             ["AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility"])
            self.assertEqual(gate.INTERNAL, "AssemblyA.Implementation.Internal")
            self.verify(cap, out, value)
            value["initializerEvents"][-1]["name"] = "AssemblyA.Implementation.Internal"
            with self.assertRaisesRegex(VerificationError, "initializerOrder"):
                self.verify(cap, out, value)


    def test_p01_retains_real_nonclosure_provider_history_without_private_publication(self):
        with tempfile.TemporaryDirectory() as t:
            data, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
            self.assertEqual([row["name"] for row in data["inputs"]], ["AssemblyA.Implementation.Internal"])
            validated = next(s for s in value["snapshots"] if s["phase"] == "after-validate")
            d = json.loads(validated["diagnosticsJson"])
            self.assertEqual(d["baselineUses"], P01_BASELINE_USES)
            self.assertEqual(d["generation"], 0)
            self.assertFalse(any(row["published"] for row in d["assemblies"]))
            self.assertTrue(self.verify(cap, out, value)["diagnosticProfileComplete"])

    def test_p01_rejects_selected_unknown_premature_or_invalid_first_use_records(self):
        mutations = [
            ("selected", lambda uses: uses[0].update(name="AssemblyA.Implementation.Internal")),
            ("unregistered", lambda uses: uses[0].update(name="System")),
            ("wrong spelling", lambda uses: uses[0].update(name="assemblya.contracts")),
            ("unknown kind", lambda uses: uses[0].update(kind="Untracked")),
            ("zero thread", lambda uses: uses[0].update(thread=0)),
            ("zero timestamp", lambda uses: uses[0].update(timestamp=0)),
            ("missing sequence", lambda uses: uses[0].update(detail="Image::ClassFromName.input")),
            ("duplicate sequence", lambda uses: uses[0].update(detail="Image::ClassFromName.input FirstUseSequence=1")),
            ("sequence gap", lambda uses: uses[0].update(detail="Image::ClassFromName.input FirstUseSequence=3")),
            ("zero sequence", lambda uses: uses[0].update(detail="Image::ClassFromName.input FirstUseSequence=0")),
            ("time regression", lambda uses: uses[0].update(timestamp=1)),
            ("duplicate record", lambda uses: uses.append(copy.deepcopy(uses[0]))),
            ("registry reorder", lambda uses: uses.reverse()),
        ]
        for label, mutate in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
                snapshot = next(s for s in value["snapshots"] if s["phase"] == "after-validate")
                d = json.loads(snapshot["diagnosticsJson"]); mutate(d["baselineUses"])
                snapshot["diagnosticsJson"] = json.dumps(d)
                with self.assertRaises(VerificationError): self.verify(cap, out, value)
        for phase in ("before-startup-ops", "after-configure", "after-begin", "after-reserve", "after-stage"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
                snapshot = next(s for s in value["snapshots"] if s["phase"] == phase)
                d = json.loads(snapshot["diagnosticsJson"]); d["baselineUses"] = copy.deepcopy(P01_BASELINE_USES)
                snapshot["diagnosticsJson"] = json.dumps(d)
                with self.assertRaisesRegex(VerificationError, "preValidationFirstUse"):
                    self.verify(cap, out, value)

    def test_p01_cannot_delete_or_rewrite_prior_main_records(self):
        mutations = [lambda uses: uses.clear(), lambda uses: uses[0].update(type="Changed.Type"),
                     lambda uses: uses[0].update(thread=123), lambda uses: uses[0].update(timestamp=1172860484094167),
                     lambda uses: uses[0].update(kind="TypeReflection"),
                     lambda uses: uses[0].update(detail="Different.Site FirstUseSequence=2")]
        for mutate in mutations:
            with tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
                snapshot = value["snapshots"][-1]; d = json.loads(snapshot["diagnosticsJson"])
                mutate(d["baselineUses"]); snapshot["diagnosticsJson"] = json.dumps(d)
                with self.assertRaisesRegex(VerificationError, "immutableFirstUse"):
                    self.verify(cap, out, value)

    def test_full_closure_keeps_empty_history_requirement(self):
        for mode in ("Control", "MetadataFailure", "InitializerFailure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), mode)
                snapshot = next(s for s in value["snapshots"] if s["phase"] == "after-validate")
                d = json.loads(snapshot["diagnosticsJson"]); d["baselineUses"] = copy.deepcopy(P01_BASELINE_USES)
                snapshot["diagnosticsJson"] = json.dumps(d)
                with self.assertRaisesRegex(VerificationError, "selected closure"):
                    self.verify(cap, out, value)

    def test_p01_observer_can_copy_prevalidate_state_then_new_validate_use_history(self):
        with tempfile.TemporaryDirectory() as t:
            _, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
            sample = value["observerSamples"][1]
            d = json.loads(sample["rawJson"])
            self.assertEqual(d["state"], "Staging")
            d["baselineUses"] = [copy.deepcopy(P01_BASELINE_USES[1])]
            sample["rawJson"] = json.dumps(d)
            later = copy.deepcopy(sample); later["ticks"] += 1
            d["baselineUses"] = copy.deepcopy(P01_BASELINE_USES); later["rawJson"] = json.dumps(d)
            value["observerSamples"].insert(2, later)
            self.verify(cap, out, value)
            # A later registry copy may add records in registry order, but can
            # never lose one even when both state copies still say Staging.
            d["baselineUses"] = []; later["rawJson"] = json.dumps(d)
            with self.assertRaisesRegex(VerificationError, "immutableFirstUse"):
                self.verify(cap, out, value)

    def test_p01_observer_rejects_initial_premature_changed_or_terminal_missing_history(self):
        for target in ("initial", "changed", "not in final", "terminal missing", "selected"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as t:
                _, cap, out, value = self.create(Path(t).resolve(), "Control", "P01")
                index = 0 if target == "initial" else -1 if target == "terminal missing" else 1
                sample = value["observerSamples"][index]; d = json.loads(sample["rawJson"])
                d["baselineUses"] = copy.deepcopy(P01_BASELINE_USES)
                if target == "changed": d["baselineUses"][0]["thread"] = 123
                if target == "not in final":
                    d["baselineUses"].append(dict(name="AssemblyShadowDemo.ContractsConsumer", kind="ClassInit",
                        detail="Class::Init FirstUseSequence=3", type="Consumer", thread=123, timestamp=1172860484094167))
                if target == "terminal missing": d["baselineUses"] = []
                if target == "selected": d["baselineUses"][0]["name"] = "AssemblyA.Implementation.Internal"
                sample["rawJson"] = json.dumps(d)
                with self.assertRaises(VerificationError): self.verify(cap, out, value)



def mutate_raw(value, index, field, mutate):
    raw = json.loads(value["snapshots"][index][field]); mutate(raw)
    value["snapshots"][index][field] = json.dumps(raw)


if __name__ == "__main__":
    unittest.main()
