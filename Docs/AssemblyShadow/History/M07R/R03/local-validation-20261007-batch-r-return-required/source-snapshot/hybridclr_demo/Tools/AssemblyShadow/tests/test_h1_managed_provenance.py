import json
import tempfile
import unittest
from pathlib import Path

import h1_managed_provenance as h

class ManagedProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name).resolve();self.root=self.base/'project';self.root.mkdir()
        (self.root/'Assets').mkdir();(self.root/'ProjectSettings').mkdir();(self.root/'Library/Bee').mkdir(parents=True)
        (self.root/'ProjectSettings/AssemblyShadowSourcePins.json').write_text('{}')
        (self.root/'dotnet').write_bytes(b'SYNTHETIC-HOST');(self.root/'csc.dll').write_bytes(b'SYNTHETIC-CSC')
        (self.root/'reference.dll').write_bytes(b'SYNTHETIC-REFERENCE')
        self.plan=[]
        for i,name in enumerate(sorted(h.REQUIRED_ASSEMBLIES)):
            source='Assets/source'+str(i)+'.cs';(self.root/source).write_text('class Fixture'+str(i)+' {}')
            self.plan.append({'name':name,'sourceFiles':[source],'defines':[],'referenceFiles':[]})
        self.evidence=self.base/'evidence'
        self.request={'projectRoot':str(self.root),'sourcePinFile':'ProjectSettings/AssemblyShadowSourcePins.json','buildId':'test-build','assemblies':self.plan}
    def tearDown(self):self.temp.cleanup()
    def run_capture(self,source_tamper=False,missing_graph=False):
        before=h.begin(self.request,self.evidence)
        if source_tamper:(self.root/self.plan[0]['sourceFiles'][0]).write_text('changed')
        nodes=[];actual=[]
        for i,a in enumerate(self.plan):
            compiler=self.root/('Library/Bee/raw/'+a['name']+'.dll');compiler.parent.mkdir(exist_ok=True,parents=True);compiler.write_bytes(('compiler'+str(i)).encode())
            transformed=self.root/('Library/Bee/ilpp/'+a['name']+'.dll');transformed.parent.mkdir(exist_ok=True,parents=True);transformed.write_bytes(('ILPP'+str(i)).encode())
            frozen=self.base/('inputs/'+a['name']+'.dll');frozen.parent.mkdir(exist_ok=True);frozen.write_bytes(transformed.read_bytes())
            nodes.extend([{'Annotation':'Csc '+a['name'],'Action':str(self.root/'dotnet')+' '+str(self.root/'csc.dll')+' /out:'+str(compiler)+' /reference:'+str(self.root/'reference.dll')+' '+a['sourceFiles'][0],
                'Inputs':[a['sourceFiles'][0]],'Outputs':[str(compiler)]},
                {'Annotation':'ILPP','Action':'ILPP','Inputs':[str(compiler)],'Outputs':[str(transformed)]}])
            actual.append({'name':a['name'],'sourcePath':str(transformed),'retainedPath':str(frozen),'sha256':h.digest(frozen)})
        if not missing_graph:(self.root/'Library/Bee/Player-managed.dag.json').write_text(json.dumps({'Nodes':nodes}))
        endreq={'buildId':'test-build','buildGuid':'a'*32,'inputSnapshotHash':'b'*64,'nativeLibrarySha256':'c'*64,'sourcePinSha256':before['sourcePinSha256'],'actualInputs':actual}
        return h.end(endreq,self.evidence)
    def test_captured_graph_is_not_automatically_passed(self):
        r=self.run_capture();self.assertFalse(r['sourceToBinaryVerified'])
        proof=h.verify(self.evidence/'h1-managed-source-capture.json')
        self.assertEqual('SourceGraphBound',proof['status']);self.assertFalse(proof['freshCompilerExecutionClaim'])
    def test_source_change_during_build_rejected(self):
        with self.assertRaisesRegex(ValueError,'changed during build'):self.run_capture(source_tamper=True)
    def test_missing_graph_stays_blocked(self):
        self.run_capture(missing_graph=True)
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):h.verify(self.evidence/'h1-managed-source-capture.json')
    def test_retained_source_tamper_rejected(self):
        self.run_capture();b=h.read_json(self.evidence/'begin.json');Path(b['sources'][0]['retainedPath']).write_text('bad')
        with self.assertRaisesRegex(ValueError,'bytes differ'):h.verify(self.evidence/'h1-managed-source-capture.json')
    def test_verifier_does_not_need_mutable_original_sources(self):
        self.run_capture()
        for a in self.plan:(self.root/a['sourceFiles'][0]).unlink()
        (self.root/'csc.dll').unlink();(self.root/'reference.dll').unlink()
        self.assertEqual('SourceGraphBound',h.verify(self.evidence/'h1-managed-source-capture.json')['status'])
    def test_new_root_required(self):
        h.begin(self.request,self.evidence)
        with self.assertRaises(ValueError):h.begin(self.request,self.evidence)
    def test_both_managed_domains_required(self):
        self.request['assemblies'].pop()
        with self.assertRaises(ValueError):h.begin(self.request,self.evidence)
    def test_reference_alias_supported(self):
        parsed=h.csc_arguments(str(self.root/'csc.dll')+' /out:out.dll /reference:global='+str(self.root/'reference.dll')+' Assets/source0.cs',self.root,{})
        self.assertIn(str(self.root/'reference.dll'),parsed['dependencyPaths'])
    def test_missing_response_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unretained'):h.csc_arguments(str(self.root/'csc.dll')+' @missing',self.root,{})
    def test_implicit_source_search_rejected(self):
        with self.assertRaisesRegex(ValueError,'Implicit'):h.csc_arguments(str(self.root/'csc.dll')+' /out:out.dll /recurse:*.cs Assets/source0.cs',self.root,{})
    def test_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):h.csc_arguments(str(self.root/'csc.dll')+' /out:out.dll Assets/source0.cs Assets/source0.cs',self.root,{})
    def test_irrelevant_action_is_not_a_compilation(self):
        self.assertIsNone(h.csc_arguments('/tool/other file',self.root,{}))


