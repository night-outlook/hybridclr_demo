#!/usr/bin/env python3
"""Host-only real Roslyn input/supervisor regression; never Unity engine evidence."""
import argparse
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from batch_contract import loads, require, sha
from batch_evidence import write
from input_validation import metadata_audit, consumers, sdk_toolchain, compiler_args
from unity_command import supervised
from run_local import Batch, git


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve(); require(not root.exists(), 'Unused host test root required'); root.mkdir()
    batch = object.__new__(Batch)
    batch.workspace, batch.root, batch.command_count = args.workspace.resolve(), root, 0
    batch.fixture_root = args.fixtures.resolve()
    result = {'kind': 'R03CompilerInputHostContracts', 'schemaVersion': 1, 'result': 'Failed',
              'platform': platform.platform(), 'architecture': platform.machine(),
              'demoCommit': git(batch.workspace / 'hybridclr_demo', 'rev-parse', 'HEAD'),
              'unityEditorRun': False, 'nativeExecution': False, 'runtimeAcceptance': False}
    sentinel = None
    try:
        audit_root, report = metadata_audit(batch)
        tools = sdk_toolchain(batch)
        result['consumerEvidence'] = consumers(batch, audit_root, report, tools, 'dotnet-sdk-8.0.318')
        # Unique, explicitly non-Unity layout for testing the existing pinned-
        # compiler supervisor against REAL Roslyn /shared, without an engine.
        # Copies (not links) ensure that no pre-existing compiler service is reused.
        contents = root / 'host-only-toolchain/Compiler Context.app/Contents'
        copied = contents / 'DotNetSdkRoslyn'
        shutil.copytree(tools[1].parent, copied)
        for path in tools[1].parent.iterdir():
            if path.is_file(): require(sha(path) == sha(copied / path.name), 'Copied compiler source identity')
        anchor = contents / 'MacOS/Unity'; anchor.parent.mkdir(); anchor.write_text('Host-only path anchor; NOT a Unity executable.\n')
        command_records = []
        sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(300)'], start_new_session=True)
        for negative in (False, True):
            folder = root / ('shared-invalid' if negative else 'shared-valid'); folder.mkdir()
            source = folder / 'Consumer.cs'; source.write_text('extern alias Subject; public class Consumer { public Subject::R03.Node Value; }\n')
            subject = Path(report['negative']['input']) if negative else batch.fixture_root / 'baseline/A.dll'
            command = compiler_args(tools[0], copied / 'csc.dll', tools[2], source, folder / 'Consumer.dll', subject, [batch.fixture_root / 'baseline/B.dll'])
            command.insert(3, '/shared')
            receipt = supervised(batch, anchor, command, 600, expected_exit=1 if negative else 0)
            value = loads(Path(receipt['completion']).read_text())
            outer = Path(receipt['outerReceipt']).parent
            log = (outer / 'stdout.log').read_text() + (outer / 'stderr.log').read_text()
            if negative:
                require('CS0009' in log and 'invalid public key' in log.lower() and not (folder / 'Consumer.dll').exists(), 'Expected shared compiler diagnostic')
            else:
                require((folder / 'Consumer.dll').is_file(), 'Real shared compiler output required')
            require(sentinel.poll() is None, 'Unrelated process was disturbed')
            command_records.append({'negative': negative, 'receipt': receipt, 'originalExit': value['commandExitCode'],
                                    'compilerChildrenObserved': len(value['completion']['before'])})
        require(any(r['compilerChildrenObserved'] for r in command_records), 'Must observe actual shared compiler lifetime, not only policy text')
        result.update(result='Passed', sharedCompilerCases=command_records, unrelatedSentinelUnaffected=True,
                      fixtureContracts=33, sdk='8.0.318', supervisorScope='Real SDK compiler; not Unity Editor',
                      metadataAuditSha256=sha(audit_root / 'results.json'))
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if sentinel is not None:
            sentinel.kill(); sentinel.wait()
        write(root / 'results.json', result)
    print(result)
    return 0 if result['result'] == 'Passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
