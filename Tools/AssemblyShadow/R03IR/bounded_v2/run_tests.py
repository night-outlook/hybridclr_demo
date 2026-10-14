#!/usr/bin/env python3
"""Build and exercise the inactive native V2 codec against the pinned Python spec.

No Unity/VM/process scheduler is loaded. Output must be a fresh external directory.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import unittest

REFERENCE_BLOB = '0866b07f758a20284d2a5d5d933b2be577b20b50'
REFERENCE_PATH = ('Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/'
                  'SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py')
REFERENCE = None
OUT = None
DRIVER = None
PROFILE = ''
COMMANDS = []
SERIAL = 0
IDENTITY = dict(runId='interop-run', caseId='baseline', processId=1234,
    requestSha256='a'*64, buildSha256='b'*64, demoCommit='1'*40,
    hybridclrCommit='2'*40, packageCommit='3'*40, nativeCommit='4'*40)
INLINE = {'reportTransport': 'NativeBoundedSnapshotV2', 'status': 'Failed',
          'preReflection': 42, 'preDelegate': 42, 'canary': 0}

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def command(argv, prefix):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
               ASAN_OPTIONS=('detect_leaks=0:abort_on_error=1' if sys.platform == 'darwin'
                             else 'detect_leaks=1:abort_on_error=1'),
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    r = subprocess.run([str(a) for a in argv], capture_output=True, env=env, timeout=120)
    prefix.with_suffix('.stdout').write_bytes(r.stdout)
    prefix.with_suffix('.stderr').write_bytes(r.stderr)
    COMMANDS.append(dict(argv=[str(a) for a in argv], exit=r.returncode,
                         stdoutSha256=sha(r.stdout), stderrSha256=sha(r.stderr),
                         record=str(prefix.relative_to(OUT)),
                         asanOptions=env['ASAN_OPTIONS'], ubsanOptions=env['UBSAN_OPTIONS']))
    if r.returncode:
        raise RuntimeError(f'{argv[0]} exit {r.returncode}: {r.stderr[-2000:]!r}')
    return r

def encode(a, b, mode='direct', fail=0, inline_size=None, kind=None):
    global SERIAL
    SERIAL += 1
    p = OUT / PROFILE / f'case-{SERIAL:04d}'
    fields = [a, b]
    data = [b'' if f is None else f for f in fields]
    tags = [int(f is not None) for f in fields] if kind is None else kind
    packed = struct.pack('>BBII', *tags, *[len(f) for f in data])
    packed += REFERENCE.binding(IDENTITY) + hashlib.sha256(REFERENCE.inline_bytes(INLINE)).digest()
    packed += data[0] + data[1]
    inp = p.with_suffix('.input'); raw = p.with_suffix('.bin'); receipt = p.with_suffix('.json')
    inp.write_bytes(packed)
    if inline_size is None:
        inline_size = len(REFERENCE.inline_bytes(INLINE))
    command([DRIVER, inp, raw, receipt, fail, mode, inline_size], p)
    return raw.read_bytes(), json.loads(receipt.read_text())

def descriptor(data):
    return dict(kind='R03BoundedDiagnosticsV2', bytes=len(data), sha256=sha(data),
                binding=REFERENCE.binding(IDENTITY).hex(),
                inlineSha256=sha(REFERENCE.inline_bytes(INLINE)))

class NativeCodecTests(unittest.TestCase):
    def roundtrip(self, a, b, mode='direct'):
        data, receipt = encode(a, b, mode)
        self.assertTrue(receipt['ok']); self.assertTrue(receipt['complete'])
        self.assertEqual(receipt['protectedNewCalls'], 0)
        fields = {k: None if v is None else v.decode('utf-8')
                  for k, v in zip(REFERENCE.FIELDS, (a, b))}
        original, expected = REFERENCE.encode(IDENTITY, INLINE, fields)
        self.assertEqual(data, original)
        self.assertEqual(receipt['bytes'], len(data))
        self.assertEqual(receipt['sha256'], expected['sha256'])
        self.assertEqual(REFERENCE.decode(io.BytesIO(data), expected, IDENTITY, INLINE), fields)
        return data, receipt

    def test_hash_and_capture_state_controls(self):
        r = command([DRIVER, 'selftest'], OUT / PROFILE / 'selftest')
        obj = json.loads(r.stdout)
        self.assertEqual(obj['shaVectors'], 3)
        self.assertLessEqual(obj['sizeofEncoder'], 256)
        self.assertLessEqual(obj['sizeofCapture'], 128)

    def test_null_empty_and_distinct_kinds(self):
        for a,b in ((None,None),(b'',None),(None,b''),(b'',b'')):
            with self.subTest(a=a,b=b): self.roundtrip(a,b)

    def test_both_fields_exceed_old_slot_without_loss(self):
        a = json.dumps({'assembly': ['a'*200 for _ in range(2048)]}).encode()
        b = json.dumps({'classes': ['b'*160 for _ in range(2200)]}).encode()
        self.assertGreater(len(a), 262144); self.assertGreater(len(b), 262144)
        for mode in ('direct', 'capture'): self.roundtrip(a,b,mode)

    def test_frame_and_hash_block_boundaries(self):
        for n in (1,55,56,57,63,64,65,127,128,65535,65536,65537,262144,262145):
            with self.subTest(n=n): self.roundtrip(b'a'*n, b'b'*(n//2))

    def test_utf8_cross_frame_and_embedded_nul(self):
        a = b'a'*65535+'😀'.encode()+b'\x00'+ '中文é'.encode()
        for mode in ('direct','capture'): self.roundtrip(a, b'\x00', mode)

    def test_random_independent_reference_vectors(self):
        rng = random.Random(928391)
        for i in range(12):
            n = rng.randrange(1, 220000)
            a = bytes(rng.randrange(32,127) for _ in range(n))
            with self.subTest(vector=i): self.roundtrip(a, a[::-1], 'capture')

    def test_exact_aggregate_limit_and_one_byte_over(self):
        maximum = REFERENCE.MAX_STREAM - 192
        while 192 + maximum + 38*((maximum+65535)//65536) > REFERENCE.MAX_STREAM:
            maximum -= 1
        data,_ = self.roundtrip(b'x'*maximum,b'')
        self.assertEqual(len(data), REFERENCE.MAX_STREAM)
        for mode in ('direct','capture'):
            data,r = encode(b'x'*(maximum+1),b'',mode)
            self.assertFalse(r['ok']);self.assertFalse(r['complete']);self.assertEqual(data,b'')
            self.assertTrue(r['error']==3 or r['captureError']==3)

    def test_invalid_utf8_fails_before_emission(self):
        for value in (b'\xc0\xaf',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',
                      b'\xf5\x80\x80\x80',b'\xe2\x82',b'\x80'):
            for mode in ('direct','capture'):
                with self.subTest(value=value,mode=mode):
                    data,r=encode(value,b'{}',mode)
                    self.assertFalse(r['ok']);self.assertEqual(data,b'')
                    self.assertTrue(r['error']==4 or r['captureError']==4)

    def test_null_with_bytes_is_not_silently_ignored(self):
        for mode in ('direct','capture'):
            data,r=encode(b'present',b'{}',mode,kind=(0,1))
            self.assertFalse(r['ok']);self.assertEqual(data,b'')

    def test_scratch_alias_short_buffer_and_null_pointer_fail_before_io(self):
        for mode in ('alias-scratch','small-scratch','null-data'):
            with self.subTest(mode=mode):
                data,r=encode(b'a'*65536,b'{}',mode)
                self.assertFalse(r['ok']);self.assertEqual(r['error'],2)
                self.assertEqual(r['sinkCalls'],0);self.assertEqual(data,b'')

    def test_inline_budget_unchanged(self):
        self.roundtrip(b'{}',b'{}')
        data,r=encode(b'{}',b'{}',inline_size=REFERENCE.RESERVE-4096+1)
        self.assertFalse(r['ok']);self.assertEqual(data,b'')

    def test_each_sink_failure_retains_incomplete_receipt(self):
        _, success = self.roundtrip(b'a'*65537,b'b'*65537)
        for index in range(1,success['sinkCalls']+1):
            with self.subTest(call=index):
                data,r=encode(b'a'*65537,b'b'*65537,fail=index)
                self.assertFalse(r['ok']);self.assertFalse(r['complete'])
                self.assertEqual(r['error'],5);self.assertEqual(r['bytes'],0)
                with self.assertRaises(REFERENCE.ContractError):
                    REFERENCE.decode(io.BytesIO(data),descriptor(data),IDENTITY,INLINE)

    def test_synchronous_sink_reentry_fails_closed(self):
        data,r=encode(b'{}',b'{}','reenter')
        self.assertFalse(r['ok']);self.assertEqual(r['error'],6)
        self.assertFalse(r['complete']);self.assertEqual(data,b'')

    def test_changed_frozen_input_latches_error_before_footer(self):
        data,r=encode(b'abcdef',b'{}','mutate')
        self.assertFalse(r['ok']);self.assertEqual(r['error'],7)
        self.assertFalse(r['complete'])
        with self.assertRaises(REFERENCE.ContractError):
            REFERENCE.decode(io.BytesIO(data),descriptor(data),IDENTITY,INLINE)

    def test_one_shot_no_second_artifact(self):
        data,r=encode(b'{}',b'{}','reuse')
        self.assertTrue(r['ok']);self.assertEqual(r['error'],1)
        expected,_=REFERENCE.encode(IDENTITY,INLINE,dict(zip(REFERENCE.FIELDS,['{}','{}'])))
        self.assertEqual(data,expected)

    def test_replay_identity_rejected(self):
        data,_=self.roundtrip(b'{}',b'{}')
        for key in IDENTITY:
            other=IDENTITY.copy()
            other[key]=4321 if key=='processId' else (other[key][:-1]+'9')
            with self.subTest(key=key),self.assertRaises(REFERENCE.ContractError):
                REFERENCE.decode(io.BytesIO(data),descriptor(data),other,INLINE)

    def test_interior_corruption_rejected_even_with_new_outer_hash(self):
        data,_=self.roundtrip(b'a'*65537,b'{}')
        for index in (0,8,40,72,73,77,79,81,112,117,120,150,len(data)-1):
            changed=bytearray(data);changed[index]^=1;changed=bytes(changed)
            with self.subTest(index=index),self.assertRaises(REFERENCE.ContractError):
                REFERENCE.decode(io.BytesIO(changed),descriptor(changed),IDENTITY,INLINE)

    def test_short_trailing_and_missing_sections_rejected(self):
        data,_=self.roundtrip(b'a'*65537,b'{}')
        for changed in (data[:72],data[:112],data[:-1],data[:-40],data+b'!'):
            with self.subTest(length=len(changed)),self.assertRaises(REFERENCE.ContractError):
                REFERENCE.decode(io.BytesIO(changed),descriptor(changed),IDENTITY,INLINE)

    def test_failed_report_never_promoted_by_hydration(self):
        data,_=self.roundtrip(b'{"allClasses":[1,2]}',b'{"allEntries":[3,4]}')
        expected=descriptor(data);raw={**INLINE,'diagnosticArtifact':expected}
        hydrated=REFERENCE.hydrate(raw,data,expected,IDENTITY)
        self.assertEqual(hydrated['status'],'Failed')
        self.assertEqual(hydrated['reportTransport'],'NativeBoundedSnapshotV2')

    def test_invalid_semantic_json_rejected_after_lossless_transport(self):
        for text in (b'{"a":1,"a":2}',b'{"n":NaN}',b'{"n":Infinity}',b'not json'):
            data,_=self.roundtrip(text,b'{}');expected=descriptor(data)
            with self.assertRaises(REFERENCE.ContractError):
                REFERENCE.hydrate({**INLINE,'diagnosticArtifact':expected},data,expected,IDENTITY)


def main():
    global REFERENCE, OUT, DRIVER, PROFILE
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reference',type=Path)
    args=p.parse_args()
    if not __debug__:raise RuntimeError('Assertions must be enabled')
    repo=args.repository.resolve(strict=True)
    here=Path(__file__).resolve().parent
    reference=args.reference or repo/REFERENCE_PATH
    original=reference.read_bytes()
    if blob(original)!=REFERENCE_BLOB:raise RuntimeError('Reference Git blob mismatch')
    spec=importlib.util.spec_from_file_location('reference_diagnostics',reference)
    REFERENCE=importlib.util.module_from_spec(spec);spec.loader.exec_module(REFERENCE)
    OUT=args.output
    if (not OUT.is_absolute() or OUT!=OUT.resolve(strict=False) or OUT.exists()
        or OUT.is_symlink() or not OUT.parent.is_dir() or repo==OUT
        or repo in OUT.parents or OUT in repo.parents):
        raise RuntimeError('Fresh canonical external output required')
    OUT.mkdir()
    inputs=[here/'BoundedDiagnosticsV2.h',here/'native_driver.cpp',Path(__file__).resolve(),reference]
    sources=[dict(path=str(f),bytes=f.stat().st_size,gitBlob=blob(f.read_bytes()),sha256=sha(f.read_bytes())) for f in inputs]
    compiler=shutil.which(os.environ.get('CXX','clang++'))
    if not compiler:raise RuntimeError('Required compiler unavailable')
    results=[]
    try:
        for PROFILE in ('strict','sanitized'):
            (OUT/PROFILE).mkdir();DRIVER=OUT/PROFILE/'native-driver'
            flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-pedantic']
            if PROFILE=='sanitized':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            command([compiler,*flags,here/'native_driver.cpp','-o',DRIVER],OUT/PROFILE/'compile')
            with (OUT/PROFILE/'tests.log').open('w') as log:
                r=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativeCodecTests))
            results.append(dict(profile=PROFILE,tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped)))
            if not r.wasSuccessful():raise RuntimeError(f'{PROFILE} tests failed: preserve tests.log')
    finally:
        unchanged=all(sha(f.read_bytes())==s['sha256'] for f,s in zip(inputs,sources))
        (OUT/'RESULT.json').write_text(json.dumps(dict(kind='BoundedNativeV2Interop',results=results,
            sources=sources,sourceUnchanged=unchanged,commands=COMMANDS,
            actualUnity=False,productionIntegration=False,runtimeAcceptance=False,
            leakSanitizer=('UnavailableOnAppleRunner' if sys.platform=='darwin' else 'Enabled')),indent=2)+'\n')
        files=[dict(path=str(f.relative_to(OUT)),bytes=f.stat().st_size,sha256=sha(f.read_bytes())) for f in sorted(OUT.rglob('*')) if f.is_file()]
        (OUT/'MANIFEST.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
    if not unchanged:raise RuntimeError('Source changed')
    print(json.dumps(dict(results=results,compilerProcessRecords=len(COMMANDS),runtimeAcceptance=False)))

if __name__=='__main__':main()
