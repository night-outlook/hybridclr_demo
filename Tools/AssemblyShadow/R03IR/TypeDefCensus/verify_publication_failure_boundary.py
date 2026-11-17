#!/usr/bin/env python3
"""Pinned source: R03 B2 publication point-of-no-return (NOT runtime acceptance).

This is a narrow lexical source contract. It checks normal-return ordering and
irreversible-state transition locations; it cannot prove exception freedom,
atomicity under concurrency, or recovery. It never changes native source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
class SourceMismatch(ValueError):
    pass

def require(ok:bool,message:str)->None:
    if not ok:raise SourceMismatch(message)

_NONCODE=re.compile(r"//[^\n]*|/\*[\s\S]*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'",re.MULTILINE)

def code_only(s:str)->str:
    return _NONCODE.sub(lambda m:re.sub(r'[^\n]',' ',m.group(0)),s)

def scope(code:str,anchor:str,label:str)->str:
    hits=list(re.finditer(anchor,code,re.MULTILINE|re.DOTALL))
    require(len(hits)==1,f'{label}: ambiguous/missing anchor {len(hits)}')
    start=code.find('{',hits[0].end())
    require(start>=0 and start-hits[0].end()<=420,label+': missing function body')
    depth=0
    for i in range(start,len(code)):
        if code[i]=='{':depth+=1
        elif code[i]=='}':
            depth-=1
            if depth==0:return code[start+1:i]
    raise SourceMismatch(label+': unbalanced function body')

NATIVE_COMMIT='cecf4b859d50b128e5c0fc6c90cd89e3a452b96a'
HYBRIDCLR_COMMIT='4b2774b066cfc6afd77a8c8aded6bda7ea574f55'
BRANCH='codex/assembly-shadow-r01b-h1'
N_SHADOW='libil2cpp/vm/AssemblyShadow.cpp'
H_STAGED='hybridclr/metadata/StagedAssembly.cpp'
H_IMAGE='hybridclr/metadata/InterpreterImage.cpp'
H_RUNTIME='hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp'
H_CODEC='hybridclr/metadata/InterpreterMetadataIndexCodec.h'
NATIVE={N_SHADOW:'dc941907884b9a7f44ade6085d05f2e4a1a96d9e'}
HYBRIDCLR={
    H_STAGED:'8b9e9da261365326b327051c43c52acc3b2052ce',
    H_IMAGE:'afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b',
    H_RUNTIME:'509e357359a8912c05adac3434a7e71b3fc3f83c',
    H_CODEC:'2020d4e2da6dea8601525203e7ab307d21c40a73',
}
MAX_BYTES=256*1024

def compact(source:str,pattern:str,label:str)->str:
    return ''.join(scope(code_only(source),pattern,label).split())

def contains(s:str,value:str,label:str)->int:
    val=''.join(value.split())
    pos=s.find(val)
    require(pos>=0,label+' missing expression '+val)
    return pos

def ordered(s:str,label:str,*fragments:str)->None:
    positions=[contains(s,x,label) for x in fragments]
    require(positions==sorted(positions) and len(positions)==len(set(positions)),label+' order changed')

def check_source(sources:dict[str,str])->dict:
    require(set(sources)==set(NATIVE)|set(HYBRIDCLR),'source inventory differs')
    native=code_only(sources[N_SHADOW]); anchor=r'\bAssemblyShadowError\s+AssemblyShadow::CommitTransaction\s*\('
    locations=list(re.finditer(anchor,native))
    require(len(locations)==2,'expected enabled and FeatureDisabled CommitTransaction definitions')
    commit=''.join(scope(native[:locations[1].start()],anchor,'enabled commit').split())
    stub=''.join(scope(native[locations[1].start():],anchor,'disabled stub').split())
    contains(stub,'return AssemblyShadowError::FeatureDisabled;','disabled source branch')
    begin=compact(sources[N_SHADOW],r'\bbool\s+TryBeginPublication\s*\(','usage begin')
    active=compact(sources[N_SHADOW],r'\bbool\s+PublishActive\s*\(','active publication')
    staged=compact(sources[H_STAGED],r'\bbool\s+Assembly::PublishStagedImagesBatch\s*\(','staged batch')
    image=compact(sources[H_IMAGE],r'\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::RegisterImagesBatch\s*\(','interpreter image batch')
    runtime=compact(sources[H_RUNTIME],r'\bRuntime::Error\s+Runtime::PublishBatch\s*\(','sparse runtime batch')
    codec=compact(sources[H_CODEC],r'\bError\s+PublishBatch\s*\(','codec batch')

    ordered(begin,'cross-callback manual lock','LockUsage();','UsedClosureMember(*publication.transaction)','returntrue;')
    contains(begin,'if(publication.used){UnlockUsage();returnfalse;}','used closure rejection')
    ordered(active,'native active publication',
       'InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)',
       'publication.runtimePublicationFailed=true;',
       'for(constauto&member:publication.transaction->closure)',
       's_active.store(publication.snapshot,std::memory_order_release);',
       'UnlockUsage();returntrue;')
    contains(active,'publication.runtimePublicationFailed=true;UnlockUsage();returnfalse;',
       'normal false path unlock')
    # This is explicitly manual: no destruction-owned UsageLock in these bodies.
    require('UsageLock' not in active and 'UsageLock' not in begin.replace('LockUsage();','').replace('UnlockUsage();',''),
        'native callback ownership changed')
    ordered(commit,'native transaction after publication',
        's_state.store(AssemblyShadowState::Committing,std::memory_order_release);',
        'MetadataCache::PublishInterpreterAssembliesBatch(assemblies,TryBeginPublication,PublishActive,&publication)',
        's_state.store(AssemblyShadowState::Validated,std::memory_order_release);',
        'snapshot.release();',
        'lock.unlock();')
    contains(commit,'publication.runtimePublicationFailed?','current normal false return selection')
    contains(staged,'InterpreterImage::RegisterImagesBatch(imageIndices.data(),imageIndices.size())','staged→image delegation')
    contains(image,'InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count)','image→runtime delegation')

    ordered(runtime,'runtime point of no return',
       'std::lock_guard<std::mutex>lock(reservationMutex);',
       'current->codec.PublishBatch(current->publishScratch,count);',
       'if(error!=Error::None)returnerror;',
       'current->records[imageIds[index]].publicationGroup.store(group,std::memory_order_release);',
       'current->groups[group].active.store(1,std::memory_order_release);',
       '++current->nextPublicationGroup;',
       'returnError::None;')
    post_runtime=runtime[runtime.index('current->groups[group].active.store'):]
    require(re.findall(r'\breturnError::(\w+)',post_runtime)==['None'],
       'normal error return introduced after publication group activation')
    ordered(codec,'codec validation before irreversible lifecycle stores',
       'std::lock_guard<std::mutex>guard(mutex_);',
       'for(size_tindex=0;index<count;++index)',
       'if(!image->sealed)returnError::Unfinalized;',
       'image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);',
       'returnError::None;')
    lifecycle=codec.index('image->lifecycle.store(')
    require(re.findall(r'\breturnError::(\w+)',codec[lifecycle:])==['None'],
       'normal error return introduced after irreversible lifecycle store')
    require('throw' not in codec[lifecycle:] and 'throw' not in post_runtime,
       'explicit throwing operation introduced after irreversible store')

    return {
      'schema':'R03B2PublicationFailureBoundaryV1',
      'result':'PinnedNormalReturnIrreversibilityBoundaryOnly',
      'nativeCommit':NATIVE_COMMIT,
      'hybridclrCommit':HYBRIDCLR_COMMIT,
      'branch':BRANCH,
      'pinnedNativeCount':len(NATIVE),
      'pinnedHybridclrCount':len(HYBRIDCLR),
      'observedPhases':['Validation','CodecLifecyclePublished','PublicationGroupVisible','ActiveSnapshotPublished'],
      'nativeNormalFailureResetsValidated':True,
      'nativeManualUsageLockAcrossCallbacks':True,
      'normalCodecErrorReturnsAfterLifecycleWritesObserved':False,
      'exceptionFreePublicationProven':False,
      'rollbackAfterCodecPublishProven':False,
      'safeRetryAfterUnknownExceptionProven':False,
      'terminalRestartPolicyIntegrated':False,
      'wholeVmEpochProven':False,
      'nativeCollectorIntegrated':False,
      'realUnityEvidence':False,
      'R03Accepted':False,'H2Passed':False,'ReadyForHumanReviewGate':False,
      'handoffAuthority':'CLOSED_NO_LOCAL_EXECUTION'
    }

def git(repo:Path,*args:str)->str:
    p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=30)
    require(p.returncode==0,'git failed '+' '.join(args))
    return p.stdout.strip()

def sha_blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def read_pinned(repo:Path,sha:str,items:dict[str,str])->dict[str,str]:
    require(git(repo,'rev-parse','HEAD')==sha,'repository HEAD differs from pinned source')
    results={}
    for path,blob in items.items():
        f=repo/path
        require(f.is_file() and not f.is_symlink(),'missing or symlink source '+path)
        raw=f.read_bytes()
        require(len(raw)<=MAX_BYTES,'oversized source '+path)
        require(sha_blob(raw)==blob and git(repo,'rev-parse','HEAD:'+path)==blob,
                'Git tree/file blob drift '+path)
        try:results[path]=raw.decode('utf-8')
        except UnicodeError as e:raise SourceMismatch('invalid UTF-8 in '+path) from e
    return results

def verify_repositories(native:Path,hybridclr:Path)->dict:
    sources={**read_pinned(native,NATIVE_COMMIT,NATIVE),**read_pinned(hybridclr,HYBRIDCLR_COMMIT,HYBRIDCLR)}
    report=check_source(sources)
    report['exactGitBlobs']={'il2cpp_plus':NATIVE,'hybridclr':HYBRIDCLR}
    return report

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-root',required=True,type=Path)
    p.add_argument('--hybridclr-root',required=True,type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    try:
        result=verify_repositories(a.native_root.resolve(strict=True),a.hybridclr_root.resolve(strict=True))
        data=json.dumps(result,sort_keys=True,indent=2)+'\n'
        if a.output:a.output.write_text(data,encoding='utf8')
        else:sys.stdout.write(data)
    except (OSError,SourceMismatch,subprocess.TimeoutExpired) as e:
        print('PublicationBoundaryRejected: '+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
