"""Fixture consumer validity and Unity compiler lifecycle subchecks for R03 C.

Added inside player-fixtures, without dropping any of the original 36 cells.
.NET host consumption is distinct from the pinned Unity compiler/Editor probes.
"""
from pathlib import Path
import re
import shutil
from batch_contract import loads, require, sha
from batch_evidence import write
from command_lifetime import build_arguments
from unity_command import clean_outer, unity_command

HERE = Path(__file__).resolve().parent


def metadata_audit(batch):
    binary, intermediate = batch.root / 'bin/fixture-audit', batch.root / 'obj/fixture-audit'
    batch.command(build_arguments(HERE / 'FixtureAudit/FixtureAudit.csproj', binary, intermediate, batch.workspace / 'hybridclr_unity'))
    root = batch.root / 'fixture-audit'
    batch.command(['dotnet', binary / 'FixtureAudit.dll', '--player', batch.fixture_root, '--output', root])
    report = loads((root / 'results.json').read_text())
    require(report['kind'] == 'R03FixtureMetadataAudit' and report['result'] == 'Passed' and
            len(report['cases']) == 33 and len({c['id'] for c in report['cases']}) == 33,
            'All 15 Player and 18 shared inputs must be audited')
    for case in report['cases']:
        require(sha(Path(case['input'])) == case['inputSha256'] and sha(Path(case['source'])) == case['sourceSha256'], 'Audit input/source binding')
        for peer in case['peers']:
            require(sha(Path(peer['path'])) == peer['sha256'], 'Peer binding')
        for reference in case['references']:
            require(reference['flags'] & 1 == 0 and reference['keyBytes'] == (8 if reference['name'] == 'mscorlib' else 0), 'Invalid fixture key flag/token')
    require(sha(Path(report['negative']['input'])) == report['negative']['inputSha256'], 'Negative control binding')
    return root, report


def binding(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), 'Missing toolchain file: ' + str(path))
    return {'path': str(path), 'sha256': sha(path), 'size': path.stat().st_size}


def sdk_toolchain(batch):
    batch.command(['dotnet', '--list-sdks'])
    log = batch.root / 'commands' / ('%04d' % batch.command_count) / 'stdout.log'
    found = re.findall(r'^8\.0\.318 \[(.+)\]$', log.read_text(), re.MULTILINE)
    require(len(found) == 1, 'SDK 8.0.318 must be installed exactly once')
    sdk = Path(found[0]) / '8.0.318'
    packs = list((sdk.parent.parent / 'packs/Microsoft.NETCore.App.Ref').glob('8.0.*/ref/net8.0'))
    packs = [p for p in packs if re.fullmatch(r'8\.0\.\d+', p.parents[1].name)]
    require(packs, 'net8 reference pack required')
    refs = max(packs, key=lambda p: tuple(map(int, p.parents[1].name.split('.'))))
    return Path(shutil.which('dotnet')).resolve(), sdk / 'Roslyn/bincore/csc.dll', sorted(refs.glob('*.dll'))


def unity_toolchain(unity):
    contents = Path(unity).parent.parent
    return (contents / 'NetCoreRuntime/dotnet', contents / 'DotNetSdkRoslyn/csc.dll',
            [contents / 'NetStandard/ref/2.1.0/netstandard.dll', contents / 'NetStandard/compat/2.1.0/shims/netfx/mscorlib.dll'])


def compiler_args(runtime, compiler, refs, source, target, subject, peers):
    return [str(runtime), 'exec', str(compiler), '/noconfig', '/nostdlib+', '/nologo', '/target:library', '/langversion:9.0',
            '/preferreduilang:en-US', '/out:' + str(target), *['/reference:' + str(p) for p in refs],
            '/reference:Subject=' + str(subject), *['/reference:Dependency%d=%s' % (i, p) for i, p in enumerate(peers)], str(source)]


def verify_negative(row, output, target):
    clean_outer(row, 1)
    require('CS0009' in output and 'invalid public key' in output.lower() and not Path(target).exists(),
            'Exact invalid-key diagnostic required; arbitrary errors do not pass')


