#!/usr/bin/env python3
"""Read-only E preservation. Does NOT accept E runtime or restore S custody.

Authenticates original E Git objects, 999 indexed files, and three 972-file
native inventories. An additional before/after snapshot preserves unindexed E
files as CURRENT snapshots, not retrospectively authenticated build inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

PUBLICATION='75500e3916300d1fd5f7774e0f9de33b9ed3e7da'
CHECKPOINT='Docs/AssemblyShadow/History/M07R/R03/local-validation-20261010-ir-r03-02-e-native-receipt'
BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
BATCH=BASE/'R03IRLocal-20261010E-native-receipt'
ROOTS=(BATCH,BASE/'Preflight-R03IRLocal-20261010E-native-receipt',
       BASE/'StorageCheck-R03IRLocal-20261010E-native-receipt',
       BASE/'Storage-R03IRLocal-20261010E-native-receipt')
OBJECTS={'batch/evidence-index.json':'bfae46082370305eff3c728c3f134d789513bc47',
         'RETAINED_LIVE_ROOTS.json':'a205d30a53b97957ce1ffdbd30753e8d039314ff'}
TOP={'LOCAL_BATCH_RESULT.json':'86d7af7b811c96be9bb6dd73f70a842098de3f085f84d23b1345efdda07d89bb',
     'BATCH_EXECUTION.json':'cd32d028b2c60adadd2424ad415c72671aa6c486096ac609f03b0b183ffb7b7d',
     'evidence-index.json':'4fe2b47612446187b09658a0b8527fab236bfc56b636ad55d67f842deace3eb2',
     'evidence.tar.gz':'ae390e3d26ad0684ba54fa4f0cffc70dd5b16dd00388267b8dca557199f8c4e7',
     'seal-receipt.json':'62c734f142d616b93f02e1d8d77d483b1ecaf7c224cffac0ce97928f64aa1757'}

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        before=os.fstat(f.fileno())
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
        after=os.fstat(f.fileno())
    require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'File changed during hashing: '+str(path))
    return h.hexdigest()

def regular(path):
    for parent in (path,*path.parents):require(not parent.is_symlink(),'Symlink in authenticated path: '+str(parent))
    require(stat.S_ISREG(path.stat().st_mode),'Nonregular evidence: '+str(path))

def relative(root,name):
    path=Path(name)
    require(not path.is_absolute() and '..' not in path.parts,'Invalid immutable relative path')
    return root/path

def original_json(demo,name):
    data=subprocess.check_output(['git','-C',str(demo),'show',PUBLICATION+':'+CHECKPOINT+'/'+name])
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(blob==OBJECTS[name],'Original E Git blob mismatch: '+name)
    return json.loads(data)

def authenticate_published(demo):
    index=original_json(demo,'batch/evidence-index.json')
    native=original_json(demo,'RETAINED_LIVE_ROOTS.json')
    require(len(index['files'])==999 and native['batch']==str(BATCH),'Wrong original E manifest')
    expected={}
    def add(path,sha,size=None):
        key=str(path)
        require(key not in expected or expected[key][0]==sha,'Conflicting E hash identity')
        expected[key]=(sha,size)
    for row in index['files']:add(relative(BATCH,row['path']),row['sha256'],row['size'])
    require(len(expected)==999,'Duplicate indexed E path')
    for name,sha in TOP.items():add(BATCH/name,sha)
    inventories=native['nativeInventories']
    require(len(inventories)==3 and {r['role'] for r in inventories}=={'candidate-release','candidate-debug','candidate-off'},'Wrong native E role census')
    for inv in inventories:
        root=BATCH/'projects'/inv['role']/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp'
        require(inv['installedNativeRoot']==str(root) and len(inv['installedFileInventory'])==972,'Wrong E installed inventory')
        require(len({r['path'] for r in inv['installedFileInventory']})==972,'Duplicate native E file')
        for row in inv['installedFileInventory']:add(relative(root,row['path']),row['sha256'],row['size'])
        require(inv['receipt']==str(BATCH/'builds'/inv['role']/'build-receipt.json'),'Wrong E build receipt path')
        add(Path(inv['receipt']),inv['receiptSha256'])
    for name,(sha,size) in expected.items():
        path=Path(name);regular(path)
        require((size is None or path.stat().st_size==size) and digest(path)==sha,'E preserved bytes differ: '+name)
    return len(expected)

def snapshot(roots):
    result={}
    for root in roots:
        require(root.is_dir() and not root.is_symlink(),'Missing/aliased retained E root: '+str(root))
        def failed(error):raise error
        for parent,dirs,files in os.walk(root,followlinks=False,onerror=failed):
            for name in list(dirs):
                p=Path(parent)/name
                if p.is_symlink():
                    result[str(p)]={'kind':'symlink','target':os.readlink(p)};dirs.remove(name)
            for name in files:
                p=Path(parent)/name
                if p.is_symlink():result[str(p)]={'kind':'symlink','target':os.readlink(p)}
                else:
                    regular(p);result[str(p)]={'kind':'file','bytes':p.stat().st_size,'sha256':digest(p)}
    return result

def write_new(path,data):
    with path.open('x',encoding='utf8') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--demo',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--phase',choices=('before','after'),required=True);p.add_argument('--before',type=Path)
    args=p.parse_args(argv);dest=args.receipt
    require(not dest.exists() and dest.parent.is_dir(),'Unused receipt under existing external directory required')
    require(not dest.is_symlink() and not dest.resolve().is_relative_to(args.demo.resolve()),'Receipt must be external')
    for root in ROOTS:require(not dest.resolve().is_relative_to(root),'No write inside retained E')
    record={'kind':'R03IRPreserveE','phase':args.phase,'result':'Blocked','originalEPublication':PUBLICATION,
            'historicalERuntime':'Failed','originalSStrictCustody':'Blocked','runtimeAcceptance':False}
    try:
        count=authenticate_published(args.demo)
        current=snapshot(ROOTS)
        if args.phase=='before':
            require(args.before is None,'Before phase cannot adopt a different prior snapshot')
            mapping=dest.with_suffix('.inventory.json');require(not mapping.exists(),'Unused E snapshot required')
            write_new(mapping,current)
            record.update(mapPath=str(mapping),mapSha256=digest(mapping))
        else:
            require(args.before is not None,'After needs original before receipt')
            prior=json.loads(args.before.read_text())
            mapping=args.before.with_suffix('.inventory.json')
            require(prior.get('kind')=='R03IRPreserveE' and prior.get('result')=='PassedPreservationOnly' and
                    prior.get('phase')=='before' and prior.get('originalEPublication')==PUBLICATION and
                    prior.get('mapPath')==str(mapping) and digest(mapping)==prior.get('mapSha256'),'Before receipt/snapshot binding mismatch')
            require(json.loads(mapping.read_text())==current,'Retained E snapshot changed; never rebaseline')
            record.update(beforeReceiptSha256=digest(args.before),mapSha256=digest(mapping))
        record.update(result='PassedPreservationOnly',publishedFilesVerified=count,snapshotEntries=len(current),
                      unindexedSnapshotClassification='Current before/after only, not retroactive build provenance')
    except (OSError,ValueError,KeyError,RuntimeError,subprocess.CalledProcessError) as error:
        record['error']=str(error)
    write_new(dest,record);print(json.dumps(record,sort_keys=True));return 0 if record['result']=='PassedPreservationOnly' else 2

if __name__=='__main__':raise SystemExit(main())
