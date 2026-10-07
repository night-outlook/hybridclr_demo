#!/usr/bin/env python3
"""Primary-only metadata preparation; never pushes or fabricates a remote HEAD.

Publish executable changes first. Prepare a control metadata commit from that
source commit, publish it, then prepare candidate metadata using its actual SHA.
The prompt command emits a handoff only after live four-repository verification.
"""
from __future__ import annotations
import argparse
import copy
from pathlib import Path
import authority
from evidence import read, require, write

BRANCH = "codex/assembly-shadow-r01b-h1"
CONTROL_BRANCH = "codex/r02-h1-runtime-control"
WORKSPACE = "/Users/ah/GitHub/hybridclr/assembly_shadow_h1r"
CONTROL_WORKSPACE = "/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control"
NATIVE = "3981da12f2cd3ee878a04dda6f573d0ad3faeda5"
H1_NATIVE = "6be7f38bec2fa4677d24efc1a4a1294240789933"
HYBRID = "1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad"
PACKAGE = "b936a495ade1691ebb6f3bab8fdff3ef34f6f192"
DOCS = "Docs/AssemblyShadow/History/M07R/R02/"


def pins(source_commit, control=False):
    authority.commit(source_commit)
    value = {"schemaVersion": 1, "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64"}
    for key, repo, revision, local in (
        ("hybridclr", "hybridclr", HYBRID, "../hybridclr"),
        ("hybridclrUnity", "hybridclr_unity", PACKAGE, "../hybridclr_unity"),
        ("il2cppPlus", "il2cpp_plus", H1_NATIVE if control else NATIVE, "../il2cpp_plus"),
        ("demo", "hybridclr_demo", source_commit, ".")):
        value[key] = {"url": "https://github.com/night-outlook/" + repo, "revision": revision, "localPath": local}
    return value


def targets(source_commit, control_head):
    authority.commit(source_commit); authority.commit(control_head)
    result = {"kind": "R02SourceTargets", "protocol": "R02LocalBatch-v1", "schemaVersion": 1,
        "H1": "PassedWithExplicitDeferredRisk", "R02Accepted": False, "mayEnterR03": False,
        "historicalR01ReferenceCommit": "88508b59b7c4ef8c5023cbbe655d43ebfcf5304c",
        "transportPolicy": "Candidate final pushed HEAD is supplied by the verified Primary handoff; its delta from sourceCommit must be metadata-only. Control publishedHead is fixed below."}
    for role, control in (("candidate", False), ("control", True)):
        branch = CONTROL_BRANCH if control else BRANCH
        root = CONTROL_WORKSPACE if control else WORKSPACE
        selection = {"branch": branch, "sourceCommit": source_commit, "workspace": root, "repositories": {}}
        for key, name in authority.NAMES.items():
            revision = pins(source_commit, control)[key]["revision"]
            selection["repositories"][name] = {
                "repository": "night-outlook/" + name, "path": root + "/" + name,
                "branch": branch if key == "demo" else ("codex/assembly-shadow-r01b" if control and key == "il2cppPlus" else BRANCH),
                "commit": control_head if control and key == "demo" else revision}
        if control: selection["publishedHead"] = control_head
        result[role] = selection
    return result


