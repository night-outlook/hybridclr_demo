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
from h1_capture_attempt import Attempt, encode
from h1_macro_domain_census import inventory as macro_census


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


def collect_responses(graph: dict, root: Path, *, attempt=None) -> dict[str, bytes]:
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
            if attempt is not None: attempt.keep_bytes(source, data, "response-file")
            actions.need(len(contents) <= 16384, "Too many response files")
            text = data.decode("utf-8-sig")
            visit(actions.split(text) if text.strip() else [], active + (source,))
    for node in graph.get("Nodes", []):
        if type(node) is dict and str(node.get("Annotation", "")).startswith(("C_Mac_arm64", "Link_Mac_arm64")) and node.get("Action"):
            visit(actions.split(node["Action"]))
    return contents


def capture(request: dict, evidence_root: Path) -> dict:
    """Capture API: its supplied object is labeled as re-encoded, not original bytes."""
    with Attempt(evidence_root, 'fresh-native-capture-api').guard() as attempt:
        attempt.keep_bytes('caller-supplied-object', encode(request), 'reencoded-request-object')
        report = _capture(request, attempt)
        attempt.finish('CapturedNotRuntimeAccepted')
        return report


def _capture(request: dict, attempt: Attempt) -> dict:
    evidence_root = attempt.root
    attempt.stage('request-validation')
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
        raw = attempt.read_file(path, 'candidate-dag')
        if old.get(str(path)) == hashlib.sha256(raw).hexdigest(): continue
        graph = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_pairs)
        if any(type(n) is dict and str(native) in [actions.resolve(root, p) for p in n.get('Outputs', [])]
               for n in graph.get('Nodes', [])):
            matches.append((path, raw, graph))
    actions.need(len(matches) == 1, "Expected one changed selected-output DAG; preserve the failed attempt and rebuild, do not relabel old DAGs")
    graph_path, raw_graph, graph = matches[0]
    config_path = canonical_file(request['il2cppConfigPath'])
    raw_config = attempt.read_file(config_path, 'il2cpp-config')
    # Retain raw inputs before interpreting any action or macro-domain policy.
    retained_graph = evidence_root / 'bee-action-graph.json'
    retained_config = evidence_root / 'il2cpp-config.h'
    write_new(retained_graph, raw_graph); write_new(retained_config, raw_config)
    attempt.stage('declared-input-retention')
    attempt.retain_declared_inputs(graph, root)
    attempt.stage('response-closure')
    responses = collect_responses(graph, root, attempt=attempt)
    write_new(evidence_root / 'macro-domain-census.json', encode(macro_census(graph, root, native, responses)))
    attempt.stage('planning', planning='Started')
    pch_plan = pch.plan(graph, root, native, raw_config.decode('utf-8'), responses, request.get("featureEnabled")) if pch.has_pch(graph, root, responses) else None
    derived = pch_plan['derived'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode('utf-8'), responses, expected_feature=request.get("featureEnabled"))
    attempt.stage('profile-validation', planning='Completed')
    actions.need(set(derived['responseSources']) == set(responses), 'Response closure differs')
    expected = {'Debug': ('1','0'), 'Release': ('0','1')}
    cpp = request.get('cppConfiguration')
    actions.need(cpp in expected and (derived['il2cppDebug'], derived['ndebug']) == expected[cpp],
                 'Effective compiler assertion/debug profile differs from requested C++ configuration')
    attempt.stage('toolchain-identity')
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
    retained_sdk = evidence_root / 'SDKSettings.plist'
    write_new(retained_sdk, sdk_bytes)
    response_rows = []
    for i, (source, data) in enumerate(sorted(responses.items())):
        retained = evidence_root / 'response-files' / ('%04d.rsp' % i)
        write_new(retained, data)
        response_rows.append({'sourcePath': source, 'retainedPath': str(retained),
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    pch_path = pch_hash = ""
    if pch_plan is not None:
        attempt.stage('pch-execution', pchReplay='InvokedSeeChildArtifacts', macroProbes='InvokedSeeChildArtifacts',
                      transitivePchHeaders='SeePchCaptureArtifacts')
        binding = {**{k: request[k] for k in pch.BINDINGS}, "graphSha256": hashlib.sha256(raw_graph).hexdigest(),
                   "projectRoot": str(root), "featureEnabled": request['featureEnabled'], "cppConfiguration": cpp}
        proof = pch.capture(pch_plan, graph, root, str(config_path), binding, evidence_root / 'pch', responses=responses)
        pch.verify(proof, graph, root, native, raw_config.decode('utf-8'), responses, binding)
        pch_path = str(evidence_root / 'pch/pch-proof.json'); pch_hash = digest(Path(pch_path))
        attempt.stage('input-recheck', pchReplay='Completed', macroProbes='Completed',
                      transitivePchHeaders='SeeVerifiedPchProof')
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
        'macroEvidence': 'All compiler actions require exact feature/count defines and selected compiler/SDK identity. A schema-2 proof exhaustively binds linked runtime, bdwgc and zlib domains; summary debug fields describe the IL2CPP runtime domain, not external-library macros. Every domain context has raw syntax/macro probes. NDEBUG uses definedness. Other forced-input routes remain prohibited.',
        'projectRoot': str(root), 'responseFiles': response_rows, 'pchProofPath': pch_path, 'pchProofSha256': pch_hash}


def capture_request(request_path: Path, evidence_root: Path) -> dict:
    """CLI owner: preserve the exact request before parsing or planning."""
    with Attempt(evidence_root, 'fresh-native-capture').guard() as attempt:
        attempt.stage('request-read')
        raw_request = attempt.read_file(request_path, 'original-request')
        request_path = canonical_file(str(request_path))
        attempt.stage('request-parse')
        request = json.loads(raw_request.decode('utf-8-sig'), object_pairs_hook=unique_pairs)
        report = _capture(request, attempt)
        actions.need(request_path.read_bytes() == raw_request, 'Capture request changed')
        attempt.stage('capture-publication')
        write_new(evidence_root / 'h1-compiler-provenance.json', (json.dumps(report, indent=2)+'\n').encode())
        attempt.finish('CapturedNotRuntimeAccepted')
        return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True); p.add_argument('--evidence-root', type=Path, required=True)
    a=p.parse_args()
    capture_request(a.request, a.evidence_root)
    print(json.dumps({'status':'CapturedNotRuntimeAccepted', 'path':str(a.evidence_root / 'h1-compiler-provenance.json')}))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print('Failed: ' + str(error), file=__import__('sys').stderr); raise SystemExit(1)