def consumers(batch, audit_root, report, toolchain, label):
    runtime, compiler, refs = toolchain
    require(refs and all(Path(p).is_file() for p in (runtime, compiler, *refs)), 'Compiler and reference profile must exist')
    root = batch.root / ('consumer-' + label); root.mkdir()
    tools = [binding(p) for p in (runtime, compiler, *refs)]
    cases = []
    for case in report['cases']:
        folder = root / case['id']; folder.mkdir()
        target = folder / 'Consumer.dll'
        args = compiler_args(runtime, compiler, refs, Path(case['source']), target, Path(case['input']), [Path(p['path']) for p in case['peers']])
        receipt = batch.command(args)
        require(target.is_file() and target.stat().st_size > 0, 'Compiler must emit actual consumer bytes')
        require(sha(Path(case['input'])) == case['inputSha256'] and sha(Path(case['source'])) == case['sourceSha256'], 'Consumed bytes changed')
        cases.append({'id': case['id'], 'result': 'Passed', 'inputSha256': case['inputSha256'],
                      'consumer': binding(target), 'commandReceipt': str(batch.root / 'commands' / ('%04d' % batch.command_count) / 'command.json')})
    # Deliberate malformed control is outside the accepted fixture inventory.
    negative = root / 'negative'; negative.mkdir()
    source = negative / 'Consumer.cs'; source.write_text('extern alias Subject; public class Consumer { public Subject::R03.Node Value; }\n')
    args = compiler_args(runtime, compiler, refs, source, negative / 'Consumer.dll', Path(report['negative']['input']), [Path(report['negative']['peer'])])
    try:
        batch.command(args)
    except RuntimeError:
        pass
    folder = batch.root / 'commands' / ('%04d' % batch.command_count)
    row = loads((folder / 'command.json').read_text())
    output = (folder / 'stdout.log').read_text() + (folder / 'stderr.log').read_text()
    verify_negative(row, output, negative / 'Consumer.dll')
    require(tools == [binding(p) for p in (runtime, compiler, *refs)], 'Compiler/reference files changed')
    result = {'kind': 'R03FixtureConsumerEvidence', 'schemaVersion': 1, 'result': 'Passed', 'toolchainLabel': label,
              'toolchain': tools, 'metadataAuditSha256': sha(audit_root / 'results.json'), 'cases': cases,
              'negative': {'result': 'ExpectedCS0009', 'commandReceipt': str(folder / 'command.json'), 'receiptSha256': sha(folder / 'command.json')},
              'unityEditorRun': False, 'nativeExecution': False, 'runtimeAcceptance': False}
    write(root / 'results.json', result)
    return {'result': str(root / 'results.json'), 'sha256': sha(root / 'results.json')}


def unity_probes(batch, audit_root):
    """Actual Editor compile-success/failure coverage; no fake engine or native claim."""
    root = batch.root / 'unity-lifecycle'; root.mkdir()
    rows = []
    for negative in (False, True):
        role = 'invalid-key' if negative else 'valid'
        project = batch.root / 'projects' / ('compiler-probe-' + role)
        for part in ('Assets/Editor', 'Assets/Fixtures', 'Packages', 'ProjectSettings'):
            (project / part).mkdir(parents=True, exist_ok=True)
        (project / '.r03-isolated-project').write_text('Compiler lifecycle probe only.\n')
        write(project / 'Packages/manifest.json', {'dependencies': {}})
        (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2022.3.62f2\n')
        a = audit_root / 'invalid-key/A.dll' if negative else batch.fixture_root / 'baseline/A.dll'
        for name, origin in [('A', a), ('B', batch.fixture_root / 'baseline/B.dll')]:
            shutil.copyfile(origin, project / ('Assets/Fixtures/' + name + '.dll'))
        (project / 'Assets/Editor/R03CompilerProbe.cs').write_text(r'''
using System;
using System.IO;
public static class R03CompilerProbe {
 public static void Run() {
  var args = Environment.GetCommandLineArgs();
  int i = Array.IndexOf(args, "-r03CompilerMarker");
  if (i < 0 || i + 1 >= args.Length) throw new InvalidOperationException("Marker required");
  using (var stream = new FileStream(args[i + 1], FileMode.CreateNew)) {
   var bytes = System.Text.Encoding.UTF8.GetBytes("R03CompilerProbe-v1");
   stream.Write(bytes, 0, bytes.Length);
  }
 }
}
''')
        log, marker = root / (role + '.log'), root / (role + '.marker')
        cmd = [batch.unity, '-batchmode', '-nographics', '-quit', '-buildTarget', 'osx', '-projectPath', project,
               '-executeMethod', 'R03CompilerProbe.Run', '-r03CompilerMarker', marker, '-logFile', log]
        receipt = unity_command(batch, cmd, 7200, expected_exit=1 if negative else 0)
        text = log.read_text(errors='replace')
        if negative:
            require('CS0009' in text and 'invalid public key' in text.lower() and not marker.exists(), 'Deliberate Unity compiler failure must precede executeMethod')
        else:
            require(marker.is_file() and marker.read_text() == 'R03CompilerProbe-v1' and 'error CS' not in text, 'Actual successful Editor compiler probe required')
        rows.append({'id': role, 'expectation': 'CS0009' if negative else 'CompiledAndInvoked', 'result': 'Passed',
                     'receipt': receipt, 'logSha256': sha(log), 'aDllSha256': sha(project / 'Assets/Fixtures/A.dll')})
    write(root / 'results.json', {'kind': 'R03UnityCompilerLifecycle', 'schemaVersion': 1, 'result': 'Passed', 'cases': rows,
                                 'unityEditorRun': True, 'nativeExecution': False, 'runtimeAcceptance': False})
    return {'result': str(root / 'results.json'), 'sha256': sha(root / 'results.json')}


def validate_inputs(batch):
    generated = batch.fixtures()
    audit_root, report = metadata_audit(batch)
    consumed = consumers(batch, audit_root, report, unity_toolchain(batch.unity), 'unity-2022.3.62f2')
    lifecycle = unity_probes(batch, audit_root)
    from build_api import validate_build_api
    build_api = validate_build_api(batch)
    return {'fixtureInventory': generated, 'metadataAudit': str(audit_root / 'results.json'),
            'metadataAuditSha256': sha(audit_root / 'results.json'), 'compilerConsumers': consumed, 'unityLifecycle': lifecycle, 'completeBuildHelper': build_api}
