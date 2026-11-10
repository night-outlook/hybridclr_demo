#pragma once
// R03 B2: test-only bridge from owned class rows into the genuine native
// frozen execution record (including the unchanged R02 frozen serializer).
// An actual VM adapter must independently prove physical source, metadata
// lifetime, canonical TypeKeys, R02 coverage and transaction epoch.
// No R03/B2 acceptance is granted by successful byte composition.
#include "BoundedOwnedExecutionSerializerBridge.h"
#include "vm/AssemblyShadowFrozenExecutionRecord.h"

namespace r03_b2_owned_execution_bridge {

inline bool AppendToFrozenRecord(
    il2cpp::vm::assembly_shadow_frozen_execution_record::Record& record,
    const r03_b2_owned_execution_rows::Rows& rows) noexcept
{
    if(!rows.Complete()) {
        record.RejectInvalidSource();
        return false;
    }
    for(size_t i=0;i<rows.Count();++i) {
        r03_b2_owned_execution_rows::RowView source{};
        if(!rows.Get(i,source)) {
            record.RejectInvalidSource();
            return false;
        }
        const auto row=ToNativeClassRow(source);
        if(!record.AddClass(row))return false;
    }
    return true; // caller MUST check Record::Freeze(), Complete() and EmitTo()
}

} // namespace r03_b2_owned_execution_bridge
