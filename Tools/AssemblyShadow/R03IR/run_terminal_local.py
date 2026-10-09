#!/usr/bin/env python3
"""R03 IR-R03-02: one new four-process native terminal-entry diagnostic batch.

Distinct from historical 90-cell S. Never rerun, replace, or modify S/R/Q/P/O/N.
Only fresh copied isolated Unity projects and unused output roots are written.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import uuid

HERE = Path(__file__).resolve().parent
R03 = HERE.parent / 'R03'
sys.path.insert(0, str(R03))
from run_local import Batch, ROOT, REPOS
from batch_contract import loads, require, sha
from batch_evidence import finalize, write


def prepare_ir(batch, role):
    observed = batch.prepare_project(role)
    project = Path(observed['project'])
    relative = 'Assets/R03TerminalPlayer.cs'
    source = HERE / 'PlayerProject/R03TerminalPlayer.cs'
    target = project / relative
    require(source.is_file() and not target.exists(), 'Unique Primary IR Player source')
    shutil.copyfile(source, target)
    manifest = project / 'source-inputs.json'
    record = loads(manifest.read_text())
    require(not any(row['path'] == relative for row in record['files']), 'No duplicate IR source')
    record['files'].append({'path': relative, 'sha256': sha(target),
                            'origin': {'kind': 'R03IRPrimarySupplement', 'source': str(source),
                                       'demoCommit': batch.pins['hybridclr_demo']}})
    manifest.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    config_path = batch.root / 'builds' / role['id'] / 'config.json'
    config = loads(config_path.read_text())
    config['sourceManifestSha256'] = sha(manifest)
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + '\n')
    batch.builds[role['id']]['config'] = config
    require(sha(target) == sha(source) and config['sourceManifestSha256'] == sha(manifest),
            'Exact IR build input')
    return {'project': str(project), 'sourceSha256': sha(target),
            'sourceManifestSha256': sha(manifest), 'configuration': str(config_path)}


def verify_ir(raw, request, launch, build_sha):
    require(type(raw) is dict and raw.get('schemaVersion') == 1 and
            raw.get('kind') == 'R03IRPostPoisonEntryV1' and raw.get('acceptance') is False,
            'Actual non-authorizing IR Player result contract')
    require(raw.get('result') == 'Passed' and not raw.get('error'), 'Player witness must explicitly pass')
    require(raw.get('runId') == request['runId'] and raw.get('caseId') == request['caseId'] and
            raw.get('stimulus') == request['stimulus'], 'Exact request identity')
    require(type(raw.get('processId')) is int and raw['processId'] == launch['pid'], 'Owned fresh Player process')
    require(raw.get('unityVersion') == '2022.3.62f2' and raw.get('platform') == 'OSXPlayer',
            'Actual Unity 2022.3 Player target')
    if request['stimulus'] == 'off':
        require(raw.get('initialState') == raw.get('finalState') == 0 and
                raw.get('prePositive') is True and raw.get('preCanaryCount') == 1 and
                raw.get('finalCanaryCount') == 2, 'Feature OFF ordinary calls')
        require(not raw.get('activeReflectionAttempted') and not raw.get('activeDelegateAttempted') and
                not raw.get('aotReflectionAttempted'), 'No synthetic terminal OFF probe')
    else:
        require(raw.get('initialState') == 6 and raw.get('poisonedState') == raw.get('finalState') == 9 and
                raw.get('prePositive') is True and raw.get('preActiveReflection') == 42 and
                raw.get('preActiveDelegate') == 42 and raw.get('preCanaryCount') == 1,
                'Current valid shadow method and AOT canary actually executed pre-poison')
        for prefix in ('activeReflection', 'activeDelegate', 'aotReflection'):
            require(raw.get(prefix + 'Attempted') is True and raw.get(prefix + 'Succeeded') is False and
                    isinstance(raw.get(prefix + 'Exception'), str) and raw[prefix + 'Exception'],
                    'Actual rejected post-poison attempted entry: ' + prefix)
        require(raw.get('finalCanaryCount') == raw.get('preCanaryCount') and
                raw.get('recoveryStable') is True and raw.get('fixedDiagnosticsReadable') is True and
                raw.get('firstRecovery') == raw.get('finalRecovery'), 'No body side effects or first-failure mutation')
        recovery = loads(raw['firstRecovery'])
        require(recovery.get('published') is True and recovery.get('stateCode') == 9 and
                recovery.get('disposition') == 'RestartRequired' and
                recovery.get('terminalFailureCode') in (13, 21), 'Actual first terminal failure')
        if request['stimulus'] == 'baseline-owner':
            require(recovery['terminalFailureCode'] == 21, 'Captured baseline-owner failure reason')
            native = loads(raw['nativeGuardJson'])
            require(native.get('available') is True and native.get('activeGuard') == 1 and
                    native.get('baselineGuard') == 0 and native.get('caughtOldGuard') == 1 and
                    native.get('stateCode') == 9 and raw.get('nativeStimulusReturn') == 1,
                    'Actual caught old-baseline managed failure')
        else:
            require(recovery['terminalFailureCode'] == 13 and raw.get('nativeStimulusReturn') == 1,
                    'Production type-resolution failure boundary was exercised')
    return {'kind': 'R03IRVerifiedPostPoisonPlayer', 'result': 'Passed',
            'caseId': request['caseId'], 'stimulus': request['stimulus'],
            'buildReceiptSha256': build_sha, 'runtimeAcceptance': False,
            'R03Accepted': False, 'H2Passed': False}


def player(batch, case):
    role = case['role']
    batch.verify_build(role)
    state = batch.builds[role]
    root = batch.root / 'players' / case['id']
    root.mkdir(parents=True)
    dll = batch.fixture_files['virtual-slot/Methods.dll']
    input_path = batch.fixture_root / 'virtual-slot/Methods.dll'
    if case['stimulus'] == 'off':
        dll_path, dll_hash = '', ''
    else:
        require(sha(input_path) == dll['sha256'], 'Exact unchanged compiled target DLL')
        dll_path, dll_hash = str(input_path), dll['sha256']
    nonce = uuid.uuid4().hex
    request = {'schemaVersion': 1, 'runId': nonce, 'caseId': case['id'],
               'baselineId': 'R03IR-Isolated-' + role, 'dllPath': dll_path,
               'dllSha256': dll_hash, 'stimulus': case['stimulus']}
    write(root / 'request.json', request)
    cmd = [str(state['executable']), '-batchmode', '-nographics',
           '-r03IrRequest', root / 'request.json', '-r03IrOutput', root / 'raw.json',
           '-r03IrRunId', nonce, '-logFile', root / 'Player.log']
    launch = batch.command(cmd, 180)
    require((root / 'raw.json').is_file(), 'Fresh Player raw evidence must exist')
    raw = loads((root / 'raw.json').read_text())
    bind = {'requestSha256': sha(root / 'request.json'), 'rawSha256': sha(root / 'raw.json'),
            'buildReceiptSha256': sha(state['root'] / 'build-receipt.json'),
            'launchPid': launch['pid'], 'runId': nonce, 'argv': [str(x) for x in cmd]}
    try:
        require(raw.get('requestSha256') == bind['requestSha256'], 'Raw/launch request digest')
        verdict = verify_ir(raw, request, launch, bind['buildReceiptSha256'])
    except Exception as error:
        write(root / 'verification.json', dict(bind, result='Failed', error=str(error)))
        raise
    verdict.update(bind)
    write(root / 'verification.json', verdict)
    return verdict


def execute(workspace, output, unity, demo_commit):
    require(HERE == Path(workspace).resolve() / 'hybridclr_demo/Tools/AssemblyShadow/R03IR',
            'Execute from the owning exact demo checkout')
    batch = Batch(workspace, output, unity, demo_commit)
    batch.cell('entry-authority', batch.authority)
    batch.cell('real-dll-fixtures', batch.fixtures, ('entry-authority',))
    roles = [r for r in batch.matrix['roles'] if r['id'] in
             ('candidate-release', 'candidate-debug', 'candidate-off')]
    require(len(roles) == 3, 'Three required native build roles')
    for role in roles:
        name = role['id']
        batch.cell('prepare-' + name, lambda r=role: prepare_ir(batch, r), ('real-dll-fixtures',))
        batch.cell('build-' + name, lambda r=role: batch.build(r), ('prepare-' + name,))
    cases = [
        {'id':'IR-R03-02-release-baseline', 'role':'candidate-release', 'stimulus':'baseline-owner'},
        {'id':'IR-R03-02-debug-baseline', 'role':'candidate-debug', 'stimulus':'baseline-owner'},
        {'id':'IR-R03-02-release-type', 'role':'candidate-release', 'stimulus':'type-resolution'},
        {'id':'IR-R03-02-off', 'role':'candidate-off', 'stimulus':'off'}
    ]
    for case in cases:
        batch.cell(case['id'], lambda c=case: player(batch, c), ('build-' + case['role'],))
    summary = {'schemaVersion':1, 'kind':'R03IRFocusedTerminalLocalBatch',
        'result':'ReturnRequired' if batch.failed else 'FocusedEvidenceReadyForPrimaryReview',
        'repositories':batch.pins, 'cells':batch.cells, 'freshBuilds':3,
        'freshPlayers':4, 'scope':'baseline-owner + synthetic type-failure + OFF controls; not complete IR-R03-02',
        'initializerFailure': 'NotRun', 'capturedGenericFailure': 'NotRun',
        'fullLegacyRegressionAcceptance':False, 'R03Accepted':False, 'H2Passed':False,
        'qualificationApproved':False, 'pureInterpreterExpansionEnabled':False}
    result = finalize(batch.root, summary)
    return 0 if (result['result'] == 'FocusedEvidenceReadyForPrimaryReview' and
                 result['sealStatus'] == 'Passed') else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('workspace','output','unity','demo-commit'):
        parser.add_argument('--' + field, required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.demo_commit) is not None, 'Exact pushed demo SHA')
    raise SystemExit(execute(args.workspace, args.output, args.unity, args.demo_commit))
