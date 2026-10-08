#include <stdint.h>

#include <cstdio>
#include <limits>
#include <stdexcept>
#include <vector>

#include "metadata/InterpreterGenericConstraintMap.h"
#include "metadata/InterpreterImageBudget.h"

namespace
{
using Map = hybridclr::metadata::InterpreterGenericConstraintMap;

int32_t EncodeOwner(uint32_t imageIndex)
{
    return static_cast<int32_t>(imageIndex << hybridclr::metadata::InterpreterImageBudget::kMetadataIndexBits);
}

uint32_t DecodeOwner(int32_t ownerIndex)
{
    return static_cast<uint32_t>(ownerIndex) >> hybridclr::metadata::InterpreterImageBudget::kMetadataIndexBits;
}

size_t checks = 0;

void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "r01b constraint check failed: %s\n", message);
        std::exit(1);
    }
}

template <typename Action>
void ExpectFailure(Action action, const char* message)
{
    bool failed = false;
    try
    {
        action();
    }
    catch (const std::runtime_error&)
    {
        failed = true;
    }
    Check(failed, message);
}

std::vector<uint32_t> RepeatedOwners(uint32_t count, uint32_t owner)
{
    return std::vector<uint32_t>(count, owner);
}

struct ProductionMapFixture
{
    explicit ProductionMapFixture(uint32_t imageIndex) : imageIndex(imageIndex) {}

    bool Build(size_t parameterCount, const std::vector<uint32_t>& owners)
    {
        parameters.assign(parameterCount, Il2CppGenericParameter());
        Map::Initialize(starts, parameters.size());
        lastBuildError = Map::Error::None;
        int32_t lastOwner = -1;
        for (size_t row = 0; row < owners.size(); ++row)
        {
            const Map::Error error = Map::RecordRow(static_cast<uint32_t>(owners[row] + 1),
                static_cast<uint32_t>(row), parameters, starts, lastOwner);
            if (error != Map::Error::None)
            {
                lastBuildError = error;
                return false;
            }
        }
        for (Il2CppGenericParameter& parameter : parameters)
            parameter.ownerIndex = EncodeOwner(imageIndex);
        rawTypeIndices.resize(owners.size());
        for (size_t i = 0; i < rawTypeIndices.size(); ++i)
            rawTypeIndices[i] = static_cast<int32_t>(100000 + i);
        return true;
    }

    int32_t Lookup(const Il2CppGenericParameter* handle, GenericParameterConstraintIndex ordinal)
    {
        uint32_t rawIndex = 0;
        const Map::Error error = ResolveError(handle, ordinal, rawIndex);
        if (error != Map::Error::None)
            throw std::runtime_error("production map rejected lookup");
        return rawTypeIndices[rawIndex];
    }

    Map::Error ResolveError(const Il2CppGenericParameter* handle,
        GenericParameterConstraintIndex ordinal, uint32_t& rawIndex) const
    {
        return Map::ResolveRawIndex(handle, imageIndex, DecodeOwner, parameters, starts,
            rawTypeIndices.size(), ordinal, rawIndex);
    }

    const Il2CppGenericParameter* Handle(size_t parameterIndex) const
    {
        return parameterIndex < parameters.size() ? &parameters[parameterIndex] : nullptr;
    }

    uint32_t imageIndex;
    std::vector<Il2CppGenericParameter> parameters;
    std::vector<uint32_t> starts;
    std::vector<int32_t> rawTypeIndices;
    Map::Error lastBuildError = Map::Error::None;
};

void TestRawStartBoundaries()
{
    ProductionMapFixture adapter(1);
    std::vector<uint32_t> owners = RepeatedOwners(32767, 0);
    owners.push_back(1);
    owners.push_back(2);
    Check(adapter.Build(3, owners), "32767/32768 setup");
    Check(adapter.Lookup(adapter.Handle(1), 0) == 132767, "32767 raw start");
    Check(adapter.Lookup(adapter.Handle(2), 0) == 132768, "32768 raw start");
    Check(adapter.Lookup(adapter.Handle(2), 0) == 132768, "stable repeated lookup");

    ProductionMapFixture pages(2);
    owners = RepeatedOwners(4095, 0);
    owners.push_back(1);
    owners.push_back(2);
    Check(pages.Build(3, owners), "4095/4096 setup");
    Check(pages.Lookup(pages.Handle(1), 0) == 104095, "4095 raw start");
    Check(pages.Lookup(pages.Handle(2), 0) == 104096, "4096 raw start");
}

