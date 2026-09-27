"""Read-only PE provenance diagnosis. No normalization is ever used for admission."""
from __future__ import annotations
import hashlib
from pathlib import Path
import subprocess
import uuid
from evidence import binding, check_binding, loads, require, write
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


def analyze_batch_e(project, output):
    require(not output.exists(), 'Unused M00 forensic output required')
    output.mkdir(parents=True)
    report = dict(kind='R02M00BatchEForensics', result='Failed', checkpoint=E_COMMIT,
                  receipts={}, images={}, comparisons=[], retainedInputs=[], runtimeAcceptance=False,
                  historicalPlayerExecutionReused=False,
                  limitation='PE fields identify observed differences; they do not reconstruct all compiler arguments.')
    try:
        frozen, encoded, origin, _ = ordinary_input.fixture(project)
        report['retainedInputs'].extend((encoded, origin))
        data = {'frozen': frozen}
        for role in ('candidate', 'control'):
            relative = E_ROOT + 'ordinary-preparation-' + role + '.json'
            raw = subprocess.check_output(['git', '-C', str(project), 'show', E_COMMIT + ':' + relative], timeout=90)
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            require(blob == E_BLOBS[role], 'Historical preparation Git blob changed')
            receipt = loads(raw.decode('utf-8'))
            report['receipts'][role] = dict(path=relative, gitBlob=blob, originalResult=receipt['result'],
                                           sourcePinsSha256=receipt['sourcePinsSha256'], sources=receipt['sources'])
            require(receipt.get('result') == 'Failed' and receipt['compiled']['sha256'] == E_IMAGES[role] and
                    receipt.get('expectedSha256') == ordinary_input.IMAGE_SHA256, 'Not the pinned failed E preparation')
            path = check_binding(receipt['compiled'])
            require(path.stat().st_size == ordinary_input.SIZE, 'Unexpected E input size')
            data[role] = path.read_bytes(); report['retainedInputs'].append(receipt['compiled'])
            check_binding(receipt['compiled'])
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
