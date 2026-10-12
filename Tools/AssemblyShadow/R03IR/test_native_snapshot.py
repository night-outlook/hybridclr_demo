"""Compile actual test-only snapshot transport; no Unity/VM semantics are mocked as passing."""
import json,os,re,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
CS=ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs'

class NativeSnapshotTests(unittest.TestCase):
    def test_transport_and_exact_wire_schema(self):
        cpp=CPP.read_text(); cs=CS.read_text()
        fragment=cpp[cpp.index('// K test-only transport:'):cpp.index('extern "C" IL2CPP_EXPORT int32_t R03_IR_ProbeBooleanReserve()')]+ '\n#endif\n'
        fragment='\n'.join(x for x in fragment.splitlines() if not x.startswith('#include "gc/'))
        fields={name:re.findall(r'"(\w+)"',re.search(r'constexpr const char\* '+name+r'\[\] = \{([^}]+)\}',fragment)[1]) for name in ('IntNames','TextNames')}
        for name,call in [('IntNames','Int'),('TextNames','Text')]:
            mapping=re.findall(r'R03_IR_Report'+call+r'\((\d+), r\.(\w+)',cs)
            self.assertEqual(mapping,[(str(i),n) for i,n in enumerate(fields[name])])
        main=r'''
#include <cassert>
#include <string>
int main(int argc,char**argv){
 assert(argc==3);std::string mode=argv[2];
 if(mode=="occupied"||mode=="symlink") {assert(R03_IR_ReportOpen(argv[1])==-1);return 0;}
 assert(R03_IR_ReportOpen(argv[1])==1);
 if(mode=="double-open"){assert(R03_IR_ReportOpen(argv[1])==-1);return 0;}
 if(mode=="missing"){assert(R03_IR_ReportSeal()==-1);return 0;}
 if(mode=="index"){assert(R03_IR_ReportInt(-1,0)==-1);return 0;}
 if(mode=="bool"){assert(R03_IR_ReportInt(14,2)==-1);return 0;}
 if(mode=="long"){std::string large(262145,'a');assert(R03_IR_ReportText(0,large.c_str())==-1);return 0;}
 for(int i=0;i<25;++i)assert(R03_IR_ReportInt(i,i<14?i:0)==1);
 if(mode=="duplicate"){assert(R03_IR_ReportInt(0,0)==-1);return 0;}
 for(int i=0;i<16;++i)assert(R03_IR_ReportText(i,i==7?nullptr:"quote\" newline\n UTF8\xe4\xb8\xad")==1);
 assert(R03_IR_ReportSeal()==1);assert(R03_IR_ReportSeal()==-1);
}
'''
        cc=shutil.which('clang++') or shutil.which('g++');self.assertTrue(cc)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve(); source=root/'probe.cpp';exe=root/'probe'
            source.write_text('#include <cstdio>\n#include <cstring>\n#define IL2CPP_EXPORT\n#define HYBRIDCLR_R03_RUNTIME_PROBE 1\n'+fragment+main)
            flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic']
            if os.environ.get('R03_SANITIZERS')=='1':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            subprocess.run([cc,*flags,str(source),'-o',str(exe)],check=True,capture_output=True,text=True)
            for mode in ['success','occupied','symlink','double-open','missing','index','bool','long','duplicate']:
                target=root/(mode+'.json')
                if mode=='occupied':target.write_text('unchanged')
                if mode=='symlink':target.symlink_to(root/'occupied.json')
                run=subprocess.run([str(exe),str(target),mode],capture_output=True,text=True,timeout=20)
                self.assertEqual(run.returncode,0,(mode,run.stderr))
                if mode=='success':
                    raw=json.loads(target.read_text());self.assertEqual(raw['reportTransport'],'NativePreopenedSnapshotV1')
                    self.assertEqual(raw['initialState'],0);self.assertIsNone(raw['error']);self.assertIs(raw['acceptance'],False)
                    self.assertIn('UTF8中',raw['result'])
                if mode in ('occupied','symlink'):self.assertEqual(target.read_text(),'unchanged')
        self.assertNotIn('JsonUtility.ToJson',cs)
        self.assertNotIn('JsonUtility.FromJson<NativeGuard>',cs)

if __name__=='__main__':unittest.main()