void TestHandleAndOrdinalValidation()
{
    ProductionMapFixture first(3), second(4);
    std::vector<uint32_t> owners(2, 0);
    Check(first.Build(1, owners), "first image setup");
    Check(second.Build(1, owners), "second image setup");
    Check(first.Handle(0) != second.Handle(0), "equal parameter counts use distinct handles");
    Check(first.Lookup(first.Handle(0), 0) == second.Lookup(second.Handle(0), 0), "equal parameter images resolve independently");
    uint32_t rawIndex = 0;
    Check(first.ResolveError(second.Handle(0), 0, rawIndex) == Map::Error::ForeignHandle, "foreign handle error comes from production map");
    Check(first.ResolveError(first.Handle(0), static_cast<GenericParameterConstraintIndex>(-1), rawIndex) == Map::Error::InvalidOrdinal, "negative ordinal error comes from production map");
    Check(first.ResolveError(first.Handle(0), 2, rawIndex) == Map::Error::InvalidOrdinal, "ordinal range error comes from production map");
    ExpectFailure([&] { first.Lookup(second.Handle(0), 0); }, "foreign generic parameter handle rejected");
    ExpectFailure([&] { first.Lookup(first.Handle(0), static_cast<GenericParameterConstraintIndex>(-1)); }, "negative ordinal rejected");
    ExpectFailure([&] { first.Lookup(first.Handle(0), 2); }, "out of range ordinal rejected");

    ProductionMapFixture empty(5);
    Check(empty.Build(1, std::vector<uint32_t>()), "empty parameter setup");
    empty.parameters[0].constraintsCount = 1;
    empty.parameters[0].ownerIndex = EncodeOwner(5);
    ExpectFailure([&] { empty.Lookup(empty.Handle(0), 0); }, "sentinel start rejected");
}

void TestMetadataValidation()
{
    std::vector<Il2CppGenericParameter> parameters(1, Il2CppGenericParameter());
    std::vector<uint32_t> starts;
    Map::Initialize(starts, parameters.size());
    int32_t lastOwner = -1;
    Check(Map::RecordRow(0, 0, parameters, starts, lastOwner) == Map::Error::InvalidOwner,
        "zero row owner rejected by production map");

    ProductionMapFixture invalidOwner(6);
    Check(!invalidOwner.Build(1, std::vector<uint32_t>(1, 1)), "row owner rejected");
    Check(invalidOwner.lastBuildError == Map::Error::InvalidOwner, "invalid owner error comes from production map");

    ProductionMapFixture noncontiguous(7);
    std::vector<uint32_t> owners = { 0, 1, 0 };
    Check(!noncontiguous.Build(2, owners), "noncontiguous owner group rejected");
    Check(noncontiguous.lastBuildError == Map::Error::NonContiguousOwner, "noncontiguous error comes from production map");

    ProductionMapFixture tooMany(8);
    owners = RepeatedOwners(32768, 0);
    Check(!tooMany.Build(1, owners), "int16 constraint count overflow rejected");
    Check(tooMany.lastBuildError == Map::Error::CountOverflow, "count overflow comes from production map");
}

void TestRawRangeValidation()
{
    ProductionMapFixture fixture(9);
    Check(fixture.Build(1, std::vector<uint32_t>(1, 0)), "raw range setup");
    uint32_t rawIndex = 0;
    fixture.parameters[0].ownerIndex = EncodeOwner(10);
    Check(fixture.ResolveError(fixture.Handle(0), 0, rawIndex) == Map::Error::ForeignHandle,
        "in-vector handle with foreign encoded owner rejected");
    fixture.parameters[0].ownerIndex = EncodeOwner(9);

    std::vector<uint32_t> truncated;
    Check(Map::ResolveRawIndex(fixture.Handle(0), 9, DecodeOwner, fixture.parameters, truncated,
        1, 0, rawIndex) == Map::Error::InvalidSidecar, "truncated sidecar rejected");

    fixture.starts[0] = static_cast<uint32_t>(fixture.rawTypeIndices.size());
    Check(fixture.ResolveError(fixture.Handle(0), 0, rawIndex) == Map::Error::InvalidRawRange,
        "raw start at total rejected");
    fixture.starts[0] = static_cast<uint32_t>(fixture.rawTypeIndices.size() + 1);
    Check(fixture.ResolveError(fixture.Handle(0), 0, rawIndex) == Map::Error::InvalidRawRange,
        "raw start past total rejected");

    Il2CppGenericParameter overflowParameter = {};
    overflowParameter.ownerIndex = EncodeOwner(11);
    overflowParameter.constraintsCount = 3;
    std::vector<Il2CppGenericParameter> overflowParameters(1, overflowParameter);
    std::vector<uint32_t> overflowStarts(1, std::numeric_limits<uint32_t>::max() - 1);
    Check(Map::ResolveRawIndex(&overflowParameters[0], 11, DecodeOwner, overflowParameters,
        overflowStarts, std::numeric_limits<uint32_t>::max(), 2, rawIndex) == Map::Error::InvalidRawRange,
        "raw index addition overflow rejected");
}

void TestNativeLayoutRemainsNarrow()
{
    Il2CppGenericParameter native = {};
    native.constraintsStart = static_cast<GenericParameterConstraintIndex>(32767);
    native.constraintsCount = 1;
    Check(sizeof(native.constraintsStart) == sizeof(int16_t), "AOT constraintsStart remains int16");
    Check(native.constraintsStart == 32767 && native.constraintsCount == 1, "AOT narrow field remains usable");
}
}

int main()
{
    TestRawStartBoundaries();
    TestHandleAndOrdinalValidation();
    TestMetadataValidation();
    TestRawRangeValidation();
    TestNativeLayoutRemainsNarrow();
    std::printf("r01b_constraint_checks=%zu PASS\n", checks);
    return 0;
}
