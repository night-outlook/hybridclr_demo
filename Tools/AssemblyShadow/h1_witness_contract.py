"""Exact H1 witness declaration. Historical M02 input remains readable.

This validates declarations only. The existing CodeGen transformer and linked
input verifier still have to prove that the declared call was transformed.
No dynamically discovered method hash is automatically approved here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SITE_ID = "h1-count-ordinary-witness-image"
ASSEMBLY = "AssemblyShadowDemo.Bootstrap"
TYPE_NAME = "AssemblyShadowDemo.H1CountEarlyStartup"
METHOD = ("AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt "
          "AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()")
METHOD_VARIANTS = (
    ("fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e", 25),
    ("4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e", 25),
)
IMAGE_SHA256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27"
IMAGE_PATH = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"
PROVIDER = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
SEMANTIC_VARIANTS = {
    "Development": "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369",
    "Release": "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022",
}
HISTORICAL_IDS = frozenset(("urp-debug-ui-prefab-types", "urp-serializable-enum-player",
    "urp-volume-assembly-domain", "urp-volume-type-domain", "m00-normal-hot-update-image"))
CURRENT_IDS = HISTORICAL_IDS | {SITE_ID}


def require(condition: object, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def validate_site(site: dict) -> None:
    require(type(site) is dict, "H1 witness site must be an object")
    expected = {"id": SITE_ID, "assembly": ASSEMBLY, "typeName": TYPE_NAME,
        "methodSignature": METHOD, "kind": "FixedAssemblyBytes", "allowedTypes": [],
        "originalMethodHash": METHOD_VARIANTS[0][0], "operationIndex": 25,
        "imageSha256": IMAGE_SHA256, "imagePath": IMAGE_PATH,
        "providerAssemblyIdentity": PROVIDER}
    for key, value in expected.items():
        require(type(site.get(key)) is type(value) and site[key] == value,
                "H1 witness exact contract differs: " + key)
    additional = site.get("additionalMethodVariants")
    require(additional == [{"originalMethodHash": METHOD_VARIANTS[1][0], "operationIndex": 25}]
            and type(additional[0]["operationIndex"]) is int,
            "H1 witness method variants differ; compiled changes require review, not discovery-based approval")
    variants = site.get("providerSemanticVariants")
    require(type(variants) is list and len(variants) == 2 and
            all(type(row) is dict and set(row) == {"compilerMode", "semanticHash"} and
                type(row["compilerMode"]) is str and type(row["semanticHash"]) is str for row in variants),
            "H1 witness requires the two exact provider semantic variants")
    require(len({row["compilerMode"] for row in variants}) == 2 and
            {row["compilerMode"]: row["semanticHash"] for row in variants} == SEMANTIC_VARIANTS,
            "H1 witness provider semantic variants differ")
    require(type(site.get("reason")) is str and bool(site["reason"].strip()), "H1 witness reason is missing")


def expected_site_ids(configuration: dict, historical_ids=HISTORICAL_IDS,
                      *, require_current: bool = False) -> frozenset[str]:
    """Return one exact schema-specific domain, never a union of optional sites.

    Callers still validate each historical declaration using the M02 verifier.
    Only archival readers may omit the H1 site. Fresh H1 preflight requires it.
    """
    require(type(configuration) is dict and type(configuration.get("sites")) is list,
            "Reflection binding configuration is missing")
    sites = configuration["sites"]
    require(all(type(site) is dict and type(site.get("id")) is str for site in sites), "Invalid binding site")
    ids = [site["id"] for site in sites]
    require(len(ids) == len(set(ids)), "Duplicate reflection binding site")
    current = SITE_ID in ids
    require(not require_current or current, "Current H1 candidate requires its witness site; historical five-site input is insufficient")
    if current:
        require(type(configuration.get("schemaVersion")) is int and configuration["schemaVersion"] == 4 and
                type(configuration.get("transformerVersion")) is int and configuration["transformerVersion"] == 4,
                "H1 witness requires schema/transformer 4")
        validate_site(next(site for site in sites if site["id"] == SITE_ID))
    expected = frozenset(historical_ids) | ({SITE_ID} if current else set())
    # Schema 1 historical generic parser is deliberately left to its old owner.
    if current or configuration.get("schemaVersion", 0) >= 2:
        require(set(ids) == expected, "Reflection binding exact site membership differs")
    return expected


def verify_runtime_probe(result: dict, configuration_sha256: str) -> None:
    require(type(result) is dict and result.get("schemaVersion") == 2 and
            result.get("mode") == "M02ReflectionBindings" and result.get("result") == "Passed" and
            result.get("il2cpp") is True, "Not a successful IL2CPP M02 runtime probe")
    require(result.get("configurationSha256") == configuration_sha256, "Runtime binding bytes differ")
    expected = {"h1WitnessContractValidated": True, "h1WitnessMethod": METHOD,
        "h1WitnessPrimaryHash": METHOD_VARIANTS[0][0], "h1WitnessOperationIndex": 25,
        "h1WitnessImageSha256": IMAGE_SHA256, "h1WitnessProviderAssembly": PROVIDER,
        "h1WitnessTamperRejected": True, "h1WitnessNullRejected": True,
        "h1WitnessCallerBytesUnchanged": True, "h1WitnessAssemblyResolveEvents": 0}
    for key, value in expected.items():
        require(type(result.get(key)) is type(value) and result[key] == value, "Runtime H1 witness check differs: " + key)
    config_hash = result.get("configurationHash")
    require(type(config_hash) is str and len(config_hash) == 64 and
            all(c in "0123456789abcdef" for c in config_hash), "Runtime configuration identity missing")
    guard = "__AssemblyShadowReflectionBinding_" + config_hash + "_" + hashlib.sha256(SITE_ID.encode()).hexdigest()
    require(result.get("h1WitnessGuard") == guard, "H1 generated wrapper identity differs")
    # Positive loading is separately mandatory in the fresh count-loader evidence.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--runtime-result", type=Path)
    args = parser.parse_args()
    root = args.project.resolve(strict=True)
    config = root / "ProjectSettings/AssemblyShadowReflectionBindings.json"
    raw = config.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    expected_site_ids(value, require_current=True)
    image = root / IMAGE_PATH
    require(image.is_file() and not image.is_symlink(), "Pinned witness image unavailable")
    require(hashlib.sha256(image.read_bytes()).hexdigest() == IMAGE_SHA256, "Pinned witness image bytes differ")
    if args.runtime_result is not None:
        verify_runtime_probe(json.loads(args.runtime_result.read_text(), object_pairs_hook=unique_pairs), hashlib.sha256(raw).hexdigest())
    print(json.dumps({"kind": "H1WitnessConfigurationCheck", "status": "ConfigurationValidatedNotCompiled",
        "configurationSha256": hashlib.sha256(raw).hexdigest(), "siteId": SITE_ID,
        "compiledTransformationVerified": False, "humanGatePassed": False, "mayEnterR02": False}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print("Failed: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
