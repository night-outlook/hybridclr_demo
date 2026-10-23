# Primary source audit — P1 Local frozen-byte collector correction

## Evidence read and reproduced

- Source: archived Local e1e5 FINDING.json, run-once.py (original SHA256 73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd), audit.py, original CPP/API frozen-comparison receipts, Local-owned status/return handoffs.
- Actual original helper line 138 omits admitted_include from early opaque CPP reconstruction and admitted_decl from the corresponding API; at line 241 the independent owned-name path already removes both. The replacement targets are unique, and both frozen opaque Git blob IDs remain unchanged.
- Independent GitHub Connector source comparison: native current CPP contains exactly one additive admitted literal and stripping it reproduces 82dd CPP byte-for-byte. Current API has exactly one analogous literal and stripping it reproduces 82dd API byte-for-byte. Both published native verifier scripts define both admission literal names.
- No product-native source change, no prior checkpoints/failed evidence rewritten. Demo code still anchored at 117cc6b1c2be8050cd2f433ef17db8b3c5138f93; this Primary delta is Docs-only.

## Tests performed

Host-only in isolated Primary Python 3.13: python3 -B -m unittest -v test_prepare_p1_admitted_local.py — **13 tests passed, zero failures/errors**, including exact two-edit output, missing/duplicate/already repaired anchors, wrong original frozen token, altered owned-name path, direct native-byte addition tamper, AST literal missing, archived manifest mutation and traversal, and root collision/symlink/relative-path refusal. Both Python modules compiled with python3 -m py_compile. Generated full historical helper is *not* executed in Primary because Unity SDK and complete source/historical raw roots exist only in Local.

Connector publication and exact Git blob readback:
- prepare_p1_admitted_local.py blob cf2fdf39fe17df076d50dcc33ed72c757eaa3b26
- test_prepare_p1_admitted_local.py blob 58e6e0b9ff870d1ada20021ab36a82882d60b837

Verification is source/static/synthetic host-only, **not** a fresh 25-component batch, not Mac Apple SDK syntax, not a live Unity run, and not independent Local audit. No SourceHostAndSDKOnly PASS is claimed for e1e5 or this new source-pinned cycle.

## Open requirements

The new Local cycle must still complete 25/25, original 85, eight inventories, new 9+9, five managed positives + exact negative, 100/100 installed official SDK syntax, 20 Git postflight and source/historical vendor preservation; then independent audit and factual publication. Any aborted unknown command lifetime remains FailedOrIncomplete without retry. Source pointer provenance, canonical TypeKeys, global epoch, full V1/runtime/Shutdown, R03/H2/Human Review remain incomplete or blocked.
