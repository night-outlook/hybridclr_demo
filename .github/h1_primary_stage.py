from pathlib import Path
import textwrap


def exact_replace(path, old, new, count=1):
    p = Path(path)
    text = p.read_text()
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"{path}: expected {count}, got {actual}: {old[:100]!r}")
    p.write_text(text.replace(old, new, count))


# Compiler action owner: preserve the legacy policy unless H1 explicitly requests
# the reviewed Apple source-domain policy.
path = "Tools/AssemblyShadow/h1_compiler_actions.py"
exact_replace(
    path,
    'TRACKED = ("IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT")\n',
    'TRACKED = ("IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT")\nH1_APPLE_BEE_DOMAIN_POLICY = "h1-apple-bee-v1"\n',
)
p = Path(path)
text = p.read_text()
start = text.index("def derive_graph_evidence(")
end = text.index("\ndef retained_responses(", start)
replacement = textwrap.dedent(r'''
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
        if _under(source, runtime_root) or (_under(source, generated_root) and
                (os.sep + "il2cppOutput" + os.sep + "cpp" + os.sep) in source):
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
''')
p.write_text(text[:start] + replacement + text[end:])

# PCH planner uses the reviewed H1 source-domain policy after stripping forced PCH syntax.
exact_replace(
    "Tools/AssemblyShadow/h1_pch_provenance.py",
    "derived = a.derive_graph_evidence(stripped, root, native, config, {}, expected_feature=feature)",
    "derived = a.derive_graph_evidence(stripped, root, native, config, {}, expected_feature=feature, domain_policy=a.H1_APPLE_BEE_DOMAIN_POLICY)",
)

# C# receipt gets canonical domain evidence.
exact_replace(
    "Assets/AssemblyShadowDemo/Editor/H1CompilerProvenance.cs",
    "public string il2cppDebug, ndebug, il2cppDevelopment, macroEvidence;\n",
    "public string il2cppDebug, ndebug, il2cppDevelopment, macroEvidence, macroDomainEvidence;\n",
)

# Strict verifier always reconstructs domain evidence from raw graph bytes.
path = "Tools/AssemblyShadow/verify-h1-compiler-provenance-strict.py"
p = Path(path)
text = p.read_text()
text = text.replace(
    "derived=strict.derive_graph_evidence(graph,root,Path(provenance['nativeLibraryPath']),config_path.read_text(),responses,expected_feature=build['featureEnabled'])",
    "derived=strict.derive_graph_evidence(graph,root,Path(provenance['nativeLibraryPath']),config_path.read_text(),responses,expected_feature=build['featureEnabled'],domain_policy=strict.H1_APPLE_BEE_DOMAIN_POLICY)",
)
anchor = "        need(set(derived['responseSources'])==set(responses),'Native response closure contains missing/unused captures')\n"
if text.count(anchor) != 1:
    raise SystemExit("strict verifier anchor changed")
text = text.replace(anchor, anchor +
    "        need(provenance.get('macroDomainEvidence')==json.dumps(derived['macroDomains'],sort_keys=True,separators=(',',':')),'Macro-domain evidence differs from raw Bee graph')\n", 1)
p.write_text(text)

