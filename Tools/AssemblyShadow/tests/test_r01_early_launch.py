import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_early_results as gate


class EarlyLaunchTests(unittest.TestCase):
    def test_positive_command_hands_off_to_existing_m07_runner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            executable = root / "AssemblyShadow.app/Contents/MacOS/AssemblyShadow"
            capsule_path = root / "Control/r01-early.capsule"
            capsule_path.parent.mkdir()
            capsule_path.write_bytes(b"capsule")
            prepared = {"runner": type("Runner", (), {"executable_for": lambda self, _: executable})(),
                        "context": {"on": {"output": root / "AssemblyShadow.app"}}}
            command = gate.command_for(prepared, "Control", root / "manifest.json", root / "build.json",
                                       capsule_path, root / "Control/r01-early.json",
                                       root / "Control/m07-T07-03-FullClosure-P03.json", root / "Control/unity.log")
            self.assertIn("-shadowM07Mode", command)
            self.assertIn("T07-03-FullClosure-P03", command)
            self.assertIn("-shadowEarlyCapsuleSha256", command)

    def test_rejection_command_has_no_m07_handoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            executable = root / "AssemblyShadow.app/Contents/MacOS/AssemblyShadow"
            capsule_path = root / "Type/r01-early.capsule"
            capsule_path.parent.mkdir()
            capsule_path.write_bytes(b"capsule")
            prepared = {"runner": type("Runner", (), {"executable_for": lambda self, _: executable})(),
                        "context": {"on": {"output": root / "AssemblyShadow.app"}}}
            command = gate.command_for(prepared, "Type", root / "manifest.json", root / "build.json",
                                       capsule_path, root / "Type/r01-early.json",
                                       root / "Type/unused-m07.json", root / "Type/unity.log")
            self.assertNotIn("-shadowM07Mode", command)
            self.assertNotIn("-shadowM07Result", command)

    def test_alternate_m07_mode_is_available_only_to_control(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            executable = root / "AssemblyShadow.app/Contents/MacOS/AssemblyShadow"
            capsule_path = root / "Control/r01-early.capsule"
            capsule_path.parent.mkdir()
            capsule_path.write_bytes(b"capsule")
            prepared = {"runner": type("Runner", (), {"executable_for": lambda self, _: executable})(),
                        "context": {"on": {"output": root / "AssemblyShadow.app"}}}
            command = gate.command_for(prepared, "Control", root / "manifest.json", root / "build.json",
                                       capsule_path, root / "Control/r01-early.json",
                                       root / "Control/m07-T07-01-Prefab-P01.json", root / "Control/unity.log",
                                       "T07-01-Prefab-P01")
            self.assertEqual(command[command.index("-shadowM07Mode") + 1], "T07-01-Prefab-P01")

    def test_default_matrix_excludes_unsupported_baseline(self):
        self.assertEqual(gate.DEFAULT_MODES, gate.MODES[:-1])
        self.assertNotIn("Baseline", gate.DEFAULT_MODES)
        self.assertIn("Oversize", gate.DEFAULT_MODES)
        self.assertIn("Mismatch", gate.DEFAULT_MODES)
        self.assertIn("NativeScript", gate.DEFAULT_MODES)

# Wire-level launcher tests replace only upstream install admission and the
# actual subprocess. Capsule reconstruction, files/hashes and early receipts
# remain real; M07's separate verifier is an explicit upstream adapter.
import copy
import importlib.util
import json
from unittest.mock import patch
from shadow_tools import VerificationError
from test_r01_early_results import make_capsule, emit_receipt, FIXED_ORDINARY


def load_launcher():
    spec = importlib.util.spec_from_file_location("r01_early_launcher_test",
        Path(gate.__file__).with_name("run-r01-early-players.py"))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def prepare_graph(root):
    (root / "Assets/AssemblyShadowDemo").mkdir(parents=True)
    (root / "_temp/AssemblyShadow").mkdir(parents=True)
    inputs = root / "inputs"; inputs.mkdir()
    data = make_capsule(inputs)
    def write(name, value):
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value)); return path
    paths = {key: write(key + ".json", {}) for key in ("fixture", "on", "off", "replay", "failures", "negative")}
    baseline = write("baseline.json", {})
    bundle = root / "resources/bundles/fixture.bundle"; bundle.parent.mkdir(parents=True); bundle.write_bytes(b"bundle")
    write("resources/resource-build-receipt.json", dict(bundleDirectory="bundles", bundles=[dict(name="fixture.bundle")]))
    fixtures = {}
    for key in ("P01", "P02", "P03", "P04", "P05", "R01-P03-InitializerThrow"):
        order = list(gate.m07.fixture_order("P03" if key == "R01-P03-InitializerThrow" else key))
        p = dict(patchId=key, loadOrder=order, dllOnly=key != "P05",
                 closure=[dict(name=r["name"], dll=Path(r["dllPath"]).name, sha256=r["dllSha256"],
                               pdb=Path(r["pdbPath"]).name if r["pdbPath"] else "", pdbSha256=r["pdbSha256"])
                          for r in data["inputs"] if r["name"] in order])
        fixtures[key] = dict(patch=p, root=inputs, path=write(key + ".json", p))
        if key == "P05":
            resource = write("replacement/P05/resource-build-receipt.json", dict(kind="synthetic replacement resources"))
            fixtures[key]["fixture"] = dict(replacementResourcePath=str(resource.parent))
    snapshot = root / "snapshot"
    ordinary = snapshot / "ReflectionBindings/Images" / (gate.capsule.FIXED_IMAGE_SHA + ".dll.bytes")
    ordinary.parent.mkdir(parents=True); ordinary.write_bytes(FIXED_ORDINARY)
    exe = root / "Player.app/Contents/MacOS/Player"; exe.parent.mkdir(parents=True); exe.write_text("synthetic process adapter")
    context = dict(manifest=dict(baselineBuildId=data["baselineBuildId"], runtimeAbiHash=data["runtimeAbiHash"],
                    candidateNames=data["candidates"], stableAotNames=data["stableAotNames"], baselineManifestPath=str(baseline)),
                   baseline=dict(resourceBaselinePath="resources"), fixtures=fixtures,
                   on=dict(output=root / "Player.app", path=paths["on"], snapshot={}, player=dict(inputSnapshot=str(snapshot))),
                   off=dict(path=paths["off"]), sourcePins={"fixture": "explicit-synthetic"})
    failure = dict(failures=dict(initializer=fixtures["R01-P03-InitializerThrow"]),
                   negative=dict(data=dict(outputPath=data["inputs"][0]["dllPath"], outputSha256=data["inputs"][0]["dllSha256"])))
    prepared = dict(context=context, failures=failure, inventory={p for p in root.rglob("*") if p.is_file()},
                    baselineResources={}, runner=type("Runner", (), {"executable_for": lambda self, _: exe})())
    return prepared, paths


