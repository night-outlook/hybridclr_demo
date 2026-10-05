"""Complete immutable compiler-policy input closure and actual guard receipts.

A declaration is not acceptance. Live proof must come from the unchanged M07
compiler gate and captured operation-bound evidence; historical replay stays so.
"""
import copy
import hashlib
import json
import re
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha

RAW = 'ProjectSettings/AssemblyShadowRawTypeAdmissions.json'
RAW_SHA = '0958d5c98ee7cdfa3662f9942687926343de95523398451c423ee5de38aa5a4c'
DEPENDENCY = 'ProjectSettings/AssemblyShadowDependencies.json'
PINS = 'ProjectSettings/AssemblyShadowSourcePins.json'
CALLSITE = 'AssemblyShadowDemo.R03CompletionExecution::OnQuit'
PROVIDER = 'AssemblyA.Implementation.Internal'
TYPE = PROVIDER + '.M06ExecutionWitness'
TARGET = TYPE + ', ' + PROVIDER
CONFIGS = (RAW, DEPENDENCY, 'ProjectSettings/AssemblyShadowExtensibilityWhitelist.json',
           'ProjectSettings/AssemblyShadowReflectionBindings.json', 'ProjectSettings/AssemblyShadowResources.json',
           'ProjectSettings/AssemblyShadowResourcesM07.json')
INPUTS = (*CONFIGS, PINS, '.r03-completion-project')
CODES = dict(zip(['R%02d'%i for i in range(1,9)], ['Success','MissingRawAdmissionEvidence','RawAdmissionMethodHashMismatch',
    'RawAdmissionOperationMismatch','RawAdmissionProviderIdentityMismatch','RawAdmissionCompilerModeMissing','RawAdmissionConsumerMissing','InvalidRawAdmissionMethodVariants']))
CODES.update({'B%02d'%i:'Approved' if i==1 else 'Rejected' for i in range(1,9)})


def regular(path):
    path = Path(path)
    require(path.is_file() and not any(p.is_symlink() for p in (path,*path.parents)), 'Regular compiler-policy file: '+str(path))
    return path


