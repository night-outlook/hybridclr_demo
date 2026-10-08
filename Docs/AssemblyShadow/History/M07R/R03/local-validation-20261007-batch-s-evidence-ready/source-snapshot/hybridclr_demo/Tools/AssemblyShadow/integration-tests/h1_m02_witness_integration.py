"""Run in the complete candidate checkout; exercises the real M02 verifier through its exact H1 parser extension."""
import copy
import json
import sys
import unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import m02_results as m02
import h1_m02_results as h1m02
import h1_witness_contract as witness

class RealM02WitnessIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h1m02.install()
        cls.path=TOOLS.parents[1]/'ProjectSettings/AssemblyShadowReflectionBindings.json'
        cls.config=json.loads(cls.path.read_text(encoding='utf-8'))
        witness.expected_site_ids(cls.config,require_current=True)
    def parse(self,value):return m02._reflection_parse(self.path,json.dumps(value).encode())
    def test_current_six_site_configuration_is_parsed_by_real_M02(self):
        result=self.parse(self.config);self.assertEqual(6,len(result['declarations']))
    def test_historical_five_site_configuration_remains_readable(self):
        value=copy.deepcopy(self.config);value['sites']=[s for s in value['sites'] if s['id']!=witness.SITE_ID]
        self.assertEqual(5,len(self.parse(value)['declarations']))
    def test_wrong_H1_method_hash_is_not_automatically_admitted(self):
        value=copy.deepcopy(self.config);next(s for s in value['sites'] if s['id']==witness.SITE_ID)['originalMethodHash']='0'*64
        with self.assertRaises(m02.VerificationError):self.parse(value)
    def test_wrong_H1_operation_index_rejected(self):
        value=copy.deepcopy(self.config);next(s for s in value['sites'] if s['id']==witness.SITE_ID)['operationIndex']=26
        with self.assertRaises(m02.VerificationError):self.parse(value)
    def test_missing_declared_variant_rejected(self):
        value=copy.deepcopy(self.config);next(s for s in value['sites'] if s['id']==witness.SITE_ID)['additionalMethodVariants']=[]
        with self.assertRaises(m02.VerificationError):self.parse(value)
    def test_duplicate_site_rejected(self):
        value=copy.deepcopy(self.config);value['sites'].append(copy.deepcopy(value['sites'][-1]))
        with self.assertRaises(m02.VerificationError):self.parse(value)
    def test_unknown_extra_site_rejected(self):
        value=copy.deepcopy(self.config);s=copy.deepcopy(value['sites'][-1]);s['id']='unapproved';value['sites'].append(s)
        with self.assertRaises(m02.VerificationError):self.parse(value)
    def test_duplicate_JSON_key_rejected(self):
        raw=json.dumps(self.config);raw=raw.replace('"schemaVersion": 4','"schemaVersion": 4, "schemaVersion": 4',1)
        with self.assertRaises(m02.VerificationError):m02._reflection_parse(self.path,raw.encode())

if __name__=='__main__':unittest.main()
