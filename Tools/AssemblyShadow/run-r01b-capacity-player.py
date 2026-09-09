#!/usr/bin/env python3
"""Run the R01B 8,192/8,193 capacity case in one owned IL2CPP Player."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

from r00_player_inputs import verify_inputs
from r01b_capacity_inputs import (canonical_directory, canonical_file, collect_direct_inputs, digest,
                                  executable_for, validate_mixed_workload, validate_overflow, validate_workload)
from shadow_tools import require


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--on-build", required=True, type=Path)
    parser.add_argument("--off-build", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--workload-manifest", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--mixed-manifest", type=Path)
    parser.add_argument("--mixed-corpus", type=Path)
    parser.add_argument("--overflow-receipt", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--mixed", action="store_true",
                        help="Commit M07 P03, retain three failed ordinary reservations, then fill the shared ledger")
    args = parser.parse_args()

    project = canonical_directory(args.project_root, "project root")
    require((project / "Assets/AssemblyShadowDemo").is_dir(), "Project is not the Assembly Shadow demo")
    fixture = canonical_file(args.fixture_manifest, "M07 fixture manifest")
    on_path = canonical_file(args.on_build, "NativeOn build receipt")
    off_path = canonical_file(args.off_build, "NativeOff build receipt")
    replay = canonical_file(args.replay_receipt, "M07 replay receipt")
    workload_path = canonical_file(args.workload_manifest, "R01B workload manifest")
    corpus = canonical_directory(args.corpus_root, "R01B corpus root")
    mixed_manifest = mixed_corpus = None
    if args.mixed:
        require(args.mixed_manifest is not None and args.mixed_corpus is not None,
                "mixed mode requires a separate mixed manifest and corpus")
        mixed_manifest = canonical_file(args.mixed_manifest, "R01B mixed workload manifest")
        mixed_corpus = canonical_directory(args.mixed_corpus, "R01B mixed corpus root")
    else:
        require(args.mixed_manifest is None and args.mixed_corpus is None,
                "ordinary mode must not claim a mixed workload")
    overflow_path = canonical_file(args.overflow_receipt, "R01B overflow receipt")
    require(1 <= args.timeout <= 3600, "timeout must be in 1..3600 seconds")
    output_root = args.output_root
    require(output_root.is_absolute() and output_root == output_root.resolve() and not output_root.exists() and
            output_root.parent == project / "_temp/AssemblyShadow", "output root must be a new direct _temp/AssemblyShadow child")

    context = verify_inputs(project, fixture, on_path, off_path, replay)
    workload, workload_files = validate_workload(workload_path, corpus, deep=False)
    mixed_workload_files = []
    if mixed_manifest is not None and mixed_corpus is not None:
        mixed_workload, mixed_workload_files = validate_mixed_workload(mixed_manifest, mixed_corpus, deep=False)
        require(mixed_workload["source"]["ordinaryManifestPath"] == str(workload_path) and
                mixed_workload["source"]["ordinaryCorpusRoot"] == str(corpus),
                "Mixed workload is not derived from the selected ordinary corpus")
    overflow, overflow_dll = validate_overflow(overflow_path, deep=False)
    require(overflow["assembly"]["name"].casefold() not in {row["name"].casefold() for row in workload["assemblies"]} and
            overflow["assembly"]["sha256"] not in {row["sha256"] for row in workload["assemblies"]},
            "Overflow DLL is not distinct from the supported workload")
    app = context["on"]["output"]
    executable = executable_for(app)
    direct_inputs = collect_direct_inputs(workload_path, workload_files, overflow_path, overflow_dll,
                                          fixture, on_path, off_path, replay, app)
    if mixed_manifest is not None and mixed_corpus is not None:
        direct_inputs.update({mixed_manifest, *mixed_workload_files})
        direct_inputs.update(Path(path).resolve(strict=True) for path in mixed_workload["shadow"]["assemblies"] for path in [path["path"]])
    hashes_before = {str(path): digest(path) for path in sorted(direct_inputs)}

    output_root.mkdir()
    prefix = "r01b-mixed" if args.mixed else "r01b-capacity"
    result_path = output_root / (prefix + "-result.json")
    m07_result_path = output_root / "m07-T07-03-FullClosure-P03.json" if args.mixed else None
    unity_log = output_root / (prefix + ".unity.log")
    console_log = output_root / (prefix + ".console.log")
    command = [str(executable), "-batchmode", "-nographics",
               "-shadowR01BManifest", str(workload_path), "-shadowR01BCorpus", str(corpus),
               "-shadowR01BOverflowDll", str(overflow_dll),
               "-shadowR01BOverflowName", overflow["assembly"]["name"],
               "-shadowR01BOverflowSha256", overflow["assembly"]["sha256"],
               "-shadowR01BResult", str(result_path), "-logFile", str(unity_log)]
    if args.mixed:
        command[3:3] = ["-shadowR01BMixed", "-shadowM07Mode", "T07-03-FullClosure-P03",
                        "-shadowM07Fixtures", str(fixture), "-shadowM07PlayerReceipt", str(on_path),
                        "-shadowM07Result", str(m07_result_path), "-shadowR01BMixedManifest", str(mixed_manifest),
                        "-shadowR01BMixedCorpus", str(mixed_corpus)]
    started = time.time()
    timed_out = False
    with console_log.open("xb") as console:
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                   stdout=console, stderr=subprocess.STDOUT)
        print(f"R01B capacity Player started pid={process.pid}", flush=True)
        try:
            exit_code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                exit_code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                exit_code = process.wait(timeout=15)

    result = None
    error = ""
    if result_path.is_file() and not result_path.is_symlink():
        try:
            result = json.loads(result_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError, UnicodeError) as problem:
            error = str(problem)
    expected = context["on"]["player"]
    m07_result = None
    if m07_result_path is not None and m07_result_path.is_file() and not m07_result_path.is_symlink():
        try:
            m07_result = json.loads(m07_result_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError, UnicodeError) as problem:
            error = error or str(problem)
    passed = (not timed_out and exit_code == 0 and type(result) is dict and result.get("schemaVersion") == 1 and
              result.get("kind") == "R01BCapacityPlayerResult" and result.get("milestone") == "R01B" and
              result.get("result") == "Passed" and result.get("error") == "" and result.get("il2cpp") is True and
              result.get("platform") == "OSXPlayer" and result.get("processId") == process.pid and
              result.get("resultPath") == str(result_path) and
              result.get("buildGuid") == expected["buildGuid"] and
              result.get("baselineBuildId") == expected["baselineBuildId"] and
              result.get("runtimeAbiHash") == expected["runtimeAbiHash"] and
              result.get("scenario") == ("MixedShadowRetainedFailures" if args.mixed else "OrdinaryEnvelope") and
              (not args.mixed or type(m07_result) is dict and m07_result.get("mode") == "T07-03-FullClosure-P03" and
               m07_result.get("result") == "Passed" and m07_result.get("processId") == process.pid))
    verify_inputs(project, fixture, on_path, off_path, replay)
    hashes_after = {str(path): digest(path) for path in sorted(direct_inputs)}
    receipt = {
        "schemaVersion": 1,
        "kind": "R01BCapacityPlayerLaunchReceipt",
        "milestone": "R01B",
        "diagnosticOnly": True,
        "scenario": "MixedShadowRetainedFailures" if args.mixed else "OrdinaryEnvelope",
        "projectRoot": str(project),
        "fixtureManifestPath": str(fixture),
        "fixtureManifestSha256": digest(fixture),
        "onBuildPath": str(on_path),
        "onBuildSha256": digest(on_path),
        "offBuildPath": str(off_path),
        "offBuildSha256": digest(off_path),
        "replayReceiptPath": str(replay),
        "replayReceiptSha256": digest(replay),
        "workloadManifestPath": str(workload_path),
        "workloadManifestSha256": digest(workload_path),
        "corpusRoot": str(corpus),
        "mixedManifestPath": str(mixed_manifest) if mixed_manifest is not None else "",
        "mixedManifestSha256": digest(mixed_manifest) if mixed_manifest is not None else "",
        "mixedCorpusRoot": str(mixed_corpus) if mixed_corpus is not None else "",
        "overflowReceiptPath": str(overflow_path),
        "overflowReceiptSha256": digest(overflow_path),
        "playerOutput": str(app),
        "playerExecutable": str(executable),
        "command": command,
        "processId": process.pid,
        "startedAtUnix": started,
        "durationSeconds": time.time() - started,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "passed": passed,
        "resultPath": str(result_path),
        "resultSha256": digest(result_path) if result_path.is_file() else "",
        "m07ResultPath": str(m07_result_path) if m07_result_path is not None else "",
        "m07ResultSha256": digest(m07_result_path) if m07_result_path is not None and m07_result_path.is_file() else "",
        "unityLogPath": str(unity_log),
        "consoleLogPath": str(console_log),
        "inputHashesBefore": hashes_before,
        "inputHashesAfter": hashes_after,
        "inputsUnchanged": hashes_before == hashes_after,
        "error": error or (result or {}).get("error", "No result file"),
        "note": "This launch receipt is provenance. verify-r01b-capacity-result.py is the strict acceptance gate.",
    }
    with (output_root / (prefix + "-player-launch.json")).open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"result": "Passed" if passed and hashes_before == hashes_after else "Failed",
                      "processId": process.pid, "exitCode": exit_code, "durationSeconds": receipt["durationSeconds"]}))
    return int(not passed or hashes_before != hashes_after)


if __name__ == "__main__":
    raise SystemExit(main())
