#!/usr/bin/env python3
"""Focused two-repository source mutation tests for transitive publication."""
from __future__ import annotations
import copy
import os
from pathlib import Path
import unittest
from verify_native_publication_mutex_chain import (
    check_chain, verify_repositories, SourceMismatch,
    N_ASSEMBLY,N_METADATA,N_SHADOW,H_ASSEMBLY,H_STAGED,H_IMAGE,H_RUNTIME,H_CODEC,
    PINS_NATIVE,PINS_HYBRID,HYBRID_COMMIT,NATIVE_COMMIT,sha_git_blob,
)

def fixtures():
    native={
        N_ASSEMBLY: '''
          bool Assembly::PublishShadowBatch() {
            os::FastAutoLock lock(&s_assemblyLock);
            if(!tryBegin(context))return false;
            s_Assemblies.push_back(assembly);
            if(!publish(context)) return false;
          }
          bool Assembly::PublishInterpreterPlaceholder() {
            os::FastAutoLock lock(&s_assemblyLock);
            commit(context);
            if(!publish(context)) {rollback(context);return false;}
            return true;
          }
        ''',
        N_METADATA: '''
          bool il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch() {
            os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
            return Assembly::PublishShadowBatch(physical, before, after, &publication);
          }
          bool PublishShadowRegistries() {
            publication->publishActive(publication->context);
            return true;
          }
        ''',
        N_SHADOW: '''
          AssemblyShadowError AssemblyShadow::CommitTransaction() {
            std::unique_lock<std::mutex> lock(transaction.mutex);
            MetadataCache::PublishInterpreterAssembliesBatch(assemblies, a, b, c);
            lock.unlock();
            InterpreterAssembly::RunStagedModuleInitializer(staged, detail);
          }
          bool TryBeginPublication(void* context) {
            LockUsage();
            publication.used=UsedClosureMember(*publication.transaction);
            if(publication.used) { UnlockUsage(); return false; }
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
          AssemblyShadowError AssemblyShadow::CommitTransaction() {
            return AssemblyShadowError::FeatureDisabled;
          }
        ''',
    }
    hybrid={
        H_ASSEMBLY: '''
          static void CommitPlaceholder(void* context) {
            *publication.placeHolder = *publication.privateAssembly;
            publication.image->RebindIl2CppAssembly(publication.placeHolder);
          }
          static bool PublishPlaceholderImage(void* context) {
            return InterpreterImage::RegisterImage(publication.image) == InterpreterMetadataIndexRuntime::Error::None;
          }
          static void RollbackPlaceholder(void* context) {
            *publication.placeHolder = publication.backup;
            publication.image->RebindIl2CppAssembly(publication.privateAssembly);
          }
          Il2CppAssembly* Assembly::Create() {
            il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
            if(!il2cpp::vm::Assembly::PublishInterpreterPlaceholder(
              CommitPlaceholder,PublishPlaceholderImage,RollbackPlaceholder,&publication))return nullptr;
          }
        ''',
        H_STAGED: '''
          bool Assembly::PublishStagedImagesBatch() {
            return !imageIndices.empty() && InterpreterImage::RegisterImagesBatch(imageIndices.data(),imageIndices.size()) == InterpreterMetadataIndexRuntime::Error::None;
          }
        ''',
        H_IMAGE: '''
          InterpreterMetadataIndexRuntime::Error InterpreterImage::RegisterImagesBatch() {
            return InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count);
          }
          InterpreterMetadataIndexRuntime::Error InterpreterImage::RegisterImage() {
            return InterpreterMetadataIndexRuntime::Publish(image->GetIndex());
          }
        ''',
        H_RUNTIME: '''
          Runtime::Error Runtime::Publish(uint32_t imageId) {
            return PublishBatch(&imageId, 1);
          }
          Runtime::Error Runtime::PublishBatch() {
            std::lock_guard<std::mutex> lock(reservationMutex);
            Error error = current->codec.PublishBatch(current->publishScratch,count);
            if (error!=Error::None)return error;
            current->groups[group].active.store(1,std::memory_order_release);
          }
        ''',
        H_CODEC: '''
          Error PublishBatch(const Reservation* reservations, size_t count) {
            std::lock_guard<std::mutex> guard(mutex_);
            Error validation=ValidateHandleLocked(image,reservation);
            if(validation!=Error::None)return validation;
            image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);
          }
        ''',
    }
    return native,hybrid


def change(path,needle,replacement='',native=True):
    a,b=fixtures()
    target=a if native else b
    assert needle in target[path],(path,needle)
    target[path]=target[path].replace(needle,replacement,1)
    return a,b

