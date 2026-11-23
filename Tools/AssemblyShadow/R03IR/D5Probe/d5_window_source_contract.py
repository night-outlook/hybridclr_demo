#!/usr/bin/env python3
"""D5 C10 source-only linkage candidate checks. No Unity/IL2CPP build or Player.

Authenticates *specific* native/overlay/managed Git blobs and syntax anchors.
A source scan cannot prove full native compilation, linkage, runtime method
admission, the C10 failure result or the time of a live publication event.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

NATIVE_COMMIT = "87a34bbea39930dab96cf4703756d8da79d54684"
NATIVE_FILES = {
    "libil2cpp/vm/AssemblyShadow.cpp":"a5e7e654a2b1ede83ae18b8f15fcb4ee51f96490",
    "libil2cpp/vm/AssemblyShadowD5WindowProbe.h":"d89d457ba73685b9505185f1d788f0bbf6a6d216",
    "libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h":"ccd10ea0a1d273f5fe31f52d346d090b0a5af79c",
}
DEMO_FILES = {
    "Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp":"c7fbc81c25e42e93c8dd318a5dd2d05455d33993",
    "Tools/AssemblyShadow/R03IR/D5Probe/R03D5P5WindowPlayer.cs":"b54d4df59e498a5eb5fb6ac59d3a17ac47505110",
    "Tools/AssemblyShadow/R03IR/D5Probe/R03D5Build.cs":"31ca04858aa00c5d1db1678d784a804ed076e159",
}
BRANCH = "codex/assembly-shadow-r01b-h1"
MACRO = "HYBRIDCLR_R03_D5_WINDOW_PROBE"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class SourceMismatch(ValueError):
    pass


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SourceMismatch(msg)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\0" + raw).hexdigest()


def git(repo: Path, *params: str) -> str:
    p = subprocess.run(["git","-C",str(repo),*params],
                       capture_output=True,text=True,timeout=60,check=False)
    require(p.returncode==0,"Git source query failed: "+str(params))
    return p.stdout.strip()


def read_source(repo: Path, paths: dict) -> dict:
    result = {}
    for rel,expected in paths.items():
        fp=repo/rel
        require(fp.is_file() and not fp.is_symlink(),"Missing/symlinked source: "+rel)
        raw=fp.read_bytes()
        require(git_blob(raw)==expected and
                git(repo,"rev-parse","HEAD:"+rel)==expected,
                "Pinned Git blob changed: "+rel)
        result[rel]=raw.decode("utf-8-sig")
    return result


def ordered(section: str, anchors: list[str], label: str) -> None:
    ps=[section.find(s) for s in anchors]
    require(all(p>=0 for p in ps) and ps==sorted(ps) and
            len(set(ps))==len(ps),label+" source order changed")


def verify_sources(native: dict[str,str], demo: dict[str,str]) -> dict:
    cpp=native["libil2cpp/vm/AssemblyShadow.cpp"]
    header=native["libil2cpp/vm/AssemblyShadowD5WindowProbe.h"]
    owner=native["libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h"]
    overlay=demo["Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp"]
    managed=demo["Tools/AssemblyShadow/R03IR/D5Probe/R03D5P5WindowPlayer.cs"]
    builder=demo["Tools/AssemblyShadow/R03IR/D5Probe/R03D5Build.cs"]

    require("#include \"AssemblyShadowD5WindowProbe.h\"" in cpp and
            cpp.count("#if defined("+MACRO+") && "+MACRO) >= 7,
            "Native D5 sources must be explicitly gated by the test-only macro")
    require("ProcessSnapshotOwner<ActiveSnapshot> activeOwner" in cpp and
            "retained_ = std::move(pending);" in owner and
            "published.store(retained_.get(), std::memory_order_release);" in owner,
            "Unmodified D4 process-owned active publication is required")

    p5=cpp.find('Event(transaction, "active-published");')
    p6=cpp.find("assembly_shadow_publication::Phase::InitializersRunning",p5)
    require(p5>=0 and p6>p5,"Actual D4 P5/P6 boundary missing")
    section=cpp[p5:p6]
    ordered(section,[
        "d5Window.AtP5();",
        "lock.unlock();",
        "d5Window.HoldP5Bounded();",
        "lock.lock();",
        "s_state.load(std::memory_order_acquire)",
    ],"Test-only release-and-reacquire")
    require("postActiveExit.Seal(" in section and
            "AssemblyShadowState::Committing" in section,
            "D5 native window must fail closed on state racing")
    later=cpp[p6:cpp.find("AssemblyShadowError AssemblyShadow::AbortTransaction()",p6)]
    require("WindowProbe::Instance().AtP6();" in later and
            "WindowProbe::Instance().Complete();" in later,
            "P6 and completed native witness annotations absent")
    method=cpp[cpp.find("bool AssemblyShadow::AssertMethodIsActive("):
               cpp.find("void AssemblyShadow::RequireActiveMethod(")]
    require(method.startswith("bool AssemblyShadow::AssertMethodIsActive(") and
            "WindowProbe::Instance().MethodBegin()" in method and
            "active->shadowToBaseline.count(owners[0])" in method and
            'std::strcmp(d5Owner->aname.name, "Methods")' in method and
            'std::strcmp(method->klass->namespaze, "R03")' in method and
            'std::strcmp(method->klass->name, "Node")' in method and
            'std::strcmp(method->name, "Keep")' in method and
            "active->shadowToBaseline.count(d5Owner)" in method and
            "MatchesTargetOnCurrentThread(method)" in method and
            method.count("WindowProbe::Instance().MethodResult(")==2 and
            "return allowed;" in method and "return false;" in method,
            "Actual shadow MethodInfo admission witness incomplete")

    require("enum class WindowPhase" in header and
            "AtP5 = 2" in header and "AtP6 = 3" in header and
            "Complete = 4" in header and
            "maximumWaitMs < 20 || maximumWaitMs > 2000" in header and
            "std::chrono::steady_clock::now()" in header and
            "std::this_thread::yield()" in header and
            "std::memory_order_acquire" in header and
            "std::memory_order_release" in header and
            "methodResultRacedP6_.fetch_add" in header,
            "Native fixed-field bounded C++11 witness changed")
    require("C10 counters are scoped" in header and
            "ArmTargetForCurrentThread" in header and
            "MatchesTargetOnCurrentThread" in header and
            "ThreadAttempt& CurrentThreadAttempt()" in header and
            "token.active = 0;" in header and
            "targetDecision_.store" in header and
            header.count("std::atomic<int32_t>")>=10 and
            "new " not in header and "delete " not in header and
            "std::mutex" not in header and "throw " not in header,
            "Native witness must not allocate, throw or acquire a mutex")

    exports=["R03_D5_WindowProtocolVersion","R03_D5_ArmP5Window",
             "R03_D5_ReleaseP5Window","R03_D5_ReadP5Window",
             "R03_D5_ReceiptOpen","R03_D5_ReceiptEvent",
             "R03_D5_BindKeepCanary","R03_D5_ReceiptSeal",
             "R03_D5_BeginKeepAttempt"]
    for sym in exports:
        require("IL2CPP_EXPORT int32_t "+sym in overlay,
                "Test-only overlay is missing native export: "+sym)
    require("static_assert(sizeof(WindowSnapshot) == sizeof(int32_t) * 11" in overlay and
            "std::memcpy(destination, &value, sizeof value);" in overlay and
            "#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined("+MACRO+") && "+MACRO in overlay and
            "operator new(" not in overlay and "operator delete(" not in overlay,
            "Fixed wire protocol, feature-OFF or allocator purity changed")
    require("O_EXCL | O_CLOEXEC | O_NOFOLLOW" in overlay and
            "::pwrite(fd" in overlay and "::fsync(fd)" in overlay and
            "kSlots = 10" in overlay and
            "sizeof(Event) == 32" in overlay and
            "sizeof(FirstErrorDisk) == 4120" in overlay and
            "TryReadFirstFailureV2(snapshot)" in overlay and
            "ReadCanary(after)" in overlay and
            "Record(9, canaryBefore, after, valid, 0)" in overlay and
            "GCHandle::New(object, true)" in overlay and
            'Class::GetFieldFromName(object->klass, "stable")' in overlay and
            "R03_D5_NATIVE_VM_EVIDENCE" in overlay and
            "NativeCollector(void*)" in overlay and
            "::pthread_create(" in overlay and
            "::pthread_detach(" in overlay and
            "::usleep(1000)" in overlay and
            "::_exit(status)" in overlay and
            "FinishNativeReceipt(stateCode, decision)" in overlay and
            "Record(5, decision, 1, 1, 0)" in overlay and
            "R03_D5_SOURCE_HOST_AUTO" in overlay and
            "R03_D5_SourceHostAutoConfigure" in overlay and
            "Class::GetMethodFromName(" in overlay and
            "ArmTargetForCurrentThread(boundKeepMethod)" in overlay,
            "Native exclusive output/canary/first-error source contract changed")

    auto_start=overlay.find("static int32_t FinishNativeReceipt(")
    auto_end=overlay.find("static void* NativeCollector(",auto_start)
    require(auto_start>=0 and auto_end>auto_start and
            "TryReadFirstFailureV2(snapshot)" in overlay[auto_start:auto_end] and
            "Record(9, canaryBefore, after, valid, 0)" in overlay[auto_start:auto_end],
            "Native autonomous seal must preserve actual first-error/canary")

    checks=[
       "R03_D5_ArmP5Window(req.maximumWaitMilliseconds)",
       "Thread thread = new Thread(worker.Run)",
       'Type.GetType("R03.Node, Methods", true)',
       "method.Invoke(instance, null)",
       "R03_D5_ReceiptOpen(outputPath, req.runId,",
       "GCHandle.ToIntPtr(handle)",
       "nativeBindSucceeded = R03_D5_BindKeepCanary(",
       "keepAttempted = R03_D5_BeginKeepAttempt() == 1;",
       "AssemblyShadowRuntime.CommitTransaction();",
       "NativeCollector publishes a bounded native-only receipt",
       "finally { handle.Free(); }",
    ]
    for needle in checks:
        require(needle in managed,"Managed exact Keep/native receipt contract missing: "+needle)
    require("JsonUtility.ToJson" not in managed and
            "FileStream(" not in managed and
            "FileMode.Create" not in managed and
            "R03Accepted = true" not in managed and
            "nativeBindSucceeded" in managed and
            "finally { handle.Free(); }" in managed and
            "keepAttempted = " in managed and
            "R03_D5_ReceiptSeal(" not in managed and
            "Thread.Join(" not in managed and
            "GetState(out state)" not in managed and
            'R03_D5_ReceiptEvent(5' not in managed,
            "Managed post-terminal source wrote JSON/I/O or lost target evidence")
    require('Application.unityVersion != "2022.3.62f2"' in managed and
            'Application.platform != RuntimePlatform.OSXPlayer' in managed and
            "AssemblyShadowRuntime.CommitTransaction()" in managed,
            "Player fixture pinned real commit/Unity source missing")

    ordered(builder,[
        "PinnedSourceInstaller.Install();",
        "File.Copy(config.overlayPath, overlayDestination, false);",
        "PrebuildCommand.GenerateAll();",
        "BuildPipeline.BuildPlayer(new BuildPlayerOptions",
    ],"Isolated Unity Builder installation/generation/BuildPipeline")
    require(re.search(r"(?<![A-Za-z0-9_])BuildPipeline\.BuildPlayer\s*\(", builder) is not None,
            "Real Unity BuildPipeline entrypoint replaced")
    require("public static class R03D5Build" in builder and
            'Application.unityVersion != "2022.3.62f2"' in builder and
            '"87a34bbea39930dab96cf4703756d8da79d54684"' in builder and
            "ScriptingImplementation.IL2CPP" in builder and
            "BuildOptions.Development | BuildOptions.DetailedBuildReport" in builder and
            "HYBRIDCLR_R03_D5_WINDOW_PROBE=" in builder and
            "HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=" in builder and
            "FileMode.CreateNew" in builder and
            "independentLinkedBinaryProof = false" in builder and
            "actualD5PlayerRun = false" in builder and
            'File.Exists(Path.Combine(project, ".r03-d5-isolated-project"))' in builder and
            "BuildResult.Succeeded" in builder and
            "receipt.compilerFlags = PlayerSettings.GetAdditionalIl2CppArgs();" in builder,
            "Test-only Unity build source binding or native build receipt lost")

    return {"schema":"R03D5C10SourceCandidateV1",
            "result":"PassedActualSourceContractOnly_NotUnityPlayer",
            "actualNativeD5ProductionHeader":True,
            "actualMethodGuardSourceInstrumented":True,
            "nativeProbeExportsDeclared":len(exports),
            "nativeAutoCollectorSourcePresent":True,
            "nativeWorkerTargetIdentityBoundSourceOnly":True,
            "nativeEvidenceAndCanaryRealPlayerVerified":False,
            "realPlayerC10Completed":False,
            "compiledUnityNativeTranslationUnit":False,
            "realPlayerFaultProducerLinked":False,
            "unityOrPlayerExecuted":False,
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
            "R03Accepted":False}


def inspect(native_root: Path,demo_root: Path,
            expected_native_head: str,expected_demo_head: str) -> dict:
    require(type(expected_native_head) is str and
            expected_native_head == NATIVE_COMMIT and
            type(expected_demo_head) is str and HEX40.fullmatch(expected_demo_head),
            "Expected Git-pinned native and full demo SHA required")
    for root in (native_root,demo_root):
        require(root.is_absolute() and root.is_dir() and
                not root.is_symlink() and root.resolve(strict=True)==root,
                "Physical Git source root required")
    require(git(native_root,"rev-parse","HEAD")==expected_native_head,
            "Native HEAD is not the pinned D5 C10 source")
    require(git(demo_root,"rev-parse","HEAD")==expected_demo_head,
            "Demo HEAD is not the current GitHub Actions commit")
    n=read_source(native_root,NATIVE_FILES)
    d=read_source(demo_root,DEMO_FILES)
    return verify_sources(n,d)


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native-root",type=Path,required=True)
    p.add_argument("--demo-root",type=Path,required=True)
    p.add_argument("--expected-native-head",required=True)
    p.add_argument("--expected-demo-head",required=True)
    a=p.parse_args()
    try:
        print(json.dumps(inspect(a.native_root,a.demo_root,
              a.expected_native_head,a.expected_demo_head),
              sort_keys=True))
        return 0
    except (SourceMismatch,OSError,ValueError,
            subprocess.SubprocessError) as err:
        print(json.dumps({"schema":"R03D5C10SourceCandidateV1",
            "result":"RejectedSourceBeforeUnityOrPlayer",
            "reason":str(err),"unityOrPlayerExecuted":False,
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION","R03Accepted":False}),
            file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
