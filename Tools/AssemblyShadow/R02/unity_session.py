#!/usr/bin/env python3
"""Own one Unity build command and retire only its exact Roslyn descendants.

Run inside evidence.run's fresh POSIX process group. This supervisor does NOT
create another group or change evidence.run's no-survivor success criterion.
Unknown descendants fail closed and are left for the outer failure cleanup.
"""
from __future__ import annotations
import argparse
import ctypes
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from evidence import binding, require, write

POLICY = "R02OwnedUnityRoslyn-v1"
TERM_GRACE = 5.0
KILL_GRACE = 3.0


def census(group):
    # Only the owned group is retained. lstart guards against PID reuse.
    proc = subprocess.Popen(["ps", "-ww", "-axo", "pid=,pgid=,stat=,lstart=,args="],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            env=dict(os.environ, LC_ALL="C"))
    stdout, stderr = proc.communicate(timeout=3)
    require(proc.returncode == 0, "Owned process census unavailable")
    rows = []
    for line in stdout.splitlines():
        parts = line.strip().split(None, 8)
        require(len(parts) == 9, "Malformed process census")
        pid, pgid = int(parts[0]), int(parts[1])
        if pgid == group and pid not in (os.getpid(), proc.pid):
            rows.append({"pid": pid, "group": pgid, "state": parts[2], "start": " ".join(parts[3:8]), "command": parts[8]})
    return sorted(rows, key=lambda row: row["pid"])


def roslyn_command(command, compiler):
    # ps need not quote executable paths containing spaces. Match the exact
    # DLL path as a boundary, not an arbitrary VBCSCompiler substring.
    executable, separator, rest = command.partition(" exec ")
    if not separator or Path(executable.strip('"')).name != "dotnet":
        return False
    expected = str(compiler)
    return any(rest == prefix or rest.startswith(prefix + " ")
               for prefix in (expected, '"' + expected + '"'))


def same_identity(original, current):
    if original is None or any(original[k] != current[k] for k in ("pid", "group", "start")):
        return False
    # A known child may become a zombie between census and waitpid. Wait for
    # disappearance; never signal/reclassify it as a new live process.
    return original["command"] == current["command"] or current.get("state", "").startswith("Z")


def reap():
    # On Linux CI the supervisor adopts grandchildren; Darwin's init reaps
    # orphaned descendants. Never wait for or affect another process's child.
    while True:
        try:
            if os.waitpid(-1, os.WNOHANG)[0] == 0:
                return
        except ChildProcessError:
            return


def retire(group, compiler, *, scan=census, send=os.kill, clock=time.monotonic, sleep=time.sleep):
    result = {"policy": POLICY, "group": group, "compiler": str(compiler),
              "termGraceSeconds": TERM_GRACE, "killGraceSeconds": KILL_GRACE,
              "clean": False, "actions": []}
    try:
        initial = scan(group)
        result["before"] = initial
        require(all(roslyn_command(row["command"], compiler) for row in initial),
                "Unknown owned descendant; compiler completion not authorized")
        identities = {row["pid"]: row for row in initial}
        for sig, grace in ((signal.SIGTERM, TERM_GRACE), (signal.SIGKILL, KILL_GRACE)):
            live = scan(group)
            require(all(same_identity(identities.get(row["pid"]), row) for row in live),
                    "Owned process identity changed during compiler completion")
            for row in live:
                # Reauthenticate immediately before each individual signal.
                current = {item["pid"]: item for item in scan(group)}.get(row["pid"])
                if current is None:
                    continue
                require(same_identity(row, current), "PID identity changed before signal")
                if current.get("state", "").startswith("Z"):
                    continue
                try:
                    send(row["pid"], sig)
                    result["actions"].append({"pid": row["pid"], "signal": int(sig), "identity": row})
                except ProcessLookupError:
                    pass
            deadline = clock() + grace
            while True:
                reap()
                remaining = scan(group)
                if not remaining:
                    result["after"] = []
                    result["clean"] = True
                    return result
                require(all(same_identity(identities.get(row["pid"]), row) for row in remaining),
                        "New or changed descendant during compiler completion")
                if clock() >= deadline:
                    break
                sleep(0.05)
        result["after"] = remaining
        result["error"] = "Owned compiler did not disappear after bounded termination"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    return result


def compiler_path(unity):
    unity = Path(unity)
    require(unity.is_absolute() and unity.is_file(), "Explicit Unity executable required")
    contents = unity.parent.parent
    require(unity.name == "Unity" and unity.parent.name == "MacOS" and contents.name == "Contents",
            "Expected pinned Unity.app/Contents/MacOS/Unity")
    compiler = contents / "DotNetSdkRoslyn/VBCSCompiler.dll"
    # Strict binding rejects symlinked paths. The path is from the supplied
    # Unity installation, not from a process command or user-supplied allowlist.
    return compiler, binding(compiler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unity", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    require(os.name == "posix" and os.getpgrp() == os.getpid() and os.getsid(0) == os.getpid(), "Fresh owned process group required")
    require(command and not args.receipt.exists(), "Command and unused receipt required")
    result = {"kind": "R02UnityCommandCompletion", "policy": POLICY, "result": "Failed",
              "command": command, "commandExitCode": None, "startedAtUnix": time.time(),
              "runtimeAcceptance": False}
    try:
        compiler, identity = compiler_path(args.unity)
        result["compilerBinding"] = identity
        if sys.platform.startswith("linux"):
            # Prevent zombie accumulation under container PID 1 during tests.
            require(ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0,
                    "Cannot establish owned Linux child reaping")
        result["commandExitCode"] = subprocess.Popen(command, stdin=subprocess.DEVNULL).wait()
        result["completion"] = retire(os.getpgrp(), compiler)
        require(binding(compiler) == identity, "Unity compiler file changed during command")
        if result["commandExitCode"] == 0 and result["completion"]["clean"]:
            result["result"] = "Passed"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    result["endedAtUnix"] = time.time()
    write(args.receipt, result)
    return 0 if result["result"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
