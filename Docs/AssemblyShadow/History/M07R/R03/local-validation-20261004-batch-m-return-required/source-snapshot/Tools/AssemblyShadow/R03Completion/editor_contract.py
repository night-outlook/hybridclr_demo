"""New reviewed package source plus the exact existing 755-case test catalog.

The catalog supplies names only. Actual XML must establish all selected results;
no ignored test is ever counted as passed and historical H is not rewritten.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import require, sha
import editor_scope as prior
from run_local import git

REVIEWED_PACKAGE_FILES = frozenset((
 'Editor/AssemblyShadow/Metadata/PureInterpreterEligibility.cs',
 'Editor/AssemblyShadow/Metadata/PureInterpreterEligibility.cs.meta',
 'Editor/AssemblyShadow/Metadata/CompiledAssemblySet.cs',
 'Editor/AssemblyShadow/Metadata/DnlibAssemblyLoader.cs',
 'Tests/Editor/AssemblyShadow/SyntheticCompiledAssemblySet.cs',
 'Tests/Editor/AssemblyShadow/SyntheticCompiledAssemblySet.cs.meta',
 'Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs',
 'Tests/Editor/AssemblyShadow/PolicyTests.cs'))
PACKAGE_FILTER = '^HybridCLR\\.Editor\\.AssemblyShadow\\.Tests\\.'


def source_scope(demo, package, revision, required_ids, *, resource_complete):
    require(git(package, 'rev-parse', 'HEAD') == revision, 'Actual package revision')
    changed = set(filter(None, git(package, 'diff', '--name-only', prior.PACKAGE, revision).splitlines()))
    require(changed == REVIEWED_PACKAGE_FILES, 'Review any additional package change before selecting Editor tests')
    scope = prior.load_scope(demo, prior.PACKAGE, required_ids)
    scope['sourceCatalogPackageRevision'] = prior.PACKAGE
    scope['packageRevision'] = revision
    scope['reviewedPackageDelta'] = sorted(changed)
    scope['resourceComplete'] = resource_complete
    if resource_complete:
        scope['kind'] = 'R03ResourceCompleteEditorScopeV1'
        scope['expectedNames'] = sorted(scope['expectedNames'] + [prior.EXCLUDED])
        scope['expectedCount'] = 755
        scope['requiredNames'] = sorted(scope['requiredNames'] + [prior.EXCLUDED])
        scope['testFilter'] = PACKAGE_FILTER
        scope['excluded'] = []
    return scope


def verify(tree, scope):
    if not scope['resourceComplete']:
        # New package is separately bound above; the original exact identity and
        # zero-skip policy remains unchanged for the original small fixture.
        return prior.verify_editor(tree, scope)
    cases = prior.case_map(tree)
    require(scope['kind'] == 'R03ResourceCompleteEditorScopeV1' and scope['testFilter'] == PACKAGE_FILTER and
            scope['excluded'] == [] and scope['expectedCount'] == 755, 'Explicit resource-complete scope')
    require(set(cases) == set(scope['expectedNames']) and len(cases) == 755, 'Exact full package test inventory')
    require(prior.EXCLUDED in cases and set(scope['requiredNames']) <= set(cases), 'Real M01 test required')
    require(tree.get('result') == 'Passed' and not tree.get('label'), 'Actual resource-complete aggregate')
    for key, value in (('total', 755), ('passed', 755), ('failed', 0), ('skipped', 0), ('inconclusive', 0)):
        require(tree.get(key) == str(value), 'Editor count: ' + key)
    require(all(v.get('result') == 'Passed' and not v.get('label') and v.find('failure') is None for v in cases.values()),
            'Every resource-complete case must pass; no ignores')
    return {'kind': scope['kind'], 'result': 'Passed', 'cases': 755, 'skipped': 0,
            'm01Case': prior.EXCLUDED, 'm01SourceAssetContract': 'Passed',
            'fullLegacyRegressionAcceptance': False, 'R03Accepted': False, 'H2Passed': False}
