"""Read-only exact-source proof for an INACTIVE restricted B2 native producer.

This is not a Unity build, complete V2 field15, an executable source admission,
an independent metadata lifetime proof, or authorization to run Local Validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MANIFEST="Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json"
FIXED_B1_DEMO="2d690bb2f7234ddcbee339f9da7125d687f5ed45"
FIXED_B1_NATIVE="8aa8d09319a89b55b2496bcc2c69ccc69cb57be9"
FIXED_HYBRIDCLR="4b2774b066cfc6afd77a8c8aded6bda7ea574f55"
FIXED_UNITY="948c0e3b4f8891481301770115e8ba4945eea6de"
NATIVE_REQUIRED={
    "libil2cpp/il2cpp-runtime-metadata.h",
    "libil2cpp/il2cpp-class-internals.h",
    "libil2cpp/vm/AssemblyShadow.cpp",
    "libil2cpp/vm/Class.cpp",
    "libil2cpp/vm/AssemblyShadowExistingPrimitiveDefaults.h",
    "libil2cpp/vm/Class.h",
    "libil2cpp/vm/Assembly.cpp",
    "libil2cpp/vm/Assembly.h",
    "libil2cpp/vm/AssemblyShadowRegisteredAotImageScan.h",
    "libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h",
    "libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h",
    "libil2cpp/vm/AssemblyShadowObservedPhysicalImages.h",
    "libil2cpp/vm/MemoryInformation.cpp",
    "libil2cpp/il2cpp-api.cpp",
    "libil2cpp/os/Posix/MutexImpl.h",
    "libil2cpp/os/Win32/MutexImpl.h",
    "libil2cpp/vm/GlobalMetadataFileInternals.h",
    "libil2cpp/vm/AssemblyShadow.h",
    "libil2cpp/vm/AssemblyShadowTypeKey.cpp",
    "libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h",
    "libil2cpp/vm/AssemblyShadowExecutionV1ByteParitySource.inl",
    "libil2cpp/vm/AssemblyShadowAdmittedExecutionDiagnosticsSource.inl",
    "libil2cpp/vm/AssemblyShadowExecutionSerializer.h",
    "libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h",
    "libil2cpp/vm/AssemblyShadowMetadataLifetime.h",
    "libil2cpp/vm/AssemblyShadowR02Diagnostics.h",
    "libil2cpp/vm/AssemblyShadowR02Snapshot.h",
    "libil2cpp/vm/AssemblyShadowObservationCounters.h",
    "libil2cpp/vm/AssemblyShadowObservationMemo.h",
    "libil2cpp/vm/AssemblyShadowDiagnosticsProfile.h",
    "libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h",
    "libil2cpp/vm/AssemblyShadowDiagnosticWriter.h",
    "libil2cpp/vm/AssemblyShadowName.h",
    "libil2cpp/vm-utils/VmStringUtils.cpp",
    "libil2cpp/vm-utils/VmStringUtils.h",
    "libil2cpp/utils/StringUtils.cpp",
    "libil2cpp/char-conversions.cpp",
    "libil2cpp/char-conversions.h",
    "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
    "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
    "libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h",
    "libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
    "libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h",
    "NativeHostTests/AssemblyShadowOwnedCompositeTypeKeyHost.cpp",
    ".github/workflows/r03-native-b2-composite-typekey-host.yml",
    "libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h",
    "NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp",
    "NativeHostTests/AssemblyShadowExecutionV1SerializerParityHost.cpp",
    ".github/workflows/r03-native-b2-execution-v1-serializer-parity-host.yml",
    "NativeHostTests/AssemblyShadowOriginalV1OwnerJoinHost.cpp",
    ".github/workflows/r03-native-b2-original-v1-owner-join-host.yml",
    "NativeHostTests/AssemblyShadowExecutionV1ByteParityHost.cpp",
    ".github/workflows/r03-native-b2-v1-parity-host.yml",
    "NativeHostTests/AssemblyShadowFoldedNameMock.h",
    "NativeHostTests/AssemblyShadowOwnedFoldedDefinitionHost.cpp",
    "NativeHostTests/AssemblyShadowNameReferenceParityHost.cpp",
    "NativeHostTests/ShadowNameParityShim/il2cpp-config.h",
    ".github/workflows/r03-native-b2-folded-assembly-host.yml",
    ".github/workflows/r03-native-b2-original-unicode-name-parity.yml",
    "NativeHostTests/AssemblyShadowOwnedConstructedTypeKeyHost.cpp",
    ".github/workflows/r03-native-b2-definition-live-source-host.yml",
    ".github/workflows/r03-native-b2-constructed-typekey-host.yml",
    "NativeHostTests/README.md",
}
DEMO_REQUIRED={
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedDefinitionTypeKey.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedObservedExecutionV1ByteParity.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOriginalV1ImageScan.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOriginalV1OwnerJoin.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/OriginalV1ExecutionGetter_2026-11-12.txt",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedConstructedTypeKey.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedCompositeTypeKey.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedExecutionRows.h",
}
class Rejected(ValueError):
    pass

def require(value:bool,what:str):
    if not value:
        raise Rejected(what)

def git(root:Path,*args:str)->str:
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,
                     text=True,timeout=30)
    require(p.returncode==0,"git failed: "+" ".join(args))
    return p.stdout.strip()

def blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def verify_file(root:Path,path:str,digest:str)->bytes:
    require(type(path) is str and path and not path.startswith("/") and
            ".." not in Path(path).parts and "\x00" not in path,
            "Untrusted source path")
    require(type(digest) is str and re.fullmatch("[0-9a-f]{40}",digest) is not None,
            "Untrusted Git blob ID")
    f=root/path
    require(f.is_file() and not f.is_symlink() and f.resolve()==f,
            "File missing or source alias: "+path)
    raw=f.read_bytes()
    require(blob(raw)==digest,"Unreviewed file bytes: "+path)
    require(git(root,"ls-tree","HEAD","--",path)==
            "100644 blob "+digest+"\t"+path,
            "Remote tree and file mismatch: "+path)
    return raw

def validate_contract(m:dict)->None:
    require(type(m) is dict and m.get("schemaVersion")==1 and
            m.get("kind")=="R03B2RestrictedPhysicalDefinitionSourceCandidate",
            "Manifest identity")
    require(m.get("branch")=="codex/assembly-shadow-r01b-h1",
            "Wrong branch")
    for key in ("candidateNative","originalB1Native","originalB1ExecutionDemo",
                "hybridclr","hybridclr_unity"):
        require(type(m.get(key)) is str and
                re.fullmatch("[0-9a-f]{40}",m[key]) is not None,
                "Invalid source pin: "+key)
    require(m["originalB1ExecutionDemo"]==FIXED_B1_DEMO and
            m["originalB1Native"]==FIXED_B1_NATIVE and
            m["hybridclr"]==FIXED_HYBRIDCLR and
            m["hybridclr_unity"]==FIXED_UNITY,
            "Previously accepted source tuple must remain immutable")
    c=m.get("nativeSourceCapabilities")
    require(type(c) is dict and
            c.get("sourceReadsAfterTerminal") is False and
            c.get("arbitraryGenericInstantiationTypeKeys") is False and
            c.get("unrestrictedCrossImageGenericArgumentsSupported") is False and
            c.get("crossImageGenericArgumentsSupportedInMock") is True and
            c.get("crossImageUnregisteredArgumentFailsClosed") is True and
            c.get("unregisteredAotArgumentFailsClosed") is True and
            "crossImageGenericArgumentsSupported" not in c and
            "crossImageOnlyWhenBothImagesMatchedObservedClass" not in c and
            "crossImageUnmatchedArgumentFailsClosed" not in c and
            c.get("registeredUnobservedArgumentSupportedInMock") is True and
            c.get("registeredAotImageLimit")==1024 and
            c.get("zeroTypeDefinitionRegisteredAotImagesSkipped") is True and
            c.get("registeredAssemblyRegistryVisits")==2 and
            c.get("registeredAotImageSetDoubleChecked") is True and
            c.get("registeredImageSetOnlyObservational") is True and
            c.get("originalAssemblyRegistrySnapshotIncompleteForFullVmEpoch") is True and
            c.get("realAssemblyCppUnityCompiled") is False and
            c.get("runtimeAcceptanceProven") is False and
            c.get("ambiguousMetadataOwnerFailsClosed") is True and
            c.get("allPhysicalMetadataImagesEnumerated") is False and
            c.get("physicalImageLimit")==64 and
            c.get("physicalEnumerationPasses")==3 and
            c.get("realUnityRuntimeIntegrationProven") is False and
            c.get("coherentVmEpochProven") is False and
            c.get("genericArgumentLimit")==16 and
            c.get("genericOwnedOutputByteLimit")==4096 and
            c.get("boundedCompositeArgumentShapesInMock") is True and
            c.get("compositeMaximumDepth")==8 and
            c.get("arrayDimensionListLimit")==32 and
            c.get("compositeCoverageReceiptRevokedOnFailure") is True and
            c.get("arbitraryPrimitiveGenericArgumentKeys") is False and
            c.get("fullLegacyNonemptyExecutionParityProven") is False and
            c.get("originalV1PhysicalTokenValidEnumeration") is True and
            c.get("originalV1IncludesInterpreterImages") is True and
            c.get("originalV1FirstEmplaceOwnerJoinSourceImplemented") is True and
            c.get("originalV1OwnerConflictRevokesSource") is True and
            c.get("originalV1ImageInventoryDoubleChecked") is True and
            c.get("originalV1PhysicalMapForAdmittedHandlesMatchedInSourceMock") is True and
            c.get("originalV1MetadataOwnerImageCap")==1024 and
            c.get("originalV1OwnerLookupsCap")==65536 and
            c.get("originalV1JoinHostCases")==12 and
            c.get("originalV1JoinHostAssertions")>=41 and
            c.get("originalV1FullField15ParityProven") is False and
            c.get("originalV1ActualSerializerDifferentialHost") is True and
            c.get("originalV1SerializerUsesActualLiveR02") is True and
            c.get("originalV1SerializerUsesActualFrozenR02") is True and
            c.get("originalV1FormatterSameImmutableRowsOnly") is True and
            c.get("originalV1FormatterHostCases")==10 and
            c.get("originalV1FormatterHostAssertions")>=91 and
            c.get("originalV1FormatterGuardedAllocations")==0 and
            c.get("originalV1RuntimeClassMetadataParityProven") is False and
            c.get("originalV1TerminalField15FormattingProven") is False and
            c.get("observedClassFactsTwoPassInNativeSource") is True and
            c.get("observedClassFactsBetweenPassMutationFailures")==2 and
            c.get("observedClassFactsDuringTypeKeyMutationFailures")==1 and
            c.get("observedClassFactsEndPassImplemented") is True and
            c.get("observedClassFactsEndPassMutationFailures")==3 and
            c.get("observedClassFactsEndPassEnumerationFailures")==2 and
            c.get("observedClassFactsEndPassVisitedSlotBytes")==2048 and
            c.get("observedClassFactsEndPassMaximumCallbacks")==65536 and
            c.get("observedClassFactsEndPassNotVmEpoch") is True and
            c.get("observedClassFactsEndPassClassCountProvenInRealUnity") is False and
            c.get("mockScenarios")>=81 and
            c.get("mockAssertionsPerExecution")>=2126 and
            c.get("observedClassFactsRegistrySlotLimit")==2048 and
            c.get("observedClassFactsBytesPerSlot")==16 and
            c.get("observedClassFactsNotCoherentVmEpoch") is True and
            c.get("completeObservedClassLifetimeProven") is False and
            c.get("actualUnityOriginalV1OwnerJoinTested") is False and
            c.get("originalV1ImagesAreLogicalShadowView") is False and
            c.get("observationalOriginalV1ByteProbeImplemented") is True and
            c.get("legacyV1GetterUnchanged") is True and
            c.get("legacyGetterByteExactFixturePinned") is True and
            c.get("legacyGetterReferenceCommit")==
                "68530d7ecb86c9122d9ae5eb20366ccb0ea086b6" and
            c.get("legacyLogicalPhysicalImageMapParityProven") is False and
            c.get("realUnityOriginalGetterProbeTested") is False and
            c.get("parityMismatchRevokesBoundedSource") is True and
            c.get("paritySourceMockUsesFakeLegacyGetter") is True and
            c.get("parityHostCases")==10 and
            c.get("paritySourceMockCases")==3 and
            c.get("parityMockAssertionsPerExecution")>=1258 and
            c.get("observedActualOriginalV1ByteEqualityInUnity") is False and
            c.get("twoObservationsAreOneCoherentVmEpoch") is False and
            c.get("completeNativeField15Proven") is False and
            c.get("primitiveDefaultClassLookupNoAllocationSourcePinned") is True and
            c.get("primitiveArgumentsWithRegisteredAotTypeDefSupportedInMock") is True and
            c.get("primitiveClassNameAncestryChecked") is True and
            c.get("primitiveGenericContainerRejected") is True and
            c.get("assertFreePrimitiveDefaultLookup") is True and
            c.get("primitiveDefaultExactSwitchParity") is True and
            c.get("primitivePeekHostCases")==20 and
            c.get("unownedPrimitiveDefaultsRejected") is True and
            c.get("realUnityPrimitiveField15ParityProven") is False and
            c.get("arbitraryPrimitiveGenericArgumentKeys") is False and
            c.get("originalUnicodeAssemblyFoldBoundInVmSource") is True and
            c.get("originalNameTableParityHostOnly") is True and
            c.get("ownedUtf16FoldNoAllocationHostVerified") is True and
            c.get("realUnityUnicodeMetadataParityProven") is False and
            c.get("openGenericExecutionTypeKeysSupported") is False and
            c.get("legacyTypeKeyGrammarSourceBlob")==
                "6b23b4bad66e9a8f36c68717ef82626351018624" and
            c.get("realGenericRuntimeMetadataAbiBlob")==
                "f7f235848209ee331adfd1c2b214b46cc753392e",
            "Cannot invent terminal/full-key/generic ABI/VM-epoch acceptance")
    for key,required in (("nativeSources",NATIVE_REQUIRED),
                         ("demoPureSources",DEMO_REQUIRED)):
        rows=m.get(key)
        require(type(rows) is list and len(rows)==len(required) and
                all(type(row) is dict and set(row)=={"path","gitBlob"} for row in rows),
                "Source roster format: "+key)
        require({row["path"] for row in rows}==required,
                "Exact source roster: "+key)
        for row in rows:
            require(type(row["gitBlob"]) is str and
                    re.fullmatch("[0-9a-f]{40}",row["gitBlob"]) is not None,
                    "Source blob ID: "+row["path"])
            require(type(row["path"]) is str and row["path"] and
                    ".." not in Path(row["path"]).parts and
                    not row["path"].startswith("/"),
                    "Noncanonical source entry")
    for key in ("readyForNativeV2FieldCapture","nativeV2TransportImplemented",
                "runtimeAcceptance","R03Accepted","H2Passed",
                "ReadyForHumanReviewGate"):
        require(m.get(key) is False,"Illegal product acceptance: "+key)
    require(m.get("handoffAuthority")=="CLOSED_NO_LOCAL_EXECUTION",
            "Cannot authorize Local from source audit")

def source_boundary(native:dict[str,bytes])->None:
    def must(path:str,*tokens:str):
        txt=native[path].decode("utf8","strict")
        for token in tokens:
            require(token in txt,"Native source drift: "+path+" : "+token)
    must("libil2cpp/il2cpp-class-internals.h",
         "typedef struct Il2CppClass", "Il2CppClass* declaringType;",
         "Il2CppMetadataTypeHandle typeMetadataHandle;",
         "Il2CppMetadataGenericContainerHandle genericContainerHandle;")
    must("libil2cpp/il2cpp-runtime-metadata.h",
         "typedef struct Il2CppGenericClass",
         "typedef struct Il2CppGenericInst",
         "const Il2CppType **type_argv",
         "Il2CppGenericContext context",
         "Il2CppGenericClass *generic_class",
         "Il2CppTypeEnum type")
    must("libil2cpp/vm/GlobalMetadataFileInternals.h",
         "typedef struct Il2CppTypeDefinition",
         "TypeIndex declaringTypeIndex",
         "GenericContainerIndex genericContainerIndex")
    must("libil2cpp/vm/MemoryInformation.cpp",
         "ReportIL2CppClasses",
         "GetInitializedTypeInfoFromAssembly",
         "ReportVisibleClass",
         "WalkAllGenericClasses")
    must("libil2cpp/il2cpp-api.cpp","MemoryInformation::ReportIL2CppClasses")
    must("libil2cpp/os/Posix/MutexImpl.h","PTHREAD_MUTEX_RECURSIVE")
    must("libil2cpp/os/Win32/MutexImpl.h","EnterCriticalSection",
         "LeaveCriticalSection")
    must("libil2cpp/vm/AssemblyShadowRegisteredAotImageScan.h",
         "namespace assembly_shadow_registered_aot_scan",
         "bool Scan(", "assembly->token",
         "assembly->image->assembly!=assembly",
         "if(!image->typeCount)continue;", "visit(image)")
    must("libil2cpp/vm/Assembly.h",
         "TryVisitOriginalV1ExecutionImages(",
         "CopyValidAssemblies",
         "TryVisitRegisteredAotImages(",
         "caller MUST hold",
         "g_MetadataLock")
    must("libil2cpp/vm/Assembly.cpp",
         "static void CopyValidAssemblies(", "if (ass->token)",
         "dst.push_back(ass);",
         "CopyValidAssemblies(assemblies, s_Assemblies);",
         "s_Assemblies.begin(),s_Assemblies.end()",
         "assembly_shadow_registered_aot_scan::Scan(",
         "IsInterpreterImage(image)",
         "assembly_shadow_original_v1_image_scan::Scan(",
         "TryVisitOriginalV1ExecutionImages(",
         "s_assemblyLock",
         "TryVisitRegisteredAotImages(")
    must("libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h",
         "namespace assembly_shadow_original_v1_image_scan",
         "bool Scan(", "if(!assembly->token)continue;",
         "if(!visit(assembly->image))return false;",
         "assembly->image->assembly!=assembly")
    must("libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h",
         "namespace assembly_shadow_original_v1_owner_join",
         "CheckFirstOwner(", "read(image,j)==handle",
         "image!=expectedAotImage",
         "Error::FirstOwnerDifferent", "Error::OwnerNotFound",
         "Error::LookupBudget", "firstEmplaceOwnerMatched=true",
         "entireOriginalV1Field15Proven=false",
         "coherentVmEpochProven=false")
    must("NativeHostTests/AssemblyShadowOriginalV1OwnerJoinHost.cpp",
         "R03B2OriginalV1FirstOwnerJoinHost",
         "InterpreterFirstConflict()", "LaterInterpreterAlias()",
         "ZeroTypeDefFirst()", "TokenZeroSkipped()", "LookupBudget()",
         "protectedAllocations")
    must(".github/workflows/r03-native-b2-original-v1-owner-join-host.yml",
         "AssemblyShadowOriginalV1OwnerJoinHost.cpp", "c++11", "c++17",
         "sanitized")
    must("libil2cpp/vm/AssemblyShadowObservedPhysicalImages.h",
         "class Inventory final","AddFromMatchedCallback",
         "AddFromRegisteredAssembly", "SameOrderedImageSet",
         "Contains(const void*",
         "~Inventory() noexcept{Scrub();}", "Error::Capacity")
    must("libil2cpp/vm/AssemblyShadowTypeKey.cpp",
         "case IL2CPP_TYPE_GENERICINST:",
         'value = "generic(" + FormatType(generic->type',
         'Part(FormatType(generic->context.class_inst->type_argv[index]',
         "kMaximumTypeDepth = 128")
    must("libil2cpp/vm/AssemblyShadowName.h",
         "inline NameView ViewName(", "inline bool NextFolded(",
         "VmStringUtils::Utf16ToLower", "inline bool NameHash(")
    must("libil2cpp/vm-utils/VmStringUtils.cpp",
         "VmStringUtils::Utf16ToLower", "ToLowerDataLow[c]",
         "ToLowerDataHigh[c - kDataHighThreshold]")
    must("libil2cpp/vm-utils/VmStringUtils.h",
         "Utf16ToLower(Il2CppChar c)")
    must("libil2cpp/utils/StringUtils.cpp",
         "StringUtils::Utf16ToUtf8(const UTF16String& utf16String)")
    must("libil2cpp/char-conversions.cpp",
         "ToLowerDataLow[]", "ToLowerDataHigh[]")
    must("libil2cpp/char-conversions.h",
         "ToLowerDataLow[9424]", "ToLowerDataHigh[223]")
    must("libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h",
         "BeginCanonicalFolded(", "uint16_t first=0,second=0",
         "nextFolded(cursor,end,first,second)",
         "if(count>kCapacity-length)", "state_=State::Open")
    must("NativeHostTests/AssemblyShadowNameReferenceParityHost.cpp",
         '#include "vm/AssemblyShadowName.h"',
         "VmStringUtils::Utf16ToLower", "ToLowerDataLow[c]",
         "originalUnicodeTables")
    must("NativeHostTests/AssemblyShadowOwnedFoldedDefinitionHost.cpp",
         "R03B2CanonicalFoldedAssemblyHost",
         "TestMalformed", "TestUntrustedFoldResults", "guardedAllocations")
    must("NativeHostTests/AssemblyShadowFoldedNameMock.h",
         "HOST TEST ONLY", "NameHash(", "NextFolded(")
    must("NativeHostTests/ShadowNameParityShim/il2cpp-config.h",
         "Host-only ABI shim", "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1")
    must("libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
         'Put("generic(",8)', 'Decimal(argument.Bytes())',
         "kMaximumArguments=16",
         "AddArgument(")
    must("libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h",
         'Put("generic(",8)', "FromArray(", "FromQualified(",
         "FromPointer(", "FromSzArray(", "kMaximumArguments=16",
         "kMaximumArrayDimensions=32", "kCapacity=4096")
    must("NativeHostTests/AssemblyShadowOwnedCompositeTypeKeyHost.cpp",
         "R03B2OwnedCompositeTypeKeyHost",
         "TestCompositeAndOriginalGrammar",
         "TestFailuresAndNoPartialOutput",
         "TestMaximumArgumentsAndSignedBounds")
    must("libil2cpp/vm/AssemblyShadowExistingPrimitiveDefaults.h",
         "inline Il2CppClass* Peek(Il2CppTypeEnum tag) noexcept",
         "return nullptr;", "il2cpp_defaults.int32_class")
    must("libil2cpp/vm/Class.h",
         "static Il2CppClass* FromIl2CppTypeEnum(Il2CppTypeEnum type);")
    must("libil2cpp/vm/Class.cpp",
         "Il2CppClass* Class::FromIl2CppTypeEnum(Il2CppTypeEnum type)",
         "#define RETURN_DEFAULT_TYPE(fieldName)",
         "RETURN_DEFAULT_TYPE(int32_class)",
         "RETURN_DEFAULT_TYPE(string_class)",
         "RETURN_DEFAULT_TYPE(systemtype_class)")
    # The original default lookup must be a pure switch returning initialized
    # il2cpp_defaults; no metadata class instantiation or cache entry is allowed
    # in this trusted primitive-source lookup branch.
    cpp=native["libil2cpp/vm/Class.cpp"].decode("utf8","strict")
    begin=cpp.index("Il2CppClass* Class::FromIl2CppTypeEnum(Il2CppTypeEnum type)")
    end=cpp.index("Il2CppClass* Class::FromSystemType(",begin)
    default_branch=cpp[begin:end]
    for forbidden in ("MetadataCalloc(", "FromGenericParameter(",
                      "Class::Init(", "GetPtrClass(", "GetArrayClass(",
                      "GetBoundedArrayClass(", "MetadataCache::"):
        require(forbidden not in default_branch,
                "Default primitive source must not create classes: "+forbidden)
    require("switch (type)" in default_branch and
            "return il2cpp_defaults.fieldName;" in default_branch and
            "return NULL;" in default_branch,
            "Default primitive direct lookup contract drift")
    # Mechanically establish exact original Class.cpp case-to-default-field
    # equivalence, including unsupported/default cases. A copied hard-coded
    # list without this source join must not be admitted as V1 compatible.
    peek=native["libil2cpp/vm/AssemblyShadowExistingPrimitiveDefaults.h"].decode("utf8","strict")
    original_pairs=re.findall(
        r"case\s+(IL2CPP_TYPE_[A-Z0-9_]+):\s*RETURN_DEFAULT_TYPE\((\w+)\);",
        default_branch)
    peek_pairs=re.findall(
        r"case\s+(IL2CPP_TYPE_[A-Z0-9_]+):\s*return\s+il2cpp_defaults\.(\w+);",
        peek)
    require(len(original_pairs)==19 and len(peek_pairs)==19 and
            len(dict(original_pairs))==19 and len(dict(peek_pairs))==19 and
            dict(original_pairs)==dict(peek_pairs),
            "Primitive peek field mapping diverges from original Class.cpp switch")
    require("IL2CPP_ASSERT(" not in peek and "Class::Init(" not in peek and
            "MetadataCache::" not in peek,
            "Primitive peek must not assert or initialize any type")
    must("libil2cpp/vm/AssemblyShadowAdmittedExecutionDiagnosticsSource.inl",
         "assembly_shadow_metadata_lifetime::Gate::Reader reader(",
         "return GetExecutionDiagnosticsJson(json);")
    must("libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h",
         "class Probe final", "bool Fresh() const noexcept",
         "bool Compare(View legacy,View bounded) noexcept",
         "kMaximumBytes=3932160",
         "firstDifferentOffset", "twoIndependentObservationsOnly",
         "coherentVmEpochProven=false", "fullCanonicalTypeKeysProven=false",
         "terminalSafeFinalExecutionDiagnostics=false",
         "nativeV2TransportImplemented=false", "R03Accepted=false")
    must("libil2cpp/vm/AssemblyShadowExecutionV1ByteParitySource.inl",
         "TryProbeBoundedExecutionV1ByteParity(",
         "assembly_shadow_metadata_lifetime::Gate::Reader admission(",
         "TryGetExecutionDiagnosticsWithMetadataAdmission(originalV1)",
         "TryCaptureBoundedDefinitionExecutionLive(",
         "parity.Compare(", "if(!equal)",
         "sourceReceipt.callbackPhysicalMembershipProven",
         "sourceReceipt.restrictedTypeDefSubsetProven",
         "sourceReceipt.observedRegistryAndCounterFenceStable",
         "originalV1.clear();", "live::Reject(")
    must("libil2cpp/vm/AssemblyShadowExecutionSerializer.h",
         "struct Header", "struct ClassRow", "AppendClass(")
    must("libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h",
         "class Record final", "bool Freeze() noexcept",
         "r02::AppendFrozenDiagnostics(")
    must("libil2cpp/vm/AssemblyShadowMetadataLifetime.h",
         "class Reader final", "kInitialEpoch=1",
         "CloseAndDrain() noexcept")
    must("libil2cpp/vm/AssemblyShadowR02Snapshot.h",
         "class Snapshot final", "TryCaptureCurrent(",
         "TryCaptureFrom(", "SnapshotReceipt")
    must("libil2cpp/vm/AssemblyShadowObservationCounters.h",
         "enum class Metric", "class ObservationCounters",
         "ObservationCounter", "kThreadCapacity = 128")
    must("libil2cpp/vm/AssemblyShadowObservationMemo.h",
         "class ObservationMemo", "TlsBytesPerThread()")
    must("libil2cpp/vm/AssemblyShadowDiagnosticsProfile.h",
         "HYBRIDCLR_R02_DEFAULT_DIAGNOSTICS_LEVEL 2")
    # Source-level R02 live/frozen field order and Metric mapping must remain
    # identical. This complements compiling BOTH ACTUAL serializers in host.
    def r02_fields(path:str):
        body=native[path].decode("utf8","strict")
        return re.findall(r'\{"([^"]+)",\s*Metric::(\w+)\}',body)
    legacy_fields=r02_fields("libil2cpp/vm/AssemblyShadowR02Diagnostics.h")
    frozen_fields=r02_fields("libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h")
    require(len(legacy_fields)>=20 and
            legacy_fields==frozen_fields and
            len(set(legacy_fields))==len(legacy_fields),
            "Original live/frozen R02 field/metric sequence drift")
    must("NativeHostTests/AssemblyShadowExecutionV1SerializerParityHost.cpp",
         "R03B2OriginalV1ExecutionSerializerParityHost",
         "r02::AppendDiagnostics(output)",
         "r02::Snapshot::TryCaptureCurrent(",
         "record->Freeze()",
         "DivergentClassFacts()", "DivergentR02Counter()",
         "actualLegacyR02Formatter", "actualFrozenR02Formatter",
         "terminalSafeField15", "guardedAllocations")
    must(".github/workflows/r03-native-b2-execution-v1-serializer-parity-host.yml",
         "AssemblyShadowExecutionV1SerializerParityHost.cpp",
         "c++11", "c++17",
         "sanitized", 'j["cases"]==10')
    must("libil2cpp/vm/AssemblyShadowR02Diagnostics.h",
         "AppendDiagnostics(")
    must("libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h",
         "AppendFrozenDiagnostics(")
    must("libil2cpp/vm/AssemblyShadowDiagnosticWriter.h",
         "class Writer")
    must("NativeHostTests/AssemblyShadowExecutionV1ByteParityHost.cpp",
         "R03B2ObservedExecutionV1ByteParityHost",
         "DifferentLength()", "MissingLegacy()", "MissingBounded()",
         "realLegacyGetter")
    must(".github/workflows/r03-native-b2-v1-parity-host.yml",
         "AssemblyShadowExecutionV1ByteParityHost.cpp",
         "c++11", "c++17", "sanitized")
    must("libil2cpp/vm/AssemblyShadow.cpp",
         '#include "AssemblyShadowBoundedDefinitionExecutionLive.h"',
         '#include "vm/GlobalMetadataFileInternals.h"',
         '#include "AssemblyShadowExistingPrimitiveDefaults.h"',
         '#include "AssemblyShadowBoundedDefinitionExecutionLiveSource.inl"',
         '#include "AssemblyShadowExecutionV1ByteParity.h"',
         '#include "AssemblyShadowExecutionV1ByteParitySource.inl"',
         "AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(",
         "Assembly::CaptureShadowEnumeration(assemblies)",
         "AssemblyShadowTypeKey::FormatMetadataOnly(",
         "assembly_shadow_execution_diagnostic::AppendClass(",
         "assembly_shadow_r02::AppendDiagnostics(output)")
    must("libil2cpp/vm/AssemblyShadow.h",
         "TryCaptureBoundedDefinitionExecutionLive",
         "Never returns a live class pointer or modifies the original getter.",
         "TryProbeBoundedExecutionV1ByteParity(")
    must("libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
         "ObservedClassFactsChanged",
         "observedClassFactsTwoPassStable",
         "observedClassFactsMatched=0",
         "observedClassFactsEndPassMatched=0",
         "observedClassFactsEndPassStable=false")
    must("libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
         "assembly_shadow_metadata_lifetime::Gate::Reader admission",
         "il2cpp_class_for_each",
         "metadataLock(&g_MetadataLock)",
         "TryObservedRegistrationBinding",
         "MetadataCache::GetAssemblyTypeHandle",
         "GlobalMetadata::GetTypeNamespaceAndName",
         "GlobalMetadata::GetIl2CppTypeFromIndex",
         "IL2CPP_TYPE_GENERICINST",
         "physical::Scratch discovery",
         "imageInventory.Count()",
         "registeredAotImages.Count()",
         "Assembly::TryVisitRegisteredAotImages",
         "registeredAfter.SameOrderedImageSet(registeredAotImages)",
         "registeredImageSetStable=true",
         "Assembly::TryVisitOriginalV1ExecutionImages(",
         "originalAfter.SameOrderedImageSet(originalV1Images)",
         "original_join::CheckFirstOwner(",
         "OriginalV1FirstOwnerConflict",
         "OriginalV1OwnerMissing",
         "originalV1FirstEmplaceOwnerMatched=",
         "ObservedClassFactsChanged",
         "ClassFacts::Read(klass)",
         "firstPassFacts.fill(ClassFacts{})",
         "receipt.observedClassFactsTwoPassStable=",
         "receipt.observedClassFactsEndPassMatched=endPass.matched",
         "receipt.observedClassFactsEndPassStable=",
         "c.firstPassFacts[registration]=finalFacts;",
         "std::array<uint8_t,physical::kSlots> seen{}",
         "endPass.matched!=receipt.registered",
         "end.seen[slot]=1",
         "if(!end.facts[slot].Same(ClassFacts::Read(klass)))",
         "usedUnobservedAotArgumentImage",
         "resolveOwner",
         "AmbiguousMetadataOwner",
         "context.images=nullptr",
         "usedCrossImageArgument",
         "assembly_shadow_detail::ViewName(",
         "assembly_shadow_detail::NameHash(",
         "assembly_shadow_detail::NextFolded(",
         "BeginCanonicalFolded(",
         "usedUnicodeAssemblyFold",
         "assembly_shadow_existing_primitive_defaults::Peek(",
         "primitive->typeMetadataHandle",
         "primitive->declaringType",
         "primitive->genericContainerHandle",
         "primitive->namespaze",
         "context.usedExistingPrimitiveDefault=true",
         "admittedPrimitiveArguments",
         "generic->context.class_inst",
         "definitionArity!=instance->type_argc",
         "composite_key::Capture genericKey",
         "Composer composer", "IL2CPP_TYPE_ARRAY",
         "IL2CPP_TYPE_PTR", "IL2CPP_TYPE_SZARRAY",
         "FromQualified(", "usedMdArrayArgument",
         "makeDefinition(value->data.typeHandle",
         "kMaximumTotalMetadataLookups",
         "assembly_shadow_first_failure_v2::State::Empty",
         "s_executionRegistrationWitnesses",
         "rows.Seal()",
         "record.Freeze()",
         "r02::Snapshot::TryCaptureCurrent",
         "not an all-VM linearization")
    must("libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
         "callbackPhysicalMembershipProven",
         "completeArbitraryTypeKeys=false",
         "usedUnicodeAssemblyFold",
         "usedExistingPrimitiveDefault",
         "completeExecutionDiagnostics=false",
         "coherentVmEpochProven=false",
         "nativeV2TransportImplemented=false",
         "runtimeAcceptance=false")
    must("NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp",
         '#include "vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl"',
         '#include "vm/AssemblyShadowExistingPrimitiveDefaults.h"',
         "TestAssertFreePrimitivePeekMapping",
         "primitivePeekCases",
         '#include "vm/AssemblyShadowExecutionV1ByteParitySource.inl"',
         "TestParityProbeMock()", "parityProbeCases",
         "realLegacyGetter",
         "Mode::StagedNestedIndex",
         "Mode::CyclicNested",
         "Mode::GenericDefinition",
         "Mode::PrimitiveDefault",
         "Mode::PrimitiveQualified",
         "Mode::PrimitiveMissingDefault",
         "Mode::PrimitiveUnregistered",
         "Mode::PrimitiveWrongHandle",
         "Mode::PrimitiveWrongImage",
         "Mode::PrimitiveUnsupportedTag",
         "Mode::PrimitiveAmbiguousOwner",
         "Mode::PrimitiveGenericArity",
         "Mode::PrimitiveClassNameMismatch",
         "Mode::PrimitiveClassNested",
         "Mode::PrimitiveClassGenericContainer",
         "Mode::OriginalV1InterpreterBeforeAot",
         "Mode::OriginalV1InterpreterAfterAot",
         "Mode::OriginalV1ZeroTypeDefInterpreter",
         "Mode::OriginalV1SnapshotChanged",
         "Mode::OriginalV1UnregisteredOwner",
         "Mode::OriginalV1InvalidImage",
         "Mode::CctorFactsChanged",
         "Mode::StaticFactsChanged",
         "Mode::CctorFactsDuringTypeKey",
         "Mode::CctorFactsChangedAtEnd",
         "Mode::StaticFactsChangedAtEnd",
         "Mode::EarlierClassFactsChangedDuringLaterTypeKey",
         "Mode::MissingEndPass",
         "Mode::DuplicateEndPass",
         "Check(g_physicalPasses==3)",
         "Mode::GenericSameImage",
         "Mode::GenericConstructedArgument",
         "Mode::UnicodeAssembly",
         "Mode::UnicodePathVersionAssembly",
         "Mode::UnicodeSupplementaryAssembly",
         "Mode::InvalidUnicodeOverlong",
         "Mode::InvalidUnicodeSurrogate",
         "Mode::GenericPointerArgument",
         "Mode::GenericSzArrayArgument",
         "Mode::GenericArrayArgument",
         "Mode::GenericQualifiedPointerArgument",
         "Mode::GenericArrayBadSizes",
         "Mode::GenericCompositeTooDeep",
         "Mode::GenericNestedArgument",
         "Mode::GenericTooManyArguments",
         "Mode::CrossImageGeneric",
         "Mode::CrossImageGenericUnobserved",
         "Mode::CrossImageGenericNotRegistered",
         "Mode::RegisteredAotChanged",
         "Mode::RegisteredAotOverflow",
         "Mode::RegisteredAotInvalidOwner",
         "Mode::RegisteredEmptyAotAssembly",
         "Mode::CrossImageGenericAmbiguous",
         "Mode::CrossImageInterpreter",
         "Mode::CrossImageNestedArgument",
         "Mode::MissingSecondPass",
         "TestPhysicalImageInventoryBounds",
         "Mode::NestedType",
         "Mode::CounterChanged",
         "NoMetadataAdmission")
    for name in (
        "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
        "libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h",
        "libil2cpp/vm/AssemblyShadowExecutionV1ByteParitySource.inl",
        "libil2cpp/vm/AssemblyShadowExistingPrimitiveDefaults.h",
        "libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h",
        "libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h",
        "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
        "libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h",
        "libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
        "libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h",
        "libil2cpp/vm/AssemblyShadowObservedPhysicalImages.h",
        "libil2cpp/vm/AssemblyShadowRegisteredAotImageScan.h",
        "libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h",
    ):
        raw=native[name]
        require(b"operator new" not in raw and b"int main(" not in raw,
                "Standalone allocator/host driver leaked into production vm: "+name)

def verify_legacy_getter_unchanged(current:bytes,reference:bytes)->None:
    start=(b"AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(std::string& json)"
           +bytes([10])+b"{")
    boundary=b"// P1 inactive reader around the original (unmodified) V1 getter."
    # This is a byte-for-byte independently pinned V1 fixture, not a
    # reimplementation, and excludes neighboring source.
    require(len(reference)>2000 and reference.startswith(start) and
            reference.endswith(b"}"+bytes([10,10])),
            "Untrusted original V1 execution getter reference fixture")
    # Production AssemblyShadow.cpp contains TWO definitions in mutually
    # exclusive compile branches: one real Shadow-on getter and one
    # HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW-off FeatureDisabled stub. Only the
    # first is the V1 reference; both source anchors must stay present.
    require(current.count(start)==2 and current.count(boundary)==1,
            "Original getter source anchor count")
    require(current.index(start,current.index(boundary))>current.index(boundary),
            "Missing expected feature-disabled alternative original getter")
    first=current.index(start)
    end=current.index(boundary,first)
    require(current[first:end]==reference,
            "Original GetExecutionDiagnosticsJson implementation was modified")

def inspect_original_v1_field15_contract(reference: bytes) -> dict:
    """Source-only field15 value/inventory contract, not a VM snapshot proof.

    This verifies the exact original V1 implementation's *mapping* and read
    boundaries. It cannot establish class allocation, GC, metadata or terminal
    lifetime, and never marks a native V2/Player acceptance predicate true.
    """
    text = reference.decode("utf-8", "strict")
    require(text.startswith(
        "AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(std::string& json)\n{"),
        "Original V1 execution getter source missing")

    # Match assignments, not just names occurring in comments or declarations.
    def assignments(name: str) -> list[tuple[str, str]]:
        return re.findall(r"^\s*" + re.escape(name) +
                          r"\.(\w+)\s*=\s*([^;\n]+);\s*$", text, re.M)

    header = [
        ("stateCode", "static_cast<int>(state)"),
        ("state", "AssemblyShadowDiagnostics::StateName(state)"),
        ("generation", "active ? active->generation : 0"),
        ("methodChecks", "methodChecks"),
        ("shadowMethodChecks", "shadowChecks"),
        ("rejectedBaselineMethods", "rejectedChecks"),
        ("baselineClassCctorStarted", "s_baselineClassCctorStarted.load(std::memory_order_relaxed)"),
        ("shadowClassCctorStarted", "s_shadowClassCctorStarted.load(std::memory_order_relaxed)"),
        ("interpreterTransformations", "transforms"),
        ("shadowInterpreterTransformations", "shadowTransforms"),
        ("droppedClassObservations", "s_droppedClassObservations.load(std::memory_order_relaxed)"),
    ]
    rows = [
        ("logicalAssembly", "assembly_shadow_diagnostic::Quoted(owner->aname.name)"),
        ("typeKey", "assembly_shadow_diagnostic::Quoted(typeKey)"),
        ("interpreterShadow", "baseline || shadow"),
        ("physicalInterpreter", "Interpreter(owner)"),
        ("isActive", "!baseline"),
        ("cctorStarted", "started"),
        ("cctorFinished", "finished"),
        ("hasInitializationException", "exception"),
        ("staticStoragePointer", "assembly_shadow_diagnostic::Quoted(pointer)"),
        ("pointerDetailsAvailable", "details"),
        ("staticStorageAvailable", "storage != nullptr"),
    ]
    require(assignments("heading") == header,
            "Original V1 execution header assignment or order drift")
    require(assignments("row") == rows,
            "Original V1 execution class assignment or order drift")

    for marker in (
        "std::array<Il2CppClass*, kMaximumExecutionClasses> classes{};",
        "if (assembly_shadow_r02::ObservationCounters::Level >= 2)",
        "ExecutionObservationLock lock;",
        "for (Il2CppClass* klass : s_executionClasses)",
        "if (klass) classes[count++] = klass;",
        "if (count) Assembly::CaptureShadowEnumeration(assemblies);",
        "images.emplace(MetadataCache::GetAssemblyTypeHandle(assembly->image, index), assembly->image);",
        "const ActiveSnapshot* active = s_active.load(std::memory_order_acquire);",
        "const AssemblyShadowState state = s_state.load(std::memory_order_acquire);",
        "const bool baseline = active && active->byAssembly.count(owner);",
        "const bool shadow = active && active->shadowToBaseline.count(owner);",
        "try { typeKey = AssemblyShadowTypeKey::FormatMetadataOnly(&klass->byval_arg, images); }",
        "catch (const ShadowTypeResolutionFailure& failure) { return failure.error; }",
        "il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);",
        "storage = klass->static_fields; // Only already-existing storage.",
        "const bool started = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_started)) != 0;",
        "const bool finished = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_finished_or_no_cctor)) != 0;",
        "const bool exception = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->initializationExceptionGCHandle)) != 0;",
        "#if IL2CPP_DEBUG\n        const bool details = true;",
        "address << \"0x\" << std::hex << reinterpret_cast<uintptr_t>(storage);",
        "#else\n        const bool details = false;\n#endif",
        "assembly_shadow_execution_diagnostic::Begin(output, heading);",
        "assembly_shadow_execution_diagnostic::AppendClass(output, row, index != 0);",
        "assembly_shadow_execution_diagnostic::EndClasses(output);",
        "assembly_shadow_r02::AppendDiagnostics(output);",
        'output << "}";',
        "json = output.str();",
    ):
        require(marker in text, "Original V1 field15 source boundary drift: " + marker)

    # These source-order checks make sure the registry lock is not falsely
    # treated as protection for subsequent class/GC reads or the live R02 tail.
    require(text.index("ExecutionObservationLock lock;") <
            text.index("if (count) Assembly::CaptureShadowEnumeration(assemblies);") <
            text.index("try { typeKey = AssemblyShadowTypeKey::FormatMetadataOnly") <
            text.index("il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);") <
            text.index("const bool started = os::Atomic::LoadRelaxed") <
            text.index("assembly_shadow_r02::AppendDiagnostics(output);"),
            "Original V1 class-source order changed")
    require("{\n            il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);\n"
            "            storage = klass->static_fields; // Only already-existing storage.\n"
            "        }" in text,
            "Original V1 static-storage metadata lock scope changed")
    return {
        "sourceContract": "PassedExactOriginalV1Field15ValueInventory",
        "headerFields": [field for field, _ in header],
        "classFields": [field for field, _ in rows],
        "classRegistryOrder": "s_executionClasses_nonnull_slot_order",
        "physicalImageOrder": "CopyValidAssemblies_token_valid_first_emplace",
        "typeKeySource": "FormatMetadataOnly_allocating",
        "staticStorageRead": "short_g_MetadataLock_only",
        "cctorRead": "three_relaxed_atomic_loads_after_metadata_lock",
        "r02Source": "live_counters_after_class_rows",
        "classGcLifetimeProven": False,
        "completeBoundedField15Proven": False,
        "terminalSafeField15Proven": False,
        "coherentVmEpochProven": False,
        "nativeV2TransportImplemented": False,
        "runtimeAcceptance": False,
    }

def inspect(demo:Path,native:Path,expected_demo:str,expected_native:str)->dict:
    demo=demo.resolve(strict=True)
    native=native.resolve(strict=True)
    require(demo!=native and demo not in native.parents and native not in demo.parents,
            "Separate repository roots")
    require(git(demo,"rev-parse","HEAD")==expected_demo,"Demo HEAD")
    require(git(native,"rev-parse","HEAD")==expected_native,"Native HEAD")
    require(not git(demo,"status","--porcelain","--untracked-files=no"),
            "Dirty demo tracked source")
    require(not git(native,"status","--porcelain","--untracked-files=no"),
            "Dirty native tracked source")
    mf=demo/MANIFEST
    require(mf.is_file() and not mf.is_symlink(),"No authenticated candidate manifest")
    m=json.loads(mf.read_text(encoding="utf8"))
    validate_contract(m)
    require(m["candidateNative"]==expected_native,"Candidate source pin drift")
    d={r["path"]:verify_file(demo,r["path"],r["gitBlob"])
       for r in m["demoPureSources"]}
    n={r["path"]:verify_file(native,r["path"],r["gitBlob"])
       for r in m["nativeSources"]}
    source_boundary(n)
    verify_legacy_getter_unchanged(
        n["libil2cpp/vm/AssemblyShadow.cpp"],
        d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/OriginalV1ExecutionGetter_2026-11-12.txt"])
    legacy_inventory=inspect_original_v1_field15_contract(
        d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/OriginalV1ExecutionGetter_2026-11-12.txt"])
    key=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedDefinitionTypeKey.h"]
    rows=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedExecutionRows.h"]
    v1_scan=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOriginalV1ImageScan.h"]
    require(n["libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h"]==v1_scan,
            "Native original V1 image visitor diverged from demo mirror")
    v1_owner=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOriginalV1OwnerJoin.h"]
    require(n["libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h"]==v1_owner,
            "Native original V1 first-owner join diverged from demo mirror")
    parity=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedObservedExecutionV1ByteParity.h"]
    require(n["libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h"]==parity,
            "Native observational V1 parity source diverged from demo mirror")
    require(n["libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h"]==key,
            "Fork TypeKey diverged from independently tested pure original")
    composed=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedConstructedTypeKey.h"]
    require(n["libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h"].replace(
                b'"AssemblyShadowOwnedDefinitionTypeKey.h"',
                b'"BoundedOwnedDefinitionTypeKey.h"')==composed,
            "Fork generic composer diverged from independent pure source")
    composite=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedCompositeTypeKey.h"]
    require(n["libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h"].replace(
                b'"AssemblyShadowOwnedDefinitionTypeKey.h"',
                b'"BoundedOwnedDefinitionTypeKey.h"')==composite,
            "Fork composite composer diverged from independent pure source")
    require(n["libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h"].replace(
                b'"AssemblyShadowOwnedDefinitionTypeKey.h"',
                b'"BoundedOwnedDefinitionTypeKey.h"').replace(
                b'"AssemblyShadowOwnedConstructedTypeKey.h"',
                b'"BoundedOwnedConstructedTypeKey.h"').replace(
                b'"AssemblyShadowOwnedCompositeTypeKey.h"',
                b'"BoundedOwnedCompositeTypeKey.h"')==rows,
            "Fork owned-row source diverged beyond local include path")
    return {
        "kind":"R03B2RestrictedDefinitionExactSourceGate",
        "result":"PassedInactiveSourceOnly_NotFullV2",
        "verifiedNativeFiles":len(n),
        "verifiedDemoPureFiles":len(d),
        "legacyField15SourceInventory":legacy_inventory,
        "pins":{"hybridclr_demo":expected_demo,"il2cpp_plus":expected_native,
                "hybridclr":m["hybridclr"],"hybridclr_unity":m["hybridclr_unity"]},
        "supportedSubset":"Registered-AOT physical TypeDefs with independently checked ORIGINAL token-valid physical V1 first-emplace owner (all images including interpreter), bounded Unicode/composite/primitive, and inactive healthy-time original-vs-owned byte observation. NOT full original field15, VM epoch, terminal source, Player or native V2",
        "liveMetadataReadProvenByUnity":False,
        "readyForNativeV2FieldCapture":False,
        "nativeV2TransportImplemented":False,
        "runtimeAcceptance":False,
        "R03Accepted":False,
        "H2Passed":False,
        "ReadyForHumanReviewGate":False,
        "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION"
    }

def main()->int:
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--demo",type=Path,required=True)
    a.add_argument("--native",type=Path,required=True)
    a.add_argument("--expected-demo",required=True)
    a.add_argument("--expected-native",required=True)
    v=a.parse_args()
    try:
        result=inspect(v.demo,v.native,v.expected_demo,v.expected_native)
    except (Rejected,OSError,ValueError,UnicodeError) as e:
        print(json.dumps({"result":"Rejected","reason":str(e),
                          "readyForNativeV2FieldCapture":False},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__=="__main__":
    sys.exit(main())
