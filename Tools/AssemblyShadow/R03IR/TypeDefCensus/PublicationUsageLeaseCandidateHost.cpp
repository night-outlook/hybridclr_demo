// R03 B2 TEST ONLY. Synthetic failure injection for two-callback usage custody.
// No Unity VM, no actual global UsageLock, and no native product modification.
#include "PublicationUsageLeaseCandidate.h"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <string>

namespace candidate=r03_b2_usage_lease_candidate;
static unsigned cases=0,checks=0;
static void Require(bool yes,const char* expr,int line) {
    ++checks;
    if(!yes){std::fprintf(stderr,"FAIL line %d: %s\n",line,expr);std::abort();}
}
#define CHECK(expr) Require(bool(expr),#expr,__LINE__)
struct LockProbe {
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    unsigned acquired=0,released=0;
    bool failAcquire=false;
    bool held=false;
};
static void Lock(void* raw) {
    auto& p=*static_cast<LockProbe*>(raw);
    if(p.failAcquire)throw std::runtime_error("synthetic lock failure");
    if(p.lock.test_and_set(std::memory_order_acquire))
        throw std::logic_error("synthetic recursive UsageLock");
    p.held=true;++p.acquired;
}
static void Unlock(void* raw) {
    auto& p=*static_cast<LockProbe*>(raw);
    p.held=false;++p.released;
    p.lock.clear(std::memory_order_release);
}
struct Context {
    candidate::Lease lease;
    LockProbe* lock=nullptr;
    bool baselineAlreadyUsed=false;
    bool codecPublished=false;
    bool activePublished=false;
    bool runtimeFailure=false;
    bool requiresRestart=false;
    explicit Context(LockProbe& p):lock(&p){}
    Context(const Context&)=delete;
    Context& operator=(const Context&)=delete;
};
enum class Outcome { Success, ReturnError, ThrowBeforeCodec,
                     ThrowAfterCodec, ThrowAfterActive };
