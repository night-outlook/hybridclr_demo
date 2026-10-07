import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from h1_capture_attempt import (Attempt, RetentionError, ENCODING_ZLIB,
                                load_retained, verify_attempt_store)

OLD_LIMIT = 256 * 1024 * 1024
SOURCE_BYTES = 640 * 1024


class VolumeRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def sparse(path, marker, size=SOURCE_BYTES):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(marker)
            stream.truncate(size)

    def graph_fixture(self):
        nodes = []
        objects = []
        external = self.root / 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/external'
        bdwgc = [external / 'bdwgc/extra/gc.c',
                 external / 'bdwgc/extra/krait_signal_handler.c']
        zlib = [external / 'zlib' / (name + '.c') for name in (
            'adler32', 'crc32', 'deflate', 'gzclose', 'gzlib', 'gzread', 'gzwrite',
            'infback', 'inffast', 'inflate', 'inftrees', 'trees', 'uncompr', 'zutil')]
        runtime = [self.root / 'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/il2cppOutput/cpp' /
                   ('Runtime_%03d.cpp' % i) for i in range(428)]
        sources = bdwgc + zlib + runtime
        self.assertEqual(444, len(sources))
        for i, path in enumerate(sources):
            # Sparse zeros keep the fixture cheap on disk while preserving >256 MiB
            # of distinct logical source bytes through the unique prefix.
            self.sparse(path, ('/* unique source %d */\n' % i).encode())
            obj = self.root / 'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/objects' / ('%03d.o' % i)
            objects.append(str(obj))
            nodes.append({'Annotation': 'C_Mac_arm64 ' + str(obj),
                          'Inputs': [str(path)], 'Outputs': [str(obj)]})
        pchdir = self.root / 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp/pch'
        for i, name in enumerate(('pch-c.h', 'pch-cpp.hpp')):
            header = pchdir / name
            header.parent.mkdir(parents=True, exist_ok=True)
            header.write_bytes(('/* pch %d */' % i).encode())
            output = self.root / 'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/pch' / ('%d.pch' % i)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b'PCH' + bytes([i]))
            nodes.append({'Annotation': 'C_Mac_arm64Pch ' + str(output),
                          'Inputs': [str(header)], 'Outputs': [str(output)]})
        game = self.root / 'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/GameAssembly.dylib'
        nodes.append({'Annotation': 'Link_Mac_arm64 ' + str(game),
                      'Inputs': objects, 'Outputs': [str(game)]})
        self.assertEqual(446, sum(str(n['Annotation']).startswith('C_Mac_arm64') for n in nodes))
        self.assertEqual(444, len(nodes[-1]['Inputs']))
        return {'Nodes': nodes}

    def test_446_action_volume_above_old_256_mib_retains_all_declared_bytes(self):
        graph = self.graph_fixture()
        attempt = Attempt(self.root / 'attempt', 'volume-regression')
        with attempt.guard():
            attempt.stage('declared-input-retention')
            attempt.retain_declared_inputs(graph, self.root)
            self.assertGreater(attempt.used_bytes, OLD_LIMIT)
            self.assertLess(attempt.stored_bytes, 64 * 1024 * 1024)
            attempt.finish('VolumeFixtureRetainedNotAcceptance')
        state = json.loads((attempt.root / 'attempt-state.json').read_text())
        self.assertEqual('Passed', state['retentionStoreVerification'])
        self.assertGreater(state['retainedUniqueBytes'], OLD_LIMIT)
        self.assertEqual(448, state['declaredInputPathCount'])
        source_rows = [r for r in attempt.rows if Path(r['sourcePath']).suffix in ('.c', '.cpp')]
        self.assertEqual(444, len(source_rows))
        self.assertTrue(all(r['retainedEncoding'] == 'zlib-v1' for r in source_rows))
        for row in (source_rows[0], source_rows[-1]):
            self.assertEqual(row['sha256'], hashlib.sha256(load_retained(row)).hexdigest())
        summary = verify_attempt_store(attempt.root)
        self.assertEqual(attempt.used_bytes, summary['logicalUniqueBytes'])
        self.assertEqual(attempt.stored_bytes, summary['storedBytes'])

    def test_logical_limit_exhaustion_is_failed_not_accepted_without_receipt(self):
        source = self.root / 'a.cpp'
        self.sparse(source, b'logical', size=2 * 1024 * 1024)
        graph = {'Nodes': [{'Annotation': 'C_Mac_arm64', 'Inputs': [str(source)], 'Outputs': ['a.o']}]}
        attempt = Attempt(self.root / 'attempt', 'logical-limit', max_total_bytes=1024 * 1024)
        with self.assertRaisesRegex(RetentionError, 'logical retention byte bound'):
            with attempt.guard():
                attempt.stage('declared-input-retention')
                attempt.retain_declared_inputs(graph, self.root)
                (attempt.root / 'h1-compiler-provenance.json').write_text('should not happen')
        state = json.loads((attempt.root / 'attempt-state.json').read_text())
        self.assertEqual('FailedNotAccepted', state['status'])
        self.assertFalse((attempt.root / 'h1-compiler-provenance.json').exists())

    def test_stored_limit_exhaustion_is_failed_not_accepted_without_receipt(self):
        raw = b''.join(hashlib.sha256(str(i).encode()).digest() for i in range(8192))
        attempt = Attempt(self.root / 'attempt', 'stored-limit', max_stored_bytes=32 * 1024)
        with self.assertRaisesRegex(RetentionError, 'stored retention byte bound'):
            with attempt.guard():
                attempt.keep_bytes('/large.cpp', raw, 'declared-native-input', storage=ENCODING_ZLIB)
        state = json.loads((attempt.root / 'attempt-state.json').read_text())
        self.assertEqual('FailedNotAccepted', state['status'])
        self.assertFalse((attempt.root / 'h1-compiler-provenance.json').exists())

    def test_compressed_blob_tamper_is_detected_fail_closed(self):
        attempt = Attempt(self.root / 'attempt', 'tamper')
        row = attempt.keep_bytes('/large.cpp', b'A' * 200000, 'declared-native-input', storage=ENCODING_ZLIB)
        path = Path(row['retainedPath'])
        path.write_bytes(path.read_bytes() + b'tamper')
        with self.assertRaisesRegex(RetentionError, 'stored length differs'):
            attempt.verify_store()

    def test_finish_refuses_corrupt_store_and_records_failure_under_guard(self):
        attempt = Attempt(self.root / 'attempt', 'finish-tamper')
        with self.assertRaises(RetentionError):
            with attempt.guard():
                row = attempt.keep_bytes('/large.cpp', b'A' * 200000, 'declared-native-input', storage=ENCODING_ZLIB)
                Path(row['retainedPath']).write_bytes(b'bad')
                attempt.finish('MustNotPass')
        state = json.loads((attempt.root / 'attempt-state.json').read_text())
        self.assertEqual('FailedNotAccepted', state['status'])
        self.assertNotEqual('Passed', state['retentionStoreVerification'])

    def test_incompressible_request_falls_back_to_raw_without_identity_change(self):
        raw = b''.join(hashlib.sha256(('x%d' % i).encode()).digest() for i in range(2048))
        attempt = Attempt(self.root / 'attempt', 'raw-fallback')
        row = attempt.keep_bytes('/large.cpp', raw, 'declared-native-input', storage=ENCODING_ZLIB)
        self.assertEqual('raw-v1', row['retainedEncoding'])
        self.assertEqual(raw, load_retained(row))


if __name__ == '__main__':
    unittest.main()
