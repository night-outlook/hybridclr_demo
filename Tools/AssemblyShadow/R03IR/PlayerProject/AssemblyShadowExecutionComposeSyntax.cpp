// P1 official Unity2022.3.62f2 SDK SYNTAX-ONLY type coverage for the
// inactive owned execution/R02 record. No VM acquisition, Player calls,
// coherent epoch, memory/GC/RSS or linked runtime evidence.
#include "vm/AssemblyShadowFrozenExecutionRecord.h"
#include <cstddef>

namespace il2cpp { namespace vm { namespace assembly_shadow_sdk_syntax {
namespace owned=assembly_shadow_frozen_execution_record;
namespace counters=assembly_shadow_r02;
namespace diagnostic=assembly_shadow_diagnostic;
namespace execution=assembly_shadow_execution_diagnostic;
static_assert(owned::Record::kMaxBytes == 3932160u, "Execution field bound changed");
static_assert(owned::Record::kMaxRows == 1024u, "Execution class bound changed");
static_assert(sizeof(owned::Record) <= owned::Record::kMaximumObjectBytes,
              "Execution owned capture object bound changed");
static_assert(sizeof(counters::Snapshot) <= counters::Snapshot::kMaximumObjectBytes,
              "R02 snapshot object bound changed");
using BeginSignature=bool (owned::Record::*)(
    const owned::Identity&,const counters::Snapshot&,size_t) noexcept;
using AddSignature=bool (owned::Record::*)(const execution::ClassRow&) noexcept;
using FreezeSignature=bool (owned::Record::*)() noexcept;
using EmitSignature=diagnostic::WriteResult (owned::Record::*)(
    diagnostic::Sink,size_t) const noexcept;
using R02CaptureSignature=bool (*)(counters::Snapshot&,
                                   counters::SnapshotReceipt&) noexcept;
BeginSignature RequireBeginSyntax() noexcept {return &owned::Record::Begin;}
AddSignature RequireAddSyntax() noexcept {return &owned::Record::AddClass;}
FreezeSignature RequireFreezeSyntax() noexcept {return &owned::Record::Freeze;}
EmitSignature RequireEmitSyntax() noexcept {return &owned::Record::EmitTo;}
R02CaptureSignature RequireR02CaptureSyntax() noexcept
{return &counters::Snapshot::TryCaptureCurrent;}
}}} // namespace il2cpp::vm::assembly_shadow_sdk_syntax
