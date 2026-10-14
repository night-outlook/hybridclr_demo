#!/usr/bin/env python3
"""Actual POSIX transaction -> independent Python V2 decode; host data only."""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import time
import unittest

ROOT = None
OUT = None
DRIVER = None
CODEC = None
READER = None
PROFILE = ''
RECORDS = []
CASE = 0
IDENTITY = {'runId': 'native-file-test', 'caseId': 'on-fixture', 'processId': 4242,
            'requestSha256': 'a'*64, 'buildSha256': 'b'*64, 'demoCommit': 'c'*40,
            'hybridclrCommit': 'd'*40, 'packageCommit': 'e'*40, 'nativeCommit': 'f'*40}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(argv, directory):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if PROFILE == 'sanitized':
        # Address/UB sanitizer remain on. Apple LeakSanitizer support is absent
        # on the tested runner; report it instead of claiming a leak check.
        env['ASAN_OPTIONS'] = 'abort_on_error=1:detect_leaks=' + ('0' if sys.platform == 'darwin' else '1')
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    start = time.time_ns()
    completed = subprocess.run([str(a) for a in argv], cwd=ROOT, capture_output=True,
                               env=env, timeout=30)
    record = {'argv': list(map(str, argv)), 'cwd': str(ROOT), 'profile': PROFILE,
              'startedNs': start, 'endedNs': time.time_ns(), 'exitCode': completed.returncode}
    for label, data in (('stdout', completed.stdout), ('stderr', completed.stderr)):
        (directory / label).write_bytes(data)
        record[label+'Sha256'] = hashlib.sha256(data).hexdigest()
    (directory / 'command.json').write_text(json.dumps(record, indent=2)+'\n')
    RECORDS.append(record)
    if completed.returncode:
        raise AssertionError(f'Host command failed: {argv}\n{completed.stderr.decode(errors="replace")}')
    return completed


