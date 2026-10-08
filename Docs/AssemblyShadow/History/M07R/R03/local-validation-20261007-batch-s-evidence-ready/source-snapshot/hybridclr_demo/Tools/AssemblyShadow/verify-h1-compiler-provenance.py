#!/usr/bin/env python3
"""Strictly verify the four H1 count Player compiler-provenance receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
from pathlib import Path


class VerificationError(ValueError):
    pass


def require(value: object, message: str) -> None:
    if not value:
        raise VerificationError(message)


def sha256(path: Path, *, allow_symlink: bool = False) -> str:
    require(path.is_file() and (allow_symlink or not path.is_symlink()), "Expected regular file: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_file(value: str, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True), label + " is not canonical")
    require(path.is_file() and not path.is_symlink(), label + " is not a regular file")
    return path


def absolute_tool_file(value: str, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path.is_file(), label + " is not an existing absolute file")
    return path


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        require(key not in value, "Duplicate JSON key: " + key)
        value[key] = item
    return value


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=reject_duplicate_keys)
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def project_root_for(receipt_path: Path) -> Path:
    for parent in receipt_path.parents:
        if (parent / "Assets").is_dir() and (parent / "ProjectSettings").is_dir():
            return parent
    raise VerificationError("Cannot derive Unity project root from receipt: " + str(receipt_path))


def resolve_graph_path(project_root: Path, value: str) -> Path:
    require(type(value) is str and value, "Bee graph contains an empty path")
    path = Path(value)
    return Path(os.path.abspath(path if path.is_absolute() else project_root / path))


def action_arguments(action: object) -> list[str]:
    require(type(action) is str and action, "Bee graph action is missing")
    try:
        result = shlex.split(action, posix=True)
    except ValueError as error:
        raise VerificationError("Bee graph action cannot be parsed: " + str(error)) from error
    require(result, "Bee graph action has no executable")
    return result


def option_value(arguments: list[str], option: str) -> str:
    positions = [index for index, value in enumerate(arguments) if value == option]
    require(len(positions) == 1 and positions[0] + 1 < len(arguments),
            "Bee action must contain exactly one " + option)
    return arguments[positions[0] + 1]


def header_default(config: str, name: str) -> str:
    match = re.search(r"(?m)^\s*#\s*ifndef\s+" + re.escape(name) +
                      r"\s*$\s*^\s*#\s*define\s+" + re.escape(name) + r"\s+([^\s/]+)", config)
    require(match is not None, "IL2CPP configuration default is missing: " + name)
    return match.group(1)


def derive_graph_evidence(graph: dict, project_root: Path, native_library_path: Path,
                          config: str) -> dict:
    nodes = graph.get("Nodes")
    require(type(nodes) is list and nodes, "Bee graph Nodes inventory is missing")
    compile_nodes = [node for node in nodes if type(node) is dict and
                     str(node.get("Annotation", "")).startswith("C_Mac_arm64") and node.get("Action")]
    link_nodes = [node for node in nodes if type(node) is dict and
                  str(node.get("Annotation", "")).startswith("Link_Mac_arm64") and node.get("Action")]
    require(compile_nodes and len(link_nodes) == 1, "Bee compile/link action inventory differs")

    action_rows = [(node, action_arguments(node["Action"])) for node in compile_nodes + link_nodes]
    compilers = {str(resolve_graph_path(project_root, arguments[0])) for _, arguments in action_rows}
    sysroots = {str(resolve_graph_path(project_root, option_value(arguments, "-isysroot")))
                for _, arguments in action_rows}
    require(len(compilers) == 1, "Bee native actions use more than one compiler")
    require(len(sysroots) == 1, "Bee native actions use more than one SDK sysroot")

    link_outputs = [resolve_graph_path(project_root, item) for item in link_nodes[0].get("Outputs", [])
                    if Path(str(item)).name == "GameAssembly.dylib"]
    require(len(link_outputs) == 1, "Bee linker must emit exactly one GameAssembly.dylib")
    reachable = {link_outputs[0]}
    while True:
        added = set()
        for node in nodes:
            if type(node) is not dict:
                continue
            inputs = {resolve_graph_path(project_root, item) for item in node.get("Inputs", [])}
            if inputs & reachable:
                added.update(resolve_graph_path(project_root, item) for item in node.get("Outputs", []))
        if added <= reachable:
            break
        reachable.update(added)
    require(Path(os.path.abspath(native_library_path)) in reachable,
            "Bee link output does not reach the selected GameAssembly.dylib")

    macros = {name: set() for name in ("IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT")}
    response_sources = set()
    for _, arguments in action_rows:
        for argument in arguments[1:]:
            if argument.startswith("-D"):
                definition = argument[2:].split("=", 1)
                if definition[0] in macros:
                    macros[definition[0]].add(definition[1] if len(definition) == 2 else "1")
            if argument.startswith("@") and len(argument) > 1:
                response_sources.add(str(resolve_graph_path(project_root, argument[1:])))
    require(all(len(values) <= 1 for values in macros.values()),
            "Bee native actions disagree on IL2CPP diagnostic macros")

    def effective(name: str, fallback: str) -> str:
        return next(iter(macros[name])) if macros[name] else fallback

    return {
        "compileActionCount": len(compile_nodes),
        "linkActionCount": 1,
        "compilerPath": next(iter(compilers)),
        "sdkPath": next(iter(sysroots)),
        "beeLinkOutputPath": str(link_outputs[0]),
        "il2cppDebug": effective("IL2CPP_DEBUG", header_default(config, "IL2CPP_DEBUG")),
        "ndebug": effective("NDEBUG", "0"),
        "il2cppDevelopment": effective("IL2CPP_DEVELOPMENT", header_default(config, "IL2CPP_DEVELOPMENT")),
        "responseSources": sorted(response_sources),
    }


def verify_receipt(receipt_path: Path) -> dict:
    project_root = project_root_for(receipt_path)
    build = read_object(receipt_path)
    require(build.get("schemaVersion") == 1 and build.get("kind") == "H1CountDiagnosticPlayerBuild" and
            build.get("diagnosticOnly") is True, "Invalid H1 build receipt: " + str(receipt_path))
    feature = build.get("featureEnabled")
    cpp = build.get("cppConfiguration")
    require(type(feature) is bool and cpp in ("Debug", "Release"), "Invalid build mode")
    mode = ("On" if feature else "Off") + "/" + cpp
    require(build.get("baselineBuildId") == "H1Count-" + mode.replace("/", "-"), "Build ID differs")
    require(("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + ("1" if feature else "0")) in build.get("nativeArguments", ""),
            "Native feature flag differs: " + mode)

    provenance_path = canonical_file(build.get("compilerProvenancePath", ""), "compiler provenance")
    require(sha256(provenance_path) == build.get("compilerProvenanceSha256"), "Compiler provenance hash differs")
    provenance = read_object(provenance_path)
    require(provenance == build.get("compilerProvenance"), "Embedded and retained compiler provenance differ")
    for field in ("buildId", "buildGuid", "inputSnapshotHash", "nativeLibraryPath",
                  "nativeLibrarySha256", "sourcePinSha256"):
        source = "baselineBuildId" if field == "buildId" else field
        require(provenance.get(field) == build.get(source), "Provenance binding differs: " + field)

    retained_paths = {}
    for path_field, hash_field in (("nativeLibraryPath", "nativeLibrarySha256"),
                                   ("beeActionGraphPath", "beeActionGraphSha256"),
                                   ("il2cppConfigPath", "il2cppConfigSha256")):
        path = canonical_file(provenance.get(path_field, ""), path_field)
        require(sha256(path) == provenance.get(hash_field), "Current bytes differ: " + path_field)
        retained_paths[path_field] = path
    graph = read_object(retained_paths["beeActionGraphPath"])
    config = retained_paths["il2cppConfigPath"].read_text(encoding="utf-8")
    derived = derive_graph_evidence(graph, project_root, retained_paths["nativeLibraryPath"], config)
    for field in ("compileActionCount", "linkActionCount", "compilerPath", "sdkPath",
                  "beeLinkOutputPath", "il2cppDebug", "ndebug", "il2cppDevelopment"):
        require(provenance.get(field) == derived[field], "Bee-derived provenance differs: " + field)
    compiler = absolute_tool_file(provenance.get("compilerPath", ""), "compilerPath")
    require(sha256(compiler, allow_symlink=True) == provenance.get("compilerSha256"),
            "Current bytes differ: compilerPath")
    sdk_settings = absolute_tool_file(provenance.get("sdkSettingsPath", ""), "sdkSettingsPath")
    require(sha256(sdk_settings, allow_symlink=True) == provenance.get("sdkSettingsSha256"),
            "Current bytes differ: sdkSettingsPath")
    require(provenance.get("compileActionCount", 0) > 0 and provenance.get("linkActionCount") == 1,
            "Compiler/link action inventory differs")
    require(Path(provenance.get("beeLinkOutputPath", "")).name == "GameAssembly.dylib",
            "Bee link output is not GameAssembly.dylib")
    expected_macros = ("1", "0") if cpp == "Debug" else ("0", "1")
    require((provenance.get("il2cppDebug"), provenance.get("ndebug")) == expected_macros and
            provenance.get("il2cppDevelopment") == "0", "Effective native macros differ: " + mode)
    responses = provenance.get("responseFiles")
    require(type(responses) is list, "Response-file inventory is missing")
    require(len(responses) == len(derived["responseSources"]), "Response-file inventory count differs")
    require(sorted(response.get("sourcePath") for response in responses) == derived["responseSources"],
            "Response-file source inventory differs")
    for response in responses:
        retained = canonical_file(response.get("retainedPath", ""), "retained response file")
        require(sha256(retained) == response.get("sha256") and retained.stat().st_size == response.get("bytes"),
                "Retained response-file bytes differ")
    return {
        "mode": mode, "receiptPath": str(receipt_path), "receiptSha256": sha256(receipt_path),
        "buildGuid": build["buildGuid"], "nativeLibrarySha256": build["nativeLibrarySha256"],
        "compilerPath": provenance["compilerPath"], "compilerSha256": provenance["compilerSha256"],
        "compilerVersion": provenance["compilerVersion"], "sdkPath": provenance["sdkPath"],
        "sdkVersion": provenance["sdkVersion"], "sdkSettingsSha256": provenance["sdkSettingsSha256"],
        "sourcePinSha256": provenance["sourcePinSha256"], "compileActionCount": provenance["compileActionCount"],
        "linkActionCount": provenance["linkActionCount"], "il2cppDebug": provenance["il2cppDebug"],
        "ndebug": provenance["ndebug"], "il2cppDevelopment": provenance["il2cppDevelopment"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(len(args.build) == 4, "Exactly four --build receipts are required")
    rows = [verify_receipt(canonical_file(str(path), "build receipt")) for path in args.build]
    require({row["mode"] for row in rows} == {"On/Debug", "On/Release", "Off/Debug", "Off/Release"},
            "The complete On/Off x Debug/Release inventory is required")
    for field in ("compilerPath", "compilerSha256", "compilerVersion", "sdkPath", "sdkVersion",
                  "sdkSettingsSha256", "sourcePinSha256"):
        require(len({row[field] for row in rows}) == 1, "Toolchain comparison differs: " + field)
    output = args.output
    require(output.is_absolute() and output == output.resolve() and not output.exists() and output.parent.is_dir(),
            "Output must be a new canonical path with an existing parent")
    report = {"schemaVersion": 1, "kind": "H1CompilerProvenanceVerification", "status": "Passed",
              "result": "Passed", "modeCount": 4, "rows": sorted(rows, key=lambda row: row["mode"])}
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "Passed", "modeCount": 4, "output": str(output)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, json.JSONDecodeError, VerificationError) as error:
        print("Failed: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
