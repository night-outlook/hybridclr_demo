#!/usr/bin/env python3
"""Execute actual image guards/semantic encoder under the pinned Unity Mono.

No Editor or Player launch, no reconstruction of the frozen DLL, no rebaseline.
"""
import argparse
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import run_owned_command
from unity_command import clean_outer
from build_api import csc_arguments, CORE_SHA
from input_validation import binding
import fixed_image_inputs as fixed


def validate(workspace,contents,output):
    workspace,contents,root=map(lambda p:Path(p).resolve(),(workspace,contents,output))
    require(not root.exists(),'Unused fixed-image compiler output')
    root.mkdir(parents=True)
    demo,package=workspace/'hybridclr_demo',workspace/'hybridclr_unity'
    runtime=contents/'NetCoreRuntime/dotnet';compiler=contents/'DotNetSdkRoslyn/csc.dll'
    mono=contents/'MonoBleedingEdge/bin/mono'
    result={'schemaVersion':1,'kind':'R03PinnedMonoFixedImage','result':'Failed','unityVersion':'2022.3.62f2',
            'unityEditorRun':False,'playerRun':False,'freshImageCompilation':False,'runtimeAcceptance':False}
    try:
        require(sha(contents/'Managed/UnityEngine/UnityEditor.CoreModule.dll')==CORE_SHA,'Pinned SDK content')
        require(mono.is_file(),'Exact Unity Mono executable required')
        refs=[*sorted((contents/'MonoBleedingEdge/lib/mono/unityaot-macos').glob('*.dll')),
              *sorted((contents/'MonoBleedingEdge/lib/mono/unityaot-macos/Facades').glob('*.dll')),package/'Plugins/dnlib.dll']
        sources=[HERE/'FixedImageTests/MonoProbe.cs',HERE/'FixedImageTests/SemanticDiagnostics.cs',
                 HERE/'FixedImageTests/EnvironmentBoundaries.cs',demo/'Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs',
                 package/'Editor/AssemblyShadow/Model/ShadowConfiguration.cs',package/'Editor/AssemblyShadow/Metadata/AssemblyIdentityUtil.cs',
                 *sorted((package/'Editor/AssemblyShadow/Hashing').glob('*.cs')),
                 *[package/('Editor/AssemblyShadow.CodeGen/'+n+'.cs') for n in
                   ('ReflectionBindingConfiguration','RawTypeAdmissionConfiguration','RawTypeAdmissionJson')]]
        project=root/'project'
        for name in (*fixed.FILES,fixed.CONFIG):
            target=project/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(demo/name,target)
        write(project/fixed.ordinary.PINS,{'kind':'PinnedMonoHostInput','runtimeAcceptance':False})
        fixed.provision(project)
        target=root/'FixedImageProbe.exe'
        args=csc_arguments(runtime,compiler,[],refs,sources,target)
        args=[a.replace('/target:library','/target:exe') for a in args if a!='/define:']
        rsp=root/'compiler.rsp';rsp.write_text('\n'.join('"'+a.replace('"','\\"')+'"' for a in args[4:])+'\n')
        tracked=[runtime,compiler,mono,*refs,*sources]
        inputs=[binding(p) for p in tracked];write(root/'inputs.json',{'files':inputs,'frozen':fixed.source_contract(project)})
        clean_outer(run_owned_command([*args[:4],'@'+str(rsp)],root/'commands/0001',600),0)
        shutil.copyfile(package/'Plugins/dnlib.dll',root/'dnlib.dll')
        clean_outer(run_owned_command([mono,target,project,root/'probe'],root/'commands/0002',120),0)
        value=loads((root/'probe/observation.json').read_text())
        result['observation']=fixed.verify_observation(value,root/'probe/controls',pinned_semantics=True)
        result['imageSemanticHash']=value['imageSemanticHash']
        require(inputs==[binding(p) for p in tracked],'Pinned compiler/runtime/source changed')
        fixed.verify_materialization(project)
        result['result']='Passed'
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error);raise
    finally: write(root/'results.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('workspace','contents','output'):p.add_argument('--'+flag,required=True)
    a=p.parse_args();validate(a.workspace,a.contents,a.output)
