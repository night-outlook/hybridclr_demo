#!/usr/bin/env python3
"""Copy the two validated M07 evidence-commit gate receipts into the report tree."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path


PROJECT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow_m07")
EVIDENCE_COMMIT = "8aaf30783eb9e5c0aebf96db6afe08aa81209ff8"
SOURCES = (
    (
        PROJECT / "_temp/AssemblyShadow/M07GateA-v6-20260906T2303/gate-a.json",
        "gate-a-v6.json",
        "990e1f63341d0fef84b78425c9720eea05628c18e8b56079dbd21af9b1fda3cf",
        "A-current-evidence-commit-tests-strict-install-and-retention",
    ),
    (
        PROJECT / "_temp/AssemblyShadow/M07GateB-v6-20260906T2308/gate-b.json",
        "gate-b-v6.json",
        "d87b6496c641740a65838a5c69f6d942cce98301671f725a6f23ddb2a71a4e98",
        "B-detached-evidence-commit-tests-strict-install-and-retention",
    ),
)


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular gate receipt: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    destination = PROJECT / "Docs/AssemblyShadow/M07/Evidence/gates"
    require(not destination.exists() and not destination.is_symlink(), "Gate destination already exists")
    destination.mkdir()
    rows = []
    for source, name, expected_hash, expected_gate in SOURCES:
        require(sha256(source) == expected_hash, "Gate receipt hash differs: " + name)
        value = json.loads(source.read_text(encoding="utf-8-sig"))
        require(value.get("schemaVersion") == 1 and value.get("milestone") == "M07" and value.get("result") == "PASS", "Gate receipt did not pass: " + name)
        require(value.get("gate") == expected_gate and value.get("evidenceCommit") == EVIDENCE_COMMIT, "Gate identity differs: " + name)
        require(value.get("python", {}).get("testCount") == 356 and value.get("strictReplay", {}).get("caseCount") == 14, "Gate replay inventory differs: " + name)
        require(value.get("retention") == {"archives": 6, "archiveMembers": 8816, "copiedArtifacts": 19}, "Gate retention inventory differs: " + name)
        target = destination / name
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(sha256(target) == expected_hash, "Copied gate receipt differs: " + name)
        rows.append({"name": name, "path": str(target), "sha256": expected_hash, "gate": expected_gate, "result": "PASS"})
    index = {
        "schemaVersion": 1,
        "milestone": "M07",
        "kind": "EvidenceCommitReviewGates",
        "result": "PASS",
        "recordedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidenceCommit": EVIDENCE_COMMIT,
        "gates": rows,
        "currentGateSha256": SOURCES[0][2],
        "detachedGateSha256": SOURCES[1][2],
        "limitation": "Gate B is an independent deterministic clean-detached-worktree process review, not an independent human or LLM review.",
    }
    index_path = destination / "gate-index-v6.json"
    with index_path.open("x", encoding="utf-8") as stream:
        json.dump(index, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"result": "PASS", "index": str(index_path), "sha256": sha256(index_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
