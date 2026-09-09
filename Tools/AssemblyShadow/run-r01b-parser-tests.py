#!/usr/bin/env python3
"""Run the R01B RawImage corpus and bounded BlobReader probes immutably."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def snapshot(paths: set[Path]) -> dict[str, str]:
    return {str(path): digest(path) for path in sorted(paths)}


def run(receipt: dict, argv: list[Path | str], cwd: Path, phase: str,
        env: dict[str, str] | None = None) -> tuple[str, str]:
    record = {"phase": phase, "argv": [str(value) for value in argv], "cwd": str(cwd)}
    if env:
        record["environmentOverrides"] = env
    receipt["commands"].append(record)
    result = subprocess.run([str(value) for value in argv], cwd=cwd,
                            env={**os.environ, **env} if env else None,
                            capture_output=True, text=True, errors="replace", check=False)
    record.update(exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    if result.returncode:
        raise RuntimeError(f"{phase} failed ({result.returncode}): {result.stderr.strip()}")
    return result.stdout, result.stderr


def dep_paths(output: str) -> set[Path]:
    text = output.replace("\\\n", " ")
    if ": " not in text:
        raise RuntimeError("compiler dependency output has no target rule")
    return {Path(item).resolve(strict=True) for item in shlex.split(text.split(": ", 1)[1])}


def verify_corpus(corpus: Path, manifest: dict) -> list[dict]:
    assemblies = manifest.get("assemblies", [])
    totals = manifest.get("totals", {})
    if len(assemblies) != 8192 or totals.get("assemblyCount") != 8192:
        raise RuntimeError("workload-v2 manifest is not the complete 8192 corpus")
    verified = []
    for entry in assemblies:
        path = (corpus / entry["file"]).resolve(strict=True)
        if path.parent != corpus.resolve() or path.is_symlink():
            raise RuntimeError(f"fixture path identity mismatch: {path}")
        if path.stat().st_size != entry["sizeBytes"] or digest(path) != entry["sha256"]:
            raise RuntimeError(f"fixture hash or size mismatch: {path}")
        verified.append({"id": entry["id"], "path": str(path),
                         "sizeBytes": entry["sizeBytes"], "sha256": entry["sha256"]})
    return verified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--installed-root", type=Path)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    demo = here.parents[1]
    native = demo.parent / "hybridclr"
    runtime = demo.parent / "il2cpp_plus"
    installed = (args.installed_root or
                 demo.parent.parent / "assembly_shadow_r01/hybridclr_demo/"
                 "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp").resolve()
    external = installed.parent / "external"
    corpus_dir = demo / "_temp/AssemblyShadow/R01B/workload-v2-corpus-512MiB-8192"
    corpus_manifest = corpus_dir / "workload-v2-manifest.json"
    dense_manifest = demo / "_temp/AssemblyShadow/R01B/workload-v3-dense-adjunct.json"
    full_harness = here / "native-tests/r01b-parser-full.cpp"
    dense_harness = here / "native-tests/r01b-parser-dense.cpp"
    fix_harness = here / "native-tests/r01b-parser-bounds.cpp"
    index_adapter = here / "native-tests/r01b-parser-index-adapter.cpp"
    compiler = Path(shutil.which("clang++") or "").resolve(strict=True)
    version_header = installed / "libil2cpp/hybridclr/generated/UnityVersion.h"
    if not version_header.exists():
        version_header = installed / "hybridclr/generated/UnityVersion.h"

    output_root = args.output_root.resolve()
    receipt_path = output_root / "r01b-parser-receipt.json"
    receipt = {"schemaVersion": 1, "kind": "R01BParserReconciledReader",
               "success": False, "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "commands": []}
    try:
        if output_root.exists():
            raise RuntimeError(f"refusing to overwrite output root: {output_root}")
        required = [corpus_dir, corpus_manifest, dense_manifest, full_harness,
                    dense_harness, fix_harness, index_adapter, version_header,
                    native / "hybridclr/metadata/BlobReader.h",
                    native / "hybridclr/metadata/BlobReaderBounds.h",
                    native / "hybridclr/metadata/RawImageBase.h",
                    native / "hybridclr/metadata/RawImageBase.cpp",
                    native / "hybridclr/metadata/RawImage.cpp",
                    native / "hybridclr/metadata/MetadataUtil.h",
                    native / "hybridclr/metadata/MetadataUtil.cpp"]
        for path in required:
            if not path.exists():
                raise RuntimeError(f"missing input: {path}")
        output_root.mkdir(parents=True)
        run_dir = output_root / "run"
        run_dir.mkdir()
        full_manifest_data = json.loads(corpus_manifest.read_text(encoding="utf-8"))
        dense_manifest_data = json.loads(dense_manifest.read_text(encoding="utf-8"))
        verified_corpus = verify_corpus(corpus_dir, full_manifest_data)
        fixtures = dense_manifest_data.get("fixtures", [])
        if len(fixtures) != 2 or dense_manifest_data.get("status") != "VerifiedSealedV1FixturesOutsideV2Envelope":
            raise RuntimeError("dense adjunct is not the sealed two-fixture manifest")
        dense_inputs = []
        for fixture in fixtures:
            path = Path(fixture["path"]).resolve(strict=True)
            if path.is_symlink() or path.stat().st_size != fixture["sizeBytes"] or digest(path) != fixture["sha256"]:
                raise RuntimeError(f"dense fixture identity, size, or hash mismatch: {path}")
            if fixture["typeDefRows"] != 4098 or fixture["methodDefRows"] != 4097 or fixture["stringsHeapBytes"] != 286888:
                raise RuntimeError(f"dense dimensions mismatch: {path}")
            dense_inputs.append({"id": fixture["id"], "path": str(path),
                                 "sizeBytes": fixture["sizeBytes"], "sha256": fixture["sha256"]})

        base_flags: list[Path | str] = ["-std=c++11", "-O1", "-g", "-fno-omit-frame-pointer",
            "-ffunction-sections", "-fdata-sections",
            "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib", "-I", runtime / "libil2cpp",
            "-I", native / "hybridclr", "-I", native,
            "-isystem", external / "baselib/Include",
            "-isystem", external / "baselib/Platforms/OSX/Include",
            "-iquote", installed / "utils", "-include", version_header]
        parser_flags = base_flags + ["-DIL2CPP_DEBUG=1", "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"]
        fix_flags = base_flags + ["-DIL2CPP_DEBUG=0", "-DIL2CPP_ENABLE_ASSERTIONS=0",
                                  "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"]
        sanitizer = ["-fsanitize=address,undefined"]
        production = [native / "hybridclr/metadata/RawImage.cpp",
                      native / "hybridclr/metadata/RawImageBase.cpp",
                      native / "hybridclr/metadata/MetadataUtil.cpp"]
        runtime_source = native / "hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp"
        production_objects = [("raw", production[0]), ("base", production[1]),
                              ("util", production[2]), ("index-runtime", runtime_source),
                              ("index-adapter", index_adapter)]
        source_targets = [full_harness, dense_harness, fix_harness, index_adapter, *production,
                          runtime_source,
                          native / "hybridclr/metadata/BlobReader.h",
                          native / "hybridclr/metadata/BlobReaderBounds.h",
                          native / "hybridclr/metadata/RawImageBase.h",
                          native / "hybridclr/metadata/MetadataUtil.h",
                          native / "hybridclr/metadata/InterpreterMetadataIndexRuntime.h", compiler, version_header]
        receipt.update(platform=platform.platform(), architecture=platform.machine(),
                       sourceRoots={"demo": str(demo), "hybridclr": str(native), "il2cppPlus": str(runtime)},
                       sourceTargets=[str(path) for path in source_targets],
                       compiler={"path": str(compiler), "sha256": digest(compiler)},
                       installedHeaderFallback={"external": True, "hashBound": True,
                                                "root": str(installed), "externalRoot": str(external),
                                                "unityVersionHeader": str(version_header),
                                                "unityVersionHeaderSha256": digest(version_header)},
                       flags={"parser": [str(v) for v in parser_flags],
                              "boundedFix": [str(v) for v in fix_flags],
                              "sanitizer": sanitizer},
                       inputs={"external": True, "hashBound": True,
                               "corpusManifest": {"path": str(corpus_manifest),
                                                  "sha256": digest(corpus_manifest),
                                                  "totals": full_manifest_data["totals"],
                                                  "verifiedFiles": verified_corpus},
                               "denseManifest": {"path": str(dense_manifest),
                                                 "sha256": digest(dense_manifest),
                                                 "fixtures": dense_inputs}},
                       controlledAdapters=["Memory::Malloc/Calloc/Free", "String/Exception stubs",
                                           "LogPanic", "il2cpp_assert"],
                       linkPolicy="strict -undefined,error with dead_strip; no dynamic lookup")
        run(receipt, [compiler, "--version"], demo, "compiler-version")

        sources = [full_harness, dense_harness, fix_harness, index_adapter, *production, runtime_source]
        dependencies = set(source_targets)
        source_flags = {fix_harness: fix_flags, index_adapter: parser_flags}
        for source in sources:
            flags = source_flags.get(source, parser_flags)
            output, _ = run(receipt, [compiler, *flags, *sanitizer, "-M", "-MT", "r01b_parser", source], native,
                             "dependencies")
            dependencies.update(dep_paths(output))
        receipt["sourceHashesBefore"] = snapshot(dependencies | {here / "run-r01b-parser-tests.py"})

        def build_group(prefix: str, flags: list[Path | str], harnesses: list[tuple[str, Path]]) -> dict[str, Path]:
            objects = {}
            for label, source in [*harnesses, *production_objects]:
                obj = run_dir / f"{prefix}-{label}.o"
                run(receipt, [compiler, *flags, *sanitizer, "-c", source, "-o", obj], native,
                    f"{prefix}-compile-{label}")
                objects[label] = obj
            for label, harness in harnesses:
                binary = run_dir / f"{prefix}-{label}"
                run(receipt, [compiler, *sanitizer, "-fno-omit-frame-pointer", "-Wl,-dead_strip",
                              "-Wl,-undefined,error", objects[label],
                              *(objects[name] for name, _ in production_objects), "-o", binary],
                    native, f"{prefix}-link-{label}")
                objects[f"{label}Binary"] = binary
            return objects

        parser_objects = build_group("parser", parser_flags, [("full", full_harness), ("dense", dense_harness)])
        fix_objects = build_group("bounded", fix_flags, [("fix8", fix_harness)])
        strict_env = {"ASAN_OPTIONS": "halt_on_error=1:abort_on_error=1",
                      "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=0"}
        full_out, full_err = run(receipt, [parser_objects["fullBinary"], corpus_dir, "8192"], native,
                                  "run-full-corpus", strict_env)
        dense_out, dense_err = run(receipt, [parser_objects["denseBinary"], dense_inputs[0]["path"],
                                             dense_inputs[1]["path"]], native, "run-dense-adjunct", strict_env)
        fix_cases = ["valid", "invalid-prefix", "skip-overflow", "skip-wrap", "zero-sentinel",
                     "validate-streams", "raw-entry-truncated", "read16-truncated", "read32-truncated",
                     "read64-truncated", "prefix2-truncated", "prefix4-truncated", "raw-decode-truncated"]
        fix_results = {}
        for case in fix_cases:
            output, error = run(receipt, [fix_objects["fix8Binary"], case], native,
                                 f"run-bounded-{case}", strict_env)
            fix_results[case] = {"stdout": output.strip(), "stderr": error,
                                 "pass": not error and "PASS" in output}
        dependencies_after = set(source_targets)
        for source in sources:
            flags = source_flags.get(source, parser_flags)
            output, _ = run(receipt, [compiler, *flags, *sanitizer, "-M", "-MT", "r01b_parser", source], native,
                             "dependencies-after")
            dependencies_after.update(dep_paths(output))
        source_hashes_after = snapshot(dependencies_after | {here / "run-r01b-parser-tests.py"})
        stable = dependencies == dependencies_after and receipt["sourceHashesBefore"] == source_hashes_after
        full_pass = "raw_image_checks=8192" in full_out and not full_err
        dense_pass = "raw_image_dense_checks=2" in dense_out and not dense_err
        bounded_pass = all(result["pass"] for result in fix_results.values())
        receipt.update(sourceHashesAfter=source_hashes_after,
                       provenanceStable=stable,
                       results={"fullCorpus": full_out.strip(), "fullCorpusStderr": full_err,
                                "denseAdjunct": dense_out.strip(), "denseAdjunctStderr": dense_err,
                                "boundedFix8": fix_results, "fullParserPass": full_pass,
                                "denseParserPass": dense_pass, "boundedReaderPass": bounded_pass,
                                "sanitizerClean": not full_err and not dense_err and
                                all(not value["stderr"] for value in fix_results.values())},
                       artifacts={str(path.relative_to(output_root)): {"sha256": digest(path), "sizeBytes": path.stat().st_size}
                                  for path in sorted(run_dir.iterdir()) if path.is_file()})
        receipt["success"] = stable and full_pass and dense_pass and bounded_pass and receipt["results"]["sanitizerClean"]
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    if output_root.exists():
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt.get(key) for key in ("success", "provenanceStable", "results", "error")}, indent=2))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
