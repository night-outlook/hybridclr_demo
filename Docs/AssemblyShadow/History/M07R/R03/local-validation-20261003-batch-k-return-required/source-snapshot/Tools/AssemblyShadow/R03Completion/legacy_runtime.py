"""Fresh original M07/R00/early contracts under explicit copied-source authority.

No --allow-incomplete or legacy-startup fallback. Original artifact and semantic
verifiers are reused; the separate copy verifier replaces ONLY the Git-project
identity assumption. Observation statistics do not authorize a performance SLA.
"""
from pathlib import Path
import statistics
import sys
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'R03'))
import m07_results as m07
import r00_results as r00
import r01_early_results as early
from batch_contract import loads, require, sha
from batch_evidence import write
from unity_command import clean_outer
from fixture_authority import authenticate_copy
from execution_contract import verify as verify_execution

EARLY_CASES = (('Control-P03', 'Control', 'P03'), ('Control-P01', 'Control', 'P01'),
               ('OrdinaryFirst', 'OrdinaryFirst', 'P03'), ('OrdinaryAfterReserve', 'OrdinaryAfterReserve', 'P03'),
               ('Oversize', 'Oversize', 'P03'), ('Mismatch', 'Mismatch', 'P03'),
               ('Type', 'Type', 'P03'), ('Object', 'Object', 'P03'), ('Cctor', 'Cctor', 'P03'),
               ('NativeScript', 'NativeScript', 'P03'))


def inventory(batch):
    authenticate_copy(batch, batch.resource_config)
    return {str(p): sha(p) for p in sorted(batch.resource_context['inventory'])}


def launch(batch, args, folder, expected_exit=0, timeout=900):
    require(type(expected_exit) is int and expected_exit in (0, 1), 'Explicit known exit contract')
    command_root = batch.root / 'commands' / ('%04d' % (batch.command_count + 1))
    try:
        batch.command(args, timeout)
    except RuntimeError:
        if expected_exit != 1: raise
    receipt = loads((command_root / 'command.json').read_text())
    clean_outer(receipt, expected_exit)
    require(receipt['command'] == [str(x) for x in args], 'Exact Player argv binding')
    for stream in ('stdout', 'stderr'):
        require(sha(command_root / (stream + '.log')) == receipt[stream + 'Sha256'], 'Retained Player command stream')
    # Original log verifier expects one console file. Preserve BOTH exact streams
    # separately and explicitly concatenate them for the read-only log check.
    console = folder / 'console-combined.log'
    with console.open('xb') as out:
        out.write((command_root / 'stdout.log').read_bytes()); out.write((command_root / 'stderr.log').read_bytes())
    return receipt, {'commandReceipt': str(command_root / 'command.json'), 'commandSha256': sha(command_root / 'command.json'),
                     'console': str(console), 'consoleSha256': sha(console)}


def capsule(batch, folder, mode, patch='P03'):
    path = folder / 'early.capsule'
    expected = early.expected_capsule(batch.resource_context, mode, batch.resource_manifest, patch)
    early._capsule_for(batch.resource_context, mode, batch.resource_manifest, path, patch)
    require(early.capsule.decode(path.read_bytes()) == expected, 'Admitted capsule exact reconstruction')
    return path


def m07_case(batch, mode):
    require(mode in m07.MODES, 'Original M07 mode')
    context = batch.resource_context['context']
    folder = batch.root / 'resource-players' / mode; folder.mkdir(parents=True)
    result_dir = batch.root / 'm07-results'; result_dir.mkdir(exist_ok=True)
    result = result_dir / ('m07-' + mode + '.json')
    log = folder / 'Player.log'; early_result = folder / 'early.json'
    patch = m07.MODE_PATCH[mode]
    build = context['on' if patch else 'off']
    args = [batch.resource_context['runner'].executable_for(build['output']), '-batchmode', '-nographics',
            '-shadowM07Mode', mode, '-shadowM07Fixtures', batch.resource_manifest,
            '-shadowM07PlayerReceipt', build['path'], '-shadowM07Result', result, '-logFile', log]
    cap = capsule(batch, folder, 'Control', patch) if patch else None
    if cap: args += ['-shadowEarlyCapsule', cap, '-shadowEarlyCapsuleSha256', sha(cap), '-shadowEarlyResult', early_result]
    before = inventory(batch); verdict = {'result': 'Failed', 'case': mode}
    try:
        command, binding = launch(batch, args, folder)
        raw = loads(result.read_text()); require(raw['processId'] == command['pid'], 'Direct M07 launch PID')
        original = m07.verify_case(result, context['manifest'], context['baseline'], context['fixtures'],
                                   batch.resource_context['baselineResources'], context['on'], context['off'])
        if cap:
            observation = early.verify_early_receipt(early_result, cap, 'Control', command['pid'], batch.resource_context['profile'])
            early.verify_imported_snapshots(observation, raw)
            early.verify_startup_logs('Control', log, Path(binding['console']))
        require(inventory(batch) == before, 'M07 inputs changed during process')
        verdict = dict(binding, result='Passed', originalContract=original, launchPid=command['pid'],
                       sourceInputHashes=before, rawPath=str(result), rawSha256=sha(result),
                       earlyReceiptSha256=sha(early_result) if cap else '', fresh=True, R03Accepted=False)
        return verdict
    except Exception as error:
        verdict['error'] = str(error); raise
    finally: write(folder / 'verification.json', verdict)


