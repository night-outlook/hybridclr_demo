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
import re
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



def checked_sdk_scratch(raw, workspace, output, unity_contents):
    """Validate an UNUSED external SDK copy root without modifying any path."""
    require(raw is not None, 'Explicit external --sdk-scratch required with --unity')
    require(raw.is_absolute() and raw == raw.resolve(strict=False),
            'Canonical absolute nonsymlink SDK scratch path required')
    scratch = raw.resolve(strict=False)
    require(scratch.parent.is_dir() and not scratch.exists(),
            'Fresh absent SDK scratch with existing parent required')
    for protected in (workspace, output, unity_contents.parent.parent):
        require(scratch != protected and scratch not in protected.parents and
                protected not in scratch.parents,
                'SDK scratch must be outside source, evidence and Unity Editor roots')
    return scratch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--unity',type=Path)
    parser.add_argument('--sdk-scratch',type=Path,help='Required fresh, nonaliasing external SDK-copy root for --unity')
    parser.add_argument('--sanitizers',action='store_true')
    parser.add_argument('--candidate-native-sha',help='Explicit P1 SDK syntax-only candidate pin; leaves historical source-pins.json unchanged')
    args=parser.parse_args(); ws=args.workspace.resolve(); output=args.output.resolve()
    require(not output.exists(),'Unused native check root required');output.mkdir(parents=True)
    native=ws/'il2cpp_plus'; hybrid=ws/'hybridclr';demo=ws/'hybridclr_demo'
    pins=loads((demo/'Tools/AssemblyShadow/R03/source-pins.json').read_text())
    candidate=args.candidate_native_sha
    if candidate is not None:
        require(bool(args.unity) and bool(re.fullmatch(r'[0-9a-f]{40}',candidate)),
                'Explicit 40-hex candidate pin requires official --unity syntax-only mode')
    for name in ('il2cpp_plus','hybridclr','hybridclr_unity'):
        path=ws/name
        if (path/'.git').exists():
            expected=candidate if name=='il2cpp_plus' and candidate else pins[name]
            require(subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()==expected,'Exact source pin: '+name)
    c=Commands(output); result={'kind':'R03NativeRuntimePrerequisites','result':'Failed','platform':platform.platform(),
                               'unitCases':[],'translationUnits':[], 'runtimeAcceptance':False,'unityEditorRun':False,
                               'candidateNativeSha':candidate,'historicalPinsOverriddenOnDisk':False}
    files=[p for root in (native/'libil2cpp/vm',native/'libil2cpp/gc',native/'tools/r03',hybrid/'hybridclr/metadata') for p in root.glob('*')
           if p.is_file() and (p.name.startswith('AssemblyShadow') or p.name in ('InterpreterImage.h','StagedAssembly.cpp','runtime_probe_tests.cpp','runtime_probe_other.cpp','producer_fence_tests.cpp','probe_identity_tests.cpp','GarbageCollector.cpp','Runtime.cpp','Object.cpp'))]
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
            fence_configs = [('c++11', '-O0', []), ('c++17', '-O1', [])]
            if args.sanitizers: fence_configs.append(('c++17', '-O1', ['-fsanitize=address,undefined','-fno-omit-frame-pointer']))
            for n, (std, optimization, extra) in enumerate(fence_configs):
                exe=output/('fence-%02d'%n)
                c.run([cc,'-std='+std,'-pthread',optimization,'-g','-Wall','-Wextra','-Werror',
                       '-DHYBRIDCLR_R03_RUNTIME_PROBE=1','-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=2',
                       '-I'+str(native/'libil2cpp'),str(native/'tools/r03/producer_fence_tests.cpp'),*extra,'-o',str(exe)])
                for mode in ('normal','defer','unrelated','existing','expire','abandoned','wrong-owner','reuse','bounds','exception','context'):
                    folder,_=c.run([str(exe),mode]); raw=loads((folder/'stdout.log').read_text())
                    require(raw['result']=='Passed' and raw['runtimeAcceptance'] is False,'Bounded producer gate contract')
                    result['unitCases'].append({'configuration':'fence-'+str(n),'mode':mode,'result':raw})
            # Same production snapshot serializer, with unavailable/overlong
            # identities and non-dereferenceable physical pointers after capture.
            for n, (std, optimization, extra) in enumerate(fence_configs):
                exe=output/('identity-%02d'%n)
                c.run([cc,'-std='+std,'-pthread',optimization,'-g','-Wall','-Wextra','-Werror',
                       '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=2',
                       '-I'+str(native/'libil2cpp'),str(native/'tools/r03/probe_identity_tests.cpp'),*extra,'-o',str(exe)])
                for mode in ('owned','copy','generic','missing','limits','text-bounds','escape','format-state','repeat','recapture-failure','stream-failure'):
                    folder,_=c.run([str(exe),mode]); raw=loads((folder/'stdout.log').read_text())
                    require(raw['result']=='Passed' and raw['runtimeAcceptance'] is False,'Owned identity observation contract')
                    result['unitCases'].append({'configuration':'identity-'+str(n),'mode':mode,'result':raw})
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
            # Never copy SDK bytes into the installed Unity Editor, source trees,
            # evidence output or an already used historical root.
            scratch=checked_sdk_scratch(args.sdk_scratch, ws, output, contents)
            copy=scratch/'libil2cpp'
            shutil.copytree(sdk/'libil2cpp',copy)
            # Preserve SDK-relative ../../external includes from libil2cpp/utils.
            shutil.copytree(sdk/'external',scratch/'external')
            shutil.copytree(native/'libil2cpp',copy,dirs_exist_ok=True)
            shutil.copytree(hybrid/'hybridclr',copy/'hybridclr',dirs_exist_ok=True)
            version='#pragma once\n#define HYBRIDCLR_UNITY_VERSION 20220362\n#define HYBRIDCLR_UNITY_2022 1\n'+''.join('#define HYBRIDCLR_UNITY_%d_OR_NEW 1\n'%y for y in range(2019,2023))
            (copy/'hybridclr/generated/UnityVersion.h').write_text(version)
            write(output/'generated-profile.json',{'versionHeader':version,'baselibInlineNamespace':'il2cpp_baselib','derivation':'Pinned package Il2CppDefGenerator.GenerateIl2CppConfig for 2022.3.62f2','runtimeAcceptance':False})
            includes=[copy,scratch,scratch/'external',scratch/'external/baselib/Include',
                      scratch/'external/baselib/Platforms/OSX/Include',scratch/'external/bdwgc/include']
            overlay=demo/'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'
            units=[copy/'vm/Runtime.cpp',copy/'vm/Object.cpp',copy/'vm/AssemblyShadow.cpp',copy/'vm/AssemblyShadowRuntimeProbe.cpp',copy/'vm/AssemblyShadowEngineReportingProbe.cpp',copy/'gc/GarbageCollector.cpp',copy/'vm/AssemblyShadowTypeResolver.cpp',copy/'vm/AssemblyShadowTypeKey.cpp',
                   copy/'hybridclr/metadata/StagedAssembly.cpp',copy/'hybridclr/metadata/InterpreterImage.cpp',overlay]
            # Explicitly cover the shared general serializer; historical matrix was 11 x 5.
            units.append(copy/'vm/AssemblyShadowDiagnostics.cpp')
            if candidate:
                # P1 candidate mode compiles actual physical/class readers too.
                # The historical official SDK matrix remains exactly 12 x 5.
                units.extend((copy/'vm/Assembly.cpp',copy/'vm/AssemblyShadowVisibility.cpp'))
            profiles=[('candidate',1,1,0,2),('debug',1,1,1,2),('probe-off',1,0,0,2),
                      ('diagnostics-off',1,0,0,0),('feature-off',0,1,0,0)]
            expected_units=14 if candidate else 12
            require(len(units)==expected_units and len(set(units))==expected_units and len(profiles)==5,
                    'Complete current candidate/historical syntax matrix required')
            result['plannedTranslationUnitCount']=expected_units*len(profiles)
            for label,feature,probe,debug,diagnostics in profiles:
                for source in units:
                    cmd=[cc,'-std=c++17','-fsyntax-only','-arch','arm64','-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib',
                         '-DIL2CPP_DEBUG='+str(debug),
                         '-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+str(feature),'-DHYBRIDCLR_R03_RUNTIME_PROBE='+str(probe),
                         '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL='+str(diagnostics),*[('-I'+str(p)) for p in includes if p.is_dir()],str(source)]
                    folder,_=c.run(cmd)
                    result['translationUnits'].append({'profile':label,'source':str(source),'sha256':sha(source),'commandReceipt':sha(folder/'command.json')})
            require(len(result['translationUnits'])==expected_units*len(profiles),
                    'All current native syntax configurations required')
            sdk_inputs=[{'path':str(p.relative_to(scratch)),'sha256':sha(p)} for p in sorted(scratch.rglob('*')) if p.is_file()]
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
