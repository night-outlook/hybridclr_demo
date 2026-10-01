import collections,datetime,hashlib,json,pathlib,shutil,subprocess,xml.etree.ElementTree as E
R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api');P=R.parent/'Preflight-R03LocalBatch-20261001D-build-api';D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();rows=[]
for receipt in sorted((R/'builds').glob('*/build-receipt.json')):
 role=receipt.parent.name;d=json.loads(receipt.read_text());project=R/'projects'/role;assert d['result']=='Passed' and d['errors']==0 and d['nonGeneratedCorePreserved'] is True
 matches=[]
 for p in sorted((project/'HybridCLRData').rglob('assembly-shadow-install.json')):
  if sha(p)!=d['installReceiptSha256']:continue
  root=p.parent;expected={x['path']:x for x in d['installedAfter']};actual={str(x.relative_to(root)):x for x in root.rglob('*') if x.is_file()};extra=sorted(set(actual)-set(expected));missing=sorted(set(expected)-set(actual));diff=[n for n in sorted(set(actual)&set(expected)) if sha(actual[n])!=expected[n]['sha256'] or actual[n].stat().st_size!=expected[n]['size']]
  saved=P/'native-receipts'/role/('installed-sdk.json' if 'LocalIl2CppData-OSXEditor' in p.parts else 'stripped-aot-copy.json');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
  matches.append({'path':str(p),'sha256':sha(p),'retainedCopy':str(saved),'nativeRoot':str(root),'files':len(actual),'exactInstalledAfterMatch':not(extra or missing or diff),'extra':extra,'missing':missing,'changed':diff,'repositories':json.loads(p.read_text())['repositories']})
 assert len(matches)==2
 app=pathlib.Path(d['outputPath']);expected={f['path']:f for f in d['playerFiles']};actual={str(p.relative_to(app)):p for p in app.rglob('*') if p.is_file()};assert set(actual)==set(expected)
 for n,p in actual.items():assert sha(p)==expected[n]['sha256'] and p.stat().st_size==expected[n]['size']
 executables=[p for p in (app/'Contents/MacOS').iterdir() if p.is_file()];assert len(executables)==1
 command=['lipo','-archs',str(executables[0])];x=subprocess.run(command,capture_output=True,text=True);assert x.returncode==0 and x.stdout.strip()=='arm64'
 rows.append({'role':role,'receiptPath':str(receipt),'receiptSha256':sha(receipt),'rawBuildResult':d['result'],'runnerBuildCellResult':'Failed','failure':'Exact native installation receipt is required','installReceiptSha256':d['installReceiptSha256'],'hashMatchingInstallReceipts':matches,'playerInventoryAuthenticated':len(expected),'playerBytes':sum(f['size'] for f in expected.values()),'architectureOperation':{'command':command,'exitCode':x.returncode,'stdout':x.stdout,'stderr':x.stderr},'fresh':True,'notAcceptanceOverride':True})
xml=R/'editor-results.xml';root=E.parse(xml).getroot();cases=list(root.iter('test-case'));admission=json.loads((R/'host/admission/results.json').read_text());required=[]
for c in admission['cases']:
 found=[x for x in cases if 'R03EvolutionContractTests.RealDllEvolutionContract' in x.get('fullname','') and c['id'] in x.get('fullname','')];assert len(found)==1 and found[0].get('result')=='Passed';required.append({'id':c['id'],'fullname':found[0].get('fullname'),'result':'Passed'})
cycle=[x for x in cases if x.get('fullname','').endswith('GraphAndInputTests.CyclesReportClosedPath')];assert len(cycle)==1 and cycle[0].get('result')=='Passed'
skipped=[{'fullname':x.get('fullname'),'result':x.get('result'),'label':x.get('label'),'reason':x.findtext('reason/message')} for x in cases if x.get('result')!='Passed'];assert len(cases)==755 and len(skipped)==1 and skipped[0]['result']=='Skipped'
record={'kind':'ReadOnlyR03BatchDDiagnosis','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Existing artifacts, receipts, source and XML only; no retry, source change, blocked Player launch or failed-cell reclassification','builds':rows,'editor':{'xml':str(xml),'sha256':sha(xml),'rootAttributes':root.attrib,'cases':len(cases),'passed':754,'failed':0,'skipped':skipped,'skippedCoverage':'NoCoverage for frozen M01 demo-resource asset test in isolated project','all35MandatoryR03Contracts':required,'targetCycleRegression':{'fullname':cycle[0].get('fullname'),'result':'Passed'},'runnerCell':'Failed','failure':'Nonzero real Editor test execution required'},'rootCauses':['verify_build globally searches HybridCLRData by hash and requires exactly one receipt; stripped-AOT generation copies the same receipt into its output tree, producing two legitimate hash matches.','editor_tests runs the entire package suite in an isolated project lacking frozen M01 resource assets; that test calls Assert.Ignore, making aggregate root Skipped:Ignored despite all mandatory R03 contracts passing.'],'sourceFiles':{str(p):sha(p) for p in [D/'Tools/AssemblyShadow/R03/run_local.py',D/'Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs',pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity/Tests/Editor/AssemblyShadow/ResourceAbiTests.cs')]}}
(P/'DIAGNOSTIC_FINDINGS.json').write_text(json.dumps(record,indent=2)+'\n');print('Diagnosis complete: four native artifacts, two matching receipts each; 754 Passed/1 Ignored, all35 required IDs and target cycle Passed')
