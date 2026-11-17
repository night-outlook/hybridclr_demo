// R03 B2 TEST ONLY. Includes the pinned original-V1 physical image scanner.
// Never add this C++ driver to a Unity/il2cpp native compilation source roster.
#include "PhysicalTypeDefSlotUpperBound.h"
#include "vm/AssemblyShadowOriginalV1ImageScan.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>

namespace slots=r03_b2_physical_slot_upper_bound;
namespace scanner=il2cpp::vm::assembly_shadow_original_v1_image_scan;
static unsigned cases=0,checks=0;
static void Require(bool ok,const char* expression,int line) {
    ++checks;
    if(!ok){std::fprintf(stderr,"FAIL line=%d: %s\n",line,expression);std::abort();}
}
#define CHECK(v) Require(bool(v),#v,__LINE__)

struct MockAssembly;
struct MockImage {
    MockAssembly* assembly=nullptr;
    uint32_t token=0,typeCount=0;
    bool interpreter=false;
};
struct MockAssemblyName {const char* name=nullptr;};
struct MockAssembly {
    uint32_t token=0;
    MockImage* image=nullptr;
    MockAssemblyName aname{};
};

static slots::ImageFact Borrow(const MockImage* image) noexcept {
    slots::ImageFact result{};
    result.imageKey=reinterpret_cast<uintptr_t>(image);
    result.assemblyKey=reinterpret_cast<uintptr_t>(image->assembly);
    result.assemblyToken=image->assembly->token;
    result.imageToken=image->token;
    result.typeCount=image->typeCount;
    result.interpreter=image->interpreter;
    result.ownerBacklinkMatched=image->assembly->image==image;
    return result;
}
template<size_t N>
static bool Visit(slots::Census& c,
                  const std::array<MockAssembly*,N>& assemblies,
                  bool secondPass) noexcept {
    const bool ok=scanner::Scan(assemblies.begin(),assemblies.end(),
       [&](const MockImage* image) noexcept -> bool {
           const slots::ImageFact facts=Borrow(image);
           return secondPass?c.ObserveSecond(facts):c.ObserveFirst(facts);
       });
    if(!ok)c.MarkUncovered();
    return ok;
}
struct Sample final {
    MockImage img[4]{};
    MockAssembly assembly[4]{};
    std::array<MockAssembly*,4> order{};
    Sample() noexcept {
        const uint32_t tokens[]={11,12,13,0};
        const uint32_t imageTokens[]={0,99,42,77};
        const uint32_t typeCounts[]={120,0,9000,100000};
        for(size_t i=0;i<4;++i){
            img[i].assembly=&assembly[i];
            img[i].token=imageTokens[i];
            img[i].typeCount=typeCounts[i];
            img[i].interpreter=(i==1 || i==2);
            assembly[i].token=tokens[i];
            assembly[i].image=&img[i];
            assembly[i].aname.name="synthetic";
            order[i]=&assembly[i];
        }
    }
};
static slots::Receipt FullSample(slots::Census& c,Sample& s) {
    CHECK(c.Prepare(4,10000000));
    CHECK(Visit(c,s.order,false));
    CHECK(c.BeginSecond());
    CHECK(Visit(c,s.order,true));
    CHECK(c.SealWithinSourceScope());
    CHECK(c.KeysScrubbed());
    return c.Snapshot();
}
static void CompleteInventoryAndNoExactDistinctClaim() {
    ++cases;Sample s;slots::Census c;
    const slots::Receipt r=FullSample(c,s);
    CHECK(r.complete && r.syntheticOnly && r.error==slots::Error::None);
    CHECK(r.firstPassImages==3 && r.secondPassImages==3);
    CHECK(r.zeroTypeImages==1 && r.interpreterImages==2 && r.aotImages==1);
    CHECK(r.aotSlotOccurrences==120 && r.interpreterSlotOccurrences==9000);
    CHECK(r.firstPassSlotOccurrences==9120);
    CHECK(r.possibleDistinctFirstOwnerHandlesUpperBound==9120);
    CHECK(r.reportedUpperBoundForSuppliedInventory);
    CHECK(r.currentB2PerImageLimitExceeded);
    CHECK(r.currentB2Combined128PotentiallyExceeded);
    CHECK(r.prototype1024PotentiallyExceeded);
    CHECK(!r.sourceOriginAuthenticated && !r.originalPhysicalEnumerationProven &&
          !r.coherentVmEpochProven && !r.realUnity && !r.nativeIntegrated &&
          !r.R03Accepted && !r.ReadyForHumanReviewGate &&
          !r.capacityDecisionAuthorized);
}
static void OnePassIsNeverComplete() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,s.order,false));
    CHECK(!c.KeysScrubbed());
    slots::Receipt before=c.Snapshot();
    CHECK(!before.complete && !before.reportedUpperBoundForSuppliedInventory);
    CHECK(before.possibleDistinctFirstOwnerHandlesUpperBound==0);
    CHECK(!c.SealWithinSourceScope());
    CHECK(c.FirstError()==slots::Error::WrongStage);
    CHECK(c.KeysScrubbed());
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
}
static void MissingSecondImageFails() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,s.order,false));
    CHECK(c.BeginSecond());
    CHECK(c.ObserveSecond(Borrow(&s.img[0])));
    CHECK(c.ObserveSecond(Borrow(&s.img[1])));
    CHECK(!c.SealWithinSourceScope());
    CHECK(c.FirstError()==slots::Error::MissingSecondPass);
    CHECK(!c.Complete() && c.KeysScrubbed());
    CHECK(c.Snapshot().secondPassImages==2);
}
static void DifferentTypeCountFails() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,s.order,false));
    CHECK(c.BeginSecond());
    s.img[0].typeCount++;
    CHECK(!Visit(c,s.order,true));
    CHECK(c.FirstError()==slots::Error::SourceChanged);
    CHECK(c.KeysScrubbed());
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
}
static void ChangedOrderAndInterpreterFlagFail() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,s.order,false));
    CHECK(c.BeginSecond());
    const auto t=s.order[0];s.order[0]=s.order[1];s.order[1]=t;
    CHECK(!Visit(c,s.order,true));
    CHECK(c.FirstError()==slots::Error::SourceChanged);
    c.Release();Sample fresh;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,fresh.order,false));
    CHECK(c.BeginSecond());fresh.img[1].interpreter=false;
    CHECK(!Visit(c,fresh.order,true));
    CHECK(c.FirstError()==slots::Error::SourceChanged);
}
static void ChangedImageAndAssemblyIdentitiesFail() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,s.order,false));
    CHECK(c.BeginSecond());s.img[0].token=71;
    CHECK(!Visit(c,s.order,true));
    CHECK(c.FirstError()==slots::Error::SourceChanged);
    c.Release();Sample other;
    CHECK(c.Prepare(4,20000));CHECK(Visit(c,other.order,false));
    CHECK(c.BeginSecond());other.assembly[0].token=77;
    CHECK(!Visit(c,other.order,true));
    CHECK(c.FirstError()==slots::Error::SourceChanged);
}
static void InvalidImageParentAndNamesFailClosed() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));
    s.assembly[1].image=&s.img[0];
    CHECK(!Visit(c,s.order,false));
    CHECK(c.FirstError()==slots::Error::UncoveredSource);
    CHECK(!c.Complete() && c.KeysScrubbed());
    c.Release();Sample missingName;
    CHECK(c.Prepare(4,20000));
    missingName.assembly[1].aname.name=nullptr;
    CHECK(!Visit(c,missingName.order,false));
    CHECK(c.FirstError()==slots::Error::UncoveredSource);
}
static void InvalidDirectImageCannotBecomePositive() {
    ++cases;slots::Census c;CHECK(c.Prepare(2,100));
    slots::ImageFact invalid{};
    invalid.imageKey=9;invalid.assemblyKey=10;invalid.typeCount=10;
    invalid.ownerBacklinkMatched=true; // assemblyToken remains zero
    CHECK(!c.ObserveFirst(invalid));
    CHECK(c.FirstError()==slots::Error::InvalidImage);
    CHECK(c.KeysScrubbed());
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
}
static void OverImageCapacityIsIncomplete() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(2,20000));CHECK(!Visit(c,s.order,false));
    CHECK(c.FirstError()==slots::Error::ImageCapacity);
    const slots::Receipt r=c.Snapshot();
    CHECK(!r.complete && r.firstPassImages==2);
    CHECK(r.firstPassSlotOccurrences==120);
    CHECK(r.possibleDistinctFirstOwnerHandlesUpperBound==0);
    CHECK(c.KeysScrubbed());
}
static void BudgetRejectsBeforeOverflow() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,200));
    CHECK(!Visit(c,s.order,false));
    CHECK(c.FirstError()==slots::Error::SlotBudget);
    CHECK(c.Snapshot().firstPassImages==2);
    CHECK(c.Snapshot().firstPassSlotOccurrences==120);
    CHECK(!c.Complete() && c.KeysScrubbed());
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
}
static void NoTokenValidImagesIsIncomplete() {
    ++cases;Sample s;slots::Census c;
    for(size_t i=0;i<4;++i)s.assembly[i].token=0;
    CHECK(c.Prepare(4,1000));CHECK(Visit(c,s.order,false));
    CHECK(!c.BeginSecond());
    CHECK(c.FirstError()==slots::Error::EmptySource);
    CHECK(c.KeysScrubbed());
}
static void LateUncoveredRevokesCompletion() {
    ++cases;Sample s;slots::Census c;
    CHECK(FullSample(c,s).complete);
    c.MarkUncovered();
    CHECK(!c.Complete());
    CHECK(c.FirstError()==slots::Error::UncoveredSource);
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
    CHECK(c.KeysScrubbed());
}
static void ReprepareOnlyAfterRelease() {
    ++cases;Sample s;slots::Census c;
    CHECK(c.Prepare(4,20000));
    CHECK(!c.Prepare(4,20000));
    CHECK(c.FirstError()==slots::Error::WrongStage);
    c.Release();CHECK(c.FirstError()==slots::Error::None);
    CHECK(FullSample(c,s).complete);
    CHECK(!c.BeginSecond());
    CHECK(c.FirstError()==slots::Error::WrongStage);
    CHECK(c.KeysScrubbed());
    c.Release();CHECK(c.Prepare(4,20000));
}
static void BadPrepareNeverAllocates() {
    ++cases;slots::Census c;
    CHECK(!c.Prepare(0,10));
    CHECK(c.FirstError()==slots::Error::InvalidPrepare);
    CHECK(c.ReservedBytes()==0 && c.KeysScrubbed());
    c.Release();CHECK(!c.Prepare(1025,10));
    CHECK(c.FirstError()==slots::Error::InvalidPrepare);
    c.Release();CHECK(!c.Prepare(1,0));
    CHECK(c.FirstError()==slots::Error::InvalidPrepare);
}
static void OneHugeImageStillCountsWithoutTypeKeyCreation() {
    ++cases;Sample s;slots::Census c;
    s.img[0].typeCount=UINT32_MAX;
    s.assembly[1].token=0;s.assembly[2].token=0;
    CHECK(c.Prepare(2,UINT64_MAX));
    CHECK(Visit(c,s.order,false));CHECK(c.BeginSecond());
    CHECK(Visit(c,s.order,true));CHECK(c.SealWithinSourceScope());
    const slots::Receipt r=c.Snapshot();
    CHECK(r.complete && r.firstPassImages==1);
    CHECK(r.firstPassSlotOccurrences==UINT32_MAX);
    CHECK(r.currentB2PerImageLimitExceeded);
    CHECK(r.maximumImageTypeCount==UINT32_MAX);
    CHECK(!r.sourceOriginAuthenticated && !r.nativeIntegrated);
}
static void NoSourcePointersAfterRelease() {
    ++cases;Sample s;slots::Census c;
    CHECK(FullSample(c,s).complete);
    CHECK(c.ReservedBytes()>0);
    c.Release();
    CHECK(c.ReservedBytes()==0 && c.KeysScrubbed());
    CHECK(c.Snapshot().firstPassImages==0);
}
static void Maximum1024ImagesAnd1025thIncomplete() {
    ++cases;
    std::array<MockImage,1025> images{};
    std::array<MockAssembly,1025> assemblies{};
    std::array<MockAssembly*,1025> order{};
    for(size_t i=0;i<1025;++i) {
        images[i].assembly=&assemblies[i];
        images[i].token=static_cast<uint32_t>(i);
        images[i].typeCount=1;
        assemblies[i].token=static_cast<uint32_t>(i+1);
        assemblies[i].image=&images[i];
        assemblies[i].aname.name="physical";
        order[i]=&assemblies[i];
    }
    slots::Census c;
    CHECK(c.Prepare(1024,1025));
    // A source containing 1025 token-valid images may not be truncated.
    CHECK(!Visit(c,order,false));
    CHECK(c.FirstError()==slots::Error::ImageCapacity);
    CHECK(c.Snapshot().firstPassSlotOccurrences==1024);
    CHECK(!c.Snapshot().reportedUpperBoundForSuppliedInventory);
    CHECK(c.KeysScrubbed());
    c.Release();
    std::array<MockAssembly*,1024> first1024{};
    for(size_t i=0;i<1024;++i)first1024[i]=order[i];
    CHECK(c.Prepare(1024,1025));
    CHECK(Visit(c,first1024,false));
    CHECK(c.BeginSecond());
    CHECK(Visit(c,first1024,true));
    CHECK(c.SealWithinSourceScope());
    CHECK(c.Snapshot().complete);
    CHECK(c.Snapshot().possibleDistinctFirstOwnerHandlesUpperBound==1024);
    CHECK(c.KeysScrubbed());
}
static void EmitFixture(bool bad) {
    Sample s;slots::Census c;
    CHECK(c.Prepare(4,10000000));
    CHECK(Visit(c,s.order,false));CHECK(c.BeginSecond());
    if(bad){s.img[2].typeCount+=1;CHECK(!Visit(c,s.order,true));}
    else{CHECK(Visit(c,s.order,true));CHECK(c.SealWithinSourceScope());}
    const slots::Receipt r=c.Snapshot();
    CHECK(c.KeysScrubbed());
    std::printf("{\"kind\":\"R03B2PhysicalSlotCensusFixture\",\"result\":\"SyntheticOnly\",\"complete\":%s,\"observedPhysicalImages\":%zu,\"zeroImages\":%zu,\"aotSlots\":%llu,\"interpreterSlots\":%llu,\"firstPassSlotOccurrences\":%llu,\"upperBoundForSuppliedInventory\":%llu,\"sourceOriginAuthenticated\":false,\"coherentVmEpochProven\":false,\"realUnity\":false,\"nativeIntegrated\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false,\"capacityDecisionAuthorized\":false}\n",
      r.complete?"true":"false",r.firstPassImages,r.zeroTypeImages,
      static_cast<unsigned long long>(r.aotSlotOccurrences),
      static_cast<unsigned long long>(r.interpreterSlotOccurrences),
      static_cast<unsigned long long>(r.firstPassSlotOccurrences),
      static_cast<unsigned long long>(r.possibleDistinctFirstOwnerHandlesUpperBound));
}
int main(int argc,char** argv) {
    if(argc==2 && std::strcmp(argv[1],"--fixture")==0){EmitFixture(false);return 0;}
    if(argc==2 && std::strcmp(argv[1],"--incomplete-fixture")==0){EmitFixture(true);return 0;}
    CompleteInventoryAndNoExactDistinctClaim();
    OnePassIsNeverComplete();MissingSecondImageFails();
    DifferentTypeCountFails();ChangedOrderAndInterpreterFlagFail();
    ChangedImageAndAssemblyIdentitiesFail();
    InvalidImageParentAndNamesFailClosed();InvalidDirectImageCannotBecomePositive();
    OverImageCapacityIsIncomplete();BudgetRejectsBeforeOverflow();
    NoTokenValidImagesIsIncomplete();LateUncoveredRevokesCompletion();
    ReprepareOnlyAfterRelease();BadPrepareNeverAllocates();
    OneHugeImageStillCountsWithoutTypeKeyCreation();NoSourcePointersAfterRelease();
    Maximum1024ImagesAnd1025thIncomplete();
    std::printf("{\"kind\":\"R03B2PhysicalTypeDefSlotUpperBoundHost\",\"result\":\"PassedSyntheticOnly\",\"cases\":%u,\"checks\":%u,\"realUnity\":false,\"nativeIntegrated\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",cases,checks);
    return 0;
}
