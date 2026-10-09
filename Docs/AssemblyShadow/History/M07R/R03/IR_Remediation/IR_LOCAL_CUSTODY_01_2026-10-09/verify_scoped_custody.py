#!/usr/bin/env python3
"""Read-only, exact-loss custody admission for the separate R03 IR focused run.

This is NOT restoration, historical-custody PASS, S acceptance, or a replacement
for a normal source/fixture/storage/Player prerequisite. All original objects
are read-only. The baseline is frozen at the C CustodyBlocked publication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from datetime import datetime, timezone

S_ROOT = '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery'
C_ROOT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked'
MAP_SHA256 = '133cba8a9b54b74a9909c6da6948838f8f604afea47bc61bdee88f45c22df0e8'
MAP_BYTES = 127296143
EXPECTED_FILES = 416844
EXPECTED_MISSING = 77477
C_BLOBS = {
    'HISTORICAL_CUSTODY_BEFORE.json': 'b44e3c3ae6abc0e79d222c459c5463a6fd0fa186996f1dd2b7ac85a8963df2fe',
    'HISTORICAL_CUSTODY_AFTER.json': '86a5e926841b50e3edb337c4a0a22bd3a6a6dd1484ad40d2f926c0c72161603b',
    'CUSTODY_FAILURE_ANALYSIS.json': '5e4476b8487e06ec98d2152e94c7e4e671b4f7ece42b5c78544553be2d4e178c',
    'NATIVE_LIVE_CUSTODY_LIMIT.json': '5cf6365c3e84e5390868984b52b40534de0fa53b92499d0359f9d',
    'CUSTODY_MAP_BINDING.json': '3f2a6621879747a821acfcdfa01eff2641b551e534fed9ae6e55a798b3e2aec5',
}
PARTS = (
    (33554432, '17b1b27364bc29fca2f1c60c554054778395be861791eeb6092abbf724272a0a'),
    (33554432, '97efad615515e4f5d9000b7ad63ad81d5253dfa881d794ee83ca6568a18924a3'),
    (33554432, 'a9659bada4d91b766d35cd9fa1f01f384605bbba4518c1e162eeb54d3bd62eaf'),
    (26632847, '10b21ceb108602703984da0e351cb5af1bc2465294c6882b0861a79ab68c9ed4'),
)
NATIVE_ROLES = ('candidate-debug', 'candidate-off', 'candidate-release', 'reference-release')
ALLOWED_GROUPS = {
    'reference-release/Library': 3598,
    'reference-release/HybridCLRData': 10402,
    'fixture-constructor-editor/Library': 2581,
    'resource-complete/Library': 18364,
    'candidate-release/Library': 3815,
    'candidate-release/HybridCLRData': 10414,
    'candidate-debug/Library': 3598,
    'candidate-debug/HybridCLRData': 10414,
    'compiler-probe-invalid-key/Library': 134,
    'compiler-probe-valid/Library': 145,
    'candidate-off/Library': 3598,
    'candidate-off/HybridCLRData': 10414,
}
SHA_RE = re.compile(r'[0-9a-f]{64}\Z')


class AdmissionError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise AdmissionError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def authenticated_json(path, expected_sha):
    data = path.read_bytes()
    require(digest(data) == expected_sha, 'Immutable C file SHA mismatch: ' + str(path))
    return json.loads(data)


def error_pairs(report):
    require(isinstance(report, dict) and isinstance(report.get('errors'), list),
            'Custody audit must contain the complete raw errors array')
    pairs = {}
    for row in report['errors']:
        require(isinstance(row, dict) and set(row) == {'path', 'expectedSha256', 'error'},
                'Unexpected custody error schema')
        p, expected = row['path'], row['expectedSha256']
        require(isinstance(p, str) and os.path.isabs(p) and isinstance(expected, str) and
                SHA_RE.fullmatch(expected) is not None, 'Malformed missing-path identity')
        require(p not in pairs, 'Duplicate missing-path identity: ' + p)
        require('[Errno 2]' in row['error'] and p in row['error'],
                'Missing-file error was not ENOENT for ' + p)
        pairs[p] = expected
    return pairs


def classify_missing(pairs):
    groups = {}
    prefix = S_ROOT + '/projects/'
    for p in pairs:
        require(p.startswith(prefix), 'Missing path outside retained S projects: ' + p)
        parts = p[len(prefix):].split('/')
        require(len(parts) >= 3, 'Unexpected missing path depth: ' + p)
        group = parts[0] + '/' + parts[1]
        require(group in ALLOWED_GROUPS, 'Unapproved missing S group: ' + group)
        groups[group] = groups.get(group, 0) + 1
    require(groups == ALLOWED_GROUPS, 'Missing S group census differs from frozen C')


def load_frozen_c(checkpoint):
    cp = Path(checkpoint)
    require(cp.is_dir() and cp.name == C_ROOT.split('/')[-1],
            'Expected immutable C custody checkpoint directory')
    pre = cp / 'preflight'
    before = authenticated_json(pre / 'HISTORICAL_CUSTODY_BEFORE.json',
                                C_BLOBS['HISTORICAL_CUSTODY_BEFORE.json'])
    after = authenticated_json(pre / 'HISTORICAL_CUSTODY_AFTER.json',
                               C_BLOBS['HISTORICAL_CUSTODY_AFTER.json'])
    analysis = authenticated_json(pre / 'CUSTODY_FAILURE_ANALYSIS.json',
                                  C_BLOBS['CUSTODY_FAILURE_ANALYSIS.json'])
    native = authenticated_json(pre / 'NATIVE_LIVE_CUSTODY_LIMIT.json',
                                C_BLOBS['NATIVE_LIVE_CUSTODY_LIMIT.json'])
    binding = authenticated_json(pre / 'CUSTODY_MAP_BINDING.json',
                                 C_BLOBS['CUSTODY_MAP_BINDING.json'])
    for phase, report in (('before', before), ('after', after)):
        require(report['phase'] == phase and report['state'] == 'Blocked' and
                report['files'] == EXPECTED_FILES and report['symlinks'] == 0 and
                report['mapSha256'] == MAP_SHA256 and
                report['historicalStatesReclassified'] is False and
                report['historicalRootsModified'] is False,
                'C audit invariants failed: ' + phase)
        r = report['retainedR']
        require(r['result'] == 'Passed' and r['filesVerified'] == 6 and
                r['settingsRemainStaged'] is True and r['originalRestoreCell'] == 'Failed',
                'Historical retained R facts changed in C')
    frozen = error_pairs(before)
    require(len(frozen) == EXPECTED_MISSING and frozen == error_pairs(after),
            'C before/after missing path identities disagree')
    classify_missing(frozen)
    require(analysis['state'] == 'CustodyBlocked' and
            analysis['expectedFiles'] == EXPECTED_FILES and
            analysis['presentFilesVerified'] == EXPECTED_FILES - EXPECTED_MISSING and
            analysis['missingFiles'] == EXPECTED_MISSING and
            analysis['changedFiles'] == 0 and
            analysis['missingByScope'] == {'projects/' + k: v for k, v in ALLOWED_GROUPS.items()} and
            analysis['indexAndArchiveMissingIntersection'] == 0 and
            analysis['sealedS']['indexedFiles'] == 15712 and
            analysis['sealedS']['archiveBytes'] == 587907380 and
            analysis['sealedS']['archiveMembers'] == 15713 and
            analysis['sealedS']['topArtifactHashes']['evidence.tar.gz'] ==
              '23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6',
            'C original sealed/unsealed classification changed')
    receipts = native.get('receipts')
    require(native.get('state') == 'LiveRetainedNativeRootsMissing' and
            isinstance(receipts, list) and len(receipts) == 4 and
            {r['role'] for r in receipts} == set(NATIVE_ROLES),
            'C four-native-root limit changed')
    for r in receipts:
        require(r['schemaVersion'] == 2 and r['liveState'] == 'Missing' and
                r['historicalReceiptModified'] is False and
                r['installedNativeRoot'] ==
                  S_ROOT + '/projects/' + r['role'] +
                  '/HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp' and
                SHA_RE.fullmatch(r['receiptSha256']) is not None,
                'C native receipt/source limit cannot be authenticated')
    require(binding['sha256'] == MAP_SHA256 and binding['uniqueFiles'] == EXPECTED_FILES,
            'C prior map binding changed')
    data = bytearray()
    for i, (size, expected_sha) in enumerate(PARTS):
        path = pre / ('prior-evidence-custody.json.part%03d' % i)
        part = path.read_bytes()
        require(len(part) == size and digest(part) == expected_sha,
                'C prior-map transport part differs: ' + str(i))
        data.extend(part)
    require(len(data) == MAP_BYTES and digest(data) == MAP_SHA256,
            'C original full custody map differs')
    original = json.loads(data)
    del data
    require(isinstance(original, dict) and len(original) == EXPECTED_FILES,
            'Original frozen custody roster count changed')
    for path, sha in original.items():
        require(isinstance(path, str) and os.path.isabs(path) and
                isinstance(sha, str) and SHA_RE.fullmatch(sha) is not None,
                'Invalid frozen path or SHA')
    for path, sha in frozen.items():
        require(original.get(path) == sha, 'C missing SHA not in original immutable map')
    return original, frozen


def audit_exact(original, frozen):
    """Independently hash every surviving path; require exact C missing set.

    Does not write, rebaseline, restore or regenerate protected paths.
    """
    verified = 0
    missing = 0
    problems = []
    parents_seen = set()
    for path, expected in original.items():
        try:
            p = Path(path)
            parent = p.parent
            while str(parent) not in parents_seen:
                require(not parent.is_symlink(), 'Symlink parent in protected inventory: ' + str(parent))
                parents_seen.add(str(parent))
                if parent == parent.parent:
                    break
                parent = parent.parent
            try:
                mode = os.lstat(path).st_mode
            except FileNotFoundError:
                if path in frozen and frozen[path] == expected:
                    missing += 1
                else:
                    problems.append({'path': path, 'kind': 'NewMissing'})
                continue
            if path in frozen:
                problems.append({'path': path, 'kind': 'UnexpectedRestorationNeedsPrimaryReview'})
            elif not stat.S_ISREG(mode):
                problems.append({'path': path, 'kind': 'NotRegularFile'})
            elif digest_file(path) != expected:
                problems.append({'path': path, 'kind': 'ChangedBytes'})
            else:
                verified += 1
        except (OSError, AdmissionError) as error:
            problems.append({'path': path, 'kind': type(error).__name__, 'detail': str(error)[:300]})
        if len(problems) >= 50:
            break
    ok = (not problems and missing == len(frozen) and
          verified == len(original) - len(frozen))
    return {'result': 'ScopedHistoricalLossStable' if ok else 'Blocked',
            'originalStrictCustody': 'Blocked', 'originalExpectedFiles': len(original),
            'presentVerified': verified, 'historicalStillMissing': missing,
            'frozenCAllowedMissing': len(frozen), 'problems': problems[:50],
            'completeScan': ok}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', required=True)
    p.add_argument('--phase', choices=('before', 'after'), required=True)
    p.add_argument('--receipt', required=True)
    args = p.parse_args(argv)
    receipt = Path(args.receipt)
    require(not receipt.exists() and receipt.parent.is_dir() and not receipt.is_symlink(),
            'Unused external receipt path required')
    begin = datetime.now(timezone.utc).isoformat()
    try:
        original, frozen = load_frozen_c(args.checkpoint)
        result = audit_exact(original, frozen)
        result['cSourceCheckpoint'] = C_ROOT
        result['cFrozenMapSha256'] = MAP_SHA256
        result['phase'] = args.phase
        result['kind'] = 'R03IRScopedHistoricalCustodyV1'
        result['strictFullHistoricalCustodyAccepted'] = False
        result['sourceBuildProcessProvenanceRestored'] = False
        result['freshUnityRun'] = False
        result['runtimeAcceptance'] = False
        result['startedUtc'] = begin
        result['completedUtc'] = datetime.now(timezone.utc).isoformat()
        with receipt.open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write('\n')
        print(json.dumps({k: result[k] for k in ('result', 'phase', 'presentVerified',
                                                  'historicalStillMissing', 'originalStrictCustody')}))
        return 0 if result['result'] == 'ScopedHistoricalLossStable' else 2
    except (OSError, ValueError, KeyError, AdmissionError) as error:
        blocked = {'kind': 'R03IRScopedHistoricalCustodyV1', 'result': 'Blocked',
                   'phase': args.phase, 'originalStrictCustody': 'Blocked',
                   'error': str(error)[:1200], 'startedUtc': begin,
                   'completedUtc': datetime.now(timezone.utc).isoformat(),
                   'runtimeAcceptance': False, 'freshUnityRun': False}
        with receipt.open('x', encoding='utf-8') as f:
            json.dump(blocked, f, indent=2, sort_keys=True)
            f.write('\n')
        print(json.dumps(blocked), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
