// Compile the production gateway against real VM structures and explicit
// lookup/invocation adapters. This is not a Unity, GC, or Player readiness test.
#include "vm/AssemblyShadowStartup.h"
#include "vm/AssemblyShadowStartupGate.h"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>

static int checks = 0;
static void Check(bool value, const char* message)
{
    ++checks;
    if (!value) {
        std::fprintf(stderr, "r01_gateway_check_failed=%s\n", message);
        std::fflush(stderr);
        throw std::runtime_error(message);
    }
    std::fprintf(stderr, "r01_gateway_check=%d PASS\n", checks);
    std::fflush(stderr);
}

static void Event(const char* name)
{
    std::fprintf(stderr, "r01_gateway_event=%s checks=%d\n", name, checks);
    std::fflush(stderr);
}
static void AtExitSentinel() { Event("atexit"); }

#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#include "vm/AssemblyShadowStartup.cpp"

namespace hybridclr {
    extern const uint32_t g_assemblyShadowStartupBootstrapSchemaVersion =
        std::getenv("R01_GATEWAY_BAD_SCHEMA") ? 2 : 1;
    const char* g_assemblyShadowStartupBootstrapAssembly = "Gateway.Bootstrap";
    const char* g_assemblyShadowStartupBootstrapNamespace = "Gateway";
    const char* g_assemblyShadowStartupBootstrapType = "Entry";
    const char* g_assemblyShadowStartupBootstrapMethod = "Run";
}

Il2CppDefaults il2cpp_defaults = {};
static std::string scenario;
static Il2CppAssembly assembly = {};
static Il2CppImage image = {};
static Il2CppClass klass = {}, integerClass = {}, otherClass = {};
static Il2CppType returnType = {};
static MethodInfo method = {};
static struct Box { Il2CppObject object; int32_t value; } box = {};
static int lookupCalls = 0, invokeCalls = 0, sealedCalls = 0;
static bool Is(const char* name) { return scenario == name; }
static void StubMethod() {}
static void StubInvoker(Il2CppMethodPointer, const MethodInfo*, void*, void**, void*) {}

namespace il2cpp { namespace vm {
Il2CppThread* Thread::Current() { return Is("wrong-thread") ? nullptr : reinterpret_cast<Il2CppThread*>(1); }
Il2CppThread* Thread::Main() { return reinterpret_cast<Il2CppThread*>(1); }
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(const char*)
{ ++lookupCalls; Event("lookup"); return Is("missing-assembly") ? nullptr : &assembly; }
bool AssemblyShadow::IsCandidate(const Il2CppAssembly*) { return Is("candidate"); }
AssemblyShadowError AssemblyShadow::ReportUnexpectedFailure()
{ ++sealedCalls; Event("seal"); return AssemblyShadowError::InternalError; }
Il2CppClass* Image::ClassFromNameDefinedInImage(const Il2CppImage* actual, const char*, const char*)
{ Check(actual == &image, "physical image used"); return Is("missing-type") ? nullptr : &klass; }
const MethodInfo* Class::GetMethods(Il2CppClass* actual, void** iterator)
{
    Check(actual == &klass, "exact declaring class used");
    uintptr_t index = reinterpret_cast<uintptr_t>(*iterator);
    *iterator = reinterpret_cast<void*>(index + 1);
    return index < (Is("duplicate-method") ? 2u : 1u) ? &method : nullptr;
}
Il2CppObject* Runtime::Invoke(const MethodInfo* actual, void* instance, void** parameters, Il2CppException** exception)
{
    ++invokeCalls;
    Check(actual == &method && !instance && !parameters && exception, "exact static invocation");
    Event("invoke");
    if (Is("native-throw")) throw std::runtime_error("injected native unwind");
    if (Is("managed-throw")) { *exception = reinterpret_cast<Il2CppException*>(1); return nullptr; }
    if (Is("reentry")) {
        AssemblyShadowStartup::AfterRuntimeInit(true);
        Event("post-recursive-init");
    }
    if (Is("null-result")) return nullptr;
    return &box.object;
}
void* Object::Unbox(Il2CppObject* object)
{ Check(object == &box.object, "actual boxed result"); return &box.value; }
}}

