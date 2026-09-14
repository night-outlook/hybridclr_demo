import hashlib
import json
import plistlib
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import h1_native_capture as h

CONFIG = '#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'

class NativeCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name).resolve()
        (self.root/'Library/Bee').mkdir(parents=True)
        self.compiler=self.root/'tool/clang++'; self.compiler.parent.mkdir();self.compiler.write_bytes(b'SYNTHETIC-COMPILER-NOT-EXECUTED')
        self.sdk=self.root/'sdk';self.sdk.mkdir();(self.sdk/'SDKSettings.plist').write_bytes(plistlib.dumps({'Version':'test-sdk'}))
        self.native=self.root/'Build/GameAssembly.dylib';self.native.parent.mkdir();self.native.write_bytes(b'SYNTHETIC-NATIVE-NOT-EXECUTED')
        self.config=self.root/'il2cpp-config.h';self.config.write_text(CONFIG)
        self.graph={'Nodes':[{'Annotation':'C_Mac_arm64', 'Action':str(self.compiler)+' -isysroot '+str(self.sdk)+' @flags.rsp -c sample.cpp', 'Outputs':['sample.o']},
            {'Annotation':'Link_Mac_arm64','Action':str(self.compiler)+' -isysroot '+str(self.sdk),'Inputs':['sample.o'],'Outputs':['Library/GameAssembly.dylib']},
            {'Annotation':'Copy','Inputs':['Library/GameAssembly.dylib'],'Outputs':[str(self.native)]}]}
        (self.root/'flags.rsp').write_text('@nested.rsp')
        (self.root/'nested.rsp').write_text('-DIL2CPP_DEBUG=1 -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1')
        self.graph_path=self.root/'Library/Bee/Player-test.dag.json';self.graph_path.write_text(json.dumps(self.graph))
        self.request={'projectRoot':str(self.root),'before':{'entries':[]}, 'buildId':'H1Count-On-Debug','buildGuid':'a'*32,
            'inputSnapshotHash':'b'*64,'nativeLibraryPath':str(self.native),'nativeLibrarySha256':h.digest(self.native),
            'sourcePinSha256':'c'*64,'il2cppConfigPath':str(self.config),'cppConfiguration':'Debug','featureEnabled':True}
    def tearDown(self): self.temp.cleanup()
    def capture(self):
        with patch.object(h.subprocess,'run',return_value=SimpleNamespace(stdout='test compiler\n',stderr='')):
            return h.capture(self.request,self.root/'evidence')
    def test_recursive_responses_and_immutable_config(self):
        value=self.capture();self.assertEqual(2,len(value['responseFiles']))
        self.assertEqual('test-sdk',value['sdkVersion'])
        self.config.write_text('changed for next build')
        self.assertEqual(CONFIG,Path(value['il2cppConfigPath']).read_text())
    def test_old_dag_is_not_fresh(self):
        self.request['before']['entries']=[{'path':str(self.graph_path),'sha256':h.digest(self.graph_path)}]
        with self.assertRaisesRegex(ValueError,'changed'): self.capture()
    def test_multiple_selected_graphs_rejected(self):
        shutil.copyfile(self.graph_path,self.graph_path.with_name('Player-duplicate.dag.json'))
        with self.assertRaisesRegex(ValueError,'one changed'):self.capture()
    def test_wrong_macro_profile_rejected(self):
        self.request['cppConfiguration']='Release'
        with self.assertRaisesRegex(ValueError,'configuration'):self.capture()
    def test_wrong_feature_in_real_actions_rejected(self):
        self.request['featureEnabled']=False
        with self.assertRaisesRegex(ValueError,'actual compiler'):self.capture()
    def test_native_hash_tamper_rejected(self):
        self.native.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'hash differs'):self.capture()
    def test_no_overwrite(self):
        (self.root/'evidence').mkdir()
        with self.assertRaises(ValueError):self.capture()
    def test_sdk_metadata_not_default_xcrun(self):
        value=self.capture(); self.assertEqual('test-sdk',value['sdkVersion'])
        self.assertEqual(h.digest(self.sdk/'SDKSettings.plist'),value['sdkSettingsSha256'])

if __name__ == '__main__': unittest.main()
