# M05 v6 evidence retention

Start with [artifact-index-v6.json](artifact-index-v6.json),
[m05-verification.json](m05-verification.json), and the parent
[review record](../M05-review.md). All copied artifacts preserve their original
bytes; their original absolute paths, sizes and hashes are indexed.

The Player archive contains all 76 original files, not filtered PASS summaries:
19 results, 18 raw-native diagnostic companions, 19 Unity logs, 19 console logs
and the launch receipt. Its [member index](player-results-v6-09a15e6.index.json)
was checked by streaming every archived member and rehashing originals. JSON,
raw type keys, process addresses and logs were not normalized.

Frozen builds retain demo source `09a15e686a4e7581e362175f4aa99d6bde80de55`.
Current offline tooling is `6f0123839ba1fe01e18c29858b15fefc1cc7b12c`; separate
installation/source-equivalence receipts bind that distinction. The final
strict verifier passed the original canonical input/result paths. These copies
are not replacement acceptance inputs, a rebuilt Player or a portable patch.
Full DLL/native/snapshot graphs remain at the indexed immutable local roots.

`history` contains preserved failures and diagnoses, never acceptance results.
`source-reviews` contains bounded source-readiness reviews, never the full M05
acceptance verdict. Native receipts disclose their physical metadata adapters.
The parent review record carries the two required independent final gates.

Capture scripts are retained for audit only. They refuse existing destinations;
do not rerun them against this evidence directory or rewrite indexed files.
