#!/usr/bin/env python3
"""Non-authorizing consumer of the new initializer observation V1 (NOT V2).

This validates typed consistency only. Independently authenticate the actual
native snapshot bytes, source tuple, build, executable, and process before any
future runtime-level claim; this consumer never returns Player acceptance.
"""
import json
import re

KIND = 'R03IRInitializerCommitObservationV1'
TRANSPORT = 'NativePreopenedInitializerObservationV1'
KEYS = frozenset((
    'schemaVersion', 'kind', 'reportTransport', 'result', 'runId', 'caseId',
    'stimulus', 'fixtureSha256', 'processId', 'commitReturn', 'finalState',
    'nativeObserverBoundBeforeFailure', 'preparedField', 'finalField',
    'positiveMask', 'initializerCallbackCalls', 'postAotAttempted',
    'postAotSucceeded', 'firstRecoveryAuthenticated',
    'completeDiagnosticsAuthenticated', 'nativeV2TransportImplemented',
    'runtimeAcceptance', 'R03Accepted', 'H2Passed'
))
SHA = re.compile(r'[0-9a-f]{64}\Z')
NONCE = re.compile(r'[A-Za-z0-9_.-]{24,95}\Z')
CASE = re.compile(r'[A-Za-z0-9_.-]{1,95}\Z')


class Rejected(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Rejected(why)


def exact_int(value, expected):
    return type(value) is int and value == expected


def exact_bool(value, expected):
    return type(value) is bool and value is expected


def strict_load(raw_bytes):
    need(type(raw_bytes) is bytes and 0 < len(raw_bytes) <= 2048,
         'Bounded native raw bytes')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw_bytes.decode('utf-8', 'strict'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          Rejected('Non-finite JSON literal: ' + value)))


def verify(raw, request, launch, fixture_sha256):
    need(all(type(x) is dict for x in (raw, request, launch)), 'Typed input objects')
    need(set(raw) == KEYS, 'Exact distinct V1 raw schema; no K/V2 relabelling')
    need(exact_int(raw['schemaVersion'], 1) and raw['kind'] == KIND and
         raw['reportTransport'] == TRANSPORT and
         raw['result'] == 'ObservedNotAccepted', 'Exact non-authorizing envelope')
    mode = request.get('stimulus')
    need(mode in ('initializer-control', 'initializer-failure') and
         type(mode) is str and raw['stimulus'] == mode,
         'Only real initializer cases admitted')
    need(type(request.get('runId')) is str and NONCE.fullmatch(request['runId']) and
         type(request.get('caseId')) is str and CASE.fullmatch(request['caseId']) and
         raw['runId'] == request['runId'] and raw['caseId'] == request['caseId'],
         'Fresh request/run/case identity')
    need(type(fixture_sha256) is str and SHA.fullmatch(fixture_sha256) and
         raw['fixtureSha256'] == fixture_sha256 and
         request.get('dllSha256') == fixture_sha256,
         'Exact externally bound target fixture digest')
    need(type(launch.get('pid')) is int and launch['pid'] > 0 and
         exact_int(raw['processId'], launch['pid']), 'Exact launch PID')
    for key in ('firstRecoveryAuthenticated','completeDiagnosticsAuthenticated',
                'nativeV2TransportImplemented', 'runtimeAcceptance', 'R03Accepted',
                'H2Passed', 'postAotSucceeded'):
        need(exact_bool(raw[key], False), 'No fabricated approval or terminal proof: ' + key)
    need(exact_bool(raw['nativeObserverBoundBeforeFailure'], True) and
         exact_int(raw['preparedField'], 3) and exact_int(raw['finalField'], 3) and
         exact_int(raw['positiveMask'], 15) and
         exact_int(raw['initializerCallbackCalls'], 1),
         'Actual native prepared field / callback cardinality contract')
    control = mode == 'initializer-control'
    need(exact_int(raw['commitReturn'], 0 if control else 19) and
         exact_int(raw['finalState'], 6 if control else 9) and
         exact_bool(raw['postAotAttempted'], not control),
         'Distinct unpromoted initializer control/failure outcomes')
    return {'schemaVersion': 1, 'kind': 'R03IRInitializerObservationHostConsumer',
            'result': 'SchemaConsistentNotRuntimeAuthenticated',
            'stimulus': mode, 'runtimeAcceptance': False,
            'R03Accepted': False, 'H2Passed': False,
            'firstRecoveryAuthenticated': False, 'nativeV2TransportImplemented': False}
