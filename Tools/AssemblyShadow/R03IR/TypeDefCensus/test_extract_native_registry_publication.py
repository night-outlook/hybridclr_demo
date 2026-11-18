#!/usr/bin/env python3
"""Pin-aware tests for exact native body extraction; no source rewrite."""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from extract_native_registry_publication import (
    NATIVE_COMMIT, PINS, ASSEMBLY, METADATA, SHADOW,
    extract_literal, produce, read_pinned, SourceMismatch, SLICES,
)


class ExtractRegistryPublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get("R03_B2_NATIVE_ROOT")
        if not path:
            raise RuntimeError("real pinned native Git checkout required; no fixture pass")
        cls.sources = read_pinned(Path(path), NATIVE_COMMIT, PINS)

    def test_01_exact_eleven_source_bodies(self):
        code, chunks = produce(self.sources)
        self.assertEqual(len(chunks), 11)
        self.assertEqual(len({item["label"] for item in chunks}), 11)
        self.assertIn("Assembly::PublishShadowBatch", code)
        self.assertIn("MetadataCache::PublishInterpreterAssembliesBatch", code)
        self.assertIn("TryBeginPublication", code)
        self.assertIn("PublishActive", code)

    def test_02_body_literal_survives_without_rewrite(self):
        code, chunks = produce(self.sources)
        self.assertTrue(code.startswith("// GENERATED FROM EXACT GIT OBJECTS"))
        self.assertIn("s_Assemblies.resize(originalSize);", code)
        self.assertIn("s_cliAssemblies.resize_uninitialized(originalSize);", code)
        self.assertIn("s_active.store(publication.snapshot, std::memory_order_release);", code)
        self.assertEqual(sum(chunk["bytes"] > 20 for chunk in chunks), 11)

    def test_03_duplicate_method_is_ambiguous(self):
        item = self.sources[ASSEMBLY]
        code = item + "\n" + (
            "bool Assembly::PublishShadowBatch(const AssemblyVector& a,"
            "bool(*b)(void*),bool(*c)(void*),void*d){return true;}"
        )
        with self.assertRaises(SourceMismatch):
            produce({**self.sources, ASSEMBLY: code})

    def test_04_missing_native_method_rejected(self):
        source = self.sources[ASSEMBLY].replace(
            "bool Assembly::PublishShadowBatch(", "bool Assembly::ChangedBatch(", 1)
        with self.assertRaises(SourceMismatch):
            produce({**self.sources, ASSEMBLY: source})

    def test_05_missing_callback_rejected(self):
        source = self.sources[SHADOW].replace(
            "bool PublishActive(void* context)", "bool ChangedActive(void* context)", 1)
        with self.assertRaises(SourceMismatch):
            produce({**self.sources, SHADOW: source})

    def test_06_missing_metadata_context_rejected(self):
        source = self.sources[METADATA].replace(
            "struct ShadowPublicationContext", "struct ChangedPublicationContext", 1)
        with self.assertRaises(SourceMismatch):
            produce({**self.sources, METADATA: source})

    def test_07_missing_file_rejected(self):
        changed = dict(self.sources)
        changed.pop(METADATA)
        with self.assertRaises(SourceMismatch):
            produce(changed)

    def test_08_unexpected_file_rejected(self):
        changed = dict(self.sources)
        changed["unknown.cpp"] = ""
        with self.assertRaises(SourceMismatch):
            produce(changed)

    def test_09_literal_body_has_braces(self):
        item = self.sources[SHADOW]
        for label, path, anchor, is_struct in SLICES:
            if path != SHADOW:
                continue
            block = extract_literal(item, anchor, label, is_struct)
            self.assertIn("{", block, label)
            self.assertIn("}", block, label)

    def test_10_only_original_three_git_files(self):
        self.assertEqual(len(PINS), 3)
        self.assertEqual(set(PINS), {ASSEMBLY, METADATA, SHADOW})
        self.assertEqual(NATIVE_COMMIT, "cecf4b859d50b128e5c0fc6c90cd89e3a452b96a")


if __name__ == "__main__":
    unittest.main()
