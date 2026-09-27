#!/usr/bin/env python3
"""Execute the fixed R02 Local Validation batch; no source/pin/branch edits.

Default prints a plan. --execute requires exact candidate/control checkouts.
Independent cells continue, dependencies fail closed. No acceptance is granted.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
import time
import uuid

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
if str(TOOLS) not in sys.path: sys.path.insert(0, str(TOOLS))
import authority
import performance
import ordinary_input
import native_prerequisite
from restoration import diagnostic_scene_allowed, restore_files, with_recovery
from evidence import EvidenceError, binding, check_binding, files_under, read, require, run, seal, sha256, write
from verify import MODES, verify_raw
import r00_results
import r00_player_inputs
import h1_count_build_batch as count_build

ENV_KEYS = ("ASSEMBLY_SHADOW_R02_OUTPUT", "ASSEMBLY_SHADOW_R02_RUN_ID", "ASSEMBLY_SHADOW_R02_ROLE")
INDEX = "Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority925e/artifact-index.json"
INDEX_BLOB = "d9636dd4d68f5d8c34bd2f45ae532c77f9862464"
SOURCE_BASE = "30bcb6ebb7f6bcd6c957894f437a9be0d421dce2"


def environment(role=None, output=None, nonce=None):
    value = dict(os.environ)
    value["PYTHONDONTWRITEBYTECODE"] = "1"
    # Canonicalize only the child environment, not validators or retained paths.
    import tempfile
    value["TMPDIR"] = str(Path(tempfile.gettempdir()).resolve(strict=True))
    value.update(DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER="1",
                 MSBUILDDISABLENODEREUSE="1", DOTNET_CLI_USE_MSBUILD_SERVER="0")
    for key in ENV_KEYS: value.pop(key, None)
    if role is not None:
        require(role in ("control", "candidate") and output is not None and nonce is not None, "Incomplete sidecar environment")
        value.update(dict(zip(ENV_KEYS, (str(output), nonce, role))))
    return value


def graph_args(graph):
    return ["--fixture-manifest", graph["fixtureManifest"], "--on-build", graph["nativeOnReceipt"],
            "--off-build", graph["nativeOffReceipt"], "--replay-receipt", graph["editorReplayReceipt"]]


def build_map(roots, graphs):
    result = {"kind": "R02ControlledBuildMap", "protocol": "R02LocalBatch-v1", "sides": {}}
    for side, role in (("A", "control"), ("B", "candidate")):
        graph = graphs[role]
        result["sides"][side] = {
            "projectRoot": str(roots[role]), "fixtureManifest": binding(Path(graph["fixtureManifest"])),
            "replayReceipt": binding(Path(graph["editorReplayReceipt"])), "builds": {}}
        for feature, prefix in (("on", "nativeOn"), ("off", "nativeOff")):
            result["sides"][side]["builds"][feature] = {
                "feature": feature, "development": True, "nativeCompilerConfiguration": "Release",
                "receipt": binding(Path(graph[prefix + "Receipt"])),
                "controlledEvidence": binding(Path(graph[prefix + "ControlledEvidence"]))}
    return result


def select_workflow(project, baseline, before):
    selected = []
    for path in (project / "_temp/AssemblyShadow").rglob("m07-build-workflow.json"):
        if path in before: continue
        row = read(path)
        if row.get("baselineBuildId") == baseline and row.get("projectPath") == str(project):
            require(row.get("result") == "Passed" and row.get("controlledPerformanceBuilds") is True, "Incomplete controlled graph")
            selected.append((path, row))
    require(len(selected) == 1, "Expected one newly created controlled build graph for exact project/baseline")
    return selected[0]


class Batch:
    def __init__(self, args):
        self.args = args
        self.roots = {"candidate": args.candidate, "control": args.control}
        self.heads = {"candidate": args.candidate_head, "control": args.control_head}
        self.targets = read(args.candidate / authority.TARGETS)
        self.out = args.output
        self.rows = {}
        self.values = {}
        self.retained = set()
        self.generated_roots = set()
        self.graphs = {}
        self.serial = 0
        self.prefix = "R02-" + uuid.uuid4().hex

    def retain_root(self, path):
        self.generated_roots.add(path)
        return path

    def new_player_root(self, role, label):
        return self.retain_root(self.roots[role] / "_temp/AssemblyShadow" / (self.prefix + "-" + label))

    def command(self, argv, project, timeout=3600, env=None, unity_owned=False):
        self.serial += 1
        folder = self.out / "commands" / str(self.serial).zfill(4)
        completion = folder.parent / (folder.name + "-unity-completion.json")
        if unity_owned:
            argv = [sys.executable, HERE / "unity_session.py", "--unity", self.args.unity,
                    "--receipt", completion, "--", *argv]
        result = run([str(a) for a in argv], project, folder, timeout, environment() if env is None else env)
        require(result["result"] == "Passed", "Command failed; retained " + str(folder))
        if unity_owned:
            observed = read(completion)
            require(observed.get("result") == "Passed" and observed.get("commandExitCode") == 0 and
                    observed.get("completion", {}).get("clean") is True,
                    "Unity command did not complete cleanly")
        return result, folder / "command.json"

    def tool(self, name, arguments, role="candidate", timeout=3600):
        return self.command([sys.executable, TOOLS / name, *arguments], self.roots[role], timeout)

    def stopped(self, role):
        self.command([self.args.pwsh, "-NoProfile", "-File", TOOLS / "Check-H1EditorStopped.ps1",
                      "-ProjectPath", self.roots[role]], self.roots[role], 90)

    def unity(self, role, method, arguments=(), timeout=28800):
        self.stopped(role)
        log = self.out / ("unity-" + uuid.uuid4().hex + ".log")
        return self.command([self.args.unity, "-batchmode", "-nographics", "-quit", "-projectPath", self.roots[role],
            "-buildTarget", "StandaloneOSX", "-executeMethod", method, *arguments, "-logFile", log], self.roots[role], timeout, unity_owned=True)

    def cell(self, name, dependencies, action, roles=()):
        row = {"name": name, "dependencies": dependencies, "result": "Blocked", "runtimeAcceptance": False}
        missing = [key for key in dependencies if self.rows[key]["result"] != "Passed"]
        if missing: row["blockedBy"] = missing
        else:
            row["startedAtUnix"] = time.time()
            try:
                # A prior failed build can leave a workspace unusable even when
                # this cell's original graph dependency passed. Reauthenticate
                # at cell boundaries, outside deliberate build mutations.
                row["inputAuthorities"] = [authority.inspect(self.roots[role], self.heads[role], role, self.targets) for role in roles]
            except Exception as error:
                row["result"] = "Blocked"
                row["sourceAuthorityError"] = type(error).__name__ + ": " + str(error)
            else:
                try:
                    self.values[name] = action()
                    row["result"] = "Passed"
                except Exception as error:
                    row["result"] = "Failed"
                    row["error"] = type(error).__name__ + ": " + str(error)
            row["endedAtUnix"] = time.time()
        self.rows[name] = row
        write(self.out / "cells" / (name + ".json"), row)
        print(name + ": " + row["result"], flush=True)
        return row

    def source(self, role, final=False):
        result = authority.inspect(self.roots[role], self.heads[role], role, self.targets)
        write(self.out / (("final-" if final else "") + role + "-authority.json"), result)
        return result

    def build(self, role):
        project = self.roots[role]
        self.command([self.args.pwsh, "-NoProfile", "-File", project / ".agents/skills/unity-debug/scripts/Find-Unity.ps1",
                      "-ProjectPath", project, "-Set", self.args.unity], project, 90)
        self.unity(role, "AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability", timeout=3600)
        self.tool("verify-installed-runtime.py", ["--project", project, "--expect-shadow", "on", "--json"], role)
        prepared = self.new_player_root(role, "ordinary-input-" + role)
        ordinary_input.preflight(project, prepared)
        self.unity(role, "AssemblyShadowBaseline.Editor.R02OrdinaryInput.Prepare",
                   ["-shadowR02OrdinaryRoot", prepared])
        authenticated = ordinary_input.verify(project, prepared)
        write(self.out / (role + "-ordinary-input.json"), authenticated)
        self.retained.add(project / ordinary_input.IMAGE_PATH)
        before = set((project / "_temp/AssemblyShadow").rglob("m07-build-workflow.json"))
        baseline = "M07-Baseline-" + self.prefix + "-" + role
        self.command([self.args.pwsh, "-NoProfile", "-File", project / "Tools/AssemblyShadow/Invoke-M07Build.ps1",
            "-ProjectPath", project, "-BaselineId", baseline, "-BuildTarget", "StandaloneOSX", "-ControlledPerformanceBuilds"], project, 86400, unity_owned=True)
        ordinary_input.verify(project, prepared)
        path, graph = select_workflow(project, baseline, before)
        self.graphs[role] = graph
        write(self.out / (role + "-graph.json"), {"workflow": binding(path), "graph": graph})
        r00_player_inputs.verify_inputs(project, *[Path(graph[key]) for key in (
            "fixtureManifest", "nativeOnReceipt", "nativeOffReceipt", "editorReplayReceipt")])
        self.retained.add(path)
        for key in ("runDirectory", "resourceBaselinePath", "nativeOnPlayer", "nativeOffPlayer"):
            self.retain_root(Path(graph[key]))
        self.track_graph_inputs(graph)
        authority.inspect(project, self.heads[role], role, self.targets)
        return graph

    def track_graph_inputs(self, graph):
        spec = importlib.util.spec_from_file_location("r02_m07_runner", TOOLS / "run-m07-players.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        paths = module.collect_inputs(Path(graph["fixtureManifest"]), Path(graph["editorReplayReceipt"]),
            (Path(graph["nativeOnReceipt"]), Path(graph["nativeOffReceipt"])))
        self.retained.update(paths)
        for key in ("nativeOnReceipt", "nativeOffReceipt"):
            receipt = read(Path(graph[key]))
            self.retain_root(Path(receipt["inputSnapshot"]))

    def freeze(self):
        value = build_map(self.roots, self.graphs)
        performance.authenticate_map(value)
        path = self.out / "build-map.json"
        write(path, value)
        write(self.out / "performance-schedule.json", performance.schedule())
        return path

    def sample(self, role, mode, label, sidecar):
        graph = self.graphs[role]
        out = self.new_player_root(role, label)
        nonce = uuid.uuid4().hex
        sidecar_root = self.out / "sidecars" / nonce
        sidecar_root.mkdir(parents=True)
        raw_path = sidecar_root / "r02.json"
        env = environment(role, raw_path, nonce) if sidecar else environment()
        argv = [sys.executable, self.roots[role] / "Tools/AssemblyShadow/run-r00-players.py",
                "--project-root", self.roots[role], *graph_args(graph), "--output-root", out, "--mode", mode, "--timeout", "900"]
        command, command_path = self.command(argv, self.roots[role], 1800, env)
        launch_path = out / "r00-player-launches.json"
        r00_results.verify_suite(launch_path, expected_mode=mode)
        launch = read(launch_path)
        require(len(launch["processLaunches"]) == 1, "Sample does not identify one Player")
        process = launch["processLaunches"][0]
        r00_path = Path(process["resultPath"])
        require(sha256(r00_path) == process["resultSha256"], "Raw changed after strict verification")
        r00 = read(r00_path)
        sample = {"kind": "R02Sample", "result": "Passed", "role": role, "mode": mode,
            "runId": nonce, "sidecarEnabled": sidecar, "command": binding(command_path),
            "launch": binding(launch_path), "raw": binding(r00_path), "runtimeAcceptance": False}
        if sidecar:
            sample["sidecar"] = binding(raw_path)
            verification = verify_raw(read(raw_path), role, mode, nonce, r00, process)
            verify_path = sidecar_root / "verification.json"; write(verify_path, verification)
            sample["verification"] = binding(verify_path)
        else:
            require(not raw_path.exists() and all(key not in env for key in ENV_KEYS), "Formal sample unexpectedly ran sidecar")
        sample_path = sidecar_root / "sample.json"; write(sample_path, sample)
        return {"runId": nonce, "receipt": binding(sample_path), "startedAtUnix": command["startedAtUnix"],
                "endedAtUnix": command["endedAtUnix"]}

    def paired(self):
        rows = []
        index = {"kind": "R02PairedIndex", "result": "Failed", "schedule": binding(self.out / "performance-schedule.json"),
                 "buildMap": binding(self.out / "build-map.json"), "pairs": rows, "runtimeAcceptance": False}
        try:
            for planned in performance.validate_schedule(read(self.out / "performance-schedule.json")):
                row = dict(planned, result="Failed", sides={}); rows.append(row)
                for side in planned["order"]:
                    role = "control" if side == "A" else "candidate"
                    row["sides"][side] = self.sample(role, planned["mode"], planned["pairId"] + "-" + side, False)
                    time.sleep(2)
                row["result"] = "Passed"
                write(self.out / "pairs" / (planned["pairId"] + ".json"), row)
            performance.verify_intervals(rows, performance.schedule()["pairs"])
            index["result"] = "Passed"
        finally:
            write(self.out / "paired-index.json", index)
        analysis = performance.analyze(self.out / "paired-index.json")
        write(self.out / "performance-analysis.json", analysis)
        return analysis

    def negatives(self):
        graph = self.graphs["candidate"]
        fixture = read(Path(graph["fixtureManifest"]))
        root = self.new_player_root("candidate", "negative-fixtures"); root.mkdir()
        failure = root / "failure"
        self.unity("candidate", "AssemblyShadowDemo.Editor.R01FailureFixtures.Build", [
            "-shadowR01FailureBaseline", fixture["baselineManifestPath"], "-shadowM07Fixtures", graph["fixtureManifest"],
            "-shadowR01FailureOutput", failure])
        negative = root / "metadata-negative"
        self.tool("r01_negative_inputs.py", ["--fixtures", graph["fixtureManifest"], "--output-dir", negative])
        return {"failure": failure / "failure-fixtures.json", "negative": negative / "q04-metadata-transform.json"}

    def regression(self, kind):
        root = self.new_player_root("candidate", kind)
        graph = self.graphs["candidate"]
        common = ["--project-root", self.roots["candidate"], *graph_args(graph)]
        if kind == "m07":
            self.tool("run-m07-players.py", common + ["--output-root", root], timeout=28800)
            self.tool("verify-m07-results.py", graph_args(graph) + ["--result-dir", root / "Results", "--output", root / "strict.json"])
        else:
            negative = self.values["negative-fixtures"]
            args = common + ["--failure-fixtures", negative["failure"], "--negative-input", negative["negative"], "--output-root", root]
            stem = "r01-early" if kind == "startup11" else "r01-failure"
            self.tool("run-" + stem + "-players.py", args, timeout=28800)
            self.tool("verify-" + stem + "-results.py", ["--launch-receipt", root / (stem + "-launches.json"), "--output", root / "strict.json"])
        return {"root": str(root)}

    def count_one(self, feature, cpp):
        project = self.roots["candidate"]
        prep = self.retain_root(project / "_temp/AssemblyShadow" / ("H1CountBuild-" + uuid.uuid4().hex)); prep.mkdir()
        before = {name: (project / name).read_bytes() for name in count_build.RESTORABLE}
        folder = self.out / "count-builds" / (feature + "-" + cpp); folder.mkdir(parents=True)
        frozen = sha256(project / "ProjectSettings/AssemblyShadowSourcePins.json")
        common = ["-shadowH1Python", sys.executable, "-shadowH1PreparationRoot", prep]
        def build_action():
            self.unity("candidate", "AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.PrepareDiagnosticBuild", common)
            self.unity("candidate", "AssemblyShadowDemo.Editor.H1CountDiagnosticBuildWithManagedProvenance.BuildDiagnosticPlayer",
                common + ["-shadowH1Feature", feature, "-shadowH1Cpp", cpp, "-shadowH1BuildReceipt", prep / "build-receipt.json",
                          "-shadowH1PlayerOutput", prep / "Player.app"])
            count_build.verify_build(project, prep / "build-receipt.json", folder, frozen)
            return prep / "build-receipt.json"
        def recover():
            # Do not hide a failed Unity restore behind a successful byte copy.
            try:
                self.unity("candidate", "AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.RestoreDiagnosticBuild", common)
            finally:
                self.stopped("candidate")
                restore_files(project, before, count_build.restore_allowed, folder / "restoration")
            authority.inspect(project, self.heads["candidate"], "candidate", self.targets)
        return with_recovery(build_action, recover, folder / "build-recovery.json")

    def counts(self):
        root = self.new_player_root("candidate", "count-inputs"); root.mkdir()
        args = []
        for family, label in (("parameters", "parameter"), ("nested", "nested")):
            target = root / family
            self.tool("create-h1-count-fixtures.py", ["--family", family, "--case-set", "all", "--seed", "20260926", "--output-root", target])
            manifest = target / "h1-count-fixture-manifest.json"; audit = target / "h1-count-fixture-audit.json"
            self.tool("audit-h1-count-fixtures.py", ["--manifest", manifest, "--output", audit])
            args.extend(["--" + label + "-manifest", manifest, "--" + label + "-audit", audit])
        builds = []
        for feature in ("on", "off"):
            for cpp in ("Debug", "Release"):
                builds.extend(["--build-" + feature + "-" + cpp.lower(), self.count_one(feature, cpp)])
        matrix = self.new_player_root("candidate", "count-matrix")
        self.tool("run-h1-count-matrix-players.py", ["--project-root", self.roots["candidate"], *args, *builds,
            "--output-root", matrix, "--timeout", "120"], timeout=28800)
        self.tool("verify-h1-count-matrix.py", ["--result-index", matrix / "result-index.json", *args, "--output", matrix / "strict.json"])
        return {"matrix": str(matrix)}

    def retained_capacity(self):
        # Follow a version-authenticated index to the exact ordinary launch. No
        # basename-only search, relocated substitute, or historical PASS reuse.
        import hashlib
        raw = __import__("subprocess").check_output(["git", "-C", str(self.roots["candidate"]), "show", SOURCE_BASE + ":" + INDEX])
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == INDEX_BLOB, "Historical fixture locator index changed")
        index = json.loads(raw)
        candidates = [r for r in index["artifacts"] if "/H1Authority925e-Capacity-20260919A/" in r["path"] and
                      r["path"].endswith("/r01b-capacity-player-launch.json")]
        require(len(candidates) == 1, "No unique indexed retained ordinary capacity launch")
        row = candidates[0]; path = Path(row["path"])
        if not path.is_absolute(): path = self.roots["candidate"] / path
        require(sha256(path) == row["sha256"] and path.stat().st_size == row["sizeBytes"], "Retained capacity locator unavailable/mismatched")
        launch = read(path)
        require(launch.get("kind") == "R01BCapacityPlayerLaunchReceipt" and launch.get("scenario") == "OrdinaryEnvelope", "Wrong retained capacity fixture locator")
        manifest, corpus = Path(launch["workloadManifestPath"]), Path(launch["corpusRoot"])
        require(sha256(manifest) == launch["workloadManifestSha256"], "Retained workload manifest mismatch")
        from r01b_capacity_inputs import validate_workload
        _, dlls = validate_workload(manifest, corpus, deep=True)
        self.retained.update([path, manifest, *dlls])
        value = {"kind": "R02RetainedFixtureAuthentication", "inputReuseOnly": True,
                 "historicalExecutionReused": False, "launchLocator": binding(path), "manifest": binding(manifest), "corpus": str(corpus)}
        write(self.out / "retained-capacity-fixture.json", value)
        return value

    def diagnostic(self):
        project = self.roots["candidate"]; graph = self.graphs["candidate"]
        root = self.new_player_root("candidate", "diagnostic-build"); root.mkdir()
        # The committed adapter selects the exact new baseline in memory only;
        # its finally block restores settings. Generated scene recovery is
        # limited to the two serialized identity fields.
        scene = project / "Assets/AssemblyShadowR01BDiagnostics/Scenes/R01BDiagnostic.unity"
        before = scene.read_bytes()
        receipt = root / "build.json"
        def build_action():
            self.unity("candidate", "AssemblyShadowDemo.Editor.R02DiagnosticBuild.Build", [
                "-shadowM07Fixtures", graph["fixtureManifest"], "-shadowM07PlayerReceipt", graph["nativeOnReceipt"],
                "-shadowR01BDiagnosticOutput", root / "Player.app", "-shadowR01BDiagnosticBuildReceipt", receipt])
        def recover():
            self.stopped("candidate")
            restore_files(project, {str(scene.relative_to(project)): before},
                lambda relative, original, current: diagnostic_scene_allowed(original, current), root / "restoration")
        with_recovery(build_action, recover, root / "build-recovery.json")
        authority.inspect(project, self.heads["candidate"], "candidate", self.targets)
        from r01b_diagnostic_inputs import verify_diagnostic_inputs
        verify_diagnostic_inputs(project, *[Path(graph[k]) for k in ("fixtureManifest", "nativeOnReceipt", "nativeOffReceipt", "editorReplayReceipt")], receipt)
        self.retain_root(Path(read(receipt)["inputSnapshot"]))
        return receipt

    def capacity(self, mixed):
        graph = self.graphs["candidate"]; fixture = self.values["retained-capacity-inputs"]
        root = self.new_player_root("candidate", "mixed-capacity" if mixed else "ordinary-capacity")
        args = ["--project-root", self.roots["candidate"], *graph_args(graph), "--diagnostic-build", self.values["diagnostic-build"],
                "--workload-manifest", check_binding(fixture["manifest"]), "--corpus-root", fixture["corpus"],
                "--overflow-receipt", self.values["overflow-fixture"]]
        if mixed:
            inputs = self.new_player_root("candidate", "mixed-inputs")
            self.tool("create-r01b-mixed-workload.py", ["--project-root", self.roots["candidate"], *graph_args(graph),
                "--ordinary-manifest", check_binding(fixture["manifest"]), "--ordinary-corpus", fixture["corpus"], "--output-root", inputs])
            args += ["--mixed", "--mixed-manifest", inputs / "r01b-mixed-workload-manifest.json", "--mixed-corpus", inputs / "corpus"]
        self.tool("run-r01b-capacity-player.py", [*args, "--output-root", root], timeout=7200)
        prefix = "r01b-mixed" if mixed else "r01b-capacity"
        self.tool("verify-r01b-capacity-result.py", [*args, "--launch-receipt", root / (prefix + "-player-launch.json"), "--output", root / "strict.json"])
        return {"root": str(root)}

    def overflow(self):
        root = self.new_player_root("candidate", "overflow-input")
        self.tool("create-r01b-overflow-fixture.py", ["--output-root", root])
        return root / "r01b-overflow-fixture-receipt.json"

    def lazy(self):
        graph = self.graphs["candidate"]
        lazy = self.new_player_root("candidate", "lazy-input"); dense = self.new_player_root("candidate", "dense-input")
        self.tool("create-r01b-lazy-fixture.py", ["--output-root", lazy])
        self.tool("create-r01b-dense-fixtures.py", ["--output-root", dense])
        root = self.new_player_root("candidate", "lazy-player")
        self.tool("run-r01b-lazy-player.py", ["--project-root", self.roots["candidate"], *graph_args(graph),
            "--diagnostic-build", self.values["diagnostic-build"], "--lazy-fixture-receipt", lazy / "r01b-lazy-fixture-receipt.json",
            "--dense-manifest", dense / "workload-v3-dense-adjunct-v2.json", "--output-root", root], timeout=7200)
        return {"root": str(root)}

    def editor_tests(self):
        project = self.roots["candidate"]
        self.stopped("candidate")
        xml = self.out / "editmode.xml"
        self.command([self.args.unity, "-batchmode", "-nographics", "-projectPath", project,
            "-runTests", "-testPlatform", "EditMode", "-testResults", xml,
            "-logFile", self.out / "editmode-unity.log"], project, 7200, unity_owned=True)
        import xml.etree.ElementTree as ET
        cases = ET.parse(xml).getroot().findall(".//test-case")
        require(cases and all(c.get("result") not in ("Failed", "Inconclusive") for c in cases), "EditMode contains failures or no cases")
        required = [c for c in cases if "R02ProbeContractTests." in c.get("fullname", "")]
        require(len(required) == 2 and all(c.get("result") == "Passed" for c in required), "R02 Editor contract coverage missing")
        result = {"kind": "R02EditorTests", "caseCount": len(cases), "passed": sum(c.get("result") == "Passed" for c in cases),
                  "otherResults": [{"name": c.get("fullname"), "result": c.get("result")} for c in cases if c.get("result") != "Passed"],
                  "xml": binding(xml), "runtimeAcceptance": False}
        write(self.out / "editor-tests.json", result)
        return result

    def native_regressions(self):
        project = self.roots["candidate"]
        native = project.parent / "hybridclr"; runtime = project.parent / "il2cpp_plus"
        definitions = [
            ("run-r01-budget-native-tests.py", ["--hybridclr-root", native]),
            ("run-r01-recovery-native-tests.py", ["--il2cpp-root", runtime]),
            ("run-r01b-index-runtime-tests.py", ["--native-root", native, "--runtime-root", runtime]),
            ("run-r01b-type-cache-tests.py", ["--native-root", native]),
        ]
        rows = []
        for script, arguments in definitions:
            try:
                self.tool(script, ["--demo-root", project, *arguments, "--output", self.out / (script + ".json")])
                rows.append({"script": script, "result": "Passed"})
            except Exception as error: rows.append({"script": script, "result": "Failed", "error": str(error)})
        write(self.out / "native-regressions.json", {"rows": rows, "runtimeAcceptance": False})
        require(all(r["result"] == "Passed" for r in rows), "Native regression matrix incomplete")
        return rows

    def native_generated_inputs(self):
        project = self.roots["candidate"]
        # Full installed-runtime verification remains outside the version-only
        # prerequisite. Do not fabricate generated headers or copy control data.
        self.tool("verify-installed-runtime.py", ["--project", project, "--expect-shadow", "on", "--json"])
        result = native_prerequisite.prepare(project, self.out / "candidate-graph.json", self.args.unity,
                                            self.out / "native-generated-inputs.json")
        self.retained.update(Path(row["path"]) for row in result["files"].values())
        return result

    def native_transaction(self):
        prerequisite = self.values["native-generated-inputs"]
        native_prerequisite.recheck(prerequisite)
        project = self.roots["candidate"]
        def execute():
            self.tool("run-r01-transaction-native-tests.py", ["--demo-root", project,
                "--hybridclr-root", project.parent / "hybridclr", "--runtime-root", project.parent / "il2cpp_plus",
                "--installed-root", prerequisite["installedRoot"],
                "--pins", prerequisite["files"]["pins"]["path"],
                "--dll", prerequisite["files"]["fixture"]["path"],
                "--baselib", prerequisite["files"]["baselib"]["path"],
                "--output", self.out / "run-r01-transaction-native-tests.py.json"])
            return {"result": "Passed", "runtimeAcceptance": False}
        return with_recovery(execute, lambda: native_prerequisite.recheck(prerequisite),
                             self.out / "native-transaction-integrity.json")

    def finish(self):
        paths = set(self.retained)
        for root in self.generated_roots:
            if root.is_dir(): paths.update(files_under(root))
        paths.update(files_under(self.out))
        sealed = seal(paths, self.out / "seal")
        summary = {"kind": "R02LocalValidationBatch", "result": "EvidenceReadyForStageReview" if all(
            row["result"] == "Passed" for row in self.rows.values()) else "ReturnRequired",
            "cells": list(self.rows.values()), "seal": binding(self.out / "seal/seal-index.json"),
            "H1": "PassedWithExplicitDeferredRisk", "R02Accepted": False, "mayEnterR03": False,
            "D1D2": "MeasuredDispositionRequiredBeforeH2", "runtimeAcceptance": False}
        write(self.out / "LOCAL_BATCH_RESULT.json", summary)
        return summary


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", required=True, type=Path); p.add_argument("--candidate-head", required=True)
    p.add_argument("--control", required=True, type=Path); p.add_argument("--control-head", required=True)
    p.add_argument("--unity", required=True, type=Path); p.add_argument("--pwsh", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path); p.add_argument("--execute", action="store_true")
    return p.parse_args(argv)


def _execute(args):
    if not args.execute:
        print(json.dumps({"protocol": "R02LocalBatch-v1", "candidate": str(args.candidate), "control": str(args.control),
            "cells": ["authority", "primary", "two-controlled-graphs", "eight-functional-sidecars", "44-pairs-88-processes",
                      "m07", "startup11", "failure", "count132", "diagnostic", "lazy-dense", "ordinary-mixed-capacity", "seal"],
            "executes": False, "runtimeAcceptance": False}, indent=2)); return 0
    require(sys.platform == "darwin", "Real batch requires macOS")
    require(args.candidate != args.control and args.output.is_absolute() and not args.output.exists(), "Separate canonical roots and new output required")
    for path in (args.candidate, args.control):
        require(path.is_absolute() and path == path.resolve(strict=True), "Canonical checkout required")
    require(args.unity.is_file() and args.unity.is_absolute() and args.pwsh.is_file() and args.pwsh.is_absolute(), "Explicit local tools required")
    require(args.output.parent == args.candidate / "_temp/AssemblyShadow", "Batch output must be a new direct candidate _temp/AssemblyShadow child")
    require(shutil.disk_usage(args.candidate).free >= 30 * 1024**3, "At least 30 GiB free required; never remove historical evidence automatically")
    args.output.mkdir()
    batch = Batch(args)
    for role in ("candidate", "control"):
        batch.cell(role + "-authority", [], lambda role=role: batch.source(role))
    batch.cell("common-sources", ["candidate-authority", "control-authority"], lambda: write(batch.out / "common-sources.json", authority.common_sources(args.candidate, args.control)))
    batch.cell("primary", ["candidate-authority"], lambda: batch.command([sys.executable, HERE / "run_primary.py",
        "--il2cpp-root", args.candidate.parent / "il2cpp_plus", "--output", args.output / "primary"], args.candidate, 7200), roles=("candidate",))
    for role in ("candidate", "control"):
        batch.cell(role + "-build", ["common-sources", "primary"], lambda role=role: batch.build(role), roles=(role,))
    batch.cell("frozen-build-map", ["candidate-build", "control-build"], batch.freeze, roles=("candidate", "control"))
    functional = []
    for role in ("control", "candidate"):
        for mode in MODES:
            name = role + "-" + mode; functional.append(name)
            batch.cell(name, ["frozen-build-map"], lambda role=role, mode=mode, name=name: batch.sample(role, mode, name, True), roles=(role,))
    batch.cell("performance", functional, batch.paired, roles=("candidate", "control"))
    batch.cell("editor-tests", ["candidate-build"], batch.editor_tests, roles=("candidate",))
    batch.cell("native-regressions", ["candidate-authority"], batch.native_regressions, roles=("candidate",))
    batch.cell("native-generated-inputs", ["candidate-build"], batch.native_generated_inputs, roles=("candidate",))
    batch.cell("native-transaction", ["native-generated-inputs"], batch.native_transaction, roles=("candidate",))
    batch.cell("negative-fixtures", ["candidate-build"], batch.negatives, roles=("candidate",))
    batch.cell("m07", ["candidate-build"], lambda: batch.regression("m07"), roles=("candidate",))
    for kind in ("startup11", "failure"):
        batch.cell(kind, ["negative-fixtures"], lambda kind=kind: batch.regression(kind), roles=("candidate",))
    batch.cell("count132", ["candidate-build"], batch.counts, roles=("candidate",))
    batch.cell("diagnostic-build", ["candidate-build"], batch.diagnostic, roles=("candidate",))
    batch.cell("retained-capacity-inputs", ["candidate-authority"], batch.retained_capacity)
    batch.cell("overflow-fixture", ["candidate-authority"], batch.overflow)
    batch.cell("lazy-dense", ["diagnostic-build"], batch.lazy, roles=("candidate",))
    for mixed in (False, True):
        batch.cell("mixed-capacity" if mixed else "ordinary-capacity", ["diagnostic-build", "retained-capacity-inputs", "overflow-fixture"], lambda mixed=mixed: batch.capacity(mixed), roles=("candidate",))
    for role in ("candidate", "control"):
        batch.cell("final-" + role + "-authority", [role + "-authority"], lambda role=role: batch.source(role, final=True))
    try: summary = batch.finish()
    except Exception as error:
        write(args.output / "SEAL_FAILED.json", {"kind": "R02SealFailure", "result": "Failed", "error": str(error), "runtimeAcceptance": False})
        return 1
    print(json.dumps({"result": summary["result"], "output": str(args.output), "runtimeAcceptance": False}))
    return 0 if summary["result"] == "EvidenceReadyForStageReview" else 1


def main(argv=None):
    args = parse(argv)
    if not args.execute: return _execute(args)
    # Serialize these two known workspaces; never kill another agent's Unity.
    import contextlib
    import fcntl
    with contextlib.ExitStack() as stack:
        for project in sorted((args.candidate, args.control)):
            require(project.is_absolute() and project == project.resolve(strict=True), "Canonical checkout required")
            parent = project / "_temp/AssemblyShadow"; parent.mkdir(parents=True, exist_ok=True)
            path = parent / "r02-local.lock"
            require(not path.is_symlink(), "Linked lock refused")
            handle = stack.enter_context(path.open("a+"))
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _execute(args)


if __name__ == "__main__": raise SystemExit(main())
