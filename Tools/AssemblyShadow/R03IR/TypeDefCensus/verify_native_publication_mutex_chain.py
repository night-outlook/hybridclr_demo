#!/usr/bin/env python3
"""R03 B2 pinned transitive publication-mutex source chain. NOT deadlock proof.

Checks two distinct exact Git commits, three il2cpp_plus and five hybridclr
files. Source-shape checks are necessary for a review, not a complete call
graph, runtime provenance, progress bound, or production integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from verify_native_source_path_boundary import SourceMismatch, code_only, require, scope
from verify_native_lock_lifetime_graph import ordered, require_part

BRANCH = 'codex/assembly-shadow-r01b-h1'
NATIVE_COMMIT = 'cecf4b859d50b128e5c0fc6c90cd89e3a452b96a'
HYBRID_COMMIT = '4b2774b066cfc6afd77a8c8aded6bda7ea574f55'

N_ASSEMBLY = 'libil2cpp/vm/Assembly.cpp'
N_METADATA = 'libil2cpp/vm/MetadataCache.cpp'
N_SHADOW = 'libil2cpp/vm/AssemblyShadow.cpp'
H_ASSEMBLY = 'hybridclr/metadata/Assembly.cpp'
H_STAGED = 'hybridclr/metadata/StagedAssembly.cpp'
H_IMAGE = 'hybridclr/metadata/InterpreterImage.cpp'
H_RUNTIME = 'hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp'
H_CODEC = 'hybridclr/metadata/InterpreterMetadataIndexCodec.h'

PINS_NATIVE = {
    N_ASSEMBLY: 'df1acbfdaf054067720d2e7c1545e49100ad93ec',
    N_METADATA: 'b9a9881c6e6a551c19069446a9be61c21f4c8584',
    N_SHADOW: 'dc941907884b9a7f44ade6085d05f2e4a1a96d9e',
}
PINS_HYBRID = {
    H_ASSEMBLY: 'b77eb08bda9fe8c34f9b64473ffe8426d7b5fff7',
    H_STAGED: '8b9e9da261365326b327051c43c52acc3b2052ce',
    H_IMAGE: 'afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b',
    H_RUNTIME: '509e357359a8912c05adac3434a7e71b3fc3f83c',
    H_CODEC: '2020d4e2da6dea8601525203e7ab307d21c40a73',
}
MAX_FILE_BYTES = 256 * 1024


def compact(source: str, pattern: str, label: str) -> str:
    return ''.join(scope(code_only(source), pattern, label).split())


def active_commit(source: str) -> str:
    # A feature-disabled stub occurs in the same .cpp. Deliberately validate
    # both versions rather than choosing the first or treating them as ambiguous.
    code = code_only(source)
    anchor = r'\bAssemblyShadowError\s+AssemblyShadow::CommitTransaction\s*\('
    instances = list(re.finditer(anchor, code))
    require(len(instances) == 2,
            'exactly one active CommitTransaction and one disabled stub required')
    enabled = ''.join(scope(code[:instances[1].start()], anchor,
                            'active CommitTransaction').split())
    disabled = ''.join(scope(code[instances[1].start():], anchor,
                             'disabled CommitTransaction').split())
    require_part(disabled, 'return AssemblyShadowError::FeatureDisabled;',
                 'disabled implementation must remain explicit')
    return enabled


def check_chain(native: dict[str, str], hybrid: dict[str, str]) -> dict:
    require(set(native) == set(PINS_NATIVE), 'native source-file set changed')
    require(set(hybrid) == set(PINS_HYBRID), 'hybridclr source-file set changed')
    shadow = native[N_SHADOW]
    commit = active_commit(shadow)
    begin = compact(shadow, r'\bbool\s+TryBeginPublication\s*\(', 'begin callback')
    active = compact(shadow, r'\bbool\s+PublishActive\s*\(', 'active callback')
    n_meta = compact(native[N_METADATA],
        r'\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(',
        'native metadata publication')
    n_registry = compact(native[N_METADATA], r'\bbool\s+PublishShadowRegistries\s*\(',
        'native registry publisher')
    n_batch = compact(native[N_ASSEMBLY], r'\bbool\s+Assembly::PublishShadowBatch\s*\(',
        'native assembly batch')
    n_placeholder = compact(native[N_ASSEMBLY],
        r'\bbool\s+Assembly::PublishInterpreterPlaceholder\s*\(',
        'native placeholder publisher')

    staged = compact(hybrid[H_STAGED],
        r'\bbool\s+Assembly::PublishStagedImagesBatch\s*\(',
        'staged image batch')
    image_batch = compact(hybrid[H_IMAGE],
        r'\bInterpreterImage::RegisterImagesBatch\s*\(', 'interpreter image batch')
    image_single = compact(hybrid[H_IMAGE],
        r'\bInterpreterImage::RegisterImage\s*\(', 'interpreter single image')
    runtime_batch = compact(hybrid[H_RUNTIME],
        r'\bRuntime::Error\s+Runtime::PublishBatch\s*\(', 'runtime batch')
    runtime_single = compact(hybrid[H_RUNTIME],
        r'\bRuntime::Error\s+Runtime::Publish\s*\(', 'runtime single')
    codec = compact(hybrid[H_CODEC], r'\bError\s+PublishBatch\s*\(', 'codec publish')
    h_create = compact(hybrid[H_ASSEMBLY],
        r'\bIl2CppAssembly\s*\*\s*Assembly::Create\s*\(',
        'ordinary assembly create')
    h_commit = compact(hybrid[H_ASSEMBLY],
        r'\bstatic\s+void\s+CommitPlaceholder\s*\(',
        'placeholder commit callback')
    h_publish = compact(hybrid[H_ASSEMBLY],
        r'\bstatic\s+bool\s+PublishPlaceholderImage\s*\(',
        'placeholder publish callback')
    h_rollback = compact(hybrid[H_ASSEMBLY],
        r'\bstatic\s+void\s+RollbackPlaceholder\s*\(',
        'placeholder rollback callback')

    # Shadow publication; exact ordered lock scopes and explicit call edges.
    ordered(commit, 'transaction holds through metadata publish',
        'std::unique_lock<std::mutex>lock(transaction.mutex)',
        'MetadataCache::PublishInterpreterAssembliesBatch(',
        'lock.unlock()')
    ordered(n_meta, 'metadata then assembly locks',
        'os::FastAutoLocklock(&il2cpp::vm::g_MetadataLock)',
        'Assembly::PublishShadowBatch(physical,')
    ordered(n_batch, 'assembly lock then callbacks',
        'os::FastAutoLocklock(&s_assemblyLock)',
        'if(!tryBegin(context))returnfalse;',
        'if(!publish(context))')
    require_part(n_registry, 'publication->publishActive(publication->context)',
                 'nested metadata registry commit callback')
    ordered(begin, 'usage lock held across success',
        'LockUsage();', 'UsedClosureMember(*publication.transaction)', 'returntrue;')
    require_part(begin, 'if(publication.used){UnlockUsage();returnfalse;}',
                 'begin failure releases usage lock')
    ordered(active, 'runtime batch completes before active publication',
        'InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)',
        's_active.store(publication.snapshot,std::memory_order_release)')
    success = require_part(active, 's_active.store(publication.snapshot,std::memory_order_release)',
                           'active release store')
    require(active.find('UnlockUsage();', success) > success,
            'success path must release UsageLock after active publication')
    require_part(active, 'publication.runtimePublicationFailed=true;UnlockUsage();returnfalse;',
                 'runtime publisher error releases usage lock')

    ordered(staged, 'staged shim -> image batch',
        'return!imageIndices.empty()&&InterpreterImage::RegisterImagesBatch(')
    ordered(image_batch, 'image batch -> runtime batch',
        'returnInterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count);')
    ordered(runtime_batch, 'runtime reservationMutex -> codec',
        'std::lock_guard<std::mutex>lock(reservationMutex)',
        'current->codec.PublishBatch(current->publishScratch,count)',
        'current->groups[group].active.store(1,std::memory_order_release)')
    ordered(codec, 'codec mutex -> atomic lifecycle stores',
        'std::lock_guard<std::mutex>guard(mutex_)',
        'image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),')
    require_part(codec, 'ValidateHandleLocked(image,reservation)',
                 'codec validation under mutex')
    # No supported callback/VM side effect appears in the reviewed Codec
    # PublishBatch body. A text audit cannot certify all indirect callees.
    for forbidden in ('g_MetadataLock', 's_assemblyLock',
                      'il2cpp_class_for_each(', 'Runtime::ClassInit('):
        require(forbidden not in codec, 'unexpected VM call inside codec publish '+forbidden)

    # Ordinary placeholder publishing uses the SAME reservationMutex/codec
    # pair; it does not use transaction/UsageLock like the shadow batch.
    ordered(h_create, 'ordinary construction before placeholder publish',
        'os::FastAutoLocklock(&il2cpp::vm::g_MetadataLock)',
        'Assembly::PublishInterpreterPlaceholder(')
    ordered(n_placeholder, 'placeholder assembly lock, commit, publish, rollback',
        'os::FastAutoLocklock(&s_assemblyLock)',
        'commit(context)', 'if(!publish(context))', 'rollback(context)')
    require_part(h_commit, '*publication.placeHolder=*publication.privateAssembly;',
                 'placeholder private assembly swap')
    require_part(h_commit, 'publication.image->RebindIl2CppAssembly(publication.placeHolder)',
                 'placeholder assembly backlink update')
    require_part(h_publish, 'InterpreterImage::RegisterImage(publication.image)',
                 'placeholder image registration')
    require_part(h_rollback, '*publication.placeHolder=publication.backup;',
                 'placeholder rollback after error')
    require_part(h_rollback, 'publication.image->RebindIl2CppAssembly(publication.privateAssembly)',
                 'placeholder rollback backlink')
    require_part(image_single, 'returnInterpreterMetadataIndexRuntime::Publish(image->GetIndex())',
                 'single image -> runtime')
    require_part(runtime_single, 'returnPublishBatch(&imageId,1)',
                 'single image uses same mutex chain')

    # User code/managed initialization is AFTER commit's metadata publication
    # and transaction lock drop. This statement does not prove all callbacks
    # are non-executing or exception-safe.
    ordered(commit, 'module init after lock release',
        'MetadataCache::PublishInterpreterAssembliesBatch(',
        'lock.unlock();',
        'InterpreterAssembly::RunStagedModuleInitializer(')

    return {
        'schema':'R03B2TransitivePublicationMutexChainV1',
        'result':'PinnedTransitivePublicationLocksOnly',
        'branch':BRANCH,
        'nativeCommit':NATIVE_COMMIT,
        'hybridclrCommit':HYBRID_COMMIT,
        'nativeFilesPinned':len(PINS_NATIVE),
        'hybridclrFilesPinned':len(PINS_HYBRID),
        'shadowPublicationLockChain':[
            'transaction.mutex','g_MetadataLock','s_assemblyLock',
            'UsageLock','reservationMutex','codec.mutex_'],
        'placeholderPublicationLockChain':[
            'g_MetadataLock','s_assemblyLock','reservationMutex','codec.mutex_'],
        'runtimeBatchUsesReservationMutex':True,
        'codecPublishUsesInternalMutex':True,
        'singleImageUsesSameRuntimePublishBatch':True,
        'moduleInitializerAfterTransactionUnlock':True,
        'reviewedNestedLockDepth':6,
        'explicitFailureUsageUnlockObserved':True,
        'transitivePublicationPathStaticallyTraced':True,
        'opaqueOrUnproved':[
            'other callers of codec/reservation locks, including indirect paths',
            'C++ exception safety of non-RAII UsageLock across third-party functions',
            'Class/GC allocation lifetime, ABA, and actual lock scheduling',
            'actual s_InitLock/reader-drain progress under concurrent publication',
            'real Unity Player, metadata lock latency and stack/RSS cost'],
        'deadlockFreedomProven':False,
        'allReverseEdgesExcluded':False,
        'usageLockExceptionSafetyProven':False,
        'shutdownDrainHasFiniteBound':False,
        'classGcVmEpochProven':False,
        'nativeCollectorIntegrated':False,
        'realUnityEvidence':False,
        'R03Accepted':False,
        'H2Passed':False,
        'ReadyForHumanReviewGate':False,
        'handoffAuthority':'CLOSED_NO_LOCAL_EXECUTION',
        'exactNativeGitBlobs':dict(PINS_NATIVE),
        'exactHybridclrGitBlobs':dict(PINS_HYBRID),
    }


def git(root: Path, *args: str) -> str:
    p = subprocess.run(['git','-C',str(root),*args], capture_output=True,
                       text=True, timeout=30, check=False)
    require(p.returncode == 0, 'Git invocation failed: '+' '.join(args))
    return p.stdout.strip()


def sha_git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def load_pins(root: Path, commit: str, pins: dict[str,str], label: str) -> dict[str,str]:
    require(git(root, 'rev-parse', 'HEAD') == commit,
            label+' repository HEAD does not match fixed source commit')
    result = {}
    for path, blob in pins.items():
        f=root/path
        require(f.is_file() and not f.is_symlink(), label+' absent/symlink file '+path)
        data=f.read_bytes()
        require(len(data)<=MAX_FILE_BYTES, label+' oversized source '+path)
        require(sha_git_blob(data)==blob, label+' worktree blob mismatch '+path)
        require(git(root,'rev-parse','HEAD:'+path)==blob,
                label+' Git tree/blob mismatch '+path)
        try: result[path]=data.decode('utf-8')
        except UnicodeError as error: raise SourceMismatch(label+' non-UTF8 source '+path) from error
    return result


def verify_repositories(native_root: Path, hybridclr_root: Path) -> dict:
    native=load_pins(native_root,NATIVE_COMMIT,PINS_NATIVE,'il2cpp_plus')
    hybrid=load_pins(hybridclr_root,HYBRID_COMMIT,PINS_HYBRID,'hybridclr')
    return check_chain(native,hybrid)


def main(argv: list[str]|None=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-root',type=Path,required=True)
    p.add_argument('--hybridclr-root',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    try:
        result=verify_repositories(args.native_root.resolve(strict=True),
                                   args.hybridclr_root.resolve(strict=True))
        text=json.dumps(result,indent=2,sort_keys=True)+'\n'
        if args.output:args.output.write_text(text,encoding='utf-8')
        else:sys.stdout.write(text)
    except (SourceMismatch,OSError,subprocess.TimeoutExpired) as error:
        print('R03B2TransitivePublicationSourceRejected: '+str(error),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
