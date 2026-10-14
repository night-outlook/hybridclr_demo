#!/usr/bin/env python3
"""Actual C++ capture/codec and POSIX sink, checked against pinned Python V2.
Not a Unity/GC/lifecycle test; it never reads a Local historical evidence root.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest

REFERENCE = 'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py'
REFERENCE_BLOB = '0866b07f758a20284d2a5d5d933b2be577b20b50'
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT: Path
RECORDS: list[dict] = []
PROFILES = ('strict', 'sanitized')
# The Apple ASan runtime rejects leak detection before entering the binary.
# Keep address/undefined instrumentation and fail-fast behavior on both OSes;
# explicitly record Darwin leak coverage as unavailable, never as Passed.
LEAK_CHECK = sys.platform != 'darwin'
ASAN = f'detect_leaks={int(LEAK_CHECK)}:abort_on_error=1'
UBSAN = 'halt_on_error=1:print_stacktrace=1'

def sha(data): return hashlib.sha256(data).hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def run(argv, expected=0):
    n=len(RECORDS)
    start=time.time()
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', ASAN_OPTIONS=ASAN, UBSAN_OPTIONS=UBSAN)
    result=subprocess.run([str(x) for x in argv],cwd=HERE,env=env,capture_output=True,timeout=40)
    row={'argv':[str(x) for x in argv],'cwd':str(HERE),'startUnix':start,'elapsedSeconds':time.time()-start,'exit':result.returncode,'expectedExit':expected,'sanitizerEnvironment':{'ASAN_OPTIONS':ASAN,'UBSAN_OPTIONS':UBSAN}}
    for name,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        p=OUT/'commands'/f'{n:04d}.{name}';p.write_bytes(data)
        row[name]={'path':str(p.relative_to(OUT)),'bytes':len(data),'sha256':sha(data)}
    RECORDS.append(row)
    if result.returncode!=expected: raise AssertionError(f'{argv!r} returned {result.returncode}, expected {expected}: {result.stderr[-2000:]!r}')
    return result.stdout

IDENTITY={'runId':'native-v2-test','caseId':'host-only','processId':12345,
          'requestSha256':'1'*64,'buildSha256':'2'*64,'demoCommit':'3'*40,
          'hybridclrCommit':'4'*40,'packageCommit':'5'*40,'nativeCommit':'6'*40}
INLINE={'reportTransport':'NativeBoundedSnapshotV2','result':'Failed','canary':2}

def native(fields,profile,chunk=7,expected=0,inline_size=None):
    directory=OUT/'cases'/str(len(RECORDS));directory.mkdir()
    paths=[]
    for i,value in enumerate(fields):
        if value is None: paths.append('-')
        else:
            p=directory/f'field{14+i}.utf8';p.write_bytes(value if isinstance(value,bytes) else value.encode('utf-8'));paths.append(p)
    inline=ref.inline_bytes(INLINE)
    args=[OUT/f'codec-{profile}','encode',ref.binding(IDENTITY).hex(),sha(inline),len(inline) if inline_size is None else inline_size,*paths,directory/'diagnostics.v2',chunk]
    metadata=json.loads(run(args,expected));raw=(directory/'diagnostics.v2').read_bytes()
    return metadata,raw

class NativeCodec(unittest.TestCase):
    def parity(self,fields,chunk=7):
        values=dict(zip(ref.FIELDS,fields))
        expected,descriptor=ref.encode(IDENTITY,INLINE,values)
        for profile in PROFILES:
            with self.subTest(profile=profile):
                meta,data=native(fields,profile,chunk)
                self.assertTrue(meta['ok']);self.assertEqual(data,expected)
                self.assertEqual(meta['bytes'],descriptor['bytes']);self.assertEqual(meta['sha256'],descriptor['sha256'])
                self.assertEqual(meta['binding'],descriptor['binding']);self.assertEqual(meta['inlineSha256'],descriptor['inlineSha256'])
                self.assertLessEqual(meta['maxWrite'],65536)
                self.assertEqual(ref.decode(io.BytesIO(data),descriptor,IDENTITY,INLINE),values)
        return expected,descriptor

    def test_01_actual_native_negative_state_io_and_allocation_controls(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                result=json.loads(run([OUT/f'codec-{profile}','selftest']))
                self.assertTrue(result['passed']);self.assertEqual(result['scenarios'],24)
                self.assertEqual(result['writeFaultPositions'],10)
                self.assertLessEqual(result['codecPlusInlineAndStackReserve'],ref.TOTAL)

    def test_02_sha256_vectors_and_block_edges(self):
        for value in (b'',b'abc',b'a'*55,b'a'*56,b'a'*63,b'a'*64,b'a'*65,b'a'*1000000,bytes(range(256))*4):
            p=OUT/'cases'/f'hash-{len(RECORDS)}';p.write_bytes(value)
            for profile in PROFILES:
                self.assertEqual(run([OUT/f'codec-{profile}','hash',p]).strip().decode(),sha(value))

    def test_03_null_distinct_from_empty(self): self.parity([None,''])
    def test_04_empty_distinct_from_null(self): self.parity(['',None])
    def test_05_both_null(self): self.parity([None,None])
    def test_06_empty_fields(self): self.parity(['',''])
    def test_07_ordinary_json(self): self.parity(['{"state":9}','{"classes":[]}'])
    def test_08_both_fields_exceed_original_slot(self): self.parity(['{"data":"'+'A'*600000+'"}', '{"items":"'+'B'*420000+'"}'],4093)
    def test_09_utf8_crosses_frame_and_append_boundary(self): self.parity(['x'*65535+'😀'+'y'*65535+'€','漢字\0café'],1)
    def test_10_binary_nul_preserved(self): self.parity(['hello\0world','\0'],2)
    def test_11_chunk_boundaries(self):
        for n in (1,65535,65536,65537,262144,262145): self.parity(['z'*n,'{}'],65537)
    def test_12_complete_maximum_budget(self):
        maximum=ref.MAX_STREAM-192-60*38
        self.parity(['x'*maximum,''],65536)
    def test_13_one_byte_above_budget_fails_before_emission(self):
        maximum=ref.MAX_STREAM-192-60*38
        for p in PROFILES:
            meta,raw=native(['x'*(maximum+1),''],p,65536,2)
            self.assertFalse(meta['ok']);self.assertEqual(meta['error'],3);self.assertEqual(raw,b'');self.assertEqual(meta['bytes'],0)
    def test_14_inline_reservation_is_not_enlarged(self):
        for p in PROFILES:
            meta,raw=native(['{}','{}'],p,expected=2,inline_size=ref.RESERVE-4095)
            self.assertEqual(meta['error'],3);self.assertEqual(raw,b'')
    def test_15_invalid_utf8_is_not_normalized(self):
        for value in (b'\xc0\x80',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\x80',b'\xe2\x82',b'\xff'):
            for p in PROFILES:
                meta,raw=native([value,'{}'],p,1,2)
                self.assertEqual(meta['error'],5);self.assertEqual(raw,b'')
    def test_16_changed_chunk_is_rejected(self):
        data,descriptor=self.parity(['x'*70000,'{}'])
        broken=bytearray(data);broken[72+40+38+7]^=1
        with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(broken),descriptor,IDENTITY,INLINE)
    def test_17_truncated_file_is_rejected(self):
        data,d=self.parity(['{}','{}'])
        for cut in (0,71,111,len(data)-1):
            with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(data[:cut]),d,IDENTITY,INLINE)
    def test_18_trailing_file_bytes_are_rejected(self):
        data,d=self.parity(['{}','{}'])
        with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(data+b'x'),d,IDENTITY,INLINE)
    def test_19_cross_process_replay_is_rejected(self):
        data,d=self.parity(['{}','{}'])
        with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(data),d,{**IDENTITY,'processId':12346},INLINE)
    def test_20_inline_receipt_substitution_is_rejected(self):
        data,d=self.parity(['{}','{}'])
        with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(data),d,IDENTITY,{**INLINE,'canary':3})
    def test_21_section_reordering_is_rejected(self):
        data,d=self.parity(['','']);wrong=bytearray(data);wrong[72]=15
        with self.assertRaises(ref.ContractError):ref.decode(io.BytesIO(wrong),d,IDENTITY,INLINE)
    def test_22_complete_transport_does_not_promote_failed_semantics(self):
        data,d=self.parity(['{"ok":true}','{"classes":[]}'])
        hydrated=ref.hydrate({**INLINE,'diagnosticArtifact':d},data,d,IDENTITY)
        self.assertEqual(hydrated['result'],'Failed');self.assertEqual(hydrated['reportTransport'],'NativeBoundedSnapshotV2')
    def test_23_duplicate_json_keys_still_fail_semantic_input(self):
        data,d=self.parity(['{"ok":false,"ok":true}','{}'])
        with self.assertRaises(ref.ContractError):ref.hydrate({**INLINE,'diagnosticArtifact':d},data,d,IDENTITY)
    def test_24_nonfinite_json_is_not_accepted(self):
        data,d=self.parity(['{"value":NaN}','{}'])
        with self.assertRaises(ref.ContractError):ref.hydrate({**INLINE,'diagnosticArtifact':d},data,d,IDENTITY)

class PosixSink(unittest.TestCase):
    def invoke(self,mode,profile,setup=None):
        p=OUT/'cases'/f'posix-{len(RECORDS)}';p.mkdir(mode=0o700)
        if setup:setup(p)
        value=json.loads(run([OUT/f'posix-{profile}',mode,p]));return p,value
    def test_01_real_file_is_synced_and_retained(self):
        for profile in PROFILES:
            p,v=self.invoke('success',profile)
            self.assertTrue(v['ok'] and v['durable']);self.assertEqual(v['receiptBytes'],272)
            self.assertEqual((p/'diagnostics.v2').stat().st_size,272);self.assertEqual(v['syncCalls'],2)
    def test_02_existing_file_is_preserved(self):
        for profile in PROFILES:
            p,v=self.invoke('occupied',profile,lambda p:(p/'diagnostics.v2').write_bytes(b'preserved'))
            self.assertFalse(v['prepared']);self.assertEqual((p/'diagnostics.v2').read_bytes(),b'preserved')
    def test_03_symlink_target_is_never_written(self):
        def setup(p):
            (p/'target').write_bytes(b'preserved');(p/'diagnostics.v2').symlink_to(p/'target')
        for profile in PROFILES:
            p,v=self.invoke('symlink',profile,setup);self.assertFalse(v['prepared']);self.assertEqual((p/'target').read_bytes(),b'preserved')
    def test_04_group_accessible_directory_refused(self):
        for profile in PROFILES:
            p,v=self.invoke('group',profile,lambda p:p.chmod(0o750));self.assertFalse(v['prepared']);self.assertFalse((p/'diagnostics.v2').exists())
    def test_05_replacement_is_not_rebound(self):
        for profile in PROFILES:
            p,v=self.invoke('replaced',profile);self.assertFalse(v['ok']);self.assertEqual(v['receiptBytes'],0);self.assertTrue((p/'preserve.partial').exists())
    def test_06_link_mode_and_name_changes_fail(self):
        for mode in ('hardlink','mode-changed','deleted','prepare-twice'):
            for profile in PROFILES:
                p,v=self.invoke(mode,profile);self.assertFalse(v['ok']);self.assertFalse(v['durable']);self.assertEqual(v['receiptBytes'],0)
    def test_07_system_io_failures_do_not_return_descriptor(self):
        for mode in ('write-error','zero-write','repeated-eintr','file-sync-error','dir-sync-error','close-error'):
            for profile in PROFILES:
                p,v=self.invoke(mode,profile);self.assertFalse(v['ok']);self.assertFalse(v['durable']);self.assertEqual(v['receiptBytes'],0)
                self.assertTrue((p/'diagnostics.v2').exists())
    def test_08_partial_writes_and_single_eintr_handled(self):
        for mode in ('once-eintr','short-writes'):
            for profile in PROFILES:
                p,v=self.invoke(mode,profile);self.assertTrue(v['ok']);self.assertTrue(v['durable']);self.assertEqual(v['receiptBytes'],272)

def main():
    global OUT, ref
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    OUT=args.output
    if not __debug__:raise RuntimeError('optimization not permitted')
    if not OUT.is_absolute() or OUT!=OUT.resolve(strict=False) or OUT.exists() or not OUT.parent.is_dir():raise RuntimeError('unused canonical output required')
    if OUT==ROOT or ROOT in OUT.parents or OUT in ROOT.parents:raise RuntimeError('output must be outside sources')
    reference=(ROOT/REFERENCE).read_bytes()
    if blob(reference)!=REFERENCE_BLOB:raise RuntimeError('reference changed')
    spec=importlib.util.spec_from_file_location('reference_v2',ROOT/REFERENCE);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
    OUT.mkdir();(OUT/'commands').mkdir();(OUT/'cases').mkdir()
    original={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in HERE.glob('*') if p.is_file()}
    compiler=shutil.which(os.environ.get('CXX','clang++'))
    if not compiler:raise RuntimeError('clang++ or explicit CXX required')
    status='FailedOrIncomplete';count=0
    try:
        for profile in PROFILES:
            flags=['-O2'] if profile=='strict' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
            for stem,driver in [('codec','native_codec_driver.cpp'),('posix','posix_sink_driver.cpp')]:
                run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic',*flags,HERE/driver,'-o',OUT/f'{stem}-{profile}'])
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(NativeCodec),unittest.defaultTestLoader.loadTestsFromTestCase(PosixSink)])
        with (OUT/'tests.log').open('w') as log:
            result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        count=result.testsRun
        if not result.wasSuccessful():raise RuntimeError('native V2 tests failed: see tests.log')
        if count!=32 or result.skipped:raise RuntimeError('full suite required')
        if any(sha((ROOT/p).read_bytes())!=value for p,value in original.items()):raise RuntimeError('source changed')
        status='PassedWithinNativeComponentScope'
    finally:
        result={'kind':'R03NativeDiagnosticsV2ComponentTest','result':status,'tests':count,'commands':RECORDS,'sourceSha256':original,'referenceGitBlob':REFERENCE_BLOB,'platform':sys.platform,'leakDetection':('Enabled' if LEAK_CHECK else 'UnavailableInAppleRuntime'),'sanitizerEnvironment':{'ASAN_OPTIONS':ASAN,'UBSAN_OPTIONS':UBSAN},
                'notUnity':True,'actualProducerCaptureIntegrated':False,'envelopeTransactionIntegrated':False,'engineAdapterImplemented':False,'runtimeAcceptance':False}
        (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
        inventory=[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(OUT.rglob('*')) if p.is_file() and not p.is_symlink()]
        links=[{'path':str(p.relative_to(OUT)),'target':os.readlink(p)} for p in sorted(OUT.rglob('*')) if p.is_symlink()]
        (OUT/'MANIFEST.json').write_text(json.dumps({'files':inventory,'testOwnedSymlinks':links},indent=2)+'\n')
    print(json.dumps({'result':status,'tests':count,'processRecords':len(RECORDS)},indent=2))

if __name__=='__main__':main()
