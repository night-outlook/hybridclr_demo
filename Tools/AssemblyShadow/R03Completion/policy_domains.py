"""Verify fresh Unity source inventory separately from derived Player policy.

The diagnostic-projection regression is maintained in compile_lo_policy_checks.
This module accepts only a fresh, input-bound live Editor report.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from compiler_policy_inputs import regular

EDGES = (
    ('Unity.Burst', 'Unity.Burst.Unsafe'),
    ('Unity.RenderPipelines.Universal.Runtime', 'Unity.RenderPipelines.Universal.2D.Internal'),
    ('Unity.RenderPipelines.Universal.Runtime', 'Unity.RenderPipelines.Universal.Config.Runtime'),
)


def diagnostic_message(consumer, provider):
    return consumer + ' references an assembly removed from the captured Player build: ' + provider + '.'


def verify_live(path, project, receipt_root, baseline_snapshot_hash):
    """Consume a fresh, input-bound source-versus-Player policy report."""
    project, receipt_root = Path(project).resolve(), Path(receipt_root).resolve()
    path = regular(path)
    require(path.resolve() == receipt_root / 'compiler-policy-domains.json' and
            receipt_root.is_relative_to(project), 'Policy report must belong to this fresh project')
    report_hash = sha(path)
    value = loads(path.read_text())
    require(value['schemaVersion'] == 1 and value['kind'] == 'R03LiveSourcePolicyDomains' and value['result'] == 'Passed', 'Live policy-domain report')
    require(value['projectPath'] == str(project) and value['unityVersion'] == '2022.3.62f2' and
            value['target'] == 'StandaloneOSX' and value['baselineSnapshotHash'] == baseline_snapshot_hash,
            'Current Unity/project/installed baseline policy domain')
    require(value['sourceInventoryValidationPassed'] is True and value['linkedPolicyRejectedForSource'] is True and
            value['sourcePolicyUnchanged'] is True and value['freshUnityInventory'] is True and
            value['sourceDiagnostics'] == [] and all(value[key] is False for key in
            ('runtimeAcceptance', 'qualificationApproved', 'expansionAuthorized', 'R03Accepted', 'H2Passed')),
            'Actual source validation and guarded linked-domain rejection; no acceptance')
    require(value['guardProviders'] == [provider for _, provider in EDGES], 'All three filtered-reference guards')
    diagnostics = value['linkedPolicyDiagnostics']
    for consumer, provider in EDGES:
        require(any(row['code'] == 'RuntimeReferencesFilteredAssembly' and
                    row['message'] == diagnostic_message(consumer, provider) for row in diagnostics),
                'Missing actual source-domain rejection: ' + provider)
    files = []
    for field, basename, classification in (('sourcePolicy', 'source-policy.json', 0), ('linkedPolicy', 'linked-policy.json', 5)):
        policy_path = regular(value[field + 'Path'])
        require(policy_path.resolve() == receipt_root / 'compiler-policy-domains' / basename and
                sha(policy_path) == value[field + 'Sha256'], 'Policy byte/path binding: ' + field)
        policy = loads(policy_path.read_text()); rows = policy['assemblies']
        names = [row['name'].casefold() for row in rows]
        require(len(names) == len(set(names)), 'Unique policy assembly identities')
        require(field != 'sourcePolicy' or all(row['classification'] != 5 for row in rows), 'Source policy cannot contain BuildFiltered roles')
        for _, provider in EDGES:
            matches = [row for row in rows if row['name'].casefold() == provider.casefold()]
            require(len(matches) == 1 and type(matches[0]['classification']) is int and
                    matches[0]['classification'] == classification, 'Provider role in correct domain: ' + provider)
        files.append((policy_path, value[field + 'Sha256']))
    require(sha(path) == report_hash and all(sha(p) == digest for p, digest in files), 'Policy report/input custody')
    return {'path': str(path), 'sha256': report_hash, 'sourceInventoryValidationPassed': True,
            'filteredReferenceGuards': 3, 'freshUnityInventory': True, 'runtimeAcceptance': False}
