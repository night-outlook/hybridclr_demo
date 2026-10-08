"""Focused synthetic tests for exact H1 reference resolution."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from h1_evidence_references import REPORT_NAME, VerificationError, authenticate_references


def _archive(path: Path, data: dict[str, object]) -> None:
    raw = json.dumps(data, separators=(",", ":")).encode()
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        info = tarfile.TarInfo("records.json"); info.size = len(raw)
        archive.addfile(info, io.BytesIO(raw))


def _index(path: Path, archive: Path, *, member_hash: str, member_size: int,
           duplicate_raw=False, zero=False) -> None:
    rows = [] if zero else [{"archiveMember": "records.json", "rawPath": "/capture/v6/records.json",
                             "sha256": member_hash, "sizeBytes": member_size}]
    payload = {"schemaVersion": 1, "memberCount": len(rows), "files": rows}
    if duplicate_raw:
        payload["files"].append(dict(rows[0]))
        payload["memberCount"] = 2
    path.write_text(json.dumps(payload), encoding="utf-8")


def _prior(path: Path, archive: Path, index: Path, *, member_hash: str, member_size: int) -> None:
    payload = {"schemaVersion": 1, "operation": "members", "status": "PASS",
               "inputs": {"archive": {"observedSha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
                           "index": {"observedSha256": hashlib.sha256(index.read_bytes()).hexdigest()}},
               "observed": {"memberCount": 1, "members": {"records.json": {"sizeBytes": member_size, "sha256": member_hash}}}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def _setup(root: Path, payload: dict[str, object], *, duplicate_raw=False, zero=False):
    archive = root / "evidence.tar.gz"; index = root / "index.json"; prior = root / "members.json"; input_map = root / "input-map.json"
    _archive(archive, payload)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    digest = hashlib.sha256(raw).hexdigest()
    _index(index, archive, member_hash=digest, member_size=len(raw), duplicate_raw=duplicate_raw, zero=zero)
    _prior(prior, archive, index, member_hash=digest, member_size=len(raw))
    mapping = {"schemaVersion": 1,
               "archive": {"path": str(archive), "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()},
               "index": {"path": str(index), "sha256": hashlib.sha256(index.read_bytes()).hexdigest()},
               "membersAudit": {"path": str(prior), "sha256": hashlib.sha256(prior.read_bytes()).hexdigest()}, "tools": []}
    input_map.write_text(json.dumps(mapping), encoding="utf-8")
    return input_map


class ReferenceAuditTests(unittest.TestCase):
    def test_exact_internal_and_pending_external(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"path": "/capture/v6/records.json", "business": "records"})
            report = authenticate_references(input_map, root / "report")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(len(report["observed"]["internalReferences"]), 1)
            self.assertEqual(report["observed"]["unresolvedReferences"], [])

    def test_path_array_preserves_locator_field_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"paths": ["/external/missing.bin"]})
            report = authenticate_references(input_map, root / "report")
            unresolved = report["observed"]["unresolvedReferences"]
            self.assertEqual(len(unresolved), 1)
            self.assertEqual(unresolved[0]["field"], "paths")
            self.assertEqual(unresolved[0]["jsonPointer"], "/paths/0")

    def test_bare_exact_archive_member_resolves_before_field_heuristic(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"note": "records.json"})
            report = authenticate_references(input_map, root / "report")
            internal = report["observed"]["internalReferences"]
            self.assertEqual(len(internal), 1)
            self.assertEqual(internal[0]["resolution"], "ExactArchiveMember")
            self.assertEqual(internal[0]["jsonPointer"], "/note")

    def test_unmatched_declared_path_string_is_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"path": "README"})
            report = authenticate_references(input_map, root / "report")
            unresolved = report["observed"]["unresolvedReferences"]
            self.assertEqual(len(unresolved), 1)
            self.assertEqual(unresolved[0]["value"], "README")
            self.assertEqual(unresolved[0]["classification"], "PendingExternalVerification")

    def test_cross_version_basename_and_missing_external_remain_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"path": "/capture/v5/records.json", "file": "/capture/v6/records.json"})
            report = authenticate_references(input_map, root / "report")
            values = {row["value"] for row in report["observed"]["unresolvedReferences"]}
            self.assertEqual(values, {"/capture/v5/records.json"})
            self.assertEqual({row["value"] for row in report["observed"]["internalReferences"]},
                             {"/capture/v6/records.json"})
            self.assertTrue(all(row["classification"] == "PendingExternalVerification" for row in report["observed"]["unresolvedReferences"]))

    def test_duplicate_rawpath_zero_and_bad_prior_digest_fail(self):
        for options, reason in ((("duplicate_raw", True), "Duplicate index rawPath"), (("zero", True), "zero entries")):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); input_map = _setup(root, {"path": "/capture/v6/records.json"}, **dict([options]))
                with self.assertRaisesRegex(VerificationError, reason):
                    authenticate_references(input_map, root / "report")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); input_map = _setup(root, {"path": "/capture/v6/records.json"})
            payload = json.loads(input_map.read_text()); payload["membersAudit"]["sha256"] = "0" * 64
            input_map.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(VerificationError, "Members audit SHA-256"):
                authenticate_references(input_map, root / "report")


if __name__ == "__main__":
    unittest.main()
