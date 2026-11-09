// Actual FirstFailureFreezeV2.h host execution, no fake VM or Unity linkage.
// C++11 and no fallback. Every scenario runs on fresh local stack storage.
#include "FirstFailureFreezeV2.h"
#include <atomic>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <new>
#include <thread>
#include <cstdio>

using namespace r03_ir_first_failure_v2;

static std::atomic<bool> g_counting(false);
static std::atomic<int> g_allocations(0);

void* operator new(std::size_t size) {
    if (g_counting.load(std::memory_order_relaxed))
        g_allocations.fetch_add(1, std::memory_order_relaxed);
    void* p = std::malloc(size ? size : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void* operator new[](std::size_t size) {
    if (g_counting.load(std::memory_order_relaxed))
        g_allocations.fetch_add(1, std::memory_order_relaxed);
    void* p = std::malloc(size ? size : 1);
    if (!p) throw std::bad_alloc();
    return p;
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
#if __cplusplus >= 201402L
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }
#endif

static bool Normal() {
    FirstFailureFreezeV2 state;
    Snapshot received{};
    if (state.status() != State::Empty || state.Read(received))
        return false;
    char detail[] = "ShadowCapturedBaselineType Context=method_inst TypePath=/arg[0]";
    const std::size_t len = sizeof(detail) - 1;
    if (!state.TryFreeze(15, detail, len) || state.status() != State::Frozen)
        return false;
    detail[0] = 'X'; // Caller can now reclaim the original buffer.
    if (!state.Read(received) || received.code != 15 ||
        received.length != len ||
        std::strcmp(received.reason,
                    "ShadowCapturedBaselineType Context=method_inst TypePath=/arg[0]"))
        return false;
    if (state.TryFreeze(19, "replacement", 11) ||
        !state.Read(received) || received.code != 15)
        return false;
    return true;
}

static bool InvalidSticky() {
    FirstFailureFreezeV2 bad;
    Snapshot result{};
    if (bad.TryFreeze(15, nullptr, 4) || bad.status() != State::Invalid ||
        bad.Read(result) || bad.TryFreeze(19, "later", 5))
        return false;
    FirstFailureFreezeV2 zero;
    if (zero.TryFreeze(0, "zero", 4) || zero.status() != State::Invalid ||
        zero.TryFreeze(15, "later", 5))
        return false;
    FirstFailureFreezeV2 empty;
    return !empty.TryFreeze(15, "", 0) &&
           empty.status() == State::Invalid &&
           !empty.Read(result);
}

static bool Utf8() {
    FirstFailureFreezeV2 valid;
    const char msg[] = "Generic type: \xe6\xb5\x8b\xe8\xaf\x95";
    Snapshot snap{};
    if (!valid.TryFreeze(15, msg, sizeof(msg)-1) ||
        !valid.Read(snap) || snap.length != sizeof(msg)-1 ||
        std::memcmp(snap.reason, msg, sizeof(msg)))
        return false;
    FirstFailureFreezeV2 truncated;
    const char bad[] = {'a', char(0xe2), char(0x82)};
    if (truncated.TryFreeze(15, bad, sizeof(bad)) ||
        truncated.status() != State::Invalid)
        return false;
    FirstFailureFreezeV2 nullByte;
    const char nul[] = {'a', '\0', 'b'};
    if (nullByte.TryFreeze(15, nul, sizeof(nul)))
        return false;
    FirstFailureFreezeV2 surrogate;
    const char surrogateText[] = {char(0xed), char(0xa0), char(0x80)};
    return !surrogate.TryFreeze(15, surrogateText, sizeof(surrogateText));
}

static bool Bounds() {
    char full[kReasonLimit + 1]{};
    std::memset(full, 'x', sizeof full);
    FirstFailureFreezeV2 max;
    Snapshot snap{};
    if (!max.TryFreeze(15, full, kReasonLimit) ||
        !max.Read(snap) || snap.length != kReasonLimit ||
        snap.reason[kReasonLimit] != '\0' ||
        snap.reason[kReasonLimit-1] != 'x')
        return false;
    FirstFailureFreezeV2 over;
    return !over.TryFreeze(15, full, kReasonLimit + 1) &&
           over.status() == State::Invalid &&
           !over.Read(snap);
}

static bool Concurrent() {
    FirstFailureFreezeV2 state;
    static constexpr unsigned count = 12;
    std::atomic<unsigned> winners(0);
    std::thread threads[count];
    for (unsigned i = 0; i < count; ++i) {
        threads[i] = std::thread([&state,&winners,i]() {
            char content[] = "writer!";
            content[6] = char('A' + i);
            if (state.TryFreeze(std::int32_t(100 + i), content, sizeof content-1))
                winners.fetch_add(1, std::memory_order_relaxed);
        });
    }
    for (unsigned i = 0; i < count; ++i) threads[i].join();
    Snapshot snap{};
    if (winners.load() != 1 || state.status() != State::Frozen ||
        !state.Read(snap) || snap.code < 100 || snap.code >= std::int32_t(100 + count) ||
        snap.length != 7 || std::memcmp(snap.reason, "writer", 6))
        return false;
    return snap.reason[6] == char('A' + snap.code - 100);
}

static bool NoAlloc() {
    FirstFailureFreezeV2 state;
    Snapshot snap{};
    const char reason[] = "First actual native failure only";
    g_allocations.store(0, std::memory_order_relaxed);
    g_counting.store(true, std::memory_order_release);
    const bool wrote = state.TryFreeze(19, reason, sizeof reason-1);
    const bool read = state.Read(snap);
    g_counting.store(false, std::memory_order_release);
    return wrote && read && snap.code == 19 &&
           g_allocations.load(std::memory_order_acquire) == 0;
}

int main() {
    if (!Normal()) return 11;
    if (!InvalidSticky()) return 12;
    if (!Utf8()) return 13;
    if (!Bounds()) return 14;
    if (!Concurrent()) return 15;
    if (!NoAlloc()) return 16;
    // Exact host-only success marker. No VM source was linked to this binary.
    const char output[] =
        "{\"kind\":\"R03IRFirstFailureFreezeV2Host\","
        "\"result\":\"PassedHostLatchOnly_NotVmOrV2Transport\","
        "\"nativeVmFirstErrorObserved\":false,"
        "\"firstErrorV2Integrated\":false,"
        "\"wholeVmEpochAuthenticated\":false,"
        "\"runtimeAcceptance\":false,\"R03Accepted\":false,\"H2Passed\":false}\n";
    return std::fwrite(output, 1, sizeof output-1, stdout) == sizeof output-1 ? 0 : 17;
}
