// R03 B2 SOURCE-HOST ONLY. Compile unchanged, Git-pinned il2cpp_plus
// publication bodies AND the actual pinned HybridCLR Runtime.cpp/Codec.h.
// Native assembly vectors, FastAutoLock, staged callback and VM bridge are mocks.
// A deliberate throw AFTER real Runtime::PublishBatch is test-only; never
// compile this file in Unity/libil2cpp, and never infer safe recovery from it.
#include "hybridclr/metadata/InterpreterMetadataIndexRuntime.h"
#include "hybridclr/metadata/AssemblyShadowBridge.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <vector>

using Runtime = hybridclr::metadata::InterpreterMetadataIndexRuntime;
using Error = Runtime::Error;
using Image = hybridclr::metadata::InterpreterImage;

struct Il2CppAssembly { int token; };
static std::atomic<int> heldLocks(0);
static uint32_t bridgeImageId = 0;
static Image* bridgeImage = nullptr;
static unsigned checks = 0;
static void Check(bool ok, const char* expr, int line)
{
    ++checks;
    if (!ok) { std::fprintf(stderr, "FAIL at line %d: %s\n", line, expr); std::abort(); }
}
#define CHECK(x) Check(bool(x), #x, __LINE__)

namespace il2cpp { namespace os {
class FastAutoLock
{
public:
    explicit FastAutoLock(std::mutex* value) : value_(value)
    {
        value_->lock();
        heldLocks.fetch_add(1, std::memory_order_relaxed);
    }
    ~FastAutoLock()
    {
        heldLocks.fetch_sub(1, std::memory_order_relaxed);
        value_->unlock();
    }
    FastAutoLock(const FastAutoLock&) = delete;
    FastAutoLock& operator=(const FastAutoLock&) = delete;
private:
    std::mutex* value_;
};
}}

template<class T>
class TestDynamicArray : public std::vector<T>
{
public:
    void resize_uninitialized(size_t size) { this->resize(size); }
};
static TestDynamicArray<Il2CppAssembly*> s_cliAssemblies;

namespace il2cpp { namespace vm {
using AssemblyVector = std::vector<const Il2CppAssembly*>;
static std::mutex g_MetadataLock;
static std::mutex s_assemblyLock;
static int32_t s_assemblyVersion = 0;
static AssemblyVector s_Assemblies;

class Assembly
{
public:
    static bool PublishShadowBatch(
        const AssemblyVector&, bool (*)(void*), bool (*)(void*), void*);
};
class MetadataCache
{
public:
    static bool PublishInterpreterAssembliesBatch(
        const std::vector<Il2CppAssembly*>&, bool (*)(void*), bool (*)(void*), void*);
};

namespace {
struct ActiveSnapshot { int generation = 1; };
struct StagedAssembly { bool published = false; };
struct Candidate { struct FirstUse { bool present = false; } firstUse; };
struct ClosureMember { Candidate* candidate; StagedAssembly* staged; };
struct Transaction { std::vector<ClosureMember> closure; };
std::atomic_flag s_usageLock = ATOMIC_FLAG_INIT;
std::atomic<const ActiveSnapshot*> s_active{nullptr};
enum class MockMode { PreCodecFalse, ActualRuntime, ThrowAfterRuntimeGroup };
MockMode mockMode = MockMode::ActualRuntime;
uint32_t observedImageId = 0;
unsigned actualRuntimeCalls = 0;
Error actualRuntimeResult = Error::InvalidState;

// The native PublishActive body is ORIGINAL, but this staging delegate is a
// TEST adapter that invokes the actual, unchanged Runtime implementation.
// The native real StagedAssembly layer is NOT compiled in this harness.
struct InterpreterAssembly
{
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>& imageIndices)
    {
        if (mockMode == MockMode::PreCodecFalse) return false;
        ++actualRuntimeCalls;
        if (imageIndices.size() != 1 || imageIndices[0] != observedImageId)
            return false;
        actualRuntimeResult = Runtime::PublishBatch(imageIndices.data(), imageIndices.size());
        if (mockMode == MockMode::ThrowAfterRuntimeGroup &&
            actualRuntimeResult == Error::None)
            throw std::runtime_error("TEST ONLY: throw after actual Runtime group publication");
        return actualRuntimeResult == Error::None;
    }
};
}
}}

