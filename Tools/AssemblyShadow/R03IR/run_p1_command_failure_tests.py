#!/usr/bin/env python3
"""Source-bound P1 command failure contracts; no Unity SDK or native compilation.

Runs actual Python command-wrapper tests, including controlled real Python child
processes. Git/SDK/VM execution in the orchestration tests is explicitly mocked.
The full Local batch supplies four-source Git custody; this child binds bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent


def binding(path:Path)->dict:
    data=path.read_bytes()
    return {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
            "gitBlob":hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()}


def test_ids(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from test_ids(item)
        else:yield item.id()


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if not __debug__:raise RuntimeError("Python -O forbidden")
    if os.environ.get("P1_RECEIPT_TEST_RUNNER"):
        raise RuntimeError("Alternate receipt test source override forbidden")
    native=args.native
    out=args.output
    demo=HERE.parents[2]
    if (not native.is_absolute() or native!=native.resolve(strict=True) or not native.is_dir()
        or not out.is_absolute() or out!=out.resolve(strict=False) or out.exists()
        or not out.parent.is_dir()):
        raise RuntimeError("Canonical native source and unused external output required")
    for protected in (native,demo):
        if out==protected or out in protected.parents or protected in out.parents:
            raise RuntimeError("Test evidence must be disjoint from source roots")
    native_tests=native/"tools/r03/diagnostic_stream"
    modules=(
        (HERE/"test_p1_metadata_preflight.py",5),
        (HERE/"test_p1_managed_receipt.py",14),
        (HERE/"test_p1_command_failures.py",44),
        (native_tests/"test_bounded_general_live_command.py",10),
        (native_tests/"test_bounded_execution_empty_live_receipts.py",12),
    )
    sources=[Path(__file__).resolve(),HERE/"run_p1_metadata_local_preflight.py",
             HERE.parent/"R03/build_api.py",HERE.parent/"R03/native_validation.py",
             native_tests/"run_bounded_general_live.py",
             native_tests/"run_bounded_execution_empty_live.py",
             native_tests/"run_physical_membership.py",
             native_tests/"run_owned_physical_names.py",
             native_tests/"run_owned_physical_json.py",
             native_tests/"owned_physical_json_fixture.cpp",
             native/"libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesJson.h",
             HERE/"PlayerProject/AssemblyShadowOwnedPhysicalNamesSyntax.cpp",
             *[p for p,_ in modules]]
    before={str(p):binding(p) for p in sources}
    out.mkdir(mode=0o700)
    record={"kind":"R03P1CommandFailureContracts","schemaVersion":1,
            "result":"FailedOrIncomplete","startedUnix":time.time(),
            "expectedTestCount":85,"testsRun":0,"testIds":[],"modules":[],
            "sourceBefore":before,"sourcePreserved":False,
            "python":sys.version,"platform":platform.platform(),
            "realPythonChildTests":True,"gitSdkVmChildrenMocked":True,
            "nativeCompilerExecuted":False,"officialUnitySdkCompiled":False,
            "UnityPlayerExecuted":False,"runtimeAcceptance":False,
            "commandLifetimeUnverified":False}
    with (out/"unittest.log").open("x",encoding="utf-8") as stream:
        try:
            suite=unittest.TestSuite()
            loader=unittest.TestLoader()
            for index,(path,count) in enumerate(modules):
                spec=importlib.util.spec_from_file_location("p1_contract_suite_"+str(index),path)
                if spec is None or spec.loader is None:raise RuntimeError("Missing test module loader")
                module=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                part=loader.loadTestsFromModule(module)
                ids=list(test_ids(part))
                if len(ids)!=count:raise RuntimeError("Changed test inventory: "+str(path))
                record["modules"].append({"path":str(path),"expectedTests":count,"testIds":ids})
                record["testIds"].extend(ids)
                suite.addTests(part)
            if len(set(record["testIds"]))!=85 or loader.errors:
                raise RuntimeError("Duplicate/missing test IDs or test loading errors")
            result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
            record.update(testsRun=result.testsRun,failures=len(result.failures),
                          errors=len(result.errors),skipped=len(result.skipped),
                          expectedFailures=len(result.expectedFailures),
                          unexpectedSuccesses=len(result.unexpectedSuccesses))
            after={str(p):binding(p) for p in sources}
            record.update(sourceAfter=after,sourcePreserved=before==after)
            if (result.wasSuccessful() and result.testsRun==85 and before==after
                and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses):
                record["result"]="PassedWithinHostScope"
        except BaseException as error:
            record["exception"]=repr(error)
            record["commandLifetimeUnverified"]=isinstance(error,KeyboardInterrupt)
            raise
        finally:
            stream.flush()
            record["finishedUnix"]=time.time()
            record["log"]=binding(out/"unittest.log")
            (out/"RESULT.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
            files=[{"path":p.name,**binding(p)} for p in sorted(out.iterdir())
                   if p.is_file() and not p.is_symlink()]
            (out/"MANIFEST.json").write_text(json.dumps({"files":files,
                "inventoryScope":"UnsealedObservedFiles" if record["commandLifetimeUnverified"]
                                 else "CompletedContractFiles"},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":record["result"],"testsRun":record["testsRun"]}))
    if record["result"]!="PassedWithinHostScope":raise SystemExit(1)

if __name__=="__main__":main()
