#!/usr/bin/env python3
"""Read-only original-S reconstruction; never changes historical verdicts."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

PUBLICATION = 'fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b'
EXECUTED = '29bb3d4a39bf8a2f23be404f77535aaba3485bfc'
CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready'
EXPECTED = {'hybridclr_demo': EXECUTED,
    'hybridclr': '4b2774b066cfc6afd77a8c8aded6bda7ea574f55',
    'hybridclr_unity': '948c0e3b4f8891481301770115e8ba4945eea6de',
    'il2cpp_plus': '1cf87f8209790f9fb2ebec97487dc1990ccd56c5'}
ORIGINAL = {
    'BATCH_EXECUTION.json': '241144d39b1cfa47be3dcd4f67a3e40f7608ab58d605117c81fcccea8c68a427',
    'LOCAL_BATCH_RESULT.json': '2e09d46c800d7721eb14a6d7a31ba1d89327d1126ff7f7be35dd889bdbdf3096',
    'evidence-index.json': '0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70',
    'evidence.tar.gz': '23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6',
    'seal-receipt.json': 'd382557e62c3e897070305daeedb452a2ab0d3f409af42e58be8fd8f03109dcf'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    value = {}
    for k, v in items:
        require(k not in value, 'Duplicate JSON key: ' + k)
        value[k] = v
    return value


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def relpath(value):
    p = PurePosixPath(value)
    require(bool(value) and not p.is_absolute() and '..' not in p.parts and
            str(p) == value and '\\' not in value, 'Unsafe/noncanonical path: ' + value)
    return p


def file_under(root, value):
    path = root / relpath(value)
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
            'Missing/nonregular file: ' + value)
    return path


def write(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def audit(repo, output, include_archive=False):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(repo), 'Unused external output required')
    require(git(repo, 'rev-parse', 'HEAD').decode().strip() == PUBLICATION, 'Exact original S publication checkout')
    require(not git(repo, 'status', '--porcelain'), 'Original checkout must be clean')
    checkpoint = repo / CHECKPOINT
    output.mkdir(parents=True)
    scratch = output / 'reconstructed'
    scratch.mkdir()
    report = {'kind': 'IRR03OriginalSProvenanceAudit', 'result': 'Failed',
        'inputCommit': PUBLICATION, 'executionCommit': EXECUTED,
        'auditScriptSha256': digest(__file__), 'runtimeAcceptance': False,
        'independentReviewer': False, 'unityRun': False, 'historicalInputsModified': False}
    try:
        tree = git(repo, 'ls-tree', '-r', '-z', PUBLICATION, '--', CHECKPOINT)
        tracked = {}
        for line in tree.split(b'\0'):
            if not line:
                continue
            attrs, path = line.split(b'\t', 1)
            mode, kind, oid = attrs.decode().split()
            name = path.decode()[len(CHECKPOINT) + 1:]
            require(kind == 'blob' and mode in ('100644', '100755'), 'Nonregular tracked checkpoint entry')
            f = file_under(checkpoint, name)
            h = hashlib.sha1(('blob ' + str(f.stat().st_size) + '\0').encode())
            with f.open('rb') as stream:
                for block in iter(lambda: stream.read(1048576), b''):
                    h.update(block)
            require(h.hexdigest() == oid, 'Git blob mismatch: ' + name)
            tracked[name] = {'gitBlob': oid, 'size': f.stat().st_size, 'sha256': digest(f)}
        write(output / 'checkpoint-git-crosswalk.json', tracked)
        manifest = file_under(checkpoint, 'MANIFEST.sha256')
        manifest_names = set()
        for line in manifest.read_text().splitlines():
            sha, name = line.split('  ', 1)
            require(name not in manifest_names and name in tracked, 'Duplicate/untracked manifest file')
            require(tracked[name]['sha256'] == sha, 'Checkpoint manifest mismatch: ' + name)
            manifest_names.add(name)
        require(set(tracked) == manifest_names | {'MANIFEST.sha256'}, 'Exact tracked checkpoint manifest membership')
        transports = load(checkpoint / 'FILE_TRANSPORT.json')
        transport_rows, reconstructed = [], {}
        for row in transports['files']:
            rel = str(relpath(row['originalPath']))
            require(rel not in reconstructed, 'Duplicate transported original')
            dst = scratch / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            total, h, seen = 0, hashlib.sha256(), set()
            with dst.open('xb') as out:
                for i, part in enumerate(row['parts']):
                    path = part['path']
                    require(path not in seen and path == rel + '.parts/part-%03d.part' % i, 'Unique ordered transport parts')
                    require(path in tracked and tracked[path]['sha256'] == part['sha256'] and
                            tracked[path]['size'] == part['size'], 'Transport part binding')
                    seen.add(path)
                    with file_under(checkpoint, path).open('rb') as inp:
                        for block in iter(lambda: inp.read(1048576), b''):
                            out.write(block); h.update(block); total += len(block)
            require(total == row['originalSize'] and h.hexdigest() == row['originalSha256'], 'Reconstruction differs: ' + rel)
            reconstructed[rel] = dst
            transport_rows.append({'path': rel, 'size': total, 'sha256': h.hexdigest(), 'parts': len(seen)})
        def original(name):
            return reconstructed.get('batch/' + name, checkpoint / 'batch' / name)
        artifacts = {n: {'sha256': digest(original(n)), 'size': original(n).stat().st_size} for n in ORIGINAL}
        require(all(artifacts[n]['sha256'] == d for n, d in ORIGINAL.items()), 'Pinned original five-artifact identity')
        seal, index = load(original('seal-receipt.json')), load(original('evidence-index.json'))
        items = {}
        for item in index['files']:
            relpath(item['path'])
            require(item['path'] not in items, 'Duplicate indexed path')
            items[item['path']] = item
        require(len(items) == 15712 and seal['members'] == len(items) + 1, 'Original S cardinalities')
        require(seal['archiveSha256'] == artifacts['evidence.tar.gz']['sha256'] and
                seal['indexSha256'] == artifacts['evidence-index.json']['sha256'], 'Seal identity')
        expected = dict(items, **{'evidence-index.json': artifacts['evidence-index.json']})
        members = {}
        with tarfile.open(original('evidence.tar.gz'), 'r|gz') as archive:
            for entry in archive:
                name = str(relpath(entry.name))
                require(entry.isfile() and name not in members and name in expected, 'Nonregular/duplicate/extra archive member')
                h = hashlib.sha256()
                with archive.extractfile(entry) as stream:
                    for block in iter(lambda: stream.read(1048576), b''):
                        h.update(block)
                require(entry.size == expected[name]['size'] and h.hexdigest() == expected[name]['sha256'], 'Archive mismatch: ' + name)
                members[name] = {'sha256': h.hexdigest(), 'size': entry.size}
        require(set(members) == set(expected), 'Incomplete archive membership')
        write(output / 'original-archive-members.json', members)
        ledger, result = load(original('BATCH_EXECUTION.json')), load(original('LOCAL_BATCH_RESULT.json'))
        stripped = {k: v for k, v in result.items() if k not in ('seal', 'sealStatus', 'executionLedgerSha256', 'R03Accepted', 'H2Passed')}
        require(stripped == ledger and result['seal'] == seal and result['sealStatus'] == 'Passed' and
                result['executionLedgerSha256'] == artifacts['BATCH_EXECUTION.json']['sha256'], 'Ledger/final result semantic equality')
        require(result['result'] == 'EvidenceReadyForPrimaryReview' and
                all(result['repositories'][k] == v for k, v in EXPECTED.items()), 'Executed source tuple')
        cells = result['cells']; seen = set(); rows = []
        require(len(cells) == 90, 'Exactly ninety cells')
        for cell in cells:
            ident = cell['id']; name = 'cells/' + ident + '.json'
            require(ident not in seen and cell['result'] == 'Passed' and all(d in seen for d in cell['dependencies']), 'Cell/dependency status')
            require(name in members, 'Cell missing from original archive')
            file = file_under(checkpoint, 'batch/' + name)
            require(digest(file) == members[name]['sha256'] and load(file) == cell, 'Ledger/cell equality: ' + ident)
            seen.add(ident)
            evidence = cell.get('evidence', {})
            rows.append({'id': ident, 'cellSha256': members[name]['sha256'], 'dependencies': cell['dependencies'],
                'result': cell['result'], 'launchPid': evidence.get('launchPid'),
                'buildReceiptSha256': evidence.get('buildReceiptSha256'),
                'requestSha256': evidence.get('requestSha256'), 'rawSha256': evidence.get('rawSha256')})
        write(output / 'ninety-cell-crosswalk.json', {'executionTuple': EXPECTED, 'cells': rows})
        recovery = load(checkpoint / 'batch/transaction-recovery/verification.json')
        require(recovery['cleanupResult'] == 'ExactOriginalBytesRestored' and recovery['remoteAuthority'] == 'Passed' and
                recovery['stage'] == 'Complete' and recovery['originalSettingsSha256'] == recovery['afterSettingsSha256'], 'P05 original recovery')
        integration_cell = load(checkpoint / 'batch/cells/production-entry-integration.json')['evidence']
        live = '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/'
        require(integration_cell['path'].startswith(live), 'Exact live integration namespace')
        integration_rel = integration_cell['path'][len(live):]
        require(members[integration_rel]['sha256'] == integration_cell['sha256'], 'Integration receipt binding')
        integration = load(checkpoint / 'batch' / integration_rel)
        require(integration['returnChangedRoots'] == [] and integration['returnClosure'] == [], 'Separate restored-baseline comparison')
        report.update(result='Passed', originalArtifacts=artifacts, transports=transport_rows,
            checkpointFiles=len(tracked), manifestFiles=len(manifest_names), archiveMembers=len(members), indexedFiles=len(items),
            originalResult=result['result'], cells=90, executedRepositories=EXPECTED,
            p05RecoverySha256=digest(checkpoint / 'batch/transaction-recovery/verification.json'),
            integrationSha256=integration_cell['sha256'], firstFailureCitationFlags='Absent, not observed false',
            liveFilesystemCustodyReexecuted=False)
        for name in ('FILE_TRANSPORT.json', 'SOURCE_BINDINGS.json', 'MANIFEST.sha256'):
            (output / name).write_bytes((checkpoint / name).read_bytes())
        for name in ('seal-receipt.json', 'evidence-index.json'):
            (output / name).write_bytes(original(name).read_bytes())
        if include_archive:
            (output / 'original-S-evidence.tar.gz').hardlink_to(original('evidence.tar.gz'))
        require(not git(repo, 'status', '--porcelain'), 'Original checkout changed during audit')
    except BaseException as error:
        report['error'] = str(error)
        raise
    finally:
        write(output / 'audit.json', report)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--include-archive', action='store_true')
    a = p.parse_args()
    print(json.dumps(audit(a.repo, a.output, a.include_archive), sort_keys=True))
