#!/usr/bin/env python3
"""Build and run the standalone R01B codec kernel in an immutable run dir.

The test includes the production header directly. Every invocation claims a
new ignored run directory, so binaries, logs, dependency evidence, and the
receipt from an earlier invocation are never overwritten.
"""

from __future__ import print_function

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSPACE = SCRIPT.parents[3]
DEMO = SCRIPT.parents[2]
SOURCE = DEMO / "Tools" / "AssemblyShadow" / "native-tests" / "r01b-codec-kernel.cpp"
HEADER = WORKSPACE / "hybridclr" / "hybridclr" / "metadata" / "InterpreterMetadataIndexCodec.h"
OUT = DEMO / "_temp" / "AssemblyShadow" / "R01B"
COMPILER = Path("/usr/bin/clang++")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def optional_sha256(path):
    return sha256(path) if path.exists() else None


def claim_run_dir():
    """Create a run directory without ever reusing an existing name."""
    OUT.mkdir(parents=True, exist_ok=True)
    run_number = 2
    while True:
        candidate = OUT / "codec-kernel-run-{}".format(run_number)
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            run_number += 1


def run_logged(argv, log_path, env=None):
    try:
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env=env, check=False)
        output = result.stdout
        code = result.returncode
    except OSError as error:
        output = ("command failed to start: {}\n".format(error)).encode("utf-8")
        code = 127
    log_path.write_bytes(output)
    return code


def run_binary(binary, log_path, env=None):
    if not binary.exists():
        log_path.write_text("binary missing; execution was attempted after failed build\n",
                            encoding="utf-8")
        return 127
    return run_logged([str(binary)], log_path, env)


