#pragma once
// Native implementation of the published R03BoundedDiagnosticsV2 wire contract.
// No VM, managed, filesystem, heap-allocation, or scheduler calls. NOT a Player adapter.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace r03::bounded_v2 {
constexpr std::size_t kTextLimit = 262144;
constexpr std::size_t kEnvelopeReserve = kTextLimit;
constexpr std::size_t kInlineLimit = kEnvelopeReserve - 4096;
constexpr std::size_t kTotal = 16 * kTextLimit;
constexpr std::size_t kMaxStream = kTotal - kEnvelopeReserve;
constexpr std::size_t kChunk = 65536;
constexpr std::size_t kFixedWire = 192;
constexpr char kArtifactName[] = "diagnostics.v2.bin";
constexpr char kEnvelopeName[] = "raw.v2.json";
using Digest = std::array<std::uint8_t, 32>;

inline void Be16(std::uint8_t* p, std::uint16_t v) noexcept {
    p[0] = static_cast<std::uint8_t>(v >> 8); p[1] = static_cast<std::uint8_t>(v);
}
inline void Be32(std::uint8_t* p, std::uint32_t v) noexcept {
    for (unsigned i = 0; i < 4; ++i) p[i] = static_cast<std::uint8_t>(v >> (24 - 8*i));
}

// Small incremental SHA-256, independently checked against hashlib and standard vectors.
class Sha256 final {
    std::array<std::uint32_t, 8> h_{{0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                                    0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19}};
    std::array<std::uint8_t,64> block_{};
    std::size_t fill_ = 0;
    std::uint64_t bytes_ = 0;
    static std::uint32_t R(std::uint32_t x, unsigned n) noexcept { return (x>>n)|(x<<(32-n)); }
    void Transform() noexcept {
        constexpr std::uint32_t k[64] = {
          0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
          0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
          0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
          0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
          0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
          0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
          0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
          0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
        std::uint32_t w[64]{};
        for(unsigned i=0;i<16;++i) {
            const auto* p=block_.data()+i*4;
            w[i]=(std::uint32_t(p[0])<<24)|(std::uint32_t(p[1])<<16)|(std::uint32_t(p[2])<<8)|p[3];
        }
        for(unsigned i=16;i<64;++i) {
            auto x=w[i-15],y=w[i-2];
            w[i]=w[i-16]+(R(x,7)^R(x,18)^(x>>3))+w[i-7]+(R(y,17)^R(y,19)^(y>>10));
        }
        auto a=h_[0],b=h_[1],c=h_[2],d=h_[3],e=h_[4],f=h_[5],g=h_[6],h=h_[7];
        for(unsigned i=0;i<64;++i) {
            auto t1=h+(R(e,6)^R(e,11)^R(e,25))+((e&f)^((~e)&g))+k[i]+w[i];
            auto t2=(R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c));
            h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
        }
        h_[0]+=a;h_[1]+=b;h_[2]+=c;h_[3]+=d;h_[4]+=e;h_[5]+=f;h_[6]+=g;h_[7]+=h;
    }
public:
    void Update(const void* data, std::size_t n) noexcept {
        auto p=static_cast<const std::uint8_t*>(data); bytes_+=n;
        while(n) {
            std::size_t m=(n<64-fill_)?n:64-fill_;
            std::memcpy(block_.data()+fill_,p,m);fill_+=m;p+=m;n-=m;
            if(fill_==64){Transform();fill_=0;}
        }
    }
    Digest Finish() const noexcept {
        Sha256 c=*this; const std::uint64_t bits=bytes_*8;
        const std::uint8_t first=0x80,zero=0;c.Update(&first,1);
        while(c.fill_!=56)c.Update(&zero,1);
        std::uint8_t tail[8];for(unsigned i=0;i<8;++i)tail[i]=static_cast<std::uint8_t>(bits>>(56-8*i));
        c.Update(tail,8);Digest out{};for(unsigned i=0;i<8;++i)Be32(out.data()+i*4,c.h_[i]);return out;
    }
    static Digest Of(const void* p,std::size_t n) noexcept { Sha256 h;h.Update(p,n);return h.Finish(); }
};

