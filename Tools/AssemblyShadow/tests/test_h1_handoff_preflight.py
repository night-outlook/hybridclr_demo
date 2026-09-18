"""Real disposable Git repositories; no fetch, external writes or Unity."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import h1_handoff_preflight as h

class LiveCommittedHandoffTests(unittest.TestCase):
    def test_actual_committed_candidate_handoff_passes_preflight(self):
        root=Path(__file__).resolve().parents[3]
        result=h.verify(root,'candidate')
        self.assertEqual('SourceTargetVerifiedNotBuildAccepted',result['status'])
        self.assertEqual('candidate',result['role'])
        self.assertEqual(self.git(root,'rev-parse','HEAD').strip(),result['checkoutCommit'])
        text=(root/h.WEB).read_text(encoding='utf-8')
        for section in h.REQUIRED_SECTIONS:
            self.assertIn(section,text)

    @staticmethod
    def git(root,*args):
        return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL,text=True)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        self.git('init','-q');self.git('config','user.name','Fixture');self.git('config','user.email','fixture@example.invalid')
        self.git('checkout','-qb','codex/assembly-shadow-r01b-h1')
        self.git('remote','add','origin','https://github.com/night-outlook/hybridclr_demo.git')
        (self.root/'ProjectSettings').mkdir();(self.root/'Assets').mkdir()
        (self.root/'Assets/fixture.cs').write_text('// synthetic source\n');self.commit()
        self.anchor=self.git('rev-parse','HEAD').strip()
        runtime={k:{'url':'https://github.com/night-outlook/'+k,'revision':'a'*40} for k in ('hybridclr','hybridclrUnity','il2cppPlus')}
        self.pins={'schemaVersion':1,'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',**runtime,
            'demo':{'url':'https://github.com/night-outlook/hybridclr_demo','revision':self.anchor,'localPath':'.'}}
        (self.root/h.s.PINS).write_text(json.dumps(self.pins))
        self.targets={'schemaVersion':1,'kind':'PrimaryImplementationSourceTargets','unityVersion':'2022.3.62f2',
            'target':'StandaloneOSX','architecture':'arm64','demoTargets':{'candidate':{'repository':'night-outlook/hybridclr_demo',
            'branch':'codex/assembly-shadow-r01b-h1','codeCommit':self.anchor,'runtimePins':runtime}}}
        (self.root/h.WEB).parent.mkdir(parents=True)
        (self.root/h.WEB).write_text('\n'.join(h.REQUIRED_SECTIONS))
        (self.root/h.TARGETS).write_text(json.dumps(self.targets));self.commit()
    def tearDown(self):self.tmp.cleanup()
    def git(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL,text=True)
    def commit(self):self.git('add','.');self.git('commit','-qm','fixture')
    def test_complete_committed_handoff(self):
        r=h.verify(self.root,'candidate');self.assertEqual(self.anchor,r['codeCommit']);self.assertFalse(r['humanGatePassed'])
    def test_absent_web_file_blocks(self):
        (self.root/h.WEB).unlink()
        with self.assertRaisesRegex(RuntimeError,'Missing'):h.verify(self.root,'candidate')
    def test_uncommitted_web_changes_block(self):
        (self.root/h.WEB).write_text('edited')
        with self.assertRaisesRegex(RuntimeError,'committed HEAD'):h.verify(self.root,'candidate')
    def test_source_change_after_anchor_blocks(self):
        (self.root/'Assets/fixture.cs').write_text('// changed');self.commit()
        with self.assertRaisesRegex(RuntimeError,'build-input'):h.verify(self.root,'candidate')
    def test_document_only_successor_allowed(self):
        (self.root/h.WEB).write_text((self.root/h.WEB).read_text()+'\nvalidated note');self.commit()
        h.verify(self.root,'candidate')
    def test_unrecognized_code_in_handoff_not_excluded(self):
        (self.root/'Docs/AssemblyShadow/Handoff/runner.py').write_text('pass');self.commit()
        with self.assertRaisesRegex(RuntimeError,'build-input'):h.verify(self.root,'candidate')
    def test_wrong_origin_blocks(self):
        self.git('remote','set-url','origin','https://github.com/other/demo')
        with self.assertRaisesRegex(RuntimeError,'origin'):h.verify(self.root,'candidate')
    def test_wrong_branch_blocks(self):
        self.git('checkout','-qb','other')
        with self.assertRaisesRegex(RuntimeError,'branch'):h.verify(self.root,'candidate')
    def test_pin_disagreement_blocks(self):
        self.pins['demo']['revision']='b'*40;(self.root/h.s.PINS).write_text(json.dumps(self.pins));self.commit()
        with self.assertRaisesRegex(RuntimeError,'source pin'):h.verify(self.root,'candidate')
    def test_missing_required_section_blocks(self):
        (self.root/h.WEB).write_text('## Objective');self.commit()
        with self.assertRaisesRegex(RuntimeError,'sections'):h.verify(self.root,'candidate')

if __name__=='__main__':unittest.main()
