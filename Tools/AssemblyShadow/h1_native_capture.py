"""Capture fresh Bee action provenance without reconstructing historical evidence.

The Unity build adapter supplies a pre-build DAG inventory. Only a changed DAG
that reaches the selected native library can be selected. Response files and
the configuration header are copied, so later builds cannot mutate the proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess

import h1_compiler_actions as actions
import h1_pch_provenance as pch



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
        tmp.write_text(json.dumps(self.state, indent=2) + "\n")
        os.replace(tmp, self.root / "attempt-state.json")
    def stage(self, name, **values):
        self.state.update(values); self.state["stage"] = name; self.save()
    def failure(self, error):
        target = self.root / "capture-failure.json"
        if not target.exists():
            write_new(target, (json.dumps({**self.state, "status": "Failed",
                       "errorType": type(error).__name__, "error": str(error)}, indent=2) + "\n").encode())


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
    write_new(evidence_root / "preplan-input-inventory.json", (json.dumps(rows, indent=2) + "\n").encode())

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        actions.need(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_file(value: str) -> Path:
    path = Path(value)
    actions.need(path.is_absolute() and path == path.resolve(strict=True) and path.is_file() and not path.is_symlink(),
                 "Expected canonical file: " + str(path))
    return path


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def collect_responses(graph: dict, root: Path) -> dict[str, bytes]:
    """Capture the transitive response closure once, preserving source locators."""
    contents = {}
    def visit(tokens: list[str], active=()):
        actions.need(len(active) <= actions.MAX_RESPONSE_DEPTH, "Response-file nesting limit exceeded")
        for token in tokens:
            if not token.startswith("@"): continue
            source = actions.resolve(root, token[1:])
            actions.need(source not in active, "Response-file cycle")
            if source in contents: continue
            path = canonical_file(source)
            actions.need(path.stat().st_size <= actions.MAX_RESPONSE_BYTES, "Response file exceeds capture bound")
            data = path.read_bytes(); contents[source] = data
            actions.need(len(contents) <= 16384, "Too many response files")
            text = data.decode("utf-8-sig")
            visit(actions.split(text) if text.strip() else [], active + (source,))
    for node in graph.get("Nodes", []):
        if type(node) is dict and str(node.get("Annotation", "")).startswith(("C_Mac_arm64", "Link_Mac_arm64")) and node.get("Action"):
            visit(actions.split(node["Action"]))
    return contents


def capture(request: dict, evidence_root: Path, *, original_request: bytes | None = None) -> dict:
    evidence_root = Path(evidence_root)
    attempt = CaptureAttempt(evidence_root, "H1NativeCaptureAttempt")
    if original_request is None:
        original_request = (json.dumps(request, sort_keys=True, separators=(",", ":")) + "\n").encode()
    write_new(evidence_root / "capture-request.json", original_request)
    try:
        attempt.stage("request-validation")
        return _capture_impl(request, evidence_root, attempt)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        attempt.failure(error); raise


def _capture_impl(request: dict, evidence_root: Path, attempt: CaptureAttempt) -> dict:
    root = Path(request["projectRoot"])
    actions.need(root.is_absolute() and root == root.resolve(strict=True), "Project root is not canonical")
    for field in ("inputSnapshotHash", "nativeLibrarySha256", "sourcePinSha256"):
        value = request.get(field)
        actions.need(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value), "Invalid " + field)
    native = canonical_file(request["nativeLibraryPath"])
    actions.need(digest(native) == request["nativeLibrarySha256"], "Native library hash differs before capture")
    old_rows = request.get("before", {}).get("entries")
    actions.need(type(old_rows) is list and all(type(row) is dict for row in old_rows), "Pre-build graph inventory missing")
    old = {row["path"]: row["sha256"] for row in old_rows}
    actions.need(len(old) == len(old_rows), "Duplicate pre-build graph entries")
    attempt.stage('graph-selection')
    matches = []
    for path in sorted((root / 'Library/Bee').glob('Player*.dag.json')):
        canonical_file(str(path))
        raw = path.read_bytes()
        if old.get(str(path)) == hashlib.sha256(raw).hexdigest(): continue
        graph = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_pairs)
        if any(type(n) is dict and str(native) in [actions.resolve(root, p) for p in n.get('Outputs', [])]
               for n in graph.get('Nodes', [])):
            matches.append((path, raw, graph))
    actions.need(len(matches) == 1, "Expected one changed selected-output DAG; preserve the failed attempt and rebuild, do not relabel old DAGs")
    graph_path, raw_graph, graph = matches[0]
    config_path = canonical_file(request['il2cppConfigPath'])
    raw_config = config_path.read_bytes()
    retained_graph = evidence_root / 'bee-action-graph.json'; retained_config = evidence_root / 'il2cpp-config.h'
    write_new(retained_graph, raw_graph); write_new(retained_config, raw_config)
    attempt.stage('preplan-input-retention'); _retain_plan_inputs(graph, root, evidence_root)
    responses = collect_responses(graph, root); response_rows = []
    for i, (source, data) in enumerate(sorted(responses.items())):
        retained = evidence_root / 'response-files' / ('%04d.rsp' % i); write_new(retained, data)
        response_rows.append({'sourcePath': source, 'retainedPath': str(retained), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    attempt.stage('planning')
    domain_policy = request.get("macroDomainPolicy")
    actions.need(domain_policy in (None, actions.H1_APPLE_BEE_DOMAIN_POLICY), "Unknown requested macro-domain policy")
    pch_plan = pch.plan(graph, root, native, raw_config.decode('utf-8'), responses, request.get("featureEnabled"), domain_policy) if pch.has_pch(graph, root, responses) else None
    derived = pch_plan['derived'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode('utf-8'), responses, expected_feature=request.get("featureEnabled"), domain_policy=domain_policy)
    attempt.stage('planning-complete')
    actions.need(set(derived['responseSources']) == set(responses), 'Response closure differs')
    expected = {'Debug': ('1','0'), 'Release': ('0','1')}
    cpp = request.get('cppConfiguration')
    actions.need(cpp in expected and (derived['il2cppDebug'], derived['ndebug']) == expected[cpp],
                 'Effective compiler assertion/debug profile differs from requested C++ configuration')
    compiler = Path(derived['compilerPath'])
    actions.need(compiler.is_absolute() and compiler.is_file(), 'Selected compiler unavailable')
    sdk_settings = Path(derived['sdkPath']) / 'SDKSettings.plist'
    actions.need(sdk_settings.is_file(), 'Selected SDKSettings.plist unavailable')
    compiler_hash = digest(compiler)
    sdk_bytes = sdk_settings.read_bytes()
    settings = plistlib.loads(sdk_bytes)
    sdk_version = settings.get('Version')
    actions.need(isinstance(sdk_version, (str,int,float)) and str(sdk_version), 'Selected SDK version is absent; do not query a different default SDK')
    run = subprocess.run([str(compiler), '--version'], capture_output=True, text=True, timeout=30, check=True)
    compiler_version = run.stdout + (('\n' + run.stderr) if run.stderr else '')
    actions.need(bool(compiler_version.strip()), 'Empty selected compiler version')
    retained_sdk = evidence_root / 'SDKSettings.plist'; write_new(retained_sdk, sdk_bytes)
    pch_path = pch_hash = ""
    if pch_plan is not None:
        binding = {**{k: request[k] for k in pch.BINDINGS}, "graphSha256": hashlib.sha256(raw_graph).hexdigest(),
                   "projectRoot": str(root), "featureEnabled": request['featureEnabled'], "cppConfiguration": cpp,
                   "macroDomainPolicy": domain_policy}
        attempt.stage('pch-execution', pchReplay='Invoked', macroProbes='Invoked')
        proof = pch.capture(pch_plan, graph, root, str(config_path), binding, evidence_root / 'pch', responses=responses)
        pch.verify(proof, graph, root, native, raw_config.decode('utf-8'), responses, binding)
        pch_path = str(evidence_root / 'pch/pch-proof.json'); pch_hash = digest(Path(pch_path))
    for path, data in [(graph_path, raw_graph), (config_path, raw_config), (sdk_settings, sdk_bytes)]:
        actions.need(digest(path) == hashlib.sha256(data).hexdigest(), 'Build input changed during capture: ' + str(path))
    actions.need(digest(native) == request['nativeLibrarySha256'] and digest(compiler) == compiler_hash, 'Compiler/native artifact changed during capture')
    for source, data in responses.items():
        actions.need(digest(Path(source)) == hashlib.sha256(data).hexdigest(), 'Response changed during capture: ' + source)
    return {'schemaVersion': 1, 'buildId': request['buildId'], 'buildGuid': request['buildGuid'],
        'inputSnapshotHash': request['inputSnapshotHash'], 'nativeLibraryPath': str(native),
        'nativeLibrarySha256': request['nativeLibrarySha256'], 'sourcePinSha256': request['sourcePinSha256'],
        'beeActionGraphPath': str(retained_graph), 'beeActionGraphSha256': hashlib.sha256(raw_graph).hexdigest(),
        'beeLinkOutputPath': derived['beeLinkOutputPath'], 'compileActionCount': derived['compileActionCount'],
        'linkActionCount': derived['linkActionCount'], 'compilerPath': str(compiler),
        'compilerSha256': compiler_hash, 'compilerVersion': compiler_version,
        'sdkPath': derived['sdkPath'], 'sdkVersion': str(sdk_version),
        'sdkSettingsPath': str(retained_sdk), 'sdkSettingsSha256': hashlib.sha256(sdk_bytes).hexdigest(),
        'il2cppConfigPath': str(retained_config), 'il2cppConfigSha256': hashlib.sha256(raw_config).hexdigest(),
        'il2cppDebug': derived['il2cppDebug'], 'ndebug': derived['ndebug'],
        'il2cppDevelopment': derived['il2cppDevelopment'],
        'macroEvidence': 'Source-owned Apple Bee domains: runtime/PCH is build-profile authoritative; BDWGC and zlib direct-link domains are independently consistent.',
        'macroDomainEvidence': json.dumps(derived['macroDomains'], sort_keys=True, separators=(',', ':')),
        'macroDomainPolicy': derived['macroDomainPolicy'],
        'projectRoot': str(root), 'responseFiles': response_rows, 'pchProofPath': pch_path, 'pchProofSha256': pch_hash}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True); p.add_argument('--evidence-root', type=Path, required=True)
    a=p.parse_args(); request_path=canonical_file(str(a.request)); raw_request=request_path.read_bytes(); before=hashlib.sha256(raw_request).hexdigest()
    report=capture(json.loads(raw_request.decode('utf-8-sig'), object_pairs_hook=unique_pairs), a.evidence_root, original_request=raw_request)
    actions.need(digest(request_path)==before, 'Capture request changed')
    write_new(a.evidence_root / 'h1-compiler-provenance.json', (json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps({'status':'CapturedNotRuntimeAccepted', 'path':str(a.evidence_root / 'h1-compiler-provenance.json')}))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print('Failed: ' + str(error), file=__import__('sys').stderr); raise SystemExit(1)
