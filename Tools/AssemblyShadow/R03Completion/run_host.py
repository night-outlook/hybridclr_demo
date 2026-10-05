#!/usr/bin/env python3
"""Completion contracts through the existing owned-command wrapper, not Player acceptance."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
from run_local import Batch, git
from resource_capabilities import host_contracts as capability_contracts
from fixture_contracts import constructor_contracts
import fixed_image_inputs as fixed_images
import layout_identity
import editor_contract
import reference_binding
import sidecar_replay


def qualification(batch):
    project = HERE / 'QualificationTests/QualificationTests.csproj'
    binary, intermediate = batch.root / 'bin/qualification', batch.root / 'obj/qualification'
    batch.command(build_arguments(project, binary, intermediate, batch.workspace / 'hybridclr_unity'))
    output = batch.root / 'qualification'
    batch.command(['dotnet', binary / 'QualificationTests.dll', '--output', output])
    data = loads((output / 'results.json').read_text())
    require(data['kind'] == 'R03QualificationContracts' and data['result'] == 'Passed' and data['failures'] == 0,
            'Actual compiled qualification contracts must pass')
    require(len(data['cases']) == len({row['id'] for row in data['cases']}) == 32 and
            all(row['result'] == 'Passed' for row in data['cases']), 'All 32 source-defined qualification cases')
    require(data['runtimeProofExecuted'] is False and data['expansionAuthorized'] is False, 'Analysis does not authorize expansion')
    for entry in data['inventory']:
        path = Path(entry['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'Fixture path')
        require(sha(output / path) == entry['sha256'] and (output / path).stat().st_size == entry['size'], 'Qualification fixture hash')
    return {'result': str(output / 'results.json'), 'sha256': sha(output / 'results.json'),
            'cases': 32, 'classification': 'RealDllStaticAnalysis', 'runtimeProofExecuted': False, 'expansionAuthorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--reference-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace, root = args.workspace.resolve(), args.output.resolve()
    require(HERE == workspace / 'hybridclr_demo/Tools/AssemblyShadow/R03Completion', 'Owning source directory')
    require(not root.exists(), 'Unused host evidence root')
    pins = loads((HERE / 'source-pins.json').read_text())
    require(git(workspace / 'hybridclr_unity', 'rev-parse', 'HEAD') == pins['hybridclr_unity'], 'Exact candidate package')
    root.mkdir(parents=True)
    batch = object.__new__(Batch)
    batch.workspace, batch.root, batch.command_count = workspace, root, 0
    batch.cells, batch.outputs, batch.failed = [], {}, False
    batch.cell('completion-tool-contracts', lambda: {'commandReceipt': batch.command([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', HERE, '-p', 'test_*.py', '-v']), 'scope': 'Synthetic tooling contracts, not Player evidence'})
    batch.cell('editor-source-scope', lambda: editor_contract.preflight(workspace / 'hybridclr_demo', workspace / 'hybridclr_unity', pins['hybridclr_unity'], root / 'editor-source-scope'))
    batch.cell('fixture-constructor-contracts', lambda: constructor_contracts(batch))
    batch.cell('capability-profile-contracts', lambda: capability_contracts(batch))
    batch.cell('fixed-image-origin', lambda: fixed_images.authenticate_origin(batch))
    batch.cell('fixed-image-guards', lambda: fixed_images.host_contracts(batch))
    batch.cell('layout-identity', lambda: layout_identity.host_contracts(batch))
    batch.cell('captured-sidecars', lambda: sidecar_replay.verify(workspace / 'hybridclr_demo', root / 'captured-sidecar-replay.json'))
    batch.cell('reference-binding', lambda: reference_binding.host_contracts(batch))
    batch.cell('qualification', lambda: qualification(batch))
    batch.cell('original-verifier-contracts', batch.python_tests)
    batch.cell('original-baseline-graph', lambda: batch.managed('HostTests', 'baseline-graph', args.reference_package.resolve(), 'baseline'))
    batch.cell('original-candidate-graph', lambda: batch.managed('HostTests', 'candidate-graph', phase='candidate'))
    batch.cell('original-admission', lambda: batch.managed('AdmissionTests', 'admission'))
    summary = {'kind': 'R03CompletionHostContracts', 'schemaVersion': 1, 'result': 'Failed' if batch.failed else 'Passed',
               'cells': batch.cells, 'sourcePins': pins, 'unityRun': False, 'playerRun': False, 'expansionAuthorized': False}
    write(root / 'results.json', summary)
    return 1 if batch.failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
