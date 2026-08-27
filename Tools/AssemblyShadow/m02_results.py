"""Independently verify the M02 Editor report and its on-disk artifacts.

This verifier deliberately treats the Unity report as an index, not as proof.
Manifest, snapshot, bundle and native-library bytes are re-read and hashed from
their recorded paths.  It validates the Unity metadata contracts emitted by
the AssemblyShadow builders; it does not claim runtime IL or PE/MVID parsing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid
import xml.etree.ElementTree as ET

from shadow_tools import VerificationError, read_json, require, safe_file


TARGET = "StandaloneOSX"
CANDIDATES = frozenset({
    "AssemblyA.Contracts",
    "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal",
    "AssemblyShadowDemo.ContractsConsumer",
    "AssemblyShadowDemo.ExtensibilityConsumer",
})
BOOTSTRAP = "AssemblyShadowDemo.Bootstrap"
INTERNAL = "AssemblyA.Implementation.Internal"
EXTENSIBILITY = "AssemblyA.Implementation.Extensibility"
CONTRACTS = "AssemblyA.Contracts"
M01_BUNDLES = frozenset({"business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle"})
M01_ASSEMBLIES = frozenset({
    "AssemblyA.Contracts",
    "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal",
})
CASE_IDS = frozenset({
    "T02-01", "T02-02", "T02-03", "T02-04", "T02-05", "T02-06", "T02-07",
    "M02-Repeatability", "M02-SnapshotTamper", "M02-LinkedEvidenceRoundTrip",
    "M02-LinkedEvidenceFacadeTamper", "M02-LinkedEvidenceReboundTamper",
    "M02-StructuralPatchEditorDomain",
})
PATCH_IDS = frozenset({"P01", "P02", "P03", "P05-requires-bundles", "P01-repeat"})
NUNIT_SUITES = ("MetadataTests", "PolicyTests", "GraphAndInputTests", "ResourceAbiTests", "SnapshotTests", "SignatureHashTests")
NUNIT_MIN_CASES = {"M02StructuralPatchCompilationTests": 22, "M02DependencyFixtureTests": 2}
NUNIT_SUITES = NUNIT_SUITES + ("ResourceReceiptTests",) + tuple(NUNIT_MIN_CASES)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"Cannot hash missing or symlinked file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _need(condition, path, message):
    require(condition, f"{path}: {message}")


def _json(path: Path):
    try:
        return read_json(path)
    except VerificationError as error:
        raise VerificationError(f"{path}: {error}") from error


def _string(value, path, field):
    _need(isinstance(value, str) and value.strip(), path, f"{field} must be a non-empty string")
    return value


def _absolute_file(path_value, path, field):
    value = _string(path_value, path, field)
    result = Path(value)
    _need(result.is_absolute(), path, f"{field} must be an absolute path")
    _need(result.is_file() and not result.is_symlink(), path, f"{field} is missing or symlinked: {result}")
    return result


def _root(path: Path, label: str) -> Path:
    original = Path(path)
    _need(not original.is_symlink(), label, "directory is symlinked")
    path = original.resolve()
    _need(path.is_dir(), label, "directory is missing")
    return path


def _relative(root: Path, value, path, field):
    value = _string(value, path, field)
    _need(not Path(value).is_absolute() and "\\" not in value, path, f"{field} must be a relative POSIX path")
    try:
        return safe_file(root, value)
    except VerificationError as error:
        raise VerificationError(f"{path}.{field}: {error}") from error


def _relative_dir(root: Path, value, path, field) -> Path:
    value = _string(value, path, field)
    _need(not Path(value).is_absolute() and "\\" not in value, path, f"{field} must be a relative POSIX path")
    parts = value.split("/")
    _need(all(part not in ("", ".", "..") for part in parts), path, f"{field} escapes its root")
    result = root.joinpath(*parts)
    _need(result.is_dir() and not result.is_symlink(), path, f"{field} directory is missing: {result}")
    for part in (result, *result.parents):
        _need(not part.is_symlink(), path, f"{field} has symlinked component: {part}")
    return result


def _name(value, path, field):
    return _string(value, path, field).strip()


def _names(items, path, field):
    _need(isinstance(items, list), path, f"{field} must be an array")
    result = []
    for index, item in enumerate(items):
        item_path = f"{path}.{field}[{index}]"
        if isinstance(item, str):
            result.append(_name(item, item_path, "name"))
        else:
            _need(isinstance(item, dict), item_path, "entry must be a string or object")
            result.append(_name(item.get("name"), item_path, "name"))
    _need(len(result) == len(set(result)), path, f"{field} contains duplicate names")
    return result


def _normal(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _csharp_len(value):
    return len(value.encode("utf-16-le")) // 2


def _resource_abi_hash(descriptor):
    """Mirror ResourceAbiHasher v2's canonical UTF-8 input for independent checking."""
    text = ["resource-abi-schema:2\n"]

    def append(key, value):
        value = "" if value is None else str(value)
        text.append(f"{key}={_csharp_len(value)}:{value}\n")

    def append_many(key, values):
        values = {value for value in (values or []) if value is not None}
        for value in sorted(values):
            append(key, value)

    append("descriptor-schema", descriptor.get("schemaVersion", ""))
    types = [item for item in (descriptor.get("types") or []) if isinstance(item, dict)]
    for item in sorted(types, key=lambda value: value.get("typeKey") or ""):
        append("type", item.get("typeKey")); append("assembly", item.get("assembly")); append("namespace", item.get("namespace"))
        append("name", item.get("type")); append("base", item.get("baseChain"))
        append_many("interface", item.get("interfaces")); append("callback", "1" if item.get("serializationCallback") is True else "0")
        append("callback-semantics", item.get("callbackSemanticHash")); append_many("serialize-reference-candidate", item.get("serializeReferenceCandidates"))
        append_many("referenced-type", item.get("referencedTypeKeys")); append_many("type-unknown-reason", item.get("unknownReasons"))
        fields = [field for field in (item.get("fields") or []) if isinstance(field, dict)]
        for field in sorted(fields, key=lambda value: (value.get("declaringType") or "", value.get("name") or "")):
            append("field.declaring", field.get("declaringType")); append("field.name", field.get("name")); append("field.type", field.get("type"))
            append("field.shape", field.get("shape")); append("field.flags", field.get("flags")); append_many("field.former", field.get("formerNames"))
            append("field.managed-reference", field.get("managedReferenceMode")); append("field.unknown", "1" if field.get("unknown") is True else "0")
        append("type.unknown", "1" if item.get("hasUnknown") is True else "0")
    append_many("unknown", descriptor.get("unknowns"))
    return "sha256:" + hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _resource_source_set_hash(sources):
    entries = []
    for source in sources:
        values = {
            "path": source.get("path", ""), "snapshotPath": source.get("snapshotPath", ""), "sha256": source.get("sha256", ""),
            "metaSnapshotPath": source.get("metaSnapshotPath", ""), "metaSha256": source.get("metaSha256", ""), "guid": source.get("guid", ""),
            "builtin": source.get("builtin", False), "dependencies": source.get("dependencies") or [],
        }
        entries.append(json.dumps(values, ensure_ascii=False, separators=(",", ":")))
    return hashlib.sha256(("resource-source-set:1\n" + "\n".join(sorted(entries))).encode("utf-8")).hexdigest()


def _runtime_abi_hash(pins, path):
    _need(isinstance(pins, dict), path, "sourcePins must be an object")
    values = [pins.get("unityVersion"), pins.get("target"), pins.get("architecture")]
    for repo in ("hybridclr", "il2cppPlus", "hybridclrUnity"):
        entry = pins.get(repo)
        _need(isinstance(entry, dict), path, f"sourcePins.{repo} is missing")
        values.append(entry.get("revision"))
    _need(all(isinstance(value, str) and value for value in values), path, "source pin identity is incomplete")
    return hashlib.sha256(("assembly-shadow-runtime-abi:1\n" + "\n".join(values)).encode("utf-8")).hexdigest()


def _canonical_assembly_name(value):
    """Mirror AssemblyIdentityUtil.CanonicalName for snapshot role hashing."""
    if not isinstance(value, str) or not value.strip():
        return ""
    name = value.strip().replace("\\", "/")
    name = name.rsplit("/", 1)[-1]
    if name.lower().endswith(".dll"):
        name = name[:-4]
    return name.strip().lower()


def _text(value):
    """StringBuilder.Append(object) renders null as an empty string in C#."""
    return "" if value is None else str(value)


REFLECTION_DEFINE_PREFIX = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_"
RETARGETING_FACADE_IDENTITY = "netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51"
M02_FIXED_IMAGE_SHA256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27"
M02_FIXED_IMAGE_PATH = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"
M02_REFLECTION_SITE_IDS = frozenset({
    "urp-debug-ui-prefab-types", "urp-serializable-enum-player",
    "urp-volume-assembly-domain", "urp-volume-type-domain", "m00-normal-hot-update-image",
})
M02_CANVAS_ALLOWED_TYPES = frozenset({
    "UnityEngine.Rendering.DebugUI+Value, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+BoolField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+IntField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+UIntField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+FloatField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+EnumField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Button, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Foldout, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ColorField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Vector2Field, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Vector3Field, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Vector4Field, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+VBox, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+HBox, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Container, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+BitField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+HistoryBoolField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+HistoryEnumField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Table, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+Table+Row, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+MessageBox, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ProgressBarValue, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ValueTuple, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ObjectField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ObjectListField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
    "UnityEngine.Rendering.DebugUI+ObjectPopupField, Unity.RenderPipelines.Core.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
})
M02_VOLUME_ALLOWED_TYPES = frozenset({
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
})


def _reflection_hash_add(buffer, value):
    """Append one ReflectionBindingConfiguration.BindingHash field."""
    if value is None:
        buffer.extend((-1).to_bytes(4, "little", signed=True))
        return
    encoded = str(value).encode("utf-8")
    buffer.extend(len(encoded).to_bytes(4, "little", signed=True))
    buffer.extend(encoded)


def _reflection_canonical_hash(configuration, path):
    sites = configuration.get("sites")
    _need(isinstance(sites, list), path, "sites must be an array")
    data = bytearray()
    _reflection_hash_add(data, "assembly-shadow-reflection-configuration:" + str(configuration.get("schemaVersion")))
    _reflection_hash_add(data, configuration.get("schemaVersion"))
    _reflection_hash_add(data, configuration.get("transformerVersion"))
    _reflection_hash_add(data, len(sites))
    for site in sorted(sites, key=lambda item: item.get("id", "")):
        for field in ("id", "assembly", "typeName", "methodSignature", "originalMethodHash"):
            _reflection_hash_add(data, site.get(field))
        _reflection_hash_add(data, site.get("operationIndex"))
        _reflection_hash_add(data, site.get("reason"))
        allowed = site.get("allowedTypes")
        _need(isinstance(allowed, list), path, "allowedTypes must be an array")
        _reflection_hash_add(data, len(allowed))
        for value in sorted(allowed):
            _reflection_hash_add(data, value)
        if configuration.get("schemaVersion") == 2:
            for field in ("kind", "imageSha256", "providerAssemblyIdentity", "imagePath"):
                _reflection_hash_add(data, site.get(field))
    return hashlib.sha256(data).hexdigest()


def _reflection_provider(value, path):
    _need(isinstance(value, str) and value and len(value) <= 4096, path,
         "allowedTypes entries must be bounded exact assembly-qualified names")
    parts = [part.strip() for part in value.split(",")]
    _need(len(parts) in (2, 5) and value == ", ".join(parts), path,
         "allowedTypes entries must use exact assembly-qualified syntax")
    _need(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*(?:\+[A-Za-z_][A-Za-z0-9_]*)*", parts[0]) is not None,
         path, "allowedTypes contains a non-concrete or malformed type")
    _need(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", parts[1]) is not None and not parts[1].lower().endswith(".dll"),
         path, "allowedTypes contains a malformed assembly name")
    if len(parts) == 5:
        _need(re.fullmatch(r"Version=[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", parts[2]) is not None and
              re.fullmatch(r"Culture=(?:neutral|[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)", parts[3]) is not None and
              re.fullmatch(r"PublicKeyToken=(?:null|[0-9a-f]{16})", parts[4]) is not None,
              path, "allowedTypes contains a malformed assembly identity")
    return parts[1]


def _reflection_full_identity(value, path):
    _need(isinstance(value, str) and value.strip(), path, "full assembly identity is required")
    parts = [part.strip() for part in value.split(",")]
    _need(len(parts) == 4 and value == ", ".join(parts), path, "full assembly identity syntax is invalid")
    _reflection_provider("Binding.Anchor, " + value, path)
    return value


