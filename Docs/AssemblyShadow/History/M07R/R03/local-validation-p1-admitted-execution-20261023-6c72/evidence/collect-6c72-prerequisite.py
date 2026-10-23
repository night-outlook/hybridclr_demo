from pathlib import Path
import json,hashlib,subprocess,datetime,os,concurrent.futures,re
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');bundle=json.loads((B/'Admission-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json').read_text());E=bundle['EXPECTED.json'];W=Path(E['workspace']);D=W/'hybridclr_demo';P=Path(E['preflight']);O=Path(E['output']);S=Path(E['scratch']);C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-6c72'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1<<20),b''):h.update(data)
 return h.hexdigest()
def save(name,v):q=B/name;assert not q.exists();q.write_text(json.dumps(v,indent=2)+'\n')
load=lambda p:json.loads(p.read_text())
started=now();dispatch=load(B/'Dispatch-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json');assert len(dispatch['commands'])==1
cmd=dispatch['commands'][0];assert cmd['exit']==1
stderr=Path(cmd['stderr']);text=stderr.read_text();assert sha(stderr)==cmd['stderrSha256'] and sha(Path(cmd['stdout']))==cmd['stdoutSha256'] and 'Ran 13 tests' in text and 'FAILED (errors=1)' in text and 'test_pristine_root_fail_closed' in text and 'ValueError: Root is non-absolute, already used, or not canonical:' in text
assert text.count('.')>=12 and '............E\n' in text
for root in [P,O,S,C]:assert not root.exists() and not root.is_symlink() and root.resolve()==root
tool=D/'Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py';test=D/'Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py'
for path,blob in [(tool,'cf2fdf39fe17df076d50dcc33ed72c757eaa3b26'),(test,'58e6e0b9ff870d1ada20021ab36a82882d60b837')]:assert path.read_bytes()==subprocess.check_output(['git','-C',str(D),'cat-file','blob',blob])
assert 'parent = Path(d)' in test.read_text() and "pristine_root(parent / 'absent')" in test.read_text()
tmp=os.environ.get('TMPDIR');assert tmp and str(Path(tmp).resolve())!=str(Path(tmp)) and Path('/var').resolve()==Path('/private/var')
failure=dict(id='IR-LOCAL-P1-PREPARER-TEMP-01',status='ReproducedPrerequisiteTestError',symptom='Published 13-test preparer suite returns exit1: 12 Passed, one ERROR in test_pristine_root_fail_closed.',failedCommand=cmd,testsRun=13,passed=12,failures=0,errors=1,skipped=0,errorTest='LocalCollectorRepairTests.test_pristine_root_fail_closed',testSourcePath=str(test),testSourceSha256=sha(test),testGitBlob='58e6e0b9ff870d1ada20021ab36a82882d60b837',testLine=106,toolSourcePath=str(tool),toolSourceSha256=sha(tool),toolGitBlob='cf2fdf39fe17df076d50dcc33ed72c757eaa3b26',toolLine=148,inheritedTMPDIR=tmp,canonicalInheritedTmp=str(Path(tmp).resolve()),sourceFixture='parent = Path(d); pristine_root(parent / absent)',actualException='ValueError: Root is non-absolute, already used, or not canonical: /var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T/tmpqsr57skb/absent',rootCause='The test-owned TemporaryDirectory path is not canonicalized. macOS /var is a symlink to /private/var, so the expected-good absent child fails the unchanged canonical-path guard before later controls run.',scope='Published preparer test fixture under Docs; no native/product/SDK failure demonstrated; prepare and core never launched.',recommendedDirection='Canonicalize only the test-owned temporary parent before constructing the expected-good absent child; add an inherited aliased-parent cohort while retaining rejection of actual noncanonical, existing, symlink and relative roots. Do not weaken pristine_root or override TMPDIR. Publish corrected tests and a new exact handoff with unused roots.',remainingUncertainty='Actual shipped preparation, corrected collector, 25-component host/SDK batch and independent auditor remain unexecuted.',validationRequired='Fresh published preparer regressions under native macOS /var alias and canonical parent, then all source/custody gates, one separately authorized 25-component cycle, official managed/100 native/Git joins and after-preservation.',coreInvoked=False,preparerInvoked=False,original85Tests='NotRun',noRetry=True,runtimeAcceptance=False)
save('FINDING-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json',failure)
# Installed official SDK after-preservation against admitted immutable inventory.
sdk=load(B/'Preflight-R03-P1-VM-OWNED-JSON-20261021-9a63/SDK_BEFORE.json')
for row in sdk['files']:
 q=Path(row['path']);assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'] and (os.readlink(q) if q.is_symlink() else None)==row['symlink']
