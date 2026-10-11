#!/usr/bin/env python3
"""Syntax-check actual native sources; this never claims runtime execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(workspace, output):
    workspace, output = Path(workspace).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    demo = workspace / 'hybridclr_demo'
    pins = json.loads((demo / 'Tools/AssemblyShadow/R03/source-pins.json').read_text())
    compiler = shutil.which('clang++') or shutil.which('c++')
    if not compiler:
        raise RuntimeError('A real C++ compiler is required.')
    identities = {}
    for repo in ('hybridclr', 'il2cpp_plus'):
        actual = subprocess.check_output(['git', '-C', str(workspace / repo), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != pins[repo]:
            raise RuntimeError('Native source pin mismatch: ' + repo)
        identities[repo] = actual
    units = [('resolver', workspace / 'il2cpp_plus/libil2cpp/vm/AssemblyShadowTypeResolver.cpp'),
             ('type-key', workspace / 'il2cpp_plus/libil2cpp/vm/AssemblyShadowTypeKey.cpp'),
             ('staging', workspace / 'hybridclr/hybridclr/metadata/StagedAssembly.cpp')]
    rows = []
    for feature, diagnostics in ((0, 0), (1, 0), (1, 2)):
        for label, source in units:
            cell = output / ('%s-f%s-d%s' % (label, feature, diagnostics))
            cell.mkdir()
            command = [compiler, '-std=c++11', '-fsyntax-only', '-pthread',
                       '-DHYBRIDCLR_UNITY_VERSION=20220362', '-DHYBRIDCLR_UNITY_2022=1',
                       '-DHYBRIDCLR_UNITY_2021_OR_NEW=1',
                       '-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + str(feature),
                       '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=' + str(diagnostics),
                       '-I', str(workspace / 'il2cpp_plus/libil2cpp'),
                       '-I', str(workspace / 'hybridclr'), str(source)]
            start = time.time()
            timeout = False
            with (cell / 'stdout.log').open('wb') as stdout, (cell / 'stderr.log').open('wb') as stderr:
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
                try:
                    code = process.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    timeout = True
                    os.killpg(process.pid, signal.SIGKILL)
                    code = process.wait()
            row = {'id': cell.name, 'command': command, 'sourceSha256': digest(source),
                   'exitCode': code, 'timeout': timeout, 'startedUtcEpoch': start,
                   'endedUtcEpoch': time.time(), 'result': 'Passed' if code == 0 and not timeout else 'Failed'}
            (cell / 'command.json').write_text(json.dumps(row, indent=2) + '\n')
            print(json.dumps(row), flush=True)
            if code:
                print((cell / 'stderr.log').read_text(errors='replace'), flush=True)
            rows.append(row)
    result = {'kind': 'R03NativeSourceCompile', 'schemaVersion': 1, 'repositories': identities,
              'compilerVersion': subprocess.check_output([compiler, '--version'], text=True),
              'cells': rows, 'result': 'Passed' if all(r['result'] == 'Passed' for r in rows) else 'Failed',
              'unityBuild': False, 'nativeRuntimeExecution': False, 'playerAcceptance': False}
    (output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['result'] == 'Passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.workspace, args.output))
