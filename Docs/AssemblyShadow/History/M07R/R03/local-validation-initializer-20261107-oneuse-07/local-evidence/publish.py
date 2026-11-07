from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-Initializer07'
workspace = base.parent / 'assembly_shadow_h1r'
demo = workspace / 'hybridclr_demo'
output = base / 'R03IR-Initializer-20261107-oneuse-07'
host = output.with_name(output.name + '-native-host-raw')
handoff = demo / 'Docs/AssemblyShadow/Handoff'
checkpoint = demo / 'Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-07'
publication = base / 'initializer-07-runtime-PUBLICATION_RECEIPT.json'

def load(path):
    return json.loads(path.read_text())

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

audit = load(preflight / 'FINAL_INDEPENDENT_AUDIT.json')
producer = load(output / 'LOCAL_BATCH_RESULT.json')
runner = load(preflight / 'runner-COMMAND.json')
before = load(preflight / 'PRESERVATION_BEFORE.json')
after = load(preflight / 'PRESERVATION_AFTER.json')
custody = [load(preflight / f'SCOPED_C_{stage}.json') for stage in ('BEFORE','AFTER')]
assert after['independentlyRepeatedBeforeAfterComparison'] == 'Passed'
assert all(r['result'] == 'ScopedHistoricalLossStable' and r['completeScan']
           and (r['presentVerified'], r['historicalStillMissing'], r['originalStrictCustody']) == (339367,77477,'Blocked')
           for r in custody)
pins = audit['sourcePins']
assert pins['hybridclr_demo'] == '6e1dc7b4349a386dc35c5ed46fca4225db273b18'
assert runner['runnerInvocations'] == 1 and not runner['retryPerformed']
assert not checkpoint.exists() and not publication.exists()
assert subprocess.check_output(['git','-C',str(demo),'status','--porcelain']) == b''
summary = (preflight / 'FINDING.md').read_text().strip()
verdict = 'PASS' if runner['exitCode'] == 0 else 'FAIL'
assert (verdict == 'PASS') == (
    producer['result'] == 'FocusedInitializerEvidenceReadyForIndependentReview'
    and audit['cellCounts'] == {'Passed':15} and audit['sealStatus'] == 'Passed'
)
checkpoint.mkdir()
bindings = []

def copy(source, relative, binary=False):
    target = checkpoint / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    hash_value = hashlib.sha256(raw).hexdigest()
    encoding = 'ExactBytes'
    if not binary:
        text = raw.decode('utf-8')
        whitespace = '\r' in text or text.endswith('\n\n') or any(line.endswith((' ', '\t')) for line in text.splitlines())
        malformed_json = False
        if source.suffix == '.json':
            try:
                json.loads(text)
            except ValueError:
                malformed_json = True
        if whitespace or malformed_json:
            target = target.with_name(target.name + '.utf8.json')
            write(target, {'kind':'ExactUtf8TextEvidenceEncoding','source':str(source),
                           'sha256':hash_value,'bytes':len(raw),'text':text})
            encoding = 'Utf8TextField'
    if encoding == 'ExactBytes':
        with target.open('xb') as stream:
            stream.write(raw)
    bindings.append({'source':str(source),'path':str(target.relative_to(checkpoint)),
                     'sha256':hash_value,'bytes':len(raw),'encoding':encoding})

for path in sorted(preflight.iterdir()):
    if path.is_file() and path.suffix in {'.json','.log','.md','.py','.cpp'}:
        copy(path, Path('local-evidence') / path.name)
for name in ('LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','seal-receipt.json','evidence-index.json'):
    path = output / name
    if path.is_file():
        copy(path, Path('batch') / name)
for directory in ('cells','commands','players','builds','host-custody','host/initializer-native-targets'):
    for path in sorted((output / directory).rglob('*')):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(output)
        if relative.suffix in {'.json','.jsonl','.log','.txt'} and path.stat().st_size <= 45*1024**2:
            copy(path, Path('batch') / relative)
        if path.name in {'Methods.dll','HOST_REGULAR_BYTES.tar.gz'} and directory in {'host-custody','host/initializer-native-targets'}:
            copy(path, Path('batch') / relative, binary=True)
for relative in ('Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md',
                 'Tools/AssemblyShadow/R03/PlayerFixtures/InitializerNativeTargetFixtures.cs',
                 'Tools/AssemblyShadow/R03IR/run_initializer_local.py'):
    copy(demo / relative, Path('source') / relative)
for relative in ('RESULT.json','historical-eight/RESULT.json'):
    path = host / relative
    if path.is_file():
        copy(path, Path('host-raw') / relative)

parts = []
archive = output / 'evidence.tar.gz'
if archive.is_file():
    folder = checkpoint / 'sealed-product'
    folder.mkdir()
    offset = 0
    combined = hashlib.sha256()
    with archive.open('rb') as stream:
        while chunk := stream.read(16*1024**2):
            part = folder / f'evidence.tar.gz.part{len(parts):04}'
            part.write_bytes(chunk)
            parts.append({'path':str(part.relative_to(checkpoint)),'offset':offset,
                          'bytes':len(chunk),'sha256':digest(part)})
            combined.update(chunk)
            offset += len(chunk)
    assert combined.hexdigest() == digest(archive)
    if audit['sealStatus'] == 'Passed':
        assert combined.hexdigest() == audit['seal']['archiveSha256']
    write(folder / 'TRANSPORT.json', {'sourcePath':str(archive),'sourceSha256':combined.hexdigest(),
                                     'bytes':offset,'parts':parts,'sealStatus':audit['sealStatus']})
