#!/usr/bin/env python3
"""One-shot R03 P1 SOURCE preflight: host suites + SDK syntax, NO Players.

A separately authorized candidate preflight. Historical Local/Player roots and
R03/source-pins.json are immutable. This is not R03/V1/runtime acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

BRANCH="codex/assembly-shadow-r01b-h1"
REPOS=("hybridclr_demo","hybridclr","hybridclr_unity","il2cpp_plus")
FIXED={"hybridclr":"4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
       "hybridclr_unity":"948c0e3b4f8891481301770115e8ba4945eea6de"}

def hash_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):h.update(part)
    return h.hexdigest()

def run(args:list[str],timeout:int=120):
    return subprocess.run(list(map(str,args)),capture_output=True,timeout=timeout)

def verify_repo(base:Path,name:str,sha:str)->dict:
    path=base/name
    if not path.is_dir() or path.is_symlink() or path.resolve()!=path:
        raise RuntimeError("Invalid canonical local checkout: "+str(path))
    def git(*args):
        p=run(["git","-C",path,*args])
        if p.returncode:raise RuntimeError("git verification failed "+name+": "+str(args))
        return p.stdout.decode().strip()
    remote=git("remote","get-url","origin")
    canonical="night-outlook/"+name
    if remote not in {"https://github.com/"+canonical,"https://github.com/"+canonical+".git",
                   "git@github.com:"+canonical,"git@github.com:"+canonical+".git",
                   "ssh://git@github.com/"+canonical+".git"}:
        raise RuntimeError("Remote repository identity mismatch "+name)
    if git("branch","--show-current")!=BRANCH or git("rev-parse","HEAD")!=sha:
        raise RuntimeError("Branch/commit mismatch "+name)
    if git("status","--porcelain"):
        raise RuntimeError("Dirty source checkout "+name)
    parts=git("ls-remote","origin","refs/heads/"+BRANCH).split()
    if len(parts)!=2 or parts[0]!=sha or parts[1]!="refs/heads/"+BRANCH:
        raise RuntimeError("Remote HEAD differs or unavailable "+name)
    return {"repository":canonical,"path":str(path),"branch":BRANCH,
            "head":sha,"remoteHead":parts[0],"origin":remote,"clean":True}

def read_managed_result(output:Path, stdout:bytes)->dict:
    """Bind the completed managed producer's stdout to its exact nested receipt.

    Read/hash/parse the same bytes. Never search for a Passed file, copy an
    obsolete root receipt, or accept a child exit code as compilation evidence.
    This consumer does not replace the producer's compiler/output validations.
    """
    def strict_object(raw:bytes)->dict:
        def pairs(items):
            result={}
            for key,value in items:
                if key in result:raise ValueError("Duplicate managed receipt key: "+key)
                result[key]=value
            return result
        def constant(value):
            raise ValueError("Non-finite managed receipt value: "+value)
        result=json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_constant=constant)
        if not isinstance(result,dict):raise ValueError("Managed receipt must be a JSON object")
        return result

    binding=strict_object(stdout)
    expected=output/"build-api/results.json"
    if set(binding)!={"result","sha256"} or binding.get("result")!=str(expected):
        raise ValueError("Managed producer returned an unexpected result path/binding")
    digest=binding["sha256"]
    if not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
        raise ValueError("Managed producer returned an invalid SHA-256")
    # Completed child, private component output: refuse symlink redirection,
    # noncanonical roots and special files. No fallback to another result path.
    if (not output.is_absolute() or output!=output.resolve(strict=True)
        or expected!=expected.resolve(strict=True)
        or not stat.S_ISREG(expected.lstat().st_mode)):
        raise ValueError("Managed result must be a canonical regular file in its component")
    raw=expected.read_bytes()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=digest:raise ValueError("Managed receipt SHA-256 mismatch")
    record=strict_object(raw)
    if (record.get("kind")!="R03CompleteBuildHelperCompile"
        or type(record.get("schemaVersion")) is not int or record["schemaVersion"]!=1
        or record.get("unityVersion")!="2022.3.62f2"
        or not isinstance(record.get("result"),str)
        or record["result"] not in ("Passed","Failed")
        or any(record.get(flag) is not False for flag in
               ("unityEditorRun","nativeExecution","runtimeAcceptance"))):
        raise ValueError("Managed receipt identity/schema/scope mismatch")
    return {"innerResult":record["result"],"innerResultPath":str(expected),
            "innerResultSha256":actual,"returnedBindingVerified":True}

def read_component_result(output:Path, filename:str, require_lifetime_marker:bool=False)->dict:
    """Parse and hash the same canonical receipt bytes; do not follow decoys."""
    if Path(filename).name!=filename:
        raise ValueError("A direct component result filename is required")
    source=output/filename
    if (not output.is_absolute() or output!=output.resolve(strict=True)
        or source!=source.resolve(strict=True)
        or not stat.S_ISREG(source.lstat().st_mode)):
        raise ValueError("Component result must be a canonical regular file")
    raw=source.read_bytes()
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError("Duplicate component receipt key: "+key)
            result[key]=value
        return result
    def constant(value):
        raise ValueError("Non-finite component receipt value: "+value)
    record=json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_constant=constant)
    if not isinstance(record,dict):raise ValueError("Component result must be an object")
    # The new native empty-live producer is fail-stop aware. An absent or
    # malformed marker cannot be interpreted as a verified-safe lifetime.
    # Older unrelated producers retain the original optional marker policy.
    if require_lifetime_marker and "commandLifetimeUnverified" not in record:
        raise ValueError("Missing required command lifetime marker")
    unknown=record.get("commandLifetimeUnverified",False)
    if type(unknown) is not bool:raise ValueError("Invalid command lifetime marker")
    return {"innerResult":record.get("result"),"innerResultPath":str(source),
            "innerResultSha256":hashlib.sha256(raw).hexdigest(),
            "commandLifetimeUnverified":unknown}


def execute_component(dest:Path,name:str,argv:list,expected:str,
                      file:str="RESULT.json",timeout:int=1800)->dict:
    """Record failure before return. Unknown command lifetime stops the batch.

    No process-group/session policy or child environment is changed. Retained
    timeout output is explicitly partial; this function cannot prove that
    detached compiler/SDK descendants have stopped.
    """
    output=dest/name
    result={"name":name,"command":list(map(str,argv)),"startedUnix":time.time(),
            "output":str(output),"expectedInnerResult":expected,"status":"Failed",
            "commandInvoked":True,"exit":None,"timedOut":False,"interrupted":False,
            "commandLifetimeUnverified":False,"descendantQuiescenceProven":False,"stopBatchReason":None,
            "outputCompleteness":"Unavailable"}
    logdir=dest/"commands"/name
    logdir.mkdir(parents=True)
    stdout=stderr=None
    returned=False
    try:
        proc=run(argv,timeout)
        returned=True
        stdout,stderr=proc.stdout,proc.stderr
        result.update(exit=proc.returncode,outputCompleteness="CompleteDirectChildStreams")
        if name=="managed-sdk":
            result.update(read_managed_result(output,stdout))
        else:
            result.update(read_component_result(
                output,file,require_lifetime_marker=(name=="empty-live")))
        if result["commandLifetimeUnverified"]:
            result["stopBatchReason"]="ChildReportedUnverifiedCommandLifetime"
        elif proc.returncode==0 and result.get("innerResult")==expected:
            result["status"]="Passed"
    except subprocess.TimeoutExpired as error:
        stdout,stderr=error.stdout,error.stderr
        result.update(exception=repr(error),timedOut=True,
                      commandLifetimeUnverified=True,outputCompleteness="CapturedPrefix",
                      stopBatchReason="OuterCommandTimeout")
    except KeyboardInterrupt as error:
        result.update(exception=type(error).__name__,interrupted=True,
                      commandLifetimeUnverified=True,stopBatchReason="OuterCommandInterrupted")
    except Exception as error:
        result["exception"]=repr(error)
        if returned and name=="empty-live":
            # A completed child without a valid lifetime receipt could have
            # timed out internally. Do not schedule more subprocess children.
            result.update(commandLifetimeUnverified=True,
                          stopBatchReason="EmptyLiveReceiptUnavailableOrInvalid")
        elif not returned and not isinstance(error,OSError):
            result.update(commandLifetimeUnverified=True,
                          stopBatchReason="UnknownCommandExecutionOutcome")
    finally:
        for stream,data in (("stdout",stdout),("stderr",stderr)):
            result[stream+"Available"]=data is not None
            if data is None:data=b""
            if not isinstance(data,bytes):
                raise TypeError("Command capture must return bytes")
            filename=stream+".bin"
            (logdir/filename).write_bytes(data)
            result[filename+"Sha256"]=hashlib.sha256(data).hexdigest()
            result[stream+"CapturedBytes"]=len(data)
        result["finishedUnix"]=time.time()
        (dest/"commands"/(name+".json")).write_text(json.dumps(result,indent=2)+"\n")
    return result


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ("workspace","unity","output","sdk-scratch"):
        parser.add_argument("--"+flag,required=True,type=Path)
    for flag in ("expected-demo","expected-native"):
        parser.add_argument("--"+flag,required=True)
    a=parser.parse_args()
    if not __debug__:raise RuntimeError("Python -O forbidden")
    for commit in (a.expected_demo,a.expected_native):
        if not re.fullmatch(r"[a-f0-9]{40}",commit):raise RuntimeError("Expected full 40-hex SHA")
    ws=a.workspace
    if not ws.is_absolute() or ws!=ws.resolve(strict=True) or not ws.is_dir():
        raise RuntimeError("Canonical absolute workspace required")
    dest=a.output
    scratch=a.sdk_scratch
    if (not dest.is_absolute() or dest!=dest.resolve(strict=False) or dest.exists()
        or not dest.parent.is_dir() or not scratch.is_absolute()
        or scratch!=scratch.resolve(strict=False) or scratch.exists()
        or not scratch.parent.is_dir() or ws in dest.parents or dest in ws.parents
        or ws in scratch.parents or scratch in ws.parents
        or scratch==dest or scratch in dest.parents or dest in scratch.parents):
        raise RuntimeError("Unused external distinct evidence and SDK scratch roots required")
    if not a.unity.is_file() or not a.unity.as_posix().endswith(
            "/2022.3.62f2/Unity.app/Contents/MacOS/Unity"):
        raise RuntimeError("Exact installed Unity2022.3.62f2 Editor binary required")
    pins=dict(FIXED,hybridclr_demo=a.expected_demo,il2cpp_plus=a.expected_native)
    before=[verify_repo(ws,n,pins[n]) for n in REPOS]
    demo=ws/"hybridclr_demo"
    native=ws/"il2cpp_plus"
    py=sys.executable
    # Scripts and gate sources are bound both and after the batch.
    inputs=[
        demo/"Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py",
        demo/"Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py",
        demo/"Tools/AssemblyShadow/R03IR/run_p1_command_failure_tests.py",
        demo/"Tools/AssemblyShadow/R03IR/test_p1_command_failures.py",
        native/"tools/r03/diagnostic_stream/test_bounded_general_live_command.py",
        demo/"Tools/AssemblyShadow/R03/native_validation.py",
        demo/"Tools/AssemblyShadow/R03/build_api.py",
        demo/"Tools/AssemblyShadow/R03/source-pins.json",
        native/"libil2cpp/vm/AssemblyShadowMetadataLifetime.h",
        native/"libil2cpp/vm/Runtime.cpp",
        native/"libil2cpp/vm/Assembly.cpp",
        native/"libil2cpp/vm/AssemblyShadowVisibility.cpp",
        native/"tools/r03/diagnostic_stream/run_metadata_lifetime_gate.py",
        native/"libil2cpp/vm/AssemblyShadowBoundedGeneralComposer.h",
        native/"libil2cpp/vm/AssemblyShadowFrozenGeneralCapture.h",
        native/"tools/r03/diagnostic_stream/run_bounded_general_composer.py",
        native/"tools/r03/diagnostic_stream/bounded_general_composer_fixture.cpp",
        native/"libil2cpp/vm/AssemblyShadowBoundedGeneralLive.h",
        native/"libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl",
        # Inactive owned execution / typed R02 record and immutable references.
        native/"libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h",
        # P1 inactive source-bound zero-class execution and mock fixture.
        native/"libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h",
        native/"libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl",
        native/"libil2cpp/vm/AssemblyShadowOpaqueExecutionInventory.h",
        native/"libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl",
        native/"tools/r03/diagnostic_stream/run_opaque_execution_inventory.py",
        native/"tools/r03/diagnostic_stream/opaque_inventory_fixture.cpp",
        native/"tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py",
        native/"tools/r03/diagnostic_stream/test_bounded_execution_empty_live_receipts.py",
        native/"tools/r03/diagnostic_stream/empty_live_fixture/MockRuntime.h",
        native/"tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowFrozenExecutionRecord.h",
        native/"tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowMetadataLifetime.h",
        native/"tools/r03/diagnostic_stream/empty_live_fixture/fixture.cpp",
        native/"libil2cpp/vm/AssemblyShadowR02Snapshot.h",
        native/"libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h",
        native/"libil2cpp/vm/AssemblyShadowExecutionSerializer.h",
        native/"libil2cpp/vm/AssemblyShadowR02Diagnostics.h",
        native/"libil2cpp/vm/AssemblyShadowDiagnosticWriter.h",
        native/"libil2cpp/vm/AssemblyShadowObservationCounters.h",
        native/"libil2cpp/vm/AssemblyShadowObservationMemo.h",
        native/"libil2cpp/vm/AssemblyShadowDiagnosticsProfile.h",
        native/"tools/r03/diagnostic_stream/run_frozen_execution.py",
        native/"tools/r03/diagnostic_stream/frozen_execution_fixture.cpp",
        native/"tools/r03/diagnostic_stream/frozen_execution_allocations.cpp",
        native/"tools/r03/diagnostic_stream/test_frozen_execution_include_path.py",
        native/"tools/r03/diagnostic_stream/reference/AssemblyShadowExecutionSerializer.h",
        native/"tools/r03/diagnostic_stream/reference/AssemblyShadowR02Diagnostics.h",
        native/"libil2cpp/vm/AssemblyShadow.h",
        native/"libil2cpp/vm/AssemblyShadow.cpp",
        native/"tools/r03/diagnostic_stream/run_bounded_general_live.py",
        native/"tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp",
        demo/"Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowGeneralComposeSyntax.cpp",
        demo/"Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionComposeSyntax.cpp",
        demo/"Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionEmptyLiveSyntax.cpp",
        demo/"Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowOpaqueInventorySyntax.cpp",
    ]
    hashes={str(p):hash_file(p) for p in inputs}
    dest.mkdir(mode=0o700)
    cases=[]
    stopped=None
    def execute(name:str,argv:list,expected:str,file:str="RESULT.json",timeout:int=1800):
        nonlocal stopped
        if stopped is not None:
            # A scheduled cell is NOT a launched child. Retain an explicit
            # NotRun receipt without creating or reusing its component root.
            result={"name":name,"command":list(map(str,argv)),
                    "output":str(dest/name),"expectedInnerResult":expected,
                    "status":"NotRun","commandInvoked":False,
                    "reason":"StoppedAfter:"+stopped}
            (dest/"commands"/(name+".json")).write_text(json.dumps(result,indent=2)+"\n")
        else:
            result=execute_component(dest,name,argv,expected,file,timeout)
            if result.get("stopBatchReason"):
                stopped=name+":"+result["stopBatchReason"]
        cases.append(result)
    try:
        execute("command-failures",[py,"-B",demo/"Tools/AssemblyShadow/R03IR/run_p1_command_failure_tests.py",
                "--native",native,"--output",dest/"command-failures"],"PassedWithinHostScope")
        execute("legacy-host",[py,"-B",demo/"Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py",
              "--workspace",ws,"--expected-demo",a.expected_demo,
              "--expected-native",a.expected_native,"--output",dest/"legacy-host"],"PassedHostOnly")
        specs=(
            ("metadata-gate","run_metadata_lifetime_gate.py","PassedWithinHostScope"),
            ("bounded-class","run_bounded_ordinary_classes.py","PassedWithinHostScope"),
            ("bounded-physical","run_bounded_physical_assemblies.py","PassedWithinHostScope"),
            ("bounded-first-use","run_bounded_first_use.py","PassedWithinHostScope"),
            ("owned-general","run_bounded_general_composer.py","PassedWithinOwnedHostScope"),
            ("live-general","run_bounded_general_live.py","PassedWithinInactiveSourceHostScope"),
            ("owned-execution","run_frozen_execution.py","PassedWithinOwnedExecutionHostScope"),
            ("empty-live","run_bounded_execution_empty_live.py","PassedWithinInactiveZeroClassHostScope"),
            ("opaque-inventory","run_opaque_execution_inventory.py","PassedWithinInactiveOpaqueHostScope"),
            ("bounded-status","run_bounded_transaction_status.py","PassedWithinHostScope"),
            ("bounded-inventory","run_bounded_transaction_inventory.py","PassedWithinHostScope"),
            ("frozen-v2","run_frozen_v2.py","PassedWithinInactiveHostScope"),
        )
        for name,script,expected in specs:
            cmd=[py,"-B",native/"tools/r03/diagnostic_stream"/script,
                 "--native",native,"--output",dest/name]
            if name=="frozen-v2":cmd.extend(("--demo",demo))
            execute(name,cmd,expected)
        execute("managed-sdk",[py,"-B",demo/"Tools/AssemblyShadow/R03/build_api.py",
                "--workspace",ws,"--unity",a.unity,"--output",dest/"managed-sdk"],
                "Passed",timeout=3600)
        execute("native-sdk",[py,"-B",demo/"Tools/AssemblyShadow/R03/native_validation.py",
                "--workspace",ws,"--unity",a.unity,"--output",dest/"native-sdk",
                "--sdk-scratch",scratch,"--candidate-native-sha",a.expected_native],
                "Passed",file="results.json",timeout=7200)
    finally:
        postflight_error=None
        after=[]
        try:
            if stopped is not None:
                raise RuntimeError("Postflight unavailable: command lifetime unverified; "+stopped)
            after=[verify_repo(ws,n,pins[n]) for n in REPOS]
            preserved=before==after and hashes=={str(p):hash_file(p) for p in inputs}
        except Exception as e:
            # Even if source changed or a checkout disappeared, retain the
            # thirteen independent cases and factual postflight errors, never mark PASS.
            postflight_error=repr(e)
            preserved=False
        success=preserved and stopped is None and len(cases)==16 and all(c["status"]=="Passed" for c in cases)
        statuses={c["name"]:c["status"] for c in cases}
        summary={"kind":"R03P1FailureAwareSourceSDKPreflight","schemaVersion":2,
          "stoppedAfter":stopped,"commandLifetimeUnverified":stopped is not None,
          "descendantQuiescenceProven":False,
          "componentCount":16,"attemptedComponentCount":sum(c["commandInvoked"] for c in cases),
          "result":"PassedSourceHostAndSDKOnly" if success else "FailedOrIncomplete",
          "fourRepositoriesBefore":before,"fourRepositoriesAfter":after,
          "sourceSha256":hashes,"sourcePreserved":preserved,
          "postflightError":postflight_error,"commands":cases,
          "officialUnitySdkCompileAttempted":all(any(c["name"]==n and c["commandInvoked"] for c in cases)
                                                 for n in ("managed-sdk","native-sdk")),
          "officialUnitySdkCompilePassed":statuses.get("managed-sdk")=="Passed" and
                                          statuses.get("native-sdk")=="Passed",
          "nativeSDKCandidateMode":True,
          "expectedNativeSyntaxUnits":90,
          "realUnityEditorLaunched":False,"UnityPlayerExecuted":False,
          "engineOwnerProven":False,"R03Accepted":False,"ReadyForHumanReviewGate":False,
          "historicalEvidenceReclassified":False}
        (dest/"RESULT.json").write_text(json.dumps(summary,indent=2)+"\n")
        # Inventory final evidence outputs but never copy SDK/vendor bytes.
        manifest=[{"path":str(p.relative_to(dest)),"size":p.stat().st_size,
                   "sha256":hash_file(p)} for p in sorted(dest.rglob("*")) if p.is_file() and not p.is_symlink()]
        (dest/"MANIFEST.json").write_text(json.dumps({"files":manifest,
            "inventoryScope":"UnsealedObservedFiles" if stopped is not None else "CompletedBatchFiles",
            "commandLifetimeUnverified":stopped is not None},indent=2)+"\n")
    print(json.dumps({"result":summary["result"],
                      "cases":[(c["name"],c["status"]) for c in cases]},indent=2))
    if any(c.get("interrupted") for c in cases):raise SystemExit(130)
    if summary["result"]!="PassedSourceHostAndSDKOnly":raise SystemExit(1)

if __name__=="__main__":main()
