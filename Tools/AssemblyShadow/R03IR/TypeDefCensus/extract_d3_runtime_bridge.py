#!/usr/bin/env python3
"""R03 B2 D3: Git-pinned exact native callbacks + actual Runtime/Codec source verifier.

Test-only extraction. Does not compile a Unity Player, modify native sources,
or claim a full VM/GC epoch. All source identities and host inputs are pinned.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from verify_publication_failure_boundary import code_only, require, read_pinned, SourceMismatch
from extract_native_registry_publication import extract_literal

NATIVE_HEAD="e31d73968e1895e46c0d790132f1b10b23f78842"
HYBRID_HEAD="c3c232023724cbad565b85e9b2c3beea8ce2789a"
BRANCH="codex/assembly-shadow-r01b-h1"
N_SHADOW="libil2cpp/vm/AssemblyShadow.cpp"
N_D1="libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h"
N_DECISION="libil2cpp/vm/AssemblyShadowPublicationD3Decision.h"
NATIVE={
    N_SHADOW:"c50ad818a8be2ba4796709427beca42d5bf6f5f5",
    N_D1:"a7edf954bfefeafa1c46ccc9a0ab411b5077cb22",
    N_DECISION:"f398ef34f050102472db7d8bc93d84b5f00e311a",
}
H_RUNTIME="hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp"
H_RUNTIME_H="hybridclr/metadata/InterpreterMetadataIndexRuntime.h"
H_IMAGE="hybridclr/metadata/InterpreterImage.cpp"
H_IMAGE_H="hybridclr/metadata/InterpreterImage.h"
H_STAGED="hybridclr/metadata/StagedAssembly.cpp"
H_ASSEMBLY_H="hybridclr/metadata/Assembly.h"
H_CODEC="hybridclr/metadata/InterpreterMetadataIndexCodec.h"
H_BRIDGE="hybridclr/metadata/AssemblyShadowBridge.h"
HYBRID={
    H_RUNTIME_H:"48dd3b9d188634633d96e86550b21dd04aa3ef34",
    H_RUNTIME:"5906b741d16d050f27e3633bc428edae3183a81a",
    H_IMAGE_H:"3f22af3dcbbb097232d4805ac1f3a5a0e72b1214",
    H_IMAGE:"00d20cdb6d0ecda2ffc493f6a5782ae9c6c7a020",
    H_ASSEMBLY_H:"09e71be1743472ef5353a9bec0952f1f278530a4",
    H_STAGED:"b0676dd1454c1b2d02c69c22cfc4dc5581982f6e",
    H_CODEC:"2020d4e2da6dea8601525203e7ab307d21c40a73",
    H_BRIDGE:"5340c0bf9e4c4c211b4379929f3f79133661505a",
}
HYBRID_BLOCKS=(
    ("imagePublisher",H_IMAGE,
        r"\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::RegisterImagesBatch\s*\(",False),
    ("stagedPublisher",H_STAGED,
        r"\bbool\s+Assembly::PublishStagedImagesBatch\s*\(",False),
)
BLOCKS=(
    ("lockUsage",r"\bvoid\s+LockUsage\s*\(",False),
    ("unlockUsage",r"\bvoid\s+UnlockUsage\s*\(",False),
    ("usedClosure",r"\bCandidate\s*\*\s*UsedClosureMember\s*\(",False),
    ("publication",r"\bstruct\s+Publication\s*\{",True),
    ("releaseUsage",r"\bvoid\s+ReleasePublicationUsage\s*\(",False),
    ("observeCodec",r"\bbool\s+ObserveCodecAttempt\s*\(",False),
    ("observeGroup",r"\bbool\s+ObserveRuntimeGroupPublished\s*\(",False),
    ("beginPublication",r"\bbool\s+TryBeginPublication\s*\(",False),
    ("publishActive",r"\bbool\s+PublishActive\s*\(",False),
)

def compact(s: str)->str:
    return "".join(code_only(s).split())

def verify_source(native:dict[str,str],hybrid:dict[str,str])->None:
    require(set(native)==set(NATIVE) and set(hybrid)==set(HYBRID),
            "source inventories differ")
    n=compact(native[N_SHADOW])
    r=compact(hybrid[H_RUNTIME])
    staged=compact(hybrid[H_STAGED])
    img=compact(hybrid[H_IMAGE])
    codec=compact(hybrid[H_CODEC])
    native_publish=compact(extract_literal(native[N_SHADOW],
        r"\bbool\s+PublishActive\s*\(", "nativePublish",False))
    require(
        "publication.phaseReceipt->Advance(assembly_shadow_publication::Phase::RegistriesAppended)" in native_publish and
        "ObserveCodecAttempt,ObserveRuntimeGroupPublished,context" in native_publish and
        "PublishStagedImagesBatch(publication.imageIndices,&observer)" in native_publish and
        "publication.phaseReceipt->Read().phase!=assembly_shadow_publication::Phase::RuntimeGroupPublished" in native_publish,
        "native PublishActive does not bind required phases"
    )
    require("ClassifyFailedNativeBatch(publicationPhase," in n and
            "snapshot.release();" in n,
            "missing native D3 classifier / post-publication boundary")
    failure=n[n.index("ClassifyFailedNativeBatch(publicationPhase,"):
              n.index("snapshot.release();")]
    require(
        "ClassifyFailedNativeBatch(publicationPhase,publication.used!=nullptr,publication.usageHeld,publication.runtimePublicationFailed)" in n and
        "D3Disposition::ProvenUsedRejection" in failure and
        "s_unexpectedFailure.store(true,std::memory_order_release)" in failure and
        "s_state.store(s_active.load(std::memory_order_acquire)?" in failure and
        "publication.phaseReceipt=&publicationPhase" in n,
        "native fail-closed classification or receipt lifetime changed"
    )
    required=(
        "observer->beforeCodec(observer->context)",
        "current->codec.PublishBatch(current->publishScratch,count)",
        "current->groups[group].active.store(1,std::memory_order_release)",
        "observer->afterRuntimeGroup(observer->context)",
    )
    require(all(item in r for item in required),
            "missing real Runtime Codec/group callback boundary")
    a,b,c,d=(r.index(item) for item in required)
    require(a<b<c<d, "Runtime callbacks are not at real irreversible boundaries")
    require("if(observer&&(!observer->beforeCodec||!observer->afterRuntimeGroup))" in r,
            "invalid observer contract admitted")
    require("RegisterImagesBatch(imageIndices.data(),imageIndices.size(),observer)" in staged,
            "staged forwarding dropped observer")
    require("InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count,observer)" in img,
            "image forwarding dropped observer")
    require("Lifecycle::Published" in codec and "image->lifecycle.store(" in codec,
            "actual Codec lifecycle store missing")
    require("ClassifyFailedNativeBatch" in native[N_DECISION] and
            "outcome == Outcome::InProgress" in native[N_DECISION],
            "D3 fail-closed header changed")
    for decl in (
        "const PublicationObserver* observer = nullptr",
    ):
        require(decl in hybrid[H_RUNTIME_H],
                "Runtime observer declaration changed")
    require("PublicationObserver* observer = nullptr" in hybrid[H_IMAGE_H] and
            "PublicationObserver* observer = nullptr" in hybrid[H_ASSEMBLY_H],
            "intermediate publisher signatures changed")

def extract(native:dict[str,str],hybrid:dict[str,str]):
    verify_source(native,hybrid)
    blocks={}
    items=[]
    for label,anchor,is_struct in BLOCKS:
        body=extract_literal(native[N_SHADOW],anchor,label,is_struct)
        blocks[label]=body
        items.append({"label":label,
                      "sha256":hashlib.sha256(body.encode()).hexdigest(),
                      "bytes":len(body.encode())})
    result="// Exact Git-pinned D3 native callback bodies; host stand-ins ONLY.\n"
    result+="namespace il2cpp { namespace vm { namespace {\n"
    result+="\n".join(blocks[label] for label,_,__ in BLOCKS)
    result+="\n}}}\n"
    result+="namespace hybridclr { namespace metadata {\n"
    for label,path,anchor,is_struct in HYBRID_BLOCKS:
        body=extract_literal(hybrid[path],anchor,label,is_struct)
        result+=body+"\n"
        items.append({"label":label,
                      "sha256":hashlib.sha256(body.encode()).hexdigest(),
                      "bytes":len(body.encode())})
    result+="}}\n"
    return result,items

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native-root",type=Path,required=True)
    p.add_argument("--hybrid-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--receipt",type=Path,required=True)
    args=p.parse_args()
    try:
        native=read_pinned(args.native_root.resolve(strict=True),NATIVE_HEAD,NATIVE)
        hybrid=read_pinned(args.hybrid_root.resolve(strict=True),HYBRID_HEAD,HYBRID)
        cpp,items=extract(native,hybrid)
        require(args.output.name=="D3ExactNativeCallbacks.inc",
                "incorrect D3 native output path")
        args.output.write_text(cpp,encoding="utf8")
        report={
            "schema":"R03B2D3SourceReceiptV1",
            "result":"PassedPinnedD3SourceAndExtractionOnly",
            "nativeHead":NATIVE_HEAD,"hybridHead":HYBRID_HEAD,
            "nativeBlobs":NATIVE,"hybridBlobs":HYBRID,
            "bodyCount":len(items),"bodies":items,
            "generatedSha256":hashlib.sha256(cpp.encode()).hexdigest(),
            "unityPlayerExecuted":False,"realVmBridge":False,
            "fullNativeTranslationUnitsCompiled":False,
            "codecRollbackProven":False,"D4Completed":False,
            "R03Accepted":False,"ReadyForHumanReviewGate":False,
            "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION",
        }
        args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print(json.dumps({"result":report["result"],"bodies":len(items),
                         "generatedSha256":report["generatedSha256"]},sort_keys=True))
        return 0
    except (OSError,ValueError,SourceMismatch) as exc:
        print("D3SourceRejected: "+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
