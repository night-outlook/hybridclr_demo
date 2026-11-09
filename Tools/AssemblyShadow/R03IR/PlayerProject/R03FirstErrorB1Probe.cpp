// R03 B1 test-only native source witness. Added to the isolated IL2CPP
// composite overlay; does not modify production AOT/HybridCLR dispatch.
// File is exclusively preopened while healthy. This is NOT B2 descriptor-
// relative V2, a VM-wide coherent epoch, or a production recovery API.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE && HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#include "vm/AssemblyShadow.h"
#include <atomic>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace r03_ir_b1_probe {
using namespace il2cpp::vm::assembly_shadow_first_failure_v2;
static std::atomic<int32_t> stage{0}; // 0 unused, 1 preopened, 2 sealed, -1 failed
static int fd=-1;
static char runId[80]{}, caseId[100]{}, fixtureSha256[65]{};
// All I/O/JSON scratch is reserved at process initialization, not at failure.
static char quoted[6*kReasonLimit+1]{};

static bool Identifier(const char* p,size_t limit,size_t minimum,bool digest=false) noexcept {
    if (!p) return false;
    const size_t n=::strnlen(p,limit);
    if (n<minimum || n==limit || (digest && n!=64)) return false;
    for(size_t i=0;i<n;++i) {
        const unsigned char c=static_cast<unsigned char>(p[i]);
        const bool plain=(c>='0'&&c<='9')||(c>='a'&&c<='z')||
                         (c>='A'&&c<='Z')||c=='_'||c=='-'||c=='.';
        const bool hex=(c>='0'&&c<='9')||(c>='a'&&c<='f');
        if (!(digest?hex:plain)) return false;
    }
    return true;
}
static bool WriteAll(const char* p,size_t n) noexcept {
    unsigned interrupted=0;
    while(n) {
        const ssize_t bytes=::write(fd,p,n);
        if(bytes<0 && errno==EINTR && ++interrupted<=16) continue;
        if(bytes<=0 || static_cast<size_t>(bytes)>n) return false;
        interrupted=0;p+=bytes;n-=static_cast<size_t>(bytes);
    }
    return true;
}
static bool Encode(const char* p,size_t n,size_t& out) noexcept {
    out=0;
    static const char hex[]="0123456789abcdef";
    if(n>kReasonLimit) return false;
    for(size_t i=0;i<n;++i) {
        const unsigned char c=static_cast<unsigned char>(p[i]);
        if(c=='"'||c=='\\') { quoted[out++]='\\';quoted[out++]=static_cast<char>(c); }
        else if(c<0x20) {
            quoted[out++]='\\';quoted[out++]='u';
            quoted[out++]='0';quoted[out++]='0';
            quoted[out++]=hex[c>>4];quoted[out++]=hex[c&15];
        }
        else quoted[out++]=static_cast<char>(c);
    }
    quoted[out]='\0';
    return true;
}
static bool ValidFd() noexcept {
    struct stat st{};
    return fd>=0 && ::fstat(fd,&st)==0 && S_ISREG(st.st_mode) &&
           st.st_size==0 && st.st_nlink==1 && st.st_uid==::geteuid() &&
           (st.st_mode&07777)==0600;
}
} // namespace

extern "C" IL2CPP_EXPORT int32_t R03_IRB1_Open(
    const char* absolute, const char* run, const char* testcase, const char* fixture)
{
    using namespace r03_ir_b1_probe;
    int32_t expected=0;
    if(!stage.compare_exchange_strong(expected,-1,std::memory_order_acq_rel))
        return -1;
    const size_t pathLen=absolute?::strnlen(absolute,4096):0;
    if(pathLen<2||pathLen==4096||absolute[0]!='/'||
       !Identifier(run,sizeof(runId),24)||
       !Identifier(testcase,sizeof(caseId),1)||
       !Identifier(fixture,sizeof(fixtureSha256),64,true))
        return -2;
    // Final component must be absent and cannot be a symlink. Ancestor chain
    // is admitted independently by Local; B2 will own descriptor-relative
    // chain identity. Do not promote this file to a B2 receipt.
    fd=::open(absolute,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(!ValidFd()) { if(fd>=0) ::close(fd);fd=-1;return -3; }
    std::strcpy(runId,run);std::strcpy(caseId,testcase);
    std::strcpy(fixtureSha256,fixture);
    stage.store(1,std::memory_order_release);
    return 1;
}

extern "C" IL2CPP_EXPORT int32_t R03_IRB1_Seal(
    int32_t expectedCode, int32_t expectedOrigin)
{
    using namespace r03_ir_b1_probe;
    using il2cpp::vm::AssemblyShadow;
    int32_t expected=1;
    if(!stage.compare_exchange_strong(expected,-1,std::memory_order_acq_rel))
        return -1;
    Snapshot snap{};
    const State status=AssemblyShadow::FirstFailureV2Status();
    const bool frozen=AssemblyShadow::TryReadFirstFailureV2(snap);
    const int32_t code=frozen?snap.code:0;
    const int32_t origin=frozen?static_cast<int32_t>(snap.origin):0;
    const bool match=expectedCode==0
        ? (expectedOrigin==0 && status==State::Empty && !frozen)
        : (expectedCode>0 && expectedOrigin>0 && status==State::Frozen &&
           frozen && code==expectedCode && origin==expectedOrigin);
    size_t quotedBytes=0;
    if(frozen && !Encode(snap.reason,snap.length,quotedBytes)) return -2;
    char prefix[1024];
    const int count=std::snprintf(prefix,sizeof prefix,
        "{\"schemaVersion\":1,\"kind\":\"R03NativeFirstErrorB1Player\","
        "\"transport\":\"PreopenedNativeB1NotV2\","
        "\"runId\":\"%s\",\"caseId\":\"%s\",\"fixtureSha256\":\"%s\","
        "\"processId\":%lld,\"state\":%u,\"code\":%d,\"origin\":%d,"
        "\"reasonLength\":%llu,\"expectedCode\":%d,\"expectedOrigin\":%d,"
        "\"matchExpected\":%s,\"reason\":",
        runId,caseId,fixtureSha256,static_cast<long long>(::getpid()),
        static_cast<unsigned>(status),code,origin,
        static_cast<unsigned long long>(frozen?snap.length:0),
        expectedCode,expectedOrigin,match?"true":"false");
    static const char tail[]=
        ",\"nativeV2TransportImplemented\":false,\"firstRecoveryAuthenticatedV2\":false,"
        "\"wholeVmEpoch\":\"NotProven\",\"runtimeAcceptance\":false,"
        "\"R03Accepted\":false,\"H2Passed\":false}\n";
    const bool ok=count>0&&static_cast<size_t>(count)<sizeof prefix&&
        WriteAll(prefix,static_cast<size_t>(count))&&
        (frozen ? (WriteAll("\"",1)&&WriteAll(quoted,quotedBytes)&&WriteAll("\"",1))
                : WriteAll("null",4))&&
        WriteAll(tail,sizeof tail-1)&&::fsync(fd)==0;
    const int closed=::close(fd);fd=-1;
    if(!ok || closed!=0) return -3;
    stage.store(2,std::memory_order_release);
    return match?1:-4;
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRB1_Open(
    const char*,const char*,const char*,const char*) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRB1_Seal(int32_t,int32_t) { return 0; }
#endif
