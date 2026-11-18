#!/usr/bin/env python3
"""CI-only exact pinned-source mutation suite; no fake pass when repos absent."""
from __future__ import annotations

import copy
import os
import unittest
from pathlib import Path

from verify_native_publication_visibility_boundary import (
    N_SHADOW, N_REGISTRY, N_METADATA, H_STAGED, H_RUNTIME, H_CODEC,
    H_BRIDGE, NATIVE, HYBRID, NATIVE_COMMIT, HYBRID_COMMIT,
    SourceMismatch, check_source, read_pinned,
)


class NativePublicationVisibilityBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native = os.environ.get("R03_B2_NATIVE_ROOT")
        hybrid = os.environ.get("R03_B2_HYBRIDCLR_ROOT")
        if not native or not hybrid:
            raise RuntimeError("Exact pinned native and hybridclr roots required; no source fixture fallback")
        cls.original = {
            **read_pinned(Path(native), NATIVE_COMMIT, NATIVE),
            **read_pinned(Path(hybrid), HYBRID_COMMIT, HYBRID),
        }

    def mutation(self, path, old, new):
        altered = copy.copy(self.original)
        count = altered[path].count(old)
        self.assertEqual(count, 1, "mutation anchor ambiguous/absent: " + path + " " + old[:50])
        altered[path] = altered[path].replace(old, new, 1)
        with self.assertRaises(SourceMismatch):
            check_source(altered)

    def test_01_real_sources_pass_with_restricted_receipt(self):
        receipt = check_source(self.original)
        self.assertEqual(receipt["result"], "PinnedNativeNormalReturnAndBridgeBoundaryOnly")
        self.assertEqual((receipt["pinnedNativeFiles"], receipt["pinnedHybridclrFiles"]), (3, 4))
        for key in (
            "exceptionalExitRollsBackRegistriesProven",
            "crossCallbackUsageLockExceptionSafe",
            "unknownPostCodecOutcomeRecoverable",
            "concurrentNativeVmReadersProven",
            "classGcMetadataLifetimeProven",
            "nativeProductionChanged", "realUnity", "R03Accepted",
            "H2Passed", "ReadyForHumanReviewGate",
        ):
            self.assertIs(receipt[key], False, key)
        self.assertEqual(receipt["handoffAuthority"], "CLOSED_NO_LOCAL_EXECUTION")

    def test_02_exact_file_inventory(self):
        altered = copy.copy(self.original)
        del altered[H_BRIDGE]
        with self.assertRaises(SourceMismatch):
            check_source(altered)
        altered = copy.copy(self.original)
        altered["unexpected.cpp"] = ""
        with self.assertRaises(SourceMismatch):
            check_source(altered)

    def test_03_metadata_lock_must_remain(self):
        self.mutation(N_METADATA,
                      "os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);\n    s_cliAssemblies.reserve",
                      "/* removed metadata lock */\n    s_cliAssemblies.reserve")

    def test_04_metadata_preallocation_must_remain(self):
        self.mutation(N_METADATA,
                      "s_cliAssemblies.reserve(s_cliAssemblies.size() + assemblies.size());",
                      "/* removed preallocation */")

    def test_05_assembly_preallocation_must_remain(self):
        self.mutation(N_REGISTRY,
                      "s_Assemblies.reserve(s_Assemblies.size() + assemblies.size());",
                      "/* removed preallocation */")

    def test_06_physical_registry_normal_rollback_must_remain(self):
        self.mutation(N_REGISTRY, "s_Assemblies.resize(originalSize);",
                      "/* no physical rollback */")

    def test_07_cli_registry_normal_rollback_must_remain(self):
        self.mutation(N_METADATA, "s_cliAssemblies.resize_uninitialized(originalSize);",
                      "/* no cli rollback */")

    def test_08_registry_begin_guard_must_remain(self):
        self.mutation(N_REGISTRY,
                      "if (!tryBegin(context)) return false;",
                      "/* begin guard removed */")

    def test_09_begin_usage_acquire_must_remain(self):
        self.mutation(N_SHADOW,
                      "        LockUsage();\n        publication.used = UsedClosureMember",
                      "        publication.used = UsedClosureMember")

    def test_10_begin_rejection_must_release(self):
        self.mutation(N_SHADOW,
                      "if (publication.used) { UnlockUsage(); return false; }",
                      "if (publication.used) { return false; }")

    def test_11_publish_failure_must_unlock(self):
        self.mutation(N_SHADOW,
                      "publication.runtimePublicationFailed = true;\n            UnlockUsage();",
                      "publication.runtimePublicationFailed = true;")

    def test_12_release_order_must_hold(self):
        self.mutation(N_SHADOW,
                      "s_active.store(publication.snapshot, std::memory_order_release);",
                      "s_active.store(publication.snapshot, std::memory_order_relaxed);")

    def test_13_commit_precommit_reset_must_remain(self):
        self.mutation(N_SHADOW,
                      "if (!MetadataCache::PublishInterpreterAssembliesBatch(assemblies, TryBeginPublication, PublishActive, &publication))\n    {\n        s_state.store(AssemblyShadowState::Validated, std::memory_order_release);",
                      "if (!MetadataCache::PublishInterpreterAssembliesBatch(assemblies, TryBeginPublication, PublishActive, &publication))\n    {\n        s_state.store(AssemblyShadowState::Committed, std::memory_order_release);")

    def test_14_ownership_release_must_remain_after_active(self):
        self.mutation(N_SHADOW,
                      "snapshot.release(); // Immutable active mapping is process-lifetime.",
                      "/* snapshot released by destructor */")

    def test_15_real_bridge_must_check_active_membership(self):
        self.mutation(H_BRIDGE,
                      "il2cpp::vm::AssemblyShadow::IsActiveShadow(image->GetIl2CppImage()->assembly)",
                      "il2cpp::vm::AssemblyShadow::IsCandidate(image->GetIl2CppImage()->assembly)")

    def test_16_real_bridge_must_check_image_identity(self):
        self.mutation(H_BRIDGE, "image->GetIndex() == imageIndex",
                      "true /* identity no longer checked */")

    def test_17_is_active_uses_acquire(self):
        self.mutation(N_SHADOW,
                      "bool AssemblyShadow::IsActiveShadow(const Il2CppAssembly* assembly)\n{\n    const ActiveSnapshot* active = s_active.load(std::memory_order_acquire);",
                      "bool AssemblyShadow::IsActiveShadow(const Il2CppAssembly* assembly)\n{\n    const ActiveSnapshot* active = s_active.load(std::memory_order_relaxed);")

    def test_18_runtime_group_activation_must_release(self):
        self.mutation(H_RUNTIME,
                      "current->groups[group].active.store(1, std::memory_order_release);",
                      "current->groups[group].active.store(1, std::memory_order_relaxed);")

    def test_19_runtime_public_requires_vm_bridge(self):
        self.mutation(H_RUNTIME,
                      "return AssemblyShadowBridge::IsPublicImage(record->reservation.imageId, image);",
                      "return image != nullptr;")

    def test_20_codec_lifecycle_must_release(self):
        self.mutation(H_CODEC, "image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),\n                std::memory_order_release);",
                      "image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Private),\n                std::memory_order_release);")

    def test_21_codec_must_reject_unsealed(self):
        self.mutation(H_CODEC, "if (!image->sealed)\n                return Error::Unfinalized;",
                      "if (false)\n                return Error::Unfinalized;")

    def test_22_state_must_be_committing_before_publish(self):
        self.mutation(N_SHADOW,
                      "s_state.store(AssemblyShadowState::Committing, std::memory_order_release);",
                      "s_state.store(AssemblyShadowState::Validated, std::memory_order_release);")

    def test_23_no_new_exception_conversion_without_review(self):
        self.mutation(N_REGISTRY,
                      "for (const Il2CppAssembly* assembly : assemblies) s_Assemblies.push_back(assembly);\n        if (!publish(context))",
                      "for (const Il2CppAssembly* assembly : assemblies) s_Assemblies.push_back(assembly);\n        try { publish(context); } catch (...) { return true; }\n        if (!publish(context))")

    def test_24_no_error_after_runtime_group_active(self):
        self.mutation(H_RUNTIME, "++current->nextPublicationGroup;\n    return Error::None;",
                      "++current->nextPublicationGroup;\n    return Error::InvalidState;")

    def test_25_no_error_after_codec_lifecycle_publish(self):
        self.mutation(H_CODEC,
                      "return Error::None;\n    }\n\n    Error Publish(",
                      "return Error::InvalidState;\n    }\n\n    Error Publish(")

    def test_26_no_disabled_stub_as_active(self):
        self.mutation(N_SHADOW,
                      "AssemblyShadowError AssemblyShadow::CommitTransaction() { return AssemblyShadowError::FeatureDisabled; }",
                      "AssemblyShadowError AssemblyShadow::CommitTransaction() { return AssemblyShadowError::Success; }")


if __name__ == "__main__":
    unittest.main()
