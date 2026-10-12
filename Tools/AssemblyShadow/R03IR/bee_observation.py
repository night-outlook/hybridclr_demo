"""Pure validation of captured Bee result-processing evidence. Never changes BuildReport."""
import re
from batch_contract import require

NEEDLE = 'failed to allocate space to load shared cache'

def expected_errors(nodes):
    """UnityCsReference 2022.3 DefaultResultProcessor, not emitter attribution."""
    errors=[]
    for node in nodes:
        require(type(node) is dict and type(node.get('exitCode')) is int, 'Actual node record')
        output=node.get('output')
        require(output is None or isinstance(output,str), 'Raw node Output must be text or null')
        destination=node.get('outputDirectory') or node.get('outputFile') or ''
        for line in (output or '').replace('\r','\n').split('\n'):
            if line[:6].lower()=='error:':
                errors.append(destination+': '+line[6:].lstrip())
    return errors

def verify_observation(data, manifest):
    require(isinstance(manifest, str) and re.fullmatch(r'[0-9a-f]{64}', manifest) is not None,
            'Expected build manifest must be a complete SHA-256')
    require(type(data) is dict and type(data.get('schemaVersion')) is int and data['schemaVersion']==1 and
            data.get('kind')=='R03BeeResultObservationV1' and data.get('runtimeAcceptance') is False,
            'Native build observation schema')
    require(data.get('sourceManifestSha256')==manifest,'Observation must bind current build inputs')
    require(data.get('result')=='CapturedForAnalysis' and data.get('sameProcessor') is True and
            data.get('driverInitiallyAbsent') is True and data.get('limitsExceeded') is False and
            data.get('acquisition') == 'ScopedOriginalFactoryForwarderV1' and data.get('factoryRestored') is True and
            type(data.get('factoryCalls')) is int and 1 <= data['factoryCalls'] <= 64 and
            type(data.get('selectedFactorySequence')) is int and 1 <= data['selectedFactorySequence'] <= data['factoryCalls'],
            'Current untruncated BeeDriverResult identity required; unavailable does not mean success')
    # A true flag alone is not evidence of which original factory/processor ran.
    # These values are emitted by R03BeeObservation from the observed instances.
    # Hash syntax is checked here; actual SDK/source inventories bind the bytes.
    require(type(data.get('capturedProcessors')) is int and
            1 <= data['capturedProcessors'] <= data['factoryCalls'],
            'Captured processor count must agree with actual factory calls')
    require(data.get('error') in (None, ''), 'Captured observation must not retain an acquisition error')
    for key in ('moduleType', 'processorType'):
        require(isinstance(data.get(key), str) and 0 < len(data[key]) <= 4096 and
                data[key].strip() == data[key], 'Original factory/processor type identity required: ' + key)
    for key in ('moduleAssemblySha256', 'processorAssemblySha256'):
        require(isinstance(data.get(key), str) and
                re.fullmatch(r'[0-9a-f]{64}', data[key]) is not None,
                'Original factory/processor assembly SHA-256 required: ' + key)
    require(type(data.get('nodes')) is list and 0<len(data['nodes'])<=4096,'Bounded actual node list')
    require(type(data.get('buildErrors')) is int and data['buildErrors']>=0,'BuildReport error count retained')
    require(type(data.get('messages')) is list,'Raw observed logs required')
    predicted=expected_errors(data['nodes'])
    messages=[m['text'] for m in data['messages'] if type(m) is dict and isinstance(m.get('text'),str)]
    require(len(messages)==len(data['messages']),'Malformed log receipt')
    linked=[{'message':m,'matchesNodeOutput':m in predicted} for m in messages]
    return {'kind':'R03BeeResultProcessingAnalysis','result':'CapturedForAnalysis',
            'nodes':len(data['nodes']),'buildErrors':data['buildErrors'],'nodeErrorLines':len(predicted),
            'sharedCacheLogs':linked,'exactEmitter':'Unavailable; task output correlation is not emitter proof',
            'buildAcceptanceChanged':False,'runtimeAcceptance':False}
