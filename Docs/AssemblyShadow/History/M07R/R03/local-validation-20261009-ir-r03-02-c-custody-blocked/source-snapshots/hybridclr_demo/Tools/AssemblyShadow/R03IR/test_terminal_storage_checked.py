"""Fail-closed IR storage-wrapper location contracts, no Player execution."""
from pathlib import Path
import tempfile
import unittest

from run_terminal_storage_checked import (
    EXPECTED_CELLS, validate_locations, ObservedTerminalBatch
)
from storage_guard import StorageBlocked, START_MIN, FLOOR


class FocusedStorageContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.workspace=self.root/"workspace"
        self.retained=self.root/"historical-Q"
        self.workspace.mkdir()
        self.retained.mkdir()
        self.output=self.root/"ir-batch"
        self.sidecar=self.root/"ir-sidecar"

    def ok(self):
        return validate_locations(self.workspace,self.output,self.sidecar,self.retained)

    def test_valid_sibling_origins_are_accepted(self):
        result=self.ok()
        self.assertEqual(result,(self.workspace,self.output,self.sidecar,self.retained))

    def test_existing_batch_and_sidecar_are_rejected(self):
        self.output.mkdir()
        with self.assertRaises(StorageBlocked):self.ok()
        self.output.rmdir()
        self.sidecar.mkdir()
        with self.assertRaises(StorageBlocked):self.ok()

    def test_workspace_or_retained_as_output_are_rejected(self):
        for output in (self.workspace,self.retained,self.workspace/"new",self.retained/"new"):
            with self.subTest(output=output):
                with self.assertRaises(StorageBlocked):
                    validate_locations(self.workspace,output,self.sidecar,self.retained)

    def test_nested_seal_and_sidecar_are_rejected(self):
        with self.assertRaises(StorageBlocked):
            validate_locations(self.workspace,self.root/"new"/"batch",self.root/"new",self.retained)

    def test_relative_input_is_rejected(self):
        with self.assertRaises(StorageBlocked):
            validate_locations(Path("relative"),self.output,self.sidecar,self.retained)

    def test_no_capacity_policy_weakening(self):
        self.assertEqual(START_MIN,64*1024**3)
        self.assertEqual(FLOOR,20*1024**3)

    def test_same_original_scheduler_and_four_players(self):
        self.assertEqual(EXPECTED_CELLS,14)
        self.assertEqual(ObservedTerminalBatch.__mro__[1].__name__,"Batch")

if __name__=="__main__":
    unittest.main()
