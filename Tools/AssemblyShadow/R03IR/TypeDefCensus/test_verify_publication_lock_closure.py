#!/usr/bin/env python3
"""Focused source-mutation tests for the pinned Runtime/Codec lock survey."""
from __future__ import annotations
import copy
import os
import unittest
from pathlib import Path
from verify_publication_lock_closure import (
 ASSEMBLY,CODEC,IMAGE,NATIVE_BLOBS,NATIVE_SHADOW,HYBRIDCLR_BLOBS,
 RUNTIME,STAGED,HYBRIDCLR_SHA,NATIVE_SHA,SourceMismatch,blob,check,
 verify_repositories,
)


def fixtures()->dict[str,str]:
 return {
  RUNTIME: '''
  std::mutex reservationMutex;
  Runtime::Error Runtime::Initialize() {
    std::lock_guard<std::mutex> lock(reservationMutex);
    std::unique_ptr<RuntimeState> fresh(new (std::nothrow) RuntimeState());return Error::None;
  }
  Runtime::Error Runtime::ReserveImages(uint32_t count, std::vector<Reservation>& output) {
    std::lock_guard<std::mutex> lock(reservationMutex);
    Error error=current.codec.ReserveBatch(requests.data(), requests.size(),reserved.data());
    return error;
  }
  Runtime::ScopedConstruction::ScopedConstruction(const Reservation& reservation,InterpreterImage* image) {
    std::lock_guard<std::mutex> lock(reservationMutex);
  }
  Runtime::ScopedConstruction::ScopedConstruction(uint32_t imageId,InterpreterImage* image,bool shadow) {
    std::lock_guard<std::mutex> lock(reservationMutex);
  }
  Runtime::Error Runtime::PublishBatch(const uint32_t* imageIds,size_t count) {
    std::lock_guard<std::mutex> lock(reservationMutex);
    Error error=current->codec.PublishBatch(current->publishScratch,count);
    if(error!=Error::None)return error;
    current->groups[group].active.store(1,std::memory_order_release);
    return Error::None;
  }
  Runtime::Error Runtime::Abort(uint32_t imageId) {
    std::lock_guard<std::mutex> lock(reservationMutex);
    return current->codec.Abort(record->reservation);
  }
  Runtime::Error Runtime::GetStats(Codec::Stats& output) {
    output=current->codec.GetStats();return Error::None;
  }
  ''',
  CODEC: '''
  mutable std::mutex mutex_;
  Error ReserveBatch() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Error Finalize() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Error GrantPages() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Error Encode() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Error Extra() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Error PublishBatch(const Reservation* reservations,size_t count) {
    std::lock_guard<std::mutex> guard(mutex_);
    image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);
    return Error::None;
  }
  Error Abort() {std::lock_guard<std::mutex> guard(mutex_);return Error::None;}
  Stats GetStats() {std::lock_guard<std::mutex> guard(mutex_);return {};}
  ''',
  IMAGE: '''
  InterpreterImageAdmission::Report InterpreterImage::ReserveImageBudget() {
    il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
    runtimeError=InterpreterMetadataIndexRuntime::GetStats(stats);
    runtimeError=InterpreterMetadataIndexRuntime::ReserveImages(static_cast<uint32_t>(sizes.size()),reservations);
    return {};
  }
  InterpreterMetadataIndexRuntime::Error InterpreterImage::GetMetadataCapacitySnapshot() {
    il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
    return GetMetadataCapacitySnapshotLocked(stats,ordinary,shadow,reserved);
  }
  InterpreterMetadataIndexRuntime::Error InterpreterImage::GetMetadataCapacitySnapshotLocked() {
    InterpreterMetadataIndexRuntime::Error error=InterpreterMetadataIndexRuntime::GetStats(stats);
    return error;
  }
  InterpreterMetadataIndexRuntime::Error InterpreterImage::RegisterImagesBatch() {
    return InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count);
  }
  ''',
  STAGED: '''
  bool Assembly::PublishStagedImagesBatch(const std::vector<uint32_t>& imageIndices) {
    return !imageIndices.empty() && InterpreterImage::RegisterImagesBatch(imageIndices.data(),imageIndices.size())==InterpreterMetadataIndexRuntime::Error::None;
  }
  ''',
  ASSEMBLY: '''
  static bool PublishPlaceholderImage(void* context) {
    return InterpreterImage::RegisterImage(publication.image)==InterpreterMetadataIndexRuntime::Error::None;
  }
  ''',
  NATIVE_SHADOW: '''
  bool TryBeginPublication(void* context) {
    LockUsage();
    publication.used=UsedClosureMember(*publication.transaction);
    if(publication.used) { UnlockUsage();return false;}
    return true;
  }
  bool PublishActive(void* context) {
    if(!InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)) {
      publication.runtimePublicationFailed=true;
      UnlockUsage();return false;
    }
    s_active.store(publication.snapshot,std::memory_order_release);
    UnlockUsage();return true;
  }
  ''',
 }

