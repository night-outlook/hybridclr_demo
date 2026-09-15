"""Bounded, independent interpretation of retained macOS Bee compiler actions.

The action graph is provenance input, not proof that a build ran. Build/launch
pairing remains mandatory. Response files are expanded from retained bytes,
not a mutable Library tree. Macro state is evaluated in argument order for
each translation unit; linker definitions cannot supply compile definitions.

Apple Bee emits several source-owned compile domains into the same final link.
Runtime/IL2CPP actions carry the C++ configuration assertion profile, while the
bundled BDWGC and zlib C sources intentionally compile with their own profile.
All selected actions still have to carry the requested Shadow/count defines and
feed the selected native output; no action is ignored or unioned into another
macro state.
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
FEATURE = "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW"
DIAGNOSTIC = "HYBRIDCLR_H1_COUNT_DIAGNOSTICS"
DOMAIN_RUNTIME = "runtime"
DOMAIN_BDWGC = "bdwgc"
DOMAIN_ZLIB = "zlib"
EXTERNAL_DOMAINS = (DOMAIN_BDWGC, DOMAIN_ZLIB)


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
                need(base_name not in ("IL2CPP_DEBUG", "IL2CPP_DEVELOPMENT", FEATURE, DIAGNOSTIC),
                     "Function-like boolean macro requires preprocessing evidence")
            if operation == "-U":
                need(not separator, "-U cannot assign a value")
                values.pop(base_name, None)
            else:
                values[base_name] = value if separator else "1"
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
            "ndebug": "1" if "NDEBUG" in defined else "0",
            "il2cppDevelopment": effective("IL2CPP_DEVELOPMENT")}


def _single_source(arguments: list[str], root: Path, node: dict | None = None) -> str:
    """Identify the one compile input without interpreting output/dependency operands."""
    operands = {"-o", "-MF", "-MT", "-MQ", "-dependency-file", "-serialize-diagnostics",
                "-isysroot", "-arch", "-target", "--target", "-I", "-F", "-isystem",
                "-iquote", "-idirafter", "-iframework", "-isystem-after", "-D", "-U",
                "-x", "-resource-dir", "-stdlib", "-std", "-B", "-include-pch"}
    sources = []
    i = 1
    while i < len(arguments):
        token = arguments[i]
        if token == "-Xclang":
            need(i + 1 < len(arguments), "Missing -Xclang operand")
            i += 2; continue
        if token in operands:
            need(i + 1 < len(arguments), "Missing option operand: " + token)
            i += 2; continue
        if token.startswith("@") or token.startswith("-"):
            i += 1; continue
        sources.append(resolve(root, token)); i += 1
    if not sources and node is not None:
        candidates=[]
        for value in node.get("Inputs", []):
            path=resolve(root,value)
            if Path(path).suffix in {".c",".cc",".cpp",".cxx",".C",".m",".mm",".h",".hpp"}:
                candidates.append(path)
        sources=sorted(set(candidates))
    need(len(sources) == 1, "Expected exactly one native compile source")
    return sources[0]


def macro_domain(source: str) -> str:
    """Source ownership defines the macro contract; macro values never select a domain."""
    normalized = source.replace("\\", "/")
    if "/external/bdwgc/" in normalized or "/bdwgc/" in normalized:
        return DOMAIN_BDWGC
    if "/external/zlib/" in normalized or "/zlib/" in normalized:
        return DOMAIN_ZLIB
    return DOMAIN_RUNTIME


def _domain_summary(rows: list[dict]) -> list[dict]:
    result = []
    for name in (DOMAIN_RUNTIME, DOMAIN_BDWGC, DOMAIN_ZLIB):
        owned = [row for row in rows if row["domain"] == name]
        if not owned:
            continue
        states = {tuple(sorted(row["macros"].items())) for row in owned}
        need(len(states) == 1, "Translation units disagree inside macro domain: " + name)
        result.append({"domain": name, "count": len(owned), "macros": owned[0]["macros"],
                       "sourcesSha256": hashlib.sha256("\n".join(sorted(row["source"] for row in owned)).encode()).hexdigest()})
    need(sum(row["count"] for row in result) == len(rows), "Macro domain accounting omitted native compile actions")
    return result


def derive_graph_evidence(graph: dict, project_root: Path, native_library_path: Path,
                          config: str, response_contents: Mapping[str, bytes] | None = None,
                          *, expected_feature: bool | None = None) -> dict:
    responses = response_contents or {}
    nodes = graph.get("Nodes")
    need(type(nodes) is list and nodes and len(nodes) <= 1_000_000, "Missing/bounded Bee node inventory")
    compile_nodes = [n for n in nodes if type(n) is dict and str(n.get("Annotation", "")).startswith("C_Mac_arm64") and n.get("Action")]
    link_nodes = [n for n in nodes if type(n) is dict and str(n.get("Annotation", "")).startswith("Link_Mac_arm64") and n.get("Action")]
    need(compile_nodes and len(link_nodes) == 1, "Expected native compile actions and one link action")
    rows = []
    used = set()
    for node in compile_nodes + link_nodes:
        tokens = split(node["Action"])
        expanded, sources = expand(tokens, project_root, responses)
        used.update(sources)
        rows.append((node, expanded))
    compilers = {resolve(project_root, args[0]) for _, args in rows}
    sysroots = {resolve(project_root, option(args, "-isysroot")) for _, args in rows}
    need(len(compilers) == len(sysroots) == 1, "Native compiler/SDK action identities disagree")
    outputs = [resolve(project_root, p) for p in link_nodes[0].get("Outputs", []) if Path(p).name == "GameAssembly.dylib"]
    need(len(outputs) == 1, "Link action does not emit one GameAssembly.dylib")
    link_inputs = {resolve(project_root, p) for p in link_nodes[0].get("Inputs", [])}
    need(link_inputs, "Link action has no declared inputs")
    reachable = {outputs[0]}
    while True:
        added = set()
        for node in nodes:
            if type(node) is dict and {resolve(project_root, p) for p in node.get("Inputs", [])} & reachable:
                added.update(resolve(project_root, p) for p in node.get("Outputs", []))
        if added <= reachable: break
        reachable.update(added)
    need(resolve(project_root, str(native_library_path)) in reachable, "Link output does not reach selected native library")

    compile_rows = []
    for node, args in rows[:len(compile_nodes)]:
        values = definitions(args)
        if expected_feature is not None:
            need(values.get(FEATURE) == ("1" if expected_feature else "0") and values.get(DIAGNOSTIC) == "1",
                 "An actual compiler action lacks the requested Shadow/count-diagnostic defines")
        source = _single_source(args, project_root, node)
        node_outputs = {resolve(project_root, p) for p in node.get("Outputs", [])}
        if not str(node.get("Annotation", "")).startswith("C_Mac_arm64Pch"):
            need(bool(node_outputs & link_inputs), "Native compile action does not feed the selected GameAssembly link: " + source)
        compile_rows.append({"source": source, "domain": macro_domain(source),
                             "macros": effective_macros(args, config),
                             "annotation": str(node.get("Annotation", ""))})

    domains = _domain_summary(compile_rows)
    runtime = [row for row in domains if row["domain"] == DOMAIN_RUNTIME]
    need(len(runtime) == 1, "Runtime macro domain is missing/ambiguous")
    runtime_state = runtime[0]["macros"]
    return {"compileActionCount": len(compile_nodes), "linkActionCount": 1,
        "compilerPath": next(iter(compilers)), "sdkPath": next(iter(sysroots)),
        "beeLinkOutputPath": outputs[0], **runtime_state, "macroDomains": domains,
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
