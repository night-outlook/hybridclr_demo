// R03 B2 test-only two-pass source coverage model. Never add to libil2cpp.
#include "TypeDefSourceCoverageReplay.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
namespace cov=r03_b2_typedef_coverage_replay;
namespace src=r03_b2_original_v1_source_adapter;
namespace census=r03_b2_typedef_native_census;
static size_t cases=0,checks=0;
static void Require(bool yes,const char* expr,int line) {
    ++checks;
    if(!yes) {std::fprintf(stderr,"FAIL line %d: %s\n",line,expr);std::abort();}
}
#define CHECK(expr) Require(bool(expr),#expr,__LINE__)
static census::SourceStamp Stamp(uint32_t images=2,uint32_t classes=1) {
    census::SourceStamp s{};
    s.nativeCommit="cecf4b859d50b128e5c0fc6c90cd89e3a452b96a";
    s.demoCommit="0778ea5feb4bef7c96591ea5b5c647465b467e79";
    s.originalV1ImageCount=images;s.observedClasses=classes;
    s.metadataReaderEpoch=1;s.metadataLockHeldDuringAdd=true;
    s.classPasses=3;s.originalV1ImagePasses=2;
    return s;
}
static census::Observation Use(uintptr_t handle,uint32_t owner,
                               cov::Kind kind) {
    census::Observation o{};
    o.handle=handle;o.ownerImageOrdinal=o.firstOwnerImageOrdinal=owner;
    o.role=cov::RoleFor(kind);
    o.namespaceBytes=4;o.simpleNameBytes=5;
    return o;
}
static const uintptr_t firstImage[]={10,20,30,40};
static const uintptr_t secondImage[]={20,50,60};
static const src::ImageView images[]={
    src::ImageView(firstImage,4,10,10),src::ImageView(secondImage,3,11,11)
};
static bool PlanSingle(cov::Replay& p,cov::Kind kind= cov::Kind::ClassRoot) {
    size_t id=0;
    return p.PlanClass(0) && p.PlanUse(0,kind,id) && id==1 && p.SealPlan();
}
static void AcceptOneAndClose() {
    ++cases;cov::Replay r;CHECK(r.Prepare(1,1,2,64));
    const size_t reserved=r.ReservedBytes();
    CHECK(PlanSingle(r));CHECK(r.VisitClass(0));
    CHECK(r.VisitUse(1,0,cov::Kind::ClassRoot,images,2,
                     Use(20,0,cov::Kind::ClassRoot)));
    CHECK(r.IndexedOwnerLookups()==2);
    CHECK(r.ReservedBytes()==reserved);
    CHECK(r.CloseAfterSource());CHECK(r.Complete());
    CHECK(r.RawHandlesScrubbed());
    std::string result;CHECK(r.EmitJson(Stamp(),result));
    CHECK(result.find("\"complete\":true")!=std::string::npos);
    CHECK(result.find("\"captureKind\":\"UnverifiedSource\"")!=std::string::npos);
    CHECK(result.find("\"handle\":")==std::string::npos);
    CHECK(r.PlannedClasses()==1 && r.VisitedClasses()==1);
    CHECK(r.PlannedSites()==1 && r.VisitedSites()==1);
    CHECK(r.RecordedEvents()==1 && r.DistinctHandles()==1);
}
static void MultiClassRolesAndNestedSources() {
    ++cases;cov::Replay r;CHECK(r.Prepare(2,7,2,95));
    CHECK(r.PlanClass(1));CHECK(r.PlanClass(0));
    size_t ids[7]{};
    CHECK(r.PlanUse(0,cov::Kind::ClassRoot,ids[0]));
    CHECK(r.PlanUse(1,cov::Kind::ClassRoot,ids[1]));
    CHECK(r.PlanUse(0,cov::Kind::GenericArgument,ids[2]));
    CHECK(r.PlanUse(1,cov::Kind::DeclaringAncestor,ids[3]));
    CHECK(r.PlanUse(1,cov::Kind::PrimitiveDefault,ids[4]));
    CHECK(r.PlanUse(0,cov::Kind::CompositeClassLeaf,ids[5]));
    CHECK(r.PlanUse(0,cov::Kind::GenericDefinition,ids[6]));
    CHECK(r.SealPlan());CHECK(r.VisitClass(0));CHECK(r.VisitClass(1));
    const uintptr_t handles[]={20,50,20,10,30,40,60};
    const uint32_t owners[]={0,1,0,0,0,0,1};
    const size_t classSlots[]={0,1,0,1,1,0,0};
    const cov::Kind kinds[]={cov::Kind::ClassRoot,cov::Kind::ClassRoot,
        cov::Kind::GenericArgument,cov::Kind::DeclaringAncestor,
        cov::Kind::PrimitiveDefault,cov::Kind::CompositeClassLeaf,
        cov::Kind::GenericDefinition};
    for(size_t j=0;j<7;++j) {
        const size_t i=6-j; // shuffled replay, stable site ID
        CHECK(ids[i]==i+1);
        CHECK(r.VisitUse(ids[i],classSlots[i],kinds[i],images,2,
                         Use(handles[i],owners[i],kinds[i])));
    }
    CHECK(r.VisitedSites()==7 && r.DistinctHandles()==6);
    CHECK(r.CloseAfterSource());
    std::string json;CHECK(r.EmitJson(Stamp(2,2),json));
    CHECK(json.find("\"declaredEvents\":7")!=std::string::npos);
    CHECK(json.find("\"complete\":true")!=std::string::npos);
}
static void MissingPlannedAndAbsentRoot() {
    ++cases;cov::Replay missing;CHECK(missing.Prepare(2,2,2,20));
    CHECK(missing.PlanClass(0));
    size_t id=0;CHECK(missing.PlanUse(0,cov::Kind::ClassRoot,id));
    CHECK(!missing.SealPlan());
    CHECK(missing.FirstError()==cov::Error::MissingPlannedCoverage);
    CHECK(!missing.Complete() && missing.RawHandlesScrubbed());
    cov::Replay noRoot;CHECK(noRoot.Prepare(1,1,2,20));
    CHECK(noRoot.PlanClass(0));
    CHECK(noRoot.PlanUse(0,cov::Kind::GenericArgument,id));
    CHECK(!noRoot.SealPlan());
    CHECK(noRoot.FirstError()==cov::Error::MissingPlannedCoverage);
}
static void MissingReplaySiteAndClass() {
    ++cases;cov::Replay a;CHECK(a.Prepare(1,2,2,32));
    CHECK(a.PlanClass(0));size_t id=0,other=0;
    CHECK(a.PlanUse(0,cov::Kind::ClassRoot,id));
    CHECK(a.PlanUse(0,cov::Kind::GenericArgument,other));
    CHECK(a.SealPlan());CHECK(a.VisitClass(0));
    CHECK(a.VisitUse(id,0,cov::Kind::ClassRoot,images,2,
                     Use(20,0,cov::Kind::ClassRoot)));
    CHECK(!a.CloseAfterSource());
    CHECK(a.FirstError()==cov::Error::MissingVisitedCoverage);
    CHECK(a.RawHandlesScrubbed());
    std::string json;CHECK(a.EmitJson(Stamp(),json));
    CHECK(json.find("\"complete\":false")!=std::string::npos);
    CHECK(json.find("\"declaredEvents\":1")!=std::string::npos);
    cov::Replay b;CHECK(b.Prepare(1,1,2,20));
    CHECK(PlanSingle(b));
    CHECK(!b.CloseAfterSource());
    CHECK(b.FirstError()==cov::Error::MissingVisitedCoverage);
}
static void DuplicateAndUnexpectedSourceUse() {
    ++cases;cov::Replay d;CHECK(d.Prepare(1,1,2,20));
    CHECK(PlanSingle(d));CHECK(d.VisitClass(0));
    CHECK(d.VisitUse(1,0,cov::Kind::ClassRoot,images,2,
                     Use(10,0,cov::Kind::ClassRoot)));
    CHECK(!d.VisitUse(1,0,cov::Kind::ClassRoot,images,2,
                      Use(10,0,cov::Kind::ClassRoot)));
    CHECK(d.FirstError()==cov::Error::DuplicateSite);
    CHECK(!d.Complete() && d.RawHandlesScrubbed());
    cov::Replay wrong;CHECK(wrong.Prepare(1,1,2,20));
    CHECK(PlanSingle(wrong));CHECK(wrong.VisitClass(0));
    CHECK(!wrong.VisitUse(1,0,cov::Kind::GenericArgument,images,2,
                          Use(10,0,cov::Kind::GenericArgument)));
    CHECK(wrong.FirstError()==cov::Error::SourcePathMismatch);
    cov::Replay duplicate;CHECK(duplicate.Prepare(1,1,2,20));
    CHECK(duplicate.PlanClass(0));
    CHECK(!duplicate.PlanClass(0));
    CHECK(duplicate.FirstError()==cov::Error::DuplicateClassSlot);
}
static void OwnerMismatchAndUnsupportedPaths() {
    ++cases;cov::Replay o;CHECK(o.Prepare(1,1,2,20));
    CHECK(PlanSingle(o));CHECK(o.VisitClass(0));
    CHECK(!o.VisitUse(1,0,cov::Kind::ClassRoot,images,2,
                      Use(20,1,cov::Kind::ClassRoot)));
    CHECK(o.FirstError()==cov::Error::OwnerRejected);
    CHECK(o.RawHandlesScrubbed());
    cov::Replay u;CHECK(u.Prepare(1,1,2,20));
    CHECK(u.PlanClass(0));u.MarkUnsupported();
    CHECK(u.FirstError()==cov::Error::UnsupportedPath);
    CHECK(!u.CloseAfterSource());
    cov::Replay late;CHECK(late.Prepare(1,1,2,20));
    CHECK(PlanSingle(late));CHECK(late.VisitClass(0));
    CHECK(late.VisitUse(1,0,cov::Kind::ClassRoot,images,2,
                        Use(10,0,cov::Kind::ClassRoot)));
    CHECK(late.CloseAfterSource());CHECK(late.Complete());
    late.MarkUnsupported();
    CHECK(!late.Complete() && late.RawHandlesScrubbed());
}
static void OverflowAndInputShape() {
    ++cases;cov::Replay x;CHECK(!x.Prepare(0,1,2,30));
    CHECK(x.FirstError()==cov::Error::BadPrepare);
    x.Reset();CHECK(!x.Prepare(2,1,2,30));
    CHECK(x.FirstError()==cov::Error::BadPrepare);
    x.Reset();CHECK(x.Prepare(1,1,2,30));
    CHECK(x.PlanClass(0));size_t id=0;
    CHECK(!x.PlanUse(0,static_cast<cov::Kind>(255),id));
    CHECK(x.FirstError()==cov::Error::InvalidSite);
    x.Reset();CHECK(x.Prepare(1,1,2,30));
    CHECK(x.PlanClass(0));
    CHECK(x.PlanUse(0,cov::Kind::ClassRoot,id));
    CHECK(!x.PlanUse(0,cov::Kind::ClassRoot,id));
    CHECK(x.FirstError()==cov::Error::InvalidSite ||
          x.FirstError()==cov::Error::DuplicateSite);
    x.Reset();CHECK(x.Prepare(1,1,2,30));
    CHECK(PlanSingle(x));CHECK(x.VisitClass(0));
    CHECK(!x.VisitUse(2,0,cov::Kind::ClassRoot,images,2,
                      Use(10,0,cov::Kind::ClassRoot)));
    CHECK(x.FirstError()==cov::Error::InvalidSite);
}
static void DistinctHandleBoundIsIncomplete() {
    ++cases;cov::Replay r;
    const size_t n=1025;
    CHECK(r.Prepare(1,n,1,600000));
    uintptr_t handles[n]{};
    for(size_t i=0;i<n;++i)handles[i]=static_cast<uintptr_t>(i+1)*16u;
    const src::ImageView one[]={src::ImageView(handles,static_cast<uint32_t>(n),1,1)};
    CHECK(r.PlanClass(0));
    size_t ids[n]{};
    for(size_t i=0;i<n;++i)
        CHECK(r.PlanUse(0,i==0?cov::Kind::ClassRoot:
                         cov::Kind::GenericArgument,ids[i]));
    CHECK(r.SealPlan());CHECK(r.VisitClass(0));
    const size_t allocated=r.ReservedBytes();
    for(size_t i=0;i<n-1;++i) {
        const cov::Kind kind=i==0?cov::Kind::ClassRoot:cov::Kind::GenericArgument;
        CHECK(r.VisitUse(ids[i],0,kind,one,1,Use(handles[i],0,kind)));
        CHECK(r.ReservedBytes()==allocated);
    }
    CHECK(r.DistinctHandles()==1024);
    CHECK(!r.VisitUse(ids[n-1],0,cov::Kind::GenericArgument,
                      one,1,Use(handles[n-1],0,cov::Kind::GenericArgument)));
    CHECK(r.FirstError()==cov::Error::OwnerRejected);
    CHECK(r.RawHandlesScrubbed() && !r.Complete());
    std::string output;CHECK(r.EmitJson(Stamp(1),output));
    CHECK(output.find("\"complete\":false")!=std::string::npos);
    CHECK(output.find("\"droppedEvents\":1")!=std::string::npos);
}
static void AbortedSessionIsNotComplete() {
    ++cases;
    {cov::Replay a;CHECK(a.Prepare(1,1,2,20));
     CHECK(a.PlanClass(0));} // destructor must fail closed
    cov::Replay b;CHECK(b.Prepare(1,1,2,20));
    CHECK(PlanSingle(b));
    b.Reset();
    CHECK(!b.Complete() && b.RawHandlesScrubbed());
    CHECK(b.FirstError()==cov::Error::None); // reset clears state
    CHECK(b.Prepare(1,1,2,20));
}
static void Fixture(bool incomplete) {
    cov::Replay r;CHECK(r.Prepare(1,3,2,64));
    CHECK(r.PlanClass(0));size_t root=0,leaf=0,other=0;
    CHECK(r.PlanUse(0,cov::Kind::ClassRoot,root));
    CHECK(r.PlanUse(0,cov::Kind::GenericArgument,leaf));
    CHECK(r.PlanUse(0,cov::Kind::PrimitiveDefault,other));
    CHECK(r.SealPlan());CHECK(r.VisitClass(0));
    CHECK(r.VisitUse(root,0,cov::Kind::ClassRoot,images,2,
                     Use(20,0,cov::Kind::ClassRoot)));
    CHECK(r.VisitUse(leaf,0,cov::Kind::GenericArgument,images,2,
                     Use(20,0,cov::Kind::GenericArgument)));
    CHECK(r.VisitUse(other,0,cov::Kind::PrimitiveDefault,images,2,
                     Use(50,1,cov::Kind::PrimitiveDefault)));
    if(incomplete)r.MarkUnsupported();else CHECK(r.CloseAfterSource());
    std::string output;CHECK(r.EmitJson(Stamp(),output));
    std::fwrite(output.data(),1,output.size(),stdout);
}
int main(int argc,char** argv) {
    if(argc==2 && std::strcmp(argv[1],"--fixture")==0) {
        Fixture(false);return 0;
    }
    if(argc==2 && std::strcmp(argv[1],"--incomplete-fixture")==0) {
        Fixture(true);return 0;
    }
    AcceptOneAndClose();MultiClassRolesAndNestedSources();
    MissingPlannedAndAbsentRoot();MissingReplaySiteAndClass();
    DuplicateAndUnexpectedSourceUse();OwnerMismatchAndUnsupportedPaths();
    OverflowAndInputShape();DistinctHandleBoundIsIncomplete();
    AbortedSessionIsNotComplete();
    std::printf("{\"kind\":\"R03B2TypeDefSourceCoverageReplayHost\",\"status\":\"PassedSyntheticOnly\",\"cases\":%zu,\"checks\":%zu,\"realUnity\":false,\"nativeIntegrated\":false,\"fullSourceProven\":false,\"R03Accepted\":false}\n",cases,checks);
    return 0;
}
