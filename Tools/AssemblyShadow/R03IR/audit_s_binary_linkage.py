#!/usr/bin/env python3
"""Read-only original S generated registration -> archived GameAssembly audit.

This validates original Git/index bytes, actual C++ registration fields, and
bounded nm output for both archived macOS binaries. It does not reconstruct
compiler invocation, object files, linker input closure or Player execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ORIGINAL = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
PREFIX = "Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch"
INDEX_SHA = "0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70"
M07 = "projects/resource-complete/Builds/AssemblyShadow/M07"
ROLES = {
    "NativeOn": ("M07-Baseline-R03Completion-29bb3d4a39bf_BackUpThisFolder_ButDontShipItWithYourGame",
                 "M07-Baseline-R03Completion-29bb3d4a39bf.app"),
    "NativeOff": ("M07-Baseline-R03Completion-29bb3d4a39bf-NativeOff_BackUpThisFolder_ButDontShipItWithYourGame",
                  "M07-Baseline-R03Completion-29bb3d4a39bf-NativeOff.app"),
}
SOURCES = {
    "Il2CppGenericMethodPointerTable.c": ("bf86c8ee7dffe81a23c0b21ccbdc37e7374d414c",
        "197debac4e5ea493126785b48703f19d0b842caa1bab0ed83d19196d73ac59b6", 11350766),
    "Il2CppInvokerTable.cpp": ("c5a9c6bb34b7a48c000e7c2f16f1b5d4844a4f86",
        "fc7a707baf8be8f23061b5362f29f6c2c3e0e52d607add49de1833c1f21c8c03", 8465159),
}
MACHO_BLOBS = {"NativeOn": ("f5e3f19b6a6e47b2b8fc8f7dab6f032513be7439", 98041110),
               "NativeOff": ("4b59b2b09c44cfb7676721a87817e2aee0c9ec1e", 96480726)}
TABLES = {"g_Il2CppGenericMethodPointers": 48232, "g_Il2CppInvokerPointers": 10198}
DECLARATIONS = {"g_Il2CppGenericMethodPointers": "Il2CppMethodPointer",
                "g_Il2CppInvokerPointers": "InvokerMethod"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    d = {}
    for key, value in pairs:
        require(key not in d, "Duplicate JSON key: " + key)
        d[key] = value
    return d


def sha256_file(file):
    digest = hashlib.sha256()
    with Path(file).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_file(path):
    path = Path(path)
    digest = hashlib.sha1(("blob %d\0" % path.stat().st_size).encode())
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def original_entry(checkpoint, indexed, repo, rel, blob=None, size=None, sha=None):
    path = checkpoint / rel
    require(path.is_file() and not path.is_symlink() and
            path.resolve().is_relative_to(checkpoint.resolve()), "Missing/nonregular original: " + rel)
    length = path.stat().st_size
    require(size is None or length == size, "Original archived file size drift: " + rel)
    actual_sha = sha256_file(path)
    actual_blob = git_blob_file(path)
    require(sha is None or actual_sha == sha, "Original archived SHA-256 drift: " + rel)
    require(blob is None or actual_blob == blob, "Original archived Git blob drift: " + rel)
    require(rel in indexed and type(indexed[rel]) is dict and
            type(indexed[rel].get("size")) is int and indexed[rel]["size"] == length and
            indexed[rel].get("sha256") == actual_sha,
            "Archived indexed original file does not match: " + rel)
    git_path = PREFIX + "/" + rel
    entries = git(repo, "ls-tree", "-z", ORIGINAL, "--", git_path).split(b"\0")
    require(len(entries) == 2 and entries[0], "Expected exactly one original Git tree file")
    props, name = entries[0].split(b"\t", 1)
    mode, kind, oid = props.split()
    required_mode = b"100755" if rel.endswith("/GameAssembly.dylib") else b"100644"
    require(mode == required_mode and kind == b"blob" and
            name.decode() == git_path and oid.decode() == actual_blob,
            "Original file Git path/blob authentication failed: " + rel)
    return {"path": rel, "bytes": length, "sha256": actual_sha, "gitBlob": actual_blob}


def registration_symbols(code):
    """Parse the exact registration initializer, not arbitrary string mentions."""
    text = code.decode("utf-8-sig", "strict")
    m = re.search(r"\bconst\s+Il2CppCodeRegistration\s+g_CodeRegistration\s*=\s*\{(.*?)\};",
                  text, re.S)
    require(m is not None, "Original generated C++ code registration initializer missing")
    fields = [part.strip() for part in m.group(1).split(",") if part.strip()]
    require(len(fields) == 17, "Unexpected registered IL2CPP code registration field count")
    require(fields[0] == "2" and fields[1] == "g_ReversePInvokeWrapperPointers" and
            fields[2] == "48232" and fields[3] == "g_Il2CppGenericMethodPointers" and
            fields[5] == "10198" and fields[6] == "g_Il2CppInvokerPointers",
            "Exact original generated table references/counts changed")
    for symbol, typename in DECLARATIONS.items():
        declaration = (r"\bIL2CPP_EXTERN_C\s+const\s+" + re.escape(typename) + r"\s+" +
                       re.escape(symbol) + r"\s*\[\s*\]")
        require(len(re.findall(declaration, text)) == 1, "Exactly one external registration declaration: " + symbol)
    require("il2cpp_codegen_register (&g_CodeRegistration, &g_MetadataRegistration" in text,
            "Original generated registration call must reference live code table")
    return {"registrationFields": fields, "genericCount": int(fields[2]),
            "invokerCount": int(fields[5]),
            "referencedSymbols": sorted(TABLES),
            "registrationCall": "il2cpp_codegen_register",
            "sourceRegistrationContract": "PassedExactFieldsAndExternalSymbols"}


def classify_nm_symbols(lines):
    """Require exact named, defined Mach-O symbols; undefined references cannot pass."""
    definitions = {name: [] for name in TABLES}
    for line in lines:
        item = line.strip()
        for name in TABLES:
            if re.search(r"(?:^|\\s)_" + re.escape(name) + r"$", item) and
                    re.match(r"^[0-9a-fA-F]{8,16}\\s+\\([^)]+\\)\\s+", item) and
                    "undefined" not in item.lower():
                definitions[name].append(item[:250])
    return {"definedSymbols": definitions,
            "allRequiredSymbolsDefined": all(len(v) == 1 for v in definitions.values())}


def bounded_nm(binary):
    """Inspect archived Mach-O symbols without equating symbols to source-object identity."""
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as output:
        try:
            result = subprocess.run(["nm", "-m", str(binary)], stdout=output,
                                    stderr=subprocess.PIPE, text=True, timeout=110, check=False)
            output.seek(0)
            scanned = 0
            matches = {name: [] for name in TABLES}
            for line in output:
                scanned += 1
                for name in TABLES:
                    if name in line and len(matches[name]) < 12:
                        matches[name].append(line.strip()[:250])
            stderr = (result.stderr or "")[:2000]
            defined = classify_nm_symbols(line for group in matches.values() for line in group)
            return {"tool": "nm -m", "returnCode": result.returncode,
                    **defined,
                    "linesExamined": scanned, "boundedMatches": matches,
                    "stderrPrefix": stderr,
                    "symbolPresence": {name: bool(matches[name]) for name in TABLES},
                    "objectFileIdentityProven": False,
                    "exactSourceBytesInBinaryProven": False}
        except (OSError, subprocess.TimeoutExpired) as error:
            return {"tool": "nm -m", "result": "Unavailable",
                    "reason": str(error)[:500],
                    "symbolPresence": {name: False for name in TABLES},
                    "objectFileIdentityProven": False,
                    "exactSourceBytesInBinaryProven": False}


def audit(original):
    original = Path(original).resolve()
    require((original / ".git").exists() and
            git(original, "rev-parse", "HEAD").decode().strip() == ORIGINAL and
            not git(original, "status", "--porcelain"), "Exact clean original S repository required")
    checkpoint = original / PREFIX
    idx = checkpoint / "evidence-index.json"
    require(idx.is_file() and not idx.is_symlink() and sha256_file(idx) == INDEX_SHA,
            "Original S index SHA-256 mismatch")
    index = json.loads(idx.read_text(encoding="utf-8"), object_pairs_hook=unique,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    require(type(index) is dict and type(index.get("files")) is list and
            len(index["files"]) == 15712, "Exact original S archive index")
    indexed = {}
    for row in index["files"]:
        require(type(row) is dict and type(row.get("path")) is str and
                row["path"] not in indexed, "Exact unique indexed S path")
        indexed[row["path"]] = row
    rows = []
    for role, (generated_folder, app_folder) in ROLES.items():
        root = "/".join((M07, generated_folder, "il2cppOutput"))
        source_rows = []
        for basename, (blob, sha, size) in SOURCES.items():
            source_rows.append(original_entry(checkpoint, indexed, original,
                                               root + "/" + basename, blob, size, sha))
        registration_path = root + "/Il2CppCodeRegistration.cpp"
        registration = original_entry(checkpoint, indexed, original, registration_path)
        source_bytes = (checkpoint / registration_path).read_bytes()
        registration["validatedFields"] = registration_symbols(source_bytes)
        binary_blob, binary_size = MACHO_BLOBS[role]
        binary = original_entry(checkpoint, indexed, original, "/".join((M07, app_folder,
            "Contents/Frameworks/GameAssembly.dylib")), binary_blob, binary_size)
        binary["nativeSymbolInspection"] = bounded_nm(checkpoint / binary["path"])
        require(binary["nativeSymbolInspection"].get("returnCode") == 0 and
                binary["nativeSymbolInspection"].get("allRequiredSymbolsDefined") is True,
                "Original Mach-O must physically define both exact generated table symbols")
        rows.append({"role": role, "generatedSources": source_rows,
                     "sourceRegistration": registration, "archivedGameAssembly": binary})
    require(rows[0]["generatedSources"][0]["sha256"] == rows[1]["generatedSources"][0]["sha256"] and
            rows[0]["generatedSources"][1]["sha256"] == rows[1]["generatedSources"][1]["sha256"],
            "Original native ON/OFF generated tables must have identical source bytes")
    require(rows[0]["sourceRegistration"]["validatedFields"] ==
            rows[1]["sourceRegistration"]["validatedFields"],
            "Original native ON/OFF code registration count/refs must agree")
    require(not git(original, "status", "--porcelain"), "Original S checkout changed during read-only audit")
    return {"schemaVersion": 1, "kind": "R03OriginalSCodeRegistrationAndMachOLinkageReadOnly",
            "result": "PassedArchivedSourceRegistrationBinaryIdentity_NotFullLinkage",
            "originalPublication": ORIGINAL, "originalIndexSha256": INDEX_SHA,
            "originalIndexMembers": len(indexed), "roles": rows,
            "sourceRegistrationLinkedByText": True,
            "twoNamedTableDefinitionsInEachOriginalMachO": True,
            "originalCompiledObjectCommandGraph": "NotProven",
            "actualGeneratedSourceObjectIdentity": "NotProven",
            "fullNativeBinaryLinkage": "NotProven",
            "executedPlayerCodeMapping": "NotProven",
            "independentReviewer": False, "unityRun": False,
            "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
            "ReadyForHumanReviewGate": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    original, output = Path(args.original).resolve(), Path(args.output).resolve()
    require(not output.exists() and not output.is_relative_to(original),
            "External unused immutable output destination required")
    record = audit(original)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as file:
        json.dump(record, file, indent=2, sort_keys=True, allow_nan=False)
        file.write("\n")
    print(json.dumps({"result": record["result"], "originalRoles": len(record["roles"]),
        "nativeBinaryLinkage": "NotProven", "newPlayerRun": False}, sort_keys=True))


if __name__ == "__main__":
    main()
