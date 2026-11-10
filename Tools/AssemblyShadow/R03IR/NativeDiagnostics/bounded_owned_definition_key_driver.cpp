// Standalone R03 B2 host regression, NEVER install in libil2cpp/vm.
// The raw TypeKey views are synthetic, not actual Il2CppClass source evidence.
#include "BoundedOwnedDefinitionTypeKey.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>

static bool inProtectedRegion = false;
static unsigned protectedAllocations = 0, tests = 0;
void* operator new(std::size_t n) {
    if(inProtectedRegion) { ++protectedAllocations; std::abort(); }
    if(void* p=std::malloc(n?n:1))return p;
    throw std::bad_alloc();
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }

using namespace r03_b2_owned_definition_key;
static void Check(bool ok) { ++tests; if(!ok) std::abort(); }
static ByteView View(const char* text) { return ByteView{text,std::strlen(text)}; }
static bool Equal(const Capture& c,const char* expected) {
    return c.Complete() && c.Data() && c.Bytes()==std::strlen(expected) &&
           std::memcmp(c.Data(),expected,c.Bytes())==0;
}
static void TestDefinition(const char* assembly,const char* ns,const char* name,
                           uint32_t arity,const char* expected) {
    Capture c;
    inProtectedRegion = true;
    const bool result=c.Begin(View(assembly),true,false,false) &&
        c.AddDeclaration(View(ns),View(name),arity) && c.Seal();
    inProtectedRegion = false;
    Check(result && Equal(c,expected));
}
static void TestHappy() {
    TestDefinition("Assembly-CSharp","Demo","Widget",0,
                   "type(15:assembly-csharp/4:Demo/6:Widget@0)");
    TestDefinition("C:\\unity\\MyGame.DLL, Version=1.2","", "Widget",2,
                   "type(6:mygame/0:/6:Widget@2)");
    TestDefinition("/x/RENDER.ExE","UI","Panel",1,
                   "type(6:render/2:UI/5:Panel@1)");
    TestDefinition("case Sensitive","C","T",0,
                   "type(14:case sensitive/1:C/1:T@0)");
    TestDefinition("pkg.dll","C","A",UINT32_MAX,
                   "type(3:pkg/1:C/1:A@4294967295)");
    const char* unicodeNs=u8"mê";
    const char* unicodeName=u8"高😀";
    Capture utf8;
    Check(utf8.Begin(View("Pkg"),true,false,false));
    Check(utf8.AddDeclaration(View(unicodeNs),View(unicodeName),0));
    Check(utf8.Seal());
    Check(Equal(utf8,u8"type(3:pkg/3:mê/7:高😀@0)"));
    Capture nested;
    Check(nested.Begin(View("Package"),true,false,false));
    Check(nested.AddDeclaration(View("A"),View("Outer"),1));
    Check(nested.AddDeclaration(View(""),View("Inner"),0));
    Check(nested.Seal());
    Check(Equal(nested,"type(7:package/1:A/5:Outer@1/0:/5:Inner@0)"));
}
static void TestReject() {
    {
        Capture c;
        Check(!c.Begin(View("Pkg"),false,false,false));
        Check(c.FirstError()==Error::UnsupportedShape && !c.Data());
    }
    {
        Capture c;
        Check(!c.Begin(View("Pkg"),true,true,false));
        Check(c.FirstError()==Error::UnsupportedShape);
    }
    {
        Capture c;
        Check(!c.Begin(View("Pkg"),true,false,true));
        Check(c.FirstError()==Error::UnsupportedShape);
    }
    {
        Capture c;
        Check(!c.Begin(View(""),true,false,false));
        Check(c.FirstError()==Error::MissingSource);
    }
    {
        Capture c;
        Check(!c.Begin(View("C:\\x\\, Version=1"),true,false,false));
        Check(c.FirstError()==Error::InvalidAssembly);
    }
    {
        Capture c;
        Check(!c.Begin(View(u8"Xä"),true,false,false));
        Check(c.FirstError()==Error::NonAsciiAssembly);
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        Check(!c.Seal());
        Check(c.FirstError()==Error::NotComplete && !c.Data());
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        const char invalid[]={'A',char(0xc0),char(0xaf)};
        Check(!c.AddDeclaration(View("C"),ByteView{invalid,sizeof invalid},0));
        Check(c.FirstError()==Error::InvalidUtf8 && !c.Data());
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        const char embedded[]={'A','\0','B'};
        Check(!c.AddDeclaration(View("C"),ByteView{embedded,sizeof embedded},0));
        Check(c.FirstError()==Error::InvalidUtf8);
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        Check(!c.AddDeclaration(View("C"),ByteView{nullptr,0},0));
        Check(c.FirstError()==Error::InvalidDeclaration);
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        Check(!c.AddDeclaration(View("C"),ByteView{reinterpret_cast<const char*>(&c),2},0));
        Check(c.FirstError()==Error::Alias && !c.Complete());
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        char huge[4097];std::memset(huge,'x',sizeof huge);
        Check(!c.AddDeclaration(View("C"),ByteView{huge,sizeof huge},0));
        Check(c.FirstError()==Error::Capacity && !c.Data());
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        for(size_t i=0;i<Capture::kMaximumDeclarations;++i)
            Check(c.AddDeclaration(View(""),View("A"),0));
        Check(!c.AddDeclaration(View(""),View("A"),0));
        Check(c.FirstError()==Error::TooDeep);
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        Check(c.AddDeclaration(View(""),View("Type"),0));
        Check(c.Seal());
        Check(!c.Begin(View("Other"),true,false,false));
        Check(c.FirstError()==Error::Reused && !c.Data());
    }
    {
        Capture c;
        Check(c.Begin(View("Pkg"),true,false,false));
        Check(c.AddDeclaration(View(""),View("Type"),0));
        Check(c.Seal());
        Check(!c.Revoke());
        Check(c.FirstError()==Error::UnsupportedShape && !c.Data());
    }
}
int main() {
    TestHappy();
    TestReject();
    Check(protectedAllocations==0);
    std::printf("{\"kind\":\"R03B2BoundedOwnedDefinitionTypeKeyHost\","
                "\"result\":\"PassedLimitedGrammarOnly\","
                "\"assertions\":%u,\"protectedAllocations\":%u,"
                "\"physicalMetadataSourceProven\":false,"
                "\"completeNonemptyExecutionSource\":false,"
                "\"nativeV2TransportImplemented\":false,\"runtimeAcceptance\":false}\n",
                tests,protectedAllocations);
    return 0;
}
