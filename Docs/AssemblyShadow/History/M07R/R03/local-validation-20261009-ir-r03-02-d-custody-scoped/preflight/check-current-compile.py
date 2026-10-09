import base64, gzip, hashlib, json, subprocess, sys
from pathlib import Path
w, p = map(Path, sys.argv[1:3]); expected = sys.argv[3]
demo = w / 'hybridclr_demo'
def require(ok, message):
    if not ok: raise RuntimeError(message)
def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])
def digest(data): return hashlib.sha256(data).hexdigest()
anchor = 'ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b'
require(git(demo, 'rev-parse', 'HEAD').decode().strip() == expected, 'Wrong demo HEAD')
subprocess.run(['git', '-C', str(demo), 'merge-base', '--is-ancestor', anchor, expected], check=True)
changed = git(demo, 'diff', '--name-only', '-z', anchor, expected).split(b'\0')
require(all(x.startswith(b'Docs/') for x in changed if x), 'Non-Docs delta after compiler source')
e = demo / 'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09'
inputs_bytes = (e / 'compile-inputs.json').read_bytes()
result_bytes = (e / 'compile-result.json').read_bytes()
require(digest(inputs_bytes) == 'e905754b191949b61fc552c179df4cbefc05c6f2f25d364291c84aa1041ea243', 'Input receipt changed')
require(digest(result_bytes) == 'f6250ed4ed4bf013fbf5b0857a4dcf38ec977aa2a63d1c0fa95fea5fb5ed1472', 'Result receipt changed')
i, r = json.loads(inputs_bytes), json.loads(result_bytes)
require(r['result'] == 'Passed' and r['demoCommit'] == anchor and r['runId'] == '37903041633', 'Wrong CI result')
require(r['inputsSha256'] == digest(inputs_bytes) and not r['runtimeAcceptance'], 'Wrong result binding')
require(git(w / 'hybridclr_unity', 'rev-parse', 'HEAD').decode().strip() == r['packageCommit'], 'Wrong package HEAD')
for row in i['inputs']:
    name = row['repository'].split('/')[1]
    require(name in ('hybridclr_demo', 'hybridclr_unity'), 'Unexpected input owner')
    root = w / name; f = root / row['path']; data = f.read_bytes()
    require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'Input bytes differ: ' + str(f))
    require(git(root, 'rev-parse', 'HEAD:' + row['path']).decode().strip() == row['gitBlob'], 'Input Git object differs')
encoded = (e / 'build.log.gz.b64').read_bytes()
require(digest(encoded) == 'd4863193f7d3289aab46853513e2d0c17a827bd7aa5a424890ae80f8435953cb', 'Encoded log changed')
log = gzip.decompress(base64.b64decode(encoded.strip(), validate=True))
require(digest(log) == r['buildLogSha256'], 'Compiler log changed')
with (p / 'compiler-build.log').open('xb') as f: f.write(log)
receipt = {'result':'SourceMatchedManagedApiEvidence','demoCommit':expected,'ciSource':anchor,
           'runId':r['runId'],'inputsMatched':len(i['inputs']),'freshLocalCompile':False,
           'unityRun':False,'runtimeAcceptance':False}
with (p / 'CI_CURRENT_SOURCE.json').open('x') as f: json.dump(receipt, f, indent=2); f.write('\n')
print(json.dumps(receipt))
