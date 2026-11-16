// Test ONLY: never add this host to Unity's native compilation roster.
#include "BoundedNativeCensusProducer.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
namespace c=r03_b2_typedef_native_census;
static size_t cases=0,checks=0;
static void Check(bool good,const char* expr,int line) {
    ++checks;if(!good){std::fprintf(stderr,"FAIL line=%d %s\n",line,expr);std::abort();}
}
#define CHECK(e) Check(bool(e),#e,__LINE__)
static c::Observation E(uintptr_t h,c::Role role=c::Role::Root,uint32_t ns=4,uint32_t name=4) {
    c::Observation e{};e.handle=h;e.role=role;
    e.namespaceBytes=ns;e.simpleNameBytes=name;
    return e;
}
static c::SourceStamp Stamp(uint32_t classes=1) {
    c::SourceStamp stamp{};
    stamp.nativeCommit="cecf4b859d50b128e5c0fc6c90cd89e3a452b96a";
    stamp.demoCommit="48c16102e4956b1980bc013e9491bd596f1a4aed";
    stamp.originalV1ImageCount=2;
    stamp.observedClasses=classes;stamp.metadataReaderEpoch=1;
    stamp.metadataLockHeldDuringAdd=true;stamp.classPasses=3;
    stamp.originalV1ImagePasses=2;
    return stamp;
}
static void RootAndNonroot() {
    ++cases;c::Producer p;CHECK(p.Prepare(300,300));
    const size_t reserved=p.ReservedBytes();
    for(size_t i=0;i<129;++i)CHECK(p.Add(E((i+1)*16u),2));
    CHECK(p.Add(E(16,c::Role::NonRoot),2));
    CHECK(p.DistinctHandles()==129 && p.RecordedEvents()==130);
    CHECK(p.ReservedBytes()==reserved);
    CHECK(p.EndCapture());CHECK(p.RawHandlesScrubbed());
    std::string s;CHECK(p.EmitJson(Stamp(129),s));
    CHECK(s.find("\"handleId\":1")!=std::string::npos);
    CHECK(s.find("\"role\":\"nonroot\"")!=std::string::npos);
    CHECK(s.find("\"complete\":true")!=std::string::npos);
    CHECK(s.find("\"captureKind\":\"UnverifiedSource\"")!=std::string::npos);
    CHECK(p.FirstError()==c::Error::None);
}
static void SharedRoot() {
    ++cases;c::Producer p;CHECK(p.Prepare(1,129));
    for(size_t i=0;i<129;++i)CHECK(p.Add(E(0xfedcba9854321u),2));
    CHECK(p.DistinctHandles()==1 && p.RecordedEvents()==129);
    CHECK(p.EndCapture());std::string out;
    CHECK(p.EmitJson(Stamp(129),out));
    CHECK(out.find("183647585444930")==std::string::npos);
}
static void AbovePreviousPrototypeAndOverflow() {
    ++cases;c::Producer p;CHECK(p.Prepare(1024,2048));
    for(size_t i=0;i<1024;++i)CHECK(p.Add(E(static_cast<uintptr_t>(i+1u)*256u),2));
    CHECK(p.DistinctHandles()==1024 && p.EndCapture());
    std::string out;CHECK(p.EmitJson(Stamp(1024),out));
    CHECK(out.find("\"complete\":true")!=std::string::npos);
    p.Release();CHECK(p.Prepare(1024,2048));
    for(size_t i=0;i<1024;++i)CHECK(p.Add(E(i+1),2));
    CHECK(!p.Add(E(1025),2));
    CHECK(p.FirstError()==c::Error::DistinctLimit);
    CHECK(p.DroppedEvents()==1u && p.RawHandlesScrubbed());
    CHECK(!p.EndCapture());CHECK(p.EmitJson(Stamp(1024),out));
    CHECK(out.find("\"complete\":false")!=std::string::npos);
    CHECK(out.find("\"droppedEvents\":1")!=std::string::npos);
}
static void ConflictAndMissingCoverage() {
    ++cases;c::Producer p;CHECK(p.Prepare(5,10));
    CHECK(p.Add(E(5),2));
    c::Observation mismatch=E(5);mismatch.genericIndex=9;
    CHECK(!p.Add(mismatch,2));
    CHECK(p.FirstError()==c::Error::DeclarationChanged);
    CHECK(p.RawHandlesScrubbed() && !p.Add(E(6),2));
    std::string out;CHECK(p.EmitJson(Stamp(),out));
    CHECK(out.find("\"declaredEvents\":1")!=std::string::npos);
    p.Release();CHECK(p.Prepare(5,10));
    CHECK(p.Add(E(5),2));p.MarkUncovered();
    CHECK(p.FirstError()==c::Error::MissingCoverage);
    CHECK(p.EmitJson(Stamp(),out));
    CHECK(out.find("\"complete\":false")!=std::string::npos);
}
static void OwnerAndNameLimit() {
    ++cases;c::Producer p;CHECK(p.Prepare(5,10));
    CHECK(p.Add(E(3,c::Role::NonRoot,65,2048),2));
    CHECK(p.EndCapture());std::string out;
    CHECK(p.EmitJson(Stamp(),out));
    CHECK(out.find("\"namespaceBytes\":65")!=std::string::npos);
    CHECK(out.find("\"simpleNameBytes\":2048")!=std::string::npos);
    p.Release();CHECK(p.Prepare(5,10));
    c::Observation bad=E(3);bad.firstOwnerImageOrdinal=1;
    CHECK(!p.Add(bad,2));
    CHECK(p.FirstError()==c::Error::FirstOwnerMismatch);
    CHECK(p.RawHandlesScrubbed());
    p.Release();CHECK(p.Prepare(5,10));
    bad=E(3);bad.namespaceBytes=1000001;
    CHECK(!p.Add(bad,2));
    CHECK(p.FirstError()==c::Error::InvalidInput);
}
static void EventCapacityAndBadStages() {
    ++cases;c::Producer p;CHECK(!p.EndCapture());
    CHECK(!p.Prepare(0,3) && p.FirstError()==c::Error::BadPrepare);
    p.Release();CHECK(p.Prepare(4,2));
    CHECK(p.Add(E(1),2));CHECK(p.Add(E(2),2));
    CHECK(!p.Add(E(3),2) && p.FirstError()==c::Error::EventLimit);
    p.Release();CHECK(p.Prepare(4,4));
    CHECK(p.Add(E(1),2));CHECK(p.EndCapture());
    CHECK(!p.Add(E(2),2));
    CHECK(p.FirstError()==c::Error::None);
    CHECK(!p.Prepare(4,4));CHECK(p.FirstError()==c::Error::WrongStage);
    CHECK(p.RawHandlesScrubbed());
}
static void BadStampCannotEmit() {
    ++cases;c::Producer p;CHECK(p.Prepare(1,1));
    CHECK(p.Add(E(1),2));CHECK(p.EndCapture());
    c::SourceStamp s=Stamp();std::string out;
    s.metadataReaderEpoch=2;CHECK(!p.EmitJson(s,out) && out.empty());
    s=Stamp();s.metadataLockHeldDuringAdd=false;
    CHECK(!p.EmitJson(s,out));
    s=Stamp();s.demoCommit="invalid";CHECK(!p.EmitJson(s,out));
}
static void EmptyCaptureIsNotCompleteEvidence() {
    ++cases;c::Producer p;CHECK(p.Prepare(2,2));
    CHECK(p.EndCapture());std::string out;
    CHECK(p.EmitJson(Stamp(0),out));
    CHECK(out.find("\"complete\":true")!=std::string::npos);
    // Analyzer will convert zero-event/zero-class to IncompleteLowerBound.
}
static void Fixture(bool incomplete) {
    c::Producer p;CHECK(p.Prepare(200,300));
    for(size_t i=0;i<130;++i)CHECK(p.Add(E((i+1)*16u),2));
    CHECK(p.Add(E(16u,c::Role::NonRoot),2));
    if(incomplete)p.MarkUncovered();else CHECK(p.EndCapture());
    std::string s;CHECK(p.EmitJson(Stamp(130),s));
    std::fwrite(s.data(),1,s.size(),stdout);
}
int main(int argc,char** argv) {
    if(argc==2 && std::strcmp(argv[1],"--fixture")==0) {Fixture(false);return 0;}
    if(argc==2 && std::strcmp(argv[1],"--incomplete-fixture")==0) {Fixture(true);return 0;}
    RootAndNonroot();SharedRoot();AbovePreviousPrototypeAndOverflow();
    ConflictAndMissingCoverage();OwnerAndNameLimit();EventCapacityAndBadStages();
    BadStampCannotEmit();EmptyCaptureIsNotCompleteEvidence();
    std::printf("{\"kind\":\"R03B2NativeCensusProducerHost\",\"status\":\"PassedSyntheticOnly\",\"cases\":%zu,\"checks\":%zu,\"realUnity\":false,\"integratedNativeB2\":false,\"R03Accepted\":false}\n",cases,checks);
    return 0;
}
