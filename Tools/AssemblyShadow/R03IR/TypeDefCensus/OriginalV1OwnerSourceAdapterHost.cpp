// R03 B2 TEST-ONLY original-V1 metadata source adapter contract. NOT IL2CPP.
#include "OriginalV1OwnerSourceAdapter.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
namespace s=r03_b2_original_v1_source_adapter;
namespace c=r03_b2_typedef_native_census;
static size_t checks=0,cases=0;
static void Require(bool value,const char* expression,int line) {
    ++checks;
    if(!value){std::fprintf(stderr,"FAIL %d %s\n",line,expression);std::abort();}
}
#define CHECK(expr) Require(bool(expr),#expr,__LINE__)
static c::Observation Use(uintptr_t handle,uint32_t owner,
                           c::Role role=c::Role::Root) {
    c::Observation o{};o.handle=handle;o.ownerImageOrdinal=owner;
    o.firstOwnerImageOrdinal=owner;o.role=role;
    o.namespaceBytes=4;o.simpleNameBytes=4;
    return o;
}
static c::SourceStamp Stamp(uint32_t count,uint32_t classes=1) {
    c::SourceStamp st{};
    st.nativeCommit="cecf4b859d50b128e5c0fc6c90cd89e3a452b96a";
    st.demoCommit="d5898ec2163050eb7b079597dad1addf4ad1ff3f";
    st.originalV1ImageCount=count;st.observedClasses=classes;
    st.metadataReaderEpoch=1;st.metadataLockHeldDuringAdd=true;
    st.classPasses=3;st.originalV1ImagePasses=2;
    return st;
}
static void OriginalOrderAndRoleOverlap() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(8,16));CHECK(a.Open(p,3,40));
    const uintptr_t tokenValidPhysical0[]={10,20,30};
    const uintptr_t tokenValidPhysical1[]={20,40}; // duplicate: first owner is 0
    const uintptr_t tokenValidPhysical2[]={50,60};
    const s::ImageView images[]={
        {tokenValidPhysical0,3,1,1},{tokenValidPhysical1,2,2,2},
        {tokenValidPhysical2,2,3,3}};
    CHECK(a.AddUse(images,3,Use(20,0)));
    CHECK(a.AddUse(images,3,Use(20,0,c::Role::NonRoot)));
    CHECK(a.AddUse(images,3,Use(40,1,c::Role::NonRoot)));
    CHECK(a.AddUse(images,3,Use(60,2,c::Role::NonRoot)));
    CHECK(p.DistinctHandles()==3 && a.AcceptedUseEvents()==4);
    CHECK(a.IndexedLookups()==16u); // 2+2+5+7 indexed reads
    CHECK(a.CloseAfterSource() && p.RawHandlesScrubbed());
    std::string json;CHECK(p.EmitJson(Stamp(3),json));
    CHECK(json.find("\"complete\":true")!=std::string::npos);
    CHECK(json.find("\"handleId\":1")!=std::string::npos);
    CHECK(json.find("\"role\":\"nonroot\"")!=std::string::npos);
    CHECK(json.find("\"handle\":") == std::string::npos);
    CHECK(!p.EmitJson(Stamp(2),json));
}
static void FirstOwnerWinsOverLaterDuplicate() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(2,4));CHECK(a.Open(p,2,50));
    const uintptr_t one[]={111},two[]={111,222};
    const s::ImageView images[]={{one,1,1,1},{two,2,2,2}};
    CHECK(!a.AddUse(images,2,Use(111,1)));
    CHECK(a.FirstError()==s::Error::FirstOwnerMismatch);
    CHECK(p.FirstError()==c::Error::MissingCoverage);
    CHECK(p.RawHandlesScrubbed());
    std::string json;CHECK(p.EmitJson(Stamp(2),json));
    CHECK(json.find("\"complete\":false")!=std::string::npos);
    CHECK(json.find("\"declaredEvents\":0")!=std::string::npos);
}
static void MissingAndBudgetAreIncomplete() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(2,4));CHECK(a.Open(p,1,2));
    const uintptr_t handles[]={1,2,3,4};
    const s::ImageView images[]={{handles,4,1,1}};
    CHECK(!a.AddUse(images,1,Use(3,0)));
    CHECK(a.FirstError()==s::Error::LookupBudget && a.IndexedLookups()==2);
    CHECK(p.RawHandlesScrubbed());
    p.Release();a.Reset();
    CHECK(p.Prepare(2,4));CHECK(a.Open(p,1,20));
    CHECK(!a.AddUse(images,1,Use(777,0)));
    CHECK(a.FirstError()==s::Error::MissingHandle);
    CHECK(p.RawHandlesScrubbed());
}
static void BadImageAndWrongStage() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(2,4));CHECK(!a.Open(p,0,30));
    CHECK(a.FirstError()==s::Error::BadSetup);
    p.Release();a.Reset();
    CHECK(p.Prepare(2,4));CHECK(a.Open(p,1,30));
    const uintptr_t handles[]={10,20};
    const s::ImageView missing[]={ {nullptr,2,1,1} };
    CHECK(!a.AddUse(missing,1,Use(10,0)));
    CHECK(a.FirstError()==s::Error::InvalidImage);
    CHECK(p.RawHandlesScrubbed());
    a.Reset();p.Release();
    CHECK(p.Prepare(2,4));CHECK(a.Open(p,1,30));
    const s::ImageView valid[]={ {handles,2,1,1} };
    CHECK(!a.AddUse(valid,2,Use(10,0)));
    CHECK(a.FirstError()==s::Error::InvalidImage);
}
static void UnsupportedPathAndLateMissingCoverage() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(3,8));CHECK(a.Open(p,1,40));
    const uintptr_t handles[]={10,11};
    const s::ImageView images[]={{handles,2,1,1}};
    CHECK(a.AddUse(images,1,Use(10,0)));
    a.MarkUncovered();
    CHECK(a.FirstError()==s::Error::UncoveredSource);
    CHECK(!a.CloseAfterSource() && p.RawHandlesScrubbed());
    std::string json;CHECK(p.EmitJson(Stamp(1),json));
    CHECK(json.find("\"complete\":false")!=std::string::npos);
    a.Reset();p.Release();
    CHECK(p.Prepare(3,8));CHECK(a.Open(p,1,40));
    CHECK(a.AddUse(images,1,Use(10,0)));
    CHECK(a.CloseAfterSource());
    a.MarkUncovered();
    CHECK(a.FirstError()==s::Error::UncoveredSource && !p.Complete());
    CHECK(p.EmitJson(Stamp(1),json));
    CHECK(json.find("\"complete\":false")!=std::string::npos);
}
static void EventProducerOverflowRetainsLowerBound() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(1,1));CHECK(a.Open(p,1,30));
    const uintptr_t handles[]={10};
    const s::ImageView images[]={{handles,1,1,1}};
    CHECK(a.AddUse(images,1,Use(10,0)));
    CHECK(!a.AddUse(images,1,Use(10,0,c::Role::NonRoot)));
    CHECK(a.FirstError()==s::Error::ProducerRejected);
    CHECK(p.FirstError()==c::Error::EventLimit);
    CHECK(p.RawHandlesScrubbed());
    std::string json;CHECK(p.EmitJson(Stamp(1),json));
    CHECK(json.find("\"declaredEvents\":1")!=std::string::npos);
    CHECK(json.find("\"complete\":false")!=std::string::npos);
}
static void InvalidTailAndEmptyPhysicalImage() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(3,3));CHECK(a.Open(p,3,40));
    const uintptr_t first[]={10,11};
    const s::ImageView images[]={{nullptr,0,1,1},
                                 {first,2,2,2},
                                 {nullptr,1,3,3}};
    CHECK(!a.AddUse(images,3,Use(10,1))); // malformed *later* slot
    CHECK(a.FirstError()==s::Error::InvalidImage && p.RawHandlesScrubbed());
    a.Reset();p.Release();
    CHECK(p.Prepare(3,3));CHECK(a.Open(p,3,40));
    const s::ImageView good[]={{nullptr,0,1,1},{first,2,2,2},
                               {nullptr,0,3,3}};
    CHECK(a.AddUse(good,3,Use(10,1)));
    CHECK(a.IndexedLookups()==1);
    CHECK(a.CloseAfterSource());
    std::string json;CHECK(p.EmitJson(Stamp(3),json));
    CHECK(json.find("\"ownerImageOrdinal\":1")!=std::string::npos);
}
static void FailedOpenAndAbandonedCapture() {
    ++cases;c::Producer p;s::Adapter a;
    CHECK(p.Prepare(2,2));
    CHECK(!a.Open(p,0,10)); // failed Open revokes producer, too
    CHECK(p.FirstError()==c::Error::MissingCoverage);
    CHECK(!p.EndCapture() && p.RawHandlesScrubbed());
    a.Reset();p.Release();
    CHECK(p.Prepare(2,2));CHECK(a.Open(p,1,20));
    const uintptr_t one[]={1};
    const s::ImageView images[]={{one,1,1,1}};
    CHECK(a.AddUse(images,1,Use(1,0)));
    a.Reset(); // discarding an open adapter cannot promote a healthy trace
    CHECK(p.FirstError()==c::Error::MissingCoverage);
    CHECK(!p.EndCapture() && p.RawHandlesScrubbed());
    std::string json;CHECK(p.EmitJson(Stamp(1),json));
    CHECK(json.find("\"complete\":false")!=std::string::npos);
}
static void Fixture(bool incomplete) {
    c::Producer p;s::Adapter a;
    CHECK(p.Prepare(4,8));CHECK(a.Open(p,2,40));
    const uintptr_t first[]={10,20};
    const uintptr_t second[]={10,30}; // duplicate 10, first owner = 0
    const s::ImageView images[]={{first,2,1,1},{second,2,2,2}};
    CHECK(a.AddUse(images,2,Use(10,0)));
    CHECK(a.AddUse(images,2,Use(10,0,c::Role::NonRoot)));
    CHECK(a.AddUse(images,2,Use(30,1,c::Role::NonRoot)));
    if(incomplete)a.MarkUncovered();
    else CHECK(a.CloseAfterSource());
    std::string json;CHECK(p.EmitJson(Stamp(2,2),json));
    std::fwrite(json.data(),1,json.size(),stdout);
}
int main(int argc,char** argv) {
    if(argc==2 && std::strcmp(argv[1],"--fixture")==0) {
        Fixture(false);return 0;
    }
    if(argc==2 && std::strcmp(argv[1],"--incomplete-fixture")==0) {
        Fixture(true);return 0;
    }
    if(argc>1){std::fprintf(stderr,"unexpected arguments: %s\n",argv[1]);return 2;}
    OriginalOrderAndRoleOverlap();FirstOwnerWinsOverLaterDuplicate();
    MissingAndBudgetAreIncomplete();BadImageAndWrongStage();
    UnsupportedPathAndLateMissingCoverage();EventProducerOverflowRetainsLowerBound();
    InvalidTailAndEmptyPhysicalImage();FailedOpenAndAbandonedCapture();
    std::printf("{\"kind\":\"R03B2OriginalV1OwnerSourceAdapterHost\",\"status\":\"PassedSyntheticOnly\",\"cases\":%zu,\"checks\":%zu,\"realUnity\":false,\"integratedNativeB2\":false,\"R03Accepted\":false}\n",cases,checks);
    return 0;
}
