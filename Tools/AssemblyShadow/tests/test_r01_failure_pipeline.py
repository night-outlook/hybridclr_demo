"""Wire-contract tests: real launcher and public verifier, synthetic Player process.

Only upstream current-install admission and subprocess execution are replaced in
pipeline tests. Files, hashes, raw native schema/arithmetic, ordering, process
bindings and strict result/launch verification remain real. This is not Player
execution evidence. Initializer tests separately exercise the full patch helper.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_failure_results as gate
import r01_results as r01
import m04_results as m04
from shadow_tools import VerificationError
from test_m04_results import diagnostic
from test_r01_metadata_pipeline import patch_fixture


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return path


def load_launcher():
    path = Path(gate.__file__).with_name('run-r01-failure-players.py')
    spec = importlib.util.spec_from_file_location('r01_failure_launcher_test', path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def prepared(root):
    root = root.resolve(); (root/'_temp/AssemblyShadow').mkdir(parents=True)
    paths = {key:write(root/(key+'.json'), {}) for key in ('fixtureManifestPath','onBuildReceiptPath','offBuildReceiptPath','replayReceiptPath','failureFixturesPath','negativeInputPath')}
    paths['projectRoot'] = root
    app=root/'Player.app';(app/'Contents').mkdir(parents=True);exe=app/'player';exe.write_text('synthetic-process-adapter')
    order=list(gate.m07.fixture_order('P03'))
    fixtures={}
    for patchid in ('P03',gate.INITIALIZER_ID):
        directory=root/patchid;directory.mkdir();rows=[]
        for index,name in enumerate(order):
            dll=directory/(name+'.dll');dll.write_bytes(bytes([index+1])*(100+index))
            rows.append(dict(name=name,mvid=f'00000000-0000-0000-0000-{index+1:012d}',dll=dll.name,sha256=gate.digest(dll),dllSize=dll.stat().st_size,pdbSha256='',pdb=''))
        p=dict(patchId=patchid,loadOrder=order,closure=rows);path=write(directory/'patch-manifest.json',p)
        fixtures[patchid]=dict(root=directory,path=path,patch=p)
    negative=root/'negative.dll';negative.write_bytes(b'negative-sidecar'.ljust(100,b'x'))
    manifest=dict(unityVersion='2022.3.62f2',baselineBuildId='failure-test',runtimeAbiHash='1'*64,
                  baselineManifestPath=str(write(root/'baseline.json',{})),baselineManifestSha256=gate.digest(root/'baseline.json'))
    player=dict(buildGuid='a'*32,nativeLibrarySha256='2'*64,nativeMetadataSha256='3'*64,inputSnapshotHash='4'*64)
    context=dict(manifest=manifest,on=dict(path=paths['onBuildReceiptPath'],output=app,player=player),fixtures=fixtures,sourcePins={'fixture':'explicit-synthetic'})
    failures=dict(path=paths['failureFixturesPath'],initializer=fixtures[gate.INITIALIZER_ID],data=dict(fixtureManifestPath=str(paths['fixtureManifestPath']),fixtureManifestSha256=gate.digest(paths['fixtureManifestPath'])))
    return dict(context=context,failures=failures,negative=dict(path=paths['negativeInputPath'],data=dict(outputPath=str(negative))),
                runner=types.SimpleNamespace(executable_for=lambda output:exe),inventory={p for p in root.rglob('*') if p.is_file()}),paths


def produce(path,mode,p,process_id):
    c=p['context'];b=c['on'];m=c['manifest'];f=p['failures'];n=p['negative'];patch=c['fixtures'][gate.INITIALIZER_ID if mode==gate.MODES[2] else 'P03']
    order=patch['patch']['loadOrder'];q04=mode==gate.MODES[1];init=mode==gate.MODES[2];terminal=13 if q04 else 19 if init else 0
    final='Failed' if q04 else 'FailedAfterCommit' if init else 'Committed'
    result={key:'' for key in gate.RESULT_FIELDS.split()}
    result.update(schemaVersion=1,kind='R01FailureResult',mode=mode,result='Passed',error='',resultPath=str(path),processId=process_id,mainThreadId=1,
        unityVersion=m['unityVersion'],platform='OSXPlayer',buildGuid=b['player']['buildGuid'],playerDataPath=str(b['output']/'Contents'),baselineBuildId=m['baselineBuildId'],runtimeAbiHash=m['runtimeAbiHash'],
        fixtureManifestPath=f['data']['fixtureManifestPath'],fixtureManifestSha256=f['data']['fixtureManifestSha256'],playerBuildReceiptPath=str(b['path']),playerBuildReceiptSha256=gate.digest(b['path']),
        baselineManifestPath=m['baselineManifestPath'],baselineManifestSha256=m['baselineManifestSha256'],failureFixturesPath=str(f['path']),failureFixturesSha256=gate.digest(f['path']),
        negativeInputPath=str(n['path']),negativeInputSha256=gate.digest(n['path']),patchId=patch['patch']['patchId'],patchManifestPath=str(patch['path']),patchManifestSha256=gate.digest(patch['path']),
        nativeLibrarySha256=b['player']['nativeLibrarySha256'],nativeMetadataSha256=b['player']['nativeMetadataSha256'],inputSnapshotHash=b['player']['inputSnapshotHash'],
        il2cpp=True,observerJoined=True,closureLoadOrder=order,observerErrors=[],byteInputs=[],operations=[],diagnostics=[],capacities=[],recovery=[],observerSamples=[],initializerEvents=[])
    for row in patch['patch']['closure']:
        source=patch['root']/row['dll'];actual=Path(n['data']['outputPath']) if q04 and row['name']=='AssemblyA.Contracts' else source
        result['byteInputs'].append(dict(name=row['name'],sourcePath=str(source),sourceSha256=row['sha256'],actualPath=str(actual),actualSha256=gate.digest(actual),length=actual.stat().st_size,pdbSha256=''))
    sizes=[row['length'] for row in result['byteInputs']];result['orderedSizes']=sizes
    def op(name,code=0,text='Success'):result['operations'].append(dict(operation=name,code=code,name=text))
    op('configure');op('begin');op('reserve')
    for name in order:op('stage:'+name)
    op('validate',13 if q04 else 0,'ReferenceResolutionFailed' if q04 else 'Success')
    if not q04:op('commit',terminal,'ModuleInitializerFailed' if init else 'Success')
    if terminal:
        for name in ('abort-rejected','begin-rejected'):op(name,2 if q04 else 18,'InvalidState' if q04 else 'AlreadyCommitted')
    phases=['before-reserve','after-reserve','after-stage','after-validate']+([] if q04 else ['after-commit'])+(['after-rejected-operations'] if terminal else [])
    counter=0
    def raw(phase,data,thread=1):
        nonlocal counter
        counter+=1;rawpath=path.with_name(path.stem+'.raw-'+str(counter)+'.json');text=json.dumps(data);rawpath.write_text(text)
        return dict(phase=phase,rawJson=text,rawPath=str(rawpath),rawSha256=gate.digest(rawpath),code=0,threadId=thread,ticks=counter)
    def diag(state,staged,published,metadata=False):
        value=diagnostic();value.update(state=state,stateCode=m04.STATE_CODES[state],lastError=terminal if state==final else 0,
            startupCandidateSchemaVersion=1,startupCandidateNames=order,startupObservationMode='EarlyTracking',metadataBudgetCapabilityVersion=1,recoveryCapabilityVersion=1,
            generation=int(published),enumerationGeneration=int(published),classEnumerationGeneration=int(published),retainedBytes=sum(sizes) if staged else 0,
            expected=len(order) if state!='Disabled' else 0,staged=len(order) if staged else 0,
            baselineBuildId=m['baselineBuildId'] if state!='Disabled' else '',patchId=patch['patch']['patchId'] if state!='Disabled' else '',
            closureLoadOrder=order if state!='Disabled' else [])
        if q04 and state=='Failed':value['detail']='AssemblyA.Contracts: Image::ReadType invalid type'
        value['ordinaryAssemblies']=[dict(name=name,isInterpreter=False) for name in order]+([dict(name=name,isInterpreter=True) for name in order] if published else [])
        if state!='Disabled':value['assemblies']=[dict(name=name,mvid=patch['patch']['closure'][i]['mvid'] if staged else '',skeletonBuilt=staged,runtimeMetadataInitialized=metadata,
            published=published,moduleInitializerAttempted=init and published and i<=1,moduleInitializerRan=init and published and i<1) for i,name in enumerate(order)]
        if state in ('Failed','Validated','Committed','FailedAfterCommit','Committing'):
            value['events']=[dict(sequence=1,kind='metadata-begin',name=order[0],generation=0,stagedCount=len(order))]
        return value
    before=r01.evaluate_budget([64,0,0,0],sizes)
    for i,phase in enumerate(phases):
        state=('Disabled','Staging','Staged','Failed' if q04 else 'Validated')[i] if i<4 else final
        published=not q04 and i>=4;d=diag(state,i>=2,published,not q04 and i>=3)
        result['diagnostics'].append(raw(phase,d))
        cap=r01.evaluate_budget([64,0,0,0] if i==0 else before['finalCursors'],sizes)
        cap.update(schemaVersion=1,enabled=True,profileVersion=1,indexBits=22,kindBits=2,remainingSlots=r01.remaining_slots(cap['cursors']),
            ordinaryAllocatedCount=0,shadowAllocatedCount=0 if i<2 else 5,reservedImageCount=0 if i==0 else 5)
        result['capacities'].append(raw(phase,cap))
        rec=dict(schemaVersion=1,enabled=True,capabilityVersion=1,stateCode=m04.STATE_CODES[state],state=state,published=published,abortAllowed=False,
            dispositionCode=0 if terminal else 4,disposition='RestartRequired' if terminal else 'ActiveShadow',terminalFailureCode=terminal,
            reason=('AssemblyA.Contracts: Image::ReadType invalid type' if q04 else 'R01-INIT-THROW:AssemblyA.Implementation.Extensibility') if terminal else '',retainedBytes=sum(sizes) if i>=2 else 0,baselineEligibilityRequiresStartupValidation=bool(terminal))
        result['recovery'].append(raw(phase,rec))
    result['observerSamples']=[raw('before',diag('Staging',False,False),2),raw('after',diag(final,True,not q04,not q04),2)]
    if init:
        for name in order[:2]:result['initializerEvents'].append(dict(name=name,diagnostics=raw('initializer',diag('Committing',True,True,True))))
    write(path,result);return result


class FailurePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.prepared,self.paths=prepared(self.root)
        self.launcher=load_launcher();self.output=self.root/'_temp/AssemblyShadow/failure-run';self.pid=100
    def tearDown(self):self.temp.cleanup()
    def launch(self):
        def process(command,project,console,timeout):
            self.pid+=1;mode=command[command.index('-shadowR01FailureMode')+1];path=Path(command[command.index('-shadowR01FailureResult')+1])
            produce(path,mode,self.prepared,self.pid);Path(command[-1]).write_text('synthetic Unity log');console.write_text('synthetic console')
            return dict(processId=self.pid,startedAtUnix=1000.0+self.pid,durationSeconds=1.0,exitCode=0,timedOut=False)
        args=[]
        for option,key in [('project-root','projectRoot'),('fixture-manifest','fixtureManifestPath'),('on-build','onBuildReceiptPath'),('off-build','offBuildReceiptPath'),('replay-receipt','replayReceiptPath'),('failure-fixtures','failureFixturesPath'),('negative-input','negativeInputPath')]:args += ['--'+option,str(self.paths[key])]
        args+=['--output-root',str(self.output)]
        with patch.object(gate,'prepare',return_value=self.prepared),patch.object(self.launcher,'run_one',side_effect=process):
            self.assertEqual(self.launcher.main(args),0)
        return self.output/'r01-failure-launches.json'
    def test_complete_launcher_producer_and_public_verifier(self):
        path=self.launch()
        with patch.object(gate,'prepare',return_value=self.prepared):
            result=gate.verify_suite(path)
            self.assertEqual(result['result'],'Passed');self.assertEqual(len(result['modes']),3)
            output=self.output/'strict.json';self.assertEqual(gate.main(['--launch-receipt',str(path),'--output',str(output)]),0)
    def test_rebound_result_tampering_is_rejected(self):
        launch=self.launch();original=gate.read(launch)
        cases=[('processId',999),('buildGuid','b'*32),('orderedSizes',[1]*5),('observerJoined',False),('observerSamples',[]),('operations',[]),('patchManifestSha256','f'*64)]
        row=original['processLaunches'][1];path=Path(row['resultPath']);saved=gate.read(path)
        for key,value in cases:
            with self.subTest(key=key):
                bad=copy.deepcopy(saved);bad[key]=value;write(path,bad);receipt=copy.deepcopy(original);receipt['processLaunches'][1]['resultSha256']=gate.digest(path);write(launch,receipt)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
        write(path,saved);write(launch,original)
    def test_raw_tampering_after_rebinding_all_hashes_is_rejected(self):
        launch=self.launch();initial=gate.read(launch)
        cases=[('diagnostics',3,'lastError',9),('diagnostics',3,'retainedBytes',0),('capacities',3,'cursors',[64,0,0,0]),
               ('recovery',-1,'baselineEligibilityRequiresStartupValidation',False),('recovery',-1,'terminalFailureCode',2),('recovery',-1,'disposition','BaselineEligibleAfterAbort'),
               ('observerSamples',-1,'enumerationGeneration',1),('observerSamples',-1,'classEnumerationGeneration',1)]
        path=Path(initial['processLaunches'][1]['resultPath']);saved=gate.read(path)
        for group,index,key,value in cases:
            with self.subTest(group=group,key=key):
                result=copy.deepcopy(saved);row=result[group][index];raw_path=Path(row['rawPath']);old=raw_path.read_text();data=json.loads(row['rawJson']);data[key]=value
                row['rawJson']=json.dumps(data);raw_path.write_text(row['rawJson']);row['rawSha256']=gate.digest(raw_path);write(path,result)
                receipt=copy.deepcopy(initial);receipt['processLaunches'][1]['resultSha256']=gate.digest(path);write(launch,receipt)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
                raw_path.write_text(old)
        write(path,saved)
    def test_recovery_startup_validation_flag_matches_native_disposition(self):
        launch=self.launch();initial=gate.read(launch)
        for mode_index,process in enumerate(initial['processLaunches']):
            path=Path(process['resultPath']);saved=gate.read(path)
            terminal_index=3 if mode_index==1 else 4
            for index in range(terminal_index,len(saved['recovery'])):
                with self.subTest(mode=mode_index,index=index):
                    result=copy.deepcopy(saved);row=result['recovery'][index];raw_path=Path(row['rawPath']);old=raw_path.read_text()
                    data=json.loads(row['rawJson']);data['baselineEligibilityRequiresStartupValidation']=mode_index==0
                    row['rawJson']=json.dumps(data);raw_path.write_text(row['rawJson']);row['rawSha256']=gate.digest(raw_path)
                    write(path,result);receipt=copy.deepcopy(initial);receipt['processLaunches'][mode_index]['resultSha256']=gate.digest(path);write(launch,receipt)
                    with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
                    raw_path.write_text(old)
            write(path,saved)
        write(launch,initial)

    def test_native_transaction_identity_tampering_with_rebound_hashes_is_rejected(self):
        launch=self.launch();initial=gate.read(launch)
        cases=[('baselineBuildId','unrelated-baseline'),('patchId','unrelated-patch'),
               ('closureLoadOrder',['unrelated-closure']),('mvid','unrelated-mvid')]
        for mode_index,process in enumerate(initial['processLaunches']):
            path=Path(process['resultPath']);saved=gate.read(path)
            locations=[(group,index) for group in ('diagnostics','observerSamples') for index in range(len(saved[group]))]
            locations += [('initializerEvents',index) for index in range(len(saved['initializerEvents']))]
            for group,index in locations:
                for key,value in cases:
                    with self.subTest(mode=mode_index,group=group,index=index,key=key):
                        result=copy.deepcopy(saved);row=result[group][index]
                        if group=='initializerEvents':row=row['diagnostics']
                        raw_path=Path(row['rawPath']);old=raw_path.read_text();data=json.loads(row['rawJson'])
                        if key=='mvid':
                            if not data['assemblies']:continue
                            data['assemblies'][0]['mvid']=value
                        else:data[key]=value
                        row['rawJson']=json.dumps(data);raw_path.write_text(row['rawJson']);row['rawSha256']=gate.digest(raw_path)
                        write(path,result);receipt=copy.deepcopy(initial);receipt['processLaunches'][mode_index]['resultSha256']=gate.digest(path);write(launch,receipt)
                        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
                        raw_path.write_text(old)
            write(path,saved)
        write(launch,initial)

    def test_launch_provenance_tampering_is_rejected(self):
        path=self.launch();original=gate.read(path)
        for key,value in [('inputHashesBefore',{}),('modes',[gate.MODES[0]]),('inputsUnchanged',False),('sourcePins',{})]:
            with self.subTest(key=key):
                bad=copy.deepcopy(original);bad[key]=value;write(path,bad)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(path)
    def test_initializer_public_helper_checks_real_pe_hash_and_capacity(self):
        directory=self.root/'initializer-helper';directory.mkdir()
        f,m,b,path,p,compiled,snapshot,seal=patch_fixture(directory,True)
        f['patchId']=p['patchId']=gate.INITIALIZER_ID;f['defines']=gate.DEFINES;seal()
        self.assertEqual(f['defines'], ['ASSEMBLY_SHADOW_P01', 'ASSEMBLY_SHADOW_P03',
            'ASSEMBLY_SHADOW_M03_INITIALIZERS', 'ASSEMBLY_SHADOW_M03_P03',
            'ASSEMBLY_SHADOW_R01_INITIALIZER_THROW'])
        with patch.object(gate.m07,'verify_compile_snapshot',return_value=(compiled,snapshot)),patch.object(gate.prior,'_reflection_snapshot',return_value=None):
            self.assertTrue(gate.verify_initializer(f,m,b,path)['r01Capability'])
            f['defines'] = f['defines'][:-1] + ['ASSEMBLY_SHADOW_M03_INITIALIZER_THROW']
            with self.assertRaisesRegex(VerificationError, 'defines'):
                gate.verify_initializer(f,m,b,path)
            f['defines'] = list(gate.DEFINES)
            p['metadataCapacityReport']['allocations'][1]['slot']=0;seal()
            with self.assertRaises(VerificationError):gate.verify_initializer(f,m,b,path)

    def test_complete_failure_fixture_inventory_replay_and_public_patch_verifier(self):
        import shutil
        directory=self.root/'failure-fixtures';directory.mkdir()
        f,m,b,path,p,compiled,snapshot,seal=patch_fixture(directory,True)
        f['patchId']=p['patchId']=gate.INITIALIZER_ID;f['defines']=gate.DEFINES
        for key in gate.m07.FIXTURE_FIELDS.split():f.setdefault(key,None)
        seal()
        replay=directory/'Replay';shutil.copytree(directory/'patch',replay)
        fixture_path=write(self.root/'real-shaped-m07-fixtures.json',{})
        baseline_path=write(self.root/'helper-baseline.json',b)
        m.update(baselineManifestPath=str(baseline_path),baselineManifestSha256=gate.digest(baseline_path))
        p['baselineManifestSha256']=m['baselineManifestSha256'];seal()
        shutil.copyfile(directory/'patch/patch-manifest.json',replay/'patch-manifest.json')
        shutil.copyfile(directory/'patch/manifest.sha256',replay/'manifest.sha256')
        receipt=dict(schemaVersion=1,kind='R01FailureFixtures',result='Passed',sourcePins=b['sourcePins'],baselineBuildId=m['baselineBuildId'],
            runtimeAbiHash=m['runtimeAbiHash'],baselineManifestPath=str(baseline_path),baselineManifestSha256=gate.digest(baseline_path),
            fixtureManifestPath=str(fixture_path),fixtureManifestSha256=gate.digest(fixture_path),initializer=f,
            replayPatchManifest=str(replay/'patch-manifest.json'),replayPatchManifestSha256=gate.digest(replay/'patch-manifest.json'),replayBytesEqual=True,
            files=[dict(path=str(file),sha256=gate.digest(file),length=file.stat().st_size) for file in sorted(directory.rglob('*')) if file.is_file()])
        receipt_path=write(directory/'failure-fixtures.json',receipt)
        context=dict(sourcePins=b['sourcePins'],manifest=m,baseline=b)
        with patch.object(gate.m07,'verify_compile_snapshot',return_value=(compiled,snapshot)),patch.object(gate.prior,'_reflection_snapshot',return_value=None):
            actual=gate.verify_failure_fixtures(receipt_path,context,fixture_path)
            self.assertEqual(actual['initializer']['patch']['patchId'],gate.INITIALIZER_ID)
            (directory/'undeclared.dll').write_bytes(b'not-in-inventory')
            with self.assertRaises(VerificationError):gate.verify_failure_fixtures(receipt_path,context,fixture_path)
            (directory/'undeclared.dll').unlink()
            changed=copy.deepcopy(receipt);changed['sourcePins']['demo']['revision']='f'*40;write(receipt_path,changed)
            with self.assertRaises(VerificationError):gate.verify_failure_fixtures(receipt_path,context,fixture_path)

    def test_initializer_failure_cannot_be_relabelled_as_complete_initialization(self):
        launch=self.launch();receipt=gate.read(launch);path=Path(receipt['processLaunches'][2]['resultPath']);result=gate.read(path)
        row=result['diagnostics'][-1];data=json.loads(row['rawJson']);data['assemblies'][1]['moduleInitializerRan']=True
        row['rawJson']=json.dumps(data);Path(row['rawPath']).write_text(row['rawJson']);row['rawSha256']=gate.digest(Path(row['rawPath']))
        write(path,result);receipt['processLaunches'][2]['resultSha256']=gate.digest(path);write(launch,receipt)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
