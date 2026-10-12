from h_common import *
mode=sys.argv[1];assert mode in ['diagnostic','execute'];clean_sources();no_unity()
for f in ['SOURCE_AUTHORITY.json','G_EQUIVALENCE.json','ORIGINAL_INPUT_PREFLIGHT.json','PRIMARY_CI_AUTHENTICATION.json','HOST_RESULT.json']:assert load(P/f)['state']=='Passed'
c=load(P/'scoped-custody-before.json');assert c['result']=='ScopedHistoricalLossStable' and c['completeScan'] and c['presentVerified']==339367 and c['historicalStillMissing']==77477 and not c['problems'];assert load(P/'retained-e-before.json')['result']=='PassedPreservationOnly';assert load(P/'FG_SDK_PRESERVATION_BEFORE.json')['state']=='PassedPreservationOnly';assert not os.path.lexists(H)
if mode=='execute':
 check=B/'StorageCheck-R03IRLocal-I-post-H-custody-7f36';assert load(P/'commands/storage-diagnostic/receipt.json')['exitCode']==0 and load(check/'admission.json')['state']=='Admitted' and not load(check/'dispatch.json')['batchStarted'] and load(check/'session.json')['state']=='Passed'
side=B/('Storage-R03IRLocal-I-post-H-custody-7f36' if mode=='execute' else 'StorageCheck-R03IRLocal-I-post-H-custody-7f36');assert not os.path.lexists(side)
args=[PY,'-B',D/'Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py','--workspace',W,'--output',H,'--unity',UNITY,'--demo-commit',pins['hybridclr_demo'],'--retained-q',B/'R03LocalBatch-20261006Q-lp-repair','--storage-evidence',side]
if mode=='execute':args.append('--execute')
print(json.dumps({'mode':mode,'runtimeRoot':str(H),'sidecar':str(side),'startUtc':now(),'noSourceOrTimeoutOverride':True}),flush=True)
r=command('storage-'+mode,args,timeout=None);sys.exit(r['exitCode'])
