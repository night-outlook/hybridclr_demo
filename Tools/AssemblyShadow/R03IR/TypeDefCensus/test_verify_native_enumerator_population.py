#!/usr/bin/env python3
"""Synthetic source mutations + actual pinned native source when available."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

import verify_native_enumerator_population as gate
from verify_native_source_path_boundary import SourceMismatch, blob_sha


def source_fixture() -> dict[str,str]:
    # Intentionally small, source-shaped fixtures. All actual native files are
    # checked independently by verify_repository in exact-source GitHub CI.
    return {
        gate.API: '''void il2cpp_class_for_each(void(*klassReportFunc)(Il2CppClass*,void*),void* userData){
            MemoryInformation::ReportIL2CppClasses(klassReportFunc,userData); }''',
        gate.MEMORY: '''static void ReportVisibleClass(Il2CppClass* klass,void* context){
            if(AssemblyShadowVisibility::IsClassVisible(klass, report->generation))
                report->callback(klass, report->context);
        }
        void ReportIL2CppClasses(ClassReportFunc callback, void* context){
            const auto* allAssemblies = Assembly::GetAllAssemblies();
            callback = ReportVisibleClass;
            Il2CppClass* type=GlobalMetadata::GetInitializedTypeInfoFromAssembly(&image, i);
            metadata::ArrayMetadata::WalkArrays(callback, context);
            metadata::ArrayMetadata::WalkSZArrays(callback, context);
            metadata::GenericMetadata::WalkAllGenericClasses(callback, context);
            MetadataCache::WalkPointerTypes(callback, context);
        }''',
        gate.ASSEMBLY: '''static void CopyValidAssemblies(AssemblyVector& dst, const AssemblyVector& src){
            if (ass->token) dst.push_back(ass);
        }
        static void CopyLogicalAssemblies(AssemblyVector& dst, const AssemblyVector& src){
            const Il2CppAssembly* logical = AssemblyShadow::ResolveAssembly(physical);
            if (seen.Find(logical->aname.name)) continue;
        }
        AssemblyVector* Assembly::GetAllAssemblies() {
            if (s_assemblyVersion != s_snapshotAssemblyVersion) {
                CopyLogicalAssemblies(*s_snapshotAssemblies, s_Assemblies);
            }
            return s_snapshotAssemblies;
        }
        bool Assembly::TryVisitOriginalV1ExecutionImages(Visit visit, void* context) noexcept {
            return assembly_shadow_original_v1_image_scan::Scan(
                s_Assemblies.begin(),s_Assemblies.end(),visit);
        }''',
        gate.IMAGE_SCAN: '''template<class Iterator,class Visit>
        bool Scan(Iterator first,Iterator last,Visit visit) noexcept {
            if(!assembly->token)continue;
            if(!visit(assembly->image))return false;
            return true;
        }''',
        gate.GLOBAL: '''Il2CppClass* il2cpp::vm::GlobalMetadata::GetInitializedTypeInfoFromAssembly(const Il2CppImage* image,AssemblyTypeIndex index) {
            os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
            klass=interpreterImage->GetCachedTypeInfoFromTypeDefinitionRawIndex(index);
            klass=s_TypeInfoDefinitionTable[typeIndex];
            return klass && klass->initialized ? klass : nullptr;
        }''',
        gate.GENERIC: '''void GenericMetadata::WalkAllGenericClasses(GenericClassWalkCallback callback,void* context){
            FastAutoLock lock(&s_GenericClassMutex);
            if ((*it).key->cached_class != NULL) callback((*it).key->cached_class, context);
        }''',
        gate.ARRAY: '''void ArrayMetadata::WalkArrays(ArrayTypeWalkCallback callback,void* context){
            FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
            callback(it->second, context);
        }
        void ArrayMetadata::WalkSZArrays(ArrayTypeWalkCallback callback,void* context){
            FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
            callback(it->second, context);
        }''',
        gate.POINTER: '''void il2cpp::vm::MetadataCache::WalkPointerTypes(WalkTypesCallback callback,void* context){
            os::FastAutoLock lock(&g_MetadataLock);
            for(auto it=s_MetadataCache.m_PointerTypes.UnlockedBegin();it!=end;++it) callback(it->second,context);
        }''',
        gate.RUNTIME: '''bool Runtime::Init(const char* domainName){
            g_MetadataLifetimeGate.OpenAfterInit();
            return true;
        }
        void Runtime::Shutdown(){
            g_MetadataLifetimeGate.CloseAndDrain();
        }''',
        gate.LIFETIME: '''class Gate final {
            class Reader final {
                Reader(Gate& gate,uint32_t sourceEpoch=detail::kInitialEpoch) noexcept {}
            };
            void CloseAndDrain() noexcept { std::this_thread::yield(); }
        };''',
        gate.B2: '''bool AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive(){
            assembly_shadow_metadata_lifetime::Gate::Reader admission(g_MetadataLifetimeGate);
            os::FastAutoLock metadataLock(&g_MetadataLock);
            Assembly::TryVisitOriginalV1ExecutionImages(foo,bar);
            NonRootOwnerAudit nonRootOwners{};
            il2cpp_class_for_each(callback,context);
            il2cpp_class_for_each(callback,context);
            il2cpp_class_for_each(callback,context);
            Assembly::TryVisitOriginalV1ExecutionImages(foo,bar);
        }''',
    }


class NativeEnumerationPopulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources=source_fixture()

    def assert_reject(self, path: str, old: str, new: str, fragment: str='') -> None:
        source=self.sources[path]
        self.assertIn(old,source)
        self.sources[path]=source.replace(old,new,1)
        with self.assertRaises(SourceMismatch) as caught:
            gate.check_population_sources(self.sources)
        if fragment:self.assertIn(fragment,str(caught.exception))

    def test_positive_fixture_retains_false_claims(self):
        r=gate.check_population_sources(self.sources)
        self.assertEqual(r['result'],'PinnedSourcePopulationMismatchOnly')
        self.assertEqual(r['nativeFilesVerified'],11)
        self.assertFalse(r['physicalAndPublicPopulationEquivalenceProven'])
        self.assertFalse(r['realPhysicalTypeDefUpperBoundMeasured'])
        self.assertFalse(r['realObservedTypeDefUsePopulationMeasured'])
        self.assertEqual(r['handoffAuthority'],'CLOSED_NO_LOCAL_EXECUTION')
        self.assertEqual(len(r['separateCacheWalkers']),4)

    def test_public_api_forwarding_is_not_direct_physical(self):
        self.assert_reject(gate.API,'MemoryInformation::ReportIL2CppClasses','Assembly::TryVisitOriginalV1ExecutionImages','API forwarding')

    def test_public_assembly_source_must_not_be_physical(self):
        self.assert_reject(gate.MEMORY,'Assembly::GetAllAssemblies()','Assembly::TryVisitOriginalV1ExecutionImages()','public logical')

    def test_visibility_callback_removal_rejected(self):
        self.assert_reject(gate.MEMORY,'callback = ReportVisibleClass;','callback = ordinary;', 'visibility wrapping')

    def test_class_visibility_predicate_removal_rejected(self):
        self.assert_reject(gate.MEMORY,'AssemblyShadowVisibility::IsClassVisible(klass, report->generation)','true','visibility filter')

    def test_public_initialized_only_rejected_if_eager(self):
        self.assert_reject(gate.MEMORY,'GlobalMetadata::GetInitializedTypeInfoFromAssembly','GlobalMetadata::GetTypeInfoFromTypeDefinitionIndex','initialized only')

    def test_logical_snapshot_remapping_is_required(self):
        self.assert_reject(gate.ASSEMBLY,'AssemblyShadow::ResolveAssembly(physical)','physical','shadow resolution')

    def test_conditional_versioned_snapshot_is_required(self):
        self.assert_reject(gate.ASSEMBLY,'if (s_assemblyVersion != s_snapshotAssemblyVersion)','if (true)','conditional cached snapshot')

    def test_physical_scan_must_come_from_registration(self):
        self.assert_reject(gate.ASSEMBLY,'s_Assemblies.begin(),s_Assemblies.end()','GetAllAssemblies().begin(),GetAllAssemblies().end()','physical table')

    def test_physical_scan_cannot_exclude_interpreters(self):
        self.assert_reject(gate.IMAGE_SCAN,'if(!visit(assembly->image))return false;',
                           'if(IsInterpreterImage(assembly->image))continue; if(!visit(assembly->image))return false;',
                           'interpreter source')

    def test_physical_scan_cannot_drop_zero_types(self):
        self.assert_reject(gate.IMAGE_SCAN,'if(!visit(assembly->image))return false;',
                           'if(!assembly->image->typeCount)continue; if(!visit(assembly->image))return false;',
                           'zero-TypeDef')

    def test_interpreter_cache_source_must_be_nonconstructing(self):
        self.assert_reject(gate.GLOBAL,'GetCachedTypeInfoFromTypeDefinitionRawIndex','GetTypeInfoFromTypeDefinitionIndex','interpreter cached')

    def test_initialized_return_guard_is_mandatory(self):
        self.assert_reject(gate.GLOBAL,'return klass && klass->initialized ? klass : nullptr;', 'return klass;', 'initialized-only')

    def test_generic_mutex_is_not_metadata_lock(self):
        self.assert_reject(gate.GENERIC,'FastAutoLock lock(&s_GenericClassMutex)','FastAutoLock lock(&il2cpp::vm::g_MetadataLock)','generic cache mutex')

    def test_array_cache_walker_is_separate(self):
        self.assert_reject(gate.MEMORY,'metadata::ArrayMetadata::WalkSZArrays(callback, context)','NoSzArrays()','SZ array walker')

    def test_pointer_cache_walker_is_separate(self):
        self.assert_reject(gate.POINTER,'m_PointerTypes.UnlockedBegin()','s_TypeInfoTable.begin()','pointer cached-map')

    def test_shutdown_drain_is_a_distinct_lifetime_gate(self):
        self.assert_reject(gate.RUNTIME,'g_MetadataLifetimeGate.CloseAndDrain()','g_MetadataLifetimeGate.Closed()','close/drain')

    def test_b2_three_class_passes_and_two_image_passes(self):
        self.assert_reject(gate.B2,'il2cpp_class_for_each(callback,context);','NoClassScan();','callback count')

    def test_b2_metadata_reader_required(self):
        self.assert_reject(gate.B2,'assembly_shadow_metadata_lifetime::Gate::Reader admission(', 'int admission(', 'B2 Reader')

    def test_spoofed_comments_do_not_restore_source_claim(self):
        text=self.sources[gate.MEMORY].replace('callback = ReportVisibleClass;', 'callback = ordinary;')
        text+='\n// callback = ReportVisibleClass;'
        self.sources[gate.MEMORY]=text
        with self.assertRaises(SourceMismatch):gate.check_population_sources(self.sources)

    def test_synced_missing_real_population_can_be_consistent(self):
        # Demonstrates only that an arbitrary cached/logical subset is not
        # proof of a physical closed world; it is NOT empirical Unity data.
        physical_token_valid={'AOT.A','AOT.B','Interpreter.X'}
        initialized_logical={'AOT.A'}
        self.assertLess(len(initialized_logical),len(physical_token_valid))
        gate.check_population_sources(self.sources)

    def test_modified_git_blob_rejected(self):
        raw=b'a source file\n'
        self.assertNotEqual(blob_sha(raw),gate.PINNED_BLOBS[gate.MEMORY])
        self.assertEqual(len(blob_sha(raw)),40)

    def test_pinned_real_checkout(self):
        env=os.environ.get('R03_B2_PINNED_NATIVE_ROOT','')
        if not env:
            self.skipTest('exact native checkout unavailable in Primary sandbox; CI must execute this test')
        r=gate.verify_repository(Path(env))
        self.assertEqual(r['nativeCommit'],gate.NATIVE_COMMIT)
        self.assertFalse(r['physicalAndPublicPopulationEquivalenceProven'])
        self.assertFalse(r['classGcMetadataEpochProven'])
        self.assertEqual(r['nativeFilesVerified'],len(gate.PINNED_BLOBS))


if __name__=='__main__':unittest.main()