class Contract(unittest.TestCase):
 def pass_check(self):
  out=check(fixtures())
  self.assertEqual(out['result'],'PinnedRuntimeCodecLockSiteSurveyOnly')
  self.assertEqual(out['reservationMutexSites'],6)
  self.assertEqual(out['codecMutexSites'],8)
  self.assertTrue(out['observedCrossCallbackManualUsageLock'])
  self.assertFalse(out['manualUsageLockExceptionSafe'])
  self.assertFalse(out['deadlockFreedomProven'])
  self.assertFalse(out['R03Accepted'])
  return out
 def rejected(self,path:str,old:str,new:str,once:bool=False):
  inp=fixtures();self.assertIn(old,inp[path]); inp[path]=inp[path].replace(old,new,1 if once else -1)
  with self.assertRaises(SourceMismatch):check(inp)
 def test_structural_positive_and_closed_flags(self): self.pass_check()
 def test_removed_runtime_reservation_site_rejected(self):
  self.rejected(RUNTIME,'std::lock_guard<std::mutex> lock(reservationMutex);','',True)
 def test_added_runtime_reservation_site_rejected(self):
  self.rejected(RUNTIME,'Runtime::Error Runtime::GetStats(Codec::Stats& output) {',
    'Runtime::Error Runtime::GetStats(Codec::Stats& output) {\n std::lock_guard<std::mutex> lock(reservationMutex);')
 def test_runtime_publish_wrong_order_rejected(self):
  self.rejected(RUNTIME,'Error error=current->codec.PublishBatch(current->publishScratch,count);',
    'Error error=Error::None;')
 def test_runtime_reserve_callback_removed_rejected(self):
  self.rejected(RUNTIME,'current.codec.ReserveBatch(', 'fakeReserve(')
 def test_runtime_abort_codec_missing_rejected(self):
  self.rejected(RUNTIME,'current->codec.Abort(', 'fakeAbort(')
 def test_codec_mutex_removed_rejected(self):
  self.rejected(CODEC,'std::lock_guard<std::mutex> guard(mutex_);','',True)
 def test_codec_new_reservation_lock_rejected(self):
  self.rejected(CODEC,'mutable std::mutex mutex_;','mutable std::mutex mutex_;\n std::mutex reservationMutex;')
 def test_codec_external_runtime_callback_rejected(self):
  self.rejected(CODEC,'Error PublishBatch(const Reservation* reservations,size_t count) {',
    'Error PublishBatch(const Reservation* reservations,size_t count) {\n Runtime::GetStats(x);')
 def test_codec_lifecycle_store_removed_rejected(self):
  self.rejected(CODEC,'image->lifecycle.store(', 'image->change.store(')
 def test_codec_lifecycle_before_mutex_rejected(self):
  inp=fixtures();s=inp[CODEC];needle='std::lock_guard<std::mutex> guard(mutex_);\n    image->lifecycle.store'
  self.assertIn(needle,s)
  inp[CODEC]=s.replace(needle,'image->lifecycle.store',1).replace('return Error::None;\n  }\n  Error Abort()',
       'std::lock_guard<std::mutex> guard(mutex_);return Error::None;\n  }\n  Error Abort()',1)
  with self.assertRaises(SourceMismatch):check(inp)
 def test_missing_metadata_lock_on_reservation_rejected(self):
  self.rejected(IMAGE,'il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);','',True)
 def test_reversed_reservation_and_stats_rejected(self):
  inp=fixtures();s=inp[IMAGE];a='runtimeError=InterpreterMetadataIndexRuntime::GetStats(stats);';b='runtimeError=InterpreterMetadataIndexRuntime::ReserveImages(static_cast<uint32_t>(sizes.size()),reservations);'
  inp[IMAGE]=s.replace(a,'PLACEHOLDER;').replace(b,a).replace('PLACEHOLDER;',b)
  with self.assertRaises(SourceMismatch):check(inp)
 def test_snapshot_missing_codec_stats_rejected(self):
  self.rejected(IMAGE,'InterpreterMetadataIndexRuntime::GetStats(stats);','NotStats(stats);',False)
 def test_staged_batch_missing_rejected(self):
  self.rejected(STAGED,'InterpreterImage::RegisterImagesBatch(', 'FakeRegister(')
 def test_placeholder_missing_rejected(self):
  self.rejected(ASSEMBLY,'InterpreterImage::RegisterImage(publication.image)','BadRegister(publication.image)')
 def test_manual_spinlock_removed_rejected(self):
  self.rejected(NATIVE_SHADOW,'LockUsage();','NoLock();')
 def test_publication_unlock_on_normal_success_missing_rejected(self):
  self.rejected(NATIVE_SHADOW,'s_active.store(publication.snapshot,std::memory_order_release);\n    UnlockUsage();return true;',
    's_active.store(publication.snapshot,std::memory_order_release);\n    return true;')
 def test_publication_unlock_on_normal_failure_missing_rejected(self):
  self.rejected(NATIVE_SHADOW,'publication.runtimePublicationFailed=true;\n      UnlockUsage();return false;',
    'publication.runtimePublicationFailed=true;\n      return false;')
 def test_native_source_file_inventory_fail_closed(self):
  data=fixtures(); del data[NATIVE_SHADOW]
  with self.assertRaises(SourceMismatch):check(data)
  data=fixtures();data['extra.cpp']='untrusted'
  with self.assertRaises(SourceMismatch):check(data)
 def test_comments_cannot_fake_codec_mutex(self):
  inp=fixtures();inp[CODEC]=inp[CODEC].replace('mutable std::mutex mutex_;','// mutable std::mutex mutex_;')
  with self.assertRaises(SourceMismatch):check(inp)
 def test_blob_hash_utility(self):
  self.assertEqual(blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
 def test_exact_checkout_mandatory_in_ci(self):
  native=os.environ.get('R03_B2_PINNED_NATIVE_ROOT')
  hybrid=os.environ.get('R03_B2_PINNED_HYBRIDCLR_ROOT')
  if not native or not hybrid:self.skipTest('requires two exact Git checkouts; CI disallows skips')
  out=verify_repositories(Path(native),Path(hybrid))
  self.assertEqual(out['nativeCommit'],NATIVE_SHA)
  self.assertEqual(out['hybridclrCommit'],HYBRIDCLR_SHA)
  self.assertEqual(out['reservationMutexSites'],6)
  self.assertEqual(out['codecMutexSites'],8)

if __name__=='__main__':unittest.main()
