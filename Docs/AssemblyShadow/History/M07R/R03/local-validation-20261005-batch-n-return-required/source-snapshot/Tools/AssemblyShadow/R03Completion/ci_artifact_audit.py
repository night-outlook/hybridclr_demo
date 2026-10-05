"""Read-only CI artifact authentication; never executes preserved artifact bytes."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import urllib.error
import urllib.request
import zipfile


def require(value, message):
    if not value:
        raise ValueError(message)


def decode_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(raw, expected, source, package):
    require(digest(raw) == expected, 'Archive digest')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        all_members = archive.infolist()
        all_names = [m.filename for m in all_members]
        require(len(all_names) == len(set(all_names)), 'Duplicate archive member')
        for member in all_members:
            path = PurePosixPath(member.filename)
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in member.filename and
                    str(path) == member.filename.rstrip('/'), 'Unsafe archive path')
            require(not stat.S_ISLNK(member.external_attr >> 16), 'Archive symlink')
        names = {m.filename for m in all_members if not m.is_dir()}
        require('provenance.json' in names, 'Missing provenance')
        provenance = decode_json(archive.read('provenance.json'))
        require(provenance['sourceCommit'] == source, 'Artifact source')
        require(provenance['repositories']['hybridclr_demo'] == source and
                provenance['repositories']['hybridclr_unity'] == package, 'Repository source tuple')
        rows = provenance['files']
        paths = [r['path'] for r in rows]
        require(len(paths) == len(set(paths)), 'Duplicate index entry')
        require(names == set(paths) | {'provenance.json'}, 'Exact index membership')
        for row in rows:
            data = archive.read(row['path'])
            require(type(row['size']) is int and len(data) == row['size'] and digest(data) == row['sha256'], 'Indexed bytes: ' + row['path'])
        result = {'sourceCommit': source, 'packageCommit': package, 'sha256': expected, 'bytes': len(raw),
                  'indexedFiles': len(rows), 'zipFiles': len(names), 'provenanceSha256': digest(archive.read('provenance.json')),
                  'commands': [], 'summaries': [], 'pythonSuites': [], 'warnings': 0, 'sourceFiles': {},
                  'basis': 'ReadOnlyArtifactAuthentication', 'unityRun': False, 'playerRun': False}
        for name in sorted(names):
            data = archive.read(name)
            if name.endswith('/command.json'):
                receipt = decode_json(data)
                require(receipt['exitCode'] == 0 and receipt['remainingProcessGroup'] is False and receipt['timeout'] is False and
                        receipt.get('postCleanupGroupExists') is False and not receipt.get('cleanupErrors') and not receipt.get('startError') and
                        receipt.get('interrupted') is False, 'Clean successful owned command: ' + name)
                parent = str(PurePosixPath(name).parent)
                for stream in ('stdout', 'stderr'):
                    value = archive.read(parent + '/' + stream + '.log')
                    require(digest(value) == receipt[stream + 'Sha256'], 'Command stream: ' + name)
                    text = value.decode('utf-8', errors='replace')
                    result['warnings'] += len(re.findall(r'\bwarning CS\d+:', text))
                    for count in re.findall(r'^Ran (\d+) tests? in ', text, re.M):
                        result['pythonSuites'].append({'command': name, 'count': int(count), 'stream': stream})
                result['commands'].append({'path': name, 'sha256': digest(data), 'exitCode': 0, 'remainingProcessGroup': False})
            if name.endswith('/results.json') or name in ('results.json', 'HOST_RESULT.json'):
                value = decode_json(data)
                require(value.get('result') not in ('Failed', 'ReturnRequired', 'Blocked'), 'Failed result: ' + name)
                if isinstance(value.get('cases'), list):
                    cases = value['cases']
                    ids = [r.get('id', r.get('name')) for r in cases]
                    require(len(ids) == len(set(ids)), 'Duplicate test ID: ' + name)
                    require(all(c.get('result') == 'Passed' for c in cases), 'Nonpassing test case: ' + name)
                    count = len(cases)
                else:
                    count = value.get('cases')
                result['summaries'].append({'path': name, 'sha256': digest(data), 'result': value.get('result'), 'caseCount': count})
            if name.startswith('sources/'):
                result['sourceFiles'][name] = digest(data)
        require(result['commands'], 'No owned command evidence')
        # Selected detailed reports are retained in the audit output, not executed.
        details = {}
        for name in names:
            if name.endswith(('comparison.json', 'replay.json', 'observation.json')) or name in ('results.json', 'BATCH_EXECUTION.json'):
                value = decode_json(archive.read(name))
                details[name] = value
        return result, details


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    root = Path(os.environ['RUNNER_TEMP']) / 'r03-lm-audit-final'
    root.mkdir()
    api = 'https://api.github.com/repos/night-outlook/hybridclr_demo'
    headers = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    path = 'Docs/AssemblyShadow/History/M07R/R03/P_ARTIFACT_AUDIT_INPUT.json'
    def get_json(url):
        return decode_json(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60).read())
    try:
        content = get_json(api + '/contents/' + path + '?ref=' + os.environ['GITHUB_SHA'])
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        print('No final audit request at this source; audit self-tests are run by host CI.')
        (root / 'NOT_REQUESTED.json').write_text(json.dumps({'result': 'NotRequested', 'workflowSource': os.environ['GITHUB_SHA']}) + '\n')
        return
    raw_input = base64.b64decode(content['content'])
    request = decode_json(raw_input)
    require(request['kind'] == 'R03LMFinalArtifactAudit' and request['schemaVersion'] == 1, 'Explicit audit request')
    source, package = request['sourceCommit'], request['packageCommit']
    require(re.fullmatch('[0-9a-f]{40}', source) and re.fullmatch('[0-9a-f]{40}', package), 'Exact pins')
    require(len(request['artifacts']) == 3 and len({x['artifactId'] for x in request['artifacts']}) == 3, 'Two hosts and one API artifact')
    output = {'kind': 'R03LMFinalArtifactAudit', 'result': 'Failed', 'requestSha256': digest(raw_input), 'workflowSource': os.environ['GITHUB_SHA'],
              'sourceCommit': source, 'packageCommit': package, 'artifacts': [], 'unityRun': False, 'playerRun': False}
    try:
        for spec in request['artifacts']:
            artifact = spec['artifactId']
            meta = get_json(api + '/actions/artifacts/' + str(artifact))
            require(meta['workflow_run']['head_sha'] == source and meta['digest'] == 'sha256:' + spec['sha256'] and not meta['expired'], 'GitHub immutable artifact metadata')
            try:
                urllib.request.build_opener(NoRedirect).open(urllib.request.Request(api + '/actions/artifacts/' + str(artifact) + '/zip', headers=headers), timeout=60)
            except urllib.error.HTTPError as error:
                require(error.code == 302, 'Artifact redirect'); url = error.headers['Location']
            else:
                raise ValueError('Missing signed artifact redirect')
            require(url.startswith('https://'), 'HTTPS blob')
            raw = urllib.request.urlopen(urllib.request.Request(url), timeout=180).read()
            require(len(raw) == meta['size_in_bytes'], 'GitHub artifact size')
            summary, details = authenticate(raw, spec['sha256'], source, package)
            expected = spec['requiredCaseCounts']
            by_path = {r['path']: r for r in summary['summaries']}
            for key, count in expected.items():
                require(key in by_path and by_path[key]['result'] == 'Passed' and by_path[key]['caseCount'] == count, 'Exact test count: ' + key)
            folder = root / str(artifact); folder.mkdir()
            (folder / 'artifact.zip').write_bytes(raw)
            for name, value in details.items():
                target = folder / 'details' / name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(value, indent=2) + '\n')
            summary['artifactId'] = artifact; summary['label'] = spec['label']
            (folder / 'audit.json').write_text(json.dumps(summary, indent=2) + '\n')
            output['artifacts'].append(summary)
            print('AUDIT_SUMMARY ' + json.dumps({k:v for k,v in summary.items() if k != 'sourceFiles'}))
            for name, value in details.items():
                if name.endswith('comparison.json'):
                    linked = value.get('linkedInventory', []); compiler = value.get('compilerInventory', [])
                    print('LAYOUT_SUMMARY ' + json.dumps({'path':name, 'rawAccepted':value.get('declared',{}).get('editorAccepted'),
                        'resolvedAccepted':value.get('resolved',{}).get('editorAccepted'), 'linkedImages':len(linked), 'compilerImages':len(compiler),
                        'mappedDeclarations':sum(r.get('runtimeFacadeUsed') is True for r in value.get('compilerResolutions',[])),
                        'types':len(value.get('resolved',{}).get('types',[]))}))
        output['result'] = 'Passed'
    finally:
        (root / 'summary.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
