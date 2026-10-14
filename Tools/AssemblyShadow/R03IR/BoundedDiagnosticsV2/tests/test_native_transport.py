#!/usr/bin/env python3
"""Actual native encoder/transaction tests versus the pinned independent V2 reference.

Compiles real native components, does real POSIX file I/O and parses their bytes.
This never loads Unity, captures runtime metadata, or approves semantic acceptance.
"""
from __future__ import annotations
import argparse
import copy
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
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
sys.path.insert(0, str(SOURCE))
import read_transaction as reader

REF_BLOB = '0866b07f758a20284d2a5d5d933b2be577b20b50'
W = None
OUT = None
BINARIES = []
COMMANDS = []
NEXT = 0
IDENTITY = {'runId':'native-v2-6d42','caseId':'contract','requestSha256':'a'*64,
            'buildSha256':'b'*64,'processId':1234,
            **{k:'c'*40 for k in ('demoCommit','hybridclrCommit','packageCommit','nativeCommit')}}
INLINE = {'reportTransport':'NativeBoundedSnapshotV2','result':'Failed','primitiveValue':2,
          'firstFailure':13,'unicode':'\u03a9'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def execute(argv, location):
    location.mkdir(parents=True, exist_ok=False)
    begin = time.time_ns()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
               ASAN_OPTIONS=('detect_leaks=0:abort_on_error=1' if sys.platform=='darwin' else 'detect_leaks=1:abort_on_error=1'),
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    p = subprocess.run([str(x) for x in argv], capture_output=True, timeout=40, env=env)
    (location/'stdout').write_bytes(p.stdout); (location/'stderr').write_bytes(p.stderr)
    record = {'argv':[str(x) for x in argv], 'cwd':str(Path.cwd()),
              'startUnixNs':begin, 'endUnixNs':time.time_ns(), 'exit':p.returncode,
              'stdoutSha256':sha(p.stdout), 'stderrSha256':sha(p.stderr),
              'ASAN_OPTIONS':env['ASAN_OPTIONS'],'UBSAN_OPTIONS':env['UBSAN_OPTIONS']}
    (location/'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
    COMMANDS.append(record)
    return p

def run_case(profile, mode='ok', fields=None, inline=None, prepare=None):
    global NEXT
    NEXT += 1
    root = OUT / f'case-{NEXT:04d}-{profile[0]}-{mode}'
    root.mkdir()
    owned = root/'owned'; owned.mkdir(mode=0o700); owned.chmod(0o700)
    fields = (b'{"classes":"'+b'a'*400000+b'"}', b'{"execution":"'+b'b'*350000+b'"}') if fields is None else fields
    names = []
    for i, data in enumerate(fields):
        if data is None:
            names.append('-')
        else:
            p = root/f'field-{i+14}'; p.write_bytes(data); names.append(str(p))
    incoming = W.canonical(INLINE if inline is None else inline)
    (root/'inline').write_bytes(incoming)
    actual_path = prepare(owned) if prepare else owned
    args = [profile[1], mode, actual_path, *names, root/'inline', W.binding(IDENTITY).hex()]
    p = execute(args, root/'command')
    try:
        info = json.loads(p.stdout)
    except Exception as exc:
        raise AssertionError(f'Native process failed without result: {p.returncode} {p.stderr[:1000]!r}') from exc
    if info['newCallsInComponent'] != 0:
        raise AssertionError('A new allocation happened inside the guarded native component')
    return root, owned, p, info, fields

class NativeTests(unittest.TestCase):
    def assertSuccess(self, row, inline=None, semantic=True):
        root, owned, p, info, fields = row
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(info['ok']); self.assertTrue(info['receipt']['committed'])
        self.assertEqual(info['error'], 0)
        self.assertLessEqual(info['largestWrite'], W.CHUNK)
        mapped = {k:(None if data is None else data.decode('utf-8')) for k,data in zip(W.FIELDS,fields)}
        values = INLINE if inline is None else inline
        expected, desc = W.encode(IDENTITY, values, mapped)
        actual = (owned/'diagnostics.v2.bin').read_bytes()
        self.assertEqual(actual, expected, 'Native encoder differs from independently pinned wire spec')
        envelope = json.loads((owned/'raw.v2.json').read_bytes())
        self.assertEqual(envelope['diagnosticArtifact'], desc)
        decoded = W.decode(io.BytesIO(actual), desc, IDENTITY, values)
        self.assertEqual(decoded, mapped)
        self.assertLessEqual(len(actual)+len((owned/'raw.v2.json').read_bytes()), W.TOTAL)
        if semantic:
            result = reader.read_transaction(owned, info['receipt'], IDENTITY, W)
            self.assertEqual(result.report, {**values, **mapped})
            self.assertFalse(result.semantic_acceptance)
        return owned, info, desc

    def test_two_complete_fields_exceeding_old_slot(self):
        for profile in BINARIES:
            with self.subTest(profile=profile[0]):
                self.assertSuccess(run_case(profile))

    def test_utf8_spans_frame_and_capture_append_boundaries(self):
        a=json.dumps({'v':'a'*65524+'\U0001f34a'*120000},ensure_ascii=False).encode()
        b=json.dumps({'v':'\u4e2d\u6587'*70000},ensure_ascii=False).encode()
        for profile in BINARIES:self.assertSuccess(run_case(profile,fields=(a,b)))

    def test_null_and_json_text_null_are_distinct(self):
        for fields in ((None,b'null'),(b'null',None),(None,None)):
            for profile in BINARIES:self.assertSuccess(run_case(profile,fields=fields))

    def test_empty_and_embedded_nul_lossless_wire_not_semantics(self):
        for profile in BINARIES:
            row=run_case(profile,fields=(b'',b'x\0y'))
            owned,info,_=self.assertSuccess(row,semantic=False)
            with self.assertRaises((reader.TransactionError,ValueError)):
                reader.read_transaction(owned,info['receipt'],IDENTITY,W)

    def test_sha256_vectors_and_incremental_updates(self):
        vectors=(b'',b'abc',b'a'*1000000,bytes(range(256))*1000)
        for profile in BINARIES:
            for number,value in enumerate(vectors):
                directory=OUT/f'hash-{profile[0]}-{number}'; directory.mkdir()
                (directory/'input').write_bytes(value)
                p=execute([profile[1],'hash',directory/'input'],directory/'command')
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(p.stdout.decode().strip(),sha(value))

    def test_exact_aggregate_boundary_and_one_byte_over(self):
        lo,hi=0,W.MAX_STREAM
        while lo<hi:
            mid=(lo+hi+1)//2
            size=192+mid+2+38*((mid+65535)//65536+1)
            if size<=W.MAX_STREAM:lo=mid
            else:hi=mid-1
        for profile in BINARIES:
            values=(b'"'+b'a'*(lo-2)+b'"',b'{}')
            self.assertSuccess(run_case(profile,fields=values))
            row=run_case(profile,fields=(values[0]+b' ',values[1]))
            self.assertEqual(row[2].returncode,3)
            self.assertEqual(row[3]['error'],3)
            self.assertFalse(row[3]['receipt']['committed'])

    def test_inline_reserve_not_increased(self):
        for profile in BINARIES:
            row=run_case(profile,fields=(b'{}',b'{}'),inline={**INLINE,'padding':'x'*W.RESERVE})
            self.assertEqual(row[2].returncode,3)
            self.assertFalse(row[3]['receipt']['committed'])

    def test_exact_inline_bound_is_retained(self):
        inline={**INLINE,'padding':''}
        inline['padding']='x'*(W.RESERVE-4096-len(W.canonical(inline)))
        self.assertEqual(len(W.canonical(inline)),W.RESERVE-4096)
        for profile in BINARIES:self.assertSuccess(run_case(profile,fields=(b'{}',b'{}'),inline=inline),inline=inline)

    def test_changed_inline_is_not_committed(self):
        for profile in BINARIES:
            row=run_case(profile,'mutate_inline')
            self.assertEqual(row[3]['error'],11)
            self.assertFalse(row[3]['receipt']['committed'])

    def test_special_mode_bits_are_not_ignored(self):
        for profile in BINARIES:
            def sgid(directory):directory.chmod(0o2700);return directory
            self.assertEqual(run_case(profile,prepare=sgid)[3]['error'],6)

    def test_capture_order_missing_and_write_after_freeze_fail(self):
        for profile in BINARIES:
            for mode in ('wrong_order','missing_section','late_append','mutate_before'):
                with self.subTest(profile=profile[0],mode=mode):
                    row=run_case(profile,mode)
                    self.assertEqual(row[2].returncode,3)
                    self.assertEqual(row[3]['error'],1)
                    self.assertFalse(row[3]['receipt']['committed'])

    def test_invalid_utf8_is_not_replaced(self):
        for profile in BINARIES:
            for value in (b'\xc0\x80',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\xe2\x82'):
                row=run_case(profile,fields=(value,b'{}'))
                self.assertEqual(row[3]['error'],4)
                self.assertFalse(row[3]['receipt']['committed'])

    def test_each_physical_write_sync_close_fault_fails_closed(self):
        modes={'write_fail':5,'write_zero':5,'persistent_eintr':5,'raw_write_fail':5,
               'sync_artifact':9,'sync_directory_first':9,'sync_raw':9,'sync_directory_final':9,
               'close_artifact':10,'close_raw':10}
        for profile in BINARIES:
            for mode,error in modes.items():
                with self.subTest(profile=profile[0],mode=mode):
                    row=run_case(profile,mode)
                    self.assertEqual(row[2].returncode,3)
                    self.assertEqual(row[3]['error'],error)
                    self.assertFalse(row[3]['receipt']['committed'])
                    self.assertTrue((row[1]/'diagnostics.v2.bin').exists(),'Failed output was deleted')
                    self.assertTrue((row[1]/'raw.v2.json').exists(),'Failed output was deleted')

    def test_short_write_and_bounded_eintr_preserve_exact_bytes(self):
        for profile in BINARIES:
            for mode in ('short_write','write_eintr'):
                self.assertSuccess(run_case(profile,mode,fields=(b'{"x":123}',b'{}')))

    def test_durability_order(self):
        for profile in BINARIES:
            row=run_case(profile)
            _,info,_=self.assertSuccess(row)
            events=info['events']
            self.assertRegex(events,r'^W+SCSW+SCS$')

    def test_frozen_capture_mutated_during_sink_is_rejected(self):
        for profile in BINARIES:
            row=run_case(profile,'mutate_during')
            self.assertEqual(row[3]['error'],11)
            self.assertFalse(row[3]['receipt']['committed'])

    def test_duplicate_commit_never_creates_second_success(self):
        for profile in BINARIES:
            row=run_case(profile,'repeat_commit')
            self.assertEqual(row[2].returncode,3)
            self.assertEqual(row[3]['error'],1)
            self.assertFalse(row[3]['receipt']['committed'])

    def test_existing_artifact_and_envelope_are_not_overwritten(self):
        for profile in BINARIES:
            for name in ('diagnostics.v2.bin','raw.v2.json'):
                def prep(directory):
                    (directory/name).write_bytes(b'original');return directory
                row=run_case(profile,prepare=prep)
                self.assertEqual(row[3]['error'],8)
                self.assertEqual((row[1]/name).read_bytes(),b'original')

    def test_noncanonical_alias_and_wrong_mode_rejected(self):
        for profile in BINARIES:
            def alias(directory):
                link=directory.parent/'alias';link.symlink_to(directory,target_is_directory=True);return link
            self.assertEqual(run_case(profile,prepare=alias)[3]['error'],7)
            def public(directory):directory.chmod(0o755);return directory
            self.assertEqual(run_case(profile,prepare=public)[3]['error'],6)
            def dotdot(directory):return str(directory)+'/../owned'
            self.assertEqual(run_case(profile,prepare=dotdot)[3]['error'],7)

    def test_ancestor_replacement_and_file_link_races_rejected(self):
        for profile in BINARIES:
            for mode in ('rename_directory','replace_artifact','hardlink_artifact','change_owner_mode'):
                row=run_case(profile,mode)
                self.assertEqual(row[3]['error'],11)
                self.assertFalse(row[3]['receipt']['committed'])
                if mode=='replace_artifact':self.assertEqual((row[1]/'sentinel').read_bytes(),b'preserve')

    def test_failed_report_never_becomes_passed(self):
        row=run_case(BINARIES[0])
        owned,info,_=self.assertSuccess(row)
        result=reader.read_transaction(owned,info['receipt'],IDENTITY,W)
        self.assertEqual(result.report['result'],'Failed')
        self.assertFalse(result.semantic_acceptance)

    def test_reader_requires_independent_commit_receipt(self):
        row=run_case(BINARIES[0]);owned,info,_=self.assertSuccess(row)
        for key,value in (('committed',False),('artifactBytes',True),('envelopeHash','x'*64),
                          ('directoryInode',info['receipt']['directoryInode']+1)):
            bad=dict(info['receipt']);bad[key]=value
            with self.subTest(key=key),self.assertRaises((reader.TransactionError,OSError)):
                reader.read_transaction(owned,bad,IDENTITY,W)

    def test_wrong_pid_request_or_source_binding_rejected(self):
        row=run_case(BINARIES[0]);owned,info,_=self.assertSuccess(row)
        for key,value in (('processId',1235),('requestSha256','d'*64),('nativeCommit','d'*40)):
            identity=dict(IDENTITY);identity[key]=value
            with self.assertRaises(W.ContractError):reader.read_transaction(owned,info['receipt'],identity,W)

    def test_reader_detects_corruption_truncation_or_trailing_bytes(self):
        for mode in ('corrupt','truncate','trailing'):
            row=run_case(BINARIES[0]);owned,info,_=self.assertSuccess(row)
            file=owned/'diagnostics.v2.bin';original=file.read_bytes()
            value=(original[:100]+bytes([original[100]^1])+original[101:] if mode=='corrupt'
                   else original[:-1] if mode=='truncate' else original+b'x')
            file.write_bytes(value)
            with self.assertRaises(reader.TransactionError):reader.read_transaction(owned,info['receipt'],IDENTITY,W)

    def test_reader_rejects_hardlink_and_symlink(self):
        for mode in ('hard','sym'):
            row=run_case(BINARIES[0]);owned,info,_=self.assertSuccess(row)
            file=owned/'diagnostics.v2.bin'
            if mode=='hard':os.link(file,owned/'duplicate')
            else:file.rename(owned/'original');file.symlink_to('original')
            with self.assertRaises((reader.TransactionError,OSError)):reader.read_transaction(owned,info['receipt'],IDENTITY,W)

    def test_reader_detects_ancestor_change_during_read(self):
        row=run_case(BINARIES[0]);owned,info,_=self.assertSuccess(row)
        original=os.read;done=False
        def raced(fd,n):
            nonlocal done
            value=original(fd,n)
            if not done:
                done=True;owned.rename(owned.with_suffix('.moved'));owned.mkdir(mode=0o700)
            return value
        with patch.object(reader.os,'read',raced),self.assertRaises(reader.TransactionError):
            reader.read_transaction(owned,info['receipt'],IDENTITY,W)

    def test_strict_json_no_duplicates_nonfinite_or_excess_depth(self):
        for payload in (b'{"a":1,"a":2}',b'{"n":NaN}',b'{"n":1e999}',b'['*65+b'0'+b']'*65):
            row=run_case(BINARIES[0],fields=(payload,b'{}'))
            owned,info,_=self.assertSuccess(row,semantic=False)
            with self.assertRaises(reader.TransactionError):reader.read_transaction(owned,info['receipt'],IDENTITY,W)

    def test_independent_decoder_rejects_frame_reorder_and_footer(self):
        row=run_case(BINARIES[0]);owned,info,desc=self.assertSuccess(row)
        source=(owned/'diagnostics.v2.bin').read_bytes()
        for position in (72,112,118,len(source)-1):
            modified=source[:position]+bytes([source[position]^1])+source[position+1:]
            expected=dict(desc);expected['sha256']=sha(modified)
            with self.assertRaises(W.ContractError):W.decode(io.BytesIO(modified),expected,IDENTITY,INLINE)


def main():
    global W, OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    data=args.reference.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=REF_BLOB:raise RuntimeError('Wrong independently pinned wire reference')
    spec=importlib.util.spec_from_file_location('diagnostic_stream',args.reference)
    W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
    OUT=args.output
    if not OUT.is_absolute() or OUT!=OUT.resolve(strict=False) or OUT.exists() or not OUT.parent.is_dir():
        raise RuntimeError('Fresh canonical external output required')
    if SOURCE in OUT.parents or HERE in OUT.parents:raise RuntimeError('Output cannot be source')
    OUT.mkdir()
    compiler=shutil.which('clang++')
    if not compiler:raise RuntimeError('clang++ required')
    for name,extra in (('strict',[]),('sanitized',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])):
        binary=OUT/('native-'+name)
        compile_argv=[compiler,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic',*extra,
              str(HERE/'native_transport_harness.cpp'),'-o',str(binary)]
        p=execute(compile_argv,OUT/('compile-'+name))
        if p.returncode:raise RuntimeError(p.stderr.decode())
        BINARIES.append((name,binary))
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(NativeTests)
    with (OUT/'tests.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    source_paths=[SOURCE/'BoundedDiagnosticsV2.h',SOURCE/'NativeArtifactTransaction.h',
                  SOURCE/'read_transaction.py',HERE/'native_transport_harness.cpp',Path(__file__),args.reference]
    records=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in source_paths]
    (OUT/'sources').mkdir()
    for p in source_paths:shutil.copyfile(p,OUT/'sources'/p.name)
    report={'kind':'NativeBoundedDiagnosticsComponentEvidence','passed':result.wasSuccessful(),
            'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'skips':len(result.skipped),'compilerAndProcessRecords':len(COMMANDS),
            'nativeVersion':'R03BoundedDiagnosticsV2','source':records,
            'commands':COMMANDS,'sourceReferenceBlob':REF_BLOB,
            'actualPOSIXIO':True,'actualNativeEncoder':True,'actualRuntimeMetadata':False,
            'unityLaunched':False,'semanticAcceptance':False,'schedulerAdapterImplemented':False}
    (OUT/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    links=[{'path':str(p.relative_to(OUT)),'target':os.readlink(p)} for p in sorted(OUT.rglob('*')) if p.is_symlink()]
    (OUT/'LINKS.json').write_text(json.dumps({'links':links},indent=2)+'\n')
    manifest=[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
              for p in sorted(OUT.rglob('*')) if p.is_file() and not p.is_symlink()]
    (OUT/'MANIFEST.json').write_text(json.dumps({'files':manifest},indent=2)+'\n')

    # Archive the test-owned negative symlinks verbatim, never follow them.
    import tarfile
    entries=sorted(OUT.rglob('*'))
    with tarfile.open(OUT/'TEST_EVIDENCE.tar.gz','w:gz',dereference=False) as tar:
        for p in entries:tar.add(p,arcname=str(p.relative_to(OUT)),recursive=False)
    print((OUT/'tests.log').read_text())
    print(json.dumps({k:v for k,v in report.items() if k not in ('commands','source')},indent=2))
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