// Include EXACT unchanged functions from the pinned native Git files.
#include "NativeRegistryExactBodies.inc"

// Only VM bridge predicates are mocked; the actual Runtime invokes these.
// Native s_active is written by the literal PublishActive callback above.
namespace hybridclr { namespace metadata {
InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t)
{
    return nullptr;
}
bool AssemblyShadowBridge::IsPublicImage(uint32_t id, InterpreterImage* image)
{
    return id == bridgeImageId && image == bridgeImage &&
           il2cpp::vm::s_active.load(std::memory_order_acquire) != nullptr;
}
}}

using namespace il2cpp::vm;
struct Marker { uint32_t tag; };

static bool UsageLocked()
{
    const bool held = s_usageLock.test_and_set(std::memory_order_acquire);
    if (!held) s_usageLock.clear(std::memory_order_release);
    return held;
}

struct Fixture
{
    Il2CppAssembly first{101}, second{102};
    Candidate candidate;
    StagedAssembly staged;
    Transaction transaction;
    ActiveSnapshot snapshot;
    Publication publication;
    std::vector<Il2CppAssembly*> assemblies;
    std::vector<Runtime::Reservation> reservations;
    Marker marker{0x10203u};
    Image* image;
    uint32_t id = 0;
    int32_t token = 0;

    explicit Fixture(bool finalize) : image(reinterpret_cast<Image*>(&marker))
    {
        CHECK(Runtime::ReserveImages(1, reservations) == Error::None);
        CHECK(reservations.size() == 1);
        id = reservations[0].imageId;
        CHECK(id != 0);
        bridgeImageId = id;
        bridgeImage = image;
        observedImageId = id;
        {
            Runtime::ScopedConstruction scope(id, image, true);
            CHECK(Runtime::Encode(id, 0, token) == Error::None);
            if (finalize)
                CHECK(Runtime::Finalize(id, 1) == Error::None);
        }
        CHECK(Runtime::GetPublishedImage(id) == nullptr);
        Runtime::Codec::DecodedData decoded{};
        CHECK(Runtime::Decode(token, decoded) == Error::OwnerRequired);
        ClosureMember member{};
        member.candidate = &candidate;
        member.staged = &staged;
        transaction.closure.push_back(member);
        publication.transaction = &transaction;
        publication.snapshot = &snapshot;
        publication.imageIndices.push_back(id);
        assemblies.push_back(&first);
        assemblies.push_back(&second);
    }

    bool Publish()
    {
        return MetadataCache::PublishInterpreterAssembliesBatch(
            assemblies, TryBeginPublication, PublishActive, &publication);
    }
    bool RuntimeVisible() const { return Runtime::GetPublishedImage(id) == image; }
    bool RuntimeHidden() const { return Runtime::GetPublishedImage(id) == nullptr; }
    bool TokenPublic() const
    {
        Runtime::Codec::DecodedData decoded{};
        return Runtime::Decode(token, decoded) == Error::None &&
               decoded.imageId == id && decoded.rawIndex == 0;
    }
    bool TokenPrivate() const
    {
        Runtime::Codec::DecodedData decoded{};
        return Runtime::Decode(token, decoded) == Error::OwnerRequired;
    }
    bool PhysicalEmpty() const { return s_Assemblies.empty() && s_cliAssemblies.empty(); }
    bool PhysicalAppended() const
    {
        return s_Assemblies.size() == 2 && s_cliAssemblies.size() == 2 &&
               s_Assemblies[0] == &first && s_Assemblies[1] == &second &&
               s_cliAssemblies[0] == &first && s_cliAssemblies[1] == &second;
    }
};

static void CheckCleanNormalReturn(const Fixture& f)
{
    CHECK(f.PhysicalEmpty());
    CHECK(s_assemblyVersion == 0);
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(!UsageLocked());
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(f.RuntimeHidden());
    CHECK(f.TokenPrivate());
    CHECK(!f.staged.published);
}

