import unittest
import legacy_scope as scope


class FakeCase(unittest.TestCase):
    def __init__(self, name):
        super().__init__(); self.name = name
    def id(self): return self.name


class LegacyScope(unittest.TestCase):
    def make(self):
        return [FakeCase(name) for name in sorted(scope.PINNED_POSITIVES)] + [FakeCase('current.' + str(i)) for i in range(381)]

    def test_partition_preserves_all_original_tests_without_overlap(self):
        current = {t.id() for t in scope.leaves(scope.select(unittest.TestSuite(self.make()), 'current'))}
        old = {t.id() for t in scope.leaves(scope.select(unittest.TestSuite(self.make()), 'historical'))}
        self.assertEqual(len(current), 381); self.assertEqual(len(old), 6)
        self.assertFalse(current & old); self.assertEqual(len(current | old), 387)

    def test_inventory_drift_is_not_silently_filtered(self):
        with self.assertRaises(ValueError):scope.select(unittest.TestSuite(self.make()[:-1]), 'current')

    def test_duplicate_or_missing_pinned_test_rejected(self):
        items = self.make();items[0] = items[-1]
        with self.assertRaises(ValueError):scope.select(unittest.TestSuite(items), 'current')

    def test_unknown_scope_rejected(self):
        with self.assertRaises(ValueError):scope.select(unittest.TestSuite(self.make()), 'other')

    def test_fixed_fixture_is_explicit_not_head(self):
        self.assertEqual(scope.H1_CHECKPOINT, '2cbf68658a5b73189930fcdfe250835b72639515')
        self.assertIn('shadow_tools.py', scope.FIXTURE_EQUIVALENCE)
        self.assertIn('h1_historical_reanalysis.py', scope.FIXTURE_EQUIVALENCE)


if __name__ == '__main__':unittest.main()
