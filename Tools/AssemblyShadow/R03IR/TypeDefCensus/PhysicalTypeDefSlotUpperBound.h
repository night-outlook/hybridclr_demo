#pragma once
// R03 B2 TEST ONLY — physical TypeDef-slot upper-bound candidate, NOT a VM census.
// Input must be supplied in ORIGINAL CopyValidAssemblies token-valid physical
// order, including interpreter and zero-TypeDef images. The host driver calls
// the ACTUAL pinned native AssemblyShadowOriginalV1ImageScan.h scanner.
// Prepare allocates before any prospective lock. Observe/close allocate nothing.
// All borrowed image/assembly keys are scrubbed before leaving source scope.
// Matching two caller-driven passes is NOT an independent VM/GC/source epoch.
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <new>

namespace r03_b2_physical_slot_upper_bound {

static const size_t kMaximumImages=1024;
static const uint32_t kExistingB2PerImageTypeLimit=8192;
static const uint64_t kExistingB2CombinedDistinctLimit=128;
static const uint64_t kCandidateStorageDistinctLimit=1024;

enum class Error : uint8_t {
    None, InvalidPrepare, AllocationFailed, WrongStage, InvalidImage,
    ImageCapacity, SlotBudget, SourceChanged, MissingSecondPass, EmptySource,
    UncoveredSource
};

struct ImageFact {
    // Opaque, never dereferenced. These must be valid only while source
    // lifetime/metadata/assembly protection is independently established.
    uintptr_t imageKey=0, assemblyKey=0;
    uint32_t assemblyToken=0, imageToken=0, typeCount=0;
    bool interpreter=false, ownerBacklinkMatched=false;
};

struct Receipt {
    Error error=Error::None;
    bool complete=false;
    bool syntheticOnly=true;
    bool sourceOriginAuthenticated=false;
    bool originalPhysicalEnumerationProven=false;
    bool coherentVmEpochProven=false;
    bool realUnity=false;
    bool nativeIntegrated=false;
    bool R03Accepted=false;
    bool ReadyForHumanReviewGate=false;
    bool capacityDecisionAuthorized=false;
    size_t firstPassImages=0,secondPassImages=0,zeroTypeImages=0;
    size_t interpreterImages=0,aotImages=0;
    uint64_t firstPassSlotOccurrences=0;
    uint64_t interpreterSlotOccurrences=0,aotSlotOccurrences=0;
    uint32_t maximumImageTypeCount=0;
    bool currentB2PerImageLimitExceeded=false;
    bool currentB2Combined128PotentiallyExceeded=false;
    bool prototype1024PotentiallyExceeded=false;
    // Applies ONLY to the supplied synthetic/unauthenticated complete image
    // inventory; not an accepted bound on any real Player's physical source.
    bool reportedUpperBoundForSuppliedInventory=false;
    uint64_t possibleDistinctFirstOwnerHandlesUpperBound=0;
};

class Census final {
    struct Record {
        uintptr_t imageKey=0,assemblyKey=0;
        uint32_t assemblyToken=0,imageToken=0,typeCount=0;
        bool interpreter=false;
        bool Matches(const ImageFact& other) const noexcept {
            return imageKey==other.imageKey && assemblyKey==other.assemblyKey &&
                assemblyToken==other.assemblyToken &&
                imageToken==other.imageToken && typeCount==other.typeCount &&
                interpreter==other.interpreter;
        }
    };
    enum class Stage : uint8_t { New, First, Second, Complete, Failed };
    std::unique_ptr<Record[]> records_{};
    Stage stage_=Stage::New;
    size_t imageLimit_=0,first_=0,second_=0,zero_=0,aot_=0,interpreter_=0;
    uint64_t slotBudget_=0,total_=0,aotSlots_=0,interpreterSlots_=0;
    uint32_t maximumImageTypes_=0;
    bool perImageCapExceeded_=false;
    Error firstError_=Error::None;