# Fresh native capture creates evidence before plan-stage validation.
path = "Tools/AssemblyShadow/h1_native_capture.py"
p = Path(path)
text = p.read_text()
helper = textwrap.dedent('''
class CaptureAttempt:
    def __init__(self, root, kind):
        self.root = Path(root)
        actions.need(self.root.is_absolute() and self.root == self.root.resolve() and not self.root.exists(),
                     "Evidence directory must be new and canonical")
        actions.need(self.root.parent.is_dir() and not self.root.parent.is_symlink(),
                     "Evidence parent must exist and not be symlinked")
        self.root.mkdir()
        self.state = {"schemaVersion": 1, "kind": kind, "stage": "created",
                      "pchReplay": "NotRun", "macroProbes": "NotRun",
                      "humanGatePassed": False, "mayEnterR02": False}
        self.save()
    def save(self):
        tmp = self.root / "attempt-state.json.tmp"
        tmp.write_text(json.dumps(self.state, indent=2) + "\\n")
        os.replace(tmp, self.root / "attempt-state.json")
    def stage(self, name, **values):
        self.state.update(values); self.state["stage"] = name; self.save()
    def failure(self, error):
        target = self.root / "capture-failure.json"
        if not target.exists():
            write_new(target, (json.dumps({**self.state, "status": "Failed",
                       "errorType": type(error).__name__, "error": str(error)}, indent=2) + "\\n").encode())


def _retain_plan_inputs(graph, root, evidence_root):
    rows = []; seen = set()
    for node in graph.get("Nodes", []):
        if type(node) is not dict or not str(node.get("Annotation", "")).startswith("C_Mac_arm64"):
            continue
        for value in node.get("Inputs", []):
            if type(value) is not str: continue
            source = Path(actions.resolve(root, value)); key = str(source)
            if key in seen: continue
            seen.add(key)
            row = {"sourcePath": key, "exists": source.is_file(), "symlink": source.is_symlink()}
            if source.is_file() and not source.is_symlink():
                row["bytes"] = source.stat().st_size
                if row["bytes"] <= 64 * 1024 * 1024:
                    data = source.read_bytes(); row["sha256"] = hashlib.sha256(data).hexdigest()
                    if source.suffix.lower() in (".pch", ".h", ".hpp", ".hh", ".hxx"):
                        retained = evidence_root / "preplan-inputs" / (row["sha256"] + source.suffix.lower())
                        if not retained.exists(): write_new(retained, data)
                        row["retainedPath"] = str(retained)
                else:
                    row["hashStatus"] = "SkippedOver64MiBPlanRetentionBound"
            rows.append(row)
            actions.need(len(rows) <= 4096, "Pre-plan input inventory exceeds bound")
    write_new(evidence_root / "preplan-input-inventory.json", (json.dumps(rows, indent=2) + "\\n").encode())

''')
marker = "def unique_pairs(pairs):\n"
if "class CaptureAttempt:" in text or marker not in text:
    raise SystemExit("native capture helper anchor changed")
text = text.replace(marker, helper + marker, 1)
old = '''def capture(request: dict, evidence_root: Path) -> dict:
    root = Path(request["projectRoot"])
    actions.need(root.is_absolute() and root == root.resolve(strict=True), "Project root is not canonical")
    actions.need(evidence_root.is_absolute() and evidence_root == evidence_root.resolve() and not evidence_root.exists(),
                 "Evidence directory must be new and canonical")'''
new = '''def capture(request: dict, evidence_root: Path, *, original_request: bytes | None = None) -> dict:
    evidence_root = Path(evidence_root)
    attempt = CaptureAttempt(evidence_root, "H1NativeCaptureAttempt")
    if original_request is None:
        original_request = (json.dumps(request, sort_keys=True, separators=(",", ":")) + "\\n").encode()
    write_new(evidence_root / "capture-request.json", original_request)
    try:
        attempt.stage("request-validation")
        return _capture_impl(request, evidence_root, attempt)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        attempt.failure(error); raise


def _capture_impl(request: dict, evidence_root: Path, attempt: CaptureAttempt) -> dict:
    root = Path(request["projectRoot"])
    actions.need(root.is_absolute() and root == root.resolve(strict=True), "Project root is not canonical")'''
if old not in text:
    raise SystemExit("native capture signature changed")
text = text.replace(old, new, 1)
text = text.replace("    matches = []\n", "    attempt.stage('graph-selection')\n    matches = []\n", 1)
old = '''    raw_config = config_path.read_bytes()
    responses = collect_responses(graph, root)
    pch_plan = pch.plan(graph, root, native, raw_config.decode('utf-8'), responses, request.get("featureEnabled")) if pch.has_pch(graph, root, responses) else None
    derived = pch_plan['derived'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode('utf-8'), responses, expected_feature=request.get("featureEnabled"))'''
