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
PACKAGE = "809a67f1f14c3626bd3c7b21721a53c1c61b1849"
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
    return f'''# Primary Implementation -> Local Validation: R02

## Objective and authority

Run `R02LocalBatch-v1` against fresh source-bound H1-runtime control and R02 candidate builds. Collect functional, concurrency, guard/regression, CPU, memory and complete raw/launch evidence in one serial batch. Do not begin R03.

Read `Docs/AssemblyShadow/README.md`, this file, `{DOCS}DESIGN.md`, `{DOCS}LOCAL_VALIDATION_TASKS.md`, and `{DOCS}source-targets.json`.

H1 remains `PassedWithExplicitDeferredRisk` following D1=A and D2=A. R02 is not accepted. The candidate demo **source anchor** is `{source_commit}`. Use the exact **final pushed transport HEAD** supplied by the Primary handoff prompt; do not substitute the source anchor as a complete handoff. The source-to-HEAD executable delta must be empty under the unchanged `shadow_tools.metadata_only` policy.

| Repository | Candidate checkout | Branch | Source commit |
| --- | --- | --- | --- |
{chr(10).join(rows)}

Control demo checkout: `{CONTROL_WORKSPACE}/hybridclr_demo`, branch `{CONTROL_BRANCH}`, exact published HEAD `{control_head}`. Its executable demo source is the same `{source_commit}`. Its three owning sibling checkouts use HybridCLR `{HYBRID}`, package `{PACKAGE}`, and IL2CPP `{H1_NATIVE}`. All three control runtime/package checkouts may be detached at their exact commits; the metadata authority checks their remote branch identities. IL2CPP control remote branch is `codex/assembly-shadow-r01b`. Never install R02 native code into the control workspace or the historical R01 reference.

Canonical remotes are `https://github.com/night-outlook/<repository>.git`. Preserve any existing unrelated worktrees; new control worktrees must use unused absolute paths and the specified owning repositories, not copies of generated outputs.

## Completed implementation

Immutable complete-physical-type admission certificates and absent-baseline counterpart caching; retained mutable-state guards; bounded observation shards and class memo; diagnostics default level 2; explicit disabled/truncated coverage; shared production-header native tests; R02 opt-in allocation/generic/array/boxing/dispatch/1000-type/worker witness; strict raw verifier; controlled paired performance; complete evidence sealing; generated-input recovery; host build/run cleanup repair; codec-owned-storage attribution.

The production native files are already committed, not patches for Local to apply. Local must not run `tools/r02/finalize_sources.py --prepare` or alter source/pins to make a verifier pass. The read-only `--verify` mode is part of Primary checks.

## Single batch

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+ with the existing project tooling, .NET SDK 8 or newer capable of net8.0 host builds, `clang++`, and PowerShell. At least 30 GiB free is an entry check, not a guarantee for every archive. Resolve actual absolute tool paths; do not assume a particular Python installation. Confirm the candidate and control owning checkouts are clean and match the final prompt/source-targets.

Run `Tools/AssemblyShadow/R02/run_local.py` with `--candidate`, the prompt's `--candidate-head`, `--control`, the fixed `--control-head`, absolute `--unity` and `--pwsh`, and an unused `--output` directly under candidate `_temp/AssemblyShadow/`. Without `--execute` it prints the plan; add `--execute` only after checking those inputs. The detailed task sheet gives the complete shell command.

Expected independent cells:

1. Four-repository/source/common-managed-graph authority and host Primary checks.
2. Two new controlled build graphs (candidate/control, ON/OFF), installed-runtime provenance and strict input checks.
3. Eight functional sidecar processes across both roles and four modes: 1/10/10000 operations, 100/1000 physical types, four workers, semantic construction checks, retained correctness diagnostics.
4. Four pilot pairs plus forty formal A/B pairs: 88 fresh processes, frozen balanced schedule, strict R00 verification, no R02 sidecar during formal timing. CPU/RSS statistics are measurements, not SLA approval.
5. Candidate Editor tests, native regressions, M07, startup11, failure/publication/recovery, fresh 132-cell count matrix, lazy/dense, and ordinary/mixed capacity.
6. Final source checks and a complete content-addressed evidence archive. `EvidenceReadyForStageReview` means evidence preparation only; `R02Accepted=false` and `mayEnterR03=false` remain.

Dependencies block on failure; independent valid cells continue. A source-state preflight before each workspace-dependent cell prevents a dirty failed build from contaminating later Players. No automatic semantic retry, source edit, lowered expectation, timeout increase, or historical result substitution is permitted.

## Evidence, failures and recovery

Keep every command JSON/stdout/stderr, partial output, failed attempt, generated-input before/after record, exact build/input binding, launch receipt, raw result, sidecar verifier, paired index, and seal index/archive. Do not retain only PASS summaries. `LOCAL_BATCH_RESULT.json` points to the seal; preserve both. The controlled graphs and count/diagnostic roots outside the batch folder are indexed and retained by the runner.

The retained ordinary capacity corpus is used as authenticated input bytes only, never reused execution. It is found through the fixed historical Git index and exact launch/workload bindings; no basename fallback. Missing external bytes block that capacity path. Preserve the historical seven count archives, source-27df performance bytes, and all H1 evidence.

Record the first actual build/semantic error and every recovery error independently. Do not convert a failed cleanup to Passed because host assertions or Player exit code were zero. If unexpected source mutations remain, preserve them and return the failure; do not reset or clean them automatically.

## D1/D2 and review

Report R02-versus-current-H1-runtime cold/warm allocation, reflection and closed generic results, distributions and sample counts. Retain the older R01 comparison separately; no codec-only causal claim. Report native owned structure bytes, managed bytes, point-in-time RSS and lifetime peak with their different meanings. `codec_memory.py` measures host constructor allocation requests for the unchanged profile-2 storage; it neither measures Unity RSS nor explains the whole historical RSS delta by itself.

After all required evidence succeeds, commission a genuinely independent R02 stage review with the existing reviewer definition and fixed source/evidence inputs. Preserve its verbatim verdict. This is not the later H2 Human Review Gate. Return D1/D2 disposition and remaining risks to Primary before any subsequent stage; no risk is silently waived.

## Local modification boundary and return

Permitted: unused output suffixes, absolute tool resolution, registered worktree setup at the listed commits, normal builds/fixture generation, exact scripted generated-input restoration, command/evidence collection, and bounded environment fixes with receipts.

Forbidden: production or verifier refactors, changing source pins or fixtures after freezing, changing the required case set, hiding failing attempts, relaxing provenance or cleanup, installing candidate runtime into control, cleanup of retained evidence, and beginning R03.

Update `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications. Put non-trivial issues in `RETURN_TO_WEB.md` with reproduction command, source/build tuple, first failing path/hash and retained evidence. Commit and push Local's reports and evidence indexes without replacing historical records. No non-trivial implementation is assigned to Local.
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
