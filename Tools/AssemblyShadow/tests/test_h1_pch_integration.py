"""Real tiny Clang PCH -> capture -> normal verifier and archive-owner tests.

The synthetic Bee graph and native marker are test data, not Unity evidence.
"""
import copy
import importlib.util
import json
import plistlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import h1_compiler_actions as a
import h1_native_capture as n
import h1_pch_provenance as p
import h1_selection_collect as collector
import h1_successor_evidence as e
from test_h1_pch_provenance import CONFIG, FLAGS, graph

TOOLS=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('strict_normal_entry',TOOLS/'verify-h1-compiler-provenance-strict.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
CLANG=shutil.which('clang')

@unittest.skipUnless(CLANG,'Actual Clang needed; absent is NotRun, not acceptance')
class CaptureIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        for sub in ('Assets','ProjectSettings','Library/Bee','sdk','run'): (self.root/sub).mkdir(parents=True,exist_ok=True)
        self.config=self.root/'il2cpp-config.h';self.config.write_text(CONFIG)
        (self.root/'p.h').write_text('#include "il2cpp-config.h"\n#define PCH_VALUE 7\n')
        (self.root/'u.c').write_text('int value=PCH_VALUE;\n')
        (self.root/'sdk/SDKSettings.plist').write_bytes(plistlib.dumps({'Version':'test-sdk'}))
        self.g=graph(self.root,CLANG)
        for row in self.g['Nodes']:row['Action']=row['Action'].replace('-isysroot /','-isysroot '+str(self.root/'sdk'))
        self.g['Nodes'][0]['Inputs'].append(str(self.root/'sdk/dummy'))
        for row in self.g['Nodes'][:2]:subprocess.run(a.split(row['Action']),cwd=self.root,check=True,capture_output=True)
        self.native=self.root/'GameAssembly.dylib';self.native.write_bytes(b'SYNTHETIC UNIT-TEST MARKER; NOT A PLAYER')
        self.path=self.root/'Library/Bee/Player-test.dag.json';self.path.write_text(json.dumps(self.g))
        request={'projectRoot':str(self.root),'nativeLibraryPath':str(self.native),'nativeLibrarySha256':n.digest(self.native),
                 'inputSnapshotHash':'b'*64,'sourcePinSha256':'c'*64,'before':{'entries':[]},'il2cppConfigPath':str(self.config),
                 'cppConfiguration':'Debug','featureEnabled':True,'buildId':'H1Count-On-Debug','buildGuid':'a'*32}
        self.request=request
        self.cp=n.capture(request,self.root/'run/compiler')
        self.cp_path=self.root/'run/compiler/capture.json'
        self.receipt=self.root/'run/build.json'
        self.build={'schemaVersion':1,'kind':'H1CountDiagnosticPlayerBuild','diagnosticOnly':True,'featureEnabled':True,
            'cppConfiguration':'Debug','baselineBuildId':'H1Count-On-Debug','nativeArguments':'-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1'}
        for key in p.BINDINGS:
            if key!='buildId':self.build[key]=self.cp[key]
        self.build['nativeLibraryPath']=str(self.native)
        self.persist()
    def tearDown(self):self.tmp.cleanup()
    def persist(self):
        self.cp_path.write_text(json.dumps(self.cp))
        self.build.update(compilerProvenance=self.cp,compilerProvenancePath=str(self.cp_path),compilerProvenanceSha256=n.digest(self.cp_path))
        self.receipt.write_text(json.dumps(self.build))
    def test_diagnostic_replay_cannot_substitute_for_fresh_build_proof(self):
        import h1_pch_diagnose as d
        path=self.root/'old-request.json';path.write_text(json.dumps(self.request))
        result=d.diagnose(path,self.path,self.root/'diagnostic')
        self.assertFalse(result['freshBuildClaim'])
        proof=p.read_json(result['proofPath'])
        binding=p.binding_from(self.cp,self.root,True,'Debug')
        with self.assertRaisesRegex(ValueError,'binding'):
            p.verify(proof,self.g,self.root,self.native,CONFIG,{},binding)
    def test_diagnostic_replay_rejects_changed_old_native(self):
        import h1_pch_diagnose as d
        path=self.root/'old-request.json';path.write_text(json.dumps(self.request))
        self.native.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'bytes differ'):d.diagnose(path,self.path,self.root/'diagnostic')
    def test_normal_strict_entry_verifies_capture(self):
        self.assertEqual('On/Debug',v.verify_receipt(self.receipt)['mode'])
    def test_pch_sdk_marker_bound_to_retained_sdk(self):
        proof=p.read_json(self.cp['pchProofPath']);marker=proof['producers'][0]['inputs'][-1]
        self.assertTrue(any(r['kind']=='bee-sdk-marker' for r in proof['producers'][0]['inputs']))
        v.verify_receipt(self.receipt)
    def test_native_capture_records_pch_pointer_hash(self):
        self.assertEqual(self.cp['pchProofSha256'],n.digest(Path(self.cp['pchProofPath'])))
    def test_normal_entry_rejects_missing_pch_pointer(self):
        self.cp['pchProofPath']='';self.cp['pchProofSha256']='';self.persist()
        with self.assertRaises((OSError,ValueError)):v.verify_receipt(self.receipt)
    def test_changed_raw_graph_rejected(self):
        Path(self.cp['beeActionGraphPath']).write_text('{}')
        with self.assertRaises(ValueError):v.verify_receipt(self.receipt)
    def test_changed_effective_macro_raw_output_rejected(self):
        proof=p.read_json(self.cp['pchProofPath'])
        Path(proof['groups'][0]['macros']['stdout']['retainedPath']).write_bytes(b'changed')
        with self.assertRaises(ValueError):v.verify_receipt(self.receipt)
    def test_selected_native_marker_tamper_rejected(self):
        self.native.write_bytes(b'changed')
        with self.assertRaises(ValueError):v.verify_receipt(self.receipt)
    def test_archive_owner_requires_every_pch_artifact(self):
        class Store:
            missing=None
            def ref(s,path,digest=None):
                if path==s.missing:raise e.EvidenceUnavailable(path)
                raw=Path(path).read_bytes()
                if digest:self.assertEqual(digest,p.sha(raw))
                return {'localPath':path,'sha256':p.sha(raw),'sizeBytes':len(raw)}
            def json_row(s,row):return p.read_json(row['localPath'])
            def binary_ref(s,path,digest):return s.ref(path,digest)
        store=Store();e.validate_pch_closure(store,self.cp,self.build)
        store.missing=p.read_json(self.cp['pchProofPath'])['producers'][0]['pch']['retainedPath']
        with self.assertRaises(e.EvidenceUnavailable):e.validate_pch_closure(store,self.cp,self.build)
    def test_collector_finds_pch_sidecar_and_all_retained_inputs(self):
        self.assertIn((self.cp['pchProofPath'],self.cp['pchProofSha256']),list(collector.refs(self.cp)))
        proof=p.read_json(self.cp['pchProofPath'])
        refs=list(collector.refs(proof))
        row=proof['producers'][0]['pch'];self.assertIn((row['retainedPath'],row['sha256']),refs)
        header=proof['producers'][0]['headers'][0];self.assertIn((header['retainedPath'],header['sha256']),refs)
    def test_no_pch_optional_empty_references_not_collected(self):
        self.assertEqual([],list(collector.refs({'pchProofPath':'','pchProofSha256':''})))
    def test_half_empty_pch_reference_not_ignored(self):
        self.assertEqual([('', 'a'*64)],list(collector.refs({'pchProofPath':'','pchProofSha256':'a'*64})))

