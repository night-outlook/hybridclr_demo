"""Authenticated nominal-layout replay and source-bound sidecar verification.

Historical M inputs remain Failed runtime evidence. The replay tests new code on
those immutable bytes; fresh Unity/linked/native/Player proof is separate.
"""
from pathlib import Path
import re
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
from compiler_policy_inputs import regular

PROFILE = 'CapturedNativeLayoutIdentityV1'
HISTORY = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261004-batch-m-return-required/preflight/layout-inputs'
BASE = 'baseline-PlayerInputs'
TARGET = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261004-batch-m-return-required/batch/projects/resource-complete/_temp/AssemblyShadow/M02Validation-d795bcc36de649e9b25ac66b73f03cf1/P05-compile/Snapshot'
BASE_SHA = '7a992755d30c79c3f267123b8c1de95d48e06ab568411718a767a44cfd356f4c'
TARGET_SHA = '2a5b9c3f1076c5593c35ebf81c38309761c7d4a76b192106e38b776a2cc6a97a'
PROOF = 'ReflectionBindings/LinkedRetargeting/evidence.json'
FACADE = 'ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes'
PROOF_SHA = '241729b0125ec6bc48abc332955c71557e3f4a0b72cc0daaf3e1452005291fc7'
NETSTANDARD = 'netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51'
REPORT = 'native-layout-admission-v1.json'
CASES = ['S01-raw-scopes-remain-distinct', 'S02-complete-forwarder-positive', 'S03-two-hop-forwarder'] + [
    'S04-' + n for n in ('parent', 'interface', 'field', 'generic', 'constraint', 'modifier', 'offset')] + [
    'S05-unrelated-same-named-types','S06-missing-declared-provider','S07-missing-forward-destination','S08-cycle',
    'S09-duplicate-image','S10-duplicate-definition'] + ['S11-' + n for n in ('duplicate','definition-and-forward','not-forwarder')] + [
    'S12-input-membership','S13-disposed-owner','S14-source-clone','S15-resolution-receipts-isolated','S16-empty-inventory',
    'S17-no-ambient-resolution','S18-full-assembly-version','M01-original-scope-reproduction','M02-authenticated-layout-positive',
    'M03-inventory-order-independent','M04-wrong-facade-hash','M05-wrong-compiler-hash','M06-definition-is-not-runtime-facade','M07-changed-real-parent']


def child(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == relative, 'Strict relative snapshot path')
    return regular(Path(root) / p)


def binding(path):
    p = regular(path)
    return {'path': str(p), 'sha256': sha(p), 'size': p.stat().st_size}


def snapshot(root, linked):
    root = Path(root)
    r = loads(regular(root / 'assembly-snapshot.json').read_text())
    require(r['schemaVersion'] == 1 and r['kind'] == ('PlayerBuildInputs' if linked else 'CompilePlayerScripts'), 'Snapshot domain')
    records = r['assemblies'] + r.get('references', []) + r.get('filteredAssemblies', [])
    rows = []
    for row in records:
        require(sha(child(root, row['path'])) == row['sha256'], 'Captured compiler image changed')
        if row.get('pdbPath'): require(sha(child(root, row['pdbPath'])) == row['pdbSha256'], 'Captured symbols changed')
    selected = r['linkedPlayerReceipt']['assemblies'] if linked else r['assemblies'] + r['references']
    for row in selected:
        p = child(root, ('LinkedPlayer/' if linked else '') + row['path'])
        require(sha(p) == row['sha256'], 'Compared image changed')
        if linked and row.get('pdbPath'):
            require(sha(child(root, 'LinkedPlayer/' + row['pdbPath'])) == row['pdbSha256'], 'Linked symbols changed')
        rows.append(binding(p))
    names = [Path(row['path']).name.lower() for row in rows]
    require(len(names) == len(set(names)) and rows, 'Complete unique identity domain')
    return r, rows


def replay_inputs(demo, output):
    origin = Path(demo) / HISTORY
    before, after = origin / BASE, Path(demo) / TARGET
    require(sha(regular(before / 'assembly-snapshot.json')) == BASE_SHA and sha(regular(after / 'assembly-snapshot.json')) == TARGET_SHA,
            'One exact historical M snapshot pair')
    b, linked = snapshot(before, True); t, compiler = snapshot(after, False)
    require(len(linked) == 56 and len(compiler) == 214, 'Full M linked/compiler inventories')
    proof = loads(regular(before / PROOF).read_text())
    require(sha(before / PROOF) == PROOF_SHA == b['linkedPlayerReceipt']['reflectionBindingEvidenceHash'], 'Historical retargeting proof')
    facade = binding(before / FACADE)
    require(facade['sha256'] == proof['facadeSha256'] and proof['buildGuid'] == b['buildGuid'], 'Captured runtime facade binding')
    ref = [r for r in t['references'] if r['name'] == 'netstandard']; require(len(ref) == 1, 'One compiler reference facade')
    value = {'kind': 'R03LayoutReplayInputs', 'basis': 'ReusedAuditedLocalMLayoutInputs', 'linked': linked, 'compiler': compiler,
             'runtimeFacade': facade, 'runtimeFacadeSha256': facade['sha256'], 'compilerFacadeSha256': ref[0]['sha256'],
             'baselineName': 'assemblya.implementation.internal.dll', 'targetName': 'AssemblyA.Implementation.Internal.dll'}
    write(output, value)
    return value