write(checkpoint / 'COPY_BINDINGS.json', {'copies':bindings,'archiveParts':len(parts),
      'rawInventory':'local-evidence/RAW_MANIFEST.json',
      'hostRawInventory':'local-evidence/HOST_RAW_MANIFEST.json',
      'hostLinksPreservedAt':str(host)})
result = {
    'result':verdict,'producerResult':producer['result'],'runner':runner,'sourcePins':pins,
    'cellCounts':audit['cellCounts'],'cellStates':audit['cellStates'],'build':audit['build'],
    'players':audit['players'],'targets':audit['targets'],'seal':audit['seal'],
    'sealStatus':audit['sealStatus'],'hostCustody':audit['hostCustody'],
    'preservation':{'before':before['result'],'after':after['result'],'originalStrictCustody':'Blocked',
                    'priorCheckpoints':len(after['history']),'retiredRootsUnavailable':17},
    'sourceExecutionRoot':str(output),'publicationReceipt':str(publication),
    'runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,
    'ReadyForHumanReviewGate':False,'nextState':'Primary Implementation',
}
write(checkpoint / 'LOCAL_RESULT.json', result)
(checkpoint / 'README.md').write_text(
    f'# Initializer oneuse-07 — {verdict}\n\n{summary}\n\n'
    'The execution source, command receipts, CI, original Player bytes, fixture targets and custody audits are bound in the checkpoint manifest. '
    'Concatenate the sealed archive parts in transport order and verify the original archive SHA-256. '
    'The original product and host roots retain the raw payloads identified by the complete inventories. '
    'Files ending in .utf8.json carry exact original bytes in their UTF-8 text field.\n\n'
    'The separate publication receipt records the closing pushed commit and verified remote heads.\n\n'
    f'- [Local result](LOCAL_RESULT.json)\n- [Independent audit](local-evidence/FINAL_INDEPENDENT_AUDIT.json)\n'
)
rel = '../History/M07R/R03/' + checkpoint.name
capacity1 = load(preflight / 'CAPACITY_1.json')['capacity']['freeGiB']
capacity3 = load(preflight / 'CAPACITY_3.json')['capacity']['freeGiB']
immediate = load(preflight / 'IMMEDIATE_CAPACITY.json')['freeGiB']
gates = (
    f'Execution source was `{pins["hybridclr_demo"]}`. The three mandatory workflows ran six successful OS jobs '
    f'at that SHA. The exact-source jobs compiled and exercised the native observer and writer. The successful managed API compile inputs were matched against the execution sources. '
    f'Fresh capacity was {capacity1:.6f} GiB and {capacity3:.6f} GiB on the same device, '
    f'with {immediate:.6f} GiB at dispatch. Read-only Unity and SDK admission passed. '
    f'Runner PID {runner["pid"]} ran once from {runner["startUtc"]} to {runner["endUtc"]}, UTC. '
    f'Exit code was {runner["exitCode"]}.\n\n'
    'Before and after custody matched 339,367 present and 77,477 historically missing frozen-C identities. '
    'Historical strict custody remains Blocked. The exact 17 retired roots and 40 duplicate paths remain Unavailable. '
    'The surviving oneuse-05 and oneuse-06 raw files, 22 prior checkpoints, Original S, installed SDK and protected outside entries matched their recorded scopes. '
    'The earlier capacity publication receipt retained identical bytes after its documented timestamp change. '
    f'[Preflight and custody]({rel}/local-evidence/PRESERVATION_AFTER.json).\n\n'
    f'The execution tuple is recorded in the [Local result]({rel}/LOCAL_RESULT.json). '
    f'The publication receipt is `{publication}`. All acceptance flags remain false.'
)
owned = []
for name, section in (
    ('LOCAL_VALIDATION.md', f'## Initializer oneuse-07 — {verdict}\n\n{summary}\n\n{gates}'),
    ('RETURN_TO_WEB.md', f'## Initializer oneuse-07 — {verdict}\n\n{summary}\n\n[Result and evidence]({rel}/README.md).'),
):
    path = handoff / name
    prior = path.read_text()
    title, sep, body = prior.partition('\n\n')
    assert sep and prior == subprocess.check_output(
        ['git','-C',str(demo),'show',pins['hybridclr_demo']+':'+str(path.relative_to(demo))],text=True)
    path.write_text(title + '\n\n' + section + '\n\n---\n\n' + body)
    owned.append(str(path.relative_to(demo)))
manifest = checkpoint / 'MANIFEST.sha256'
files = sorted(path for path in checkpoint.rglob('*') if path.is_file())
manifest.write_text(''.join(f'{digest(path)}  {path.relative_to(checkpoint)}\n' for path in files))
write(preflight / 'PUBLICATION_PLAN.json', {'result':verdict,'executionPins':pins,
      'checkpoint':str(checkpoint),'checkpointManifestSha256':digest(manifest),
      'ownedReports':owned,'checkpointFiles':len(files)+1,'archiveParts':len(parts)})
print('Prepared checkpoint', len(files)+1, 'files', len(parts), 'archive parts')
