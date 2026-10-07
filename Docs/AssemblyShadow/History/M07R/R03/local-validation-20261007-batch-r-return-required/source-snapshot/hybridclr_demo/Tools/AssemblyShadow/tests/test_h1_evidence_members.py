"""Focused synthetic tests for the H1 archive member authenticator."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import h1_evidence_members as members
from h1_evidence_members import REPORT_NAME, VerificationError, authenticate_members


def _write_archive(path: Path, members: list[tuple[str, bytes, str]]) -> None:
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for name, data, kind in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            if kind == "regular":
                archive.addfile(info, io.BytesIO(data))
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = data.decode()
                info.size = 0
                archive.addfile(info)
            elif kind == "directory":
                info.type = tarfile.DIRTYPE
                info.size = 0
                archive.addfile(info)
            else:
                raise AssertionError(kind)


def _index(path: Path, archive_path: Path, members: list[tuple[str, bytes, str]], *, duplicate_json=False,
           schema=1, member_count=None) -> None:
    rows = [{"archiveMember": name, "mode": "0644", "rawPath": "/capture/" + name,
             "sha256": hashlib.sha256(data).hexdigest(), "sizeBytes": len(data)}
            for name, data, kind in members if kind == "regular"]
    payload = {"schemaVersion": schema, "kind": "Synthetic", "archivePath": str(archive_path),
               "archiveSha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
               "archiveSizeBytes": archive_path.stat().st_size, "memberCount": len(rows) if member_count is None else member_count,
               "files": rows}
    text = json.dumps(payload)
    if duplicate_json:
        text = text[:-1] + ',"memberCount":0}'
    path.write_text(text, encoding="utf-8")


def _map(path: Path, archive: Path, index: Path, root: Path, *, bad_archive=False, bad_index=False) -> None:
    payload = {"schemaVersion": 1,
               "archive": {"path": str(archive), "sha256": ("0" * 64 if bad_archive else hashlib.sha256(archive.read_bytes()).hexdigest()),
                           "sizeBytes": archive.stat().st_size},
               "index": {"path": str(index), "sha256": ("0" * 64 if bad_index else hashlib.sha256(index.read_bytes()).hexdigest())},
               "tools": []}
    path.write_text(json.dumps(payload), encoding="utf-8")


class MemberAuditTests(unittest.TestCase):
    def run_case(self, members, *, index_members=None, **kwargs):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); archive = root / "evidence.tar.gz"; index = root / "index.json"; input_map = root / "input-map.json"
            _write_archive(archive, members)
            _index(index, archive, members if index_members is None else index_members,
                   duplicate_json=kwargs.pop("duplicate_json", False), schema=kwargs.pop("schema", 1),
                   member_count=kwargs.pop("member_count", None))
            _map(input_map, archive, index, root, **kwargs)
            output = root / "report"
            return authenticate_members(input_map, output), output

    def test_valid_case_and_zero_case_fail(self):
        report, output = self.run_case([("one.json", b"{}", "regular")])
        self.assertEqual(report["status"], "PASS")
        with self.assertRaisesRegex(VerificationError, "Zero-member archive/index is not acceptable"):
            self.run_case([])

    def test_bad_hash_retains_failure_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); archive = root / "evidence.tar.gz"; index = root / "index.json"; input_map = root / "input-map.json"
            _write_archive(archive, [("one", b"1", "regular")])
            _index(index, archive, [("one", b"1", "regular")])
            _map(input_map, archive, index, root, bad_archive=True)
            output = root / "report"
            with self.assertRaisesRegex(VerificationError, "Archive SHA-256 does not match input map"):
                authenticate_members(input_map, output)
            report = json.loads((output / REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAIL")
            self.assertNotEqual(report["inputs"]["archive"]["expectedSha256"], report["inputs"]["archive"]["observedSha256"])

    def test_index_replacement_after_digest_cannot_authenticate_new_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); archive = root / "evidence.tar.gz"; index = root / "index.json"; input_map = root / "input-map.json"
            _write_archive(archive, [("one", b"1", "regular")])
            _index(index, archive, [("one", b"1", "regular")])
            corrected_index = index.read_bytes()
            wrong = json.loads(corrected_index)
            wrong["files"][0]["sha256"] = "0" * 64
            index.write_text(json.dumps(wrong), encoding="utf-8")
            _map(input_map, archive, index, root)
            output = root / "report"
            original_read = members._read_file_bytes
            replacements = []

            def replace_after_capture(path, **kwargs):
                result = original_read(path, **kwargs)
                if path == index:
                    index.write_bytes(corrected_index)
                    replacements.append(path)
                return result

            with mock.patch.object(members, "_read_file_bytes", side_effect=replace_after_capture):
                with self.assertRaisesRegex(VerificationError, "Archive member one size/hash differs from index"):
                    authenticate_members(input_map, output)
            self.assertEqual(replacements, [index])
            self.assertEqual(index.read_bytes(), corrected_index)
            report = json.loads((output / REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAIL")

    def test_declared_tool_hash_mismatch_retains_failure_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); archive = root / "evidence.tar.gz"; index = root / "index.json"; input_map = root / "input-map.json"
            _write_archive(archive, [("one", b"1", "regular")])
            _index(index, archive, [("one", b"1", "regular")])
            _map(input_map, archive, index, root)
            payload = json.loads(input_map.read_text(encoding="utf-8"))
            payload["tools"] = [{"name": "declared", "path": str(Path(members.__file__).resolve()), "sha256": "0" * 64}]
            input_map.write_text(json.dumps(payload), encoding="utf-8")
            output = root / "report"
            with self.assertRaisesRegex(VerificationError, "Tool hash mismatch for declared"):
                authenticate_members(input_map, output)
            report = json.loads((output / REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("Tool hash mismatch for declared", report["error"])

    def test_duplicate_index_json_and_archive_members_fail(self):
        with self.assertRaisesRegex(VerificationError, "Duplicate JSON key: memberCount"):
            self.run_case([("one", b"1", "regular")], duplicate_json=True)
        with self.assertRaisesRegex(VerificationError, "Duplicate archive member: one"):
            self.run_case([("one", b"1", "regular"), ("one", b"1", "regular")],
                          index_members=[("one", b"1", "regular")])

    def test_duplicate_json_key_in_archived_member_fails(self):
        with self.assertRaisesRegex(VerificationError, "Duplicate JSON key: a"):
            self.run_case([("one.json", b'{"a":1,"a":2}', "regular")])

    def test_unsafe_member_and_nonregular_member_fail(self):
        with self.assertRaisesRegex(VerificationError, "Non-canonical archive member path"):
            self.run_case([("../escape", b"x", "regular")], index_members=[("safe", b"x", "regular")])
        with self.assertRaisesRegex(VerificationError, r"Archive member is not a regular file \(symlink\): link"):
            self.run_case([("link", b"target", "symlink")])

    def test_missing_and_unindexed_members_fail(self):
        with self.assertRaisesRegex(VerificationError, "Archive/index member sets differ"):
            self.run_case([("one", b"1", "regular")], index_members=[])
        with self.assertRaisesRegex(VerificationError, "Archive/index member sets differ"):
            self.run_case([], index_members=[("one", b"1", "regular")])

    def test_wrong_index_version_fails(self):
        with self.assertRaisesRegex(VerificationError, "Unsupported evidence index schemaVersion"):
            self.run_case([("one", b"1", "regular")], schema=2)


if __name__ == "__main__":
    unittest.main()
