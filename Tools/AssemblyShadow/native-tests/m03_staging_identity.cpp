// Focused native metadata regression, not an IL2CPP runtime/transaction test.
// Include the real implementation to exercise its private borrowed preparser.
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include "hybridclr/metadata/StagedAssembly.cpp"
#include "vm/AssemblyShadowName.h"

// The borrowed parser releases ownership before RawImageBase destruction.
// This allocator adapter is the only VM stub; all parser/folding code is real.
namespace il2cpp { namespace utils {
void Memory::Free(void* pointer) { std::free(pointer); }
}}

namespace {
using namespace hybridclr::metadata;
using il2cpp::vm::AssemblyShadowError;
using Bytes = std::vector<hybridclr::byte>;

void Require(bool condition, const char* detail)
{
    if (!condition) throw std::runtime_error(detail);
}

Bytes ReadDll(const char* path)
{
    std::ifstream stream(path, std::ios::binary);
    Require(stream.good(), "DLL fixture cannot be opened");
    Bytes bytes((std::istreambuf_iterator<char>(stream)), {});
    Require(bytes.size() >= 64, "DLL fixture is empty or truncated");
    return bytes;
}

size_t CheckDll(const char* path)
{
    Bytes bytes = ReadDll(path);
    std::string name, detail, mvid;
    std::vector<std::string> references;
    AssemblyShadowError result = ParseIdentity(bytes.data(), bytes.size(), name, &mvid, &references, detail);
    if (result != AssemblyShadowError::Success)
        throw std::runtime_error(std::string(path) + ": " + detail);
    std::cout << name << " " << mvid << " refs=" << references.size() << "\n";
    size_t checks = 1;
    // A PE may contain unused trailing bytes. Stop at the first valid prefix,
    // rather than incorrectly requiring the original physical file length.
    for (size_t length = 0; length < bytes.size(); ++length)
    {
        result = Assembly::ReadStagedAssemblyIdentity(bytes.data(), length, name, detail);
        if (result == AssemblyShadowError::Success) break;
        Require(result != AssemblyShadowError::InternalError, "Truncated DLL raised an unexpected native failure");
        ++checks;
    }
    Bytes corrupt = bytes;
    corrupt[0] = 0;
    Require(Assembly::ReadStagedAssemblyIdentity(corrupt.data(), corrupt.size(), name, detail) == AssemblyShadowError::BadImage,
        "Invalid DOS signature was accepted");
    ++checks;
    corrupt = bytes;
    for (size_t i = 0x3c; i < 0x40; ++i) corrupt[i] = 255;
    Require(Assembly::ReadStagedAssemblyIdentity(corrupt.data(), corrupt.size(), name, detail) == AssemblyShadowError::BadImage,
        "Out-of-range PE header was accepted");
    return checks + 1;
}

size_t CheckMutations(const char* path)
{
    const Bytes original = ReadDll(path);
    uint32_t rng = 123456789;
    for (int attempt = 0; attempt < 6000; ++attempt)
    {
        Bytes bytes = original;
        for (int mutation = 0; mutation < 1 + attempt % 4; ++mutation)
        {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            bytes[rng % bytes.size()] ^= hybridclr::byte(rng >> 16);
        }
        std::string name, detail;
        // Mutations may remain valid. ASan verifies memory safety regardless
        // of result; an unexpected native exception is always a test failure.
        Require(Assembly::ReadStagedAssemblyIdentity(bytes.data(), bytes.size(), name, detail) != AssemblyShadowError::InternalError,
            "Mutated DLL raised an unexpected native failure");
    }
    return 6000;
}

size_t CheckPortablePdb()
{
    Bytes pdb(112, 0);
    auto put32 = [&](size_t offset, uint32_t value) {
        for (int i = 0; i < 4; ++i) pdb[offset + i] = hybridclr::byte(value >> (i * 8));
    };
    put32(0, 0x424a5342); put32(12, 12);
    std::memcpy(pdb.data() + 16, "PDB v1.0", 8); pdb[30] = 2;
    put32(32, 64); put32(36, 24); std::memcpy(pdb.data() + 40, "#~", 3);
    put32(44, 88); put32(48, 24); std::memcpy(pdb.data() + 52, "#Pdb", 5);
    pdb[68] = 2;
    {
        BorrowedCheckedImage<PDBImage> symbols(true);
        Require(symbols.Load(pdb.data(), pdb.size()) == LoadImageErrorCode::BAD_IMAGE, "Truncated #Pdb stream was accepted");
    }
    pdb.resize(120); put32(48, 32);
    {
        BorrowedCheckedImage<PDBImage> symbols(true);
        Require(symbols.Load(pdb.data(), pdb.size()) == LoadImageErrorCode::OK, "Valid synthetic portable PDB was rejected");
    }
    for (size_t length = 0; length < pdb.size(); ++length)
    {
        BorrowedCheckedImage<PDBImage> symbols(true);
        Require(symbols.Load(pdb.data(), length) != LoadImageErrorCode::OK, "Truncated portable PDB was accepted");
    }
    return 2 + pdb.size();
}

size_t CheckNames()
{
    using namespace il2cpp::vm::assembly_shadow_detail;
    struct Normalization { const char* input; const char* expected; };
    const Normalization cases[] = {
        { "Alpha", "Alpha" }, { "ALPHA.DLL", "ALPHA" },
        { "/patches/Alpha.exe", "Alpha" }, { "C:\\patches\\Alpha.dll", "Alpha" },
        { "Alpha.dll , Version=1.2.3.4, Culture=neutral", "Alpha" },
        { "With Space.dll", "With Space" }, { u8"/patches/Ångström.DLL", u8"Ångström" }
    };
    size_t checks = 0;
    for (const auto& entry : cases)
    {
        std::string canonical;
        Require(CanonicalName(entry.input, canonical) && canonical == entry.expected, "Name normalization mismatch");
        ++checks;
    }
    const char* invalid[] = { nullptr, "", ".dll", "\x01", "\x7f", "\xc0\xaf", "\xed\xa0\x80", "\xf4\x90\x80\x80" };
    for (const char* input : invalid)
    {
        std::string canonical;
        Require(!CanonicalName(input, canonical), "Invalid name encoding was accepted");
        ++checks;
    }
    const char* pairs[][2] = {
        { "ALPHA", "alpha" }, { u8"Ångström", u8"ångström" },
        { u8"Σίγμα", u8"σίγμα" }, { u8"Kelvin", "kelvin" },
        { u8"𐐀", u8"𐐨" }, { u8"中", u8"中" }, { "Alpha", "Beta" }
    };
    il2cpp::utils::VmStringUtils::CaseInsensitiveComparer comparer;
    for (const auto& pair : pairs)
    {
        bool expected = comparer(pair[0], pair[1]);
        Require(NameEquals(ViewName(pair[0]), ViewName(pair[1])) == expected, "Name equality differs from real VM folding");
        NameIndex<int> index;
        index.Reserve(1); index.Add(pair[0], 123);
        Require(index.Find(pair[1]) == (expected ? 123 : 0), "NameIndex lookup differs from real VM folding");
        checks += 2;
    }
    NameIndex<int> index;
    index.Add("Alpha", 1);
    Require(index.Find("C:\\patches\\ALPHA.DLL, Version=1.2.3.4") == 1, "Normalized NameIndex lookup failed");
    return checks + 1;
}
}

int main(int argc, char** argv)
{
    try
    {
        Require(argc > 1, "Provide at least one real DLL fixture");
        size_t identityChecks = 0;
        for (int arg = 1; arg < argc; ++arg) identityChecks += CheckDll(argv[arg]);
        identityChecks += CheckMutations(argv[1]) + CheckPortablePdb();
        size_t nameChecks = CheckNames();
        std::cout << "native_identity_checks=" << identityChecks << " name_checks=" << nameChecks << " PASS\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "FAIL: " << error.what() << "\n";
        return 1;
    }
}
