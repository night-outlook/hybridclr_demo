"""Source-bound frozen-image provisioning. Never import an ignored cache image.

The historical archive is an immutable INPUT authority, not reused runtime proof.
The actual current provider/mode still passes the unmodified Player ILPP/policy.
"""
import copy
import hashlib
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
for path in (HERE.parent / 'R03', HERE.parent, HERE.parent / 'R02'):
    if str(path) not in sys.path: sys.path.append(str(path))
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
import ordinary_input as ordinary
import export_m00_fixture as origin_export

PROFILE = 'R03FrozenFixedImageV1'
CONFIG = 'ProjectSettings/AssemblyShadowReflectionBindings.json'
CONFIG_SHA = '26837a5f710abae42a69a85ea2edf66939eff9afa6f6e8ce5b8e2cafc44f564a'
MATERIALIZATION = '_temp/AssemblyShadow/R03CompletionFixedImage'
FILES = {
    ordinary.FIXTURE: '9803eb472c0ef6eaf713a38a59d3fe07aa93830e',
    ordinary.ORIGIN: '245d7b56ffeccc16c897dfc8ef40bfb4f73fe098',
}
SITES = ['h1-count-ordinary-witness-image', 'm00-normal-hot-update-image']
MODES = {'Development': '7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369',
         'Release': 'e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022'}
CODES = {'F01-exact-image': 'Success', 'F02-missing-image': 'FixedImageEvidenceMissing',
         'F03-mutated-image': 'FixedImageHashMismatch', 'F04-provider-identity': 'FixedImageIdentityMismatch',
         'F05-development': 'Success', 'F06-release': 'Success',
         'F07-missing-mode': 'ProviderSemanticCompilerModeMissing', 'F08-unknown-mode': 'ProviderSemanticCompilerModeMissing',
         'F09-omitted-variant': 'InvalidProviderSemanticVariants', 'F10-image-path': 'InvalidFixedImage'}
INPUTS = [CONFIG, ordinary.IMAGE_PATH, ordinary.PINS, '.r03-completion-project',
          MATERIALIZATION + '/preparation.json', *FILES]
SOURCES = ['Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs',
           'Assets/AssemblyShadowDemo/Editor/R03CompletionFixedImageContract.cs']


def regular(path):
    path = Path(path)
    require(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)), 'Regular fixed-image path required: ' + str(path))
    return path


def source_contract(project):
    project = Path(project)
    for name, blob in FILES.items():
        data = regular(project / name).read_bytes()
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == blob,
                'Fixed input authority differs from reviewed Git blob: ' + name)
    require(sha(regular(project / CONFIG)) == CONFIG_SHA, 'Original six-site reflection contract changed')
    config = loads((project / CONFIG).read_text())
    fixed = [s for s in config['sites'] if s['kind'] == 'FixedAssemblyBytes']
    require(config['schemaVersion'] == 4 and config['transformerVersion'] == 4 and len(config['sites']) == 6 and
            sorted(s['id'] for s in fixed) == SITES, 'Complete fixed-image site audit')
    for site in fixed:
        require(site['imagePath'] == ordinary.IMAGE_PATH and site['imageSha256'] == ordinary.IMAGE_SHA256 and
                site['providerAssemblyIdentity'] == ordinary.PROVIDER and
                {v['compilerMode']: v['semanticHash'] for v in site['providerSemanticVariants']} == MODES,
                'Fixed-image path/hash/provider/compiler-mode contract')
    data, _, _, identity = ordinary.fixture(project)
    return {'profile': PROFILE, 'siteIds': SITES, 'imageSha256': ordinary.IMAGE_SHA256,
            'sizeBytes': len(data), 'identity': identity, 'configurationSha256': CONFIG_SHA,
            'classification': ordinary.CLASSIFICATION, 'runtimeAcceptance': False}


def provision(project):
    source_contract(project)
    # Exclusive materialization of the already-reviewed frozen input, not a DLL
    # build or permission to select a cache/ancestor/previous-batch file.
    return ordinary.prepare(project, project / MATERIALIZATION)


def verify_materialization(project):
    contract = source_contract(project)
    contract['materialization'] = ordinary.verify(project, project / MATERIALIZATION)
    return contract


