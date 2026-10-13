from h_common import *
assert load(P/'HOST_RESULT.json')['state']=='Passed' and load(P/'SOURCE_PRESERVATION_BEFORE.json')['state']=='Passed'
assert load(P/'scoped-custody-before.json')['result']=='ScopedHistoricalLossStable' and load(P/'retained-e-before.json')['result']=='PassedPreservationOnly' and load(P/'FG_SDK_PRESERVATION_BEFORE.json')['state']=='PassedPreservationOnly'
clean_sources();no_unity();M=B/'ManagedAPI-R03N-after-M-6f28';N=B/'NativeSDK-R03N-after-M-6f28';S=B/'Scratch-R03N-after-M-6f28';assert not M.exists() and not N.exists() and not S.exists()
managed=command('managed-api',[PY,'-B',D/'Tools/AssemblyShadow/R03/build_api.py','--workspace',W,'--unity',UNITY,'--output',M],timeout=1800)
if managed['exitCode']!=0:
 save(P/'COMPILER_INVOCATIONS.json',{'recordedUtc':now(),'managed':managed,'native':'NotRun after managed prerequisite failure','managedInvocations':1,'nativeInvocations':0,'UnityLaunches':0,'Players':0});sys.exit(managed['exitCode'])
clean_sources();no_unity()
native=command('native-sdk',[PY,'-B',D/'Tools/AssemblyShadow/R03/native_validation.py','--workspace',W,'--unity',UNITY,'--output',N,'--sdk-scratch',S],timeout=1800)
save(P/'COMPILER_INVOCATIONS.json',{'recordedUtc':now(),'managed':managed,'native':native,'managedInvocations':1,'nativeInvocations':1,'runtimeForbiddenUnlessBothPass':True,'UnityLaunches':0,'Players':0})
