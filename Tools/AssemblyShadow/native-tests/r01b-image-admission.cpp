#include "metadata/InterpreterImageAdmission.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <vector>

using Admission = hybridclr::metadata::InterpreterImageAdmission;
static unsigned checks = 0;
static void Check(bool value)
{
    ++checks;
    if (!value) std::abort();
}
int main()
{
    std::vector<uint64_t> sizes(8192, 65536);
    for (uint32_t retained : {0u, 1u, 4096u, 8191u, 8192u})
    {
        size_t remaining = 8192u - retained;
        auto report = Admission::Evaluate(retained, sizes.data(), remaining);
        Check(report.IsSuccess());
        Check(report.reservedImageCountAfter == 8192);
        Check(report.runtimeFinalizationRequired);
        report = Admission::Evaluate(retained, sizes.data(), remaining + 1);
        Check(report.error == Admission::Error::ImageLimit);
        Check(report.firstFailureIndex == remaining);
        Check(report.reservedImageCountAfter == retained);
    }
    for (size_t failure : {size_t(0), size_t(4095), size_t(8191)})
    {
        sizes[failure] = 0;
        auto report = Admission::Evaluate(0, sizes.data(), sizes.size());
        Check(report.error == Admission::Error::EmptyDll);
        Check(report.firstFailureIndex == failure);
        Check(report.reservedImageCountAfter == 0);
        sizes[failure] = Admission::kMaximumDllBytes + 1;
        report = Admission::Evaluate(0, sizes.data(), sizes.size());
        Check(report.error == Admission::Error::DllTooLarge);
        Check(report.firstFailureIndex == failure);
        sizes[failure] = 65536;
    }
    uint64_t size = Admission::kMaximumDllBytes;
    Check(Admission::Evaluate(8191, &size, 1).IsSuccess());
    size = std::numeric_limits<uint64_t>::max();
    Check(Admission::Evaluate(8191, &size, 1).error == Admission::Error::DllTooLarge);
    Check(Admission::Evaluate(0, &size, std::numeric_limits<size_t>::max()).error == Admission::Error::ImageLimit);
    Check(Admission::Evaluate(UINT32_MAX, nullptr, 0).error == Admission::Error::InvalidState);
    Check(Admission::Evaluate(0, nullptr, 1).error == Admission::Error::InvalidInput);
    Check(Admission::Evaluate(8192, nullptr, 0).IsSuccess());
    // Preliminary admission cannot turn DLL bytes into a final index/RAM budget.
    sizes.assign(8192, uint64_t(Admission::kMaximumDllBytes));
    auto report = Admission::Evaluate(0, sizes.data(), sizes.size());
    Check(report.IsSuccess() && report.runtimeFinalizationRequired);
    std::printf("r01b_image_admission_checks=%u PASS\n", checks);
}