static void PureGateChecks()
{
    using namespace il2cpp::vm::assembly_shadow_startup;
    int calls = 0;
    Gate disabled;
    Check(disabled.Run(false, false, [&] { ++calls; return true; }), "unconfigured compatibility");
    Check(calls == 0 && disabled.State() == GateState::Idle, "disabled executes nothing");
    Gate early;
    Check(!early.Run(true, true, [&] { ++calls; return true; }), "no execution before complete core");
    early.MarkCoreReady();
    Check(!early.Run(true, true, [&] { ++calls; return true; }) && calls == 0, "premature failure is sticky");
    Gate once; once.MarkCoreReady();
    Check(once.Run(true, true, [&] { ++calls; return true; }), "successful dispatch");
    Check(once.Run(true, false, [&] { ++calls; return false; }) && calls == 1, "repeat success without invocation");
    Gate refusal; refusal.MarkCoreReady();
    Check(!refusal.Run(true, true, [] { return false; }), "known refusal");
    Check(!refusal.Run(true, true, [] { return true; }), "known refusal sticky");
    Gate thrown; thrown.MarkCoreReady();
    Check(!thrown.Run(true, true, []() -> bool { throw 1; }), "exception captured");
    Check(thrown.Reason() == Failure::CallbackThrew && !thrown.Run(true, true, [] { return true; }), "exception sticky");
    Gate recursive; recursive.MarkCoreReady();
    bool inner = true;
    Check(!recursive.Run(true, true, [&] {
        inner = recursive.Run(true, true, [] { return true; }); return true;
    }), "owner cannot overwrite recursive failure");
    Check(!inner && recursive.Reason() == Failure::PendingEntry, "recursive call cannot escape success");

    // Deterministic overlap, not a timing-based stress assumption.
    Gate concurrent; concurrent.MarkCoreReady();
    std::atomic<bool> entered(false), release(false);
    std::atomic<int> attempts(0);
    bool owner = true;
    std::thread first([&] {
        owner = concurrent.Run(true, true, [&] {
            ++attempts; entered.store(true);
            while (!release.load()) std::this_thread::yield();
            return true;
        });
    });
    while (!entered.load()) std::this_thread::yield();
    bool second = concurrent.Run(true, false, [&] { ++attempts; return true; });
    release.store(true); first.join();
    Check(!owner && !second && attempts == 1, "concurrent entry poisons without duplicate invocation");
    Check(concurrent.Reason() == Failure::PendingEntry, "concurrent pending reason retained");
    Gate wrong; wrong.MarkCoreReady();
    Check(!wrong.Run(true, false, [] { return true; }), "dispatch requires main thread");
}

