#!/usr/bin/env python3
"""Source-shaped mutation tests plus mandatory CI pinned native/hybridclr checkout."""
from __future__ import annotations
import os
import unittest
from pathlib import Path
from verify_publication_failure_boundary import (
    N_SHADOW,H_STAGED,H_IMAGE,H_RUNTIME,H_CODEC,NATIVE,HYBRIDCLR,
    SourceMismatch,check_source,sha_blob,verify_repositories,NATIVE_COMMIT,HYBRIDCLR_COMMIT,
)

def fixture()->dict[str,str]:
    return {
        N_SHADOW: '''
          bool TryBeginPublication(void* ctx) {
            LockUsage();
            publication.used = UsedClosureMember(*publication.transaction);
            if (publication.used) { UnlockUsage(); return false; }
            return true;
          }
          bool PublishActive(void* ctx) {
            if(!InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)) {
              publication.runtimePublicationFailed=true;
              UnlockUsage(); return false;
            }
            for(const auto& member : publication.transaction->closure)
              member.staged->published=true;
            s_active.store(publication.snapshot,std::memory_order_release);
            UnlockUsage(); return true;
          }
          AssemblyShadowError AssemblyShadow::CommitTransaction() {
            s_state.store(AssemblyShadowState::Committing,std::memory_order_release);
            if(!MetadataCache::PublishInterpreterAssembliesBatch(
                assemblies,TryBeginPublication,PublishActive,&publication)) {
              s_state.store(AssemblyShadowState::Validated,std::memory_order_release);
              return publication.runtimePublicationFailed?
                 Result(transaction,AssemblyShadowError::InternalError):Result(transaction,AssemblyShadowError::BaselineAlreadyUsed);
            }
            snapshot.release();
            lock.unlock();
            return AssemblyShadowError::Success;
          }
          AssemblyShadowError AssemblyShadow::CommitTransaction() {
            return AssemblyShadowError::FeatureDisabled;
          }
        ''',
        H_STAGED: '''
          bool Assembly::PublishStagedImagesBatch(const std::vector<uint32_t>& imageIndices) {
            return !imageIndices.empty() && InterpreterImage::RegisterImagesBatch(
              imageIndices.data(), imageIndices.size()) == InterpreterMetadataIndexRuntime::Error::None;
          }
        ''',
        H_IMAGE: '''
          InterpreterMetadataIndexRuntime::Error InterpreterImage::RegisterImagesBatch(
              const uint32_t* imageIndices,size_t count) {
            return InterpreterMetadataIndexRuntime::PublishBatch(imageIndices,count);
          }
        ''',
        H_RUNTIME: '''
          Runtime::Error Runtime::PublishBatch(const uint32_t* imageIds,size_t count) {
            std::lock_guard<std::mutex> lock(reservationMutex);
            Error error = current->codec.PublishBatch(current->publishScratch,count);
            if(error!=Error::None)return error;
            for(size_t index=0;index<count;++index)
              current->records[imageIds[index]].publicationGroup.store(group,std::memory_order_release);
            current->groups[group].active.store(1,std::memory_order_release);
            ++current->nextPublicationGroup;
            return Error::None;
          }
        ''',
        H_CODEC: '''
          Error PublishBatch(const Reservation* reservations,size_t count) {
            std::lock_guard<std::mutex> guard(mutex_);
            for(size_t index=0;index<count;++index) {
              if (!image->sealed) return Error::Unfinalized;
            }
            for(size_t index=0;index<count;++index) {
              image->lifecycle.store(static_cast<uint8_t>(Lifecycle::Published),std::memory_order_release);
            }
            return Error::None;
          }
        ''',
    }

