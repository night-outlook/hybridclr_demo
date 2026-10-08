"""Fixed R02 source authority. No Git writes, pin rewrites, or historical overrides."""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import sys
from evidence import require, read, binding

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import shadow_tools

TARGETS = "Docs/AssemblyShadow/History/M07R/R02/source-targets.json"
NAMES = {"demo": "hybridclr_demo", "hybridclr": "hybridclr", "hybridclrUnity": "hybridclr_unity", "il2cppPlus": "il2cpp_plus"}


def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=90)
    require(p.returncode == 0, "Git read failed: " + p.stderr.strip())
    return p.stdout.strip()


def commit(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{40}", value) is not None, "Exact lowercase commit required")
    return value


def inspect(project: Path, expected_head: str, role: str, targets: dict, remote=True):
    require(role in ("candidate", "control"), "Unknown R02 source role")
    require(project.is_absolute() and project == project.resolve(strict=True), "Canonical project required")
    commit(expected_head)
    require(targets.get("kind") == "R02SourceTargets" and targets.get("protocol") == "R02LocalBatch-v1", "Wrong source targets")
    selection = targets[role]
    require(git(project, "rev-parse", "HEAD") == expected_head, "Demo transport HEAD mismatch")
    require(git(project, "branch", "--show-current") == selection["branch"], "Wrong demo branch")
    pins = read(project / shadow_tools.PINS)
    require(pins["demo"]["revision"] == selection["sourceCommit"], "Wrong executable source anchor")
    require(pins["unityVersion"] == "2022.3.62f2" and pins["target"] == "StandaloneOSX" and pins["architecture"] == "arm64", "Wrong build target")
    rows = {}
    for key, name in NAMES.items():
        item = selection["repositories"][name]
        expected = expected_head if key == "demo" else commit(item["commit"])
        root = (project / pins[key]["localPath"]).resolve(strict=True)
        require(root == Path(git(root, "rev-parse", "--show-toplevel")), "Not an owning repository root")
        origin = git(root, "remote", "get-url", "origin")
        allowed = ("https://github.com/night-outlook/" + name, "https://github.com/night-outlook/" + name + ".git", "git@github.com:night-outlook/" + name + ".git")
        require(origin in allowed, "Wrong repository identity: " + name)
        head = git(root, "rev-parse", "HEAD")
        require(head == expected, "Wrong repository HEAD: " + name)
        require(not git(root, "status", "--porcelain=v1", "--untracked-files=all"), "Dirty repository: " + name)
        require(pins[key]["revision"] == (selection["sourceCommit"] if key == "demo" else expected), "Pin mismatch: " + name)
        remote_head = None
        if remote:
            branch = selection["branch"] if key == "demo" else item["branch"]
            lines = git(root, "ls-remote", "origin", "refs/heads/" + branch).splitlines()
            require(len(lines) == 1 and lines[0].split()[0] == expected, "Remote HEAD changed: " + name)
            remote_head = expected
        rows[name] = {"path": str(root), "head": head, "origin": origin, "remoteHead": remote_head}
    shadow_tools.verify_demo(project, pins["demo"])
    return {"kind": "R02SourceAuthority", "result": "SourceVerifiedNotBuildAccepted", "role": role,
            "demoHead": expected_head, "sourceCommit": selection["sourceCommit"], "repositories": rows,
            "sourcePins": pins, "sourcePinBinding": binding(project / shadow_tools.PINS), "runtimeAcceptance": False}


def common_sources(candidate: Path, control: Path):
    # Same complete demo source graph, with pins/documents the only permitted
    # differences. This includes startup, all fixtures and all measurement code.
    a = {p: v for p, v in shadow_tools.tree(candidate, "HEAD").items() if not shadow_tools.metadata_only(p)}
    b = {p: v for p, v in shadow_tools.tree(control, "HEAD").items() if not shadow_tools.metadata_only(p)}
    require(a == b, "Control/candidate executable source graphs differ")
    return {"kind": "R02CommonManagedSources", "result": "Passed", "blobCount": len(a),
            "blobs": a, "runtimeAcceptance": False}
