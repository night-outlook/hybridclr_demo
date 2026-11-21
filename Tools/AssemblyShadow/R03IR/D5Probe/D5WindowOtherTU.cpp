// Separate C++ translation unit: tests the C++11 header singleton is unique.
#include "vm/AssemblyShadowD5WindowProbe.h"
extern "C" void* D5ProbeOtherTU()
{
    return &il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance();
}
