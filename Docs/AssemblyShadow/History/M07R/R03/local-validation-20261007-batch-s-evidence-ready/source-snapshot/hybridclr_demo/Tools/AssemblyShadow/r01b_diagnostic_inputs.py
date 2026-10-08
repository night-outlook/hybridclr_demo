"""Separate, fail-closed provenance for the R01B diagnostic Player.

This does not confer production policy admission and never substitutes the
artifact for the regular M07 ON/OFF pair. Compatibility is conservative byte
comparison, allowing only parsed PE provenance differences, not a claimed
semantic hash or a names-only comparison.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import uuid

import m07_results as m07
from m04_metadata import Reader, _metadata, read_identity, read_identity_bytes
from r00_player_inputs import verify_inputs
from r01b_capacity_inputs import canonical_directory, canonical_file, digest, executable_for
from shadow_tools import require

DIAGNOSTIC_DEFINE = 'ASSEMBLY_SHADOW_R01B_DIAGNOSTICS'
DIAGNOSTIC_ASSEMBLY = 'AssemblyShadow.R01BDiagnostics'
CORE_ASSEMBLIES = tuple(m07.CANDIDATES) + ('HybridCLR.Runtime', 'AssemblyShadowDemo.Bootstrap')
NATIVE_ARGUMENTS = '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"'


def normalized_pe(data: bytes, label):
    """Keep every runtime byte; mask only bounded, typed provenance locations.

    Layout is kept, including debug pointers/sizes/types. The caller requires
    identical mask ranges as well as equal normalized bytes. Unknown debug
    types are retained verbatim. This deliberately rejects semantic-equivalent
    images whose metadata layout, IL, resources or linking differ.
    """
    identity = read_identity_bytes(data, label)
    streams = _metadata(data, label)
    r = Reader(data, label)
    pe = r.number(0x3c, 4); opt = pe + 24
    directory = 96 if r.number(opt, 2) == 0x10b else 112
    sections, opt_size = r.number(pe + 6, 2), r.number(pe + 20, 2)
    headers = r.number(opt + 60, 4)
    section_spans = []
    for index in range(sections):
        off = opt + opt_size + index * 40
        section_spans.append((r.number(off+12, 4), r.number(off+16, 4), r.number(off+20, 4)))

    def rva(value, size):
        found = [ptr + value-start for start, count, ptr in section_spans if start <= value and value+size <= start+count]
        if value+size <= headers: found.append(value)
        require(len(found) == 1, f'{label}: ambiguous provenance RVA')
        r.block(found[0], size)
        return found[0]

    cli = rva(r.number(opt+directory+14*8, 4), 72)
    md_size = r.number(cli+12, 4); md = rva(r.number(cli+8, 4), md_size)
    cursor = md + ((16+r.number(md+12, 4)+3) & ~3)
    count = r.number(cursor+2, 2); cursor += 4
    guid_offset = None
    for _ in range(count):
        offset, size = r.number(cursor, 4), r.number(cursor+4, 4)
        end = cursor+8
        while r.number(end, 1): end += 1
        if r.block(cursor+8, end-cursor-8) == b'#GUID': guid_offset = md+offset
        cursor = (end+4) & ~3
    tables = Reader(streams.get('#~', streams.get('#-')), label)
    valid, heap_sizes = tables.number(8, 8), tables.number(6, 1)
    module_offset = 24 + valid.bit_count()*4
    string_width = 4 if heap_sizes & 1 else 2
    guid_width = 4 if heap_sizes & 2 else 2
    module_guid = tables.number(module_offset+2+string_width, guid_width)
    require(tables.number(module_offset+2+string_width+guid_width, guid_width) == 0 and
            tables.number(module_offset+2+string_width+2*guid_width, guid_width) == 0,
            f'{label}: Edit-and-Continue Module identity is unsupported')
    mvid_offset = guid_offset+(module_guid-1)*16
    require(r.block(mvid_offset,16) == uuid.UUID(identity['mvid']).bytes_le, f'{label}: MVID range differs')
    ranges = [(pe+8, 4, 'coff-timestamp'), (opt+64, 4, 'pe-checksum'), (mvid_offset, 16, 'module-mvid')]
    debug_rva, debug_size = r.number(opt+directory+6*8,4), r.number(opt+directory+6*8+4,4)
    if debug_rva or debug_size:
        require(debug_rva and debug_size and debug_size % 28 == 0, f'{label}: malformed PE debug directory')
        debug = rva(debug_rva, debug_size)
        require(not (debug < md+md_size and md < debug+debug_size), f'{label}: debug directory overlaps CLI metadata')
        for off in range(debug,debug+debug_size,28):
            kind, size, address, ptr = (r.number(off+n,4) for n in (12,16,20,24))
            r.block(ptr,size)
            if size and address: require(rva(address,size) == ptr, f'{label}: debug payload address differs')
            ranges.append((off+4,4,'debug-timestamp'))
            if kind == 2:
                require(size >= 25 and r.block(ptr,4) == b'RSDS' and r.block(ptr+size-1,1) == b'\0', f'{label}: malformed CodeView payload')
                ranges.append((ptr,size,'codeview'))
            elif kind == 19:
                require(size >= 8 and b'\0' in r.block(ptr,min(size,16)), f'{label}: malformed PDB checksum payload')
                ranges.append((ptr,size,'pdb-checksum'))
            elif kind == 16:
                require(size == 0, f'{label}: reproducible debug record has payload')
            # Embedded PDBs and unknown kinds remain byte-identical.
        for offset,size,kind in ranges:
            if kind in ('codeview','pdb-checksum'):
                require(not (offset < md+md_size and md < offset+size) and
                        not (offset < debug+debug_size and debug < offset+size), f'{label}: debug payload overlaps metadata/directory')
    normalized = bytearray(data)
    previous = -1
    for offset,size,kind in sorted(ranges):
        require(offset >= previous, f'{label}: overlapping provenance ranges')
        r.block(offset,size); previous=offset+size
        normalized[offset:offset+size] = bytes(size)
    return bytes(normalized), sorted(ranges)


def verify_compatible_dll(production: Path, diagnostic: Path, label):
    production = canonical_file(production, label+'.production')
    diagnostic = canonical_file(diagnostic, label+'.diagnostic')
    left, right = production.read_bytes(), diagnostic.read_bytes()
    a, b = read_identity_bytes(left,production), read_identity_bytes(right,diagnostic)
    m07.exact({k:v for k,v in a.items() if k != 'mvid'}, {k:v for k,v in b.items() if k != 'mvid'}, label+'.assemblyIdentity')
    if left == right:
        return dict(policy='ExactDllBytes', sha256=hashlib.sha256(left).hexdigest())
    normalized_a, ranges_a = normalized_pe(left,production)
    normalized_b, ranges_b = normalized_pe(right,diagnostic)
    m07.exact(ranges_a,ranges_b,label+'.provenanceLayout')
    require(normalized_a == normalized_b,
            f'{label}: runtime DLL bytes differ beyond PE provenance; normalized semantic compatibility is unproved')
    return dict(policy='ExactRuntimeBytesExceptPeProvenanceV1', sha256=hashlib.sha256(normalized_a).hexdigest())


def _inventory(snapshot, root, linked=False):
    sections = [snapshot['linkedPlayerReceipt']['assemblies']] if linked else [snapshot[key] for key in ('assemblies','filteredAssemblies','references')]
    base = root/'LinkedPlayer' if linked else root
    rows = {}
    for section in sections:
        for row in section:
            name = row['name'].casefold()
            require(name not in rows, f'{root}: duplicate physical assembly inventory {name}')
            rows[name] = m07.prior._rel(base,row['path'],root,'captured DLL')
    return rows


def verify_core_compatibility(production, diagnostic, path):
    proofs = []
    for linked in (False,True):
        regular = _inventory(production['snapshot'],production['root'],linked)
        actual = _inventory(diagnostic['snapshot'],diagnostic['root'],linked)
        require(DIAGNOSTIC_ASSEMBLY.casefold() not in regular, f'{path}: diagnostic assembly entered production')
        require(DIAGNOSTIC_ASSEMBLY.casefold() in actual, f'{path}: diagnostic assembly missing from diagnostic capture')
        for name in CORE_ASSEMBLIES:
            key=name.casefold()
            require(key in regular and key in actual, f'{path}: compatibility assembly missing: {name}')
            proofs.append(dict(assembly=name,stage='LinkedPlayer' if linked else 'PlayerInput',
                               **verify_compatible_dll(regular[key],actual[key],f'{path}.{name}')))
    return proofs


def collect_diagnostic_inputs(context):
    """All immutable diagnostic capture/app bytes to bind before and after launch."""
    diagnostic = context['diagnostic']; files = {diagnostic['path']}
    for root in (diagnostic['root'],diagnostic['output']):
        for item in root.rglob('*'):
            require(not item.is_symlink(), f'{item}: symlink in diagnostic evidence')
            if item.is_file(): files.add(item.resolve(strict=True))
    return files


RECEIPT_FIELDS = '''schemaVersion nativeMetadataVersion diagnosticOnly productionPolicyAdmission kind milestone uniqueGuid
baselineBuildId runtimeAbiHash unityVersion target architecture buildGuid playerOutput playerExecutable playerExecutableSha256
inputSnapshot inputSnapshotHash sourcePinFile sourcePinSha256 sourcePinsJson nativeLibraryPath nativeLibrarySha256
nativeArguments extraScriptingDefines linkedInputNames linkedInputSha256 assemblyIdentities nativeMetadataPath
nativeMetadataSha256 diagnosticAssemblyName nativeAssemblyIdentities nativeGeneratedAssemblyNames scenes
regularFixtureManifestPath regularFixtureManifestSha256 regularPlayerReceiptPath regularPlayerReceiptSha256 note'''
DIAGNOSTIC_SCENE = 'Assets/AssemblyShadowR01BDiagnostics/Scenes/R01BDiagnostic.unity'


def _verify_receipt_header(player, context, project, path):
    m07.fields(player, RECEIPT_FIELDS, path)
    for key, expected in dict(schemaVersion=1, kind='R01BDiagnosticPlayerBuild', milestone='R01B',
            diagnosticOnly=True, productionPolicyAdmission=False, diagnosticAssemblyName=DIAGNOSTIC_ASSEMBLY,
            nativeArguments=NATIVE_ARGUMENTS, scenes=[DIAGNOSTIC_SCENE,'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity']).items():
        m07.exact(player[key],expected,f'{path}.{key}')
    arrays = {'extraScriptingDefines','linkedInputNames','linkedInputSha256','assemblyIdentities',
              'nativeAssemblyIdentities','nativeGeneratedAssemblyNames','scenes'}
    for key in arrays:m07.array(player[key],f'{path}.{key}')
    for key in set(RECEIPT_FIELDS.split())-arrays-{'schemaVersion','nativeMetadataVersion','diagnosticOnly','productionPolicyAdmission'}:
        require(type(player[key]) is str, f'{path}.{key}: expected string')
    require(player['note'], f'{path}: diagnostic evidence boundary note is missing')
    m07.integer(player['nativeMetadataVersion'],path,1)
    import re
    require(re.fullmatch('[0-9a-f]{32}',player['uniqueGuid']) is not None, f'{path}: invalid receipt identity')
    m07.prior._guid(player['buildGuid'],path,'buildGuid')
    require(player['buildGuid'] not in (context['on']['player']['buildGuid'],context['off']['player']['buildGuid']),
            f'{path}: diagnostic Player reuses a production build GUID')
    baseline=context['baseline']
    for key in ('baselineBuildId','runtimeAbiHash','unityVersion','target','architecture'):
        m07.exact(player[key],baseline[key],f'{path}.{key}')
    for key, expected in (('regularFixtureManifestPath',Path(context['manifest']['_path'])),
                          ('regularPlayerReceiptPath',context['on']['path'])):
        actual=canonical_file(player[key],f'{path}.{key}')
        m07.exact(actual,expected,f'{path}.{key}')
        hash_key=key.replace('Path','Sha256')
        m07.exact(player[hash_key],digest(actual),f'{path}.{hash_key}')
    source=canonical_file(player['sourcePinFile'],f'{path}.sourcePinFile')
    from shadow_tools import PINS
    m07.exact(source,project/PINS,f'{path}.sourcePinFile')
    m07.exact(player['sourcePinSha256'],digest(source),f'{path}.sourcePinSha256')
    m07.exact(m07.prior._obj(source),context['sourcePins'],f'{path}.currentSourcePins')
    m07.exact(m07.json_text(player['sourcePinsJson'],path),context['sourcePins'],f'{path}.sourcePinsJson')
    defines=player['extraScriptingDefines']
    require(all(type(item) is str and item for item in defines) and len(defines)==len(set(defines)), f'{path}: malformed diagnostic defines')
    production_defines=context['on']['snapshot']['extraScriptingDefines']
    require(DIAGNOSTIC_DEFINE not in production_defines and
            DIAGNOSTIC_DEFINE not in context['off']['snapshot']['extraScriptingDefines'], f'{path}: production includes diagnostic define')
    m07.exact(sorted(defines),sorted(production_defines+[DIAGNOSTIC_DEFINE]),f'{path}.diagnosticDefines')


def verify_diagnostic_inputs(project, fixture, on, off, replay, diagnostic_receipt):
    """Verify the unchanged regular context, then attach a separately proved app."""
    project=canonical_directory(project,'R01B project')
    context=verify_inputs(project,fixture,on,off,replay)
    path=canonical_file(diagnostic_receipt,'R01B diagnostic build receipt')
    require(path.is_relative_to(project),f'{path}: diagnostic receipt outside integration project')
    player=m07.prior._obj(path)
    _verify_receipt_header(player,context,project,path)
    root=canonical_directory(player['inputSnapshot'],'diagnostic snapshot')
    require(root.is_relative_to(project/'_temp/AssemblyShadow/R01B'), f'{path}: diagnostic capture outside R01B evidence root')
    require(root not in (context['on']['root'],context['off']['root']),f'{path}: diagnostic reuses production capture')
    snapshot=m07.prior._verify_snapshot(root,player['baselineBuildId'],player['runtimeAbiHash'],context['baseline'],path,False)
    for key, source in (('inputSnapshotHash','snapshotHash'),('buildGuid','buildGuid'),('playerOutput','playerOutput'),
                        ('nativeLibraryPath','nativeLibraryPath'),('nativeLibrarySha256','nativeLibrarySha256'),
                        ('extraScriptingDefines','extraScriptingDefines')):
        m07.exact(player[key],snapshot[source],f'{path}.{key}')
    require(type(snapshot.get('playerBuildOptions')) is int and snapshot['playerBuildOptions'] & 1,
            f'{path}: diagnostic must be a Development Player')
    m07.prior._pins(snapshot['sourcePins'],path,context['sourcePins'])
    output=canonical_directory(player['playerOutput'],'diagnostic Player')
    require(output.is_relative_to(project/'Builds/AssemblyShadow/R01B') and
            output not in (context['on']['output'],context['off']['output']),f'{path}: diagnostic Player is not a distinct R01B artifact')
    executable=executable_for(output)
    m07.exact(player['playerExecutable'],str(executable),f'{path}.playerExecutable')
    m07.exact(player['playerExecutableSha256'],digest(executable),f'{path}.playerExecutableSha256')
    native=canonical_file(player['nativeLibraryPath'],'diagnostic native library')
    require(native.is_relative_to(output),f'{path}: native library outside diagnostic app')
    m07.exact(player['nativeLibrarySha256'],digest(native),f'{path}.nativeLibrarySha256')
    require(player['nativeLibrarySha256'] not in (context['on']['player']['nativeLibrarySha256'],context['off']['player']['nativeLibrarySha256']),f'{path}: diagnostic reuses production native artifact')
    m07.prior._snapshot_files(snapshot,root,path)
    m07.prior._verify_linked_player(root,snapshot,{row['name']:row for row in context['baseline']['assemblies']},path)
    # These verify existing generated contracts, without claiming global
    # production admission of the explicitly external diagnostic loader.
    m07.prior._reflection_snapshot(root,snapshot,path,require_linked=True)
    m07.raw_admissions.verify_snapshot(root,snapshot,require_linked=True)
    linked=snapshot['linkedPlayerReceipt']['assemblies']
    linked_paths=[m07.prior._rel(root/'LinkedPlayer',row['path'],path,'linked DLL') for row in linked]
    m07.prior.verify_identities(player['assemblyIdentities'],linked_paths,path)
    m07.prior._verify_native_metadata(player,path)
    actual_linked=sorted((read_identity(dll) for dll in linked_paths),key=lambda row:row['name'])
    m07.exact(player['linkedInputNames'],[row['name'] for row in actual_linked],f'{path}.linkedInputNames')
    m07.exact(player['linkedInputSha256'],[row['sha256'] for row in actual_linked],f'{path}.linkedInputSha256')
    diagnostic=dict(path=path,root=root,snapshot=snapshot,player=player,output=output,executable=executable)
    diagnostic['compatibility']=verify_core_compatibility(context['on'],diagnostic,path)
    # Check OFF independently too: absence is a property of both real captures.
    for linked_stage in (False,True):
        require(DIAGNOSTIC_ASSEMBLY.casefold() not in _inventory(context['off']['snapshot'],context['off']['root'],linked_stage),
                f'{path}: diagnostic assembly entered production OFF')
    context['diagnostic']=diagnostic
    diagnostic['inventory']=collect_diagnostic_inputs(context)
    diagnostic['inventory'].add(canonical_file(player['sourcePinFile'],'source pins'))
    return context
