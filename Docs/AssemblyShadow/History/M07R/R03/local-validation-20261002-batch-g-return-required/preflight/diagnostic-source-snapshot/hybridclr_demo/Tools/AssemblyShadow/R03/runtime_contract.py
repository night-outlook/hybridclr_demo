"""Strict native-window/attribution contract, never a +1 counter allowance.

Historical broad snapshots remain visible and must match exact native observer
boundaries. Every cold delta must have a full key/site/thread attribution. The
allocation loop still admits zero new proof/layout work globally.
"""
from collections import Counter
import re
from batch_contract import fields, integer, loads, require

COLD = ('admissionCacheMisses', 'admissionProofAttempts', 'admissionProofRejections',
        'admissionEntries', 'admissionRetainedBytes', 'admissionUnready')
COUNTERS = ('admissionCacheHits', 'baselineStateChecks', 'fieldWorkspaceBuilds',
            'interfaceWorkspaceBuilds', 'layoutCheckCalls', 'genericContextChecks') + COLD
PROBE_FIELDS = '''schemaVersion available policy used sealed invalid overflow generation ownerThread target eventCapacity samples events layouts producerFence runtimeAcceptance'''
TYPE = 'physical assembly namespace name typeKey'
SAMPLE = 'label eventEnd thread saturated droppedThreads counters'
EVENT = 'index metric amount phase thread generation domain context site type producer'
FENCE = 'policy requested acquired released expired invalid drained admitted completed deferred deferredCompleted ownerOsThread elapsedMicros leaseMs'
LAYOUT = '''baseline target fieldsChanged baselineReady targetReady targetDefinitionReady physicalProof
sourceSizeInited targetSizeInited sourcePending targetPending baselineInitialized baselineVtable baselineCctor
targetInitialized targetVtable targetCctor sourceSize targetSize sourceNativeSize targetNativeSize sourceFieldCount
targetFieldCount truncated error sourceOffsets sourceAttrs targetOffsets targetAttrs targetStorage
baselineInitializedAtRead baselineVtableAtRead baselineCctorAtRead'''


def physical_type(value, *, target=False, assembly=None):
    fields(value, TYPE, 'Native physical type')
    require(type(value['physical']) is str and re.fullmatch(r'0x[0-9a-f]+', value['physical']) and
            int(value['physical'], 16) > 0, 'Actual non-null native key required')
    for k in ('assembly', 'name', 'typeKey'):
        require(type(value[k]) is str and value[k], 'Cold key identity unavailable: ' + k)
    require(type(value['namespace']) is str, 'Native namespace')
    if target:
        require(value['assembly'] == assembly and value['namespace'] == 'R03' and value['name'] == 'Node', 'Measured target identity')


def probe_header(text):
    p = loads(text)
    fields(p, PROBE_FIELDS, 'Runtime probe')
    require(type(p['schemaVersion']) is int and p['schemaVersion'] == 2 and p['available'] is True and p['policy'] == 'R03ExactAllocationWindowV1' and
            p['runtimeAcceptance'] is False and p['invalid'] is False and p['overflow'] is False,
            'Complete bounded native probe required')
    require(type(p['events']) is list and type(p['samples']) is list and type(p['layouts']) is list, 'Native probe collections')
    return p


