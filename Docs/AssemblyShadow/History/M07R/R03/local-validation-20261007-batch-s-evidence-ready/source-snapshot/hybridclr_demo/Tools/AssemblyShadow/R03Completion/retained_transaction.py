#!/usr/bin/env python3
"""Read-only audit of the pinned stranded R transaction; never restores or launches.

R remains forensic state. Its paths, files and missing receipts are authenticated
without rewriting them. Recovery behavior is exercised only by tests and a new
batch; this tool cannot resume, repair, finalize or reclassify an old batch.
"""
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from fixture_project import regular


def inputs():
    value = loads((HERE/'lr-retained.json').read_text())
    require(value['schemaVersion']==1 and value['kind']=='R03RetainedRTransactionPins', 'Retained R manifest')
    return value


def verify(root, manifest):
    """Bounded immutable-input verification, not a complete custody re-audit."""
    root = Path(root).absolute()
    require(root.is_dir() and root == root.resolve(), 'Canonical retained source root')
    paths = {}
    for key, row in manifest['files'].items():
        rel = Path(row['path'])
        require(not rel.is_absolute() and '..' not in rel.parts, 'Relative retained path')
        path = regular(root/rel)
        require(path.stat().st_size==row['size'] and sha(path)==row['sha256'], 'Retained file differs: '+key)
        paths[key] = path
    absent = []
    for relative in manifest['absent']:
        rel = Path(relative)
        require(not rel.is_absolute() and '..' not in rel.parts, 'Relative absent-evidence path')
        path = root/rel
        absent.append(path)
        require(not path.exists() and not path.is_symlink(), 'Unexpected historical restore evidence: '+relative)
    state, compiled, marker, failed = (loads(paths[key].read_text()) for key in ('state','compile','marker','failedCell'))
    require(state['schemaVersion']==2 and state['projectDirectory']==manifest['liveRoot']+'/'+manifest['project'] and
        state['runDirectory']==manifest['liveRoot']+'/'+manifest['run'], 'Historical transaction ownership')
    require(state['originalSettingsSha256']==sha(paths['original']) and state['originalDefines']=='' and
        state['stagedDefines']=='ASSEMBLY_SHADOW_P05', 'Recorded original/staged settings')
    require(compiled['stateSha256']==sha(paths['state']) and compiled['snapshotPath']=='P05-compile/Snapshot', 'Historical compile state binding')
    require(marker['owningDemoCommit']==manifest['executedDemoCommit'] and
        state['sourcePins']['demo']['revision']==manifest['executedDemoCommit'], 'Historical source pin')
    require(failed['id']=='resource-p05-restore' and failed['result']=='Failed' and
        failed['error']=='Git command failed: ls-remote origin', 'Unmodified original failed cell')
    require(all(sha(paths[k])==row['sha256'] for k,row in manifest['files'].items()), 'Retained custody after read')
    require(all(not p.exists() and not p.is_symlink() for p in absent), 'Historical receipt appeared during read')
    return {'kind':'R03RetainedP05ReadOnlyAudit','result':'Passed','filesVerified':len(paths),
        'inputRoot':str(root),'historicalSource':manifest['executedDemoCommit'],
        'originalGitTransportCause':'Unavailable','settingsRemainStaged':True,
        'originalRestoreCell':'Failed','historicalEvidenceModified':False,'restorationPerformed':False,
        'unityRun':False,'playerRun':False,'runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--retained-r');source.add_argument('--checkpoint',action='store_true')
    parser.add_argument('--output',required=True);args=parser.parse_args(argv)
    manifest=inputs();demo=HERE.parents[2]
    root=demo/manifest['checkpoint'] if args.checkpoint else Path(args.retained_r)
    require(args.checkpoint or str(root)==manifest['liveRoot'], 'Exact retained R path required')
    output=Path(args.output).absolute()
    require(output==output.resolve() and not output.exists() and output.parent.is_dir(), 'Unused audit output')
    require(not output.is_relative_to(root) and not root.is_relative_to(output) and
        not output.is_relative_to(demo), 'Write only outside retained evidence and owning repository')
    output.mkdir()
    result={'result':'Failed','historicalEvidenceModified':False,'restorationPerformed':False}
    try:
        result=verify(root,manifest)
        result['basis']='HistoricalCheckpointReadOnly' if args.checkpoint else 'LiveRetainedRReadOnly'
        result['inputManifestSha256']=sha(HERE/'lr-retained.json')
    except Exception as error:
        result['error']=str(error);raise
    finally:write(output/'verification.json',result)
    return 0


if __name__=='__main__':raise SystemExit(main())
