"""Materialize the byte-pinned historical input; never substitute compiler output."""
from __future__ import annotations
import base64
import hashlib
import os
import zlib
from pathlib import Path
from evidence import binding, check_binding, read, require, write
from h1_witness_contract import IMAGE_PATH, IMAGE_SHA256, PROVIDER
from m04_metadata import read_identity_bytes

FIXTURE = 'Tools/AssemblyShadow/R02/fixtures/m00-frozen.dll.zlib.base64.txt'
ORIGIN = 'Tools/AssemblyShadow/R02/fixtures/m00-origin.json'
SIZE = 4608
ARCHIVE_SHA = '2ecb3d04cdd093c469717d4c2959ec416ec8d0745c51c2a4ba37c82f9bc253e8'
MEMBER = ('_temp/AssemblyShadow/H1Authority925e-FailureFixtures-20260919A/'
          'CompileSnapshot/ReflectionBindings/Images/' + IMAGE_SHA256 + '.dll.bytes')
CLASSIFICATION = 'FrozenHistoricalInputMaterialization'
PINS = 'ProjectSettings/AssemblyShadowSourcePins.json'


def fixture(project):
    encoded_binding = binding(project / FIXTURE)
    origin_binding = binding(project / ORIGIN)
    encoded = (project / FIXTURE).read_bytes()
    require(len(encoded) <= 8192 and encoded.endswith(b'\n'), 'Invalid frozen fixture encoding')
    compressed = base64.b64decode(encoded[:-1], validate=True)
    require(base64.b64encode(compressed) + b'\n' == encoded, 'Noncanonical frozen fixture encoding')
    decoder = zlib.decompressobj()
    try:
        data = decoder.decompress(compressed, SIZE + 1)
    except zlib.error as error:
        require(False, 'Malformed compressed frozen fixture: ' + str(error))
    require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail, 'Truncated or oversized frozen fixture')
    require(len(data) == SIZE and hashlib.sha256(data).hexdigest() == IMAGE_SHA256,
            'Frozen fixture bytes differ; no compiler-output fallback')
    identity = read_identity_bytes(data, FIXTURE)
    require(identity['fullName'] == PROVIDER, 'Frozen provider identity differs')
    origin = read(project / ORIGIN)
    require(origin.get('kind') == 'R02FrozenM00Origin' and origin.get('schemaVersion') == 1 and
            origin.get('encoding') == 'zlib+base64' and
            origin.get('imageSha256') == IMAGE_SHA256 and origin.get('sizeBytes') == SIZE and
            origin.get('archiveSha256') == ARCHIVE_SHA and origin.get('member') == MEMBER and
            origin.get('archive') == 'Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority925e/raw-evidence.tar.gz' and
            origin.get('classification') == 'ImmutableHistoricalInputNotNewCompilation' and
            origin.get('runtimeAcceptance') is False and origin.get('historicalPlayerExecutionReused') is False,
            'Frozen fixture origin differs')
    check_binding(encoded_binding); check_binding(origin_binding)
    return data, encoded_binding, origin_binding, identity


def preflight(project, output):
    require(project.is_absolute() and project == project.resolve(strict=True), 'Canonical ordinary-input project required')
    require(output.parent == project / '_temp/AssemblyShadow' and not output.exists(), 'Unused ordinary-input root required')
    destination = project / IMAGE_PATH
    for path in (output, destination):
        require(not path.is_symlink() and all(not p.is_symlink() for p in path.parents), 'Linked ordinary-input path')
    fixture(project)
    if destination.exists():
        require(binding(destination)['sha256'] == IMAGE_SHA256, 'Existing M00 input differs; preserve it')


def _create(path, data):
    require(not path.is_symlink() and all(not p.is_symlink() for p in path.parents), 'Linked materialization path')
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: neither foreign bytes nor a racing writer is replaced.
    with path.open('xb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def prepare(project, output):
    preflight(project, output)
    output.mkdir(parents=True)
    row = dict(kind='R02OrdinaryInputPreparation', schemaVersion=2, result='Failed',
               projectRoot=str(project), outputRoot=str(output), expectedSha256=IMAGE_SHA256,
               classification=CLASSIFICATION, freshCscExecutionClaimed=False,
               historicalPlayerExecutionReused=False, runtimeAcceptance=False)
    try:
        data, encoded, origin, identity = fixture(project)
        row.update(fixture=encoded, origin=origin, identity=identity,
                   sourcePinsSha256=binding(project / PINS)['sha256'])
        destination = project / IMAGE_PATH
        row['destinationBefore'] = binding(destination) if destination.exists() else None
        _create(output / 'materialized.dll.bytes', data)
        if destination.exists():
            require(binding(destination)['sha256'] == IMAGE_SHA256, 'Existing M00 input changed; preserve it')
        else:
            _create(destination, data)
        row['materialized'] = binding(output / 'materialized.dll.bytes')
        row['staged'] = binding(destination)
        check_binding(encoded); check_binding(origin)
        require(binding(project / PINS)['sha256'] == row['sourcePinsSha256'], 'Source pins changed during materialization')
        require(row['staged']['sha256'] == IMAGE_SHA256, 'Staged M00 bytes changed')
        row['result'] = 'Passed'
    except Exception as error:
        row['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(output / 'preparation.json', row)
    return verify(project, output)


def verify(project, output):
    receipt = read(output / 'preparation.json')
    require(receipt.get('kind') == 'R02OrdinaryInputPreparation' and receipt.get('schemaVersion') == 2 and
            receipt.get('result') == 'Passed', 'Ordinary-input materialization did not pass')
    require(receipt.get('projectRoot') == str(project) and receipt.get('outputRoot') == str(output), 'Wrong workspace/output')
    require(receipt.get('classification') == CLASSIFICATION and receipt.get('freshCscExecutionClaimed') is False and
            receipt.get('historicalPlayerExecutionReused') is False and receipt.get('runtimeAcceptance') is False,
            'Invalid historical-input claim')
    data, encoded, origin, identity = fixture(project)
    require(receipt.get('fixture') == encoded and receipt.get('origin') == origin and receipt.get('identity') == identity,
            'Fixture binding or provider identity changed')
    require(receipt.get('expectedSha256') == IMAGE_SHA256 and receipt.get('sourcePinsSha256') ==
            binding(project / PINS)['sha256'], 'Ordinary-input contract/pins changed')
    for key, path in (('materialized', output / 'materialized.dll.bytes'), ('staged', project / IMAGE_PATH)):
        record = receipt[key]
        require(record['path'] == str(path) and record['sha256'] == IMAGE_SHA256 and record['sizeBytes'] == len(data),
                'Wrong frozen input bytes/path')
        check_binding(record)
    before = receipt.get('destinationBefore')
    require(before is None or before == receipt['staged'], 'Existing staged input was replaced or changed')
    return dict(kind='R02OrdinaryInputAuthentication', result='Passed', classification=CLASSIFICATION,
                projectRoot=str(project), receipt=binding(output / 'preparation.json'), staged=receipt['staged'],
                runtimeAcceptance=False, freshCscExecutionClaimed=False)
