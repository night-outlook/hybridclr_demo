#pragma once
// R03BoundedDiagnosticsV2 native codec. Not connected to the Unity Player.
// Caller owns healthy preparation, coherent serializer capture and durable files.
// Single-owner object: publish only after Freeze; no concurrent mutation/re-entry.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

namespace r03::diagnostics_v2 {
using Digest = std::array<std::uint8_t, 32>;
inline constexpr std::size_t FrameLimit = 65536;
inline constexpr std::size_t TextLimit = 262144;
inline constexpr std::size_t TotalBudget = 16 * TextLimit;
inline constexpr std::size_t InlineLimit = TextLimit - 4096;
inline constexpr std::size_t ArtifactBudget = TotalBudget - TextLimit;
inline constexpr std::size_t FixedOverhead = 72 + 2 * 40 + 40;
inline constexpr std::size_t FrameOverhead = 38;
inline constexpr std::size_t RawCapacity = ArtifactBudget - FixedOverhead;

inline void U16(std::uint8_t* p, std::uint16_t n) noexcept {
    p[0] = static_cast<std::uint8_t>(n >> 8); p[1] = static_cast<std::uint8_t>(n);
}
inline void U32(std::uint8_t* p, std::uint32_t n) noexcept {
    p[0] = static_cast<std::uint8_t>(n >> 24); p[1] = static_cast<std::uint8_t>(n >> 16);
    p[2] = static_cast<std::uint8_t>(n >> 8); p[3] = static_cast<std::uint8_t>(n);
}

// Allocation-free SHA-256, independently checked against hashlib and vectors.
class Sha256 final {
    std::array<std::uint32_t, 8> h_{{0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                                    0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19}};
    std::array<std::uint8_t, 64> block_{};
    std::uint64_t bytes_ = 0;
    std::size_t used_ = 0;
    static std::uint32_t R(std::uint32_t x, unsigned n) noexcept { return (x >> n) | (x << (32 - n)); }
    void Compress(const std::uint8_t* p) noexcept {
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
        for (std::size_t i=0;i<16;++i) w[i]=(std::uint32_t(p[i*4])<<24)|(std::uint32_t(p[i*4+1])<<16)|
                                          (std::uint32_t(p[i*4+2])<<8)|p[i*4+3];
        for (std::size_t i=16;i<64;++i) {
            const auto a=w[i-15], b=w[i-2];
            w[i]=w[i-16]+(R(a,7)^R(a,18)^(a>>3))+w[i-7]+(R(b,17)^R(b,19)^(b>>10));
        }
        auto a=h_[0], b=h_[1], c=h_[2], d=h_[3], e=h_[4], f=h_[5], g=h_[6], h=h_[7];
        for (std::size_t i=0;i<64;++i) {
            const auto t1=h+(R(e,6)^R(e,11)^R(e,25))+((e&f)^(~e&g))+k[i]+w[i];
            const auto t2=(R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c));
            h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        h_[0]+=a; h_[1]+=b; h_[2]+=c; h_[3]+=d; h_[4]+=e; h_[5]+=f; h_[6]+=g; h_[7]+=h;
    }
public:
    bool Update(const void* data, std::size_t n) noexcept {
        if ((n != 0 && data == nullptr) || n > (std::numeric_limits<std::uint64_t>::max()/8)-bytes_) return false;
        const auto* p=static_cast<const std::uint8_t*>(data); bytes_+=n;
        while (n != 0) {
            const std::size_t take=n < 64-used_ ? n : 64-used_;
            std::memcpy(block_.data()+used_,p,take); used_+=take; p+=take; n-=take;
            if (used_==64) { Compress(block_.data()); used_=0; }
        }
        return true;
    }
    Digest Final() const noexcept {
        Sha256 c=*this;
        c.block_[c.used_++]=0x80;
        if (c.used_>56) { while(c.used_<64)c.block_[c.used_++]=0; c.Compress(c.block_.data()); c.used_=0; }
        while(c.used_<56)c.block_[c.used_++]=0;
        const auto bits=c.bytes_*8;
        for (unsigned i=0;i<8;++i) c.block_[56+i]=static_cast<std::uint8_t>(bits>>(56-8*i));
        c.Compress(c.block_.data()); Digest out{};
        for (std::size_t i=0;i<8;++i) U32(out.data()+i*4,c.h_[i]);
        return out;
    }
};
inline Digest Hash(const void* data, std::size_t n) noexcept {
    Sha256 hash; if (!hash.Update(data,n)) return {}; return hash.Final();
}

// Streaming UTF-8 validation. Embedded NUL is accepted; overlongs, surrogate
// encodings and values beyond U+10FFFF are not. Chunk boundaries are irrelevant.
class Utf8 final {
    std::uint8_t remaining_=0, low_=0x80, high_=0xbf;
public:
    bool Add(const std::uint8_t* p, std::size_t n) noexcept {
        for (std::size_t i=0;i<n;++i) {
            const auto c=p[i];
            if (remaining_) {
                if(c<low_ || c>high_) return false;
                --remaining_; low_=0x80; high_=0xbf;
            } else if (c<=0x7f) {} else if(c>=0xc2 && c<=0xdf) remaining_=1;
            else if(c>=0xe0 && c<=0xef) { remaining_=2; low_=c==0xe0?0xa0:0x80; high_=c==0xed?0x9f:0xbf; }
            else if(c>=0xf0 && c<=0xf4) { remaining_=3; low_=c==0xf0?0x90:0x80; high_=c==0xf4?0x8f:0xbf; }
            else return false;
        }
        return true;
    }
    bool Complete() const noexcept { return remaining_==0; }
};

enum class Error : std::uint8_t { None, State, SlotOrder, Resource, NullContent, InvalidUtf8,
                                 InvalidPointer, SinkWrite, SinkFinish, Reentry };
struct Failure { Error reason=Error::None; int slot=-1; std::size_t knownBytes=0; int io=0; };
struct Descriptor { Digest binding{}, inlineHash{}, artifactHash{}; std::size_t bytes=0; };
struct Sink {
    void* context=nullptr;
    // Callbacks synchronously consume the bytes. They must not retain spans or
    // throw, mutate the capture, or re-enter. No callback call exceeds 65536.
    bool (*write)(void*,const std::uint8_t*,std::size_t,int&) noexcept=nullptr;
    // For a file sink, finish must verify identity and durably finish the file.
    bool (*finish)(void*,int&) noexcept=nullptr;
};

class Capture final {
    enum class State { Ready, Section, Frozen, Writing, Done, Failed };
    struct Section { std::size_t offset=0, length=0; bool isNull=false; Digest hash{}; };
    std::array<std::uint8_t,RawCapacity> bytes_{};
    std::array<Section,2> sections_{};
    Digest binding_{}, inlineHash_{};
    State state_=State::Ready;
    Failure failure_{};
    std::size_t used_=0, next_=0, wireBytes_=FixedOverhead;
    Sha256 sectionHash_{};
    Utf8 utf8_{};
    bool ready_=false;
    static std::size_t Frames(std::size_t n) noexcept { return (n+FrameLimit-1)/FrameLimit; }
    bool Fail(Error e,int slot=-1,std::size_t n=0,int io=0) noexcept {
        if(failure_.reason==Error::None) failure_={e,slot,n,io};
        state_=State::Failed; return false;
    }
    bool Output(Sink& sink,Sha256& whole,const void* p,std::size_t n) noexcept {
        if (state_!=State::Writing) return false;
        int err=0;
        if (!sink.write(sink.context,static_cast<const std::uint8_t*>(p),n,err))
            return Fail(Error::SinkWrite,-1,0,err);
        // A re-entering callback must not be able to return this operation to
        // success; preserve the first nested rejection instead.
        if(state_!=State::Writing) return false;
        return whole.Update(p,n) || Fail(Error::Resource);
    }
public:
    Capture() = default;
    Capture(const Capture&)=delete;
    Capture& operator=(const Capture&)=delete;
    // Preparation takes digests from the trusted canonical identity/envelope
    // owner; it does not authenticate a self-reported PID/build on its own.
    bool Prepare(const Digest& binding,const Digest& inlineHash,std::size_t inlineBytes) noexcept {
        if(ready_ || state_!=State::Ready) return Fail(Error::State);
        if(inlineBytes>InlineLimit) return Fail(Error::Resource);
        binding_=binding; inlineHash_=inlineHash; ready_=true; return true;
    }
    bool Begin(unsigned slot,bool isNull) noexcept {
        if(state_==State::Writing) return Fail(Error::Reentry);
        if(!ready_ || state_!=State::Ready) return Fail(Error::State,static_cast<int>(slot));
        if(next_>=2 || slot!=14+next_) return Fail(Error::SlotOrder,static_cast<int>(slot));
        sections_[next_].offset=used_; sections_[next_].isNull=isNull;
        sectionHash_=Sha256{}; utf8_=Utf8{}; state_=State::Section; return true;
    }
    bool Append(const void* p,std::size_t n) noexcept {
        if(state_==State::Writing) return Fail(Error::Reentry);
        if(state_!=State::Section) return Fail(Error::State);
        auto& s=sections_[next_]; const int slot=static_cast<int>(14+next_);
        if(n>0 && p==nullptr) return Fail(Error::InvalidPointer,slot);
        if(s.isNull && n!=0) return Fail(Error::NullContent,slot);
        // Check sizes before pointer inspection, arithmetic overflow or copies.
        if(n>RawCapacity-used_) return Fail(Error::Resource,slot,s.length);
        const auto frames=Frames(s.length+n);
        const auto extra=frames-Frames(s.length);
        if(frames>64 || n>ArtifactBudget-wireBytes_ ||
           extra*FrameOverhead>ArtifactBudget-wireBytes_-n) return Fail(Error::Resource,slot,s.length);
        if(!utf8_.Add(static_cast<const std::uint8_t*>(p),n)) return Fail(Error::InvalidUtf8,slot,s.length);
        if(n) std::memcpy(bytes_.data()+used_,p,n);
        if(!sectionHash_.Update(p,n)) return Fail(Error::Resource,slot,s.length);
        s.length+=n; used_+=n; wireBytes_+=n+extra*FrameOverhead; return true;
    }
    bool End() noexcept {
        if(state_!=State::Section) return Fail(state_==State::Writing?Error::Reentry:Error::State);
        if(!utf8_.Complete()) return Fail(Error::InvalidUtf8,static_cast<int>(14+next_),sections_[next_].length);
        sections_[next_].hash=sectionHash_.Final(); ++next_; state_=State::Ready; return true;
    }
    bool Freeze() noexcept {
        if(!ready_ || state_!=State::Ready || next_!=2) return Fail(Error::State);
        state_=State::Frozen; return true;
    }
    bool Encode(Sink sink, Descriptor& out) noexcept {
        // Descriptor is published only after complete output and durable finish.
        out=Descriptor{};
        if(state_!=State::Frozen) return Fail(state_==State::Writing?Error::Reentry:Error::State);
        if(!sink.write || !sink.finish) return Fail(Error::InvalidPointer);
        state_=State::Writing; Sha256 whole;
        std::uint8_t header[72]{};
        std::memcpy(header,"R03DIA2\0",8); std::memcpy(header+8,binding_.data(),32);
        std::memcpy(header+40,inlineHash_.data(),32);
        if(!Output(sink,whole,header,sizeof header)) return false;
        for(std::size_t j=0;j<2;++j) {
            const auto& s=sections_[j]; const auto count=Frames(s.length);
            std::uint8_t sh[40]{}; sh[0]=static_cast<std::uint8_t>(14+j); sh[1]=s.isNull?0:1;
            U32(sh+2,static_cast<std::uint32_t>(s.length)); U16(sh+6,static_cast<std::uint16_t>(count));
            std::memcpy(sh+8,s.hash.data(),32);
            if(!Output(sink,whole,sh,sizeof sh)) return false;
            for(std::size_t i=0;i<count;++i) {
                const auto offset=i*FrameLimit; const auto n=s.length-offset<FrameLimit?s.length-offset:FrameLimit;
                const auto* part=bytes_.data()+s.offset+offset;
                Sha256 frame; constexpr char domain[]="R03-FRAME-V2";
                frame.Update(domain,sizeof domain); frame.Update(binding_.data(),32);
                std::uint8_t context[9]{}; context[0]=sh[0]; U32(context+1,static_cast<std::uint32_t>(i));
                U32(context+5,static_cast<std::uint32_t>(n)); frame.Update(context,sizeof context); frame.Update(part,n);
                std::uint8_t fh[38]{}; U32(fh,static_cast<std::uint32_t>(i)); U16(fh+4,static_cast<std::uint16_t>(n-1));
                const auto digest=frame.Final(); std::memcpy(fh+6,digest.data(),32);
                if(!Output(sink,whole,fh,sizeof fh) || !Output(sink,whole,part,n)) return false;
            }
        }
        const auto prefix=whole.Final(); std::uint8_t footer[40]{};
        std::memcpy(footer,"R03END2\0",8); std::memcpy(footer+8,prefix.data(),32);
        if(!Output(sink,whole,footer,sizeof footer)) return false;
        int error=0;
        if(!sink.finish(sink.context,error)) return Fail(Error::SinkFinish,-1,0,error);
        if(state_!=State::Writing) return false;
        out={binding_,inlineHash_,whole.Final(),wireBytes_}; state_=State::Done; return true;
    }
    const Failure& FirstFailure() const noexcept { return failure_; }
    std::size_t CapturedBytes() const noexcept { return used_; }
    std::size_t EncodedBytes() const noexcept { return wireBytes_; }
};
// Includes full reserved inline bytes plus codec/capture and a conservative
// 2KiB serializer stack reserve. Does NOT include producer metadata or host RSS.
static_assert(sizeof(Capture)+InlineLimit+2048<=TotalBudget,"capture/codec budget");
} // namespace r03::diagnostics_v2
