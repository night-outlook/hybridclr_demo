import json
import tempfile
import unittest
from pathlib import Path
import h1_selection_collect as c
import h1_successor_evidence as h

class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.roles={}
        for role in h.SINGLE_ROLES:
            p=self.root/(role+'.json');p.write_text('{}');self.roles[role]=str(p)
        for role,count in h.MULTI_ROLES.items():
            values=[]
            for i in range(count):
                p=self.root/(role+'-'+str(i)+'.json');p.write_text('{}');values.append(str(p))
            self.roles[role]=values
        self.request={'schemaVersion':1,'kind':'H1SuccessorCollectionRequest','chainId':'synthetic','allowedRoots':[str(self.root)],'roles':self.roles}
    def tearDown(self):self.temp.cleanup()
    def test_collect_structural_roles_without_claiming_runtime_pass(self):
        s=c.collect(self.request);self.assertEqual(len(h.SINGLE_ROLES)+sum(h.MULTI_ROLES.values()),len(s['artifacts']))
    def test_nested_retained_path_preferred_over_mutable_source(self):
        p=self.root/'retained-source.bin';p.write_text('source')
        Path(self.roles['source-equivalence']).write_text(json.dumps({'source':{'path':'/missing/live/source.cs','retainedPath':str(p),'sha256':h.digest(p)}}))
        s=c.collect(self.request);self.assertIn(str(p),[r['rawPath'] for r in s['artifacts']])
    def test_locator_map_preserves_raw_receipt(self):
        p=self.root/'capture.json';p.write_text('{}');raw='external-artifact://test/capture.json'
        self.request['locatorMap']={raw:str(p)}
        Path(self.roles['source-equivalence']).write_text(json.dumps({'path':raw,'sha256':h.digest(p)}))
        row=next(r for r in c.collect(self.request)['artifacts'] if r['rawPath']==raw)
        self.assertEqual(str(p),row['localPath'])
    def test_unresolved_locator_blocks(self):
        Path(self.roles['source-equivalence']).write_text(json.dumps({'path':'external-artifact://missing','sha256':'0'*64}))
        with self.assertRaises(h.EvidenceUnavailable):c.collect(self.request)
    def test_tampered_referenced_hash(self):
        Path(self.roles['source-equivalence']).write_text(json.dumps({'path':self.roles['startup-launches'],'sha256':'0'*64}))
        with self.assertRaisesRegex(ValueError,'hash|bytes'):c.collect(self.request)
    def test_assert_termination_missing_managed_result_is_not_collected(self):
        refs=list(c.refs({'classification':'AssertAbort','crashed':True,'rawResultPath':'missing','rawLaunchPath':'launch','rawUnityLogPath':'log'}))
        self.assertEqual([('launch',None),('log',None)],refs)
    def test_positive_reproduction_requires_raw_result(self):
        self.assertIn(('result',None),list(c.refs({'classification':'UnexpectedAccepted','rawResultPath':'result'})))
    def test_repeated_reference_with_different_hash_rejected(self):
        Path(self.roles['source-equivalence']).write_text(json.dumps([{'path':self.roles['startup-launches'],'sha256':h.digest(Path(self.roles['startup-launches']))},{'path':self.roles['startup-launches'],'sha256':'a'*64}]))
        with self.assertRaises(ValueError):c.collect(self.request)
    def test_empty_roots_rejected(self):
        self.request['allowedRoots']=[]
        with self.assertRaises(ValueError):c.collect(self.request)
    def test_cannot_exclude_required_role(self):
        self.request['notPackaged']=[{'rawPath':self.roles['startup-launches'],'sha256':'0'*64,'sizeBytes':1,'artifactClass':'NativeBinary','reason':'test'}]
        with self.assertRaisesRegex(ValueError,'Mandatory'):c.collect(self.request)

if __name__ == '__main__': unittest.main()
