"""Diagnostic projections and fresh-report contracts; fixtures are not Unity runs."""
import json
from pathlib import Path
import tempfile
import unittest

import policy_domains as domain
from batch_contract import ContractError, sha

HERE = Path(__file__).resolve().parent


class LivePolicyWiringTests(unittest.TestCase):
    def test_actual_producer_and_consumer_both_require_live_domain_receipt(self):
        source = (HERE.parents[2] / 'Assets/AssemblyShadowDemo/Editor/R03CompletionBuild.cs').read_text()
        self.assertIn('ValidateBeforeCompile(source, EditorUserBuildSettings.activeBuildTarget)', source)
        self.assertIn('ValidateBeforeCompile(linked, EditorUserBuildSettings.activeBuildTarget)', source)
        self.assertLess(source.index('string policyDomains = VerifyPolicyDomains('), source.index('string restored = AssemblySnapshot.CompileWithOptions('))
        self.assertIn('policy_domains.verify_live(', (HERE / 'resource_pipeline.py').read_text())


class LivePolicyReportContractTests(unittest.TestCase):
    """Synthetic receipt-shape controls, never emitted as runtime evidence."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve() / 'project'; self.project.mkdir()
        self.root = self.project / '_temp/AssemblyShadow/R03CompletionArtifacts'
        folder = self.root / 'compiler-policy-domains'; folder.mkdir(parents=True)
        self.path = self.root / 'compiler-policy-domains.json'; self.baseline = 'a' * 64
        self.value = dict(schemaVersion=1, kind='R03LiveSourcePolicyDomains', result='Passed',
            projectPath=str(self.project), unityVersion='2022.3.62f2', target='StandaloneOSX',
            baselineSnapshotHash=self.baseline, sourceInventoryValidationPassed=True,
            linkedPolicyRejectedForSource=True, sourcePolicyUnchanged=True, freshUnityInventory=True,
            sourceDiagnostics=[], guardProviders=[p for _, p in domain.EDGES],
            linkedPolicyDiagnostics=[dict(code='RuntimeReferencesFilteredAssembly', message=domain.diagnostic_message(*edge)) for edge in domain.EDGES])
        self.value.update({key: False for key in ('runtimeAcceptance','qualificationApproved','expansionAuthorized','R03Accepted','H2Passed')})
        for field, name, role in (('sourcePolicy','source-policy.json',0),('linkedPolicy','linked-policy.json',5)):
            p = folder / name
            p.write_text(json.dumps({'assemblies': [dict(name=provider, classification=role) for _, provider in domain.EDGES]}))
            self.value[field + 'Path'] = str(p); self.value[field + 'Sha256'] = sha(p)

    def verify(self):
        self.path.write_text(json.dumps(self.value))
        return domain.verify_live(self.path, self.project, self.root, self.baseline)

    def test_contract_fixture_positive(self):
        self.assertEqual(self.verify()['filteredReferenceGuards'], 3)

    def test_no_invented_runtime_or_gate_acceptance(self):
        for flag in ('runtimeAcceptance','qualificationApproved','expansionAuthorized','R03Accepted','H2Passed'):
            with self.subTest(flag=flag):
                self.value[flag] = True
                with self.assertRaises(ContractError): self.verify()
                self.value[flag] = False

    def test_missing_guard_rejected(self):
        self.value['linkedPolicyDiagnostics'].pop()
        with self.assertRaises(ContractError): self.verify()

    def test_wrong_consumer_rejected(self):
        self.value['linkedPolicyDiagnostics'][0]['message'] = domain.diagnostic_message('Foreign.Burst',domain.EDGES[0][1])
        with self.assertRaises(ContractError): self.verify()

    def test_historical_or_foreign_baseline_rejected(self):
        self.value['baselineSnapshotHash'] = 'b' * 64
        with self.assertRaises(ContractError): self.verify()

    def test_source_validation_failure_rejected(self):
        self.value['sourceDiagnostics'] = [dict(code='Failure', message='source failure')]
        with self.assertRaises(ContractError): self.verify()

    def test_mutated_policy_bytes_rejected(self):
        p = Path(self.value['sourcePolicyPath']); p.write_text(p.read_text() + ' ')
        with self.assertRaises(ContractError): self.verify()

    def test_same_player_policy_reused_as_source_rejected(self):
        p = Path(self.value['sourcePolicyPath']); p.write_text(Path(self.value['linkedPolicyPath']).read_text())
        self.value['sourcePolicySha256'] = sha(p)
        with self.assertRaises(ContractError): self.verify()

    def test_duplicate_canonical_policy_names_rejected(self):
        p = Path(self.value['sourcePolicyPath']); d = json.loads(p.read_text())
        d['assemblies'].append(dict(d['assemblies'][0], name=d['assemblies'][0]['name'].upper()))
        p.write_text(json.dumps(d)); self.value['sourcePolicySha256'] = sha(p)
        with self.assertRaises(ContractError): self.verify()

    def test_foreign_project_rejected(self):
        self.value['projectPath'] += '-other'
        with self.assertRaises(ContractError): self.verify()

    def test_foreign_policy_file_even_same_bytes_rejected(self):
        p = self.project / 'same-bytes.json'; p.write_text(Path(self.value['sourcePolicyPath']).read_text())
        self.value['sourcePolicyPath'] = str(p)
        with self.assertRaises(ContractError): self.verify()


if __name__ == '__main__': unittest.main()
