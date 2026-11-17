#!/usr/bin/env python3
"""Exact-source static B2 TypeDef path boundary inventory. NOT a runtime census.

This tool checks that the reviewed native snapshot still contains the source
paths and pre-owner rejection boundaries that any future census must cover.
A matching pinned source cannot prove actual callback or VM/GC completeness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

NATIVE_COMMIT = 'cecf4b859d50b128e5c0fc6c90cd89e3a452b96a'
BRANCH = 'codex/assembly-shadow-r01b-h1'
SOURCE = 'libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl'
OWNER = 'libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h'
LIFETIME = 'libil2cpp/vm/AssemblyShadowMetadataLifetime.h'
LIMITS = 'libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h'
PINNED_BLOBS = {
    SOURCE: 'f988e8a3ebaefe13dde80fa2cb784a673326f395',
    OWNER: '75fc8717ed3b54b1aeee583e28671e304ab233e0',
    LIFETIME: 'd2fe09dd51debbbbc71d67b21347f5d971a3cafd',
    LIMITS: '06ce1e0413089e27c555eeb3b6481e03cf560664',
}
MAX_FILE_BYTES = 160_000

# These labels are an inventory of reviewed *static* obligations, not a
# generated closed-world census or a source-instrumentation implementation.
PATHS = (
    ('ClassRoot', 'buildDefinition(definition,image,definitionKey', 'root'),
    ('DeclaringAncestor', 'handle=declaring->data.typeHandle;', 'nonroot'),
    ('GenericDefinition', 'makeDefinition(g->type->data.typeHandle', 'nonroot'),
    ('GenericArgument', 'Format(args->type_argv[i],child,depth+1)', 'nonroot'),
    ('CompositeClassLeaf', 'makeDefinition(value->data.typeHandle', 'nonroot'),
    ('PrimitiveDefault', 'makeDefinition(primitive->typeMetadataHandle', 'nonroot'),
)
REJECTIONS = (
    ('PreOwnerMissingTypeDef', 'if(!handle)'),
    ('AncestryCycle', 'if(verifiedHandles[j]==handle)'),
    ('InterpreterUnsupportedAncestry', 'if(hybridclr::metadata::IsInterpreterIndex(currentOwner->token)'),
    ('MissingCompositeType', 'if(!value||depth>MaximumDepth)'),
    ('MissingGenericContainer', 'if(!g||!g->type||'),
    ('InvalidArrayShape', 'if(!array||!array->rank'),
    ('MissingPrimitiveDefault', 'if(!primitive || !primitive->image ||'),
)

class SourceMismatch(ValueError):
    pass

def require(condition: bool, error: str) -> None:
    if not condition:
        raise SourceMismatch(error)

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

_CXX_NONTEXT = re.compile(
    r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.MULTILINE)

def code_only(source: str) -> str:
    """Replace comments/quoted text with whitespace, retaining offsets."""
    return _CXX_NONTEXT.sub(lambda match: re.sub(r'[^\n]', ' ', match.group(0)), source)

def scope(code: str, anchor: str, label: str) -> str:
    matches = list(re.finditer(anchor, code, re.MULTILINE | re.DOTALL))
    require(len(matches)==1, f'{label}: anchor missing or ambiguous ({len(matches)})')
    start = (matches[0].end()-1 if code[matches[0].end()-1]=='{'
             else code.find('{', matches[0].end()))
    require(start >= 0 and start-matches[0].end() <= 420,
            f'{label}: no bounded body')
    depth = 0
    for i in range(start,len(code)):
        if code[i]=='{':
            depth+=1
        elif code[i]=='}':
            depth-=1
            if depth==0:
                return code[start+1:i]
    raise SourceMismatch(f'{label}: unbalanced braces')

def present(block: str, fragment: str, label: str) -> int:
    # Whitespace differences are intentionally permitted when checking a
    # semantic source statement; the whole Git blob is pinned separately.
    pattern = re.escape(fragment)
    pattern = re.sub(r'\\\s+',r'\\s*', pattern)
    matches=list(re.finditer(pattern,block))
    require(len(matches)>0, f'{label}: missing source expression {fragment!r}')
    return matches[0].start()

def check_source(source: str, owner: str, lifetime: str, limits: str) -> dict:
    code=code_only(source)
    join=code_only(owner)
    life=code_only(lifetime)
    limit=code_only(limits)
    capture=scope(code,r'\bbool\s+AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive\s*\(', 'Capture')
    resolve=scope(capture,r'\bauto\s+resolveOwner\s*=\s*\[&\]', 'resolveOwner')
    definition=scope(capture,r'\bauto\s+buildDefinition\s*=\s*\[&\]', 'buildDefinition')
    composer=scope(capture,r'\bstruct\s+Composer\s*\{', 'Composer')
    formatting=scope(composer,r'\bbool\s+Format\s*\(', 'Composer.Format')
    raw=scope(composer,r'\bbool\s+Raw\s*\(', 'Composer.Raw')

    require(len(re.findall(r'\bil2cpp_class_for_each\s*\(',capture))==3,
            'expected exactly three physical class enumerations')
    require(len(re.findall(r'\bAssembly::TryVisitOriginalV1ExecutionImages\s*\(',capture))==2,
            'expected two original-V1 physical image enumerations')
    present(capture,'assembly_shadow_metadata_lifetime::Gate::Reader admission(', 'admitted metadata reader')
    present(capture,'os::FastAutoLock metadataLock(&g_MetadataLock)', 'real metadata lock')
    present(capture,'Assembly::TryVisitOriginalV1ExecutionImages(', 'original source')
    present(capture,'CountDistinctKeysCapped<', 'root-only preflight')
    present(capture,'NonRootOwnerAudit nonRootOwners{}', '128-cap exact audit')
    present(limit,'kMaximumNonRootTypeDefOwnerPairs = 128;', 'combined native handle ceiling')
    present(limit,'kMaximumTotalMetadataLookups = 65536;', 'native indexed lookup ceiling')
    present(limit,'kMaximumNonRootTypeDefNameBytes = 64;', 'native exact name ceiling')

    first=present(resolve,'original_join::CheckFirstOwner(', 'first-owner check')
    note=present(resolve,'c.nonRootOwners->Note(', '128-cap audit insertion')
    require(first<note,'B2 audit insertion now precedes original first-owner proof')
    index=present(resolve,'MetadataCache::GetAssemblyTypeHandle(', 'indexed TypeDef source')
    require(index<first,'indexed TypeDef source no longer precedes first-owner proof')
    resolved=present(definition,'resolveOwner(handle,', 'TypeDef source owner')
    deref=present(definition,'reinterpret_cast<const Il2CppTypeDefinition*>(handle)', 'metadata dereference')
    require(resolved<deref,'TypeDef dereference moved before owner resolution')
    present(join,'for(size_t i=0;i<originalImages.Count();++i)', 'original V1 image order')
    present(join,'if(read(image,j)==handle)', 'original first-emplace equality')
    present(join,'if(image!=expectedAotImage)', 'first owner validation')
    present(life,'sourceEpoch=detail::kInitialEpoch', 'initial metadata lifetime admission')

    witness_blocks={
        'ClassRoot':capture,
        'DeclaringAncestor':definition,
        'GenericDefinition':raw,
        'GenericArgument':raw,
        'CompositeClassLeaf':raw,
        'PrimitiveDefault':raw,
    }
    for name,fragment,_ in PATHS:
        present(witness_blocks[name],fragment,f'path:{name}')
    present(formatting,'if(!value||depth>MaximumDepth)return Fail()', 'composite recursion limit')
    for tag in ['IL2CPP_TYPE_CLASS','IL2CPP_TYPE_VALUETYPE','IL2CPP_TYPE_GENERICINST',
                'IL2CPP_TYPE_PTR','IL2CPP_TYPE_SZARRAY','IL2CPP_TYPE_ARRAY']:
        present(raw,'case '+tag+':',f'composite switch {tag}')
    present(raw,'assembly_shadow_existing_primitive_defaults::Peek(', 'primitive default lookup')
    for label,fragment in REJECTIONS:
        if label in ('PreOwnerMissingTypeDef','AncestryCycle','InterpreterUnsupportedAncestry'):
            block=definition
        elif label=='MissingCompositeType':
            block=formatting
        else:
            block=raw
        present(block,fragment,f'pre-owner rejection:{label}')
    require('TypeDefSourceCoverageReplay' not in code,
            'source changed to include a prototype coverage module')
    # This proves only the *pinned source statements* exist. No native census
    # attaches here; the gap count is descriptive, never an acceptance claim.
    return {
        'kind':'R03B2NativeSourcePathBoundary',
        'result':'PinnedStaticBoundaryOnly',
        'branch':BRANCH,
        'nativeCommit':NATIVE_COMMIT,
        'staticPathLabels':[p[0] for p in PATHS],
        'preOwnerOrPreCoverageRejectionBoundaries':[p[0] for p in REJECTIONS],
        'physicalClassPasses':3,
        'originalV1ImagePasses':2,
        'originalFirstOwnerBefore128Audit':True,
        'nativeCombinedTypeDefLimit':128,
        'nativeIndexedLookupLimit':65536,
        'nativePerNameFieldLimit':64,
        'producerIntegrated':False,
        'allRealTypeDefPathsDiscovered':False,
        'rejectedPathsObservedByNativeCensus':False,
        'metadataLifetimeIndependentlyProven':False,
        'classGcVmEpochProven':False,
        'realUnityPlayerEvidence':False,
        'R03Accepted':False,
        'H2Passed':False,
        'ReadyForHumanReviewGate':False,
        'handoffAuthority':'CLOSED_NO_LOCAL_EXECUTION'
    }

def git(repo: Path,*args: str) -> str:
    proc=subprocess.run(['git','-C',str(repo),*args],capture_output=True,
                        text=True,timeout=30,check=False)
    require(proc.returncode==0, 'git invocation failed: '+' '.join(args))
    return proc.stdout.strip()

def read_pinned(repo: Path,relative: str,expected: str) -> str:
    path=repo/relative
    require(path.is_file() and not path.is_symlink(), 'missing/symlink native source: '+relative)
    data=path.read_bytes()
    require(len(data)<=MAX_FILE_BYTES,'oversized native source: '+relative)
    require(blob_sha(data)==expected,'native Git blob changed: '+relative)
    line=git(repo,'ls-tree','HEAD','--',relative)
    require(len(line.split())>=3 and line.split()[2]==expected,
            'worktree/native Git-tree provenance mismatch: '+relative)
    try:
        return data.decode('utf-8')
    except UnicodeError as exc:
        raise SourceMismatch('invalid UTF-8 source') from exc

def verify_repository(repo: Path) -> dict:
    require(git(repo,'rev-parse','HEAD')==NATIVE_COMMIT,
            'native checkout does not match pinned source commit')
    inputs={k:read_pinned(repo,k,digest) for k,digest in PINNED_BLOBS.items()}
    result=check_source(inputs[SOURCE],inputs[OWNER],inputs[LIFETIME],inputs[LIMITS])
    result['nativeSourceGitBlob']=PINNED_BLOBS[SOURCE]
    result['exactSourceFiles']=dict(PINNED_BLOBS)
    return result

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native-root',type=Path,required=True)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    try:
        result=verify_repository(args.native_root.resolve(strict=True))
        encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
        if args.output:
            args.output.write_text(encoded,encoding='utf-8')
        else:
            print(encoded,end='')
    except (OSError,SourceMismatch,subprocess.TimeoutExpired) as exc:
        print('B2SourceBoundaryRejected: '+str(exc),file=__import__('sys').stderr)
        return 2
    return 0
if __name__=='__main__':
    raise SystemExit(main())
