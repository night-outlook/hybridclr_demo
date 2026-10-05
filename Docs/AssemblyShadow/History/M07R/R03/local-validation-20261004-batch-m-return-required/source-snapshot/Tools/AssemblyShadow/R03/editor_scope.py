"""Explicit isolated-Editor scope: keep all 754 executable package contracts.

The immutable D XML is an enumerated test-name catalog ONLY. It is never fresh
execution evidence. Exclude exactly one absent M01 asset contract; do not accept
arbitrary skipped aggregates or infer resource coverage from the filtered run.
"""
import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from batch_contract import require, sha

POLICY = 'R03IsolatedEditorScopeV1'
PACKAGE = '120bb01be680cec0375002a0823552d66d34b84c'
REFERENCE = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-d-return-required/batch/editor-results.xml'
REFERENCE_BLOB = '74da7de9e99e79aae01365f2c3dea5e49f812ef5'
EXCLUDED = 'HybridCLR.Editor.AssemblyShadow.Tests.ResourceAbiTests.FrozenDemoResourcesUseActualScriptGuidsAndOnlyAffectedBundles'
REASON = 'The frozen M01 demo assets are not present in this project.'
PREFIX = 'HybridCLR.Editor.AssemblyShadow.Tests.R03EvolutionContractTests.RealDllEvolutionContract'
CYCLE = 'HybridCLR.Editor.AssemblyShadow.Tests.GraphAndInputTests.CyclesReportClosedPath'
MISSING_ASSETS = ('Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab',
                  'Assets/AssemblyShadowDemo/Scenes/Business.unity',
                  'Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset')
TEST_FILTER = '!^' + re.escape(EXCLUDED) + '$'


def case_map(tree):
    require(tree.tag == 'test-run', 'Actual NUnit test-run XML required')
    result = {}
    for case in tree.iter('test-case'):
        name = case.get('fullname', '')
        require(name and name not in result, 'Missing or duplicate Editor test identity: ' + name)
        result[name] = case
    require(result, 'Nonzero real Editor test execution required')
    return result


def mandatory_names(required_ids):
    require(type(required_ids) is list and len(required_ids) == len(set(required_ids)) == 35,
            'Exactly 35 unique R03 contract IDs required')
    require(all(type(i) is str and re.fullmatch('[LM][0-9]{2}-[a-z0-9-]+', i) for i in required_ids),
            'Malformed R03 contract identity')
    return [PREFIX + '("' + i + '")' for i in required_ids] + [CYCLE]


def catalog(tree, required_ids):
    """Read a catalog, not a verdict. Caller authenticates its immutable bytes."""
    cases = case_map(tree)
    require(len(cases) == 755 and EXCLUDED in cases, 'Pinned Editor catalog changed')
    excluded = cases[EXCLUDED]
    reason = ''.join(excluded.itertext())
    require(excluded.get('result') in ('Skipped', 'Skipped:Ignored') and REASON in reason,
            'Pinned unavailable M01 fixture declaration changed')
    expected = sorted(set(cases) - {EXCLUDED})
    require(all(cases[n].get('result') == 'Passed' for n in expected), 'Unexpected catalog case state')
    mandatory = mandatory_names(required_ids)
    require(set(mandatory) <= set(expected), 'Missing mandatory R03 identity in catalog')
    return {'schemaVersion': 1, 'kind': POLICY, 'packageRevision': PACKAGE,
            'testFilter': TEST_FILTER, 'expectedCount': 754, 'expectedNames': expected,
            'requiredNames': mandatory, 'requiredIds': required_ids,
            'excluded': [{'fullname': EXCLUDED, 'coverage': 'NoCoverage', 'reason': REASON,
                          'missingAssets': list(MISSING_ASSETS)}],
            'referenceUse': 'Test-name catalog only; not execution evidence',
            'fullLegacyRegressionAcceptance': False}


def load_scope(demo, package_revision, required_ids):
    require(package_revision == PACKAGE, 'Editor scope requires the reviewed package revision')
    reference = Path(demo) / REFERENCE
    data = reference.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    require(blob == REFERENCE_BLOB, 'Immutable D Editor catalog bytes changed')
    scope = catalog(ET.fromstring(data), required_ids)
    scope.update(referencePath=REFERENCE, referenceBlob=blob, referenceSha256=sha(reference))
    return scope


def verify_scope_project(project):
    # An explicit fixture scope, not a runtime fallback based on test outcomes.
    present = [name for name in MISSING_ASSETS if (Path(project) / name).exists()]
    require(not present, 'Isolated fixture scope changed; review the M01 selection before running')
    return {'absentAssets': list(MISSING_ASSETS), 'coverage': 'NoCoverage', 'excludedTest': EXCLUDED}


def verify_editor(tree, scope):
    cases = case_map(tree)
    expected = set(scope['expectedNames'])
    require(scope['kind'] == POLICY and scope['testFilter'] == TEST_FILTER and
            len(expected) == scope['expectedCount'] == 754, 'Reviewed Editor scope required')
    missing, extra = sorted(expected - set(cases)), sorted(set(cases) - expected)
    require(not missing and not extra, 'Editor selection mismatch; missing=' + repr(missing[:6]) + '; extra=' + repr(extra[:6]))
    require(tree.get('result') == 'Passed' and not tree.get('label'), 'Selected Editor aggregate must be Passed')
    for field, value in (('total', 754), ('passed', 754), ('failed', 0), ('skipped', 0), ('inconclusive', 0)):
        require(tree.get(field) == str(value), 'Editor aggregate count mismatch: ' + field)
    require(all(c.get('result') == 'Passed' and not c.get('label') and c.find('failure') is None for c in cases.values()),
            'Every selected Editor case must pass without skips')
    require(set(mandatory_names(scope['requiredIds'])) == set(scope['requiredNames']) <= set(cases),
            'Exact mandatory Editor identities required')
    return {'kind': 'R03ScopedEditorVerification', 'schemaVersion': 1, 'result': 'Passed',
            'cases': 754, 'passed': 754, 'skipped': 0, 'r03RequiredIds': scope['requiredIds'],
            'testFilter': TEST_FILTER, 'excludedCoverage': scope['excluded'],
            'fullLegacyRegressionAcceptance': False, 'R03Accepted': False, 'H2Passed': False}
