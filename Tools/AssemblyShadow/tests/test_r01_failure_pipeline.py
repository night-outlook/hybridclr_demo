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
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_failure_results as gate
import r01_early_capsule as early_capsule
import r01_results as r01
import m04_results as m04
from shadow_tools import VerificationError
from test_m04_results import diagnostic, make_pe
from test_r01_metadata_pipeline import patch_fixture
from test_r01_early_results import emit_receipt


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
            dll=directory/(name+'.dll');mvid=uuid.UUID(int=index+1);dll.write_bytes(make_pe(name,mvid=mvid))
            rows.append(dict(name=name,mvid=str(mvid),dll=dll.name,sha256=gate.digest(dll),dllSize=dll.stat().st_size,pdbSha256='',pdb=''))
        p=dict(patchId=patchid,loadOrder=order,closure=rows,dllOnly=True);path=write(directory/'patch-manifest.json',p)
        fixtures[patchid]=dict(root=directory,path=path,patch=p)
    negative=root/'negative.dll'
    negative.write_bytes((fixtures['P03']['root']/'AssemblyA.Contracts.dll').read_bytes())
    baseline_path=write(root/'baseline.json',{})
    resource_root=root/'resource';resource_root.mkdir()
    write(resource_root/'resource-build-receipt.json',dict(bundleDirectory='Bundles',bundles=[]))
    manifest=dict(unityVersion='2022.3.62f2',baselineBuildId='failure-test',runtimeAbiHash='1'*64,
                  baselineManifestPath=str(baseline_path),baselineManifestSha256=gate.digest(baseline_path),
                  candidateNames=order,stableAotNames=['AssemblyShadowDemo.Bootstrap','mscorlib'])
    player=dict(buildGuid='a'*32,nativeLibrarySha256='2'*64,nativeMetadataSha256='3'*64,inputSnapshotHash='4'*64)
    context=dict(manifest=manifest,baseline=dict(resourceBaselinePath='resource'),
                 on=dict(path=paths['onBuildReceiptPath'],output=app,player=player),
                 fixtures=fixtures,sourcePins={'fixture':'explicit-synthetic'})
    failures=dict(path=paths['failureFixturesPath'],initializer=fixtures[gate.INITIALIZER_ID],
                  data=dict(fixtureManifestPath=str(paths['fixtureManifestPath']),fixtureManifestSha256=gate.digest(paths['fixtureManifestPath'])),
                  files={paths['failureFixturesPath']})
    negative_info=dict(path=paths['negativeInputPath'],data=dict(outputPath=str(negative)),
                       files={paths['negativeInputPath'],negative})
    return dict(context=context,profile=1,failures=failures,negative=negative_info,
                runner=types.SimpleNamespace(executable_for=lambda output:exe),
                inventory={p for p in root.rglob('*') if p.is_file()}),paths