static bool TryBegin(Context& p) {
    if(!p.lease.Enter(p.lock,Lock,Unlock))return false;
    if(p.baselineAlreadyUsed){p.lease.Release();return false;}
    return true;
}
static bool PublishActive(Context& p,Outcome result) {
    CHECK(p.lease.Held());
    if(result==Outcome::ReturnError) {
        p.runtimeFailure=true;
        p.lease.Release();
        return false;
    }
    if(result==Outcome::ThrowBeforeCodec)
        throw std::runtime_error("precommit codec exception");
    p.codecPublished=true;
    if(result==Outcome::ThrowAfterCodec)
        throw std::runtime_error("post-codec, pre-active exception");
    p.activePublished=true;
    if(result==Outcome::ThrowAfterActive)
        throw std::runtime_error("post-active exception");
    p.lease.Release();
    return true;
}
static void NormalSuccess() {
    ++cases;LockProbe p;
    {Context x(p);CHECK(TryBegin(x));CHECK(p.held);
     CHECK(PublishActive(x,Outcome::Success));
     CHECK(x.codecPublished && x.activePublished);
     CHECK(!x.lease.Held());}
    CHECK(!p.held && p.acquired==1 && p.released==1);
}
static void BaselinePreventsCommit() {
    ++cases;LockProbe p;
    {Context x(p);x.baselineAlreadyUsed=true;
     CHECK(!TryBegin(x));CHECK(!x.lease.Held());
     CHECK(!x.codecPublished && !x.activePublished);}
    CHECK(!p.held && p.acquired==1 && p.released==1);
}
static void ErrorReleases() {
    ++cases;LockProbe p;
    {Context x(p);CHECK(TryBegin(x));CHECK(!PublishActive(x,Outcome::ReturnError));
     CHECK(x.runtimeFailure && !x.codecPublished && !x.activePublished);
     CHECK(!x.lease.Held());}
    CHECK(!p.held && p.acquired==1 && p.released==1);
}
static void ExceptionBeforeCodecReleases() {
    ++cases;LockProbe p;bool caught=false;
    try{Context x(p);CHECK(TryBegin(x));
        CHECK(p.held);PublishActive(x,Outcome::ThrowBeforeCodec);}
    catch(const std::runtime_error&){caught=true;}
    CHECK(caught && !p.held);
    CHECK(p.acquired==1 && p.released==1);
}
static void ExceptionAfterCodecNeedsRestart() {
    ++cases;LockProbe p;bool caught=false;
    try{Context x(p);CHECK(TryBegin(x));
        PublishActive(x,Outcome::ThrowAfterCodec);}
    catch(const std::runtime_error&){caught=true;}
    CHECK(caught && !p.held);
    CHECK(p.acquired==1 && p.released==1);
    // Lock release alone cannot roll back a published metadata-index state.
    // Real native design must seal terminal failure and require restart.
}
static void ExceptionAfterActiveReleasesButNotTransaction() {
    ++cases;LockProbe p;bool caught=false;
    try{Context x(p);CHECK(TryBegin(x));
        PublishActive(x,Outcome::ThrowAfterActive);}
    catch(const std::runtime_error&){caught=true;}
    CHECK(caught && !p.held && p.released==1);
    // The caller has no evidence that the active store and metadata publish
    // may be treated as one rollback-safe transaction after an exception.
}
static void ExceptionDuringAcquireNeverArms() {
    ++cases;LockProbe p;p.failAcquire=true;bool caught=false;
    {Context x(p);
     try{TryBegin(x);}catch(const std::runtime_error&){caught=true;}
     CHECK(!x.lease.Held());}
    CHECK(caught && !p.held && p.acquired==0 && p.released==0);
}
static void ContextScopeAbandonedReleases() {
    ++cases;LockProbe p;
    {Context x(p);CHECK(TryBegin(x));CHECK(x.lease.Held());}
    CHECK(!p.held && p.acquired==1 && p.released==1);
}
static void DuplicateEnterRejected() {
    ++cases;LockProbe p;
    {candidate::Lease l;CHECK(l.Enter(&p,Lock,Unlock));
     CHECK(!l.Enter(&p,Lock,Unlock));CHECK(p.held);
     l.Release();CHECK(!l.Held());}
    CHECK(!p.held && p.acquired==1 && p.released==1);
}
static void NullCallbacksFailClosed() {
    ++cases;LockProbe p;candidate::Lease l;
    CHECK(!l.Enter(nullptr,Lock,Unlock));
    CHECK(!l.Enter(&p,nullptr,Unlock));
    CHECK(!l.Enter(&p,Lock,nullptr));
    CHECK(!l.Held() && !p.held && p.released==0);
}
static void ReleaseIdempotent() {
    ++cases;LockProbe p;
    {candidate::Lease l;CHECK(l.Enter(&p,Lock,Unlock));
     l.Release();l.Release();CHECK(!l.Held());}
    CHECK(p.acquired==1 && p.released==1 && !p.held);
}
static void RetryAfterReleased() {
    ++cases;LockProbe p;
    {candidate::Lease l;CHECK(l.Enter(&p,Lock,Unlock));l.Release();
     CHECK(l.Enter(&p,Lock,Unlock));l.Release();}
    CHECK(p.acquired==2 && p.released==2 && !p.held);
}
static void AnotherSessionCanEnterAfterUnwind() {
    ++cases;LockProbe p;
    try{Context x(p);CHECK(TryBegin(x));
        PublishActive(x,Outcome::ThrowAfterCodec);}
    catch(const std::runtime_error&){}
    {Context x(p);CHECK(TryBegin(x));CHECK(PublishActive(x,Outcome::Success));}
    CHECK(!p.held && p.acquired==2 && p.released==2);
}
static void NoExceptionsInReleaseFunction() {
    ++cases;LockProbe p;
    {Context x(p);CHECK(TryBegin(x));x.lease.Release();
     CHECK(!x.lease.Held());CHECK(!p.held);}
    CHECK(p.released==1);
}
int main() {
    NormalSuccess();BaselinePreventsCommit();ErrorReleases();
    ExceptionBeforeCodecReleases();ExceptionAfterCodecNeedsRestart();
    ExceptionAfterActiveReleasesButNotTransaction();
    ExceptionDuringAcquireNeverArms();ContextScopeAbandonedReleases();
    DuplicateEnterRejected();NullCallbacksFailClosed();
    ReleaseIdempotent();RetryAfterReleased();
    AnotherSessionCanEnterAfterUnwind();NoExceptionsInReleaseFunction();
    std::printf("{\"kind\":\"R03B2PublicationUsageLeaseCandidateHost\",\"result\":\"PassedSyntheticOnly\",\"cases\":%u,\"checks\":%u,\"nativeIntegrated\":false,\"manualUsageLockExceptionSafeProven\":false,\"realUnity\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",cases,checks);
    return 0;
}
