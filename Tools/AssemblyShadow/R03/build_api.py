"""Compile complete R03Build.cs and its real package dependencies using pinned Unity.

No Unity API stubs, Editor launch, installer execution, or native acceptance.
The same routine runs in CI and as a subcheck of the existing Local fixture cell.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import run_owned_command
from input_validation import binding, unity_toolchain
from unity_command import clean_outer

HERE = Path(__file__).resolve().parent
CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-c-return-required'
CORE_SHA = 'e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e'
OLD_BLOB = '7b54381bc96b4be133ebed5f7b7173fcc0a57849'
UNITY_PREFIX = '/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/'


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def compile_profile(log, contents):
    """Use the platform/defines/reference profile recorded by the real failed build."""
    defines = sorted(set(re.findall(r'^-define:([A-Za-z0-9_]+)\s*$', log, re.MULTILINE)))
    require('UNITY_EDITOR_OSX' in defines and 'UNITY_2022_3' in defines,
            'Pinned macOS Editor compile defines required')
    require(not {'UNITY_EDITOR_WIN', 'UNITY_EDITOR_LINUX'} & set(defines), 'Mixed Editor platforms')
    refs = []
    for value in re.findall(r'^-r:"([^"]+)"\s*$', log, re.MULTILINE):
        if value.startswith(UNITY_PREFIX):
            relative = Path(value[len(UNITY_PREFIX):])
            require('..' not in relative.parts, 'Unsafe reference path')
            refs.append(Path(contents) / relative)
    refs = sorted(set(refs))
    names = {p.name for p in refs}
    require({'UnityEditor.CoreModule.dll', 'UnityEngine.CoreModule.dll', 'UnityEditor.OSXStandalone.Extensions.dll',
             'netstandard.dll', 'mscorlib.dll'} <= names, 'Incomplete actual Unity reference profile')
    return defines, refs


def assembly_plan(package):
    """Select actual asmdef-owned sources and transitive package dependencies."""
    package = Path(package)
    definitions = {}
    for path in package.rglob('*.asmdef'):
        if any(p.endswith('~') for p in path.relative_to(package).parts):
            continue
        data = loads(path.read_text())
        require(data['name'] not in definitions, 'Duplicate package assembly name')
        definitions[data['name']] = (path, data)
    sources = {name: [] for name in definitions}
    for path in package.rglob('*.cs'):
        owners = [(name, asm) for name, (asm, _) in definitions.items() if path.is_relative_to(asm.parent)]
        if owners:
            owner = max(owners, key=lambda item: len(item[1].parent.parts))[0]
            sources[owner].append(path)
    order, visiting = [], set()
    def visit(name):
        require(name in definitions, 'Missing package assembly: ' + name)
        if name in order:
            return
        require(name not in visiting, 'Package assembly dependency cycle')
        visiting.add(name)
        path, data = definitions[name]
        require(not data.get('defineConstraints') and not data.get('versionDefines'), 'Unsupported conditional asmdef: ' + name)
        require(not data.get('excludePlatforms') and (not data.get('includePlatforms') or data['includePlatforms'] == ['Editor']),
                'Unsupported platform asmdef: ' + name)
        for dep in data.get('references', []):
            visit(dep)
        require(sources[name], 'No actual package source: ' + name)
        visiting.remove(name)
        order.append(name)
    visit('HybridCLR.Editor')
    require('HybridCLR.Runtime' in order, 'Actual runtime dependency required')
    return [(name, definitions[name][0], definitions[name][1], sorted(sources[name])) for name in order]


def csc_arguments(runtime, compiler, defines, refs, sources, target):
    return [str(runtime), 'exec', str(compiler), '/noconfig', '/nostdlib+', '/nologo',
            '/target:library', '/langversion:9.0', '/unsafe+', '/preferreduilang:en-US',
            '/define:' + ';'.join(defines), '/out:' + str(target),
            *['/reference:' + str(p) for p in refs], *map(str, sources)]


def verify_negative(receipt, output, target):
    clean_outer(receipt, 1)
    errors = re.findall(r'\berror (CS\d+):', output)
    require(errors == ['CS0266', 'CS0266'] and not Path(target).exists(),
            'Original complete helper must fail only the two count conversions')
    require("'int' to 'uint'" in output, 'Expected original count type diagnostic')


def validate_build_api(batch):
    demo, package = batch.workspace / 'hybridclr_demo', batch.workspace / 'hybridclr_unity'
    root = batch.root / 'build-api'; root.mkdir()
    result = {'kind': 'R03CompleteBuildHelperCompile', 'schemaVersion': 1, 'result': 'Failed',
              'unityVersion': '2022.3.62f2', 'unityEditorRun': False, 'nativeExecution': False,
              'runtimeAcceptance': False, 'packageAssemblies': [], 'commands': []}
    try:
        contents = Path(batch.unity).parent.parent
        core = contents / 'Managed/UnityEngine/UnityEditor.CoreModule.dll'
        require(sha(core) == CORE_SHA, 'Pinned UnityEditor.CoreModule bytes differ from Local C')
        log = demo / CHECKPOINT / 'batch/builds/candidate-release/Editor.log'
        old = demo / CHECKPOINT / 'batch/projects/candidate-release/Assets/Editor/R03Build.cs'
        current = HERE / 'PlayerProject/R03Build.cs'
        player = HERE.parent / 'R03IR/PlayerProject/R03TerminalPlayer.cs'
        require(git_blob(old.read_bytes()) == OLD_BLOB, 'Preserved C helper source changed')
        defines, references = compile_profile(log.read_text(), contents)
        runtime, compiler, _ = unity_toolchain(batch.unity)
        # ILPostProcessor dependencies are added by Unity for its special CodeGen assembly.
        references = sorted(set(references + [contents / 'Managed/Unity.CompilationPipeline.Common.dll']))
        plan = assembly_plan(package)
        plugins = sorted((package / 'Plugins').rglob('*.dll'))
        require(any(p.name == 'dnlib.dll' for p in plugins), 'Actual package dnlib dependency required')
        sources = [p for _, asmdef, _, files in plan for p in [asmdef, *files]]
        tracked = sorted(set([runtime, compiler, core, log, old, current, player, *references, *plugins, *sources]))
        before = [binding(p) for p in tracked]
        result.update(inputs=before, defines=defines, oldSourceBlob=OLD_BLOB,
                      helperSourceSha256=sha(current), referenceCoreSha256=sha(core))
        write(root / 'inputs.json', {'files': before, 'defines': defines})
        built = {}
        def compile_one(label, files, deps, negative=False):
            directory = root / label; directory.mkdir()
            target = directory / (label + '.dll')
            args = csc_arguments(runtime, compiler, defines, references + plugins + deps, files, target)
            # /noconfig must be on the command line: Roslyn ignores it in response files.
            # The remaining response file avoids argv limits and is retained as evidence.
            response = directory / 'compiler.rsp'
            response.write_text('\n'.join('"' + a.replace('"', '\\"') + '"' for a in args[4:]) + '\n')
            try:
                receipt = batch.command([*args[:4], '@' + str(response)])
                require(not negative, 'Original uint helper unexpectedly compiled')
            except RuntimeError:
                if not negative:
                    raise
                folder = batch.root / 'commands' / ('%04d' % batch.command_count)
                receipt = loads((folder / 'command.json').read_text())
                output = (folder / 'stdout.log').read_text() + (folder / 'stderr.log').read_text()
                verify_negative(receipt, output, target)
            folder = batch.root / 'commands' / ('%04d' % batch.command_count)
            result['commands'].append({'id': label, 'expectedExit': 1 if negative else 0,
                                       'receipt': binding(folder / 'command.json'), 'response': binding(response)})
            if not negative:
                clean_outer(receipt, 0)
                require(target.is_file() and target.stat().st_size > 0, 'Missing compiled assembly')
            return target
        for name, asmdef, data, files in plan:
            target = compile_one(name, files, [built[n] for n in data.get('references', [])])
            built[name] = target
            result['packageAssemblies'].append({'name': name, 'asmdef': binding(asmdef), 'sourceCount': len(files), 'output': binding(target)})
        target = compile_one('R03Build', [current], list(built.values()))
        result['completeHelper'] = binding(target)
        # Compile the exact changed supplementary Player against the official
        # Unity managed reference set; the separate stub API job is not enough.
        player_output = compile_one('R03TerminalPlayerApi', [player], list(built.values()))
        result['terminalPlayerApi'] = {'source': binding(player), 'output': binding(player_output),
            'profile': 'Official Unity 2022.3.62f2 managed assemblies; Editor reference defines',
            'playerExecution': False}
        compile_one('OriginalUnsignedCounts', [old], list(built.values()), negative=True)
        require(before == [binding(p) for p in tracked], 'Compiler/reference/source input changed')
        result['result'] = 'Passed'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(root / 'results.json', result)
    return {'result': str(root / 'results.json'), 'sha256': sha(root / 'results.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--unity', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    class Host:
        def __init__(self):
            self.workspace, self.root, self.unity = args.workspace.resolve(), args.output.resolve(), args.unity.resolve()
            require(not self.root.exists(), 'Unused host evidence root required')
            self.root.mkdir(parents=True)
            self.command_count = 0
        def command(self, command, timeout=600):
            self.command_count += 1
            return run_owned_command(command, self.root / 'commands' / ('%04d' % self.command_count), timeout)
    host = Host()
    pins = loads((HERE / 'source-pins.json').read_text())
    actual = subprocess.check_output(['git', '-C', str(host.workspace / 'hybridclr_unity'), 'rev-parse', 'HEAD'], text=True).strip()
    require(actual == pins['hybridclr_unity'], 'Host package pin mismatch')
    print(json.dumps(validate_build_api(host)))
