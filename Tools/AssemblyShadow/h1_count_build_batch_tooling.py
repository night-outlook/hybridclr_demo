#!/usr/bin/env python3
"""Strict H1 build batch with split reproduction behavior/tooling identity.

Candidate behavior and tooling remain one source anchor. Reproduction behavior
stays pinned to the protected unfixed source while Unity runs from the exact
reviewed tooling-only successor authenticated by candidate source-targets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h1_count_build_batch as base
import h1_reproduction_tooling as repro_tools
import shadow_tools as source

TOOLS=Path(__file__).resolve().parent
AUTHORITY_PROJECT=TOOLS.parent.parent
_ORIGINAL_INSPECT=base.inspect_project


def digest(raw): return hashlib.sha256(raw).hexdigest()


def inspect_project(root,role):
    if role=='candidate':
        return _ORIGINAL_INSPECT(root,role)
    source.require(role=='reproduction','Unknown build source role')
    root=root.resolve(strict=True)
    tooling=repro_tools.verify(root,AUTHORITY_PROJECT)
    pins=source.read_json(root/source.PINS)
    text=(root/base.SETTINGS).read_text()
    import re
    line=re.search(r'(?m)^  additionalIl2CppArgs:([^\n]*)$',text)
    source.require(line is not None,'Missing native compiler arguments')
    expected_shadow='on' if '-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1' in line[1] else 'off'
    # Product/runtime installation is still checked against the protected pins.
    # Demo-source equivalence was independently and more strictly proved above
    # using the explicit tooling-only tree contract.
    installed=source.verify(root,demo_source=False,expected_shadow=expected_shadow)
    return {'head':source.git(root,'rev-parse','HEAD').decode().strip(),'pins':pins,
            'sourcePinSha256':digest((root/source.PINS).read_bytes()),'installed':installed,
            'handoff':tooling,'behaviorSourceCommit':tooling['behaviorSourceCommit'],
            'validationToolingCommit':tooling['validationToolingCommit']}


def main():
    # run_one() resolves this global dynamically for both the initial freeze and
    # the post-restore source check, so the split identity is enforced twice.
    base.inspect_project=inspect_project
    try:
        return base.main()
    finally:
        base.inspect_project=_ORIGINAL_INSPECT


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,KeyError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
