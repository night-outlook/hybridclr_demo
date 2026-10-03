#!/usr/bin/env python3
"""One source-bound R03 completion batch. All substantive work is implemented here.

Retains the original 37 focused cells; adds qualification, original resource
compilation/Editor/runtime, real production-entry integration and fixed unfenced
observations. No result implies qualification approval or R03/H2 acceptance.
"""
import argparse
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from run_local import Batch as FocusedBatch, REPOS, ROOT
from batch_contract import loads, require, sha
from batch_evidence import finalize, write
from input_validation import validate_inputs
from run_host import qualification
from resource_capabilities import host_contracts as capability_contracts
from fixture_contracts import constructor_contracts, editor_preflight
import resource_pipeline as resources
import legacy_runtime as legacy


def cell_plan(matrix):
    names = ['entry-authority', 'completion-tool-contracts', 'qualification', 'verifier-contracts', 'reference-sources',
             'host-baseline-graph', 'host-candidate-graph', 'host-admission', 'player-fixtures']
    for role in matrix['roles']:
        names += ['prepare-' + role['id'], 'build-' + role['id']]
    names += ['editor-tests'] + [case['id'] for case in matrix['cases']] + ['producer-controls']
    names += ['resource-prepare', 'resource-install', 'resource-compiler', 'resource-bundles', 'resource-player-on',
              'resource-player-off', 'resource-p05-prepare', 'resource-p05-compile', 'resource-p05-restore',
              'resource-p05-finalize', 'resource-editor', 'production-entry-integration', 'resource-input-binding']
    names += ['resource-' + mode for mode in sorted(legacy.m07.MODES)] + ['resource-contracts']
    names += ['measure-' + mode + '-' + str(rep) for mode in legacy.r00.MODES for rep in range(3)] + ['measurement-summary']
    names += ['early-' + label for label, _, _ in legacy.EARLY_CASES] + ['final-authority']
    require(len(names) == len(set(names)) == 90, 'Exact ninety-cell completion plan')
    return names


