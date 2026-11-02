from pathlib import Path
import json,subprocess,hashlib,datetime,re
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';base='d802632594321f431716e636ad41c68d1f667c7c';head='c726ed74654a921c8f51d65189dcf6a6e63d0803';nb='6510aed7cab67e9fc70b13ae22a115ad9819193b';nh='ca0aab8e0abcbcb60a1532223d9e1bdb0aea86c4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
changed=git(D,'diff','--name-only',base,head).splitlines();assert changed==['Docs/AssemblyShadow/README.md','Tools/AssemblyShadow/R03IR/test_k_contracts.py']
# The four required workflows run explicit named suites, not discovery of test_k_contracts.
inputs=[]
for path in git(D,'ls-tree','-r','--name-only',head,'Tools/AssemblyShadow/R03','Tools/AssemblyShadow/R03IR','.github/workflows/r03-ir-current-native-local-cycle-host.yml','.github/workflows/r03-ir-current-native-source-only.yml','.github/workflows/r03-ir-current-native-vm-delta-source-only.yml','.github/workflows/r03-ir-fixture.yml').splitlines():
 if path=='Tools/AssemblyShadow/R03IR/test_k_contracts.py':continue
 a=git(D,'rev-parse',base+':'+path);b=git(D,'rev-parse',head+':'+path);assert a==b;inputs.append(dict(repository='hybridclr_demo',path=path,gitBlob=a,sha256=sha(D/path)))
nd=git(W/'il2cpp_plus','diff','--name-only',nb,nh).splitlines();assert nd==['tools/r03/diagnostic_stream/current_execution_producer.py','tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py'];assert not git(W/'il2cpp_plus','diff','--name-only',nb,nh,'libil2cpp/vm','.github/workflows/r03-cxx11-unity-compat-host.yml')
for path in git(W/'il2cpp_plus','ls-tree','-r','--name-only',nh,'libil2cpp/vm','.github/workflows/r03-cxx11-unity-compat-host.yml','tools/r03/diagnostic_stream/cxx11_unity_compat_fixture.cpp','tools/r03/diagnostic_stream/bounded_general_composer_fixture.cpp','tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp','tools/r03/diagnostic_stream/owned_physical_names_fixture.cpp','tools/r03/diagnostic_stream/empty_live_fixture').splitlines():
 a=git(W/'il2cpp_plus','rev-parse',nb+':'+path);assert a==git(W/'il2cpp_plus','rev-parse',nh+':'+path);inputs.append(dict(repository='il2cpp_plus',path=path,gitBlob=a,sha256=sha(W/'il2cpp_plus'/path)))
jobs=[]
for p in sorted(B.glob('oneuse-E-CI_JOBS-*.json')):
 g=load(p)
 for j in g['jobs']:
  assert j['status']=='completed' and j['conclusion']=='success';log=B/f"oneuse-E-CI_LOG-{j['id']}.json";data=load(log);assert not data.get('isError');text=data['structuredContent']['content'];expected=nb if g['repo'].endswith('il2cpp_plus') else base;assert expected in text
  jobs.append(dict(run=g['run'],repo=g['repo'],job=j['id'],name=j['name'],conclusion=j['conclusion'],executedCommit=expected,logPath=str(log),logSha256=sha(log),testCounts=[int(n) for n in re.findall(r'Ran (\d+) tests?',text)]))
assert len(jobs)==11
artifacts=[]
for osname,aid,digest in [('macos',13120939483,'f25168cd0fef632eed1b3ee83970fc3ec132139251be7ca3ceaea58e59fade36'),('ubuntu',13121941328,'34208c260f9253457ec5916d75478d837c4d00641c4f1335b977273e2942c5df')]:
 root=B/'oneuse-E-CI-artifacts-20261102'/osname;assert sha(root/'artifact.zip')==digest;raw=(root/'historical-differences.json').read_bytes();assert raw.endswith(b'\n') and not raw.endswith(b'\\n');d=json.loads(raw);assert d['generatedOriginalCount']==d['matchedPathAssemblyRefsAndSize']==d['differentByteOrMvidCount']==15 and len(d['differences'])==15 and d['historicalSBytesReplaced'] is False
 v=load(root/'verified.json');assert v['source']==base and v['regeneratedOriginalSBytesAdopted'] is False
 t=load(root/'pinned-target-verdict.json');assert t['result']=='PassedPinnedFreshGeneratorBytesAndRepeatability_HostOnly'
 for k in ['first','repeat']:
  assert t[k]['bytes']==2048 and t[k]['sha256']=='8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd' and t[k]['mvid']=='597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff'
 assert 'Build succeeded.' in (root/'build.log').read_text() and int((root/'duplicate.exit').read_text())!=0
 receipt=dict(artifactId=aid,runId=41401796170,source=base,zipSha256=digest,transport='Connector short-lived artifact URL, curl normal TLS verification; URL intentionally not persisted',strictComparisonJsonParsed=True,trailingRealLf=True,files=[dict(path=str(p.relative_to(root)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(root.rglob('*')) if p.is_file()])
 (root/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');artifacts.append(dict(os=osname,receipt=receipt,comparison=d,strictIrProof=t))
p=B/'oneuse-E-CI_GATE-20261102.json';assert not p.exists();p.write_text(json.dumps(dict(kind='IndependentOneuseESourceBoundCIGate',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PassedRequiredSourceEquivalentCI_HostOnly',actualGeneratorGatePassed=True,demoFinalSource=head,demoExecutedCI=base,demoDelta=changed,equivalenceLimit='README status and test_k_contracts.py only; test_k is not imported or discovered by any of the four required workflows. Final commit K/L/terminal CI successes separately available. No changed required workflow/tooling input is substituted.',nativeFinalSource=nh,nativeExecutedCI=nb,nativeDelta=nd,nativeEquivalenceLimit='Two unrelated host tools differ; every production VM file, C++11 workflow and its fixture inputs are byte-identical. Not a new native Player or SDK compile.',sourceInputBindings=inputs,jobs=jobs,artifacts=artifacts,ordinaryMvidNote='Ordinary comparison inventory lacks MVID fields; SHA differences recorded, no unreported MVID inferred',historicalSBytesAdopted=False,runtimeAcceptance=False),indent=2)+'\n');print('CI gate Passed',len(jobs),'jobs;',len(inputs),'source input blob/SHA bindings')
