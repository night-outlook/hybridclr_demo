#!/usr/bin/env python3
"""D4 exact-source provenance, publication ordering and failure mutation tests."""
import copy
import os
import unittest
from pathlib import Path

from extract_d4_snapshot_ownership import (
    NATIVE_HEAD, HYBRID_HEAD, NATIVE, HYBRID, N_SHADOW, N_OWNER,
    N_ASSEMBLY, N_METADATA, SourceMismatch, read_pinned, extract
)

class D4ExactOwnership(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native=os.environ.get("R03_D4_NATIVE_ROOT")
        hybrid=os.environ.get("R03_D4_HYBRID_ROOT")
        if not native or not hybrid:
            raise RuntimeError("D4 requires both exact native and hybridclr source roots")
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

    def test_01_exact_body_inventory(self):
        cpp,bodies=extract(self.native,self.hybrid)
        self.assertEqual(len(bodies),22)
        self.assertEqual(len(set(x["label"] for x in bodies)),22)
        self.assertIn("ScopedPostActiveExit",cpp)
        self.assertIn("PublishActive",cpp)
        self.assertIn("ScopedCliRollback",cpp)
        self.assertIn("Assembly::PublishStagedImagesBatch",cpp)

    def test_02_exact_source_roster(self):
        self.assertEqual(len(NATIVE),12)
        self.assertEqual(len(HYBRID),8)
        self.assertEqual(len(NATIVE_HEAD),40)
        self.assertEqual(len(HYBRID_HEAD),40)

    def test_03_owner_move_required(self):
        self.reject("native",N_OWNER,"retained_ = std::move(pending);",
                    "/* omitted process ownership move */")

    def test_04_owner_publication_must_follow_move(self):
        original=("        retained_ = std::move(pending); // std::unique_ptr default deleter, noexcept\n"
                  "        published.store(retained_.get(), std::memory_order_release);")
        changed=("        published.store(pending.get(), std::memory_order_release);\n"
                 "        retained_ = std::move(pending);")
        self.reject("native",N_OWNER,original,changed)

    def test_05_owner_cannot_republish(self):
        self.reject("native",N_OWNER,"if (!pending || retained_ || published.load",
                    "if (!pending || published.load")

    def test_06_p5_must_not_precede_owner_transfer(self):
        self.reject("native",N_SHADOW,
                    "publication.transaction->activeOwner.TryPublish(",
                    "publication.transaction->activeOwner.TrySkipPublish(")

    def test_07_p5_actual_phase_required(self):
        self.reject("native",N_SHADOW,
                    "assembly_shadow_publication::Phase::ActiveSnapshotPublished",
                    "assembly_shadow_publication::Phase::RuntimeGroupPublished")

    def test_08_pending_owner_handoff_required(self):
        self.reject("native",N_SHADOW,"publication.pendingSnapshot = &snapshot;",
                    "publication.pendingSnapshot = nullptr;")

    def test_09_transaction_owning_slot_required(self):
        self.reject("native",N_SHADOW,
                    "ProcessSnapshotOwner<ActiveSnapshot> activeOwner;",
                    "ProcessSnapshotOwner<ActiveSnapshot> misplacedOwner;")

    def test_10_no_local_release_after_publication(self):
        self.reject("native",N_SHADOW,
                    "ScopedPostActiveExit postActiveExit(publicationPhase);",
                    "snapshot.release(); ScopedPostActiveExit postActiveExit(publicationPhase);")

    def test_11_p6_phase_before_initializers(self):
        self.reject("native",N_SHADOW,
                    "if (!publicationPhase.Advance(\n            assembly_shadow_publication::Phase::InitializersRunning))",
                    "if (!publicationPhase.Advance(\n            assembly_shadow_publication::Phase::ActiveSnapshotPublished))"

    def test_12_completion_required(self):
        self.reject("native",N_SHADOW,
                    "if (!publicationPhase.Complete())",
                    "if (true)")

    def test_13_post_active_guard_must_seal(self):
        self.reject("native",N_SHADOW,
                    "phaseReceipt->MarkTerminal(phaseReason);",
                    "/* incorrectly ignored postactive phase failure */")

    def test_14_post_active_guard_must_deny_execution(self):
        self.reject("native",N_SHADOW,
                    "s_state.store(AssemblyShadowState::FailedAfterCommit,",
                    "s_state.store(AssemblyShadowState::Committed,")

    def test_15_postactive_first_error_required(self):
        self.reject("native",N_SHADOW,
                    "            s_firstFailureV2.TryFreeze(\n                static_cast<int32_t>(AssemblyShadowError::InternalError),\n                assembly_shadow_first_failure_v2::Origin::UnexpectedFailure,",
                    "            /* first error omitted */ (\n                static_cast<int32_t>(AssemblyShadowError::InternalError),\n                assembly_shadow_first_failure_v2::Origin::UnexpectedFailure,")

    def test_16_d3_lease_terminal_must_survive(self):
        self.reject("native",N_SHADOW,
                    "SealFailedPublicationBeforeUsageUnlock(publication);",
                    "/* removed lease seal */")

    def test_17_d2_physical_rollback_must_survive(self):
        self.reject("native",N_ASSEMBLY,
                    "entries.resize(previousSize);",
                    "/* removed physical rollback */")

    def test_18_d2_cli_rollback_must_survive(self):
        self.reject("native",N_METADATA,
                    "~ScopedCliRollback() noexcept",
                    "~SkippedRollback() noexcept")

    def test_19_no_untracked_native_source(self):
        native=copy.copy(self.native)
        native["unexpected"]="extra"
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(native,self.hybrid)

    def test_20_missing_runtime_source_rejected(self):
        hybrid=copy.copy(self.hybrid)
        hybrid.pop("hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp")
        with self.assertRaises((SourceMismatch,ValueError)):
            extract(self.native,hybrid)

if __name__=="__main__":
    unittest.main()
