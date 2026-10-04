import hashlib,json,os,shutil,sys
from pathlib import Path
workspace=Path(os.environ['GITHUB_WORKSPACE']);demo=workspace/'hybridclr_demo';package=workspace/'hybridclr_unity'
sys.path.insert(0,str(demo/'Tools/AssemblyShadow/R03'))
from command_lifetime import run_owned_command
from unity_command import clean_outer
base=Path(os.environ['RUNNER_TEMP']);contents=next((base/'expanded').rglob('Unity.app/Contents'))
out=base/'lk-tools';out.mkdir();generators=sorted(contents.rglob('*SourceGenerator*.dll'))
selected=set((contents/'NetStandard').rglob('*'))
for g in generators:selected.update(g.parent.rglob('*'))
for p in sorted(selected):
    if not p.is_file():continue
    rel=p.relative_to(contents);dst=out/'Contents'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
report={'kind':'PinnedUnityFixedImageInvestigation','workflowSource':os.environ['GITHUB_SHA'],'unity':'2022.3.62f2','sdkArchiveSha256':'5d2575c1b10a2a9f1f89bf40631a6b9bec3628fe16ca5f2203720af7943a3f05','unityRun':False,'playerRun':False,'diagnosticOnly':True,'commands':[]}
count=0;runtime=contents/'NetCoreRuntime/dotnet';csc=contents/'DotNetSdkRoslyn/csc.dll'
def command(args,cwd):
    global count
    count+=1;previous=Path.cwd()
    try:
        os.chdir(cwd);r=run_owned_command(args,out/'commands'/('%03d'%count),180);clean_outer(r,0)
        report['commands'].append({'command':count,'cwd':str(cwd),'passed':True});return r
    finally:os.chdir(previous)
try:
    refs=sorted((contents/'NetStandard/ref/2.1.0').glob('*.dll'));assert refs
    analyzer=contents/'Tools/Unity.SourceGenerators/Unity.SourceGenerators.dll'
    assert hashlib.sha256(analyzer.read_bytes()).hexdigest()=='9fe0035b735b968c517eefbfe418a1a9a5f951e3c119265af789d1ea24b964d4'
    images=[]
    for mode in ('Development','Release'):
        for repeat in ('first','second'):
            root=out/(mode+'-'+repeat);root.mkdir();src=root/'Assets/AssemblyShadowBaseline/HotUpdate/Entry.cs';src.parent.mkdir(parents=True)
            shutil.copyfile(demo/'Assets/AssemblyShadowBaseline/HotUpdate/Entry.cs',src);(root/'out').mkdir();(root/'generated').mkdir()
            (root/'source.UnityAdditionalFile.txt').write_text(str(root))
            args=[runtime,csc,'/noconfig','/nologo','/nostdlib+','/target:library','/langversion:9.0','/deterministic+','/debug:portable','/optimize'+('+' if mode=='Release' else '-'),'/additionalfile:source.UnityAdditionalFile.txt','/out:out/AssemblyShadowBaseline.HotUpdate.dll','/generatedfilesout:generated','/pathmap:'+str(root)+'=/_/r03-m00,'+str(contents)+'=/_/unity','/analyzer:'+str(analyzer)]+['/r:'+str(p) for p in refs]+['Assets/AssemblyShadowBaseline/HotUpdate/Entry.cs']
            command(args,root);image=root/'out/AssemblyShadowBaseline.HotUpdate.dll';images.append(image)
            print('IMAGE',mode,repeat,len(image.read_bytes()),hashlib.sha256(image.read_bytes()).hexdigest(),flush=True)
    tool=out/'semantics';tool.mkdir();shutil.copyfile(package/'Plugins/dnlib.dll',tool/'dnlib.dll')
    bcl=contents/'MonoBleedingEdge/lib/mono/unityaot-macos'
    sources=[workspace/'Tools/AssemblyShadow/LKInvestigation/Semantics.cs',demo/'Tools/AssemblyShadow/R03/HostTests/EnvironmentBoundaries.cs',package/'Editor/AssemblyShadow/Model/ShadowConfiguration.cs',package/'Editor/AssemblyShadow/Metadata/AssemblyIdentityUtil.cs',*sorted((package/'Editor/AssemblyShadow/Hashing').glob('*.cs'))]
    args=[runtime,csc,'/noconfig','/nologo','/nostdlib+','/target:exe','/out:'+str(tool/'Semantics.exe'),'/r:'+str(tool/'dnlib.dll')]+['/r:'+str(bcl/p) for p in ('mscorlib.dll','System.dll','System.Core.dll')]+[str(p) for p in sources]
    command(args,tool)
    historical=demo/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-k-return-required/preflight/ignored-historical-input/AssemblyShadowBaseline.HotUpdate.dll.bytes'
    mono=contents/'MonoBleedingEdge/bin/mono';assert mono.is_file(),mono
    command([mono,tool/'Semantics.exe',historical,*images],tool)
    report['result']='CompletedInvestigation'
except Exception as error:
    report['result']='InvestigationFailed';report['error']=str(error);print('ERROR',error,flush=True)
finally:
    files=[]
    for p in sorted(out.rglob('*')):
        if p.is_file():files.append({'path':str(p.relative_to(out)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    report['files']=files;(out/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')
if report['result']!='CompletedInvestigation':raise SystemExit(1)
