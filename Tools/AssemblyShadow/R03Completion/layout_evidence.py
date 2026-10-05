"""Additional integrity checks for fresh production layout-identity sidecars.

The production factory rederives Unity framework and linked proofs. This verifier
checks source/membership/path agreement; it does not substitute a Python alias map
for the actual metadata resolver or certify physical allocation safety.
"""
from pathlib import Path
import re
import layout_identity as identity
from batch_contract import loads, require, sha
from batch_evidence import write
from compiler_policy_inputs import regular


def declaration_name(text):
    require(isinstance(text, str) and len(text) <= 65536, 'Bounded complete declaration')
    data = text.encode('utf-16-le'); at = 0; values = []
    while at < len(data):
        colon = data.find(b':\0', at)
        require(colon >= at and (colon-at) % 2 == 0, 'Canonical declaration length')
        size = data[at:colon].decode('utf-16-le')
        require(re.fullmatch('0|[1-9][0-9]*', size) and len(size) <= 6, 'Canonical declaration length')
        end = colon + 2 + 2 * int(size)
        require(end + 2 <= len(data) and data[end:end+2] == b';\0', 'Complete declaration token')
        values.append(data[colon+2:end].decode('utf-16-le')); at = end+2
    require(len(values) >= 3 and re.fullmatch('[1-9][0-9]*', values[1]) and
            int(values[1]) == len(values)-2 and len(values)-2 < 129 and all(values[2:]), 'Exact nested declaration shape')
    return (values[0]+'.' if values[0] else '') + '/'.join(values[2:])


def verify_value(value, baseline, target, linked, compiler, proof, proof_hash, facade_hash, order):
    require(value['schemaVersion'] == 2 and value['profile'] == 'NativeLayoutAdmissionV1' and value['inputBasis'] == 'LinkedPlayer', 'New captured-identity sidecar schema')
    require(value['nativeProofExecuted'] is False and value['runtimeMustRevalidate'] is True and
            value['pureInterpreterExpansionEnabled'] is False, 'Nominal comparison is not native proof')
    for key, expected in [('baselineSnapshotHash', baseline['snapshotHash']), ('linkedPlayerReceiptHash', baseline['linkedPlayerReceiptHash']),
                          ('baselineNativeLibrarySha256', baseline['nativeLibrarySha256']), ('targetSnapshotHash', target['snapshotHash'])]:
        require(value[key] == expected, 'Sidecar source binding: ' + key)
    require(value['targetLoadOrder'] == order and len(order) == len(set(order)), 'Exact target-only load order')
    evidence = value['identityEvidence']
    require(evidence['profile'] == identity.PROFILE and evidence['linkedRetargetingEvidenceHash'] == proof_hash ==
            baseline['linkedPlayerReceipt']['reflectionBindingEvidenceHash'], 'Captured retargeting proof binding')
    require(evidence['runtimeFacadeSha256'] == facade_hash == proof['facadeSha256'] and proof['facadePath'] == identity.FACADE and
            proof['buildGuid'] == baseline['buildGuid'] and proof['mappingPolicyVersion'] == 1, 'Exact baseline forwarding facade')
    for key in ('unityVersion', 'target', 'architecture'):
        require(baseline[key] == target[key] == proof[key], 'Two domains must share Unity target: ' + key)
    # This hash is minted by the actual Unity catalog verifier in production, not
    # a substitute here for invoking that verifier. Its concrete netstandard
    # input is independently bound to exactly the target reference inventory.
    require(re.fullmatch('[0-9a-f]{64}', evidence['targetFrameworkProvenanceHash']) is not None, 'Production framework provenance required')
    refs = [r for r in target['references'] if r['name'].lower() == 'netstandard']
    require(len(refs) == 1 and refs[0]['sha256'] == evidence['compilerFacadeSha256'], 'Compiler facade is one actual reference')
    li = identity.validate_inventory(evidence['linkedInventory'], linked)
    ci = identity.validate_inventory(evidence['compilerInventory'], compiler)
    require(ci.get(identity.NETSTANDARD) == evidence['compilerFacadeSha256'], 'Exact compiler facade full identity')
    identity.validate_resolutions(evidence['linkedResolutions'], li, {}, '')
    mapped = identity.validate_resolutions(evidence['compilerResolutions'], ci, li, facade_hash)
    forwarders = {r['typeFullName']: r['destinationAssemblyIdentity'] for r in proof['forwarders']}
    require(len(forwarders) == len(proof['forwarders']) and forwarders, 'Unambiguous captured export domain')
    for r in evidence['compilerResolutions']:
        name = declaration_name(r['declaration'])
        if r['runtimeFacadeUsed']:
            pivot = r['forwardingPath'].index(identity.NETSTANDARD + ' | runtime-facade=' + facade_hash)
            require(pivot+1 < len(r['forwardingPath']) and name in forwarders and
                    r['forwardingPath'][pivot+1].rsplit(' | sha256=', 1)[0] == forwarders[name], 'Resolution must follow this declaration\'s actual captured export')
    assemblies = value['assemblies']; require(len(assemblies) == len(order), 'One assembly result per closure input')
    b_files = {Path(r['path']).name.lower(): r['sha256'] for r in linked}
    t_files = {r['name'].lower(): r['sha256'] for r in target['assemblies']}
    for name, report in zip(order, assemblies):
        require(report['schemaVersion'] == 2 and report['profile'] == 'NativeLayoutAdmissionV1' and report['assembly'].lower() == name,
                'Source-bound assembly report')
        require(report['baselineDllSha256'] == b_files[name+'.dll'] and report['targetDllSha256'] == t_files[name], 'Exact compared DLLs')
        require(report['editorAccepted'] is True and report['nativeProofExecuted'] is False and report['allocationProofStillRequired'] is True and
                report['pureInterpreterExpansionEnabled'] is False, 'Conservative assembly admission')
        rows = report['types']; require(rows and len({r['typeKey'] for r in rows}) == len(rows), 'Unique full type rows')
        for row in rows:
            require(row['decision'] in ('NeedsNativeProof', 'NoBaselineCounterpart', 'NoActiveCounterpart') and row['reasons'], 'No hidden rejected type')
    return {'assemblies': len(assemblies), 'linkedImages': len(linked), 'compilerImages': len(compiler), 'mappedDeclarations': mapped,
            'nativeProofExecuted': False, 'runtimeMustRevalidate': True, 'expansionAuthorized': False}


