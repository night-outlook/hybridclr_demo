#ifndef R03_BOUNDED_DIAGNOSTICS_V2_H
#define R03_BOUNDED_DIAGNOSTICS_V2_H
// Standalone, inactive transport component. Does not admit managed execution,
// acquire VM locks, perform file I/O, or authenticate caller-owned run identity.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace r03_diag_v2 {
constexpr size_t kTextLimit = 262144;
constexpr size_t kFrame = 65536;
constexpr size_t kTotal = 16 * kTextLimit;
constexpr size_t kEnvelopeReserve = kTextLimit;
constexpr size_t kInlineLimit = kEnvelopeReserve - 4096;
constexpr size_t kArtifactMax = kTotal - kEnvelopeReserve;
using Digest = std::array<uint8_t, 32>;

inline void Put32(uint8_t* p, uint32_t n) noexcept {
    for (unsigned i = 0; i != 4; ++i) p[i] = uint8_t(n >> (24 - 8 * i));
}
inline void Put16(uint8_t* p, uint16_t n) noexcept { p[0] = uint8_t(n >> 8); p[1] = uint8_t(n); }

// SHA-256, incremental, fixed storage. A finished digest is computed on a copy.
// Callers below restrict input to <=4 MiB, far below the 64-bit bit-count bound.
class Sha256 {
    uint32_t h_[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                      0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    uint8_t block_[64]{};
    size_t used_ = 0;
    uint64_t bytes_ = 0;
    static uint32_t R(uint32_t v, unsigned n) noexcept { return (v >> n) | (v << (32-n)); }
    void Compress() noexcept {
        static constexpr uint32_t k[64] = {
            0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
            0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
            0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
            0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
            0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
            0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
            0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
            0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
        uint32_t w[64]{};
        for (unsigned i=0; i<16; ++i) {
            const auto* p=block_+4*i;
            w[i]=(uint32_t(p[0])<<24)|(uint32_t(p[1])<<16)|(uint32_t(p[2])<<8)|uint32_t(p[3]);
        }
        for (unsigned i=16; i<64; ++i) {
            uint32_t a=w[i-15], b=w[i-2];
            w[i]=w[i-16]+(R(a,7)^R(a,18)^(a>>3))+w[i-7]+(R(b,17)^R(b,19)^(b>>10));
        }
        uint32_t a=h_[0],b=h_[1],c=h_[2],d=h_[3],e=h_[4],f=h_[5],g=h_[6],h=h_[7];
        for (unsigned i=0; i<64; ++i) {
            uint32_t t1=h+(R(e,6)^R(e,11)^R(e,25))+((e&f)^(~e&g))+k[i]+w[i];
            uint32_t t2=(R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c));
            h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
        }
        h_[0]+=a;h_[1]+=b;h_[2]+=c;h_[3]+=d;h_[4]+=e;h_[5]+=f;h_[6]+=g;h_[7]+=h;
    }
public:
    void Update(const uint8_t* p, size_t n) noexcept {
        bytes_ += n;
        while (n) {
            size_t take=64-used_; if (take>n) take=n;
            std::memcpy(block_+used_,p,take);used_+=take;p+=take;n-=take;
            if (used_==64) { Compress(); used_=0; }
        }
    }
    Digest Finish() const noexcept {
        Sha256 s=*this;
        const uint64_t bits=s.bytes_*8;
        const uint8_t pad=0x80, zero=0;
        s.Update(&pad,1);
        while (s.used_!=56) s.Update(&zero,1);
        uint8_t size[8]{};
        for (unsigned i=0;i<8;++i) size[i]=uint8_t(bits>>(56-8*i));
        s.Update(size,8);
        Digest out{};for(unsigned i=0;i<8;++i) Put32(out.data()+4*i,s.h_[i]);
        return out;
    }
    static Digest Of(const uint8_t* p,size_t n) noexcept { Sha256 s;s.Update(p,n);return s.Finish(); }
};

struct FieldView { const uint8_t* data; size_t size; bool isNull; };
enum class Error : uint8_t { None, Reused, InvalidInput, ResourceLimit, InvalidUtf8,
    SinkFailure, Reentered, ChangedCapture, WrongSlot, NotFrozen, Capacity };
struct Receipt { size_t bytes=0; Digest sha256{}; bool complete=false; };
struct Failure { Error error=Error::None; int slot=-1; size_t emitted=0; };
using Write = bool (*)(void*,const uint8_t*,size_t) noexcept;
inline size_t Frames(size_t n) noexcept { return n/kFrame+(n%kFrame!=0); }
inline bool ValidUtf8(const uint8_t* p,size_t n) noexcept {
    for(size_t i=0;i<n;) {
        uint32_t cp=p[i++];unsigned more=0;uint32_t minimum=0;
        if(cp<0x80) continue;
        if(cp>=0xc2 && cp<=0xdf){more=1;cp&=0x1f;minimum=0x80;}
        else if(cp>=0xe0 && cp<=0xef){more=2;cp&=15;minimum=0x800;}
        else if(cp>=0xf0 && cp<=0xf4){more=3;cp&=7;minimum=0x10000;}
        else return false;
        if(n-i<more) return false;
        while(more--){uint8_t c=p[i++];if((c&0xc0)!=0x80)return false;cp=(cp<<6)|(c&0x3f);}
        if(cp<minimum||cp>0x10ffff||(cp>=0xd800&&cp<=0xdfff))return false;
    }
    return true;
}
inline bool WireSize(size_t a,size_t b,size_t& out) noexcept {
    if(a>kArtifactMax||b>kArtifactMax||Frames(a)>64||Frames(b)>64) return false;
    out=192+a+b+38*(Frames(a)+Frames(b));
    return out<=kArtifactMax;
}

// Caller preallocates this storage while healthy. Append is a serializer sink,
// not a VM census implementation. Caller must serialize under reviewed locks.
// Single owner only: concurrent access to Capture/Encoder is not supported.
class Capture {
    uint8_t* storage_;size_t capacity_;size_t used_=0;size_t start_[2]{};size_t size_[2]{};
    bool null_[2]{};unsigned completed_=0;bool active_=false,frozen_=false;
    Error error_=Error::None;
    bool Fail(Error e) noexcept {if(error_==Error::None)error_=e;return false;}
public:
    Capture(uint8_t* storage,size_t capacity) noexcept : storage_(storage),capacity_(capacity) {
        if(!storage||capacity>kArtifactMax) error_=Error::Capacity;
    }
    Capture(const Capture&) = delete;
    Capture& operator=(const Capture&) = delete;
    Error error() const noexcept {return error_;}
    bool Begin(unsigned slot,bool isNull) noexcept {
        if(error_!=Error::None)return false;
        if(active_||frozen_||completed_>=2||slot!=14+completed_)return Fail(Error::WrongSlot);
        active_=true;start_[completed_]=used_;null_[completed_]=isNull;return true;
    }
    bool Append(const uint8_t* p,size_t n) noexcept {
        if(error_!=Error::None)return false;
        if(!active_||frozen_||null_[completed_]||(!p&&n))return Fail(Error::InvalidInput);
        if(n>capacity_-used_)return Fail(Error::Capacity);
        size_t wire=0,a=size_[0],b=size_[1];
        if(completed_==0)a+=n;else b+=n;
        if(!WireSize(a,b,wire))return Fail(Error::ResourceLimit);
        if(n)std::memcpy(storage_+used_,p,n);
        used_+=n;size_[completed_]+=n;return true;
    }
    bool End() noexcept {
        if(error_!=Error::None)return false;
        if(!active_||frozen_)return Fail(Error::WrongSlot);
        if(!ValidUtf8(storage_+start_[completed_],size_[completed_]))return Fail(Error::InvalidUtf8);
        active_=false;++completed_;return true;
    }
    bool Freeze() noexcept {
        if(error_!=Error::None)return false;
        if(active_||frozen_||completed_!=2)return Fail(Error::NotFrozen);
        frozen_=true;return true;
    }
    bool View(unsigned slot,FieldView& out) const noexcept {
        if(error_!=Error::None||!frozen_||slot<14||slot>15)return false;
        unsigned i=slot-14;out={storage_+start_[i],size_[i],null_[i]};return true;
    }
    size_t bytes() const noexcept {return used_;}
};

// One-shot framing over complete immutable FieldViews. No path handling, no
// durable commit, no JSON semantic acceptance and no full identity validation.
// context/inlineHash must come from the authenticated healthy-time envelope.
// Write must synchronously consume bytes, not retain the scratch pointer.
class Encoder {
    bool started_=false,running_=false;
    Failure first_{};size_t emitted_=0;Sha256 stream_;
    bool Fail(Error e,int slot) noexcept {
        if(first_.error==Error::None) first_={e,slot,emitted_};
        return false;
    }
    bool Send(Write write,void* user,const uint8_t* p,size_t n,int slot) noexcept {
        if(first_.error!=Error::None)return false;
        if(n>kArtifactMax-emitted_)return Fail(Error::ResourceLimit,slot);
        if(!write(user,p,n))return Fail(Error::SinkFailure,slot);
        if(first_.error!=Error::None)return false; // callback attempted re-entry
        stream_.Update(p,n);emitted_+=n;return true;
    }
public:
    Encoder() noexcept = default;
    Encoder(const Encoder&) = delete;
    Encoder& operator=(const Encoder&) = delete;
    Failure failure() const noexcept {return first_;}
    bool Encode(Digest context,Digest inlineHash,size_t inlineBytes,
                const FieldView (&fields)[2],uint8_t* scratch,size_t scratchBytes,
                Write write,void* user,Receipt& receipt) noexcept {
        receipt=Receipt{};
        if(running_)return Fail(Error::Reentered,-1);
        if(started_)return Fail(Error::Reused,-1);
        started_=true;
        if(!write||!scratch||scratchBytes<kFrame||inlineBytes>kInlineLimit)
            return Fail(Error::InvalidInput,-1);
        const FieldView frozen[2]={fields[0],fields[1]};
        size_t total=0;
        if(!WireSize(frozen[0].size,frozen[1].size,total))return Fail(Error::ResourceLimit,-1);
        const uintptr_t sb=reinterpret_cast<uintptr_t>(scratch);
        if(sb>UINTPTR_MAX-kFrame)return Fail(Error::InvalidInput,-1);
        Digest expected[2]{};
        for(unsigned i=0;i<2;++i){
            const auto& f=frozen[i];
            if((!f.data&&f.size)||(f.isNull&&f.size))return Fail(Error::InvalidInput,int(14+i));
            const uintptr_t fb=reinterpret_cast<uintptr_t>(f.data);
            if(fb>UINTPTR_MAX-f.size || (f.size && fb<sb+kFrame && sb<fb+f.size))
                return Fail(Error::InvalidInput,int(14+i));
            if(!ValidUtf8(f.data,f.size))return Fail(Error::InvalidUtf8,int(14+i));
            expected[i]=Sha256::Of(f.data,f.size);
        }
        running_=true;
        uint8_t header[72]={'R','0','3','D','I','A','2',0};
        std::memcpy(header+8,context.data(),32);std::memcpy(header+40,inlineHash.data(),32);
        bool ok=Send(write,user,header,sizeof header,-1);
        for(unsigned i=0;ok&&i<2;++i){
            const auto& f=frozen[i];const uint8_t slot=uint8_t(14+i);
            uint8_t section[40]{};section[0]=slot;section[1]=uint8_t(!f.isNull);
            Put32(section+2,uint32_t(f.size));Put16(section+6,uint16_t(Frames(f.size)));
            std::memcpy(section+8,expected[i].data(),32);
            ok=Send(write,user,section,sizeof section,slot);Sha256 observed;
            for(size_t j=0;ok&&j<Frames(f.size);++j){
                size_t n=f.size-j*kFrame;if(n>kFrame)n=kFrame;
                std::memcpy(scratch,f.data+j*kFrame,n);observed.Update(scratch,n);
                static constexpr uint8_t domain[]="R03-FRAME-V2"; // includes one NUL
                Sha256 frame;frame.Update(domain,sizeof domain);frame.Update(context.data(),32);
                uint8_t numbers[9]{};numbers[0]=slot;Put32(numbers+1,uint32_t(j));Put32(numbers+5,uint32_t(n));
                frame.Update(numbers,sizeof numbers);frame.Update(scratch,n);
                Digest hash=frame.Finish();uint8_t fh[38]{};Put32(fh,uint32_t(j));Put16(fh+4,uint16_t(n-1));
                std::memcpy(fh+6,hash.data(),32);
                ok=Send(write,user,fh,sizeof fh,slot)&&Send(write,user,scratch,n,slot);
            }
            if(ok&&observed.Finish()!=expected[i])ok=Fail(Error::ChangedCapture,slot);
        }
        if(ok){
            Digest prefix=stream_.Finish();uint8_t footer[40]={'R','0','3','E','N','D','2',0};
            std::memcpy(footer+8,prefix.data(),32);ok=Send(write,user,footer,sizeof footer,-1);
        }
        running_=false;
        if(!ok||first_.error!=Error::None)return false;
        if(emitted_!=total)return Fail(Error::InvalidInput,-1);
        receipt.bytes=emitted_;receipt.sha256=stream_.Finish();receipt.complete=true;return true;
    }
};
} // namespace r03_diag_v2
#endif