class TransitivePublicationSourceTests(unittest.TestCase):
    def reject(self,args):
        with self.assertRaises(SourceMismatch):check_chain(*args)

    def test_baseline_source_grammar(self):
        r=check_chain(*fixtures())
        self.assertEqual(r['result'],'PinnedTransitivePublicationLocksOnly')
        self.assertEqual(r['reviewedNestedLockDepth'],6)
        self.assertEqual(r['nativeFilesPinned'],3)
        self.assertEqual(r['hybridclrFilesPinned'],5)
        self.assertFalse(r['deadlockFreedomProven'])
        self.assertFalse(r['usageLockExceptionSafetyProven'])
        self.assertEqual(r['handoffAuthority'],'CLOSED_NO_LOCAL_EXECUTION')

    def test_native_metadata_lock_mandatory(self):
        self.reject(change(N_METADATA,'os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);'))

    def test_native_assembly_lock_mandatory(self):
        self.reject(change(N_ASSEMBLY,'os::FastAutoLock lock(&s_assemblyLock);'))

    def test_usage_lock_mandatory(self):
        self.reject(change(N_SHADOW,'LockUsage();'))

    def test_begin_usage_lock_release_on_early_failure(self):
        self.reject(change(N_SHADOW,'if(publication.used) { UnlockUsage(); return false; }',
                           'if(publication.used) { return false; }'))

    def test_publish_usage_lock_release_on_failure(self):
        self.reject(change(N_SHADOW,'publication.runtimePublicationFailed=true;\n              UnlockUsage();return false;',
                           'publication.runtimePublicationFailed=true;return false;'))

    def test_publish_usage_lock_release_on_success(self):
        self.reject(change(N_SHADOW,'s_active.store(publication.snapshot,std::memory_order_release);\n            UnlockUsage();',
                           's_active.store(publication.snapshot,std::memory_order_release);'))

    def test_disabled_source_branch_must_exist(self):
        a,b=fixtures()
        a[N_SHADOW]=a[N_SHADOW].replace('return AssemblyShadowError::FeatureDisabled;',
                                      'return AssemblyShadowError::Success;')
        self.reject((a,b))

    def test_staged_batch_cannot_skip_image_adapter(self):
        self.reject(change(H_STAGED,'InterpreterImage::RegisterImagesBatch',
                           'UnsafeAlternatePublisher',native=False))

    def test_interpreter_image_must_call_runtime_batch(self):
        self.reject(change(H_IMAGE,'InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count);',
                           'InterpreterMetadataIndexRuntime::Publish(imageIndices[0]);',native=False))

    def test_reservation_mutex_comes_before_codec_batch(self):
        self.reject(change(H_RUNTIME,'std::lock_guard<std::mutex> lock(reservationMutex);',
                           '',native=False))
        a,b=fixtures()
        b[H_RUNTIME]=b[H_RUNTIME].replace(
            'std::lock_guard<std::mutex> lock(reservationMutex);',
            'Error error = current->codec.PublishBatch(current->publishScratch,count);')
        self.reject((a,b))

    def test_codec_mutex_mandatory(self):
        self.reject(change(H_CODEC,'std::lock_guard<std::mutex> guard(mutex_);','',native=False))

    def test_codec_published_lifecycle_store_mandatory(self):
        self.reject(change(H_CODEC,'image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);',
                           '',native=False))

    def test_no_vm_lock_or_callback_inside_codec_publish(self):
        a,b=fixtures()
        b[H_CODEC]=b[H_CODEC].replace('Error validation=',
                                  'os::FastAutoLock late(&g_MetadataLock);Error validation=')
        self.reject((a,b))

    def test_placeholder_must_pass_under_assembly_lock(self):
        a,b=fixtures()
        block='bool Assembly::PublishInterpreterPlaceholder() {\n            os::FastAutoLock lock(&s_assemblyLock);'
        self.assertIn(block,a[N_ASSEMBLY])
        a[N_ASSEMBLY]=a[N_ASSEMBLY].replace(block,'bool Assembly::PublishInterpreterPlaceholder() {')
        self.reject((a,b))

    def test_placeholder_rollback_stays(self):
        self.reject(change(N_ASSEMBLY,'rollback(context);','',native=True))
        self.reject(change(H_ASSEMBLY,'*publication.placeHolder = publication.backup;',
                           '',native=False))

    def test_placeholder_single_uses_same_runtime_batch(self):
        self.reject(change(H_IMAGE,'InterpreterMetadataIndexRuntime::Publish(image->GetIndex())',
                           'InterpreterMetadataIndexRuntime::PublishDirect(image->GetIndex())',native=False))
        self.reject(change(H_RUNTIME,'return PublishBatch(&imageId, 1);','return Error::None;',native=False))

    def test_initializer_is_outside_transaction_mutex(self):
        a,b=fixtures()
        a[N_SHADOW]=a[N_SHADOW].replace(
            'lock.unlock();\n            InterpreterAssembly::RunStagedModuleInitializer',
            'InterpreterAssembly::RunStagedModuleInitializer')
        self.reject((a,b))

    def test_no_file_set_drift(self):
        a,b=fixtures();del a[N_ASSEMBLY];self.reject((a,b))
        a,b=fixtures();b['other.cc']='x';self.reject((a,b))

    def test_cpp_comments_strings_not_proof(self):
        a,b=fixtures()
        b[H_CODEC]=b[H_CODEC].replace(
            'std::lock_guard<std::mutex> guard(mutex_);',
            'const char* str="std::lock_guard<std::mutex> guard(mutex_);";')
        self.reject((a,b))

    def test_sha_utility(self):
        self.assertEqual(sha_git_blob(b'test'),
                         '30d74d258442c7c65512eafab474568dd706c430')

    def test_real_native_and_hybridclr_sources_required_by_ci(self):
        native=os.environ.get('R03_B2_PINNED_NATIVE_ROOT')
        hybrid=os.environ.get('R03_B2_PINNED_HYBRIDCLR_ROOT')
        if not native or not hybrid:
            self.skipTest('pinned cross-repository checkouts required by CI; CI rejects skips')
        r=verify_repositories(Path(native),Path(hybrid))
        self.assertEqual(r['nativeCommit'],NATIVE_COMMIT)
        self.assertEqual(r['hybridclrCommit'],HYBRID_COMMIT)
        self.assertEqual(r['result'],'PinnedTransitivePublicationLocksOnly')

if __name__=='__main__':unittest.main()
