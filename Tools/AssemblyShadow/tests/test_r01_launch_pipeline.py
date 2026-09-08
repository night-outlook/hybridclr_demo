"""Complete launcher -> receipt -> verify_suite offline round trip.

Only source/build admission and OS process launch are substituted. The real
input collector, executable/receipt binding, per-mode validators, immutable
hash inventory and strict vs diagnostic acceptance remain active.
"""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from test_r01_pipeline import fixture
import r01_results as gate
from shadow_tools import VerificationError


def runner_module():
    source=Path(gate.__file__).with_name('run-r01-players.py')
    spec=importlib.util.spec_from_file_location('r01_test_launcher',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class R01LaunchPipelineTests(unittest.TestCase):
    def round_trip(self, root, expectation):
        root=root.resolve();launcher=runner_module();templates={}
        for mode in gate.MODES:
            _,r,context,on=fixture(root,mode,expectation);templates[mode]=r
        (root/'Assets/AssemblyShadowDemo').mkdir(parents=True)
        (root/'_temp/AssemblyShadow').mkdir(parents=True)
        resources=root/'Resources';resources.mkdir();(resources/'resource').write_text('resource')
        scratch=root/'ReplayScratch';scratch.mkdir();(scratch/'proof').write_text('proof')
        native=root/'native';native.write_text('native')
        metadata=root/'metadata';metadata.write_text('metadata')
        placeholder=root/'placeholder';placeholder.write_text('placeholder')
        resource_receipt=root/'resource-receipt.json';resource_receipt.write_text('{}')
        output=Path(on['player']['playerOutput']);binary=output/'Contents/MacOS/Player';binary.parent.mkdir();binary.write_text('not executed')
        (output/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='Player')))
        on['output']=output
        on['player'].update(placeholderManifestPath=str(placeholder),resourceBuildReceiptPath=str(resource_receipt),resourceBaselinePath=str(resources))
        off=copy.deepcopy(on);off['path']=root/'off-player.json';off['player']['buildGuid']='off-guid'
        on['path'].write_text(json.dumps(on['player']));off['path'].write_text(json.dumps(off['player']))
        baseline_path=root/'baseline.json';baseline_path.write_text(json.dumps(dict(resourceBaselinePath='Resources',playerInputSnapshot='Inputs')))
        manifest=context['manifest'];manifest['baselineManifestSha256']=gate.digest(baseline_path)
        manifest['baselineInputSnapshot']=str(root/'Inputs');manifest['rejectedFixtures']=[]
        item=context['fixtures']['P03'];item['r01Capability']=True
        item['fixture'].update(compileSnapshot=str(root/'Inputs'),replacementResourcePath='')
        manifest['fixtures']=[item['fixture']]
        fixture_path=root/'fixtures.json';fixture_path.write_text(json.dumps({k:v for k,v in manifest.items() if not k.startswith('_')}))
        replay=root/'replay.json';replay.write_text(json.dumps(dict(replayScratchPath=str(scratch))))
        context.update(on=on,off=off,sourcePins=dict(testOnly='upstream-admission-substituted'),baseline=dict(nativeBudgetCapabilityVersion=1))
        out=root/'_temp/AssemblyShadow/Run'
        def run(command,cwd,console_path,timeout):
            mode=command[command.index('-shadowR01Mode')+1];r=copy.deepcopy(templates[mode]);build=off if mode==gate.OFF_MODE else on
            path=Path(command[command.index('-shadowR01Result')+1]);r.update(resultPath=str(path),processId=1000+gate.MODES.index(mode),buildGuid=build['player']['buildGuid'],
                 playerBuildReceiptPath=str(build['path']),playerBuildReceiptSha256=gate.digest(build['path']),fixtureManifestSha256=gate.digest(fixture_path),baselineManifestSha256=gate.digest(baseline_path))
            path.write_text(json.dumps(r));Path(command[-1]).write_text('offline process substitute');console_path.write_text('offline process substitute')
            return dict(processId=r['processId'],exitCode=0,timedOut=False,startedAtUnix=1.0,durationSeconds=0.25)
        args=['--project-root',str(root),'--fixture-manifest',str(fixture_path),'--on-build',str(on['path']),'--off-build',str(off['path']),'--replay-receipt',str(replay),'--output-root',str(out),'--startup-expectation',expectation]
        with patch.object(launcher,'verify_inputs',return_value=context),patch.object(launcher,'_run_one',side_effect=run),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(launcher.main(args),0)
        launch=out/'r01-player-launches.json'
        with patch.object(gate,'verify_inputs',return_value=context):
            result=gate.verify_suite(launch,expectation)
        self.assertEqual(len(result['modes']),10)
        self.assertEqual(result['diagnosticOnly'],expectation==gate.STARTUP_OBSERVATION_GAP)
        return launch,context

    def test_public_launcher_receipt_and_suite_cover_both_explicit_expectations(self):
        for expectation in gate.STARTUP_EXPECTATIONS:
            with self.subTest(expectation=expectation),tempfile.TemporaryDirectory() as temp:
                launch,context=self.round_trip(Path(temp),expectation)
                original=json.loads(launch.read_text())
                for mutation in ('diagnosticOnly','inputHash','receiptAlias','processReuse'):
                    bad=copy.deepcopy(original)
                    if mutation=='diagnosticOnly':bad['diagnosticOnly']=not bad['diagnosticOnly']
                    elif mutation=='inputHash':
                        key=next(iter(bad['inputHashesBefore']));bad['inputHashesBefore'][key]='0'*64;bad['inputHashesAfter'][key]='0'*64
                    elif mutation=='receiptAlias':bad['onBuildReceiptPath']=str(Path(bad['onBuildReceiptPath']).parent)+'/./player.json'
                    else:bad['processLaunches'][1]['processId']=bad['processLaunches'][0]['processId']
                    launch.write_text(json.dumps(bad))
                    with self.subTest(mutation=mutation),patch.object(gate,'verify_inputs',return_value=context),self.assertRaises(VerificationError):gate.verify_suite(launch,expectation)
                launch.write_text(json.dumps(original))
                with patch.object(gate,'verify_inputs',return_value=context),self.assertRaises(VerificationError):
                    gate.verify_suite(launch,gate.STARTUP_OBSERVATION_GAP if expectation==gate.STARTUP_EARLY_GUARD else gate.STARTUP_EARLY_GUARD)
