// R03 B2 D2. Compile unchanged exact native function bodies extracted from
// the pinned production il2cpp_plus fork. Unity metadata, locks and staged
// image publisher are host stand-ins. Test-only, NOT a Player or recovery test.
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>
#if !defined(D2_NO_EXCEPTIONS)
#include <stdexcept>
#endif

struct Il2CppAssembly { int token; };
static std::atomic<int> heldLocks(0);
static std::atomic<int> wrongUnlockOrder(0);
static std::atomic_flag* watchedUsage = nullptr;
static bool failCliAppend = false;
static unsigned cliAppendCount = 0;

namespace il2cpp { namespace os {
class FastAutoLock
{
public:
    explicit FastAutoLock(std::mutex* mutex) : mutex_(mutex)
    {
        mutex_->lock();
        heldLocks.fetch_add(1, std::memory_order_relaxed);
    }
    ~FastAutoLock()
    {
        // When the inner physical lock unwinds, the usage lease must ALREADY
        // be cleared. The test-owned atomic probe cannot prove real OS locks.
        if (heldLocks.load(std::memory_order_relaxed) == 2 && watchedUsage)
        {
            const bool held = watchedUsage->test_and_set(std::memory_order_acquire);
            if (!held) watchedUsage->clear(std::memory_order_release);
            else wrongUnlockOrder.fetch_add(1, std::memory_order_relaxed);
        }
        heldLocks.fetch_sub(1, std::memory_order_relaxed);
        mutex_->unlock();
    }
    FastAutoLock(const FastAutoLock&) = delete;
    FastAutoLock& operator=(const FastAutoLock&) = delete;
private:
    std::mutex* mutex_;
};
}}

template<class T>
class TestDynamicArray : public std::vector<T>
{
public:
    void resize_uninitialized(size_t n) { this->resize(n); }
    void push_back(const T& item)
    {
        ++cliAppendCount;
#if !defined(D2_NO_EXCEPTIONS)
        if (failCliAppend && cliAppendCount == 2)
            throw std::runtime_error("injected CLI append exception after first entry");
#endif
        std::vector<T>::push_back(item);
    }
};
static TestDynamicArray<Il2CppAssembly*> s_cliAssemblies;

namespace il2cpp { namespace vm {
using AssemblyVector = std::vector<const Il2CppAssembly*>;
static std::mutex g_MetadataLock;
static std::mutex s_assemblyLock;
static int32_t s_assemblyVersion = 0;
static AssemblyVector s_Assemblies;

enum class AssemblyShadowError { InternalError = 100 };
enum class AssemblyShadowState { Validated, Committing, Failed, FailedAfterCommit };
namespace assembly_shadow_first_failure_v2 {
enum class Origin { UnexpectedFailure };
}
struct FakeFirstError
{
    bool frozen = false;
    unsigned calls = 0;
    AssemblyShadowError error = AssemblyShadowError::InternalError;
    assembly_shadow_first_failure_v2::Origin origin =
        assembly_shadow_first_failure_v2::Origin::UnexpectedFailure;
    char reason[100] = {};
    bool TryFreeze(int32_t code, assembly_shadow_first_failure_v2::Origin where,
                   const char* raw, size_t n) noexcept
    {
        ++calls;
        if (frozen) return false;
        frozen = true;
        error = static_cast<AssemblyShadowError>(code);
        origin = where;
        const size_t count = n < sizeof reason - 1 ? n : sizeof reason - 1;
        std::memcpy(reason, raw, count);
        reason[count] = '\0';
        return true;
    }
};
static FakeFirstError s_firstFailureV2;
static std::atomic<bool> s_unexpectedFailure{false};
static std::atomic<AssemblyShadowState> s_state{AssemblyShadowState::Validated};

static std::mutex shadowStateLock;
class Assembly
{
public:
    static bool PublishShadowBatch(const AssemblyVector&,
        bool (*)(void*), bool (*)(void*), void (*)(void*), void*);
};
class MetadataCache
{
public:
    static bool PublishInterpreterAssembliesBatch(
        const std::vector<Il2CppAssembly*>&,
        bool (*)(void*), bool (*)(void*), void (*)(void*), void*);
};

namespace {
struct ActiveSnapshot { int generation = 1; };
struct StagedAssembly { bool published = false; };
struct Candidate { struct FirstUse { bool present = false; } firstUse; };
struct ClosureMember { Candidate* candidate; StagedAssembly* staged; };
struct Transaction { std::vector<ClosureMember> closure; };
std::atomic_flag s_usageLock = ATOMIC_FLAG_INIT;
std::atomic<const ActiveSnapshot*> s_active{nullptr};
enum class Mode { Success, FalseReturn, StageException, PostStageException };
Mode mode = Mode::Success;
unsigned stagedCalls = 0;
struct InterpreterAssembly
{
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>& ids)
    {
        ++stagedCalls;
        if (ids.empty()) return false;
#if !defined(D2_NO_EXCEPTIONS)
        if (mode == Mode::StageException)
            throw std::runtime_error("injected staging callback throw");
        if (mode == Mode::PostStageException)
            throw std::runtime_error("injected after hypothetical group completion");
#endif
        return mode != Mode::FalseReturn;
    }
};
}
}}

