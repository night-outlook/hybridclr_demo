// R03 P1 official Unity2022.3.62f2 SDK SYNTAX-ONLY signature check.
// Inactive zero-class execution/R02 method. No call and no linked Player.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowBoundedExecutionEmptyLive.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace live=assembly_shadow_bounded_execution_empty_live;
namespace record=assembly_shadow_frozen_execution_record;
static_assert(assembly_shadow_r02::Snapshot::kMaximumObjectBytes<=512,
              "R02 owned capture bound changed");
static_assert(record::Record::kMaxBytes==3932160,
              "Execution single-field byte bound changed");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using Signature = bool (*) (record::Record&, live::Receipt&);
Signature RequireInactiveMethodSyntax() noexcept
{
    return &AssemblyShadow::TryCaptureBoundedEmptyExecutionLive;
}
#endif
}}} // namespaces
