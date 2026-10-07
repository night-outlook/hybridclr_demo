"""Synthetic membership/archive tests, NOT Unity/Player/compiler executions."""
import copy
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import h1_successor_evidence as h
import h1_witness_contract as w
from test_h1_witness_contract import configuration


def witness_result(config_sha):
    digest='f'*64
    return {'schemaVersion':2,'mode':'M02ReflectionBindings','result':'Passed','il2cpp':True,
        'configurationSha256':config_sha,'configurationHash':digest,
        'h1WitnessContractValidated':True,'h1WitnessMethod':w.METHOD,'h1WitnessPrimaryHash':w.METHOD_VARIANTS[0][0],
        'h1WitnessOperationIndex':25,'h1WitnessImageSha256':w.IMAGE_SHA256,'h1WitnessProviderAssembly':w.PROVIDER,
        'h1WitnessGuard':'__AssemblyShadowReflectionBinding_'+digest+'_'+hashlib.sha256(w.SITE_ID.encode()).hexdigest(),
        'h1WitnessTamperRejected':True,'h1WitnessNullRejected':True,'h1WitnessCallerBytesUnchanged':True,
        'h1WitnessAssemblyResolveEvents':0}


class Fixture:
    def __init__(self,root):
        self.root=root;self.root.mkdir();self.rows={};self.roles={}
        self.source={k:{'revision':str(i+1)*40} for i,k in enumerate(('demo','hybridclr','hybridclrUnity','il2cppPlus'))}
        self.source.update(unityVersion='2022.3.62f2',target='StandaloneOSX',architecture='arm64')
        self.add('candidate-source-pins',self.source,role=True)
        self.add('reproduction-source-pins',dict(self.source,demo={'revision':'a'*40}),role=True)
        conf=self.add('witness-configuration',configuration(),role=True)
        self.add('witness-runtime',witness_result(conf['sha256']),role=True)
        for role in h.SINGLE_ROLES-set(self.roles):self.add(role,{'notRuntimeEvidence':True},role=True)
        for role in h.MULTI_ROLES:self.roles[role]=[]
        self.builds={}
        for prefix,modes in (('candidate',('On/Debug','On/Release','Off/Debug','Off/Release')),('reproduction',('On/Debug','On/Release'))):
            builds={};proofs=[];summary=[];pin=self.rows[prefix+'-source-pins'];src=self.json(pin)
            for i,mode in enumerate(modes):
                ident=prefix+'-'+mode.replace('/','-');guid=hashlib.md5(ident.encode()).hexdigest()
                native=self.add(ident+'-native',b'SYNTHETIC-NATIVE');compiler=self.add(ident+'-compiler',b'SYNTHETIC-COMPILER')
                graph=self.add(ident+'-graph',{'Nodes':[]});header=self.add(ident+'-config',b'fixture');sdk=self.add(ident+'-sdk',b'fixture')
                base={'buildGuid':guid,'inputSnapshotHash':'5'*64,'nativeLibrarySha256':native['sha256'],'sourcePinSha256':pin['sha256']}
                cp=dict(base,buildId='H1Count-'+mode.replace('/','-'),nativeLibraryPath=native['rawPath'],compilerPath=compiler['rawPath'],compilerSha256=compiler['sha256'],responseFiles=[],
                    beeActionGraphPath=graph['rawPath'],beeActionGraphSha256=graph['sha256'],il2cppConfigPath=header['rawPath'],il2cppConfigSha256=header['sha256'],sdkSettingsPath=sdk['rawPath'],sdkSettingsSha256=sdk['sha256'])
                cp_row=self.add(ident+'-cp',cp)
                begin=self.add(ident+'-begin',{'kind':'H1ManagedSourceBegin','sourcePinSha256':pin['sha256'],'sources':[]})
                mc=dict(base,kind='H1ManagedSourceCapture',begin={'path':begin['rawPath'],'sha256':begin['sha256']},actualInputs=[],graphs=[])
                mc_row=self.add(ident+'-mc',mc)
                b=dict(base,schemaVersion=1,kind='H1CountDiagnosticPlayerBuild',diagnosticOnly=True,featureEnabled=mode.startswith('On/'),cppConfiguration=mode.split('/')[1],
                       baselineBuildId=cp['buildId'],sourcePinsJson=json.dumps(src),compilerProvenance=cp,
                       compilerProvenancePath=cp_row['rawPath'],compilerProvenanceSha256=cp_row['sha256'],
                       managedSourceProvenancePath=mc_row['rawPath'],managedSourceProvenanceSha256=mc_row['sha256'])
                br=self.add(ident+'-build',b);builds[mode]=(br,b);self.roles[prefix+'-count-builds'].append(br['id'])
                mr=self.add(ident+'-mv',dict(base,kind='H1ManagedSourceGraphVerification',status='SourceGraphBound',capturePath=mc_row['rawPath'],captureSha256=mc_row['sha256'],rows=[{'assembly':a} for a in ('AssemblyShadowDemo.Bootstrap','AssemblyShadow.R01BDiagnostics')]))
                self.roles[prefix+'-managed-verifications'].append(mr['id'])
                summary.append(dict(base,mode=mode,receiptPath=br['rawPath'],receiptSha256=br['sha256'],il2cppDebug='1' if mode.endswith('Debug') else '0',ndebug='0' if mode.endswith('Debug') else '1'))
            self.builds[prefix]=builds
            self.add(prefix+'-compiler-verification',{'kind':'H1CompilerProvenanceVerification','status':'Passed','rows':summary},role=True)
        self.make_count();self.make_startup();self.make_reproduction()
    def add(self,id,value,role=False):
        path=self.root/(id+'.bin');path.write_bytes(value if type(value) is bytes else json.dumps(value,sort_keys=True).encode())
        row={'id':id,'rawPath':'external-artifact://test/'+id,'localPath':str(path),'sha256':h.digest(path),'sizeBytes':path.stat().st_size}
        self.rows[id]=row
        if role:self.roles[id]=id
        return row
    def json(self,row):return h.read_json(row['localPath'])
    def make_count(self):
        cells=[]
        for i,cellid in enumerate(sorted(h.COUNT_CELLS)):
            family,case,path,cpp=cellid.split('/');build=self.builds['candidate'][('Off' if path=='Ordinary-OFF' else 'On')+'/'+cpp][0]
            raw=self.add('count-raw-'+str(i),{'schemaVersion':2,'result':'Passed','family':family,'caseId':case})
            launch=self.add('count-launch-'+str(i),{'synthetic':i})
            cells.append({'cellId':cellid,'reportSha256':raw['sha256'],'launchReceiptSha256':launch['sha256'],'buildReceiptSha256':build['sha256'],'runId':'run-'+str(i)})
        self.add('count-matrix',{'schemaVersion':1,'kind':'H1CountMatrixVerification','result':'Passed','cellCount':132,'expectedCellCount':132,'cells':cells,'inputs':{}},role=True)
    def make_startup(self):
        self.add('baseline-on',{'player':{'buildGuid':'6'*32}},role=True);self.add('baseline-off',{'player':{'buildGuid':'7'*32}},role=True)
        rows=[];summaries=[]
        for i,mode in enumerate(h.STARTUP_MODES):
            positive=i<3;pid=i+100
            cap=self.add('cap-'+mode,b'capsule-'+mode.encode());log=self.add('log-'+mode,b'log');console=self.add('console-'+mode,b'log')
            early=self.add('early-'+mode,{'kind':'R01EarlyStartupReceipt','mode':mode,'processId':pid,'capsuleSha256':cap['sha256'],
                'result':'Passed' if positive else 'PassedExpectedFailure' if mode in ('MetadataFailure','InitializerFailure') else 'PassedExpectedRejection','callbackReturnCode':0 if positive else 1,'error':''})
            m07=self.add('m07-'+mode,{'result':'Passed','buildGuid':'6'*32}) if positive else None
            rows.append({'mode':mode,'passed':True,'inputsUnchanged':True,'timedOut':False,'exitCode':0 if positive else 1,'processId':pid,'startedAtUnix':10000+i,
                'capsulePath':cap['rawPath'],'capsuleSha256':cap['sha256'],'earlyResultPath':early['rawPath'],'earlyResultSha256':early['sha256'],
                'm07ResultPath':m07['rawPath'] if m07 else '', 'm07ResultSha256':m07['sha256'] if m07 else '',
                'logPath':log['rawPath'],'logSha256':log['sha256'],'consolePath':console['rawPath'],'consoleSha256':console['sha256']})
            summaries.append({'mode':mode,'diagnosticProfileComplete':True})
        launch=self.add('startup-launches',{'kind':'R01EarlyLaunches','sourcePins':self.source,'inputsUnchanged':True,'requestedModes':list(h.STARTUP_MODES),'processLaunches':rows,
            'onBuildReceiptPath':self.rows['baseline-on']['rawPath'],'offBuildReceiptPath':self.rows['baseline-off']['rawPath'],'inputHashesBefore':{},'inputHashesAfter':{}},role=True)
        self.add('startup-verification',{'kind':'R01EarlyVerification','result':'PassedBoundedProfile','launchReceipt':launch['rawPath'],'launchReceiptSha256':launch['sha256'],'sourcePins':self.source,'modes':summaries},role=True)
    def make_reproduction(self):
        cells=[]
        for i,(family,case,cpp) in enumerate(sorted(h.REPRO_CELLS)):
            name='repro-'+str(i);abort=family=='nested' and cpp=='Debug';launch=self.add(name+'-launch',{'fixture':case})
            cell={'family':family,'caseId':case,'cppConfiguration':cpp,'inputsUnchanged':True,'rawLaunchPath':launch['rawPath'],
                'classification':'AssertAbort' if abort else 'UnexpectedAccepted'}
            if abort:
                log=self.add(name+'-log',b'Assertion failed: nested_type_count\nSIGABRT (6)')
                cell.update(crashed=True,launcherExitCode=-6,rawUnityLogPath=log['rawPath'],rawResultPath='expected-missing')
            else:
                raw=self.add(name+'-result',{'caseId':case,'result':'Failed','operationSteps':[{'operation':'ordinary-path-selected'},{'operation':'Assembly.Load(byte[])','success':True,'code':'Success'}]})
                cell['rawResultPath']=raw['rawPath']
            cells.append(cell)
        self.add('reproduction-execution',{'kind':'H1UnfixedReproductionExecution','candidateAcceptance':False,'freshProcessPerCell':True,'sourcePinSha256':self.rows['reproduction-source-pins']['sha256'],
            'builds':{cpp:{'receipt':self.builds['reproduction']['On/'+cpp][0]['rawPath'],'receiptSha256':self.builds['reproduction']['On/'+cpp][0]['sha256']} for cpp in ('Debug','Release')},'cells':cells},role=True)
    def selection(self):return {'schemaVersion':2,'kind':'H1SuccessorEvidenceSelection','chainId':'synthetic-only','roles':self.roles,'artifacts':list(self.rows.values())}
    def store(self):return h.Store(self.selection())


class SuccessorTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.f=Fixture(self.root/'artifacts')
    def tearDown(self):self.temp.cleanup()
    def test_membership_gate_never_approves_M08(self):
        _,r=h.validate_selection(self.f.selection());self.assertEqual('SelectionBoundNotM08Acceptance',r['status']);self.assertFalse(r['humanGatePassed']);self.assertFalse(r['mayEnterR02'])
    def test_missing_reproduction_role(self):
        del self.f.roles['reproduction-execution']
        with self.assertRaisesRegex(ValueError,'membership'):self.f.store()
    def test_missing_capture_is_unavailable_not_failed_runtime(self):
        Path(self.f.rows['count-matrix']['localPath']).unlink()
        with self.assertRaises(h.EvidenceUnavailable):self.f.store()
    def test_hash_mismatch_is_invalid(self):
        Path(self.f.rows['count-matrix']['localPath']).write_bytes(b'changed')
        with self.assertRaises(h.EvidenceInvalid):self.f.store()
    def test_raw_schema1_rejected_summary_schema1_allowed(self):
        matrix=self.f.json(self.f.rows['count-matrix']);row=matrix['cells'][0]
        original=next(r for r in self.f.rows.values() if r['sha256']==row['reportSha256']);v=self.f.json(original);v['schemaVersion']=1
        new=self.f.add(original['id'],v);row['reportSha256']=new['sha256'];self.f.add('count-matrix',matrix,role=True)
        with self.assertRaisesRegex(ValueError,'raw count schema'):h.validate_count_matrix(self.f.store(),self.f.builds['candidate'])
    def test_wrong_feature_cell_build_rejected(self):
        matrix=self.f.json(self.f.rows['count-matrix']);matrix['cells'][0]['buildReceiptSha256']=self.f.builds['candidate']['On/Debug'][0]['sha256'];self.f.add('count-matrix',matrix,role=True)
        with self.assertRaisesRegex(ValueError,'compiler/feature'):h.validate_count_matrix(self.f.store(),self.f.builds['candidate'])
    def test_missing_count_run_rejected(self):
        matrix=self.f.json(self.f.rows['count-matrix']);matrix['cells'].pop();self.f.add('count-matrix',matrix,role=True)
        with self.assertRaises(ValueError):h.validate_count_matrix(self.f.store(),self.f.builds['candidate'])
    def test_negative_startup_exit1_and_no_m07_are_correct(self):self.assertEqual(11,h.validate_startup(self.f.store())['modes'])
    def test_negative_startup_exit0_is_not_pass(self):
        v=self.f.json(self.f.rows['startup-launches']);v['processLaunches'][3]['exitCode']=0;self.f.add('startup-launches',v,role=True)
        with self.assertRaisesRegex(ValueError,'expected process exit'):h.validate_startup(self.f.store())
    def test_negative_startup_cannot_handoff(self):
        v=self.f.json(self.f.rows['startup-launches']);v['processLaunches'][3]['m07ResultPath']='wrong';self.f.add('startup-launches',v,role=True)
        with self.assertRaisesRegex(ValueError,'must not hand off'):h.validate_startup(self.f.store())
    def test_startup_reuse_audit_cannot_substitute(self):
        v=self.f.json(self.f.rows['startup-launches']);v['kind']='H1StartupReuseAudit';self.f.add('startup-launches',v,role=True)
        with self.assertRaisesRegex(ValueError,'reuse audit'):h.validate_startup(self.f.store())
    def test_startup_diagnostic_incomplete_rejected(self):
        v=self.f.json(self.f.rows['startup-verification']);v['result']='DiagnosticIncomplete';self.f.add('startup-verification',v,role=True)
        with self.assertRaisesRegex(ValueError,'bounded result'):h.validate_startup(self.f.store())
    def test_repro_assert_does_not_require_missing_managed_result(self):
        self.assertEqual({'cells':8,'unexpectedAccepted':6,'assertAbort':2},h.validate_reproduction(self.f.store(),self.f.builds['reproduction']))
    def test_repro_summary_cannot_replace_assert_log(self):
        v=self.f.json(self.f.rows['reproduction-execution']);cell=next(c for c in v['cells'] if c['classification']=='AssertAbort')
        r=self.f.add('empty-assert-log',b'crash summary');cell['rawUnityLogPath']=r['rawPath'];self.f.add('reproduction-execution',v,role=True)
        with self.assertRaisesRegex(ValueError,'actual nested-count'):h.validate_reproduction(self.f.store(),self.f.builds['reproduction'])
    def test_repro_wrong_fresh_build_rejected(self):
        v=self.f.json(self.f.rows['reproduction-execution']);v['builds']['Debug']['receiptSha256']='0'*64;self.f.add('reproduction-execution',v,role=True)
        with self.assertRaises(ValueError):h.validate_reproduction(self.f.store(),self.f.builds['reproduction'])
    def test_compiler_graph_cannot_be_unarchived(self):
        del self.f.rows['candidate-On-Debug-graph']
        with self.assertRaises(h.EvidenceUnavailable):h.validate_provenance_closure(self.f.store(),self.f.builds['candidate'])
    def test_external_json_cannot_be_excused_as_binary(self):
        s=self.f.selection();s['notPackaged']=[{'rawPath':'/missing/raw.json','sha256':'0'*64,'sizeBytes':1,'reason':'test','artifactClass':'NativeBinary'}]
        with self.assertRaisesRegex(ValueError,'proof text'):h.Store(s)
    def test_index_and_archive_round_trip(self):
        selection=self.root/'selection.json';selection.write_text(json.dumps(self.f.selection()));out=self.root/'package'
        r=h.package(selection,out);self.assertEqual('IntegrityVerified',r['status']);self.assertFalse(r['M08Passed']);self.assertEqual(len(self.f.rows),r['members'])
    def test_archive_digest_mismatch(self):
        selection=self.root/'selection.json';selection.write_text(json.dumps(self.f.selection()));out=self.root/'package';r=h.package(selection,out)
        with self.assertRaisesRegex(ValueError,'archive SHA'):h.audit_archive(out/'h1-successor-evidence.tar.gz',out/'evidence-index.json','0'*64,r['indexSha256'])
    def test_path_safety(self):
        for name in ('../x','/x','x/../y','x\\y','./x','x//y','.'):
            with self.subTest(name=name):self.assertFalse(h.safe_member(name))
        self.assertTrue(h.safe_member('files/a.bin'))
    def test_human_approval_is_never_inferred_from_package(self):
        self.f.roles['m07-full']='witness-runtime'
        with self.assertRaisesRegex(ValueError,'cannot alias'):h.validate_selection(self.f.selection())

if __name__ == '__main__': unittest.main()
