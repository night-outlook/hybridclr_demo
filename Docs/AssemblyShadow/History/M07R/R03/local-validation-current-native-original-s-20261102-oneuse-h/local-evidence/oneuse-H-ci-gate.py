from pathlib import Path
import json,hashlib,datetime,re,subprocess
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';H='3e838edf8995e40058f3bc6c42f071446a0be821';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=load(B/'oneuse-H-CI_EXACT_DEMO_RUNS.json');runs=json.loads(raw['structuredContent']['content'])['workflow_runs'];required=['r03-ir-current-native-local-cycle-host.yml','r03-ir-current-native-source-only.yml','r03-ir-current-native-vm-delta-source-only.yml','r03-ir-current-native-oracle-source-only.yml','r03-ir-fixture.yml','r03-ir-host.yml','r03-k-host-contracts.yml','r03-k-sourcecheck.yml','r03-l-contracts.yml'];records=[]
for name in required:
 rows=[x for x in runs if x['path']=='.github/workflows/'+name];assert len(rows)==1;r=rows[0];assert r['head_sha']==H and r['event']=='push' and r['status']=='completed' and r['conclusion']=='success';j=load(B/f"oneuse-H-CI_JOBS-{r['id']}.json")['metadata']['structuredContent']['jobs'];assert len(j)==2 and any('macos' in x['name'] for x in j) and any('ubuntu' in x['name'] for x in j);jobs=[]
 for x in j:
  assert x['status']=='completed' and x['conclusion']=='success';p=B/f"oneuse-H-CI_LOG-{x['id']}.json";data=load(p);assert not data.get('isError');s=data['structuredContent']['content'];assert H in s
  if 'local-cycle-host' in name:
   for n in ['snapshot_general_transport_contracts.py','engine_owner_quit_contracts.py','complete_general_diagnostic_contracts.py','failed_player_receipt_contracts.py','current_native_handoff_ci_contracts.py']:assert n in s
   assert 'cdd3f7bc671880052e4f55ae4c1cd75b99a603e1' in s
  jobs.append(dict(id=x['id'],name=x['name'],conclusion=x['conclusion'],log=str(p),sha256=sha(p),testCountSummaries=[int(n) for n in re.findall(r'Ran (\d+) tests?',s)]))
 p=D/'.github/workflows'/name;records.append(dict(run=r['id'],head=H,event=r['event'],path=r['path'],conclusion=r['conclusion'],workflowSha256=sha(p),jobs=jobs))
artifacts=[]
for osname,id,digest in [('macos',13212925052,'78d14259bca8b50fa3ad4ba74a89c68817099f5382b32f5c7be29d90bb871816'),('ubuntu',13212212703,'146843759f158e53d1db2781a25a065bf0203ab14dd2e96871e86eeb84ea66fa')]:
 root=B/'oneuse-H-CI-artifacts-20261102'/osname;assert sha(root/'artifact.zip')==digest;raw=(root/'historical-differences.json').read_bytes();assert raw.endswith(b'\n');c=json.loads(raw);v=load(root/'verified.json');t=load(root/'pinned-target-verdict.json');assert c['matchedPathAssemblyRefsAndSize']==c['generatedOriginalCount']==15 and c['historicalSBytesReplaced'] is False and v['source']==H and v['regeneratedOriginalSBytesAdopted'] is False
 assert t['result']=='PassedPinnedFreshGeneratorBytesAndRepeatability_HostOnly'
 for k in ['first','repeat']:assert t[k]['bytes']==2048 and t[k]['sha256']=='8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd' and t[k]['mvid']=='597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff'
 assert 'Build succeeded.' in (root/'build.log').read_text() and int((root/'duplicate.exit').read_text())!=0
 receipt=dict(artifactId=id,run=41596496942,source=H,zipSha256=digest,transport='Connector artifact download reference; curl default TLS; temporary URL not persisted',strictJsonParsed=True,files=[dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)) for p in root.rglob('*') if p.is_file()]);(root/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');artifacts.append(dict(os=osname,receipt=receipt,comparison=c,strictIr=t))
source=[]
for r in load(D/'Tools/AssemblyShadow/R03IR/current_native_candidate.json')['files']+[dict(repository='il2cpp_plus',**r) for r in load(D/'Tools/AssemblyShadow/R03IR/current_native_vm_delta.json')['files']]:
 p=W/r['repository']/r['path'];assert subprocess.check_output(['git','-C',str(W/r['repository']),'hash-object',str(p)],text=True).strip()==r['gitBlob'];source.append(dict(repository=r['repository'],path=r['path'],gitBlob=r['gitBlob'],sha256=sha(p)))
assert len(source)==56
out=B/'oneuse-H-CI_GATE.json';assert not out.exists();out.write_text(json.dumps(dict(kind='IndependentOneuseHExactSourceCIGate',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PassedNineExactPushWorkflows_EighteenJobs_HostOnly',actualGeneratorGatePassed=True,head=H,native='cdd3f7bc671880052e4f55ae4c1cd75b99a603e1',requiredWorkflows=records,requiredWorkflowCount=9,requiredJobsPassed=18,sourceBindings=source,artifactProof=artifacts,supplementalCancelledRuns=[dict(id=r['id'],path=r['path'],conclusion=r['conclusion'],mandatory=False) for r in runs if r['path'] not in ['.github/workflows/'+n for n in required]],ordinaryMvidNote='Only recorded SHA differences accepted; ordinary inventories omit MVID fields',originalSRegeneratedBytesAdopted=False,runtimeAcceptance=False),indent=2)+'\n');print('Exact source CI gate Passed:9 fresh push workflows,18 jobs,56 source bindings, both generator artifacts authenticated.')