class CompletionBatch(FocusedBatch):
    def __init__(self, workspace, output, unity, demo_commit):
        super().__init__(workspace, output, unity, demo_commit)
        require(HERE == self.workspace / 'hybridclr_demo/Tools/AssemblyShadow/R03Completion', 'Owning completion source')
        pins = loads((HERE / 'source-pins.json').read_text())
        require(pins['branch'] == self.pins['branch'] and pins['expansionAuthorized'] is False and pins['runtimeAcceptance'] is False,
                'Non-authorizing exact completion profile')
        self.pins = dict(pins, hybridclr_demo=demo_commit)
        self.resource_config = None
        self.planned = cell_plan(self.matrix)
        write(self.root / 'completion-plan.json', {'schemaVersion': 1, 'kind': 'R03CompletionPlan', 'cells': self.planned,
              'repositories': self.pins, 'freshNativeBuilds': 6, 'focusedPlayerProcesses': 23, 'resourcePlayerProcesses': 14,
              'measurementPlayerProcesses': 12, 'earlyPlayerProcesses': 10, 'editorProjects': {'focused': 754, 'resource': 755},
              'R03Accepted': False, 'H2Passed': False, 'expansionAuthorized': False})

    def completion_tests(self):
        receipt = self.command([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', HERE, '-p', 'test_*.py', '-v'])
        capabilities = capability_contracts(self)
        constructor = constructor_contracts(self)
        editor = editor_preflight(self)
        return {'commandReceipt': receipt, 'constructorContracts': constructor, 'capabilityProfileContracts': capabilities, 'earlyEditorFixtures': editor,
                'scope': 'Host helper and eighteen real Editor regressions; full rosters still required'}

    def execute(self):
        self.cell('entry-authority', self.authority)
        self.cell('completion-tool-contracts', self.completion_tests, ('entry-authority',))
        self.cell('qualification', lambda: qualification(self), ('entry-authority',))
        self.cell('verifier-contracts', self.python_tests, ('entry-authority',))
        self.cell('reference-sources', self.reference_worktrees, ('entry-authority',))
        self.cell('host-baseline-graph', lambda: self.managed('HostTests', 'baseline-graph', self.references['hybridclr_unity'], 'baseline'), ('reference-sources',))
        self.cell('host-candidate-graph', lambda: self.managed('HostTests', 'candidate-graph', phase='candidate'), ('entry-authority',))
        self.cell('host-admission', lambda: self.managed('AdmissionTests', 'admission'), ('entry-authority',))
        self.cell('player-fixtures', lambda: validate_inputs(self), ('host-admission',))
        for role in self.matrix['roles']:
            name = role['id']
            deps = ('player-fixtures', 'reference-sources', 'verifier-contracts') if not role['candidate'] else ('player-fixtures', 'entry-authority', 'verifier-contracts')
            self.cell('prepare-' + name, lambda r=role: self.prepare_project(r), deps)
            self.cell('build-' + name, lambda r=role: self.build(r), ('prepare-' + name,))
        self.cell('editor-tests', lambda: resources.editor(self, complete=False), ('prepare-candidate-release', 'host-admission'))
        for case in self.matrix['cases']:
            self.cell(case['id'], lambda c=case: self.player(c), ('build-' + case['role'],))
        self.cell('producer-controls', self.producer_controls, ('build-candidate-release',))
        self.cell('resource-prepare', lambda: resources.prepare(self), ('entry-authority', 'completion-tool-contracts'))
        self.cell('resource-install', lambda: resources.phase(self, 'install'), ('resource-prepare',))
        self.cell('resource-compiler', lambda: resources.phase(self, 'compiler'), ('resource-install',))
        self.cell('resource-bundles', lambda: resources.phase(self, 'resources'), ('resource-compiler',))
        self.cell('resource-player-on', lambda: resources.phase(self, 'player-on'), ('resource-bundles',))
        self.cell('resource-player-off', lambda: resources.phase(self, 'player-off'), ('resource-bundles',))
        self.cell('resource-p05-prepare', lambda: resources.phase(self, 'prepare'), ('resource-player-on', 'resource-player-off'))
        self.cell('resource-p05-compile', lambda: resources.phase(self, 'compile'), ('resource-p05-prepare',))
        # Cleanup runs even when Prepare/Compile failed after recording mutation.
        # It does not relabel a failed/blocked compile as Passed.
        self.cell('resource-p05-restore', lambda: resources.restore(self), ('resource-prepare',))
        self.cell('resource-p05-finalize', lambda: resources.phase(self, 'finalize'), ('resource-p05-compile', 'resource-p05-restore'))
        self.cell('resource-editor', lambda: resources.editor(self, complete=True), ('resource-install', 'resource-p05-restore', 'host-admission'))
        self.cell('production-entry-integration', lambda: resources.integration(self), ('resource-p05-finalize',))
        self.cell('resource-input-binding', lambda: resources.graph(self), ('resource-p05-finalize',))
        for mode in sorted(legacy.m07.MODES):
            self.cell('resource-' + mode, lambda m=mode: legacy.m07_case(self, m), ('resource-input-binding',))
        self.cell('resource-contracts', lambda: legacy.m07_summary(self), tuple('resource-' + mode for mode in sorted(legacy.m07.MODES)))
        for mode in legacy.r00.MODES:
            for rep in range(3):
                self.cell('measure-' + mode + '-' + str(rep), lambda m=mode, r=rep: legacy.r00_case(self, m, r), ('resource-input-binding',))
        self.cell('measurement-summary', lambda: legacy.measurements(self), tuple('measure-' + mode + '-' + str(rep) for mode in legacy.r00.MODES for rep in range(3)))
        for label, mode, patch in legacy.EARLY_CASES:
            self.cell('early-' + label, lambda l=label, m=mode, p=patch: legacy.early_case(self, l, m, p), ('resource-input-binding',))
        self.cell('final-authority', self.authority)
        require([r['id'] for r in self.cells] == self.planned, 'Complete predetermined cell ledger')
        summary = {'schemaVersion': 1, 'kind': 'R03CompletionLocalBatch', 'repositories': self.pins,
                   'matrixSha256': sha(ROOT / 'player-cases.json'), 'completionPlanSha256': sha(self.root / 'completion-plan.json'),
                   'cells': self.cells, 'retainedReferenceWorktrees': {k: str(v) for k, v in self.references.items()},
                   'result': 'ReturnRequired' if self.failed else 'EvidenceReadyForPrimaryReview',
                   'R03Accepted': False, 'H2Passed': False, 'pureInterpreterExpansionEnabled': False,
                   'qualificationApproved': False, 'fullLegacyRegressionAcceptance': False}
        result = finalize(self.root, summary)
        return 0 if result['result'] == 'EvidenceReadyForPrimaryReview' and result['sealStatus'] == 'Passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'output', 'unity', 'demo-commit'): parser.add_argument('--' + name, required=True)
    a = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', a.demo_commit) is not None, 'Latest exact pushed demo SHA required')
    raise SystemExit(CompletionBatch(a.workspace, a.output, a.unity, a.demo_commit).execute())
