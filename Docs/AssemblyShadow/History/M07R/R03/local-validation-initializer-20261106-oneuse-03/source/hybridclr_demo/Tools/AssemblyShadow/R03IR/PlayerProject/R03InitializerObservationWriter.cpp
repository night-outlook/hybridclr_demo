// Test-only native initializer V1 writer and independent durable diagnostic journal.
// The diagnostic journal is NOT the strict V1 observation and never grants V2
// transport, R03 acceptance, recovery completeness or executable provenance.
// All post-Commit journal operations use preopened fds and native primitives.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(
    int32_t*, int32_t*, int32_t*, int32_t*, int32_t*);

namespace r03_irw_output {
static std::atomic<int32_t> state{0}; // 0 unused, 1 opened, 2 sealed, -1 invalid
static std::atomic<int32_t> nextSequence{0};
static std::atomic_flag journalBusy = ATOMIC_FLAG_INIT;
static std::atomic<bool> journalBroken{false};
static int fd = -1, journal = -1;
static char runId[96]{}, caseId[96]{}, stimulus[32]{}, digest[65]{};
static const int MAX_EVENTS = 128;

static bool Safe(const char* p, size_t cap, bool isDigest) noexcept {
    if (!p) return false;
    const size_t n = ::strnlen(p, cap);
    if (n == 0 || n == cap || (isDigest && n != 64)) return false;
    for (size_t i = 0; i < n; ++i) {
        const char c = p[i];
        const bool ascii = (c >= 'a' && c <= 'z') ||
                           (c >= 'A' && c <= 'Z') ||
                           (c >= '0' && c <= '9') ||
                           c == '-' || c == '_' || c == '.';
        const bool hex = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
        if (!(isDigest ? hex : ascii)) return false;
    }
    return true;
}

static bool WriteAll(int output, const char* data, size_t n) noexcept {
    unsigned retries = 0;
    while (n) {
        const ssize_t wrote = ::write(output, data, n);
        if (wrote < 0) {
            if (errno == EINTR && ++retries <= 8) continue;
            return false;
        }
        if (wrote == 0 || static_cast<size_t>(wrote) > n) return false;
        data += wrote; n -= static_cast<size_t>(wrote); retries = 0;
    }
    return true;
}

static bool ValidFd(int value) noexcept {
    struct stat info{};
    return value >= 0 && ::fstat(value, &info) == 0 && S_ISREG(info.st_mode) &&
           (info.st_mode & 0777) == 0600 && info.st_nlink == 1;
}

static int32_t Event(int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d) noexcept {
    if (journal < 0 || journalBroken.load(std::memory_order_acquire)) return -1;
    if (journalBusy.test_and_set(std::memory_order_acquire)) {
        journalBroken.store(true, std::memory_order_release);
        return -2;
    }
    const int32_t sequence = nextSequence.fetch_add(1, std::memory_order_relaxed) + 1;
    char line[512];
    const int size = std::snprintf(line, sizeof line,
        "{\"kind\":\"R03IRInitializerNativeTraceV1\","
        "\"runId\":\"%s\",\"caseId\":\"%s\",\"stimulus\":\"%s\","
        "\"fixtureSha256\":\"%s\",\"pid\":%ld,\"seq\":%d,"
        "\"phase\":%d,\"a\":%d,\"b\":%d,\"c\":%d,\"d\":%d,"
        "\"runtimeAcceptance\":false,\"R03Accepted\":false,\"H2Passed\":false}\n",
        runId, caseId, stimulus, digest, static_cast<long>(::getpid()),
        sequence, phase, a, b, c, d);
    const bool valid = sequence <= MAX_EVENTS && size > 0 &&
        static_cast<size_t>(size) < sizeof line &&
        WriteAll(journal, line, static_cast<size_t>(size)) && ::fsync(journal) == 0;
    if (!valid) journalBroken.store(true, std::memory_order_release);
    journalBusy.clear(std::memory_order_release);
    return valid ? 1 : -3;
}

static void CloseOutputs() noexcept {
    if (fd >= 0) { ::close(fd); fd = -1; }
    if (journal >= 0) { ::fsync(journal); ::close(journal); journal = -1; }
}
} // namespace r03_irw_output

