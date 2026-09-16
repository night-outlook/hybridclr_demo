"""Bounded failure evidence owned by one newly created capture attempt.

This journal is diagnostic-only. It cannot create a build receipt, alter an old
attempt, approve a macro domain, or substitute for compiler/PCH execution.

Large generated native sources are retained as reversible, content-addressed
compressed blobs. Raw SHA-256/length remain the source identity; compression is
only a storage representation. Semantic inputs such as requests, graphs, PCHs,
headers, response files, and plists remain raw unless the caller explicitly
requests compress-if-smaller storage.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import traceback
import uuid
import zlib

MAX_FILE_BYTES = 64 * 1024 * 1024
# The previous 256 MiB raw aggregate ceiling was below the measured real Apple
# graph. Keep logical source volume and physical evidence storage independently
# bounded so compression never changes source identity or becomes an allowlist.
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
MAX_STORED_BYTES = 512 * 1024 * 1024
MAX_FILES = 4096
COMPRESS_LEVEL = 1
ENCODING_RAW = "raw-v1"
ENCODING_ZLIB = "zlib-v1"
SOURCE_SUFFIXES = frozenset((".c", ".cpp", ".cc", ".cxx", ".m", ".mm"))


def encode(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def new_file(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


class RetentionError(ValueError):
    pass


def _canonical_retained(path: Path) -> Path:
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise RetentionError("Retained evidence path must be absolute and not symlinked")
    resolved = path.resolve(strict=True)
    if path != resolved or not path.is_file():
        raise RetentionError("Retained evidence path must be a canonical file")
    return path


def _decode_row(row: dict) -> bytes:
    if row.get("status") != "Retained":
        raise RetentionError("Only retained rows have evidence bytes")
    raw_bytes = row.get("bytes")
    raw_sha = row.get("sha256")
    stored_bytes = row.get("retainedBytes")
    stored_sha = row.get("retainedSha256")
    encoding = row.get("retainedEncoding")
    if (type(raw_bytes) is not int or not 0 <= raw_bytes <= MAX_FILE_BYTES or
            type(stored_bytes) is not int or stored_bytes < 0 or
            type(raw_sha) is not str or len(raw_sha) != 64 or
            type(stored_sha) is not str or len(stored_sha) != 64):
        raise RetentionError("Malformed retained evidence metadata")
    path = _canonical_retained(Path(row.get("retainedPath", "")))
    if path.stat().st_size != stored_bytes:
        raise RetentionError("Retained evidence stored length differs")
    stored = path.read_bytes()
    if hashlib.sha256(stored).hexdigest() != stored_sha:
        raise RetentionError("Retained evidence stored hash differs")
    if encoding == ENCODING_RAW:
        raw = stored
    elif encoding == ENCODING_ZLIB:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(stored, raw_bytes + 1)
        if decoder.unconsumed_tail or len(raw) > raw_bytes:
            raise RetentionError("Retained compressed evidence expands beyond declared raw length")
        raw += decoder.flush()
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise RetentionError("Retained compressed evidence stream is incomplete or has trailing bytes")
    else:
        raise RetentionError("Unsupported retained evidence encoding")
    if len(raw) != raw_bytes or hashlib.sha256(raw).hexdigest() != raw_sha:
        raise RetentionError("Retained evidence raw identity differs")
    return raw


def load_retained(row: dict) -> bytes:
    """Return authenticated original bytes from one retained inventory row."""
    return _decode_row(row)


def _json_line(raw: bytes) -> dict:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise RetentionError("Duplicate retention inventory key: " + key)
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=unique)
    except (ValueError, UnicodeError) as error:
        raise RetentionError("Invalid retention inventory JSON: " + str(error)) from error


def verify_attempt_store(root: Path) -> dict:
    """Independently authenticate a retained content store from disk."""
    root = Path(root)
    if not root.is_absolute() or root != root.resolve(strict=True) or any(
            p.is_symlink() for p in (root, *root.parents)):
        raise RetentionError("Attempt root is not canonical")
    state_path = root / "attempt-state.json"
    inventory = root / "attempt-inputs.jsonl"
    inputs = root / "attempt-inputs"
    if not state_path.is_file() or not inventory.is_file() or not inputs.is_dir():
        raise RetentionError("Incomplete attempt retention store")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rows = []
    for line in inventory.read_bytes().splitlines():
        if line:
            rows.append(_json_line(line))
    if state.get("retainedInputCount") != len(rows):
        raise RetentionError("Retention observation count differs from state")
    unique_raw = {}
    unique_stored = {}
    for row in rows:
        if row.get("status") != "Retained":
            continue
        path = _canonical_retained(Path(row.get("retainedPath", "")))
        try:
            path.relative_to(inputs)
        except ValueError as error:
            raise RetentionError("Retained evidence escapes attempt store") from error
        raw = _decode_row(row)
        identity = row["sha256"]
        previous = unique_raw.get(identity)
        if previous is not None and previous != (row["bytes"], hashlib.sha256(raw).hexdigest()):
            raise RetentionError("Conflicting raw identity in retention store")
        unique_raw[identity] = (row["bytes"], hashlib.sha256(raw).hexdigest())
        stored_key = str(path)
        stored_value = (row["retainedBytes"], row["retainedSha256"], row["retainedEncoding"])
        if stored_key in unique_stored and unique_stored[stored_key] != stored_value:
            raise RetentionError("Conflicting stored identity in retention store")
        unique_stored[stored_key] = stored_value
    logical = sum(value[0] for value in unique_raw.values())
    stored = sum(value[0] for value in unique_stored.values())
    if state.get("retainedUniqueBytes") != logical:
        raise RetentionError("Retained logical byte total differs from state")
    if state.get("retainedStoredBytes") != stored:
        raise RetentionError("Retained stored byte total differs from state")
    limits = state.get("retentionLimits")
    if type(limits) is not dict or any(type(limits.get(key)) is not int or limits[key] <= 0 for key in (
            "maxFileBytes", "maxLogicalUniqueBytes", "maxStoredBytes", "maxObservations")):
        raise RetentionError("Retention limits missing or malformed in state")
    if any(row.get("status") == "Retained" and row.get("bytes", -1) > limits["maxFileBytes"] for row in rows):
        raise RetentionError("Retained file exceeds declared per-file limit")
    if (logical > limits["maxLogicalUniqueBytes"] or stored > limits["maxStoredBytes"] or
            len(rows) > limits["maxObservations"]):
        raise RetentionError("Retained store exceeds declared limits")
    return {
        "inventorySha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
        "observationCount": len(rows),
        "uniqueContentCount": len(unique_raw),
        "storedBlobCount": len(unique_stored),
        "logicalUniqueBytes": logical,
        "storedBytes": stored,
    }


class Attempt:
    def __init__(self, root: Path, operation: str, *, max_file_bytes=MAX_FILE_BYTES,
                 max_total_bytes=MAX_TOTAL_BYTES, max_files=MAX_FILES,
                 max_stored_bytes=MAX_STORED_BYTES):
        self.root = Path(root)
        if not self.root.is_absolute() or self.root != self.root.resolve():
            raise RetentionError("Capture attempt root must be absolute and canonical")
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise RetentionError("Symlink in capture attempt root")
        if any(type(x) is not int or x <= 0 for x in (
                max_file_bytes, max_total_bytes, max_files, max_stored_bytes)):
            raise RetentionError("Invalid retention bound")
        if self.root.exists():
            raise RetentionError("Capture attempt root must be new")
        self.root.mkdir(parents=True, exist_ok=False, mode=0o700)
        self.inputs = self.root / "attempt-inputs"
        self.inputs.mkdir(mode=0o700)
        self.limits = (max_file_bytes, max_total_bytes, max_files, max_stored_bytes)
        self.rows = []
        self.used_bytes = 0
        self.stored_bytes = 0
        self.seen = {}
        self.content_hashes = set()
        self.stores = {}
        self.inventory = self.root / "attempt-inputs.jsonl"
        new_file(self.inventory, b"")
        self.state = {"schemaVersion": 1, "kind": "H1CaptureAttempt", "operation": operation,
            "status": "InProgress", "stage": "created", "diagnosticOnly": True,
            "candidateAcceptance": False, "humanGatePassed": False, "mayEnterR02": False,
            "planning": "NotRun", "pchReplay": "NotRun", "macroProbes": "NotRun",
            "transitivePchHeaders": "NotDiscoveredBeforePchInspection",
            "retentionPolicy": "content-addressed-compress-if-smaller-v1",
            "retentionStoreVerification": "NotRun",
            "retentionLimits": {
                "maxFileBytes": max_file_bytes,
                "maxLogicalUniqueBytes": max_total_bytes,
                "maxStoredBytes": max_stored_bytes,
                "maxObservations": max_files,
            }}
        self._state()

    def _state(self) -> None:
        self.state["retainedInputCount"] = len(self.rows)
        self.state["retainedUniqueBytes"] = self.used_bytes
        self.state["retainedStoredBytes"] = self.stored_bytes
        tmp = self.root / ("attempt-state-" + uuid.uuid4().hex + ".tmp")
        new_file(tmp, encode(self.state))
        os.replace(tmp, self.root / "attempt-state.json")

    def stage(self, stage: str, **facts) -> None:
        self.state.update(stage=stage, **facts)
        self._state()

    def _record(self, row: dict) -> dict:
        if len(self.rows) >= self.limits[2]:
            raise RetentionError("Capture input inventory exceeds retention count bound")
        with self.inventory.open("ab") as stream:
            stream.write(encode(row).replace(b"\n", b"") + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.rows.append(row)
        return row

    def _storage(self, raw: bytes, requested: str) -> tuple[str, bytes]:
        if requested == ENCODING_RAW:
            return ENCODING_RAW, raw
        if requested != ENCODING_ZLIB:
            raise RetentionError("Unsupported retention storage policy")
        compressed = zlib.compress(raw, level=COMPRESS_LEVEL)
        # Never make one stored member larger than its already bounded raw input.
        return (ENCODING_ZLIB, compressed) if len(compressed) < len(raw) else (ENCODING_RAW, raw)

    def keep_bytes(self, source: str, raw: bytes, role: str, *, storage=ENCODING_RAW) -> dict:
        if type(raw) is not bytes:
            raise RetentionError("Retention requires bytes")
        digest = hashlib.sha256(raw).hexdigest()
        key = (str(source), role)
        previous = self.seen.get(key)
        if previous is not None:
            if previous["sha256"] != digest:
                raise RetentionError("Capture input changed during retention: " + str(source))
            return previous
        is_new_content = digest not in self.content_hashes
        if len(raw) > self.limits[0]:
            self._record({"sourcePath": str(source), "role": role, "status": "RetentionFileBoundExceeded",
                          "bytes": len(raw), "sha256": digest})
            raise RetentionError("Capture input exceeds per-file retention byte bound: " + str(source))
        if is_new_content and self.used_bytes + len(raw) > self.limits[1]:
            self._record({"sourcePath": str(source), "role": role, "status": "RetentionLogicalBoundExceeded",
                          "bytes": len(raw), "sha256": digest})
            raise RetentionError("Capture input exceeds logical retention byte bound: " + str(source))
        encoding, stored = self._storage(raw, storage)
        store_key = (digest, encoding)
        retained = self.stores.get(store_key)
        if retained is None:
            stored_digest = hashlib.sha256(stored).hexdigest()
            if self.stored_bytes + len(stored) > self.limits[3]:
                self._record({"sourcePath": str(source), "role": role, "status": "RetentionStoredBoundExceeded",
                              "bytes": len(raw), "sha256": digest, "retainedEncoding": encoding,
                              "retainedBytes": len(stored), "retainedSha256": stored_digest})
                raise RetentionError("Capture input exceeds stored retention byte bound: " + str(source))
            suffix = ".zlib" if encoding == ENCODING_ZLIB else ".bin"
            target = self.inputs / (digest + suffix)
            new_file(target, stored)
            retained = {"retainedPath": str(target), "retainedEncoding": encoding,
                        "retainedBytes": len(stored), "retainedSha256": stored_digest}
            self.stores[store_key] = retained
            self.stored_bytes += len(stored)
        if is_new_content:
            self.content_hashes.add(digest)
            self.used_bytes += len(raw)
        row = self._record({"sourcePath": str(source), "role": role, "status": "Retained",
            **retained, "bytes": len(raw), "sha256": digest})
        self.seen[key] = row
        return row

    def read_file(self, path: Path, role: str, *, required=True, storage=ENCODING_RAW) -> bytes | None:
        path = Path(path)
        try:
            if not path.is_absolute() or path != path.resolve() or any(
                    p.is_symlink() for p in (path, *path.parents)):
                raise RetentionError("Input must be absolute, canonical, and not symlinked")
            with path.open("rb") as stream:
                before = os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode):
                    raise RetentionError("Input is not a regular file")
                if before.st_size > self.limits[0]:
                    raise RetentionError("Input exceeds per-file retention bound")
                raw = stream.read(self.limits[0] + 1)
                after = os.fstat(stream.fileno())
            if any(p.is_symlink() for p in (path, *path.parents)):
                raise RetentionError("Input became symlinked during read")
            current = path.stat()
            identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            if identity(before) != identity(after) or identity(after) != identity(current) or len(raw) != after.st_size:
                raise RetentionError("Input changed during read")
        except (OSError, ValueError) as error:
            self._record({"sourcePath": str(path), "role": role, "status": "UnavailableToRetention",
                "errorType": type(error).__name__, "error": str(error)})
            if required:
                raise
            return None
        # Retention budget exhaustion remains fatal even when the source itself was
        # optional to diagnostics.
        self.keep_bytes(str(path), raw, role, storage=storage)
        return raw

    def retain_declared_inputs(self, graph: dict, project: Path) -> None:
        """Snapshot declared native inputs without executing an unvalidated action.

        Every selected source is retained byte-for-byte logically. Generated native
        source storage may be compressed reversibly; PCH/header/rsp/plist evidence
        stays raw. Transitive includes remain unknown until PCH/header inspection.
        """
        suffixes = {".pch", ".h", ".hpp", ".hxx", ".c", ".cpp", ".cc", ".cxx", ".m", ".mm", ".rsp", ".plist"}
        selected = set()
        nodes = graph.get("Nodes", [])
        if type(nodes) is not list:
            return
        for node in nodes:
            if type(node) is not dict or not str(node.get("Annotation", "")).startswith(("C_Mac_arm64", "Link_Mac_arm64")):
                continue
            for key in ("Inputs", "Outputs"):
                values = node.get(key, [])
                if type(values) is not list:
                    continue
                for source in values:
                    if type(source) is not str or not source or "\0" in source:
                        continue
                    path = Path(os.path.abspath(source if os.path.isabs(source) else project / source))
                    if path.suffix in suffixes and (key == "Inputs" or path.suffix == ".pch"):
                        selected.add(path)
                        if len(selected) > self.limits[2]:
                            raise RetentionError("Declared input inventory exceeds retention bound")
        # Nominal path volume is diagnostic only; authenticated raw identity remains
        # the per-content SHA/length captured below.
        nominal = 0
        available = 0
        for path in selected:
            try:
                if path.is_file() and not path.is_symlink():
                    nominal += path.stat().st_size
                    available += 1
            except OSError:
                pass
        self.state.update(declaredInputPathCount=len(selected),
                          declaredInputAvailableAtCensus=available,
                          declaredInputNominalBytes=nominal)
        self._state()
        for path in sorted(selected):
            storage = ENCODING_ZLIB if path.suffix in SOURCE_SUFFIXES else ENCODING_RAW
            self.read_file(path, "declared-native-input", required=False, storage=storage)

    def verify_store(self) -> dict:
        self._state()
        summary = verify_attempt_store(self.root)
        if summary["logicalUniqueBytes"] != self.used_bytes or summary["storedBytes"] != self.stored_bytes:
            raise RetentionError("In-memory and retained store accounting differ")
        return summary

    def finish(self, status: str) -> None:
        summary = self.verify_store()
        self.state.update(status=status, retentionStoreVerification="Passed",
                          retentionInventorySha256=summary["inventorySha256"],
                          retainedUniqueContentCount=summary["uniqueContentCount"],
                          retainedBlobCount=summary["storedBlobCount"])
        self._state()

    def fail(self, error: BaseException) -> None:
        if self.state["stage"] == "planning" and self.state["planning"] == "Started":
            self.state["planning"] = "Failed"
        self.state.update(status="FailedNotAccepted", errorType=type(error).__name__, error=str(error))
        self._state()
        failure = dict(self.state)
        failure["traceback"] = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        raw = self.inventory.read_bytes()
        failure["inputInventorySha256"] = hashlib.sha256(raw).hexdigest()
        new_file(self.root / "attempt-failure.json", encode(failure))

    @contextmanager
    def guard(self):
        try:
            yield self
        except BaseException as error:
            try:
                self.fail(error)
            except BaseException as retention_error:
                # Preserve the original product/parser exception as the propagated cause.
                try:
                    error.add_note("Failure-journal write also failed: " + str(retention_error))
                except AttributeError:
                    pass
            raise
