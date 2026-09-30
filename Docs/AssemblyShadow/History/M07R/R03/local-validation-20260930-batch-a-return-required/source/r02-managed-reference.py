"""Owned .NET build/run processes for the R02 host witness.

Build servers are disabled per invocation, not shut down globally. A successful
host assertion does not override a failed process-group cleanup receipt.
"""
from __future__ import annotations
import os
from pathlib import Path
from evidence import binding, check_binding, loads, require, run, write

VARIANTS = (("Baseline", "", 3000, 102),
            ("P01", "ASSEMBLY_SHADOW_P01", 3001, 111),
            ("P03", "ASSEMBLY_SHADOW_P03", 3003, 111))


def build_plan(dotnet: str, csproj: Path, output: Path, name: str, define: str):
    require((name, define) in [(v[0], v[1]) for v in VARIANTS], "Unknown managed host variant")
    require(csproj.is_absolute() and output.is_absolute(), "Absolute managed input/output required")
    binary_dir = output / ("managed-bin-" + name)
    command = [dotnet, "build", str(csproj), "--configuration", name,
               "--disable-build-servers", "--output", str(binary_dir),
               "--property:UseSharedCompilation=false", "-nodeReuse:false",
               "--property:WitnessDefine=" + define,
               "--property:BaseIntermediateOutputPath=" + str(output / ("managed-obj-" + name)) + "/"]
    return command, binary_dir / "ManagedTests.dll"


def host_environment(env: dict | None):
    result = dict(os.environ if env is None else env)
    result.update(MSBUILDDISABLENODEREUSE="1", DOTNET_CLI_USE_MSBUILD_SERVER="0")
    return result


def verify_result(stdout: Path, marker: int, checks: int):
    # Only this explicit program record is acceptance data. Compiler output,
    # exit code, or a substring containing 'Passed' is not an assertion result.
    rows = []
    for line in stdout.read_text(encoding="utf-8-sig").splitlines():
        if line.lstrip().startswith("{"):
            value = loads(line)
            if isinstance(value, dict) and value.get("kind") == "R02ManagedHostTests":
                rows.append(value)
    require(len(rows) == 1, "Expected exactly one managed witness result")
    row = rows[0]
    require(row.get("result") == "Passed" and row.get("unityPlayerRun") is False,
            "Managed witness failed or claimed Player execution")
    require(type(row.get("marker")) is int and row["marker"] == marker, "Wrong managed witness variant")
    require(type(row.get("checks")) is int and row["checks"] == checks, "Managed assertion coverage changed")
    return row


def run_suite(dotnet: str, csproj: Path, project: Path, output: Path, env: dict | None = None):
    rows = []
    for name, define, marker, checks in VARIANTS:
        command, assembly = build_plan(dotnet, csproj, output, name, define)
        build_dir = output / ("managed-" + name + "-build")
        run_dir = output / ("managed-" + name + "-run")
        row = {"cell": "managed-" + name, "result": "Failed", "unityPlayerRun": False}
        built = run(command, project, build_dir, 180, host_environment(env))
        row["build"] = binding(build_dir / "command.json")
        if built["result"] != "Passed":
            row["runResult"] = "Blocked"
            row["reason"] = "Build or owned process-group cleanup failed"
        else:
            try:
                row["assembly"] = binding(assembly)
                invoked = run([dotnet, "exec", str(assembly)], project, run_dir, 180, host_environment(env))
                row["run"] = binding(run_dir / "command.json")
                require(invoked["result"] == "Passed", "Host run or owned process-group cleanup failed")
                check_binding(row["assembly"])
                row["assertions"] = verify_result(run_dir / "stdout.log", marker, checks)
                row["runResult"] = "Passed"
                row["result"] = "Passed"
            except (OSError, ValueError, KeyError, TypeError) as error:
                row["runResult"] = "Failed"
                row["reason"] = type(error).__name__ + ": " + str(error)
        write(output / ("managed-" + name + "-result.json"), row)
        rows.append(row)
    return rows
