// Real POSIX files and actual general serializer; VM snapshot is synthetic and
// prepared before watched code. Execution diagnostic bytes are caller fixtures.
#include "PosixDiagnosticTransaction.h"
#include "AssemblyShadowDiagnostics.h"
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace r03_diag_v2;
using namespace il2cpp::vm;
namespace fmt=il2cpp::vm::assembly_shadow_diagnostic;
extern bool watch;
extern size_t newCalls;
struct Ops:PosixIO {
    size_t count[9]{}; int selected=-1;size_t at=0;bool triggered=false,shortWrite=false,shortRead=false;
    void (*callback)(void*)=nullptr;void* context=nullptr;
    bool Fail(unsigned op) noexcept {++count[op];if(selected==int(op)&&count[op]==at){triggered=true;errno=EIO;return true;}return false;}
    int Open(const char*p,int f)noexcept{return Fail(0)?-1:PosixIO::Open(p,f);}
    int OpenAt(int d,const char*p,int f,mode_t m)noexcept{return Fail(1)?-1:PosixIO::OpenAt(d,p,f,m);}
    int Stat(int d,struct stat*s)noexcept{return Fail(2)?-1:PosixIO::Stat(d,s);}
    int StatAt(int d,const char*p,struct stat*s)noexcept{return Fail(3)?-1:PosixIO::StatAt(d,p,s);}
    ssize_t Write(int d,const void*p,size_t n)noexcept{
        if(callback){auto fn=callback;callback=nullptr;fn(context);}
        if(Fail(4))return -1;
        return PosixIO::Write(d,p,shortWrite&&n>7?7:n);
    }
    ssize_t ReadAt(int d,void*p,size_t n,off_t o)noexcept{return Fail(5)?-1:PosixIO::ReadAt(d,p,shortRead&&n>7?7:n,o);}
    int SyncFile(int d)noexcept{return Fail(6)?-1:PosixIO::SyncFile(d);}
    int SyncDirectory(int d)noexcept{return Fail(7)?-1:PosixIO::SyncDirectory(d);}
    int Close(int d)noexcept {bool bad=Fail(8);int result=PosixIO::Close(d);if(bad){errno=EIO;return -1;}return result;}
};
using Tx=PosixDiagnosticTransaction<Ops>;
static std::string Read(const char*p){std::ifstream f(p,std::ios::binary);assert(f);return {std::istreambuf_iterator<char>(f),{}};}
static void File(const std::string&p,const std::string&x){std::ofstream f(p,std::ios::binary);assert(f);f.write(x.data(),std::streamsize(x.size()));f.close();assert(f);}
static std::string Hex(Digest d){static const char* h="0123456789abcdef";std::string s;for(uint8_t b:d){s+=h[b>>4];s+=h[b&15];}return s;}
static Digest Parse(const char*p){Digest d{};assert(std::strlen(p)==64);for(size_t i=0;i<32;++i){auto h=[](char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;};int a=h(p[2*i]),b=h(p[2*i+1]);assert(a>=0&&b>=0);d[i]=uint8_t(a*16+b);}return d;}
static ShadowDiagnosticSnapshot Snapshot(size_t count){ShadowDiagnosticSnapshot s;s.enabled=true;s.state=AssemblyShadowState::FailedAfterCommit;s.lastError=AssemblyShadowError::ReferenceResolutionFailed;s.detail="same complete native snapshot\n\"\\";s.detail.push_back(0);s.detail+="\xc3\xa9\xe4\xb8\xad";s.generation=7;s.expected=3;s.staged=3;s.baselineBuildId="native-test";s.patchId="stream-test";s.startupObservationMode="EarlyTracking";for(size_t i=0;i<count;++i)s.ordinaryClasses.push_back({"Methods.R03","Namespace.Type_"+std::to_string(i),true,false,false});return s;}
struct CaptureSink{Capture* capture;static bool Write(void*p,const char*d,size_t n)noexcept{return static_cast<CaptureSink*>(p)->capture->Append(reinterpret_cast<const uint8_t*>(d),n);}};
struct Reentry{Tx* tx;static void Enter(void*p)noexcept{auto&s=*static_cast<Reentry*>(p);TransactionReceipt r;FieldView f[2]{};assert(!s.tx->Commit({},nullptr,0,f,nullptr,0,r));assert(!r.complete);}};
static void PrintFile(const FileIdentity&x){std::cout<<"{\"device\":"<<x.device<<",\"inode\":"<<x.inode<<",\"bytes\":"<<x.bytes<<",\"sha256\":\""<<Hex(x.sha256)<<"\"}";}
int main(int argc,char**argv){
    assert(argc==9);const std::string mode=argv[1],root=argv[2];std::string in=Read(argv[3]),execution=Read(argv[4]);Digest context=Parse(argv[5]);size_t classes=std::stoull(argv[6]);
    Ops io;io.selected=std::stoi(argv[7]);io.at=std::stoull(argv[8]);io.shortWrite=mode=="short-write";io.shortRead=mode=="short-read";
    auto snapshot=Snapshot(classes);std::string expectedGeneral=AssemblyShadowDiagnostics::Serialize(snapshot);
    const Digest generalHash=Sha256::Of(reinterpret_cast<const uint8_t*>(expectedGeneral.data()),expectedGeneral.size());
    std::vector<uint8_t> storage(kArtifactMax),scratch(kFrame);Capture capture(storage.data(),storage.size());CaptureSink target{&capture};FieldView fields[2]{};
    newCalls=0;watch=true;bool captured=capture.Begin(14,false);
    auto formatted=AssemblyShadowDiagnostics::SerializeTo(snapshot,{&target,CaptureSink::Write},kArtifactMax);
    captured=captured&&formatted.complete&&capture.End()&&capture.Begin(15,false)&&capture.Append(reinterpret_cast<const uint8_t*>(execution.data()),execution.size())&&capture.End()&&capture.Freeze();
    watch=false;size_t formatNew=newCalls;
    if(captured){assert(capture.View(14,fields[0])&&capture.View(15,fields[1]));assert(fields[0].size==expectedGeneral.size());assert(std::memcmp(fields[0].data,expectedGeneral.data(),fields[0].size)==0);}
    struct stat s{};assert(::stat(root.c_str(),&s)==0);DirectoryIdentity directory{s.st_dev,s.st_ino,s.st_uid};if(mode=="wrong-root")++directory.inode;
    TransactionReceipt receipt;TransactionFailure failure;bool armed=false,committed=false;size_t transactionNew=0;
    {
        Tx tx(io);Reentry reentry{&tx};
        newCalls=0;watch=true;armed=tx.Arm(root.c_str(),directory);watch=false;transactionNew+=newCalls;
        if(armed&&captured){
            if(mode=="rename-root"){assert(::rename(root.c_str(),(root+".moved").c_str())==0);assert(::mkdir(root.c_str(),0700)==0);}
            if(mode=="replace-artifact"){assert(::rename((root+"/diagnostics.r03v2").c_str(),(root+"/original.r03v2").c_str())==0);File(root+"/diagnostics.r03v2","do-not-touch");}
            if(mode=="hardlink"){assert(::link((root+"/diagnostics.r03v2").c_str(),(root+"/extra-link").c_str())==0);}
            if(mode=="reenter"){io.callback=&Reentry::Enter;io.context=&reentry;}
            newCalls=0;watch=true;committed=tx.Commit(context,reinterpret_cast<const uint8_t*>(in.data()),in.size(),fields,scratch.data(),scratch.size(),receipt);watch=false;transactionNew+=newCalls;
            if(mode=="repeat"){assert(committed);newCalls=0;watch=true;committed=tx.Commit(context,reinterpret_cast<const uint8_t*>(in.data()),in.size(),fields,scratch.data(),scratch.size(),receipt);watch=false;transactionNew+=newCalls;}
        }
        failure=tx.failure();
    }
    assert(!watch);assert(formatNew==0&&transactionNew==0);
    std::cout<<"{\"armed\":"<<(armed?"true":"false")<<",\"captured\":"<<(captured?"true":"false")<<",\"committed\":"<<(committed?"true":"false")<<",\"error\":"<<int(failure.error)<<",\"errno\":"<<failure.systemError<<",\"faultTriggered\":"<<(io.triggered?"true":"false")<<",\"formatNew\":"<<formatNew<<",\"transactionNew\":"<<transactionNew<<",\"generalBytes\":"<<expectedGeneral.size()<<",\"generalSha256\":\""<<Hex(generalHash)<<"\",\"calls\":[";
    for(size_t i=0;i<9;++i){if(i)std::cout<<',';std::cout<<io.count[i];}
    std::cout<<"],\"receipt\":{\"complete\":"<<(receipt.complete?"true":"false")<<",\"directory\":{\"device\":"<<receipt.directory.device<<",\"inode\":"<<receipt.directory.inode<<",\"owner\":"<<receipt.directory.owner<<"},\"artifact\":";PrintFile(receipt.artifact);std::cout<<",\"envelope\":";PrintFile(receipt.envelope);std::cout<<"}}\n";
}
