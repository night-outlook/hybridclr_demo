import copy
import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_early_capsule as capsule


def fixture():
    return dict(mode='Control',baselineBuildId='baseline',runtimeAbiHash='a'*64,patchId='P03',
        candidates=['A'],stableAotNames=['Bootstrap'],inputs=[dict(name='A',dllPath='/fixture/A.dll',
        dllLength=512,dllSha256='b'*64,pdbPath='',pdbLength=0,pdbSha256='')],
        ordinaryPath='',ordinarySha256='',prerequisiteFiles=[dict(path='/fixture/resources.json',length=7,sha256='c'*64)])


class CapsuleBoundaryTests(unittest.TestCase):
    def test_versioned_wire_and_absent_pdb_roundtrip(self):
        value=fixture();payload=capsule.encode(value)
        self.assertEqual(b'R01EARLY\x01\x00\x00\x00\x07\x00\x00\x00Control',payload[:23])
        self.assertEqual(value,capsule.decode(payload))
        ordinary=copy.deepcopy(value);ordinary.update(mode='OrdinaryFirst',ordinaryPath='/fixture/fixed.bytes',ordinarySha256=capsule.FIXED_IMAGE_SHA)
        self.assertEqual(ordinary,capsule.decode(capsule.encode(ordinary)))

    def test_truncated_payload_rejected_at_every_boundary(self):
        payload=capsule.encode(fixture())
        for end in range(len(payload)):
            with self.subTest(end=end),self.assertRaises((ValueError,RuntimeError)):
                capsule.decode(payload[:end])

    def test_version_length_utf8_and_trailing_rejections(self):
        payload=capsule.encode(fixture())
        mutations=[payload+b'\0',b'INVALID!'+payload[8:],payload[:8]+struct.pack('<i',2)+payload[12:],
            payload[:12]+struct.pack('<i',-1)+payload[16:],payload[:12]+struct.pack('<i',16385)+payload[16:],
            payload[:16]+b'\xff'+payload[17:],payload[:16]+b'\0'+payload[17:]]
        for mutated in mutations:
            with self.subTest(prefix=mutated[:24]),self.assertRaises((ValueError,RuntimeError)):
                capsule.decode(mutated)

    def test_identity_and_input_role_rejections(self):
        for mutate in [lambda d:d.update(candidates=['A','a']),lambda d:d.update(stableAotNames=['a']),
            lambda d:d['inputs'].append(copy.deepcopy(d['inputs'][0])),lambda d:d['inputs'][0].update(name='Outside'),
            lambda d:d['inputs'][0].update(dllLength=-1),lambda d:d['inputs'][0].update(pdbSha256='d'*64),
            lambda d:d.update(prerequisiteFiles=[]),lambda d:d.update(mode='OrdinaryFirst'),
            lambda d:d.update(ordinaryPath='/fixture/file',ordinarySha256=capsule.FIXED_IMAGE_SHA),
            lambda d:d.update(runtimeAbiHash='A'*64)]:
            data=fixture();mutate(data)
            with self.assertRaises((ValueError,RuntimeError)):capsule.encode(data)

    def test_immutable_output_and_file_digest_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory).resolve()/'capsule.bin';data=fixture();receipt=capsule.write_capsule(path,data)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),receipt['sha256'])
            with self.assertRaises(FileExistsError):capsule.write_capsule(path,data)
            self.assertEqual(receipt['sha256'],capsule._file(path,receipt['sha256'])['sha256'])
            path.write_bytes(path.read_bytes()+b'tamper')
            with self.assertRaises((ValueError,RuntimeError)):capsule._file(path,receipt['sha256'])

    def test_context_uses_load_order_and_catalog_bundle_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            def file(name, value=b'fixture'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value)
                return path
            baseline = file('baseline.json')
            patch_path = file('patch.json')
            player = file('player.json')
            fixture_path = file('fixtures.json')
            a, b = file('A.dll'), file('B.dll')
            bundle = file('ResourceInputs/custom-bundles/example.bundle')
            catalog = file('ResourceInputs/resource-build-receipt.json', json.dumps({
                'bundleDirectory': 'custom-bundles', 'bundles': [{'name': 'example.bundle'}]}).encode())
            patch = dict(patchId='P03', loadOrder=['B','A'], dllOnly=True, closure=[
                dict(name=name, dll=name+'.dll', sha256=capsule.digest(path), pdb='', pdbSha256='')
                for name,path in [('A',a),('B',b)]])
            context = dict(manifest=dict(baselineBuildId='baseline', runtimeAbiHash='a'*64,
                candidateNames=['A','B'], stableAotNames=['Bootstrap'], baselineManifestPath=str(baseline)),
                baseline=dict(resourceBaselinePath='ResourceInputs'), on=dict(path=player),
                fixtures={'P03':dict(patch=patch, root=root, path=patch_path)})
            data = capsule.from_context(context, 'Control', fixture_path=fixture_path)
            self.assertEqual(['B','A'], [row['name'] for row in data['inputs']])
            self.assertEqual({str(path) for path in [baseline, patch_path, player, fixture_path, bundle, catalog]},
                             {row['path'] for row in data['prerequisiteFiles']})
            self.assertEqual(data, capsule.decode(capsule.encode(data)))


if __name__=='__main__':unittest.main()
