// Wire producer is the actual native header, not a manually reconstructed R02 object.
#include "AssemblyShadowR02Diagnostics.h"
#include <iostream>
#include <string>
#include <thread>
#include <cstdint>
using namespace il2cpp::vm::assembly_shadow_r02;
int main(int argc, char** argv)
{
    if (argc != 2) return 2;
    std::string mode(argv[1]);
    if (mode == "normal") ObservationCounters::Add(Metric::AdmissionHits, UINT64_MAX - 1);
    else if (mode == "saturated") {
        ObservationCounters::Add(Metric::AdmissionHits, UINT64_MAX);
        ObservationCounters::Add(Metric::AdmissionHits, 1);
    }
    else if (mode == "truncated") {
        for (int i = 0; i < 130; ++i) {
            std::thread worker([] { ObservationCounters::Add(Metric::AdmissionHits, 1); });
            worker.join();
        }
    }
    else if (mode == "classes") ObservationCounters::Add(Metric::DroppedClasses, 1);
    else if (mode != "legacy") return 2;
    // The outer legacy schema is a host fixture; only AppendDiagnostics is a
    // real native runtime producer. No VM integration is claimed here.
    std::cout << R"({"schemaVersion":1,"logicalAssembly":"Test","executionModeCode":0,"executionMode":"AotBaseline","isActive":true,"physicalImageKind":"Aot","typeKey":"Test.Type","inputTypePointer":"","activeTypePointer":"","baselineTypePointer":"","pointerDetailsAvailable":false,"baselinePointerAvailable":false,"containsShadowTypes":false,"definitionCacheHits":18446744073709551615,"definitionCacheMisses":0,"compositeRebuilds":0,"allocationRemaps":0,"guardFailures":0)";
    if (mode != "legacy") AppendDiagnostics(std::cout);
    std::cout << "}" << std::endl;
    return 0;
}