def _reflection_parse(path: Path, raw: bytes):
    try:
        configuration = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"{path}: invalid reflection binding configuration: {error}") from error
    _need(isinstance(configuration, dict), path, "reflection binding configuration must be an object")
    schema = configuration.get("schemaVersion")
    transformer = configuration.get("transformerVersion")
    _need((schema == 1 and transformer == 1) or (schema == 2 and transformer == 2),
         path, "reflection binding configuration schema/transformer versions must match 1 or 2")
    sites = configuration.get("sites")
    _need(isinstance(sites, list) and 0 < len(sites) <= 4096, path,
         "reflection binding configuration sites must be a bounded non-empty array")
    ids = set(); methods = set(); declarations = []
    for index, site in enumerate(sites):
        site_path = f"{path}.sites[{index}]"
        _need(isinstance(site, dict), site_path, "reflection binding site must be an object")
        site_id = site.get("id"); assembly = site.get("assembly")
        _need(isinstance(site_id, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", site_id or ""), site_path,
             "site id is invalid")
        _need(site_id not in ids, site_path, "duplicate reflection binding site id")
        ids.add(site_id)
        _need(isinstance(assembly, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", assembly or "") is not None and
              not assembly.lower().endswith(".dll"), site_path, "site assembly is invalid")
        for field in ("typeName", "methodSignature", "reason"):
            _need(isinstance(site.get(field), str) and site[field].strip(), site_path, f"{field} is required")
        _hash64(site.get("originalMethodHash"), site_path, "originalMethodHash")
        operation = site.get("operationIndex")
        _need(isinstance(operation, int) and not isinstance(operation, bool) and operation >= 0, site_path,
             "operationIndex must be a non-negative integer")
        method_key = assembly + "\n" + site["typeName"] + "\n" + site["methodSignature"]
        _need(method_key not in methods, site_path, "duplicate reflection binding method site")
        methods.add(method_key)
        kind = site.get("kind") or "TypeGetType"
        _need((schema == 1 and kind == "TypeGetType") or
              (schema == 2 and kind in ("TypeGetType", "FiniteAssemblyList", "FiniteAssemblyTypes", "FixedAssemblyBytes")),
             site_path, "reflection binding acquisition kind is invalid")
        allowed = site.get("allowedTypes")
        _need(isinstance(allowed, list) and len(allowed) <= 4096, site_path, "allowedTypes must be a bounded array")
        if schema == 2:
            _need(site_id in M02_REFLECTION_SITE_IDS, site_path, "schema-2 reflection binding site id is not part of the M02 contract")
            if site_id == "urp-debug-ui-prefab-types":
                _need(kind == "TypeGetType" and set(allowed) == M02_CANVAS_ALLOWED_TYPES, site_path,
                     "schema-2 canvas site does not declare the exact 26 configured AQNs")
            elif site_id in ("urp-volume-assembly-domain", "urp-volume-type-domain"):
                _need(kind in ("FiniteAssemblyList", "FiniteAssemblyTypes") and set(allowed) == M02_VOLUME_ALLOWED_TYPES, site_path,
                     "schema-2 volume site does not declare the exact 17 Universal.Runtime AQNs")
            elif site_id == "urp-serializable-enum-player":
                _need(kind == "TypeGetType" and allowed == [], site_path,
                     "schema-2 serializable-enum site must deny all types")
        seen_allowed = set(); providers = []
        for allowed_index, value in enumerate(allowed):
            allowed_path = f"{site_path}.allowedTypes[{allowed_index}]"
            _need(value not in seen_allowed, allowed_path, "duplicate allowed type")
            seen_allowed.add(value)
            provider = _reflection_provider(value, allowed_path)
            if kind in ("FiniteAssemblyList", "FiniteAssemblyTypes"):
                _reflection_full_identity(value[value.index(",") + 2:], allowed_path)
            providers.append(_canonical_assembly_name(provider))
        image_sha = site.get("imageSha256")
        provider_identity = site.get("providerAssemblyIdentity")
        image_path = site.get("imagePath")
        if kind == "FixedAssemblyBytes":
            _need(not allowed, site_path, "FixedAssemblyBytes must have an empty allowedTypes array")
            _hash64(image_sha, site_path, "imageSha256")
            _reflection_full_identity(provider_identity, site_path)
            _need(isinstance(image_path, str) and image_path and not Path(image_path).is_absolute() and "\\" not in image_path and ":" not in image_path and
                  all(part not in ("", ".", "..") for part in image_path.split("/")), site_path, "imagePath is not a safe relative path")
            _need(site_id == "m00-normal-hot-update-image" and image_sha == M02_FIXED_IMAGE_SHA256 and
                  image_path == M02_FIXED_IMAGE_PATH and
                  provider_identity == "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
                 site_path, "fixed image site does not match the pinned M00 normal hot-update contract")
            providers = [_canonical_assembly_name(provider_identity.split(",", 1)[0])]
        else:
            _need(image_sha in (None, "") and provider_identity in (None, "") and image_path in (None, ""), site_path,
                 "non-fixed reflection binding site cannot claim image evidence")
        declarations.append({
            "id": site_id, "consumer": assembly, "typeName": site["typeName"],
            "methodSignature": site["methodSignature"], "originalMethodHash": site["originalMethodHash"],
            "operationIndex": operation, "allowedTypes": sorted(allowed), "reason": site["reason"],
            "providers": sorted(set(providers)), "kind": kind if schema == 2 else None,
            "imageSha256": image_sha, "providerAssemblyIdentity": provider_identity, "imagePath": image_path,
        })
    if schema == 2:
        _need(ids == M02_REFLECTION_SITE_IDS, path, "schema-2 reflection binding configuration must contain exactly the five M02 sites")
    return {
        "rawSha256": hashlib.sha256(raw).hexdigest(),
        "canonicalHash": _reflection_canonical_hash(configuration, path),
        "declarations": sorted(declarations, key=lambda item: item["id"]),
        "configuration": configuration,
    }


def _reflection_control(defines, path):
    _need(isinstance(defines, list), path, "extraScriptingDefines must be an array")
    # ReflectionBindingDefines.TryGetEnabledHash intentionally disables the
    # contract for editor-only compilation, even if a stale control token is
    # present in the serialized define list.
    if "UNITY_EDITOR" in defines:
        return None
    controls = []
    for index, value in enumerate(defines):
        define_path = f"{path}.extraScriptingDefines[{index}]"
        _need(isinstance(value, str), define_path, "compiler define must be a string")
        if value.startswith(REFLECTION_DEFINE_PREFIX):
            _need(re.fullmatch(re.escape(REFLECTION_DEFINE_PREFIX) + r"[0-9a-f]{64}", value) is not None,
                 define_path, "reflection binding control define must contain a lowercase raw SHA-256")
            controls.append(value[len(REFLECTION_DEFINE_PREFIX):])
    _need(len(controls) <= 1, path, "exactly one reflection binding control define is allowed")
    return controls[0] if controls else None


def _reflection_user_defines(defines, path):
    _reflection_control(defines, path)
    return [value for value in defines if not value.startswith(REFLECTION_DEFINE_PREFIX)]


def _retargeting_profile_hash(proof, path):
    forwarders = proof.get("forwarders")
    runtime = proof.get("runtimeFrameworkModules")
    _need(isinstance(forwarders, list) and isinstance(runtime, list), path,
         "retargeting forwarders and runtimeFrameworkModules must be arrays")
    data = bytearray()
    _reflection_hash_add(data, "assembly-shadow-reflection-retargeting-profile:1")
    _reflection_hash_add(data, proof.get("mappingPolicyVersion"))
    _reflection_hash_add(data, proof.get("facadeSha256"))
    _reflection_hash_add(data, proof.get("sourceAssemblyIdentity"))
    _reflection_hash_add(data, len(forwarders))
    for item in sorted(forwarders, key=lambda value: value.get("typeFullName", "")):
        _reflection_hash_add(data, item.get("typeFullName")); _reflection_hash_add(data, item.get("destinationAssemblyIdentity"))
    _reflection_hash_add(data, len(runtime))
    for item in sorted(runtime, key=lambda value: value.get("assemblyIdentity", "")):
        _reflection_hash_add(data, item.get("assemblyIdentity")); _reflection_hash_add(data, item.get("sha256")); _reflection_hash_add(data, item.get("mvid"))
    return hashlib.sha256(data).hexdigest()


def _verify_linked_reflection_evidence(root: Path, receipt: dict, reflection: dict, path: Path):
    directory = root / "ReflectionBindings" / "LinkedRetargeting"
    evidence_path = directory / "evidence.json"
    facade_path = directory / "netstandard.dll.bytes"
    _need(directory.is_dir() and not directory.is_symlink(), directory, "linked reflection retargeting directory is missing or symlinked")
    _need(evidence_path.is_file() and not evidence_path.is_symlink() and facade_path.is_file() and not facade_path.is_symlink(), directory,
         "linked reflection evidence requires evidence.json and netstandard.dll.bytes")
    entries = list(directory.rglob("*"))
    _need(not any(item.is_symlink() for item in entries), directory, "linked reflection evidence contains a symlinked entry")
    _need({item.resolve() for item in entries if item.is_file()} == {evidence_path.resolve(), facade_path.resolve()}, directory,
         "linked reflection retargeting directory must contain exactly its two proof files")
    proof = _json(evidence_path)
    _need(proof.get("schemaVersion") == 1 and proof.get("mappingPolicyVersion") == 1, evidence_path,
         "linked reflection evidence schema/mappingPolicyVersion must be 1")
    for field in ("unityVersion", "target", "architecture", "buildGuid", "il2cppDotNetProfile", "configurationSha256", "configurationHash",
                  "facadeSourcePath", "facadePath", "facadeSha256", "sourceAssemblyIdentity", "profileHash"):
        _string(proof.get(field), evidence_path, field)
    _need(proof["unityVersion"] == receipt.get("unityVersion") and proof["target"] == receipt.get("target") and
          proof["architecture"] == receipt.get("architecture") and proof["buildGuid"] == receipt.get("buildGuid"), evidence_path,
         "linked reflection evidence identity differs from Player receipt")
    _need(proof["configurationSha256"] == reflection["rawSha256"] and proof["configurationHash"] == reflection["canonicalHash"], evidence_path,
         "linked reflection evidence configuration identity differs from frozen configuration")
    _need(re.fullmatch(r"unityaot-[A-Za-z0-9-]+", proof["il2cppDotNetProfile"]) is not None,
         evidence_path, "il2cppDotNetProfile is not a permitted target-aware IL2CPP profile")
    _need(Path(proof["facadeSourcePath"]).is_absolute() and proof["facadePath"] == "ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes",
         evidence_path, "linked reflection facade path/source identity is invalid")
    facade_source = Path(proof["facadeSourcePath"])
    _need(facade_source.parent.name == "Facades" and facade_source.parent.parent.name == proof["il2cppDotNetProfile"], evidence_path,
         "facadeSourcePath does not belong to the recorded IL2CPP profile")
    _need(proof["sourceAssemblyIdentity"] == RETARGETING_FACADE_IDENTITY, evidence_path,
         "sourceAssemblyIdentity is not the pinned netstandard facade identity")
    _hash64(proof["facadeSha256"], evidence_path, "facadeSha256")
    _need(digest(facade_path) == proof["facadeSha256"], facade_path, "linked reflection facade SHA differs from evidence")
    forwarders = proof.get("forwarders"); runtime = proof.get("runtimeFrameworkModules"); sites = proof.get("sites")
    _need(isinstance(forwarders, list) and isinstance(runtime, list) and isinstance(sites, list), evidence_path,
         "linked reflection evidence arrays are missing")
    seen_types = set()
    for index, item in enumerate(forwarders):
        item_path = f"{evidence_path}.forwarders[{index}]"
        _need(isinstance(item, dict), item_path, "forwarder must be an object")
        type_name = _string(item.get("typeFullName"), item_path, "typeFullName")
        destination = _string(item.get("destinationAssemblyIdentity"), item_path, "destinationAssemblyIdentity")
        _need(type_name not in seen_types, item_path, "duplicate retargeting forwarder type")
        seen_types.add(type_name)
        _need("\n" not in destination, item_path, "destinationAssemblyIdentity is invalid")
    _need([item.get("typeFullName") for item in forwarders] == sorted(item.get("typeFullName") for item in forwarders),
         evidence_path, "forwarders are not in canonical ordinal order")
    _need(proof["profileHash"] == _retargeting_profile_hash(proof, evidence_path), evidence_path,
         "profileHash differs from canonical retargeting profile")
    linked = receipt.get("linkedPlayerReceipt")
    _need(isinstance(linked, dict), evidence_path, "linked Player receipt is missing")
    _need(linked.get("reflectionBindingEvidenceHash") == digest(evidence_path), evidence_path,
         "linked Player reflectionBindingEvidenceHash differs from evidence.json")
    linked_by_path = {}
    for index, item in enumerate(linked.get("assemblies") or []):
        if isinstance(item, dict):
            linked_by_path["LinkedPlayer/" + item.get("path", "")] = item
    seen_runtime = set()
    for index, item in enumerate(runtime):
        item_path = f"{evidence_path}.runtimeFrameworkModules[{index}]"
        _need(isinstance(item, dict), item_path, "runtime framework module must be an object")
        for field in ("assemblyIdentity", "path", "sha256", "mvid"):
            _string(item.get(field), item_path, field)
        _hash64(item["sha256"], item_path, "sha256")
        _need(item["path"].startswith("LinkedPlayer/Assemblies/") and ".." not in Path(item["path"]).parts,
             item_path, "runtime framework module path must be under LinkedPlayer")
        linked_item = linked_by_path.get(item["path"])
        _need(linked_item is not None and item["sha256"] == linked_item.get("sha256") and item["mvid"] == linked_item.get("mvid"),
             item_path, "runtime framework module does not match LinkedPlayer receipt")
        _need(item["assemblyIdentity"] not in seen_runtime, item_path, "duplicate runtime framework module")
        seen_runtime.add(item["assemblyIdentity"])
    _need([item.get("assemblyIdentity") for item in runtime] == sorted(item.get("assemblyIdentity") for item in runtime),
         evidence_path, "runtime framework modules are not in canonical ordinal order")
    expected_sites = {site["id"]: site for site in reflection["configuration"].get("sites", [])}
    _need(len(sites) == len(expected_sites), evidence_path, "linked reflection site proof count differs from configuration")
    linked_by_name = {_canonical_assembly_name(item.get("name")): item for item in linked.get("assemblies", []) if isinstance(item, dict)}
    input_by_name = {_canonical_assembly_name(item.get("name")): item for item in receipt.get("assemblies", []) if isinstance(item, dict)}
    seen_sites = set()
    for index, item in enumerate(sites):
        item_path = f"{evidence_path}.sites[{index}]"
        _need(isinstance(item, dict), item_path, "linked reflection site must be an object")
        site_id = _string(item.get("id"), item_path, "id")
        _need(site_id in expected_sites and site_id not in seen_sites, item_path, "linked reflection site is missing or duplicated")
        seen_sites.add(site_id)
        config_site = expected_sites[site_id]
        consumer = _canonical_assembly_name(config_site["assembly"])
        compiled = input_by_name.get(consumer); linked_item = linked_by_name.get(consumer)
        _need(compiled is not None and linked_item is not None, item_path, "linked reflection site consumer is absent")
        _need(item.get("consumer") == config_site["assembly"] and item.get("methodSignature") == config_site["methodSignature"] and
              item.get("operationIndex") == config_site["operationIndex"], item_path,
             "linked reflection site identity differs from configuration")
        _need(item.get("compiledPath") == compiled.get("path") and item.get("compiledSha256") == compiled.get("sha256") and
              item.get("linkedPath") == "LinkedPlayer/" + linked_item.get("path") and item.get("linkedSha256") == linked_item.get("sha256"), item_path,
             "linked reflection site paths or SHA differ from captured inputs")
        guard = "__AssemblyShadowReflectionBinding_" + reflection["canonicalHash"] + "_" + hashlib.sha256(site_id.encode("utf-8")).hexdigest()
        _need(item.get("guardMethod") == guard, item_path, "linked reflection guard identity differs from configuration")
        for field in ("compiledMethodHash", "linkedMethodHash", "compiledGuardHash", "linkedGuardHash"):
            _hash64(item.get(field), item_path, field)
    _need([item.get("id") for item in sites] == sorted(item.get("id") for item in sites), evidence_path,
         "linked reflection sites are not in canonical ordinal order")
    _need(seen_sites == set(expected_sites), evidence_path, "linked reflection site proof is incomplete")
    return proof


def _reflection_snapshot(root: Path, receipt: dict, path: Path, require_linked=False):
    expected = _reflection_control(receipt.get("extraScriptingDefines", []), path)
    directory = root / "ReflectionBindings"
    if expected is None:
        _need(not directory.exists() and not directory.is_symlink(), path,
             "snapshot without a reflection binding control define cannot contain ReflectionBindings evidence")
        linked = receipt.get("linkedPlayerReceipt")
        _need(not isinstance(linked, dict) or (linked.get("schemaVersion") != 2 and linked.get("reflectionBindingEvidenceHash") in (None, "")), path,
             "snapshot without a reflection binding control define cannot claim linked binding evidence")
        return None
    _need(directory.is_dir() and not directory.is_symlink(), directory,
         "ReflectionBindings evidence directory is missing or symlinked")
    config_path = directory / "configuration.json"
    _need(config_path.is_file() and not config_path.is_symlink(), config_path,
         "reflection binding configuration is missing or symlinked")
    entries = list(directory.rglob("*"))
    _need(not any(item.is_symlink() for item in entries), directory,
         "ReflectionBindings contains a symlinked entry")
    files = [item for item in entries if item.is_file()]
    raw = config_path.read_bytes()
    _need(hashlib.sha256(raw).hexdigest() == expected, config_path,
         "reflection binding configuration SHA differs from control define")
    reflection = _reflection_parse(config_path, raw)
    fixed_paths = []
    for site in reflection["configuration"].get("sites", []):
        if (site.get("kind") or "TypeGetType") != "FixedAssemblyBytes":
            continue
        image = directory / "Images" / (site["imageSha256"] + ".dll.bytes")
        _need(image.is_file() and not image.is_symlink(), image,
             "fixed assembly image evidence is missing or symlinked")
        _need(digest(image) == site["imageSha256"], image,
             "fixed assembly image SHA differs from configuration")
        fixed_paths.append(image.resolve())
    expected_files = {config_path.resolve(), *fixed_paths}
    if require_linked:
        expected_files.update({
            (directory / "LinkedRetargeting" / "evidence.json").resolve(),
            (directory / "LinkedRetargeting" / "netstandard.dll.bytes").resolve(),
        })
    _need({item.resolve() for item in files} == expected_files, directory,
         "ReflectionBindings contains undeclared or missing evidence files")
    assemblies = receipt.get("assemblies")
    _need(isinstance(assemblies, list), path, "assemblies must be an array for reflection binding provenance")
    for declaration in reflection["declarations"]:
        consumer = _canonical_assembly_name(declaration["consumer"])
        matching = [entry for entry in assemblies if isinstance(entry, dict) and _canonical_assembly_name(entry.get("name")) == consumer]
        _need(len(matching) == 1, path, f"reflection binding consumer is not exactly one unfiltered compiler input: {declaration['consumer']}")
        if require_linked:
            linked = receipt.get("linkedPlayerReceipt")
            _need(isinstance(linked, dict), path, f"linked Player evidence is missing for reflection binding consumer: {declaration['consumer']}")
            linked_receipt_path = root / "LinkedPlayer" / "linked-player-receipt.json"
            _need(linked_receipt_path.is_file() and not linked_receipt_path.is_symlink(), linked_receipt_path,
                 "linked Player receipt is missing or symlinked for reflection binding evidence")
            _need(_normal(_json(linked_receipt_path)) == _normal(linked), linked_receipt_path,
                 "linked Player receipt differs from the embedded snapshot receipt")
            _need(receipt.get("linkedPlayerReceiptHash") == _snapshot_linked_hash(linked), path,
                 "linkedPlayerReceiptHash differs from the linked Player receipt")
            linked_entries = [entry for entry in (linked.get("assemblies") or [])
                              if isinstance(entry, dict) and _canonical_assembly_name(entry.get("name")) == consumer]
            _need(len(linked_entries) == 1, path,
                 f"linked Player evidence is missing reflection binding consumer: {declaration['consumer']}")
            linked_entry_path = f"{path}.linkedPlayerReceipt.assemblies[{linked_entries.index(linked_entries[0])}]"
            linked_path = _relative(root / "LinkedPlayer", linked_entries[0].get("path"), linked_entry_path, "path")
            _need(linked_path.is_file() and not linked_path.is_symlink(), linked_path,
                 "linked reflection binding consumer file is missing or symlinked")
            _need(hashlib.sha256(linked_path.read_bytes()).hexdigest() == linked_entries[0].get("sha256"), linked_path,
                 "linked reflection binding consumer SHA differs from linked receipt")
    if require_linked:
        _verify_linked_reflection_evidence(root, receipt, reflection, path)
    return reflection


def _reflection_manifest(manifest: dict, reflection, path: Path):
    raw = manifest.get("reflectionBindingConfigurationSha256")
    canonical = manifest.get("reflectionBindingConfigurationHash")
    declarations = manifest.get("reflectionBindings")
    if reflection is None:
        _need(raw in (None, "") and canonical in (None, "") and declarations in (None, []), path,
             "manifest contains reflection binding claims without a verified configuration")
        return
    _need(raw == reflection["rawSha256"], path, "reflectionBindingConfigurationSha256 differs from frozen configuration")
    _need(canonical == reflection["canonicalHash"], path, "reflectionBindingConfigurationHash differs from canonical configuration")
    _need(isinstance(declarations, list), path, "reflectionBindings declaration projection must be an array")
    expected_declarations = reflection["declarations"]
    _need(len(declarations) == len(expected_declarations), path,
         "reflectionBindings declaration projection count differs from frozen configuration")
    normalized_declarations = []
    for index, (actual, expected) in enumerate(zip(declarations, expected_declarations)):
        declaration_path = f"{path}.reflectionBindings[{index}]"
        _need(isinstance(actual, dict), declaration_path, "reflection binding declaration must be an object")
        normalized = dict(actual)
        # JsonUtility writes null public string fields as empty strings. This
        # normalization is limited to fields whose frozen configuration has no
        # value; meaningful fixed-image claims remain exact and non-empty.
        for field in ("kind", "imageSha256", "providerAssemblyIdentity", "imagePath"):
            if normalized.get(field) == "" and expected.get(field) is None:
                normalized[field] = None
        normalized_declarations.append(normalized)
    _need(normalized_declarations == expected_declarations, path,
         "reflectionBindings declaration projection differs from frozen configuration")
    if isinstance(manifest.get("assemblies"), list) and isinstance(manifest.get("dependencyGraph"), list):
        known = {_canonical_assembly_name(item.get("name")) for item in manifest["assemblies"] if isinstance(item, dict)}
        graph = {(_canonical_assembly_name(item.get("consumer")), _canonical_assembly_name(item.get("provider")))
                 for item in manifest["dependencyGraph"] if isinstance(item, dict)}
        for declaration in declarations:
            consumer = _canonical_assembly_name(declaration["consumer"])
            for provider in declaration.get("providers") or []:
                provider = _canonical_assembly_name(provider)
                _need(provider in known, path, f"reflection binding provider is absent from manifest assembly graph: {provider}")
                _need((consumer, provider) in graph or consumer == provider, path,
                     f"reflection binding provider edge is absent from manifest dependency graph: {consumer} -> {provider}")


def _reflection_copy(root: Path, reflection, path: Path):
    directory = root / "ReflectionBindings"
    if reflection is None:
        _need(not directory.exists() and not directory.is_symlink(), path,
             "artifact contains ReflectionBindings without a verified configuration")
        return
    _need(directory.is_dir() and not directory.is_symlink(), directory, "artifact ReflectionBindings directory is missing")
    config_path = directory / "configuration.json"
    _need(config_path.is_file() and not config_path.is_symlink(), config_path, "artifact reflection configuration is missing")
    entries = list(directory.rglob("*"))
    _need(not any(item.is_symlink() for item in entries), directory,
         "artifact ReflectionBindings contains a symlinked entry")
    raw = config_path.read_bytes()
    _need(hashlib.sha256(raw).hexdigest() == reflection["rawSha256"], config_path,
         "artifact reflection configuration SHA differs from compiled configuration")
    parsed = _reflection_parse(config_path, raw)
    _need(parsed["canonicalHash"] == reflection["canonicalHash"] and parsed["declarations"] == reflection["declarations"], config_path,
         "artifact reflection configuration differs from compiled configuration")
    expected_files = {config_path.resolve()}
    for site in parsed["configuration"].get("sites", []):
        if (site.get("kind") or "TypeGetType") != "FixedAssemblyBytes":
            continue
        image = directory / "Images" / (site["imageSha256"] + ".dll.bytes")
        _need(image.is_file() and not image.is_symlink() and digest(image) == site["imageSha256"], image,
             "artifact fixed assembly image evidence is missing or stale")
        expected_files.add(image.resolve())
    _need({item.resolve() for item in entries if item.is_file()} == expected_files, directory,
         "artifact ReflectionBindings contains undeclared or missing evidence files")


def _verify_reflection_probe(path: Path, receipt: dict, reflection):
    """Verify the executable M02 reflection acceptance probe against frozen evidence."""
    _need(isinstance(reflection, dict), path, "reflection probe requires verified frozen reflection configuration")
    probe = _json(path)
    _need(isinstance(probe, dict), path, "reflection probe result must be an object")
    probe_schema = probe.get("schemaVersion")
    _need(probe_schema in (1, 2) and probe.get("milestone") == "M02" and
          probe.get("mode") == "M02ReflectionBindings", path,
         "reflection probe schema, milestone or mode is invalid")
    _need(probe.get("result") == "Passed" and probe.get("il2cpp") is True, path,
         "reflection probe must be a passed IL2CPP Player result")
    _need(probe.get("error") in (None, ""), path, "passed reflection probe must not contain an error")
    for field in ("unityVersion", "platform", "buildGuid", "playerDataPath", "configurationSha256", "configurationHash",
                  "canvasGuard", "enumGuard"):
        _string(probe.get(field), path, field)
    _need(probe["unityVersion"] == receipt.get("unityVersion"), path,
         "reflection probe Unity version differs from Player snapshot")
    _need(probe["platform"] == "OSXPlayer", path, "reflection probe platform must be OSXPlayer")
    _need(probe["buildGuid"] == receipt.get("buildGuid"), path,
         "reflection probe buildGuid differs from Player snapshot")
    _need(probe["configurationSha256"] == reflection.get("rawSha256") and
          probe["configurationHash"] == reflection.get("canonicalHash"), path,
         "reflection probe configuration hashes differ from frozen Player configuration")
    output_value = _string(receipt.get("playerOutput"), path, "Player snapshot playerOutput")
    output = Path(output_value)
    _need(output.is_absolute() and output.exists() and not output.is_symlink(), path,
         "Player snapshot playerOutput is missing or symlinked")
    expected_data = output / "Contents" if output.suffix.lower() == ".app" else output
    _need(Path(probe["playerDataPath"]).is_absolute() and
          Path(probe["playerDataPath"]).resolve() == expected_data.resolve(), path,
         "reflection probe playerDataPath does not identify the captured Player output")
    staged = []
    for candidate in output.rglob("reflection-bindings.json"):
        if candidate.is_file() and not candidate.is_symlink():
            parts = candidate.relative_to(output).parts
            if len(parts) >= 4 and parts[-4:] == ("StreamingAssets", "AssemblyShadow", "M02", "reflection-bindings.json"):
                staged.append(candidate)
    _need(len(staged) == 1 and digest(staged[0]) == reflection.get("rawSha256"), path,
         "staged Player reflection configuration is missing, duplicated or stale")
    configuration = reflection.get("configuration") or {}
    sites = configuration.get("sites") or []
    canvas = next((site for site in sites if isinstance(site, dict) and site.get("id") == "urp-debug-ui-prefab-types"), None)
    enum = next((site for site in sites if isinstance(site, dict) and site.get("id") == "urp-serializable-enum-player"), None)
    _need(isinstance(canvas, dict) and isinstance(canvas.get("allowedTypes"), list) and len(canvas["allowedTypes"]) == 26 and
          isinstance(enum, dict) and enum.get("allowedTypes") == [], path,
         "reflection probe finite domains do not match the frozen configuration")
    guard_prefix = "__AssemblyShadowReflectionBinding_"
    for field, site in (("canvasGuard", canvas), ("enumGuard", enum)):
        expected_guard = guard_prefix + reflection["canonicalHash"] + "_" + hashlib.sha256(site["id"].encode("utf-8")).hexdigest()
        _need(probe[field] == expected_guard, path, f"{field} does not identify the frozen site/configuration")
    if probe_schema == 2:
        site_map = {site.get("id"): site for site in sites if isinstance(site, dict)}
        expected_ids = {"urp-debug-ui-prefab-types", "urp-serializable-enum-player", "urp-volume-assembly-domain",
                        "urp-volume-type-domain", "m00-normal-hot-update-image"}
        _need(set(site_map) == expected_ids, path, "schema-2 reflection probe configuration sites are incomplete")
        finite_assembly = site_map["urp-volume-assembly-domain"]
        finite_types = site_map["urp-volume-type-domain"]
        fixed_image = site_map["m00-normal-hot-update-image"]
        _need(finite_assembly.get("kind") == "FiniteAssemblyList" and finite_types.get("kind") == "FiniteAssemblyTypes" and
              isinstance(finite_assembly.get("allowedTypes"), list) and len(finite_assembly["allowedTypes"]) == 17 and
              finite_assembly["allowedTypes"] == finite_types.get("allowedTypes") and
              fixed_image.get("kind") == "FixedAssemblyBytes" and fixed_image.get("allowedTypes") == [], path,
             "schema-2 finite/image acquisition domains do not match the frozen configuration")
        _need(probe.get("finiteAssemblyGuard") == guard_prefix + reflection["canonicalHash"] + "_" + hashlib.sha256(finite_assembly["id"].encode("utf-8")).hexdigest() and
              probe.get("finiteTypesGuard") == guard_prefix + reflection["canonicalHash"] + "_" + hashlib.sha256(finite_types["id"].encode("utf-8")).hexdigest() and
              probe.get("fixedImageGuard") == guard_prefix + reflection["canonicalHash"] + "_" + hashlib.sha256(fixed_image["id"].encode("utf-8")).hexdigest(), path,
             "schema-2 finite/image guard identities are invalid")
        _need(probe.get("discoveryAllowedTypes") == sorted(finite_types["allowedTypes"]) and
              probe.get("discoveryAssemblyNames") == ["Unity.RenderPipelines.Universal.Runtime"] and
              probe.get("discoveryDeniedBeforeEnumeration") is True, path,
             "schema-2 discovery evidence does not cover the exact finite domain")
        _hash64(fixed_image.get("imageSha256"), path, "fixedImage.imageSha256")
        _need(probe.get("fixedImageSha256") == fixed_image["imageSha256"] and
              probe.get("fixedImageLoadedAssembly") == fixed_image.get("providerAssemblyIdentity") and
              probe.get("fixedImageLoadedMarker") == "M00-HOTUPDATE-OK" and
              probe.get("fixedImageTamperRejected") is True and probe.get("fixedImageNullRejected") is True and
              probe.get("fixedImageCallerBytesUnchanged") is True and
              probe.get("volumeManagerMatchesContract") is True, path,
             "schema-2 fixed-image acceptance evidence is incomplete")
    allowed = probe.get("allowed")
    expected_allowed = []
    for value in sorted(canvas["allowedTypes"]):
        parts = [part.strip() for part in value.split(",")]
        expected_allowed.append({"input": value, "type": parts[0], "assembly": parts[1]})
    _need(isinstance(allowed, list) and allowed == expected_allowed, path,
         "reflection probe allowed results do not cover the exact 26 configured AQNs")
    expected_names = ["candidate", "generic-provider-escape", "null", "unqualified", "unknown", "mutated-string",
                      "runtime-prefab-mutation", "serializable-enum-deny-all"]
    denied = probe.get("denied")
    _need(isinstance(denied, list) and [item.get("name") for item in denied if isinstance(item, dict)] == expected_names,
         path, "reflection probe denied results must contain the exact eight vectors")
    candidate = "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal"
    expected_inputs = {
        "candidate": candidate,
        "generic-provider-escape": "System.Collections.Generic.List`1[[" + candidate + "]], mscorlib",
        "null": None,
        "unqualified": "UnityEngine.Rendering.DebugUI+Value",
        "unknown": "AssemblyShadowUnknown.Type, AssemblyShadowUnknown",
        "mutated-string": canvas["allowedTypes"][0] + " ",
        "runtime-prefab-mutation": candidate,
    }
    for index, item in enumerate(denied):
        item_path = f"{path}.denied[{index}]"
        _need(isinstance(item, dict), item_path, "denied result must be an object")
        name = item.get("name")
        _need(item.get("denied") is True and item.get("exceptionType") == "System.InvalidOperationException" and
              item.get("assemblyResolveEvents") == 0 and isinstance(item.get("message"), str), item_path,
             "denied result does not prove the expected guarded exception")
        site_id = "urp-serializable-enum-player" if name == "serializable-enum-deny-all" else "urp-debug-ui-prefab-types"
        _need(item["message"] == "AssemblyShadow reflection denied; configuration=" + reflection["canonicalHash"] + "; site=" + site_id,
             item_path, "denied result has an unexpected guard message")
        if name in expected_inputs:
            expected_input = expected_inputs[name]
            if expected_input is None:
                # Unity JsonUtility materializes a null string field as the
                # empty string on readback. The explicit marker remains the
                # authoritative null distinction; non-empty values are not
                # accepted as an equivalent representation.
                _need(item.get("input") in (None, "") and item.get("inputWasNull") is True, item_path,
                     "denied vector null input must be empty/null with inputWasNull=true")
            else:
                _need(item.get("input") == expected_input and item.get("inputWasNull") is False, item_path,
                     "denied vector input or null-input marker differs from the exact probe contract")
        else:
            _need(isinstance(item.get("input"), str) and item["input"], item_path,
                 "serializable-enum-deny-all input must be a non-empty assembly-qualified name")
            _need(item.get("inputWasNull") is False, item_path, "serializable-enum-deny-all input cannot be null")
    result = {"result": "Passed", "allowed": len(allowed), "denied": len(denied), "assemblyResolveEvents": 0}
    if probe_schema == 2:
        result["discoveryAllowedTypes"] = len(probe["discoveryAllowedTypes"])
        result["fixedImageSha256"] = probe["fixedImageSha256"]
    return result


def _verify_source_pins(pins, path, expected=None):
    """Validate the complete source-pin DTO, including demo provenance.

    RuntimeAbiHash intentionally excludes the demo revision, so checking only
    that derived value would allow a different demo source tree to masquerade
    as the same runtime ABI.  The manifest, Player receipt and resource receipt
    must therefore carry the same complete four-repository pin object.
    """
    _need(isinstance(pins, dict), path, "sourcePins must be an object")
    _need(pins.get("schemaVersion") == 1, path, "sourcePins schemaVersion must be 1")
    for field in ("unityVersion", "target", "architecture"):
        _string(pins.get(field), path, field)
    for repo in ("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"):
        entry = pins.get(repo)
        entry_path = f"{path}.{repo}"
        _need(isinstance(entry, dict), entry_path, "repository pin is missing")
        _string(entry.get("url"), entry_path, "url")
        revision = _string(entry.get("revision"), entry_path, "revision")
        _need(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, entry_path,
             "revision must be an exact forty-character commit SHA")
    if expected is not None:
        _need(_normal(pins) == _normal(expected), path, "source pins differ from baseline provenance")


def _snapshot_files(receipt, root: Path, path: Path, validate_sections=True):
    arrays = (("assemblies", receipt.get("assemblies")), ("filteredAssemblies", receipt.get("filteredAssemblies")),
              ("references", receipt.get("references")))
    by_name = {}
    all_files = []
    for section, entries in arrays:
        _need(isinstance(entries, list), path, f"{section} must be an array")
        for index, entry in enumerate(entries):
            entry_path = f"{path}.{section}[{index}]"
            _need(isinstance(entry, dict), entry_path, "snapshot entry must be an object")
            name = _name(entry.get("name"), entry_path, "name")
            _need("/" not in name and "\\" not in name, entry_path, "assembly name must not contain path separators")
            if validate_sections:
                section_path = {"assemblies": "Assemblies", "filteredAssemblies": "Assemblies/Filtered", "references": "References"}[section]
                _need(entry.get("path") == f"{section_path}/{name}.dll", entry_path,
                     "captured DLL cannot be renamed or moved between input/reference/filter roles")
                if entry.get("pdbPath"):
                    _need(entry.get("pdbPath") == f"{section_path}/{name}.pdb", entry_path,
                         "captured PDB cannot be renamed or moved between input/reference/filter roles")
            _need(name not in by_name, entry_path, f"duplicate snapshot assembly: {name}")
            by_name[name] = entry
            all_files.append(entry)
            dll = _relative(root, entry.get("path"), entry_path, "path")
            _need(digest(dll) == entry.get("sha256"), entry_path, "snapshot DLL SHA-256 differs from bytes")
            if entry.get("pdbPath"):
                pdb = _relative(root, entry["pdbPath"], entry_path, "pdbPath")
                _need(digest(pdb) == entry.get("pdbSha256"), entry_path, "snapshot PDB SHA-256 differs from bytes")
    expected = {str(path.resolve()) for entry in all_files for path in [root / entry["path"]]}
    actual = {str(path.resolve()) for path in root.rglob("*.dll")
             if "LinkedPlayer" not in path.relative_to(root).parts}
    _need(expected == actual, path, "snapshot DLL inventory contains undeclared or missing files")
    return by_name, all_files


def _snapshot_hash(receipt, root: Path, path):
    text = ["assembly-shadow-snapshot:1\n"]
    text.extend(_text(receipt.get(field, "")) + "\n" for field in ("kind", "unityVersion", "target", "architecture"))
    text.append(_runtime_abi_hash(receipt.get("sourcePins"), path) + "\n")
    text.append(("filtered-proof" if receipt.get("playerBuildFilterCaptured") is True else "compiler-output") + "\n")
    text.append(str(receipt.get("playerBuildOptions", 0)) + "\n")
    for name in sorted(receipt.get("normalHotUpdateAssemblies") or []): text.append("normal:" + name + "\n")
    roles = receipt.get("filteredAssemblyCapabilities") or []
    _need(isinstance(roles, list), path, "filteredAssemblyCapabilities must be an array")
    for role in sorted(roles, key=lambda item: item.get("name", "") if isinstance(item, dict) else ""):
        _need(isinstance(role, dict), path, "filtered capability must be an object")
        text.append("filtered-role:" + _canonical_assembly_name(_name(role.get("name"), path, "filteredAssemblyCapabilities.name")) + ":" +
                    _text(role.get("classification", 0)) + ":" + _text(role.get("isPrecompiled", False)) + ":" +
                    _text(role.get("isShadowCapable", False)) + ":" + _text(role.get("isBootstrap", False)) + ":" +
                    _text(role.get("capabilityDeclared", False)) + "\n")
    text.append("linked-player:" + _text(receipt.get("linkedPlayerReceiptHash")) + "\n")
    for name in sorted(receipt.get("linkerExcludedAssemblies") or []):
        text.append("linker-excluded:" + _text(name) + "\n")
    linker_roles = receipt.get("linkerExcludedAssemblyCapabilities") or []
    _need(isinstance(linker_roles, list), path, "linkerExcludedAssemblyCapabilities must be an array")
    for role in sorted(linker_roles, key=lambda item: item.get("name", "") if isinstance(item, dict) else ""):
        _need(isinstance(role, dict), path, "linker-excluded capability must be an object")
        text.append("linker-excluded-role:" + _canonical_assembly_name(_text(role.get("name"))) + ":" +
                    _text(role.get("classification", 0)) + ":" + _text(role.get("isPrecompiled", False)) + ":" +
                    _text(role.get("isShadowCapable", False)) + ":" + _text(role.get("isBootstrap", False)) + ":" +
                    _text(role.get("capabilityDeclared", False)) + "\n")
    for define in sorted(receipt.get("extraScriptingDefines") or []): text.append(_text(define) + "\n")
    _, all_files = _snapshot_files(receipt, root, path, validate_sections=False)
    for entry in sorted(all_files, key=lambda item: item.get("path", "")):
        for field in ("path", "sha256", "pdbPath", "pdbSha256"):
            text.append(str(entry.get(field, "")) + "\n")
    return hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _hash64(value, path, field):
    _need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
          path, f"{field} must be a lowercase SHA-256")
    return value


def _linked_claim_absent(receipt):
    """Mirror ShadowLinkedPlayerEvidence.IsAbsent after Unity JSON materialization."""
    if receipt.get("linkedPlayerReceiptHash") not in (None, ""):
        return False
    for field in ("linkerExcludedAssemblies", "linkerExcludedAssemblyCapabilities"):
        values = receipt.get(field)
        if values is not None and (not isinstance(values, list) or len(values) != 0):
            return False
    linked = receipt.get("linkedPlayerReceipt")
    if linked is None:
        return True
    # A raw `{}` also materializes as the DTO's constructor-default object in
    # Unity (schemaVersion 1); Python's missing key is the equivalent absence.
    if not isinstance(linked, dict) or linked.get("schemaVersion") not in (None, 0, 1):
        return False
    for field in ("buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"):
        if linked.get(field) not in (None, ""):
            return False
    if linked.get("reflectionBindingEvidenceHash") not in (None, ""):
        return False
    for field in ("protectedAssemblies", "assemblies"):
        values = linked.get(field)
        if values is not None and (not isinstance(values, list) or len(values) != 0):
            return False
    return True


def _canonical_names(values, path, field):
    _need(isinstance(values, list), path, f"{field} must be an array")
    names = []
    for index, value in enumerate(values):
        item_path = f"{path}.{field}[{index}]"
        name = _name(value, item_path, "name")
        canonical = _canonical_assembly_name(name)
        _need(name == canonical, item_path, "assembly identity must be canonical lowercase")
        _need(canonical not in names, item_path, "duplicate assembly identity")
        names.append(canonical)
    return set(names)


def _verify_linked_player(snapshot: Path, receipt: dict, descriptors: dict, path: Path):
    linked_root = snapshot / "LinkedPlayer"
    linked_path = linked_root / "linked-player-receipt.json"
    linked = _json(linked_path)
    _need(linked.get("schemaVersion") in (1, 2), linked_path, "linked player receipt schemaVersion must be 1 or 2")
    for field in ("buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"):
        _string(linked.get(field), linked_path, field)
    _need(Path(linked["sourceDirectory"]).is_absolute(), linked_path, "sourceDirectory must be absolute")
    _need(linked.get("buildGuid") == receipt.get("buildGuid") and
          linked.get("nativeLibrarySha256") == receipt.get("nativeLibrarySha256") and
          linked.get("target") == receipt.get("target") and linked.get("architecture") == receipt.get("architecture"),
          linked_path, "linked Player evidence identity differs from the Player receipt")
    binding_enabled = _reflection_control(receipt.get("extraScriptingDefines", []), path) is not None
    if binding_enabled:
        _need(linked.get("schemaVersion") == 2, linked_path,
             "reflection-bound Player requires linked receipt schemaVersion 2")
        _hash64(linked.get("reflectionBindingEvidenceHash"), linked_path, "reflectionBindingEvidenceHash")
    else:
        _need(linked.get("schemaVersion") == 1 and linked.get("reflectionBindingEvidenceHash") in (None, ""), linked_path,
             "schema 1 linked Player evidence cannot claim reflection-binding proof")
    _hash64(linked["nativeLibrarySha256"], linked_path, "nativeLibrarySha256")
    _need(receipt.get("linkedPlayerReceiptHash") == _hash64(receipt.get("linkedPlayerReceiptHash"), path, "linkedPlayerReceiptHash"),
          path, "linkedPlayerReceiptHash is missing")
    _need(_snapshot_linked_hash(linked) == receipt["linkedPlayerReceiptHash"], linked_path,
          "linkedPlayerReceiptHash differs from receipt")
    protected = _canonical_names(linked.get("protectedAssemblies"), linked_path, "protectedAssemblies")
    _need(protected == {_canonical_assembly_name(name) for name in CANDIDATES | {BOOTSTRAP}}, linked_path,
          "linked protectedAssemblies must contain exactly the five candidates and Bootstrap")
    files = linked.get("assemblies")
    _need(isinstance(files, list) and files, linked_path, "linked assemblies are missing")
    linked_names = set()
    expected_files = {linked_path.resolve()}
    for index, item in enumerate(files):
        item_path = f"{linked_path}.assemblies[{index}]"
        _need(isinstance(item, dict), item_path, "linked assembly entry must be an object")
        name = _name(item.get("name"), item_path, "name")
        canonical = _canonical_assembly_name(name)
        _need(name == canonical and name not in linked_names, item_path, "linked assembly name must be unique canonical lowercase")
        _need(item.get("path") == f"Assemblies/{name}.dll", item_path, "linked assembly path is not canonical")
        _hash64(item.get("sha256"), item_path, "sha256")
        try:
            parsed = uuid.UUID(_string(item.get("mvid"), item_path, "mvid"))
        except (ValueError, AttributeError) as error:
            raise VerificationError(f"{item_path}.mvid: invalid GUID") from error
        _need(parsed.int != 0, item_path, "mvid must not be empty")
        dll = _relative(linked_root, item["path"], item_path, "path")
        _need(digest(dll) == item["sha256"], item_path, "linked DLL SHA-256 differs from bytes")
        expected_files.add(dll.resolve())
        pdb_path = item.get("pdbPath")
        pdb_sha = item.get("pdbSha256")
        if pdb_path or pdb_sha:
            _need(pdb_path == f"Assemblies/{name}.pdb", item_path, "linked PDB path is not canonical")
            _hash64(pdb_sha, item_path, "pdbSha256")
            pdb = _relative(linked_root, pdb_path, item_path, "pdbPath")
            _need(digest(pdb) == pdb_sha, item_path, "linked PDB SHA-256 differs from bytes")
            expected_files.add(pdb.resolve())
        linked_names.add(name)
    for item in linked_root.rglob("*"):
        _need(not item.is_symlink(), item, "linked Player proof contains a symlink")
    actual_files = {item.resolve() for item in linked_root.rglob("*") if item.is_file()}
    _need(actual_files == expected_files, linked_root, "linked Player proof contains undeclared or missing files")
    descriptor_by_name = {}
    for descriptor_name, descriptor in descriptors.items():
        canonical_descriptor_name = _canonical_assembly_name(descriptor_name)
        _need(canonical_descriptor_name not in descriptor_by_name, path,
             f"baseline descriptors contain duplicate canonical assembly identity: {descriptor_name}")
        descriptor_by_name[canonical_descriptor_name] = descriptor
    player_names = {_canonical_assembly_name(entry["name"]) for entry in receipt.get("assemblies", [])}
    excluded = _canonical_names(receipt.get("linkerExcludedAssemblies"), path, "linkerExcludedAssemblies")
    _need(excluded == player_names - linked_names, path,
          "linkerExcludedAssemblies must equal Player inputs absent from linked output")
    _need(not (excluded & protected), path, "linker exclusions cannot contain protected candidates or Bootstrap")
    normal_values = receipt.get("normalHotUpdateAssemblies") or []
    _need(isinstance(normal_values, list), path, "normalHotUpdateAssemblies must be an array")
    normal_names = set()
    for index, value in enumerate(normal_values):
        normal_path = f"{path}.normalHotUpdateAssemblies[{index}]"
        normal_name = _canonical_assembly_name(_name(value, normal_path, "name"))
        _need(normal_name and normal_name not in normal_names, normal_path, "duplicate normal hot-update assembly identity")
        normal_names.add(normal_name)
    roles = receipt.get("linkerExcludedAssemblyCapabilities")
    _need(isinstance(roles, list), path, "linkerExcludedAssemblyCapabilities must be an array")
    role_names = set()
    for index, role in enumerate(roles):
        role_path = f"{path}.linkerExcludedAssemblyCapabilities[{index}]"
        _need(isinstance(role, dict), role_path, "linker-excluded capability must be an object")
        raw_name = _name(role.get("name"), role_path, "name")
        name = _canonical_assembly_name(raw_name)
        _need(name, role_path, "linker-excluded capability name must contain an assembly identity")
        _need(name in excluded and name not in role_names, role_path, "linker-excluded capability does not match exclusions")
        _need(role.get("classification") in (0, 1, 2, 3, 4), role_path,
             "linker-excluded capability must preserve an original source role (0 through 4)")
        _need((role["classification"] == 4) == (name in normal_names), role_path,
             "linker-excluded capability normal-hot-update membership disagrees with its original classification")
        _need(role.get("isShadowCapable") is not True and role.get("isBootstrap") is not True, role_path,
             "linker-excluded capability cannot be a candidate or Bootstrap")
        role_names.add(name)
        descriptor = descriptor_by_name.get(name)
        _need(descriptor is not None, role_path, "linker-excluded capability is absent from baseline descriptors")
        expected_classification = 4 if role["classification"] == 4 else 5
        _need(descriptor.get("classification") == expected_classification, role_path,
             "linker-excluded projected descriptor classification differs from its original role")
        for field in ("isPrecompiled", "isShadowCapable", "isBootstrap", "capabilityDeclared"):
            _need(descriptor.get(field, False) == role.get(field, False), role_path,
                  f"linker-excluded role {field} differs from baseline descriptor")
    _need(role_names == excluded, path, "linker-excluded capability inventory is incomplete")
    _need(protected <= linked_names and protected <= player_names, linked_path,
          "all protected candidates and Bootstrap must be present in linked output")
    return linked, linked_names


def _snapshot_linked_hash(linked):
    schema = linked.get("schemaVersion", 1)
    text = ["assembly-shadow-linked-player:" + _text(schema) + "\n"]
    text.extend(_text(linked.get(field)) + "\n" for field in ("schemaVersion", "buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"))
    if schema == 2:
        text.append("reflection-bindings:" + _text(linked.get("reflectionBindingEvidenceHash")) + "\n")
    for name in sorted(linked.get("protectedAssemblies") or []):
        text.append("protected:" + _text(name) + "\n")
    for item in sorted(linked.get("assemblies") or [], key=lambda value: value.get("path", "") if isinstance(value, dict) else ""):
        _need(isinstance(item, dict), "linkedPlayerReceipt", "linked assembly entry must be an object")
        for field in ("name", "path", "sha256", "mvid", "pdbPath", "pdbSha256"):
            text.append(_text(item.get(field)) + "\n")
    return hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _verify_editor_report(path: Path):
    report = _json(path)
    _need(isinstance(report, dict), path, "report must be an object")
    _need(report.get("schemaVersion") == 1, path, "schemaVersion must be 1")
    _need(report.get("result") == "Passed", path, "result must be Passed")
    _string(report.get("runDirectory"), path, "runDirectory")
    run = _root(Path(report["runDirectory"]), f"{path}.runDirectory")
    cases = report.get("cases")
    _need(isinstance(cases, list), path, "cases must be an array")
    observed = []
    for index, case in enumerate(cases):
        case_path = f"{path}.cases[{index}]"
        _need(isinstance(case, dict), case_path, "case must be an object")
        observed.append(_name(case.get("id"), case_path, "id"))
        _need(case.get("passed") is True, case_path, "passed must be true")
    _need(set(observed) == CASE_IDS and len(observed) == len(CASE_IDS), path,
         "cases must contain T02-01..T02-07, M02-Repeatability, M02-SnapshotTamper, linked-evidence cases and M02-StructuralPatchEditorDomain")
    _need(isinstance(report.get("artifacts"), list), path, "artifacts must be an array")
    artifacts = {}
    for index, artifact in enumerate(report["artifacts"]):
        artifact_path = f"{path}.artifacts[{index}]"
        _need(isinstance(artifact, dict), artifact_path, "artifact must be an object")
        artifact_id = _name(artifact.get("id"), artifact_path, "id")
        _need(artifact_id not in artifacts, artifact_path, f"duplicate artifact id: {artifact_id}")
        artifact_file = _absolute_file(artifact.get("path"), artifact_path, "path")
        _need(isinstance(artifact.get("sha256"), str) and artifact["sha256"], artifact_path,
             "sha256 must be present")
        _need(digest(artifact_file) == artifact["sha256"], artifact_path, "artifact SHA-256 differs from bytes")
        _need(artifact_file.name == "patch-manifest.json", artifact_path, "artifact must be patch-manifest.json")
        _need(artifact_file.parent.resolve().is_relative_to(run), artifact_path,
             "patch artifact root must be below report.runDirectory")
        artifacts[artifact_id] = artifact_file
    _need(set(artifacts) == PATCH_IDS, path, "artifacts must contain P01, P02, P03, P05-requires-bundles and P01-repeat exactly")
    baseline_path = _absolute_file(report.get("baselineManifestPath"), path, "baselineManifestPath")
    _need(report.get("baselineManifestSha256") == digest(baseline_path), path,
         "baselineManifestSha256 differs from actual baseline-manifest.json")
    _need(baseline_path.name == "baseline-manifest.json", path, "baselineManifestPath must name baseline-manifest.json")
    return report, run, baseline_path, artifacts


def _verify_sidecar_manifest(root: Path, manifest: dict, path: Path):
    _need(manifest.get("schemaVersion") == 1 and manifest.get("semanticHashSchema") == 1,
         path, "manifest schemaVersion and semanticHashSchema must be 1")
    manifest_sidecar = root / "manifest.sha256"
    _need(manifest_sidecar.is_file() and not manifest_sidecar.is_symlink(), manifest_sidecar,
         "manifest SHA sidecar is missing")
    _need(manifest_sidecar.read_text().strip() == digest(path), manifest_sidecar,
         "manifest SHA sidecar differs from baseline-manifest.json")
    for field in ("baselineBuildId", "unityVersion", "target", "architecture", "runtimeAbiHash",
                  "bootstrapAbiHash", "resourceAbiHash", "resourceIndexHash", "playerInputSnapshotHash",
                  "playerBuildGuid", "nativeLibrarySha256", "resourceBaselinePath", "resourceBuildReceiptHash"):
        _string(manifest.get(field), path, field)
    _need(manifest["target"] == TARGET, path, "target must be StandaloneOSX")
    sidecars = {
        "resource-abi.json": root / "resource-abi.json",
        "resource-script-index.json": root / "resource-script-index.json",
        "source-pins.json": root / "source-pins.json",
        "policy.json": root / "policy.json",
    }
    for name, sidecar in sidecars.items():
        _need(sidecar.is_file() and not sidecar.is_symlink(), f"{path.parent}/{name}", "required baseline sidecar is missing")
    abi = _json(sidecars["resource-abi.json"])
    index = _json(sidecars["resource-script-index.json"])
    _need(abi.get("schemaVersion") == 2, sidecars["resource-abi.json"], "resource ABI schemaVersion must be 2")
    _need(index.get("schemaVersion") == 2, sidecars["resource-script-index.json"], "resource script index schemaVersion must be 2")
    _need(abi.get("unknowns") in (None, []), sidecars["resource-abi.json"], "baseline resource ABI contains unknown entries")
    _need(index.get("hasUnknown") in (None, False) and index.get("unknowns") in (None, []),
         sidecars["resource-script-index.json"], "baseline resource index contains unknown entries")
    _need(_resource_abi_hash(abi) == manifest.get("resourceAbiHash"), sidecars["resource-abi.json"],
         "resourceAbiHash does not match resource-abi.json")
    source_pins = _json(sidecars["source-pins.json"])
    _verify_source_pins(source_pins, sidecars["source-pins.json"], manifest.get("sourcePins"))
    _need(_normal(source_pins) == _normal(manifest.get("sourcePins")), sidecars["source-pins.json"],
         "source-pins.json differs from baseline manifest")
    _need(manifest.get("resourceBaselinePath") == "ResourceInputs", path,
         "resourceBaselinePath must be the fixed ResourceInputs evidence directory")
    _need(digest(sidecars["policy.json"]) == manifest.get("policyHash"), sidecars["policy.json"],
         "policyHash does not match policy.json")
    _need(digest(sidecars["resource-script-index.json"]) == manifest["resourceIndexHash"], path,
         "resourceIndexHash does not match resource-script-index.json")
    _need(isinstance(manifest.get("shadowCandidates"), list) and set(manifest["shadowCandidates"]) == CANDIDATES and
         len(manifest["shadowCandidates"]) == len(CANDIDATES), path, "shadowCandidates must contain exactly five M02 candidates")
    _need(isinstance(manifest.get("bootstrapAssemblies"), list) and manifest["bootstrapAssemblies"] == [BOOTSTRAP],
         path, "bootstrapAssemblies must contain the fixed Bootstrap exactly")
    _need(isinstance(manifest.get("assemblies"), list) and manifest["assemblies"], path, "assemblies are missing")
    descriptors = {}
    for index, descriptor in enumerate(manifest["assemblies"]):
        descriptor_path = f"{path}.assemblies[{index}]"
        _need(isinstance(descriptor, dict), descriptor_path, "assembly descriptor must be an object")
        name = _name(descriptor.get("name"), descriptor_path, "name")
        _need("/" not in name and "\\" not in name, descriptor_path, "assembly name must not contain path separators")
        _need(name not in descriptors, descriptor_path, f"duplicate assembly descriptor: {name}")
        descriptors[name] = descriptor
        file_path = _relative(root, descriptor.get("filePath"), descriptor_path, "filePath")
        _need(digest(file_path) == descriptor.get("sha256"), descriptor_path, "assembly SHA-256 differs from manifest")
        sidecar = _relative(root, f"assemblies/{name}.json", descriptor_path, "sidecar")
        _need(sidecar.is_file() and not sidecar.is_symlink(), descriptor_path, "assembly sidecar is missing")
        side = _json(sidecar)
        for field in ("name", "mvid", "sha256", "semanticHash"):
            _need(side.get(field) == descriptor.get(field), sidecar, f"sidecar {field} differs from manifest descriptor")
    _need(BOOTSTRAP in descriptors, path, "fixed Bootstrap descriptor is missing")
    _need({name for name, descriptor in descriptors.items() if descriptor.get("isShadowCapable") is True} == CANDIDATES,
         path, "manifest must mark exactly the five M02 candidates as shadow-capable")
    _need({name for name, descriptor in descriptors.items() if descriptor.get("isBootstrap") is True} == {BOOTSTRAP},
         path, "manifest must mark exactly the fixed Bootstrap as bootstrap")
    bootstrap = descriptors[BOOTSTRAP]
    _need(bootstrap.get("isBootstrap") is True and bootstrap.get("isShadowCapable") is False,
         path, "Bootstrap metadata is not fixed/non-shadow")
    _need(not (set(bootstrap.get("references") or ()) & CANDIDATES), path,
         "Bootstrap metadata references a shadow candidate")
    return descriptors


def _verify_player_snapshot(root: Path, manifest: dict, descriptors: dict, path: Path):
    snapshot = _relative_dir(root, manifest.get("playerInputSnapshot"), path, "playerInputSnapshot")
    receipt_path = snapshot / "assembly-snapshot.json"
    receipt = _json(receipt_path)
    _need(receipt.get("schemaVersion") == 1 and receipt.get("kind") == "PlayerBuildInputs", receipt_path,
         "not a PlayerBuildInputs receipt")
    _need(receipt.get("playerBuildSucceeded") is True and receipt.get("playerBuildFilterCaptured") is True and
          _string(receipt.get("buildGuid"), receipt_path, "buildGuid"),
         receipt_path, "successful Player build and non-empty buildGuid are required")
    _need(isinstance(receipt.get("playerBuildOptions"), int) and receipt["playerBuildOptions"] & 1,
         receipt_path, "Player build options must include Development")
    for field in ("unityVersion", "target", "architecture", "snapshotHash", "nativeLibrarySha256"):
        _string(receipt.get(field), receipt_path, field)
    for field in ("unityVersion", "target", "architecture"):
        _need(receipt[field] == manifest[field], receipt_path, f"{field} differs from baseline manifest")
    _verify_source_pins(receipt.get("sourcePins"), receipt_path, manifest.get("sourcePins"))
    native = _absolute_file(receipt.get("nativeLibraryPath"), receipt_path, "nativeLibraryPath")
    _need(digest(native) == receipt["nativeLibrarySha256"] == manifest["nativeLibrarySha256"], receipt_path,
         "native library SHA-256 does not match receipt and baseline manifest")
    _need(receipt["snapshotHash"] == manifest["playerInputSnapshotHash"], receipt_path,
         "snapshotHash differs from baseline manifest")
    linked, linked_names = _verify_linked_player(snapshot, receipt, descriptors, receipt_path)
    reflection = _reflection_snapshot(snapshot, receipt, receipt_path, require_linked=True)
    by_name, _ = _snapshot_files(receipt, snapshot, receipt_path)
    aot = {_canonical_assembly_name(entry["name"]) for entry in receipt.get("assemblies", [])}
    filtered = {_canonical_assembly_name(entry["name"]) for entry in receipt.get("filteredAssemblies", [])}
    candidate_names = {_canonical_assembly_name(name) for name in CANDIDATES}
    bootstrap_name = _canonical_assembly_name(BOOTSTRAP)
    _need(candidate_names <= aot and len(candidate_names & aot) == 5, receipt_path,
         "captured Player inputs do not contain exactly the five candidates")
    _need(not (candidate_names & filtered) and bootstrap_name not in filtered, receipt_path,
         "shadow candidate or Bootstrap was filtered out of AOT")
    normal = receipt.get("normalHotUpdateAssemblies") or []
    _need(isinstance(normal, list), receipt_path, "normalHotUpdateAssemblies must be an array")
    normal_names = []
    for index, value in enumerate(normal):
        normal_path = f"{receipt_path}.normalHotUpdateAssemblies[{index}]"
        raw_name = _name(value, normal_path, "name")
        canonical_name = _canonical_assembly_name(raw_name)
        _need(canonical_name and canonical_name not in normal_names, normal_path, "duplicate normal hot-update assembly identity")
        normal_names.append(canonical_name)
    normal = set(normal_names)
    _need(not (normal & candidate_names), receipt_path,
         "normal hot-update role overlaps a shadow candidate")
    roles = receipt.get("filteredAssemblyCapabilities") or []
    role_map = {}
    descriptor_by_name = {}
    for descriptor_name, descriptor in descriptors.items():
        canonical_descriptor_name = _canonical_assembly_name(descriptor_name)
        _need(canonical_descriptor_name not in descriptor_by_name, path,
             f"baseline descriptors contain duplicate canonical assembly identity: {descriptor_name}")
        descriptor_by_name[canonical_descriptor_name] = descriptor
    for index, role in enumerate(roles):
        role_path = f"{receipt_path}.filteredAssemblyCapabilities[{index}]"
        _need(isinstance(role, dict), role_path, "filtered capability must be an object")
        raw_name = _name(role.get("name"), role_path, "name")
        name = _canonical_assembly_name(raw_name)
        _need(name, role_path, "filtered capability name must contain an assembly identity")
        _need(name in filtered and name not in role_map, role_path, "filtered capability does not match a filtered DLL")
        _need(role.get("classification") in (0, 1, 2, 3, 4), role_path,
             "filtered capability must preserve an original source role (0 through 4)")
        _need(role.get("isShadowCapable") is not True and role.get("isBootstrap") is not True, role_path,
             "filtered DLL cannot be a candidate or Bootstrap")
        _need((role["classification"] == 4) == (name in normal), role_path,
             "filtered capability normal-hot-update membership disagrees with its original classification")
        descriptor = descriptor_by_name.get(name)
        _need(descriptor is not None, role_path, "filtered capability is absent from baseline descriptors")
        expected_classification = 4 if role["classification"] == 4 else 5
        _need(descriptor.get("classification") == expected_classification, role_path,
             "filtered projected descriptor classification differs from its original role")
        for field in ("isPrecompiled", "isShadowCapable", "isBootstrap", "capabilityDeclared"):
            _need(descriptor.get(field, False) == role.get(field, False), role_path,
                  f"filtered role {field} differs from baseline descriptor")
        role_map[name] = role
    _need(set(role_map) == filtered, receipt_path, "filtered DLL role inventory is incomplete")
    _need(set(descriptor_by_name) == aot | filtered, path,
         "baseline manifest descriptors must cover the AOT and filtered Player assemblies exactly")
    for name in aot:
        descriptor = descriptor_by_name.get(name)
        if descriptor is not None and name in candidate_names:
            _need(descriptor.get("isShadowCapable") is True and descriptor.get("classification", 0) == 0,
                 path, f"candidate descriptor has an invalid filtered role: {name}")
    for name, role in role_map.items():
        descriptor = descriptor_by_name.get(name)
        _need(descriptor is not None and descriptor.get("classification") == (4 if role.get("classification") == 4 else 5) and
              descriptor.get("isShadowCapable") is not True and descriptor.get("isBootstrap") is not True,
              path, f"filtered descriptor role differs from receipt: {name}")
    _need(_snapshot_hash(receipt, snapshot, receipt_path) == receipt.get("snapshotHash"), receipt_path,
         "snapshotHash does not match the complete receipt proof")
    for candidate in CANDIDATES:
        candidate_key = _canonical_assembly_name(candidate)
        entry = next((value for key, value in by_name.items() if _canonical_assembly_name(key) == candidate_key), None)
        _need(entry is not None, path, f"candidate input is missing from captured Player receipt: {candidate}")
        descriptor = descriptors.get(candidate)
        _need(descriptor is not None, path, f"candidate descriptor is missing: {candidate}")
        copied = _relative(root, descriptor.get("filePath"), path, f"assemblies[{candidate}].filePath")
        _need(digest(copied) == entry["sha256"] == descriptor.get("sha256"), path,
             f"candidate {candidate} bytes do not match captured Player input")
    by_name_canonical = {_canonical_assembly_name(name): entry for name, entry in by_name.items()}
    for name, descriptor in descriptors.items():
        canonical_name = _canonical_assembly_name(name)
        if canonical_name not in by_name_canonical:
            continue
        expected = _relative(root, descriptor.get("filePath"), path, f"assemblies[{name}].filePath")
        _need(digest(expected) == by_name_canonical[canonical_name].get("sha256") == descriptor.get("sha256"), path,
             f"manifest descriptor bytes differ from captured receipt: {name}")
    return receipt, snapshot, by_name, reflection


def _verify_bundles(m01_root: Path, manifest: dict, path: Path):
    m01_manifest_path = m01_root / "baseline-manifest.json"
    if not m01_manifest_path.is_file():
        nested_manifest = m01_root / "Original" / "baseline-manifest.json"
        if nested_manifest.is_file():
            m01_manifest_path = nested_manifest
    m01 = _json(m01_manifest_path)
    _need(isinstance(m01.get("bundles"), list), m01_manifest_path, "M01 bundles are missing")
    old = {}
    for index, bundle in enumerate(m01["bundles"]):
        bundle_path = f"{m01_manifest_path}.bundles[{index}]"
        _need(isinstance(bundle, dict), bundle_path, "bundle must be an object")
        name = _name(bundle.get("name"), bundle_path, "name")
        _need(name not in old, bundle_path, f"duplicate M01 bundle: {name}")
        physical = _relative(m01_root, bundle.get("path"), bundle_path, "path")
        _need(digest(physical) == bundle.get("sha256"), bundle_path, "frozen M01 bundle SHA-256 differs from bytes")
        old[name] = bundle["sha256"]
    _need(set(old) == M01_BUNDLES, m01_manifest_path, "M01 must contain exactly the original three bundles")
    bundles = manifest.get("bundles")
    _need(isinstance(bundles, list) and len(bundles) == 3, path, "M02 must contain exactly three baseline bundles")
    current = {}
    for index, bundle in enumerate(bundles):
        bundle_path = f"{path}.bundles[{index}]"
        _need(isinstance(bundle, dict), bundle_path, "bundle must be an object")
        name = _name(bundle.get("name"), bundle_path, "name")
        _need(name not in current, bundle_path, f"duplicate M02 bundle: {name}")
        current[name] = _string(bundle.get("sha256"), bundle_path, "sha256")
    _need(current == old, path, "M02 baseline bundle hashes differ from frozen M01 bundle files/manifest")


def _verify_builtin_source(resource_root: Path, source: dict, path: Path, unity_version: str):
    snapshot = _relative(resource_root, source.get("snapshotPath"), path, "snapshotPath")
    proof = _json(snapshot)
    _need(proof.get("schemaVersion") == 1 and proof.get("unityVersion") == unity_version and
          proof.get("virtualPath") == source.get("path") and proof.get("guid") == source.get("guid") and
          isinstance(proof.get("guid"), str) and proof["guid"], snapshot, "builtin resource proof identity is invalid")
    _hash64(proof.get("backingSha256"), snapshot, "backingSha256")
    backing = _relative(resource_root, proof.get("backingPath"), snapshot, "backingPath")
    _need(digest(backing) == proof["backingSha256"], backing, "builtin backing bytes SHA differs from proof")
    modules = proof.get("modules")
    _need(isinstance(modules, list) and modules, snapshot, "builtin module proof is missing")
    module_names = set(); module_paths = set()
    for index, module in enumerate(modules):
        module_path = f"{snapshot}.modules[{index}]"
        _need(isinstance(module, dict), module_path, "builtin module proof must be an object")
        name = _string(module.get("assemblyName"), module_path, "assemblyName")
        _need(name not in module_names and (name == "UnityEngine" or name.startswith("UnityEngine.") or name == "UnityEditor" or name.startswith("UnityEditor.")),
             module_path, "builtin module must be a unique Unity installation module")
        module_names.add(name)
        _hash64(module.get("sha256"), module_path, "sha256")
        _need(module.get("path") == "BuiltinProof/Modules/" + module["sha256"] + "/" + name + ".dll", module_path,
             "builtin module path is not bound to its SHA and assembly name")
        physical = _relative(resource_root, module["path"], module_path, "path")
        _need(digest(physical) == module["sha256"], physical, "builtin module bytes SHA differs from proof")
        module_paths.add(physical.resolve())
    _need([item.get("assemblyName") for item in modules] == sorted(item.get("assemblyName") for item in modules), snapshot,
         "builtin modules are not in canonical ordinal order")
    objects = proof.get("objects")
    _need(isinstance(objects, list) and objects, snapshot, "builtin object proof is missing")
    local_ids = set()
    for index, obj in enumerate(objects):
        object_path = f"{snapshot}.objects[{index}]"
        _need(isinstance(obj, dict), object_path, "builtin object proof must be an object")
        _need(obj.get("persistent") is True and obj.get("guid") == proof["guid"] and
              isinstance(obj.get("localId"), int) and not isinstance(obj.get("localId"), bool) and obj["localId"] != 0 and
              obj["localId"] not in local_ids, object_path, "builtin object identity is missing or duplicated")
        local_ids.add(obj["localId"])
        assembly_name = _string(obj.get("assemblyName"), object_path, "assemblyName")
        type_name = _string(obj.get("typeName"), object_path, "typeName")
        _need(assembly_name in module_names, object_path, "builtin object type has no captured engine module")
        _hash64(obj.get("serializedSha256"), object_path, "serializedSha256")
    _need([item.get("localId") for item in objects] == sorted(item.get("localId") for item in objects), snapshot,
         "builtin objects are not in canonical local-id order")


def _verify_resource_baseline(root: Path, manifest: dict, path: Path, m01_root: Path):
    resource_root = _relative_dir(root, manifest.get("resourceBaselinePath"), path, "resourceBaselinePath")
    receipt_path = resource_root / "resource-build-receipt.json"
    _need(receipt_path.is_file() and not receipt_path.is_symlink(), receipt_path, "resource baseline receipt is missing")
    _need(digest(receipt_path) == manifest.get("resourceBuildReceiptHash"), receipt_path,
         "resourceBuildReceiptHash differs from resource-build-receipt.json")
    receipt_manifest_hash = resource_root / "manifest.sha256"
    _need(receipt_manifest_hash.is_file() and receipt_manifest_hash.read_text().strip() == digest(receipt_path), receipt_manifest_hash,
         "resource receipt manifest SHA sidecar is missing or stale")
    receipt = _json(receipt_path)
    _verify_source_pins(receipt.get("sourcePins", manifest.get("sourcePins")), receipt_path, manifest.get("sourcePins"))
    _need(receipt.get("schemaVersion") == 1 and receipt.get("provenance") in
          ("CompilePlayerScriptsAndBuildAssetBundles", "M01AuditedFrozenSourceReconstruction"), receipt_path,
         "resource baseline receipt schema/provenance is not recognized")
    for field in ("unityVersion", "target", "architecture", "compilerSnapshotHash", "resourceAbiHash", "resourceAbiFileSha256",
                  "resourceIndexHash", "sourceSetHash", "bundleDirectory", "compilerSnapshotPath", "metadataAssemblyDirectory"):
        _string(receipt.get(field), receipt_path, field)
    for field in ("unityVersion", "target", "architecture"):
        _need(receipt[field] == manifest[field], receipt_path, f"resource receipt {field} differs from baseline")
    candidate_names = receipt.get("candidateAssemblies")
    _need(isinstance(candidate_names, list) and set(candidate_names) == CANDIDATES and len(candidate_names) == 5,
         receipt_path, "resource receipt candidateAssemblies must contain exactly five candidates")
    abi_path = _relative(resource_root, receipt.get("resourceAbiPath"), receipt_path, "resourceAbiPath")
    index_path = _relative(resource_root, receipt.get("resourceIndexPath"), receipt_path, "resourceIndexPath")
    _need(digest(abi_path) == receipt["resourceAbiFileSha256"], receipt_path, "resource ABI file SHA differs from receipt")
    _need(digest(index_path) == receipt["resourceIndexHash"], receipt_path, "resource index SHA differs from receipt")
    abi = _json(abi_path); index = _json(index_path)
    _need(abi.get("schemaVersion") == 2 and _resource_abi_hash(abi) == receipt["resourceAbiHash"], abi_path,
         "resource ABI schema/hash is invalid")
    _need(index.get("schemaVersion") == 2 and index.get("hasUnknown") is False and index.get("unknowns") == [], index_path,
         "resource index is unproven or contains unknowns")
    _need(receipt["resourceAbiHash"] == manifest["resourceAbiHash"], receipt_path,
         "resource receipt ABI differs from baseline manifest")
    bundles = receipt.get("bundles")
    _need(isinstance(bundles, list) and len(bundles) == 3, receipt_path,
         "resource receipt must contain exactly three bundles")
    for index_number, bundle in enumerate(bundles):
        _need(isinstance(bundle, dict), f"{receipt_path}.bundles[{index_number}]", "bundle must be an object")
        _name(bundle.get("name"), f"{receipt_path}.bundles[{index_number}]", "name")
    _need({bundle["name"] for bundle in bundles} == M01_BUNDLES, receipt_path,
         "resource receipt must contain the original three bundles")
    build_map = receipt.get("buildMap")
    _need(isinstance(build_map, dict) and build_map.get("schemaVersion") == 1 and isinstance(build_map.get("bundles"), list),
         receipt_path, "resource build map is missing or invalid")
    map_by_name = {item.get("name"): item.get("assets") for item in build_map["bundles"] if isinstance(item, dict)}
    receipt_by_name = {item.get("name"): item.get("assets") for item in bundles}
    _need(map_by_name == receipt_by_name, receipt_path, "resource build map differs from captured bundle definitions")
    for index_number, bundle in enumerate(bundles):
        bundle_path = f"{receipt_path}.bundles[{index_number}]"
        physical = _relative(resource_root, receipt["bundleDirectory"] + "/" + _name(bundle.get("name"), bundle_path, "name"), bundle_path, "bundle")
        _need(digest(physical) == bundle.get("sha256"), bundle_path, "resource bundle SHA differs from bytes")
    sources = receipt.get("sources")
    _need(isinstance(sources, list) and sources, receipt_path, "resource source inventory is missing")
    _need(_resource_source_set_hash(sources) == receipt.get("sourceSetHash"), receipt_path,
         "resource source set hash does not match captured sources")
    for index_number, source in enumerate(sources):
        source_path = f"{receipt_path}.sources[{index_number}]"
        _need(isinstance(source, dict), source_path, "resource source must be an object")
        _relative(resource_root, source.get("snapshotPath"), source_path, "snapshotPath")
        _need(digest(_relative(resource_root, source["snapshotPath"], source_path, "snapshotPath")) == source.get("sha256"),
             source_path, "resource source SHA differs from snapshot bytes")
        if source.get("metaSnapshotPath"):
            meta = _relative(resource_root, source["metaSnapshotPath"], source_path, "metaSnapshotPath")
            _need(digest(meta) == source.get("metaSha256"), source_path, "resource meta SHA differs from snapshot bytes")
        if source.get("builtin") is True:
            _verify_builtin_source(resource_root, source, source_path, manifest["unityVersion"])
    compiler_root = _relative_dir(resource_root, receipt["compilerSnapshotPath"], receipt_path, "compilerSnapshotPath")
    compiler_receipt = _json(compiler_root / "assembly-snapshot.json")
    _verify_source_pins(compiler_receipt.get("sourcePins"), compiler_root / "assembly-snapshot.json", manifest.get("sourcePins"))
    _need(compiler_receipt.get("snapshotHash") == receipt["compilerSnapshotHash"], receipt_path,
         "resource compiler snapshot hash differs from receipt")
    _need(_snapshot_hash(compiler_receipt, compiler_root, compiler_root / "assembly-snapshot.json") == compiler_receipt.get("snapshotHash"),
         compiler_root / "assembly-snapshot.json", "resource compiler snapshot proof hash is invalid")
    compiler_reflection = _reflection_snapshot(
        compiler_root, compiler_receipt, compiler_root / "assembly-snapshot.json",
        require_linked=compiler_receipt.get("kind") == "PlayerBuildInputs")
    _reflection_manifest(manifest, compiler_reflection, receipt_path)
    if receipt["provenance"] == "CompilePlayerScriptsAndBuildAssetBundles":
        defines = compiler_receipt.get("extraScriptingDefines")
        _need(receipt.get("compilerSnapshotIsPlayer") is False and compiler_receipt.get("kind") == "CompilePlayerScripts" and
              _reflection_user_defines(defines, compiler_root / "assembly-snapshot.json") == [], receipt_path,
             "fresh resource build must use an empty-define compile snapshot")
    else:
        _need(receipt.get("compilerSnapshotIsPlayer") is True, receipt_path, "M01 resource import must retain Player compiler proof")
    metadata = receipt.get("metadataAssemblies")
    _need(isinstance(metadata, list) and metadata, receipt_path, "resource metadata assembly proof is missing")
    _need(all(isinstance(item, dict) for item in metadata), receipt_path,
         "resource metadata proof contains a malformed entry")
    metadata_names = [_canonical_assembly_name(Path(item.get("path", "")).name) for item in metadata]
    _need(len(metadata_names) == len(set(metadata_names)) and set(metadata_names) ==
         {_canonical_assembly_name(name) for name in candidate_names}, receipt_path,
         "resource metadata proof must contain exactly the five candidate roots")
    _relative_dir(resource_root, receipt["metadataAssemblyDirectory"], receipt_path, "metadataAssemblyDirectory")
    compiler_aot = {_canonical_assembly_name(item.get("name")): item for item in compiler_receipt.get("assemblies", [])
                    if isinstance(item, dict)}
    if receipt["provenance"] == "CompilePlayerScriptsAndBuildAssetBundles":
        _need(receipt["metadataAssemblyDirectory"] == "ResourceAssemblies", receipt_path,
             "fresh resource metadata must use ResourceAssemblies")
        for index_number, item in enumerate(metadata):
            item_path = f"{receipt_path}.metadataAssemblies[{index_number}]"
            name = _canonical_assembly_name(Path(item.get("path", "")).name)
            compiled = compiler_aot.get(name)
            _need(compiled is not None and item.get("path") == "ResourceAssemblies/" + compiled.get("name") + ".dll" and
                  item.get("sha256") == compiled.get("sha256"), item_path,
                 "fresh resource metadata bytes differ from the same empty-define compiler input")
    for index_number, item in enumerate(metadata):
        item_path = f"{receipt_path}.metadataAssemblies[{index_number}]"
        physical = _relative(resource_root, item.get("path"), item_path, "path")
        _need(digest(physical) == item.get("sha256"), item_path, "metadata proof SHA differs from bytes")
    metadata_root = resource_root / receipt["metadataAssemblyDirectory"]
    expected_metadata = {(_relative(resource_root, item["path"], receipt_path, "metadataAssemblies.path")).resolve() for item in metadata}
    actual_metadata = {item.resolve() for item in metadata_root.rglob("*.dll")}
    _need(expected_metadata == actual_metadata, metadata_root,
         "resource metadata DLL set differs from the exact candidate proof")
    if receipt.get("provenance") == "M01AuditedFrozenSourceReconstruction":
        _need(receipt.get("originalManifestPath") and receipt.get("originalSourceAuditPath") and receipt.get("reconstructionProof"),
             receipt_path, "M01 resource import proof is incomplete")
        original_path = _relative(resource_root, receipt["originalManifestPath"], receipt_path, "originalManifestPath")
        audit_path = _relative(resource_root, receipt["originalSourceAuditPath"], receipt_path, "originalSourceAuditPath")
        _need(digest(original_path) == receipt.get("originalManifestSha256"), original_path, "original M01 manifest SHA mismatch")
        _need(digest(audit_path) == receipt.get("originalSourceAuditSha256"), audit_path, "original M01 audit SHA mismatch")
        original = _json(original_path); audit = _json(audit_path)
        original_assemblies = original.get("assemblies")
        _need(original.get("baselineBuildId") == "M01-Baseline-v1" and audit.get("verified") is True and
             isinstance(original_assemblies, list) and
             {item.get("name") for item in original_assemblies if isinstance(item, dict)} == M01_ASSEMBLIES and
             len(original_assemblies) == len(M01_ASSEMBLIES), receipt_path,
             "M01 resource import proof identity is invalid")
        _need({item.get("name"): item.get("sha256") for item in original.get("bundles", [])} ==
             {item.get("name"): item.get("sha256") for item in bundles}, receipt_path, "M01 imported bundle proof differs")
        reconstruction = receipt.get("reconstructionProof")
        _need(isinstance(reconstruction, list) and reconstruction, receipt_path,
             "M01 reconstruction proof is missing")
        for index_number, proof_file in enumerate(reconstruction):
            proof_path = f"{receipt_path}.reconstructionProof[{index_number}]"
            _need(isinstance(proof_file, dict), proof_path, "reconstruction proof entry must be an object")
            physical = _relative(resource_root, proof_file.get("path"), proof_path, "path")
            _need(digest(physical) == proof_file.get("sha256"), proof_path,
                 "reconstruction proof SHA-256 differs from captured bytes")
        for index_number, assembly in enumerate(original_assemblies):
            assembly_path = f"{original_path}.assemblies[{index_number}]"
            _need(isinstance(assembly, dict), assembly_path, "historical assembly must be an object")
            matches = [item for item in metadata
                       if isinstance(item, dict) and Path(item.get("path", "")).name == assembly.get("name") + ".dll"
                       and item.get("sha256") == assembly.get("sha256")]
            _need(len(matches) == 1, assembly_path,
                 "historical assembly must match exactly one metadata assembly proof")
        compared_files = audit.get("comparedFiles")
        _need(isinstance(compared_files, list) and compared_files, audit_path,
             "historical source audit has no compared files")
        for index_number, item in enumerate(compared_files):
            item_path = f"{audit_path}.comparedFiles[{index_number}]"
            _need(isinstance(item, dict) and item.get("matchesFrozen") is True, item_path,
                 "historical source audit entry is not marked as matching frozen bytes")
            matches = []
            for source in sources:
                if not isinstance(source, dict):
                    continue
                if source.get("path") == item.get("path"):
                    matches.append(source.get("sha256") == item.get("sha256"))
                elif source.get("path", "") + ".meta" == item.get("path"):
                    matches.append(source.get("metaSha256") == item.get("sha256"))
            _need(len(matches) == 1 and matches[0], item_path,
                 "historical source audit entry differs from captured resource source proof")
        external_manifest = m01_root / "baseline-manifest.json"
        if not external_manifest.is_file():
            external_manifest = m01_root / "Original" / "baseline-manifest.json"
        _need(external_manifest.is_file() and not external_manifest.is_symlink(), external_manifest,
             "provided frozen M01 root is missing its baseline manifest")
        _need(digest(external_manifest) == receipt.get("originalManifestSha256"), external_manifest,
             "provided frozen M01 manifest SHA differs from the accepted historical proof")
        frozen = _json(external_manifest)
        _need(frozen.get("schemaVersion") == 1 and frozen.get("baselineBuildId") == "M01-Baseline-v1" and
              frozen.get("unityVersion") == receipt["unityVersion"] and frozen.get("target") == receipt["target"] and
              frozen.get("architecture") == receipt["architecture"], external_manifest,
             "provided frozen M01 manifest identity differs from historical proof")
        _need({item.get("name"): item.get("sha256") for item in frozen.get("bundles", [])} ==
             {item.get("name"): item.get("sha256") for item in original.get("bundles", [])}, external_manifest,
             "provided frozen M01 manifest differs from embedded historical bundle proof")
        _need({item.get("name"): item.get("sha256") for item in frozen.get("assemblies", [])} ==
             {item.get("name"): item.get("sha256") for item in original.get("assemblies", [])}, external_manifest,
             "provided frozen M01 manifest differs from embedded historical assembly proof")
        frozen_assemblies = frozen.get("assemblies")
        _need(isinstance(frozen_assemblies, list) and frozen_assemblies, external_manifest,
             "provided frozen M01 manifest has no assembly proof")
        for index_number, assembly in enumerate(frozen_assemblies):
            assembly_path = f"{external_manifest}.assemblies[{index_number}]"
            _need(isinstance(assembly, dict), assembly_path, "historical assembly proof must be an object")
            physical = _relative(m01_root, assembly.get("path"), assembly_path, "path")
            _need(digest(physical) == assembly.get("sha256"), assembly_path,
                 "provided frozen M01 assembly SHA-256 differs from bytes")
        external_audit = m01_root / "source-audit.json"
        if not external_audit.is_file():
            external_audit = m01_root / "Original" / "source-audit.json"
        if external_audit.is_file() and not external_audit.is_symlink():
            _need(digest(external_audit) == receipt.get("originalSourceAuditSha256"), external_audit,
                 "provided frozen M01 source audit SHA differs from the accepted historical proof")
            _need(_normal(_json(external_audit)) == _normal(audit), external_audit,
                 "provided frozen M01 source audit differs from embedded historical audit")
        source_snapshot_path = frozen.get("sourceSnapshotPath")
        _need(isinstance(source_snapshot_path, str) and source_snapshot_path,
             external_manifest, "provided frozen M01 source snapshot path is missing")
        source_snapshot_root = _relative_dir(m01_root, source_snapshot_path, external_manifest, "sourceSnapshotPath")
        compared_files = audit.get("comparedFiles")
        _need(isinstance(compared_files, list) and compared_files, external_manifest,
             "historical source audit has no compared files")
        for index_number, item in enumerate(compared_files):
            item_path = f"{external_manifest}.sourceAudit.comparedFiles[{index_number}]"
            _need(isinstance(item, dict) and item.get("matchesFrozen") is True, item_path,
                 "historical source audit entry is not marked as matching frozen bytes")
            source_file = _relative(source_snapshot_root, item.get("path"), item_path, "path")
            _need(digest(source_file) == item.get("sha256"), item_path,
                 "provided frozen M01 source bytes differ from accepted audit")
    return receipt


def _edges(items, path):
    _need(isinstance(items, list), path, "dependencyGraph must be an array")
    result = []
    seen_pairs = set()
    for index, edge in enumerate(items):
        edge_path = f"{path}[{index}]"
        _need(isinstance(edge, dict), edge_path, "dependency edge must be an object")
        consumer = _name(edge.get("consumer"), edge_path, "consumer")
        provider = _name(edge.get("provider"), edge_path, "provider")
        _need(consumer != provider, edge_path, "self-dependency is forbidden")
        _need(_name(edge.get("kind"), edge_path, "kind"), edge_path, "edge kind is required")
        _need((consumer, provider) not in seen_pairs, edge_path, f"duplicate dependency edge: {consumer} -> {provider}")
        seen_pairs.add((consumer, provider))
        result.append((consumer, provider, edge.get("kind"), edge.get("evidence")))
    return result


def _closure(edges, roots, known, path):
    reverse = {name: set() for name in known}
    for consumer, provider, _, _ in edges:
        _need(consumer in known and provider in known, path, f"dependency edge names unknown assembly: {consumer} -> {provider}")
        reverse[provider].add(consumer)
    seen = set(roots)
    queue = list(sorted(roots))
    while queue:
        provider = queue.pop(0)
        for consumer in sorted(reverse[provider]):
            if consumer not in seen:
                seen.add(consumer)
                queue.append(consumer)
    return seen


def _verify_topological(order, closure, edges, path):
    _need(isinstance(order, list), path, "loadOrder must be an array")
    _need(len(order) == len(set(order)) and set(order) == closure, path, "loadOrder must contain closure exactly once")
    positions = {name: index for index, name in enumerate(order)}
    for consumer, provider, _, _ in edges:
        if consumer in closure and provider in closure:
            _need(positions[provider] < positions[consumer], path,
                 f"loadOrder is not dependency-first: {provider} must precede {consumer}")


def _pins(manifest, receipt, path):
    _need(manifest.get("sourcePins") is not None and receipt.get("sourcePins") is not None, path,
         "source pins are required")
    _verify_source_pins(manifest["sourcePins"], path)
    _verify_source_pins(receipt["sourcePins"], path, manifest["sourcePins"])
    _need(_normal(manifest["sourcePins"]) == _normal(receipt["sourcePins"]), path,
         "compile/Player source pins differ from baseline")
    _need(_runtime_abi_hash(receipt["sourcePins"], path) == manifest.get("runtimeAbiHash"), path,
         "runtimeAbiHash does not match source pins")


def _verify_compile_snapshot(run: Path, patch_root: Path, patch: dict, baseline: dict, patch_path: Path,
                             patch_id: str):
    source_root = run / f"{patch_id}-compile" / "Snapshot"
    _need(source_root.is_dir() and not source_root.is_symlink(), patch_path,
         f"compile snapshot source is missing: {source_root}")
    source_receipt_path = source_root / "assembly-snapshot.json"
    sidecar_path = patch_root / "compile-snapshot-receipt.json"
    _need(sidecar_path.is_file() and not sidecar_path.is_symlink(), patch_path,
         "compile-snapshot-receipt.json sidecar is missing")
    source_receipt = _json(source_receipt_path)
    sidecar = _json(sidecar_path)
    _need(_normal(source_receipt) == _normal(sidecar), sidecar_path,
         "compile snapshot sidecar differs from the single original receipt")
    _need(source_receipt.get("schemaVersion") == 1 and source_receipt.get("kind") == "CompilePlayerScripts",
         source_receipt_path, "not a CompilePlayerScripts receipt")
    _need(_linked_claim_absent(source_receipt) and
          not (source_root / "LinkedPlayer").exists() and not (source_root / "LinkedPlayer").is_symlink(),
          source_receipt_path, "compiler snapshot cannot claim linked Player evidence")
    _need(patch.get("compileSnapshotHash") == source_receipt.get("snapshotHash"), patch_path,
         "compileSnapshotHash differs from receipt snapshotHash")
    for field in ("unityVersion", "target", "architecture"):
        _need(source_receipt.get(field) == baseline.get(field) and
             (field != "target" or source_receipt.get(field) == TARGET),
             source_receipt_path, f"compile snapshot {field} differs from baseline")
    _pins(baseline, source_receipt, source_receipt_path)
    reflection = _reflection_snapshot(source_root, source_receipt, source_receipt_path, require_linked=False)
    by_name, _ = _snapshot_files(source_receipt, source_root, source_receipt_path)
    _need(_snapshot_hash(source_receipt, source_root, source_receipt_path) == source_receipt.get("snapshotHash"),
         source_receipt_path, "snapshotHash does not match the complete compile receipt")
    return {entry["name"]: entry for entry in source_receipt.get("assemblies", [])}, reflection


def _verify_patch(patch_path: Path, run: Path, baseline: dict, descriptors: dict, baseline_edges, expected_root,
                  expected_closure, expected_bundles=None):
    patch_root = patch_path.parent
    patch = _json(patch_path)
    manifest_sidecar = patch_root / "manifest.sha256"
    _need(manifest_sidecar.is_file() and not manifest_sidecar.is_symlink(), manifest_sidecar,
         "manifest SHA sidecar is missing")
    _need(manifest_sidecar.read_text().strip() == digest(patch_path), manifest_sidecar,
         "manifest SHA sidecar differs from patch-manifest.json")
    _need(patch.get("schemaVersion") == 1 and patch.get("semanticHashSchema") == 1, patch_path,
         "patch manifest schemaVersion and semanticHashSchema must be 1")
    patch_id = _name(patch.get("patchId"), patch_path, "patchId")
    _need(patch_id in {"P01", "P02", "P03", "P05"}, patch_path, "unexpected patchId")
    for field in ("baselineBuildId", "baselineManifestSha256", "unityVersion", "target", "architecture",
                  "runtimeAbiHash", "compileSnapshotHash", "bootstrapAbiHash", "baselineResourceAbiHash",
                  "resourceAbiHash", "resourceChangeLevel"):
        _string(patch.get(field), patch_path, field)
        if field == "baselineBuildId":
            _need(patch[field] == baseline.get(field), patch_path, "baselineBuildId differs from baseline")
        elif field in baseline and field not in ("resourceAbiHash",):
            _need(patch[field] == baseline[field], patch_path, f"{field} differs from baseline")
    _need(patch["baselineManifestSha256"] == baseline.get("_actualSha256"), patch_path,
         "baselineManifestSha256 does not identify the actual baseline manifest")
    _need(patch.get("unsigned") is True and patch.get("signatureAlgorithm") == "None", patch_path,
         "patch must explicitly declare unsigned/None signature")
    _need(patch.get("sourcePins") is not None and _normal(patch["sourcePins"]) == _normal(baseline.get("sourcePins")),
         patch_path, "patch source pins differ from baseline")
    resource_sidecar = patch_root / "resource-abi.json"
    _need(resource_sidecar.is_file() and not resource_sidecar.is_symlink(), resource_sidecar,
         "patch resource-abi.json sidecar is missing")
    patch_abi = _json(resource_sidecar)
    _need(patch_abi.get("schemaVersion") == 2 and _resource_abi_hash(patch_abi) == patch.get("resourceAbiHash"), resource_sidecar,
         "resourceAbiHash does not match patch resource-abi.json")
    _need(patch.get("changedRoots") == [expected_root], patch_path, "changedRoots differs from expected M02 case")
    closure_names = _names(patch.get("closure"), patch_path, "closure")
    _need(set(closure_names) == expected_closure and len(closure_names) == len(expected_closure), patch_path,
         "closure does not equal independently computed reverse dependency closure")
    current_edges = _edges(patch.get("dependencyGraph"), f"{patch_path}.dependencyGraph")
    all_edges = baseline_edges + current_edges
    _need(_closure(all_edges, {expected_root}, set(descriptors), patch_path) == expected_closure, patch_path,
         "reverse closure from current+baseline dependency edges differs from patch closure")
    _verify_topological(patch.get("loadOrder"), expected_closure, all_edges, patch_path)
    receipt_entries, reflection = _verify_compile_snapshot(run, patch_root, patch, baseline, patch_path, patch_id)
    _reflection_manifest(patch, reflection, patch_path)
    baseline_has_reflection = baseline.get("reflectionBindingConfigurationHash") not in (None, "")
    _need((reflection is not None) == baseline_has_reflection, patch_path,
         "patch reflection binding control/evidence presence differs from the baseline contract")
    if reflection is not None:
        baseline_canonical = baseline.get("reflectionBindingConfigurationHash")
        _need(reflection["canonicalHash"] == baseline_canonical, patch_path,
             "patch reflection binding configuration differs from the baseline contract")
    _reflection_copy(patch_root, reflection, patch_path)
    closure = patch.get("closure")
    for index, entry in enumerate(closure):
        entry_path = f"{patch_path}.closure[{index}]"
        _need(isinstance(entry, dict), entry_path, "closure entry must be an object")
        name = _name(entry.get("name"), entry_path, "name")
        _need(name in expected_closure, entry_path, f"unexpected closure assembly: {name}")
        input_entry = receipt_entries.get(name)
        _need(input_entry is not None, entry_path, f"assembly is absent from the single compile snapshot receipt: {name}")
        dll = _relative(patch_root, entry.get("dll"), entry_path, "dll")
        _need(digest(dll) == entry.get("sha256") == input_entry.get("sha256"), entry_path,
             "closure DLL SHA-256 differs from manifest or compile snapshot")
        if entry.get("pdb"):
            _need(input_entry.get("pdbPath"), entry_path, "closure PDB is not present in compile snapshot receipt")
            pdb = _relative(patch_root, entry["pdb"], entry_path, "pdb")
            source_pdb = _relative(run / f"{patch_id}-compile" / "Snapshot", input_entry["pdbPath"], entry_path, "receipt.pdbPath")
            _need(digest(pdb) == entry.get("pdbSha256") == input_entry.get("pdbSha256") == digest(source_pdb), entry_path,
                 "closure PDB SHA-256 differs from manifest or compile snapshot")
        else:
            _need(not input_entry.get("pdbPath"), entry_path, "closure must include the compile snapshot PDB")
    if patch_id in ("P01", "P02", "P03"):
        _need(patch.get("dllOnly") is True and patch["resourceAbiHash"] == patch["baselineResourceAbiHash"], patch_path,
             "P01/P02/P03 must be DLL-only with unchanged resource ABI")
        _need(patch.get("resourceBundlesRequired") == [], patch_path, "code-only patches must require no bundles")
    else:
        _need(patch.get("dllOnly") is False and patch.get("resourceChangeLevel") == "ResourceRebuildRequired", patch_path,
             "P05 must require a resource rebuild and must not be DLL-only")
        _need(set(patch.get("resourceBundlesRequired") or ()) == {"business-scene.bundle", "versioned-prefab.bundle"} and
             len(patch.get("resourceBundlesRequired") or ()) == 2 and "versioned-data.bundle" not in patch["resourceBundlesRequired"],
             patch_path, "P05 must require exactly business-scene.bundle and versioned-prefab.bundle")
    return patch


def _verify_nunit(path: Path):
    _need(path.is_file() and not path.is_symlink() and path.stat().st_size > 0, path, "NUnit XML is missing or empty")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise VerificationError(f"{path}: invalid NUnit XML: {error}") from error
    result = str(root.attrib.get("result", "")).lower()
    _need(result == "passed", path, "NUnit test-run result must be Passed")
    _need(str(root.attrib.get("failed", "0")) == "0", path, "NUnit test-run failed count must be zero")
    cases = list(root.iter())
    test_cases = [node for node in cases if node.tag.rsplit("}", 1)[-1].lower() == "test-case"]
    _need(test_cases, path, "NUnit XML contains no test cases")
    for node in test_cases:
        _need(str(node.attrib.get("result", "")).lower() == "passed", path,
             f"NUnit test case is not Passed: {node.attrib.get('fullname', node.attrib.get('name', '<unnamed>'))}")
    _need(not any(str(node.attrib.get("result", "")).lower() == "failed" for node in cases), path,
         "NUnit XML contains a failed suite or test")
    coverage = {suite: 0 for suite in NUNIT_SUITES}

    def visit(node, inherited_labels=()):
        labels = set(inherited_labels)
        values = " ".join(str(value) for value in node.attrib.values())
        labels.update(suite for suite in NUNIT_SUITES if suite in values)
        if node.tag.rsplit("}", 1)[-1].lower() == "test-case":
            for suite in labels:
                coverage[suite] += 1
        for child in node:
            visit(child, labels)

    visit(root)
    for suite in NUNIT_SUITES:
        minimum = NUNIT_MIN_CASES.get(suite, 1)
        _need(coverage[suite] >= minimum, path,
             f"NUnit test cases do not cover {suite}: expected at least {minimum}, found {coverage[suite]}")
    return {"testCases": len(test_cases), "suitesCovered": list(NUNIT_SUITES)}


def verify(editor_result: Path, nunit_results: Path, m01_baseline_root: Path, reflection_result: Path | None = None):
    report, run, baseline_path, artifacts = _verify_editor_report(editor_result)
    baseline_root = _root(baseline_path.parent, "baseline artifact root")
    baseline = _json(baseline_path)
    descriptors = _verify_sidecar_manifest(baseline_root, baseline, baseline_path)
    baseline["_actualSha256"] = digest(baseline_path)
    receipt, _, _, baseline_reflection = _verify_player_snapshot(baseline_root, baseline, descriptors, baseline_path)
    _reflection_manifest(baseline, baseline_reflection, baseline_path)
    reflection_probe = None
    if reflection_result is not None:
        _need(baseline_reflection is not None, reflection_result,
             "reflection probe acceptance requires a frozen reflection binding configuration")
        reflection_probe = _verify_reflection_probe(reflection_result, receipt, baseline_reflection)
    _pins(baseline, receipt, baseline_path)
    m01_root = _root(m01_baseline_root, "--m01-baseline-root")
    _verify_resource_baseline(baseline_root, baseline, baseline_path, m01_root)
    _verify_bundles(m01_root, baseline, baseline_path)
    baseline_edges = _edges(baseline.get("dependencyGraph"), f"{baseline_path}.dependencyGraph")
    for consumer, provider, _, _ in baseline_edges:
        _need(descriptors.get(consumer, {}).get("classification") != 5 and descriptors.get(provider, {}).get("classification") != 5,
             baseline_path, f"BuildFiltered assembly participates in runtime dependency graph: {consumer} -> {provider}")
    _need(report.get("unityVersion") == baseline["unityVersion"], editor_result,
         "editor report Unity version differs from baseline")
    _need(report.get("target") == baseline["target"] == TARGET, editor_result,
         "editor report target differs from baseline")
    expected = {
        "P01": (INTERNAL, {INTERNAL}),
        "P02": (EXTENSIBILITY, {EXTENSIBILITY, INTERNAL, "AssemblyShadowDemo.ExtensibilityConsumer"}),
        "P03": (CONTRACTS, set(CANDIDATES)),
        "P05": (INTERNAL, {INTERNAL}),
    }
    patches = {}
    for patch_id, (root, closure) in expected.items():
        patch_path = artifacts["P05-requires-bundles"] if patch_id == "P05" else artifacts[patch_id]
        patch = _verify_patch(patch_path, run, baseline, descriptors, baseline_edges, root, closure)
        patches[patch_id] = patch
    repeat = artifacts["P01-repeat"]
    repeat_sidecar = repeat.parent / "manifest.sha256"
    _need(repeat_sidecar.is_file() and repeat_sidecar.read_text().strip() == digest(repeat), repeat_sidecar,
         "P01 repeat manifest SHA sidecar is missing or stale")
    _need(repeat.read_bytes() == artifacts["P01"].read_bytes(), repeat,
         "P01 repeat patch manifest is not byte-identical")
    baseline_repeat = run / "baseline-repeat" / "baseline-manifest.json"
    _need(baseline_repeat.is_file() and not baseline_repeat.is_symlink(), baseline_repeat,
         "baseline-repeat manifest is missing from actual report runDirectory")
    _need(baseline_repeat.read_bytes() == baseline_path.read_bytes(), baseline_repeat,
         "baseline-repeat manifest is not byte-identical to the actual baseline manifest")
    nunit = _verify_nunit(nunit_results)
    return {
        "milestone": "M02",
        "resultPassed": True,
        "unityVersion": baseline["unityVersion"],
        "target": baseline["target"],
        "baselineManifestSha256": baseline["_actualSha256"],
        "patches": {name: {"changedRoots": patch["changedRoots"], "closure": patch["loadOrder"], "dllOnly": patch["dllOnly"]}
                    for name, patch in patches.items()},
        "nunit": nunit,
        **({"reflectionProbe": reflection_probe} if reflection_probe is not None else {}),
        "evidence": "SHA-256 bytes, Unity AssemblyShadow manifest/snapshot metadata, and NUnit test evidence",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-result", type=Path, required=True)
    parser.add_argument("--nunit-results", type=Path, required=True)
    parser.add_argument("--m01-baseline-root", type=Path, required=True)
    parser.add_argument("--reflection-result", type=Path,
                        help="Optional IL2CPP Player reflection-binding acceptance probe JSON")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        reflection_result = args.reflection_result.resolve() if args.reflection_result else None
        result = verify(args.editor_result.resolve(), args.nunit_results.resolve(), args.m01_baseline_root.resolve(), reflection_result)
        output = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
