#!/usr/bin/env python3
"""Verify the committed primary handoff and source target before local tools.

This command performs no fetch, checkout, pin mutation, installation or Unity
invocation. It reports source preflight, not build provenance or gate approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shadow_tools as s

WEB='Documents/AgentHandoff/WEB_TO_LOCAL.md'
TARGETS='Documents/AgentHandoff/source-targets.json'
REQUIRED_SECTIONS=('## Objective','## Source targets','## Implementation','## Local validation',
                   '## Failure evidence','## Alternatives','## Risks','## Local correction boundary','## Human review gate')


def verify(project,role):
    project=Path(project).resolve(strict=True)
    s.require(Path(s.git(project,'rev-parse','--show-toplevel').decode().strip()).resolve()==project,'Project must be a Git root')
    committed={}
    for relative in (WEB,TARGETS):
        path=s.safe_file(project,relative)
        s.require(path.is_file(),'Missing authoritative handoff: '+relative)
        raw=s.git(project,'show','HEAD:'+relative)
        s.require(raw==path.read_bytes(),'Handoff differs from committed HEAD: '+relative)
        committed[relative]=hashlib.sha256(raw).hexdigest()
    text=(project/WEB).read_text()
    s.require(all(section in text for section in REQUIRED_SECTIONS),'Incomplete handoff sections')
    targets=s.read_json(project/TARGETS)
    s.require(targets.get('schemaVersion')==1 and targets.get('kind')=='PrimaryImplementationSourceTargets','Unsupported handoff target schema')
    target=targets.get('demoTargets',{}).get(role)
    s.require(isinstance(target,dict),'Missing source target role')
    branch=s.git(project,'branch','--show-current').decode().strip()
    s.require(branch==target.get('branch'),'Wrong handoff branch')
    origin=s.git(project,'remote','get-url','origin').decode().strip()
    s.require(origin in ('git@github.com:night-outlook/hybridclr_demo.git','https://github.com/night-outlook/hybridclr_demo.git','https://github.com/night-outlook/hybridclr_demo'),'Wrong handoff origin')
    anchor=target.get('codeCommit','')
    s.require(re.fullmatch('[0-9a-f]{40}',anchor) is not None and target.get('repository')=='night-outlook/hybridclr_demo','Invalid source anchor')
    pins=s.read_json(project/s.PINS)
    s.require(pins.get('demo',{}).get('revision')==anchor,'Demo source pin does not identify this handoff implementation')
    for key in ('unityVersion','target','architecture'):
        s.require(pins.get(key)==targets.get(key),'Handoff environment differs: '+key)
    for key in ('hybridclr','hybridclrUnity','il2cppPlus'):
        expected=target['runtimePins'][key]
        s.require(all(pins.get(key,{}).get(k)==expected.get(k) for k in ('url','revision')),'Handoff runtime source differs: '+key)
    s.verify_demo(project,pins['demo'])
    return {'kind':'PrimaryHandoffPreflight','status':'SourceTargetVerifiedNotBuildAccepted','role':role,
            'repository':target['repository'],'branch':branch,'checkoutCommit':s.git(project,'rev-parse','HEAD').decode().strip(),
            'codeCommit':anchor,'handoffHashes':committed,'sourcePinSha256':hashlib.sha256((project/s.PINS).read_bytes()).hexdigest(),
            'nativeInstallationVerified':False,'humanGatePassed':False,'mayEnterR02':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True)
    p.add_argument('--role',choices=('candidate','reproduction'),required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();report=verify(a.project,a.role)
    s.require(a.output.is_absolute() and a.output==a.output.resolve() and a.output.parent.is_dir(),'Output must be a new canonical file in an existing directory')
    with a.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,RuntimeError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
