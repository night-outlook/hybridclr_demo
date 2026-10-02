"""Strict focused R03 observation contracts; never fabricate Player evidence."""
import hashlib
import json
from pathlib import Path


class ContractError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def _pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, 'Duplicate JSON member: ' + key)
        result[key] = value
    return result


def loads(text):
    def invalid(value):
        raise ContractError('Non-finite JSON number: ' + value)
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def fields(value, expected, label):
    require(type(value) is dict and set(value) == set(expected.split()), label + ': exact field set required')


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


RAW_FIELDS = '''schemaVersion kind runId caseId requestSha256 pid startedUtc endedUtc unityVersion platform il2cpp
published phase steps exception exceptionType exceptionStack invocationResult delegateResult warmAllocationCount
beforeWarm afterWarm nativeMethod runtimeProbe rejectionProbe diagnostics diagnosticsCode finalState recovery recoveryCode managedBytesBefore managedBytesAfter acceptance'''
METHOD_FIELDS = '''schemaVersion available mappingCode mappingDetail baselineToken baselineSlot activeToken activeSlot
differentPhysicalMethods activeOwner cacheIdentityStable baselineCctorBefore baselineCctorAfter activeGuard baselineGuard stateCode activeGeneration'''
RECOVERY_FIELDS = '''schemaVersion enabled capabilityVersion stateCode state published abortAllowed dispositionCode disposition
terminalFailureCode reason retainedBytes baselineEligibilityRequiresStartupValidation'''
TYPE_FIELDS = '''schemaVersion logicalAssembly executionModeCode executionMode isActive physicalImageKind typeKey inputTypePointer
activeTypePointer baselineTypePointer pointerDetailsAvailable baselinePointerAvailable containsShadowTypes definitionCacheHits
definitionCacheMisses compositeRebuilds allocationRemaps guardFailures r02'''
R02_FIELDS = '''schemaVersion diagnosticsLevel definitionSearches definitionRowsScanned admissionCacheHits admissionCacheMisses
admissionProofAttempts admissionProofRejections admissionEntries admissionRetainedBytes admissionUnready baselineStateChecks
fieldWorkspaceBuilds interfaceWorkspaceBuilds layoutCheckCalls counterpartCacheHits counterpartCacheMisses counterpartEntries
absentCounterpartEntries cacheFixedBytes counterpartRetainedBytes genericContextChecks observationLockContentions observationMemoHits
observationMemoTlsBytesPerThread counterStorageBytes counterThreadCapacity droppedCounterThreads counterSaturated counterCoverage
classesCoverage memoryAccountingAvailable memoryAccountingScope'''


