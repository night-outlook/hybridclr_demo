#!/usr/bin/env python3
"""Exact Git-pinned D2 publisher-body extractor: host-only, not a Unity build.

Literal native definitions are copied byte-for-byte. All 5 source and header
blobs and the pinned HEAD are authenticated before extraction. No change to
Unity build rosters or production files. Source extraction is NOT a CFG proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from verify_publication_failure_boundary import code_only, require, SourceMismatch, read_pinned
from extract_native_registry_publication import extract_literal

BRANCH="codex/assembly-shadow-r01b-h1"
COMMIT="b86a97e1dcca18163df5ac2d5f268bf6de18bbdf"
N_ASSEMBLY="libil2cpp/vm/Assembly.cpp"
N_METADATA="libil2cpp/vm/MetadataCache.cpp"
N_SHADOW="libil2cpp/vm/AssemblyShadow.cpp"
N_ASSEMBLY_H="libil2cpp/vm/Assembly.h"
N_METADATA_H="libil2cpp/vm/MetadataCache.h"
PINS={
 N_ASSEMBLY:"e46ece727d5f03a914a4a6ba147cc69bc4e0a427",
 N_METADATA:"f0f8124ee979d563fdd170fc13c8d90ea29bf702",
 N_SHADOW:"a03111cd93e02ea9d89cd2a3dba8e764e922ba46",
 N_ASSEMBLY_H:"934de0826582339878dc7a70c53f966327c6ef69",
 N_METADATA_H:"1f99a863e80a692053e57781648dba1bcc50f80c",
}
BLOCKS=(
 ("assemblyBatch",N_ASSEMBLY,r"\bbool\s+Assembly::PublishShadowBatch\s*\(",False),
 ("usageAcquire",N_SHADOW,r"\bvoid\s+LockUsage\s*\(",False),
 ("usageRelease",N_SHADOW,r"\bvoid\s+UnlockUsage\s*\(",False),
 ("usedClosure",N_SHADOW,r"\bCandidate\s*\*\s*UsedClosureMember\s*\(",False),
 ("publication",N_SHADOW,r"\bstruct\s+Publication\s*\{",True),
 ("releasePublicationUsage",N_SHADOW,r"\bvoid\s+ReleasePublicationUsage\s*\(",False),
 ("beginPublication",N_SHADOW,r"\bbool\s+TryBeginPublication\s*\(",False),
 ("publishActive",N_SHADOW,r"\bbool\s+PublishActive\s*\(",False),
 ("exceptionTerminal",N_SHADOW,r"\bstruct\s+ScopedUnexpectedPublicationExit\s*\{",False),
 ("metadataContext",N_METADATA,r"\bstruct\s+ShadowPublicationContext\s*\{",True),
 ("metadataBegin",N_METADATA,r"\bbool\s+BeginShadowPublication\s*\(",False),
 ("metadataAbandon",N_METADATA,r"\bvoid\s+AbandonShadowPublication\s*\(",False),
 ("metadataRegistries",N_METADATA,r"\bbool\s+PublishShadowRegistries\s*\(",False),
 ("metadataBatch",N_METADATA,r"\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(",False),
)

def extract(sources):
    require(set(sources)==set(PINS),"D2 source set changed")
    for name,decl in ((N_ASSEMBLY_H,"void (*onAbandon)(void*)"),
                      (N_METADATA_H,"void (*onAbandon)(void*)")):
        require(decl in sources[name],"D2 native header callback signature missing "+name)
    # Fail closed on a source mutation that removes any exception-custody step.
    compact=lambda path:"".join(code_only(sources[path]).split())
    assembly=compact(N_ASSEMBLY)
    metadata=compact(N_METADATA)
    shadowBody=compact(N_SHADOW)
    require("~ScopedPhysicalRollback()noexcept" in assembly and
            "abandon(context);" in assembly and
            "entries.resize(previousSize);" in assembly and
            "rollback.committed=true;" in assembly,
            "physical registry exceptional cleanup contract changed")
    require("~ScopedCliRollback()noexcept" in metadata and
            "s_cliAssemblies.resize_uninitialized(previousSize);" in metadata and
            "AbandonShadowPublication,&publication" in metadata,
            "CLI registry exceptional cleanup contract changed")
    require("if(!publication.usageHeld)return;" in shadowBody and
            "publication.usageHeld=true;" in shadowBody and
            "ReleasePublicationUsage(context);" in shadowBody,
            "idempotent native usage custody contract changed")
    require("exceptionalExit.returned=true;" in shadowBody and
            "s_unexpectedFailure.store(true,std::memory_order_release);" in shadowBody and
            "ReleasePublicationUsage,&publication);" in shadowBody,
            "native terminal-on-exception/usage call site changed")
    published="".join(code_only(extract_literal(
        sources[N_SHADOW],r"\bbool\s+PublishActive\s*\(",
        "native publish active",False)).split())
    require("publication.runtimePublicationFailed=true;ReleasePublicationUsage(context);returnfalse;" in published and
            "s_active.store(publication.snapshot,std::memory_order_release);ReleasePublicationUsage(context);returntrue;" in published,
            "native normal-return usage custody changed")
    shadow=code_only(sources[N_SHADOW])
    enabled=r"\bAssemblyShadowError\s+AssemblyShadow::CommitTransaction\s*\("
    require(len(list(re.finditer(enabled,shadow)))==2,"native enabled+disabled commit must remain")
    require("ReleasePublicationUsage, &publication" in sources[N_SHADOW],"missing native usage release call")
    require("ScopedUnexpectedPublicationExit" in sources[N_SHADOW],"missing exception terminal guard")
    blocks={}
    receipt=[]
    for label,path,anchor,is_struct in BLOCKS:
        exact=extract_literal(sources[path],anchor,label,is_struct)
        if label=="exceptionTerminal":
            # The production function uses 'struct {...} exceptionalExit;'
            # as a local declaration. Retain the exact struct body; append
            # only a host declaration semicolon instead of a local variable.
            require("} exceptionalExit;" in sources[path],
                    "native terminal guard local declarator changed")
            exact += ";"
        blocks[label]=exact
        receipt.append({"label":label,"path":path,
                        "sha256":hashlib.sha256(exact.encode()).hexdigest(),
                        "bytes":len(exact.encode())})
    cpp=(
      "// EXACT PINNED NATIVE DEFINITIONS, TEST-ONLY COMPOSITION\n"
      "namespace il2cpp { namespace vm {\n"
      +blocks["assemblyBatch"]+"\n"
      +"namespace {\n"
      +"\n".join(blocks[x] for x in (
        "usageAcquire","usageRelease","usedClosure","publication",
        "releasePublicationUsage","beginPublication","publishActive",
        "exceptionTerminal"))
      +"\n} // native shadow anonymous\n"
      +"} } // il2cpp::vm\n"
      +"namespace {\n"
      +"\n".join(blocks[x] for x in (
        "metadataContext","metadataBegin","metadataAbandon",
        "metadataRegistries"))
      +"\n} // metadata anonymous\n"
      +blocks["metadataBatch"]+"\n"
    )
    return cpp,receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--receipt",required=True,type=Path)
    a=p.parse_args()
    try:
        sources=read_pinned(a.native_root.resolve(strict=True),COMMIT,PINS)
        content,items=extract(sources)
        require(a.output.name=="D2ExactNativeBodies.inc","D2 output must be D2ExactNativeBodies.inc")
        require(a.output.parent.is_dir() and a.receipt.parent.is_dir(),
                "D2 output/receipt parent absent")
        a.output.write_text(content,encoding="utf8")
        data={
            "schema":"R03B2D2NativeCustodyExactExtractV1",
            "result":"PinnedD2NativeSourceBodiesExtractedOnly",
            "nativeCommit":COMMIT,"branch":BRANCH,
            "sourceBlobs":PINS,"bodyCount":len(items),"bodies":items,
            "generatedSha256":hashlib.sha256(content.encode()).hexdigest(),
            "nativeProductionModifiedByTest":False,
            "runtimeCodecReal":False,"realUnity":False,"R03Accepted":False,
            "H2Passed":False,"ReadyForHumanReviewGate":False,
            "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION",
        }
        a.receipt.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print(json.dumps({"result":data["result"],"bodyCount":data["bodyCount"],
                          "generatedSha256":data["generatedSha256"]},sort_keys=True))
        return 0
    except (SourceMismatch,OSError,ValueError) as e:
        print("R03B2D2NativeSourceRejected: "+str(e),file=sys.stderr)
        return 2
if __name__=="__main__":raise SystemExit(main())
