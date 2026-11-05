#!/usr/bin/env python3
"""Read-only original S generated-source identity and lexical audit.

A bounded textual scan is NOT semantic C++ AST inspection or proof of
compiler inputs, linked executable, Unity execution, or R03 acceptance.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ORIGINAL = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
CHECKPOINT = "Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch"
INDEX_SHA = "0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70"
PREFIX = "projects/resource-complete/Builds/AssemblyShadow/M07"
ROLES = {
    "NativeOff": "M07-Baseline-R03Completion-29bb3d4a39bf-NativeOff_BackUpThisFolder_ButDontShipItWithYourGame",
    "NativeOn": "M07-Baseline-R03Completion-29bb3d4a39bf_BackUpThisFolder_ButDontShipItWithYourGame",
}
FILES = {
    "Il2CppGenericMethodPointerTable.c": ("bf86c8ee7dffe81a23c0b21ccbdc37e7374d414c",
        "197debac4e5ea493126785b48703f19d0b842caa1bab0ed83d19196d73ac59b6", 11350766, 96487),
    "Il2CppInvokerTable.cpp": ("c5a9c6bb34b7a48c000e7c2f16f1b5d4844a4f86",
        "fc7a707baf8be8f23061b5362f29f6c2c3e0e52d607add49de1833c1f21c8c03", 8465159, 91940),
}
MARKERS = {
    "methodPointer": re.compile(r"\bIl2CppMethodPointer\b"),
    "invoker": re.compile(r"\b(?:InvokerMethod|Invoker)\b", re.I),
    "generic": re.compile(r"\bGenericMethod\b", re.I),
    "externC": re.compile(r"\bIL2CPP_EXTERN_C\b"),
    "include": re.compile(r"^\s*#\s*include\b"),
    "conditional": re.compile(r"^\s*#\s*(?:if|ifdef|ifndef|elif|else|endif)\b"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def no_duplicates(items):
    result = {}
    for k, v in items:
        require(k not in result, "Duplicate JSON key: " + k)
        result[k] = v
    return result


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(("blob %d\0" % len(raw)).encode() + raw).hexdigest()


def scan(raw):
    """Literal line markers only, never inferred compiler or VM semantics."""
    require(type(raw) is bytes and raw and b"\0" not in raw, "Nonempty text input without NUL required")
    lines = raw.decode("utf-8", "strict").splitlines(keepends=True)
    counts = {k: 0 for k in MARKERS}
    summaries = {k: hashlib.sha256() for k in MARKERS}
    samples = {k: [] for k in MARKERS}
    for number, line in enumerate(lines, 1):
        for name, pattern in MARKERS.items():
            if pattern.search(line):
                counts[name] += 1
                summaries[name].update(line.encode("utf-8"))
                if len(samples[name]) < 8:
                    samples[name].append({"line": number,
                        "lineSha256": sha256(line.encode("utf-8")),
                        "prefix": line.strip()[:140]})
    return {"lines": len(lines), "counts": counts,
        "lineFingerprints": {n: h.hexdigest() for n, h in summaries.items()},
        "samples": samples, "semanticCxxAstReviewed": False,
        "compiledObjectBound": False, "linkedPlayerBound": False}


def audit(root):
    root = Path(root).resolve()
    require((root / ".git").exists(), "Original S Git checkout required")
    require(git(root, "rev-parse", "HEAD").decode().strip() == ORIGINAL,
            "Exact immutable original S commit required")
    require(not git(root, "status", "--porcelain"), "Original S checkout must be clean")
    checkpoint = root / CHECKPOINT
    idx = checkpoint / "evidence-index.json"
    require(idx.is_file() and not idx.is_symlink(), "Original S archive index required")
    data = idx.read_bytes()
    require(sha256(data) == INDEX_SHA, "Original S archive index hash mismatch")
    index = json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates,
        parse_constant=lambda v: (_ for _ in ()).throw(ValueError("Nonfinite JSON: " + v)))
    require(type(index) is dict and type(index.get("files")) is list and
            len(index["files"]) == 15712, "Original S archive index cardinality")
    lookup = {}
    for row in index["files"]:
        require(type(row) is dict and type(row.get("path")) is str and
                row["path"] not in lookup, "Unique original S archive member path")
        lookup[row["path"]] = row
    rows = []
    for basename, (oid, sha, size, line_count) in sorted(FILES.items()):
        for role, folder in ROLES.items():
            relative = "/".join((PREFIX, folder, "il2cppOutput", basename))
            f = checkpoint / relative
            require(f.is_file() and not f.is_symlink() and
                    f.resolve().is_relative_to(checkpoint.resolve()),
                    "Missing/symlink original source: " + relative)
            raw = f.read_bytes()
            require(len(raw) == size and sha256(raw) == sha and git_blob(raw) == oid,
                    "Exact original source identity failed: " + relative)
            require(relative in lookup and type(lookup[relative].get("size")) is int and
                    lookup[relative]["size"] == size and lookup[relative].get("sha256") == sha,
                    "Original evidence-index/source mismatch: " + relative)
            path = CHECKPOINT + "/" + relative
            tree = git(root, "ls-tree", "-z", ORIGINAL, "--", path).split(b"\0")
            require(len(tree) == 2 and tree[0], "Exactly one original tree entry required")
            attrs, name = tree[0].split(b"\t")
            mode, kind, found = attrs.split()
            require(mode == b"100644" and kind == b"blob" and
                    found.decode() == oid and name.decode() == path,
                    "Original source path Git tree/blob mismatch")
            lexical = scan(raw)
            require(lexical["lines"] == line_count, "Original generated source line-count drift")
            rows.append({"role": role, "relativePath": relative, "gitBlob": oid,
                "sha256": sha, "bytes": size, "lexicalScan": lexical})
    for basename in FILES:
        pair = [row for row in rows if row["relativePath"].endswith("/" + basename)]
        require(len(pair) == 2 and pair[0]["lexicalScan"] == pair[1]["lexicalScan"],
                "ON/OFF original generated-source content differs")
    require(not git(root, "status", "--porcelain"), "Audit modified original S checkout")
    return {"schemaVersion": 1, "kind": "R03OriginalSGeneratedMaterialReadOnlyScan",
        "result": "PassedIdentityAndLexicalScanOnly", "originalPublication": ORIGINAL,
        "originalIndexSha256": INDEX_SHA, "originalIndexMembers": len(lookup),
        "sourceOccurrences": rows, "uniqueSourceBlobs": 2,
        "onOffSourceBytesIdentical": True, "sourceToObjectBuildJoin": "NotProven",
        "generatedCppBinaryLinkage": "NotProven",
        "originalCaptureOmissionsFullReconciliation": "NotRun",
        "fullCxxSemanticInspection": False, "independentReviewer": False,
        "unityRun": False, "runtimeAcceptance": False,
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    original, output = Path(args.original).resolve(), Path(args.output).resolve()
    require(not output.exists() and not output.is_relative_to(original),
            "Unused output outside original S checkout required")
    result = audit(original)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as file:
        json.dump(result, file, indent=2, sort_keys=True, allow_nan=False)
        file.write("\n")
    print(json.dumps({"result": result["result"], "sourceOccurrences": 4,
                      "fullCxxSemanticInspection": False, "generatedCppBinaryLinkage": "NotProven"}))


if __name__ == "__main__":
    main()
