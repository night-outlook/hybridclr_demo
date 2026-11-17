// R03 B2 HOST ONLY. C++11 mechanics against exact pinned native Gate+Scan.
// Never compile this file into Unity, GameAssembly or libil2cpp product.
#include "PhysicalSlotSourceSession.h"
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <thread>

namespace slots=r03_b2_physical_slot_upper_bound;
namespace source=r03_b2_physical_slot_source_session;
namespace gate_ns=il2cpp::vm::assembly_shadow_metadata_lifetime;
static size_t cases=0,checks=0;
static void Require(bool ok,const char* expr,int line) {
    ++checks;
    if(!ok){std::fprintf(stderr,"Source session failure line=%d %s\n",line,expr);std::abort();}
}
#define CHECK(x) Require(bool(x),#x,__LINE__)

struct Image;
struct Assembly {
    uint32_t token=0;
    Image* image=nullptr;
    struct {const char* name=nullptr;} aname;
};
struct Image {
    Assembly* assembly=nullptr;
    uint32_t token=0;
    uint32_t typeCount=0;
};
struct Sample {
    std::array<Assembly,4> assemblies{};
    std::array<Image,4> images{};
    std::array<Assembly*,4> order{};
    Sample() noexcept {
        for(size_t i=0;i<4;++i){
            assemblies[i].token=static_cast<uint32_t>(i+1);
            assemblies[i].image=&images[i];
            assemblies[i].aname.name="physical";
            images[i].assembly=&assemblies[i];
            images[i].token=static_cast<uint32_t>(i==1?100+i:i+1);
            order[i]=&assemblies[i];
        }
        images[0].typeCount=120;
        images[1].typeCount=9000;
        images[2].typeCount=0;
        images[3].typeCount=33;
        assemblies[3].token=0; // original CopyValidAssemblies excludes this
    }
    Sample(const Sample&)=delete;
    Sample& operator=(const Sample&)=delete;
};
struct Extract {
    slots::ImageFact operator()(const Image* image) const noexcept {
        slots::ImageFact f{};
        if(!image)return f;
        f.imageKey=reinterpret_cast<uintptr_t>(image);
        f.assemblyKey=reinterpret_cast<uintptr_t>(image->assembly);
        f.assemblyToken=image->assembly?image->assembly->token:0;
        f.imageToken=image->token;
        f.typeCount=image->typeCount;
        f.interpreter=image->token>=100;
        f.ownerBacklinkMatched=image->assembly && image->assembly->image==image;
        return f;
    }
};
static bool Full(source::SourceSession& s,Sample& sample) {
    if(!s.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}))return false;
    return s.VisitSecondAndSeal(sample.order.begin(),sample.order.end(),Extract{});
}
static void ClosedReaderDoesNotRead() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;
    CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(session.ReaderEpoch()==0);
        CHECK(!session.SourceScopeHeld());
        CHECK(!session.Sealed());
        Sample sample;
        CHECK(!Full(session,sample));
    }
    const auto result=census.Snapshot();
    CHECK(result.error==slots::Error::UncoveredSource);
    CHECK(!result.complete && !result.reportedUpperBoundForSuppliedInventory);
    CHECK(result.firstPassImages==0 && census.KeysScrubbed());
    CHECK(gate.ReaderCount()==0 && gate.Closed());
}
static void HappyInitialEpochAndScrub() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());
    CHECK(census.Prepare(4,100000));
    const size_t before=census.ReservedBytes();
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(session.ReaderEpoch()==1 && session.SourceScopeHeld());
        CHECK(gate.ReaderCount()==1);
        CHECK(Full(session,sample));
        CHECK(session.Sealed());
        CHECK(census.KeysScrubbed());
        CHECK(census.ReservedBytes()==before);
    }
    CHECK(gate.ReaderCount()==0);
    const auto result=census.Snapshot();
    CHECK(result.complete && result.reportedUpperBoundForSuppliedInventory);
    CHECK(result.firstPassImages==3 && result.secondPassImages==3);
    CHECK(result.zeroTypeImages==1 && result.interpreterImages==1 && result.aotImages==2);
    CHECK(result.aotSlotOccurrences==120 && result.interpreterSlotOccurrences==9000);
    CHECK(result.possibleDistinctFirstOwnerHandlesUpperBound==9120);
    CHECK(!result.sourceOriginAuthenticated && !result.originalPhysicalEnumerationProven);
    CHECK(!result.coherentVmEpochProven && !result.nativeIntegrated);
    CHECK(!result.R03Accepted && !result.ReadyForHumanReviewGate);
    gate.CloseAndDrain();
    CHECK(gate.Closed());
}
static void AbandonedSecondPassRevokes() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(session.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}));
        CHECK(gate.ReaderCount()==1);
        // Deliberately leave without matching second pass.
    }
    CHECK(gate.ReaderCount()==0);
    CHECK(census.FirstError()==slots::Error::UncoveredSource);
    CHECK(!census.Complete() && census.KeysScrubbed());
    CHECK(!census.Snapshot().reportedUpperBoundForSuppliedInventory);
    gate.CloseAndDrain();
}
static void SourceDriftInsideAdmittedSession() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(session.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}));
        sample.images[1].typeCount=9001;
        CHECK(!session.VisitSecondAndSeal(sample.order.begin(),sample.order.end(),Extract{}));
        CHECK(!session.Sealed() && census.KeysScrubbed());
    }
    CHECK(gate.ReaderCount()==0);
    CHECK(census.FirstError()==slots::Error::SourceChanged);
    CHECK(census.Snapshot().possibleDistinctFirstOwnerHandlesUpperBound==0);
    gate.CloseAndDrain();
}
static void InvalidPhysicalBacklinkRevokes() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    sample.assemblies[1].image=&sample.images[0];
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(!session.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}));
        CHECK(census.KeysScrubbed());
    }
    CHECK(census.FirstError()==slots::Error::UncoveredSource);
    CHECK(!census.Snapshot().reportedUpperBoundForSuppliedInventory);
    gate.CloseAndDrain();
}
static void ImageCapacityFailureIsNotPositive() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(2,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(!session.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}));
        CHECK(census.KeysScrubbed());
    }
    CHECK(census.FirstError()==slots::Error::ImageCapacity);
    CHECK(census.Snapshot().firstPassImages==2);
    CHECK(census.Snapshot().possibleDistinctFirstOwnerHandlesUpperBound==0);
    gate.CloseAndDrain();
}
static void DuplicatePhysicalRegistrationIsConservative() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    sample.order[3]=&sample.assemblies[0];
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(Full(session,sample));
    }
    const auto r=census.Snapshot();
    CHECK(r.complete && r.firstPassImages==4);
    CHECK(r.firstPassSlotOccurrences==9240);
    CHECK(r.possibleDistinctFirstOwnerHandlesUpperBound==9240);
    // The repeated physical registration can share all 120 TypeDef handles.
    // It is intentionally counted twice in the *upper bound* only.
    CHECK(!r.capacityDecisionAuthorized && !r.sourceOriginAuthenticated);
    gate.CloseAndDrain();
}
static void ZeroEligibleAssembliesIsIncomplete() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    for(auto& a:sample.assemblies)a.token=0;
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(!session.VisitFirst(sample.order.begin(),sample.order.end(),Extract{}));
    }
    CHECK(census.FirstError()==slots::Error::EmptySource);
    CHECK(census.KeysScrubbed());
    gate.CloseAndDrain();
}
static void RepeatedVisitAfterSealRevokes() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(Full(session,sample));
        CHECK(session.Sealed());
        CHECK(!session.VisitSecondAndSeal(sample.order.begin(),sample.order.end(),Extract{}));
        CHECK(!session.Sealed());
    }
    CHECK(census.FirstError()==slots::Error::UncoveredSource);
    CHECK(!census.Snapshot().reportedUpperBoundForSuppliedInventory);
    gate.CloseAndDrain();
}
static void LateMarkUncoveredRevokes() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(Full(session,sample));
        CHECK(session.Sealed());
        session.MarkUncovered();
        CHECK(!session.Sealed() && census.KeysScrubbed());
    }
    CHECK(census.FirstError()==slots::Error::UncoveredSource);
    CHECK(!census.Snapshot().reportedUpperBoundForSuppliedInventory);
    gate.CloseAndDrain();
}
static void ShutdownClosesAndDrainsRealNativeGate() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());CHECK(census.Prepare(4,100000));
    std::atomic<bool> complete{false};
    std::thread shutdown;
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(Full(session,sample) && gate.ReaderCount()==1);
        shutdown=std::thread([&]{gate.CloseAndDrain();complete.store(true,std::memory_order_release);});
        bool closed=false;
        for(int i=0;i<5000;++i) {
            if(gate.Closed()){closed=true;break;}
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        CHECK(closed);
        CHECK(gate.ReaderCount()==1);
        CHECK(!complete.load(std::memory_order_acquire));
        // Shutdown holds closed admission while an existing Reader drains.
        gate_ns::Gate::Reader tooLate(gate);
        CHECK(!tooLate && tooLate.Epoch()==0);
    } // Unlock source mutex and then release Reader.
    shutdown.join();
    CHECK(complete.load(std::memory_order_acquire));
    CHECK(gate.Closed() && gate.ReaderCount()==0);
    CHECK(census.Snapshot().complete && census.KeysScrubbed());
}
static void DefaultInitialEpochCannotEnterReopenedSession() {
    ++cases;gate_ns::Gate gate;std::mutex mutex;slots::Census census;Sample sample;
    CHECK(gate.OpenAfterInit());
    gate.CloseAndDrain();
    CHECK(gate.OpenAfterInit()); // next session is epoch 2
    CHECK(census.Prepare(4,100000));
    {
        source::SourceSession session(census,gate,mutex);
        CHECK(session.ReaderEpoch()==0 && !session.SourceScopeHeld());
        CHECK(!Full(session,sample));
    }
    CHECK(census.FirstError()==slots::Error::UncoveredSource);
    CHECK(!census.Snapshot().reportedUpperBoundForSuppliedInventory);
    {
        gate_ns::Gate::Reader explicitSecond(gate,2);
        CHECK(explicitSecond && explicitSecond.Epoch()==2);
    }
    // Epoch 2 would ALSO require an independently stamped source, unavailable
    // to the actual current P1 class registries. No provenance is claimed.
    gate.CloseAndDrain();
    CHECK(gate.Closed());
}
int main() {
    ClosedReaderDoesNotRead();HappyInitialEpochAndScrub();
    AbandonedSecondPassRevokes();SourceDriftInsideAdmittedSession();
    InvalidPhysicalBacklinkRevokes();ImageCapacityFailureIsNotPositive();
    DuplicatePhysicalRegistrationIsConservative();ZeroEligibleAssembliesIsIncomplete();
    RepeatedVisitAfterSealRevokes();LateMarkUncoveredRevokes();
    ShutdownClosesAndDrainsRealNativeGate();
    DefaultInitialEpochCannotEnterReopenedSession();
    std::printf("{\"kind\":\"R03B2PhysicalSlotSourceSessionHost\",\"result\":\"PassedSyntheticReaderLockScopeOnly\",\"cases\":%zu,\"checks\":%zu,\"realUnity\":false,\"realMetadataLock\":false,\"nativeSourceIntegrated\":false,\"coherentVmEpochProven\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",cases,checks);
    return 0;
}