static void InitializeFixture()
{
    assembly.aname.name = "Gateway.Bootstrap"; assembly.image = &image;
    image.name = "Gateway.Bootstrap.dll"; image.nameNoExt = assembly.aname.name; image.assembly = &assembly;
    klass.image = &image; klass.name = "Entry"; klass.namespaze = "Gateway";
    returnType.type = IL2CPP_TYPE_I4;
    method.name = "Run"; method.klass = &klass; method.return_type = &returnType;
    method.flags = METHOD_ATTRIBUTE_STATIC; method.methodPointer = StubMethod; method.invoker_method = StubInvoker;
    il2cpp_defaults.int32_class = &integerClass; box.object.klass = &integerClass;
    if (Is("empty"))
        hybridclr::g_assemblyShadowStartupBootstrapAssembly = hybridclr::g_assemblyShadowStartupBootstrapNamespace =
            hybridclr::g_assemblyShadowStartupBootstrapType = hybridclr::g_assemblyShadowStartupBootstrapMethod = "";
    if (Is("global-namespace")) hybridclr::g_assemblyShadowStartupBootstrapNamespace = klass.namespaze = "";
    if (Is("partial")) hybridclr::g_assemblyShadowStartupBootstrapMethod = "";
    if (Is("namespace-only")) {
        hybridclr::g_assemblyShadowStartupBootstrapAssembly = hybridclr::g_assemblyShadowStartupBootstrapType =
            hybridclr::g_assemblyShadowStartupBootstrapMethod = "";
    }
    if (Is("bad-name")) hybridclr::g_assemblyShadowStartupBootstrapType = "Outer+Inner";
    if (Is("null-name")) hybridclr::g_assemblyShadowStartupBootstrapType = nullptr;
    if (Is("wrong-assembly")) assembly.aname.name = "Other";
    if (Is("dynamic")) image.dynamic = true;
    if (Is("interpreter")) image.token = UINT32_C(1) << 31;
    if (Is("nested")) klass.declaringType = &otherClass;
    if (Is("generic-type")) klass.is_generic = true;
    if (Is("wrong-type")) klass.name = "Other";
    if (Is("wrong-type-image")) klass.image = nullptr;
    if (Is("instance")) method.flags = 0;
    if (Is("abstract")) method.flags |= METHOD_ATTRIBUTE_ABSTRACT;
    if (Is("generic-method")) method.is_generic = true;
    if (Is("inflated-method")) method.is_inflated = true;
    if (Is("parameters")) method.parameters_count = 1;
    if (Is("wrong-return")) returnType.type = IL2CPP_TYPE_VOID;
    if (Is("byref-return")) returnType.byref = true;
    if (Is("wrong-method")) method.name = "Other";
    if (Is("wrong-owner")) method.klass = &otherClass;
    if (Is("uncallable")) method.invoker_method = nullptr;
    if (Is("wrong-result")) box.object.klass = &otherClass;
    if (Is("refuse")) box.value = 7;
    if (Is("refuse-13")) box.value = 13;
    if (Is("refuse-19")) box.value = 19;
}
#endif

int main(int argc, char** argv)
{
    try
    {
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        Check(argc == 2, "one scenario required"); scenario = argv[1];
        if (Is("success")) PureGateChecks();
        InitializeFixture();
        using il2cpp::vm::AssemblyShadowStartup;
        if (!Is("before-core")) AssemblyShadowStartup::MarkCoreReady();
        bool initialized = !Is("core-failed");
        Check(std::atexit(AtExitSentinel) == 0, "atexit sentinel registered");
        Event("before-init");
        bool accepted = AssemblyShadowStartup::AfterRuntimeInit(initialized);
        Event("post-init");
        bool expected = Is("success") || Is("global-namespace") || Is("empty");
        Check(accepted == expected, "gateway outcome");
        Check(AssemblyShadowStartup::AfterRuntimeInit(initialized) == expected, "gateway repeat outcome");
        bool invoked = expected && !Is("empty");
        invoked = invoked || Is("native-throw") || Is("managed-throw") || Is("null-result") ||
            Is("wrong-result") || Is("refuse") || Is("reentry");
        Check(invokeCalls == (invoked ? 1 : 0), "callback invocation count");
        bool unexpected = Is("native-throw") || Is("managed-throw") || Is("reentry");
        Check(sealedCalls == (unexpected ? 1 : 0), "known errors preserved; unexpected failure sealed once");
        if (Is("empty")) {
            Check(lookupCalls == 0, "empty gateway does not inspect metadata");
            Check(!AssemblyShadowStartup::AfterRuntimeInit(false), "empty preserves runtime failure");
        }
        std::cout << "r01_startup_gateway_checks=" << checks << " scenario=" << scenario << " PASS\n";
#else
        (void)argc; (void)argv;
        Check(il2cpp::vm::AssemblyShadowStartup::AfterRuntimeInit(true), "OFF retains success");
        Check(!il2cpp::vm::AssemblyShadowStartup::AfterRuntimeInit(false), "OFF retains failure");
        il2cpp::vm::AssemblyShadowStartup::MarkCoreReady();
        std::cout << "r01_startup_gateway_checks=" << checks << " scenario=off PASS\n";
#endif
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
