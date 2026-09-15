"""PCH-aware H1 provenance. A graph is a plan, never proof of execution.

The only newly admitted driver escape is -Xclang -fno-pch-timestamp on a
PCH producer/consumer. Every consumed PCH needs one producer, a declared
file/node dependency, retained bytes/headers, and real compiler probes.
No ambient compiler, SDK, directory search, or unverified fallback is used.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import time

import h1_compiler_actions as a

FEATURE = "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW"
DIAGNOSTIC = "HYBRIDCLR_H1_COUNT_DIAGNOSTICS"
MACROS = ("IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT", FEATURE, DIAGNOSTIC)
SCHEMA = 1
MAX_GROUPS = 1024
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_TEXT_BYTES = 32 * 1024 * 1024
MAX_HEADERS = 32768
# Prefixes with an operand are parsed before flag prefixes. Unknown options
# stop the attempt rather than being silently dropped from compiler probes.
PAIRED = {"-isysroot", "-arch", "-target", "--target", "-I", "-F", "-isystem",
          "-iquote", "-idirafter", "-iframework", "-isystem-after", "-D", "-U",
          "-x", "-resource-dir", "-stdlib", "-std", "-B"}
DROP_PAIRS = {"-o", "-MF", "-MT", "-MQ", "-dependency-file", "-serialize-diagnostics"}
DROP_FLAGS = {"-c", "-MD", "-MMD", "-MP", "-MG"}
LANGUAGES = {".c": "c", ".cc": "c++", ".cpp": "c++", ".cxx": "c++",
             ".C": "c++", ".m": "objective-c", ".mm": "objective-c++",
             ".h": "c", ".hpp": "c++"}
SAFE_F = {"-fPIC", "-fpic", "-fPIE", "-fpie", "-fno-exceptions", "-fexceptions",
          "-fno-rtti", "-frtti", "-fvisibility=hidden", "-fvisibility=default",
          "-fvisibility-inlines-hidden", "-fno-strict-aliasing", "-fstrict-aliasing",
          "-ffunction-sections", "-fdata-sections", "-fno-omit-frame-pointer",
          "-fomit-frame-pointer", "-fno-common", "-fcommon", "-fwrapv",
          "-fno-fast-math", "-ffast-math", "-fno-math-errno", "-fno-stack-protector",
          "-fstack-protector", "-fstack-protector-strong", "-fblocks", "-fno-blocks",
          "-fno-unwind-tables", "-funwind-tables", "-fno-asynchronous-unwind-tables",
          "-fasynchronous-unwind-tables", "-fno-ident", "-fno-builtin", "-fno-inline",
          "-fno-limit-debug-info", "-fstandalone-debug", "-fno-standalone-debug",
          "-fcolor-diagnostics", "-fno-color-diagnostics", "-fdiagnostics-absolute-paths",
          "-fno-caret-diagnostics", "-fno-show-column", "-fno-diagnostics-show-option",
          "-fno-ms-compatibility", "-fms-extensions", "-fno-ms-extensions",
          "-fsigned-char", "-funsigned-char", "-fno-threadsafe-statics",
          "-fno-delete-null-pointer-checks", "-fno-strict-overflow"}
SAFE_FLAG_PATTERNS = (r"-O(?:[0-3sgz]|fast)", r"-g(?:[0-3]|line-tables-only|dwarf-[2-5])?",
    r"-W(?!l,|p,|a,)[A-Za-z0-9_=+.,-]+", r"-m(?:macosx-version-min|ios-version-min)=[0-9.]+",
    r"-m(?:arch|cpu|tune|abi)=[A-Za-z0-9_.+-]+", r"-f(?:error-limit|message-length)=\d+",
    r"-f(?:debug|file|macro)-prefix-map=.+", r"-std=[A-Za-z0-9+_-]+", r"-stdlib=[A-Za-z0-9+_-]+")
BINDINGS = ("buildId", "buildGuid", "inputSnapshotHash", "nativeLibrarySha256", "sourcePinSha256")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            a.need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def file_bytes(path, bound=MAX_FILE_BYTES):
    path = Path(path)
    a.need(path.is_absolute() and path.is_file(), "Missing absolute PCH input: " + str(path))
    a.need(path.stat().st_size <= bound, "PCH input exceeds size bound: " + str(path))
    return path.read_bytes()


def load_row(row):
    path = Path(row["retainedPath"])
    a.need(not path.is_symlink() and path == path.resolve(strict=True), "Noncanonical retained PCH evidence")
    raw = file_bytes(path)
    a.need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "Retained PCH evidence bytes differ")
    return raw


def has_pch(graph, root, responses):
    for node in graph.get("Nodes", []):
        if not isinstance(node, dict) or not str(node.get("Annotation", "")).startswith("C_Mac_arm64"):
            continue
        args, _ = a.expand(a.split(node["Action"]), root, responses)
        if str(node["Annotation"]).startswith("C_Mac_arm64Pch") or any(t.startswith("-include-pch") for t in args):
            return True
    return False


def parse_action(args, root, producer):
    """Return probe flags, exact source/output and the single forced PCH."""
    kept, sources, pchs, outputs, timestamps = [args[0]], [], [], [], 0
    language = None
    i = 1
    while i < len(args):
        t = args[i]
        a.need("\n" not in t and "\r" not in t and "\x00" not in t, "Control character in action")
        if t == "-Xclang":
            a.need(i + 1 < len(args) and args[i + 1] == "-fno-pch-timestamp", "Forbidden -Xclang escape")
            timestamps += 1; i += 2; continue
        if t == "-include-pch":
            a.need(i + 1 < len(args) and not args[i + 1].startswith("-"), "Missing PCH operand")
            pchs.append(a.resolve(root, args[i + 1])); i += 2; continue
        a.need(not t.startswith(("-include", "-imacros", "-Wp,", "-Xpreprocessor", "-Xclang",
                                "-fmodule", "-fno-validate-pch", "-ivfsoverlay", "--config",
                                "-fplugin", "-load", "-cc1", "-save-temps")), "Forbidden forced/compiler input: " + t)
        if t in DROP_PAIRS or t in PAIRED:
            a.need(i + 1 < len(args), "Missing option operand: " + t)
            v = args[i + 1]
            if t == "-o": outputs.append(a.resolve(root, v))
            elif t == "-x":
                a.need(language is None, "Duplicate source language")
                language = v
            elif t in PAIRED:
                a.need(t != "-B", "Compiler subprogram override is not supported")
                kept.extend([t, v])
            i += 2; continue
        if t in DROP_FLAGS:
            i += 1; continue
        if not t.startswith("-"):
            sources.append(a.resolve(root, t)); i += 1; continue
        if t.startswith(("-D", "-U", "-I", "-F", "--target=")) or t in SAFE_F or t in ("-pipe", "-pthread", "-pedantic", "-pedantic-errors", "-w") or any(re.fullmatch(p, t) for p in SAFE_FLAG_PATTERNS):
            kept.append(t); i += 1; continue
        raise a.CompilerActionError("Unsupported probe option (retain this action; do not drop it): " + t)
    a.need(len(sources) == len(outputs) == 1, "Each native action needs one source and one -o output")
    a.need(timestamps <= 1 and len(pchs) <= 1 and not (producer and pchs), "Duplicate/chained PCH options")
    a.need(not timestamps or producer or pchs, "Timestamp escape has no evidenced PCH relation")
    source, output = sources[0], outputs[0]
    if language is None: language = LANGUAGES.get(Path(source).suffix)
    allowed = ("c-header", "c++-header", "objective-c-header", "objective-c++-header") if producer else ("c", "c++", "objective-c", "objective-c++")
    a.need(language in allowed, "Unsupported/implicit PCH source language: " + str(language))
    if producer: language = language.removesuffix("-header")
    # Original flags, minus only output/dependency switches and language/source.
    # No invocation is ever executed as a shell string.
    return {"flags": kept, "source": source, "output": output, "language": language,
            "pch": pchs[0] if pchs else None, "timestampPair": bool(timestamps)}


def dependency(nodes, consumer_index, producer_index, pch, root):
    """Bee file dependencies or explicit node-index dependencies are evidence.

    A coincident command-line filename without a graph edge is not accepted.
    Preserve which representation was used; never infer an edge from ordering.
    """
    node = nodes[consumer_index]
    if pch in [a.resolve(root, x) for x in node.get("Inputs", [])]:
        return {"kind": "declared-file-input", "consumer": consumer_index, "producer": producer_index, "path": pch}
    def edges(n):
        keys = [k for k in ("Deps", "Dependencies") if k in n]
        a.need(len(keys) <= 1, "Ambiguous Bee dependency representation")
        items = n[keys[0]] if keys else []
        a.need(type(items) is list and all(type(x) is int and 0 <= x < len(nodes) for x in items), "Invalid Bee node-index dependencies")
        return items
    queue = [(consumer_index, [consumer_index])]; seen = set()
    while queue:
        index, path = queue.pop()
        if index in seen: continue
        seen.add(index)
        for dep in edges(nodes[index]):
            if dep == producer_index:
                return {"kind": "declared-node-path", "nodes": path + [dep], "path": pch}
            queue.append((dep, path + [dep]))
    raise a.CompilerActionError("Consumed PCH lacks a declared Bee producer dependency: " + pch)


def plan(graph, root, native, config, responses, feature):
    a.need(type(feature) is bool, "PCH proof requires an explicit feature mode")
    nodes = graph.get("Nodes")
    a.need(type(nodes) is list and 0 < len(nodes) <= 1_000_000, "Invalid Bee graph")
    stripped = copy.deepcopy(graph)
    units, producers, used = [], {}, set()
    errors = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict) or not str(node.get("Annotation", "")).startswith(("C_Mac_arm64", "Link_Mac_arm64")) or not node.get("Action"):
            continue
        args, rsp = a.expand(a.split(node["Action"]), root, responses); used.update(rsp)
        if str(node["Annotation"]).startswith("Link_Mac_arm64"):
            stripped["Nodes"][index]["Action"] = shlex.join(args); continue
        producer = str(node["Annotation"]).startswith("C_Mac_arm64Pch")
        try:
            parsed = parse_action(args, root, producer)
            a.need(parsed["source"] in [a.resolve(root, p) for p in node.get("Inputs", [])], "Native source absent from Bee Inputs")
            a.need(parsed["output"] in [a.resolve(root, p) for p in node.get("Outputs", [])], "Native -o differs from Bee Outputs")
        except ValueError as error:
            errors.append({"nodeIndex": index, "annotation": node.get("Annotation"), "error": str(error)}); continue
        row = {"nodeIndex": index, "nodeSha256": sha(canonical(node)), "producer": producer, **parsed}
        units.append(row)
        if producer:
            a.need(Path(parsed["output"]).suffix == ".pch" and parsed["output"] not in producers, "Duplicate/non-PCH producer output")
            producers[parsed["output"]] = row
        # This copy is used ONLY for old command-line INTENT checks, not PCH proof.
        stripped["Nodes"][index]["Action"] = shlex.join(parsed["flags"])
    a.need(not errors, "Unsupported native actions:\n" + json.dumps(errors, indent=2))
    a.need(producers, "No PCH producer found")
    for output in producers:
        owners = [i for i, n in enumerate(nodes) if isinstance(n, dict) and output in [a.resolve(root, p) for p in n.get("Outputs", [])]]
        a.need(owners == [producers[output]["nodeIndex"]], "PCH output has another graph producer")
    consumers, groups = [], {}
    for unit in units:
        pch = unit["output"] if unit["producer"] else unit["pch"]
        if pch is None: continue
        a.need(pch in producers, "Consumed PCH is not produced in this selected graph")
        if not unit["producer"]:
            edge = dependency(nodes, unit["nodeIndex"], producers[pch]["nodeIndex"], pch, root)
            consumers.append({"nodeIndex": unit["nodeIndex"], "pch": pch, "dependency": edge})
        # All flag contexts get their own probe; only byte-identical contexts coalesce.
        context = {"flags": unit["flags"], "language": unit["language"], "pch": pch}
        key = sha(canonical(context))
        groups.setdefault(key, {"id": key, **context, "unitIndices": []})["unitIndices"].append(unit["nodeIndex"])
    a.need(consumers and {c["pch"] for c in consumers} == set(producers), "Unused/missing PCH consumers")
    a.need(len(groups) <= MAX_GROUPS, "Too many distinct PCH probe contexts")
    derived = a.derive_graph_evidence(stripped, root, native, config, {}, expected_feature=feature)
    derived["responseSources"] = sorted(used)
    return {"schemaVersion": SCHEMA, "units": units, "producers": sorted(producers.values(), key=lambda u: u["output"]),
            "consumers": consumers, "groups": sorted(groups.values(), key=lambda g: g["id"]), "derived": derived}


def expected_macros(blueprint, feature):
    d = blueprint["derived"]
    return {"IL2CPP_DEBUG": d["il2cppDebug"], "NDEBUG": d["ndebug"], "IL2CPP_DEVELOPMENT": d["il2cppDevelopment"], FEATURE: "1" if feature else "0", DIAGNOSTIC: "1"}


def probe_source(config_path, expected):
    a.need(not any(c in str(config_path) for c in ('"', '\\', '\n', '\r')), "Unsafe configuration include path")
    lines = ['/* H1 PCH state probe v1: after the forced prefix and exact config. */', '#include "' + str(config_path) + '"']
    for macro in MACROS:
        if macro == "NDEBUG":
            lines += [("#ifndef " if expected[macro] == "1" else "#ifdef ") + macro, '#error H1_PCH_NDEBUG_DEFINEDNESS', '#endif']
        else:
            lines += ['#if !defined(' + macro + ') || ((' + macro + ') != ' + expected[macro] + ')', '#error H1_PCH_' + macro, '#endif']
    return ("\n".join(lines) + "\n").encode()


def dump_state(raw):
    text = raw.decode("utf-8")
    result = {}
    for name in MACROS:
        a.need(name == "NDEBUG" or not re.search(r"(?m)^#define[ \t]+" + re.escape(name) + r"\(", text), "Function-like effective boolean macro: " + name)
        matches = re.findall(r"(?m)^#define[ \t]+" + re.escape(name) + r"(?:\([^\n]*?\))?(?:[ \t]+([^\n]*))?$", text)
        a.need(len(matches) <= 1, "Duplicate tracked macro in compiler output: " + name)
        if name == "NDEBUG": result[name] = "1" if matches else "0"
        else:
            a.need(len(matches) == 1, "Missing effective compiler macro: " + name)
            result[name] = a.boolean_macro(matches[0].strip(), name)
    return result


def pch_headers(raw, root):
    text = raw.decode("utf-8")
    a.need("Information for module file" in text and "Input file:" in text, "Unrecognized Clang PCH inventory; preserve raw output")
    a.need(not re.search(r"(?mi)^\s*(?:Imports|Imported module|VFS overlay file):\s*\S", text), "Chained/module/VFS PCH is outside this contract")
    values = []
    for line in text.splitlines():
        if not line.strip().startswith("Input file:"): continue
        value = line.strip()[len("Input file:"):].strip()
        value = re.sub(r"\s+\[System\]$", "", value)
        a.need(value and not re.search(r"\[[^]]+\]$", value), "Unsupported PCH input inventory suffix")
        values.append(a.resolve(root, value))
    a.need(0 < len(values) <= MAX_HEADERS and len(values) == len(set(values)), "Invalid/duplicate PCH header inventory")
    return sorted(values)


def commands(group, retained_pch, source_path):
    prefix = group["flags"] + ["-include-pch", retained_pch, "-x", group["language"]]
    return {"syntax": prefix + ["-fsyntax-only", source_path], "macros": prefix + ["-E", "-dM", source_path]}


def rebuild_command(args, destination):
    result = list(args)
    for i, token in enumerate(result[:-1]):
        if token == "-o": result[i + 1] = str(destination)
        elif token in ("-MF", "-dependency-file"): result[i + 1] = str(destination) + ".d"
        elif token == "-serialize-diagnostics": result[i + 1] = str(destination) + ".dia"
    return result


def capture(blueprint, graph, root, config_path, binding, out, responses=None, timeout=60):
    """Called only as part of a fresh build capture; failure leaves raw attempts."""
    out = Path(out)
    a.need(not out.exists(), "PCH proof directory must be new")
    out.mkdir(parents=True)
    tracked, records = {}, {}
    deadline = time.monotonic() + 1500  # Leave time for the 30-minute Unity adapter to collect failures.
    def retain(source):
        source = str(source)
        if source in records: return records[source]
        raw = file_bytes(source); digest = sha(raw)
        target = out / "inputs" / (digest + (".pch" if Path(source).suffix == ".pch" else ".bin"))
        if not target.exists(): write(target, raw)
        a.need(file_bytes(target) == raw, "Retained PCH input collision")
        row = {"sourcePath": source, "retainedPath": str(target), "sha256": digest, "bytes": len(raw)}
        records[source] = row; tracked[source] = digest
        return row
    def execute(argv, name, require_success=True):
        remaining = deadline - time.monotonic()
        a.need(remaining > 0, "PCH capture budget exhausted; preserve this partial attempt")
        result = {"argv": argv, "cwd": str(root), "exitCode": None}
        stdout, stderr = out / (name + ".stdout"), out / (name + ".stderr")
        # File-backed output avoids an unbounded subprocess pipe. Never a shell.
        with stdout.open("xb") as so, stderr.open("xb") as se:
            try:
                run = subprocess.run(argv, cwd=root, stdout=so, stderr=se, timeout=min(timeout, remaining), check=False)
                result["exitCode"] = run.returncode
            except subprocess.TimeoutExpired:
                result["timeout"] = True
        for key, p in (("stdout", stdout), ("stderr", stderr)):
            raw = file_bytes(p, MAX_TEXT_BYTES)
            result[key] = {"retainedPath": str(p), "sha256": sha(raw), "bytes": len(raw)}
        write(out / (name + ".execution.json"), canonical(result) + b"\n")
        a.need(not require_success or result["exitCode"] == 0, "PCH compiler diagnostic failed; raw execution retained: " + name)
        return result
    compiler = blueprint["derived"]["compilerPath"]
    compiler_hash = sha(file_bytes(compiler))
    expected = expected_macros(blueprint, binding["featureEnabled"])
    producers = []
    for number, producer in enumerate(blueprint["producers"]):
        pch = retain(producer["output"])
        info = execute([compiler, "-module-file-info", pch["retainedPath"]], "pch-%03d-info" % number)
        headers = pch_headers(load_row(info["stdout"]), root)
        a.need(producer["source"] in headers, "PCH does not identify its producer source header")
        rows = [retain(p) for p in headers]
        input_rows = []
        for source in sorted(set(a.resolve(root, p) for p in graph["Nodes"][producer["nodeIndex"]].get("Inputs", []))):
            if source == str(Path(blueprint["derived"]["sdkPath"]) / "dummy") and not Path(source).exists():
                # Bee's SDK marker is not a source file. Preserve that fact and
                # bind it to the selected SDK metadata; do not invent its bytes.
                sdk = retain(str(Path(blueprint["derived"]["sdkPath"]) / "SDKSettings.plist"))
                input_rows.append({"sourcePath": source, "kind": "bee-sdk-marker", "sdkSettings": sdk})
            elif source == compiler or Path(source).name in ("clang++", "clang", "libtool"):
                raw = file_bytes(source); digest = sha(raw); tracked[source] = digest
                input_rows.append({"kind": "toolchain-binary", "toolPath": source, "toolSha256": digest, "bytes": len(raw)})
            else:
                input_rows.append({"kind": "file", **retain(source)})
        original_args, _ = a.expand(a.split(graph["Nodes"][producer["nodeIndex"]]["Action"]), root, responses or {})
        rebuilt_path = out / ("producer-%03d-rebuilt.pch" % number)
        rebuilt_run = execute(rebuild_command(original_args, rebuilt_path), "producer-%03d-rebuild" % number)
        rebuilt_bytes = file_bytes(rebuilt_path)
        rebuilt = {"retainedPath": str(rebuilt_path), "sha256": sha(rebuilt_bytes), "bytes": len(rebuilt_bytes)}
        a.need(sha(rebuilt_bytes) == pch["sha256"] and len(rebuilt_bytes) == pch["bytes"],
               "Exact PCH producer replay differs; retain both artifacts and return to primary implementation (no fallback)")
        producers.append({"nodeIndex": producer["nodeIndex"], "pch": pch, "info": info, "headers": rows, "inputs": input_rows,
                          "rebuild": {"execution": rebuilt_run, "output": rebuilt}})
    config = retain(config_path)
    groups, failures = [], []
    pch_map = {p["pch"]["sourcePath"]: p["pch"]["retainedPath"] for p in producers}
    for group in blueprint["groups"]:
        source_path = out / ("probe-" + group["id"] + ".txt")
        raw = probe_source(config_path, expected); write(source_path, raw)
        cmds = commands(group, pch_map[group["pch"]], str(source_path))
        results = {kind: execute(argv, group["id"] + "-" + kind, require_success=False) for kind, argv in cmds.items()}
        try:
            a.need(all(r["exitCode"] == 0 and not r.get("timeout") for r in results.values()), "PCH compiler diagnostic failed")
            a.need(dump_state(load_row(results["macros"]["stdout"])) == expected, "PCH effective macro state differs from requested profile")
        except ValueError as error:
            failures.append({"context": group["id"], "error": str(error)})
        groups.append({"id": group["id"], "source": {"retainedPath": str(source_path), "sha256": sha(raw), "bytes": len(raw)}, **results})
    for source, digest in tracked.items():
        a.need(sha(file_bytes(source)) == digest, "PCH input changed during capture: " + source)
    a.need(sha(file_bytes(compiler)) == compiler_hash, "Compiler changed during PCH probes")
    proof = {"schemaVersion": SCHEMA, "kind": "H1PchProvenance", "status": "CompilerProbedNotRuntimeAccepted",
        "binding": copy.deepcopy(binding), "plan": copy.deepcopy(blueprint), "compilerSha256": compiler_hash, "config": config,
        "producers": producers, "groups": groups, "expectedMacros": expected,
        "scope": "Exact PCH producers and consumer contexts; macros after PCH plus the pinned il2cpp-config.h, before the translation-unit body. Not a claim that arbitrary source code cannot redefine macros.",
        "humanGatePassed": False, "mayEnterR02": False}
    if failures:
        write(out / "pch-failed-attempt.json", canonical({**proof, "status": "Failed", "failures": failures}) + b"\n")
        raise a.CompilerActionError("PCH compiler diagnostic failed in " + str(len(failures)) + " context(s); all raw probes retained")
    write(out / "pch-proof.json", canonical(proof) + b"\n")
    return proof


def verify(proof, graph, root, native, config, responses, binding, read=load_row):
    """Pure archive-capable check; the reader resolves locators through the index.

    It checks raw probe source/output/argv, not a previous PASS summary. Actual
    build/launch authenticity and optional live replay remain separate layers.
    """
    a.need(type(proof.get("schemaVersion")) is int and proof["schemaVersion"] == SCHEMA and proof.get("kind") == "H1PchProvenance", "Unsupported PCH proof")
    a.need(proof.get("binding") == binding, "PCH proof build/graph binding differs")
    blueprint = plan(graph, root, native, config, responses, binding["featureEnabled"])
    a.need(proof.get("plan") == blueprint, "PCH producer/consumer plan differs from the raw graph")
    expected = expected_macros(blueprint, binding["featureEnabled"])
    a.need(proof.get("expectedMacros") == expected, "PCH expected macro profile differs")
    def checked(row):
        raw = read(row)
        a.need(type(raw) is bytes and type(row.get("bytes")) is int and len(raw) == row["bytes"] and sha(raw) == row.get("sha256"), "PCH artifact hash/size differs")
        return raw
    a.need(checked(proof["config"]).decode("utf-8") == config, "PCH config differs")
    def execution(row, argv):
        a.need(row.get("argv") == argv and row.get("cwd") == str(root) and type(row.get("exitCode")) is int and row["exitCode"] == 0 and not row.get("timeout"), "PCH compiler execution differs/failed")
        checked(row["stderr"])
        return checked(row["stdout"])
    producer_rows = proof.get("producers")
    a.need(type(producer_rows) is list and len(producer_rows) == len(blueprint["producers"]), "PCH producer proof inventory differs")
    pch_map = {}
    for expected_row, row in zip(blueprint["producers"], producer_rows):
        a.need(row.get("nodeIndex") == expected_row["nodeIndex"] and row["pch"]["sourcePath"] == expected_row["output"], "PCH producer proof order differs")
        original_pch = checked(row["pch"]); pch_map[expected_row["output"]] = row["pch"]["retainedPath"]
        original_args, _ = a.expand(a.split(graph["Nodes"][expected_row["nodeIndex"]]["Action"]), root, responses)
        replay = row["rebuild"]
        execution(replay["execution"], rebuild_command(original_args, replay["output"]["retainedPath"]))
        a.need(checked(replay["output"]) == original_pch, "Rebuilt PCH differs from original producer output")
        info = execution(row["info"], [blueprint["derived"]["compilerPath"], "-module-file-info", row["pch"]["retainedPath"]])
        headers = pch_headers(info, root)
        a.need(expected_row["source"] in headers and [h["sourcePath"] for h in row["headers"]] == headers, "PCH header provenance differs")
        for header in row["headers"]: checked(header)
        original_inputs = sorted(set(a.resolve(root, p) for p in graph["Nodes"][expected_row["nodeIndex"]].get("Inputs", [])))
        a.need([r.get("sourcePath", r.get("toolPath")) for r in row["inputs"]] == original_inputs, "PCH producer input inventory differs")
        for item in row["inputs"]:
            if item.get("kind") == "bee-sdk-marker":
                a.need(item["sourcePath"] == str(Path(blueprint["derived"]["sdkPath"]) / "dummy") and item["sdkSettings"]["sourcePath"] == str(Path(blueprint["derived"]["sdkPath"]) / "SDKSettings.plist"), "Unapproved virtual producer input")
                checked(item["sdkSettings"])
            elif item.get("kind") == "toolchain-binary":
                a.need((item["toolPath"] == blueprint["derived"]["compilerPath"] or Path(item["toolPath"]).name in ("clang", "clang++", "libtool")) and re.fullmatch(r"[0-9a-f]{64}", item["toolSha256"]) and type(item.get("bytes")) is int and item["bytes"] > 0, "Malformed producer toolchain identity")
                if item["toolPath"] == blueprint["derived"]["compilerPath"]:
                    a.need(item["toolSha256"] == proof.get("compilerSha256"), "PCH producer compiler identity differs")
            else:
                a.need(item.get("kind") == "file", "Unknown PCH input role"); checked(item)
    groups = proof.get("groups")
    a.need(type(groups) is list and len(groups) == len(blueprint["groups"]), "Missing PCH context proofs")
    for group, row in zip(blueprint["groups"], groups):
        a.need(row.get("id") == group["id"], "PCH context proof order differs")
        a.need(checked(row["source"]) == probe_source(proof["config"]["sourcePath"], expected), "PCH assertion source differs")
        cmds = commands(group, pch_map[group["pch"]], row["source"]["retainedPath"])
        execution(row["syntax"], cmds["syntax"])
        raw = execution(row["macros"], cmds["macros"])
        a.need(dump_state(raw) == expected, "Effective PCH macro output differs")
    return blueprint["derived"]


def binding_from(provenance, root, feature, cpp):
    return {**{k: provenance[k] for k in BINDINGS}, "graphSha256": provenance["beeActionGraphSha256"],
            "projectRoot": str(root), "featureEnabled": feature, "cppConfiguration": cpp}


def main():
    p = argparse.ArgumentParser(description="Read-only PCH graph preflight; never writes a build receipt")
    p.add_argument("--graph", type=Path, required=True); p.add_argument("--project", type=Path, required=True)
    p.add_argument("--native", type=Path, required=True); p.add_argument("--config", type=Path, required=True)
    p.add_argument("--feature", choices=("on", "off"), required=True); p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    import h1_native_capture as capture_module
    graph = read_json(args.graph); root = args.project.resolve(strict=True)
    result = {"kind": "H1PchGraphPreflight", "diagnosticOnly": True, "humanGatePassed": False, "mayEnterR02": False}
    try:
        responses = capture_module.collect_responses(graph, root)
        result["plan"] = plan(graph, root, args.native, args.config.read_text(), responses, args.feature == "on")
        result["status"] = "StructureSupportedNotBuildAccepted"
    except (OSError, ValueError) as error:
        result["status"] = "Blocked"; result["error"] = str(error)
    write(args.output, canonical(result) + b"\n")
    return 0 if result["status"] != "Blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
