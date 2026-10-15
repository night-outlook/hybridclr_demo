// Host-only driver: files, vectors and formatting are NOT runtime producers.
#include "BoundedDiagnosticsV2.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <memory>
#include <new>
#include <string>
#include <vector>
using namespace r03::diagnostics_v2;
static bool forbidAllocation=false;
void* operator new(std::size_t n) { if(forbidAllocation) std::abort(); if(void* p=std::malloc(n?n:1))return p; throw std::bad_alloc(); }
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }
struct MemorySink {
    std::unique_ptr<std::uint8_t[]> bytes{new std::uint8_t[ArtifactBudget]};
    std::size_t used=0,calls=0,maxWrite=0,failAt=0; bool finishFail=false,finished=false;
    Capture* reenter=nullptr;
    static bool Write(void* self,const std::uint8_t* p,std::size_t n,int& error) noexcept {
        auto& s=*static_cast<MemorySink*>(self); ++s.calls;
        if(s.failAt==s.calls) { error=28; return false; }
        if(s.reenter) { auto* c=s.reenter; s.reenter=nullptr; c->Begin(14,false); }
        if(n>FrameLimit || n>ArtifactBudget-s.used) { error=75; return false; }
        if(n>s.maxWrite)s.maxWrite=n;
        if(n) std::memcpy(s.bytes.get()+s.used,p,n);
        s.used+=n;
        return true;
    }
    static bool Finish(void* self,int& error) noexcept {
        auto& s=*static_cast<MemorySink*>(self);
        if(s.finishFail) { error=5; return false; } s.finished=true; return true;
    }
    Sink AsSink() noexcept { return {this,Write,Finish}; }
};
static bool Fill(Capture& c,const Digest& a,const Digest& b,
                 const std::vector<std::uint8_t>& x,const std::vector<std::uint8_t>& y,
                 bool nullX=false,bool nullY=false,std::size_t chunk=7,std::size_t inlineN=2) {
    if(!c.Prepare(a,b,inlineN))return false;
    for(unsigned slot=14;slot<16;++slot) {
        const auto& v=slot==14?x:y; const bool isNull=slot==14?nullX:nullY;
        if(!c.Begin(slot,isNull))return false;
        for(std::size_t i=0;i<v.size();) {const auto n=v.size()-i<chunk?v.size()-i:chunk;if(!c.Append(v.data()+i,n))return false;i+=n;}
        if(!c.End())return false;
    }
    return c.Freeze();
}
static std::string Hex(const Digest& d) {std::string out;for(auto b:d){out+="0123456789abcdef"[b>>4];out+="0123456789abcdef"[b&15];}return out;}
static Digest Parse(const std::string& text) {
    if(text.size()!=64) throw std::runtime_error("hash length");
    Digest d{};
    for(unsigned i=0;i<32;++i){unsigned v=0;for(unsigned j=0;j<2;++j){char c=text[i*2+j];if(c>='0'&&c<='9')v=v*16+unsigned(c-'0');else if(c>='a'&&c<='f')v=v*16+unsigned(c-'a'+10);else throw std::runtime_error("hash characters");}d[i]=static_cast<std::uint8_t>(v);}return d;
}
static std::vector<std::uint8_t> Read(const std::string& path) {
    if(path=="-") return {};
    std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("input file");
    return {std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()};
}
static void Save(const char* path,const MemorySink& s) {
    // Test driver only. The codec owns no filesystem path and claims no fsync.
    std::ofstream f(path,std::ios::binary);if(!f)throw std::runtime_error("output file");
    f.write(reinterpret_cast<const char*>(s.bytes.get()),static_cast<std::streamsize>(s.used));
    if(!f)throw std::runtime_error("output write");
}
#define CHECK(x) do{if(!(x)){std::fprintf(stderr,"selftest line %d: %s\n",__LINE__,#x);return 1;}}while(false)
static int SelfTest() {
    Digest d=Hash("x",1); std::vector<std::uint8_t> x(65540,'x'),y(17,'y'); unsigned scenarios=0;
    const auto create=[&](){return std::make_unique<Capture>();};
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));forbidAllocation=true;bool ok=c->Encode(s.AsSink(),r);forbidAllocation=false;CHECK(ok&&s.finished&&r.bytes==s.used&&s.maxWrite<=FrameLimit);++scenarios;}
    std::size_t callCount=0;
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));CHECK(c->Encode(s.AsSink(),r));callCount=s.calls;}
    for(std::size_t i=1;i<=callCount;++i) {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));s.failAt=i;forbidAllocation=true;bool ok=c->Encode(s.AsSink(),r);forbidAllocation=false;CHECK(!ok&&!s.finished&&r.bytes==0&&c->FirstFailure().reason==Error::SinkWrite&&c->FirstFailure().io==28);c->Begin(15,false);CHECK(c->FirstFailure().reason==Error::SinkWrite);++scenarios;}
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));s.finishFail=true;CHECK(!c->Encode(s.AsSink(),r));CHECK(r.bytes==0&&c->FirstFailure().reason==Error::SinkFinish);++scenarios;}
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));s.reenter=c.get();CHECK(!c->Encode(s.AsSink(),r));CHECK(!s.finished&&r.bytes==0&&c->FirstFailure().reason==Error::Reentry);++scenarios;}
    {auto c=create();CHECK(!c->Freeze());CHECK(c->FirstFailure().reason==Error::State);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(!c->Begin(15,false));CHECK(c->FirstFailure().reason==Error::SlotOrder);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,false));CHECK(c->End());CHECK(!c->Begin(14,false));CHECK(c->FirstFailure().reason==Error::SlotOrder);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,true));CHECK(!c->Append("x",1));CHECK(c->FirstFailure().reason==Error::NullContent);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,false));CHECK(!c->Append(nullptr,1));CHECK(c->FirstFailure().reason==Error::InvalidPointer);++scenarios;}
    {auto c=create();CHECK(!c->Prepare(d,d,InlineLimit+1));CHECK(c->FirstFailure().reason==Error::Resource);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,false));CHECK(!c->Append("x",std::numeric_limits<std::size_t>::max()));CHECK(c->FirstFailure().reason==Error::Resource);++scenarios;}
    {auto c=create();CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,false));CHECK(c->Append("\xf0\x9f",2));CHECK(!c->End());CHECK(c->FirstFailure().reason==Error::InvalidUtf8);++scenarios;}
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));CHECK(c->Encode(s.AsSink(),r));const auto n=s.used;CHECK(!c->Encode(s.AsSink(),r));CHECK(s.used==n&&r.bytes==0);++scenarios;}
    {auto c=create();MemorySink s;Descriptor r;CHECK(c->Prepare(d,d,2));CHECK(c->Begin(14,false));CHECK(c->Append("abc",3));CHECK(c->End());CHECK(!c->Freeze());CHECK(!c->Encode(s.AsSink(),r));CHECK(s.used==0);++scenarios;}
    {auto c=create();MemorySink s;Descriptor r;CHECK(Fill(*c,d,d,x,y));CHECK(!c->Append("x",1));CHECK(!c->Encode(s.AsSink(),r));CHECK(s.used==0);++scenarios;}
    std::printf("{\"passed\":true,\"scenarios\":%u,\"writeFaultPositions\":%zu,\"captureBytes\":%zu,\"codecPlusInlineAndStackReserve\":%zu}\n",scenarios,callCount,sizeof(Capture),sizeof(Capture)+InlineLimit+2048);return 0;
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="selftest")return SelfTest();
        if(argc==3 && std::string(argv[1])=="hash") {auto v=Read(argv[2]);Sha256 s;for(std::size_t i=0;i<v.size();++i)s.Update(v.data()+i,1);std::printf("%s\n",Hex(s.Final()).c_str());return 0;}
        if(argc!=9)throw std::runtime_error("usage: encode binding inlineDigest inlineBytes field14|- field15|- output appendChunk");
        Digest context=Parse(argv[2]),inlineHash=Parse(argv[3]);const auto inlineN=std::stoull(argv[4]);
        auto a=Read(argv[5]),b=Read(argv[6]);const auto chunk=std::stoull(argv[8]);if(!chunk)throw std::runtime_error("chunk");
        auto c=std::make_unique<Capture>();MemorySink sink;Descriptor receipt;
        forbidAllocation=true;
        const bool frozen=Fill(*c,context,inlineHash,a,b,std::string_view(argv[5])=="-",std::string_view(argv[6])=="-",chunk,inlineN);
        // Prove capture ownership: source buffers may change without affecting bytes.
        if(frozen){for(auto& v:a)v=0;for(auto& v:b)v=0;}
        const bool ok=frozen&&c->Encode(sink.AsSink(),receipt);
        forbidAllocation=false;
        Save(argv[7],sink);const auto f=c->FirstFailure();
        std::printf("{\"ok\":%s,\"error\":%u,\"slot\":%d,\"knownBytes\":%zu,\"bytes\":%zu,\"sha256\":\"%s\",\"binding\":\"%s\",\"inlineSha256\":\"%s\",\"maxWrite\":%zu,\"capturedBytes\":%zu}\n",ok?"true":"false",unsigned(f.reason),f.slot,f.knownBytes,receipt.bytes,Hex(receipt.artifactHash).c_str(),Hex(receipt.binding).c_str(),Hex(receipt.inlineHash).c_str(),sink.maxWrite,c->CapturedBytes());
        return ok?0:2;
    } catch(const std::exception& e) {forbidAllocation=false;std::fprintf(stderr,"driver: %s\n",e.what());return 99;}
}
