// Host test instrumentation only. Separate translation unit avoids conflating
// global-new interposition with STL inlining under GCC's mismatch diagnostics.
#include <cstdlib>
#include <new>
bool watchNew=false;
unsigned newCalls=0;
void* operator new(size_t n) {
    if(watchNew)++newCalls;
    void* p=std::malloc(n?n:1);
    if(!p)throw std::bad_alloc();
    return p;
}
void* operator new[](size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{::operator delete(p);}
#if defined(__cpp_sized_deallocation)
void operator delete(void* p,size_t) noexcept{::operator delete(p);}
void operator delete[](void* p,size_t) noexcept{::operator delete(p);}
#endif
