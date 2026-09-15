import json,tempfile,unittest
from pathlib import Path
from unittest import mock
import h1_native_capture as n
class Tests(unittest.TestCase):
    def test_capture_retains_plan_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=root/'project'; (project/'Library/Bee').mkdir(parents=True); native=project/'Build/GameAssembly.dylib'; native.parent.mkdir(); native.write_bytes(b'n'); config=project/'config.h'; config.write_text('#define IL2CPP_DEBUG 1\n#define IL2CPP_DEVELOPMENT 0\n'); graph={'Nodes':[{'Annotation':'Copy','Inputs':[],'Outputs':[str(native)]}]}; (project/'Library/Bee/Player.dag.json').write_text(json.dumps(graph)); request={'projectRoot':str(project),'inputSnapshotHash':'1'*64,'nativeLibraryPath':str(native),'nativeLibrarySha256':n.digest(native),'sourcePinSha256':'2'*64,'before':{'entries':[]},'il2cppConfigPath':str(config),'featureEnabled':True,'cppConfiguration':'Debug','buildId':'H1Count-On-Debug','buildGuid':'g'}; out=root/'out'
            with mock.patch.object(n.pch,'has_pch',return_value=True),mock.patch.object(n.pch,'plan',side_effect=ValueError('boom')):
                with self.assertRaisesRegex(ValueError,'boom'): n.capture(request,out)
            self.assertTrue((out/'capture-failure.json').is_file()); self.assertTrue((out/'bee-action-graph.json').is_file()); self.assertFalse((out/'h1-compiler-provenance.json').exists())
if __name__=='__main__': unittest.main()