// 100-299 managed phase transitions; 300-399 actual prepublication native
// callback decisions; 400-499 actual postpublication primitive read;
// 600-699 native seal inputs/reasons; 900-999 managed catch/finally context.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d) {
    return r03_irw_output::Event(phase, a, b, c, d);
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(
    const char* path, const char* run, const char* caseName,
    const char* mode, const char* sha) {
    using namespace r03_irw_output;
    int32_t expected = 0;
    if (!state.compare_exchange_strong(expected, 1)) return -1;
    static const char suffix[] = ".native-trace.jsonl";
    const size_t pathLen = path ? ::strnlen(path, 4096) : 0;
    if (!path || pathLen < 2 || path[0] != '/' ||
        pathLen + sizeof suffix > 4096 ||
        !Safe(run, sizeof(runId), false) || ::strlen(run) < 24 ||
        !Safe(caseName, sizeof(caseId), false) ||
        !Safe(mode, sizeof(stimulus), false) ||
        !(::strcmp(mode, "initializer-control") == 0 ||
          ::strcmp(mode, "initializer-failure") == 0) ||
        !Safe(sha, sizeof(digest), true)) {
        state.store(-1); return -2;
    }
    // These are fixed validated ASCII strings: never escape arbitrary
    // user-controlled text into JSON or format a managed exception.
    ::strcpy(runId, run); ::strcpy(caseId, caseName);
    ::strcpy(stimulus, mode); ::strcpy(digest, sha);
    char tracePath[4096];
    std::memcpy(tracePath, path, pathLen);
    std::memcpy(tracePath + pathLen, suffix, sizeof suffix);
    journal = ::open(tracePath, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (!ValidFd(journal)) {
        CloseOutputs(); state.store(-1); return -3;
    }
    if (Event(100, 1, 0, 0, 0) != 1) {
        CloseOutputs(); state.store(-1); return -4;
    }
    fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (!ValidFd(fd)) {
        Event(101, -5, errno, 0, 0);
        CloseOutputs(); state.store(-1); return -5;
    }
    if (Event(101, 1, 0, 0, 0) != 1) {
        CloseOutputs(); state.store(-1); return -6;
    }
    return 1;
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(
    int32_t commit, int32_t finalState, int32_t canaryBefore,
    int32_t canaryAfter, int32_t attempted, int32_t succeeded) {
    using namespace r03_irw_output;
    const int32_t started = Event(600, commit, finalState, attempted, succeeded);
    Event(601, canaryBefore, canaryAfter, 0, 0);
    int32_t expected = 1;
    if (!state.compare_exchange_strong(expected, -1) || fd < 0) {
        Event(610, -1, expected, fd, 0);
        CloseOutputs(); return -1;
    }
    int32_t field = -1, preField = -1, ready = -1, mask = -1, calls = -1;
    const int32_t observed = R03_IRW_ReadPrepared(&field, &preField, &ready, &mask, &calls);
    Event(602, observed, field, preField, ready);
    Event(603, mask, calls, 0, 0);
    const bool control = ::strcmp(stimulus, "initializer-control") == 0;
    int32_t reason = 0;
    if (observed != 1) reason = 1;
    else if (field != 3 || preField != 3 || ready != 1) reason = 2;
    else if (mask != 15 || calls != 1) reason = 3;
    else if (canaryBefore != 1 || canaryAfter != 1 || succeeded != 0) reason = 4;
    else if (control ? (commit != 0 || finalState != 6 || attempted != 0)
                     : (commit != 19 || finalState != 9 || attempted != 1)) reason = 5;
    if (started != 1 || journalBroken.load(std::memory_order_acquire)) reason = 6;
    if (reason) {
        Event(610, -2, reason, observed, 0);
        CloseOutputs(); return -2;
    }
    char raw[2048];
    const int len = std::snprintf(raw, sizeof raw,
        "{\"schemaVersion\":1,\"kind\":\"R03IRInitializerCommitObservationV1\","
        "\"reportTransport\":\"NativePreopenedInitializerObservationV1\","
        "\"result\":\"ObservedNotAccepted\",\"runId\":\"%s\","
        "\"caseId\":\"%s\",\"stimulus\":\"%s\","
        "\"fixtureSha256\":\"%s\",\"processId\":%ld,"
        "\"commitReturn\":%d,\"finalState\":%d,"
        "\"nativeObserverBoundBeforeFailure\":true,\"preparedField\":%d,"
        "\"finalField\":%d,\"positiveMask\":%d,\"initializerCallbackCalls\":%d,"
        "\"postAotAttempted\":%s,\"postAotSucceeded\":false,"
        "\"firstRecoveryAuthenticated\":false,\"completeDiagnosticsAuthenticated\":false,"
        "\"nativeV2TransportImplemented\":false,\"runtimeAcceptance\":false,"
        "\"R03Accepted\":false,\"H2Passed\":false}\n",
        runId, caseId, stimulus, digest, static_cast<long>(::getpid()),
        commit, finalState, preField, field, mask, calls,
        attempted ? "true" : "false");
    if (len <= 0 || static_cast<size_t>(len) >= sizeof raw ||
        !WriteAll(fd, raw, static_cast<size_t>(len)) ||
        ::fsync(fd) != 0 || ::close(fd) != 0) {
        fd = -1;
        Event(610, -3, len, errno, 0);
        CloseOutputs(); return -3;
    }
    fd = -1;
    if (Event(620, 1, commit, finalState, observed) != 1) {
        CloseOutputs(); return -4;
    }
    if (::close(journal) != 0) {
        journal = -1; return -5;
    }
    journal = -1;
    state.store(2, std::memory_order_release);
    return 1;
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(
    const char*, const char*, const char*, const char*, const char*) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t, int32_t, int32_t, int32_t, int32_t) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(
    int32_t,int32_t,int32_t,int32_t,int32_t,int32_t) { return 0; }
#endif
