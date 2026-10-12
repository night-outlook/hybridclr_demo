"""Synthetic read-only diagnostic collection tests; not a Local Bee observation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import collect_i_debug_cache as c


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve(strict=True)
        self.bee=self.root/'Bee';self.bee.mkdir()
        self.output=self.root/'out'
        self.source=self.bee/'tundra.json';self.source.write_bytes(c.NEEDLE+b' at %s\n')

    def test_exact_read_only_copy_and_context(self):
        original=self.source.read_bytes();r=c.collect(self.bee,self.output)
        self.assertEqual(r['result'],'CollectedForPrimaryAnalysis')
        self.assertEqual(len(r['files']),1);self.assertEqual(len(r['diagnosticOccurrences']),1)
        self.assertEqual(self.source.read_bytes(),original)
        self.assertEqual((self.output/'files/tundra.json').read_bytes(),original)
        self.assertFalse(r['runtimeAcceptance']);self.assertEqual(r['buildsRun'],0)

    def test_object_file_excluded(self):
        (self.bee/'native.o').write_bytes(b'not diagnostics')
        r=c.collect(self.bee,self.output)
        self.assertEqual(len(r['files']),1)
        self.assertFalse((self.output/'files/native.o').exists())

    def test_consumed_output_rejected(self):
        self.output.mkdir();(self.output/'keep').write_text('keep')
        with self.assertRaises(ValueError):c.collect(self.bee,self.output)
        self.assertEqual((self.output/'keep').read_text(),'keep')

    def test_input_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlaps'):c.collect(self.bee,self.bee/'out')
        self.assertFalse((self.bee/'out').exists())

    def test_other_protected_overlap_rejected(self):
        protected=self.root/'old';protected.mkdir()
        with self.assertRaisesRegex(ValueError,'overlaps'):c.collect(self.bee,protected/'out',(protected,))

    def test_symlink_file_rejected(self):
        (self.bee/'alias.log').symlink_to(self.source)
        with self.assertRaises(ValueError):c.collect(self.bee,self.output)

    def test_symlink_parent_rejected(self):
        alias=self.root/'alias';alias.symlink_to(self.bee,target_is_directory=True)
        with self.assertRaises(ValueError):c.collect(alias,self.output)

    def test_missing_bee_rejected(self):
        with self.assertRaises(ValueError):c.collect(self.root/'absent',self.output)

    def test_empty_selected_set_unavailable(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError,'No selected'):c.collect(self.bee,self.output)

    def test_file_bound_fails_before_copy(self):
        with patch.object(c,'MAX_FILE',1),self.assertRaises(ValueError):c.collect(self.bee,self.output)
        self.assertFalse(self.output.exists())

    def test_total_bound_fails_before_copy(self):
        with patch.object(c,'MAX_TOTAL',1),self.assertRaises(ValueError):c.collect(self.bee,self.output)
        self.assertFalse(self.output.exists())

    def test_drift_between_inventories_rejected(self):
        real=c.inventory;calls=[]
        def changed(root):
            calls.append(1)
            if len(calls)==2:self.source.write_bytes(b'changed')
            return real(root)
        with patch.object(c,'inventory',side_effect=changed),self.assertRaisesRegex(ValueError,'changed'):
            c.collect(self.bee,self.output)
        self.assertFalse((self.output/'collection.json').exists())

    def test_relative_output_rejected(self):
        with self.assertRaises(ValueError):c.collect(self.bee,Path('out'))

    def test_count_bound(self):
        with patch.object(c,'MAX_FILES',0),self.assertRaises(ValueError):c.collect(self.bee,self.output)
        self.assertFalse(self.output.exists())

if __name__=='__main__':unittest.main()
