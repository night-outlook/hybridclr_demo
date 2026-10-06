"""Synthetic actual-report-shaped negative tests, not fabricated execution proof."""
import copy
import json
from pathlib import Path
import shutil
import unittest

import fixed_image_inputs as fixed
import fixture_project as fixture
from batch_contract import ContractError
import test_completion_contracts as fixtures
import test_lk_contracts as observations


class FixedReportTests(unittest.TestCase):
    def setUp(self):
        fixtures.SourceFixtureTests.setUp(self)
        self.project,config=fixture.provision(self.batch);self.batch.resource_config=config
        self.receipt=Path(config['receiptRoot'])/'fixed-image-contract.json'
        self.receipt.parent.mkdir(parents=True)
        item=observations.FixedObservationTests();item.setUp();self.addCleanup(item.doCleanups)
        controls=self.receipt.parent/'fixed-image-controls';shutil.copytree(item.controls,controls)
        value=copy.deepcopy(item.value)
        for row in value['cases']:
            row['configurationPath']=str(controls/Path(row['configurationPath']).name)
            if row['imagePath']:row['imagePath']=str(controls/Path(row['imagePath']).name)
        inputs=[{'path':p,'sha256':fixed.sha(self.project/p)} for p in fixed.INPUTS]
        self.value={'kind':'R03ActualFixedImageContract','schemaVersion':1,'result':'Passed',
                    'projectPath':str(self.project),'baselineId':config['baselineId'],
                    'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',
                    'unityEditorRun':True,'actualProjectImageValidator':True,'snapshotCompilationRun':False,
                    'runtimeAcceptance':False,'expansionAuthorized':False,'R03Accepted':False,'H2Passed':False,
                    'before':inputs,'after':copy.deepcopy(inputs),
                    'sources':[{'path':p,'sha256':fixed.sha(self.project/p)} for p in fixed.SOURCES], 'observation':value}

    def verify(self):
        self.receipt.write_text(json.dumps(self.value))
        return fixed.verify_report(self.receipt,self.batch,self.project)

    def test_exact_synthetic_report(self):self.assertEqual(self.verify()['result'],'Passed')
    def test_wrong_platform(self):
        self.value['architecture']='x64'
        with self.assertRaises(ContractError):self.verify()
    def test_wrong_source_tuple_hash(self):
        (self.project/fixed.ordinary.PINS).write_text('{}')
        with self.assertRaises(ContractError):self.verify()
    def test_before_after_difference(self):
        self.value['after'][0]['sha256']='f'*64
        with self.assertRaises(ContractError):self.verify()
    def test_changed_observer_source(self):
        (self.project/fixed.SOURCES[0]).write_text('changed')
        with self.assertRaises(ContractError):self.verify()
    def test_host_is_not_unity(self):
        self.value['unityEditorRun']=False
        with self.assertRaises(ContractError):self.verify()
    def test_missing_actual_project_validator(self):
        self.value['actualProjectImageValidator']=False
        with self.assertRaises(ContractError):self.verify()
    def test_preflight_cannot_claim_compilation(self):
        self.value['snapshotCompilationRun']=True
        with self.assertRaises(ContractError):self.verify()
    def test_preflight_cannot_authorize_expansion(self):
        self.value['expansionAuthorized']=True
        with self.assertRaises(ContractError):self.verify()
    def test_changed_materialization_claim_rejected(self):
        p=self.project/fixed.MATERIALIZATION/'preparation.json'
        row=json.loads(p.read_text());row['freshCscExecutionClaimed']=True;p.write_text(json.dumps(row))
        with self.assertRaises(ContractError):self.verify()
