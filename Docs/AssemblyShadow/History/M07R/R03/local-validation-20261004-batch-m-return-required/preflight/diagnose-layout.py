"""Read immutable CLI metadata; no compilation, dnlib execution or layout approval."""
import pathlib,json,hashlib,sys,subprocess,datetime,shutil,re
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261004M-policy';R=P.parent/'R03LocalBatch-20261004M-policy';sys.path.insert(0,str(D/'Tools/AssemblyShadow'))
import m04_metadata as md
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
class Metadata:
 def __init__(self,path):
  self.path=path;self.identity=md.read_identity(path);s=md._metadata(path.read_bytes(),str(path));self.streams=s;t=md.Reader(s.get('#~',s.get('#-')),str(path));self.t=t;hs=t.number(6,1);valid=t.number(8,8);rows=[0]*45;cursor=24
  for n in range(45):
   if valid&(1<<n):rows[n]=t.number(cursor,4);cursor+=4
  self.rows=rows;self.offset={};self.width={}
  def width(c):
   if isinstance(c,int):return 4 if rows[c]>=65536 else 2
   if c in ('u2','u4'):return int(c[1:])
   if c in 'sbg':return 4 if hs&{'s':1,'g':2,'b':4}[c] else 2
   bits,tables=md.CODED[c];return 4 if max(rows[i] for i in tables)>=1<<(16-bits) else 2
  for n,schema in enumerate(md.TABLES):self.offset[n]=cursor;self.width[n]=[width(c) for c in schema];size=rows[n]*sum(self.width[n]);t.block(cursor,size);cursor+=size
  self.nested={self.row(41,i)[0]:self.row(41,i)[1] for i in range(1,rows[41]+1)}
 def row(self,table,i):
  assert 1<=i<=self.rows[table];p=self.offset[table]+(i-1)*sum(self.width[table]);v=[]
  for w in self.width[table]:v.append(self.t.number(p,w));p+=w
  return v
 def string(self,i):
  h=self.streams['#Strings'];assert 0<=i<len(h);end=h.index(b'\0',i);return h[i:end].decode()
 def compressed(self,b,p):
  a=b[p]
  if a<128:return a,p+1
  if a<192:return ((a&63)<<8)|b[p+1],p+2
  assert a<224;return ((a&31)<<24)|int.from_bytes(b[p+1:p+4],'big'),p+4
 def blob(self,i):
  h=self.streams['#Blob'];n,p=self.compressed(h,i);assert p+n<=len(h);return h[p:p+n]
 def defname(self,i):
  r=self.row(2,i);name=self.string(r[1]);ns=self.string(r[2]);parent=self.nested.get(i)
  if parent:return self.defname(parent)+'/'+name
  return ns+'.'+name if ns else name
 def ref(self,i,depth=0):
  assert depth<128;r=self.row(1,i);tag=r[0]&3;rid=r[0]>>2;name=self.string(r[1]);ns=self.string(r[2])
  if tag==2:scope=self.string(self.row(35,rid)[6])
  elif tag==3:
   p=self.ref(rid,depth+1);return {'assembly':p['assembly'],'type':p['type']+'/'+name}
  else:scope=self.identity['name']
  return {'assembly':scope,'type':ns+'.'+name if ns else name}
 def typedefref(self,c):
  tag=c&3;rid=c>>2
  if c==0:return {'assembly':'','type':'<none>'}
  if tag==1:return self.ref(rid)
  if tag==0:return {'assembly':self.identity['name'],'type':self.defname(rid)}
  assert tag==2;return {'spec':self.blob(self.row(27,rid)[0]).hex()}
 def leading_field_type(self,blob):
  assert blob[0]==6;p=1;et=blob[p];p+=1;value={'elementType':et,'signatureHex':blob.hex()}
  if et in (0x11,0x12):c,p=self.compressed(blob,p);value['declaredType']=self.typedefref(c)
  elif et==0x15:
   value['genericKind']=blob[p];p+=1;c,p=self.compressed(blob,p);value['genericDefinition']=self.typedefref(c)
  return value
 def types(self):
  result={}
  for i in range(1,self.rows[2]+1):
   row=self.row(2,i);end=self.row(2,i+1)[4] if i<self.rows[2] else self.rows[4]+1;fields={}
   for n in range(row[4],end):
    flags,name,sig=self.row(4,n)
    if not flags&16:fields[self.string(name)]=self.leading_field_type(self.blob(sig))
   result[self.defname(i)]={'base':self.typedefref(row[3]),'instanceFields':fields}
  return result
