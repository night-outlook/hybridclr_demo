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
from process_identity import attach, same_birth

POLICY = "R02OwnedUnityRoslyn-v2"
TERM_GRACE = 5.0
KILL_GRACE = 3.0


class CensusError(ValueError):
    def __init__(self, message, members):
        super().__init__(message)
        self.members = members


def census(group):
    # Only the owned group is retained. Birth identity comes from the kernel;
    # never parse ps lstart, whose display may change while Darwin exits.
    proc = subprocess.Popen(["ps", "-ww", "-axo", "pid=,pgid=,stat=,args="],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            env=dict(os.environ, LC_ALL="C"))
    try:
        stdout, stderr = proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.communicate()
        raise
    require(proc.returncode == 0, "Owned process census unavailable")
    rows = []
    for line in stdout.splitlines():
        parts = line.strip().split(None, 3)
        require(len(parts) >= 3, "Malformed process census")
        pid, pgid = int(parts[0]), int(parts[1])
        if pgid == group and pid not in (os.getpid(), proc.pid):
            rows.append({"pid": pid, "group": pgid, "state": parts[2], "command": parts[3] if len(parts) == 4 else ""})
    bound = []
    for row in rows:
        try:
            attached = attach(row)
        except (OSError, ValueError) as error:
            raise CensusError(str(error), rows) from error
        if attached is not None:
            bound.append(attached)
    return sorted(bound, key=lambda row: row["pid"])


def roslyn_command(command, compiler):
    # ps need not quote executable paths containing spaces. Match the exact
    # DLL path as a boundary, not an arbitrary VBCSCompiler substring.
    executable, separator, rest = command.partition(" exec ")
    if not separator or Path(executable.strip('"')).name != "dotnet":
        return False
    expected = str(compiler)
    return any(rest == prefix or rest.startswith(prefix + " ")
               for prefix in (expected, '"' + expected + '"'))


def exiting(row):
    info = row.get("kernel")
    return bool(info and (info.get("exiting") or info.get("zombie")))


def same_identity(original, current):
    # Production censuses always carry kernel identity. Display start/argv can
    # disappear in Darwin exit(), and are retained only as diagnostics.
    if original is None:
        return False
    if "kernel" in original or "kernel" in current:
        if not same_birth(original.get("kernel"), current.get("kernel")):
            return False
        return original["command"] == current["command"] or exiting(current)
    # Explicit synthetic policy rows from the original tests; not a production
    # fallback when kernel information is unavailable (census raises instead).
    return all(original[k] == current[k] for k in ("pid", "group", "start")) and (
        original["command"] == current["command"] or current.get("state", "").startswith("Z"))


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
              "clean": False, "actions": [], "observations": [], "after": []}
    phase = "initial"

    def observe(label):
        nonlocal phase
        phase = label
        try:
            rows = scan(group)
        except CensusError as error:
            result["after"] = error.members
            result["observations"].append({"phase": label, "members": error.members,
                                           "censusError": str(error)})
            raise
        # Persist the actual rejecting snapshot BEFORE any policy assertion.
        result["after"] = rows
        result["observations"].append({"phase": label, "atMonotonic": clock(), "members": rows})
        require(len(result["observations"]) <= 512 and len(rows) <= 64,
                "Owned completion census budget exceeded")
        return rows

    def authenticate(identities, rows):
        for row in rows:
            expected = identities.get(row["pid"])
            if not same_identity(expected, row):
                result["identityMismatch"] = {"phase": phase, "expected": expected, "observed": row}
                raise ValueError("New or changed descendant during compiler completion")

    try:
        initial = observe("initial")
        result["before"] = initial
        require(all(roslyn_command(row["command"], compiler) for row in initial),
                "Unknown owned descendant; compiler completion not authorized")
        identities = {row["pid"]: row for row in initial}
        for sig, grace in ((signal.SIGTERM, TERM_GRACE), (signal.SIGKILL, KILL_GRACE)):
            live = observe("before-" + sig.name)
            authenticate(identities, live)
            for row in live:
                checked = observe("signal-identity-" + sig.name)
                authenticate(identities, checked)
                current = {item["pid"]: item for item in checked}.get(row["pid"])
                if current is None:
                    continue
                # Exiting/zombie instances are waited for, not signalled or
                # called clean. A changed live argv still fails authentication.
                if exiting(current) or current.get("state", "").startswith("Z"):
                    continue
                try:
                    send(row["pid"], sig)
                    result["actions"].append({"pid": row["pid"], "signal": int(sig), "identity": current})
                except ProcessLookupError:
                    pass
            deadline = clock() + grace
            while True:
                reap()
                remaining = observe("wait-" + sig.name)
                if not remaining:
                    result["clean"] = True
                    return result
                authenticate(identities, remaining)
                if clock() >= deadline:
                    break
                sleep(0.05)
        result["error"] = "Owned compiler did not disappear after bounded termination"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result["error"] = type(error).__name__ + ": " + str(error)
        result["errorPhase"] = phase
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
