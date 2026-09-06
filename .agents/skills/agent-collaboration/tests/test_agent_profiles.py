import importlib.util
from pathlib import Path
import shutil
import subprocess
import tomllib
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('checker', Path(__file__).resolve().parents[1] / 'scripts/check_agent_profiles.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / '.codex/agents', self.root / '.codex/agents')
        self.skill = self.root / '.agents/skills/agent-collaboration/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / '.agents/skills/agent-collaboration/SKILL.md', self.skill)

    def change(self, file, old, new):
        path = self.root / '.codex/agents' / file
        path.write_text(path.read_text().replace(old, new))

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required for routing integration')
    def test_reviewer_model_matches_profile(self):
        script = ROOT / '.agents/skills/agent-collaboration/scripts/Get-GateReviewMode.ps1'
        for main, role in [('gpt-5.6-sol', 'code-gate-reviewer-sol'), ('gpt-6-astra', 'code-gate-reviewer-astra')]:
            with self.subTest(main=main):
                result = subprocess.run(['pwsh', '-NoProfile', '-File', str(script), '-ReviewerModel', '-EffectiveMainAgentModel', main], capture_output=True, text=True, check=True)
                profile = tomllib.loads((self.root / '.codex/agents' / (role + '.toml')).read_text())
                self.assertEqual(result.stdout.strip(), profile['model'])
                self.assertEqual(profile['model_reasoning_effort'], 'max')
                self.assertEqual(profile['sandbox_mode'], 'read-only')

    def test_gate_profiles_share_review_contract(self):
        directory = self.root / '.codex/agents'
        astra = tomllib.loads((directory / 'code-gate-reviewer-astra.toml').read_text())
        sol = tomllib.loads((directory / 'code-gate-reviewer-sol.toml').read_text())
        self.assertEqual(astra['developer_instructions'], sol['developer_instructions'])

    def test_pair_instruction_drift(self):
        for role in checker.PAIRED_ROLES:
            with self.subTest(role=role):
                path = self.root / '.codex/agents' / f'{role}-sol.toml'
                original = path.read_text()
                path.write_text(original.replace('Do not spawn', 'You may spawn'))
                self.assertTrue(any('paired profile contracts differ' in e for e in checker.check(self.root)))
                path.write_text(original)

    def test_pair_permission_and_effort_drift(self):
        for old, new in [('model_reasoning_effort = "high"', 'model_reasoning_effort = "max"'),
                         ('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')]:
            path = self.root / '.codex/agents/code-reviewer-sol.toml'
            original = path.read_text()
            path.write_text(original.replace(old, new))
            self.assertTrue(any('paired profile contracts differ' in e for e in checker.check(self.root)))
            path.write_text(original)

    def test_wrong_variant_family(self):
        self.change('code-debugger-sol.toml', 'gpt-5.6-sol', 'gpt-6-astra')
        self.assertTrue(any('model family differs from profile suffix' in e for e in checker.check(self.root)))

    def test_missing_pair(self):
        (self.root / '.codex/agents/code-debugger-sol.toml').unlink()
        self.assertTrue(any('missing Sol/Astra pair member' in e for e in checker.check(self.root)))

    def test_valid(self):
        self.assertEqual(checker.check(self.root), [])

    def test_model_drift(self):
        self.change('code-debugger-astra.toml', 'gpt-6-astra', 'retired-model')
        self.assertTrue(any('differs' in e for e in checker.check(self.root)))

    def test_missing_effort(self):
        self.change('code-worker.toml', 'model_reasoning_effort = "high"', '')
        self.assertTrue(any('missing explicit model_reasoning_effort' in e for e in checker.check(self.root)))

    def test_write_access_regression(self):
        self.change('code-general.toml', 'sandbox_mode = "read-only"', '')
        self.assertTrue(any('requires read-only' in e for e in checker.check(self.root)))

    def test_explicit_sandbox_is_not_inherited(self):
        for mode in ('danger-full-access', 'workspace-write', ''):
            with self.subTest(mode=mode):
                path = self.root / '.codex/agents/code-worker.toml'
                original = path.read_text()
                path.write_text(original + f'\nsandbox_mode = "{mode}"\n')
                self.assertTrue(any('access differs' in e for e in checker.check(self.root)))
                path.write_text(original)

    def test_duplicate(self):
        self.change('code-general.toml', 'name = "code-general"', 'name = "code-explorer"')
        self.assertTrue(any('duplicate name' in e for e in checker.check(self.root)))

    def test_malformed_toml(self):
        self.change('code-worker.toml', 'model = ', 'model = [')
        self.assertTrue(any('invalid TOML' in e for e in checker.check(self.root)))

    def test_missing_route(self):
        self.skill.write_text('\n'.join(line for line in self.skill.read_text().splitlines() if '| `code-general` |' not in line))
        self.assertTrue(any('no routing row' in e for e in checker.check(self.root)))

    def test_fallback_drift(self):
        self.skill.write_text(self.skill.read_text().replace('`default`, `gpt-6-astra` / `high`', '`default`, `old-model` / `high`'))
        self.assertTrue(any('fallback model/effort differs' in e for e in checker.check(self.root)))

    def test_host_capabilities(self):
        host = {'gpt-5.6-luna': ['medium', 'high'], 'gpt-6-astra': ['high', 'max'], 'gpt-5.6-sol': ['high', 'max']}
        self.assertEqual(checker.check(self.root, host), [])
        host['gpt-6-astra'] = ['high']
        self.assertTrue(any('unsupported' in e for e in checker.check(self.root, host)))
        del host['gpt-6-astra']
        self.assertTrue(any('absent' in e for e in checker.check(self.root, host)))


if __name__ == '__main__':
    unittest.main()