def handoff(source_commit, control_head):
    target = targets(source_commit, control_head)
    rows = []
    for name, item in target["candidate"]["repositories"].items():
        rows.append("| " + " | ".join((item["repository"], "`" + item["path"] + "`", "`" + item["branch"] + "`", "`" + item["commit"] + "`")) + " |")
    return f'''# Primary Implementation -> Local Validation: R02 after batch F

## Authority and read order

Read `Docs/AssemblyShadow/README.md`, this handoff, `{DOCS}F_INTEGRATION_REPAIR.md`, `DESIGN.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json` in that R02 directory.

Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`. F remains 22 Passed, 8 Failed, 4 Blocked followed by failed complete sealing; its preservation inventory is not a complete seal. Preserve A/B/C/D/E/F, all H1 evidence, old R01 comparison and failed raw results.

Common executable/tool source anchor: `{source_commit}`. Use the final pushed candidate transport HEAD from Primary's prompt, not this source anchor. Post-anchor changes must be metadata-only under unchanged `shadow_tools.metadata_only`.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
{chr(10).join(rows)}

Control demo: `{CONTROL_WORKSPACE}/hybridclr_demo`, branch `{CONTROL_BRANCH}`, exact HEAD `{control_head}`. Its siblings use HybridCLR `{HYBRID}`, package `{PACKAGE}`, H1 IL2CPP `{H1_NATIVE}`. Control sibling worktrees may be detached at exact commits; their remote branches are `{BRANCH}` for HybridCLR/package and `codex/assembly-shadow-r01b` for IL2CPP. Both demo worktrees must use their specified branches. Canonical remotes: `https://github.com/night-outlook/<repository>.git`.

All eight worktrees must be clean and source-bound. The control includes the common source as ancestry and differs only in source pins. **Both roles use the new managed parser package.** Do not reuse the old control package, install R02 native runtime into control, or alter unrelated worktrees.

## Completed Primary repairs

The strict type-resolution parser admits the known 33-field R02 extension and still rejects missing/duplicate/unknown/mistyped fields. It preserves UInt64 values and unavailable coverage. `r02` is a preserved parsed view with non-serialized backing storage; the legacy eighteen public serialized fields stay unchanged. Retain raw native JSON for R02 persistence; legacy DTO serialization intentionally excludes that transient view. The real build proof checks the nested 33-field schema separately. New Editor tests cover stripped/narrowed fields and Unity serialization; the actual native-writer/managed-parser and BCL round trips are required host tests.

M07 now prepares and supplies mode-specific Control early-startup capsules before launching. Counts dispatch parameter and nested manifests to their respective existing auditors. Count and diagnostic build transactions capture linker XML and restore only the exact permitted empty-to-known-netstandard expansion; arbitrary changes still fail.

E forensics copies authenticated raw inputs before builds. Missing live E DLLs may be read only from their original Git-bound, digest-verified E archive and exact indexed members. The archive/index and copies are retained. Corrupt existing live data never falls back to an archive. Missing required inputs still prevent a complete seal. No old path is reconstructed and no failed execution is relabeled.

Fixed M00 materialization, native prerequisite ordering, Roslyn v2 kernel identities, source policies, correctness guards, runtime cache and formal timing are unchanged. No non-trivial implementation is assigned to Local.

## One new 34-cell batch

Protocol: `R02LocalBatch-v1`.

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, clang++, and at least 30 GiB free (entry minimum, not a total archive-space guarantee). Close both Unity editors. Resolve absolute tool paths. Set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

Run candidate `Tools/AssemblyShadow/R02/run_local.py` with `--candidate`, final `--candidate-head`, `--control`, `--control-head {control_head}`, absolute `--unity`/`--pwsh`, and an unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Inspect the plan without `--execute`, then add it for one execution. Do not resume or relabel F.

The 34 cells preserve the full scope: exact source/common graph; expanded host checks; E raw forensics; two fixed M00 materializations and fresh controlled ON/OFF graphs; eight functional sidecars; four pilot plus forty formal A/B pairs (88 fresh timing processes); Editor/native/generated-transaction/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity; final authority and full sealing. Require all three new `R02TypeResolutionSchemaTests` and the existing two `R02ProbeContractTests` to pass in Editor results. Inspect M07 early receipts separately from later runtime parser results.

Independent valid cells continue; failed prerequisites block consumers. No automatic semantic retry, timeout increase, hash/pin changes, verifier relaxation, source refactor or case-set reduction is allowed. A new linker output outside the fixed restoration policy returns to Primary with original/generated bytes, not a Local permission change.

## Evidence, review and return

Preserve type-resolution raw JSON and interoperability results, per-mode M07 capsule files/manifests/early receipts, both count audits, linker original/generated/restored bytes, copied E DLLs and their origin/index/archive, per-role M00 materialization, Unity completion snapshots, generated-native receipts, current build maps, all launch/raw/verifier chains, failed attempts, performance analysis and full content-addressed seal. Keep indexed generated roots outside the batch directory. `LOCAL_BATCH_RESULT.json` must bind the completed seal; `SEAL_FAILED.json` or an inventory is not equivalent.

Do not delete retained history to make disk checks pass. If E source paths are absent, the committed forensic cell handles only the exact archived bytes; Local must not improvise another source. Incomplete forensic acquisition remains a fatal full-seal failure even when independent builds complete.

Update and push `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications, first errors, source/build/input hashes and exact evidence locations. Preserve original negative cases; no summary-only replacement of raw evidence. Commission the genuinely independent R02 stage reviewer only when complete evidence is eligible, and retain its verbatim verdict.

H1 remains `PassedWithExplicitDeferredRisk`. D1=A/D2=A are development-stage deferrals, not performance/RAM acceptance. Report measured allocation/reflection/closed-generic and native/managed/RSS effects before H2; keep historical R01 and new H1-runtime-control comparisons distinct. Stop and return to Primary. R02Accepted=false; mayEnterR03=false.
'''


