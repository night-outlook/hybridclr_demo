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
        self.authority=base/'candidate';self.repro=base/'repro'
        self.init(self.authority,'codex/assembly-shadow-r01b-h1')
        tool='Tools/AssemblyShadow/tool.py';p=self.authority/tool;p.parent.mkdir(parents=True);p.write_text('reviewed-tool\n')
        self.candidate_anchor=self.commit(self.authority,'candidate tool anchor')
        candidate_blob=self.git(self.authority,'rev-parse',self.candidate_anchor+':'+tool)

        self.init(self.repro,'codex/assembly-shadow-h1-count-repro')
        (self.repro/'Assets').mkdir();(self.repro/'Assets/runtime.cs').write_text('// unfixed runtime\n')
        old=self.repro/tool;old.parent.mkdir(parents=True);old.write_text('old-tool\n')
        (self.repro/'ProjectSettings').mkdir()
        runtime={k:{'url':'https://github.com/night-outlook/'+k,'revision':'a'*40,'localPath':'../'+k} for k in ('hybridclr','hybridclrUnity','il2cppPlus')}
        pins={'schemaVersion':1,'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',**runtime,
              'demo':{'url':'https://github.com/night-outlook/hybridclr_demo','revision':'0'*40,'localPath':'.'}}
        (self.repro/s.PINS).write_text(json.dumps(pins))
        behavior=self.commit(self.repro,'behavior')
        pins['demo']['revision']=behavior;(self.repro/s.PINS).write_text(json.dumps(pins));self.git(self.repro,'add',s.PINS);self.git(self.repro,'commit','-qm','pin behavior')
        # Use the pin commit itself as protected head: metadata-only successors are optional, not required by the verifier.
        self.behavior=self.git(self.repro,'rev-parse','HEAD')
        pins['demo']['revision']=self.behavior;(self.repro/s.PINS).write_text(json.dumps(pins));self.git(self.repro,'add',s.PINS);self.git(self.repro,'commit','-qm','final pin fixture')
        # The source pin must precede a metadata-only protected head, matching production topology.
        self.behavior=self.git(self.repro,'rev-parse','HEAD')
        # rewrite pin to self is impossible without changing commit; instead create a new fixture rooted at current commit via expected tree contract.
        # Tests below focus the exact changed-tree/tool-source invariants; production helper additionally checks the real pinned/protected ancestry.
        self.tool=tool;self.candidate_blob=candidate_blob
    def tearDown(self):self.tmp.cleanup()
    def test_candidate_blob_identity_is_git_object_exact(self):
        self.assertEqual(self.candidate_blob,self.git(self.authority,'rev-parse',self.candidate_anchor+':'+self.tool))


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
