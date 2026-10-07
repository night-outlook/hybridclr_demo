#include "metadata/InterpreterTypeCacheInsertion.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <new>
#include <stdexcept>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

namespace
{
using Cache = hybridclr::metadata::InterpreterTypeCacheInsertion;
using Pointer = const int*;
using BaseMap = std::unordered_map<Pointer, uint32_t>;

bool failAlloc = false;
size_t checks = 0;

void* Allocate(std::size_t size)
{
    if (failAlloc)
        throw std::bad_alloc();
    void* result = std::malloc(size == 0 ? 1 : size);
    if (result == nullptr)
        throw std::bad_alloc();
    return result;
}
}

void* operator new(std::size_t size) { return Allocate(size); }
void* operator new[](std::size_t size) { return Allocate(size); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
#if __cplusplus >= 201402L
void operator delete(void* pointer, std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { std::free(pointer); }
#endif

namespace
{
void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "r01b type-cache check failed: %s\n", message);
        std::exit(1);
    }
}

struct ThrowingMap
{
    using iterator = BaseMap::iterator;

    iterator find(Pointer pointer) { return values.find(pointer); }
    iterator end() { return values.end(); }
    std::pair<iterator, bool> insert(const std::pair<Pointer, uint32_t>& value)
    {
        if (throwInsert)
            throw std::bad_alloc();
        return values.insert(value);
    }
    size_t size() const { return values.size(); }
    bool empty() const { return values.empty(); }

    BaseMap values;
    bool throwInsert = false;
};

struct Encoder
{
    mutable uint32_t calls = 0;
    bool throwError = false;
    uint32_t bias = 1000;

    uint32_t operator()(uint32_t index) const
    {
        ++calls;
        if (throwError)
            throw std::runtime_error("encoder failure");
        return bias + index;
    }
};

template<typename Action>
void ExpectBadAlloc(Action action, const char* message)
{
    bool raised = false;
    try
    {
        action();
    }
    catch (const std::bad_alloc&)
    {
        raised = true;
    }
    Check(raised, message);
}

void TestVectorReserveFailure()
{
    std::vector<Pointer> types;
    ThrowingMap indices;
    int value = 1;
    Encoder encoder;
    failAlloc = true;
    ExpectBadAlloc([&] { Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder); },
        "vector reserve bad_alloc propagates");
    failAlloc = false;
    Check(types.empty() && indices.empty(), "vector reserve failure leaves logical state unchanged");
    const uint32_t encoded = Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder);
    Check(encoded == 1000 && types.size() == 1 && indices.size() == 1,
        "successful retry inserts one entry");
}

void TestEncoderFailure()
{
    std::vector<Pointer> types;
    ThrowingMap indices;
    int value = 2;
    Encoder encoder;
    encoder.throwError = true;
    bool raised = false;
    try
    {
        Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder);
    }
    catch (const std::runtime_error&)
    {
        raised = true;
    }
    Check(raised, "encoder failure propagates");
    Check(types.empty() && indices.empty(), "encoder failure leaves logical state unchanged");
    encoder.throwError = false;
    Check(Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder) == 1000 &&
        types.size() == 1 && indices.size() == 1,
        "encoder failure supports successful retry");
}

void TestMapInsertFailure()
{
    std::vector<Pointer> types;
    ThrowingMap indices;
    int value = 3;
    Encoder encoder;
    types.reserve(1);
    indices.throwInsert = true;
    ExpectBadAlloc([&] { Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder); },
        "map insert bad_alloc propagates");
    indices.throwInsert = false;
    Check(types.empty() && indices.empty(), "map insert failure leaves logical state unchanged");
    Check(Cache::GetOrInsert(types, indices, static_cast<Pointer>(&value), encoder) == 1000 &&
        types.size() == 1 && indices.size() == 1,
        "map insert failure supports successful retry");
}

void TestDedupAndGrowth()
{
    std::vector<Pointer> types;
    ThrowingMap indices;
    int values[96] = {};
    Encoder encoder;
    for (uint32_t i = 0; i < 64; ++i)
    {
        Check(Cache::GetOrInsert(types, indices, static_cast<Pointer>(&values[i]), encoder) == 1000 + i,
            "distinct pointer gets stable encoded index");
    }
    const size_t sizeBeforeDedup = types.size();
    const uint32_t callsBeforeDedup = encoder.calls;
    Check(Cache::GetOrInsert(types, indices, static_cast<Pointer>(&values[17]), encoder) == 1017,
        "equivalent key deduplicates");
    Check(types.size() == sizeBeforeDedup && indices.size() == sizeBeforeDedup &&
        encoder.calls == callsBeforeDedup,
        "dedup does not encode or grow vectors");
    Check(types.capacity() >= types.size() && types.capacity() < 96,
        "capacity growth remains amortized");
}

void TestSerializedConcurrentWriters()
{
    std::vector<int> values(128);
    std::vector<Pointer> types;
    ThrowingMap indices;
    std::mutex mutex;
    Encoder encoder;
    std::vector<std::thread> workers;
    for (int worker = 0; worker < 4; ++worker)
    {
        workers.emplace_back([&] {
            for (uint32_t i = 0; i < values.size(); ++i)
            {
                std::lock_guard<std::mutex> guard(mutex);
                Cache::GetOrInsert(types, indices, static_cast<Pointer>(&values[i]), encoder);
            }
        });
    }
    for (std::thread& worker : workers)
        worker.join();
    Check(types.size() == values.size() && indices.size() == values.size(),
        "serialized concurrent writers retain one entry per equivalent key");
}
}

int main()
{
    TestVectorReserveFailure();
    TestEncoderFailure();
    TestMapInsertFailure();
    TestDedupAndGrowth();
    TestSerializedConcurrentWriters();
    std::printf("r01b_type_cache_checks=%zu PASS\n", checks);
    return 0;
}
