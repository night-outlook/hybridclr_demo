// R03 B2 test-only source-host: compile exact Git-pinned native publication
// function bodies injected by extract_native_registry_publication.py.
// OS locks, Unity assembly vectors, InterpreterAssembly and VM state are mocks.
// Never compile this TU in Unity/libil2cpp. No product acceptance is implied.
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <vector>

struct Il2CppAssembly
{
    int token;
};
static std::atomic<int> heldLocks(0);

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

template<typename T>
class TestDynamicArray : public std::vector<T>
{
public:
    void resize_uninitialized(size_t count) { this->resize(count); }
};
// MetadataCache.cpp owns this vector at file scope.
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

// Types backing the real TryBeginPublication and PublishActive bodies.
namespace {
struct ActiveSnapshot { int generation = 1; };
struct StagedAssembly { bool published = false; };
struct Candidate { struct FirstUse { bool present = false; } firstUse; };
struct ClosureMember { Candidate* candidate; StagedAssembly* staged; };
struct Transaction { std::vector<ClosureMember> closure; };
std::atomic_flag s_usageLock = ATOMIC_FLAG_INIT;
std::atomic<const ActiveSnapshot*> s_active{nullptr};
enum class MockPublishMode { Success, FalseReturn, ThrowDuringRuntimeBatch };
MockPublishMode mockMode = MockPublishMode::Success;
unsigned runtimeBatchCalls = 0;

// This is the only mocked stage of the real PublishActive callback.
struct InterpreterAssembly
{
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>& indices)
    {
        ++runtimeBatchCalls;
        if (indices.empty()) return false;
        if (mockMode == MockPublishMode::ThrowDuringRuntimeBatch)
            throw std::runtime_error("injected stub runtime publish exception");
        return mockMode != MockPublishMode::FalseReturn;
    }
};
}
}}

// The generated file contains the ORIGINAL, UNMODIFIED Git-pinned C++ bodies:
// Assembly::PublishShadowBatch,
// MetadataCache::ShadowPublicationContext / BeginShadowPublication /
// PublishShadowRegistries / PublishInterpreterAssembliesBatch,
// AssemblyShadow::LockUsage / UnlockUsage / UsedClosureMember /
// Publication / TryBeginPublication / PublishActive.
#include "NativeRegistryExactBodies.inc"

static unsigned scenarios = 0;
static unsigned checks = 0;
static void Check(bool condition, const char* expression, int line)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "FAIL at line %d: %s\n", line, expression);
        std::abort();
    }
}
#define CHECK(expr) Check(bool(expr), #expr, __LINE__)

using namespace il2cpp::vm;

static bool UsageLocked()
{
    // Probe/test-release only; a true result remains set for explicit test cleanup.
    const bool locked = s_usageLock.test_and_set(std::memory_order_acquire);
    if (!locked)
        s_usageLock.clear(std::memory_order_release);
    return locked;
}

static void ResetMockState()
{
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    s_Assemblies.clear();
    s_cliAssemblies.clear();
    s_assemblyVersion = 0;
    s_active.store(nullptr, std::memory_order_release);
    s_usageLock.clear(std::memory_order_release);
    mockMode = MockPublishMode::Success;
    runtimeBatchCalls = 0;
}

struct Fixture
{
    Il2CppAssembly first{101};
    Il2CppAssembly second{102};
    Candidate candidate;
    StagedAssembly staged;
    Transaction transaction;
    ActiveSnapshot snapshot;
    Publication publication;
    std::vector<Il2CppAssembly*> assemblies;

    Fixture()
    {
        ClosureMember member{};
        member.candidate = &candidate;
        member.staged = &staged;
        transaction.closure.push_back(member);
        publication.transaction = &transaction;
        publication.snapshot = &snapshot;
        publication.imageIndices.push_back(7);
        assemblies.push_back(&first);
        assemblies.push_back(&second);
    }
    bool Publish()
    {
        return MetadataCache::PublishInterpreterAssembliesBatch(
            assemblies, TryBeginPublication, PublishActive, &publication);
    }
};

