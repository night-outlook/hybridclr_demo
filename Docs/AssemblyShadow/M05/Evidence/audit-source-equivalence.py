"""M05 task-local read-only source/artifact audit; writes one new audit receipt."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess

BUILD = "09a15e686a4e7581e362175f4aa99d6bde80de55"
VERIFIER = "6f0123839ba1fe01e18c29858b15fefc1cc7b12c"
TOOLS = {
    "Tools/AssemblyShadow/m05_results.py",
    "Tools/AssemblyShadow/m05_types.py",
    "Tools/AssemblyShadow/tests/test_m05_results.py",
    "Tools/AssemblyShadow/tests/test_m05_type_keys.py",
}
PINS = "ProjectSettings/AssemblyShadowSourcePins.json"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def run(command, root=None):
    return subprocess.check_output(command, cwd=root, env=dict(os.environ, LC_ALL="C"))


def git(root, *args):
    return run(["git", *args], root)


def metadata(path):
    return path == PINS or path.startswith("Docs/AssemblyShadow/")


def tree(root, revision):
    result = {}
    for item in git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if not item:
            continue
        header, name = item.split(b"\t", 1)
        mode, kind, blob = header.decode().split()
        require(kind == "blob" and mode in ("100644", "100755"), "Unsupported tree item")
        result[name.decode()] = (mode, blob)
    return result


def sha(path):
    require(path.is_file() and not path.is_symlink(), "Missing/symlinked audit input: " + str(path))
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read(path):
    require(path.is_file() and not path.is_symlink(), "Missing/symlinked JSON")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def abi(pins):
    values = [pins[name] for name in ("unityVersion", "target", "architecture")]
    values += [pins[name]["revision"] for name in ("hybridclr", "il2cppPlus", "hybridclrUnity")]
    return hashlib.sha256(("assembly-shadow-runtime-abi:1\n" + "\n".join(values)).encode()).hexdigest()


def audit(root):
    before, after = tree(root, BUILD), tree(root, VERIFIER)
    delta = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    changed_inputs = {path for path in delta if not metadata(path)}
    require(changed_inputs == TOOLS, "Executable/build-input change outside exact verifier correction")
    require(all(before.get(path) == after.get(path) for path in before.keys() | after.keys()
                if path not in TOOLS and not metadata(path)), "Unexpected executable source drift")
    live = tree(root, "HEAD")
    require({p: v for p, v in live.items() if not metadata(p)} ==
            {p: v for p, v in after.items() if not metadata(p)}, "Live non-metadata tree differs from verifier")
    for path, (_, blob) in after.items():
        if metadata(path):
            continue
        source = root / path
        require(source.is_file() and not source.is_symlink(), "Missing/nonregular source " + path)
        data = source.read_bytes()
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob,
                "Working bytes differ from verifier Git tree: " + path)
    for path in git(root, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0"):
        require(not path or metadata(path), "Untracked non-metadata source: " + path)
    pins = read(root / PINS)
    baseline_path = root / "HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M05-Baseline-v6/baseline-manifest.json"
    baseline = read(baseline_path)
    frozen = baseline["sourcePins"]
    require(frozen["demo"]["revision"] == BUILD and pins["demo"]["revision"] == VERIFIER, "Build/tooling pins conflated")
    require(pins["demo"]["url"] == frozen["demo"]["url"] and pins["demo"]["localPath"] == frozen["demo"]["localPath"], "Demo identity/path changed")
    require(abi(pins) == abi(frozen) == baseline["runtimeAbiHash"], "Runtime ABI changed")
    repositories = []
    for name in ("hybridclr", "il2cppPlus", "hybridclrUnity"):
        require(pins[name] == frozen[name], "Native/package source pin changed: " + name)
        repository = (root / pins[name]["localPath"]).resolve()
        head = git(repository, "rev-parse", "HEAD").decode().strip()
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all").decode()
        require(head == pins[name]["revision"] and not status, "Paired repository drift: " + name)
        repositories.append(dict(name=name, path=str(repository), revision=head, status=status))
    launch_path = root / "_temp/AssemblyShadow/M05V6Execution-FlFy78z1/Players/player-launches.json"
    launch = read(launch_path)
    require(launch["inputHashesBefore"] == launch["inputHashesAfter"] and launch["inputsUnchanged"], "Original Player inputs changed")
    watched = dict(launch["inputHashesAfter"])
    processes = launch["processLaunches"]
    require(len(processes) == 19 and len({p["processId"] for p in processes}) == 19, "Fresh process matrix incomplete")
    for process in processes:
        require(process["exitCode"] == 0 and process["passed"] and not process["timedOut"], "Failed actual Player")
        watched[process["resultPath"]] = process["resultSha256"]
        result = read(Path(process["resultPath"]))
        require(result["processId"] == process["processId"] and result["mode"] == process["mode"], "Process/result identity mismatch")
        if result["rawDiagnosticsPath"]:
            watched[result["rawDiagnosticsPath"]] = result["rawDiagnosticsSha256"]
    for file, expected in watched.items():
        require(sha(Path(file)) == expected, "Changed frozen input/result: " + file)
    original = root.parent / "hybridclr_demo"
    original_status = git(original, "status", "--short").decode().splitlines()
    require(set(original_status) == {
        " M Assets/Settings/Renderer2D.asset", "?? .DS_Store", "?? Assets/Editor.meta",
        "?? Documents/HybridCLR_AssemblyShadow_Design_and_Plans/.DS_Store"}, "Original checkout status membership changed")
    editor = " ".join(run(["ps", "-p", "13313", "-o", "pid=,lstart=,comm="]).decode().split())
    require(editor.startswith("13313 Thu Aug 27 01:46:54 2026 ") and editor.endswith("/Contents/MacOS/Unity"), "Original Editor identity changed")
    return dict(schemaVersion=1, milestone="M05", kind="FrozenExecutableOfflineVerifierEquivalence", success=True,
                runtimeAcceptance=False, checkedUtc=dt.datetime.now(dt.timezone.utc).isoformat(),
                project=str(root), frozenDemoBuildRevision=BUILD, offlineVerifierRevision=VERIFIER,
                currentHead=git(root, "rev-parse", "HEAD").decode().strip(), sourceDelta=delta,
                changedNonMetadataInputs=sorted(changed_inputs),
                unchangedOtherNonMetadataFiles=sum(not metadata(p) and p not in TOOLS for p in after),
                verifierFileHashes=[dict(path=p, sha256=sha(root / p)) for p in sorted(TOOLS)],
                currentPins=pins, frozenBuildPins=frozen, runtimeAbiHash=abi(pins), repositories=repositories,
                baselineManifest=dict(path=str(baseline_path), sha256=sha(baseline_path)),
                originalLaunchReceipt=dict(path=str(launch_path), sha256=sha(launch_path)),
                frozenInputsAndResults=[dict(path=p, sha256=h) for p, h in sorted(watched.items())],
                originalCheckoutStatusMembership=original_status, originalEditor=editor,
                limitation="Exact tooling-only source equivalence and unchanged evidence; not a rebuild or standalone milestone acceptance.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists() and not args.output.is_symlink(), "Refusing existing output")
    result = audit(args.project_root.resolve())
    result["auditSourceSha256"] = sha(Path(__file__).resolve())
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(success=True, unchangedFiles=result["unchangedOtherNonMetadataFiles"],
                          frozenFiles=len(result["frozenInputsAndResults"]), output=str(args.output))))
