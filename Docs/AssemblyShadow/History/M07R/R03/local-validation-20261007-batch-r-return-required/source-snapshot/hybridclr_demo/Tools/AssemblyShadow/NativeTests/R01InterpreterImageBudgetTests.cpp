#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <string>
#include <vector>

#include "metadata/InterpreterImageBudget.h"

namespace
{
using hybridclr::metadata::InterpreterImageBudget;

size_t checks = 0;

void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "R01 budget check failed: %s\n", message);
        std::fflush(stderr);
        std::exit(1);
    }
}

bool SameState(const InterpreterImageBudget::State& left,
               const InterpreterImageBudget::State& right)
{
    return std::memcmp(&left, &right, sizeof(left)) == 0;
}

void CheckAllocation(const InterpreterImageBudget::Allocation& allocation,
                     uint32_t imageIndex, int32_t kind, const char* message)
{
    Check(allocation.IsSuccess(), message);
    Check(allocation.imageIndex == imageIndex, message);
    Check(allocation.kind == kind, message);
    Check(allocation.imageIndex != InterpreterImageBudget::kInvalidImageIndex, message);
}

void TestProfileAndBoundaries()
{
    static_assert(InterpreterImageBudget::kProfileVersion == 1, "R01 profile version changed");
    static_assert(InterpreterImageBudget::kMetadataIndexBits == 22, "R01 base bits changed");
    static_assert(InterpreterImageBudget::kMetadataKindBits == 2, "R01 kind bits changed");
    static_assert(InterpreterImageBudget::kMetadataImageIndexKindShift == 8, "R01 kind shift changed");
    static_assert(InterpreterImageBudget::kMetadataIndexMaskA == 268435455u, "R01 kind 0 mask changed");
    static_assert(InterpreterImageBudget::kMetadataIndexMaskB == 67108863u, "R01 kind 1 mask changed");
    static_assert(InterpreterImageBudget::kMetadataIndexMaskC == 16777215u, "R01 kind 2 mask changed");
    static_assert(InterpreterImageBudget::kMetadataIndexMaskD == 4194303u, "R01 kind 3 mask changed");

    const uint64_t oneMiB = 1ull << 20;
    const uint64_t fourMiB = 4ull << 20;
    const uint64_t sixteenMiB = 16ull << 20;
    const uint64_t sixtyFourMiB = 64ull << 20;

    Check(InterpreterImageBudget::GetImageKind(0) == -1, "zero has no image kind");
    Check(InterpreterImageBudget::GetImageKind(1) == 3, "one byte uses kind 3");
    Check(InterpreterImageBudget::GetImageKind(oneMiB - 1) == 3, "just below 1 MiB uses kind 3");
    Check(InterpreterImageBudget::GetImageKind(oneMiB) == 2, "1 MiB uses kind 2");
    Check(InterpreterImageBudget::GetImageKind(fourMiB - 1) == 2, "just below 4 MiB uses kind 2");
    Check(InterpreterImageBudget::GetImageKind(fourMiB) == 1, "4 MiB uses kind 1");
    Check(InterpreterImageBudget::GetImageKind(sixteenMiB - 1) == 1, "just below 16 MiB uses kind 1");
    Check(InterpreterImageBudget::GetImageKind(sixteenMiB) == 0, "16 MiB uses kind 0");
    Check(InterpreterImageBudget::GetImageKind(sixtyFourMiB - 1) == 0, "just below 64 MiB uses kind 0");
    Check(InterpreterImageBudget::GetImageKind(sixtyFourMiB) == -1, "64 MiB is outside the profile");

    const InterpreterImageBudget::State fresh = InterpreterImageBudget::FreshState();
    Check(fresh.cursors[0] == 64 && fresh.cursors[1] == 0 &&
          fresh.cursors[2] == 0 && fresh.cursors[3] == 0, "fresh cursors match production");
    Check(InterpreterImageBudget::IsValidState(fresh), "fresh state validates");

    const uint64_t sizes[] = {1, oneMiB, fourMiB, sixteenMiB};
    const uint32_t firstIndices[] = {768, 512, 256, 64};
    const int32_t kinds[] = {3, 2, 1, 0};
    for (size_t i = 0; i < 4; ++i)
    {
        InterpreterImageBudget::State state = fresh;
        CheckAllocation(InterpreterImageBudget::TryAllocate(state, sizes[i]),
                        firstIndices[i], kinds[i], "first index follows encoded kind");
    }
}

