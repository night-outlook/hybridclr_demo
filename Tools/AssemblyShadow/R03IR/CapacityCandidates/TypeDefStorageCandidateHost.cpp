// R03 B2 test-only capacity comparison. This is NOT the inactive collector.
// It uses synthetic authenticated identity VALUES, not real Unity metadata.
#include "TypeDefStorageCandidates.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace cap=r03_b2_typedef_capacity_candidates;
static unsigned checks=0,cases=0;
static void Require(bool ok,const char* expression,int line) {
    ++checks;
    if(!ok){
        std::fprintf(stderr,"Capacity candidate failure line=%d expr=%s\n",
                     line,expression);
        std::abort();
    }
}
#define CHECK(e) Require(bool(e),#e,__LINE__)

static cap::View V(uintptr_t h,uint8_t roles=cap::kRoot,
                   const char* ns="Demo",const char* name="Leaf",
                   uintptr_t owner=0x1000) {
    cap::View v{};
    v.handle=h;v.owner=owner;v.roles=roles;
    v.nameSpace=ns;v.namespaceBytes=std::strlen(ns);
    v.simpleName=name;v.nameBytes=std::strlen(name);
    v.declaringIndex=-1;v.genericIndex=-1;v.arity=0;
    return v;
}
template<class Census>
static void Test1024(size_t arenaBudget,bool compact) {
    ++cases;
    Census c;
    CHECK(c.Prepare(1024,arenaBudget));
    const size_t reserved=c.ReservedBytes();
    CHECK(reserved>0);
    for(size_t i=0;i<1024;++i) {
        const cap::View v=V(static_cast<uintptr_t>(i+1)*16,
                            (i%2)?cap::kRoot:cap::kNonRoot);
        CHECK(c.Add(v));
        CHECK(c.ReservedBytes()==reserved); // no growth after Prepare()
    }
    cap::Receipt receipt{};
    CHECK(c.Seal(receipt));
    CHECK(receipt.complete && receipt.pairs==1024);
    CHECK(receipt.roots==512 && receipt.nonRoots==512);
    CHECK(receipt.exactNameBytes==1024*8u);
    CHECK(receipt.reservedBytes==reserved);
    CHECK(receipt.indexReservedBytes>0);
    CHECK(receipt.indexNodeCapacity==2048);
    CHECK(receipt.maximumLookupVisits<=cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(receipt.maximumInsertVisits<=cap::BoundedHandlePatriciaIndex::kMaxInsertVisits);
    CHECK(receipt.totalLookupVisits<=1024u*
          cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(receipt.deterministicLookupVisitBound==
          cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(!receipt.realUnity && !receipt.coherentVmEpoch &&
          !receipt.runtimeAcceptance);
    if(compact)CHECK(reserved<1024*160u);
    c.Release();
    CHECK(c.ReservedBytes()==0);
    CHECK(c.FirstError()==cap::Error::None);
}
template<class Census>
static void Test129(size_t arenaBudget) {
    ++cases;
    Census c;
    CHECK(c.Prepare(129,arenaBudget));
    for(size_t i=0;i<129;++i)
        CHECK(c.Add(V(static_cast<uintptr_t>(i+1)*32)));
    cap::Receipt r{};
    CHECK(c.Seal(r));
    CHECK(r.complete && r.pairs==129 && r.roots==129);
    CHECK(r.exactNameBytes==129*8u);
}
template<class Census>
static void TestDuplicateAndChange(size_t arenaBudget) {
    ++cases;
    Census c;
    CHECK(c.Prepare(4,arenaBudget));
    char name[]="Leaf";
    CHECK(c.Add(V(16,cap::kRoot,"Demo",name)));
    name[0]='X'; // original input bytes are NOT retained by the store
    CHECK(c.Add(V(16,cap::kNonRoot,"Demo","Leaf")));
    CHECK(c.Add(V(32,cap::kRoot|cap::kNonRoot)));
    cap::Receipt r{};
    CHECK(c.Seal(r));
    CHECK(r.complete && r.pairs==2 && r.roots==2 && r.nonRoots==2);
    CHECK(r.exactNameBytes==16);

    ++cases;
    Census changed;
    CHECK(changed.Prepare(3,arenaBudget));
    CHECK(changed.Add(V(16)));
    CHECK(!changed.Add(V(16,cap::kRoot,"Demo","Laff")));
    CHECK(changed.FirstError()==cap::Error::ContentChanged);
    cap::Receipt rejected{};CHECK(!changed.Seal(rejected));
    CHECK(!rejected.complete && rejected.pairs==0 && rejected.roots==0);
}
template<class Census>
static void TestOwnerCollision(size_t arenaBudget) {
    ++cases;
    Census c;CHECK(c.Prepare(3,arenaBudget));
    CHECK(c.Add(V(16)));
    CHECK(!c.Add(V(16,cap::kNonRoot,"Demo","Leaf",0x2000)));
    CHECK(c.FirstError()==cap::Error::OwnerConflict);
    CHECK(!c.Add(V(32))); // first error wins
    CHECK(c.FirstError()==cap::Error::OwnerConflict);
    cap::Receipt r{};CHECK(!c.Seal(r));
    CHECK(!r.complete && r.pairs==0);
}
template<class Census>
static void TestPairCapacity(size_t arenaBudget) {
    ++cases;
    Census c;CHECK(c.Prepare(128,arenaBudget));
    for(size_t i=0;i<128;++i)
        CHECK(c.Add(V(static_cast<uintptr_t>(i+1)*16)));
    CHECK(!c.Add(V(129*16u)));
    CHECK(c.FirstError()==cap::Error::PairCapacity);
    cap::Receipt r{};
    CHECK(!c.Seal(r) && !r.complete && r.pairs==0);

    ++cases;
    Census invalid;
    CHECK(invalid.Prepare(1,arenaBudget));
    CHECK(!invalid.Add(V(0)));
    CHECK(invalid.FirstError()==cap::Error::InvalidInput);
}
template<class Census>
static void TestNameBudget(size_t arenaBudget) {
    ++cases;
    Census c;CHECK(c.Prepare(2,arenaBudget));
    char full[65]{};
    std::memset(full,'X',64);
    full[64]=0;
    CHECK(c.Add(V(16,cap::kRoot,full,"Leaf")));
    cap::Receipt result{};CHECK(c.Seal(result));
    CHECK(result.complete && result.pairs==1);
    CHECK(result.exactNameBytes==68);

    ++cases;
    Census tooLong;CHECK(tooLong.Prepare(2,arenaBudget));
    char oversized[66]{};
    std::memset(oversized,'Y',65);
    oversized[65]=0;
    CHECK(!tooLong.Add(V(16,cap::kRoot,oversized,"Leaf")));
    CHECK(tooLong.FirstError()==cap::Error::NameLimit);
}

static uintptr_t AdversarialHandle(size_t i) {
    // Identical low bits: intentionally defeats a naive (key>>3)%N table.
    const uintptr_t top=static_cast<uintptr_t>(1u)
                        << (cap::BoundedHandlePatriciaIndex::kKeyBits-1u);
    return top | (static_cast<uintptr_t>(i+1u)<<8u) |
           static_cast<uintptr_t>(0x80u);
}
template<class Census>
static void TestReverseOrderAdversarialHandles(size_t arenaBudget) {
    ++cases;
    Census c;
    CHECK(c.Prepare(1024,arenaBudget));
    const size_t allocated=c.ReservedBytes();
    for(size_t i=0;i<1024;++i)
        CHECK(c.Add(V(AdversarialHandle(i),cap::kRoot)));
    // Duplicate role merge in reverse arrival order: no new text records,
    // no heap growth and no pointer-order dependence.
    for(size_t i=1024;i>0;--i)
        CHECK(c.Add(V(AdversarialHandle(i-1),cap::kNonRoot)));
    CHECK(c.ReservedBytes()==allocated);
    cap::Receipt receipt{};
    CHECK(c.Seal(receipt));
    CHECK(receipt.complete && receipt.pairs==1024);
    CHECK(receipt.roots==1024 && receipt.nonRoots==1024);
    CHECK(receipt.exactNameBytes==8192);
    CHECK(receipt.maximumLookupVisits<=
          cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(receipt.maximumInsertVisits<=
          cap::BoundedHandlePatriciaIndex::kMaxInsertVisits);
    CHECK(receipt.totalLookupVisits<=2048u*
          cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(!receipt.realUnity && !receipt.runtimeAcceptance);
}
template<class Census>
static void TestHighBitPrefixAndOwnerConflict(size_t arenaBudget) {
    ++cases;
    Census c;
    CHECK(c.Prepare(128,arenaBudget));
    const uintptr_t high=static_cast<uintptr_t>(1u)
                           << (cap::BoundedHandlePatriciaIndex::kKeyBits-1u);
    CHECK(c.Add(V(high)));
    for(size_t bit=0;bit+1<cap::BoundedHandlePatriciaIndex::kKeyBits;++bit) {
        const uintptr_t key=high|(static_cast<uintptr_t>(1u)<<bit);
        CHECK(c.Add(V(key)));
    }
    // The last existing leaf must remain findable regardless of trie splits.
    const uintptr_t last=high|static_cast<uintptr_t>(1u);
    CHECK(!c.Add(V(last,cap::kRoot,"Demo","Leaf",0x2000u)));
    CHECK(c.FirstError()==cap::Error::OwnerConflict);
    cap::Receipt r{};CHECK(!c.Seal(r));
    CHECK(!r.complete && r.pairs==0);
    c.Release();
    CHECK(c.Prepare(3,arenaBudget));
    CHECK(c.Add(V(high)));
    CHECK(c.Add(V(last)));
    cap::Receipt after{};
    CHECK(c.Seal(after) && after.complete && after.pairs==2);
    CHECK(after.maximumLookupVisits<=
          cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
}
static void TestDirectPatriciaInvariants() {
    ++cases;
    cap::BoundedHandlePatriciaIndex idx;
    CHECK(!idx.Prepare(0));
    CHECK(idx.Prepare(1024));
    CHECK(idx.ReservedBytes()>0 && idx.NodeCapacity()==2048);
    for(size_t i=0;i<1024;++i) {
        size_t steps=0;
        CHECK(idx.Insert(AdversarialHandle(i),i,steps));
        CHECK(steps<=cap::BoundedHandlePatriciaIndex::kMaxInsertVisits);
    }
    CHECK(idx.Count()==1024);
    for(size_t i=1024;i>0;--i) {
        size_t row=1024,steps=0;
        CHECK(idx.Find(AdversarialHandle(i-1),row,steps));
        CHECK(row==i-1);
        CHECK(steps<=cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    }
    size_t absent=1024,steps=0;
    CHECK(!idx.Find(AdversarialHandle(1024),absent,steps));
    CHECK(absent==0 && steps<=cap::BoundedHandlePatriciaIndex::kMaxLookupVisits);
    CHECK(!idx.Find(0,absent,steps));
    CHECK(!idx.Insert(AdversarialHandle(0),0,steps));
    idx.Clear();
    CHECK(idx.Count()==0);
    CHECK(!idx.Find(AdversarialHandle(0),absent,steps));
    CHECK(idx.Insert(AdversarialHandle(0),0,steps));
    CHECK(idx.Find(AdversarialHandle(0),absent,steps) && absent==0);
    idx.Release();
    CHECK(idx.ReservedBytes()==0 && idx.Count()==0);
    CHECK(idx.Prepare(1));
    CHECK(idx.Insert(1,0,steps));
    CHECK(!idx.Insert(2,0,steps));
    idx.Release();
}

static void TestArenaExhaustionAndReuse() {
    ++cases;
    cap::CompactArenaCensus c;
    CHECK(c.Prepare(4,12));
    CHECK(c.Add(V(16))); // 8 bytes
    CHECK(!c.Add(V(32))); // second row needs another 8
    CHECK(c.FirstError()==cap::Error::ArenaCapacity);
    cap::Receipt r{};CHECK(!c.Seal(r));
    CHECK(!r.complete && !r.runtimeAcceptance);
    c.Release();
    CHECK(c.ReservedBytes()==0);
    CHECK(c.Prepare(4,64));
    CHECK(c.Add(V(16)));
    CHECK(c.Add(V(32)));
    cap::Receipt fresh{};CHECK(c.Seal(fresh));
    CHECK(fresh.complete && fresh.pairs==2);
}
static void TestInvalidPrepare() {
    ++cases;
    cap::FixedSlabCensus slab;
    CHECK(!slab.Prepare(0));
    CHECK(slab.FirstError()==cap::Error::BadPrepare);
    slab.Release();
    CHECK(slab.Prepare(1024));
    CHECK(!slab.Prepare(1024));
    CHECK(slab.FirstError()==cap::Error::WrongStage);
    slab.Release();

    ++cases;
    cap::CompactArenaCensus compact;
    CHECK(!compact.Prepare(cap::kMaximumPairs+1,4096));
    CHECK(compact.FirstError()==cap::Error::BadPrepare);
    compact.Release();
    CHECK(!compact.Prepare(100,0));
    CHECK(compact.FirstError()==cap::Error::AllocationFailed);
}
int main() {
    Test1024<cap::FixedSlabCensus>(1,false);
    Test1024<cap::CompactArenaCensus>(32*1024,true);
    Test129<cap::FixedSlabCensus>(1);
    Test129<cap::CompactArenaCensus>(4*1024);
    TestDuplicateAndChange<cap::FixedSlabCensus>(1);
    TestDuplicateAndChange<cap::CompactArenaCensus>(128);
    TestOwnerCollision<cap::FixedSlabCensus>(1);
    TestOwnerCollision<cap::CompactArenaCensus>(128);
    TestPairCapacity<cap::FixedSlabCensus>(1);
    TestPairCapacity<cap::CompactArenaCensus>(2048);
    TestNameBudget<cap::FixedSlabCensus>(1);
    TestNameBudget<cap::CompactArenaCensus>(128);
    TestReverseOrderAdversarialHandles<cap::FixedSlabCensus>(1);
    TestReverseOrderAdversarialHandles<cap::CompactArenaCensus>(32*1024);
    TestHighBitPrefixAndOwnerConflict<cap::FixedSlabCensus>(1);
    TestHighBitPrefixAndOwnerConflict<cap::CompactArenaCensus>(1024);
    TestDirectPatriciaInvariants();
    TestArenaExhaustionAndReuse();
    TestInvalidPrepare();

    cap::FixedSlabCensus slab;
    cap::CompactArenaCensus compact;
    CHECK(slab.Prepare(1024));
    CHECK(compact.Prepare(1024,32*1024));
    const size_t slabReserved=slab.ReservedBytes();
    const size_t compactReserved=compact.ReservedBytes();
    CHECK(compactReserved<slabReserved);
    CHECK(slab.ReservedBytes()==slabReserved &&
          compact.ReservedBytes()==compactReserved);
    cap::BoundedHandlePatriciaIndex indexProbe;
    CHECK(indexProbe.Prepare(1024));
    const size_t indexReserved=indexProbe.ReservedBytes();
    const size_t indexNodes=indexProbe.NodeCapacity();
    CHECK(indexNodes==2048 && indexReserved>0);
    CHECK(slabReserved>indexReserved && compactReserved>indexReserved);
    indexProbe.Release();
    std::printf("{\"kind\":\"R03B2StorageCandidateHost\","
       "\"result\":\"PassedSyntheticStorageOnly\","
       "\"cases\":%u,\"assertions\":%u,"
       "\"capacity\":1024,\"priorLiveCap\":128,"
       "\"slabReservedBytes\":%zu,\"compactReservedBytes\":%zu,"
       "\"compactArenaBudgetBytes\":32768,"
       "\"indexReservedBytes\":%zu,\"indexNodeCapacity\":%zu,"
       "\"indexKind\":\"BoundedPatriciaTrie\","
       "\"indexMaxLookupVisits\":%zu,"
       "\"indexMaxInsertVisits\":%zu,"
       "\"realUnity\":false,\"realMetadata\":false,"
       "\"integratedInB2\":false,\"runtimeAcceptance\":false,"
       "\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",
       cases,checks,slabReserved,compactReserved,
       indexReserved,indexNodes,
       cap::BoundedHandlePatriciaIndex::kMaxLookupVisits,
       cap::BoundedHandlePatriciaIndex::kMaxInsertVisits);
    return 0;
}
