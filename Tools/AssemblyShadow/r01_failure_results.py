"""Strict provenance and raw-runtime gate for the separate R01 failure matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import m07_results as m07
import m04_results as m04
import r01_results as r01
import r01_early_capsule as early_capsule
from r00_player_inputs import verify_inputs
from shadow_tools import require

MODES = ("R01-Failure-P03-Control", "R01-Failure-Q04-Metadata", "R01-Failure-InitializerThrow")
EARLY_BINDING_KIND = "R01FailureEarlyAdmissionBinding"
EARLY_MODE_BY_FAILURE = {
    MODES[0]: "Control",
    MODES[1]: "MetadataFailureContinue",
    MODES[2]: "InitializerFailureContinue",
}

def early_mode(mode):
    require(mode in EARLY_MODE_BY_FAILURE, "Unknown failure/publication mode")
    return EARLY_MODE_BY_FAILURE[mode]

def expected_early_result(mode):
    return "Passed" if mode == MODES[0] else "PassedExpectedFailureContinued"

INITIALIZER_ID = "R01-P03-InitializerThrow"
INITIALIZER_TARGET = "AssemblyA.Implementation.Extensibility"
INITIALIZER_REASON = "R01-INIT-THROW:" + INITIALIZER_TARGET
DEFINES = ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M03_INITIALIZERS",
           "ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_R01_INITIALIZER_THROW"]
RESULT_FIELDS = "schemaVersion kind mode result error resultPath processId mainThreadId unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineManifestPath baselineManifestSha256 failureFixturesPath failureFixturesSha256 negativeInputPath negativeInputSha256 patchId patchManifestPath patchManifestSha256 nativeLibrarySha256 nativeMetadataSha256 inputSnapshotHash il2cpp closureLoadOrder orderedSizes byteInputs earlyMode earlyReceiptPath earlyReceiptSha256 capsulePath capsuleSha256 postHostDiagnostics postHostCapacity postHostRecovery"
RAW_FIELDS = "phase rawJson rawPath rawSha256 code threadId ticks"
RECEIPT_FIELDS = "schemaVersion kind result sourcePins baselineManifestPath baselineManifestSha256 baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 initializer replayPatchManifest replayPatchManifestSha256 replayBytesEqual files"
LAUNCH_FIELDS = "schemaVersion kind projectRoot fixtureManifestPath onBuildReceiptPath offBuildReceiptPath replayReceiptPath failureFixturesPath negativeInputPath sourcePins modes processLaunches resultDirectory capsuleDirectory inputHashesBefore inputHashesAfter inputsUnchanged"
PROCESS_FIELDS = "mode command processId startedAtUnix durationSeconds exitCode timedOut passed earlyBindingPath earlyBindingSha256 capsulePath capsuleSha256 earlyResultPath earlyResultSha256 resultPath resultSha256 logPath logSha256 consolePath consoleSha256 error"
read, exact, fields, digest, bound, canonical = r01.read, r01.exact, r01.fields, r01.digest, r01.bound, r01.canonical
prior = m07.prior

PROFILE2_PROFILE_FIELDS = getattr(m07, "R01B_PROFILE_FIELDS", (
    "schemaVersion profileVersion nativeBudgetCapabilityVersion codecId codecBits "
    "invalidIndexSentinel aotMaxIndex minImageId maximumImageCount pageValues "
    "usablePageCapacity chargedPageCeiling minimumFreePageMargin maximumDllBytes "
    "aggregateDllEnvelopeBytes nativeSourceRevision nativeCodecHeaderSha256"
))
PROFILE2_CAPACITY_FIELDS = (
    "schemaVersion enabled profileVersion maximumImageCount maximumDllBytes usablePageCapacity "
    "chargedPageCeiling minimumFreePageMargin reservedPages mappedPages lifetimeReservedImageCount "
    "remainingImageCount requiredImages acceptedImages firstFailingIndex firstFailingSize "
    "failureReason fitsPreliminary runtimeFinalizationRequired aggregateInputDllBytes "
    "aggregateInputDllBytesInformational ordinaryAllocatedCount shadowAllocatedCount reservedShadowImageCount"
)
PROFILE2_BASELINE_CAPACITY_FIELDS = getattr(m07, "R01B_REPORT_FIELDS", (
    "schemaVersion profileVersion budgetCapabilityVersion nativeBudgetCapabilityVersion nativeSourceRevision "
    "nativeCodecHeaderSha256 codecId codecBits invalidIndexSentinel aotMaxIndex minImageId maxImages pageValues "
    "usablePages maxChargedPages maxDllBytes aggregateDllEnvelopeBytes maximumImageCount maximumDllBytes "
    "usablePageCapacity chargedPageCeiling minimumFreePageMargin currentReservedImageCount reservedImageCountBefore "
    "reservedImageCountAfter requestedImageCount requiredImages aggregateDllBytes aggregateInputDllBytes "
    "aggregateInputDllBytesInformational reservedPages mappedPages lifetimeReservedImageCount remainingImageCount "
    "inputs allocations acceptedImages fitsImageCount aggregateDllEnvelopeFits aggregateDllEnvelopeExceeded "
    "inputCountWasBounded admissionAccepted fitsPreliminary finalPageFitKnown runtimeFinalizationRequired "
    "admissionKind firstFailingIndex firstFailingAssembly failureReason"
))
PROFILE2_MAX_IMAGES = 8192
PROFILE2_MAX_DLL_BYTES = 32 * 1024 * 1024
PROFILE2_USABLE_PAGE_CAPACITY = 524287
PROFILE2_CHARGED_PAGE_CEILING = 393215
PROFILE2_MINIMUM_FREE_PAGE_MARGIN = 131072


def metadata_profile(context, label="R01"):
    """Return the negotiated metadata profile from already verified inputs.

    The profile is selected from the baseline contract, rather than inferred
    from an untrusted Player snapshot.  Profile 1 remains delegated to the
    historical R01 input gate; profile 2 requires its complete baseline
    declarations before any raw result is accepted.
    """
    baseline = context["baseline"]
    capability = baseline.get("nativeBudgetCapabilityVersion", 0)
    require(type(capability) is int and capability in (1, 2),
            f"{label}: unsupported baseline budget capability")
    if capability == 1:
        return 1
    profile = fields(baseline.get("metadataEncodingProfile2"), PROFILE2_PROFILE_FIELDS,
                     f"{label}.baseline.metadataEncodingProfile2")
    report = fields(baseline.get("metadataCapacityReport2"), PROFILE2_BASELINE_CAPACITY_FIELDS,
                    f"{label}.baseline.metadataCapacityReport2")
    for key, expected in (("schemaVersion", 2), ("profileVersion", 2),
                          ("nativeBudgetCapabilityVersion", 2),
                          ("maximumImageCount", PROFILE2_MAX_IMAGES),
                          ("maximumDllBytes", PROFILE2_MAX_DLL_BYTES),
                          ("usablePageCapacity", PROFILE2_USABLE_PAGE_CAPACITY),
                          ("chargedPageCeiling", PROFILE2_CHARGED_PAGE_CEILING),
                          ("minimumFreePageMargin", PROFILE2_MINIMUM_FREE_PAGE_MARGIN)):
        exact(profile[key], expected, f"{label}.baseline.metadataEncodingProfile2.{key}")
    for key, expected in (("schemaVersion", 2), ("profileVersion", 2),
                          ("maximumImageCount", PROFILE2_MAX_IMAGES),
                          ("maximumDllBytes", PROFILE2_MAX_DLL_BYTES),
                          ("usablePageCapacity", PROFILE2_USABLE_PAGE_CAPACITY),
                          ("chargedPageCeiling", PROFILE2_CHARGED_PAGE_CEILING),
                          ("minimumFreePageMargin", PROFILE2_MINIMUM_FREE_PAGE_MARGIN),
                          ("runtimeFinalizationRequired", True),
                          ("aggregateInputDllBytesInformational", True)):
        exact(report[key], expected, f"{label}.baseline.metadataCapacityReport2.{key}")
    exact(report.get("nativeBudgetCapabilityVersion"), 2,
          f"{label}.baseline.metadataCapacityReport2.nativeBudgetCapabilityVersion")
    return 2


def verify_profile2_capacity(value, sizes, label):
    """Verify the native profile 2 preliminary admission report.

    Page counts are native observations and are checked for type and bounds;
    admission, aggregate bytes, and all-or-nothing acceptance are recomputed
    here from the ordered DLL sizes and the committed reservation count.
    """
    fields(value, PROFILE2_CAPACITY_FIELDS, label)
    exact(value["schemaVersion"], 2, label + ".schemaVersion")
    exact(value["enabled"], True, label + ".enabled")
    exact(value["profileVersion"], 2, label + ".profileVersion")
    for key, expected in (("maximumImageCount", PROFILE2_MAX_IMAGES),
                          ("maximumDllBytes", PROFILE2_MAX_DLL_BYTES),
                          ("usablePageCapacity", PROFILE2_USABLE_PAGE_CAPACITY),
                          ("chargedPageCeiling", PROFILE2_CHARGED_PAGE_CEILING),
                          ("minimumFreePageMargin", PROFILE2_MINIMUM_FREE_PAGE_MARGIN)):
        exact(value[key], expected, label + "." + key)
    require(type(sizes) is list and all(type(size) is int and not isinstance(size, bool) and size >= 0 for size in sizes),
            label + ".sizes: expected non-negative integers")
    for key in ("reservedPages", "mappedPages", "lifetimeReservedImageCount", "remainingImageCount",
                "requiredImages", "acceptedImages", "firstFailingSize", "aggregateInputDllBytes",
                "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedShadowImageCount"):
        r01.integer(value[key], label + "." + key)
    exact(value["requiredImages"], len(sizes), label + ".requiredImages")
    reserved = value["lifetimeReservedImageCount"]
    require(reserved <= PROFILE2_MAX_IMAGES, label + ".lifetimeReservedImageCount")
    exact(value["remainingImageCount"], PROFILE2_MAX_IMAGES - reserved, label + ".remainingImageCount")
    aggregate = 0
    for size in sizes:
        aggregate = min((1 << 64) - 1, aggregate + size)
    exact(value["aggregateInputDllBytes"], aggregate, label + ".aggregateInputDllBytes")
    exact(value["runtimeFinalizationRequired"], True, label + ".runtimeFinalizationRequired")
    exact(value["aggregateInputDllBytesInformational"], True, label + ".aggregateInputDllBytesInformational")
    failure_index = -1
    failure_reason = "None"
    if len(sizes) > PROFILE2_MAX_IMAGES - reserved:
        failure_index, failure_reason = PROFILE2_MAX_IMAGES - reserved, "ImageLimit"
    else:
        for index, size in enumerate(sizes):
            if size == 0:
                failure_index, failure_reason = index, "EmptyDll"
                break
            if size > PROFILE2_MAX_DLL_BYTES:
                failure_index, failure_reason = index, "DllTooLarge"
                break
    fits = failure_index == -1
    exact(value["fitsPreliminary"], fits, label + ".fitsPreliminary")
    exact(value["acceptedImages"], len(sizes) if fits else 0, label + ".acceptedImages")
    exact(value["firstFailingIndex"], failure_index, label + ".firstFailingIndex")
    exact(value["firstFailingSize"], 0 if failure_index < 0 else sizes[failure_index], label + ".firstFailingSize")
    exact(value["failureReason"], failure_reason, label + ".failureReason")
    require(value["reservedShadowImageCount"] <= value["lifetimeReservedImageCount"],
            label + ".reservedShadowImageCount")
    return value


def verify_initializer(fixture, manifest, baseline, manifest_path):
    patch_id = fixture["patchId"]
    exact(patch_id, INITIALIZER_ID, "initializer.patchId")
    defines, roots, dll_only = DEFINES, list(m07.fixture_order("P03")), True
    exact(sorted(fixture["defines"]), sorted(defines), f"{manifest_path}.{patch_id}.defines")
    exact(set(fixture["changedRoots"]), set(roots), f"{manifest_path}.{patch_id}.changedRoots")
    exact(fixture["dllOnly"], dll_only, f"{manifest_path}.{patch_id}.dllOnly")
    expected_order = m07.fixture_order("P03")
    exact(fixture["closureLoadOrder"], expected_order, f"{manifest_path}.{patch_id}.closureLoadOrder")
    compile_root, compiled = m07.verify_compile_snapshot(fixture["compileSnapshot"], fixture["compileSnapshotHash"],
                                                     baseline, manifest_path, defines)
    patch_root = canonical(fixture["patchDirectory"], manifest_path, "patchDirectory", True)
    patch_path = bound(fixture["patchManifest"], fixture["patchManifestSha256"], manifest_path, "patchManifest")
    exact(patch_path, patch_root / "patch-manifest.json", f"{manifest_path}.{patch_id}.patchManifest")
    patch = prior._obj(patch_path)
    # m07.patch_schema is the single verified wire-schema selector. It keeps
    # historical profile 1 fixtures strict while admitting the explicit
    # profile 2 extension owned by the current native baseline.
    capability = m07.patch_schema(patch, patch_path)
    sidecar = patch_root / "manifest.sha256"
    require(sidecar.is_file() and not sidecar.is_symlink() and sidecar.read_text(encoding="utf-8").strip() == digest(patch_path),
            f"{sidecar}: missing or stale patch manifest sidecar")
    exact(patch["schemaVersion"], 1, f"{patch_path}.schemaVersion")
    exact(patch["semanticHashSchema"], 1, f"{patch_path}.semanticHashSchema")
    exact(patch["patchId"], patch_id, f"{patch_path}.patchId")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        exact(patch[key], manifest[key], f"{patch_path}.{key}")
    exact(patch["baselineManifestSha256"], manifest["baselineManifestSha256"], f"{patch_path}.baselineManifestSha256")
    exact(patch["compileSnapshotHash"], compiled["snapshotHash"], f"{patch_path}.compileSnapshotHash")
    prior._pins(patch["sourcePins"], patch_path, baseline["sourcePins"])
    exact(prior._runtime_abi_hash(patch["sourcePins"], patch_path), manifest["runtimeAbiHash"], f"{patch_path}.runtimeAbiHash")
    exact(patch["unsigned"], True, f"{patch_path}.unsigned")
    exact(patch["signatureAlgorithm"], "None", f"{patch_path}.signatureAlgorithm")
    exact(patch["dllOnly"], dll_only, f"{patch_path}.dllOnly")
    exact(set(patch["changedRoots"]), set(roots), f"{patch_path}.changedRoots")
    exact(patch["loadOrder"], expected_order, f"{patch_path}.loadOrder")
    exact(fixture["baselineResourceAbiHash"], baseline["resourceAbiHash"], f"{manifest_path}.{patch_id}.baselineResourceAbiHash")
    exact(patch["baselineResourceAbiHash"], baseline["resourceAbiHash"], f"{patch_path}.baselineResourceAbiHash")
    exact(fixture["resourceAbiHash"], patch["resourceAbiHash"], f"{manifest_path}.{patch_id}.resourceAbiHash")
    exact(fixture["resourceChangeLevel"], patch["resourceChangeLevel"], f"{manifest_path}.{patch_id}.resourceChangeLevel")
    exact(fixture["resourceBundlesRequired"], patch["resourceBundlesRequired"], f"{manifest_path}.{patch_id}.resourceBundlesRequired")
    if patch_id == "P05":
        exact(patch["resourceChangeLevel"], "ResourceRebuildRequired", f"{patch_path}.resourceChangeLevel")
        require(patch["resourceAbiHash"] != baseline["resourceAbiHash"] and not patch["dllOnly"],
                f"{patch_path}: P05 did not change structural resource ABI")
        required = m07.names(patch["resourceBundlesRequired"], f"{patch_path}.resourceBundlesRequired")
        require(set(required) <= set(m07.BUNDLES) and required, f"{patch_path}: invalid P05 required bundles")
    else:
        exact(patch["resourceChangeLevel"], "CodeOnly", f"{patch_path}.resourceChangeLevel")
        exact(patch["resourceAbiHash"], baseline["resourceAbiHash"], f"{patch_path}.resourceAbiHash")
        exact(patch["resourceBundlesRequired"], [], f"{patch_path}.resourceBundlesRequired")
        exact(patch["resourceChangeReasons"], [], f"{patch_path}.resourceChangeReasons")

    closure = m07.array(patch["closure"], f"{patch_path}.closure")
    exact([row.get("name") for row in closure], expected_order, f"{patch_path}.closure")
    compiled_by_name = {row["name"]: row for row in compiled.get("assemblies", []) if type(row) is dict}
    baseline_by_name = {row["name"]: row for row in baseline["assemblies"]}
    dlls, pdbs = [], []
    for index, row in enumerate(closure):
        rp = f"{patch_path}.closure[{index}]"
        fields(row, m07.R01_PATCH_ASSEMBLY_FIELDS if capability else m07.PATCH_ASSEMBLY_FIELDS, rp)
        name = row["name"]
        require(name in compiled_by_name and name in baseline_by_name, f"{rp}: unknown closure assembly")
        dll = prior._rel(patch_root, row["dll"], rp, "dll")
        exact(digest(dll), row["sha256"], rp + ".sha256")
        exact(row["sha256"], compiled_by_name[name]["sha256"], rp + ".compilerSha256")
        exact(row["baselineMvid"], baseline_by_name[name]["mvid"], rp + ".baselineMvid")
        pdb = prior._rel(patch_root, row["pdb"], rp, "pdb")
        source_pdb = prior._rel(compile_root, compiled_by_name[name]["pdbPath"], rp, "compiler PDB")
        exact(digest(pdb), row["pdbSha256"], rp + ".pdbSha256")
        exact(row["pdbSha256"], digest(source_pdb), rp + ".compilerPdbSha256")
        if capability:
            m07._uint(row["dllSize"], rp + ".dllSize")
            exact(row["dllSize"], dll.stat().st_size, rp + ".dllSize")
        dlls.append(dll)
        pdbs.append(pdb)
    identities = prior.verify_identities(fixture["assemblyIdentities"], dlls, f"{manifest_path}.{patch_id}.assemblyIdentities")
    for row in closure:
        actual = identities[row["name"]]
        exact(row["mvid"], actual["mvid"], f"{patch_path}.{row['name']}.mvid")
        exact(m07.canonical_names(row["references"], f"{patch_path}.{row['name']}.references"),
              sorted(m07.canonical_names([item["name"] for item in actual["referenceIdentities"]],
                                     f"{patch_path}.{row['name']}.referenceIdentities")),
              f"{patch_path}.{row['name']}.references")
    exact({path.resolve() for path in patch_root.rglob("*.dll")}, {path.resolve() for path in dlls},
          f"{patch_path}: DLL inventory")
    exact({path.resolve() for path in patch_root.rglob("*.pdb")}, {path.resolve() for path in pdbs},
          f"{patch_path}: PDB inventory")
    edges = prior._edges(patch["dependencyGraph"], patch_path)
    closure_set = prior._closure(edges, patch["changedRoots"], {row["name"] for row in baseline["assemblies"]}, patch_path)
    exact(closure_set, set(expected_order), f"{patch_path}: reverse closure")
    prior._verify_topological(expected_order, closure_set, edges, patch_path)
    reflected = prior._reflection_snapshot(compile_root, compiled, patch_path)
    prior._reflection_manifest(patch, reflected, patch_path)
    if capability:
        m07._verify_r01_patch_metadata(patch, closure, patch_root, expected_order, patch_path)
    m07.verify_budget_binding(patch, baseline, patch_path)
    return dict(fixture=fixture, patch=patch, root=patch_root, path=patch_path,
                compile_root=compile_root, compiled=compiled, identities=identities,
                r01Capability=capability)


def verify_failure_fixtures(path, context, fixture_path):
    path = canonical(str(path), Path(path), "failure fixtures")
    data = fields(read(path), RECEIPT_FIELDS, str(path))
    for key, expected in (("schemaVersion", 1), ("kind", "R01FailureFixtures"), ("result", "Passed"),
                          ("sourcePins", context["sourcePins"]), ("replayBytesEqual", True),
                          ("fixtureManifestPath", str(fixture_path)), ("fixtureManifestSha256", digest(fixture_path))):
        exact(data[key], expected, "failure fixtures." + key)
    for key in ("baselineBuildId", "runtimeAbiHash", "baselineManifestPath", "baselineManifestSha256"):
        exact(data[key], context["manifest"][key], "failure fixtures." + key)
    inventory = {}
    for row in data["files"]:
        fields(row, "path sha256 length", "failure fixture file")
        file = bound(row["path"], row["sha256"], path, "failure fixture file")
        require(file.is_relative_to(path.parent) and file != path, "Failure fixture inventory escaped its root")
        exact(file.stat().st_size, row["length"], "failure fixture length")
        require(str(file) not in inventory, "Duplicate failure fixture file")
        inventory[str(file)] = row["sha256"]
    actual = {str(file.resolve()) for file in path.parent.rglob("*") if file.is_file() and file != path}
    exact(set(inventory), actual, "complete failure fixture tree")
    fields(data["initializer"], m07.FIXTURE_FIELDS, "initializer fixture")
    initializer = verify_initializer(data["initializer"], context["manifest"], context["baseline"], path)
    replay = bound(data["replayPatchManifest"], data["replayPatchManifestSha256"], path, "initializer replay")
    exact(digest(replay), digest(initializer["path"]), "initializer replay manifest bytes")
    def tree(root):
        return {str(file.relative_to(root)): digest(file) for file in root.rglob("*") if file.is_file()}
    exact(tree(replay.parent), tree(initializer["root"]), "initializer replay artifact bytes")
    return dict(path=path, data=data, initializer=initializer, files={Path(file) for file in inventory} | {path})


def verify_negative(path, fixture_path, p03):
    # Pure recomputation using the promoted metadata parser; never emit/repair inputs here.
    import r01_negative_inputs as negative
    path = canonical(str(path), Path(path), "negative receipt")
    data = read(path)
    row = next(row for row in p03["patch"]["closure"] if row["name"] == "AssemblyA.Contracts")
    source = prior._rel(p03["root"], row["dll"], path, "Q04 source")
    output = bound(data["outputPath"], data["outputSha256"], path, "Q04 output")
    require(output != source and output.is_relative_to(path.parent), "Q04 output is not a separate confined sidecar")
    original, changed = source.read_bytes(), output.read_bytes()
    mutation = negative.find_mutation(original, str(source))
    expected = bytearray(original); expected[mutation["changedByteOffset"]] = 255
    exact(changed, bytes(expected), "Q04 exact recomputed negative transformation")
    before = negative.identity_projection(negative.read_identity_bytes(original, source))
    after = negative.identity_projection(negative.read_identity_bytes(changed, output))
    exact(before, after, "Q04 identity and AssemblyRefs")
    expected_data = dict(schemaVersion=1, kind="Q04-NegativeMetadataTransform", transformId=negative.TRANSFORM_ID,
        sourceFixture="P03", sourceAssembly="AssemblyA.Contracts", sourceProvenance=negative.provenance_for(fixture_path),
        sourcePath=str(source), outputPath=str(output), sourceSha256=digest(source), outputSha256=digest(output),
        sourceLength=len(original), outputLength=len(changed), lengthPreserved=True, changedByteCount=1,
        identityUnchanged=True, sourcePatchRowMatches=True, sourceIdentity=before, outputIdentity=after,
        mutation=mutation, mutatedByte="ff", originalByte="01", assemblyReferencesUnchanged=True)
    exact(data, expected_data, "Q04 complete transform receipt")
    return dict(path=path, data=data, files={path, source, output})


def prepare(project, fixture_path, on_path, off_path, replay_path, failures_path, negative_path):
    context = verify_inputs(project, fixture_path, on_path, off_path, replay_path)
    profile = metadata_profile(context, "R01 failure")
    if profile == 1:
        r01.require_r01_inputs(context)
    failures = verify_failure_fixtures(failures_path, context, fixture_path)
    negative = verify_negative(negative_path, fixture_path, context["fixtures"]["P03"])
    runner = r01._load_m07_runner()
    inventory = runner.collect_inputs(fixture_path, replay_path, (on_path, off_path)) | failures["files"] | negative["files"]
    return dict(context=context, profile=profile, failures=failures, negative=negative, inventory=inventory, runner=runner)


def raw(row, result_path, label):
    fields(row, RAW_FIELDS, label)
    exact(row["code"], 0, label + ".code")
    r01.integer(row["threadId"], label + ".threadId", 1); r01.integer(row["ticks"], label + ".ticks", 1)
    path = bound(row["rawPath"], row["rawSha256"], result_path, label + ".raw")
    require(path.parent == result_path.parent and path.name.startswith(result_path.stem + ".raw-"), label + ": escaped raw response")
    exact(path.read_text(encoding="utf-8"), row["rawJson"], label + ".rawBytes")
    return m07.json_text(row["rawJson"], label)


def ordinary(value, patch, baseline_id, label, begun=True, profile=1):
    closure = patch["loadOrder"]
    fields(value, m04.R01_DIAGNOSTIC_FIELDS, label)
    m04._diagnostic(value, label, expected_abi=profile)
    exact(value["schemaVersion"], 1, label + ".schemaVersion")
    exact(value["runtimeAbiVersion"], profile, label + ".runtimeAbiVersion")
    exact(value["metadataBudgetCapabilityVersion"], profile, label + ".metadataBudgetCapabilityVersion")
    exact(value["recoveryCapabilityVersion"], 1, label + ".recoveryCapabilityVersion")
    exact(value["startupCandidateSchemaVersion"], 1, label + ".startupCandidateSchemaVersion")
    exact(value["enabled"], True, label + ".enabled")
    exact(value["startupObservationMode"], "EarlyTracking", label + ".startupObservationMode")
    exact(value["startupCandidateNames"], closure, label + ".startupCandidateNames")
    g, e, c = (r01.integer(value[key], label + key) for key in ("generation", "enumerationGeneration", "classEnumerationGeneration"))
    require(0 <= g <= e <= c <= 1, label + ": incoherent generations")
    if not c:
        require(all(not row["usesStagedMetadata"] for row in value["ordinaryClasses"]), label + ": private class leaked")
    for name in closure:
        rows = [row for row in value["ordinaryAssemblies"] if row["name"] == name]
        exact(sum(not row["isInterpreter"] for row in rows), 1, label + ".physicalBaseline." + name)
        exact(sum(row["isInterpreter"] for row in rows), e, label + ".publishedClosure." + name)
    exact(value["baselineUses"], [], label + ".unexpectedBaselineUse")
    # The first main snapshot precedes Configure; every other capture follows
    # Begin. Hash binding alone does not prove which native transaction ran.
    exact(value["baselineBuildId"], baseline_id if begun else "", label + ".baselineBuildId")
    exact(value["patchId"], patch["patchId"] if begun else "", label + ".patchId")
    exact(value["closureLoadOrder"], closure if begun else [], label + ".closureLoadOrder")
    exact(value["expected"], len(closure) if begun else 0, label + ".expected")
    exact([row["name"] for row in value["assemblies"]], closure if begun else [], label + ".assemblies")
    identities = {row["name"]: row["mvid"] for row in patch["closure"]}
    for row in value["assemblies"]:
        exact(row["mvid"], identities[row["name"]] if row["skeletonBuilt"] else "", label + ".mvid." + row["name"])
    exact(value["staged"], sum(row["skeletonBuilt"] for row in value["assemblies"]), label + ".staged")
    return g, e, c


def expected_byte_inputs(mode, prepared):
    context, failures, negative = (prepared[key] for key in ("context", "failures", "negative"))
    fixture = failures["initializer"] if mode == MODES[2] else context["fixtures"]["P03"]
    rows = []
    for row in fixture["patch"]["closure"]:
        source = prior._rel(fixture["root"], row["dll"], fixture["path"], "source DLL")
        actual = Path(negative["data"]["outputPath"]) if mode == MODES[1] and row["name"] == "AssemblyA.Contracts" else source
        rows.append(dict(
            name=row["name"], sourcePath=str(source), sourceSha256=row["sha256"],
            actualPath=str(actual), actualSha256=digest(actual), length=actual.stat().st_size,
            pdbSha256=row["pdbSha256"] or ""))
    return fixture, rows


def _verify_post_host_diagnostics(value, mode, prepared, early):
    context = prepared["context"]
    profile = prepared["profile"]
    fixture, _ = expected_byte_inputs(mode, prepared)
    patch = fixture["patch"]
    closure = patch["loadOrder"]
    fields(value, m04.R01_DIAGNOSTIC_FIELDS, mode + ".postHostDiagnostics")
    m04._diagnostic(value, mode + ".postHostDiagnostics", expected_abi=profile)

    expected_state = "Committed" if mode == MODES[0] else "Failed" if mode == MODES[1] else "FailedAfterCommit"
    expected_state_code = 6 if mode == MODES[0] else 8 if mode == MODES[1] else 9
    expected_generation = 0 if mode == MODES[1] else 1
    expected_last_error = 0 if mode == MODES[0] else 2 if mode == MODES[1] else 18

    for key, expected in (
        ("enabled", True), ("runtimeAbiVersion", profile),
        ("metadataBudgetCapabilityVersion", profile), ("recoveryCapabilityVersion", 1),
        ("startupCandidateSchemaVersion", 1), ("startupObservationMode", "EarlyTracking"),
        ("startupCandidateNames", context["manifest"]["candidateNames"]),
        ("state", expected_state), ("stateCode", expected_state_code),
        ("lastError", expected_last_error),
        ("baselineBuildId", context["manifest"]["baselineBuildId"]),
        ("patchId", patch["patchId"]), ("closureLoadOrder", closure),
        ("expected", len(closure)), ("staged", len(closure)),
        ("generation", expected_generation), ("enumerationGeneration", expected_generation),
        ("classEnumerationGeneration", expected_generation),
    ):
        exact(value[key], expected, mode + ".postHost." + key)

    require(value["retainedBytes"] >= sum(row["length"] for row in expected_byte_inputs(mode, prepared)[1]),
            mode + ".postHost.retainedBytes")
    exact([row["name"] for row in value["assemblies"]], closure, mode + ".postHost.assemblies")
    by_name = {row["name"]: row for row in patch["closure"]}
    published = mode != MODES[1]
    for row in value["assemblies"]:
        source = by_name[row["name"]]
        exact(row["mvid"], source["mvid"], mode + ".postHost.mvid." + row["name"])
        exact(row["skeletonBuilt"], True, mode + ".postHost.skeleton." + row["name"])
        exact(row["runtimeMetadataInitialized"], mode != MODES[1],
              mode + ".postHost.metadata." + row["name"])
        exact(row["published"], published, mode + ".postHost.published." + row["name"])

    early_final = early["snapshots"][-1]["diagnostics"]
    import r01_early_results as early_gate
    early_gate.verify_first_use_history(
        value["baselineUses"], early_final["baselineUses"], early["capsule"],
        mode + ".postHost.firstUseHistory")
    if published:
        # Any post-publication physical baseline use would seal the runtime and
        # contradict the required Committed/FailedAfterCommit state.
        exact(value["baselineUses"], early_final["baselineUses"], mode + ".postHost.noLateBaselineUse")
    return value


def verify_handoff_result(path, mode, prepared, early, capsule_path, early_path):
    path = canonical(str(path), Path(path), "failure handoff result")
    result = fields(read(path), RESULT_FIELDS, str(path))
    context, failures, negative = (prepared[key] for key in ("context", "failures", "negative"))
    manifest, build = context["manifest"], context["on"]
    fixture, expected_inputs = expected_byte_inputs(mode, prepared)
    closure = fixture["patch"]["loadOrder"]

    expected = dict(
        schemaVersion=2, kind="R01FailureHandoffResult", mode=mode, result="Passed", error="",
        resultPath=str(path), unityVersion=manifest["unityVersion"], platform="OSXPlayer",
        buildGuid=build["player"]["buildGuid"], baselineBuildId=manifest["baselineBuildId"],
        runtimeAbiHash=manifest["runtimeAbiHash"],
        fixtureManifestPath=failures["data"]["fixtureManifestPath"],
        fixtureManifestSha256=failures["data"]["fixtureManifestSha256"],
        playerBuildReceiptPath=str(build["path"]), playerBuildReceiptSha256=digest(build["path"]),
        baselineManifestPath=manifest["baselineManifestPath"],
        baselineManifestSha256=manifest["baselineManifestSha256"],
        failureFixturesPath=str(failures["path"]), failureFixturesSha256=digest(failures["path"]),
        negativeInputPath=str(negative["path"]), negativeInputSha256=digest(negative["path"]),
        patchId=fixture["patch"]["patchId"], patchManifestPath=str(fixture["path"]),
        patchManifestSha256=digest(fixture["path"]),
        nativeLibrarySha256=build["player"]["nativeLibrarySha256"],
        nativeMetadataSha256=build["player"]["nativeMetadataSha256"],
        inputSnapshotHash=build["player"]["inputSnapshotHash"], il2cpp=True,
        closureLoadOrder=closure, orderedSizes=[row["length"] for row in expected_inputs],
        byteInputs=expected_inputs, earlyMode=early_mode(mode),
        earlyReceiptPath=str(early_path), earlyReceiptSha256=digest(early_path),
        capsulePath=str(capsule_path), capsuleSha256=digest(capsule_path),
    )
    for key, wanted in expected.items():
        exact(result[key], wanted, mode + "." + key)

    pid = r01.integer(result["processId"], mode + ".processId", 1)
    exact(pid, early["pid"], mode + ".sameProcess")
    r01.integer(result["mainThreadId"], mode + ".mainThreadId", 1)
    data_path = canonical(result["playerDataPath"], path, mode + ".playerDataPath", True)
    require(data_path.is_relative_to(build["output"]), mode + ": result came from a different Player")

    diagnostics = raw(result["postHostDiagnostics"], path, mode + ".postHostDiagnostics")
    capacity = raw(result["postHostCapacity"], path, mode + ".postHostCapacity")
    recovery = raw(result["postHostRecovery"], path, mode + ".postHostRecovery")
    _verify_post_host_diagnostics(diagnostics, mode, prepared, early)

    # Host continuation must not mutate the process-lifetime metadata ledger or
    # durable recovery classification established by the early transaction.
    exact(capacity, early["snapshots"][-1]["capacity"], mode + ".postHost.capacityStable")
    exact(recovery, early["snapshots"][-1]["recovery"], mode + ".postHost.recoveryStable")
    exact(result["postHostDiagnostics"]["threadId"], result["mainThreadId"], mode + ".postHost.diagThread")
    exact(result["postHostCapacity"]["threadId"], result["mainThreadId"], mode + ".postHost.capacityThread")
    exact(result["postHostRecovery"]["threadId"], result["mainThreadId"], mode + ".postHost.recoveryThread")

    raw_paths = [
        result["postHostDiagnostics"]["rawPath"],
        result["postHostCapacity"]["rawPath"],
        result["postHostRecovery"]["rawPath"],
    ]
    require(len(set(raw_paths)) == 3, mode + ": post-host raw responses reused")
    exact({str(file) for file in path.parent.glob(path.stem + ".raw-*.json")},
          set(raw_paths), mode + ".completePostHostRawInventory")
    return dict(mode=mode, result="Passed", processId=pid,
                earlyMode=early_mode(mode), postHostState=diagnostics["state"])


def admission_binding(prepared, mode, paths):
    require(mode in MODES, "Unknown failure/publication mode")
    context = prepared["context"]
    return dict(
        schemaVersion=2,
        kind=EARLY_BINDING_KIND,
        failureMode=mode,
        earlyMode=early_mode(mode),
        baselineBuildId=context["manifest"]["baselineBuildId"],
        runtimeAbiHash=context["manifest"]["runtimeAbiHash"],
        fixtureManifestPath=str(paths["fixtureManifestPath"]),
        fixtureManifestSha256=digest(paths["fixtureManifestPath"]),
        onBuildReceiptPath=str(context["on"]["path"]),
        onBuildReceiptSha256=digest(context["on"]["path"]),
        failureFixturesPath=str(paths["failureFixturesPath"]),
        failureFixturesSha256=digest(paths["failureFixturesPath"]),
        negativeInputPath=str(paths["negativeInputPath"]),
        negativeInputSha256=digest(paths["negativeInputPath"]),
        sourcePins=context["sourcePins"],
    )


def admission_capsule(prepared, mode, paths, binding_path):
    binding_path = Path(binding_path)
    extras = set(prepared["failures"]["files"]) | set(prepared["negative"]["files"]) | {binding_path}
    replacement = {
        "initializer": prepared["failures"]["initializer"],
        "negative": prepared["negative"],
    }
    return early_capsule.from_context(
        prepared["context"], early_mode(mode), "P03", paths["fixtureManifestPath"],
        replacement=replacement, extra_prerequisites=extras)


def materialize_admission_inputs(prepared, paths, root):
    root = Path(root)
    require(root.is_absolute() and root == root.resolve() and root.is_dir() and not root.is_symlink(),
            "Early transaction root must be a canonical directory")
    require(not any(root.iterdir()), "Early transaction root must be empty")
    result = {}
    for mode in MODES:
        binding_path = root / (mode + ".binding.json")
        binding = admission_binding(prepared, mode, paths)
        binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        capsule_path = root / (mode + ".capsule")
        receipt = early_capsule.write_capsule(
            capsule_path, admission_capsule(prepared, mode, paths, binding_path))
        result[mode] = dict(bindingPath=binding_path, bindingSha256=digest(binding_path),
                            capsulePath=capsule_path, capsuleSha256=receipt["sha256"])
    return result


def verify_admission_binding(path, mode, prepared, paths):
    path = canonical(str(path), Path(path), mode + ".earlyBinding")
    exact(read(path), admission_binding(prepared, mode, paths), mode + ".earlyBinding")
    return path


def verify_admission_capsule(path, mode, binding_path, prepared, paths):
    path = canonical(str(path), Path(path), mode + ".earlyCapsule")
    actual = early_capsule.decode(path.read_bytes())
    exact(actual, admission_capsule(prepared, mode, paths, binding_path), mode + ".earlyCapsule")
    exact(actual["mode"], early_mode(mode), mode + ".earlyCapsuleMode")
    return path


def command_for(prepared, mode, paths, capsule_path, early_result_path, result_path, log_path):
    build = prepared["context"]["on"]
    return [str(prepared["runner"].executable_for(build["output"])), "-batchmode", "-nographics",
        "-shadowEarlyCapsule", str(capsule_path), "-shadowEarlyCapsuleSha256", digest(capsule_path),
        "-shadowEarlyResult", str(early_result_path),
        "-shadowR01FailureMode", mode,
        "-shadowM07Fixtures", str(paths["fixtureManifestPath"]), "-shadowM07PlayerReceipt", str(build["path"]),
        "-shadowR01FailureFixtures", str(paths["failureFixturesPath"]), "-shadowR01NegativeInput", str(paths["negativeInputPath"]),
        "-shadowR01FailureResult", str(result_path), "-logFile", str(log_path)]


def verify_suite(launch_path):
    import r01_early_results as early_gate

    launch_path = canonical(str(launch_path), Path(launch_path), "failure launch")
    launch = fields(read(launch_path), LAUNCH_FIELDS, "failure launch")
    for key, expected in (("schemaVersion", 3), ("kind", "R01FailureLaunches"),
                          ("modes", list(MODES)), ("inputsUnchanged", True)):
        exact(launch[key], expected, "launch." + key)
    paths = {key: canonical(launch[key], launch_path, key, key == "projectRoot") for key in
             ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath",
              "replayReceiptPath", "failureFixturesPath", "negativeInputPath")}
    prepared = prepare(*(paths[key] for key in
                         ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath",
                          "replayReceiptPath", "failureFixturesPath", "negativeInputPath")))
    exact(launch["sourcePins"], prepared["context"]["sourcePins"], "launch.sourcePins")
    result_dir = canonical(launch["resultDirectory"], launch_path, "result directory", True)
    exact(result_dir, launch_path.parent / "Results", "result directory confinement")
    capsule_dir = canonical(launch["capsuleDirectory"], launch_path, "capsule directory", True)
    exact(capsule_dir, launch_path.parent / "EarlyTransactions", "capsule directory confinement")

    rows = launch["processLaunches"]
    exact([row["mode"] for row in rows], list(MODES), "complete ordered process matrix")
    require(len({r01.integer(row["processId"], "pid", 1) for row in rows}) == len(MODES),
            "Failure modes did not use fresh processes")

    transaction_files = set()
    admissions = {}
    for index, row in enumerate(rows):
        fields(row, PROCESS_FIELDS, f"launch.process[{index}]")
        mode = row["mode"]
        binding = bound(row["earlyBindingPath"], row["earlyBindingSha256"], launch_path, mode + ".earlyBinding")
        exact(binding, capsule_dir / (mode + ".binding.json"), mode + ".earlyBindingPath")
        verify_admission_binding(binding, mode, prepared, paths)
        capsule_path = bound(row["capsulePath"], row["capsuleSha256"], launch_path, mode + ".earlyCapsule")
        exact(capsule_path, capsule_dir / (mode + ".capsule"), mode + ".earlyCapsulePath")
        verify_admission_capsule(capsule_path, mode, binding, prepared, paths)
        admissions[mode] = (binding, capsule_path)
        transaction_files.update((binding, capsule_path))

    inventory = {str(path): digest(path) for path in sorted(set(prepared["inventory"]) | transaction_files)}
    exact(launch["inputHashesBefore"], inventory, "launch.completeInventory")
    exact(launch["inputHashesAfter"], inventory, "launch.inputsUnchanged")

    results = []
    for row in rows:
        mode = row["mode"]
        exact(row["exitCode"], 0, mode + ".exitCode")
        exact(row["timedOut"], False, mode + ".timedOut")
        exact(row["passed"], True, mode + ".passed")
        exact(row["error"], "", mode + ".error")
        require(isinstance(row["startedAtUnix"], (int, float)) and row["startedAtUnix"] > 0 and
                isinstance(row["durationSeconds"], (int, float)) and row["durationSeconds"] > 0,
                "Missing process timing")

        binding, capsule_path = admissions[mode]
        early_path = bound(row["earlyResultPath"], row["earlyResultSha256"], launch_path, mode + ".earlyResult")
        exact(early_path, result_dir / (mode + ".early.json"), mode + ".earlyResultPath")
        early = early_gate.verify_early_receipt(
            early_path, capsule_path, early_mode(mode), row["processId"], prepared["profile"])
        exact(early["capsule"], admission_capsule(prepared, mode, paths, binding), mode + ".earlyTransaction")
        exact(early["receipt"]["callbackReturnCode"], 0, mode + ".earlyCallbackReturnCode")
        exact(early["receipt"]["result"], expected_early_result(mode), mode + ".earlyResult")

        path = bound(row["resultPath"], row["resultSha256"], launch_path, mode + ".result")
        exact(path, result_dir / (mode + ".json"), mode + ".resultPath")
        log_path = bound(row["logPath"], row["logSha256"], launch_path, mode + ".log")
        console_path = bound(row["consolePath"], row["consoleSha256"], launch_path, mode + ".console")
        exact(log_path, launch_path.parent / (mode + ".unity.log"), mode + ".logPath")
        exact(console_path, launch_path.parent / (mode + ".console.log"), mode + ".consolePath")
        exact(row["command"], command_for(prepared, mode, paths, capsule_path, early_path, path, log_path),
              mode + ".exactExecutedCommand")
        exact(read(path)["processId"], row["processId"], mode + ".producerProcessIdentity")
        result = verify_handoff_result(path, mode, prepared, early, capsule_path, early_path)
        result["earlyBinding"] = str(binding)
        result["earlyBindingSha256"] = digest(binding)
        results.append(result)

    return dict(schemaVersion=3, kind="R01FailureVerification", result="Passed",
                launchReceipt=str(launch_path), launchReceiptSha256=digest(launch_path),
                sourcePins=prepared["context"]["sourcePins"],
                transactionOwnership="EarliestStartup",
                modes=results)



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    require(not args.output.exists() and args.output.parent.is_dir(), "Use a fresh verifier output path")
    try:
        result = verify_suite(args.launch_receipt)
    except Exception as error:
        result = dict(schemaVersion=3, kind="R01FailureVerification", result="Failed", error=str(error))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return int(result["result"] != "Passed")


if __name__ == "__main__":
    raise SystemExit(main())
