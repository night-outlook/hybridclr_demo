#!/usr/bin/env python3
"""Exact-source Bee candidate assembly; only blob/tree object uploads, no commits/refs."""
import argparse,base64,hashlib,json,os,subprocess,urllib.request
from pathlib import Path
BASE='2b5cf60363dc7c895deaad26bdaf7af70cde612a'
EXPECTED={
'Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs':('8027ecbdeb75523b8202d00b5eef2279c9463f17','90eeccfa30e904955708d11530b99f179584de8c'),
'Tools/AssemblyShadow/R03IR/bee_observation.py':('9534c1b822b79d524cf93df145022a6fcb45f9bc','5468729abfe8d222b752be5e69a865cef6888d17'),
'Tools/AssemblyShadow/R03IR/test_k_contracts.py':('cd52aafa9f912a1027864e09a7c36db06eb69dfb','2f7b8056a7ec75bd6b398d14ef176622f01e9b27'),
'Tools/AssemblyShadow/R03IR/test_factory_observation.py':(None,'eca88cfa6a0b68b376425c6f5a0cfa8804c1ac48')}
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,('Nonunique exact-source anchor',a[:80])
 return s.replace(a,b)
def prepare(root,controls,out):
 assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==BASE
 for name,(old,new) in EXPECTED.items():
  p=root/name
  if old is None:
   assert not p.exists();data=(controls/name).read_bytes();assert blob(data)==new
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  else:assert blob(p.read_bytes())==old,(name,blob(p.read_bytes()))
 p=root/'Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs';s=p.read_text()
 a='    // K observational instrumentation. No detours or result-processor replacement.'
 assert s.count(a)==1
 s=s[:s.index(a)]+(controls/'Tools/AssemblyShadow/R03IR/l-bee-tail.cs.txt').read_text();p.write_text(s)
 p=root/'Tools/AssemblyShadow/R03IR/bee_observation.py';s=p.read_text()
 a="            data.get('driverInitiallyAbsent') is True and data.get('limitsExceeded') is False,"
 b="""            data.get('driverInitiallyAbsent') is True and data.get('limitsExceeded') is False and
            data.get('acquisition') == 'ScopedOriginalFactoryForwarderV1' and data.get('factoryRestored') is True and
            type(data.get('factoryCalls')) is int and 1 <= data['factoryCalls'] <= 64 and
            type(data.get('selectedFactorySequence')) is int and 1 <= data['selectedFactorySequence'] <= data['factoryCalls'],"""
 s=once(s,a,b);p.write_text(s)
 p=root/'Tools/AssemblyShadow/R03IR/test_k_contracts.py';s=p.read_text()
 a="             'driverInitiallyAbsent':True,'limitsExceeded':False,'buildErrors':2,"
 s=once(s,a,a+"\n             'acquisition':'ScopedOriginalFactoryForwarderV1','factoryRestored':True,'factoryCalls':2,'selectedFactorySequence':1,")
 s=once(s,"for field in ['sameProcessor','driverInitiallyAbsent']:","for field in ['sameProcessor','driverInitiallyAbsent','factoryRestored']:");p.write_text(s)
 rows=[]
 for name,(_,expected) in EXPECTED.items():
  data=(root/name).read_bytes();assert blob(data)==expected,(name,blob(data),expected)
  rows.append({'path':name,'gitBlob':expected,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 out.mkdir(parents=True,exist_ok=True)
 (out/'candidate.json').write_text(json.dumps({'base':BASE,'files':rows,'branchesUpdated':False},indent=2)+'\n')
 subprocess.run(['git','-C',str(root),'diff','--check'],check=True)
 print(json.dumps({'result':'ExactBeeCandidatePrepared','files':len(rows),'base':BASE}))
def objects(root,out):
 record=json.loads((out/'candidate.json').read_text());assert record['base']==BASE
 def api(path,data):
  assert path in ('git/blobs','git/trees')
  req=urllib.request.Request('https://api.github.com/repos/night-outlook/hybridclr_demo/'+path,data=json.dumps(data).encode(),method='POST',headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'PinnedPrimaryCandidateAssembler'})
  with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
 rows=[]
 for entry in record['files']:
  data=(root/entry['path']).read_bytes();assert blob(data)==entry['gitBlob'] and hashlib.sha256(data).hexdigest()==entry['sha256']
  result=api('git/blobs',{'content':base64.b64encode(data).decode(),'encoding':'base64'});assert result['sha']==entry['gitBlob']
  rows.append({'path':entry['path'],'mode':'100644','type':'blob','sha':result['sha']})
 tree=subprocess.check_output(['git','-C',str(root),'rev-parse',BASE+'^{tree}'],text=True).strip()
 result=api('git/trees',{'base_tree':tree,'tree':rows})
 (out/'remote-tree.json').write_text(json.dumps({'baseCommit':BASE,'baseTree':tree,'candidateTree':result['sha'],'entries':rows,'commitsCreated':False,'refsUpdated':False},indent=2)+'\n')
 print('Candidate tree:',result['sha'],'; no commit or ref created')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--objects-only',action='store_true');a=p.parse_args()
 if a.objects_only:objects(a.source,a.output)
 else:prepare(a.source,a.controls,a.output)
