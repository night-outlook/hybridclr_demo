import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from evidence import EvidenceError, binding
import ordinary_input as ordinary


class OrdinaryInput(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.addCleanup(self.temp.cleanup)
        self.output=self.root/'_temp/AssemblyShadow/prepared'
        self.data=b'M00 test fixture; not real Player evidence'
        self.sha=hashlib.sha256(self.data).hexdigest()
        self.patch=patch.object(ordinary,'IMAGE_SHA256',self.sha);self.patch.start();self.addCleanup(self.patch.stop)
        source=self.root/ordinary.SOURCE;source.mkdir(parents=True)
        (source/'Entry.cs').write_text('fixture');(source/'Fixture.asmdef').write_text('{}')
        pins=self.root/'ProjectSettings/AssemblyShadowSourcePins.json';pins.parent.mkdir();pins.write_text('{}')
        self.receipt=dict(kind='R02OrdinaryInputPreparation',schemaVersion=1,result='Passed',projectRoot=str(self.root),
            outputRoot=str(self.output),unityVersion='2022.3.62f2',target='StandaloneOSX',development=True,
            classification='CurrentWorkspaceCompilerOutput',freshCscExecutionClaimed=False,runtimeAcceptance=False,
            expectedSha256=self.sha,sourcePinsSha256=binding(pins)['sha256'],sources=[binding(p) for p in sorted(source.iterdir())])

    def emit(self):
        self.output.mkdir(parents=True)
        for key,path in [('compiled',self.output/'compiled/AssemblyShadowBaseline.HotUpdate.dll'),('staged',self.root/ordinary.IMAGE_PATH)]:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(self.data);self.receipt[key]=binding(path)
        self.save()

    def save(self):
        (self.output/'preparation.json').write_text(json.dumps(self.receipt))

    def test_generated_input_bound_to_own_workspace(self):
        ordinary.preflight(self.root,self.output);self.emit()
        self.assertEqual(ordinary.verify(self.root,self.output)['result'],'Passed')

    def test_wrong_contract_or_workspace_or_mode_rejected(self):
        self.emit();original=copy.deepcopy(self.receipt)
        for key,value in [('projectRoot','/other'),('outputRoot','/other'),('expectedSha256','f'*64),
                          ('target','Android'),('unityVersion','other'),('development',False),
                          ('result','Failed'),('runtimeAcceptance',True),('freshCscExecutionClaimed',True),
                          ('sourcePinsSha256','e'*64)]:
            with self.subTest(field=key):
                self.receipt=copy.deepcopy(original);self.receipt[key]=value;self.save()
                with self.assertRaises(EvidenceError):ordinary.verify(self.root,self.output)

    def test_missing_and_duplicate_source_rejected(self):
        self.emit();original=copy.deepcopy(self.receipt)
        for rows in ([],original['sources'][:1],original['sources']+[original['sources'][0]]):
            self.receipt=copy.deepcopy(original);self.receipt['sources']=rows;self.save()
            with self.assertRaises(EvidenceError):ordinary.verify(self.root,self.output)

    def test_mutated_compiler_output_not_accepted(self):
        self.emit();Path(self.receipt['compiled']['path']).write_bytes(b'changed')
        with self.assertRaises(EvidenceError):ordinary.verify(self.root,self.output)

    def test_changed_source_not_accepted(self):
        self.emit();Path(self.receipt['sources'][0]['path']).write_bytes(b'changed')
        with self.assertRaises(EvidenceError):ordinary.verify(self.root,self.output)

    def test_preflight_never_overwrites_existing_wrong_bytes(self):
        dest=self.root/ordinary.IMAGE_PATH;dest.parent.mkdir(parents=True);dest.write_bytes(b'old')
        with self.assertRaises(EvidenceError):ordinary.preflight(self.root,self.output)
        self.assertEqual(dest.read_bytes(),b'old');self.assertFalse(self.output.exists())

    def test_existing_matching_bytes_do_not_skip_new_generation(self):
        dest=self.root/ordinary.IMAGE_PATH;dest.parent.mkdir(parents=True);dest.write_bytes(self.data)
        ordinary.preflight(self.root,self.output)
        with self.assertRaises(EvidenceError):ordinary.verify(self.root,self.output)

    def test_linked_destination_is_rejected_before_unity(self):
        dest=self.root/ordinary.IMAGE_PATH;dest.parent.mkdir(parents=True)
        source=self.root/'foreign';source.write_bytes(self.data);dest.symlink_to(source)
        with self.assertRaises(EvidenceError):ordinary.preflight(self.root,self.output)

    def test_reused_output_is_rejected(self):
        self.output.mkdir(parents=True)
        with self.assertRaises(EvidenceError):ordinary.preflight(self.root,self.output)

    def test_generation_source_preserves_contract_and_avoids_configure(self):
        path=Path(__file__).resolve().parents[4]/'Assets/AssemblyShadowBaseline/Editor/R02OrdinaryInput.cs'
        text=path.read_text()
        self.assertIn('CompileDllCommand.CompileDll(compiledRoot, EditorUserBuildSettings.activeBuildTarget, true)',text)
        self.assertIn('9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27',text)
        self.assertNotIn('BaselineBuild.Configure()',text)
        self.assertNotIn('PrebuildCommand.GenerateAll()',text)
        self.assertIn('FileMode.CreateNew',text)


if __name__=='__main__':unittest.main()
