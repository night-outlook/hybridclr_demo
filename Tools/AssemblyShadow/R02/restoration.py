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


GENERATED_LINK = "Assets/HybridCLRGenerate/link.xml"
DIAGNOSTIC_LINK_TYPES = frozenset((
    "System.Array", "System.Byte", "System.CodeDom.Compiler.GeneratedCodeAttribute",
    "System.ComponentModel.EditorBrowsableAttribute", "System.ComponentModel.EditorBrowsableState",
    "System.Diagnostics.DebuggableAttribute", "System.Diagnostics.DebuggableAttribute/DebuggingModes",
    "System.Object", "System.Runtime.CompilerServices.CompilationRelaxationsAttribute",
    "System.Runtime.CompilerServices.CompilerGeneratedAttribute",
    "System.Runtime.CompilerServices.RuntimeCompatibilityAttribute", "System.Runtime.CompilerServices.RuntimeHelpers",
    "System.RuntimeFieldHandle", "System.ValueType",
))


def generated_link_allowed(before: bytes, after: bytes):
    """Only the exact known netstandard preservation expansion from batch F.

    A different graph needs review; well-formed arbitrary linker XML is not an
    authorization to overwrite concurrent/user changes. Originals are restored
    byte-for-byte, including BOM/newlines, by restore_files.
    """
    import xml.etree.ElementTree as ET
    if before == after:
        return True
    def shape(raw):
        require(len(raw) <= 65536 and b"<!" not in raw, "Unexpected generated linker declaration")
        tree = ET.fromstring(raw)
        require(tree.tag == "linker" and not tree.attrib and not (tree.text or "").strip(), "Unexpected linker root")
        if len(tree) == 0:
            return frozenset()
        require(len(tree) == 1, "Unexpected linker assembly count")
        assembly = tree[0]
        require(assembly.tag == "assembly" and assembly.attrib == {"fullname": "netstandard"} and
                not (assembly.text or "").strip() and not (assembly.tail or "").strip(), "Unexpected linker assembly")
        names = []
        for item in assembly:
            require(item.tag == "type" and set(item.attrib) == {"fullname", "preserve"} and
                    item.attrib["preserve"] == "all" and len(item) == 0 and
                    not (item.text or "").strip() and not (item.tail or "").strip(), "Unexpected linker type")
            names.append(item.attrib["fullname"])
        require(len(names) == len(set(names)), "Duplicate linker type")
        return frozenset(names)
    try:
        return shape(before) == frozenset() and shape(after) == DIAGNOSTIC_LINK_TYPES
    except (ValueError, ET.ParseError):
        return False


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
