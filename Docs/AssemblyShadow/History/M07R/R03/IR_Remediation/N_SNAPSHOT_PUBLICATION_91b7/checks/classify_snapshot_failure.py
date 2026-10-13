#!/usr/bin/env python3
"""Classify source-defined native writer diagnostics, never semantic acceptance.

Reads one authenticated existing log. Optional output is exclusively created;
no process, compiler, Player, repository, or historical evidence is modified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

PATTERN = re.compile(
    rb'^\[R03SnapshotFailure\] version=1 pid=(\d+) operation=([a-z-]+) '
    rb'field=(-?\d+) reason=(\d+) previousState=(-?\d+) length=(\d+) '
    rb'limit=(\d+) errno=(-?\d+) intMask=([0-9a-f]{8}) textMask=([0-9a-f]{8})$'
)
REASONS = {
    1: 'ConcurrentOrReentrantWriter', 2: 'WrongWriterState', 3: 'InvalidOutputPath',
    4: 'ExclusiveOpenFailed', 5: 'FdopenFailed', 6: 'InvalidSlotIndex',
    7: 'DuplicateSlot', 8: 'InvalidBooleanValue', 9: 'TextExceedsOriginalLimit',
    10: 'MissingOutputStream', 11: 'MissingIntegerSlot', 12: 'MissingTextSlot',
    13: 'StreamWriteFailed', 14: 'FlushFailed', 15: 'FsyncFailed', 16: 'CloseFailed',
}
OPERATIONS = {'open', 'fdopen', 'int', 'text', 'seal', 'missing-int', 'missing-text',
              'write', 'flush', 'fsync', 'close'}
REASON_OPERATIONS = {1: {'open','int','text','seal'}, 2: {'open','int','text','seal'},
    3: {'open'}, 4: {'open'}, 5: {'fdopen'}, 6: {'int','text'},
    7: {'int','text'}, 8: {'int'}, 9: {'text'}, 10: {'seal'},
    11: {'missing-int'}, 12: {'missing-text'}, 13: {'write'},
    14: {'flush'}, 15: {'fsync'}, 16: {'close'}}


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def classify(data: bytes, expected_pid: int, expected_sha256: str) -> dict:
    require(type(data) is bytes and len(data) <= 64 * 1024 * 1024, 'Bounded bytes log required')
    require(type(expected_pid) is int and expected_pid > 0, 'Exact positive PID required')
    require(type(expected_sha256) is str and re.fullmatch('[0-9a-f]{64}', expected_sha256) is not None,
            'Exact SHA-256 required')
    digest = hashlib.sha256(data).hexdigest()
    require(digest == expected_sha256, 'Log SHA-256 mismatch')
    lines = [line for line in data.splitlines() if b'[R03SnapshotFailure]' in line]
    require(len(lines) <= 1, 'More than one purported immutable first-failure record')
    value = None
    if lines:
        match = PATTERN.fullmatch(lines[0])
        require(match is not None, 'Malformed or unbound native failure line')
        groups = match.groups()
        pid, field, reason, previous, length, limit, error = (
            int(groups[i]) for i in (0, 2, 3, 4, 5, 6, 7))
        operation = groups[1].decode('ascii')
        int_mask, text_mask = int(groups[8], 16), int(groups[9], 16)
        require(pid == expected_pid, 'Native failure PID mismatch')
        require(operation in OPERATIONS and reason in REASONS, 'Unknown operation/reason')
        require(operation in REASON_OPERATIONS[reason], 'Operation/reason pair not emitted by source')
        require(previous in (-1, 0, 1, 2, 3), 'Unknown writer state')
        require(-2147483648 <= field <= 2147483647, 'Invalid recorded slot')
        require(limit == 262144 and 0 <= length <= limit + 1, 'Changed scan bound or invalid length')
        require(length == (limit + 1 if reason == 9 else 0), 'Inconsistent bounded scan length')
        require(int_mask < (1 << 25) and text_mask < (1 << 16), 'Out-of-schema slot mask')
        require(error >= 0, 'Invalid native errno')
        value = {
            'operation': operation, 'slot': field, 'reason': REASONS[reason], 'reasonCode': reason,
            'previousWriterState': previous, 'scannedPrefixBytes': length, 'originalTextLimit': limit,
            'fullLengthKnown': False, 'lengthMeasured': reason == 9, 'errno': error, 'integerMask': int_mask, 'textMask': text_mask,
        }
    return {
        'schemaVersion': 1, 'kind': 'R03SnapshotTransportClassification',
        'result': 'NativeTransportFailureRecorded' if value else 'NoNativeTransportFailureRecorded',
        'pid': expected_pid, 'logBytes': len(data), 'logSha256': digest, 'firstFailure': value,
        'semanticVerification': 'SeparateOriginalRawVerifierRequired',
        'runtimeAcceptance': False, 'historicalResultChanged': False,
        'limits': 'A recorded over-limit length is a bounded prefix, not the full producer length; '
                  'absence of a failure line does not prove a complete raw file, cause, or successful run.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    path = args.log
    require(path.is_absolute() and path.resolve(strict=True) == path and path.is_file(),
            'Canonical existing regular log required')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Linked log refused')
    require(path.stat().st_size <= 64 * 1024 * 1024, 'Log exceeds analysis input bound')
    result = classify(path.read_bytes(), args.pid, args.sha256)
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output is not None:
        out = args.output
        require(out.is_absolute() and out == out.resolve(strict=False) and out.parent.is_dir(),
                'Canonical output with existing parent required')
        require(not out.exists() and not out.is_symlink(), 'Output must be unused')
        with out.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
