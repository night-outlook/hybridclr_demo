// Exact production D4 ProcessSnapshotOwner + D1 receipt, no Unity/VM.
// Compiles with C++11, C++17 and -fno-exceptions -fno-rtti.
// Process-lifetime owner is guaranteed in production by heap-retained
// Transaction; this host intentionally destroys the owner at process exit.
#include "AssemblyShadowProcessSnapshotOwner.h"
#include "AssemblyShadowPublicationPhaseReceipt.h"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <type_traits>
#include <utility>

struct Snapshot
{
    int value;
    static int live;
    explicit Snapshot(int n) noexcept : value(n) { ++live; }
    ~Snapshot() noexcept { --live; }
};
int Snapshot::live=0;
using Owner = il2cpp::vm::assembly_shadow_publication::ProcessSnapshotOwner<Snapshot>;
namespace phase=il2cpp::vm::assembly_shadow_publication;
static_assert(noexcept(std::declval<Owner&>().TryPublish(
    std::declval<std::unique_ptr<Snapshot>&>(),
    std::declval<std::atomic<const Snapshot*>&>())),
    "D4 persistent owner may not allocate/throw during publish");
static_assert(noexcept(std::declval<const Owner&>().get()),
    "D4 process snapshot read must be noexcept");

static unsigned checks=0;
static void Check(bool ok,const char* expression)
{
    ++checks;
    if(!ok){std::fprintf(stderr,"D4 OWNER FAIL: %s\n",expression);std::abort();}
}
#define CHECK(x) Check(bool(x),#x)

int main(int argc,char**argv)
{
    if(argc!=2) return 2;
    const char* which=argv[1];
    std::atomic<const Snapshot*> active{nullptr};
    Owner owner;
    phase::PublicationPhaseReceipt receipt;
    std::unique_ptr<Snapshot> pending(new Snapshot(42));
    CHECK(Snapshot::live==1);
    CHECK(!owner.get());
    CHECK(!active.load(std::memory_order_acquire));
    CHECK(receipt.Advance(phase::Phase::UsageAdmitted));
    CHECK(receipt.Advance(phase::Phase::RegistriesAppended));
    CHECK(receipt.Advance(phase::Phase::CodecAttempted));
    CHECK(receipt.Advance(phase::Phase::RuntimeGroupPublished));

    if(which[0]=='0') // no transfer on invalid input
    {
        std::unique_ptr<Snapshot> nullPending;
        CHECK(!owner.TryPublish(nullPending,active));
        CHECK(!owner.get());
        CHECK(pending && Snapshot::live==1);
        CHECK(!active.load(std::memory_order_acquire));
        receipt.MarkTerminal(phase::Reason::MissingCleanupProof);
        CHECK(receipt.RestartRequired());
    }
    else if(which[0]=='1') // ownership precedes publication; duplicate refused
    {
        Snapshot* original=pending.get();
        CHECK(owner.TryPublish(pending,active));
        CHECK(pending.get()==nullptr);
        CHECK(active.load(std::memory_order_acquire)==original);
        CHECK(owner.get()==original);
        CHECK(Snapshot::live==1);
        CHECK(receipt.Advance(phase::Phase::ActiveSnapshotPublished));
        CHECK(receipt.Advance(phase::Phase::InitializersRunning));
        CHECK(receipt.Complete());
        CHECK(receipt.IsComplete());
        std::unique_ptr<Snapshot> duplicate(new Snapshot(55));
        CHECK(!owner.TryPublish(duplicate,active));
        CHECK(duplicate.get()!=nullptr);
        CHECK(owner.get()==original && active.load()==original);
        CHECK(Snapshot::live==2);
    }
    else if(which[0]=='2') // a previously public pointer cannot be overwritten
    {
        Snapshot external(11);
        active.store(&external,std::memory_order_release);
        CHECK(!owner.TryPublish(pending,active));
        CHECK(owner.get()==nullptr);
        CHECK(pending && Snapshot::live==2);
        CHECK(active.load(std::memory_order_acquire)==&external);
        active.store(nullptr,std::memory_order_release);
    }
    else if(which[0]=='3') // post-active terminal retains the public object
    {
        Snapshot* original=pending.get();
        CHECK(owner.TryPublish(pending,active));
        CHECK(receipt.Advance(phase::Phase::ActiveSnapshotPublished));
        receipt.MarkTerminal(phase::Reason::NativePublicationFailure);
        CHECK(receipt.RestartRequired());
        CHECK(!receipt.Advance(phase::Phase::InitializersRunning));
        CHECK(owner.get()==original);
        CHECK(active.load(std::memory_order_acquire)==original);
        CHECK(Snapshot::live==1);
    }
    else return 2;
    std::printf("{\"schema\":\"R03D4OwnerHeaderNoExceptionsV1\","
        "\"result\":\"PassedExactD4OwnerNoExceptionsHostOnly\","
        "\"case\":\"%c\",\"checks\":%u,"
        "\"actualNativeD4Header\":true,\"actualD1Receipt\":true,"
        "\"unityPlayerExecuted\":false,\"R03Accepted\":false}\n",which[0],checks);
    return 0;
}