def verify_raw(request, raw, expected, request_sha, launch_pid):
    fields(raw, RAW_FIELDS, 'Player observation')
    require(type(raw['schemaVersion']) is int and raw['schemaVersion'] == 3 and raw['kind'] == 'R03PlayerObservation', 'Observation schema')
    require(raw['acceptance'] is False and raw['il2cpp'] is True, 'Actual IL2CPP observation, not acceptance')
    require(raw['runId'] == request['runId'] and raw['caseId'] == request['caseId'], 'Request/run identity')
    require(raw['requestSha256'] == request_sha and raw['pid'] == launch_pid, 'Launch and exact request binding')
    require(raw['unityVersion'] == '2022.3.62f2' and raw['platform'] == 'OSXPlayer', 'Exact Player platform')
    require(type(raw['published']) is bool and integer(raw['finalState']), 'State field types')
    require(type(raw['steps']) is list, 'Actual native API step list')
    for step in raw['steps']:
        fields(step, 'phase code state', 'Native step')
        require(integer(step['code']) and integer(step['state']), 'Native step integer codes')
    phases = ['Configure', 'Begin', 'Reserve'] + ['Stage:' + d['name'] for d in request['dlls']] + ['Validate', 'Commit']
    outcome = expected['outcome']
    if outcome == 'baseline':
        require(not raw['steps'] and raw['published'] is False and raw['phase'] == 'Completed', 'Baseline-only execution')
        require(not raw['exception'], 'Unexpected baseline exception')
        require(raw['invocationResult'] == 41 and raw['delegateResult'] == 41 and raw['warmAllocationCount'] == 10000, 'Actual baseline calls')
        return {'outcome': outcome, 'nativeCalls': 0}

    require(raw['diagnosticsCode'] == 0 and raw['recoveryCode'] == 0, 'Native diagnostics and recovery must be available')
    diagnostics = loads(raw['diagnostics'])
    require(diagnostics.get('schemaVersion') == 1 and diagnostics.get('stateCode') == raw['finalState'], 'Diagnostic native state')
    require(diagnostics.get('baselineBuildId') == request['baselineId'] and diagnostics.get('patchId') == 'R03-' + request['runId'], 'Native transaction identity')
    recovery = loads(raw['recovery'])
    fields(recovery, RECOVERY_FIELDS, 'Recovery')
    require(recovery['schemaVersion'] == 1 and recovery['stateCode'] == raw['finalState'] and recovery['published'] is raw['published'], 'Recovery publication/state agreement')
    observed = [s['phase'] for s in raw['steps']]
    if outcome in ('admission-reject', 'target-cycle'):
        require(observed == phases[:-1] and all(s['code'] == 0 for s in raw['steps'][:-1]), 'Failure must occur at Validate, not PE parse or an earlier setup error')
        code = 16 if outcome == 'admission-reject' else 13
        require(raw['steps'][-1]['code'] == code and diagnostics['lastError'] == code, 'Exact production rejection code')
        require(raw['published'] is False and raw['phase'] == 'Validate' and not raw['exception'], 'No commit, business invocation or exception substitution')
        require(raw['invocationResult'] == 0 and raw['warmAllocationCount'] == 0 and not raw['nativeMethod'], 'No post-failure business work')
        if outcome == 'admission-reject':
            require(raw['finalState'] == 8 and recovery['disposition'] == 'RestartRequired' and recovery['abortAllowed'] is False, 'Metadata failure remains terminal before publication')
            require('NativeLayoutAdmissionV1' in diagnostics['detail'], 'V1 rejection diagnostic, not unrelated code 16')
            from rejection_contract import verify_rejection_observation
            observation = verify_rejection_observation(raw, request)
            return {'outcome': outcome, 'code': code, 'state': raw['finalState'], 'rejectionObservation': observation}
        else:
            require(raw['finalState'] == 3, 'Actual AssemblyRef order rejected before metadata initialization')
        return {'outcome': outcome, 'code': code, 'state': raw['finalState']}

    require(observed == phases and all(s['code'] == 0 for s in raw['steps']), 'Complete successful publication API chain')
    require(raw['steps'][-1]['state'] == 6 and raw['published'] is True, 'Actual successful publication')
    if outcome == 'legacy-late-layout':
        require(raw['phase'] == 'ActiveInvoke' and bool(raw['exception']), 'Original allocation failure must be observed after commit')
        require(raw['finalState'] == 9 and recovery['terminalFailureCode'] == 16 and recovery['disposition'] == 'RestartRequired', 'Original physical-layout guard, not arbitrary managed exception')
        require(raw['invocationResult'] == 0 and raw['warmAllocationCount'] == 0, 'Incompatible object was not successfully invoked')
        return {'outcome': outcome, 'state': 9, 'code': 16}

    require(raw['phase'] == 'Completed' and not raw['exception'], 'Successful execution without hidden exception')
    require(raw['invocationResult'] == expected['value'] and raw['delegateResult'] == expected['value'], 'Actual reflection and delegate results')
    require(raw['warmAllocationCount'] == 10000, 'Complete warm allocation loop')
    runtime_evidence = {}
    if expected.get('warmCertificate'):
        before, after = loads(raw['beforeWarm']), loads(raw['afterWarm'])
        for value in (before, after):
            fields(value, TYPE_FIELDS, 'Type-resolution observation')
            require(value['schemaVersion'] == 1 and value['logicalAssembly'] == request['invokeAssembly'] and value['executionModeCode'] == 1,
                    'Active logical type observation')
            fields(value['r02'], R02_FIELDS, 'R02 counters')
            require(value['r02']['schemaVersion'] == 1 and value['r02']['diagnosticsLevel'] == 2 and
                    value['r02']['counterSaturated'] is False and value['r02']['droppedCounterThreads'] == 0, 'Counter coverage')
        a, b = before['r02'], after['r02']
        for key in ('admissionCacheHits', 'baselineStateChecks', 'admissionCacheMisses', 'admissionProofAttempts', 'admissionUnready',
                    'fieldWorkspaceBuilds', 'interfaceWorkspaceBuilds', 'layoutCheckCalls'):
            require(integer(a[key]) and integer(b[key]) and b[key] >= a[key], 'Monotonic integer counter: ' + key)
        require(b['admissionCacheHits'] - a['admissionCacheHits'] >= 10000 and b['baselineStateChecks'] - a['baselineStateChecks'] >= 10000,
                'Warm certificate reuse retains baseline checks')
        from runtime_contract import verify_warm, verify_primitive_layout, verify_producer_control
        control = expected.get('producerControl', False)
        require(type(request.get('producerControl')) is bool and request['producerControl'] is control,
                'Source-bound producer-control request')
        if control:
            require(expected['role'] == 'candidate-release' and expected['id'].startswith('PC-'), 'Dedicated natural-control identity')
            runtime_evidence['warmWindow'] = verify_producer_control(raw['runtimeProbe'], a, b, request['invokeAssembly'])
        else:
            runtime_evidence['warmWindow'] = verify_warm(raw['runtimeProbe'], a, b, request['invokeAssembly'])
        if expected.get('primitiveLayoutProof'):
            runtime_evidence['prepublicationLayout'] = verify_primitive_layout(raw['runtimeProbe'])
    if request['observeMethod']:
        method = loads(raw['nativeMethod'])
        fields(method, METHOD_FIELDS, 'Real MethodInfo probe')
        require(method['schemaVersion'] == 1 and method['available'] is True and integer(method['baselineToken'], 1), 'Physical baseline MethodInfo')
        require(method['baselineCctorBefore'] == 0 and method['baselineCctorAfter'] == 0, 'No baseline business initializer')
        require(integer(method['activeGeneration'], 1), 'Active generation exists')
        if outcome == 'legacy-slot':
            require(method['mappingCode'] == 13 and 'ShadowMethodNotFound' in method['mappingDetail'] and method['activeOwner'] is False,
                    'Original slot-based lookup failure')
        else:
            require(method['mappingCode'] == 0 and method['differentPhysicalMethods'] is True and method['activeOwner'] is True and
                    method['cacheIdentityStable'] is True, 'Actual active MethodInfo mapping and stable cached identity')
            require(method['baselineSlot'] != method['activeSlot'], 'The actual native virtual slot must have moved')
        if request['oldExecutionGuard']:
            require(method['activeGuard'] == 1 and method['baselineGuard'] == 0 and method['stateCode'] == 9 and raw['finalState'] == 9,
                    'Actual old-AOT execution guard was not authorized by remapping')
            require(recovery['disposition'] == 'RestartRequired' and recovery['terminalFailureCode'] == 21, 'Old method guard preserves poison/restart')
        else:
            require(method['activeGuard'] == -1 and method['baselineGuard'] == -1 and raw['finalState'] == 6, 'No unintended guard test')
    else:
        require(not raw['nativeMethod'] and raw['finalState'] == 6, 'No unexpected native probe or failure')
    return {'outcome': outcome, 'state': raw['finalState'], 'value': raw['invocationResult'], **runtime_evidence}
