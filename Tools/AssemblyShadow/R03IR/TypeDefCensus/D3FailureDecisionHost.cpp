// R03 B2 D3: exact native no-throw classification header.
// Deliberately independent of mocked Runtime/VM and usable with -fno-exceptions.
#include "AssemblyShadowPublicationD3Decision.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
using namespace il2cpp::vm::assembly_shadow_publication;
static unsigned checks=0;
static void Check(bool x){++checks;if(!x)std::abort();}
int main(int argc,char**argv)
{
    if(argc!=2)return 2;
    PublicationPhaseReceipt r;
    const char* mode=argv[1];
    if (!std::strcmp(mode,"used-denial"))
    {
        Check(ClassifyFailedNativeBatch(r,true,false,false)==D3Disposition::ProvenUsedRejection);
        Check(r.Read().outcome==Outcome::RejectedBeforeCodec);
        Check(r.MayReturnValidated());
        Check(!r.RestartRequired());
    }
    else if(!std::strcmp(mode,"held-usage"))
    {
        Check(ClassifyFailedNativeBatch(r,true,true,false)==D3Disposition::TerminalRestartRequired);
        Check(r.RestartRequired());
        Check(r.Read().reason==Reason::MissingCleanupProof);
    }
    else if(!std::strcmp(mode,"runtime-failed"))
    {
        Check(ClassifyFailedNativeBatch(r,true,false,true)==D3Disposition::TerminalRestartRequired);
        Check(r.RestartRequired());
    }
    else if(!std::strcmp(mode,"precodec-after-append"))
    {
        Check(r.Advance(Phase::UsageAdmitted));
        Check(r.Advance(Phase::RegistriesAppended));
        Check(ClassifyFailedNativeBatch(r,false,false,false)==D3Disposition::TerminalRestartRequired);
        Check(r.Read().reason==Reason::MissingCleanupProof);
    }
    else if(!std::strcmp(mode,"codec-attempted"))
    {
        Check(r.Advance(Phase::UsageAdmitted));
        Check(r.Advance(Phase::RegistriesAppended));
        Check(r.Advance(Phase::CodecAttempted));
        Check(ClassifyFailedNativeBatch(r,true,false,false)==D3Disposition::TerminalRestartRequired);
        Check(r.Read().reason==Reason::CodecOutcomeUnknown);
    }
    else if(!std::strcmp(mode,"terminal-reason-immutable"))
    {
        r.MarkTerminal(Reason::NativePublicationFailure);
        Check(ClassifyFailedNativeBatch(r,true,false,false)==D3Disposition::TerminalRestartRequired);
        Check(r.Read().reason==Reason::NativePublicationFailure);
        Check(r.RestartRequired());
    }
    else return 2;
    std::printf("{\"schema\":\"R03B2D3ActualDecisionHeaderV1\",\"result\":\"PassedExactNativeDecisionHeaderOnly\",\"case\":\"%s\",\"checks\":%u,\"noUnity\":true}\n",mode,checks);
    return 0;
}
