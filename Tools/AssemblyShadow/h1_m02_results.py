#!/usr/bin/env python3
"""Run the existing M02 verifier with the exact H1 witness parser extension.

The underlying M02 verifier remains the owner of manifests, snapshots, linked
proofs, resources and NUnit evidence. This wrapper changes only interpretation
of the sixth exact H1 FixedAssemblyBytes declaration; historical five-site
artifacts continue through the original parser unchanged.
"""
from __future__ import annotations

import hashlib
import json
import sys

import m02_results as m02
import h1_witness_contract as witness

_original_parse = m02._reflection_parse


def _current_parse(path, raw: bytes):
    try:
        configuration = json.loads(raw.decode("utf-8"), object_pairs_hook=witness.unique_pairs)
    except (UnicodeDecodeError, ValueError) as error:
        raise m02.VerificationError(f"{path}: invalid reflection binding configuration: {error}") from error
    if not isinstance(configuration, dict) or not isinstance(configuration.get("sites"), list):
        return _original_parse(path, raw)
    ids = [site.get("id") for site in configuration["sites"] if isinstance(site, dict)]
    if witness.SITE_ID not in ids:
        return _original_parse(path, raw)
    try:
        witness.expected_site_ids(configuration, m02.M02_REFLECTION_SITE_IDS, require_current=True)
    except ValueError as error:
        raise m02.VerificationError(f"{path}: {error}") from error

    historical = dict(configuration)
    historical["sites"] = [site for site in configuration["sites"] if site.get("id") != witness.SITE_ID]
    historical_raw = json.dumps(historical, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    base = _original_parse(path, historical_raw)
    site = next(site for site in configuration["sites"] if site.get("id") == witness.SITE_ID)
    declaration = {
        "id": site["id"], "consumer": site["assembly"], "typeName": site["typeName"],
        "methodSignature": site["methodSignature"], "originalMethodHash": site["originalMethodHash"],
        "operationIndex": site["operationIndex"], "allowedTypes": [], "reason": site["reason"],
        "providers": [m02._canonical_assembly_name(site["providerAssemblyIdentity"].split(",", 1)[0])],
        "kind": "FixedAssemblyBytes", "imageSha256": site["imageSha256"],
        "providerAssemblyIdentity": site["providerAssemblyIdentity"], "imagePath": site["imagePath"],
    }
    declarations = list(base["declarations"]) + [declaration]
    declarations.sort(key=lambda item: item["id"])
    return {
        "rawSha256": hashlib.sha256(raw).hexdigest(),
        "canonicalHash": m02._reflection_canonical_hash(configuration, path),
        "declarations": declarations,
        "configuration": configuration,
    }


def install() -> None:
    m02._reflection_parse = _current_parse


def main(argv=None) -> int:
    install()
    return m02.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