def parse_result(log_path):
    if not log_path.exists():
        return None, None
    match = re.search(r"checks=(\d+) failures=(\d+)",
                      log_path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        return None, None
    return int(match.group(1)), int(match.group(2))


def parse_performance(log_path):
    if not log_path.exists():
        return None
    match = re.search(
        r"decode_iterations=(\d+) sparse_nanoseconds=(\d+) legacy_profile1_nanoseconds=(\d+) checksum=(\d+)",
        log_path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        return None
    return {
        "iterations": int(match.group(1)),
        "sparseNanoseconds": int(match.group(2)),
        "legacyProfile1Nanoseconds": int(match.group(3)),
        "checksum": int(match.group(4)),
    }


def dependency_paths(dependency_file):
    if not dependency_file.exists():
        return []
    tokens = dependency_file.read_text(encoding="utf-8", errors="replace")
    tokens = tokens.replace("\\\n", " ").split()
    result = []
    for token in tokens[1:]:
        candidate = Path(token)
        if candidate.exists() and candidate not in result:
            result.append(candidate)
    return result


def main():
    run_dir = claim_run_dir()
    release = run_dir / "codec-kernel-release"
    sanitizer = run_dir / "codec-kernel-asan-ubsan"
    release_log = run_dir / "codec-kernel-run-release.log"
    sanitizer_log = run_dir / "codec-kernel-run-asan-ubsan.log"
    release_build_log = run_dir / "codec-kernel-build-release.log"
    sanitizer_build_log = run_dir / "codec-kernel-build-asan-ubsan.log"
    dependency_file = run_dir / "codec-kernel-dependencies.d"
    receipt_path = run_dir / "codec-kernel-receipt.json"

    runner_sha_before = optional_sha256(SCRIPT)
    compiler_sha_before = optional_sha256(COMPILER)
    source_sha_before = optional_sha256(SOURCE)
    header_sha_before = optional_sha256(HEADER)
    compiler_version = "unavailable"
    if COMPILER.exists():
        version_result = subprocess.run([str(COMPILER), "--version"],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        check=False)
        compiler_version = version_result.stdout.decode("utf-8", "replace").strip()

    include_dir = WORKSPACE / "hybridclr" / "hybridclr"
    release_argv = [str(COMPILER), "-std=c++11", "-O2", "-DNDEBUG", "-Wall",
                    "-Wextra", "-Werror", "-I", str(include_dir), str(SOURCE),
                    "-o", str(release)]
    sanitizer_argv = [str(COMPILER), "-std=c++11", "-O1", "-g", "-Wall",
                      "-Wextra", "-Werror", "-fno-omit-frame-pointer",
                      "-fsanitize=address,undefined", "-I", str(include_dir),
                      str(SOURCE), "-o", str(sanitizer)]
    dependency_argv = [str(COMPILER), "-std=c++11", "-MM", "-I", str(include_dir),
                       str(SOURCE)]

    release_build_exit = run_logged(release_argv, release_build_log)
    sanitizer_build_exit = run_logged(sanitizer_argv, sanitizer_build_log)
    dependency_exit = run_logged(dependency_argv, dependency_file)

    release_run_exit = run_binary(release, release_log)
    sanitizer_env = os.environ.copy()
    sanitizer_env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    sanitizer_env["UBSAN_OPTIONS"] = "halt_on_error=1"
    sanitizer_run_exit = run_binary(sanitizer, sanitizer_log, sanitizer_env)

    source_sha_after = optional_sha256(SOURCE)
    header_sha_after = optional_sha256(HEADER)
    runner_sha_after = optional_sha256(SCRIPT)
    compiler_sha_after = optional_sha256(COMPILER)
    release_checks, release_failures = parse_result(release_log)
    sanitizer_checks, sanitizer_failures = parse_result(sanitizer_log)
    release_performance = parse_performance(release_log)

    failure_reasons = []
    for label, code in (("release_build", release_build_exit),
                        ("asan_ubsan_build", sanitizer_build_exit),
                        ("dependency_scan", dependency_exit),
                        ("release_run", release_run_exit),
                        ("asan_ubsan_run", sanitizer_run_exit)):
        if code != 0:
            failure_reasons.append("{} exit {}".format(label, code))
    if release_checks is None or release_failures is None:
        failure_reasons.append("release result line missing")
    elif release_failures != 0:
        failure_reasons.append("release reported {} failures".format(release_failures))
    if sanitizer_checks is None or sanitizer_failures is None:
        failure_reasons.append("asan/ubsan result line missing")
    elif sanitizer_failures != 0:
        failure_reasons.append("asan/ubsan reported {} failures".format(sanitizer_failures))
    if release_performance is None:
        failure_reasons.append("release performance result line missing")
    if source_sha_before != source_sha_after:
        failure_reasons.append("test source changed during run")
    if header_sha_before != header_sha_after:
        failure_reasons.append("production header changed during run")
    if runner_sha_before != runner_sha_after:
        failure_reasons.append("runner changed during run")
    if compiler_sha_before != compiler_sha_after:
        failure_reasons.append("compiler changed during run")

    passed = not failure_reasons
    receipt = {
        "artifact": "R01B production standalone interpreter metadata index codec kernel",
        "run_directory": str(run_dir),
        "status": ("production_kernel_checks_passed; standalone_no_Player_capacity_claim"
                   if passed else "production_kernel_checks_failed; evidence_captured"),
        "failure_reasons": failure_reasons,
        "scope": {
            "production_header": str(HEADER),
            "test_source": str(SOURCE),
            "runner": str(SCRIPT),
            "source_sha256_before": source_sha_before,
            "source_sha256_after": source_sha_after,
            "header_sha256_before": header_sha_before,
            "header_sha256_after": header_sha_after,
            "runner_sha256_before": runner_sha_before,
            "runner_sha256_after": runner_sha_after,
            "kernel_runtime_files_modified_by_runner": False,
            "prior_run_artifacts_overwritten": False,
        },
        "compiler": {
            "executable": str(COMPILER),
            "sha256_before": compiler_sha_before,
            "sha256_after": compiler_sha_after,
            "version": compiler_version,
            "release_argv": release_argv,
            "asan_ubsan_argv": sanitizer_argv,
            "dependency_argv": dependency_argv,
        },
        "verification": {
            "release_build_exit": release_build_exit,
            "asan_ubsan_build_exit": sanitizer_build_exit,
            "dependency_scan_exit": dependency_exit,
            "release_run_exit": release_run_exit,
            "asan_ubsan_run_exit": sanitizer_run_exit,
            "release_checks": release_checks,
            "asan_ubsan_checks": sanitizer_checks,
            "release_failures": release_failures,
            "asan_ubsan_failures": sanitizer_failures,
            "release_decode_performance": release_performance,
            "asan_environment": {
                "ASAN_OPTIONS": sanitizer_env["ASAN_OPTIONS"],
                "UBSAN_OPTIONS": sanitizer_env["UBSAN_OPTIONS"],
            },
        },
        "artifacts": {
            "release_binary": {"path": str(release), "sha256": optional_sha256(release)},
            "asan_ubsan_binary": {"path": str(sanitizer), "sha256": optional_sha256(sanitizer)},
            "dependency_file": {"path": str(dependency_file), "sha256": optional_sha256(dependency_file)},
            "dependencies": [
                {"path": str(path), "sha256": sha256(path)}
                for path in dependency_paths(dependency_file)
            ],
            "logs": {
                "release_build": {"path": str(release_build_log), "sha256": sha256(release_build_log)},
                "asan_ubsan_build": {"path": str(sanitizer_build_log), "sha256": sha256(sanitizer_build_log)},
                "release_run": {"path": str(release_log), "sha256": sha256(release_log)},
                "asan_ubsan_run": {"path": str(sanitizer_log), "sha256": sha256(sanitizer_log)},
            },
        },
        "design": {
            "raw_domain": "[0, 2^31), -1 sentinel excluded; positive decode values are AOT",
            "pages": "4096-value pages; 524287 usable; max charged 393215",
            "images": "internal monotonic IDs 1..8192; ordinary and Shadow share ledger",
            "lifecycle": ["Private", "Published", "Aborted"],
            "storage": "preallocated stable image records, page credits/descriptors, and reverse map",
            "growth": "all credits charged before lazy binding; per-image linked credit lists support interleaving",
            "finalization": "checked half-open [0,L) union mapped sparse pages; atomic charge/seal; publication requires seal",
            "decode": "lock-free atomic descriptor loads; no allocation",
        },
        "honest_limits": [
            "This receipt exercises the production kernel header directly; runtime-adapter and Player evidence are separate.",
            "Explicit owner arguments model adapter authorization and are not production TLS checks.",
            "No ThreadSanitizer claim; only release and AddressSanitizer/UndefinedBehaviorSanitizer runs.",
            "The benchmark is a same-process hot-decode comparison; it is not an end-to-end Player performance claim.",
        ],
    }
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "status": receipt["status"],
        "release_checks": release_checks,
        "asan_ubsan_checks": sanitizer_checks,
        "release_sha256": optional_sha256(release),
        "asan_ubsan_sha256": optional_sha256(sanitizer),
    }, sort_keys=True))
    if not passed:
        raise RuntimeError("; ".join(failure_reasons))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print("codec-kernel verification failed: {}".format(error), file=sys.stderr)
        sys.exit(1)
