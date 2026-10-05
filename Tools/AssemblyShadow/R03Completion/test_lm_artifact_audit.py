"""Adversarial tests of the read-only artifact authenticator, not Player evidence."""
import copy
import io
import json
import stat
import unittest
import warnings
import zipfile
from ci_artifact_audit import authenticate, digest

SOURCE = '1' * 40
PACKAGE = '2' * 40


def payload(change=None, extra=None, duplicate=False, symlink=False):
    receipt = {'exitCode':0,'remainingProcessGroup':False,'postCleanupGroupExists':False,'timeout':False,'interrupted':False,'startError':None,'cleanupErrors':[],
               'stdoutSha256':digest(b''),'stderrSha256':digest(b'')}
    if change:
        receipt.update(change)
    files = {'commands/0001/command.json':json.dumps(receipt).encode(), 'commands/0001/stdout.log':b'', 'commands/0001/stderr.log':b'',
             'results.json':json.dumps({'result':'Passed','cases':[{'id':'P01','result':'Passed'}]}).encode()}
    provenance = {'sourceCommit':SOURCE,'repositories':{'hybridclr_demo':SOURCE,'hybridclr_unity':PACKAGE},
                  'files':[{'path':k,'size':len(v),'sha256':digest(v)} for k,v in files.items()]}
    files['provenance.json'] = json.dumps(provenance).encode()
    if extra:
        files.update(extra)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer,'w') as archive:
        for name,data in files.items():
            archive.writestr(name,data)
        if duplicate:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');archive.writestr('results.json',files['results.json'])
        if symlink:
            entry=zipfile.ZipInfo('link');entry.create_system=3;entry.external_attr=(stat.S_IFLNK|0o777)<<16;archive.writestr(entry,'target')
    return buffer.getvalue()


class ArtifactAuditTests(unittest.TestCase):
    def check_bad(self, raw, message, source=SOURCE, package=PACKAGE, expected=None):
        with self.assertRaisesRegex(ValueError,message):
            authenticate(raw,expected or digest(raw),source,package)
    def test_complete_archive_passes(self):
        raw=payload();result,_=authenticate(raw,digest(raw),SOURCE,PACKAGE)
        self.assertEqual((result['indexedFiles'],result['zipFiles']),(4,5))
        self.assertEqual(len(result['commands']),1)
    def test_wrong_digest_rejected(self):self.check_bad(payload(),'Archive digest',expected='0'*64)
    def test_wrong_source_rejected(self):self.check_bad(payload(),'Artifact source',source='3'*40)
    def test_wrong_package_rejected(self):self.check_bad(payload(),'Repository source tuple',package='3'*40)
    def test_unindexed_member_rejected(self):self.check_bad(payload(extra={'extra':b'x'}),'Exact index membership')
    def test_changed_indexed_member_rejected(self):self.check_bad(payload(extra={'commands/0001/stdout.log':b'x'}),'Indexed bytes')
    def test_duplicate_zip_member_rejected(self):self.check_bad(payload(duplicate=True),'Duplicate archive member')
    def test_traversal_rejected(self):self.check_bad(payload(extra={'../outside':b'x'}),'Unsafe archive path')
    def test_symlink_rejected(self):self.check_bad(payload(symlink=True),'Archive symlink')
    def test_nonzero_command_rejected(self):self.check_bad(payload(change={'exitCode':1}),'Clean successful')
    def test_survivor_rejected(self):self.check_bad(payload(change={'remainingProcessGroup':True}),'Clean successful')
    def test_timeout_rejected(self):self.check_bad(payload(change={'timeout':True}),'Clean successful')
    def test_stream_binding_rejected(self):self.check_bad(payload(change={'stdoutSha256':'0'*64}),'Command stream')

if __name__ == '__main__':unittest.main()
