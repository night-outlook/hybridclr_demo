#pragma once
// R03 B2 TEST ONLY: a bounded two-pass coverage replay for a synthetic source.
// No connection to Unity, il2cpp_class_for_each, metadata locks or GC epoch.
// A caller must independently prove that discovery enumerates *all* source
// paths. Matching two enumerations cannot prove absence of omitted paths.
// Prepare alone allocates; every plan/visit/close operation is allocation-free.
// Source pointers stay borrowed only through VisitUse. EmitJson is post-source.
#include "OriginalV1OwnerSourceAdapter.h"
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <string>

namespace r03_b2_typedef_coverage_replay {
namespace census=r03_b2_typedef_native_census;
namespace owner=r03_b2_original_v1_source_adapter;

// Source-aware categories derived from the current restricted B2 TypeKey
// paths: buildDefinition root/declaring ancestry and Composer raw cases.
// Distinct source occurrences must use distinct site slots, even when the
// same handle is shared by root, nested, generic or primitive roles.
enum class Kind : uint8_t {
    ClassRoot=1, DeclaringAncestor=2, GenericDefinition=3,
    GenericArgument=4, CompositeClassLeaf=5, PrimitiveDefault=6
};
inline bool ValidKind(Kind kind) noexcept {
    return kind==Kind::ClassRoot || kind==Kind::DeclaringAncestor ||
           kind==Kind::GenericDefinition || kind==Kind::GenericArgument ||
           kind==Kind::CompositeClassLeaf || kind==Kind::PrimitiveDefault;
}
inline census::Role RoleFor(Kind kind) noexcept {
    return kind==Kind::ClassRoot?census::Role::Root:census::Role::NonRoot;
}

enum class Error : uint8_t {
    None, BadPrepare, AllocationFailed, WrongStage,
    InvalidClassSlot, DuplicateClassSlot, InvalidSite,
    DuplicateSite, MissingPlannedCoverage, MissingVisitedCoverage,
    SourcePathMismatch, OwnerRejected, UnsupportedPath, Abandoned
};

class Replay final {
    struct Site {
        uint16_t classSlot=0;
        Kind kind=Kind::ClassRoot;
        bool visited=false;
    };
    // The producer owns both event storage and the only opaque handle index.
    // The adapter borrows it, and is destroyed before producer_ by C++ member
    // reverse-destruction order. Neither pointer escapes this object.
    census::Producer producer_{};
    owner::Adapter adapter_{};
    std::unique_ptr<uint8_t[]> plannedClass_{};
    std::unique_ptr<uint8_t[]> visitedClass_{};
    std::unique_ptr<uint8_t[]> plannedRoot_{};
    std::unique_ptr<Site[]> sites_{};
    size_t classCapacity_=0,siteCapacity_=0;
    size_t classesPlanned_=0,sitesPlanned_=0;
    size_t classesVisited_=0,sitesVisited_=0;
    enum class Stage : uint8_t { New, Planning, Visiting, Closed, Failed };
    Stage stage_=Stage::New;
    Error first_=Error::None;

