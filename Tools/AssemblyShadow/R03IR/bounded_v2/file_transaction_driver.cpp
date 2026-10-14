// Host driver only. Synthetic inputs are loaded before testing the native transaction.
#include "BoundedFileTransactionV2.h"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <new>
#include <string>
#include <vector>
using namespace r03_diag_v2;
using namespace r03_diag_v2::files;
static bool forbiddenNew=false;
static unsigned allocationCalls=0;
void* operator new(std::size_t n){if(forbiddenNew){++allocationCalls;std::abort();}if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete[](void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
void operator delete[](void* p,std::size_t) noexcept {std::free(p);}
static std::vector<uint8_t> Read(const char* p){std::ifstream in(p,std::ios::binary);if(!in)throw std::runtime_error("input");return {std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>()};}
static std::string Hex(Digest h){constexpr char c[]="0123456789abcdef";std::string s;for(uint8_t x:h){s+=c[x>>4];s+=c[x&15];}return s;}
static Digest Parse(const char* s){if(std::strlen(s)!=64)throw std::runtime_error("hex length");Digest d{};for(unsigned i=0;i<64;++i){const char* p=std::strchr("0123456789abcdef",s[i]);if(!p)throw std::runtime_error("hex");d[i/2]=uint8_t((d[i/2]<<4)|unsigned(p-"0123456789abcdef"));}return d;}
struct Fault {
    size_t count=0,failAt=0,writeCalls=0;const char* mode="normal";const char* root=nullptr;
    unsigned per[8][3]{};bool acted=false;Transaction* tx=nullptr;
    const uint8_t* input=nullptr;size_t inputBytes=0;FieldView (*fields)[2]=nullptr;uint8_t* scratch=nullptr;
};
static bool GateCall(void* data,Stage stage,Target target) noexcept {
    auto& f=*static_cast<Fault*>(data);++f.count;const unsigned times=++f.per[unsigned(stage)][unsigned(target)];
    if(f.failAt==f.count)return false;
    if(f.acted)return true;
    if(stage==Stage::Write && target==Target::Artifact && !std::strcmp(f.mode,"reentry")){
        f.acted=true;Publication nested;f.tx->Seal(f.input,f.inputBytes,*f.fields,f.scratch,kFrame,nested);return true;
    }
    if(stage==Stage::Verify && target==Target::Artifact && times==3){
        const int dir=::open(f.root,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);if(dir<0)return false;
        if(!std::strcmp(f.mode,"replace")){
            f.acted=true;::renameat(dir,kArtifactName,dir,"retained-original.bin");
            int fd=::openat(dir,kArtifactName,O_CREAT|O_EXCL|O_WRONLY,0600);if(fd>=0)::close(fd);
        }else if(!std::strcmp(f.mode,"hardlink")){
            if(::linkat(dir,kArtifactName,dir,"extra-link.bin",0)!=0){::close(dir);return false;}
            f.acted=true;
        }else if(!std::strcmp(f.mode,"corrupt")){
            int fd=::openat(dir,kArtifactName,O_WRONLY|O_NOFOLLOW);
            if(fd<0){::close(dir);return false;}
            const char x='X';const ssize_t changed=::pwrite(fd,&x,1,0);const int closed=::close(fd);
            if(changed!=1 || closed!=0){::close(dir);return false;}
            f.acted=true;
        }
        ::close(dir);
    }
    if(stage==Stage::Encode && target==Target::Artifact && !std::strcmp(f.mode,"root-replace")){
        f.acted=true;char saved[kPathBytes+32]{};std::snprintf(saved,sizeof saved,"%s.original",f.root);
        if(::rename(f.root,saved)!=0 || ::mkdir(f.root,0700)!=0)return false;
    }
    return true;
}
static ssize_t WriteTest(void* data,int fd,const uint8_t* bytes,size_t count) noexcept {
    auto& f=*static_cast<Fault*>(data);++f.writeCalls;
    if(!std::strcmp(f.mode,"short-write"))return ::write(fd,bytes,count>7?7:count);
    if(!std::strcmp(f.mode,"eintr-always") || (!std::strcmp(f.mode,"eintr-once") && f.writeCalls==1)){
        errno=EINTR;return -1;
    }
    if(!std::strcmp(f.mode,"zero-write"))return 0;
    if(!std::strcmp(f.mode,"partial-error")){
        if(f.writeCalls==1)return ::write(fd,bytes,count>3?3:count);
        errno=EIO;return -1;
    }
    if(!std::strcmp(f.mode,"inline-mutation") && !f.acted){
        f.acted=true;const_cast<uint8_t*>(f.input)[1]='X';
    }
    return ::write(fd,bytes,count);
}
static void Id(const FileIdentity& i){std::cout<<"{\"device\":"<<i.device<<",\"inode\":"<<i.inode<<",\"owner\":"<<i.owner<<",\"mode\":"<<i.mode<<"}";}
int main(int argc,char** argv){
    if(argc!=8)return 90;
    try{
        auto in=Read(argv[3]);auto a=Read(argv[4]);auto b=Read(argv[5]);
        const Digest context=Parse(argv[2]);struct stat d{};if(::stat(argv[1],&d)!=0)return 91;
        FileIdentity expected=Identity(d);if(!std::strcmp(argv[6],"wrong-root"))++expected.inode;
        FieldView fields[2]={{a.data(),a.size(),false},{b.data(),b.size(),false}};
        if(!std::strcmp(argv[6],"null")){fields[0]={nullptr,0,true};fields[1]={nullptr,0,true};}
        std::vector<uint8_t> scratch(kFrame);Fault f;f.mode=argv[6];f.root=argv[1];
        f.failAt=std::strtoull(argv[7],nullptr,10);f.input=in.data();f.inputBytes=in.size();f.fields=&fields;f.scratch=scratch.data();
        Transaction tx(GateCall,&f,WriteTest,&f);f.tx=&tx;Publication receipt;
        forbiddenNew=true;
        bool armed=tx.Arm(argv[1],expected,context);
        const uint8_t* inlineInput=in.data();
        if(!std::strcmp(f.mode,"inline-overlap") && in.size()<=scratch.size()){
            std::memcpy(scratch.data(),in.data(),in.size());inlineInput=scratch.data();
        }
        bool passed=armed && tx.Seal(inlineInput,in.size(),fields,scratch.data(),scratch.size(),receipt);
        bool reuseRejected=true;
        if(passed && !std::strcmp(f.mode,"reuse")){Publication again;reuseRejected=!tx.Seal(in.data(),in.size(),fields,scratch.data(),scratch.size(),again)&&!again.complete;}
        forbiddenNew=false;const FirstFailure failure=tx.failure();
        std::cout<<"{\"armed\":"<<(armed?"true":"false")<<",\"complete\":"<<(passed&&receipt.complete?"true":"false")
            <<",\"error\":"<<unsigned(failure.error)<<",\"stage\":"<<unsigned(failure.stage)<<",\"target\":"<<unsigned(failure.target)
            <<",\"errno\":"<<failure.systemError<<",\"artifactWrittenAtFirstError\":"<<failure.artifactWritten
            <<",\"envelopeWrittenAtFirstError\":"<<failure.envelopeWritten<<",\"gateCalls\":"<<f.count<<",\"writeCalls\":"<<f.writeCalls
            <<",\"faultActed\":"<<(f.acted?"true":"false")<<",\"reuseRejected\":"<<(reuseRejected?"true":"false")
            <<",\"operatorNewCalls\":"<<allocationCalls<<",\"context\":\""<<Hex(receipt.context)<<"\",\"inlineHash\":\""<<Hex(receipt.inlineHash)
            <<"\",\"artifact\":{\"bytes\":"<<receipt.artifact.bytes<<",\"sha256\":\""<<Hex(receipt.artifact.sha256)
            <<"\"},\"envelope\":{\"bytes\":"<<receipt.envelope.bytes<<",\"sha256\":\""<<Hex(receipt.envelope.sha256)<<"\"},\"directory\":";
        Id(receipt.directory);std::cout<<",\"artifactFile\":";Id(receipt.artifactFile);std::cout<<",\"envelopeFile\":";Id(receipt.envelopeFile);
        std::cout<<",\"powerLossTested\":false,\"semanticAcceptance\":false}\n";
        return 0; // Host assertion layer requires the exact expected result, not this exit alone.
    }catch(const std::exception& e){forbiddenNew=false;std::cerr<<e.what()<<'\n';return 92;}
}
