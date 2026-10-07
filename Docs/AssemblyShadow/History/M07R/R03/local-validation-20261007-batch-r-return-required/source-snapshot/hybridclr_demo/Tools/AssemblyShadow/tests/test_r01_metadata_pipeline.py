"""Metadata transport regression from Unity JsonUtility and actual public helpers.

The checked-in JSON is the 2026-09-07 production DTO export, a serialization
sample only. Public verify_patch tests use synthetic PE files and replace only
upstream compiler-snapshot admission; PE/hash/closure/report checks stay real.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch as mock_patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m07_results as gate
import m06_results as m06
from shadow_tools import VerificationError
from test_m04_results import make_pe

SAMPLE = Path(__file__).parent / 'data/r01-metadata-serialization.json'


def metadata(rows, cursors=None):
    sample=json.loads(SAMPLE.read_text())
    profile=sample['profile'];report=sample['capacity']
    before=list(cursors or [64,0,0,0]);current=list(before)
    report.update(inputs=[],allocations=[],cursorsBefore=before,requiredImages=len(rows),acceptedImages=len(rows),
                  ordinaryAssemblyCount=0,aotCandidateAssemblyCount=5)
    for row in rows:
        source=dict(name=row['name'],bytes=row['dllSize'],dllSize=row['dllSize'],sha256=row['sha256'])
        report['inputs'].append(source)
        report['allocations'].append(dict(source,imageIndex=768+current[3],kind=3,cursorBefore=current[3],cursorAfter=current[3]+1,slot=current[3]))
        current[3]+=1
    report.update(cursorsAfter=current,remainingSlotsBefore=[3,16,64,255-before[3]],remainingSlotsAfter=[3,16,64,255-current[3]],availableImages=338-before[3])
    return dict(nativeBudgetCapabilityVersion=1,metadataEncodingProfile=profile,metadataCapacityReport=report)


def patch_fixture(root, negotiated):
    root=root.resolve();compiled_root=root/'compile';compiled_root.mkdir();patch_root=root/'patch';patch_root.mkdir()
    manifest_path=root/'fixtures.json';manifest_path.write_text('{}')
    pin=json.loads(SAMPLE.read_text())['profile']['nativeSourceRevision']
    pins=dict(schemaVersion=1,unityVersion='2022.3.62f2',target='StandaloneOSX',architecture='arm64')
    for repo in ('hybridclr','hybridclrUnity','il2cppPlus','demo'):
        pins[repo]=dict(url='https://example.invalid/'+repo,revision=pin,localPath=str(root/repo))
    order=gate.fixture_order('P03');rows=[];compiled=[];identities=[]
    for name in order:
        dll=patch_root/(name+'.dll');dll.write_bytes(make_pe(name))
        identity=gate.prior.read_identity(dll);identities.append(identity)
        pdb=patch_root/(name+'.pdb');pdb.write_bytes(b'portable-symbol-fixture')
        (compiled_root/pdb.name).write_bytes(pdb.read_bytes())
        rows.append(dict(name=name,dll=dll.name,sha256=gate.digest(dll),semanticHash='f'*64,mvid=identity['mvid'],baselineMvid=identity['mvid'],pdb=pdb.name,pdbSha256=gate.digest(pdb),references=[]))
        compiled.append(dict(name=name,sha256=gate.digest(dll),pdbPath=pdb.name))
    baseline=dict(sourcePins=pins,resourceAbiHash='sha256:'+'1'*64,assemblies=[dict(name=row['name'],mvid=row['mvid']) for row in rows])
    manifest=dict(baselineBuildId='M07-Baseline-Synthetic',runtimeAbiHash=gate.prior._runtime_abi_hash(pins,manifest_path),unityVersion=pins['unityVersion'],target=pins['target'],architecture=pins['architecture'],baselineManifestSha256='2'*64)
    patch={field:None for field in gate.PATCH_FIELDS.split()}
    patch.update(manifest,sourcePins=pins,schemaVersion=1,semanticHashSchema=1,patchId='P03',compileSnapshotHash='3'*64,
                 unsigned=True,signatureAlgorithm='None',dllOnly=True,changedRoots=gate.fixture_policy('P03')[1],loadOrder=order,
                 baselineResourceAbiHash=baseline['resourceAbiHash'],resourceAbiHash=baseline['resourceAbiHash'],resourceChangeLevel='CodeOnly',resourceBundlesRequired=[],resourceChangeReasons=[],closure=rows,
                 dependencyGraph=[dict(consumer=name,provider=gate.CONTRACTS,kind='TypeReference',evidence='synthetic') for name in order if name not in (gate.CONTRACTS,gate.INTERNAL)],
                 reflectionBindingConfigurationSha256='',reflectionBindingConfigurationHash='',reflectionBindings=[])
    if negotiated:
        for row in rows:row['dllSize']=(patch_root/row['dll']).stat().st_size
        patch.update(metadata(rows));baseline.update(metadata([]))
    patch_path=patch_root/'patch-manifest.json'
    defines,roots,dll_only=gate.fixture_policy('P03')
    fixture=dict(patchId='P03',defines=defines,changedRoots=roots,dllOnly=dll_only,closureLoadOrder=order,
                 compileSnapshot=str(compiled_root),compileSnapshotHash='3'*64,patchDirectory=str(patch_root),patchManifest=str(patch_path),
                 baselineResourceAbiHash=baseline['resourceAbiHash'],resourceAbiHash=baseline['resourceAbiHash'],resourceChangeLevel='CodeOnly',resourceBundlesRequired=[],assemblyIdentities=identities)
    snapshot=dict(snapshotHash='3'*64,assemblies=compiled)
    def write():
        patch_path.write_text(json.dumps(patch));fixture['patchManifestSha256']=gate.digest(patch_path)
        (patch_root/'manifest.sha256').write_text(gate.digest(patch_path))
    write()
    return fixture,manifest,baseline,manifest_path,patch,compiled_root,snapshot,write


class R01MetadataPipelineTests(unittest.TestCase):
    def test_actual_jsonutility_sample_through_complete_helper_with_path_label(self):
        sample=json.loads(SAMPLE.read_text())
        self.assertEqual(sample['capacity']['firstFailingAssembly'],'')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();rows=[]
            # This helper consumes caller-verified hashes; full verify_patch below
            # independently exercises the preceding physical hash/PE boundary.
            for source in sample['capacity']['inputs']:
                dll=root/(source['name']+'.dll');dll.write_bytes(bytes(source['dllSize']))
                rows.append(dict(name=source['name'],dll=dll.name,dllSize=source['dllSize'],sha256=source['sha256']))
            patch=dict(nativeBudgetCapabilityVersion=1,metadataEncodingProfile=sample['profile'],metadataCapacityReport=sample['capacity'])
            gate._verify_r01_patch_metadata(patch,rows,root,[r['name'] for r in rows],root/'patch-manifest.json')
            for key,value in [('firstFailingAssembly',None),('cursorsAfter',[64,0,0,6]),('remainingSlotsAfter',[3,16,64,249]),('availableImages',339)]:
                bad=copy.deepcopy(patch);bad['metadataCapacityReport'][key]=value
                with self.subTest(key=key),self.assertRaises(VerificationError):gate._verify_r01_patch_metadata(bad,rows,root,[r['name'] for r in rows],root/'patch-manifest.json')
            bad=copy.deepcopy(patch);bad['metadataCapacityReport']['allocations'][1]['slot']=0
            with self.assertRaises(VerificationError):gate._verify_r01_patch_metadata(bad,rows,root,[r['name'] for r in rows],root/'patch-manifest.json')

    def test_public_verify_patch_accepts_legacy_and_r01_and_rejects_tampered_report(self):
        for negotiated in (False,True):
            with self.subTest(negotiated=negotiated),tempfile.TemporaryDirectory() as temp:
                fixture,manifest,baseline,path,patch,compiled_root,snapshot,write=patch_fixture(Path(temp),negotiated)
                with mock_patch.object(gate,'verify_compile_snapshot',return_value=(compiled_root,snapshot)),mock_patch.object(gate.prior,'_reflection_snapshot',return_value=None):
                    result=gate.verify_patch(fixture,manifest,baseline,path)
                    self.assertEqual(result['r01Capability'],negotiated)
                    if negotiated:
                        patch['metadataCapacityReport']['allocations'][0]['imageIndex']+=1;write()
                        with self.assertRaises(VerificationError):gate.verify_patch(fixture,manifest,baseline,path)

    def test_complete_budget_chain_rejects_legacy_r01_mix_and_changed_baseline_cursors(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture,manifest,baseline,path,patch,compiled_root,snapshot,write=patch_fixture(Path(temp),True)
            for change in ('legacy','cursor','revision','profile'):
                bad=copy.deepcopy(baseline)
                if change=='legacy':bad.pop('nativeBudgetCapabilityVersion')
                elif change=='cursor':bad['metadataCapacityReport']['cursorsAfter'][3]+=1
                elif change=='revision':bad['sourcePins']['hybridclr']['revision']='0'*40
                else:bad['metadataEncodingProfile']['indexMasks'][0]-=1
                with self.subTest(change=change),self.assertRaises(VerificationError):gate.verify_budget_binding(patch,bad,path)

class LegacyResultPipelineTests(unittest.TestCase):
    def test_m06_full_header_legacy_and_negotiated_wire_shapes(self):
        from test_m06_results import M06ResultTests
        for negotiated in (False,True):
            with self.subTest(negotiated=negotiated),tempfile.TemporaryDirectory() as temp:
                path,result,context,build=M06ResultTests().header_fixture(Path(temp))
                if negotiated:
                    result['reserveCode']=0
                    build['proof']=dict(apiSignatures=['HybridCLR.AssemblyShadowErrorCode HybridCLR.AssemblyShadowRuntime::'+n for n in m06.LEGACY_API_NAMES+m06.NEGOTIATED_API_NAMES])
                path.write_text(json.dumps(result));m06.verify_result_header(path,context,build)
                bad=copy.deepcopy(result)
                if negotiated:del bad['reserveCode']
                else:bad['reserveCode']=0
                path.write_text(json.dumps(bad))
                with self.assertRaises(VerificationError):m06.verify_result_header(path,context,build)

    def test_m06_native_reservation_event_is_versioned_without_rewriting_legacy(self):
        closure=[gate.INTERNAL]
        legacy=m06.transaction_events('staged',closure)
        current=m06.transaction_events('staged',closure,True)
        self.assertEqual([r['kind'] for r in legacy],['candidates-registered','transaction-begun','skeleton-created'])
        self.assertEqual([r['kind'] for r in current],['candidates-registered','transaction-begun','metadata-budget-reserved','skeleton-created'])
        self.assertEqual(current[2],dict(sequence=3,kind='metadata-budget-reserved',name='',generation=0,stagedCount=0))
        self.assertEqual(m06.transaction_events('initial',closure,True),[])

    def test_m07_complete_headers_bind_legacy_r01_and_off_result_shapes(self):
        for negotiated,off in ((False,False),(True,False),(True,True)):
            with self.subTest(negotiated=negotiated,off=off),tempfile.TemporaryDirectory() as temp:
                root=Path(temp).resolve();mode='T07-14-FeatureOff' if off else 'T07-03-FullClosure-P03'
                manifest_path=root/'fixtures.json';manifest_path.write_text('{}');receipt=root/'player.json';receipt.write_text('{}')
                output=root/'Player.app';data=output/'Contents';data.mkdir(parents=True)
                result={key:'' for key in gate.RESULT_FIELDS.split()}
                for key in ('stageOrder','checks','stageResults','snapshots','bundles','assets','scenes','typeResolutions','cacheEvents','assemblyModes'):result[key]=[]
                for key in ('graphSum','p04RuntimeValue','p05SerializedValue','baselineUseCount','nativeEventCount','transactionGeneration'):result[key]=0
                for key in ('resourcePrecheckPassed','commitCompletedBeforeResourceLoad','businessResourceLoadStarted'):result[key]=False
                player=dict(baselineBuildId='M07-Baseline-Synthetic',runtimeAbiHash='a'*64,unityVersion='2022.3.62f2',buildGuid='guid')
                manifest=dict(_path=str(manifest_path),baselineManifestPath=str(root/'baseline.json'),baselineManifestSha256='b'*64)
                baseline=dict(resourceAbiHash='sha256:'+'c'*64)
                result.update(player,schemaVersion=1,processId=10,milestone='M07',mode=mode,result='Passed',il2cpp=True,platform='OSXPlayer',playerDataPath=str(data),
                              fixtureManifestPath=str(manifest_path),fixtureManifestSha256=gate.digest(manifest_path),playerBuildReceiptPath=str(receipt),playerBuildReceiptSha256=gate.digest(receipt),
                              baselineManifestPath=manifest['baselineManifestPath'],baselineManifestSha256=manifest['baselineManifestSha256'],baselineResourceAbiHash=baseline['resourceAbiHash'])
                if negotiated:baseline['nativeBudgetCapabilityVersion']=1;result['reserveMetadataBudget']='' if off else 'Success'
                build=dict(player=player,path=receipt,output=output);path=root/('m07-'+mode+'.json');path.write_text(json.dumps(result))
                gate.verify_result_header(path,manifest,baseline,build)
                bad=copy.deepcopy(result)
                if negotiated:del bad['reserveMetadataBudget']
                else:bad['reserveMetadataBudget']='Success'
                path.write_text(json.dumps(bad))
                with self.assertRaises(VerificationError):gate.verify_result_header(path,manifest,baseline,build)

    def test_m07_complete_transaction_requires_negotiated_reservation_check_and_outcome(self):
        from test_r01_pipeline import diagnostic
        import r01_results as r01
        for negotiated in (False,True):
            with self.subTest(negotiated=negotiated),tempfile.TemporaryDirectory() as temp:
                fixture,manifest,baseline,manifest_path,patch,compiled_root,snapshot,write=patch_fixture(Path(temp),negotiated)
                path=manifest_path.parent/'m07-T07-03-FullClosure-P03.json';order=fixture['closureLoadOrder'];manifest['stableAotNames']=['mscorlib']
                resource_checks=['resource-load-not-started-at-entry','prefab-serialized-state','serialize-reference-graph','nested-cross-reference','monoscript-evidence-policy','monoscript-logical-identity','monoscript-active-after-unload-true','scriptable-object-state','dont-destroy-survives-scene-switch','p04-runtime-storage','p05-serialized-storage']
                checks=['configure','begin']+(['reserve-metadata-budget'] if negotiated else [])+['stage-'+name for name in order]+['validate','commit']+['assembly-mode-'+name for name in gate.CANDIDATES]+resource_checks
                result=dict(mode='T07-03-FullClosure-P03',checks=[dict(name=name,actual='Success',expected='Success',passed=True) for name in checks],
                            configureCode='Success',beginCode='Success',validateCode='Success',commitCode='Success',stateCode='Success',state='Committed',
                            stageProbeCode='',abortCode='',executionModeCode='',diagnosticsCode='',typeResolutionCode='',executionDiagnosticsCode='',stageOrder=order,
                            stageResults=[dict(name=row['name'],code='Success',dllSha256=row['sha256'],pdbSha256=row['pdbSha256']) for row in patch['closure']],snapshots=[],baselineUseCount=0)
                if negotiated:result['reserveMetadataBudget']='Success'
                for i,phase in enumerate(('staged','validated-resource-precheck-complete','committed-before-resources','final-resource')):
                    state='Staged' if i==0 else 'Validated' if i==1 else 'Committed';published=i>=2
                    d=json.loads(diagnostic(phase,list(gate.CANDIDATES),state,r01.STARTUP_OBSERVATION_GAP)['rawJson'])
                    if not negotiated:
                        for key in set(gate.prior.R01_DIAGNOSTIC_FIELDS.split())-set(gate.prior.DIAGNOSTIC_FIELDS.split()):del d[key]
                    d.update(baselineBuildId=manifest['baselineBuildId'],patchId='P03',generation=int(published),enumerationGeneration=int(published),classEnumerationGeneration=int(published),
                             expected=len(order),staged=len(order),retainedBytes=100,closureLoadOrder=order,stableAotNames=['mscorlib'],commitOrder=order if published else [],
                             assemblies=[dict(name=row['name'],mvid=row['mvid'],skeletonBuilt=True,runtimeMetadataInitialized=i>0,published=published,moduleInitializerAttempted=published,moduleInitializerRan=published) for row in patch['closure']],
                             ordinaryAssemblies=[dict(name=name,isInterpreter=False) for name in gate.CANDIDATES]+([dict(name=name,isInterpreter=True) for name in order] if published else []),
                             events=m06.transaction_events('staged' if i==0 else 'validated' if i==1 else 'committed',order,negotiated))
                    result['snapshots'].append(dict(phase=phase,diagnostics=d))
                raw_path=path.with_name(path.stem+'-diagnostics.json');raw_path.write_text(json.dumps(d))
                result.update(nativeDiagnosticsJson=raw_path.read_text(),rawDiagnosticsPath=str(raw_path),rawDiagnosticsSha256=gate.digest(raw_path),nativeEventCount=len(d['events']),transactionGeneration=1)
                item=dict(fixture=fixture,patch=patch,r01Capability=negotiated)
                gate.verify_transaction(result,path,manifest,item)
                if negotiated:
                    bad=copy.deepcopy(result);bad['reserveMetadataBudget']='MetadataCapacityExceeded'
                    with self.assertRaises(VerificationError):gate.verify_transaction(bad,path,manifest,item)
                    bad=copy.deepcopy(result);bad['checks']=[row for row in bad['checks'] if row['name']!='reserve-metadata-budget']
                    with self.assertRaises(VerificationError):gate.verify_transaction(bad,path,manifest,item)
