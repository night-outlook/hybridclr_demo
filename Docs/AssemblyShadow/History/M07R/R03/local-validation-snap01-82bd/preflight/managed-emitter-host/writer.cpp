#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#define IL2CPP_EXPORT
namespace r03_ir_snapshot {
constexpr size_t TextLimit = 262144;
constexpr const char* IntNames[] = {"initialState","poisonedState","finalState","nativeStimulusReturn","preActiveReflection","preActiveDelegate","preCanaryCount","finalCanaryCount","preShadowField","finalShadowField","nativePhase","failurePhase","terminalReportingProbeMask","reserveGcProbeMask","shadowFieldReadable","prePositive","activeReflectionAttempted","activeReflectionSucceeded","activeDelegateAttempted","activeDelegateSucceeded","aotReflectionAttempted","aotReflectionSucceeded","recoveryStable","fixedDiagnosticsReadable","acceptance"};
constexpr const char* TextNames[] = {"result","runId","caseId","requestSha256","stimulus","unityVersion","platform","error","nativeGuardJson","activeReflectionException","activeDelegateException","aotReflectionException","firstRecovery","finalRecovery","finalDiagnostics","finalExecutionDiagnostics"};
constexpr int IntCount = 25;
constexpr int FirstBool = 14;
constexpr int TextCount = 16;
static std::atomic<int> state{0}; // 0 unused,1 open,2 sealed,3 sealing,-1 failed
static FILE* stream = nullptr;
static int32_t ints[IntCount] = {};
static bool haveInt[IntCount] = {}, haveText[TextCount] = {}, nullText[TextCount] = {};
static char texts[TextCount][TextLimit + 1] = {};
static std::atomic<uint32_t> intMask{0}, textMask{0};
static std::atomic<int> firstFailure{0};
static std::atomic_flag writerBusy = ATOMIC_FLAG_INIT;
// First native failure is supplemental evidence, never a replacement for raw.
// No managed method, dynamic string, new report path or larger limit is used.
static int Reject(const char* operation, int field, int reason, size_t length = 0,
                  int errorNumber = 0) noexcept
{
    const int previous = state.exchange(-1, std::memory_order_acq_rel);
    int expected = 0;
    if (firstFailure.compare_exchange_strong(expected, reason, std::memory_order_acq_rel))
    {
        std::fprintf(stderr,
            "[R03SnapshotFailure] version=1 pid=%d operation=%s field=%d reason=%d previousState=%d length=%zu limit=%zu errno=%d intMask=%08x textMask=%08x\n",
            static_cast<int>(::getpid()), operation, field, reason, previous,
            length, TextLimit, errorNumber, intMask.load(std::memory_order_acquire),
            textMask.load(std::memory_order_acquire));
        std::fflush(stderr);
    }
    return -1;
}
struct WriterCall
{
    bool owns;
    WriterCall() noexcept : owns(!writerBusy.test_and_set(std::memory_order_acquire)) {}
    ~WriterCall() { if (owns) writerBusy.clear(std::memory_order_release); }
};
static void Quote(FILE* f, const char* text)
{
    if (!text) { std::fputs("null", f); return; }
    std::fputc('"', f);
    for (const unsigned char* p = reinterpret_cast<const unsigned char*>(text); *p; ++p)
    {
        if (*p == '"' || *p == '\\') { std::fputc('\\', f); std::fputc(*p, f); }
        else if (*p < 32) std::fprintf(f, "\\u%04x", static_cast<unsigned>(*p));
        else std::fputc(*p, f);
    }
    std::fputc('"', f);
}
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportOpen(const char* path)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("open", -1, 1);
    int expected = 0;
    if (!state.compare_exchange_strong(expected, 1)) return Reject("open", -1, 2);
    if (!path || path[0] != '/') return Reject("open", -1, 3);
    errno = 0;
    int fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (fd < 0) return Reject("open", -1, 4, 0, errno);
    errno = 0;
    stream = ::fdopen(fd, "w");
    if (!stream)
    {
        const int saved = errno;
        ::close(fd);
        return Reject("fdopen", -1, 5, 0, saved);
    }
    return 1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportInt(int32_t field, int32_t value)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("int", field, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("int", field, 2);
    if (field < 0 || field >= IntCount) return Reject("int", field, 6);
    if (haveInt[field]) return Reject("int", field, 7);
    if (field >= FirstBool && value != 0 && value != 1) return Reject("int", field, 8);
    ints[field] = value; haveInt[field] = true;
    intMask.fetch_or(uint32_t(1) << field, std::memory_order_release);
    return state.load(std::memory_order_acquire) == 1 ? 1 : -1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportText(int32_t field, const char* value)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("text", field, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("text", field, 2);
    if (field < 0 || field >= TextCount) return Reject("text", field, 6);
    if (haveText[field]) return Reject("text", field, 7);
    const size_t n = value ? ::strnlen(value, TextLimit + 1) : 0;
    if (n > TextLimit) return Reject("text", field, 9, n);
    if (value) std::memcpy(texts[field], value, n + 1);
    nullText[field] = value == nullptr; haveText[field] = true;
    textMask.fetch_or(uint32_t(1) << field, std::memory_order_release);
    return state.load(std::memory_order_acquire) == 1 ? 1 : -1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportSeal()
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("seal", -1, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("seal", -1, 2);
    if (!stream) return Reject("seal", -1, 10);
    for (int i = 0; i < IntCount; ++i)
        if (!haveInt[i]) return Reject("missing-int", i, 11);
    for (int i = 0; i < TextCount; ++i)
        if (!haveText[i]) return Reject("missing-text", i, 12);
    int expected = 1;
    if (!state.compare_exchange_strong(expected, 3)) return Reject("seal", -1, 2);
    errno = 0;
    std::fprintf(stream, "{\"schemaVersion\":1,\"kind\":\"R03IRPostPoisonEntryV1\","
        "\"reportTransport\":\"NativePreopenedSnapshotV1\",\"processId\":%d", static_cast<int>(::getpid()));
    for (int i = 0; i < IntCount; ++i)
    {
        std::fputc(',', stream); Quote(stream, IntNames[i]); std::fputc(':', stream);
        if (i < FirstBool) std::fprintf(stream, "%d", ints[i]);
        else std::fputs(ints[i] ? "true" : "false", stream);
    }
    for (int i = 0; i < TextCount; ++i)
    {
        std::fputc(',', stream); Quote(stream, TextNames[i]); std::fputc(':', stream);
        Quote(stream, nullText[i] ? nullptr : texts[i]);
    }
    std::fputs("}\n", stream);
    bool ok = true;
    if (std::ferror(stream)) { Reject("write", -1, 13, 0, errno); ok = false; }
    errno = 0;
    if (std::fflush(stream) != 0) { Reject("flush", -1, 14, 0, errno); ok = false; }
    errno = 0;
    if (::fsync(::fileno(stream)) != 0) { Reject("fsync", -1, 15, 0, errno); ok = false; }
    errno = 0;
    if (std::fclose(stream) != 0) { Reject("close", -1, 16, 0, errno); ok = false; }
    stream = nullptr;
    expected = 3;
    if (!ok || !state.compare_exchange_strong(expected, 2)) return -1;
    std::fprintf(stderr,
        "[R03SnapshotSealed] version=1 pid=%d intMask=%08x textMask=%08x\n",
        static_cast<int>(::getpid()), intMask.load(), textMask.load());
    std::fflush(stderr);
    return 1;
}
