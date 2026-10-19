// R03 P1 official Unity2022.3.62f2 SDK SYNTAX-ONLY probe.
// The inactive native collector captures no class metadata and never exposes
// physical pointers, type keys, Player APIs or coherent VM epoch.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowOpaqueExecutionInventory.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace opaque=assembly_shadow_opaque_execution;
static_assert(opaque::kSlotCount==2048,"Opaque slots changed");
static_assert(opaque::kMaximumClasses==1024,"Opaque capacity changed");
static_assert(sizeof(opaque::Scratch)<=33000u,"Opaque owned scratch changed");
static_assert(!opaque::Receipt{}.physicalClassPointerOriginProven,
              "Opaque method cannot claim provenance");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using CaptureSignature=bool (*)(opaque::Scratch&,opaque::Receipt&);
CaptureSignature RequireInactiveOpaqueSourceSyntax() noexcept
{return &AssemblyShadow::TryCaptureOpaqueExecutionInventory;}
#endif
}}} // namespaces
