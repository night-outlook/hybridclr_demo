#!/usr/bin/env python3
"""R03 B2 lock-order contract: synthetic mutation tests + mandatory CI native pin."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from verify_native_lock_lifetime_graph import (
    ASSEMBLY, B2, GATE, GLOBAL, MEMORY, METADATA, NATIVE, PINS, RUNTIME,
    SCAN, SHADOW, SourceMismatch, check_lock_graph, sha_git_blob,
    verify_repository,
)


def sources() -> dict[str,str]:
    # Compact native-shaped methods exercise lexical scopes and mutation
    # detection; ONLY the actual checked-out Git blobs can prove native pins.
    return {
        B2: '''
            bool AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive() {
                assembly_shadow_metadata_lifetime::Gate::Reader admission(g_MetadataLifetimeGate);
                if(!admission)return false;
                os::FastAutoLock metadataLock(&g_MetadataLock);
                Assembly::TryVisitOriginalV1ExecutionImages(readOriginalV1,&sink);
                il2cpp_class_for_each(callback,&ctx);
                il2cpp_class_for_each(callback,&ctx);
                il2cpp_class_for_each(callback,&ctx);
                Assembly::TryVisitOriginalV1ExecutionImages(readOriginalV1,&sink2);
                nonRootOwners.Scrub();
                firstPassFacts.Scrub();
            }
        ''',
        ASSEMBLY: '''
            bool Assembly::TryVisitOriginalV1ExecutionImages() {
                os::FastAutoLock lock(&s_assemblyLock);
                return assembly_shadow_original_v1_image_scan::Scan(
                    s_Assemblies.begin(),s_Assemblies.end(),
                    [=](const Il2CppImage* image) noexcept -> bool {
                       return visit(image,context);
                    });
            }
            bool Assembly::TryVisitRegisteredAotImages() {
                os::FastAutoLock lock(&s_assemblyLock);
                return assembly_shadow_registered_aot_scan::Scan();
            }
            bool Assembly::PublishShadowBatch() {
                os::FastAutoLock lock(&s_assemblyLock);
                if(!tryBegin(context))return false;
                s_Assemblies.push_back(assembly);
                if(!publish(context))return false;
                return true;
            }
            bool Assembly::PublishInterpreterPlaceholder() {
                os::FastAutoLock lock(&s_assemblyLock);
                commit(context);
                if(!publish(context)) {rollback(context);return false;}
                return true;
            }
        ''',
        METADATA: '''
            bool PublishShadowRegistries() {
                publication->publishActive(publication->context);
                return true;
            }
            bool il2cpp::vm::MetadataCache::PublishInterpreterAssembliesBatch() {
                os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
                return il2cpp::vm::Assembly::PublishShadowBatch(physical, a,b,&publication);
            }
        ''',
        RUNTIME: '''
            bool Runtime::Init() {
                os::FastAutoLock lock(&s_InitLock);
                MetadataAllocInitialize();
                bool opened = g_MetadataLifetimeGate.OpenAfterInit();
                AssemblyShadowStartup::MarkCoreReady();return true;
            }
            void Runtime::Shutdown() {
                os::FastAutoLock lock(&s_InitLock);
                FireProcessExitEvent();
                g_MetadataLifetimeGate.CloseAndDrain();
                shutting_down = true;
                Thread::AbortAllThreads();
                MetadataAllocCleanup();
            }
        ''',
        GATE: '''
            class Gate final {
               class Reader final {
                 explicit Reader(Gate& gate, uint32_t sourceEpoch=detail::kInitialEpoch) noexcept
                   :gate_(gate.TryEnter(sourceEpoch)?&gate:nullptr) {}
                 ~Reader() noexcept {if(gate_)gate_->Leave();}
               };
               void CloseAndDrain() noexcept {
                 state_.fetch_or(detail::kClosed,std::memory_order_acq_rel);
                 while((state_.load(std::memory_order_acquire)&detail::kReaders)!=0)
                   std::this_thread::yield();
               }
            };
        ''',
        SCAN: '''
            bool Scan() {
                if(!assembly->token)continue;
                if(!assembly->image||assembly->image->assembly!=assembly)return false;
                if(!visit(assembly->image))return false;
            }
        ''',
        SHADOW: '''
            bool TryBeginPublication(void* context) {
                LockUsage();
                publication.used = UsedClosureMember(*publication.transaction);
                if(publication.used){UnlockUsage();return false;}
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
                std::unique_lock<std::mutex> lock(transaction.mutex);
                if(!MetadataCache::PublishInterpreterAssembliesBatch(assemblies,a,b,&p))return fail;
                lock.unlock();
            }
        ''',
        GLOBAL: '''
            Il2CppClass* il2cpp::vm::GlobalMetadata::GetInitializedTypeInfoFromAssembly() {
               os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
               return klass && klass->initialized ? klass : nullptr;
            }
            Il2CppClass* il2cpp::vm::GlobalMetadata::GetTypeInfoFromTypeDefinitionIndex() {
                return utils::InitOnce(&s_TypeInfoDefinitionTable[index],&il2cpp::vm::g_MetadataLock,[index](){return FromTypeDefinition(index);});
            }
        ''',
        MEMORY: '''
            void ReportIL2CppClasses() {
                const auto* classes = Assembly::GetAllAssemblies();
                Il2CppClass* k = GlobalMetadata::GetInitializedTypeInfoFromAssembly(&image,i);
            }
        ''',
    }


def mutate(old: str, replacement: str, path: str, bundle: dict[str,str] | None = None) -> dict[str,str]:
    result=copy.deepcopy(sources() if bundle is None else bundle)
    assert result[path].count(old)==1, f'test fixture ambiguous: {old}'
    result[path]=result[path].replace(old,replacement)
    return result


class ContractTests(unittest.TestCase):
    def test_source_shaped_contract_is_structural_only(self):
        result=check_lock_graph(sources())
        self.assertEqual(result['result'],'PinnedLockOrderObservationsOnly')
        self.assertEqual(result['pinnedNativeFileCount'],9)
        self.assertEqual(len(result['reviewedDirectOrdering']),5)
        self.assertEqual(len(result['remainingOpaqueWorkUnderAssemblyAndUsageLocks']),4)
        self.assertIs(result['knownNestedPublicationUsageLock'],True)
        for field in ('deadlockFreedomProven','transitivePublicationCallbackLocksAudited',
                      'metadataImageAllocationEpochProven','classGcVmEpochProven',
                      'originalPhysicalRegistryAtomicallyProven','nativeCollectorIntegrated',
                      'realUnityEvidence','R03Accepted','H2Passed',
                      'ReadyForHumanReviewGate','shutdownDrainHasProvenFiniteTimeout'):
            self.assertIs(result[field],False,field)
        self.assertEqual(result['handoffAuthority'],'CLOSED_NO_LOCAL_EXECUTION')

    def reject(self,data):
        with self.assertRaises(SourceMismatch):check_lock_graph(data)

    def test_reader_missing_or_late_is_rejected(self):
        self.reject(mutate('assembly_shadow_metadata_lifetime::Gate::Reader admission(g_MetadataLifetimeGate);','',B2))
        x=sources();start='assembly_shadow_metadata_lifetime::Gate::Reader admission(g_MetadataLifetimeGate);';lock='os::FastAutoLock metadataLock(&g_MetadataLock);'
        x[B2]=x[B2].replace(start,'READER_GOES_LATER;').replace(lock,start+'\n'+lock).replace('READER_GOES_LATER;',lock)
        self.reject(x)

    def test_metadata_lock_removed_or_late_is_rejected(self):
        self.reject(mutate('os::FastAutoLock metadataLock(&g_MetadataLock);','',B2))
        x=sources(); lock='os::FastAutoLock metadataLock(&g_MetadataLock);';visitor='Assembly::TryVisitOriginalV1ExecutionImages(readOriginalV1,&sink);'
        x[B2]=x[B2].replace(lock,visitor).replace(visitor+'\n                '+visitor,visitor+'\n                '+lock)
        self.reject(x)

    def test_original_image_visits_and_three_class_passes_required(self):
        self.reject(mutate('Assembly::TryVisitOriginalV1ExecutionImages(readOriginalV1,&sink2);','',B2))
        self.reject(self._drop_one_class())

    def _drop_one_class(self):
        x=sources()
        needle='il2cpp_class_for_each(callback,&ctx);'
        x[B2]=x[B2].replace(needle,'NO_PUBLIC_PASS;',1)
        return x

    def test_scoped_b2_scrub_must_stay_inside_source_session(self):
        self.reject(mutate('nonRootOwners.Scrub();','',B2))
        self.reject(mutate('firstPassFacts.Scrub();','',B2))

    def test_physical_assembly_lock_and_raw_registry_required(self):
        x=sources()
        x[ASSEMBLY]=x[ASSEMBLY].replace('os::FastAutoLock lock(&s_assemblyLock);','',1)
        self.reject(x)
        self.reject(mutate('s_Assemblies.begin(),s_Assemblies.end()', 'GetAllAssemblies().begin(),GetAllAssemblies().end()',ASSEMBLY))
        self.reject(mutate('return visit(image,context);','return false;',ASSEMBLY))

    def test_registered_source_must_take_assembly_lock(self):
        x=sources(); needle='os::FastAutoLock lock(&s_assemblyLock);'
        pos=x[ASSEMBLY].find('bool Assembly::TryVisitRegisteredAotImages()')
        x[ASSEMBLY]=x[ASSEMBLY][:pos]+x[ASSEMBLY][pos:].replace(needle,'',1)
        self.reject(x)

    def test_physical_scan_token_and_backlink_required(self):
        self.reject(mutate('if(!assembly->token)continue;','if(!assembly->image->token)continue;',SCAN))
        self.reject(mutate('assembly->image->assembly!=assembly','false',SCAN))
        self.reject(mutate('if(!visit(assembly->image))return false;', '',SCAN))

    def test_metadata_batch_publication_acquires_metadata_first(self):
        self.reject(mutate('os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);','',METADATA))
        self.reject(mutate('il2cpp::vm::Assembly::PublishShadowBatch(physical, a,b,&publication)', 'other()', METADATA))

    def test_callbacks_under_assembly_lock_are_not_promoted_to_safe(self):
        self.reject(mutate('if(!tryBegin(context))return false;','',ASSEMBLY))
        x=sources()
        # A moved lock in the publication scope cannot be accepted.
        x[ASSEMBLY]=x[ASSEMBLY].replace('bool Assembly::PublishShadowBatch() {\n                os::FastAutoLock lock(&s_assemblyLock);',
                                        'bool Assembly::PublishShadowBatch() {\n                // missing lock')
        self.reject(x)

    def test_usage_lock_callback_chain_is_required_and_not_certified_cycle_free(self):
        self.reject(mutate('publication->publishActive(publication->context);','',METADATA))
        self.reject(mutate('LockUsage();','',SHADOW))
        self.reject(mutate('UsedClosureMember(*publication.transaction)','other()',SHADOW))
        self.reject(mutate('InterpreterAssembly::PublishStagedImagesBatch(publication.imageIndices)',
                           'other()',SHADOW))
        self.reject(mutate('s_active.store(publication.snapshot,std::memory_order_release);',
                           '',SHADOW))
        x=sources()
        # UnlockUsage occurs three times, remove the final post-publication one.
        needle='s_active.store(publication.snapshot,std::memory_order_release);\n                UnlockUsage();'
        self.assertIn(needle,x[SHADOW])
        x[SHADOW]=x[SHADOW].replace(needle,
                    's_active.store(publication.snapshot,std::memory_order_release);')
        self.reject(x)

    def test_placeholder_callbacks_are_review_obligations(self):
        self.reject(mutate('rollback(context);','return;',ASSEMBLY))
        x=sources(); pos=x[ASSEMBLY].find('bool Assembly::PublishInterpreterPlaceholder()')
        x[ASSEMBLY]=x[ASSEMBLY][:pos]+x[ASSEMBLY][pos:].replace('os::FastAutoLock lock(&s_assemblyLock);','',1)
        self.reject(x)

    def test_transaction_mutex_must_remain_around_publish(self):
        self.reject(mutate('std::unique_lock<std::mutex> lock(transaction.mutex);','',SHADOW))
        x=sources()
        x[SHADOW]=x[SHADOW].replace('std::unique_lock<std::mutex> lock(transaction.mutex);',
            'std::unique_lock<std::mutex> lock(transaction.mutex);\n lock.unlock();')
        self.reject(x)

    def test_shutdown_order_and_init_gate(self):
        self.reject(mutate('g_MetadataLifetimeGate.OpenAfterInit();','',RUNTIME))
        self.reject(mutate('g_MetadataLifetimeGate.CloseAndDrain();','',RUNTIME))
        self.reject(mutate('MetadataAllocCleanup();','',RUNTIME))
        x=sources()
        x[RUNTIME]=x[RUNTIME].replace('g_MetadataLifetimeGate.CloseAndDrain();','CLOSE_LATER;').replace(
            'MetadataAllocCleanup();','g_MetadataLifetimeGate.CloseAndDrain();\n MetadataAllocCleanup();').replace('CLOSE_LATER;','')
        self.reject(x)

    def test_shutdown_managed_event_is_before_gate_closure(self):
        x=sources()
        x[RUNTIME]=x[RUNTIME].replace('FireProcessExitEvent();','EVENT_LATER;').replace(
            'g_MetadataLifetimeGate.CloseAndDrain();','g_MetadataLifetimeGate.CloseAndDrain();\n FireProcessExitEvent();').replace('EVENT_LATER;','')
        self.reject(x)
        self.reject(mutate('FireProcessExitEvent();','',RUNTIME))

    def test_gate_reader_is_initial_only_and_drains(self):
        self.reject(mutate('sourceEpoch=detail::kInitialEpoch','sourceEpoch=0',GATE))
        self.reject(mutate('gate_->Leave();','',GATE))
        self.reject(mutate('state_.fetch_or(detail::kClosed,std::memory_order_acq_rel);','',GATE))
        self.reject(mutate('std::this_thread::yield();','',GATE))

    def test_cached_class_is_not_a_physical_population(self):
        self.reject(mutate('klass && klass->initialized ? klass : nullptr', 'klass',GLOBAL))
        self.reject(mutate('s_TypeInfoDefinitionTable[index]','s_TypeInfoTable[index]',GLOBAL))
        self.reject(mutate('Assembly::GetAllAssemblies()', 'TryVisitOriginalV1ExecutionImages()',MEMORY))

    def test_missing_or_extra_source_pin_rejected(self):
        data=sources();del data[B2];self.reject(data)
        data=sources();data['other.cpp']='untrusted';self.reject(data)

    def test_cpp_strings_and_comments_do_not_count_as_operations(self):
        data=sources()
        p=data[ASSEMBLY].find('bool Assembly::TryVisitOriginalV1ExecutionImages()')
        data[ASSEMBLY]=data[ASSEMBLY][:p]+data[ASSEMBLY][p:].replace('os::FastAutoLock lock(&s_assemblyLock);',
            'const char* note="os::FastAutoLock lock(&s_assemblyLock);";',1)
        self.reject(data)

    def test_git_blob_utility_matches_exact_hash(self):
        self.assertEqual(sha_git_blob(b'test'), '30d74d258442c7c65512eafab474568dd706c430')

    def test_native_checkout_required_on_ci(self):
        native=os.environ.get('R03_B2_PINNED_NATIVE_ROOT')
        if not native:self.skipTest('requires exact native checkout; CI forbids skips')
        report=verify_repository(Path(native))
        self.assertEqual(report['nativeCommit'],NATIVE)
        self.assertEqual(report['result'],'PinnedLockOrderObservationsOnly')
        self.assertEqual(report['pinnedNativeFileCount'],9)


if __name__=='__main__': unittest.main()
