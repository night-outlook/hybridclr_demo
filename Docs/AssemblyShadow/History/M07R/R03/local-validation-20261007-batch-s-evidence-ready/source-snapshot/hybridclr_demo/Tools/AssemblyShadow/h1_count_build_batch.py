#!/usr/bin/env python3
"""Serial fresh count builds with provenance verification and bounded recovery.

Default is a printed plan, not execution. No branch switch, source-pin rewrite,
cache cleanup, force operation, historical receipt rewrite, or gate approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

import h1_local_batch as batch
import shadow_tools as source
import h1_handoff_preflight as handoff

SCENE = 'Assets/AssemblyShadowR01BDiagnostics/Scenes/H1CountDiagnostic.unity'
SETTINGS = 'ProjectSettings/ProjectSettings.asset'
RESTORABLE = (SCENE, SCENE + '.meta', SETTINGS)
SCENE_FIELDS = ('expectedBaselineBuildId', 'expectedRuntimeAbiHash', 'expectedFeatureEnabled', 'expectedCppConfiguration')
TOOLS = Path(__file__).resolve().parent


def digest(raw): return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def restore_allowed(relative, before, after):
    if before == after: return True
    if relative == SETTINGS:
        old = b'  scriptingDefineSymbols: {}\n'
        new = b'  scriptingDefineSymbols:\n    Standalone: \n'
        return before.count(old) == 1 and before.replace(old, new, 1) == after
    if relative == SCENE:
        def stripped(raw):
            for key in SCENE_FIELDS:
                pattern = rb'(?m)^  ' + key.encode() + rb': ([^\r\n]*)$'
                values = re.findall(pattern, raw)
                source.require(len(values) == 1, 'Ambiguous diagnostic scene field: ' + key)
                if key == 'expectedRuntimeAbiHash': source.require(re.fullmatch(rb'[0-9a-f]{64}', values[0]), 'Invalid scene ABI hash')
                elif key == 'expectedBaselineBuildId': source.require(re.fullmatch(rb'H1Count-(On|Off)-(Debug|Release)',values[0]), 'Invalid scene build ID')
                elif key == 'expectedFeatureEnabled': source.require(values[0] in (b'0',b'1'), 'Invalid scene feature')
                else: source.require(values[0] in (b'Debug',b'Release'), 'Invalid scene configuration')
                raw = re.sub(pattern, b'  ' + key.encode() + b': <recorded-mode>', raw)
            return raw
        return stripped(before) == stripped(after)
    return False


def modes(scope):
    if scope == 'smoke': return [('candidate','on','Debug')]
    return [('candidate','on','Debug'),('candidate','on','Release'),('candidate','off','Debug'),
            ('candidate','off','Release'),('reproduction','on','Debug'),('reproduction','on','Release')]


def inspect_project(root, role):
    source.require(role in ('candidate', 'reproduction'), 'Unknown build source role')
    source.require(root.is_absolute() and root == root.resolve(strict=True), 'Project must be canonical')
    # A reviewed tooling successor can preserve the original reproduction branch.
    # The committed handoff owns the exact branch/anchor; no CLI override or
    # unchecked alternative branch is admitted by the batch runner.
    handoff_state = handoff.verify(root, role)
    remote=source.git(root,'remote','get-url','origin').decode().strip()
    source.require(remote in ('git@github.com:night-outlook/hybridclr_demo.git','https://github.com/night-outlook/hybridclr_demo.git','https://github.com/night-outlook/hybridclr_demo'), 'Unexpected demo origin')
    pins=source.read_json(root/source.PINS)
    # Do not let stale archived install receipts pass by opting out of source checking.
    text=(root/SETTINGS).read_text()
    line=re.search(r'(?m)^  additionalIl2CppArgs:([^\n]*)$',text)
    source.require(line is not None,'Missing native compiler arguments')
    expected_shadow='on' if '-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1' in line[1] else 'off'
    report=source.verify(root,demo_source=True,expected_shadow=expected_shadow)
    return {'head':source.git(root,'rev-parse','HEAD').decode().strip(),'pins':pins,
            'sourcePinSha256':digest((root/source.PINS).read_bytes()),'installed':report,'handoff':handoff_state}


def command(argv, project, log, timeout):
    result=batch.run_command(argv,str(project),dict(os.environ),log,timeout)
    save(log.with_suffix(log.suffix+'.execution.json'),result)
    source.require(result.get('exitCode')==0 and not result.get('timedOut'),'Command failed; preserve '+str(log))
    return result


def stopped(project, pwsh, log):
    return command([pwsh,'-NoProfile','-File',str(TOOLS/'Check-H1EditorStopped.ps1'),'-ProjectPath',str(project)],project,log,60)


def verify_build(project, receipt, out, expected_pin):
    build=source.read_json(receipt)
    source.require(build.get('sourcePinSha256')==expected_pin,'Build does not use this frozen source chain')
    command([sys.executable,str(TOOLS/'verify-h1-compiler-provenance-strict.py'),'--scope','single','--build',str(receipt),'--output',str(out/'native-verification.json')],project,out/'verify-native.log',1800)
    capture=receipt.parent/'ManagedSourceProvenance/h1-managed-source-capture.json'
    command([sys.executable,str(TOOLS/'h1_managed_provenance.py'),'verify','--capture',str(capture),'--output',str(out/'managed-verification.json')],project,out/'verify-managed.log',1800)
    return {'receiptPath':str(receipt),'receiptSha256':digest(receipt.read_bytes()),'buildGuid':build['buildGuid'],
            'nativeVerification':str(out/'native-verification.json'),'managedVerification':str(out/'managed-verification.json')}


def run_one(project, unity, pwsh, feature, cpp, frozen, out):
    preparation=project/'_temp/AssemblyShadow'/('H1CountBuild-'+uuid.uuid4().hex)
    preparation.mkdir(parents=True,exist_ok=False)
    out.mkdir(parents=True,exist_ok=False)
    source.require(shutil.disk_usage(project).free >= 10 * 1024**3, 'At least 10 GiB free is required before each build; never clean historical evidence automatically')
    before={relative:source.safe_file(project,relative).read_bytes() for relative in RESTORABLE}
    save(out/'before.json',{p:digest(data) for p,data in before.items()})
    common=[unity,'-batchmode','-nographics','-quit','-projectPath',str(project),'-buildTarget','StandaloneOSX',
            '-shadowH1Python',sys.executable,'-shadowH1PreparationRoot',str(preparation)]
    receipt=preparation/'build-receipt.json'
    started=False
    error=None
    try:
        stopped(project,pwsh,out/'ownership-prepare.log')
        started=True
        command(common+['-executeMethod','AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.PrepareDiagnosticBuild','-logFile',str(out/'prepare-unity.log')],project,out/'prepare.log',900)
        stopped(project,pwsh,out/'ownership-build.log')
        command(common+['-executeMethod','AssemblyShadowDemo.Editor.H1CountDiagnosticBuildWithManagedProvenance.BuildDiagnosticPlayer',
                '-shadowH1Feature',feature,'-shadowH1Cpp',cpp,'-shadowH1BuildReceipt',str(receipt),
                '-shadowH1PlayerOutput',str(preparation/'Player.app'),'-logFile',str(out/'build-unity.log')],project,out/'build.log',14400)
        result=verify_build(project,receipt,out,frozen['sourcePinSha256'])
    except Exception as failure:
        error=failure
    finally:
        if started:
            try:
                stopped(project,pwsh,out/'ownership-restore.log')
                command(common+['-executeMethod','AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.RestoreDiagnosticBuild','-logFile',str(out/'restore-unity.log')],project,out/'restore.log',900)
                stopped(project,pwsh,out/'ownership-recovery.log')
                after={relative:source.safe_file(project,relative).read_bytes() for relative in RESTORABLE}
                # Persist every changed byte before any eligible restoration.
                rows=[]
                for relative in RESTORABLE:
                    if before[relative]==after[relative]:continue
                    key=hashlib.sha256(relative.encode()).hexdigest()[:16]
                    for suffix,data in [('before',before[relative]),('after',after[relative])]:
                        path=out/(key+'.'+suffix+'.bin')
                        with path.open('xb') as stream:stream.write(data)
                    rows.append({'path':relative,'beforeSha256':digest(before[relative]),'afterSha256':digest(after[relative]),
                                 'allowed':restore_allowed(relative,before[relative],after[relative])})
                save(out/'restoration-check.json',{'changes':rows})
                source.require(all(r['allowed'] for r in rows),'Unrecognized generated change; preserved without overwriting it')
                for row in rows:
                    target=source.safe_file(project,row['path'])
                    source.require(target.read_bytes()==after[row['path']],'Concurrent change during recovery')
                    target.write_bytes(before[row['path']])
                # Pins, runtime, and all non-document source must still match.
                restored=inspect_project(project,'candidate' if frozen['role']=='candidate' else 'reproduction')
                source.require(restored['head']==frozen['head'] and restored['sourcePinSha256']==frozen['sourcePinSha256'],'Source freeze changed during build')
                save(out/'restored.json',{'status':'ExactRestorationVerified','sourcePinSha256':frozen['sourcePinSha256']})
            except Exception as recovery:
                save(out/'recovery-failure.json',{'error':str(recovery),'originalError':str(error) if error else None})
                raise
    if error is not None:
        save(out/'failed.json',{'error':str(error),'preparation':str(preparation),'candidateAcceptance':False})
        raise error
    save(out/'result.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True,type=Path);p.add_argument('--reproduction',type=Path)
    p.add_argument('--unity',required=True);p.add_argument('--pwsh',required=True)
    p.add_argument('--scope',choices=('smoke','all'),default='smoke')
    p.add_argument('--reuse-smoke',type=Path,help='Explicit already verified receipt from this exact source chain; never auto-selected')
    p.add_argument('--output',required=True,type=Path);p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    source.require(not args.reuse_smoke or args.scope == 'all', 'Reuse requires --scope all')
    roots={'candidate':args.candidate.resolve(strict=True)}
    if args.scope=='all':
        source.require(args.reproduction is not None,'All mode needs a separate reproduction checkout')
        roots['reproduction']=args.reproduction.resolve(strict=True)
        source.require(roots['candidate']!=roots['reproduction'],'Separate candidate/reproduction checkouts required')
    plan={'scope':args.scope,'modes':modes(args.scope),'projects':{k:str(v) for k,v in roots.items()},'humanGatePassed':False,'mayEnterR02':False}
    if not args.execute: print(json.dumps(plan,indent=2));return 0
    source.require(sys.platform=='darwin','Acceptance builds require macOS; this host must not produce fake build receipts')
    source.require(Path(args.unity).is_absolute() and Path(args.unity).is_file(),'Explicit Unity executable required')
    source.require(Path(args.pwsh).is_absolute() and Path(args.pwsh).is_file(),'Explicit PowerShell executable required')
    source.require(args.output.is_absolute() and args.output == args.output.resolve(), 'Output must be an explicit canonical absolute path')
    out=args.output;out.mkdir(parents=True,exist_ok=False)
    frozen={role:{**inspect_project(root,role),'role':role} for role,root in roots.items()}
    save(out/'source-preflight.json',frozen);save(out/'plan.json',plan)
    results=[]
    # A verified candidate On/Debug receipt is the dependency for the other five.
    for role,feature,cpp in modes(args.scope):
        target=out/(role+'-'+feature+'-'+cpp)
        if not results and args.reuse_smoke:
            source.require(args.scope=='all','Reuse is only for continuing after a successful smoke')
            target.mkdir();result=verify_build(roots[role],args.reuse_smoke.resolve(strict=True),target,frozen[role]['sourcePinSha256'])
            build=source.read_json(args.reuse_smoke)
            source.require(build.get('featureEnabled') is True and build.get('cppConfiguration')=='Debug','Reuse must be candidate On/Debug')
            result['reuse']='ExplicitExactSmokeReceiptReverified'
        else:
            result=run_one(roots[role],args.unity,args.pwsh,feature,cpp,frozen[role],target)
        results.append({'role':role,'feature':feature,'cpp':cpp,**result})
    if args.scope=='all':
        for role in roots:
            argv=[sys.executable,str(TOOLS/'verify-h1-compiler-provenance-strict.py'),'--scope',role,'--output',str(out/(role+'-compiler-verification.json'))]
            for r in results:
                if r['role']==role:argv+=['--build',r['receiptPath']]
            command(argv,roots[role],out/(role+'-compiler-verification.log'),1800)
    save(out/'batch-result.json',{'status':'BuildsAndProvenanceVerifiedNotRuntimeAccepted','results':results,'humanGatePassed':False,'mayEnterR02':False})
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,KeyError) as error:
        print('Blocked: '+str(error),file=sys.stderr);raise SystemExit(1)
