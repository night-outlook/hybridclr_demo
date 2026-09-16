import json
import tempfile
import unittest
from pathlib import Path

import h1_managed_provenance as h


class ManagedBeeCacheProofTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name).resolve(); self.root=self.base/'project'; self.root.mkdir()
        (self.root/'Assets').mkdir(); (self.root/'ProjectSettings').mkdir(); (self.root/'Library/Bee').mkdir(parents=True)
        (self.root/'ProjectSettings/AssemblyShadowSourcePins.json').write_text('{"pin":1}')
        (self.root/'ProjectSettings/AssemblyShadowReflectionBindings.json').write_text('{}')
        (self.root/'Packages').mkdir(); (self.root/'Packages/manifest.json').write_text('{}'); (self.root/'Packages/packages-lock.json').write_text('{}')
        (self.root/'dotnet').write_bytes(b'DOTNET'); (self.root/'csc.dll').write_bytes(b'CSC'); (self.root/'reference.dll').write_bytes(b'REFERENCE-v1')
        self.plan=[]; self.paths={}; nodes=[]
        for i,name in enumerate(sorted(h.REQUIRED_ASSEMBLIES)):
            source='Assets/source%d.cs'%i; (self.root/source).write_text('class Fixture%d {}'%i)
            self.plan.append({'name':name,'sourceFiles':[source],'defines':['H1_PLAYER'],'referenceFiles':[str(self.root/'reference.dll')]})
            raw=self.root/('Library/Bee/raw/'+name+'.dll'); raw.parent.mkdir(parents=True,exist_ok=True); raw.write_bytes(('RAW-'+name).encode())
            ilpp=self.root/('Library/Bee/ilpp/'+name+'.dll'); ilpp.parent.mkdir(parents=True,exist_ok=True); ilpp.write_bytes(('ILPP-'+name).encode())
            self.paths[name]=(raw,ilpp)
            action='{} {} /out:{} /reference:{} /define:H1_PLAYER {}'.format(self.root/'dotnet',self.root/'csc.dll',raw,self.root/'reference.dll',source)
            nodes.append({'Annotation':'Csc '+name,'Action':action,'Inputs':[source,str(self.root/'reference.dll')],'Outputs':[str(raw)]})
            nodes.append({'Annotation':'ILPP '+name,'Action':'ILPP','Inputs':[str(raw)],'Outputs':[str(ilpp)]})
        self.graph={'Nodes':nodes}; self.graph_path=self.root/'Library/Bee/Player-managed.dag.json'; self.save_graph()
        self.evidence=self.base/'evidence'
        self.request={'projectRoot':str(self.root),'sourcePinFile':'ProjectSettings/AssemblyShadowSourcePins.json','buildId':'test-build',
                      'assemblies':self.plan,'extraScriptingDefines':['H1_PLAYER']}
    def tearDown(self): self.temp.cleanup()
    def save_graph(self): self.graph_path.write_text(json.dumps(self.graph,indent=2)+'\n')
    def begin(self): return h.begin(self.request,self.evidence)
    def end(self, overrides=None):
        before=h.read_json(self.evidence/'begin.json'); actual=[]
        for name in sorted(h.REQUIRED_ASSEMBLIES):
            source=self.paths[name][1]
            if overrides and name in overrides: source=overrides[name]
            frozen=self.base/('inputs/'+name+'.dll'); frozen.parent.mkdir(parents=True,exist_ok=True); frozen.write_bytes(Path(source).read_bytes())
            actual.append({'name':name,'sourcePath':str(source),'retainedPath':str(frozen),'sha256':h.digest(frozen)})
        req={'buildId':'test-build','buildGuid':'a'*32,'inputSnapshotHash':'b'*64,'nativeLibrarySha256':'c'*64,
             'sourcePinSha256':before['sourcePinSha256'],'actualInputs':actual}
        return h.end(req,self.evidence)
    def proof(self): return h.verify(self.evidence/'h1-managed-source-capture.json')
    def test_unchanged_bee_cache_is_bound_to_fresh_player_inputs(self):
        b=self.begin(); self.assertEqual(2,sum(len(g['compilations']) for g in b['cacheGraphs']))
        self.end(); r=self.proof()
        self.assertEqual({'BeeCacheHitBoundToFreshPlayerInput'},{x['evidenceMode'] for x in r['rows']})
        self.assertFalse(r['freshCompilerExecutionClaim'])
    def test_stale_cached_output_is_rejected(self):
        self.begin(); name=sorted(h.REQUIRED_ASSEMBLIES)[0]; self.paths[name][1].write_bytes(b'STALE-OR-CHANGED')
        self.end()
        with self.assertRaisesRegex(ValueError,'changed|Missing'): self.proof()
    def test_ambiguous_cached_actions_are_rejected(self):
        name=sorted(h.REQUIRED_ASSEMBLIES)[0]; source=self.plan[0]['sourceFiles'][0]
        raw2=self.root/'Library/Bee/raw/duplicate.dll'; raw2.write_bytes(b'DUP-RAW'); target=self.paths[name][1]
        action='{} {} /out:{} /reference:{} /define:H1_PLAYER {}'.format(self.root/'dotnet',self.root/'csc.dll',raw2,self.root/'reference.dll',source)
        self.graph['Nodes'].insert(0,{'Annotation':'Csc duplicate','Action':action,'Inputs':[source,str(self.root/'reference.dll')],'Outputs':[str(raw2)]})
        self.graph['Nodes'].insert(1,{'Annotation':'ILPP duplicate','Action':'ILPP','Inputs':[str(raw2)],'Outputs':[str(target)]})
        self.save_graph(); self.begin(); self.end()
        with self.assertRaisesRegex(ValueError,'ambiguous managed action chain'): self.proof()
    def test_changed_source_is_rejected_before_cache_acceptance(self):
        self.begin(); (self.root/self.plan[0]['sourceFiles'][0]).write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed during build'): self.end()
    def test_changed_response_file_is_rejected(self):
        rsp=self.root/'flags.rsp'; rsp.write_text('/reference:'+str(self.root/'reference.dll'))
        for node in self.graph['Nodes']:
            if str(node.get('Annotation','')).startswith('Csc '):
                node['Action']=node['Action'].replace(' /reference:'+str(self.root/'reference.dll'),' @'+str(rsp))
        self.save_graph(); self.begin(); rsp.write_text('/reference:'+str(self.root/'reference.dll')+'\n/define:CHANGED')
        self.end()
        with self.assertRaisesRegex(ValueError,'response.*changed|Missing'): self.proof()
    def test_changed_dependency_is_rejected(self):
        self.begin(); (self.root/'reference.dll').write_bytes(b'REFERENCE-v2'); self.end()
        with self.assertRaisesRegex(ValueError,'dependency.*changed|Missing'): self.proof()
    def test_wrong_fresh_player_binding_is_rejected_even_with_identical_bytes(self):
        self.begin(); name=sorted(h.REQUIRED_ASSEMBLIES)[0]; wrong=self.root/'Library/Bee/unrelated/'+name+'.dll'
        wrong.parent.mkdir(parents=True); wrong.write_bytes(self.paths[name][1].read_bytes()); self.end({name:wrong})
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous managed action chain'): self.proof()
    def test_output_missing_at_begin_cannot_be_retroactively_proved(self):
        name=sorted(h.REQUIRED_ASSEMBLIES)[0]; target=self.paths[name][1]; saved=target.read_bytes(); target.unlink()
        self.begin(); target.write_bytes(saved); self.end()
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous managed action chain'): self.proof()


if __name__=='__main__': unittest.main()
