#!/usr/bin/env python3
"""Prove an immutable profile-1 Player refuses profile-2 inputs before configuration.

This tests the embedded baseline/runtime identity boundary. It does not claim
that an old binary implements profile-2 internal calls. Capability negotiation
is tested independently by the managed runtime contract tests.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import time

import m07_results as gate
from r00_player_inputs import verify_inputs
from shadow_tools import require

spec = importlib.util.spec_from_file_location('m07_launch', Path(__file__).with_name('run-m07-players.py'))
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


def old_pair(fixture, on, off, replay):
    manifest, baseline, fixtures, rejected, resources = gate.verify_inputs(fixture)
    require(baseline['metadataEncodingProfile']['profileVersion'] == 1, 'Old baseline must use profile 1')
    gate.prepare_fixture_resources(manifest, baseline, fixtures, resources)
    build = gate.verify_player(on, manifest, baseline, resources, 'NativeOn')
    gate.verify_player(off, manifest, baseline, resources, 'NativeOff')
    gate.verify_replay(replay, manifest, baseline, fixtures, rejected, build, resources)
    return baseline, build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('project-root', 'fixture-manifest', 'on-build', 'off-build', 'replay-receipt',
                 'old-fixture-manifest', 'old-on-build', 'old-off-build', 'old-replay-receipt', 'output-root'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    project = args.project_root
    require(project.is_absolute() and project == project.resolve(strict=True), 'Canonical project required')
    require(1 <= args.timeout <= 900, 'Timeout must be bounded')
    paths = {name: launch.canonical_file(getattr(args, name)) for name in
             ('fixture_manifest', 'on_build', 'off_build', 'replay_receipt', 'old_fixture_manifest',
              'old_on_build', 'old_off_build', 'old_replay_receipt')}
    current = verify_inputs(project, paths['fixture_manifest'], paths['on_build'], paths['off_build'], paths['replay_receipt'])
    require(current['baseline']['metadataEncodingProfile2']['profileVersion'] == 2, 'New baseline must use profile 2')
    old, build = old_pair(paths['old_fixture_manifest'], paths['old_on_build'], paths['old_off_build'], paths['old_replay_receipt'])
    require(old['runtimeAbiHash'] != current['baseline']['runtimeAbiHash'], 'Runtime identities must differ')
    inputs = launch.collect_inputs(paths['fixture_manifest'], paths['replay_receipt'], (paths['on_build'], paths['off_build']))
    inputs |= launch.collect_inputs(paths['old_fixture_manifest'], paths['old_replay_receipt'], (paths['old_on_build'], paths['old_off_build']))
    inputs.add(Path(__file__).resolve())
    before = {str(path): launch.digest(path) for path in sorted(inputs)}
    output = launch.canonical_new_child(args.output_root, project / '_temp/AssemblyShadow', 'Compatibility output')
    output.mkdir()
    result_path, log, console = (output / name for name in ('old-player-result.json', 'unity.log', 'console.log'))
    command = [str(launch.executable_for(build['output'])), '-batchmode', '-nographics',
               '-shadowM07Mode', 'T07-03-FullClosure-P03', '-shadowM07Fixtures', str(paths['fixture_manifest']),
               '-shadowM07PlayerReceipt', str(paths['old_on_build']), '-shadowM07Result', str(result_path), '-logFile', str(log)]
    started = time.time()
    timed_out = False
    with console.open('xb') as stream:
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
        try:
            code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait(timeout=15)
    after = {str(path): launch.digest(path) for path in sorted(inputs)}
    error = ''
    try:
        result = launch.read_object(result_path)
        require(not timed_out and code == 1 and before == after, 'Expected clean refusal with immutable inputs')
        require(result['result'] == 'Failed' and result['processId'] == process.pid and result['il2cpp'] is True and
                result['platform'] == 'OSXPlayer' and result['buildGuid'] == build['player']['buildGuid'] and
                result['runtimeAbiHash'] == old['runtimeAbiHash'] and result['baselineBuildId'] == old['baselineBuildId'],
                'Refusal is not bound to the old Player')
        require('M07 embedded baseline/runtime ABI identity differs.' in result['error'], 'Unexpected refusal reason')
        for field in ('stageOrder', 'stageResults', 'snapshots', 'bundles', 'assets', 'scenes'):
            require(result[field] == [], 'Old Player progressed past input refusal: ' + field)
        for field in ('configureCode', 'beginCode', 'commitCode'):
            require(result[field] in ('', None), 'Old Player invoked ' + field)
        require(result['businessResourceLoadStarted'] is False and log.is_file(), 'Unexpected resource load or missing log')
        passed = True
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as problem:
        passed, error = False, str(problem)
    receipt = dict(schemaVersion=1, kind='R01BOldPlayerIdentityRejection', result='Passed' if passed else 'Failed',
                   boundary='Embedded profile-1 baseline/runtime identity refuses profile-2 inputs before Configure and Stage',
                   command=command, processId=process.pid, startedAtUnix=started, durationSeconds=time.time()-started,
                   exitCode=code, timedOut=timed_out, oldSourcePins=old['sourcePins'], newSourcePins=current['sourcePins'],
                   inputsBefore=before, inputsAfter=after, inputsUnchanged=before == after, error=error,
                   outputs=[dict(path=str(p), sha256=launch.digest(p)) for p in (result_path, log, console) if p.is_file()])
    (output / 'old-player-rejection-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['result'] + (': ' + error if error else ''), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