cfg=load(R/'resource-project.json');run=pathlib.Path(cfg['runPath']);state=load(run/'p05-define-state.json');manifest=pathlib.Path(state['baselinePath']);baseline=manifest.parent/'PlayerInputs';target=run/'P05-compile/Snapshot';br=load(baseline/'assembly-snapshot.json');tr=load(target/'assembly-snapshot.json')
brec=next(f for f in br['linkedPlayerReceipt']['assemblies'] if f['name']=='assemblya.implementation.internal');trec=next(f for f in tr['assemblies'] if f['name']=='AssemblyA.Implementation.Internal');b=baseline/'LinkedPlayer'/brec['path'];t=target/trec['path'];assert sha(b)==brec['sha256'] and sha(t)==trec['sha256'];bm=Metadata(b);tm=Metadata(t);bt=bm.types();tt=tm.types();bases=[];fields=[]
for name in sorted(set(bt)&set(tt)):
 before,after=bt[name],tt[name]
 if before['base']!=after['base']:bases.append({'type':name,'linkedBaseline':before['base'],'compilerTarget':after['base'],'sameQualifiedTypeName':before['base'].get('type')==after['base'].get('type')})
 for field in sorted(set(before['instanceFields'])&set(after['instanceFields'])):
  x,y=before['instanceFields'][field],after['instanceFields'][field]
  # Report only declared scope/type changes, not token-number-only differences.
  if x.get('declaredType')!=y.get('declaredType') or x.get('genericDefinition')!=y.get('genericDefinition'):fields.append({'type':name,'field':field,'linkedBaseline':x,'compilerTarget':y})
assert any(r['type']=='AssemblyA.Implementation.Internal.InternalEntry' and r['linkedBaseline']=={'assembly':'mscorlib','type':'System.Object'} and r['compilerTarget']=={'assembly':'netstandard','type':'System.Object'} for r in bases)
assert any(r['type']=='AssemblyA.Implementation.Internal.M06ExecutionWitness/M06InternalNode' and r['field']=='Changed' and r['linkedBaseline']['declaredType']['assembly']=='mscorlib' and r['compilerTarget']['declaredType']['assembly']=='netstandard' for r in fields)
dest=P/'layout-inputs';dest.mkdir(exist_ok=False);shutil.copytree(baseline,dest/'baseline-PlayerInputs');shutil.copy2(manifest,dest/'baseline-manifest.json');copies=[]
for src in [target/'assembly-snapshot.json',t,run/'p05-compile-receipt.json',run/'p05-define-state.json',run/'p05-restored.json',run/'p05-settings-restored.json',run/'p05-project-settings.original',run/'p05-unity-restored.bytes']:
 out=dest/'target-and-state'/src.relative_to(run);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);copies.append({'path':str(src),'sha256':sha(src),'snapshot':str(out)})
report={'kind':'ReadOnlyMNativeLayoutInputDiagnosis','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','interpretation':'Metadata diagnosis only, not dnlib/native layout verification or forwarder equivalence approval. Original structural compile remains Failed.','baselineManifest':{'path':str(manifest),'sha256':sha(manifest)},'baselineSnapshot':{'path':str(baseline/'assembly-snapshot.json'),'sha256':sha(baseline/'assembly-snapshot.json'),'snapshotHash':br['snapshotHash'],'buildGuid':br['buildGuid'],'nativeLibrarySha256':br['nativeLibrarySha256']},'targetSnapshot':{'path':str(target/'assembly-snapshot.json'),'sha256':sha(target/'assembly-snapshot.json'),'snapshotHash':tr['snapshotHash']},'linkedBaselineDll':{'path':str(b),'sha256':sha(b),'identity':bm.identity},'targetDll':{'path':str(t),'sha256':sha(t),'identity':tm.identity},'rawDeclaredBaseDifferences':bases,'declaredFieldScopeDifferences':fields,'copies':copies,'baselineSnapshotCopy':str(dest/'baseline-PlayerInputs'),'scopeLimit':'No type-forwarder chain resolver, native allocation/offset check, signature bypass, source fix or new compiler invocation. Representative scope mismatch is independently observed; complete compatibility remains unproven.','R03Accepted':False,'H2Passed':False}
(P/'NATIVE_LAYOUT_DIAGNOSIS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'Passed','baseDifferences':len(bases),'declaredFieldScopeDifferences':len(fields),'baseline':sha(b),'target':sha(t)}))