def verify_graph(batch):
    project = Path(batch.resource_config['projectPath']); path = regular(batch.resource_manifest)
    require(path.is_relative_to(project), 'Fixture graph belongs to current batch')
    manifest = loads(path.read_text()); baseline_root = Path(manifest['baselineInputSnapshot'])
    require(baseline_root.is_relative_to(project), 'Baseline snapshot belongs to current project')
    baseline, linked = identity.snapshot(baseline_root, True)
    proof_path = identity.child(baseline_root, identity.PROOF); proof = loads(proof_path.read_text())
    facade_hash = sha(identity.child(baseline_root, identity.FACADE))
    require([r['patchId'] for r in manifest['fixtures']] == ['P01','P02','P03','P04','P05'], 'All five atomic fixtures')
    result = {'kind': 'R03FreshLayoutIdentityVerification', 'result': 'Failed', 'schemaVersion': 1, 'fixtures': [],
              'runtimeAcceptance': False, 'nativeProofExecuted': False, 'expansionAuthorized': False}
    try:
        for row in manifest['fixtures']:
            root = Path(row['compileSnapshot']); patch = Path(row['patchDirectory'])
            require(root.is_relative_to(project) and patch.is_relative_to(project), 'No historical/foreign fixture inputs')
            target, compiler = identity.snapshot(root, False)
            require(target['snapshotHash'] == row['compileSnapshotHash'] and baseline['snapshotHash'] == manifest['baselineInputSnapshotHash'], 'Manifest snapshot binding')
            sidecar = identity.child(patch, identity.REPORT); value = loads(sidecar.read_text())
            checks = verify_value(value, baseline, target, linked, compiler, proof, sha(proof_path), facade_hash, row['closureLoadOrder'])
            result['fixtures'].append({'patchId': row['patchId'], 'path': str(sidecar), 'sha256': sha(sidecar), 'checks': checks})
        require(result['fixtures'][-1]['checks']['mappedDeclarations'] > 0, 'P05 actual forwarding coverage')
        result['result'] = 'Passed'
        return result
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error); raise
    finally:
        write(batch.root / 'layout-identity-verification.json', result)
