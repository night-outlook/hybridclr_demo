import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from m02_results import (CASE_IDS, CANDIDATES, M02_CANVAS_ALLOWED_TYPES, NUNIT_SUITES, _reflection_manifest, _reflection_parse, _reflection_snapshot,
                         _retargeting_profile_hash,
                         _resource_abi_hash, _resource_source_set_hash, _runtime_abi_hash,
                         _snapshot_files, _snapshot_hash, _snapshot_linked_hash, _verify_linked_player,
                         _verify_builtin_source, _verify_reflection_probe, verify)
from shadow_tools import VerificationError


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class M02EvidenceTests(unittest.TestCase):
    def reflection_fixture(self, root):
        snapshot = root / "Snapshot"
        (snapshot / "Assemblies").mkdir(parents=True)
        dll = snapshot / "Assemblies" / "Consumer.dll"
        dll.write_bytes(b"consumer")
        config = {
            "schemaVersion": 1,
            "transformerVersion": 1,
            "sites": [{
                "id": "site-1", "assembly": "Consumer", "typeName": "Demo.Type",
                "methodSignature": "System.Void Demo.Type::Method()", "originalMethodHash": "a" * 64,
                "operationIndex": 0, "allowedTypes": [], "reason": "finite target contract",
            }],
        }
        config_path = snapshot / "ReflectionBindings" / "configuration.json"
        config_path.parent.mkdir()
        config_path.write_text(json.dumps(config, separators=(",", ":")))
        receipt = {
            "schemaVersion": 1, "kind": "CompilePlayerScripts", "extraScriptingDefines": [],
            "assemblies": [{"name": "Consumer", "path": "Assemblies/Consumer.dll", "sha256": sha(dll)}],
        }
        return snapshot, config, receipt, config_path

    def reflection_probe_fixture(self, root):
        output = root / "Player.app"
        staged = output / "Contents" / "Resources" / "Data" / "StreamingAssets" / "AssemblyShadow" / "M02" / "reflection-bindings.json"
        staged.parent.mkdir(parents=True)
        allowed = [f"Demo.Type{index:02d}, Provider{index:02d}" for index in range(26)]
        config = {
            "schemaVersion": 1, "transformerVersion": 1,
            "sites": [
                {"id": "urp-debug-ui-prefab-types", "assembly": "DebugUI", "typeName": "Demo.Canvas",
                 "methodSignature": "System.Void Demo.Canvas::Rebuild()", "originalMethodHash": "a" * 64,
                 "operationIndex": 0, "allowedTypes": allowed, "reason": "finite canvas types"},
                {"id": "urp-serializable-enum-player", "assembly": "Serializable", "typeName": "Demo.Enum",
                 "methodSignature": "System.Void Demo.Enum::Read()", "originalMethodHash": "b" * 64,
                 "operationIndex": 0, "allowedTypes": [], "reason": "deny all enum reflection"},
            ],
        }
        staged.write_text(json.dumps(config, separators=(",", ":")))
        reflection = _reflection_parse(staged, staged.read_bytes())
        receipt = {"unityVersion": "2022.3.62f2", "buildGuid": "player-guid",
                   "playerOutput": str(output)}
        configuration_hash = reflection["canonicalHash"]
        candidate = "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal"
        denied_inputs = {
            "candidate": candidate,
            "generic-provider-escape": "System.Collections.Generic.List`1[[" + candidate + "]], mscorlib",
            "null": None, "unqualified": "UnityEngine.Rendering.DebugUI+Value",
            "unknown": "AssemblyShadowUnknown.Type, AssemblyShadowUnknown",
            "mutated-string": allowed[0] + " ", "runtime-prefab-mutation": candidate,
            "serializable-enum-deny-all": "System.DayOfWeek, mscorlib",
        }
        denied = []
        for name, value in denied_inputs.items():
            site = "urp-serializable-enum-player" if name == "serializable-enum-deny-all" else "urp-debug-ui-prefab-types"
            denied.append({"name": name, "input": value, "inputWasNull": value is None, "denied": True,
                           "exceptionType": "System.InvalidOperationException",
                           "message": "AssemblyShadow reflection denied; configuration=" + configuration_hash + "; site=" + site,
                           "assemblyResolveEvents": 0})
        probe = {"schemaVersion": 1, "milestone": "M02", "mode": "M02ReflectionBindings", "result": "Passed", "il2cpp": True,
                 "unityVersion": receipt["unityVersion"], "platform": "OSXPlayer", "buildGuid": receipt["buildGuid"],
                 "playerDataPath": str(output / "Contents"), "configurationSha256": reflection["rawSha256"],
                 "configurationHash": configuration_hash,
                 "canvasGuard": "__AssemblyShadowReflectionBinding_" + configuration_hash + "_" + hashlib.sha256(config["sites"][0]["id"].encode()).hexdigest(),
                 "enumGuard": "__AssemblyShadowReflectionBinding_" + configuration_hash + "_" + hashlib.sha256(config["sites"][1]["id"].encode()).hexdigest(),
                 "allowed": [{"input": value, "type": value.split(",")[0], "assembly": value.split(",")[1].strip()} for value in sorted(allowed)],
                 "denied": denied, "error": ""}
        probe_path = root / "reflection-result.json"
        probe_path.write_text(json.dumps(probe))
        return probe_path, receipt, reflection, probe

    def linked_reflection_fixture(self, root):
        snapshot, config, receipt, config_path = self.reflection_fixture(root)
        receipt["kind"] = "PlayerBuildInputs"
        receipt.update({"unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64", "buildGuid": "guid"})
        receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
        linked_root = snapshot / "LinkedPlayer" / "Assemblies"
        linked_root.mkdir(parents=True)
        linked_dll = linked_root / "consumer.dll"
        linked_dll.write_bytes(b"linked-consumer")
        linked = {
            "schemaVersion": 2, "buildGuid": "guid", "nativeLibrarySha256": "a" * 64,
            "target": "StandaloneOSX", "architecture": "arm64", "sourceDirectory": str(root / "linked-source"),
            "reflectionBindingEvidenceHash": "", "protectedAssemblies": [],
            "assemblies": [{"name": "consumer", "path": "Assemblies/consumer.dll", "sha256": sha(linked_dll),
                            "mvid": "00000000-0000-0000-0000-000000000001", "pdbPath": "", "pdbSha256": ""}],
        }
        receipt["linkedPlayerReceipt"] = linked
        evidence_root = snapshot / "ReflectionBindings" / "LinkedRetargeting"
        evidence_root.mkdir(parents=True)
        facade = evidence_root / "netstandard.dll.bytes"
        facade.write_bytes(b"facade-bytes")
        proof = {
            "schemaVersion": 1, "mappingPolicyVersion": 1, "unityVersion": "2022.3.62f2",
            "target": "StandaloneOSX", "architecture": "arm64", "buildGuid": "guid", "il2cppDotNetProfile": "unityaot-macos",
            "configurationSha256": sha(config_path), "configurationHash": _reflection_parse(config_path, config_path.read_bytes())["canonicalHash"],
            "facadeSourcePath": "/editor/MonoBleedingEdge/lib/mono/unityaot-macos/Facades/netstandard.dll",
            "facadePath": "ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes", "facadeSha256": sha(facade),
            "sourceAssemblyIdentity": "netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51",
            "profileHash": "", "forwarders": [], "runtimeFrameworkModules": [], "sites": [],
        }
        proof["sites"] = [{
            "id": "site-1", "consumer": "Consumer", "compiledPath": "Assemblies/Consumer.dll", "compiledSha256": receipt["assemblies"][0]["sha256"],
            "linkedPath": "LinkedPlayer/Assemblies/consumer.dll", "linkedSha256": sha(linked_dll),
            "methodSignature": config["sites"][0]["methodSignature"], "guardMethod": "__AssemblyShadowReflectionBinding_" + proof["configurationHash"] + "_" + hashlib.sha256(b"site-1").hexdigest(),
            "operationIndex": 0, "compiledMethodHash": "a" * 64, "linkedMethodHash": "b" * 64,
            "compiledGuardHash": "c" * 64, "linkedGuardHash": "d" * 64,
        }]
        proof["profileHash"] = _retargeting_profile_hash(proof, evidence_root / "evidence.json")
        evidence_path = evidence_root / "evidence.json"
        evidence_path.write_text(json.dumps(proof))
        linked["reflectionBindingEvidenceHash"] = sha(evidence_path)
        receipt["linkedPlayerReceiptHash"] = _snapshot_linked_hash(linked)
        (snapshot / "LinkedPlayer" / "linked-player-receipt.json").write_text(json.dumps(linked))
        return snapshot, receipt, config_path, evidence_path

    def reflection_schema2_fixture(self, root):
        snapshot = root / "Snapshot"
        (snapshot / "Assemblies").mkdir(parents=True)
        dll = snapshot / "Assemblies" / "Consumer.dll"
        dll.write_bytes(b"consumer-schema2")
        finite = [
            "UnityEngine.Rendering.Universal.Bloom, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ChannelMixer, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ChromaticAberration, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ColorAdjustments, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ColorCurves, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ColorLookup, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.DepthOfField, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.FilmGrain, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.LensDistortion, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.LiftGammaGain, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.MotionBlur, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.PaniniProjection, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.ShadowsMidtonesHighlights, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.SplitToning, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.Tonemapping, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.Vignette, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            "UnityEngine.Rendering.Universal.WhiteBalance, Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
        ]
        image = (Path(__file__).resolve().parents[3] / "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes").read_bytes()
        image_sha = hashlib.sha256(image).hexdigest()
        config = {"schemaVersion": 2, "transformerVersion": 2, "sites": [
            {"id": "urp-debug-ui-prefab-types", "assembly": "Consumer", "typeName": "Demo.Canvas", "methodSignature": "M1", "originalMethodHash": "a" * 64, "operationIndex": 0, "allowedTypes": sorted(M02_CANVAS_ALLOWED_TYPES), "reason": "canvas", "kind": "TypeGetType"},
            {"id": "urp-serializable-enum-player", "assembly": "Consumer", "typeName": "Demo.Enum", "methodSignature": "M2", "originalMethodHash": "b" * 64, "operationIndex": 0, "allowedTypes": [], "reason": "enum", "kind": "TypeGetType"},
            {"id": "urp-volume-assembly-domain", "assembly": "Consumer", "typeName": "Demo.Volume", "methodSignature": "M3", "originalMethodHash": "c" * 64, "operationIndex": 0, "allowedTypes": finite, "reason": "volume assembly", "kind": "FiniteAssemblyList"},
            {"id": "urp-volume-type-domain", "assembly": "Consumer", "typeName": "Demo.Volume", "methodSignature": "M4", "originalMethodHash": "d" * 64, "operationIndex": 0, "allowedTypes": finite, "reason": "volume type", "kind": "FiniteAssemblyTypes"},
            {"id": "m00-normal-hot-update-image", "assembly": "Consumer", "typeName": "Demo.Image", "methodSignature": "M5", "originalMethodHash": "e" * 64, "operationIndex": 0, "allowedTypes": [], "reason": "fixed image", "kind": "FixedAssemblyBytes", "imageSha256": image_sha, "providerAssemblyIdentity": "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null", "imagePath": "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"},
        ]}
        config_path = snapshot / "ReflectionBindings" / "configuration.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps(config, separators=(",", ":")))
        image_path = snapshot / "ReflectionBindings" / "Images" / (image_sha + ".dll.bytes")
        image_path.parent.mkdir()
        image_path.write_bytes(image)
        receipt = {"schemaVersion": 1, "kind": "CompilePlayerScripts", "extraScriptingDefines": ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)],
                   "assemblies": [{"name": "Consumer", "path": "Assemblies/Consumer.dll", "sha256": sha(dll)}]}
        return snapshot, config, receipt, config_path, image_path

    def reflection_schema2_probe_fixture(self, root):
        snapshot, config, receipt, config_path, image_path = self.reflection_schema2_fixture(root)
        reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
        output = root / "Player.app"
        staged = output / "Contents" / "Resources" / "Data" / "StreamingAssets" / "AssemblyShadow" / "M02" / "reflection-bindings.json"
        staged.parent.mkdir(parents=True)
        staged.write_bytes(config_path.read_bytes())
        receipt.update({"unityVersion": "2022.3.62f2", "buildGuid": "player-guid", "playerOutput": str(output)})
        sites = {site["id"]: site for site in config["sites"]}
        configuration_hash = reflection["canonicalHash"]
        guard = lambda site_id: "__AssemblyShadowReflectionBinding_" + configuration_hash + "_" + hashlib.sha256(site_id.encode()).hexdigest()
        canvas = sites["urp-debug-ui-prefab-types"]
        enum = sites["urp-serializable-enum-player"]
        allowed = [{"input": value, "type": value.split(",")[0], "assembly": value.split(",")[1].strip()}
                   for value in sorted(canvas["allowedTypes"])]
        candidate = "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal"
        denied_inputs = {
            "candidate": candidate,
            "generic-provider-escape": "System.Collections.Generic.List`1[[" + candidate + "]], mscorlib",
            "null": None,
            "unqualified": "UnityEngine.Rendering.DebugUI+Value",
            "unknown": "AssemblyShadowUnknown.Type, AssemblyShadowUnknown",
            "mutated-string": canvas["allowedTypes"][0] + " ",
            "runtime-prefab-mutation": candidate,
            "serializable-enum-deny-all": "System.DayOfWeek, mscorlib",
        }
        denied = []
        for name, value in denied_inputs.items():
            site_id = enum["id"] if name == "serializable-enum-deny-all" else canvas["id"]
            denied.append({"name": name, "input": "" if value is None else value, "inputWasNull": value is None, "denied": True,
                           "exceptionType": "System.InvalidOperationException",
                           "message": "AssemblyShadow reflection denied; configuration=" + configuration_hash + "; site=" + site_id,
                           "assemblyResolveEvents": 0})
        probe = {"schemaVersion": 2, "milestone": "M02", "mode": "M02ReflectionBindings", "result": "Passed", "il2cpp": True,
                 "unityVersion": receipt["unityVersion"], "platform": "OSXPlayer", "buildGuid": receipt["buildGuid"],
                 "playerDataPath": str(output / "Contents"), "configurationSha256": reflection["rawSha256"],
                 "configurationHash": configuration_hash,
                 "canvasGuard": guard(canvas["id"]), "enumGuard": guard(enum["id"]),
                 "finiteAssemblyGuard": guard(sites["urp-volume-assembly-domain"]["id"]),
                 "finiteTypesGuard": guard(sites["urp-volume-type-domain"]["id"]),
                 "fixedImageGuard": guard(sites["m00-normal-hot-update-image"]["id"]),
                 "discoveryAllowedTypes": sorted(sites["urp-volume-type-domain"]["allowedTypes"]),
                 "discoveryAssemblyNames": ["Unity.RenderPipelines.Universal.Runtime"],
                 "discoveryDeniedBeforeEnumeration": True, "volumeManagerMatchesContract": True,
                 "fixedImageSha256": sites["m00-normal-hot-update-image"]["imageSha256"],
                 "fixedImageLoadedAssembly": sites["m00-normal-hot-update-image"]["providerAssemblyIdentity"],
                 "fixedImageLoadedMarker": "M00-HOTUPDATE-OK", "fixedImageTamperRejected": True,
                 "fixedImageNullRejected": True, "fixedImageCallerBytesUnchanged": True,
                 "allowed": allowed, "denied": denied, "error": ""}
        probe_path = root / "reflection-result-schema2.json"
        probe_path.write_text(json.dumps(probe))
        return probe_path, receipt, reflection, probe

    def fixture(self, root):
        run = root / "run"
        baseline_root = root / "m02-baseline"
        m01_root = root / "m01"
        run.mkdir(); baseline_root.mkdir(); m01_root.mkdir()
        names = sorted(CANDIDATES | {"AssemblyShadowDemo.Bootstrap"})
        bundles = ["business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle"]
        old_bundles = []
        for name in bundles:
            item = m01_root / name
            item.write_bytes(name.encode())
            old_bundles.append({"name": name, "path": name, "sha256": sha(item)})
        (m01_root / "baseline-manifest.json").write_text(json.dumps({"schemaVersion": 1, "bundles": old_bundles}))
        player = baseline_root / "PlayerInputs"
        (player / "Assemblies").mkdir(parents=True)
        native = root / "GameAssembly.dylib"; native.write_bytes(b"native")
        source_pins = {"schemaVersion": 1, "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64",
                       "hybridclr": {"url": "hybridclr", "revision": "1" * 40},
                       "il2cppPlus": {"url": "il2cppPlus", "revision": "2" * 40},
                       "hybridclrUnity": {"url": "hybridclrUnity", "revision": "3" * 40},
                       "demo": {"url": "demo", "revision": "4" * 40}}
        descriptors = []
        player_entries = []
        for name in names:
            dll = player / "Assemblies" / (name + ".dll"); dll.write_bytes(("baseline-" + name).encode())
            item = {"name": name, "path": "Assemblies/" + name + ".dll", "sha256": sha(dll)}
            player_entries.append(item)
            descriptors.append({"name": name, "mvid": "mvid-" + name, "filePath": "PlayerInputs/Assemblies/" + name + ".dll",
                                "sha256": item["sha256"], "semanticHash": "semantic-" + name, "references": [],
                                "isShadowCapable": name in CANDIDATES, "isBootstrap": name == "AssemblyShadowDemo.Bootstrap"})
        by_desc = {item["name"]: item for item in descriptors}
        by_desc["AssemblyA.Implementation.Internal"]["references"] = ["AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility"]
        by_desc["AssemblyA.Implementation.Extensibility"]["references"] = ["AssemblyA.Contracts"]
        by_desc["AssemblyShadowDemo.ExtensibilityConsumer"]["references"] = ["AssemblyA.Implementation.Extensibility"]
        by_desc["AssemblyShadowDemo.ContractsConsumer"]["references"] = ["AssemblyA.Contracts"]
        edges = [
            {"consumer": "AssemblyA.Implementation.Internal", "provider": "AssemblyA.Contracts", "kind": "AssemblyRef"},
            {"consumer": "AssemblyA.Implementation.Internal", "provider": "AssemblyA.Implementation.Extensibility", "kind": "AssemblyRef"},
            {"consumer": "AssemblyA.Implementation.Extensibility", "provider": "AssemblyA.Contracts", "kind": "AssemblyRef"},
            {"consumer": "AssemblyShadowDemo.ExtensibilityConsumer", "provider": "AssemblyA.Implementation.Extensibility", "kind": "AssemblyRef"},
            {"consumer": "AssemblyShadowDemo.ContractsConsumer", "provider": "AssemblyA.Contracts", "kind": "AssemblyRef"},
        ]
        receipt = {"schemaVersion": 1, "kind": "PlayerBuildInputs", "snapshotHash": "", "unityVersion": "2022.3.62f2",
                   "target": "StandaloneOSX", "architecture": "arm64", "buildGuid": "guid", "playerBuildSucceeded": True,
                   "playerBuildFilterCaptured": True, "playerBuildOptions": 1, "normalHotUpdateAssemblies": [], "filteredAssemblies": [], "filteredAssemblyCapabilities": [],
                   "nativeLibraryPath": str(native), "nativeLibrarySha256": sha(native), "sourcePins": source_pins, "assemblies": player_entries, "references": []}
        linked_root = player / "LinkedPlayer"
        (linked_root / "Assemblies").mkdir(parents=True)
        linked_files = []
        for index, name in enumerate(names, 1):
            linked_name = name.lower()
            linked_file = linked_root / "Assemblies" / (linked_name + ".dll")
            linked_file.write_bytes((player / "Assemblies" / (name + ".dll")).read_bytes())
            linked_files.append({"name": linked_name, "path": "Assemblies/" + linked_name + ".dll", "sha256": sha(linked_file),
                                 "mvid": "00000000-0000-0000-0000-" + str(index).zfill(12), "pdbPath": "", "pdbSha256": ""})
        linked = {"schemaVersion": 1, "buildGuid": "guid", "nativeLibrarySha256": sha(native), "target": "StandaloneOSX", "architecture": "arm64",
                  "sourceDirectory": str(root / "linked-player-source"), "protectedAssemblies": sorted(name.lower() for name in CANDIDATES | {"AssemblyShadowDemo.Bootstrap"}),
                  "assemblies": linked_files}
        (linked_root / "linked-player-receipt.json").write_text(json.dumps(linked))
        receipt["linkedPlayerReceipt"] = linked
        receipt["linkedPlayerReceiptHash"] = _snapshot_linked_hash(linked)
        receipt["linkerExcludedAssemblies"] = []
        receipt["linkerExcludedAssemblyCapabilities"] = []
        receipt["snapshotHash"] = _snapshot_hash(receipt, player, player / "assembly-snapshot.json")
        (player / "assembly-snapshot.json").write_text(json.dumps(receipt))
        for item in descriptors:
            side = baseline_root / "assemblies" / (item["name"] + ".json"); side.parent.mkdir(exist_ok=True)
            side.write_text(json.dumps(item))
        resource_index = baseline_root / "resource-script-index.json"; resource_index.write_text(json.dumps({"schemaVersion": 2, "hasUnknown": False, "unknowns": []}))
        for name, data in (("resource-abi.json", {"schemaVersion": 2, "unknowns": []}), ("source-pins.json", source_pins), ("policy.json", {})):
            (baseline_root / name).write_text(json.dumps(data))
        policy_hash = sha(baseline_root / "policy.json")
        resource_hash = _resource_abi_hash(json.loads((baseline_root / "resource-abi.json").read_text()))
        resource_root = baseline_root / "ResourceInputs"; (resource_root / "CompilerInputs" / "Assemblies").mkdir(parents=True)
        (resource_root / "ResourceAssemblies").mkdir()
        (resource_root / "Bundles").mkdir()
        (resource_root / "Sources" / "ProjectSettings").mkdir(parents=True)
        (resource_root / "resource-abi.json").write_bytes((baseline_root / "resource-abi.json").read_bytes())
        (resource_root / "resource-script-index.json").write_bytes((baseline_root / "resource-script-index.json").read_bytes())
        pin_snapshot = resource_root / "Sources" / "ProjectSettings" / "AssemblyShadowSourcePins.json"; pin_snapshot.write_text(json.dumps(source_pins))
        source_item = {"path": "ProjectSettings/AssemblyShadowSourcePins.json", "snapshotPath": "Sources/ProjectSettings/AssemblyShadowSourcePins.json", "sha256": sha(pin_snapshot), "metaSnapshotPath": "", "metaSha256": ""}
        compiler_entries = []
        for name in names:
            src = player / "Assemblies" / (name + ".dll"); dst = resource_root / "CompilerInputs" / "Assemblies" / src.name; dst.write_bytes(src.read_bytes())
            compiler_entries.append({"name": name, "path": "Assemblies/" + src.name, "sha256": sha(dst), "pdbPath": "", "pdbSha256": ""})
            if name in CANDIDATES:
                (resource_root / "ResourceAssemblies" / src.name).write_bytes(src.read_bytes())
        compiler_receipt = {"schemaVersion": 1, "kind": "CompilePlayerScripts", "snapshotHash": "", "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64", "sourcePins": source_pins, "assemblies": compiler_entries, "references": [], "filteredAssemblies": [], "filteredAssemblyCapabilities": [], "normalHotUpdateAssemblies": [], "extraScriptingDefines": [], "playerBuildFilterCaptured": False, "playerBuildOptions": 0}
        compiler_receipt["snapshotHash"] = _snapshot_hash(compiler_receipt, resource_root / "CompilerInputs", resource_root / "CompilerInputs" / "assembly-snapshot.json")
        (resource_root / "CompilerInputs" / "assembly-snapshot.json").write_text(json.dumps(compiler_receipt))
        for name, item in zip(bundles, old_bundles): (resource_root / "Bundles" / name).write_bytes((m01_root / name).read_bytes())
        resource_bundles = [{"name": name, "sha256": item["sha256"], "assets": [name + ".asset"]} for name, item in zip(bundles, old_bundles)]
        resource_receipt = {"schemaVersion": 1, "provenance": "CompilePlayerScriptsAndBuildAssetBundles", "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64", "compilerSnapshotPath": "CompilerInputs", "compilerSnapshotHash": compiler_receipt["snapshotHash"], "compilerSnapshotIsPlayer": False, "metadataAssemblyDirectory": "ResourceAssemblies", "metadataAssemblies": [{"path": "ResourceAssemblies/" + name + ".dll", "sha256": sha(resource_root / "ResourceAssemblies" / (name + ".dll"))} for name in sorted(CANDIDATES)], "resourceAbiPath": "resource-abi.json", "resourceAbiHash": resource_hash, "resourceAbiFileSha256": sha(resource_root / "resource-abi.json"), "resourceIndexPath": "resource-script-index.json", "resourceIndexHash": sha(resource_root / "resource-script-index.json"), "bundleDirectory": "Bundles", "candidateAssemblies": sorted(CANDIDATES), "buildMap": {"schemaVersion": 1, "bundleDirectory": "Bundles", "bundles": [{"name": name, "assets": [name + ".asset"]} for name in bundles]}, "bundles": resource_bundles, "sources": [source_item], "sourceSetHash": _resource_source_set_hash([source_item]), "scripts": [], "dependencies": {"schemaVersion": 1, "runtimeDependencies": [], "resourceDependencies": [], "bootstrapEntrypoints": []}}
        (resource_root / "resource-build-receipt.json").write_text(json.dumps(resource_receipt)); (resource_root / "manifest.sha256").write_text(sha(resource_root / "resource-build-receipt.json") + "\n")
        baseline_bundles = [{"name": name, "sha256": item["sha256"], "assets": []} for name, item in zip(bundles, old_bundles)]
        baseline = {"schemaVersion": 1, "semanticHashSchema": 1, "baselineBuildId": "M02-Baseline-v1", "unityVersion": "2022.3.62f2",
                    "target": "StandaloneOSX", "architecture": "arm64", "sourcePins": source_pins, "runtimeAbiHash": _runtime_abi_hash(source_pins, "fixture"),
                    "shadowCandidates": sorted(CANDIDATES), "bootstrapAssemblies": ["AssemblyShadowDemo.Bootstrap"], "bootstrapAbiHash": "bootstrap",
                    "resourceAbiHash": resource_hash, "resourceIndexHash": sha(resource_index), "resourceBaselinePath": "ResourceInputs", "resourceBuildReceiptHash": sha(resource_root / "resource-build-receipt.json"), "policyHash": policy_hash,
                    "playerInputSnapshot": "PlayerInputs", "playerInputSnapshotHash": receipt["snapshotHash"], "playerBuildGuid": "guid",
                    "nativeLibrarySha256": sha(native), "assemblies": descriptors, "dependencyGraph": edges, "bundles": baseline_bundles}
        baseline_path = baseline_root / "baseline-manifest.json"; baseline_path.write_text(json.dumps(baseline, indent=2))
        (baseline_root / "manifest.sha256").write_text(sha(baseline_path) + "\n")
        # A source compile snapshot and artifact are made for each patch.
        artifacts = []
        for patch_id, closure in (("P01", {"AssemblyA.Implementation.Internal"}),
                                  ("P02", {"AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ExtensibilityConsumer"}),
                                  ("P03", set(CANDIDATES)), ("P05", {"AssemblyA.Implementation.Internal"})):
            snapshot = run / (patch_id + "-compile") / "Snapshot"; (snapshot / "Assemblies").mkdir(parents=True)
            entries = []
            for name in names:
                dll = snapshot / "Assemblies" / (name + ".dll"); dll.write_bytes((patch_id + "-" + name).encode())
                entries.append({"name": name, "path": "Assemblies/" + name + ".dll", "sha256": sha(dll), "pdbPath": "", "pdbSha256": ""})
            compile_receipt = {"schemaVersion": 1, "kind": "CompilePlayerScripts", "snapshotHash": "", "unityVersion": "2022.3.62f2",
                               "target": "StandaloneOSX", "architecture": "arm64", "sourcePins": source_pins, "assemblies": entries, "references": [],
                               "filteredAssemblies": [], "filteredAssemblyCapabilities": [], "normalHotUpdateAssemblies": [], "extraScriptingDefines": [], "playerBuildFilterCaptured": False, "playerBuildOptions": 0}
            compile_receipt["snapshotHash"] = _snapshot_hash(compile_receipt, snapshot, snapshot / "assembly-snapshot.json")
            (snapshot / "assembly-snapshot.json").write_text(json.dumps(compile_receipt))
            patch_root = run / patch_id; patch_root.mkdir()
            closure_entries = []
            for name in sorted(closure):
                source = snapshot / "Assemblies" / (name + ".dll")
                target = patch_root / "DLLs" / source.name; target.parent.mkdir(exist_ok=True)
                target.write_bytes(source.read_bytes())
                closure_entries.append({"name": name, "dll": "DLLs/" + source.name, "sha256": sha(target), "semanticHash": "semantic-" + name,
                                        "mvid": "mvid-" + name, "baselineMvid": "mvid-" + name, "pdb": "", "pdbSha256": "", "references": []})
            (patch_root / "compile-snapshot-receipt.json").write_text(json.dumps(compile_receipt))
            (patch_root / "resource-abi.json").write_text(json.dumps({"schemaVersion": 2, "unknowns": []}))
            resource_level = "ResourceRebuildRequired" if patch_id == "P05" else "CodeOnly"
            patch = {"schemaVersion": 1, "semanticHashSchema": 1, "patchId": patch_id, "baselineBuildId": "M02-Baseline-v1",
                     "baselineManifestSha256": "BASELINE_HASH", "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64",
                     "sourcePins": source_pins, "runtimeAbiHash": _runtime_abi_hash(source_pins, "fixture"), "compileSnapshotHash": compile_receipt["snapshotHash"], "bootstrapAbiHash": "bootstrap",
                     "baselineResourceAbiHash": resource_hash, "resourceAbiHash": resource_hash, "resourceChangeLevel": resource_level,
                     "dllOnly": patch_id != "P05", "resourceBundlesRequired": ["business-scene.bundle", "versioned-prefab.bundle"] if patch_id == "P05" else [],
                     "changedRoots": ["AssemblyA.Implementation.Internal" if patch_id in ("P01", "P05") else "AssemblyA.Implementation.Extensibility" if patch_id == "P02" else "AssemblyA.Contracts"],
                     "loadOrder": (["AssemblyA.Contracts", "AssemblyShadowDemo.ContractsConsumer", "AssemblyA.Implementation.Extensibility", "AssemblyShadowDemo.ExtensibilityConsumer", "AssemblyA.Implementation.Internal"] if patch_id == "P03" else
                                   ["AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ExtensibilityConsumer"] if patch_id == "P02" else sorted(closure)),
                     "closure": closure_entries, "dependencyGraph": edges, "unsigned": True, "signatureAlgorithm": "None"}
            patch_path = patch_root / "patch-manifest.json"; patch_path.write_text(json.dumps(patch, indent=2))
            (patch_root / "manifest.sha256").write_text(sha(patch_path) + "\n")
            artifacts.append({"id": "P05-requires-bundles" if patch_id == "P05" else patch_id, "path": str(patch_path), "sha256": sha(patch_path)})
        baseline["_actualSha256"] = sha(baseline_path)
        actual = baseline_path.read_text();
        for patch in (run / "P01" / "patch-manifest.json", run / "P02" / "patch-manifest.json", run / "P03" / "patch-manifest.json", run / "P05" / "patch-manifest.json"):
            data = json.loads(patch.read_text()); data["baselineManifestSha256"] = baseline["_actualSha256"]; patch.write_text(json.dumps(data, indent=2)); (patch.parent / "manifest.sha256").write_text(sha(patch) + "\n")
        (run / "P01-repeat").mkdir(); (run / "P01-repeat" / "patch-manifest.json").write_bytes((run / "P01" / "patch-manifest.json").read_bytes()); (run / "P01-repeat" / "manifest.sha256").write_text(sha(run / "P01-repeat" / "patch-manifest.json") + "\n")
        artifacts = [{"id": a["id"], "path": a["path"], "sha256": sha(Path(a["path"]))} for a in artifacts]
        artifacts.append({"id": "P01-repeat", "path": str(run / "P01-repeat" / "patch-manifest.json"), "sha256": sha(run / "P01-repeat" / "patch-manifest.json")})
        (run / "baseline-repeat").mkdir(); (run / "baseline-repeat" / "baseline-manifest.json").write_bytes(baseline_path.read_bytes())
        report = {"schemaVersion": 1, "result": "Passed", "unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "runDirectory": str(run),
                  "baselineManifestPath": str(baseline_path), "baselineManifestSha256": sha(baseline_path),
                  "cases": [{"id": item, "passed": True} for item in sorted(CASE_IDS)],
                  "artifacts": artifacts}
        editor = root / "editor.json"; editor.write_text(json.dumps(report))
        suites = "".join('<test-suite fullname="{0}"><test-case result="Passed" name="{0}.ok"/></test-suite>'.format(name) for name in NUNIT_SUITES)
        nunit = root / "nunit.xml"; nunit.write_text('<test-run result="Passed" failed="0">' + suites + '</test-run>')
        # Correct baseline hash after all manifest writes.
        for patch in (run / "P01" / "patch-manifest.json", run / "P02" / "patch-manifest.json", run / "P03" / "patch-manifest.json", run / "P05" / "patch-manifest.json"):
            data = json.loads(patch.read_text()); data["baselineManifestSha256"] = sha(baseline_path); patch.write_text(json.dumps(data, indent=2)); (patch.parent / "manifest.sha256").write_text(sha(patch) + "\n")
        report["artifacts"] = [{"id": a["id"], "path": a["path"], "sha256": sha(Path(a["path"]))} for a in artifacts]
        report["baselineManifestSha256"] = sha(baseline_path); editor.write_text(json.dumps(report))
        return editor, nunit, m01_root

    def test_complete_fixture_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            result = verify(editor, nunit, m01)
            self.assertTrue(result["resultPassed"])
            self.assertEqual(set(result["patches"]), {"P01", "P02", "P03", "P05"})

    def test_linked_evidence_validation_cases_are_required_and_passing(self):
        for case_id in ("M02-LinkedEvidenceRoundTrip", "M02-LinkedEvidenceFacadeTamper", "M02-LinkedEvidenceReboundTamper"):
            with self.subTest(case_id=case_id), tempfile.TemporaryDirectory() as folder:
                editor, nunit, m01 = self.fixture(Path(folder))
                report = json.loads(editor.read_text())
                self.assertTrue(next(case for case in report["cases"] if case["id"] == case_id)["passed"])
                self.assertTrue(verify(editor, nunit, m01)["resultPassed"])

    def test_linked_evidence_validation_case_omission_or_failure_fails(self):
        for mode in ("omit", "fail"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                editor, nunit, m01 = self.fixture(Path(folder))
                report = json.loads(editor.read_text())
                target = "M02-LinkedEvidenceFacadeTamper"
                if mode == "omit":
                    report["cases"] = [case for case in report["cases"] if case["id"] != target]
                else:
                    next(case for case in report["cases"] if case["id"] == target)["passed"] = False
                editor.write_text(json.dumps(report))
                with self.assertRaises(VerificationError) as error:
                    verify(editor, nunit, m01)
                self.assertTrue(str(error.exception))

    def test_reflection_configuration_projects_canonical_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path = self.reflection_fixture(Path(folder))
            control = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)
            receipt["extraScriptingDefines"] = [control]
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertEqual(reflection["rawSha256"], sha(config_path))
            self.assertEqual(reflection["declarations"][0]["allowedTypes"], [])
            self.assertEqual(reflection["declarations"][0]["providers"], [])
            self.assertRegex(reflection["canonicalHash"], r"^[0-9a-f]{64}$")

    def test_reflection_configuration_projects_sorted_concrete_providers(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path = self.reflection_fixture(Path(folder))
            config["sites"][0]["allowedTypes"] = ["Zed.Value, Zed.Provider", "System.String, mscorlib"]
            config_path.write_text(json.dumps(config, separators=(",", ":")))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertEqual(reflection["declarations"][0]["allowedTypes"], ["System.String, mscorlib", "Zed.Value, Zed.Provider"])
            self.assertEqual(reflection["declarations"][0]["providers"], ["mscorlib", "zed.provider"])

    def test_reflection_nonconcrete_provider_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path = self.reflection_fixture(Path(folder))
            config["sites"][0]["allowedTypes"] = ["System.String[], mscorlib"]
            config_path.write_text(json.dumps(config, separators=(",", ":")))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("non-concrete", str(error.exception))

    def test_reflection_schema2_image_and_finite_domains_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, _, image_path = self.reflection_schema2_fixture(Path(folder))
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertEqual(reflection["canonicalHash"], _reflection_parse(snapshot / "ReflectionBindings/configuration.json", (snapshot / "ReflectionBindings/configuration.json").read_bytes())["canonicalHash"])
            self.assertEqual(len(reflection["configuration"]["sites"]), 5)
            fixed = next(item for item in reflection["declarations"] if item["id"] == "m00-normal-hot-update-image")
            self.assertEqual(fixed["kind"], "FixedAssemblyBytes")
            self.assertEqual(fixed["providers"], ["assemblyshadowbaseline.hotupdate"])
            self.assertTrue(image_path.is_file())

    def test_reflection_schema2_project_hash_matches_csharp_golden(self):
        project_config = Path(__file__).resolve().parents[3] / "ProjectSettings" / "AssemblyShadowReflectionBindings.json"
        reflection = _reflection_parse(project_config, project_config.read_bytes())
        self.assertEqual(reflection["canonicalHash"], "79ef642d19d3e5ed4866c152aa63691741b5dd1d96ead13231b0e11b75f031ad")

    def test_reflection_schema2_image_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, _, image_path = self.reflection_schema2_fixture(Path(folder))
            image_path.write_bytes(b"tampered-image")
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("fixed assembly image SHA", str(error.exception))

    def test_reflection_schema2_finite_domain_substitution_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path, _ = self.reflection_schema2_fixture(Path(folder))
            config["sites"][2]["allowedTypes"][0] = config["sites"][2]["allowedTypes"][0].replace("Bloom", "Exposure")
            config_path.write_text(json.dumps(config, separators=(",", ":")))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("exact 17", str(error.exception))

    def test_reflection_schema2_probe_acceptance_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, _ = self.reflection_schema2_probe_fixture(Path(folder))
            result = _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertEqual(result["result"], "Passed")
            self.assertEqual(result["discoveryAllowedTypes"], 17)
            self.assertEqual(result["fixedImageSha256"], "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27")

    def test_reflection_schema2_probe_contract_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, probe = self.reflection_schema2_probe_fixture(Path(folder))
            probe["volumeManagerMatchesContract"] = False
            probe_path.write_text(json.dumps(probe))
            with self.assertRaises(VerificationError) as error:
                _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertIn("fixed-image acceptance evidence", str(error.exception))

    def test_reflection_schema2_probe_null_marker_cannot_hide_value(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, probe = self.reflection_schema2_probe_fixture(Path(folder))
            probe["denied"][2]["input"] = "forged-nonempty-value"
            probe_path.write_text(json.dumps(probe))
            with self.assertRaises(VerificationError) as error:
                _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertIn("null input", str(error.exception))

    def builtin_source_fixture(self, root):
        resource_root = root / "ResourceInputs"
        resource_root.mkdir()
        backing = resource_root / "BuiltinProof" / "Resources" / "backing" / "builtin.asset"
        backing.parent.mkdir(parents=True)
        backing.write_bytes(b"builtin backing")
        module = resource_root / "BuiltinProof" / "Modules" / "pending" / "UnityEngine.dll"
        module.parent.mkdir(parents=True)
        module.write_bytes(b"UnityEngine module bytes")
        module_sha = sha(module)
        final_module = resource_root / "BuiltinProof" / "Modules" / module_sha / "UnityEngine.dll"
        final_module.parent.mkdir(parents=True)
        final_module.write_bytes(module.read_bytes())
        module = final_module
        proof = {
            "schemaVersion": 1, "unityVersion": "2022.3.62f2", "virtualPath": "Library/builtin.asset", "guid": "builtin-guid",
            "backingPath": "BuiltinProof/Resources/backing/builtin.asset", "backingSha256": sha(backing),
            "modules": [{"assemblyName": "UnityEngine", "path": "BuiltinProof/Modules/" + module_sha + "/UnityEngine.dll", "sha256": module_sha}],
            "objects": [{"name": "Builtin Material", "typeName": "UnityEngine.Material", "assemblyName": "UnityEngine",
                         "guid": "builtin-guid", "localId": 1, "persistent": True, "serializedSha256": "a" * 64}],
        }
        proof_path = resource_root / "Sources" / "builtin-proof.json"
        proof_path.parent.mkdir()
        proof_path.write_text(json.dumps(proof, separators=(",", ":")))
        source = {"path": "Library/builtin.asset", "snapshotPath": "Sources/builtin-proof.json", "sha256": sha(proof_path), "guid": "builtin-guid", "builtin": True}
        return resource_root, source, proof_path, proof

    def test_builtin_source_nested_proof_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            resource_root, source, proof_path, _ = self.builtin_source_fixture(Path(folder))
            _verify_builtin_source(resource_root, source, proof_path, "2022.3.62f2")

    def test_builtin_source_object_identity_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            resource_root, source, proof_path, proof = self.builtin_source_fixture(Path(folder))
            proof["objects"].append(dict(proof["objects"][0], localId=1, name="duplicate"))
            proof_path.write_text(json.dumps(proof, separators=(",", ":")))
            source["sha256"] = sha(proof_path)
            with self.assertRaises(VerificationError) as error:
                _verify_builtin_source(resource_root, source, proof_path, "2022.3.62f2")
            self.assertIn("duplicated", str(error.exception))

    def test_builtin_source_nested_module_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            resource_root, source, proof_path, proof = self.builtin_source_fixture(Path(folder))
            module_path = resource_root / proof["modules"][0]["path"]
            module_path.write_bytes(b"tampered engine module")
            with self.assertRaises(VerificationError) as error:
                _verify_builtin_source(resource_root, source, proof_path, "2022.3.62f2")
            self.assertIn("module bytes SHA", str(error.exception))

    def test_reflection_probe_acceptance_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, _ = self.reflection_probe_fixture(Path(folder))
            result = _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertEqual(result, {"result": "Passed", "allowed": 26, "denied": 8, "assemblyResolveEvents": 0})

    def test_reflection_probe_guid_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, probe = self.reflection_probe_fixture(Path(folder))
            probe["buildGuid"] = "other-guid"
            probe_path.write_text(json.dumps(probe))
            with self.assertRaises(VerificationError) as error:
                _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertIn("buildGuid", str(error.exception))

    def test_reflection_probe_staged_config_omission_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, _ = self.reflection_probe_fixture(Path(folder))
            staged = Path(receipt["playerOutput"]) / "Contents" / "Resources" / "Data" / "StreamingAssets" / "AssemblyShadow" / "M02" / "reflection-bindings.json"
            staged.unlink()
            with self.assertRaises(VerificationError) as error:
                _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertIn("staged Player reflection configuration", str(error.exception))

    def test_reflection_probe_domain_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            probe_path, receipt, reflection, probe = self.reflection_probe_fixture(Path(folder))
            probe["allowed"] = probe["allowed"][:-1]
            probe_path.write_text(json.dumps(probe))
            with self.assertRaises(VerificationError) as error:
                _verify_reflection_probe(probe_path, receipt, reflection)
            self.assertIn("exact 26 configured AQNs", str(error.exception))

    def test_reflection_stale_control_hash_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, config_path = self.reflection_fixture(Path(folder))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + "b" * 64]
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("differs from control define", str(error.exception))

    def test_reflection_directory_without_control_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, _ = self.reflection_fixture(Path(folder))
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("cannot contain ReflectionBindings evidence", str(error.exception))

    def test_reflection_control_without_configuration_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, config_path = self.reflection_fixture(Path(folder))
            config_path.unlink()
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + "a" * 64]
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            self.assertIn("configuration is missing", str(error.exception))

    def test_reflection_manifest_projection_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, config_path = self.reflection_fixture(Path(folder))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            manifest = {
                "reflectionBindingConfigurationSha256": reflection["rawSha256"],
                "reflectionBindingConfigurationHash": reflection["canonicalHash"],
                "reflectionBindings": [dict(reflection["declarations"][0], reason="tampered")],
            }
            with self.assertRaises(VerificationError) as error:
                _reflection_manifest(manifest, reflection, Path(folder) / "baseline-manifest.json")
            self.assertIn("declaration projection", str(error.exception))

    def test_reflection_manifest_accepts_jsonutility_empty_nullable_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path, _ = self.reflection_schema2_fixture(Path(folder))
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            declarations = [dict(item) for item in reflection["declarations"]]
            for declaration in declarations:
                if declaration["kind"] != "FixedAssemblyBytes":
                    declaration["imageSha256"] = ""
                    declaration["providerAssemblyIdentity"] = ""
                    declaration["imagePath"] = ""
            manifest = {"reflectionBindingConfigurationSha256": reflection["rawSha256"],
                        "reflectionBindingConfigurationHash": reflection["canonicalHash"],
                        "reflectionBindings": declarations}
            _reflection_manifest(manifest, reflection, Path(folder) / "baseline-manifest.json")

    def test_reflection_manifest_rejects_injected_nonempty_nullable_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path, _ = self.reflection_schema2_fixture(Path(folder))
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            declarations = [dict(item) for item in reflection["declarations"]]
            target = next(item for item in declarations if item["kind"] != "FixedAssemblyBytes")
            target["imagePath"] = "ReflectionBindings/Images/injected.dll.bytes"
            manifest = {"reflectionBindingConfigurationSha256": reflection["rawSha256"],
                        "reflectionBindingConfigurationHash": reflection["canonicalHash"],
                        "reflectionBindings": declarations}
            with self.assertRaises(VerificationError) as error:
                _reflection_manifest(manifest, reflection, Path(folder) / "baseline-manifest.json")
            self.assertIn("declaration projection", str(error.exception))

    def test_reflection_manifest_accepts_schema1_jsonutility_empty_kind(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, config, receipt, config_path = self.reflection_fixture(Path(folder))
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json")
            declaration = dict(reflection["declarations"][0], kind="", imageSha256="",
                               providerAssemblyIdentity="", imagePath="")
            manifest = {"reflectionBindingConfigurationSha256": reflection["rawSha256"],
                        "reflectionBindingConfigurationHash": reflection["canonicalHash"],
                        "reflectionBindings": [declaration]}
            _reflection_manifest(manifest, reflection, Path(folder) / "baseline-manifest.json")

    def test_tampering_compile_snapshot_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            source = Path(folder) / "run" / "P02-compile" / "Snapshot" / "Assemblies" / "AssemblyA.Implementation.Extensibility.dll"
            source.write_bytes(b"tampered-compile-input")
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("P02-compile/Snapshot", str(error.exception))

    def test_tampering_patch_dll_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            report = json.loads(editor.read_text()); patch = Path(next(item["path"] for item in report["artifacts"] if item["id"] == "P01"))
            data = json.loads(patch.read_text()); dll = patch.parent / data["closure"][0]["dll"]; dll.write_bytes(b"tampered")
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("closure[0]", str(error.exception))

    def test_tampering_resource_receipt_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            receipt = Path(folder) / "run" / ".." / "m02-baseline" / "ResourceInputs" / "resource-build-receipt.json"
            receipt.write_text(receipt.read_text().replace('"schemaVersion": 1', '"schemaVersion": 9', 1))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("resource-build-receipt.json", str(error.exception))

    def test_tampering_resource_asset_or_index_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            resource = Path(folder) / "m02-baseline" / "ResourceInputs"
            index = resource / "resource-script-index.json"
            index.write_text(index.read_text().replace('"schemaVersion": 2', '"schemaVersion": 3', 1))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("resource index SHA", str(error.exception))

    def test_tampering_filtered_role_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            receipt_path = Path(folder) / "m02-baseline" / "PlayerInputs" / "assembly-snapshot.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["filteredAssemblyCapabilities"] = [{
                "name": "Injected.FilteredAssembly", "classification": 5,
                "isPrecompiled": False, "isShadowCapable": False,
                "isBootstrap": False, "capabilityDeclared": True,
            }]
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("filteredAssemblyCapabilities[0]", str(error.exception))

    def test_tampering_demo_source_pin_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            receipt_path = Path(folder) / "m02-baseline" / "PlayerInputs" / "assembly-snapshot.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["sourcePins"]["demo"]["revision"] = "5" * 40
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("source pins differ from baseline provenance", str(error.exception))

    def test_tampering_linked_player_bytes_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            linked_dll = Path(folder) / "m02-baseline" / "PlayerInputs" / "LinkedPlayer" / "Assemblies" / "assemblya.contracts.dll"
            linked_dll.write_bytes(b"tampered-linked-player")
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("linked DLL SHA-256", str(error.exception))

    def test_stale_linked_receipt_claim_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            linked_path = Path(folder) / "m02-baseline" / "PlayerInputs" / "LinkedPlayer" / "linked-player-receipt.json"
            linked = json.loads(linked_path.read_text())
            linked["sourceDirectory"] = str(Path(folder) / "different-linked-source")
            linked_path.write_text(json.dumps(linked))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("linkedPlayerReceiptHash", str(error.exception))

    def test_linked_protected_candidate_absent_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, _, _ = self.fixture(Path(folder))
            root = Path(folder) / "m02-baseline"
            receipt_path = root / "PlayerInputs" / "assembly-snapshot.json"
            receipt = json.loads(receipt_path.read_text())
            linked = receipt["linkedPlayerReceipt"]
            linked["protectedAssemblies"].remove("assemblya.contracts")
            linked["assemblies"] = [item for item in linked["assemblies"] if item["name"] != "assemblya.contracts"]
            (root / "PlayerInputs" / "LinkedPlayer" / "linked-player-receipt.json").write_text(json.dumps(linked))
            receipt["linkedPlayerReceiptHash"] = _snapshot_linked_hash(linked)
            descriptors = {item["name"]: item for item in json.loads((root / "baseline-manifest.json").read_text())["assemblies"]}
            with self.assertRaises(VerificationError) as error:
                _verify_linked_player(root / "PlayerInputs", receipt, descriptors, receipt_path)
            self.assertIn("protectedAssemblies", str(error.exception))

    def test_fresh_resource_metadata_substitution_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            resource = Path(folder) / "m02-baseline" / "ResourceInputs"
            source = resource / "ResourceAssemblies" / "AssemblyA.Contracts.dll"
            source.write_bytes((resource / "CompilerInputs" / "Assemblies" / "AssemblyShadowDemo.Bootstrap.dll").read_bytes())
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("metadata proof SHA", str(error.exception))

    def test_snapshot_hash_canonicalizes_mixed_case_role_path(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, _, _ = self.fixture(Path(folder))
            del editor
            snapshot_root = Path(folder) / "m02-baseline" / "PlayerInputs"
            receipt_path = snapshot_root / "assembly-snapshot.json"
            receipt = json.loads(receipt_path.read_text())
            filtered_path = snapshot_root / "Assemblies" / "Filtered" / "Role.dll"
            filtered_path.parent.mkdir()
            filtered_path.write_bytes(b"filtered-role")
            receipt["filteredAssemblies"] = [{"name": "Role", "path": "Assemblies/Filtered/Role.dll", "sha256": sha(filtered_path)}]
            receipt["filteredAssemblyCapabilities"] = [{
                "name": "Packages/UnityEngine.TestRunner.DLL", "classification": 5,
                "isPrecompiled": False, "isShadowCapable": False,
                "isBootstrap": False, "capabilityDeclared": True,
            }]
            first = _snapshot_hash(receipt, snapshot_root, receipt_path)
            receipt["filteredAssemblyCapabilities"][0]["name"] = "unityengine.testrunner"
            second = _snapshot_hash(receipt, snapshot_root, receipt_path)
            self.assertEqual(first, second)

    def test_rehashed_snapshot_rejects_rows_moved_between_sections(self):
        for section in ("References", "Assemblies/Filtered"):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as folder:
                editor, _, _ = self.fixture(Path(folder))
                del editor
                snapshot_root = Path(folder) / "m02-baseline" / "PlayerInputs"
                receipt_path = snapshot_root / "assembly-snapshot.json"
                receipt = json.loads(receipt_path.read_text())
                entry = receipt["assemblies"][0]
                old_path = snapshot_root / entry["path"]
                new_path = snapshot_root / section / (entry["name"] + ".dll")
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
                entry["path"] = section + "/" + entry["name"] + ".dll"
                receipt["snapshotHash"] = _snapshot_hash(receipt, snapshot_root, receipt_path)
                with self.assertRaises(VerificationError) as error:
                    _snapshot_files(receipt, snapshot_root, receipt_path)
                self.assertIn("moved between input/reference/filter roles", str(error.exception))

    def test_compile_snapshot_accepts_materialized_empty_linked_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            run = Path(folder) / "run"
            source_path = run / "P01-compile" / "Snapshot" / "assembly-snapshot.json"
            sidecar_path = run / "P01" / "compile-snapshot-receipt.json"
            source = json.loads(source_path.read_text())
            source["linkedPlayerReceipt"] = {
                "schemaVersion": 0, "buildGuid": "", "nativeLibrarySha256": "", "target": "", "architecture": "",
                "sourceDirectory": "", "protectedAssemblies": [], "assemblies": [],
            }
            source["linkerExcludedAssemblies"] = None
            source["linkerExcludedAssemblyCapabilities"] = None
            source_path.write_text(json.dumps(source))
            sidecar_path.write_text(json.dumps(source))
            result = verify(editor, nunit, m01)
            self.assertTrue(result["resultPassed"])

    def test_compile_snapshot_partial_linked_claim_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            source_path = Path(folder) / "run" / "P01-compile" / "Snapshot" / "assembly-snapshot.json"
            sidecar_path = Path(folder) / "run" / "P01" / "compile-snapshot-receipt.json"
            source = json.loads(source_path.read_text())
            source["linkedPlayerReceipt"] = {
                "schemaVersion": 1, "buildGuid": "claimed", "nativeLibrarySha256": "", "target": "", "architecture": "",
                "sourceDirectory": "", "protectedAssemblies": [], "assemblies": [],
            }
            source_path.write_text(json.dumps(source))
            sidecar_path.write_text(json.dumps(source))
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("compiler snapshot cannot claim linked Player evidence", str(error.exception))

    def test_compile_snapshot_rejects_linked_player_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            linked_dir = Path(folder) / "run" / "P01-compile" / "Snapshot" / "LinkedPlayer"
            linked_dir.mkdir()
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("compiler snapshot cannot claim linked Player evidence", str(error.exception))

    def test_linked_schema2_proof_claim_requires_binding_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, _, _ = self.fixture(Path(folder))
            del editor
            snapshot = Path(folder) / "m02-baseline" / "PlayerInputs"
            receipt_path = snapshot / "assembly-snapshot.json"
            receipt = json.loads(receipt_path.read_text())
            linked = receipt["linkedPlayerReceipt"]
            linked["schemaVersion"] = 2
            linked["reflectionBindingEvidenceHash"] = "a" * 64
            receipt["linkedPlayerReceiptHash"] = _snapshot_linked_hash(linked)
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, receipt_path, require_linked=False)
            self.assertIn("cannot claim linked binding evidence", str(error.exception))

    def test_linked_binding_configuration_requires_three_file_player_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, _, receipt, config_path = self.reflection_fixture(Path(folder))
            receipt["kind"] = "PlayerBuildInputs"
            receipt["extraScriptingDefines"] = ["ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + sha(config_path)]
            receipt["linkedPlayerReceipt"] = {"schemaVersion": 2, "assemblies": []}
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json", require_linked=True)
            self.assertIn("undeclared or missing evidence files", str(error.exception))

    def test_linked_binding_evidence_profile_and_sites_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, receipt, _, _ = self.linked_reflection_fixture(Path(folder))
            reflection = _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json", require_linked=True)
            self.assertEqual(reflection["configuration"]["schemaVersion"], 1)

    def test_linked_binding_evidence_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot, receipt, _, evidence_path = self.linked_reflection_fixture(Path(folder))
            proof = json.loads(evidence_path.read_text())
            proof["profileHash"] = "e" * 64
            evidence_path.write_text(json.dumps(proof))
            with self.assertRaises(VerificationError) as error:
                _reflection_snapshot(snapshot, receipt, snapshot / "assembly-snapshot.json", require_linked=True)
            self.assertIn("profileHash", str(error.exception))

    def test_tampering_frozen_resource_bundle_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            bundle = Path(folder) / "m02-baseline" / "ResourceInputs" / "Bundles" / "business-scene.bundle"
            bundle.write_bytes(b"tampered-resource")
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("resource bundle SHA", str(error.exception))

    def test_nunit_unrelated_only_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            editor, nunit, m01 = self.fixture(Path(folder))
            nunit.write_text('<test-run result="Passed" failed="0"><test-case result="Passed" name="Other"/></test-run>')
            with self.assertRaises(VerificationError) as error:
                verify(editor, nunit, m01)
            self.assertIn("MetadataTests", str(error.exception))


if __name__ == "__main__":
    unittest.main()
