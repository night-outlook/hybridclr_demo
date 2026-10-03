#!/usr/bin/env python3
"""Compile complete original-resource helpers/dependencies; no Unity API stubs.

Host compiler/runtime and API origins are recorded separately. A pinned upstream
Core RP source provides compile-time metadata only, not UPM artifact equivalence.
Unity installation/import/link/Player execution remain separate Local checks.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from build_api import compile_profile, assembly_plan, csc_arguments, CORE_SHA, CHECKPOINT
from command_lifetime import run_owned_command
from input_validation import binding
from unity_command import clean_outer


def collect_definitions(root):
    definitions = {}
    for path in Path(root).rglob('*.asmdef'):
        d = loads(path.read_text()); name = d['name']
        require(name not in definitions, 'Duplicate assembly: ' + name)
        definitions[name] = (path, d, [])
    for source in Path(root).rglob('*.cs'):
        owners = [(name, p) for name, (p, _, _) in definitions.items() if source.is_relative_to(p.parent)]
        if owners:
            name = max(owners, key=lambda item: len(item[1].parent.parts))[0]
            definitions[name][2].append(source)
    return definitions


def validate(workspace, contents, core_source, runtime, compiler, output):
    workspace, contents, core_source, runtime, compiler, root = map(lambda p: Path(p).resolve(),
                                                                 (workspace, contents, core_source, runtime, compiler, output))
    require(not root.exists(), 'Unused compilation evidence root')
    root.mkdir(parents=True)
    demo, package = workspace / 'hybridclr_demo', workspace / 'hybridclr_unity'
    result = {'kind': 'R03ResourceFullSourceCompilation', 'schemaVersion': 1, 'result': 'Failed', 'assemblies': [],
              'unityVersion': '2022.3.62f2', 'upmByteEquivalenceClaimed': False, 'unityEditorRun': False,
              'playerRun': False, 'expansionAuthorized': False}
    command_count = 0
    try:
        require(sha(contents / 'Managed/UnityEngine/UnityEditor.CoreModule.dll') == CORE_SHA, 'Pinned CoreModule API hash')
        original_log = demo / CHECKPOINT / 'batch/builds/candidate-release/Editor.log'
        defines, refs = compile_profile(original_log.read_text(), contents)
        refs = sorted(set(refs + [contents / 'Managed/Unity.CompilationPipeline.Common.dll']))
        definitions = collect_definitions(demo / 'Assets')
        package_plan = assembly_plan(package)
        for name, asm, data, sources in package_plan:
            definitions[name] = (asm, data, sources)
        gui = contents / 'Resources/PackageManager/BuiltInPackages/com.unity.ugui'
        guis = collect_definitions(gui)
        require('UnityEngine.UI' in guis and 'UnityEditor.UI' in guis, 'Actual built-in UGUI sources required')
        definitions.update(guis)
        metadata = loads((core_source / 'package.json').read_text())
        require(metadata['name'] == 'com.unity.render-pipelines.core' and metadata['version'] == '14.0.12', 'Exact declared Core RP version')
        definitions.update(collect_definitions(core_source / 'Runtime'))
        plugins = sorted((package / 'Plugins').rglob('*.dll'))
        guids = {}
        for name, (asm, _, _) in definitions.items():
            meta = asm.with_suffix(asm.suffix + '.meta')
            if meta.is_file():
                for line in meta.read_text().splitlines():
                    if line.startswith('guid: '): guids['GUID:' + line[6:].strip()] = name
        plans, visiting = [], set()
        # Official InputSystem 1.7.0 asmdef.meta identifies this optional reference.
        # The original copied project has no InputSystem package; Core guards all
        # such calls with ENABLE_INPUT_SYSTEM_PACKAGE, which remains undefined.
        optional_input = 'GUID:75469ad4d38634e559750d17036d5f7c'
        result['absentOptionalReferences'] = [{'owner': 'Unity.RenderPipelines.Core.Runtime', 'guid': optional_input,
            'assembly': 'Unity.InputSystem', 'define': 'ENABLE_INPUT_SYSTEM_PACKAGE', 'defined': False,
            'identityMetaBlob': 'ea88215b174341b5b83aa2eeb9c51c366561ba4c'}]
        def visit(name):
            if name in plans or any(p.stem == name for p in refs + plugins): return
            require(name in definitions and name not in visiting, 'Missing/cyclic assembly: ' + name)
            visiting.add(name); asm, data, sources = definitions[name]
            require(sources, 'Empty full-source assembly: ' + name)
            require('UNITY_INCLUDE_TESTS' not in data.get('defineConstraints', []), 'Do not claim test assembly execution from helper compilation')
            for dep in data.get('references', []):
                if name == 'Unity.RenderPipelines.Core.Runtime' and dep == optional_input: continue
                visit(guids.get(dep, dep))
            visiting.remove(name); plans.append(name)
        visit('UnityEditor.UI')
        visit('AssemblyShadowDemo.Editor')
        tracked = sorted(set([runtime, compiler, original_log, core_source / 'package.json', *refs, *plugins,
                              *[p for name in plans for p in [definitions[name][0], *definitions[name][2]]]]))
        inputs = [binding(p) for p in tracked]
        write(root / 'inputs.json', {'kind': result['kind'], 'files': inputs, 'defines': defines,
                                    'compiler': binding(compiler), 'runtime': binding(runtime),
                                    'apiCoreSha256': CORE_SHA, 'coreSourcePackage': metadata})
        built = {}
        for name in plans:
            asm, data, sources = definitions[name]
            folder = root / name; folder.mkdir(); target = folder / (name + '.dll')
            profile = set(defines)
            for version in data.get('versionDefines', []):
                if version['name'] in ('com.unity.modules.vr', 'com.unity.modules.xr', 'com.unity.modules.nvidia', 'com.unity.modules.physics', 'com.unity.modules.physics2d', 'com.unity.modules.animation', 'com.unity.modules.uielements'):
                    module = {'com.unity.modules.vr': 'UnityEngine.VRModule.dll', 'com.unity.modules.xr': 'UnityEngine.XRModule.dll',
                              'com.unity.modules.nvidia': 'UnityEngine.NVIDIAModule.dll', 'com.unity.modules.physics': 'UnityEngine.PhysicsModule.dll',
                              'com.unity.modules.physics2d': 'UnityEngine.Physics2DModule.dll', 'com.unity.modules.animation': 'UnityEngine.AnimationModule.dll',
                              'com.unity.modules.uielements': 'UnityEngine.UIElementsModule.dll'}[version['name']]
                    if any(p.name == module for p in refs): profile.add(version['define'])
            args = csc_arguments(runtime, compiler, sorted(profile), refs + plugins + list(built.values()), sorted(sources), target)
            rsp = folder / 'compiler.rsp'
            rsp.write_text('\n'.join('"' + a.replace('"', '\\"') + '"' for a in args[4:]) + '\n')
            command_count += 1
            receipt = run_owned_command([*args[:4], '@' + str(rsp)], root / 'commands' / ('%04d' % command_count), 600)
            clean_outer(receipt, 0); require(target.is_file(), 'Compiled output missing: ' + name)
            built[name] = target
            result['assemblies'].append({'name': name, 'sourceCount': len(sources), 'asmdef': binding(asm),
                                         'compilerResponse': binding(rsp), 'command': command_count, 'output': binding(target)})
        require(inputs == [binding(p) for p in tracked], 'Source/reference bytes changed during compilation')
        result['sourceFiles'] = sum(row['sourceCount'] for row in result['assemblies'])
        result['compiler'] = binding(compiler); result['runtime'] = binding(runtime)
        result['result'] = 'Passed'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(root / 'results.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace', 'contents', 'core-source', 'runtime', 'compiler', 'output'): p.add_argument('--' + flag, required=True, type=Path)
    a = p.parse_args()
    validate(a.workspace, a.contents, a.core_source, a.runtime, a.compiler, a.output)
