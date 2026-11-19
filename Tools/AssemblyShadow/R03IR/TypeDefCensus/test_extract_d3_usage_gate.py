#!/usr/bin/env python3
"""IR-D3-01 exact multi-repository source identity and mutation regressions."""
import copy
import os
import unittest
from pathlib import Path
from extract_d3_usage_gate import (
    NATIVE_HEAD, HYBRID_HEAD, NATIVE, HYBRID, N_SHADOW,
    N_ASSEMBLY, N_METADATA, extract, read_pinned, SourceMismatch,
)
from extract_d3_runtime_bridge import H_RUNTIME

class D3PublicationLeaseCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native=os.environ.get("R03_D3_LEASE_NATIVE_ROOT")
        hybrid=os.environ.get("R03_D3_LEASE_HYBRID_ROOT")
        if not native or not hybrid:
            raise RuntimeError("IR-D3-01 requires both pinned native and hybridclr worktrees")
        cls.native=read_pinned(Path(native),NATIVE_HEAD,NATIVE)
        cls.hybrid=read_pinned(Path(hybrid),HYBRID_HEAD,HYBRID)

    def reject(self,where,path,old,new):
        native=copy.copy(self.native)
        hybrid=copy.copy(self.hybrid)
        target=native if where=="native" else hybrid
        self.assertIn(old,target[path])
        target[path]=target[path].replace(old,new,1)
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(native,hybrid)

    def test_01_exact_bodies(self):
        source,bodies=extract(self.native,self.hybrid)
        self.assertEqual(len(bodies),21)
        self.assertEqual(len(set(b["label"] for b in bodies)),21)
        self.assertIn("SealFailedPublicationBeforeUsageUnlock",source)
        self.assertIn("TerminalMethodDenied",source)
        self.assertIn("ScopedPhysicalRollback",source)
        self.assertIn("ScopedCliRollback",source)
        self.assertIn("Assembly::PublishStagedImagesBatch",source)

    def test_02_git_pins(self):
        self.assertEqual(len(NATIVE_HEAD),40)
        self.assertEqual(len(HYBRID_HEAD),40)
        self.assertEqual(len(NATIVE),11)
        self.assertEqual(len(HYBRID),8)

    def test_03_release_cannot_skip_early_terminal(self):
        self.reject("native",N_SHADOW,
                    "SealFailedPublicationBeforeUsageUnlock(publication);",
                    "/* removed terminal seal */")

    def test_04_release_cannot_unlock_before_seal(self):
        self.reject("native",N_SHADOW,
                    "        if (publication.leaseExit == PublicationLeaseExit::Unknown)\n            SealFailedPublicationBeforeUsageUnlock(publication);\n        publication.usageHeld = false;\n        UnlockUsage();",
                    "        publication.usageHeld = false;\n        UnlockUsage();\n        if (publication.leaseExit == PublicationLeaseExit::Unknown)\n            SealFailedPublicationBeforeUsageUnlock(publication);")

    def test_05_missing_durable_terminal_signal(self):
        self.reject("native",N_SHADOW,
                    "        s_unexpectedFailure.store(true, std::memory_order_release);\n        s_state.store(s_active.load(std::memory_order_acquire)",
                    "        s_unexpectedFailure.store(false, std::memory_order_release);\n        s_state.store(s_active.load(std::memory_order_acquire)")

    def test_06_missing_early_first_error(self):
        self.reject("native",N_SHADOW,
                    "        s_firstFailureV2.TryFreeze(\n            static_cast<int32_t>(AssemblyShadowError::InternalError),\n            publication.normalFailure",
                    "        /* skipped FirstErrorV2 */ (\n            static_cast<int32_t>(AssemblyShadowError::InternalError),\n            publication.normalFailure")

    def test_07_double_unlock_prevention(self):
        self.reject("native",N_SHADOW,
                    "        if (!publication.usageHeld) return;\n        if (publication.leaseExit",
                    "        if (publication.usageHeld) return;\n        if (publication.leaseExit")

    def test_08_used_denial_must_not_be_terminal(self):
        self.reject("native",N_SHADOW,
                    "publication.leaseExit = PublicationLeaseExit::UsedBeforeAppend;",
                    "publication.leaseExit = PublicationLeaseExit::Unknown;")

    def test_09_success_must_not_seal_failed(self):
        self.reject("native",N_SHADOW,
                    "publication.leaseExit = PublicationLeaseExit::ActivePublished;",
                    "publication.leaseExit = PublicationLeaseExit::Unknown;")

    def test_10_normal_failure_must_be_tagged(self):
        self.reject("native",N_SHADOW,
                    "            publication.normalFailure = true;\n            ReleasePublicationUsage(context);",
                    "            publication.normalFailure = false;\n            ReleasePublicationUsage(context);")

    def test_11_original_d2_physical_rollback(self):
        self.reject("native",N_ASSEMBLY,
                    "entries.resize(previousSize);",
                    "/* removed physical rollback */")

    def test_12_original_d2_cli_rollback(self):
        self.reject("native",N_METADATA,
                    "~ScopedCliRollback() noexcept",
                    "~RemovedRollback() noexcept")

    def test_13_method_guard_reads_durable(self):
        self.reject("native",N_SHADOW,
                    "s_unexpectedFailure.load(std::memory_order_acquire) ||",
                    "s_unexpectedFailure.load(std::memory_order_relaxed) ||")

    def test_14_native_frozen_first_reason(self):
        self.reject("native",N_SHADOW,
                    "publication.normalFailure\n                ? assembly_shadow_first_failure_v2::Origin::TransactionTerminal",
                    "publication.normalFailure\n                ? assembly_shadow_first_failure_v2::Origin::Guard")

    def test_15_runtime_actual_codec_entry(self):
        self.reject("hybrid",H_RUNTIME,
                    "observer->beforeCodec(observer->context)",
                    "observer->afterRuntimeGroup(observer->context)")

    def test_16_runtime_real_group_store(self):
        self.reject("hybrid",H_RUNTIME,
                    "current->groups[group].active.store(1, std::memory_order_release);",
                    "current->groups[group].active.store(0, std::memory_order_release);")

    def test_17_native_inventory_fail_closed(self):
        native=copy.copy(self.native)
        native.pop(N_SHADOW)
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(native,self.hybrid)

    def test_18_hybrid_inventory_fail_closed(self):
        hybrid=copy.copy(self.hybrid)
        hybrid.pop(H_RUNTIME)
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(self.native,hybrid)

    def test_19_extra_native_file_rejected(self):
        native=copy.copy(self.native)
        native["unexpected-file"]="unexpected"
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(native,self.hybrid)

if __name__=="__main__":
    unittest.main()
