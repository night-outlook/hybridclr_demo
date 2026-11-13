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
        self.assertEqual(len(self.original["nativeSources"]),64)
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
        self.assertEqual(len(self.original["nativeSources"]),64)
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

    def test_original_field15_formatter_and_class_fact_scope(self):
        c=self.original["nativeSourceCapabilities"]
        required_true=(
            "originalV1ActualSerializerDifferentialHost",
            "originalV1SerializerUsesActualLiveR02",
            "originalV1SerializerUsesActualFrozenR02",
            "originalV1FormatterSameImmutableRowsOnly",
            "observedClassFactsTwoPassInNativeSource",
            "observedClassFactsNotCoherentVmEpoch",
        )
        required_false=(
            "originalV1RuntimeClassMetadataParityProven",
            "originalV1TerminalField15FormattingProven",
            "completeObservedClassLifetimeProven",
        )
        for key in required_true:
            self.assertTrue(c[key])
            wrong=copy.deepcopy(self.original)
            wrong["nativeSourceCapabilities"][key]=False
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(wrong)
        for key in required_false:
            self.assertFalse(c[key])
            wrong=copy.deepcopy(self.original)
            wrong["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(wrong)
        self.assertEqual(c["originalV1FormatterHostCases"],10)
        self.assertGreaterEqual(c["originalV1FormatterHostAssertions"],91)
        self.assertEqual(c["originalV1FormatterGuardedAllocations"],0)
        self.assertEqual(c["observedClassFactsBetweenPassMutationFailures"],2)
        self.assertEqual(c["observedClassFactsDuringTypeKeyMutationFailures"],1)
        self.assertGreaterEqual(c["mockScenarios"],76)
        self.assertGreaterEqual(c["mockAssertionsPerExecution"],1865)
        for field,val in (
            ("observedClassFactsDuringTypeKeyMutationFailures",0),
            ("mockScenarios",75),
            ("mockAssertionsPerExecution",1849),
        ):
            wrong=copy.deepcopy(self.original)
            wrong["nativeSourceCapabilities"][field]=val
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(wrong)
        self.assertEqual(c["observedClassFactsRegistrySlotLimit"],2048)
        self.assertEqual(c["observedClassFactsBytesPerSlot"],2)
        needed={
            "NativeHostTests/AssemblyShadowExecutionV1SerializerParityHost.cpp",
            ".github/workflows/r03-native-b2-execution-v1-serializer-parity-host.yml",
            "libil2cpp/vm/AssemblyShadowR02Snapshot.h",
            "libil2cpp/vm/AssemblyShadowObservationCounters.h",
            "libil2cpp/vm/AssemblyShadowObservationMemo.h",
            "libil2cpp/vm/AssemblyShadowDiagnosticsProfile.h",
        }
        self.assertTrue(needed.issubset(audit.NATIVE_REQUIRED))
        self.assertEqual({row["path"] for row in self.original["nativeSources"]},
                         audit.NATIVE_REQUIRED)

    def test_native_endpass_class_facts_acceptance_stays_scoped(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertEqual(c["physicalEnumerationPasses"],3)
        self.assertEqual(c["mockScenarios"],115)
        self.assertEqual(c["mockAssertionsPerExecution"],4656)
        self.assertTrue(c["observedClassFactsEndPassImplemented"])
        self.assertTrue(c["observedClassFactsEndPassNotVmEpoch"])
        self.assertFalse(c["observedClassFactsEndPassClassCountProvenInRealUnity"])
        self.assertEqual(c["observedClassFactsEndPassMutationFailures"],3)
        self.assertEqual(c["observedClassFactsEndPassEnumerationFailures"],2)
        for key,wrong in (
            ("physicalEnumerationPasses",2),
            ("mockScenarios",111),
            ("mockAssertionsPerExecution",4237),
            ("observedClassFactsEndPassImplemented",False),
            ("observedClassFactsEndPassMutationFailures",2),
            ("observedClassFactsEndPassEnumerationFailures",1),
            ("observedClassFactsEndPassVisitedSlotBytes",4096),
            ("observedClassFactsEndPassMaximumCallbacks",0),
            ("observedClassFactsEndPassNotVmEpoch",False),
            ("observedClassFactsEndPassClassCountProvenInRealUnity",True),
        ):
            broken=copy.deepcopy(self.original)
            broken["nativeSourceCapabilities"][key]=wrong
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(broken)

    def test_original_v1_plain_interpreter_definition_only(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertTrue(c["simpleInterpreterTypeDefSourceImplemented"])
        self.assertEqual(c["simpleInterpreterTypeDefMockPositives"],2)
        self.assertEqual(c["simpleInterpreterTypeDefMockNegatives"],5)
        self.assertTrue(c["simpleInterpreterOwnedViaOriginalV1PhysicalImages"])
        self.assertTrue(c["simpleInterpreterFirstEmplaceOwnerChecked"])
        for field in (
            "interpreterGenericCompositeTypeKeysSupported",
            "interpreterVarMvarExecutionTypeKeysSupported",
            "actualUnityInterpreterTypeDefParityProven",
            "wholeVmInterpreterClassLifetimeProven",
        ):
            self.assertIs(c[field],False,field)
        for field,mutated in (
            ("simpleInterpreterTypeDefSourceImplemented",False),
            ("simpleInterpreterTypeDefMockPositives",1),
            ("simpleInterpreterTypeDefMockNegatives",4),
            ("simpleInterpreterOwnedViaOriginalV1PhysicalImages",False),
            ("simpleInterpreterFirstEmplaceOwnerChecked",False),
            ("interpreterGenericCompositeTypeKeysSupported",True),
            ("interpreterVarMvarExecutionTypeKeysSupported",True),
            ("actualUnityInterpreterTypeDefParityProven",True),
            ("wholeVmInterpreterClassLifetimeProven",True),
        ):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=mutated
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)


    def test_interpreter_only_zero_aot_source_scope(self):
        c = self.original["nativeSourceCapabilities"]
        self.assertTrue(c["interpreterOnlyWithoutAotSourceSupportedInMock"])
        self.assertEqual(c["interpreterOnlyWithoutAotPositiveCases"], 2)
        self.assertEqual(c["interpreterOnlyWithoutAotNegativeCases"], 4)
        self.assertTrue(c["registeredAotSourceRequiredPerAotDefinition"])
        self.assertTrue(c["interpreterOnlyOriginalV1PhysicalOwnerStillRequired"])
        self.assertFalse(c["interpreterOnlyUnityPlayerProven"])
        self.assertFalse(c["interpreterOnlyFullField15OrVmEpochProven"])
        for field, wrong in (
            ("interpreterOnlyWithoutAotSourceSupportedInMock", False),
            ("interpreterOnlyWithoutAotPositiveCases", 1),
            ("interpreterOnlyWithoutAotNegativeCases", 3),
            ("registeredAotSourceRequiredPerAotDefinition", False),
            ("interpreterOnlyOriginalV1PhysicalOwnerStillRequired", False),
            ("interpreterOnlyUnityPlayerProven", True),
            ("interpreterOnlyFullField15OrVmEpochProven", True),
        ):
            altered = copy.deepcopy(self.original)
            altered["nativeSourceCapabilities"][field] = wrong
            with self.subTest(field=field), self.assertRaises(audit.Rejected):
                audit.validate_contract(altered)

    def test_interpreter_only_aot_guard_regressions(self):
        candidate = b"""if(!registeredAotImages.Healthy())
            return reject(live::Error::UnadmittedMetadataOwner);
receipt.registeredPhysicalAotImages=registeredAotImages.Count();
d.registry->Contains(img)
d.originalV1Images->Contains(img)
c.originalV1Images->Contains(constrained)
original_join::CheckFirstOwner(
!originalV1Images.Count()
"""
        audit.verify_interpreter_only_aot_gate(candidate)
        for before, after in (
            (b"if(!registeredAotImages.Healthy())",
             b"if(!registeredAotImages.Healthy() || !registeredAotImages.Count())"),
            (b"d.registry->Contains(img)", b"d.anyImage->Contains(img)"),
            (b"d.originalV1Images->Contains(img)", b"d.anyImage->Contains(img)"),
            (b"c.originalV1Images->Contains(constrained)",
             b"c.anyImage->Contains(constrained)"),
            (b"original_join::CheckFirstOwner(", b"AlwaysAcceptOwner("),
            (b"!originalV1Images.Count()", b"true"),
        ):
            self.assertIn(before, candidate)
            with self.subTest(before=before), self.assertRaises(audit.Rejected):
                audit.verify_interpreter_only_aot_gate(
                    candidate.replace(before, after, 1))

    def test_original_v1_physical_image_primitive_scope(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertTrue(c["originalV1ImageFactsTwoPassInNativeSource"])
        self.assertEqual(c["originalV1ImageFactsFields"],
                         ["typeCount","imageToken","assemblyToken"])
        self.assertEqual(c["originalV1ImageFactsMaxStackBytes"],12288)
        self.assertEqual(c["originalV1ImageFactsMutationFailures"],4)
        self.assertTrue(c["originalV1DuplicatePhysicalImageFailsClosed"])
        self.assertTrue(c["originalV1ImageFactsNotWholeVmEpoch"])
        self.assertFalse(c["originalV1ImageFactsTestedInUnity"])
        self.assertFalse(c["originalV1MetadataHandleMapStableProven"])
        for key,value in (
            ("originalV1ImageFactsTwoPassInNativeSource",False),
            ("originalV1ImageFactsFields",["typeCount","imageToken"]),
            ("originalV1ImageFactsMaxStackBytes",8192),
            ("originalV1ImageFactsMutationFailures",3),
            ("originalV1DuplicatePhysicalImageFailsClosed",False),
            ("originalV1ImageFactsNotWholeVmEpoch",False),
            ("originalV1ImageFactsTestedInUnity",True),
            ("originalV1MetadataHandleMapStableProven",True),
        ):
            modified=copy.deepcopy(self.original)
            modified["nativeSourceCapabilities"][key]=value
            with self.subTest(field=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(modified)

    def test_root_facts_provenance_remains_scoped(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertTrue(c["observedClassRootFactsThreePassInNativeSource"])
        self.assertEqual(c["observedClassRootFields"],
            ["image","definition","typeData","generic","typeCode"])
        self.assertEqual(c["observedClassRootMutationNegativeCases"],7)
        self.assertEqual(c["observedClassRootFactsSlotCount"],2048)
        self.assertEqual(c["observedClassRootFactsMaxBytes64"],53264)
        self.assertEqual(c["observedClassRootFactsAdditionalStackBytes64"],20496)
        self.assertTrue(c["observedClassRootUnionTagRestricted"])
        self.assertTrue(c["observedClassRootFactsNotWholeVmEpoch"])
        for field in ("observedClassRootGcLifetimeProven",
                      "observedClassRootMetadataContentStableProven",
                      "observedClassRootUnityPlayerVerified"):
            self.assertFalse(c[field])
        for field,value in (
            ("observedClassRootFactsThreePassInNativeSource",False),
            ("observedClassRootFields",["image","definition"]),
            ("observedClassRootMutationNegativeCases",6),
            ("observedClassRootFactsSlotCount",1024),
            ("observedClassRootFactsMaxBytes64",98304),
            ("observedClassRootFactsAdditionalStackBytes64",65536),
            ("observedClassRootFactsNotWholeVmEpoch",False),
            ("observedClassRootGcLifetimeProven",True),
            ("observedClassRootMetadataContentStableProven",True),
            ("observedClassRootUnityPlayerVerified",True),
            ("observedClassRootUnionTagRestricted",False),
        ):
            broken=copy.deepcopy(self.original)
            broken["nativeSourceCapabilities"][field]=value
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(broken)

    def test_dense_packed_class_facts_source_scope(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertTrue(c["packedClassFactsSourceImplemented"])
        self.assertEqual(c["packedClassFactsCapacity"],1024)
        self.assertEqual(c["packedClassFactsRegistrySlots"],2048)
        self.assertEqual(c["packedClassFactsSlotIndexBytes"],2)
        self.assertEqual(c["packedClassFactsMaxBytes64"],53264)
        self.assertEqual(c["packedClassFactsSavedStackBytes64AtLeast"],45040)
        self.assertEqual(c["packedClassFactsPureHostCases"],5)
        self.assertTrue(c["packedClassFactsEarlyRejectDestructorScrub"])
        for flag in ("packedClassFactsUsesHeapAllocation",
                     "packedClassFactsUnityStackVerified",
                     "packedClassFactsGcLifetimeProven",
                     "packedClassFactsWholeVmEpochProven"):
            self.assertIs(c[flag],False,flag)
        for field,changedValue in (
            ("packedClassFactsSourceImplemented",False),
            ("packedClassFactsCapacity",2048),
            ("packedClassFactsRegistrySlots",1024),
            ("packedClassFactsSlotIndexBytes",4),
            ("packedClassFactsMaxBytes64",98304),
            ("packedClassFactsSavedStackBytes64AtLeast",0),
            ("packedClassFactsPureHostCases",4),
            ("packedClassFactsEarlyRejectDestructorScrub",False),
            ("packedClassFactsUsesHeapAllocation",True),
            ("packedClassFactsUnityStackVerified",True),
            ("packedClassFactsGcLifetimeProven",True),
            ("packedClassFactsWholeVmEpochProven",True),
        ):
            bad=copy.deepcopy(self.original)
            bad["nativeSourceCapabilities"][field]=changedValue
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(bad)

    def test_original_v1_root_first_owner_endpass_scope(self):
        c=self.original["nativeSourceCapabilities"]
        self.assertTrue(c["originalV1RootFirstOwnerRecheckedAtEndPass"])
        self.assertEqual(c["originalV1RootFirstOwnerEndPassLookupLimit"],65536)
        self.assertEqual(c["originalV1RootFirstOwnerEndPassMutationFailures"],4)
        for key in ("originalV1RootFirstOwnerEndPassMatchedObservedOnly",
                    "originalV1RootFirstOwnerEndPassNoExtraClassTraversal",
                    "originalV1RootFirstOwnerEndPassNoAllocationSourceClaim",
                    "originalV1RootFirstOwnerEndPassNotCompleteTypeDefTable",
                    "originalV1RootFirstOwnerEndPassNoVmEpoch"):
            self.assertIs(c[key],True,key)
        for key in ("originalV1RootFirstOwnerEndPassRealUnityProven",
                    "originalV1RootFirstOwnerEndPassClassGcLifetimeProven",
                    "originalV1RootFirstOwnerEndPassWholeTableStableProven"):
            self.assertIs(c[key],False,key)
        for field,bad in (
            ("originalV1RootFirstOwnerRecheckedAtEndPass",False),
            ("originalV1RootFirstOwnerEndPassLookupLimit",0),
            ("originalV1RootFirstOwnerEndPassMutationFailures",3),
            ("originalV1RootFirstOwnerEndPassMatchedObservedOnly",False),
            ("originalV1RootFirstOwnerEndPassNoExtraClassTraversal",False),
            ("originalV1RootFirstOwnerEndPassNoAllocationSourceClaim",False),
            ("originalV1RootFirstOwnerEndPassNotCompleteTypeDefTable",False),
            ("originalV1RootFirstOwnerEndPassNoVmEpoch",False),
            ("originalV1RootFirstOwnerEndPassRealUnityProven",True),
            ("originalV1RootFirstOwnerEndPassClassGcLifetimeProven",True),
            ("originalV1RootFirstOwnerEndPassWholeTableStableProven",True),
        ):
            altered=copy.deepcopy(self.original)
            altered["nativeSourceCapabilities"][field]=bad
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(altered)

    def test_no_execution_authority_transmitted(self):
        self.assertEqual(self.original["handoffAuthority"],"CLOSED_NO_LOCAL_EXECUTION")
        self.assertEqual(self.original["nativeSourceCapabilities"]["sourceReadsAfterTerminal"],False)

class OriginalV1Field15InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = (HERE / "NativeDiagnostics" /
                         "OriginalV1ExecutionGetter_2026-11-12.txt").read_bytes()

    def test_complete_original_header_and_class_field_mapping(self):
        result = audit.inspect_original_v1_field15_contract(self.reference)
        self.assertEqual(result["sourceContract"],
                         "PassedExactOriginalV1Field15ValueInventory")
        self.assertEqual(len(result["headerFields"]), 11)
        self.assertEqual(len(result["classFields"]), 11)
        self.assertEqual(result["classFields"][0], "logicalAssembly")
        self.assertEqual(result["classFields"][-1], "staticStorageAvailable")
        self.assertEqual(result["r02Source"], "live_counters_after_class_rows")
        for key in ("classGcLifetimeProven", "completeBoundedField15Proven",
                    "terminalSafeField15Proven", "coherentVmEpochProven",
                    "nativeV2TransportImplemented", "runtimeAcceptance"):
            self.assertIs(result[key], False, key)

    def test_header_semantics_and_field_order_fail_closed(self):
        cases = (
            (b"heading.generation = active ? active->generation : 0;",
             b"heading.generation = 0;"),
            (b"heading.methodChecks = methodChecks;",
             b"heading.methodChecks = shadowChecks;"),
            (b"heading.shadowClassCctorStarted = s_shadowClassCctorStarted.load(std::memory_order_relaxed);",
             b"heading.shadowClassCctorStarted = 0;"),
            (b"heading.droppedClassObservations = s_droppedClassObservations.load(std::memory_order_relaxed);",
             b"heading.droppedClassObservations = 0;"),
        )
        for before, after in cases:
            self.assertIn(before, self.reference)
            with self.subTest(before=before), self.assertRaises(audit.Rejected):
                audit.inspect_original_v1_field15_contract(
                    self.reference.replace(before, after, 1))

    def test_class_field_semantics_and_completeness_fail_closed(self):
        cases = (
            (b"row.logicalAssembly = assembly_shadow_diagnostic::Quoted(owner->aname.name);",
             b"row.logicalAssembly = assembly_shadow_diagnostic::Quoted(\"constant\");"),
            (b"row.typeKey = assembly_shadow_diagnostic::Quoted(typeKey);",
             b"row.typeKey = assembly_shadow_diagnostic::Quoted(\"missing\");"),
            (b"row.interpreterShadow = baseline || shadow;",
             b"row.interpreterShadow = baseline;"),
            (b"row.isActive = !baseline;",
             b"row.isActive = baseline;"),
            (b"row.cctorStarted = started;",
             b"row.cctorStarted = finished;"),
            (b"row.hasInitializationException = exception;",
             b"row.hasInitializationException = false;"),
            (b"row.staticStorageAvailable = storage != nullptr;",
             b"row.staticStorageAvailable = false;"),
            (b"row.pointerDetailsAvailable = details;", b""),
        )
        for before, after in cases:
            self.assertIn(before, self.reference)
            with self.subTest(before=before), self.assertRaises(audit.Rejected):
                audit.inspect_original_v1_field15_contract(
                    self.reference.replace(before, after, 1))

    def test_source_identity_lifetime_and_live_r02_fail_closed(self):
        cases = (
            (b"for (Il2CppClass* klass : s_executionClasses)",
             b"for (Il2CppClass* klass : otherClasses)"),
            (b"Assembly::CaptureShadowEnumeration(assemblies)",
             b"Assembly::GetAllAssemblies(assemblies)"),
            (b"images.emplace(MetadataCache::GetAssemblyTypeHandle",
             b"images.insert(MetadataCache::GetAssemblyTypeHandle"),
            (b"FormatMetadataOnly(&klass->byval_arg, images)",
             b"GetName(&klass->byval_arg, images)"),
            (b"il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);", b""),
            (b"os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_started))",
             b"klass->cctor_started"),
            (b"#if IL2CPP_DEBUG\n        const bool details = true;",
             b"const bool details = true;"),
            (b"assembly_shadow_r02::AppendDiagnostics(output);", b""),
        )
        for before, after in cases:
            self.assertIn(before, self.reference)
            with self.subTest(before=before), self.assertRaises(audit.Rejected):
                audit.inspect_original_v1_field15_contract(
                    self.reference.replace(before, after, 1))

if __name__=="__main__":
    unittest.main()
