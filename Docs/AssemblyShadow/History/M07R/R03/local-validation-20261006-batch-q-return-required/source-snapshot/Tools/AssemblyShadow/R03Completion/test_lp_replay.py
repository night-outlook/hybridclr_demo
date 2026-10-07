"""The immutable P corpus is replayed without launching or reclassifying Players."""
from pathlib import Path
import unittest
import lp_replay


class OriginalPResourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = lp_replay.replay(Path(__file__).resolve().parents[3])

    def test_all_seventeen_failed_schema_boundaries_now_pass_resource_observations(self):
        failed = [r for r in self.result['cases'] if r['originalState'] == 'Failed']
        self.assertEqual(len(failed), 17)
        self.assertTrue(all("unknown=['r02']" in r['originalSchemaError'] for r in failed))
        self.assertTrue(all(r['resourceObservationReplay'] == 'Passed' for r in failed))
        self.assertEqual(self.result['typeInfoObjects'], 289)

    def test_original_off_contract_is_not_projected(self):
        off = [r for r in self.result['cases'] if r['originalState'] == 'Passed']
        self.assertEqual(len(off), 1)
        self.assertEqual(off[0]['typeInfoBridge']['verifiedTypeInfoObjects'], 0)
        self.assertIsNone(off[0]['originalSchemaError'])

    def test_historical_verdict_and_evidence_limits_remain_explicit(self):
        self.assertEqual(self.result['historicalPResult'], 'ReturnRequired')
        for key in ('historicalEvidenceModified', 'unityRun', 'playerRun', 'runtimeAcceptance', 'R03Accepted', 'H2Passed'):
            self.assertIs(self.result[key], False)
        self.assertEqual(self.result['verifiedInputFiles'], 40)
        self.assertEqual(len({r['processId'] for r in self.result['cases']}), 18)


if __name__ == '__main__': unittest.main()
