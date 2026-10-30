#!/usr/bin/env python3
"""R03 IR-02 current-native source preflight. SOURCE ONLY; no Unity or compiler.

The original R03 source-pins.json remains immutable. This checks a separate
candidate native tuple and source Git blobs before proposing a fresh Player run.
It neither creates a Player project nor permits any historical result promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "current_native_candidate.json"
BRANCH = "codex/assembly-shadow-r01b-h1"
OLD_NATIVE = "74dbdbea80d83923863303bd2b2c0a87f36541b1"
CURRENT = {
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "ca0aab8e0abcbcb60a1532223d9e1bdb0aea86c4",
}
# Each source blob was directly fetched at the fixed repository commit.
# A config edit cannot weaken the required source file inventory or hashes.
FILES = {
    ("hybridclr_demo", "Tools/AssemblyShadow/R03/source-pins.json"): "9d72a237fb6ecd3efe3267ca89625aa49c61775d",
    ("hybridclr_demo", "Tools/AssemblyShadow/R03/run_local.py"): "9aef8093f98fb7f9b5dd395ba4e5c2ed0220276e",
    ("hybridclr_demo", "Tools/AssemblyShadow/R03IR/run_terminal_local.py"): "70b1a27f2dbbcad93f67e8caddcf7282ff3afd73",
    ("hybridclr_demo", "Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs"): "598feeec3231707091699d99fbf4428d50b52024",
    ("hybridclr_demo", "Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs"): "b993703d918090733a659bd7c3ac883cd5d753e1",
    ("hybridclr_demo", "Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp"): "2f13925190a1576738457d8d43f3646a4c7c095f",
    ("il2cpp_plus", "libil2cpp/vm/AssemblyShadow.cpp"): "57cf47f964a83973df8296955ccf856b105c595f",
    ("il2cpp_plus", "libil2cpp/vm/AssemblyShadowTerminalExecution.h"): "33258986c31b2e6ae3af17b8553030482a83aef7",
    ("il2cpp_plus", "libil2cpp/vm/Runtime.cpp"): "96b914fbeb31c69d649e4076a802de0b6418daa8",
    ("hybridclr", "hybridclr/interpreter/Interpreter_Execute.cpp"): "2dbdb7527afee7f2546e45f20e6ef93e1bca237a",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class CandidateSourceError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise CandidateSourceError(message)


def git_blob(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\0" + data)
    return h.hexdigest()


def strict_object(pairs):
    d = {}
    for key, val in pairs:
        require(key not in d, "Duplicate JSON key: " + key)
        d[key] = val
    return d


def read_config(path: Path = CONFIG) -> dict:
    require(path.is_file() and not path.is_symlink(), "Missing source candidate config")
    d = json.loads(path.read_bytes(), object_pairs_hook=strict_object)
    require(type(d) is dict, "Candidate config must be an object")
    require(d.get("schemaVersion") == 1 and d.get("kind") == "R03IRCurrentNativeSourceCandidate",
            "Source candidate schema/kind changed")
    require(d.get("branch") == BRANCH, "Source candidate branch changed")
    require(d.get("legacyR03NativePin") == OLD_NATIVE, "Original R03 pin changed")
    require(d.get("candidateNativePin") == CURRENT["il2cpp_plus"] and
            d["candidateNativePin"] != d["legacyR03NativePin"], "New native candidate source identity changed")
    require(d.get("hybridclrPin") == CURRENT["hybridclr"] and
            d.get("hybridclrUnityPin") == CURRENT["hybridclr_unity"],
            "Interpreter/package candidate source identity changed")
    require(d.get("originalR03SourcePinsGitBlob") == FILES[("hybridclr_demo", "Tools/AssemblyShadow/R03/source-pins.json")],
            "Original historical source-pins.json identity changed")
    require(type(d.get("files")) is list and len(d["files"]) == len(FILES),
            "Source file inventory cardinality changed")
    seen = set()
    for entry in d["files"]:
        require(type(entry) is dict and set(entry) == {"repository", "path", "gitBlob"},
                "Source file record fields changed")
        key = (entry["repository"], entry["path"])
        require(key in FILES and key not in seen, "Unexpected or duplicated source file identity")
        require(entry["gitBlob"] == FILES[key], "Source file Git blob changed: " + str(key))
        seen.add(key)
    require(seen == set(FILES), "Required source file missing from candidate")
    require(d.get("expectedFocusedPlayers") == 5 and d.get("expectedCandidateBuilds") == 3 and
            d.get("expectedOriginalSFixtureCount") == 15, "Focused test case cardinality changed")
    for flag in ("candidateRuntimeAcceptance", "sourceOnlyValidationIsProductValidation",
                 "originalSResultReclassified", "originalB7e3AndC42aFailReclassified"):
        require(d.get(flag) is False, "Candidate source-only/legacy acceptance flag changed: " + flag)
    require(d.get("ownerGate") == "No Local execution authorized; requires a new explicit source-pinned Local handoff.",
            "Local gate boundary changed")
    return d


def read_source(repo: Path, relative: str) -> bytes:
    candidate = repo / relative
    require(candidate.is_file() and not candidate.is_symlink() and
            candidate.resolve(strict=True) == candidate,
            "Missing/symlink/aliased source: " + str(candidate))
    return candidate.read_bytes()


def candidate_pins(legacy: dict, config: dict) -> dict:
    require(type(legacy) is dict and type(config) is dict, "Source pins must be objects")
    require(legacy.get("schemaVersion") == 1 and legacy.get("phase") == "candidate" and
            legacy.get("branch") == BRANCH, "Historical R03 source pin format/branch changed")
    for name in ("hybridclr", "hybridclr_unity"):
        require(legacy.get(name) == CURRENT[name], "Unexpected legacy interpreter/package source pin: " + name)
    require(legacy.get("il2cpp_plus") == OLD_NATIVE,
            "Original historical R03 native pin changed instead of using overlay")
    require(legacy.get("runtimeAcceptance") is False, "Original runtime acceptance flag changed")
    require(config["candidateNativePin"] == CURRENT["il2cpp_plus"], "Unexpected candidate native identity")
    combined = dict(legacy)
    combined["il2cpp_plus"] = config["candidateNativePin"]
    require(combined["il2cpp_plus"] != legacy["il2cpp_plus"], "Candidate overlay did not change native tuple")
    return combined


def git_head(repo: Path) -> str:
    cp = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                        capture_output=True, text=True, check=False, timeout=30)
    require(cp.returncode == 0 and HEX40.fullmatch(cp.stdout.strip()) is not None,
            "Unable to bind source checkout HEAD: " + str(repo))
    return cp.stdout.strip()


def verify_source_roots(roots: dict, *, require_checkout_heads: bool = False) -> dict:
    require(set(roots) == {"hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus"},
            "Exactly four repository paths required")
    checked = {}
    for name, root in roots.items():
        path = Path(root)
        require(path.is_absolute() and path.is_dir() and not path.is_symlink() and
                path.resolve(strict=True) == path, "Source repository root is missing/noncanonical: " + name)
        checked[name] = path
    require(len(set(checked.values())) == 4, "Repositories must be separate roots")
    config = read_config()
    current = {}
    for name in CURRENT:
        if require_checkout_heads:
            observed = git_head(checked[name])
            require(observed == CURRENT[name], "Checked-out source HEAD differs: " + name)
            current[name] = observed
        else:
            current[name] = "NotChecked_RawSourceBlobsOnly"
    files = []
    for (name, relative), expected in FILES.items():
        raw = read_source(checked[name], relative)
        observed = git_blob(raw)
        require(observed == expected, "Source bytes/Git blob mismatch: " + name + "/" + relative)
        files.append({"repository": name, "path": relative,
                      "gitBlob": observed, "bytes": len(raw)})
    legacy = json.loads(read_source(checked["hybridclr_demo"],
                                    "Tools/AssemblyShadow/R03/source-pins.json"),
                        object_pairs_hook=strict_object)
    effective = candidate_pins(legacy, config)
    player = read_source(checked["hybridclr_demo"],
                         "Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs").decode("utf-8")
    runner = read_source(checked["hybridclr_demo"],
                         "Tools/AssemblyShadow/R03IR/run_terminal_local.py").decode("utf-8")
    for anchor in ("activeReflectionAttempted", "activeDelegateAttempted",
                   "aotReflectionAttempted", "preShadowField", "finalShadowField",
                   "recoveryStable", "fixedDiagnosticsReadable"):
        require(anchor in player, "Post-terminal Player source witness missing: " + anchor)
    for anchor in ("def execute(", "batch_type=Batch",
                   "IR-R03-02-release-baseline", "IR-R03-02-debug-baseline",
                   "IR-R03-02-release-type", "IR-R03-02-off", "IR-R03-02-release-engine"):
        require(anchor in runner, "Focused R03 original case or injection point missing: " + anchor)
    return {
        "schemaVersion": 1, "kind": "R03IRCurrentNativeCoherentSourceOnlyGate",
        "result": "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
        "branch": BRANCH, "historicalR03PinRemains": OLD_NATIVE,
        "currentCandidatePins": {k: effective[k] for k in CURRENT},
        "checkoutHeads": current, "sourceFiles": files, "verifiedSourceFiles": len(files),
        "focusedPlayerCaseCount": config["expectedFocusedPlayers"],
        "candidateNativeBuildRoles": config["expectedCandidateBuilds"],
        "originalSFixtureCount": config["expectedOriginalSFixtureCount"],
        "originalR03PinsRewritten": False,
        "newBuildOrUnityPlayerRun": False, "runtimeAcceptance": False,
        "R03Accepted": False, "H2Passed": False, "ReadyForHumanReviewGate": False,
        "currentSourceMatchedPlayerExecution": "NotRun",
        "fullOriginalSIndependentReview": "NotPassed",
        "nextLocalAuthority": "NotAuthorized",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("demo", "native", "hybridclr", "package"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--exact-checkout-heads", action="store_true",
                        help="Require actual git HEAD to equal manifest fixed native/interpreter/package pins")
    parser.add_argument("--output", type=Path,
                        help="Optional new output report path; must not exist")
    args = parser.parse_args()
    try:
        result = verify_source_roots({
            "hybridclr_demo": args.demo,
            "il2cpp_plus": args.native,
            "hybridclr": args.hybridclr,
            "hybridclr_unity": args.package,
        }, require_checkout_heads=args.exact_checkout_heads)
        serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            require(args.output.is_absolute() and not args.output.exists() and
                    not args.output.is_symlink(), "Report path must be an absent absolute path")
            require(all(not args.output.is_relative_to(Path(v)) for v in
                        (args.demo, args.native, args.hybridclr, args.package)),
                    "Never write results into a source repository")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as fh:
                fh.write(serialized.encode("utf-8"))
        print("SOURCE_ONLY_CURRENT_NATIVE=" + json.dumps({
            "result": result["result"], "sourceFiles": result["verifiedSourceFiles"],
            "oldNative": result["historicalR03PinRemains"],
            "candidateNative": result["currentCandidatePins"]["il2cpp_plus"],
            "playerExecution": result["currentSourceMatchedPlayerExecution"]}))
        return 0
    except (CandidateSourceError, KeyError, TypeError, OSError) as error:
        print("SOURCE_ONLY_CANDIDATE_BLOCKED: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
