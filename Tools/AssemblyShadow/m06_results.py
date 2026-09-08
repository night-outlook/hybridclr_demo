"""Strict read-only M06 execution/artifact acceptance gate.

Unsigned receipts are evidence, not authentication. Exact Editor replay owns
semantic/resource policy; this gate independently reopens bytes and execution
observations. Historical M00-M05 proof domains are never rewritten.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

import m04_results as prior
import m07_results as r01_schema
import m05_results as types
import m05_raw_type_admissions as raw
from m06_execution_metadata import ExecutionMetadata, LinkedSchemaResolver, read_methods, schema_fields
from shadow_tools import VerificationError, require, unique_object

CANDIDATES = prior.CANDIDATES
ORDER = prior.PROVIDER_ORDER
INTERNAL = prior.INTERNAL
CONTRACTS, EXTENSIBILITY, _, CONTRACTS_CONSUMER, EXTENSIBILITY_CONSUMER = CANDIDATES
MODES = frozenset([f"T06-{n:02d}-{word}-{p}" for n,word in ((1,"New"),(2,"Statics"),(6,"Delegates"),(7,"Generics"),(8,"Async"),(10,"Warmup"),(12,"NoWarmup")) for p in ("P01","P02","P03")] +
                  ["T06-03-P01","T06-04-P02","T06-05-P03","T06-09-InitializerFailure","T06-09-BaselineRecovery","T06-11-FeatureOff","T06-13-ReleaseNoPdb"])
RESULT_INTS = "schemaVersion processId configureCode beginCode validateCode commitCode abortCode stateCode executionModeCode diagnosticsCode executionDiagnosticsCode typeResolutionCode"
RESULT_STRINGS = "milestone mode result error unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash variant moduleMvidObservationPolicy fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 generationProofPath generationProofSha256 executionProofPath executionProofSha256 patchId patchManifestPath patchManifestSha256 compileSnapshotHash state executionMode nativeDiagnosticsJson executionDiagnosticsJson rawTransactionDiagnosticsPath rawTransactionDiagnosticsSha256 rawExecutionDiagnosticsPath rawExecutionDiagnosticsSha256 recoveryResultPath recoveryResultSha256"
RESULT_ARRAYS = "stageOrder checks transactionSnapshots executionSnapshots observations methodObservations moduleObservations warmupObservations timings supplementaryMetadata stageResults"
RESULT_FIELDS = RESULT_INTS+" "+RESULT_STRINGS+" "+RESULT_ARRAYS+" il2cpp developmentBuild businessLaunched ordinary"
R01_RESULT_FIELDS = RESULT_FIELDS + " reserveCode"
MANIFEST_FIELDS=prior.MANIFEST_FIELDS+" developmentBuild generationProofPath generationProofSha256 initializerFailureFixture"
FIXTURE_FIELDS=prior.FIXTURE_FIELDS+" typeInventories variant generationPlanPath generationPlanSha256 developmentBuild requiredAotMetadataNames"
PLAYER_FIELDS=prior.PLAYER_FIELDS+" buildOptions developmentBuild typeProofPath typeProofSha256 executionProofPath executionProofSha256 generationProofPath generationProofSha256 supplementaryMetadataInputs"
GENERATION_FIELDS="schemaVersion milestone policy baselineBuildId unityVersion target architecture baselineCompileSnapshot baselineCompileSnapshotHash selectedPlanId developmentBuild sourcePins plans installedOutputs"
PLAN_PROOF_FIELDS="planId compileSnapshot compileSnapshotHash planPath planSha256 planHash compilerModePath compilerModeSha256 executionPolicyPath executionPolicySha256 aotInputPath aotInputSha256 aotInventoryHash stripBuildGuid stripOutput stripSourceDirectory stripBuildOptions linkReceiptPath linkReceiptSha256 bridgeReceiptPath bridgeReceiptSha256 aotReceiptPath aotReceiptSha256 defines changedRoots closureLoadOrder requiredAotMetadataNames"
PLAN_FIELDS="schemaVersion kind purpose target architecture unityVersion snapshotHash snapshotReceiptSha256 policySha256 planHash sourcePins explicitRoots closure loadOrder ordinaryAssemblies images catalog"
IMAGE_FIELDS="name assemblyIdentity mvid path sha256 pdbPath pdbSha256 sourcePath role"
OUTPUT_FIELDS="schemaVersion kind planHash aotInventoryHash stage target architecture templateSha256 outputPath outputSha256 outputHash development maxIterations nativePointerDispatchHasMethodInfo reversePInvokeGuardPolicy collectorRoots collectorTypes collectorMethods reverseMethods nativeCallSignatures aotTypes aotMethods emittedAssemblyNames resolverCatalog managedToNative nativeToManaged adjustThunks reversePInvoke calli structMappings"
AOT_FIELDS="schemaVersion kind planHash target architecture sourceDirectory inventoryHash excludedSelectedNames images"
ABI_KINDS="managedToNative nativeToManaged adjustThunks reversePInvoke calli structMappings".split()
DTO_PRIMITIVES=frozenset("System.Int32 System.UInt32 System.UInt64 System.Int64 System.Boolean System.String".split())
EXECUTION_FIELDS="schemaVersion milestone policy compileSnapshotHash linkedPlayerReceiptHash nativeLibrarySha256 buildGuid generationProofPath generationProofSha256 typeProofPath typeProofSha256 developmentBuild apiSignatures errorCodes schemaTypes images"
EXECUTION_IMAGE_FIELDS="role planId compileSnapshotHash planHash pdbPath pdbSha256 pdbAvailable identity methods"
METHOD_FIELDS="declaringType name signature metadataToken genericArity methodFlags implementationFlags maxStack isStatic hasBody initLocals returnType parameterTypes genericParameterNames locals instructions exceptionHandlers sequencePoints"
REPLAY_FIELDS="schemaVersion milestone result comparisonPolicy fixtureManifestPath fixtureManifestSha256 baselineManifestPath baselineManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 generationProofPath generationProofSha256 baselineInputSnapshotHash baselineBuildId playerBuildGuid nativeLibrarySha256 linkedPlayerReceiptHash replayScratchPath developmentBuild validatorSourcePins fixtures"
EXEC_INTS="schemaVersion stateCode"
EXEC_COUNTERS="generation methodChecks shadowMethodChecks rejectedBaselineMethods baselineClassCctorStarted shadowClassCctorStarted interpreterTransformations shadowInterpreterTransformations droppedClassObservations"
EXEC_FIELDS=EXEC_INTS+" "+EXEC_COUNTERS+" enabled state classes"
CLASS_STRINGS="logicalAssembly typeKey executionMode physicalImageKind staticStoragePointer"
CLASS_BOOLS="isActive cctorStarted cctorFinished hasInitializationException pointerDetailsAvailable staticStorageAvailable"
CLASS_FIELDS=CLASS_STRINGS+" "+CLASS_BOOLS+" executionModeCode"
LEGACY_API_NAMES=("ConfigureCandidates(System.String,System.String[],System.String[])","BeginTransaction(System.String,System.String,System.String[],System.Int32)","StageAssembly(System.Byte[],System.Byte[])","ValidateTransaction()","CommitTransaction()","AbortTransaction()","GetState(HybridCLR.AssemblyShadowState&)","GetAssemblyExecutionMode(System.String,HybridCLR.AssemblyExecutionMode&)","GetDiagnosticsJson(System.String&)","GetTypeResolutionInfo(System.Type,System.String&)","GetExecutionDiagnosticsJson(System.String&)")
NEGOTIATED_API_NAMES=("GetMetadataCapacityJson(System.Int64[],System.String&)","ReserveMetadataBudget(System.Int64[],System.Int32)","GetRecoveryInfoJson(System.String&)")
API_NAMES=LEGACY_API_NAMES
LEGACY_ERROR_NAMES="Success FeatureDisabled InvalidState InvalidArgument CandidateNotRegistered DuplicateAssemblyName BaselineAssemblyNotFound BaselineBuildMismatch AssemblyNameMismatch BadImage UnsupportedAssembly ClosureMemberMissing UnexpectedClosureMember ReferenceResolutionFailed ReferenceEscapesClosure BaselineAlreadyUsed ResourceAbiMismatch RuntimeAbiMismatch AlreadyCommitted ModuleInitializerFailed InternalError BaselineMethodExecution".split()
NEGOTIATED_ERROR_NAMES=LEGACY_ERROR_NAMES+"CapabilityUnavailable MetadataCapacityExceeded MetadataBudgetMismatch".split()
ERROR_NAMES=LEGACY_ERROR_NAMES
fields, array, boolean, strings = prior._fields, prior._array, prior._bool, prior._strings
bound, canonical, digest = types._bound_file, types._canonical, prior.digest


def integer(value,path,minimum=-(1<<31),maximum=(1<<31)-1):
    require(type(value) is int and minimum<=value<=maximum,f"{path}: invalid exact integer")
    return value


def uint64(value,path): return integer(value,path,0,(1<<64)-1)


def exact(value,expected,path):
    require(type(value) is type(expected),f"{path}: expected {type(expected).__name__}, got {type(value).__name__}")
    if type(expected) is dict:
        require(set(value)==set(expected),f"{path}: missing {sorted(set(expected)-set(value))}, unknown {sorted(set(value)-set(expected))}")
        for key,wanted in expected.items():exact(value[key],wanted,f"{path}.{key}")
    elif type(expected) is list:
        require(len(value)==len(expected),f"{path}: expected {len(expected)} rows, got {len(value)}")
        for i,wanted in enumerate(expected):exact(value[i],wanted,f"{path}[{i}]")
    else:require(value==expected,f"{path}: expected {str(expected)[:240]!r}, got {str(value)[:240]!r}")


def json_text(text,path):
    require(type(text) is str,f"{path}: invalid JSON text")
    try:return json.loads(text,object_pairs_hook=unique_object,parse_constant=lambda value: (_ for _ in ()).throw(VerificationError(f"{path}: invalid numeric constant")))
    except (ValueError,TypeError) as error:raise VerificationError(f"{path}: invalid JSON: {error}") from error


def obj(path,shape=None):
    value=json_text(Path(path).read_text(encoding="utf-8"),path)
    require(type(value) is dict,f"{path}: expected object")
    return fields(value,shape,path) if shape else value


def names(value,path):
    rows=array(value,path);require(all(type(n) is str and n for n in rows) and len(set(rows))==len(rows),f"{path}: missing/duplicate names")
    return rows


def canonical_names(value,path):
    rows=[name.casefold() for name in names(value,path)]
    require(len(rows)==len(set(rows)),f"{path}: case-insensitive duplicate names")
    return rows


def named(rows,name,path):
    """Join receipt transport names canonically, never alter metadata identity."""
    index={}
    for row in rows:
        key=row.get('name');require(type(key) is str and key and key==key.strip(),f"{path}: invalid transport name")
        folded=key.casefold();require(folded not in index,f"{path}: colliding transport name {key}");index[folded]=row
    require(name.casefold() in index,f"{path}: missing transport name {name}")
    return index[name.casefold()]


def datacontract_bytes(value):
    # Unannotated DataContractJsonSerializer members are ordinal-name ordered.
    # It escapes solidus and control characters, but not ordinary Unicode.
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).replace('/',r'\/').encode('utf-8')


def canonical_hash(value,field,domain):
    copy_=copy.deepcopy(value);copy_[field]=None
    return hashlib.sha256((domain+'\n'+base64.b64encode(datacontract_bytes(copy_)).decode()).encode()).hexdigest()


def read_canonical(path,shape,hash_field,domain):
    value=obj(path,shape)
    require(Path(path).read_bytes()==datacontract_bytes(value),f"{path}: noncanonical DataContract JSON")
    exact(value[hash_field],canonical_hash(value,hash_field,domain),f"{path}: canonical hash")
    return value


def order_for(pid):
    if pid in ("P01","InitializerFailure"):return [INTERNAL]
    if pid=="P02":return [EXTENSIBILITY,INTERNAL,EXTENSIBILITY_CONSUMER]
    if pid=="P03":return list(ORDER)
    if pid=="Ordinary":return []
    raise VerificationError("Unknown M06 patch/plan identity")


def expected_defines(pid):
    if pid=="Ordinary":return []
    value=["ASSEMBLY_SHADOW_P01","ASSEMBLY_SHADOW_M06"]
    if pid in ("P02","P03"):value += ["ASSEMBLY_SHADOW_"+pid,"ASSEMBLY_SHADOW_M06_"+pid]
    if pid=="InitializerFailure":value += ["ASSEMBLY_SHADOW_M06_INITIALIZER_THROW"]
    return value


def verify_execution_diagnostic(value,path,development):
    fields(value,EXEC_FIELDS,path)
    strings(value,path,'state')
    for key in EXEC_INTS.split():integer(value[key],str(path)+'.'+key)
    for key in EXEC_COUNTERS.split():uint64(value[key],str(path)+'.'+key)
    exact(value['schemaVersion'],1,path);exact(value['enabled'],True,path)
    require(value['state'] in prior.STATE_CODES and value['stateCode']==prior.STATE_CODES[value['state']],f"{path}: execution state mismatch")
    for key in ('rejectedBaselineMethods','baselineClassCctorStarted','droppedClassObservations'):exact(value[key],0,f"{path}.{key}")
    require(value['shadowMethodChecks']<=value['methodChecks'] and value['shadowInterpreterTransformations']<=value['interpreterTransformations'],f"{path}: subset counters exceed totals")
    seen=set()
    for row in array(value['classes'],path):
        fields(row,CLASS_FIELDS,path);strings(row,path,CLASS_STRINGS)
        for key in CLASS_BOOLS.split():boolean(row[key],path)
        integer(row['executionModeCode'],path,0,1)
        exact(row['executionMode'],('AotBaseline','InterpreterShadow')[row['executionModeCode']],path)
        exact(row['physicalImageKind'],('Aot','Interpreter')[row['executionModeCode']],path)
        require(row['logicalAssembly'] and row['typeKey'] and (row['logicalAssembly'],row['typeKey'],row['executionModeCode']) not in seen,f"{path}: invalid/duplicate class observation")
        seen.add((row['logicalAssembly'],row['typeKey'],row['executionModeCode']))
        # Native exposes cctor_finished_or_no_cctor verbatim: a class with no
        # .cctor legitimately has finished=true and started=false.
        require(not row['hasInitializationException'] or row['cctorStarted'],f"{path}: exception without cctor start")
        if not development:exact(row['pointerDetailsAvailable'],False,path)
        require(not row['staticStoragePointer'] if not row['pointerDetailsAvailable'] or not row['staticStorageAvailable'] else re.fullmatch(r'0x[0-9a-f]+',row['staticStoragePointer']) and int(row['staticStoragePointer'],16)>0,f"{path}: fabricated/missing static address")
    return value


def verify_compiler_mode(root,snapshot,development):
    path=root/'compiler-mode.json';value=obj(path,'schemaVersion kind developmentBuild compilerOptions unityVersion target architecture snapshotHash snapshotReceiptSha256 extraScriptingDefines')
    exact(value['schemaVersion'],1,path);exact(value['kind'],'CompilePlayerScriptsMode',path)
    exact(value['developmentBuild'],development,path);exact(value['compilerOptions'],1 if development else 0,path)
    for key in ('unityVersion','target','architecture','snapshotHash','extraScriptingDefines'):exact(value[key],snapshot[key],f"{path}.{key}")
    exact(value['snapshotReceiptSha256'],digest(root/'assembly-snapshot.json'),path)
    return value


def verify_compile(root,expected_hash,baseline,development):
    root=canonical(str(root),root,'compileSnapshot',True);path=root/'assembly-snapshot.json';snapshot=obj(path)
    exact(snapshot['schemaVersion'],1,path);exact(snapshot['kind'],'CompilePlayerScripts',path)
    require(prior._linked_claim_absent(snapshot) and not (root/'LinkedPlayer').exists(),f"{path}: compile-only input claims linked acceptance")
    prior._pins(snapshot['sourcePins'],path,baseline['sourcePins'])
    prior._snapshot_files(snapshot,root,path)
    exact(snapshot['snapshotHash'],expected_hash,path);exact(snapshot['snapshotHash'],prior._snapshot_hash(snapshot,root,path),path)
    for key in ('unityVersion','target','architecture'):exact(snapshot[key],baseline[key],path)
    prior._reflection_snapshot(root,snapshot,path);raw.verify_snapshot(root,snapshot)
    verify_compiler_mode(root,snapshot,development)
    return snapshot


def verify_generation_image(image,root,path):
    fields(image,IMAGE_FIELDS,path)
    dll=prior._rel(root,image['path'],path,'generation DLL')
    actual=prior.read_identity(dll)
    for claim,key in (('name','name'),('assemblyIdentity','fullName'),('mvid','mvid'),('sha256','sha256')):exact(image[claim],actual[key],path)
    require(type(image['sourcePath']) is str and Path(image['sourcePath']).is_absolute(),f"{path}: missing generator source path")
    if image['pdbPath']:
        pdb=prior._rel(root,image['pdbPath'],path,'generation PDB');exact(digest(pdb),image['pdbSha256'],path)
    else:exact(image['pdbPath'],None,path);exact(image['pdbSha256'],None,path)
    return image


def generation_source_pdb(source,path):
    pdb_path=source.get('pdbPath');pdb_sha=source.get('pdbSha256')
    require(bool(pdb_path)==bool(pdb_sha),f"{path}: compiler PDB path/hash availability differs")
    return ('Snapshot/'+pdb_path,pdb_sha) if pdb_path else (None,None)


def verify_abi_coverage(selected,required,path):
    for key in ('target','architecture','development','templateSha256'):exact(required[key],selected[key],f"{path}.{key}")
    for kind in ABI_KINDS:
        for row in required[kind]:
            if kind=='structMappings': found=any(a['key']==row['key'] and a['abi']==row['abi'] for a in selected[kind])
            else:found=any(a['abi']==row['abi'] and a['capacity']>=row['capacity'] for a in selected[kind])
            require(found,f"{path}: selected optimized {kind} lacks actual structural ABI/capacity coverage")


def verify_output(path,plan,aot,development,stage):
    value=read_canonical(path,OUTPUT_FIELDS,'outputHash','assembly-shadow-generation-output:1')
    exact(value['schemaVersion'],1,path);exact(value['kind'],'GenerationOutput',path);exact(value['stage'],stage,path)
    for key in ('planHash','target','architecture'):exact(value[key],plan[key],path)
    exact(value['development'],development if stage=='MethodBridge' else False,path);exact(value['nativePointerDispatchHasMethodInfo'],False,path)
    exact(value['reversePInvokeGuardPolicy'],'AbortBeforeExternalDispatch' if stage=='MethodBridge' else None,path)
    exact(value['aotInventoryHash'],None if stage=='Link' else aot['inventoryHash'],path)
    selected=[i['name'] for i in plan['images']]
    roots=sorted(set(selected+[i['name'] for i in aot['images'] if i['name'].casefold() not in aot['excludedSelectedNames']])) if stage=='MethodBridge' else selected
    exact(value['collectorRoots'],roots,path)
    if stage=='MethodBridge':prior._hash(value['templateSha256'],path,'templateSha256')
    else:exact(value['templateSha256'],None,path)
    integer(value['maxIterations'],path,0,20);require(value['maxIterations']==0 if stage=='Link' else value['maxIterations']>0,f"{path}: wrong generator iteration limit")
    output=prior._rel(Path(path).parent,value['outputPath'],path,'generator output');exact(digest(output),value['outputSha256'],path)
    for kind in ABI_KINDS:
        seen=set()
        for row in array(value[kind],path):
            fields(row,'key abi capacity',path);strings(row,path,'key abi');integer(row['capacity'],path,1)
            require(row['key'] and row['abi'] and row['key'] not in seen,f"{path}: invalid duplicate optimized ABI key");seen.add(row['key'])
    for key in 'collectorRoots collectorTypes collectorMethods reverseMethods nativeCallSignatures aotTypes aotMethods emittedAssemblyNames'.split():names(value[key],path)
    unused=ABI_KINDS+['reverseMethods','nativeCallSignatures'] if stage!='MethodBridge' else ['aotTypes','aotMethods','emittedAssemblyNames']
    if stage=='Link':unused+=['collectorMethods','aotTypes','aotMethods','emittedAssemblyNames']
    for key in unused:exact(value[key],[],path)
    return value


def verify_startup(path,snapshot):
    value=obj(path,'schemaVersion bootstrapExecutionOrder milestone compileSnapshotHash startupScenePath startupSceneSha256 bootstrapScriptPath bootstrapScriptSha256 bootstrapAssemblyIdentity bootstrapTypeName startupSceneSourcePath bootstrapScriptSourcePath files scripts preloadedAssets diagnostics')
    exact(value['schemaVersion'],1,path);exact(value['milestone'],'M06',path);exact(value['compileSnapshotHash'],snapshot['snapshotHash'],path)
    exact(value['diagnostics'],[],path);exact(value['bootstrapExecutionOrder'],-32000,path)
    exact(value['bootstrapTypeName'],'AssemblyShadowDemo.M06BootstrapRunner',path)
    bound(value['startupScenePath'],value['startupSceneSha256'],path,'startupScenePath');bound(value['bootstrapScriptPath'],value['bootstrapScriptSha256'],path,'bootstrapScriptPath')
    for row in array(value['files'],path):fields(row,'sourcePath path sha256',path);bound(row['path'],row['sha256'],path,'startup file')
    for row in array(value['preloadedAssets'],path):
        fields(row,'assetPath sourcePath typeName assemblyIdentity sha256 isCandidate',path);exact(row['isCandidate'],False,path);bound(row['assetPath'],row['sha256'],path,'preloaded asset')
        require(row['assemblyIdentity'].split(',')[0] not in CANDIDATES,f"{path}: preloaded candidate asset")
    runners=[]
    for row in array(value['scripts'],path):
        fields(row,'rootAssetPath assetPath scriptPath assemblyIdentity typeName phase assetSha256 scriptSha256 assetSourcePath scriptSourcePath executionOrder isCandidate isBootstrapRunner isCandidateDependent dependencyProved callbacks dependencyEvidence',path)
        for key in ('isCandidate','isBootstrapRunner','isCandidateDependent','dependencyProved'):boolean(row[key],path)
        integer(row['executionOrder'],path);names(row['callbacks'],path);names(row['dependencyEvidence'],path)
        bound(row['assetPath'],row['assetSha256'],path,'startup script asset');bound(row['scriptPath'],row['scriptSha256'],path,'startup script')
        exact(row['isCandidate'],False,path)
        if row['isBootstrapRunner']:runners.append(row)
        elif row['callbacks'] and (row['phase']=='PreloadedAsset' or row['executionOrder']<=value['bootstrapExecutionOrder']):
            exact(row['dependencyProved'],True,path);exact(row['isCandidateDependent'],False,path)
    require(len(runners)==1 and runners[0]['typeName']==value['bootstrapTypeName'] and 'Awake' in runners[0]['callbacks'],f"{path}: actual startup runner missing/ambiguous")
    return value


def verify_generation(path,baseline,development):
    proof=obj(path,GENERATION_FIELDS);exact(proof['schemaVersion'],1,path);exact(proof['milestone'],'M06',path)
    exact(proof['policy'],'compile-only-generator-provenance:1',path);exact(proof['developmentBuild'],development,path);exact(proof['selectedPlanId'],'P03',path)
    for key in ('baselineBuildId','unityVersion','target','architecture'):exact(proof[key],baseline[key],path)
    prior._pins(proof['sourcePins'],path,baseline['sourcePins'])
    rows=array(proof['plans'],path);exact(sorted(names([r['planId'] for r in rows],path)),sorted(['Ordinary','P01','P02','P03','InitializerFailure']),path)
    plans={};outputs={}
    for row in rows:
        fields(row,PLAN_PROOF_FIELDS,path);pid=row['planId'];root=canonical(row['compileSnapshot'],path,'compileSnapshot',True)
        snapshot=verify_compile(root,row['compileSnapshotHash'],baseline,development)
        mode=bound(row['compilerModePath'],row['compilerModeSha256'],path,'compilerModePath');exact(mode,root/'compiler-mode.json',path)
        plan_path=bound(row['planPath'],row['planSha256'],path,'planPath');exact(plan_path.name,'generation-plan.json',path)
        plan=read_canonical(plan_path,PLAN_FIELDS,'planHash','assembly-shadow-generation-plan:1');exact(plan['planHash'],row['planHash'],path)
        exact(plan['schemaVersion'],1,path);exact(plan['kind'],'CompileOnlyGeneration',path);exact(plan['purpose'],'NotDeployable',path)
        for key in ('target','architecture','unityVersion'):exact(plan[key],proof[key],path)
        prior._pins(plan['sourcePins'],path,proof['sourcePins']);exact(plan['snapshotHash'],snapshot['snapshotHash'],path)
        copied=plan_path.parent/'Snapshot';exact(types._artifact_tree(root),types._artifact_tree(copied),path)
        exact(plan['snapshotReceiptSha256'],digest(root/'assembly-snapshot.json'),path)
        exact(digest(plan_path.parent/'policy.json'),plan['policySha256'],path)
        exact(sorted(names(row['defines'],path)),sorted(expected_defines(pid)),path)
        controls=('ASSEMBLY_SHADOW_REFLECTION_BINDINGS_',raw.PREFIX)
        exact(sorted(d for d in names(snapshot['extraScriptingDefines'],path) if not d.startswith(controls)),sorted(row['defines']),path)
        exact(row['closureLoadOrder'],order_for(pid),path);exact(sorted(row['changedRoots']),sorted(order_for(pid)),path)
        exact(plan['loadOrder'],order_for(pid),path)
        exact(plan['closure'],sorted(order_for(pid)),path);exact(plan['explicitRoots'],sorted(n.casefold() for n in row['changedRoots']),path)
        for collection in ('images','catalog'):
            names([i['name'].casefold() for i in array(plan[collection],path)],path)
            for image in plan[collection]:verify_generation_image(image,plan_path.parent,path)
        exact([i['name'].casefold() for i in plan['images']],[n.casefold() for n in plan['loadOrder']]+plan['ordinaryAssemblies'],path)
        catalog={i['name'].casefold():i for i in plan['catalog']}
        originals={i['name'].casefold():i for i in snapshot['assemblies']+snapshot['references']}
        exact(set(catalog),set(originals),path)
        compiled={i['name'].casefold() for i in snapshot['assemblies']}
        exact(plan['ordinaryAssemblies'],['assemblyshadowbaseline.hotupdate'],path)
        for key,image in catalog.items():
            source=originals[key]
            if key in plan['ordinaryAssemblies']:
                exact(image['role'],'Ordinary',path);exact(image['path'],'Ordinary/'+image['name']+'.dll',path)
                original=prior.read_identity(prior._rel(root,source['path'],path,'ordinary compiler DLL'))
                exact(image['assemblyIdentity'],original['fullName'],path)
                # Full ordinary semantic equivalence is independently replayed
                # by the byte-bound Editor generation verifier.
            else:
                pdb_path,pdb_sha=generation_source_pdb(source,path)
                for field,value in dict(role='Compiler' if key in compiled else 'Reference',path='Snapshot/'+source['path'],sourcePath=source['sourcePath'],sha256=source['sha256'],pdbSha256=pdb_sha,pdbPath=pdb_path).items():exact(image[field],value,path)
        for image in plan['images']:
            expected=copy.deepcopy(catalog[image['name'].casefold()]);expected['role']='Ordinary' if image['name'].casefold() in plan['ordinaryAssemblies'] else 'Shadow';exact(image,expected,path)
        startup=bound(row['executionPolicyPath'],row['executionPolicySha256'],path,'executionPolicyPath');verify_startup(startup,snapshot)
        aot_path=bound(row['aotInputPath'],row['aotInputSha256'],path,'aotInputPath');aot=read_canonical(aot_path,AOT_FIELDS,'inventoryHash','assembly-shadow-generation-aot:1')
        exact(aot['schemaVersion'],1,path);exact(aot['kind'],'GeneratorStripInputs',path);exact(aot['inventoryHash'],row['aotInventoryHash'],path)
        for key in ('planHash','target','architecture'):exact(aot[key],plan[key],path)
        # StripFresh verifies the Unity source and its post-strip copy before
        # capture. They are distinct mutable locations; only captured bytes are
        # reopened here, never a later plan's overwritten compiler cache.
        require(all(type(v) is str and Path(v).is_absolute() for v in (aot['sourceDirectory'],row['stripSourceDirectory'],row['stripOutput'])),f"{path}: missing strip-build source/output provenance")
        images=array(aot['images'],path);require(images,f"{path}: empty actual stripped AOT catalog");names([i['name'].casefold() for i in images],path)
        for image in images:
            verify_generation_image(image,aot_path.parent,path);exact(image['role'],'StrippedAot',path);exact(image['path'],'Assemblies/'+image['name']+'.dll',path)
            exact(Path(image['sourcePath']).parent,Path(aot['sourceDirectory']),path)
        exact({prior._rel(aot_path.parent,i['path'],path,'stripped AOT DLL') for i in images},set(aot_path.parent.rglob('*.dll')),path)
        exact(aot['excludedSelectedNames'],sorted(set(i['name'].casefold() for i in aot['images'])&set(i['name'].casefold() for i in plan['images'])),path)
        stage_outputs={}
        for stage,prefix in (('Link','link'),('MethodBridge','bridge'),('AotGenericReference','aot')):
            output_path=bound(row[prefix+'ReceiptPath'],row[prefix+'ReceiptSha256'],path,prefix+'ReceiptPath')
            output=verify_output(output_path,plan,aot,development,stage)
            expected_catalog=dict(catalog)
            if stage!='Link':expected_catalog.update({i['name'].casefold():i for i in aot['images'] if i['name'].casefold() not in aot['excludedSelectedNames']})
            exact(output['resolverCatalog'],sorted(expected_catalog.values(),key=lambda i:i['name']),path)
            stage_outputs[stage]=(output,output_path)
        emitted=stage_outputs['AotGenericReference'][0]['emittedAssemblyNames']
        exact(row['requiredAotMetadataNames'],sorted(n.removesuffix('.dll') for n in emitted if n.removesuffix('.dll').casefold() not in [c.casefold() for c in plan['closure']]),path)
        exact(row['stripBuildOptions'],536871041 if development else 536871040,path)
        prior._guid(row['stripBuildGuid'],path,'stripBuildGuid')
        plans[pid]=(row,plan,snapshot,plan_path);outputs[pid]=stage_outputs
    exact(proof['baselineCompileSnapshot'],plans['Ordinary'][0]['compileSnapshot'],path);exact(proof['baselineCompileSnapshotHash'],plans['Ordinary'][0]['compileSnapshotHash'],path)
    for pid in ('Ordinary','P01','P02','InitializerFailure'):verify_abi_coverage(outputs['P03']['MethodBridge'][0],outputs[pid]['MethodBridge'][0],path)
    slots=array(proof['installedOutputs'],path);exact(sorted(names([s['role'] for s in slots],path)),sorted(['Link','MethodBridge','AotGenericReference','AssemblyManifest','UnityVersion']),path)
    for slot in slots:
        fields(slot,'role sourcePath destinationPath sha256',path);file=bound(slot['sourcePath'],slot['sha256'],path,'installed source')
        require(Path(slot['destinationPath']).is_absolute(),f"{path}: missing installed destination provenance")
        if slot['role'] in outputs['P03']:
            output,receipt=outputs['P03'][slot['role']];exact(file,receipt.parent/output['outputPath'],path);exact(slot['sha256'],output['outputSha256'],path)
    return proof,plans


def witness(name):
    return ('AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness' if name==CONTRACTS_CONSUMER else
            'AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness' if name==EXTENSIBILITY_CONSUMER else name+'.M06ExecutionWitness')


def business_generic_type(name,image,path):
    require(name in CANDIDATES,f"{path}: generic type owner is not a registered candidate")
    identity=image['identity']
    if name==CONTRACTS:
        contracts_identity=identity['fullName']
    else:
        rows=[row for row in identity['referenceIdentities'] if row['name'].casefold()==CONTRACTS.casefold()]
        require(len(rows)==1,f"{path}: missing/ambiguous exact Contracts reference for generic type")
        contracts_identity=rows[0]['fullName']
    nested='GenericBox' if name==CONTRACTS else 'Pair'
    return witness(name)+'+'+nested+'`1[[AssemblyA.Contracts.DemoValue, '+contracts_identity+']]'


def compiler_core_identity(identity,providers,path):
    choices=[row for row in identity['referenceIdentities']
             if row['name'].casefold() in ('mscorlib','netstandard')]
    require(len(choices)==1,f"{path}: ambiguous/missing actual compiler corlib identity")
    core=choices[0];key=core['name'].casefold()
    require(key in providers,f"{path}: compiler corlib is absent from the verified compiler snapshot")
    exact(core['fullName'],providers[key]['fullName'],path)
    return core['fullName']


def runtime_warmup_aqn(identity,build,path):
    """Bind a declared compiler primitive to its exact runtime provider.

    The schema-2 warmup manifest intentionally preserves the compiler's
    byte-bound corlib reference. Unity 2022 IL2CPP can retarget that declared
    netstandard signature to the linked mscorlib implementation, and the
    runtime observation records Type.AssemblyQualifiedName after retargeting.
    Keep both proofs: verify_warmup validates the compiler identity, while this
    function requires the exact linked runtime identity from the Player receipt.
    """
    fields(identity,'assembly type',path)
    require(identity['assembly'].partition(',')[0].casefold() in ('mscorlib','netstandard'),
            f"{path}: warmup primitive has an unsupported compiler provider")
    rows=[row for row in build['player']['assemblyIdentities'] if row['name'].casefold()=='mscorlib']
    require(len(rows)==1,f"{path}: missing/ambiguous exact linked runtime corlib identity")
    return identity['type']+', '+rows[0]['fullName']


def verify_warmup(value,closure,cores,path):
    fields(value,'types methods',path)
    exact(value['types'],[dict(assembly=n,type=witness(n)) for n in closure],path)
    expected=[]
    for name in closure:
        require(name in cores,f"{path}: missing byte-bound compiler corlib for {name}")
        core=cores[name]
        for method,type_,arity in (('WarmupValue','System.Int32',0),('WarmupEcho','System.Int32',1),('WarmupEcho','System.String',1),('Run','System.String',0)):
            arg=dict(assembly=core,type=type_)
            expected.append(dict(assembly=name,declaringType=witness(name),name=method,isStatic=True,genericArity=arity,genericArguments=[arg] if arity else [],returnType=dict(assembly=core,type='System.String[]') if method=='Run' else arg,parameterTypes=[arg]))
    exact(value['methods'],expected,path)
    return value


def verify_patch(fixture,manifest,baseline,plan_tuple,path):
    fields(fixture,FIXTURE_FIELDS,path);pid=fixture['patchId'];row,plan,snapshot,plan_path=plan_tuple
    for field,other in (('compileSnapshot','compileSnapshot'),('compileSnapshotHash','compileSnapshotHash'),('generationPlanPath','planPath'),('generationPlanSha256','planSha256'),('defines','defines'),('changedRoots','changedRoots'),('closureLoadOrder','closureLoadOrder'),('requiredAotMetadataNames','requiredAotMetadataNames')):exact(fixture[field],row[other],path)
    exact(fixture['stableAotNames'],manifest['stableAotNames'],path);exact(fixture['developmentBuild'],manifest['developmentBuild'],path);exact(fixture['variant'],'Development' if manifest['developmentBuild'] else 'ReleaseNoPdb',path)
    root=canonical(fixture['patchDirectory'],path,'patchDirectory',True);patch_path=bound(fixture['patchManifest'],fixture['patchManifestSha256'],path,'patchManifest');exact(patch_path,root/'patch-manifest.json',path)
    exact((root/'manifest.sha256').read_text().strip(),digest(patch_path),path)
    envelope=obj(patch_path,'schemaVersion patch warmup');exact(envelope['schemaVersion'],2,path);patch=envelope['patch']
    r01_capability = r01_schema._schema_variant(patch, r01_schema.PATCH_FIELDS, r01_schema.R01_PATCH_FIELDS, path)
    exact(patch['schemaVersion'],1,path);exact(patch['semanticHashSchema'],1,path);exact(patch['patchId'],pid,path)
    for key in ('baselineBuildId','baselineManifestSha256','unityVersion','target','architecture','runtimeAbiHash'):exact(patch[key],manifest[key],path)
    exact(patch['compileSnapshotHash'],fixture['compileSnapshotHash'],path);prior._pins(patch['sourcePins'],path,baseline['sourcePins'])
    exact(patch['dllOnly'],True,path);exact(patch['unsigned'],True,path);exact(patch['signatureAlgorithm'],'None',path)
    exact(patch['loadOrder'],order_for(pid),path);exact(sorted(patch['changedRoots']),sorted(fixture['changedRoots']),path)
    for key,base in (('bootstrapAbiHash','bootstrapAbiHash'),('baselineResourceAbiHash','resourceAbiHash'),('resourceAbiHash','resourceAbiHash')):exact(patch[key],baseline[base],path)
    exact(patch['resourceBundlesRequired'],[],path)
    source={i['name']:i for i in snapshot['assemblies']};base={i['name']:i for i in baseline['assemblies']}
    exact(sorted(names([i['name'] for i in patch['closure']],path)),sorted(order_for(pid)),path)
    dlls=[];identities={}
    for item in patch['closure']:
        fields(item, r01_schema.R01_PATCH_ASSEMBLY_FIELDS if r01_capability else 'name dll sha256 semanticHash mvid baselineMvid pdb pdbSha256 references', path);name=item['name'];dll=prior._rel(root,item['dll'],path,'patch DLL');dlls.append(dll)
        actual=prior.read_identity(dll);identities[name]=actual
        for key in ('name','sha256','mvid'):exact(item[key],actual[key],path)
        exact(item['sha256'],source[name]['sha256'],path);exact(item['baselineMvid'],base[name]['mvid'],path)
        if r01_capability:
            require(type(item['dllSize']) is int and not isinstance(item['dllSize'], bool) and item['dllSize'] >= 0,
                    f"{path}: invalid R01 dllSize")
            exact(item['dllSize'],dll.stat().st_size,path)
        exact(sorted(canonical_names(item['references'],path)),
              sorted(canonical_names([r['name'] for r in actual['referenceIdentities']],path)),path)
        if manifest['developmentBuild']:
            pdb=prior._rel(root,item['pdb'],path,'patch PDB');exact(digest(pdb),item['pdbSha256'],path);exact(item['pdbSha256'],source[name]['pdbSha256'],path)
        else:require(item['pdb'] in ('',None) and item['pdbSha256'] in ('',None),f"{path}: release patch deploys PDB")
    exact(set(dlls),set(root.rglob('*.dll')),path)
    if not manifest['developmentBuild']:exact(list(root.rglob('*.pdb')),[],path)
    prior.verify_identities(fixture['assemblyIdentities'],dlls,path);types.verify_type_inventories(fixture['typeInventories'],fixture['assemblyIdentities'],path)
    edges=prior._edges(patch['dependencyGraph'],path);closure=prior._closure(edges,patch['changedRoots'],set(base),path)
    exact(closure,set(patch['loadOrder']),path);prior._verify_topological(patch['loadOrder'],closure,edges,path)
    reflection=prior._reflection_snapshot(Path(fixture['compileSnapshot']),snapshot,path);prior._reflection_manifest(patch,reflection,path)
    exact(types._artifact_tree(root/'RawTypeAdmissions'),types._artifact_tree(Path(fixture['compileSnapshot'])/'RawTypeAdmissions'),path)
    snapshot_root=Path(fixture['compileSnapshot']);providers={}
    for row in snapshot['references']+snapshot['assemblies']:
        key=row['name'].casefold()
        if key in ('mscorlib','netstandard'):
            require(key not in providers,f"{path}: duplicate compiler corlib provider")
            providers[key]=prior.read_identity(prior._rel(snapshot_root,row['path'],path,'compiler corlib DLL'))
    cores={name:compiler_core_identity(identities[name],providers,path) for name in patch['loadOrder']}
    verify_warmup(envelope['warmup'],patch['loadOrder'],cores,path)
    if r01_capability:
        r01_schema._verify_r01_patch_metadata(patch, patch['closure'], root, patch['loadOrder'], path)
    r01_schema.verify_budget_binding(patch,baseline,path)
    return dict(fixture=fixture,patch=patch,warmup=envelope['warmup'],root=root,snapshot=snapshot,r01Capability=r01_capability)


def verify_baseline(manifest,path,m01_root):
    baseline_path=bound(manifest['baselineManifestPath'],manifest['baselineManifestSha256'],path,'baselineManifestPath');baseline=obj(baseline_path)
    exact(baseline['schemaVersion'],1,path);exact(baseline['semanticHashSchema'],1,path)
    for key in ('baselineBuildId','runtimeAbiHash','unityVersion','target','architecture'):exact(baseline[key],manifest[key],path)
    prior._pins(baseline['sourcePins'],path);exact(prior._runtime_abi_hash(baseline['sourcePins'],path),manifest['runtimeAbiHash'],path)
    prior._name_set(baseline['shadowCandidates'],CANDIDATES,path,'shadowCandidates')
    prior._hash(baseline['bootstrapAbiHash'],path,'bootstrapAbiHash');prior._resource_abi_hash(baseline['resourceAbiHash'],path,'resourceAbiHash')
    descriptors=baseline['assemblies'];names([a['name'].casefold() for a in descriptors],path)
    for row in descriptors:
        actual=prior.read_identity(prior._rel(baseline_path.parent,row['filePath'],path,'frozen prelink DLL'))
        for key in ('name','mvid','sha256'):exact(actual[key],row[key],path)
    root=canonical(manifest['baselineInputSnapshot'],path,'baselineInputSnapshot',True)
    snapshot=prior._verify_snapshot(root,manifest['baselineBuildId'],manifest['runtimeAbiHash'],baseline,path)
    prior._snapshot_files(snapshot,root,path);prior._verify_linked_player(root,snapshot,{a['name']:a for a in descriptors},path)
    reflection=prior._reflection_snapshot(root,snapshot,path,require_linked=True);prior._reflection_manifest(baseline,reflection,path);raw.verify_snapshot(root,snapshot,require_linked=True)
    frozen_root=canonical(str(baseline_path.parent/baseline['playerInputSnapshot']),path,'frozen Player inputs',True)
    frozen=prior._verify_snapshot(frozen_root,manifest['baselineBuildId'],manifest['runtimeAbiHash'],baseline,path)
    prior._snapshot_files(frozen,frozen_root,path);raw.verify_snapshot(frozen_root,frozen,require_linked=True)
    exact(snapshot,frozen,path);exact(manifest['baselineInputSnapshotHash'],snapshot['snapshotHash'],path)
    prior._verify_bundles(Path(m01_root),baseline,path)
    resource=prior._verify_resource_baseline(baseline_path.parent,baseline,path,Path(m01_root))
    exact(resource['provenance'],'M01AuditedFrozenSourceReconstruction',path);exact(resource['compilerSnapshotHash'],snapshot['snapshotHash'],path)
    lines=manifest['stableAotProvenance'].split('\n');exact([s.partition('=')[0] for s in lines],['framework','compiler-libraries','linked-player','bootstrap-policy','physical'],path)
    for line in lines[:2]:prior._hash(line.partition('=')[2],path,'compiler proof hash')
    exact(lines[2],'linked-player='+snapshot['linkedPlayerReceiptHash'],path)
    exact(lines[3],'bootstrap-policy='+','.join(sorted(n.casefold() for n in baseline['bootstrapAssemblies'])),path)
    exact(lines[4],'physical='+','.join(manifest['stableAotNames']),path)
    require({n.casefold() for n in manifest['stableAotNames']} <= {i['name'].casefold() for i in snapshot['linkedPlayerReceipt']['assemblies']},f"{path}: stable provider absent from linked bytes")
    return baseline,snapshot


def verify_inputs(path,m01_root,development):
    path=canonical(str(path),path,'fixtureManifest');manifest=obj(path,MANIFEST_FIELDS)
    exact(manifest['schemaVersion'],1,path);exact(manifest['milestone'],'M06',path);exact(manifest['developmentBuild'],development,path)
    require(re.fullmatch(r'M06-Baseline-[A-Za-z0-9_.-]+',manifest['baselineBuildId']),f"{path}: non-M06 baseline")
    exact((manifest['unityVersion'],manifest['target'],manifest['architecture']),('2022.3.62f2','StandaloneOSX','arm64'),path)
    exact(manifest['candidateNames'],list(CANDIDATES),path);exact(manifest['closureLoadOrder'],list(ORDER),path)
    stable=names(manifest['stableAotNames'],path);require(stable==sorted(stable) and stable and not set(n.casefold() for n in stable)&set(n.casefold() for n in CANDIDATES),f"{path}: invalid stable providers")
    exact(manifest['stableAotProvenanceHash'],hashlib.sha256(('m06-stable-aot:1\n'+manifest['stableAotProvenance']).encode()).hexdigest(),path)
    baseline,snapshot=verify_baseline(manifest,path,m01_root)
    generation_path=bound(manifest['generationProofPath'],manifest['generationProofSha256'],path,'generationProofPath')
    generation,plans=verify_generation(generation_path,baseline,development)
    exact([r['patchId'] for r in array(manifest['fixtures'],path)],['P01','P02','P03'],path)
    exact(manifest['initializerFailureFixture']['patchId'],'InitializerFailure',path)
    fixtures={}
    for fixture in manifest['fixtures']+[manifest['initializerFailureFixture']]:
        fixtures[fixture['patchId']]=verify_patch(fixture,manifest,baseline,plans[fixture['patchId']],path)
        exact(raw.control_hash(fixtures[fixture['patchId']]['snapshot']['extraScriptingDefines'],path),raw.control_hash(snapshot['extraScriptingDefines'],path),path)
    return dict(manifest=manifest,path=path,baseline=baseline,snapshot=snapshot,generation=generation,plans=plans,fixtures=fixtures)


def verify_schema_rows(rows,modules,resolver,path,r01_capability=False):
    seen=set();actual_rows=[]
    for row in array(rows,path):
        fields(row,'side assemblyName assemblyIdentity typeName typeAttributes isSerializable fields',path)
        key=(row['side'],row['assemblyName'],row['typeName']);require(key not in seen,f"{path}: duplicate schema row");seen.add(key)
        require((row['side'],row['assemblyName']) in modules,f"{path}: schema side/assembly not captured")
        module=modules[row['side'],row['assemblyName']];exact(row['assemblyIdentity'],module.identity['fullName'],path)
        matches=[rid for rid,name in module.type_names.items() if name==row['typeName']];require(len(matches)==1,f"{path}: missing schema TypeDef")
        flags=module.tables.row(2,matches[0])[0];exact(row['typeAttributes'],flags,path);exact(row['isSerializable'],bool(flags&0x2000),path);exact(row['isSerializable'],True,path)
        exact(row['fields'],schema_fields(module,row['typeName'],resolver),path)
        actual_rows.append(row)
    for side in ('PlayerInput','LinkedPlayer'):
        for name,expected in (('HybridCLR.AssemblyShadowExecutionDiagnostics',14),('HybridCLR.AssemblyShadowExecutionClassInfo',12)):
            rows_=[r for r in actual_rows if r['side']==side and r['typeName']==name]
            require(len(rows_)==1 and len(rows_[0]['fields'])==expected,f"{path}: missing exact execution 14/12 schema")
        pending=[('AssemblyShadowDemo.Bootstrap','AssemblyShadowDemo.M06ExecutionProbe/'+name) for name in 'Result FixtureManifest PlayerBuildReceipt TypeProof ExecutionProof GenerationProof ExecutionPolicyProof PatchManifestVersion PatchManifestEnvelope PatchManifest BaselineManifest SnapshotReceipt GenerationPlan CompilerModeProof GenerationOutput AotInputProof LinkedPlayerReceipt'.split()]
        pending += [('AssemblyShadowDemo.Bootstrap','AssemblyShadowDemo.M04OrdinaryAssemblyProbe/'+name) for name in ('Configuration','Site')]
        pending += [('HybridCLR.Runtime',name) for name in ('HybridCLR.AssemblyShadowDiagnostics','HybridCLR.AssemblyShadowTypeResolutionInfo','HybridCLR.AssemblyShadowExecutionDiagnostics','HybridCLR.AssemblyShadowExecutionClassInfo')]
        if r01_capability:
            pending += [('HybridCLR.Runtime',name) for name in ('HybridCLR.AssemblyShadowMetadataCapacity','HybridCLR.AssemblyShadowMetadataAllocation','HybridCLR.AssemblyShadowRecoveryInfo')]
        required=set()
        while pending:
            assembly,type_name=pending.pop()
            if (assembly,type_name) in required:continue
            required.add((assembly,type_name));module=modules[side,assembly]
            owner=next((rid for rid,name in module.type_names.items() if name==type_name),None)
            require(owner is not None,f"{path}: missing actual required DTO {type_name}")
            for rid,type_rid in module.field_owners.items():
                if owner!=type_rid:continue
                attr,_,blob=module.tables.row(4,rid)
                if attr&7!=6 or attr&0x10 or attr&0x80:continue
                from m05_types import Signature
                sig=Signature(module.tables.blob(blob),path);require(sig.byte()==6,f"{path}: invalid DTO field")
                while sig.position<len(sig.data) and sig.data[sig.position]==29:sig.byte()
                child=module.shape(sig)
                if child.arguments:
                    require(child.full.startswith('System.Collections.Generic.List`1<') and len(child.arguments)==1,f"{path}: unsupported DTO collection")
                    child=child.arguments[0]
                target=child.assembly.partition(',')[0]
                if (side,target) in modules:
                    exact(child.assembly,modules[side,target].identity['fullName'],path);pending.append((target,child.full))
                else:require(child.full in DTO_PRIMITIVES,f"{path}: unsupported DTO primitive/owner {child.full}")
        exact({(r['assemblyName'],r['typeName']) for r in actual_rows if r['side']==side},required,path)
    resolver.verify_unchanged()
    return actual_rows


def verify_execution_proof(player,snapshot,context,path):
    proof_path=bound(player['executionProofPath'],player['executionProofSha256'],path,'executionProofPath');proof=obj(proof_path,EXECUTION_FIELDS)
    exact(proof_path,Path(player['inputSnapshot'])/'m06-execution-proof.json',path);exact(proof['schemaVersion'],1,path);exact(proof['milestone'],'M06',path);exact(proof['policy'],'execution-world:1',path)
    for key in ('buildGuid','nativeLibrarySha256','developmentBuild','generationProofPath','generationProofSha256','typeProofPath','typeProofSha256'):exact(proof[key],player[key],path)
    exact(proof['compileSnapshotHash'],snapshot['snapshotHash'],path);exact(proof['linkedPlayerReceiptHash'],snapshot['linkedPlayerReceiptHash'],path)
    legacy_api=['HybridCLR.AssemblyShadowErrorCode HybridCLR.AssemblyShadowRuntime::'+n for n in LEGACY_API_NAMES]
    negotiated_api=['HybridCLR.AssemblyShadowErrorCode HybridCLR.AssemblyShadowRuntime::'+n for n in NEGOTIATED_API_NAMES]
    if proof['apiSignatures'] == legacy_api:
        r01_capability=False; expected_api=legacy_api; expected_errors=LEGACY_ERROR_NAMES
    elif proof['apiSignatures'] == legacy_api + negotiated_api:
        r01_capability=True; expected_api=legacy_api + negotiated_api; expected_errors=NEGOTIATED_ERROR_NAMES
    else:
        require(False,f"{path}: unsupported execution API capability schema")
    for item in context['fixtures'].values():
        exact(item.get('r01Capability',False),r01_capability,f'{path}: patch/execution-proof capability')
    exact(proof['apiSignatures'],expected_api,path)
    exact(proof['errorCodes'],[dict(name=name,value=i) for i,name in enumerate(expected_errors)],path)
    type_path=bound(player['typeProofPath'],player['typeProofSha256'],path,'typeProofPath');type_proof=obj(type_path,types.PROOF_FIELDS)
    exact(type_path,Path(player['inputSnapshot'])/'m06-type-proof.json',path);exact(type_proof['schemaVersion'],1,path);exact(type_proof['milestone'],'M06',path);exact(type_proof['policy'],'active-execution-types:1',path)
    for key in ('compileSnapshotHash','linkedPlayerReceiptHash','nativeLibrarySha256','buildGuid','developmentBuild'):exact(type_proof[key],proof[key],path)
    types.verify_type_inventories(type_proof['assemblies'],player['assemblyIdentities'],path)
    core=next(i for i in player['assemblyIdentities'] if i['name']=='mscorlib');exact(type_proof['moduleMethods'],types.read_method_witnesses(core['path']),path)
    root=Path(player['inputSnapshot']);modules={}
    for side in ('PlayerInput','LinkedPlayer'):
        files=snapshot['assemblies'] if side=='PlayerInput' else snapshot['linkedPlayerReceipt']['assemblies'];directory=root if side=='PlayerInput' else root/'LinkedPlayer'
        for name in ('AssemblyShadowDemo.Bootstrap','HybridCLR.Runtime'):
            file=named(files,name,path);dll=prior._rel(directory,file['path'],path,'schema DLL');modules[side,name]=ExecutionMetadata(dll.read_bytes(),dll)
            exact(modules[side,name].identity['name'],name,path)
        runtime=modules[side,'HybridCLR.Runtime'];actual_api=[]
        for rid,owner in runtime.method_owners.items():
            if runtime.type_names[owner]!='HybridCLR.AssemblyShadowRuntime':continue
            row=runtime.tables.row(6,rid)
            if row[2]&7==6 and row[2]&16:actual_api.append(runtime.member_shape(6,rid)[1])
        exact(sorted(actual_api),sorted(proof['apiSignatures']),path)
        enum_owner=next(rid for rid,name in runtime.type_names.items() if name=='HybridCLR.AssemblyShadowErrorCode');constants={}
        for rid in range(1,runtime.tables.counts[11]+1):
            element,parent,blob=runtime.tables.row(11,rid);table,field=runtime.tables.coded(parent,'HasConstant')
            if table!=4 or runtime.field_owners[field]!=enum_owner:continue
            require(element&255==8 and len(runtime.tables.blob(blob))==4,f"{path}: error enum constant is not Int32")
            name=runtime.tables.string(runtime.tables.row(4,field)[1]);require(name not in constants,f"{path}: duplicate enum constant")
            constants[name]=int.from_bytes(runtime.tables.blob(blob),'little',signed=True)
        exact(constants,{name:i for i,name in enumerate(expected_errors)},path)
        expected_root={key:'System.UInt64' for key in EXEC_COUNTERS.split()};expected_root.update({key:'System.Int32' for key in EXEC_INTS.split()});expected_root.update(enabled='System.Boolean',state='System.String',classes='HybridCLR.AssemblyShadowExecutionClassInfo[]')
        expected_class={key:'System.String' for key in CLASS_STRINGS.split()};expected_class.update({key:'System.Boolean' for key in CLASS_BOOLS.split()});expected_class['executionModeCode']='System.Int32'
        for name,expected in (('HybridCLR.AssemblyShadowExecutionDiagnostics',expected_root),('HybridCLR.AssemblyShadowExecutionClassInfo',expected_class)):
            actual_fields=[f for f in runtime.fields(name) if f['flags']&7==6 and not f['flags']&16]
            exact({f['name']:f['type'] for f in actual_fields},expected,path)
    resolver=LinkedSchemaResolver({i['fullName']:i['path'] for i in player['assemblyIdentities']})
    verify_schema_rows(proof['schemaTypes'],modules,resolver,path,r01_capability)
    expected=[]
    for role in ('PlayerInput','LinkedPlayer'):
        files=snapshot['assemblies'] if role=='PlayerInput' else snapshot['linkedPlayerReceipt']['assemblies'];directory=root if role=='PlayerInput' else root/'LinkedPlayer'
        for name in CANDIDATES:
            file=named(files,name,path)
            expected.append((role,'',snapshot['snapshotHash'],'',name,prior._rel(directory,file['path'],path,'candidate DLL'),prior._rel(directory,file['pdbPath'],path,'candidate PDB') if file['pdbPath'] else None))
    for pid in sorted(context['plans']):
        row,plan,_,plan_path=context['plans'][pid]
        for name in plan['loadOrder']:
            file=next(i for i in plan['images'] if i['name']==name)
            expected.append(('GenerationPlan',pid,row['compileSnapshotHash'],row['planHash'],name,prior._rel(plan_path.parent,file['path'],path,'plan DLL'),prior._rel(plan_path.parent,file['pdbPath'],path,'plan PDB') if file['pdbPath'] else None))
    images=array(proof['images'],path);exact(len(images),len(expected),path);lookup={}
    for image,(role,pid,snapshot_hash,plan_hash,name,dll,pdb) in zip(images,expected):
        fields(image,EXECUTION_IMAGE_FIELDS,path)
        for key,value in dict(role=role,planId=pid,compileSnapshotHash=snapshot_hash,planHash=plan_hash,pdbPath=str(pdb) if pdb else '',pdbSha256=digest(pdb) if pdb else '',pdbAvailable=pdb is not None).items():exact(image[key],value,path)
        prior.verify_identities([image['identity']],[dll],path)
        actual_methods=read_methods(dll,pdb);exact(image['methods'],actual_methods,f"{path}: {role}/{pid}/{name} methods")
        lookup[role,pid,name]=image
    return proof,lookup


def verify_player(path,context,native_enabled,development):
    path=canonical(str(path),path,'playerBuildReceipt');player=obj(path,PLAYER_FIELDS);manifest=context['manifest'];baseline=context['baseline']
    exact(player['schemaVersion'],1,path);exact(player['milestone'],'M06',path);exact(player['variant'],'NativeOn' if native_enabled else 'NativeOff',path);exact(player['developmentBuild'],development,path)
    for key in ('baselineBuildId','runtimeAbiHash','unityVersion','target','architecture'):exact(player[key],manifest[key],path)
    exact(player['nativeArguments'],'--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+('1' if native_enabled else '0')+'"',path)
    root=canonical(player['inputSnapshot'],path,'inputSnapshot',True);exact(path,root/'m06-player-build.json',path)
    snapshot=prior._verify_snapshot(root,manifest['baselineBuildId'],manifest['runtimeAbiHash'],baseline,path,native_enabled)
    for key,source in (('inputSnapshotHash','snapshotHash'),('buildGuid','buildGuid'),('playerOutput','playerOutput'),('nativeLibraryPath','nativeLibraryPath'),('nativeLibrarySha256','nativeLibrarySha256'),('buildOptions','playerBuildOptions')):exact(player[key],snapshot[source],path)
    exact(player['buildOptions'],536870912|128|(1 if development else 0),path)
    output=canonical(player['playerOutput'],path,'playerOutput',True);library=bound(player['nativeLibraryPath'],player['nativeLibrarySha256'],path,'nativeLibraryPath');require(library.is_relative_to(output),f"{path}: native binary outside Player")
    prior._snapshot_files(snapshot,root,path);prior._verify_linked_player(root,snapshot,{a['name']:a for a in baseline['assemblies']},path);prior._reflection_snapshot(root,snapshot,path,require_linked=True);raw.verify_snapshot(root,snapshot,require_linked=True)
    exact(raw.control_hash(snapshot['extraScriptingDefines'],path),raw.control_hash(context['snapshot']['extraScriptingDefines'],path),path)
    linked=snapshot['linkedPlayerReceipt']['assemblies'];prior.verify_identities(player['assemblyIdentities'],[prior._rel(root/'LinkedPlayer',i['path'],path,'linked DLL') for i in linked],path)
    prior._verify_native_metadata(player,path)
    placeholder=bound(player['placeholderManifestPath'],player['placeholderManifestSha256'],path,'placeholderManifestPath');exact(placeholder,root/'m06-placeholder-AssemblyManifest.cpp',path);exact(player['placeholderAssemblyNames'],prior.parse_placeholders(placeholder.read_bytes(),path),path)
    exact(player['generationProofPath'],manifest['generationProofPath'],path);exact(player['generationProofSha256'],manifest['generationProofSha256'],path)
    for row in array(player['supplementaryMetadataInputs'],path):
        fields(row,'assemblyName path sha256 identity',path);dll=bound(row['path'],row['sha256'],path,'supplementary metadata');prior.verify_identities([row['identity']],[dll],path)
        actual=next(i for i in player['assemblyIdentities'] if i['name']==row['assemblyName']);exact(row['identity'],actual,path)
    proof,images=verify_execution_proof(player,snapshot,context,path)
    return dict(player=player,path=path,snapshot=snapshot,proof=proof,images=images)


def managed_player_inputs(snapshot,path):
    """Project a Player snapshot onto the byte-bound managed build inputs.

    Native-ON and native-OFF builds must differ in their native identity, while
    this projection must remain exactly equal. Native build GUIDs, outputs,
    binary hashes and linked reflection receipts are deliberately excluded.
    """
    root_keys=("schemaVersion","kind","unityVersion","target","architecture","buildId",
               "playerBuildSucceeded","playerBuildFilterCaptured","playerBuildOptions",
               "normalHotUpdateAssemblies","extraScriptingDefines","sourcePins","assemblies",
               "references","filteredAssemblies","filteredAssemblyCapabilities",
               "linkerExcludedAssemblies","linkerExcludedAssemblyCapabilities")
    linked_keys=("schemaVersion","target","architecture","sourceDirectory","protectedAssemblies","assemblies")
    require(type(snapshot) is dict and all(key in snapshot for key in root_keys) and
            type(snapshot.get("linkedPlayerReceipt")) is dict and
            all(key in snapshot["linkedPlayerReceipt"] for key in linked_keys),
            f"{path}: incomplete managed Player input projection")
    projection={key:copy.deepcopy(snapshot[key]) for key in root_keys}
    projection["linkedPlayerReceipt"]={key:copy.deepcopy(snapshot["linkedPlayerReceipt"][key]) for key in linked_keys}
    return projection


def values_map(values,path):
    result={}
    for value in array(values,path):
        require(type(value) is str and '=' in value,f"{path}: malformed business value")
        key,_,body=value.partition('=');require(key and key not in result,f"{path}: duplicate business value {key}");result[key]=body
    return result


def numeric_string(value,path,minimum=0):
    require(type(value) is str and re.fullmatch(r'-?(0|[1-9][0-9]*)',value),f"{path}: noncanonical integer string")
    require(str(int(value))==value,f"{path}: noncanonical signed zero")
    return integer(int(value),path,minimum,(1<<63)-1)


def literal_values(image,method_name=None):
    values=[]
    for method in image['methods']:
        if method_name and method['name']!=method_name:continue
        for line in method['instructions']:
            if ':ldstr utf8:' in line:values.append(base64.b64decode(line.split(' utf8:',1)[1],validate=True).decode())
    return values


def physical_marker(image,path):
    markers={s.removeprefix('marker=') for s in literal_values(image,'NewObservations') if s.startswith('marker=M06-')}
    require(len(markers)==1,f"{path}: actual business marker absent/ambiguous")
    methods=[m for m in image['methods'] if m['name']=='WarmupValue' and m['declaringType']==witness(image['identity']['name'])]
    require(len(methods)==1,f"{path}: missing byte-bound WarmupValue")
    constants=[]
    for line in methods[0]['instructions']:
        match=re.fullmatch(r'[0-9]+:ldc\.i4(?:\.s)? System\.(?:Int32|SByte):(-?[0-9]+)',line)
        if match:constants.append(int(match[1]))
    require(len(constants)==1 and any(line.endswith(':add') for line in methods[0]['instructions']),f"{path}: unsupported frozen generation computation")
    return markers.pop(),constants[0]


def verify_business(values,name,phase,image,path,invocation=0,first=None,provider_image=None):
    observed=values_map(values,path);marker,generation=physical_marker(image,path)
    expected={};expected['phase']=phase
    if phase=='new':
        offset={CONTRACTS:10,EXTENSIBILITY:20,INTERNAL:30,CONTRACTS_CONSUMER:40,EXTENSIBILITY_CONSUMER:50}[name]
        expected.update(marker=marker,ctor=str(generation+offset),field=marker+':field',interface=marker+':interface',event=marker+':event:1')
        expected.update({'ctor.first':str(generation+offset),'ctor.second':str(generation+offset),'ctor.count':'2','helper.count':'2'})
        if name in (CONTRACTS,EXTENSIBILITY,INTERNAL):expected['property']=marker+':property'
        if name in (CONTRACTS,CONTRACTS_CONSUMER):expected['default.ctor']=str(generation+99)
        if name in (CONTRACTS_CONSUMER,EXTENSIBILITY_CONSUMER):expected['contract']='M01'
        if name in (EXTENSIBILITY,INTERNAL,EXTENSIBILITY_CONSUMER):
            expected.update({'base.field':'M06-BASE-FIELD','base.property':'M06-BASE-PROPERTY','base.event':'M06-BASE-EVENT'})
            if name in (INTERNAL,EXTENSIBILITY_CONSUMER):expected['base']=marker+(':base:M06-BASE-VIRTUAL' if name==INTERNAL else ':base')
    elif phase=='statics':
        expected.update(marker=marker,cctor='1')
        expected.update({'generic.int':str(invocation*2+1),'generic.string':str(invocation*2+1),'generic.int.repeat':str(invocation*2+2),'generic.string.repeat':str(invocation*2+2),
                         'explicit.value':str(invocation+2),'explicit.type':witness(name)+'+ExplicitStaticState','beforefieldinit.flag':'True','beforefieldinit.count':'2'})
        a=numeric_string(observed.get('beforefieldinit.int.first'),path);b=numeric_string(observed.get('beforefieldinit.string.first'),path)
        exact(sorted((a-generation-5,b-generation-6)),[1,2],path)
        for key,value in (('int',a),('string',b)):
            expected['beforefieldinit.'+key+'.first']=str(value);expected['beforefieldinit.'+key+'.repeat']=str(value)
            if first is not None:exact(str(value),values_map(first,path)['beforefieldinit.'+key+'.first'],path)
    elif phase=='dispatch':
        expected.update(virtual=marker+(':virtual' if name in (CONTRACTS,CONTRACTS_CONSUMER) else ':sealed'),interface=marker+':interface',base=marker+(':base:M06-BASE-VIRTUAL' if name in (INTERNAL,EXTENSIBILITY) else ':base'))
        if name==CONTRACTS:expected.update(index=marker+':index2');expected['contract.interface']=marker+':contract'
        if name in (INTERNAL,EXTENSIBILITY,EXTENSIBILITY_CONSUMER):expected.update(abstract=marker+':abstract',assignable='True')
        if name in (INTERNAL,EXTENSIBILITY):expected['contract']='M01'
        if name==EXTENSIBILITY_CONSUMER:expected['ext']=str(physical_marker(provider_image,path)[1]+2)
    elif phase=='delegates':
        expected.update(instance=marker+':I2',static=marker+':S2',closed=marker+':I3',multicast=marker+(':I2' if name==CONTRACTS else ':S2'))
        if name==CONTRACTS:expected['contract.delegate']=marker+':I2'
        expected.update({'invocation.count':'2','handler.first':'2','handler.second':'1','event.beforeRemove':'2','event.afterRemove':'2','event.removed':'True'})
    elif phase=='generics':
        expected.update({'generic.value':'4','method':marker,'nullable':'4','boxed':'4','generic.method':'6','array':'2','ref':str((generation if name==INTERNAL else 0)+6),'out':str((generation if name==INTERNAL else 0)+7)})
        expected['generic.type']=business_generic_type(name,image,path)
        if name==INTERNAL:expected['struct']=str(generation+4)
    elif phase=='async':
        expected={'cancel':'TaskCanceledException','async.throw':marker+':async','iterator.begin':'true','iterator.moveNext':'True','iterator.value':str(generation),'iterator.finally':'true','iterator.disposed':'true','async':'sync-boundary','marker':marker}
    elif phase=='coroutine':
        expected={'coroutine.begin':marker,'coroutine.continuation':str(generation+1),'driver.disposed':'true'}
        for key in ('driver.yields','driver.frameDelta'):expected[key]=str(numeric_string(observed.get(key),path,1))
    else:raise VerificationError(f"{path}: unsupported business phase")
    exact(observed,expected,path)
    if first is not None and phase!='statics':exact(values,first,path)
    return observed


def verify_exception(values,image,path,shadow,development):
    data=values_map(values,path);marker,_=physical_marker(image,path)
    for key,value in dict(phase='exceptions',filter=marker,finally_='ran',wrapped='InvalidOperationException').items():exact(data.get('finally' if key=='finally_' else key),value,path)
    require(type(data.get('stack.text')) is str and data['stack.text'],f"{path}: empty exception stack")
    numeric_string(data.get('stack.frames'),path,1)
    token=numeric_string(data.get('method.token'),path,1)
    throwing=[m for m in image['methods'] if m['metadataToken']==token]
    require(len(throwing)==1 and throwing[0]['name']=='ThrowForEvidence' and throwing[0]['declaringType']==witness(image['identity']['name']),f"{path}: exception method token not in selected physical DLL")
    frame_ids=sorted({int(match[1]) for key in data for match in [re.fullmatch(r'frame\.([0-9]+)\.declaringType',key)] if match})
    exact(frame_ids,list(range(len(frame_ids))),path);require(frame_ids,f"{path}: missing stack frame observations")
    allowed={'phase','filter','finally','wrapped','stack.text','stack.frames','method.token','source.status'};found=False;source=False;any_source=False
    for index in frame_ids:
        prefix=f'frame.{index}.';allowed.update(prefix+k for k in ('declaringType','method','methodAvailable','token','file','line','column'))
        available=data.get(prefix+'methodAvailable');require(available in ('True','False'),f"{path}: missing actual StackFrame method availability")
        frame_token=numeric_string(data.get(prefix+'token'),path);line=numeric_string(data.get(prefix+'line'),path);numeric_string(data.get(prefix+'column'),path)
        file=data.get(prefix+'file');require(type(file) is str and file,f"{path}: missing frame file observation")
        any_source |= file!='absent'
        if available=='False':
            exact(data[prefix+'declaringType'],'absent',path);exact(data[prefix+'method'],'absent',path);exact(frame_token,0,path)
        if available=='True' and data[prefix+'declaringType']==witness(image['identity']['name']):
            matches=[m for m in image['methods'] if m['metadataToken']==frame_token and m['name']==data[prefix+'method'] and m['declaringType']==data[prefix+'declaringType']]
            require(len(matches)==1 and matches[0]['hasBody'],f"{path}: stack frame has no actual physical method")
            found |= matches[0]['name'] in ('ThrowNested','ThrowForEvidence')
            if file!='absent' and line>0:
                if shadow:require(image['pdbAvailable'] and any(p['document']==file and p['startLine']<=line<=p['endLine'] for p in matches[0]['sequencePoints']),f"{path}: patch source line not in actual portable PDB")
                source=True
    exact(set(data),allowed,path);require(found,f"{path}: throwing witness missing from stack")
    exact(data['source.status'],'available' if any_source else 'absent',path)
    if shadow:require(source if development else not source,f"{path}: wrong Development/PDB vs release/no-PDB source evidence")


def verify_result_header(path,context,build):
    result=obj(path);player=build['player'];manifest=context['manifest']
    capability=r01_schema._schema_variant(result,RESULT_FIELDS,R01_RESULT_FIELDS,path)
    proof=build.get('proof', {})
    expected_capability=any('::ReserveMetadataBudget(' in signature for signature in proof.get('apiSignatures', []))
    exact(capability,expected_capability,f"{path}: result/execution-proof capability")
    if capability:integer(result['reserveCode'],path)
    for key in RESULT_INTS.split():integer(result[key],path)
    for key in RESULT_STRINGS.split():require(type(result[key]) is str,f"{path}: missing string/default {key}")
    for key in ('il2cpp','developmentBuild','businessLaunched'):boolean(result[key],path)
    for key in RESULT_ARRAYS.split():array(result[key],path)
    exact(result['schemaVersion'],1,path);exact(result['milestone'],'M06',path);exact(result['result'],'Passed',path);exact(result['error'],'',path);exact(result['il2cpp'],True,path)
    require(result['mode'] in MODES,f"{path}: unknown M06 case");integer(result['processId'],path,1)
    for key in ('unityVersion','buildGuid','baselineBuildId','runtimeAbiHash','variant','developmentBuild','generationProofPath','generationProofSha256','executionProofPath','executionProofSha256'):exact(result[key],player[key],path)
    exact(result['platform'],'OSXPlayer',path);exact(result['moduleMvidObservationPolicy'],prior.MVID_POLICY,path)
    require(canonical(result['playerDataPath'],path,'playerDataPath',True).is_relative_to(Path(player['playerOutput'])),f"{path}: actual Player path differs")
    exact(result['fixtureManifestPath'],str(context['path']),path);exact(result['fixtureManifestSha256'],digest(context['path']),path)
    exact(result['playerBuildReceiptPath'],str(build['path']),path);exact(result['playerBuildReceiptSha256'],digest(build['path']),path)
    for prefix,raw_key in (('rawTransaction','nativeDiagnosticsJson'),('rawExecution','executionDiagnosticsJson')):
        file_path=result[prefix+'DiagnosticsPath'];sha=result[prefix+'DiagnosticsSha256'];text=result[raw_key]
        if text:
            file=bound(file_path,sha,path,prefix+'DiagnosticsPath');exact(file.parent,Path(path).parent,path);exact(file.read_text(),text,path)
        else:exact(file_path,'',path);exact(sha,'',path)
    return result


def business_phases(mode):
    if mode.startswith(('T06-10-','T06-12-')):return ['new','dispatch','generics']
    return [next((word for prefix,word in (('T06-01-','new'),('T06-02-','statics'),('T06-06-','delegates'),('T06-07-','generics'),('T06-08-','async')) if mode.startswith(prefix)),'dispatch')]


def execution_layout(mode,closure):
    """Exact emitted observation order; counter endpoints index real snapshots.

    Repeated generic method names deliberately remain repeated rows. A map keyed
    by phase would silently discard WarmupEcho<int>/WarmupEcho<string> evidence.
    """
    if mode=='T06-09-BaselineRecovery':return ['baseline-recovery'],[]
    if mode=='T06-11-FeatureOff':return [],[]
    phases=['initial'];timings=[]
    def snapshot(phase):phases.append(phase);return len(phases)-1
    def timing(phase,before,after):timings.append((phase,before,after))
    for phase in ('configure','begin','stage','validate','commit'):
        before=snapshot(phase+'-before');after=snapshot(phase+'-after');timing(phase,before,after)
    if mode=='T06-09-InitializerFailure':snapshot('initializer-failure');return phases,timings
    committed=snapshot('committed')
    if mode.startswith('T06-10-'):
        for name in closure:snapshot('warmup-type-'+name)
        for name in closure:
            for method in ('WarmupValue','WarmupEcho','WarmupEcho','Run'):snapshot('warmup-method-'+name+'-'+method)
        prejit=len(phases)-1;timing('prejit',committed,prejit)
        for name in closure:
            snapshot('module-warmup-before-'+name)
            for method in ('WarmupValue','WarmupEcho','WarmupEcho'):
                snapshot('warmup-call-before-'+name+'-'+method);snapshot('warmup-call-after-'+name+'-'+method)
            snapshot('module-warmup-after-'+name)
        timing('module-warmup',prejit,len(phases)-1);after=snapshot('warmup');timing('warmup',committed,after)
    business=snapshot('business-before')
    for name in CANDIDATES:
        for phase in business_phases(mode):
            for invocation in range(2):
                boundary=name+'-'+phase+'-'+str(invocation)
                before=snapshot(boundary+'-before');after=snapshot(boundary+'-after')
                timing('first' if invocation==0 else 'second',before,after)
                if phase in ('dispatch','generics'):timing('virtual' if phase=='dispatch' else 'generic',before,after)
    after=snapshot('business-after');timing('business',business,after);snapshot('final')
    return phases,timings


def verify_checks(result,closure,path):
    expected=[]
    def check(name,code,actual):expected.append(dict(name=name,actualCode=code,expectedCode=code,actual=actual,expected=actual))
    mode=result['mode']
    if mode=='T06-11-FeatureOff':
        for api,value in (('GetState','Disabled'),('GetAssemblyExecutionMode','AotBaseline'),('GetTypeResolutionInfo','')):check(api+':disabled',1,value)
    elif mode=='T06-09-BaselineRecovery':
        check('GetState:baseline-recovery',0,'Disabled');check('GetAssemblyExecutionMode:recovery',4,'AotBaseline')
        check('GetAssemblyExecutionMode:baseline-recovery:'+INTERNAL,4,'AotBaseline');check('GetTypeResolutionInfo:'+witness(INTERNAL),0,'')
    else:
        check('GetState:initial',0,'Disabled');check('GetState:staging',0,'Staging')
        failure=mode=='T06-09-InitializerFailure'
        check('GetState:initializer-failure' if failure else 'GetState:committed',0,'FailedAfterCommit' if failure else 'Committed')
        if not failure:
            for name in CANDIDATES:
                world='InterpreterShadow' if name in closure else 'AotBaseline'
                check('GetAssemblyExecutionMode:'+name,0,world);check('GetTypeResolutionInfo:'+witness(name),0,'')
                phases=['mode']+[p for phase in business_phases(mode) for p in (phase,'second-'+phase)]+['exceptions']
                if business_phases(mode)==['async']:phases.append('coroutine')
                for phase in phases:
                    check('GetAssemblyExecutionMode:'+phase+':'+name,0,world);check('GetTypeResolutionInfo:'+witness(name),0,'')
    exact(result['checks'],expected,path)


def transaction_events(phase,closure,r01_capability=False):
    if phase in ('initial','baseline-recovery'):return []
    rows=[]
    def add(kind,name='',generation=0,staged=0):rows.append(dict(sequence=len(rows)+1,kind=kind,name=name,generation=generation,stagedCount=staged))
    add('candidates-registered');add('transaction-begun')
    if r01_capability:add('metadata-budget-reserved')
    for i,name in enumerate(closure):add('skeleton-created',name,staged=i+1)
    if phase=='staged':return rows
    for name in closure:
        add('metadata-begin',name,staged=len(closure));add('metadata-ready',name,staged=len(closure))
    add('transaction-validated',staged=len(closure))
    if phase=='validated':return rows
    add('active-published',generation=1,staged=len(closure))
    for name in closure:
        add('initializer-begin',name,1,len(closure))
        add('initializer-failed' if phase=='initializer-failure' else 'initializer-complete',name,1,len(closure))
        if phase=='initializer-failure':return rows
    add('transaction-committed',generation=1,staged=len(closure))
    return rows


def verify_snapshots(result,context,path,closure):
    transaction=[]
    for row in result['transactionSnapshots']:
        fields(row,'phase rawJson diagnostics',path);strings(row,path,'phase rawJson');d=prior._diagnostic(json_text(row['rawJson'],path),path);exact(row['diagnostics'],d,path)
        exact(d['enabled'],True,path)
        phase=row['phase'];expected_state={'initial':0,'baseline-recovery':0,'staged':3,'validated':4,'committed':6,'final':6,'initializer-failure':9}
        require(phase in expected_state,f"{path}: unknown transaction phase");exact(d['stateCode'],expected_state[phase],path)
        exact('metadataBudgetCapabilityVersion' in d,'reserveCode' in result,f'{path}: result/diagnostic capability')
        exact(d['events'],transaction_events(phase,closure,'reserveCode' in result),path)
        exact(d['generation'],1 if phase in ('committed','final','initializer-failure') else 0,path)
        if row['phase'] not in ('initial','baseline-recovery'):
            exact(d['closureLoadOrder'],closure,path);exact(d['baselineBuildId'],context['manifest']['baselineBuildId'],path)
            exact(d['expected'],len(closure),path);exact(d['staged'],len(closure),path)
            exact([a['name'] for a in d['assemblies']],closure,path)
            item=context['fixtures'][result['patchId']]
            identities={i['name']:i for i in item['fixture']['assemblyIdentities']}
            for assembly in d['assemblies']:
                exact(assembly['mvid'],identities[assembly['name']]['mvid'],path);exact(assembly['skeletonBuilt'],True,path)
                exact(assembly['runtimeMetadataInitialized'],phase!='staged',path)
            retained=sum(Path(i['path']).stat().st_size for i in identities.values())
            if result['developmentBuild']:
                retained+=sum(prior._rel(item['root'],i['pdb'],path,'staged PDB').stat().st_size for i in item['patch']['closure'])
            exact(d['retainedBytes'],retained,path)
            require(not any(u['name'] in closure for u in d['baselineUses']),f"{path}: selected baseline was used")
        else:
            for key in ('expected','staged','retainedBytes'):exact(d[key],0,path)
            for key in ('closureLoadOrder','commitOrder','assemblies'):exact(d[key],[],path)
        if row['phase'] in ('initial','staged','validated'):
            require(all(not a['published'] and not a['moduleInitializerAttempted'] and not a['moduleInitializerRan'] for a in d['assemblies']),f"{path}: precommit initializer/publication")
        if row['phase'] in ('committed','final'):
            exact(d['commitOrder'],closure,path);exact(d['lastError'],0,path);exact(d['stateCode'],6,path)
            require(all(a['published'] and a['moduleInitializerAttempted'] and a['moduleInitializerRan'] for a in d['assemblies']),f"{path}: missing committed initializer")
        if phase=='initializer-failure':
            exact(d['commitOrder'],[],path);exact(d['lastError'],19,path)
            require(all(a['published'] and a['moduleInitializerAttempted'] and not a['moduleInitializerRan'] for a in d['assemblies']),f"{path}: failed initializer physical state differs")
        elif phase not in ('initial','baseline-recovery'):exact(d['lastError'],0,path)
        transaction.append(d)
    phases=[r['phase'] for r in result['transactionSnapshots']]
    expected=['initial','staged','validated','initializer-failure'] if result['mode']=='T06-09-InitializerFailure' else ['initial','staged','validated','committed','final']
    if result['mode']=='T06-09-BaselineRecovery':expected=['baseline-recovery']
    exact(phases,expected,path)
    execution=[]
    execution_phases,timing_layout=execution_layout(result['mode'],closure)
    exact([r['phase'] for r in result['executionSnapshots']],execution_phases,path)
    for row in result['executionSnapshots']:
        fields(row,'phase rawJson diagnostics',path);strings(row,path,'phase rawJson');d=verify_execution_diagnostic(json_text(row['rawJson'],path),path,result['developmentBuild']);exact(row['diagnostics'],d,path)
        if execution:
            for key in EXEC_COUNTERS.split():require(d[key]>=execution[-1][key],f"{path}: monotonic counter regressed {key}")
        if d['stateCode']<5:exact(d['shadowClassCctorStarted'],0,path);exact(d['shadowMethodChecks'],0,path)
        phase=row['phase'];state={'initial':0,'baseline-recovery':0,'configure-before':0,'configure-after':1,'begin-before':1,'begin-after':2,'stage-before':2,'stage-after':3,'validate-before':3,'validate-after':4,'commit-before':4}.get(phase,9 if result['mode']=='T06-09-InitializerFailure' else 6)
        exact(d['stateCode'],state,path);exact(d['generation'],1 if state in (6,9) else 0,path)
        execution.append(d)
    require(execution and transaction,f"{path}: missing fresh diagnostics domains")
    exact(result['nativeDiagnosticsJson'],result['transactionSnapshots'][-1]['rawJson'],path);exact(result['executionDiagnosticsJson'],result['executionSnapshots'][-1]['rawJson'],path)
    exact(result['stateCode'],transaction[-1]['stateCode'],path);exact(result['state'],transaction[-1]['state'],path)
    exact(execution[-1]['stateCode'],transaction[-1]['stateCode'],path);exact(execution[-1]['generation'],transaction[-1]['generation'],path)
    if closure:require(execution[-1]['shadowMethodChecks']>0,f"{path}: no actual guarded shadow method observations")
    verify_timings(result,execution,execution_phases,timing_layout,closure,path)
    return transaction,execution


def verify_timings(result,execution,execution_phases,timing_layout,closure,path):
    exact([r['phase'] for r in result['timings']],[r[0] for r in timing_layout],path)
    for timing,(_,before,after) in zip(result['timings'],timing_layout):
        fields(timing,'phase stopwatchFrequency startTicks endTicks elapsedTicks transformationsBefore transformationsAfter shadowTransformationsBefore shadowTransformationsAfter',path)
        require(type(timing['phase']) is str and timing['phase'],f"{path}: timing phase missing")
        for key in ('stopwatchFrequency','startTicks','endTicks','elapsedTicks'):integer(timing[key],path,0,(1<<63)-1)
        require(timing['stopwatchFrequency']>0 and timing['startTicks']>0 and timing['endTicks']>=timing['startTicks'] and timing['elapsedTicks']==timing['endTicks']-timing['startTicks'],f"{path}: fabricated elapsed timing")
        for key in ('transformationsBefore','transformationsAfter','shadowTransformationsBefore','shadowTransformationsAfter'):uint64(timing[key],path)
        require(timing['transformationsAfter']>=timing['transformationsBefore'] and timing['shadowTransformationsAfter']>=timing['shadowTransformationsBefore'],f"{path}: negative transform delta")
        for suffix,index in (('Before',before),('After',after)):
            exact(timing['transformations'+suffix],execution[index]['interpreterTransformations'],path)
            exact(timing['shadowTransformations'+suffix],execution[index]['shadowInterpreterTransformations'],path)
        if timing['phase'] in ('first','second'):
            owner=execution_phases[before].removesuffix('-before').rsplit('-',2)[0]
            asynchronous=business_phases(result['mode'])==['async']
            if owner in closure and not asynchronous and (timing['phase']=='second' or result['mode'].startswith('T06-10-')):
                exact(timing['shadowTransformationsBefore'],timing['shadowTransformationsAfter'],path)
    frequencies={t['stopwatchFrequency'] for t in result['timings']};require(len(frequencies)<=1,f"{path}: inconsistent stopwatch clock")


def active_images(build,pid):
    closure=order_for(pid) if pid!='BASELINE' else []
    return {name:build['images'][('GenerationPlan',pid,name) if name in closure else ('LinkedPlayer','',name)] for name in CANDIDATES}


def global_module_type_key(name):
    def part(value):return str(len(value.encode('utf-8')))+':'+value
    return 'type('+part(name.casefold())+'/'+part('')+'/'+part('<Module>')+'@0)'


def verify_class_keys(execution,identities,closure,path):
    """Decode observed physical class keys only against already-bound DLLs.

    Generic arguments may live in any exact linked provider; loading their
    inventories lazily avoids eagerly decoding the entire framework catalog.
    No search outside that closed catalog can satisfy an unknown name.
    """
    class Inventories(dict):
        def __getitem__(self,name):
            value=super().__getitem__(name)
            if value is None:
                value=types.read_type_inventory(identities[name]['path'])['types'];self[name]=value
            return value
    inventories=Inventories.fromkeys(identities);seen={}
    module_keys={global_module_type_key(name):name for name in identities}
    for snapshot in execution:
        for row in snapshot['classes']:
            name=row['logicalAssembly'];require(name in CANDIDATES,f"{path}: observation owner is not a registered candidate")
            key=row['typeKey']
            if key not in seen:
                module_name=module_keys.get(key)
                if module_name is not None:
                    inventories[module_name] # Reopen actual bytes and require their ECMA global Module TypeDef.
                    seen[key]=dict(assemblyName=module_name)
                else:seen[key]=types.TypeKeyReader(key,inventories,identities,closure,path).read()
            shape=seen[key];exact(shape['assemblyName'],name,path);exact(row['isActive'],True,path)
            shadow=snapshot['generation']>0 and name in closure
            exact(row['executionModeCode'],int(shadow),path)
            exact(row['physicalImageKind'],'Interpreter' if shadow else 'Aot',path)


def verify_module_observations(result,images,closure,path):
    rows=result['moduleObservations'];exact([(r['assemblyName'],r['phase']) for r in rows],[(n,phase) for n in CANDIDATES for phase in ('before-business','after-business')],path)
    previous=0
    for name in CANDIDATES:
        pair=[r for r in rows if r['assemblyName']==name]
        for row in pair:
            fields(row,'phase assemblyName moduleName providerMarker providerAssembly values moduleCount providerCount initializerStartTicks initializerEndTicks initializerStopwatchFrequency',path)
            strings(row,path,'phase assemblyName moduleName providerMarker providerAssembly')
            for key in ('moduleCount','providerCount'):integer(row[key],path,0)
            for key in ('initializerStartTicks','initializerEndTicks','initializerStopwatchFrequency'):integer(row[key],path,0,(1<<63)-1)
            values=values_map(row['values'],path)
            fields(values,'assembly marker cctor runs module.count module.startTicks module.endTicks module.frequency provider.assembly provider.marker provider.count',path)
            exact(values['assembly'],name,path);exact(values['marker'],physical_marker(images[name],path)[0],path);exact(values['cctor'],'1',path)
            for field,key in (('moduleCount','module.count'),('providerCount','provider.count'),('initializerStartTicks','module.startTicks'),('initializerEndTicks','module.endTicks'),('initializerStopwatchFrequency','module.frequency')):exact(row[field],numeric_string(values[key],path),path)
            exact(row['providerAssembly'],values['provider.assembly'],path);exact(row['providerMarker'],values['provider.marker'],path)
            exact(row['moduleCount'],1 if name in closure else 0,path);exact(row['moduleName'],name+'.dll',path)
            if name not in closure:
                for key in ('initializerStartTicks','initializerEndTicks','initializerStopwatchFrequency','providerCount'):exact(row[key],0,path)
                exact(row['providerAssembly'],'none',path);exact(row['providerMarker'],'none',path)
        before,after=pair
        warm_runs=int(result['mode'].startswith('T06-10-') and name in closure)
        exact(numeric_string(values_map(before['values'],path)['runs'],path),warm_runs,path)
        exact(numeric_string(values_map(after['values'],path)['runs'],path),warm_runs+2*len(business_phases(result['mode']))+1,path)
        for key in ('moduleCount','providerCount','providerAssembly','providerMarker','initializerStartTicks','initializerEndTicks','initializerStopwatchFrequency'):exact(before[key],after[key],path)
        if name in closure:
            require(before['initializerStartTicks']>0 and before['initializerStartTicks']>=previous and before['initializerEndTicks']>=before['initializerStartTicks'] and before['initializerStopwatchFrequency']>0,f"{path}: initializer order/time evidence invalid")
            previous=before['initializerEndTicks']
            provider='none' if name==CONTRACTS else EXTENSIBILITY if name in (INTERNAL,EXTENSIBILITY_CONSUMER) else CONTRACTS
            exact(before['providerAssembly'],provider,path);exact(before['providerCount'],int(provider in closure),path)
            exact(before['providerMarker'],'none' if provider=='none' else physical_marker(images[provider],path)[0],path)


def verify_observations(result,build,pid,path):
    closure=order_for(pid) if pid!='BASELINE' else [];images=active_images(build,pid)
    mode=result['mode'];comparison=mode.startswith(('T06-10-','T06-12-'))
    phase=next((word for prefix,word in (('T06-01-','new'),('T06-02-','statics'),('T06-06-','delegates'),('T06-07-','generics'),('T06-08-','async')) if mode.startswith(prefix)),'dispatch')
    phases=['new','dispatch','generics'] if comparison else [phase]
    expected=[]
    for name in CANDIDATES:
        expected.append((name,'mode'))
        for p in phases:expected.extend(((name,p),(name,'second-'+p)))
        expected.append((name,'exceptions'))
        if phase=='async':expected.append((name,'coroutine'))
    if pid=='BASELINE':expected=[(INTERNAL,'baseline-recovery')]
    exact([(r['assemblyName'],r['phase']) for r in result['observations']],expected,path)
    first={}
    for row in result['observations']:
        fields(row,'phase assemblyName witness typeInfoJson mode executionCode repeatedSameType values',path);strings(row,path,'phase assemblyName witness typeInfoJson mode')
        name=row['assemblyName'];image=images[name];shadow=name in closure
        exact(row['witness'],witness(name),path);exact(row['executionCode'],4 if pid=='BASELINE' else 0,path);exact(row['repeatedSameType'],True,path)
        exact(row['mode'],'InterpreterShadow' if shadow else 'AotBaseline',path)
        info=types.verify_type_info(json_text(row['typeInfoJson'],path),path)
        exact(info['logicalAssembly'],name,path);exact(info['executionModeCode'],1 if shadow else 0,path);exact(info['isActive'],True,path);exact(info['physicalImageKind'],'Interpreter' if shadow else 'Aot',path)
        exact(info['containsShadowTypes'],shadow,path)
        inventories={n:types.read_type_inventory(im['identity']['path'])['types'] for n,im in images.items()}
        key=types.TypeKeyReader(info['typeKey'],inventories,{n:im['identity'] for n,im in images.items()},closure,path).read()
        exact(key['fullName'],witness(name),path);exact(key['assemblyName'],name,path)
        if not result['developmentBuild']:exact(info['pointerDetailsAvailable'],False,path)
        p=row['phase'];values=row['values']
        if p=='mode':exact(values,[],path)
        elif p=='exceptions':verify_exception(values,image,path,shadow,result['developmentBuild'])
        else:
            repeat=p.startswith('second-');business='new' if p=='baseline-recovery' else p.removeprefix('second-')
            verify_business(values,name,business,image,path,int(repeat),first.get((name,business)) if repeat else None,images[EXTENSIBILITY])
            if not repeat:first[name,business]=values
    if pid=='BASELINE':return
    exact([r['assemblyName'] for r in result['methodObservations']],list(CANDIDATES),path)
    for row in result['methodObservations']:
        fields(row,'phase assemblyName actualDeclaringType name signature metadataToken',path);strings(row,path,'phase assemblyName actualDeclaringType name signature');integer(row['metadataToken'],path,1)
        exact(row['phase'],'business',path);exact(row['name'],'Run',path);exact(row['actualDeclaringType'],witness(row['assemblyName']),path)
        actual=next((m for m in images[row['assemblyName']]['methods'] if m['metadataToken']==row['metadataToken']),None)
        require(actual and actual['name']=='Run' and actual['declaringType']==row['actualDeclaringType'] and actual['parameterTypes'][0]['type']=='System.String' and actual['returnType']['type']=='System.String[]',f"{path}: invoked method token/signature differs from actual selected image")
        exact(row['signature'],'System.String[] Run(System.String)',path)
    verify_module_observations(result,images,closure,path)


def verify_warmup_observations(result,item,build,path):
    rows=result['warmupObservations'];warm=result['mode'].startswith('T06-10-')
    if not warm:exact(rows,[],path);return
    manifest=item['warmup'];images=active_images(build,item['fixture']['patchId'])
    expected=[('prejit','type',r['assembly'],r['type'],'') for r in manifest['types']]+[('prejit','method',r['assembly'],r['declaringType'],r['name']) for r in manifest['methods']]
    for entry in manifest['types']:
        expected += [('module-warmup-method','method',r['assembly'],r['declaringType'],r['name']) for r in manifest['methods'] if r['assembly']==entry['assembly'] and r['name']!='Run']
        expected.append(('module-warmup','module',entry['assembly'],entry['type'],'Run'))
    exact([(r['phase'],r['targetKind'],r['assemblyName'],r['declaringType'],r['name']) for r in rows],expected,path)
    method_entries=iter(manifest['methods']);call_entries=iter(r for r in manifest['methods'] if r['name']!='Run')
    snapshot_rows=result['executionSnapshots'];snapshots=[r['diagnostics'] for r in snapshot_rows]
    warmup_indices=[i for i,r in enumerate(snapshot_rows) if r['phase'].startswith('warmup-type-') or r['phase'].startswith('warmup-method-')]
    indices=iter(warmup_indices);previous_call=0
    for row in rows:
        fields(row,'phase targetKind assemblyName declaringType name returnType actualReturn genericArguments parameterTypes genericArity metadataToken preJitClass preJitMethod transformationBefore transformationAfter shadowTransformationBefore shadowTransformationAfter returnedValues',path)
        strings(row,path,'phase targetKind assemblyName declaringType name returnType actualReturn');integer(row['genericArity'],path,0);integer(row['metadataToken'],path,0)
        for key in ('genericArguments','parameterTypes','returnedValues'):array(row[key],path);require(all(type(v) is str for v in row[key]),f"{path}: malformed warmup string array")
        for key in ('preJitClass','preJitMethod'):boolean(row[key],path)
        for key in ('transformationBefore','transformationAfter','shadowTransformationBefore','shadowTransformationAfter'):uint64(row[key],path)
        require(row['transformationAfter']>=row['transformationBefore'] and row['shadowTransformationAfter']>=row['shadowTransformationBefore'],f"{path}: warmup counter regression")
        exact(row['preJitClass'],row['targetKind']=='type',path);exact(row['preJitMethod'],row['phase']=='prejit' and row['targetKind']=='method',path)
        image=images[row['assemblyName']]
        if row['phase']=='prejit':
            after=next(indices);before=after-1
        else:
            prefix='warmup-call' if row['phase']=='module-warmup-method' else 'module-warmup'
            suffix=row['assemblyName']+('-'+row['name'] if prefix=='warmup-call' else '')
            # Repeated Echo calls consume the next matching pair, never collapse.
            start=previous_call if row['phase']=='module-warmup-method' else 0
            before=next(i for i in range(start,len(snapshot_rows)) if snapshot_rows[i]['phase']==prefix+'-before-'+suffix)
            after=next(i for i in range(before+1,len(snapshot_rows)) if snapshot_rows[i]['phase']==prefix+'-after-'+suffix)
            if row['phase']=='module-warmup-method':previous_call=after+1
        for stem,key in (('transformation','interpreterTransformations'),('shadowTransformation','shadowInterpreterTransformations')):
            exact(row[stem+'Before'],snapshots[before][key],path);exact(row[stem+'After'],snapshots[after][key],path)
        if row['targetKind']=='method':
            entry=next(method_entries if row['phase']=='prejit' else call_entries)
            methods=[m for m in image['methods'] if m['metadataToken']==row['metadataToken']]
            require(len(methods)==1 and methods[0]['name']==row['name'] and methods[0]['genericArity']==row['genericArity'] and methods[0]['declaringType']==row['declaringType'],f"{path}: warmup method not in selected patch")
            if row['phase']=='prejit':
                qualify=lambda v:runtime_warmup_aqn(v,build,path)
                exact(row['genericArguments'],[qualify(v) for v in entry['genericArguments']],path)
                exact(row['returnType'],qualify(entry['returnType']),path);exact(row['parameterTypes'],[qualify(v) for v in entry['parameterTypes']],path)
                returned='True'
            else:
                exact(row['genericArguments'],[],path);exact(row['parameterTypes'],[],path);exact(row['returnType'],'',path)
                returned=str(physical_marker(image,path)[1]+7) if row['name']=='WarmupValue' else '7' if entry['returnType']['type']=='System.Int32' else 'warmup'
            exact(row['actualReturn'],returned,path);exact(row['returnedValues'],[returned],path)
        else:
            for key in ('genericArguments','parameterTypes'):exact(row[key],[],path)
            exact(row['returnType'],'',path);exact(row['genericArity'],0,path);exact(row['metadataToken'],0,path)
            if row['targetKind']=='type':exact(row['actualReturn'],'',path);exact(row['returnedValues'],[],path)
        if row['targetKind']=='module':
            values=values_map(row['returnedValues'],path);fields(values,'phase warmup echo new dispatch generic',path)
            exact(values['phase'],'warmup',path);exact(values['echo'],'warmup',path);exact(values['warmup'],str(physical_marker(image,path)[1]+7),path)
            marker=physical_marker(image,path)[0]
            exact(values['new'],'marker='+marker,path);exact(values['generic'],'generic.type='+business_generic_type(row['assemblyName'],image,path),path)
            exact(values['dispatch'],'virtual='+marker+(':virtual' if row['assemblyName'] in (CONTRACTS,CONTRACTS_CONSUMER) else ':sealed'),path)
            exact(row['actualReturn'],';'.join(row['returnedValues']),path)


def verify_case(path,context,build):
    result=verify_result_header(path,context,build);mode=result['mode'];off=mode=='T06-11-FeatureOff';recovery=mode=='T06-09-BaselineRecovery';failure=mode=='T06-09-InitializerFailure'
    if off:
        if 'reserveCode' in result:exact(result['reserveCode'],-1,path)
        for key in ('configureCode','beginCode','validateCode','commitCode','abortCode','stateCode','executionModeCode','diagnosticsCode','executionDiagnosticsCode','typeResolutionCode'):exact(result[key],1,path)
        exact(result['stageResults'],[dict(name='',dllSha256='',pdbSha256='',code=1)],path);exact(result['state'],'Disabled',path);exact(result['executionMode'],'AotBaseline',path)
        disabled=prior._diagnostic(json_text(result['nativeDiagnosticsJson'],path),path);exact(disabled['enabled'],False,path);exact(disabled['lastError'],1,path);exact(disabled['stateCode'],0,path)
        for key,value in disabled.items():
            if key == 'startupObservationMode':exact(value,'Unavailable',path)
            elif key not in ('schemaVersion','runtimeAbiVersion','enabled','lastError','stateCode','state'):
                exact(value,[] if type(value) is list else '' if type(value) is str else 0,path)
        exact(result['executionDiagnosticsJson'],'',path);exact(result['businessLaunched'],False,path)
        for key in RESULT_ARRAYS.split():
            if key not in ('stageResults','checks','transactionSnapshots'):exact(result[key],[],path)
        exact(result['transactionSnapshots'],[dict(phase='disabled',rawJson=result['nativeDiagnosticsJson'],diagnostics=disabled)],path)
        verify_checks(result,[],path)
        for key in ('patchId','patchManifestPath','patchManifestSha256','compileSnapshotHash','recoveryResultPath','recoveryResultSha256'):exact(result[key],'',path)
        prior._verify_ordinary(result['ordinary'],build['player'],path)
        return result
    exact(result['diagnosticsCode'],0,path);exact(result['executionDiagnosticsCode'],0,path)
    exact(result['abortCode'],-1,path);prior._inactive(result['ordinary'],prior.ORDINARY_FIELDS,path)
    if recovery:
        if 'reserveCode' in result:exact(result['reserveCode'],-1,path)
        for key in ('configureCode','beginCode','validateCode','commitCode'):exact(result[key],-1,path)
        exact(result['stateCode'],0,path);exact(result['typeResolutionCode'],0,path);exact(result['businessLaunched'],True,path)
        for key in ('patchId','patchManifestPath','patchManifestSha256','compileSnapshotHash'):exact(result[key],'',path)
        for key in ('stageOrder','stageResults','methodObservations','moduleObservations','warmupObservations','timings','supplementaryMetadata'):exact(result[key],[],path)
        exact(result['executionModeCode'],4,path);exact(result['executionMode'],'AotBaseline',path)
        verify_checks(result,[],path);_,execution=verify_snapshots(result,context,path,[])
        verify_class_keys(execution,{i['name']:i for i in build['player']['assemblyIdentities']},[],path)
        verify_observations(result,build,'BASELINE',path);return result
    pid='InitializerFailure' if failure else 'P03' if mode.endswith('P03') or mode=='T06-13-ReleaseNoPdb' else 'P02' if mode.endswith('P02') else 'P01'
    item=context['fixtures'][pid];fixture=item['fixture'];closure=fixture['closureLoadOrder']
    exact('reserveCode' in result,item.get('r01Capability',False),f'{path}: result/patch budget capability')
    if 'reserveCode' in result:exact(result['reserveCode'],0,path)
    for key in ('patchId','patchManifestPath','patchManifestSha256','compileSnapshotHash'):exact(result[key],fixture['patchManifest'] if key=='patchManifestPath' else fixture[key],path)
    for key in ('configureCode','beginCode','validateCode'):exact(result[key],0,path)
    exact(result['commitCode'],19 if failure else 0,path);exact(result['stateCode'],9 if failure else 6,path);exact(result['typeResolutionCode'],-1 if failure else 0,path)
    exact(result['businessLaunched'],not failure,path);exact(result['stageOrder'],closure,path)
    exact(result['executionModeCode'],-1 if failure else 0,path)
    exact(result['executionMode'],'' if failure else 'InterpreterShadow' if CANDIDATES[-1] in closure else 'AotBaseline',path)
    for key in ('recoveryResultPath','recoveryResultSha256'):exact(result[key],'',path)
    verify_checks(result,closure,path)
    expected=[]
    for name in closure:
        image=next(i for i in item['patch']['closure'] if i['name']==name)
        expected.append(dict(name=name,code=0,dllSha256=image['sha256'],pdbSha256=image['pdbSha256'] or ''))
    exact(result['stageResults'],expected,path)
    exact([r['assemblyName'] for r in result['supplementaryMetadata']],fixture['requiredAotMetadataNames'],path)
    for row in result['supplementaryMetadata']:
        fields(row,'assemblyName path sha256 resultCode loaded',path);exact(row['resultCode'],0,path);exact(row['loaded'],True,path)
        item_=next(i for i in build['player']['supplementaryMetadataInputs'] if i['assemblyName']==row['assemblyName'])
        exact(row['path'],item_['path'],path);exact(row['sha256'],item_['sha256'],path)
    transaction,execution=verify_snapshots(result,context,path,closure)
    identities={i['name']:i for i in build['player']['assemblyIdentities']}
    identities.update({name:image['identity'] for name,image in active_images(build,pid).items()})
    verify_class_keys(execution,identities,closure,path)
    if failure:
        exact(transaction[-1]['lastError'],19,path)
        for key in ('observations','methodObservations','moduleObservations','warmupObservations'):exact(result[key],[],path)
    else:
        verify_observations(result,build,pid,path);verify_warmup_observations(result,item,build,path)
    return result


def replay_receipt_path(context,receipt_path=None):
    selected=context['path'].parent/'m06-editor-replay.json' if receipt_path is None else Path(receipt_path)
    return canonical(str(selected),context['path'],'editorReplayReceipt')


def verify_replay(context,build,receipt_path=None):
    path=replay_receipt_path(context,receipt_path);receipt=obj(path,REPLAY_FIELDS);manifest=context['manifest'];player=build['player']
    exact(receipt['schemaVersion'],1,path);exact(receipt['milestone'],'M06',path);exact(receipt['result'],'Passed',path);exact(receipt['comparisonPolicy'],'compiler-linked-resource-generation-warmup:1',path)
    for key in ('baselineManifestPath','baselineManifestSha256','baselineInputSnapshotHash','baselineBuildId','generationProofPath','generationProofSha256','developmentBuild'):exact(receipt[key],manifest[key],path)
    for key,value in dict(fixtureManifestPath=str(context['path']),fixtureManifestSha256=digest(context['path']),playerBuildReceiptPath=str(build['path']),playerBuildReceiptSha256=digest(build['path']),playerBuildGuid=player['buildGuid'],nativeLibrarySha256=player['nativeLibrarySha256'],linkedPlayerReceiptHash=build['snapshot']['linkedPlayerReceiptHash']).items():exact(receipt[key],value,path)
    prior._pins(receipt['validatorSourcePins'],path,context['baseline']['sourcePins'])
    scratch=canonical(receipt['replayScratchPath'],path,'replayScratchPath',True);require(scratch.name.startswith('M06Replay-') and scratch!=context['path'].parent,f"{path}: replay scratch is not independent")
    expected=[]
    for pid,item in context['fixtures'].items():
        expected.append({key:item['fixture'][key] for key in 'patchId patchManifestSha256 compileSnapshotHash generationPlanSha256 changedRoots closureLoadOrder'.split()})
        exact(types._artifact_tree(item['root']),types._artifact_tree(scratch/pid),path)
    exact(receipt['fixtures'],expected,path)
    return dict(path=str(path),sha256=digest(path))


def record_case(found,pids,result,file):
    mode=result.get('mode');require(mode in MODES and mode not in found,f"{file}: unknown/duplicate case")
    integer(result.get('processId'),file,1)
    require(result['processId'] not in pids,f"{file}: process reused between cases")
    pids.add(result['processId']);found[mode]=(result,file)


def verify_suite(fixture_manifest,on_build,off_build,release_fixture_manifest,release_build,results,m01_baseline_root):
    development=verify_inputs(fixture_manifest,m01_baseline_root,True);release=verify_inputs(release_fixture_manifest,m01_baseline_root,False)
    on=verify_player(on_build,development,True,True);off=verify_player(off_build,development,False,True);released=verify_player(release_build,release,True,False)
    require(len({b['player']['buildGuid'] for b in (on,off,released)})==3 and len({b['player']['nativeLibrarySha256'] for b in (on,off,released)})==3,f"{results}: ON/OFF/release are not three actual builds")
    for key in ('snapshotHash','buildGuid','playerOutput','nativeLibraryPath','nativeLibrarySha256','linkedPlayerReceiptHash'):
        exact(on['snapshot'][key]!=off['snapshot'][key],True,f"{results}: native ON/OFF {key}")
    exact(managed_player_inputs(on['snapshot'],on['path']),managed_player_inputs(off['snapshot'],off['path']),f"{results}: native ON/OFF managed inputs")
    require(development['manifest']['baselineBuildId']!=release['manifest']['baselineBuildId'] and development['path']!=release['path'],f"{results}: release baseline was relabeled")
    replays=[verify_replay(development,on),verify_replay(release,released)]
    result_root=canonical(str(results),results,'results',True);found={};pids=set();files=[]
    for file in sorted(result_root.glob('m06-*.json')):
        if file.name.endswith(('-native-diagnostics.json','-execution-diagnostics.json')):continue
        header=obj(file);mode=header.get('mode')
        require(mode in MODES and mode not in found,f"{file}: unknown/duplicate case")
        context,build=(release,released) if mode=='T06-13-ReleaseNoPdb' else (development,off) if mode=='T06-11-FeatureOff' else (development,on)
        result=verify_case(file,context,build);record_case(found,pids,result,file);files.append(dict(mode=mode,path=str(file),sha256=digest(file),processId=result['processId']))
    exact(set(found),set(MODES),result_root)
    failed,failed_path=found['T06-09-InitializerFailure'];recovery,_=found['T06-09-BaselineRecovery']
    exact(recovery['recoveryResultPath'],str(failed_path),result_root);exact(recovery['recoveryResultSha256'],digest(failed_path),result_root)
    for key in ('baselineBuildId','playerBuildReceiptSha256','buildGuid','fixtureManifestSha256','runtimeAbiHash'):exact(recovery[key],failed[key],result_root)
    for pid in ('P01','P02','P03'):
        warm=found['T06-10-Warmup-'+pid][0];cold=found['T06-12-NoWarmup-'+pid][0]
        exact(warm['patchManifestSha256'],cold['patchManifestSha256'],result_root)
        # Compare actual successful transformations, not wall-clock thresholds.
        warm_delta=sum(t['shadowTransformationsAfter']-t['shadowTransformationsBefore'] for t in warm['timings'] if t['phase']=='first')
        cold_delta=sum(t['shadowTransformationsAfter']-t['shadowTransformationsBefore'] for t in cold['timings'] if t['phase']=='first')
        require(warm_delta<=cold_delta,f"{result_root}: declared warmup did not reduce/retain synchronous transform work")
    return dict(schemaVersion=1,milestone='M06',result='Passed',caseCount=len(found),results=files,editorReplays=replays,
                fixtureManifestSha256=digest(development['path']),releaseFixtureManifestSha256=digest(release['path']))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('fixture-manifest','on-build','off-build','release-fixture-manifest','release-build','results','m01-baseline-root'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        receipt=verify_suite(args.fixture_manifest,args.on_build,args.off_build,args.release_fixture_manifest,args.release_build,args.results,args.m01_baseline_root)
        text=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
        if args.output:
            with args.output.open('x',encoding='utf-8') as stream:stream.write(text)
        print(text,end='');return 0
    except (VerificationError,OSError,ValueError,KeyError,TypeError,AttributeError,IndexError,StopIteration) as error:
        print('M06 verification failed: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
