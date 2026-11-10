#!/usr/bin/env python3
"""Fail-closed production build roster + linked allocator tripwire for R03 native B1.

The native B1 host driver defines global C++ allocation overrides and main().
It is a standalone test, not a VM compilation input. This host-side verifier
can validate the installed tree and the ACTUAL linked GameAssembly nm -gU
stdout. It is not a Player startup or runtime acceptance result.
"""
from __future__ import annotations
from pathlib import Path

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