def key_token(value):
    return str(len(value.encode('utf-16-le')) // 2) + ':' + value + ';'


def validate_inventory(rows, expected):
    require(isinstance(rows, list) and len(rows) == len(expected), 'Complete resolved image inventory')
    require({r['sha256'] for r in rows} == {r['sha256'] for r in expected}, 'Resolved inventory must bind exact images')
    names = [r['assemblyIdentity'] for r in rows]
    require(names == sorted(names) and len(names) == len(set(names)), 'Unambiguous sorted assembly identities')
    require(all(re.fullmatch(r'[0-9a-f]{64}', r['sha256']) and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', r['mvid']) for r in rows), 'Full image evidence')
    return {r['assemblyIdentity']: r['sha256'] for r in rows}


def validate_resolutions(rows, own, runtime, facade):
    require(isinstance(rows, list), 'Resolution observations required')
    seen = set(); mapped = 0
    for r in rows:
        declaration, origin, destination = r['declaration'], r['declaredAssemblyIdentity'], r['definitionAssemblyIdentity']
        require(type(r['runtimeFacadeUsed']) is bool, 'Boolean facade claim required')
        pair = (origin, declaration); require(pair not in seen, 'Duplicate resolution'); seen.add(pair)
        require(own.get(origin) == r['declaredModuleSha256'], 'Declared provider is outside inventory')
        require(r['canonicalKey'] == key_token(destination) + key_token(declaration), 'Canonical identity must keep assembly and declaration')
        path = r['forwardingPath']; require(isinstance(path, list) and path and len(path) <= 258, 'Bounded nonempty forwarding path')
        require(path[0] == origin + ' | sha256=' + r['declaredModuleSha256'] and path[-1] == destination + ' | sha256=' + r['definitionModuleSha256'], 'Path endpoints')
        require(len(path) == len(set(path)), 'No repeated forwarding path segment')
        mapped += int(r['runtimeFacadeUsed'] is True)
        at_runtime = False
        for segment in path:
            if segment == NETSTANDARD + ' | runtime-facade=' + facade:
                require(r['runtimeFacadeUsed'] is True and not at_runtime, 'One captured runtime-facade transition')
                at_runtime = True
            else:
                pieces = segment.rsplit(' | sha256=', 1)
                require(len(pieces) == 2 and (runtime if at_runtime else own).get(pieces[0]) == pieces[1], 'Forwarding step not authenticated')
        require(at_runtime == r['runtimeFacadeUsed'], 'Facade claim/path mismatch')
    return mapped


def verify_comparison(value, inputs):
    require(value['basis'] == 'ReusedAuditedLocalMLayoutInputs' and value['nativeProofExecuted'] is False and value['runtimeAcceptance'] is False, 'Replay is not new runtime proof')
    old, new = value['declared'], value['resolved']
    require(old['editorAccepted'] is False and sum('ParentChanged' in r['reasons'] for r in old['types']) == 43, 'Preserved scope reproduction')
    require(new['schemaVersion'] == 2 and new['editorAccepted'] is True and new['nativeProofExecuted'] is False and
            new['allocationProofStillRequired'] is True and new['pureInterpreterExpansionEnabled'] is False, 'Nominal admission only')
    for field, rows, name in [('baselineDllSha256', inputs['linked'], inputs['baselineName']), ('targetDllSha256', inputs['compiler'], inputs['targetName'])]:
        require(new[field] == old[field] == next(r['sha256'] for r in rows if Path(r['path']).name == name), 'Actual compared inputs')
    linked = validate_inventory(value['linkedInventory'], inputs['linked']); compiler = validate_inventory(value['compilerInventory'], inputs['compiler'])
    validate_resolutions(value['linkedResolutions'], linked, {}, '')
    require(validate_resolutions(value['compilerResolutions'], compiler, linked, inputs['runtimeFacadeSha256']) > 0, 'Actual framework mapping coverage')


def verify_results(root, inputs):
    root = Path(root); r = loads(regular(root / 'results.json').read_text())
    require(r['kind'] == 'R03LayoutIdentityContracts' and r['schemaVersion'] == 1 and r['result'] == 'Passed' and r['failures'] == 0, 'All identity cases must pass')
    require([c['id'] for c in r['cases']] == CASES and all(c['result'] == 'Passed' for c in r['cases']), 'Exact complete identity test set')
    require(all(r[k] is False for k in ('unityEditorRun', 'playerRun', 'runtimeAcceptance', 'nativeProofExecuted', 'expansionAuthorized')), 'Host cannot authorize runtime')
    for f in r['files']:
        p = child(root, f['path']); require(sha(p) == f['sha256'] and p.stat().st_size == f['size'], 'Synthetic fixture hash')
    verify_comparison(loads((root / 'comparison.json').read_text()), inputs)
    for f in inputs['linked'] + inputs['compiler'] + [inputs['runtimeFacade']]:
        require(binding(f['path']) == f, 'Replay changed preserved inputs')
    return {'path': str(root / 'results.json'), 'sha256': sha(root / 'results.json'), 'cases': len(CASES),
            'basis': inputs['basis'], 'runtimeAcceptance': False, 'nativeProofExecuted': False}


def host_contracts(batch):
    inputs = replay_inputs(batch.workspace / 'hybridclr_demo', batch.root / 'layout-identity-inputs.json')
    binary, obj = batch.root / 'bin/layout-identity', batch.root / 'obj/layout-identity'
    batch.command(build_arguments(HERE / 'LayoutIdentityTests/LayoutIdentityTests.csproj', binary, obj, batch.workspace / 'hybridclr_unity'))
    batch.command(['dotnet', binary / 'LayoutIdentityTests.dll', '--output', batch.root / 'layout-identity', '--input', batch.root / 'layout-identity-inputs.json'])
    return verify_results(batch.root / 'layout-identity', inputs)