new = '''    raw_config = config_path.read_bytes()
    retained_graph = evidence_root / 'bee-action-graph.json'; retained_config = evidence_root / 'il2cpp-config.h'
    write_new(retained_graph, raw_graph); write_new(retained_config, raw_config)
    attempt.stage('preplan-input-retention'); _retain_plan_inputs(graph, root, evidence_root)
    responses = collect_responses(graph, root); response_rows = []
    for i, (source, data) in enumerate(sorted(responses.items())):
        retained = evidence_root / 'response-files' / ('%04d.rsp' % i); write_new(retained, data)
        response_rows.append({'sourcePath': source, 'retainedPath': str(retained), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    attempt.stage('planning')
    pch_plan = pch.plan(graph, root, native, raw_config.decode('utf-8'), responses, request.get("featureEnabled")) if pch.has_pch(graph, root, responses) else None
    derived = pch_plan['derived'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode('utf-8'), responses, expected_feature=request.get("featureEnabled"), domain_policy=actions.H1_APPLE_BEE_DOMAIN_POLICY)
    attempt.stage('planning-complete')'''
if old not in text: raise SystemExit("native capture plan block changed")
text = text.replace(old, new, 1)
old = '''    # No output is created until structural selection and macro interpretation pass.
    evidence_root.mkdir(parents=False)
    retained_graph = evidence_root / 'bee-action-graph.json'
    retained_config = evidence_root / 'il2cpp-config.h'
    retained_sdk = evidence_root / 'SDKSettings.plist'
    write_new(retained_graph, raw_graph); write_new(retained_config, raw_config); write_new(retained_sdk, sdk_bytes)
    response_rows = []
    for i, (source, data) in enumerate(sorted(responses.items())):
        retained = evidence_root / 'response-files' / ('%04d.rsp' % i)
        write_new(retained, data)
        response_rows.append({'sourcePath': source, 'retainedPath': str(retained),
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})'''
if old not in text: raise SystemExit("native capture output block changed")
text = text.replace(old, "    retained_sdk = evidence_root / 'SDKSettings.plist'; write_new(retained_sdk, sdk_bytes)", 1)
text = text.replace(
    "        proof = pch.capture(pch_plan, graph, root, str(config_path), binding, evidence_root / 'pch', responses=responses)",
    "        attempt.stage('pch-execution', pchReplay='Invoked', macroProbes='Invoked')\n        proof = pch.capture(pch_plan, graph, root, str(config_path), binding, evidence_root / 'pch', responses=responses)", 1)
text = text.replace(
    "        'macroEvidence': 'Per-unit ordered -D/-U intent; NDEBUG uses definedness. PCH contexts additionally require the bound raw syntax/macro proof when pchProofPath is nonempty. Other forced-input routes remain prohibited.',",
    "        'macroEvidence': 'Source-owned Apple Bee domains: runtime/PCH is build-profile authoritative; BDWGC and zlib direct-link domains are independently consistent.',\n        'macroDomainEvidence': json.dumps(derived['macroDomains'], sort_keys=True, separators=(',', ':')),", 1)
text = text.replace(
    "    a=p.parse_args(); request_path=canonical_file(str(a.request)); before=digest(request_path)\n    report=capture(read_json(request_path), a.evidence_root)\n    actions.need(digest(request_path)==before, 'Capture request changed')",
    "    a=p.parse_args(); request_path=canonical_file(str(a.request)); raw_request=request_path.read_bytes(); before=hashlib.sha256(raw_request).hexdigest()\n    report=capture(json.loads(raw_request.decode('utf-8-sig'), object_pairs_hook=unique_pairs), a.evidence_root, original_request=raw_request)\n    actions.need(digest(request_path)==before, 'Capture request changed')", 1)
p.write_text(text)

