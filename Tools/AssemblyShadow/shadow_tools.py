"""Read-only source verification and narrowly scoped, recoverable cache handling."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import uuid

REPOSITORIES = ("hybridclr", "hybridclrUnity", "il2cppPlus", "demo")
GENERATED = frozenset("hybridclr/generated/" + name for name in (
    "AssemblyManifest.cpp", "MethodBridge.cpp", "UnityVersion.h", "libil2cpp-version.txt"))
RECEIPT = "assembly-shadow-install.json"
PINS = "ProjectSettings/AssemblyShadowSourcePins.json"
PACKAGE = "com.code-philosophy.hybridclr"
CACHES = ("Library/Bee", "Library/Il2cppBuildCache")


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink(), f"Missing or symlinked JSON: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise VerificationError(f"Invalid JSON {path}: {error}") from error


def command(args, cwd=None):
    try:
        process = subprocess.run(args, cwd=cwd, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise VerificationError(f"Cannot run {args[0]}: {error}") from error
    require(process.returncode == 0,
            f"{args[0]} failed ({process.returncode}): {process.stderr.decode('utf-8', 'replace').strip()}")
    return process.stdout


def git(root, *args):
    return command(["git", "-C", str(root), *args])


def metadata_only(path):
    return path == PINS or path.startswith("Docs/AssemblyShadow/")


def safe_file(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative,
            f"Invalid source path: {relative!r}")
    components = relative.split("/")
    require(not Path(relative).is_absolute() and all(part not in ("", ".", "..") for part in components),
            f"Unsafe source path: {relative!r}")
    result = root
    for component in components:
        result = result / component
        require(not result.is_symlink(), f"Symlink is not allowed: {result}")
    require(result.resolve().is_relative_to(root.resolve()), f"Path escapes root: {relative}")
    return result


def files_under(root):
    require(root.is_dir() and not root.is_symlink(), f"Missing or symlinked directory: {root}")
    result = set()
    for base, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            item = Path(base) / name
            require(not item.is_symlink(), f"Symlink is not allowed: {item}")
        result.update((Path(base) / name).relative_to(root).as_posix() for name in files)
    return result


def tree(root, revision):
    result = {}
    for record in git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if not record:
            continue
        header, path = record.split(b"\t", 1)
        mode, kind, object_id = header.decode("ascii").split()
        require(kind == "blob" and mode in ("100644", "100755"),
                f"Symlink/submodule/unsupported mode in {root}: {path!r}")
        name = path.decode("utf-8")
        safe_file(root, name)
        result[name] = object_id
    return result


def verify_blob(path, object_id):
    require(path.is_file(), f"Pinned source file is missing: {path}")
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    require(actual == object_id, f"Working bytes do not match pinned Git blob: {path}")
    return hashlib.sha256(data).hexdigest()


def repository_paths(project, pins):
    require(pins.get("schemaVersion") == 1, "Unsupported source pin schema")
    entries = pins.get("repositories", pins)
    paths = {}
    for name in REPOSITORIES:
        entry = entries.get(name)
        require(isinstance(entry, dict), f"Missing repository pin: {name}")
        require(re.fullmatch(r"[0-9a-fA-F]{40}", str(entry.get("revision", ""))) is not None,
                f"{name} must specify a full exact SHA")
        require(isinstance(entry.get("url"), str) and entry["url"], f"Missing {name} URL")
        local = entry.get("localPath")
        require(isinstance(local, str) and local and not Path(local).is_absolute(),
                f"{name} localPath must be relative to the project")
        candidate = project / local
        require(not candidate.is_symlink(), f"Symlinked repository path: {candidate}")
        root = candidate.resolve()
        actual_root = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
        require(root == actual_root, f"{name} path is not its Git root")
        paths[name] = root
    require(paths["demo"] == project, "demo localPath must identify this project")
    require(len(set(paths.values())) == 4, "Four distinct repository roots are required")
    return entries, paths


def source_inventory(entries, paths):
    expected = {}
    for name in ("hybridclr", "hybridclrUnity", "il2cppPlus"):
        root = paths[name]
        revision = entries[name]["revision"].lower()
        require(git(root, "rev-parse", "HEAD").decode().strip() == revision, f"{name} HEAD differs from pin")
        require(not git(root, "status", "--porcelain=v1", "--untracked-files=all").strip(), f"{name} is dirty")
        tracked = tree(root, revision)
        hashes = {path: verify_blob(safe_file(root, path), oid) for path, oid in tracked.items()}
        if name == "hybridclrUnity":
            continue
        prefix = "libil2cpp/" if name == "il2cppPlus" else "hybridclr/"
        native = {path[len(prefix):] for path in tracked if path.startswith(prefix)}
        require(native, f"No native source files in {name}")
        require(files_under(root / prefix.rstrip("/")) == native, f"Unexpected native files in {name}")
        for path in tracked:
            if not path.startswith(prefix):
                continue
            installed = path[len(prefix):] if name == "il2cppPlus" else path
            require(installed not in expected, f"Colliding installed path: {installed}")
            expected[installed] = {"source": name, "sha256": hashes[path]}
    return expected


def verify_demo(project, entry):
    revision = entry["revision"]
    git(project, "merge-base", "--is-ancestor", revision, "HEAD")
    pinned = {path: oid for path, oid in tree(project, revision).items() if not metadata_only(path)}
    current = {path: oid for path, oid in tree(project, "HEAD").items() if not metadata_only(path)}
    require(pinned == current, "Demo HEAD contains build-input changes after the source pin")
    for path, oid in pinned.items():
        verify_blob(safe_file(project, path), oid)
    untracked = git(project, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    require(not any(path and not metadata_only(path) for path in untracked), "Demo has untracked build inputs")
    # Ignored C# or asmdef files still compile in Unity and must not evade Git status.
    for directory in ("Assets", "Packages"):
        for suffix in ("*.cs", "*.asmdef"):
            for path in (project / directory).rglob(suffix):
                require(path.relative_to(project).as_posix() in pinned, f"Unpinned Unity code input: {path}")


def default_installed_root(project):
    host = {"darwin": "OSXEditor", "win32": "WindowsEditor", "linux": "LinuxEditor"}.get(sys.platform)
    require(host is not None, "Specify --installed-root for this host")
    return project / "HybridCLRData" / ("LocalIl2CppData-" + host) / "il2cpp/libil2cpp"


def verify(project, installed=None, demo_source=True, expected_shadow="off"):
    project = project.resolve()
    pins = read_json(project / PINS)
    entries, paths = repository_paths(project, pins)
    version_text = (project / "ProjectSettings/ProjectVersion.txt").read_text()
    match = re.search(r"^m_EditorVersion:\s*(\S+)$", version_text, re.M)
    require(match is not None and match[1] == pins.get("unityVersion"), "Unity version differs from pins")
    require(pins.get("target") in ("StandaloneOSX", "StandaloneWindows64"), "Unsupported M00 target")
    expected = source_inventory(entries, paths)
    installed = installed or default_installed_root(project)
    # Do not resolve away symlinks before checking every path component.
    for parent in (installed, *installed.parents):
        require(not parent.is_symlink(), f"Symlinked installed path: {parent}")
    receipt = read_json(installed / RECEIPT)
    require(receipt.get("schemaVersion") == 1 and receipt.get("installMode") == "PinnedLocal", "Invalid install receipt schema/mode")
    for key in ("unityVersion", "target"):
        require(receipt.get(key) == pins.get(key), f"Receipt {key} differs from pins")
    for name in REPOSITORIES:
        observed = receipt.get("repositories", {}).get(name, {})
        require(all(observed.get(key) == entries[name].get(key) for key in ("url", "revision", "localPath")),
                f"Receipt {name} source pin mismatch")
    require(receipt.get("packageRevision") == entries["hybridclrUnity"]["revision"], "Package revision mismatch")
    package = read_json(paths["hybridclrUnity"] / "package.json")
    require(package.get("name") == PACKAGE and receipt.get("packageVersion") == package.get("version"), "Package identity/version mismatch")
    dependency = read_json(project / "Packages/manifest.json").get("dependencies", {}).get(PACKAGE, "")
    require(dependency.startswith("file:"), "Package manifest does not use pinned local UPM source")
    require((project / "Packages" / dependency[5:]).resolve() == paths["hybridclrUnity"], "UPM package path differs from pin")
    exclusions = receipt.get("generatedFileExclusions", [])
    require(isinstance(exclusions, list) and len(exclusions) == len(GENERATED) and set(exclusions) == GENERATED,
            "Generated exclusions must match the fixed four-file allowlist")
    observed = {}
    for entry in receipt.get("sourceFileHashes", []):
        require(isinstance(entry, dict), "Invalid source hash entry")
        path = entry.get("path")
        safe_file(installed, path)
        require(path not in observed, f"Duplicate receipt path: {path}")
        observed[path] = {"source": entry.get("source"), "sha256": entry.get("sha256")}
    require(observed == expected, "Receipt inventory/hashes do not match the exact pinned Git sources")
    expected_paths = set(expected) | GENERATED | {RECEIPT}
    actual_paths = files_under(installed)
    require(actual_paths == expected_paths,
            f"Installed inventory differs: missing={sorted(expected_paths - actual_paths)}, extra={sorted(actual_paths - expected_paths)}")
    for relative, info in expected.items():
        path = safe_file(installed, relative)
        if relative not in GENERATED:
            require(hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"], f"Installed byte mismatch: {relative}")
    require(receipt.get("defaultShadowMacro") == 0 and receipt.get("defaultShadowMacroSource") == "AssemblyShadowConfig.h",
            "Receipt does not assert the default-OFF native feature")
    header = (installed / "AssemblyShadowConfig.h").read_text()
    require(re.search(r"(?m)^\s*#ifndef\s+HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\s*$", header) is not None and
            re.search(r"(?m)^\s*#define\s+HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\s+0\s*$", header) is not None,
            "Native Shadow feature does not default to OFF")
    require('#include "AssemblyShadowConfig.h"' in (installed / "il2cpp-config.h").read_text(), "Native feature header is not included")
    player_settings = (project / "ProjectSettings/ProjectSettings.asset").read_text()
    arguments = re.search(r"(?m)^  additionalIl2CppArgs:([^\n]*)$", player_settings)
    require(arguments is not None, "Native build arguments are missing from Player settings")
    overrides = re.findall(r"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=(\S+)", arguments[1])
    overrides = [value.rstrip('"\'') for value in overrides]
    require(len(overrides) <= 1 and all(value in ("0", "1") for value in overrides), "Ambiguous native Shadow compiler definitions")
    require("-UHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW" not in arguments[1], "Ambiguous native Shadow undefinition")
    configured_mode = "on" if overrides == ["1"] else "off"
    require(configured_mode == expected_shadow, f"Native build configuration is {configured_mode}, expected {expected_shadow}")
    if demo_source:
        verify_demo(project, entries["demo"])
    return {"unityVersion": pins["unityVersion"], "target": pins["target"], "sourceFiles": len(expected),
            "installedFiles": len(actual_paths), "demoSourceVerified": demo_source, "configuredShadowMode": configured_mode,
            "receiptSha256": hashlib.sha256((installed / RECEIPT).read_bytes()).hexdigest()}


def print_pins(project):
    pins = read_json(project / PINS)
    entries, paths = repository_paths(project, pins)
    result = {"unityVersion": pins["unityVersion"], "target": pins["target"],
              "host": platform.platform(), "machine": platform.machine(), "repositories": {}}
    for name, root in paths.items():
        result["repositories"][name] = {
            "path": str(root), "pinnedRevision": entries[name]["revision"],
            "head": git(root, "rev-parse", "HEAD").decode().strip(),
            "branch": git(root, "branch", "--show-current").decode().strip(),
            "commitDate": git(root, "show", "-s", "--format=%cI", "HEAD").decode().strip(),
            "dirty": git(root, "status", "--short").decode().strip(),
            "remotes": git(root, "remote", "-v").decode().strip(),
        }
    compiler = shutil.which("clang++") or shutil.which("cl")
    result["compiler"] = command([compiler, "--version"]).decode().splitlines()[0] if compiler and not compiler.endswith("cl.exe") else compiler
    if sys.platform == "darwin":
        result["sdk"] = command(["xcrun", "--show-sdk-path"]).decode().strip()
    return result


def check_editor_stopped(project):
    helper = safe_file(project, ".agents/skills/unity-debug/scripts/UnityDebug.Common.ps1")
    require(helper.is_file(), "Shared Unity safety helper is required for cache mutation")
    shell = shutil.which("pwsh")
    require(shell is not None, "PowerShell 7 is required for exact-project Editor detection")
    quote = lambda value: "'" + str(value).replace("'", "''") + "'"
    script = "$ErrorActionPreference = 'Stop'; . " + quote(helper) + "; if (Test-UnityProjectRunning -ProjectPath " + quote(project) + ") { exit 2 }; exit 0"
    process = subprocess.run([shell, "-NoLogo", "-NoProfile", "-Command", script], capture_output=True, timeout=45)
    require(process.returncode == 0, "Cache move blocked: project Editor is running, detection failed, or ownership is ambiguous")


def clean_cache(project, apply=False):
    project = project.resolve()
    require((project / "ProjectSettings/ProjectVersion.txt").is_file(), "Not a Unity project")
    require(Path(git(project, "rev-parse", "--show-toplevel").decode().strip()).resolve() == project, "Project must be a Git root")
    targets = [safe_file(project, relative) for relative in CACHES]
    for path in targets:
        require(not path.exists() or path.is_dir(), f"Cache target is not a directory: {path}")
    result = {"project": str(project), "applied": apply, "targets": [str(path) for path in targets if path.exists()], "moved": []}
    if not apply:
        return result
    check_editor_stopped(project)
    backup_root = safe_file(project, "_temp/AssemblyShadow/CacheBackups")
    backup = backup_root / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8])
    backup.mkdir(parents=True, exist_ok=False)
    result["backup"] = str(backup)
    manifest = backup / "manifest.json"
    manifest.write_text(json.dumps(result, indent=2) + "\n")
    for path in targets:
        check_editor_stopped(project)
        path = safe_file(project, path.relative_to(project).as_posix())
        if path.exists():
            destination = backup / path.name
            path.rename(destination)
            result["moved"].append({"source": str(path), "backup": str(destination)})
            manifest.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("verify", "pins", "cache"))
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--skip-demo-source", action="store_true", help="Development inspection only; not M00 acceptance")
    parser.add_argument("--verify-demo-source", action="store_true", help="Default: verify demo build source")
    parser.add_argument("--expect-shadow", choices=("off", "on"), default="off")
    parser.add_argument("--apply", action="store_true", help="Move only the two whitelisted caches; default is dry-run")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        require(not (args.skip_demo_source and args.verify_demo_source), "Conflicting demo verification options")
        if args.operation == "pins":
            result = print_pins(args.project.resolve())
        elif args.operation == "cache":
            result = clean_cache(args.project, args.apply)
        else:
            result = verify(args.project, args.installed_root, not args.skip_demo_source, args.expect_shadow)
            if not args.json:
                for label in ("Unity version", "hybridclr source revision", "il2cpp_plus source revision",
                              "Package revision", "Target platform", "HybridCLR installed"):
                    print("[PASS] " + label)
                print("[PASS] Shadow native default OFF; configured mode " + result["configuredShadowMode"].upper())
                print("[PASS] Demo build-source revision" if result["demoSourceVerified"] else "[SKIP] Demo source: development inspection only")
        print(json.dumps(result, indent=2))
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
