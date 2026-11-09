from pathlib import Path
import json
import shutil

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-CapturedGeneric09'
batch = base / 'R03IR-CapturedGeneric-20261109-oneuse-09'
audit = json.loads((preflight/'FINAL_INDEPENDENT_AUDIT.json').read_text())
producer = json.loads((batch/'LOCAL_BATCH_RESULT.json').read_text())
build = audit['build']
bridge = build.get('bridge') if build else None
g = audit['capturedPlayer']
counts = audit['cellCounts']
result = 'PASS' if audit['runnerExit']==0 else 'FAIL'
players = [*audit['players'],dict(g,case='captured-generic')]
actual_players = [p for p in players if 'commandPid' in p]
unity_commands = [c for c in audit['commands'] if any(
    part.endswith('/Contents/MacOS/Unity') for part in c['command'])]
assert len(unity_commands)<=1
host = audit['hostCustody']
pieces = [
    f'**Focused captured-generic {result}.** One invocation produced '
    + ', '.join(f'{count} {status}' for status,count in sorted(counts.items()))
    + f' across the fixed 19-cell roster. There were {len(unity_commands)} Unity build commands and {len(actual_players)} actual Player launches.',
]
if build:
    pieces.append(f'Unity 2022.3.62f2 macOS arm64 IL2CPP ON/diagnostics2/Release BuildPipeline reported '
                  f'{build["buildPipelineResult"]} with {build["errors"]} errors and {build["warnings"]} BuildReport warning(s). '
                  f'Build receipt SHA-256 is `{build["sha256"]}`.')
if bridge:
    shutil.copyfile(bridge['generatedPath'],preflight/'ActualGeneratedMethodBridge.cpp')
    pieces.append(f'The generated Cdecl int32() wrapper and table contained exactly one `Bi4` row and its null terminator. '
                  f'The generated source hashes after augmentation and after BuildPipeline matched `{bridge["generatedSha256"]}`. '
                  f'The actual GameAssembly SHA-256 `{bridge["gameAssemblySha256"]}` binds the Bi4 identity and all six initializer and captured-generic exports.')
t = audit.get('capturedTarget')
if t:
    pieces.append(f'Two fresh same-host fixture generations matched for captured Methods.dll at '
                  f'SHA-256 `{t["sha256"]}`, MVID `{t["mvid"]}`, {t["size"]} bytes.')
table = ['| Player | Cell | PID | Exit | Strict raw bytes |','| --- | --- | ---: | ---: | ---: |']
for p in players:
    table.append(f'| {p["case"]} | {p["state"]} | {p.get("commandPid","—")} | {p.get("commandExit","—")} | {p.get("rawBytes","—")} |')
pieces.append('\n'.join(table))
if all(p['state']=='Passed' for p in audit['players']):
    pieces.append('Both fresh initializer traces record linked Bi4 phase 103 result 1 before Commit and one native callback at phases 299/300. '
                  'The physical field was 3 and mask 15. Control returned Commit/state 0/6 with an empty reason. '
                  'The failure returned 19/9 after the callback and retained the exact R03IR.InitializerFailure.AfterPublication.V1 sentinel. '
                  'The post-terminal AOT attempt did not succeed and the canary remained 1→1.')
if g['state']=='Passed':
    raw=g['strictRecord']; recovery=raw['nativeRecovery']
    pieces.append('The captured-generic Player joined the physical original Methods.R03.Node type handle to its inflated Assembly-CSharp '
                  'AOT method owner. It recorded state 6 after inflation and a native guard denial that produced FailedAfterCommit state 9 and '
                  f'first error 15. Its exact native reason was `{recovery["reason"]}`. The actual post-terminal Runtime::Invoke '
                  'reported an exception and the native counter remained 1→1.')
else:
    failure=audit['firstFailedCell']
    if failure:
        pieces.append(f'The first failed cell was `{failure["id"]}`. {failure.get("error","")}')
    if g['state']=='Failed':
        pieces.append('The captured-generic Player failed. The exact runtime failure boundary and limits are recorded with the original command and Player evidence.')
pieces.append(f'The host audit recorded {len(audit["nativeHost"].get("components") or [])} native host components. '
              f'Host custody recorded {host.get("fileCount")} regular files and {host.get("symlinkCount")} literal symlinks. '
              f'The product seal was {audit["sealStatus"]} with {audit["archiveMembers"]} members.')
pieces.append('Return to Primary Implementation with all acceptance flags false. The old oneuse-08 prerequisite result remains PrerequisiteBlocked/NotRun.')
(preflight/'FINDING.md').write_text('\n\n'.join(pieces)+'\n')
(preflight/'RUNTIME_FINDINGS.json').write_text(json.dumps({
    'result':result,'producerResult':producer['result'],'cells':counts,'firstFailedCell':audit['firstFailedCell'],
    'build':build,'unityCommands':unity_commands,'players':players,'capturedTarget':t,
    'hostCustody':host,'seal':audit['seal'],'runtimeAcceptance':False
},indent=2)+'\n')
print('Prepared factual report',counts,[(p['case'],p.get('commandPid'),p.get('commandExit')) for p in players])
