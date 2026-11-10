#pragma once
// R03 B2 test-only adapter from immutable, source-unverified owned rows to
// the ACTUAL shared native execution JSON class-row serializer.
// This is not a VM reader. Caller owns all immutable row storage and must
// separately validate source provenance, header/R02 counters, sink Finish()
// and the final semantic byte/identity/epoch contract.
#include "BoundedOwnedExecutionRows.h"
#include "AssemblyShadowExecutionSerializer.h"

namespace r03_b2_owned_execution_bridge {

template<class Output>
bool AppendClassRows(Output& output,
                     const r03_b2_owned_execution_rows::Rows& rows)
{
    if (!rows.Complete()) return false;
    namespace source=r03_b2_owned_execution_rows;
    namespace target=il2cpp::vm::assembly_shadow_execution_diagnostic;
    for(size_t index=0; index<rows.Count(); ++index)
    {
        source::RowView observed{};
        if (!rows.Get(index,observed)) return false;
        target::ClassRow row{};
        row.logicalAssembly.data=observed.logicalAssembly.data;
        row.logicalAssembly.bytes=observed.logicalAssembly.size;
        row.typeKey.data=observed.typeKey.data;
        row.typeKey.bytes=observed.typeKey.size;
        row.interpreterShadow=observed.fields.interpreterShadow;
        row.physicalInterpreter=observed.fields.physicalInterpreter;
        row.isActive=observed.fields.isActive;
        row.cctorStarted=observed.fields.cctorStarted;
        row.cctorFinished=observed.fields.cctorFinished;
        row.hasInitializationException=observed.fields.hasInitializationException;
        row.staticStoragePointer.data=observed.staticStoragePointer.data;
        row.staticStoragePointer.bytes=observed.staticStoragePointer.size;
        row.pointerDetailsAvailable=observed.fields.pointerDetailsAvailable;
        row.staticStorageAvailable=observed.fields.staticStorageAvailable;
        target::AppendClass(output,row,index!=0);
    }
    return true; // NOT a Writer::Finish(), source-admission, or V2 receipt.
}

} // namespace r03_b2_owned_execution_bridge
