"""Replay exact N compiler inputs; never reinterpret N's failed qualification as Passed."""
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
        # Exactly the loader's assembly + reference domain, not filtered Player assemblies.
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


def verify_results(root, expected):
    root = Path(root); r = loads(regular(root / 'results.json').read_text())
    require(r['kind'] == 'R03ReferenceBindingContracts' and r['basis'] == expected['basis'] and r['result'] == 'Passed' and r['failures'] == 0, 'Actual reference replay must pass')
    require(len(r['cases']) == len({v['id'] for v in r['cases']}) == 15 and all(v['result'] == 'Passed' for v in r['cases']), 'All 15 reference controls')
    require(all(r[k] is False for k in ('runtimeAcceptance','qualificationApproved','expansionAuthorized','unityEditorRun','playerRun')), 'No execution/authority promotion')
    d = loads(regular(root / 'reference-context-diagnosis.json').read_text())
    require(d['isolated']['semanticHash'] != d['closed']['semanticHash'] and d['differences'] and d['runtimeAcceptance'] is False, 'Section-level context mismatch reproduced')
    require(d['oldUncontextualizedComparison'] == 'Rejected' and d['repairedClosedComparison'] == 'Passed', 'Distinct old/new comparison')
    for w in expected['worlds']:
        for f in w['files']: require(sha(regular(f['path'])) == f['sha256'], 'Historical bytes changed by replay')
    return {'result': str(root/'results.json'), 'cases': 15, 'sha256': sha(root/'results.json'),
            'contextDifferences': d['differences'], 'basis': expected['basis'], 'runtimeAcceptance': False}


def host_contracts(batch):
    data = inputs(batch.workspace / 'hybridclr_demo', batch.root / 'reference-binding-inputs.json')
    project = HERE / 'ReferenceBindingTests/ReferenceBindingTests.csproj'
    binary, intermediate = batch.root/'bin/reference-binding', batch.root/'obj/reference-binding'
    batch.command(build_arguments(project, binary, intermediate, batch.workspace/'hybridclr_unity'))
    root = batch.root/'reference-binding'
    batch.command(['dotnet', binary/'ReferenceBindingTests.dll', '--input', batch.root/'reference-binding-inputs.json', '--output', root], timeout=600)
    return verify_results(root, data)
