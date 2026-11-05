#!/usr/bin/env python3
"""IR-R03-02 proposed remaining-Player witness consumer (source-only).

Rejects stale/relabelled K evidence. A successful semantic check is NEVER a
runtime-acceptance verdict or proof that native/Unity ran; independent build,
source, process and native snapshot authentication is mandatory upstream.
"""
import json
import re

SCHEMA = 1
KIND = 'R03IRRemainingTerminalWitnessV1'
STIMULI = frozenset(('captured-generic', 'initializer-failure', 'initializer-control'))
HEX = re.compile(r'^[0-9a-f]{64}$')
COMMIT = re.compile(r'^[0-9a-f]{40}$')
REPOS = ('hybridclr_demo', 'hybridclr', 'hybridclr_unity', 'il2cpp_plus')
MVID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
SENTINEL = 'R03IR.InitializerFailure.AfterPublication.V1'


class WitnessRejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise WitnessRejected(reason)


def integer(v, value):
    return type(v) is int and v == value


def boolean(v, value):
    return type(v) is bool and v is value


def positive(v):
    return type(v) is int and v > 0


def image_index(v):
    return type(v) is int and v >= 0


def digest(v):
    return type(v) is str and HEX.fullmatch(v) is not None


def parse_recovery(encoded):
    need(type(encoded) is str and encoded, 'Full first recovery is required')
    try:
        recovery = json.loads(encoded)
    except (TypeError, ValueError) as error:
        raise WitnessRejected('Invalid first recovery JSON') from error
    need(type(recovery) is dict and boolean(recovery.get('published'), True) and
         recovery.get('disposition') == 'RestartRequired' and
         integer(recovery.get('stateCode'), 9), 'Authentic terminal recovery contract')
    return recovery


