"""Fresh synthetic evidence mutations; no production artifact is rewritten."""
import copy
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import m06_results as gate
from shadow_tools import VerificationError


def diagnostic():
    return dict(schemaVersion=1,enabled=True,stateCode=6,state='Committed',generation=1,methodChecks=8,
                shadowMethodChecks=4,rejectedBaselineMethods=0,baselineClassCctorStarted=0,shadowClassCctorStarted=2,
                interpreterTransformations=9,shadowInterpreterTransformations=5,droppedClassObservations=0,classes=[])


def class_row():
    return dict(logicalAssembly=gate.INTERNAL,typeKey='type(1:x/1:y/1:z@0)',executionModeCode=1,executionMode='InterpreterShadow',physicalImageKind='Interpreter',isActive=True,
                cctorStarted=True,cctorFinished=True,hasInitializationException=False,staticStoragePointer='',pointerDetailsAvailable=False,staticStorageAvailable=True)


def image():
    return dict(identity=dict(name=gate.INTERNAL,fullName=gate.INTERNAL+', Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'),methods=[
        dict(name='NewObservations',declaringType=gate.witness(gate.INTERNAL),instructions=['0000:ldstr utf8:TWFya2Vy'],metadataToken=0x06000001),
        dict(name='WarmupValue',declaringType=gate.witness(gate.INTERNAL),instructions=['0000:ldc.i4 System.Int32:5000','0001:ldarg.0','0002:add','0003:ret'],metadataToken=0x06000002)])


