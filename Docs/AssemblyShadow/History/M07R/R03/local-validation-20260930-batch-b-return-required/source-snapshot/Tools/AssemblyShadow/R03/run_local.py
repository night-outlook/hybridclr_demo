#!/usr/bin/env python3
"""One unused R03 batch. No product source edits, retries, or acceptance promotion."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

from batch_contract import loads, require, sha, verify_raw
from batch_evidence import finalize, write
from command_lifetime import build_arguments, run_owned_command

REPOS = ('hybridclr_demo', 'hybridclr', 'hybridclr_unity', 'il2cpp_plus')
BRANCH = 'codex/assembly-shadow-r01b-h1'
ROOT = Path(__file__).resolve().parent
REFERENCE_PACKAGE = 'b936a495ade1691ebb6f3bab8fdff3ef34f6f192'


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT='0'), timeout=120)
    require(result.returncode == 0, 'Git command failed: ' + ' '.join(args[:2]))
    return result.stdout.strip()


def identity(repo, expected):
    repo = Path(repo).resolve()
    require(Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() == repo, 'Not the owning checkout: ' + repo.name)
    require(git(repo, 'rev-parse', 'HEAD') == expected, 'Exact HEAD mismatch: ' + repo.name)
    require(not git(repo, 'status', '--porcelain=v1', '--untracked-files=all'), 'Dirty owning repository: ' + repo.name)
    url = git(repo, 'remote', 'get-url', 'origin')
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)(night-outlook/(?:hybridclr_demo|hybridclr|hybridclr_unity|il2cpp_plus))(?:\.git)?', url)
    require(match is not None and match.group(1) == 'night-outlook/' + repo.name, 'Canonical repository identity mismatch')
    require(git(repo, 'branch', '--show-current') == BRANCH, 'Working branch mismatch: ' + repo.name)
    remote = git(repo, 'ls-remote', 'origin', 'refs/heads/' + BRANCH).split()
    require(remote == [expected, 'refs/heads/' + BRANCH], 'Remote HEAD mismatch: ' + repo.name)
    return {'repository': match.group(1), 'path': str(repo), 'commit': expected, 'branch': BRANCH, 'remoteHeadVerified': True}


class Batch:
    def __init__(self, workspace, output, unity, demo_commit):
        self.workspace = Path(workspace).resolve()
        self.root = Path(output).resolve()
        self.unity = str(Path(unity).resolve())
        require(ROOT == self.workspace / 'hybridclr_demo/Tools/AssemblyShadow/R03', 'Run the script from the exact owning demo checkout')
        require(not self.root.exists() and self.root != self.workspace, 'Batch destination must be unused')
        for name in REPOS:
            require(not self.root.is_relative_to(self.workspace / name), 'Place the batch outside all four owning repositories')
        require(Path(self.unity).is_file(), 'Exact Unity executable is required')
        self.pins = loads((ROOT / 'source-pins.json').read_text())
        self.pins['hybridclr_demo'] = demo_commit
        self.matrix = loads((ROOT / 'player-cases.json').read_text())
        require(len(self.matrix['cases']) == 19 and len({c['id'] for c in self.matrix['cases']}) == 19, 'Exact nineteen-cell native matrix')
        self.root.mkdir(parents=True)
        self.cells, self.outputs, self.references, self.builds = [], {}, {}, {}
        self.command_count, self.failed = 0, False

    def command(self, args, timeout=600):
        self.command_count += 1
        root = self.root / 'commands' / ('%04d' % self.command_count)
        return run_owned_command(args, root, timeout)

    def cell(self, name, action, dependencies=()):
        row = {'id': name, 'result': 'Blocked', 'dependencies': list(dependencies)}
        if all(self.outputs.get(d, False) for d in dependencies):
            try:
                row['evidence'] = action()
                row['result'] = 'Passed'
            except Exception as error:
                row['result'], row['error'] = 'Failed', str(error)
        else:
            row['reason'] = 'Required prerequisite did not pass; no substitute or retry.'
        self.outputs[name] = row['result'] == 'Passed'
        self.failed |= not self.outputs[name]
        self.cells.append(row)
        write(self.root / 'cells' / (name + '.json'), row)
        print(json.dumps(row), flush=True)

    def authority(self):
        require(sys.platform == 'darwin', 'This execution batch requires macOS; host-only CI is separate')
        records = [identity(self.workspace / name, self.pins[name]) for name in REPOS]
        return {'repositories': records}

    def reference_worktrees(self):
        pins = dict(self.matrix['referenceCore'], hybridclr_unity=REFERENCE_PACKAGE)
        for name, revision in pins.items():
            origin = self.workspace / name
            git(origin, 'merge-base', '--is-ancestor', revision, self.pins[name])
            path = self.root / 'reference-worktrees' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            self.command(['git', '-C', origin, 'worktree', 'add', '--detach', path, revision], 120)
            self.references[name] = path
            require(git(path, 'rev-parse', 'HEAD') == revision and not git(path, 'status', '--porcelain'), 'Reference worktree source integrity')
        return {'paths': {k: str(v) for k, v in self.references.items()}, 'commits': pins,
                'retained': True, 'authority': 'Exact published ancestors of the verified candidate remote heads'}

    def managed(self, project, output, package=None, phase=None):
        package = package or self.workspace / 'hybridclr_unity'
        binary, intermediate = self.root / 'bin' / output, self.root / 'obj' / output
        self.command(build_arguments(ROOT / project / (project + '.csproj'), binary, intermediate, package))
        result_root = self.root / 'host' / output
        arguments = ['--phase', phase] if phase else []
        self.command(['dotnet', binary / (project + '.dll'), *arguments, '--output', result_root])
        result_file = result_root / ('inventory.json' if project == 'PlayerFixtures' else 'results.json')
        result = loads(result_file.read_text())
        if project != 'PlayerFixtures':
            require(result['result'] == 'Passed' and result['failures'] == 0, 'Managed contract failures')
            count = 35 if project == 'AdmissionTests' else 9
            require(len(result['cases']) == count and len({x['id'] for x in result['cases']}) == count, 'Managed contract identity count')
        return {'result': str(result_file), 'sha256': sha(result_file)}

    def fixtures(self):
        result = self.managed('PlayerFixtures', 'player-fixtures')
        self.fixture_root = self.root / 'host/player-fixtures'
        inventory = loads((self.fixture_root / 'inventory.json').read_text())
        require(len(inventory['files']) == 15 and len({f['path'] for f in inventory['files']}) == 15, 'Complete fixture inventory')
        self.fixture_files = {f['path']: f for f in inventory['files']}
        for path, entry in self.fixture_files.items():
            require(sha(self.fixture_root / path) == entry['sha256'], 'Actual fixture hash mismatch')
        return result

    def prepare_project(self, role):
        name = role['id']
        project = self.root / 'projects' / name
        project.mkdir(parents=True)
        for directory in ('Assets/Editor', 'Assets/R03', 'Assets/Fixtures', 'Packages', 'ProjectSettings'):
            (project / directory).mkdir(parents=True)
        (project / '.r03-isolated-project').write_text('R03 focused diagnostic project; not a deployable product.\n')
        origins = []
        def copy(source, relative, origin):
            target = project / relative
            shutil.copyfile(source, target)
            origins.append({'path': relative, 'sha256': sha(target), 'origin': origin})
        copy(ROOT / 'PlayerProject/R03Player.cs', 'Assets/R03Player.cs', 'Primary source')
        copy(ROOT / 'PlayerProject/R03Build.cs', 'Assets/Editor/R03Build.cs', 'Primary source')
        for entry in self.fixture_files.values():
            if entry['path'].startswith('baseline/'):
                copy(self.fixture_root / entry['path'], 'Assets/Fixtures/' + entry['assembly'] + '.dll', entry)
        manifest = loads((self.workspace / 'hybridclr_demo/Packages/manifest.json').read_text())
        dependencies = {k: v for k, v in manifest['dependencies'].items() if k.startswith('com.unity.modules.') or k in ('com.unity.test-framework', 'com.unity.ugui')}
        dependencies['com.code-philosophy.hybridclr'] = 'file:' + str(self.workspace / 'hybridclr_unity')
        write(project / 'Packages/manifest.json', {'dependencies': dependencies, 'testables': ['com.code-philosophy.hybridclr']})
        (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2022.3.62f2\n')
        (project / 'Assets/R03/link.xml').write_text('<linker>' + ''.join('<assembly fullname="' + a + '" preserve="all" />' for a in ('Layout', 'Methods', 'A', 'B', 'R03Contract', 'Assembly-CSharp')) + '</linker>\n')
        repos, pins = {r: self.workspace / r for r in REPOS}, {r: self.pins[r] for r in REPOS}
        if not role['candidate']:
            for repo, revision in self.matrix['referenceCore'].items():
                repos[repo], pins[repo] = self.references[repo], revision
        names = {'hybridclr': 'hybridclr', 'hybridclr_unity': 'hybridclrUnity', 'il2cpp_plus': 'il2cppPlus', 'hybridclr_demo': 'demo'}
        install_pins = {'schemaVersion': 1, 'unityVersion': '2022.3.62f2', 'target': 'StandaloneOSX'}
        for repo, key in names.items():
            install_pins[key] = {'url': 'https://github.com/night-outlook/' + repo + '.git', 'revision': pins[repo], 'localPath': os.path.relpath(repos[repo], project)}
        write(project / 'ProjectSettings/AssemblyShadowSourcePins.json', install_pins)
        write(project / 'source-inputs.json', {'schemaVersion': 1, 'demoCommit': self.pins['hybridclr_demo'], 'files': origins,
              'fixtureInventorySha256': sha(self.fixture_root / 'inventory.json'), 'repositories': pins,
              'note': 'Current package and identical new test harness on both native cores; reference is not the old accepted Player.'})
        build_root = self.root / 'builds' / name
        build_root.mkdir(parents=True)
        overlay = ROOT / 'PlayerProject/AssemblyShadowR03Probe.cpp'
        config = {'schemaVersion': 1, 'projectPath': str(project), 'outputPath': str(build_root / 'R03Isolated.app'),
                  'receiptPath': str(build_root / 'build-receipt.json'), 'overlayPath': str(overlay), 'overlaySha256': sha(overlay),
                  'sourceManifestSha256': sha(project / 'source-inputs.json'), 'featureEnabled': role['feature'],
                  'diagnosticsLevel': 2 if role['feature'] else 0, 'cppConfiguration': role['cpp']}
        write(build_root / 'config.json', config)
        self.builds[name] = {'project': project, 'root': build_root, 'config': config}
        return {'project': str(project), 'config': str(build_root / 'config.json')}

    def build(self, role):
        state = self.builds[role['id']]
        self.command([self.unity, '-batchmode', '-nographics', '-quit', '-buildTarget', 'osx', '-projectPath', state['project'],
                      '-executeMethod', 'AssemblyShadow.R03.Editor.R03Build.Build', '-r03Config', state['root'] / 'config.json',
                      '-logFile', state['root'] / 'Editor.log'], 7200)
        self.verify_build(role['id'])
        return {'receipt': str(state['root'] / 'build-receipt.json'), 'sha256': sha(state['root'] / 'build-receipt.json')}

    @staticmethod
    def verify_inventory(root, entries):
        root = Path(root).resolve()
        require(type(entries) is list and entries, 'A nonempty exact inventory is required')
        expected = {}
        for entry in entries:
            path = Path(entry['path'])
            require(not path.is_absolute() and '..' not in path.parts and entry['path'] not in expected, 'Unsafe or duplicate inventory path')
            expected[entry['path']] = entry
        actual = {str(p.relative_to(root)): p for p in root.rglob('*') if p.is_file()}
        require(set(actual) == set(expected), 'Exact file membership: ' + str(root))
        for name, path in actual.items():
            require(not path.is_symlink() and sha(path) == expected[name]['sha256'] and path.stat().st_size == expected[name]['size'], 'File changed: ' + name)

    def verify_build(self, role_id):
        state = self.builds[role_id]
        receipt = loads((state['root'] / 'build-receipt.json').read_text())
        require(receipt['result'] == 'Passed' and receipt['nonGeneratedCorePreserved'] is True and receipt['errors'] == 0, 'Successful verified native build required')
        for field in ('featureEnabled', 'diagnosticsLevel', 'cppConfiguration', 'outputPath', 'projectPath', 'sourceManifestSha256'):
            require(receipt[field] == state['config'][field], 'Build/config mismatch: ' + field)
        require(receipt['unityVersion'] == '2022.3.62f2' and receipt['target'] == 'StandaloneOSX' and receipt['architecture'] == 'arm64', 'Exact build target')
        require(receipt['testOverlaySha256'] == sha(ROOT / 'PlayerProject/AssemblyShadowR03Probe.cpp') and
                receipt['sourceManifestSha256'] == sha(state['project'] / 'source-inputs.json'), 'Native overlay and managed source binding')
        app = Path(state['config']['outputPath'])
        self.verify_inventory(app, receipt['playerFiles'])
        # Locate exactly one installed receipt by its expected hash; the actual
        # native root is derived from that receipt, not guessed from SDK layout.
        installs = [p for p in (state['project'] / 'HybridCLRData').rglob('assembly-shadow-install.json') if sha(p) == receipt['installReceiptSha256']]
        require(len(installs) == 1, 'Exact native installation receipt is required')
        native = installs[0].parent
        self.verify_inventory(native, receipt['installedAfter'])
        require(sha(native / 'vm/AssemblyShadowR03Probe.cpp') == receipt['testOverlaySha256'], 'Installed diagnostic source binding')
        before = {e['path']: e for e in receipt['installedBefore']}
        after = {e['path']: e for e in receipt['installedAfter']}
        generated = {'hybridclr/generated/AssemblyManifest.cpp', 'hybridclr/generated/MethodBridge.cpp',
                     'hybridclr/generated/UnityVersion.h', 'hybridclr/generated/libil2cpp-version.txt'}
        for path, entry in before.items():
            if path not in generated:
                require(path in after and after[path]['sha256'] == entry['sha256'], 'Changed non-generated installed source: ' + path)
        require(set(after) - set(before) <= generated | {'vm/AssemblyShadowR03Probe.cpp'}, 'Unexplained native source addition')
        manifest = loads((state['project'] / 'source-inputs.json').read_text())
        for entry in manifest['files']:
            require(sha(state['project'] / entry['path']) == entry['sha256'], 'Managed source or baseline fixture changed')
        executables = [p for p in (app / 'Contents/MacOS').iterdir() if p.is_file()]
        require(len(executables) == 1, 'One actual Player executable required')
        info = subprocess.run(['lipo', '-archs', str(executables[0])], capture_output=True, text=True, timeout=30)
        require(info.returncode == 0 and info.stdout.strip() == 'arm64', 'Actual Player must be ARM64')
        state['executable'] = executables[0]
        return receipt

    def editor_tests(self):
        state = self.builds['candidate-release']
        result = self.root / 'editor-results.xml'
        self.command([self.unity, '-batchmode', '-nographics', '-projectPath', state['project'], '-runTests', '-testPlatform', 'EditMode',
                      '-testResults', result, '-logFile', self.root / 'editor-tests.log'], 3600)
        tree = ET.parse(result).getroot()
        cases = list(tree.iter('test-case'))
        require(tree.attrib.get('result') == 'Passed' and len(cases) > 35, 'Nonzero real Editor test execution required')
        require(not any(c.get('result') == 'Failed' for c in cases), 'Editor failures')
        required = [c['id'] for c in loads((self.root / 'host/admission/results.json').read_text())['cases']]
        for test_id in required:
            found = [c for c in cases if 'R03EvolutionContractTests.RealDllEvolutionContract' in c.get('fullname', '') and test_id in c.get('fullname', '')]
            require(len(found) == 1 and found[0].get('result') == 'Passed', 'Missing, repeated or failed Editor contract: ' + test_id)
        cycle = [c for c in cases if c.get('fullname', '').endswith('GraphAndInputTests.CyclesReportClosedPath')]
        require(len(cycle) == 1 and cycle[0].get('result') == 'Passed', 'Actual target-cycle Editor regression required')
        return {'xml': str(result), 'sha256': sha(result), 'cases': len(cases), 'passed': sum(c.get('result') == 'Passed' for c in cases),
                'skipped': sum(c.get('result') == 'Skipped' for c in cases), 'r03RequiredIds': required}

    def player(self, case):
        self.verify_build(case['role'])
        state = self.builds[case['role']]
        root = self.root / 'players' / case['id']
        root.mkdir(parents=True)
        run_id, dlls = uuid.uuid4().hex, []
        for path in case['dlls']:
            entry = self.fixture_files[path]
            require(sha(self.fixture_root / path) == entry['sha256'], 'DLL changed before launch')
            dlls.append({'name': entry['assembly'], 'path': str(self.fixture_root / path), 'sha256': entry['sha256']})
        request = {'schemaVersion': 1, 'runId': run_id, 'caseId': case['id'], 'baselineId': 'R03-Isolated-' + case['role'],
                   'candidates': ['A', 'B', 'Layout', 'Methods', 'R03Contract'], 'stable': ['mscorlib'], 'roots': [d['name'] for d in dlls],
                   'dlls': dlls, 'invokeAssembly': case['invoke'], 'observeMethod': case.get('observeMethod', False),
                   'oldExecutionGuard': case.get('oldExecutionGuard', False), 'noPatch': case.get('noPatch', False)}
        write(root / 'request.json', request)
        launch = self.command([state['executable'], '-batchmode', '-nographics', '-r03Request', root / 'request.json',
                               '-r03Output', root / 'raw.json', '-r03RunId', run_id, '-logFile', root / 'Player.log'], 180)
        raw = loads((root / 'raw.json').read_text())
        verdict = verify_raw(request, raw, case, sha(root / 'request.json'), launch['pid'])
        verdict.update({'rawSha256': sha(root / 'raw.json'), 'requestSha256': sha(root / 'request.json'),
                        'buildReceiptSha256': sha(state['root'] / 'build-receipt.json'), 'launchPid': launch['pid'], 'runId': run_id})
        write(root / 'verification.json', verdict)
        return verdict

    def python_tests(self):
        receipt = self.command([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', ROOT, '-p', 'test_*.py', '-v'])
        return {'commandReceipt': receipt, 'scope': 'Synthetic verifier/filesystem contracts, not Player evidence'}

    def execute(self):
        self.cell('entry-authority', self.authority)
        self.cell('verifier-contracts', self.python_tests, ('entry-authority',))
        self.cell('reference-sources', self.reference_worktrees, ('entry-authority',))
        self.cell('host-baseline-graph', lambda: self.managed('HostTests', 'baseline-graph', self.references['hybridclr_unity'], 'baseline'), ('reference-sources',))
        self.cell('host-candidate-graph', lambda: self.managed('HostTests', 'candidate-graph', phase='candidate'), ('entry-authority',))
        self.cell('host-admission', lambda: self.managed('AdmissionTests', 'admission'), ('entry-authority',))
        self.cell('player-fixtures', self.fixtures, ('host-admission',))
        for role in self.matrix['roles']:
            name = role['id']
            deps = ('player-fixtures', 'reference-sources', 'verifier-contracts') if not role['candidate'] else ('player-fixtures', 'entry-authority', 'verifier-contracts')
            self.cell('prepare-' + name, lambda r=role: self.prepare_project(r), deps)
            self.cell('build-' + name, lambda r=role: self.build(r), ('prepare-' + name,))
        self.cell('editor-tests', self.editor_tests, ('prepare-candidate-release', 'host-admission'))
        for case in self.matrix['cases']:
            self.cell(case['id'], lambda c=case: self.player(c), ('build-' + case['role'],))
        self.cell('final-authority', self.authority)
        require(len(self.cells) == 36 and len({r['id'] for r in self.cells}) == 36, 'Exact thirty-six-cell execution ledger')
        summary = {'schemaVersion': 1, 'kind': 'R03ConservativeLocalBatch', 'repositories': self.pins,
                   'matrixSha256': sha(ROOT / 'player-cases.json'), 'cells': self.cells,
                   'retainedReferenceWorktrees': {k: str(v) for k, v in self.references.items()},
                   'result': 'ReturnRequired' if self.failed else 'EvidenceReadyForPrimaryReview', 'R03Accepted': False, 'H2Passed': False,
                   'pureInterpreterExpansionEnabled': False, 'fullLegacyRegressionAcceptance': False}
        result = finalize(self.root, summary)
        return 0 if result['result'] == 'EvidenceReadyForPrimaryReview' and result['sealStatus'] == 'Passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--unity', required=True)
    parser.add_argument('--demo-commit', required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.demo_commit) is not None, 'Exact published demo HEAD required')
    raise SystemExit(Batch(args.workspace, args.output, args.unity, args.demo_commit).execute())
