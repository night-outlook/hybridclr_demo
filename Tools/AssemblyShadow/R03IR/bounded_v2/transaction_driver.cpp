// Host-only integration driver: synthetic frozen fields -> actual encoder ->
// actual POSIX transaction. Never used as a Unity plugin or runtime producer.
#include "PosixDiagnosticTransaction.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <new>
#include <string>
#include <vector>
#include <algorithm>

static bool track=false;static size_t allocations=0;
void* operator new(std::size_t n) { if(track)++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc(); }
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept {std::free(p);}
void operator delete[](void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
void operator delete[](void* p,std::size_t) noexcept {std::free(p);}

using namespace r03_diag_v2;
static const char* events[16384]{};static size_t eventCount=0,failAt=0;
static std::string mode;
static bool altered=false;
static int liveDescriptors[256]{};static size_t liveCount=0;
static bool duplicateClose=false,allCloseOnExec=true;
static int opened(int fd){if(fd>=0){if(liveCount==256)std::abort();liveDescriptors[liveCount++]=fd;
    allCloseOnExec=allCloseOnExec&&((::fcntl(fd,F_GETFD)&FD_CLOEXEC)!=0);}return fd;}
static void (*reenter)()=nullptr;
struct TestOps:PosixFileOps {
    static bool Event(const char* op) noexcept {
        if(eventCount>=16384)std::abort();
        events[eventCount++]=op;
        if(eventCount==failAt){errno=EIO;return true;}return false;
    }
    static int OpenRoot() noexcept {return Event("root-open")?-1:opened(PosixFileOps::OpenRoot());}
    static int OpenAt(int f,const char* p,int flags,mode_t m) noexcept {
        return Event((flags&O_CREAT)?"file-open":"directory-open")?-1:opened(PosixFileOps::OpenAt(f,p,flags,m));
    }
    static int Stat(int f,struct stat* s) noexcept {return Event("fstat")?-1:PosixFileOps::Stat(f,s);}
    static int StatAt(int f,const char* p,struct stat* s) noexcept {return Event("fstatat")?-1:PosixFileOps::StatAt(f,p,s);}
    static ssize_t Write(int f,const uint8_t* p,size_t n) noexcept {
        if(Event("write"))return -1;
        if(mode=="reentry"&&!altered){altered=true;reenter();}
        if(mode=="zero-write")return 0;
        if(mode=="all-eintr"){errno=EINTR;return -1;}
        if(mode=="one-eintr"&&!altered){altered=true;errno=EINTR;return -1;}
        if(mode=="short-write")n=std::min(n,size_t(7));
        return PosixFileOps::Write(f,p,n);
    }
    static ssize_t ReadAt(int f,uint8_t* p,size_t n,off_t o) noexcept {
        if(Event("pread"))return -1;
        const ssize_t result=PosixFileOps::ReadAt(f,p,n,o);
        if(mode=="bad-readback"&&result>0)p[0]^=1;
        return result;
    }
    static int Sync(int f,bool d) noexcept {
        if(Event(d?"directory-sync":"file-sync"))return -1;
        const int result=PosixFileOps::Sync(f,d);
        if(!d && result==0 && mode=="mutate-after-sync" && !altered){
            altered=true;const uint8_t corrupt='X';if(::pwrite(f,&corrupt,1,0)!=1)std::abort();
        }
        return result;
    }
    static int Close(int f) noexcept {
        const bool fail=Event("close");
        size_t i=0;while(i<liveCount&&liveDescriptors[i]!=f)++i;
        if(i==liveCount)duplicateClose=true;else liveDescriptors[i]=liveDescriptors[--liveCount];
        const int rc=PosixFileOps::Close(f);
        if(fail){errno=EIO;return -1;}return rc;
    }
};
static PosixDiagnosticTransaction<TestOps>* active=nullptr;
static void Reenter(){const uint8_t x=0;active->AppendArtifact(&x,1);}
static uint32_t number(const std::vector<uint8_t>& data,size_t& at){
    if(at+4>data.size())throw std::runtime_error("short fixture");
    uint32_t v=0;for(int i=0;i<4;++i)v=(v<<8)|data[at++];return v;
}
static std::vector<uint8_t> take(const std::vector<uint8_t>& data,size_t& at,size_t n){
    if(n>data.size()-at)throw std::runtime_error("short fixture");
    auto b=data.begin()+static_cast<ptrdiff_t>(at);at+=n;return {b,b+static_cast<ptrdiff_t>(n)};
}
static void hex(Digest d){for(uint8_t c:d)std::printf("%02x",unsigned(c));}
static void identity(const FileIdentity& f){
    std::printf("{\"device\":%llu,\"inode\":%llu,\"owner\":%llu,\"mode\":%llu,\"bytes\":%llu,\"sha256\":\"",
        (unsigned long long)f.device,(unsigned long long)f.inode,(unsigned long long)f.owner,
        (unsigned long long)f.mode,(unsigned long long)f.bytes);hex(f.sha256);std::printf("\"}");
}
int main(int argc,char** argv){
    if(argc!=5)return 90;
    const std::string root=argv[1];mode=argv[3];failAt=std::strtoull(argv[4],nullptr,10);
    std::ifstream in(argv[2],std::ios::binary);if(!in)return 91;
    std::vector<uint8_t> fixture((std::istreambuf_iterator<char>(in)),{});size_t pos=0;
    const auto contextBytes=take(fixture,pos,32), inlineBytes=take(fixture,pos,32);
    Digest context{},inlineHash{};std::copy(contextBytes.begin(),contextBytes.end(),context.begin());
    std::copy(inlineBytes.begin(),inlineBytes.end(),inlineHash.begin());
    const auto inlineSize=number(fixture,pos);auto envelope=take(fixture,pos,number(fixture,pos));
    std::vector<uint8_t> data[2];FieldView fields[2];
    for(int i=0;i<2;++i){bool null=number(fixture,pos)!=0;data[i]=take(fixture,pos,number(fixture,pos));fields[i]={data[i].data(),data[i].size(),null};}
    if(pos!=fixture.size())return 92;
    std::vector<uint8_t> scratch(kFrame);
    struct stat admitted{};if(::stat(root.c_str(),&admitted))return 93;
    bool prepared=false,encoded=false,sealed=false,committed=false;
    FileFailure failure;TransactionReceipt receipt;
    {
    PosixDiagnosticTransaction<TestOps> tx;active=&tx;reenter=&Reenter;
    Receipt wire;
    track=true;prepared=tx.Prepare(root.c_str(),uint64_t(admitted.st_dev),uint64_t(admitted.st_ino)+(mode=="wrong-root"?1:0));track=false;
    if(prepared&&mode=="rename-directory"){
        if(::rename(root.c_str(),(root+".moved").c_str())||::mkdir(root.c_str(),0700))return 94;
    }
    if(prepared&&mode=="hardlink"){
        if(::link((root+"/"+kDiagnosticFile).c_str(),(root+"/another-link").c_str()))return 95;
    }
    if(prepared&&mode=="replace-file"){
        if(::rename((root+"/"+kDiagnosticFile).c_str(),(root+"/retained-original").c_str()))return 96;
        const int f=::open((root+"/"+kDiagnosticFile).c_str(),O_CREAT|O_EXCL|O_WRONLY,0600);if(f<0)return 97;::close(f);
    }
    if(prepared&&mode=="early-envelope"){
        track=true;committed=tx.CommitEnvelope(envelope.data(),envelope.size());track=false;
    }else if(prepared){
        Encoder encoder;
        track=true;
        encoded=encoder.Encode(context,inlineHash,inlineSize,fields,scratch.data(),scratch.size(),
            &PosixDiagnosticTransaction<TestOps>::ArtifactSink,&tx,wire);
        if(mode=="wrong-receipt")wire.sha256[0]^=1;
        if(encoded)sealed=tx.FinishArtifact(wire);
        if(sealed)committed=tx.CommitEnvelope(envelope.data(),envelope.size());
        if(mode=="repeat"&&committed)committed=tx.CommitEnvelope(envelope.data(),envelope.size());
        track=false;
    }
    failure=tx.failure();receipt=tx.receipt();
    // Verify immutable first cause with a deliberately late invalid call.
    if(failure.error!=FileError::None){tx.CommitEnvelope(nullptr,0);if(tx.failure().error!=failure.error||
        tx.failure().operation!=failure.operation||tx.failure().systemError!=failure.systemError)return 98;}
    } // All handles closed once before diagnostics, including failed paths.
    std::printf("{\"prepared\":%s,\"encoded\":%s,\"artifactSealed\":%s,\"committed\":%s,\"error\":%u,\"operation\":\"%s\",\"errno\":%d,\"operatorNewCalls\":%zu,\"transactionBytes\":%zu,\"receipt\":{\"kind\":\"R03PosixDiagnosticTransactionV2\",\"complete\":%s,\"syncPolicy\":\"%s\",\"root\":",
        prepared?"true":"false",encoded?"true":"false",sealed?"true":"false",committed?"true":"false",
        unsigned(failure.error),failure.operation,failure.systemError,allocations,sizeof(PosixDiagnosticTransaction<TestOps>),receipt.complete?"true":"false",receipt.syncPolicy);
    identity(receipt.root);std::printf(",\"artifact\":");identity(receipt.artifact);std::printf(",\"envelope\":");identity(receipt.envelope);std::printf("},\"events\":[");
    for(size_t i=0;i<eventCount;++i)std::printf("%s\"%s\"",i?",":"",events[i]);
    std::printf("],\"openDescriptors\":%zu,\"duplicateClose\":%s,\"allCloseOnExec\":%s}\n",liveCount,duplicateClose?"true":"false",allCloseOnExec?"true":"false");return 0; // Harness result only: committed is checked by Python.
}
