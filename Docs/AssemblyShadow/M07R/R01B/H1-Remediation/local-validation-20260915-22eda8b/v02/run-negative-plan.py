from pathlib import Path
import hashlib
import json
import plistlib
import sys

TOOLS=Path(__file__).resolve().parents[7]/'Tools'/'AssemblyShadow'
sys.path.insert(0,str(TOOLS))
import h1_native_capture as native

root=(Path(__file__).resolve().parent/'negative-plan-inputs').resolve()
root.mkdir()
(root/'Library/Bee').mkdir(parents=True)
compiler=root/'clang'
compiler.write_bytes(b'synthetic-not-executed')
sdk=root/'sdk'
sdk.mkdir()
(sdk/'SDKSettings.plist').write_bytes(plistlib.dumps({'Version':'synthetic'}))
binary=root/'Built/GameAssembly.dylib'
binary.parent.mkdir()
binary.write_bytes(b'synthetic-not-executed')
config=root/'il2cpp-config.h'
config.write_text('#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n')
flags=f'{compiler} -isysroot {sdk} -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1'
units=[]
for i in range(446):
    units.append({
        'Annotation':'C_Mac_arm64',
        'Action':flags+(' -DIL2CPP_DEBUG=1' if i>=16 else '')+f' -c unit{i}.cpp -o unit{i}.o',
        'Inputs':[],
        'Outputs':[f'unit{i}.o'],
    })
graph={'Nodes':units+[
    {'Annotation':'Link_Mac_arm64','Action':f'{compiler} -isysroot {sdk}',
     'Inputs':[u['Outputs'][0] for u in units],'Outputs':['Library/GameAssembly.dylib']},
    {'Annotation':'Copy','Inputs':['Library/GameAssembly.dylib'],'Outputs':[str(binary)]},
]}
graph_path=root/'Library/Bee/Player-negative.dag.json'
graph_path.write_text(json.dumps(graph,indent=2)+'\n')
request={
    'projectRoot':str(root),
    'before':{'entries':[]},
    'buildId':'H1Count-On-Debug',
    'buildGuid':'a'*32,
    'inputSnapshotHash':'b'*64,
    'nativeLibraryPath':str(binary),
    'nativeLibrarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
    'sourcePinSha256':'c'*64,
    'il2cppConfigPath':str(config),
    'cppConfiguration':'Debug',
    'featureEnabled':True,
}
request_path=root/'request.json'
request_path.write_text(json.dumps(request,indent=2)+'\n')
output=(Path(__file__).resolve().parent/'negative-plan-attempt').resolve()
try:
    native.capture_request(request_path,output)
except Exception as exc:
    print(type(exc).__name__+': '+str(exc))
    raise SystemExit(0)
raise SystemExit('Expected bounded negative planning failure did not occur')