def analyze_window(text, before, after, assembly):
    p = probe_header(text)
    require(p['used'] is True and p['sealed'] is True and integer(p['generation'], 1) and integer(p['ownerThread'], 1), 'One sealed native interval')
    physical_type(p['target'], target=True, assembly=assembly)
    samples, events = p['samples'], p['events']
    require(type(p['eventCapacity']) is int and p['eventCapacity'] == 128 and len(events) <= 128 and len(samples) == 6, 'Bounded trace shape')
    require([s.get('label') for s in samples] == [0, 10, 1, 2, 11, 3], 'Exact observer/loop boundary order')
    last_end = 0
    for s in samples:
        fields(s, SAMPLE, 'Native boundary')
        require(s['thread'] == p['ownerThread'] and integer(s['thread'], 1) and s['saturated'] is False and integer(s['droppedThreads']) and s['droppedThreads'] == 0,
                'Owner and complete counter coverage')
        require(integer(s['eventEnd']) and last_end <= s['eventEnd'] <= len(events), 'Monotonic event boundaries')
        last_end = s['eventEnd']
        fields(s['counters'], ' '.join(COUNTERS), 'Native counters')
        require(all(integer(v) for v in s['counters'].values()), 'Nonnegative integer native counters')
    require(samples[0]['eventEnd'] == 0 and samples[-1]['eventEnd'] == len(events), 'Complete event retention')
    for i, e in enumerate(events):
        fields(e, EVENT, 'Cold allocation event')
        require(e['index'] == i and type(e['index']) is int and e['metric'] in COLD and integer(e['amount'], 1), 'Exact cold event')
        require(integer(e['generation'], 1) and e['generation'] == p['generation'] and type(e['domain']) is int and e['domain'] == 1 and e['context'] == '0x0' and integer(e['thread'], 1), 'Complete admission key/thread')
        require(type(e['site']) is str and e['site'] and e['site'] != '<unspecified>' and len(e['site'].encode()) < 128, 'Full allocation site')
        physical_type(e['type'])
        producer = e['producer']; fields(producer, 'osThread recognizedArrayPool finalizerType callback', 'Cold producer context')
        require(integer(producer['osThread']) and type(producer['recognizedArrayPool']) is bool, 'Producer thread and qualification types')
        if producer['finalizerType'] is not None: physical_type(producer['finalizerType'])
        if producer['callback'] is not None:
            fields(producer['callback'], 'name token declaringType', 'Finalizer callback')
            require(type(producer['callback']['name']) is str and producer['callback']['name'] and integer(producer['callback']['token'], 1), 'Actual callback metadata')
            physical_type(producer['callback']['declaringType'])
        phase = 1 if i < samples[2]['eventEnd'] else 2 if i < samples[3]['eventEnd'] else 3
        require(e['phase'] == phase and type(e['phase']) is int, 'Event phase/boundary agreement')
    # Reconcile EVERY consecutive native span, not just a final net delta.
    for a, b in zip(samples, samples[1:]):
        for k in COUNTERS:
            require(b['counters'][k] >= a['counters'][k], 'Monotonic native metric: ' + k)
        tally = Counter()
        for e in events[a['eventEnd']:b['eventEnd']]: tally[e['metric']] += e['amount']
        for k in COLD:
            require(b['counters'][k] - a['counters'][k] == tally[k], 'Unattributed native delta: ' + k)
    for raw, sample in ((before, samples[1]), (after, samples[4])):
        require(all(raw[k] == sample['counters'][k] for k in COUNTERS), 'Broad managed/native snapshot binding')
    a, b = samples[2]['counters'], samples[3]['counters']
    require(b['admissionCacheHits'] - a['admissionCacheHits'] >= 10000 and
            b['baselineStateChecks'] - a['baselineStateChecks'] >= 10000,
            'Exact warm loop retains certificate hits and per-allocation baseline checks')
    return p, a, b


def verify_fence(p, required):
    f = p['producerFence']; fields(f, FENCE, 'Producer lease')
    require(f['policy'] == 'R03ArrayPoolFinalizerFenceV1', 'Exact producer-isolation policy')
    for k in ('requested', 'acquired', 'released', 'expired', 'invalid', 'drained'):
        require(type(f[k]) is bool, 'Producer lease boolean: ' + k)
    for k in ('admitted', 'completed', 'deferred', 'deferredCompleted', 'ownerOsThread', 'elapsedMicros', 'leaseMs'):
        require(integer(f[k]), 'Producer lease integer: ' + k)
    require(not f['expired'] and not f['invalid'] and f['completed'] <= f['admitted'] and f['deferredCompleted'] <= f['deferred'], 'Producer lease did not expire or corrupt')
    require(f['requested'] is required, 'Requested isolation must match the exact witness mode')
    if required:
        require(f['acquired'] and f['released'] and f['drained'] and f['ownerOsThread'] > 0 and
                f['leaseMs'] == 5000 and f['elapsedMicros'] < 5000000 and f['deferredCompleted'] == f['deferred'],
                'Bounded completed producer lease and drained deferred work required')
    else:
        require(not f['acquired'] and not f['released'] and not f['drained'] and f['leaseMs'] == 0 and
                f['elapsedMicros'] == 0 and f['ownerOsThread'] == 0 and f['deferred'] == 0, 'Natural control must not isolate or defer callbacks')
    return f


def verify_warm(text, before, after, assembly):
    p, a, b = analyze_window(text, before, after, assembly)
    fence = verify_fence(p, True)
    samples, events = p['samples'], p['events']
    for k in COLD + ('fieldWorkspaceBuilds', 'interfaceWorkspaceBuilds', 'layoutCheckCalls'):
        require(b[k] == a[k], 'Repeated exact-loop proof work: ' + k)
    broad = events[samples[1]['eventEnd']:samples[4]['eventEnd']]
    require(all(e['phase'] in (1, 3) and e['type']['physical'] != p['target']['physical'] and
                tuple(e['type'][k] for k in ('assembly', 'namespace', 'name')) !=
                tuple(p['target'][k] for k in ('assembly', 'namespace', 'name')) for e in broad),
            'Target proof or cold work leaked into the measured loop')
    return {'policy': p['policy'], 'exactLoopProofDelta': 0, 'broadColdEvents': broad,
            'broadCounterDelta': {k: after[k] - before[k] for k in COUNTERS},
            'target': p['target'], 'ownerThread': p['ownerThread'], 'producerFence': fence, 'runtimeAcceptance': False}


