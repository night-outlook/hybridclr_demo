"""Synthetic evidence tests, not Player acceptance. Every mutation starts from a passing suite.

Bytes deliberately are not PE files: PE/semantic verification is the separately
bound Editor replay's responsibility. The Python verifier checks observations,
cross-artifact identities and the exact shared snapshot hash algorithms.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m03_results as verifier
from shadow_tools import VerificationError


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, separators=(",", ":")), encoding="utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def uid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, value))


class SyntheticSuite:
    def __init__(self, root):
        self.root = root.resolve()
        self.results = self.root / "results"
        self.results.mkdir()
        self.fixture_path = self.root / "fixtures" / "m03-fixtures.json"
        self.baseline_path = self.root / "baseline" / "baseline-manifest.json"
        self.stable = ["assemblyshadowdemo.bootstrap", "mscorlib"]
        self.pins = {"schemaVersion": 1, "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64"}
        for i, repo in enumerate(("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"), 1):
            self.pins[repo] = {"url": "https://example.invalid/" + repo, "revision": str(i) * 40}
        self.abi = verifier._runtime_abi_hash(self.pins, "synthetic")
        self.build_id = "M03-Baseline-synthetic-tests"
        self.on = self.snapshot("on", player=True)
        self.off = self.snapshot("off", player=True)
        self.baseline = {
            "schemaVersion": 1, "semanticHashSchema": 1, "baselineBuildId": self.build_id,
            "runtimeAbiHash": self.abi, "sourcePins": self.pins,
            "unityVersion": self.pins["unityVersion"], "target": "StandaloneOSX", "architecture": "arm64",
            "shadowCandidates": list(verifier.CANDIDATES), "bootstrapAssemblies": ["AssemblyShadowDemo.Bootstrap"],
            "bootstrapAbiHash": sha(b"bootstrap-abi"), "resourceAbiHash": sha(b"resource-abi"),
            "playerInputSnapshotHash": self.on[1]["snapshotHash"], "playerBuildGuid": self.on[1]["buildGuid"],
            "nativeLibrarySha256": self.on[1]["nativeLibrarySha256"],
            "assemblies": [{"name": name, "mvid": uid("baseline/" + name)} for name in verifier.CANDIDATES],
        }
        write_json(self.baseline_path, self.baseline)
        self.patch_docs, fixtures = {}, []
        for patch_id in ("P01", "P03", "P03-InitializerThrow"):
            defines = ["ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01"]
            if patch_id != "P01":
                defines += ["ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03"]
            if patch_id.endswith("Throw"):
                defines += ["ASSEMBLY_SHADOW_M03_INITIALIZER_THROW"]
            compile_root, compiled = self.snapshot(patch_id + "-compile", defines=defines)
            patch_root = self.fixture_path.parent / patch_id
            patch_root.mkdir(parents=True)
            order = [verifier.INTERNAL] if patch_id == "P01" else list(verifier.CANDIDATES)
            closure = []
            for name in reversed(order):  # closure is a SET; loadOrder alone determines execution.
                source = next(a for a in compiled["assemblies"] if a["name"] == name)
                for relative in (source["path"], source["pdbPath"]):
                    target = patch_root / relative
                    target.parent.mkdir(exist_ok=True)
                    target.write_bytes((compile_root / relative).read_bytes())
                closure.append({"name": name, "dll": source["path"], "sha256": source["sha256"],
                                "pdb": source["pdbPath"], "pdbSha256": source["pdbSha256"],
                                "mvid": uid(patch_id + "/" + name), "baselineMvid": uid("baseline/" + name)})
            patch = {key: self.baseline[key] for key in ("schemaVersion", "semanticHashSchema", "baselineBuildId", "runtimeAbiHash", "sourcePins", "unityVersion", "target", "architecture", "bootstrapAbiHash", "resourceAbiHash")}
            patch.update(patchId=patch_id, baselineManifestSha256=verifier.digest(self.baseline_path),
                         baselineResourceAbiHash=self.baseline["resourceAbiHash"], compileSnapshotHash=compiled["snapshotHash"],
                         dllOnly=True, unsigned=True, signatureAlgorithm="None", loadOrder=order, closure=closure, changedRoots=sorted(order))
            patch_path = patch_root / "patch-manifest.json"
            write_json(patch_path, patch)
            (patch_root / "manifest.sha256").write_text(verifier.digest(patch_path) + "\n")
            self.patch_docs[patch_id] = patch
            fixtures.append({"patchId": patch_id, "defines": defines, "changedRoots": order,
                             "compileSnapshot": str(compile_root), "compileSnapshotHash": compiled["snapshotHash"],
                             "patchDirectory": str(patch_root), "patchManifest": str(patch_path),
                             "patchManifestSha256": verifier.digest(patch_path), "closureLoadOrder": order,
                             "stableAotNames": self.stable})
        provenance = "framework=" + sha(b"verified framework") + "\nlinked-player=" + self.on[1]["linkedPlayerReceiptHash"] + "\nbootstrap-policy=assemblyshadowdemo.bootstrap\nphysical=" + ",".join(self.stable)
        self.manifest = {"schemaVersion": 1, "milestone": "M03", "baselineBuildId": self.build_id,
                         "runtimeAbiHash": self.abi, "unityVersion": self.pins["unityVersion"], "target": "StandaloneOSX", "architecture": "arm64",
                         "baselineManifestPath": str(self.baseline_path), "baselineManifestSha256": verifier.digest(self.baseline_path),
                         "baselineInputSnapshot": str(self.on[0]), "baselineInputSnapshotHash": self.on[1]["snapshotHash"],
                         "candidateNames": list(verifier.CANDIDATES), "closureLoadOrder": list(verifier.CANDIDATES),
                         "stableAotNames": self.stable, "stableAotProvenance": provenance,
                         "stableAotProvenanceHash": sha(("m03-stable-aot:1\n" + provenance).encode()), "fixtures": fixtures}
        write_json(self.fixture_path, self.manifest)
        self.replay_path = self.fixture_path.with_name("m03-editor-replay.json")
        replay = {key: self.manifest[key] for key in ("baselineManifestPath", "baselineManifestSha256", "baselineInputSnapshotHash", "baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture", "stableAotProvenanceHash")}
        replay.update(schemaVersion=1, milestone="M03", result="Passed", comparisonPolicy="compiler-linked-policy-graph-resource-abi:1",
                      fixtureManifestPath=str(self.fixture_path), fixtureManifestSha256=verifier.digest(self.fixture_path),
                      playerBuildGuid=self.baseline["playerBuildGuid"], nativeLibrarySha256=self.baseline["nativeLibrarySha256"],
                      linkedPlayerReceiptHash=self.on[1]["linkedPlayerReceiptHash"], validatorSourcePins=self.pins,
                      fixtures=[{k: f[k] for k in ("patchId", "patchManifestSha256", "compileSnapshotHash", "changedRoots", "closureLoadOrder")} for f in fixtures])
        write_json(self.replay_path, replay)
        self.marker_path = self.root / "fallback.json"
        failed = fixtures[2]
        write_json(self.marker_path, {"schemaVersion": 1, "baselineBuildId": self.build_id, "runtimeAbiHash": self.abi,
                                     "baselineManifestSha256": self.manifest["baselineManifestSha256"], "patchId": failed["patchId"],
                                     "patchManifestSha256": failed["patchManifestSha256"], "compileSnapshotHash": failed["compileSnapshotHash"],
                                     "failure": "ModuleInitializerFailed", "state": "FailedAfterCommit", "generation": 1, "businessStarted": False, "processId": 1008})
        for mode in sorted(verifier.REQUIRED_MODES):
            self.write_result(mode, self.result(mode))

    def snapshot(self, label, player=False, defines=None):
        root = self.root / label
        root.mkdir()
        files = []
        for name in (*verifier.CANDIDATES, "AssemblyShadowDemo.Bootstrap", "mscorlib"):
            dll, pdb = root / "Assemblies" / (name + ".dll"), root / "Assemblies" / (name + ".pdb")
            dll.parent.mkdir(exist_ok=True)
            dll.write_bytes(("SYNTHETIC-NOT-PE/" + label + "/" + name).encode())
            pdb.write_bytes(("SYNTHETIC-PDB/" + label + "/" + name).encode())
            files.append({"name": name, "path": str(dll.relative_to(root)), "sha256": verifier.digest(dll),
                          "pdbPath": str(pdb.relative_to(root)), "pdbSha256": verifier.digest(pdb)})
        receipt = {"schemaVersion": 1, "kind": "PlayerBuildInputs" if player else "CompilePlayerScripts",
                   "unityVersion": self.pins["unityVersion"], "target": "StandaloneOSX", "architecture": "arm64", "sourcePins": self.pins,
                   "assemblies": files, "references": [], "filteredAssemblies": [], "extraScriptingDefines": defines or [],
                   "filteredAssemblyCapabilities": [], "normalHotUpdateAssemblies": [], "linkerExcludedAssemblies": [],
                   "linkerExcludedAssemblyCapabilities": [], "playerBuildFilterCaptured": player, "playerBuildOptions": 0,
                   "linkedPlayerReceiptHash": "", "linkedPlayerReceipt": None}
        if player:
            app = self.root / (label + ".app")
            native = app / "Contents" / "MacOS" / "GameAssembly.dylib"
            native.parent.mkdir(parents=True)
            native.write_bytes(("SYNTHETIC-NATIVE/" + label).encode())
            linked = {"schemaVersion": 1, "buildGuid": uid(label).replace("-", ""), "nativeLibrarySha256": verifier.digest(native),
                      "target": "StandaloneOSX", "architecture": "arm64", "sourceDirectory": str(root / "Assemblies"),
                      "protectedAssemblies": sorted([n.casefold() for n in (*verifier.CANDIDATES, "AssemblyShadowDemo.Bootstrap")]), "assemblies": []}
            for entry in files:
                name = entry["name"].casefold()
                dll = root / "LinkedPlayer" / "Assemblies" / (name + ".dll")
                dll.parent.mkdir(parents=True, exist_ok=True)
                dll.write_bytes((root / entry["path"]).read_bytes())
                linked["assemblies"].append({"name": name, "path": "Assemblies/" + name + ".dll", "sha256": verifier.digest(dll),
                                             "mvid": uid("linked/" + name), "pdbPath": "", "pdbSha256": ""})
            write_json(root / "LinkedPlayer" / "linked-player-receipt.json", linked)
            receipt.update(buildId=self.build_id, buildGuid=linked["buildGuid"], nativeLibraryPath=str(native), nativeLibrarySha256=verifier.digest(native),
                           playerOutput=str(app), playerBuildSucceeded=True, linkedPlayerReceipt=linked,
                           linkedPlayerReceiptHash=verifier._snapshot_linked_hash(linked))
        receipt["snapshotHash"] = verifier._snapshot_hash(receipt, root, "synthetic")
        write_json(root / "assembly-snapshot.json", receipt)
        if player:
            write_json(root / "m03-player-build.json", {"schemaVersion": 1, "milestone": "M03", "variant": "NativeOn" if label == "on" else "NativeOff",
                       "baselineBuildId": self.build_id, "runtimeAbiHash": self.abi, "unityVersion": self.pins["unityVersion"], "target": "StandaloneOSX", "architecture": "arm64",
                       "buildGuid": receipt["buildGuid"], "playerOutput": receipt["playerOutput"], "inputSnapshot": str(root), "inputSnapshotHash": receipt["snapshotHash"],
                       "nativeLibraryPath": receipt["nativeLibraryPath"], "nativeLibrarySha256": receipt["nativeLibrarySha256"],
                       "nativeArguments": '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + ("1" if label == "on" else "0") + '"'})
        return root, receipt

    def result(self, mode):
        patch_id = "P03-InitializerThrow" if mode in {"T03-08", "T03-08-Fallback"} else "P03" if mode in {"T03-02", "T03-03", "T03-07", "T03-12", "T03-15"} else "P01"
        patch = self.patch_docs[patch_id]
        fixture = next(f for f in self.manifest["fixtures"] if f["patchId"] == patch_id)
        player = self.off[1] if mode == "T03-09" else self.on[1]
        result = {"schemaVersion": 2, "milestone": "M03", "mode": mode, "result": "Passed", "error": "", "il2cpp": True, "platform": "OSXPlayer",
                  "unityVersion": self.pins["unityVersion"], "baselineBuildId": self.build_id, "runtimeAbiHash": self.abi,
                  "playerBuildGuid": player["buildGuid"], "playerDataPath": str(Path(player["playerOutput"]) / "Contents"),
                  "processId": 2008 if mode.endswith("Fallback") else 1000 + int(mode[-2:]),
                  "baselineManifestSha256": self.manifest["baselineManifestSha256"], "fixtureManifestPath": str(self.fixture_path),
                  "fixtureManifestSha256": verifier.digest(self.fixture_path), "stableAotNames": self.stable, "stableAotProvenanceHash": self.manifest["stableAotProvenanceHash"],
                  "integrityOnlyUnsigned": True, "patchId": patch_id, "patchManifestPath": fixture["patchManifest"],
                  "patchManifestSha256": fixture["patchManifestSha256"], "compileSnapshotHash": fixture["compileSnapshotHash"],
                  "checks": [], "states": [], "snapshots": [], "stageResults": [], "initializerEvents": [], "reentrantQueries": 0,
                  "initializersAfterStage": 0, "initializersAfterValidate": 0, "businessStarted": False, "businessMarker": ""}
        d = {"schemaVersion": 1, "enabled": mode != "T03-09", "runtimeAbiVersion": 1, "state": "Disabled", "stateCode": 0,
             "lastError": 0, "detail": "", "baselineBuildId": "", "patchId": "", "generation": 0, "enumerationGeneration": 0,
             "classEnumerationGeneration": 0, "expected": 0, "staged": 0, "retainedBytes": 0, "closureLoadOrder": [], "stableAotNames": [],
             "commitOrder": [], "assemblies": [], "events": [], "baselineUses": [], "ordinaryClasses": [],
             "ordinaryAssemblies": [{"name": n.lower(), "isInterpreter": False} for n in verifier.CANDIDATES]}

        def code(op, error="Success"):
            result["checks"].append({"operation": op, "actual": error, "expected": error, "actualCode": verifier.ERROR_CODES[error], "expectedCode": verifier.ERROR_CODES[error]})
            d["lastError"] = verifier.ERROR_CODES[error]

        def state(point, value):
            d["state"], d["stateCode"] = value, verifier.STATE_CODES[value]
            result["states"].append(f"{point}:{verifier.STATE_CODES[value]}:{value}")
            result["state"], result["stateCode"] = value, "Success"
            saved = d["lastError"]
            code("state-" + point)
            d["lastError"] = saved

        def snap(point):
            saved = d["lastError"]
            code("diagnostics-" + point)
            d["lastError"] = saved
            result["snapshots"].append({"point": point, "diagnostics": copy.deepcopy(d)})

        def event(kind, name=""):
            d["events"].append({"sequence": len(d["events"]) + 1, "kind": kind, "name": name, "generation": d["generation"], "stagedCount": d["staged"]})

        def abort():
            code("abort"); state("aborted", "Aborted"); event("transaction-aborted"); snap("aborted")
            for op in ("begin-after-abort", "commit-after-abort", "abort-again"):
                code(op, "InvalidState")
            state("aborted-frozen", "Aborted")

        if mode == "T03-09":
            for op in ("configure-null", "begin-null-invalid-abi", "stage-null", "validate", "commit", "abort", "state", "mode-null", "diagnostics", "configure-valid-off", "stage-empty-off"):
                code(op, "FeatureDisabled")
            result.update(patchId="", state="Disabled", stateCode="FeatureDisabled", executionModeCode="FeatureDisabled", executionMode="AotBaseline")
            result["_diag"] = d
            return result
        if mode == "T03-08-Fallback":
            state("fallback-initial", "Disabled"); snap("fallback-before-business")
            code("fallback-unregistered-mode", "CandidateNotRegistered")
            # Native read-only mode query does not change transaction.lastError.
            d["lastError"] = 0
            state("fallback-after-business", "Disabled"); snap("fallback-after-business")
            result.update(fallbackObserved=True, businessStarted=True, businessMarker="BASELINE-INTERNAL", executionModeCode="CandidateNotRegistered", executionMode="AotBaseline",
                          fallbackMarkerPath=str(self.marker_path), fallbackMarkerSha256=verifier.digest(self.marker_path))
            return result
        closure = list(verifier.CANDIDATES[:3]) if mode == "T03-03" else patch["loadOrder"]
        result["expectedClosure"] = closure
        state("initial", "Disabled"); snap("initial")
        if mode == "T03-14":
            for op in ("stage-disabled", "validate-disabled", "commit-disabled", "abort-disabled"):
                code(op, "InvalidState")
            code("configure-null", "InvalidArgument"); state("invalid-configure-unchanged", "Disabled")
        code("configure"); d.update(baselineBuildId=self.build_id, stableAotNames=self.stable); state("configured", "CandidatesRegistered"); event("candidates-registered")
        if mode == "T03-14":
            for op, error in (("configure-again", "InvalidState"), ("abi-mismatch", "RuntimeAbiMismatch"), ("duplicate-closure", "DuplicateAssemblyName"), ("unknown-candidate", "CandidateNotRegistered"), ("empty-closure", "InvalidArgument"), ("null-mode", "InvalidArgument"), ("unknown-mode", "CandidateNotRegistered")):
                code(op, error)
            state("begin-errors-unchanged", "CandidatesRegistered"); snap("begin-errors-no-images")
        if mode == "T03-06":
            code("begin", "BaselineBuildMismatch"); state("wrong-baseline", "CandidatesRegistered"); snap("wrong-baseline")
            return result
        code("begin"); d.update(patchId=patch_id, expected=len(closure), closureLoadOrder=closure)
        d["assemblies"] = [{"name": n, "mvid": "", "skeletonBuilt": False, "runtimeMetadataInitialized": False, "published": False, "moduleInitializerAttempted": False, "moduleInitializerRan": False} for n in closure]
        state("begun", "Staging"); event("transaction-begun"); snap("begun")
        if mode == "T03-04":
            code("extra-candidate", "UnexpectedClosureMember"); snap("extra-rejected"); abort()
            return result
        if mode == "T03-13":
            code("bad-pdb", "BadImage"); snap("bad-pdb-rejected"); state("bad-pdb-retryable", "Staging")
        if mode == "T03-14":
            for op, error in (("commit-before-validate", "InvalidState"), ("null-dll", "InvalidArgument"), ("bad-dll", "BadImage")):
                code(op, error)
            snap("invalid-inputs-no-images")
        stages = list(closure[:2]) if mode == "T03-03" else list(reversed(closure)) if mode in {"T03-02", "T03-07", "T03-12"} else list(closure)
        if mode in {"T03-02", "T03-07", "T03-12"}:
            result.update(stageOrder=stages, stageSeed=3107)
        for name in stages:
            entry = next(a for a in patch["closure"] if a["name"] == name)
            row = next(a for a in d["assemblies"] if a["name"] == name)
            code("stage-" + name); row.update(skeletonBuilt=True, mvid=entry["mvid"])
            d["staged"] += 1; d["retainedBytes"] += 100
            if d["staged"] == len(closure):
                d.update(state="Staged", stateCode=3)
            event("skeleton-created", name); snap("staged-" + name)
            result["stageResults"].append({"name": name, "code": "Success", "dllSha256": entry["sha256"], "pdbSha256": entry["pdbSha256"]})
        state("after-stage", "Staging" if mode == "T03-03" else "Staged")
        if mode == "T03-05":
            snap("before-duplicate"); code("duplicate", "DuplicateAssemblyName"); snap("after-duplicate"); abort()
            return result
        validation = "ClosureMemberMissing" if mode == "T03-03" else "BaselineAlreadyUsed" if mode in {"T03-10", "T03-11"} else "Success"
        code("validate", validation)
        if validation == "Success":
            for row in d["assemblies"]:
                event("metadata-begin", row["name"]); row["runtimeMetadataInitialized"] = True; event("metadata-ready", row["name"])
            d.update(state="Validated", stateCode=4)
        if mode in {"T03-10", "T03-11"}:
            d["baselineUses"] = [{"name": verifier.INTERNAL.lower(), "kind": "AssemblyReflection", "detail": "baseline handle"}]
            if mode == "T03-10":
                result["baselineUseAssemblyLoad"] = verifier.INTERNAL + ", Version=0.0.0.0"
            else:
                result["managedEnumeration"] = copy.deepcopy(d["ordinaryAssemblies"])
        snap("after-validate")
        if validation != "Success":
            abort(); return result
        state("validated", "Validated"); result["stateAtValidate"] = "Validated"
        if mode == "T03-15":
            abort(); return result
        code("commit", "ModuleInitializerFailed" if mode == "T03-08" else "Success")
        d.update(generation=1, enumerationGeneration=1, classEnumerationGeneration=1, state="FailedAfterCommit" if mode == "T03-08" else "Committed", stateCode=9 if mode == "T03-08" else 6)
        d["ordinaryAssemblies"] += [{"name": n.lower(), "isInterpreter": True} for n in closure]
        if len(closure) == 5:
            d["ordinaryClasses"] = [{"assemblyName": verifier.CANDIDATES[1], "typeName": "M03Fixtures.M03Pair`1", "isInterpreter": True, "isConstructedGeneric": True, "usesStagedMetadata": True},
                                    {"assemblyName": "mscorlib", "typeName": "System.Nullable`1", "isInterpreter": False, "isConstructedGeneric": True, "usesStagedMetadata": True}]
        attempted = closure[:3] if mode == "T03-08" else closure
        for row in d["assemblies"]:
            row.update(published=True, moduleInitializerAttempted=row["name"] in attempted, moduleInitializerRan=row["name"] in (attempted[:-1] if mode == "T03-08" else attempted))
        d["commitOrder"] = attempted[:-1] if mode == "T03-08" else attempted
        result["initializerEvents"] = [{"name": n, "state": "Committing", "stateCode": "Success", "diagnosticsCode": "Success", "generation": 1} for n in attempted]
        result["reentrantQueries"] = len(attempted)
        snap("after-commit")
        if mode == "T03-08":
            state("initializer-failure", "FailedAfterCommit"); code("abort-after-failure", "AlreadyCommitted"); code("commit-after-failure", "AlreadyCommitted"); state("still-failed-after-commit", "FailedAfterCommit")
            result.update(fallbackMarkerPath=str(self.marker_path), fallbackMarkerSha256=verifier.digest(self.marker_path))
        else:
            state("committed", "Committed"); code("active-execution-mode"); code("commit-again", "AlreadyCommitted"); code("abort-after-commit", "AlreadyCommitted"); state("committed-frozen", "Committed")
            result.update(stateAfterCommit="Committed", executionModeCode="Success", executionMode="InterpreterShadow", businessStarted=True, businessMarker="PATCH-P01-INTERNAL")
        if mode == "T03-12":
            result.update(stressStarted=True, stressJoined=True, stressBefore=1, stressAfter=1, stressIterations=2, stressErrors=[],
                          stressSamples=[{"generation": 0, "enumerationGeneration": 0, "shadowCount": 0}, {"generation": 1, "enumerationGeneration": 1, "shadowCount": 5}])
        return result

    def result_path(self, mode):
        return self.results / ("m03-" + mode + ".json")

    def write_result(self, mode, result):
        path = self.result_path(mode)
        d = result.pop("_diag", None) or (result["snapshots"][-1]["diagnostics"] if result["snapshots"] else json.loads(result["nativeDiagnosticsJson"]))
        sidecar = path.with_name(path.stem + "-native-diagnostics.json")
        write_json(sidecar, d)
        result.update(nativeDiagnosticsPath=str(sidecar), nativeDiagnosticsSha256=verifier.digest(sidecar), nativeDiagnosticsJson=sidecar.read_text())
        write_json(path, result)

    def verify(self):
        return verifier.verify_suite(self.fixture_path, self.results, on_build_path=self.on[0] / "m03-player-build.json", off_build_path=self.off[0] / "m03-player-build.json")


class M03WholeSuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="m03-verifier-")
        self.addCleanup(self.temp.cleanup)
        self.suite = SyntheticSuite(Path(self.temp.name))
        # Every negative test independently proves its starting evidence passes.
        self.assertTrue(self.suite.verify()["resultPassed"])

    def mutate_result(self, mode, mutate):
        value = json.loads(self.suite.result_path(mode).read_text())
        mutate(value)
        self.suite.write_result(mode, value)

    def rejects(self, reason):
        with self.assertRaisesRegex(VerificationError, reason):
            self.suite.verify()

    def test_valid_whole_suite_with_real_sidecar_names_shuffled_staging_and_lowercase_linked_names(self):
        result = self.suite.verify()
        self.assertEqual(16, len(result["modes"]))
        self.assertNotIn("compileSnapshotHash", self.suite.manifest)
        self.assertEqual(16, len(list(self.suite.results.glob("*-native-diagnostics.json"))))

    def test_cli_accepts_valid_complete_synthetic_suite(self):
        process = subprocess.run([sys.executable, str(Path(verifier.__file__).with_name("verify-m03-results.py")),
                                  "--fixture-manifest", str(self.suite.fixture_path), "--result-dir", str(self.suite.results),
                                  "--on-build", str(self.suite.on[0] / "m03-player-build.json"), "--off-build", str(self.suite.off[0] / "m03-player-build.json")], capture_output=True, text=True)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertTrue(json.loads(process.stdout)["resultPassed"])

    def test_missing_mode_fails_at_mode_inventory(self):
        self.suite.result_path("T03-07").unlink()
        self.rejects("required M03 mode set differs")

    def test_unknown_result_filename_is_not_silently_ignored(self):
        write_json(self.suite.results / "m03-T03-99.json", {"mode": "T03-99"})
        self.rejects("unexpected result filename/mode")

    def test_wrong_native_build_guid_rejected_against_actual_snapshot(self):
        path = self.suite.off[0] / "m03-player-build.json"
        value = json.loads(path.read_text()); value["buildGuid"] = "f" * 32; write_json(path, value)
        self.rejects("buildGuid differs from actual assembly snapshot")

    def test_wrong_result_build_guid_rejected_against_build_receipt(self):
        self.mutate_result("T03-01", lambda r: r.update(playerBuildGuid="f" * 32))
        self.rejects("result playerBuildGuid differs")

    def test_missing_editor_replay_receipt_rejected(self):
        self.suite.replay_path.unlink()
        self.rejects("editorReplayReceipt is missing")

    def test_stale_editor_replay_binding_rejected(self):
        path = self.suite.replay_path
        value = json.loads(path.read_text()); value["fixtureManifestSha256"] = "f" * 64; write_json(path, value)
        self.rejects("Editor replay fixtureManifestSha256 binding differs")

    def test_wrong_patch_dll_rejected_at_bytes(self):
        fixture = self.suite.manifest["fixtures"][0]
        entry = self.suite.patch_docs["P01"]["closure"][0]
        (Path(fixture["patchDirectory"]) / entry["dll"]).write_bytes(b"changed")
        self.rejects("DLL hash differs from bytes/snapshot")

    def test_wrong_patch_pdb_rejected_at_bytes(self):
        fixture = self.suite.manifest["fixtures"][0]
        entry = self.suite.patch_docs["P01"]["closure"][0]
        (Path(fixture["patchDirectory"]) / entry["pdb"]).write_bytes(b"changed")
        self.rejects("PDB hash differs from bytes/snapshot")

    def test_missing_patch_abi_is_not_defaulted(self):
        # Call the artifact layer after proving the whole suite, updating its SHA
        # sidecar so the intended missing ABI validation is reached.
        manifest, baseline, _, fixtures = verifier._verify_inputs(self.suite.fixture_path, None, None)
        path = fixtures["P01"][2]
        value = json.loads(path.read_text()); value.pop("bootstrapAbiHash"); write_json(path, value)
        path.with_name("manifest.sha256").write_text(verifier.digest(path))
        with self.assertRaisesRegex(VerificationError, "bootstrapAbiHash must be a lowercase SHA-256"):
            verifier._verify_patch("P01", fixtures["P01"], manifest, baseline)

    def test_wrong_patch_compile_hash_rejected_at_per_fixture_binding(self):
        manifest, baseline, _, fixtures = verifier._verify_inputs(self.suite.fixture_path, None, None)
        path = fixtures["P01"][2]
        value = json.loads(path.read_text()); value["compileSnapshotHash"] = "f" * 64; write_json(path, value)
        path.with_name("manifest.sha256").write_text(verifier.digest(path))
        with self.assertRaisesRegex(VerificationError, "compiler snapshot binding differs"):
            verifier._verify_patch("P01", fixtures["P01"], manifest, baseline)

    def test_mvid_must_match_actual_selected_patch(self):
        self.mutate_result("T03-01", lambda r: r["snapshots"][2]["diagnostics"]["assemblies"][0].update(mvid=uid("wrong")))
        self.rejects("diagnostic assembly MVID differs from patch")

    def test_self_reported_green_does_not_hide_early_initializer(self):
        self.mutate_result("T03-01", lambda r: r["snapshots"][2]["diagnostics"]["assemblies"][0].update(moduleInitializerAttempted=True))
        self.rejects("private generation contains publication or initializer")

    def test_private_constructed_class_leak_rejected(self):
        self.mutate_result("T03-15", lambda r: r["snapshots"][-1]["diagnostics"]["ordinaryClasses"].append({"assemblyName": "mscorlib", "typeName": "System.Nullable`1", "isInterpreter": False, "isConstructedGeneric": True, "usesStagedMetadata": True}))
        self.rejects("private staged class leaked")

    def test_partial_publication_rejected(self):
        self.mutate_result("T03-02", lambda r: r["snapshots"][-1]["diagnostics"]["ordinaryAssemblies"].pop())
        self.rejects("partial ordinary publication")

    def test_failed_initializer_prefix_is_valid_but_full_order_is_not(self):
        self.mutate_result("T03-08", lambda r: r["snapshots"][-1]["diagnostics"].update(commitOrder=list(verifier.CANDIDATES)))
        self.rejects("commitOrder claims an initializer that did not run")

    def test_committing_prefix_is_valid_without_complete_commit_order(self):
        d = copy.deepcopy(json.loads(self.suite.result_path("T03-02").read_text())["snapshots"][-1]["diagnostics"])
        d.update(state="Committing", stateCode=5, commitOrder=[verifier.CANDIDATES[0]])
        for index, row in enumerate(d["assemblies"]):
            row.update(moduleInitializerAttempted=index < 2, moduleInitializerRan=index == 0)
        verifier._verify_diag_invariants(d, list(verifier.CANDIDATES), self.suite.stable, "committing", patch=self.suite.patch_docs["P03"])

    def test_casefolded_candidate_cannot_enter_stable_allowlist(self):
        value = copy.deepcopy(self.suite.manifest)
        value["stableAotNames"] = sorted(value["stableAotNames"] + [verifier.INTERNAL.lower()])
        write_json(self.suite.fixture_path, value)
        self.rejects("stableAotNames must be sorted, non-empty and exclude candidates")

    def test_missing_resource_abi_fields_are_not_defaulted(self):
        manifest, baseline, _, fixtures = verifier._verify_inputs(self.suite.fixture_path, None, None)
        path = fixtures["P01"][2]
        original = json.loads(path.read_text())
        for field in ("resourceAbiHash", "baselineResourceAbiHash"):
            with self.subTest(field=field):
                value = copy.deepcopy(original); value.pop(field); write_json(path, value)
                path.with_name("manifest.sha256").write_text(verifier.digest(path))
                with self.assertRaisesRegex(VerificationError, field + " must be a lowercase SHA-256"):
                    verifier._verify_patch("P01", fixtures["P01"], manifest, baseline)

    def test_wrong_operation_name_rejected_at_operation_contract(self):
        self.mutate_result("T03-01", lambda r: r["checks"][1].update(operation="diagnostics"))
        self.rejects("unknown operation for mode: diagnostics")

    def test_wrong_error_cannot_be_hidden_by_matching_expected_field(self):
        self.mutate_result("T03-06", lambda r: next(c for c in r["checks"] if c["operation"] == "begin").update(actual="Success", expected="Success", actualCode=0, expectedCode=0))
        self.rejects("begin reports wrong native code")

    def test_duplicate_image_retention_rejected(self):
        self.mutate_result("T03-05", lambda r: next(s for s in r["snapshots"] if s["point"] == "after-duplicate")["diagnostics"].update(retainedBytes=200))
        self.rejects("duplicate Stage allocated another image")

    def test_bad_pdb_retry_must_not_retain_an_image(self):
        self.mutate_result("T03-13", lambda r: next(s for s in r["snapshots"] if s["point"] == "bad-pdb-rejected")["diagnostics"].update(retainedBytes=100))
        self.rejects("retained bytes disagree with staged images")

    def test_unjoined_stress_rejected(self):
        self.mutate_result("T03-12", lambda r: r.update(stressJoined=False))
        self.rejects("bounded stress completion/counts invalid")

    def test_partial_stress_generation_rejected(self):
        self.mutate_result("T03-12", lambda r: r["stressSamples"][1].update(shadowCount=4))
        self.rejects("stress sample proves partial publication")

    def test_fallback_must_be_a_new_process(self):
        self.mutate_result("T03-08-Fallback", lambda r: r.update(processId=1008))
        self.rejects("fallback marker process identity")

    def test_fallback_must_execute_baseline_business(self):
        self.mutate_result("T03-08-Fallback", lambda r: r.update(businessMarker="PATCH-P01-INTERNAL"))
        self.rejects("fallback lacks actual unregistered baseline business execution")

    def test_off_status_is_api_error_not_state_integer(self):
        self.mutate_result("T03-09", lambda r: r.update(stateCode=0))
        self.rejects("native-OFF result must retain Disabled/AotBaseline")


if __name__ == "__main__":
    unittest.main()
