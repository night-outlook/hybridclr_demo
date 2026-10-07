// Real PE/CLI reader and the production declared-AssemblyRef conversion.
// Mutations are confined to a malloc-owned copy of the supplied fixture DLL.
#include "hybridclr/metadata/AssemblyShadowAssemblyReference.h"
#include "hybridclr/metadata/RawImage.h"
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <vector>

size_t CheckDeclaredReferenceIdentity(const char* fixture)
{
    using namespace hybridclr::metadata;
    size_t checks = 0;
    auto check = [&checks](bool condition, const char* message) {
        ++checks;
        if (!condition) throw std::runtime_error(message);
    };
    std::ifstream stream(fixture, std::ios::binary);
    check(stream.good(), "reference fixture readable");
    std::vector<uint8_t> file((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
    void* bytes = std::malloc(file.size());
    check(bytes != nullptr, "reference fixture owned copy");
    memcpy(bytes, file.data(), file.size());
    RawImage raw;
    check(raw.Load(bytes, file.size()) == LoadImageErrorCode::OK, "reference fixture CLI parser");
    const uint32_t count = raw.GetTableRowNum(TableType::ASSEMBLYREF);
    check(count > 0, "real reference rows available");
    bool facade = false, token = false;
    for (uint32_t row = 1; row <= count; ++row)
    {
        TbAssemblyRef reference = raw.ReadAssemblyRef(row);
        AssemblyReferenceIdentity result = ReadDeclaredAssemblyReference(raw, reference);
        check(strcmp(result.name.name, raw.GetStringFromRawIndex(reference.name)) == 0, "declared name retained");
        check(strcmp(result.name.culture, raw.GetStringFromRawIndex(reference.locale)) == 0, "declared culture retained");
        check(result.name.major == reference.majorVersion && result.name.minor == reference.minorVersion &&
            result.name.build == reference.buildNumber && result.name.revision == reference.revisionNumber, "four-part declared version retained");
        if (strcmp(result.name.name, "netstandard") == 0) facade = true;
        BlobReader key = raw.GetBlobReaderByRawIndex(reference.publicKeyOrToken);
        if (!token && !(reference.flags & 1) && key.GetLength() == 8)
        {
            token = true;
            check(result.hasPublicKeyToken && !result.name.public_key && memcmp(result.name.public_key_token, key.GetData(), 8) == 0,
                "declared token differs from full public key");
            uint8_t* mutableToken = const_cast<uint8_t*>(key.GetData());
            uint8_t saved[8];
            memcpy(saved, mutableToken, 8);
            for (size_t index = 0; index < 8; ++index) mutableToken[index] = static_cast<uint8_t>(index);
            reference.majorVersion = 11; reference.minorVersion = 22; reference.buildNumber = 33; reference.revisionNumber = 44;
            result = ReadDeclaredAssemblyReference(raw, reference);
            check(result.hasPublicKeyToken && result.name.public_key_token[0] == 0 && result.name.public_key_token[7] == 7,
                "zero-leading token preserves presence and exact bytes");
            check(result.name.major == 11 && result.name.minor == 22 && result.name.build == 33 && result.name.revision == 44,
                "patched version not replaced with provider version");
            reference.flags |= 1;
            result = ReadDeclaredAssemblyReference(raw, reference);
            const uint8_t expected[] = {0x6b,0xdd,0x3d,0x1a,0x73,0xdc,0xc0,0xd6}; // SHA1(00..07), reversed final 8 bytes.
            check(result.hasPublicKeyToken && result.name.public_key && memcmp(result.name.public_key_token, expected, 8) == 0,
                "full public key computes correct declared token");
            reference.flags &= ~1u;
            memset(mutableToken, 0, 8);
            result = ReadDeclaredAssemblyReference(raw, reference);
            check(result.hasPublicKeyToken && memcmp(result.name.public_key_token, mutableToken, 8) == 0,
                "all-zero token is still present");
            memcpy(mutableToken, saved, 8);
            reference.publicKeyOrToken = 0;
            result = ReadDeclaredAssemblyReference(raw, reference);
            check(!result.hasPublicKeyToken && !result.name.public_key, "absent token remains absent");
        }
    }
    check(facade, "logical netstandard identity returned without a physical Assembly");
    check(token, "real strong-name token fixture exercised");
    return checks;
}
