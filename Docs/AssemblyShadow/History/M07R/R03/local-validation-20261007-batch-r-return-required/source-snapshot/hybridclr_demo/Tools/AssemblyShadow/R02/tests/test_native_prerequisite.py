import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from evidence import binding, read
import native_prerequisite as prereq
import run_local


class NativePrerequisite(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name).resolve(); self.addCleanup(self.temp.cleanup)
        self.project = self.root/'demo'; self.project.mkdir()
        self.installed = self.project/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp'
        self.installed.mkdir(parents=True)
        self.unity = self.root/'Unity.app/Contents/MacOS/Unity'
        self.unity.parent.mkdir(parents=True); self.unity.write_text('fixture')
        self.graph = dict(result='Passed', projectPath=str(self.project), controlledPerformanceBuilds=True,
                          resourceBaselinePath=str(self.project/'_temp/AssemblyShadow/current-resources'))
        self.workflow = self.root/'workflow.json'; self.workflow.write_text(json.dumps(self.graph))
        self.graph_path = self.root/'candidate-graph.json'
        self.graph_path.write_text(json.dumps(dict(workflow=binding(self.workflow), graph=self.graph)))
        self.pins = dict(unityVersion='2022.3.62f2', target='StandaloneOSX', architecture='arm64')
        self.pins.update({k: dict(revision='a'*40) for k in ('demo','hybridclr','hybridclrUnity','il2cppPlus')})
        self.pinpath = self.project/'ProjectSettings/AssemblyShadowSourcePins.json'
        self.pinpath.parent.mkdir(); self.pinpath.write_text(json.dumps(self.pins))
        (self.installed/'assembly-shadow-install.json').write_text(json.dumps(dict(installMode='PinnedLocal',
            repositories={k:self.pins[k] for k in ('demo','hybridclr','hybridclrUnity','il2cppPlus')})))
        self.header = self.installed/'hybridclr/generated/UnityVersion.h'; self.header.parent.mkdir(parents=True)
        self.header.write_text('\n'.join('#define '+k+' '+v for k,v in prereq.VERSION.items()))
        self.fixture = Path(self.graph['resourceBaselinePath'])/'CompilerInputs/Assemblies/AssemblyA.Contracts.dll'
        self.fixture.parent.mkdir(parents=True); self.fixture.write_bytes(b'fixture')
        lib = self.unity.parent.parent/'PlaybackEngines/MacStandaloneSupport/baselib.a'
        lib.parent.mkdir(parents=True); lib.write_bytes(b'fixture')
        self.output = self.root/'inputs.json'

    def prepare(self):
        return prereq.prepare(self.project, self.graph_path, self.unity, self.output)

    def test_current_graph_and_generated_version_accepted(self):
        result = self.prepare(); prereq.recheck(result)
        self.assertEqual(result['files']['fixture']['path'], str(self.fixture))
        self.assertEqual(result['result'], 'Passed')

    def test_stub_header_fails_before_probe_with_diagnostic(self):
        self.header.write_text('#pragma once\n// ungenerated')
        with self.assertRaises(ValueError): self.prepare()
        result = read(self.output)
        self.assertEqual(result['result'], 'Failed'); self.assertIn('version', result['files'])
        self.assertIn('2022.3.62f2', result['error'])

    def test_foreign_version_or_duplicate_macro_rejected(self):
        text = self.header.read_text()
        for changed in (text.replace('20220362','20210362'),text+'\n#define HYBRIDCLR_UNITY_2022 1'):
            with self.assertRaises(ValueError): prereq.check_version(changed)

    def test_stale_installer_rejected(self):
        installed = self.installed/'assembly-shadow-install.json'; data=read(installed)
        data['repositories']['demo']['revision']='b'*40; installed.write_text(json.dumps(data))
        with self.assertRaises(ValueError): self.prepare()

    def test_changed_fixture_does_not_pass_recheck(self):
        result=self.prepare(); self.fixture.write_bytes(b'changed')
        with self.assertRaises(ValueError): prereq.recheck(result)

    def test_missing_fixture_not_replaced_with_historical_default(self):
        self.fixture.unlink()
        with self.assertRaises(ValueError): self.prepare()
        self.assertIn('Missing regular file', read(self.output)['error'])

    def test_failed_build_blocks_transaction_but_not_independent_kernels(self):
        batch=object.__new__(run_local.Batch); batch.out=self.root/'batch';batch.rows={};batch.values={}
        called=[]
        with contextlib.redirect_stdout(io.StringIO()):
            batch.cell('candidate-build',[],lambda:(_ for _ in ()).throw(ValueError('build failed')))
            batch.cell('native-regressions',[],lambda:called.append('four independent'))
            batch.cell('native-generated-inputs',['candidate-build'],lambda:called.append('prepare'))
            batch.cell('native-transaction',['native-generated-inputs'],lambda:called.append('compile'))
        self.assertEqual(called,['four independent'])
        self.assertEqual(batch.rows['native-transaction']['result'],'Blocked')
        source=Path(run_local.__file__).read_text()
        self.assertIn('"native-generated-inputs", ["candidate-build"]',source)
        self.assertIn('"native-transaction", ["native-generated-inputs"]',source)
        independent=source.split('def native_regressions(self):',1)[1].split('def native_generated_inputs',1)[0]
        self.assertNotIn('run-r01-transaction-native-tests.py',independent)


if __name__ == '__main__': unittest.main()
