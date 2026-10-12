"""Pure validation of captured Bee result-processing evidence. Never changes BuildReport."""
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
    require(type(data) is dict and data.get('schemaVersion')==1 and
            data.get('kind')=='R03BeeResultObservationV1' and data.get('runtimeAcceptance') is False,
            'Native build observation schema')
    require(data.get('sourceManifestSha256')==manifest,'Observation must bind current build inputs')
    require(data.get('result')=='CapturedForAnalysis' and data.get('sameProcessor') is True and
            data.get('driverInitiallyAbsent') is True and data.get('limitsExceeded') is False,
            'Current untruncated BeeDriverResult identity required; unavailable does not mean success')
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
