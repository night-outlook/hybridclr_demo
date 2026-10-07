"""Run the real constructor, cell scheduler and execute order with fake external work.

These are orchestration unit tests, not Unity/Player or custody evidence.
No test pre-populates resource_context before the graph action.
"""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_completion as runner


class CompletionDataflowTests(unittest.TestCase):
    def exercise(self, *, fail_graph=False, fail_layout=False, fail_integration=False,
                 fail_finalize=False):
        with tempfile.TemporaryDirectory() as temp, contextlib.ExitStack() as stack:
            root = Path(temp).resolve()
            unity = root / 'Unity'; unity.write_text('Not an executable: constructor fixture only')
            batch = runner.CompletionBatch(runner.HERE.parents[3], root / 'batch', unity, 'a' * 40)
            self.assertFalse(hasattr(batch, 'resource_context'))
            calls = []

            def references():
                batch.references['hybridclr_unity'] = root / 'reference-package'
                return {}

            def graph(value):
                self.assertIs(value, batch)
                self.assertFalse(hasattr(value, 'resource_context'))
                calls.append('graph')
                if fail_graph: raise RuntimeError('controlled graph failure')
                value.resource_context = {'context': {'on': {'snapshot': {'snapshotHash': 'b' * 64}}}}
                return {}

            def layout(value):
                calls.append('layout')
                if fail_layout: raise RuntimeError('controlled layout failure after context creation')
                return {}

            def integration(value):
                # Mirrors the actual integration consumer's required graph value.
                self.assertEqual(value.resource_context['context']['on']['snapshot']['snapshotHash'], 'b' * 64)
                self.assertTrue(value.outputs['resource-input-binding'])
                calls.append('integration')
                if fail_integration: raise RuntimeError('controlled integration failure')
                return {}

            def phase(value, name):
                if fail_finalize and name == 'finalize': raise RuntimeError('controlled finalize failure')
                return {}

            for name in ('authority', 'completion_tests', 'python_tests', 'managed', 'prepare_project',
                         'build', 'player', 'producer_controls'):
                stack.enter_context(mock.patch.object(batch, name, return_value={}))
            stack.enter_context(mock.patch.object(batch, 'reference_worktrees', side_effect=references))
            for name in ('qualification', 'validate_inputs'):
                stack.enter_context(mock.patch.object(runner, name, return_value={}))
            for name in ('prepare', 'restore', 'editor'):
                stack.enter_context(mock.patch.object(runner.resources, name, return_value={}))
            stack.enter_context(mock.patch.object(runner.resources, 'phase', side_effect=phase))
            stack.enter_context(mock.patch.object(runner.resources, 'graph', side_effect=graph))
            stack.enter_context(mock.patch.object(runner.layout_evidence, 'verify_graph', side_effect=layout))
            entry = stack.enter_context(mock.patch.object(runner.resources, 'integration', side_effect=integration))
            players = {}
            for name in ('m07_case', 'm07_summary', 'r00_case', 'measurements', 'early_case'):
                players[name] = stack.enter_context(mock.patch.object(runner.legacy, name, return_value={}))
            stack.enter_context(mock.patch.object(runner, 'finalize', side_effect=lambda root, value: dict(value, sealStatus='Passed')))
            with contextlib.redirect_stdout(io.StringIO()): code = batch.execute()
            self.assertEqual([c['id'] for c in batch.cells], batch.planned)
            self.assertEqual(len(batch.cells), 90)
            self.assertEqual(len(set(batch.planned)), 90)
            return code, {c['id']: c for c in batch.cells}, calls, entry.call_count, {n: m.call_count for n, m in players.items()}

    def test_actual_constructor_and_execution_bind_before_integration(self):
        code, cells, calls, count, players = self.exercise()
        self.assertEqual(code, 0)
        self.assertEqual(calls, ['graph', 'layout', 'integration'])
        self.assertEqual(cells['production-entry-integration']['dependencies'], ['resource-input-binding'])
        self.assertEqual(count, 1)
        self.assertEqual(players['m07_case'], 14)
        self.assertEqual(players['r00_case'], 12)
        self.assertEqual(players['early_case'], 10)
        self.assertTrue(all(row['result'] == 'Passed' for row in cells.values()))

    def test_failed_graph_blocks_integration_and_dependents(self):
        code, cells, calls, count, players = self.exercise(fail_graph=True)
        self.assertEqual(code, 1)
        self.assertEqual(cells['resource-input-binding']['result'], 'Failed')
        self.assertEqual(cells['production-entry-integration']['result'], 'Blocked')
        self.assertEqual(count, 0)
        self.assertEqual(players['m07_case'] + players['r00_case'] + players['early_case'], 0)
        self.assertEqual(cells['final-authority']['result'], 'Passed')

    def test_context_left_by_failed_layout_is_not_authority(self):
        code, cells, calls, count, _ = self.exercise(fail_layout=True)
        self.assertEqual(code, 1)
        self.assertEqual(calls, ['graph', 'layout'])
        self.assertEqual(cells['resource-input-binding']['result'], 'Failed')
        self.assertEqual(cells['production-entry-integration']['result'], 'Blocked')
        self.assertEqual(count, 0)

    def test_integration_failure_does_not_block_independent_players(self):
        code, cells, calls, count, players = self.exercise(fail_integration=True)
        self.assertEqual(code, 1)
        self.assertEqual(cells['production-entry-integration']['result'], 'Failed')
        self.assertEqual(count, 1)
        self.assertEqual(players['m07_case'], 14)
        self.assertEqual(players['r00_case'], 12)
        self.assertEqual(players['early_case'], 10)

    def test_finalize_failure_keeps_cleanup_but_blocks_graph_and_integration(self):
        code, cells, calls, count, _ = self.exercise(fail_finalize=True)
        self.assertEqual(code, 1)
        self.assertEqual(cells['resource-p05-restore']['result'], 'Passed')
        self.assertEqual(cells['resource-input-binding']['result'], 'Blocked')
        self.assertEqual(cells['production-entry-integration']['result'], 'Blocked')
        self.assertEqual(calls, [])
        self.assertEqual(count, 0)


if __name__ == '__main__': unittest.main()
