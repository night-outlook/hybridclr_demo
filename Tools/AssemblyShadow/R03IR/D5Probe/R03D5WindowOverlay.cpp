// R03 D5 C10 ONLY: native P5 witness and fail-closed, preopened evidence.
// This is a test-only Player source, not a normal Unity/libil2cpp component.
// A completed file is source-host material until a real binary/PID is audited.
#include "il2cpp-config.h"
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <chrono>

#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
#include "vm/AssemblyShadowD5WindowProbe.h"
#endif
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
#include "vm/AssemblyShadow.h"
#include "vm/Class.h"
#include "gc/GCHandle.h"
#include "il2cpp-object-internals.h"
#include "il2cpp-class-internals.h"
#endif

#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
namespace r03_d5_evidence
{
static const uint32_t kMagic = 0xC105D5E1u;
static const int32_t kSlots = 10;
// Explicit fixed native layout: no C++ objects, pointers or ABI-sized fields.
struct Header final
{
    char magic[8]; // "D5C10E1!"
    int32_t schema;
    int32_t pid;
    char runId[64];
    char requestSha256[64];
    char fixtureSha256[64];
    int32_t reserved;
};
struct Event final
{
    uint32_t magic;
    int32_t slot;
    int32_t a, b, c, d;
    uint32_t checksum;
    uint32_t size;
};
struct FirstErrorDisk final
{
    uint32_t magic;
    int32_t status;
    int32_t code;
    int32_t origin;
    int32_t reasonLength;
    char reason[4097];
};
static_assert(sizeof(Header) == 212, "D5 evidence header layout");
static_assert(sizeof(Event) == 32, "D5 evidence event layout");
static_assert(sizeof(FirstErrorDisk) == 4120, "D5 evidence first error layout");
static const off_t kFirstErrorOffset = static_cast<off_t>(sizeof(Header) + kSlots * sizeof(Event));
static std::atomic<int32_t> stage{0}; // 0 unused, 1 opening, 2 open, 3 sealed, -1 failed
static std::atomic<uint32_t> slots{0};
static int fd = -1;
static int32_t canaryBefore = -1;
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
// Explicitly SYNTHETIC source-host inputs, never a real IL2CPP VM source.
static std::atomic<int32_t> hostState{5}, hostAfter{0}, hostBound{0};
static std::atomic<int32_t> hostFrozen{0}, hostCompleted{0};
#endif
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
static int32_t canaryOffset = -1;
static uint32_t pinnedObject = 0; // never freed before isolated test process exit
static Il2CppObject* pinnedInstance = nullptr;
static const MethodInfo* boundKeepMethod = nullptr;
static std::atomic<int32_t> canaryReady{0};
#endif

static bool AsciiId(const char* raw) noexcept
{
    if (!raw) return false;
    int32_t i = 0;
    for (; i < 63 && raw[i]; ++i)
    {
        const char c = raw[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '-' || c == '_')) return false;
    }
    return i > 0 && i < 63 && raw[i] == 0;
}
static bool Hex64(const char* raw) noexcept
{
    if (!raw) return false;
    for (int32_t i = 0; i < 64; ++i)
    {
        const char c = raw[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return raw[64] == 0;
}
static bool PWriteAll(off_t offset, const void* source, size_t bytes) noexcept
{
    const char* data = static_cast<const char*>(source);
    unsigned interrupts = 0;
    while (bytes)
    {
        const ssize_t n = ::pwrite(fd, data, bytes, offset);
        if (n < 0 && errno == EINTR && ++interrupts < 8) continue;
        if (n <= 0 || static_cast<size_t>(n) > bytes) return false;
        data += n; bytes -= static_cast<size_t>(n); offset += n;
        interrupts = 0;
    }
    return true;
}
static int32_t Record(int32_t slot, int32_t a, int32_t b, int32_t c, int32_t d) noexcept
{
    if (stage.load(std::memory_order_acquire) != 2 || slot < 1 || slot > kSlots) return -1;
    const uint32_t bit = 1u << static_cast<uint32_t>(slot - 1);
    if (slots.fetch_or(bit, std::memory_order_acq_rel) & bit) return -2;
    Event record{};
    record.magic = kMagic; record.slot = slot;
    record.a = a; record.b = b; record.c = c; record.d = d;
    record.checksum = kMagic ^ static_cast<uint32_t>(slot) ^
        static_cast<uint32_t>(a) ^ static_cast<uint32_t>(b) ^
        static_cast<uint32_t>(c) ^ static_cast<uint32_t>(d);
    record.size = sizeof(Event);
    const off_t offset = static_cast<off_t>(sizeof(Header) + (slot - 1) * sizeof(Event));
    return PWriteAll(offset, &record, sizeof record) && ::fsync(fd) == 0 ? 1 : -3;
}
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
static bool ReadCanary(int32_t& value) noexcept
{
    if (canaryReady.load(std::memory_order_acquire) != 1)
        return false;
    // The prior pinned native GC root and release/acquire boundReady ordering
    // make this a fixed primitive memory read: no GetTarget/GC/VM callback after
    // a possible terminal guard or during the detached writer's finalization.
    const Il2CppObject* object = pinnedInstance;
    if (!pinnedObject || !object ||
        canaryOffset < static_cast<int32_t>(sizeof(Il2CppObject)) ||
        static_cast<uint64_t>(canaryOffset) + sizeof(int32_t) > object->klass->instance_size)
        return false;
    std::memcpy(&value, reinterpret_cast<const uint8_t*>(object) + canaryOffset, sizeof value);
    return true;
}
#endif

// D5-C10-only native-owned terminal receipt. The collector thread is started
// exactly once, before Configure/Stage/Commit, when managed runtime is healthy.
// It does not acquire transaction, metadata or usage locks, allocate managed
// objects, invoke callbacks, or wait inside a method guard. After a finite
// deadline it writes a complete source-material record (NoCoverage on missing
// phase/attempt/guard), then terminates this isolated test Player natively.
// The full VM/GC branch remains uncompiled in source-host CI.
#if (HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) || (defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO)
static int32_t FinishNativeReceipt(int32_t stateCode, int32_t decision) noexcept
{
    using il2cpp::vm::assembly_shadow_d5::WindowProbe;
    const auto window = WindowProbe::Instance().Read();
    if (Record(6, -1, stateCode, 1, WindowProbe::Instance().TargetArmCount()) != 1 ||
        Record(7, window.shadowMethodAttemptsInP5,
               window.shadowMethodAllowedInP5,
               window.shadowMethodDeniedInP5, window.methodResultRacedP6) != 1 ||
        Record(8, window.p5Count, window.p6Count,
               window.timedOut, window.releaseCount) != 1)
        return -2;
    int32_t after = -1;
    int32_t valid = 0;
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
    valid = hostBound.load(std::memory_order_acquire) == 1 ? 1 : 0;
    after = valid ? hostAfter.load(std::memory_order_acquire) : -1;
#else
    valid = ReadCanary(after) ? 1 : 0;
#endif
    if (Record(9, canaryBefore, after, valid, 0) != 1)
        return -3;
    FirstErrorDisk error{};
    error.magic = kMagic;
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
    // Explicit mock first-error bytes to test native writer serialization
    // with ZERO claim to VM origin, terminal behavior or real Player.
    if (hostFrozen.load(std::memory_order_acquire) == 1)
    {
        static const char text[] = "synthetic Keep terminal source host";
        error.status = 2; error.code = 21; error.origin = 1;
        error.reasonLength = static_cast<int32_t>(sizeof text - 1);
        std::memcpy(error.reason, text, sizeof text);
    }
#else
    using il2cpp::vm::assembly_shadow_first_failure_v2::State;
    using il2cpp::vm::assembly_shadow_first_failure_v2::Snapshot;
    const State nativeError = il2cpp::vm::AssemblyShadow::FirstFailureV2Status();
    error.status = static_cast<int32_t>(nativeError);
    if (nativeError == State::Frozen)
    {
        Snapshot snapshot{};
        if (!il2cpp::vm::AssemblyShadow::TryReadFirstFailureV2(snapshot) ||
            snapshot.length > 4096)
            return -4;
        error.code = snapshot.code;
        error.origin = static_cast<int32_t>(snapshot.origin);
        error.reasonLength = static_cast<int32_t>(snapshot.length);
        std::memcpy(error.reason, snapshot.reason, snapshot.length + 1);
    }
#endif
    if (!PWriteAll(kFirstErrorOffset, &error, sizeof error) ||
        Record(10, 1, valid, decision, 1) != 1 ||
        ::fsync(fd) != 0)
        return -5;
    stage.store(3, std::memory_order_release);
    const int savedFd = fd;
    return ::close(savedFd) == 0 ? 1 : -6;
}

static void* NativeCollector(void*) noexcept
{
    using il2cpp::vm::assembly_shadow_d5::WindowProbe;
    using il2cpp::vm::assembly_shadow_d5::WindowPhase;
    WindowProbe& probe = WindowProbe::Instance();
    bool sawP5 = false, sawCanary = false, sawAttempt = false, sawGuard = false;
    const auto start = std::chrono::steady_clock::now();
    for (;;)
    {
        const auto now = std::chrono::steady_clock::now();
        const auto elapsedMs = std::chrono::duration_cast<
            std::chrono::milliseconds>(now - start).count();
        const auto witness = probe.Read();
        if (!sawP5 && witness.p5Count == 1)
        {
            sawP5 = Record(2, 2, witness.p5Count, 0, 0) == 1;
        }
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
        if (!sawCanary && hostBound.load(std::memory_order_acquire) == 1)
        {
            canaryBefore = 0; // synthetic only
            sawCanary = Record(3, canaryBefore, 32, 1, 0) == 1;
        }
#else
        if (!sawCanary && canaryReady.load(std::memory_order_acquire) == 1)
        {
            sawCanary = Record(3, canaryBefore, canaryOffset, 1, 0) == 1;
        }
#endif
        if (!sawAttempt && probe.TargetArmCount() == 1)
        {
            sawAttempt = Record(4, 1, 1, 0, 0) == 1;
        }
        const int32_t decision = probe.TargetDecision();
        if (!sawGuard && decision != 0)
        {
            // Slot 5 is the *native same-thread method-guard completion*,
            // not a managed Invoke return (which may be terminal-denied).
            sawGuard = Record(5, decision, 1, 1, 0) == 1;
        }
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
        const int32_t stateCode = hostState.load(std::memory_order_acquire);
#else
        il2cpp::vm::AssemblyShadowState state{};
        const int32_t stateCode =
            il2cpp::vm::AssemblyShadow::GetState(state) ==
                il2cpp::vm::AssemblyShadowError::Success
                ? static_cast<int32_t>(state) : -1;
#endif
        const bool terminal = stateCode == 8 || stateCode == 9;
        const bool released = witness.releaseCount != 0 ||
            witness.p6Count != 0 ||
            witness.phase >= static_cast<int32_t>(WindowPhase::AtP6);
        const bool terminalDenied = decision == 2 && terminal;
        const bool allowedCompleted = decision == 1 && released;
        const bool racedCompleted = decision == 3 && released;
        if (terminalDenied || allowedCompleted || racedCompleted ||
            elapsedMs >=
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
                500
#else
                8000
#endif
            )
        {
            // All disk work is from THIS prestarted independent native thread,
            // outside the publication and method-entry critical locks.
            const int32_t sealed = FinishNativeReceipt(stateCode, decision);
            // Never report an authenticated Player pass from a source-only
            // fixture. The actual binary/PID must be externally checked.
            // 42 denotes an admitted P5 guard; 0 is only a native receipt
            // candidate, and 2 means incomplete/failing source material.
            const int32_t status = sealed == 1 &&
                decision == 1 ? 42 :
                sealed == 1 && terminalDenied && sawP5 && sawCanary &&
                sawAttempt && sawGuard ? 0 : 2;
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
            (void)status;
            hostCompleted.store(1, std::memory_order_release);
            return nullptr; // host test binary continues to verify exact file
#else
            ::_exit(status); // isolated C10-only disposable Player
#endif
        }
        ::usleep(1000); // outside all VM critical locks, finite 8s deadline
    }
}
#endif
} // namespace r03_d5_evidence
#endif

extern "C" IL2CPP_EXPORT int32_t R03_D5_WindowProtocolVersion()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return 1;
#else
    return 0;
#endif
}
extern "C" IL2CPP_EXPORT int32_t R03_D5_ArmP5Window(int32_t waitMilliseconds)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().Arm(waitMilliseconds) ? 1 : -1;
#else
    (void)waitMilliseconds;
    return 0;
