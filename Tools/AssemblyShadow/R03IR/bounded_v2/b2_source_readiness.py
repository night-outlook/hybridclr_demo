"""Read-only R03 B2 source-admission audit.

A successful audit is a VERIFIED BLOCK, not readiness to emit field14/15.
The original V2 slots contain complete final general/execution diagnostics,
not the existing frozen B1 first error. No Unity/VM action is performed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

NATIVE = {
    "libil2cpp/vm/AssemblyShadow.cpp": "4ab5b6257d300bb796579c32e54f6a16c822c21c",
    "libil2cpp/vm/AssemblyShadow.h": "538312675c99c97ffa73072aac78bd6aefedd49e",
    "libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl": "a85a6ec310b85e96dfe199c6d773407cf47779b3",
    "libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl": "94bcd4e12e553c2f28c727d9c74bc2feb0b22e8c",
    "libil2cpp/vm/AssemblyShadowTypeKey.cpp": "6b23b4bad66e9a8f36c68717ef82626351018624",
    "libil2cpp/vm/AssemblyShadowMetadataLifetime.h": "d2fe09dd51debbbbc71d67b21347f5d971a3cafd",
    "libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h": "eeb413f8c8c0f6c1658da68ddd404b9b478e6e70",
    "libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl": "4e66890239ff40f0c073cc8b379c6a5f54bb1fa3",
}
REFERENCE = "Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py"
REFERENCE_BLOB = "0866b07f758a20284d2a5d5d933b2be577b20b50"
NATIVE_PIN = "8aa8d09319a89b55b2496bcc2c69ccc69cb57be9"

class SourceAdmissionError(RuntimeError):
    pass

def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SourceAdmissionError(detail)

def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args],
                            capture_output=True, text=True, timeout=30)
    require(result.returncode == 0, "Git identity failure: " + " ".join(args))
    return result.stdout.strip()

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def read_pinned(root: Path, path: str, blob: str) -> str:
    f = root / path
    require(f.is_file() and not f.is_symlink(), "Missing/aliased source: " + path)
    require(f.resolve() == root / path, "Noncanonical source: " + path)
    raw = f.read_bytes()
    require(git_blob(raw) == blob, "Unreviewed source content: " + path)
    object_line = run_git(root, "ls-tree", "HEAD", "--", path)
    require(object_line == "100644 blob " + blob + "\t" + path,
            "Git tree/source mismatch: " + path)
    return raw.decode("utf-8", "strict")

def schema(text: str) -> tuple[str, str]:
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "FIELDS" for t in node.targets
        ):
            value = ast.literal_eval(node.value)
            require(type(value) is tuple and
                    value == ("finalDiagnostics", "finalExecutionDiagnostics"),
                    "Original field14/15 schema changed; independent review required")
            return value
    raise SourceAdmissionError("Original V2 FIELDS declaration missing")

def assess(sources: dict[str, str], reference: str) -> dict:
    fields = schema(reference)
    def has(path: str, *tokens: str) -> None:
        require(path in sources, "Required actual native source absent: " + path)
        for token in tokens:
            require(token in sources[path],
                    "B2 source boundary changed without review: " + path + ": " + token)
    head = "libil2cpp/vm/"
    has(head + "AssemblyShadow.h",
        "TryCaptureBoundedGeneralLive", "TryCaptureBoundedEmptyExecutionLive",
        "TryReadFirstFailureV2")
    has(head + "AssemblyShadow.cpp",
        "AssemblyShadow::GetDiagnosticsJson", "ShadowDiagnosticSnapshot snapshot",
        "AssemblyShadow::GetExecutionDiagnosticsJson", "std::ostringstream output",
        "FormatMetadataOnly")
    has(head + "AssemblyShadowBoundedGeneralLiveSource.inl",
        "AssemblyShadow::TryCaptureBoundedGeneralLive",
        "assembly_shadow_metadata_lifetime::Gate::Reader reader",
        "receipt.componentSourcesComplete=true",
        "receipt.observableSourceFenceStable=true",
        "not an atomic all-VM epoch")
    has(head + "AssemblyShadowBoundedExecutionEmptyLiveSource.inl",
        "AssemblyShadow::TryCaptureBoundedEmptyExecutionLive",
        "if(before.count!=0)",
        "live::Error::ClassRowsNotSupported",
        "assembly_shadow_metadata_lifetime::Gate::Reader admission")
    has(head + "AssemblyShadowTypeKey.cpp",
        "std::string FormatType(", "MetadataDefinitionKey(", "std::string value",
        "AssemblyShadowTypeKey::FormatMetadataOnly")
    has(head + "AssemblyShadowMetadataLifetime.h",
        "sourceEpoch", "initial admitted session", "class Gate final")
    has(head + "AssemblyShadowFrozenExecutionRecord.h",
        "class Record final", "size_t Bytes() const noexcept",
        "bool Complete() const noexcept", "RejectInvalidSource()")
    has(head + "AssemblyShadowOwnedPhysicalNamesSource.inl",
        "namesCopiedFromMatchedEnumeratorCallbacks=true",
        "not an execution TypeKey")

    # Never equate a structurally verified, partially supported source with
    # an accepted V2 producer. Removing a rejection branch requires review.
    return {
        "schemaVersion": 1,
        "kind": "R03B2ExactVMSourceReadinessAudit",
        "sourceAudit": "PassedPinnedStructuralInspection",
        "field14": fields[0],
        "field15": fields[1],
        "generalStatus": "BoundedComponentFence_NotWholeVmOrTerminalSource",
        "executionStatus": "ZeroClassSubsetOnly_NonemptyClassUnsupported",
        "typeKeyStatus": "LegacyMetadataOnlyAllocationful_NoBoundedCanonicalRows",
        "wholeVmEpoch": "NotProven",
        "readyForNativeV2FieldCapture": False,
        "nativeV2TransportImplemented": False,
        "runtimeAcceptance": False,
        "R03Accepted": False,
        "H2Passed": False,
        "ReadyForHumanReviewGate": False,
        "blockers": [
            "B2-SRC-01: no complete bounded postterminal field14 and nonempty field15 source",
            "B2-SRC-03: canonical class TypeKeys/metadata lifetime and whole-VM epoch not proven",
            "B2-SRC-04: no integrated independently authenticated native V2 producer/receipt",
        ],
    }

def inspect(demo: Path, native: Path, expected_demo: str, expected_native: str) -> dict:
    demo = demo.resolve(strict=True)
    native = native.resolve(strict=True)
    require(demo != native and not (demo in native.parents or native in demo.parents),
            "Independent repositories required")
    require(run_git(demo, "rev-parse", "HEAD") == expected_demo,
            "Wrong exact demo commit")
    require(expected_native == NATIVE_PIN and
            run_git(native, "rev-parse", "HEAD") == expected_native,
            "Wrong exact native commit")
    require(not run_git(demo, "status", "--porcelain", "--untracked-files=no"),
            "Demo working tree changed")
    require(not run_git(native, "status", "--porcelain", "--untracked-files=no"),
            "Native working tree changed")
    actual = {p: read_pinned(native, p, blob) for p, blob in NATIVE.items()}
    original = read_pinned(demo, REFERENCE, REFERENCE_BLOB)
    result = assess(actual, original)
    result["repositoryPins"] = {"hybridclr_demo": expected_demo, "il2cpp_plus": expected_native}
    result["verifiedNativeFiles"] = len(actual)
    result["verifiedReferenceBlob"] = REFERENCE_BLOB
    result["handoffAuthority"] = "CLOSED_NO_LOCAL_EXECUTION"
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--expected-demo", required=True)
    parser.add_argument("--expected-native", required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.demo, args.native, args.expected_demo, args.expected_native)
    except (SourceAdmissionError, UnicodeError, OSError, ValueError) as error:
        print(json.dumps({"sourceAudit": "Rejected", "reason": str(error),
                          "readyForNativeV2FieldCapture": False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
