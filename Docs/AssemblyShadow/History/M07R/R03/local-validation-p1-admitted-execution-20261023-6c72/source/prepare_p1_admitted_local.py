#!/usr/bin/env python3
"""Prepare a new, single-use R03 P1 Local collector from immutable Local evidence.

Only creates the fresh audit/preflight root. Never starts a core batch, compiler,
Unity, or an independent audit; never changes consumed evidence or source.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BRANCH = "codex/assembly-shadow-r01b-h1"
OLD_DEMO = "050a086304ac81b5680c6b4a9ae237418e492464"
NATIVE = "e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb"
PREVIOUS_NATIVE = "82ddcef9417e3d662fdd39916a92124b5c835094"
FIXED = {
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": NATIVE,
}
ARCHIVE = "Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261022-e1e5"
ORIGINAL_HELPER_SHA256 = "73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd"
CPP_OLD = "cpp_without_live=cpp.replace(literals['integrated_json_header'],'')"
CPP_NEW = "cpp_without_live=cpp.replace(literals['admitted_include'],'').replace(literals['integrated_json_header'],'')"
API_OLD = ";api=api.replace(literals['integrated_json_forward'],'')"
API_NEW = ";api=api.replace(literals['admitted_decl'],'').replace(literals['integrated_json_forward'],'')"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def required_single(text: str, token: str) -> None:
    if not token or text.count(token) != 1:
        raise ValueError("Missing or duplicated exact source token: " + repr(token[:90]))


def transform_helper(original: bytes) -> bytes:
    """Repair only the two omitted literals in the archived opaque reconstruction."""
    text = original.decode("utf-8", errors="strict")
    for old, new in ((CPP_OLD, CPP_NEW), (API_OLD, API_NEW)):
        required_single(text, old)
        if new in text:
            raise ValueError("Collector already transformed; refuse second repair")
        text = text.replace(old, new)
    # The previously correct, later independent reconstruction must survive.
    for token in (
        "restoredcpp=actualcpp.replace(ol['admitted_include'],'')",
        "restoredapi=actualapi.replace(ol['admitted_decl'],'')",
        "'53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2'",
        "'32956c2c4084951131b497c1201712a0d4fe11b3'",
    ):
        required_single(text, token)
    compile(text, "prepared-run-once.py", "exec")
    return text.encode("utf-8")


def admitted_addition(current: bytes, previous: bytes, literal: bytes) -> None:
    if not literal or current.count(literal) != 1 or current.replace(literal, b"", 1) != previous:
        raise ValueError("Current native CPP/API not equal to pinned prior plus ONE exact admission literal")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def literal_map(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    funs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "verify"]
    if len(funs) != 1:
        raise ValueError("Native verifier must have exactly one verify()")
    out = {}
    for node in funs[0].body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                val = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(val, str):
                out[node.targets[0].id] = val
    if not all(k in out for k in ("admitted_include", "admitted_decl")):
        raise ValueError("Missing authenticated native admitted literals")
    return out


def check_source(native: Path, archive: Path) -> dict:
    finding = json.loads((archive / "FINDING.json").read_text(encoding="utf-8"))
    if finding["id"] != "IR-LOCAL-P1-ADMITTED-PREFLIGHT-01" or finding["coreBatchResult"] != "NotRun":
        raise ValueError("Historical blocked Local finding changed")
    scripts = [native / "tools/r03/diagnostic_stream" / name for name in (
        "run_opaque_execution_inventory.py", "run_owned_physical_names.py")]
    a, b = (literal_map(path) for path in scripts)
    for key in ("admitted_include", "admitted_decl"):
        if a[key] != b[key]:
            raise ValueError("Published native verifiers disagree: " + key)
    result = {}
    for filename, key in (("AssemblyShadow.cpp", "admitted_include"), ("AssemblyShadow.h", "admitted_decl")):
        path = "libil2cpp/vm/" + filename
        current = (native / path).read_bytes()
        prior = git(native, "show", PREVIOUS_NATIVE + ":" + path)
        literal = a[key].encode("utf-8")
        record = next((x for x in finding["currentSourceExactlyMatchesExpectedAdditiveDelta"] if x["path"] == path), None)
        frozen = next((x for x in finding["reproduction"] if x["path"] == path), None)
        if not record or not frozen or a[key] != frozen["omittedOnlyNewLiteral"]:
            raise ValueError("Admission literal diverged from immutable Local finding: " + path)
        if (digest(current) != record["currentSha256"] or digest(prior) != record["prior82ddSha256"]
                or current != git(native, "show", NATIVE + ":" + path)):
            raise ValueError("Native source differs from recorded source pin: " + path)
        admitted_addition(current, prior, literal)
        old_blob = git(native, "cat-file", "blob", frozen["originalGitBlob"])
        if digest(old_blob) != frozen["originalSha256"]:
            raise ValueError("Frozen source blob differs: " + path)
        result[path] = {"currentSha256": digest(current), "priorSha256": digest(prior),
                        "literalSha256": digest(literal), "frozenBlob": frozen["originalGitBlob"]}
    return result


def archive_integrity(archive: Path) -> dict:
    """Bind ALL already-consumed e1e5 checkpoint bytes, not only the finding."""
    manifest = archive / "MANIFEST.sha256"
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError("Historical checkpoint manifest unavailable")
    count = 0
    seen = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        sha, sep, rel = line.partition("  ")
        path = Path(rel)
        if sep != "  " or len(sha) != 64 or path.is_absolute() or ".." in path.parts or rel in seen:
            raise ValueError("Invalid archived checkpoint manifest entry")
        file = archive / path
        if not file.is_file() or file.is_symlink() or digest(file.read_bytes()) != sha:
            raise ValueError("Modified historical checkpoint: " + rel)
        seen.add(rel)
        count += 1
    if count < 30 or "FINDING.json" not in seen or "preflight/run-once.py" not in seen:
        raise ValueError("Historical blocked checkpoint manifest incomplete")
    return {"manifestSha256": digest(manifest.read_bytes()), "filesVerified": count,
            "originalHelperSha256": digest((archive / "preflight/run-once.py").read_bytes())}


def pristine_root(path: Path) -> None:
    if not path.is_absolute() or path.exists() or path.is_symlink() or path.resolve() != path:
        raise ValueError("Root is non-absolute, already used, or not canonical: " + str(path))


def prepare(args: argparse.Namespace) -> dict:
    workspace = Path(args.workspace)
    demo = workspace / "hybridclr_demo"
    native = workspace / "il2cpp_plus"
    archive = demo / ARCHIVE
    demo_sha = args.demo_sha
    if len(demo_sha) != 40 or any(c not in "0123456789abcdef" for c in demo_sha):
        raise ValueError("Expected actual 40-character demo commit")
    for name, sha in {"hybridclr_demo": demo_sha, **FIXED}.items():
        repo = workspace / name
        if git(repo, "rev-parse", "HEAD").decode().strip() != sha:
            raise ValueError("Incorrect local commit in " + name)
        if git(repo, "branch", "--show-current").decode().strip() != BRANCH:
            raise ValueError("Incorrect working branch in " + name)
        if git(repo, "status", "--porcelain"):
            raise ValueError("Working tree is not clean: " + name)
    if git(demo, "diff", "--name-only", "117cc6b1c2be8050cd2f433ef17db8b3c5138f93", demo_sha,
           "--", ".", ":(exclude)Docs/**"):
        raise ValueError("Unreviewed non-document demo delta")

    archived = archive_integrity(archive)
    historical_helper = (archive / "preflight/run-once.py").read_bytes()
    if digest(historical_helper) != ORIGINAL_HELPER_SHA256:
        raise ValueError("Historical failed collector SHA differs")
    # No file may be silently replaced with a locally altered historical version.
    for rel in ("preflight/run-once.py", "preflight/audit.py", "FINDING.json", "MANIFEST.sha256"):
        file_bytes = (archive / rel).read_bytes()
        if file_bytes != git(demo, "show", OLD_DEMO + ":" + ARCHIVE + "/" + rel):
            raise ValueError("Historical git content differs from immutable source: " + rel)
    source = check_source(native, archive)
    prepared = transform_helper(historical_helper)
    audit = (archive / "preflight/audit.py").read_bytes()
    compile(audit, "archived-independent-audit.py", "exec")

    preflight = Path(args.preflight)
    output = Path(args.output)
    scratch = Path(args.scratch)
    cp_rel = Path(args.checkpoint)
    if cp_rel.is_absolute() or ".." in cp_rel.parts or not str(cp_rel).startswith("Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-"):
        raise ValueError("Checkpoint must be new R03 P1 additive path under Docs/AssemblyShadow")
    checkpoint = demo / cp_rel
    all_roots = (preflight, output, scratch, checkpoint)
    for root in all_roots:
        pristine_root(root)
    for i, root in enumerate(all_roots):
        for other in all_roots[i+1:]:
            if root in other.parents or other in root.parents:
                raise ValueError("Roots overlap")
    for root in all_roots[:3]:
        if any(root == r or r in root.parents or root in r.parents for r in (demo, native, workspace / "hybridclr", workspace / "hybridclr_unity")):
            raise ValueError("Non-checkpoint root overlaps source checkout")
    expected = {"pins": {"hybridclr_demo": demo_sha, **FIXED}, "workspace": str(workspace),
                "output": str(output), "scratch": str(scratch), "unity": args.unity,
                "preflight": str(preflight)}
    receipt = {"kind": "R03P1AdmittedLocalCollectorPreparation", "result": "PreparedNotExecuted",
               "historicalFailedCollectorSha256": digest(historical_helper),
               "correctedCollectorSha256": digest(prepared), "independentAuditSha256": digest(audit),
               "repairScope": ["opaque CPP admitted_include exact strip", "opaque API admitted_decl exact strip"],
               "historicalCheckpoint": archived, "nativeByteSourceProof": source,
               "pins": expected["pins"], "roots": [str(p) for p in all_roots],
               "coreInvoked": False, "sdkCompiled": False, "runtimeAcceptance": False}
    # No writes or creates before ALL source/history/root checks above succeed.
    preflight.mkdir(mode=0o700)
    for name, raw in (("run-once.py", prepared), ("audit.py", audit),
                      ("EXPECTED.json", (json.dumps(expected, indent=2) + "\n").encode()),
                      ("PREPARATION.json", (json.dumps(receipt, indent=2) + "\n").encode())):
        with (preflight / name).open("xb") as f:
            f.write(raw)
    return receipt


def verify_after(workspace: Path, preflight: Path) -> dict:
    receipt_path = preflight / "PREPARATION.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("kind") != "R03P1AdmittedLocalCollectorPreparation" or receipt.get("coreInvoked") is not False:
        raise ValueError("Preflight preparation receipt invalid")
    archive = workspace / "hybridclr_demo" / ARCHIVE
    after = archive_integrity(archive)
    if after != receipt["historicalCheckpoint"]:
        raise ValueError("Historical blocked checkpoint changed after Local batch")
    if digest((preflight / "run-once.py").read_bytes()) != receipt["correctedCollectorSha256"]:
        raise ValueError("Prepared Local collector changed")
    if digest((preflight / "audit.py").read_bytes()) != receipt["independentAuditSha256"]:
        raise ValueError("Prepared independent audit script changed")
    result = {"kind": "R03P1BlockedHistoryAfter", "result": "Preserved",
              "priorBlockedCheckpoint": after, "noHistoricalReclassification": True}
    with (preflight / "BLOCKED_HISTORY_AFTER.json").open("xb") as f:
        f.write((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--verify-after", action="store_true", help="Verify archived blocked Local checkpoint after the batch; never rerun core")
    parser.add_argument("--demo-sha")
    parser.add_argument("--unity")
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--output")
    parser.add_argument("--scratch")
    parser.add_argument("--checkpoint", help="repository-relative new checkpoint path")
    args = parser.parse_args()
    try:
        if args.verify_after:
            result = verify_after(Path(args.workspace), Path(args.preflight))
        else:
            if not all((args.demo_sha, args.unity, args.output, args.scratch, args.checkpoint)):
                raise ValueError("All prepare-mode arguments required")
            result = prepare(args)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError, UnicodeError, SyntaxError) as error:
        print("PREREQUISITE BLOCKED: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