static void TestUsedClosurePrecommitRejection()
{
    ++scenarios;
    ResetMockState();
    Fixture f;
    f.candidate.firstUse.present = true;
    CHECK(!f.Publish());
    CHECK(f.publication.used == &f.candidate);
    CHECK(s_Assemblies.empty());
    CHECK(s_cliAssemblies.empty());
    CHECK(s_assemblyVersion == 0);
    CHECK(runtimeBatchCalls == 0);
    CHECK(!UsageLocked());
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(!f.staged.published);
}

static void TestNormalRuntimeFalseReturnRollback()
{
    ++scenarios;
    ResetMockState();
    Fixture f;
    mockMode = MockPublishMode::FalseReturn;
    CHECK(!f.Publish());
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(runtimeBatchCalls == 1);
    CHECK(s_Assemblies.empty());
    CHECK(s_cliAssemblies.empty());
    CHECK(s_assemblyVersion == 0);
    CHECK(!UsageLocked());
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(!f.staged.published);
}

static void TestNormalSuccess()
{
    ++scenarios;
    ResetMockState();
    Fixture f;
    CHECK(f.Publish());
    CHECK(runtimeBatchCalls == 1);
    CHECK(s_Assemblies.size() == 2);
    CHECK(s_cliAssemblies.size() == 2);
    CHECK(s_Assemblies[0] == &f.first && s_Assemblies[1] == &f.second);
    CHECK(s_cliAssemblies[0] == &f.first && s_cliAssemblies[1] == &f.second);
    CHECK(s_assemblyVersion == 1);
    CHECK(!UsageLocked());
    CHECK(s_active.load(std::memory_order_acquire) == &f.snapshot);
    CHECK(f.staged.published);
}

static void TestExceptionalCallbackLeavesUnsealedRegistries()
{
    ++scenarios;
    ResetMockState();
    Fixture f;
    mockMode = MockPublishMode::ThrowDuringRuntimeBatch;
    bool caught = false;
    try
    {
        (void)f.Publish();
    }
    catch (const std::runtime_error&)
    {
        caught = true;
    }
    CHECK(caught);
    CHECK(runtimeBatchCalls == 1);
    // Source body outcomes, not permitted production recovery:
    CHECK(s_Assemblies.size() == 2);
    CHECK(s_cliAssemblies.size() == 2);
    CHECK(s_Assemblies[0] == &f.first && s_Assemblies[1] == &f.second);
    CHECK(s_cliAssemblies[0] == &f.first && s_cliAssemblies[1] == &f.second);
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(UsageLocked());  // manual native LockUsage has not been released
    CHECK(s_assemblyVersion == 0);
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(!f.staged.published);
    // Test-owned cleanup only. This is never a native rollback or safe retry.
    ResetMockState();
}

int main()
{
    TestUsedClosurePrecommitRejection();
    TestNormalRuntimeFalseReturnRollback();
    TestNormalSuccess();
    TestExceptionalCallbackLeavesUnsealedRegistries();
    std::printf("{\"kind\":\"R03B2PinnedNativeRegistryPublisherHost\","
                "\"result\":\"ObservedExceptionalRegistryAndUsageLockLeakInHost\","
                "\"scenarios\":%u,\"checks\":%u,"
                "\"actualNativeSourceBodiesCompiled\":true,"
                "\"mockNativeDependencies\":true,"
                "\"actualCodecRuntimeInvoked\":false,"
                "\"injectedCallbackException\":true,"
                "\"exceptionalRegistryRollbackObserved\":false,"
                "\"usageLockReleasedOnException\":false,"
                "\"realUnity\":false,\"nativeProductionChanged\":false,"
                "\"safeRecoveryProven\":false,\"R03Accepted\":false,"
                "\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
                scenarios, checks);
    return 0;
}