static void CaseUsedRejection()
{
    Fixture f(true);
    f.candidate.firstUse.present = true;
    CHECK(!f.Publish());
    CHECK(f.publication.used == &f.candidate);
    CHECK(actualRuntimeCalls == 0);
    CheckCleanNormalReturn(f);
}

static void CasePreCodecFalse()
{
    Fixture f(true);
    mockMode = MockMode::PreCodecFalse;
    CHECK(!f.Publish());
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(actualRuntimeCalls == 0);
    CheckCleanNormalReturn(f);
}

static void CaseActualCodecUnfinalized()
{
    Fixture f(false);
    CHECK(!f.Publish());
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(actualRuntimeCalls == 1);
    CHECK(actualRuntimeResult == Error::Unfinalized);
    CheckCleanNormalReturn(f);
}

static void CaseActualRuntimeSuccess()
{
    Fixture f(true);
    CHECK(f.Publish());
    CHECK(actualRuntimeCalls == 1);
    CHECK(actualRuntimeResult == Error::None);
    CHECK(f.PhysicalAppended());
    CHECK(s_assemblyVersion == 1);
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(!UsageLocked());
    CHECK(s_active.load(std::memory_order_acquire) == &f.snapshot);
    CHECK(f.staged.published);
    CHECK(f.RuntimeVisible());
    CHECK(f.TokenPublic());
    CHECK(Runtime::Publish(f.id) == Error::InvalidState);
    CHECK(Runtime::Abort(f.id) == Error::InvalidState);
}

static void CaseThrowAfterGroupBeforeSnapshot()
{
    Fixture f(true);
    mockMode = MockMode::ThrowAfterRuntimeGroup;
    bool caught = false;
    try { (void)f.Publish(); }
    catch (const std::runtime_error&) { caught = true; }
    CHECK(caught);
    CHECK(actualRuntimeCalls == 1);
    CHECK(actualRuntimeResult == Error::None);
    CHECK(f.PhysicalAppended());
    CHECK(s_assemblyVersion == 0);
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(UsageLocked()); // native manual flag remains held
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(!f.staged.published);
    CHECK(f.RuntimeHidden());  // mock active-VM gate remains closed
    CHECK(f.TokenPrivate());   // actual Runtime gates codec's published state
    CHECK(Runtime::Abort(f.id) == Error::InvalidState); // group already active
    CHECK(Runtime::Publish(f.id) == Error::InvalidState); // no retry allowed
    // No cleanup here. Process ends in an intentionally inconsistent state.
}

int main(int argc, char** argv)
{
    if (argc != 2) { std::fputs("Usage: host <case>\n", stderr); return 2; }
    const char* name = argv[1];
    if (std::strcmp(name, "used-rejection") == 0) CaseUsedRejection();
    else if (std::strcmp(name, "precodec-false") == 0) CasePreCodecFalse();
    else if (std::strcmp(name, "codec-unfinalized") == 0) CaseActualCodecUnfinalized();
    else if (std::strcmp(name, "runtime-success") == 0) CaseActualRuntimeSuccess();
    else if (std::strcmp(name, "post-group-throw") == 0) CaseThrowAfterGroupBeforeSnapshot();
    else { std::fputs("Unknown test case\n", stderr); return 2; }

    std::printf("{\"kind\":\"R03B2NativeActualRuntimePostGroup\","
        "\"result\":\"PassedPinnedHostScenario\","
        "\"case\":\"%s\",\"checks\":%u,"
        "\"actualNativeBodiesCompiled\":true,\"actualRuntimeCodecCalled\":%s,"
        "\"nativeVmMocked\":true,\"bridgeMocked\":true,"
        "\"exceptionAfterActualGroup\":%s,"
        "\"nativeProductionModified\":false,\"safeRecoveryProven\":false,"
        "\"exceptionSafePublicationProven\":false,\"realUnity\":false,"
        "\"R03Accepted\":false,\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
        name, checks,
        actualRuntimeCalls != 0 ? "true" : "false",
        std::strcmp(name, "post-group-throw") == 0 ? "true" : "false");
    return 0;
}
