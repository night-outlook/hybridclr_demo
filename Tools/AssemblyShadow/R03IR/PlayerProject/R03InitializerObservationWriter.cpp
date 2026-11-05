// Test-only initializer observation writer. Not a V2 terminal snapshot.
// The output is preopened while healthy; no managed file writes follow Commit.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(int32_t*,int32_t*,int32_t*,int32_t*,int32_t*);

namespace r03_irw_output {
static std::atomic<int32_t> state{0}; // 0 unused, 1 opened, 2 sealed, -1 invalid
static int fd=-1;
static char runId[96]{}, caseId[96]{}, stimulus[32]{}, digest[65]{};
static bool Safe(const char* p,size_t cap,bool isDigest) noexcept
{
    if (!p) return false;
    size_t n=::strnlen(p,cap);
    if (!n || n==cap || (isDigest && n!=64)) return false;
    for(size_t i=0;i<n;++i)
    {
        const char c=p[i];
        const bool ascii=(c>='a'&&c<='z')||(c>='A'&&c<='Z')||
                         (c>='0'&&c<='9')||c=='-'||c=='_'||c=='.';
        const bool hex=(c>='0'&&c<='9')||(c>='a'&&c<='f');
        if(!(isDigest?hex:ascii)) return false;
    }
    return true;
}
static bool WriteAll(const char* data,size_t n) noexcept
{
    unsigned retries=0;
    while(n)
    {
        ssize_t wrote=::write(fd,data,n);
        if(wrote<0)
        {
            if(errno==EINTR && ++retries<=8) continue;
            return false;
        }
        if(wrote==0 || static_cast<size_t>(wrote)>n) return false;
        retries=0; data+=wrote; n-=static_cast<size_t>(wrote);
    }
    return true;
}
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(
    const char* path,const char* run,const char* caseName,
    const char* mode,const char* sha)
{
    using namespace r03_irw_output;
    int32_t expected=0;
    if(!state.compare_exchange_strong(expected,1)) return -1;
    if(!path || path[0]!='/' || ::strnlen(path,4096)==4096 ||
       !Safe(run,sizeof(runId),false) || ::strlen(run)<24 ||
       !Safe(caseName,sizeof(caseId),false) ||
       !Safe(mode,sizeof(stimulus),false) ||
       !(::strcmp(mode,"initializer-control")==0 ||
         ::strcmp(mode,"initializer-failure")==0) ||
       !Safe(sha,sizeof(digest),true))
    { state.store(-1); return -2; }
    int target=::open(path,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW,0600);
    if(target<0) { state.store(-1); return -3; }
    struct stat info{};
    if(::fstat(target,&info)!=0 || !S_ISREG(info.st_mode) ||
       (info.st_mode&0777)!=0600 || info.st_nlink!=1)
    { ::close(target); state.store(-1); return -4; }
    ::strcpy(runId,run);::strcpy(caseId,caseName);
    ::strcpy(stimulus,mode);::strcpy(digest,sha);
    fd=target;
    return 1;
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(
    int32_t commit,int32_t finalState,int32_t canaryBefore,int32_t canaryAfter,
    int32_t attempted,int32_t succeeded)
{
    using namespace r03_irw_output;
    int32_t expected=1;
    if(!state.compare_exchange_strong(expected,-1) || fd<0) return -1;
    int32_t field=-1,preField=-1,ready=-1,positiveMask=-1,calls=-1;
    const int rc=R03_IRW_ReadPrepared(&field,&preField,&ready,&positiveMask,&calls);
    const bool control=::strcmp(stimulus,"initializer-control")==0;
    if(rc!=1 || field!=3 || preField!=3 || ready!=1 || positiveMask!=15 ||
       calls!=1 || canaryBefore!=1 || canaryAfter!=1 || succeeded!=0 ||
       (control?(commit!=0||finalState!=6||attempted!=0)
               :(commit!=19||finalState!=9||attempted!=1)))
    { ::close(fd);fd=-1;return -2; }
    char raw[2048];
    const int len=std::snprintf(raw,sizeof(raw),
        "{\"schemaVersion\":1,\"kind\":\"R03IRInitializerCommitObservationV1\","
        "\"reportTransport\":\"NativePreopenedInitializerObservationV1\","
        "\"result\":\"ObservedNotAccepted\",\"runId\":\"%s\","
        "\"caseId\":\"%s\",\"stimulus\":\"%s\","
        "\"fixtureSha256\":\"%s\",\"processId\":%ld,"
        "\"commitReturn\":%d,\"finalState\":%d,"
        "\"nativeObserverBoundBeforeFailure\":true,\"preparedField\":%d,"
        "\"finalField\":%d,\"positiveMask\":%d,\"initializerCallbackCalls\":%d,"
        "\"postAotAttempted\":%s,\"postAotSucceeded\":false,"
        "\"firstRecoveryAuthenticated\":false,\"completeDiagnosticsAuthenticated\":false,"
        "\"nativeV2TransportImplemented\":false,\"runtimeAcceptance\":false,"
        "\"R03Accepted\":false,\"H2Passed\":false}\n",
        runId,caseId,stimulus,digest,static_cast<long>(::getpid()),
        commit,finalState,preField,field,positiveMask,calls,
        attempted?"true":"false");
    if(len<=0 || static_cast<size_t>(len)>=sizeof(raw) ||
       !WriteAll(raw,static_cast<size_t>(len)) ||
       ::fsync(fd)!=0 || ::close(fd)!=0)
    { fd=-1;return -3; }
    fd=-1;state.store(2,std::memory_order_release);
    return 1;
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(const char*,const char*,const char*,const char*,const char*) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(int32_t,int32_t,int32_t,int32_t,int32_t,int32_t) { return 0; }
#endif
