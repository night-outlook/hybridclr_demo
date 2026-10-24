#!/usr/bin/env python3
"""Launch exactly ONE ISOLATED historical evidence audit; never run core or SDK.

Consumes the fresh audit-only staging root even on failure or interruption.
Original retained raw/sdk/preflight/evidence paths are never written to.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

SOURCE_BLOB = "220aa2831458b37a81f66555f27d95349ec7013f"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def blob(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or nonregular audit stage input: " + str(path))
    return json.loads(path.read_bytes())


def one_shot(stage: Path, timeout_seconds: int):
    root = stage.resolve()
    if stage != root or not stage.is_absolute():
        raise ValueError("Audit-only stage path must be canonical and absolute")
    stage_receipt = safe_json(stage / "AUDIT_ONLY_STAGE.json")
    if (stage_receipt["status"] != "StagedNotExecuted" or
            stage_receipt["originalLocalResultPromoted"] is not False or
            stage_receipt["originalCoreRetried"] is not False or
            stage_receipt["stage"] != str(stage)):
        raise ValueError("Invalid/stale historical audit stage receipt")
    source = stage / "audit.py"
    if blob(source) != SOURCE_BLOB:
        raise ValueError("Staged historical audit source differs from audited blob")
    if (stage / "EVIDENCE_AUDIT.json").exists():
        raise ValueError("Audit evidence already exists; never rerun")
    marker = stage / "AUDIT_ONLY_INVOCATION.json"
    stdout = stage / "audit-only.stdout.bin"
    stderr = stage / "audit-only.stderr.bin"
    resultfile = stage / "AUDIT_ONLY_RUN_RECEIPT.json"
    if any(p.exists() or p.is_symlink() for p in (marker, stdout, stderr, resultfile)):
        raise ValueError("Audit-only invocation already consumed")
    argv = [sys.executable, "-B", str(source)]
    start = now()
    # x-mode is the atomic one-shot barrier, committed BEFORE launching any work.
    with marker.open("x", encoding="utf-8") as f:
        json.dump(dict(kind="R03P1HistoricalEvidenceAuditInvocation",
                       time=start, argv=argv, cwd=str(stage),
                       originalConsumedCoreRetried=False,
                       originalLocalResult="FAIL",
                       processLifetime="NotYetObserved"), f, indent=2)
        f.write("\n")
    state = {"kind": "R03P1HistoricalEvidenceAuditRun", "schemaVersion": 1,
             "scope": "NewIsolatedAuditOnly", "sourceGitBlob": SOURCE_BLOB,
             "argv": argv, "cwd": str(stage), "start": start,
             "timedOut": False, "unknownCommandLifetime": False,
             "sourceSdkCompilerInvokedByRunner": False,
             "originalRawCoreRetried": False,
             "originalB7E3LocalResult": "FAIL",
             "fullProductAcceptance": False}
    started = time.monotonic()
    with stdout.open("xb") as so, stderr.open("xb") as se:
        proc = None
        try:
            proc = subprocess.Popen(argv, cwd=stage, stdout=so, stderr=se,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                                         "GIT_TERMINAL_PROMPT": "0"},
                                    start_new_session=True)
            state["pid"] = proc.pid
            state["exit"] = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            state["timedOut"] = True
            state["unknownCommandLifetime"] = True
            state["exit"] = None
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=10)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=10)
                    except (OSError, subprocess.TimeoutExpired):
                        state["unreapedAuditProcess"] = True
        except BaseException as error:
            state["exception"] = repr(error)
            state["unknownCommandLifetime"] = True
            state["exit"] = None
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=10)
                except (OSError, subprocess.TimeoutExpired):
                    state["unreapedAuditProcess"] = True
    state["end"] = now()
    state["elapsedMonotonicSeconds"] = time.monotonic() - started
    state["stdoutSha256"] = sha(stdout)
    state["stderrSha256"] = sha(stderr)
    state["stdoutBytes"] = stdout.stat().st_size
    state["stderrBytes"] = stderr.stat().st_size
    state["auditReportObserved"] = (stage / "EVIDENCE_AUDIT.json").is_file()
    state["result"] = "FailedOrIncomplete"
    if (state["exit"] == 0 and not state["unknownCommandLifetime"] and
            state["auditReportObserved"]):
        audit = safe_json(stage / "EVIDENCE_AUDIT.json")
        if (audit.get("result") == "PassedHistoricalEvidenceAuditOnly" and
                audit.get("auditMode") == "ReadOnlyIsolatedB7E3History" and
                audit.get("originalB7E3LocalResult") == "FAIL" and
                audit.get("liveRemoteHeadCheck") == "NotRun_TimeVariant" and
                audit.get("productAcceptance") is False):
            state["result"] = "PassedHistoricalAuditOnly_UnchangedLocalFail"
    with resultfile.open("xb") as f:
        f.write((json.dumps(state, indent=2) + "\n").encode())
    print(json.dumps(state, indent=2))
    return 0 if state["result"].startswith("PassedHistorical") else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    args = parser.parse_args()
    try:
        if not 60 <= args.timeout_seconds <= 3600:
            raise ValueError("Audit-only timeout must be between 60s and 3600s")
        return one_shot(args.stage, args.timeout_seconds)
    except (ValueError, OSError, KeyError) as error:
        print("AUDIT_ONLY_BLOCKED_OR_FAILED: " + repr(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
