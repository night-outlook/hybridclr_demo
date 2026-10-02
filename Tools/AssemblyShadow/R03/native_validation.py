#!/usr/bin/env python3
"""Production-header regression and optional pinned SDK translation-unit compile.

No Unity Editor launch, native Player execution, source rewrite, or acceptance.
The SDK copy is temporary; all changed sources and inputs remain hash-bound.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import run_owned_command


class Commands:
    def __init__(self, output):
        self.root=output; self.index=0; self.rows=[]
    def run(self, args, timeout=180):
        self.index+=1; folder=self.root/'commands'/('%04d'%self.index)
        receipt=run_owned_command(args, folder, timeout)
        self.rows.append({'command':str(folder/'command.json'),'sha256':sha(folder/'command.json')})
        return folder, receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--unity',type=Path)
    parser.add_argument('--sanitizers',action='store_true')
    args=parser.parse_args(); ws=args.workspace.resolve(); output=args.output.resolve()
    require(not output.exists(),'Unused native check root required');output.mkdir(parents=True)
    native=ws/'il2cpp_plus'; hybrid=ws/'hybridclr';demo=ws/'hybridclr_demo'
    pins=loads((demo/'Tools/AssemblyShadow/R03/source-pins.json').read_text())
    for name in ('il2cpp_plus','hybridclr','hybridclr_unity'):
        path=ws/name
        if (path/'.git').exists():
            require(subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()==pins[name],'Exact source pin: '+name)
    c=Commands(output); result={'kind':'R03NativeRuntimePrerequisites','result':'Failed','platform':platform.platform(),
                               'unitCases':[],'translationUnits':[], 'runtimeAcceptance':False,'unityEditorRun':False}
    files=[p for root in (native/'libil2cpp/vm',native/'tools/r03',hybrid/'hybridclr/metadata') for p in root.glob('*')
           if p.is_file() and (p.name.startswith('AssemblyShadow') or p.name in ('InterpreterImage.h','StagedAssembly.cpp','runtime_probe_tests.cpp','runtime_probe_other.cpp'))]
    sources=[{'path':str(p.relative_to(ws)),'sha256':sha(p)} for p in sorted(files)]
    try:
        cc=shutil.which('clang++');require(cc,'clang++ is required')
        c.run([cc,'--version'])
        if not args.unity:
            configs=[(std,probe,level,[]) for std in ('c++11','c++17') for probe,level in ((0,0),(0,1),(0,2),(1,2))]
            if args.sanitizers:configs.append(('c++17',1,2,['-fsanitize=address,undefined','-fno-omit-frame-pointer']))
            for n,(std,probe,level,extra) in enumerate(configs):
                exe=output/('unit-%02d'%n)
                c.run([cc,'-std='+std,'-pthread','-O1','-g','-Wall','-Wextra','-Werror',
                       '-DHYBRIDCLR_R03_RUNTIME_PROBE='+str(probe),'-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL='+str(level),
                       '-I'+str(native/'libil2cpp'),str(native/'tools/r03/runtime_probe_tests.cpp'),str(native/'tools/r03/runtime_probe_other.cpp'),
                       *extra,'-o',str(exe)])
                for mode in (('disabled',) if not probe else ('window','loop-cold','thread','overflow','wrong-owner','unsealed')):
                    folder,_=c.run([str(exe),mode]);raw=loads((folder/'stdout.log').read_text())
                    require(raw['result']=='Passed' and raw['runtimeAcceptance'] is False,'Production probe header test')
                    result['unitCases'].append({'configuration':n,'mode':mode,'result':raw})
            # Original production cache/proof/negative-path/counter suites, unchanged.
            for script in ('run_tests.py','run_revision_tests.py'):
                target=output/script.replace('.py','')
                c.run([sys.executable,'-B',str(native/'tools/r02'/script),'--output',str(target)],timeout=300)
                original=loads((target/'results.json').read_text());require(original['result']=='Passed','Existing R02 native regression')
        else:
            require(sys.platform=='darwin','Official macOS/ARM64 compiler profile required')
            contents=args.unity.resolve().parent.parent
            sdk=contents/'il2cpp';require((sdk/'libil2cpp/il2cpp-config.h').is_file(),'Exact SDK extraction required')
            # Copy outside the evidence output, never publish vendor SDK files.
            copy=contents.parent.parent/'R03NativeCompileSDK';require(not copy.exists(),'Unused SDK copy required')
            require(output not in copy.parents and copy not in output.parents,'SDK copy must be outside evidence output')
            shutil.copytree(sdk/'libil2cpp',copy)
            shutil.copytree(native/'libil2cpp',copy,dirs_exist_ok=True)
            shutil.copytree(hybrid/'hybridclr',copy/'hybridclr',dirs_exist_ok=True)
            version='#pragma once\n#define HYBRIDCLR_UNITY_VERSION 20220362\n#define HYBRIDCLR_UNITY_2022 1\n'+''.join('#define HYBRIDCLR_UNITY_%d_OR_NEW 1\n'%y for y in range(2019,2023))
            (copy/'hybridclr/generated/UnityVersion.h').write_text(version)
            write(output/'generated-profile.json',{'versionHeader':version,'derivation':'Pinned package Il2CppDefGenerator.GenerateIl2CppConfig for 2022.3.62f2','runtimeAcceptance':False})
            includes=[copy,sdk,sdk/'external',sdk/'external/baselib/Include',sdk/'external/baselib/Platforms/OSX/Include',sdk/'external/bdwgc/include']
            overlay=demo/'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'
            units=[copy/'vm/AssemblyShadowTypeResolver.cpp',copy/'hybridclr/metadata/StagedAssembly.cpp',copy/'hybridclr/metadata/InterpreterImage.cpp',overlay]
            profiles=[('candidate',1,1,0),('debug',1,1,1),('probe-off',1,0,0),('feature-off',0,0,0)]
            for label,feature,probe,debug in profiles:
                for source in units:
                    cmd=[cc,'-std=c++17','-fsyntax-only','-arch','arm64','-DIL2CPP_DEBUG='+str(debug),
                         '-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+str(feature),'-DHYBRIDCLR_R03_RUNTIME_PROBE='+str(probe),
                         '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=2',*[('-I'+str(p)) for p in includes if p.is_dir()],str(source)]
                    folder,_=c.run(cmd)
                    result['translationUnits'].append({'profile':label,'source':str(source),'sha256':sha(source),'commandReceipt':sha(folder/'command.json')})
            sdk_inputs=[{'path':str(p.relative_to(copy)),'sha256':sha(p)} for p in sorted(copy.rglob('*')) if p.is_file()]
            write(output/'native-sdk-inputs.json',{'files':sdk_inputs,'vendorFilesUploaded':False})
        require(sources==[{'path':str(p.relative_to(ws)),'sha256':sha(p)} for p in sorted(files)],'Native source bytes changed')
        result['result']='Passed'
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error)
        raise
    finally:
        result['sources']=sources;result['commands']=c.rows
        write(output/'results.json',result)
    print(json.dumps({'result':result['result'],'unitCases':len(result['unitCases']),'translationUnits':len(result['translationUnits']),'runtimeAcceptance':False}))

if __name__=='__main__':main()
