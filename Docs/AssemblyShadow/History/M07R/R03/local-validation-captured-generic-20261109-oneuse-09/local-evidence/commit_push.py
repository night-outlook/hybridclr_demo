from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-CapturedGeneric09'
workspace = base.parent / 'assembly_shadow_h1r'
demo = workspace / 'hybridclr_demo'
branch = 'codex/assembly-shadow-r01b-h1'
plan = json.loads((preflight / 'PUBLICATION_PLAN.json').read_text())
checkpoint = Path(plan['checkpoint'])
pins = plan['executionPins']
owned = set(plan['ownedReports'])
start = datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def git(repo, *args):
    command = ['git','-C',str(repo),*args]
    result = subprocess.run(command, text=True, capture_output=True, check=True, timeout=120)
    return result.stdout

def verify(item, clean=True):
    name, commit = item
    repo = workspace / name
    info = {}
    for key, args in {
        'root':('rev-parse','--show-toplevel'),
        'branch':('branch','--show-current'),
        'head':('rev-parse','HEAD'),
        'status':('status','--short'),
        'remote':('ls-remote','origin','refs/heads/'+branch),
    }.items():
        info[key] = git(repo,*args).strip()
    assert info['root'] == str(repo) and info['branch'] == branch and info['head'] == commit, info
    assert info['remote'] == f'{commit}\trefs/heads/{branch}', info
    assert not info['status'] if clean else True
    return name, info

with ThreadPoolExecutor(max_workers=4) as pool:
    authority = dict(pool.map(lambda item: verify(item, item[0] != 'hybridclr_demo'), pins.items()))
manifest = checkpoint / 'MANIFEST.sha256'
assert sha(manifest) == plan['checkpointManifestSha256']
manifest_paths = set()
for line in manifest.read_text().splitlines():
    expected, relative = line.split('  ', 1)
    path = checkpoint / relative
    assert path.is_file() and not path.is_symlink() and sha(path) == expected, path
    manifest_paths.add(relative)
    if path.suffix == '.json':
        json.loads(path.read_text())
assert {str(path.relative_to(checkpoint)) for path in checkpoint.rglob('*') if path.is_file()} == manifest_paths | {'MANIFEST.sha256'}
for entry in json.loads((checkpoint / 'COPY_BINDINGS.json').read_text())['copies']:
    dest = checkpoint / entry['path']
    raw = (json.loads(dest.read_text())['text'].encode('utf-8')
           if entry['encoding'] == 'Utf8TextField' else dest.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == entry['sha256'] == sha(Path(entry['source']))
archive = checkpoint / 'sealed-product/TRANSPORT.json'
if archive.is_file():
    transport = json.loads(archive.read_text())
    combined = hashlib.sha256()
    offset = 0
    for part in transport['parts']:
        data = (checkpoint / part['path']).read_bytes()
        assert part['offset'] == offset and part['bytes'] == len(data)
        assert hashlib.sha256(data).hexdigest() == part['sha256']
        combined.update(data)
        offset += len(data)
    assert combined.hexdigest() == transport['sourceSha256'] and offset == transport['bytes']
prefix = str(checkpoint.relative_to(demo))
for relative in owned:
    older = git(demo,'show',pins['hybridclr_demo']+':'+relative)
    assert (demo / relative).read_text().endswith(older.partition('\n\n')[2])
status = authority['hybridclr_demo']['status']
# Treat the leading status column separately since verify strips outer whitespace.
status = git(demo,'status','--short','--untracked-files=all')
for line in status.splitlines():
    name = line[3:]
    assert name in owned or name.startswith(prefix+'/'), line
git(demo,'add','-f','--',prefix,*sorted(owned))
git(demo,'diff','--cached','--check')
git(demo,'diff','--check')
staged = git(demo,'diff','--cached','--name-only').splitlines()
assert set(staged) == owned | {prefix+'/'+x for x in manifest_paths|{'MANIFEST.sha256'}}
for relative in staged:
    assert git(demo,'rev-parse',':'+relative).strip() == git(demo,'hash-object',relative).strip(), relative
git(demo,'commit','-m','docs: publish captured-generic oneuse-09 Local validation evidence')
head = git(demo,'rev-parse','HEAD').strip()
assert git(demo,'rev-parse','HEAD^').strip() == pins['hybridclr_demo']
assert not git(demo,'status','--short')
assert not git(demo,'diff',pins['hybridclr_demo'],head,'--','.',':(exclude)Docs')
print('Committed',head,flush=True)
command = ['git','-C',str(demo),'push','--progress','origin','HEAD:refs/heads/'+branch]
with (preflight/'publication-push.log').open('xb') as log:
    pushed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
assert pushed.returncode == 0
heads = {**pins,'hybridclr_demo':head}
with ThreadPoolExecutor(max_workers=4) as pool:
    verified = dict(pool.map(verify, heads.items()))
receipt = {
    'result':'PublishedAndVerifiedAllFourRemoteHeads',
    'validationResult':plan['result'],'executionPins':pins,'latestPushedHeads':heads,
    'repositories':verified,'prepublicationSourceAuthority':authority,
    'checkpoint':str(checkpoint),'checkpointManifestSha256':sha(manifest),
    'checkpointFiles':plan['checkpointFiles'],'stagedFiles':len(staged),
    'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'pushCommand':command,'pushExitCode':pushed.returncode,'pushLogSha256':sha(preflight/'publication-push.log'),
    'runnerInvocations':1,'R03Accepted':False,'runtimeAcceptance':False,'H2Passed':False,
    'ReadyForHumanReviewGate':False,'nextState':'Primary Implementation',
}
with (base/'captured-generic-09-runtime-PUBLICATION_RECEIPT.json').open('x') as stream:
    json.dump(receipt,stream,indent=2)
    stream.write('\n')
print(receipt['result'],head,flush=True)
