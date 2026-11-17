#pragma once
// R03 B2 HOST-ONLY publication failure-state candidate. NOT native VM code.
// This is a conservative policy model, NOT actual rollback or exception proof.
// After entering an opaque codec publisher, an unknown failure must never be
// classified as a recoverable precommit rejection without independent proof.
// The caller's Receipt must outlive Session. Lease release is separate from
// transaction atomicity. This model performs no allocation or metadata access.
#include "PublicationUsageLeaseCandidate.h"
#include <cstdint>

namespace r03_b2_publication_failure_boundary {

enum class Phase : uint8_t {
    Idle, UsageHeld, CodecAttempted, CodecReturnedSuccess,
    PublicationGroupVisible, ActiveSnapshotPublished,
    Complete, RejectedBeforeAttempt, TerminalRestartRequired
};
enum class Reason : uint8_t {
    None, KnownPrecommitRejection, UnknownFailure, InvalidOrder,
    Abandoned, LeaseUnavailable
};
struct Receipt {
    Phase phase=Phase::Idle;
    Reason reason=Reason::None;
    unsigned codecAttempts=0;
    bool complete=false;
    bool knownRecoverablePrecommitOnly=false;
    bool terminalRestartRequired=false;
    bool leaseHeld=false;
    // Acceptance indicators are deliberately non-upgradable in this model.
    bool nativeIntegrated=false;
    bool realUnity=false;
    bool realRollbackProven=false;
    bool exceptionSafetyOfNativePublisherProven=false;
    bool R03Accepted=false;
    bool ReadyForHumanReviewGate=false;
};

class Session final {
    r03_b2_usage_lease_candidate::Lease lease_{};
    Receipt& receipt_;
    bool Terminal(Reason why) noexcept {
        const bool alreadyTerminal=receipt_.phase==Phase::TerminalRestartRequired;
        receipt_.complete=false;
        receipt_.knownRecoverablePrecommitOnly=false;
        receipt_.terminalRestartRequired=true;
        receipt_.phase=Phase::TerminalRestartRequired;
        if(!alreadyTerminal)receipt_.reason=why;
        lease_.Release();receipt_.leaseHeld=false;
        return false;
    }
    bool RequirePhase(Phase expected) noexcept {
        return receipt_.phase==expected || Terminal(Reason::InvalidOrder);
    }
public:
    explicit Session(Receipt& receipt) noexcept : receipt_(receipt) {}
    Session(const Session&)=delete;
    Session& operator=(const Session&)=delete;
    ~Session() noexcept {
        if(receipt_.phase!=Phase::Complete &&
           receipt_.phase!=Phase::RejectedBeforeAttempt &&
           receipt_.phase!=Phase::TerminalRestartRequired &&
           receipt_.phase!=Phase::Idle)
            Terminal(Reason::Abandoned);
        lease_.Release();receipt_.leaseHeld=false;
    }
    // A throwing or refused lock cannot certify its own acquisition state.
    bool Enter(void* context,void(*lock)(void*),void(*unlock)(void*)) {
        if(!RequirePhase(Phase::Idle))return false;
        try {
            if(!lease_.Enter(context,lock,unlock))return Terminal(Reason::LeaseUnavailable);
        } catch(...) {
            Terminal(Reason::LeaseUnavailable);
            throw;
        }
        receipt_.leaseHeld=true;
        receipt_.phase=Phase::UsageHeld;
        return true;
    }
    // Only a known rejection BEFORE entering the codec operation is eligible
    // for this synthetic "recoverable precommit" classification.
    bool RejectKnownBeforeCodec() noexcept {
        if(!RequirePhase(Phase::UsageHeld))return false;
        receipt_.phase=Phase::RejectedBeforeAttempt;
        receipt_.reason=Reason::KnownPrecommitRejection;
        receipt_.knownRecoverablePrecommitOnly=true;
        lease_.Release();receipt_.leaseHeld=false;
        return true;
    }
    bool BeginCodecAttempt() noexcept {
        if(!RequirePhase(Phase::UsageHeld))return false;
        receipt_.phase=Phase::CodecAttempted;
        ++receipt_.codecAttempts;
        return true;
    }
    bool CodecReturnedSuccess() noexcept {
        if(!RequirePhase(Phase::CodecAttempted))return false;
        receipt_.phase=Phase::CodecReturnedSuccess;
        return true;
    }
    bool PublicationGroupVisible() noexcept {
        if(!RequirePhase(Phase::CodecReturnedSuccess))return false;
        receipt_.phase=Phase::PublicationGroupVisible;
        return true;
    }
    bool ActiveSnapshotPublished() noexcept {
        if(!RequirePhase(Phase::PublicationGroupVisible))return false;
        receipt_.phase=Phase::ActiveSnapshotPublished;
        return true;
    }
    bool Commit() noexcept {
        if(!RequirePhase(Phase::ActiveSnapshotPublished))return false;
        receipt_.phase=Phase::Complete;
        receipt_.complete=true;
        lease_.Release();receipt_.leaseHeld=false;
        return true;
    }
    // Unknown outcome after BeginCodecAttempt is terminal even if a test
    // injects failure before the first lifecycle write: no external proof of
    // non-publication exists. Conservatism is intentional.
    bool UnknownFailure() noexcept {return Terminal(Reason::UnknownFailure);}
    const Receipt& State() const noexcept {return receipt_;}
};
} // namespace r03_b2_publication_failure_boundary
