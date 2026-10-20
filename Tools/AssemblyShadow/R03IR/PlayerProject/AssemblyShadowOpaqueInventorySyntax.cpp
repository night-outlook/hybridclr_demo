// R03 P1 official Unity2022.3.62f2 SDK SYNTAX-ONLY probe.
// The inactive native collector captures no class metadata and never exposes
// physical pointers, type keys, Player APIs or coherent VM epoch.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowOpaqueExecutionInventory.h"
#include "vm/AssemblyShadowExecutionRegistryRevision.h"
#include "vm/AssemblyShadowExecutionRegistrationWitness.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace opaque=assembly_shadow_opaque_execution;
namespace revision=assembly_shadow_execution_registry;
namespace witness=assembly_shadow_execution_witness;
static_assert(opaque::kSlotCount==2048,"Opaque slots changed");
static_assert(witness::kSlots==opaque::kSlotCount,
              "Witness registry must align with observed slot count");
static_assert(sizeof(witness::Table)<=40960u,
              "Registration source witness memory bound changed");
static_assert(!opaque::Receipt{}.registrationWitnessesObserved,
              "Witness proof must never default to acceptance");
static_assert(opaque::kMaximumClasses==1024,"Opaque capacity changed");
static_assert(sizeof(opaque::Scratch)<=33000u,"Opaque owned scratch changed");
static_assert(sizeof(revision::Revision)==sizeof(uint64_t),
              "Revision must remain fixed size, without heap state");
static_assert(!opaque::Receipt{}.registryRevisionFenceStable,
              "Registry revision is only observed when successfully captured");
static_assert(!opaque::Receipt{}.physicalClassPointerOriginProven,
              "Opaque method cannot claim provenance");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using CaptureSignature=bool (*)(opaque::Scratch&,opaque::Receipt&);
CaptureSignature RequireInactiveOpaqueSourceSyntax() noexcept
{return &AssemblyShadow::TryCaptureOpaqueExecutionInventory;}
#endif
}}} // namespaces
