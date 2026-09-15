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


def capture(request: dict, evidence_root: Path) -> dict:
    root = Path(request["projectRoot"])
    actions.need(root.is_absolute() and root == root.resolve(strict=True), "Project root is not canonical")
    actions.need(evidence_root.is_absolute() and evidence_root == evidence_root.resolve() and not evidence_root.exists(),
                 "Evidence directory must be new and canonical")
    for field in ("inputSnapshotHash", "nativeLibrarySha256", "sourcePinSha256"):
        value = request.get(field)
        actions.need(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value), "Invalid " + field)
    native = canonical_file(request["nativeLibraryPath"])
    actions.need(digest(native) == request["nativeLibrarySha256"], "Native library hash differs before capture")
    old_rows = request.get("before", {}).get("entries")
    actions.need(type(old_rows) is list and all(type(row) is dict for row in old_rows), "Pre-build graph inventory missing")
    old = {row["path"]: row["sha256"] for row in old_rows}
    actions.need(len(old) == len(old_rows), "Duplicate pre-build graph entries")
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
    responses = collect_responses(graph, root)
    pch_plan = pch.plan(graph, root, native, raw_config.decode('utf-8'), responses, request.get("featureEnabled")) if pch.has_pch(graph, root, responses) else None
    derived = pch_plan['derived'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode('utf-8'), responses, expected_feature=request.get("featureEnabled"))
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
    # No output is created until structural selection and macro interpretation pass.
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
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    pch_path = pch_hash = ""
    if pch_plan is not None:
        binding = {**{k: request[k] for k in pch.BINDINGS}, "graphSha256": hashlib.sha256(raw_graph).hexdigest(),
                   "projectRoot": str(root), "featureEnabled": request['featureEnabled'], "cppConfiguration": cpp}
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
        'macroEvidence': 'Per-unit ordered -D/-U intent; NDEBUG uses definedness. PCH contexts additionally require the bound raw syntax/macro proof when pchProofPath is nonempty. Other forced-input routes remain prohibited.',
        'projectRoot': str(root), 'responseFiles': response_rows, 'pchProofPath': pch_path, 'pchProofSha256': pch_hash}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True); p.add_argument('--evidence-root', type=Path, required=True)
    a=p.parse_args(); request_path=canonical_file(str(a.request)); before=digest(request_path)
    report=capture(read_json(request_path), a.evidence_root)
    actions.need(digest(request_path)==before, 'Capture request changed')
    write_new(a.evidence_root / 'h1-compiler-provenance.json', (json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps({'status':'CapturedNotRuntimeAccepted', 'path':str(a.evidence_root / 'h1-compiler-provenance.json')}))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print('Failed: ' + str(error), file=__import__('sys').stderr); raise SystemExit(1)
