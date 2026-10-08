import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from h1_failure_bundle_census import read_graph, export, digest


class FailureBundleCensusTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.archive=self.root/'bundle.tar.gz'
        self.raw=b'{"Nodes":[{"Annotation":"C_Mac_arm64","Action":"/clang -c s.c -o o.o","Inputs":["s.c"],"Outputs":["o.o"]}]}'
        self.graph_hash=hashlib.sha256(self.raw).hexdigest()
    def tearDown(self):self.temp.cleanup()
    def create(self,entries):
        with tarfile.open(self.archive,'w:gz') as tar:
            for name,raw in entries:
                info=tarfile.TarInfo(name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
        return digest(self.archive)
    def test_graph_found_by_hash_not_filename(self):
        h=self.create([('inputs/opaque.bin',self.raw),('irrelevant',b'x')])
        graph,raw,manifest=read_graph(self.archive,h,self.graph_hash)
        self.assertEqual(self.raw,raw);self.assertEqual(1,len(graph['Nodes']));self.assertEqual(2,len(manifest['members']))
    def test_wrong_archive_hash_rejected(self):
        self.create([('graph',self.raw)])
        with self.assertRaisesRegex(ValueError,'archive SHA'):read_graph(self.archive,'0'*64,self.graph_hash)
    def test_wrong_graph_hash_rejected(self):
        h=self.create([('graph',self.raw)])
        with self.assertRaisesRegex(ValueError,'absent'):read_graph(self.archive,h,'0'*64)
    def test_unsafe_members_rejected_without_extraction(self):
        h=self.create([('../escape',b'x'),('graph',self.raw)])
        with self.assertRaisesRegex(ValueError,'Unsafe'):read_graph(self.archive,h,self.graph_hash)
        self.assertFalse((self.root.parent/'escape').exists())
    def test_duplicate_member_names_rejected(self):
        h=self.create([('graph',self.raw),('graph',self.raw)])
        with self.assertRaisesRegex(ValueError,'duplicate'):read_graph(self.archive,h,self.graph_hash)
    def test_export_is_diagnostic_only(self):
        h=self.create([('graph.bin',self.raw)]);out=self.root/'out'
        result=export(self.archive,out,Path('/original/project'),Path('/original/project/GameAssembly.dylib'),h,self.graph_hash)
        self.assertFalse(result['candidateAcceptance']);self.assertFalse(result['domainPolicyChanged'])
        self.assertEqual(self.raw,(out/'bee-action-graph.json').read_bytes())
    def test_missing_archive_creates_failure_record(self):
        out=self.root/'out'
        with self.assertRaises(FileNotFoundError):export(self.archive,out,Path('/original/project'),Path('/original/GameAssembly.dylib'))
        self.assertTrue((out/'attempt-failure.json').is_file());self.assertFalse((out/'macro-domain-census.json').exists())
    def test_old_output_preserved(self):
        h=self.create([('graph',self.raw)]);out=self.root/'out';out.mkdir();(out/'keep').write_bytes(b'old')
        with self.assertRaises(ValueError):export(self.archive,out,Path('/original'),Path('/original/native'),h,self.graph_hash)
        self.assertEqual(['keep'],[p.name for p in out.iterdir()])
