import base64
import zlib
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from evidence import EvidenceError, read
import ordinary_input as ordinary

SOURCE_ROOT = Path(__file__).resolve().parents[4]


def setup_project(root):
    for name in (ordinary.FIXTURE, ordinary.ORIGIN):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE_ROOT / name, target)
    pins = root / ordinary.PINS
    pins.parent.mkdir(parents=True)
    pins.write_text('{}')
    return root


class OrdinaryInput(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = setup_project(Path(self.temp.name).resolve() / 'candidate')
        self.output = self.root / '_temp/AssemblyShadow/materialization'
        self.destination = self.root / ordinary.IMAGE_PATH

    def prepare(self):
        return ordinary.prepare(self.root, self.output)

    def test_exact_committed_fixture_identity_and_original_contract(self):
        data, _, _, identity = ordinary.fixture(self.root)
        self.assertEqual(len(data), 4608)
        self.assertEqual(identity['fullName'], ordinary.PROVIDER)
        self.assertEqual(identity['mvid'], 'e7f5b1ac-eca4-4034-8da4-69e25ca9fe3b')

    def test_independent_roles_decode_their_own_fixture(self):
        control = setup_project(Path(self.temp.name).resolve() / 'control')
        self.prepare()
        a = read(self.output / 'preparation.json')
        out = control / '_temp/AssemblyShadow/materialization'
        ordinary.prepare(control, out)
        b = read(out / 'preparation.json')
        self.assertEqual(self.destination.read_bytes(), (control / ordinary.IMAGE_PATH).read_bytes())
        self.assertNotEqual(a['fixture']['path'], b['fixture']['path'])
        self.assertNotEqual(a['staged']['path'], b['staged']['path'])
        self.assertEqual(a['classification'], 'FrozenHistoricalInputMaterialization')
        self.assertFalse(a['freshCscExecutionClaimed'])
        self.assertFalse(b['historicalPlayerExecutionReused'])
        self.assertFalse(b['runtimeAcceptance'])

    def test_existing_matching_destination_is_not_rewritten(self):
        data = ordinary.fixture(self.root)[0]
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(data)
        before = self.destination.stat()
        self.prepare()
        after = self.destination.stat()
        self.assertEqual((before.st_ino, before.st_mtime_ns), (after.st_ino, after.st_mtime_ns))
        receipt = read(self.output / 'preparation.json')
        self.assertEqual(receipt['destinationBefore'], receipt['staged'])

    def test_wrong_destination_preserved_and_no_output_created(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b'wrong existing bytes')
        with self.assertRaises(EvidenceError): self.prepare()
        self.assertEqual(self.destination.read_bytes(), b'wrong existing bytes')
        self.assertFalse(self.output.exists())

    def test_old_compiler_receipt_is_not_relabelled(self):
        self.prepare()
        receipt = read(self.output / 'preparation.json')
        receipt.update(schemaVersion=1, classification='CurrentWorkspaceCompilerOutput')
        (self.output / 'preparation.json').write_text(json.dumps(receipt))
        with self.assertRaises(EvidenceError): ordinary.verify(self.root, self.output)

    def test_receipt_claim_and_path_mutations_fail(self):
        self.prepare()
        path = self.output / 'preparation.json'
        original = read(path)
        for field, value in [('projectRoot', '/other'), ('outputRoot', '/other'),
                             ('expectedSha256', 'f'*64), ('result', 'Failed'),
                             ('runtimeAcceptance', True), ('historicalPlayerExecutionReused', True),
                             ('freshCscExecutionClaimed', True), ('sourcePinsSha256', 'e'*64),
                             ('classification', 'CurrentWorkspaceCompilerOutput')]:
            with self.subTest(field=field):
                row = copy.deepcopy(original); row[field] = value
                path.write_text(json.dumps(row))
                with self.assertRaises(EvidenceError): ordinary.verify(self.root, self.output)

    def test_changed_staged_or_materialized_bytes_rejected(self):
        self.prepare()
        for path in (self.destination, self.output / 'materialized.dll.bytes'):
            with self.subTest(path=path.name):
                old = path.read_bytes(); path.write_bytes(b'changed')
                with self.assertRaises(EvidenceError): ordinary.verify(self.root, self.output)
                path.write_bytes(old)

    def test_changed_source_pins_rejected(self):
        self.prepare(); (self.root / ordinary.PINS).write_text('{"changed":true}')
        with self.assertRaises(EvidenceError): ordinary.verify(self.root, self.output)

    def test_wrong_fixture_hash_never_admitted(self):
        path = self.root / ordinary.FIXTURE
        data = bytearray(ordinary.fixture(self.root)[0]); data[-1] ^= 1
        path.write_bytes(base64.b64encode(zlib.compress(bytes(data),9)) + b'\n')
        with self.assertRaises(EvidenceError): self.prepare()
        self.assertFalse(self.destination.exists())

    def test_noncanonical_encoding_rejected(self):
        path = self.root / ordinary.FIXTURE
        original = path.read_bytes()
        for data in (original[:-1], original+b'\n', b'!bad!\n', original[:10]+b'\n'+original[10:]):
            with self.subTest(size=len(data)):
                path.write_bytes(data)
                with self.assertRaises((EvidenceError, ValueError)): self.prepare()

    def test_compressed_fixture_cannot_expand_or_append_unbounded_bytes(self):
        path = self.root / ordinary.FIXTURE
        for compressed in (zlib.compress(b'A'*100000), zlib.compress(b'small')+b'trailing', b'broken'):
            path.write_bytes(base64.b64encode(compressed)+b'\n')
            with self.assertRaises(EvidenceError): self.prepare()

    def test_origin_mutations_rejected(self):
        path = self.root / ordinary.ORIGIN; original = read(path)
        for key, value in [('imageSha256', '0'*64), ('member', 'unrelated'),
                           ('archiveSha256', 'e'*64), ('sizeBytes', 1),
                           ('runtimeAcceptance', True), ('historicalPlayerExecutionReused', True),
                           ('classification', 'CurrentWorkspaceCompilerOutput')]:
            with self.subTest(field=key):
                row = copy.deepcopy(original); row[key] = value
                path.write_text(json.dumps(row))
                with self.assertRaises(EvidenceError): self.prepare()

    def test_linked_destination_and_fixture_rejected(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.symlink_to(self.root / ordinary.FIXTURE)
        with self.assertRaises(EvidenceError): self.prepare()
        self.destination.unlink()
        path = self.root / ordinary.FIXTURE; old = path.read_bytes()
        path.unlink(); foreign = self.root / 'foreign'; foreign.write_bytes(old); path.symlink_to(foreign)
        with self.assertRaises(EvidenceError): self.prepare()

    def test_linked_output_parent_rejected(self):
        target = self.root / 'outside'; target.mkdir()
        (self.root / '_temp').symlink_to(target, target_is_directory=True)
        with self.assertRaises(EvidenceError): self.prepare()

    def test_foreign_or_reused_output_refused(self):
        with self.assertRaises(EvidenceError): ordinary.prepare(self.root, self.root / 'wrong')
        self.prepare()
        with self.assertRaises(EvidenceError): self.prepare()

    def test_racing_destination_is_not_overwritten(self):
        create = ordinary._create
        def competing(path, data):
            if path == self.output / 'materialized.dll.bytes':
                self.destination.parent.mkdir(parents=True)
                self.destination.write_bytes(b'concurrent bytes')
            create(path, data)
        with patch.object(ordinary, '_create', side_effect=competing):
            with self.assertRaises(EvidenceError): self.prepare()
        self.assertEqual(self.destination.read_bytes(), b'concurrent bytes')
        self.assertEqual(read(self.output / 'preparation.json')['result'], 'Failed')

    def test_pin_change_mid_materialization_keeps_failure_receipt(self):
        create = ordinary._create
        def changing(path, data):
            create(path, data); (self.root / ordinary.PINS).write_text('{"changed":true}')
        with patch.object(ordinary, '_create', side_effect=changing):
            with self.assertRaises(EvidenceError): self.prepare()
        self.assertEqual(read(self.output / 'preparation.json')['result'], 'Failed')

    def test_no_obsolete_compiler_helper_or_stub_remains(self):
        self.assertFalse((SOURCE_ROOT/'Assets/AssemblyShadowBaseline/Editor/R02OrdinaryInput.cs').exists())
        csproj = (SOURCE_ROOT/'Tools/AssemblyShadow/R02/ManagedTests/ManagedTests.csproj').read_text()
        self.assertNotIn('OrdinaryInputStubs.cs', csproj)
        self.assertNotIn('R02OrdinaryInput.cs', csproj)


if __name__ == '__main__': unittest.main()
