"""Host include isolation and exact contract orchestration, not Player tests."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from evidence import EvidenceError, read, write
import type_resolution_contract as contract


class ContractIncludes(unittest.TestCase):
    def test_all_levels_use_quote_only_project_search(self):
        for level in (0, 1, 2):
            args = contract.writer_command('/usr/bin/c++', Path('/native root'), Path('/source root'), Path('/out/writer'), level)
            self.assertEqual(args[3:5], ['-iquote', '/native root/libil2cpp/vm'])
            self.assertNotIn('-I', args)
            self.assertNotIn('-isystem', args)
            self.assertIn('-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=' + str(level), args)
            self.assertEqual(args[-3:], ['/source root/writer.cpp', '-o', '/out/writer'])

    def test_invalid_level_is_not_coerced(self):
        for level in (-1, 3, True, '0', 0.0):
            with self.subTest(level=level), self.assertRaises(EvidenceError):
                contract.writer_command('c++', Path('/n'), Path('/s'), Path('/b'), level)

    def test_real_system_header_collision_and_quoted_sibling_resolution(self):
        compilers = list(dict.fromkeys(filter(None, (shutil.which('c++'), shutil.which('clang++')))))
        self.assertTrue(compilers, 'A host C++ compiler is required for this regression')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            native = root / 'native with spaces'; vm = native / 'libil2cpp/vm'; vm.mkdir(parents=True)
            source = root / 'source with spaces'; source.mkdir()
            # Models the real basename collision without depending on libc++'s
            # indirect include ordering. The negative control must hit this.
            (vm / 'string.h').write_text('#error EXPECTED_PROJECT_STRING_H_COLLISION\n')
            (vm / 'sibling.h').write_text('#define QUOTED_SIBLING 3\n')
            (vm / 'AssemblyShadowR02Diagnostics.h').write_text('#include <cstring>\n#include "sibling.h"\n')
            (source / 'writer.cpp').write_text('#include "AssemblyShadowR02Diagnostics.h"\nint main(){return std::strlen("abc") == QUOTED_SIBLING ? 0 : 1;}\n')
            for i, compiler in enumerate(compilers):
                with self.subTest(compiler=compiler):
                    binary = root / ('writer-' + str(i))
                    good = contract.writer_command(compiler, native, source, binary, 0)
                    bad = ['-I' if arg == '-iquote' else arg for arg in good]
                    rejected = subprocess.run(bad, capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(rejected.returncode, 0)
                    self.assertIn('EXPECTED_PROJECT_STRING_H_COLLISION', rejected.stderr)
                    accepted = subprocess.run(good, capture_output=True, text=True, timeout=60)
                    self.assertEqual(accepted.returncode, 0, accepted.stderr)
                    self.assertEqual(subprocess.run([str(binary)], timeout=10).returncode, 0)


class ContractExecution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.native = self.root / 'native'; self.package = self.root / 'package'; self.output = self.root / 'results'
        for path in (self.native / 'libil2cpp/vm/AssemblyShadowR02Diagnostics.h',
                     self.package / 'Runtime/AssemblyShadow/AssemblyShadowTypeResolutionInfo.cs'):
            path.parent.mkdir(parents=True); path.write_text('explicit orchestration fixture\n')
        self.calls = []
        self.fail = None
        self.assertions = dict(kind='R02ProducerParserContract', result='Passed', nativeFixtures=12, legacyFixtures=1, checks=1310)

    def fake_run(self, args, cwd, output, timeout, env):
        self.calls.append((output.name, args, env))
        output.mkdir(parents=True)
        result = dict(result='Failed' if output.name == self.fail else 'Passed', processGroupClean=True)
        write(output / 'command.json', result)
        text = 'fixture compiler version\n' if output.name == 'compiler-version' else json.dumps(self.assertions if output.name == 'managed-run' else {'fixture': output.name})
        if output.name.startswith('emit-') and not output.name.endswith('legacy'):
            # This is an orchestration fixture, not native execution.
            from type_resolution_schema import COUNTERS
            level = int(output.name.split('-')[1])
            value = dict.fromkeys(COUNTERS, 0)
            value.update(schemaVersion=1, diagnosticsLevel=level, counterThreadCapacity=128,
                         counterSaturated=False, memoryAccountingAvailable=level != 0,
                         counterCoverage='Disabled' if level == 0 else 'BoundedComplete',
                         classesCoverage='Disabled' if level < 2 else 'BoundedComplete',
                         memoryAccountingScope='R02StructuresExcludingAllocatorOverhead')
            text = json.dumps({'r02': value})
        (output / 'stdout.log').write_text(text)
        return result

    def invoke(self):
        with patch.object(contract.shutil, 'which', return_value='/usr/bin/c++'), patch.object(contract, 'run', side_effect=self.fake_run):
            return contract.execute(self.native, self.package, self.output, 'dotnet')

    def test_real_execute_uses_isolated_command_for_every_level(self):
        report = self.invoke()
        self.assertEqual(report['result'], 'Passed')
        self.assertEqual(report['includePolicy'], contract.INCLUDE_POLICY)
        self.assertEqual(len(report['nativeFixtures']), 13)
        self.assertEqual(sum(row['mode'] == 'legacy' for row in report['nativeFixtures']), 1)
        for level in (0, 1, 2):
            args = next(args for label, args, _ in self.calls if label == 'compile-' + str(level))
            self.assertIn('-iquote', args); self.assertNotIn('-I', args)
        self.assertEqual(self.calls[0][0], 'compiler-version')
        self.assertEqual([row[0] for row in self.calls][-2:], ['managed-build', 'managed-run'])
        self.assertEqual(report['assertions'], self.assertions)

    def test_compile_failure_is_retained_and_cannot_reach_parser(self):
        self.fail = 'compile-0'
        with self.assertRaises(EvidenceError): self.invoke()
        report = read(self.output / 'results.json')
        self.assertEqual(report['result'], 'Failed')
        self.assertIn('compile-0', report['error'])
        self.assertFalse(any(label.startswith('managed') for label, _, _ in self.calls))
        self.assertFalse(report['runtimeAcceptance']); self.assertFalse(report['unityPlayerRun'])

    def test_all_native_fixtures_and_assertions_remain_mandatory(self):
        for key, value in (('nativeFixtures', 11), ('legacyFixtures', 0), ('checks', 1000), ('result', 'Failed')):
            with self.subTest(key=key):
                self.output = self.root / key
                self.assertions = dict(kind='R02ProducerParserContract', result='Passed', nativeFixtures=12, legacyFixtures=1, checks=1310)
                self.assertions[key] = value
                with self.assertRaises(EvidenceError): self.invoke()
                self.assertEqual(read(self.output / 'results.json')['result'], 'Failed')

    def test_failed_managed_command_is_not_overridden_by_passed_stdout(self):
        self.fail = 'managed-run'
        with self.assertRaises(EvidenceError): self.invoke()
        self.assertEqual(read(self.output / 'results.json')['result'], 'Failed')

    def test_missing_compiler_is_not_an_optional_pass(self):
        with patch.object(contract.shutil, 'which', return_value=None), self.assertRaises(EvidenceError):
            contract.execute(self.native, self.package, self.output)
        self.assertEqual(read(self.output / 'results.json')['result'], 'Failed')


if __name__ == '__main__': unittest.main()
