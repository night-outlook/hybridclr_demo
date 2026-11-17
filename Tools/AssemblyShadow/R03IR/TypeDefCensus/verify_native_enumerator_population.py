#!/usr/bin/env python3
"""R03 B2 pinned-native population/metadata-lifetime source audit. NOT a census.

Checks the physical-vs-logical enumeration distinction in actual IL2CPP code.
Does not enumerate runtime objects, certify closed-world coverage, or authorize
native source attachment, capacity changes, Player, or Local Validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from verify_native_source_path_boundary import (
    NATIVE_COMMIT, BRANCH, SourceMismatch, require, read_pinned,
    code_only, scope,
)

API = 'libil2cpp/il2cpp-api.cpp'
MEMORY = 'libil2cpp/vm/MemoryInformation.cpp'
ASSEMBLY = 'libil2cpp/vm/Assembly.cpp'
IMAGE_SCAN = 'libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h'
GLOBAL = 'libil2cpp/vm/GlobalMetadata.cpp'
GENERIC = 'libil2cpp/metadata/GenericMetadata.cpp'
ARRAY = 'libil2cpp/metadata/ArrayMetadata.cpp'
POINTER = 'libil2cpp/vm/MetadataCache.cpp'
RUNTIME = 'libil2cpp/vm/Runtime.cpp'
LIFETIME = 'libil2cpp/vm/AssemblyShadowMetadataLifetime.h'
B2 = 'libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl'
PINNED_BLOBS = {
    API: '780f8416bdae08362ae811abe3a4386d043be9ce',
    MEMORY: 'f5bf451d3115d02880f8b54cb932c20c4eda60f6',
    ASSEMBLY: 'df1acbfdaf054067720d2e7c1545e49100ad93ec',
    IMAGE_SCAN: '41cdb90776f1f68f3fc7cbff85045965e29b99b0',
    GLOBAL: '90a9da38496b316becc3c771be0cd29f8bbf7e7b',
    GENERIC: 'ddecffe04fe2810badeb284f3ec54e751719531c',
    ARRAY: '85004bb647060b7f488a3a63976f9e4a0efbf17b',
    POINTER: 'b9a9881c6e6a551c19069446a9be61c21f4c8584',
    RUNTIME: '1b176ee5fd3e2127a0237877e5c9c32bc53058b3',
    LIFETIME: 'd2fe09dd51debbbbc71d67b21347f5d971a3cafd',
    B2: 'f988e8a3ebaefe13dde80fa2cb784a673326f395',
}
# This is a statement-order/source-contract audit, NOT an AST/CFG checker.
# The exact blob pins are necessary to prevent stale/aliased source evidence.
PHYSICAL_SOURCE = 'OriginalV1TokenValidPhysicalRegistrations'
PUBLIC_SOURCE = 'LogicalVisibilityFilteredInitializedAndConstructedCaches'
MAX_NATIVE_FILE_BYTES = 160_000


def narrow(source: str, anchor: str, name: str) -> str:
    return re.sub(r'\s+', '', scope(code_only(source), anchor, name))


def has(body: str, snippet: str, label: str) -> int:
    compact = re.sub(r'\s+', '', snippet)
    at = body.find(compact)
    require(at >= 0, f'{label}: missing expected native source expression {snippet}')
    return at


def absence(body: str, snippet: str, label: str) -> None:
    require(re.sub(r'\s+', '', snippet) not in body, f'{label}: unexpected direct physical source')


def check_population_sources(source: dict[str, str]) -> dict:
    require(set(source) == set(PINNED_BLOBS), 'source file set differs from pinned contract')
    public = narrow(source[API], r'\bvoid\s+il2cpp_class_for_each\s*\(', 'api class_for_each')
    has(public, 'MemoryInformation::ReportIL2CppClasses(klassReportFunc, userData)', 'API forwarding')

    memory = narrow(source[MEMORY], r'\bvoid\s+ReportIL2CppClasses\s*\(', 'class reporter')
    filter_callback = narrow(source[MEMORY], r'\bstatic\s+void\s+ReportVisibleClass\s*\(', 'visibility callback')
    has(memory, 'Assembly::GetAllAssemblies()', 'public logical assembly source')
    has(memory, 'GlobalMetadata::GetInitializedTypeInfoFromAssembly(&image, i)', 'initialized only type source')
    has(memory, 'callback = ReportVisibleClass', 'shadow visibility wrapping')
    has(filter_callback, 'AssemblyShadowVisibility::IsClassVisible(klass, report->generation)', 'visibility filter')
    has(memory, 'metadata::ArrayMetadata::WalkArrays(callback, context)', 'array walker')
    has(memory, 'metadata::ArrayMetadata::WalkSZArrays(callback, context)', 'SZ array walker')
    has(memory, 'metadata::GenericMetadata::WalkAllGenericClasses(callback, context)', 'generic class walker')
    has(memory, 'MetadataCache::WalkPointerTypes(callback, context)', 'pointer walker')
    absence(memory, 'Assembly::TryVisitOriginalV1ExecutionImages(', 'public physical independence')

    get_all = narrow(source[ASSEMBLY], r'\bAssemblyVector\s*\*\s*Assembly::GetAllAssemblies\s*\(\s*\)', 'GetAllAssemblies')
    logical = narrow(source[ASSEMBLY], r'\bstatic\s+void\s+CopyLogicalAssemblies\s*\(', 'logical filter')
    physical = narrow(source[ASSEMBLY], r'\bbool\s+Assembly::TryVisitOriginalV1ExecutionImages\s*\(', 'physical visitor')
    valid = narrow(source[ASSEMBLY], r'\bstatic\s+void\s+CopyValidAssemblies\s*\(', 'original V1 eligibility')
    has(get_all, 'CopyLogicalAssemblies(*s_snapshotAssemblies, s_Assemblies)', 'logical snapshot construction')
    has(get_all, 'if (s_assemblyVersion != s_snapshotAssemblyVersion)', 'conditional cached snapshot')
    has(logical, 'AssemblyShadow::ResolveAssembly(physical)', 'shadow resolution')
    has(logical, 'seen.Find(logical->aname.name)', 'logical name deduplication')
    has(valid, 'if (ass->token)', 'token-valid original V1 policy')
    has(physical, 'assembly_shadow_original_v1_image_scan::Scan(', 'physical source scan')
    has(physical, 's_Assemblies.begin(),s_Assemblies.end()', 'physical table iteration')
    absence(physical, 'GetAllAssemblies()', 'physical source cannot be logical snapshot')

    scan = narrow(source[IMAGE_SCAN], r'\bbool\s+Scan\s*\(', 'original V1 physical scan template')
    has(scan, 'if(!assembly->token)continue', 'physical token eligibility')
    has(scan, 'if(!visit(assembly->image))return false', 'physical callback')
    absence(scan, 'IsInterpreterImage(', 'interpreter source must not be filtered')
    absence(scan, 'if(!assembly->image->typeCount)', 'zero-TypeDef images remain eligible')

    initialized = narrow(source[GLOBAL], r'\bIl2CppClass\s*\*\s*il2cpp::vm::GlobalMetadata::GetInitializedTypeInfoFromAssembly\s*\(', 'cached definition')
    has(initialized, 'os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock)', 'metadata lock for cached lookup')
    has(initialized, 'GetCachedTypeInfoFromTypeDefinitionRawIndex(', 'interpreter cached definition only')
    has(initialized, 's_TypeInfoDefinitionTable[typeIndex]', 'AOT cached definition only')
    has(initialized, 'return klass && klass->initialized ? klass : nullptr', 'initialized-only result')
    absence(initialized, 'return GetTypeInfoFromTypeDefinitionIndex(', 'no eager creation')

    generic = narrow(source[GENERIC], r'\bvoid\s+GenericMetadata::WalkAllGenericClasses\s*\(', 'generic walker')
    has(generic, 'FastAutoLock lock(&s_GenericClassMutex)', 'generic cache mutex')
    has(generic, 'if ((*it).key->cached_class != NULL)', 'cached generic only')
    for typ in ('WalkArrays', 'WalkSZArrays'):
        arrays = narrow(source[ARRAY], r'\bvoid\s+ArrayMetadata::'+typ+r'\s*\(', typ)
        has(arrays, 'FastAutoLock lock(&il2cpp::vm::g_MetadataLock)', typ+' metadata lock')
        has(arrays, 'callback(it->second, context)', typ+' cached iterator')
    pointers = narrow(source[POINTER], r'\bvoid\s+il2cpp::vm::MetadataCache::WalkPointerTypes\s*\(', 'pointer walker')
    has(pointers, 'os::FastAutoLock lock(&g_MetadataLock)', 'pointer metadata lock')
    has(pointers, 'm_PointerTypes.UnlockedBegin()', 'pointer cached-map only')

    init = narrow(source[RUNTIME], r'\bbool\s+Runtime::Init\s*\(', 'Runtime Init')
    shutdown = narrow(source[RUNTIME], r'\bvoid\s+Runtime::Shutdown\s*\(', 'Runtime Shutdown')
    gate = narrow(source[LIFETIME], r'\bclass\s+Gate\s+final\s*\{', 'lifetime gate')
    has(init, 'g_MetadataLifetimeGate.OpenAfterInit()', 'admission after startup')
    has(shutdown, 'g_MetadataLifetimeGate.CloseAndDrain()', 'close/drain before metadata teardown')
    has(gate, 'class Reader final', 'Reader lifetime admission')
    has(gate, 'sourceEpoch=detail::kInitialEpoch', 'initial epoch only')
    has(gate, 'std::this_thread::yield()', 'unbounded drain/spin risk')

    b2 = narrow(source[B2], r'\bbool\s+AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive\s*\(', 'B2 captured source')
    has(b2, 'assembly_shadow_metadata_lifetime::Gate::Reader admission(', 'B2 Reader')
    has(b2, 'os::FastAutoLock metadataLock(&g_MetadataLock)', 'B2 source metadata lock')
    has(b2, 'Assembly::TryVisitOriginalV1ExecutionImages(', 'B2 physical registry visit')
    require(b2.count('il2cpp_class_for_each(')==3, 'B2 callback count changed from three')
    require(b2.count('Assembly::TryVisitOriginalV1ExecutionImages(')==2, 'B2 physical visit count changed from two')
    has(b2, 'NonRootOwnerAudit nonRootOwners{}', 'current combined 128 TypeDef audit')
    # These two inventories are deliberately not a homogeneous population.
    # No proof that public observer covers all physical TypeDefs or full VM epoch.
    return {
        'schema':'R03B2EnumeratorPopulationBoundaryV1',
        'result':'PinnedSourcePopulationMismatchOnly',
        'nativeCommit':NATIVE_COMMIT,
        'branch':BRANCH,
        'publicClassPopulation':PUBLIC_SOURCE,
        'originalV1PhysicalPopulation':PHYSICAL_SOURCE,
        'publicClassReportPassesInB2':3,
        'originalPhysicalImagePassesInB2':2,
        'nativeFilesVerified':len(PINNED_BLOBS),
        'separateCacheWalkers': ['array','szarray','generic','pointer'],
        'physicalTokenValidImagesIncludeInterpreterAndZeroTypeDef':True,
        'publicDefinitionLookupRequiresInitializedCachedClass':True,
        'publicLogicalSnapshotMayChangeWithAssemblyVersion':True,
        'physicalAndPublicPopulationEquivalenceProven':False,
        'realPhysicalTypeDefUpperBoundMeasured':False,
        'realObservedTypeDefUsePopulationMeasured':False,
        'realRejectedTypeDefPathsObserved':False,
        'classGcMetadataEpochProven':False,
        'fullOriginalV1Fields14And15Proven':False,
        'nativeV2TransportImplemented':False,
        'realUnityEvidence':False,
        'R03Accepted':False,
        'H2Passed':False,
        'ReadyForHumanReviewGate':False,
        'handoffAuthority':'CLOSED_NO_LOCAL_EXECUTION',
        'exactSourceGitBlobs':dict(PINNED_BLOBS),
    }


def verify_repository(repo: Path) -> dict:
    require((repo / '.git').exists(), 'source must be an exact checkout with .git')
    head = subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True,timeout=30,check=False)
    require(head.returncode==0 and head.stdout.strip()==NATIVE_COMMIT, 'wrong native HEAD')
    source = {path:read_pinned(repo,path,sha) for path,sha in PINNED_BLOBS.items()}
    return check_population_sources(source)


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-root',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        result=verify_repository(args.native_root.resolve(strict=True))
        out=json.dumps(result,sort_keys=True,indent=2)+'\n'
        if args.output:args.output.write_text(out,encoding='utf-8')
        else:sys.stdout.write(out)
    except (SourceMismatch,OSError,subprocess.TimeoutExpired) as ex:
        print(f'B2EnumeratorPopulationRejected: {ex}',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
