#!/usr/bin/env python3
"""CI-only blob staging; no Git ref, commit, branch, or historical evidence write."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

root=Path(__file__).resolve().parents[4]
out=Path(os.environ['RUNNER_TEMP'])/'ir-runtime01-demo'
names=['Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs',
'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp',
'Tools/AssemblyShadow/R03/PlayerApiCompile/UnityEnvironment.cs',
'Tools/AssemblyShadow/R03IR/run_terminal_local.py',
'Tools/AssemblyShadow/R03IR/test_terminal_contract.py',
'Tools/AssemblyShadow/R03/native_validation.py','Tools/AssemblyShadow/R03/source-pins.json',
'Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03IR/Runtime01/test_candidate.py']
expected=sorted(set(names)-{'Tools/AssemblyShadow/R03IR/Runtime01/test_candidate.py'}|
                {'Tools/AssemblyShadow/R03IR/Runtime01/apply_exact_patch.py'})
changed=sorted(subprocess.check_output(['git','-C',str(root),'diff','--name-only'],text=True).splitlines())
assert changed==expected,(changed,expected)
subprocess.run(['git','-C',str(root),'diff','--check'],check=True)
(out/'diff.patch').write_bytes(subprocess.check_output(['git','-C',str(root),'diff','--',*names]))
rows=[]
for name in names:
    data=(root/name).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    req=urllib.request.Request('https://api.github.com/repos/night-outlook/hybridclr_demo/git/blobs',
        data=json.dumps({'content':data.decode(),'encoding':'utf-8'}).encode(),
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=60) as response:assert json.load(response)['sha']==blob
    target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    rows.append({'path':name,'gitBlob':blob,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
pins=json.loads((root/'Tools/AssemblyShadow/R03/source-pins.json').read_text())
receipt={'kind':'IRRuntime01DemoCandidate','result':'HostPassed','sourceCommit':os.environ['GITHUB_SHA'],
         'runId':os.environ['GITHUB_RUN_ID'],'package':pins['hybridclr_unity'],'native':pins['il2cpp_plus'],
         'files':rows,'gitRefsModifiedByJob':False,'unityRun':False,'runtimeAcceptance':False}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True))
