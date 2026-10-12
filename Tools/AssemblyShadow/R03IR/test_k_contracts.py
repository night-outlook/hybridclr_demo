"""K additional strict evidence contracts; no mocked runtime pass claims."""
import copy,unittest
from run_terminal_local import verify_engine
from bee_observation import expected_errors,verify_observation
from batch_contract import ContractError

class EngineContracts(unittest.TestCase):
    def setUp(self):
        self.request={'runId':'a'*32,'caseId':'engine','stimulus':'engine-unhandled'}
        self.launch={'pid':321}
        self.raw={'schemaVersion':1,'kind':'R03IREngineReportingV1','runtimeAcceptance':False,
            'result':'ObservedNotAccepted','runId':'a'*32,'caseId':'engine','processId':321,
            'timedOut':False,'initialState':6,'finalState':9,'preManagedLoggerCalls':1,
            'finalManagedLoggerCalls':1,'completedReports':1,'observationMilliseconds':500,
            'recovery':{'published':True,'stateCode':9,'terminalFailureCode':13,'disposition':'RestartRequired'}}
        self.log='[R03ReserveGcProbe] mask=31 collectionsBefore=0 collectionsAfter=1\n[AssemblyShadowTerminalReport] sequence=1 state=9 message="R03_ENGINE_UNHANDLED_'+('a'*32)+'" managedHandlerExecuted=false\n'
    def check(self):return verify_engine(self.raw,self.request,self.launch,self.log)
    def test_positive_shape(self):self.assertEqual(self.check()['result'],'Passed')
    def test_reject_direct_probe_without_sentinel(self):
        self.log=self.log.replace('R03_ENGINE_UNHANDLED_', 'synthetic-direct-')
        with self.assertRaises(ContractError):self.check()
    def test_reject_managed_handler_execution(self):
        self.raw['finalManagedLoggerCalls']=2
        with self.assertRaises(ContractError):self.check()
    def test_reject_wrong_process(self):
        self.raw['processId']+=1
        with self.assertRaises(ContractError):self.check()
    def test_reject_missing_gc_proof(self):
        self.log=self.log.replace('mask=31','mask=27')
        with self.assertRaises(ContractError):self.check()
    def test_reject_fatal(self):
        self.log+='fatal=FixedBooleanReserveUnavailable'
        with self.assertRaises(ContractError):self.check()
    def test_reject_boolean_counts_and_bad_recovery(self):
        for key,value in [('completedReports',True),('initialState',True),('timedOut',True)]:
            original=self.raw[key];self.raw[key]=value
            with self.assertRaises(ContractError):self.check()
            self.raw[key]=original
        self.raw['recovery']['terminalFailureCode']=21
        with self.assertRaises(ContractError):self.check()

class BeeReceiptOutcomeContracts(unittest.TestCase):
    def test_build_receipt_uses_actual_observation_result(self):
        from pathlib import Path
        source=(Path(__file__).resolve().parents[1]/'R03/PlayerProject/R03Build.cs').read_text()
        self.assertIn('public string Outcome { get { return data.result; } }',source)
        self.assertIn('receipt.beeObservationStatus = observation.Outcome;',source)
        self.assertNotIn('receipt.beeObservationStatus = "RecordedForAnalysis";',source)
        # A diagnostic being absent never changes strict Unity BuildReport gating.
        self.assertIn('report.summary.totalErrors != 0',source)
        self.assertIn('throw new BuildFailedException("Actual IL2CPP Player build did not succeed.")',source)


class BeeContracts(unittest.TestCase):
    def test_exit_zero_can_still_report_error(self):
        rows=[{'exitCode':0,'outputFile':'test.o','output':'warning: other\nerror: failed to allocate space to load shared cache file at %s'}]
        self.assertEqual(expected_errors(rows),['test.o: failed to allocate space to load shared cache file at %s'])
    def test_prefix_semantics_no_false_positive(self):
        self.assertEqual(expected_errors([{'exitCode':0,'output':'source says error: x\n error: y'}]),[])
    def test_capture_not_build_acceptance(self):
        raw={'schemaVersion':1,'kind':'R03BeeResultObservationV1','runtimeAcceptance':False,
             'sourceManifestSha256':'a','result':'CapturedForAnalysis','sameProcessor':True,
             'driverInitiallyAbsent':True,'limitsExceeded':False,'buildErrors':2,
             'nodes':[{'exitCode':0,'output':''}],'messages':[]}
        self.assertFalse(verify_observation(raw,'a')['buildAcceptanceChanged'])
        for field in ['sameProcessor','driverInitiallyAbsent']:
            change=copy.deepcopy(raw);change[field]=False
            with self.assertRaises(ContractError):verify_observation(change,'a')
        raw['limitsExceeded']=True
        with self.assertRaises(ContractError):verify_observation(raw,'a')
if __name__=='__main__':unittest.main()
