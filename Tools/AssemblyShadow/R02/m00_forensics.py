"""Read-only PE provenance diagnosis. No normalization is ever used for admission."""
from __future__ import annotations
import hashlib
from pathlib import Path
import subprocess
import shutil
import tarfile
import uuid
from evidence import audit_archive, binding, check_binding, loads, read, require, write
from m04_metadata import read_identity_bytes
from r01b_diagnostic_inputs import normalized_pe
import ordinary_input

E_COMMIT = '1d7dc134003206ada8a92b50763ca2da7dc9530d'
E_ROOT = 'Docs/AssemblyShadow/History/M07R/R02/local-validation-20260927-batch-e-m00-return-required/'
E_BLOBS = {'candidate': '922dbf928bb7b1de9e383e983f6911eb33e5a75f',
           'control': '35ce524b8ed951b52890f1e07d49844a37537e89'}
E_IMAGES = {'candidate': '9d05065f57806073919b551cb9b23e8f2ef86fab96bb3cb6d8da80f74b82ba99',
            'control': 'b6e8b232d1749ed67db7f7bda028522993c7e912a68192c05cad0fe8ef31f5e5'}


def describe(data, label):
    require(isinstance(data, (bytes, bytearray)) and 0 < len(data) <= 1024*1024, 'Bounded ordinary PE required')
    data = bytes(data)
    identity = read_identity_bytes(data, label)
    normalized, ranges = normalized_pe(data, label)
    fields = []
    for offset, size, kind in ranges:
        raw = data[offset:offset+size]
        row = dict(offset=offset, sizeBytes=size, kind=kind, sha256=hashlib.sha256(raw).hexdigest())
        if kind == 'codeview':
            row.update(pdbId=str(uuid.UUID(bytes_le=raw[4:20])),
                       age=int.from_bytes(raw[20:24], 'little'),
                       pdbPath=raw[24:-1].decode('utf-8', errors='strict'))
        elif kind in ('coff-timestamp', 'debug-timestamp', 'pe-checksum'):
            row['value'] = int.from_bytes(raw, 'little')
        fields.append(row)
    return dict(identity=identity, sha256=hashlib.sha256(data).hexdigest(), sizeBytes=len(data),
                parsedProvenance=fields, maskRanges=ranges,
                normalizedSha256=hashlib.sha256(normalized).hexdigest(), runtimeAcceptance=False)


def compare(left, right, left_label, right_label):
    a, b = describe(left, left_label), describe(right, right_label)
    ranges = []; start = None
    for offset in range(max(len(left), len(right))):
        different = offset >= min(len(left), len(right)) or left[offset] != right[offset]
        if different and start is None: start = offset
        if not different and start is not None:
            ranges.append([start, offset-start]); start = None
    if start is not None: ranges.append([start, max(len(left), len(right))-start])
    same = a['maskRanges'] == b['maskRanges'] and a['normalizedSha256'] == b['normalizedSha256']
    return dict(left=left_label, right=right_label, exactBytesEqual=left == right,
                differingSpans=ranges, equalOutsideExistingPeProvenanceMask=same,
                pdbPathsDiffer=[r.get('pdbPath') for r in a['parsedProvenance'] if r['kind'] == 'codeview'] !=
                               [r.get('pdbPath') for r in b['parsedProvenance'] if r['kind'] == 'codeview'],
                mvidDiffers=a['identity']['mvid'] != b['identity']['mvid'],
                classification=('ExactBytes' if left == right else 'OnlyExistingPeProvenanceRangesDiffer' if same
                                else 'OtherBytesOrLayoutAlsoDiffer'),
                admissionPolicyUnchanged=True, runtimeAcceptance=False)


E_BINDINGS_BLOB = '7d2a0cf83d0550b875f8c1c078daeec3bc1832b5'


def snapshot_file(row, target):
    """Copy exact authenticated input while available, never a dangling locator."""
    source = check_binding(row)
    target.parent.mkdir(parents=True, exist_ok=True)
    require(target.parent == target.parent.resolve(strict=True) and not target.exists() and not target.is_symlink(),
            'Unused canonical snapshot path required')
    with source.open('rb') as incoming, target.open('xb') as outgoing:
        shutil.copyfileobj(incoming, outgoing)
    copied = binding(target)
    require((copied['sha256'], copied['sizeBytes']) == (row['sha256'], row['sizeBytes']), 'Snapshot changed during copy')
    check_binding(row)
    return copied


def git_bytes(project, relative, expected):
    raw = subprocess.check_output(['git', '-C', str(project), 'show', E_COMMIT + ':' + relative], timeout=90)
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == expected, 'Historical preparation Git blob changed: ' + relative)
    return raw


