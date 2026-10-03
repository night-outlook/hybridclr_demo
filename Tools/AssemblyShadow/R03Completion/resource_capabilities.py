"""Reviewed resource-only dependency/profile contract. No optional DLL fallbacks."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments

PROFILE = 'R03ResourceCapabilitiesV1'
INCLUDED = ('Newtonsoft.Json', 'Unity.Burst.Unsafe', 'nunit.framework')
EXCLUDED = ('Unity.Collections.LowLevel.ILSupport', 'Unity.VisualScripting.Antlr3.Runtime')
# Exact non-module closure observed in J's resolved lock, now explicit roots.
# No Collections version is invented and no unused VisualScripting is imported.
PACKAGES = {'com.unity.burst': '1.8.21', 'com.unity.mathematics': '1.2.6',
            'com.unity.ext.nunit': '1.0.6', 'com.unity.nuget.newtonsoft-json': '3.2.1',
            'com.unity.render-pipelines.core': '14.0.12', 'com.unity.render-pipelines.universal': '14.0.12',
            'com.unity.render-pipelines.universal-config': '14.0.10', 'com.unity.searcher': '4.9.2',
            'com.unity.shadergraph': '14.0.12', 'com.unity.test-framework': '1.1.33', 'com.unity.ugui': '1.0.0'}
CODES = {'scoped-policy': 'Success', 'original-inherited': 'UnknownPrecompiledCapability',
         'excluded-collections': 'UnknownPrecompiledCapability', 'excluded-antlr': 'UnknownPrecompiledCapability',
         'unknown-plugin': 'UnknownPrecompiledCapability', 'source-as-plugin': 'InvalidPrecompiledCapability',
         'framework-as-plugin': 'InvalidPrecompiledCapability', 'nonruntime-plugin': 'InvalidCapabilityClassification',
         'ordinary-fixed-plugin': 'Success', 'ordinary-shadow-plugin': 'InvalidCapabilityClassification'}
INPUTS = ('Packages/manifest.json', 'Packages/packages-lock.json', 'ProjectSettings/AssemblyShadowSettings.asset',
          'ProjectSettings/ProjectSettings.asset', 'ProjectSettings/AssemblyShadowSourcePins.json', '.r03-completion-project')
SOURCES = ('R03ResourceCapabilityProfile.cs', 'R03CompletionInventoryContract.cs', 'M02Build.cs')


def dependency_profile(original, package):
    require(all(original.get(k) == PACKAGES[k] for k in ('com.unity.render-pipelines.universal', 'com.unity.test-framework', 'com.unity.ugui')),
            'Original resource direct package versions changed')
    modules = {k: v for k, v in original.items() if k.startswith('com.unity.modules.')}
    require(modules and all(v == '1.0.0' for v in modules.values()), 'Exact original built-in module versions')
    return {'dependencies': dict(modules, **PACKAGES, **{'com.code-philosophy.hybridclr': 'file:' + str(package)}),
            'testables': ['com.code-philosophy.hybridclr']}


def validate_packages(manifest, lock):
    deps = manifest['dependencies']; resolved = lock['dependencies']
    require(set(k for k in deps if not k.startswith('com.unity.modules.')) == {*PACKAGES, 'com.code-philosophy.hybridclr'}, 'Complete scoped dependency set')
    require(set(resolved) == set(deps), 'Unexpected or missing resolved package')
    for name, version in deps.items():
        expected = PACKAGES.get(name, '1.0.0' if name.startswith('com.unity.modules.') else version)
        require(version == expected and resolved[name]['version'] == expected, 'Resolved version mismatch: ' + name)
    return True



def reconstruct_inventory(groups, unity):
    """Independent replay of production's inventory rules, from captured Unity arrays."""
    def canonical(value):
        value = Path(value).name
        return value[:-4] if value.lower().endswith('.dll') else value
    player = [r for r in groups if r['mode'] == 'Player']
    production = [r for r in groups if r['mode'] == 'PlayerWithoutTestAssemblies']
    names = {canonical(r['name']).lower() for r in production}
    result = {}
    for r in player:
        name = canonical(r['name']); key = name.lower()
        require(key not in result, 'Duplicate case-insensitive Player assembly')
        result[key] = (name, 'TestOnly' if key not in names else 'EditorOnly' if 'EditorAssembly' in r['flags'] else 'Runtime', False)
    require(names <= set(result), 'Production source absent from full Player inventory')
    contents = Path(unity).parents[1]
    for r in production + player:
        for reference in r['compiledReferences']:
            name = canonical(reference); key = name.lower()
            if key in result: continue
            framework = Path(reference).is_relative_to(contents)
            result[key] = (name, 'Reference' if framework else 'Runtime' if canonical(r['name']).lower() in names else 'TestOnly', not framework)
    return result


