// Runs with an exclusively test-owned canonical directory; never production paths.
#include "PosixDiagnosticFile.h"
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
using namespace r03::diagnostics_v2;
static int writeMode=0,syncMode=0,syncCount=0,closeMode=0,writeCount=0;
static ssize_t TestWrite(int fd,const void* p,std::size_t n){++writeCount;if(writeMode==1){errno=ENOSPC;return -1;}if(writeMode==2)return 0;if(writeMode==3){errno=EINTR;return -1;}if(writeMode==4 && writeCount==1){errno=EINTR;return -1;}return ::write(fd,p,writeMode==5 && n>1?1:n);}
static int TestSync(int fd){++syncCount;if(syncMode==syncCount){errno=EIO;return -1;}return ::fsync(fd);}
static int TestClose(int fd){const int n=::close(fd);if(closeMode){errno=EINTR;return -1;}return n;}
int main(int argc,char** argv){
    if(argc!=3)return 99;
    const std::string mode=argv[1];int directory=::open(argv[2],O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);if(directory<0)return 98;
    PosixCalls calls{TestWrite,TestSync,TestClose};PosixDiagnosticFile sink(calls);
    if(mode=="write-error") writeMode=1;
    if(mode=="zero-write") writeMode=2;
    if(mode=="repeated-eintr") writeMode=3;
    if(mode=="once-eintr") writeMode=4;
    if(mode=="short-writes") writeMode=5;
    if(mode=="file-sync-error") syncMode=1;
    if(mode=="dir-sync-error") syncMode=2;
    if(mode=="close-error") closeMode=1;
    bool prepared=sink.Prepare(directory);bool ok=false;
    auto c=std::make_unique<Capture>();Digest d=Hash("context",7);Descriptor out;
    if(prepared){
        if(mode=="replaced") {::renameat(directory,"diagnostics.v2",directory,"preserve.partial");int x=::openat(directory,"diagnostics.v2",O_WRONLY|O_CREAT|O_EXCL,0600);if(x<0)return 97;::close(x);}
        if(mode=="hardlink") {if(::linkat(directory,"diagnostics.v2",directory,"extra-link",0)<0)return 96;}
        if(mode=="mode-changed") {if(::fchmodat(directory,"diagnostics.v2",0644,0)<0)return 95;}
        if(mode=="deleted") {if(::unlinkat(directory,"diagnostics.v2",0)<0)return 94;}
        if(mode=="prepare-twice") {prepared=sink.Prepare(directory);}
        if(prepared && c->Prepare(d,d,2) && c->Begin(14,false) && c->Append("{}",2) && c->End() && c->Begin(15,false) && c->Append("{}",2) && c->End() && c->Freeze())ok=c->Encode(sink.AsSink(),out);
    }
    ::close(directory);
    std::printf("{\"prepared\":%s,\"ok\":%s,\"durable\":%s,\"firstError\":%d,\"codecError\":%u,\"receiptBytes\":%zu,\"written\":%zu,\"syncCalls\":%d,\"writeCalls\":%d}\n",prepared?"true":"false",ok?"true":"false",sink.DurableSidecar()?"true":"false",sink.FirstError(),unsigned(c->FirstFailure().reason),out.bytes,sink.BytesWritten(),syncCount,writeCount);
    return 0;
}
