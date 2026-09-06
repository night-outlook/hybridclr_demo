#!/usr/bin/env python3
"""Run the complete post-Player validation suite for M06 v8."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow")
ORIGINAL = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo")
ROOT = PROJECT / "_temp" / "AssemblyShadow"
UPSTREAM = ROOT / "m06-v8-continuation.json"
RECOVERY = ROOT / "M06CloseoutValidation-v8"
COMPLETED = ROOT / "M06CloseoutValidation-v8-retry2"
OUTPUT = ROOT / "M06CloseoutValidation-v8-retry4"
STATE = ROOT / "m06-closeout-validation-v8.json"
PWSH = Path("/usr/local/microsoft/powershell/7/pwsh")
EXPECTED_DEMO_DIRTY = {
    " M Assets/AssemblyShadowDemo/Scenes/M06Bootstrap.unity",
    " M Assets/HybridCLRGenerate/AOTGenericReferences.cs",
    " M Assets/HybridCLRGenerate/link.xml",
    " M ProjectSettings/AssemblyShadowSettings.asset",
    " M ProjectSettings/ProjectSettings.asset",
    " M Tools/AssemblyShadow/m06_results.py",
    " M Tools/AssemblyShadow/tests/test_m06_results.py",
}
EXPECTED_ORIGINAL_DIRTY = {
    " M Assets/Settings/Renderer2D.asset",
    "?? .DS_Store",
    "?? .agents/.DS_Store",
    "?? .codex/.DS_Store",
    "?? Assets/Editor.meta",
    "?? Documents/HybridCLR_AssemblyShadow_Design_and_Plans/.DS_Store",
}
PAIRED = {
    Path("/Users/ah/GitHub/hybridclr/hybridclr"): "a19db144751f4f016769b90e61a80b8c27578678",
    Path("/Users/ah/GitHub/hybridclr/il2cpp_plus"): "5b12ee96e574999d0eb82a6200d95a5b63c7fcfc",
    Path("/Users/ah/GitHub/hybridclr/hybridclr_unity"): "8d2e811fb37f4427ea15321369c883a61975a57d",
}


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular file: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def output(command: list[str], cwd: Path) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True, env={**os.environ, "LC_ALL": "C"})


def optional_process(pid: int, cwd: Path) -> str:
    result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "pid=,lstart=,command="], cwd=cwd,
                            text=True, capture_output=True, env={**os.environ, "LC_ALL": "C"})
    require(result.returncode in (0, 1), "Unable to inspect process identity: " + result.stderr.strip())
    return " ".join(result.stdout.split())


def status(root: Path) -> set[str]:
    return set(output(["git", "status", "--short"], root).splitlines())


def shadow_unity() -> list[str]:
    return [line.strip() for line in output(["/bin/ps", "ax", "-o", "command="], PROJECT).splitlines()
            if line.strip().startswith("/Applications/Unity/") and "-projectPath " + str(PROJECT) in line]


def run(name: str, command: list[str], timeout: int, environment: dict[str, str] | None = None) -> dict:
    require(not shadow_unity(), "Shadow-project Unity is running before " + name)
    log = OUTPUT / (name + ".log")
    before_unity_logs = set((PROJECT / "_temp").glob("UnityExec_*.log"))
    started = time.time()
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " START " + name, flush=True)
    with log.open("xb") as stream:
        completed = subprocess.run(command, cwd=PROJECT, stdin=subprocess.DEVNULL, stdout=stream,
                                   stderr=subprocess.STDOUT, timeout=timeout,
                                   env={**os.environ, "LC_ALL": "C", **(environment or {})})
    require(completed.returncode == 0, f"{name} failed with exit {completed.returncode}; log={log}")
    require(not shadow_unity(), name + " returned before its Unity process exited")
    new_unity_logs = sorted(set((PROJECT / "_temp").glob("UnityExec_*.log")) - before_unity_logs)
    result = {"name": name, "command": command, "durationSeconds": time.time() - started,
              "logPath": str(log), "logSha256": digest(log),
              "unityLogs": [{"path": str(path), "sha256": digest(path)} for path in new_unity_logs]}
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " PASS " + name, flush=True)
    return result


def recover(name: str, command: list[str], root: Path = RECOVERY) -> dict:
    log = root / (name + ".log")
    require(log.is_file() and not log.is_symlink(), "Missing/nonregular completed closeout log: " + str(log))
    unity_logs = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("[INFO] Log: "):
            continue
        path = Path(line.removeprefix("[INFO] Log: ").strip())
        require(path.is_absolute() and path.parent == PROJECT / "_temp" and
                path.is_file() and not path.is_symlink(), "Recovered Unity log is missing or outside the task root")
        unity_logs.append({"path": str(path), "sha256": digest(path)})
    stat = log.stat()
    started = getattr(stat, "st_birthtime", stat.st_mtime)
    result = {"name": name, "command": command, "durationSeconds": max(0.0, stat.st_mtime - started),
              "logPath": str(log), "logSha256": digest(log), "unityLogs": unity_logs,
              "recoveredAfterCloseoutInterruption": True}
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME " + name, flush=True)
    return result


def main() -> int:
    require(not OUTPUT.exists() and not STATE.exists(), "M06 v8 closeout output already exists")
    initial_demo_status = status(PROJECT)
    require(EXPECTED_DEMO_DIRTY <= initial_demo_status and all(
        row in EXPECTED_DEMO_DIRTY or row[3:].startswith("Docs/AssemblyShadow/M06/")
        for row in initial_demo_status),
        "Unexpected source change exists before closeout: " + repr(sorted(initial_demo_status)))
    upstream = read(UPSTREAM)
    require(upstream.get("result") == "Passed", "M06 v8 runtime continuation did not pass")
    require(digest(Path(upstream["strictReceipt"])) == upstream["strictReceiptSha256"], "M06 strict receipt changed")
    strict = read(Path(upstream["strictReceipt"]))
    require(strict.get("result") == "Passed" and strict.get("caseCount") == 28, "M06 strict receipt is incomplete")
    require(not shadow_unity(), "Shadow-project Unity remains open after runtime capture")
    OUTPUT.mkdir()
    commands: list[dict] = []

    compiler_root = ROOT / "M05RawAdmissionCompiler-955e889bd4c1442eaf694f53ff6a0ff3" / "Assemblies"
    raw_configuration = PROJECT / "ProjectSettings" / "AssemblyShadowRawTypeAdmissions.json"
    require(len(list(compiler_root.glob("*.dll"))) == 36 and raw_configuration.is_file(), "Preserved real M05 compiler boundary is missing")
    python_command = [sys.executable, "-m", "unittest", "discover", "-s", "Tools/AssemblyShadow/tests", "-q"]
    python = recover("python-tests", python_command)
    commands.append(python)
    text = Path(python["logPath"]).read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Ran (\d+) tests? in", text)
    require(match is not None and re.search(r"(?m)^OK$", text) and "skipped=" not in text, "Full Python suite was not an unskipped pass")
    python["testCount"] = int(match.group(1))

    native_receipts = []
    scripts = {
        "m03": "run-m03-native-tests.py", "visibility": "run-m03-visibility-tests.py",
        "m04": "run-m04-native-tests.py", "m05": "run-m05-native-tests.py", "m06": "run-m06-native-tests.py",
    }
    for stem, script in scripts.items():
        receipt = RECOVERY / (stem + "-native-tests.json")
        native_command = [sys.executable, str(PROJECT / "Tools" / "AssemblyShadow" / script),
                          "--output", str(receipt)]
        commands.append(recover(stem + "-native", native_command))
        require(read(receipt).get("success") is True, stem + " native receipt did not pass")
        native_receipts.append({"name": stem, "path": str(receipt), "sha256": digest(receipt)})

    install_receipt = ROOT / "m00-install-receipt.json"
    install_repeatability = ROOT / "m00-install-repeatability.json"
    install_command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(PROJECT / ".agents" / "skills" / "unity-debug" / "scripts" / "Invoke-UnityMethod.ps1"),
        "-Method", "AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability", "-ProjectPath", str(PROJECT),
        "-BuildTarget", "StandaloneOSX", "-TimeoutSec", "3600"]
    install = recover("install-repeatability", install_command)
    require("[SUCCESS] Unity method completed." in Path(install["logPath"]).read_text(encoding="utf-8", errors="replace"),
            "Recovered install-repeatability log does not contain the wrapper success boundary")
    commands.append(install)
    require(install_receipt.is_file() and install_repeatability.is_file(), "Pinned installation emitted no stable receipts")

    installed_before_command = [sys.executable,
        str(PROJECT / "Tools" / "AssemblyShadow" / "verify-installed-runtime.py"), "--project", str(PROJECT),
        "--skip-demo-source", "--expect-shadow", "on", "--json"]
    commands.append(recover("installed-source-before-editor", installed_before_command, COMPLETED))

    editor_command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(PROJECT / "Tools" / "AssemblyShadow" / "Invoke-ShadowEditorTests.ps1"),
        "-TestFilter", "HybridCLR.Editor.AssemblyShadow.Tests;AssemblyShadowDemo.EditorTests", "-TimeoutSec", "3600"]
    editor_command_result = recover("editor-tests-wrapper", editor_command, COMPLETED)
    commands.append(editor_command_result)
    editor_text = Path(editor_command_result["logPath"]).read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"(?m)^Unity test output: (.+)$", editor_text)
    require(len(matches) == 1, "Recovered Editor wrapper does not identify exactly one test output")
    editor_root = Path(matches[0])
    require(editor_root.is_absolute() and editor_root.parent == ROOT and editor_root.is_dir() and not editor_root.is_symlink(),
            "Recovered Editor output is missing or outside the evidence root")
    xml_path, unity_log = editor_root / "results.xml", editor_root / "unity.log"
    test_run = ET.parse(xml_path).getroot()
    summary = {key: test_run.attrib.get(key, "") for key in ("result", "total", "passed", "failed", "skipped", "inconclusive")}
    require(summary["result"] == "Passed" and int(summary["total"]) == int(summary["passed"]) and int(summary["total"]) > 0 and
            all(int(summary[key]) == 0 for key in ("failed", "skipped", "inconclusive")), "Fresh Editor suite was not a complete pass: " + repr(summary))

    installed_final_command = [sys.executable,
        str(PROJECT / "Tools" / "AssemblyShadow" / "verify-installed-runtime.py"), "--project", str(PROJECT),
        "--skip-demo-source", "--expect-shadow", "on", "--json"]
    commands.append(recover("installed-source-final", installed_final_command, COMPLETED))

    require(status(PROJECT) == initial_demo_status, "Shadow demo changed during closeout: " + repr(sorted(status(PROJECT))))
    require(status(ORIGINAL) == EXPECTED_ORIGINAL_DIRTY, "Original checkout status differs: " + repr(sorted(status(ORIGINAL))))
    original_editor = optional_process(13313, PROJECT)
    require(not original_editor or
            (original_editor.startswith("13313 Thu Aug 27 01:46:54 2026 ") and "/Contents/MacOS/Unity" in original_editor),
            "Original Editor identity changed or was replaced: " + original_editor)
    for repository, revision in PAIRED.items():
        require(output(["git", "rev-parse", "HEAD"], repository).strip() == revision and not status(repository),
                "Paired source repository drift: " + str(repository))

    value = {
        "schemaVersion": 1, "milestone": "M06", "kind": "PostPlayerCloseoutValidation", "result": "Passed",
        "upstreamStatePath": str(UPSTREAM), "upstreamStateSha256": digest(UPSTREAM), "python": python,
        "nativeReceipts": native_receipts,
        "installReceipt": {"path": str(install_receipt), "sha256": digest(install_receipt)},
        "installRepeatability": {"path": str(install_repeatability), "sha256": digest(install_repeatability)},
        "editor": {"root": str(editor_root), "resultsPath": str(xml_path), "resultsSha256": digest(xml_path),
                   "unityLogPath": str(unity_log), "unityLogSha256": digest(unity_log), **summary},
        "commands": commands, "demoStatus": sorted(status(PROJECT)), "originalStatus": sorted(status(ORIGINAL)),
        "originalEditor": original_editor, "originalEditorState": "PresentUntouched" if original_editor else "AbsentAtCloseout",
    }
    write_new(STATE, value)
    print(json.dumps({"result": "Passed", "state": str(STATE), "editorTests": summary["total"],
                      "pythonTests": python["testCount"]}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("M06 v8 closeout FAILED: " + repr(error), file=sys.stderr, flush=True)
        raise
