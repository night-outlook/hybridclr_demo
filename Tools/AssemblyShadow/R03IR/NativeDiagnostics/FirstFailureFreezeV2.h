#pragma once
// R03 B1 HOST-ONLY candidate: preallocated, allocation-free first-error copy.
//
// NOT included in libil2cpp or any Unity Player. This captures a caller-supplied
// actual VM first-error code/detail; it does NOT independently discover the
// first VM error or guarantee a whole-VM diagnostic epoch.
//
// One terminal attempt owns the slot. A malformed first attempt permanently
// freezes Invalid, never authorizing a later "successful" substitute.
// No heap allocation, logging, metadata resolution, locks, string formatting,
// IO, dynamic retry, or managed code in TryFreeze/Read. C++11 only.
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace r03_ir_first_failure_v2 {

static constexpr std::size_t kReasonLimit = 4096;

enum class State : std::uint8_t {
    Empty = 0, Writing = 1, Frozen = 2, Invalid = 3
};

struct Snapshot final {
    std::int32_t code = 0;
    std::size_t length = 0;
    char reason[kReasonLimit + 1] = {};
};

class FirstFailureFreezeV2 final {
    std::atomic<State> state_{State::Empty};
    std::int32_t code_ = 0;
    std::size_t length_ = 0;
    char reason_[kReasonLimit + 1] = {};

    static bool ValidUtf8(const char* raw, std::size_t bytes) noexcept {
        // Use only in-bounds bytes; callers must own the pointer for 'bytes'.
        const auto* p = reinterpret_cast<const std::uint8_t*>(raw);
        for (std::size_t i = 0; i < bytes;) {
            std::uint32_t code = p[i++];
            std::uint32_t minimum = 0;
            unsigned extra = 0;
            if (code < 0x80) {
                if (code == 0) return false; // Embedded NUL cannot be JSON reason.
                continue;
            }
            if (code >= 0xc2 && code <= 0xdf) {
                extra = 1; minimum = 0x80; code &= 0x1f;
            } else if (code >= 0xe0 && code <= 0xef) {
                extra = 2; minimum = 0x800; code &= 0x0f;
            } else if (code >= 0xf0 && code <= 0xf4) {
                extra = 3; minimum = 0x10000; code &= 0x07;
            } else return false;
            if (bytes - i < extra) return false;
            for (unsigned n = 0; n < extra; ++n) {
                const std::uint8_t next = p[i++];
                if ((next & 0xc0) != 0x80) return false;
                code = (code << 6) | (next & 0x3f);
            }
            if (code < minimum || code > 0x10ffff ||
                (code >= 0xd800 && code <= 0xdfff)) return false;
        }
        return true;
    }

public:
    FirstFailureFreezeV2() noexcept = default;
    FirstFailureFreezeV2(const FirstFailureFreezeV2&) = delete;
    FirstFailureFreezeV2& operator=(const FirstFailureFreezeV2&) = delete;

    State status() const noexcept {
        return state_.load(std::memory_order_acquire);
    }

    bool TryFreeze(std::int32_t code, const char* source, std::size_t bytes) noexcept {
        State expected = State::Empty;
        if (!state_.compare_exchange_strong(expected, State::Writing,
                                             std::memory_order_acq_rel,
                                             std::memory_order_acquire)) {
            return false;  // First attempt already owns the slot. Never override.
        }
        if (code <= 0 || !source || bytes == 0 || bytes > kReasonLimit ||
            !ValidUtf8(source, bytes)) {
            state_.store(State::Invalid, std::memory_order_release);
            return false;  // Sticky invalid first error: never fill from a later one.
        }
        code_ = code;
        length_ = bytes;
        std::memcpy(reason_, source, bytes);
        reason_[bytes] = '\0';
        state_.store(State::Frozen, std::memory_order_release);
        return true;
    }

    bool Read(Snapshot& out) const noexcept {
        if (state_.load(std::memory_order_acquire) != State::Frozen)
            return false; // Never observe partial writer data.
        // All fields become immutable before the release-publish of Frozen.
        out.code = code_;
        out.length = length_;
        std::memcpy(out.reason, reason_, length_ + 1);
        return true;
    }
};
static_assert(sizeof(FirstFailureFreezeV2) < 4608,
              "Bounded terminal-first-error latch storage");

} // namespace r03_ir_first_failure_v2
