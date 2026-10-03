"""Independent schema and actual Unity consumer receipt checks; never repair input.

The Python screen catches document-shape errors before Editor launch. Only the
separate real ShadowSourcePins.Read receipt proves Unity's native deserialization.
"""
import os
from pathlib import Path
import re
from batch_contract import loads, require, sha

PLATFORM = {'unityVersion': '2022.3.62f2', 'target': 'StandaloneOSX', 'architecture': 'arm64'}
REPOSITORIES = {'demo': 'hybridclr_demo', 'hybridclr': 'hybridclr', 'hybridclrUnity': 'hybridclr_unity', 'il2cppPlus': 'il2cpp_plus'}
CODES = {'generated': 'Success', 'roundtrip': 'Success', 'missing-architecture': 'SourcePinTarget',
         'wrong-architecture': 'SourcePinTarget', 'wrong-target': 'SourcePinTarget', 'wrong-unity': 'SourcePinTarget',
         'wrong-schema': 'SourcePinSchema', 'bad-revision': 'InvalidSourcePin', 'missing-repository': 'InvalidSourcePin',
         'wrong-build-source': 'BuildSourceProvenanceMismatch'}
INPUTS = ('ProjectSettings/AssemblyShadowSourcePins.json', 'ProjectSettings/AssemblyShadowSettings.asset',
          'ProjectSettings/ProjectSettings.asset', '.r03-completion-project')


def validate_document(value, batch, project):
    require(type(value) is dict and set(value) == {'schemaVersion', *PLATFORM, *REPOSITORIES}, 'Complete production source-pin fields required')
    require(type(value['schemaVersion']) is int and value['schemaVersion'] == 1, 'Exact source-pin schema')
    require(all(value[k] == v for k, v in PLATFORM.items()), 'Source-pin Unity/target/architecture mismatch')
    for field, repo in REPOSITORIES.items():
        pin = value[field]
        require(type(pin) is dict and set(pin) == {'url', 'revision', 'localPath'}, 'Complete repository pin: ' + field)
        require(pin['url'] == 'https://github.com/night-outlook/' + repo + '.git' and
                type(pin['revision']) is str and re.fullmatch('[0-9a-f]{40}', pin['revision']) is not None and
                pin['revision'] == batch.pins[repo], 'Exact repository revision/URL: ' + field)
        require(type(pin['localPath']) is str and pin['localPath'] == os.path.relpath(batch.workspace / repo, project),
                'Exact relative owning repository: ' + field)
    return value


def verify_report(path, batch, project):
    project, path = Path(project), Path(path)
    report = loads(path.read_text())
    require(report.get('kind') == 'R03ProductionSourcePinContract' and report.get('schemaVersion') == 1 and
            report.get('result') == 'Passed', 'Actual source-pin consumer report must pass')
    require(report.get('projectPath') == str(project) and report.get('baselineId') == batch.resource_config['baselineId'], 'Consumer project/baseline')
    require(all(report.get(k) == v for k, v in PLATFORM.items()), 'Consumer platform tuple')
    require(report.get('consumer') == 'HybridCLR.Editor.AssemblyShadow.ShadowSourcePins.Read' and
            report.get('serialization') == 'UnityEngine.JsonUtility' and report.get('unityEditorRun') is True and
            report.get('nativeInstallationRun') is False, 'Actual pre-install production deserializer is required')
    require(report.get('R03Accepted') is False and report.get('H2Passed') is False and
            report.get('expansionAuthorized') is False, 'Consumer check cannot authorize runtime changes')
    rows = report.get('cases', [])
    require(type(rows) is list and len(rows) == len(CODES) and {r.get('id') for r in rows} == set(CODES), 'Exact consumer positive/negative cases')
    input_path = project / INPUTS[0]
    validate_document(loads(input_path.read_text()), batch, project)
    for row in rows:
        require(row.get('observedCode') == row.get('expectedCode') == CODES[row['id']] and row.get('result') == 'Passed',
                'Exact source-pin rejection code: ' + row['id'])
        p = Path(row['path'])
        require(p.is_file() and not any(x.is_symlink() for x in (p, *p.parents)) and
                (p == input_path if row['id'] == 'generated' else p.parent == path.parent / 'source-pin-contract-inputs'), 'Owned source-pin contract input')
        require(row.get('sha256') == sha(p), 'Consumed source-pin input bytes')
    for label in ('before', 'after'):
        inputs = report.get(label, [])
        require(len(inputs) == len(INPUTS) and {r.get('path') for r in inputs} == set(INPUTS), 'Complete consumer input inventory')
        require(all(r.get('sha256') == sha(project / r['path']) for r in inputs), 'Consumer modified input: ' + label)
    require(report['before'] == report['after'], 'Preflight must not modify project settings/pins')
    require(re.fullmatch('[0-9a-f]{64}', report.get('runtimeAbiHash', '')) is not None, 'Actual ABI hash required')
    return {'result': str(path), 'sha256': sha(path), 'cases': len(CODES), 'serialization': report['serialization'],
            'unityEditorRun': True, 'nativeInstallationRun': False, 'runtimeAcceptance': False}
