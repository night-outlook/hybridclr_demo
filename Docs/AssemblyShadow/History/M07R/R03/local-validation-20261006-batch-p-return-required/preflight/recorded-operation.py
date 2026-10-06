"""Record a Local-owned read-only audit/publication operation, never retry the batch."""
import pathlib,sys,subprocess,datetime,json,hashlib,os
P=pathlib.Path(__file__).resolve().parent
name=sys.argv[1];assert name.endswith('.py') and '/' not in name
script=P/name;assert script.is_file()
root=P/'local-operations';root.mkdir(exist_ok=True)
seq=1
while (root/(script.stem+'-'+str(seq))).exists():seq+=1
folder=root/(script.stem+'-'+str(seq));folder.mkdir()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
command=[sys.executable,'-B',str(script),*sys.argv[2:]]
with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:
 result=subprocess.run(command,cwd='/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo',stdout=out,stderr=err,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'operation':name,'command':command,'startedUtc':start,'endedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':result.returncode,'scriptSha256':sha(script),'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log'),'scope':'Local-owned evidence audit/publication; not a product batch rerun'}
(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'operation':name,'exitCode':result.returncode,'evidence':str(folder)}),flush=True)
for stream in ['stdout.log','stderr.log']:
 print(stream+':\n'+(folder/stream).read_text(errors='replace')[-8000:],flush=True)
sys.exit(result.returncode)
