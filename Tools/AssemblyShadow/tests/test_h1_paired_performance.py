import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import h1_paired_performance as analysis
from shadow_tools import VerificationError

ROOT = Path("/Users/ah/GitHub/hybridclr")
PROTOCOL = ROOT / "h1r-execution-20260910/performance-protocol.preregistered.json"
SCHEDULE = ROOT / "h1r-coordination-20260910/performance-schedule.preregistered.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def bind(path):
    return {"path": str(path), "sha256": sha(path)}


def inventory_hash(rows):
    text = "\n".join(row["path"] + "\0" + row["source"] + "\0" + row["sha256"]
                     for row in sorted(rows, key=lambda row: row["path"]))
    return hashlib.sha256(text.encode()).hexdigest()


class H1PairedPerformanceTests(unittest.TestCase):
    def temp(self, prefix="h1-paired-"):
        root = Path(tempfile.mkdtemp(prefix=prefix)).resolve()
        self.addCleanup(shutil.rmtree, root)
        return root

    def protocol_schedule(self, root):
        protocol_path = root / "protocol.json"
        write(protocol_path, json.loads(PROTOCOL.read_text()))
        schedule = json.loads(SCHEDULE.read_text())
        schedule["protocolPath"] = str(protocol_path)
        schedule["protocolSha256"] = sha(protocol_path)
        schedule_path = root / "schedule.json"
        write(schedule_path, schedule)
        return protocol_path, schedule_path, schedule

    def provenance(self, project, pins, build_name):
        root = project / ("provenance-" + build_name)
        files = {
            "source-pins.json": pins.read_bytes(),
            "tools/verify-installed-runtime.py": b"verify",
            "tools/shadow_tools.py": b"support",
            "installedlibil2cpp/assembly-shadow-install.json": b"install",
            "installedlibil2cpp/native.cpp": b"native source",
            "external/external.h": b"external source",
        }
        rows = []
        for relative, data in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            rows.append({"path": relative, "source": "snapshot", "sha256": sha(path)})
        python = project / ("python3-" + build_name)
        python.write_bytes(b"python")
        return {
            "schemaVersion": 2, "projectRoot": str(project), "snapshotRoot": str(root),
            "snapshotFiles": rows, "snapshotInventorySha256": inventory_hash(rows),
            "sourcePinFile": str(root / "source-pins.json"), "sourcePinSha256": sha(pins),
            "verificationToolPath": str(root / "tools/verify-installed-runtime.py"),
            "verificationToolSha256": sha(root / "tools/verify-installed-runtime.py"),
            "verificationSupportToolPath": str(root / "tools/shadow_tools.py"),
            "verificationSupportToolSha256": sha(root / "tools/shadow_tools.py"),
            "installReceiptPath": str(root / "installedlibil2cpp/assembly-shadow-install.json"),
            "installReceiptSha256": sha(root / "installedlibil2cpp/assembly-shadow-install.json"),
            "pythonExecutable": str(python), "pythonExecutableSha256": sha(python),
            "verificationExitCode": 0,
        }

    def build_map(self, root):
        sides, refs, facts = {}, {}, {}
        for side in ("A", "B"):
            project = root / (side + "-project")
            core = project / analysis.MEASUREMENT_CORE
            process_memory = project / analysis.PROCESS_MEMORY
            witness = project / analysis.WITNESS
            pins = project / "ProjectSettings/AssemblyShadowSourcePins.json"
            for path, data in ((core, b"same core"), (process_memory, b"same process memory"),
                               (witness, b"same witness"),
                               (pins, ("pins-" + side).encode())):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            fixture, replay = project / "fixture.json", project / "replay.json"
            write(fixture, {"schemaVersion": 1})
            write(replay, {"schemaVersion": 1, "result": "Passed"})
            builds, refs[side] = {}, {}
            for flavor in ("on", "off"):
                feature_bit = "1" if flavor == "on" else "0"
                variant = "NativeOn" if flavor == "on" else "NativeOff"
                native_args = '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + feature_bit + '"'
                snapshot = project / ("M07PlayerInputs-" + flavor)
                app = project / (flavor + ".app")
                executable = app / "Contents/MacOS/Player"
                native = app / "Contents/Frameworks/libil2cpp.dylib"
                metadata = app / "Contents/Resources/metadata.dat"
                for path, data in ((executable, b"exe" + side.encode() + flavor.encode()),
                                   (native, b"native" + side.encode() + flavor.encode()),
                                   (metadata, b"meta" + side.encode() + flavor.encode())):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                snapshot.mkdir(parents=True)
                receipt_path = snapshot / "m07-player-build.json"
                guid = side + "-" + flavor + "-guid"
                abi = ("a" if side == "A" else "b") * 64
                receipt = {"schemaVersion": 1, "milestone": "M07", "variant": variant,
                           "baselineBuildId": side + "-baseline", "runtimeAbiHash": abi,
                           "unityVersion": analysis.UNITY_VERSION, "target": analysis.TARGET,
                           "architecture": analysis.ARCHITECTURE, "buildGuid": guid,
                           "playerOutput": str(app), "inputSnapshot": str(snapshot),
                           "inputSnapshotHash": hashlib.sha256((side + flavor).encode()).hexdigest(),
                           "nativeLibraryPath": str(native), "nativeLibrarySha256": sha(native),
                           "nativeMetadataPath": str(metadata), "nativeMetadataSha256": sha(metadata),
                           "nativeArguments": native_args, "assemblyIdentities": [],
                           "nativeAssemblyIdentities": [], "nativeGeneratedAssemblyNames": []}
                write(receipt_path, receipt)
                provenance = self.provenance(project, pins, flavor)
                measurement_root = project / ("measurement-sources-" + flavor)
                measurement_rows = []
                for relative in (analysis.MEASUREMENT_CORE, analysis.PROCESS_MEMORY, analysis.WITNESS):
                    source = project / relative
                    snapshot_source = measurement_root / relative
                    snapshot_source.parent.mkdir(parents=True, exist_ok=True)
                    snapshot_source.write_bytes(source.read_bytes())
                    measurement_rows.append({"relativePath": relative,
                                             "originalSourcePath": str(source),
                                             "snapshotPath": str(snapshot_source),
                                             "sha256": sha(snapshot_source)})
                config = {"development": True, "developmentOption": True, "scriptingBackend": "IL2CPP",
                          "il2CppCompilerConfiguration": "Release", "managedStrippingLevel": "Low",
                          "il2CppCodeGeneration": "OptimizeSpeed", "allowDebugging": False,
                          "connectProfiler": False, "deepProfiling": False, "buildScriptsOnly": False,
                          "nativeArguments": native_args}
                evidence_path = project / ("controlled-" + flavor + ".json")
                evidence = {"schemaVersion": 1, "kind": "R00ControlledBuildEvidence", "result": "Passed",
                            "feature": flavor, "selectedBuildMethod": "BuildPlayerBaseline" if flavor == "on" else "BuildFeatureDisabledPlayer",
                            "provenanceComplete": True, "sourcePinsUnchanged": True,
                            "measurementSourcesUnchanged": True,
                            "measurementSourceSnapshotRoot": str(measurement_root),
                            "measurementSourcesBuildGuid": guid, "measurementSources": measurement_rows,
                            "requestedConfiguration": config, "effectiveConfiguration": config,
                            "nativeProvenance": provenance, "actualReceiptPath": str(receipt_path),
                            "actualReceiptSha256": sha(receipt_path), "actualReceiptVariant": variant,
                            "buildGuid": guid, "baselineBuildId": receipt["baselineBuildId"],
                            "runtimeAbiHash": abi, "playerOutput": str(app),
                            "playerExecutable": str(executable), "playerExecutableSha256": sha(executable),
                            "nativeLibraryPath": str(native), "nativeLibrarySha256": sha(native),
                            "nativeMetadataPath": str(metadata), "nativeMetadataSha256": sha(metadata),
                            "inputSnapshotPath": str(snapshot), "inputSnapshotSha256": receipt["inputSnapshotHash"],
                            "nativeArguments": native_args, "sourcePinsPath": provenance["sourcePinFile"],
                            "sourcePinsSha256Before": sha(pins), "sourcePinsSha256After": sha(pins)}
                write(evidence_path, evidence)
                builds[flavor] = {"feature": flavor, "development": True,
                                  "nativeCompilerConfiguration": "Release", "buildGuid": guid,
                                  "playerOutput": str(app), "receipt": bind(receipt_path),
                                  "controlledEvidence": bind(evidence_path)}
                refs[side][flavor.upper()] = {"receiptPath": receipt_path, "receipt": receipt,
                                             "evidencePath": evidence_path,
                                             "evidenceBinding": builds[flavor]["controlledEvidence"],
                                             "livePins": pins, "snapshotPins": Path(provenance["sourcePinFile"])}
            sides[side] = {"projectRoot": str(project), "fixtureManifest": bind(fixture),
                           "replayReceipt": bind(replay), "builds": builds}
            facts[side] = {"developmentCppRelease": True, "unity": analysis.UNITY_VERSION,
                           "architecture": analysis.ARCHITECTURE, "strip": "Low", "codegen": "OptimizeSpeed",
                           "startup": analysis.STARTUP_STRATEGY, "commonMeasurementCoreSha256": sha(core),
                           "witnessSha256": sha(witness), "runtimeAbiHash": refs[side]["ON"]["receipt"]["runtimeAbiHash"],
                           "sourcePins": sha(pins)}
        comparability = {field: {side: facts[side][field] for side in ("A", "B")}
                         for field in analysis.MATCH_FIELDS + analysis.EXPECTED_DIFFERENCES}
        return {"schemaVersion": 1, "kind": "H1ControlledBuildMap", "status": "Frozen",
                "protocolId": analysis.PROTOCOL_ID, "target": analysis.TARGET,
                "architecture": analysis.ARCHITECTURE,
                "configuration": {"development": True, "nativeCompilerConfiguration": "Release",
                                  "nativeAssertions": False},
                "comparability": comparability, "sides": sides}, refs

    def mutate_evidence(self, refs, side, flavor, mutation):
        ref = refs[side][flavor]
        value = copy.deepcopy(json.loads(ref["evidencePath"].read_text()))
        mutation(value)
        write(ref["evidencePath"], value)
        ref["evidenceBinding"]["sha256"] = sha(ref["evidencePath"])

    def test_producer_schema_build_map_authenticates_actual_facts(self):
        build_map, _ = self.build_map(self.temp())
        result = analysis.validate_build_map(build_map)
        self.assertEqual(result["status"], "ComparabilityPassed")
        self.assertEqual(result["matchedFields"]["startup"], "R01EarlyStartup")

    def test_wrong_guid_receipt_configuration_and_source_proof_are_rejected(self):
        mutations = [
            ("guid", lambda refs: self.mutate_evidence(refs, "A", "ON", lambda value: value.update(buildGuid="wrong"))),
            ("receipt", lambda refs: refs["A"]["ON"]["receiptPath"].write_text("{}")),
            ("config", lambda refs: self.mutate_evidence(refs, "B", "OFF", lambda value: value["effectiveConfiguration"].update(development=False))),
            ("source", lambda refs: refs["A"]["ON"]["snapshotPins"].write_bytes(b"changed")),
        ]
        for label, mutation in mutations:
            with self.subTest(label=label):
                build_map, refs = self.build_map(self.temp("h1-negative-"))
                mutation(refs)
                self.assertEqual(analysis.validate_build_map(build_map)["status"], "ComparabilityFailed")
        build_map, _ = self.build_map(self.temp("h1-same-candidate-"))
        build_map["sides"]["B"] = build_map["sides"]["A"]
        result = analysis.validate_build_map(build_map)
        self.assertEqual(result["status"], "ComparabilityFailed")
        self.assertIn("reuses", result["reasons"][0])
        for relative, replacement, reason in (
                (analysis.MEASUREMENT_CORE, b"different build-time core", "commonMeasurementCoreSha256"),
                (analysis.PROCESS_MEMORY, b"different build-time memory", "processMemorySha256")):
            with self.subTest(built_source=relative):
                build_map, refs = self.build_map(self.temp("h1-built-source-difference-"))
                for flavor in ("ON", "OFF"):
                    ref = refs["B"][flavor]
                    evidence = json.loads(ref["evidencePath"].read_text())
                    row = next(item for item in evidence["measurementSources"]
                               if item["relativePath"] == relative)
                    Path(row["snapshotPath"]).write_bytes(replacement)
                    row["sha256"] = sha(Path(row["snapshotPath"]))
                    write(ref["evidencePath"], evidence)
                    ref["evidenceBinding"]["sha256"] = sha(ref["evidencePath"])
                self.assertEqual(sha(Path(build_map["sides"]["A"]["projectRoot"]) / relative),
                                 sha(Path(build_map["sides"]["B"]["projectRoot"]) / relative))
                result = analysis.validate_build_map(build_map)
                self.assertEqual(result["status"], "ComparabilityFailed")
                self.assertIn(reason, result["reasons"][0])

    def test_minimal_or_claim_only_build_map_cannot_pass(self):
        value = {"schemaVersion": 1, "kind": "H1ControlledBuildMap", "status": "Frozen",
                 "protocolId": analysis.PROTOCOL_ID, "target": analysis.TARGET,
                 "architecture": analysis.ARCHITECTURE,
                 "configuration": {"development": True, "nativeCompilerConfiguration": "Release", "nativeAssertions": False},
                 "comparability": {field: {"A": True, "B": True}
                                   for field in analysis.MATCH_FIELDS + analysis.EXPECTED_DIFFERENCES},
                 "buildReceipts": {"A": {}, "B": {}}, "controlledEvidence": {"path": "fake", "sha256": "0" * 64}}
        self.assertEqual(analysis.validate_build_map(value)["status"], "ComparabilityFailed")

    def pending_fixture(self):
        root = self.temp()
        protocol, schedule, schedule_value = self.protocol_schedule(root)
        build = root / "build.json"
        write(build, {"schemaVersion": 1, "kind": "H1ControlledBuildMap", "status": "BuildMapPending"})
        launch = root / "launch.json"
        write(launch, {})
        launch_binding = bind(launch)
        attempts = [{"pairId": row["pairId"], "attempt": 1,
                     "A": {"launchReceipt": launch_binding}, "B": {"launchReceipt": launch_binding}}
                    for row in schedule_value["pairs"]]
        index = {"schemaVersion": 1, "kind": "H1ControlledSamples", "protocol": bind(protocol),
                 "schedule": bind(schedule), "buildMap": bind(build), "attempts": attempts}
        return root, protocol, schedule, index, launch

    def test_schedule_and_failed_launch_binding_guards(self):
        _, protocol, schedule, index, _ = self.pending_fixture()
        index["attempts"].pop()
        with self.assertRaises(VerificationError):
            analysis.validate_sample_index(index, protocol, schedule)
        root, protocol, schedule, index, launch = self.pending_fixture()
        write(launch, {"processLaunches": [{"startedAtUnix": 1.0, "durationSeconds": 1.0}]})
        index_path = root / "index.json"
        write(index_path, index)
        result = analysis.analyze_sample_index(index_path, protocol, schedule)
        self.assertFalse(result["requirements"]["globalIntervalsResolved"])
        self.assertFalse(result["requirements"]["chronologyComplete"])

    def raw(self, mode, expected):
        receipt = expected["receipt"]
        return {"mode": mode, "result": "Passed",
                "playerBuildReceipt": {"path": str(expected["receiptPath"]), "sha256": sha(expected["receiptPath"]),
                                       "buildGuid": receipt["buildGuid"], "baselineBuildId": receipt["baselineBuildId"],
                                       "runtimeAbiHash": receipt["runtimeAbiHash"]},
                "operations": [{"operation": operation, "phase": phase, "elapsedTicks": 20,
                                "stopwatchFrequency": 1000, "requestedIterations": 1}
                               for operation in analysis.OPERATIONS for phase in analysis.PHASES],
                "readiness": {"businessReady": True, "businessReadyUtcTicks": 100},
                "memorySnapshots": [{"phase": phase, "measurement": analysis.MEMORY_MEASUREMENT,
                                     "measurementSemantics": analysis.MEMORY_SEMANTICS,
                                     "currentRssBytes": 100, "managedBytes": 50, "lifetimePeakRssBytes": 120}
                                    for phase in analysis.MEMORY_PHASES]}

    def test_analyze_sample_index_complete_positive(self):
        root = self.temp("h1-complete-")
        protocol, schedule, schedule_value = self.protocol_schedule(root)
        build_map, refs = self.build_map(root)
        build = root / "build.json"
        write(build, build_map)
        attempts, pilot, formal = [], 0, 0
        for row in schedule_value["pairs"]:
            if row["phase"] == "pilot":
                base, pilot = pilot * 3.0, pilot + 1
            else:
                base, formal = 100.0 + formal * 3.0, formal + 1
            result_sides = {}
            world = "OFF" if row["mode"] == analysis.MODES[0] else "ON"
            for offset, side in enumerate(row["order"]):
                raw_path = root / "raw" / (row["pairId"] + side + ".json")
                write(raw_path, self.raw(row["mode"], refs[side][world]))
                launch = root / "launch" / (row["pairId"] + side + ".json")
                write(launch, {"processLaunches": [{"mode": row["mode"], "startedAtUnix": base + offset,
                                                    "durationSeconds": .5, "resultPath": str(raw_path),
                                                    "resultSha256": sha(raw_path)}]})
                result_sides[side] = {"launchReceipt": bind(launch)}
            attempts.append({"pairId": row["pairId"], "attempt": 1, **result_sides})
        index = root / "index.json"
        write(index, {"schemaVersion": 1, "kind": "H1ControlledSamples", "protocol": bind(protocol),
                      "schedule": bind(schedule), "buildMap": bind(build), "attempts": attempts})

        def verifier(_path, expected_mode):
            return {"requestedModeIds": [expected_mode], "executedModeIds": [expected_mode],
                    "modes": [{"launchToBusinessReadyMilliseconds": 10.0}]}

        result = analysis.analyze_sample_index(index, protocol, schedule, verifier)
        self.assertEqual(result["status"], "ComparabilityPassed")
        self.assertEqual(result["result"], "Passed")
        self.assertTrue(result["requirements"]["chronologyComplete"])
        self.assertEqual(sum(result["requirements"]["formalPairsPerMode"].values()), 40)


if __name__ == "__main__":
    unittest.main()
