import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import h1_local_batch as batch
import h1_replay_batch as replay
from test_h1_pdb_constant_audit import fixture


class ReplayBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.capture=self.root/'failure-one';self.capture.mkdir()
        rows=[]
        for role,name,data in [('pe','input.dll',b'synthetic-pe'),('pdb','input.pdb',fixture()),('configuration','configuration.json',b'{}')]:
            (self.capture/name).write_bytes(data);rows.append({'role':role,'path':name,'sha256':hashlib.sha256(data).hexdigest(),'sizeBytes':len(data)})
        (self.capture/'capture.json').write_text(json.dumps({'schemaVersion':1,'kind':'ReflectionBindingFailureCapture','files':rows,'missingReferences':[]}))
    def tearDown(self):self.temp.cleanup()
    def test_generates_replay_and_audit_tasks(self):
        plan=replay.make_plan(self.root);self.assertEqual(2,len(plan['tasks']));batch.validate(plan)
    def test_no_capture_does_not_guess_another_root(self):
        other=self.root/'empty';other.mkdir()
        with self.assertRaises(batch.BatchError):replay.make_plan(other)
    def test_hash_tamper_rejected(self):
        (self.capture/'input.dll').write_bytes(b'changed')
        with self.assertRaises(batch.BatchError):replay.make_plan(self.root)
    def test_all_capture_directories_are_included(self):
        import shutil
        shutil.copytree(self.capture,self.root/'failure-two');self.assertEqual(4,len(replay.make_plan(self.root)['tasks']))
    def test_legacy_failure_does_not_hide_a_valid_A_route(self):
        out=self.root/'replay';out.mkdir()
        manifest_hash=replay.digest(self.capture/'capture.json')
        for mode in replay.MODES:
            row={'kind':'ReflectionBindingFailureReplay','mode':mode,'captureManifestSha256':manifest_hash,'result':'Failed','exception':'Synthetic legacy writer failure'}
            if mode=='compiler-references':
                pe=b'emitted';pdb=fixture();(out/(mode+'.dll')).write_bytes(pe);(out/(mode+'.pdb')).write_bytes(pdb)
                row.update(result='EmittedAndVerified',peSha256=hashlib.sha256(pe).hexdigest(),pdbSha256=hashlib.sha256(pdb).hexdigest())
            (out/(mode+'.json')).write_text(json.dumps(row))
        result=replay.audit_replay(self.capture,out);self.assertEqual(['compiler-references'],result['availableRoutes']);self.assertFalse(result['routeAutomaticallySelected'])
    def test_unavailable_reference_is_not_a_pass(self):
        path=self.capture/'capture.json';value=json.loads(path.read_text());value['missingReferences']=['missing.dll'];path.write_text(json.dumps(value))
        with self.assertRaises(batch.BatchError):replay.make_plan(self.root)


if __name__=='__main__':unittest.main()