#endif
}
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReleaseP5Window()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().ReleaseP5() ? 1 : -1;
#else
    return 0;
#endif
}
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReadP5Window(int32_t* destination, int32_t count)
{
    if (!destination || count != 11) return -2;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    using il2cpp::vm::assembly_shadow_d5::WindowProbe;
    using il2cpp::vm::assembly_shadow_d5::WindowSnapshot;
    static_assert(sizeof(WindowSnapshot) == sizeof(int32_t) * 11,
        "Native/managed D5 witness wire fields changed");
    const WindowSnapshot value = WindowProbe::Instance().Read();
    std::memcpy(destination, &value, sizeof value);
    return 1;
#else
    for (int32_t i=0; i<count; ++i) destination[i] = 0;
    return 0;
#endif
}

// Must run while managed runtime is healthy; no outputs can be reopened.
// Native writes after poisoning use only fixed structs, pwrite, fsync, close.
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReceiptOpen(
    const char* path, const char* runId, const char* requestSha256, const char* fixtureSha256)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    using namespace r03_d5_evidence;
    int32_t expected = 0;
    if (!stage.compare_exchange_strong(expected, 1, std::memory_order_acq_rel)) return -1;
    if (!path || path[0] != '/' || ::strnlen(path, 4096) >= 4096 ||
        !AsciiId(runId) || !Hex64(requestSha256) || !Hex64(fixtureSha256))
    { stage.store(-1, std::memory_order_release); return -2; }
    fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (fd < 0) { stage.store(-1, std::memory_order_release); return -3; }
    Header header{};
    std::memcpy(header.magic, "D5C10E1!", sizeof header.magic);
    header.schema = 1;
    header.pid = static_cast<int32_t>(::getpid());
    std::memcpy(header.runId, runId, std::strlen(runId));
    std::memcpy(header.requestSha256, requestSha256, 64);
    std::memcpy(header.fixtureSha256, fixtureSha256, 64);
    if (!PWriteAll(0, &header, sizeof header) || ::fsync(fd) != 0)
    { ::close(fd); fd = -1; stage.store(-1, std::memory_order_release); return -4; }
    stage.store(2, std::memory_order_release);