def verify_report(path, batch, project):
    path, project = Path(path), Path(project)
    require(path.parent == Path(batch.resource_config['receiptRoot']), 'Exact capability receipt directory')
    require(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)), 'Regular owned report required')
    report = loads(path.read_text())
    require(report.get('kind') == 'R03ActualTargetCapabilityContract' and report.get('schemaVersion') == 1 and report.get('result') == 'Passed', 'Actual policy contract must pass')
    require(report.get('profile') == PROFILE and report.get('projectPath') == str(project) and report.get('baselineId') == batch.resource_config['baselineId'], 'Policy authority identity')
    require(report.get('unityVersion') == '2022.3.62f2' and report.get('target') == 'StandaloneOSX' and report.get('architecture') == 'arm64', 'Exact active platform')
    require(report.get('unityEditorRun') is True and report.get('snapshotCompilationRun') is False and
            all(report.get(k) is False for k in ('R03Accepted', 'H2Passed', 'expansionAuthorized')), 'Actual inventory is not compiled or runtime acceptance')
    require(report.get('consumer') == 'AssemblyShadowSettingsUtil.CreatePolicyConfiguration/BuildCompilerInventory/BuildCapabilities', 'Actual production policy consumer')
    validate_packages(loads((project / INPUTS[0]).read_text()), loads((project / INPUTS[1]).read_text()))
    for field in ('before', 'after'):
        rows = report.get(field, [])
        require(len(rows) == len(INPUTS) and {r['path'] for r in rows} == set(INPUTS), 'Complete policy input hashes')
        require(all(sha(project / r['path']) == r['sha256'] for r in rows), 'Policy consumer changed input')
    require(report['before'] == report['after'], 'Consumer controls must not mutate configured inputs')
    rows = report.get('sourceFiles', [])
    require(len(rows) == len(SOURCES) and {r['path'] for r in rows} == set(SOURCES), 'Complete actual consumer sources')
    for r in rows:
        require(sha(project / 'Assets/AssemblyShadowDemo/Editor' / r['path']) == r['sha256'], 'Consumer source mismatch')
    inventory = report['inventory']; caps = {r['name']: r for r in inventory}
    require(len(caps) == len(inventory) and len(caps) > len(INCLUDED), 'Full derived inventory, not hand-authored subset')
    require(all(n not in caps for n in EXCLUDED), 'Excluded provider unexpectedly in active target; scope review required')
    require(all(n in caps and caps[n]['isPrecompiled'] is True and caps[n]['classification'] == 'Runtime' for n in INCLUDED), 'Required fixed runtime plugins missing/misclassified')
    audited = report['declarations']
    require(len(audited) == 5 and {r['name'] for r in audited} == {*INCLUDED, *EXCLUDED}, 'All inherited declarations must be audited')
    require(all(r['included'] == (r['name'] in INCLUDED) and r['present'] == r['included'] and r['isShadowCapable'] is False for r in audited), 'Explicit inclusion/exclusion contract')
    groups = report['compilerAssemblies']
    require({r['mode'] for r in groups} == {'Player', 'PlayerWithoutTestAssemblies'} and len({(r['mode'],r['name']) for r in groups}) == len(groups), 'Both actual Unity inventories required')
    rebuilt = reconstruct_inventory(groups, batch.unity)
    require({r['name'].lower(): (r['name'], r['classification'], r['isPrecompiled']) for r in inventory} == rebuilt, 'Complete inventory must reproduce from actual compiler arrays')
    policy = loads(report['policyJson'])
    require(policy['rejectUnknownReflectionDependencies'] is True and policy['enforceResourceAbi'] is True, 'Policy guards disabled')
    declared = [r for r in policy['assemblies'] if r['isPrecompiled'] and r['capabilityDeclared']]
    require(len(declared) == len(INCLUDED) and {r['name'] for r in declared} == set(INCLUDED), 'Full policy precompiled declarations')
    require(all(r['classification'] == 0 and r['isShadowCapable'] is False and r['isBootstrap'] is False for r in declared), 'Policy classification/ownership drift')
    referenced = {p for r in groups for p in r['compiledReferences']}
    files = report['referenceFiles']; require(len(files) == len(referenced) and {r['path'] for r in files} == referenced, 'All referenced compiler DLL bytes required')
    for r in files:
        f = Path(r['path']); require(f.is_file() and f.stat().st_size == r['size'] and sha(f) == r['sha256'], 'Referenced DLL changed')
    cases = report['cases']; require(len(cases) == len(CODES) and {r['id'] for r in cases} == set(CODES), 'All policy positive/negative controls required')
    for r in cases:
        require(r['expectedCode'] == r['observedCode'] == CODES[r['id']] and r['result'] == 'Passed', 'Exact production guard code')
        f = Path(r['path']); require(f.parent == path.parent / 'capability-inputs' and f.is_file() and not f.is_symlink() and sha(f) == r['sha256'], 'Owned control bytes')
    return {'path': str(path), 'sha256': sha(path), 'cases': len(cases), 'inventory': len(inventory),
            'declarationsAudited': 5, 'runtimeAcceptance': False}


def host_contracts(batch):
    binary, intermediate = batch.root / 'bin/capability-profile', batch.root / 'obj/capability-profile'
    batch.command(build_arguments(HERE / 'CapabilityProfileTests/CapabilityProfileTests.csproj', binary, intermediate, batch.workspace / 'hybridclr_unity'))
    root = batch.root / 'capability-profile-host'
    batch.command(['dotnet', binary / 'CapabilityProfileTests.dll', '--output', root])
    result = loads((root / 'results.json').read_text())
    require(result['result'] == 'Passed' and len(result['cases']) == 20 and all(r['result'] == 'Passed' for r in result['cases']), 'All twenty actual profile-core tests')
    require(result['unityEditorRun'] is False and result['runtimeAcceptance'] is False, 'Host profile is not target inventory')
    return {'path': str(root / 'results.json'), 'sha256': sha(root / 'results.json'), 'cases': 20}
