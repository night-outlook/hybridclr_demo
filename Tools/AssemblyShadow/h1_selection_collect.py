"""Collect a successor selection from explicit roles and immutable references.

No 'latest' directory selection, remote fetching, path rewriting in receipts,
acceptance inference, or automatic binary exclusion. An explicit locator map
resolves transferred external-artifact:// references to local files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import h1_successor_evidence as evidence


def refs(value):
    """Known receipt reference shapes; return locators without altering bytes."""
    if type(value) is list:
        for item in value: yield from refs(item)
    elif type(value) is dict:
        # A retained source's original path is a capture locator, not a request
        # to hash mutable live source again in place of its retained bytes.
        if 'sha256' in value:
            key='retainedPath' if 'retainedPath' in value else 'path'
            if type(value.get(key)) is str:yield value[key],value['sha256']
        for key,item in value.items():
            if type(item) is str and key.endswith('Path') and key not in ('retainedPath','rawPath'):
                hash_key=key[:-4]+'Sha256'
                if hash_key in value:yield item,value[hash_key]
            if key=='sourcePinFile' and 'sourcePinSha256' in value:yield item,value['sourcePinSha256']
            if key in ('inputHashesBefore','inputHashesAfter') and type(item) is dict:
                for locator,digest in item.items():yield locator,digest
            if type(item) in (dict,list):yield from refs(item)
        # Crash termination legitimately has no managed result. Its raw launch
        # and assertion log must still be included and verified independently.
        for key in ('rawLaunchPath','rawUnityLogPath','rawResultPath'):
            if type(value.get(key)) is str and value[key]:
                if key=='rawResultPath' and value.get('classification')=='AssertAbort' and value.get('crashed') is True:continue
                yield value[key],None
        if value.get('kind')=='H1UnfixedReproductionExecution':
            for row in value.get('builds',{}).values():
                if type(row) is dict and type(row.get('receipt')) is str:yield row['receipt'],row.get('receiptSha256')


def collect(config):
    evidence.exact(config.get('schemaVersion'),1,'collection configuration schema')
    evidence.exact(config.get('kind'),'H1SuccessorCollectionRequest','collection request kind')
    roots=config.get('allowedRoots');evidence.need(type(roots) is list and roots,'Explicit local roots are required')
    roots=[Path(p).resolve(strict=True) for p in roots]
    evidence.need(all(p.is_dir() for p in roots),'Allowed roots must be directories')
    locator_map=config.get('locatorMap',{});evidence.need(type(locator_map) is dict,'Locator map must be an object')
    external=config.get('notPackaged',[]);evidence.need(type(external) is list,'Explicit exclusions must be an array')
    excluded={r['rawPath']:r for r in external};evidence.need(len(excluded)==len(external),'Duplicate external exclusions')
    roles=config.get('roles');evidence.need(type(roles) is dict and set(roles)==evidence.SINGLE_ROLES|set(evidence.MULTI_ROLES),'Exact role paths required')
    selected={};queue=[];role_ids={}
    for role in sorted(roles):
        values=[roles[role]] if role in evidence.SINGLE_ROLES else roles[role]
        evidence.need(type(values) is list and all(type(v) is str and v for v in values),'Invalid explicit role path')
        ids=[]
        for locator in values:
            evidence.need(locator not in excluded,'Mandatory role cannot be an excluded binary')
            queue.append((locator,None));ids.append('a-'+hashlib.sha256(locator.encode()).hexdigest())
        role_ids[role]=ids[0] if role in evidence.SINGLE_ROLES else ids
    cursor=0
    while cursor<len(queue):
        evidence.need(len(queue)<=1000000 and len(selected)<=100000,'Evidence collection exceeds bound')
        locator,expected=queue[cursor];cursor+=1
        evidence.need(type(locator) is str and locator,'Empty capture locator')
        if expected is not None:evidence.sha(expected)
        if locator in excluded:
            if expected is not None:evidence.exact(excluded[locator]['sha256'],expected,'excluded hash declaration')
            continue
        if locator in selected:
            if expected is not None:evidence.exact(selected[locator]['sha256'],expected,'repeated referenced hash')
            continue
        local_value=locator_map.get(locator,locator)
        path=Path(local_value)
        if not path.is_absolute() or not path.is_file():raise evidence.EvidenceUnavailable('No local capture for '+locator)
        evidence.need(not path.is_symlink() and path==path.resolve(strict=True),'Capture must resolve to a canonical regular file')
        evidence.need(any(path.is_relative_to(root) for root in roots),'Capture outside explicit roots: '+str(path))
        digest=evidence.digest(path)
        if expected is not None:evidence.exact(digest,expected,'captured reference bytes')
        row={'id':'a-'+hashlib.sha256(locator.encode()).hexdigest(),'rawPath':locator,'localPath':str(path),'sha256':digest,'sizeBytes':path.stat().st_size}
        selected[locator]=row
        # Do not parse arbitrary source files or binary payloads as JSON.
        if locator.lower().endswith('.json') or path.suffix.lower()=='.json':
            value=evidence.read_json(path);queue.extend(refs(value))
            evidence.exact(evidence.digest(path),digest,'JSON changed during dependency collection')
    result={'schemaVersion':2,'kind':'H1SuccessorEvidenceSelection','chainId':config['chainId'],
        'roles':role_ids,'artifacts':sorted(selected.values(),key=lambda r:r['id']),'notPackaged':external}
    # Structural/index checks only; semantic selection check is a separate step.
    evidence.Store(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();before=evidence.digest(a.request);result=collect(evidence.read_json(a.request))
    evidence.need(a.output.is_absolute() and a.output==a.output.resolve() and not a.output.exists(),'New canonical output required')
    evidence.exact(evidence.digest(a.request),before,'collection request changed')
    with a.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':'CollectedNotAccepted','artifacts':len(result['artifacts']),'output':str(a.output),'humanGatePassed':False,'mayEnterR02':False}))
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError) as error:
        print('Blocked: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
