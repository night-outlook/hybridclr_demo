#!/usr/bin/env python3
"""One unused R03 batch. No product source edits, retries, or acceptance promotion."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import uuid
import xml.etree.ElementTree as ET

from batch_contract import ContractError, loads, require, sha, verify_raw

REPOS = ('hybridclr_demo', 'hybridclr', 'hybridclr_unity', 'il2cpp_plus')
BRANCH = 'codex/assembly-shadow-r01b-h1'
ROOT = Path(__file__).resolve().parent
REFERENCE_PACKAGE = 'b936a495ade1691ebb6f3bab8fdff3ef34f6f192'


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(repo, *args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, env=env, timeout=120)
    require(result.returncode == 0, 'Git command failed: ' + ' '.join(args[:2]))
    return result.stdout.strip()


def identity(repo, expected, branch=True, remote=True):
    repo = Path(repo).resolve()
    require(Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() == repo, 'Not the owning checkout: ' + repo.name)
    require(git(repo, 'rev-parse', 'HEAD') == expected, 'Exact HEAD mismatch: ' + repo.name)
    require(not git(repo, 'status', '--porcelain=v1', '--untracked-files=all'), 'Dirty owning repository: ' + repo.name)
    url = git(repo, 'remote', 'get-url', 'origin')
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)(night-outlook/(?:hybridclr_demo|hybridclr|hybridclr_unity|il2cpp_plus))(?:\.git)?', url)
    require(match is not None and match.group(1) == 'night-outlook/' + repo.name, 'Canonical repository identity mismatch')
    if branch:
        require(git(repo, 'branch', '--show-current') == BRANCH, 'Working branch mismatch: ' + repo.name)
    if remote:
        result = git(repo, 'ls-remote', 'origin', 'refs/heads/' + BRANCH).split()
        require(result == [expected, 'refs/heads/' + BRANCH], 'Remote HEAD mismatch: ' + repo.name)
    return {'repository': match.group(1), 'path': str(repo), 'commit': expected, 'branch': BRANCH if branch else '(detached)', 'remoteHeadVerified': remote}


class Batch:
    def __init__(self, workspace, output, unity, demo_commit):
        self.workspace = Path(workspace).resolve()
        self.root = Path(output).resolve()
        self.unity = str(Path(unity).resolve())
        require(self.root != self.workspace and not self.root.exists(), 'Batch destination must be unused')
        self.root.mkdir(parents=True)
        self.pins = loads((ROOT / 'source-pins.json').read_text())
        self.pins['hybridclr_demo'] = demo_commit
        self.matrix = loads((ROOT / 'player-cases.json').read_text())
        require(len(self.matrix['cases']) == 19 and len({c['id'] for c in self.matrix['cases']}) == 19, 'Exact nineteen-cell native matrix')
        require(Path(self.unity).is_file(), 'Exact Unity executable is required')
        self.cells = []
        self.outputs = {}
        self.command_count = 0
        self.failed = False
        self.references = {}
        self.builds = {}

    def command(self, args, timeout=600):
        self.command_count += 1
        root = self.root / 'commands' / ('%04d' % self.command_count)
        root.mkdir(parents=True)
        args = [str(x) for x in args]
        start = time.time()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0', TMPDIR='/private/tmp')
        timed_out = False
        with (root / 'stdout.log').open('wb') as out, (root / 'stderr.log').open('wb') as err:
            process = subprocess.Popen(args, stdout=out, stderr=err, env=env, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
        receipt = {'command': args, 'pid': process.pid, 'startedUtcEpoch': start, 'endedUtcEpoch': time.time(),
                   'exitCode': code, 'timeout': timed_out, 'stdoutSha256': sha(root / 'stdout.log'), 'stderrSha256': sha(root / 'stderr.log')}
        write(root / 'command.json', receipt)
        require(code == 0 and not timed_out, 'Command failed; preserved receipt: ' + str(root / 'command.json'))
        return receipt

    def cell(self, name, action, dependencies=()):
        row = {'id': name, 'result': 'Blocked', 'dependencies': list(dependencies)}
        if all(self.outputs.get(d, False) for d in dependencies):
            try:
                row['evidence'] = action()
                row['result'] = 'Passed'
                self.outputs[name] = True
            except Exception as error:
                row['result'] = 'Failed'
                row['error'] = str(error)
                self.failed = True
                self.outputs[name] = False
        else:
            row['reason'] = 'Required prerequisite did not pass; no substitute or retry.'
            self.outputs[name] = False
            self.failed = True
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
        binary = self.root / 'bin' / output
        intermediate = self.root / 'obj' / output
        self.command(['dotnet', 'build', ROOT / project / (project + '.csproj'), '-c', 'Release', '--output', binary,
                      '-p:PackageRoot=' + str(package), '-p:BaseIntermediateOutputPath=' + str(intermediate) + '/'])
        result_root = self.root / 'host' / output
        arguments = ['--phase', phase] if phase else []
        self.command(['dotnet', binary / (project + '.dll'), *arguments, '--output', result_root])
        result_file = result_root / ('inventory.json' if project == 'PlayerFixtures' else 'results.json')
        result = loads(result_file.read_text())
        if project != 'PlayerFixtures':
            require(result['result'] == 'Passed' and result['failures'] == 0, 'Managed contract failures')
            expected = 35 if project == 'AdmissionTests' else 9
            require(len(result['cases']) == expected and len({x['id'] for x in result['cases']}) == expected, 'Managed contract identity count')
        return {'result': str(result_file), 'sha256': sha(result_file)}

    def fixtures(self):
        result = self.managed('PlayerFixtures', 'player-fixtures')
        self.fixture_root = self.root / 'host' / 'player-fixtures'
        inventory = loads((self.fixture_root / 'inventory.json').read_text())
        require(len(inventory['files']) == 15 and len({f['path'] for f in inventory['files']}) == 15, 'Complete fixture inventory')
        self.fixture_files = {f['path']: f for f in inventory['files']}
        for path, entry in self.fixture_files.items():
            require(sha(self.fixture_root / path) == entry['sha256'], 'Actual fixture hash mismatch')
        return result

    def prepare_project(self, role):
        role_id = role['id']
        project = self.root / 'projects' / role_id
        project.mkdir(parents=True)
        for name in ('Assets/Editor', 'Assets/R03', 'Assets/Fixtures', 'Packages', 'ProjectSettings'):
            (project / name).mkdir(parents=True)
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
        source_manifest = loads((self.workspace / 'hybridclr_demo/Packages/manifest.json').read_text())
        dependencies = {k: v for k, v in source_manifest['dependencies'].items() if k.startswith('com.unity.modules.') or k in ('com.unity.test-framework', 'com.unity.ugui')}
        dependencies['com.code-philosophy.hybridclr'] = 'file:' + str(self.workspace / 'hybridclr_unity')
        write(project / 'Packages/manifest.json', {'dependencies': dependencies, 'testables': ['com.code-philosophy.hybridclr']})
        (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2022.3.62f2\n')
        (project / 'Assets/R03/link.xml').write_text('<linker>' + ''.join('<assembly fullname="' + name + '" preserve="all" />' for name in ('Layout', 'Methods', 'A', 'B', 'R03Contract', 'Assembly-CSharp')) + '</linker>\n')
        native_repos = {name: self.workspace / name for name in REPOS}
        native_pins = {name: self.pins[name] for name in REPOS}
        if not role['candidate']:
            for name, revision in self.matrix['referenceCore'].items():
                native_repos[name], native_pins[name] = self.references[name], revision
        names = {'hybridclr': 'hybridclr', 'hybridclr_unity': 'hybridclrUnity', 'il2cpp_plus': 'il2cppPlus', 'hybridclr_demo': 'demo'}
        pins = {'schemaVersion': 1, 'unityVersion': '2022.3.62f2', 'target': 'StandaloneOSX'}
        for name, key in names.items():
            pins[key] = {'url': 'https://github.com/night-outlook/' + name + '.git', 'revision': native_pins[name], 'localPath': os.path.relpath(native_repos[name], project)}
        write(project / 'ProjectSettings/AssemblyShadowSourcePins.json', pins)
        write(project / 'source-inputs.json', {'schemaVersion': 1, 'demoCommit': self.pins['hybridclr_demo'], 'files': origins,
              'fixtureInventorySha256': sha(self.fixture_root / 'inventory.json'), 'repositories': native_pins,
              'note': 'Current package and identical new test harness on both native cores; reference is not the old accepted Player.'})
        build_root = self.root / 'builds' / role_id
        build_root.mkdir(parents=True)
        overlay = ROOT / 'PlayerProject/AssemblyShadowR03Probe.cpp'
        config = {'schemaVersion': 1, 'projectPath': str(project), 'outputPath': str(build_root / 'R03Isolated.app'),
                  'receiptPath': str(build_root / 'build-receipt.json'), 'overlayPath': str(overlay), 'overlaySha256': sha(overlay),
                  'sourceManifestSha256': sha(project / 'source-inputs.json'), 'featureEnabled': role['feature'],
                  'diagnosticsLevel': 2 if role['feature'] else 0, 'cppConfiguration': role['cpp']}
        write(build_root / 'config.json', config)
        self.builds[role_id] = {'project': project, 'root': build_root, 'config': config}
        return {'project': str(project), 'config': str(build_root / 'config.json')}

    def build(self, role):
        state = self.builds[role['id']]
        self.command([self.unity, '-batchmode', '-nographics', '-quit', '-buildTarget', 'osx', '-projectPath', state['project'],
                      '-executeMethod', 'AssemblyShadow.R03.Editor.R03Build.Build', '-r03Config', state['root'] / 'config.json',
                      '-logFile', state['root'] / 'Editor.log'], 7200)
        self.verify_build(role['id'])
        return {'receipt': str(state['root'] / 'build-receipt.json'), 'sha256': sha(state['root'] / 'build-receipt.json')}

    def verify_build(self, role_id):
        state = self.builds[role_id]
        receipt = loads((state['root'] / 'build-receipt.json').read_text())
        require(receipt['result'] == 'Passed' and receipt['nonGeneratedCorePreserved'] is True and receipt['errors'] == 0, 'Successful verified native build required')
        require(receipt['testOverlaySha256'] == sha(ROOT / 'PlayerProject/AssemblyShadowR03Probe.cpp') and
                receipt['sourceManifestSha256'] == sha(state['project'] / 'source-inputs.json'), 'Native test overlay and managed source manifest binding')
        app = Path(state['config']['outputPath'])
        actual = {str(p.relative_to(app)): p for p in app.rglob('*') if p.is_file()}
        expected = {f['path']: f for f in receipt['playerFiles']}
        require(set(actual) == set(expected), 'Complete Player file membership')
        for name, path in actual.items():
            require(sha(path) == expected[name]['sha256'] and path.stat().st_size == expected[name]['size'], 'Player changed: ' + name)
        manifest = loads((state['project'] / 'source-inputs.json').read_text())
        for entry in manifest['files']:
            require(sha(state['project'] / entry['path']) == entry['sha256'], 'Managed source or baseline fixture changed')
        executables = [p for p in (app / 'Contents/MacOS').iterdir() if p.is_file()]
        require(len(executables) == 1, 'One actual Player executable required')
        result = subprocess.run(['lipo', '-archs', str(executables[0])], capture_output=True, text=True, timeout=30)
        require(result.returncode == 0 and result.stdout.strip() == 'arm64', 'Actual Player must be ARM64')
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
        run_id = uuid.uuid4().hex
        dlls = []
        for path in case['dlls']:
            entry = self.fixture_files[path]
            require(sha(self.fixture_root / path) == entry['sha256'], 'Actual DLL changed before launch')
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

    def seal(self):
        # The focused evidence archive excludes rebuildable caches, detached Git
        # worktrees and SDK installations. Their exact source/install inventories
        # and live roots remain in build receipts. This is not R02's full seal.
        files = []
        exclusions = []
        for path in sorted(self.root.rglob('*')):
            relative = path.relative_to(self.root)
            parts = relative.parts
            excluded = parts[0] in ('reference-worktrees', 'bin', 'obj') or
            False
            if parts[0] == 'projects' and len(parts) > 2 and parts[2] in ('Library', 'Temp', 'Logs', 'HybridCLRData', 'obj'):
                excluded = True
            if excluded or not path.is_file():
                continue
            require(not path.is_symlink(), 'Unexpected symlink in focused evidence: ' + str(relative))
            files.append({'path': str(relative), 'size': path.stat().st_size, 'sha256': sha(path)})
        exclusions = ['reference-worktrees/**', 'bin/**', 'obj/**', 'projects/*/{Library,Temp,Logs,HybridCLRData,obj}/**']
        write(self.root / 'evidence-index.json', {'schemaVersion': 1, 'kind': 'R03FocusedEvidenceIndex', 'files': files,
              'excludedLiveRoots': exclusions, 'fullR02Seal': False, 'runtimeAcceptance': False})
        archive = self.root / 'evidence.tar.gz'
        with tarfile.open(archive, 'x:gz') as output:
            for item in files:
                output.add(self.root / item['path'], arcname=item['path'], recursive=False)
            output.add(self.root / 'evidence-index.json', arcname='evidence-index.json', recursive=False)
        with tarfile.open(archive, 'r:gz') as source:
            members = {m.name: m for m in source.getmembers()}
            require(set(members) == {f['path'] for f in files} | {'evidence-index.json'}, 'Archive membership')
            for item in files:
                stream = source.extractfile(members[item['path']])
                digest = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block)
                require(digest.hexdigest() == item['sha256'] and members[item['path']].size == item['size'], 'Archive byte authentication')
        receipt = {'archiveSha256': sha(archive), 'indexSha256': sha(self.root / 'evidence-index.json'), 'members': len(files),
                   'boundedEvidenceOnly': True, 'runtimeAcceptance': False}
        write(self.root / 'seal-receipt.json', receipt)
        return receipt

    def execute(self):
        self.cell('entry-authority', self.authority)
        self.cell('reference-sources', self.reference_worktrees, ('entry-authority',))
        self.cell('host-baseline-graph', lambda: self.managed('HostTests', 'baseline-graph', self.references['hybridclr_unity'], 'baseline'), ('reference-sources',))
        self.cell('host-candidate-graph', lambda: self.managed('HostTests', 'candidate-graph', phase='candidate'), ('entry-authority',))
        self.cell('host-admission', lambda: self.managed('AdmissionTests', 'admission'), ('entry-authority',))
        self.cell('player-fixtures', self.fixtures, ('host-admission',))
        for role in self.matrix['roles']:
            name = role['id']
            deps = ('player-fixtures', 'reference-sources') if not role['candidate'] else ('player-fixtures', 'entry-authority')
            self.cell('prepare-' + name, lambda r=role: self.prepare_project(r), deps)
            self.cell('build-' + name, lambda r=role: self.build(r), ('prepare-' + name,))
        self.cell('editor-tests', self.editor_tests, ('prepare-candidate-release', 'host-admission'))
        for case in self.matrix['cases']:
            self.cell(case['id'], lambda c=case: self.player(c), ('build-' + case['role'],))
        self.cell('final-authority', self.authority)
        summary = {'schemaVersion': 1, 'kind': 'R03ConservativeLocalBatch', 'repositories': self.pins,
                   'matrixSha256': sha(ROOT / 'player-cases.json'), 'cells': self.cells,
                   'result': 'ReturnRequired' if self.failed else 'EvidenceReadyForPrimaryReview', 'R03Accepted': False, 'H2Passed': False,
                   'pureInterpreterExpansionEnabled': False, 'fullLegacyRegressionAcceptance': False}
        write(self.root / 'LOCAL_BATCH_RESULT.json', summary)
        try:
            self.seal()
        except Exception as error:
            write(self.root / 'SEAL_FAILED.json', {'error': str(error), 'result': 'ReturnRequired'})
            return 1
        return 1 if self.failed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--unity', required=True)
    parser.add_argument('--demo-commit', required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.demo_commit) is not None, 'Exact published demo HEAD required')
    raise SystemExit(Batch(args.workspace, args.output, args.unity, args.demo_commit).execute())
