#!/usr/bin/env python3
"""Task-local M05 process capture; this does not replace strict evidence replay."""
import argparse
import hashlib
import json
import plistlib
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path('/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow')
MODES = (
    'T05-01-P01', 'T05-01-P03', 'T05-02-P01', 'T05-02-P03',
    'T05-03-P01', 'T05-03-P03', 'T05-04-EarlyType',
    'T05-05-P01', 'T05-05-P03', 'T05-06-P01', 'T05-07-P03',
    'T05-08-P01', 'T05-08-P03', 'T05-09-LayoutMismatch',
    'T05-10-P01', 'T05-10-P03', 'T05-11-FeatureOff',
    'T05-12-BenchmarkOn', 'T05-13-BenchmarkOff',
)
OFF = {'T05-11-FeatureOff', 'T05-13-BenchmarkOff'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def existing_file(value):
    path = Path(value)
    if not path.is_absolute() or str(path) != str(path.resolve(strict=True)) or not path.is_file():
        raise ValueError('Expected an existing canonical absolute file: ' + value)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-manifest', required=True, type=existing_file)
    parser.add_argument('--on-build', required=True, type=existing_file)
    parser.add_argument('--off-build', required=True, type=existing_file)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--mode', action='append', choices=MODES)
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 900:
        raise ValueError('Use a bounded 1-900 second owned-Player timeout.')
    root = args.output_root
    if not root.is_absolute() or str(root) != str(root.resolve()) or root.exists():
        raise ValueError('Process output must be a new canonical absolute directory.')
    root.relative_to(PROJECT / '_temp' / 'AssemblyShadow')
    modes = args.mode or list(MODES)
    if len(set(modes)) != len(modes):
        raise ValueError('Duplicate modes are not allowed in a capture.')
    builds = {}
    input_paths = {args.fixture_manifest, args.on_build, args.off_build}
    for enabled, receipt_path in ((True, args.on_build), (False, args.off_build)):
        receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
        expected = 'NativeOn' if enabled else 'NativeOff'
        if receipt['milestone'] != 'M05' or receipt['variant'] != expected:
            raise ValueError('Wrong M05 Player variant: ' + str(receipt_path))
        app = Path(receipt['playerOutput']).resolve(strict=True)
        app.relative_to(PROJECT / 'Builds' / 'AssemblyShadow' / 'M05')
        with (app / 'Contents' / 'Info.plist').open('rb') as stream:
            executable_name = plistlib.load(stream)['CFBundleExecutable']
        if Path(executable_name).name != executable_name:
            raise ValueError('Invalid Player executable name.')
        executable = existing_file(str(app / 'Contents' / 'MacOS' / executable_name))
        for field in ('nativeLibraryPath', 'nativeMetadataPath', 'typeProofPath'):
            item = existing_file(receipt[field])
            expected_hash = receipt[field.replace('Path', 'Sha256')]
            if digest(item) != expected_hash:
                raise ValueError('Player receipt hash mismatch: ' + str(item))
            input_paths.add(item)
        input_paths.add(executable)
        builds[enabled] = (receipt_path, executable, receipt['buildGuid'])
    before = {str(path): digest(path) for path in sorted(input_paths)}
    root.mkdir()
    results = root / 'Results'
    results.mkdir()
    launches = []
    failed = False
    for mode in modes:
        receipt_path, executable, build_guid = builds[mode not in OFF]
        result_path = results / ('m05-' + mode + '.json')
        log_path = root / (mode + '.unity.log')
        command = [str(executable), '-batchmode', '-nographics',
                   '-shadowM05Mode', mode, '-shadowM05Fixtures', str(args.fixture_manifest),
                   '-shadowM05PlayerReceipt', str(receipt_path),
                   '-shadowM05Result', str(result_path), '-logFile', str(log_path)]
        started = time.time()
        timed_out = False
        with (root / (mode + '.console.log')).open('xb') as console:
            process = subprocess.Popen(command, cwd=str(PROJECT), stdin=subprocess.DEVNULL,
                                       stdout=console, stderr=subprocess.STDOUT)
            print(mode + ' started pid=' + str(process.pid), flush=True)
            try:
                code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.terminate()
                try:
                    code = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    code = process.wait(timeout=10)
        outcome = None
        error = ''
        if result_path.is_file():
            try:
                outcome = json.loads(result_path.read_text(encoding='utf-8-sig'))
            except (OSError, ValueError) as problem:
                error = str(problem)
        passed = (not timed_out and code == 0 and outcome is not None and
                  outcome.get('mode') == mode and outcome.get('result') == 'Passed' and
                  outcome.get('processId') == process.pid and outcome.get('buildGuid') == build_guid)
        launches.append(dict(mode=mode, command=command, processId=process.pid,
                             startedAtUnix=started, durationSeconds=time.time() - started,
                             exitCode=code, timedOut=timed_out, passed=passed,
                             resultPath=str(result_path), resultSha256=digest(result_path) if result_path.is_file() else '',
                             error=error or (outcome or {}).get('error', 'No result file')))
        print(mode + ' ' + ('Passed' if passed else 'FAILED') + ' exit=' + str(code), flush=True)
        if not passed:
            failed = True
            break
    after = {str(path): digest(path) for path in sorted(input_paths)}
    receipt = dict(milestone='M05', diagnosticOnly=True, fullModeInventory=list(MODES),
                   requestedModes=modes, completedModes=len(launches), processLaunches=launches,
                   inputHashesBefore=before, inputHashesAfter=after, inputsUnchanged=before == after,
                   resultDirectory=str(results), note='Launch receipts are not strict M05 acceptance.')
    with (root / 'player-launches.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    return int(failed or before != after)


if __name__ == '__main__':
    sys.exit(main())
