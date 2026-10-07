"""Stream and authenticate the regular members of an H1 evidence archive."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import tarfile
import unicodedata
from typing import Any, Iterable


class VerificationError(RuntimeError):
    """Raised when an input cannot be authenticated under the H1 contract."""


HASH_RE = r"[0-9a-f]{64}"
CHUNK_SIZE = 1024 * 1024
MAX_CAPTURE_BYTES = 512 * 1024 * 1024
REPORT_NAME = "members-audit.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    require(path.is_file() and not path.is_symlink(), f"Missing or symlinked JSON: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object)
    except VerificationError:
        raise
    except (OSError, UnicodeError, ValueError) as error:
        raise VerificationError(f"Invalid JSON {path}: {error}") from error


def read_json_bytes(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    except VerificationError:
        raise
    except (UnicodeError, ValueError) as error:
        raise VerificationError(f"Invalid JSON {label}: {error}") from error


def _read_file_bytes(path: Path, *, maximum: int = MAX_CAPTURE_BYTES) -> bytes:
    require(path.is_file() and not path.is_symlink(), f"Input is not a regular file: {path}")
    data = bytearray()
    try:
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                data.extend(chunk)
                require(len(data) <= maximum, f"Input exceeds capture limit: {path}")
    except VerificationError:
        raise
    except OSError as error:
        raise VerificationError(f"Cannot read {path}: {error}") from error
    return bytes(data)


def sha256_file(path: Path) -> tuple[str, int]:
    require(path.is_file() and not path.is_symlink(), f"Input is not a regular file: {path}")
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
    except OSError as error:
        raise VerificationError(f"Cannot read {path}: {error}") from error
    return digest.hexdigest(), size


def _hash(value: Any, label: str) -> str:
    require(type(value) is str and re.fullmatch(HASH_RE, value) is not None,
            f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _nonnegative_integer(value: Any, label: str) -> int:
    require(type(value) is int and not isinstance(value, bool) and value >= 0,
            f"{label} must be a non-negative integer")
    return value


def _canonical_input_path(path_value: Any, base: Path, label: str) -> Path:
    require(type(path_value) is str and path_value, f"{label}.path must be a non-empty string")
    path = Path(path_value)
    if not path.is_absolute():
        path = base / path
    current = path
    while current != current.parent:
        require(not current.is_symlink(), f"Symlinked {label}.path is not allowed: {current}")
        current = current.parent
    # Resolve is used only to compare an already existing input; no output path is followed.
    try:
        return path.resolve(strict=True)
    except OSError as error:
        raise VerificationError(f"Cannot resolve {label}.path: {path}: {error}") from error


def _binding(value: Any, base: Path, label: str, *, size_required: bool) -> dict[str, Any]:
    require(type(value) is dict, f"{label} must be an object")
    path = _canonical_input_path(value.get("path"), base, label)
    expected_hash = _hash(value.get("sha256"), f"{label}.sha256")
    result: dict[str, Any] = {"path": path, "expectedSha256": expected_hash}
    if size_required:
        result["expectedSizeBytes"] = _nonnegative_integer(value.get("sizeBytes"), f"{label}.sizeBytes")
    elif "sizeBytes" in value:
        result["expectedSizeBytes"] = _nonnegative_integer(value["sizeBytes"], f"{label}.sizeBytes")
    return result


def _input_map(data: Any, map_path: Path) -> dict[str, Any]:
    require(type(data) is dict, "Input map must be a JSON object")
    require(data.get("schemaVersion") == 1, "Unsupported input-map schemaVersion")
    base = map_path.parent.resolve()
    archive_value = data.get("archive")
    if archive_value is None:
        archive_value = {"path": data.get("archivePath"), "sha256": data.get("archiveSha256")}
        if "archiveSizeBytes" in data:
            archive_value["sizeBytes"] = data["archiveSizeBytes"]
    index_value = data.get("index")
    if index_value is None:
        index_value = {"path": data.get("indexPath"), "sha256": data.get("indexSha256")}
        if "indexSizeBytes" in data:
            index_value["sizeBytes"] = data["indexSizeBytes"]
    archive = _binding(archive_value, base, "archive", size_required=False)
    index = _binding(index_value, base, "index", size_required=False)
    tools: list[dict[str, Any]] = []
    declared_tools = data.get("tools", [])
    require(type(declared_tools) is list, "tools must be an array")
    for position, item in enumerate(declared_tools):
        binding = _binding(item, base, f"tools[{position}]", size_required=False)
        binding["name"] = item.get("name", f"tool-{position}")
        require(type(binding["name"]) is str and binding["name"], f"tools[{position}].name must be non-empty")
        tools.append(binding)
    return {"archive": archive, "index": index, "tools": tools}


def _safe_member_name(name: Any) -> tuple[str, str]:
    require(type(name) is str and name, "Archive member has an empty or non-string name")
    require("\x00" not in name and "\\" not in name, f"Unsafe archive member path: {name!r}")
    require(not name.startswith("/"), f"Absolute archive member path: {name!r}")
    # PAX names are POSIX paths. Empty, dot, and parent components are rejected so a
    # later extractor cannot assign a different meaning to the authenticated name.
    parts = name.split("/")
    require(all(part not in ("", ".", "..") for part in parts),
            f"Non-canonical archive member path: {name!r}")
    normalized = posixpath.normpath(name)
    nfc = unicodedata.normalize("NFC", name)
    require(normalized == name and nfc == name,
            f"Non-canonical archive member path: {name!r}")
    require(PurePosixPath(name).is_relative_to(PurePosixPath(".")),
            f"Unsafe archive member path: {name!r}")
    return name, nfc


def _index_entries(index: Any) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    require(type(index) is dict, "Index must be a JSON object")
    require(index.get("schemaVersion") == 1, "Unsupported evidence index schemaVersion")
    rows = index.get("files")
    require(type(rows) is list, "Index files must be an array")
    expected_count = _nonnegative_integer(index.get("memberCount"), "Index memberCount")
    require(expected_count == len(rows), "Index memberCount differs from files length")
    entries: dict[str, dict[str, Any]] = {}
    normalized: dict[str, str] = {}
    for position, row in enumerate(rows):
        require(type(row) is dict, f"Index files[{position}] must be an object")
        member, normalized_name = _safe_member_name(row.get("archiveMember"))
        require(member not in entries, f"Duplicate index archiveMember: {member}")
        require(normalized_name not in normalized, f"Normalized index member conflict: {member}")
        normalized[normalized_name] = member
        entries[member] = {
            "sizeBytes": _nonnegative_integer(row.get("sizeBytes"), f"Index files[{position}].sizeBytes"),
            "sha256": _hash(row.get("sha256"), f"Index files[{position}].sha256"),
        }
    return entries, {"schemaVersion": index["schemaVersion"], "memberCount": expected_count}


def _member_type(member: tarfile.TarInfo) -> str:
    if member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.isreg():
        return "regular"
    if member.isdir():
        return "directory"
    if member.issym():
        return "symlink"
    if member.islnk():
        return "hardlink"
    if member.isdev() or member.isfifo() or member.ischr() or member.isblk():
        return "device"
    return f"type-{member.type!r}"


def _stream_members(archive_bytes: bytes, archive_label: Path) -> tuple[dict[str, dict[str, Any]], int]:
    observed: dict[str, dict[str, Any]] = {}
    normalized: dict[str, str] = {}
    count = 0
    try:
        # Parse the immutable bytes whose digest was authenticated. This avoids a
        # replacement between hashing and parsing the archive path.
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r|gz", errorlevel=2) as stream:
            while True:
                member = stream.next()
                if member is None:
                    break
                # tarfile applies PAX path/size metadata to TarInfo. Reject link and
                # sparse metadata explicitly rather than authenticating hidden semantics.
                member_name, normalized_name = _safe_member_name(member.name)
                require(member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.isreg(),
                        f"Archive member is not a regular file ({_member_type(member)}): {member_name}")
                require("linkpath" not in member.pax_headers and
                        not any(key.startswith("GNU.sparse.") for key in member.pax_headers),
                        f"Unsupported PAX link/sparse metadata: {member_name}")
                require(member_name not in observed, f"Duplicate archive member: {member_name}")
                require(normalized_name not in normalized,
                        f"Normalized archive member conflict: {member_name}")
                normalized[normalized_name] = member_name
                size = _nonnegative_integer(member.size, f"Archive member {member_name}.size")
                digest = hashlib.sha256()
                read_size = 0
                json_bytes = bytearray() if member_name.casefold().endswith(".json") else None
                extracted = stream.extractfile(member)
                require(extracted is not None, f"Cannot stream archive member: {member_name}")
                while True:
                    chunk = extracted.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    digest.update(chunk)
                    if json_bytes is not None:
                        json_bytes.extend(chunk)
                    read_size += len(chunk)
                require(read_size == size,
                        f"Archive member {member_name} read size differs: {read_size} != {size}")
                if json_bytes is not None:
                    try:
                        json.loads(bytes(json_bytes), object_pairs_hook=_unique_object)
                    except VerificationError:
                        raise
                    except (UnicodeError, ValueError) as error:
                        raise VerificationError(f"Invalid JSON archive member {member_name}: {error}") from error
                observed[member_name] = {"sizeBytes": size, "sha256": digest.hexdigest()}
                count += 1
    except VerificationError:
        raise
    except (OSError, tarfile.TarError, EOFError, ValueError) as error:
        raise VerificationError(f"Cannot stream archive {archive_label}: {error}") from error
    return observed, count


def _tool_observations(bindings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for binding in bindings:
        observed_hash, observed_size = sha256_file(binding["path"])
        expected_hash = binding.get("expectedSha256")
        if expected_hash is not None:
            require(observed_hash == expected_hash,
                    f"Tool hash mismatch for {binding['name']}: {observed_hash} != {expected_hash}")
        expected_size = binding.get("expectedSizeBytes")
        if expected_size is not None:
            require(observed_size == expected_size,
                    f"Tool size mismatch for {binding['name']}: {observed_size} != {expected_size}")
        result.append({"name": binding["name"], "path": str(binding["path"]),
                       "expectedSha256": expected_hash, "observedSha256": observed_hash,
                       "expectedSizeBytes": binding.get("expectedSizeBytes"),
                       "observedSizeBytes": observed_size})
    return result


def authenticate_members(input_map_path: Path, output_root: Path) -> dict[str, Any]:
    """Authenticate one archive/index binding and return the report object.

    The archive is read in tar streaming mode. No member is extracted to disk and
    no archive content is interpreted as executable code.
    """
    input_map_path = Path(input_map_path).resolve(strict=True)
    output_root = Path(output_root)
    require(output_root.is_absolute(), "output-root must be an absolute path")
    output_root = output_root.resolve(strict=False)
    require(not output_root.exists() and not output_root.is_symlink(),
            f"output-root must be a new directory: {output_root}")
    output_root.mkdir(parents=True, exist_ok=False)
    archive: dict[str, Any] | None = None
    index: dict[str, Any] | None = None
    tools: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "operation": "members",
        "status": "FAIL",
        "inputMap": {"path": str(input_map_path)},
        "inputs": {},
        "tools": [],
    }
    try:
        parsed = _input_map(read_json(input_map_path), input_map_path)
        archive, index, tools = parsed["archive"], parsed["index"], parsed["tools"]
        # Always record the exact two source files that implement this operation;
        # input-map tool bindings can additionally pin their expected hashes.
        known_tool_paths = {Path(item["path"]).resolve() for item in tools}
        for name, path in (("audit-h1-evidence.py", Path(__file__).with_name("audit-h1-evidence.py").resolve()),
                           ("h1_evidence_members.py", Path(__file__).resolve())):
            if path not in known_tool_paths:
                tools.append({"name": name, "path": path})
        # Capture each authenticated input once. Parsing below uses these exact
        # bytes, so a path replacement cannot turn an old digest into a new PASS.
        archive_bytes = _read_file_bytes(archive["path"])
        index_bytes = _read_file_bytes(index["path"])
        archive_hash, archive_size = hashlib.sha256(archive_bytes).hexdigest(), len(archive_bytes)
        index_hash, index_size = hashlib.sha256(index_bytes).hexdigest(), len(index_bytes)
        report["inputs"] = {
            "archive": {"path": str(archive["path"]), "expectedSha256": archive["expectedSha256"],
                        "observedSha256": archive_hash, "expectedSizeBytes": archive.get("expectedSizeBytes"),
                        "observedSizeBytes": archive_size},
            "index": {"path": str(index["path"]), "expectedSha256": index["expectedSha256"],
                      "observedSha256": index_hash, "expectedSizeBytes": index.get("expectedSizeBytes"),
                      "observedSizeBytes": index_size},
        }
        require(archive_hash == archive["expectedSha256"], "Archive SHA-256 does not match input map")
        if archive.get("expectedSizeBytes") is not None:
            require(archive_size == archive["expectedSizeBytes"], "Archive size does not match input map")
        require(index_hash == index["expectedSha256"], "Index SHA-256 does not match input map")
        if index.get("expectedSizeBytes") is not None:
            require(index_size == index["expectedSizeBytes"], "Index size does not match input map")
        report["tools"] = _tool_observations(tools)
        index_data = read_json_bytes(index_bytes, str(index["path"]))
        expected, index_shape = _index_entries(index_data)
        archive_path_in_index = index_data.get("archivePath")
        if archive_path_in_index is not None:
            require(type(archive_path_in_index) is str and archive_path_in_index,
                    "Index archivePath must be a non-empty string")
        if "archiveSha256" in index_data:
            require(index_data["archiveSha256"] == archive_hash, "Index archiveSha256 differs from archive")
        if "archiveSizeBytes" in index_data:
            require(index_data["archiveSizeBytes"] == archive_size, "Index archiveSizeBytes differs from archive")
        observed, observed_count = _stream_members(archive_bytes, archive["path"])
        report["expected"] = {"memberCount": index_shape["memberCount"],
                              "members": {name: expected[name] for name in sorted(expected)}}
        report["observed"] = {"memberCount": observed_count,
                              "members": {name: observed[name] for name in sorted(observed)}}
        expected_names, observed_names = set(expected), set(observed)
        require(expected_names == observed_names,
                f"Archive/index member sets differ: missing={sorted(expected_names - observed_names)}, "
                f"unindexed={sorted(observed_names - expected_names)}")
        require(observed_count > 0, "Zero-member archive/index is not acceptable")
        for name in sorted(expected_names):
            require(observed[name] == expected[name],
                    f"Archive member {name} size/hash differs from index")
        require(observed_count == index_shape["memberCount"], "Observed member count differs from index")
        report["status"] = "PASS"
        report["message"] = "Archive regular members exactly match the authenticated index."
    except Exception as error:
        report["error"] = str(error)
        if archive is not None and "archive" not in report["inputs"]:
            report["inputs"]["archive"] = {"path": str(archive["path"]),
                                            "expectedSha256": archive["expectedSha256"]}
        if index is not None and "index" not in report["inputs"]:
            report["inputs"]["index"] = {"path": str(index["path"]),
                                          "expectedSha256": index["expectedSha256"]}
        if tools and not report["tools"]:
            report["tools"] = [{"name": item["name"], "path": str(item["path"]),
                                "expectedSha256": item.get("expectedSha256"),
                                "observedSha256": None} for item in tools]
    report_path = output_root / REPORT_NAME
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] != "PASS":
        raise VerificationError(report["error"])
    return report
