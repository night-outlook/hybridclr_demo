"""Exercise the lazy Player ledger acceptance boundary independently of Unity."""
import ast
import copy
import importlib.util
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
