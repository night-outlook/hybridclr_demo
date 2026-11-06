#pragma once
#include <string>
namespace il2cpp { namespace vm {
enum class AssemblyShadowError { Success = 0, InternalError = 20 };
class AssemblyShadow {
public:
    static AssemblyShadowError GetRecoveryInfoJson(std::string& json);
};
}}
