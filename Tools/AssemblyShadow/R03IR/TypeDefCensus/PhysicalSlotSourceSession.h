#pragma once
// R03 B2 HOST-ONLY source-session mechanics against exact native Gate/Scan.
// NOT a Unity integration, metadata provenance proof or VM-wide lock/GC epoch.
// The mutex is a test-owned stand-in, NEVER assumed equivalent to g_MetadataLock.
// Prepare the Census before SourceSession. The initial-epoch Reader is acquired
// before this wrapper's source mutex; its destructor releases the mutex first.
// The source reader must remain admitted throughout both visits and sealing.
#include "PhysicalTypeDefSlotUpperBound.h"
#include "vm/AssemblyShadowMetadataLifetime.h"
#include "vm/AssemblyShadowOriginalV1ImageScan.h"
#include <mutex>
#include <utility>

namespace r03_b2_physical_slot_source_session {
namespace slots=r03_b2_physical_slot_upper_bound;
namespace native_gate=il2cpp::vm::assembly_shadow_metadata_lifetime;
namespace native_scan=il2cpp::vm::assembly_shadow_original_v1_image_scan;

class SourceSession final {
    slots::Census& census_;
    native_gate::Gate::Reader reader_;
    // Declared after Reader so its destructor unlocks BEFORE Reader leaves.
    std::unique_lock<std::mutex> sourceLock_;
    enum class Stage : unsigned char { Denied, First, Second, Sealed, Failed };
    Stage stage_=Stage::Denied;

    bool Fail() noexcept {
        stage_=Stage::Failed;
        census_.MarkUncovered();
        return false;
    }
    template<class Extract>
    struct Visit {
        slots::Census& census;
        Extract& extract;
        bool second;
        template<class Image>
        bool operator()(const Image* image) const noexcept {
            const slots::ImageFact fact=extract(image);
            return second?census.ObserveSecond(fact):census.ObserveFirst(fact);
        }
    };
public:
    SourceSession(slots::Census& census, native_gate::Gate& gate,
                  std::mutex& sourceMutex)
        :census_(census),reader_(gate),
         sourceLock_(sourceMutex,std::defer_lock) {
        if(!reader_){
            census_.MarkUncovered();
            return;
        }
        try {
            sourceLock_.lock();
            stage_=Stage::First;
        } catch (...) {
            census_.MarkUncovered();
            throw;
        }
    }
    SourceSession(const SourceSession&)=delete;
    SourceSession& operator=(const SourceSession&)=delete;
    ~SourceSession() noexcept {
        // This executes while both the initial Reader and source mutex live.
        // Never leave borrowed keys in Census when source protection ends.
        if(stage_==Stage::First || stage_==Stage::Second)
            Fail();
    }
    uint32_t ReaderEpoch() const noexcept {return reader_.Epoch();}
    bool SourceScopeHeld() const noexcept {
        return bool(reader_) && sourceLock_.owns_lock();
    }
    bool Sealed() const noexcept {
        return stage_==Stage::Sealed && census_.Complete();
    }
    template<class Iterator,class Extract>
    bool VisitFirst(Iterator first,Iterator last,Extract extract) noexcept {
        if(stage_!=Stage::First || !SourceScopeHeld())return Fail();
        Visit<Extract> callback{census_,extract,false};
        if(!native_scan::Scan(first,last,callback))return Fail();
        if(!census_.BeginSecond())return Fail();
        stage_=Stage::Second;
        return true;
    }
    template<class Iterator,class Extract>
    bool VisitSecondAndSeal(Iterator first,Iterator last,Extract extract) noexcept {
        if(stage_!=Stage::Second || !SourceScopeHeld())return Fail();
        Visit<Extract> callback{census_,extract,true};
        if(!native_scan::Scan(first,last,callback))return Fail();
        // Must scrub keys while Reader+mutex are BOTH still owned by us.
        if(!census_.SealWithinSourceScope())return Fail();
        stage_=Stage::Sealed;
        return true;
    }
    void MarkUncovered() noexcept {Fail();}
};
} // r03_b2_physical_slot_source_session
