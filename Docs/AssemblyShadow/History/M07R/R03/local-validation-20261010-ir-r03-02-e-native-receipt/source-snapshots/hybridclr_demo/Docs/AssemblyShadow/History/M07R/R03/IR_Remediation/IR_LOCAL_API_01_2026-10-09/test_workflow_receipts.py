"""Primary synthetic tests for the workflow's Python receipt steps, not C# or Unity tests."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml

WORKFLOW = Path(os.environ.get('R03_API_WORKFLOW', str(Path(__file__).with_name('r03-ir-player-api.yml')))).resolve()
STEPS = yaml.safe_load(WORKFLOW.read_text())['jobs']['managed-api']['steps']
PRE = next(s['run'] for s in STEPS if s.get('name') == 'Bind exact compilation inputs before build')
POST = next(s['run'] for s in STEPS if s.get('name') == 'Authenticate unchanged inputs and successful compiler output')
PLAYER = 'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'
PROJECT = 'Tools/AssemblyShadow/R03/PlayerApiCompile/PlayerApiCompile.csproj'

class ReceiptChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.oldcwd = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.oldcwd)
        self.addCleanup(self.temp.cleanup)
        for name in ('hybridclr_demo', 'hybridclr_unity'):
            (self.root/name).mkdir()
            self.git(name, 'init', '-q')
            self.git(name, 'config', 'user.name', 'Synthetic Receipt Test')
            self.git(name, 'config', 'user.email', 'test@example.invalid')
        self.write('hybridclr_unity/Runtime/FakeApi.cs', '// synthetic, not a real API\n')
        self.commit('hybridclr_unity')
        self.write('hybridclr_demo/' + PLAYER, '// synthetic Player input\n')
        self.write('hybridclr_demo/' + PROJECT, '''<Project><PropertyGroup><TargetFramework>net8.0</TargetFramework><LangVersion>9.0</LangVersion><DefineConstants>UNITY_EDITOR</DefineConstants><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup><ItemGroup><Compile Include="../../R03IR/PlayerProject/R03TerminalPlayer.cs"/><Compile Include="$(PackageRoot)/Runtime/*.cs"/></ItemGroup></Project>''')
        self.write('hybridclr_demo/Tools/AssemblyShadow/R03/source-pins.json', json.dumps({'hybridclr_unity':self.head('hybridclr_unity')}))
        self.write('hybridclr_demo/.github/workflows/r03-ir-player-api.yml', WORKFLOW.read_text())
        self.commit('hybridclr_demo')
        self.env = {'GITHUB_SHA':self.head('hybridclr_demo'), 'GITHUB_RUN_ID':'synthetic-not-github', 'GITHUB_RUN_ATTEMPT':'1', 'RUNNER_TEMP':str(self.root/'runner')}

    def git(self, name, *args):
        return subprocess.check_output(['git','-C',name,*args], stderr=subprocess.STDOUT).decode().strip()
    def head(self, name): return self.git(name,'rev-parse','HEAD')
    def commit(self, name):
        self.git(name,'add','.')
        self.git(name,'commit','-qm','synthetic test fixture')
    def write(self, name, data):
        p=Path(name); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(data)
    def execute(self, code):
        with patch.dict(os.environ,self.env), contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code,'workflow-python-step','exec'),{})
    def build_placeholder(self):
        # Only exercises post-build hashing. This is NOT a compiled assembly.
        self.write('runner/r03-ir-managed/bin/PlayerApiCompile.dll','synthetic output placeholder')
        self.write('runner/r03-ir-managed/build.log','synthetic build placeholder; no compiler executed')
    def test_positive_source_and_output_binding(self):
        self.execute(PRE); self.build_placeholder(); self.execute(POST)
        result=json.loads(Path('runner/r03-ir-managed/compile-result.json').read_text())
        self.assertEqual(result['demoCommit'],self.env['GITHUB_SHA'])
        self.assertFalse(result['runtimeAcceptance'])
    def test_wrong_demo_commit(self):
        self.env['GITHUB_SHA']='0'*40
        with self.assertRaisesRegex(RuntimeError,'Demo checkout'): self.execute(PRE)
    def test_wrong_package_pin(self):
        self.write('hybridclr_demo/Tools/AssemblyShadow/R03/source-pins.json',json.dumps({'hybridclr_unity':'0'*40}))
        with self.assertRaisesRegex(RuntimeError,'Package checkout'): self.execute(PRE)
    def test_dirty_player(self):
        self.write('hybridclr_demo/'+PLAYER,'changed')
        with self.assertRaisesRegex(RuntimeError,'Dirty compilation input'): self.execute(PRE)
    def test_missing_player_compile_item(self):
        p=Path('hybridclr_demo/'+PROJECT); p.write_text(p.read_text().replace('<Compile Include="../../R03IR/PlayerProject/R03TerminalPlayer.cs"/>',''))
        with self.assertRaisesRegex(RuntimeError,'not a compilation input'): self.execute(PRE)
    def test_unmatched_glob(self):
        Path('hybridclr_unity/Runtime/FakeApi.cs').unlink()
        with self.assertRaisesRegex(RuntimeError,'matched no files'): self.execute(PRE)
    def test_symlink_input(self):
        p=Path('hybridclr_demo/'+PLAYER); p.unlink(); p.symlink_to(self.root/'hybridclr_unity/Runtime/FakeApi.cs')
        with self.assertRaisesRegex(RuntimeError,'ordinary file'): self.execute(PRE)
    def test_implicit_compile_items(self):
        p=Path('hybridclr_demo/'+PROJECT); p.write_text(p.read_text().replace('false','true'))
        with self.assertRaisesRegex(RuntimeError,'explicit Compile items'): self.execute(PRE)
    def test_input_changed_after_build(self):
        self.execute(PRE); self.build_placeholder(); self.write('hybridclr_demo/'+PLAYER,'changed')
        with self.assertRaisesRegex(RuntimeError,'input changed during build'): self.execute(POST)
    def test_missing_compiler_output(self):
        self.execute(PRE)
        with self.assertRaisesRegex(RuntimeError,'Missing actual compiler output'): self.execute(POST)
    def test_head_changed_after_build(self):
        self.execute(PRE); self.build_placeholder(); self.write('hybridclr_demo/new.txt','changed'); self.commit('hybridclr_demo')
        with self.assertRaisesRegex(RuntimeError,'Checkout changed'): self.execute(POST)

if __name__ == '__main__': unittest.main(verbosity=2)
