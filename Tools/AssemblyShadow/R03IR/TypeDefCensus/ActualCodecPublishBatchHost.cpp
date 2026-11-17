// R03 B2 SOURCE-HOST ONLY — compile the actual pinned standalone HybridCLR
// InterpreterMetadataIndexCodec.h, never a Unity/IL2CPP production TU.
// Tests normal-return codec batch semantics, NOT native exception freedom,
// Runtime publication groups, physical TypeDef census, or Player behavior.
#include "hybridclr/metadata/InterpreterMetadataIndexCodec.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>

namespace hybrid = hybridclr::metadata;
using Codec = hybrid::InterpreterMetadataIndexCodec;
using Error = Codec::Error;
static unsigned scenarios=0, checks=0;
static void Check(bool ok, const char* expr, int line) {
    ++checks;
    if (!ok) { std::fprintf(stderr,"FAIL line %d: %s\n",line,expr); std::abort(); }
}
#define CHECK(x) Check(bool(x),#x,__LINE__)

struct Fixture {
    // Even small logical limits use the codec's actual fixed preallocated arrays.
    Codec codec;
    Codec::Reservation ids[4];
    int32_t tokens[4]{};
    uint64_t owners[4] = {11,22,33,44};
    Fixture():codec(8,32) {
        CHECK(codec.IsValid());
        const Codec::BatchRequest request[4] = {{11,1},{22,1},{33,1},{44,1}};
        CHECK(codec.ReserveBatch(request,4,ids)==Error::None);
        for (int i=0;i<4;++i) {
            CHECK(ids[i].imageId>0 && ids[i].owner==owners[i]);
            CHECK(codec.Encode(ids[i],0,owners[i],tokens[i])==Error::None);
        }
    }
    bool Private(int i) {
        Codec::DecodedData data{};
        return codec.Decode(tokens[i],0,data)==Error::OwnerRequired &&
               codec.Decode(tokens[i],owners[i],data)==Error::None &&
               data.imageId==ids[i].imageId && data.rawIndex==0;
    }
    bool Public(int i) {
        Codec::DecodedData data{};
        return codec.Decode(tokens[i],0,data)==Error::None &&
               data.imageId==ids[i].imageId && data.rawIndex==0;
    }
};
static void InputValidation(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.PublishBatch(nullptr,1)==Error::InvalidArgument);
    CHECK(f.codec.PublishBatch(f.ids,0)==Error::InvalidArgument);
    CHECK(f.Private(0) && f.Private(1));
}
static void UnfinalizedLaterDoesNotPublishEarlier(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.Finalize(f.ids[0],f.owners[0],1)==Error::None);
    CHECK(f.codec.PublishBatch(f.ids,2)==Error::Unfinalized);
    CHECK(f.Private(0) && f.Private(1));
}
static void WrongLaterOwnerDoesNotPublishEarlier(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.Finalize(f.ids[1],f.owners[1],1)==Error::None);
    Codec::Reservation batch[2]={f.ids[0],f.ids[1]};
    batch[1].owner++;
    CHECK(f.codec.PublishBatch(batch,2)==Error::InvalidReservation);
    CHECK(f.Private(0) && f.Private(1));
}
static void DuplicateIndexDoesNotPublish(Fixture& f) {
    ++scenarios;
    Codec::Reservation same[2]={f.ids[0],f.ids[0]};
    CHECK(f.codec.PublishBatch(same,2)==Error::InvalidArgument);
    CHECK(f.Private(0) && f.Private(1));
}
static void AbortedLaterDoesNotPublishEarlier(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.Finalize(f.ids[2],f.owners[2],1)==Error::None);
    CHECK(f.codec.Abort(f.ids[2])==Error::None);
    Codec::Reservation batch[2]={f.ids[0],f.ids[2]};
    CHECK(f.codec.PublishBatch(batch,2)==Error::InvalidState);
    CHECK(f.Private(0));
    Codec::DecodedData out{};
    CHECK(f.codec.Decode(f.tokens[2],f.owners[2],out)==Error::InvalidState);
}
static void ValidBatchPublishesBoth(Fixture& f) {
    ++scenarios;
    const auto before=f.codec.GetStats();
    CHECK(f.codec.PublishBatch(f.ids,2)==Error::None);
    CHECK(f.Public(0) && f.Public(1));
    CHECK(f.Private(3));
    const auto after=f.codec.GetStats();
    CHECK(before.reservationCount==after.reservationCount);
    CHECK(before.reservedPages==after.reservedPages);
    CHECK(before.mappedPages==after.mappedPages);
}
static void PublishedCannotBeRevertedByAbort(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.Abort(f.ids[0])==Error::InvalidState);
    CHECK(f.codec.Abort(f.ids[1])==Error::InvalidState);
    CHECK(f.Public(0) && f.Public(1));
}
static void RepeatingPublicationIsRejected(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.PublishBatch(f.ids,2)==Error::InvalidState);
    CHECK(f.Public(0) && f.Public(1));
}
static void MixingPublishedAndPrivateDoesNotPublishPrivate(Fixture& f) {
    ++scenarios;
    CHECK(f.codec.Finalize(f.ids[3],f.owners[3],1)==Error::None);
    Codec::Reservation batch[2]={f.ids[0],f.ids[3]};
    CHECK(f.codec.PublishBatch(batch,2)==Error::InvalidState);
    CHECK(f.Private(3));
    CHECK(f.Public(0));
}
static void InitialAllocationFailureIsClosed() {
    ++scenarios;
    // Only constructor-failure behavior: no runtime metadata or VM involved.
    Codec bad(2,4,0);
    CHECK(!bad.IsValid() && bad.InitializationError()==Error::OutOfMemory);
    CHECK(bad.PublishBatch(nullptr,0)==Error::OutOfMemory);
}
int main() {
    Fixture f;
    InputValidation(f);
    UnfinalizedLaterDoesNotPublishEarlier(f);
    WrongLaterOwnerDoesNotPublishEarlier(f);
    DuplicateIndexDoesNotPublish(f);
    AbortedLaterDoesNotPublishEarlier(f);
    ValidBatchPublishesBoth(f);
    PublishedCannotBeRevertedByAbort(f);
    RepeatingPublicationIsRejected(f);
    MixingPublishedAndPrivateDoesNotPublishPrivate(f);
    InitialAllocationFailureIsClosed();
    std::printf("{\"kind\":\"R03B2ActualStandaloneCodecPublishBatch\",\"result\":\"PassedActualCodecHostOnly\",\"scenarios\":%u,\"checks\":%u,\"sourcePinRequired\":true,\"unityNativeIntegrated\":false,\"exceptionFreedomProven\":false,\"runtimeGroupVisibilityProven\":false,\"rollbackAfterPublicationPossible\":false,\"realUnity\":false,\"R03Accepted\":false,\"ReadyForHumanReviewGate\":false}\n",scenarios,checks);
    return 0;
}
