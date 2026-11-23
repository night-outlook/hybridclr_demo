#!/usr/bin/env python3
"""D5-C10 native source→object→binary evidence MATERIAL verifier, not execution.

The positive result proves supplied files/digests/command text are internally
consistent. Logs, BuildReceipt and nm dumps are UNTRUSTED inputs; the verifier
does not execute Unity, Bee, compiler, nm, or a Player and NEVER attests them.
An independent Local reviewer must authenticate raw producer/linked binary/PID.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

PINSET = Path(__file__).resolve().with_name("d5c10_link_source_pinset_v1.json")
PINSET_BLOB = "fe531a9ab5a585a4b2e0217a1db236fb9ae0b4a0"
BRANCH = "codex/assembly-shadow-r01b-h1"
NATIVE = "87a34bbea39930dab96cf4703756d8da79d54684"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
EXPECTED_TUS = (
    "vm/Assembly.cpp",
    "vm/AssemblyShadow.cpp",
    "vm/MetadataCache.cpp",
    "vm/Runtime.cpp",
    "vm/AssemblyShadowD5WindowOverlay.cpp",
)
EXPORTS = ("R03_D5_WindowProtocolVersion","R03_D5_ArmP5Window",
           "R03_D5_ReleaseP5Window","R03_D5_ReadP5Window",
           "R03_D5_ReceiptOpen","R03_D5_ReceiptEvent",
           "R03_D5_BindKeepCanary","R03_D5_ReceiptSeal",
           "R03_D5_BeginKeepAttempt")
ALLOWED_STATES = ("SyntheticSourceHost",)  # NO real-Player claims under D5-B prep


class Rejected(ValueError):
    pass


def require(ok, message):
    if not ok: raise Rejected(message)


def read_obj(raw: bytes):
    def pairs(rows):
        o={}
        for k,v in rows:
            require(k not in o, "Duplicate JSON key: "+k)
            o[k]=v
        return o
    x=json.loads(raw,object_pairs_hook=pairs)
    require(type(x) is dict,"JSON object required")
    return x


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\0" + data).hexdigest()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_pinset(raw: bytes) -> dict:
    require(git_blob(raw)==PINSET_BLOB,"D5 C10 pinset Git blob has drifted")
    x=read_obj(raw)
    require(x.get("schemaVersion")==1 and
            x.get("kind")=="R03D5C10NativeLinkSourcePinsetV1" and
            x.get("branch")==BRANCH, "Wrong native provenance schema")
    pins=x.get("sourcePins")
    require(type(pins) is dict and set(pins)==set(ROLES) and
            pins["il2cpp_plus"]==NATIVE and
            pins["hybridclr"]=="c3c232023724cbad565b85e9b2c3beea8ce2789a" and
            pins["hybridclr_unity"]=="948c0e3b4f8891481301770115e8ba4945eea6de" and
            pins["hybridclr_demo"]==
                "DEMO_HEAD_FROM_GITHUB_ACTIONS_AND_FUTURE_APPROVED_HANDOFF",
            "Four original approved source roles have drifted")
    inputs=x.get("nativeInstalledSources")
    require(type(inputs) is dict and len(inputs)==13 and
            all(type(k) is str and type(v) is str and
                HEX40.fullmatch(v) for k,v in inputs.items()),
            "All 13 actual native source/header Git blobs required")
    require(x.get("compiledTranslationUnits")==list(EXPECTED_TUS) and
            x.get("overlayInstallDestination")==EXPECTED_TUS[-1] and
            x.get("expectedExportSymbols")==list(EXPORTS),
            "Native actual translation-unit/overlay/export roster changed")
    require(x.get("excludedSource")==[
            "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"],
            "Standalone allocator host source must stay outside linked inputs")
    require(x.get("authority")=={
        "D5BLocalExecution":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted":False,"H2Passed":False,
        "ReadyForHumanReviewGate":False},
        "Unreviewed D5-B authorization")
    return x


def canonical_dir(path: Path,label: str) -> Path:
    require(path.is_absolute() and path.is_dir() and not path.is_symlink()
            and path.resolve(strict=True)==path,
            "Non-symlink absolute canonical root required for "+label)
    return path


def safe_relative(base: Path, name: str) -> Path:
    require(type(name) is str and name and
            not name.startswith("/") and "\\" not in name and
            not ".." in PurePosixPath(name).parts,
            "Relative material path must not traverse directories")
    p=base.joinpath(*PurePosixPath(name).parts)
    require(p.is_file() and not p.is_symlink() and
            p.resolve(strict=True)==p and base in p.parents,
            "Material must be a regular canonical file inside its root: "+name)
    return p


def files_with_sha(root: Path, names: dict[str,str]) -> dict[str,str]:
    found={}
    for name,blob in names.items():
        data=safe_relative(root,name).read_bytes()
        require(git_blob(data)==blob,"Wrong installed/native Git blob: "+name)
        found[name]=sha(data)
    return found


def check_native_installed_source(
        native_checkout: Path, installed_native: Path,
        pinset: dict) -> dict:
    native_checkout=canonical_dir(native_checkout,"native Git source")
    installed_native=canonical_dir(installed_native,"installed native copy")
    expected=pinset["nativeInstalledSources"]
    src=files_with_sha(native_checkout,{"libil2cpp/"+k:v for k,v in expected.items()})
    actual={}
    for rel in expected:
        data=safe_relative(installed_native,rel).read_bytes()
        h=sha(data)
        require(h==src["libil2cpp/"+rel],
                "Installed native byte identity mismatch: "+rel)
        actual[rel]=h
    excluded=installed_native/"NativeHostTests"/"AssemblyShadowFirstFailureV2Host.cpp"
    require(not excluded.exists() and not excluded.is_symlink(),
            "Standalone global allocator test entered installed native root")
    return actual


def check_submitted_link_material(
        evidence_root: Path, native_checkout: Path,
        installed_native: Path, overlay_source: Path,
        pinset: dict, envelope: dict) -> dict:
    """Verify synthetic/replayed materials; NEVER claim actual Unity/Player."""
    evidence_root=canonical_dir(evidence_root,"evidence bundle")
    canonical_dir(native_checkout,"native Git source")
    canonical_dir(installed_native,"installed native copy")
    require(envelope.get("schemaVersion")==1 and
            envelope.get("kind")=="R03D5C10LinkMaterialBundleV1" and
            envelope.get("evidenceClass")=="SyntheticSourceHost",
            "Only explicitly synthetic bundles may be analyzed before Local")
    require(envelope.get("sourcePins")==pinset["sourcePins"] and
            envelope.get("buildRole")=="ON-Release" and
            envelope.get("target")=="macOS-arm64-Unity2022.3.62f2-IL2CPP",
            "Bundle has unreviewed source role or platform")
    native_hashes=check_native_installed_source(
        native_checkout,installed_native,pinset)
    require(overlay_source.is_file() and not overlay_source.is_symlink(),
            "Exact original D5 overlay source file missing")
    overlay_bytes=overlay_source.read_bytes()
    overlay_name="Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp"
    require(git_blob(overlay_bytes)==pinset["isolatedOverlaySource"][overlay_name],
            "D5 overlay Git source changed")
    installed_overlay=safe_relative(installed_native,
                                    pinset["overlayInstallDestination"])
    require(installed_overlay.read_bytes()==overlay_bytes,
            "Linked-candidate overlay source bytes changed")

    record=read_obj(safe_relative(evidence_root,
                         envelope.get("buildReceipt","")).read_bytes())
    require(record.get("kind")=="R03D5C10IsolatedUnityBuildV1" and
            record.get("result")=="BuildPipelineSucceeded_NotYetBinaryVerified" and
            record.get("unityVersion")=="2022.3.62f2" and
            record.get("featureEnabled") is True and
            record.get("cppConfiguration")=="Release" and
            record.get("actualUnityBuildPipelineInvoked") is True and
            record.get("actualUnityBuildReportSucceeded") is True and
            record.get("independentLinkedBinaryProof") is False and
            record.get("actualD5PlayerRun") is False and
            record.get("R03Accepted") is False and
            record.get("nativeCommit")==NATIVE,
            "Submitted BuildReport claims/bound identities inconsistent")
    flags=record.get("compilerFlags","")
    require("-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1" in flags and
            "-DHYBRIDCLR_R03_D5_WINDOW_PROBE=1" in flags and
            "-DHYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1" in flags,
            "Compiled-source probe feature flags missing")
    observations=record.get("requiredNativeFileHashes")
    require(type(observations) is list and
            len(observations)==len(native_hashes) and
            {row["path"]:row["sha256"] for row in observations
             if type(row) is dict}==native_hashes,
            "Native source install receipt list does not match actual bytes")
    require(record.get("overlayInstalledSha256")==sha(overlay_bytes),
            "Native overlay installed hash does not match source")

    compiled=envelope.get("compiledInputs")
    require(type(compiled) is list and len(compiled)==len(EXPECTED_TUS) and
            {x.get("source") for x in compiled if type(x) is dict} ==
                set(EXPECTED_TUS),"One compile-source record per required TU")
    expected_commands={}
    for row in compiled:
        src=row["source"]
        obj_path=row.get("object")
        obj=safe_relative(evidence_root,obj_path)
        require(type(row.get("objectSha256")) is str and
                sha(obj.read_bytes())==row["objectSha256"],
                "Compiled object output bytes/digest missing: "+src)
        command=safe_relative(evidence_root,row.get("command")).read_text(
            encoding="utf-8")
        require(src in command and obj_path in command and
                "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1" in command and
                "-DHYBRIDCLR_R03_D5_WINDOW_PROBE=1" in command and
                 "-DHYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1" in command,
                "Raw compiler command does not bind input/object/feature: "+src)
        require("NativeHostTests/" not in command,
                "Standalone global allocator test compiled")
        expected_commands[src]=sha(command.encode("utf-8"))
    link=safe_relative(evidence_root,envelope.get("linkCommand")).read_text(
        encoding="utf-8")
    require(all(x["object"] in link for x in compiled) and
            "NativeHostTests/" not in link,
            "Link command lacks native TU objects or contains standalone host")
    binary=safe_relative(evidence_root,envelope.get("linkedBinary"))
    raw=binary.read_bytes()
    require(len(raw)>=64 and raw[:4] in
                (b"\xcf\xfa\xed\xfe",b"\xca\xfe\xba\xbe"),
            "Target does not present a 64-bit/FAT Mach-O file header")
    require(sha(raw)==envelope.get("linkedBinarySha256"),
            "Linked binary SHA-256 does not match its material")
    symbols=safe_relative(evidence_root,envelope.get("nmSymbols")).read_text(
        encoding="utf-8")
    actual={line.split()[-1].lstrip("_") for line in symbols.splitlines()
            if line.strip() and len(line.split())>=2}
    require(set(EXPORTS).issubset(actual),
            "Required four test-only native overlay exports absent from supplied nm text")
    return {
        "schema":"R03D5C10LinkMaterialCheckV1",
        "result":"SyntheticMaterialCoherent_NotIndependentUnityBuild",
        "nativeSourcesMatched":len(native_hashes),
        "compiledInputRecordsMatched":len(compiled),
        "linkedBinarySha256":sha(raw),
        "exportSymbolsMatched":len(EXPORTS),
        "nativeEvidenceWriterCompileVerified":False,
        "nativeVMEvidenceCaptureVerified":False,
        "rawCompilerCommandHashes":expected_commands,
        "actualUnityOrIL2CPPExecutionVerified":False,
        "actualBeeCompilerCommandExecutionVerified":False,
        "realPlayerC10Passed":False,
        "D5BLocalExecution":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION","R03Accepted":False
    }


def preview() -> dict:
    pinset=source_pinset(PINSET.read_bytes())
    return {"schema":"R03D5C10LinkMaterialCheckV1",
            "result":"SourceOnlyProvenanceContract_NotRun",
            "sourcePins":pinset["sourcePins"],"nativeInputCount":13,
            "compiledTranslationUnitIntentCount":5,
            "actualUnityOrIL2CPPExecutionVerified":False,
            "actualBeeCompilerCommandExecutionVerified":False,
            "realPlayerC10Passed":False,
            "D5BLocalExecution":"NotAuthorized",
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION","R03Accepted":False}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-preview-only",action="store_true",required=True)
    p.parse_args()
    try:
        print(json.dumps(preview(),sort_keys=True))
        return 0
    except (Rejected,OSError,ValueError) as error:
        print(json.dumps({"result":"BlockedSourceOnly",
            "reason":str(error),"D5BLocalExecution":"NotAuthorized",
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION"},sort_keys=True),
            file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
