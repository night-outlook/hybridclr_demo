import hashlib
import unittest

import h1_successor_sidecar as sidecar
import h1_witness_contract as witness
from test_h1_successor_evidence import Fixture
import tempfile
from pathlib import Path


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.fixture=Fixture(self.root/'artifacts')
    def tearDown(self):self.temp.cleanup()
    def test_managed_capture_is_paired_in_memory_without_rewriting_build_receipt(self):
        store=self.fixture.store();rows=sidecar.selected_builds(store,'candidate-count-builds','candidate-source-pins',('On/Debug','On/Release','Off/Debug','Off/Release'))
        self.assertIn('managedSourceProvenancePath',rows['On/Debug'][1])
        original=self.fixture.json(self.fixture.builds['candidate']['On/Debug'][0])
        self.assertNotIn('managedSourceProvenancePath',original)
    def test_dedicated_witness_probe_contract(self):
        config='f'*64
        value={'schemaVersion':1,'kind':'H1WitnessGuardRuntimeProbe','result':'Passed','il2cpp':True,
            'configurationSha256':config,'configurationHash':'e'*64,
            'guardName':'__AssemblyShadowReflectionBinding_'+'e'*64+'_'+hashlib.sha256(witness.SITE_ID.encode()).hexdigest(),
            'imageSha256':witness.IMAGE_SHA256,'tamperRejected':True,'nullRejected':True,'callerBytesUnchanged':True,
            'assemblyResolveEvents':0,'humanGatePassed':False,'mayEnterR02':False}
        sidecar.witness_probe(value,config)
    def test_witness_probe_cannot_open_r02(self):
        config='f'*64
        value={'schemaVersion':1,'kind':'H1WitnessGuardRuntimeProbe','result':'Passed','il2cpp':True,
            'configurationSha256':config,'configurationHash':'e'*64,
            'guardName':'__AssemblyShadowReflectionBinding_'+'e'*64+'_'+hashlib.sha256(witness.SITE_ID.encode()).hexdigest(),
            'imageSha256':witness.IMAGE_SHA256,'tamperRejected':True,'nullRejected':True,'callerBytesUnchanged':True,
            'assemblyResolveEvents':0,'humanGatePassed':False,'mayEnterR02':True}
        with self.assertRaises(ValueError):sidecar.witness_probe(value,config)

if __name__=='__main__':unittest.main()
