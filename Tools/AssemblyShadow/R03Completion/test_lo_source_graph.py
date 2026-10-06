"""Keep the reported source preflight graph distinct from DLL AssemblyRefs."""
import copy
import unittest
from test_lo_contracts import inputs, loads, HERE, ContractError


class ReportedSourceGraphContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = loads((inputs() / 'preflight/PRIMARY_ISSUES.json').read_text())

    def setUp(self):
        import compile_lo_policy_checks as policy_checks
        self.parse = policy_checks.source_graph
        self.report_copy = copy.deepcopy(self.report)
        self.issue = next(row for row in self.report_copy['issues'] if row['id'] == 'R03-LO-001')

    def test_original_report_keeps_all_three_source_edges(self):
        graph = self.parse(self.report_copy)
        self.assertEqual(graph['Unity.Burst'], ['Unity.Burst.Unsafe'])
        self.assertEqual(graph['Unity.RenderPipelines.Universal.Runtime'], [
            'Unity.RenderPipelines.Universal.2D.Internal', 'Unity.RenderPipelines.Universal.Config.Runtime'])
        self.assertEqual(sum(map(len, graph.values())), 3)

    def test_missing_urp_source_edge_is_not_inferred_from_dll(self):
        self.issue['relevantExcerpt'] = '\n'.join(line for line in self.issue['relevantExcerpt'].splitlines()
            if 'Unity.RenderPipelines.Universal.Config.Runtime.' not in line)
        with self.assertRaisesRegex(ContractError, 'Exact three'): self.parse(self.report_copy)

    def test_duplicate_edge_rejected(self):
        line = next(line for line in self.issue['relevantExcerpt'].splitlines() if line.startswith('RuntimeReferencesFilteredAssembly:'))
        self.issue['relevantExcerpt'] += '\n' + line
        with self.assertRaisesRegex(ContractError, 'Exact three'): self.parse(self.report_copy)

    def test_foreign_provider_rejected(self):
        self.issue['relevantExcerpt'] = self.issue['relevantExcerpt'].replace('Unity.Burst.Unsafe', 'Foreign.Provider')
        with self.assertRaisesRegex(ContractError, 'Exact three'): self.parse(self.report_copy)

    def test_duplicate_issue_rejected(self):
        self.report_copy['issues'].append(copy.deepcopy(self.issue))
        with self.assertRaisesRegex(ContractError, 'Exactly one'): self.parse(self.report_copy)

    def test_unrelated_issue_report_rejected(self):
        self.report_copy['kind'] = 'NotO'
        with self.assertRaisesRegex(ContractError, 'Original O'): self.parse(self.report_copy)

    def test_probe_records_separate_source_and_physical_domains(self):
        source = (HERE / 'CompilerPolicyTests/PolicyDomainProbe.cs').read_text()
        self.assertIn('physicalRefs[name] = module.GetAssemblyRefs()', source)
        self.assertIn('references = refs[row.name]', source)
        self.assertIn('compilerAssemblyRefsUsedAsSourceGraph = false', source)
        self.assertIn('freshSourceGraphCapture = false', source)
