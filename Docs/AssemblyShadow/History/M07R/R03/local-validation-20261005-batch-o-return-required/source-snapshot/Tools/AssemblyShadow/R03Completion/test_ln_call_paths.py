"""Static closure of explicit codec authority through the production call chain.

These checks complement real Git/cwd tests. They execute no Players and accept
no artifact result; they prevent dropping source_context in a nested verifier.
"""
import ast
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
M07 = HERE.parent / 'm07_results.py'


def functions(text):
    return {n.name: n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}


def guarded_functions(text):
    return {name: n for name, n in functions(text).items()
            if any(a.arg == 'source_context' for a in (*n.args.posonlyargs, *n.args.args, *n.args.kwonlyargs))}


def missing_context(text, guarded, imported):
    misses = []
    for caller, node in functions(text).items():
        if not imported and caller not in guarded:
            continue  # Standalone legacy entry points may accept absolute pins.
        for call in (n for n in ast.walk(node) if isinstance(n, ast.Call)):
            f = call.func
            name = (f.attr if imported and isinstance(f, ast.Attribute) and
                    isinstance(f.value, ast.Name) and f.value.id == 'm07' else
                    f.id if not imported and isinstance(f, ast.Name) else None)
            if name not in guarded:
                continue
            target = guarded[name]
            positional = [a.arg for a in (*target.args.posonlyargs, *target.args.args)]
            supplied = [k.value for k in call.keywords if k.arg == 'source_context']
            if 'source_context' in positional and len(call.args) > positional.index('source_context'):
                supplied.append(call.args[positional.index('source_context')])
            if len(supplied) != 1 or isinstance(supplied[0], ast.Constant) and supplied[0].value is None:
                misses.append((caller, name, call.lineno))
    return misses


class CodecCallChainContracts(unittest.TestCase):
    def test_all_context_aware_m07_functions_forward_authority(self):
        source = M07.read_text()
        guarded = guarded_functions(source)
        self.assertGreaterEqual(len(guarded), 8)
        self.assertEqual(missing_context(source, guarded, False), [])

    def test_all_completion_entry_calls_forward_authority(self):
        guarded = guarded_functions(M07.read_text())
        for filename in ('fixture_authority.py', 'legacy_runtime.py'):
            with self.subTest(filename=filename):
                self.assertEqual(missing_context((HERE / filename).read_text(), guarded, True), [])

    def test_guard_detects_original_early_success_omission(self):
        sample = "def early_case():\n    m07.verify_case(a,b,c,d,e,f,g)\n"
        self.assertEqual(missing_context(sample, guarded_functions(M07.read_text()), True)[0][:2],
                         ('early_case', 'verify_case'))

    def test_none_is_not_an_authenticated_context(self):
        sample = "def early_case():\n    m07.verify_case(a,b,c,d,e,f,g,source_context=None)\n"
        self.assertEqual(len(missing_context(sample, guarded_functions(M07.read_text()), True)), 1)

    def test_explicit_owner_context_is_retained(self):
        sample = "def early_case():\n    m07.verify_case(a,b,c,d,e,f,g,source_context=batch.resource_context['codecContext'])\n"
        self.assertEqual(missing_context(sample, guarded_functions(M07.read_text()), True), [])


if __name__ == '__main__':
    unittest.main()
