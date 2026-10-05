"""Replay exact N compiler inputs without reclassifying N's failed qualification."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
from compiler_policy_inputs import regular

CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261005-batch-n-return-required'
DIAGNOSIS_SHA = '7438cb1f7335554b72ae3ece069db3d1746aa7672fa7115225371222b88a604d'
UNITY_BASE = '/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/'
KINDS = ['baseline','P01','P02','P03','P04','P05']
CASE_IDS = tuple('N-' + name + '-unchanged-closed-domain' for name in KINDS) + (
    'N-reference-context-diagnosis', 'N-reference-type-mutation', 'N-reference-method-mutation',
    'N-reference-attribute-mutation', 'N-primary-and-descriptor-mutation',
    'N-reference-assembly-identity-mutation', 'N-disposed-domain',
    'N-reference-disk-mutation', 'N-reference-disappeared')
FLAGS = ('runtimeAcceptance','qualificationApproved','expansionAuthorized','unityEditorRun','playerRun')


def inputs(demo, output):
    history = Path(demo) / CHECKPOINT
    path = regular(history / 'preflight/QUALIFICATION_INPUT_DIAGNOSIS.json')
    require(sha(path) == DIAGNOSIS_SHA, 'One exact immutable N diagnosis')
    diagnosis = loads(path.read_text()); rows = diagnosis['referenceInputs']
    require([r['world'] for r in rows] == KINDS, 'Exact six N worlds')
    worlds = []
    for row in rows:
        suffix = row['snapshotReceipt'].split('/projects/resource-complete/', 1)[1]
        require('..' not in Path(suffix).parts and not Path(suffix).is_absolute(), 'Captured snapshot suffix')
        receipt_path = regular(history / 'batch/projects/resource-complete' / suffix)
        require(sha(receipt_path) == row['snapshotReceiptSha256'], 'Exact captured receipt hash')
        receipt = loads(receipt_path.read_text()); root = receipt_path.parent; files = []
        for field in ('assemblies', 'references'):
            for f in receipt[field]:
                rel = Path(f['path'])
                require(not rel.is_absolute() and '..' not in rel.parts, 'Captured DLL relative path')
                p = regular(root / rel)
                require(sha(p) == f['sha256'], 'Captured qualification input changed')
                files.append({'name': f['name'], 'path': str(p), 'sha256': sha(p), 'size': p.stat().st_size,
                              'referenceOnly': field == 'references',
                              'framework': field == 'references' and f['sourcePath'].startswith(UNITY_BASE + 'NetStandard/'),
                              'originalSourcePath': f['sourcePath']})
        names = [f['name'].lower() for f in files]
        require(len(names) == len(set(names)) and len(files) > 100, 'Complete unique qualification domain')
        animation = next(f for f in files if f['name'].lower() == 'unityengine.animationmodule')
        require(animation['sha256'] == row['sha256'] == '7f329fc53ba65594d97bea0b60feb9a061ad2b6310c20f948db0461321aeda2d', 'Exact observed reference bytes')
        worlds.append({'name': row['world'], 'root': str(root), 'receiptSha256': sha(receipt_path), 'files': files})
    result = {'kind': 'R03NReferenceInputs', 'basis': 'ReusedAuditedLocalNCompilerInputs', 'worlds': worlds,
              'diagnosticResolverPolicy': 'CapturedNetStandardReferencesOnlyNotLiveUnityAuthority',
              'historicalQualification': 'Failed', 'runtimeAcceptance': False}
    write(output, result)
    return result


def case_arguments(input_path, output, case):
    require(case in CASE_IDS, 'One exact reference case')
    return ['--input', input_path, '--output', output, '--case', case]


def run_cases(root, expected, run_one):
    """Fifteen fixed fresh invocations, each with its own unchanged 600s bound.

    The caller owns process supervision. Missing/failed cases stay failed; no
    retry or partial aggregate can pass. This is host diagnostic granularity,
    not a change to any Unity/Player deadline or runtime acceptance condition.
    """
    root = Path(root); require(not root.exists(), 'Unused reference case collection')
    (root / 'cases').mkdir(parents=True)
    result = {'schemaVersion': 1, 'kind': 'R03ReferenceBindingContracts', 'basis': expected['basis'],
              'result': 'Failed', 'failures': 0, 'cases': [], 'caseReceipts': [],
              'executionPolicy': 'FifteenFreshSupervisedCasesV1', 'perCaseTimeoutSeconds': 600,
              **{key: False for key in FLAGS}}
    for case in CASE_IDS:
        folder = root / 'cases' / case
        try:
            run_one(case, folder)
            path = regular(folder / 'results.json'); row = loads(path.read_text())
            require(row['kind'] == result['kind'] and row['basis'] == expected['basis'] and row['selection'] == case,
                    'Exact managed case source/selection')
            require(all(row[key] is False for key in FLAGS), 'No case authority promotion')
            require(row['result'] == 'Passed' and row['failures'] == 0 and len(row['cases']) == 1 and
                    row['cases'][0]['id'] == case and row['cases'][0]['result'] == 'Passed', 'One complete passing case')
            require(loads(regular(folder / 'case-result.json').read_text()) == row['cases'][0], 'Progress and final case agree')
            result['cases'].append(row['cases'][0])
            result['caseReceipts'].append({'id': case, 'path': str(path.relative_to(root)), 'sha256': sha(path)})
        except Exception as error:
            result['failures'] += 1
            result['cases'].append({'id': case, 'result': 'Failed', 'error': type(error).__name__ + ': ' + str(error)})
            result['caseReceipts'].append({'id': case, 'status': 'FailedOrUnavailable'})
    diagnosis = root / 'cases/N-reference-context-diagnosis/reference-context-diagnosis.json'
    if diagnosis.is_file():
        with (root / 'reference-context-diagnosis.json').open('xb') as target:
            target.write(regular(diagnosis).read_bytes())
    if result['failures'] == 0:
        result['result'] = 'Passed'
    write(root / 'results.json', result)
    require(result['result'] == 'Passed', 'All fifteen reference cases are mandatory; preserve failed collection')
    return result


def verify_results(root, expected):
    root = Path(root); r = loads(regular(root / 'results.json').read_text())
    require(r['kind'] == 'R03ReferenceBindingContracts' and r['basis'] == expected['basis'] and r['result'] == 'Passed' and r['failures'] == 0, 'Actual reference replay must pass')
    require(tuple(v['id'] for v in r['cases']) == CASE_IDS and all(v['result'] == 'Passed' for v in r['cases']), 'All 15 reference controls')
    require(r['executionPolicy'] == 'FifteenFreshSupervisedCasesV1' and r['perCaseTimeoutSeconds'] == 600,
            'Fixed per-case supervision profile')
    require(tuple(v['id'] for v in r['caseReceipts']) == CASE_IDS, 'Exact receipt collection')
    for case, row in zip(CASE_IDS, r['caseReceipts']):
        require(row['path'] == 'cases/' + case + '/results.json' and sha(regular(root / row['path'])) == row['sha256'], 'Source case receipt changed')
    require(all(r[k] is False for k in FLAGS), 'No execution/authority promotion')
    d = loads(regular(root / 'reference-context-diagnosis.json').read_text())
    require(d['isolated']['semanticHash'] != d['closed']['semanticHash'] and d['differences'] and d['runtimeAcceptance'] is False, 'Section-level context mismatch reproduced')
    require(d['oldUncontextualizedComparison'] == 'Rejected' and d['repairedClosedComparison'] == 'Passed', 'Distinct old/new comparison')
    for w in expected['worlds']:
        for f in w['files']: require(sha(regular(f['path'])) == f['sha256'], 'Historical bytes changed by replay')
    return {'result': str(root/'results.json'), 'cases': 15, 'sha256': sha(root/'results.json'),
            'contextDifferences': d['differences'], 'basis': expected['basis'], 'runtimeAcceptance': False}


def host_contracts(batch):
    input_path = batch.root / 'reference-binding-inputs.json'
    data = inputs(batch.workspace / 'hybridclr_demo', input_path)
    project = HERE / 'ReferenceBindingTests/ReferenceBindingTests.csproj'
    binary, intermediate = batch.root/'bin/reference-binding', batch.root/'obj/reference-binding'
    batch.command(build_arguments(project, binary, intermediate, batch.workspace/'hybridclr_unity'))
    root = batch.root/'reference-binding'
    run_cases(root, data, lambda case, output: batch.command(
        ['dotnet', binary/'ReferenceBindingTests.dll', *case_arguments(input_path, output, case)], timeout=600))
    return verify_results(root, data)