def authenticate_origin(batch):
    demo = batch.workspace / 'hybridclr_demo'
    source_contract(demo)
    regular(demo / origin_export.ARCHIVE)
    output = batch.root / 'fixed-image-origin'
    command = batch.command([sys.executable, '-B', demo / 'Tools/AssemblyShadow/R02/export_m00_fixture.py',
                             '--project', demo, '--output', output, '--verify-committed'])
    proof = loads(regular(output / 'search.json').read_text())
    require(proof['result'] == 'FrozenFixtureOriginVerified' and proof['archive'] == origin_export.ARCHIVE and
            proof['archiveSha256'] == origin_export.ARCHIVE_SHA and proof['frozenSha256'] == ordinary.IMAGE_SHA256 and
            proof['historicalPlayerExecutionReused'] is False and proof['runtimeAcceptance'] is False,
            'Original immutable archive authority required')
    require(any(r['member'] == ordinary.MEMBER and r['sizeBytes'] == 4608 and r['sha256'] == ordinary.IMAGE_SHA256
                for r in proof['matches']), 'Exact original archive member missing')
    require(sha(regular(output / 'frozen-m00.dll')) == ordinary.IMAGE_SHA256, 'Archive and compact fixture differ')
    return {'command': command, 'receipt': str(output / 'search.json'), 'sha256': sha(output / 'search.json'),
            'classification': 'ImmutableHistoricalInputNotNewCompilation', 'historicalPlayerExecutionReused': False}


def host_contracts(batch):
    demo = batch.workspace / 'hybridclr_demo'
    project = batch.root / 'fixed-image-host-project'
    require(not project.exists(), 'Unused fixed-image host project')
    for name in (*FILES, CONFIG):
        target = project / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(regular(demo / name), target)
    write(project / ordinary.PINS, {'kind': 'HostOnlyFixedImageFixture', 'runtimeAcceptance': False})
    materialization = provision(project)
    binary = batch.root / 'bin/fixed-image'
    batch.command(build_arguments(HERE / 'FixedImageTests/FixedImageTests.csproj', binary,
                                   batch.root / 'obj/fixed-image', batch.workspace / 'hybridclr_unity'))
    output = batch.root / 'fixed-image-host'
    batch.command(['dotnet', binary / 'FixedImageTests.dll', '--project', project, '--output', output])
    report = loads(regular(output / 'results.json').read_text())
    require(report['kind'] == 'R03FixedImageHostContracts' and report['result'] == 'Passed' and
            report['unityEditorRun'] is False and report['pinnedMonoSemanticVerification'] is False,
            'Host checks are not pinned Mono/Unity semantic acceptance')
    verify_observation(report['observation'], output / 'controls', pinned_semantics=False)
    verify_materialization(project)
    return {'result': str(output / 'results.json'), 'sha256': sha(output / 'results.json'), 'cases': 10,
            'materialization': materialization, 'unityEditorRun': False, 'runtimeAcceptance': False}