def markdown(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream: stream.write(content)


def prepare(role, source_commit, output, control_head=None):
    require(role in ('candidate','control'), 'Unknown publication role')
    require(output.is_absolute() and not output.exists(), 'New absolute preparation output required')
    authority.commit(source_commit)
    if role == 'candidate': authority.commit(control_head)
    output.mkdir(parents=True)
    write(output / 'ProjectSettings/AssemblyShadowSourcePins.json', pins(source_commit, role=='control'))
    if role == 'candidate':
        write(output / authority.TARGETS, targets(source_commit, control_head))
        markdown(output / 'Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md', handoff(source_commit, control_head))
    write(output / 'PREPARATION.json', {'kind':'R02MetadataPreparation', 'role':role,
        'sourceCommit':source_commit, 'controlPublishedHead':control_head,
        'published':False, 'runtimeAcceptance':False,
        'instruction':'Primary must verify source, commit/push these metadata-only files, verify final refs and passing Primary CI before issuing the prompt.'})


def prompt(project, head, control, control_head):
    value=read(project/authority.TARGETS)
    require(value['control']['publishedHead']==control_head,'Wrong frozen control HEAD')
    candidate=authority.inspect(project,head,'candidate',value)
    authority.inspect(control,control_head,'control',value)
    authority.common_sources(project,control)
    lines=['[HANDOFF: Primary Implementation -> Local Validation]', '',
        'Objective: Execute the frozen R02LocalBatch-v1 and return complete source/build/launch/raw evidence; do not begin R03.', '',
        'Read first:', '- night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md',
        '- night-outlook/hybridclr_demo/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md','',
        'Repositories and latest pushed commits:']
    for name,row in candidate['repositories'].items():
        item=value['candidate']['repositories'][name]
        lines.append(f"- night-outlook/{name} | path={row['path']} | branch={item['branch']} | commit={row['head']} | remote=verified")
    lines.extend(['',f'Control: {control} | branch={value["control"]["branch"]} | commit={control_head} | remote=verified',
        'Implementation completed: R02 production cache/observation changes, witness, strict batch, cleanup/recovery fixes, and storage attribution.',
        'Required validation: Run R02LocalBatch-v1, review full evidence independently, retain D1/D2 disposition; no R03.',
        'Expected evidence: LOCAL_BATCH_RESULT.json, full seal/launch/raw/build receipts, LOCAL_VALIDATION.md and any RETURN_TO_WEB.md.',
        'Known risks or blockers: Actual Unity/IL2CPP acceptance and performance remain to be measured; missing prerequisites or external corpus must be reported.',
        '', 'Work only from the listed paths and commits. Do not infer missing state from chat history. Report the final validation result in LOCAL_VALIDATION.md.'])
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    for role in ('candidate','control'):
        p=sub.add_parser(role);p.add_argument('--source-commit',required=True);p.add_argument('--output',required=True,type=Path)
        if role=='candidate':p.add_argument('--control-head',required=True)
    p=sub.add_parser('prompt');p.add_argument('--candidate',required=True,type=Path);p.add_argument('--candidate-head',required=True)
    p.add_argument('--control',required=True,type=Path);p.add_argument('--control-head',required=True)
    args=parser.parse_args(argv)
    if args.action=='prompt':print(prompt(args.candidate,args.candidate_head,args.control,args.control_head),end='')
    else:prepare(args.action,args.source_commit,args.output,getattr(args,'control_head',None))
    return 0

if __name__=='__main__':raise SystemExit(main())
