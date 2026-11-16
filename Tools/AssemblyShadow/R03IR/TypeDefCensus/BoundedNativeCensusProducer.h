#pragma once
// R03 B2 TEST ONLY. This type neither inspects nor authenticates Unity VM state.
// Caller supplies stable, borrowed observations while metadata is protected.
// Prepare allocates; Add and Finish perform no allocation or IO.
// EndCapture MUST be called after the source lock is released: it scrubs
// the only retained raw pointer-valued handle index. EmitJson runs later.
#include "../CapacityCandidates/BoundedHandlePatriciaIndex.h"
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <string>

namespace r03_b2_typedef_native_census {
namespace index_ns=r03_b2_typedef_capacity_candidates;
static const size_t kMaxDistinct=1024; // independent of B2 native 128; NOT a proposed product cap
static const size_t kMaxEvents=4096;
static const uint32_t kMaxNameLength=1000000;
enum class Role:uint8_t { Root=1, NonRoot=2 };
enum class Error:uint8_t { None, BadPrepare, Allocation, WrongStage, InvalidInput,
    FirstOwnerMismatch, DeclarationChanged, DistinctLimit, EventLimit, IndexInvariant, MissingCoverage };
struct Observation {
    uintptr_t handle=0; // opaque, used only as an equality key, never serialized
    uint32_t ownerImageOrdinal=0, firstOwnerImageOrdinal=0;
    Role role=Role::Root;
    uint32_t namespaceBytes=0, simpleNameBytes=0;
    int32_t declaringIndex=-1, genericIndex=-1;
    uint32_t arity=0;
};
struct SourceStamp {
    const char* nativeCommit=nullptr;
    const char* demoCommit=nullptr;
    uint32_t originalV1ImageCount=0;
    uint32_t observedClasses=0;
    uint32_t metadataReaderEpoch=0;
    bool metadataLockHeldDuringAdd=false;
    uint32_t classPasses=0, originalV1ImagePasses=0;
};
struct RecordedEvent {
    uint32_t handleId=0;
    uint32_t ownerImageOrdinal=0,firstOwnerImageOrdinal=0;
    uint32_t namespaceBytes=0,simpleNameBytes=0;
    int32_t declaringIndex=-1,genericIndex=-1;
    uint32_t arity=0;
    Role role=Role::Root;
};

class Producer final {
    using Index=index_ns::BoundedHandlePatriciaIndex;
    struct UniqueRecord {
        uint32_t owner=0, first=0, ns=0, name=0;
        int32_t declaring=-1,generic=-1;
        uint32_t arity=0;
    };
    Index index_{};
    std::unique_ptr<UniqueRecord[]> unique_{};
    std::unique_ptr<RecordedEvent[]> events_{};
    size_t uniqueLimit_=0,eventLimit_=0,uniques_=0,eventsUsed_=0;
    uint32_t dropped_=0;
    Error first_=Error::None;
    enum class State { New, Collecting, Complete, Incomplete };
    State state_=State::New;

