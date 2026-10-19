#!/usr/bin/env python3
"""Host-only receipt consumer and thirteen-component orchestration regression tests.

Git, compilers, SDK inputs and all child suites are MOCKED. The managed result
root, initial record, final write and returned binding are executed from the
actual build_api.py AST; no installed SDK, Unity or Player is executed.
"""
from __future__ import annotations
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parent / 'R03/build_api.py'
RUNNER = Path(os.environ.get('P1_RECEIPT_TEST_RUNNER',
                             str(HERE / 'run_p1_metadata_local_preflight.py')))

def load_runner():
    spec = importlib.util.spec_from_file_location('receipt_preflight_under_test', RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def producer_response(output, verdict='Passed'):
    """Execute unchanged producer receipt expressions; mock compilation only."""
    tree = ast.parse(PRODUCER.read_text(encoding='utf-8'))
    function, = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == 'validate_build_api']
    assignments = {n.targets[0].id: n for n in function.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    trial, = [n for n in function.body if isinstance(n, ast.Try)]
    returned, = [n for n in function.body if isinstance(n, ast.Return)]
    mkdir, = [n for n in function.body if isinstance(n, ast.Expr)
              and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Attribute)
              and n.value.func.attr == 'mkdir']
    env = {'batch': SimpleNamespace(root=output), 'sha': digest,
           'write': lambda p, v: p.write_text(json.dumps(v, sort_keys=True, indent=2)+'\n',
                                             encoding='utf-8')}
    prefix = ast.Module(body=[assignments['root'], mkdir, assignments['result']], type_ignores=[])
    exec(compile(prefix, str(PRODUCER), 'exec'), env)
    # Five product records and one expected-negative compiler record. These
    # are synthetic receipts, NOT actual compiler or product output evidence.
    labels = ['HybridCLR.Runtime', 'Unity.HybridCLR.AssemblyShadow.CodeGen',
              'HybridCLR.Editor', 'R03Build', 'R03TerminalPlayerApi', 'OriginalUnsignedCounts']
    env['result'].update(result=verdict, commands=[{'id': n, 'expectedExit': int(i == 5)}
                                                for i, n in enumerate(labels)],
                         inputs=[{'mock': True}], completeHelper={'mock': True},
                         terminalPlayerApi={'playerExecution': False, 'mock': True})
    exec(compile(ast.Module(body=trial.finalbody, type_ignores=[]), str(PRODUCER), 'exec'), env)
    binding = eval(compile(ast.Expression(returned.value), str(PRODUCER), 'eval'), env)
    return (json.dumps(binding)+'\n').encode(), Path(binding['result'])

class ManagedReceiptContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / 'managed-sdk'
        self.output.mkdir()
        self.runner = load_runner()
        self.stdout, self.receipt = producer_response(self.output)

    def consume(self, stdout=None):
        return self.runner.read_managed_result(self.output, self.stdout if stdout is None else stdout)

    def rebind(self):
        self.stdout = json.dumps({'result': str(self.receipt), 'sha256': digest(self.receipt)}).encode()

    def test_actual_producer_response_joins_nested_file(self):
        result = self.consume()
        self.assertFalse((self.output/'results.json').exists())
        self.assertEqual(result['innerResult'], 'Passed')
        self.assertEqual(result['innerResultPath'], str(self.receipt))
        self.assertEqual(result['innerResultSha256'], digest(self.receipt))
        self.assertTrue(result['returnedBindingVerified'])

    def test_missing_result_and_obsolete_root_decoy_are_rejected(self):
        self.receipt.unlink()
        (self.output/'results.json').write_text('{"result":"Passed"}')
        with self.assertRaises((ValueError, OSError)):
            self.consume()

    def test_mutated_result_bytes_are_rejected(self):
        self.receipt.write_bytes(self.receipt.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.consume()

    def test_failed_inner_verdict_is_not_promoted(self):
        record = json.loads(self.receipt.read_bytes())
        record['result'] = 'Failed'
        self.receipt.write_text(json.dumps(record))
        self.rebind()
        (self.output/'results.json').write_text('{"result":"Passed"}')
        self.assertEqual(self.consume()['innerResult'], 'Failed')

    def test_wrong_returned_paths_are_rejected(self):
        for path in [str(self.output/'results.json'), str(self.root/'other/results.json'),
                     'build-api/results.json', str(self.output)+'/build-api/../build-api/results.json']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.consume(json.dumps({'result': path, 'sha256': digest(self.receipt)}).encode())

    def test_invalid_binding_shapes_hashes_and_duplicate_keys(self):
        for raw in [b'', b'[]', b'null', b'{}', b'no JSON', b'\xff',
                    b'{"result":"a","result":"b","sha256":"c"}',
                    b'{"result":NaN,"sha256":"x"}',
                    json.dumps({'result':str(self.receipt),'sha256':None}).encode(),
                    json.dumps({'result':str(self.receipt),'sha256':'g'*64}).encode(),
                    json.dumps({'result':str(self.receipt),'sha256':'0'*64}).encode(),
                    json.dumps({'result':str(self.receipt),'sha256':digest(self.receipt),'extra':1}).encode()]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.consume(raw)

    def test_invalid_inner_json_or_identity_is_rejected(self):
        valid = self.receipt.read_bytes()
        variants = [b'[]', b'null', b'{', b'{"result":"Failed","result":"Passed"}', b'{"x":Infinity}']
        for field, value in [('kind','Other'), ('schemaVersion',True), ('schemaVersion',2),
                             ('result',None), ('unityVersion','other'), ('runtimeAcceptance',True),
                             ('nativeExecution',True), ('unityEditorRun',True)]:
            record = json.loads(valid); record[field] = value
            variants.append(json.dumps(record).encode())
        for raw in variants:
            with self.subTest(raw=raw):
                self.receipt.write_bytes(raw); self.rebind()
                with self.assertRaises(ValueError): self.consume()

    def test_file_and_parent_symlinks_are_rejected(self):
        outside = self.root/'outside.json'
        self.receipt.replace(outside)
        self.receipt.symlink_to(outside)
        with self.assertRaises(ValueError): self.consume()
        self.receipt.unlink()
        self.receipt.parent.rmdir()
        directory = self.root/'outside-directory'; directory.mkdir()
        outside.replace(directory/'results.json')
        self.receipt.parent.symlink_to(directory, target_is_directory=True)
        with self.assertRaises(ValueError): self.consume()

    def test_directory_in_place_of_receipt_is_rejected(self):
        self.receipt.unlink(); self.receipt.mkdir()
        with self.assertRaises(ValueError): self.consume()

class AggregateReceiptIntegration(unittest.TestCase):
    def exercise(self, mode='passed'):
        """Run the actual main; mock all subprocesses and Git/SDK environment."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); ws = root/'workspace'; ws.mkdir()
            output = root/'batch'; scratch = root/'sdk-copy'
            demo = ws/'hybridclr_demo'; native = ws/'il2cpp_plus'
            paths = [demo/'Tools/AssemblyShadow/R03IR'/n for n in
                     ('run_p1_metadata_local_preflight.py','run_primary_host_preflight.py',
                      'run_p1_command_failure_tests.py','test_p1_command_failures.py')]
            paths += [demo/'Tools/AssemblyShadow/R03'/n for n in
                      ('native_validation.py','build_api.py','source-pins.json')]
            paths += [native/'libil2cpp/vm'/n for n in
                      ('AssemblyShadowMetadataLifetime.h','Runtime.cpp','Assembly.cpp','AssemblyShadowVisibility.cpp')]
            paths += [native/'tools/r03/diagnostic_stream'/n for n in
                      ('run_metadata_lifetime_gate.py','run_bounded_general_composer.py',
                       'bounded_general_composer_fixture.cpp',
                       'run_bounded_general_live.py','bounded_general_live_fixture.cpp',
                       'test_bounded_general_live_command.py',
                       'run_frozen_execution.py','frozen_execution_fixture.cpp',
                       'frozen_execution_allocations.cpp',
                       'test_frozen_execution_include_path.py')]
            paths += [native/'libil2cpp/vm'/n for n in
                      ('AssemblyShadowBoundedGeneralComposer.h','AssemblyShadowFrozenGeneralCapture.h',
                       'AssemblyShadowBoundedGeneralLive.h','AssemblyShadowBoundedGeneralLiveSource.inl',
                       'AssemblyShadow.h','AssemblyShadow.cpp',
                       'AssemblyShadowFrozenExecutionRecord.h','AssemblyShadowR02Snapshot.h',
                       'AssemblyShadowFrozenR02Serializer.h','AssemblyShadowExecutionSerializer.h',
                       'AssemblyShadowR02Diagnostics.h','AssemblyShadowDiagnosticWriter.h',
                       'AssemblyShadowObservationCounters.h','AssemblyShadowObservationMemo.h',
                       'AssemblyShadowDiagnosticsProfile.h')]
            paths += [native/'tools/r03/diagnostic_stream/reference'/n for n in
                      ('AssemblyShadowExecutionSerializer.h','AssemblyShadowR02Diagnostics.h')]
            paths += [demo/'Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowGeneralComposeSyntax.cpp',
                      demo/'Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionComposeSyntax.cpp']
            for p in paths:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text('mock SDK/source input\n')
            unity = root/'Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity'
            unity.parent.mkdir(parents=True); unity.write_text('mock anchor: never executed')
            runner = load_runner(); launched = []; verifying = []
            def verify(base, name, sha):
                verifying.append(name)
                if mode == 'postflight-error' and len(verifying)>4:
                    raise RuntimeError('mock remote mismatch after execution')
                return {'repository':'night-outlook/'+name, 'head':sha, 'clean':True}
            def child(argv, timeout=120):
                args = list(map(str, argv)); launched.append(args)
                dest = Path(args[args.index('--output')+1]); dest.mkdir()
                name = dest.name
                if name == 'managed-sdk':
                    if mode == 'child-exception': raise FileNotFoundError('mock compiler launch error')
                    stdout, receipt = producer_response(dest, 'Failed' if mode=='inner-failed' else 'Passed')
                    if mode == 'missing': receipt.unlink()
                    if mode == 'mutated': receipt.write_bytes(receipt.read_bytes()+b' ')
                    if mode == 'root-only': receipt.replace(dest/'results.json')
                    if mode == 'source-changed': paths[0].write_text('changed mock source')
                    if mode == 'wrong-binding':
                        stdout=json.dumps({'result':str(dest/'results.json'),'sha256':digest(receipt)}).encode()
                    return subprocess.CompletedProcess(args, 9 if mode=='exit-nonzero' else 0, stdout, b'mock warning\n')
                if (mode=='live-general-failed' and name=='live-general') or \
                   (mode=='owned-execution-failed' and name=='owned-execution'):
                    (dest/'RESULT.json').write_text(json.dumps({'result':'FailedOrIncomplete'}))
                    return subprocess.CompletedProcess(args,1,b'mock failed bridge\n',b'')
                expected = ('PassedHostOnly' if name=='legacy-host' else
                            'Passed' if name=='native-sdk' else
                            'PassedWithinOwnedHostScope' if name=='owned-general' else
                            'PassedWithinInactiveSourceHostScope' if name=='live-general' else
                            'PassedWithinOwnedExecutionHostScope' if name=='owned-execution' else
                            'PassedWithinInactiveHostScope' if name=='frozen-v2' else 'PassedWithinHostScope')
                (dest/('results.json' if name=='native-sdk' else 'RESULT.json')).write_text(json.dumps({'result':expected}))
                return subprocess.CompletedProcess(args, 0, b'mock child\n', b'')
            argv = [str(RUNNER), '--workspace',str(ws),'--unity',str(unity),
                    '--output',str(output),'--sdk-scratch',str(scratch),
                    '--expected-demo','a'*40,'--expected-native','b'*40]
            exit_code=0
            with patch.object(sys,'argv',argv), patch.object(runner,'verify_repo',side_effect=verify), \
                 patch.object(runner,'run',side_effect=child), contextlib.redirect_stdout(io.StringIO()):
                try: runner.main()
                except SystemExit as e: exit_code=e.code
            report=json.loads((output/'RESULT.json').read_bytes())
            self.assertEqual(len(report['commands']),14)
            self.assertEqual(len(launched),14)
            self.assertEqual(len(set(Path(cmd[2]).name for cmd in launched)),14)
            self.assertFalse(scratch.exists()) # no compiler, SDK copy or Unity execution
            self.assertEqual(report['expectedNativeSyntaxUnits'],80)
            self.assertFalse(report['R03Accepted'])
            self.assertFalse(report['UnityPlayerExecuted'])
            self.assertFalse(report['historicalEvidenceReclassified'])
            self.assertTrue((output/'commands/managed-sdk.json').is_file())
            self.assertTrue((output/'MANIFEST.json').is_file())
            for record in json.loads((output/'MANIFEST.json').read_bytes())['files']:
                self.assertEqual(digest(output/record['path']),record['sha256'])
            managed=next(c for c in report['commands'] if c['name']=='managed-sdk')
            self.assertEqual(managed,json.loads((output/'commands/managed-sdk.json').read_bytes()))
            if mode!='child-exception':
                self.assertEqual(digest(output/'commands/managed-sdk/stdout.bin'),managed['stdout.binSha256'])
                self.assertEqual((output/'commands/managed-sdk/stderr.bin').read_bytes(),b'mock warning\n')
            self.assertEqual(launched[-1][-2:],['--candidate-native-sha','b'*40])
            return exit_code,report,managed

    def test_fourteen_components_pass_with_actual_producer_response(self):
        code,report,managed=self.exercise()
        self.assertEqual(code,0)
        self.assertEqual(report['result'],'PassedSourceHostAndSDKOnly')
        self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertTrue(managed['returnedBindingVerified'])
        self.assertTrue(managed['innerResultPath'].endswith('/managed-sdk/build-api/results.json'))

    def test_managed_failures_preserve_thirteen_passed_one_failed(self):
        for mode in ('missing','root-only','mutated','wrong-binding','inner-failed','exit-nonzero','child-exception'):
            with self.subTest(mode=mode):
                code,report,managed=self.exercise(mode)
                self.assertEqual(code,1)
                self.assertEqual(report['result'],'FailedOrIncomplete')
                self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),13)
                self.assertEqual(managed['status'],'Failed')
                self.assertFalse(report['officialUnitySdkCompilePassed'])
                self.assertTrue(report['sourcePreserved'])
                if mode=='inner-failed': self.assertEqual(managed['innerResult'],'Failed')

    def test_inactive_native_child_failure_retains_accurate_aggregate_and_sdk_flags(self):
        for mode,target in (('live-general-failed','live-general'),
                            ('owned-execution-failed','owned-execution')):
            with self.subTest(mode=mode):
                code,report,_=self.exercise(mode)
                self.assertEqual(code,1)
                self.assertEqual(report['result'],'FailedOrIncomplete')
                self.assertEqual(len(report['commands']),14)
                self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),13)
                child=next(c for c in report['commands'] if c['name']==target)
                self.assertEqual(child['status'],'Failed')
                self.assertEqual(child['exit'],1)
                self.assertEqual(child['innerResult'],'FailedOrIncomplete')
                # Compiler children may pass but cannot promote a failed host.
                self.assertTrue(report['officialUnitySdkCompilePassed'])
                self.assertTrue(report['sourcePreserved'])
                self.assertFalse(report['R03Accepted'])

    def test_source_change_never_becomes_aggregate_pass(self):
        code,report,_=self.exercise('source-changed')
        self.assertEqual(code,1)
        self.assertFalse(report['sourcePreserved'])
        self.assertEqual(report['result'],'FailedOrIncomplete')

    def test_postflight_error_retains_failure_receipt(self):
        code,report,_=self.exercise('postflight-error')
        self.assertEqual(code,1)
        self.assertIn('mock remote mismatch',report['postflightError'])
        self.assertFalse(report['sourcePreserved'])

if __name__=='__main__':
    unittest.main(verbosity=2)
