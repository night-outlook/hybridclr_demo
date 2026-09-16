#!/usr/bin/env python3
"""Authenticate a tooling-only reproduction checkout against candidate authority.

The protected reproduction behaviour/pins remain authoritative. A separate
checkout may differ from the protected published head only at the exact
validation-tool override paths committed in candidate source-targets. The
complete required validation-tool set, including already-identical files, must
also match reviewed candidate Git blobs. This is source/tooling preflight only;
it does not accept a Player or H1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import shadow_tools as s

TARGETS = 'Documents/AgentHandoff/source-targets.json'
REPOSITORY = 'night-outlook/hybridclr_demo'
ORIGINS = ('git@github.com:night-outlook/hybridclr_demo.git',
           'https://github.com/night-outlook/hybridclr_demo.git',
           'https://github.com/night-outlook/hybridclr_demo')
TOOL_PREFIXES = ('Tools/AssemblyShadow/', 'Assets/AssemblyShadowDemo/Editor/')


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value) is not None


def changed_build_inputs(base_tree, current_tree):
    paths=set(base_tree)|set(current_tree)
    return {p for p in paths if not s.metadata_only(p) and base_tree.get(p)!=current_tree.get(p)}


def _valid_tool_map(files):
    return isinstance(files,dict) and bool(files) and all(
        isinstance(p,str) and p.startswith(TOOL_PREFIXES) and _sha(oid) for p,oid in files.items())


def verify_tree_contract(base_tree, current_tree, overrides):
    s.require(_valid_tool_map(overrides), 'Reproduction tooling override allowlist is empty/invalid')
    changed=changed_build_inputs(base_tree,current_tree)
    s.require(changed==set(overrides), 'Reproduction tooling checkout has non-tooling or missing tool changes')
    for path,oid in overrides.items():
        s.require(current_tree.get(path)==oid, 'Reproduction tooling blob differs: '+path)
    return changed


def _committed_authority(authority):
    authority=Path(authority).resolve(strict=True)
    s.require(Path(s.git(authority,'rev-parse','--show-toplevel').decode().strip()).resolve()==authority,
              'Authority project must be a Git root')
    target_path=s.safe_file(authority,TARGETS)
    raw=s.git(authority,'show','HEAD:'+TARGETS)
    s.require(target_path.is_file() and raw==target_path.read_bytes(), 'Candidate source-target authority differs from committed HEAD')
    return authority,s.read_json(target_path),hashlib.sha256(raw).hexdigest()


def verify(project, authority):
    project=Path(project).resolve(strict=True)
    authority,targets,target_sha=_committed_authority(authority)
    s.require(Path(s.git(project,'rev-parse','--show-toplevel').decode().strip()).resolve()==project,
              'Reproduction tooling project must be a Git root')
    target=targets.get('demoTargets',{}).get('reproduction')
    s.require(isinstance(target,dict) and target.get('repository')==REPOSITORY, 'Missing reproduction source target')
    tooling=target.get('validationTooling')
    s.require(isinstance(tooling,dict), 'Missing explicit reproduction validationTooling target')
    protected=target.get('publishedHead',''); behavior=target.get('codeCommit','')
    revision=tooling.get('revision',''); branch=tooling.get('branch',''); candidate_anchor=tooling.get('candidateToolSourceAnchor','')
    s.require(all(_sha(v) for v in (protected,behavior,revision,candidate_anchor)), 'Invalid split reproduction source identity')
    s.require(isinstance(branch,str) and branch, 'Missing reproduction tooling branch')
    files=tooling.get('files');overrides=tooling.get('overrides')
    s.require(_valid_tool_map(files) and _valid_tool_map(overrides) and set(overrides)<=set(files),
              'Missing/invalid reproduction tooling file maps')

    origin=s.git(project,'remote','get-url','origin').decode().strip()
    s.require(origin in ORIGINS, 'Unexpected reproduction tooling origin')
    head=s.git(project,'rev-parse','HEAD').decode().strip()
    actual_branch=s.git(project,'branch','--show-current').decode().strip()
    s.require(actual_branch==branch and head==revision, 'Wrong reproduction tooling branch/revision')
    s.git(project,'merge-base','--is-ancestor',behavior,protected)
    s.git(project,'merge-base','--is-ancestor',protected,revision)

    pins=s.read_json(project/s.PINS)
    s.require(pins.get('demo',{}).get('revision')==behavior, 'Protected reproduction behavior pin changed')
    for key in ('unityVersion','target','architecture'):
        s.require(pins.get(key)==targets.get(key), 'Reproduction tooling environment differs: '+key)
    for key in ('hybridclr','hybridclrUnity','il2cppPlus'):
        expected=target['runtimePins'][key]
        s.require(all(pins.get(key,{}).get(k)==expected.get(k) for k in ('url','revision')),
                  'Protected reproduction runtime pin changed: '+key)

    pinned=s.tree(project,behavior); protected_tree=s.tree(project,protected); current=s.tree(project,revision)
    pinned_build={p:o for p,o in pinned.items() if not s.metadata_only(p)}
    protected_build={p:o for p,o in protected_tree.items() if not s.metadata_only(p)}
    s.require(pinned_build==protected_build, 'Protected reproduction published head changed build behavior after its source pin')
    verify_tree_contract(protected_tree,current,overrides)

    # Every required tool dependency must match both this checkout and the exact
    # reviewed candidate source blob, even when it needed no override.
    for path,oid in files.items():
        s.require(current.get(path)==oid, 'Reproduction required tooling blob differs: '+path)
        source_oid=s.git(authority,'rev-parse',candidate_anchor+':'+path).decode().strip()
        s.require(source_oid==oid, 'Tooling blob is not from the reviewed candidate source anchor: '+path)

    for path,oid in current.items():
        if not s.metadata_only(path): s.verify_blob(s.safe_file(project,path),oid)
    untracked=s.git(project,'ls-files','--others','--exclude-standard','-z').decode().split('\0')
    s.require(not any(p and not s.metadata_only(p) for p in untracked), 'Reproduction tooling checkout has untracked build inputs')
    for directory in ('Assets','Packages'):
        root=project/directory
        if not root.is_dir(): continue
        for suffix in ('*.cs','*.asmdef'):
            for path in root.rglob(suffix):
                s.require(path.relative_to(project).as_posix() in current, 'Unpinned Unity code input: '+str(path))

    return {'kind':'ReproductionValidationToolingPreflight','status':'BehaviorAndToolingSourcesVerifiedNotBuildAccepted',
            'repository':REPOSITORY,'branch':actual_branch,'checkoutCommit':head,'behaviorSourceCommit':behavior,
            'protectedPublishedHead':protected,'validationToolingCommit':revision,
            'candidateToolSourceAnchor':candidate_anchor,'toolFiles':files,'toolOverrides':overrides,
            'sourceTargetSha256':target_sha,'sourcePinSha256':hashlib.sha256((project/s.PINS).read_bytes()).hexdigest(),
            'nativeInstallationVerified':False,'humanGatePassed':False,'mayEnterR02':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True);p.add_argument('--authority-project',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=verify(a.project,a.authority_project)
    s.require(a.output.is_absolute() and a.output==a.output.resolve() and a.output.parent.is_dir(),
              'Output must be a new canonical file in an existing directory')
    with a.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report,indent=2));return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,RuntimeError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
