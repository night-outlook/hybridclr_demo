import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import h1_reproduction_tooling as r
import h1_count_build_batch_tooling as wrapper
import shadow_tools as s


class ToolingTreeContractTests(unittest.TestCase):
    def test_exact_tooling_delta(self):
        base={'Assets/runtime.cs':'1'*40,'Tools/AssemblyShadow/tool.py':'2'*40}
        current=dict(base);current['Tools/AssemblyShadow/tool.py']='3'*40
        self.assertEqual({'Tools/AssemblyShadow/tool.py'},r.verify_tree_contract(base,current,{'Tools/AssemblyShadow/tool.py':'3'*40}))
    def test_extra_runtime_delta_rejected(self):
        base={'Assets/runtime.cs':'1'*40,'Tools/AssemblyShadow/tool.py':'2'*40}
        current={'Assets/runtime.cs':'4'*40,'Tools/AssemblyShadow/tool.py':'3'*40}
        with self.assertRaisesRegex(RuntimeError,'non-tooling'):
            r.verify_tree_contract(base,current,{'Tools/AssemblyShadow/tool.py':'3'*40})
    def test_wrong_tool_blob_rejected(self):
        base={'Tools/AssemblyShadow/tool.py':'2'*40};current={'Tools/AssemblyShadow/tool.py':'3'*40}
        with self.assertRaisesRegex(RuntimeError,'blob differs'):
            r.verify_tree_contract(base,current,{'Tools/AssemblyShadow/tool.py':'4'*40})
    def test_non_validation_allowlist_path_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'allowlist'):
            r.verify_tree_contract({'Assets/runtime.cs':'1'*40},{'Assets/runtime.cs':'2'*40},{'Assets/runtime.cs':'2'*40})


class RealGitSplitIdentityTests(unittest.TestCase):
    def git(self,root,*args):
        return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
    def init(self,root,branch):
        root.mkdir();self.git(root,'init','-q');self.git(root,'config','user.name','Fixture');self.git(root,'config','user.email','fixture@example.invalid')
        self.git(root,'checkout','-qb',branch);self.git(root,'remote','add','origin','https://github.com/night-outlook/hybridclr_demo.git')
    def commit(self,root,message):
        self.git(root,'add','.');self.git(root,'commit','-qm',message);return self.git(root,'rev-parse','HEAD')
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();base=Path(self.tmp.name).resolve()
        self.authority=base/'candidate';self.repro=base/'repro';self.tool='Tools/AssemblyShadow/tool.py'
        runtime={k:{'url':'https://github.com/night-outlook/'+k,'revision':'a'*40,'localPath':'../'+k} for k in ('hybridclr','hybridclrUnity','il2cppPlus')}
        self.runtime=runtime

        self.init(self.authority,'codex/assembly-shadow-r01b-h1')
        p=self.authority/self.tool;p.parent.mkdir(parents=True);p.write_text('reviewed-tool\n')
        self.candidate_anchor=self.commit(self.authority,'candidate tool anchor')
        self.candidate_blob=self.git(self.authority,'rev-parse',self.candidate_anchor+':'+self.tool)

        self.init(self.repro,'codex/assembly-shadow-h1-count-repro')
        (self.repro/'Assets').mkdir();(self.repro/'Assets/runtime.cs').write_text('// unfixed runtime\n')
        old=self.repro/self.tool;old.parent.mkdir(parents=True);old.write_text('old-tool\n')
        (self.repro/'ProjectSettings').mkdir()
        pins={'schemaVersion':1,'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',**runtime,
              'demo':{'url':'https://github.com/night-outlook/hybridclr_demo','revision':'0'*40,'localPath':'.'}}
        (self.repro/s.PINS).write_text(json.dumps(pins))
        self.behavior=self.commit(self.repro,'unfixed behavior source')
        pins['demo']['revision']=self.behavior;(self.repro/s.PINS).write_text(json.dumps(pins))
        self.protected=self.commit(self.repro,'metadata-only protected source pin')
        self.assertEqual(self.behavior,pins['demo']['revision'])
        self.git(self.repro,'checkout','-qb','codex/assembly-shadow-h1-count-repro-tooling')
        (self.repro/self.tool).write_text('reviewed-tool\n')
        self.tooling=self.commit(self.repro,'tooling successor')
        self.tooling_blob=self.git(self.repro,'rev-parse',self.tooling+':'+self.tool)
        self.assertEqual(self.candidate_blob,self.tooling_blob)

        targets={'schemaVersion':1,'kind':'PrimaryImplementationSourceTargets','unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',
                 'demoTargets':{'reproduction':{'repository':'night-outlook/hybridclr_demo','branch':'codex/assembly-shadow-h1-count-repro',
                    'publishedHead':self.protected,'codeCommit':self.behavior,'runtimePins':runtime,
                    'validationTooling':{'branch':'codex/assembly-shadow-h1-count-repro-tooling','revision':self.tooling,
                        'candidateToolSourceAnchor':self.candidate_anchor,'files':{self.tool:self.candidate_blob}}}}}
        target=self.authority/r.TARGETS;target.parent.mkdir(parents=True);target.write_text(json.dumps(targets));self.commit(self.authority,'tooling authority')
    def tearDown(self):self.tmp.cleanup()
    def test_full_split_identity_preflight(self):
        proof=r.verify(self.repro,self.authority)
        self.assertEqual(self.behavior,proof['behaviorSourceCommit']);self.assertEqual(self.tooling,proof['validationToolingCommit'])
        self.assertFalse(proof['humanGatePassed'])
    def test_dirty_tool_bytes_rejected(self):
        (self.repro/self.tool).write_text('tampered\n')
        with self.assertRaisesRegex(RuntimeError,'Working bytes'):
            r.verify(self.repro,self.authority)
    def test_candidate_source_blob_must_match_tooling_blob(self):
        targets=json.loads((self.authority/r.TARGETS).read_text());targets['demoTargets']['reproduction']['validationTooling']['files'][self.tool]='f'*40
        (self.authority/r.TARGETS).write_text(json.dumps(targets));self.commit(self.authority,'wrong blob authority')
        with self.assertRaisesRegex(RuntimeError,'blob differs|candidate source'):
            r.verify(self.repro,self.authority)


class WrapperTests(unittest.TestCase):
    def test_reproduction_install_check_follows_tooling_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();(root/'ProjectSettings').mkdir();(root/wrapper.base.SETTINGS).write_text('  additionalIl2CppArgs: -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\n')
            (root/s.PINS).write_text('{}')
            proof={'behaviorSourceCommit':'b'*40,'validationToolingCommit':'c'*40}
            def git(path,*args): return b'd'*40
            with patch.object(wrapper.repro_tools,'verify',return_value=proof) as preflight,patch.object(s,'read_json',return_value={}),patch.object(s,'git',side_effect=git),patch.object(s,'verify',return_value={'demoSourceVerified':False}) as installed:
                row=wrapper.inspect_project(root,'reproduction')
            preflight.assert_called_once_with(root,wrapper.AUTHORITY_PROJECT)
            installed.assert_called_once_with(root,demo_source=False,expected_shadow='on')
            self.assertEqual('c'*40,row['validationToolingCommit'])
    def test_candidate_path_delegates_unchanged(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(wrapper,'_ORIGINAL_INSPECT',return_value={'candidate':True}) as original:
            root=Path(temp).resolve();self.assertEqual({'candidate':True},wrapper.inspect_project(root,'candidate'));original.assert_called_once_with(root,'candidate')


if __name__=='__main__':unittest.main()