#if (HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) || (defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO)
    pthread_t nativeCollector{};
    const int threadResult = ::pthread_create(
        &nativeCollector, nullptr, &r03_d5_evidence::NativeCollector, nullptr);
    if (threadResult != 0)
    {
        stage.store(-1, std::memory_order_release);
        ::close(fd);
        return -5; // precommit failure, no fallback to managed postterminal I/O
    }
    ::pthread_detach(nativeCollector);
#endif
    return 1;
#else
    (void)path; (void)runId; (void)requestSha256; (void)fixtureSha256;
    return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_D5_ReceiptEvent(
    int32_t slot, int32_t a, int32_t b, int32_t c, int32_t d)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return r03_d5_evidence::Record(slot,a,b,c,d);
#else
    (void)slot; (void)a; (void)b; (void)c; (void)d;
    return 0;
#endif
}

// Bind the genuine R03.Node.stable field. The managed worker holds a GCHandle
// through this call; the test-only native pinned root survives terminal state.
// No fabricated MethodInfo, no cctor invocation or managed field reads.
extern "C" IL2CPP_EXPORT int32_t R03_D5_BindKeepCanary(void* handle)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
    using namespace r03_d5_evidence;
    if (stage.load(std::memory_order_acquire) != 2 || pinnedObject ||
        !handle || reinterpret_cast<uintptr_t>(handle) > UINT32_MAX ||
        il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().MethodBegin() != 2) return -1;
    Il2CppObject* object = il2cpp::gc::GCHandle::GetTarget(
        static_cast<uint32_t>(reinterpret_cast<uintptr_t>(handle)));
    if (!object || !object->klass || !object->klass->image ||
        !object->klass->image->assembly || !object->klass->image->assembly->aname.name ||
        !object->klass->namespaze || !object->klass->name ||
        std::strcmp(object->klass->image->assembly->aname.name, "Methods") ||
        std::strcmp(object->klass->namespaze, "R03") ||
        std::strcmp(object->klass->name, "Node") ||
        !il2cpp::vm::AssemblyShadow::IsActiveShadow(object->klass->image->assembly)) return -2;
    const FieldInfo* stable = il2cpp::vm::Class::GetFieldFromName(object->klass, "stable");
    if (!stable || stable->parent != object->klass || !stable->type ||
        stable->type->type != IL2CPP_TYPE_I4 ||
        (stable->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        stable->offset < static_cast<int32_t>(sizeof(Il2CppObject)) ||
        static_cast<uint64_t>(stable->offset) + sizeof(int32_t) > object->klass->instance_size)
        return -3;
    const uint32_t rooted = il2cpp::gc::GCHandle::New(object, true);
    if (!rooted) return -4;
    const MethodInfo* keep = il2cpp::vm::Class::GetMethodFromName(
        object->klass, "Keep", 0);
    if (!keep || keep->klass != object->klass) return -5;
    pinnedObject = rooted;
    pinnedInstance = object;
    boundKeepMethod = keep;
    canaryOffset = stable->offset;
    int32_t value = -1;
    std::memcpy(&value, reinterpret_cast<const uint8_t*>(object) +
        canaryOffset, sizeof value);
    if (value != 0) return -6;
    canaryBefore = value;
    canaryReady.store(1, std::memory_order_release);
    return 1; // disk event 3 belongs to the prestarted native collector
#else
    (void)handle;
    return 0; // host and feature-OFF cannot claim a real native VM canary
#endif
}