def m07_summary(batch):
    verdict = m07.verify_suite(batch.resource_manifest, batch.root / 'm07-results', batch.resource_on,
                              batch.resource_off, allow_incomplete=False, replay_receipt=batch.resource_replay)
    require(verdict['resultPassed'] is True and len(verdict['modes']) == 14, 'Complete original M07 contract')
    write(batch.root / 'resource-contracts.json', {'kind': 'R03FreshM07Contracts', 'result': 'Passed',
          'originalVerifierOutput': verdict, 'profile': 'UnfencedDevelopmentBuild',
          'originalGateLabelIsNotNewHumanApproval': True, 'R03Accepted': False, 'H2Passed': False})
    return {'path': str(batch.root / 'resource-contracts.json'), 'sha256': sha(batch.root / 'resource-contracts.json'), 'modes': 14}


def r00_case(batch, mode, repetition):
    require(mode in r00.MODES and type(repetition) is int and 0 <= repetition < 3, 'Fixed original R00 selection')
    context = batch.resource_context['context']; build = context['off' if mode == r00.OFF_MODE else 'on']
    folder = batch.root / 'measurements' / mode / str(repetition); folder.mkdir(parents=True)
    result, log, early_result = folder / (mode + '.json'), folder / 'Player.log', folder / 'early.json'
    early_mode = 'Control' if mode in r00.MODES[1:3] else 'Baseline'
    patch = 'P01' if mode == 'R00-ON-P01' else 'P03'
    cap = capsule(batch, folder, early_mode, patch) if mode != r00.OFF_MODE else None
    request = {'schemaVersion': 1, 'kind': 'R03ExecutionSupplement', 'runId': uuid.uuid4().hex,
               'mode': mode, 'repetition': repetition, 'phases': ['statics', 'delegates', 'exceptions'],
               'output': str(folder / 'execution.json'), 'r00Result': str(result)}
    write(folder / 'request.json', request)
    args = [batch.resource_context['runner'].executable_for(build['output']), '-batchmode', '-nographics',
            '-shadowR00Mode', mode, '-shadowM07Fixtures', batch.resource_manifest, '-shadowM07PlayerReceipt', build['path'],
            '-shadowR00Result', result, '-shadowR03ExecutionRequest', folder / 'request.json', '-logFile', log]
    if cap: args += ['-shadowEarlyCapsule', cap, '-shadowEarlyCapsuleSha256', sha(cap), '-shadowEarlyResult', early_result]
    before = inventory(batch); verdict = {'result': 'Failed', 'mode': mode, 'repetition': repetition}
    try:
        command, binding = launch(batch, args, folder)
        raw = loads(result.read_text()); require(raw['processId'] == command['pid'], 'R00 direct process binding')
        row = {'resultPath': str(result), 'earlyCapsulePath': str(cap) if cap else '',
               'earlyCapsuleSha256': sha(cap) if cap else '', 'earlyResultPath': str(early_result) if cap else '',
               'earlyResultSha256': sha(early_result) if cap else ''}
        original = r00.verify_result(raw, mode, context, row, 'R01EarlyStartup', True)
        if cap:
            early.verify_early_receipt(early_result, cap, early_mode, command['pid'], batch.resource_context['profile'])
            early.verify_startup_logs(early_mode, log, Path(binding['console']))
        extra = verify_execution(request, loads((folder / 'execution.json').read_text()), raw,
                                 sha(folder / 'request.json'), sha(result), command['pid'], context)
        require(inventory(batch) == before, 'R00 source/artifact inputs changed during process')
        verdict = dict(binding, result='Passed', mode=mode, repetition=repetition, launchPid=command['pid'],
                       originalContract=original, executionSupplement=extra, rawPath=str(result), rawSha256=sha(result),
                       supplementSha256=sha(folder / 'execution.json'), sourceInputHashes=before, fresh=True,
                       profile='UnfencedDevelopmentBuild', releasePerformanceAcceptance=False)
        return verdict
    except Exception as error:
        verdict['error'] = str(error); raise
    finally: write(folder / 'verification.json', verdict)


