// R03 B2 HOST ONLY. No metadata pointer, native lock, Unity Player or commit.
#include "PublicationFailureBoundaryCandidate.h"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
namespace policy=r03_b2_publication_failure_boundary;
static unsigned cases=0, checks=0;
static void Require(bool ok,const char* what,int line) {
    ++checks;
    if(!ok){std::fprintf(stderr,"FAIL %d %s\n",line,what);std::abort();}
}
#define CHECK(x) Require(bool(x),#x,__LINE__)
struct LockProbe {
    std::atomic_flag mutex=ATOMIC_FLAG_INIT;
    unsigned enters=0,exits=0;
    bool held=false,throwOnLock=false;
};
static void Lock(void* opaque) {
    auto& p=*static_cast<LockProbe*>(opaque);
    if(p.throwOnLock)throw std::runtime_error("synthetic lock failed");
    if(p.mutex.test_and_set(std::memory_order_acquire))throw std::logic_error("lock already held");
    ++p.enters;p.held=true;
}
static void Unlock(void* opaque) {
    auto& p=*static_cast<LockProbe*>(opaque);
    p.held=false;++p.exits;p.mutex.clear(std::memory_order_release);
}
static bool SafeFlags(const policy::Receipt& p) {
    return !p.nativeIntegrated && !p.realUnity && !p.realRollbackProven &&
           !p.exceptionSafetyOfNativePublisherProven && !p.R03Accepted &&
           !p.ReadyForHumanReviewGate;
}
static void NormalComplete() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);
     CHECK(s.Enter(&l,Lock,Unlock));CHECK(s.BeginCodecAttempt());
     CHECK(s.CodecReturnedSuccess());CHECK(s.PublicationGroupVisible());
     CHECK(s.ActiveSnapshotPublished());CHECK(s.Commit());
     CHECK(p.complete && p.phase==policy::Phase::Complete);
     CHECK(!p.terminalRestartRequired && !p.leaseHeld);}
    CHECK(!l.held && l.enters==1 && l.exits==1 && SafeFlags(p));
}
static void KnownPreCodecReject() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.RejectKnownBeforeCodec());CHECK(!p.complete);
     CHECK(p.phase==policy::Phase::RejectedBeforeAttempt);
     CHECK(p.knownRecoverablePrecommitOnly);
     CHECK(p.codecAttempts==0);}
    CHECK(!l.held && l.enters==1 && l.exits==1 && SafeFlags(p));
}
static void RejectAfterAttemptCannotRecover() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(!s.RejectKnownBeforeCodec());
     CHECK(p.terminalRestartRequired && !p.knownRecoverablePrecommitOnly);
     CHECK(!s.Commit());}
    CHECK(!l.held && l.exits==1 && p.codecAttempts==1);
}
static void UnknownDuringCodecAttemptTerminal() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(!s.UnknownFailure());}
    CHECK(p.phase==policy::Phase::TerminalRestartRequired);
    CHECK(!p.complete && p.terminalRestartRequired && !p.leaseHeld);
    CHECK(!l.held && l.exits==1 && SafeFlags(p));
}
static void ThrowDuringCodecAttempt() {
    ++cases;LockProbe l;policy::Receipt p;bool caught=false;
    try{
        policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
        CHECK(s.BeginCodecAttempt());throw std::runtime_error("unknown codec outcome");
    }catch(const std::runtime_error&){caught=true;}
    CHECK(caught && p.terminalRestartRequired);
    CHECK(p.reason==policy::Reason::Abandoned && p.codecAttempts==1);
    CHECK(!l.held && l.exits==1);
}
static void ThrowAfterCodecReturnedSuccess() {
    ++cases;LockProbe l;policy::Receipt p;bool caught=false;
    try{policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
        CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
        throw std::runtime_error("after codec lifecycle");
    }catch(const std::runtime_error&){caught=true;}
    CHECK(caught && p.terminalRestartRequired && !p.complete);
    CHECK(!l.held && l.exits==1);
}
static void ThrowAfterGroupVisible() {
    ++cases;LockProbe l;policy::Receipt p;bool caught=false;
    try{policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
        CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
        CHECK(s.PublicationGroupVisible());throw std::runtime_error("after group");
    }catch(const std::runtime_error&){caught=true;}
    CHECK(caught && p.terminalRestartRequired && !l.held);
    CHECK(p.reason==policy::Reason::Abandoned && l.exits==1);
}
static void ThrowAfterActiveSnapshot() {
    ++cases;LockProbe l;policy::Receipt p;bool caught=false;
    try{policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
        CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
        CHECK(s.PublicationGroupVisible());CHECK(s.ActiveSnapshotPublished());
        throw std::runtime_error("after active");
    }catch(const std::runtime_error&){caught=true;}
    CHECK(caught && p.terminalRestartRequired && !p.complete);
    CHECK(!l.held && l.exits==1);
}
static void IllegalGroupWithoutCodec() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(!s.PublicationGroupVisible());CHECK(p.terminalRestartRequired);}
    CHECK(!l.held && l.exits==1);
}
static void IllegalActiveWithoutGroup() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
     CHECK(!s.ActiveSnapshotPublished());CHECK(!s.Commit());}
    CHECK(p.terminalRestartRequired && !p.complete && l.exits==1);
}
static void AbandonedBeforeAttemptTerminal() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));}
    CHECK(p.terminalRestartRequired && p.codecAttempts==0);
    CHECK(!l.held && l.exits==1);
}
static void AbandonedAfterAttemptTerminal() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());}
    CHECK(p.terminalRestartRequired && p.codecAttempts==1);
    CHECK(!l.held && l.exits==1);
}
static void SameReceiptCannotReopenAfterTerminal() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(!s.UnknownFailure());}
    {policy::Session s(p);CHECK(!s.Enter(&l,Lock,Unlock));
     CHECK(!s.Commit());}
    CHECK(p.terminalRestartRequired && !p.complete && l.enters==1 && l.exits==1);
}
static void SameReceiptCannotReopenAfterSuccess() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
     CHECK(s.PublicationGroupVisible());CHECK(s.ActiveSnapshotPublished());
     CHECK(s.Commit());}
    {policy::Session s(p);CHECK(!s.Enter(&l,Lock,Unlock));}
    CHECK(!p.complete && p.terminalRestartRequired && l.exits==1);
}
static void LockThrowIsNotAValidSuccess() {
    ++cases;LockProbe l;l.throwOnLock=true;policy::Receipt p;
    bool caught=false;
    {policy::Session s(p);
     try{s.Enter(&l,Lock,Unlock);}catch(const std::runtime_error&){caught=true;}}
    CHECK(caught && p.terminalRestartRequired && !p.complete);
    CHECK(!l.held && l.enters==0 && l.exits==0);
}
static void UnknownFailureBeforeCodecIsConservative() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(!s.UnknownFailure());}
    CHECK(p.terminalRestartRequired && !p.knownRecoverablePrecommitOnly);
    CHECK(!l.held && l.exits==1);
}
static void PrecommitRejectCannotBecomeCommit() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.RejectKnownBeforeCodec());
     CHECK(!s.BeginCodecAttempt());CHECK(!s.Commit());}
    CHECK(p.terminalRestartRequired && !p.complete && !l.held && l.exits==1);
    CHECK(p.reason==policy::Reason::InvalidOrder);
}
static void RepeatCodecAttemptTerminal() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(!s.BeginCodecAttempt());}
    CHECK(p.terminalRestartRequired && !l.held && l.exits==1);
}
static void VoidUnknownCannotReportComplete() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
     CHECK(s.PublicationGroupVisible());CHECK(s.ActiveSnapshotPublished());
     CHECK(!s.UnknownFailure());}
    CHECK(!p.complete && p.terminalRestartRequired && SafeFlags(p));
    CHECK(!l.held && l.exits==1);
}
static void FlagsNeverClaimNativeProof() {
    ++cases;LockProbe l;policy::Receipt p;
    {policy::Session s(p);CHECK(s.Enter(&l,Lock,Unlock));
     CHECK(s.BeginCodecAttempt());CHECK(s.CodecReturnedSuccess());
     CHECK(s.PublicationGroupVisible());CHECK(s.ActiveSnapshotPublished());
     CHECK(s.Commit());}
    CHECK(SafeFlags(p));CHECK(p.complete && !p.terminalRestartRequired);
}
int main() {
    NormalComplete();KnownPreCodecReject();RejectAfterAttemptCannotRecover();
    UnknownDuringCodecAttemptTerminal();ThrowDuringCodecAttempt();
    ThrowAfterCodecReturnedSuccess();ThrowAfterGroupVisible();
    ThrowAfterActiveSnapshot();IllegalGroupWithoutCodec();
    IllegalActiveWithoutGroup();AbandonedBeforeAttemptTerminal();
    AbandonedAfterAttemptTerminal();SameReceiptCannotReopenAfterTerminal();
    SameReceiptCannotReopenAfterSuccess();LockThrowIsNotAValidSuccess();
    UnknownFailureBeforeCodecIsConservative();PrecommitRejectCannotBecomeCommit();
    RepeatCodecAttemptTerminal();VoidUnknownCannotReportComplete();
    FlagsNeverClaimNativeProof();
    std::printf("{\"kind\":\"R03B2PublicationFailureBoundaryHost\",\"status\":\"PassedSyntheticOnly\",\"cases\":%u,\"checks\":%u,\"productionIntegrated\":false,\"exceptionSafetyProven\":false,\"realUnity\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",cases,checks);
    return 0;
}
