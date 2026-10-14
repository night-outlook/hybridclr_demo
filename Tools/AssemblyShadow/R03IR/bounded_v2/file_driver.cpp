// Host-only real POSIX fixture. No Unity/VM, scheduler, or product data.
#include "BoundedDiagnosticsFiles.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <new>
#include <string>
#include <vector>

extern bool watchNew;
extern unsigned newCalls;
using namespace r03_diag_v2;
struct Ops : PosixFileOps {
    static inline std::string scenario;
    static inline int artifact=-1,envelope=-1;
    static inline unsigned openCount=0,closeCount=0,writeCalls=0,readCalls=0,syncCalls=0,fullCalls=0,dirSyncs=0;
    static inline unsigned artifactSyncOrder=0,envelopeFirstOrder=0,envelopeSyncOrder=0,sequence=0;
    static inline bool injected=false,afterPrepare=false;
    static inline void (*reenter)()=nullptr;
    static bool Fault(const char* s) noexcept {return scenario==s&&!injected;}
    static int OpenRoot() noexcept {
        if(Fault("open-root")){injected=true;errno=EACCES;return -1;}
        int fd=PosixFileOps::OpenRoot();if(fd>=0)++openCount;return fd;
    }
    static int OpenAt(int parent,const char* name,int flags,mode_t mode) noexcept {
        bool a=std::strcmp(name,kArtifactName)==0,e=std::strcmp(name,kEnvelopeName)==0;
        if((!a&&!e&&Fault("open-dir"))||(a&&Fault("open-artifact"))||(e&&Fault("open-envelope")))
        {injected=true;errno=EACCES;return -1;}
        int fd=PosixFileOps::OpenAt(parent,name,flags,mode);if(fd>=0){++openCount;if(a)artifact=fd;if(e)envelope=fd;}return fd;
    }
    static int Stat(int fd,struct stat* st) noexcept {
        if(Fault("stat")){injected=true;errno=EIO;return -1;}return PosixFileOps::Stat(fd,st);
    }
    static int StatAt(int fd,const char* name,struct stat* st) noexcept {
        if(Fault("stat-at")){injected=true;errno=EIO;return -1;}return PosixFileOps::StatAt(fd,name,st);
    }
    static ssize_t Write(int fd,const uint8_t* p,size_t n) noexcept {
        ++writeCalls;++sequence;if(fd==envelope&&!envelopeFirstOrder)envelopeFirstOrder=sequence;
        if(Fault("reenter")&&reenter){injected=true;reenter();}
        if((fd==artifact&&Fault("write-artifact"))||(fd==envelope&&Fault("write-envelope")))
        {injected=true;errno=EIO;return -1;}
        if(Fault("zero-write")){injected=true;return 0;}
        if(Fault("invalid-write-count")){injected=true;return ssize_t(n+1);}
        if(Fault("eintr-write")){injected=true;errno=EINTR;return -1;}
        if(scenario=="eintr-write-forever"){errno=EINTR;return -1;}
        if(scenario=="short-write")n=std::min(n,size_t(37));
        return PosixFileOps::Write(fd,p,n);
    }
    static ssize_t ReadAt(int fd,uint8_t* p,size_t n,off_t at) noexcept {
        ++readCalls;
        if((fd==artifact&&Fault("read-artifact"))||(fd==envelope&&Fault("read-envelope")))
        {injected=true;errno=EIO;return -1;}
        if(Fault("zero-read")){injected=true;return 0;}
        if(Fault("invalid-read-count")){injected=true;return ssize_t(n+1);}
        if(Fault("eintr-read")){injected=true;errno=EINTR;return -1;}
        if(scenario=="eintr-read-forever"){errno=EINTR;return -1;}
        if(scenario=="short-read")n=std::min(n,size_t(71));
        return PosixFileOps::ReadAt(fd,p,n,at);
    }
    static int Sync(int fd) noexcept {
        ++syncCalls;++sequence;
        bool isDir=fd!=artifact&&fd!=envelope;
        if(isDir)++dirSyncs;
        if((fd==artifact&&Fault("sync-artifact"))||(fd==envelope&&Fault("sync-envelope"))||
           (isDir&&dirSyncs==1&&Fault("sync-dir-first"))||(isDir&&dirSyncs==2&&Fault("sync-dir-last")))
        {injected=true;errno=EIO;return -1;}
        if(fd==artifact&&Fault("mutate-after-artifact-check")){
            injected=true;const char c='X';if(::pwrite(fd,&c,1,0)!=1)std::abort();
        }
        if(fd==envelope&&Fault("mutate-before-final-check")){
            injected=true;const char c='X';if(::pwrite(artifact,&c,1,0)!=1)std::abort();
        }
        return PosixFileOps::Sync(fd);
    }
    static int FullSync(int fd) noexcept {
        ++fullCalls;++sequence;
        if((fd==artifact&&Fault("full-artifact"))||(fd==envelope&&Fault("full-envelope")))
        {injected=true;errno=ENOTSUP;return -1;}
        const int result=PosixFileOps::FullSync(fd);
        if(result==0){if(fd==artifact)artifactSyncOrder=sequence;else envelopeSyncOrder=sequence;}return result;
    }
    static int Close(int fd) noexcept {
        ++closeCount;
        const int rc=PosixFileOps::Close(fd);
        if((fd==artifact&&Fault("close-artifact"))||(fd==envelope&&Fault("close-envelope"))||
           (fd!=artifact&&fd!=envelope&&Fault("close-dir"))||Fault("close-eintr")){
            injected=true;errno=scenario=="close-eintr"?EINTR:EIO;return -1;
        }
        return rc;
    }
    static pid_t Process() noexcept {return PosixFileOps::Process()+(afterPrepare&&scenario=="process-changed"?1:0);}
};
static FileTransaction<Ops>* active=nullptr;
static void Reenter() {active->Prepare("/",FileIdentity{},Digest{});}
static std::string HexDigest(Digest d){std::string s;const char* h="0123456789abcdef";for(auto c:d){s+=h[c>>4];s+=h[c&15];}return s;}
static bool Eq(const char* a){return Ops::scenario==a;}
static void Must(bool value){if(!value){std::cerr<<"Host fixture setup failed\n";std::exit(99);}}
static std::string ReadFile(const char* p){std::ifstream f(p,std::ios::binary);Must(bool(f));return std::string(std::istreambuf_iterator<char>(f),{});}
int main(int argc,char** argv){
    if(argc!=5)return 99;
    const std::string root=argv[1];Ops::scenario=argv[2];
    std::string inlineText=ReadFile(argv[3]);std::string contextHex=argv[4];
    if(contextHex=="-"){std::cout<<"{\"readyPid\":"<<::getpid()<<"}\n"<<std::flush;std::getline(std::cin,contextHex);}
    // Host controller sets binding independent of runtime data; PID is bound in
    // returned receipt. The controller verifies all contextual hashes afterward.
    if(contextHex.size()!=64)return 99;
    Digest context{};for(size_t i=0;i<32;++i){char b[3]={contextHex[2*i],contextHex[2*i+1],0};context[i]=uint8_t(std::strtoul(b,nullptr,16));}
    struct stat st{};Must(::stat(root.c_str(),&st)==0);
    FileIdentity expected=FileIdentity::From(st);if(Eq("wrong-root-identity"))++expected.inode;
    std::string a="{\"data\":\""+std::string(300000,'a')+"\"}";
    std::string b="{\"data\":\""+std::string(350000,'b')+"\"}";
    if(Eq("unicode")){a="{\"data\":\"";for(size_t i=0;i<100000;++i)a+="\xf0\x9f\x98\x80";a+="\"}";}
    if(Eq("empty")){a.clear();b.clear();}
    if(Eq("null")){a.clear();b.clear();}
    if(Eq("invalid-utf8"))a="\xff";
    if(Eq("overflow"))a.assign(kArtifactMax,'x');
    if(Eq("boundary")){
        size_t n=kArtifactMax-192-300011;
        while(n){size_t wire=0;if(WireSize(a.size(),n,wire)&&wire==kArtifactMax)break;--n;}
        Must(n>20);b="{\"data\":\""+std::string(n-11,'b')+"\"}";
    }
    FieldView fields[2]={{reinterpret_cast<const uint8_t*>(a.data()),a.size(),Eq("null")},
                         {reinterpret_cast<const uint8_t*>(b.data()),b.size(),Eq("null")}};
    std::vector<uint8_t> scratch(kFrame);
    FileReceipt receipt,second;FileFailure failure,repeatFailure;
    bool prepared=false,committed=false,secondOk=false;unsigned newAtPrepare=0,newAtCommit=0;
    std::string preparePath=root;
    if(Eq("relative"))preparePath="relative";
    if(Eq("trailing"))preparePath+="/";
    if(Eq("dot"))preparePath+="/.";
    if(Eq("double-slash"))preparePath="/"+preparePath;
    if(Eq("path-too-long"))preparePath=std::string(kPathBytes,'x');
    {
        FileTransaction<Ops> txn;active=&txn;Ops::reenter=Reenter;
        watchNew=true;prepared=txn.Prepare(preparePath.c_str(),expected,context);watchNew=false;newAtPrepare=newCalls;
        Ops::afterPrepare=true;
        if(prepared){
            if(Eq("artifact-replaced")){
                Must(::rename((root+"/"+kArtifactName).c_str(),(root+"/original-artifact").c_str())==0);
                int fd=::open((root+"/"+kArtifactName).c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);Must(fd>=0);::close(fd);
            }
            if(Eq("envelope-replaced")){
                Must(::rename((root+"/"+kEnvelopeName).c_str(),(root+"/original-envelope").c_str())==0);
                int fd=::open((root+"/"+kEnvelopeName).c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);Must(fd>=0);::close(fd);
            }
            if(Eq("artifact-hardlinked"))Must(::link((root+"/"+kArtifactName).c_str(),(root+"/second-link").c_str())==0);
            if(Eq("directory-permission"))Must(::chmod(root.c_str(),0777)==0);
            if(Eq("directory-replaced")){
                Must(::rename(root.c_str(),(root+"-original").c_str())==0);Must(::mkdir(root.c_str(),0700)==0);
            }
            if(Eq("ancestor-replaced")){
                size_t end=root.rfind('/');std::string parent=root.substr(0,end),leaf=root.substr(end+1);
                Must(::rename(parent.c_str(),(parent+"-original").c_str())==0);Must(::mkdir(parent.c_str(),0700)==0);Must(::mkdir((parent+"/"+leaf).c_str(),0700)==0);
            }
            watchNew=true;
            committed=txn.Commit(reinterpret_cast<const uint8_t*>(inlineText.data()),inlineText.size(),fields,scratch.data(),scratch.size(),receipt);
            watchNew=false;newAtCommit=newCalls-newAtPrepare;
            if(Eq("repeat")){secondOk=txn.Commit(reinterpret_cast<const uint8_t*>(inlineText.data()),inlineText.size(),fields,scratch.data(),scratch.size(),second);repeatFailure=txn.failure();}
        }
        failure=txn.failure();active=nullptr;
    }
    std::cout<<"{\"prepared\":"<<prepared<<",\"committed\":"<<committed<<",\"complete\":"<<receipt.complete
      <<",\"error\":"<<unsigned(failure.error)<<",\"stage\":"<<unsigned(failure.stage)<<",\"errno\":"<<failure.systemError
      <<",\"acceptedArtifact\":"<<failure.artifactBytes<<",\"acceptedEnvelope\":"<<failure.envelopeBytes
      <<",\"artifactBytes\":"<<receipt.artifactBytes<<",\"envelopeBytes\":"<<receipt.envelopeBytes
      <<",\"artifactSha256\":\""<<HexDigest(receipt.artifactSha256)<<"\",\"envelopeSha256\":\""<<HexDigest(receipt.envelopeSha256)
      <<"\",\"inlineSha256\":\""<<HexDigest(receipt.inlineSha256)<<"\",\"binding\":\""<<HexDigest(receipt.binding)
      <<"\",\"processId\":"<<receipt.processId<<",\"actualPid\":"<<::getpid()<<",\"appleFullFileSync\":"<<receipt.appleFullFileSync
      <<",\"artifactInode\":"<<receipt.artifact.inode<<",\"envelopeInode\":"<<receipt.envelope.inode
      <<",\"newAtPrepare\":"<<newAtPrepare<<",\"newAtCommit\":"<<newAtCommit
      <<",\"openCount\":"<<Ops::openCount<<",\"closeCount\":"<<Ops::closeCount<<",\"writeCalls\":"<<Ops::writeCalls
      <<",\"readCalls\":"<<Ops::readCalls<<",\"syncCalls\":"<<Ops::syncCalls<<",\"fullCalls\":"<<Ops::fullCalls
      <<",\"artifactSyncOrder\":"<<Ops::artifactSyncOrder<<",\"envelopeFirstOrder\":"<<Ops::envelopeFirstOrder
      <<",\"envelopeSyncOrder\":"<<Ops::envelopeSyncOrder<<",\"secondOk\":"<<secondOk
      <<",\"secondComplete\":"<<second.complete<<",\"repeatError\":"<<unsigned(repeatFailure.error)
      <<",\"transactionBytes\":"<<sizeof(FileTransaction<Ops>)<<",\"actualUnity\":false}\n";
    return 0;
}
