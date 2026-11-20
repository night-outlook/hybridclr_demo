#!/usr/bin/env python3
"""D5-A read-only Git-source admission. No Unity, Player, SDK or local handoff."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

BRANCH = "codex/assembly-shadow-r01b-h1"
PINS = {
    "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699",
}
REPOS = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
COUNTS = {"hybridclr_demo": 7, "hybridclr": 9,
          "hybridclr_unity": 4, "il2cpp_plus": 13}
PROFILE_BLOB = "4f871e1818adc1056652857546658ff94062a221"
FIXTURE_BLOB = "dbdfd51b85b1a8dfc9caedd9916842e1b0d042fc"
LEGACY_NATIVE = "8aa8d09319a89b55b2496bcc2c69ccc69cb57be9"
LEGACY_HYBRID = "4b2774b066cfc6afd77a8c8aded6bda7ea574f55"
ORIGINAL_S = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
CASES = tuple("D5-C%02d" % n for n in range(1, 19))
HEX = re.compile(r"^[0-9a-f]{40}$")
PROFILE = "Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json"
FIXTURES = "Tools/AssemblyShadow/R03IR/D5Admission/d5a_fixture_registry_v1.json"

class Rejected(ValueError): pass

def need(ok, why):
    if not ok: raise Rejected(why)

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate JSON key " + key)
        result[key] = value
    return result

def read_json(raw: bytes):
    value = json.loads(raw, object_pairs_hook=strict_pairs)
    need(type(value) is dict, "Expected JSON object")
    return value

def validate_profile(p):
    need(p.get("schemaVersion") == 1 and
         p.get("kind") == "R03B2D5APinnedSourceAdmissionV1" and
         p.get("branch") == BRANCH and
         p.get("predecessorGate") == "PassD4ForNextGate",
         "D5-A exact profile schema/branch/gate")
    need(p.get("pins") == {**PINS,
         "hybridclr_demo": "EXPECTED_DEMO_HEAD_ARGUMENT_REQUIRED"},
         "D4 source pins or mandatory dynamic demo pin changed")
    need(p.get("authority") == {
        "D5A":"ApprovedByUser","D5B":"NotAuthorized",
        "D5LocalValidation":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted":False,"H2Passed":False,
        "ReadyForHumanReviewGate":False,
        "allowUnityOrPlayerExecution":False},
        "D5-B Local execution not authorized")
    need(p.get("historicalReadOnly") == {
        "originalS":ORIGINAL_S,"oldNative":LEGACY_NATIVE,
        "oldHybridclr":LEGACY_HYBRID,"oldB1SourceCount":14,
        "oldB1VmDeltaCount":46,"allowHistoricalEvidenceForD5":False,
        "allowReplacingOldCandidate":False}, "Historical B1 profile changed")
    inventory = p.get("sourceGitBlobs")
    need(type(inventory) is dict and set(inventory) == set(REPOS),
         "Exact four source inventory roles")
    for repo in REPOS:
        m = inventory[repo]
        need(type(m) is dict and len(m) == COUNTS[repo] and
             all(type(k) is str and k and not k.startswith("/") and
                 ".." not in Path(k).parts and
                 type(v) is str and HEX.fullmatch(v) for k,v in m.items()),
             "Source inventory invalid for "+repo)
    native = inventory["il2cpp_plus"]
    need("libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h" in native and
         "libil2cpp/vm/AssemblyShadow.cpp" in native and
         "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp" in native,
         "Required exact D4 owner/host sources absent")
    allowed = set(native) - {"libil2cpp/vm/AssemblyShadow.h",
        "libil2cpp/utils/dynamic_array.h",
        "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"}
    need(set(p.get("nativeInstallSources",[])) == allowed and
         p.get("forbiddenInstalledSourcePrefixes") ==
            ["NativeHostTests/","Tests/"],
         "Native test allocator must not enter production install roster")
    need(p.get("sourceOnlyBuildRosterEvidence") ==
         "ReviewedSourceInventoryOnly_NotInstalledUnityCompilation",
         "Cannot promote source roster to installed native evidence")
    need(p.get("fixtureRegistryPath") == FIXTURES, "D5-A fixture moved")
    need(p.get("targetPreview") == {
        "unity":"2022.3.62f2","platform":"macOS","arch":"arm64",
        "scriptingBackend":"IL2CPP","cppMode":"Release",
        "featureOn":True,"featureOffControl":True,
        "actualHostVerified":False}, "Target or toolchain preview changed")
    need(p.get("readOnlyOutputOnly") is True and
         p.get("ciTestedDemoHeadMustMatchCheckout") is True,
         "D5-A may only verify source")
    return p

def validate_fixture(f,p):
    need(f.get("schemaVersion")==1 and
         f.get("kind")=="R03B2D5AProposedRealPlayerFixtureRegistryV1" and
         f.get("applicableBranch")==BRANCH and
         f.get("sourceAnchor")=="D4IndependentReviewPassD4ForNextGate" and
         f.get("status")=="SourceInventoryOnly_NotRealD5PlayerCoverage",
         "Fixture schema/source authority mismatch")
    need(f.get("localExecutionAuthority") is False and
         f.get("unityOrPlayerExecuted") is False and
         type(f.get("realPlayerEvidenceCount")) is int and
         f["realPlayerEvidenceCount"]==0,
         "Source tests cannot assert real Player acceptance")
    rows=f.get("cases")
    need(type(rows) is list and len(rows)==18 and
         f.get("caseCount")==18 and
         tuple(x.get("id") for x in rows if type(x) is dict)==CASES,
         "Exactly 18 ordered D5 Player cases")
    for c in rows:
        need(type(c) is dict and
             set(c)=={"id","phase","sourceClass","historicalSource",
                       "d5RealPlayerProducerLinked","d5RealPlayerProof",
                       "mayRunLocally","preApprovalNeed"} and
             c["sourceClass"] in ("HistoricalPlayerControl",
                                  "ExactSourceHostOnly","MissingD5Producer") and
             type(c["phase"]) is str and c["phase"] and
             type(c["preApprovalNeed"]) is str and c["preApprovalNeed"] and
             c["d5RealPlayerProducerLinked"] is False and
             c["d5RealPlayerProof"]=="NoCoverage" and
             c["mayRunLocally"] is False,
             "Fixture cannot assert unperformed Unity/IL2CPP Player proof")
        source=c["historicalSource"]
        need(source is None or
             (c["sourceClass"]=="HistoricalPlayerControl" and
              source in p["sourceGitBlobs"]["hybridclr_demo"]),
             "Historical Player source not verified by current source profile")
    need(f.get("mandatoryUnproven")==[
             "D5-C07","D5-C08","D5-C09","D5-C10","D5-C13","D5-C17"] and
         len(f.get("expectedPhaseOrder",[]))==8 and
         f["expectedPhaseOrder"][0]=="P0 Prepared" and
         f["expectedPhaseOrder"][-1]=="Complete",
         "Critical phase/GC/P5–P6 coverage gap omitted")
    need(f.get("authority")=={
        "D5A":"ApprovedByUser","D5B":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION","R03Accepted":False},
        "Local fixture handoff illegally enabled")
    return f

def code(raw):
    return re.sub(r"//[^\n]*|/\*[\s\S]*?\*/","",raw)

def ordered(text, chunks, label):
    positions=[text.find(item) for item in chunks]
    need(all(x>=0 for x in positions) and
         positions==sorted(positions) and len(set(positions))==len(chunks),
         "Source phase/ownership order violated: "+label)

def validate_native_boundary(inventory):
    native=inventory["il2cpp_plus"]
    hybrid=inventory["hybridclr"]
    demo=inventory["hybridclr_demo"]
    shadow=code(native["libil2cpp/vm/AssemblyShadow.cpp"])
    owner=code(native["libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h"])
    start=shadow.find("bool PublishActive(void* context)")
    stop=shadow.find("\n    void CopyDetail(",start)
    need(start>=0 and stop>start,"D4 PublishActive missing")
    ordered(shadow[start:stop],[
        "activeOwner.TryPublish(","Phase::ActiveSnapshotPublished",
        "PublicationLeaseExit::ActivePublished"],"P4→P5 ownership")
    ordered(owner,["retained_ = std::move(pending);",
        "published.store(retained_.get(), std::memory_order_release);"],
        "ProcessSnapshotOwner retained pointer")
    need("if (!pending || retained_ || published.load(" in owner and
         "ProcessSnapshotOwner<ActiveSnapshot> activeOwner;" in shadow and
         "static Transaction* transaction = new Transaction();" in shadow,
         "Process-lifetime unique owner absent")
    a=shadow.find("AssemblyShadowError AssemblyShadow::CommitTransaction()")
    b=shadow.find("AssemblyShadowError AssemblyShadow::AbortTransaction()",a)
    need(a>=0 and b>a,"Actual native CommitTransaction missing")
    commit=shadow[a:b]
    need("publication.pendingSnapshot = &snapshot;" in commit and
         "snapshot.release()" not in commit and
         "ScopedPostActiveExit postActiveExit(publicationPhase);" in commit and
         "Phase::InitializersRunning" in commit and
         "publicationPhase.Complete()" in commit,
         "P5/P6/Complete/exception owner custody changed")
    a=shadow.find("void ReleasePublicationUsage(void* context)")
    b=shadow.find("bool TryBeginPublication(void* context)",a)
    need(a>=0 and b>a,"D3 usage lock callback unavailable")
    ordered(shadow[a:b],["SealFailedPublicationBeforeUsageUnlock(publication);",
        "UnlockUsage();"],"D3 terminal-before-usage-unlock")
    need("~ScopedPhysicalRollback() noexcept" in
         code(native["libil2cpp/vm/Assembly.cpp"]) and
         "~ScopedCliRollback() noexcept" in
         code(native["libil2cpp/vm/MetadataCache.cpp"]),
         "D2 physical/CLI rollback source changed")
    ordered(code(hybrid["hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp"]),[
        "observer->beforeCodec(observer->context)",
        "current->codec.PublishBatch(current->publishScratch, count)",
        "current->groups[group].active.store(1, std::memory_order_release)",
        "observer->afterRuntimeGroup(observer->context)"],"actual Runtime P3/P4")
    build=code(demo["Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs"])
    for term in ('Application.unityVersion != "2022.3.62f2"',
                 "ScriptingImplementation.IL2CPP",
                 "BuildPipeline.BuildPlayer(", "BuildOptions.Development",
                 "PrebuildCommand.GenerateAll();",
                 "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW="):
        need(term in build,"Real Unity builder baseline changed: "+term)
    old=read_json(demo["Tools/AssemblyShadow/R03IR/current_native_candidate.json"].encode())
    gate=demo["Tools/AssemblyShadow/R03IR/current_native_source_gate.py"]
    runner=demo["Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py"]
    need(old.get("candidateNativePin")==LEGACY_NATIVE and
         old.get("hybridclrPin")==LEGACY_HYBRID and
         LEGACY_NATIVE in gate and LEGACY_HYBRID in gate and
         "== len(source.FILES) == 14" in runner and
         "== len(delta.EXPECTED_VM_NAMES) == 46" in runner,
         "Historical B1 exact 14/46 admission contract was altered")
    test=native["NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"]
    need("void* operator new(std::size_t" in test and
         "void operator delete(void*" in test and
         "NativeHostTests/" not in shadow,
         "Global allocator host driver must not be installed into libil2cpp")

def read_only_output_guard(roots, output, historical=()):
    need(output.is_absolute() and output.name.startswith("R03-B2-D5-") and
         output.name!="R03-B2-D5-" and not output.exists() and
         not output.is_symlink() and ".." not in output.parts and
         output.parent.is_dir() and not output.parent.is_symlink() and
         output.parent.resolve(strict=True)==output.parent,
         "D5 Local evidence must use a new absent canonical one-use path")
    out=output.resolve(strict=False)
    for root in list(roots.values())+list(historical):
        if root.exists():
            x=root.resolve(strict=True)
            need(x!=out and x not in out.parents and out not in x.parents,
                 "Evidence root intersects a source or historical root")
    return True

def canonical_remote(value, role):
    slug="night-outlook/"+role
    return value in ("https://github.com/"+slug,
        "https://github.com/"+slug+".git",
        "git@github.com:"+slug,"git@github.com:"+slug+".git",
        "ssh://git@github.com/"+slug,
        "ssh://git@github.com/"+slug+".git")

def git(root,*args):
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,
                     text=True,timeout=45,check=False)
    need(p.returncode==0,"Git command failed: "+" ".join(args)+
         " "+p.stderr[-200:])
    return p.stdout.strip()

def validate_git_checkout(root,role,sha):
    need(root.is_absolute() and root.is_dir() and not root.is_symlink() and
         root.resolve(strict=True)==root,
         "Absolute physically canonical root required for "+role)
    need(git(root,"rev-parse","--show-toplevel")==str(root),
         "Repo root mismatch for "+role)
    need(git(root,"rev-parse","HEAD")==sha,
         "Exact pinned commit mismatch for "+role)
    need(canonical_remote(git(root,"remote","get-url","origin"),role),
         "Canonical GitHub remote mismatch for "+role)
    checkout_branch=git(root,"branch","--show-current")
    need(checkout_branch in ("",BRANCH),"Unexpected source branch for "+role)
    need(not git(root,"status","--porcelain=v1","--untracked-files=all"),
         "Dirty source tree: "+role)
    return {"commit":sha,"repository":"night-outlook/"+role,
            "branch":checkout_branch or "DetachedPinnedCommit",
            "canonicalRemote":True,"clean":True}

def audit_source_bytes(roots,profile):
    files={}
    count=0
    for role in REPOS:
        files[role]={}
        for path,sha in profile["sourceGitBlobs"][role].items():
            f=roots[role]/path
            need(f.is_file() and not f.is_symlink(),
                 "Required source absent or symlinked: "+role+"/"+path)
            data=f.read_bytes()
            need(not data.startswith(b"version https://git-lfs.github.com/spec/v1"),
                 "Unmaterialized LFS pointer: "+path)
            need(git_blob(data)==sha and
                 git(roots[role],"rev-parse","HEAD:"+path)==sha,
                 "Source blob mismatch: "+role+"/"+path)
            files[role][path]=data.decode("utf-8-sig")
            count+=1
    return files,count

def inspect(roots,demo_head):
    need(type(demo_head) is str and HEX.fullmatch(demo_head),
         "Expected exact latest demo SHA argument")
    need(set(roots)==set(REPOS) and len(set(roots.values()))==4,
         "Exactly four distinct source checkouts required")
    need(len({r.parent for r in roots.values()})==1,
         "Four source roots must be siblings")
    demo=roots["hybridclr_demo"]
    raw=(demo/PROFILE).read_bytes()
    f_raw=(demo/FIXTURES).read_bytes()
    need(git_blob(raw)==PROFILE_BLOB and
         git_blob(f_raw)==FIXTURE_BLOB,
         "Immutable D5-A profile/fixture Git bytes changed")
    profile=validate_profile(read_json(raw))
    fixtures=validate_fixture(read_json(f_raw),profile)
    expected={"hybridclr_demo":demo_head,**PINS}
    checkouts={role:validate_git_checkout(roots[role],role,expected[role])
               for role in REPOS}
    sources,count=audit_source_bytes(roots,profile)
    validate_native_boundary(sources)
    return {"schemaVersion":1,"kind":"R03B2D5AReadOnlySourceGateReceiptV1",
            "result":"PassedD5ASourceOnly_NoUnityOrLocal",
            "branch":BRANCH,"repositories":checkouts,
            "sourceFilesVerified":count,
            "sourceRoles":{k:len(v) for k,v in profile["sourceGitBlobs"].items()},
            "profileBlob":PROFILE_BLOB,"fixtureBlob":FIXTURE_BLOB,
            "historicalB1Preserved":True,
            "sourceOnlyNativeRosterAuthenticated":True,
            "installedUnityNativeSourceValidated":False,
            "UnityOrPlayerExecuted":False,
            "realD5PlayerCellsPassed":0,
            "D5PlayerCellsNoCoverage":len(fixtures["cases"]),
            "D5A":"ApprovedByUser","D5B":"NotAuthorized",
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
            "R03Accepted":False,"H2Passed":False,
            "ReadyForHumanReviewGate":False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root",type=Path,required=True)
    parser.add_argument("--hybridclr-root",type=Path,required=True)
    parser.add_argument("--package-root",type=Path,required=True)
    parser.add_argument("--native-root",type=Path,required=True)
    parser.add_argument("--expected-demo-head",required=True)
    a=parser.parse_args()
    try:
        roots={"hybridclr_demo":a.demo_root,
               "hybridclr":a.hybridclr_root,
               "hybridclr_unity":a.package_root,
               "il2cpp_plus":a.native_root}
        print(json.dumps(inspect(roots,a.expected_demo_head),
                         indent=2,sort_keys=True))
        return 0
    except (Rejected,OSError,ValueError,UnicodeError,
            subprocess.SubprocessError) as error:
        print(json.dumps({"kind":"R03B2D5AReadOnlySourceGateReceiptV1",
            "result":"BlockedBeforeAnyUnityOrLocalExecution",
            "reason":str(error),"UnityOrPlayerExecuted":False,
            "D5B":"NotAuthorized",
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
            "R03Accepted":False},sort_keys=True),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
