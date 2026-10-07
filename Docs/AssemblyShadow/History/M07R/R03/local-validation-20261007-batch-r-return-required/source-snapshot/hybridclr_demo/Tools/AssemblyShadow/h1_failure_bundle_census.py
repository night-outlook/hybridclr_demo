"""Export a full graph census from a hash-pinned failure archive, without extraction.

The export makes source/edge facts readable; it never approves a macro domain.
Original project/native locators must be supplied, not rewritten in raw records.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

from h1_capture_attempt import Attempt, encode, new_file
from h1_macro_domain_census import inventory
from h1_compiler_actions import need

ARCHIVE_SHA256 = 'e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8'
GRAPH_SHA256 = 'dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181'
MAX_EXPANDED = 512 * 1024 * 1024
MAX_MEMBER = 64 * 1024 * 1024
MAX_MEMBERS = 10000


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_graph(archive, archive_hash, graph_hash):
    need(digest(archive) == archive_hash, 'Failure archive SHA-256 mismatch')
    seen=set(); rows=[]; total=0; graph_bytes=None; matches=[]
    with tarfile.open(archive, 'r|gz') as tar:
        for member in tar:
            path=PurePosixPath(member.name)
            need(not path.is_absolute() and '..' not in path.parts and '\\' not in member.name and
                 member.name not in seen and (member.isfile() or member.isdir()), 'Unsafe or duplicate archive member')
            seen.add(member.name);total+=member.size
            need(len(seen)<=MAX_MEMBERS and total<=MAX_EXPANDED and 0<=member.size<=MAX_MEMBER, 'Archive retention bound exceeded')
            if member.isdir(): continue
            with tar.extractfile(member) as stream:
                raw=stream.read(MAX_MEMBER+1)
            need(len(raw)==member.size, 'Archive member length mismatch')
            sha=hashlib.sha256(raw).hexdigest()
            rows.append({'member':member.name,'bytes':len(raw),'sha256':sha})
            if sha==graph_hash:
                graph_bytes=raw;matches.append(member.name)
    need(graph_bytes is not None, 'Exact graph hash is absent from failure archive')
    need(digest(archive)==archive_hash, 'Failure archive changed while reading')
    def unique(pairs):
        value={}
        for key,item in pairs:
            need(key not in value,'Duplicate graph JSON key: '+key);value[key]=item
        return value
    graph=json.loads(graph_bytes.decode('utf-8-sig'),object_pairs_hook=unique)
    return graph,graph_bytes,{'archiveSha256':archive_hash,'graphSha256':graph_hash,
        'matchingGraphMembers':matches,'members':rows,'expandedBytes':total}


def export(archive, output, project, native, archive_hash=ARCHIVE_SHA256, graph_hash=GRAPH_SHA256):
    need(Path(project).is_absolute() and Path(native).is_absolute(), 'Original absolute source locators required')
    with Attempt(output, 'failure-bundle-census').guard() as attempt:
        attempt.stage('archive-authentication')
        graph,raw,manifest=read_graph(archive,archive_hash,graph_hash)
        attempt.keep_bytes('archive-graph:'+graph_hash,raw,'authenticated-graph')
        attempt.stage('graph-census')
        result=inventory(graph,Path(project),Path(native))
        result.update(archiveSha256=archive_hash,graphSha256=graph_hash)
        new_file(Path(output)/'bee-action-graph.json',raw)
        new_file(Path(output)/'archive-member-inventory.json',encode(manifest))
        new_file(Path(output)/'macro-domain-census.json',encode(result))
        attempt.finish('InventoryOnlyNotAcceptance')
        return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--project',type=Path,required=True);parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--archive-sha256',default=ARCHIVE_SHA256);parser.add_argument('--graph-sha256',default=GRAPH_SHA256)
    args=parser.parse_args()
    result=export(args.archive,args.output,args.project,args.native,args.archive_sha256,args.graph_sha256)
    print(json.dumps({'status':result['status'],'compileActionCount':result['compileActionCount'],
        'macroPolicyApproved':False,'humanGatePassed':False,'mayEnterR02':False}));return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except (OSError,ValueError,KeyError,tarfile.TarError) as error:
        print('Census failed (not a runtime result): '+str(error),file=__import__('sys').stderr);raise SystemExit(1)
