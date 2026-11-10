// Standalone pure B2 row ownership tests, not a VM class source.
#include "BoundedOwnedExecutionRows.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <type_traits>

static bool protect=false;
static unsigned allocations=0, assertions=0;
void* operator new(std::size_t n){
    if(protect){++allocations;std::abort();}
    if(void* p=std::malloc(n?n:1))return p;
    throw std::bad_alloc();
}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
void operator delete[](void* p,std::size_t) noexcept{std::free(p);}

using namespace r03_b2_owned_execution_rows;
static_assert(!std::is_copy_constructible<Rows>::value,"Rows must be single owner");
static_assert(!std::is_copy_constructible<Capture>::value,"TypeKey must be single owner");
static void Check(bool okay){++assertions;if(!okay)std::abort();}
static ByteView V(const char* x){return ByteView{x,std::strlen(x)};}
static bool Equal(ByteView text,const char* expected) {
    return text.data && text.size==std::strlen(expected)&&
           std::memcmp(text.data,expected,text.size)==0;
}
static void Key(Capture& key,const char* name) {
    Check(key.Begin(V("Assembly-CSharp"),true,false,false));
    Check(key.AddDeclaration(V("Game"),V(name),0));
    Check(key.Seal());
}
static void Happy() {
    Capture first,second;
    Key(first,"Player");Key(second,"Monster");
    Flags a{};a.interpreterShadow=true;a.isActive=true;
    a.cctorStarted=true;a.staticStorageAvailable=true;
    Flags b{};b.physicalInterpreter=true;b.cctorFinished=true;
    b.hasInitializationException=true;b.pointerDetailsAvailable=true;
    Rows rows;RowView view{};
    Check(rows.Begin(2));
    Check(!rows.Get(0,view) && rows.Count()==0);
    protect=true;
    const bool ok1=rows.Add(300,Source::Candidate,V("Assembly-CSharp"),
                            first,V("0x1234"),a);
    const bool ok2=rows.Add(11,Source::ActiveShadow,V("Methods"),
                            second,V(""),b);
    const bool sealed=rows.Seal();
    protect=false;
    Check(ok1&&ok2&&sealed);
    Check(rows.Complete()&&rows.Count()==2&&rows.TextBytes()>0);
    Check(rows.Get(0,view));
    Check(view.registrySlot==11&&view.source==Source::ActiveShadow);
    Check(Equal(view.logicalAssembly,"Methods"));
    Check(Equal(view.typeKey,"type(15:assembly-csharp/4:Game/7:Monster@0)"));
    Check(view.fields.physicalInterpreter&&view.fields.cctorFinished);
    Check(view.fields.hasInitializationException&&view.fields.pointerDetailsAvailable);
    Check(rows.Get(1,view));
    Check(view.registrySlot==300&&view.source==Source::Candidate);
    Check(Equal(view.logicalAssembly,"Assembly-CSharp"));
    Check(Equal(view.typeKey,"type(15:assembly-csharp/4:Game/6:Player@0)"));
    Check(Equal(view.staticStoragePointer,"0x1234"));
    Check(view.fields.interpreterShadow&&view.fields.isActive);
    Check(view.fields.cctorStarted&&view.fields.staticStorageAvailable);
    Check(!rows.Get(2,view));
    // Original TypeKey bytes are no longer needed after successful copy.
    Check(!first.Revoke()&&!second.Revoke());
    Check(rows.Get(1,view));
    Check(Equal(view.typeKey,"type(15:assembly-csharp/4:Game/6:Player@0)"));
}
static void Reject() {
    Capture key;Key(key,"Item");
    Flags bits{};
    {
        Rows r;Check(!r.Begin(kMaximumRows+1));
        Check(r.FirstError()==Error::InvalidCount);
    }
    {
        Rows r;RowView v{};Check(r.Begin(2));
        Check(r.Add(9,Source::Candidate,V("Methods"),key,V(""),bits));
        Check(!r.Add(9,Source::Candidate,V("Methods"),key,V(""),bits));
        Check(r.FirstError()==Error::DuplicateSlot && !r.Get(0,v));
    }
    {
        Rows r;Check(r.Begin(1));
        Check(!r.Add(2048,Source::Candidate,V("Methods"),key,V(""),bits));
        Check(r.FirstError()==Error::InvalidSlot);
    }
    {
        Rows r;Check(r.Begin(1));
        Check(!r.Add(2,static_cast<Source>(55),V("Methods"),key,V(""),bits));
        Check(r.FirstError()==Error::UnsupportedRole);
    }
    {
        Rows r;Check(r.Begin(2));
        Check(r.Add(9,Source::Candidate,V("Methods"),key,V(""),bits));
        Check(!r.Seal() && r.FirstError()==Error::CountMismatch);
    }
    {
        Rows r;Check(r.Begin(1));
        Check(!r.Add(2,Source::Candidate,V(""),key,V(""),bits));
        Check(r.FirstError()==Error::MissingText);
    }
    {
        Rows r;Check(r.Begin(1));
        Check(!r.Add(2,Source::Candidate,ByteView{reinterpret_cast<const char*>(&r),3},
                     key,V(""),bits));
        Check(r.FirstError()==Error::AliasedInput);
    }
    {
        Rows r;Check(r.Begin(1));
        const char bad[]={char(0xc0),char(0xaf)};
        Check(!r.Add(2,Source::Candidate,ByteView{bad,sizeof bad},key,V(""),bits));
        Check(r.FirstError()==Error::InvalidUtf8);
    }
    {
        Capture incomplete;
        Rows r;Check(r.Begin(1));
        Check(!r.Add(2,Source::Candidate,V("Methods"),incomplete,V(""),bits));
        Check(r.FirstError()==Error::IncompleteDefinitionKey);
    }
    {
        Rows r;Check(r.Begin(0));Check(r.Seal());
        Check(r.Complete()&&r.Count()==0);
        Check(!r.Begin(0)&&r.FirstError()==Error::Reused);
    }
    {
        Rows r;RowView view{};Check(r.Begin(1));
        Check(r.Add(2,Source::Candidate,V("Methods"),key,V(""),bits));
        Check(r.Seal());Check(r.Get(0,view));
        Check(!r.Revoke()&&r.FirstError()==Error::NotComplete);
        Check(!r.Get(0,view) && r.TextBytes()==0);
    }
    {
        // Strict 256KiB shared owned-text cap; no clipped or partial rows.
        char longName[3500];std::memset(longName,'Z',sizeof longName);
        Capture large;
        Check(large.Begin(V("Pkg"),true,false,false));
        Check(large.AddDeclaration(V(""),ByteView{longName,sizeof longName},0));
        Check(large.Seal());
        Rows r;Check(r.Begin(100));
        bool failed=false;
        protect=true;
        for(size_t i=0;i<100;++i) {
            if(!r.Add(i,Source::Candidate,V("Pkg"),large,V(""),bits)) {
                failed=true;break;
            }
        }
        protect=false;
        Check(failed&&r.FirstError()==Error::TextCapacity);
        Check(!r.Complete()&&r.TextBytes()==0);
    }
}
int main(){
    Happy();Reject();
    Check(allocations==0);
    std::printf("{\"kind\":\"R03B2OwnedExecutionRowsHost\","
                "\"result\":\"PassedOwnedNonemptyRowsOnly\","
                "\"assertions\":%u,\"protectedAllocations\":%u,"
                "\"realPhysicalClassOriginProven\":false,"
                "\"canonicalGenericExecutionTypeKeysComplete\":false,"
                "\"fullFinalExecutionDiagnostics\":false,"
                "\"nativeV2TransportImplemented\":false,"
                "\"runtimeAcceptance\":false}\n",assertions,allocations);
}
