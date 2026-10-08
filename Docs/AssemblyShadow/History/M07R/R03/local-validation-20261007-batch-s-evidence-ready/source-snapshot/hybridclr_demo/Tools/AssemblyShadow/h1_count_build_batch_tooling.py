#!/usr/bin/env python3
"""Strict H1 build batch with split reproduction behavior/tooling identity.

Candidate behavior and tooling remain one source anchor. Reproduction behavior
stays pinned to the protected unfixed source while Unity runs from the exact
reviewed tooling-only successor authenticated by candidate source-targets.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import h1_count_build_batch as base
import h1_reproduction_tooling as repro_tools
import shadow_tools as source

TOOLS=Path(__file__).resolve().parent
AUTHORITY_PROJECT=TOOLS.parent.parent
_ORIGINAL_INSPECT=base.inspect_project
_ORIGINAL_VERIFY=base.verify_build
_FROZEN_BY_PROJECT={}


def digest(raw): return hashlib.sha256(raw).hexdigest()


def inspect_project(root,role):
    root=root.resolve(strict=True)
    if role=='candidate':
        row={**_ORIGINAL_INSPECT(root,role),'role':role}
        _FROZEN_BY_PROJECT[str(root)]=row
        return row
    source.require(role=='reproduction','Unknown build source role')
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
    row={'head':source.git(root,'rev-parse','HEAD').decode().strip(),'pins':pins,
         'sourcePinSha256':digest((root/source.PINS).read_bytes()),'installed':installed,
         'handoff':tooling,'behaviorSourceCommit':tooling['behaviorSourceCommit'],
         'validationToolingCommit':tooling['validationToolingCommit'],'role':role}
    _FROZEN_BY_PROJECT[str(root)]=row
    return row


def verify_build(project,receipt,out,expected_pin):
    project=project.resolve(strict=True);receipt=receipt.resolve(strict=True)
    result=_ORIGINAL_VERIFY(project,receipt,out,expected_pin)
    frozen=_FROZEN_BY_PROJECT.get(str(project))
    source.require(isinstance(frozen,dict),'Build tooling identity was not frozen before verification')
    handoff=frozen.get('handoff',{})
    role=frozen.get('role')
    behavior=frozen.get('behaviorSourceCommit',handoff.get('codeCommit'))
    tooling=frozen.get('validationToolingCommit',frozen.get('head'))
    source.require(role in ('candidate','reproduction') and isinstance(behavior,str) and isinstance(tooling,str),
                   'Incomplete validation tooling binding')
    receipt_sha=digest(receipt.read_bytes())
    target_sha=handoff.get('sourceTargetSha256')
    if target_sha is None:
        target_sha=handoff.get('handoffHashes',{}).get('Docs/AssemblyShadow/Handoff/source-targets.json')
    binding={'schemaVersion':1,'kind':'H1ValidationToolingBinding',
             'status':'ToolingBoundToVerifiedBuildReceiptNotRuntimeAccepted','role':role,
             'buildReceiptPath':str(receipt),'buildReceiptSha256':receipt_sha,
             'sourcePinSha256':expected_pin,'validationCheckoutCommit':frozen['head'],
             'behaviorSourceCommit':behavior,'validationToolingCommit':tooling,
             'authoritySourceTargetSha256':target_sha,
             'toolFiles':handoff.get('toolFiles',{}),
             'humanGatePassed':False,'mayEnterR02':False}
    binding_path=out/'validation-tooling-binding.json';base.save(binding_path,binding)
    result['validationToolingBindingPath']=str(binding_path)
    result['validationToolingBindingSha256']=digest(binding_path.read_bytes())
    return result


def main():
    # run_one() resolves these globals dynamically for initial freeze, build
    # verification, and the post-restore source check, so split identity is
    # enforced before and after every reproduction build.
    base.inspect_project=inspect_project;base.verify_build=verify_build
    try:
        return base.main()
    finally:
        base.inspect_project=_ORIGINAL_INSPECT;base.verify_build=_ORIGINAL_VERIFY
        _FROZEN_BY_PROJECT.clear()


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,KeyError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