enum class Error : unsigned { None, State, Input, Resource, Utf8, Write, Owner, Path, File, Sync, Close, Changed };
struct Failure {
    Error code=Error::None; unsigned slot=0; std::size_t observed=0; int osError=0;
    bool Set(Error c,unsigned s=0,std::size_t n=0,int e=0) noexcept {
        if(code==Error::None){code=c;slot=s;observed=n;osError=e;}return false;
    }
};
inline bool ValidUtf8(const std::uint8_t* p,std::size_t n) noexcept {
    std::uint32_t v=0,min=0;unsigned left=0;
    for(std::size_t i=0;i<n;++i){auto b=p[i];
        if(!left){
            if(b<0x80)continue;
            if(b>=0xc2&&b<=0xdf){v=b&31;left=1;min=0x80;}
            else if(b>=0xe0&&b<=0xef){v=b&15;left=2;min=0x800;}
            else if(b>=0xf0&&b<=0xf4){v=b&7;left=3;min=0x10000;}
            else return false;
        }else{
            if((b&0xc0)!=0x80)return false;v=(v<<6)|(b&63);
            if(--left==0&&(v<min||v>0x10ffff||(v>=0xd800&&v<=0xdfff)))return false;
        }
    }return left==0;
}
inline std::size_t Frames(std::size_t n) noexcept { return n/kChunk+(n%kChunk!=0); }
inline std::size_t WireSize(std::size_t a,std::size_t b) noexcept {
    return kFixedWire+a+b+38*(Frames(a)+Frames(b));
}

struct Section { std::size_t offset=0,size=0; bool text=false; Digest hash{}; };
// The caller allocates this arena while healthy and retains exclusive ownership.
// This class does not capture VM metadata; serializer/lock integration is separate.
class Capture final {
    std::uint8_t* arena_;std::size_t capacity_,used_=0;unsigned next_=0;
    bool open_=false,frozen_=false;std::array<Section,2> sections_{};Failure failure_{};
public:
    Capture(std::uint8_t* arena,std::size_t capacity) noexcept:arena_(arena),capacity_(capacity){
        if(!arena||capacity>kMaxStream)failure_.Set(Error::Input);
    }
    Capture(const Capture&)=delete;Capture& operator=(const Capture&)=delete;
    const Failure& GetFailure() const noexcept{return failure_;}
    bool Begin(unsigned slot,bool text) noexcept {
        if(failure_.code!=Error::None)return false;
        if(frozen_||open_||next_>=2||slot!=14+next_)return failure_.Set(Error::State,slot);
        auto& s=sections_[next_];s.offset=used_;s.text=text;open_=true;return true;
    }
    bool Append(const void* bytes,std::size_t n) noexcept {
        if(failure_.code!=Error::None)return false;
        if(!open_||frozen_||next_>=2)return failure_.Set(Error::State,14+next_);
        auto& s=sections_[next_];
        if((!bytes&&n)||(!s.text&&n))return failure_.Set(Error::Input,14+next_);
        if(n>capacity_-used_||n>kMaxStream-used_)return failure_.Set(Error::Resource,14+next_,used_);
        auto a=sections_[0].size+(next_==0?n:0),b=sections_[1].size+(next_==1?n:0);
        if(WireSize(a,b)>kMaxStream)return failure_.Set(Error::Resource,14+next_,used_);
        if(n)std::memcpy(arena_+used_,bytes,n);used_+=n;s.size+=n;return true;
    }
    bool End() noexcept {
        if(failure_.code!=Error::None)return false;
        if(!open_||frozen_)return failure_.Set(Error::State,14+next_);
        auto& s=sections_[next_];
        if(!ValidUtf8(arena_+s.offset,s.size))return failure_.Set(Error::Utf8,14+next_,s.size);
        s.hash=Sha256::Of(arena_+s.offset,s.size);open_=false;++next_;return true;
    }
    bool Freeze() noexcept {
        if(failure_.code!=Error::None)return false;
        if(frozen_||open_||next_!=2)return failure_.Set(Error::State);
        frozen_=true;return true;
    }
    bool Ready() const noexcept{return frozen_&&failure_.code==Error::None;}
    const Section& At(unsigned i) const noexcept{return sections_[i];}
    const std::uint8_t* Data(unsigned i) const noexcept{return arena_+sections_[i].offset;}
    bool Unchanged() const noexcept{
        if(!Ready())return false;
        for(unsigned i=0;i<2;++i)if(Sha256::Of(Data(i),At(i).size)!=At(i).hash)return false;
        return true;
    }
};
static_assert(sizeof(Capture)<1024,"Capture bookkeeping must remain bounded");