def archived_origin(project, output):
    # Only the exact original E index/archive, selected by an immutable Git
    # binding, is allowed. Never search for a matching basename or newer run.
    raw = git_bytes(project, E_ROOT + 'LIVE_EVIDENCE_BINDINGS.json', E_BINDINGS_BLOB)
    origin = loads(raw.decode('utf-8'))
    require(origin.get('kind') == 'R02LocalBatchELiveEvidenceBindings' and
            origin.get('result') == 'AuthenticatedAtCheckpoint', 'Wrong historical archive authority')
    root = origin['batchRoot']
    expected = {}
    for name in ('seal-index.json', 'evidence.tar.gz'):
        matches = [r for r in origin['files'] if r['path'] == root + '/seal/' + name]
        require(len(matches) == 1, 'No unique exact E archive binding: ' + name)
        expected[name] = matches[0]
    folder = output / 'archive-origin'; folder.mkdir()
    (folder / 'git-binding.json').write_bytes(raw)
    index_copy = snapshot_file(expected['seal-index.json'], folder / 'seal-index.json')
    archive_copy = snapshot_file(expected['evidence.tar.gz'], folder / 'evidence.tar.gz')
    index = read(Path(index_copy['path']))
    require(index.get('result') == 'Passed' and index.get('archive') == expected['evidence.tar.gz'],
            'Archive/index binding disagreement')
    # The original index bytes are retained verbatim; this read-only projection
    # directs the existing full member audit at the exact newly copied archive.
    audit_archive(dict(index, archive=archive_copy))
    return dict(index=index, archive=archive_copy, retained=[binding(folder / 'git-binding.json'), index_copy, archive_copy])


def recover_member(original, origin, target):
    matches = [r for r in origin['index']['files'] if r['path'] == original['path']]
    require(len(matches) == 1, 'Exact historical locator missing from archive index: ' + original['path'])
    row = matches[0]
    require(all(row[k] == original[k] for k in ('path', 'sha256', 'sizeBytes')) and
            row['member'] == 'blobs/' + original['sha256'], 'Historical member identity disagreement')
    check_binding(origin['archive'])
    found = False
    with tarfile.open(origin['archive']['path'], 'r|gz') as archive:
        for member in archive:
            if member.name != row['member']:
                continue
            require(not found and member.isfile() and member.size == original['sizeBytes'], 'Invalid selected member')
            data = archive.extractfile(member).read(original['sizeBytes'] + 1)
            require(len(data) == original['sizeBytes'] and hashlib.sha256(data).hexdigest() == original['sha256'],
                    'Selected archive bytes changed')
            with target.open('xb') as stream:
                stream.write(data)
            found = True
    require(found, 'Required historical member unavailable')
    check_binding(origin['archive'])
    return binding(target)


def analyze_batch_e(project, output):
    require(output.is_absolute() and output == output.resolve() and not output.exists(), 'Unused canonical M00 forensic output required')
    output.mkdir(parents=True)
    report = dict(kind='R02M00BatchEForensics', result='Failed', checkpoint=E_COMMIT,
                  receipts={}, images={}, comparisons=[], retainedInputs=[], runtimeAcceptance=False,
                  historicalPlayerExecutionReused=False, inputsSnapshotted=False, inputAcquisition={},
                  limitation='PE fields identify observed differences; they do not reconstruct all compiler arguments.')
    try:
        frozen, encoded, origin, _ = ordinary_input.fixture(project)
        report['retainedInputs'].extend((encoded, origin))
        data = {'frozen': frozen}
        origin_archive = None
        for role in ('candidate', 'control'):
            relative = E_ROOT + 'ordinary-preparation-' + role + '.json'
            raw = git_bytes(project, relative, E_BLOBS[role])
            blob = E_BLOBS[role]
            receipt_copy = output / (role + '-original-preparation.json')
            receipt_copy.write_bytes(raw)
            report['retainedInputs'].append(binding(receipt_copy))
            receipt = loads(raw.decode('utf-8'))
            report['receipts'][role] = dict(path=relative, gitBlob=blob, originalResult=receipt['result'],
                                           sourcePinsSha256=receipt['sourcePinsSha256'], sources=receipt['sources'])
            require(receipt.get('result') == 'Failed' and receipt['compiled']['sha256'] == E_IMAGES[role] and
                    receipt.get('expectedSha256') == ordinary_input.IMAGE_SHA256, 'Not the pinned failed E preparation')
            original = receipt['compiled']
            require(original['sizeBytes'] == ordinary_input.SIZE, 'Unexpected E input size')
            path = Path(original['path'])
            target = output / (role + '-original.dll')
            report['inputAcquisition'][role] = dict(original=original, classification='AcquisitionPending')
            if path.exists() or path.is_symlink():
                copied = snapshot_file(original, target)
                acquisition = 'AuthenticatedLiveSnapshot'
            else:
                if origin_archive is None:
                    origin_archive = archived_origin(project, output)
                    report['retainedInputs'].extend(origin_archive['retained'])
                copied = recover_member(original, origin_archive, target)
                acquisition = 'AuthenticatedArchiveMemberSnapshot'
            report['inputAcquisition'][role] = dict(classification=acquisition, original=original, snapshot=copied)
            data[role] = target.read_bytes(); report['retainedInputs'].append(copied)
            check_binding(copied)
        report['inputsSnapshotted'] = True
        for label, raw in data.items(): report['images'][label] = describe(raw, label)
        for a, b in (('frozen', 'candidate'), ('frozen', 'control'), ('candidate', 'control')):
            report['comparisons'].append(compare(data[a], data[b], a, b))
        for item in report['retainedInputs']: check_binding(item)
        report['result'] = 'AnalyzedNotRuntimeAccepted'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(output / 'analysis.json', report)
    return report
