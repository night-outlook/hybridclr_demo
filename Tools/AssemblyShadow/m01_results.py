"""Independently check M01 Player assertions against physical native evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from uuid import UUID

from shadow_tools import VerificationError, read_json, require, safe_file

NAME = "AssemblyA.Implementation.Internal"
TYPE = NAME + ".VersionedPrefabComponent"
BASELINE_MARKER = "BASELINE-INTERNAL"
PATCH_MARKER = "PATCH-P01-INTERNAL"
BUSINESS_NAMES = {"AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", NAME}
NEGATIVE_MODES = {"PreUseType", "PreUseReflection", "PreUsePrefab", "PreUseScene"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(info, shadow, expected_assembly=None):
    require(isinstance(info, dict) and info.get("class") not in (None, "", "0x0", "(nil)"), "Missing physical class")
    assembly = info.get("physicalAssembly", {})
    require(assembly.get("name") == NAME, "Wrong physical component assembly")
    require(assembly.get("isInterpreter") is shadow and assembly.get("matchesShadow") is shadow,
            "Physical object provenance does not match the expected mode")
    if expected_assembly is not None:
        require(assembly.get("assembly") == expected_assembly, "Object header assembly differs from the staged shadow")


def component(probe, shadow, expected_assembly=None):
    require(isinstance(probe, dict) and probe.get("passed") is True, "Component probe failed or missing")
    for field in ("getComponentByName", "getComponentByNameFound", "getComponentByType", "dataReference"):
        require(probe.get(field) is True, "Failed component " + field)
    require(probe.get("missingScript") is False, "Missing Script or missing assertion")
    require(probe.get("serializedValue") == 1234 and probe.get("baseSerializedValue") == 7,
            "Serialized component values changed")
    marker = PATCH_MARKER if shadow else BASELINE_MARKER
    require(probe.get("result") == "BASELINE-EXT|" + marker + "|1234", "Wrong executable component marker")
    physical(probe.get("nativeObject"), shadow, expected_assembly)
    physical(probe.get("byNameNativeObject"), shadow, expected_assembly)
    require(probe["byNameNativeObject"].get("object") == probe["nativeObject"].get("object"),
            "String lookup returned a different physical component")


def verify_result(path, shadow):
    result = read_json(path)
    require(result.get("milestone") == "M01" and result.get("il2cpp") is True, "Not a real M01 IL2CPP result")
    require(result.get("mode") == ("P01" if shadow else "Baseline") and result.get("result") == "Passed",
            "Wrong mode or failed Player")
    require(result.get("gate") == ("CONDITIONAL-GO" if shadow else "BASELINE-PASS"), "Wrong or overstated Player gate")
    require(result.get("nativeFeatureEnabled") is True and result.get("originalBundlesUnchanged") is True,
            "Native feature or immutable bundle check absent")
    native_path = Path(result["nativeDiagnosticsPath"])
    require(digest(native_path) == result["nativeDiagnosticsSha256"], "Native diagnostics hash mismatch")
    native = read_json(native_path)
    require(native.get("enabled") is True and native.get("active") is shadow, "Wrong native activation state")
    shadow_pointer = None
    if shadow:
        base, patch = native.get("baseline", {}), native.get("shadow", {})
        shadow_pointer = patch.get("assembly")
        require(base.get("name") == NAME and patch.get("name") == NAME and
                base.get("isInterpreter") is False and patch.get("isInterpreter") is True,
                "Native baseline/shadow assembly pairing invalid")
        require(base.get("assembly") != shadow_pointer and shadow_pointer not in (None, "", "0x0", "(nil)"),
                "Physical assemblies are not distinct")
        require(result.get("baselineUsesBeforeActivate") == [], "Positive run used baseline business types before activation")
    reflection = result.get("reflection", {})
    require(reflection.get("passed") is True and reflection.get("typeAssemblyIdentity") is True,
            "Reflection identity/probe failed")
    require(reflection.get("moduleMvidSupported") is False and not reflection.get("moduleMvid") and
            bool(reflection.get("moduleMvidNote")), "Unsupported IL2CPP module MVID API must be reported honestly")
    require(reflection.get("result") == (PATCH_MARKER if shadow else BASELINE_MARKER), "Reflection did not execute expected body")
    physical(reflection.get("instance"), shadow, shadow_pointer)
    if shadow:
        require(reflection.get("assembly", {}).get("assembly") == shadow_pointer,
                "Assembly.Load returned a different physical assembly")
    component(result.get("prefab"), shadow, shadow_pointer)
    scene = result.get("scene", {})
    require(scene.get("passed") is True and scene.get("derivedConsumerAot") is True and
            scene.get("derivedConsumerResult") == "BASELINE-EXT", "Scene/AOT consumer failed")
    component(scene.get("firstLoad"), shadow, shadow_pointer)
    component(scene.get("reload"), shadow, shadow_pointer)
    data = result.get("scriptableObject", {})
    require(data.get("passed") is True and data.get("serializedValue") == 5678 and data.get("result") == "BASELINE-DATA",
            "ScriptableObject serialized data or unchanged method differs")
    physical(data.get("nativeObject"), shadow, shadow_pointer)
    if shadow:
        events = native.get("events", [])
        for phase in ("prefab", "scene-first", "scene-reload"):
            matches = [event for event in events if event.get("phase") == phase and event.get("type") == TYPE and
                       event.get("site") == "Object::New.input" and event.get("isInterpreter") is True and
                       event.get("assembly") == shadow_pointer]
            require(matches and any(event.get("stack") for event in matches),
                    "Missing real native creation stack for " + phase)
    return result, native


def verify_player_evidence(path, baseline_root, manifest):
    evidence = read_json(path)
    require(evidence.get("schemaVersion") == 1 and evidence.get("milestone") == "M01",
            "Invalid Player assembly evidence schema")
    for field in ("unityVersion", "target", "architecture"):
        require(evidence.get(field) == manifest.get(field), "Player input platform differs: " + field)
    require(evidence.get("baselineManifestSha256") == digest(baseline_root / "baseline-manifest.json"),
            "Player inputs used a different frozen baseline manifest")
    require(digest(Path(evidence["gameAssemblyPath"])) == evidence.get("gameAssemblySha256"),
            "Built native Player library differs from captured assembly inputs")
    assemblies = evidence.get("assemblies", [])
    require(len(assemblies) == len(BUSINESS_NAMES) and {item.get("name") for item in assemblies} == BUSINESS_NAMES,
            "Player stripped AOT input inventory differs")
    expected = {item["name"]: item for item in manifest.get("assemblies", [])}
    require(set(expected) == BUSINESS_NAMES, "Frozen AOT assembly inventory differs")
    for item in assemblies:
        baseline = expected[item["name"]]
        require(digest(Path(item["path"])) == item.get("sha256"), "Captured stripped AOT DLL changed: " + item["name"])
        require(digest(safe_file(baseline_root, baseline["path"])) == baseline["sha256"],
                "Frozen baseline DLL changed: " + item["name"])
        require(item.get("baselineMvid") == baseline["mvid"] and item.get("baselineSha256") == baseline["sha256"],
                "Player input baseline pairing differs: " + item["name"])
        require(UUID(item["mvid"]).int != 0, "Missing stripped Player input MVID: " + item["name"])
        require(item.get("matchesBaselineMvid") is (item["mvid"] == baseline["mvid"]),
                "Incorrect stripped/baseline MVID comparison: " + item["name"])
        require(item.get("matchesBaselineSemantics") is True and
                item.get("comparisonPolicy") == "same-types-fields-method-signatures-and-il",
                "Stripped Player input semantics differ from frozen baseline: " + item["name"])
    return evidence


def verify_negative_result(path, baseline_manifest_sha, patch_dll_sha):
    observed = read_json(path)
    uses = observed.get("baselineUsesBeforeActivate", [])
    require(observed.get("mode") in NEGATIVE_MODES and observed.get("il2cpp") is True and uses,
            "Negative timing run has no real pre-use witness")
    require(observed.get("nativeFeatureEnabled") is True and observed.get("originalBundlesUnchanged") is True,
            "Negative timing run did not finish immutable-resource probes")
    require(observed.get("baselineManifestSha256") == baseline_manifest_sha and
            observed.get("patchDllSha256") == patch_dll_sha, "Negative timing run used different artifacts")
    require(observed.get("result") in ("Passed", "Failed"), "Negative run has no completed result")
    native_path = Path(observed["nativeDiagnosticsPath"])
    require(digest(native_path) == observed.get("nativeDiagnosticsSha256"), "Negative native trace hash mismatch")
    native = read_json(native_path)
    require(native.get("enabled") is True and native.get("active") is True and
            native.get("moduleInitializerRun") is False, "Negative run did not activate the prototype normally")
    require(observed.get("reflection", {}).get("passed") is True, "Negative run failed before post-activation reflection")
    for use in uses:
        resource_use = observed["mode"] in ("PreUsePrefab", "PreUseScene")
        info = ((use.get("objectBefore") or {}).get("physicalAssembly") if resource_use else use.get("assemblyBefore"))
        require(info and info.get("name") == NAME and info.get("isInterpreter") is False,
                "Negative timing witness was not baseline AOT")
        if resource_use:
            before, after = use.get("objectBefore"), use.get("objectAfterActivate")
            physical(before, False)
            physical(after, False)
            require(before.get("object") == after.get("object") and before.get("class") == after.get("class"),
                    "Previously created baseline object was replaced or retyped")
            require(use.get("resultAfterActivate") == "BASELINE-EXT|BASELINE-INTERNAL|1234",
                    "Previously created baseline object no longer executes its original body")
    return {"mode": observed["mode"], "result": observed["result"], "uses": uses}


def verify(baseline_root, baseline_result, patch_result, patch_dll, player_evidence, negative_results=()):
    manifest = read_json(baseline_root / "baseline-manifest.json")
    require(manifest.get("schemaVersion") == 1, "Invalid baseline schema")
    inputs = verify_player_evidence(player_evidence, baseline_root, manifest)
    bundles = manifest.get("bundles", [])
    require({item["name"] for item in bundles} == {"business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle"},
            "Baseline bundle inventory differs")
    for item in bundles:
        path = safe_file(baseline_root, item["path"])
        require(digest(path) == item["sha256"], "First-build bundle changed: " + item["name"])
        require(path.stat().st_mode & 0o222 == 0, "Baseline bundle is not read-only: " + item["name"])
    baseline, _ = verify_result(baseline_result, False)
    patch, native = verify_result(patch_result, True)
    for result in (baseline, patch):
        require(result.get("baselineManifestSha256") == digest(baseline_root / "baseline-manifest.json"), "Player used a different baseline manifest")
        require(result.get("baselineBundleSha256") == bundles, "Player did not use the original bundle hashes")
    require(patch.get("patchDllSha256") == digest(patch_dll), "Player used a different P01 DLL")
    internal = next((item for item in manifest.get("assemblies", []) if item.get("name") == NAME), None)
    require(internal is not None and digest(safe_file(baseline_root, internal["path"])) == internal["sha256"], "Baseline DLL snapshot changed")
    require(patch.get("baselineMvid") == internal["mvid"] and patch.get("patchMvid") != internal["mvid"], "Patch MVID pairing invalid")
    # RuntimeAssembly.GetManifestModuleInternal deliberately throws in this pinned
    # IL2CPP version. Runtime identity is proven by native physical pointers; PE
    # MVIDs belong to the separately verified build/patch input evidence.
    negatives = [verify_negative_result(path, digest(baseline_root / "baseline-manifest.json"), digest(patch_dll))
                 for path in negative_results]
    require(len(negatives) == len(NEGATIVE_MODES) and {item["mode"] for item in negatives} == NEGATIVE_MODES,
            "All four distinct pre-activation timing observations are required")
    return {"verified": True, "gate": "CONDITIONAL-GO", "baselineBuildId": manifest["baselineBuildId"],
            "bundleCount": len(bundles), "patchDllSha256": digest(patch_dll),
            "gameAssemblySha256": inputs["gameAssemblySha256"],
            "runtimeMvidSupported": False, "aotInputMvidsRecorded": True, "aotInputSemanticsVerified": True,
            "nativeEventCount": len(native["events"]), "negativeTimingObservations": negatives,
            "scope": "macOS ARM64 IL2CPP P01 only; final gate also requires independent native-path review"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--baseline-result", type=Path, required=True)
    parser.add_argument("--patch-result", type=Path, required=True)
    parser.add_argument("--patch-dll", type=Path, required=True)
    parser.add_argument("--player-assemblies", type=Path, required=True,
                        help="Build-time stripped AOT DLL and native library evidence receipt")
    parser.add_argument("--negative-result", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify(args.baseline_root.resolve(), args.baseline_result, args.patch_result, args.patch_dll,
                        args.player_assemblies, args.negative_result)
        output = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output)
        print(output, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
