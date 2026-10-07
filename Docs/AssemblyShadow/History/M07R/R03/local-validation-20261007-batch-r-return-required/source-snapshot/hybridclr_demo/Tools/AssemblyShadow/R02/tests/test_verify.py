import copy
import json
import unittest
from evidence import EvidenceError
from verify import COUNTERS, MODES, expected_rows, expected_checksum, marker, verify_raw

START=638945472000000000
NONCE='a'*32

def fixture(role='candidate',mode='R00-ON-P01'):
    identity={'processId':12,'buildGuid':'b'*32,'baselineBuildId':'M07-Baseline-test','runtimeAbiHash':'c'*64,
              'unityVersion':'2022.3.62f2','platform':'OSXPlayer','mode':mode}
    raw=dict(identity,schemaVersion=1,kind='R02PlayerWitness',protocol='R02LocalBatch-v1',result='Passed',error='',runtimeAcceptance=False,
             role=role,runId=NONCE,marker=marker(mode),witnessType='AssemblyA.Implementation.Internal.R02AllocationWitness',
             startedUtcTicks=START,endedUtcTicks=START+10000000,memoryMeasurement='Darwin',memorySemantics='noForcedGC',
             scaleTypeHandles=[str(i+1) for i in range(1000)],rows=[])
    raw['typeInfoCode']='FeatureDisabled' if mode==MODES[0] else 'Success'
    raw['typeInfoJson']=json.dumps({'logicalAssembly':'AssemblyA.Implementation.Internal','isActive':True,
                                 'executionMode':'InterpreterShadow' if mode.endswith(('P01','P03')) else 'AotBaseline'})
    def snapshot(after=False):
        counters={k:0 for k in COUNTERS};counters['admissionCacheHits']=10000 if after else 0
        counters.update(schemaVersion=1,diagnosticsLevel=2,counterCoverage='BoundedComplete',counterSaturated=False,
                        droppedCounterThreads=0,classesCoverage='Truncated',memoryAccountingAvailable=True,
                        memoryAccountingScope='R02StructuresExcludingAllocatorOverhead',counterStorageBytes=128,
                        counterThreadCapacity=128,observationMemoTlsBytesPerThread=64)
        return dict(utcTicks=START+1000,currentRssBytes=100,managedBytes=10,lifetimePeakRssBytes=150,
                    executionCode='FeatureDisabled' if mode==MODES[0] else 'Success',
                    executionJson=json.dumps({'r02':counters} if role=='candidate' and mode!=MODES[0] else {}))
    for op,phase,n,seed in expected_rows(mode):
        value=expected_checksum(n,seed,marker(mode))
        raw['rows'].append(dict(operation=op,phase=phase,iterations=n,seed=seed,checksum=value,expectedChecksum=value,
                               constructorsBefore=0,constructorsAfter=n,elapsedTicks=100,stopwatchFrequency=1000,passed=True,
                               before=snapshot(),after=snapshot(True)))
    raw['parallel']=dict(workerCount=4,iterationsPerWorker=1000,seed=7017,passed=True,joined=[True]*4,
                         threadIds=[1,2,3,4],errors=['']*4,constructorsBefore=0,constructorsAfter=4000,
                         checksums=[expected_checksum(1000,7017+i*1000,marker(mode)) for i in range(4)],
                         elapsedTicks=100,stopwatchFrequency=1000,before=snapshot(),after=snapshot(True))
    r00=dict(identity,il2cpp=True,result='Passed')
    launch=dict(processId=12,exitCode=0,timedOut=False,passed=True,startedAtUnix=START/1e7-62135596800,durationSeconds=2)
    return raw,r00,launch

class RawTests(unittest.TestCase):
    def test_all_role_mode_positive_contracts(self):
        for role in ('candidate','control'):
            for mode in MODES:
                with self.subTest(role=role,mode=mode):
                    raw,r00,launch=fixture(role,mode)
                    result=verify_raw(raw,role,mode,NONCE,r00,launch)
                    self.assertEqual(result['result'],'Passed');self.assertFalse(result['runtimeAcceptance'])
    def reject(self,change):
        raw,r00,launch=fixture();change(raw,r00,launch)
        with self.assertRaises((EvidenceError,KeyError,TypeError,ValueError)):
            verify_raw(raw,'candidate','R00-ON-P01',NONCE,r00,launch)

def mutation(name, fn):
    def test(self):self.reject(fn)
    setattr(RawTests,'test_reject_'+name,test)

for key,value in [('kind','Unknown'),('result','Failed'),('error','error'),('runtimeAcceptance',True),('runId','d'*32),
                  ('role','control'),('marker',3000),('buildGuid','d'*32),('runtimeAbiHash','d'*64),('processId',13),
                  ('unityVersion','2022.3.1'),('witnessType','Other'),('endedUtcTicks',START-1),('memorySemantics','unknown')]:
    mutation(key,lambda r,z,l,k=key,v=value:r.__setitem__(k,v))
mutation('missing_row',lambda r,z,l:r['rows'].pop())
mutation('duplicate_row',lambda r,z,l:r['rows'].__setitem__(1,r['rows'][0]))
mutation('checksum',lambda r,z,l:r['rows'][0].__setitem__('checksum',0))
mutation('constructor_count',lambda r,z,l:r['rows'][0].__setitem__('constructorsAfter',0))
mutation('boolean_iterations',lambda r,z,l:r['rows'][0].__setitem__('iterations',True))
mutation('negative_ticks',lambda r,z,l:r['rows'][0].__setitem__('elapsedTicks',-1))
mutation('zero_frequency',lambda r,z,l:r['rows'][0].__setitem__('stopwatchFrequency',0))
mutation('duplicate_types',lambda r,z,l:r['scaleTypeHandles'].__setitem__(1,'1'))
mutation('worker_failure',lambda r,z,l:r['parallel']['joined'].__setitem__(2,False))
mutation('duplicate_threads',lambda r,z,l:r['parallel']['threadIds'].__setitem__(2,1))
mutation('wrong_thread_checksum',lambda r,z,l:r['parallel']['checksums'].__setitem__(2,0))
mutation('launch_failure',lambda r,z,l:l.__setitem__('exitCode',1))
mutation('launch_timeout',lambda r,z,l:l.__setitem__('timedOut',True))
mutation('outside_launch',lambda r,z,l:l.__setitem__('startedAtUnix',l['startedAtUnix']+100))
mutation('non_il2cpp',lambda r,z,l:z.__setitem__('il2cpp',False))

def diagnostics(r,key,value):
    snap=r['rows'][2]['after'];data=json.loads(snap['executionJson']);data['r02'][key]=value;snap['executionJson']=json.dumps(data)
for key,value in [('schemaVersion',2),('diagnosticsLevel',0),('counterCoverage','Truncated'),('counterSaturated',True),
                  ('droppedCounterThreads',1),('memoryAccountingAvailable',False),('admissionCacheHits',0),
                  ('admissionProofAttempts',1),('definitionRowsScanned',1),('layoutCheckCalls',1),('admissionProofRejections',1)]:
    mutation('diagnostic_'+key,lambda r,z,l,k=key,v=value:diagnostics(r,k,v))