class FileTransaction(unittest.TestCase):
    def case(self, mode='normal', *, fields=None, status='Passed', fail=0,
             root_setup=None, mutate_envelope=None):
        global CASE
        CASE += 1
        case = OUT / PROFILE / f'case-{CASE:04d}'
        case.mkdir(parents=True)
        root = case / 'transaction'
        root.mkdir(mode=0o700)
        # The test owns this new directory. Remove inherited setgid bits from
        # the test fixture, never from a production or historical input root.
        root.chmod(0o700)
        if fields is None:
            fields = {'finalDiagnostics': '{"complete":true}', 'finalExecutionDiagnostics': '{"value":2}'}
        inline = {'reportTransport': 'NativeBoundedSnapshotV2', 'runId': IDENTITY['runId'],
                  'caseId': IDENTITY['caseId'], 'processId': IDENTITY['processId'], 'result': status,
                  'postPoisonField': 2}
        wire, descriptor = CODEC.encode(IDENTITY, inline, fields)
        raw = {**inline, 'diagnosticArtifact': descriptor}
        envelope = CODEC.canonical(raw)
        if mutate_envelope:
            envelope = mutate_envelope(raw, envelope)
        data = bytearray(CODEC.binding(IDENTITY)+hashlib.sha256(CODEC.canonical(inline)).digest())
        data += struct.pack('>II', len(CODEC.canonical(inline)), len(envelope)) + envelope
        for name in CODEC.FIELDS:
            field = fields[name]
            value = b'' if field is None else field.encode('utf-8')
            data += struct.pack('>II', int(field is None), len(value)) + value
        fixture = case / 'input.bin'
        fixture.write_bytes(data)
        if root_setup:
            root = root_setup(root)
        result = execute([DRIVER, root, fixture, mode, str(fail)], case)
        observed = json.loads(result.stdout)
        self.assertEqual(observed['operatorNewCalls'], 0, 'actual transaction/encoder called operator new')
        self.assertEqual(observed['openDescriptors'], 0)
        self.assertFalse(observed['duplicateClose'])
        self.assertTrue(observed['allCloseOnExec'])
        (case/'result.json').write_text(json.dumps(observed, indent=2)+'\n')
        return Path(root), observed, fields, wire

    def success(self, **kwargs):
        root, result, fields, wire = self.case(**kwargs)
        self.assertTrue(result['committed'])
        self.assertTrue(result['receipt']['complete'])
        self.assertEqual((root/READER.ARTIFACT).read_bytes(), wire)
        view = READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)
        for name in CODEC.FIELDS:
            self.assertEqual(view[name], fields[name])
        self.assertEqual(view['reportTransport'], 'NativeBoundedSnapshotV2')
        return root, result, view

    def negative(self, expected=None, **kwargs):
        root, result, _, _ = self.case(**kwargs)
        self.assertFalse(result['committed'])
        self.assertFalse(result['receipt']['complete'])
        if expected is not None:
            self.assertEqual(result['operation'], expected)
        with self.assertRaises(READER.TransactionError):
            READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)
        return root, result

    def test_complete_native_encoder_file_consumer(self):
        self.success()

    def test_large_fields_and_utf8_cross_frames(self):
        fields = {name: json.dumps({'allBytes': '水é\\\"\u0000' * 66000}, ensure_ascii=False,
                                   separators=(',', ':')) for name in CODEC.FIELDS}
        self.assertTrue(all(len(v.encode()) > 262144 for v in fields.values()))
        self.success(fields=fields)

    def test_null_and_failed_report_are_not_promoted(self):
        _, _, view = self.success(fields={name: None for name in CODEC.FIELDS}, status='Failed')
        self.assertEqual(view['result'], 'Failed')
        self.assertIsNone(view['finalDiagnostics'])

    def test_short_write_and_single_eintr_preserve_bytes(self):
        for mode in ('short-write', 'one-eintr'):
            with self.subTest(mode=mode):
                self.success(mode=mode)

    def test_zero_write_and_bounded_interruption_fail(self):
        for mode in ('zero-write', 'all-eintr'):
            with self.subTest(mode=mode):
                _, result = self.negative(mode=mode, expected='write')
                self.assertLessEqual(result['events'].count('write'), 17)

    def test_reentry_is_immutable_first_failure(self):
        self.negative(mode='reentry', expected='reentry')

    def test_bad_encoder_receipt_fails_before_envelope(self):
        root, _ = self.negative(mode='wrong-receipt', expected='encoder-receipt')
        self.assertEqual((root/READER.ENVELOPE).stat().st_size, 0)

    def test_readback_corruption_is_not_a_commit(self):
        self.negative(mode='bad-readback', expected='readback-sha256')

    def test_link_and_replacement_preserve_original_files(self):
        for mode in ('hardlink', 'replace-file'):
            with self.subTest(mode=mode):
                self.negative(mode=mode, expected='file-replaced-or-resized')

    def test_directory_replacement_cannot_redirect_original_descriptors(self):
        root, _ = self.negative(mode='rename-directory', expected='ancestor-replaced')
        self.assertEqual(list(root.iterdir()), [])
        self.assertTrue(Path(str(root)+'.moved').is_dir())

    def test_noncanonical_root_is_not_resolved_away(self):
        def alias(root):
            other = root.with_name('alias')
            other.symlink_to(root, target_is_directory=True)
            return other
        root, _ = self.negative(root_setup=alias, expected='directory-open')
        self.assertEqual(list(root.iterdir()), [])

    def test_occupied_names_remain_untouched(self):
        for name in (READER.ARTIFACT, READER.ENVELOPE):
            def occupy(root):
                (root/name).write_bytes(b'original')
                return root
            with self.subTest(name=name):
                root, _ = self.negative(root_setup=occupy, expected='exclusive-file-open')
                self.assertEqual((root/name).read_bytes(), b'original')

    def test_early_and_repeated_commit_not_accepted(self):
        for mode in ('early-envelope', 'repeat'):
            self.negative(mode=mode, expected='envelope-order')

    def test_wrong_root_identity_and_permissions(self):
        self.negative(mode='wrong-root', expected='admitted-root')
        def permissions(root):
            root.chmod(0o755)
            return root
        self.negative(root_setup=permissions, expected='admitted-root')

    def test_bad_lexical_components_rejected(self):
        for suffix in ('/', '//', '/.', '/../transaction'):
            self.negative(root_setup=lambda root: str(root)+suffix)

    def test_envelope_budget_unchanged(self):
        self.negative(mutate_envelope=lambda r, e: e+b' '*(262145-len(e)), expected='envelope-bound')

    def test_incomplete_receipt_cannot_be_read_as_complete(self):
        root, result, _ = self.success()
        result['receipt']['complete'] = False
        with self.assertRaises(READER.TransactionError):
            READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_artifact_hash_and_size_corruption_rejected(self):
        for transform in (lambda b: b[:-1], lambda b: bytes([b[0]^1])+b[1:], lambda b: b+b'x'):
            root, result, _ = self.success()
            p = root/READER.ARTIFACT
            p.write_bytes(transform(p.read_bytes()))
            with self.assertRaises((READER.TransactionError, CODEC.ContractError)):
                READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_postcommit_same_bytes_new_inode_and_hardlink_rejected(self):
        for kind in ('replace', 'link'):
            root, result, _ = self.success()
            p = root/READER.ARTIFACT
            if kind == 'replace':
                p.rename(root/'old')
                p.write_bytes((root/'old').read_bytes())
                p.chmod(0o600)
            else:
                os.link(p, root/'extra')
            with self.assertRaises(READER.TransactionError):
                READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_envelope_hash_changes_are_rejected(self):
        root, result, _ = self.success()
        with (root/READER.ENVELOPE).open('ab') as stream:
            stream.write(b' ')
        with self.assertRaises(READER.TransactionError):
            READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_pid_and_source_replay_rejected(self):
        root, result, _ = self.success()
        for key, replacement in (('processId', 999), ('nativeCommit', 'a'*40), ('requestSha256', 'f'*64)):
            identity = dict(IDENTITY)
            identity[key] = replacement
            with self.assertRaises(CODEC.ContractError):
                READER.read_snapshot(root, result['receipt'], identity, CODEC)

    def test_strict_receipt_types_keys_and_sync_policy(self):
        root, result, _ = self.success()
        for part, key, value in (('', 'extra', 1), ('', 'syncPolicy', 'none'),
                                 ('artifact', 'bytes', True), ('root', 'mode', 0o755),
                                 ('envelope', 'sha256', 'x'*64)):
            receipt = copy.deepcopy(result['receipt'])
            target = receipt[part] if part else receipt
            target[key] = value
            with self.assertRaises(READER.TransactionError):
                READER.read_snapshot(root, receipt, IDENTITY, CODEC)

    def test_strict_envelope_json_transport_and_collisions(self):
        mutations = [lambda r, e: b'{"result":1,"result":2}',
                     lambda r, e: CODEC.canonical({**r, 'reportTransport': 'NativePreopenedSnapshotV1'}),
                     lambda r, e: CODEC.canonical({**r, 'finalDiagnostics': '{}'}),
                     lambda r, e: b'{"x":NaN}', lambda r, e: b'{"x":1e309}']
        for mutation in mutations:
            root, result, _, _ = self.case(mutate_envelope=mutation)
            self.assertTrue(result['committed'], 'File transaction is not a JSON semantic validator')
            with self.assertRaises(READER.TransactionError):
                READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_change_during_decode_is_not_returned(self):
        root, result, _ = self.success()
        class ChangingCodec:
            FIELDS = CODEC.FIELDS
            strict_json = staticmethod(CODEC.strict_json)
            @staticmethod
            def decode(*args):
                result = CODEC.decode(*args)
                p = root/READER.ENVELOPE
                p.rename(root/'retained-envelope')
                p.write_bytes((root/'retained-envelope').read_bytes())
                p.chmod(0o600)
                return result
        with self.assertRaises(READER.TransactionError):
            READER.read_snapshot(root, result['receipt'], IDENTITY, ChangingCodec)

    def test_overflowed_diagnostic_numbers_rejected(self):
        fields = {'finalDiagnostics': '{"x":1e309}', 'finalExecutionDiagnostics': '{}'}
        root, result, _, _ = self.case(fields=fields)
        self.assertTrue(result['committed'])
        with self.assertRaises(READER.TransactionError):
            READER.read_snapshot(root, result['receipt'], IDENTITY, CODEC)

    def test_every_commit_io_failure_fails_closed(self):
        _, base, _ = self.success()
        # Exercise every mutating/durability/close boundary plus first/last
        # path/identity/read calls. These are host fault injections, not OS faults.
        events = base['events']
        chosen = {i+1 for i, op in enumerate(events) if op in
                  ('root-open', 'directory-open', 'file-open', 'write', 'file-sync', 'directory-sync', 'close')}
        for op in ('pread', 'fstat', 'fstatat'):
            positions = [i+1 for i, value in enumerate(events) if value == op]
            chosen.update((positions[0], positions[-1]))
        for index in sorted(chosen):
            with self.subTest(index=index, operation=events[index-1]):
                _, result = self.negative(fail=index)
                self.assertEqual(result['errno'], 5)  # EIO on supported POSIX targets.