def measurements(batch):
    rows = [loads((batch.root / 'measurements' / mode / str(rep) / 'verification.json').read_text())
            for mode in r00.MODES for rep in range(3)]
    require(all(r['result'] == 'Passed' for r in rows) and len({r['launchPid'] for r in rows}) == 12,
            'Twelve distinct source-bound measurement processes')
    summary = []
    for mode in r00.MODES:
        selected = [r for r in rows if r['mode'] == mode]
        for operation in r00.OPERATIONS:
            for phase, _, _ in r00.PHASES:
                values = [o['nanosecondsPerIteration'] for r in selected for o in r['originalContract']['operations']
                          if o['operation'] == operation and o['phase'] == phase]
                require(len(values) == 3 and all(v >= 0 for v in values), 'All fixed observations required')
                summary.append({'mode': mode, 'operation': operation, 'phase': phase, 'samples': values,
                                'min': min(values), 'median': statistics.median(values), 'max': max(values)})
    report = {'kind': 'R03UnfencedCurrentProfileObservations', 'result': 'Passed', 'processes': 12,
              'statistics': summary, 'profile': 'OriginalDevelopmentIL2CPPBuildNoR03ProbeOrLease',
              'memoryEvidence': [r['rawPath'] for r in rows], 'noiseOrOverheadThresholdClaimed': False,
              'releasePerformanceAcceptance': False, 'R02DeferredCpuRiskAcceptedHere': False,
              'H1RssRiskAcceptedHere': False, 'R03Accepted': False, 'H2Passed': False}
    write(batch.root / 'measurements.json', report)
    return {'path': str(batch.root / 'measurements.json'), 'sha256': sha(batch.root / 'measurements.json'), 'processes': 12}


def early_case(batch, case, mode, patch):
    require((case, mode, patch) in EARLY_CASES, 'Fixed early case identity')
    folder = batch.root / 'early' / case; folder.mkdir(parents=True)
    cap = capsule(batch, folder, mode, patch)
    result, log = folder / 'early.json', folder / 'Player.log'
    m07_mode = 'T07-01-Prefab-P01' if patch == 'P01' else early.DEFAULT_M07_MODE
    result_m07 = folder / ('m07-' + m07_mode + '.json')
    args = early.command_for(batch.resource_context, mode, batch.resource_manifest, batch.resource_on, cap, result, result_m07, log, m07_mode)
    expected_exit = 0 if mode in early.POSITIVE_MODES else 1
    before = inventory(batch); verdict = {'result': 'Failed', 'case': case, 'mode': mode}
    try:
        command, binding = launch(batch, args, folder, expected_exit)
        observed = early.verify_early_receipt(result, cap, mode, command['pid'], batch.resource_context['profile'])
        require(observed['diagnosticProfileComplete'], 'Complete actual early diagnostic profile required')
        early.verify_startup_logs(mode, log, Path(binding['console']))
        if mode in early.POSITIVE_MODES:
            raw = loads(result_m07.read_text()); require(raw['processId'] == command['pid'], 'M07 and early PID pairing')
            early.verify_imported_snapshots(observed, raw)
            c = batch.resource_context['context']
            m07.verify_case(result_m07, c['manifest'], c['baseline'], c['fixtures'], batch.resource_context['baselineResources'], c['on'], c['off'])
        else: require(not result_m07.exists(), 'Rejected early startup must not execute business resource handoff')
        require(inventory(batch) == before, 'Early inputs changed during process')
        verdict = dict(binding, result='Passed', case=case, mode=mode, patch=patch, launchPid=command['pid'],
                       originalExit=expected_exit, rawSha256=sha(result), capsuleSha256=sha(cap),
                       sourceInputHashes=before, profile=2, expectedRejection=expected_exit == 1, R03Accepted=False)
        return verdict
    except Exception as error:
        verdict['error'] = str(error); raise
    finally: write(folder / 'verification.json', verdict)