# Diagnostic replay retains exact bytes before planning.
Path("Tools/AssemblyShadow/h1_pch_diagnose.py").write_text(textwrap.dedent(r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import h1_native_capture as n
import h1_pch_provenance as p

def diagnose(request_path, graph_path, output):
    output = Path(output); attempt = n.CaptureAttempt(output, "H1PchDiagnosticReplayAttempt")
    summary = {"kind": "H1PchDiagnosticReplay", "status": "Blocked", "diagnosticOnly": True,
               "freshBuildClaim": False, "humanGatePassed": False, "mayEnterR02": False}
    try:
        attempt.stage("request-and-graph-retention")
        request_path = n.canonical_file(str(request_path)); graph_path = n.canonical_file(str(graph_path))
        request_bytes = request_path.read_bytes(); graph_bytes = graph_path.read_bytes()
        n.write_new(output / "original-request.json", request_bytes); n.write_new(output / "original-graph.json", graph_bytes)
        request = json.loads(request_bytes.decode("utf-8-sig"), object_pairs_hook=n.unique_pairs)
        graph = json.loads(graph_bytes.decode("utf-8-sig"), object_pairs_hook=n.unique_pairs)
        root = Path(request["projectRoot"]); p.a.need(root.is_absolute() and root == root.resolve(strict=True), "Original project root unavailable")
        native = n.canonical_file(request["nativeLibraryPath"]); config = n.canonical_file(request["il2cppConfigPath"]); config_bytes = config.read_bytes()
        n.write_new(output / "il2cpp-config.h", config_bytes); p.a.need(n.digest(native) == request["nativeLibrarySha256"], "Selected failed native output bytes differ")
        attempt.stage("preplan-input-retention"); n._retain_plan_inputs(graph, root, output); responses = n.collect_responses(graph, root)
        for i, (source, data) in enumerate(sorted(responses.items())): n.write_new(output / "response-files" / ("%04d.rsp" % i), data)
        attempt.stage("planning"); blueprint = p.plan(graph, root, native, config_bytes.decode("utf-8"), responses, request["featureEnabled"])
        binding = {**{k: request[k] for k in p.BINDINGS}, "graphSha256": p.sha(graph_bytes), "projectRoot": str(root),
                   "featureEnabled": request["featureEnabled"], "cppConfiguration": request["cppConfiguration"],
                   "diagnosticOnly": True, "replayedRequestSha256": p.sha(request_bytes)}
        attempt.stage("pch-execution", pchReplay="Invoked", macroProbes="Invoked")
        proof = p.capture(blueprint, graph, root, str(config), binding, output / "pch", responses)
        p.verify(proof, graph, root, native, config_bytes.decode("utf-8"), responses, binding)
        summary.update(status="DiagnosticReplayVerifiedNotBuildAccepted", proofPath=str(output / "pch/pch-proof.json"), proofSha256=n.digest(output / "pch/pch-proof.json"))
        attempt.stage("completed", pchReplay="Completed", macroProbes="Completed")
    except (OSError, ValueError, KeyError, TypeError) as error:
        summary.update(error=str(error), errorType=type(error).__name__, failedStage=attempt.state["stage"])
        n.write_new(output / "diagnostic-result.json", (json.dumps(summary, indent=2) + "\n").encode()); attempt.failure(error); raise
    n.write_new(output / "diagnostic-result.json", (json.dumps(summary, indent=2) + "\n").encode()); return summary

def main():
    q=argparse.ArgumentParser(); q.add_argument("--request",type=Path,required=True); q.add_argument("--graph",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
    x=q.parse_args(); print(json.dumps(diagnose(x.request,x.graph,x.output),indent=2)); return 0
if __name__ == "__main__":
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error: print("Blocked diagnostic replay: " + str(error), file=__import__("sys").stderr); raise SystemExit(1)
'''))

# Focused source-domain tests.
Path("Tools/AssemblyShadow/tests/test_h1_apple_macro_domains.py").write_text(textwrap.dedent(r'''import unittest
from pathlib import Path
import h1_compiler_actions as h
CONFIG='#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'
class Tests(unittest.TestCase):
    def graph(self,release=False):
        root=Path('/project'); base=root/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp'; sources=[base/'libil2cpp/vm/A.cpp',base/'external/bdwgc/extra/gc.c',base/'external/zlib/adler32.c',base/'external/zlib/crc32.c']; runtime='-DNDEBUG=1' if release else '-DIL2CPP_DEBUG=1'; nodes=[]
        for i,src in enumerate(sources):
            out=f'o{i}.o'; flag=runtime if i==0 else ''; lang='c++' if i==0 else 'c'; nodes.append({'Annotation':'C_Mac_arm64 '+out,'Action':f'/tool/clang++ -isysroot /sdk -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1 {flag} -c -x {lang} "{src}" -o {out}','Inputs':[str(src)],'Outputs':[out]})
        nodes += [{'Annotation':'Link_Mac_arm64','Action':'/tool/clang++ -isysroot /sdk','Inputs':[f'o{i}.o' for i in range(4)],'Outputs':['Library/GameAssembly.dylib']},{'Annotation':'Copy','Inputs':['Library/GameAssembly.dylib'],'Outputs':['Build/GameAssembly.dylib']}]; return root,{'Nodes':nodes}
    def derive(self,g,release=False): root,_=self.graph(release); return h.derive_graph_evidence(g,root,root/'Build/GameAssembly.dylib',CONFIG,{},expected_feature=True,domain_policy=h.H1_APPLE_BEE_DOMAIN_POLICY)
    def test_split(self): _,g=self.graph(); r=self.derive(g); self.assertEqual({'runtime':1,'bdwgc':1,'zlib':2},{x['name']:x['unitCount'] for x in r['macroDomains']}); self.assertEqual(('1','0'),(r['il2cppDebug'],r['ndebug']))
    def test_release(self): _,g=self.graph(True); r=self.derive(g,True); self.assertEqual(('0','1'),(r['il2cppDebug'],r['ndebug']))
    def test_aux_mismatch_rejected(self):
        _,g=self.graph(); g['Nodes'][3]['Action']=g['Nodes'][3]['Action'].replace(' -c ',' -DIL2CPP_DEBUG=1 -c ')
        with self.assertRaisesRegex(ValueError,'domain disagrees internally'): self.derive(g)
    def test_unknown_rejected(self):
        _,g=self.graph(); old='/project/HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/external/zlib/adler32.c'; g['Nodes'][2]['Inputs']=['/other/adler32.c']; g['Nodes'][2]['Action']=g['Nodes'][2]['Action'].replace(old,'/other/adler32.c')
        with self.assertRaisesRegex(ValueError,'Unreviewed Apple'): self.derive(g)
    def test_link_relation_required(self):
        _,g=self.graph(); g['Nodes'][4]['Inputs'].remove('o2.o')
        with self.assertRaisesRegex(ValueError,'direct input'): self.derive(g)
if __name__=='__main__': unittest.main()
'''))
Path("Tools/AssemblyShadow/tests/test_h1_plan_stage_retention.py").write_text(textwrap.dedent(r'''import json,tempfile,unittest
from pathlib import Path
from unittest import mock
import h1_native_capture as n
class Tests(unittest.TestCase):
    def test_capture_retains_plan_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=root/'project'; (project/'Library/Bee').mkdir(parents=True); native=project/'Build/GameAssembly.dylib'; native.parent.mkdir(); native.write_bytes(b'n'); config=project/'config.h'; config.write_text('#define IL2CPP_DEBUG 1\n#define IL2CPP_DEVELOPMENT 0\n'); graph={'Nodes':[{'Annotation':'Copy','Inputs':[],'Outputs':[str(native)]}]}; (project/'Library/Bee/Player.dag.json').write_text(json.dumps(graph)); request={'projectRoot':str(project),'inputSnapshotHash':'1'*64,'nativeLibraryPath':str(native),'nativeLibrarySha256':n.digest(native),'sourcePinSha256':'2'*64,'before':{'entries':[]},'il2cppConfigPath':str(config),'featureEnabled':True,'cppConfiguration':'Debug','buildId':'H1Count-On-Debug','buildGuid':'g'}; out=root/'out'
            with mock.patch.object(n.pch,'has_pch',return_value=True),mock.patch.object(n.pch,'plan',side_effect=ValueError('boom')):
                with self.assertRaisesRegex(ValueError,'boom'): n.capture(request,out)
            self.assertTrue((out/'capture-failure.json').is_file()); self.assertTrue((out/'bee-action-graph.json').is_file()); self.assertFalse((out/'h1-compiler-provenance.json').exists())
if __name__=='__main__': unittest.main()
'''))
Path("Documents/AgentHandoff/primary-bee-fix-33543").mkdir(parents=True,exist_ok=True)
Path("Documents/AgentHandoff/primary-bee-fix-33543/STATIC_REVIEW.md").write_text("# Primary static review\n\nThe authenticated failure archive proves the 16-action split is exactly 2 BDWGC + 14 zlib C sources, all direct GameAssembly link inputs. Classification is by source ownership, never node number, language, or macro value. Runtime/PCH remains build-profile authoritative; BDWGC/zlib remain separately fail-closed. Unknown roots fail. Requested feature/count defines, compiler/SDK identity, selected-output reachability and direct link membership remain mandatory. Capture now retains request/graph/config/input inventory before plan validation and cannot emit a success receipt on planning failure. This is static/tool review only; V01-V05 remain required.\n")
