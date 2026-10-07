"""Explicit, read-only source authority for a recorded profile-2 codec input.

A relative source pin has meaning only with its captured project base and exact
owning repository. No cwd-relative or neighboring-checkout fallback is permitted.
"""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import subprocess

HEADER = 'hybridclr/metadata/InterpreterMetadataIndexCodec.h'
ORIGINS = frozenset(('git@github.com:night-outlook/hybridclr.git',
                     'https://github.com/night-outlook/hybridclr.git',
                     'https://github.com/night-outlook/hybridclr'))


@dataclass(frozen=True)
class CodecSourceContext:
    project_root: Path
    repository_root: Path
    revision: str


def _require(value, message):
    if not value:
        raise ValueError(message)


def _regular_root(path):
    p = Path(path)
    _require(p.is_absolute(), 'Source authority root must be absolute')
    _require(not any(x.is_symlink() for x in (p, *p.parents)), 'Symlink in source authority path')
    p = p.resolve(strict=True)
    _require(p.is_dir(), 'Source authority directory required')
    return p


def _git(repository, *args):
    return subprocess.run(['git', '-C', str(repository), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout


def read_codec(pin, revision, expected_hash, context=None):
    _require(isinstance(pin, dict) and re.fullmatch('[0-9a-f]{40}', revision or ''), 'Exact codec source revision')
    _require(pin.get('revision') == revision and pin.get('url') in ORIGINS, 'Canonical codec source pin')
    _require(re.fullmatch('[0-9a-f]{64}', expected_hash or ''), 'Exact codec hash')
    recorded = pin.get('localPath')
    _require(type(recorded) is str and bool(recorded), 'Explicit recorded source path required')
    relative = Path(recorded)
    if context is None:
        _require(relative.is_absolute(), 'Relative codec pin requires explicit authenticated project/owner context')
        repository = _regular_root(relative)
        project = None
    else:
        _require(type(context) is CodecSourceContext and context.revision == revision, 'Wrong source context/revision')
        project = _regular_root(context.project_root)
        owner = _regular_root(context.repository_root)
        repository = _regular_root(relative if relative.is_absolute() else project / relative)
        _require(repository == owner, 'Recorded pin resolves to a foreign owning repository')
    top = _git(repository, 'rev-parse', '--show-toplevel').decode().strip()
    _require(_regular_root(top) == repository, 'Source pin must be the owning repository top level')
    head = _git(repository, 'rev-parse', 'HEAD').decode().strip()
    origin = _git(repository, 'config', '--get', 'remote.origin.url').decode().strip()
    _require(head == revision and origin in ORIGINS, 'Wrong owning codec repository or HEAD')
    content = _git(repository, 'show', revision + ':' + HEADER)
    observed = hashlib.sha256(content).hexdigest()
    _require(observed == expected_hash, 'Pinned codec header hash mismatch')
    # Re-read authority after the blob read; no mutable working-tree header used.
    _require(_git(repository, 'rev-parse', 'HEAD').decode().strip() == revision and
             _git(repository, 'config', '--get', 'remote.origin.url').decode().strip() == origin,
             'Codec source authority changed during verification')
    return content, {'kind': 'R03ExplicitCodecSource', 'result': 'Passed', 'projectRoot': str(project) if project else None,
                     'recordedLocalPath': recorded, 'repositoryRoot': str(repository), 'revision': revision,
                     'origin': origin, 'header': HEADER, 'sha256': observed, 'runtimeAcceptance': False}
