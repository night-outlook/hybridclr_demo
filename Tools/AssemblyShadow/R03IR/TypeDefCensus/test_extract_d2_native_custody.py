#!/usr/bin/env python3
"""D2 exact-source and fail-closed mutation tests. Real Git checkouts required."""
from __future__ import annotations
import copy
import os
import unittest
from pathlib import Path
from extract_d2_native_custody import (
    COMMIT,PINS,N_ASSEMBLY,N_METADATA,N_SHADOW,N_ASSEMBLY_H,N_METADATA_H,
    extract, read_pinned,SourceMismatch,
)

class D2ExactCustodySourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get("R03_B2_D2_NATIVE_ROOT")
        if not root: raise RuntimeError("D2 exact native pinned checkout required")
        cls.sources=read_pinned(Path(root),COMMIT,PINS)

    def reject(self,path,old,new):
        mutated=copy.copy(self.sources)
        self.assertIn(old,mutated[path])
        mutated[path]=mutated[path].replace(old,new,1)
        with self.assertRaises(SourceMismatch):
            extract(mutated)

    def test_01_real_exact_native_methods(self):
        result,blobs=extract(self.sources)
        self.assertEqual(len(blobs),14)
        self.assertEqual(len({b["label"] for b in blobs}),14)
        self.assertIn("ScopedPhysicalRollback",result)
        self.assertIn("ScopedCliRollback",result)
        self.assertIn("ReleasePublicationUsage",result)
        self.assertIn("ScopedUnexpectedPublicationExit",result)

    def test_02_source_pins_and_receipt(self):
        self.assertEqual(COMMIT,"b86a97e1dcca18163df5ac2d5f268bf6de18bbdf")
        self.assertEqual(len(PINS),5)
        self.assertEqual(set(PINS),{N_ASSEMBLY,N_METADATA,N_SHADOW,N_ASSEMBLY_H,N_METADATA_H})

    def test_03_missing_native_assembly_header_abort(self):
        self.reject(N_ASSEMBLY_H,"void (*onAbandon)(void*)","void (*onError)(void*)")

    def test_04_missing_metadata_header_abort(self):
        self.reject(N_METADATA_H,"void (*onAbandon)(void*)","void (*onError)(void*)")

    def test_05_missing_physical_scope(self):
        self.reject(N_ASSEMBLY,"~ScopedPhysicalRollback() noexcept",
                    "~ScopedPhysicalChanged() noexcept")

    def test_06_missing_usage_release_inside_assembly_scope(self):
        self.reject(N_ASSEMBLY,"abandon(context);","/* custody omitted */")

    def test_07_missing_physical_registry_shrink(self):
        self.reject(N_ASSEMBLY,"entries.resize(previousSize);","/* physical rollback omitted */")

    def test_08_missing_physical_commit_disarm(self):
        self.reject(N_ASSEMBLY,"rollback.committed = true;","/* committed not marked */")

    def test_09_missing_cli_scope(self):
        self.reject(N_METADATA,"~ScopedCliRollback() noexcept",
                    "~ScopedCliChanged() noexcept")

    def test_10_missing_cli_shrink(self):
        self.reject(N_METADATA,"s_cliAssemblies.resize_uninitialized(previousSize);",
                    "/* CLI rollback omitted */")

    def test_11_missing_meta_to_assembly_abort_wrapper(self):
        self.reject(N_METADATA,"AbandonShadowPublication, &publication",
                    "nullptr, &publication")

    def test_12_usage_marker_not_set(self):
        self.reject(N_SHADOW,"publication.usageHeld = true;","publication.usageHeld = false;")

    def test_13_usage_release_not_idempotent(self):
        self.reject(N_SHADOW,"if (!publication.usageHeld) return;",
                    "if (publication.usageHeld) return;")

    def test_14_absent_release_on_normal_publication(self):
        self.reject(N_SHADOW,
                    "s_active.store(publication.snapshot, std::memory_order_release);\n        ReleasePublicationUsage(context);",
                    "s_active.store(publication.snapshot, std::memory_order_release);\n        /* usage release omitted */")

    def test_15_missing_exceptional_terminal_latch(self):
        self.reject(N_SHADOW,"exceptionalExit.returned = true;",
                    "/* terminal-on-exception guard not disarmed */")

    def test_16_omitted_native_usage callback_call(self):
        self.reject(N_SHADOW,"ReleasePublicationUsage, &publication);",
                    "nullptr, &publication);")

    def test_17_extra_file_rejected(self):
        x=copy.copy(self.sources);x["libil2cpp/vm/Other.cpp"]=""
        with self.assertRaises(SourceMismatch):extract(x)

    def test_18_missing_file_rejected(self):
        x=copy.copy(self.sources);x.pop(N_SHADOW)
        with self.assertRaises(SourceMismatch):extract(x)

if __name__=="__main__":unittest.main()
