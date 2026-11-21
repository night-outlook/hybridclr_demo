// D5 C10 isolated validation Player native overlay ONLY.
// It must be copied into the NEW D5-specific native source roster after
// independently verified installation. No production or B1 Player references.
#include "il2cpp-config.h"
#include <cstdint>
#include <cstring>

#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
#include "vm/AssemblyShadowD5WindowProbe.h"
#endif

extern "C" IL2CPP_EXPORT int32_t R03_D5_WindowProtocolVersion()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return 1;
#else
    return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_D5_ArmP5Window(int32_t waitMilliseconds)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().Arm(
        waitMilliseconds) ? 1 : -1;
#else
    (void)waitMilliseconds;
    return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_D5_ReleaseP5Window()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    return il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance().
        ReleaseP5() ? 1 : -1;
#else
    return 0;
#endif
}

// Uses an exact 11-int32 fixed representation. This call never formats JSON,
// resolves managed classes, creates a VM object or locks engine metadata.
extern "C" IL2CPP_EXPORT int32_t R03_D5_ReadP5Window(
    int32_t* destination, int32_t count)
{
    if (!destination || count != 11)
        return -2;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE
    using il2cpp::vm::assembly_shadow_d5::WindowProbe;
    using il2cpp::vm::assembly_shadow_d5::WindowSnapshot;
    static_assert(sizeof(WindowSnapshot) == sizeof(int32_t) * 11,
        "Native/managed D5 witness wire fields changed");
    const WindowSnapshot value = WindowProbe::Instance().Read();
    std::memcpy(destination, &value, sizeof value);
    return 1;
#else
    for (int32_t i=0; i<count; ++i) destination[i] = 0;
    return 0;
#endif
}