def produce(path,mode,p,process_id,capsule_path,early_path):
    c=p['context'];b=c['on'];m=c['manifest'];f=p['failures'];n=p['negative']
    patch=c['fixtures'][gate.INITIALIZER_ID if mode==gate.MODES[2] else 'P03']
    order=patch['patch']['loadOrder']
    early=gate.read(early_path);final=early['snapshots'][-1]
    expected_inputs=[]
    for row in patch['patch']['closure']:
        source=patch['root']/row['dll']
        actual=Path(n['data']['outputPath']) if mode==gate.MODES[1] and row['name']=='AssemblyA.Contracts' else source
        expected_inputs.append(dict(name=row['name'],sourcePath=str(source),sourceSha256=row['sha256'],
            actualPath=str(actual),actualSha256=gate.digest(actual),length=actual.stat().st_size,pdbSha256=''))
    counter=0
    def raw(label,text):
        nonlocal counter
        counter+=1;raw_path=path.with_name(path.stem+'.raw-'+str(counter)+'.json')
        raw_path.write_text(text)
        return dict(phase='after-host-continuation',rawJson=text,rawPath=str(raw_path),
                    rawSha256=gate.digest(raw_path),code=0,threadId=1,ticks=counter)
    result=dict(schemaVersion=2,kind='R01FailureHandoffResult',mode=mode,result='Passed',error='',
        resultPath=str(path),processId=process_id,mainThreadId=1,
        unityVersion=m['unityVersion'],platform='OSXPlayer',buildGuid=b['player']['buildGuid'],
        playerDataPath=str(b['output']/'Contents'),baselineBuildId=m['baselineBuildId'],runtimeAbiHash=m['runtimeAbiHash'],
        fixtureManifestPath=f['data']['fixtureManifestPath'],fixtureManifestSha256=f['data']['fixtureManifestSha256'],
        playerBuildReceiptPath=str(b['path']),playerBuildReceiptSha256=gate.digest(b['path']),
        baselineManifestPath=m['baselineManifestPath'],baselineManifestSha256=m['baselineManifestSha256'],
        failureFixturesPath=str(f['path']),failureFixturesSha256=gate.digest(f['path']),
        negativeInputPath=str(n['path']),negativeInputSha256=gate.digest(n['path']),
        patchId=patch['patch']['patchId'],patchManifestPath=str(patch['path']),patchManifestSha256=gate.digest(patch['path']),
        nativeLibrarySha256=b['player']['nativeLibrarySha256'],nativeMetadataSha256=b['player']['nativeMetadataSha256'],
        inputSnapshotHash=b['player']['inputSnapshotHash'],il2cpp=True,closureLoadOrder=order,
        orderedSizes=[row['length'] for row in expected_inputs],byteInputs=expected_inputs,
        earlyMode=gate.early_mode(mode),earlyReceiptPath=str(early_path),earlyReceiptSha256=gate.digest(early_path),
        capsulePath=str(capsule_path),capsuleSha256=gate.digest(capsule_path),
        postHostDiagnostics=raw('diagnostics',final['diagnosticsJson']),
        postHostCapacity=raw('capacity',final['capacityJson']),
        postHostRecovery=raw('recovery',final['recoveryJson']))
    write(path,result);return result


class FailurePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.prepared,self.paths=prepared(self.root)
        self.launcher=load_launcher();self.output=self.root/'_temp/AssemblyShadow/failure-run';self.pid=100
    def tearDown(self):self.temp.cleanup()
    def launch(self):
        def process(command,project,console,timeout):
            self.pid+=1
            mode=command[command.index('-shadowR01FailureMode')+1]
            path=Path(command[command.index('-shadowR01FailureResult')+1])
            capsule_path=Path(command[command.index('-shadowEarlyCapsule')+1])
            early_path=Path(command[command.index('-shadowEarlyResult')+1])
            data=early_capsule.decode(capsule_path.read_bytes())
            write(early_path,emit_receipt(data,capsule_path,early_path,pid=self.pid))
            produce(path,mode,self.prepared,self.pid,capsule_path,early_path)
            Path(command[-1]).write_text('synthetic Unity log');console.write_text('synthetic console')
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
    def test_failure_admission_capsules_are_mode_bound_baseline_inputs(self):
        launch=self.launch();receipt=gate.read(launch)
        hashes=set()
        for row in receipt['processLaunches']:
            data=early_capsule.decode(Path(row['capsulePath']).read_bytes())
            self.assertEqual(gate.early_mode(row['mode']),data['mode'])
            binding=gate.read(Path(row['earlyBindingPath']))
            self.assertEqual(row['mode'],binding['failureMode'])
            self.assertEqual(gate.early_mode(row['mode']),binding['earlyMode'])
            self.assertIn(str(Path(row['earlyBindingPath'])),[item['path'] for item in data['prerequisiteFiles']])
            hashes.add(row['capsuleSha256'])
        self.assertEqual(len(gate.MODES),len(hashes))

    def test_missing_stale_substituted_and_mode_mismatched_capsules_reject(self):
        launch=self.launch();original=gate.read(launch)
        row=original['processLaunches'][1]
        capsule_path=Path(row['capsulePath']);saved=capsule_path.read_bytes()

        capsule_path.unlink()
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)
        capsule_path.write_bytes(saved)

        bad=copy.deepcopy(original);bad['processLaunches'][1]['capsuleSha256']='0'*64;write(launch,bad)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)

        source=Path(original['processLaunches'][0]['capsulePath'])
        capsule_path.write_bytes(source.read_bytes())
        substituted=copy.deepcopy(original);new_hash=gate.digest(capsule_path)
        substituted['processLaunches'][1]['capsuleSha256']=new_hash
        command=substituted['processLaunches'][1]['command'];index=command.index('-shadowEarlyCapsuleSha256')+1;command[index]=new_hash
        write(launch,substituted)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)

        capsule_path.write_bytes(saved)
        data=early_capsule.decode(saved);data['mode']='Control';capsule_path.write_bytes(early_capsule.encode(data))
        mismatch=copy.deepcopy(original);new_hash=gate.digest(capsule_path)
        mismatch['processLaunches'][1]['capsuleSha256']=new_hash
        command=mismatch['processLaunches'][1]['command'];index=command.index('-shadowEarlyCapsuleSha256')+1;command[index]=new_hash
        write(launch,mismatch)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)

        capsule_path.write_bytes(saved);write(launch,original)

    def test_early_receipt_must_bind_same_process_and_capsule(self):
        launch=self.launch();original=gate.read(launch);row=original['processLaunches'][2]
        early_path=Path(row['earlyResultPath']);saved=gate.read(early_path)
        for key,value in [('processId',999999),('capsuleSha256','f'*64),('mode','Control')]:
            with self.subTest(key=key):
                changed=copy.deepcopy(saved);changed[key]=value;write(early_path,changed)
                receipt=copy.deepcopy(original);receipt['processLaunches'][2]['earlyResultSha256']=gate.digest(early_path);write(launch,receipt)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
                    gate.verify_suite(launch)
        write(early_path,saved);write(launch,original)

    def test_failure_probe_adopts_early_transaction_without_late_mutation(self):
        source=(Path(gate.__file__).resolve().parents[2] /
                'Assets/AssemblyShadowDemo/Bootstrap/R01FailureProbe.cs').read_text()
        self.assertIn('ShadowPatchMetadataReservation.ValidateIfDeclared',source)
        self.assertIn('R01EarlyStartup.LastReceiptJson',source)
        self.assertIn('MetadataFailureContinue',source)
        self.assertIn('InitializerFailureContinue',source)
        self.assertIn('CapturePostHost',source)
        for call in ('ConfigureCandidates(', 'BeginTransaction(', 'ReserveMetadataBudget(',
                     'StageAssembly(', 'ValidateTransaction(', 'CommitTransaction('):
            self.assertNotIn('AssemblyShadowRuntime.'+call,source)
        self.assertNotIn('patch.nativeBudgetCapabilityVersion == 1',source)

    def test_public_verifier_has_direct_module_entrypoint(self):
        source=Path(gate.__file__).read_text()
        self.assertIn('if __name__ == "__main__":',source)
        self.assertIn('raise SystemExit(main())',source)

    def test_rebound_result_tampering_is_rejected(self):
        launch=self.launch();original=gate.read(launch)
        cases=[('processId',999),('buildGuid','b'*32),('orderedSizes',[1]*5),('earlyMode','Baseline'),('capsuleSha256','f'*64),('patchManifestSha256','f'*64)]
        row=original['processLaunches'][1];path=Path(row['resultPath']);saved=gate.read(path)
        for key,value in cases:
            with self.subTest(key=key):
                bad=copy.deepcopy(saved);bad[key]=value;write(path,bad);receipt=copy.deepcopy(original);receipt['processLaunches'][1]['resultSha256']=gate.digest(path);write(launch,receipt)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):gate.verify_suite(launch)
        write(path,saved);write(launch,original)
    def test_post_host_raw_tampering_after_rebinding_hashes_is_rejected(self):
        launch=self.launch();initial=gate.read(launch)
        process=initial['processLaunches'][1];path=Path(process['resultPath']);saved=gate.read(path)
        cases=[('postHostDiagnostics','state','Committed'),('postHostDiagnostics','patchId','wrong'),
               ('postHostCapacity','lifetimeReservedImageCount',999),
               ('postHostRecovery','terminalFailureCode',0),
               ('postHostRecovery','disposition','ActiveShadow')]
        for group,key,value in cases:
            with self.subTest(group=group,key=key):
                result=copy.deepcopy(saved);row=result[group];raw_path=Path(row['rawPath']);old=raw_path.read_text()
                data=json.loads(row['rawJson']);data[key]=value
                row['rawJson']=json.dumps(data);raw_path.write_text(row['rawJson']);row['rawSha256']=gate.digest(raw_path)
                write(path,result);receipt=copy.deepcopy(initial);receipt['processLaunches'][1]['resultSha256']=gate.digest(path);write(launch,receipt)
                with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
                    gate.verify_suite(launch)
                raw_path.write_text(old)
        write(path,saved);write(launch,initial)

    def test_early_transaction_identity_is_authoritative(self):
        launch=self.launch();initial=gate.read(launch);row=initial['processLaunches'][2]
        early_path=Path(row['earlyResultPath']);saved=gate.read(early_path)
        changed=copy.deepcopy(saved);changed['patchId']='wrong-early-patch';write(early_path,changed)
        receipt=copy.deepcopy(initial);receipt['processLaunches'][2]['earlyResultSha256']=gate.digest(early_path);write(launch,receipt)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)
        write(early_path,saved);write(launch,initial)

    def test_initializer_publication_cannot_be_relabelled_post_host(self):
        launch=self.launch();initial=gate.read(launch);row=initial['processLaunches'][2]
        path=Path(row['resultPath']);saved=gate.read(path);result=copy.deepcopy(saved)
        raw_row=result['postHostDiagnostics'];raw_path=Path(raw_row['rawPath']);old=raw_path.read_text()
        data=json.loads(raw_row['rawJson']);data['assemblies'][1]['moduleInitializerRan']=True
        raw_row['rawJson']=json.dumps(data);raw_path.write_text(raw_row['rawJson']);raw_row['rawSha256']=gate.digest(raw_path)
        write(path,result);initial['processLaunches'][2]['resultSha256']=gate.digest(path);write(launch,initial)
        with patch.object(gate,'prepare',return_value=self.prepared),self.assertRaises(VerificationError):
            gate.verify_suite(launch)
        raw_path.write_text(old)

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

    def test_profile2_capacity_recomputes_all_or_nothing_admission(self):
        sizes = [100, 200]
        value = dict(schemaVersion=2, enabled=True, profileVersion=2,
            maximumImageCount=gate.PROFILE2_MAX_IMAGES, maximumDllBytes=gate.PROFILE2_MAX_DLL_BYTES,
            usablePageCapacity=gate.PROFILE2_USABLE_PAGE_CAPACITY,
            chargedPageCeiling=gate.PROFILE2_CHARGED_PAGE_CEILING,
            minimumFreePageMargin=gate.PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
            reservedPages=0, mappedPages=0, lifetimeReservedImageCount=7,
            remainingImageCount=gate.PROFILE2_MAX_IMAGES - 7, requiredImages=2,
            acceptedImages=2, firstFailingIndex=-1, firstFailingSize=0, failureReason='None',
            fitsPreliminary=True, runtimeFinalizationRequired=True,
            aggregateInputDllBytes=300, aggregateInputDllBytesInformational=True,
            ordinaryAllocatedCount=4, shadowAllocatedCount=0, reservedShadowImageCount=7)
        self.assertIs(gate.verify_profile2_capacity(value, sizes, 'profile2'), value)
        for key, replacement in [('aggregateInputDllBytes', 301), ('acceptedImages', 1),
                                 ('fitsPreliminary', False)]:
            bad = copy.deepcopy(value); bad[key] = replacement
            with self.subTest(key=key), self.assertRaises(VerificationError):
                gate.verify_profile2_capacity(bad, sizes, 'profile2')

    def test_profile2_capacity_reports_native_admission_priority(self):
        sizes = [100, gate.PROFILE2_MAX_DLL_BYTES + 1]
        value = dict(schemaVersion=2, enabled=True, profileVersion=2,
            maximumImageCount=gate.PROFILE2_MAX_IMAGES, maximumDllBytes=gate.PROFILE2_MAX_DLL_BYTES,
            usablePageCapacity=gate.PROFILE2_USABLE_PAGE_CAPACITY,
            chargedPageCeiling=gate.PROFILE2_CHARGED_PAGE_CEILING,
            minimumFreePageMargin=gate.PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
            reservedPages=0, mappedPages=0, lifetimeReservedImageCount=0,
            remainingImageCount=gate.PROFILE2_MAX_IMAGES, requiredImages=2,
            acceptedImages=0, firstFailingIndex=1, firstFailingSize=sizes[1], failureReason='DllTooLarge',
            fitsPreliminary=False, runtimeFinalizationRequired=True,
            aggregateInputDllBytes=sum(sizes), aggregateInputDllBytesInformational=True,
            ordinaryAllocatedCount=0, shadowAllocatedCount=0, reservedShadowImageCount=0)
        gate.verify_profile2_capacity(value, sizes, 'profile2.failure')

    def test_profile2_selection_requires_complete_verified_baseline_contract(self):
        profile = dict(schemaVersion=2, profileVersion=2, nativeBudgetCapabilityVersion=2,
            codecId='SparseSignedInt32', codecBits=32, invalidIndexSentinel=-1,
            aotMaxIndex=2147483647, minImageId=1, maximumImageCount=gate.PROFILE2_MAX_IMAGES,
            pageValues=4096, usablePageCapacity=gate.PROFILE2_USABLE_PAGE_CAPACITY,
            chargedPageCeiling=gate.PROFILE2_CHARGED_PAGE_CEILING,
            minimumFreePageMargin=gate.PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
            maximumDllBytes=gate.PROFILE2_MAX_DLL_BYTES, aggregateDllEnvelopeBytes=536870912,
            nativeSourceRevision='a' * 40, nativeCodecHeaderSha256='b' * 64)
        report = dict(schemaVersion=2, profileVersion=2, nativeBudgetCapabilityVersion=2,
            budgetCapabilityVersion=2, nativeSourceRevision='a' * 40,
            nativeCodecHeaderSha256='b' * 64, codecId='SparseSignedInt32', codecBits=32,
            invalidIndexSentinel=-1, aotMaxIndex=2147483647, minImageId=1,
            maxImages=gate.PROFILE2_MAX_IMAGES, pageValues=4096,
            usablePages=gate.PROFILE2_USABLE_PAGE_CAPACITY,
            maxChargedPages=gate.PROFILE2_CHARGED_PAGE_CEILING,
            maxDllBytes=gate.PROFILE2_MAX_DLL_BYTES, aggregateDllEnvelopeBytes=536870912,
            maximumImageCount=gate.PROFILE2_MAX_IMAGES, maximumDllBytes=gate.PROFILE2_MAX_DLL_BYTES,
            usablePageCapacity=gate.PROFILE2_USABLE_PAGE_CAPACITY,
            chargedPageCeiling=gate.PROFILE2_CHARGED_PAGE_CEILING,
            minimumFreePageMargin=gate.PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
            currentReservedImageCount=0, reservedImageCountBefore=0, reservedImageCountAfter=0,
            requestedImageCount=0,
            reservedPages=0, mappedPages=0, lifetimeReservedImageCount=0,
            remainingImageCount=gate.PROFILE2_MAX_IMAGES, requiredImages=0,
            aggregateDllBytes=0, aggregateInputDllBytes=0,
            aggregateInputDllBytesInformational=True, inputs=[], allocations=[], acceptedImages=0,
            fitsImageCount=True, aggregateDllEnvelopeFits=True, aggregateDllEnvelopeExceeded=False,
            inputCountWasBounded=False, admissionAccepted=True, fitsPreliminary=True,
            finalPageFitKnown=False, runtimeFinalizationRequired=True, admissionKind='Preliminary',
            firstFailingIndex=-1, firstFailingAssembly=None, failureReason='None')
        context = {'baseline': {'nativeBudgetCapabilityVersion': 2,
            'metadataEncodingProfile2': profile, 'metadataCapacityReport2': report}}
        self.assertEqual(gate.metadata_profile(context), 2)
        bad = copy.deepcopy(context); bad['baseline'].pop('metadataCapacityReport2')
        with self.assertRaises(VerificationError): gate.metadata_profile(bad)


if __name__ == "__main__":
    unittest.main()
