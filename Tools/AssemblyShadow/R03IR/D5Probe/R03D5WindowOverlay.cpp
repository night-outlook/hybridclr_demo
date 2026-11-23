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
static int32_t canaryBefore = -1, canaryOffset = -1;
static uint32_t pinnedObject = 0;

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
    if (!pinnedObject || canaryOffset < static_cast<int32_t>(sizeof(Il2CppObject))) return false;
    Il2CppObject* object = il2cpp::gc::GCHandle::GetTarget(pinnedObject);
    if (!object || !object->klass ||
        static_cast<uint64_t>(canaryOffset) + sizeof(int32_t) > object->klass->instance_size)
        return false;
    std::memcpy(&value, reinterpret_cast<const uint8_t*>(object) + canaryOffset, sizeof value);
    return true;
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
    pinnedObject = rooted; canaryOffset = stable->offset;
    int32_t value = -1;
    if (!ReadCanary(value) || value != 0) return -5;
    canaryBefore = value;
    return Record(3, value, canaryOffset, 1, 0);
#else
    (void)handle;
    return 0; // host and feature-OFF cannot claim a real native VM canary
#endif
}

// Source-host writer semantics are testable independently. A real Player's
// first-error bytes are captured from the existing B1 immutable native source.
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReceiptSeal(
    int32_t commitCode, int32_t stateCode, int32_t workerFinished, int32_t keepAttempted)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    using namespace r03_d5_evidence;
    if (stage.load(std::memory_order_acquire) != 2 || workerFinished != 1) return -1;
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
