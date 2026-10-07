#!/usr/bin/env python3
"""Admit one unused complete R03 batch only after measured storage prerequisites.

Default is diagnostics only. --execute is a conditional, single-use launch,
not authorization to reclaim evidence or change the original batch semantics.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03Completion'))
from run_completion import CompletionBatch
from run_local import identity, git, REPOS
from batch_contract import loads
import storage_guard as storage

# These actions must still be attempted when storage observations fail. Their
# existing core prerequisites/receipts remain authoritative; no new cleanup.
ESSENTIAL = frozenset(('resource-p05-restore', 'final-authority'))


class StorageCheckedBatch(CompletionBatch):
    def __init__(self, *args, session, **kwargs):
        self.storage_session = session
        self.storage_phase = 'constructor'
        super().__init__(*args, **kwargs)

    def cell(self, name, action, dependencies=()):
        def checked_action():
            self.storage_phase = name
            try:
                self.storage_session.before(name, cleanup=name in ESSENTIAL)
                return action()
            except BaseException as error:
                self.storage_session.record_failure(name, error)
                raise
            finally:
                self.storage_session.observe('cell-after')
        # Retains the real cell scheduler, IDs, dependencies, error states and
        # failed/blocked continuation; no extra acceptance cell is invented.
        return super().cell(name, checked_action, dependencies)

    def command(self, args, timeout=600):
        phase = self.storage_phase + '/command-' + str(self.command_count + 1)
        try:
            self.storage_session.before(phase, cleanup=self.storage_phase in ESSENTIAL)
            return super().command(args, timeout)
        except BaseException as error:
            self.storage_session.record_failure(phase, error)
            raise
        finally:
            self.storage_session.observe('command-after')


def validate_locations(workspace, output, evidence, retained):
    workspace, output, evidence, retained = map(storage.canonical, (workspace, output, evidence, retained))
    storage.require(workspace.is_dir() and retained.is_dir(), 'Existing workspace and retained Q root required')
    for path in (output, evidence):
        storage.require(not path.exists() and path.parent.is_dir(), 'Unused immediate output under an existing parent required: ' + str(path))
        storage.require(not path.is_relative_to(workspace) and not workspace.is_relative_to(path), 'New outputs must be outside the owning workspace')
        storage.require(not path.is_relative_to(retained) and not retained.is_relative_to(path), 'Retained Q must not overlap new outputs')
    storage.require(not output.is_relative_to(evidence) and not evidence.is_relative_to(output), 'Sidecar must be outside the batch seal/root')
    storage.require(not retained.is_relative_to(workspace) and not workspace.is_relative_to(retained), 'Retained Q must be a separate root')
    return workspace, output, evidence, retained


def source_authority(workspace, demo_commit):
    storage.require(re.fullmatch('[0-9a-f]{40}', demo_commit) is not None, 'Exact final pushed SHA required')
    storage.require(HERE == workspace / 'hybridclr_demo/Tools/AssemblyShadow/R03Storage', 'Run storage tools from the owning checkout')
    pins = loads((HERE.parent / 'R03Completion/source-pins.json').read_text())
    pins = dict(pins, hybridclr_demo=demo_commit)
    records = [identity(workspace / name, pins[name]) for name in REPOS]
    files = [HERE / 'storage_guard.py', Path(__file__).resolve(), HERE.parent / 'R03Completion/run_completion.py',
             HERE.parent / 'R03Completion/legacy_runtime.py', HERE.parent / 'R03/run_local.py',
             HERE.parent / 'R03/source-pins.json', HERE.parent / 'R03Completion/source-pins.json']
    return {'repositories': records, 'files': [{'path': str(p), 'sha256': storage.digest(p)} for p in files]}


def run(args):
    storage.require(sys.platform == 'darwin', 'Local storage admission is macOS-only; CI tests are separate')
    workspace, output, evidence, retained = validate_locations(args.workspace, args.output, args.storage_evidence, args.retained_q)
    authority = source_authority(workspace, args.demo_commit)
    # command_lifetime.child_environment pins every spawned command's TMPDIR
    # to this location. Relocating only the batch would not relocate temp I/O.
    paths = {'batch': output, 'workspace': workspace, 'childTemp': Path('/private/tmp'),
             'pythonTemp': Path(__import__('tempfile').gettempdir()).resolve(), 'sidecar': evidence,
             'restoredCapture': output / 'projects/resource-complete/_temp/AssemblyShadow/R03CompletionArtifacts/return-baseline'}
    for name in REPOS:
        repo = workspace / name
        common = Path(git(repo, 'rev-parse', '--git-common-dir'))
        paths['gitCommon-' + name] = (repo / common).resolve() if not common.is_absolute() else common.resolve()
    session = storage.StorageSession(evidence, paths)
    started = False
    code = 2
    report = None
    try:
        storage.write_new(evidence / 'source-authority.json', authority)
        admission = session.admit(retained)
        print(json.dumps({'storageAdmission': admission['state'], 'evidence': str(evidence),
                          'batchStarted': False, 'requiredBytes': admission.get('requiredAvailableBytesEachLocation')}), flush=True)
        if admission['state'] != 'Admitted':
            code = 2
        elif not args.execute:
            code = 0
        else:
            # Do not reuse a diagnostic-only admission: the executing invocation
            # always obtains its own measurement/probes and checks immediately again.
            latest = session.observe('immediately-before-constructor')
            storage.require(latest is not None, 'Immediate storage check unavailable')
            storage.capacity_ok(latest, admission['requiredAvailableBytesEachLocation'], session.devices)
            storage.require(session.problem is None, 'Storage prerequisite lost before launch')
            storage.require(not output.exists(), 'Batch root appeared during preflight; do not reuse it')
            session.start()
            storage.write_new(evidence / 'launch-intent.json', {
                'workspace': str(workspace), 'output': str(output), 'demoCommit': args.demo_commit,
                'unity': str(args.unity), 'retainedQ': str(retained), 'startedUtc': storage.utc(),
                'entryPoint': str(Path(__file__).resolve()), 'coreEntryPoint': str(HERE.parent / 'R03Completion/run_completion.py'),
                'pid': os.getpid(), 'expectedCells': 90, 'expectedFreshBuilds': 6, 'expectedPlayers': 59,
                'runtimeAcceptance': False})
            started = True
            code = StorageCheckedBatch(workspace, output, args.unity, args.demo_commit, session=session).execute()
            # Supplemental observation does not rewrite any sealed core result.
            for record in authority['files']:
                storage.require(storage.digest(record['path']) == record['sha256'], 'Owning source changed during execution')
    except BaseException as error:
        code = 2 if not started else 1
        session.record_failure('entry-point', error)
        raise
    finally:
        report = session.finish(batch_started=started, batch_exit=code if started else None)
        result_path = output / 'LOCAL_BATCH_RESULT.json'
        storage.write_new(evidence / 'dispatch.json', {
            'batchStarted': started, 'batchExitCode': code if started else None,
            'coreResultPath': str(result_path) if result_path.is_file() else None,
            'coreResultSha256': storage.digest(result_path) if result_path.is_file() else None,
            'storageSessionSha256': storage.digest(evidence / 'session.json'),
            'runtimeAcceptance': False, 'R03Accepted': False, 'H2Passed': False,
            'qualificationApproved': False, 'pureInterpreterExpansionEnabled': False})
    return code if not started or report['state'] == 'Passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace', 'output', 'unity', 'demo-commit', 'storage-evidence', 'retained-q'):
        parser.add_argument('--' + flag, required=True)
    parser.add_argument('--execute', action='store_true', help='Admit then execute exactly once; otherwise diagnose only')
    try:
        raise SystemExit(run(parser.parse_args()))
    except storage.StorageBlocked as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