// Literal, authenticated production bodies; no expression rewrite.
#include "D2ExactNativeBodies.inc"

static unsigned checks = 0;
static void Check(bool passed, const char* expr, int line)
{
    ++checks;
    if (!passed)
    {
        std::fprintf(stderr, "R03 D2 host FAIL line %d: %s\n", line, expr);
        std::abort();
    }
}
#define CHECK(x) Check(bool(x), #x, __LINE__)
using namespace il2cpp::vm;

static bool UsageHeld()
{
    const bool locked = s_usageLock.test_and_set(std::memory_order_acquire);
    if (!locked) s_usageLock.clear(std::memory_order_release);
    return locked;
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

    Fixture()
    {
        watchedUsage = &s_usageLock;
        ClosureMember member{};
        member.candidate = &candidate;
        member.staged = &staged;
        transaction.closure.push_back(member);
        publication.transaction = &transaction;
        publication.snapshot = &snapshot;
        publication.imageIndices.push_back(7);
        assemblies.push_back(&first);
        assemblies.push_back(&second);
        s_state.store(AssemblyShadowState::Committing, std::memory_order_release);
    }

    bool Publish(bool (*begin)(void*) = TryBeginPublication)
    {
        return MetadataCache::PublishInterpreterAssembliesBatch(
            assemblies, begin, PublishActive, ReleasePublicationUsage, &publication);
    }
    bool RegistriesEmpty() const
    {
        return s_Assemblies.empty() && s_cliAssemblies.empty();
    }
    bool RegistriesComplete() const
    {
        return s_Assemblies.size() == 2 && s_cliAssemblies.size() == 2 &&
            s_Assemblies[0] == &first && s_Assemblies[1] == &second &&
            s_cliAssemblies[0] == &first && s_cliAssemblies[1] == &second;
    }
};

static void CheckScopeClean(const Fixture& f, bool expectedPublished)
{
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(wrongUnlockOrder.load(std::memory_order_relaxed) == 0);
    CHECK(!UsageHeld());
    CHECK(!f.publication.usageHeld);
    CHECK(f.RegistriesEmpty() != expectedPublished);
    CHECK(s_assemblyVersion == (expectedPublished ? 1 : 0));
    CHECK((s_active.load(std::memory_order_acquire) == &f.snapshot) == expectedPublished);
    CHECK(f.staged.published == expectedPublished);
}

#if !defined(D2_NO_EXCEPTIONS)
static bool BeginThenThrow(void* opaque)
{
    const bool admitted = TryBeginPublication(opaque);
    if (admitted) throw std::runtime_error("injected after UsageLock acquisition");
    return false;
}
#endif

static bool Invoke(Fixture& f, bool& escaped, bool (*begin)(void*) = TryBeginPublication)
{
#if defined(D2_NO_EXCEPTIONS)
    (void)escaped;
    ScopedUnexpectedPublicationExit exceptional;
    const bool returned = f.Publish(begin);
    exceptional.returned = true;
    return returned;
#else
    try
    {
        ScopedUnexpectedPublicationExit exceptional;
        const bool returned = f.Publish(begin);
        exceptional.returned = true;
        return returned;
    }
    catch (const std::runtime_error&)
    {
        escaped = true;
        return false;
    }
#endif
}

static void CheckTerminal(bool expected)
{
    CHECK(s_unexpectedFailure.load(std::memory_order_acquire) == expected);
    CHECK(s_firstFailureV2.frozen == expected);
    CHECK(s_firstFailureV2.calls == (expected ? 1u : 0u));
    CHECK(s_state.load(std::memory_order_acquire) ==
        (expected ? AssemblyShadowState::Failed : AssemblyShadowState::Committing));
    if (expected)
        CHECK(std::strstr(s_firstFailureV2.reason, "restart required") != nullptr);
}

