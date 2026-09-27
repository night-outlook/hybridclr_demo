"""Authenticate generated inputs for the build-dependent R01 transaction probe."""
from pathlib import Path
import re
from evidence import binding, check_binding, read, require, write

VERSION = {'HYBRIDCLR_UNITY_VERSION': '20220362', 'HYBRIDCLR_UNITY_2022': '1',
           'HYBRIDCLR_UNITY_2019_OR_NEW': '1', 'HYBRIDCLR_UNITY_2020_OR_NEW': '1',
           'HYBRIDCLR_UNITY_2021_OR_NEW': '1', 'HYBRIDCLR_UNITY_2022_OR_NEW': '1'}


def check_version(text):
    pairs = re.findall(r'^\s*#define\s+(HYBRIDCLR_UNITY_\w+)\s+(\d+)\s*$', text, re.M)
    require(len(pairs) == len(dict(pairs)) and dict(pairs) == VERSION,
            'Generated Unity version is not exactly the pinned 2022.3.62f2 profile')


def prepare(project, graph_path, unity, output):
    result = {'kind': 'R02NativeGeneratedPrerequisite', 'result': 'Failed',
              'runtimeAcceptance': False, 'files': {}}
    try:
        frozen = read(graph_path)
        check_binding(frozen['workflow'])
        graph = frozen['graph']
        require(read(Path(frozen['workflow']['path'])) == graph and graph['result'] == 'Passed' and
                graph['projectPath'] == str(project) and graph['controlledPerformanceBuilds'] is True,
                'Current candidate controlled graph is required')
        result['graph'] = binding(graph_path)
        installed = project / 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp'
        paths = {'pins': project / 'ProjectSettings/AssemblyShadowSourcePins.json',
                 'install': installed / 'assembly-shadow-install.json',
                 'version': installed / 'hybridclr/generated/UnityVersion.h',
                 'fixture': Path(graph['resourceBaselinePath']) / 'CompilerInputs/Assemblies/AssemblyA.Contracts.dll',
                 'baselib': unity.parent.parent / 'PlaybackEngines/MacStandaloneSupport/baselib.a'}
        for key, path in paths.items():
            # Keep successfully observed bindings even if a later input fails.
            result['files'][key] = binding(path)
        check_version(paths['version'].read_text())
        pins = read(paths['pins']); install = read(paths['install'])
        require(pins['unityVersion'] == '2022.3.62f2' and pins['target'] == 'StandaloneOSX' and
                pins['architecture'] == 'arm64' and install['installMode'] == 'PinnedLocal',
                'Wrong transaction target/install mode')
        for key in ('demo', 'hybridclr', 'hybridclrUnity', 'il2cppPlus'):
            require(install['repositories'][key] == pins[key], 'Stale installed source pin: ' + key)
        result['installedRoot'] = str(installed)
        result['result'] = 'Passed'
        return result
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(output, result)


def recheck(receipt):
    require(receipt['result'] == 'Passed', 'Native generated prerequisites did not pass')
    check_binding(receipt['graph'])
    for item in receipt['files'].values():
        check_binding(item)
