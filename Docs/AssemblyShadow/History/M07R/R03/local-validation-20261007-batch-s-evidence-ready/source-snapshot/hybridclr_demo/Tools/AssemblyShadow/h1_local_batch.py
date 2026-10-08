#!/usr/bin/env python3
"""Run an explicit local diagnostic task graph with fresh logs and no shell.

This runner never changes branches/pins, cleans caches, chooses a PDB fix route,
or grants H1/M08 approval. Failed tasks block only their declared dependents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
from string import Template
import subprocess
import time
import xml.etree.ElementTree as ET


class BatchError(ValueError):
    pass


def need(value, message):
    if not value:
        raise BatchError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)


def validate(plan):
    need(type(plan) is dict and plan.get('schemaVersion') == 1 and plan.get('kind') == 'H1LocalDiagnosticBatch', 'Unsupported diagnostic plan')
    tasks = plan.get('tasks')
    need(type(tasks) is list and bool(tasks), 'A nonempty task list is required')
    seen = set()
    for task in tasks:
        need(type(task) is dict and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', task.get('id', '')), 'Unsafe task ID')
        need(task['id'] not in seen, 'Duplicate task ID')
        dependencies = task.get('requires', [])
        need(type(dependencies) is list and all(type(item) is str and item in seen for item in dependencies), 'Dependencies must name earlier tasks')
        seen.add(task['id'])
        need(task.get('kind') in ('python', 'unity', 'command'), 'Unknown task kind')
        need(type(task.get('cwd')) is str, 'A working-directory string is required')
        need(type(task.get('environment', {})) is dict and all(type(k) is str and type(v) is str for k, v in task.get('environment', {}).items()), 'Environment overrides must be strings')
        need(type(task.get('argv')) is list and task['argv'] and all(type(value) is str and '\0' not in value for value in task['argv']), 'argv must be a nonempty string array')
        need(type(task.get('timeoutSec')) in (int, float) and 0 < task['timeoutSec'] <= 86400, 'A bounded timeout is required')
        need(task.get('validator', 'exit-code') in ('exit-code', 'unittest', 'nunit'), 'Unknown result validator')
        if task['kind'] == 'unity':
            need(type(task.get('unityProject')) is str and task['unityProject'], 'Unity tasks require an exact project ownership guard')
    return plan


def substitute(value, variables):
    try:
        return Template(value).substitute(variables)
    except (KeyError, ValueError) as error:
        raise BatchError('Unresolved/invalid plan variable: ' + str(error)) from error


def validate_nunit(path, minimum=1):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), 'NUnit XML is absent or symlinked')
    raw = path.read_bytes()
    need(b'<!DOCTYPE' not in raw.upper(), 'NUnit XML must not contain a DTD')
    root = ET.fromstring(raw)
    cases = [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'test-case']
    need(len(cases) >= minimum, 'NUnit did not execute the required number of test cases')
    counts = {}
    for case in cases:
        result = case.get('result', 'Unknown')
        counts[result] = counts.get(result, 0) + 1
    return {'testCount': len(cases), 'counts': counts,
            'passed': root.get('result', '').lower() == 'passed' and all(case.get('result', '').lower() == 'passed' for case in cases)}


def run_command(argv, cwd, env, log, timeout):
    # Only the process group created here is terminated on timeout/interruption.
    started = time.monotonic()
    with Path(log).open('xb') as output:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT,
                                   shell=False, start_new_session=os.name == 'posix')
        timed_out = False
        try:
            code = process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
            timed_out = isinstance(error, subprocess.TimeoutExpired)
            if os.name == 'posix':
                try:
                    if os.getpgid(process.pid) == process.pid:
                        os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                process.terminate()
            try:
                code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name == 'posix':
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                code = process.wait(timeout=5)
            if not timed_out:
                raise
    return {'exitCode': code, 'timedOut': timed_out, 'elapsedSeconds': time.monotonic() - started,
            'logSha256': hashlib.sha256(Path(log).read_bytes()).hexdigest()}


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def run_plan(plan, variables, output, execute=False):
    validate(plan)
    need(type(variables) is dict and all(type(k) is str and type(v) is str for k, v in variables.items()), 'Variables must be strings')
    output = Path(output).absolute()
    need(not output.exists() and not output.is_symlink(), 'The run directory must be new; historical output is never overwritten')
    needed_space = plan.get('minimumFreeGiB', 0)
    need(type(needed_space) in (int, float) and needed_space >= 0, 'Invalid disk-space floor')
    check_root = output.parent
    while not check_root.exists():
        check_root = check_root.parent
    if execute:
        need(shutil.disk_usage(check_root).free >= needed_space * 1024**3, 'Insufficient free space; no evidence is deleted automatically')
    for capture in plan.get('captureIndex', []):
        path = Path(capture['path'])
        need(path.is_absolute() and path.is_file() and not path.is_symlink() and
             hashlib.sha256(path.read_bytes()).hexdigest() == capture['sha256'], 'Selected replay capture changed after plan preparation')
    prepared = []
    # Resolve the complete plan before executing the first command.
    for task in plan['tasks']:
        local = dict(variables, RUN_DIR=str(output), TASK_DIR=str(output / task['id']))
        row = dict(task)
        row['argv'] = [substitute(value, local) for value in task['argv']]
        row['cwd'] = substitute(task['cwd'], local)
        need(Path(row['cwd']).is_absolute() and Path(row['cwd']).is_dir(), 'Task working directory is missing or not absolute')
        row['environment'] = {key: substitute(value, local) for key, value in task.get('environment', {}).items()}
        if 'nunitXml' in task:
            row['nunitXml'] = substitute(task['nunitXml'], local)
            need(Path(row['nunitXml']).resolve().is_relative_to((output / task['id']).resolve()), 'NUnit output must remain under its fresh task directory')
        if task['kind'] == 'unity':
            row['unityProject'] = substitute(task['unityProject'], local)
            need(Path(row['unityProject']).is_absolute() and Path(row['unityProject']).is_dir(), 'Invalid Unity project')
            need('pwsh' in variables, 'Unity ownership checks require an explicit PowerShell executable')
            guard = Path(__file__).with_name('Check-H1EditorStopped.ps1')
            row['guardArgv'] = [variables['pwsh'], '-NoProfile', '-File', str(guard), '-ProjectPath', row['unityProject']]
        prepared.append(row)
    if not execute:
        return {'kind': 'H1LocalDiagnosticBatchPreview', 'tasks': prepared, 'executed': False,
                'humanGatePassed': False, 'mayEnterR02': False}
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / 'input-plan.json', plan)
    write_new(output / 'resolved-plan.json', {'tasks': prepared, 'variables': variables, 'captureIndex': plan.get('captureIndex', [])})
    results = {}
    for task in prepared:
        directory = output / task['id']; directory.mkdir()
        blocked = [name for name in task.get('requires', []) if results[name]['status'] != 'Passed']
        row = {'id': task['id'], 'status': 'Blocked' if blocked else 'NotRun', 'blockedBy': blocked}
        if not blocked:
            environment = dict(os.environ, **task['environment'])
            try:
                if 'guardArgv' in task:
                    guard = run_command(task['guardArgv'], task['cwd'], environment, directory / 'ownership.log', 45)
                    need(guard['exitCode'] == 0 and not guard['timedOut'], 'Exact-project Editor is running or ownership detection failed')
                observed = run_command(task['argv'], task['cwd'], environment, directory / 'process.log', task['timeoutSec'])
                row.update(observed)
                row['status'] = 'Timeout' if observed['timedOut'] else ('Passed' if observed['exitCode'] == 0 else 'Failed')
                if row['status'] == 'Passed' and task.get('validator') == 'nunit':
                    row['nunit'] = validate_nunit(task['nunitXml'], task.get('minimumTests', 1))
                    if not row['nunit']['passed']:
                        row['status'] = 'Failed'
                if row['status'] == 'Passed' and task.get('validator') == 'unittest':
                    text = (directory / 'process.log').read_text(encoding='utf-8', errors='replace')
                    counts = re.findall(r'^Ran (\d+) tests? in ', text, re.M)
                    need(counts and int(counts[-1]) >= task.get('minimumTests', 1), 'Python test execution count is absent or insufficient')
                    row['testCount'] = int(counts[-1])
            except (OSError, ValueError, ET.ParseError) as error:
                row['status'] = 'Blocked' if 'exitCode' not in row else 'Failed'
                row['error'] = str(error)
        results[task['id']] = row
        write_new(directory / 'task-result.json', row)
    report = {'schemaVersion': 1, 'kind': 'H1LocalDiagnosticBatchResult', 'tasks': list(results.values()),
              'status': 'DiagnosticsPassed' if all(row['status'] == 'Passed' for row in results.values()) else 'Incomplete',
              'wholeChainM08Pass': False, 'humanGatePassed': False, 'mayEnterR02': False}
    write_new(output / 'batch-result.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--variables', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    report = run_plan(read_json(args.plan), read_json(args.variables), args.output, args.execute)
    print(json.dumps(report, indent=2))
    return 1 if report.get('status') == 'Incomplete' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print('Blocked: ' + str(error), file=__import__('sys').stderr)
        raise SystemExit(1)
