#!/usr/bin/env python3
"""Read-only original S transport audit. This is not runtime or independent-agent approval."""
import argparse, collections, hashlib, json, pathlib, re, subprocess, tarfile
PUBLICATION='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b'
CHECKPOINT='Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready'
LIVE='/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/'
PINS=dict(hybridclr_demo='29bb3d4a39bf8a2f23be404f77535aaba3485bfc',hybridclr='4b2774b066cfc6afd77a8c8aded6bda7ea574f55',hybridclr_unity='948c0e3b4f8891481301770115e8ba4945eea6de',il2cpp_plus='1cf87f8209790f9fb2ebec97487dc1990ccd56c5')
CACHE={}
def require(v,m):
    if not v:raise ValueError(m)
def safe(root,rel):
    p=pathlib.PurePosixPath(rel)
    require(not p.is_absolute() and '..' not in p.parts and str(p)==rel,'Noncanonical path '+rel)
    out=root.joinpath(*p.parts)
    for q in [out,*out.parents]:
        require(not q.is_symlink(),'Symlink '+str(q))
        if q==root:break
    return out
def sha(p):
    st=p.stat();key=(str(p),st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    if key not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
        CACHE[key]=h.hexdigest()
    return CACHE[key]
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args])
def load(p):
    def unique(rows):
        d={}
        for k,v in rows:require(k not in d,'Duplicate JSON key '+k);d[k]=v
        return d
    return json.loads(p.read_text(),object_pairs_hook=unique)
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def audit(ws,out):
    demo=ws/'hybridclr_demo';root=demo/CHECKPOINT
    require(git(demo,'rev-parse','HEAD').decode().strip()==PUBLICATION,'Exact S publication')
    before=git(demo,'status','--porcelain=v1','--untracked-files=all');require(not before,'Clean input')
    out.mkdir(parents=True,exist_ok=False);actual={}
    for entry in git(demo,'ls-tree','-rz','HEAD',CHECKPOINT).split(b'\0'):
        if not entry:continue
        meta,path=entry.split(b'\t',1);mode,kind,oid=meta.decode().split();rel=path.decode()[len(CHECKPOINT)+1:];p=safe(root,rel)
        require(mode in ('100644','100755') and kind=='blob' and p.is_file(),'Regular Git file '+rel)
        h=hashlib.sha1();h.update(('blob %d\0'%p.stat().st_size).encode())
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
        require(h.hexdigest()==oid,'Git object '+rel);actual[rel]=sha(p)
    manifest={}
    for line in (root/'MANIFEST.sha256').read_text().splitlines():
        h,p=line.split('  ',1);require(p not in manifest and re.fullmatch('[a-f0-9]{64}',h),'Unique manifest')
        require(actual.get(p)==h,'Manifest bytes '+p);manifest[p]=h
    require(set(actual)==set(manifest)|{'MANIFEST.sha256'},'Complete checkpoint manifest')
    transport=load(root/'FILE_TRANSPORT.json');reconstructed={};parts=[]
    for item in transport['files']:
        rel=item['originalPath'];require(rel not in reconstructed,'Duplicate original')
        target=safe(out/'originals',rel);target.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();total=0;seen=set()
        with target.open('xb') as dst:
            for part in item['parts']:
                p=safe(root,part['path']);require(part['path'] not in seen,'Duplicate part');seen.add(part['path'])
                require(p.stat().st_size==part['size'] and sha(p)==part['sha256'],'Part bytes '+part['path'])
                with p.open('rb') as src:
                    for b in iter(lambda:src.read(1048576),b''):h.update(b);dst.write(b);total+=len(b)
        require(total==item['originalSize'] and h.hexdigest()==item['originalSha256'],'Concatenation '+rel)
        reconstructed[rel]=target;parts.append(dict(path=rel,sha256=h.hexdigest(),bytes=total,parts=item['parts']))
    def rp(rel):return reconstructed.get('batch/'+rel,safe(root,'batch/'+rel))
    index=load(root/'batch/evidence-index.json');seal=load(root/'batch/seal-receipt.json')
    require(sha(rp('evidence-index.json'))==seal['indexSha256'] and sha(rp('evidence.tar.gz'))==seal['archiveSha256'],'Seal identities')
    indexed={}
    for row in index['files']:
        rel=row['path'];require(rel not in indexed,'Duplicate indexed path');indexed[rel]=row;p=rp(rel)
        require(p.is_file() and p.stat().st_size==row['size'] and sha(p)==row['sha256'],'Indexed bytes '+rel)
    expected=dict(indexed);expected['evidence-index.json']=dict(path='evidence-index.json',size=rp('evidence-index.json').stat().st_size,sha256=seal['indexSha256'])
    members=[];seen=set()
    with tarfile.open(rp('evidence.tar.gz'),'r|gz') as stream:
        for m in stream:
            require(m.name not in seen and m.name in expected and m.isfile(),'Archive member '+m.name);seen.add(m.name)
            row=expected[m.name];require(m.size==row['size'],'Member size');h=hashlib.sha256();f=stream.extractfile(m)
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
            require(h.hexdigest()==row['sha256'],'Member digest '+m.name);members.append(dict(path=m.name,bytes=m.size,sha256=h.hexdigest()))
    require(seen==set(expected) and len(seen)==seal['members'],'Exact archive set')
    ledger=load(rp('BATCH_EXECUTION.json'));final=load(rp('LOCAL_BATCH_RESULT.json'))
    require(final['executionLedgerSha256']==sha(rp('BATCH_EXECUTION.json')),'Ledger binding')
    require(final['seal']==seal and final['sealStatus']=='Passed','Final seal binding')
    require(all(final[k]==v for k,v in ledger.items()),'All original ledger fields preserved')
    require(final['result']=='EvidenceReadyForPrimaryReview' and not final['R03Accepted'] and not final['H2Passed'],'Historical result, not acceptance')
    for k,v in PINS.items():require(final['repositories'][k]==v,'Executed source '+k)
    plan=load(root/'batch/completion-plan.json');cells=final['cells'];done=set();joins=[]
    require(len(cells)==90 and len({c['id'] for c in cells})==90 and [c['id'] for c in cells]==plan['cells'],'Exact ninety-cell plan')
    for c in cells:
        require(c['result']=='Passed' and all(d in done for d in c['dependencies']),'Dependency '+c['id'])
        cp=root/('batch/cells/'+c['id']+'.json');require(load(cp)==c,'Cell/ledger equality '+c['id']);done.add(c['id']);e=c.get('evidence',{})
        joins.append(dict(id=c['id'],cellSha256=sha(cp),dependencies=c['dependencies'],result=c['result'],evidenceKeys=sorted(e),sourceBinding=e.get('nativeBinding',{}).get('repositories',final['repositories']),buildReceiptSha256=e.get('buildReceiptSha256',e.get('sha256')),launchPid=e.get('launchPid')))
    processes=[];pids=set();excluded={};byhash=collections.defaultdict(list)
    for row in indexed.values():byhash[row['sha256']].append(row['path'])
    for p in sorted((root/'batch').rglob('verification.json')):
        if not any(x in p.parts for x in ('players','resource-players','measurements','early')):continue
        v=load(p)
        if 'launchPid' not in v:continue
        pid=v['launchPid'];require(isinstance(pid,int) and pid>0 and pid not in pids,'Distinct process');pids.add(pid)
        rel=p.relative_to(root/'batch').as_posix();require(rel in indexed and v['result']=='Passed','Indexed process result')
        raw=v.get('rawPath',str(p.parent/'raw.json'));rawp=rp(raw[len(LIVE):]) if raw.startswith(LIVE) else pathlib.Path(raw)
        require(rawp.is_file() and sha(rawp)==v['rawSha256'],'Raw process binding '+rel)
        if 'requestSha256' in v:require(sha(p.parent/'request.json')==v['requestSha256'],'Request binding '+rel)
        if 'commandReceipt' in v:
            c=v['commandReceipt'];require(c.startswith(LIVE) and sha(rp(c[len(LIVE):]))==v['commandSha256'],'Command binding '+rel)
        verified=0
        for path,h in v.get('sourceInputHashes',{}).items():
            if path.startswith(LIVE):
                relinput=path[len(LIVE):];ip=rp(relinput)
                if ip.is_file():require(sha(ip)==h,'Process source input '+relinput);verified+=1
                else:
                    require('/HybridCLRData/' in relinput or '/Library/' in relinput or '/Temp/' in relinput or relinput.startswith('reference-worktrees/'),'Unexpected missing source '+relinput)
                    old=excluded.get(relinput);require(old is None or old['sha256']==h,'Excluded conflicting identity')
                    excluded[relinput]=dict(sha256=h,indexedByteMatches=byhash.get(h,[]),status='ExcludedLivePathNotReobserved')
        if 'buildReceiptSha256' in v:
            matches=[x for x in indexed.values() if x['sha256']==v['buildReceiptSha256'] and x['path'].endswith('build-receipt.json')]
            require(len(matches)==1,'Exact physical build join '+rel)
        processes.append(dict(path=rel,pid=pid,verificationSha256=sha(p),rawSha256=v['rawSha256'],verifiedLiveInputBindings=verified,recordedSourceInputCount=len(v.get('sourceInputHashes',{})),buildReceiptSha256=v.get('buildReceiptSha256')))
    require(len(processes)==59,'All fifty-nine processes: '+str(len(processes)))
    bindings=load(root/'SOURCE_BINDINGS.json');require(bindings['repositories']==PINS,'Snapshot quartet')
    for row in bindings['files']:
        name=pathlib.PurePosixPath(row['repositoryPath']).name;require(row['commit']==PINS[name],'Snapshot source pin')
        b=git(ws/name,'show',row['commit']+':'+row['path'])
        require(hashlib.sha256(b).hexdigest()==row['sha256']==sha(safe(root,row['snapshot'])),'Snapshot vs Git '+name+'/'+row['path'])
    recovery=load(root/'batch/transaction-recovery/verification.json')
    require(recovery['cleanupResult']=='ExactOriginalBytesRestored' and recovery['remoteAuthority']=='Passed' and recovery['stage']=='Complete','P05 independent restoration/authority')
    require(recovery['originalSettingsSha256']==recovery['afterSettingsSha256'],'P05 bytes')
    integration=load(root/'batch/cells/production-entry-integration.json')['evidence'];ir=rp(integration['path'][len(LIVE):])
    require(sha(ir)==integration['sha256'],'Integration raw identity');iv=load(ir)
    require(iv['returnChangedRoots']==[] and iv['returnClosure']==[],'Separate restored-generation proof')
    require(git(demo,'status','--porcelain=v1','--untracked-files=all')==before,'Input checkout unchanged')
    put(out/'members.json',members);put(out/'cell-provenance.json',joins);put(out/'process-provenance.json',processes);put(out/'excluded-live-inputs.json',excluded)
    report=dict(kind='IRR03OriginalSProvenanceAudit',result='Passed',inputCommit=PUBLICATION,executedPins=PINS,checkpoint=CHECKPOINT,gitFilesVerified=len(actual),manifestFilesVerified=len(manifest),transport=parts,seal=seal,indexedFiles=len(indexed),archiveMembers=len(members),cells=len(cells),processes=len(processes),sourceSnapshotBindings=len(bindings['files']),excludedLiveInputCount=len(excluded),p05=recovery,integration=dict(path=integration['path'],sha256=integration['sha256'],returnChangedRoots=[],returnClosure=[]),auditScriptSha256=sha(pathlib.Path(__file__).resolve()),originalArtifacts={n:dict(sha256=sha(rp(n)),bytes=rp(n).stat().st_size) for n in ('BATCH_EXECUTION.json','LOCAL_BATCH_RESULT.json','evidence-index.json','evidence.tar.gz','seal-receipt.json')},artifacts={p.name:sha(p) for p in sorted(out.glob('*.json'))},priorFivePartFamily='Withdrawn: not the committed S checkpoint; no authenticated transformation asserted',unityRun=False,playerRun=False,independentAgentReview=False,runtimeAcceptance=False)
    put(out/'audit.json',report);print(json.dumps({k:report[k] for k in ('result','gitFilesVerified','indexedFiles','archiveMembers','cells','processes','sourceSnapshotBindings','excludedLiveInputCount')}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();audit(a.workspace.resolve(),a.output.resolve())
