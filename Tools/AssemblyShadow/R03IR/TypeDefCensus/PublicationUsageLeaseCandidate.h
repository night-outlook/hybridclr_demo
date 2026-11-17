#pragma once
// R03 B2 TEST-ONLY DESIGN CANDIDATE, NEVER included by libil2cpp.
// Transfer an existing manual UsageLock across two callbacks through a
// context-owned RAII lease, to avoid a permanently held lock on unwinding.
// This lease alone DOES NOT restore atomic publication or convert a partially
// published metadata-index transaction into a rollback-safe operation.
#include <cstddef>

namespace r03_b2_usage_lease_candidate {
class Lease final {
    using Operation=void (*)(void*);
    void* context_=nullptr;
    Operation release_=nullptr;
    bool acquired_=false;
public:
    Lease() noexcept=default;
    Lease(const Lease&)=delete;
    Lease& operator=(const Lease&)=delete;
    ~Lease() noexcept { Release(); }

    // Lock callback may throw. Only mark acquired after it returns normally.
    // Release callback must be noexcept in behavior; a throw in a destructor
    // would terminate. The exact native UnlockUsage is an atomic_flag.clear.
    bool Enter(void* context,Operation lock,Operation release) {
        if(acquired_ || !context || !lock || !release)return false;
        lock(context);
        context_=context;release_=release;acquired_=true;
        return true;
    }
    void Release() noexcept {
        if(!acquired_)return;
        // Clear state first to avoid accidental double-release on reentry.
        acquired_=false;
        Operation release=release_;
        void* context=context_;
        context_=nullptr;release_=nullptr;
        release(context);
    }
    bool Held() const noexcept {return acquired_;}
};
} // namespace r03_b2_usage_lease_candidate