void TestHomogeneousCapacity(uint64_t size, size_t expectedCount,
                             const char* label)
{
    InterpreterImageBudget::State state = InterpreterImageBudget::FreshState();
    const int32_t requestedKind = InterpreterImageBudget::GetImageKind(size);
    size_t kindCounts[4] = {0, 0, 0, 0};
    for (size_t i = 0; i < expectedCount; ++i)
    {
        InterpreterImageBudget::Allocation allocation =
            InterpreterImageBudget::TryAllocate(state, size);
        Check(allocation.IsSuccess(), label);
        Check(allocation.kind >= 0 && allocation.kind <= 3, label);
        Check(allocation.kind <= requestedKind, "fallback only moves toward kind zero");
        Check(allocation.imageIndex != InterpreterImageBudget::kInvalidImageIndex, label);
        Check((allocation.imageIndex >> InterpreterImageBudget::kMetadataImageIndexKindShift) ==
              static_cast<uint32_t>(allocation.kind), "encoded kind matches allocation kind");
        ++kindCounts[allocation.kind];
    }

    const InterpreterImageBudget::State beforeFailure = state;
    const InterpreterImageBudget::Allocation failure =
        InterpreterImageBudget::TryAllocate(state, size);
    Check(!failure.IsSuccess() && failure.error == InterpreterImageBudget::Error::Exhausted, label);
    Check(SameState(beforeFailure, state), "failed exhausted allocation retains cursors");

    if (requestedKind == 3)
    {
        Check(kindCounts[3] == 255 && kindCounts[2] == 64 &&
              kindCounts[1] == 16 && kindCounts[0] == 3, "small-image capacity is 338");
        Check(state.cursors[3] == 255 && state.cursors[2] == 256 &&
              state.cursors[1] == 256 && state.cursors[0] == 256,
              "full small-image state retains kind 3 invalid sentinel");
    }
    else if (requestedKind == 2)
    {
        Check(kindCounts[3] == 0 && kindCounts[2] == 64 &&
              kindCounts[1] == 16 && kindCounts[0] == 3, "kind-2 capacity is 83");
    }
    else if (requestedKind == 1)
    {
        Check(kindCounts[3] == 0 && kindCounts[2] == 0 &&
              kindCounts[1] == 16 && kindCounts[0] == 3, "kind-1 capacity is 19");
    }
    else
    {
        Check(kindCounts[3] == 0 && kindCounts[2] == 0 &&
              kindCounts[1] == 0 && kindCounts[0] == 3, "kind-0 capacity is 3");
    }
}

void TestIndexProgression()
{
    const uint64_t oneMiB = 1ull << 20;
    const uint64_t fourMiB = 4ull << 20;
    const uint64_t sixteenMiB = 16ull << 20;
    InterpreterImageBudget::State state = InterpreterImageBudget::FreshState();

    CheckAllocation(InterpreterImageBudget::TryAllocate(state, 1), 768, 3,
                    "kind 3 first image index");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, oneMiB), 512, 2,
                    "kind 2 first image index");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, fourMiB), 256, 1,
                    "kind 1 first image index");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, sixteenMiB), 64, 0,
                    "kind 0 first image index");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, 1), 769, 3,
                    "kind 3 cursor increments by one");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, oneMiB), 516, 2,
                    "kind 2 cursor increments by four");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, fourMiB), 272, 1,
                    "kind 1 cursor increments by sixteen");
    CheckAllocation(InterpreterImageBudget::TryAllocate(state, sixteenMiB), 128, 0,
                    "kind 0 cursor increments by sixty-four");
}

