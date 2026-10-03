"""Execute the real constructor helper and early exact Editor regression subset.

Host construction is not acquisition-policy execution. The independent Unity
XML proves the 18 actual fixture/test methods, before expensive native builds.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
from unity_command import unity_command

HERE = Path(__file__).resolve().parent


def constructor_contracts(batch):
    binary, intermediate = batch.root / 'bin/fixture-contracts', batch.root / 'obj/fixture-contracts'
    batch.command(build_arguments(HERE / 'FixtureContractTests/FixtureContractTests.csproj', binary, intermediate, batch.workspace / 'hybridclr_unity'))
    root = batch.root / 'fixture-constructor-host'
    batch.command(['dotnet', binary / 'FixtureContractTests.dll', '--output', root])
    data = loads((root / 'results.json').read_text())
    require(data['kind'] == 'R03SyntheticFixtureConstructorContracts' and data['result'] == 'Passed' and data['failures'] == 0,
            'Actual constructor/helper contracts must pass')
    require(len(data['cases']) == len({c['id'] for c in data['cases']}) == 12 and all(c['result'] == 'Passed' for c in data['cases']), 'Exactly twelve host constructor checks')
    require(data['unityEditorRun'] is False and data['qualificationAuthorized'] is False and data['expansionAuthorized'] is False,
            'Synthetic constructor evidence is not qualified input or Editor acceptance')
    return {'result': str(root / 'results.json'), 'sha256': sha(root / 'results.json'), 'cases': 12, 'unityEditorRun': False}


def roster():
    value = loads((HERE / 'fixture-constructor-cases.json').read_text())
    names = value['names']
    require(value['kind'] == 'R03LIConstructorRegressionRoster' and value['schemaVersion'] == 1 and
            len(names) == len(set(names)) == value['count'] == 18, 'Exact LI fixture roster')
    require(sum('.ManagedAcquisitionPolicyTests.' in n for n in names) == 17 and
            'HybridCLR.Editor.AssemblyShadow.Tests.PolicyTests.CompiledReferenceModulesNeedNotBeSnapshotDescriptors' in names,
            'Retain all eighteen actual failed-I identities')
    return names


def verify_editor(tree, names):
    require(tree.tag == 'test-run' and tree.get('result') == 'Passed' and not tree.get('label'), 'Actual passing Editor test-run required')
    cases = list(tree.iter('test-case'))
    require(len(cases) == 18 and {c.get('fullname') for c in cases} == set(names), 'Exact 18 Editor fixture tests; no omissions/substitutions')
    for key, count in (('total', 18), ('passed', 18), ('failed', 0), ('skipped', 0), ('inconclusive', 0)):
        require(tree.get(key) == str(count), 'Fixture count mismatch: ' + key)
    require(all(c.get('result') == 'Passed' and not c.get('label') and c.find('failure') is None for c in cases), 'Every fixture case must pass; no skips')
    return {'kind': 'R03LIEarlyEditorFixtures', 'result': 'Passed', 'cases': 18, 'unityEditorRun': True,
            'fullEditorRosterReplaced': False, 'R03Accepted': False, 'H2Passed': False}


def editor_preflight(batch):
    root = batch.root / 'fixture-constructor-editor'; root.mkdir()
    project = batch.root / 'projects/fixture-constructor-editor'
    require(not project.exists(), 'New fixture preflight project required')
    for part in ('Assets', 'Packages', 'ProjectSettings'): (project / part).mkdir(parents=True, exist_ok=True)
    (project / '.r03-isolated-project').write_text('R03 LI early fixture construction only.\n')
    (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2022.3.62f2\n')
    original = loads((batch.workspace / 'hybridclr_demo/Packages/manifest.json').read_text())['dependencies']
    dependencies = {k: v for k, v in original.items() if k.startswith('com.unity.modules.') or k in ('com.unity.test-framework', 'com.unity.ugui')}
    dependencies['com.code-philosophy.hybridclr'] = 'file:' + str(batch.workspace / 'hybridclr_unity')
    write(project / 'Packages/manifest.json', {'dependencies': dependencies, 'testables': ['com.code-philosophy.hybridclr']})
    names = roster(); pattern = '^(?:' + '|'.join(re.escape(n) for n in names) + ')$'
    write(root / 'scope.json', {'names': names, 'testFilter': pattern, 'rosterSha256': sha(HERE / 'fixture-constructor-cases.json'),
                              'packageRevision': batch.pins['hybridclr_unity'], 'fullEditorRosterReplaced': False})
    verdict = {'kind': 'R03LIEarlyEditorFixtures', 'result': 'Failed', 'R03Accepted': False, 'H2Passed': False}
    try:
        receipt = unity_command(batch, [batch.unity, '-batchmode', '-nographics', '-buildTarget', 'osx', '-projectPath', project,
                                '-runTests', '-testPlatform', 'EditMode', '-testFilter', pattern, '-testResults', root / 'results.xml',
                                '-logFile', root / 'Editor.log'], 3600)
        verdict = verify_editor(ET.parse(root / 'results.xml').getroot(), names)
        verdict.update(xmlSha256=sha(root / 'results.xml'), scopeSha256=sha(root / 'scope.json'), command=receipt)
        return verdict
    except Exception as error:
        verdict['error'] = str(error); raise
    finally:
        write(root / 'verification.json', verdict)
