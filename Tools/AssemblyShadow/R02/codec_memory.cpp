// Host attribution of unchanged profile-2 codec storage, not Unity RSS.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <new>
static bool capture = false;
static std::size_t bytes = 0, calls = 0;
static void* allocate(std::size_t size)
{
    void* p = std::malloc(size ? size : 1);
    if (!p) throw std::bad_alloc();
    if (capture) { bytes += size; ++calls; }
    return p;
}
void* operator new(std::size_t size) { return allocate(size); }
void* operator new[](std::size_t size) { return allocate(size); }
void* operator new(std::size_t size, const std::nothrow_t&) noexcept { try { return allocate(size); } catch (...) { return nullptr; } }
void* operator new[](std::size_t size, const std::nothrow_t&) noexcept { try { return allocate(size); } catch (...) { return nullptr; } }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }
void operator delete(void* p, const std::nothrow_t&) noexcept { std::free(p); }
void operator delete[](void* p, const std::nothrow_t&) noexcept { std::free(p); }
#include "hybridclr/metadata/InterpreterMetadataIndexCodec.h"
int main()
{
    using Codec = hybridclr::metadata::InterpreterMetadataIndexCodec;
    capture = true;
    Codec codec;
    capture = false;
    if (!codec.IsValid() || calls != 4 || bytes == 0) return 1;
    std::printf("{\"kind\":\"R02CodecOwnedStorage\",\"result\":\"Measured\",\"allocationCalls\":%zu,\"requestedHeapBytes\":%zu,\"codecObjectBytes\":%zu,\"pointerBytes\":%zu,\"imageCapacity\":%u,\"usablePages\":%u,\"maxChargedPages\":%u,\"runtimeAcceptance\":false,\"unityPlayerRun\":false}\n",
        calls, bytes, sizeof(Codec), sizeof(void*), Codec::kMaxImageCount, Codec::kUsablePageCount, Codec::kMaxChargedPages);
    return 0;
}
