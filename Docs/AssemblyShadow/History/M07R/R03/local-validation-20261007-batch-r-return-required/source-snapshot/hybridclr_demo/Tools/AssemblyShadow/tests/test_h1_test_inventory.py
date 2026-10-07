import tempfile
import unittest
from pathlib import Path
import h1_test_inventory as t

class TestInventoryTests(unittest.TestCase):
    def test_leaf_passes_not_suite_passes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.xml';p.write_text('<test-run total="2"><test-suite result="Passed"><test-case fullname="A" result="Passed"/><test-case fullname="B" result="Passed"/></test-suite></test-run>')
            r=t.nunit(p);self.assertEqual(2,r['count']);self.assertFalse(r['humanGatePassed'])
    def test_skips_are_not_passes(self):
        r=t.summarize([{'id':'A','result':'Skipped'}],'test');self.assertEqual('CompletedWithNonPass',r['status'])
    def test_zero_tests_rejected(self):
        with self.assertRaises(ValueError):t.summarize([],'test')
    def test_duplicate_names_rejected(self):
        with self.assertRaises(ValueError):t.summarize([{'id':'A','result':'Passed'},{'id':'A','result':'Passed'}],'test')
    def test_nunit_total_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.xml';p.write_text('<test-run total="2"><test-case fullname="A" result="Passed"/></test-run>')
            with self.assertRaises(ValueError):t.nunit(p)
    def test_nunit_external_entity_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.xml';p.write_text('<!DOCTYPE test-run><test-run/>')
            with self.assertRaises(ValueError):t.nunit(p)
    def test_python_suite_records_unique_leaf_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'test_unique_inventory_fixture.py').write_text('import unittest\nclass A(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
            r=t.python_suite(root,'test_unique_inventory_fixture.py',root/'raw.log');self.assertEqual(1,r['count']);self.assertEqual('Passed',r['status'])
    def test_expected_failure_not_plain_pass(self):
        r=t.summarize([{'id':'A','result':'ExpectedFailure'}],'test');self.assertEqual('CompletedWithNonPass',r['status'])

if __name__ == '__main__': unittest.main()
