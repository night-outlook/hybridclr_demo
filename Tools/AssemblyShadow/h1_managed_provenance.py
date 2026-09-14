"""Source-before-build ledger and managed Bee-action-to-Player-input binding.

Run begin BEFORE BuildPipeline.BuildPlayer and end after the existing linked
input capture has succeeded. Missing managed DAG coverage is recorded as
Blocked, not repaired by hashing today's sources against an old executable.
This tool does not approve H1 or replace the production ILPP/linked verifier.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

import h1_compiler_actions as actions
from h1_native_capture import read_json, digest, write_new, unique_pairs

REQUIRED_ASSEMBLIES = frozenset(('AssemblyShadowDemo.Bootstrap', 'AssemblyShadow.R01BDiagnostics'))


def logical(root: Path, value: str) -> Path:
    return Path(actions.resolve(root, value))


def retain(path: Path, root: Path, category: str) -> dict:
    original = Path(os.path.abspath(path))
    path = path.resolve(strict=True)
    actions.need(path.is_file(), 'Missing regular input: ' + str(path))
    before = digest(path); size = path.stat().st_size
    destination = root / category / (before + '.bin')
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with path.open('rb') as source, destination.open('xb') as output:
            for data in iter(lambda: source.read(1024 * 1024), b''): output.write(data)
            output.flush(); os.fsync(output.fileno())
    actions.need(digest(destination) == before and digest(path) == before and path.stat().st_size == size,
                 'Input changed during capture: ' + str(path))
    return {'path': str(path), 'logicalPath': str(original), 'retainedPath': str(destination), 'sha256': before, 'sizeBytes': size}


def verify_retained(row: dict) -> Path:
    p=Path(row['retainedPath'])
    actions.need(p.is_absolute() and p == p.resolve(strict=True) and not p.is_symlink() and p.is_file(), 'Retained file is not canonical')
    actions.need(type(row.get('sizeBytes')) is int and p.stat().st_size == row['sizeBytes'] and digest(p) == row['sha256'],
                 'Retained managed input bytes differ: ' + str(p))
    return p


def begin(request: dict, output: Path) -> dict:
    root = Path(request['projectRoot']).resolve(strict=True)
    actions.need(root.is_dir() and output.is_absolute() and not output.exists() and output == output.resolve(), 'New canonical evidence root required')
    extra=request.get('extraScriptingDefines', [])
    actions.need(type(extra) is list and all(type(v) is str for v in extra) and len(extra)==len(set(extra)), 'Invalid extra compiler defines')
    assemblies=request.get('assemblies')
    actions.need(type(assemblies) is list and len(assemblies) == len(REQUIRED_ASSEMBLIES) and
                 {a.get('name') for a in assemblies} == REQUIRED_ASSEMBLIES, 'Both diagnostic managed source domains are required')
    for a in assemblies:
        actions.need(type(a.get('sourceFiles')) is list and a['sourceFiles'] and
                     all(type(p) is str and p.endswith('.cs') for p in a['sourceFiles']), 'Managed source list is empty/invalid')
        actions.need(type(a.get('defines')) is list and type(a.get('referenceFiles')) is list, 'Compiler source plan is incomplete')
    paths = set()
    for a in assemblies:
        paths.update(logical(root,p) for p in a['sourceFiles'])
    # The orchestration and exact configuration are part of source provenance,
    # not included in the declaration that they are compiled into the Player.
    orchestration = list((root / 'Assets/AssemblyShadowDemo/Editor').glob('*.cs'))
    orchestration += list((root / 'Tools/AssemblyShadow').glob('*.py'))
    paths.update(orchestration)
    for name in ('ProjectSettings/AssemblyShadowSourcePins.json', 'ProjectSettings/AssemblyShadowReflectionBindings.json',
                 'Packages/manifest.json', 'Packages/packages-lock.json'):
        p=root/name
        if p.exists(): paths.add(p)
    for pattern in ('*.asmdef','*.asmref'):
        paths.update((root/'Assets').rglob(pattern))
    paths.update(Path(str(p)+'.meta') for p in tuple(paths) if Path(str(p)+'.meta').is_file())
    actions.need(len(paths) <= 100000, 'Source ledger exceeds bound')
    # Pre-existing cache outputs distinguish newly produced compiler outputs
    # from reused ones. Existing outputs are not deleted to manufacture freshness.
    bee=root/'Library/Bee'
    existing=sorted(str(p.resolve()) for p in bee.rglob('*.dll')) if bee.is_dir() else []
    graph_before={str(p.resolve()):digest(p) for p in bee.glob('*.dag.json')} if bee.is_dir() else {}
    output.mkdir(parents=True)
    rows=[]
    for path in sorted(paths):
        row=retain(path,output,'sources'); row['logicalPath']=str(path); rows.append(row)
    pins=logical(root,request['sourcePinFile'])
    record={'schemaVersion':1,'kind':'H1ManagedSourceBegin','projectRoot':str(root),
        'buildId':request['buildId'], 'sourcePinSha256':digest(pins), 'assemblies':assemblies, 'extraScriptingDefines':extra,
        'sources':rows,'preExistingBeeDlls':existing,'beeGraphsBefore':graph_before,
        'sourceToBinaryVerified':False}
    write_new(output/'begin.json',(json.dumps(record,indent=2)+'\n').encode())
    return record


def csc_arguments(action: str, root: Path, responses: dict[str, bytes]) -> dict | None:
    tokens=actions.split(action)
    arguments, used=actions.expand(tokens,root,responses)
    csc_positions=[i for i,a in enumerate(arguments) if Path(a).name.lower() in ('csc.dll','csc.exe','csc')]
    if not csc_positions: return None
    actions.need(len(csc_positions)==1,'Ambiguous managed compiler')
    source=[]; references=[]; tools=[arguments[0],arguments[csc_positions[0]]]; outputs=[]; defines=[]
    prefixes=('/reference:', '-reference:', '/r:', '-r:', '/analyzer:', '-analyzer:',
              '/additionalfile:', '-additionalfile:', '/analyzerconfig:', '-analyzerconfig:',
              '/ruleset:', '-ruleset:', '/keyfile:', '-keyfile:', '/win32res:', '-win32res:', '/embed:', '-embed:')
    for a in arguments[csc_positions[0]+1:]:
        low=a.lower()
        if low.startswith(('/recurse:', '-recurse:', '/lib:', '-lib:')):
            raise actions.CompilerActionError('Implicit managed compiler input search is not supported')
        if low.endswith('.cs') and re.match(r'^[-/][A-Za-z]+:', a) is None:
            source.append(str(logical(root,a)))
        elif low.startswith(('/out:','-out:')): outputs.append(str(logical(root,a.split(':',1)[1])))
        elif low.startswith(('/define:', '-define:', '/d:', '-d:')): defines.append(a.split(':',1)[1])
        elif low.startswith(prefixes):
            value=a.split(':',1)[1]
            if low.startswith(('/reference:', '-reference:', '/r:', '-r:')) and '=' in value:
                alias, candidate=value.split('=',1)
                if re.fullmatch(r'[A-Za-z_][\w]*(?:,[A-Za-z_][\w]*)*',alias): value=candidate
            actions.need(',' not in value, 'Combined compiler input lists require explicit expansion')
            references.append(str(logical(root,value)))
        elif low.startswith(('/recurse:', '-recurse:', '/lib:', '-lib:')):
            raise actions.CompilerActionError('Implicit managed compiler input search is not supported')
    actions.need(source and len(source)==len(set(source)) and len(outputs)==1,'Incomplete/duplicate Csc source or output inventory')
    tools=[str(logical(root,p)) for p in tools]
    return {'sourcePaths':sorted(source),'dependencyPaths':sorted(set(references+tools)),
            'output':outputs[0],'defines':defines,'responseSources':sorted(used)}


def collect_managed_responses(graph: dict, root: Path) -> dict[str,bytes]:
    result={}
    def visit(tokens,active=()):
        actions.need(len(active)<=actions.MAX_RESPONSE_DEPTH,'Managed response nesting exceeds bound')
        for token in tokens:
            if not token.startswith('@'): continue
            path=str(logical(root,token[1:]))
            actions.need(path not in active,'Managed response cycle')
            if path in result: continue
            data=Path(path).read_bytes()
            actions.need(len(data)<=actions.MAX_RESPONSE_BYTES and len(result)<16384,'Managed response inventory exceeds bound')
            result[path]=data; text=data.decode('utf-8-sig')
            visit(actions.split(text) if text.strip() else [],active+(path,))
    for node in graph.get('Nodes',[]):
        if type(node) is dict and node.get('Action') and ('csc' in node['Action'].lower()):
            visit(actions.split(node['Action']))
    return result


def reaches(nodes, root, start: str, target: str) -> bool:
    reached={start}
    while target not in reached:
        new=set()
        for node in nodes:
            if type(node) is not dict: continue
            inputs={str(logical(root,p)) for p in node.get('Inputs',[])}
            if inputs & reached: new.update(str(logical(root,p)) for p in node.get('Outputs',[]))
        if new <= reached: return False
        reached.update(new)
    return True


def end(request: dict, evidence_root: Path) -> dict:
    before_path=evidence_root/'begin.json'; before=read_json(before_path)
    actions.need(before.get('kind')=='H1ManagedSourceBegin','Source begin ledger missing')
    root=Path(before['projectRoot'])
    actions.need(request['buildId']==before['buildId'] and request['sourcePinSha256']==before['sourcePinSha256'], 'Build source identity changed')
    for row in before['sources']:
        verify_retained(row)
        actions.need(str(Path(row['logicalPath']).resolve(strict=True))==row['path'] and digest(Path(row['path']))==row['sha256'],
                     'Managed source/configuration changed during build: '+row['path'])
    actual=request.get('actualInputs')
    actions.need(type(actual) is list and len(actual)==2 and {row['name'] for row in actual}==REQUIRED_ASSEMBLIES,
                 'Actual filtered Player input domain differs')
    input_rows=[]
    for row in actual:
        path=Path(row['retainedPath'])
        actions.need(digest(path)==row['sha256'] and digest(Path(row['sourcePath']))==row['sha256'], 'Actual Player input changed')
        item=retain(path,evidence_root,'actual-inputs'); item.update(name=row['name'],sourcePath=str(Path(row['sourcePath']).resolve()))
        input_rows.append(item)
    wanted_sources = {frozenset(str(logical(root,p)) for p in a['sourceFiles']) for a in before['assemblies']}
    graph_rows=[]; problems=[]
    for path in sorted((root/'Library/Bee').glob('*.dag.json')):
        if before['beeGraphsBefore'].get(str(path.resolve()))==digest(path): continue
        graph=read_json(path)
        if not any(type(n) is dict and 'csc' in str(n.get('Action','')).lower() for n in graph.get('Nodes',[])): continue
        record=retain(path,evidence_root,'managed-graphs')
        try:
            responses=collect_managed_responses(graph,root)
            response_rows=[]; parsed=[]
            for p,data in sorted(responses.items()):
                rr=retain(Path(p),evidence_root,'managed-responses'); rr['sourcePath']=p; response_rows.append(rr)
            for index,node in enumerate(graph.get('Nodes',[])):
                if type(node) is not dict or 'csc' not in str(node.get('Action','')).lower(): continue
                item=csc_arguments(node['Action'],root,responses)
                if item and frozenset(item['sourcePaths']) in wanted_sources:
                    item['nodeIndex']=index
                    item['dependencies']=[retain(Path(p),evidence_root,'compiler-inputs') for p in item['dependencyPaths']]
                    if Path(item['output']).is_file(): item['compilerOutput']=retain(Path(item['output']),evidence_root,'compiler-outputs')
                    parsed.append(item)
            record.update(responseFiles=response_rows,compilations=parsed)
        except (OSError,ValueError) as error:
            record['captureError']=str(error); problems.append(str(error))
        graph_rows.append(record)
    record={'schemaVersion':1,'kind':'H1ManagedSourceCapture','status':'CapturedAwaitingIndependentGraphCheck',
        'begin':{'path':str(before_path),'sha256':digest(before_path),'sizeBytes':before_path.stat().st_size},
        'buildId':request['buildId'],'buildGuid':request['buildGuid'],'inputSnapshotHash':request['inputSnapshotHash'],
        'nativeLibrarySha256':request['nativeLibrarySha256'],'sourcePinSha256':request['sourcePinSha256'],
        'actualInputs':input_rows,'graphs':graph_rows,'captureProblems':problems,
        'sourceToBinaryVerified':False,'humanGatePassed':False,'mayEnterR02':False}
    write_new(evidence_root/'h1-managed-source-capture.json',(json.dumps(record,indent=2)+'\n').encode())
    return record


def verify(path: Path) -> dict:
    value=read_json(path); ref=value['begin']; before_path=Path(ref['path'])
    actions.need(value.get('kind')=='H1ManagedSourceCapture' and digest(before_path)==ref['sha256'] and before_path.stat().st_size==ref['sizeBytes'], 'Begin ledger differs')
    before=read_json(before_path); root=Path(before['projectRoot'])
    actions.need(value['buildId']==before['buildId'] and value['sourcePinSha256']==before['sourcePinSha256'], 'Source capture binding differs')
    sources={row['logicalPath']:row for row in before['sources']}
    actions.need(len(sources)==len(before['sources']), 'Duplicate managed source rows')
    for row in sources.values(): verify_retained(row)
    actions.need(not value.get('captureProblems'), 'Managed graph capture has unresolved problems')
    expected={a['name']:{str(logical(root,p)) for p in a['sourceFiles']} for a in before['assemblies']}
    inputs=value['actualInputs']
    actions.need(len(inputs)==2 and {r['name'] for r in inputs}==REQUIRED_ASSEMBLIES,'Actual managed input membership differs')
    rows=[]
    for target in inputs:
        verify_retained(target); matches=[]
        for graph_row in value['graphs']:
            graph=read_json(verify_retained(graph_row)); response_data={}
            for r in graph_row['responseFiles']:
                actions.need(r['sourcePath'] not in response_data,'Duplicate retained managed response')
                response_data[r['sourcePath']]=verify_retained(r).read_bytes()
            for compiled in graph_row['compilations']:
                node=graph['Nodes'][compiled['nodeIndex']]
                parsed=csc_arguments(node['Action'],root,response_data)
                if not parsed or set(parsed['sourcePaths'])!=expected[target['name']]: continue
                for k in ('sourcePaths','dependencyPaths','output','defines','responseSources'):
                    actions.need(parsed[k]==compiled[k],'Managed compiler transcript differs: '+k)
                actual_defines = {v for definition in parsed['defines'] for v in re.split('[;,]', definition) if v}
                actions.need(set(before.get('extraScriptingDefines', [])) <= actual_defines and 'UNITY_EDITOR' not in actual_defines,
                             'Required Player compiler defines differ or Editor output selected')
                actions.need(all(p in sources for p in parsed['sourcePaths']), 'Compiled source was not captured before build')
                deps={r['logicalPath']:r for r in compiled['dependencies']}
                actions.need(set(deps)==set(parsed['dependencyPaths']) and len(deps)==len(compiled['dependencies']), 'Compiler dependency closure differs')
                for dep in deps.values(): verify_retained(dep)
                actions.need('compilerOutput' in compiled, 'Managed compiler output was not retained')
                verify_retained(compiled['compilerOutput'])
                actions.need(compiled['compilerOutput']['logicalPath']==parsed['output'], 'Compiler output location differs')
                if reaches(graph['Nodes'],root,parsed['output'],target['sourcePath']):
                    matches.append({'assembly':target['name'],'graphSha256':graph_row['sha256'],
                        'compilerOutputSha256':compiled['compilerOutput']['sha256'],'playerInputSha256':target['sha256'],
                        'compilerOutputExistedBeforeBuild':parsed['output'] in before['preExistingBeeDlls']})
        actions.need(len(matches)==1,'Missing or ambiguous managed action chain for '+target['name'])
        rows.extend(matches)
    # This is intentionally narrower than independent M08 or fresh execution proof.
    return {'schemaVersion':1,'kind':'H1ManagedSourceGraphVerification','status':'SourceGraphBound',
        'capturePath':str(path),'captureSha256':digest(path),'buildId':value['buildId'],'buildGuid':value['buildGuid'],
        'inputSnapshotHash':value['inputSnapshotHash'],'nativeLibrarySha256':value['nativeLibrarySha256'],
        'sourcePinSha256':value['sourcePinSha256'],'rows':rows,
        'scope':'Pre-build source bytes, retained compiler/dependency/response graph, and actual Player-input binding. Existing ILPP verification and build execution provenance remain separate requirements.',
        'freshCompilerExecutionClaim':False,'humanGatePassed':False,'mayEnterR02':False}



def verify_exact_reuse(path: Path, prior_proof_path: Path) -> dict:
    """Explicit reuse of independently rechecked, byte-identical managed inputs.

    This does not retrofit provenance onto an old unproven build. A complete
    earlier direct graph proof is required and reverified from retained bytes.
    A later native build may bind that same managed source/DLL identity without
    pretending its managed compiler ran again. No automatic fallback occurs.
    """
    proof=read_json(prior_proof_path)
    actions.need(proof.get('kind')=='H1ManagedSourceGraphVerification' and proof.get('status')=='SourceGraphBound'
                 and 'reusedFrom' not in proof, 'A direct prior graph proof is required; reuse chains are not accepted')
    prior_path=Path(proof['capturePath'])
    actions.need(digest(prior_path)==proof['captureSha256'],'Prior managed capture differs')
    actions.need(proof==verify(prior_path),'Prior managed graph verification cannot be independently reproduced')
    prior=read_json(prior_path);prior_begin=read_json(Path(prior['begin']['path']))
    current=read_json(path);ref=current['begin'];begin_path=Path(ref['path'])
    actions.need(current.get('kind')=='H1ManagedSourceCapture' and digest(begin_path)==ref['sha256'] and
                 begin_path.stat().st_size==ref['sizeBytes'],'Current source-begin binding differs')
    current_begin=read_json(begin_path)
    actions.need(current['buildId']==current_begin['buildId'] and
                 current['sourcePinSha256']==current_begin['sourcePinSha256']==prior['sourcePinSha256'],
                 'Current/prior source pin identity differs')
    for field in ('projectRoot','assemblies','extraScriptingDefines'):
        actions.need(current_begin.get(field)==prior_begin.get(field),'Managed reuse source plan differs: '+field)
    def source_map(value):
        rows=value['sources']; result={}
        for row in rows:
            verify_retained(row)
            actions.need(row['logicalPath'] not in result,'Duplicate source identity in reuse')
            result[row['logicalPath']]=(row['sha256'],row['sizeBytes'])
        return result
    actions.need(source_map(current_begin)==source_map(prior_begin),'Managed reuse source/configuration bytes differ')
    def input_map(value):
        result={}
        for row in value['actualInputs']:
            verify_retained(row);actions.need(row['name'] not in result,'Duplicate managed input in reuse')
            result[row['name']]=(row['sha256'],row['sizeBytes'])
        actions.need(set(result)==REQUIRED_ASSEMBLIES,'Managed reuse input domain differs')
        return result
    actions.need(input_map(current)==input_map(prior),'Actual Player DLLs differ from the proven prior managed compilation')
    return {'schemaVersion':1,'kind':'H1ManagedSourceGraphVerification','status':'SourceGraphBound',
        'capturePath':str(path),'captureSha256':digest(path),'buildId':current['buildId'],'buildGuid':current['buildGuid'],
        'inputSnapshotHash':current['inputSnapshotHash'],'nativeLibrarySha256':current['nativeLibrarySha256'],
        'sourcePinSha256':current['sourcePinSha256'],'rows':proof['rows'],
        'reusedFrom':{'path':str(prior_proof_path),'sha256':digest(prior_proof_path),
                     'capturePath':str(prior_path),'captureSha256':digest(prior_path)},
        'scope':'Explicit reuse of a reverified direct managed graph proof with identical source/configuration/defines and actual Player DLL bytes. Current native execution remains a separate proof.',
        'freshCompilerExecutionClaim':False,'humanGatePassed':False,'mayEnterR02':False}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('action',choices=('begin','end','verify'))
    p.add_argument('--reuse-proof',type=Path,help='Explicit direct prior managed graph proof; never an automatic fallback')
    p.add_argument('--request',type=Path); p.add_argument('--evidence-root',type=Path); p.add_argument('--capture',type=Path); p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.action=='verify':
        actions.need(a.capture is not None and a.output is not None,'verify requires capture and new output')
        report=verify_exact_reuse(a.capture,a.reuse_proof) if a.reuse_proof else verify(a.capture); write_new(a.output,(json.dumps(report,indent=2)+'\n').encode())
    else:
        actions.need(a.request is not None and a.evidence_root is not None,'Capture requires request and evidence-root')
        report=(begin if a.action=='begin' else end)(read_json(a.request),a.evidence_root)
    print(json.dumps({'kind':report['kind'],'status':report.get('status','SourceBeginCaptured'),'humanGatePassed':False,'mayEnterR02':False})); return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except (OSError,ValueError,KeyError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr); raise SystemExit(1)