class TestSourceBoundaries(unittest.TestCase):
    def reject(self,contents:dict[str,str])->None:
        with self.assertRaises(SourceMismatch):check_source(contents)
    def changed(self,path:str,old:str,new:str)->dict[str,str]:
        a=fixture();self.assertIn(old,a[path]);a[path]=a[path].replace(old,new,1);return a
    def test_source_shape_is_nonaccepting(self):
        row=check_source(fixture())
        self.assertEqual(row['result'],'PinnedNormalReturnIrreversibilityBoundaryOnly')
        self.assertEqual(len(row['observedPhases']),4)
        for flag in ('exceptionFreePublicationProven','rollbackAfterCodecPublishProven',
                     'safeRetryAfterUnknownExceptionProven','terminalRestartPolicyIntegrated',
                     'realUnityEvidence','R03Accepted','H2Passed','ReadyForHumanReviewGate'):
            self.assertIs(row[flag],False,flag)
    def test_exact_file_set_required(self):
        a=fixture();del a[H_IMAGE];self.reject(a)
        a=fixture();a['other.cpp']='';self.reject(a)
    def test_disabled_commit_stub_is_required(self):
        self.reject(self.changed(N_SHADOW,'return AssemblyShadowError::FeatureDisabled;',
                                 'return AssemblyShadowError::Success;'))
    def test_manual_usage_lock_required(self):
        self.reject(self.changed(N_SHADOW,'LockUsage();','NoLock();'))
    def test_normal_failure_unlock_required(self):
        self.reject(self.changed(N_SHADOW,'publication.runtimePublicationFailed=true;\n              UnlockUsage();',
                                'publication.runtimePublicationFailed=true;'))
    def test_success_unlock_required(self):
        self.reject(self.changed(N_SHADOW,'s_active.store(publication.snapshot,std::memory_order_release);\n            UnlockUsage();',
                                's_active.store(publication.snapshot,std::memory_order_release);'))
    def test_active_before_codec_rejected(self):
        self.reject(self.changed(N_SHADOW,'s_active.store(publication.snapshot,std::memory_order_release);',
                                '/* missing active */'))
    def test_false_return_classification_required(self):
        self.reject(self.changed(N_SHADOW,'s_state.store(AssemblyShadowState::Validated,std::memory_order_release);',
                                's_state.store(AssemblyShadowState::Committed,std::memory_order_release);'))
    def test_manual_failure_indicator_required(self):
        self.reject(self.changed(N_SHADOW,'publication.runtimePublicationFailed=true;',
                                'publication.runtimePublicationFailed=false;'))
    def test_staged_to_image_delegation_required(self):
        self.reject(self.changed(H_STAGED,'InterpreterImage::RegisterImagesBatch(',
                                'InterpreterImage::RegisterImage('))
    def test_image_to_runtime_required(self):
        self.reject(self.changed(H_IMAGE,'InterpreterMetadataIndexRuntime::PublishBatch(',
                                'InterpreterMetadataIndexRuntime::Abort('))
    def test_reservation_mutex_required(self):
        self.reject(self.changed(H_RUNTIME,'std::lock_guard<std::mutex> lock(reservationMutex);',''))
    def test_codec_publish_required(self):
        self.reject(self.changed(H_RUNTIME,'current->codec.PublishBatch(',
                                'current->codec.Abort('))
    def test_group_membership_required(self):
        self.reject(self.changed(H_RUNTIME,
          'current->records[imageIds[index]].publicationGroup.store(group,std::memory_order_release);',''))
    def test_group_active_required(self):
        self.reject(self.changed(H_RUNTIME,'current->groups[group].active.store(1,std::memory_order_release);',''))
    def test_group_after_codec_required(self):
        a=fixture()
        old='current->groups[group].active.store(1,std::memory_order_release);'
        a[H_RUNTIME]=a[H_RUNTIME].replace(old,'').replace('Error error = current->codec.PublishBatch',old+'\n            Error error = current->codec.PublishBatch')
        self.reject(a)
    def test_normal_failure_after_codec_detected(self):
        self.reject(self.changed(H_RUNTIME,'++current->nextPublicationGroup;',
                                'return Error::InvalidState;\n ++current->nextPublicationGroup;'))
    def test_codec_mutex_required(self):
        self.reject(self.changed(H_CODEC,'std::lock_guard<std::mutex> guard(mutex_);',''))
    def test_codec_validation_required(self):
        self.reject(self.changed(H_CODEC,'if (!image->sealed) return Error::Unfinalized;',
                                '/* validation removed */'))
    def test_lifecycle_store_required(self):
        self.reject(self.changed(H_CODEC,'Lifecycle::Published','Lifecycle::Private'))
    def test_codec_post_store_error_detected(self):
        self.reject(self.changed(H_CODEC,'return Error::None;',
                                'if(broken)return Error::InvalidState;return Error::None;'))
    def test_codec_post_store_throw_detected(self):
        self.reject(self.changed(H_CODEC,'return Error::None;',
                                'throw std::runtime_error("unexpected");return Error::None;'))
    def test_comments_do_not_prove_body(self):
        self.reject(self.changed(H_RUNTIME,'std::lock_guard<std::mutex> lock(reservationMutex);',
                                '// std::lock_guard<std::mutex> lock(reservationMutex);'))
    def test_git_blob_calculator(self):
        self.assertEqual(sha_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
    def test_repository_pins_are_five_files(self):
        self.assertEqual(len(NATIVE),1);self.assertEqual(len(HYBRIDCLR),4)
    def test_actual_source_required_in_ci(self):
        native=os.getenv('R03_B2_PINNED_NATIVE_ROOT')
        hybridclr=os.getenv('R03_B2_PINNED_HYBRIDCLR_ROOT')
        if not native or not hybridclr:self.skipTest('exact native/hybridclr Git checkout required; CI rejects skips')
        result=verify_repositories(Path(native),Path(hybridclr))
        self.assertEqual(result['nativeCommit'],NATIVE_COMMIT)
        self.assertEqual(result['hybridclrCommit'],HYBRIDCLR_COMMIT)
        self.assertEqual(result['result'],'PinnedNormalReturnIrreversibilityBoundaryOnly')

if __name__=='__main__':unittest.main()
