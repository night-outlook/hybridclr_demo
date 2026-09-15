#!/usr/bin/env python3
"""Replay PCH diagnostics from an explicitly selected failed attempt.

Reads the old graph/PCHs; writes only a new output directory. The extra binding
marks replay-only results, making them ineligible for the fresh build verifier.
It never manufactures, modifies, or completes an old Player build receipt.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import h1_native_capture as n
import h1_pch_provenance as p


def diagnose(request_path,graph_path,output):
    request_path=n.canonical_file(str(request_path));graph_path=n.canonical_file(str(graph_path))
    request_bytes=request_path.read_bytes();graph_bytes=graph_path.read_bytes()
    request=n.read_json(request_path);graph=n.read_json(graph_path)
    root=Path(request['projectRoot'])
    p.a.need(root.is_absolute() and root==root.resolve(strict=True),'Original project root is unavailable; do not rewrite the receipt')
    native=n.canonical_file(request['nativeLibraryPath']);config=n.canonical_file(request['il2cppConfigPath'])
    p.a.need(n.digest(native)==request['nativeLibrarySha256'],'Selected failed native output bytes differ')
    p.a.need(request['cppConfiguration'] in ('Debug','Release') and type(request['featureEnabled']) is bool,'Original build mode absent')
    p.a.need(output.is_absolute() and output==output.resolve() and not output.exists(),'Diagnostic output must be new and canonical')
    responses=n.collect_responses(graph,root)
    blueprint=p.plan(graph,root,native,config.read_text(),responses,request['featureEnabled'])
    binding={**{k:request[k] for k in p.BINDINGS},'graphSha256':p.sha(graph_bytes),
        'projectRoot':str(root),'featureEnabled':request['featureEnabled'],'cppConfiguration':request['cppConfiguration'],
        'diagnosticOnly':True,'replayedRequestSha256':p.sha(request_bytes)}
    output.mkdir(parents=True,exist_ok=False)
    p.write(output/'original-request.json',request_bytes);p.write(output/'original-graph.json',graph_bytes)
    summary={'kind':'H1PchDiagnosticReplay','status':'Blocked','diagnosticOnly':True,
             'requestSha256':p.sha(request_bytes),'graphSha256':p.sha(graph_bytes),
             'freshBuildClaim':False,'humanGatePassed':False,'mayEnterR02':False}
    try:
        proof=p.capture(blueprint,graph,root,str(config),binding,output/'pch',responses)
        p.verify(proof,graph,root,native,config.read_text(),responses,binding)
        p.a.need(request_path.read_bytes()==request_bytes and graph_path.read_bytes()==graph_bytes,'Original attempt changed during diagnosis')
        summary.update(status='DiagnosticReplayVerifiedNotBuildAccepted',proofPath=str(output/'pch/pch-proof.json'),
                       proofSha256=n.digest(output/'pch/pch-proof.json'))
    except (OSError,ValueError,KeyError) as error:
        summary['error']=str(error)
        p.write(output/'diagnostic-result.json',p.canonical(summary)+b'\n')
        raise
    p.write(output/'diagnostic-result.json',p.canonical(summary)+b'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True);parser.add_argument('--graph',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();print(json.dumps(diagnose(a.request,a.graph,a.output),indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError) as error:
        print('Blocked diagnostic replay: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
