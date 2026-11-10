#!/usr/bin/env python3
"""Fail-closed production build roster + linked allocator tripwire for R03 native B1.

The native B1 host driver defines global C++ allocation overrides and main().
It is a standalone test, not a VM compilation input. This host-side verifier
can validate the installed tree and the ACTUAL linked GameAssembly nm -gU
stdout. It is not a Player startup or runtime acceptance result.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json

HOST_NAME = "AssemblyShadowFirstFailureV2Host.cpp"
BAD_PREFIXES = ("__Znw", "__Zna", "__Zdl", "__Zda",
                "_Znw", "_Zna", "_Zdl", "_Zda")
DEFINED = frozenset(("T", "D", "B", "S", "W", "V", "R"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inspect(installed_libil2cpp: Path, linked_defined_nm: str) -> dict:
    """Reject a source roster that can rebuild the oneuse-11 malloc crash.

    `nm -gU GameAssembly.dylib` is deliberately used by the caller on macOS:
    it lists only external, defined symbols. We still parse the symbol type
    so an undefined libc++ import cannot be misidentified as an override.
    """
    root = Path(installed_libil2cpp)
    require(root.is_absolute() and root.is_dir() and not root.is_symlink() and
            root.resolve(strict=True) == root,
            "Canonical installed libil2cpp root required")
    driver = root / "vm" / HOST_NAME
    require(not driver.exists() and not driver.is_symlink(),
            "Standalone allocation host test driver is installed in Unity VM source roster")
    require(type(linked_defined_nm) is str and bool(linked_defined_nm.strip()),
            "Actual linked nm output required; no missing/empty-symbol waiver")
    bad = []
    parsed = 0
    for line in linked_defined_nm.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[-2] in DEFINED:
            parsed += 1
            name = parts[-1]
            if name.startswith(BAD_PREFIXES):
                bad.append(name)
    require(parsed > 0, "No defined linked symbols observed")
    require(not bad, "Global C++ allocation override linked into GameAssembly: " +
            ", ".join(sorted(set(bad))))
    return {"kind": "R03B1InstalledSourceAndLinkedAllocatorExclusionV1",
            "result": "PassedInstalledTreeAndDefinedSymbols_NotPlayerStartup",
            "hostDriverAbsentFromInstalledVM": True,
            "linkedHostAllocatorOverrides": 0,
            "definedSymbolsInspected": parsed,
            "actualUnityPlayerStarted": False,
            "runtimeAcceptance": False, "R03Accepted": False}


def attest(evidence_directory: Path, installed_libil2cpp: Path,
           game_assembly: Path, nm_stdout: str,
           nm_stderr: str, nm_exit_code: int) -> dict:
    """Persist actual nm stdout and exclusion verdict, including a failure.

    Called after a real Unity build but before starting ANY Player. A repeated
    verification must re-derive byte-identical evidence; it cannot overwrite
    the first immutable observation. The actual libil2cpp root and GameAssembly
    digest bind this report, not a host-test substitute.
    """
    evidence = Path(evidence_directory)
    binary = Path(game_assembly)
    require(evidence.is_absolute() and evidence.is_dir() and
            evidence.resolve(strict=True) == evidence and
            not evidence.is_symlink(), "Existing canonical build evidence root required")
    require(binary.is_absolute() and binary.is_file() and
            binary.resolve(strict=True) == binary and
            not binary.is_symlink(), "Actual canonical GameAssembly required")
    require(type(nm_stdout) is str and type(nm_stderr) is str and
            type(nm_exit_code) is int,
            "Raw nm process output and exact integer exit status required")
    raw = nm_stdout.encode("utf-8")
    def digest(source: bytes) -> str:
        return hashlib.sha256(source).hexdigest()
    def digest_file(path: Path) -> str:
        hashed = hashlib.sha256()
        with path.open("rb") as stream:
            for data in iter(lambda: stream.read(1024 * 1024), b""):
                hashed.update(data)
        return hashed.hexdigest()
    observed = None
    failure = None
    try:
        require(nm_exit_code == 0, "Actual nm -gU process failed: " + str(nm_exit_code))
        observed = inspect(installed_libil2cpp, nm_stdout)
    except ValueError as error:
        failure = str(error)
    result = {
        "schemaVersion": 1, "kind": "R03B1ActualLinkedAllocatorExclusionReceiptV1",
        "result": "PassedSourceAndLinkedDefinedExclusion_NotPlayerStartup"
                  if failure is None else "RejectedNativeLinkedRoster_NotPlayerRun",
        "nmArgv": ["nm", "-gU", str(binary)],
        "nmExitCode": nm_exit_code,
        "nmStdoutSha256": digest(raw),
        "nmStdoutBytes": len(raw),
        "nmStderr": nm_stderr,
        "nmStderrSha256": digest(nm_stderr.encode("utf-8")),
        "nativeInstalledLibil2cpp": str(installed_libil2cpp),
        "actualGameAssembly": str(binary),
        "actualGameAssemblySha256": digest_file(binary),
        "verifiedExclusion": observed,
        "failure": failure,
        "actualUnityPlayerStarted": False,
        "runtimeAcceptance": False, "R03Accepted": False,
    }
    def exclusive_or_same(path: Path, data: bytes) -> None:
        require(not path.is_symlink(), "Linked evidence destination is forbidden")
        if path.exists():
            require(path.is_file() and path.read_bytes() == data,
                    "Prior exclusive B1 linked receipt changed: " + str(path))
        else:
            with path.open("xb") as stream:
                stream.write(data)
    exclusive_or_same(evidence / "native-b1-linked-symbols.nm", raw)
    receipt_data = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8")
    exclusive_or_same(evidence / "native-b1-linked-roster.json", receipt_data)
    require(failure is None, "Actual linked allocator roster refused: " + str(failure))
    return result
