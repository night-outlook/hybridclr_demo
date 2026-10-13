
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <cassert>
#include <string>
#include <thread>
#define IL2CPP_EXPORT
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
static std::string failure;
static FILE* test_fdopen(int fd,const char* mode){if(failure=="fdopen"){errno=ENOMEM;return nullptr;}return ::fdopen(fd,mode);}
static int test_ferror(FILE* f){if(failure=="write"){errno=EIO;return 1;}return std::ferror(f);}
static int test_fflush(FILE* f){int r=std::fflush(f);if(failure=="flush"){errno=ENOSPC;return -1;}return r;}
static int test_fsync(int fd){if(failure=="fsync"){errno=EIO;return -1;}return ::fsync(fd);}
static int test_fclose(FILE* f){int r=std::fclose(f);if(failure=="close"){errno=EIO;return -1;}return r;}
namespace il2cpp {namespace vm {
enum class AssemblyShadowState{FailedAfterCommit=9};
enum class AssemblyShadowError{Success=0};
struct AssemblyShadow{static AssemblyShadowError GetState(AssemblyShadowState& s){s=AssemblyShadowState::FailedAfterCommit;return AssemblyShadowError::Success;}};
}}
static const char* guardJson="{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":1,\"stateCode\":9,\"extra\":\"entire original producer output retained\"}";
static int R03_ObserveMethod(const char*,const char*,const char*,const char*,int mode,char* out,int capacity){
 assert(mode==3);size_t n=std::strlen(guardJson);assert(n+1<static_cast<size_t>(capacity));std::memcpy(out,guardJson,n+1);return static_cast<int>(n);
}
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
    stream = test_fdopen(fd, "w");
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
    if (test_ferror(stream)) { Reject("write", -1, 13, 0, errno); ok = false; }
    errno = 0;
    if (test_fflush(stream) != 0) { Reject("flush", -1, 14, 0, errno); ok = false; }
    errno = 0;
    if (test_fsync(::fileno(stream)) != 0) { Reject("fsync", -1, 15, 0, errno); ok = false; }
    errno = 0;
    if (test_fclose(stream) != 0) { Reject("close", -1, 16, 0, errno); ok = false; }
    stream = nullptr;
    expected = 3;
    if (!ok || !state.compare_exchange_strong(expected, 2)) return -1;
    std::fprintf(stderr,
        "[R03SnapshotSealed] version=1 pid=%d intMask=%08x textMask=%08x\n",
        static_cast<int>(::getpid()), intMask.load(), textMask.load());
    std::fflush(stderr);
    return 1;
}

namespace r03_ir_observe{static bool UniqueValue(const char* json, const char* key, const char* value) noexcept
{
    if (!json || !key || !value) return false;
    const char* pos = std::strstr(json, key);
    if (!pos || std::strstr(pos + 1, key) != nullptr) return false;
    pos += std::strlen(key);
    const size_t n = std::strlen(value);
    return std::strncmp(pos, value, n) == 0 && (pos[n] == ',' || pos[n] == '}');
}}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ObserveOldGuardIntoSnapshot()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_ir_observe;
    char buffer[16384] = {};
    const int32_t count = R03_ObserveMethod("Methods", "R03", "Node", "Keep", 3,
        buffer, static_cast<int32_t>(sizeof buffer));
    if (count <= 0 || count >= static_cast<int32_t>(sizeof buffer) || buffer[count] != '\0')
        return -1;
    AssemblyShadowState state;
    if (AssemblyShadow::GetState(state) != AssemblyShadowError::Success ||
        state != AssemblyShadowState::FailedAfterCommit ||
        !UniqueValue(buffer, "\"available\":", "true") ||
        !UniqueValue(buffer, "\"activeGuard\":", "1") ||
        !UniqueValue(buffer, "\"baselineGuard\":", "0") ||
        !UniqueValue(buffer, "\"caughtOldGuard\":", "1") ||
        !UniqueValue(buffer, "\"stateCode\":", "9"))
        return -2;
    // Preserve complete original native producer JSON directly into the
    // once-only preopened snapshot. Host independently parses exact fields.
    return R03_IR_ReportText(8, buffer) == 1 ? 1 : -3;
#else
    return 0;
