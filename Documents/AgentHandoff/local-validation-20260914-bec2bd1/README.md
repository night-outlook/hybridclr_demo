# H1 local-validation checkpoint: bec2bd1

This is the portable V00–V03 result for the candidate checkout `bec2bd1936171313663a425d63bd3b0249b171c5`. V00 and V01 passed. V02 and the fresh V03 smoke reproduced the Apple Bee macro-domain blocker. V04 and V05 were not run because no provenance-bound smoke receipt exists.

Read in this order:

1. [`../LOCAL_VALIDATION.md`](../LOCAL_VALIDATION.md)
2. [`../RETURN_TO_WEB.md`](../RETURN_TO_WEB.md)
3. [`checkpoint-manifest.json`](checkpoint-manifest.json)
4. Exact Python and NUnit inventory JSON files in this directory
5. V02 original request and derived macro-action diagnostic in this directory
6. [`validation-raw-results.tar.gz`](validation-raw-results.tar.gz)
7. [`fresh-smoke-failure-inputs.tar.gz`](fresh-smoke-failure-inputs.tar.gz)

Archive identities:

- `fresh-smoke-failure-inputs.tar.gz`: `e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8`
- `validation-raw-results.tar.gz`: `b5bd929bf8be4dd95afc42650ed5b4576e01f5f088e640cacce3cc70b7641a37`

Extract archives into new directories. Do not overwrite historical evidence or relabel the fresh failed Player as accepted. Human gate remains false and R02 remains prohibited.

The V02 raw old DAG was present when replay ran but was replaced in the mutable Bee cache by V03 before it was copied. It is marked `Unavailable`; the old request and derived action inventory remain. The complete fresh V03 graph reproduces the same 16/430 split and is included in the failure archive.