def verify_remaining(raw, request, launch, expected):
    """Validate one new, non-authorizing raw record against external expected pins.

    `expected` is supplied ONLY from independently authenticated coordinator
    receipts, not from raw Player bytes. This routine cannot authenticate the
    witness producer, side effects, or source on its own.
    """
    need(type(raw) is dict and type(request) is dict and type(launch) is dict and
         type(expected) is dict, 'Distinct typed producer/request/launch/authority records')
    stimulus = request.get('stimulus')
    need(type(stimulus) is str and stimulus in STIMULI, 'Unsupported remaining witness stimulus')
    need(integer(raw.get('schemaVersion'), SCHEMA) and raw.get('kind') == KIND and
         raw.get('reportTransport') == 'NativePreopenedSnapshotV2' and
         raw.get('result') == 'ObservedNotAccepted' and
         boolean(raw.get('runtimeAcceptance'), False) and
         boolean(raw.get('R03Accepted'), False) and
         boolean(raw.get('H2Passed'), False) and not raw.get('error'),
         'Versioned non-authorizing native snapshot contract')
    need(raw.get('stimulus') == stimulus and
         type(request.get('runId')) is str and len(request['runId']) >= 24 and
         raw.get('runId') == request['runId'] and
         type(request.get('caseId')) is str and request['caseId'] and
         raw.get('caseId') == request['caseId'] and
         positive(launch.get('pid')) and integer(raw.get('processId'), launch['pid']) and
         raw.get('unityVersion') == '2022.3.62f2' and raw.get('platform') == 'OSXPlayer',
         'Fresh exact Unity Player process and case identity')
    for field in ('requestSha256','fixtureSha256','buildReceiptSha256',
                  'sourceManifestSha256','nativeOverlaySha256'):
        authority = expected.get(field)
        need(digest(authority) and raw.get(field) == authority,
             'Independently pinned digest mismatch: ' + field)
    required_repos = expected.get('repositories')
    need(type(required_repos) is dict and set(required_repos) == set(REPOS) and
         all(type(required_repos[name]) is str and COMMIT.fullmatch(required_repos[name])
             for name in REPOS) and raw.get('repositories') == required_repos,
         'Full independently pinned four-repository source identity')
    need(type(expected.get('fixtureMvid')) is str and
         MVID.fullmatch(expected['fixtureMvid']) is not None and
         raw.get('fixtureMvid') == expected['fixtureMvid'],
         'Exact target fixture MVID')
    need(boolean(raw.get('nativeObserverBoundBeforeFailure'), True) and
         boolean(raw.get('nativeObserverReadAfterFailure'), stimulus != 'initializer-control') and
         integer(raw.get('preparedField'), 3),
         'Actual pre-bound native instance field observation')
    need(integer(raw.get('preDirectReturn'), 42) and
         integer(raw.get('preDelegateReturn'), 42) and
         integer(raw.get('preGenericReturn'), 42), 'Three actual positive bodies before terminal boundary')
    if stimulus == 'initializer-control':
        need(integer(raw.get('commitReturn'), 0) and integer(raw.get('finalState'), 6) and
             boolean(raw.get('initializerAttempted'), True) and
             boolean(raw.get('initializerCompleted'), True) and
             integer(raw.get('initializerAttemptCount'), 1) and
             boolean(raw.get('initializerSentinelObserved'), False) and
             raw.get('firstRecovery') is None and raw.get('finalRecovery') is None and
             boolean(raw.get('postTerminalEntryAttempted'), False) and
             integer(raw.get('finalField'), 3),
             'Successful real initializer control without invented terminal state')
        return {'kind':'R03IRRemainingWitnessHostSemanticCheck', 'result':'SchemaSemanticsOnly',
                'stimulus':stimulus, 'runtimeAcceptance':False, 'R03Accepted':False, 'H2Passed':False}
    need(integer(raw.get('finalState'), 9) and integer(raw.get('finalField'), 3) and
         boolean(raw.get('postTerminalEntryAttempted'), True) and
         boolean(raw.get('postTerminalEntrySucceeded'), False) and
         type(raw.get('postTerminalException')) is str and raw['postTerminalException'] and
         integer(raw.get('preAotCanaryCount'), 1) and
         integer(raw.get('finalAotCanaryCount'), 1) and
         boolean(raw.get('firstFailureStable'), True) and
         type(raw.get('firstRecovery')) is str and
         raw.get('firstRecovery') == raw.get('finalRecovery'),
         'Terminal attempts must be denied without managed body side effects')
    recovery = parse_recovery(raw['firstRecovery'])
    if stimulus == 'captured-generic':
        need(integer(raw.get('commitReturn'), 0) and integer(raw.get('initialState'), 6) and
             integer(recovery.get('terminalFailureCode'), 15) and
             raw.get('guardReason') == 'CapturedBaselineType' and
             raw.get('capturedArgumentAssembly') == 'Methods' and
             type(raw.get('physicalGenericOwnerAssembly')) is str and
             raw['physicalGenericOwnerAssembly'] not in ('', 'Methods') and
             image_index(raw.get('physicalGenericOwnerImageIndex')) and
             image_index(raw.get('physicalCapturedArgumentImageIndex')) and
             raw['physicalGenericOwnerImageIndex'] != raw['physicalCapturedArgumentImageIndex'] and
             boolean(raw.get('physicalBaselineArgumentVerified'), True) and
             boolean(raw.get('closedGenericMethodInflated'), True) and
             boolean(raw.get('nativeMethodGuardEntered'), True) and
             boolean(raw.get('initializerAttempted'), False),
             'Real physical captured-baseline generic guard, error 15 not 13/21')
    else:
        need(integer(raw.get('commitReturn'), 19) and
             integer(recovery.get('terminalFailureCode'), 19) and
             boolean(raw.get('initializerAttempted'), True) and
             boolean(raw.get('initializerCompleted'), False) and
             integer(raw.get('initializerAttemptCount'), 1) and
             boolean(raw.get('initializerSentinelObserved'), True) and
             raw.get('initializerSentinel') == SENTINEL and
             type(raw.get('firstFailureDetail')) is str and
             SENTINEL in raw['firstFailureDetail'] and
             boolean(raw.get('afterPublication'), True) and
             integer(raw.get('initialState'), 5),
             'Post-publication real failed module initializer, error 19')
    return {'kind':'R03IRRemainingWitnessHostSemanticCheck', 'result':'SchemaSemanticsOnly',
            'stimulus':stimulus, 'runtimeAcceptance':False, 'R03Accepted':False, 'H2Passed':False}
