from h_common import *
assert load(P/'HOST_RESULT.json')['state']=='Passed'
assert load(P/'scoped-custody-before.json')['result']=='ScopedHistoricalLossStable'
assert load(P/'retained-e-before.json')['result']=='PassedPreservationOnly'
assert load(P/'FG_SDK_PRESERVATION_BEFORE.json')['state']=='PassedPreservationOnly'
clean_sources();no_unity()
N=B/'NativeSDK-R03J-reserve-6f02';S=B/'Scratch-R03J-reserve-6f02';O=B/'DebugBee-R03J-reserve-6f02';doc=hist/'IR_Remediation/IR_I_RESPONSE_RESERVE_6f02'
assert not N.exists() and not S.exists() and not O.exists()
r=command('native-sdk',[PY,'-B',D/'Tools/AssemblyShadow/R03/native_validation.py','--workspace',W,'--unity',UNITY,'--output',N,'--sdk-scratch',S],timeout=1800)
save(P/'NATIVE_INVOCATION.json',{'state':'Passed' if r['exitCode']==0 else 'Failed','commandReceipt':r,'invocations':1,'UnityLaunches':0,'linkedBuilds':0,'Players':0})
# Collection is independent of the compiler outcome after shared gate success.
clean_sources();no_unity()
for x in load(P/'J_SOURCE_BINDINGS.json')['currentSources']:assert sha(x['path'])==x['sha256']
r=command('debug-bee-collection',[PY,'-B',doc/'collect_i_debug_cache.py','--demo',D,'--output',O],timeout=600)
save(P/'COLLECTION_INVOCATION.json',{'state':'Passed' if r['exitCode']==0 else 'Failed','commandReceipt':r,'invocations':1,'UnityLaunches':0,'originalI':'FAIL unchanged'})
print('J one native invocation and one read-only collector completed',flush=True)
