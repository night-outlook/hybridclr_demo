import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parents[1]

import sys
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from h1_m07_workflow_authority import BASELINE_BOUND, VerificationError, authenticate_originals, verify


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.STDOUT).decode().strip()


def load_runtime_wrapper():
    path = TOOLS / 'verify-installed-runtime.py'
    spec = importlib.util.spec_from_file_location('h1_verify_installed_runtime_for_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M07WorkflowAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'
        self.recovery = self.base / 'recovery'
        self.project.mkdir()
        self.recovery.mkdir()
        git(self.project, 'init')
        git(self.project, 'config', 'user.email', 'h1@example.invalid')
        git(self.project, 'config', 'user.name', 'H1 Test')

        files = {
            'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity': 'scene: pinned\n',
            'ProjectSettings/AssemblyShadowSettings.asset': 'buildId: pinned\n',
            'ProjectSettings/EditorBuildSettings.asset': 'scenes: pinned\n',
            'Assets/AssemblyShadowDemo/Editor/Immutable.cs': 'sealed class ImmutableInput {}\n',
            'Assets/AssemblyShadowDemo/Tests/Editor/EditorTests.asmdef': '{"name":"EditorTests"}\n',
            'ProjectSettings/AssemblyShadowSourcePins.json': '{"schemaVersion":1,"demo":{"revision":"0000000000000000000000000000000000000000"}}\n',
        }
        for relative, text in files.items():
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        git(self.project, 'add', '.')
        git(self.project, 'commit', '-m', 'source anchor')
        self.anchor = git(self.project, 'rev-parse', 'HEAD')
        pins = {'schemaVersion': 1, 'demo': {'revision': self.anchor}}
        (self.project / 'ProjectSettings/AssemblyShadowSourcePins.json').write_text(json.dumps(pins) + '\n')
        git(self.project, 'add', 'ProjectSettings/AssemblyShadowSourcePins.json')
        git(self.project, 'commit', '-m', 'metadata pin')

        backups = {
            'm07-bootstrap-scene.original': 'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity',
            'assembly-shadow-settings.original': 'ProjectSettings/AssemblyShadowSettings.asset',
            'editor-build-settings.original': 'ProjectSettings/EditorBuildSettings.asset',
        }
        for name, relative in backups.items():
            shutil.copyfile(self.project / relative, self.recovery / name)
        self.baseline = 'M07-Baseline-authority-regression'

    def tearDown(self):
        self.temp.cleanup()

    def mutate_required(self):
        (self.project / 'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity').write_text(
            'scene expectedBaselineBuildId: ' + self.baseline + '\n')
        (self.project / 'ProjectSettings/AssemblyShadowSettings.asset').write_text(
            'buildId: ' + self.baseline + '\n')

    def test_exact_mutable_state_preserves_immutable_authority(self):
        before = authenticate_originals(self.project, self.recovery)
        self.assertFalse(before['requiredMutationObserved'])
        self.mutate_required()
        result = verify(self.project, self.recovery, self.baseline)
        self.assertEqual('M07PostValidationAuthorityVerifiedNotBuildAccepted', result['status'])
        rows = {row['path']: row for row in result['mutablePaths']}
        self.assertEqual(set(BASELINE_BOUND), {path for path, row in rows.items() if row['baselineBound']})
        for path in BASELINE_BOUND:
            self.assertTrue(rows[path]['changed'])
        self.assertFalse(result['candidateAcceptance'])
        self.assertFalse(result['humanGatePassed'])
        self.assertFalse(result['mayEnterR02'])

    def test_immutable_build_input_tamper_fails(self):
        self.mutate_required()
        (self.project / 'Assets/AssemblyShadowDemo/Editor/Immutable.cs').write_text('tampered\n')
        with self.assertRaises(VerificationError):
            verify(self.project, self.recovery, self.baseline)

    def test_saved_original_tamper_fails(self):
        self.mutate_required()
        (self.recovery / 'm07-bootstrap-scene.original').write_text('wrong original\n')
        with self.assertRaises(VerificationError):
            verify(self.project, self.recovery, self.baseline)

    def test_partial_or_wrong_baseline_mutation_fails(self):
        scene = self.project / 'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity'
        scene.write_text('scene expectedBaselineBuildId: ' + self.baseline + '\n')
        with self.assertRaises(VerificationError):
            verify(self.project, self.recovery, self.baseline)
        self.mutate_required()
        with self.assertRaises(VerificationError):
            verify(self.project, self.recovery, 'M07-Baseline-other')

    def test_untracked_code_input_still_fails(self):
        self.mutate_required()
        extra = self.project / 'Assets/AssemblyShadowDemo/Editor/Unexpected.cs'
        extra.write_text('class Unexpected {}\n')
        with self.assertRaises(VerificationError):
            verify(self.project, self.recovery, self.baseline)


class M07CoreDispatchContractTests(unittest.TestCase):
    def test_core_uses_current_coordinator_verifier_for_external_projects(self):
        source=(TOOLS/'Invoke-M07Build.Core.ps1').read_text()
        self.assertIn("Join-Path $PSScriptRoot 'verify-installed-runtime.py'",source)
        self.assertNotIn("Join-Path $Project 'Tools/AssemblyShadow/verify-installed-runtime.py'",source)
        self.assertNotIn('--skip-demo-source',source)
        self.assertIn('--expect-shadow on --json',source)
        wrapper=(TOOLS/'verify-installed-runtime.py').read_text()
        self.assertIn('H1_M07_WORKFLOW_AUTHORITY_ROOT',wrapper)
        self.assertIn('verify_m07_workflow',wrapper)


class M07InstalledRuntimeDispatchTests(unittest.TestCase):
    def test_pre_mutation_keeps_full_generic_verifier(self):
        module = load_runtime_wrapper()
        context = {
            'mutablePaths': [
                {'path': path, 'changed': False} for path in BASELINE_BOUND
            ]
        }
        env = {
            module.ENV_ROOT: '/tmp/m07-root',
            module.ENV_BASELINE: 'M07-Baseline-dispatch',
        }
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.object(module, 'authenticate_originals', return_value=context), \
             mock.patch.object(module, 'main', return_value=0) as generic, \
             mock.patch.object(module, 'verify_m07_workflow') as m07:
            result = module._run_m07_context(['--project', '/tmp/project', '--expect-shadow', 'on', '--json'])
        self.assertEqual(0, result)
        generic.assert_called_once_with(['verify', '--project', '/tmp/project', '--expect-shadow', 'on', '--json'])
        m07.assert_not_called()

    def test_post_mutation_recheck_uses_runtime_plus_exact_m07_authority(self):
        module = load_runtime_wrapper()
        context = {
            'mutablePaths': [
                {'path': path, 'changed': True} for path in BASELINE_BOUND
            ]
        }
        authority = {'status': 'M07PostValidationAuthorityVerifiedNotBuildAccepted'}
        env = {
            module.ENV_ROOT: '/tmp/m07-root',
            module.ENV_BASELINE: 'M07-Baseline-dispatch',
        }
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.object(module, 'authenticate_originals', return_value=context), \
             mock.patch.object(module, 'main', return_value=0) as generic, \
             mock.patch.object(module, 'verify_m07_workflow', return_value=authority) as m07:
            result = module._run_m07_context(['--project', '/tmp/project', '--expect-shadow', 'on', '--json'])
        self.assertEqual(0, result)
        generic.assert_called_once_with([
            'verify', '--project', '/tmp/project', '--expect-shadow', 'on', '--json', '--skip-demo-source'])
        m07.assert_called_once_with(Path('/tmp/project'), Path('/tmp/m07-root'), 'M07-Baseline-dispatch')

    def test_m07_context_rejects_caller_demo_skip(self):
        module = load_runtime_wrapper()
        env = {
            module.ENV_ROOT: '/tmp/m07-root',
            module.ENV_BASELINE: 'M07-Baseline-dispatch',
        }
        with mock.patch.dict(os.environ, env, clear=False):
            with self.assertRaises(VerificationError):
                module._run_m07_context(['--project', '/tmp/project', '--skip-demo-source'])


if __name__ == '__main__':
    unittest.main()
