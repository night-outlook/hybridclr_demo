"""Run bounded Primary regressions with exact test IDs and immutable output.

This does not launch Unity, mutate project pins, accept old builds, or approve
M08. Apple graph tests authenticate the recorded failure fixture; real compiler
probes use tiny host-Clang fixtures and remain distinct from Apple execution.
"""
from __future__ import annotations
import argparse
from collections import Counter
import contextlib
import hashlib
import json
from pathlib import Path
import platform
import sys
import unittest

MODULES = (
    'test_h1_bee_macro_domains', 'test_h1_bee_domain_probes',
    'test_h1_capture_attempt', 'test_h1_capture_volume',
    'test_h1_macro_domain_census', 'test_h1_failure_bundle_census',
    'test_h1_plan_failure_retention', 'test_h1_compiler_actions', 'test_h1_native_capture',
    'test_h1_pch_provenance', 'test_h1_pch_integration', 'test_h1_count_build_batch',
    'test_h1_handoff_preflight', 'test_h1_selection_collect', 'test_h1_successor_evidence',
    'test_h1_successor_sidecar',
)


def run(output):
    output=Path(output)
    if not output.is_absolute() or output!=output.resolve() or output.exists():
        raise ValueError('New canonical output directory required')
    output.mkdir(parents=True)
    sys.path.insert(0,str(Path(__file__).resolve().parent/'tests'))
    suite=unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    class Result(unittest.TextTestResult):
        def __init__(self,*args,**kw):super().__init__(*args,**kw);self.rows=[];self.subfailed=set()
        def addSuccess(self,t):super().addSuccess(t);self.rows.append({'id':t.id(),'result':'Passed'})
        def addFailure(self,t,e):
            super().addFailure(t,e);self.rows.append({'id':t.id(),'result':'Failed','detail':self._exc_info_to_string(e,t)})
        def addError(self,t,e):
            super().addError(t,e);self.rows.append({'id':t.id(),'result':'Error','detail':self._exc_info_to_string(e,t)})
        def addSkip(self,t,r):super().addSkip(t,r);self.rows.append({'id':t.id(),'result':'Skipped','reason':r})
        def addSubTest(self,t,st,e):
            super().addSubTest(t,st,e)
            if e:self.subfailed.add(t.id())
        def stopTest(self,t):
            if t.id() in self.subfailed and not any(x['id']==t.id() for x in self.rows):
                self.rows.append({'id':t.id(),'result':'FailedSubtest'})
            super().stopTest(t)
    log=output/'tests.log'
    with log.open('x') as stream,contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    counts=dict(Counter(r['result'] for r in result.rows))
    passed=result.wasSuccessful() and not result.skipped and result.testsRun>0
    report={'kind':'H1BeePrimaryRegression','status':'PassedBoundedTests' if passed else 'CompletedWithNonPass',
        'testCount':result.testsRun,'counts':counts,'tests':sorted(result.rows,key=lambda r:r['id']),
        'host':platform.platform(),'python':sys.version,'rawLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),
        'scope':'Pinned Apple graph planning, >256 MiB logical retention, fail-closed storage limits, and host-Clang synthetic probes; not Unity/Apple Player validation',
        'UnityCompile':'NotRun','AppleClangExecution':'NotRun','M08':'NotRun','humanGatePassed':False,'mayEnterR02':False}
    (output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    summary={k:report[k] for k in ('status','testCount','counts')}
    summary['nonpasses']=[{k:v for k,v in row.items() if k in ('id','result','detail','reason')} for row in report['tests'] if row['result']!='Passed']
    print(json.dumps(summary))
    return 0 if passed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().output))
