#pragma once
// R03 B2 INACTIVE capacity prototypes, NOT attached to the VM/Player.
// Caller must authenticate owner/metadata provenance before Add().
// Prepare() is the ONLY allocating method and MUST run before metadata lock.
// No class/GC/VM epoch, original V1 parity, or runtime acceptance is claimed.
#include "BoundedHandlePatriciaIndex.h"
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <new>

namespace r03_b2_typedef_capacity_candidates {

static const size_t kMaximumPairs=1024;
static const size_t kMaximumNameBytes=64;
static const uint8_t kRoot=1, kNonRoot=2;

enum class Error : uint8_t {
    None, BadPrepare, AllocationFailed, WrongStage, InvalidInput,
    NameLimit, OwnerConflict, ContentChanged, PairCapacity, ArenaCapacity,
    IndexInvariant
};
struct View {
    uintptr_t handle=0, owner=0; // opaque values: no dereference
    const char* nameSpace=nullptr;
    size_t namespaceBytes=0;
    const char* simpleName=nullptr;
    size_t nameBytes=0;
    int32_t declaringIndex=0, genericIndex=0;
    uint32_t arity=0;
    uint8_t roles=0; // kRoot|kNonRoot
};
struct Receipt {
    bool complete=false;
    bool realUnity=false, coherentVmEpoch=false, runtimeAcceptance=false;
    size_t pairs=0, roots=0, nonRoots=0;
    size_t reservedBytes=0, exactNameBytes=0;
    size_t indexReservedBytes=0,indexNodeCapacity=0;
    size_t totalLookupVisits=0,maximumLookupVisits=0,maximumInsertVisits=0;
    size_t deterministicLookupVisitBound=BoundedHandlePatriciaIndex::kMaxLookupVisits;
};
inline bool SameBytes(const char* a,const char* b,size_t n) noexcept {
    return !n || std::memcmp(a,b,n)==0;
}
inline bool Valid(const View& v) noexcept {
    return v.handle && v.owner &&
        (!v.namespaceBytes || v.nameSpace) &&
        (!v.nameBytes || v.simpleName) &&
        v.namespaceBytes<=kMaximumNameBytes &&
        v.nameBytes<=kMaximumNameBytes &&
        v.roles && !(v.roles&~(kRoot|kNonRoot));
}
struct Metadata {
    uintptr_t handle=0, owner=0;
    int32_t declaringIndex=0,genericIndex=0;
    uint32_t arity=0;
    uint8_t roles=0,namespaceBytes=0,nameBytes=0;
};
inline bool MatchMetadata(const Metadata& a,const View& b) noexcept {
    return a.handle==b.handle && a.owner==b.owner &&
        a.declaringIndex==b.declaringIndex &&
        a.genericIndex==b.genericIndex && a.arity==b.arity &&
        a.namespaceBytes==b.namespaceBytes && a.nameBytes==b.nameBytes;
}
inline Metadata ToMetadata(const View& v) noexcept {
    Metadata m{};
    m.handle=v.handle; m.owner=v.owner;
    m.declaringIndex=v.declaringIndex; m.genericIndex=v.genericIndex;
    m.arity=v.arity; m.roles=v.roles;
    m.namespaceBytes=static_cast<uint8_t>(v.namespaceBytes);
    m.nameBytes=static_cast<uint8_t>(v.nameBytes);
    return m;
}

// Candidate A: fixed record slab. Worst case exactly two 64-byte name arrays
// per pair, even when real namespace/simple-name text is much shorter.
class SlabStorage final {
    struct Entry {
        Metadata meta{};
        char nameSpace[kMaximumNameBytes]{};
        char simpleName[kMaximumNameBytes]{};
    };
    std::unique_ptr<Entry[]> items_{};
    size_t capacity_=0;
public:
    SlabStorage() noexcept=default;
    ~SlabStorage() noexcept{Release();}
    SlabStorage(const SlabStorage&)=delete;
    SlabStorage& operator=(const SlabStorage&)=delete;
    bool Prepare(size_t capacity,size_t) noexcept {
        if(items_ || !capacity || capacity>kMaximumPairs)return false;
        items_.reset(new(std::nothrow) Entry[capacity]());
        if(!items_)return false;
        capacity_=capacity;return true;
    }
    size_t ReservedBytes() const noexcept{return capacity_*sizeof(Entry);}
    bool Put(size_t i,const View& v) noexcept {
        if(i>=capacity_ || !items_)return false;
        Entry& e=items_[i];e.meta=ToMetadata(v);
        if(v.namespaceBytes)std::memcpy(e.nameSpace,v.nameSpace,v.namespaceBytes);
        if(v.nameBytes)std::memcpy(e.simpleName,v.simpleName,v.nameBytes);
        return true;
    }
    const Metadata& Meta(size_t i) const noexcept{return items_[i].meta;}
    bool Same(size_t i,const View& v) const noexcept {
        const Entry& e=items_[i];
        return MatchMetadata(e.meta,v) &&
            SameBytes(e.nameSpace,v.nameSpace,v.namespaceBytes) &&
            SameBytes(e.simpleName,v.simpleName,v.nameBytes);
    }
    void MergeRole(size_t i,uint8_t roles) noexcept{items_[i].meta.roles|=roles;}
    void Clear() noexcept {
        for(size_t i=0;i<capacity_;++i)items_[i]=Entry{};
    }
    void Release() noexcept {Clear();items_.reset();capacity_=0;}
};

// Candidate B: compact metadata records plus an exact-byte packed arena.
// The arena is deliberately NOT an interned string table: duplicate handles
// reuse their own existing bytes; unrelated declarations never alias names.
class ArenaStorage final {
    struct Entry {
        Metadata meta{};
        uint32_t namespaceOffset=0,nameOffset=0;
    };
    std::unique_ptr<Entry[]> items_{};
    std::unique_ptr<char[]> arena_{};
    size_t capacity_=0,arenaCapacity_=0,used_=0;
public:
    ArenaStorage() noexcept=default;
    ~ArenaStorage() noexcept{Release();}
    ArenaStorage(const ArenaStorage&)=delete;
    ArenaStorage& operator=(const ArenaStorage&)=delete;
    bool Prepare(size_t capacity,size_t arenaBytes) noexcept {
        if(items_ || arena_ || !capacity || capacity>kMaximumPairs ||
           !arenaBytes || arenaBytes>kMaximumPairs*kMaximumNameBytes*2)
            return false;
        items_.reset(new(std::nothrow) Entry[capacity]());
        if(!items_)return false;
        arena_.reset(new(std::nothrow) char[arenaBytes]());
        if(!arena_){items_.reset();return false;}
        capacity_=capacity;arenaCapacity_=arenaBytes;used_=0;return true;
    }
    size_t ReservedBytes() const noexcept {
        return capacity_*sizeof(Entry)+arenaCapacity_;
    }
    bool Put(size_t i,const View& v) noexcept {
        const size_t needed=v.namespaceBytes+v.nameBytes;
        if(i>=capacity_ || !items_ || !arena_ ||
           needed>arenaCapacity_-used_)return false;
        Entry& e=items_[i];
        e.meta=ToMetadata(v);
        e.namespaceOffset=static_cast<uint32_t>(used_);
        if(v.namespaceBytes)
            std::memcpy(arena_.get()+used_,v.nameSpace,v.namespaceBytes);
        used_+=v.namespaceBytes;
        e.nameOffset=static_cast<uint32_t>(used_);
        if(v.nameBytes)
            std::memcpy(arena_.get()+used_,v.simpleName,v.nameBytes);
        used_+=v.nameBytes;
        return true;
    }
    const Metadata& Meta(size_t i) const noexcept{return items_[i].meta;}
    bool Same(size_t i,const View& v) const noexcept {
        const Entry& e=items_[i];
        return MatchMetadata(e.meta,v) &&
            SameBytes(arena_.get()+e.namespaceOffset,
                      v.nameSpace,v.namespaceBytes) &&
            SameBytes(arena_.get()+e.nameOffset,
                      v.simpleName,v.nameBytes);
    }
    void MergeRole(size_t i,uint8_t roles) noexcept{items_[i].meta.roles|=roles;}
    void Clear() noexcept {
        for(size_t i=0;i<capacity_;++i)items_[i]=Entry{};
        if(arena_)std::memset(arena_.get(),0,arenaCapacity_);
        used_=0;
    }
    void Release() noexcept {
        Clear();items_.reset();arena_.reset();capacity_=arenaCapacity_=0;
    }
};

template<class Storage>
class Census final {
    Storage storage_{};
    BoundedHandlePatriciaIndex index_{};
    size_t capacity_=0,count_=0,nameBytes_=0;
    size_t totalLookupVisits_=0,maximumLookupVisits_=0,maximumInsertVisits_=0;
    Error first_=Error::None;
    enum class Stage:uint8_t{New,Collecting,Complete,Failed};
    Stage stage_=Stage::New;
    bool Fail(Error e) noexcept {
        if(first_==Error::None)first_=e;
        stage_=Stage::Failed;storage_.Clear();index_.Clear();
        count_=nameBytes_=totalLookupVisits_=0;
        maximumLookupVisits_=maximumInsertVisits_=0;
        return false;
    }
public:
    Census() noexcept=default;
    Census(const Census&)=delete;
    Census& operator=(const Census&)=delete;
    Error FirstError() const noexcept{return first_;}
    size_t ReservedBytes() const noexcept {
        return storage_.ReservedBytes()+index_.ReservedBytes();
    }
    bool Prepare(size_t capacity,size_t arenaBudget=1) noexcept {
        if(stage_!=Stage::New)return Fail(Error::WrongStage);
        if(!capacity || capacity>kMaximumPairs)return Fail(Error::BadPrepare);
        if(!storage_.Prepare(capacity,arenaBudget))
            return Fail(Error::AllocationFailed);
        if(!index_.Prepare(capacity)) {
            storage_.Release(); // no partial prepared candidate on OOM
            return Fail(Error::AllocationFailed);
        }
        capacity_=capacity;stage_=Stage::Collecting;return true;
    }
    // Add does NOT allocate, dereference handle/owner or keep input strings.
    // Owner/TypeDef identity must already be authenticated by the caller.
    bool Add(const View& view) noexcept {
        if(stage_!=Stage::Collecting)return Fail(Error::WrongStage);
        if(view.namespaceBytes>kMaximumNameBytes ||
           view.nameBytes>kMaximumNameBytes)return Fail(Error::NameLimit);
        if(!Valid(view))return Fail(Error::InvalidInput);
        // Indexed handle lookup is independent of the number and order of
        // records. The Patricia path has <= pointer-width+1 node visits even
        // for deliberately adversarial handle bit patterns (no hash attack).
        size_t existing=0,lookupVisits=0;
        const bool found=index_.Find(view.handle,existing,lookupVisits);
        totalLookupVisits_+=lookupVisits;
        if(lookupVisits>maximumLookupVisits_)
            maximumLookupVisits_=lookupVisits;
        if(lookupVisits>BoundedHandlePatriciaIndex::kMaxLookupVisits)
            return Fail(Error::IndexInvariant);
        if(found) {
            if(existing>=count_)return Fail(Error::IndexInvariant);
            const Metadata& m=storage_.Meta(existing);
            if(m.handle!=view.handle)return Fail(Error::IndexInvariant);
            if(m.owner!=view.owner)return Fail(Error::OwnerConflict);
            if(!storage_.Same(existing,view))
                return Fail(Error::ContentChanged);
            storage_.MergeRole(existing,view.roles);return true;
        }
        if(count_==capacity_)return Fail(Error::PairCapacity);
        if(!storage_.Put(count_,view))return Fail(Error::ArenaCapacity);
        size_t insertVisits=0;
        if(!index_.Insert(view.handle,count_,insertVisits) ||
           insertVisits>BoundedHandlePatriciaIndex::kMaxInsertVisits)
            return Fail(Error::IndexInvariant);
        if(insertVisits>maximumInsertVisits_)
            maximumInsertVisits_=insertVisits;
        nameBytes_+=view.namespaceBytes+view.nameBytes;
        ++count_;return true;
    }
    bool Seal(Receipt& receipt) noexcept {
        receipt=Receipt{};
        if(stage_!=Stage::Collecting)return Fail(Error::WrongStage);
        // Validate index invariants BEFORE any positive receipt or
        // Complete transition. An index failure must never leave a
        // previously emitted success-like receipt.
        if(index_.Count()!=count_ ||
           maximumLookupVisits_>BoundedHandlePatriciaIndex::kMaxLookupVisits ||
           maximumInsertVisits_>BoundedHandlePatriciaIndex::kMaxInsertVisits)
            return Fail(Error::IndexInvariant);
        receipt.pairs=count_;
        receipt.exactNameBytes=nameBytes_;
        receipt.reservedBytes=ReservedBytes();
        receipt.indexReservedBytes=index_.ReservedBytes();
        receipt.indexNodeCapacity=index_.NodeCapacity();
        receipt.totalLookupVisits=totalLookupVisits_;
        receipt.maximumLookupVisits=maximumLookupVisits_;
        receipt.maximumInsertVisits=maximumInsertVisits_;
        for(size_t i=0;i<count_;++i) {
            const uint8_t roles=storage_.Meta(i).roles;
            if(roles&kRoot)++receipt.roots;
            if(roles&kNonRoot)++receipt.nonRoots;
        }
        stage_=Stage::Complete;
        receipt.complete=true; // publish only after all checks
        return true;
    }
    void Release() noexcept {
        storage_.Release();index_.Release();
        capacity_=count_=nameBytes_=totalLookupVisits_=0;
        maximumLookupVisits_=maximumInsertVisits_=0;
        first_=Error::None;stage_=Stage::New;
    }
};
using FixedSlabCensus=Census<SlabStorage>;
using CompactArenaCensus=Census<ArenaStorage>;
} // namespace r03_b2_typedef_capacity_candidates
