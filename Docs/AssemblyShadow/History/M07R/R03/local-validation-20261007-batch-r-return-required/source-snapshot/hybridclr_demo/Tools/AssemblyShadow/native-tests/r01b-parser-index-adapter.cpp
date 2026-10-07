// Parser-only adapter: RawImage does not construct or publish interpreter
// images, so the metadata index runtime's shadow ownership hooks stay inert.
#include "metadata/AssemblyShadowBridge.h"

namespace hybridclr
{
namespace metadata
{
    InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t)
    {
        return nullptr;
    }

    bool AssemblyShadowBridge::IsPublicImage(uint32_t, InterpreterImage*)
    {
        return false;
    }
}
}