class ManagedExplicitReuseTests(unittest.TestCase):
    setUp = ManagedProvenanceTests.setUp
    tearDown = ManagedProvenanceTests.tearDown
    run_capture = ManagedProvenanceTests.run_capture
    """Same synthetic capture under a new native build, not another Csc execution."""
    def prior_and_current(self):
        self.run_capture()
        prior=self.evidence/'h1-managed-source-capture.json';proof=h.verify(prior)
        proof_path=self.base/'prior-proof.json';proof_path.write_text(json.dumps(proof))
        current=h.read_json(prior);current['buildGuid']='9'*32;current['nativeLibrarySha256']='8'*64
        current['graphs']=[]
        path=self.base/'current-capture.json';path.write_text(json.dumps(current))
        return path,proof_path
    def test_explicit_identical_reuse(self):
        path,proof=self.prior_and_current();r=h.verify_exact_reuse(path,proof)
        self.assertIn('reusedFrom',r);self.assertEqual('9'*32,r['buildGuid']);self.assertFalse(r['freshCompilerExecutionClaim'])
    def test_unproven_prior_cannot_be_reused(self):
        path,proof=self.prior_and_current();v=h.read_json(proof);v['status']='Captured';proof.write_text(json.dumps(v))
        with self.assertRaisesRegex(ValueError,'direct prior'):h.verify_exact_reuse(path,proof)
    def test_changed_source_pins_cannot_reuse(self):
        path,proof=self.prior_and_current();v=h.read_json(path);v['sourcePinSha256']='0'*64;path.write_text(json.dumps(v))
        with self.assertRaisesRegex(ValueError,'source pin'):h.verify_exact_reuse(path,proof)
    def test_reuse_without_direct_proof_is_not_implicit(self):
        path,proof=self.prior_and_current()
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):h.verify(path)
    def test_changed_player_input_cannot_reuse(self):
        path,proof=self.prior_and_current();v=h.read_json(path);row=v['actualInputs'][0]
        new=self.base/'new-dll';new.write_bytes(b'NEW');row.update(retainedPath=str(new),sha256=h.digest(new),sizeBytes=3)
        path.write_text(json.dumps(v))
        with self.assertRaisesRegex(ValueError,'Player DLLs differ'):h.verify_exact_reuse(path,proof)

if __name__ == '__main__': unittest.main()
