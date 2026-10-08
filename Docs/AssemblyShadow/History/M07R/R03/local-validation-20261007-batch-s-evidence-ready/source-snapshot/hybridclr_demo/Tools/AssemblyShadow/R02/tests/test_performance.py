import copy
import unittest
from evidence import EvidenceError
from performance import schedule, validate_schedule, verify_intervals
class PerformanceTests(unittest.TestCase):
    def test_schedule_is_deterministic_and_balanced(self):
        value=schedule();pairs=validate_schedule(value);self.assertEqual(len(pairs),44)
        self.assertEqual([p['phase'] for p in pairs[:4]],['pilot']*4)
        for mode in {p['mode'] for p in pairs}:
            rows=[p for p in pairs if p['mode']==mode and p['phase']=='formal']
            self.assertEqual(len(rows),10);self.assertEqual(sum(r['order']==['A','B'] for r in rows),5)
    def test_modified_protocol_rejected(self):
        value=schedule();value['ratioResolutionTicks']=1
        with self.assertRaises(EvidenceError):validate_schedule(value)
    def valid(self):
        expected=schedule()['pairs'];rows=[];clock=100
        for p in expected:
            row=dict(p,result='Passed',sides={})
            for side in p['order']:
                row['sides'][side]=dict(startedAtUnix=clock,endedAtUnix=clock+1,runId=str(clock));clock+=2
            rows.append(row)
        return rows,expected
    def test_complete_series_intervals(self):
        rows,expected=self.valid();self.assertEqual(len(verify_intervals(rows,expected)),88)
    def test_duplicate_nonce_rejected(self):
        rows,e=self.valid();rows[1]['sides']['A']['runId']=rows[0]['sides']['A']['runId']
        with self.assertRaises(EvidenceError):verify_intervals(rows,e)
    def test_overlap_rejected(self):
        rows,e=self.valid();rows[1]['sides']['A']['startedAtUnix']=1
        with self.assertRaises(EvidenceError):verify_intervals(rows,e)
    def test_failed_pair_rejected(self):
        rows,e=self.valid();rows[1]['result']='Failed'
        with self.assertRaises(EvidenceError):verify_intervals(rows,e)
    def test_partial_series_rejected(self):
        rows,e=self.valid()
        with self.assertRaises(EvidenceError):verify_intervals(rows[:-1],e)
