#!/usr/bin/env python3
"""R03 B2 exact-source VM publication visibility/exception boundary.

Source-contract witness, not a compiler control-flow graph, exception-safety
proof, Unity Player run, or permission to edit native production code.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from verify_publication_failure_boundary import (
    SourceMismatch, code_only, scope, require, read_pinned,
)

BRANCH = "codex/assembly-shadow-r01b-h1"
NATIVE_COMMIT = "cecf4b859d50b128e5c0fc6c90cd89e3a452b96a"
HYBRID_COMMIT = "4b2774b066cfc6afd77a8c8aded6bda7ea574f55"

N_SHADOW = "libil2cpp/vm/AssemblyShadow.cpp"
N_REGISTRY = "libil2cpp/vm/Assembly.cpp"
N_METADATA = "libil2cpp/vm/MetadataCache.cpp"
H_STAGED = "hybridclr/metadata/StagedAssembly.cpp"
H_RUNTIME = "hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp"
H_CODEC = "hybridclr/metadata/InterpreterMetadataIndexCodec.h"
H_BRIDGE = "hybridclr/metadata/AssemblyShadowBridge.cpp"

NATIVE = {
    N_SHADOW: "dc941907884b9a7f44ade6085d05f2e4a1a96d9e",
    N_REGISTRY: "df1acbfdaf054067720d2e7c1545e49100ad93ec",
    N_METADATA: "b9a9881c6e6a551c19069446a9be61c21f4c8584",
}
HYBRID = {
    H_STAGED: "8b9e9da261365326b327051c43c52acc3b2052ce",
    H_RUNTIME: "509e357359a8912c05adac3434a7e71b3fc3f83c",
    H_CODEC: "2020d4e2da6dea8601525203e7ab307d21c40a73",
    H_BRIDGE: "d756308613e4a8e64f67b5295b1ec1787c3901fc",
}


def body(source: str, anchor: str, label: str) -> str:
    return "".join(scope(code_only(source), anchor, label).split())


def location(source: str, token: str, label: str) -> int:
    compact = "".join(token.split())
    pos = source.find(compact)
    require(pos != -1, label + ": missing " + compact[:110])
    require(source.find(compact, pos + 1) == -1,
            label + ": repeated/ambiguous " + compact[:110])
    return pos


def ordered(source: str, label: str, *tokens: str) -> None:
    positions = [location(source, token, label) for token in tokens]
    require(positions == sorted(positions) and len(set(positions)) == len(positions),
            label + ": source order changed")


def enabled_commit(source: str) -> str:
    code = code_only(source)
    anchor = r"\bAssemblyShadowError\s+AssemblyShadow::CommitTransaction\s*\("
    hits = list(re.finditer(anchor, code))
    require(len(hits) == 2, "enabled + disabled CommitTransaction definitions required")
    current = "".join(scope(code[:hits[1].start()], anchor, "enabled commit").split())
    disabled = "".join(scope(code[hits[1].start():], anchor, "disabled commit").split())
    location(disabled, "return AssemblyShadowError::FeatureDisabled;", "disabled branch")
    return current


def check_source(sources: dict[str, str]) -> dict:
    require(set(sources) == set(NATIVE) | set(HYBRID),
            "exact 3 native + 4 HybridCLR source inventory required")

    native = sources[N_SHADOW]
    commit = enabled_commit(native)
    begin = body(native, r"\bbool\s+TryBeginPublication\s*\(", "begin")
    active = body(native, r"\bbool\s+PublishActive\s*\(", "active")
    is_active = body(native, r"\bbool\s+AssemblyShadow::IsActiveShadow\s*\(",
                     "VM active predicate")
    assembly = body(sources[N_REGISTRY],
                    r"\bbool\s+Assembly::PublishShadowBatch\s*\(", "assembly registry")
    registry = body(sources[N_METADATA], r"\bbool\s+PublishShadowRegistries\s*\(",
                    "metadata registry callback")
    metadata = body(sources[N_METADATA],
                    r"\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(",
                    "metadata publisher")
    staged = body(sources[H_STAGED],
                  r"\bbool\s+Assembly::PublishStagedImagesBatch\s*\(", "staged")
    codec = body(sources[H_CODEC], r"\bError\s+PublishBatch\s*\(", "codec")
    runtime = body(sources[H_RUNTIME],
                   r"\bRuntime::Error\s+Runtime::PublishBatch\s*\(", "runtime group")
    public = body(sources[H_RUNTIME], r"\bbool\s+Public\s*\(", "runtime public")
    bridge = body(sources[H_BRIDGE],
                  r"\bbool\s+AssemblyShadowBridge::IsPublicImage\s*\(", "bridge")

    # This source ordering prevents normal-return readers of the registries
    # from observing partially published physical/metadata vectors. It does
    # not prove exceptional exits, callbacks, memory lifetime, or lock progress.
    ordered(metadata, "metadata lock and allocation admission",
            "os::FastAutoLocklock(&il2cpp::vm::g_MetadataLock);",
            "s_cliAssemblies.reserve(s_cliAssemblies.size()+assemblies.size());",
            "Assembly::PublishShadowBatch(physical,")
    ordered(assembly, "physical reserve and publication callback",
            "os::FastAutoLocklock(&s_assemblyLock);",
            "s_Assemblies.reserve(s_Assemblies.size()+assemblies.size());",
            "if(!tryBegin(context))returnfalse;",
            "constsize_toriginalSize=s_Assemblies.size();",
            "for(constIl2CppAssembly*assembly:assemblies)s_Assemblies.push_back(assembly);",
            "if(!publish(context))",
            "s_Assemblies.resize(originalSize);",
            "++s_assemblyVersion;")
    ordered(registry, "metadata rollback on normal false return",
            "constsize_toriginalSize=s_cliAssemblies.size();",
            "for(Il2CppAssembly*assembly:*publication->assemblies)s_cliAssemblies.push_back(assembly);",
            "if(!publication->publishActive(publication->context))",
            "s_cliAssemblies.resize_uninitialized(originalSize);",
            "returntrue;")
    ordered(begin, "cross-callback UsageLock lease",
            "LockUsage();",
            "publication.used=UsedClosureMember(*publication.transaction);",
            "if(publication.used){UnlockUsage();returnfalse;}",
            "returntrue;")
    ordered(active, "runtime group and active snapshot release",
            "InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)",
            "publication.runtimePublicationFailed=true;",
            "for(constauto&member:publication.transaction->closure)",
            "s_active.store(publication.snapshot,std::memory_order_release);",
            "UnlockUsage();returntrue;")
    location(active, "publication.runtimePublicationFailed=true;UnlockUsage();returnfalse;",
             "normal runtime false case")
    ordered(commit, "ownership and failure reset",
            "std::unique_lock<std::mutex>lock(transaction.mutex)",
            "std::unique_ptr<ActiveSnapshot>snapshot(newActiveSnapshot());",
            "s_state.store(AssemblyShadowState::Committing,std::memory_order_release);",
            "MetadataCache::PublishInterpreterAssembliesBatch(assemblies,TryBeginPublication,PublishActive,&publication)",
            "s_state.store(AssemblyShadowState::Validated,std::memory_order_release);",
            "snapshot.release();",
            "lock.unlock();")
    location(commit, "publication.runtimePublicationFailed?", "normal error distinction")
    location(staged,
             "InterpreterImage::RegisterImagesBatch(imageIndices.data(),imageIndices.size())",
             "staged index delegate")
    ordered(runtime, "codec then Runtime group activation",
            "std::lock_guard<std::mutex>lock(reservationMutex);",
            "current->codec.PublishBatch(current->publishScratch,count);",
            "if(error!=Error::None)returnerror;",
            "current->records[imageIds[index]].publicationGroup.store(group,std::memory_order_release);",
            "current->groups[group].active.store(1,std::memory_order_release);",
            "++current->nextPublicationGroup;")
    ordered(codec, "irreversible codec publication",
            "std::lock_guard<std::mutex>guard(mutex_);",
            "if(!image->sealed)returnError::Unfinalized;",
            "image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);",
            "returnError::None;")
    ordered(public, "Runtime public group/VM gate",
            "record->publicationGroup.load(std::memory_order_acquire)",
            "current->groups[group].active.load(std::memory_order_acquire)",
            "AssemblyShadowBridge::IsPublicImage(record->reservation.imageId,image)")
    ordered(bridge, "Bridge assembly identity and VM gate",
            "image->GetIndex()==imageIndex",
            "image->GetIl2CppImage()->assembly&&",
            "il2cpp::vm::AssemblyShadow::IsActiveShadow(image->GetIl2CppImage()->assembly)")
    ordered(is_active, "acquire active snapshot and map member check",
            "s_active.load(std::memory_order_acquire)",
            "active->shadowToBaseline.count(assembly)")

    # Require callback failure to be a true false-return only, not a catch
    # handler masquerading as safe precommit cancellation. These checks alone
    # CANNOT show that all transitive callbacks are noexcept.
    for label, fragment in (
        ("tryBegin", begin), ("publishActive", active),
        ("registry callback", registry), ("assembly registry", assembly),
        ("metadata publisher", metadata), ("commit", commit),
    ):
        require("catch(" not in fragment, label + ": catch/failure policy changed")
    require("UsageLock" not in begin and "UsageLock" not in active,
            "a native usage-lease implementation change requires separate review")
    after_codec = codec[location(codec, "image->lifecycle.store(", "codec store"):]
    require(re.findall(r"\breturnError::(\w+)", after_codec) == ["None"],
            "normal codec return introduced after irreversible publication")
    after_group = runtime[location(runtime, "current->groups[group].active.store(", "group store"):]
    require(re.findall(r"\breturnError::(\w+)", after_group) == ["None"],
            "Runtime error return introduced after group activation")

    return {
        "schema": "R03B2NativePublicationVisibilityBoundaryV1",
        "result": "PinnedNativeNormalReturnAndBridgeBoundaryOnly",
        "branch": BRANCH,
        "nativeCommit": NATIVE_COMMIT,
        "hybridclrCommit": HYBRID_COMMIT,
        "pinnedNativeFiles": len(NATIVE),
        "pinnedHybridclrFiles": len(HYBRID),
        "normalFalseReturnRollsBackPhysicalAndCliVectors": True,
        "runtimeGroupRequiresCodecSuccess": True,
        "vmBridgeRequiresActiveSnapshotMembership": True,
        "usageLockTransferredAcrossCallbacks": True,
        "nativeNormalFailureResetsValidated": True,
        "exceptionalExitRollsBackRegistriesProven": False,
        "crossCallbackUsageLockExceptionSafe": False,
        "unknownPostCodecOutcomeRecoverable": False,
        "concurrentNativeVmReadersProven": False,
        "classGcMetadataLifetimeProven": False,
        "sourceOnly": True,
        "nativeProductionChanged": False,
        "realUnity": False,
        "R03Accepted": False,
        "H2Passed": False,
        "ReadyForHumanReviewGate": False,
        "handoffAuthority": "CLOSED_NO_LOCAL_EXECUTION",
    }


def verify_roots(native: Path, hybrid: Path) -> dict:
    sources = {
        **read_pinned(native, NATIVE_COMMIT, NATIVE),
        **read_pinned(hybrid, HYBRID_COMMIT, HYBRID),
    }
    return check_source(sources)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--hybridclr-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_roots(args.native_root.resolve(strict=True),
                              args.hybridclr_root.resolve(strict=True))
        rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (OSError, SourceMismatch, ValueError) as error:
        print("NativePublicationBoundaryRejected: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
