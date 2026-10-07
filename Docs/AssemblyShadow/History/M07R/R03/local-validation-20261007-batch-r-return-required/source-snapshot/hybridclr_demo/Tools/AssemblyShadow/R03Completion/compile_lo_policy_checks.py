#!/usr/bin/env python3
"""Run actual package policy domains on pinned Mono and the captured O input graph."""
import argparse
from pathlib import Path
import os
import re
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import run_owned_command
from unity_command import clean_outer
from build_api import csc_arguments, CORE_SHA
from input_validation import binding
from compiler_policy_inputs import regular
import lo_regressions as corpus

COMPILER = 'projects/resource-complete/_temp/AssemblyShadow/M07CompilerPreflight-bf405d4f5600495f93f6ebd466f7425f/Snapshot'
POLICY = 'projects/resource-complete/_temp/AssemblyShadow/R03CompletionArtifacts/integration/P01/generation/policy.json'
NAMES = ('Unity.Burst', 'Unity.Burst.Unsafe', 'Unity.RenderPipelines.Universal.Runtime',
         'Unity.RenderPipelines.Universal.2D.Internal', 'Unity.RenderPipelines.Universal.Config.Runtime')


def source_graph(document):
    """Reconstruct the bounded source-edge fixture from authenticated O diagnostics.

    A compiled AssemblyRef table is not Unity's effective asmdef/preflight graph.
    This fixture is reported source evidence, not a fresh CompilerPipeline capture.
    The caller authenticates PRIMARY_ISSUES.json through the immutable corpus.
    """
    require(document.get('kind') == 'R03OPrimaryImplementationIssues', 'Original O issue report required')
    issues = [row for row in document.get('issues', []) if row.get('id') == 'R03-LO-001']
    require(len(issues) == 1, 'Exactly one LO-001 report required')
    excerpt = issues[0].get('relevantExcerpt', '')
    require(isinstance(excerpt, str), 'Original source preflight excerpt required')
    edges = re.findall(r'^RuntimeReferencesFilteredAssembly: (\S+) references an assembly removed from the captured Player build: (\S+)\.$', excerpt, re.MULTILINE)
    expected = [(NAMES[0], NAMES[1]), (NAMES[2], NAMES[3]), (NAMES[2], NAMES[4])]
    require(len(edges) == len(expected) and set(edges) == set(expected), 'Exact three original source preflight edges required')
    return {name: sorted(provider for consumer, provider in edges if consumer == name) for name in NAMES}


def validate(workspace, contents, api_output, newtonsoft, output):
    workspace, contents, api, root = map(lambda p: Path(p).resolve(), (workspace, contents, api_output, output))
    require(not root.exists(), 'Unused LO policy output'); root.mkdir(parents=True)
    demo, package = workspace / 'hybridclr_demo', workspace / 'hybridclr_unity'
    result = {'schemaVersion': 1, 'kind': 'R03LOPinnedMonoPolicyDomainReplay', 'result': 'Failed',
        'historicalOResult': 'Failed', 'historicalEvidenceModified': False,
        'unityEditorRun': False, 'playerRun': False, 'freshCompilerSnapshot': False, 'runtimeAcceptance': False}
    try:
        checkpoint, _ = corpus.checkpoint(demo)
        batch = checkpoint / 'batch'
        policy, compiler = batch / POLICY, batch / COMPILER
        issue = checkpoint / 'preflight/PRIMARY_ISSUES.json'
        graph = root / 'source-graph.json'
        write(graph, {'kind': 'R03LOReportedSourceGraphFixture', 'basis': 'AuthenticatedLocalOReportedPreflightEdges',
            'issueSha256': sha(issue), 'references': source_graph(loads(issue.read_text())),
            'freshSourceGraphCapture': False, 'compilerAssemblyRefsUsedAsSourceGraph': False})
        player = batch / 'projects/resource-complete/_temp/AssemblyShadow' / corpus.PLAYER_INPUTS['on'] / 'assembly-snapshot.json'
        require(sha(contents / 'Managed/UnityEngine/UnityEditor.CoreModule.dll') == CORE_SHA, 'Pinned Unity API')
        built = loads((api / 'results.json').read_text()); require(built['result'] == 'Passed', 'Actual full dependency compilation required')
        assemblies = [Path(row['output']['path']) for row in built['assemblies']]
        source = HERE / 'CompilerPolicyTests/PolicyDomainProbe.cs'; target = root / 'PolicyDomainProbe.exe'
        runtime, csc, mono = contents / 'NetCoreRuntime/dotnet', contents / 'DotNetSdkRoslyn/csc.dll', contents / 'MonoBleedingEdge/bin/mono'
        refs = [*sorted((contents / 'MonoBleedingEdge/lib/mono/unityaot-macos').glob('*.dll')),
            *sorted((contents / 'MonoBleedingEdge/lib/mono/unityaot-macos/Facades').glob('*.dll')), *assemblies,
            package / 'Plugins/dnlib.dll', Path(newtonsoft).resolve()]
        snapshot = loads((compiler / 'assembly-snapshot.json').read_text()); physical = []
        for name in NAMES:
            rows = [row for row in snapshot['assemblies'] + snapshot['references'] if row['name'] == name]
            require(len(rows) == 1, 'One captured compiler input: ' + name)
            relative = Path(rows[0]['path']); require(not relative.is_absolute() and '..' not in relative.parts, 'Compiler path')
            dll = regular(compiler / relative); require(sha(dll) == rows[0]['sha256'], 'Original compiler DLL hash')
            physical.append(dll)
        tracked = [source, issue, graph, policy, player, compiler / 'assembly-snapshot.json', *physical, runtime, csc, mono, *refs]
        before = [binding(p) for p in tracked]; write(root / 'inputs.json', {'files': before, 'historicalInputPublication': '7025f1026fd61f101a81fbafafb999095aa8604e',
            'sourceBinding': binding(source), 'driverBinding': binding(Path(__file__).resolve()),
            'sourceGraphBasis': 'AuthenticatedLocalOReportedPreflightEdges'})
        args = csc_arguments(runtime, csc, [], refs, [source], target)
        args = [arg.replace('/target:library', '/target:exe') for arg in args if arg != '/define:']
        rsp = root / 'compiler.rsp'; rsp.write_text('\n'.join('"' + arg.replace('"', '\\"') + '"' for arg in args[4:]) + '\n')
        clean_outer(run_owned_command([*args[:4], '@' + str(rsp)], root / 'commands/0001', 600), 0)
        paths = [p.parent for p in assemblies] + [package / 'Plugins', Path(newtonsoft).resolve().parent,
            contents / 'Managed', contents / 'Managed/UnityEngine', contents / 'MonoBleedingEdge/lib/mono/unityaot-macos',
            contents / 'MonoBleedingEdge/lib/mono/unityaot-macos/Facades']
        clean_outer(run_owned_command(['/usr/bin/env', 'MONO_PATH=' + os.pathsep.join(map(str, paths)), mono, target,
            policy, player, compiler, graph, root / 'policy-domain.json'], root / 'commands/0002', 180), 0)
        observation = loads((root / 'policy-domain.json').read_text())
        require(observation['result'] == 'Passed' and observation['failures'] == 0 and len(observation['cases']) == 10,
            'All ten actual policy-domain cases must pass')
        require(before == [binding(p) for p in tracked], 'Input/source custody after policy execution')
        result.update(result='Passed', observation=observation)
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally: write(root / 'results.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace', 'contents', 'api-output', 'newtonsoft', 'output'): parser.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    validate(args.workspace, args.contents, args.api_output, args.newtonsoft, args.output)
