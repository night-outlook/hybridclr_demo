"""Portable, explicit H1 successor selection and archive integrity contract.

This is not the independent M08 reviewer. It binds critical membership and raw
identities, rejects known stale substitutions, and archives unchanged bytes.
Existing strict runtime verifiers and the independent whole-chain review are
still required. An unavailable file is BLOCKED, not a failed runtime test.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import h1_pch_provenance as pch

from h1_witness_contract import expected_site_ids, verify_runtime_probe

STARTUP_MODES = ('Control','OrdinaryFirst','OrdinaryAfterReserve','Oversize','Mismatch','Type','Object','Cctor','NativeScript','MetadataFailure','InitializerFailure')
PARAMETERS = ('H1R-P01-a','H1R-P01-b','H1R-P01-c','H1R-P01-d','H1R-P02-a','H1R-P02-b','H1R-P03-a','H1R-P03-b',
              'H1R-P04-return255','H1R-P04-partial-names','H1R-P04-instance','H1R-P04-mixed-kinds')
NESTED = ('H1R-N01-a','H1R-N01-b','H1R-N01-c','H1R-N01-d','H1R-N02-a','H1R-N02-b',
          'H1R-N03-interleaved','H1R-N04-adjacent-valid','H1R-N04-adjacent-overflow','H1R-N05-final-repeat')
COUNT_CELLS = frozenset('/'.join((family, case, path, cpp))
    for family,cases in (('parameters',PARAMETERS),('nested',NESTED)) for case in cases
    for path in ('Ordinary-OFF','Ordinary-ON','Shadow-ON') for cpp in ('Debug','Release'))
REPRO_CELLS = frozenset((family,case,cpp) for family,cases in
    (('parameters',('H1R-P03-a','H1R-P03-b')),('nested',('H1R-N02-a','H1R-N02-b')))
    for case in cases for cpp in ('Debug','Release'))
SINGLE_ROLES = frozenset(('candidate-source-pins','reproduction-source-pins','witness-configuration','witness-runtime',
    'count-matrix','candidate-compiler-verification','reproduction-compiler-verification',
    'startup-launches','startup-verification','baseline-on','baseline-off','reproduction-execution',
    'm06-aggregate','m06-impact','m07-full','r00-results','performance-analysis','performance-receipt',
    'ordinary-capacity','mixed-capacity','lazy-dense','old-player','editor-inventory','python-inventory','source-equivalence','scope-dispositions'))
MULTI_ROLES = {'candidate-count-builds':4,'reproduction-count-builds':2,
              'candidate-managed-verifications':4,'reproduction-managed-verifications':2}
MAX_JSON = 512 * 1024 * 1024


class EvidenceInvalid(ValueError): pass
class EvidenceUnavailable(FileNotFoundError): pass


def need(condition, message):
    if not condition: raise EvidenceInvalid(message)


def unique_pairs(pairs):
    value={}
    for key,item in pairs:
        need(key not in value,'Duplicate JSON key: '+key); value[key]=item
    return value


def read_json(path):
    need(Path(path).stat().st_size<=MAX_JSON,'JSON artifact exceeds bound')
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),object_pairs_hook=unique_pairs)


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def sha(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'Invalid SHA-256'); return value


def exact(actual,expected,label):
    def equal(left,right):
        if type(left) is not type(right):return False
        if type(left) is dict:return left.keys()==right.keys() and all(equal(left[k],right[k]) for k in left)
        if type(left) in (list,tuple):return len(left)==len(right) and all(equal(a,b) for a,b in zip(left,right))
        return left==right
    need(equal(actual,expected),'Mismatch: '+label)


class Store:
    def __init__(self,selection):
        exact(selection.get('schemaVersion'),2,'selection schema')
        exact(selection.get('kind'),'H1SuccessorEvidenceSelection','selection kind')
        need(re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',selection.get('chainId','')),'Invalid chain identity')
        rows=selection.get('artifacts'); need(type(rows) is list and rows,'No selected artifacts')
        self.by_id={};self.by_path={};self.by_hash={};self.external={}
        for row in selection.get('notPackaged', []):
            need(type(row) is dict and type(row.get('rawPath')) is str and row['rawPath'], 'Invalid external locator')
            need(row['rawPath'] not in self.external, 'Duplicate external locator')
            sha(row.get('sha256')); need(type(row.get('sizeBytes')) is int and row['sizeBytes'] >= 0, 'Invalid external size')
            need(row.get('artifactClass') in ('NativeBinary', 'ToolchainBinary', 'InputDll', 'ResourceBinary') and
                 type(row.get('reason')) is str and row['reason'].strip(), 'External binary requires an explicit disposition')
            need(not row['rawPath'].lower().endswith(('.json','.log','.xml','.rsp','.cs','.py','.h','.cpp','.plist')), 'Required proof text cannot be excluded')
            self.external[row['rawPath']]=row
        for row in rows:
            need(type(row) is dict and re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',row.get('id','')),'Invalid artifact identity')
            need(row['id'] not in self.by_id,'Duplicate artifact ID')
            need(type(row.get('rawPath')) is str and row['rawPath'] and row['rawPath'] not in self.by_path,'Duplicate/missing capture locator')
            sha(row.get('sha256')); need(type(row.get('sizeBytes')) is int and row['sizeBytes']>=0,'Invalid size')
            need(row['rawPath'] not in self.external, 'Capture cannot be both packaged and excluded')
            local=Path(row.get('localPath',''))
            if not local.is_file(): raise EvidenceUnavailable('Unavailable capture: '+row['rawPath'])
            need(local.is_absolute() and local==local.resolve(strict=True) and not local.is_symlink(),'Noncanonical artifact file')
            need(local.stat().st_size==row['sizeBytes'] and digest(local)==row['sha256'],'Artifact bytes differ: '+row['id'])
            self.by_id[row['id']]=row; self.by_path[row['rawPath']]=row
            self.by_hash.setdefault(row['sha256'],[]).append(row)
        self.roles=selection.get('roles')
        need(type(self.roles) is dict and set(self.roles)==SINGLE_ROLES|set(MULTI_ROLES),'Mandatory successor role membership differs')
        for role in SINGLE_ROLES:
            need(type(self.roles[role]) is str and self.roles[role] in self.by_id,'Missing role artifact: '+role)
        single_ids=[self.roles[role] for role in SINGLE_ROLES]
        need(len(set(single_ids))==len(single_ids),'Different successor roles cannot alias one artifact')
        for role,count in MULTI_ROLES.items():
            ids=self.roles[role]
            need(type(ids) is list and len(ids)==count and len(set(ids))==count and all(i in self.by_id for i in ids),'Missing/duplicate role inventory: '+role)
    def row(self,role): return self.by_id[self.roles[role]]
    def read(self,role): return self.json_row(self.row(role))
    def json_row(self,row): return read_json(row['localPath'])
    def ref(self,path,hash_value=None):
        if path not in self.by_path: raise EvidenceUnavailable('Unarchived required capture locator: '+str(path))
        row=self.by_path[path]
        if hash_value is not None: exact(row['sha256'],sha(hash_value),'referenced artifact hash')
        return row
    def binary_ref(self,path,hash_value):
        """An excluded binary remains unavailable to archive-only verification."""
        if path in self.by_path: return self.ref(path,hash_value)
        if path in self.external:
            exact(self.external[path]['sha256'],sha(hash_value),'excluded binary hash declaration')
            return self.external[path]
        raise EvidenceUnavailable('Required binary has no capture or explicit exclusion: '+str(path))
    def hashed(self,hash_value):
        rows=self.by_hash.get(sha(hash_value),[])
        if not rows: raise EvidenceUnavailable('Unarchived required hash: '+hash_value)
        return rows[0]


def pins(value):
    need(type(value) is dict,'Source pin object missing')
    result={}
    for name in ('demo','hybridclr','hybridclrUnity','il2cppPlus'):
        revision=(value.get(name) or {}).get('revision')
        need(type(revision) is str and re.fullmatch('[0-9a-f]{40}',revision),'Missing exact source revision: '+name)
        result[name]=revision
    for name in ('unityVersion','target','architecture'):
        need(type(value.get(name)) is str and value[name],'Missing source environment: '+name); result[name]=value[name]
    return result


def build_pins(build):
    raw=build.get('sourcePinsJson')
    return pins(json.loads(raw,object_pairs_hook=unique_pairs) if type(raw) is str else build.get('sourcePins'))


def validate_builds(store,role,pin_role,expected_modes):
    expected=pins(store.read(pin_role)); reports={}
    for identifier in store.roles[role]:
        row=store.by_id[identifier]; build=store.json_row(row)
        exact(build.get('kind'),'H1CountDiagnosticPlayerBuild','count build kind')
        exact(build.get('schemaVersion'),1,'count build schema'); exact(build.get('diagnosticOnly'),True,'diagnostic build')
        need(type(build.get('featureEnabled')) is bool,'Feature flag is not boolean')
        mode=('On' if build['featureEnabled'] else 'Off')+'/'+str(build.get('cppConfiguration'))
        need(mode in expected_modes and mode not in reports,'Unexpected/duplicate count build mode')
        exact(build.get('baselineBuildId'),'H1Count-'+mode.replace('/','-'),'count build id')
        need(build_pins(build)==expected,'Build source pins differ from selected source chain')
        store.ref(build['compilerProvenancePath'],build['compilerProvenanceSha256'])
        store.ref(build['managedSourceProvenancePath'],build['managedSourceProvenanceSha256'])
        exact(build['sourcePinSha256'],store.row(pin_role)['sha256'],'count source-pin bytes')
        reports[mode]=(row,build)
    need(set(reports)==set(expected_modes),'Count build coverage missing')
    return reports


def validate_compiler_summary(store,role,builds):
    report=store.read(role)
    exact(report.get('kind'),'H1CompilerProvenanceVerification','compiler verifier kind')
    exact(report.get('status'),'Passed','compiler verification status')
    rows=report.get('rows'); need(type(rows) is list and len(rows)==len(builds),'Compiler result inventory differs')
    seen=set()
    for row in rows:
        mode=row.get('mode'); need(mode in builds and mode not in seen,'Duplicate/unknown compiler result mode');seen.add(mode)
        selected,build=builds[mode]
        exact(row.get('receiptPath'),selected['rawPath'],'compiler-selected build path')
        exact(row.get('receiptSha256'),selected['sha256'],'compiler-selected build hash')
        for key in ('buildGuid','nativeLibrarySha256','sourcePinSha256'):exact(row.get(key),build[key],'compiler/build '+key)
        expected=('1','0') if mode.endswith('/Debug') else ('0','1')
        need((row.get('il2cppDebug'),row.get('ndebug'))==expected,'Compiler profile attribution differs')


def validate_managed(store,role,builds):
    by_guid={b['buildGuid']:b for _,b in builds.values()};seen=set()
    for identifier in store.roles[role]:
        result=store.json_row(store.by_id[identifier])
        exact(result.get('kind'),'H1ManagedSourceGraphVerification','managed source verifier kind')
        exact(result.get('status'),'SourceGraphBound','managed source graph status')
        guid=result.get('buildGuid');need(guid in by_guid and guid not in seen,'Managed build pairing differs');seen.add(guid)
        build=by_guid[guid]
        for key in ('inputSnapshotHash','nativeLibrarySha256','sourcePinSha256'):exact(result.get(key),build[key],'managed/build '+key)
        capture=store.ref(result['capturePath'],result['captureSha256'])
        exact(capture['rawPath'],build['managedSourceProvenancePath'],'managed capture path')
        exact(capture['sha256'],build['managedSourceProvenanceSha256'],'managed capture hash')
        data=store.json_row(capture); store.ref(data['begin']['path'],data['begin']['sha256'])
        if 'reusedFrom' in result:
            previous=result['reusedFrom']; old=store.json_row(store.ref(previous['path'],previous['sha256']))
            need(old.get('kind')=='H1ManagedSourceGraphVerification' and old.get('status')=='SourceGraphBound' and
                 'reusedFrom' not in old,'Managed reuse requires a direct prior proof')
            prior=store.json_row(store.ref(previous['capturePath'],previous['captureSha256']))
            store.ref(prior['begin']['path'],prior['begin']['sha256'])
            def include_retained(value):
                if type(value) is dict:
                    if 'retainedPath' in value and 'sha256' in value:store.ref(value['retainedPath'],value['sha256'])
                    for child in value.values(): include_retained(child)
                elif type(value) is list:
                    for child in value:include_retained(child)
            include_retained(prior);include_retained(store.json_row(store.ref(prior['begin']['path'],prior['begin']['sha256'])))
        rows=result.get('rows')
        need(type(rows) is list and len(rows)==2 and {r.get('assembly') for r in rows}=={'AssemblyShadowDemo.Bootstrap','AssemblyShadow.R01BDiagnostics'},'Managed source domain coverage differs')


def validate_provenance_closure(store, builds):
    """Require raw compiler graphs, responses and retained managed-source inputs.

    Hash declarations for explicitly excluded native/toolchain binaries are
    recorded, not reinterpreted as independent verification of those bytes.
    """
    for _, build in builds.values():
        cp=store.json_row(store.ref(build['compilerProvenancePath'],build['compilerProvenanceSha256']))
        exact(cp,build.get('compilerProvenance'),'embedded compiler capture')
        for k in ('buildGuid','inputSnapshotHash','nativeLibrarySha256','sourcePinSha256'):
            exact(cp.get(k),build.get(k),'compiler raw capture binding '+k)
        for name in ('beeActionGraph','il2cppConfig','sdkSettings'):
            store.ref(cp[name+'Path'],cp[name+'Sha256'])
        for name in ('nativeLibrary','compiler'):
            store.binary_ref(cp[name+'Path'],cp[name+'Sha256'])
        responses=cp.get('responseFiles')
        need(type(responses) is list,'Native response inventory missing')
        for r in responses:
            retained=store.ref(r['retainedPath'],r['sha256'])
            exact(retained['sizeBytes'],r['bytes'],'native response size')
        validate_pch_closure(store,cp,build)
        managed=store.json_row(store.ref(build['managedSourceProvenancePath'],build['managedSourceProvenanceSha256']))
        first=managed['begin']; before=store.json_row(store.ref(first['path'],first['sha256']))
        exact(before.get('kind'),'H1ManagedSourceBegin','managed begin kind')
        exact(before.get('sourcePinSha256'),build['sourcePinSha256'],'managed begin source pins')
        def retained_rows(value):
            if type(value) is list:
                for item in value: retained_rows(item)
            elif type(value) is dict:
                if 'retainedPath' in value and 'sha256' in value:
                    r=store.ref(value['retainedPath'],value['sha256'])
                    if 'sizeBytes' in value:exact(r['sizeBytes'],value['sizeBytes'],'managed retained size')
                for child in value.values():
                    if type(child) in (dict,list):retained_rows(child)
        retained_rows(before);retained_rows(managed)


def validate_pch_closure(store, cp, build):
    """PCH artifacts are mandatory archive members, not excluded binaries."""
    graph=store.json_row(store.ref(cp['beeActionGraphPath'],cp['beeActionGraphSha256']))
    root=Path(cp.get('projectRoot') or str(Path(build.get('sourcePinFile','/ProjectSettings/pins.json')).parent.parent))
    responses={}
    for row in cp['responseFiles']:
        data=Path(store.ref(row['retainedPath'],row['sha256'])['localPath']).read_bytes()
        need(row['sourcePath'] not in responses,'Duplicate PCH response source')
        exact(len(data),row['bytes'],'PCH response bytes');responses[row['sourcePath']]=data
    if not pch.has_pch(graph,root,responses):
        need(not cp.get('pchProofPath') and not cp.get('pchProofSha256'),'PCH proof without a PCH graph')
        return
    need(type(cp.get('projectRoot')) is str and root.is_absolute(),'PCH capture needs its exact project root')
    proof=store.json_row(store.ref(cp.get('pchProofPath'),cp.get('pchProofSha256')))
    config=Path(store.ref(cp['il2cppConfigPath'],cp['il2cppConfigSha256'])['localPath']).read_text()
    def read_row(row):
        return Path(store.ref(row['retainedPath'],row['sha256'])['localPath']).read_bytes()
    exact(proof.get('compilerSha256'),cp['compilerSha256'],'PCH compiler hash')
    derived=pch.verify(proof,graph,root,Path(cp['nativeLibraryPath']),config,responses,
        pch.binding_from(cp,root,build['featureEnabled'],build['cppConfiguration']),read=read_row)
    exact(set(derived['responseSources']),set(responses),'PCH response closure')
    for key in ('compileActionCount','linkActionCount','compilerPath','sdkPath','beeLinkOutputPath','il2cppDebug','ndebug','il2cppDevelopment'):
        exact(cp.get(key),derived[key],'PCH-derived '+key)
    for producer in proof['producers']:
        for item in producer['inputs']:
            if item['kind']=='toolchain-binary': store.binary_ref(item['toolPath'],item['toolSha256'])
            elif item['kind']=='bee-sdk-marker':exact(item['sdkSettings']['sha256'],cp['sdkSettingsSha256'],'PCH SDK marker')


def validate_count_matrix(store,builds):
    matrix=store.read('count-matrix')
    exact(matrix.get('kind'),'H1CountMatrixVerification','matrix kind');exact(matrix.get('result'),'Passed','matrix result')
    rows=matrix.get('cells');need(type(rows) is list and len(rows)==132,'132 count cells are required')
    ids=[r.get('cellId') for r in rows];need(len(set(ids))==132 and set(ids)==COUNT_CELLS,'Exact count cell membership differs')
    need(matrix.get('cellCount')==132 and matrix.get('expectedCellCount')==132,'Matrix totals differ')
    run_ids=set()
    build_hashes={r['sha256'] for r,_ in builds.values()}
    for cell in rows:
        need(cell.get('buildReceiptSha256') in build_hashes,'Matrix uses an unselected count build')
        raw=store.json_row(store.hashed(cell['reportSha256']))
        exact(raw.get('schemaVersion'),2,'raw count schema; old schema-1 cannot substitute')
        exact(raw.get('result'),'Passed','raw candidate count result')
        family,case,path,cpp=cell['cellId'].split('/')
        selected_mode=('Off' if path=='Ordinary-OFF' else 'On')+'/'+cpp
        exact(cell['buildReceiptSha256'],builds[selected_mode][0]['sha256'],'count cell compiler/feature build')
        exact(raw.get('family'),family,'raw count family');exact(raw.get('caseId'),case,'raw count case')
        need(type(cell.get('runId')) is str and cell['runId'] not in run_ids,'Duplicate/missing count run identity');run_ids.add(cell['runId'])
        store.hashed(cell['launchReceiptSha256'])
    for ref in matrix.get('inputs',{}).values():
        if type(ref) is dict and 'path' in ref and 'sha256' in ref:store.ref(ref['path'],ref['sha256'])


def validate_startup(store):
    launch=store.read('startup-launches')
    exact(launch.get('kind'),'R01EarlyLaunches','fresh startup launch kind (a reuse audit is insufficient)')
    exact(launch.get('inputsUnchanged'),True,'startup immutable inputs')
    modes=launch.get('requestedModes');need(type(modes) is list and len(modes)==11 and set(modes)==set(STARTUP_MODES),'Exact 11 startup modes required')
    need(pins(launch.get('sourcePins'))==pins(store.read('candidate-source-pins')),'Startup source chain differs')
    for field,role in (('onBuildReceiptPath','baseline-on'),('offBuildReceiptPath','baseline-off')):
        exact(launch.get(field),store.row(role)['rawPath'],'startup baseline selection')
    on=store.read('baseline-on'); on=on.get('player',on)
    rows=launch.get('processLaunches');need(type(rows) is list and len(rows)==11,'Startup launch inventory differs')
    seen=set();processes=set()
    for row in rows:
        mode=row.get('mode');need(mode in STARTUP_MODES and mode not in seen,'Duplicate/unknown startup mode');seen.add(mode)
        for key in ('passed','inputsUnchanged'):exact(row.get(key),True,'startup '+key)
        positive=mode in ('Control','OrdinaryFirst','OrdinaryAfterReserve')
        exact(row.get('timedOut'),False,'startup timeout');exact(row.get('exitCode'),0 if positive else 1,'startup expected process exit')
        need(type(row.get('processId')) is int and row['processId']>0,'Invalid startup process id')
        identity=(row['processId'],row.get('startedAtUnix'));need(identity not in processes,'Duplicate startup process/run');processes.add(identity)
        capsule=store.ref(row['capsulePath'],row['capsuleSha256'])
        early=store.json_row(store.ref(row['earlyResultPath'],row['earlyResultSha256']))
        if positive:
            m07=store.json_row(store.ref(row['m07ResultPath'],row['m07ResultSha256']))
        else:
            exact(row.get('m07ResultPath'),'','rejected startup must not hand off to M07')
            exact(row.get('m07ResultSha256'),'','rejected startup must not fabricate an M07 hash')
        exact(early.get('kind'),'R01EarlyStartupReceipt','raw early result kind')
        exact(early.get('mode'),mode,'raw early mode');exact(early.get('processId'),row['processId'],'raw early process')
        exact(early.get('capsuleSha256'),capsule['sha256'],'raw early capsule')
        expected_early='Passed' if positive else 'PassedExpectedFailure' if mode in ('MetadataFailure','InitializerFailure') else 'PassedExpectedRejection'
        exact(early.get('result'),expected_early,'raw early bounded outcome')
        exact(early.get('callbackReturnCode'),0 if positive else 1,'raw early callback result')
        exact(early.get('error'),'','early probe unexpected error')
        if positive:
            exact(m07.get('result'),'Passed','follow-on M07 oracle')
            exact(m07.get('buildGuid'),on.get('buildGuid'),'startup build pairing')
        # Guard/failure modes may intentionally reject inside the early callback.
        # Their safety semantics are owned by the existing strict R01 verifier.
        for path_key,hash_key in (('logPath','logSha256'),('consolePath','consoleSha256')):
            store.ref(row[path_key],row[hash_key])
    # All immutable input locators referenced by the launch must be accounted.
    exact(launch.get('inputHashesBefore'),launch.get('inputHashesAfter'),'startup input before/after hashes')
    need(type(launch.get('inputHashesBefore')) is dict,'Missing startup input hashes')
    # Full inputs can include explicitly external native binaries. This archive
    # records those hashes but does not silently certify excluded binary bytes.
    check=store.read('startup-verification')
    need(type(check) is dict,'Startup strict verification artifact missing')
    exact(check.get('kind'),'R01EarlyVerification','startup strict verifier kind')
    exact(check.get('result'),'PassedBoundedProfile','startup strict bounded result')
    exact(check.get('launchReceipt'),store.row('startup-launches')['rawPath'],'strict startup launch selection')
    exact(check.get('launchReceiptSha256'),store.row('startup-launches')['sha256'],'strict startup launch bytes')
    need(pins(check.get('sourcePins'))==pins(launch['sourcePins']),'Strict startup source pins differ')
    need(type(check.get('modes')) is list and len(check['modes'])==11 and
         {r.get('mode') for r in check['modes']}==set(STARTUP_MODES) and
         all(r.get('diagnosticProfileComplete') is True for r in check['modes']),'Strict startup mode coverage differs')
    return {'modes':11,'launchSha256':store.row('startup-launches')['sha256']}


def validate_reproduction(store,builds):
    value=store.read('reproduction-execution')
    exact(value.get('kind'),'H1UnfixedReproductionExecution','reproduction kind')
    exact(value.get('candidateAcceptance'),False,'reproduction is not candidate acceptance')
    exact(value.get('freshProcessPerCell'),True,'reproduction process freshness')
    rows=value.get('cells');need(type(rows) is list and len(rows)==8,'Eight unfixed reproduction cells required')
    ids={(r.get('family'),r.get('caseId'),r.get('cppConfiguration')) for r in rows}
    need(ids==REPRO_CELLS,'Reproduction cell membership differs')
    exact(value.get('sourcePinSha256'),store.row('reproduction-source-pins')['sha256'],'reproduction source pin bytes')
    for cpp in ('Debug','Release'):
        selected,_=builds['On/'+cpp]; ref=value['builds'][cpp]
        exact(ref['receipt'],selected['rawPath'],'reproduction build path');exact(ref['receiptSha256'],selected['sha256'],'reproduction build hash')
    classifications=[]
    for cell in rows:
        exact(cell.get('inputsUnchanged'),True,'reproduction input retention')
        raw_launch=store.json_row(store.ref(cell['rawLaunchPath']))
        expected='AssertAbort' if cell['family']=='nested' and cell['cppConfiguration']=='Debug' else 'UnexpectedAccepted'
        exact(cell.get('classification'),expected,'unfixed counterexample classification');classifications.append(expected)
        if expected=='AssertAbort':
            exact(cell.get('crashed'),True,'assertion termination');exact(cell.get('launcherExitCode'),-6,'assertion SIGABRT')
            log=Path(store.ref(cell['rawUnityLogPath'])['localPath']).read_text(encoding='utf-8',errors='replace')
            need('Assertion failed' in log and 'nested_type_count' in log and 'SIGABRT' in log,'Missing actual nested-count assertion log')
            # The missing managed result is expected after SIGABRT, not an archive omission.
        else:
            raw=store.json_row(store.ref(cell['rawResultPath']))
            exact(raw.get('caseId'),cell['caseId'],'unfixed raw case')
            steps=raw.get('operationSteps')
            need(type(steps) is list and len(steps)==2 and steps[0].get('operation')=='ordinary-path-selected' and
                 steps[1].get('operation')=='Assembly.Load(byte[])' and steps[1].get('success') is True and
                 steps[1].get('code')=='Success','UnexpectedAccepted requires actual target Assembly.Load success, not an exception string')
            # Preserve Failed/ProbeFailure: the fixed-candidate oracle failing on
            # an unfixed build is not a candidate PASS and must not be rewritten.
            need(raw.get('result')!='Passed','Unfixed acceptance cannot be relabeled candidate PASS')
    return {'cells':8,'unexpectedAccepted':classifications.count('UnexpectedAccepted'),'assertAbort':classifications.count('AssertAbort')}


def validate_selection(selection):
    store=Store(selection)
    expected_site_ids(store.read('witness-configuration'),require_current=True)
    verify_runtime_probe(store.read('witness-runtime'),store.row('witness-configuration')['sha256'])
    candidate=validate_builds(store,'candidate-count-builds','candidate-source-pins',('On/Debug','On/Release','Off/Debug','Off/Release'))
    repro=validate_builds(store,'reproduction-count-builds','reproduction-source-pins',('On/Debug','On/Release'))
    validate_compiler_summary(store,'candidate-compiler-verification',candidate)
    validate_compiler_summary(store,'reproduction-compiler-verification',repro)
    validate_managed(store,'candidate-managed-verifications',candidate);validate_managed(store,'reproduction-managed-verifications',repro)
    validate_provenance_closure(store,candidate);validate_provenance_closure(store,repro)
    validate_count_matrix(store,candidate)
    startup=validate_startup(store);reproduction=validate_reproduction(store,repro)
    return store,{'status':'SelectionBoundNotM08Acceptance','chainId':selection['chainId'],'countCells':132,
        'startup':startup,'reproduction':reproduction,'humanGatePassed':False,'mayEnterR02':False,
        'excludedBinaryCount':len(store.external),
        'scope':'Critical schema/membership and raw identity checks, not complete runtime, performance, compiler execution, or independent M08 acceptance.'}


def package(selection_path: Path, output: Path):
    selection_hash=digest(selection_path);selection=read_json(selection_path);store,summary=validate_selection(selection)
    need(output.is_absolute() and output==output.resolve() and not output.exists(),'New canonical package directory required')
    output.mkdir(parents=True)
    archive=output/'h1-successor-evidence.tar.gz';entries=[]
    # Each indexed member is an unchanged source artifact. Index stays outside
    # the archive to avoid a circular archive/index hash dependency.
    with archive.open('xb') as stream:
        import gzip
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as zipped:
            with tarfile.open(fileobj=zipped,mode='w') as tar:
                for identifier,row in sorted(store.by_id.items()):
                    path=Path(row['localPath']);member='files/'+identifier+'.bin'
                    need(digest(path)==row['sha256'] and path.stat().st_size==row['sizeBytes'],'Artifact changed before packaging')
                    info=tarfile.TarInfo(member);info.size=row['sizeBytes'];info.mode=0o644;info.mtime=0
                    with path.open('rb') as data:tar.addfile(info,data)
                    need(digest(path)==row['sha256'],'Artifact changed during packaging')
                    entries.append({'id':identifier,'rawPath':row['rawPath'],'archiveMember':member,'sha256':row['sha256'],'sizeBytes':row['sizeBytes']})
    need(digest(selection_path)==selection_hash,'Selection changed while packaging')
    index={'schemaVersion':2,'kind':'H1SuccessorEvidenceIndex','chainId':selection['chainId'],
        'archiveSha256':digest(archive),'archiveSizeBytes':archive.stat().st_size,'selectionSha256':selection_hash,
        'roles':selection['roles'],'files':entries,'summary':summary,
        'notPackaged':selection.get('notPackaged',[]),'humanGatePassed':False,'mayEnterR02':False}
    index_path=output/'evidence-index.json'
    with index_path.open('x',encoding='utf-8') as stream:json.dump(index,stream,indent=2);stream.write('\n')
    result=audit_archive(archive,index_path,index['archiveSha256'],digest(index_path))
    (output/'archive-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def safe_member(name):
    p=PurePosixPath(name)
    return bool(name) and name != '.' and not p.is_absolute() and '\\' not in name and '..' not in p.parts and str(p)==name


def audit_archive(archive,index_path,archive_sha256,index_sha256):
    exact(digest(index_path),sha(index_sha256),'index SHA-256');exact(digest(archive),sha(archive_sha256),'archive SHA-256')
    index=read_json(index_path)
    exact(index.get('schemaVersion'),2,'index schema');exact(index.get('kind'),'H1SuccessorEvidenceIndex','index kind')
    exact(index.get('archiveSha256'),archive_sha256,'index archive digest')
    exact(index.get('archiveSizeBytes'),Path(archive).stat().st_size,'archive size')
    rows=index.get('files');need(type(rows) is list and rows,'Empty member index')
    need(all(type(r) is dict and type(r.get('archiveMember')) is str and safe_member(r['archiveMember']) and
             type(r.get('sizeBytes')) is int and r['sizeBytes'] >= 0 for r in rows),'Malformed indexed member')
    expected={r['archiveMember']:r for r in rows};need(len(expected)==len(rows),'Duplicate indexed members')
    need(len({r['id'] for r in rows})==len(rows),'Duplicate indexed artifact identities')
    need(len({r['rawPath'] for r in rows})==len(rows),'Duplicate indexed capture locators')
    seen=set();total=0
    with tarfile.open(archive,'r|gz') as tar:
        for item in tar:
            need(item.isfile() and safe_member(item.name) and item.name not in seen and item.name in expected,'Unsafe, duplicate or unindexed archive member')
            row=expected[item.name];exact(item.size,row['sizeBytes'],'member size')
            need(type(item.size) is int and item.size>=0,'Invalid member size')
            source=tar.extractfile(item);need(source is not None,'Unreadable member')
            with source:actual=hashlib.file_digest(source,'sha256').hexdigest()
            exact(actual,sha(row['sha256']),'member hash');seen.add(item.name);total+=item.size
    need(seen==set(expected),'Missing archive members')
    return {'schemaVersion':1,'kind':'H1SuccessorArchiveAudit','status':'IntegrityVerified',
        'archiveSha256':archive_sha256,'indexSha256':index_sha256,'members':len(seen),'uncompressedBytes':total,
        'runtimeAcceptanceClaim':False,'M08Passed':False,'humanGatePassed':False,'mayEnterR02':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('check');q.add_argument('--selection',type=Path,required=True)
    q=sub.add_parser('package');q.add_argument('--selection',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('audit');q.add_argument('--archive',type=Path,required=True);q.add_argument('--index',type=Path,required=True)
    q.add_argument('--archive-sha256',required=True);q.add_argument('--index-sha256',required=True)
    a=p.parse_args()
    if a.action=='check':_,result=validate_selection(read_json(a.selection))
    elif a.action=='package':result=package(a.selection,a.output)
    else:result=audit_archive(a.archive,a.index,a.archive_sha256,a.index_sha256)
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (EvidenceUnavailable,FileNotFoundError) as error:
        print(json.dumps({'status':'Blocked','reason':str(error),'humanGatePassed':False,'mayEnterR02':False}));raise SystemExit(3)
    except (EvidenceInvalid,ValueError,KeyError,OSError,tarfile.TarError) as error:
        print(json.dumps({'status':'InvalidEvidence','reason':str(error),'humanGatePassed':False,'mayEnterR02':False}));raise SystemExit(2)
