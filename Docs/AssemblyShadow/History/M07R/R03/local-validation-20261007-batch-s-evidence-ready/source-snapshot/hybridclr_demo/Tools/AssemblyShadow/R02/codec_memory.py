#!/usr/bin/env python3
"""Attribute profile-2 constructor heap requests on this host, never infer RSS."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
from evidence import binding, check_binding, read, require, run, write


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hybridclr-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    root=args.hybridclr_root.resolve(strict=True);output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).resolve().with_suffix('.cpp')
    header=root/'hybridclr/metadata/InterpreterMetadataIndexCodec.h'
    inputs=[binding(source),binding(header)]
    rows=[]
    for i,compiler in enumerate(dict.fromkeys(p for p in (shutil.which('g++'),shutil.which('clang++')) if p)):
        executable=output/('codec-'+str(i))
        row={'compiler':compiler,'result':'Failed'}
        compiled=run([compiler,'-std=c++17','-O2','-pthread','-Wall','-Wextra','-Werror','-I'+str(root),str(source),'-o',str(executable)],output,output/('compile-'+str(i)),120)
        row['compile']=binding(output/('compile-'+str(i))/'command.json')
        if compiled['result']=='Passed':
            invoked=run([str(executable)],output,output/('run-'+str(i)),60)
            row['execution']=binding(output/('run-'+str(i))/'command.json')
            if invoked['result']=='Passed':
                try:
                    raw=read(output/('run-'+str(i))/'stdout.log')
                    require(raw.get('kind')=='R02CodecOwnedStorage' and raw.get('result')=='Measured' and
                            raw.get('runtimeAcceptance') is False and raw.get('unityPlayerRun') is False,'Unexpected storage measurement')
                    require(raw['allocationCalls']==4 and type(raw['requestedHeapBytes']) is int and raw['requestedHeapBytes']>0,'Missing measured constructor allocations')
                    row.update(result='Measured',measurement=raw)
                except (ValueError,KeyError,TypeError) as error:row['error']=str(error)
        rows.append(row)
    for item in inputs:check_binding(item)
    success=bool(rows) and all(row['result']=='Measured' for row in rows)
    result={'kind':'R02CodecStorageAttribution','result':'Passed' if success else 'IncompleteOrFailed',
        'rows':rows,'inputs':inputs,'runtimeAcceptance':False,'unityPlayerRun':False,
        'scope':'Host compiler ABI and exact profile-2 header; four preallocated codec arrays. Includes allocation request sizes, not malloc overhead, RSS, Unity memory, or R02-added bytes.',
        'interpretation':'The profile-2 header is unchanged between the H1 runtime control and R02. Its storage is a retained component, not a new R02 regression or proof of the whole H1 RSS delta.'}
    write(output/'results.json',result);print(json.dumps(result))
    return 0 if success else 1

if __name__=='__main__':raise SystemExit(main())
