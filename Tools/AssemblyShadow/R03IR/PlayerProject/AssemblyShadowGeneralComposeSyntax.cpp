// P1 syntax-only official Unity2022.3.62f2 SDK type surface for the
// inactive, source-bound, owned general V1 composer. This has NO runtime
// registration, public Player API, scheduling, metadata fetch or execution.
#include "vm/AssemblyShadowBoundedGeneralComposer.h"
#include <cstddef>

namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
using namespace assembly_shadow_bounded_general;
static_assert(kMaxStartupNames == 4096, "Candidate source capacity changed");
static_assert(kMaxTotalOwnedObjectBytes <= 16u*1024u*1024u,
              "Owned general capture object budget changed");
static_assert(sizeof(Receipt) <= 256,
              "P1 bounded composition receipt unexpectedly grew");
// Declaration forces normal C++17 parsing of the full inline implementation
// under every candidate/debug/probe/feature-off native compile profile.
using ActualComposeSignature = bool (*)(const Inputs&,
    assembly_shadow_frozen_general::Capture&, Receipt&) noexcept;
ActualComposeSignature RequireComposerSyntax() noexcept
{
    return &Compose;
}
}}} // namespaces
