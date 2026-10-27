#!/usr/bin/env python3
"""Source-only contracts for bounded fc55 sparse-worktree projection.

Real tiny temporary Git repositories only. No original-S files or worktrees,
Unity/Player builds, caches, user files or external Local roots are modified.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import original_s_sparse_projection as proj


class SparseProjectionContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-sparse-custody-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(strict=True)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.protected = "checkpoint/fixed"
        (self.repo / self.protected).mkdir(parents=True)
        (self.repo / self.protected / "part-000.part").write_bytes(b"source evidence bytes" * 8)
        (self.repo / self.protected / "inventory.json").write_text('{"source":"original"}\n')
        (self.repo / "unrelated/deep").mkdir(parents=True)
        (self.repo / "unrelated/deep/old-history.txt").write_bytes(b"older tracked content" * 5)
        self.g("init", "-q")
        self.g("config", "user.email", "ci-fixture@example.invalid")
        self.g("config", "user.name", "R03 Test Fixture")
        self.g("add", ".")
        self.g("commit", "-qm", "synthetic tracked source only")

    def g(self, *args):
        p = subprocess.run(["git", "-C", str(self.repo), *args],
                           capture_output=True, check=True)
        return p.stdout.strip()

    def rows(self):
        return proj.checkpoint_rows(self.repo, self.protected)

    def test_01_fixed_original_s_commit_and_checkpoint_tree(self):
        self.assertEqual(proj.FC55, "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b")
        self.assertEqual(proj.CHECKPOINT_TREE,
                         "2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79")
        self.assertEqual(proj.CHECKPOINT_FILES, 16978)
        self.assertEqual(proj.CHECKPOINT_LOGICAL_BYTES, 3882340952)

    def test_02_malicious_relative_paths_rejected(self):
        for name in ("", "../escape", "/root/escape", "root/../else",
                     "root\\else", "root//else", "root/\nname", "root/\tname"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                proj.canonical_relative(name)

    def test_03_canonical_relative_file_passes(self):
        self.assertEqual(proj.canonical_relative(self.protected), self.protected)

    def test_04_synthetic_committed_source_tree_is_found(self):
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({x["path"] for x in rows}), 2)
        self.assertTrue(all(x["path"].startswith(self.protected + "/") for x in rows))

    def test_05_physical_git_blobs_match_committed_objects(self):
        rows = self.rows()
        for entry in rows:
            path = self.repo / entry["path"]
            self.assertEqual(proj.actual_git_blob(path, entry["size"]), entry["gitBlob"])

    def test_06_full_protected_checkpoint_verified_as_bytes(self):
        r = proj.verify_materialized(self.repo, self.rows())
        self.assertEqual(r["result"], "PassedPhysicalFileVsPinnedGitBlobs")
        self.assertEqual(r["files"], 2)
        self.assertFalse(r["materializedEvidenceRewritten"])

    def test_07_same_size_tamper_detected(self):
        rows = self.rows()
        file = self.repo / self.protected / "inventory.json"
        file.write_bytes(file.read_bytes().replace(b"original", b"altered!"))
        with self.assertRaisesRegex(ValueError, "Protected checkpoint differs"):
            proj.verify_materialized(self.repo, rows)

    def test_08_missing_protected_file_refused(self):
        rows = self.rows()
        (self.repo / self.protected / "inventory.json").unlink()
        with self.assertRaises(ValueError):
            proj.verify_materialized(self.repo, rows)

    def test_09_protected_symlink_refused(self):
        rows = self.rows()
        source = self.repo / self.protected / "inventory.json"
        alias = self.repo / "original-inventory.txt"
        alias.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(alias)
        with self.assertRaises(ValueError):
            proj.verify_materialized(self.repo, rows)

    def test_10_clean_fixture_required(self):
        proj.require_clean(self.repo)

    def test_11_untracked_file_prevents_sparse_change(self):
        (self.repo / "untracked-sensitive.txt").write_text("user content\n")
        with self.assertRaisesRegex(ValueError, "absolutely clean"):
            proj.require_clean(self.repo)

    def test_12_dirty_tracked_source_prevents_sparse_change(self):
        (self.repo / "unrelated/deep/old-history.txt").write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "absolutely clean"):
            proj.require_clean(self.repo)

    def test_13_submodule_state_is_a_hard_gate(self):
        with mock.patch.object(proj, "git", side_effect=[
            subprocess.CompletedProcess([], 0, b"", b""),
            subprocess.CompletedProcess([], 0, b" aaaa external\n", b"")]):
            with self.assertRaises(ValueError):
                proj.require_clean(self.repo)

    def test_14_synthetic_git_sparse_projection_preserves_checkpoint(self):
        rows = self.rows()
        other = self.repo / "unrelated/deep/old-history.txt"
        prior = other.read_bytes()
        result = proj.sparse_command(self.repo, self.protected, timeout=60)
        self.assertEqual(result["exitCode"], 0, result["stderr"])
        self.assertTrue(proj.sparse_enabled(self.repo))
        self.assertTrue((self.repo / self.protected / "inventory.json").is_file())
        self.assertEqual(proj.verify_materialized(self.repo, rows)["files"], 2)
        self.assertFalse(other.exists())
        self.assertEqual(self.g("show", "HEAD:unrelated/deep/old-history.txt"), prior)
        proj.require_clean(self.repo)

    def test_15_sparse_worktree_retains_same_head_and_clean_status(self):
        before = self.g("rev-parse", "HEAD")
        result = proj.sparse_command(self.repo, self.protected, timeout=60)
        self.assertEqual(result["exitCode"], 0)
        self.assertEqual(before, self.g("rev-parse", "HEAD"))
        self.assertEqual(self.g("status", "--porcelain=v1", "--untracked-files=all"), b"")

    def test_16_sparse_projection_does_not_prune_git_objects(self):
        prior = self.g("rev-parse", "HEAD:unrelated/deep/old-history.txt")
        proj.sparse_command(self.repo, self.protected, timeout=60)
        self.assertEqual(self.g("rev-parse", "HEAD:unrelated/deep/old-history.txt"), prior)
        self.g("cat-file", "-e", prior)

    def test_17_sparse_path_list_matches_single_projection(self):
        result = proj.sparse_command(self.repo, self.protected, timeout=60)
        self.assertEqual(result["exitCode"], 0)
        self.assertEqual(self.g("sparse-checkout", "list").decode().splitlines(),
                         [self.protected])

    def test_18_no_sparse_conversion_before_explicit_apply(self):
        self.assertFalse(proj.sparse_enabled(self.repo))
        self.rows()
        proj.require_clean(self.repo)
        self.assertFalse(proj.sparse_enabled(self.repo))

    def test_19_intent_receipt_is_create_only(self):
        path = self.root / "receipts" / "INTENT.json"
        proj.write_new(path, {"result": "First"})
        with self.assertRaises(FileExistsError):
            proj.write_new(path, {"result": "Overwritten"})
        self.assertIn('"First"', path.read_text())

    def test_20_failed_command_has_explicit_status(self):
        with mock.patch.object(proj, "git", return_value=
             subprocess.CompletedProcess([], 2, b"", b"failure")) as cmd:
            result = proj.sparse_command(self.repo, self.protected)
        self.assertEqual(result["exitCode"], 2)
        self.assertEqual(result["attemptCount"], 1)
        cmd.assert_called_once()

    def test_21_git_timeout_is_preserved_not_retried(self):
        with mock.patch.object(proj, "git", side_effect=
             subprocess.TimeoutExpired(cmd="git sparse-checkout", timeout=1,
                                       output=b"partial", stderr=b"timeout")) as cmd:
            result = proj.sparse_command(self.repo, self.protected, timeout=1)
        self.assertTrue(result["timedOut"])
        self.assertEqual(result["attemptCount"], 1)
        self.assertIn("partial", result["stdout"])
        cmd.assert_called_once()

    def test_22_no_automatic_cache_or_historical_cleanup(self):
        src = Path(proj.__file__).read_text(encoding="utf-8")
        self.assertNotIn('"worktree", "remove"', src)
        self.assertNotIn('"worktree", "prune"', src)
        self.assertNotIn('"sparse-checkout", "disable"', src)
        self.assertNotIn("shutil.rmtree(", src)
        self.assertIn("reversalMayRequireOriginalFullDiskCapacity", src)

    def test_23_runtime_acceptance_stays_false(self):
        src = Path(proj.__file__).read_text()
        self.assertIn('"coordinatorInvoked": False', src)
        self.assertIn('"ReadyForHumanReviewGate": False', src)
        self.assertIn('"R03Accepted": False', src)

    def test_24_original_s_archive_is_not_rebuilt_or_executed(self):
        src = Path(proj.__file__).read_text()
        self.assertNotIn("audit_s_provenance.py", src)
        self.assertNotIn("run_terminal_current.py", src)
        self.assertIn("originalArchiveExecuted", src)

    def test_25_different_git_blob_even_same_length_is_rejected(self):
        entry = self.rows()[0]
        path = self.repo / entry["path"]
        changed = b"Q" * entry["size"]
        path.write_bytes(changed)
        self.assertNotEqual(proj.actual_git_blob(path, entry["size"]), entry["gitBlob"])

    def test_26_synthetic_projection_has_unchanged_commit(self):
        base = self.g("rev-parse", "HEAD")
        self.assertEqual(proj.sparse_command(self.repo, self.protected)["exitCode"], 0)
        self.assertEqual(self.g("rev-parse", "HEAD"), base)
        self.assertEqual(self.g("show", "HEAD:checkpoint/fixed/inventory.json"),
                         b'{"source":"original"}')

    def test_27_sparsified_fixture_not_suitable_for_second_apply(self):
        self.assertFalse(proj.sparse_enabled(self.repo))
        proj.sparse_command(self.repo, self.protected)
        self.assertTrue(proj.sparse_enabled(self.repo))
        # Production apply refuses the same source on the next attempt.
        src = Path(proj.__file__).read_text()
        self.assertIn('"Worktree is already sparse; never repeat', src)


    def test_28_regular_index_allows_honest_source_projection(self):
        with mock.patch.object(proj, "CHECKPOINT_FILES", 1):
            self.assertGreaterEqual(proj.require_unhidden_index(self.repo), 3)

    def test_29_assume_unchanged_hidden_tracked_data_rejected(self):
        path = "unrelated/deep/old-history.txt"
        self.g("update-index", "--assume-unchanged", path)
        self.assertEqual(self.g("status", "--porcelain=v1"), b"")
        with mock.patch.object(proj, "CHECKPOINT_FILES", 1):
            with self.assertRaisesRegex(ValueError, "Hidden or abnormal"):
                proj.require_unhidden_index(self.repo)

    def test_30_preexisting_skip_worktree_entry_rejected(self):
        self.g("update-index", "--skip-worktree", "unrelated/deep/old-history.txt")
        with mock.patch.object(proj, "CHECKPOINT_FILES", 1):
            with self.assertRaisesRegex(ValueError, "Hidden or abnormal"):
                proj.require_unhidden_index(self.repo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