    bool Fail(Error reason) noexcept {
        if(first_==Error::None)first_=reason;
        stage_=Stage::Failed;
        adapter_.MarkUncovered();
        producer_.MarkUncovered();
        return false;
    }
public:
    Replay() noexcept=default;
    Replay(const Replay&)=delete;
    Replay& operator=(const Replay&)=delete;
    ~Replay() noexcept {
        if(stage_==Stage::Planning || stage_==Stage::Visiting)
            Fail(Error::Abandoned);
        Reset();
    }
    Error FirstError() const noexcept {return first_;}
    bool Complete() const noexcept {
        return stage_==Stage::Closed && producer_.Complete();
    }
    bool RawHandlesScrubbed() const noexcept {
        return producer_.RawHandlesScrubbed();
    }
    size_t PlannedClasses() const noexcept {return classesPlanned_;}
    size_t PlannedSites() const noexcept {return sitesPlanned_;}
    size_t VisitedClasses() const noexcept {return classesVisited_;}
    size_t VisitedSites() const noexcept {return sitesVisited_;}
    size_t DistinctHandles() const noexcept {return producer_.DistinctHandles();}
    size_t RecordedEvents() const noexcept {return producer_.RecordedEvents();}
    size_t IndexedOwnerLookups() const noexcept {return adapter_.IndexedLookups();}
    size_t ReservedBytes() const noexcept {
        return producer_.ReservedBytes()+classCapacity_*3u*sizeof(uint8_t)+
               siteCapacity_*sizeof(Site);
    }
    // Preallocate outside any prospective metadata source lock.
    // expected class/site counts are untrusted caller assertions until a
    // separately reviewed native enumerator authenticates them.
    bool Prepare(size_t expectedClasses,size_t expectedSites,
                 uint32_t originalV1Images,size_t ownerLookupBudget) noexcept {
        if(stage_!=Stage::New)return Fail(Error::WrongStage);
        if(!expectedClasses || expectedClasses>1024u ||
           !expectedSites || expectedSites>4096u ||
           expectedSites<expectedClasses ||
           !originalV1Images || originalV1Images>1024u ||
           !ownerLookupBudget || ownerLookupBudget>1000000u)
            return Fail(Error::BadPrepare);
        plannedClass_.reset(new(std::nothrow) uint8_t[expectedClasses]());
        visitedClass_.reset(new(std::nothrow) uint8_t[expectedClasses]());
        plannedRoot_.reset(new(std::nothrow) uint8_t[expectedClasses]());
        sites_.reset(new(std::nothrow) Site[expectedSites]());
        if(!plannedClass_ || !visitedClass_ || !plannedRoot_ || !sites_)
            return Fail(Error::AllocationFailed);
        classCapacity_=expectedClasses;siteCapacity_=expectedSites;
        if(!producer_.Prepare(expectedSites<1024u?expectedSites:1024u,
                              expectedSites) ||
           !adapter_.Open(producer_,originalV1Images,ownerLookupBudget))
            return Fail(Error::AllocationFailed);
        stage_=Stage::Planning;
        return true;
    }
    // Phase A: independent discovery callback plan. No raw handle is stored.
    // Class slots are dense but may arrive in any order.
    bool PlanClass(size_t slot) noexcept {
        if(stage_!=Stage::Planning)return Fail(Error::WrongStage);
        if(slot>=classCapacity_)return Fail(Error::InvalidClassSlot);
        if(plannedClass_[slot])return Fail(Error::DuplicateClassSlot);
        plannedClass_[slot]=1;++classesPlanned_;return true;
    }
    // A caller receives a stable one-based site ID. Repeated occurrences
    // need different IDs even if class/kind/handle values later coincide.
    bool PlanUse(size_t classSlot,Kind kind,size_t& siteId) noexcept {
        siteId=0;
        if(stage_!=Stage::Planning)return Fail(Error::WrongStage);
        if(classSlot>=classCapacity_ || !plannedClass_[classSlot] ||
           !ValidKind(kind))return Fail(Error::InvalidSite);
        if(sitesPlanned_==siteCapacity_)return Fail(Error::InvalidSite);
        if(kind==Kind::ClassRoot && plannedRoot_[classSlot])
            return Fail(Error::DuplicateSite);
        Site& site=sites_[sitesPlanned_];
        site.classSlot=static_cast<uint16_t>(classSlot);
        site.kind=kind;
        if(kind==Kind::ClassRoot)plannedRoot_[classSlot]=1;
        siteId=++sitesPlanned_;
        return true;
    }
    // Must seal the full declared discovery plan before any second-pass use.
    bool SealPlan() noexcept {
        if(stage_!=Stage::Planning)return Fail(Error::WrongStage);
        if(classesPlanned_!=classCapacity_ || sitesPlanned_!=siteCapacity_)
            return Fail(Error::MissingPlannedCoverage);
        for(size_t i=0;i<classCapacity_;++i)
            if(!plannedRoot_[i])return Fail(Error::MissingPlannedCoverage);
        stage_=Stage::Visiting;return true;
    }
    // Phase B: callback replay must bind exactly each planned class and site.
    bool VisitClass(size_t slot) noexcept {
        if(stage_!=Stage::Visiting)return Fail(Error::WrongStage);
        if(slot>=classCapacity_ || !plannedClass_[slot])
            return Fail(Error::InvalidClassSlot);
        if(visitedClass_[slot])return Fail(Error::DuplicateClassSlot);
        visitedClass_[slot]=1;++classesVisited_;return true;
    }
    bool VisitUse(size_t siteId,size_t classSlot,Kind kind,
                  const owner::ImageView* images,size_t imageCount,
                  const census::Observation& use) noexcept {
        if(stage_!=Stage::Visiting)return Fail(Error::WrongStage);
        if(!siteId || siteId>sitesPlanned_ || classSlot>=classCapacity_ ||
           !visitedClass_[classSlot])return Fail(Error::InvalidSite);
        Site& site=sites_[siteId-1u];
        if(site.visited)return Fail(Error::DuplicateSite);
        if(site.classSlot!=classSlot || site.kind!=kind ||
           use.role!=RoleFor(kind))return Fail(Error::SourcePathMismatch);
        if(!adapter_.AddUse(images,imageCount,use))
            return Fail(Error::OwnerRejected);
        site.visited=true;++sitesVisited_;return true;
    }
    // Report unsupported/earlier-rejected/unrecognized paths explicitly.
    // Failure leaves a lower-bound trace; it never promises coverage.
    void MarkUnsupported() noexcept {
        if(stage_==Stage::Planning || stage_==Stage::Visiting ||
           stage_==Stage::Closed)Fail(Error::UnsupportedPath);
    }
    // Caller must invoke this *after* source protection leaves; this code
    // cannot verify metadata lock ownership or actual callback completeness.
    bool CloseAfterSource() noexcept {
        if(stage_!=Stage::Visiting)return Fail(Error::WrongStage);
        if(classesVisited_!=classCapacity_ || sitesVisited_!=siteCapacity_)
            return Fail(Error::MissingVisitedCoverage);
        if(!adapter_.CloseAfterSource())return Fail(Error::OwnerRejected);
        stage_=Stage::Closed;return true;
    }
    // Source-host JSON remains UnverifiedSource; outputs no raw handle values.
    // Only called after close/failure, never from source/metadata callbacks.
    bool EmitJson(const census::SourceStamp& stamp,std::string& out) const {
        out.clear();
        if(stage_!=Stage::Closed && stage_!=Stage::Failed)return false;
        return producer_.EmitJson(stamp,out);
    }
    void Reset() noexcept {
        if(stage_==Stage::Planning || stage_==Stage::Visiting)
            Fail(Error::Abandoned);
        adapter_.Reset();producer_.Release();
        plannedClass_.reset();visitedClass_.reset();plannedRoot_.reset();
        sites_.reset();
        classCapacity_=siteCapacity_=classesPlanned_=sitesPlanned_=0;
        classesVisited_=sitesVisited_=0;
        stage_=Stage::New;first_=Error::None;
    }
};
} // namespace r03_b2_typedef_coverage_replay
