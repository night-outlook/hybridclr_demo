"""Actual native snapshot/emitter and serializer tests; no Unity runtime claim.

The C# emitter call plan is mechanically translated for native faults. A separate
managed integration test executes the actual C# method through real P/Invoke.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from snapshot_test_support import prepare, body
from snapshot_serializer_fixture import stub as SERIALIZER_STUB, main as SERIALIZER_MAIN

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / 'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
CS = ROOT / 'R03IR/PlayerProject/R03TerminalPlayer.cs'
NATIVE = ROOT.parents[2] / 'il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp'
SCENARIOS = {
 'baseline':None,'type':None,'off':None,'unicode':None,'failed-semantic':None,
 'at-limit':None,'repeat-seal':('seal',2),'no-open':('int',2),
 'relative-open':('open',3),'fdopen':('fdopen',5),'repeat-open':('open',2),
 'occupied':('open',4),'symlink':('open',4),'wrong-thread-reentry':('int',1),
 'invalid-int':('int',6),'invalid-text':('text',6),'invalid-bool':('int',8),
 'duplicate-int':('int',7),'duplicate-text':('text',7),'missing-int':('missing-int',11),
 'missing-text':('missing-text',12),'over-limit':('text',9),'write':('write',13),
 'flush':('flush',14),'fsync':('fsync',15),'close':('close',16),
}

class SnapshotDiagnostics(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(strict=True)
        self.compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertTrue(self.compiler, 'C++17 compiler required, no skipped controls')
        self.flags = ['-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread']
        if os.environ.get('R03_SANITIZERS') == '1':
            self.flags += ['-fsanitize=address,undefined','-fno-omit-frame-pointer']

    def invoke(self, argv):
        p = subprocess.run(argv,capture_output=True,timeout=45)
        self.assertEqual(p.returncode,0,p.stderr.decode(errors='replace')[-8000:])
        return p

    def compile(self, code, name):
        source, exe = self.root/(name+'.cpp'), self.root/name
        source.write_text(code)
        self.invoke([self.compiler,*self.flags,str(source),'-o',str(exe)])
        return exe

    def test_actual_emitter_all_native_store_and_io_paths(self):
        exe = self.compile(prepare(CPP, CS), 'writer')
        for mode, expected in SCENARIOS.items():
            with self.subTest(mode=mode):
                raw = self.root/(mode+'.json')
                if mode=='occupied': raw.write_text('preserve')
                if mode=='symlink':
                    target=self.root/'target';target.write_text('preserve');raw.symlink_to(target)
                p=self.invoke([str(exe),mode,str(raw)])
                failures=re.findall(rb'\[R03SnapshotFailure\] [^\n]+',p.stderr)
                if expected:
                    self.assertEqual(len(failures),1)
                    self.assertIn(('operation='+expected[0]).encode(),failures[0])
                    self.assertIn(('reason='+str(expected[1])+' ').encode(),failures[0])
                else:
                    self.assertFalse(failures)
                    doc=json.loads(raw.read_bytes())
                    self.assertEqual(doc['result'],'Failed' if mode=='failed-semantic' else 'Passed')
                    if mode=='baseline': self.assertEqual(json.loads(doc['nativeGuardJson'])['caughtOldGuard'],1)
                    if mode=='at-limit': self.assertEqual(len(doc['finalExecutionDiagnostics']),262144)
                if mode in ('occupied','symlink'): self.assertEqual(raw.read_text(),'preserve')

    def test_actual_1024_class_producer_roundtrips_without_truncation(self):
        self.assertTrue(NATIVE.is_file(), 'Pinned sibling native source required')
        function=body(NATIVE.read_text(),'AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson')
        self.assertEqual(hashlib.sha256(function.encode()).hexdigest(),
                         '051497faf816e4094b8f4e8f194c5b877812cee034c6901c755e8b6efdff9c40')
        producer=self.compile(SERIALIZER_STUB+function+SERIALIZER_MAIN,'producer')
        datafile=self.root/'producer.json';self.invoke([str(producer),str(datafile)])
        data=datafile.read_bytes()
        self.assertEqual(len(json.loads(data)['classes']),1024)
        self.assertEqual(len(data),331078)
        code=prepare(CPP,CS).replace('assert(argc==3);','assert(argc==4);')
        code='#include <fstream>\n#include <iterator>\n'+code
        code=code.replace(' std::string text;',r'''
 std::string text;
 if(mode=="producer-json") {
   std::ifstream input(argv[3],std::ios::binary);
   text.assign(std::istreambuf_iterator<char>(input),std::istreambuf_iterator<char>());
   assert(text.size()==331078);r.finalExecutionDiagnostics=text.c_str();
 }
''')
        writer=self.compile(code,'combined')
        raw=self.root/'raw.json';p=self.invoke([str(writer),'producer-json',str(raw),str(datafile)])
        self.assertNotIn(b'[R03SnapshotFailure]',p.stderr)
        self.assertEqual(json.loads(raw.read_bytes())['finalExecutionDiagnostics'].encode(),data)
        metrics=re.search(rb'inputBytes=(\d+) storedBytes=(\d+) totalTextBytes=(\d+) totalTextLimit=(\d+)',p.stderr)
        self.assertIsNotNone(metrics)
        size,stored,total,limit=map(int,metrics.groups())
        self.assertEqual(size,len(data));self.assertLessEqual(stored,262144)
        self.assertLessEqual(total,limit);self.assertEqual(limit,16*262144)

    def test_packing_corruption_and_original_aggregate_budget_fail_closed(self):
        code=prepare(CPP,CS)
        at=code.index('int main(');code=code[:at]+r'''
int main(int argc,char**argv) {
 assert(argc==3);std::string mode=argv[1]; (void)&EmitNativeReport;
 assert(R03_IR_ReportOpen(argv[2])==1);
 using namespace r03_ir_snapshot;
 for(int i=0;i<25;++i)assert(R03_IR_ReportInt(i,0)==1);
 std::string diagnostic;
 for(int i=0;i<40000;++i)diagnostic+="\"hasInitializationException\":";
 if(mode=="aggregate") {
   std::string large(262144,'x');
   for(int i=0;i<5;++i)assert(R03_IR_ReportText(i,large.c_str())==1);
   while(diagnostic.size()<3200000)diagnostic+="\"hasInitializationException\":";
   assert(R03_IR_ReportText(15,diagnostic.c_str())==-1);
   assert(firstFailure.load()==18);assert(R03_IR_ReportSeal()==-1);return 0;
 }
 if(mode=="input-budget") {
   diagnostic.assign(OriginalReportTextBudget+1,'a');
   assert(R03_IR_ReportText(15,diagnostic.c_str())==-1);
   assert(firstFailure.load()==18);return 0;
 }
 diagnostic+="tail";
 assert(R03_IR_ReportText(15,diagnostic.c_str())==1);
 assert(packedExecution && CheckPackedExecution());
 for(int i=0;i<15;++i)assert(R03_IR_ReportText(i,nullptr)==1);
 if(mode=="token"){texts[15][1]=static_cast<char>(254);}
 if(mode=="truncated"){packedBytes=1;texts[15][0]=static_cast<char>(255);}
 if(mode=="length"){++executionDecodedBytes;}
 if(mode=="literal-flip"){texts[15][packedBytes-1] ^= 1;}
 if(mode=="length-short"){executionDecodedBytes=0;}
 if(mode=="stored-bound"){packedBytes=TextLimit+1;}
 if(mode=="duplicate"){assert(R03_IR_ReportText(15,"again")==-1);assert(firstFailure.load()==7);}
 assert(R03_IR_ReportSeal()==-1);
 if(mode!="duplicate")assert(firstFailure.load()==17);
 return 0;
}
'''
        exe=self.compile(code,'negative')
        for mode in ('aggregate','input-budget','token','truncated','length','length-short','stored-bound','literal-flip','duplicate'):
            with self.subTest(mode=mode):
                raw=self.root/(mode+'.json');p=self.invoke([str(exe),mode,str(raw)])
                self.assertEqual(raw.stat().st_size,0)
                self.assertEqual(p.stderr.count(b'[R03SnapshotFailure]'),1)

    def test_unchanged_schema_storage_arrays_and_full_seal(self):
        cpp=CPP.read_text();cs=CS.read_text()
        self.assertIn('constexpr size_t TextLimit = 262144;',cpp)
        self.assertIn('static char texts[TextCount][TextLimit + 1] = {};',cpp)
        self.assertIn('OriginalReportTextBudget = TextCount * TextLimit',cpp)
        self.assertIn('int seal = R03_IR_ReportSeal();',cs)
        self.assertIn('return ok && seal == 1;',cs)
        self.assertIn('if (r.stimulus != "baseline-owner")',cs)
        self.assertIn('report.finalShadowField == report.preShadowField',cs)
        self.assertIn('exact_int(raw.get(\'finalShadowField\'), 2)',(ROOT/'R03IR/run_terminal_local.py').read_text())

if __name__=='__main__': unittest.main()
