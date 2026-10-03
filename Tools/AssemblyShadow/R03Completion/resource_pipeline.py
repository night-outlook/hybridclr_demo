"""One fresh resource pipeline; production entry points and exact P05 restoration."""
import hashlib
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from unity_command import unity_command
from fixture_project import provision, regular, verify_sources
from fixture_authority import authenticate_copy, verify_graph, verify_installation
from editor_contract import source_scope, verify as verify_editor

METHODS = {'install': 'Install', 'compiler': 'CompilerPreflight', 'resources': 'Resources',
           'player-on': 'PlayerOn', 'player-off': 'PlayerOff', 'prepare': 'StructuralPrepare',
           'compile': 'StructuralCompile', 'restore': 'StructuralRestore', 'finalize': 'FinalizeFixtures',
           'integration': 'VerifyProductionEntries'}


def prepare(batch):
    project, config = provision(batch)
    batch.resource_config = config
    write(batch.root / 'resource-project.json', config)
    return verify_sources(project, config)


def command(batch, phase):
    config = batch.resource_config
    project = Path(config['projectPath'])
    log = batch.root / 'resource-logs' / (phase + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    require(not log.exists(), 'Resource phase cannot be retried')
    return [batch.unity, '-batchmode', '-nographics', '-quit', '-buildTarget', 'osx', '-projectPath', project,
            '-executeMethod', 'AssemblyShadowDemo.Editor.R03CompletionBuild.' + METHODS[phase],
            '-shadowBaselineId', config['baselineId'], '-shadowM07ResourceOutput', project / '_temp/AssemblyShadow/R03Resources',
            '-shadowValidationRoot', config['runPath'], '-logFile', log]


def phase(batch, name):
    config = batch.resource_config
    project, pins = authenticate_copy(batch, config)
    if name == 'prepare':
        run = Path(config['runPath'])
        require(not run.exists(), 'P05 transaction run must be unused')
        run.mkdir(parents=True)
        original = regular(project / 'ProjectSettings/ProjectSettings.asset').read_bytes()
        with (run / 'p05-project-settings.original').open('xb') as stream:
            stream.write(original)
    before = verify_sources(project, config, configured=name != 'install')
    receipt = unity_command(batch, command(batch, name), 7200 if name in ('player-on', 'player-off') else 3600)
    after = verify_sources(project, config, configured=True)
    path = Path(config['receiptRoot']) / (name + '.json')
    result = loads(regular(path).read_text())
    require(result.get('kind') == 'R03OriginalResourceBuildAdapter' and result.get('phase') == name and
            result.get('projectPath') == str(project) and result.get('baselineId') == config['baselineId'] and
            result.get('unityVersion') == '2022.3.62f2' and result.get('target') == 'StandaloneOSX', 'Source-bound phase receipt')
    require(result.get('sourcePinsSha256') == sha(project / 'ProjectSettings/AssemblyShadowSourcePins.json') and
            all(result.get(k) is False for k in ('expansionAuthorized', 'R03Accepted', 'H2Passed')), 'Phase must not authorize expansion or change sources')
    if name in ('player-on', 'player-off'):
        player = regular(result['playerReceipt'])
        require(player.is_relative_to(project / '_temp/AssemblyShadow') and sha(player) == result['playerReceiptSha256'], 'Exact newly produced Player receipt')
        setattr(batch, 'resource_on' if name == 'player-on' else 'resource_off', player)
    if name == 'finalize':
        for key, target in (('fixtureManifest', 'resource_manifest'), ('replayReceipt', 'resource_replay')):
            file = regular(result[key])
            require(file.is_relative_to(Path(config['runPath'])) and sha(file) == result[key + 'Sha256'], 'Exact fixture graph output')
            setattr(batch, target, file)
    return {'phaseReceipt': str(path), 'sha256': sha(path), 'unity': receipt, 'beforeSources': before, 'afterSources': after}


def restore_bytes(project, run):
    """Only the already-proved, exact P05 settings mutation may be restored.

    The production restore receipt binds its reserialized bytes. Preserve those
    bytes, restore the original copy, and emit the original expected wrapper
    receipt. Never edit the receipt to claim its hash was the original hash.
    """
    project, run = Path(project), Path(run)
    require(run.parent == project / '_temp/AssemblyShadow' and run.name.startswith('M02Validation-'), 'Owned P05 run')
    state_path = regular(run / 'p05-define-state.json'); state = loads(state_path.read_text())
    receipt_path = regular(run / 'p05-restored.json'); restored = loads(receipt_path.read_text())
    settings = regular(project / 'ProjectSettings/ProjectSettings.asset')
    original = regular(run / 'p05-project-settings.original')
    require(state['schemaVersion'] == 2 and restored['schemaVersion'] == 2 and
            state['projectDirectory'] == str(project) and state['runDirectory'] == str(run), 'Exact structural ownership')
    require(restored['stateSha256'] == sha(state_path) and restored['originalDefines'] == state['originalDefines'], 'Original production restore acknowledgement')
    require(sha(original) == state['originalSettingsSha256'] == restored['originalSettingsSha256'], 'Original settings backup binding')
    require(sha(settings) == restored['restoredSettingsSha256'], 'Concurrent settings edit: refuse overwrite')
    destination = run / 'p05-settings-restored.json'
    require(not destination.exists() and not (run / 'p05-unity-restored.bytes').exists(), 'No second restore')
    with (run / 'p05-unity-restored.bytes').open('xb') as stream: stream.write(settings.read_bytes())
    with settings.open('wb') as stream: stream.write(original.read_bytes())
    require(sha(settings) == state['originalSettingsSha256'], 'Exact settings restoration failed')
    write(destination, {'schemaVersion': 1, 'stateSha256': sha(state_path),
                        'originalSettingsSha256': state['originalSettingsSha256'],
                        'restoredSettingsSha256': restored['restoredSettingsSha256']})
    return {'receipt': str(destination), 'sha256': sha(destination), 'result': 'ExactOriginalBytesRestored'}


def restore(batch):
    config = batch.resource_config
    project, _ = authenticate_copy(batch, config)
    state = Path(config['runPath']) / 'p05-define-state.json'
    if not state.exists():
        # No state means Prepare never recorded authority to mutate defines.
        # This is cleanup only; failed/blocked compilation cells remain so.
        return {'cleanup': 'NoRecordedMutation', 'restorationCoverage': 'NotApplicable', 'sourceVerification': verify_sources(project, config, configured=True)}
    value = phase(batch, 'restore')
    value['byteRestoration'] = restore_bytes(project, Path(config['runPath']))
    return value


def graph(batch):
    batch.resource_context = verify_graph(batch, batch.resource_config, batch.resource_manifest,
                                        batch.resource_on, batch.resource_off, batch.resource_replay)
    return {'fixtureManifest': str(batch.resource_manifest), 'sha256': sha(batch.resource_manifest),
            'editorReplay': str(batch.resource_replay), 'editorReplaySha256': sha(batch.resource_replay),
            'installed': batch.resource_context['context']['installed'], 'profile': batch.resource_context['profile'],
            'newLinkedOnOffBuilds': True, 'historicalAppReuse': False}


def integration(batch):
    project, _ = authenticate_copy(batch, batch.resource_config)
    unity = unity_command(batch, command(batch, 'integration'), 3600)
    path = Path(batch.resource_config['receiptRoot']) / 'integration.json'
    value = loads(regular(path).read_text())
    require(value['kind'] == 'R03ProductionEntryIntegration' and value['schemaVersion'] == 1 and
            all(value[k] is False for k in ('runtimeProofExecuted', 'expansionAuthorized', 'R03Accepted', 'H2Passed')), 'Qualification/generation evidence is not runtime authorization')
    require([row['patchId'] for row in value['patches']] == ['P01', 'P02', 'P03', 'P04', 'P05'], 'All original complete-target fixtures')
    require(value['returnChangedRoots'] == [] and value['returnClosure'] == [], 'Complete restored target compared with installation baseline')
    for row in value['patches']:
        require(row['expansionAuthorized'] is False, 'No eligibility permission')
        for field, hash_field in (('patchManifest', 'patchManifestSha256'), ('eligibilityPath', 'eligibilitySha256')):
            source = regular(row[field]); require(source.is_relative_to(project) and sha(source) == row[hash_field], 'Production entry evidence binding')
        report = loads(Path(row['eligibilityPath']).read_text())
        require(report['kind'] == 'R03PureInterpreterEligibilityV1' and
                all(report[k] is False for k in ('expansionAuthorized', 'runtimeProofExecuted', 'qualificationApproved')),
                'Static qualification must remain explicitly non-authorizing')
        require(report['closure'] == row['closure'] and report['targetLoadOrder'] == row['loadOrder'], 'Qualification and production graph agreement')
    return {'path': str(path), 'sha256': sha(path), 'unity': unity, 'patches': 5,
            'returnToBaselineRoots': 0, 'qualificationGate': 'PendingIndependentReviewAndOwnerApproval',
            'sourceVerification': verify_sources(project, batch.resource_config, configured=True)}


def editor(batch, *, complete):
    project = Path(batch.resource_config['projectPath']) if complete else batch.builds['candidate-release']['project']
    required = [c['id'] for c in loads((batch.root / 'host/admission/results.json').read_text())['cases']]
    scope = source_scope(batch.workspace / 'hybridclr_demo', batch.workspace / 'hybridclr_unity',
                         batch.pins['hybridclr_unity'], required, resource_complete=complete)
    if complete:
        authenticate_copy(batch, batch.resource_config)
    folder = batch.root / ('resource-editor' if complete else 'focused-editor'); folder.mkdir()
    write(folder / 'scope.json', scope)
    result = {'result': 'Failed', 'kind': scope['kind'], 'R03Accepted': False, 'H2Passed': False}
    try:
        unity_command(batch, [batch.unity, '-batchmode', '-nographics', '-projectPath', project, '-runTests',
                              '-testPlatform', 'EditMode', '-testFilter', scope['testFilter'], '-testResults', folder / 'results.xml',
                              '-logFile', folder / 'Editor.log'], 3600)
        result = verify_editor(ET.parse(folder / 'results.xml').getroot(), scope)
        result.update(xml=str(folder / 'results.xml'), xmlSha256=sha(folder / 'results.xml'), scopeSha256=sha(folder / 'scope.json'))
        return result
    except Exception as error:
        result['error'] = str(error); raise
    finally:
        write(folder / 'verification.json', result)
