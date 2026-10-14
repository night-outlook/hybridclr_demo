// Host-only driver. File reads/allocations are outside the protected core.
#include "BoundedDiagnosticsV2.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <new>
#include <string>
#include <vector>
#include <type_traits>
static_assert(!std::is_copy_constructible<r03_diag_v2::Encoder>::value, "one-shot encoder");
static_assert(!std::is_copy_constructible<r03_diag_v2::Capture>::value, "single owner capture");
using namespace r03_diag_v2;
static bool forbidNew=false;
static size_t protectedAllocations=0;
void* operator new(std::size_t n) {
    if(forbidNew){++protectedAllocations;std::abort();}
    void* p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();return p;
}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete[](void* p) noexcept {::operator delete(p);}
void operator delete[](void* p,std::size_t) noexcept {::operator delete(p);}
static void Check(bool x){if(!x)std::abort();}
static uint32_t Get32(const uint8_t* p){return(uint32_t(p[0])<<24)|(uint32_t(p[1])<<16)|(uint32_t(p[2])<<8)|p[3];}
static std::string Hex(const Digest& d){const char* h="0123456789abcdef";std::string s;for(auto c:d){s+=h[c>>4];s+=h[c&15];}return s;}
struct Output {
    uint8_t* p;size_t capacity;size_t n=0,calls=0,failCall=0;bool reenter=false,mutate=false;
    Encoder* encoder=nullptr;FieldView* fields=nullptr;uint8_t* scratch=nullptr;
    Digest context{},inl{};
};
static bool Sink(void* ptr,const uint8_t* p,size_t n) noexcept {
    auto& o=*static_cast<Output*>(ptr);++o.calls;
    if(o.failCall&&o.calls==o.failCall)return false;
    if(o.reenter&&o.calls==1){
        Receipt inner;
        auto& f=*reinterpret_cast<FieldView (*)[2]>(o.fields);
        o.encoder->Encode(o.context,o.inl,2,f,o.scratch,kFrame,Sink,&o,inner);
        return false;
    }
    if(o.mutate&&o.calls==1&&o.fields[0].size){
        const_cast<uint8_t*>(o.fields[0].data)[0]^=1;
    }
    if(n>o.capacity-o.n)return false;
    std::memcpy(o.p+o.n,p,n);o.n+=n;return true;
}
static int SelfTest(){
    Check(Hex(Sha256::Of(nullptr,0))=="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    Check(Hex(Sha256::Of(reinterpret_cast<const uint8_t*>("abc"),3))=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    Sha256 h;const uint8_t a='a';for(int i=0;i<1000000;++i)h.Update(&a,1);
    Check(Hex(h.Finish())=="cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    Check(h.Finish()==h.Finish());
    uint8_t space[64]{};FieldView v{};
    Capture notReady(space,64);Check(!notReady.View(14,v));Check(!notReady.Freeze());Check(notReady.error()==Error::NotFrozen);
    Capture dup(space,64);Check(dup.Begin(14,false));Check(!dup.Begin(14,false));Check(dup.error()==Error::WrongSlot);
    Capture null(space,64);Check(null.Begin(14,true));Check(!null.Append(&a,1));Check(null.error()==Error::InvalidInput);
    Capture order(space,64);Check(!order.Begin(15,false));Check(order.error()==Error::WrongSlot);
    Capture valid(space,64);Check(valid.Begin(14,false));Check(valid.Append(&a,1));Check(valid.End());Check(valid.Begin(15,true));Check(valid.End());Check(valid.Freeze());Check(valid.View(14,v)&&v.size==1);Check(valid.View(15,v)&&v.isNull);Check(!valid.Append(&a,1));
    std::printf("{\"result\":\"Passed\",\"shaVectors\":3,\"sizeofEncoder\":%zu,\"sizeofCapture\":%zu,\"sizeofSha256\":%zu}\n",sizeof(Encoder),sizeof(Capture),sizeof(Sha256));return 0;
}
int main(int argc,char** argv){
    if(argc==2&&std::string(argv[1])=="selftest")return SelfTest();
    // Binary input: tags u8/u8, sizes BEu32/BEu32, identityDigest/inlineDigest,
    // then exact field bytes. CLI flags are controlled by run_tests.py only.
    if(argc!=7)return 90;
    std::ifstream in(argv[1],std::ios::binary);
    std::vector<uint8_t> input((std::istreambuf_iterator<char>(in)),{});
    if(input.size()<74)return 91;
    size_t a=Get32(input.data()+2),b=Get32(input.data()+6);
    if(a>kTotal||b>kTotal||input.size()!=74+a+b)return 92;
    FieldView fields[2]={{input.data()+74,a,input[0]==0},{input.data()+74+a,b,input[1]==0}};
    const bool badTag=input[0]>1||input[1]>1;
    Digest context{},inl{};std::memcpy(context.data(),input.data()+10,32);std::memcpy(inl.data(),input.data()+42,32);
    std::vector<uint8_t> output(kArtifactMax),captureStorage(kArtifactMax),scratch(kFrame);
    Encoder encoder;Output out{output.data(),output.size()};out.context=context;out.inl=inl;
    out.failCall=std::strtoul(argv[4],nullptr,10);std::string mode=argv[5];size_t inlineSize=std::strtoul(argv[6],nullptr,10);
    out.encoder=&encoder;out.fields=fields;out.scratch=scratch.data();out.reenter=mode=="reenter";out.mutate=mode=="mutate";
    Capture capture(captureStorage.data(),captureStorage.size());Receipt result;bool ok=!badTag;
    forbidNew=true;
    if(mode=="capture"){
        for(unsigned i=0;ok&&i<2;++i){
            ok=capture.Begin(14+i,fields[i].isNull);
            for(size_t offset=0;ok&&offset<fields[i].size;){
                size_t count=fields[i].size-offset;if(count>7919)count=7919;
                ok=capture.Append(fields[i].data+offset,count);offset+=count;
            }
            if(ok)ok=capture.End();
        }
        if(ok)ok=capture.Freeze();
        for(unsigned i=0;ok&&i<2;++i)ok=capture.View(14+i,fields[i]);
    }
    uint8_t* frameBuffer=scratch.data();size_t frameSize=scratch.size();
    if(mode=="alias-scratch")frameBuffer=const_cast<uint8_t*>(fields[0].data);
    if(mode=="small-scratch")frameSize=kFrame-1;
    if(mode=="null-data"&&fields[0].size)fields[0].data=nullptr;
    if(ok)ok=encoder.Encode(context,inl,inlineSize,fields,frameBuffer,frameSize,Sink,&out,result);
    if(mode=="reuse"&&ok){Receipt again;Check(!encoder.Encode(context,inl,inlineSize,fields,scratch.data(),scratch.size(),Sink,&out,again));Check(!again.complete);}
    forbidNew=false;
    std::FILE* f=std::fopen(argv[2],"wb");if(!f)return 93;
    if(out.n&&std::fwrite(output.data(),1,out.n,f)!=out.n)return 94;
    if(std::fclose(f))return 95;
    f=std::fopen(argv[3],"wb");if(!f)return 96;
    Failure error=encoder.failure();
    std::fprintf(f,"{\"ok\":%s,\"complete\":%s,\"bytes\":%zu,\"sha256\":\"%s\",\"error\":%u,\"slot\":%d,\"failureEmitted\":%zu,\"sinkBytes\":%zu,\"sinkCalls\":%zu,\"captureError\":%u,\"protectedNewCalls\":%zu}\n",ok?"true":"false",result.complete?"true":"false",result.bytes,Hex(result.sha256).c_str(),unsigned(error.error),error.slot,error.emitted,out.n,out.calls,unsigned(capture.error()),protectedAllocations);
    return std::fclose(f)?97:0;
}
