// R03 P1 official Unity2022.3.62f2 Apple SDK SYNTAX-ONLY probe.
// Copy observed physical display names during a metadata-locked enumerator
// callback into caller-owned text, never a class pointer or execution TypeKey.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowPhysicalMembership.h"
#include "vm/AssemblyShadowOwnedPhysicalNames.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace owned=assembly_shadow_owned_physical_names;
namespace physical=assembly_shadow_physical_membership;
static_assert(owned::kMaximumRows==physical::kMaximumObserved,
              "Owned name rows must match observed registry bound");
static_assert(owned::kMaximumTextBytes==256u*1024u,
              "Reviewed owned physical text limit changed");
static_assert(sizeof(owned::Capture)<=512u*1024u,
              "Owned physical name capture grew beyond fixed memory budget");
static_assert(!owned::Receipt{}.classPointerOwnershipProven,
              "Owned names cannot prove class pointer ownership");
static_assert(!owned::Receipt{}.completeExecutionTypeKeys,
              "Physical names are not canonical execution TypeKeys");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using Signature=bool(*)(physical::Scratch&,owned::Capture&,owned::Receipt&);
Signature RequireInactiveOwnedNamesSourceSyntax() noexcept
{return &AssemblyShadow::TryCaptureOwnedObservedPhysicalNames;}
#endif
}}} // namespaces
