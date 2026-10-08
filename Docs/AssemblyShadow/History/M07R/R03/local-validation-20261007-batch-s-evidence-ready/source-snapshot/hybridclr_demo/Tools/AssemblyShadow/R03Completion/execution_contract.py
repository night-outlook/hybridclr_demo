"""Supplementary M06 assertions use the actual selected DLL and original rules."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'R03'))
import m06_results as m06
import m06_execution_metadata as metadata
from batch_contract import loads, require, sha


def selected_image(context, mode):
    """Materialize the M06 image-record contract from the selected physical bytes.

    Receipt names are canonical lookup keys only. The parsed assembly identity,
    MVID, IL and portable symbols remain bound to the authenticated file hashes.
    Linked AOT symbols are intentionally not claimed as portable patch evidence.
    """
    require(mode in ('R00-ON-NoPatch', 'R00-OFF-NoPatch', 'R00-ON-P01', 'R00-ON-P03'),
            'Unknown execution supplement mode')
    if mode in ('R00-ON-P01', 'R00-ON-P03'):
        patch = context['fixtures']['P01' if mode.endswith('P01') else 'P03']
        row = m06.named(patch['patch']['closure'], m06.INTERNAL, 'Selected physical patch DLL')
        dll = m06.prior._rel(patch['root'], row['dll'], 'Selected physical patch DLL', 'dll')
        pdb = m06.prior._rel(patch['root'], row['pdb'], 'Selected physical patch PDB', 'pdb')
        require(sha(dll) == row['sha256'] and sha(pdb) == row['pdbSha256'], 'Selected patch bytes/symbols changed')
    else:
        build = context['off' if mode == 'R00-OFF-NoPatch' else 'on']
        row = m06.named(build['snapshot']['linkedPlayerReceipt']['assemblies'], m06.INTERNAL, 'Actual linked baseline DLL')
        dll = m06.prior._rel(build['root'] / 'LinkedPlayer', row['path'], 'Actual linked baseline DLL', 'path')
        pdb = None
        require(sha(dll) == row['sha256'], 'Linked DLL bytes changed')
    identity = m06.prior.read_identity(dll)
    require(identity['name'] == m06.INTERNAL and identity['mvid'] == row['mvid'] and
            identity['sha256'] == row['sha256'], 'Selected physical assembly identity/MVID/hash differs')
    image = {'identity': identity, 'methods': metadata.read_methods(dll, pdb), 'pdbAvailable': pdb is not None}
    # Parsing and all returned observations must describe the same immutable bytes.
    require(sha(dll) == row['sha256'] and (pdb is None or sha(pdb) == row['pdbSha256']),
            'Selected image changed while reading metadata')
    return image


def verify(request, extra, original, request_hash, original_hash, pid, context):
    require(extra['schemaVersion'] == 1 and extra['kind'] == request['kind'] == 'R03ExecutionSupplement' and
            extra['runId'] == request['runId'] and extra['mode'] == request['mode'] == original['mode'], 'Supplement identity')
    require(extra['requestSha256'] == request_hash and extra['r00Sha256'] == original_hash and
            extra['processId'] == pid == original['processId'] and extra['buildGuid'] == original['buildGuid'], 'Supplement actual process/input binding')
    require(extra['il2cpp'] is True and extra['R03Accepted'] is False and extra['H2Passed'] is False and
            extra['result'] == 'Observed' and not extra['error'], 'Supplement observation without acceptance promotion')
    require(extra['featureEnabled'] is original['featureEnabled'] and extra['transactionCommitted'] is original['transactionCommitted'], 'Same executed world')
    require(extra['typeName'] == m06.witness(m06.INTERNAL), 'Actual M06 witness')
    require(extra['diagnosticsCode'] == ('Success' if original['featureEnabled'] else 'FeatureDisabled'), 'Type diagnostics availability')
    if original['featureEnabled']:
        info = loads(extra['diagnostics'])
        require(info['isActive'] is True and info['logicalAssembly'] == m06.INTERNAL and
                info['executionMode'] == ('InterpreterShadow' if original['transactionCommitted'] else 'AotBaseline'), 'Actual selected runtime method/type')
    rows = extra['observations']
    require([(r['phase'], r['repetition']) for r in rows] == [(p, n) for p in ('statics', 'delegates', 'exceptions') for n in range(2)], 'Complete supplemental phase order')
    image = selected_image(context, original['mode']); first = {}
    for row in rows:
        phase, values, rep = row['phase'], row['values'], row['repetition']
        if phase == 'exceptions':
            m06.verify_exception(values, image, 'R03 supplement', original['transactionCommitted'], True)
        else:
            m06.verify_business(values, m06.INTERNAL, phase, image, 'R03 supplement', rep, first.get(phase))
        if rep == 0: first[phase] = values
    return {'result': 'Passed', 'phases': 6, 'physicalDll': image['identity'], 'pdbAvailable': image['pdbAvailable'],
            'originalM06BusinessAndExceptionRules': True, 'measuredIntervalIncludesSupplement': False,
            'fullM06MatrixClaimed': False, 'R03Accepted': False}