    void ScrubKeys() noexcept {
        if(records_)
            for(size_t i=0;i<imageLimit_;++i)records_[i]=Record{};
    }
    bool Fail(Error error) noexcept {
        if(firstError_==Error::None)firstError_=error;
        stage_=Stage::Failed;
        ScrubKeys();
        return false;
    }
    static bool Valid(const ImageFact& image) noexcept {
        // Original V1 CopyValidAssemblies selects ASSEMBLY token!=0; the
        // physical image token itself is NOT an eligibility filter here.
        return image.imageKey && image.assemblyKey && image.assemblyToken &&
            image.ownerBacklinkMatched;
    }
public:
    Census() noexcept=default;
    ~Census() noexcept {Release();}
    Census(const Census&)=delete;
    Census& operator=(const Census&)=delete;
    Error FirstError() const noexcept{return firstError_;}
    size_t ReservedBytes() const noexcept{return imageLimit_*sizeof(Record);}
    bool Complete() const noexcept {return stage_==Stage::Complete;}
    bool KeysScrubbed() const noexcept {
        if(stage_==Stage::First || stage_==Stage::Second)return false;
        if(records_)for(size_t i=0;i<imageLimit_;++i)
            if(records_[i].imageKey || records_[i].assemblyKey)return false;
        return true;
    }
    bool Prepare(size_t maximumImages,uint64_t slotBudget) noexcept {
        if(stage_!=Stage::New)return Fail(Error::WrongStage);
        if(!maximumImages || maximumImages>kMaximumImages || !slotBudget)
            return Fail(Error::InvalidPrepare);
        records_.reset(new(std::nothrow) Record[maximumImages]());
        if(!records_)return Fail(Error::AllocationFailed);
        imageLimit_=maximumImages;slotBudget_=slotBudget;
        stage_=Stage::First;return true;
    }
    // These methods intentionally require caller-provided scalar observations.
    // They never dereference the opaque keys or invoke Class::From*/TypeInfo.
    bool ObserveFirst(const ImageFact& image) noexcept {
        if(stage_!=Stage::First)return Fail(Error::WrongStage);
        if(!Valid(image))return Fail(Error::InvalidImage);
        if(first_==imageLimit_)return Fail(Error::ImageCapacity);
        const uint64_t count=static_cast<uint64_t>(image.typeCount);
        if(total_>std::numeric_limits<uint64_t>::max()-count ||
           count>slotBudget_-total_)
            return Fail(Error::SlotBudget);
        Record& record=records_[first_++];
        record.imageKey=image.imageKey;record.assemblyKey=image.assemblyKey;
        record.assemblyToken=image.assemblyToken;
        record.imageToken=image.imageToken;
        record.typeCount=image.typeCount;
        record.interpreter=image.interpreter;
        total_+=count;
        if(image.typeCount==0)++zero_;
        if(image.typeCount>maximumImageTypes_)maximumImageTypes_=image.typeCount;
        if(image.typeCount>kExistingB2PerImageTypeLimit)perImageCapExceeded_=true;
        if(image.interpreter){++interpreter_;interpreterSlots_+=count;}
        else{++aot_;aotSlots_+=count;}
        return true;
    }
    bool BeginSecond() noexcept {
        if(stage_!=Stage::First)return Fail(Error::WrongStage);
        if(!first_)return Fail(Error::EmptySource);
        stage_=Stage::Second;return true;
    }
    bool ObserveSecond(const ImageFact& image) noexcept {
        if(stage_!=Stage::Second)return Fail(Error::WrongStage);
        if(!Valid(image))return Fail(Error::InvalidImage);
        if(second_>=first_ || !records_[second_].Matches(image))
            return Fail(Error::SourceChanged);
        ++second_;return true;
    }
    // Must execute before leaving independently owned Reader/metadata/assembly
    // protection: borrowed pointer-value identities are discarded here.
    bool SealWithinSourceScope() noexcept {
        if(stage_!=Stage::Second)return Fail(Error::WrongStage);
        if(second_!=first_)return Fail(Error::MissingSecondPass);
        ScrubKeys();stage_=Stage::Complete;return true;
    }
    void MarkUncovered() noexcept {
        if(stage_==Stage::First || stage_==Stage::Second ||
           stage_==Stage::Complete)Fail(Error::UncoveredSource);
    }
    Receipt Snapshot() const noexcept {
        Receipt r{};
        r.error=firstError_;
        r.complete=stage_==Stage::Complete && KeysScrubbed();
        r.firstPassImages=first_;r.secondPassImages=second_;
        r.zeroTypeImages=zero_;r.interpreterImages=interpreter_;
        r.aotImages=aot_;r.firstPassSlotOccurrences=total_;
        r.interpreterSlotOccurrences=interpreterSlots_;
        r.aotSlotOccurrences=aotSlots_;
        r.maximumImageTypeCount=maximumImageTypes_;
        r.currentB2PerImageLimitExceeded=perImageCapExceeded_;
        // NOT evidence of an actual >128/1024 distinct TypeDef population:
        // these flags say only that enough physical *slots* are available.
        r.currentB2Combined128PotentiallyExceeded=total_>kExistingB2CombinedDistinctLimit;
        r.prototype1024PotentiallyExceeded=total_>kCandidateStorageDistinctLimit;
        if(r.complete){
            r.reportedUpperBoundForSuppliedInventory=true;
            r.possibleDistinctFirstOwnerHandlesUpperBound=total_;
        }
        return r;
    }
    void Release() noexcept {
        ScrubKeys();records_.reset();
        imageLimit_=first_=second_=zero_=aot_=interpreter_=0;
        slotBudget_=total_=aotSlots_=interpreterSlots_=0;
        maximumImageTypes_=0;perImageCapExceeded_=false;
        firstError_=Error::None;stage_=Stage::New;
    }
};
} // namespace r03_b2_physical_slot_upper_bound
