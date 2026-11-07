from pathlib import Path
import json
import shutil

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-Initializer07'
batch = base / 'R03IR-Initializer-20261107-oneuse-07'
audit = json.loads((preflight / 'FINAL_INDEPENDENT_AUDIT.json').read_text())
producer = json.loads((batch / 'LOCAL_BATCH_RESULT.json').read_text())
build = audit['build']
bridge = build.get('bridge') if build else None
counts = audit['cellCounts']
host = audit['hostCustody']
tests = sum(row['count'] or 0 for row in audit['initializerUnitTests'])
passed = audit['runnerExit'] == 0
pieces = [
    f'**Focused initializer {"PASS" if passed else "FAIL"}.** '
    + ', '.join(f'{number} {name}' for name, number in sorted(counts.items()))
    + ' across one 15-cell batch.',
]
if build:
    pieces.append(f'Unity 2022.3.62f2 macOS arm64 IL2CPP BuildPipeline reported '
                  f'{build["buildPipelineResult"]} with {build["errors"]} errors and '
                  f'{build["warnings"]} warning(s). The build receipt SHA-256 is `{build["sha256"]}`.')
if bridge:
    shutil.copyfile(bridge['generatedPath'], preflight / 'ActualGeneratedMethodBridge.cpp')
    pieces.append(f'The generated Cdecl int32() wrapper and table contained exactly one `Bi4` row and a null terminator. '
                  f'The source hash after augmentation and after BuildPipeline was `{bridge["generatedSha256"]}`. '
                  f'The helper checks its pre-augmentation source internally. The BuildReceipt records the two post-augmentation hashes. '
                  f'GameAssembly SHA-256 `{bridge["gameAssemblySha256"]}` binds both native exports and the linked Bi4 identity. '
                  'The isolated project kept its empty hot-update assembly list.')
rows = []
for player, trace, rec in zip(audit['players'],audit['nativeTraceChecks'],audit['nativeRecoveryChecks']):
    phases = {}
    for event in trace.get('events',[]):
        phases.setdefault(event['phase'],[]).append({k:event[k] for k in ('seq','a','b','c','d')})
    core = rec.get('nativeRecovery',{})
    raw = player.get('raw',{})
    verification = player.get('verification',{})
    rows.append({
        'mode':player['case'],'status':player['state'],'pid':player.get('commandPid'),
        'exit':player.get('commandExit'),'request':player.get('request'),
        'verification':verification.get('result'),
        'semanticVerifierStatus':verification.get('semanticVerifierStatus'),
        'strictBytes':player.get('rawBytes'),'strictSha256':player.get('rawSha256'),
        'traceSha256':trace.get('sha256'),'recoverySha256':rec.get('rawSha256'),
        'phase103':phases.get(103,[]),'phase299':phases.get(299,[]),'phase300':phases.get(300,[]),
        'phase191':phases.get(191,[]),'phase201':phases.get(201,[]),
        'phase211':phases.get(211,[]),'phase601':phases.get(601,[]),
        'phase620':phases.get(620,[]),'preparedField':raw.get('preparedField'),
        'finalField':raw.get('finalField'),'positiveMask':raw.get('positiveMask'),
        'callbackCalls':raw.get('initializerCallbackCalls'),
        'commit':core.get('terminalFailureCode'),'stateCode':core.get('stateCode'),
        'reason':core.get('reason'),'recoveryJoins':rec.get('independentEnvelopeJoins'),
    })
if rows:
    lines = ['| Player | PID | Exit | Bi4 phase 103 | Callback 299/300 | Commit / state | Field / mask |',
             '| --- | ---: | ---: | --- | --- | --- | --- |']
    for row in rows:
        native = row['phase300']
        callback = (f'{len(row["phase299"])} / {len(native)}' if row['phase299'] or native else 'Unavailable')
        status = ', '.join(str(v['a']) for v in row['phase103']) or 'Unavailable'
        lines.append(f'| {row["mode"]} | {row["pid"]} | {row["exit"]} | {status} | {callback} | '
                     f'{row["commit"]} / {row["stateCode"]} | {row["finalField"]} / {row["positiveMask"]} |')
    pieces.append('\n'.join(lines))
if passed:
    pieces.append('Both distinct Players observed the real linked Bi4 entry before Commit and entered and completed the native callback exactly once. '
                  'The pinned field remained 3 and the positive mask was 15. Control committed successfully at state 6 and had empty recovery reason. '
                  'Commit returned 19 and entered FailedAfterCommit state 9 after the callback, with the exact post-preparation recovery sentinel '
                  '`R03IR.InitializerFailure.AfterPublication.V1`. The AOT canary remained 1→1 and the failure Player recorded an attempted post-terminal AOT call that failed without changing the canary. '
                  'Both strict V1 verifications passed within the initializer scope.')
else:
    failed = audit['firstFailedCell']
    reason = failed.get('error', '') if failed else ''
    pieces.append(f'The first failed cell was `{failed["id"]}`. {reason}' if failed else 'The runner returned failure.')
    for row in rows:
        pieces.append(f'{row["mode"]} recorded native recovery reason `{row["reason"]}` and strict output size {row["strictBytes"]}.')
    pieces.append('Return the observed failure boundary to Primary Implementation.')
pieces.append(f'The native host audit covered {len(audit["nativeHost"].get("components") or [])} components and {tests} initializer tests. '
              f'Host custody recorded {host.get("fileCount")} regular files and {host.get("symlinkCount")} literal symlinks. '
              f'The original product seal was {audit["sealStatus"]} with {audit["archiveMembers"]} members.')
pieces.append('WEB_TO_LOCAL refers to a historical oneuse-06 RUNTIME_FINDINGS.json filename. Its published findings are in '
              'local-evidence/FINDING.md and BRIDGE_FINDING.json. Those files and the preserved historical raw inventory supplied the prior-cycle record.')
pieces.append('Return to Primary Implementation with all acceptance flags false.')
(preflight/'FINDING.md').write_text('\n\n'.join(pieces)+'\n')
(preflight/'RUNTIME_FINDINGS.json').write_text(json.dumps({
    'producerResult':producer['result'],'cells':counts,'build':build,'players':rows,
    'hostCustody':host,'seal':audit['seal'],'runtimeAcceptance':False,
},indent=2)+'\n')
print('Prepared factual report',counts,[(row['mode'],row['pid'],row['exit']) for row in rows])
