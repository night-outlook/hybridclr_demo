import copy
import json
import unittest

import h1_witness_contract as h


def site():
    return {"id": h.SITE_ID, "assembly": h.ASSEMBLY, "typeName": h.TYPE_NAME,
        "methodSignature": h.METHOD, "kind": "FixedAssemblyBytes", "allowedTypes": [],
        "originalMethodHash": h.METHOD_VARIANTS[0][0], "operationIndex": 25,
        "additionalMethodVariants": [{"originalMethodHash": h.METHOD_VARIANTS[1][0], "operationIndex": 25}],
        "imageSha256": h.IMAGE_SHA256, "imagePath": h.IMAGE_PATH, "providerAssemblyIdentity": h.PROVIDER,
        "providerSemanticVariants": [{"compilerMode": k, "semanticHash": v} for k, v in h.SEMANTIC_VARIANTS.items()],
        "reason": "Pinned ordinary witness; not a general byte loader"}


def configuration():
    return {"schemaVersion": 4, "transformerVersion": 4,
            "sites": [{"id": name} for name in sorted(h.HISTORICAL_IDS)] + [site()]}


class WitnessContractTests(unittest.TestCase):
    def test_current_exact(self):
        self.assertEqual(h.CURRENT_IDS, h.expected_site_ids(configuration(), require_current=True))

    def test_historical_five_preserved(self):
        data = configuration(); data["sites"].pop()
        self.assertEqual(h.HISTORICAL_IDS, h.expected_site_ids(data))
        with self.assertRaisesRegex(ValueError, "requires its witness"):
            h.expected_site_ids(data, require_current=True)

    def test_unknown_site_rejected(self):
        data = configuration(); data["sites"].append({"id": "unbounded-loader"})
        with self.assertRaises(ValueError): h.expected_site_ids(data)

    def test_duplicate_site_rejected(self):
        data = configuration(); data["sites"].append(site())
        with self.assertRaises(ValueError): h.expected_site_ids(data)

    def test_schema3_cannot_authorize_h1(self):
        data = configuration(); data["schemaVersion"] = data["transformerVersion"] = 3
        with self.assertRaises(ValueError): h.expected_site_ids(data)

    def test_every_pinned_field_rejected_when_changed(self):
        for key in ("assembly", "typeName", "methodSignature", "originalMethodHash", "kind",
                    "imagePath", "imageSha256", "providerAssemblyIdentity"):
            with self.subTest(field=key):
                data = site(); data[key] += "changed"
                with self.assertRaises(ValueError): h.validate_site(data)

    def test_operation_not_boolean_or_different(self):
        for value in (True, 24, 26, "25"):
            with self.subTest(value=value):
                data = site(); data["operationIndex"] = value
                with self.assertRaises(ValueError): h.validate_site(data)

    def test_discovered_variant_not_auto_approved(self):
        data = site(); data["additionalMethodVariants"].append({"originalMethodHash": "0" * 64, "operationIndex": 25})
        with self.assertRaises(ValueError): h.validate_site(data)

    def test_missing_provider_variant(self):
        data = site(); data["providerSemanticVariants"].pop()
        with self.assertRaises(ValueError): h.validate_site(data)

    def test_duplicate_provider_mode(self):
        data = site(); data["providerSemanticVariants"][1] = copy.deepcopy(data["providerSemanticVariants"][0])
        with self.assertRaises(ValueError): h.validate_site(data)

    def test_reversed_provider_order_allowed(self):
        data = site(); data["providerSemanticVariants"].reverse(); h.validate_site(data)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError): json.loads('{"id":1,"id":2}', object_pairs_hook=h.unique_pairs)

    def test_not_a_new_type_whitelist(self):
        data = site(); data["allowedTypes"] = ["AssemblyA.Contracts.Foo, AssemblyA.Contracts"]
        with self.assertRaises(ValueError): h.validate_site(data)

if __name__ == '__main__': unittest.main()