class M06ResultTests(unittest.TestCase):
    def test_declared_inventory_is_exact_twenty_eight(self):
        self.assertEqual(len(gate.MODES),28)
        self.assertIn('T06-13-ReleaseNoPdb',gate.MODES)
        self.assertIn('T06-09-BaselineRecovery',gate.MODES)

    def test_public_inventory_eleven_and_twenty_two(self):
        self.assertEqual(len(gate.API_NAMES),11);self.assertEqual(len(gate.ERROR_NAMES),22)
        self.assertEqual(gate.ERROR_NAMES[21],'BaselineMethodExecution')

    def test_exact_dto_primitive_inventory_includes_native_metadata_token(self):
        self.assertEqual(gate.DTO_PRIMITIVES,frozenset(('System.Int32','System.UInt32','System.UInt64',
                                                       'System.Int64','System.Boolean','System.String')))

    def test_feature_off_projection_ignores_only_native_identity(self):
        linked=dict(schemaVersion=2,buildGuid='on-guid',nativeLibrarySha256='1'*64,target='StandaloneOSX',architecture='arm64',
                    sourceDirectory='/managed/linked',reflectionBindingEvidenceHash='2'*64,protectedAssemblies=['Bootstrap'],
                    assemblies=[dict(name='Business',path='Business.dll',sha256='3'*64,mvid='mvid',pdbPath='Business.pdb',pdbSha256='4'*64)])
        on=dict(schemaVersion=1,kind='PlayerBuildInputs',snapshotHash='5'*64,unityVersion='2022.3.62f2',target='StandaloneOSX',architecture='arm64',
                buildId='M06-Baseline-v7',buildGuid='on-guid',playerOutput='/players/on',nativeLibraryPath='/players/on/GameAssembly.dylib',
                nativeLibrarySha256='1'*64,playerBuildSucceeded=True,playerBuildFilterCaptured=True,playerBuildOptions=129,
                normalHotUpdateAssemblies=['Business'],extraScriptingDefines=['PINNED'],sourcePins=dict(schemaVersion=1),
                assemblies=[dict(name='Business',path='Assemblies/Business.dll',sha256='6'*64,pdbPath='Symbols/Business.pdb',pdbSha256='7'*64,sourcePath='/compiler/Business.dll')],
                references=[],filteredAssemblies=[],filteredAssemblyCapabilities=[],linkedPlayerReceipt=linked,linkedPlayerReceiptHash='8'*64,
                linkerExcludedAssemblies=[],linkerExcludedAssemblyCapabilities=[])
        off=copy.deepcopy(on)
        off.update(snapshotHash='9'*64,buildGuid='off-guid',playerOutput='/players/off',nativeLibraryPath='/players/off/GameAssembly.dylib',
                   nativeLibrarySha256='a'*64,linkedPlayerReceiptHash='b'*64)
        off['linkedPlayerReceipt'].update(buildGuid='off-guid',nativeLibrarySha256='a'*64,reflectionBindingEvidenceHash='c'*64)
        self.assertEqual(gate.managed_player_inputs(on,'on'),gate.managed_player_inputs(off,'off'))
        off['assemblies'][0]['sha256']='d'*64
        self.assertNotEqual(gate.managed_player_inputs(on,'on'),gate.managed_player_inputs(off,'off'))

    def test_native_syntax_gate_covers_global_metadata_scope(self):
        source=(Path(__file__).resolve().parents[1]/'run-m06-native-tests.py').read_text()
        self.assertIn('"vm/GlobalMetadata.cpp"',source)

    def test_valid_actual_counter_shape(self):
        self.assertEqual(gate.verify_execution_diagnostic(diagnostic(),'test',True),diagnostic())

    def test_every_execution_field_is_required(self):
        for key in gate.EXEC_FIELDS.split():
            with self.subTest(field=key):
                value=diagnostic();del value[key]
                with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'missing',True)

    def test_unknown_execution_fields_rejected(self):
        value=diagnostic();value['phantom']=0
        with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'unknown',True)

    def test_zero_false_types_are_not_interchangeable(self):
        for key in gate.EXEC_COUNTERS.split()+gate.EXEC_INTS.split():
            with self.subTest(field=key):
                value=diagnostic();value[key]=False
                with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'bool',True)
        value=diagnostic();value['enabled']=1
        with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'integer',True)

    def test_ulong_overflow_negative_float_and_numeric_string_reject(self):
        for invalid in (-1,1<<64,1.0,'0',None):
            value=diagnostic();value['methodChecks']=invalid
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'ulong',True)

    def test_uint64_does_not_truncate_at_signed_max(self):
        value=diagnostic();value['methodChecks']=(1<<64)-1
        gate.verify_execution_diagnostic(value,'ulong-max',True)

    def test_overflow_and_baseline_execution_are_never_acceptance(self):
        for key in ('droppedClassObservations','rejectedBaselineMethods','baselineClassCctorStarted'):
            value=diagnostic();value[key]=1
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'unsafe',True)

    def test_subset_counters_cannot_exceed_totals(self):
        for subset,total in (('shadowMethodChecks','methodChecks'),('shadowInterpreterTransformations','interpreterTransformations')):
            value=diagnostic();value[subset]=value[total]+1
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'subset',True)

    def test_state_code_name_both_required(self):
        for field,value_ in (('state','FailedAfterCommit'),('stateCode',9),('stateCode',True)):
            value=diagnostic();value[field]=value_
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'state',True)

    def test_class_twelve_field_inventory(self):
        self.assertEqual(len(gate.CLASS_FIELDS.split()),12)
        value=diagnostic();value['classes']=[class_row()]
        gate.verify_execution_diagnostic(value,'class',False)
        for key in gate.CLASS_FIELDS.split():
            bad=copy.deepcopy(value);del bad['classes'][0][key]
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(bad,'class-missing',False)

    def test_release_does_not_publish_or_fabricate_addresses(self):
        for changes in (dict(pointerDetailsAvailable=True,staticStoragePointer='0x123'),dict(staticStoragePointer='0x123')):
            value=diagnostic();row=class_row();row.update(changes);value['classes']=[row]
            with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'release-pointer',False)

    def test_missing_storage_never_gets_synthetic_zero_pointer(self):
        value=diagnostic();row=class_row();row.update(pointerDetailsAvailable=True,staticStorageAvailable=False,staticStoragePointer='0x0');value['classes']=[row]
        with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'fake-pointer',True)

    def test_duplicate_class_observation_rejects(self):
        value=diagnostic();value['classes']=[class_row(),class_row()]
        with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'duplicate',True)

    def test_native_finished_or_no_cctor_is_preserved(self):
        value=diagnostic();row=class_row();row['cctorStarted']=False;value['classes']=[row]
        gate.verify_execution_diagnostic(value,'no-cctor',True)
        row['hasInitializationException']=True
        with self.assertRaises(VerificationError):gate.verify_execution_diagnostic(value,'exception-without-start',True)

    def test_global_module_type_key_is_exact_and_owner_bound(self):
        self.assertEqual(gate.global_module_type_key(gate.INTERNAL),
                         'type(33:assemblya.implementation.internal/0:/8:<Module>@0)')
        self.assertNotEqual(gate.global_module_type_key(gate.INTERNAL),
                            'type(33:assemblya.implementation.internal/0:/8:<module>@0)')
        self.assertNotEqual(gate.global_module_type_key(gate.CONTRACTS),
                            gate.global_module_type_key(gate.INTERNAL))

    def test_json_duplicate_unknown_numeric_constants_reject(self):
        for text in ('{"value":0,"value":1}','{"value":NaN}','{"value":Infinity}'):
            with self.assertRaises(VerificationError):gate.json_text(text,'json')

    def test_exact_nested_boolean_tampering_rejects(self):
        with self.assertRaises(VerificationError):gate.exact({'rows':[{'value':False}]},{'rows':[{'value':0}]},'typed')

    def test_generation_hash_domain_and_clear_field(self):
        value=dict(schemaVersion=1,planHash='old',path='a/b',enabled=False,capacity=0)
        one=gate.canonical_hash(value,'planHash','assembly-shadow-generation-plan:1')
        value['planHash']='replacement'
        self.assertEqual(one,gate.canonical_hash(value,'planHash','assembly-shadow-generation-plan:1'))
        self.assertNotEqual(one,gate.canonical_hash(value,'planHash','assembly-shadow-generation-output:1'))
        value['enabled']=True
        self.assertNotEqual(one,gate.canonical_hash(value,'planHash','assembly-shadow-generation-plan:1'))

    def test_generation_source_pdb_normalizes_release_and_development_pairs(self):
        self.assertEqual(gate.generation_source_pdb(dict(pdbPath='',pdbSha256=''),'release'),(None,None))
        self.assertEqual(gate.generation_source_pdb(dict(pdbPath='Symbols/Test.pdb',pdbSha256='a'*64),'development'),
                         ('Snapshot/Symbols/Test.pdb','a'*64))
        for value in (dict(pdbPath='Symbols/Test.pdb',pdbSha256=''),dict(pdbPath='',pdbSha256='a'*64)):
            with self.assertRaises(VerificationError):gate.generation_source_pdb(value,'mismatch')

    def test_patch_reference_names_compare_canonically_without_collisions(self):
        self.assertEqual(gate.canonical_names(['AssemblyA.Contracts','netstandard'],'references'),
                         ['assemblya.contracts','netstandard'])
        with self.assertRaises(VerificationError):
            gate.canonical_names(['AssemblyA.Contracts','assemblya.contracts'],'references')

    def test_canonical_generation_json_rejects_whitespace(self):
        with tempfile.TemporaryDirectory(prefix='m06-json-') as directory:
            path=Path(directory)/'generation.json';value=dict(schemaVersion=1,planHash=None)
            value['planHash']=gate.canonical_hash(value,'planHash','test:1');path.write_bytes(gate.datacontract_bytes(value))
            gate.read_canonical(path,'schemaVersion planHash','planHash','test:1')
            path.write_text(json.dumps(value,indent=2))
            with self.assertRaises(VerificationError):gate.read_canonical(path,'schemaVersion planHash','planHash','test:1')

    def test_replay_receipt_path_supports_default_and_explicit_independent_receipts(self):
        with tempfile.TemporaryDirectory(prefix='m06-replay-path-') as directory:
            root=Path(directory).resolve();manifest=root/'m06-fixtures.json';manifest.write_text('{}')
            default=root/'m06-editor-replay.json';default.write_text('{}')
            explicit=root/'m06-editor-replay-independent.json';explicit.write_text('{}')
            context=dict(path=manifest)
            self.assertEqual(gate.replay_receipt_path(context),default)
            self.assertEqual(gate.replay_receipt_path(context,explicit),explicit)
            with self.assertRaises(VerificationError):gate.replay_receipt_path(context,Path('relative.json'))

    def test_capacity_coverage_is_structural_not_key_name(self):
        selected=dict(target='StandaloneOSX',architecture='arm64',development=False,templateSha256='a')
        required=copy.deepcopy(selected)
        for kind in gate.ABI_KINDS:selected[kind]=[];required[kind]=[]
        selected['reversePInvoke']=[dict(key='optimized',abi='structural',capacity=3)]
        required['reversePInvoke']=[dict(key='unoptimized',abi='structural',capacity=2)]
        gate.verify_abi_coverage(selected,required,'coverage')
        required['reversePInvoke'][0]['capacity']=4
        with self.assertRaises(VerificationError):gate.verify_abi_coverage(selected,required,'capacity')

    def test_struct_runtime_key_mapping_cannot_be_dropped(self):
        selected=dict(target='StandaloneOSX',architecture='arm64',development=True,templateSha256='a')
        for kind in gate.ABI_KINDS:selected[kind]=[]
        required=copy.deepcopy(selected);selected['structMappings']=[dict(key='wrong',abi='same',capacity=1)];required['structMappings']=[dict(key='needed',abi='same',capacity=1)]
        with self.assertRaises(VerificationError):gate.verify_abi_coverage(selected,required,'struct')

    def test_generation_development_context_is_not_relabelable(self):
        selected=dict(target='StandaloneOSX',architecture='arm64',development=True,templateSha256='a')
        required=dict(selected,development=False)
        with self.assertRaises(VerificationError):gate.verify_abi_coverage(selected,required,'release')

    def test_business_duplicate_keys_are_not_last_wins(self):
        with self.assertRaises(VerificationError):gate.values_map(['marker=a','marker=b'],'values')

    def test_warmup_exact_four_methods_per_owner(self):
        core='mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089';name=gate.INTERNAL;owner=gate.witness(name)
        methods=[]
        for method,type_,arity in (('WarmupValue','System.Int32',0),('WarmupEcho','System.Int32',1),('WarmupEcho','System.String',1),('Run','System.String',0)):
            arg=dict(assembly=core,type=type_);methods.append(dict(assembly=name,declaringType=owner,name=method,isStatic=True,genericArity=arity,genericArguments=[arg] if arity else [],returnType=dict(assembly=core,type='System.String[]') if method=='Run' else arg,parameterTypes=[arg]))
        value=dict(types=[dict(assembly=name,type=owner)],methods=methods)
        gate.verify_warmup(value,[name],{name:core},'warmup')
        for mutation in ('missing','false-static','wrong-owner','wrong-return'):
            bad=copy.deepcopy(value)
            if mutation=='missing':bad['methods'].pop()
            elif mutation=='false-static':bad['methods'][0]['isStatic']=False
            elif mutation=='wrong-owner':bad['methods'][0]['assembly']=gate.CONTRACTS
            else:bad['methods'][0]['returnType']['type']='System.Int64'
            with self.assertRaises(VerificationError):gate.verify_warmup(bad,[name],{name:core},'warmup-tamper')

    def test_warmup_uses_each_byte_bound_compiler_corlib_provider(self):
        mscorlib='mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'
        netstandard='netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51'
        providers={name.casefold():dict(fullName=full) for name,full in (('mscorlib',mscorlib),('netstandard',netstandard))}
        identity=dict(referenceIdentities=[dict(name='netstandard',fullName=netstandard)])
        self.assertEqual(gate.compiler_core_identity(identity,providers,'compiler-core'),netstandard)
        identity['referenceIdentities']=[dict(name='mscorlib',fullName=mscorlib)]
        self.assertEqual(gate.compiler_core_identity(identity,providers,'compiler-core'),mscorlib)
        identity['referenceIdentities'].append(dict(name='netstandard',fullName=netstandard))
        with self.assertRaises(VerificationError):gate.compiler_core_identity(identity,providers,'ambiguous-core')
        identity['referenceIdentities']=[dict(name='netstandard',fullName=netstandard.replace('2.1.0.0','9.0.0.0'))]
        with self.assertRaises(VerificationError):gate.compiler_core_identity(identity,providers,'changed-core')

    def test_normal_and_negative_fixture_roots_are_explicit(self):
        self.assertEqual(gate.order_for('P01'),[gate.INTERNAL]);self.assertEqual(len(gate.order_for('P02')),3);self.assertEqual(len(gate.order_for('P03')),5)
        self.assertIn('ASSEMBLY_SHADOW_M06_INITIALIZER_THROW',gate.expected_defines('InitializerFailure'))
        with self.assertRaises(VerificationError):gate.order_for('Unrecognized')

    def test_off_api_checks_keep_actual_codes_and_null_string_output(self):
        result=dict(mode='T06-11-FeatureOff',checks=[dict(name=api+':disabled',actualCode=1,expectedCode=1,actual=value,expected=value) for api,value in (('GetState','Disabled'),('GetAssemblyExecutionMode','AotBaseline'),('GetTypeResolutionInfo',''))])
        gate.verify_checks(result,[],'off')
        for mutate in ('omit','code','false','output','unknown'):
            bad=copy.deepcopy(result)
            if mutate=='omit':bad['checks'].pop()
            elif mutate=='code':bad['checks'][0]['actualCode']=0
            elif mutate=='false':bad['checks'][0]['expectedCode']=True
            elif mutate=='output':bad['checks'][-1]['actual']='must-be-cleared'
            else:bad['checks'][0]['passed']=True
            with self.assertRaises(VerificationError):gate.verify_checks(bad,[],'off-tamper')

    def test_recovery_requires_not_registered_not_fabricated_success(self):
        rows=[('GetState:baseline-recovery',0,'Disabled'),('GetAssemblyExecutionMode:recovery',4,'AotBaseline'),('GetAssemblyExecutionMode:baseline-recovery:'+gate.INTERNAL,4,'AotBaseline'),('GetTypeResolutionInfo:'+gate.witness(gate.INTERNAL),0,'')]
        result=dict(mode='T06-09-BaselineRecovery',checks=[dict(name=name,actualCode=code,expectedCode=code,actual=value,expected=value) for name,code,value in rows])
        gate.verify_checks(result,[],'recovery')
        for index in (1,2):
            bad=copy.deepcopy(result);bad['checks'][index]['actualCode']=0
            with self.assertRaises(VerificationError):gate.verify_checks(bad,[],'recovery-tamper')

    def test_failure_stops_at_commit_not_business(self):
        phases,timings=gate.execution_layout('T06-09-InitializerFailure',[gate.INTERNAL])
        self.assertEqual(phases[-1],'initializer-failure');self.assertNotIn('business-before',phases)
        self.assertEqual([r[0] for r in timings],['configure','begin','stage','validate','commit'])

    def test_native_event_order_publishes_before_initializers(self):
        closure=list(gate.CANDIDATES);rows=gate.transaction_events('committed',closure)
        self.assertEqual([r['sequence'] for r in rows],list(range(1,len(rows)+1)))
        published=next(i for i,r in enumerate(rows) if r['kind']=='active-published')
        self.assertTrue(all(r['generation']==0 for r in rows[:published]))
        self.assertEqual([r['name'] for r in rows if r['kind']=='initializer-complete'],closure)
        self.assertTrue(all(not r['kind'].startswith('initializer-') for r in gate.transaction_events('validated',closure)))
        failed=gate.transaction_events('initializer-failure',[gate.INTERNAL])
        self.assertEqual(failed[-1]['kind'],'initializer-failed');self.assertNotIn('transaction-committed',[r['kind'] for r in failed])

    def test_warmup_preserves_each_generic_call_and_first_second_boundary(self):
        phases,timings=gate.execution_layout('T06-10-Warmup-P03',list(gate.CANDIDATES))
        self.assertEqual(phases.count('warmup-method-'+gate.INTERNAL+'-WarmupEcho'),2)
        self.assertEqual(phases.count('warmup-call-before-'+gate.INTERNAL+'-WarmupEcho'),2)
        self.assertEqual(sum(row[0]=='first' for row in timings),15)
        self.assertEqual(sum(row[0]=='second' for row in timings),15)
        for _,before,after in timings:self.assertGreater(after,before)

    def test_release_has_full_observations_not_development_relabel(self):
        phases,timings=gate.execution_layout('T06-13-ReleaseNoPdb',list(gate.CANDIDATES))
        self.assertEqual(phases[-1],'final');self.assertEqual(sum(row[0]=='first' for row in timings),5)
        self.assertNotIn('warmup',phases)

    def header_fixture(self,root):
        root=root.resolve()
        manifest=root/'fixtures.json';manifest.write_text('{}');receipt=root/'player.json';receipt.write_text('{}')
        output=root/'Player.app';data=output/'Contents';data.mkdir(parents=True)
        player=dict(unityVersion='2022.3.62f2',buildGuid='b'*32,baselineBuildId='c'*64,runtimeAbiHash='d'*64,variant='NativeOn',developmentBuild=True,generationProofPath=str(root/'generation.json'),generationProofSha256='e'*64,executionProofPath=str(root/'execution.json'),executionProofSha256='f'*64,playerOutput=str(output))
        result={key:'' for key in gate.RESULT_STRINGS.split()};result.update({key:0 for key in gate.RESULT_INTS.split()});result.update({key:[] for key in gate.RESULT_ARRAYS.split()})
        result.update({key:value for key,value in player.items() if key!='playerOutput'})
        result.update(schemaVersion=1,milestone='M06',mode='T06-01-New-P01',result='Passed',il2cpp=True,businessLaunched=False,ordinary=None,processId=4321,platform='OSXPlayer',playerDataPath=str(data),moduleMvidObservationPolicy=gate.prior.MVID_POLICY,fixtureManifestPath=str(manifest),fixtureManifestSha256=gate.digest(manifest),playerBuildReceiptPath=str(receipt),playerBuildReceiptSha256=gate.digest(receipt))
        return root/'result.json',result,dict(path=manifest,manifest={}),dict(path=receipt,player=player)

    def test_header_exact_required_unknown_and_mistyped_fields(self):
        with tempfile.TemporaryDirectory(prefix='m06-header-') as directory:
            path,result,context,build=self.header_fixture(Path(directory));path.write_text(json.dumps(result));gate.verify_result_header(path,context,build)
            for key in gate.RESULT_FIELDS.split():
                bad=copy.deepcopy(result);del bad[key];path.write_text(json.dumps(bad))
                with self.subTest(field=key),self.assertRaises(VerificationError):gate.verify_result_header(path,context,build)
            for changes in (dict(unknown=0),dict(processId=0),dict(processId=False),dict(il2cpp=1),dict(developmentBuild=False),dict(mode='T06-unknown'),dict(fixtureManifestSha256='0'*64),dict(playerBuildReceiptSha256='0'*64)):
                bad=copy.deepcopy(result);bad.update(changes);path.write_text(json.dumps(bad))
                with self.subTest(change=changes),self.assertRaises(VerificationError):gate.verify_result_header(path,context,build)

    def test_header_binds_actual_raw_bytes_not_only_json_claim(self):
        with tempfile.TemporaryDirectory(prefix='m06-header-') as directory:
            root=Path(directory).resolve();path,result,context,build=self.header_fixture(root)
            raw=root/'raw.json';raw.write_text('{"counter":7}');result.update(nativeDiagnosticsJson=raw.read_text(),rawTransactionDiagnosticsPath=str(raw),rawTransactionDiagnosticsSha256=gate.digest(raw));path.write_text(json.dumps(result))
            gate.verify_result_header(path,context,build)
            raw.write_text('{"counter":8}')
            with self.assertRaises(VerificationError):gate.verify_result_header(path,context,build)

    def test_header_duplicate_keys_are_not_last_wins(self):
        with tempfile.TemporaryDirectory(prefix='m06-header-') as directory:
            path,result,context,build=self.header_fixture(Path(directory));path.write_text(json.dumps(result)[:-1]+',"processId":4321}')
            with self.assertRaises(VerificationError):gate.verify_result_header(path,context,build)

    def test_fresh_case_inventory_rejects_pid_reuse_and_duplicates(self):
        found={};pids=set()
        for i,mode in enumerate(sorted(gate.MODES)):gate.record_case(found,pids,dict(mode=mode,processId=i+10),'case')
        self.assertEqual(len(found),28)
        for value in (dict(mode='T06-13-ReleaseNoPdb',processId=99),dict(mode='unknown',processId=99)):
            with self.assertRaises(VerificationError):gate.record_case(found,pids,value,'duplicate')
        found={};pids=set();gate.record_case(found,pids,dict(mode='T06-03-P01',processId=10),'one')
        for pid in (10,False,0,-1):
            with self.assertRaises(VerificationError):gate.record_case(found,pids,dict(mode='T06-04-P02',processId=pid),'reuse')

    def test_canonical_transport_join_preserves_physical_name_and_rejects_collisions(self):
        row=dict(name='assemblya.contracts',path='Assemblies/assemblya.contracts.dll')
        self.assertIs(gate.named([row],'AssemblyA.Contracts','join'),row)
        with self.assertRaises(VerificationError):gate.named([row,dict(name='AssemblyA.Contracts')],'AssemblyA.Contracts','collision')

    def test_timing_endpoint_counters_cannot_be_borrowed_from_other_snapshots(self):
        execution=[dict(interpreterTransformations=n,shadowInterpreterTransformations=n//2) for n in (2,4,6,8)]
        phases=['configure-before','configure-after','begin-before','begin-after'];layout=[('configure',0,1),('begin',2,3)]
        rows=[]
        for phase,before,after in layout:
            rows.append(dict(phase=phase,stopwatchFrequency=1000,startTicks=10,endTicks=12,elapsedTicks=2,transformationsBefore=execution[before]['interpreterTransformations'],transformationsAfter=execution[after]['interpreterTransformations'],shadowTransformationsBefore=execution[before]['shadowInterpreterTransformations'],shadowTransformationsAfter=execution[after]['shadowInterpreterTransformations']))
        result=dict(mode='T06-01-New-P01',timings=rows)
        gate.verify_timings(result,execution,phases,layout,[gate.INTERNAL],'timing')
        for changes in (dict(transformationsAfter=8,shadowTransformationsAfter=4),dict(elapsedTicks=0),dict(stopwatchFrequency=False),dict(transformationsBefore='2')):
            bad=copy.deepcopy(result);bad['timings'][0].update(changes)
            with self.assertRaises(VerificationError):gate.verify_timings(bad,execution,phases,layout,[gate.INTERNAL],'timing-tamper')
        for changed in ([],rows[:1],rows[::-1],rows+rows):
            with self.assertRaises(VerificationError):gate.verify_timings(dict(mode=result['mode'],timings=changed),execution,phases,layout,[gate.INTERNAL],'timing-missing')


class M06ActualWitnessTests(unittest.TestCase):
    """Execute only freshly compiled baseline C# bodies, not Unity/native APIs.

    This catches expected-value drift independently of Bootstrap's validator.
    Real interpreter dispatch, native state and Player sequencing remain separate
    required evidence in the 28-case gate.
    """
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='m06-offline-witness-');cls.root=Path(cls.temp.name).resolve()
        cls.base=Path(os.environ.get('UNITY_MONO_ROOT','/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge'))
        if not (cls.base/'bin/mono').is_file():raise unittest.SkipTest('Pinned Unity Mono compiler unavailable')
        cls.project=Path(__file__).resolve().parents[3]
        engine=cls.base.parent/'Managed/UnityEngine'
        references=['-r:'+str(f) for f in sorted(engine.glob('*.dll'))]+['-r:'+str(cls.base/'lib/mono/4.5/Facades/netstandard.dll')]
        cls.images={}
        dirs=['AssemblyA/Contracts','AssemblyA/Implementation/Extensibility','AssemblyA/Implementation/Internal','Consumers/ContractsConsumer','Consumers/ExtensibilityConsumer']
        for name,directory in zip(gate.CANDIDATES,dirs):
            output=cls.root/(name+'.dll')
            command=[str(cls.base/'bin/mono'),str(cls.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:library','-langversion:latest','-out:'+str(output)]+references+[str(p) for p in sorted((cls.project/'Assets/AssemblyShadowDemo'/directory).rglob('*.cs'))]
            run=subprocess.run(command,capture_output=True,text=True)
            if run.returncode:raise RuntimeError(run.stdout+run.stderr)
            references.append('-r:'+str(output))
            module=gate.ExecutionMetadata(output.read_bytes(),output)
            cls.images[name]=dict(identity=module.identity,methods=gate.read_methods(output))
        source=cls.root/'Run.cs'
        source.write_text('''using System; using System.Reflection; using System.Threading.Tasks; using System.Collections.Generic; using System.Runtime.Serialization.Json;
public class Row { public string name; public string[][] values; }
public static class Run { public static void Main(string[] args) { var rows=new List<Row>(); foreach(var name in args[1].Split('|')) { string owner=name=="AssemblyShadowDemo.ContractsConsumer"?"AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness":name=="AssemblyShadowDemo.ExtensibilityConsumer"?"AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness":name+".M06ExecutionWitness"; var type=Assembly.Load(name).GetType(owner,true); var values=new string[2][]; for(int i=0;i<2;i++) values[i]=args[0]=="async"?((Task<string[]>)type.GetMethod("RunAsync").Invoke(null,null)).GetAwaiter().GetResult():(string[])type.GetMethod("Run").Invoke(null,new object[]{args[0]}); rows.Add(new Row {name=name,values=values}); } new DataContractJsonSerializer(typeof(Row[])).WriteObject(Console.OpenStandardOutput(),rows.ToArray()); } }''')
        run=subprocess.run([str(cls.base/'bin/mono'),str(cls.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:exe','-out:'+str(cls.root/'Run.exe'),'-r:'+str(cls.base/'lib/mono/4.5/System.Runtime.Serialization.dll'),str(source)],capture_output=True,text=True)
        if run.returncode:raise RuntimeError(run.stdout+run.stderr)
        cls.env=dict(os.environ,MONO_PATH=str(engine))

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_all_six_actual_baseline_phase_pairs(self):
        for phase in ('new','statics','dispatch','delegates','generics','async'):
            run=subprocess.run([str(self.base/'bin/mono'),str(self.root/'Run.exe'),phase,'|'.join(gate.CANDIDATES)],capture_output=True,text=True,env=self.env)
            self.assertEqual(run.returncode,0,run.stderr)
            rows=json.loads(run.stdout);self.assertEqual(len(rows),5)
            for row in rows:
                for invocation,values in enumerate(row['values']):
                    with self.subTest(phase=phase,owner=row['name'],invocation=invocation):
                        gate.verify_business(values,row['name'],phase,self.images[row['name']],'actual-baseline',invocation,row['values'][0] if invocation else None,self.images[gate.EXTENSIBILITY])

    def test_actual_baseline_exception_frames_retain_method_availability(self):
        run=subprocess.run([str(self.base/'bin/mono'),str(self.root/'Run.exe'),'exceptions','|'.join(gate.CANDIDATES)],capture_output=True,text=True,env=self.env)
        self.assertEqual(run.returncode,0,run.stderr)
        for row in json.loads(run.stdout):
            for values in row['values']:
                with self.subTest(owner=row['name']):gate.verify_exception(values,self.images[row['name']],'actual-exception',False,True)
        first=json.loads(run.stdout)[0];values=first['values'][0]
        missing=[value for value in values if '.methodAvailable=' not in value]
        with self.assertRaises(VerificationError):gate.verify_exception(missing,self.images[first['name']],'missing-availability',False,True)
        observed=gate.values_map(values,'actual-exception')
        for key,value in list(observed.items()):
            if key.endswith('.declaringType') and value==gate.witness(first['name']):
                prefix=key.removesuffix('declaringType')
                for suffix,replacement in (('methodAvailable','False'),('declaringType','absent'),('method','absent'),('token','0')):observed[prefix+suffix]=replacement
        with self.assertRaises(VerificationError):gate.verify_exception([key+'='+value for key,value in observed.items()],self.images[first['name']],'unavailable-is-not-candidate-proof',False,True)

    def test_class_keys_require_actual_owner_and_definition_bytes(self):
        identities={name:gate.prior.read_identity(self.root/(name+'.dll')) for name in gate.CANDIDATES}
        name=gate.INTERNAL;namespace,typename=gate.witness(name).rsplit('.',1)
        part=lambda text:str(len(text.encode('utf-8')))+':'+text
        key='type('+part(name.casefold())+'/'+part(namespace)+'/'+part(typename)+'@0)'
        row=class_row();row['typeKey']=key;snapshot=diagnostic();snapshot['classes']=[row]
        gate.verify_class_keys([snapshot],identities,[name],'actual-class-key')
        for changes in (dict(typeKey=key.replace(typename,'X'*len(typename))),dict(logicalAssembly=gate.CONTRACTS),dict(isActive=False),dict(executionModeCode=0),dict(physicalImageKind='Aot')):
            bad=copy.deepcopy(snapshot);bad['classes'][0].update(changes)
            with self.assertRaises(VerificationError):gate.verify_class_keys([bad],identities,[name],'forged-class-key')


if __name__=='__main__':unittest.main()
