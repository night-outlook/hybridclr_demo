#!/usr/bin/env python3
"""Host-only regression of the actual Local Batch.command/managed call chain.

This deliberately constructs only the host-method receiver, without Unity or
four-repository Local authority. It cannot emit a Local batch PASS or call execute.
"""
import argparse
import json
import platform
from pathlib import Path
import re

from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import BUILD_ENV, BUILD_FLAGS, POLICY, build_arguments
from run_local import Batch, ROOT, REFERENCE_PACKAGE, git


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--reference-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace, output = args.workspace.resolve(), args.output.resolve()
    reference = args.reference_package.resolve()
    require(not output.exists(), 'Host evidence root must be unused')
    require(ROOT == workspace / 'hybridclr_demo/Tools/AssemblyShadow/R03', 'Exact source directory required')
    pins = loads((ROOT / 'source-pins.json').read_text())
    require(git(workspace / 'hybridclr_unity', 'rev-parse', 'HEAD') == pins['hybridclr_unity'], 'Package source pin')
    require(git(reference, 'rev-parse', 'HEAD') == REFERENCE_PACKAGE, 'Reference package pin')
    output.mkdir(parents=True)
    # Test-only receiver: no mocking/reimplementation of command(), managed(),
    # fixtures() or their assertions. Never use this as a Local execution entry.
    batch = object.__new__(Batch)
    batch.workspace, batch.root, batch.command_count = workspace, output / 'execution', 0
    batch.root.mkdir()
    records = []

    def case(name, action):
        row = {'id': name, 'result': 'Failed'}
        try:
            row['evidence'] = action()
            row['result'] = 'Passed'
        except Exception as error:
            row['error'] = str(error)
        records.append(row)
        write(output / (name + '.json'), row)
        print(json.dumps(row), flush=True)

    def sdk():
        batch.command(['dotnet', '--version'])
        observed = (batch.root / 'commands/0001/stdout.log').read_text().strip()
        require(observed == '8.0.318', 'This regression must exercise the Local SDK version: ' + observed)
        batch.command(['dotnet', '--info'])
        return {'version': observed, 'info': 'execution/commands/0002/stdout.log'}

    case('sdk', sdk)
    if records[0]['result'] == 'Passed':
        def contracts():
            evidence = batch.python_tests()
            log = batch.root / 'commands' / ('%04d' % batch.command_count) / 'stderr.log'
            text = log.read_text()
            require(re.search(r'Ran 67 tests in ', text) and '\nOK\n' in text and 'skipped=' not in text,
                    'All 67 tool/process tests must execute without skips')
            return evidence
        case('python-contracts', contracts)
        case('baseline-graph', lambda: batch.managed('HostTests', 'baseline-graph', reference, 'baseline'))
        case('candidate-graph', lambda: batch.managed('HostTests', 'candidate-graph', phase='candidate'))
        case('admission', lambda: batch.managed('AdmissionTests', 'admission'))
        case('player-fixtures', batch.fixtures)
        case('player-api-compile', lambda: batch.command(build_arguments(
            ROOT / 'PlayerApiCompile/PlayerApiCompile.csproj', batch.root / 'bin/player-api',
            batch.root / 'obj/player-api', workspace / 'hybridclr_unity')))

    def audit_commands():
        receipts = sorted((batch.root / 'commands').glob('*/command.json'))
        require(len(receipts) == 12, 'Expected twelve real owned command invocations')
        builds = []
        for path in receipts:
            row = loads(path.read_text())
            require(row['schemaVersion'] == 2 and row['lifetimePolicy'] == POLICY, 'Production lifetime receipt')
            require(row['exitCode'] == 0 and row['timeout'] is False and row['remainingProcessGroup'] is False and
                    row['postCleanupGroupExists'] is False and row['cleanupErrors'] == [] and
                    row['startError'] is None and row['interrupted'] is False, 'Owned command did not finish cleanly')
            for key, value in BUILD_ENV.items():
                require(row['childEnvironmentPolicy'][key] == value, 'Child environment policy')
            for stream in ('stdout', 'stderr'):
                require(sha(path.parent / (stream + '.log')) == row[stream + 'Sha256'], 'Command log binding')
            if row['command'][:2] == ['dotnet', 'build']:
                require(tuple(row['command'][-3:]) == BUILD_FLAGS, 'Managed build flags')
                builds.append(str(path.relative_to(output)))
        require(len(builds) == 5, 'Five actual managed builds required')
        return {'commands': len(receipts), 'managedBuilds': builds, 'noSurvivingProcessGroups': True}

    case('command-audit', audit_commands)
    result = {'schemaVersion': 1, 'kind': 'R03ManagedLifetimeHostEvidence',
              'result': 'Passed' if len(records) == 8 and all(r['result'] == 'Passed' for r in records) else 'Failed',
              'cases': records, 'platform': platform.platform(), 'architecture': platform.machine(),
              'demoCommit': git(workspace / 'hybridclr_demo', 'rev-parse', 'HEAD'),
              'packageCommit': pins['hybridclr_unity'], 'referencePackageCommit': REFERENCE_PACKAGE,
              'unityEditorRun': False, 'il2cppPlayerRun': False, 'runtimeAcceptance': False,
              'R03Accepted': False, 'H2Passed': False}
    write(output / 'results.json', result)
    print(json.dumps(result, indent=2))
    return 0 if result['result'] == 'Passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
