#!/usr/bin/env python3
"""Feed real serializer output from the synthetic class census into actual writer.

This demonstrates a supported-size incompatibility; it does NOT assert that N's
unrecorded class census or first writer failure had this size or cause.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
from test_snapshot_integration import prepare
from classify_snapshot_failure import classify
H = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--producer-json', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
data = a.producer_json.read_bytes()
parsed = json.loads(data)
assert len(parsed['classes']) == 1024 and len(data) == 331078
assert hashlib.sha256(data).hexdigest() == '3d68d22ef23e09b677c06e44f44acac5042b819987719c6cc2937f830f05785a'
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
base = H/'candidate/hybridclr_demo/Tools/AssemblyShadow'
code = prepare(base/'R03/PlayerProject/AssemblyShadowR03Probe.cpp', base/'R03IR/PlayerProject/R03TerminalPlayer.cs')
code = '#include <fstream>\n#include <iterator>\n' + code
assert code.count('assert(argc==3);') == 1
code = code.replace('assert(argc==3);', 'assert(argc==4);')
old = ' std::string text;'
assert code.count(old) == 1
code = code.replace(old, old + r'''
 if(mode=="producer-json") {
  std::ifstream input(argv[3], std::ios::binary);
  text.assign(std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>());
  assert(text.size()==331078);r.finalExecutionDiagnostics=text.c_str();expect=false;
 }
''')
(out/'producer_to_snapshot.cpp').write_text(code)
cc=shutil.which('clang++') or shutil.which('g++'); assert cc
records=[]
for name, flags in [('strict', []), ('sanitized', ['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    exe=out/name
    argv=[cc,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread',*flags,str(out/'producer_to_snapshot.cpp'),'-o',str(exe)]
    c=subprocess.run(argv,capture_output=True,timeout=40)
    (out/(name+'-compile.stdout')).write_bytes(c.stdout); (out/(name+'-compile.stderr')).write_bytes(c.stderr)
    assert c.returncode == 0,c.stderr.decode()
    raw=out/(name+'-raw.json')
    argv2=[str(exe),'producer-json',str(raw),str(a.producer_json.resolve())]
    r=subprocess.run(argv2,capture_output=True,timeout=20)
    (out/(name+'.stdout')).write_bytes(r.stdout); (out/(name+'.stderr')).write_bytes(r.stderr)
    assert r.returncode == 0,r.stderr.decode()
    pid=int(re.search(rb'pid=(\d+)', r.stderr).group(1))
    diag=classify(r.stderr,pid,hashlib.sha256(r.stderr).hexdigest())
    assert diag['firstFailure']['reasonCode']==9 and diag['firstFailure']['slot']==15
    assert raw.stat().st_size == 0
    (out/(name+'-classification.json')).write_text(json.dumps(diag,indent=2)+'\n')
    records.append({'profile':name,'compilerArgv':argv,'compilerExit':0,'processArgv':argv2,'processExit':0,
                    'producerBytes':len(data),'producerSha256':hashlib.sha256(data).hexdigest(),
                    'stderrSha256':hashlib.sha256(r.stderr).hexdigest(),'rawBytes':0,
                    'classification':diag,'NRootCauseProven':False})
result={'result':'SizeIncompatibilityAndPreciseFailureReproduced','compilerProcessRecords':4,
        'sourceFunctions':'Real execution serializer, actual candidate writer and exact translated C# emission sequence',
        'syntheticDependencies':'1024-class census/VM metadata, guard producer and report values; no Unity/IL2CPP marshalling',
        'NRootCauseProven':False,'originalLimitsUnchanged':True,'records':records}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
