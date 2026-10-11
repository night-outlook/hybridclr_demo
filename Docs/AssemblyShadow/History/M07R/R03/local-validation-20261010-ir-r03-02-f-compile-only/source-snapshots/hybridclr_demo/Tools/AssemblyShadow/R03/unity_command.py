"""Unity invocation adapter: use the existing birth-authenticated R02 supervisor.

The supervisor completes its compiler children BEFORE the outer command returns.
run_owned_command itself remains unchanged and rejects every residual group.
"""
from pathlib import Path
import sys
from batch_contract import loads, require, sha

HERE = Path(__file__).resolve().parent
SUPERVISOR = HERE.parent / 'R02/unity_session.py'
SUPPORT = (SUPERVISOR, HERE.parent / 'R02/process_identity.py', HERE.parent / 'R02/evidence.py')


def clean_outer(row, exit_code):
    require(type(row.get('exitCode')) is int and row['exitCode'] == exit_code and
            row.get('schemaVersion') == 2 and row.get('lifetimePolicy') == 'R03OwnedCommandV1' and
            row.get('timeout') is False and row.get('remainingProcessGroup') is False and
            row.get('postCleanupGroupExists') is False and row.get('interrupted') is False and
            row.get('startError') is None and row.get('cleanupErrors') == [],
            'Command exit/lifetime failed; successful cleanup is not an acceptance override')


def supervised(batch, unity, command, timeout, *, expected_exit=0):
    """expected_exit=1 is only for a separate, explicit compiler-negative control."""
    require(expected_exit in (0, 1) and type(expected_exit) is int, 'Unsupported expectation')
    sources = {str(p): sha(p) for p in SUPPORT}
    command = [str(x) for x in command]
    folder = batch.root / 'commands' / ('%04d' % (batch.command_count + 1))
    completion = folder / 'unity-completion.json'
    wrapper = [sys.executable, str(SUPERVISOR), '--unity', str(unity), '--receipt', str(completion), '--', *command]
    try:
        batch.command(wrapper, timeout)
    except RuntimeError:
        if expected_exit == 0:
            raise
        # A deliberately failing compiler must still complete cleanly. Any
        # timeout, missing receipt, unknown child or failed census fails the test.
    row = loads((folder / 'command.json').read_text())
    clean_outer(row, expected_exit)
    require(row['command'] == wrapper, 'Wrong wrapper command')
    value = loads(completion.read_text())
    require(value.get('kind') == 'R02UnityCommandCompletion' and value.get('policy') == 'R02OwnedUnityRoslyn-v2', 'Unexpected supervisor receipt')
    require(value.get('command') == command and type(value.get('commandExitCode')) is int and value['commandExitCode'] == expected_exit,
            'Original compiler/Unity exit must be preserved')
    require(value.get('result') == ('Passed' if expected_exit == 0 else 'Failed') and
            value.get('completion', {}).get('clean') is True and 'error' not in value,
            'Owned compiler completion failed')
    compiler = Path(unity).parent.parent / 'DotNetSdkRoslyn/VBCSCompiler.dll'
    require(value['compilerBinding'] == {'path': str(compiler), 'sha256': sha(compiler), 'sizeBytes': compiler.stat().st_size}, 'Compiler binding mismatch')
    require(sources == {str(p): sha(p) for p in SUPPORT}, 'Supervisor source changed during invocation')
    return {'outerReceipt': str(folder / 'command.json'), 'outerSha256': sha(folder / 'command.json'),
            'completion': str(completion), 'completionSha256': sha(completion), 'supportSources': sources,
            'originalExitCode': expected_exit, 'clean': True}


def unity_command(batch, command, timeout, *, expected_exit=0):
    require(str(command[0]) == batch.unity and list(command).count('-projectPath') == 1, 'Exact supplied Unity command required')
    project = Path(command[list(command).index('-projectPath') + 1]).resolve()
    require(project.is_relative_to(batch.root) and (project / '.r03-isolated-project').is_file(), 'Only batch-owned isolated projects may run')
    return supervised(batch, Path(batch.unity), command, timeout, expected_exit=expected_exit)
