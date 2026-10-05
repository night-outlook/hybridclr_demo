#!/usr/bin/env python3
"""Pinned-Mono execution of actual nominal-identity rules, not a Unity Player run."""
import argparse
import os
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import run_owned_command
from unity_command import clean_outer
from build_api import csc_arguments, CORE_SHA
from input_validation import binding
import reference_binding as replay


def validate(workspace, contents, api_output, newtonsoft, output):
    workspace, contents, api, root = map(lambda p: Path(p).resolve(), (workspace, contents, api_output, output))
    require(not root.exists(), 'Unused reference replay output'); root.mkdir(parents=True)
    demo, package = workspace / 'hybridclr_demo', workspace / 'hybridclr_unity'
    runtime, compiler = contents / 'NetCoreRuntime/dotnet', contents / 'DotNetSdkRoslyn/csc.dll'
    mono = contents / 'MonoBleedingEdge/bin/mono'
    result = {'schemaVersion': 1, 'kind': 'R03PinnedMonoReferenceBinding', 'result': 'Failed',
              'basis': 'ReusedAuditedLocalNCompilerInputs', 'historicalFinalPolicy': 'Failed',
              'currentCompilerSnapshotProduced': False, 'nativeProofExecuted': False, 'runtimeAcceptance': False,
              'unityEditorRun': False, 'playerRun': False, 'expansionAuthorized': False}
    try:
        require(sha(contents / 'Managed/UnityEngine/UnityEditor.CoreModule.dll') == CORE_SHA, 'Pinned Unity API bytes')
        inputs = replay.inputs(demo, root / 'replay-inputs.json')
        # Independently corroborate each diagnostic framework-provider byte against
        # the extracted pinned distribution; no live Editor/catalog claim.
        for world in inputs['worlds']:
            for file in world['files']:
                if file['framework']:
                    suffix = file['originalSourcePath'][len(replay.UNITY_BASE):]
                    require(sha(contents / suffix) == file['sha256'], 'Pinned framework replay bytes differ')
        built = loads((api / 'results.json').read_text()); require(built['result'] == 'Passed', 'Actual full package compilation required')
        assemblies = [Path(r['output']['path']) for r in built['assemblies']]
        profile = contents / 'MonoBleedingEdge/lib/mono/unityaot-macos'
        refs = [*sorted(profile.glob('*.dll')), *sorted((profile / 'Facades').glob('*.dll')), *assemblies,
                package / 'Plugins/dnlib.dll', Path(newtonsoft).resolve()]
        source, target = HERE / 'ReferenceBindingTests/Program.cs', root / 'ReferenceBindingProbe.exe'
        args = csc_arguments(runtime, compiler, [], refs, [source], target)
        args = [a.replace('/target:library', '/target:exe') for a in args if a != '/define:']
        rsp = root / 'compiler.rsp'; rsp.write_text('\n'.join('"' + a.replace('"', '\\"') + '"' for a in args[4:]) + '\n')
        tracked = [runtime, compiler, mono, source, *refs, root / 'replay-inputs.json']
        before = [binding(p) for p in tracked]; write(root / 'inputs.json', {'files': before, 'ruleStubsUsed': False})
        clean_outer(run_owned_command([*args[:4], '@' + str(rsp)], root / 'commands/0001', 600), 0)
        paths = [p.parent for p in assemblies] + [package / 'Plugins', Path(newtonsoft).resolve().parent,
                    contents / 'Managed', contents / 'Managed/UnityEngine', profile, profile / 'Facades']
        clean_outer(run_owned_command(['/usr/bin/env', 'MONO_PATH=' + os.pathsep.join(map(str, paths)), mono, target,
                    '--output', root / 'contracts', '--input', root / 'replay-inputs.json'], root / 'commands/0002', 600), 0)
        result['checks'] = replay.verify_results(root / 'contracts', inputs)
        require(before == [binding(p) for p in tracked], 'Sources or consumer references changed')
        result['result'] = 'Passed'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error); raise
    finally:
        write(root / 'results.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace', 'contents', 'api-output', 'newtonsoft', 'output'):
        parser.add_argument('--' + flag, required=True)
    a = parser.parse_args(); validate(a.workspace, a.contents, a.api_output, a.newtonsoft, a.output)
