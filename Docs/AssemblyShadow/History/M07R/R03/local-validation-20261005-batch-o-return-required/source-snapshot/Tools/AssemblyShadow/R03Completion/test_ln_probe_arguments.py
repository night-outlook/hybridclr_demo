"""Probe transport contracts, separate from actual managed replay evidence."""
import ast
import os
from pathlib import Path
import unittest
import compile_reference_checks as checks
import reference_binding as replay

HERE = Path(__file__).resolve().parent


class ProbeArgumentContracts(unittest.TestCase):
    def test_managed_parser_argument_order(self):
        case = replay.CASE_IDS[0]
        command = checks.replay_arguments([Path('/one path'), Path('/two')], Path('/mono'),
                                         Path('/probe.exe'), Path('/input.json'), Path('/new output'), case)
        self.assertEqual(command[-6:], ['--input', Path('/input.json'), '--output', Path('/new output'), '--case', case])
        self.assertEqual(command[:4], ['/usr/bin/env', 'MONO_PATH=/one path' + os.pathsep + '/two', Path('/mono'), Path('/probe.exe')])
        source = (HERE / 'ReferenceBindingTests/Program.cs').read_text()
        self.assertIn('args[0]=="--input"&&args[2]=="--output"&&args[4]=="--case"', source)

    def test_no_shell_or_argument_splitting(self):
        command = checks.replay_arguments([], '/mono space', '/probe space', '/input space', '/output space', replay.CASE_IDS[-1])
        self.assertEqual(len(command), 10)
        self.assertEqual(command[-3], '/output space')
        self.assertNotIn('sh', command)

    def test_validate_uses_tested_argument_builder(self):
        tree = ast.parse((HERE / 'compile_reference_checks.py').read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate')
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'replay_arguments']
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0].args), 6)

    def test_historical_qualification_and_compiler_states_remain_distinct(self):
        tree = ast.parse((HERE / 'compile_reference_checks.py').read_text())
        states = [dict((k.value, v.value) for k, v in zip(n.keys, n.values)
                       if isinstance(k, ast.Constant) and isinstance(v, ast.Constant))
                  for n in ast.walk(tree) if isinstance(n, ast.Dict)]
        report = next(s for s in states if s.get('kind') == 'R03PinnedMonoReferenceBinding')
        self.assertEqual(report['historicalQualification'], 'Failed')
        self.assertEqual(report['historicalCompilerPolicy'], 'Passed')
        self.assertNotIn('historicalFinalPolicy', report)
        for key in ('runtimeAcceptance', 'unityEditorRun', 'playerRun', 'expansionAuthorized'):
            self.assertIs(report[key], False)


if __name__ == '__main__':
    unittest.main()
