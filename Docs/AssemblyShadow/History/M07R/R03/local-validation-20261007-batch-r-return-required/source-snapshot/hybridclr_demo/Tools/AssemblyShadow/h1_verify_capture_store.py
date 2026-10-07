#!/usr/bin/env python3
"""Independently verify one H1 capture-attempt retention store.

This validates reversible retained bytes, raw/stored hashes and both logical and
physical budgets. It does not approve compiler provenance, a build receipt, M08,
or any human gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from h1_capture_attempt import RetentionError, verify_attempt_store


def read_state(root: Path) -> dict:
    path = root / 'attempt-state.json'
    if not path.is_file() or path.is_symlink():
        raise RetentionError('Missing canonical attempt state')
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.attempt_root.resolve(strict=True)
    summary = verify_attempt_store(root)
    state = read_state(root)
    output = args.output
    if not output.is_absolute() or output != output.resolve() or output.exists() or not output.parent.is_dir():
        raise RetentionError('Output must be a new canonical file in an existing directory')
    result = {
        'schemaVersion': 1,
        'kind': 'H1CaptureRetentionStoreVerification',
        'status': 'StoreVerifiedNotAcceptance',
        'attemptRoot': str(root),
        'attemptStatus': state.get('status'),
        'attemptStage': state.get('stage'),
        'retentionPolicy': state.get('retentionPolicy'),
        'retentionLimits': state.get('retentionLimits'),
        **summary,
        'candidateAcceptance': False,
        'humanGatePassed': False,
        'mayEnterR02': False,
    }
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print('Retention store verification failed: ' + str(error), file=__import__('sys').stderr)
        raise SystemExit(1)