// Source-host-only C ABI for deterministic native autoseal tests. These are
// deliberately never compiled into a Unity Player and cannot claim VM data.
#if defined(HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO) && HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO
extern "C" IL2CPP_EXPORT int32_t R03_D5_SourceHostAutoConfigure(
    int32_t state, int32_t after, int32_t bound, int32_t frozen)
{
    using namespace r03_d5_evidence;
    hostAfter.store(after, std::memory_order_release);
    hostBound.store(bound, std::memory_order_release);
    hostFrozen.store(frozen, std::memory_order_release);
    hostState.store(state, std::memory_order_release);
    return 1;
}
extern "C" IL2CPP_EXPORT int32_t R03_D5_SourceHostAutoDone()
{
    return r03_d5_evidence::hostCompleted.load(std::memory_order_acquire);
}
#endif

// Called once on the C10 worker thread immediately before MethodInfo.Invoke.
// The bound native method pointer and TLS live in the exact header shared
// with AssemblyShadow::AssertMethodIsActive. No syscall, managed callback,
// allocation or VM lock is performed here.
extern "C" IL2CPP_EXPORT int32_t R03_D5_BeginKeepAttempt()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
    using namespace r03_d5_evidence;
    if (stage.load(std::memory_order_acquire) != 2 ||
        canaryReady.load(std::memory_order_acquire) != 1 ||
        !boundKeepMethod)
        return -1;
    return il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().
        ArmTargetForCurrentThread(boundKeepMethod) ? 1 : -2;
