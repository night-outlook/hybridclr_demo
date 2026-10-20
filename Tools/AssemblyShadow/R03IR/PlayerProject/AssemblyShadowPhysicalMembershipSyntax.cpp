// R03 P1 official Unity2022.3.62f2 SDK SYNTAX-ONLY type check.
// The collector observes only physical iterator membership, without reading
// an observed Il2CppClass pointer or allowing caller-side metadata access.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowPhysicalMembership.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace membership=assembly_shadow_physical_membership;
static_assert(membership::kSlots==2048,"Observed registry slot count changed");
static_assert(membership::kMaximumObserved==1024,"Observed class cap changed");
static_assert(membership::kMaximumEnumerated==65536,"Physical iterator bound changed");
static_assert(sizeof(membership::Scratch)<=24576u,"Fixed membership buffer changed");
static_assert(!membership::Receipt{}.physicalClassPointerOriginProven,
              "Enumeration is not a physical pointer origin proof");
static_assert(!membership::Receipt{}.metadataPointerLifetimeProven,
              "Enumeration is not a metadata pointer lifetime proof");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using Signature=bool (*)(membership::Scratch&,membership::Receipt&);
Signature RequireInactivePhysicalMembershipSyntax() noexcept
{return &AssemblyShadow::TryAuditObservedPhysicalClassMembership;}
#endif
}}} // namespaces
