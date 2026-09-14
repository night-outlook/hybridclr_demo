#!/usr/bin/env python3
"""Adapter for immutable build receipts plus separate managed-source proof."""
from __future__ import annotations
import hashlib
import re
import h1_successor_evidence as core
import h1_witness_contract as witness


def witness_probe(value, config_sha):
    core.exact(value.get('schemaVersion'),1,'witness schema')
    core.exact(value.get('kind'),'H1WitnessGuardRuntimeProbe','witness kind')
    core.exact(value.get('result'),'Passed','witness result')
    core.exact(value.get('il2cpp'),True,'witness IL2CPP')
    core.exact(value.get('configurationSha256'),config_sha,'witness config')
    core.exact(value.get('imageSha256'),witness.IMAGE_SHA256,'witness image')
    for key in ('tamperRejected','nullRejected','callerBytesUnchanged'):
        core.exact(value.get(key),True,'witness '+key)
    core.exact(value.get('assemblyResolveEvents'),0,'witness resolver events')
    core.exact(value.get('humanGatePassed'),False,'witness human gate')
    core.exact(value.get('mayEnterR02'),False,'witness R02 gate')
    config=value.get('configurationHash')
    core.need(type(config) is str and re.fullmatch('[0-9a-f]{64}',config),'witness configuration hash')
    expected='__AssemblyShadowReflectionBinding_'+config+'_'+hashlib.sha256(witness.SITE_ID.encode()).hexdigest()
    core.exact(value.get('guardName'),expected,'witness guard')


def selected_builds(store, role, pin_role, modes):
    expected=core.pins(store.read(pin_role)); proofs_role='candidate-managed-verifications' if role.startswith('candidate-') else 'reproduction-managed-verifications'
    proofs={}
    for ident in store.roles[proofs_role]:
        proof=store.json_row(store.by_id[ident]); proofs[proof.get('buildGuid')]=proof
    result={}
    for ident in store.roles[role]:
        row=store.by_id[ident]; value=store.json_row(row)
        core.exact(value.get('kind'),'H1CountDiagnosticPlayerBuild','build kind')
        core.exact(value.get('schemaVersion'),1,'build schema')
        core.exact(value.get('diagnosticOnly'),True,'diagnostic build')
        core.need(type(value.get('featureEnabled')) is bool,'feature flag')
        mode=('On' if value['featureEnabled'] else 'Off')+'/'+str(value.get('cppConfiguration'))
        core.need(mode in modes and mode not in result,'build mode membership')
        core.exact(value.get('baselineBuildId'),'H1Count-'+mode.replace('/','-'),'build identity')
        core.need(core.build_pins(value)==expected,'build source pins')
        store.ref(value['compilerProvenancePath'],value['compilerProvenanceSha256'])
        core.exact(value['sourcePinSha256'],store.row(pin_role)['sha256'],'source pin bytes')
        proof=proofs.get(value.get('buildGuid')); core.need(proof is not None,'missing managed proof for selected build')
        value['managedSourceProvenancePath']=proof['capturePath']
        value['managedSourceProvenanceSha256']=proof['captureSha256']
        result[mode]=(row,value)
    core.need(set(result)==set(modes),'build mode coverage')
    return result


def install():
    core.verify_runtime_probe=witness_probe
    core.validate_builds=selected_builds


def main():
    install(); return core.main()

if __name__=='__main__': raise SystemExit(main())
