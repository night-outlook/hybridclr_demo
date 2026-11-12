"""Negative and exact-source admission contract tests, no Unity required."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import b2_definition_source_gate as audit

HERE=Path(__file__).resolve().parent
class SourceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((HERE/"b2_definition_native_candidate.json").read_text())

    def test_manifest_is_pinned_but_explicitly_not_v2(self):
        audit.validate_contract(self.original)
        self.assertFalse(self.original["runtimeAcceptance"])
        self.assertFalse(self.original["readyForNativeV2FieldCapture"])

    def test_product_promotions_all_rejected(self):
        for key in ("runtimeAcceptance","R03Accepted","H2Passed",
                    "ReadyForHumanReviewGate","nativeV2TransportImplemented",
                    "readyForNativeV2FieldCapture"):
            changed=copy.deepcopy(self.original);changed[key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_wrong_branch_and_handoff_authority_rejected(self):
        for key,value in (("branch","main"),
                          ("handoffAuthority","OpenForLocal"),
                          ("candidateNative","0"*39+"g"),
                          ("originalB1Native","bad")):
            changed=copy.deepcopy(self.original);changed[key]=value
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_missing_or_added_source_is_rejected(self):
        for key in ("nativeSources","demoPureSources"):
            for mutation in ("pop","duplicate"):
                changed=copy.deepcopy(self.original)
                if mutation=="pop":changed[key].pop()
                else:changed[key].append(copy.deepcopy(changed[key][0]))
                with self.subTest(key=key,mutation=mutation),self.assertRaises(audit.Rejected):
                    audit.validate_contract(changed)

    def test_source_roster_wrong_blob_shape(self):
        changed=copy.deepcopy(self.original)
        changed["nativeSources"][0]["gitBlob"]="hello"
        with self.assertRaises(audit.Rejected):
            audit.validate_contract(changed)
        # Format is checked on the actual file; invalid blob cannot be admitted.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            (root/"sample").write_bytes(b"a")
            with self.assertRaises(audit.Rejected):
                audit.verify_file(root,"sample","hello")

    def test_actual_git_blob_header(self):
        raw=b"physical-native-source"
        expected=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
        self.assertEqual(audit.blob(raw),expected)
        self.assertNotEqual(audit.blob(raw),audit.blob(raw+b" "))

    def test_tree_sha_and_content_must_both_match(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve();(root/"x.h").write_bytes(b"data")
            digest=audit.blob(b"data")
            with patch.object(audit,"git",return_value="100644 blob "+digest+"\tx.h"):
                self.assertEqual(audit.verify_file(root,"x.h",digest),b"data")
            with patch.object(audit,"git",return_value=""):
                with self.assertRaises(audit.Rejected):
                    audit.verify_file(root,"x.h",digest)

    def test_symlink_alias_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            (root/"real").write_bytes(b"data")
            (root/"link").symlink_to(root/"real")
            with self.assertRaises(audit.Rejected):
                audit.verify_file(root,"link",audit.blob(b"data"))

    def test_unsafe_paths_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            for unsafe in ("../escape","/absolute","some/../escape","bad"+chr(0)+"path"):
                with self.subTest(unsafe=repr(unsafe)),self.assertRaises(audit.Rejected):
                    audit.verify_file(root,unsafe,"0"*40)

    def test_structural_source_drift_is_rejected(self):
        snippets={p: b"" for p in audit.NATIVE_REQUIRED}
        with self.assertRaises(audit.Rejected):
            audit.source_boundary(snippets)

    def test_historical_four_repo_pins_are_frozen(self):
        for key in ("originalB1ExecutionDemo","originalB1Native",
                    "hybridclr","hybridclr_unity"):
            changed=copy.deepcopy(self.original)
            changed[key]="0"*40
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_terminal_and_epoch_capabilities_cannot_be_promoted(self):
        for key in ("sourceReadsAfterTerminal",
                    "arbitraryGenericInstantiationTypeKeys",
                    "unrestrictedCrossImageGenericArgumentsSupported",
                    "realUnityRuntimeIntegrationProven",
                    "coherentVmEpochProven"):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_generic_source_limits_cannot_be_relaxed(self):
        for field,bad in (("genericArgumentLimit",17),
                          ("genericOwnedOutputByteLimit",8192),
                          ("legacyTypeKeyGrammarSourceBlob","0"*40),
                          ("realGenericRuntimeMetadataAbiBlob","0"*40)):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=bad
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_cross_image_physical_inventory_capability_cannot_be_overstated(self):
        for key,bad in (
            ("crossImageUnregisteredArgumentFailsClosed",False),
            ("unregisteredAotArgumentFailsClosed",False),
            ("registeredUnobservedArgumentSupportedInMock",False),
            ("registeredAotImageSetDoubleChecked",False),
            ("registeredImageSetOnlyObservational",False),
            ("originalAssemblyRegistrySnapshotIncompleteForFullVmEpoch",False),
            ("realAssemblyCppUnityCompiled",True),
            ("runtimeAcceptanceProven",True),
            ("ambiguousMetadataOwnerFailsClosed",False),
            ("crossImageGenericArgumentsSupportedInMock",False),
            ("allPhysicalMetadataImagesEnumerated",True),
            ("physicalImageLimit",65),
            ("registeredAotImageLimit",1025),
            ("zeroTypeDefinitionRegisteredAotImagesSkipped",False),
            ("registeredAssemblyRegistryVisits",1),
            ("physicalEnumerationPasses",1)):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=bad
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_ambiguous_legacy_capability_keys_are_rejected(self):
        for key in ("crossImageGenericArgumentsSupported",
                    "crossImageOnlyWhenBothImagesMatchedObservedClass",
                    "crossImageUnmatchedArgumentFailsClosed"):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_composite_contract_is_bounded_and_never_full_v2(self):
        caps=self.original["nativeSourceCapabilities"]
        self.assertIs(caps["boundedCompositeArgumentShapesInMock"],True)
        self.assertIs(caps["fullLegacyNonemptyExecutionParityProven"],False)
        self.assertIs(caps["arbitraryPrimitiveGenericArgumentKeys"],False)
        for field,value in (
            ("boundedCompositeArgumentShapesInMock",False),
            ("compositeMaximumDepth",9),
            ("arrayDimensionListLimit",33),
            ("compositeCoverageReceiptRevokedOnFailure",False),
            ("arbitraryPrimitiveGenericArgumentKeys",True),
            ("fullLegacyNonemptyExecutionParityProven",True),
        ):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=value
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_pure_composite_header_and_host_are_source_pinned(self):
        self.assertIn("libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h",
                      audit.NATIVE_REQUIRED)
        self.assertIn("NativeHostTests/AssemblyShadowOwnedCompositeTypeKeyHost.cpp",
                      audit.NATIVE_REQUIRED)
        self.assertIn(".github/workflows/r03-native-b2-composite-typekey-host.yml",
                      audit.NATIVE_REQUIRED)
        self.assertIn(
            "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedCompositeTypeKey.h",
            audit.DEMO_REQUIRED)
        self.assertEqual(len(self.original["nativeSources"]),len(audit.NATIVE_REQUIRED))
        self.assertEqual(len(self.original["demoPureSources"]),len(audit.DEMO_REQUIRED))

    def test_reference_unicode_fold_pinned_without_full_runtime_parity(self):
        caps=self.original["nativeSourceCapabilities"]
        self.assertTrue(caps["originalUnicodeAssemblyFoldBoundInVmSource"])
        self.assertTrue(caps["originalNameTableParityHostOnly"])
        self.assertTrue(caps["ownedUtf16FoldNoAllocationHostVerified"])
        self.assertFalse(caps["realUnityUnicodeMetadataParityProven"])
        self.assertFalse(caps["openGenericExecutionTypeKeysSupported"])
        for field,value in (
            ("originalUnicodeAssemblyFoldBoundInVmSource",False),
            ("originalNameTableParityHostOnly",False),
            ("ownedUtf16FoldNoAllocationHostVerified",False),
            ("realUnityUnicodeMetadataParityProven",True),
            ("openGenericExecutionTypeKeysSupported",True),
        ):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=value
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_reference_unicode_sources_and_hosts_are_all_exact_pins(self):
        expected={
            "libil2cpp/vm/AssemblyShadowName.h",
            "libil2cpp/vm-utils/VmStringUtils.cpp",
            "libil2cpp/vm-utils/VmStringUtils.h",
            "libil2cpp/utils/StringUtils.cpp",
            "libil2cpp/char-conversions.cpp",
            "libil2cpp/char-conversions.h",
            "NativeHostTests/AssemblyShadowFoldedNameMock.h",
            "NativeHostTests/AssemblyShadowOwnedFoldedDefinitionHost.cpp",
            "NativeHostTests/AssemblyShadowNameReferenceParityHost.cpp",
            "NativeHostTests/ShadowNameParityShim/il2cpp-config.h",
            ".github/workflows/r03-native-b2-folded-assembly-host.yml",
            ".github/workflows/r03-native-b2-original-unicode-name-parity.yml",
        }
        self.assertTrue(expected.issubset(audit.NATIVE_REQUIRED))
        self.assertEqual(
            {row["path"] for row in self.original["nativeSources"]},
            audit.NATIVE_REQUIRED)
        self.assertEqual(len(self.original["nativeSources"]),57)
        self.assertEqual(len(self.original["demoPureSources"]),8)

    def test_bounded_existing_primitive_defaults_and_noncreating_source_contract(self):
        c=self.original["nativeSourceCapabilities"]
        for key in ("primitiveDefaultClassLookupNoAllocationSourcePinned",
                    "primitiveArgumentsWithRegisteredAotTypeDefSupportedInMock",
                    "primitiveClassNameAncestryChecked",
                    "primitiveGenericContainerRejected",
                    "assertFreePrimitiveDefaultLookup",
                    "primitiveDefaultExactSwitchParity",
                    "unownedPrimitiveDefaultsRejected"):
            self.assertTrue(c[key])
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=False
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)
        for key in ("realUnityPrimitiveField15ParityProven",
                    "arbitraryPrimitiveGenericArgumentKeys"):
            self.assertFalse(c[key])
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)
        self.assertIn("libil2cpp/il2cpp-class-internals.h",audit.NATIVE_REQUIRED)
        self.assertIn("libil2cpp/vm/AssemblyShadowExistingPrimitiveDefaults.h",audit.NATIVE_REQUIRED)
        self.assertIn("libil2cpp/vm/Class.cpp",audit.NATIVE_REQUIRED)
        self.assertIn("libil2cpp/vm/Class.h",audit.NATIVE_REQUIRED)
        self.assertEqual({e["path"] for e in self.original["nativeSources"]},
                         audit.NATIVE_REQUIRED)

    def test_null_safe_primitive_peek_case_roster_must_remain_complete(self):
        caps=self.original["nativeSourceCapabilities"]
        self.assertEqual(caps["primitivePeekHostCases"],20)
        changed=copy.deepcopy(self.original)
        changed["nativeSourceCapabilities"]["primitivePeekHostCases"]=19
        with self.assertRaises(audit.Rejected):
            audit.validate_contract(changed)

    def test_v1_observational_byte_probe_is_not_a_terminal_field(self):
        caps=self.original["nativeSourceCapabilities"]
        for flag in ("observationalOriginalV1ByteProbeImplemented",
                     "legacyV1GetterUnchanged",
                     "parityMismatchRevokesBoundedSource",
                     "paritySourceMockUsesFakeLegacyGetter"):
            self.assertTrue(caps[flag])
            wrong=copy.deepcopy(self.original)
            wrong["nativeSourceCapabilities"][flag]=False
            with self.subTest(flag=flag),self.assertRaises(audit.Rejected):
                audit.validate_contract(wrong)
        for flag in ("observedActualOriginalV1ByteEqualityInUnity",
                     "twoObservationsAreOneCoherentVmEpoch",
                     "completeNativeField15Proven"):
            self.assertFalse(caps[flag])
            wrong=copy.deepcopy(self.original)
            wrong["nativeSourceCapabilities"][flag]=True
            with self.subTest(flag=flag),self.assertRaises(audit.Rejected):
                audit.validate_contract(wrong)
        self.assertTrue(caps["legacyGetterByteExactFixturePinned"])
        self.assertFalse(caps["legacyLogicalPhysicalImageMapParityProven"])
        self.assertFalse(caps["realUnityOriginalGetterProbeTested"])
        self.assertEqual(caps["legacyGetterReferenceCommit"],
                         "68530d7ecb86c9122d9ae5eb20366ccb0ea086b6")
        for field,value in (
            ("legacyGetterByteExactFixturePinned",False),
            ("legacyLogicalPhysicalImageMapParityProven",True),
            ("realUnityOriginalGetterProbeTested",True),
            ("legacyGetterReferenceCommit","0"*40),
        ):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=value
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)
        self.assertEqual(caps["parityHostCases"],10)
        self.assertEqual(caps["paritySourceMockCases"],3)
        self.assertGreaterEqual(caps["parityMockAssertionsPerExecution"],1258)

    def test_original_and_frozen_parity_sources_are_exact_pinned(self):
        expected={
            "libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h",
            "libil2cpp/vm/AssemblyShadowExecutionV1ByteParitySource.inl",
            "libil2cpp/vm/AssemblyShadowAdmittedExecutionDiagnosticsSource.inl",
            "libil2cpp/vm/AssemblyShadowExecutionSerializer.h",
            "libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h",
            "libil2cpp/vm/AssemblyShadowMetadataLifetime.h",
            "libil2cpp/vm/AssemblyShadowR02Diagnostics.h",
            "libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h",
            "libil2cpp/vm/AssemblyShadowDiagnosticWriter.h",
            "NativeHostTests/AssemblyShadowExecutionV1ByteParityHost.cpp",
            ".github/workflows/r03-native-b2-v1-parity-host.yml",
        }
        self.assertTrue(expected.issubset(audit.NATIVE_REQUIRED))
        self.assertEqual(len(self.original["nativeSources"]),57)
        self.assertEqual(len(self.original["demoPureSources"]),8)
        self.assertIn(
            "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedObservedExecutionV1ByteParity.h",
            audit.DEMO_REQUIRED)

    def test_original_execution_getter_must_remain_byte_identical(self):
        fixture=(HERE/"NativeDiagnostics"/
                 "OriginalV1ExecutionGetter_2026-11-12.txt").read_bytes()
        start=b"prefix"+bytes([10])
        end=(b"// P1 inactive reader around the original "
             b"(unmodified) V1 getter.")
        fallback=(b"AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(std::string& json)"
                  +bytes([10])+b"{"+bytes([10])
                  +b"    json.clear();"+bytes([10])
                  +b"    return AssemblyShadowError::FeatureDisabled;"+bytes([10])
                  +b"}"+bytes([10]))
        source=start+fixture+end+bytes([10])+fallback
        audit.verify_legacy_getter_unchanged(source,fixture)
        changed=bytearray(fixture)
        changed[100]=ord("!") if changed[100]!=ord("!") else ord("?")
        for corruptSource,corruptFixture in (
            (source,bytes(changed)),
            (start+bytes(changed)+end+bytes([10])+fallback,fixture),
            (start+fixture,fixture),
            (start+fixture+end,fixture),
            (source+end,fixture),
        ):
            with self.assertRaises(audit.Rejected):
                audit.verify_legacy_getter_unchanged(
                    corruptSource,corruptFixture)

    def test_original_v1_token_valid_physical_first_owner_contract(self):
        c=self.original["nativeSourceCapabilities"]
        for key in (
            "originalV1PhysicalTokenValidEnumeration",
            "originalV1IncludesInterpreterImages",
            "originalV1FirstEmplaceOwnerJoinSourceImplemented",
            "originalV1OwnerConflictRevokesSource",
            "originalV1ImageInventoryDoubleChecked",
        ):
            self.assertTrue(c[key])
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=False
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)
        for key in (
            "originalV1FullField15ParityProven",
            "actualUnityOriginalV1OwnerJoinTested",
            "originalV1ImagesAreLogicalShadowView",
        ):
            self.assertFalse(c[key])
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)
        self.assertEqual(c["originalV1JoinHostCases"],12)
        self.assertGreaterEqual(c["originalV1JoinHostAssertions"],41)
        for key,newValue in (("originalV1JoinHostCases",11),
                             ("originalV1JoinHostAssertions",0)):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=newValue
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_original_v1_image_and_join_sources_exactly_mirrored(self):
        for filename in ("BoundedOriginalV1ImageScan.h",
                         "BoundedOriginalV1OwnerJoin.h"):
            path="Tools/AssemblyShadow/R03IR/NativeDiagnostics/"+filename
            self.assertIn(path,audit.DEMO_REQUIRED)
        for filename in ("AssemblyShadowOriginalV1ImageScan.h",
                         "AssemblyShadowOriginalV1OwnerJoin.h"):
            self.assertIn("libil2cpp/vm/"+filename,audit.NATIVE_REQUIRED)
        self.assertEqual({r["path"] for r in self.original["nativeSources"]},
                         audit.NATIVE_REQUIRED)
        self.assertEqual({r["path"] for r in self.original["demoPureSources"]},
                         audit.DEMO_REQUIRED)

    def test_no_execution_authority_transmitted(self):
        self.assertEqual(self.original["handoffAuthority"],"CLOSED_NO_LOCAL_EXECUTION")
        self.assertEqual(self.original["nativeSourceCapabilities"]["sourceReadsAfterTerminal"],False)

if __name__=="__main__":
    unittest.main()
