import hashlib,json,pathlib,shutil,subprocess
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005N-identity');P=R.parent/'Preflight-R03LocalBatch-20261005N-identity';C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261005-batch-n-'+('evidence-ready' if json.loads((R/'LOCAL_BATCH_RESULT.json').read_text())['result']=='EvidenceReadyForPrimaryReview' else 'return-required'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert subprocess.check_output(['git','-C',str(D),'status','--short'],text=True)=='';C.mkdir(exist_ok=False)
idx=json.loads((R/'evidence-index.json').read_text());hashes=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes']
for name in [f['path'] for f in idx['files']]+['LOCAL_BATCH_RESULT.json','evidence-index.json','seal-receipt.json']:
 dest=C/'batch'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,dest)
parts=C/'batch/evidence.tar.gz.parts';parts.mkdir();partRecords=[]
with (R/'evidence.tar.gz').open('rb') as f:
 number=0
 while data:=f.read(64*1024*1024):
  p=parts/('part-%03d'%number);p.write_bytes(data);partRecords.append({'path':str(p.relative_to(C)),'size':len(data),'sha256':sha(p)});number+=1
combined=hashlib.sha256()
for part in partRecords:
 with (C/part['path']).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):combined.update(b)
assert combined.hexdigest()==hashes['evidence.tar.gz']
(C/'ARCHIVE_TRANSPORT.json').write_text(json.dumps({'kind':'BytePreservingArchiveTransport','reason':'Sealed archive split into exact ordered byte parts for Git publication only; original live bytes and seal remain unchanged','originalLivePath':str(R/'evidence.tar.gz'),'originalSha256':hashes['evidence.tar.gz'],'originalSize':(R/'evidence.tar.gz').stat().st_size,'partSizeLimit':64*1024*1024,'parts':partRecords,'concatenationSha256Verified':True,'originalSealUnchanged':True},indent=2)+'\n')
(C/'REASSEMBLE_EVIDENCE.py').write_text('''"""Reconstruct the exact sealed archive at a new, caller-specified path."""
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
manifest=json.loads((root/'ARCHIVE_TRANSPORT.json').read_text())
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/evidence.tar.gz')
target=pathlib.Path(sys.argv[1]);assert target.is_absolute() and not target.exists()
whole=hashlib.sha256();size=0
with target.open('xb') as output:
 for part in manifest['parts']:
  h=hashlib.sha256();n=0
  with (root/part['path']).open('rb') as source:
   for block in iter(lambda:source.read(1048576),b''):
    h.update(block);whole.update(block);output.write(block);n+=len(block)
  assert h.hexdigest()==part['sha256'] and n==part['size'];size+=n
assert whole.hexdigest()==manifest['originalSha256'] and size==manifest['originalSize']
print('Authenticated archive:',target,whole.hexdigest(),size)
''')
shutil.copytree(P,C/'preflight')
for name in ['Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/build_provenance.py','Tools/AssemblyShadow/R03/editor_scope.py','Tools/AssemblyShadow/R03/batch_contract.py','Tools/AssemblyShadow/R03/runtime_contract.py','Tools/AssemblyShadow/R03/test_producer_control.py','Tools/AssemblyShadow/R03/rejection_contract.py','Tools/AssemblyShadow/R03/test_rejection_contract.py','Tools/AssemblyShadow/R03/PlayerProject/R03Player.cs','Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp','Tools/AssemblyShadow/R03/input_validation.py','Tools/AssemblyShadow/R03/unity_command.py','Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md','Tools/AssemblyShadow/R02/ordinary_input.py','Tools/AssemblyShadow/R02/export_m00_fixture.py','Tools/AssemblyShadow/R02/evidence.py','Tools/AssemblyShadow/R02/fixtures/m00-frozen.dll.zlib.base64.txt','Tools/AssemblyShadow/R02/fixtures/m00-origin.json','Tools/AssemblyShadow/m04_metadata.py','Tools/AssemblyShadow/h1_witness_contract.py']:
 dest=C/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/name,dest)
