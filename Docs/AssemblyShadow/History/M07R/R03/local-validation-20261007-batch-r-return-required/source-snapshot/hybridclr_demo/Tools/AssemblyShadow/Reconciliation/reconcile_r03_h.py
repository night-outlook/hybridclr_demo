"""Read-only re-audit of published R03 H; never run a Player or promote a stage.

Inputs are the immutable Local publication and its byte-preserving archive.
Outputs must be outside that checkout. Semantic replay imports the ORIGINAL
executed verifier, not a replacement interpretation of its expected results.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET

PUBLICATION = '3a9d51a9bb42b12bf29dfd6e0d7d12956ae04a68'
EXECUTED = '2007c5dbd3dcf535706688e6595700e3ba26a11e'
CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261002-batch-h-evidence-ready'
INDEX_HASH = 'ef0e33ef8efa345bca758539646a8d81aefd2d16b5a1e0b139f78234332d1a28'
ARCHIVE_HASH = 'dd7adb4de12aa7203c69f993e57ebbde49e4f223edfd1179a2945e3d55f6e5cd'
SOURCES = {'hybridclr_demo': EXECUTED,
           'hybridclr': '4b2774b066cfc6afd77a8c8aded6bda7ea574f55',
           'hybridclr_unity': '120bb01be680cec0375002a0823552d66d34b84c',
           'il2cpp_plus': '1cf87f8209790f9fb2ebec97487dc1990ccd56c5'}


def require(value, message):
    if not value:
        raise ValueError(message)


def pairs(items):
    result = {}
    for k, v in items:
        require(k not in result, 'Duplicate JSON member: ' + k)
        result[k] = v
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def digest(path):
    with Path(path).open('rb') as stream:
        return stream_hash(stream)


def stream_hash(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()


def relative(name):
    require(isinstance(name, str) and name and '\\' not in name and '\0' not in name,
            'Unsafe relative path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/'))
            and ':' not in name and str(p) == name, 'Unsafe relative path: ' + name)
    return p


def file_at(root, name):
    p = root.joinpath(*relative(name).parts)
    require(p.is_file() and not p.is_symlink(), 'Missing or linked evidence: ' + name)
    require(all(not x.is_symlink() for x in p.parents if x != root.parent), 'Linked ancestor')
    return p


def audit_index(root, entries):
    table = {}
    for row in entries:
        name = str(relative(row['path']))
        require(name not in table, 'Duplicate indexed path')
        p = file_at(root, name)
        require(p.stat().st_size == row['size'] and digest(p) == row['sha256'], 'Indexed byte mismatch: ' + name)
        table[name] = row
    return table


def audit_archive(archive, table, index):
    expected = dict(table)
    expected['evidence-index.json'] = {'size': index.stat().st_size, 'sha256': digest(index)}
    seen = set()
    with tarfile.open(archive, 'r|gz') as stream:
        for member in stream:
            name = str(relative(member.name))
            require(name not in seen and member.isfile() and name in expected, 'Unsafe/extra/duplicate archive member: ' + name)
            seen.add(name)
            row = expected[name]
            with stream.extractfile(member) as data:
                require(member.size == row['size'] and stream_hash(data) == row['sha256'], 'Archive byte mismatch: ' + name)
    require(seen == set(expected), 'Missing archive members')
    return len(seen)


def self_tests():
    cases = 0
    for name in ('../x', '/x', 'a//b', 'a/./b', 'a\\b', 'a/../b', 'C:/x'):
        try:
            relative(name)
        except ValueError:
            cases += 1
        else:
            raise AssertionError('Unsafe path accepted')
    require(str(relative('a/b.json')) == 'a/b.json', 'Valid path'); cases += 1
    try:
        json.loads('{"x":1,"x":2}', object_pairs_hook=pairs)
    except ValueError:
        cases += 1
    else:
        raise AssertionError('Duplicate JSON accepted')
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); (root/'x').write_bytes(b'exact')
        row = {'path': 'x', 'size': 5, 'sha256': digest(root/'x')}
        require(len(audit_index(root, [row])) == 1, 'Valid inventory'); cases += 1
        for entries in ([row, row], [dict(row, size=6)], [dict(row, sha256='0'*64)]):
            try:
                audit_index(root, entries)
            except ValueError:
                cases += 1
            else:
                raise AssertionError('Invalid inventory accepted')
    return cases


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    pub, output = Path(args.publication).resolve(), Path(args.output).resolve()
    require(not output.exists() and output != pub and pub not in output.parents, 'Unused external output required')
    output.mkdir(parents=True)
    result = {'kind': 'R03HPrimaryReadOnlyReconciliation', 'schemaVersion': 1,
              'result': 'Failed', 'publication': PUBLICATION, 'executedSources': SOURCES,
              'classification': 'ReusedAuditedEvidence', 'newPlayerRuns': 0, 'newEditorRuns': 0,
              'R03Accepted': False, 'H2Passed': False, 'independentStageReview': False,
              'pureInterpreterExpansionEnabled': False, 'fullLegacyRegressionAcceptance': False}
    try:
        result['auditorSelfTests'] = self_tests()
        require(git(pub, 'rev-parse', 'HEAD') == PUBLICATION, 'Exact Local publication required')
        require(not git(pub, 'status', '--porcelain'), 'Publication checkout must be clean')
        changed = git(pub, 'diff', '--name-only', EXECUTED, PUBLICATION).splitlines()
        require(changed and all(p.startswith('Docs/AssemblyShadow/') for p in changed), 'Executable delta after H execution')
        source = pub/'Tools/AssemblyShadow/R03'
        source_tree = git(pub, 'rev-parse', EXECUTED + ':Tools/AssemblyShadow/R03')
        require(source_tree == git(pub, 'rev-parse', PUBLICATION + ':Tools/AssemblyShadow/R03'), 'Exact executed verifier tree')
        result['executedVerifierTree'] = source_tree
        cp = pub/CHECKPOINT; batch = cp/'batch'
        manifest = cp/'MANIFEST.sha256'; before_manifest = digest(manifest)
        entries = []
        for line in manifest.read_text().splitlines():
            checksum, name = line.split('  ', 1)
            entries.append({'path': name, 'size': file_at(cp, name).stat().st_size, 'sha256': checksum})
        checkpoint_table = audit_index(cp, entries)
        actual = {str(p.relative_to(cp)) for p in cp.rglob('*') if p.is_file()}
        require(actual == set(checkpoint_table) | {'MANIFEST.sha256'}, 'Checkpoint exact membership')
        result['checkpointFilesAuthenticated'] = len(checkpoint_table)
        result['checkpointManifestSha256'] = before_manifest
        index = batch/'evidence-index.json'
        require(digest(index) == INDEX_HASH, 'Authoritative H index hash')
        table = audit_index(batch, load(index)['files'])
        require(len(table) == 1901, 'H indexed file count')
        transport, seal = load(cp/'ARCHIVE_TRANSPORT.json'), load(batch/'seal-receipt.json')
        require(transport['originalSha256'] == ARCHIVE_HASH == seal['archiveSha256'], 'Archive authority')
        require(seal['indexSha256'] == INDEX_HASH and seal['runtimeAcceptance'] is False, 'Seal binding and scope')
        archive = output/'reconstructed-h.tar.gz'
        with archive.open('xb') as dest:
            for part in transport['parts']:
                p = file_at(cp, part['path'])
                require(p.stat().st_size == part['size'] and digest(p) == part['sha256'], 'Archive part binding')
                with p.open('rb') as inp:
                    shutil.copyfileobj(inp, dest)
        require(archive.stat().st_size == transport['originalSize'] == 164177597 and digest(archive) == ARCHIVE_HASH, 'Whole archive binding')
        result['archiveMembersAuthenticated'] = audit_archive(archive, table, index)
        require(result['archiveMembersAuthenticated'] == seal['members'] == 1902, 'Archive membership count')
        result.update(indexedFilesAuthenticated=1901, indexSha256=INDEX_HASH, archiveSha256=ARCHIVE_HASH,
                      archiveBytes=archive.stat().st_size, archiveParts=len(transport['parts']))
        # The original archive stays in the publication. Remove only OUR external reconstruction.
        archive.unlink()
        summary, ledger = load(batch/'LOCAL_BATCH_RESULT.json'), load(batch/'BATCH_EXECUTION.json')
        require(summary['cells'] == ledger['cells'], 'Result/ledger cell equality')
        require(summary['result'] == 'EvidenceReadyForPrimaryReview' and summary['sealStatus'] == 'Passed', 'Focused result')
        for name in ('R03Accepted', 'H2Passed', 'pureInterpreterExpansionEnabled', 'fullLegacyRegressionAcceptance'):
            require(summary[name] is False and ledger[name] is False, 'Acceptance promotion: ' + name)
        cells = {c['id']: c for c in summary['cells']}
        require(len(cells) == len(summary['cells']) == 37 and all(c['result'] == 'Passed' for c in cells.values()), '37 Passed cells')
        for name, cell in cells.items():
            require(load(batch/'cells'/ (name+'.json')) == cell, 'Cell/ledger identity: ' + name)
        for name in ('entry-authority', 'final-authority'):
            tuples = cells[name]['evidence']['repositories']
            require(len(tuples) == 4, 'Four repositories')
            for repo, commit in SOURCES.items():
                matches = [r for r in tuples if r['repository'] == 'night-outlook/'+repo]
                require(len(matches) == 1 and matches[0]['commit'] == commit and matches[0]['remoteHeadVerified'] is True
                        and matches[0]['branch'] == 'codex/assembly-shadow-r01b-h1', 'Executed source pairing')
        result['cells'] = {'Passed': 37, 'Failed': 0, 'Blocked': 0}
        command_paths = sorted((batch/'commands').glob('*/command.json'))
        commands = [load(p) for p in command_paths]
        require(len(commands) == 83, 'Original command count')
        for receipt, command in zip(command_paths, commands):
            require(command['schemaVersion'] == 2 and command['lifetimePolicy'] == 'R03OwnedCommandV1', 'Original lifetime schema')
            require(command['exitCode'] in (0, 1) and command['timeout'] is False and command['remainingProcessGroup'] is False
                    and command['postCleanupGroupExists'] is False and command['startError'] is None
                    and command['cleanupErrors'] == [] and command['interrupted'] is False, 'Original command failure')
            for stream in ('stdout', 'stderr'):
                require(digest(receipt.parent/(stream+'.log')) == command[stream+'Sha256'], 'Command stream binding')
        require([p.parent.name for p,c in zip(command_paths,commands) if c['exitCode'] == 1] == ['0048','0050','0055'], 'Named negative controls')
        result['commandExitCounts'] = dict(collections.Counter(str(c['exitCode']) for c in commands))
        require(result['commandExitCounts'] == {'0': 80, '1': 3}, 'Expected negative command count')
        result['ownedCommandLifetimeAndStreamsAuthenticated'] = 83
        # Reuse the source-bound original verifier, never launch its Batch/Player methods.
        sys.path.insert(0, str(source))
        from batch_contract import verify_raw
        from editor_scope import verify_editor
        matrix = load(source/'player-cases.json')
        require(summary['matrixSha256'] == digest(source/'player-cases.json'), 'Executed expected matrix')
        expected = list(matrix['cases'])
        paired = ('C03-moved-slot', 'C04-old-AOT-guard', 'C05-direction-reversal', 'C07-private-primitive-append')
        expected += [dict(next(c for c in expected if c['id'] == name), id='PC-'+name, producerControl=True) for name in paired]
        results = []; pids = set(); run_ids = set()
        for case in expected:
            root = batch/'players'/case['id']; req = load(root/'request.json'); raw = load(root/'raw.json'); stored = load(root/'verification.json')
            launches = [c for c in commands if '-r03RunId' in c['command'] and req['runId'] in c['command']]
            require(len(launches) == 1, 'Unique original launch receipt')
            pid = launches[0]['pid']; require(pid not in pids and req['runId'] not in run_ids, 'Unique Player process/nonce')
            pids.add(pid); run_ids.add(req['runId'])
            replay = verify_raw(req, raw, case, digest(root/'request.json'), pid)
            replay.update(rawSha256=digest(root/'raw.json'), requestSha256=digest(root/'request.json'),
                          buildReceiptSha256=digest(batch/'builds'/case['role']/'build-receipt.json'),
                          launchPid=pid, runId=req['runId'], result='Passed')
            require(replay == stored, 'Original verifier replay differs: '+case['id'])
            results.append(dict(id=case['id'], **replay))
        require(len(results) == 23, '23 Player contracts')
        result['playerContractReplay'] = results
        result['rejectionSubchecks'] = sum('rejectionObservation' in r for r in results)
        result['isolatedWarmSubchecks'] = sum('warmWindow' in r and not r['id'].startswith('PC-') for r in results)
        controls = load(batch/'producer-controls.json')
        require(controls['result'] == 'Passed' and controls['identifiedLoopAdmissions'] == 4, 'Four identified producer controls')
        for row in controls['cases']:
            actual_verdict = next({k:v for k,v in r.items() if k != 'id'} for r in results if r['id'] == row['id'])
            require(row['result'] == 'Passed' and row['evidence'] == actual_verdict, 'Control receipt equality')
            require(row['evidence']['warmWindow']['unisolatedWarmCertificate'] == 'Failed', 'Contaminated control certificate')
        result['controlDiagnosticPassed'] = 4; result['unisolatedWarmCertificatesFailed'] = 4
        scope = load(batch/'editor-scope.json')
        result['editorReplay'] = verify_editor(ET.parse(batch/'editor-results.xml').getroot(), scope)
        require(result['rejectionSubchecks'] == 5 and result['isolatedWarmSubchecks'] == 6, 'Focused subcheck counts')
        result['localCustodyClaim'] = {'earlierBindings':9000, 'attribution':'Local report; prior macOS live roots not accessible to Primary'}
        require(digest(manifest) == before_manifest and not git(pub, 'status', '--porcelain'), 'Published evidence mutated')
        result['publishedCheckoutUnchanged'] = True
        result['result'] = 'Passed'
    finally:
        (output/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('playerContractReplay','editorReplay')}, indent=2))


if __name__ == '__main__':
    main()
