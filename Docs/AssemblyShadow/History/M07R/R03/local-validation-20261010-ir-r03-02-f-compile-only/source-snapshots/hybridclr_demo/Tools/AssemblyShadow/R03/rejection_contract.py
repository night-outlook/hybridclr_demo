"""Rejected-stage observation must preserve the original failure, not restore it.

Whole raw diagnostic documents are retained. Their transaction/error projection
and the entire recovery document must be invariant across capacity failure and
two full reads. Ordinary-class enumeration can grow due to managed observation;
it is deliberately not asserted to be the immutable transaction snapshot.
"""
import hashlib
from batch_contract import fields, integer, loads, require, RECOVERY_FIELDS
from runtime_contract import probe_header, verify_fence

OBSERVATION = 'schemaVersion policy before afterSmall afterFirst afterSecond smallCapacity smallReturn firstReturn secondReturn repeatedProbe'
STATE = 'stateCode diagnosticsCode diagnostics recoveryCode recovery'
TERMINAL = '''schemaVersion state stateCode lastError detail baselineBuildId patchId generation expected staged retainedBytes
closureLoadOrder stableAotNames commitOrder assemblies events baselineUses'''.split()


def terminal(value, request):
    fields(value, STATE, 'Rejected observation state')
    require(type(value['stateCode']) is int and value['stateCode'] == 8 and
            type(value['diagnosticsCode']) is int and value['diagnosticsCode'] == 0 and
            type(value['recoveryCode']) is int and value['recoveryCode'] == 0,
            'Original rejected state and diagnostics must remain available')
    d, r = loads(value['diagnostics']), loads(value['recovery'])
    require(type(d) is dict and set(TERMINAL) <= set(d), 'Complete immutable transaction projection')
    require(type(d['lastError']) is int and d['lastError'] == 16 and d['stateCode'] == 8 and d['state'] == 'Failed' and
            type(d['generation']) is int and d['generation'] == 0 and d['commitOrder'] == [] and
            type(d['detail']) is str and 'NativeLayoutAdmissionV1' in d['detail'],
            'Original prepublication error 16 must not be replaced')
    require(d['baselineBuildId'] == request['baselineId'] and d['patchId'] == 'R03-' + request['runId'], 'Rejected transaction identity')
    require(type(d['assemblies']) is list and all(a.get('published') is False and
            a.get('moduleInitializerAttempted') is False and a.get('moduleInitializerRan') is False for a in d['assemblies']),
            'Observation cannot publish or initialize rejected assemblies')
    fields(r, RECOVERY_FIELDS, 'Rejected recovery observation')
    require(type(r['terminalFailureCode']) is int and r['terminalFailureCode'] == 16 and r['stateCode'] == 8 and
            r['published'] is False and r['abortAllowed'] is False and r['disposition'] == 'RestartRequired',
            'Original terminal recovery must be retained')
    return {k: d[k] for k in TERMINAL}, r


def verify_rejection_observation(raw, request):
    require(type(raw['rejectionProbe']) is str and raw['rejectionProbe'], 'Rejected observation receipt required')
    o = loads(raw['rejectionProbe']); fields(o, OBSERVATION, 'Rejected probe observation')
    require(type(o['schemaVersion']) is int and o['schemaVersion'] == 1 and
            o['policy'] == 'R03RejectedProbeNonMutationV1', 'Rejected probe observation policy')
    require(type(o['smallCapacity']) is int and o['smallCapacity'] == 16 and
            type(o['smallReturn']) is int and o['smallReturn'] == -2, 'Named insufficient-capacity control')
    captures = ['before', 'afterSmall', 'afterFirst', 'afterSecond']
    bound = [terminal(o[k], request) for k in captures]
    bound.append(terminal(dict(stateCode=raw['finalState'], diagnosticsCode=raw['diagnosticsCode'],
                              diagnostics=raw['diagnostics'], recoveryCode=raw['recoveryCode'], recovery=raw['recovery']), request))
    require(all(b == bound[0] for b in bound[1:]), 'Probe observation mutated terminal transaction/recovery')
    for key, text in (('firstReturn', raw['runtimeProbe']), ('secondReturn', o['repeatedProbe'])):
        require(type(text) is str and integer(o[key], 1) and o[key] < 131072 and len(text.encode('utf-8')) == o[key],
                'Full native read length and raw bytes must agree')
    first, second = probe_header(raw['runtimeProbe']), probe_header(o['repeatedProbe'])
    for p in (first, second):
        require(p['used'] is False and p['sealed'] is False and type(p['generation']) is int and p['generation'] == 0 and
                type(p['ownerThread']) is int and p['ownerThread'] == 0 and
                p['samples'] == [] and p['events'] == [], 'Rejected observation must not begin a warm session')
        require(p['target'] == dict(physical='0x0', assembly='', namespace='', name='', typeKey=''),
                'Rejected observation has no published warm target')
        require(1 <= len(p['layouts']) <= 32, 'Retained rejected-stage rows cannot be omitted')
        verify_fence(p, False)
    require(first['layouts'] == second['layouts'], 'Immutable captured layout identity changed on repeated read')
    # Do not claim the retained row is the failing row: rejection may precede
    # RecordLayout for that type, leaving only prior successfully observed rows.
    return {'policy': o['policy'], 'terminalFailureCode': 16, 'captures': 4, 'capacityControl': -2,
            'fullReads': 2, 'layoutRows': len(first['layouts']), 'layoutIdentityPolicy': 'R03OwnedLayoutIdentityV1',
            'terminalUnchanged': True, 'fullReadHashes': [hashlib.sha256(t.encode()).hexdigest()
                for t in (raw['runtimeProbe'], o['repeatedProbe'])], 'failingRowIdentified': False}