    void Fail(Error e) noexcept {
        if(first_==Error::None)first_=e;
        state_=State::Incomplete;
        if(dropped_<200000u)++dropped_;
        index_.Clear(); // raw handles are discarded even on failure
    }
    static bool Same(const UniqueRecord& a,const Observation& b) noexcept {
        return a.owner==b.ownerImageOrdinal && a.first==b.firstOwnerImageOrdinal &&
            a.ns==b.namespaceBytes && a.name==b.simpleNameBytes &&
            a.declaring==b.declaringIndex && a.generic==b.genericIndex &&
            a.arity==b.arity;
    }
    static bool Sha(const char* s) noexcept {
        if(!s)return false;
        for(size_t i=0;i<40;++i)
            if(!((s[i]>='0'&&s[i]<='9')||(s[i]>='a'&&s[i]<='f')))return false;
        return s[40]=='\0';
    }
    static void AppendUInt(std::string& out,uint64_t n) {
        char buf[32];std::snprintf(buf,sizeof(buf),"%llu",static_cast<unsigned long long>(n));
        out+=buf;
    }
    static void AppendInt(std::string& out,int32_t n) {
        char buf[32];std::snprintf(buf,sizeof(buf),"%d",static_cast<int>(n));
        out+=buf;
    }
public:
    Producer() noexcept=default;
    ~Producer() noexcept {Release();}
    Producer(const Producer&)=delete;
    Producer& operator=(const Producer&)=delete;
    Error FirstError() const noexcept{return first_;}
    size_t RecordedEvents() const noexcept{return eventsUsed_;}
    size_t DistinctHandles() const noexcept{return uniques_;}
    uint32_t DroppedEvents() const noexcept{return dropped_;}
    bool Complete() const noexcept{return state_==State::Complete;}
    bool RawHandlesScrubbed() const noexcept {
        return state_!=State::Collecting && index_.Count()==0;
    }
    size_t ReservedBytes() const noexcept {
        return index_.ReservedBytes()+uniqueLimit_*sizeof(UniqueRecord)+
               eventLimit_*sizeof(RecordedEvent);
    }
    bool Prepare(size_t uniqueLimit,size_t eventLimit) noexcept {
        if(state_!=State::New) {Fail(Error::WrongStage);return false;}
        if(!uniqueLimit || uniqueLimit>kMaxDistinct || !eventLimit ||
           eventLimit>kMaxEvents) {Fail(Error::BadPrepare);return false;}
        unique_.reset(new(std::nothrow) UniqueRecord[uniqueLimit]());
        events_.reset(new(std::nothrow) RecordedEvent[eventLimit]());
        if(!unique_ || !events_ || !index_.Prepare(uniqueLimit)) {
            Release(); first_=Error::Allocation;state_=State::Incomplete;
            return false;
        }
        uniqueLimit_=uniqueLimit;eventLimit_=eventLimit;
        state_=State::Collecting;return true;
    }
    // Caller must have authenticated the original first-emplace image owner.
    // This method verifies only that supplied scalar values agree; never
    // dereferences handle/owner pointers or claims callback completeness.
    bool Add(const Observation& value,uint32_t imageCount) noexcept {
        if(state_!=State::Collecting){
            if(state_==State::New)Fail(Error::WrongStage);
            return false;
        }
        if(!value.handle || !imageCount ||
            (value.role!=Role::Root && value.role!=Role::NonRoot) ||
            value.ownerImageOrdinal>=imageCount ||
            value.firstOwnerImageOrdinal>=imageCount ||
            value.namespaceBytes>kMaxNameLength ||
            value.simpleNameBytes>kMaxNameLength){Fail(Error::InvalidInput);return false;}
        if(value.ownerImageOrdinal!=value.firstOwnerImageOrdinal){
            Fail(Error::FirstOwnerMismatch);return false;
        }
        if(eventsUsed_==eventLimit_){Fail(Error::EventLimit);return false;}
        size_t row=0,visits=0;
        bool found=index_.Find(value.handle,row,visits);
        if(visits>Index::kMaxLookupVisits){Fail(Error::IndexInvariant);return false;}
        if(found){
            if(row>=uniques_ || !Same(unique_[row],value)){
                Fail(Error::DeclarationChanged);return false;
            }
        } else {
            if(uniques_==uniqueLimit_){Fail(Error::DistinctLimit);return false;}
            if(!index_.Insert(value.handle,uniques_,visits) ||
               visits>Index::kMaxInsertVisits){Fail(Error::IndexInvariant);return false;}
            row=uniques_++;
            UniqueRecord& u=unique_[row];
            u.owner=value.ownerImageOrdinal;u.first=value.firstOwnerImageOrdinal;
            u.ns=value.namespaceBytes;u.name=value.simpleNameBytes;
            u.declaring=value.declaringIndex;u.generic=value.genericIndex;
            u.arity=value.arity;
        }
        RecordedEvent& r=events_[eventsUsed_++];
        r.handleId=static_cast<uint32_t>(row+1u);
        r.ownerImageOrdinal=value.ownerImageOrdinal;
        r.firstOwnerImageOrdinal=value.firstOwnerImageOrdinal;
        r.namespaceBytes=value.namespaceBytes;r.simpleNameBytes=value.simpleNameBytes;
        r.declaringIndex=value.declaringIndex;r.genericIndex=value.genericIndex;
        r.arity=value.arity;r.role=value.role;
        return true;
    }
    // Missing/unsupported type path: cannot claim a complete census.
    void MarkUncovered() noexcept {
        if(state_==State::Collecting)Fail(Error::MissingCoverage);
    }
    // Invoke after the source callback/metadata lock has exited. Counts
    // remain an unauthenticated population observation, not VM acceptance.
    bool EndCapture() noexcept {
        if(state_!=State::Collecting)return false;
        index_.Clear();state_=State::Complete;return true;
    }
    // A separate caller must invoke this ONLY after source protection exits.
    // Serialization allocates and cannot run inside the metadata lock.
    // The returned JSON is UNVERIFIED even if source claims healthy passes.
    bool EmitJson(const SourceStamp& stamp,std::string& out) const {
        out.clear();
        if(state_!=State::Complete && state_!=State::Incomplete)return false;
        if(!RawHandlesScrubbed() || !Sha(stamp.nativeCommit) ||
           !Sha(stamp.demoCommit) || stamp.originalV1ImageCount==0 ||
           stamp.originalV1ImageCount>65536u || stamp.observedClasses>200000u ||
           stamp.metadataReaderEpoch!=1 || !stamp.metadataLockHeldDuringAdd ||
           stamp.classPasses!=3 || stamp.originalV1ImagePasses!=2)return false;
        out="{\"schema\":\"R03B2TypeDefCensusV1\",\"captureKind\":\"UnverifiedSource\",\"source\":{\"branch\":\"codex/assembly-shadow-r01b-h1\",\"nativeCommit\":\"";
        out+=stamp.nativeCommit;out+="\",\"demoCommit\":\"";out+=stamp.demoCommit;
        out+="\",\"metadataReaderEpoch\":1,\"metadataLockHeld\":true,\"originalV1ImageCount\":";
        AppendUInt(out,stamp.originalV1ImageCount);
        out+=",\"classPasses\":3,\"originalV1ImagePasses\":2,\"observedClasses\":";
        AppendUInt(out,stamp.observedClasses);
        out+=",\"declaredEvents\":";AppendUInt(out,eventsUsed_);
        out+=",\"droppedEvents\":";AppendUInt(out,dropped_);
        out+=",\"complete\":";
        out+=(state_==State::Complete?"true":"false");out+="},\"events\":[";
        for(size_t i=0;i<eventsUsed_;++i){
            if(i)out+=',';
            const RecordedEvent& e=events_[i];
            out+="{\"handleId\":";AppendUInt(out,e.handleId);
            out+=",\"ownerImageOrdinal\":";AppendUInt(out,e.ownerImageOrdinal);
            out+=",\"firstOwnerImageOrdinal\":";AppendUInt(out,e.firstOwnerImageOrdinal);
            out+=",\"role\":\"";out+=(e.role==Role::Root?"root":"nonroot");
            out+="\",\"namespaceBytes\":";AppendUInt(out,e.namespaceBytes);
            out+=",\"simpleNameBytes\":";AppendUInt(out,e.simpleNameBytes);
            out+=",\"declaringIndex\":";AppendInt(out,e.declaringIndex);
            out+=",\"genericIndex\":";AppendInt(out,e.genericIndex);
            out+=",\"arity\":";AppendUInt(out,e.arity);out+='}';
        }
        out+="]}\n";
        return true;
    }
    void Release() noexcept {
        index_.Release();
        if(unique_)for(size_t i=0;i<uniqueLimit_;++i)unique_[i]=UniqueRecord{};
        if(events_)for(size_t i=0;i<eventLimit_;++i)events_[i]=RecordedEvent{};
        unique_.reset();events_.reset();
        uniqueLimit_=eventLimit_=uniques_=eventsUsed_=0;
        dropped_=0;first_=Error::None;state_=State::New;
    }
};
} // namespace r03_b2_typedef_native_census
