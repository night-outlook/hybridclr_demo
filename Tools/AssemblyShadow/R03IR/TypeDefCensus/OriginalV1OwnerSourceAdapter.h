#pragma once
// R03 B2 SOURCE-HOST ONLY. Synthetic physical V1 image inventory adapter.
// No Unity VM calls, production source registration, or source provenance.
// The caller MUST borrow images only under the actual metadata lifetime Reader
// and g_MetadataLock if this design is ever adapted to the real VM.
// Input handles and image/token primitives are untrusted host observations.
// The original-V1 owner is the FIRST token-valid physical image in order that
// contains a TypeDef handle. Do not replace this with AOT-only membership.
// Add() performs no allocation, IO, string formatting or pointer retention.
#include "BoundedNativeCensusProducer.h"
#include <cstddef>
#include <cstdint>

namespace r03_b2_original_v1_source_adapter {
namespace census=r03_b2_typedef_native_census;

// One test-owned image slot in ORIGINAL token-valid CopyValidAssemblies order.
// Real production code MUST independently prove these fields and lifetimes.
struct ImageView {
    const uintptr_t* typeHandles=nullptr; // indexed TypeDef keys, never dereferenced
    uint32_t typeCount=0;
    uint32_t imageToken=0,assemblyToken=0;
    ImageView(const uintptr_t* handles=nullptr,uint32_t count=0,
              uint32_t token=0,uint32_t assembly=0) noexcept
        :typeHandles(handles),typeCount(count),imageToken(token),assemblyToken(assembly) {}
};

enum class Error : uint8_t {
    None, BadSetup, WrongStage, InvalidImage, MissingHandle,
    FirstOwnerMismatch, LookupBudget, ProducerRejected, UncoveredSource
};

class Adapter final {
    enum class Stage:uint8_t {New,Collecting,Closed,Failed};
    census::Producer* producer_=nullptr; // non-owning; must outlive this adapter
    Stage stage_=Stage::New;
    Error first_=Error::None;
    uint32_t originalImages_=0;
    size_t lookups_=0,maxLookups_=0,accepted_=0;

    bool Fail(Error error) noexcept {
        if(first_==Error::None)first_=error;
        stage_=Stage::Failed;
        if(producer_)producer_->MarkUncovered(); // never mark any such trace complete
        return false;
    }
public:
    Adapter() noexcept=default;
    Adapter(const Adapter&)=delete;
    Adapter& operator=(const Adapter&)=delete;
    Error FirstError() const noexcept{return first_;}
    size_t IndexedLookups() const noexcept{return lookups_;}
    size_t AcceptedUseEvents() const noexcept{return accepted_;}
    uint32_t OriginalImageCount() const noexcept{return originalImages_;}
    bool Open(census::Producer& producer,uint32_t originalImageCount,
              size_t lookupBudget) noexcept {
        if(stage_!=Stage::New)return Fail(Error::WrongStage);
        producer_=&producer; // Even a rejected Open must revoke producer completion.
        // These are test-only budgets; the existing native limit is 65,536.
        if(!originalImageCount || originalImageCount>1024u ||
           !lookupBudget || lookupBudget>1000000u)return Fail(Error::BadSetup);
        producer_=&producer;originalImages_=originalImageCount;
        maxLookups_=lookupBudget;stage_=Stage::Collecting;return true;
    }
    bool AddUse(const ImageView* images,size_t imageCount,
                const census::Observation& observation) noexcept {
        if(stage_!=Stage::Collecting)return Fail(Error::WrongStage);
        if(!images || imageCount!=originalImages_ || !observation.handle ||
           observation.ownerImageOrdinal>=imageCount ||
           observation.firstOwnerImageOrdinal>=imageCount)
            return Fail(Error::InvalidImage);
        // Fail closed on malformed images even when a handle would first
        // match an earlier slot. A future VM adapter must use a fully
        // authenticated ordered physical V1 image inventory.
        for(size_t i=0;i<imageCount;++i) {
            const ImageView& image=images[i];
            if(!image.imageToken || !image.assemblyToken ||
               image.typeCount>8192u ||
               (image.typeCount && !image.typeHandles))
                return Fail(Error::InvalidImage);
        }
        // Identity-first indexed lookup, like original field15's first-emplace
        // mapping. The actual image source MUST come from the independent
        // original-V1 token-valid physical assembly enumerator; this mock
        // array does NOT establish that provenance.
        size_t first=imageCount;
        for(size_t imageIndex=0;imageIndex<imageCount;++imageIndex) {
            const ImageView& image=images[imageIndex];
            for(size_t i=0;i<image.typeCount;++i) {
                if(lookups_==maxLookups_)return Fail(Error::LookupBudget);
                ++lookups_;
                if(image.typeHandles[i]==observation.handle){
                    first=imageIndex;break;
                }
            }
            if(first!=imageCount)break;
        }
        if(first==imageCount)return Fail(Error::MissingHandle);
        if(first!=observation.ownerImageOrdinal ||
           first!=observation.firstOwnerImageOrdinal)
            return Fail(Error::FirstOwnerMismatch);
        if(!producer_ ||
           !producer_->Add(observation,originalImages_))
            return Fail(Error::ProducerRejected);
        ++accepted_;
        return true;
    }
    // Any unvisited/unrecognized type path is a lower bound, not completeness.
    void MarkUncovered() noexcept {
        if(stage_==Stage::Collecting || stage_==Stage::Closed)
            Fail(Error::UncoveredSource);
    }
    // Invoke only AFTER original source protection exits. This is a caller
    // contract; the test-only Adapter does not possess a VM lock/Reader.
    bool CloseAfterSource() noexcept {
        if(stage_!=Stage::Collecting)return false;
        if(!producer_ || !producer_->EndCapture())
            return Fail(Error::ProducerRejected);
        stage_=Stage::Closed;return true;
    }
    void Reset() noexcept {
        // Abandoning an active capture is never evidence of completeness.
        // A closed capture may be reset after the caller has finished using
        // its output; neither Reset nor this adapter can revoke a copied file.
        if(stage_==Stage::Collecting)Fail(Error::UncoveredSource);
        producer_=nullptr;stage_=Stage::New;first_=Error::None;
        originalImages_=0;lookups_=maxLookups_=accepted_=0;
    }
};
} // namespace r03_b2_original_v1_source_adapter
