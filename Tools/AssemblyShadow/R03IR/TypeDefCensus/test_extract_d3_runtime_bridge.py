#!/usr/bin/env python3
"""D3 two-repo exact source and adversarial observer-path mutation tests."""
import copy
import os
import unittest
from pathlib import Path
from extract_d3_runtime_bridge import (
    NATIVE_HEAD,HYBRID_HEAD,NATIVE,HYBRID,N_SHADOW,N_DECISION,
    H_RUNTIME,H_STAGED,H_IMAGE,extract,read_pinned,SourceMismatch
)

class D3ExactRuntimeBridgeSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        n=os.environ.get("R03_B2_D3_NATIVE_ROOT")
        h=os.environ.get("R03_B2_D3_HYBRID_ROOT")
        if not n or not h:
            raise RuntimeError("Both exact native and Runtime repositories required")
        cls.native=read_pinned(Path(n),NATIVE_HEAD,NATIVE)
        cls.hybrid=read_pinned(Path(h),HYBRID_HEAD,HYBRID)

    def mutated(self,repo,path,old,new):
        native=copy.copy(self.native)
        hybrid=copy.copy(self.hybrid)
        dest=native if repo=="native" else hybrid
        self.assertIn(old,dest[path])
        dest[path]=dest[path].replace(old,new,1)
        with self.assertRaises(SourceMismatch):extract(native,hybrid)

    def test_01_exact_sources(self):
        code,items=extract(self.native,self.hybrid)
        self.assertEqual(len(items),9)
        self.assertIn("ObserveCodecAttempt",code)
        self.assertIn("ObserveRuntimeGroupPublished",code)
        self.assertIn("PublishActive",code)

    def test_02_authority_and_inventory(self):
        self.assertEqual(len(NATIVE),3)
        self.assertEqual(len(HYBRID),8)
        self.assertEqual(len(NATIVE_HEAD),40)
        self.assertEqual(len(HYBRID_HEAD),40)

    def test_03_missing_attempt_callback(self):
        self.mutated("hybrid",H_RUNTIME,"observer->beforeCodec(observer->context)",
                     "observer->afterRuntimeGroup(observer->context)")

    def test_04_removed_after_group_callback(self):
        self.mutated("hybrid",H_RUNTIME,"observer->afterRuntimeGroup(observer->context)",
                     "observer->beforeCodec(observer->context)")

    def test_05_codec_call_before_attempt(self):
        s=self.hybrid[H_RUNTIME]
        begin="    if (observer && !observer->beforeCodec(observer->context))\n        return Error::InvalidState;\n"
        self.assertIn(begin,s)
        self.mutated("hybrid",H_RUNTIME,begin,"")

    def test_06_group_callback_before_active(self):
        self.mutated("hybrid",H_RUNTIME,
                     "    if (observer && !observer->afterRuntimeGroup(observer->context))",
                     "    if (observer && !observer->beforeCodec(observer->context))")

    def test_07_missing_staged_forwarding(self):
        self.mutated("hybrid",H_STAGED,
                     "imageIndices.data(), imageIndices.size(), observer",
                     "imageIndices.data(), imageIndices.size(), nullptr")

    def test_08_missing_image_forwarding(self):
        self.mutated("hybrid",H_IMAGE,
                     "PublishBatch(imageIndices, count, observer)",
                     "PublishBatch(imageIndices, count)")

    def test_09_missing_native_callback(self):
        self.mutated("native",N_SHADOW,
                     "ObserveCodecAttempt, ObserveRuntimeGroupPublished, context",
                     "nullptr, ObserveRuntimeGroupPublished, context")

    def test_10_native_legacy_codec_false(self):
        self.mutated("native",N_SHADOW,
                     "ClassifyFailedNativeBatch(",
                     "LegacyUnsafeClassify(")

    def test_11_removed_terminal_latch(self):
        self.mutated("native",N_SHADOW,
                     "s_unexpectedFailure.store(true, std::memory_order_release);",
                     "s_unexpectedFailure.store(false, std::memory_order_release);")

    def test_12_lost_phase_receipt(self):
        self.mutated("native",N_SHADOW,
                     "publication.phaseReceipt = &publicationPhase;",
                     "publication.phaseReceipt = nullptr;")

    def test_13_missing_group_verification(self):
        self.mutated("native",N_SHADOW,
                     "assembly_shadow_publication::Phase::RuntimeGroupPublished",
                     "assembly_shadow_publication::Phase::RegistriesAppended")

    def test_14_missing_classifier(self):
        self.mutated("native",N_DECISION,
                     "ClassifyFailedNativeBatch(",
                     "ClassifyUnsafeBatch(")

    def test_15_source_inventory(self):
        n=copy.copy(self.native);n["extra"]="x"
        with self.assertRaises(SourceMismatch):extract(n,self.hybrid)
        h=copy.copy(self.hybrid);h.pop(H_RUNTIME)
        with self.assertRaises(SourceMismatch):extract(self.native,h)

if __name__=="__main__":unittest.main()
