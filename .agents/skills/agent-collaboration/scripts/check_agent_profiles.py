"""Validate repository agent contracts using Python 3.11+ standard library only."""
import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

PAIRED_ROLES = ('code-debugger', 'code-reviewer', 'code-gate-reviewer')
READ_ONLY = {'code-explorer', 'code-general'} | {
    f'{role}-{family}' for role in ('code-reviewer', 'code-gate-reviewer')
    for family in ('sol', 'astra')
}



def check(root, host_models=None):
    errors = []
    profiles = {}
    for path in sorted((root / '.codex/agents').glob('*.toml')):
        try:
            profile = tomllib.loads(path.read_text())
        except (ValueError, OSError) as exc:
            errors.append(f'{path.name}: invalid TOML: {exc}')
            continue
        name = profile.get('name')
        if not isinstance(name, str) or not name:
            errors.append(f'{path.name}: missing name')
            continue
        if name in profiles:
            errors.append(f'{path.name}: duplicate name {name}')
        profiles[name] = profile
        if name != path.stem:
            errors.append(f'{path.name}: name must match filename')
        for field in ('model', 'model_reasoning_effort', 'description', 'developer_instructions'):
            if not isinstance(profile.get(field), str) or not profile[field].strip():
                errors.append(f'{name}: missing explicit {field}')
        if name in READ_ONLY and profile.get('sandbox_mode') != 'read-only':
            errors.append(f'{name}: requires read-only sandbox')
        if host_models is not None:
            model, effort = profile.get('model'), profile.get('model_reasoning_effort')
            if not isinstance(model, str) or model not in host_models:
                errors.append(f'{name}: model absent from supplied host snapshot: {model}')
            elif effort not in host_models[model]:
                errors.append(f'{name}: effort {effort} unsupported by supplied host snapshot')
    for role in PAIRED_ROLES:
        if role in profiles:
            errors.append(f'{role}: retired unsuffixed profile')
        pair = [profiles.get(f'{role}-{family}') for family in ('sol', 'astra')]
        if any(profile is None for profile in pair):
            errors.append(f'{role}: missing Sol/Astra pair member')
            continue
        for family, profile in zip(('sol', 'astra'), pair):
            model = profile.get('model')
            families = set(re.findall(r'(?i)(?<![a-z])(sol|astra)(?![a-z])', model.lower())) if isinstance(model, str) else set()
            if families != {family}:
                errors.append(f'{role}-{family}: model family differs from profile suffix')
        # All behavioral and permission fields must agree, including future fields.
        contracts = [{k: v for k, v in p.items() if k not in {'name', 'description', 'model'}} for p in pair]
        if contracts[0] != contracts[1]:
            errors.append(f'{role}: paired profile contracts differ')
    if not profiles:
        errors.append('No agent profiles found')
    skill = root / '.agents/skills/agent-collaboration/SKILL.md'
    try:
        content = skill.read_text()
    except OSError as exc:
        return errors + [str(exc)]
    routes = set()
    for line in content.splitlines():
        if not line.startswith('|') or '`code-' not in line:
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) != 4:
            errors.append(f'Malformed routing row: {line}')
            continue
        names = re.findall(r'`([^`]+)`', cells[1])
        fixed = re.fullmatch(r'`([^`]+)` / `([^`]+)` / (read-only|inherited permissions)', cells[2])
        fallback = re.fullmatch(r'`(default|worker|explorer)`, `([^`]+)` / `([^`]+)`', cells[3])
        if len(names) != 1 or not fixed or not fallback:
            errors.append(f'Malformed routing row: {line}')
            continue
        name = names[0]
        if name in routes:
            errors.append(f'{name}: duplicate routing row')
        routes.add(name)
        if name not in profiles:
            errors.append(f'{name}: route has no profile')
            continue
        model, effort, access = fixed.groups()
        profile = profiles[name]
        if (profile.get('model'), profile.get('model_reasoning_effort')) != (model, effort):
            errors.append(f'{name}: profile model/effort differs from routing table')
        actual_access = ('inherited permissions' if 'sandbox_mode' not in profile
                         else profile['sandbox_mode'])
        if actual_access != access:
            errors.append(f'{name}: profile access differs from routing table')
        if fallback.groups()[1:] != (model, effort):
            errors.append(f'{name}: fallback model/effort differs from fixed route')
    for name in sorted(profiles.keys() - routes):
        errors.append(f'{name}: profile has no routing row')
    for name in sorted(READ_ONLY - profiles.keys()):
        errors.append(f'{name}: required read-only role missing')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--host-models', type=Path, help='Current host JSON mapping model IDs to supported effort arrays')
    args = parser.parse_args()
    try:
        host = json.loads(args.host_models.read_text()) if args.host_models else None
        if args.host_models and (not isinstance(host, dict) or not host or any(
            not isinstance(k, str) or not isinstance(v, list) or not v or
            any(not isinstance(e, str) or not e for e in v) for k, v in host.items()
        )):
            raise ValueError('Host snapshot must be a nonempty object mapping model IDs to nonempty effort arrays')
        errors = check(args.root, host)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    for error in errors:
        print(f'FAIL: {error}', file=sys.stderr)
    if errors:
        return 1
    print('PASS: agent profiles and routing agree')
    print('Model availability: checked against supplied snapshot' if host is not None else
          'Model availability: NOT CHECKED (no current host snapshot supplied)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
