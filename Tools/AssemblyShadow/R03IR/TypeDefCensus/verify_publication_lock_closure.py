#!/usr/bin/env python3
"""R03 B2 pinned Runtime/Codec lock-site survey, NOT a deadlock proof.

Source-only; no native integration, Unity execution, or Local Validation authority.
Check both original repositories at their exact reviewed commits and Git blobs.
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

NATIVE_SHA='cecf4b859d50b128e5c0fc6c90cd89e3a452b96a'
HYBRIDCLR_SHA='4b2774b066cfc6afd77a8c8aded6bda7ea574f55'
BRANCH='codex/assembly-shadow-r01b-h1'
NATIVE_SHADOW='libil2cpp/vm/AssemblyShadow.cpp'
RUNTIME='hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp'
CODEC='hybridclr/metadata/InterpreterMetadataIndexCodec.h'
IMAGE='hybridclr/metadata/InterpreterImage.cpp'
STAGED='hybridclr/metadata/StagedAssembly.cpp'
ASSEMBLY='hybridclr/metadata/Assembly.cpp'
NATIVE_BLOBS={NATIVE_SHADOW:'dc941907884b9a7f44ade6085d05f2e4a1a96d9e'}
HYBRIDCLR_BLOBS={
 RUNTIME:'509e357359a8912c05adac3434a7e71b3fc3f83c',
 CODEC:'2020d4e2da6dea8601525203e7ab307d21c40a73',
 IMAGE:'afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b',
 STAGED:'8b9e9da261365326b327051c43c52acc3b2052ce',
 ASSEMBLY:'b77eb08bda9fe8c34f9b64473ffe8426d7b5fff7',
}
MAX_BYTES=240_000

def compact(source: str, pattern: str, label: str) -> str:
 return ''.join(scope(code_only(source),pattern,label).split())

def need(s: str, fragment: str, label: str) -> int:
 target=''.join(fragment.split())
 offset=s.find(target)
 require(offset>=0, label+': missing '+target)
 return offset

def order(s: str, label: str, *items: str) -> None:
 loc=[need(s,x,label) for x in items]
 require(loc==sorted(loc) and len(set(loc))==len(loc), label+': source order changed')

def check(sources: dict[str,str]) -> dict:
 require(set(sources)==set(NATIVE_BLOBS)|set(HYBRIDCLR_BLOBS),'source files differ from pins')
 runtime=code_only(sources[RUNTIME]); codec=code_only(sources[CODEC]);
 image=code_only(sources[IMAGE]); staged=code_only(sources[STAGED]);
 assembly=code_only(sources[ASSEMBLY]); native=code_only(sources[NATIVE_SHADOW]);
 runtime_lock=re.findall(r'\bstd\s*::\s*lock_guard\s*<\s*std\s*::\s*mutex\s*>\s+lock\s*\(\s*reservationMutex\s*\)',runtime)
 codec_lock=re.findall(r'\bstd\s*::\s*lock_guard\s*<\s*std\s*::\s*mutex\s*>\s+guard\s*\(\s*mutex_\s*\)',codec)
 require(len(runtime_lock)==6,'reservationMutex acquisition inventory drift')
 require(len(codec_lock)==8,'codec mutex acquisition inventory drift')
 require(re.search(r'\bstd\s*::\s*mutex\s+reservationMutex\s*;',runtime)!=None,'reservation mutex declaration absent')
 require(re.search(r'\bmutable\s+std\s*::\s*mutex\s+mutex_\s*;',codec)!=None,'codec mutex declaration absent')
 # For this bounded source scope, the dependency-free codec must not call back
 # into Runtime or acquire its reservation/meta/usage locks.
 for forbidden in ('reservationMutex','g_MetadataLock','LockUsage(','UnlockUsage(',
                   'InterpreterMetadataIndexRuntime::','AssemblyShadow::'):
  require(forbidden not in codec,'codec gained external lock/caller dependency: '+forbidden)
 reserve=compact(runtime,r'\bRuntime::Error\s+Runtime::ReserveImages\s*\(','Runtime ReserveImages')
 publish=compact(runtime,r'\bRuntime::Error\s+Runtime::PublishBatch\s*\(','Runtime PublishBatch')
 abort=compact(runtime,r'\bRuntime::Error\s+Runtime::Abort\s*\(\s*uint32_t','Runtime Abort(imageId)')
 stats=compact(runtime,r'\bRuntime::Error\s+Runtime::GetStats\s*\(','Runtime GetStats')
 init=compact(runtime,r'\bRuntime::Error\s+Runtime::Initialize\s*\(','Runtime Initialize')
 order(reserve,'reservation before codec reserve','lock(reservationMutex);','current.codec.ReserveBatch(')
 order(publish,'reservation before codec publish','lock(reservationMutex);','current->codec.PublishBatch(', 'current->groups[group].active.store(')
 order(abort,'reservation before codec abort','lock(reservationMutex);','current->codec.Abort(')
 order(init,'reservation before state construction','lock(reservationMutex);','new(std::nothrow)RuntimeState()')
 need(stats,'current->codec.GetStats()','direct codec stats source')
 require('reservationMutex' not in stats,'GetStats unexpectedly acquired reservation lock')
 # The two ScopedConstruction overloads also account for the other two
 # reservationMutex sites. No unmodeled acquisition is silently accepted.
 scoped=re.findall(r'\bRuntime::ScopedConstruction::ScopedConstruction\s*\(',runtime)
 require(len(scoped)==2,'ScopedConstruction overload inventory drift')
 remaining=runtime.count('lock(reservationMutex)')
 require(remaining==6,'runtime reservationMutex lock expression inventory drift')
 codec_publish=compact(codec,r'\bError\s+PublishBatch\s*\(','Codec PublishBatch')
 order(codec_publish,'codec published lifecycle under mutex',
       'guard(mutex_);','image->lifecycle.store(', 'returnError::None;')
 require('Runtime::' not in codec_publish,'codec PublishBatch has external Runtime callback')
 image_reserve=compact(image,r'\bInterpreterImageAdmission::Report\s+InterpreterImage::ReserveImageBudget\s*\(','image reserve budget')
 order(image_reserve,'metadata before codec stats and reservation',
       'lock(&il2cpp::vm::g_MetadataLock);',
       'InterpreterMetadataIndexRuntime::GetStats(stats);',
       'InterpreterMetadataIndexRuntime::ReserveImages(')
 image_snapshot=compact(image,r'\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::GetMetadataCapacitySnapshot\s*\(','image stats snapshot')
 order(image_snapshot,'metadata before direct codec stats',
       'lock(&il2cpp::vm::g_MetadataLock);','GetMetadataCapacitySnapshotLocked(')
 image_snapshot_inner=compact(image,r'\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::GetMetadataCapacitySnapshotLocked\s*\(','image locked stats')
 need(image_snapshot_inner,'InterpreterMetadataIndexRuntime::GetStats(stats)','snapshot reads codec stats')
 staged_batch=compact(staged,r'\bbool\s+Assembly::PublishStagedImagesBatch\s*\(','staged batch')
 need(staged_batch,'InterpreterImage::RegisterImagesBatch(','staged image batch delegation')
 image_register=compact(image,r'\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::RegisterImagesBatch\s*\(','image register batch')
 need(image_register,'InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count)','image batch invokes runtime')
 placeholder=compact(assembly,r'\bstatic\s+bool\s+PublishPlaceholderImage\s*\(','placeholder callback')
 need(placeholder,'InterpreterImage::RegisterImage(publication.image)','ordinary placeholder codec publication')
 native_begin=compact(native,r'\bbool\s+TryBeginPublication\s*\(','native begin publication')
 native_active=compact(native,r'\bbool\s+PublishActive\s*\(','native active publication')
 order(native_begin,'manual cross-callback UsageLock custody','LockUsage();','UsedClosureMember(*publication.transaction)','returntrue;')
 order(native_active,'runtime batch then active store then unlock',
       'InterpreterAssembly::PublishStagedImagesBatch(',
       's_active.store(publication.snapshot,std::memory_order_release);',
       'UnlockUsage();returntrue;')
 require(native_active.count('UnlockUsage();')==2,'ordinary failure/success release count drift')
 # Presence of explicit UnlockUsage on ordinary returns is NOT an exception
 # safe ownership proof. This remains a negative result in all reports.
 return {
  'schema':'R03B2PublicationLockClosureV1',
  'result':'PinnedRuntimeCodecLockSiteSurveyOnly',
  'nativeCommit':NATIVE_SHA,'hybridclrCommit':HYBRIDCLR_SHA,'branch':BRANCH,
  'pinnedFiles':{'il2cpp_plus':dict(NATIVE_BLOBS),'hybridclr':dict(HYBRIDCLR_BLOBS)},
  'reservationMutexSites':len(runtime_lock),'codecMutexSites':len(codec_lock),
  'scopedConstructionOverloads':len(scoped),
  'reviewedMutexOrder':['metadata -> reservationMutex -> codec.mutex_',
                        'reservationMutex -> codec.mutex_',
                        'metadata -> codec.mutex_'],
  'directReverseEdgeInAuditedRuntimeCodecSourceObserved':False,
  'observedCrossCallbackManualUsageLock':True,
  'manualUsageLockExceptionSafe':False,
  'reviewedScopeExhaustsAllRuntimeLocks':False,
  'deadlockFreedomProven':False,'shutdownProgressProven':False,
  'classGcVmEpochProven':False,'nativeChangesApplied':False,
  'runtimeUnityEvidence':False,'R03Accepted':False,
  'H2Passed':False,'ReadyForHumanReviewGate':False,
  'handoffAuthority':'CLOSED_NO_LOCAL_EXECUTION'
 }

def git(repo:Path,*args:str)->str:
 p=subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True,timeout=30)
 require(p.returncode==0,'git failed: '+' '.join(args))
 return p.stdout.strip()

def blob(data:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def verified_file(repo:Path,path:str,expected:str)->str:
 f=repo/path
 require(f.is_file() and not f.is_symlink(),'missing/nonregular native source '+path)
 raw=f.read_bytes()
 require(len(raw)<=MAX_BYTES,'source too large '+path)
 require(blob(raw)==expected,'Git blob mismatch '+path)
 require(git(repo,'rev-parse','HEAD:'+path)==expected,'Git tree mismatch '+path)
 try:return raw.decode('utf8')
 except UnicodeError as exc:raise SourceMismatch('source invalid UTF-8 '+path) from exc

def verify_repositories(native:Path,hybridclr:Path)->dict:
 require(git(native,'rev-parse','HEAD')==NATIVE_SHA,'native commit differs')
 require(git(hybridclr,'rev-parse','HEAD')==HYBRIDCLR_SHA,'hybridclr commit differs')
 sources={}
 for path,sha in NATIVE_BLOBS.items():sources[path]=verified_file(native,path,sha)
 for path,sha in HYBRIDCLR_BLOBS.items():sources[path]=verified_file(hybridclr,path,sha)
 return check(sources)

def main(argv:list[str]|None=None)->int:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--native-root',type=Path,required=True)
 p.add_argument('--hybridclr-root',type=Path,required=True)
 p.add_argument('--output',type=Path)
 args=p.parse_args(argv)
 try:
  result=verify_repositories(args.native_root.resolve(strict=True),args.hybridclr_root.resolve(strict=True))
  result_str=json.dumps(result,sort_keys=True,indent=2)+'\n'
  if args.output:args.output.write_text(result_str,encoding='utf8')
  else:sys.stdout.write(result_str)
 except (SourceMismatch,OSError,subprocess.TimeoutExpired) as e:
  print('B2PublicationLockSurveyRejected: '+str(e),file=sys.stderr)
  return 2
 return 0

if __name__=='__main__':raise SystemExit(main())
