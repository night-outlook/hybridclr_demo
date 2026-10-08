"""Tiny real Linux/host-Clang domain probes, not Unity source or Player tests."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import h1_bee_macro_domains as d
import h1_compiler_actions as a
import h1_pch_provenance as p
from test_h1_pch_provenance import CONFIG, graph

CLANG = shutil.which('clang')


@unittest.skipUnless(CLANG, 'Real Clang unavailable; do not count as an execution pass')
class DomainProbeTests(unittest.TestCase):
    def fixture(self, root, feature=True, release=False):
        config = root/'il2cpp-config.h'; config.write_text(CONFIG)
        (root/'p.h').write_text('#include "il2cpp-config.h"\n#define PCH_VALUE 7\n')
        (root/'u.c').write_text('int value=PCH_VALUE;\n')
        g=graph(root,CLANG)
        for library, files in d.EXTERNAL.items():
            for number,name in enumerate(sorted(files)):
                path=root/d.INSTALLED/'external'/library/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('int '+library+'_fixture_'+str(number)+';\n')
                out=str(root/(library+str(number)+'.o'))
                flags=f'{CLANG} -isysroot / -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1'
                g['Nodes'].append({'Annotation':'C_Mac_arm64 external fixture','Action':f'{flags} -x c -c {path} -o {out}',
                    'Inputs':[str(path)],'Outputs':[out]})
                g['Nodes'][2]['Inputs'].append(out);g['Nodes'][2]['Action']+=' '+out
        for node in g['Nodes']:
            if not feature:node['Action']=node['Action'].replace('SHADOW=1','SHADOW=0')
            if release and node['Annotation'].startswith('C_Mac_arm64'):
                node['Action']=node['Action'].replace('-DIL2CPP_DEBUG=1','-DIL2CPP_DEBUG=0')+' -DNDEBUG=0'
        # Only the PCH producer and runtime object supply real fixture outputs;
        # all external flag domains are executed by the proof's syntax/macro probes.
        # This synthetic graph is explicitly not an executed Player build.
        for node in g['Nodes'][:2]:
            if node['Annotation'].startswith('C_Mac_arm64'):
                subprocess.run(a.split(node['Action']),cwd=root,check=True,capture_output=True,timeout=30)
        binding={'featureEnabled':feature,'cppConfiguration':'Release' if release else 'Debug'}
        blueprint=p.plan(g,root,root/'GameAssembly.dylib',CONFIG,{},feature)
        proof=p.capture(blueprint,g,root,str(config),binding,root/'proof')
        return g,binding,blueprint,proof
    def roundtrip(self,feature,release):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root,feature,release)
            p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
            self.assertEqual(16,len(proof['externalSources']))
            for group,row in zip(bp['groups'],proof['groups']):
                if group['macroDomain']!=d.RUNTIME:
                    text=p.load_row(row['macros']['stdout'])
                    self.assertNotIn(b'#define IL2CPP_DEBUG ',text)
                    self.assertNotIn('-include-pch',row['syntax']['argv'])
                    self.assertNotIn(b'#include',p.load_row(row['source']))
    def test_on_debug(self):self.roundtrip(True,False)
    def test_off_debug(self):self.roundtrip(False,False)
    def test_on_release_ndebug_zero_defined(self):self.roundtrip(True,True)
    def test_off_release(self):self.roundtrip(False,True)
    def test_rehashed_external_macro_forgery_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            for group,row in zip(bp['groups'],proof['groups']):
                if group['macroDomain']=='external-zlib':
                    record=row['macros']['stdout'];raw=p.load_row(record)+b'#define IL2CPP_DEBUG 0\n'
                    Path(record['retainedPath']).write_bytes(raw);record.update(sha256=p.sha(raw),bytes=len(raw))
            with self.assertRaisesRegex(ValueError,'Unexpected external'):
                p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_external_source_evidence_cannot_be_omitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            proof['externalSources'].pop()
            with self.assertRaisesRegex(ValueError,'External compiler source evidence'):
                p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_external_source_byte_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            Path(proof['externalSources'][0]['retainedPath']).write_bytes(b'changed')
            with self.assertRaises(ValueError):p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_missing_external_context_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            proof['groups'].pop()
            with self.assertRaisesRegex(ValueError,'Missing PCH context'):
                p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_domain_classification_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            proof['plan']['units'][0]['macroDomain']='external-zlib'
            with self.assertRaisesRegex(ValueError,'plan differs'):
                p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_partial_proof_is_never_a_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            proof['status']='Failed'
            with self.assertRaisesRegex(ValueError,'partial/failed'):
                p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b)
    def test_archive_reader_remains_portable_for_external_probes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();g,b,bp,proof=self.fixture(root)
            stored={}
            def walk(v):
                if type(v) is dict:
                    if 'retainedPath' in v:stored[v['retainedPath']]=p.load_row(v)
                    for item in v.values():walk(item)
                elif type(v) is list:
                    for item in v:walk(item)
            walk(proof);shutil.rmtree(root)
            p.verify(proof,g,root,root/'GameAssembly.dylib',CONFIG,{},b,read=lambda row:stored[row['retainedPath']])


if __name__=='__main__':unittest.main()
