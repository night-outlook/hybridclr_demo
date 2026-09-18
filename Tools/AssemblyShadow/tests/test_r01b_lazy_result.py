"""Exercise the lazy Player ledger acceptance boundary independently of Unity."""
import ast
import copy
import json
import importlib.util
from pathlib import Path
from unittest.mock import patch
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('r01b_lazy_runner', TOOLS / 'run-r01b-lazy-player.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class LazyResultLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dll = Path(self.temp.name) / 'lazy.dll'
        self.dll.write_bytes(b'fixture bytes; PE admission is tested separately')
        self.result_path = Path(self.temp.name) / 'result.json'
        self.expected = dict(buildGuid='diagnostic-guid', baselineBuildId='baseline', runtimeAbiHash='abi')
        self.fixture = {'assembly': dict(sha256=runner.digest(self.dll), name='Lazy', fullName='Lazy, Version=1.0.0.1')}
        self.dense = {'fixtures': [{}, {}]}
        # Discover the declared check inventory, while independently exercising the
        # ledger transition and provenance predicates below.
        tree = ast.parse((TOOLS / 'run-r01b-lazy-player.py').read_text())
        required = next(ast.literal_eval(node.value) for node in ast.walk(tree)
                        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'required_checks' for t in node.targets))
        phases = ['before-load', 'after-load', 'after-generics', 'after-arrays', 'after-interfaces',
                  'after-valid-attribute', 'after-failed-attribute-1', 'after-failed-attribute-2',
                  'after-malformed-attribute-1', 'after-malformed-attribute-2', 'after-dense-adjunct']
        snapshots = []
        for index, phase in enumerate(phases):
            count = 0 if index == 0 else 3 if index == len(phases)-1 else 1
            snapshots.append(dict(phase=phase, reservedPages=count*10, mappedPages=count*5,
                                  lifetimeReservedImageCount=count, remainingImageCount=8192-count,
                                  ordinaryAllocatedCount=count, shadowAllocatedCount=0,
                                  reservedShadowImageCount=0, aggregateInputDllBytes=count*100))
        self.result = dict(self.expected, schemaVersion=1, processId=123, passedChecks=len(required),
                           failedAttributeAttempts=2, malformedAttributeAttempts=2, malformedConstructorCalls=0,
                           denseFixtures=2, denseBoundaryChecks=4, fixtureBytes=self.dll.stat().st_size,
                           kind='R01BLazyPlayerResult', milestone='R01B', result='Passed', error='',
                           unityVersion='2022.3.62f2', platform='OSXPlayer', resultPath=str(self.result_path),
                           fixturePath=str(self.dll), fixtureSha256=self.fixture['assembly']['sha256'],
                           assemblyName='Lazy', assemblyFullName=self.fixture['assembly']['fullName'], il2cpp=True,
                           checks=[dict(name=n, detail='', passed=True) for n in sorted(required)],
                           capacitySnapshots=snapshots, retryExceptions=['exception']*4)

    def verify(self, value):
        runner.verify_result(value, self.result_path, 123, self.expected, self.fixture, self.dll,
                             Path(self.temp.name)/'dense.json', self.dense, True)

    def test_accepts_one_load_stable_lazy_operations_then_two_dense_images(self):
        self.verify(self.result)

    def test_rejects_lazy_operation_allocating_an_extra_image(self):
        value = copy.deepcopy(self.result)
        row = value['capacitySnapshots'][4]
        row.update(lifetimeReservedImageCount=2, remainingImageCount=8190, ordinaryAllocatedCount=2)
        with self.assertRaises(Exception):
            self.verify(value)

    def test_accepts_distinct_repeated_reflection_observations(self):
        value = copy.deepcopy(self.result)
        for invocation in range(4):
            value['checks'].append(dict(name='method-present-LazyBox-Echo-' + str(invocation), detail='', passed=True))
        value['passedChecks'] = len(value['checks'])
        self.verify(value)

    def test_rejects_duplicate_reflection_observations(self):
        value = copy.deepcopy(self.result)
        value['checks'].extend([dict(name='method-present-LazyBox-Echo', detail='', passed=True)] * 2)
        value['passedChecks'] = len(value['checks'])
        with self.assertRaises(Exception):
            self.verify(value)

    def test_rejects_production_guid_substitution(self):
        value = copy.deepcopy(self.result)
        value['buildGuid'] = 'production-guid'
        with self.assertRaises(Exception):
            self.verify(value)


    def test_deterministic_dense_v2_manifest_is_admitted_and_normalized(self):
        root=Path(self.temp.name).resolve()/'dense-v2';root.mkdir()
        fixtures=root/'fixtures';fixtures.mkdir()
        rows=[]
        mvids={1:'00000000-0000-0000-0000-000000000001',2:'00000000-0000-0000-0000-000000000002'}
        for fixture_id in (1,2):
            path=fixtures/f'AssemblyShadow.Workload.I{fixture_id:04d}.dll'
            path.write_bytes((bytes([fixture_id])*4096).ljust(1024*1024,b'\0'))
            name=f'AssemblyShadow.Workload.I{fixture_id:04d}'
            rows.append(dict(id=fixture_id,name=name,file=path.name,path=str(path),sha256=runner.digest(path),
                sizeBytes=path.stat().st_size,mvid=mvids[fixture_id],
                fullName=name+', Version=1.0.0.'+str(fixture_id)+', Culture=neutral, PublicKeyToken=null',
                typeDefRows=4098,methodDefRows=4097,stringsHeapBytes=70000,typeDefRowBytes=18,methodDefRowBytes=16))
        mono=root/'mono';compiler=root/'mcs';cecil=root/'Mono.Cecil.dll'
        for path,payload in ((mono,b'mono'),(compiler,b'mcs'),(cecil,b'cecil')):path.write_bytes(payload)
        manifest=root/'workload-v3-dense-adjunct-v2.json'
        value=dict(schemaVersion=2,kind='R01BDenseAdjunctManifest',status='GeneratedDeterministicDenseV2',
            evidenceIdentity='replacement-fixtures-require-fresh-native-and-player-evidence',
            historicalEvidenceReused=False,fixtures=rows,
            shapeContract=dict(fixtureCount=2,sizeBytesEach=1024*1024,typeDefRows=4098,methodDefRows=4097,
                stringsHeapMinimumBytes=65536,purpose='boundary'),
            historicalSealedV1=[
                dict(id=1,sha256=runner.DENSE_V2_HISTORICAL[1],status='UnavailableDoNotRelabel'),
                dict(id=2,sha256=runner.DENSE_V2_HISTORICAL[2],status='UnavailableDoNotRelabel')],
            generator=dict(sourcePath=str(runner.DENSE_SOURCE),sourceSha256=runner.digest(runner.DENSE_SOURCE),
                launcherPath=str(runner.DENSE_LAUNCHER),launcherSha256=runner.digest(runner.DENSE_LAUNCHER),
                monoPath=str(mono),monoSha256=runner.digest(mono),monoVersion='fixture mono',
                compilerPath=str(compiler),compilerSha256=runner.digest(compiler),compilerVersion='fixture mcs',
                cecilPath=str(cecil),cecilSha256=runner.digest(cecil),
                compileCommand=[str(compiler),'-nologo','-target:exe','-out:'+str(root/'g.exe'),'-r:'+str(cecil),str(runner.DENSE_SOURCE)],
                generateCommands=[[str(mono),str(root/'g.exe'),str(root/f'I{fixture_id:04d}-run{run_index}.dll')]
                                  for fixture_id in (1,2) for run_index in (1,2)],
                inputsUnchanged=True,twoFreshRunsByteIdentical=True),
            createdAtUtc='2026-09-18T00:00:00Z')
        manifest.write_text(json.dumps(value))

        class FakeTables:
            def __init__(self,_data,_label):
                self.counts=[0]*64;self.counts[2]=4098;self.counts[6]=4097
                self.streams={'#Strings':b'x'*70000}
                self.widths=[[] for _ in range(64)];self.widths[2]=[18];self.widths[6]=[16]
            def type_inventory(self):return {'types':[{}]*4097}

        def fake_identity(path):
            fixture_id=1 if 'I0001' in Path(path).name else 2
            row=rows[fixture_id-1]
            return {'name':row['name'],'mvid':row['mvid'],'fullName':row['fullName']}

        with patch.object(runner,'MONO',mono),patch.object(runner,'COMPILER',compiler),patch.object(runner,'CECIL',cecil),\
             patch.object(runner,'read_identity',side_effect=fake_identity),patch.object(runner,'CliTables',FakeTables):
            normalized,inputs=runner.verify_dense_manifest(manifest)
        self.assertEqual(2,normalized['schemaVersion'])
        self.assertEqual('GeneratedDeterministicDenseV2',normalized['status'])
        self.assertEqual([1,2],[row['id'] for row in normalized['fixtures']])
        self.assertIn(manifest,inputs)
        self.assertTrue(all(Path(row['path']) in inputs for row in normalized['fixtures']))

    def test_deterministic_dense_v2_rejects_historical_relabel(self):
        root=Path(self.temp.name).resolve()/'dense-v2-relabel';root.mkdir()
        manifest=root/'workload-v3-dense-adjunct-v2.json'
        manifest.write_text(json.dumps(dict(schemaVersion=2,kind='R01BDenseAdjunctManifest',
            status='GeneratedDeterministicDenseV2',
            evidenceIdentity='replacement-fixtures-require-fresh-native-and-player-evidence',
            historicalEvidenceReused=True,fixtures=[],shapeContract={},historicalSealedV1=[],generator={},
            createdAtUtc='2026-09-18T00:00:00Z')))
        with self.assertRaises(Exception):
            runner.verify_dense_manifest(manifest)


if __name__ == '__main__':
    unittest.main()
