from h_common import *
phase=sys.argv[1];assert phase in ['before','after']
if phase=='before':assert load(P/'SNAPSHOT_HOST_GATES.json')['state']=='Passed';assert load(P/'HOST_RESULT.json')['state']=='Passed';clean_sources();no_unity()
C=hist/'local-validation-20261009-ir-r03-02-c-custody-blocked';c=hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py';r=command('custody-'+phase,[PY,'-B',c,'--checkpoint',C,'--phase',phase,'--receipt',P/('scoped-custody-'+phase+'.json')]);assert r['exitCode']==0
j=load(P/('scoped-custody-'+phase+'.json'));assert j['result']=='ScopedHistoricalLossStable' and j['completeScan'] and j['originalExpectedFiles']==416844 and j['presentVerified']==339367 and j['historicalStillMissing']==77477 and not j['problems']
e=hist/'IR_Remediation/IR_RUNTIME_01_2026-10-10/verify_retained_e.py';args=[PY,'-B',e,'--demo',D,'--phase',phase,'--receipt',P/('retained-e-'+phase+'.json')]
if phase=='after':
 if not (P/'retained-e-before.json').exists() or load(P/'retained-e-before.json')['result']!='PassedPreservationOnly':
  save(P/'RETAINED_E_AFTER_NOTRUN.json',{'state':'NotRun','reason':'Before snapshot did not pass; no invented before/after join'});sys.exit(2)
 args += ['--before',P/'retained-e-before.json']
r=command('retained-e-'+phase,args,timeout=1800);assert r['exitCode']==0 and load(P/('retained-e-'+phase+'.json'))['result']=='PassedPreservationOnly'
r=command('fg-sdk-'+phase,[PY,'-B',P/'preserve.py',phase],timeout=600);assert r['exitCode']==0 and load(P/('FG_SDK_PRESERVATION_'+phase.upper()+'.json'))['state']=='PassedPreservationOnly';print('Independent '+phase+' audits Passed',flush=True)
