"""Record leaf test identities, not just a claimed aggregate pass count.

NUnit input is parsed without executing Unity. Python mode runs the specified
unittest suite and preserves its log. These inventories do not approve H1.
"""
from __future__ import annotations
import argparse
from collections import Counter
import contextlib
import hashlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET


def summarize(rows,kind,input_hash=None):
    ids=[r['id'] for r in rows]
    if not rows or len(ids)!=len(set(ids)):raise ValueError('Empty or duplicate test identity inventory')
    counts=dict(sorted(Counter(r['result'] for r in rows).items()))
    result={'schemaVersion':1,'kind':kind,'status':'Passed' if counts=={'Passed':len(rows)} else 'CompletedWithNonPass',
        'count':len(rows),'counts':counts,'tests':sorted(rows,key=lambda r:r['id']),
        'humanGatePassed':False,'mayEnterR02':False}
    if input_hash:result['inputSha256']=input_hash
    return result


def nunit(path):
    raw=Path(path).read_bytes()
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('DTD/entity XML is not supported')
    root=ET.fromstring(raw)
    if root.tag!='test-run':raise ValueError('Expected NUnit-3 test-run root')
    rows=[]
    for case in root.iter('test-case'):
        ident=case.get('fullname');result=case.get('result')
        if not ident or result not in ('Passed','Failed','Skipped','Inconclusive','Warning'):raise ValueError('Unknown/missing NUnit leaf identity or outcome')
        rows.append({'id':ident,'result':result,'duration':case.get('duration',''),'label':case.get('label','')})
    value=summarize(rows,'H1NUnitLeafInventory',hashlib.sha256(raw).hexdigest())
    if root.get('total') is not None and int(root.get('total'))!=value['count']:raise ValueError('NUnit total differs from leaf inventory')
    value['rootAttributes']=dict(root.attrib)
    return value


def python_suite(tests,pattern,log):
    suite=unittest.TestLoader().discover(str(tests),pattern=pattern)
    def flatten(value):
        for item in value:
            if isinstance(item,unittest.TestSuite):yield from flatten(item)
            else:yield item
    ids=[t.id() for t in flatten(suite)]
    if not ids or len(ids)!=len(set(ids)):raise ValueError('Empty or duplicate unittest discovery')
    class Result(unittest.TextTestResult):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.rows=[];self.failed_subtests=set()
        def record(self,test,result):self.rows.append({'id':test.id(),'result':result})
        def addSuccess(self,test):super().addSuccess(test);self.record(test,'Passed')
        def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'Failed')
        def addError(self,test,err):super().addError(test,err);self.record(test,'Error')
        def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'Skipped')
        def addExpectedFailure(self,test,err):super().addExpectedFailure(test,err);self.record(test,'ExpectedFailure')
        def addUnexpectedSuccess(self,test):super().addUnexpectedSuccess(test);self.record(test,'UnexpectedSuccess')
        def addSubTest(self,test,subtest,err):
            super().addSubTest(test,subtest,err)
            if err:self.failed_subtests.add(test.id())
        def stopTest(self,test):
            if test.id() in self.failed_subtests and not any(r['id']==test.id() for r in self.rows):self.record(test,'FailedSubtest')
            super().stopTest(test)
    with Path(log).open('x',encoding='utf-8') as stream,contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    value=summarize(result.rows,'H1PythonLeafInventory');value['discoveredCount']=len(ids)
    if set(ids)!={r['id'] for r in result.rows}:raise ValueError('Executed identities differ from discovered suite')
    value['logPath']=str(log);value['logSha256']=hashlib.sha256(Path(log).read_bytes()).hexdigest()
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    q=sub.add_parser('nunit');q.add_argument('--xml',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('python');q.add_argument('--tests',type=Path,required=True);q.add_argument('--pattern',default='test*.py');q.add_argument('--log',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Inventory output already exists')
    value=nunit(a.xml) if a.mode=='nunit' else python_suite(a.tests,a.pattern,a.log)
    with a.output.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps({k:value[k] for k in ('kind','status','count','counts')}))
    return 0 if value['status']=='Passed' else 2

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,ET.ParseError) as error:
        print('Failed inventory: '+str(error),file=sys.stderr);raise SystemExit(1)
