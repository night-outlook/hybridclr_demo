#!/usr/bin/env python3
"""Strictly verify fresh H1 native compiler provenance for candidate or repro builds.

Unlike the historical verifier, this command evaluates each native translation
unit with retained transitive response files and ordered -D/-U semantics.
NDEBUG uses definedness. Link flags cannot establish compile macros.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

import h1_compiler_actions as strict
import h1_pch_provenance as pch


class VerificationError(ValueError): pass

def need(value, message):
    if not value: raise VerificationError(message)

def digest(path: Path, *, allow_symlink=False) -> str:
    need(path.is_file() and (allow_symlink or not path.is_symlink()), "Expected file: " + str(path))
    with path.open("rb") as stream: return hashlib.file_digest(stream, "sha256").hexdigest()

def unique_pairs(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,"Duplicate JSON key: "+key);result[key]=value
    return result

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs)

def canonical(value: str, label: str, *, allow_symlink=False) -> Path:
    path=Path(value)
    need(path.is_absolute() and path.is_file() and (allow_symlink or not path.is_symlink()), label+" missing")
    resolved=path.resolve(strict=True)
    if not allow_symlink: need(path==resolved,label+" is not canonical")
    return path

def project_root(receipt: Path) -> Path:
    for parent in receipt.parents:
        if (parent/'Assets').is_dir() and (parent/'ProjectSettings').is_dir(): return parent
    raise VerificationError("Cannot derive Unity project root")

def mode_for(build):
    feature=build.get('featureEnabled');cpp=build.get('cppConfiguration')
    need(type(feature) is bool and cpp in ('Debug','Release'),'Invalid build mode')
    return ('On' if feature else 'Off')+'/'+cpp


def verify_receipt(receipt_path: Path) -> dict:
    receipt_path=canonical(str(receipt_path),'build receipt')
    root=project_root(receipt_path);build=read(receipt_path);mode=mode_for(build)
    need(build.get('schemaVersion')==1 and build.get('kind')=='H1CountDiagnosticPlayerBuild' and build.get('diagnosticOnly') is True,'Invalid H1 build receipt')
    need(build.get('baselineBuildId')=='H1Count-'+mode.replace('/','-'),'Build ID differs')
    need(('HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+('1' if build['featureEnabled'] else '0')) in build.get('nativeArguments',''),'Feature compiler intent differs')
    p=canonical(build.get('compilerProvenancePath',''),'compiler provenance');need(digest(p)==build.get('compilerProvenanceSha256'),'Compiler provenance hash differs')
    provenance=read(p);need(provenance==build.get('compilerProvenance'),'Embedded and retained compiler provenance differ')
    need(provenance.get('macroDomainPolicy')==strict.H1_APPLE_BEE_DOMAIN_POLICY,'Fresh H1 build lacks the reviewed Apple macro-domain policy')
    for field in ('buildId','buildGuid','inputSnapshotHash','nativeLibraryPath','nativeLibrarySha256','sourcePinSha256'):
        source='baselineBuildId' if field=='buildId' else field
        need(provenance.get(field)==build.get(source),'Build/provenance differs: '+field)
    graph_path=canonical(provenance['beeActionGraphPath'],'Bee graph');config_path=canonical(provenance['il2cppConfigPath'],'IL2CPP config')
    need(digest(graph_path)==provenance['beeActionGraphSha256'] and digest(config_path)==provenance['il2cppConfigSha256'],'Retained native input hash differs')
    responses=strict.retained_responses(provenance,digest)
    try:
        graph=read(graph_path)
        if pch.has_pch(graph,root,responses):
            need(provenance.get('projectRoot')==str(root),'PCH project root differs from the build receipt location')
            proof_path=canonical(provenance.get('pchProofPath',''),'PCH proof')
            need(digest(proof_path)==provenance.get('pchProofSha256'),'PCH proof hash differs')
            proof=read(proof_path)
            need(proof.get('compilerSha256')==provenance['compilerSha256'],'PCH compiler identity differs')
            binding=pch.binding_from(provenance,root,build['featureEnabled'],build['cppConfiguration'])
            derived=pch.verify(proof,graph,root,Path(provenance['nativeLibraryPath']),config_path.read_text(),responses,binding)
            for producer in proof['producers']:
                for item in producer['inputs']:
                    if item['kind']=='toolchain-binary':
                        tool=canonical(item['toolPath'],'PCH producer tool',allow_symlink=True)
                        need(digest(tool,allow_symlink=True)==item['toolSha256'],'PCH producer tool bytes differ')
                    elif item['kind']=='bee-sdk-marker':
                        need(item['sdkSettings']['sha256']==provenance['sdkSettingsSha256'],'PCH SDK marker differs')
        else:
            need(not provenance.get('pchProofPath') and not provenance.get('pchProofSha256'),'Unexpected PCH proof on a non-PCH graph')
            derived=strict.derive_graph_evidence(graph,root,Path(provenance['nativeLibraryPath']),config_path.read_text(),responses,expected_feature=build['featureEnabled'],domain_policy=strict.H1_APPLE_BEE_DOMAIN_POLICY)
        need(set(derived['responseSources'])==set(responses),'Native response closure contains missing/unused captures')
        need(provenance.get('macroDomainEvidence')==json.dumps(derived['macroDomains'],sort_keys=True,separators=(',',':')),'Macro-domain evidence differs from raw Bee graph')
    except strict.CompilerActionError as error:
        raise VerificationError(str(error)) from error
    for field in ('compileActionCount','linkActionCount','compilerPath','sdkPath','beeLinkOutputPath','il2cppDebug','ndebug','il2cppDevelopment'):
        need(provenance.get(field)==derived[field],'Bee-derived provenance differs: '+field)
    compiler=canonical(provenance['compilerPath'],'compiler',allow_symlink=True)
    need(digest(compiler,allow_symlink=True)==provenance['compilerSha256'],'Compiler bytes differ')
    sdk=canonical(provenance['sdkSettingsPath'],'SDK settings')
    need(digest(sdk)==provenance['sdkSettingsSha256'],'SDK settings bytes differ')
    native=canonical(provenance['nativeLibraryPath'],'native library')
    need(digest(native)==provenance['nativeLibrarySha256'],'Selected native library bytes differ')
    expected=('1','0') if mode.endswith('/Debug') else ('0','1')
    need((provenance['il2cppDebug'],provenance['ndebug'])==expected and provenance['il2cppDevelopment']=='0','Effective native assertion/debug profile differs: '+mode)
    return {'mode':mode,'receiptPath':str(receipt_path),'receiptSha256':digest(receipt_path),
        'buildGuid':build['buildGuid'],'inputSnapshotHash':build['inputSnapshotHash'],'nativeLibrarySha256':build['nativeLibrarySha256'],
        'sourcePinSha256':build['sourcePinSha256'],'compilerPath':provenance['compilerPath'],'compilerSha256':provenance['compilerSha256'],
        'compilerVersion':provenance['compilerVersion'],'sdkPath':provenance['sdkPath'],'sdkVersion':provenance['sdkVersion'],
        'sdkSettingsSha256':provenance['sdkSettingsSha256'],'compileActionCount':provenance['compileActionCount'],
        'linkActionCount':provenance['linkActionCount'],'il2cppDebug':provenance['il2cppDebug'],'ndebug':provenance['ndebug'],
        'il2cppDevelopment':provenance['il2cppDevelopment']}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='append',required=True,type=Path)
    p.add_argument('--scope',choices=('candidate','reproduction','single'),default='candidate');p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    expected={'On/Debug','On/Release','Off/Debug','Off/Release'} if a.scope=='candidate' else {'On/Debug','On/Release'}
    if a.scope=='single':
        need(len(a.build)==1,'Single-build smoke verification requires exactly one receipt')
        expected={mode_for(read(a.build[0]))}
    need(len(a.build)==len(expected),'Selected scope requires exactly '+str(len(expected))+' receipts')
    rows=[verify_receipt(path) for path in a.build];need({r['mode'] for r in rows}==expected,'Compiler mode inventory differs')
    for field in ('compilerPath','compilerSha256','compilerVersion','sdkPath','sdkVersion','sdkSettingsSha256','sourcePinSha256'):
        need(len({r[field] for r in rows})==1,'Toolchain comparison differs: '+field)
    out=a.output;need(out.is_absolute() and out==out.resolve() and not out.exists() and out.parent.is_dir(),'New canonical output required')
    result={'schemaVersion':1,'kind':'H1CompilerProvenanceVerification','status':'Passed','result':'Passed','scope':a.scope,
        'modeCount':len(expected),'rows':sorted(rows,key=lambda r:r['mode']),'humanGatePassed':False,'mayEnterR02':False}
    with out.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'result':'Passed','scope':a.scope,'modeCount':len(expected),'output':str(out)}));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,KeyError,json.JSONDecodeError,VerificationError,strict.CompilerActionError) as error:
        print('Failed: '+str(error),file=__import__('sys').stderr);raise SystemExit(1)