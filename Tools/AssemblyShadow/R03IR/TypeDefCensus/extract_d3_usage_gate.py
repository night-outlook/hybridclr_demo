#!/usr/bin/env python3
"""IR-D3-01 exact Git-pinned D2+D3 lease-custody integration extractor.

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
    verify_source as verify_d3_bridge,
)
from verify_publication_failure_boundary import (
    read_pinned, code_only, require, SourceMismatch,
)
from extract_native_registry_publication import extract_literal

BRANCH="codex/assembly-shadow-r01b-h1"
NATIVE_HEAD="40d9a16a6e357f0b3ad1cc93362a93cc41768258"
N_ASSEMBLY="libil2cpp/vm/Assembly.cpp"
N_ASSEMBLY_H="libil2cpp/vm/Assembly.h"
N_METADATA="libil2cpp/vm/MetadataCache.cpp"
N_METADATA_H="libil2cpp/vm/MetadataCache.h"
N_FIRST="libil2cpp/vm/AssemblyShadowFirstFailureV2.h"
N_TERMINAL="libil2cpp/vm/AssemblyShadowTerminalExecution.h"
N_TYPES="libil2cpp/vm/AssemblyShadowTypes.h"
N_ARRAY="libil2cpp/utils/dynamic_array.h"
NATIVE={
    N_SHADOW:"5e5fb4b094ae8111e5f674dfc534d411bf597690",
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
            "D3 lease source roster changed")
    verify_d3_bridge({p:native[p] for p in (N_SHADOW,N_D1,N_DECISION)},hybrid)
    block={name:compact(literal(native[path],anchor,name,is_struct))
           for name,path,anchor,is_struct in NATIVE_BLOCKS}
    seal=block["sealBeforeUnlock"]
    release=block["releaseUsage"]
    begin=block["beginPublication"]
    publish=block["publishActive"]
    require("publication.phaseReceipt->MarkTerminal(" in seal and
            "s_firstFailureV2.TryFreeze(" in seal and
            "s_unexpectedFailure.store(true,std::memory_order_release);" in seal and
            "s_state.store(" in seal,
            "D3 failure seal incomplete")
    require(release.index("SealFailedPublicationBeforeUsageUnlock(publication);") <
            release.index("publication.usageHeld=false;") <
            release.index("UnlockUsage();"),
            "terminal seal must precede usage release")
    require("if(!publication.usageHeld)return;" in release and
            "publication.leaseExit==PublicationLeaseExit::Unknown" in release,
            "abandon release no longer idempotent and fail-closed")
    require(begin.index("publication.leaseExit=PublicationLeaseExit::UsedBeforeAppend;") <
            begin.index("ReleasePublicationUsage(context);"),
            "P0 witnessed denial must be flagged before release")
    require(publish.index("s_active.store(publication.snapshot,std::memory_order_release);") <
            publish.index("publication.leaseExit=PublicationLeaseExit::ActivePublished;") <
            publish.rindex("ReleasePublicationUsage(context);"),
            "native successful active publication release boundary changed")
    require(publish.count("publication.normalFailure=true;") == 2 and
            begin.count("publication.normalFailure=true;") == 1,
            "normal failure receipt not set before usage release")
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
    source=("// Exact Git-pinned D2+D3 source bodies, NOT a Unity Player.\n"
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
        require(a.output.name=="D3LeaseExactSources.inc",
                "incorrect generated native include name")
        a.output.write_text(source,encoding="utf-8")
        receipt={"schema":"R03D3TerminalBeforeUnlockSourceV1",
                 "result":"PinnedD3LeaseCustodyBodiesExtractedOnly",
                 "nativeCommit":NATIVE_HEAD,"hybridCommit":HYBRID_HEAD,
                 "nativeBlobs":NATIVE,"hybridBlobs":HYBRID,
                 "bodyCount":len(bodies),"bodies":bodies,
                 "generatedSha256":hashlib.sha256(source.encode()).hexdigest(),
                 "compileFullNativeTUs":False,"unityPlayerExecuted":False,
                 "gcVmEpochProven":False,"postCodecRollbackProven":False,
                 "D3IndependentReview":"Pending","D4Started":False,
                 "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION"}
        a.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"result":receipt["result"],
                          "bodyCount":len(bodies),
                          "generatedSha256":receipt["generatedSha256"]},sort_keys=True))
    except (SourceMismatch,OSError,ValueError) as error:
        print("D3LeaseSourceRejected: "+str(error),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