for src in (D/'Tools/AssemblyShadow/R03Completion').rglob('*'):
 if src.is_file() and '__pycache__' not in src.parts:
  dest=C/'source-snapshot'/src.relative_to(D);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

src=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity/Tests/Editor/AssemblyShadow/ResourceAbiTests.cs');dest=C/'source-snapshot/hybridclr_unity/Tests/Editor/AssemblyShadow/ResourceAbiTests.cs';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

for name in ['Assets/AssemblyShadowDemo/Editor/M02Build.cs','Assets/AssemblyShadowDemo/Editor/M07Build.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionBuild.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionSourcePinContract.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionSourcePinContract.cs.meta','Assets/AssemblyShadowDemo/Editor/R03CompletionInventoryContract.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionInventoryContract.cs.meta','Assets/AssemblyShadowDemo/Editor/R03ResourceCapabilityProfile.cs','Assets/AssemblyShadowDemo/Editor/R03ResourceCapabilityProfile.cs.meta','Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs','Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs.meta','Assets/AssemblyShadowDemo/Editor/R03CompletionFixedImageContract.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionFixedImageContract.cs.meta']:
 dest=C/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/name,dest)
for name in ['Tests/Editor/AssemblyShadow/SyntheticCompiledAssemblySet.cs','Tests/Editor/AssemblyShadow/SyntheticCompiledAssemblySet.cs.meta','Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs','Tests/Editor/AssemblyShadow/PolicyTests.cs','Editor/AssemblyShadow/Metadata/CompiledAssemblySet.cs','Editor/AssemblyShadow/Metadata/PureInterpreterEligibility.cs']:
 src=D.parent/'hybridclr_unity'/name;dest=C/'source-snapshot/hybridclr_unity'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

(C/'.gitattributes').write_text('# Preserve immutable sealed bytes, including generated native whitespace.\n*.dll binary\n*.dylib binary\nbatch/evidence.tar.gz.parts/* binary\nbatch/** -whitespace\n')
print('Raw checkpoint created',C,'archive parts',len(partRecords))

# Batch-N input/consumer contracts are captured from the exact executed source.
for name in ['Assets/AssemblyShadowDemo/Editor/R03CompilerPolicyChecks.cs','Assets/AssemblyShadowDemo/Editor/R03CompilerPolicyChecks.cs.meta','Assets/AssemblyShadowDemo/Editor/R03CompletionCompilerPolicyContract.cs','Assets/AssemblyShadowDemo/Editor/R03CompletionCompilerPolicyContract.cs.meta','Assets/AssemblyShadowDemo/Bootstrap/R03CompletionExecution.cs','Assets/AssemblyShadowDemo/Bootstrap/M05BoundTypeQueries.cs','ProjectSettings/AssemblyShadowRawTypeAdmissions.json','ProjectSettings/AssemblyShadowDependencies.json','ProjectSettings/AssemblyShadowExtensibilityWhitelist.json','ProjectSettings/AssemblyShadowReflectionBindings.json','ProjectSettings/AssemblyShadowResources.json','ProjectSettings/AssemblyShadowResourcesM07.json']:
 src=D/name;data=subprocess.check_output(['git','-C',str(D),'show','15f6c2c9a5e070e631fdcda9a2bb022f4b61a733:'+name]);assert data==src.read_bytes();dest=C/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

# Authenticated package identity factory/resolver/signature implementation at the executed pin.
for name in ['Editor/AssemblyShadow/Build/NativeLayoutAdmissionSnapshot.cs','Editor/AssemblyShadow/Metadata/EvolutionSignature.cs','Editor/AssemblyShadow/Metadata/NativeLayoutAdmissionValidator.cs','Editor/AssemblyShadow/Metadata/NativeLayoutIdentityContext.cs','Editor/AssemblyShadow/Metadata/NativeLayoutIdentityContext.cs.meta']:
 src=D.parent/'hybridclr_unity'/name;data=subprocess.check_output(['git','-C',str(D.parent/'hybridclr_unity'),'show','ef6c70f30248c4b7c41e9e85d81e08f5709dc4ba:'+name]);assert data==src.read_bytes();dest=C/'source-snapshot/hybridclr_unity'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
