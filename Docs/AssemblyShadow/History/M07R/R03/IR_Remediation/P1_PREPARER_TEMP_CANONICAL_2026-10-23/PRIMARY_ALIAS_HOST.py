#!/usr/bin/env python3
"""Host-only fixture: simulate an inherited /var -> /private/var aliased temp parent."""
from pathlib import Path
import tempfile
import unittest
import test_prepare_p1_admitted_local as tests

with tempfile.TemporaryDirectory() as parent_dir:
    parent = Path(parent_dir).resolve(strict=True)
    actual = parent / "private" / "var" / "folders"
    actual.mkdir(parents=True)
    (parent / "var").symlink_to(parent / "private" / "var", target_is_directory=True)
    alias = parent / "var" / "folders"
    assert alias.resolve(strict=True) == actual
    original = tempfile.tempdir
    tempfile.tempdir = str(alias)
    try:
        probe = Path(tempfile.mkdtemp(prefix="p1-aliased-"))
        assert probe.resolve(strict=True) != probe
        probe.rmdir()
        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        print(f"SIMULATED_ALIAS=Passed tests={result.testsRun} errors={len(result.errors)} failures={len(result.failures)}")
        if not result.wasSuccessful() or result.testsRun != 15:
            raise SystemExit(1)
    finally:
        tempfile.tempdir = original