#endif
}
struct Report {
 int initialState=0;
 int poisonedState=0;
 int finalState=0;
 int nativeStimulusReturn=0;
 int preActiveReflection=0;
 int preActiveDelegate=0;
 int preCanaryCount=0;
 int finalCanaryCount=0;
 int preShadowField=0;
 int finalShadowField=0;
 int nativePhase=0;
 int failurePhase=0;
 int terminalReportingProbeMask=0;
 int reserveGcProbeMask=0;
 bool shadowFieldReadable=false;
 bool prePositive=false;
 bool activeReflectionAttempted=false;
 bool activeReflectionSucceeded=false;
 bool activeDelegateAttempted=false;
 bool activeDelegateSucceeded=false;
 bool aotReflectionAttempted=false;
 bool aotReflectionSucceeded=false;
 bool recoveryStable=false;
 bool fixedDiagnosticsReadable=false;
 bool acceptance=false;
 const char* result=nullptr;
 const char* runId=nullptr;
 const char* caseId=nullptr;
 const char* requestSha256=nullptr;
 const char* stimulus=nullptr;
 const char* unityVersion=nullptr;
 const char* platform=nullptr;
 const char* error=nullptr;
 const char* nativeGuardJson=nullptr;
 const char* activeReflectionException=nullptr;
 const char* activeDelegateException=nullptr;
 const char* aotReflectionException=nullptr;
 const char* firstRecovery=nullptr;
 const char* finalRecovery=nullptr;
 const char* finalDiagnostics=nullptr;
 const char* finalExecutionDiagnostics=nullptr;
};
static bool EmitNativeReport(const Report& r)
        {
            bool ok = true;
            ok &= R03_IR_ReportInt(0, r.initialState) == 1;
            ok &= R03_IR_ReportInt(1, r.poisonedState) == 1;
            ok &= R03_IR_ReportInt(2, r.finalState) == 1;
            ok &= R03_IR_ReportInt(3, r.nativeStimulusReturn) == 1;
            ok &= R03_IR_ReportInt(4, r.preActiveReflection) == 1;
            ok &= R03_IR_ReportInt(5, r.preActiveDelegate) == 1;
            ok &= R03_IR_ReportInt(6, r.preCanaryCount) == 1;
            ok &= R03_IR_ReportInt(7, r.finalCanaryCount) == 1;
            ok &= R03_IR_ReportInt(8, r.preShadowField) == 1;
            ok &= R03_IR_ReportInt(9, r.finalShadowField) == 1;
            ok &= R03_IR_ReportInt(10, r.nativePhase) == 1;
            ok &= R03_IR_ReportInt(11, r.failurePhase) == 1;
            ok &= R03_IR_ReportInt(12, r.terminalReportingProbeMask) == 1;
            ok &= R03_IR_ReportInt(13, r.reserveGcProbeMask) == 1;
            ok &= R03_IR_ReportInt(14, r.shadowFieldReadable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(15, r.prePositive ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(16, r.activeReflectionAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(17, r.activeReflectionSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(18, r.activeDelegateAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(19, r.activeDelegateSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(20, r.aotReflectionAttempted ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(21, r.aotReflectionSucceeded ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(22, r.recoveryStable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(23, r.fixedDiagnosticsReadable ? 1 : 0) == 1;
            ok &= R03_IR_ReportInt(24, r.acceptance ? 1 : 0) == 1;
            ok &= R03_IR_ReportText(0, r.result) == 1;
            ok &= R03_IR_ReportText(1, r.runId) == 1;
            ok &= R03_IR_ReportText(2, r.caseId) == 1;
            ok &= R03_IR_ReportText(3, r.requestSha256) == 1;
            ok &= R03_IR_ReportText(4, r.stimulus) == 1;
            ok &= R03_IR_ReportText(5, r.unityVersion) == 1;
            ok &= R03_IR_ReportText(6, r.platform) == 1;
            ok &= R03_IR_ReportText(7, r.error) == 1;
            // Baseline slot 8 was already filled exactly once by the native
            // guard observer. A second write must never mask/corrupt it.
            if (std::strcmp(r.stimulus, "baseline-owner") != 0)
                ok &= R03_IR_ReportText(8, r.nativeGuardJson) == 1;
            ok &= R03_IR_ReportText(9, r.activeReflectionException) == 1;
            ok &= R03_IR_ReportText(10, r.activeDelegateException) == 1;
            ok &= R03_IR_ReportText(11, r.aotReflectionException) == 1;
            ok &= R03_IR_ReportText(12, r.firstRecovery) == 1;
            ok &= R03_IR_ReportText(13, r.finalRecovery) == 1;
            ok &= R03_IR_ReportText(14, r.finalDiagnostics) == 1;
            ok &= R03_IR_ReportText(15, r.finalExecutionDiagnostics) == 1;
            // Call Seal even after a rejected store, so native failure state is
            // observed. It must never seal a failed/missing/duplicate field set.
            int seal = R03_IR_ReportSeal();
            return ok && seal == 1;
        }

int main(int argc,char** argv){
 assert(argc==3); std::string mode=argv[1]; const char* output=argv[2];
 Report r;
 r.initialState=6;r.poisonedState=9;r.finalState=9;r.nativeStimulusReturn=1;
 r.preActiveReflection=42;r.preActiveDelegate=42;r.preCanaryCount=1;r.finalCanaryCount=1;
 r.preShadowField=2;r.finalShadowField=2;r.nativePhase=910;r.failurePhase=0;
 r.terminalReportingProbeMask=15;r.reserveGcProbeMask=31;
 r.shadowFieldReadable=true;r.prePositive=true;r.activeReflectionAttempted=true;r.activeDelegateAttempted=true;r.aotReflectionAttempted=true;
 r.recoveryStable=true;r.fixedDiagnosticsReadable=true;
 r.result="Passed";r.runId="00112233445566778899aabbccddeeff";r.caseId="case-source";
 r.requestSha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 r.stimulus=mode=="baseline"?"baseline-owner":"type-resolution";
 r.unityVersion="2022.3.62f2";r.platform="OSXPlayer";
 r.activeReflectionException=r.activeDelegateException=r.aotReflectionException="ManagedExceptionCaught";
 r.firstRecovery=r.finalRecovery="{\"stateCode\":9,\"terminalFailureCode\":13}";
 r.finalDiagnostics="{\"stateCode\":9}";r.finalExecutionDiagnostics="{\"classes\":[]}";
 bool expect=true;
 if(mode=="no-open"){assert(R03_IR_ReportInt(0,6)==-1);assert(R03_IR_ReportSeal()==-1);return 0;}
 if(mode=="relative-open"){assert(R03_IR_ReportOpen("relative")==-1);return 0;}
 if(mode=="fdopen") failure=mode;
 int openResult=R03_IR_ReportOpen(output);
 if(mode=="fdopen"||mode=="occupied"||mode=="symlink"){assert(openResult==-1);return 0;}
 assert(openResult==1);
 if(mode=="repeat-open"){assert(R03_IR_ReportOpen(output)==-1);return 0;}
 if(mode=="wrong-thread-reentry"){
  r03_ir_snapshot::writerBusy.test_and_set();assert(R03_IR_ReportInt(0,6)==-1);r03_ir_snapshot::writerBusy.clear();assert(R03_IR_ReportSeal()==-1);return 0;
 }
 if(mode=="invalid-int"){assert(R03_IR_ReportInt(25,0)==-1);return 0;}
 if(mode=="invalid-text"){assert(R03_IR_ReportText(-1,nullptr)==-1);return 0;}
 if(mode=="invalid-bool"){assert(R03_IR_ReportInt(24,2)==-1);return 0;}
 if(mode=="duplicate-int"){assert(R03_IR_ReportInt(3,1)==1);assert(R03_IR_ReportInt(3,1)==-1);expect=false;}
 if(mode=="baseline"){assert(R03_IR_ObserveOldGuardIntoSnapshot()==1);}
 if(mode=="duplicate-text") {assert(R03_IR_ObserveOldGuardIntoSnapshot()==1);assert(R03_IR_ObserveOldGuardIntoSnapshot()==-3);expect=false;}
 if(mode=="missing-int"){assert(R03_IR_ReportSeal()==-1);return 0;}
 if(mode=="missing-text"){for(int i=0;i<25;++i)assert(R03_IR_ReportInt(i,0)==1);assert(R03_IR_ReportSeal()==-1);return 0;}
 std::string text;
 if(mode=="at-limit"||mode=="over-limit") {text.assign(mode=="at-limit"?262144:262145,'x');r.finalExecutionDiagnostics=text.c_str();expect=mode=="at-limit";}
 if(mode=="unicode"){r.error="quotes\" backslash\\ newline\n \xe4\xb8\xad\xe6\x96\x87";}
 if(mode=="failed-semantic"){r.result="Failed";r.failurePhase=170;}
 if(mode=="write"||mode=="flush"||mode=="fsync"||mode=="close"){failure=mode;expect=false;}
 if(mode=="off") {r.stimulus="off";r.initialState=r.poisonedState=r.finalState=0;r.terminalReportingProbeMask=r.reserveGcProbeMask=0;r.finalCanaryCount=2;}
 bool ok=EmitNativeReport(r);
 assert(ok==expect);
 if(expect){assert(r03_ir_snapshot::state.load()==2);assert(r03_ir_snapshot::intMask.load()==((1u<<25)-1));assert(r03_ir_snapshot::textMask.load()==((1u<<16)-1));}
 else {assert(r03_ir_snapshot::state.load()==-1);assert(R03_IR_ReportInt(0,99)==-1);assert(R03_IR_ReportSeal()==-1);}
 if(mode=="repeat-seal"){assert(R03_IR_ReportSeal()==-1);}
 return 0;
}
