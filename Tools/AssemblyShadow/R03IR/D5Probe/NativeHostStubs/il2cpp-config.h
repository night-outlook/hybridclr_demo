#pragma once
// Test-only fake export macro for compiling the D5 overlay outside Unity.
// Source-host compilation is NOT evidence the actual IL2CPP TU/Player linked.
#if defined(_WIN32)
#define IL2CPP_EXPORT __declspec(dllexport)
#else
#define IL2CPP_EXPORT __attribute__((visibility("default")))
#endif