#else
    return 0;
#endif
}

// Source-host writer semantics are testable independently. A real Player's
// first-error bytes are captured from the existing B1 immutable native source.
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReceiptSeal(
    int32_t commitCode, int32_t stateCode, int32_t workerFinished, int32_t keepAttempted)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    using namespace r03_d5_evidence;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
    // A real Player never seals from managed code after potential poison.
    // NativeCollector is the only owner of the evidence finish/exit.
    (void)commitCode; (void)stateCode; (void)workerFinished; (void)keepAttempted;
    return -7;
#else
    if (stage.load(std::memory_order_acquire) != 2 || workerFinished != 1) return -1;
#endif
    using il2cpp::vm::assembly_shadow_d5::WindowProbe;
    const auto native = WindowProbe::Instance().Read();
    if (Record(6, commitCode, stateCode, workerFinished, keepAttempted) != 1 ||
        Record(7, native.shadowMethodAttemptsInP5, native.shadowMethodAllowedInP5,
               native.shadowMethodDeniedInP5, native.methodResultRacedP6) != 1 ||
        Record(8, native.p5Count, native.p6Count, native.timedOut, native.releaseCount) != 1)
        return -2;
    int32_t after = -1;
    int32_t valid = 0;
#if defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
    valid = ReadCanary(after) ? 1 : 0;
#endif
    if (Record(9, canaryBefore, after, valid, 0) != 1) return -3;
    FirstErrorDisk error{};
    error.magic = kMagic;
#if defined(HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE) && HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE
    using namespace il2cpp::vm::assembly_shadow_first_failure_v2;
    const auto status = il2cpp::vm::AssemblyShadow::FirstFailureV2Status();
    error.status = static_cast<int32_t>(status);
    if (status == State::Frozen)
    {
        Snapshot snapshot{};
        if (!il2cpp::vm::AssemblyShadow::TryReadFirstFailureV2(snapshot) ||
            snapshot.length > 4096) return -4;
        error.code = snapshot.code;
        error.origin = static_cast<int32_t>(snapshot.origin);
        error.reasonLength = static_cast<int32_t>(snapshot.length);
        std::memcpy(error.reason, snapshot.reason, snapshot.length + 1);
    }
#endif
    if (!PWriteAll(kFirstErrorOffset, &error, sizeof error) ||
        Record(10, 1, valid, 0, 0) != 1 || ::fsync(fd) != 0) return -5;
    stage.store(3, std::memory_order_release);
    return ::close(fd) == 0 ? 1 : -6;
#else
    (void)commitCode; (void)stateCode; (void)workerFinished; (void)keepAttempted;
    return 0;
#endif
}
