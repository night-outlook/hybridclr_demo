// R03 P1 official Unity2022.3.62f2 Apple SDK SYNTAX-ONLY probe.
// Copy observed physical display names during a metadata-locked enumerator
// callback into caller-owned text, never a class pointer or execution TypeKey.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowPhysicalMembership.h"
#include "vm/AssemblyShadowOwnedPhysicalNames.h"
#include "vm/AssemblyShadowOwnedPhysicalNamesJson.h"
#include "vm/AssemblyShadowObservedTypeShape.h"
#include "vm/AssemblyShadowObservedTypeShapeCensus.h"
#include <cstddef>
namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace owned=assembly_shadow_owned_physical_names;
namespace physical=assembly_shadow_physical_membership;
namespace ownedJson=assembly_shadow_owned_physical_json;
namespace observedShape=assembly_shadow_observed_type_shape;
namespace shapeCensus=assembly_shadow_observed_type_shape_census;
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
static_assert(observedShape::kCategoryCount==9 &&
              observedShape::kClassTypeCode==0x12 &&
              observedShape::kValueTypeCode==0x11,
              "Shape hint categories differ from reviewed IL2CPP ABI");
bool RequireObservedTypeShapeCensusSyntax(const owned::Capture& names,
                                         const owned::Receipt& source,
                                         shapeCensus::Result& destination) noexcept
{
    return shapeCensus::Build(names,source,destination);
}
static_assert(ownedJson::Record::kMaximumBytes==2u*1024u*1024u,
              "Owned JSON fixed output limit changed");
static_assert(sizeof(ownedJson::Record)<=ownedJson::Record::kMaximumObjectBytes,
              "Owned JSON object exceeded reviewed bound");
static_assert(!ownedJson::Receipt{}.canonicalExecutionTypeKeys &&
              !ownedJson::Receipt{}.runtimeAcceptance,
              "Owned JSON is not a complete execution record");
bool RequireOwnedPhysicalJsonSourceSyntax(const owned::Capture& capture,
                                          const owned::Receipt& sourceReceipt,
                                          ownedJson::Record& destination,
                                          ownedJson::Receipt& receipt) noexcept
{
    return ownedJson::Compose(capture,sourceReceipt,destination,receipt);
}
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
using Signature=bool(*)(physical::Scratch&,owned::Capture&,owned::Receipt&);
Signature RequireInactiveOwnedNamesSourceSyntax() noexcept
{return &AssemblyShadow::TryCaptureOwnedObservedPhysicalNames;}
// Compile the real inactive VM source→owned JSON entry point with the
// same official installed SDK features/profiles, without a new source TU.
using LiveJsonSignature=bool(*)(physical::Scratch&,owned::Capture&,
    owned::Receipt&,ownedJson::Record&,ownedJson::Receipt&,size_t);
LiveJsonSignature RequireInactiveLiveOwnedJsonSourceSyntax() noexcept
{return &AssemblyShadow::TryCaptureOwnedObservedPhysicalJson;}
// Compile the genuine first-match VM-source→primitive type-shape census
// entry point in each official SDK feature profile, without another TU.
using LiveTypeShapeSignature=bool(*)(physical::Scratch&,owned::Capture&,
    owned::Receipt&,shapeCensus::Result&);
LiveTypeShapeSignature RequireInactiveLiveTypeShapeCensusSyntax() noexcept
{return &AssemblyShadow::TryCaptureObservedTypeShapeCensus;}
#endif
}}} // namespaces
