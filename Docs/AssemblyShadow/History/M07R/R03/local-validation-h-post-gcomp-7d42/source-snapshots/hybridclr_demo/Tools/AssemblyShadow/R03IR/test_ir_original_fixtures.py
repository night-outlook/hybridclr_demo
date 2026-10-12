"""Unit contracts for pinned-S artifact admission. Temporary Git only; no Unity."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "R03"))
import ir_original_fixtures as subject


NAMES = (
    "baseline/A.dll", "baseline/B.dll", "baseline/Layout.dll",
    "baseline/Methods.dll", "baseline/R03Contract.dll",
    "interface/R03Contract.dll", "primitive/R03Contract.dll",
    "private-reference/Layout.dll", "removal/R03Contract.dll",
    "reversal/A.dll", "reversal/B.dll", "true-cycle/A.dll",
    "true-cycle/B.dll", "value/R03Contract.dll", "virtual-slot/Methods.dll"
)


def command(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args],
                                   stderr=subprocess.PIPE, text=True).strip()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class SFixtureAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.demo = root / "hybridclr_demo"
        self.demo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.demo)], check=True)
        command(self.demo, "config", "user.email", "r03-ir@example.invalid")
        command(self.demo, "config", "user.name", "R03 Fixture Tests")
        self.source = self.demo / subject.S_RELATIVE_ROOT
        self.source.mkdir(parents=True)
        records = []
        for name in NAMES:
            f = self.source / name
            f.parent.mkdir(parents=True, exist_ok=True)
            data = ("R03 synthetic fixture " + name + "\n").encode()
            f.write_bytes(data)
            records.append({"path": name, "assembly": Path(name).stem,
                            "mvid": "00000000-0000-0000-0000-000000000001",
                            "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                            "references": ["mscorlib"]})
        document = {"kind": "R03PlayerFixtureInventory", "schemaVersion": 1,
                    "files": records, "nativeExecution": False, "runtimeAcceptance": False}
        (self.source / "inventory.json").write_text(json.dumps(document, indent=2) + "\n")
        command(self.demo, "add", ".")
        command(self.demo, "commit", "-q", "-m", "Test original S baseline")
        self.commit = command(self.demo, "rev-parse", "HEAD")
        self.blob = command(self.demo, "rev-parse",
                            "HEAD:" + subject.S_RELATIVE_ROOT + "/inventory.json")
        self.output = root / "out"
        self.source_patch = mock.patch.object(subject, "S_PUBLICATION", self.commit)
        self.blob_patch = mock.patch.object(subject, "S_INVENTORY_BLOB", self.blob)
        self.source_patch.start()
        self.blob_patch.start()
        self.addCleanup(self.source_patch.stop)
        self.addCleanup(self.blob_patch.stop)

    def test_copies_exact_original_blob_inputs_without_regenerating(self):
        rows, receipt = subject.stage_immutable_original_s(self.demo, self.output, sha)
        self.assertEqual(set(rows), set(NAMES))
        report = json.loads(receipt.read_text())
        self.assertEqual(report["result"], "AuthenticatedCopied")
        self.assertEqual(report["originalFixtureCount"], 15)
        self.assertIs(report["fixtureBytesRegenerated"], False)
        self.assertIs(report["historicalInputsModified"], False)
        self.assertFalse(command(self.demo, "status", "--porcelain"))
        for row in report["files"]:
            self.assertEqual(sha(self.output / row["path"]), row["sha256"])

    def test_existing_destination_is_rejected_before_copy(self):
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, "Unused external"):
            subject.stage_immutable_original_s(self.demo, self.output, sha)

    def test_modified_tracked_fixture_is_rejected_fail_closed(self):
        (self.source / "baseline/Methods.dll").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "fixture byte mismatch"):
            subject.stage_immutable_original_s(self.demo, self.output, sha)
        self.assertFalse(self.output.exists())

    def test_replaced_tracked_history_blob_is_rejected(self):
        (self.source / "baseline/Methods.dll").write_bytes(b"another committed version")
        command(self.demo, "add", ".")
        command(self.demo, "commit", "-q", "-m", "Changed history bytes")
        with self.assertRaisesRegex(ValueError, "fixture byte mismatch"):
            subject.stage_immutable_original_s(self.demo, self.output, sha)

    def test_dirty_original_inventory_is_rejected(self):
        with (self.source / "inventory.json").open("a") as stream:
            stream.write(" ")
        with self.assertRaisesRegex(ValueError, "Working original S inventory"):
            subject.stage_immutable_original_s(self.demo, self.output, sha)
        self.assertFalse(self.output.exists())

    def test_symlink_fixture_is_rejected(self):
        source = self.source / "baseline/Methods.dll"
        source.unlink()
        source.symlink_to(self.source / "baseline/Layout.dll")
        with self.assertRaisesRegex(ValueError, "fixture byte mismatch"):
            subject.stage_immutable_original_s(self.demo, self.output, sha)

    def test_invalid_inventory_path_and_duplicate_fail(self):
        document = json.loads((self.source / "inventory.json").read_text())
        document["files"][0]["path"] = "../bad.dll"
        with self.assertRaisesRegex(ValueError, "Noncanonical"):
            subject.validate_inventory(document)
        document["files"][0]["path"] = document["files"][1]["path"]
        with self.assertRaisesRegex(ValueError, "Invalid/duplicate"):
            subject.validate_inventory(document)

    def test_invalid_field_types_fail(self):
        document = json.loads((self.source / "inventory.json").read_text())
        document["files"][0]["size"] = True
        with self.assertRaisesRegex(ValueError, "Invalid/duplicate"):
            subject.validate_inventory(document)
        document["files"][0]["size"] = 10
        document["files"][0]["sha256"] = "0"
        with self.assertRaisesRegex(ValueError, "Invalid/duplicate"):
            subject.validate_inventory(document)


if __name__ == "__main__":
    unittest.main()
