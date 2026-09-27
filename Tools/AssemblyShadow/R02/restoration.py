"""Bounded recovery of known generated inputs; preserve every failure cause."""
from __future__ import annotations
from pathlib import Path
import re
from evidence import binding, require, write


def diagnostic_scene_allowed(before: bytes, after: bytes):
    def scrub(value):
        for key in (b"expectedBaselineBuildId", b"expectedRuntimeAbiHash"):
            value, count = re.subn(rb"(?m)^  " + key + rb": [^\r\n]*$", b"  " + key + b": <identity>", value)
            require(count == 1, "Non-unique diagnostic scene identity field")
        return value
    return scrub(before) == scrub(after)


def restore_files(project: Path, before: dict, permitted, folder: Path):
    """Capture all files before considering restoration; never mask a mismatch.

    No writes to the checkout occur unless the complete observed change set is
    allowed. Each file is checked again immediately before its bounded write.
    """
    folder.mkdir(parents=True, exist_ok=False)
    report = {"kind": "R02GeneratedInputRestoration", "result": "Failed", "files": []}
    captured = {}
    try:
        for i, (relative, original) in enumerate(before.items()):
            path = project / relative
            original_path = folder / (str(i).zfill(3) + ".before")
            original_path.write_bytes(original)
            row = {"path": relative, "before": binding(original_path), "allowed": False}
            report["files"].append(row)
            # This also refuses links and missing regular files.
            binding(path)
            current = path.read_bytes()
            after_path = folder / (str(i).zfill(3) + ".after")
            after_path.write_bytes(current)
            row["after"] = binding(after_path)
            row["allowed"] = bool(permitted(relative, original, current))
            captured[relative] = current
        require(all(r["allowed"] for r in report["files"]), "Unexpected generated-input mutation; checkout not overwritten")
        for relative, current in captured.items():
            require((project / relative).read_bytes() == current, "Concurrent change before restoration; checkout not overwritten")
        for row in report["files"]:
            relative = row["path"]; path = project / relative
            require(path.read_bytes() == captured[relative], "Concurrent change during restoration; remaining writes stopped")
            if captured[relative] != before[relative]:
                path.write_bytes(before[relative])
            require(path.read_bytes() == before[relative], "Generated input not restored exactly")
            row["restored"] = binding(path)
        report["result"] = "Passed"
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    write(folder / "restoration.json", report)
    require(report["result"] == "Passed", report.get("error", "Restoration failed"))
    return report


def with_recovery(action, recovery, receipt: Path):
    """Record action and recovery independently; neither can overwrite the other."""
    record = {"kind": "R02BuildRecovery", "result": "Failed", "actionResult": "Failed", "recoveryResult": "Failed"}
    value = None
    try:
        value = action()
        record["actionResult"] = "Passed"
    except Exception as error:
        record["actionError"] = type(error).__name__ + ": " + str(error)
    try:
        recovery()
        record["recoveryResult"] = "Passed"
    except Exception as error:
        record["recoveryError"] = type(error).__name__ + ": " + str(error)
    if record["actionResult"] == record["recoveryResult"] == "Passed":
        record["result"] = "Passed"
    write(receipt, record)
    require(record["result"] == "Passed", "Build/recovery failure: " + str(record))
    return value
