#!/usr/bin/env python3
"""R03 B2 D4 exact-source snapshot ownership and P5/P6 host extractor.

Only literal native function/type bodies are compiled into the host. Tests
substitute VM objects, locks and allocator; the actual Runtime/Codec and native
dynamic_array template are separately compiled from exact Git-pinned sources.
No Unity Player, GC epoch or native production TU acceptance is implied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

from extract_d3_runtime_bridge import (
    HYBRID_HEAD, HYBRID, N_SHADOW, N_D1, N_DECISION,
)
from verify_publication_failure_boundary import (
    read_pinned, code_only, require, SourceMismatch,
)
from extract_native_registry_publication import extract_literal

BRANCH="codex/assembly-shadow-r01b-h1"
NATIVE_HEAD="760fe3e7a11ac8cf053714f933e90d26533a9644"
N_ASSEMBLY="libil2cpp/vm/Assembly.cpp"
N_ASSEMBLY_H="libil2cpp/vm/Assembly.h"
N_METADATA="libil2cpp/vm/MetadataCache.cpp"
N_METADATA_H="libil2cpp/vm/MetadataCache.h"
N_FIRST="libil2cpp/vm/AssemblyShadowFirstFailureV2.h"
N_TERMINAL="libil2cpp/vm/AssemblyShadowTerminalExecution.h"
N_TYPES="libil2cpp/vm/AssemblyShadowTypes.h"
N_ARRAY="libil2cpp/utils/dynamic_array.h"
N_OWNER="libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h"
NATIVE={
    N_SHADOW:"19fb95655c56bd8307e247207f7c333ff6a14545",
    N_OWNER:"ccd10ea0a1d273f5fe31f52d346d090b0a5af79c",
    N_D1:"a7edf954bfefeafa1c46ccc9a0ab411b5077cb22",
    N_DECISION:"f398ef34f050102472db7d8bc93d84b5f00e311a",
    N_ASSEMBLY:"e46ece727d5f03a914a4a6ba147cc69bc4e0a427",
    N_ASSEMBLY_H:"934de0826582339878dc7a70c53f966327c6ef69",
    N_METADATA:"f0f8124ee979d563fdd170fc13c8d90ea29bf702",
    N_METADATA_H:"1f99a863e80a692053e57781648dba1bcc50f80c",
    N_FIRST:"85683f06f966725e55891ed08d12b961c9685e56",
    N_TERMINAL:"33258986c31b2e6ae3af17b8553030482a83aef7",
    N_TYPES:"6d1379bc33300e4682468705942721d355481ca7",
    N_ARRAY:"0e6653e6e7efe93f023f63893c1a3b94f347a1d0",
}

def compact(src:str)->str:
    return "".join(code_only(src).split())

def literal(src:str,pattern:str,label:str,is_struct:bool=False)->str:
    return extract_literal(src,pattern,label,is_struct)

# Source-backed bodies in their original C++ namespace.
NATIVE_BLOCKS=(
    ("lockUsage",N_SHADOW,r"\bvoid\s+LockUsage\s*\(",False),
    ("unlockUsage",N_SHADOW,r"\bvoid\s+UnlockUsage\s*\(",False),
    ("usedClosure",N_SHADOW,r"\bCandidate\s*\*\s*UsedClosureMember\s*\(",False),
    ("leaseExitEnum",N_SHADOW,r"\benum\s+class\s+PublicationLeaseExit\s*:",True),
    ("publication",N_SHADOW,r"\bstruct\s+Publication\s*\{",True),
    ("observeCodec",N_SHADOW,r"\bbool\s+ObserveCodecAttempt\s*\(",False),
    ("observeGroup",N_SHADOW,r"\bbool\s+ObserveRuntimeGroupPublished\s*\(",False),
    ("sealBeforeUnlock",N_SHADOW,r"\bvoid\s+SealFailedPublicationBeforeUsageUnlock\s*\(",False),
    ("releaseUsage",N_SHADOW,r"\bvoid\s+ReleasePublicationUsage\s*\(",False),
    ("beginPublication",N_SHADOW,r"\bbool\s+TryBeginPublication\s*\(",False),
    ("publishActive",N_SHADOW,r"\bbool\s+PublishActive\s*\(",False),
    ("terminalMethod",N_SHADOW,r"\bbool\s+TerminalMethodDenied\s*\(",False),
    ("postActiveExit",N_SHADOW,r"\bstruct\s+ScopedPostActiveExit\s*\{",True),
    ("unexpectedExit",N_SHADOW,r"\bstruct\s+ScopedUnexpectedPublicationExit\s*\{",False),
)
METADATA_BLOCKS=(
    ("metadataContext",N_METADATA,r"\bstruct\s+ShadowPublicationContext\s*\{",True),
    ("metadataBegin",N_METADATA,r"\bbool\s+BeginShadowPublication\s*\(",False),
    ("metadataAbandon",N_METADATA,r"\bvoid\s+AbandonShadowPublication\s*\(",False),
    ("metadataRegistries",N_METADATA,r"\bbool\s+PublishShadowRegistries\s*\(",False),
)
HYBRID_BLOCKS=(
    ("imagePublisher","hybridclr/metadata/InterpreterImage.cpp",
     r"\bInterpreterMetadataIndexRuntime::Error\s+InterpreterImage::RegisterImagesBatch\s*\(",False),
    ("stagedPublisher","hybridclr/metadata/StagedAssembly.cpp",
     r"\bbool\s+Assembly::PublishStagedImagesBatch\s*\(",False),
)

def verify(native:dict[str,str],hybrid:dict[str,str])->None:
    require(set(native)==set(NATIVE) and set(hybrid)==set(HYBRID),
            "D4 snapshot source roster changed")
    # Verify real HybridCLR phase boundaries without relying on D3's obsolete
    # `snapshot.release()` source contract.
    run=compact(hybrid["hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp"])
    begin=run.index("observer->beforeCodec(observer->context)")
    codec=run.index("current->codec.PublishBatch(current->publishScratch,count)")
    group=run.index("current->groups[group].active.store(1,std::memory_order_release)")
    after=run.index("observer->afterRuntimeGroup(observer->context)")
    require(begin < codec < group < after, "real Runtime/Codec P3/P4 order changed")
    block={name:compact(literal(native[path],anchor,name,is_struct))
           for name,path,anchor,is_struct in NATIVE_BLOCKS}
    seal=block["sealBeforeUnlock"]
    release=block["releaseUsage"]
    begin=block["beginPublication"]
    publish=block["publishActive"]
    require("publication.phaseReceipt->MarkTerminal(" in seal and
            "s_firstFailureV2.TryFreeze(" in seal and
            "publication.normalFailure?assembly_shadow_first_failure_v2::Origin::TransactionTerminal:assembly_shadow_first_failure_v2::Origin::UnexpectedFailure" in seal and
            "s_unexpectedFailure.store(true,std::memory_order_release);" in seal and
            "s_state.store(" in seal,
            "D3 failure seal / first-error origin incomplete")
    positions=("SealFailedPublicationBeforeUsageUnlock(publication);",
               "publication.usageHeld=false;","UnlockUsage();")
    require(all(item in release for item in positions),
            "terminal seal / usage release step missing")
    require(release.index(positions[0]) < release.index(positions[1]) <
            release.index(positions[2]),
            "terminal seal must precede usage release")
    require("if(!publication.usageHeld)return;" in release and
            "publication.leaseExit==PublicationLeaseExit::Unknown" in release,
            "abandon release no longer idempotent and fail-closed")
    require(begin.index("publication.leaseExit=PublicationLeaseExit::UsedBeforeAppend;") <
            begin.index("ReleasePublicationUsage(context);"),
            "P0 witnessed denial must be flagged before release")
    owner=compact(native[N_OWNER])
    commit=compact(native[N_SHADOW])
    postExit=block["postActiveExit"]
    transfer="publication.transaction->activeOwner.TryPublish(*publication.pendingSnapshot,s_active)"
    p5="publication.phaseReceipt->Advance(assembly_shadow_publication::Phase::ActiveSnapshotPublished)"
    require(transfer in publish and p5 in publish and
            publish.index(transfer) < publish.index(p5) <
            publish.index("publication.leaseExit=PublicationLeaseExit::ActivePublished;") <
            publish.rindex("ReleasePublicationUsage(context);"),
            "P5 was not witnessed AFTER process-owned active pointer release store")
    require("if(!pending||retained_||published.load(std::memory_order_acquire))returnfalse;" in owner and
            "retained_=std::move(pending);" in owner and
            "published.store(retained_.get(),std::memory_order_release);" in owner and
            owner.index("retained_=std::move(pending);") <
                owner.index("published.store(retained_.get(),std::memory_order_release);"),
            "snapshot ownership does not precede the public store")
    require("ProcessSnapshotOwner<ActiveSnapshot>activeOwner;" in commit and
            "publication.pendingSnapshot=&snapshot;" in commit and
            "snapshot.release();" not in commit,
            "snapshot still owned only by the temporary commit stack")
    p6="publicationPhase.Advance(assembly_shadow_publication::Phase::InitializersRunning)"
    finish="publicationPhase.Complete()"
    require(p6 in commit and finish in commit and commit.index(p6) < commit.index(finish) and
            "ScopedPostActiveExitpostActiveExit(publicationPhase);" in commit and
            "postActiveExit.handled=true;" in commit,
            "P6/Complete or protected post-active initializer path missing")
    require("phaseReceipt->MarkTerminal(phaseReason);" in postExit and
            "s_firstFailureV2.TryFreeze(" in postExit and
            "s_unexpectedFailure.store(true,std::memory_order_release);" in postExit and
            "s_state.store(AssemblyShadowState::FailedAfterCommit" in postExit,
            "post-active guard does not fail closed on unexpected exits")
    require(publish.count("publication.normalFailure=true;") >= 4 and
            begin.count("publication.normalFailure=true;") == 1,
            "P4/P5 failure lease classification missing")
    require("if(!committed)" in compact(literal(
                native[N_ASSEMBLY],r"\bbool\s+Assembly::PublishShadowBatch\s*\(",
                "native physical batch")) and
            "abandon(context);entries.resize(previousSize);" in compact(native[N_ASSEMBLY]),
            "D2 physical unwind custody removed")
    require("~ScopedCliRollback()noexcept" in compact(native[N_METADATA]),
            "D2 CLI unwind custody removed")
    require("if(error==AssemblyShadowError::Success)return!TerminalMethodDenied(method);" in
            compact(native[N_SHADOW]),
            "actual AssertMethodIsActive terminal recheck removed")
    require("s_unexpectedFailure.load(std::memory_order_acquire)" in block["terminalMethod"],
            "terminal method guard no longer sees durable publication failure")
    require("s_firstFailureV2.TryFreeze(" in block["unexpectedExit"],
            "original D2 unexpected exit guard removed")

def extract(native:dict[str,str],hybrid:dict[str,str]):
    verify(native,hybrid)
    items=[]
    def get(label,path,regex,is_struct=False):
        body=literal((native if path in native else hybrid)[path],regex,label,is_struct)
        items.append({"label":label,"path":path,
                      "bytes":len(body.encode()),
                      "sha256":hashlib.sha256(body.encode()).hexdigest()})
        return body
    getblock=lambda entry:get(*entry)
    physical=get("physicalBatch",N_ASSEMBLY,r"\bbool\s+Assembly::PublishShadowBatch\s*\(")
    meta_batch=get("metadataBatch",N_METADATA,
                   r"\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(")
    callbacks=[(e[0],getblock(e)) for e in NATIVE_BLOCKS]
    # The production local declaration has "} exceptionalExit;" instead of a
    # standalone struct terminator. Only the trailing host ";" is added.
    callbacks=[(name,src+(";" if name=="unexpectedExit" else ""))
               for name,src in callbacks]
    metadata=[getblock(e) for e in METADATA_BLOCKS]
    hybrid_wrappers=[getblock(e) for e in HYBRID_BLOCKS]
    source=("// Exact Git-pinned D2+D3+D4 source bodies, NOT a Unity Player.\n"
        "namespace il2cpp { namespace vm {\n"
        +physical+"\nnamespace {\n"
        +"\n".join(v for _,v in callbacks)
        +"\n} } }\n"
        +"\nnamespace {\n"+"\n".join(metadata)+"\n}\n"
        +meta_batch+"\n"
        +"namespace hybridclr { namespace metadata {\n"
        +"\n".join(hybrid_wrappers)+"\n} }\n")
    return source,items

def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--native-root",required=True,type=Path)
    arg.add_argument("--hybrid-root",required=True,type=Path)
    arg.add_argument("--output",required=True,type=Path)
    arg.add_argument("--receipt",required=True,type=Path)
    a=arg.parse_args()
    try:
        native=read_pinned(a.native_root.resolve(strict=True),NATIVE_HEAD,NATIVE)
        hybrid=read_pinned(a.hybrid_root.resolve(strict=True),HYBRID_HEAD,HYBRID)
        source,bodies=extract(native,hybrid)
        require(a.output.name=="D4ExactNativeSources.inc",
                "incorrect generated native include name")
        a.output.write_text(source,encoding="utf-8")
        receipt={"schema":"R03D4SnapshotOwnerSourceV1",
                 "result":"PinnedD4SnapshotOwnershipBodiesExtractedOnly",
                 "nativeCommit":NATIVE_HEAD,"hybridCommit":HYBRID_HEAD,
                 "nativeBlobs":NATIVE,"hybridBlobs":HYBRID,
                 "bodyCount":len(bodies),"bodies":bodies,
                 "generatedSha256":hashlib.sha256(source.encode()).hexdigest(),
                 "compileFullNativeTUs":False,"unityPlayerExecuted":False,
                 "gcVmEpochProven":False,"postCodecRollbackProven":False,
                 "D3IndependentReview":"PassD3ForD4","D4IndependentReview":"Pending",
                 "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION"}
        a.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"result":receipt["result"],
                          "bodyCount":len(bodies),
                          "generatedSha256":receipt["generatedSha256"]},sort_keys=True))
    except (SourceMismatch,OSError,ValueError) as error:
        print("D4SourceRejected: "+str(error),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