def main():
    global ROOT, OUT, DRIVER, CODEC, READER, PROFILE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    ROOT = args.repository.resolve(strict=True)
    OUT = args.output
    if not (OUT.is_absolute() and OUT == OUT.resolve(strict=False) and not OUT.exists() and
            OUT.parent.is_dir() and ROOT not in OUT.parents and OUT not in ROOT.parents):
        raise RuntimeError('Fresh canonical external output with existing parent required')
    here = ROOT/'Tools/AssemblyShadow/R03IR/bounded_v2'
    reference = ROOT/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py'
    CODEC = load(reference, 'wire_reference')
    READER = load(here/'transaction_reader.py', 'transaction_reader')
    OUT.mkdir()
    sources = []
    for p in (here/'BoundedDiagnosticsV2.h', here/'PosixDiagnosticTransaction.h', here/'transaction_driver.cpp',
              here/'transaction_reader.py', here/'run_transaction_tests.py', reference):
        data = p.read_bytes()
        sources.append({'path': str(p.relative_to(ROOT)), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                        'gitBlob': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
    profiles = []
    try:
        for PROFILE in ('strict', 'sanitized'):
            path = OUT/PROFILE
            path.mkdir()
            DRIVER = path/'transaction-driver'
            compiler = shutil.which(os.environ.get('CXX', 'clang++'))
            if not compiler:
                raise RuntimeError('Native C++ compiler required')
            args = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic', '-g',
                    str(here/'transaction_driver.cpp'), '-o', str(DRIVER)]
            if PROFILE == 'sanitized':
                args += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
                if sys.platform != 'darwin':
                    args += ['-fno-pie', '-no-pie']
            compile_dir = path/'compile'
            compile_dir.mkdir()
            execute(args, compile_dir)
            with (path/'tests.log').open('w') as log:
                result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FileTransaction))
            profiles.append({'profile': PROFILE, 'tests': result.testsRun, 'failures': len(result.failures),
                             'errors': len(result.errors), 'skipped': len(result.skipped)})
            if not result.wasSuccessful() or result.skipped:
                raise RuntimeError('Native transaction tests failed; preserve tests.log')
        print(json.dumps({'profiles': profiles, 'commands': len(RECORDS)}, indent=2))
    finally:
        (OUT/'RESULT.json').write_text(json.dumps({'kind': 'InactiveNativeFileTransactionTests', 'profiles': profiles,
              'sources': sources, 'commands': len(RECORDS), 'actualUnity': False, 'productionTransportEnabled': False,
              'VMProducerOrSemanticAcceptanceProven': False, 'platform': platform.platform(),
              'leakSanitizer': 'UnavailableOnApple' if sys.platform == 'darwin' else 'Enabled',
              'devicePowerLossTested': False}, indent=2)+'\n')
        entries = [{'path': str(p.relative_to(OUT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in sorted(OUT.rglob('*')) if p.is_file()]
        (OUT/'MANIFEST.json').write_text(json.dumps({'files': entries}, indent=2)+'\n')

if __name__ == '__main__':
    main()