paths={Path(sdk['anchor']),Path(sdk['anchor']).parent.parent/'Info.plist'}
for root in sdk['roots']:paths.update(q for q in Path(root).rglob('*') if q.is_file())
assert paths=={Path(row['path']) for row in sdk['files']}
ret=bundle['ADMISSION_RETAINED_BEFORE.json'];links=0
for item in ret['consumed']:
 raw=Path(item['rawRoot']);scratch=Path(item['scratchRoot']);assert sha(raw/'MANIFEST.json')==item['manifestSha256']
 for row in load(raw/'MANIFEST.json')['files']:
  q=raw/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
 for row in load(raw/'native-sdk/native-sdk-inputs.json')['files']:assert sha(scratch/row['path'])==row['sha256']
 for row in load(raw/'legacy-host/MANIFEST.json')['files']:
  if row.get('kind')=='Symlink':q=raw/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target'];links+=1
 audit=Path(item['auditRoot']);assert {str(q) for q in audit.rglob('*') if q.is_file() and not q.is_symlink()}=={row['path'] for row in item['auditFiles']}
 for row in item['auditFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
cps=bundle['ADMISSION_CHECKPOINTS_BEFORE.json']
for item in cps['checkpoints']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 assert {str(q.relative_to(root)) for q in root.rglob('*') if q.is_file()}=={row['path'] for row in item['files']}|{'MANIFEST.sha256'}
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
blocked=bundle['BLOCKED_ADMISSION_BEFORE.json'];root=Path(blocked['checkpoint']);assert sha(root/'MANIFEST.sha256')==blocked['manifestSha256']
for row in blocked['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
for row in blocked['externalFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
bp=Path(blocked['externalPreflight']);assert {str(q) for q in bp.rglob('*') if q.is_file() and not q.is_symlink()}=={row['path'] for row in blocked['externalFiles']}
assert not (B/'R03-P1-ADMITTED-EXECUTION-20261022-e1e5').exists() and not (B/'Scratch-R03-P1-ADMITTED-EXECUTION-20261022-e1e5').exists()
original_hosts=[]
for suffix in ['fc0d3565','74dbdbea-a1']:
 raw=B/('R03-PRIMARY-HOST-ONLY-20261015-'+suffix);cp=D/'Docs/AssemblyShadow/History/M07R/R03'/('local-validation-host-only-20261015-'+suffix)
 assert sha(raw/'MANIFEST.json')==sha(cp/'host/MANIFEST.json')
 for row in load(raw/'MANIFEST.json')['files']:
  q=raw/row['path']
  if row.get('kind')=='Symlink':assert q.is_symlink() and os.readlink(q)==row['target']
  else:assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
 original_hosts.append(dict(root=str(raw),manifestSha256=sha(raw/'MANIFEST.json'),verifiedEntries=len(load(raw/'MANIFEST.json')['files']),result=load(raw/'RESULT.json')['result']))
def check(n):
 rows=[];path=W/n
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  argv=['git','-C',str(path),*args];t=now();r=subprocess.run(argv,capture_output=True,text=True,timeout=90);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==E['pins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==E['pins'][n]
 return n,rows
repos=dict(concurrent.futures.ThreadPoolExecutor(4).map(check,E['pins']))
versions=[]
for argv in [['python3','--version'],['sw_vers']]:
 t=now();r=subprocess.run(argv,capture_output=True,text=True);versions.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
after=dict(kind='IndependentPreservationAfterPrerequisiteFailure_NotPrimaryVerifyAfterReceipt',result='Preserved',start=started,end=now(),sourcePins=E['pins'],fourCleanExactGitRepositories=repos,SDKFilesVerified=len(sdk['files']),SDKBytesVerified=sum(row['bytes'] for row in sdk['files']),SDKInventoryUnchanged=True,consumedP1RawScratchAudits=len(ret['consumed']),historicalNegativeSymlinks=links,priorCheckpointSets=len(cps['checkpoints']),separateBlockedCheckpointFilesVerified=len(blocked['files']),separateBlockedExternalPreflightFilesVerified=len(blocked['externalFiles']),originalHosts=original_hosts,oldBlockedRawAndScratchStillAbsent=True,allHistoricalStatesUnchanged=True,protectedSourcesUnmodified=True,inheritedTMPDIR=tmp,canonicalTmp=str(Path(tmp).resolve()),environment=versions,preparation='NotRun',core='NotRun',officialSDKCompiles='NotRun',PrimaryBLOCKED_HISTORY_AFTER='NotRun_NoPREPARATIONReceipt')
save('PreservationAfter-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json',after)
names=['command-failures','legacy-host','metadata-gate','bounded-class','bounded-physical','bounded-first-use','owned-general','live-general','owned-execution','empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json','live-owned-physical-json','observed-type-shape','live-type-shape-census','observed-type-shape-json','vm-shape-json','admitted-execution','bounded-status','bounded-inventory','frozen-v2','managed-sdk','native-sdk']
result=dict(kind='IndependentLocalPrerequisiteOutcome_NotCoreResult',result='PrerequisiteBlocked',batchResult='NotRun',findingId=failure['id'],sourcePins=E['pins'],rootAdmission='PassedForEnumeratedBindings',preparerUnitTests=dict(status='Failed',tests=13,passed=12,errors=1,failures=0,skipped=0,receipt=cmd),preparerExecution='NotRun',PREPARATION='Unavailable_NotRun',coreExecution='NotRun',components=[dict(name=n,status='NotRun',invoked=False) for n in names],componentCount=25,attemptedComponentCount=0,original85FailureTests='NotRun',allEightInventories='NotRun',nineAdmissionCasesPerProfile='NotRun',managedProductsAndNegative='NotRun',native100Configurations='NotRun',batch20GitCommands='NotRun',independentAuditor='NotRun',PrimaryVerifyAfter='NotRun_NoPreparationReceipt',independentAfterPreservation='Passed',newRootsStillAbsent=list(map(str,[P,O,S,C])),newRootIdentifiersConsumed=True,compilerCompilations=0,unityEditorAndPlayer='NotRun',noRetry=True,R03Accepted=False,H2Passed=False,qualificationApproved=False,ReadyForHumanReviewGate=False,fullLegacyRegressionAcceptance=False,runtimeAcceptance=False,nextState='Primary Implementation')
save('LocalResult-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json',result);print(json.dumps(result,indent=2))
