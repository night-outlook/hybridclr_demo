"""Resolve exact capture references in authenticated H1 evidence JSON members."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
from typing import Any

from h1_evidence_members import (
    CHUNK_SIZE,
    MAX_CAPTURE_BYTES,
    REPORT_NAME as MEMBERS_REPORT_NAME,
    VerificationError,
    _member_type,
    _safe_member_name,
    _unique_object,
    read_json_bytes,
)


REPORT_NAME = "references-audit.json"
HASH_RE = r"[0-9a-f]{64}"
PATH_KEYS = frozenset({
    "path", "rawpath", "file", "filepath", "sourcepath", "outputpath",
    "assetpath", "archivepath", "receiptpath", "binarypath", "rootpath",
    "paths", "rawpaths", "files", "filepaths", "sourcepaths", "outputpaths",
})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _hash(value: Any, label: str) -> str:
    require(type(value) is str and re.fullmatch(HASH_RE, value) is not None,
            f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _path_binding(value: Any, base: Path, label: str) -> dict[str, Any]:
    require(type(value) is dict, f"{label} must be an object")
    path_value = value.get("path")
    require(type(path_value) is str and path_value, f"{label}.path must be a non-empty string")
    path = Path(path_value)
    if not path.is_absolute():
        path = base / path
    current = path
    while current != current.parent:
        require(not current.is_symlink(), f"Symlinked {label}.path is not allowed: {current}")
        current = current.parent
    try:
        path = path.resolve(strict=True)
    except OSError as error:
        raise VerificationError(f"Cannot resolve {label}.path: {path}: {error}") from error
    result = {"path": path, "expectedSha256": _hash(value.get("sha256"), f"{label}.sha256")}
    if "sizeBytes" in value:
        size = value["sizeBytes"]
        require(type(size) is int and not isinstance(size, bool) and size >= 0,
                f"{label}.sizeBytes must be a non-negative integer")
        result["expectedSizeBytes"] = size
    return result


def _read_capture(path: Path, label: str) -> bytes:
    require(path.is_file() and not path.is_symlink(), f"Input is not a regular file: {path}")
    captured = bytearray()
    try:
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                captured.extend(chunk)
                require(len(captured) <= MAX_CAPTURE_BYTES, f"{label} exceeds capture limit")
    except VerificationError:
        raise
    except OSError as error:
        raise VerificationError(f"Cannot read {label}: {error}") from error
    return bytes(captured)


def _parse_input_map(data: Any, map_path: Path) -> dict[str, Any]:
    require(type(data) is dict and data.get("schemaVersion") == 1,
            "Unsupported references input-map schemaVersion")
    base = map_path.parent.resolve()
    archive = _path_binding(data.get("archive"), base, "archive")
    index = _path_binding(data.get("index"), base, "index")
    prior_value = data.get("membersAudit", data.get("priorMembersAudit"))
    prior = _path_binding(prior_value, base, "membersAudit")
    tools = []
    declared = data.get("tools", [])
    require(type(declared) is list, "tools must be an array")
    for position, item in enumerate(declared):
        binding = _path_binding(item, base, f"tools[{position}]")
        binding["name"] = item.get("name", f"tool-{position}")
        require(type(binding["name"]) is str and binding["name"],
                f"tools[{position}].name must be non-empty")
        tools.append(binding)
    return {"archive": archive, "index": index, "membersAudit": prior, "tools": tools}


def _tool_report(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in bindings:
        data = _read_capture(item["path"], f"tool {item['name']}")
        observed = hashlib.sha256(data).hexdigest()
        expected = item.get("expectedSha256")
        if expected is not None:
            require(observed == expected, f"Tool hash mismatch for {item['name']}")
        expected_size = item.get("expectedSizeBytes")
        if expected_size is not None:
            require(len(data) == expected_size, f"Tool size mismatch for {item['name']}")
        result.append({"name": item["name"], "path": str(item["path"]),
                       "expectedSha256": expected, "observedSha256": observed,
                       "expectedSizeBytes": expected_size, "observedSizeBytes": len(data)})
    return result


def _index_rows(index: Any, prior_members: dict[str, dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    require(type(index) is dict and index.get("schemaVersion") == 1,
            "Unsupported evidence index schemaVersion")
    rows = index.get("files")
    require(type(rows) is list, "Evidence index files must be an array")
    count = index.get("memberCount")
    require(type(count) is int and not isinstance(count, bool) and count == len(rows),
            "Evidence index memberCount differs from files length")
    require(count > 0, "Evidence index has zero entries")
    raw_to_member: dict[str, str] = {}
    member_to_raw: dict[str, str] = {}
    for position, row in enumerate(rows):
        require(type(row) is dict, f"Evidence index files[{position}] must be an object")
        raw_path = row.get("rawPath")
        require(type(raw_path) is str and raw_path, f"Evidence index files[{position}].rawPath is invalid")
        member, _ = _safe_member_name(row.get("archiveMember"))
        require(member in prior_members, f"Index archiveMember is absent from prior members audit: {member}")
        row_hash = _hash(row.get("sha256"), f"Evidence index files[{position}].sha256")
        row_size = row.get("sizeBytes")
        require(type(row_size) is int and not isinstance(row_size, bool) and row_size >= 0,
                f"Evidence index files[{position}].sizeBytes is invalid")
        require(prior_members[member] == {"sizeBytes": row_size, "sha256": row_hash},
                f"Index digest/size differs from prior members audit: {member}")
        require(raw_path not in raw_to_member, f"Duplicate index rawPath: {raw_path}")
        require(member not in member_to_raw, f"Duplicate index archiveMember: {member}")
        raw_to_member[raw_path] = member
        member_to_raw[member] = raw_path
    return raw_to_member, member_to_raw


def _pointer(parent: str, key: Any) -> str:
    token = str(key).replace("~", "~0").replace("/", "~1")
    return parent + "/" + token


def _looks_like_locator(key: str, value: str) -> bool:
    folded = key.casefold()
    field = folded.rsplit(".", 1)[-1]
    if field not in PATH_KEYS and not field.endswith("path") and not field.endswith("file"):
        return False
    if not value:
        return False
    if value.startswith(("/", "\\", "./", "../")) or re.match(r"^[A-Za-z]:[\\/]", value):
        return True
    if "/" in value or "\\" in value:
        return True
    return "." in Path(value).name and not value.startswith(".")


def _scan(value: Any, source_member: str, raw_to_member: dict[str, str], member_to_raw: dict[str, str],
          pointer: str = "", context_field: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    internal: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    ignored = 0

    def classify(child: str, child_pointer: str, field: str) -> None:
        # Exact identities are authoritative even when the surrounding JSON key
        # is a business field such as "note" or an array index.
        declared_field = field.casefold().rsplit(".", 1)[-1]
        is_declared_locator = (declared_field in PATH_KEYS or declared_field.endswith("path") or
                               declared_field.endswith("file"))
        if child in raw_to_member:
            internal.append({"member": source_member, "jsonPointer": child_pointer, "field": field,
                             "value": child, "archiveMember": raw_to_member[child],
                             "resolution": "ExactRawPath"})
        elif child in member_to_raw:
            internal.append({"member": source_member, "jsonPointer": child_pointer, "field": field,
                             "value": child, "archiveMember": child,
                             "resolution": "ExactArchiveMember"})
        elif is_declared_locator and child:
            unresolved.append({"member": source_member, "jsonPointer": child_pointer, "field": field,
                               "value": child, "classification": "PendingExternalVerification"})
        elif is_declared_locator:
            ignored_nonlocal[0] += 1

    ignored_nonlocal = [0]
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = _pointer(pointer, key)
            if isinstance(child, str):
                classify(child, child_pointer, str(key))
                continue
            child_internal, child_unresolved, child_ignored = _scan(
                child, source_member, raw_to_member, member_to_raw, child_pointer, str(key))
            internal.extend(child_internal)
            unresolved.extend(child_unresolved)
            ignored += child_ignored
    elif isinstance(value, list):
        for position, child in enumerate(value):
            child_pointer = _pointer(pointer, position)
            if isinstance(child, str):
                classify(child, child_pointer, context_field or str(position))
                continue
            child_internal, child_unresolved, child_ignored = _scan(
                child, source_member, raw_to_member, member_to_raw, child_pointer, context_field)
            internal.extend(child_internal)
            unresolved.extend(child_unresolved)
            ignored += child_ignored
    return internal, unresolved, ignored + ignored_nonlocal[0]


def _archive_json(archive_bytes: bytes, archive_path: Path, prior_members: dict[str, dict[str, Any]]) -> dict[str, Any]:
    json_members: dict[str, Any] = {}
    observed: dict[str, dict[str, Any]] = {}
    normalized: dict[str, str] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r|gz", errorlevel=2) as stream:
            while True:
                member = stream.next()
                if member is None:
                    break
                name, normalized_name = _safe_member_name(member.name)
                require(member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.isreg(),
                        f"Archive member is not a regular file ({_member_type(member)}): {name}")
                require(name not in observed, f"Duplicate archive member: {name}")
                require(normalized_name not in normalized, f"Normalized archive member conflict: {name}")
                normalized[normalized_name] = name
                extracted = stream.extractfile(member)
                require(extracted is not None, f"Cannot stream archive member: {name}")
                data = bytearray()
                digest = hashlib.sha256()
                while True:
                    chunk = extracted.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    data.extend(chunk)
                    digest.update(chunk)
                record = {"sizeBytes": len(data), "sha256": digest.hexdigest()}
                require(name in prior_members and prior_members[name] == record,
                        f"Archive member differs from prior members audit: {name}")
                observed[name] = record
                if name.casefold().endswith(".json"):
                    json_members[name] = read_json_bytes(bytes(data), name)
    except VerificationError:
        raise
    except (OSError, tarfile.TarError, EOFError, ValueError) as error:
        raise VerificationError(f"Cannot stream archive {archive_path}: {error}") from error
    require(set(observed) == set(prior_members), "Archive member set differs from prior members audit")
    return json_members


def authenticate_references(input_map_path: Path, output_root: Path) -> dict[str, Any]:
    input_map_path = Path(input_map_path).resolve(strict=True)
    output_root = Path(output_root)
    require(output_root.is_absolute(), "output-root must be an absolute path")
    require(not output_root.exists() and not output_root.is_symlink(),
            f"output-root must be a new directory: {output_root}")
    output_root = output_root.resolve(strict=False)
    output_root.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {"schemaVersion": 1, "operation": "references", "status": "FAIL",
                              "inputMap": {"path": str(input_map_path)}, "inputs": {}, "tools": [],
                              "scanRules": {"fieldNames": sorted(PATH_KEYS),
                                            "pathLikeValues": "absolute Unix/Windows, relative with slash, or filename with extension",
                                            "resolution": "exact rawPath or exact archiveMember only",
                                            "externalClassification": "PendingExternalVerification"}}
    parsed: dict[str, Any] | None = None
    try:
        parsed = _parse_input_map(read_json_bytes(_read_capture(input_map_path, "input map"), str(input_map_path)), input_map_path)
        archive, index, prior, tools = parsed["archive"], parsed["index"], parsed["membersAudit"], parsed["tools"]
        for name, path in (("audit-h1-evidence-references.py", Path(__file__).with_name("audit-h1-evidence-references.py").resolve()),
                           ("h1_evidence_references.py", Path(__file__).resolve())):
            if not any(Path(item["path"]).resolve() == path for item in tools):
                tools.append({"name": name, "path": path})
        archive_bytes = _read_capture(archive["path"], "archive")
        index_bytes = _read_capture(index["path"], "index")
        prior_bytes = _read_capture(prior["path"], "members audit")
        archive_hash, index_hash, prior_hash = (hashlib.sha256(data).hexdigest() for data in (archive_bytes, index_bytes, prior_bytes))
        report["inputs"] = {
            "archive": {"path": str(archive["path"]), "expectedSha256": archive["expectedSha256"],
                        "observedSha256": archive_hash, "expectedSizeBytes": archive.get("expectedSizeBytes"),
                        "observedSizeBytes": len(archive_bytes)},
            "index": {"path": str(index["path"]), "expectedSha256": index["expectedSha256"],
                      "observedSha256": index_hash, "expectedSizeBytes": index.get("expectedSizeBytes"),
                      "observedSizeBytes": len(index_bytes)},
            "membersAudit": {"path": str(prior["path"]), "expectedSha256": prior["expectedSha256"],
                             "observedSha256": prior_hash, "expectedSizeBytes": prior.get("expectedSizeBytes"),
                             "observedSizeBytes": len(prior_bytes)},
        }
        require(archive_hash == archive["expectedSha256"], "Archive SHA-256 does not match input map")
        require(index_hash == index["expectedSha256"], "Index SHA-256 does not match input map")
        require(prior_hash == prior["expectedSha256"], "Members audit SHA-256 does not match input map")
        for binding, data in ((archive, archive_bytes), (index, index_bytes), (prior, prior_bytes)):
            if binding.get("expectedSizeBytes") is not None:
                require(len(data) == binding["expectedSizeBytes"], "Input size does not match input map")
        report["tools"] = _tool_report(tools)
        index_data = read_json_bytes(index_bytes, str(index["path"]))
        prior_data = read_json_bytes(prior_bytes, str(prior["path"]))
        require(prior_data.get("operation") == "members" and prior_data.get("status") == "PASS",
                "Prior members audit is not a PASS report")
        prior_inputs = prior_data.get("inputs")
        require(type(prior_inputs) is dict, "Prior members audit inputs are missing")
        for key, digest in (("archive", archive_hash), ("index", index_hash)):
            item = prior_inputs.get(key)
            require(type(item) is dict and item.get("observedSha256") == digest,
                    f"Prior members audit {key} snapshot differs from current input")
        prior_observed = prior_data.get("observed", {}).get("members")
        require(type(prior_observed) is dict and prior_observed, "Prior members audit has no authenticated members")
        prior_members = {name: {"sizeBytes": row.get("sizeBytes"), "sha256": row.get("sha256")}
                         for name, row in prior_observed.items()}
        raw_to_member, member_to_raw = _index_rows(index_data, prior_members)
        json_members = _archive_json(archive_bytes, archive["path"], prior_members)
        internal, unresolved, ignored = [], [], 0
        for member_name, value in json_members.items():
            found_internal, found_unresolved, found_ignored = _scan(value, member_name, raw_to_member, member_to_raw)
            internal.extend(found_internal)
            unresolved.extend(found_unresolved)
            ignored += found_ignored
        report["expected"] = {"indexedMemberCount": len(prior_members), "indexedRawPathCount": len(raw_to_member)}
        report["observed"] = {"jsonMemberCount": len(json_members), "internalReferences": internal,
                              "unresolvedReferences": unresolved, "ignoredBusinessValues": ignored}
        report["status"] = "PASS"
        report["message"] = "Exact capture references resolved; external bytes remain pending verification."
    except Exception as error:
        report["error"] = str(error)
        if parsed:
            for key in ("archive", "index", "membersAudit"):
                item = parsed.get(key)
                if item is not None and key not in report["inputs"]:
                    report["inputs"][key] = {"path": str(item["path"]), "expectedSha256": item["expectedSha256"],
                                              "observedSha256": None}
            if not report["tools"]:
                report["tools"] = [{"name": item["name"], "path": str(item["path"]),
                                    "expectedSha256": item.get("expectedSha256"), "observedSha256": None}
                                   for item in parsed.get("tools", [])]
    (output_root / REPORT_NAME).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] != "PASS":
        raise VerificationError(report["error"])
    return report
