#!/usr/bin/env python3
"""Replay diagnostics into a new, bounded root; never repair an old receipt."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import h1_native_capture as n
import h1_pch_provenance as p
from h1_capture_attempt import Attempt, encode
from h1_macro_domain_census import inventory as macro_census


def diagnose(request_path, graph_path, output):
    output = Path(output)
    with Attempt(output, 'diagnostic-replay').guard() as attempt:
        summary = {'kind': 'H1PchDiagnosticReplay', 'status': 'Blocked', 'diagnosticOnly': True,
            'freshBuildClaim': False, 'humanGatePassed': False, 'mayEnterR02': False}
        try:
            attempt.stage('request-and-graph-retention')
            request_bytes = attempt.read_file(Path(request_path), 'original-request')
            graph_bytes = attempt.read_file(Path(graph_path), 'original-dag')
            request_path = n.canonical_file(str(request_path)); graph_path = n.canonical_file(str(graph_path))
            p.write(output / 'original-request.json', request_bytes)
            p.write(output / 'original-graph.json', graph_bytes)
            request = json.loads(request_bytes.decode('utf-8-sig'), object_pairs_hook=n.unique_pairs)
            graph = json.loads(graph_bytes.decode('utf-8-sig'), object_pairs_hook=n.unique_pairs)
            summary.update(requestSha256=p.sha(request_bytes), graphSha256=p.sha(graph_bytes))
            root = Path(request['projectRoot'])
            p.a.need(root.is_absolute() and root == root.resolve(strict=True),
                     'Original project root is unavailable; do not rewrite the receipt')
            config = n.canonical_file(request['il2cppConfigPath'])
            config_bytes = attempt.read_file(config, 'il2cpp-config')
            attempt.stage('declared-input-retention')
            attempt.retain_declared_inputs(graph, root)
            attempt.stage('request-validation')
            native = n.canonical_file(request['nativeLibraryPath'])
            p.a.need(n.digest(native) == request['nativeLibrarySha256'], 'Selected failed native output bytes differ')
            p.a.need(request['cppConfiguration'] in ('Debug', 'Release') and type(request['featureEnabled']) is bool,
                     'Original build mode absent')
            attempt.stage('response-closure')
            responses = n.collect_responses(graph, root, attempt=attempt)
            p.write(output / 'macro-domain-census.json', encode(macro_census(graph, root, native, responses)))
            attempt.stage('planning', planning='Started')
            blueprint = p.plan(graph, root, native, config_bytes.decode('utf-8'), responses, request['featureEnabled'])
            binding = {**{k: request[k] for k in p.BINDINGS}, 'graphSha256': p.sha(graph_bytes),
                'projectRoot': str(root), 'featureEnabled': request['featureEnabled'],
                'cppConfiguration': request['cppConfiguration'], 'diagnosticOnly': True,
                'replayedRequestSha256': p.sha(request_bytes)}
            attempt.stage('pch-execution', planning='Completed',
                          pchReplay='InvokedSeeChildArtifacts', macroProbes='InvokedSeeChildArtifacts',
                          transitivePchHeaders='SeePchCaptureArtifacts')
            proof = p.capture(blueprint, graph, root, str(config), binding, output / 'pch', responses)
            p.verify(proof, graph, root, native, config_bytes.decode('utf-8'), responses, binding)
            p.a.need(request_path.read_bytes() == request_bytes and graph_path.read_bytes() == graph_bytes and
                     config.read_bytes() == config_bytes, 'Original attempt changed during diagnosis')
            summary.update(status='DiagnosticReplayVerifiedNotBuildAccepted', proofPath=str(output / 'pch/pch-proof.json'),
                           proofSha256=n.digest(output / 'pch/pch-proof.json'))
            attempt.stage('diagnostic-publication', pchReplay='Completed', macroProbes='Completed',
                          transitivePchHeaders='SeeVerifiedPchProof')
        except (OSError, ValueError, KeyError, TypeError) as error:
            summary.update(error=str(error), errorType=type(error).__name__, failedStage=attempt.state['stage'])
            try:
                p.write(output / 'diagnostic-result.json', encode(summary))
            except (OSError, ValueError) as secondary:
                error.add_note('Diagnostic summary write also failed: ' + str(secondary))
            raise
        p.write(output / 'diagnostic-result.json', encode(summary))
        attempt.finish('DiagnosticReplayVerifiedNotBuildAccepted')
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True); parser.add_argument('--graph', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(diagnose(args.request, args.graph, args.output), indent=2)); return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Blocked diagnostic replay: ' + str(error), file=__import__('sys').stderr); raise SystemExit(1)
