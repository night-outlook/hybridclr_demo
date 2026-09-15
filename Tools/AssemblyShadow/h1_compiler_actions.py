"""Bounded, independent interpretation of retained macOS Bee compiler actions.

The action graph is provenance input, not proof that a build ran. Build/launch
pairing remains mandatory. Response files are expanded from retained bytes,
not a mutable Library tree. Macro state is evaluated in argument order for
each translation unit; linker definitions cannot supply compile definitions.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shlex
from typing import Mapping

MAX_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_EXPANDED_ARGUMENTS = 1_000_000
MAX_RESPONSE_DEPTH = 16
TRACKED = ("IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT")
H1_APPLE_BEE_DOMAIN_POLICY = "h1-apple-bee-v1"


class CompilerActionError(ValueError):
    pass


def need(condition: object, message: str) -> None:
    if not condition:
        raise CompilerActionError(message)


def resolve(root: Path, value: str) -> str:
    need(type(value) is str and value and "\x00" not in value, "Empty or NUL compiler path")
    return os.path.abspath(value if os.path.isabs(value) else os.path.join(root, value))


def split(command: str) -> list[str]:
    need(type(command) is str and command.strip(), "Missing compiler action")
    try:
        result = shlex.split(command, posix=True)
    except ValueError as error:
        raise CompilerActionError("Malformed compiler arguments") from error
    need(result and not any(token in {"&&", "||", ";", "|", ">", "<"} for token in result),
         "Only direct compiler actions are supported")
    return result


def expand(arguments: list[str], root: Path, responses: Mapping[str, bytes]) -> tuple[list[str], set[str]]:
    result: list[str] = []
    used: set[str] = set()
    total_bytes = 0

    def visit(values: list[str], active: tuple[str, ...]) -> None:
        nonlocal total_bytes
        need(len(active) <= MAX_RESPONSE_DEPTH, "Response-file nesting limit exceeded")
        for argument in values:
            if argument.startswith("@"):
                need(len(argument) > 1, "Empty response-file argument")
                source = resolve(root, argument[1:])
                need(source not in active, "Response-file cycle: " + source)
                need(source in responses, "Unretained response file: " + source)
                data = responses[source]
                need(type(data) is bytes and len(data) <= MAX_RESPONSE_BYTES, "Invalid retained response bytes")
                total_bytes += len(data)
                need(total_bytes <= MAX_RESPONSE_BYTES * 4, "Expanded response-file byte budget exceeded")
                used.add(source)
                try:
                    text = data.decode("utf-8-sig")
                except UnicodeDecodeError as error:
                    raise CompilerActionError("Response file is not UTF-8") from error
                visit(split(text) if text.strip() else [], active + (source,))
            else:
                need("\x00" not in argument, "NUL compiler argument")
                result.append(argument)
                need(len(result) <= MAX_EXPANDED_ARGUMENTS, "Expanded compiler argument limit exceeded")
    visit(arguments, ())
    return result, used


def option(arguments: list[str], name: str) -> str:
    positions = [i for i, token in enumerate(arguments) if token == name]
    need(len(positions) == 1 and positions[0] + 1 < len(arguments), "Expected exactly one " + name)
    return arguments[positions[0] + 1]


def header_default(text: str, name: str) -> str:
    # Restrict this fallback to the existing #ifndef / #define contract.
    pattern = (r"(?m)^\s*#\s*ifndef\s+" + re.escape(name) +
        r"[ \t]*\r?\n[ \t]*#\s*define\s+" + re.escape(name) + r"[ \t]+([^\s/]+)")
    matches = re.findall(pattern, text)
    need(len(matches) == 1, "Missing/ambiguous header default: " + name)
    return boolean_macro(matches[0], name)


def boolean_macro(value: str, name: str) -> str:
    while value.startswith("(") and value.endswith(")"):
        value = value[1:-1]
    need(value in ("0", "1"), "Unresolved boolean macro expression: " + name)
    return value


def definitions(arguments: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    i = 0
    while i < len(arguments):
        argument = arguments[i]
        operation = None
        if argument in ("-D", "-U"):
            operation = argument
            i += 1
            need(i < len(arguments), "Missing macro operand")
            operand = arguments[i]
        elif argument.startswith(("-D", "-U")):
            operation, operand = argument[:2], argument[2:]
        if operation:
            name, separator, value = operand.partition("=")
            need(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?", name), "Invalid macro operand")
            base_name = name.split("(", 1)[0]
            if "(" in name:
                need(operation == "-D", "Function-like -U operand is not supported")
                need(base_name not in ("IL2CPP_DEBUG", "IL2CPP_DEVELOPMENT", "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW", "HYBRIDCLR_H1_COUNT_DIAGNOSTICS"),
                     "Function-like boolean macro requires preprocessing evidence")
            if operation == "-U":
                need(not separator, "-U cannot assign a value")
                values.pop(base_name, None)
            else:
                values[base_name] = value if separator else "1"
        # Forced include/macro files may redefine tracked values; do not guess.
        need(argument not in ("-include", "-imacros") and
             not argument.startswith(("-include", "-imacros", "-Wp,")) and
             argument not in ("-Xpreprocessor", "-Xclang"),
             "Forced preprocessor inputs require explicit preprocessing evidence")
        i += 1
    return values


def effective_macros(arguments: list[str], config: str) -> dict[str, str]:
    defined = definitions(arguments)
    def effective(name):
        return boolean_macro(defined[name], name) if name in defined else header_default(config, name)
    return {"il2cppDebug": effective("IL2CPP_DEBUG"),
            # assert uses definedness, not the numeric value. -DNDEBUG=0 is still defined.
            "ndebug": "1" if "NDEBUG" in defined else "0",
            "il2cppDevelopment": effective("IL2CPP_DEVELOPMENT")}



def _under(path: str, parent: str) -> bool:
    path = os.path.abspath(path)
    parent = os.path.abspath(parent)
    try:
        return os.path.commonpath((path, parent)) == parent
    except ValueError:
        return False


def _source_from_node(node: dict, project_root: Path) -> str:
    annotation = str(node.get("Annotation", ""))
    extensions = (".h", ".hpp", ".hh", ".hxx") if annotation.startswith("C_Mac_arm64Pch") else (".c", ".cc", ".cpp", ".cxx", ".m", ".mm")
    candidates = [resolve(project_root, value) for value in node.get("Inputs", [])
                  if type(value) is str and Path(value).suffix.lower() in extensions]
    if not annotation.startswith("C_Mac_arm64Pch"):
        # Bee declares the source header used to build the consumed PCH as an
        # input of many compile nodes. It is dependency evidence, not the TU.
        candidates = [value for value in candidates
                      if (os.sep + "libil2cpp" + os.sep + "pch" + os.sep) not in value]
    need(len(candidates) == 1, "Expected exactly one compile source in Bee Inputs: " + annotation)
    return candidates[0]


def _direct_assertion_profile(arguments: list[str]) -> dict[str, str]:
    values = definitions(arguments)
    def direct(name: str) -> str:
        return boolean_macro(values[name], name) if name in values else "undefined"
    return {"il2cppDebug": direct("IL2CPP_DEBUG"),
            "ndebug": "1" if "NDEBUG" in values else "0",
            "il2cppDevelopment": direct("IL2CPP_DEVELOPMENT")}


def _h1_apple_macro_domains(compile_nodes: list[dict], compile_arguments: list[list[str]],
                            link_node: dict, project_root: Path, config: str) -> tuple[dict[str, str], list[dict]]:
    sources = [_source_from_node(node, project_root) for node in compile_nodes]
    runtime_roots = set()
    for source in sources:
        parts = Path(source).parts
        indexes = [i for i, part in enumerate(parts) if part == "libil2cpp"]
        if indexes:
            need(len(indexes) == 1, "Ambiguous libil2cpp source root: " + source)
            runtime_roots.add(str(Path(*parts[:indexes[0] + 1])))
    need(len(runtime_roots) == 1, "Expected one installed libil2cpp source root for H1 Apple provenance")
    runtime_root = next(iter(runtime_roots))
    external_root = os.path.join(os.path.dirname(runtime_root), "external")
    parts = Path(runtime_root).parts
    try:
        hybrid_index = parts.index("HybridCLRData")
        graph_project_root = str(Path(*parts[:hybrid_index]))
    except ValueError:
        raise CompilerActionError("Installed IL2CPP root is not below HybridCLRData: " + runtime_root)
    generated_root = os.path.join(graph_project_root, "Library", "Bee", "artifacts", "MacStandalonePlayerBuildProgram")
    link_inputs = {resolve(project_root, value) for value in link_node.get("Inputs", [])}
    domains: dict[str, list[dict[str, str]]] = {"runtime": [], "bdwgc": [], "zlib": []}
    examples = {name: [] for name in domains}
    for node, arguments, source in zip(compile_nodes, compile_arguments, sources):
        producer = str(node.get("Annotation", "")).startswith("C_Mac_arm64Pch")
        generated_runtime = (_under(source, generated_root) and
            ((os.sep + "il2cppOutput" + os.sep + "cpp" + os.sep) in source or source.endswith(".lump.cpp")))
        if _under(source, runtime_root) or generated_runtime:
            domain = "runtime"
        elif _under(source, os.path.join(external_root, "bdwgc")):
            domain = "bdwgc"
        elif _under(source, os.path.join(external_root, "zlib")):
            domain = "zlib"
        else:
            raise CompilerActionError("Unreviewed Apple native source domain: " + source)
        if domain != "runtime":
            need(not producer, "External auxiliary domains may not produce the runtime PCH")
        if not producer:
            outputs = [resolve(project_root, value) for value in node.get("Outputs", []) if str(value).endswith(".o")]
            need(len(outputs) == 1 and outputs[0] in link_inputs,
                 "Native object is not a direct input of the selected GameAssembly link: " + source)
        profile = effective_macros(arguments, config) if domain == "runtime" else _direct_assertion_profile(arguments)
        domains[domain].append(profile)
        if len(examples[domain]) < 4:
            examples[domain].append(source)
    need(domains["runtime"], "H1 Apple provenance has no runtime/PCH domain")
    result = []
    for name in ("runtime", "bdwgc", "zlib"):
        rows = domains[name]
        if not rows:
            continue
        need(all(row == rows[0] for row in rows), "Apple Bee macro domain disagrees internally: " + name)
        result.append({"name": name, "unitCount": len(rows),
                       "profileKind": "effective-runtime-config" if name == "runtime" else "direct-command-line",
                       "profile": rows[0], "sourceExamples": examples[name]})
    return domains["runtime"][0], result


def derive_graph_evidence(graph: dict, project_root: Path, native_library_path: Path,
                          config: str, response_contents: Mapping[str, bytes] | None = None,
                          *, expected_feature: bool | None = None, domain_policy: str | None = None) -> dict:
    responses = response_contents or {}
    nodes = graph.get("Nodes")
    need(type(nodes) is list and nodes and len(nodes) <= 1_000_000, "Missing/bounded Bee node inventory")
    compile_nodes = [n for n in nodes if type(n) is dict and str(n.get("Annotation", "")).startswith("C_Mac_arm64") and n.get("Action")]
    link_nodes = [n for n in nodes if type(n) is dict and str(n.get("Annotation", "")).startswith("Link_Mac_arm64") and n.get("Action")]
    need(compile_nodes and len(link_nodes) == 1, "Expected native compile actions and one link action")
    rows = []
    used = set()
    for node in compile_nodes + link_nodes:
        expanded, sources = expand(split(node["Action"]), project_root, responses)
        used.update(sources)
        rows.append((node, expanded))
    compilers = {resolve(project_root, args[0]) for _, args in rows}
    sysroots = {resolve(project_root, option(args, "-isysroot")) for _, args in rows}
    need(len(compilers) == len(sysroots) == 1, "Native compiler/SDK action identities disagree")
    outputs = [resolve(project_root, value) for value in link_nodes[0].get("Outputs", []) if Path(value).name == "GameAssembly.dylib"]
    need(len(outputs) == 1, "Link action does not emit one GameAssembly.dylib")
    reachable = {outputs[0]}
    while True:
        added = set()
        for node in nodes:
            if type(node) is dict and {resolve(project_root, value) for value in node.get("Inputs", [])} & reachable:
                added.update(resolve(project_root, value) for value in node.get("Outputs", []))
        if added <= reachable:
            break
        reachable.update(added)
    need(resolve(project_root, str(native_library_path)) in reachable, "Link output does not reach selected native library")
    compile_arguments = [args for _, args in rows[:len(compile_nodes)]]
    if expected_feature is not None:
        for args in compile_arguments:
            values = definitions(args)
            need(values.get("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW") == ("1" if expected_feature else "0") and
                 values.get("HYBRIDCLR_H1_COUNT_DIAGNOSTICS") == "1",
                 "An actual compiler action lacks the requested Shadow/count-diagnostic defines")
    if domain_policy is None:
        states = [effective_macros(args, config) for args in compile_arguments]
        need(all(state == states[0] for state in states),
             "Translation units disagree on effective diagnostic macros (link flags are not compile evidence)")
        runtime_profile = states[0]
        macro_domains = [{"name": "global-legacy", "unitCount": len(states),
                          "profileKind": "effective-runtime-config", "profile": runtime_profile,
                          "sourceExamples": []}]
    else:
        need(domain_policy == H1_APPLE_BEE_DOMAIN_POLICY, "Unknown compiler macro-domain policy")
        runtime_profile, macro_domains = _h1_apple_macro_domains(
            compile_nodes, compile_arguments, link_nodes[0], project_root, config)
    return {"compileActionCount": len(compile_nodes), "linkActionCount": 1,
            "compilerPath": next(iter(compilers)), "sdkPath": next(iter(sysroots)),
            "beeLinkOutputPath": outputs[0], **runtime_profile,
            "macroDomains": macro_domains, "macroDomainPolicy": domain_policy or "legacy-global",
            "responseSources": sorted(used)}

def retained_responses(provenance: dict, hash_file) -> dict[str, bytes]:
    rows = provenance.get("responseFiles")
    need(type(rows) is list and len(rows) <= 16384, "Missing/bounded response-file inventory")
    result = {}
    for row in rows:
        need(type(row) is dict and type(row.get("sourcePath")) is str, "Invalid response row")
        source = row["sourcePath"]
        need(os.path.isabs(source) and os.path.abspath(source) == source and source not in result,
             "Duplicate/nonabsolute response source")
        path = Path(row.get("retainedPath", ""))
        need(path.is_absolute() and path == path.resolve(strict=True) and path.is_file() and not path.is_symlink(),
             "Retained response file must be canonical")
        need(type(row.get("bytes")) is int and 0 <= row["bytes"] <= MAX_RESPONSE_BYTES,
             "Response size is invalid")
        need(path.stat().st_size == row["bytes"] and hash_file(path) == row.get("sha256"), "Retained response bytes differ")
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == row.get("sha256"), "Response changed while reading")
        result[source] = data
    return result
