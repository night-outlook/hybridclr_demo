#!/usr/bin/env python3
"""Observe all four exact Git authorities once, with durable failure evidence.

This is a point-in-time transport prerequisite, not a reusable acceptance lease.
No fetch, merge, reset, credential change, Unity launch or automatic retry occurs.
"""
import argparse
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'R03'))
from batch_contract import loads,require,sha
from batch_evidence import write
from git_diagnostics import capture_git,redact
from run_local import identity,REPOS


def check(workspace,output,demo_commit):
    workspace,output=Path(workspace).absolute(),Path(output).absolute()
    require(workspace==workspace.resolve() and HERE==workspace/'hybridclr_demo/Tools/AssemblyShadow/R03Completion', 'Exact owning source workspace')
    require(re.fullmatch('[0-9a-f]{40}',demo_commit) is not None, 'Exact published demo revision')
    require(output==output.resolve() and not output.exists() and output.parent.is_dir() and
        not output.is_relative_to(workspace) and not workspace.is_relative_to(output), 'Unused external transport output')
    pins=loads((HERE/'source-pins.json').read_text())
    other=loads((HERE.parent/'R03/source-pins.json').read_text())
    require(all(pins[k]==other[k] for k in (*REPOS[1:],'branch')), 'Two source pin manifests agree')
    pins=dict(pins,hybridclr_demo=demo_commit);output.mkdir()
    rows=[]
    for name in REPOS:
        row={'repository':'night-outlook/'+name,'path':str(workspace/name),'expectedCommit':pins[name],'result':'Failed'}
        try:
            with capture_git(output/'git-observations',pins,'transport-preflight/'+name):
                row['authority']=identity(workspace/name,pins[name])
            row['result']='Passed'
        except Exception as error:
            row['error']={'type':type(error).__name__,'message':redact(str(error))}
        rows.append(row)
    result={'kind':'R03TransportPreflight','schemaVersion':1,'result':'TransportReady' if all(r['result']=='Passed' for r in rows) else 'TransportBlocked',
        'repositories':rows,'pins':pins,'helperSha256':sha(Path(__file__)),
        'pointInTimeOnly':True,'runtimeAcceptance':False,'unityRun':False,'playerRun':False,'retryPerformed':False}
    write(output/'verification.json',result)
    return 0 if result['result']=='TransportReady' else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('workspace','output','demo-commit'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    return check(args.workspace,args.output,args.demo_commit)


if __name__=='__main__':raise SystemExit(main())