class EarlyLaunchPipelineTests(unittest.TestCase):
    def launch(self, root, modes, exit_override=None, corrupt=None, m07_mode=gate.DEFAULT_M07_MODE, logs=None):
        launcher = load_launcher()
        prepared, paths = prepare_graph(root)
        output = root / "_temp/AssemblyShadow/run"
        args = ["--project-root", str(root), "--fixture-manifest", str(paths["fixture"]),
                "--on-build", str(paths["on"]), "--off-build", str(paths["off"]),
                "--replay-receipt", str(paths["replay"]), "--failure-fixtures", str(paths["failures"]),
                "--negative-input", str(paths["negative"]), "--output-root", str(output), "--m07-mode", m07_mode]
        for mode in modes: args += ["--mode", mode]
        pid = 5000
        def run(command, project, console, timeout):
            nonlocal pid
            pid += 1
            value = lambda name: command[command.index(name) + 1]
            cap = Path(value("-shadowEarlyCapsule")); data = gate.capsule.decode(cap.read_bytes())
            out = Path(value("-shadowEarlyResult")); receipt = emit_receipt(data, cap, out, pid)
            if corrupt: corrupt(receipt)
            out.write_text(json.dumps(receipt))
            refusal = ("[AssemblyShadowStartup] Failed: Bootstrap explicitly refused startup\n"
                       "[AssemblyShadowStartup] Terminating process before host continuation (exit=1)\n")
            unity_text, console_text = logs if logs is not None else (
                (refusal, "") if data["mode"] in gate.REJECTION_MODES else ("synthetic Unity log", "synthetic console"))
            console.write_text(console_text)
            Path(value("-logFile")).write_text(unity_text)
            if "-shadowM07Result" in command:
                imported = []
                for source, target in (("after-stage", "staged"), ("after-validate", "validated-resource-precheck-complete")):
                    snapshot = next(row for row in receipt["snapshots"] if row["phase"] == source)
                    imported.append(dict(phase=target, diagnostics=json.loads(snapshot["diagnosticsJson"])))
                Path(value("-shadowM07Result")).write_text(json.dumps(dict(
                    processId=pid, mode=m07_mode, result="Passed", snapshots=imported)))
            return dict(processId=pid, startedAtUnix=100.0 + pid, durationSeconds=1.0, timedOut=False,
                        exitCode=exit_override if exit_override is not None else 1 if data["mode"] in gate.REJECTION_MODES else 0)
        # The only reflection admission replaced is the existing separately
        # verified M00 build snapshot; the fixed payload bytes/hash are genuine.
        with patch.object(gate, "_prepare", return_value=prepared),              patch.object(gate.capsule, "from_context", wraps=gate.capsule.from_context),              patch.object(gate.m07.prior, "_reflection_snapshot"),              patch.object(launcher, "_run_one", side_effect=run):
            code = launcher.main(args)
        return code, output / "r01-early-launches.json", prepared

    def verify(self, path, prepared):
        with patch.object(gate, "_prepare", return_value=prepared),              patch.object(gate.m07.prior, "_reflection_snapshot"),              patch.object(gate.m07, "verify_case"):
            return gate.verify_suite(path)

    def test_all_modes_real_capsule_and_full_receipt_pipeline(self):
        with tempfile.TemporaryDirectory() as t:
            code, path, prepared = self.launch(Path(t).resolve(), list(gate.DEFAULT_MODES))
            self.assertEqual(code, 0)
            verified = self.verify(path, prepared)
            self.assertEqual(verified["result"], "PassedBoundedProfile")
            self.assertFalse(verified["milestoneAccepted"])
            self.assertTrue(verified["diagnosticOnly"])
            self.assertEqual(len(verified["modes"]), len(gate.DEFAULT_MODES))

    def test_baseline_remains_explicitly_incomplete(self):
        with tempfile.TemporaryDirectory() as t:
            code, path, prepared = self.launch(Path(t).resolve(), ["Baseline"])
            self.assertEqual(code, 0)
            self.assertEqual(self.verify(path, prepared)["result"], "DiagnosticIncomplete")

    def test_wrong_receipt_result_is_not_launcher_success(self):
        with tempfile.TemporaryDirectory() as t:
            code, path, _ = self.launch(Path(t).resolve(), ["Type"], corrupt=lambda d: d.update(result="Failed", error="witness failed"))
            self.assertEqual(code, 1)
            self.assertFalse(gate.read(path)["processLaunches"][0]["passed"])

    def test_signal_and_unrelated_nonzero_exit_never_count_as_expected_refusal(self):
        for exit_code in (-6, -11, 42, 139, 0):
            with self.subTest(exit=exit_code), tempfile.TemporaryDirectory() as t:
                code, path, prepared = self.launch(Path(t).resolve(), ["Type"], exit_override=exit_code)
                self.assertEqual(code, 1)
                with self.assertRaises(VerificationError): self.verify(path, prepared)

    def test_timeout_even_with_valid_receipt_is_rejected(self):
        launcher = load_launcher()
        with self.assertRaisesRegex(VerificationError, "timed out"):
            launcher._verify_process_output(dict(mode="Type"),
                dict(exitCode=1, timedOut=True), gate.DEFAULT_M07_MODE)

    def test_rebound_capsule_mutations_rejected_against_admitted_graph(self):
        mutations = [
            lambda d: d.update(baselineBuildId="other"),
            lambda d: d.update(runtimeAbiHash="b" * 64),
            lambda d: d.update(patchId="P01"),
            lambda d: d.update(candidates=d["candidates"][:-1], inputs=d["inputs"][:-1]),
            lambda d: d.update(inputs=list(reversed(d["inputs"]))),
            lambda d: d.update(prerequisiteFiles=d["prerequisiteFiles"][:-1]),
            lambda d: d.update(stableAotNames=["DifferentBootstrap"]),
        ]
        for mutate in mutations:
            with tempfile.TemporaryDirectory() as t:
                _, path, prepared = self.launch(Path(t).resolve(), ["Control"])
                launch = gate.read(path); row = launch["processLaunches"][0]
                cap = Path(row["capsulePath"]); data = gate.capsule.decode(cap.read_bytes()); mutate(data)
                cap.write_bytes(gate.capsule.encode(data))
                # Rebind every self-hash/projection, as a stale producer could.
                row["capsuleSha256"] = gate.digest(cap)
                row["command"][row["command"].index("-shadowEarlyCapsuleSha256") + 1] = row["capsuleSha256"]
                for owner in (row, launch):
                    for key in ("inputHashesBefore", "inputHashesAfter"): owner[key][str(cap)] = gate.digest(cap)
                out = Path(row["earlyResultPath"]); out.write_text(json.dumps(emit_receipt(data, cap, out, row["processId"])))
                row["earlyResultSha256"] = gate.digest(out)
                path.write_text(json.dumps(launch))
                with self.assertRaisesRegex(VerificationError, "admittedCapsule"):
                    self.verify(path, prepared)

    def test_m07_wrong_mode_and_process_provenance_mutants(self):
        with tempfile.TemporaryDirectory() as t:
            _, path, prepared = self.launch(Path(t).resolve(), ["Control"])
            original = gate.read(path)
            for key, value in (("processId", 9000), ("passed", False), ("error", "error"),
                               ("timedOut", True), ("exitCode", -6), ("durationSeconds", -1)):
                altered = copy.deepcopy(original); altered["processLaunches"][0][key] = value
                path.write_text(json.dumps(altered))
                with self.assertRaises(VerificationError): self.verify(path, prepared)
            altered = copy.deepcopy(original); row = altered["processLaunches"][0]
            m07 = Path(row["m07ResultPath"]); result = gate.read(m07); result["mode"] = "T07-01-Prefab-P01"
            m07.write_text(json.dumps(result)); row["m07ResultSha256"] = gate.digest(m07)
            path.write_text(json.dumps(altered))
            with self.assertRaisesRegex(VerificationError, "m07Mode"): self.verify(path, prepared)

    def test_alternative_control_patch_reconstructed_and_bound(self):
        with tempfile.TemporaryDirectory() as t:
            code, path, prepared = self.launch(Path(t).resolve(), ["Control"], m07_mode="T07-01-Prefab-P01")
            self.assertEqual(code, 0)
            self.assertEqual(self.verify(path, prepared)["result"], "PassedBoundedProfile")

    def test_all_m07_control_patches_have_no_console_initializer_markers(self):
        for m07_mode in ("T07-01-Prefab-P01", "T07-02-Nested-P02", "T07-03-FullClosure-P03",
                         "T07-12-P04-NonSerialized", "T07-13-P05-Rebuilt"):
            with self.subTest(mode=m07_mode), tempfile.TemporaryDirectory() as t:
                code, path, prepared = self.launch(Path(t).resolve(), ["Control"], m07_mode=m07_mode)
                self.assertEqual(code, 0)
                self.assertEqual(self.verify(path, prepared)["result"], "PassedBoundedProfile")
                launch = gate.read(path); row = launch["processLaunches"][0]
                early_path = Path(row["earlyResultPath"]); early = gate.read(early_path)
                self.assertEqual(early["patchId"], gate.m07.MODE_PATCH[m07_mode])
                self.assertEqual(early["initializerEvents"], [])
                committed = json.loads(early["snapshots"][-1]["diagnosticsJson"])
                order = list(gate.m07.fixture_order(early["patchId"]))
                self.assertEqual(committed["commitOrder"], order)
                self.assertTrue(all(a["moduleInitializerAttempted"] and a["moduleInitializerRan"]
                                    for a in committed["assemblies"]))
                # A fabricated Console event must fail even though the native
                # initializer lifecycle correctly covers every closure member.
                early["initializerEvents"] = [dict(name=order[0], diagnostics=copy.deepcopy(early["observerSamples"][0]))]
                early_path.write_text(json.dumps(early)); row["earlyResultSha256"] = gate.digest(early_path)
                path.write_text(json.dumps(launch))
                with self.assertRaisesRegex(VerificationError, "initializerOrder"):
                    self.verify(path, prepared)

    def test_rebound_receipt_hash_cannot_hide_imported_snapshot_divergence(self):
        for mode in ("Control", "OrdinaryFirst", "OrdinaryAfterReserve"):
            for source_phase, target_phase in (("after-stage", "staged"),
                                                ("after-validate", "validated-resource-precheck-complete")):
                for side in ("early", "m07"):
                    with self.subTest(mode=mode, phase=source_phase, side=side), tempfile.TemporaryDirectory() as t:
                        _, path, prepared = self.launch(Path(t).resolve(), [mode])
                        self.verify(path, prepared)
                        launch = gate.read(path); row = launch["processLaunches"][0]
                        receipt_path = Path(row[side + "ResultPath"])
                        receipt = gate.read(receipt_path)
                        phase = source_phase if side == "early" else target_phase
                        snapshot = next(item for item in receipt["snapshots"] if item["phase"] == phase)
                        diagnostics = json.loads(snapshot["diagnosticsJson"]) if side == "early" else snapshot["diagnostics"]
                        # A separately captured stable BCL cache entry would be
                        # admissible. An imported snapshot must be identical.
                        diagnostics["ordinaryClasses"].append(dict(assemblyName="mscorlib",
                            typeName="System.Object", isInterpreter=False,
                            isConstructedGeneric=False, usesStagedMetadata=False))
                        gate.m04._diagnostic(diagnostics, "admissible cache mutation")
                        if side == "early": snapshot["diagnosticsJson"] = json.dumps(diagnostics)
                        receipt_path.write_text(json.dumps(receipt))
                        row[side + "ResultSha256"] = gate.digest(receipt_path)
                        path.write_text(json.dumps(launch))
                        if side == "early":
                            gate.verify_early_receipt(receipt_path, Path(row["capsulePath"]), mode, row["processId"])
                        with self.assertRaisesRegex(VerificationError, "handoff.importedDiagnostics"):
                            self.verify(path, prepared)

    def test_handoff_compares_parsed_json_not_json_formatting(self):
        with tempfile.TemporaryDirectory() as t:
            _, path, prepared = self.launch(Path(t).resolve(), ["Control"])
            launch = gate.read(path); row = launch["processLaunches"][0]
            early_path = Path(row["earlyResultPath"]); receipt = gate.read(early_path)
            for snapshot in receipt["snapshots"]:
                snapshot["diagnosticsJson"] = json.dumps(json.loads(snapshot["diagnosticsJson"]), indent=2, sort_keys=True)
            early_path.write_text(json.dumps(receipt)); row["earlyResultSha256"] = gate.digest(early_path)
            path.write_text(json.dumps(launch))
            self.assertEqual(self.verify(path, prepared)["result"], "PassedBoundedProfile")

    def test_negative_requires_terminal_pair_and_no_host_continuation_in_either_stream(self):
        refusal = "[AssemblyShadowStartup] Failed: Bootstrap explicitly refused startup\n"
        terminal = "[AssemblyShadowStartup] Terminating process before host continuation (exit=1)\n"
        # Captured v2 Oversize shape: a genuine early receipt and exit=1, but
        # Unity ignored il2cpp_init(false) and M07 failed later with missing args.
        continued = refusal + ("Initialize engine version: 2022.3.62f2 (7670c08855a9)\n"
                               "ArgumentException: The specified path is not of a legal form (empty).\n"
                               "  at AssemblyShadowDemo.M07Probe.ReadInputs (...)\n"
                               "  at AssemblyShadowDemo.M07BootstrapRunner+<Start>d__3.MoveNext ()\n")
        cases = [(continued, ""), (continued + terminal, ""), (refusal, ""),
                 (terminal, ""), (refusal + terminal + "late output\n", ""),
                 ("[AssemblyShadowStartup] Failed: CallbackThrew\n" + terminal, ""),
                 ("[AssemblyShadowStartup] Failed: Invalid bootstrap configuration\n" + terminal, ""),
                 (refusal + terminal, "M07BootstrapRunner.Start\n"),
                 ("", ""), (refusal + terminal.replace("exit=1", "exit=2"), "")]
        for logs in cases:
            with self.subTest(logs=logs), tempfile.TemporaryDirectory() as t:
                code, path, prepared = self.launch(Path(t).resolve(), ["Oversize"], logs=logs)
                self.assertEqual(code, 1)
                launch = gate.read(path); row = launch["processLaunches"][0]
                self.assertEqual(row["exitCode"], 1)
                # Prove the independent offline gate does not trust launcher refusal.
                row.update(passed=True, error=""); path.write_text(json.dumps(launch))
                with self.assertRaises(VerificationError): self.verify(path, prepared)

    def test_terminal_pair_can_be_in_console_or_both_streams(self):
        pair = ("[AssemblyShadowStartup] Failed: Bootstrap explicitly refused startup\n"
                "[AssemblyShadowStartup] Terminating process before host continuation (exit=1)\n")
        for logs in (("", pair), (pair, pair)):
            with tempfile.TemporaryDirectory() as t:
                code, path, prepared = self.launch(Path(t).resolve(), ["Oversize"], logs=logs)
                self.assertEqual(code, 0)
                self.assertEqual(self.verify(path, prepared)["result"], "PassedBoundedProfile")

    def test_both_log_hashes_are_bound_and_rebound_continuation_is_rejected(self):
        for mode in ("Control", "Oversize"):
            for key, hash_key in (("logPath", "logSha256"), ("consolePath", "consoleSha256")):
                with self.subTest(mode=mode, stream=key), tempfile.TemporaryDirectory() as t:
                    _, path, prepared = self.launch(Path(t).resolve(), [mode])
                    launch = gate.read(path); row = launch["processLaunches"][0]; log = Path(row[key])
                    self.assertEqual(row[hash_key], gate.digest(log))
                    log.write_text(log.read_text() + "M07BootstrapRunner.Start\n")
                    with self.assertRaises(VerificationError): self.verify(path, prepared)
                    if mode == "Oversize":
                        row[hash_key] = gate.digest(log); path.write_text(json.dumps(launch))
                        with self.assertRaisesRegex(VerificationError, "continuation"):
                            self.verify(path, prepared)



if __name__ == "__main__":
    unittest.main()