void TestBatchAndFailureRetention()
{
    const uint64_t oneMiB = 1ull << 20;
    const uint64_t fourMiB = 4ull << 20;
    const uint64_t sixteenMiB = 16ull << 20;
    const std::vector<uint64_t> mixed = {1, oneMiB, 2, fourMiB, 3, sixteenMiB};
    const std::vector<uint64_t> reversed = {sixteenMiB, 3, fourMiB, 2, oneMiB, 1};

    InterpreterImageBudget::State initial = InterpreterImageBudget::FreshState();
    InterpreterImageBudget::Evaluation result =
        InterpreterImageBudget::Evaluate(initial, mixed);
    Check(result.IsSuccess() && result.allocations.size() == mixed.size(),
          "mixed batch succeeds");
    Check(SameState(initial, InterpreterImageBudget::FreshState()),
          "Evaluate does not mutate its initial state");
    for (size_t i = 0; i < result.allocations.size(); ++i)
        Check(result.allocations[i].imageIndex != 0, "mixed batch has no invalid index");

    InterpreterImageBudget::Evaluation reverseResult =
        InterpreterImageBudget::Evaluate(initial, reversed);
    Check(reverseResult.IsSuccess() && reverseResult.allocations.size() == reversed.size(),
          "reordered batch succeeds");
    Check(result.allocations[0].imageIndex != reverseResult.allocations[0].imageIndex,
          "allocation order affects the actual index sequence");

    const std::vector<uint64_t> partial = {1, 1, 0, 1};
    InterpreterImageBudget::Evaluation failed =
        InterpreterImageBudget::Evaluate(initial, partial);
    Check(!failed.IsSuccess() && failed.firstFailureIndex == 2 &&
          failed.firstFailure == InterpreterImageBudget::Error::InvalidSize,
          "batch reports the first failing item");
    Check(failed.allocations.size() == 2 && failed.finalState.cursors[3] == 2,
          "batch reports partial cursor consumption");
    Check(initial.cursors[3] == 0, "batch failure leaves caller state untouched");

    InterpreterImageBudget::State committed = failed.finalState;
    CheckAllocation(InterpreterImageBudget::TryAllocate(committed, 1), 770, 3,
                    "caller can explicitly commit partial dry-run state");

    InterpreterImageBudget::State consumed = InterpreterImageBudget::FreshState();
    for (size_t i = 0; i < 10; ++i)
        Check(InterpreterImageBudget::TryAllocate(consumed, 1).IsSuccess(),
              "ordinary allocation consumes shared budget");
    const InterpreterImageBudget::State beforeInvalid = consumed;
    const InterpreterImageBudget::Allocation invalid =
        InterpreterImageBudget::TryAllocate(consumed, 0);
    Check(!invalid.IsSuccess() && invalid.error == InterpreterImageBudget::Error::InvalidSize,
          "failed zero-size allocation reports invalid size");
    Check(SameState(beforeInvalid, consumed), "failed allocation does not return or consume a slot");
    CheckAllocation(InterpreterImageBudget::TryAllocate(consumed, 1), 778, 3,
                    "successful allocation retains previous consumption");
}

void TestOrdinaryFirstAndStress()
{
    const uint64_t twoMiB = 2ull << 20;
    InterpreterImageBudget::State ordinaryFirst = InterpreterImageBudget::FreshState();
    CheckAllocation(InterpreterImageBudget::TryAllocate(ordinaryFirst, twoMiB), 512, 2,
                    "ordinary interpreter allocation uses shared kind 2 bucket");
    for (size_t i = 0; i < 337; ++i)
        Check(InterpreterImageBudget::TryAllocate(ordinaryFirst, 1).IsSuccess(),
              "small allocations share ordinary budget");
    const InterpreterImageBudget::State beforeFailure = ordinaryFirst;
    const InterpreterImageBudget::Allocation failure =
        InterpreterImageBudget::TryAllocate(ordinaryFirst, 1);
    Check(!failure.IsSuccess() && failure.error == InterpreterImageBudget::Error::Exhausted,
          "ordinary-first budget rejects the 338th small image");
    Check(SameState(beforeFailure, ordinaryFirst), "ordinary-first failure retains consumption");

    const size_t stressCounts[] = {100, 300, 1000};
    for (size_t count : stressCounts)
    {
        std::vector<uint64_t> sizes(count, 1);
        InterpreterImageBudget::Evaluation result =
            InterpreterImageBudget::Evaluate(InterpreterImageBudget::FreshState(), sizes);
        if (count <= 300)
        {
            Check(result.IsSuccess() && result.allocations.size() == count,
                  "100/300 small-image stress tier succeeds");
        }
        else
        {
            Check(!result.IsSuccess() && result.firstFailureIndex == 338 &&
                  result.firstFailure == InterpreterImageBudget::Error::Exhausted &&
                  result.allocations.size() == 338,
                  "1000 small-image stress tier rejects at 338");
        }
    }
}