def validate_inputs(project):
    project = Path(project)
    rows = [{'path':p,'sha256':sha(regular(project/p))} for p in CONFIGS]
    require(rows[0]['sha256']==RAW_SHA, 'Original raw-type operation configuration changed')
    raw=loads((project/RAW).read_text())
    require(raw['schemaVersion']==2 and raw['policy']=='assembly-shadow-raw-type-admission:2' and len(raw['sites'])==25,
            'Complete original 25-site policy required')
    entries=loads((project/DEPENDENCY).read_text())['bootstrapEntrypoints']
    chosen=[e for e in entries if e.get('callSite',e.get('method'))==CALLSITE]
    require(len(chosen)==1 and chosen[0].get('consumer')=='AssemblyShadowDemo.Bootstrap' and
        chosen[0].get('provider')==PROVIDER and chosen[0].get('typeName')==TYPE and chosen[0].get('target')==TARGET and
        chosen[0].get('reason','').strip() and chosen[0].get('method')==CALLSITE and 'callSite' not in chosen[0],
        'Exact finite supplemental bootstrap entry required')
    original=loads((project/DEPENDENCY).read_text())
    original['bootstrapEntrypoints']=[e for e in original['bootstrapEntrypoints'] if e is not chosen[0] and e.get('method')!=CALLSITE]
    require(hashlib.sha256(json.dumps(original,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='0bd51c8fd2868b9ae77e6f61f028ea50bb55a7ee6f80a85a1bd9e02c315caac9', 'Existing dependency contracts must remain unchanged')
    return rows


def verify_observation(value, project, snapshot, controls):
    project,snapshot,controls=map(Path,(project,snapshot,controls))
    require(value['kind']=='R03CompilerPolicyChecks' and value['mode']=='Development' and value['rawSha256']==RAW_SHA and
        value['dependencySha256']==sha(regular(project/DEPENDENCY)) and
        all(value[k] is False for k in ('linkedProofExecuted','runtimeAcceptance','expansionAuthorized')), 'Guard observation claim')
    snap=loads(regular(snapshot/'assembly-snapshot.json').read_text())
    require(value['snapshotSha256']==sha(snapshot/'assembly-snapshot.json'), 'Exact compiler byte basis')
    files=snap['assemblies']+snap['references']; expected=[]; module_hashes={}
    for f in files:
        p=Path(f['path']);require(not p.is_absolute() and '..' not in p.parts, 'Snapshot traversal')
        path=regular(snapshot/p);require(sha(path)==f['sha256'] and f['name'] not in module_hashes,'Compiler input binding')
        expected.append({'path':str(path),'sha256':f['sha256']});module_hashes[f['name']]=f['sha256']
    require({str(p) for p in snapshot.rglob('*.dll')}=={r['path'] for r in expected}, 'Unexpected compiler DLL')
    require(value['moduleFiles']==expected, 'Complete actual compiler inventory')
    raw=loads((project/RAW).read_text());sites={s['id']:s for s in raw['sites']}
    observed=value['sites'];require([r['id'] for r in observed]==sorted(sites), 'All 25 operation identities')
    for r in observed:
        s=sites[r['id']]; v=next(v for v in s['compilerVariants'] if v['compilerMode']=='Development')
        require(r['methodSignature']==s['methodSignature'] and r['methodHash']==v['methodHash'] and
            r['operationIndex']==v['operationIndex'] and r['operationSignature']==s['operationSignature'] and
            r['providerAssemblyIdentity']==s['providerAssemblyIdentity'] and
            r['consumerAssemblyIdentity'].split(',')[0]==s['consumerAssembly'] and
            r['consumerSha256']==module_hashes[s['consumerAssembly']] and
            r['providerSha256']==module_hashes[s['providerAssemblyIdentity'].split(',')[0]], 'Exact raw operation/provider bytes')
        require(re.fullmatch('[0-9a-f]{64}',r['providerInventoryHash']), 'Provider inventory proof missing')
    require(re.fullmatch('[0-9a-f]{64}',value['onQuitMethodHash']),'Actual compiled OnQuit identity required')
    rows=value['controls'];require([r['id'] for r in rows]==list(CODES),'Exact 16 guard controls')
    dependencies=loads((project/DEPENDENCY).read_text())
    for r in rows:
        label=r['id']; p=regular(r['configurationPath']);require(p==controls/(label+'.json') and sha(p)==r['configurationSha256'],'Control file binding')
        require(r['result']=='Passed' and r['expected']==r['actual']==CODES[label], 'Guard outcome')
        if label.startswith('R'):
            expected_config=copy.deepcopy(raw)
            if label=='R02':expected_config=None
            if label=='R03':
                method=expected_config['sites'][0]['methodSignature']
                for s in expected_config['sites']:
                    if s['methodSignature']==method:
                        next(v for v in s['compilerVariants'] if v['compilerMode']=='Development')['methodHash']='0'*64
            if label=='R04':expected_config['sites'][0]['compilerVariants'][0]['operationIndex']=100000
            if label=='R05':expected_config['sites'][0]['providerAssemblyIdentity']='AssemblyA.Contracts, Version=9.0.0.0, Culture=neutral, PublicKeyToken=null'
            if label=='R08':expected_config['sites'][0]['compilerVariants'].pop(1)
            require(r['operation']=='RawTypeAdmissionVerifier.Verify' and
                (r['mode'] or None)==(None if label=='R06' else 'Development') and
                (r['omittedModule'] or None)==('AssemblyShadowDemo.Bootstrap' if label=='R07' else None),'Exact raw control operation')
        else:
            expected_config=copy.deepcopy(dependencies)
            entry=next(e for e in expected_config['bootstrapEntrypoints'] if e.get('method')==CALLSITE)
            if label=='B02':expected_config['bootstrapEntrypoints'].remove(entry)
            fields={'B03':('method',CALLSITE+'Wrong'),'B04':('provider','AssemblyA.Contracts'),'B05':('typeName',TYPE+'Wrong'),
                    'B06':('target',TARGET+'Wrong'),'B07':('consumer','Other.Bootstrap'),'B08':('reason','')}
            if label in fields:field,val=fields[label];entry[field]=val
            require(r['operation']=='BootstrapIsolationRule.IsApprovedReflection' and not r['mode'] and not r['omittedModule'],'Exact bootstrap operation')
        require(loads(p.read_text())==expected_config,'Guard control mutation differs')
    require({p.name for p in controls.iterdir()}=={k+'.json' for k in CODES}|{'observation.json'},'Exact guard control files')
    require(loads(regular(controls/'observation.json').read_text())==value,'Independent observation receipt differs')
    return {'guardControls':16,'rawSites':25,'moduleFiles':len(expected),'runtimeAcceptance':False}


def verify_report(path,batch,project):
    project=Path(project);config=batch.resource_config;root=Path(config['receiptRoot']);path=regular(path)
    require(path==root/'compiler-policy-contract.json','Exact live compiler contract')
    r=loads(path.read_text());require(r['kind']=='R03ActualCompilerPolicyContract' and r['schemaVersion']==1 and r['result']=='Passed' and
        r['projectPath']==str(project) and r['baselineId']==config['baselineId'] and r['unityVersion']=='2022.3.62f2' and
        r['target']=='StandaloneOSX' and r['architecture']=='arm64' and r['unityEditorRun'] is True and
        r['originalCompilerPolicyPassed'] is True and r['capturedRawProofVerified'] is True and
        all(r[k] is False for k in ('linkedProofExecuted','runtimeAcceptance','expansionAuthorized','R03Accepted','H2Passed')), 'Actual non-authorizing compiler proof')
    expected=[{'path':p,'sha256':sha(regular(project/p))} for p in INPUTS]
    require(r['before']==r['after']==expected,'Immutable compiler policy inputs changed')
    snapshot=Path(r['snapshot']);require(snapshot.parent.parent==project/'_temp/AssemblyShadow' and snapshot.parent.name.startswith('M07CompilerPreflight-') and snapshot.name=='Snapshot','Exact current compiler root')
    require(sha(regular(snapshot/'assembly-snapshot.json'))==r['snapshotSha256'],'Snapshot receipt hash')
    snap=loads((snapshot/'assembly-snapshot.json').read_text())
    require(snap['kind']=='CompilePlayerScripts' and snap['playerBuildSucceeded'] is False and
        snap['sourcePins']==loads((project/PINS).read_text()) and
        'ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_'+RAW_SHA in snap['extraScriptingDefines'],'Actual controlled compiler source tuple')
    require(sha(regular(snapshot/'RawTypeAdmissions/configuration.json'))==RAW_SHA and
        sha(regular(snapshot/'RawTypeAdmissions/compiled-evidence.json'))==r['compiledProofSha256'],'Captured raw proof binding')
    proof=loads((snapshot/'RawTypeAdmissions/compiled-evidence.json').read_text())
    require(proof['phase']=='Compiled' and proof['configurationSha256']==RAW_SHA and not proof['buildGuid'] and
        [s['id'] for s in proof['sites']]==[s['id'] for s in r['observation']['sites']], 'No omitted raw proof or linked claim')
    for p,s in zip(proof['sites'],r['observation']['sites']):
        require(all(p[k]==s[k] for k in ('consumerAssemblyIdentity','consumerSha256','providerAssemblyIdentity','providerSha256','providerInventoryHash','methodSignature','operationIndex','operationSignature')) and p['compiledMethodHash']==s['methodHash'],'Captured/recomputed raw proof differs')
    checked=verify_observation(r['observation'],project,snapshot,root/'compiler-policy-controls')
    return dict(checked,kind=r['kind'],result='Passed',receipt=str(path),sha256=sha(path),capturedRawProofVerified=True)
