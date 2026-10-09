#!/usr/bin/env python3
"""Original S semantic *identity* joins; not a fresh Player or exhaustive ABI review.

Run only after audit_s_provenance.py authenticated the full original archive,
cell ledger and Git checkpoint under a clean fc55 checkout. Never modify inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from audit_s_provenance import (
    CHECKPOINT, PUBLICATION, EXPECTED, bound_json, digest, git, json_equal, load,
    relpath, require, write,
)

LIVE = "/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/"
FOCUSED = re.compile(r"^(?:C|D|O|R)\d\d-")
EXPECTED_GROUPS = {"focused": 19, "producer": 4, "early": 10, "resource": 14, "measurement": 12}


def native_int(value):
    return type(value) is int and value > 0


def bound_file(members, path, value, label):
    require(path in members and isinstance(value, str) and value == members[path]["sha256"],
            label + " source/archive digest join: " + path)


def original_relpath(value):
    require(isinstance(value, str) and value.startswith(LIVE),
            "Not an exact S live-root path: " + repr(value)[:160])
    rel = value[len(LIVE):]
    return str(relpath(rel))


def check_command(read, members, receipt, folder, result):
    require(receipt.get("result") == "Passed" and receipt.get("R03Accepted", False) is False,
            "Original verification not recorded Passed")
    cmd = original_relpath(receipt["commandReceipt"])
    bound_file(members, cmd, receipt["commandSha256"], "Command")
    obj = read(cmd)
    require(native_int(receipt.get("launchPid")) and
            obj.get("pid") == receipt["launchPid"] and
            obj.get("pgid") == receipt["launchPid"] and
            obj.get("lifetimePolicy") == "R03OwnedCommandV1" and
            obj.get("interrupted") is False and
            obj.get("remainingProcessGroup") is False,
            "Owned command PID/lifetime does not bind verification: " + folder)
    if "originalExit" in receipt:
        require(type(receipt["originalExit"]) is int and
                obj["exitCode"] == receipt["originalExit"],
                "Command exit mismatch: " + folder)
    if "consoleSha256" in receipt:
        path = original_relpath(receipt["console"])
        bound_file(members, path, receipt["consoleSha256"], "Console")
    return {"command": cmd, "commandSha256": receipt["commandSha256"],
            "pid": obj["pid"], "exitCode": obj["exitCode"]}


def check_raw(read, members, receipt, relative, label):
    bound_file(members, relative, receipt["rawSha256"], label)
    return relative


def original_process_joins(checkpoint, members, ledger):
    checkpoint = Path(checkpoint)
    cells = {cell["id"]: cell for cell in ledger["cells"]}
    require(len(cells) == 90 and all(row["result"] == "Passed" for row in cells.values()),
            "Original S exact ninety passing cell input")
    def read(relative):
        return bound_json(checkpoint / "batch", members, relative)
    groups = {name: [] for name in EXPECTED_GROUPS}
    process_ids = set()
    command_paths = set()
    for name in sorted(cells):
        if FOCUSED.fullmatch(name) or FOCUSED.match(name):
            kind, base, identity = "focused", "players", name
        elif name.startswith("resource-T07-"):
            kind, base, identity = "resource", "resource-players", name[len("resource-"):]
        elif name.startswith("early-"):
            kind, base, identity = "early", "early", name[len("early-"):]
        elif name.startswith("measure-R00-"):
            kind, base, tail = "measurement", "measurements", name[len("measure-"):]
            mode, count = tail.rsplit("-", 1)
            require(re.fullmatch(r"[0-2]", count) and mode.startswith("R00-"), "Measurement repetition")
            identity = mode + "/" + count
        else:
            continue
        prefix = base + "/" + identity + "/"
        verify_path = prefix + "verification.json"
        verified = read(verify_path)
        require(verified.get("result") == "Passed", "Original per-process verification not Passed: " + identity)
        row = {"cell": name, "category": kind, "verificationSha256": members[verify_path]["sha256"],
               "assurance": ["CommittedCheckpointBlob", "OriginalArchiveIndexBytes", "OriginalLedgerCellPassed"]}
        if kind == "focused":
            require(verified.get("R03Accepted", False) is False and
                    len(cells[name]["dependencies"]) == 1 and
                    cells[name]["dependencies"][0].startswith("build-"),
                    "Focused cell/build dependency")
            request, raw = read(prefix + "request.json"), read(prefix + "raw.json")
            bound_file(members, prefix + "request.json", verified["requestSha256"], "Focused request")
            bound_file(members, prefix + "raw.json", verified["rawSha256"], "Focused raw")
            require(request["caseId"] == name and raw["caseId"] == name and
                    request["runId"] == raw["runId"] == verified["runId"] and
                    raw["requestSha256"] == verified["requestSha256"] and
                    native_int(raw["pid"]) and raw["pid"] == verified["launchPid"] and
                    raw["acceptance"] is False,
                    "Focused request/raw/verification/PID join: " + name)
            role = cells[name]["dependencies"][0][len("build-"):]
            build_path = "builds/" + role + "/build-receipt.json"
            bound_file(members, build_path, verified["buildReceiptSha256"], "Focused build")
            build = read(build_path)
            require(build.get("result") == "Passed" and
                    build.get("unityVersion") == "2022.3.62f2" and
                    build.get("architecture") == "arm64" and
                    build.get("nonGeneratedCorePreserved") is True,
                    "Real pinned native build role: " + role)
            row.update(role=role, requestSha256=verified["requestSha256"],
                       rawSha256=verified["rawSha256"], runId=verified["runId"],
                       nativeBuildSha256=verified["buildReceiptSha256"], pid=raw["pid"])
            row["assurance"] += ["RequestRawReceiptEquality", "FreshPlayerPid", "ActualBuildReceiptBinding"]
            # The cell evidence must use the exact same verification contract.
            require(json_equal(cells[name].get("evidence"), verified),
                    "Focused cell evidence differs from original verification: " + name)
        else:
            if "commandReceipt" in verified:
                row.update(check_command(read, members, verified, prefix, name))
                require(row["command"] not in command_paths, "Reused process command")
                command_paths.add(row["command"])
            if "rawPath" in verified:
                raw = original_relpath(verified["rawPath"])
                check_raw(read, members, verified, raw, kind + " raw")
                row["rawSha256"] = verified["rawSha256"]
                row["rawPath"] = raw
            elif kind == "early":
                check_raw(read, members, verified, prefix + "early.json", "Early raw")
                row["rawSha256"] = verified["rawSha256"]
            else:
                require(False, "Unbound raw process in category " + kind)
            if "consoleSha256" in verified: row["consoleSha256"] = verified["consoleSha256"]
            if "fresh" in verified: require(verified["fresh"] is True, "Nonfresh Player")
            if kind == "early":
                require(verified.get("case") == identity and verified.get("R03Accepted") is False,
                        "Early case identity or approval")
                bound_file(members, prefix + "early.capsule", verified["capsuleSha256"], "Early capsule")
            if kind == "resource":
                require(verified.get("R03Accepted") is False, "Resource acceptance flag")
            if kind == "measurement":
                require(verified.get("mode") + "/" + str(verified.get("repetition")) == identity and
                        verified.get("releasePerformanceAcceptance") is False,
                        "Original S measurement profile must remain observational")
            row["assurance"] += ["CommandAndOutputFileHashes", "OriginalReceiptDoesNotPromoteAcceptance"]
        if kind != "focused" and "pid" in row:
            require(row["pid"] not in process_ids, "Duplicate process PID")
            process_ids.add(row["pid"])
        groups[kind].append(row)
    # Four unisolated controls are *not* converted into clean warm certificates.
    for name in ("C03-moved-slot", "C04-old-AOT-guard", "C05-direction-reversal",
                 "C07-private-primitive-append"):
        ident = "PC-" + name
        prefix = "players/" + ident + "/"
        v = read(prefix + "verification.json")
        require(v.get("result") == "Passed" and v.get("R03Accepted", False) is False,
                "Recorded producer-control verification")
        for file, digest_key in (("request.json", "requestSha256"), ("raw.json", "rawSha256")):
            bound_file(members, prefix + file, v[digest_key], "Producer control")
        raw = read(prefix + "raw.json")
        request = read(prefix + "request.json")
        require(raw.get("pid") == v["launchPid"] and
                raw.get("runId") == request.get("runId") == v.get("runId"),
                "Producer-control process identity")
        groups["producer"].append({"case": ident, "verificationSha256": members[prefix + "verification.json"]["sha256"],
            "rawSha256": v["rawSha256"], "pid": v["launchPid"],
            "assurance": ["CommittedRawAndRequest", "UnisolatedCertificateNotPromoted"],
            "warmCertificateAcceptance": "NotProvenByThisCrosswalk"})
    counts = {k: len(v) for k, v in groups.items()}
    require(counts == EXPECTED_GROUPS, "Original S process group counts: " + repr(counts))
    require(sum(counts.values()) == 59, "Actual fifty-nine fresh process receipts")
    return {"schemaVersion": 1, "kind": "IRR03OriginalSRoleProcessIdentityCrosswalk",
        "result": "Passed", "originalPublication": PUBLICATION, "executedRepositories": EXPECTED,
        "originalArchiveBytesPreviouslyAuthenticated": True, "originalLedgerCellsPreviouslyAuthenticated": 90,
        "categories": counts, "totalPlayerReceipts": 59, "processRecords": groups,
        "scope": "Original archival digest/request/command/PID/build role joins; not a new Player, exhaustive native ABI or product acceptance.",
        "roleSpecificSourceBuildProcessSemanticAuditComplete": False,
        "capturedGenericExecutionProof": False, "independentReviewer": False,
        "R03Accepted": False, "H2Passed": False, "runtimeAcceptance": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--audit", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    checkpoint = args.original.resolve() / CHECKPOINT
    audit = args.audit.resolve()
    out = args.output.resolve()
    require(not out.exists(), "Unused external crosswalk output required")
    require(git(args.original, "rev-parse", "HEAD").decode().strip() == PUBLICATION and
            not git(args.original, "status", "--porcelain"), "Exact clean original S checkout")
    authenticated = load(audit / "audit.json")
    require(authenticated.get("result") == "Passed" and authenticated.get("inputCommit") == PUBLICATION and
            authenticated.get("archiveMembers") == 15713 and authenticated.get("cells") == 90,
            "Provenance audit must succeed first at original S")
    members = load(audit / "original-archive-members.json")
    require(len(members) == 15713, "Exact archive member map")
    # Original BATCH_EXECUTION.json is deliberately split into transport
    # parts in Git. Consume only the already authenticated reconstructed bytes.
    ledger_path = audit / "reconstructed/batch/BATCH_EXECUTION.json"
    require(ledger_path.is_file() and ledger_path.stat().st_size == members["BATCH_EXECUTION.json"]["size"] and
            digest(ledger_path) == members["BATCH_EXECUTION.json"]["sha256"],
            "Authenticated original S execution ledger reconstruction")
    ledger = load(ledger_path)
    report = original_process_joins(checkpoint, members, ledger)
    out.mkdir(parents=True)
    write(out / "process-joins.json", report)
    require(not git(args.original, "status", "--porcelain"), "Original S changed during crosswalk")
    print(json.dumps({k:v for k,v in report.items() if k!="processRecords"}, sort_keys=True))


if __name__ == "__main__":
    main()