@unittest.skipUnless(CLANG,'Actual Clang needed')
class ProfileMatrixTests(unittest.TestCase):
    def exercise(self,cpp,feature,release):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();(root/'il2cpp-config.h').write_text(CONFIG)
            (root/'p.h').write_text('#include "il2cpp-config.h"\n#define PCH_VALUE 7\n')
            source='u.cpp' if cpp else 'u.c';(root/source).write_text('int value=PCH_VALUE;\n')
            g=graph(root,CLANG)
            for row in g['Nodes']:
                row['Action']=row['Action'].replace('-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1','-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+str(int(feature)))
                if release:row['Action']=row['Action'].replace('-DIL2CPP_DEBUG=1','-DIL2CPP_DEBUG=0 -DNDEBUG=0')
                if cpp:row['Action']=row['Action'].replace('-x c-header','-x c++-header').replace('u.c','u.cpp');row['Inputs']=[x.replace('u.c','u.cpp') for x in row.get('Inputs',[])]
            for row in g['Nodes'][:2]:subprocess.run(a.split(row['Action']),cwd=root,capture_output=True,check=True)
            binding={'featureEnabled':feature,'cppConfiguration':'Release' if release else 'Debug'}
            blueprint=p.plan(g,root,root/'GameAssembly.dylib',CONFIG,{},feature)
            proof=p.capture(blueprint,g,root,str(root/'il2cpp-config.h'),binding,root/'proof')
            p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},binding)
    def test_c_on_debug(self):self.exercise(False,True,False)
    def test_c_off_debug(self):self.exercise(False,False,False)
    def test_c_on_release_ndebug_zero_is_defined(self):self.exercise(False,True,True)
    def test_c_off_release(self):self.exercise(False,False,True)
    def test_cpp_on_debug(self):self.exercise(True,True,False)
    def test_cpp_off_debug(self):self.exercise(True,False,False)
    def test_cpp_on_release(self):self.exercise(True,True,True)
    def test_cpp_off_release(self):self.exercise(True,False,True)

if __name__=='__main__':unittest.main()
