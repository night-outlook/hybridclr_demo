#pragma once
// Executable DESIGN CONTRACT, NOT a Unity scheduler adapter or method guard.
// An engine owner must prove the safe point and native-maintenance semantics.
#include <array>
#include <atomic>
#include <cstdint>

namespace r03_boundary {
using Digest = std::array<std::uint8_t, 32>;
enum class Phase : int { Unbound, Prepared, Publishing, Requested, Acknowledged, Ready, Failed };
enum class Verdict : int { Pending, ReadyForRestart, Failed };
constexpr std::uint32_t MaintenanceRequired = 0x0fu; // pump, GC service, IO, control channel
constexpr std::uint64_t WindowNs = 500000000ull;
inline bool Nonzero(const Digest& d) noexcept {
    std::uint8_t v = 0; for (auto b : d) v |= b; return v != 0;
}

class Coordinator final {
    std::atomic<Phase> phase_{Phase::Unbound};
    Digest owner_{};
    std::uint64_t baseline_ = 0, generation_ = 0, start_ = 0;
    std::uint64_t latest_ = 0, ack_ = 0, pulse_ = 0, pulseCount_ = 0, lastClock_ = 0;
    std::uint32_t cause_ = 0;
    std::atomic<bool> lateManaged_{false};
    bool finished_ = false;

    bool Fail() noexcept { phase_.store(Phase::Failed, std::memory_order_release); return false; }
    bool Owner(const Digest& d) const noexcept { return d == owner_; }
public:
    // Healthy startup, before publishing this object to callback threads. The
    // digest binds the reviewed adapter/module/build/instance; a hash alone is
    // NOT permission to trust an arbitrary pointer or unreviewed native owner.
    bool Prepare(const Digest& verifiedOwner, std::uint64_t baselineReports) noexcept {
        if (!Nonzero(verifiedOwner) || phase_.load() != Phase::Unbound) return false;
        owner_ = verifiedOwner; baseline_ = latest_ = baselineReports;
        phase_.store(Phase::Prepared, std::memory_order_release); return true;
    }
    // Callback-safe single publication: no allocator, lock, logger, engine call,
    // managed callback, OS thread suspension or counter mutation. Losers never
    // overwrite the first cause, timestamp or generation.
    bool Request(std::uint32_t cause, std::uint64_t generation, std::uint64_t monotonicNs) noexcept {
        if (!cause || !generation) return false;
        Phase expected = Phase::Prepared;
        if (!phase_.compare_exchange_strong(expected, Phase::Publishing, std::memory_order_acq_rel))
            return false;
        cause_ = cause; generation_ = generation; start_ = lastClock_ = monotonicNs;
        phase_.store(Phase::Requested, std::memory_order_release); return true;
    }
    // Called by the REAL scheduler before admission, not by Runtime::Invoke to
    // fabricate a benign return from an already-dispatched managed method.
    bool MayScheduleManaged() const noexcept { return phase_.load(std::memory_order_acquire) == Phase::Prepared; }
    void RecordLateManagedDispatch() noexcept { lateManaged_.store(true, std::memory_order_release); }

    // Owner thread only, after completing/cancelling in-flight engine work at a
    // supported safe point. The adapter must provide independent evidence that
    // these fields describe reality, not merely set bits to pass this model.
    bool Acknowledge(const Digest& owner, std::uint64_t generation,
                     std::uint64_t epoch, std::uint32_t activeManaged,
                     std::uint32_t maintenanceMask, std::uint64_t now) noexcept {
        if (phase_.load(std::memory_order_acquire) != Phase::Requested) return false;
        if (!Owner(owner) ||
            generation != generation_ || !epoch || activeManaged != 0 ||
            maintenanceMask != MaintenanceRequired || now < start_ || lateManaged_.load()) return Fail();
        ack_ = epoch; lastClock_ = now;
        phase_.store(Phase::Acknowledged, std::memory_order_release); return true;
    }
    bool Pulse(const Digest& owner, std::uint64_t epoch, std::uint64_t pulseSequence,
               std::uint32_t maintenanceMask, std::uint64_t now) noexcept {
        if (phase_.load(std::memory_order_acquire) != Phase::Acknowledged) return false;
        if (!Owner(owner) ||
            epoch != ack_ || pulseSequence != pulse_ + 1 || maintenanceMask != MaintenanceRequired ||
            now < lastClock_ || lateManaged_.load()) return Fail();
        pulse_ = pulseSequence; ++pulseCount_; lastClock_ = now; return true;
    }
    // Read-only observation of the ORIGINAL uncapped native reporting counter.
    // Even 51213 is retained as observed; this object does not suppress reports.
    bool Sample(std::uint64_t actualCompletedCounter) noexcept {
        const auto p = phase_.load(std::memory_order_acquire);
        if (p != Phase::Requested && p != Phase::Acknowledged) return false;
        if (actualCompletedCounter < latest_) return Fail();
        latest_ = actualCompletedCounter; return true;
    }
    Verdict Evaluate(const Digest& owner, std::uint64_t now,
                     const Digest& durableCompleteSnapshot, bool fsyncComplete) noexcept {
        const auto phase = phase_.load(std::memory_order_acquire);
        if (phase == Phase::Failed) return Verdict::Failed;
        if (phase == Phase::Unbound || phase == Phase::Prepared || phase == Phase::Publishing)
            return Verdict::Pending;
        if (phase == Phase::Ready) return Verdict::ReadyForRestart;
        if (!Owner(owner) || now < start_ || now < lastClock_ || lateManaged_.load()) {
            Fail(); return Verdict::Failed;
        }
        if (now - start_ < WindowNs) return Verdict::Pending;
        if (phase_.load(std::memory_order_acquire) != Phase::Acknowledged || pulseCount_ < 2 ||
            latest_ < baseline_ || latest_ - baseline_ < 1 || latest_ - baseline_ > 64 ||
            !Nonzero(durableCompleteSnapshot) || !fsyncComplete) {
            Fail(); return Verdict::Failed;
        }
        finished_ = true; phase_.store(Phase::Ready, std::memory_order_release);
        return Verdict::ReadyForRestart;
    }
    // Called only after real native teardown and supervisor creation of a new
    // process; this contract performs NEITHER operation and approves no cleanup.
    bool BindRestart(std::uint64_t oldPid, std::uint64_t newPid,
                     const Digest& oldRun, const Digest& newRun) const noexcept {
        return finished_ && phase_.load(std::memory_order_acquire) == Phase::Ready &&
            oldPid && newPid && oldPid != newPid && Nonzero(oldRun) && Nonzero(newRun) && oldRun != newRun;
    }
    Phase State() const noexcept { return phase_.load(std::memory_order_acquire); }
    std::uint64_t ReportsObserved() const noexcept { return latest_ - baseline_; }
    std::uint32_t FirstCause() const noexcept {
        const auto p = phase_.load(std::memory_order_acquire);
        return (p == Phase::Unbound || p == Phase::Prepared || p == Phase::Publishing) ? 0 : cause_;
    }
};
} // namespace r03_boundary