def verify_producer_control(text, before, after, assembly):
    """An unisolated diagnostic, NOT a passed warm certificate or a tolerance.

    Full publication/business/method/layout validation is performed by the
    caller. The original zero-all-thread test's observed verdict is retained.
    """
    p, a, b = analyze_window(text, before, after, assembly)
    verify_fence(p, False)
    for k in ('fieldWorkspaceBuilds', 'interfaceWorkspaceBuilds', 'layoutCheckCalls'):
        require(a[k] == b[k], 'Natural control repeated physical proof work')
    loop = [e for e in p['events'] if e['phase'] == 2]
    for e in p['events']:
        require(e['type']['physical'] != p['target']['physical'] and e['type']['typeKey'] != p['target']['typeKey'], 'Natural control must not hide target proof')
        if e['phase'] != 2: continue  # Unrelated observer work remains fully recorded.
        c = e['producer']; callback = c['callback']; finalizer = c['finalizerType']
        require(e['thread'] != p['ownerThread'] and e['site'] == 'Object::NewAllocSpecific', 'Only identified concurrent producer evidence is admissible in this control')
        require(c['recognizedArrayPool'] and c['osThread'] > 0 and finalizer is not None and callback is not None, 'Actual native finalizer and delegate identity required')
        require((finalizer['assembly'], finalizer['namespace'], finalizer['name']) == ('mscorlib', 'System', 'Gen2GcCallback'), 'Pinned Gen2 callback producer')
        owner = callback['declaringType']
        require((owner['assembly'], owner['namespace'], owner['name']) ==
                ('mscorlib', 'System.Buffers', 'TlsOverPerCoreLockedStacksArrayPool`1') and
                callback['name'] == 'Gen2GcCallbackFunc', 'Actual ArrayPool trimming delegate')
        require(e['type']['assembly'] == 'mscorlib' and e['type']['name'] == 'Enumerator' and
                'ConditionalWeakTable' in e['type']['typeKey'] and 'Enumerator' in e['type']['typeKey'], 'Full nested/generic Enumerator owner must be visible')
        require(e['metric'] not in ('admissionProofRejections', 'admissionUnready'), 'Producer control cannot hide proof rejection or unreadiness')
    count = sum(e['amount'] for e in loop if e['metric'] == 'admissionCacheMisses')
    return {'policy': 'R03NaturalProducerControlV1', 'identifiedLoopAdmissions': count,
            'observation': 'ExpectedContaminationObserved' if count else 'NoContaminationObserved',
            'unisolatedWarmCertificate': 'Failed' if count else 'Passed',
            'allColdEvents': p['events'], 'exactLoopDelta': {k: b[k] - a[k] for k in COUNTERS},
            'runtimeAcceptance': False}



def verify_primitive_layout(text):
    p = probe_header(text)
    rows = [x for x in p['layouts'] if x.get('target', {}).get('assembly') == 'R03Contract' and
            x.get('target', {}).get('namespace') == 'R03' and x.get('target', {}).get('name') == 'Node']
    require(len(rows) == 1, 'One prepublication primitive-layout witness')
    row = rows[0]; fields(row, LAYOUT, 'Prepublication layout witness')
    physical_type(row['baseline'], target=True, assembly='R03Contract')
    physical_type(row['target'], target=True, assembly='R03Contract')
    require(row['baseline']['physical'] != row['target']['physical'], 'Separate physical baseline and staged type')
    for k in ('fieldsChanged', 'baselineReady', 'targetReady', 'targetDefinitionReady', 'physicalProof'):
        require(row[k] is True, 'Missing physical readiness/proof: ' + k)
    for k in ('sourcePending', 'targetPending', 'baselineInitialized', 'baselineVtable', 'targetInitialized', 'targetVtable',
              'truncated', 'baselineInitializedAtRead', 'baselineVtableAtRead'):
        require(row[k] is False, 'No partial layout or business initialization: ' + k)
    require(all(integer(row[k]) for k in ('error', 'baselineCctor', 'targetCctor', 'baselineCctorAtRead')) and row['error'] == 0 and row['baselineCctor'] == 0 and row['targetCctor'] == 0 and row['baselineCctorAtRead'] == 0,
            'Successful metadata-only proof without business initializer')
    require(type(row['sourceFieldCount']) is int and type(row['targetFieldCount']) is int and row['sourceFieldCount'] == 1 and row['targetFieldCount'] == 2, 'Exact private primitive append shape')
    for name, count in (('sourceOffsets', 1), ('sourceAttrs', 1), ('targetOffsets', 2), ('targetAttrs', 2), ('targetStorage', 2)):
        require(type(row[name]) is list and len(row[name]) == count and all(integer(v) for v in row[name]), 'Exact field array: ' + name)
    require(integer(row['sourceSize'], 16) and integer(row['targetSize'], row['sourceSize']), 'Positive native allocation sizes')
    require(row['sourceOffsets'][0] == row['targetOffsets'][0] and row['sourceAttrs'][0] == row['targetAttrs'][0], 'Retained field layout')
    require(row['targetStorage'][-1] == 8 and row['targetAttrs'][-1] & 7 == 1 and
            row['targetOffsets'][-1] >= row['sourceSize'] and row['targetOffsets'][-1] + 8 <= row['targetSize'],
            'Private Int64 occupies newly proved tail storage')
    return row
