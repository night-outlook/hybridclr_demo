#!/usr/bin/env python3
"""Extract literal, exact Git-pinned native publication functions for a host-only TU.

No rewrite, transpilation, product source change, or claim that mock types
reproduce Unity VM/GC/metadata behavior. Fails closed on source/ref drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from verify_publication_failure_boundary import SourceMismatch, code_only, read_pinned, require

BRANCH = "codex/assembly-shadow-r01b-h1"
NATIVE_COMMIT = "cecf4b859d50b128e5c0fc6c90cd89e3a452b96a"
ASSEMBLY = "libil2cpp/vm/Assembly.cpp"
METADATA = "libil2cpp/vm/MetadataCache.cpp"
SHADOW = "libil2cpp/vm/AssemblyShadow.cpp"
PINS = {
    ASSEMBLY: "df1acbfdaf054067720d2e7c1545e49100ad93ec",
    METADATA: "b9a9881c6e6a551c19069446a9be61c21f4c8584",
    SHADOW: "dc941907884b9a7f44ade6085d05f2e4a1a96d9e",
}

# Order matters: these are the methods declared in NativeRegistryExceptionalHost.
SLICES = (
    ("assemblyBatch", ASSEMBLY, r"\bbool\s+Assembly::PublishShadowBatch\s*\(", False),
    ("usageAcquire", SHADOW, r"\bvoid\s+LockUsage\s*\(", False),
    ("usageRelease", SHADOW, r"\bvoid\s+UnlockUsage\s*\(", False),
    ("usedClosure", SHADOW, r"\bCandidate\s*\*\s*UsedClosureMember\s*\(", False),
    ("publicationContext", SHADOW, r"\bstruct\s+Publication\s*\{", True),
    ("beginPublication", SHADOW, r"\bbool\s+TryBeginPublication\s*\(", False),
    ("publishActive", SHADOW, r"\bbool\s+PublishActive\s*\(", False),
    ("metadataContext", METADATA, r"\bstruct\s+ShadowPublicationContext\s*\{", True),
    ("metadataBegin", METADATA, r"\bbool\s+BeginShadowPublication\s*\(", False),
    ("metadataRegistries", METADATA, r"\bbool\s+PublishShadowRegistries\s*\(", False),
    ("metadataBatch", METADATA, r"\bbool\s+il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch\s*\(", False),
)


def extract_literal(source: str, anchor: str, label: str, is_struct: bool) -> str:
    clean = code_only(source)  # preserves offsets, blanks literals and comments
    matches = list(re.finditer(anchor, clean))
    require(len(matches) == 1, label + ": missing/ambiguous source definition")
    match = matches[0]
    brace = clean.find("{", match.start())
    require(brace >= 0 and brace - match.end() < 600,
            label + ": missing body after signature")
    depth = 0
    end = -1
    for index in range(brace, len(clean)):
        if clean[index] == "{":
            depth += 1
        elif clean[index] == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    require(end > 0, label + ": unbalanced literal function")
    if is_struct:
        require(clean[end:end + 1] == ";", label + ": struct terminator missing")
        end += 1
    return source[match.start():end]


def produce(sources: dict[str, str]) -> tuple[str, list[dict]]:
    require(set(sources) == set(PINS), "exact three-file native inventory required")
    extracted = {}
    receipt = []
    for label, path, anchor, is_struct in SLICES:
        block = extract_literal(sources[path], anchor, label, is_struct)
        extracted[label] = block
        receipt.append({
            "label": label,
            "source": path,
            "sha256": hashlib.sha256(block.encode("utf8")).hexdigest(),
            "bytes": len(block.encode("utf8")),
        })
    # Only namespace wrappers and comments are introduced around exact bodies.
    # Every extracted body is returned unmodified, including whitespace.
    compiled = (
        "// GENERATED FROM EXACT GIT OBJECTS; NEVER A UNITY PRODUCTION SOURCE\n"
        "namespace il2cpp { namespace vm {\n"
        + extracted["assemblyBatch"] + "\n"
        "namespace {\n"
        + "\n".join(extracted[n] for n in (
            "usageAcquire", "usageRelease", "usedClosure", "publicationContext",
            "beginPublication", "publishActive"))
        + "\n} // anonymous native shadow callbacks\n"
        "} } // il2cpp::vm\n"
        "namespace {\n"
        + "\n".join(extracted[n] for n in (
            "metadataContext", "metadataBegin", "metadataRegistries"))
        + "\n} // global anonymous native metadata callbacks\n"
        + extracted["metadataBatch"] + "\n"
    )
    return compiled, receipt


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--receipt", required=True, type=Path)
    a = p.parse_args()
    try:
        sources = read_pinned(a.native_root.resolve(strict=True), NATIVE_COMMIT, PINS)
        code, chunks = produce(sources)
        require(a.output.name == "NativeRegistryExactBodies.inc",
                "explicit source-host output name required")
        require(a.output.parent.is_dir() and a.receipt.parent.is_dir(),
                "output and receipt parent directories must exist")
        a.output.write_text(code, encoding="utf8")
        evidence = {
            "schema": "R03B2ExactNativeRegistryExceptionalHostV1",
            "result": "PinnedNativeBodiesExtractedOnly",
            "branch": BRANCH,
            "nativeCommit": NATIVE_COMMIT,
            "sourceBlobs": PINS,
            "bodyCount": len(chunks),
            "bodies": chunks,
            "generatedSha256": hashlib.sha256(code.encode("utf8")).hexdigest(),
            "compiledActualNativeBodyRequired": True,
            "unityVmDependenciesMocked": True,
            "nativeProductionModified": False,
            "realUnity": False,
            "fullNativeExceptionSafetyProven": False,
            "safeRegistryRollbackAfterExceptionProven": False,
            "R03Accepted": False,
            "H2Passed": False,
            "ReadyForHumanReviewGate": False,
            "handoffAuthority": "CLOSED_NO_LOCAL_EXECUTION",
        }
        a.receipt.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                             encoding="utf8")
        print(json.dumps({
            "result": evidence["result"],
            "bodyCount": len(chunks),
            "generatedSha256": evidence["generatedSha256"],
            "realUnity": False,
        }, sort_keys=True))
        return 0
    except (OSError, SourceMismatch, subprocess.TimeoutExpired) as error:
        print("ExactNativeRegistryHostRejected: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
