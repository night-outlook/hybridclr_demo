#!/usr/bin/env python3
"""R03 B2 exact-source lock/lifetime observations, NOT a deadlock/VM proof.

The verified native SHA and complete Git blob pins are mandatory. A lexical
C++ source contract is NOT a compiler control-flow/call-graph analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from verify_native_source_path_boundary import SourceMismatch, code_only, scope, require

NATIVE = 'cecf4b859d50b128e5c0fc6c90cd89e3a452b96a'
BRANCH = 'codex/assembly-shadow-r01b-h1'
BASE = 'libil2cpp/vm/'
B2 = BASE + 'AssemblyShadowBoundedDefinitionExecutionLiveSource.inl'
ASSEMBLY = BASE + 'Assembly.cpp'
METADATA = BASE + 'MetadataCache.cpp'
RUNTIME = BASE + 'Runtime.cpp'
GATE = BASE + 'AssemblyShadowMetadataLifetime.h'
SCAN = BASE + 'AssemblyShadowOriginalV1ImageScan.h'
SHADOW = BASE + 'AssemblyShadow.cpp'
GLOBAL = BASE + 'GlobalMetadata.cpp'
MEMORY = BASE + 'MemoryInformation.cpp'

PINS = {
    B2: 'f988e8a3ebaefe13dde80fa2cb784a673326f395',
    ASSEMBLY: 'df1acbfdaf054067720d2e7c1545e49100ad93ec',
    METADATA: 'b9a9881c6e6a551c19069446a9be61c21f4c8584',
    RUNTIME: '1b176ee5fd3e2127a0237877e5c9c32bc53058b3',
    GATE: 'd2fe09dd51debbbbc71d67b21347f5d971a3cafd',
    SCAN: '41cdb90776f1f68f3fc7cbff85045965e29b99b0',
    SHADOW: 'dc941907884b9a7f44ade6085d05f2e4a1a96d9e',
    GLOBAL: '90a9da38496b316becc3c771be0cd29f8bbf7e7b',
    MEMORY: 'f5bf451d3115d02880f8b54cb932c20c4eda60f6',
}
MAX_BYTES = 256 * 1024


def compact(source: str, pattern: str, label: str) -> str:
    return ''.join(scope(code_only(source), pattern, label).split())


def require_part(code: str, part: str, label: str) -> int:
    part = ''.join(part.split())
    offset = code.find(part)
    require(offset >= 0, f'{label}: expected native operation not found: {part}')
    return offset


def ordered(code: str, label: str, *parts: str) -> None:
    indexes = [require_part(code, item, label) for item in parts]
    require(indexes == sorted(indexes) and len(set(indexes)) == len(indexes),
            f'{label}: source operation order changed: {parts}')


def check_lock_graph(sources: dict[str, str]) -> dict:
    require(set(sources) == set(PINS), 'native source paths differ from exact contract')
    b2 = compact(sources[B2], r'\bbool\s+AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive\s*\(', 'B2')
    phys = compact(sources[ASSEMBLY], r'\bbool\s+Assembly::TryVisitOriginalV1ExecutionImages\s*\(', 'physical visitor')
    scan = compact(sources[SCAN], r'\bbool\s+Scan\s*\(', 'original V1 scan')
    registered = compact(sources[ASSEMBLY], r'\bbool\s+Assembly::TryVisitRegisteredAotImages\s*\(', 'AOT visitor')
    shadow_batch = compact(sources[ASSEMBLY], r'\bbool\s+Assembly::PublishShadowBatch\s*\(', 'shadow batch')
    placeholder = compact(sources[ASSEMBLY], r'\bbool\s+Assembly::PublishInterpreterPlaceholder\s*\(', 'placeholder')
    publisher = compact(sources[METADATA], r'\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(', 'MetadataCache publisher')
    commit = compact(sources[SHADOW], r'\bAssemblyShadowError\s+AssemblyShadow::CommitTransaction\s*\(', 'CommitTransaction')
    begin = compact(sources[SHADOW], r'\bbool\s+TryBeginPublication\s*\(', 'TryBeginPublication callback')
    active = compact(sources[SHADOW], r'\bbool\s+PublishActive\s*\(', 'PublishActive callback')
    registry_publisher = compact(sources[METADATA], r'\bbool\s+PublishShadowRegistries\s*\(', 'PublishShadowRegistries callback')

    ordered(b2, 'B2 Reader -> metadata lock -> physical visitation',
            'assembly_shadow_metadata_lifetime::Gate::Readeradmission(',
            'os::FastAutoLockmetadataLock(&g_MetadataLock)',
            'Assembly::TryVisitOriginalV1ExecutionImages(')
    require(b2.count('Assembly::TryVisitOriginalV1ExecutionImages(') == 2,
            'B2 must visit original-V1 physical images twice under metadata lock')
    require(b2.count('il2cpp_class_for_each(') == 3,
            'B2 public-class callback count drift')
    ordered(b2, 'borrowed source scrub within protected scope',
            'Assembly::TryVisitOriginalV1ExecutionImages(',
            'nonRootOwners.Scrub();',
            'firstPassFacts.Scrub();')
    ordered(phys, 'physical visitation source lock and callback',
            'os::FastAutoLocklock(&s_assemblyLock)',
            'assembly_shadow_original_v1_image_scan::Scan(',
            'visit(image,context)')
    require_part(phys, 's_Assemblies.begin(),s_Assemblies.end()', 'physical registered vector')
    require('GetAllAssemblies(' not in phys, 'physical visitor must not use logical class API')
    ordered(registered, 'registered AOT visitor source lock',
            'os::FastAutoLocklock(&s_assemblyLock)',
            'assembly_shadow_registered_aot_scan::Scan(')
    require_part(scan, 'if(!assembly->token)continue;', 'original V1 token-valid physical eligibility')
    require_part(scan, 'assembly->image->assembly!=assembly', 'physical owner backlink check')
    require_part(scan, 'if(!visit(assembly->image))returnfalse;', 'synchronous physical callback')

    ordered(shadow_batch, 'shadow batch assembly lock and opaque callbacks',
            'os::FastAutoLocklock(&s_assemblyLock)',
            'if(!tryBegin(context))returnfalse;',
            'if(!publish(context))')
    require_part(shadow_batch, 's_Assemblies.push_back(assembly)', 'shadow publication append')
    ordered(placeholder, 'placeholder source lock and callbacks',
            'os::FastAutoLocklock(&s_assemblyLock)', 'commit(context)',
            'if(!publish(context))', 'rollback(context)')
    ordered(publisher, 'metadata lock held across shadow batch publication',
            'os::FastAutoLocklock(&il2cpp::vm::g_MetadataLock)',
            'Assembly::PublishShadowBatch(physical,')
    ordered(commit, 'transaction mutex around metadata/assembly publication',
            'std::unique_lock<std::mutex>lock(transaction.mutex)',
            'MetadataCache::PublishInterpreterAssembliesBatch(',
            'lock.unlock()')
    # Resolve one previously opaque callback *one hop further*: the shadow
    # publication holds transaction -> metadata -> assembly -> short UsageLock.
    # PublishStagedImagesBatch and other callback callees are NOT transitively
    # audited, so this is still no deadlock-freedom or lock-graph closure proof.
    require_part(registry_publisher, 'publication->publishActive(publication->context)',
                 'batch delegates to active publication callback')
    ordered(begin, 'begin callback keeps usage lock held for publication',
            'LockUsage();', 'UsedClosureMember(*publication.transaction)',
            'returntrue;')
    begin_publish=require_part(active,
        'InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)',
        'runtime image batch publication')
    commit_store=require_part(active,
        's_active.store(publication.snapshot,std::memory_order_release)',
        'active release publication')
    require(begin_publish<commit_store and
            active.find('UnlockUsage();',commit_store)>commit_store and
            active.count('UnlockUsage();')>=2,
            'active publication lacks usage lock release on success/failure')
    require_part(active, 'publication.runtimePublicationFailed=true',
                 'publication failure also releases UsageLock')

    init = compact(sources[RUNTIME], r'\bbool\s+Runtime::Init\s*\(', 'Runtime Init')
    shutdown = compact(sources[RUNTIME], r'\bvoid\s+Runtime::Shutdown\s*\(', 'Runtime Shutdown')
    ordered(init, 'runtime gate initial admission after metadata bootstrap',
            'os::FastAutoLocklock(&s_InitLock)',
            'MetadataAllocInitialize();',
            'g_MetadataLifetimeGate.OpenAfterInit()',
            'AssemblyShadowStartup::MarkCoreReady();')
    ordered(shutdown, 'shutdown callback, reader drain, and teardown',
            'os::FastAutoLocklock(&s_InitLock)',
            'FireProcessExitEvent();',
            'g_MetadataLifetimeGate.CloseAndDrain();',
            'shutting_down=true;',
            'Thread::AbortAllThreads();',
            'MetadataAllocCleanup();')
    gate = compact(sources[GATE], r'\bclass\s+Gate\s+final\s*\{', 'MetadataLifetimeGate')
    reader = compact(sources[GATE], r'\bclass\s+Reader\s+final\s*\{', 'Gate Reader')
    close = compact(sources[GATE], r'\bvoid\s+CloseAndDrain\s*\(', 'Gate CloseAndDrain')
    require_part(reader, 'sourceEpoch=detail::kInitialEpoch', 'initial-session gate admission')
    require_part(reader, 'gate.TryEnter(sourceEpoch)', 'reader CAS admission')
    require_part(reader, '~Reader()noexcept{if(gate_)gate_->Leave();}', 'reader release after scope exit')
    ordered(close, 'gate closure and unbounded drain',
            'state_.fetch_or(detail::kClosed,std::memory_order_acq_rel)',
            'while((state_.load(std::memory_order_acquire)&detail::kReaders)!=0)',
            'std::this_thread::yield()')

    cached = compact(sources[GLOBAL], r'\bIl2CppClass\s*\*\s*il2cpp::vm::GlobalMetadata::GetInitializedTypeInfoFromAssembly\s*\(', 'cached classes')
    require_part(cached, 'os::FastAutoLocklock(&il2cpp::vm::g_MetadataLock)', 'cached class metadata protection')
    require_part(cached, 'returnklass&&klass->initialized?klass:nullptr;', 'cached initialized only')
    materialize = compact(sources[GLOBAL], r'\bIl2CppClass\s*\*\s*il2cpp::vm::GlobalMetadata::GetTypeInfoFromTypeDefinitionIndex\s*\(', 'class construction')
    require_part(materialize, 'utils::InitOnce(&s_TypeInfoDefinitionTable[index],&il2cpp::vm::g_MetadataLock', 'class type cache initialization')
    public = compact(sources[MEMORY], r'\bvoid\s+ReportIL2CppClasses\s*\(', 'public enumerator')
    require_part(public, 'Assembly::GetAllAssemblies()', 'logical public assembly list')
    require_part(public, 'GlobalMetadata::GetInitializedTypeInfoFromAssembly(&image,i)', 'cache-only enumeration')

    # These are *syntactically observed* edges; a complete call graph across
    # opaque callbacks is not available. Never promote to deadlock freedom.
    return {
        'schema': 'R03B2NativeLockLifetimeBoundaryV1',
        'result': 'PinnedLockOrderObservationsOnly',
        'nativeCommit': NATIVE,
        'branch': BRANCH,
        'pinnedNativeFileCount': len(PINS),
        'reviewedDirectOrdering': [
            'B2: Reader -> g_MetadataLock -> Assembly.TryVisitOriginalV1 -> s_assemblyLock',
            'MetadataCache.PublishInterpreterAssembliesBatch: g_MetadataLock -> Assembly.PublishShadowBatch -> s_assemblyLock',
            'AssemblyShadow.CommitTransaction: transactionMutex -> MetadataCache.PublishInterpreterAssembliesBatch',
            'Runtime.Shutdown: s_InitLock -> FireProcessExitEvent -> CloseAndDrain -> metadata cleanup',
            'Shadow publication callback: Assembly.s_assemblyLock -> TryBeginPublication -> UsageLock, held through PublishActive',
        ],
        'knownNestedPublicationUsageLock': True,
        'remainingOpaqueWorkUnderAssemblyAndUsageLocks': [
            'PublishActive.InterpreterAssembly.PublishStagedImagesBatch',
            'PublishInterpreterPlaceholder.commit', 'PublishInterpreterPlaceholder.publish',
            'PublishInterpreterPlaceholder.rollback',
        ],
        'shutdownDrainHasProvenFiniteTimeout': False,
        'transitivePublicationCallbackLocksAudited': False,
        'deadlockFreedomProven': False,
        'metadataImageAllocationEpochProven': False,
        'classGcVmEpochProven': False,
        'originalPhysicalRegistryAtomicallyProven': False,
        'nativeCollectorIntegrated': False,
        'realUnityEvidence': False,
        'R03Accepted': False,
        'H2Passed': False,
        'ReadyForHumanReviewGate': False,
        'handoffAuthority': 'CLOSED_NO_LOCAL_EXECUTION',
        'exactNativeGitBlobs': dict(PINS),
    }


def sha_git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\x00'+data).hexdigest()


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(['git','-C',str(repo),*args],capture_output=True,
                            text=True,timeout=30,check=False)
    require(result.returncode == 0, 'git failed: '+' '.join(args))
    return result.stdout.strip()


def verify_repository(repo: Path) -> dict:
    require(git(repo,'rev-parse','HEAD')==NATIVE, 'native HEAD differs from required commit')
    sources = {}
    for path,expected in PINS.items():
        file = repo/path
        require(file.is_file() and not file.is_symlink(), 'missing/nonregular pinned file '+path)
        data=file.read_bytes()
        require(len(data)<=MAX_BYTES, 'native file exceeds bounded verification size '+path)
        require(sha_git_blob(data)==expected, 'native file Git blob mismatch '+path)
        require(git(repo,'rev-parse','HEAD:'+path)==expected,
                'native Git tree/blob mismatch '+path)
        try: sources[path]=data.decode('utf-8')
        except UnicodeError as e: raise SourceMismatch('native file invalid UTF-8 '+path) from e
    return check_lock_graph(sources)


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-root',type=Path,required=True)
    p.add_argument('--output',type=Path)
    options=p.parse_args(argv)
    try:
        response=verify_repository(options.native_root.resolve(strict=True))
        output=json.dumps(response,sort_keys=True,indent=2)+'\n'
        if options.output: options.output.write_text(output,encoding='utf-8')
        else: sys.stdout.write(output)
    except (SourceMismatch,OSError,subprocess.TimeoutExpired) as error:
        print(f'B2LockLifetimeRejected: {error}',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