struct Descriptor { std::size_t bytes=0;Digest sha{},binding{},inlineSha{}; };
// Sink.Write must consume exactly n bytes or return false. No partial descriptor
// is returned; failed physical writes may remain on disk for diagnostic custody.
template<class Sink> bool Encode(const Capture& c,Digest context,
                                 const void* inlineJson,std::size_t inlineSize,
                                 Sink& sink,Descriptor& result,Failure& failure) noexcept {
    if(failure.code!=Error::None)return false;
    if(!c.Unchanged())return failure.Set(Error::State);
    if(!inlineJson||inlineSize>kInlineLimit)return failure.Set(Error::Resource,0,inlineSize);
    if(!ValidUtf8(static_cast<const std::uint8_t*>(inlineJson),inlineSize))return failure.Set(Error::Utf8);
    Sha256 prefix,whole;std::size_t count=0;
    auto write=[&](const void* p,std::size_t n,bool addPrefix=true) noexcept {
        if(n>kMaxStream-count)return failure.Set(Error::Resource,0,count);
        if(!sink.Write(p,n))return failure.Set(Error::Write,0,count);
        whole.Update(p,n);if(addPrefix)prefix.Update(p,n);count+=n;return true;
    };
    std::uint8_t h[72]{};std::memcpy(h,"R03DIA2\0",8);std::memcpy(h+8,context.data(),32);
    auto ih=Sha256::Of(inlineJson,inlineSize);std::memcpy(h+40,ih.data(),32);
    if(!write(h,sizeof(h)))return false;
    for(unsigned i=0;i<2;++i){
        const auto& s=c.At(i);const auto* data=c.Data(i);const auto chunks=Frames(s.size);
        std::uint8_t sh[40]{};sh[0]=static_cast<std::uint8_t>(14+i);sh[1]=s.text?1:0;
        Be32(sh+2,static_cast<std::uint32_t>(s.size));Be16(sh+6,static_cast<std::uint16_t>(chunks));
        std::memcpy(sh+8,s.hash.data(),32);if(!write(sh,sizeof(sh)))return false;
        for(std::size_t j=0;j<chunks;++j){
            const auto remain=s.size-j*kChunk,n=(remain<kChunk)?remain:kChunk;
            Sha256 fh;constexpr char domain[]="R03-FRAME-V2";fh.Update(domain,sizeof(domain));fh.Update(context.data(),32);
            std::uint8_t fctx[9];fctx[0]=static_cast<std::uint8_t>(14+i);
            Be32(fctx+1,static_cast<std::uint32_t>(j));Be32(fctx+5,static_cast<std::uint32_t>(n));fh.Update(fctx,9);fh.Update(data+j*kChunk,n);
            std::uint8_t frame[38];Be32(frame,static_cast<std::uint32_t>(j));Be16(frame+4,static_cast<std::uint16_t>(n-1));
            auto digest=fh.Finish();std::memcpy(frame+6,digest.data(),32);
            if(!write(frame,38)||!write(data+j*kChunk,n))return false;
        }
    }
    if(!c.Unchanged())return failure.Set(Error::Changed);
    const auto hash=prefix.Finish();
    if(!write("R03END2\0",8,false)||!write(hash.data(),32,false))return false;
    Descriptor done;done.bytes=count;done.sha=whole.Finish();done.binding=context;done.inlineSha=ih;
    result=done;return true;
}
inline void Hex(const Digest& h,char* out) noexcept {
    constexpr char digits[]="0123456789abcdef";for(unsigned i=0;i<32;++i){out[2*i]=digits[h[i]>>4];out[2*i+1]=digits[h[i]&15];}out[64]=0;
}
} // namespace r03::bounded_v2