void TestInvalidInputsAndStates()
{
    const uint64_t quarterMax = std::numeric_limits<uint64_t>::max() / 4;
    const uint64_t max = std::numeric_limits<uint64_t>::max();
    const uint64_t fourMiB = 4ull << 20;
    const uint64_t sixtyFourMiB = 64ull << 20;
    const uint64_t invalidSizes[] = {0, sixtyFourMiB, quarterMax + 1, max};
    const InterpreterImageBudget::Error expected[] = {
        InterpreterImageBudget::Error::InvalidSize,
        InterpreterImageBudget::Error::Oversize,
        InterpreterImageBudget::Error::Overflow,
        InterpreterImageBudget::Error::Overflow,
    };
    for (size_t i = 0; i < 4; ++i)
    {
        InterpreterImageBudget::State state = InterpreterImageBudget::FreshState();
        const InterpreterImageBudget::State before = state;
        const InterpreterImageBudget::Allocation allocation =
            InterpreterImageBudget::TryAllocate(state, invalidSizes[i]);
        Check(!allocation.IsSuccess() && allocation.error == expected[i],
              "invalid size has a precise failure reason");
        Check(SameState(before, state), "invalid size does not mutate state");
    }
    Check(InterpreterImageBudget::GetImageKind(quarterMax + 1) == -1,
          "overflow input is rejected before multiplication");

    InterpreterImageBudget::State invalid = InterpreterImageBudget::FreshState();
    invalid.cursors[0] = 0;
    const InterpreterImageBudget::State invalidBefore = invalid;
    InterpreterImageBudget::Allocation allocation =
        InterpreterImageBudget::TryAllocate(invalid, 1);
    Check(!allocation.IsSuccess() && allocation.error == InterpreterImageBudget::Error::InvalidState,
          "kind zero cursor below reserved range is invalid");
    Check(SameState(invalidBefore, invalid), "invalid state is not repaired or mutated");

    invalid = InterpreterImageBudget::FreshState();
    invalid.cursors[1] = 3;
    Check(!InterpreterImageBudget::IsValidState(invalid), "misaligned kind one cursor is invalid");
    allocation = InterpreterImageBudget::TryAllocate(invalid, fourMiB);
    Check(!allocation.IsSuccess() && allocation.error == InterpreterImageBudget::Error::InvalidState,
          "misaligned state fails closed");

    invalid = InterpreterImageBudget::FreshState();
    invalid.cursors[3] = 256;
    Check(!InterpreterImageBudget::IsValidState(invalid), "kind three reserved sentinel is invalid");

    invalid = InterpreterImageBudget::FreshState();
    invalid.cursors[0] = 256;
    invalid.cursors[1] = 256;
    invalid.cursors[2] = 256;
    invalid.cursors[3] = 255;
    Check(InterpreterImageBudget::IsValidState(invalid), "fully exhausted state remains valid");
    const InterpreterImageBudget::State exhaustedBefore = invalid;
    allocation = InterpreterImageBudget::TryAllocate(invalid, 1);
    Check(!allocation.IsSuccess() && allocation.error == InterpreterImageBudget::Error::Exhausted,
          "fully exhausted state reports capacity failure");
    Check(SameState(exhaustedBefore, invalid), "capacity failure retains fully exhausted state");
}
}

int main()
{
    TestProfileAndBoundaries();
    TestHomogeneousCapacity(1, 338, "small homogeneous capacity");
    TestHomogeneousCapacity(1ull << 20, 83, "kind two homogeneous capacity");
    TestHomogeneousCapacity(4ull << 20, 19, "kind one homogeneous capacity");
    TestHomogeneousCapacity(16ull << 20, 3, "kind zero homogeneous capacity");
    TestIndexProgression();
    TestBatchAndFailureRetention();
    TestOrdinaryFirstAndStress();
    TestInvalidInputsAndStates();
    std::printf("r01_budget_checks=%zu PASS\n", checks);
    return 0;
}
