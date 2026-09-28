"""Compile the actual native extension writer and link the actual package parser."""
from pathlib import Path
import argparse
import json
import os
import shutil
from evidence import binding, read, require, run, write


def execute(native, package, output, dotnet='dotnet'):
    here = Path(__file__).resolve().parent
    source = here / 'TypeResolutionContract'
    require(not output.exists(), 'Unused contract output required')
    output.mkdir(parents=True)
    fixtures = output / 'fixtures'; fixtures.mkdir()
    env = dict(os.environ, DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER='1',
               MSBUILDDISABLENODEREUSE='1', DOTNET_CLI_USE_MSBUILD_SERVER='0')
    rows = []
    def command(label, args):
        result = run([str(a) for a in args], here.parents[2], output / label, 300, env)
        rows.append(dict(label=label, receipt=binding(output / label / 'command.json')))
        require(result['result'] == 'Passed', 'Contract command failed: ' + label)
        return output / label / 'stdout.log'
    parser = package / 'Runtime/AssemblyShadow/AssemblyShadowTypeResolutionInfo.cs'
    report = dict(kind='R02TypeResolutionContractRun', result='Failed', commands=rows,
                  parser=binding(parser), writer=binding(native / 'libil2cpp/vm/AssemblyShadowR02Diagnostics.h'),
                  runtimeAcceptance=False, unityPlayerRun=False)
    try:
        compiler = shutil.which('c++'); require(compiler is not None, 'Host C++ compiler required')
        for level in range(3):
            binary = output / ('writer-' + str(level))
            command('compile-' + str(level), [compiler, '-std=c++11', '-pthread', '-I', native / 'libil2cpp/vm',
                '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=' + str(level), source / 'writer.cpp', '-o', binary])
            for mode in ('normal', 'saturated', 'truncated', 'classes') + (('legacy',) if level == 0 else ()):
                label = str(level) + '-' + mode
                stdout = command('emit-' + label, [binary, mode])
                raw = read(stdout)
                target = fixtures / ('legacy.json' if mode == 'legacy' else label + '.json')
                write(target, raw)
        csproj = source / 'Contract.csproj'
        command('managed-build', [dotnet, 'build', csproj, '--disable-build-servers', '-p:UseSharedCompilation=false',
            '-nodeReuse:false', '-p:ParserSource=' + str(parser), '-p:BaseIntermediateOutputPath=' + str(output / 'obj') + '/',
            '-o', output / 'bin', '--nologo'])
        stdout = command('managed-run', [dotnet, 'exec', output / 'bin/Contract.dll', fixtures])
        result = read(stdout)
        require(result.get('kind') == 'R02ProducerParserContract' and result.get('result') == 'Passed' and
                result.get('nativeFixtures') == 12 and result.get('legacyFixtures') == 1 and result.get('checks', 0) > 1000,
                'Incomplete cross-language contract result')
        report['assertions'] = result
        report['result'] = 'Passed'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    write(output / 'results.json', report)
    require(report['result'] == 'Passed', report.get('error', 'Contract failed'))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-root', required=True, type=Path)
    p.add_argument('--package-root', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--dotnet', default='dotnet')
    a = p.parse_args()
    execute(a.runtime_root, a.package_root, a.output, a.dotnet)