static void UsedDenial()
{
    Fixture f;
    f.candidate.firstUse.present = true;
    bool escaped = false;
    CHECK(!Invoke(f, escaped));
    CHECK(!escaped);
    CHECK(f.publication.used == &f.candidate);
    CHECK(stagedCalls == 0);
    CheckScopeClean(f, false);
    CheckTerminal(false);
}
static void NormalFalse()
{
    Fixture f;
    mode = Mode::FalseReturn;
    bool escaped = false;
    CHECK(!Invoke(f, escaped));
    CHECK(!escaped);
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(stagedCalls == 1);
    CheckScopeClean(f, false);
    CheckTerminal(false);
}
static void NormalSuccess()
{
    Fixture f;
    bool escaped = false;
    CHECK(Invoke(f, escaped));
    CHECK(!escaped);
    CHECK(stagedCalls == 1);
    CHECK(f.RegistriesComplete());
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(wrongUnlockOrder.load(std::memory_order_relaxed) == 0);
    CHECK(!UsageHeld());
    CHECK(!f.publication.usageHeld);
    CHECK(s_assemblyVersion == 1);
    CHECK(s_active.load(std::memory_order_acquire) == &f.snapshot);
    CHECK(f.staged.published);
    CheckTerminal(false);
}
#if !defined(D2_NO_EXCEPTIONS)
static void FailedException(Mode newMode, bool failCli, bool throwBegin)
{
    Fixture f;
    mode = newMode;
    failCliAppend = failCli;
    bool escaped = false;
    CHECK(!Invoke(f, escaped, throwBegin ? BeginThenThrow : TryBeginPublication));
    CHECK(escaped);
    CHECK(heldLocks.load(std::memory_order_relaxed) == 0);
    CHECK(wrongUnlockOrder.load(std::memory_order_relaxed) == 0);
    CHECK(!UsageHeld());
    CHECK(!f.publication.usageHeld);
    CHECK(f.RegistriesEmpty());
    CHECK(s_assemblyVersion == 0);
    CHECK(s_active.load(std::memory_order_acquire) == nullptr);
    CHECK(!f.staged.published);
    CheckTerminal(true); // exact native CommitTransaction exceptional guard
}
#endif

int main(int argc, char** argv)
{
    if (argc != 2) { std::fputs("Expected scenario name\n", stderr); return 2; }
    const char* scenario = argv[1];
    if (std::strcmp(scenario, "used-denial") == 0) UsedDenial();
    else if (std::strcmp(scenario, "normal-false") == 0) NormalFalse();
    else if (std::strcmp(scenario, "normal-success") == 0) NormalSuccess();
#if !defined(D2_NO_EXCEPTIONS)
    else if (std::strcmp(scenario, "cli-append-exception") == 0)
        FailedException(Mode::Success, true, false);
    else if (std::strcmp(scenario, "usage-acquired-exception") == 0)
        FailedException(Mode::Success, false, true);
    else if (std::strcmp(scenario, "staged-exception") == 0)
        FailedException(Mode::StageException, false, false);
    else if (std::strcmp(scenario, "post-stage-exception") == 0)
        FailedException(Mode::PostStageException, false, false);
#endif
    else { std::fputs("Unknown native D2 host case\n", stderr); return 2; }
    std::printf("{\"schema\":\"R03B2D2NativeCustodyHostV1\","
                "\"result\":\"PassedPinnedD2CustodyHostOnly\","
                "\"case\":\"%s\",\"checks\":%u,"
                "\"compiledPinnedNativeBodies\":true,"
                "\"usageReleasedBeforeAssemblyUnlock\":true,"
                "\"sourceNativeCommit\":\"b86a97e1dcca18163df5ac2d5f268bf6de18bbdf\","
                "\"mockNativeDependencies\":true,"
                "\"nativeRuntimeCodecActual\":false,"
                "\"nativeProductionSourceChanged\":true,"
                "\"unityPlayerExecuted\":false,"
                "\"postCodecRollbackProven\":false,"
                "\"R03Accepted\":false,\"H2Passed\":false,"
                "\"ReadyForHumanReviewGate\":false}\n", scenario, checks);
    return 0;
}