def verify_observation(value, controls, *, pinned_semantics):
    require(value['profile'] == PROFILE and value['imageSha256'] == ordinary.IMAGE_SHA256 and value['sizeBytes'] == 4608 and
            value['providerIdentity'] == ordinary.PROVIDER and value['siteIds'] == SITES and
            value['mvid'] == 'e7f5b1ac-eca4-4034-8da4-69e25ca9fe3b' and value['classification'] == ordinary.CLASSIFICATION and
            all(value[k] is False for k in ('runtimeAcceptance', 'freshCscExecutionClaimed', 'historicalPlayerExecutionReused')),
            'Exact frozen image/claim/identity contract')
    if pinned_semantics:
        require(value['imageSemanticHash'] in MODES.values(), 'Pinned runtime must prove an original declared semantic variant')
    original = loads(regular(HERE.parents[2] / CONFIG).read_text())
    require(sha(HERE.parents[2] / CONFIG) == CONFIG_SHA, 'Verifier original configuration binding')
    original_image = ordinary.fixture(HERE.parents[2])[0]
    rows = value['cases']
    require([r['id'] for r in rows] == list(CODES), 'Exact ten fixed-image controls')
    for row in rows:
        require(row['expectedCode'] == row['observedCode'] == CODES[row['id']] and row['result'] == 'Passed', 'Exact guard code')
        path = regular(row['configurationPath'])
        require(path == controls / (row['id'] + '.json') and sha(path) == row['configurationSha256'], 'Bounded actual control config')
        config = loads(path.read_text())
        expected_config = copy.deepcopy(original)
        if row['id'] == 'F04-provider-identity':
            for site in expected_config['sites']:
                if site['kind'] == 'FixedAssemblyBytes':
                    site['providerAssemblyIdentity'] = 'Other, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'
        elif row['id'] == 'F09-omitted-variant':
            next(site for site in expected_config['sites'] if site['id'] == SITES[0])['providerSemanticVariants'] = \
                next(site for site in original['sites'] if site['id'] == SITES[0])['providerSemanticVariants'][:1]
        elif row['id'] == 'F10-image-path':
            next(site for site in expected_config['sites'] if site['id'] == SITES[0])['imagePath'] = '../outside.dll'
        require(config == expected_config, 'Control bytes differ from exact declared mutation')
        expected_operation = 'ValidateImageEvidence' if row['id'] in list(CODES)[:4] else \
            'ProviderSemanticHash' if row['id'] in list(CODES)[4:8] else 'Parse'
        expected_mode = {'F05-development': 'Development', 'F06-release': 'Release', 'F08-unknown-mode': 'Unknown'}.get(row['id'])
        require(row['operation'] == expected_operation and (row['mode'] or None) == expected_mode, 'Guard operation/mode substitution')
        require(bool(row['imagePath']) == (row['id'] in ('F01-exact-image','F03-mutated-image','F04-provider-identity')), 'Exact image presence control')
        if row['imagePath']:
            image = regular(row['imagePath'])
            require(image == controls / (row['id'] + '.dll.bytes') and sha(image) == row['imageSha256'], 'Actual image control bytes')
            if row['id'] == 'F03-mutated-image':
                require(image.read_bytes() == original_image[:-1] + bytes([original_image[-1] ^ 1]), 'Exact mutation control bytes')
            else: require(sha(image) == ordinary.IMAGE_SHA256, 'Positive/provider control uses exact frozen image')
        else: require(row['imageSha256'] in (None, ''), 'Absent image cannot claim a hash')
    expected_files = {label + '.json' for label in CODES} | {label + '.dll.bytes' for label in ('F01-exact-image','F03-mutated-image','F04-provider-identity')}
    require({p.name for p in controls.iterdir()} == expected_files, 'Exact control file inventory')
    for label, mode in (('F05-development', 'Development'), ('F06-release', 'Release')):
        row = next(r for r in rows if r['id'] == label)
        require(row['mode'] == mode and row['selectedSemanticHash'] == MODES[mode], 'Exact compiler-mode selection')
    return {'cases': 10, 'pinnedSemanticsVerified': pinned_semantics}


def verify_report(path, batch, project):
    config = batch.resource_config
    path = regular(path)
    require(path == Path(config['receiptRoot']) / 'fixed-image-contract.json', 'Exact actual fixed-image receipt')
    report = loads(path.read_text())
    require(report['kind'] == 'R03ActualFixedImageContract' and report['schemaVersion'] == 1 and report['result'] == 'Passed' and
            report['projectPath'] == str(project) and report['baselineId'] == config['baselineId'] and
            report['unityVersion'] == '2022.3.62f2' and report['target'] == 'StandaloneOSX' and report['architecture'] == 'arm64' and
            report['unityEditorRun'] is True and report['actualProjectImageValidator'] is True and
            all(report[k] is False for k in ('snapshotCompilationRun', 'runtimeAcceptance', 'expansionAuthorized', 'R03Accepted', 'H2Passed')),
            'Actual source-bound non-authorizing fixed-image consumer')
    expected = [{'path': name, 'sha256': sha(regular(project / name))} for name in INPUTS]
    require(report['before'] == report['after'] == expected, 'Original image/config/pins/authority changed during controls')
    require(report['sources'] == [{'path': name, 'sha256': sha(regular(project / name))} for name in SOURCES], 'Actual observer sources')
    verification = verify_observation(report['observation'], Path(config['receiptRoot']) / 'fixed-image-controls', pinned_semantics=True)
    verification.update(kind=report['kind'], result='Passed', receipt=str(path), sha256=sha(path),
                        materialization=verify_materialization(project), runtimeAcceptance=False)
    return verification
