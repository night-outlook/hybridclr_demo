"""Producer-shaped offline fixtures, not Player or build-acceptance evidence.

These execute verify_result without mocking any verifier. Wire names and operation
order follow M07R01Probe; numeric native states remain in raw native JSON while
Result.stateCode is the managed GetState return code.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_results as gate
import m04_results as m04
from shadow_tools import VerificationError


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixed_reflection(build):
    fixed = next(path for path in Path(build['player']['inputSnapshot']).rglob('*.dll.bytes'))
    return {'declarations': [{'id': 'm00-normal-hot-update-image', 'kind': 'FixedAssemblyBytes',
                              'imageSha256': fixed.name[:-len('.dll.bytes')],
                              'providerAssemblyIdentity': gate.ORDINARY + ', Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'}]}


def capacity(phase, sizes, allocated=0, ordinary=0, reserved=0):
    # Small fixture DLLs use kind 3. Hard-coded cursor construction is independent
    # of the verifier's reported-cursor acceptance and includes shared consumption.
    cursors = [64, 0, 0, allocated]
    accepted = next((i for i, size in enumerate(sizes) if size >= 64 * 1024 * 1024), len(sizes))
    fits = accepted == len(sizes)
    raw = dict(schemaVersion=1, enabled=True, profileVersion=1, indexBits=22, kindBits=2,
               cursors=cursors, remainingSlots=[3, 16, 64, 255 - allocated],
               finalCursors=[64, 0, 0, allocated + accepted], requiredImages=len(sizes),
               acceptedImages=accepted, firstFailingIndex=-1 if fits else accepted,
               firstFailingSize=0 if fits else sizes[accepted], failureReason='None' if fits else 'InvalidSizeOrProfileState',
               fits=fits, allocations=[dict(imageIndex=768 + allocated + i, kind=3, dllSize=size)
                                       for i, size in enumerate(sizes[:accepted])],
               ordinaryAllocatedCount=ordinary, shadowAllocatedCount=0, reservedImageCount=reserved)
    projection = {key: value for key, value in raw.items() if key not in ('schemaVersion', 'enabled', 'allocations')}
    return dict(projection, phase=phase, code='Success', rawJson=json.dumps(raw), orderedSizes=sizes, parsed=True)


def diagnostic(phase, candidates, state, expectation, used=False):
    d = {key: 0 for key in 'schemaVersion runtimeAbiVersion stateCode lastError generation expected staged retainedBytes enumerationGeneration classEnumerationGeneration'.split()}
    d.update({key: '' for key in 'state detail baselineBuildId patchId'.split()})
    d.update({key: [] for key in 'ordinaryAssemblies ordinaryClasses closureLoadOrder stableAotNames commitOrder assemblies events baselineUses'.split()})
    d.update(schemaVersion=1, runtimeAbiVersion=1, enabled=True, state=state, stateCode=m04.STATE_CODES[state],
             startupCandidateSchemaVersion=1, startupCandidateNames=candidates,
             startupObservationMode='EarlyTracking' if expectation == gate.STARTUP_EARLY_GUARD else 'ConfigureOnly',
             metadataBudgetCapabilityVersion=1, recoveryCapabilityVersion=1)
    if used:
        d['baselineUses'] = [dict(name=gate.INTERNAL, kind='AssemblyReflection', detail='Assembly::Load', type='', thread=17, timestamp=21)]
    return dict(phase=phase, code='Success', rawJson=json.dumps(d), parsed=True)


def fixture(root, mode, expectation):
    root = root.resolve()
    fixture_path = root / 'fixtures.json'; fixture_path.write_text('{}')
    receipt = root / 'player.json'; receipt.write_text('{}')
    output = root / 'Player.app'; data = output / 'Contents'; data.mkdir(parents=True,exist_ok=True)
    snapshot = root / 'Inputs'; snapshot.mkdir(exist_ok=True)
    patch_root = root / 'P03'; patch_root.mkdir(exist_ok=True)
    patch_path = patch_root / 'patch-manifest.json'; patch_path.write_text('{}')
    candidates = list(m04.CANDIDATES); closure = list(m04.PROVIDER_ORDER)
    patch_rows = []
    for index, name in enumerate(closure):
        content = bytes([index + 1]) * (512 + index * 16)
        dll = patch_root / (name + '.dll'); dll.write_bytes(content)
        patch_rows.append(dict(name=name, dll=dll.name, sha256=sha(content), dllSize=len(content), pdbSha256='', pdb=''))
    filtered_ordinary = snapshot / (gate.ORDINARY + '.dll'); filtered_ordinary.write_bytes(b'filtered-ordinary' * 64)
    fixed_bytes = b'approved-fixed-image'; fixed_hash = sha(fixed_bytes)
    fixed_ordinary = snapshot / 'ReflectionBindings' / 'Images' / (fixed_hash + '.dll.bytes')
    fixed_ordinary.parent.mkdir(parents=True, exist_ok=True); fixed_ordinary.write_bytes(fixed_bytes)
    manifest = dict(_path=str(fixture_path), unityVersion='2022.3.62f2', target='StandaloneOSX', architecture='arm64',
                    baselineBuildId='R01-test', runtimeAbiHash='a'*64, baselineManifestPath=str(root/'baseline.json'),
                    baselineManifestSha256='b'*64, candidateNames=candidates)
    player = dict(buildGuid='test-guid', inputSnapshot=str(snapshot), inputSnapshotHash='c'*64,
                  nativeLibraryPath=str(root/'native'), nativeLibrarySha256='d'*64,
                  nativeMetadataPath=str(root/'metadata'), nativeMetadataSha256='e'*64, playerOutput=str(output))
    build = dict(path=receipt, player=player, snapshot=dict(filteredAssemblies=[dict(name=gate.ORDINARY+'.dll', path=filtered_ordinary.name, sha256=sha(filtered_ordinary.read_bytes()))]))
    item = dict(fixture=dict(closureLoadOrder=closure, patchDirectory=str(patch_root), patchManifest=str(patch_path), patchManifestSha256=gate.digest(patch_path)), patch=dict(closure=patch_rows))
    context = dict(manifest=manifest, fixtures={'P03': item})
    r = {key: '' for key in gate.RESULT_STRINGS.split()}
    r.update({key: [] for key in gate.RESULT_ARRAYS.split()})
    r.update(schemaVersion=1, processId=1001, profileVersion=1, milestone='M07R-R01', mode=mode, result='Passed', il2cpp=True,
             startupExpectation=expectation, unityVersion=manifest['unityVersion'], platform='OSXPlayer', buildGuid=player['buildGuid'],
             playerDataPath=str(data), baselineBuildId=manifest['baselineBuildId'], runtimeAbiHash=manifest['runtimeAbiHash'],
             target=manifest['target'], architecture=manifest['architecture'], fixtureManifestPath=str(fixture_path),
             fixtureManifestSha256=gate.digest(fixture_path), playerBuildReceiptPath=str(receipt), playerBuildReceiptSha256=gate.digest(receipt),
             baselineManifestPath=manifest['baselineManifestPath'], baselineManifestSha256=manifest['baselineManifestSha256'],
             playerInputSnapshot=player['inputSnapshot'], playerInputSnapshotSha256=player['inputSnapshotHash'], candidateNames=candidates)
    for key in ('nativeLibraryPath','nativeLibrarySha256','nativeMetadataPath','nativeMetadataSha256'): r[key]=player[key]
    r['checks'] = [dict(name='completed', actual='Success', expected='Success', passed=True)]
    if mode == gate.OFF_MODE:
        r.update(capacityCode='FeatureDisabled', reserveCode='FeatureDisabled', recoveryCode='FeatureDisabled', stateCode='FeatureDisabled', state='Disabled')
    else:
        r.update(patchId='P03', patchManifestPath=str(patch_path), patchManifestSha256=gate.digest(patch_path), closureLoadOrder=closure,
                 configureCode='Success', beginCode='Success', reserveCode='Success', stateCode='Success', diagnosticsCode='Success')
        def byte_row(name, path, phase, transform='verified closure bytes'):
            original=path.read_bytes(); actual=original
            if transform == 'one-byte zero-padding': actual += b'\0'
            if transform == 'zero-padding-to-64MiB': actual += b'\0'*(64*1024*1024-len(actual))
            return dict(phase=phase, assemblyName=name, path=str(path), originalSha256=sha(original), actualSha256=sha(actual),
                        originalLength=len(original), actualLength=len(actual), transformation=transform)
        for i, row in enumerate(patch_rows):
            transform = ('one-byte zero-padding' if mode == 'R01-P03-Mismatch' and i == 0 else
                         'zero-padding-to-64MiB' if mode == 'R01-P03-Oversize' and i == len(closure)-1 else 'verified closure bytes')
            r['byteInputs'].append(byte_row(row['name'], patch_root/row['dll'], 'closure', transform))
        sizes = [row['originalLength'] if mode == 'R01-P03-Mismatch' else row['actualLength'] for row in r['byteInputs']]
        ordinary_count = int(mode in ('R01-P03-OrdinaryFirst', 'R01-P03-OrdinaryAfterReserve'))
        if ordinary_count:
            phase='ordinary-before-configure' if mode.endswith('OrdinaryFirst') else 'ordinary-after-reserve'
            row=byte_row(gate.ORDINARY,fixed_ordinary,phase,'verified ON snapshot fixed M00 image')
            r['byteInputs'].insert(0,row) if mode.endswith('OrdinaryFirst') else r['byteInputs'].append(row)
            r['observations'].append(dict(phase=phase,kind='ordinary-interpreter-load' if mode.endswith('OrdinaryFirst') else 'reserved-slot-isolation',detail='verified',passed=True))
        caps=[]
        if mode == 'R01-P03-OrdinaryFirst':
            caps=[capacity('before-ordinary',[]),capacity('after-ordinary-before-configure',sizes,1,1),capacity('after-reserve',sizes,6,1,5)]
        elif mode == 'R01-P03-OrdinaryAfterReserve':
            caps=[capacity('before-configure',sizes),capacity('after-reserve',sizes,5,0,5),capacity('after-ordinary-after-reserve',sizes,6,1,5)]
        elif mode in gate.PRECONFIGURE_MODES: caps=[capacity('after-preconfigure-observation',sizes)]
        elif mode == 'R01-P03-Oversize': caps=[capacity('before-configure',sizes),capacity('after-failed-reserve',sizes)]
        else:
            caps=[capacity('before-configure',sizes),capacity('after-reserve',sizes,5,0,5)]
            if mode == 'R01-P03-Mismatch': caps.append(capacity('after-mismatch',sizes,5,0,5))
        r.update(capacitySnapshots=caps,capacityCode='Success',capacityJson=caps[-1]['rawJson'])
        committed=mode in gate.COMMITTED_MODES
        r.update(state='Committed' if committed else 'Aborted', abortCode='' if committed else 'Success', commitCode='Success' if committed else '')
        state_rows=[('configured','CandidatesRegistered'),('begun','Staging')]
        if mode not in ('R01-P03-Oversize','R01-P03-Mismatch'):
            state_rows.append(('staged','Staged'))
            r['stageOrder']=closure
            r['stageResults']=[dict(name=row['assemblyName'],code='Success',dllSha256=row['actualSha256'],pdbSha256='',actualLength=row['actualLength']) for row in r['byteInputs'] if row['phase']=='closure']
            r['stageCode']='Success'
            r['validateCode']='BaselineAlreadyUsed' if mode in gate.PRECONFIGURE_MODES and expectation == gate.STARTUP_EARLY_GUARD else 'Success'
            state_rows.append(('validated' if committed else 'validated-or-early-guard','Staged' if r['validateCode']=='BaselineAlreadyUsed' else 'Validated'))
        elif mode=='R01-P03-Mismatch':
            row=r['byteInputs'][0];r['stageResults']=[dict(name=closure[0],code='MetadataBudgetMismatch',dllSha256=row['actualSha256'],pdbSha256='',actualLength=row['actualLength'])];r['stageCode']='MetadataBudgetMismatch'
        else: r['reserveCode']='MetadataCapacityExceeded'
        state_rows.append(('committed' if committed else 'aborted',r['state']))
        r['stateSnapshots']=[dict(phase=phase,state=state,code='Success',passed=True) for phase,state in state_rows]
        phases=['before-configure','configured','committed' if committed else 'aborted']
        if mode in gate.PRECONFIGURE_MODES:
            phases=['before-preconfigure-observation']
            if mode.endswith('NativePrefab'): phases+=['before-native-prefab-load','after-native-prefab-load']
            phases+=['after-preconfigure-observation','before-configure','configured','aborted']
            kind={'Type':'type','Object':'object','Cctor':'cctor','NativePrefab':'native-prefab-direct'}[mode.rsplit('-',1)[1]]
            r['observations']=[dict(phase='before-configure',kind=kind,detail='observed',passed=True),dict(phase='preconfigure-result',kind=kind,detail=r['validateCode'],passed=True)]
        elif mode.endswith('OrdinaryFirst'): phases.insert(0,'ordinary-before-configure')
        elif mode.endswith('OrdinaryAfterReserve'): phases.insert(2,'ordinary-after-reserve')
        for phase in phases:
            state='CandidatesRegistered' if phase=='configured' else 'Committed' if phase=='committed' else 'Aborted' if phase=='aborted' else 'Staging' if phase=='ordinary-after-reserve' else 'Disabled'
            used=mode in gate.PRECONFIGURE_MODES and expectation==gate.STARTUP_EARLY_GUARD and phase not in ('before-preconfigure-observation','before-native-prefab-load')
            r['diagnosticSnapshots'].append(diagnostic(phase,candidates,state,expectation,used))
        r['nativeDiagnosticsJson']=r['diagnosticSnapshots'][-1]['rawJson']
        raw=dict(schemaVersion=1,enabled=True,capabilityVersion=1,stateCode=6 if committed else 7,state=r['state'],published=committed,
                 abortAllowed=False,dispositionCode=4 if committed else 3,disposition='ActiveShadow' if committed else 'BaselineEligibleAfterAbort',
                 terminalFailureCode=0,reason='ActivePublished' if committed else 'AbortedBeforePublication',retainedBytes=100,
                 baselineEligibilityRequiresStartupValidation=not committed)
        recovery={key:value for key,value in raw.items() if key not in ('schemaVersion','enabled','capabilityVersion')}
        recovery.update(phase='committed' if committed else 'aborted',code='Success',rawJson=json.dumps(raw),parsed=True,reason='')
        r.update(recoverySnapshots=[recovery],recoveryCode='Success',recoveryJson=recovery['rawJson'])
        if committed:r['physicalWorld']=[dict(phase='committed',assemblyName=name,code='Success',mode='InterpreterShadow',passed=True) for name in candidates]
    for row in r['observations']:
        row.setdefault('path','');row.setdefault('assemblyName','')
    path=root/'result.json';r['resultPath']=str(path)
    return path,r,context,build


class R01PipelineTests(unittest.TestCase):
    def test_all_ten_producer_shaped_results_pass_complete_public_validator(self):
        for mode in gate.MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                path,r,context,build=fixture(Path(temp),mode,gate.STARTUP_OBSERVATION_GAP)
                path.write_text(json.dumps(r))
                with patch.object(gate.m07.prior, '_reflection_snapshot', return_value=fixed_reflection(build)):
                    self.assertEqual(gate.verify_result(path,mode,context,build,gate.STARTUP_OBSERVATION_GAP)['mode'],mode)

    def test_all_preconfigure_early_guards_require_full_first_use_retention(self):
        for mode in sorted(gate.PRECONFIGURE_MODES):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                path,r,context,build=fixture(Path(temp),mode,gate.STARTUP_EARLY_GUARD)
                path.write_text(json.dumps(r))
                with patch.object(gate.m07.prior, '_reflection_snapshot', return_value=fixed_reflection(build)):
                    gate.verify_result(path,mode,context,build,gate.STARTUP_EARLY_GUARD)
                row=next(row for row in r['diagnosticSnapshots'] if row['phase']=='configured')
                raw=json.loads(row['rawJson']);raw['baselineUses'][0]['timestamp']+=1;row['rawJson']=json.dumps(raw)
                path.write_text(json.dumps(r))
                with patch.object(gate.m07.prior, '_reflection_snapshot', return_value=fixed_reflection(build)), self.assertRaises(VerificationError):
                    gate.verify_result(path,mode,context,build,gate.STARTUP_EARLY_GUARD)

    def test_unknown_dto_fields_and_wrong_native_use_key_fail_closed(self):
        for mutation in ('unknown','missing','assembly-key','numeric-state','wrong-stage-hash'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temp:
                mode='R01-PreConfigure-Type';path,r,context,build=fixture(Path(temp),mode,gate.STARTUP_EARLY_GUARD)
                if mutation=='unknown':r['unknown']=1
                elif mutation=='missing':del r['capacityJson']
                elif mutation=='numeric-state':r['stateCode']=7
                elif mutation=='wrong-stage-hash':r['stageResults'][0]['dllSha256']='0'*64
                else:
                    row=r['diagnosticSnapshots'][1];raw=json.loads(row['rawJson']);raw['baselineUses'][0]['assembly']=raw['baselineUses'][0].pop('name');row['rawJson']=json.dumps(raw)
                path.write_text(json.dumps(r))
                with patch.object(gate.m07.prior, '_reflection_snapshot', return_value=fixed_reflection(build)), self.assertRaises(VerificationError):
                    gate.verify_result(path,mode,context,build,gate.STARTUP_EARLY_GUARD)
