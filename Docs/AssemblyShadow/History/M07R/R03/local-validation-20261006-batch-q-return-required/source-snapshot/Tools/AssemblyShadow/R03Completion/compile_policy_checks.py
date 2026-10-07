#!/usr/bin/env python3
"""Actual guard replay over authenticated L compiler bytes, not a new Unity run.

Uses the complete real package/Editor assemblies just compiled against the pinned
Unity APIs; no test doubles for RawTypeAdmissionVerifier or BootstrapIsolationRule.
"""
import argparse
from pathlib import Path
import os
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'R03'))
from batch_contract import loads,require,sha
from batch_evidence import write
from command_lifetime import run_owned_command
from unity_command import clean_outer
from build_api import csc_arguments,CORE_SHA
from input_validation import binding
import compiler_policy_inputs as policy

HISTORICAL='Docs/AssemblyShadow/History/M07R/R03/local-validation-20261004-batch-l-return-required/batch/projects/resource-complete/_temp/AssemblyShadow/M07CompilerPreflight-6c29f2bb4942421a863f6d03a977bbfb/Snapshot'
RECEIPT_SHA='fc3c1a83ba6c22e632cbf9ee5e90dbc7c89f4d1343287d478c88a631648c06f2'

def validate(workspace,contents,api_output,newtonsoft,output):
    workspace,contents,api,root=map(lambda p:Path(p).resolve(),(workspace,contents,api_output,output))
    require(not root.exists(),'Unused compiler-policy replay output');root.mkdir(parents=True)
    demo,package=workspace/'hybridclr_demo',workspace/'hybridclr_unity'
    runtime=contents/'NetCoreRuntime/dotnet';compiler=contents/'DotNetSdkRoslyn/csc.dll';mono=contents/'MonoBleedingEdge/bin/mono'
    snapshot=demo/HISTORICAL
    result={'schemaVersion':1,'kind':'R03PinnedMonoCompilerPolicyReplay','result':'Failed','basis':'ReusedAuditedLocalLCompilerInputs',
            'historicalFinalPolicy':'Failed','historicalEvidenceModified':False,'unityEditorRun':False,'playerRun':False,
            'currentCompilerSnapshotProduced':False,'linkedProofExecuted':False,'runtimeAcceptance':False,'expansionAuthorized':False}
    try:
        require(sha(contents/'Managed/UnityEngine/UnityEditor.CoreModule.dll')==CORE_SHA,'Pinned API hash')
        require(sha(snapshot/'assembly-snapshot.json')==RECEIPT_SHA,'One exact L compiler receipt; no discovery fallback')
        receipt=loads((snapshot/'assembly-snapshot.json').read_text());rows=receipt['assemblies']+receipt['references']
        historical=[snapshot/'assembly-snapshot.json']
        for row in rows:
            for pkey,hkey in (('path','sha256'),('pdbPath','pdbSha256')):
                if row.get(pkey):
                    p=Path(row[pkey]);require(not p.is_absolute() and '..' not in p.parts,'Historical path')
                    path=policy.regular(snapshot/p);require(sha(path)==row[hkey],'Historical compiler bytes');historical.append(path)
        require(len(rows)==213,'All original 213 DLLs')
        built=loads((api/'results.json').read_text());require(built['result']=='Passed','Complete actual dependency compilation prerequisite')
        assemblies=[Path(row['output']['path']) for row in built['assemblies']]
        refs=[*sorted((contents/'MonoBleedingEdge/lib/mono/unityaot-macos').glob('*.dll')),
              *sorted((contents/'MonoBleedingEdge/lib/mono/unityaot-macos/Facades').glob('*.dll')),*assemblies,
              package/'Plugins/dnlib.dll',Path(newtonsoft).resolve()]
        source=HERE/'CompilerPolicyTests/MonoProbe.cs';target=root/'CompilerPolicyProbe.exe'
        args=csc_arguments(runtime,compiler,[],refs,[source],target)
        args=[a.replace('/target:library','/target:exe') for a in args if a!='/define:']
        rsp=root/'compiler.rsp';rsp.write_text('\n'.join('"'+a.replace('"','\\"')+'"' for a in args[4:])+'\n')
        tracked=[runtime,compiler,mono,source,*refs,*historical,demo/policy.RAW,demo/policy.DEPENDENCY]
        before=[binding(p) for p in tracked];write(root/'inputs.json',{'files':before,'historicalReceiptSha256':RECEIPT_SHA,'actualPackageAssemblies':list(map(str,assemblies))})
        clean_outer(run_owned_command([*args[:4],'@'+str(rsp)],root/'commands/0001',600),0)
        paths=[p.parent for p in assemblies]+[package/'Plugins',Path(newtonsoft).resolve().parent,
            contents/'Managed',contents/'Managed/UnityEngine',contents/'MonoBleedingEdge/lib/mono/unityaot-macos',contents/'MonoBleedingEdge/lib/mono/unityaot-macos/Facades']
        clean_outer(run_owned_command(['/usr/bin/env','MONO_PATH='+os.pathsep.join(map(str,paths)),mono,target,demo,snapshot,root/'controls'],root/'commands/0002',180),0)
        observation=loads((root/'controls/observation.json').read_text())
        result['checks']=policy.verify_observation(observation,demo,snapshot,root/'controls')
        serialization=loads((root/'serialization-control.json').read_text())
        require(serialization=={'kind':'ActualReportSerializationControl','result':'Passed','unityEditorRun':False,'runtimeAcceptance':False},'Exact report serialization control')
        result['serializationControl']=serialization
        require(before==[binding(p) for p in tracked],'Evidence/source mutation during replay')
        result['result']='Passed'
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error);raise
    finally:write(root/'results.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace','contents','api-output','newtonsoft','output'):p.add_argument('--'+flag,required=True)
    a=p.parse_args();validate(a.workspace,a.contents,a.api_output,a.newtonsoft,a.output)
