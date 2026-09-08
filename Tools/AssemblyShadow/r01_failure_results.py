"""Strict provenance and raw-runtime gate for the separate R01 failure matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import m07_results as m07
import m04_results as m04
import r01_results as r01
from r00_player_inputs import verify_inputs
from shadow_tools import require

MODES = ("R01-Failure-P03-Control", "R01-Failure-Q04-Metadata", "R01-Failure-InitializerThrow")
INITIALIZER_ID = "R01-P03-InitializerThrow"
DEFINES = ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M03_INITIALIZERS",
           "ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_M03_INITIALIZER_THROW"]
RESULT_FIELDS = "schemaVersion kind mode result error resultPath processId mainThreadId unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineManifestPath baselineManifestSha256 failureFixturesPath failureFixturesSha256 negativeInputPath negativeInputSha256 patchId patchManifestPath patchManifestSha256 nativeLibrarySha256 nativeMetadataSha256 inputSnapshotHash il2cpp observerJoined closureLoadOrder observerErrors orderedSizes byteInputs operations diagnostics capacities recovery observerSamples initializerEvents"
RAW_FIELDS = "phase rawJson rawPath rawSha256 code threadId ticks"
RECEIPT_FIELDS = "schemaVersion kind result sourcePins baselineManifestPath baselineManifestSha256 baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 initializer replayPatchManifest replayPatchManifestSha256 replayBytesEqual files"
LAUNCH_FIELDS = "schemaVersion kind projectRoot fixtureManifestPath onBuildReceiptPath offBuildReceiptPath replayReceiptPath failureFixturesPath negativeInputPath sourcePins modes processLaunches resultDirectory inputHashesBefore inputHashesAfter inputsUnchanged"
read, exact, fields, digest, bound, canonical = r01.read, r01.exact, r01.fields, r01.digest, r01.bound, r01.canonical
prior = m07.prior


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
    capability = m07._schema_variant(patch, m07.PATCH_FIELDS, m07.R01_PATCH_FIELDS, patch_path)
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
    r01.require_r01_inputs(context)
    failures = verify_failure_fixtures(failures_path, context, fixture_path)
    negative = verify_negative(negative_path, fixture_path, context["fixtures"]["P03"])
    runner = r01._load_m07_runner()
    inventory = runner.collect_inputs(fixture_path, replay_path, (on_path, off_path)) | failures["files"] | negative["files"]
    return dict(context=context, failures=failures, negative=negative, inventory=inventory, runner=runner)


def raw(row, result_path, label):
    fields(row, RAW_FIELDS, label)
    exact(row["code"], 0, label + ".code")
    r01.integer(row["threadId"], label + ".threadId", 1); r01.integer(row["ticks"], label + ".ticks", 1)
    path = bound(row["rawPath"], row["rawSha256"], result_path, label + ".raw")
    require(path.parent == result_path.parent and path.name.startswith(result_path.stem + ".raw-"), label + ": escaped raw response")
    exact(path.read_text(encoding="utf-8"), row["rawJson"], label + ".rawBytes")
    return m07.json_text(row["rawJson"], label)


def ordinary(value, patch, baseline_id, label, begun=True):
    closure = patch["loadOrder"]
    fields(value, m04.R01_DIAGNOSTIC_FIELDS, label)
    m04._diagnostic(value, label)
    for key in ("schemaVersion", "runtimeAbiVersion", "metadataBudgetCapabilityVersion", "recoveryCapabilityVersion", "startupCandidateSchemaVersion"):
        exact(value[key], 1, label + "." + key)
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


def verify_result(path, mode, prepared):
    path = canonical(str(path), Path(path), "result")
    result = fields(read(path), RESULT_FIELDS, str(path))
    context, failures, negative = (prepared[key] for key in ("context", "failures", "negative"))
    manifest, build = context["manifest"], context["on"]
    fixture = failures["initializer"] if mode == MODES[2] else context["fixtures"]["P03"]
    closure = fixture["patch"]["loadOrder"]
    for key, expected in dict(schemaVersion=1, kind="R01FailureResult", mode=mode, result="Passed", error="", resultPath=str(path),
        il2cpp=True, observerJoined=True, observerErrors=[], closureLoadOrder=closure, unityVersion=manifest["unityVersion"],
        platform="OSXPlayer", buildGuid=build["player"]["buildGuid"], baselineBuildId=manifest["baselineBuildId"], runtimeAbiHash=manifest["runtimeAbiHash"],
        fixtureManifestPath=failures["data"]["fixtureManifestPath"], fixtureManifestSha256=failures["data"]["fixtureManifestSha256"],
        playerBuildReceiptPath=str(build["path"]), playerBuildReceiptSha256=digest(build["path"]),
        baselineManifestPath=manifest["baselineManifestPath"], baselineManifestSha256=manifest["baselineManifestSha256"],
        failureFixturesPath=str(failures["path"]), failureFixturesSha256=digest(failures["path"]), negativeInputPath=str(negative["path"]),
        negativeInputSha256=digest(negative["path"]), patchId=fixture["patch"]["patchId"], patchManifestPath=str(fixture["path"]),
        patchManifestSha256=digest(fixture["path"]), nativeLibrarySha256=build["player"]["nativeLibrarySha256"],
        nativeMetadataSha256=build["player"]["nativeMetadataSha256"], inputSnapshotHash=build["player"]["inputSnapshotHash"]).items():
        exact(result[key], expected, mode + "." + key)
    r01.integer(result["processId"], "result.processId", 1); r01.integer(result["mainThreadId"], "result.mainThreadId", 1)
    data_path = canonical(result["playerDataPath"], path, "Player data", True)
    require(data_path.is_relative_to(build["output"]), "Result came from a different Player")
    expected_inputs = []
    for row in fixture["patch"]["closure"]:
        source = prior._rel(fixture["root"], row["dll"], path, "source DLL")
        actual = Path(negative["data"]["outputPath"]) if mode == MODES[1] and row["name"] == "AssemblyA.Contracts" else source
        expected_inputs.append(dict(name=row["name"], sourcePath=str(source), sourceSha256=row["sha256"], actualPath=str(actual),
            actualSha256=digest(actual), length=actual.stat().st_size, pdbSha256=row["pdbSha256"] or ""))
    exact(result["byteInputs"], expected_inputs, "actual Stage bytes")
    sizes = [row["length"] for row in expected_inputs]; exact(result["orderedSizes"], sizes, "ordered reservation sizes")
    q04, initializer = mode == MODES[1], mode == MODES[2]
    terminal, state, state_code = (13, "Failed", 8) if q04 else (19, "FailedAfterCommit", 9) if initializer else (0, "Committed", 6)
    codes = [("configure", 0, "Success"), ("begin", 0, "Success"), ("reserve", 0, "Success")]
    codes += [("stage:" + name, 0, "Success") for name in closure]
    codes += [("validate", 13 if q04 else 0, "ReferenceResolutionFailed" if q04 else "Success")]
    if not q04: codes += [("commit", terminal, "ModuleInitializerFailed" if initializer else "Success")]
    if terminal: codes += [("abort-rejected", 2 if q04 else 18, "InvalidState" if q04 else "AlreadyCommitted"),
                            ("begin-rejected", 2 if q04 else 18, "InvalidState" if q04 else "AlreadyCommitted")]
    exact(result["operations"], [dict(operation=op, code=code, name=name) for op, code, name in codes], "ordered runtime operations")
    phases = ["before-reserve", "after-reserve", "after-stage", "after-validate"]
    if not q04: phases += ["after-commit"]
    if terminal: phases += ["after-rejected-operations"]
    parsed = {}
    raw_paths = []
    for group in ("diagnostics", "capacities", "recovery"):
        exact([row["phase"] for row in result[group]], phases, group + " phases")
        parsed[group] = [raw(row, path, group + "." + row["phase"]) for row in result[group]]
        raw_paths += [row["rawPath"] for row in result[group]]
        require(all(row["threadId"] == result["mainThreadId"] for row in result[group]), "Main snapshots used another thread")
        require([row["ticks"] for row in result[group]] == sorted(row["ticks"] for row in result[group]), "Snapshot time regressed")
    for i, value in enumerate(parsed["diagnostics"]):
        ordinary(value, fixture["patch"], manifest["baselineBuildId"], "diagnostics." + phases[i], begun=i > 0)
        expected_state = ("Disabled", "Staging", "Staged", "Failed" if q04 else "Validated")[i] if i < 4 else state
        exact(value["state"], expected_state, "diagnostic state")
        if i < 2: exact(value["retainedBytes"], 0, "premature retained owner")
        else:
            require(value["retainedBytes"] >= sum(sizes), "Stage did not retain real DLL owners")
            exact(value["staged"], len(closure), "incomplete staged closure")
            exact([row["name"] for row in value["assemblies"]], closure, "diagnostic closure")
            require(all(row["skeletonBuilt"] for row in value["assemblies"]), "Missing genuine skeleton")
        published = not q04 and phases[i] in ("after-commit", "after-rejected-operations")
        exact(value["generation"], int(published), "diagnostic publication")
        if i >= 2: exact([row["published"] for row in value["assemblies"]], [published] * len(closure), "atomic publication")
        if not published: require(not any(row["moduleInitializerAttempted"] for row in value["assemblies"]), "Private initializer ran")
        if phases[i] in ("after-validate", "after-commit", "after-rejected-operations") and not q04:
            require(all(row["runtimeMetadataInitialized"] for row in value["assemblies"]), "Uninitialized publication metadata")
    if q04:
        failure = parsed["diagnostics"][3]
        exact(failure["lastError"], 13, "Q04 exact failure")
        require(all(not row["runtimeMetadataInitialized"] for row in failure["assemblies"]), "Q04 failure did not stop at the first provider")
        require(failure["detail"].startswith("AssemblyA.Contracts:") and "Image::ReadType invalid type" in failure["detail"],
                "Q04 did not fail at the intended production method-signature parser")
        exact([(row["name"], row["stagedCount"]) for row in failure["events"] if row["kind"] == "metadata-begin"],
              [("AssemblyA.Contracts", len(closure))], "Q04 real metadata initializer entry")
        require(not any(row["kind"] == "metadata-ready" for row in failure["events"]), "Q04 reported completed provider metadata")
    if initializer: exact(parsed["diagnostics"][-2]["lastError"], 19, "initializer exact failure")
    capacities = parsed["capacities"]
    for value in capacities:
        fields(value, "schemaVersion enabled profileVersion indexBits kindBits cursors remainingSlots requiredImages acceptedImages firstFailingIndex firstFailingSize failureReason fits allocations finalCursors ordinaryAllocatedCount shadowAllocatedCount reservedImageCount", "capacity raw")
        model = r01.evaluate_budget(value["cursors"], sizes)
        for key in model: exact(value[key], model[key], "capacity dry-run." + key)
        exact(value["remainingSlots"], r01.remaining_slots(value["cursors"]), "capacity remaining slots")
        for key, expected in (("schemaVersion", 1), ("enabled", True), ("profileVersion", 1), ("indexBits", 22), ("kindBits", 2)):
            exact(value[key], expected, "capacity." + key)
    exact(capacities[1]["cursors"], capacities[0]["finalCursors"], "reservation advanced exact planned cursors")
    exact(capacities[1]["reservedImageCount"], capacities[0]["reservedImageCount"] + len(sizes), "complete reserved budget")
    for value in capacities[1:]:
        exact(value["cursors"], capacities[1]["cursors"], "retained budget cursor cannot roll back")
        exact(value["ordinaryAllocatedCount"], capacities[0]["ordinaryAllocatedCount"], "unexpected ordinary image")
        exact(value["reservedImageCount"], capacities[1]["reservedImageCount"], "reservation discarded")
    for value in capacities[2:]: exact(value["shadowAllocatedCount"], capacities[1]["shadowAllocatedCount"] + len(sizes), "staged reserved slots consumed exactly once")
    for value in parsed["recovery"]:
        fields(value, "schemaVersion enabled capabilityVersion stateCode state published abortAllowed dispositionCode disposition terminalFailureCode reason retainedBytes baselineEligibilityRequiresStartupValidation", "recovery raw")
        for key in ("enabled", "published", "abortAllowed", "baselineEligibilityRequiresStartupValidation"): r01.boolean(value[key], "recovery." + key)
        r01.integer(value["retainedBytes"], "recovery.retainedBytes")
    for value in parsed["diagnostics"][2:]:
        exact(value["retainedBytes"], parsed["diagnostics"][2]["retainedBytes"], "retained owner lifetime")
    terminal_index = phases.index("after-validate" if q04 else "after-commit")
    for value in parsed["recovery"][terminal_index:]:
        for key, expected in dict(schemaVersion=1, enabled=True, capabilityVersion=1, state=state, stateCode=state_code,
            published=not q04, abortAllowed=False, disposition="RestartRequired" if terminal else "ActiveShadow",
            dispositionCode=0 if terminal else 4, terminalFailureCode=terminal, baselineEligibilityRequiresStartupValidation=bool(terminal)).items():
            exact(value[key], expected, "durable recovery." + key)
        require(value["retainedBytes"] >= sum(sizes), "Recovery lost genuine owner retention")
        if terminal:
            expected_reason = "Image::ReadType invalid type" if q04 else "M03-INIT-THROW:AssemblyA.Implementation.Internal"
            require(expected_reason in value["reason"], "Terminal recovery lost the actual injected failure reason")
    if terminal:
        exact(parsed["recovery"][-1], parsed["recovery"][terminal_index], "rejected operations rewrote terminal recovery")
    samples = result["observerSamples"]
    require(samples and {row["phase"] for row in samples} == {"before", "after"}, "Missing actual observer samples on both sides")
    require(len(samples) <= 32 and len({row["threadId"] for row in samples}) == 1 and samples[0]["threadId"] != result["mainThreadId"], "Observer did not execute on a separate bounded thread")
    previous = (0, 0, 0)
    for row in samples:
        value = raw(row, path, "observer"); raw_paths.append(row["rawPath"])
        current = ordinary(value, fixture["patch"], manifest["baselineBuildId"], "observer")
        require(all(a <= b for a, b in zip(previous, current)), "Observer generations regressed"); previous = current
        if row["phase"] == "after": exact(value["state"], state, "observer final state"); exact(current, (0, 0, 0) if q04 else (1, 1, 1), "observer final publication")
    require(any(raw(row, path, "observer initial")["enumerationGeneration"] == 0 for row in samples if row["phase"] == "before"), "No actual pre-publication sample")
    if initializer:
        attempted = closure[:closure.index("AssemblyA.Implementation.Internal") + 1]
        exact([row["name"] for row in result["initializerEvents"]], attempted, "actual throwing initializer order")
        for row in result["initializerEvents"]:
            value = raw(row["diagnostics"], path, "initializer reentrant"); raw_paths.append(row["diagnostics"]["rawPath"])
            exact(value["state"], "Committing", "initializer reentrant state"); exact(ordinary(value, fixture["patch"], manifest["baselineBuildId"], "initializer"), (1, 1, 1), "initializer complete publication")
        final_rows = parsed["diagnostics"][-1]["assemblies"]
        exact([row["moduleInitializerAttempted"] for row in final_rows], [name in attempted for name in closure], "initializer attempts")
        exact([row["moduleInitializerRan"] for row in final_rows], [name in attempted[:-1] for name in closure], "initializer completion")
    else: exact(result["initializerEvents"], [], "unexpected initializer fixture")
    require(len(set(raw_paths)) == len(raw_paths), "Raw responses reused across observations")
    exact({str(file) for file in path.parent.glob(path.stem + ".raw-*.json")}, set(raw_paths), "complete raw response inventory")
    return dict(mode=mode, state=state, terminalFailureCode=terminal, result="Passed", processId=result["processId"], observerSamples=len(samples))


def command_for(prepared, mode, paths, result_path, log_path):
    build = prepared["context"]["on"]
    return [str(prepared["runner"].executable_for(build["output"])), "-batchmode", "-nographics", "-shadowR01FailureMode", mode,
        "-shadowM07Fixtures", str(paths["fixtureManifestPath"]), "-shadowM07PlayerReceipt", str(build["path"]),
        "-shadowR01FailureFixtures", str(paths["failureFixturesPath"]), "-shadowR01NegativeInput", str(paths["negativeInputPath"]),
        "-shadowR01FailureResult", str(result_path), "-logFile", str(log_path)]


def verify_suite(launch_path):
    launch_path = canonical(str(launch_path), Path(launch_path), "failure launch")
    launch = fields(read(launch_path), LAUNCH_FIELDS, "failure launch")
    for key, expected in (("schemaVersion", 1), ("kind", "R01FailureLaunches"), ("modes", list(MODES)), ("inputsUnchanged", True)):
        exact(launch[key], expected, "launch." + key)
    paths = {key: canonical(launch[key], launch_path, key, key == "projectRoot") for key in
             ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath", "replayReceiptPath", "failureFixturesPath", "negativeInputPath")}
    prepared = prepare(*(paths[key] for key in ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath", "replayReceiptPath", "failureFixturesPath", "negativeInputPath")))
    exact(launch["sourcePins"], prepared["context"]["sourcePins"], "launch.sourcePins")
    inventory = {str(path): digest(path) for path in sorted(prepared["inventory"])}
    exact(launch["inputHashesBefore"], inventory, "launch.completeInventory")
    exact(launch["inputHashesAfter"], inventory, "launch.inputsUnchanged")
    result_dir = canonical(launch["resultDirectory"], launch_path, "result directory", True)
    exact(result_dir, launch_path.parent / "Results", "result directory confinement")
    rows = launch["processLaunches"]
    exact([row["mode"] for row in rows], list(MODES), "complete ordered process matrix")
    require(len({r01.integer(row["processId"], "pid", 1) for row in rows}) == len(MODES), "Failure modes did not use fresh processes")
    results = []
    for row in rows:
        fields(row, "mode command processId startedAtUnix durationSeconds exitCode timedOut passed resultPath resultSha256 logPath consolePath error", "launch process")
        mode = row["mode"]
        exact(row["exitCode"], 0, mode + ".exitCode"); exact(row["timedOut"], False, mode + ".timedOut"); exact(row["passed"], True, mode + ".passed")
        require(isinstance(row["startedAtUnix"], (int, float)) and row["startedAtUnix"] > 0 and
                isinstance(row["durationSeconds"], (int, float)) and row["durationSeconds"] > 0, "Missing process timing")
        path = bound(row["resultPath"], row["resultSha256"], launch_path, mode + ".result")
        exact(path, result_dir / (mode + ".json"), "result path")
        exact(row["logPath"], str(launch_path.parent / (mode + ".unity.log")), "Unity log path")
        exact(row["consolePath"], str(launch_path.parent / (mode + ".console.log")), "console path")
        for key in ("logPath", "consolePath"): canonical(row[key], launch_path, key)
        exact(row["command"], command_for(prepared, mode, paths, path, Path(row["logPath"])), "exact executed command")
        exact(read(path)["processId"], row["processId"], "producer/process identity")
        results.append(verify_result(path, mode, prepared))
    return dict(schemaVersion=1, kind="R01FailureVerification", result="Passed", launchReceipt=str(launch_path),
                launchReceiptSha256=digest(launch_path), sourcePins=prepared["context"]["sourcePins"], modes=results)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    require(not args.output.exists() and args.output.parent.is_dir(), "Use a fresh verifier output path")
    try:
        result = verify_suite(args.launch_receipt)
    except Exception as error:
        result = dict(schemaVersion=1, kind="R01FailureVerification", result="Failed", error=str(error))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return int(result["result"] != "Passed")
