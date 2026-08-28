"""Adversarial offline proof tests. Synthetic PE fixtures are not Player evidence."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch as mock_patch
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m04_results as v
from m04_metadata import read_identity, read_identity_bytes
from shadow_tools import VerificationError
import m02_results as generic


def make_pe(name="Example", refs=(), key=b"", flags=0, culture="", version=(1, 2, 3, 4), mvid=None, wide=False):
    """Small structurally valid CLI assembly with real identity table/heap bytes."""
    strings, blobs = bytearray(b"\0"), bytearray(b"\0")
    def string(value):
        index = len(strings); strings.extend(value.encode() + b"\0"); return index
    def blob(value):
        if not value: return 0
        index = len(blobs)
        n = len(value)
        blobs.extend(bytes([n]) if n < 128 else bytes([0x80 | (n >> 8), n & 255]))
        blobs.extend(value)
        return index
    module = struct.pack("<HHHHH", 0, string(name + ".dll"), 1, 0, 0)
    assembly = struct.pack("<IHHHHIHHH", 0x8004, *version, flags, blob(key), string(name), string(culture))
    reference_rows = b""
    for ref in refs:
        reference_rows += struct.pack("<HHHHIHHHH", *ref.get("version", (4, 0, 0, 0)), ref.get("flags", 0),
                                      blob(ref.get("key", b"")), string(ref["name"]), string(ref.get("culture", "")), 0)
    valid = (1 << 0) | (1 << 32) | ((1 << 35) if refs else 0)
    tables = struct.pack("<IBBBBQQ", 0, 2, 0, 0, 1, valid, 0) + struct.pack("<II", 1, 1)
    if refs: tables += struct.pack("<I", len(refs))
    tables += module + assembly + reference_rows
    guid = (mvid or uuid.UUID("00112233-4455-6677-8899-aabbccddeeff")).bytes_le
    streams = [("#~", tables), ("#Strings", bytes(strings)), ("#Blob", bytes(blobs)), ("#GUID", guid)]
    root = struct.pack("<IHHII", 0x424a5342, 1, 1, 0, 12) + b"v4.0.30319\0\0" + struct.pack("<HH", 0, 4)
    headers_size = sum(8 + ((len(n) + 1 + 3) & ~3) for n, _ in streams)
    offset = len(root) + headers_size
    headers, content = b"", b""
    for n, data in streams:
        raw = n.encode() + b"\0"
        headers += struct.pack("<II", offset, len(data)) + raw + b"\0" * ((-len(raw)) % 4)
        content += data; offset += len(data)
    metadata = root + headers + content
    pe = bytearray(1024 + len(metadata))
    pe[0:2] = b"MZ"; struct.pack_into("<I", pe, 0x3c, 0x80)
    pe[0x80:0x84] = b"PE\0\0"
    size = 240 if wide else 224
    struct.pack_into("<HHIIIHH", pe, 0x84, 0x8664 if wide else 0x14c, 1, 0, 0, 0, size, 0x2102)
    opt = 0x98
    struct.pack_into("<H", pe, opt, 0x20b if wide else 0x10b)
    struct.pack_into("<I", pe, opt + 60, 512)
    struct.pack_into("<I", pe, opt + (108 if wide else 92), 16)
    struct.pack_into("<II", pe, opt + (112 if wide else 96) + 14 * 8, 0x2000, 72)
    section = opt + size
    pe[section:section + 8] = b".text\0\0\0"
    struct.pack_into("<IIII", pe, section + 8, len(pe) - 512, 0x2000, len(pe) - 512, 512)
    struct.pack_into("<IHHII", pe, 512, 72, 2, 5, 0x2200, len(metadata))
    pe[1024:] = metadata
    return bytes(pe)


def diagnostic(enabled=True):
    d = dict(schemaVersion=1, enabled=enabled, runtimeAbiVersion=1, state="Disabled", stateCode=0,
             lastError=0 if enabled else 1, detail="", baselineBuildId="", patchId="", generation=0,
             expected=0, staged=0, retainedBytes=0, enumerationGeneration=0, classEnumerationGeneration=0)
    for field in "ordinaryAssemblies ordinaryClasses closureLoadOrder stableAotNames commitOrder assemblies events baselineUses".split(): d[field] = []
    return d


class MetadataTests(unittest.TestCase):
    def test_actual_identity_and_ordered_rows(self):
        for wide in (False, True):
            data = make_pe(refs=[dict(name="Z", key=b"\0" * 8), dict(name="A", culture="fr", version=(2, 3, 4, 5))], wide=wide)
            identity = read_identity_bytes(data)
            self.assertEqual(identity["mvid"], "00112233-4455-6677-8899-aabbccddeeff")
            self.assertEqual(identity["fullName"], "Example, Version=1.2.3.4, Culture=neutral, PublicKeyToken=null")
            self.assertEqual([r["name"] for r in identity["referenceIdentities"]], ["Z", "A"])
            self.assertEqual(identity["referenceIdentities"][0]["publicKeyToken"], "0000000000000000")
            self.assertEqual(identity["referenceIdentities"][1]["culture"], "fr")

    def test_full_key_token_sha1_reversed_not_zero_collapsed(self):
        key = bytes(range(128))
        actual = read_identity_bytes(make_pe(key=key, flags=1, refs=[dict(name="Signed", key=key, flags=1)]))
        expected = hashlib.sha1(key).digest()[-8:][::-1].hex()
        self.assertEqual(actual["publicKeyToken"], expected)
        self.assertEqual(actual["referenceIdentities"][0]["publicKeyToken"], expected)
        zero = read_identity_bytes(make_pe(key=b"\0" * 8))
        self.assertEqual(zero["publicKeyToken"], "0000000000000000")
        self.assertNotEqual(zero["fullName"], read_identity_bytes(make_pe())["fullName"])

    def test_truncations_bad_headers_and_invalid_token_fail(self):
        valid = make_pe()
        for data in (b"synthetic-not-pe", valid[:2], valid[:80], valid[:-1], make_pe(key=b"short"), make_pe(mvid=uuid.UUID(int=0))):
            with self.subTest(length=len(data)):
                with self.assertRaises(VerificationError): read_identity_bytes(data)
        for offset, replacement in ((0, b"XY"), (0x80, b"BAD!"), (0x3c, b"\xff" * 4), (1024, b"NOPE")):
            changed = bytearray(valid); changed[offset:offset + len(replacement)] = replacement
            with self.assertRaises(VerificationError): read_identity_bytes(bytes(changed))

    def test_metadata_overlap_and_unknown_tables_fail(self):
        data = bytearray(make_pe())
        struct.pack_into("<I", data, 1024 + 32, 0)
        with self.assertRaises(VerificationError): read_identity_bytes(bytes(data))
        data = bytearray(make_pe())
        table_start = struct.unpack_from("<I", data, 1024 + 32)[0] + 1024
        data[table_start + 15] |= 0x80
        with self.assertRaises(VerificationError): read_identity_bytes(bytes(data))

    def test_fabricated_identity_with_rehashed_receipt_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "Example.dll"; path.write_bytes(make_pe(refs=[dict(name="Z"), dict(name="A")]))
            actual = read_identity(path)
            v.verify_identities([actual], [path], "identities")
            mutations = [lambda a: a.update(mvid=str(uuid.uuid4())), lambda a: a.update(version="9.0.0.0"),
                         lambda a: a.update(fullName="fabricated"), lambda a: a.update(publicKeyToken="0000000000000000"),
                         lambda a: a["referenceIdentities"].reverse(), lambda a: a["referenceIdentities"][0].update(referenceIndex=True),
                         lambda a: a["referenceIdentities"][0].update(version="5.0.0.0"),
                         lambda a: a["referenceIdentities"][0].pop("publicKeyToken"), lambda a: a.update(extra="unknown")]
            for mutate in mutations:
                claimed = copy.deepcopy(actual); mutate(claimed)
                with self.assertRaises(VerificationError): v.verify_identities([claimed], [path], "identities")
            path.write_bytes(make_pe(name="Different", refs=[dict(name="Z"), dict(name="A")]))
            actual["sha256"] = v.digest(path)
            with self.assertRaises(VerificationError): v.verify_identities([actual], [path], "identity rehash attack")

    def test_symlinked_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "real.dll"; path.write_bytes(make_pe())
            link = Path(tmp).resolve() / "link.dll"; link.symlink_to(path)
            with self.assertRaises(VerificationError): read_identity(link)


class StrictEvidenceTests(unittest.TestCase):
    def test_placeholder_exact_region_and_order(self):
        good = b'prefix\n//!!!{{PLACE_HOLDER\n"B",\n "A",\n//!!!}}PLACE_HOLDER\nsuffix'
        self.assertEqual(v.parse_placeholders(good), ["B", "A"])
        for data in (good + b"//!!!{{PLACE_HOLDER", good.replace(b'"A"', b'"b"'),
                     good.replace(b'"A"', b'"path/A"'), good.replace(b'"A"', b'" A"'),
                     good.replace(b'"A",', b"/*comment*/"), b"//!!!}}PLACE_HOLDER//!!!{{PLACE_HOLDER", good + b"\xff"):
            with self.assertRaises(VerificationError): v.parse_placeholders(data)

    def test_every_diagnostic_zero_field_is_required_and_unknown_rejected(self):
        d = diagnostic(); v._diagnostic(d, "good")
        self.assertEqual(len(d), 23)
        for field in d:
            bad = copy.deepcopy(d); del bad[field]
            with self.subTest(field=field):
                with self.assertRaises(VerificationError): v._diagnostic(bad, "missing")
        d["unknown"] = 0
        with self.assertRaises(VerificationError): v._diagnostic(d, "unknown")

    def test_uint64_exact_not_float_signed_or_boolean(self):
        d = diagnostic()
        d["baselineUses"] = [dict(name="A", kind="Reflection", detail="", type="", thread=(1 << 64) - 1, timestamp=1 << 63)]
        v._diagnostic(d, "unsigned")
        for value in (-1, 1 << 64, float(1 << 63), True):
            bad = copy.deepcopy(d); bad["baselineUses"][0]["thread"] = value
            with self.assertRaises(VerificationError): v._diagnostic(bad, "invalid unsigned")

    def test_native_inline_duplicate_members_and_fresh_snapshot_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "m04-T04-01.json"
            raw = path.with_name(path.stem + "-native-diagnostics.json")
            d = diagnostic(); text = json.dumps(d); raw.write_text(text)
            result = dict(rawDiagnosticsPath=str(raw), rawDiagnosticsSha256=v.digest(raw), nativeDiagnosticsJson=text,
                          snapshots=[dict(phase="final", diagnostics=copy.deepcopy(d))])
            v._raw_diagnostic(result, path)
            result["nativeDiagnosticsJson"] = text[:-1] + ',"enabled":true}'
            with self.assertRaises(VerificationError): v._raw_diagnostic(result, path)
            result["nativeDiagnosticsJson"] = text
            result["snapshots"][0]["diagnostics"]["generation"] = 1
            with self.assertRaises(VerificationError): v._raw_diagnostic(result, path)
            result["snapshots"][0]["diagnostics"]["generation"] = 0
            raw.write_text(text + " ")
            with self.assertRaises(VerificationError): v._raw_diagnostic(result, path)

    def test_benchmark_requires_million_raw_measurements_and_bound_identity(self):
        identity = read_identity_bytes(make_pe(name=v.INTERNAL, refs=[dict(name="mscorlib")]))
        b = dict(enabled=True, finalSameAssembly=True, finalMvidAvailable=False, requestedName=v.INTERNAL, warmupCount=1000, lookupCount=1_000_000,
                 elapsedTicks=23, stopwatchFrequency=1_000_000_000, checksum=1_000_000,
                 finalAssemblyName=v.INTERNAL, finalFullName=identity["fullName"], finalMvid="",
                 finalReferenceIdentities=[r["fullName"] for r in identity["referenceIdentities"]])
        v._verify_benchmark(b, identity, True, "benchmark")
        for key, value in (("enabled", False), ("lookupCount", 999999), ("elapsedTicks", 0), ("stopwatchFrequency", 0),
                           ("checksum", True), ("finalMvid", str(uuid.uuid4())), ("requestedName", "mscorlib"),
                           ("finalReferenceIdentities", [])):
            bad = dict(b); bad[key] = value
            with self.assertRaises(VerificationError): v._verify_benchmark(bad, identity, True, "bad benchmark")

    def test_strict_m04_schema_does_not_admit_m03_or_duplicate_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text('{"milestone":"M04","milestone":"M03"}')
            with self.assertRaises(VerificationError): v._obj(path)
        for field in v.MANIFEST_FIELDS.split():
            obj = {f: "" for f in v.MANIFEST_FIELDS.split()}; del obj[field]
            with self.assertRaises(VerificationError): v._fields(obj, v.MANIFEST_FIELDS, "manifest")

    def test_actual_source_pin_dto_includes_local_path_and_rejects_missing(self):
        pins = dict(schemaVersion=1, unityVersion="2022.3.62f2", target="StandaloneOSX", architecture="arm64")
        for i, name in enumerate(("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"), 1):
            pins[name] = dict(url="https://example.invalid/" + name, revision=str(i) * 40, localPath="../" + name)
        v._pins(pins, "pins")
        for name in ("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"):
            bad = copy.deepcopy(pins); del bad[name]["localPath"]
            with self.assertRaises(VerificationError): v._pins(bad, "missing provenance")

    def test_native_build_flag_must_be_exact_and_match_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "m04-player-build.json"
            r = {key: "" for key in v.PLAYER_FIELDS.split()}
            r.update(schemaVersion=1, milestone="M04", variant="NativeOn", baselineBuildId="M04-Baseline-test", runtimeAbiHash="a" * 64,
                     unityVersion="2022.3.62f2", target="StandaloneOSX", architecture="arm64", assemblyIdentities=[], placeholderAssemblyNames=[])
            for flag in ('--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0"',
                         '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DEXTRA"', ""):
                r["nativeArguments"] = flag; path.write_text(json.dumps(r))
                with self.assertRaisesRegex(VerificationError, "exact native compiler switch"):
                    v._verify_player_build_receipt(path, r, {}, "NativeOn")

    def test_editor_replay_hash_schema_policy_and_order_are_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fixture_path = root / "m04-fixtures.json"; fixture_path.write_text("{}")
            build_path = root / "m04-player-build.json"; build_path.write_text("{}")
            manifest = {key: "bound-" + key for key in "baselineManifestPath baselineManifestSha256 baselineInputSnapshotHash baselineBuildId runtimeAbiHash unityVersion target architecture stableAotProvenanceHash".split()}
            manifest.update(_path=str(fixture_path), _snapshot=dict(linkedPlayerReceiptHash="c" * 64))
            pins = dict(schemaVersion=1, unityVersion="2022.3.62f2", target="StandaloneOSX", architecture="arm64")
            for i, name in enumerate(("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"), 1):
                pins[name] = dict(url="https://example.invalid/" + name, revision=str(i) * 40, localPath="../" + name)
            baseline = dict(playerBuildGuid="1" * 32, nativeLibrarySha256="d" * 64, sourcePins=pins)
            rows = [dict(patchId=pid, patchManifestSha256="e" * 64, compileSnapshotHash="f" * 64,
                         changedRoots=[v.INTERNAL] if pid == "P01" else list(v.CANDIDATES),
                         closureLoadOrder=[v.INTERNAL] if pid == "P01" else list(v.CANDIDATES)) for pid in ("P01", "P03")]
            fixtures = {r["patchId"]: (r,) for r in rows}
            replay = {key: value for key, value in manifest.items() if not key.startswith("_")}
            replay.update(schemaVersion=1, milestone="M04", result="Passed", comparisonPolicy=v.EDITOR_REPLAY_POLICY,
                          fixtureManifestPath=str(fixture_path), fixtureManifestSha256=v.digest(fixture_path),
                          playerBuildReceiptPath=str(build_path), playerBuildReceiptSha256=v.digest(build_path),
                          playerBuildGuid=baseline["playerBuildGuid"], nativeLibrarySha256=baseline["nativeLibrarySha256"],
                          linkedPlayerReceiptHash="c" * 64, validatorSourcePins=pins, fixtures=copy.deepcopy(rows))
            replay_path = root / "m04-editor-replay.json"; replay_path.write_text(json.dumps(replay))
            v._verify_replay(replay_path, manifest, baseline, fixtures, build_path)
            mutations = [lambda r: r.update(comparisonPolicy="compiler-linked-policy-graph-resource-abi:2"),
                         lambda r: r.update(playerBuildReceiptSha256="0" * 64), lambda r: r.update(milestone="M03"),
                         lambda r: r["fixtures"].reverse(), lambda r: r.pop("playerBuildReceiptPath"),
                         lambda r: r["validatorSourcePins"]["demo"].update(revision="9" * 40), lambda r: r.update(unknown=True)]
            for mutate in mutations:
                bad = copy.deepcopy(replay); mutate(bad); replay_path.write_text(json.dumps(bad))
                with self.assertRaises(VerificationError): v._verify_replay(replay_path, manifest, baseline, fixtures, build_path)


class SyntheticRuntimeSuite:
    """Result-gate fixtures only. Not the compiler/resource/Editor input gate."""
    def __init__(self, root):
        self.root = root
        self.results = root / "results"; self.results.mkdir()
        self.fixture_path = root / "m04-fixtures.json"
        self.manifest = dict(_path=str(self.fixture_path), baselineBuildId="M04-Baseline-unit-test", runtimeAbiHash="a" * 64,
                             stableAotNames=["mscorlib", "unityengine.coremodule"])
        self.fixture_path.write_text('{"syntheticFixtureOnly":true}')
        self.players, self.player_paths, self.fixtures = {}, {}, {}
        for enabled in (True, False):
            label = "on" if enabled else "off"
            snap = root / label; snap.mkdir()
            output = root / (label + ".app"); (output / "Contents").mkdir(parents=True)
            identities = []
            for name in (*v.CANDIDATES, "mscorlib", "UnityEngine.CoreModule"):
                dll = snap / (name + ".dll")
                refs = [dict(name=v.CANDIDATES[0])] if name == v.INTERNAL else []
                dll.write_bytes(make_pe(name=name, refs=refs, mvid=uuid.uuid5(uuid.NAMESPACE_DNS, label + name)))
                identities.append(read_identity(dll))
            player = dict(baselineBuildId=self.manifest["baselineBuildId"], runtimeAbiHash=self.manifest["runtimeAbiHash"],
                          unityVersion="2022.3.62f2", buildGuid=label * 16, playerOutput=str(output), inputSnapshot=str(snap),
                          assemblyIdentities=identities, placeholderAssemblyNames=["AssemblyShadowBaseline.HotUpdate"])
            self.players[label] = player
            self.player_paths[label] = snap / "m04-player-build.json"
            self.player_paths[label].write_text(json.dumps(player))
        self.manifest["_onBuild"] = self.players["on"]
        for pid in ("P01", "P03"):
            root_patch = root / pid; root_patch.mkdir()
            order = [v.INTERNAL] if pid == "P01" else list(v.CANDIDATES)
            identities, closure = [], []
            for name in order:
                dll = root_patch / (name + ".dll"); pdb = root_patch / (name + ".pdb")
                dll.write_bytes(make_pe(name=name, refs=[dict(name="mscorlib", key=b"\0" * 8)], mvid=uuid.uuid5(uuid.NAMESPACE_DNS, pid + name)))
                pdb.write_bytes(b"synthetic-symbols")
                identity = read_identity(dll); identities.append(identity)
                closure.append(dict(name=name, mvid=identity["mvid"], sha256=identity["sha256"], pdbSha256=v.digest(pdb)))
            patch_path = root_patch / "patch-manifest.json"
            patch_path.write_text(json.dumps(dict(patchId=pid, closure=closure)))
            fixture = dict(patchId=pid, closureLoadOrder=order, assemblyIdentities=identities, compileSnapshotHash="b" * 64)
            self.fixtures[pid] = (fixture, root_patch, patch_path, root_patch, {})
        self.fixed_bytes = make_pe(name="AssemblyShadowBaseline.HotUpdate", version=(0, 0, 0, 0))
        self.fixed_hash = hashlib.sha256(self.fixed_bytes).hexdigest()
        self.documents = {}
        for index, mode in enumerate(sorted(v.REQUIRED_MODES)):
            self.documents[mode] = self.result(mode, index + 100)
            self.write(mode)

    def ordinary(self, player):
        ints = "schemaVersion assemblyCountBefore assemblyCountAfter ordinaryCountBefore ordinaryCountAfter ordinaryCountAfterDuplicate knownNameResolveEvents supplementaryFirstCode supplementaryRepeatCode supplementaryInvalidModeCode".split()
        bools = "aotLoadMatchesType aotMvidAvailable placeholderFoundBefore placeholderHiddenBefore placeholderSameAfterLoad fixedImageMvidAvailable fixedImageTamperRejected fixedImageNullRejected fixedImageCallerBytesUnchanged loadedNameSame enumeratedSame duplicateRejected knownNameResolveSame supplementaryCallerBytesUnchanged".split()
        result = {k: 0 if k in ints else False if k in bools else "" for k in v.ORDINARY_FIELDS.split()}
        for key in set(bools) - {"aotMvidAvailable", "fixedImageMvidAvailable"}: result[key] = True
        result.update(schemaVersion=1, moduleMvidObservationPolicy=v.MVID_POLICY, assemblyCountBefore=10, assemblyCountAfter=11,
                      ordinaryCountAfter=1, ordinaryCountAfterDuplicate=1, supplementaryFirstCode=0, supplementaryRepeatCode=5,
                      supplementaryInvalidModeCode=6, placeholderName="AssemblyShadowBaseline.HotUpdate",
                      knownNameResolveInput="AssemblyShadowBaseline.HotUpdate", fixedImageMarker="M00-HOTUPDATE-OK",
                      duplicateExceptionType="System.ExecutionEngineException", duplicateMessage="reloading placeholder assembly is not supported!")
        mscorlib = next(a for a in player["assemblyIdentities"] if a["name"] == "mscorlib")
        result.update(aotFullName=mscorlib["fullName"], supplementaryInputPath=mscorlib["path"], supplementaryInputSha256=mscorlib["sha256"],
                      supplementaryInputFullName=mscorlib["fullName"], supplementaryInputMvid=mscorlib["mvid"])
        image = Path(player["playerOutput"]) / "Contents/Resources/Data/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"
        image.parent.mkdir(parents=True, exist_ok=True); image.write_bytes(self.fixed_bytes)
        parsed = read_identity(image)
        result.update(fixedImagePath=str(image), fixedImageSha256=parsed["sha256"], fixedImageFullName=parsed["fullName"], knownNameResolveFullName=parsed["fullName"])
        sites = []
        for i, site_id in enumerate(sorted(generic.M02_REFLECTION_SITE_IDS)):
            kind = "FixedAssemblyBytes" if site_id == "m00-normal-hot-update-image" else "FiniteAssemblyList" if site_id == "urp-volume-assembly-domain" else "FiniteAssemblyTypes" if site_id == "urp-volume-type-domain" else "TypeGetType"
            allowed = sorted(generic.M02_CANVAS_ALLOWED_TYPES) if site_id == "urp-debug-ui-prefab-types" else sorted(generic.M02_VOLUME_ALLOWED_TYPES) if site_id.startswith("urp-volume") else []
            sites.append(dict(id=site_id, assembly="AssemblyShadowDemo.Bootstrap", typeName="Synthetic.Owner", kind=kind,
                              methodSignature="System.Void Synthetic.Owner::Method" + str(i) + "()", originalMethodHash="a" * 64,
                              operationIndex=0, reason="synthetic verifier regression", allowedTypes=allowed,
                              imageSha256=self.fixed_hash if kind == "FixedAssemblyBytes" else "",
                              providerAssemblyIdentity=parsed["fullName"] if kind == "FixedAssemblyBytes" else "",
                              imagePath=generic.M02_FIXED_IMAGE_PATH if kind == "FixedAssemblyBytes" else ""))
        raw = json.dumps(dict(schemaVersion=2, transformerVersion=2, sites=sites)).encode()
        config = Path(player["playerOutput"]) / "Contents/reflection-bindings.json"; config.write_bytes(raw)
        captured = Path(player["inputSnapshot"]) / "ReflectionBindings/configuration.json"; captured.parent.mkdir(exist_ok=True); captured.write_bytes(raw)
        # Only this synthetic fixture's M00 hash differs from the immutable
        # production contract. No production validator is replaced or skipped.
        with mock_patch.object(generic, "M02_FIXED_IMAGE_SHA256", self.fixed_hash):
            reflection = v._reflection_parse(config, raw)
        result.update(configurationPath=str(config), configurationSha256=v.digest(config), configurationHash=reflection["canonicalHash"],
                      fixedImageGuard="__AssemblyShadowReflectionBinding_" + reflection["canonicalHash"] + "_" + hashlib.sha256(b"m00-normal-hot-update-image").hexdigest())
        return result

    def benchmark(self, identity, enabled):
        return dict(enabled=enabled, finalSameAssembly=True, finalMvidAvailable=False, finalMvid="", requestedName=v.INTERNAL,
                    warmupCount=1000, lookupCount=1_000_000, checksum=1_000_000, elapsedTicks=55, stopwatchFrequency=1_000_000_000,
                    finalAssemblyName=v.INTERNAL, finalFullName=identity["fullName"],
                    finalReferenceIdentities=[r["fullName"] for r in identity["referenceIdentities"]])

    def result(self, mode, pid):
        array_fields = "stageOrder checks snapshots actualLogicalAssemblies assemblyObservations loadObservations refRows executingWitnesses stageResults".split()
        r = {key: [] if key in array_fields else "" for key in v.RESULT_FIELDS.split()}
        label = "off" if mode in v.OFF_MODES else "on"; player = self.players[label]
        r.update(schemaVersion=1, processId=pid, milestone="M04", mode=mode, result="Passed", error="", il2cpp=True,
                 moduleMvidObservationPolicy=v.MVID_POLICY, platform="OSXPlayer", playerDataPath=str(Path(player["playerOutput"]) / "Contents"),
                 fixtureManifestPath=str(self.fixture_path), fixtureManifestSha256=v.digest(self.fixture_path), playerBuildReceiptPath=str(self.player_paths[label]),
                 playerBuildReceiptSha256=v.digest(self.player_paths[label]), businessMarker="M04-REFERENCE-PROBE", ordinary=None, benchmark=None)
        for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "buildGuid"): r[key] = player[key]
        identities = {a["name"]: a for a in player["assemblyIdentities"]}
        def check(name, code="Success"):
            r["checks"].append(dict(name=name, actual=code, expected=code, actualCode=v.ERROR_CODES[code], expectedCode=v.ERROR_CODES[code]))
        def observation(name, closure, logical=True):
            shadow = name in closure
            return dict(name=name, fullName=identities[name]["fullName"], mvid="", mvidAvailable=False,
                        executionCode="Success" if name in v.CANDIDATES else "CandidateNotRegistered",
                        executionMode="InterpreterShadow" if shadow else "AotBaseline", isInterpreter=shadow, logical=logical)
        if mode in v.OFF_MODES:
            r["benchmark"] = self.benchmark(identities[v.INTERNAL], False)
            if mode == "T04-08":
                for name in "configure begin stage validate commit abort state execution-mode diagnostics".split(): check(name, "FeatureDisabled")
                for key in "configure begin stage validate commit abort stateCode executionModeCode diagnosticsCode".split(): r[key] = "FeatureDisabled"
                r.update(state="Disabled", executionMode="AotBaseline", ordinary=self.ordinary(player))
                r["snapshots"] = [dict(phase="disabled", diagnostics=diagnostic(False))]
            return r
        patch_id = "P01" if mode == "T04-01" else "P03"
        f, _, path, _, _ = self.fixtures[patch_id]
        patch = json.loads(path.read_text())
        expected = [v.CANDIDATES[0]] if mode == "T04-05" else f["closureLoadOrder"]
        stages = [v.INTERNAL] if mode == "T04-04" else expected
        r.update(patchId=patch_id, patchManifestPath=str(path), patchManifestSha256=v.digest(path), compileSnapshotHash=f["compileSnapshotHash"],
                 configure="Success", begin="Success", stateCode="Success", diagnosticsCode="Success", stageOrder=list(stages))
        d = diagnostic(); d["ordinaryAssemblies"] = [dict(name=n, isInterpreter=False) for n in identities]
        def snapshot(phase): r["snapshots"].append(dict(phase=phase, diagnostics=copy.deepcopy(d)))
        def event(kind, name=""):
            d["events"].append(dict(sequence=len(d["events"]) + 1, kind=kind, name=name, generation=d["generation"], stagedCount=d["staged"]))
        snapshot("initial"); check("configure"); check("begin")
        d.update(baselineBuildId=r["baselineBuildId"], patchId=patch_id, state="Staging" if mode == "T04-04" else "Staged",
                 stableAotNames=self.manifest["stableAotNames"], expected=len(expected), staged=len(stages), retainedBytes=500,
                 closureLoadOrder=list(expected))
        d["stateCode"] = v.STATE_CODES[d["state"]]
        for n in expected:
            entry = next(a for a in patch["closure"] if a["name"] == n)
            d["assemblies"].append(dict(name=n, mvid=entry["mvid"] if n in stages else "", skeletonBuilt=n in stages,
                                        runtimeMetadataInitialized=False, published=False, moduleInitializerAttempted=False, moduleInitializerRan=False))
        for n in stages:
            check("stage-" + n); event("skeleton-created", n)
            entry = next(a for a in patch["closure"] if a["name"] == n)
            r["stageResults"].append(dict(name=n, code="Success", dllSha256=entry["sha256"], pdbSha256=entry["pdbSha256"]))
        snapshot("staged")
        validation = "ClosureMemberMissing" if mode == "T04-04" else "ReferenceEscapesClosure" if mode == "T04-05" else "Success"
        r["validate"] = validation; check("validate", validation); d["lastError"] = v.ERROR_CODES[validation]
        if mode == "T04-05": d["detail"] = f"ShadowClosureViolation Requester={v.INTERNAL} Provider={v.CANDIDATES[0]} ReferenceIndex=0 Path={v.INTERNAL} -> {v.CANDIDATES[0]} Site=Validate.PhysicalAotAssemblyRef"
        if validation == "Success":
            d.update(state="Validated", stateCode=v.STATE_CODES["Validated"])
            for a in d["assemblies"]:
                a["runtimeMetadataInitialized"] = True; event("metadata-begin", a["name"]); event("metadata-ready", a["name"])
        snapshot("validated")
        if mode not in v.SUCCESS_MODES:
            if mode == "T04-03":
                check("commit-after-baseline-use", "BaselineAlreadyUsed"); check("abort-after-baseline-use")
                r["commit"] = "BaselineAlreadyUsed"
                r["loadObservations"] = [dict(requested=v.CANDIDATES[0], overload="staged-normal", assemblyName=v.CANDIDATES[0], sameAssembly=True)]
                r["actualLogicalAssemblies"] = [observation(n, set(), False) for n in identities]
                d["baselineUses"] = [dict(name=v.CANDIDATES[0], kind="Reflection", detail="normal baseline load", type="", thread=(1 << 64) - 1, timestamp=123)]
            else: check("abort")
            r.update(abort="Success", state="Aborted")
            d.update(state="Aborted", stateCode=v.STATE_CODES["Aborted"], lastError=0)
            event("transaction-aborted"); snapshot("sealed" if mode == "T04-03" else "aborted")
            return r
        check("commit"); r.update(commit="Success", state="Committed", businessMarker="PATCH-P01-INTERNAL")
        d.update(state="Committed", stateCode=v.STATE_CODES["Committed"], generation=1, enumerationGeneration=1, classEnumerationGeneration=1,
                 commitOrder=list(expected))
        event("active-published")
        for a in d["assemblies"]:
            a.update(published=True, moduleInitializerAttempted=True, moduleInitializerRan=True)
            d["ordinaryAssemblies"].append(dict(name=a["name"], isInterpreter=True))
            event("initializer-begin", a["name"]); event("initializer-complete", a["name"])
        snapshot("committed")
        identities.update({a["name"]: a for a in f["assemblyIdentities"]})
        r["assemblyObservations"] = [observation(n, set(expected)) for n in identities]
        if mode != "T04-09-BenchmarkOn": r["actualLogicalAssemblies"] = copy.deepcopy(r["assemblyObservations"])
        if mode in ("T04-02", "T04-06", "T04-07"):
            for name in v.PROVIDER_ORDER:
                prefix = "AssemblyA" if name.startswith("AssemblyA.") else "Consumers"
                for overload, requested in (("simple", name), ("dll-suffix", name + ".dll"), ("AssemblyName", name),
                                            ("Type.GetType", v.TYPE_NAMES[name] + ", " + name), ("path", prefix + "/" + name + ".dll"),
                                            ("case", name.lower()), ("backslash-path", prefix + "\\" + name + ".dll")):
                    r["loadObservations"].append(dict(requested=requested, overload=overload, assemblyName=name, sameAssembly=True))
                r["refRows"].extend(dict(assemblyName=name, **ref) for ref in identities[name]["referenceIdentities"])
                r["executingWitnesses"].append(dict(assemblyName=name, executingAssemblyName=name, sameAssembly=True))
        if mode == "T04-02": r["ordinary"] = self.ordinary(player)
        if mode == "T04-09-BenchmarkOn": r["benchmark"] = self.benchmark(identities[v.INTERNAL], True)
        snapshot("final")
        return r

    def write(self, mode):
        result = self.documents[mode]
        path = self.results / ("m04-" + mode + ".json")
        if result["snapshots"]:
            raw = path.with_name(path.stem + "-native-diagnostics.json")
            text = json.dumps(result["snapshots"][-1]["diagnostics"])
            raw.write_text(text)
            result.update(rawDiagnosticsPath=str(raw), rawDiagnosticsSha256=v.digest(raw), nativeDiagnosticsJson=text)
        path.write_text(json.dumps(result))
        return path

    def verify(self):
        with mock_patch.object(generic, "M02_FIXED_IMAGE_SHA256", self.fixed_hash):
            return v.verify_results(self.results, self.manifest, {}, self.fixtures, self.players["on"], self.players["off"], self.player_paths["on"], self.player_paths["off"])


class RuntimeModeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.suite = SyntheticRuntimeSuite(Path(self.temp.name).resolve())

    def test_all_ten_runtime_mode_contracts_pass(self):
        result = self.suite.verify()
        self.assertTrue(result["resultPassed"])
        self.assertEqual({r["mode"] for r in result["modes"]}, v.REQUIRED_MODES)

    def test_adversarial_rehashed_runtime_observations(self):
        self.suite.verify()
        mutations = [
            ("T04-01", lambda r: r["assemblyObservations"][2].update(isInterpreter=False)),
            ("T04-01", lambda r: r["assemblyObservations"][0].update(mvidAvailable=True, mvid=str(uuid.uuid4()))),
            ("T04-01", lambda r: r["actualLogicalAssemblies"].reverse()),
            ("T04-01", lambda r: r["actualLogicalAssemblies"].append(copy.deepcopy(r["actualLogicalAssemblies"][0]))),
            ("T04-02", lambda r: r["refRows"][0].update(publicKeyToken="")),
            ("T04-02", lambda r: r["refRows"].reverse()),
            ("T04-02", lambda r: r["ordinary"].update(knownNameResolveEvents=1)),
            ("T04-02", lambda r: r["ordinary"].update(supplementaryRepeatCode=0)),
            ("T04-03", lambda r: r["snapshots"][-1]["diagnostics"].update(baselineUses=[])),
            ("T04-03", lambda r: r.update(commit="Success")),
            ("T04-04", lambda r: r["snapshots"][2]["diagnostics"]["assemblies"][2].update(runtimeMetadataInitialized=True)),
            ("T04-05", lambda r: r["snapshots"][2]["diagnostics"].update(detail="ShadowClosureViolation")),
            ("T04-05", lambda r: r["snapshots"][2]["diagnostics"].update(detail=r["snapshots"][2]["diagnostics"]["detail"].replace("ReferenceIndex=0", "ReferenceIndex=9"))),
            ("T04-06", lambda r: r["loadObservations"][5].update(requested=v.CANDIDATES[0])),
            ("T04-07", lambda r: r["executingWitnesses"][0].update(sameAssembly=False)),
            ("T04-08", lambda r: r["checks"][0].update(actual="Success", actualCode=0, expected="Success", expectedCode=0)),
            ("T04-08", lambda r: r["snapshots"][0]["diagnostics"].pop("generation")),
            ("T04-09-BenchmarkOn", lambda r: r["benchmark"].update(finalSameAssembly=False)),
            ("T04-10-BenchmarkOff", lambda r: r.update(configure="FeatureDisabled")),
            ("T04-10-BenchmarkOff", lambda r: r["benchmark"].update(enabled=True)),
            ("T04-01", lambda r: r["snapshots"].__setitem__(1, copy.deepcopy(r["snapshots"][-1]))),
            ("T04-01", lambda r: r["snapshots"][1]["diagnostics"]["assemblies"][0].update(mvid=str(uuid.uuid4()))),
            ("T04-01", lambda r: r["checks"].reverse()),
            ("T04-01", lambda r: r["snapshots"][-1]["diagnostics"]["ordinaryAssemblies"].pop()),
        ]
        for mode, mutate in mutations:
            original = copy.deepcopy(self.suite.documents[mode])
            mutate(self.suite.documents[mode]); self.suite.write(mode)
            with self.subTest(mode=mode, mutation=mutate):
                with self.assertRaises(VerificationError): self.suite.verify()
            self.suite.documents[mode] = original; self.suite.write(mode)

    def test_missing_mode_duplicate_process_or_extra_mode_fail(self):
        self.suite.verify()
        path = self.suite.results / "m04-T04-01.json"
        path.rename(path.with_suffix(".saved"))
        with self.assertRaises(VerificationError): self.suite.verify()
        path.with_suffix(".saved").rename(path)
        self.suite.documents["T04-02"]["processId"] = self.suite.documents["T04-01"]["processId"]
        self.suite.write("T04-02")
        with self.assertRaises(VerificationError): self.suite.verify()

    def test_production_fixed_image_pin_cannot_be_replaced(self):
        o = self.suite.documents["T04-02"]["ordinary"]
        with self.assertRaises(VerificationError): v._verify_ordinary(o, self.suite.players["on"], "untrusted synthetic M00 bytes")


if __name__ == "__main__":
    unittest.main()
